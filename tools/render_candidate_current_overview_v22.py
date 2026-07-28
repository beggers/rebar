#!/usr/bin/env python3
"""Render the actual, zero-worker corrected-C runner failure without guesses."""

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
from pathlib import Path, PurePosixPath
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
SCHEMA = "rebar-candidate-current-overview-v22"
SELF = "tools/render_candidate_current_overview_v22.py"
OUTPUT = "docs/evidence/candidate-current-overview-v22"
MAX_FILE = 64 * 1024 * 1024
MAX_REPORT = 4 * 1024 * 1024
V21 = {
    "source": (
        "tools/render_candidate_current_overview_v21.py",
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v21.inputs.json",
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v21.json",
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v21.svg",
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
    ),
}
CURRENT_ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures.json.gz",
    "a37a70f7ab9e4dcc72b176ca51fb1bfe8514d906431e8f02f269871a8b946810",
    2496,
)
CURRENT_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v2-c-phase2-v9-original-p0-"
    "failures-publication-receipt.json",
    "8a16520de9ac80aac1a6ea6d9a6cec3778379d35a611a52a2bca692685645c81",
    934,
)
CURRENT_UNCOMPRESSED_SHA256 = (
    "5aa8b513eec30c7ab13bc4b638a5b5026a6f03821f8cd411f6ea3201b0813cfd"
)
CURRENT_UNCOMPRESSED_BYTES = 5941
INNER_STDOUT_SHA256 = (
    "93899f2cfc24a638785af66e683ca2f0866488be9cfbcdc2ffdd73be1b8e3f65"
)
INNER_STDOUT_BYTES = 517
INNER_FAILURE = "'Namespace' object has no attribute 'runner_source_sha256'"
LABEL = "phase2-v9-original-p0"
ORIGINAL_NATIVE = (
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd",
    149976,
)
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
OLD_EVIDENCE_OWNERS = 103
OLD_REFERENCE_PATHS = 108
NEW_EVIDENCE_OWNERS = 2
EVIDENCE_OWNERS = OLD_EVIDENCE_OWNERS + NEW_EVIDENCE_OWNERS
REFERENCE_PATHS = OLD_REFERENCE_PATHS + NEW_EVIDENCE_OWNERS


class GraphError(Exception):
    """The independently observed corrected-C result cannot be proven."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(value: bytes) -> str:
    need(type(value) is bytes, "hash only complete evidence bytes")
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise GraphError("invalid canonical V22 evidence") from error


def checked_digest(value: object, label: str) -> str:
    need(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "invalid " + label + " SHA-256",
    )
    return value


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode
        and os.path.abspath(sys.executable) == PYTHON
        and os.path.realpath(sys.executable) == PYTHON,
        "use only the isolated, pinned CPython 3.14.6 oracle",
    )


def pinned(value: dict, path: str, sha: str, size: int) -> None:
    need(
        type(value) is dict
        and value.get("relative") == path
        and value.get("sha256") == sha
        and value.get("size_bytes") == size
        and type(value.get("device")) is int
        and type(value.get("inode")) is int
        and value.get("mode") == 0o600,
        "require the exact independently owned evidence file: " + path,
    )


def decode_stream(process: dict, name: str) -> bytes:
    value = process.get(name + "_base64")
    need(type(value) is str, "missing actual runner " + name)
    try:
        result = base64.b64decode(value, validate=True)
    except (TypeError, ValueError) as error:
        raise GraphError("invalid actual runner " + name) from error
    need(
        len(result) == process.get(name + "_bytes")
        and digest(result) == process.get(name + "_sha256"),
        "truncated or substituted actual runner " + name,
    )
    return result


def private_owner(claim: dict, filename: str) -> tuple[bytes, dict]:
    need(type(claim) is dict, "missing authenticated private " + filename)
    name = claim.get("path")
    need(type(name) is str and len(name) <= 512, "invalid private owner path")
    parts = PurePosixPath(name).parts
    need(
        len(parts) == 4
        and parts[0] == "/"
        and parts[1] == "tmp"
        and parts[2].startswith("rebar-phase2-native-activation-v5-c-")
        and parts[3] == filename,
        "reject an unrelated private recovery owner",
    )
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    parent = os.open("/tmp", flags | os.O_DIRECTORY)
    root = None
    fd = None
    try:
        root = os.open(parts[2], flags | os.O_DIRECTORY, dir_fd=parent)
        directory = os.fstat(root)
        need(
            stat.S_ISDIR(directory.st_mode)
            and stat.S_IMODE(directory.st_mode) == 0o700
            and directory.st_uid == os.geteuid(),
            "require the owner-only genuine V5 recovery root",
        )
        fd = os.open(filename, flags, dir_fd=root)
        before = os.fstat(fd)
        need(
            stat.S_ISREG(before.st_mode)
            and stat.S_IMODE(before.st_mode) == 0o600
            and before.st_nlink == 1
            and before.st_uid == os.geteuid()
            and before.st_dev == claim.get("device")
            and before.st_ino == claim.get("inode")
            and before.st_size == claim.get("bytes")
            and 0 < before.st_size <= MAX_REPORT,
            "reject a swapped or unsafe genuine private recovery owner",
        )
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            piece = os.read(fd, min(remaining, 1024 * 1024))
            need(bool(piece), "incomplete genuine private recovery owner")
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(fd, 1) == b"", "private recovery owner has extra bytes")
        after = os.fstat(fd)
        need(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "private recovery owner changed while being read",
        )
        raw = b"".join(pieces)
        need(digest(raw) == claim.get("sha256"), "changed private recovery owner")
        return raw, {
            "path": name,
            "sha256": digest(raw),
            "bytes": len(raw),
            "device": before.st_dev,
            "inode": before.st_ino,
            "mode": stat.S_IMODE(before.st_mode),
            "nlink": before.st_nlink,
        }
    finally:
        if fd is not None:
            os.close(fd)
        if root is not None:
            os.close(root)
        os.close(parent)


def authenticate_previous() -> tuple[types.ModuleType, dict, dict, dict[str, str]]:
    runtime()
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    fd = os.open(str(ROOT / V21["source"][0]), flags)
    try:
        parts: list[bytes] = []
        while True:
            piece = os.read(fd, 1024 * 1024)
            if not piece:
                break
            parts.append(piece)
        raw = b"".join(parts)
    finally:
        os.close(fd)
    need(digest(raw) == V21["source"][1], "the frozen V21 renderer changed")
    previous = types.ModuleType("_rebar_exact_current_overview_v21_for_v22")
    previous.__file__ = str(ROOT / V21["source"][0])
    exec(compile(raw, previous.__file__, "exec"), previous.__dict__)
    need(
        previous.SCHEMA == "rebar-candidate-current-overview-v21"
        and previous.SELF == V21["source"][0]
        and tuple(previous.SUITES) == SUITES,
        "load only the exact original independently frozen V21 renderer",
    )
    manifest, snapshot, outputs = previous.build(
        V21["source"][1],
        previous.OUTER_ARCHIVE[1],
        previous.OUTER_RECEIPT[1],
    )
    observed = {path: value for path, value in outputs}
    for name in ("inputs", "summary", "svg"):
        path, sha = V21[name]
        actual, _ = previous.read_owner(path, sha)
        need(
            observed.get(path) == actual and digest(actual) == sha,
            "the published exact V21 " + name + " is not reproducible",
        )
    summary = previous.document(observed[V21["summary"][0]], "frozen V21")
    need(
        type(manifest) is dict
        and summary.get("snapshot") == snapshot
        and summary.get("repository_evidence_owner_count") == OLD_EVIDENCE_OWNERS
        and summary.get("authenticated_digest_addressed_history_paths")
        == OLD_REFERENCE_PATHS
        and summary.get("qualified_candidate_count") == 0,
        "never replace or silently recount the complete V21 result",
    )
    _, _, history = previous.authenticate_previous()
    old_failure, old_owners = previous.authenticate_campaign(
        previous.OUTER_ARCHIVE[1], previous.OUTER_RECEIPT[1]
    )
    references = dict(history)
    need(
        len(references) == 78
        and len(old_owners) == 30
        and not (set(references) & set(old_owners)),
        "preserve every previous history path and all 30 failed owners",
    )
    references.update(old_owners)
    need(
        len(references) == OLD_REFERENCE_PATHS
        and snapshot.get("c_v8_repaired_original_campaign") == old_failure
        and old_failure.get("infrastructure_failure_count") == 13,
        "preserve the independently authenticated old thirteen runner failures",
    )
    return previous, summary, snapshot, references


def missing_new_suite_evidence() -> int:
    evidence = "oracle/phase2/evidence/"
    base = evidence + "frozen-p0-candidate-v9-c-" + LABEL
    absent = [
        base + suffix
        for stem in ("", "-failures")
        for suffix in (stem + ".json.gz", stem + "-publication-receipt.json")
    ]
    for suite, _ in SUITES:
        stem = (
            evidence
            + "frozen-p0-candidate-worker-v7-c-"
            + LABEL
            + "-"
            + suite
        )
        absent.extend((stem + ".json.gz", stem + "-publication-receipt.json"))
    need(len(absent) == 30 and len(set(absent)) == 30, "bound V9 owner paths")
    for relative in absent:
        try:
            os.stat(str(ROOT / relative), follow_symlinks=False)
        except FileNotFoundError:
            continue
        raise GraphError("a supposedly unstarted V9 owner exists: " + relative)
    return len(absent)


def authenticate_current(
    previous: types.ModuleType,
    archive_sha: str,
    receipt_sha: str,
) -> tuple[dict, dict[str, str]]:
    need(
        archive_sha == CURRENT_ARCHIVE[1] and receipt_sha == CURRENT_RECEIPT[1],
        "independently pin the only two genuine new corrected-C owners",
    )
    compressed, archive_owner = previous.read_owner(
        CURRENT_ARCHIVE[0], archive_sha, size=CURRENT_ARCHIVE[2], private=True
    )
    receipt_raw, receipt_owner = previous.read_owner(
        CURRENT_RECEIPT[0], receipt_sha, size=CURRENT_RECEIPT[2], private=True
    )
    receipt = previous.document(receipt_raw, "actual corrected C publication")
    previous.require_published_archive(receipt, archive_owner, "corrected C")
    need(
        receipt.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v2-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("family") == "c"
        and receipt.get("label") == LABEL
        and receipt.get("suite_count") == 13
        and receipt.get("case_execution_denominator") == 31237
        and receipt.get("uncompressed_sha256") == CURRENT_UNCOMPRESSED_SHA256
        and receipt.get("uncompressed_bytes") == CURRENT_UNCOMPRESSED_BYTES
        and receipt.get("historical_evidence_owner_count") == OLD_EVIDENCE_OWNERS
        and receipt.get("historical_authenticated_reference_count")
        == OLD_REFERENCE_PATHS
        and receipt.get("original_native_restored") is True,
        "do not treat successful evidence publication as candidate success",
    )
    need(
        receipt.get("holdout") == "NOT OPENED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("winner_selected") is False,
        "the actual signed receipt crossed the sealed performance boundary",
    )
    full = previous.expand_archive(
        compressed,
        expected_sha=CURRENT_UNCOMPRESSED_SHA256,
        expected_bytes=CURRENT_UNCOMPRESSED_BYTES,
        label="genuine bounded corrected-C infrastructure result",
    )
    need(
        full.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v2-actual-recovered-campaign"
        and full.get("status") == "FAIL"
        and full.get("family") == "c"
        and full.get("label") == LABEL
        and full.get("suite_count") == 13
        and full.get("case_execution_denominator") == 31237
        and full.get("named_private_waiver_count") == 13
        and full.get("completed_suite_count") == "NOT MEASURED"
        and full.get("verified_passing_case_count") == "NOT MEASURED"
        and full.get("semantic_mismatch_count") == "NOT MEASURED"
        and full.get("infrastructure_failure_count") == 1
        and full.get("all_original_suite_evidence_preserved") is False
        and full.get("candidate_qualified") is False
        and full.get("original_native_restored") is True
        and full.get("historical_evidence_owner_count") == OLD_EVIDENCE_OWNERS
        and full.get("historical_authenticated_reference_count")
        == OLD_REFERENCE_PATHS
        and full.get("preserved_failed_campaign_evidence_owner_count") == 30,
        "never claim thirteen corrected C suite workers or invented matching",
    )
    previous.boundary(full, "new corrected C complete evidence")
    failure = full.get("failure")
    need(
        type(failure) is dict
        and failure.get("error_type") == "CampaignError"
        and failure.get("error_message")
        == "never turn a partial original campaign or failed recovery into a pass",
        "preserve the exact genuine outer infrastructure failure",
    )
    process = failure.get("actual_aggregate_process")
    need(
        type(process) is dict
        and process.get("actual_aggregate_processes") == 1
        and process.get("returncode") == 1
        and process.get("timed_out") is False,
        "preserve exactly one genuine failed V9 process",
    )
    stdout = decode_stream(process, "stdout")
    stderr = decode_stream(process, "stderr")
    need(
        len(stdout) == INNER_STDOUT_BYTES
        and digest(stdout) == INNER_STDOUT_SHA256
        and stderr == b"",
        "preserve complete original V9 process streams",
    )
    inner = previous.document(stdout, "real V9 process entry failure")
    need(
        inner.get("schema") == "rebar-frozen-python-re-p0-candidate-v9-entry-failure"
        and inner.get("status") == "FAIL"
        and inner.get("error_type") == "AttributeError"
        and inner.get("error_message") == INNER_FAILURE
        and inner.get("actual_candidate_workers") == 0
        and inner.get("actual_reference_workers") == 0
        and inner.get("actual_native_activations") == 0
        and inner.get("actual_source_builds") == 0
        and inner.get("candidate_qualified") is False,
        "identify the actual missing runner_source_sha256 before matching",
    )
    previous.boundary(inner, "genuine V9 zero-worker failure")
    raw_native, native = previous.read_owner(
        ORIGINAL_NATIVE[0], ORIGINAL_NATIVE[1], size=ORIGINAL_NATIVE[2]
    )
    need(
        digest(raw_native) == ORIGINAL_NATIVE[1]
        and native.get("device") == 2064
        and native.get("inode") == 430300
        and native.get("mode") == 0o755
        and native.get("nlink") == 1,
        "the exact original user C native inode was not restored",
    )
    claimed = full.get("original_native_owner")
    need(
        type(claimed) is dict
        and claimed.get("relative") == native.get("path")
        and all(
            claimed.get(key) == native.get(key)
            for key in ("sha256", "bytes", "device", "inode", "mode", "nlink")
        ),
        "the current original inode differs from the signed restoration",
    )
    recovery = full.get("recovery")
    need(
        type(recovery) is dict
        and recovery.get("route") == "existing-authenticated-restoration-receipt"
        and type(recovery.get("owner")) is dict
        and type(recovery.get("report")) is dict,
        "require one actual authenticated restoration receipt",
    )
    private_raw, _ = private_owner(recovery["owner"], "restoration-receipt.json")
    private_report = previous.document(private_raw, "real private restoration")
    need(
        private_report == recovery["report"]
        and private_report.get("schema")
        == "rebar-phase2-verified-native-activation-v5-actual-restoration"
        and private_report.get("status") == "PASS"
        and private_report.get("route") == "reportless-recovery"
        and private_report.get("original_inode_preserved") is True
        and private_report.get("original") == claimed,
        "require the real exact-once private original-inode restoration",
    )
    journal_claim = private_report.get("recovery_journal")
    private_journal, _ = private_owner(journal_claim, "recovery-journal.json")
    journal = previous.document(private_journal, "actual V5 recovery journal")
    need(
        journal.get("schema")
        == "rebar-phase2-verified-native-activation-v5-recovery-journal"
        and journal.get("status") == "PREPARED"
        and journal.get("family") == "c"
        and journal.get("original") == claimed,
        "never adopt an invented or unrelated restoration journal",
    )
    missing = missing_new_suite_evidence()
    proof = {
        "status": "FAIL",
        "failure_class": "RUNNER INFRASTRUCTURE FAILED BEFORE MATCHING",
        "family": "c",
        "label": LABEL,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "completed_suite_count": "NOT MEASURED",
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_aggregate_process_count": 1,
        "actual_aggregate_process_exit_status": 1,
        "infrastructure_failure_count": 1,
        "infrastructure_failure_type": "AttributeError",
        "infrastructure_failure_message": INNER_FAILURE,
        "observed_matching_case_count": 0,
        "verified_passing_case_count": "NOT MEASURED",
        "semantic_mismatch_count": "NOT MEASURED",
        "all_original_suite_evidence_preserved": False,
        "new_suite_and_aggregate_owners_absent": missing,
        "qualified": False,
        "archive": previous.pin(archive_owner["path"], archive_owner["sha256"], archive_owner["bytes"]),
        "receipt": previous.pin(receipt_owner["path"], receipt_owner["sha256"], receipt_owner["bytes"]),
        "uncompressed_sha256": CURRENT_UNCOMPRESSED_SHA256,
        "uncompressed_bytes": CURRENT_UNCOMPRESSED_BYTES,
        "actual_v9_stdout_sha256": INNER_STDOUT_SHA256,
        "actual_v9_stdout_bytes": INNER_STDOUT_BYTES,
        "new_repository_evidence_owner_count": NEW_EVIDENCE_OWNERS,
        "original_canonical_native_restored": True,
        "original_canonical_native": {
            key: native[key]
            for key in ("path", "sha256", "bytes", "device", "inode", "mode", "nlink")
        },
        "restoration_status": "PASS",
        "restoration_route": "reportless-recovery",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, {
        archive_owner["path"]: archive_owner["sha256"],
        receipt_owner["path"]: receipt_owner["sha256"],
    }


def validate_snapshot(snapshot: dict) -> None:
    need(
        type(snapshot) is dict
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and tuple(snapshot.get("suite_ids", ())) == tuple(name for name, _ in SUITES)
        and snapshot.get("baseline_passed") == 31237
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("current_source_owner_count") == 25
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("preserved_v21_repository_evidence_owner_count")
        == OLD_EVIDENCE_OWNERS
        and snapshot.get("preserved_v21_digest_addressed_history_path_count")
        == OLD_REFERENCE_PATHS
        and snapshot.get("new_corrected_c_campaign_repository_evidence_owner_count")
        == NEW_EVIDENCE_OWNERS
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count")
        == EVIDENCE_OWNERS
        and snapshot.get("all_digest_addressed_history_path_count") == REFERENCE_PATHS,
        "reject changed denominators or the true 103+2/108+2 accounting",
    )
    previous = snapshot.get("c_v8_repaired_original_campaign")
    need(
        type(previous) is dict
        and previous.get("status") == "FAIL"
        and previous.get("completed_suite_count") == 13
        and previous.get("infrastructure_failure_count") == 13
        and previous.get("observed_matching_case_count") == 0
        and previous.get("semantic_mismatch_count") == "NOT MEASURED"
        and previous.get("failure_causes")
        == {
            "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 12,
            "SAVED PYTHON REFERENCE DECODING": 1,
        }
        and type(previous.get("suite_results")) is list
        and len(previous["suite_results"]) == 13,
        "never erase or merge the thirteen previous infrastructure failures",
    )
    current = snapshot.get("c_v9_repaired_original_campaign")
    need(
        type(current) is dict
        and current.get("status") == "FAIL"
        and current.get("label") == LABEL
        and current.get("actual_candidate_workers") == 0
        and current.get("actual_aggregate_process_count") == 1
        and current.get("actual_aggregate_process_exit_status") == 1
        and current.get("infrastructure_failure_count") == 1
        and current.get("infrastructure_failure_type") == "AttributeError"
        and current.get("infrastructure_failure_message") == INNER_FAILURE
        and current.get("observed_matching_case_count") == 0
        and current.get("completed_suite_count") == "NOT MEASURED"
        and current.get("verified_passing_case_count") == "NOT MEASURED"
        and current.get("semantic_mismatch_count") == "NOT MEASURED"
        and current.get("all_original_suite_evidence_preserved") is False
        and current.get("new_suite_and_aggregate_owners_absent") == 30
        and current.get("new_repository_evidence_owner_count") == 2
        and current.get("qualified") is False,
        "never invent corrected-C suite results, matches or qualification",
    )
    native = current.get("original_canonical_native")
    need(
        type(native) is dict
        and native.get("path") == ORIGINAL_NATIVE[0]
        and native.get("sha256") == ORIGINAL_NATIVE[1]
        and native.get("bytes") == ORIGINAL_NATIVE[2]
        and native.get("device") == 2064
        and native.get("inode") == 430300
        and native.get("mode") == 0o755
        and native.get("nlink") == 1
        and current.get("original_canonical_native_restored") is True
        and current.get("restoration_status") == "PASS",
        "require exact original device, inode, bytes, permissions and recovery",
    )
    need(
        snapshot.get("c_actual_semantic_mismatch_count") == 2094
        and snapshot.get("c_verified_passing_case_executions") == 7197
        and snapshot.get("rust_actual_semantic_mismatch_count") == 2042
        and snapshot.get("rust_verified_passing_case_executions") == 7461
        and snapshot.get("zig_actual_semantic_mismatch_count") == 1764
        and snapshot.get("zig_verified_passing_case_executions") == 3583
        and snapshot.get("cpp_full_original_campaign", {}).get("semantic_mismatch_count") == 2308
        and snapshot.get("go_v2_full_original_campaign", {}).get("semantic_mismatch_count") == 4518,
        "preserve every genuine previous C, Rust, Zig, C++ and Go loss",
    )
    need(
        snapshot.get("repaired_c_full_matching_test_status")
        == "RUNNER FAILED BEFORE MATCHING; NOT MEASURED"
        and snapshot.get("repaired_c_actual_verified_matching_case_count") == 0
        and snapshot.get("repaired_c_semantic_mismatch_count") == "NOT MEASURED"
        and snapshot.get("repaired_c_infrastructure_failure_count") == 1
        and snapshot.get("repaired_c_completed_suite_count") == "NOT MEASURED"
        and snapshot.get("repaired_c_native_promoted") is False,
        "distinguish the single new runner failure from the earlier thirteen",
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
        "never claim speed, memory, undefined behavior, or an opened holdout",
    )


def xml(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def make_svg(snapshot: dict, source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(snapshot)
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1660" height="1700" viewBox="0 0 1660 1700" role="img" aria-labelledby="v22-title v22-description">',
        '<title id="v22-title">Building a faster Python re: the corrected C runner stopped before matching</title>',
        '<desc id="v22-description">Python passes all 31,237 original reference checks. None of six replacement families is fully compatible. The latest corrected C campaign started one real runner, but its runner raised an AttributeError before any candidate worker or matching case began. Its matching result is not measured. An earlier C campaign separately failed all 13 test groups before matching. All previous candidate failures remain visible. There are exactly 105 evidence files and 110 separately authenticated history paths. The exact original C binary was restored. Speed, memory and the 4,194,304-case final comparison remain not measured.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:33px;font-weight:760;fill:#16324f}.heading{font-size:24px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:18px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.pending{font-size:15px;font-weight:740;fill:#53667b}.big{font-size:25px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}</style>',
        '<rect width="1660" height="1700" rx="22" fill="#f4f7fb"/>',
        '<text x="54" y="68" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="56" y="98" class="body">The latest C runner stopped before testing a single match. Compatibility and speed remain unproven.</text>',
    ]
    cards = (
        ("31,237", "original Python reference checks"),
        ("0 of 6", "fully compatible replacements"),
        ("0", "latest C matching cases observed"),
        ("105", "independently verified evidence files"),
        ("NOT MEASURED", "speed and memory"),
    )
    for index, (number, label) in enumerate(cards):
        x = 54 + index * 320
        lines.extend((
            f'<rect x="{x}" y="122" width="304" height="104" rx="13" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 14}" y="165" class="big">{xml(number)}</text>',
            f'<text x="{x + 14}" y="201" class="body">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="54" y="244" width="1552" height="1040" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="76" y="285" class="heading">1. Does it behave like Python?</text>',
        '<text x="77" y="312" class="body">The original reference has 13 groups and 31,237 cases. A runner error is not a matching result.</text>',
    ))
    rows = (
        ("Python re", "PASSED", "31,237 of 31,237 original Python reference checks passed.", "pass"),
        ("C — latest corrected runner", "RUNNER FAILED", "One runner failed before starting any test worker. Matching: NOT MEASURED.", "fail"),
        ("C — earlier runner attempt", "RUNNER FAILED", "All 13 earlier test groups failed before matching; these failures are preserved.", "fail"),
        ("C — earlier matching build", "FAILED", "7,197 verified passes and 2,094 genuine matching differences.", "fail"),
        ("Rust", "FAILED", "7,461 verified passes and 2,042 genuine matching differences.", "fail"),
        ("Zig", "FAILED", "3,583 verified passes and 1,764 genuine matching differences.", "fail"),
        ("C++", "FAILED", "128 verified passes, 2,308 matching differences and five runner failures.", "fail"),
        ("Go", "FAILED", "128 verified passes, 4,518 matching differences and four runner failures.", "fail"),
        ("Fortran", "NOT READY", "Independently built engine outputs differ. Matching: NOT MEASURED.", "pending"),
    )
    for index, (name, result, detail, category) in enumerate(rows):
        y = 335 + 82 * index
        lines.extend((
            f'<rect x="75" y="{y}" width="1510" height="71" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="94" y="{y + 26}" class="name">{xml(name)}</text>',
            f'<text x="1564" y="{y + 26}" class="{category}" text-anchor="end">{xml(result)}</text>',
            f'<text x="96" y="{y + 52}" class="body">{xml(detail)}</text>',
        ))
    details = (
        "Latest cause: the runner expected a missing runner_source_sha256 field and exited before matching.",
        "Latest evidence: one failed runner; zero candidate workers; passing and mismatch counts NOT MEASURED.",
        "Previous evidence: 13 separate old runner failures; 12 ownership errors and one reference-decoding error.",
        "The exact original C binary, permissions and inode were restored; the repaired binary is not active.",
        "105 actual evidence files = 103 preserved files + the latest genuine report and its receipt.",
        "All 110 distinct signed historical evidence references are authenticated; none are silently recounted.",
    )
    for index, message in enumerate(details):
        lines.append(
            f'<text x="77" y="{1094 + index * 28}" class="body">{xml(message)}</text>'
        )
    lines.extend((
        '<rect x="54" y="1300" width="1552" height="220" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="76" y="1342" class="heading">2. Is it faster than Python?</text>',
        '<text x="78" y="1376" class="body">NOT MEASURED. There is no tested speed, memory, confidence interval, ranking or winner.</text>',
        '<text x="78" y="1410" class="body">The planned 4,194,304-case final comparison has not been generated, opened or timed.</text>',
        '<text x="78" y="1444" class="body">Next: repair the independently proven missing runner field; then rerun all original correctness cases.</text>',
        f'<text x="58" y="1564" class="foot">Inputs SHA-256: {xml(inputs_sha)}</text>',
        f'<text x="58" y="1590" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="58" y="1616" class="foot">Actual corrected C report SHA-256: {CURRENT_ARCHIVE[1]}</text>',
        f'<text x="58" y="1642" class="foot">Actual corrected C receipt SHA-256: {CURRENT_RECEIPT[1]}</text>',
        '</svg>',
        '',
    ))
    return "\n".join(lines).encode("utf-8")


def build(
    source_sha: str,
    archive_sha: str,
    receipt_sha: str,
) -> tuple[dict, dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    source_sha = checked_digest(source_sha, "V22 source")
    previous, old_summary, old_snapshot, references = authenticate_previous()
    previous.read_owner(SELF, source_sha)
    proof, current_owners = authenticate_current(previous, archive_sha, receipt_sha)
    need(
        len(references) == OLD_REFERENCE_PATHS
        and len(current_owners) == NEW_EVIDENCE_OWNERS
        and not (set(references) & set(current_owners)),
        "the only two genuinely new files overlap preserved evidence",
    )
    references.update(current_owners)
    need(len(references) == REFERENCE_PATHS, "silently changed signed reference count")
    for path, sha in sorted(references.items()):
        previous.read_owner(path, sha)
    snapshot = copy.deepcopy(old_snapshot)
    snapshot.update({
        "preserved_v21_repository_evidence_owner_count": OLD_EVIDENCE_OWNERS,
        "preserved_v21_digest_addressed_history_path_count": OLD_REFERENCE_PATHS,
        "new_corrected_c_campaign_repository_evidence_owner_count": NEW_EVIDENCE_OWNERS,
        "all_actual_candidate_and_native_evidence_owner_count": EVIDENCE_OWNERS,
        "all_digest_addressed_history_path_count": REFERENCE_PATHS,
        "c_v9_repaired_original_campaign": copy.deepcopy(proof),
        "repaired_c_full_matching_test_status": "RUNNER FAILED BEFORE MATCHING; NOT MEASURED",
        "repaired_c_actual_verified_matching_case_count": 0,
        "repaired_c_semantic_mismatch_count": "NOT MEASURED",
        "repaired_c_infrastructure_failure_count": 1,
        "repaired_c_completed_suite_count": "NOT MEASURED",
        "repaired_c_native_promoted": False,
        "existing_canonical_c_native_target": copy.deepcopy(proof["original_canonical_native"]),
    })
    validate_snapshot(snapshot)
    old_inputs_raw, _ = previous.read_owner(V21["inputs"][0], V21["inputs"][1])
    old_inputs = previous.document(old_inputs_raw, "exact V21 signed manifest")
    manifest = {
        "schema": SCHEMA + "-inputs",
        "version": 22,
        "python": "3.14.6",
        "renderer": previous.pin(SELF, source_sha),
        "previous_overview": {
            name: previous.pin(path, sha)
            for name, (path, sha) in sorted(V21.items())
        },
        "original_correctness_manifest": copy.deepcopy(old_inputs["original_correctness_manifest"]),
        "original_source_freeze": copy.deepcopy(old_inputs["original_source_freeze"]),
        "previous_failed_c_campaign": copy.deepcopy(snapshot["c_v8_repaired_original_campaign"]),
        "corrected_c_original_campaign": copy.deepcopy(proof),
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "candidate_families": ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "candidate_qualified_count": 0,
        "preserved_v21_repository_evidence_owner_count": OLD_EVIDENCE_OWNERS,
        "new_corrected_c_campaign_repository_evidence_owner_count": NEW_EVIDENCE_OWNERS,
        "repository_evidence_owner_count": EVIDENCE_OWNERS,
        "preserved_v21_digest_addressed_history_path_count": OLD_REFERENCE_PATHS,
        "all_digest_addressed_history_path_count": REFERENCE_PATHS,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    manifest_raw = canonical(manifest)
    manifest_sha = digest(manifest_raw)
    svg = make_svg(snapshot, source_sha, manifest_sha)
    families = copy.deepcopy(old_summary["families"])
    for family in families:
        if family.get("family") == "c":
            family["historical_v8_repaired_original_campaign"] = copy.deepcopy(
                snapshot["c_v8_repaired_original_campaign"]
            )
            family["current_repaired_original_campaign"] = copy.deepcopy(proof)
            family["current_repaired_matching_test_status"] = (
                "RUNNER FAILED BEFORE MATCHING; NOT MEASURED"
            )
            family["current_repaired_observed_matching_case_count"] = 0
            family["current_repaired_verified_passing_case_count"] = "NOT MEASURED"
            family["current_repaired_semantic_mismatch_count"] = "NOT MEASURED"
            family["current_repaired_infrastructure_failure_count"] = 1
            family["current_repaired_completed_suite_count"] = "NOT MEASURED"
            family["current_repaired_candidate_worker_count"] = 0
            family["current_repaired_canonical_native_promoted"] = False
            family["current_repaired_canonical_native_restored"] = True
    summary = {
        "schema": SCHEMA + "-summary",
        "status": "PASS",
        "python": "3.14.6",
        "source": previous.pin(SELF, source_sha),
        "inputs": previous.pin(OUTPUT + ".inputs.json", manifest_sha),
        "svg": previous.pin(OUTPUT + ".svg", digest(svg)),
        "previous_overview": {
            name: previous.pin(path, sha)
            for name, (path, sha) in sorted(V21.items())
        },
        "snapshot": snapshot,
        "families": families,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "repository_evidence_owner_count": EVIDENCE_OWNERS,
        "authenticated_digest_addressed_history_paths": REFERENCE_PATHS,
        "preserved_v21_repository_evidence_owner_count": OLD_EVIDENCE_OWNERS,
        "preserved_v21_authenticated_reference_path_count": OLD_REFERENCE_PATHS,
        "new_corrected_c_campaign_repository_evidence_owner_count": NEW_EVIDENCE_OWNERS,
        "qualified_candidate_count": 0,
        "c_repaired_build_status": "PASS",
        "c_repaired_matching_test_status": "RUNNER FAILED BEFORE MATCHING; NOT MEASURED",
        "c_repaired_observed_matching_case_count": 0,
        "c_repaired_verified_passing_case_count": "NOT MEASURED",
        "c_repaired_semantic_mismatch_count": "NOT MEASURED",
        "c_repaired_infrastructure_failure_count": 1,
        "c_repaired_completed_suite_count": "NOT MEASURED",
        "c_repaired_candidate_worker_count": 0,
        "c_repaired_original_campaign_status": "FAIL",
        "c_repaired_native_promoted": False,
        "existing_canonical_native_present": True,
        "original_canonical_native_restored": True,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    return manifest, snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".svg", svg),
        (OUTPUT + ".json", canonical(summary)),
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
            raise GraphError("V22 source-only operation blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir", "makedirs", "unlink", "remove", "replace", "rename", "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text", "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object, _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_snapshot() -> dict:
    old = {
        "status": "FAIL",
        "completed_suite_count": 13,
        "infrastructure_failure_count": 13,
        "observed_matching_case_count": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "failure_causes": {
            "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 12,
            "SAVED PYTHON REFERENCE DECODING": 1,
        },
        "suite_results": [
            {"suite": name, "case_execution_denominator": count}
            for name, count in SUITES
        ],
    }
    current = {
        "status": "FAIL",
        "label": LABEL,
        "actual_candidate_workers": 0,
        "actual_aggregate_process_count": 1,
        "actual_aggregate_process_exit_status": 1,
        "infrastructure_failure_count": 1,
        "infrastructure_failure_type": "AttributeError",
        "infrastructure_failure_message": INNER_FAILURE,
        "observed_matching_case_count": 0,
        "completed_suite_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "semantic_mismatch_count": "NOT MEASURED",
        "all_original_suite_evidence_preserved": False,
        "new_suite_and_aggregate_owners_absent": 30,
        "new_repository_evidence_owner_count": 2,
        "qualified": False,
        "original_canonical_native": {
            "path": ORIGINAL_NATIVE[0],
            "sha256": ORIGINAL_NATIVE[1],
            "bytes": ORIGINAL_NATIVE[2],
            "device": 2064,
            "inode": 430300,
            "mode": 0o755,
            "nlink": 1,
        },
        "original_canonical_native_restored": True,
        "restoration_status": "PASS",
    }
    return {
        "full_case_denominator": 31237,
        "suite_count": 13,
        "suite_ids": [name for name, _ in SUITES],
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "current_source_owner_count": 25,
        "qualified_candidate_count": 0,
        "preserved_v21_repository_evidence_owner_count": OLD_EVIDENCE_OWNERS,
        "preserved_v21_digest_addressed_history_path_count": OLD_REFERENCE_PATHS,
        "new_corrected_c_campaign_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": EVIDENCE_OWNERS,
        "all_digest_addressed_history_path_count": REFERENCE_PATHS,
        "c_v8_repaired_original_campaign": old,
        "c_v9_repaired_original_campaign": current,
        "c_actual_semantic_mismatch_count": 2094,
        "c_verified_passing_case_executions": 7197,
        "rust_actual_semantic_mismatch_count": 2042,
        "rust_verified_passing_case_executions": 7461,
        "zig_actual_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_executions": 3583,
        "cpp_full_original_campaign": {"semantic_mismatch_count": 2308},
        "go_v2_full_original_campaign": {"semantic_mismatch_count": 4518},
        "repaired_c_full_matching_test_status": "RUNNER FAILED BEFORE MATCHING; NOT MEASURED",
        "repaired_c_actual_verified_matching_case_count": 0,
        "repaired_c_semantic_mismatch_count": "NOT MEASURED",
        "repaired_c_infrastructure_failure_count": 1,
        "repaired_c_completed_suite_count": "NOT MEASURED",
        "repaired_c_native_promoted": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0,
        "performance_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def self_test() -> dict:
    with SourceOnlyWall() as wall:
        base = synthetic_snapshot()
        validate_snapshot(base)
        accepted = 1
        rejected = 0

        def reject(snapshot: object) -> None:
            nonlocal rejected
            try:
                validate_snapshot(snapshot)  # type: ignore[arg-type]
            except (GraphError, KeyError, TypeError, ValueError, AttributeError):
                rejected += 1
                return
            raise GraphError("accepted a forged source-only current overview")

        changed = {
            "full_case_denominator": 31236,
            "suite_count": 12,
            "baseline_passed": 31236,
            "frozen_independent_engine_family_count": 7,
            "current_source_owner_count": 24,
            "qualified_candidate_count": 1,
            "preserved_v21_repository_evidence_owner_count": 104,
            "preserved_v21_digest_addressed_history_path_count": 109,
            "new_corrected_c_campaign_repository_evidence_owner_count": 30,
            "all_actual_candidate_and_native_evidence_owner_count": 133,
            "all_digest_addressed_history_path_count": 138,
            "c_actual_semantic_mismatch_count": 0,
            "c_verified_passing_case_executions": 0,
            "rust_actual_semantic_mismatch_count": 0,
            "rust_verified_passing_case_executions": 0,
            "zig_actual_semantic_mismatch_count": 0,
            "zig_verified_passing_case_executions": 0,
            "repaired_c_full_matching_test_status": "PASS",
            "repaired_c_actual_verified_matching_case_count": 31237,
            "repaired_c_semantic_mismatch_count": 0,
            "repaired_c_infrastructure_failure_count": 13,
            "repaired_c_completed_suite_count": 13,
            "repaired_c_native_promoted": True,
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
        for key, value in changed.items():
            altered = copy.deepcopy(base)
            altered[key] = value
            reject(altered)
        current_changes = {
            "status": "PASS",
            "label": "phase2-v8-original-p0",
            "actual_candidate_workers": 1,
            "actual_aggregate_process_count": 0,
            "actual_aggregate_process_exit_status": 0,
            "infrastructure_failure_count": 13,
            "infrastructure_failure_type": "RuntimeError",
            "infrastructure_failure_message": "guessed",
            "observed_matching_case_count": 31237,
            "completed_suite_count": 13,
            "verified_passing_case_count": 0,
            "semantic_mismatch_count": 0,
            "all_original_suite_evidence_preserved": True,
            "new_suite_and_aggregate_owners_absent": 0,
            "new_repository_evidence_owner_count": 30,
            "qualified": True,
            "original_canonical_native_restored": False,
            "restoration_status": "FAIL",
        }
        for key, value in current_changes.items():
            altered = copy.deepcopy(base)
            altered["c_v9_repaired_original_campaign"][key] = value
            reject(altered)
        previous_changes = {
            "status": "PASS",
            "completed_suite_count": 1,
            "infrastructure_failure_count": 1,
            "observed_matching_case_count": 1,
            "semantic_mismatch_count": 0,
            "failure_causes": {"SAVED PYTHON REFERENCE DECODING": 1},
            "suite_results": [],
        }
        for key, value in previous_changes.items():
            altered = copy.deepcopy(base)
            altered["c_v8_repaired_original_campaign"][key] = value
            reject(altered)
        native_changes = {
            "path": "candidates/not-the-original.so",
            "sha256": "0" * 64,
            "bytes": 1,
            "device": 2049,
            "inode": 430301,
            "mode": 0o600,
            "nlink": 2,
        }
        for key, value in native_changes.items():
            altered = copy.deepcopy(base)
            altered["c_v9_repaired_original_campaign"]["original_canonical_native"][key] = value
            reject(altered)
        for name in ("cpp_full_original_campaign", "go_v2_full_original_campaign"):
            altered = copy.deepcopy(base)
            altered[name]["semantic_mismatch_count"] = 0
            reject(altered)
        reject({})
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"runner_source_sha256",
            b"NOT MEASURED",
            b"105",
            b"110",
            b"13 earlier",
            b"4,194,304",
            b"zero candidate workers",
        ):
            need(phrase in picture, "the graph omits essential honest evidence")
        probes = (
            lambda: builtins.open("/tmp/rebar-v22-forbidden", "rb"),
            lambda: os.open("/tmp/rebar-v22-forbidden", os.O_RDONLY),
            lambda: os.write(-1, b"forbidden"),
            lambda: subprocess.run(("forbidden-v22-candidate",)),
            lambda: importlib.import_module("candidates.vm_candidate"),
            lambda: threading.Thread(target=lambda: None).start(),
            lambda: socket.create_connection(("127.0.0.1", 1)),
            lambda: time.perf_counter(),
            lambda: tempfile.mkdtemp(),
        )
        for probe in probes:
            before = wall.blocked
            try:
                probe()
            except GraphError:
                need(wall.blocked == before + 1, "source-only probe was not blocked")
                rejected += 1
            else:
                raise GraphError("a source-only gate caused a real effect")
        need(rejected >= 70, "incomplete independent hostile source controls")
        return {
            "schema": SCHEMA + "-self-test",
            "status": "PASS",
            "version": 22,
            "accepted_synthetic_controls": accepted,
            "rejected_hostile_controls": rejected,
            "blocked_effect_count": wall.blocked,
            "repository_evidence_owner_count": EVIDENCE_OWNERS,
            "authenticated_digest_addressed_history_paths": REFERENCE_PATHS,
            "preserved_v21_evidence_owner_count": OLD_EVIDENCE_OWNERS,
            "preserved_v21_history_path_count": OLD_REFERENCE_PATHS,
            "new_actual_evidence_owner_count": NEW_EVIDENCE_OWNERS,
            "previous_repaired_c_infrastructure_failure_count": 13,
            "current_repaired_c_infrastructure_failure_count": 1,
            "current_repaired_c_candidate_worker_count": 0,
            "current_repaired_c_matching": "NOT MEASURED",
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "winner_selected": False,
            "synthetic_svg_sha256": digest(picture),
        }


def verify_output(previous: types.ModuleType, path: str, expected: bytes) -> None:
    actual, _ = previous.read_owner(path, digest(expected), size=len(expected))
    need(actual == expected, "the committed V22 graph output is not reproducible")


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-inputs", action="store_true")
    modes.add_argument("--emit-svg", action="store_true")
    modes.add_argument("--emit-summary", action="store_true")
    modes.add_argument("--verify", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--campaign-archive-sha256")
    parser.add_argument("--campaign-receipt-sha256")
    parser.add_argument("--manifest-sha256")
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(
                all(
                    getattr(args, name) is None
                    for name in (
                        "source_sha256",
                        "campaign_archive_sha256",
                        "campaign_receipt_sha256",
                        "manifest_sha256",
                    )
                ),
                "synthetic verification cannot authorize any genuine evidence",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked_digest(args.source_sha256, "V22 source")
        archive = checked_digest(args.campaign_archive_sha256, "actual V2 report")
        receipt = checked_digest(args.campaign_receipt_sha256, "actual V2 receipt")
        manifest, snapshot, outputs = build(source, archive, receipt)
        manifest_raw = outputs[0][1]
        manifest_sha = digest(manifest_raw)
        if args.emit_inputs:
            need(args.manifest_sha256 is None, "input emission cannot assume a manifest")
            sys.stdout.buffer.write(manifest_raw)
            return 0
        need(
            checked_digest(args.manifest_sha256, "caller-pinned V22 inputs")
            == manifest_sha,
            "independently pin the exact V22 graph inputs",
        )
        if args.emit_svg:
            sys.stdout.buffer.write(outputs[1][1])
            return 0
        if args.emit_summary:
            sys.stdout.buffer.write(outputs[2][1])
            return 0
        previous, _, _, _ = authenticate_previous()
        for path, raw in outputs:
            verify_output(previous, path, raw)
        validate_snapshot(snapshot)
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-verified",
            "status": "PASS",
            "version": 22,
            "source_sha256": source,
            "inputs_sha256": manifest_sha,
            "svg_sha256": digest(outputs[1][1]),
            "summary_sha256": digest(outputs[2][1]),
            "actual_campaign_archive_sha256": archive,
            "actual_campaign_receipt_sha256": receipt,
            "suite_count": 13,
            "full_case_denominator": 31237,
            "candidate_family_count": 6,
            "repository_evidence_owner_count": EVIDENCE_OWNERS,
            "authenticated_digest_addressed_history_paths": REFERENCE_PATHS,
            "preserved_v21_evidence_owner_count": OLD_EVIDENCE_OWNERS,
            "preserved_v21_history_path_count": OLD_REFERENCE_PATHS,
            "new_corrected_c_evidence_owner_count": NEW_EVIDENCE_OWNERS,
            "previous_repaired_c_infrastructure_failure_count": 13,
            "current_repaired_c_infrastructure_failure_count": 1,
            "current_repaired_c_actual_aggregate_process_count": 1,
            "current_repaired_c_candidate_worker_count": 0,
            "current_repaired_c_matching": "NOT MEASURED",
            "current_repaired_c_passing_cases": "NOT MEASURED",
            "current_repaired_c_semantic_mismatches": "NOT MEASURED",
            "original_canonical_native_restored": True,
            "original_canonical_native_inode": 430300,
            "original_canonical_native_mode": "0755",
            "qualified_candidate_count": 0,
            "outputs_written": False,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "hidden_cases_read": 0,
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
        }))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError, gzip.BadGzipFile) as error:
        sys.stderr.write("current V22 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
