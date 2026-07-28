#!/usr/bin/env python3
"""Render the real, complete repaired-C correctness result without timing it."""

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
SCHEMA = "rebar-candidate-current-overview-v23"
SELF = "tools/render_candidate_current_overview_v23.py"
OUTPUT = "docs/evidence/candidate-current-overview-v23"
LABEL = "phase2-v10-live-original-p0"
V22 = {
    "source": (
        "tools/render_candidate_current_overview_v22.py",
        "a07bf3d6e6d8dc28c206218f14e2ed6f6089e31c66dbab2961979409b30fc955",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v22.inputs.json",
        "6843292a1f1d62d4635be4737a1565554cee8ec9f359506bc95a94cb80af7b58",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v22.json",
        "5dc6229696e5aba546c38e3d1d1bd4ce422a892a57ec562ccea8cb75cbbfb21f",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v22.svg",
        "7314d28286b90ee8161c02fee175904ba2ddd2c67dd78163f93b04fef2d0a26c",
    ),
}
OUTER_ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v3-c-phase2-v10-live-original-p0-failures.json.gz",
    "8dae792944509b4e8879d42b149a723d629c237b40c387a577fac5443bd2e4c7",
    12100,
)
OUTER_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v3-c-phase2-v10-live-original-p0-"
    "failures-publication-receipt.json",
    "f3383b6c00ab28d4466332b99c759e981b423a9f427757b0524f7a85f0cf253d",
    1039,
)
OUTER_EXPANDED = (
    "44caaaa21a4ba8ab9d4f94b7b9e9ef6577b1fdb072a180f54ff7443928b94d2f",
    49645,
)
INNER_ARCHIVE = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-v9-c-phase2-v10-live-original-p0-failures.json.gz",
    "b3ade63c2a5b1b8152af680c83fc19d5e89fd0fa955aa428737c97fffbfab173",
    10579,
)
INNER_RECEIPT = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-v9-c-phase2-v10-live-original-p0-"
    "failures-publication-receipt.json",
    "d9476eaee24864ae6b96efd3dfef30cf2355f32398d567d99244d47363de0b54",
    2959,
)
INNER_EXPANDED = (
    "03765db905e57636efde4c31f066b95e80891a3ec5817937a6f6b58bf2868d57",
    45835,
)
ORIGINAL_NATIVE = (
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd",
    149976,
)
ORIGINAL_PRODUCER = "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c"
BUILD_ARCHIVE_SHA = "69a795af6c407c0719b68dfa9fd4cb6dcfca2595271f72b83bc43678521f2598"
BUILD_RECEIPT_SHA = "3b0983af9729b3150ae239a83dd0fdb37c6e790b3c03ebea48c77215f51456b8"
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
PREVIOUS_OWNERS = 105
PREVIOUS_REFERENCES = 110
NEW_OWNERS = 30
TOTAL_OWNERS = 135
TOTAL_REFERENCES = 140
MAX_SOURCE = 8 * 1024 * 1024
MAX_SUITE_EXPANDED = 48 * 1024 * 1024


class GraphError(Exception):
    """The complete published C result or its visualization is not genuine."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(value: bytes) -> str:
    need(type(value) is bytes, "hash only exact authenticated evidence bytes")
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V23 graph evidence") from error


def checked_digest(value: object, name: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(part in "0123456789abcdef" for part in value),
         "require a separately pinned SHA-256: " + name)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON,
         "use only isolated, bytecode-free pinned CPython 3.14.6")


def load_v22() -> types.ModuleType:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / V22["source"][0]), flags)
    try:
        info = os.fstat(descriptor)
        need(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= MAX_SOURCE,
             "load only the bounded immutable V22 renderer")
        pieces: list[bytes] = []
        remaining = info.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            need(bool(piece), "reject truncated immutable V22 source")
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(descriptor, 1) == b"", "reject concealed V22 source bytes")
        raw = b"".join(pieces)
        need(digest(raw) == V22["source"][1], "reject substituted immutable V22 source")
    finally:
        os.close(descriptor)
    module = types.ModuleType("_rebar_exact_candidate_overview_v22_for_v23")
    module.__file__ = str(ROOT / V22["source"][0])
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    need(module.SCHEMA == "rebar-candidate-current-overview-v22"
         and module.SELF == V22["source"][0]
         and tuple(module.SUITES) == tuple((name, count) for name, count, _, _ in SUITES),
         "reject a changed original correctness denominator or previous renderer")
    return module


def authenticate_previous() -> tuple[types.ModuleType, types.ModuleType, dict, dict, dict[str, str]]:
    renderer = load_v22()
    previous, _v21_summary, _v21_snapshot, references = renderer.authenticate_previous()
    need(len(references) == 108, "preserve all 108 independently authenticated V21 references")
    previous_proof, additional = renderer.authenticate_current(
        previous, renderer.CURRENT_ARCHIVE[1], renderer.CURRENT_RECEIPT[1],
    )
    need(len(additional) == 2 and not (set(references) & set(additional)),
         "preserve the exact two real V22 runner-failure owners")
    references = dict(references)
    references.update(additional)
    need(len(references) == PREVIOUS_REFERENCES,
         "preserve all 110 distinct signed V22 history references")
    previous_outputs: dict[str, bytes] = {}
    for key, (path, sha) in V22.items():
        raw, _ = previous.read_owner(path, sha)
        previous_outputs[key] = raw
    summary = previous.document(previous_outputs["summary"], "exact published V22 summary")
    inputs = previous.document(previous_outputs["inputs"], "exact published V22 inputs")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "require the unchanged complete V22 snapshot")
    renderer.validate_snapshot(snapshot)
    need(summary.get("status") == "PASS"
         and summary.get("repository_evidence_owner_count") == PREVIOUS_OWNERS
         and summary.get("authenticated_digest_addressed_history_paths") == PREVIOUS_REFERENCES
         and summary.get("qualified_candidate_count") == 0
         and summary.get("families") is not None
         and summary.get("full_case_denominator") == 31237
         and summary.get("suite_count") == 13
         and inputs.get("repository_evidence_owner_count") == PREVIOUS_OWNERS
         and inputs.get("all_digest_addressed_history_path_count") == PREVIOUS_REFERENCES
         and snapshot.get("c_v9_repaired_original_campaign") == previous_proof
         and previous_outputs["svg"]
         == renderer.make_svg(snapshot, V22["source"][1], V22["inputs"][1]),
         "independently reproduce and preserve all four exact V22 overview owners")
    for path, sha in sorted(references.items()):
        previous.read_owner(path, sha)
    return renderer, previous, summary, inputs, references


def signed_owner(previous: types.ModuleType, claim: object, name: str,
                 exact: tuple[str, str, int] | None = None) -> tuple[bytes, dict]:
    raw, owner = previous.owner_from_signed(claim, name)
    if exact is not None:
        need(owner.get("path") == exact[0] and owner.get("sha256") == exact[1]
             and owner.get("bytes") == exact[2],
             "reject a changed independently frozen " + name)
    return raw, owner


def stream_suite(compressed: bytes, expected_sha: str, expected_bytes: int,
                 suite: str) -> None:
    checked_digest(expected_sha, suite + " complete case records")
    need(type(expected_bytes) is int and 0 < expected_bytes <= MAX_SUITE_EXPANDED,
         "reject an oversized original-suite record archive")
    result = hashlib.sha256()
    observed = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as archive:
            while True:
                block = archive.read(1024 * 1024)
                if not block:
                    break
                observed += len(block)
                need(observed <= expected_bytes,
                     "reject additional or unbounded real suite case records")
                result.update(block)
    except (EOFError, OSError, gzip.BadGzipFile) as error:
        raise GraphError("reject incomplete actual case records: " + suite) from error
    need(observed == expected_bytes and result.hexdigest() == expected_sha,
         "authenticate every byte of each complete original-suite case record")


def decode_stream(process: dict, prefix: str) -> bytes:
    try:
        raw = base64.b64decode(process.get(prefix + "_base64"), validate=True)
    except (TypeError, ValueError) as error:
        raise GraphError("reject the incomplete real " + prefix + " process stream") from error
    need(len(raw) == process.get(prefix + "_bytes")
         and digest(raw) == process.get(prefix + "_sha256"),
         "authenticate the complete actual aggregate " + prefix)
    return raw


def authenticate_campaign(previous: types.ModuleType, renderer: types.ModuleType,
                          archive_sha: str, receipt_sha: str) -> tuple[dict, dict[str, str]]:
    need(archive_sha == OUTER_ARCHIVE[1] and receipt_sha == OUTER_RECEIPT[1],
         "require independent caller pins for the actual final C campaign")
    archive_raw, archive_owner = previous.read_owner(
        OUTER_ARCHIVE[0], archive_sha, size=OUTER_ARCHIVE[2], private=True,
    )
    receipt_raw, receipt_owner = previous.read_owner(
        OUTER_RECEIPT[0], receipt_sha, size=OUTER_RECEIPT[2], private=True,
    )
    receipt = previous.document(receipt_raw, "actual recovered C V3 durable receipt")
    previous.require_published_archive(receipt, archive_owner, "actual C V3 campaign")
    need(receipt.get("schema") == "rebar-owned-repaired-c-original-campaign-v3-durable-publication-receipt"
         and receipt.get("status") == "PASS" and receipt.get("candidate_status") == "FAIL"
         and receipt.get("family") == "c" and receipt.get("label") == LABEL
         and receipt.get("suite_count") == 13 and receipt.get("case_execution_denominator") == 31237
         and receipt.get("uncompressed_sha256") == OUTER_EXPANDED[0]
         and receipt.get("uncompressed_bytes") == OUTER_EXPANDED[1]
         and receipt.get("historical_evidence_owner_count") == PREVIOUS_OWNERS
         and receipt.get("historical_authenticated_reference_count") == PREVIOUS_REFERENCES
         and receipt.get("preserved_v21_evidence_owner_count") == 103
         and receipt.get("preserved_v21_authenticated_reference_count") == 108
         and receipt.get("original_native_restored") is True
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("memory") == "NOT MEASURED"
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("winner_selected") is False,
         "a durable evidence receipt is not a passing compatible C candidate")
    outer = previous.expand_archive(archive_raw, expected_sha=OUTER_EXPANDED[0],
                                    expected_bytes=OUTER_EXPANDED[1],
                                    label="complete original corrected-C V3 result")
    previous.boundary(outer, "complete actual C V3 result")
    need(outer.get("schema") == "rebar-owned-repaired-c-original-campaign-v3-actual-recovered-campaign"
         and outer.get("status") == "FAIL" and outer.get("family") == "c"
         and outer.get("label") == LABEL and outer.get("suite_count") == 13
         and outer.get("case_execution_denominator") == 31237
         and outer.get("named_private_waiver_count") == 13
         and outer.get("completed_suite_count") == 13
         and outer.get("verified_passing_case_count") == 7325
         and outer.get("semantic_mismatch_count") == 1262
         and outer.get("infrastructure_failure_count") == 0
         and outer.get("candidate_qualified") is False
         and outer.get("all_original_suite_evidence_preserved") is True
         and outer.get("failure") is None
         and outer.get("original_native_restored") is True
         and outer.get("historical_evidence_owner_count") == PREVIOUS_OWNERS
         and outer.get("historical_authenticated_reference_count") == PREVIOUS_REFERENCES
         and outer.get("preserved_v21_evidence_owner_count") == 103
         and outer.get("preserved_v21_authenticated_reference_count") == 108
         and outer.get("preserved_failed_campaign_evidence_owner_count") == 30
         and outer.get("original_producer_sha256") == ORIGINAL_PRODUCER
         and outer.get("actual_build_archive_sha256") == BUILD_ARCHIVE_SHA
         and outer.get("actual_build_receipt_sha256") == BUILD_RECEIPT_SHA,
         "preserve the complete genuine C semantic failure without invented passes")

    aggregate_raw, aggregate_owner = signed_owner(
        previous, outer.get("original_aggregate_archive"), "original V9 aggregate", INNER_ARCHIVE,
    )
    aggregate_receipt_raw, aggregate_receipt_owner = signed_owner(
        previous, outer.get("original_aggregate_receipt"), "original V9 receipt", INNER_RECEIPT,
    )
    aggregate_receipt = previous.document(aggregate_receipt_raw, "actual V9 aggregate receipt")
    previous.require_published_archive(aggregate_receipt, aggregate_owner, "actual V9 aggregate")
    previous.boundary(aggregate_receipt, "actual V9 aggregate receipt")
    need(aggregate_receipt.get("schema") == "rebar-frozen-python-re-p0-candidate-v9-durable-publication-receipt"
         and aggregate_receipt.get("status") == "PASS"
         and aggregate_receipt.get("candidate_status") == "FAIL"
         and aggregate_receipt.get("candidate_family") == "c"
         and aggregate_receipt.get("label") == LABEL
         and aggregate_receipt.get("suite_count") == 13
         and aggregate_receipt.get("completed_suite_count") == 13
         and aggregate_receipt.get("case_execution_denominator") == 31237
         and aggregate_receipt.get("all_original_suite_evidence_preserved") is True
         and aggregate_receipt.get("uncompressed_sha256") == INNER_EXPANDED[0]
         and aggregate_receipt.get("uncompressed_bytes") == INNER_EXPANDED[1],
         "require the real independently preserved all-suite V9 aggregate")
    inner = previous.expand_archive(aggregate_raw, expected_sha=INNER_EXPANDED[0],
                                    expected_bytes=INNER_EXPANDED[1],
                                    label="complete actual thirteen-worker V9 report")
    previous.boundary(inner, "complete actual V9 matching report")
    need(inner.get("schema") == "rebar-frozen-python-re-p0-candidate-v9-complete-original-candidate-evaluation"
         and inner.get("status") == "FAIL" and inner.get("candidate_family") == "c"
         and inner.get("label") == LABEL and inner.get("suite_count") == 13
         and inner.get("case_execution_denominator") == 31237
         and inner.get("named_private_waiver_count") == 13
         and inner.get("completed_suite_count") == 13
         and inner.get("actual_candidate_workers") == 13
         and inner.get("verified_passing_case_count") == 7325
         and inner.get("semantic_mismatch_count") == 1262
         and inner.get("infrastructure_failure_count") == 0
         and inner.get("infrastructure_failure_suites") == []
         and inner.get("all_original_suite_evidence_preserved") is True
         and inner.get("candidate_qualified") is False
         and inner.get("outer_failure") is None
         and inner.get("original_producer_sha256") == ORIGINAL_PRODUCER
         and inner.get("actual_v8_build_archive_sha256") == BUILD_ARCHIVE_SHA
         and inner.get("actual_v8_build_receipt_sha256") == BUILD_RECEIPT_SHA,
         "never mistake a complete semantic mismatch for infrastructure or success")
    process = outer.get("original_aggregate_process")
    need(type(process) is dict and process.get("actual_aggregate_processes") == 1
         and process.get("returncode") == 1 and process.get("timed_out") is False,
         "require exactly one real failed-for-mismatches V9 aggregate process")
    stdout = decode_stream(process, "stdout")
    stderr = decode_stream(process, "stderr")
    publication = previous.document(stdout, "real complete live-adapter aggregate stdout")
    need(stderr == b"" and publication.get("schema")
         == "rebar-frozen-python-re-p0-candidate-v9-published-complete-candidate"
         and publication.get("status") == "FAIL"
         and publication.get("candidate_family") == "c"
         and publication.get("label") == LABEL
         and publication.get("actual_candidate_workers") in (None, 13)
         and publication.get("completed_suite_count") == 13
         and publication.get("verified_passing_case_count") == 7325
         and publication.get("semantic_mismatch_count") == 1262
         and publication.get("infrastructure_failure_count") == 0
         and publication.get("candidate_qualified") is False
         and publication.get("restoration_status") == "PASS"
         and type(publication.get("archive")) is dict
         and type(publication.get("receipt")) is dict
         and all(publication["archive"].get(key)
                 == outer["original_aggregate_archive"].get(key)
                 for key in ("relative", "sha256", "size_bytes", "device", "inode", "mode"))
         and all(publication["receipt"].get(key)
                 == outer["original_aggregate_receipt"].get(key)
                 for key in ("relative", "sha256", "size_bytes", "device", "inode", "mode"))
         and all(publication["archive"].get(key) is True
                 and publication["receipt"].get(key) is True
                 for key in ("exclusive_creation", "file_fsync_completed",
                             "directory_fsync_completed", "same_inode_readback_verified")),
         "authenticate the actual original V9 process output and semantic exit")

    outer_rows = outer.get("original_suite_results")
    inner_rows = inner.get("suite_results")
    need(type(outer_rows) is list and type(inner_rows) is list
         and len(outer_rows) == len(inner_rows) == len(SUITES),
         "require every original worker and complete suite evidence")
    paths: dict[str, str] = {
        OUTER_ARCHIVE[0]: OUTER_ARCHIVE[1],
        OUTER_RECEIPT[0]: OUTER_RECEIPT[1],
        INNER_ARCHIVE[0]: INNER_ARCHIVE[1],
        INNER_RECEIPT[0]: INNER_RECEIPT[1],
    }
    observed_rows: list[dict] = []
    for expected, outside, inside in zip(SUITES, outer_rows, inner_rows, strict=True):
        suite, count, mismatches, display = expected
        status = "PASS" if mismatches == 0 else "FAIL"
        failure_class = "PASS" if mismatches == 0 else "SEMANTIC MISMATCH"
        need(type(outside) is dict and type(inside) is dict
             and outside.get("suite") == inside.get("suite") == suite
             and outside.get("status") == inside.get("status") == status
             and outside.get("case_execution_denominator")
             == inside.get("case_execution_denominator") == count
             and outside.get("mismatch_count") == inside.get("mismatch_count") == mismatches
             and outside.get("failure_class") == inside.get("failure_class") == failure_class
             and outside.get("actual_worker_started") is True
             and inside.get("actual_worker_started") is True
             and inside.get("all_original_records_and_mismatches_preserved") is True,
             "preserve exact genuine worker and semantic results: " + suite)
        worker_process = outside.get("process")
        need(type(worker_process) is dict and worker_process == inside.get("process")
             and worker_process.get("returncode") == (0 if status == "PASS" else 1)
             and worker_process.get("timed_out") is False,
             "authenticate each actual independently started worker: " + suite)
        worker_archive_raw, worker_archive = signed_owner(
            previous, outside.get("archive"), suite + " actual worker archive",
        )
        worker_receipt_raw, worker_receipt_owner = signed_owner(
            previous, outside.get("receipt"), suite + " actual worker receipt",
        )
        need(outside.get("archive") == inside.get("suite_archive")
             and outside.get("receipt") == inside.get("suite_receipt")
             and (worker_archive["device"], worker_archive["inode"])
             != (worker_receipt_owner["device"], worker_receipt_owner["inode"]),
             "preserve distinct aggregate-bound suite archive and receipt owners")
        worker_receipt = previous.document(worker_receipt_raw, suite + " actual durable receipt")
        previous.require_published_archive(worker_receipt, worker_archive, suite)
        previous.boundary(worker_receipt, suite + " durable matching receipt")
        need(worker_receipt.get("schema")
             == "rebar-frozen-python-re-p0-candidate-worker-v7-durable-suite-publication-receipt"
             and worker_receipt.get("status") == "PASS"
             and worker_receipt.get("candidate_status") == status
             and worker_receipt.get("candidate_family") == "c"
             and worker_receipt.get("label") == LABEL
             and worker_receipt.get("suite") == suite
             and worker_receipt.get("case_execution_denominator") == count
             and worker_receipt.get("phase_one_case_execution_denominator") == 31237
             and worker_receipt.get("genuine_original_suite") is True
             and worker_receipt.get("mismatch_count") == mismatches
             and worker_receipt.get("all_original_records_and_mismatches_preserved") is True
             and worker_receipt.get("candidate_qualified") is False
             and worker_receipt.get("original_producer_sha256") == ORIGINAL_PRODUCER
             and worker_receipt.get("historical_evidence_owner_count") == 103
             and worker_receipt.get("historical_authenticated_reference_count") == 108
             and worker_receipt.get("uncompressed_sha256") == outside.get("uncompressed_sha256")
             and worker_receipt.get("uncompressed_bytes") == outside.get("uncompressed_bytes")
             and outside.get("uncompressed_sha256") == inside.get("uncompressed_sha256")
             and outside.get("uncompressed_bytes") == inside.get("uncompressed_bytes"),
             "preserve all original records, receipt status and actual mismatch count")
        stream_suite(worker_archive_raw, worker_receipt["uncompressed_sha256"],
                     worker_receipt["uncompressed_bytes"], suite)
        for owner in (worker_archive, worker_receipt_owner):
            path, fingerprint = owner["path"], owner["sha256"]
            need(path not in paths, "never recount or substitute a worker evidence owner")
            paths[path] = fingerprint
        observed_rows.append({
            "suite": suite, "display_name": display,
            "status": status, "failure_class": failure_class,
            "case_execution_denominator": count,
            "mismatch_count": mismatches,
            "actual_worker_started": True,
            "worker_returncode": worker_process["returncode"],
            "archive": previous.pin(worker_archive["path"], worker_archive["sha256"],
                                    worker_archive["bytes"]),
            "receipt": previous.pin(worker_receipt_owner["path"],
                                     worker_receipt_owner["sha256"],
                                     worker_receipt_owner["bytes"]),
            "uncompressed_sha256": worker_receipt["uncompressed_sha256"],
            "uncompressed_bytes": worker_receipt["uncompressed_bytes"],
            "all_original_records_and_mismatches_preserved": True,
        })
    need(len(paths) == NEW_OWNERS
         and sum(row["case_execution_denominator"] for row in observed_rows) == 31237
         and sum(row["mismatch_count"] for row in observed_rows) == 1262
         and sum(row["status"] == "PASS" for row in observed_rows) == 8
         and sum(row["case_execution_denominator"] for row in observed_rows
                 if row["status"] == "PASS") == 7325,
         "derive all thirty genuinely distinct owners and every genuine suite total")

    native_raw, native = previous.read_owner(
        ORIGINAL_NATIVE[0], ORIGINAL_NATIVE[1], size=ORIGINAL_NATIVE[2],
    )
    claimed = outer.get("original_native_owner")
    need(digest(native_raw) == ORIGINAL_NATIVE[1]
         and native.get("device") == 2064 and native.get("inode") == 430300
         and native.get("mode") == 0o755 and native.get("nlink") == 1
         and type(claimed) is dict and claimed.get("relative") == native.get("path")
         and all(claimed.get(key) == native.get(key)
                 for key in ("sha256", "bytes", "device", "inode", "mode", "nlink")),
         "verify the exact original C target inode and 0755 mode after recovery")
    recovery = outer.get("recovery")
    need(type(recovery) is dict
         and recovery.get("route") == "existing-authenticated-restoration-receipt"
         and type(recovery.get("owner")) is dict
         and type(recovery.get("report")) is dict,
         "preserve the genuine exactly-once V5 restoration receipt")
    recovery_raw, _ = renderer.private_owner(recovery["owner"], "restoration-receipt.json")
    recovery_report = previous.document(recovery_raw, "actual V5 private original restoration")
    inner_restoration = inner.get("restoration")
    need(recovery_report == recovery["report"]
         and recovery_report.get("schema")
         == "rebar-phase2-verified-native-activation-v5-actual-restoration"
         and recovery_report.get("status") == "PASS"
         and recovery_report.get("original_inode_preserved") is True
         and recovery_report.get("original") == claimed
         and type(inner_restoration) is dict
         and all(inner_restoration.get(key) == value
                 for key, value in recovery_report.items())
         and type(inner_restoration.get("restoration_receipt")) is dict
         and inner_restoration["restoration_receipt"].get("sha256")
         == recovery["owner"].get("sha256"),
         "require the real V9 restoration before both actual evidence publications")
    journal_raw, _ = renderer.private_owner(
        recovery_report.get("recovery_journal"), "recovery-journal.json",
    )
    journal = previous.document(journal_raw, "genuine complete V5 recovery journal")
    need(journal.get("schema") == "rebar-phase2-verified-native-activation-v5-recovery-journal"
         and journal.get("status") == "PREPARED" and journal.get("family") == "c"
         and journal.get("original") == claimed,
         "never fabricate an original-native recovery journal")
    proof = {
        "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
        "family": "c", "label": LABEL,
        "full_case_denominator": 31237, "suite_count": 13,
        "completed_suite_count": 13, "actual_candidate_workers": 13,
        "actual_aggregate_process_count": 1,
        "actual_aggregate_process_exit_status": 1,
        "fully_passing_suite_count": 8,
        "verified_passing_case_count": 7325,
        "observed_matching_case_count": 31237,
        "semantic_mismatch_count": 1262,
        "infrastructure_failure_count": 0,
        "all_original_suite_evidence_preserved": True,
        "suite_results": observed_rows,
        "new_repository_evidence_owner_count": NEW_OWNERS,
        "archive": previous.pin(archive_owner["path"], archive_owner["sha256"],
                                archive_owner["bytes"]),
        "receipt": previous.pin(receipt_owner["path"], receipt_owner["sha256"],
                                receipt_owner["bytes"]),
        "aggregate_archive": previous.pin(aggregate_owner["path"],
                                          aggregate_owner["sha256"], aggregate_owner["bytes"]),
        "aggregate_receipt": previous.pin(aggregate_receipt_owner["path"],
                                          aggregate_receipt_owner["sha256"],
                                          aggregate_receipt_owner["bytes"]),
        "uncompressed_sha256": OUTER_EXPANDED[0],
        "uncompressed_bytes": OUTER_EXPANDED[1],
        "aggregate_uncompressed_sha256": INNER_EXPANDED[0],
        "aggregate_uncompressed_bytes": INNER_EXPANDED[1],
        "original_canonical_native": {
            "path": native["path"], "sha256": native["sha256"],
            "bytes": native["bytes"], "device": native["device"],
            "inode": native["inode"], "mode": native["mode"],
            "nlink": native["nlink"],
        },
        "original_canonical_native_restored": True,
        "restoration_status": "PASS",
        "restoration_route": recovery_report["route"],
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "qualified": False, "winner_selected": False,
    }
    return proof, paths


def validate_snapshot(snapshot: dict) -> None:
    need(type(snapshot) is dict and snapshot.get("full_case_denominator") == 31237
         and snapshot.get("suite_count") == 13
         and tuple(snapshot.get("suite_ids", ()))
         == tuple(name for name, _, _, _ in SUITES)
         and snapshot.get("baseline_passed") == 31237
         and snapshot.get("frozen_independent_engine_family_count") == 6
         and snapshot.get("current_source_owner_count") == 25
         and snapshot.get("qualified_candidate_count") == 0
         and snapshot.get("preserved_v22_repository_evidence_owner_count") == PREVIOUS_OWNERS
         and snapshot.get("preserved_v22_digest_addressed_history_path_count") == PREVIOUS_REFERENCES
         and snapshot.get("new_v10_c_campaign_repository_evidence_owner_count") == NEW_OWNERS
         and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == TOTAL_OWNERS
         and snapshot.get("all_digest_addressed_history_path_count") == TOTAL_REFERENCES,
         "never silently recount the unchanged oracle or the exact 105+30/110+30 owners")
    first = snapshot.get("c_v8_repaired_original_campaign")
    second = snapshot.get("c_v9_repaired_original_campaign")
    current = snapshot.get("c_v10_repaired_original_campaign")
    need(type(first) is dict and first.get("status") == "FAIL"
         and first.get("completed_suite_count") == 13
         and first.get("infrastructure_failure_count") == 13
         and first.get("semantic_mismatch_count") == "NOT MEASURED"
         and type(first.get("suite_results")) is list
         and len(first["suite_results"]) == 13,
         "preserve all thirteen original earlier C runner failures")
    need(type(second) is dict and second.get("status") == "FAIL"
         and second.get("actual_candidate_workers") == 0
         and second.get("infrastructure_failure_count") == 1
         and second.get("semantic_mismatch_count") == "NOT MEASURED"
         and second.get("infrastructure_failure_type") == "AttributeError",
         "preserve the separate earlier one-runner failure without inventing matches")
    need(type(current) is dict and current.get("status") == "FAIL"
         and current.get("failure_class") == "SEMANTIC MISMATCH"
         and current.get("label") == LABEL
         and current.get("actual_candidate_workers") == 13
         and current.get("actual_aggregate_process_count") == 1
         and current.get("actual_aggregate_process_exit_status") == 1
         and current.get("full_case_denominator") == 31237
         and current.get("suite_count") == 13
         and current.get("completed_suite_count") == 13
         and current.get("fully_passing_suite_count") == 8
         and current.get("observed_matching_case_count") == 31237
         and current.get("verified_passing_case_count") == 7325
         and current.get("semantic_mismatch_count") == 1262
         and current.get("infrastructure_failure_count") == 0
         and current.get("all_original_suite_evidence_preserved") is True
         and current.get("new_repository_evidence_owner_count") == NEW_OWNERS
         and current.get("qualified") is False,
         "never relabel the thirteen real workers or the genuine 1,262 mismatches")
    rows = current.get("suite_results")
    need(type(rows) is list and len(rows) == 13,
         "never omit any complete original case group")
    for row, (suite, count, mismatches, display) in zip(rows, SUITES, strict=True):
        expected = "PASS" if mismatches == 0 else "FAIL"
        need(type(row) is dict and row.get("suite") == suite
             and row.get("display_name") == display
             and row.get("case_execution_denominator") == count
             and row.get("mismatch_count") == mismatches
             and row.get("status") == expected
             and row.get("failure_class")
             == ("PASS" if mismatches == 0 else "SEMANTIC MISMATCH")
             and row.get("actual_worker_started") is True
             and row.get("worker_returncode") == (0 if mismatches == 0 else 1)
             and row.get("all_original_records_and_mismatches_preserved") is True,
             "reject a changed real suite, worker or matching result: " + suite)
    native = current.get("original_canonical_native")
    need(type(native) is dict and native.get("path") == ORIGINAL_NATIVE[0]
         and native.get("sha256") == ORIGINAL_NATIVE[1]
         and native.get("bytes") == ORIGINAL_NATIVE[2]
         and native.get("device") == 2064 and native.get("inode") == 430300
         and native.get("mode") == 0o755 and native.get("nlink") == 1
         and current.get("original_canonical_native_restored") is True
         and current.get("restoration_status") == "PASS",
         "require restoration of the real original user-owned C binary")
    need(snapshot.get("c_actual_semantic_mismatch_count") == 2094
         and snapshot.get("c_verified_passing_case_executions") == 7197
         and snapshot.get("rust_actual_semantic_mismatch_count") == 2042
         and snapshot.get("rust_verified_passing_case_executions") == 7461
         and snapshot.get("zig_actual_semantic_mismatch_count") == 1764
         and snapshot.get("zig_verified_passing_case_executions") == 3583
         and snapshot.get("cpp_full_original_campaign", {}).get("semantic_mismatch_count") == 2308
         and snapshot.get("go_v2_full_original_campaign", {}).get("semantic_mismatch_count") == 4518,
         "preserve every historical independently implemented candidate result")
    need(snapshot.get("repaired_c_full_matching_test_status") == "FAIL: 1,262 SEMANTIC MISMATCHES"
         and snapshot.get("repaired_c_actual_verified_matching_case_count") == 31237
         and snapshot.get("repaired_c_verified_passing_case_count") == 7325
         and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
         and snapshot.get("repaired_c_infrastructure_failure_count") == 0
         and snapshot.get("repaired_c_completed_suite_count") == 13
         and snapshot.get("repaired_c_actual_candidate_worker_count") == 13
         and snapshot.get("repaired_c_native_promoted") is False,
         "show genuine matching and never conflate old infrastructure with current results")
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
         "never invent speed, memory, rankings, winner or holdout measurements")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))


def make_svg(snapshot: dict, source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(snapshot)
    current = snapshot["c_v10_repaired_original_campaign"]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1660" height="1990" viewBox="0 0 1660 1990" role="img" aria-labelledby="v23-title v23-description">',
        '<title id="v23-title">Building a faster Python re: the repaired C engine ran all tests but still differs from Python</title>',
        '<desc id="v23-description">The original Python reference passes 31,237 checks. The repaired first-party C engine genuinely ran all 13 test groups and all 31,237 checks. Eight complete groups containing 7,325 checks passed. Five groups contain 1,262 recorded differences. There were zero infrastructure failures. The C candidate is not fully compatible; none of the six replacement families qualifies. Both earlier C runner failures remain visible. All 135 distinct evidence files and 140 signed history references are independently authenticated. Speed, memory, ranking and the final holdout have not been measured.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:33px;font-weight:760;fill:#16324f}.heading{font-size:24px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:17px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.pending{font-size:15px;font-weight:740;fill:#53667b}.big{font-size:25px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}.small{font-size:13px;fill:#42556c}</style>',
        '<rect width="1660" height="1990" rx="22" fill="#f4f7fb"/>',
        '<text x="54" y="66" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="56" y="96" class="body">The repaired C engine now really runs all tests, but 1,262 results still differ from Python.</text>',
    ]
    cards = (
        ("31,237", "original Python checks run"),
        ("8 of 13", "C test groups fully passed"),
        ("1,262", "real C matching differences"),
        ("0", "current C runner failures"),
        ("NOT MEASURED", "speed and memory"),
    )
    for index, (value, label) in enumerate(cards):
        x = 54 + index * 320
        lines.extend((
            f'<rect x="{x}" y="120" width="304" height="104" rx="13" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 14}" y="163" class="big">{xml(value)}</text>',
            f'<text x="{x + 14}" y="198" class="body">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="54" y="241" width="1552" height="700" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="282" class="heading">1. Does each replacement behave exactly like Python?</text>',
        '<text x="78" y="309" class="body">A replacement qualifies only if every original check agrees. A published failure is not a passing candidate.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original reference checks pass.", "pass"),
        ("C — latest repaired engine", "NOT COMPATIBLE", "All 13 groups ran: 8 completely passed (7,325 checks); 1,262 differences; 0 runner failures.", "fail"),
        ("C — earlier matching engine", "NOT COMPATIBLE", "7,197 fully verified passing checks; 2,094 matching differences.", "fail"),
        ("Rust", "NOT COMPATIBLE", "7,461 fully verified passing checks; 2,042 matching differences.", "fail"),
        ("Zig", "NOT COMPATIBLE", "3,583 fully verified passing checks; 1,764 matching differences.", "fail"),
        ("C++", "NOT COMPATIBLE", "128 fully verified passing checks; 2,308 matching differences and 5 earlier runner failures.", "fail"),
        ("Go", "NOT COMPATIBLE", "128 fully verified passing checks; 4,518 matching differences and 4 runner failures.", "fail"),
        ("Fortran", "NOT READY", "Its independently built engine is not yet compatible. Matching: NOT MEASURED.", "pending"),
    )
    for index, (name, result, detail, category) in enumerate(rows):
        y = 326 + index * 69
        lines.extend((
            f'<rect x="75" y="{y}" width="1510" height="60" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="94" y="{y + 23}" class="name">{xml(name)}</text>',
            f'<text x="1564" y="{y + 23}" class="{category}" text-anchor="end">{xml(result)}</text>',
            f'<text x="96" y="{y + 46}" class="small">{xml(detail)}</text>',
        ))
    lines.extend((
        '<text x="78" y="903" class="body">The earlier C attempts remain recorded separately: 13 old runner failures, then one runner failure before matching.</text>',
        '<rect x="54" y="958" width="1552" height="648" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="999" class="heading">2. Which C test groups still differ?</text>',
        '<text x="78" y="1026" class="body">All 13 groups and all original case records were preserved; differences are actual observed results.</text>',
        '<text x="92" y="1053" class="small">TEST GROUP</text>',
        '<text x="1225" y="1053" class="small" text-anchor="end">ORIGINAL CHECKS</text>',
        '<text x="1562" y="1053" class="small" text-anchor="end">RESULT</text>',
    ))
    for index, row in enumerate(current["suite_results"]):
        y = 1066 + index * 35
        even = "#f8fafd" if index % 2 == 0 else "#ffffff"
        result = ("PASSED" if row["mismatch_count"] == 0
                  else f'{row["mismatch_count"]:,} DIFFERENCES')
        category = "pass" if row["mismatch_count"] == 0 else "fail"
        lines.extend((
            f'<rect x="77" y="{y}" width="1506" height="31" rx="5" fill="{even}"/>',
            f'<text x="95" y="{y + 21}" class="body">{xml(row["display_name"])}</text>',
            f'<text x="1225" y="{y + 21}" class="body" text-anchor="end">{row["case_execution_denominator"]:,}</text>',
            f'<text x="1562" y="{y + 21}" class="{category}" text-anchor="end">{xml(result)}</text>',
        ))
    lines.extend((
        '<text x="79" y="1550" class="body">Eight complete groups pass. The 7,325 passed checks count only those completely passing groups.</text>',
        '<text x="79" y="1576" class="body">The remaining five groups contain 1,262 exact differences; no differences or failures were hidden.</text>',
        '<rect x="54" y="1622" width="1552" height="193" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="1663" class="heading">3. Is any replacement faster?</text>',
        '<text x="79" y="1695" class="body">NOT MEASURED. No candidate has first passed every correctness test.</text>',
        '<text x="79" y="1725" class="body">There is no speed or memory comparison, confidence interval, ranking, winner, or opened final holdout.</text>',
        '<text x="79" y="1755" class="body">Evidence: 105 earlier files + 30 new real worker and campaign files = 135 verified files; 140 signed references.</text>',
        '<text x="79" y="1785" class="body">The original C binary, its exact inode, and its 0755 permissions were restored.</text>',
        f'<text x="58" y="1853" class="foot">Inputs SHA-256: {xml(inputs_sha)}</text>',
        f'<text x="58" y="1878" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="58" y="1903" class="foot">Actual C campaign archive SHA-256: {OUTER_ARCHIVE[1]}</text>',
        f'<text x="58" y="1928" class="foot">Actual C campaign receipt SHA-256: {OUTER_RECEIPT[1]}</text>',
        '</svg>',
        '',
    ))
    return "\n".join(lines).encode("utf-8")


def build(source_sha: str, archive_sha: str,
          receipt_sha: str) -> tuple[dict, dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked_digest(source_sha, "V23 renderer source")
    renderer, previous, old_summary, old_inputs, references = authenticate_previous()
    previous.read_owner(SELF, source_sha)
    current, additions = authenticate_campaign(previous, renderer, archive_sha, receipt_sha)
    need(len(references) == PREVIOUS_REFERENCES and len(additions) == NEW_OWNERS
         and not (set(references) & set(additions)),
         "authenticate exactly thirty genuinely new independent C evidence owners")
    references.update(additions)
    need(len(references) == TOTAL_REFERENCES,
         "never silently recount the complete 140 signed history references")
    for path, sha in sorted(references.items()):
        previous.read_owner(path, sha)
    snapshot = copy.deepcopy(old_summary["snapshot"])
    snapshot.update({
        "preserved_v22_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v22_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "new_v10_c_campaign_repository_evidence_owner_count": NEW_OWNERS,
        "all_actual_candidate_and_native_evidence_owner_count": TOTAL_OWNERS,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "c_v10_repaired_original_campaign": copy.deepcopy(current),
        "repaired_c_full_matching_test_status": "FAIL: 1,262 SEMANTIC MISMATCHES",
        "repaired_c_actual_verified_matching_case_count": 31237,
        "repaired_c_verified_passing_case_count": 7325,
        "repaired_c_semantic_mismatch_count": 1262,
        "repaired_c_infrastructure_failure_count": 0,
        "repaired_c_completed_suite_count": 13,
        "repaired_c_actual_candidate_worker_count": 13,
        "repaired_c_native_promoted": False,
        "existing_canonical_c_native_target": copy.deepcopy(current["original_canonical_native"]),
    })
    validate_snapshot(snapshot)
    manifest = {
        "schema": SCHEMA + "-inputs", "version": 23, "python": "3.14.6",
        "renderer": previous.pin(SELF, source_sha),
        "previous_overview": {
            key: previous.pin(path, sha) for key, (path, sha) in sorted(V22.items())
        },
        "original_correctness_manifest": copy.deepcopy(old_inputs["original_correctness_manifest"]),
        "original_source_freeze": copy.deepcopy(old_inputs["original_source_freeze"]),
        "first_failed_c_campaign": copy.deepcopy(snapshot["c_v8_repaired_original_campaign"]),
        "second_failed_c_campaign": copy.deepcopy(snapshot["c_v9_repaired_original_campaign"]),
        "current_complete_c_campaign": copy.deepcopy(current),
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "candidate_families": ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "candidate_qualified_count": 0,
        "preserved_v22_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "new_v10_c_campaign_repository_evidence_owner_count": NEW_OWNERS,
        "repository_evidence_owner_count": TOTAL_OWNERS,
        "preserved_v22_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }
    manifest_raw = canonical(manifest)
    manifest_sha = digest(manifest_raw)
    svg = make_svg(snapshot, source_sha, manifest_sha)
    families = copy.deepcopy(old_summary["families"])
    for family in families:
        if family.get("family") == "c":
            family["historical_v8_repaired_original_campaign"] = copy.deepcopy(
                snapshot["c_v8_repaired_original_campaign"])
            family["historical_v9_repaired_original_campaign"] = copy.deepcopy(
                snapshot["c_v9_repaired_original_campaign"])
            family["current_repaired_original_campaign"] = copy.deepcopy(current)
            family["current_repaired_matching_test_status"] = "FAIL: 1,262 SEMANTIC MISMATCHES"
            family["current_repaired_observed_matching_case_count"] = 31237
            family["current_repaired_verified_passing_case_count"] = 7325
            family["current_repaired_semantic_mismatch_count"] = 1262
            family["current_repaired_infrastructure_failure_count"] = 0
            family["current_repaired_completed_suite_count"] = 13
            family["current_repaired_candidate_worker_count"] = 13
            family["current_repaired_canonical_native_promoted"] = False
            family["current_repaired_canonical_native_restored"] = True
            family["qualified"] = False
    summary = {
        "schema": SCHEMA + "-summary", "status": "PASS", "python": "3.14.6",
        "source": previous.pin(SELF, source_sha),
        "inputs": previous.pin(OUTPUT + ".inputs.json", manifest_sha),
        "svg": previous.pin(OUTPUT + ".svg", digest(svg)),
        "previous_overview": {
            key: previous.pin(path, sha) for key, (path, sha) in sorted(V22.items())
        },
        "snapshot": snapshot, "families": families,
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "repository_evidence_owner_count": TOTAL_OWNERS,
        "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
        "preserved_v22_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v22_authenticated_reference_path_count": PREVIOUS_REFERENCES,
        "new_v10_c_campaign_repository_evidence_owner_count": NEW_OWNERS,
        "qualified_candidate_count": 0,
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
        "existing_canonical_native_present": True,
        "original_canonical_native_restored": True,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
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
            raise GraphError("V23 source-only operation blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)), (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir", "makedirs",
                  "unlink", "remove", "replace", "rename", "system", "fork", "posix_spawn")),
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

    def __exit__(self, _kind: object, _value: object, _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_snapshot() -> dict:
    old_first = {
        "status": "FAIL", "completed_suite_count": 13,
        "infrastructure_failure_count": 13,
        "semantic_mismatch_count": "NOT MEASURED",
        "suite_results": [{"suite": name, "case_execution_denominator": count}
                          for name, count, _, _ in SUITES],
    }
    old_second = {
        "status": "FAIL", "actual_candidate_workers": 0,
        "infrastructure_failure_count": 1,
        "semantic_mismatch_count": "NOT MEASURED",
        "infrastructure_failure_type": "AttributeError",
    }
    rows = [{
        "suite": name, "display_name": display,
        "status": "PASS" if mismatches == 0 else "FAIL",
        "failure_class": "PASS" if mismatches == 0 else "SEMANTIC MISMATCH",
        "case_execution_denominator": count,
        "mismatch_count": mismatches,
        "actual_worker_started": True,
        "worker_returncode": 0 if mismatches == 0 else 1,
        "all_original_records_and_mismatches_preserved": True,
    } for name, count, mismatches, display in SUITES]
    current = {
        "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
        "label": LABEL, "actual_candidate_workers": 13,
        "actual_aggregate_process_count": 1,
        "actual_aggregate_process_exit_status": 1,
        "full_case_denominator": 31237, "suite_count": 13,
        "completed_suite_count": 13, "fully_passing_suite_count": 8,
        "observed_matching_case_count": 31237,
        "verified_passing_case_count": 7325,
        "semantic_mismatch_count": 1262,
        "infrastructure_failure_count": 0,
        "all_original_suite_evidence_preserved": True,
        "new_repository_evidence_owner_count": NEW_OWNERS,
        "qualified": False, "suite_results": rows,
        "original_canonical_native": {
            "path": ORIGINAL_NATIVE[0], "sha256": ORIGINAL_NATIVE[1],
            "bytes": ORIGINAL_NATIVE[2], "device": 2064,
            "inode": 430300, "mode": 0o755, "nlink": 1,
        },
        "original_canonical_native_restored": True,
        "restoration_status": "PASS",
    }
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "suite_ids": [name for name, _, _, _ in SUITES],
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "current_source_owner_count": 25,
        "qualified_candidate_count": 0,
        "preserved_v22_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v22_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "new_v10_c_campaign_repository_evidence_owner_count": NEW_OWNERS,
        "all_actual_candidate_and_native_evidence_owner_count": TOTAL_OWNERS,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "c_v8_repaired_original_campaign": old_first,
        "c_v9_repaired_original_campaign": old_second,
        "c_v10_repaired_original_campaign": current,
        "c_actual_semantic_mismatch_count": 2094,
        "c_verified_passing_case_executions": 7197,
        "rust_actual_semantic_mismatch_count": 2042,
        "rust_verified_passing_case_executions": 7461,
        "zig_actual_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_executions": 3583,
        "cpp_full_original_campaign": {"semantic_mismatch_count": 2308},
        "go_v2_full_original_campaign": {"semantic_mismatch_count": 4518},
        "repaired_c_full_matching_test_status": "FAIL: 1,262 SEMANTIC MISMATCHES",
        "repaired_c_actual_verified_matching_case_count": 31237,
        "repaired_c_verified_passing_case_count": 7325,
        "repaired_c_semantic_mismatch_count": 1262,
        "repaired_c_infrastructure_failure_count": 0,
        "repaired_c_completed_suite_count": 13,
        "repaired_c_actual_candidate_worker_count": 13,
        "repaired_c_native_promoted": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def self_test() -> dict:
    with SourceOnlyWall() as wall:
        base = synthetic_snapshot()
        validate_snapshot(base)
        accepted = 1
        rejected = 0

        def reject(value: object) -> None:
            nonlocal rejected
            try:
                validate_snapshot(value)  # type: ignore[arg-type]
            except (GraphError, KeyError, TypeError, ValueError, AttributeError):
                rejected += 1
                return
            raise GraphError("accepted forged synthetic complete C matching evidence")

        changed = {
            "full_case_denominator": 31236, "suite_count": 12,
            "baseline_passed": 31236,
            "frozen_independent_engine_family_count": 5,
            "current_source_owner_count": 24, "qualified_candidate_count": 1,
            "preserved_v22_repository_evidence_owner_count": 104,
            "preserved_v22_digest_addressed_history_path_count": 109,
            "new_v10_c_campaign_repository_evidence_owner_count": 29,
            "all_actual_candidate_and_native_evidence_owner_count": 134,
            "all_digest_addressed_history_path_count": 139,
            "c_actual_semantic_mismatch_count": 0,
            "c_verified_passing_case_executions": 0,
            "rust_actual_semantic_mismatch_count": 0,
            "rust_verified_passing_case_executions": 0,
            "zig_actual_semantic_mismatch_count": 0,
            "zig_verified_passing_case_executions": 0,
            "repaired_c_full_matching_test_status": "PASS",
            "repaired_c_actual_verified_matching_case_count": 7325,
            "repaired_c_verified_passing_case_count": 31237,
            "repaired_c_semantic_mismatch_count": 0,
            "repaired_c_infrastructure_failure_count": 1,
            "repaired_c_completed_suite_count": 12,
            "repaired_c_actual_candidate_worker_count": 12,
            "repaired_c_native_promoted": True,
            "performance": "1.5x faster", "memory": "0 bytes",
            "confidence_intervals": "95%",
            "hidden_cases_read": 1, "performance_files_read": 1,
            "clock_samples": 1, "timing_trials_run": 1,
            "final_comparison_planned_case_count": 4194303,
            "final_comparison_cases_generated": True,
            "final_holdout_opened": True, "winner_selected": True,
        }
        for key, forged in changed.items():
            altered = copy.deepcopy(base)
            altered[key] = forged
            reject(altered)
        changes = {
            "status": "PASS", "failure_class": "INFRASTRUCTURE FAILURE",
            "label": "phase2-v9-original-p0", "actual_candidate_workers": 12,
            "actual_aggregate_process_count": 0,
            "actual_aggregate_process_exit_status": 0,
            "full_case_denominator": 31236, "suite_count": 12,
            "completed_suite_count": 12, "fully_passing_suite_count": 13,
            "observed_matching_case_count": 7325,
            "verified_passing_case_count": 31237,
            "semantic_mismatch_count": 0,
            "infrastructure_failure_count": 1,
            "all_original_suite_evidence_preserved": False,
            "new_repository_evidence_owner_count": 29,
            "qualified": True,
            "original_canonical_native_restored": False,
            "restoration_status": "FAIL",
        }
        for key, forged in changes.items():
            altered = copy.deepcopy(base)
            altered["c_v10_repaired_original_campaign"][key] = forged
            reject(altered)
        for key, forged in (("infrastructure_failure_count", 0),
                            ("status", "PASS"), ("completed_suite_count", 12)):
            altered = copy.deepcopy(base)
            altered["c_v8_repaired_original_campaign"][key] = forged
            reject(altered)
        for key, forged in (("infrastructure_failure_count", 0),
                            ("actual_candidate_workers", 1),
                            ("semantic_mismatch_count", 0)):
            altered = copy.deepcopy(base)
            altered["c_v9_repaired_original_campaign"][key] = forged
            reject(altered)
        for index, (name, _count, _mismatches, _display) in enumerate(SUITES):
            for key, forged in (("suite", name + "-forged"),
                                ("mismatch_count", -1),
                                ("actual_worker_started", False)):
                altered = copy.deepcopy(base)
                altered["c_v10_repaired_original_campaign"]["suite_results"][index][key] = forged
                reject(altered)
        for key, forged in (("sha256", "0" * 64), ("inode", 430301),
                            ("mode", 0o600), ("nlink", 2)):
            altered = copy.deepcopy(base)
            altered["c_v10_repaired_original_campaign"]["original_canonical_native"][key] = forged
            reject(altered)
        reject({})
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (b"1,262", b"7,325", b"8 of 13", b"NOT MEASURED",
                       b"135", b"140", b"13 old runner failures",
                       b"one runner failure", b"zero infrastructure failures",
                       b"Public types and serialization", b"672 DIFFERENCES"):
            need(phrase in picture, "the accessible graph omits real C evidence")
        probes = (
            lambda: builtins.open("/tmp/rebar-v23-forbidden", "rb"),
            lambda: os.open("/tmp/rebar-v23-forbidden", os.O_RDONLY),
            lambda: os.write(-1, b"forbidden"),
            lambda: subprocess.run(("forbidden-v23-candidate",)),
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
                need(wall.blocked == before + 1,
                     "independently prove every forbidden source-only effect")
                rejected += 1
            else:
                raise GraphError("V23 source-only verification caused a real effect")
        need(rejected >= 95, "require comprehensive hostile actual-C truth controls")
        return {
            "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
            "version": 23, "synthetic_only": True,
            "accepted_synthetic_controls": accepted,
            "rejected_hostile_controls": rejected,
            "blocked_effect_count": wall.blocked,
            "repository_evidence_owner_count": TOTAL_OWNERS,
            "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
            "preserved_v22_evidence_owner_count": PREVIOUS_OWNERS,
            "preserved_v22_history_path_count": PREVIOUS_REFERENCES,
            "new_actual_evidence_owner_count": NEW_OWNERS,
            "suite_count": 13, "full_case_denominator": 31237,
            "current_repaired_c_candidate_worker_count": 13,
            "current_repaired_c_passing_suite_count": 8,
            "current_repaired_c_verified_passing_case_count": 7325,
            "current_repaired_c_semantic_mismatch_count": 1262,
            "current_repaired_c_infrastructure_failure_count": 0,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_holdout_opened": False, "winner_selected": False,
            "synthetic_svg_sha256": digest(picture),
        }


def publish_output(path: str, raw: bytes) -> None:
    need(path in (OUTPUT + ".inputs.json", OUTPUT + ".svg", OUTPUT + ".json")
         and type(raw) is bytes and raw.endswith(b"\n")
         and not raw.endswith(b"\n\n"),
         "publish only the three exact canonical assigned V23 graph outputs")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        position = 0
        while position < len(raw):
            written = os.write(descriptor, raw[position:])
            need(type(written) is int and written > 0,
                 "reject incomplete deterministic V23 graph output")
            position += written
        os.fsync(descriptor)
        recorded = os.fstat(descriptor)
        need(stat.S_ISREG(recorded.st_mode)
             and stat.S_IMODE(recorded.st_mode) == 0o600
             and recorded.st_nlink == 1 and recorded.st_size == len(raw),
             "require one exclusive complete V23 output owner")
    finally:
        os.close(descriptor)
    directory = os.open(str(ROOT / "docs/evidence"),
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_CLOEXEC", 0)
                        | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


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
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(all(getattr(args, key) is None for key in (
                "source_sha256", "campaign_archive_sha256",
                "campaign_receipt_sha256", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            )), "synthetic self-tests cannot authorize actual evidence or publication")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked_digest(args.source_sha256, "V23 source")
        archive = checked_digest(args.campaign_archive_sha256, "genuine V3 campaign archive")
        receipt = checked_digest(args.campaign_receipt_sha256, "genuine V3 campaign receipt")
        manifest, snapshot, outputs = build(source, archive, receipt)
        expected = {path: raw for path, raw in outputs}
        if args.render:
            need(args.inputs_sha256 is None and args.summary_sha256 is None
                 and args.svg_sha256 is None,
                 "source-frozen deterministic rendering cannot accept substituted output pins")
            for path, raw in outputs:
                publish_output(path, raw)
            result = {
                "schema": SCHEMA + "-published", "status": "PASS", "version": 23,
                "source_sha256": source,
                "inputs_sha256": digest(expected[OUTPUT + ".inputs.json"]),
                "summary_sha256": digest(expected[OUTPUT + ".json"]),
                "svg_sha256": digest(expected[OUTPUT + ".svg"]),
                "repository_evidence_owner_count": TOTAL_OWNERS,
                "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
                "new_actual_evidence_owner_count": NEW_OWNERS,
                "current_repaired_c_candidate_worker_count": 13,
                "current_repaired_c_passing_suite_count": 8,
                "current_repaired_c_verified_passing_case_count": 7325,
                "current_repaired_c_semantic_mismatch_count": 1262,
                "current_repaired_c_infrastructure_failure_count": 0,
                "outputs_written": True,
                "actual_candidate_imports": 0,
                "actual_candidate_processes_started": 0,
                "hidden_cases_read": 0, "clock_samples": 0,
                "timing_trials_run": 0,
                "performance": "NOT MEASURED", "memory": "NOT MEASURED",
                "final_holdout_opened": False, "winner_selected": False,
            }
            sys.stdout.buffer.write(canonical(result))
            return 0
        pinned_outputs = {
            OUTPUT + ".inputs.json": checked_digest(args.inputs_sha256, "V23 inputs"),
            OUTPUT + ".json": checked_digest(args.summary_sha256, "V23 summary"),
            OUTPUT + ".svg": checked_digest(args.svg_sha256, "V23 accessible SVG"),
        }
        previous = authenticate_previous()[1]
        for path, fingerprint in pinned_outputs.items():
            raw, _ = previous.read_owner(path, fingerprint, size=len(expected[path]))
            need(raw == expected[path] and digest(raw) == fingerprint,
                 "independently reproduce every published V23 graph byte")
        validate_snapshot(snapshot)
        result = {
            "schema": SCHEMA + "-read-only-frozen-context", "status": "PASS",
            "version": 23, "read_only": True,
            "source_sha256": source,
            "inputs_sha256": pinned_outputs[OUTPUT + ".inputs.json"],
            "summary_sha256": pinned_outputs[OUTPUT + ".json"],
            "svg_sha256": pinned_outputs[OUTPUT + ".svg"],
            "actual_campaign_archive_sha256": archive,
            "actual_campaign_receipt_sha256": receipt,
            "suite_count": 13, "full_case_denominator": 31237,
            "candidate_family_count": 6,
            "repository_evidence_owner_count": TOTAL_OWNERS,
            "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
            "preserved_v22_evidence_owner_count": PREVIOUS_OWNERS,
            "preserved_v22_history_path_count": PREVIOUS_REFERENCES,
            "new_actual_evidence_owner_count": NEW_OWNERS,
            "earliest_repaired_c_infrastructure_failure_count": 13,
            "previous_repaired_c_infrastructure_failure_count": 1,
            "current_repaired_c_candidate_worker_count": 13,
            "current_repaired_c_passing_suite_count": 8,
            "current_repaired_c_verified_passing_case_count": 7325,
            "current_repaired_c_semantic_mismatch_count": 1262,
            "current_repaired_c_infrastructure_failure_count": 0,
            "original_canonical_native_restored": True,
            "original_canonical_native_inode": 430300,
            "original_canonical_native_mode": "0755",
            "qualified_candidate_count": 0,
            "outputs_written": False,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False, "winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            gzip.BadGzipFile, KeyError, AttributeError) as error:
        sys.stderr.write("current V23 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
