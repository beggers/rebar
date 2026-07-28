#!/usr/bin/env python3
"""Show the genuine first Zig setup failure without inventing matching or speed."""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SCHEMA = "rebar-candidate-current-overview-v26"
SELF = "tools/render_candidate_current_overview_v26.py"
OUTPUT = "docs/evidence/candidate-current-overview-v26"
MAX_OWNER = 8 * 1024 * 1024
MAX_EXPANDED = 8 * 1024 * 1024
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
V25 = {
    "source": (
        "tools/render_candidate_current_overview_v25.py",
        "9b1eabba4a3bd991c4359af4ab1482fe6f1ce848bb9e5df6fdd9e8bdafb21204",
        98948,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v25.inputs.json",
        "123210219fac109506c03c2f76f89fda33aa5e08b0628fef43b9236d05bc1abe",
        37281,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v25.json",
        "8e4101c896e316190928d0710ca4442488c925ee5ef421507ba4dd08ff10a6d9",
        144980,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v25.svg",
        "db2f1a11e49fd58701ad89111aa422e619431eb9834d3fb5ae66deffcd75f0bb",
        13188,
    ),
}
PRESERVATION = {
    "source": (
        "tools/preserve_owned_zig_campaign_preflight_failure_v1.py",
        "4a401ea42b4446535d51d1c7c65c688196185a0bb9fa2e15aebdb3bfebb85498",
        58558,
    ),
    "protocol": (
        "oracle/phase2/ZIG-CAMPAIGN-PREFLIGHT-FAILURE-V1.md",
        "a3c005c95c61a68a5683125f7805564f4749ea9e82350f2d883da9e29b2817c5",
        4413,
    ),
    "contract": (
        "oracle/phase2/zig-campaign-preflight-failure-v1.json",
        "534a3cde3084c12a4124f5dea057ddb80b53fa4c591c8c72e26931bc277735f0",
        16494,
    ),
}
FAILURE_ARCHIVE = (
    "oracle/phase2/evidence/"
    "zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz",
    "1cb38eb48a2d3305ea98d5103a27ce6ae758137168f68df07a408dec3d055a37",
    3711,
    2064,
    524606,
)
FAILURE_RECEIPT = (
    "oracle/phase2/evidence/"
    "zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-"
    "failures-publication-receipt.json",
    "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23",
    1992,
    2064,
    524607,
)
PLAIN_SHA256 = "df0c3cff6b6f956b58fe43f828d6b8d26efc8b9b0dac8972ae4f9902dd58302d"
PLAIN_BYTES = 9482
STDERR_SHA256 = "4810a51ee1a1194292f5fce1414b35fc1e2ed3e280dd28ef326314c84349593e"
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


class GraphError(Exception):
    """A preserved historical result or genuine failure could not be verified."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only exact independently authenticated bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise GraphError("reject noncanonical V26 graph evidence") from error


def checked_digest(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require an independently pinned SHA-256: " + label)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON,
         "use only exact isolated, bytecode-free CPython 3.14.6")


def document(raw: bytes, label: str) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        result: dict[str, object] = {}
        for key, value in pairs:
            need(key not in result, "reject duplicate JSON keys in " + label)
            result[key] = value
        return result

    def no_constant(value: str) -> object:
        raise GraphError("reject a nonfinite JSON constant in " + label + ": " + value)

    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                            parse_constant=no_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed JSON in " + label) from error
    need(type(result) is dict and canonical(result) == raw,
         "require exact canonical JSON bytes for " + label)
    return result


def read_owner(path: str, fingerprint: str, size: int | None = None,
               *, private: bool = False, device: int | None = None,
               inode: int | None = None) -> tuple[bytes, dict]:
    need(type(path) is str and bool(path) and not path.startswith("/")
         and ".." not in Path(path).parts,
         "read only the exact relative frozen evidence owner")
    checked_digest(fingerprint, path)
    descriptor = os.open(str(ROOT / path),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode)
             and before.st_nlink == 1
             and 0 <= before.st_size <= MAX_OWNER
             and (size is None or before.st_size == size)
             and (not private or stat.S_IMODE(before.st_mode) == 0o600)
             and (device is None or before.st_dev == device)
             and (inode is None or before.st_ino == inode),
             "reject an absent, linked, substituted, or nonprivate owner: " + path)
        remaining = before.st_size
        pieces: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            need(bool(block), "reject a truncated frozen owner: " + path)
            pieces.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"",
             "reject concealed trailing owner bytes: " + path)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need((before.st_dev, before.st_ino, before.st_size, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size, after.st_nlink)
             and digest(raw) == fingerprint,
             "reject changed owner identity or wrong digest: " + path)
        owner = {
            "path": path, "sha256": fingerprint, "bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "nlink": after.st_nlink, "uid": after.st_uid,
        }
        return raw, owner
    finally:
        os.close(descriptor)


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked_digest(fingerprint, path)
    need(type(size) is int and 0 <= size <= MAX_OWNER,
         "bound every genuine frozen source and graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def load_module(frozen: tuple[str, str, int], name: str) -> types.ModuleType:
    raw, _owner = read_owner(frozen[0], frozen[1], frozen[2])
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / frozen[0])
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    return module


def authenticate_v25() -> tuple[types.ModuleType, dict, dict, dict[str, str]]:
    v25 = load_module(V25["source"], "_rebar_exact_candidate_overview_v25_for_v26")
    need(v25.SCHEMA == "rebar-candidate-current-overview-v25"
         and v25.SELF == V25["source"][0]
         and tuple(v25.SUITES) == SUITES
         and v25.TOTAL_OWNERS == 139 and v25.TOTAL_REFERENCES == 144,
         "retain the exact frozen V25 source, suites, and 139/144 history")
    _v24, previous, _old_summary, _old_inputs, references = v25.authenticate_history()
    need(type(references) is dict and len(references) == 142,
         "authenticate every distinct signed pre-Rust historical reference")
    rust, additions = v25.authenticate_rust(
        previous, v25.RUST_ARCHIVE[1], v25.RUST_RECEIPT[1],
    )
    need(type(additions) is dict and len(additions) == 2
         and not (set(references) & set(additions)),
         "authenticate both distinct real Rust evidence owners")
    references = dict(references)
    references.update(additions)
    need(len(references) == 144,
         "derive all 144 genuine V25 references from distinct authenticated owners")
    frozen: dict[str, bytes] = {}
    for key, item in sorted(V25.items()):
        frozen[key], _owner = read_owner(item[0], item[1], item[2])
    old_summary = document(frozen["summary"], "published V25 summary")
    old_inputs = document(frozen["inputs"], "published V25 inputs")
    snapshot = old_summary.get("snapshot")
    need(type(snapshot) is dict,
         "retain the complete immutable V25 correctness snapshot")
    v25.validate_snapshot(snapshot)
    need(old_summary.get("schema") == v25.SCHEMA + "-summary"
         and old_summary.get("status") == "PASS"
         and old_summary.get("repository_evidence_owner_count") == 139
         and old_summary.get("authenticated_digest_addressed_history_paths") == 144
         and old_summary.get("full_case_denominator") == 31237
         and old_summary.get("suite_count") == 13
         and old_summary.get("private_waiver_count") == 13
         and old_summary.get("qualified_candidate_count") == 0
         and old_summary.get("performance") == "NOT MEASURED"
         and old_summary.get("memory") == "NOT MEASURED"
         and old_summary.get("final_holdout_opened") is False
         and old_summary.get("winner_selected") is False
         and type(old_summary.get("families")) is list
         and len(old_summary["families"]) == 7
         and old_inputs.get("schema") == v25.SCHEMA + "-inputs"
         and old_inputs.get("repository_evidence_owner_count") == 139
         and old_inputs.get("all_digest_addressed_history_path_count") == 144
         and snapshot.get("rust_v11_dual_overlay_repaired_source_build") == rust
         and frozen["svg"] == v25.make_svg(
             snapshot, V25["source"][1], V25["inputs"][1]),
         "independently reproduce all four original V25 owners without hiding a loss")
    return v25, old_summary, old_inputs, references


def authenticate_failure(archive_sha: str, receipt_sha: str,
                         references: dict[str, str]) -> tuple[dict, dict[str, str]]:
    need(checked_digest(archive_sha, "actual preserved Zig failure archive")
         == FAILURE_ARCHIVE[1]
         and checked_digest(receipt_sha, "actual preserved Zig failure receipt")
         == FAILURE_RECEIPT[1],
         "caller-pin both separately published genuine failure owners")
    preservation = load_module(
        PRESERVATION["source"], "_rebar_exact_zig_preflight_failure_v1_for_v26",
    )
    need(preservation.SCHEMA == "rebar-owned-zig-campaign-preflight-failure-v1"
         and preservation.LABEL == LABEL
         and digest(preservation.OBSERVED_STDERR) == STDERR_SHA256
         and len(preservation.OBSERVED_STDERR) == 1539
         and len(preservation.TRACEBACK_FRAMES) == 6,
         "authenticate the original pinned six-frame captured failure source")
    for key in ("protocol", "contract"):
        raw, _owner = read_owner(*PRESERVATION[key])
        if key == "contract":
            preservation.validate_contract(
                document(raw, "exact preserved preflight failure contract"),
                PRESERVATION["source"][1], PRESERVATION["protocol"][1],
            )
    archive_raw, archive_owner = read_owner(
        FAILURE_ARCHIVE[0], archive_sha, FAILURE_ARCHIVE[2], private=True,
        device=FAILURE_ARCHIVE[3], inode=FAILURE_ARCHIVE[4],
    )
    receipt_raw, receipt_owner = read_owner(
        FAILURE_RECEIPT[0], receipt_sha, FAILURE_RECEIPT[2], private=True,
        device=FAILURE_RECEIPT[3], inode=FAILURE_RECEIPT[4],
    )
    need((archive_owner["device"], archive_owner["inode"])
         != (receipt_owner["device"], receipt_owner["inode"])
         and archive_owner["uid"] == receipt_owner["uid"] == 1000
         and archive_owner["path"] not in references
         and receipt_owner["path"] not in references,
         "count only two genuinely new, distinct, private actual evidence owners")
    try:
        expanded = gzip.decompress(archive_raw)
    except (OSError, EOFError, gzip.BadGzipFile) as error:
        raise GraphError("reject malformed preserved Zig failure archive") from error
    need(0 < len(expanded) <= MAX_EXPANDED
         and len(expanded) == PLAIN_BYTES
         and digest(expanded) == PLAIN_SHA256
         and gzip.compress(expanded, compresslevel=9, mtime=0) == archive_raw,
         "require exactly one canonical zero-mtime genuine gzip failure member")
    report = document(expanded, "complete genuine Zig preflight failure report")
    receipt = document(receipt_raw, "genuine separately published failure receipt")
    expected_campaign = {
        name: preservation.pin(value)
        for name, value in sorted(preservation.CAMPAIGN.items())
    }
    controller = report.get("actual_once_only_controller")
    root_cause = report.get("root_cause")
    need(type(controller) is dict and type(root_cause) is dict,
         "retain the actual controller and independently proved ownership error")
    stderr = controller.get("stderr")
    stdout = controller.get("stdout")
    try:
        exact_stderr = base64.b64decode(stderr["base64"], validate=True)
    except (TypeError, ValueError, KeyError) as error:
        raise GraphError("reject a forged captured preflight traceback") from error
    expected_frames = [
        {"path": path, "line": line, "function": function}
        for path, line, function in preservation.TRACEBACK_FRAMES
    ]
    need(report.get("schema") == preservation.SCHEMA
         + "-actual-preserved-infrastructure-failure"
         and report.get("version") == 1
         and report.get("status") == "FAIL"
         and report.get("failure_class") == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
         and report.get("family") == "zig"
         and report.get("label") == LABEL
         and report.get("preservation_source_sha256") == PRESERVATION["source"][1]
         and report.get("preservation_protocol_sha256") == PRESERVATION["protocol"][1]
         and report.get("preservation_contract_sha256") == PRESERVATION["contract"][1]
         and report.get("original_campaign") == expected_campaign
         and controller.get("observation_provenance")
         == "EXACT PARENT-CAPTURED ONCE-ONLY ORIGINAL CAMPAIGN PROCESS"
         and controller.get("argv") == preservation.observed_argv()
         and controller.get("exit_status") == 1
         and controller.get("process_id") == "NOT RECORDED"
         and controller.get("process_id_recorded") is False
         and type(stdout) is dict
         and stdout == {"bytes": 0, "sha256": EMPTY_SHA256, "base64": ""}
         and type(stderr) is dict
         and stderr.get("bytes") == 1539
         and stderr.get("sha256") == STDERR_SHA256
         and stderr.get("complete") is True
         and exact_stderr == preservation.OBSERVED_STDERR
         and controller.get("traceback_frames") == expected_frames
         and controller.get("exception_type") == "ActivationError"
         and controller.get("exception_message")
         == "refuse an absent, linked, altered, or substituted original Zig engine inode",
         "authenticate the one real exit-1 controller, complete stderr, and all six frames")
    roles = root_cause.get("roles")
    originals = report.get("genuine_original_native_targets")
    need(root_cause.get("status") == "PASS"
         and root_cause.get("traceback_frame_count") == 6
         and root_cause.get("v6_missing_required_owner_fields") == ["nlink", "uid"]
         and root_cause.get("actual_canonical_target_reads") == 0
         and root_cause.get("actual_canonical_target_stats") == 0
         and type(roles) is dict and set(roles) == {"engine", "bridge"}
         and type(originals) is dict and set(originals) == {"engine", "bridge"},
         "preserve the actual missing owner fields without probing native targets")
    for role, expected in preservation.ORIGINALS.items():
        item = roles[role]
        native = originals[role]
        need(type(item) is dict and type(native) is dict
             and item.get("actual_canonical_target_inspected") is False
             and item.get("actual_mature_shape_matches") is False
             and item.get("normalized_shape_matches") is True
             and item.get("missing_fields") == ["nlink", "uid"]
             and item.get("original_device") == expected["device"]
             and item.get("original_inode") == expected["inode"]
             and item.get("original_sha256") == expected["sha256"]
             and item.get("original_bytes") == expected["bytes"]
             and item.get("original_mode") == "0700"
             and native.get("path") == expected["relative"]
             and native.get("sha256") == expected["sha256"]
             and native.get("bytes") == expected["bytes"]
             and native.get("device") == expected["device"]
             and native.get("inode") == expected["inode"]
             and native.get("mode") == "0700"
             and native.get("nlink") == 1 and native.get("uid") == 1000,
             "preserve the recorded unchanged actual original Zig " + role)
    states = report.get("original_campaign_evidence")
    need(type(states) is list and len(states) == 4
         and all(type(item) is dict and item.get("status") == "ABSENT"
                 for item in states)
         and report.get("original_campaign_archive_created") is False
         and report.get("original_campaign_receipt_created") is False
         and report.get("original_native_targets_unchanged") is True
         and report.get("native_target_restoration_required") is False
         and report.get("native_target_activation_occurred") is False
         and report.get("suite_count") == 13
         and report.get("case_execution_denominator") == 31237
         and report.get("private_waiver_count") == 13
         and report.get("completed_suite_count") == 0
         and report.get("actual_candidate_workers") == 0
         and report.get("actual_matching_case_execution_count") == 0
         and report.get("semantic_mismatch_count") == "NOT MEASURED"
         and report.get("candidate_correctness") == "NOT MEASURED"
         and report.get("candidate_qualified") is False
         and report.get("published_v25_evidence_owner_count") == 139
         and report.get("published_v25_authenticated_reference_count") == 144
         and report.get("actual_c_candidate_workers") == 13
         and report.get("actual_c_semantic_mismatch_count") == 1262
         and report.get("actual_c_verified_passing_case_count") == 7325
         and report.get("actual_zig_build_process_count") == 26
         and report.get("actual_rust_build_process_count") == 28
         and report.get("actual_rust_public_source_repair_count") == 2
         and report.get("actual_rust_bridge_source_repair_count") == 2
         and report.get("historical_rust_semantic_mismatch_count") == 2042
         and report.get("historical_zig_semantic_mismatch_count") == 1764
         and report.get("hidden_cases_read") == 0
         and report.get("benchmark_files_read") == 0
         and report.get("clock_samples") == 0
         and report.get("timing_trials_run") == 0
         and report.get("performance") == "NOT MEASURED"
         and report.get("memory") == "NOT MEASURED"
         and report.get("undefined_behavior") == "NOT MEASURED"
         and report.get("holdout") == "NOT OPENED"
         and report.get("winner_selected") is False
         and report.get("archive_published_only_after_original_targets_verified") is True,
         "never mistake a pre-activation infrastructure failure for Zig matching")
    archived = receipt.get("archive")
    need(type(archived) is dict
         and receipt.get("schema") == preservation.SCHEMA
         + "-durable-publication-receipt"
         and receipt.get("version") == 1
         and receipt.get("status") == "PASS"
         and receipt.get("preserved_failure_status") == "FAIL"
         and receipt.get("failure_class") == report["failure_class"]
         and receipt.get("family") == "zig"
         and receipt.get("label") == LABEL
         and receipt.get("source_sha256") == PRESERVATION["source"][1]
         and receipt.get("protocol_sha256") == PRESERVATION["protocol"][1]
         and receipt.get("contract_sha256") == PRESERVATION["contract"][1]
         and archived.get("path") == archive_owner["path"]
         and archived.get("sha256") == archive_owner["sha256"]
         and archived.get("bytes") == archive_owner["bytes"]
         and archived.get("device") == archive_owner["device"]
         and archived.get("inode") == archive_owner["inode"]
         and archived.get("mode") == "0600"
         and archived.get("nlink") == 1
         and archived.get("exclusive_creation") is True
         and archived.get("file_fsync_completed") is True
         and archived.get("directory_fsync_completed") is True
         and receipt.get("uncompressed_sha256") == digest(expanded)
         and receipt.get("uncompressed_bytes") == len(expanded)
         and receipt.get("actual_observed_controller_run_count") == 1
         and receipt.get("actual_observed_controller_exit_status") == 1
         and receipt.get("actual_observed_controller_process_id") == "NOT RECORDED"
         and receipt.get("actual_observed_stdout_sha256") == EMPTY_SHA256
         and receipt.get("actual_observed_stderr_sha256") == STDERR_SHA256
         and receipt.get("actual_candidate_workers") == 0
         and receipt.get("actual_native_activations") == 0
         and receipt.get("actual_matching_case_execution_count") == 0
         and receipt.get("candidate_correctness") == "NOT MEASURED"
         and receipt.get("semantic_mismatch_count") == "NOT MEASURED"
         and receipt.get("original_campaign_archive_created") is False
         and receipt.get("original_campaign_receipt_created") is False
         and receipt.get("original_native_targets_unchanged") is True
         and receipt.get("published_v25_evidence_owner_count") == 139
         and receipt.get("published_v25_authenticated_reference_count") == 144
         and receipt.get("new_repository_evidence_owner_count") == 2
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("benchmark_files_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("memory") == "NOT MEASURED"
         and receipt.get("undefined_behavior") == "NOT MEASURED"
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("winner_selected") is False,
         "require a distinct genuine durable receipt for the actual failed attempt")
    new_references = {
        archive_owner["path"]: archive_owner["sha256"],
        receipt_owner["path"]: receipt_owner["sha256"],
    }
    need(len(new_references) == 2 and not (set(references) & set(new_references)),
         "derive exactly two genuinely new digest-addressed evidence owners")
    proof = {
        "schema": SCHEMA + "-authenticated-zig-preflight-failure",
        "status": "FAIL",
        "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "family": "zig",
        "label": LABEL,
        "archive": archive_owner,
        "receipt": receipt_owner,
        "report": report,
        "publication_receipt": receipt,
        "preserved_failure_report_sha256": PLAIN_SHA256,
        "preserved_failure_report_bytes": PLAIN_BYTES,
        "observed_controller_run_count": 1,
        "observed_controller_exit_status": 1,
        "observed_controller_process_id": "NOT RECORDED",
        "observed_stderr_sha256": STDERR_SHA256,
        "observed_stderr_bytes": 1539,
        "actual_candidate_workers": 0,
        "actual_matching_case_execution_count": 0,
        "actual_native_activations": 0,
        "original_native_targets_unchanged": True,
        "candidate_correctness": "NOT MEASURED",
        "semantic_mismatch_count": "NOT MEASURED",
        "new_repository_evidence_owner_count": len(new_references),
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, new_references


def validate_proof(proof: object) -> None:
    need(type(proof) is dict
         and proof.get("schema") == SCHEMA + "-authenticated-zig-preflight-failure"
         and proof.get("status") == "FAIL"
         and proof.get("failure_class") == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
         and proof.get("family") == "zig"
         and proof.get("label") == LABEL
         and proof.get("preserved_failure_report_sha256") == PLAIN_SHA256
         and proof.get("preserved_failure_report_bytes") == PLAIN_BYTES
         and proof.get("observed_controller_run_count") == 1
         and proof.get("observed_controller_exit_status") == 1
         and proof.get("observed_controller_process_id") == "NOT RECORDED"
         and proof.get("observed_stderr_sha256") == STDERR_SHA256
         and proof.get("observed_stderr_bytes") == 1539
         and proof.get("actual_candidate_workers") == 0
         and proof.get("actual_matching_case_execution_count") == 0
         and proof.get("actual_native_activations") == 0
         and proof.get("original_native_targets_unchanged") is True
         and proof.get("candidate_correctness") == "NOT MEASURED"
         and proof.get("semantic_mismatch_count") == "NOT MEASURED"
         and proof.get("new_repository_evidence_owner_count") == 2
         and proof.get("performance") == "NOT MEASURED"
         and proof.get("memory") == "NOT MEASURED"
         and proof.get("undefined_behavior") == "NOT MEASURED"
         and proof.get("holdout") == "NOT OPENED"
         and proof.get("winner_selected") is False,
         "keep the genuine Zig setup failure separate from matching or timing")
    archive = proof.get("archive")
    receipt = proof.get("receipt")
    need(type(archive) is dict and type(receipt) is dict
         and archive.get("path") == FAILURE_ARCHIVE[0]
         and archive.get("sha256") == FAILURE_ARCHIVE[1]
         and archive.get("bytes") == FAILURE_ARCHIVE[2]
         and archive.get("device") == FAILURE_ARCHIVE[3]
         and archive.get("inode") == FAILURE_ARCHIVE[4]
         and archive.get("mode") == "0600"
         and archive.get("nlink") == 1 and archive.get("uid") == 1000
         and receipt.get("path") == FAILURE_RECEIPT[0]
         and receipt.get("sha256") == FAILURE_RECEIPT[1]
         and receipt.get("bytes") == FAILURE_RECEIPT[2]
         and receipt.get("device") == FAILURE_RECEIPT[3]
         and receipt.get("inode") == FAILURE_RECEIPT[4]
         and receipt.get("mode") == "0600"
         and receipt.get("nlink") == 1 and receipt.get("uid") == 1000
         and (archive["device"], archive["inode"])
         != (receipt["device"], receipt["inode"]),
         "reject missing, linked, substituted, or duplicated genuine failure owners")
    report = proof.get("report")
    published = proof.get("publication_receipt")
    need(type(report) is dict and type(published) is dict
         and report.get("status") == "FAIL"
         and published.get("status") == "PASS"
         and report.get("failure_class")
         == published.get("failure_class")
         == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
         and report.get("actual_candidate_workers") == 0
         and report.get("actual_matching_case_execution_count") == 0
         and report.get("semantic_mismatch_count") == "NOT MEASURED"
         and report.get("candidate_correctness") == "NOT MEASURED"
         and published.get("preserved_failure_status") == "FAIL"
         and published.get("actual_candidate_workers") == 0
         and published.get("actual_matching_case_execution_count") == 0,
         "never label a successful preservation receipt a passing Zig test")


def validate_snapshot(snapshot: object) -> None:
    need(type(snapshot) is dict
         and snapshot.get("full_case_denominator") == 31237
         and snapshot.get("suite_count") == 13
         and tuple(snapshot.get("suite_ids", ()))
         == tuple(name for name, _count, _difference, _display in SUITES)
         and snapshot.get("baseline_passed") == 31237
         and snapshot.get("frozen_independent_engine_family_count") == 6
         and snapshot.get("qualified_candidate_count") == 0
         and snapshot.get("preserved_v25_repository_evidence_owner_count") == 139
         and snapshot.get("preserved_v25_digest_addressed_history_path_count") == 144
         and snapshot.get("new_zig_preflight_failure_repository_evidence_owner_count") == 2
         and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 141
         and snapshot.get("all_digest_addressed_history_path_count") == 146,
         "retain all 31,237 original checks and derive genuine 139+2/144+2 owners")
    current = snapshot.get("c_v10_repaired_original_campaign")
    need(type(current) is dict and current.get("status") == "FAIL"
         and current.get("failure_class") == "SEMANTIC MISMATCH"
         and current.get("actual_candidate_workers") == 13
         and current.get("completed_suite_count") == 13
         and current.get("fully_passing_suite_count") == 8
         and current.get("observed_matching_case_count") == 31237
         and current.get("verified_passing_case_count") == 7325
         and current.get("semantic_mismatch_count") == 1262
         and current.get("infrastructure_failure_count") == 0
         and current.get("all_original_suite_evidence_preserved") is True
         and current.get("original_canonical_native_restored") is True
         and current.get("qualified") is False,
         "retain every genuine corrected C result, including all 1,262 differences")
    rows = current.get("suite_results")
    need(type(rows) is list and len(rows) == len(SUITES),
         "show all thirteen unchanged original C groups")
    for row, (name, count, differences, display) in zip(rows, SUITES, strict=True):
        need(type(row) is dict
             and row.get("suite") == name
             and row.get("display_name") == display
             and row.get("case_execution_denominator") == count
             and row.get("mismatch_count") == differences
             and row.get("status") == ("PASS" if differences == 0 else "FAIL")
             and row.get("actual_worker_started") is True
             and row.get("all_original_records_and_mismatches_preserved") is True,
             "reject a changed original C matching group: " + name)
    need(snapshot.get("c_actual_semantic_mismatch_count") == 2094
         and snapshot.get("c_verified_passing_case_executions") == 7197
         and snapshot.get("rust_actual_semantic_mismatch_count") == 2042
         and snapshot.get("rust_verified_passing_case_executions") == 7461
         and snapshot.get("zig_actual_semantic_mismatch_count") == 1764
         and snapshot.get("zig_verified_passing_case_executions") == 3583
         and type(snapshot.get("cpp_full_original_campaign")) is dict
         and snapshot["cpp_full_original_campaign"].get("semantic_mismatch_count") == 2308
         and type(snapshot.get("go_v2_full_original_campaign")) is dict
         and snapshot["go_v2_full_original_campaign"].get("semantic_mismatch_count") == 4518,
         "retain every historical C, Rust, Zig, C++, and Go matching loss")
    need(snapshot.get("zig_scanner_repaired_build_status") == "PASS"
         and snapshot.get("zig_scanner_repaired_build_process_count") == 26
         and snapshot.get("zig_scanner_repaired_source_apply_count") == 2
         and snapshot.get("zig_scanner_repaired_reproducibility") == "PASS"
         and snapshot.get("zig_scanner_repaired_matching_status") == "NOT MEASURED"
         and snapshot.get("zig_scanner_repaired_candidate_worker_count") == 0
         and snapshot.get("zig_scanner_repaired_candidate_qualified") is False
         and snapshot.get("rust_dual_overlay_repaired_build_status") == "PASS"
         and snapshot.get("rust_dual_overlay_repaired_build_process_count") == 28
         and snapshot.get("rust_dual_overlay_repaired_bridge_source_apply_count") == 2
         and snapshot.get("rust_dual_overlay_repaired_public_source_apply_count") == 2
         and snapshot.get("rust_dual_overlay_repaired_reproducibility") == "PASS"
         and snapshot.get("rust_dual_overlay_repaired_matching_status") == "NOT MEASURED"
         and snapshot.get("rust_dual_overlay_repaired_candidate_worker_count") == 0
         and snapshot.get("rust_dual_overlay_repaired_candidate_qualified") is False
         and snapshot.get("repaired_c_full_matching_test_status")
         == "FAIL: 1,262 SEMANTIC MISMATCHES"
         and snapshot.get("repaired_c_actual_verified_matching_case_count") == 31237
         and snapshot.get("repaired_c_verified_passing_case_count") == 7325
         and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
         and snapshot.get("repaired_c_infrastructure_failure_count") == 0
         and snapshot.get("repaired_c_completed_suite_count") == 13
         and snapshot.get("repaired_c_actual_candidate_worker_count") == 13
         and snapshot.get("repaired_c_native_promoted") is False,
         "distinguish genuine first-party builds from measured C and untested Zig")
    validate_proof(snapshot.get("zig_original_campaign_preflight_failure"))
    need(snapshot.get("zig_original_campaign_attempt_count") == 1
         and snapshot.get("zig_original_campaign_controller_exit_status") == 1
         and snapshot.get("zig_original_campaign_controller_process_id") == "NOT RECORDED"
         and snapshot.get("zig_original_campaign_failure_class")
         == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
         and snapshot.get("zig_original_campaign_actual_candidate_worker_count") == 0
         and snapshot.get("zig_original_campaign_actual_matching_case_count") == 0
         and snapshot.get("zig_original_campaign_semantic_mismatch_count") == "NOT MEASURED"
         and snapshot.get("zig_original_campaign_matching_status") == "NOT MEASURED"
         and snapshot.get("zig_original_campaign_original_targets_unchanged") is True
         and snapshot.get("performance") == "NOT MEASURED"
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
         "never turn a setup failure into matching, speed, a ranking, or an opened holdout")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def make_svg(snapshot: dict, source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(snapshot)
    checked_digest(source_sha, "frozen V26 renderer")
    checked_digest(inputs_sha, "frozen V26 graph inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1960" viewBox="0 0 1440 1960" role="img" aria-labelledby="v26-title v26-description">',
        '<title id="v26-title">Building a faster Python re: the first repaired Zig test stopped before matching</title>',
        '<desc id="v26-description">Python passes all 31,237 frozen checks. A real repaired Zig test controller stopped once during setup, before activation and before any matching worker started. Both original native Zig files were unchanged. A durable archive and its separate receipt preserve the complete failure, producing 141 distinct actual evidence files and 146 authenticated references. The independent Rust and Zig source builds completed 28 and 26 actual steps, but their repaired matching remains unmeasured. The independently tested C engine has 1,262 genuine matching differences across all 13 original groups. Earlier Rust, Zig, C, C++, and Go losses remain visible. No replacement qualifies. Speed, memory, confidence intervals, rankings, and undefined behavior are not measured; the 4,194,304-case final holdout has not been opened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:31px;font-weight:760;fill:#16324f}.heading{font-size:22px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:16px;font-weight:720;fill:#16324f}.pass{font-size:14px;font-weight:750;fill:#00794c}.fail{font-size:14px;font-weight:740;fill:#a15e00}.pending{font-size:14px;font-weight:740;fill:#53667b}.big{font-size:23px;font-weight:760;fill:#16324f}.small{font-size:13px;fill:#42556c}.foot{font-size:11px;fill:#53667b}</style>',
        '<rect width="1440" height="1960" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="61" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="46" y="91" class="body">The new Zig test stopped during setup. No matching test ran, so correctness and speed are NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0", "compatible replacements"),
        ("1,262", "measured C differences"),
        ("1", "recorded Zig setup failure"),
        ("NOT MEASURED", "speed versus Python"),
        ("141 / 146", "evidence files / references"),
    )
    for index, (value, label) in enumerate(cards):
        x = 44 + index * 226
        lines.extend((
            f'<rect x="{x}" y="111" width="216" height="96" rx="12" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 11}" y="151" class="big">{xml(value)}</text>',
            f'<text x="{x + 11}" y="181" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="224" width="1352" height="734" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="262" class="heading">1. Does each replacement work like Python?</text>',
        '<text x="65" y="287" class="body">A successful build is not a passed matching test. A setup failure is not a matching result.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original checks pass; this is the compatibility baseline.", "pass"),
        ("Zig — newly repaired engine", "SETUP STOPPED; 0 TESTS", "One real controller exited 1 before activation or matching. Both original Zig files were unchanged.", "fail"),
        ("Rust — newly repaired engine", "BUILT; MATCHING NOT MEASURED", "28 genuine first-party build and inspection steps; independently repeated native outputs.", "pending"),
        ("C — latest repaired engine", "NOT COMPATIBLE", "All 13 groups ran: 7,325 verified passing checks and 1,262 matching differences.", "fail"),
        ("Rust — previously tested engine", "NOT COMPATIBLE", "7,461 verified passing checks; 2,042 recorded matching differences.", "fail"),
        ("Zig — previously tested engine", "NOT COMPATIBLE", "3,583 verified passing checks; 1,764 recorded matching differences.", "fail"),
        ("C — earlier tested engine", "NOT COMPATIBLE", "7,197 verified passing checks; 2,094 recorded matching differences.", "fail"),
        ("C++", "NOT COMPATIBLE", "128 verified passing checks; 2,308 recorded differences and 5 earlier worker failures.", "fail"),
        ("Go", "NOT COMPATIBLE", "128 verified passing checks; 4,518 recorded differences and 4 earlier worker failures.", "fail"),
        ("Fortran", "NOT READY", "Independent build attempts differ; no compatible matching engine has been established.", "pending"),
    )
    for index, (name, outcome, detail, category) in enumerate(rows):
        y = 305 + index * 61
        lines.extend((
            f'<rect x="63" y="{y}" width="1314" height="54" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="79" y="{y + 21}" class="name">{xml(name)}</text>',
            f'<text x="1358" y="{y + 21}" class="{category}" text-anchor="end">{xml(outcome)}</text>',
            f'<text x="81" y="{y + 42}" class="small">{xml(detail)}</text>',
        ))
    lines.append('<text x="65" y="943" class="body">The first-party Zig build itself previously completed 26 genuine steps; the interrupted controller did not test it.</text>')
    lines.extend((
        '<rect x="44" y="975" width="1352" height="558" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1013" class="heading">2. Which complete C test groups still differ?</text>',
        '<text x="65" y="1038" class="body">Every original group and every loss remains visible. A passed example inside a failed group is not a passing group.</text>',
        '<text x="80" y="1062" class="small">ORIGINAL PYTHON TEST GROUP</text>',
        '<text x="1040" y="1062" class="small" text-anchor="end">CHECKS</text>',
        '<text x="1355" y="1062" class="small" text-anchor="end">RESULT</text>',
    ))
    for index, row in enumerate(snapshot["c_v10_repaired_original_campaign"]["suite_results"]):
        y = 1073 + index * 30
        background = "#f8fafd" if index % 2 == 0 else "#ffffff"
        result = ("PASSED" if row["mismatch_count"] == 0
                  else f'{row["mismatch_count"]:,} DIFFERENCES')
        category = "pass" if row["mismatch_count"] == 0 else "fail"
        lines.extend((
            f'<rect x="64" y="{y}" width="1312" height="27" rx="4" fill="{background}"/>',
            f'<text x="80" y="{y + 19}" class="small">{xml(row["display_name"])}</text>',
            f'<text x="1040" y="{y + 19}" class="small" text-anchor="end">{row["case_execution_denominator"]:,}</text>',
            f'<text x="1355" y="{y + 19}" class="{category}" text-anchor="end">{xml(result)}</text>',
        ))
    lines.extend((
        '<text x="66" y="1497" class="body">Eight complete groups passed; five contain all 1,262 recorded C differences. All 13 real workers ran.</text>',
        '<rect x="44" y="1550" width="1352" height="304" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1588" class="heading">3. Is any replacement faster?</text>',
        '<text x="66" y="1620" class="body">NOT MEASURED. No replacement has first passed every original Python compatibility check.</text>',
        '<text x="66" y="1650" class="body">There is no speed or memory comparison, confidence interval, performance ranking, or winner.</text>',
        '<text x="66" y="1680" class="body">The expanded 4,194,304-case final comparison is not generated and has not been opened.</text>',
        '<text x="66" y="1710" class="body">Evidence: 139 previously verified files + the real Zig failure archive and its distinct receipt = 141 files.</text>',
        '<text x="66" y="1740" class="body">All 146 independently authenticated references retain every historical result and genuine setup failure.</text>',
        '<text x="66" y="1770" class="body">Receipt PASS means the failure was safely preserved. The Zig matching attempt itself remains FAIL / NOT MEASURED.</text>',
        '<text x="66" y="1800" class="body">The original Zig engine and Python bridge retained their recorded original identities and permissions.</text>',
        f'<text x="47" y="1884" class="foot">Inputs SHA-256: {xml(inputs_sha)}</text>',
        f'<text x="47" y="1906" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="47" y="1928" class="foot">Actual Zig failure archive: {xml(FAILURE_ARCHIVE[1])}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(source_sha: str, archive_sha: str,
          receipt_sha: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked_digest(source_sha, "V26 renderer source")
    source_raw, _source_owner = read_owner(SELF, source_sha)
    v25, old_summary, old_inputs, references = authenticate_v25()
    proof, additions = authenticate_failure(archive_sha, receipt_sha, references)
    need(len(references) == 144 and len(additions) == 2
         and not (set(references) & set(additions)),
         "require independently authenticated, disjoint V25 and preserved-failure owners")
    all_references = dict(references)
    all_references.update(additions)
    owner_count = old_summary["repository_evidence_owner_count"] + len(additions)
    need(owner_count == 141 and len(all_references) == 146,
         "derive 141/146 exclusively from actual distinct evidence owners")
    previous_snapshot = old_summary["snapshot"]
    v25.validate_snapshot(previous_snapshot)
    snapshot = copy.deepcopy(previous_snapshot)
    snapshot.update({
        "preserved_v25_repository_evidence_owner_count":
            old_summary["repository_evidence_owner_count"],
        "preserved_v25_digest_addressed_history_path_count": len(references),
        "new_zig_preflight_failure_repository_evidence_owner_count": len(additions),
        "all_actual_candidate_and_native_evidence_owner_count": owner_count,
        "all_digest_addressed_history_path_count": len(all_references),
        "zig_original_campaign_preflight_failure": copy.deepcopy(proof),
        "zig_original_campaign_attempt_count": 1,
        "zig_original_campaign_controller_exit_status": 1,
        "zig_original_campaign_controller_process_id": "NOT RECORDED",
        "zig_original_campaign_failure_class":
            "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "zig_original_campaign_actual_candidate_worker_count": 0,
        "zig_original_campaign_actual_matching_case_count": 0,
        "zig_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_original_campaign_matching_status": "NOT MEASURED",
        "zig_original_campaign_original_targets_unchanged": True,
    })
    validate_snapshot(snapshot)
    previous_pins = {
        key: pin(path, fingerprint, count)
        for key, (path, fingerprint, count) in sorted(V25.items())
    }
    preservation_pins = {
        key: pin(path, fingerprint, count)
        for key, (path, fingerprint, count) in sorted(PRESERVATION.items())
    }
    manifest = {
        "schema": SCHEMA + "-inputs", "version": 26, "python": "3.14.6",
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
        "preserved_zig_preflight_failure_source_freeze": preservation_pins,
        "preserved_zig_original_campaign_preflight_failure": copy.deepcopy(proof),
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "candidate_families": copy.deepcopy(old_inputs["candidate_families"]),
        "candidate_qualified_count": 0,
        "preserved_v25_repository_evidence_owner_count":
            old_summary["repository_evidence_owner_count"],
        "preserved_v25_digest_addressed_history_path_count": len(references),
        "new_zig_preflight_failure_repository_evidence_owner_count": len(additions),
        "repository_evidence_owner_count": owner_count,
        "all_digest_addressed_history_path_count": len(all_references),
        "actual_zig_candidate_workers": 0,
        "actual_zig_matching_case_execution_count": 0,
        "zig_matching_test_status": "NOT MEASURED",
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
            family["current_scanner_repaired_matching_test_status"] = "NOT MEASURED"
            family["current_scanner_repaired_candidate_worker_count"] = 0
            family["current_original_campaign_preflight_failure"] = copy.deepcopy(proof)
            family["current_original_campaign_attempt_count"] = 1
            family["current_original_campaign_controller_exit_status"] = 1
            family["current_original_campaign_matching_case_count"] = 0
            family["current_original_campaign_matching_test_status"] = "NOT MEASURED"
            family["current_original_campaign_original_targets_unchanged"] = True
            family["qualified"] = False
    need(zig_count == 1,
         "retain exactly one independently authored first-party Zig candidate family")
    summary = {
        "schema": SCHEMA + "-summary", "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_sha, len(source_raw)),
        "inputs": pin(OUTPUT + ".inputs.json", manifest_sha, len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(picture), len(picture)),
        "previous_overview": previous_pins,
        "preserved_zig_preflight_failure_source_freeze": preservation_pins,
        "snapshot": snapshot,
        "families": families,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "preserved_v25_repository_evidence_owner_count":
            old_summary["repository_evidence_owner_count"],
        "preserved_v25_authenticated_reference_path_count": len(references),
        "new_zig_preflight_failure_repository_evidence_owner_count": len(additions),
        "repository_evidence_owner_count": owner_count,
        "authenticated_digest_addressed_history_paths": len(all_references),
        "qualified_candidate_count": 0,
        "zig_original_campaign_preflight_failure": copy.deepcopy(proof),
        "zig_original_campaign_attempt_count": 1,
        "zig_original_campaign_controller_exit_status": 1,
        "zig_original_campaign_controller_process_id": "NOT RECORDED",
        "zig_original_campaign_failure_class":
            "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "zig_original_campaign_candidate_worker_count": 0,
        "zig_original_campaign_matching_case_execution_count": 0,
        "zig_original_campaign_matching_test_status": "NOT MEASURED",
        "zig_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_original_campaign_original_targets_unchanged": True,
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
        "zig_scanner_repaired_matching_test_status": "NOT MEASURED",
        "zig_scanner_repaired_candidate_worker_count": 0,
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

        def blocked(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GraphError("V26 source-only side effect blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir", "makedirs",
                  "unlink", "remove", "replace", "rename", "system", "fork",
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
        "path": FAILURE_ARCHIVE[0], "sha256": FAILURE_ARCHIVE[1],
        "bytes": FAILURE_ARCHIVE[2], "device": FAILURE_ARCHIVE[3],
        "inode": FAILURE_ARCHIVE[4], "mode": "0600", "nlink": 1, "uid": 1000,
    }
    receipt = {
        "path": FAILURE_RECEIPT[0], "sha256": FAILURE_RECEIPT[1],
        "bytes": FAILURE_RECEIPT[2], "device": FAILURE_RECEIPT[3],
        "inode": FAILURE_RECEIPT[4], "mode": "0600", "nlink": 1, "uid": 1000,
    }
    report = {
        "status": "FAIL", "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "actual_candidate_workers": 0, "actual_matching_case_execution_count": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
    }
    published = {
        "status": "PASS", "preserved_failure_status": "FAIL",
        "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "actual_candidate_workers": 0, "actual_matching_case_execution_count": 0,
    }
    return {
        "schema": SCHEMA + "-authenticated-zig-preflight-failure",
        "status": "FAIL", "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "family": "zig", "label": LABEL,
        "archive": archive, "receipt": receipt,
        "report": report, "publication_receipt": published,
        "preserved_failure_report_sha256": PLAIN_SHA256,
        "preserved_failure_report_bytes": PLAIN_BYTES,
        "observed_controller_run_count": 1,
        "observed_controller_exit_status": 1,
        "observed_controller_process_id": "NOT RECORDED",
        "observed_stderr_sha256": STDERR_SHA256,
        "observed_stderr_bytes": 1539,
        "actual_candidate_workers": 0,
        "actual_matching_case_execution_count": 0,
        "actual_native_activations": 0,
        "original_native_targets_unchanged": True,
        "candidate_correctness": "NOT MEASURED",
        "semantic_mismatch_count": "NOT MEASURED",
        "new_repository_evidence_owner_count": 2,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def synthetic_snapshot() -> dict:
    rows = [{
        "suite": name, "display_name": display,
        "status": "PASS" if differences == 0 else "FAIL",
        "case_execution_denominator": count,
        "mismatch_count": differences,
        "actual_worker_started": True,
        "all_original_records_and_mismatches_preserved": True,
    } for name, count, differences, display in SUITES]
    current = {
        "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
        "actual_candidate_workers": 13,
        "completed_suite_count": 13, "fully_passing_suite_count": 8,
        "observed_matching_case_count": 31237,
        "verified_passing_case_count": 7325,
        "semantic_mismatch_count": 1262,
        "infrastructure_failure_count": 0,
        "all_original_suite_evidence_preserved": True,
        "original_canonical_native_restored": True,
        "qualified": False, "suite_results": rows,
    }
    return {
        "full_case_denominator": 31237,
        "suite_count": 13,
        "suite_ids": [name for name, _count, _differences, _display in SUITES],
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v25_repository_evidence_owner_count": 139,
        "preserved_v25_digest_addressed_history_path_count": 144,
        "new_zig_preflight_failure_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 141,
        "all_digest_addressed_history_path_count": 146,
        "c_v10_repaired_original_campaign": current,
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
        "zig_scanner_repaired_matching_status": "NOT MEASURED",
        "zig_scanner_repaired_candidate_worker_count": 0,
        "zig_scanner_repaired_candidate_qualified": False,
        "rust_dual_overlay_repaired_build_status": "PASS",
        "rust_dual_overlay_repaired_build_process_count": 28,
        "rust_dual_overlay_repaired_bridge_source_apply_count": 2,
        "rust_dual_overlay_repaired_public_source_apply_count": 2,
        "rust_dual_overlay_repaired_reproducibility": "PASS",
        "rust_dual_overlay_repaired_matching_status": "NOT MEASURED",
        "rust_dual_overlay_repaired_candidate_worker_count": 0,
        "rust_dual_overlay_repaired_candidate_qualified": False,
        "repaired_c_full_matching_test_status": "FAIL: 1,262 SEMANTIC MISMATCHES",
        "repaired_c_actual_verified_matching_case_count": 31237,
        "repaired_c_verified_passing_case_count": 7325,
        "repaired_c_semantic_mismatch_count": 1262,
        "repaired_c_infrastructure_failure_count": 0,
        "repaired_c_completed_suite_count": 13,
        "repaired_c_actual_candidate_worker_count": 13,
        "repaired_c_native_promoted": False,
        "zig_original_campaign_preflight_failure": synthetic_proof(),
        "zig_original_campaign_attempt_count": 1,
        "zig_original_campaign_controller_exit_status": 1,
        "zig_original_campaign_controller_process_id": "NOT RECORDED",
        "zig_original_campaign_failure_class":
            "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "zig_original_campaign_actual_candidate_worker_count": 0,
        "zig_original_campaign_actual_matching_case_count": 0,
        "zig_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_original_campaign_matching_status": "NOT MEASURED",
        "zig_original_campaign_original_targets_unchanged": True,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def self_test() -> dict:
    runtime()
    with SourceOnlyWall() as wall:
        base = synthetic_snapshot()
        validate_snapshot(base)
        rejected = 0

        def reject_snapshot(value: dict) -> None:
            nonlocal rejected
            try:
                validate_snapshot(value)
            except (GraphError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise GraphError("acceptance of forged V26 history is forbidden")

        changed = {
            "full_case_denominator": 31236,
            "suite_count": 12,
            "baseline_passed": 31236,
            "frozen_independent_engine_family_count": 5,
            "qualified_candidate_count": 1,
            "preserved_v25_repository_evidence_owner_count": 138,
            "preserved_v25_digest_addressed_history_path_count": 143,
            "new_zig_preflight_failure_repository_evidence_owner_count": 1,
            "all_actual_candidate_and_native_evidence_owner_count": 140,
            "all_digest_addressed_history_path_count": 145,
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
            "zig_scanner_repaired_matching_status": "PASS",
            "zig_scanner_repaired_candidate_worker_count": 1,
            "zig_scanner_repaired_candidate_qualified": True,
            "rust_dual_overlay_repaired_build_status": "FAIL",
            "rust_dual_overlay_repaired_build_process_count": 27,
            "rust_dual_overlay_repaired_bridge_source_apply_count": 1,
            "rust_dual_overlay_repaired_public_source_apply_count": 1,
            "rust_dual_overlay_repaired_reproducibility": "FAIL",
            "rust_dual_overlay_repaired_matching_status": "PASS",
            "rust_dual_overlay_repaired_candidate_worker_count": 1,
            "rust_dual_overlay_repaired_candidate_qualified": True,
            "repaired_c_full_matching_test_status": "PASS",
            "repaired_c_actual_verified_matching_case_count": 7325,
            "repaired_c_verified_passing_case_count": 31237,
            "repaired_c_semantic_mismatch_count": 0,
            "repaired_c_infrastructure_failure_count": 1,
            "repaired_c_completed_suite_count": 12,
            "repaired_c_actual_candidate_worker_count": 12,
            "repaired_c_native_promoted": True,
            "zig_original_campaign_attempt_count": 0,
            "zig_original_campaign_controller_exit_status": 0,
            "zig_original_campaign_controller_process_id": 12345,
            "zig_original_campaign_failure_class": "SEMANTIC MISMATCH",
            "zig_original_campaign_actual_candidate_worker_count": 1,
            "zig_original_campaign_actual_matching_case_count": 1,
            "zig_original_campaign_semantic_mismatch_count": 0,
            "zig_original_campaign_matching_status": "PASS",
            "zig_original_campaign_original_targets_unchanged": False,
            "performance": "1.5x faster",
            "memory": "0 bytes",
            "confidence_intervals": "95%",
            "hidden_cases_read": 1,
            "performance_files_read": 1,
            "clock_samples": 1,
            "timing_trials_run": 1,
            "final_comparison_planned_case_count": 4194303,
            "final_comparison_cases_generated": True,
            "final_holdout_opened": True,
            "winner_selected": True,
        }
        for key, forged in changed.items():
            altered = copy.deepcopy(base)
            altered[key] = forged
            reject_snapshot(altered)
        proof_changes = {
            "schema": "forged",
            "status": "PASS",
            "failure_class": "SEMANTIC MISMATCH",
            "family": "rust",
            "label": "forged",
            "preserved_failure_report_sha256": "0" * 64,
            "preserved_failure_report_bytes": PLAIN_BYTES - 1,
            "observed_controller_run_count": 0,
            "observed_controller_exit_status": 0,
            "observed_controller_process_id": 12345,
            "observed_stderr_sha256": "0" * 64,
            "observed_stderr_bytes": 1538,
            "actual_candidate_workers": 1,
            "actual_matching_case_execution_count": 1,
            "actual_native_activations": 1,
            "original_native_targets_unchanged": False,
            "candidate_correctness": "PASS",
            "semantic_mismatch_count": 0,
            "new_repository_evidence_owner_count": 1,
            "performance": "1.5x faster",
            "memory": "0 bytes",
            "undefined_behavior": "PASS",
            "holdout": "OPENED",
            "winner_selected": True,
        }
        for key, forged in proof_changes.items():
            altered = copy.deepcopy(base)
            altered["zig_original_campaign_preflight_failure"][key] = forged
            reject_snapshot(altered)
        for role, field, forged in (
            ("archive", "sha256", "0" * 64),
            ("archive", "inode", FAILURE_RECEIPT[4]),
            ("archive", "mode", "0644"),
            ("archive", "nlink", 2),
            ("receipt", "sha256", "0" * 64),
            ("receipt", "inode", FAILURE_ARCHIVE[4]),
            ("receipt", "mode", "0644"),
            ("receipt", "nlink", 2),
        ):
            altered = copy.deepcopy(base)
            altered["zig_original_campaign_preflight_failure"][role][field] = forged
            reject_snapshot(altered)
        for index, (_name, _count, _differences, _display) in enumerate(SUITES):
            altered = copy.deepcopy(base)
            altered["c_v10_repaired_original_campaign"]["suite_results"][index]["mismatch_count"] += 1
            reject_snapshot(altered)
        for name in ("cpp_full_original_campaign", "go_v2_full_original_campaign"):
            altered = copy.deepcopy(base)
            altered[name]["semantic_mismatch_count"] = 0
            reject_snapshot(altered)
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"SETUP STOPPED; 0 TESTS", b"1,262", b"2,042", b"1,764",
            b"2,308", b"4,518", b"31,237", b"141 / 146",
            b"NOT MEASURED", b"both original native Zig files were unchanged",
        ):
            need(phrase.lower() in picture.lower(),
                 "the accessible V26 graph hides a genuine result or setup failure")
        side_effects = (
            lambda: builtins.open("forbidden-v26-owner"),
            lambda: io.open("forbidden-v26-owner"),
            lambda: os.open("forbidden-v26-owner", os.O_RDONLY),
            lambda: os.stat("forbidden-v26-owner"),
            lambda: subprocess.run(("forbidden-v26-candidate",)),
            lambda: importlib.import_module("candidates.zig_candidate"),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for action in side_effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("a V26 synthetic self-test permitted a real side effect")
        need(wall.blocked == len(side_effects),
             "block every attempted source-only filesystem, worker, clock, and network effect")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 26,
            "status": "PASS",
            "synthetic_only": True,
            "accepted_control_count": 1,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "suite_count": 13,
            "full_case_denominator": 31237,
            "preserved_v25_repository_evidence_owner_count": 139,
            "preserved_v25_authenticated_reference_count": 144,
            "new_actual_preserved_failure_evidence_owner_count": 2,
            "repository_evidence_owner_count": 141,
            "authenticated_digest_addressed_history_paths": 146,
            "actual_zig_controller_attempts": 1,
            "actual_zig_controller_exit_status": 1,
            "actual_zig_controller_process_id": "NOT RECORDED",
            "actual_zig_candidate_workers": 0,
            "actual_zig_matching_case_execution_count": 0,
            "historical_rust_semantic_mismatch_count": 2042,
            "historical_zig_semantic_mismatch_count": 1764,
            "current_c_semantic_mismatch_count": 1262,
            "current_c_verified_passing_case_count": 7325,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "actual_candidate_workers": 0,
            "actual_native_activations": 0,
            "canonical_target_reads": 0,
            "canonical_target_stats": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
            "synthetic_svg_sha256": digest(picture),
        }


def publish_output(path: str, raw: bytes) -> None:
    allowed = {
        OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg",
    }
    need(path in allowed and type(raw) is bytes and 0 < len(raw) <= MAX_OWNER,
         "publish only one of the three exact bounded new V26 graph owners")
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
                 "reject incomplete exclusive V26 graph publication")
            position += count
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        need(stat.S_ISREG(owner.st_mode)
             and owner.st_size == len(raw)
             and owner.st_nlink == 1
             and stat.S_IMODE(owner.st_mode) == 0o600,
             "reject linked, incomplete, or nonprivate V26 graph output")
    finally:
        os.close(descriptor)


def result(source_sha: str, archive_sha: str, receipt_sha: str,
           outputs: dict[str, bytes], *, written: bool,
           schema: str) -> dict:
    return {
        "schema": SCHEMA + schema,
        "version": 26,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_zig_failure_archive_sha256": archive_sha,
        "actual_zig_failure_receipt_sha256": receipt_sha,
        "suite_count": 13,
        "full_case_denominator": 31237,
        "private_waiver_count": 13,
        "candidate_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v25_repository_evidence_owner_count": 139,
        "preserved_v25_authenticated_reference_count": 144,
        "new_actual_preserved_failure_evidence_owner_count": 2,
        "repository_evidence_owner_count": 141,
        "authenticated_digest_addressed_history_paths": 146,
        "zig_preflight_failure_status": "FAIL",
        "zig_preflight_failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "actual_zig_controller_attempts": 1,
        "actual_zig_controller_exit_status": 1,
        "actual_zig_controller_process_id": "NOT RECORDED",
        "actual_zig_candidate_workers": 0,
        "actual_zig_matching_case_execution_count": 0,
        "actual_zig_native_activations": 0,
        "zig_original_native_targets_unchanged": True,
        "zig_matching_test_status": "NOT MEASURED",
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
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--failure-archive-sha256")
    parser.add_argument("--failure-receipt-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        runtime()
        if options.self_test:
            need(all(getattr(options, name) is None for name in (
                "source_sha256", "failure_archive_sha256",
                "failure_receipt_sha256", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            )), "a synthetic self-test never authorizes frozen evidence or rendering")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source_sha = checked_digest(options.source_sha256, "V26 renderer source")
        archive_sha = checked_digest(options.failure_archive_sha256,
                                     "actual preserved Zig failure archive")
        receipt_sha = checked_digest(options.failure_receipt_sha256,
                                     "actual preserved Zig failure receipt")
        _snapshot, raw_outputs = build(source_sha, archive_sha, receipt_sha)
        outputs = dict(raw_outputs)
        if options.render:
            need(options.inputs_sha256 is None
                 and options.summary_sha256 is None
                 and options.svg_sha256 is None,
                 "exclusive once-only rendering must not accept substituted output pins")
            for path, raw in raw_outputs:
                publish_output(path, raw)
            sys.stdout.buffer.write(canonical(result(
                source_sha, archive_sha, receipt_sha, outputs,
                written=True, schema="-published",
            )))
            return 0
        expected_pins = {
            OUTPUT + ".inputs.json": checked_digest(
                options.inputs_sha256, "published V26 graph inputs"),
            OUTPUT + ".json": checked_digest(
                options.summary_sha256, "published V26 graph summary"),
            OUTPUT + ".svg": checked_digest(
                options.svg_sha256, "published V26 accessible graph"),
        }
        for path, fingerprint in expected_pins.items():
            raw, _owner = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(raw == outputs[path],
                 "independently reproduce every original published V26 graph byte")
        sys.stdout.buffer.write(canonical(result(
            source_sha, archive_sha, receipt_sha, outputs,
            written=False, schema="-read-only-frozen-context",
        )))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            gzip.BadGzipFile, KeyError, AttributeError) as error:
        sys.stderr.write("current V26 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
