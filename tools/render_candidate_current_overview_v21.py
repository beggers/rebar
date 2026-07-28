#!/usr/bin/env python3
"""Render the genuine failed repaired-C retest without inventing matching."""

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


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SCHEMA = "rebar-candidate-current-overview-v21"
SELF = "tools/render_candidate_current_overview_v21.py"
OUTPUT = "docs/evidence/candidate-current-overview-v21"
MAX_FILE = 64 * 1024 * 1024
MAX_REPORT = 4 * 1024 * 1024
V20 = {
    "source": ("tools/render_candidate_current_overview_v20.py", "3f4b63de113743204f2b6736c5486e9160f4f4c029575052676f68943a3210d2"),
    "inputs": ("docs/evidence/candidate-current-overview-v20.inputs.json", "bf09019d4a8df9ab5519a0b6bbbe9c4aaa8574dbcc4a9eafc1b424ba1961f021"),
    "summary": ("docs/evidence/candidate-current-overview-v20.json", "89e89c27a9295bc5c2f0ddb1141bb9969b1fda32a82c546e4afd55bc9c758544"),
    "svg": ("docs/evidence/candidate-current-overview-v20.svg", "44d62f5c497178a404950d7e71d604aafcf41349f621396bf32f2112fa685061"),
}
BUILD_ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v8-c-phase2-v8.json.gz",
    "69a795af6c407c0719b68dfa9fd4cb6dcfca2595271f72b83bc43678521f2598",
    37452,
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v8-c-phase2-v8-publication-receipt.json",
    "3b0983af9729b3150ae239a83dd0fdb37c6e790b3c03ebea48c77215f51456b8",
    1848,
)
OUTER_ARCHIVE = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures.json.gz",
    "a8319a686c2486e27374bfb9c6ada4e4ec104c27c1cafdbc2205c98f40fa9fb7",
    5120,
)
OUTER_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures-publication-receipt.json",
    "034207331f8d61ef69f510cb42b9babe921b85570c571198ea8eb310c75ffecd",
    933,
)
AGGREGATE_ARCHIVE = (
    "oracle/phase2/evidence/frozen-p0-candidate-v8-c-phase2-v8-original-p0-failures.json.gz",
    "28aa89319262d9ba14ad6f07931d880770ef18dc025610750fa3b99c68d2f32f",
    10286,
)
AGGREGATE_RECEIPT = (
    "oracle/phase2/evidence/frozen-p0-candidate-v8-c-phase2-v8-original-p0-failures-publication-receipt.json",
    "088736e5329b24bab3f2fb8c5069c005b8adeb1afc27cf84742b26be923ee71d",
    2945,
)
ORIGINAL_NATIVE = (
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd",
    149976,
)
ORIGINAL_C_SHA = "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
DERIVED_C_SHA = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
REPAIRED_NATIVE_SHA = "60e50499c34267927e8d312908d7d86b536106b32f418f76453833df7e91694f"
PRODUCER_SHA = "36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33"
OWNER_FAILURE = (
    "ProducerError: require genuinely owned Pattern and Match, "
    "including Python-owned C++ types"
)
REFERENCE_FAILURE = (
    "CandidateGateError: the authenticated complete original "
    "reference vector is absent: reference_a"
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


class GraphError(Exception):
    """Reject inaccurate, substituted, or incomplete campaign evidence."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only complete original evidence bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise GraphError("invalid canonical V21 graph value") from error


def checked_digest(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(char in "0123456789abcdef" for char in value),
         "invalid " + label + " SHA-256")
    return value


def checked_path(value: object) -> tuple[str, ...]:
    need(type(value) is str and 0 < len(value) <= 512
         and "\\" not in value and "\x00" not in value,
         "invalid signed evidence path")
    parsed = PurePosixPath(value)
    need(not parsed.is_absolute() and str(parsed) == value
         and 0 < len(parsed.parts) <= 12
         and all(part not in ("", ".", "..") for part in parsed.parts),
         "signed evidence path escaped its repository")
    return parsed.parts


def read_owner(path: str, expected: str, *, size: int | None = None,
               private: bool = False,
               maximum: int = MAX_FILE) -> tuple[bytes, dict]:
    checked_digest(expected, path)
    parts = checked_path(path)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for component in parts[:-1]:
            following = os.open(component, flags | os.O_DIRECTORY,
                                dir_fd=directory)
            os.close(directory)
            directory = following
        fd = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(fd)
            named = os.stat(parts[-1], dir_fd=directory,
                            follow_symlinks=False)
            need(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                 and (before.st_dev, before.st_ino)
                 == (named.st_dev, named.st_ino)
                 and 0 < before.st_size <= maximum,
                 "substituted, missing, or oversized owner: " + path)
            if size is not None:
                need(before.st_size == size,
                     "changed exact evidence owner size: " + path)
            if private:
                need(stat.S_IMODE(before.st_mode) == 0o600
                     and before.st_uid == os.geteuid()
                     and before.st_nlink == 1,
                     "campaign evidence must have its genuine private owner")
            pieces: list[bytes] = []
            remaining = before.st_size
            while remaining:
                piece = os.read(fd, min(remaining, 1024 * 1024))
                need(bool(piece), "truncated signed evidence owner")
                pieces.append(piece)
                remaining -= len(piece)
            need(os.read(fd, 1) == b"", "concealed trailing owner bytes")
            after = os.fstat(fd)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "evidence changed during authenticated descriptor read")
            raw = b"".join(pieces)
            need(digest(raw) == expected, "changed genuine owner: " + path)
            return raw, {
                "path": path, "sha256": expected, "bytes": before.st_size,
                "device": before.st_dev, "inode": before.st_ino,
                "mode": stat.S_IMODE(before.st_mode),
                "nlink": before.st_nlink, "uid": before.st_uid,
            }
        finally:
            os.close(fd)
    finally:
        os.close(directory)


def unique(pairs: list[tuple[str, object]]) -> dict:
    found: dict[str, object] = {}
    for key, value in pairs:
        need(type(key) is str and key not in found,
             "duplicate signed graph JSON key")
        found[key] = value
    return found


def document(raw: bytes, name: str) -> dict:
    try:
        value = json.loads(
            raw, object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("non-finite signed JSON")),
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise GraphError("invalid signed JSON: " + name) from error
    need(type(value) is dict and canonical(value) == raw,
         "noncanonical signed evidence owner: " + name)
    return value


def pin(path: str, sha: str, size: int | None = None) -> dict:
    checked_path(path)
    checked_digest(sha, path)
    result: dict[str, object] = {"path": path, "sha256": sha}
    if size is not None:
        need(type(size) is int and size > 0, "invalid exact evidence size")
        result["bytes"] = size
    return result


def boundary(value: dict, label: str) -> None:
    need(type(value) is dict
         and value.get("hidden_cases_read") == 0
         and value.get("clock_samples") == 0
         and value.get("timing_trials_run") == 0
         and value.get("holdout") == "NOT OPENED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("memory") == "NOT MEASURED"
         and value.get("winner_selected") is False,
         label + " crossed the sealed performance or holdout boundary")


def owner_from_signed(value: object, label: str) -> tuple[bytes, dict]:
    need(type(value) is dict, "missing signed " + label + " owner")
    relative = value.get("relative")
    expected = checked_digest(value.get("sha256"), label)
    length = value.get("size_bytes")
    need(type(length) is int and 0 < length <= MAX_FILE,
         "invalid exact signed " + label + " owner length")
    raw, owner = read_owner(relative, expected, size=length, private=True)
    need(value.get("device") == owner["device"]
         and value.get("inode") == owner["inode"]
         and value.get("mode") == owner["mode"] == 0o600,
         "substituted signed " + label + " owner inode or mode")
    return raw, owner


def expand_archive(compressed: bytes, *, expected_sha: str,
                   expected_bytes: int, label: str) -> dict:
    checked_digest(expected_sha, label + " uncompressed")
    need(type(expected_bytes) is int and 0 < expected_bytes <= MAX_REPORT,
         "invalid bounded " + label + " archive size")
    try:
        expanded = gzip.decompress(compressed)
    except (EOFError, OSError, gzip.BadGzipFile) as error:
        raise GraphError("invalid deterministic " + label + " archive") from error
    need(len(expanded) == expected_bytes
         and digest(expanded) == expected_sha
         and gzip.compress(expanded, compresslevel=9, mtime=0) == compressed,
         "noncanonical, concatenated, or substituted " + label + " archive")
    return document(expanded, label + " expanded report")


def require_published_archive(receipt: dict, archive: dict,
                              label: str) -> None:
    recorded = receipt.get("archive")
    need(type(recorded) is dict
         and recorded.get("relative") == archive["path"]
         and recorded.get("sha256") == archive["sha256"]
         and recorded.get("size_bytes") == archive["bytes"]
         and recorded.get("device") == archive["device"]
         and recorded.get("inode") == archive["inode"]
         and recorded.get("mode") == archive["mode"] == 0o600
         and recorded.get("exclusive_creation") is True
         and recorded.get("file_fsync_completed") is True
         and recorded.get("directory_fsync_completed") is True
         and recorded.get("same_inode_readback_verified") is True,
         "require durable original " + label + " archive publication")


def authenticate_previous() -> tuple[dict, dict, dict[str, str]]:
    previous: dict[str, bytes] = {}
    for name, (path, sha) in V20.items():
        previous[name], _ = read_owner(path, sha)
    namespace: dict[str, object] = {"__name__": "_rebar_frozen_v20_graph"}
    exec(compile(previous["source"], str(ROOT / V20["source"][0]), "exec"),
         namespace)
    _v19, snapshot, outputs = namespace["build"](
        V20["source"][1], BUILD_ARCHIVE[1], BUILD_RECEIPT[1],
    )
    for path, raw in outputs:
        namespace["publish_output"](path, raw, verify=True)
    old_inputs = document(previous["inputs"], "frozen V20 inputs")
    old_summary = document(previous["summary"], "frozen V20 summary")
    need(old_summary.get("schema") == "rebar-candidate-current-overview-v20-summary"
         and old_summary.get("status") == "PASS"
         and old_summary.get("snapshot") == snapshot
         and old_summary.get("repository_evidence_owner_count") == 73
         and old_summary.get("authenticated_digest_addressed_history_paths") == 78
         and old_inputs.get("repository_evidence_owner_count") == 73
         and old_inputs.get("all_digest_addressed_history_path_count") == 78,
         "require all four unchanged, independently reproduced V20 owners")
    prior = namespace["PRIOR"]
    v19_inputs_raw, _ = read_owner(*prior["inputs"])
    v19_summary_raw, _ = read_owner(*prior["summary"])
    history: dict[str, str] = {}
    namespace["discover_history"](document(v19_inputs_raw, "frozen V19 inputs"),
                                  history)
    namespace["discover_history"](document(v19_summary_raw, "frozen V19 summary"),
                                  history)
    need(len(history) == 76, "require exactly 76 preserved V19 references")
    for path, sha in ((BUILD_ARCHIVE[0], BUILD_ARCHIVE[1]),
                      (BUILD_RECEIPT[0], BUILD_RECEIPT[1])):
        need(path not in history, "V8 build owners must be genuinely additional")
        history[path] = sha
    need(len(history) == 78, "require exactly 78 preserved V20 references")
    return old_summary, snapshot, history


def validate_worker(row: dict, suite: str, denominator: int,
                    aggregate_row: dict) -> tuple[dict, str, tuple[dict, dict]]:
    need(type(row) is dict and type(aggregate_row) is dict
         and row.get("suite") == aggregate_row.get("suite") == suite
         and row.get("case_execution_denominator")
         == aggregate_row.get("case_execution_denominator") == denominator
         and row.get("status") == aggregate_row.get("status") == "FAIL"
         and row.get("failure_class")
         == aggregate_row.get("failure_class") == "INFRASTRUCTURE FAILURE"
         and row.get("mismatch_count") is None
         and aggregate_row.get("mismatch_count") is None,
         "never turn an unobserved " + suite + " match into a semantic result")
    compressed, archive = owner_from_signed(row.get("archive"), suite + " archive")
    receipt_raw, receipt_owner = owner_from_signed(
        row.get("receipt"), suite + " receipt",
    )
    receipt = document(receipt_raw, suite + " durable receipt")
    require_published_archive(receipt, archive, suite)
    need(receipt.get("schema")
         == "rebar-frozen-python-re-p0-candidate-worker-v6-durable-suite-publication-receipt"
         and receipt.get("status") == "PASS"
         and receipt.get("candidate_family") == "c"
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("candidate_qualified") is False
         and receipt.get("suite") == suite
         and receipt.get("case_execution_denominator") == denominator
         and receipt.get("phase_one_case_execution_denominator") == 31237
         and receipt.get("mismatch_count") is None
         and receipt.get("genuine_original_suite") is False
         and receipt.get("all_original_records_and_mismatches_preserved") is True
         and receipt.get("historical_evidence_owner_count") == 71
         and receipt.get("historical_authenticated_reference_count") == 76
         and receipt.get("derived_c_source_sha256") == DERIVED_C_SHA
         and receipt.get("original_c_source_sha256") == ORIGINAL_C_SHA
         and receipt.get("original_producer_sha256") == PRODUCER_SHA,
         "changed authenticated " + suite + " failure receipt")
    boundary(receipt, suite + " receipt")
    expanded_sha = checked_digest(row.get("uncompressed_sha256"), suite)
    expanded_bytes = row.get("uncompressed_bytes")
    need(receipt.get("uncompressed_sha256") == expanded_sha
         and receipt.get("uncompressed_bytes") == expanded_bytes
         and aggregate_row.get("uncompressed_sha256") == expanded_sha
         and aggregate_row.get("uncompressed_bytes") == expanded_bytes,
         "changed " + suite + " original uncompressed failure")
    worker = expand_archive(compressed, expected_sha=expanded_sha,
                            expected_bytes=expanded_bytes, label=suite)
    need(worker.get("schema")
         == "rebar-frozen-python-re-p0-candidate-worker-v6-complete-original-suite-failure"
         and worker.get("status") == "FAIL"
         and worker.get("candidate_family") == "c"
         and worker.get("candidate_qualified") is False
         and worker.get("suite") == suite
         and worker.get("case_execution_denominator") == denominator
         and worker.get("genuine_original_suite") is False
         and worker.get("mismatch_count") is None
         and worker.get("derived_c_source_sha256") == DERIVED_C_SHA
         and worker.get("original_c_source_sha256") == ORIGINAL_C_SHA
         and worker.get("original_producer_sha256") == PRODUCER_SHA,
         "changed original " + suite + " infrastructure failure")
    boundary(worker, suite + " report")
    traceback = worker.get("traceback")
    need(type(traceback) is list and all(type(line) is str for line in traceback),
         "missing complete authenticated " + suite + " traceback")
    trace = "".join(traceback)
    if suite == "public_types_v1":
        need(worker.get("error_type") == "CandidateGateError"
             and worker.get("error_message")
             == "the authenticated complete original reference vector is absent: reference_a"
             and REFERENCE_FAILURE in trace,
             "preserve the separate missing original reference-vector failure")
        cause = "SAVED PYTHON REFERENCE DECODING"
    else:
        if suite == "original_bounded_v5":
            expected_error = "the literal unchanged upstream public-method source failed"
        elif suite == "subinterpreter_v2":
            expected_error = (
                "retain every genuine failed private-interpreter call and cleanup"
            )
        else:
            expected_error = "preserve the complete genuine original case failure: " + suite
        need(worker.get("error_type") == "ActualSuiteFailure"
             and worker.get("error_message") == expected_error
             and OWNER_FAILURE in trace,
             "preserve the actual owned Pattern and Match producer failure")
        cause = "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK"
    return {
        "suite": suite,
        "case_execution_denominator": denominator,
        "status": "FAIL",
        "failure_class": "INFRASTRUCTURE FAILURE",
        "failure_cause": cause,
        "observed_matching_case_count": 0,
        "semantic_mismatches": "NOT MEASURED",
        "archive": pin(archive["path"], archive["sha256"], archive["bytes"]),
        "receipt": pin(receipt_owner["path"], receipt_owner["sha256"],
                       receipt_owner["bytes"]),
        "uncompressed_sha256": expanded_sha,
        "uncompressed_bytes": expanded_bytes,
    }, cause, (archive, receipt_owner)


def authenticate_campaign(archive_sha: str,
                          receipt_sha: str) -> tuple[dict, dict[str, str]]:
    need(archive_sha == OUTER_ARCHIVE[1]
         and receipt_sha == OUTER_RECEIPT[1],
         "caller must independently pin both recovered C campaign owners")
    outer_compressed, outer_owner = read_owner(
        OUTER_ARCHIVE[0], archive_sha, size=OUTER_ARCHIVE[2], private=True,
    )
    outer_receipt_raw, outer_receipt_owner = read_owner(
        OUTER_RECEIPT[0], receipt_sha, size=OUTER_RECEIPT[2], private=True,
    )
    outer_receipt = document(outer_receipt_raw, "recovered campaign receipt")
    require_published_archive(outer_receipt, outer_owner, "recovered campaign")
    need(outer_receipt.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v1-durable-publication-receipt"
         and outer_receipt.get("status") == "PASS"
         and outer_receipt.get("candidate_status") == "FAIL"
         and outer_receipt.get("family") == "c"
         and outer_receipt.get("label") == "phase2-v8-original-p0"
         and outer_receipt.get("case_execution_denominator") == 31237
         and outer_receipt.get("suite_count") == 13
         and outer_receipt.get("historical_evidence_owner_count") == 73
         and outer_receipt.get("historical_authenticated_reference_count") == 78
         and outer_receipt.get("original_native_restored") is True
         and outer_receipt.get("holdout") == "NOT OPENED"
         and outer_receipt.get("performance") == "NOT MEASURED"
         and outer_receipt.get("memory") == "NOT MEASURED"
         and outer_receipt.get("winner_selected") is False,
         "changed recovered repaired-C publication receipt")
    outer = expand_archive(
        outer_compressed,
        expected_sha=outer_receipt.get("uncompressed_sha256"),
        expected_bytes=outer_receipt.get("uncompressed_bytes"),
        label="recovered repaired-C campaign",
    )
    need(outer.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v1-actual-recovered-campaign"
         and outer.get("status") == "FAIL"
         and outer.get("family") == "c"
         and outer.get("label") == "phase2-v8-original-p0"
         and outer.get("case_execution_denominator") == 31237
         and outer.get("suite_count") == 13
         and outer.get("completed_suite_count") == 13
         and outer.get("infrastructure_failure_count") == 13
         and outer.get("verified_passing_case_count") == 0
         and outer.get("semantic_mismatch_count") == 0
         and outer.get("all_original_suite_evidence_preserved") is True
         and outer.get("named_private_waiver_count") == 13
         and outer.get("candidate_qualified") is False
         and outer.get("original_native_restored") is True
         and outer.get("actual_build_archive_sha256") == BUILD_ARCHIVE[1]
         and outer.get("actual_build_receipt_sha256") == BUILD_RECEIPT[1]
         and outer.get("actual_repaired_native_sha256") == REPAIRED_NATIVE_SHA
         and outer.get("derived_c_source_sha256") == DERIVED_C_SHA
         and outer.get("original_c_source_sha256") == ORIGINAL_C_SHA
         and outer.get("original_producer_sha256") == PRODUCER_SHA
         and outer.get("historical_evidence_owner_count") == 73
         and outer.get("historical_authenticated_reference_count") == 78
         and outer.get("v19_historical_evidence_owner_count") == 71
         and outer.get("v19_historical_reference_path_count") == 76
         and outer.get("benchmark_files_read") == 0,
         "changed actual failed 13-suite repaired-C campaign")
    boundary(outer, "recovered repaired-C campaign")
    aggregate_compressed, aggregate_owner = owner_from_signed(
        outer.get("original_aggregate_archive"), "original aggregate archive",
    )
    aggregate_receipt_raw, aggregate_receipt_owner = owner_from_signed(
        outer.get("original_aggregate_receipt"), "original aggregate receipt",
    )
    need((aggregate_owner["path"], aggregate_owner["sha256"],
          aggregate_owner["bytes"]) == AGGREGATE_ARCHIVE
         and (aggregate_receipt_owner["path"], aggregate_receipt_owner["sha256"],
              aggregate_receipt_owner["bytes"]) == AGGREGATE_RECEIPT,
         "require the exact two originally published full-campaign owners")
    aggregate_receipt = document(aggregate_receipt_raw,
                                 "original aggregate durable receipt")
    require_published_archive(aggregate_receipt, aggregate_owner,
                              "original aggregate")
    need(aggregate_receipt.get("schema")
         == "rebar-frozen-python-re-p0-candidate-v8-durable-publication-receipt"
         and aggregate_receipt.get("status") == "PASS"
         and aggregate_receipt.get("candidate_status") == "FAIL"
         and aggregate_receipt.get("candidate_family") == "c"
         and aggregate_receipt.get("label") == "phase2-v8-original-p0"
         and aggregate_receipt.get("case_execution_denominator") == 31237
         and aggregate_receipt.get("suite_count") == 13
         and aggregate_receipt.get("completed_suite_count") == 13
         and aggregate_receipt.get("named_private_waiver_count", 13) == 13
         and aggregate_receipt.get("all_original_suite_evidence_preserved") is True
         and aggregate_receipt.get("historical_evidence_owner_count") == 71
         and aggregate_receipt.get("historical_authenticated_reference_count") == 76
         and aggregate_receipt.get("derived_c_source_sha256") == DERIVED_C_SHA
         and aggregate_receipt.get("original_c_source_sha256") == ORIGINAL_C_SHA
         and aggregate_receipt.get("original_producer_sha256") == PRODUCER_SHA,
         "changed original frozen full-campaign publication receipt")
    boundary(aggregate_receipt, "original aggregate receipt")
    aggregate = expand_archive(
        aggregate_compressed,
        expected_sha=aggregate_receipt.get("uncompressed_sha256"),
        expected_bytes=aggregate_receipt.get("uncompressed_bytes"),
        label="original frozen repaired-C aggregate",
    )
    need(aggregate.get("schema")
         == "rebar-frozen-python-re-p0-candidate-v8-complete-original-candidate-evaluation"
         and aggregate.get("status") == "FAIL"
         and aggregate.get("candidate_family") == "c"
         and aggregate.get("candidate_qualified") is False
         and aggregate.get("case_execution_denominator") == 31237
         and aggregate.get("suite_count") == 13
         and aggregate.get("completed_suite_count") == 13
         and aggregate.get("actual_candidate_workers") == 13
         and aggregate.get("infrastructure_failure_count") == 13
         and aggregate.get("verified_passing_case_count") == 0
         and aggregate.get("semantic_mismatch_count") == 0
         and aggregate.get("named_private_waiver_count") == 13
         and aggregate.get("all_original_suite_evidence_preserved") is True
         and aggregate.get("actual_v8_build_archive_sha256") == BUILD_ARCHIVE[1]
         and aggregate.get("actual_v8_build_receipt_sha256") == BUILD_RECEIPT[1]
         and aggregate.get("derived_c_source_sha256") == DERIVED_C_SHA
         and aggregate.get("original_c_source_sha256") == ORIGINAL_C_SHA
         and aggregate.get("original_producer_sha256") == PRODUCER_SHA
         and aggregate.get("nested_producer_sha256") == PRODUCER_SHA
         and aggregate.get("historical_evidence_owner_count") == 71
         and aggregate.get("historical_authenticated_reference_count") == 76
         and aggregate.get("benchmark_files_read") == 0,
         "changed original 13-suite aggregate infrastructure failure")
    boundary(aggregate, "original full-campaign aggregate")
    signed_suites = outer.get("original_suite_results")
    aggregate_suites = aggregate.get("suite_results")
    need(type(signed_suites) is list and type(aggregate_suites) is list
         and len(signed_suites) == len(aggregate_suites) == len(SUITES),
         "require all 13 original distinct archived suite failures")
    owners: dict[str, str] = {}
    for item in (outer_owner, outer_receipt_owner,
                 aggregate_owner, aggregate_receipt_owner):
        need(item["path"] not in owners, "duplicate actual campaign owner")
        owners[item["path"]] = item["sha256"]
    workers: list[dict] = []
    causes: dict[str, int] = {}
    for expected, signed_row, aggregate_row in zip(
        SUITES, signed_suites, aggregate_suites, strict=True,
    ):
        proof, cause, pair = validate_worker(
            signed_row, expected[0], expected[1], aggregate_row,
        )
        workers.append(proof)
        causes[cause] = causes.get(cause, 0) + 1
        for item in pair:
            need(item["path"] not in owners,
                 "each original suite needs its own genuine evidence owner")
            owners[item["path"]] = item["sha256"]
    need(len(owners) == 30
         and sum(row["case_execution_denominator"] for row in workers) == 31237
         and causes == {
             "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 12,
             "SAVED PYTHON REFERENCE DECODING": 1,
         }, "require all 30 actual owners and exactly two genuine failure causes")
    process = outer.get("original_aggregate_process")
    need(type(process) is dict and process.get("actual_aggregate_processes") == 1
         and process.get("returncode") == 1
         and process.get("timed_out") is False,
         "preserve the actual failing aggregate process, not a synthetic run")
    for stream in ("stdout", "stderr"):
        encoded = process.get(stream + "_base64")
        need(type(encoded) is str, "missing authenticated aggregate " + stream)
        try:
            raw_stream = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError) as error:
            raise GraphError("invalid signed aggregate " + stream) from error
        need(len(raw_stream) == process.get(stream + "_bytes")
             and digest(raw_stream) == process.get(stream + "_sha256"),
             "changed actual aggregate " + stream + " bytes")
        if stream == "stdout":
            published = document(raw_stream, "actual aggregate process stdout")
            need(published.get("schema")
                 == "rebar-frozen-python-re-p0-candidate-v8-published-complete-candidate"
                 and published.get("status") == "FAIL"
                 and published.get("candidate_family") == "c"
                 and published.get("completed_suite_count") == 13
                 and published.get("infrastructure_failure_count") == 13
                 and published.get("semantic_mismatch_count") == 0
                 and published.get("verified_passing_case_count") == 0
                 and published.get("archive") == aggregate_receipt["archive"]
                 and published.get("receipt", {}).get("relative")
                 == aggregate_receipt_owner["path"]
                 and published.get("receipt", {}).get("sha256")
                 == aggregate_receipt_owner["sha256"]
                 and published.get("holdout") == "NOT OPENED"
                 and published.get("performance") == "NOT MEASURED"
                 and published.get("memory") == "NOT MEASURED"
                 and published.get("winner_selected") is False,
                 "actual failing aggregate stdout does not authenticate both owners")
    native_raw, native = read_owner(
        ORIGINAL_NATIVE[0], ORIGINAL_NATIVE[1], size=ORIGINAL_NATIVE[2],
    )
    need(digest(native_raw) != REPAIRED_NATIVE_SHA
         and native["device"] == 2064 and native["inode"] == 430300
         and native["mode"] == 0o755 and native["nlink"] == 1,
         "require the exact genuinely restored original 0755 native inode")
    declared_original = outer.get("original_native_owner")
    recovery = outer.get("recovery")
    need(type(declared_original) is dict
         and declared_original.get("relative") == native["path"]
         and declared_original.get("sha256") == native["sha256"]
         and declared_original.get("bytes") == native["bytes"]
         and declared_original.get("device") == native["device"]
         and declared_original.get("inode") == native["inode"]
         and declared_original.get("mode") == native["mode"]
         and declared_original.get("nlink") == native["nlink"]
         and type(recovery) is dict
         and recovery.get("route") == "existing-authenticated-restoration-receipt"
         and type(recovery.get("report")) is dict,
         "require the authenticated preserved original canonical native owner")
    restoration = recovery["report"]
    aggregate_restoration = aggregate.get("restoration")
    receipt_restoration = aggregate_receipt.get("restoration")
    need(type(aggregate_restoration) is dict
         and aggregate_restoration == receipt_restoration,
         "require matching original aggregate and receipt restoration reports")
    complete_restoration = copy.deepcopy(aggregate_restoration)
    private_receipt = complete_restoration.pop("restoration_receipt", None)
    declared_private_receipt = recovery.get("owner")
    need(type(private_receipt) is dict
         and type(declared_private_receipt) is dict
         and all(private_receipt.get(key) == declared_private_receipt.get(key)
                 for key in ("bytes", "device", "inode", "mode", "nlink",
                             "path", "relative", "sha256", "uid"))
         and private_receipt.get("exclusive_creation") is True
         and private_receipt.get("file_fsync_completed") is True
         and private_receipt.get("directory_fsync_completed") is True
         and private_receipt.get("same_inode_readback_verified") is True,
         "preserve, without counting, the private durable restoration receipt")
    need(restoration.get("schema")
         == "rebar-phase2-verified-native-activation-v5-actual-restoration"
         and restoration.get("status") == "PASS"
         and restoration.get("route") == "journal-backed-restore"
         and restoration.get("target") == native["path"]
         and restoration.get("original_inode_preserved") is True
         and restoration.get("originally_absent") is False
         and restoration.get("original") == declared_original
         and complete_restoration == restoration,
         "preserve the genuine journal-backed restored original inode")
    proof = {
        "status": "FAIL",
        "failure_class": "INFRASTRUCTURE FAILURE; MATCHING NOT MEASURED",
        "family": "c",
        "label": "phase2-v8-original-p0",
        "full_case_denominator": 31237,
        "suite_count": 13,
        "completed_suite_count": 13,
        "infrastructure_failure_count": 13,
        "failure_causes": causes,
        "observed_matching_case_count": 0,
        "verified_passing_case_count": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "qualified": False,
        "actual_aggregate_process_count": 1,
        "actual_aggregate_process_exit_status": 1,
        "all_original_suite_evidence_preserved": True,
        "suite_results": workers,
        "new_repository_evidence_owner_count": 30,
        "archive": pin(outer_owner["path"], outer_owner["sha256"],
                       outer_owner["bytes"]),
        "receipt": pin(outer_receipt_owner["path"],
                       outer_receipt_owner["sha256"], outer_receipt_owner["bytes"]),
        "original_aggregate_archive": pin(
            aggregate_owner["path"], aggregate_owner["sha256"],
            aggregate_owner["bytes"],
        ),
        "original_aggregate_receipt": pin(
            aggregate_receipt_owner["path"], aggregate_receipt_owner["sha256"],
            aggregate_receipt_owner["bytes"],
        ),
        "derived_source_sha256": DERIVED_C_SHA,
        "repaired_native_sha256": REPAIRED_NATIVE_SHA,
        "original_canonical_native_restored": True,
        "original_canonical_native": {
            "path": native["path"], "sha256": native["sha256"],
            "bytes": native["bytes"], "device": native["device"],
            "inode": native["inode"], "mode": native["mode"],
            "nlink": native["nlink"], "present": True,
            "is_repaired_v8_native": False,
        },
        "restoration_status": "PASS",
        "restoration_route": "journal-backed-restore",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, owners


def validate_snapshot(snap: dict) -> None:
    need(type(snap) is dict
         and snap.get("full_case_denominator") == 31237
         and snap.get("suite_count") == 13
         and tuple(snap.get("suite_ids", ()))
         == tuple(name for name, _ in SUITES)
         and snap.get("baseline_passed") == 31237
         and snap.get("frozen_independent_engine_family_count") == 6
         and snap.get("current_source_owner_count") == 25
         and snap.get("current_tested_candidate_family_count") == 5
         and snap.get("qualified_candidate_count") == 0
         and snap.get("verified_activation_v4_actual_activation_count") == 3
         and snap.get("verified_activation_v4_current_active_target_count") == 0
         and snap.get("preserved_v20_repository_evidence_owner_count") == 73
         and snap.get("new_repaired_c_campaign_repository_evidence_owner_count") == 30
         and snap.get("all_actual_candidate_and_native_evidence_owner_count") == 103
         and snap.get("preserved_v20_digest_addressed_history_path_count") == 78
         and snap.get("all_digest_addressed_history_path_count") == 108,
         "reject altered original denominators, families, owners, or references")
    need(snap.get("c_actual_semantic_mismatch_count") == 2094
         and snap.get("c_verified_passing_case_executions") == 7197
         and snap.get("rust_actual_semantic_mismatch_count") == 2042
         and snap.get("rust_verified_passing_case_executions") == 7461
         and snap.get("zig_actual_semantic_mismatch_count") == 1764
         and snap.get("zig_verified_passing_case_executions") == 3583,
         "never erase previous genuine C, Rust, or Zig semantic failures")
    c = snap.get("c_full_gate")
    cpp = snap.get("cpp_full_original_campaign")
    go = snap.get("go_v2_full_original_campaign")
    need(type(c) is dict and c.get("gate_status") == "FAIL"
         and c.get("actual_semantic_mismatch_count") == 2094
         and c.get("qualified_candidate_count") == 0
         and type(cpp) is dict and cpp.get("status") == "FAIL"
         and cpp.get("semantic_mismatch_count") == 2308
         and cpp.get("verified_passing_case_count") == 128
         and type(go) is dict and go.get("status") == "FAIL"
         and go.get("semantic_mismatch_count") == 4518
         and go.get("infrastructure_failure_count") == 4
         and go.get("verified_passing_case_count") == 128
         and go.get("restoration_status") == "PASS",
         "never replace previous C, C++, or Go failures with repaired results")
    build = snap.get("c_v8_repaired_build")
    need(type(build) is dict and build.get("status") == "PASS"
         and build.get("phase_count") == 2
         and build.get("compiler_process_count") == 14
         and build.get("native_sha256") == REPAIRED_NATIVE_SHA
         and build.get("complete_native_elf_byte_identical") is True
         and snap.get("historical_compiler_process_count_before_v8") == 169
         and snap.get("historical_compiler_process_count_including_v8") == 183,
         "preserve the actual reproducible historical repaired-C build")
    proof = snap.get("c_v8_repaired_original_campaign")
    need(type(proof) is dict and proof.get("status") == "FAIL"
         and proof.get("suite_count") == 13
         and proof.get("completed_suite_count") == 13
         and proof.get("infrastructure_failure_count") == 13
         and proof.get("observed_matching_case_count") == 0
         and proof.get("verified_passing_case_count") == 0
         and proof.get("semantic_mismatch_count") == "NOT MEASURED"
         and proof.get("failure_causes") == {
             "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 12,
             "SAVED PYTHON REFERENCE DECODING": 1,
         }
         and proof.get("new_repository_evidence_owner_count") == 30
         and proof.get("qualified") is False
         and type(proof.get("suite_results")) is list
         and len(proof["suite_results"]) == 13,
         "require thirteen failed infrastructure groups and no observed matching")
    for expected, row in zip(SUITES, proof["suite_results"], strict=True):
        need(type(row) is dict and row.get("suite") == expected[0]
             and row.get("case_execution_denominator") == expected[1]
             and row.get("status") == "FAIL"
             and row.get("failure_class") == "INFRASTRUCTURE FAILURE"
             and row.get("observed_matching_case_count") == 0
             and row.get("semantic_mismatches") == "NOT MEASURED",
             "never present unobserved suite matching as zero mismatches")
    native = snap.get("existing_canonical_c_native_target")
    need(type(native) is dict and native.get("present") is True
         and native.get("path") == ORIGINAL_NATIVE[0]
         and native.get("sha256") == ORIGINAL_NATIVE[1]
         and native.get("bytes") == ORIGINAL_NATIVE[2]
         and native.get("device") == 2064
         and native.get("inode") == 430300
         and native.get("mode") == 0o755
         and native.get("is_repaired_v8_native") is False
         and snap.get("repaired_c_full_matching_test_status")
         == "TEST-RUNNER FAILED; MATCHING NOT MEASURED"
         and snap.get("repaired_c_native_promoted") is False
         and snap.get("repaired_c_actual_verified_matching_case_count") == 0
         and snap.get("repaired_c_semantic_mismatch_count") == "NOT MEASURED"
         and snap.get("repaired_c_infrastructure_failure_count") == 13
         and snap.get("repaired_c_completed_suite_count") == 13,
         "require the genuinely restored original inode and honest repaired-C state")
    need(snap.get("performance") == "NOT MEASURED"
         and snap.get("memory") == "NOT MEASURED"
         and snap.get("confidence_intervals") == "NOT MEASURED"
         and snap.get("hidden_cases_read") == 0
         and snap.get("performance_files_read") == 0
         and snap.get("clock_samples") == 0
         and snap.get("timing_trials_run") == 0
         and snap.get("final_comparison_planned_case_count") == 4194304
         and snap.get("final_comparison_cases_generated") is False
         and snap.get("final_holdout_opened") is False
         and snap.get("winner_selected") is False,
         "never invent speed, confidence, a winner, or an opened holdout")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def make_svg(snap: dict, source_sha: str, manifest_sha: str) -> bytes:
    validate_snapshot(snap)
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1660" height="1720" viewBox="0 0 1660 1720" role="img" aria-labelledby="v21-title v21-description">',
        '<title id="v21-title">Building a faster Python re: compatibility and the actual failed repaired C retest</title>',
        '<desc id="v21-description">Python passes its original 31,237 reference cases. None of six replacement families is fully compatible. The repaired first-party C build was tested through all 13 original suite workers; every worker stopped before matching. Twelve runner ownership checks rejected Python-compatible public type names, and one runner could not decode its already saved Python reference. Consequently zero matches were observed and repaired matching is not measured. The previous C, Rust, Zig, C++, and Go mismatches remain preserved. The exact original C binary was restored. All 103 actual repository evidence owners and 108 digest references are authenticated. Speed and memory are not measured and the planned 4,194,304-case holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:34px;font-weight:760;fill:#16324f}.heading{font-size:25px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:18px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.pending{font-size:15px;font-weight:740;fill:#53667b}.big{font-size:26px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}</style>',
        '<rect width="1660" height="1720" rx="22" fill="#f4f7fb"/>',
        '<text x="54" y="69" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="56" y="100" class="body">The repaired C test runner failed before matching. Compatibility and speed remain unproven.</text>',
    ]
    cards = (
        ("31,237", "original Python reference checks"),
        ("0 of 6", "fully compatible replacements"),
        ("13 of 13", "repaired C test groups failed"),
        ("103", "actual evidence files"),
        ("NOT MEASURED", "speed and memory"),
    )
    for index, (number, label) in enumerate(cards):
        x = 54 + index * 320
        lines.extend((
            f'<rect x="{x}" y="124" width="304" height="104" rx="13" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 14}" y="168" class="big">{xml(number)}</text>',
            f'<text x="{x + 14}" y="203" class="body">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="54" y="248" width="1552" height="995" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="76" y="290" class="heading">1. Does it behave like Python?</text>',
        '<text x="77" y="318" class="body">The fixed reference contains 13 test groups and 31,237 cases. A failed runner is not a passing matching result.</text>',
    ))
    rows = (
        ("Python re", "PASSED", "31,237 of 31,237 frozen reference checks passed.", "pass"),
        ("C - last previously matched version", "FAILED", "7,197 verified passes and 2,094 genuine matching differences; historical result preserved.", "fail"),
        ("C repair - actual new full retest", "RUNNER FAILED", "All 13 groups stopped before matching; 0 matching observations; matching NOT MEASURED.", "fail"),
        ("Rust", "FAILED", "7,461 verified passes and 2,042 genuine matching differences.", "fail"),
        ("Zig", "FAILED", "3,583 verified passes and 1,764 genuine matching differences.", "fail"),
        ("C++", "FAILED", "128 verified passes, 2,308 matching differences, and five infrastructure failures.", "fail"),
        ("Go", "FAILED", "128 verified passes, 4,518 matching differences, and four infrastructure failures.", "fail"),
        ("Fortran", "NOT READY", "Two independently built engine outputs differed; matching remains NOT MEASURED.", "pending"),
    )
    for index, (name, outcome, detail, category) in enumerate(rows):
        y = 343 + index * 84
        lines.extend((
            f'<rect x="75" y="{y}" width="1510" height="73" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="94" y="{y + 27}" class="name">{xml(name)}</text>',
            f'<text x="1564" y="{y + 27}" class="{category}" text-anchor="end">{xml(outcome)}</text>',
            f'<text x="96" y="{y + 54}" class="body">{xml(detail)}</text>',
        ))
    lines.extend((
        '<text x="77" y="1047" class="body">In 12 groups, a runner ownership check rejected Python-compatible Pattern and Match names before matching.</text>',
        '<text x="77" y="1076" class="body">In the remaining public-types group, the runner could not decode its already saved Python reference_a.</text>',
        '<text x="77" y="1105" class="body">Zero observed comparisons does not mean zero matching differences. The repaired C candidate is not qualified.</text>',
        '<text x="77" y="1134" class="body">The exact original 0755 C binary was restored, including its original inode; no repaired binary remains active.</text>',
        '<text x="77" y="1163" class="body">103 actual repository evidence files = 73 previous + 26 per-group reports and receipts + 4 full-campaign files.</text>',
        '<text x="77" y="1192" class="body">All 108 digest-addressed historical and current evidence references are independently authenticated.</text>',
        '<rect x="54" y="1261" width="1552" height="273" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="76" y="1304" class="heading">2. Is it faster than Python?</text>',
        '<text x="78" y="1336" class="body">NOT MEASURED. There is no trustworthy speed, memory, confidence interval, ranking, or winner.</text>',
        '<text x="78" y="1370" class="body">A reproducible native build is not proof that matching works; the attempted repaired-C retest actually failed.</text>',
        '<text x="78" y="1404" class="body">The planned 4,194,304-case final comparison has not been generated, opened, or timed.</text>',
        '<text x="78" y="1438" class="body">Next: repair both authenticated runner blockers, then rerun every unchanged frozen correctness case.</text>',
        '<text x="78" y="1472" class="body">The previous two identical C builds and all original candidate failures remain preserved.</text>',
        f'<text x="58" y="1583" class="foot">Inputs SHA-256: {xml(manifest_sha)}</text>',
        f'<text x="58" y="1609" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="58" y="1635" class="foot">Recovered C campaign archive SHA-256: {OUTER_ARCHIVE[1]}</text>',
        f'<text x="58" y="1661" class="foot">Recovered C campaign receipt SHA-256: {OUTER_RECEIPT[1]}</text>',
        '</svg>',
        '',
    ))
    return "\n".join(lines).encode("utf-8")


def build(source_sha: str, archive_sha: str,
          receipt_sha: str) -> tuple[dict, dict, tuple[tuple[str, bytes], ...]]:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode
         and sys.executable == PYTHON,
         "use only isolated pinned stable CPython 3.14.6")
    read_owner(SELF, checked_digest(source_sha, "V21 renderer"))
    old_summary, old_snapshot, history = authenticate_previous()
    previous_inputs_raw, _ = read_owner(V20["inputs"][0], V20["inputs"][1])
    previous_inputs = document(previous_inputs_raw, "V20 frozen manifest")
    proof, owners = authenticate_campaign(archive_sha, receipt_sha)
    need(all(path not in history for path in owners),
         "each of 30 campaign owners must be genuinely new to the preserved graph")
    all_references = dict(history)
    all_references.update(owners)
    need(len(history) == 78 and len(owners) == 30
         and len(all_references) == 108,
         "authenticate exactly 78 previous and 30 genuinely new digest references")
    for path, sha in sorted(all_references.items()):
        read_owner(path, sha)
    snap = copy.deepcopy(old_snapshot)
    snap.update({
        "preserved_v20_repository_evidence_owner_count": 73,
        "new_repaired_c_campaign_repository_evidence_owner_count": 30,
        "all_actual_candidate_and_native_evidence_owner_count": 103,
        "preserved_v20_digest_addressed_history_path_count": 78,
        "all_digest_addressed_history_path_count": 108,
        "c_v8_repaired_original_campaign": copy.deepcopy(proof),
        "repaired_c_full_matching_test_status":
            "TEST-RUNNER FAILED; MATCHING NOT MEASURED",
        "repaired_c_actual_verified_matching_case_count": 0,
        "repaired_c_semantic_mismatch_count": "NOT MEASURED",
        "repaired_c_infrastructure_failure_count": 13,
        "repaired_c_completed_suite_count": 13,
        "repaired_c_native_promoted": False,
        "existing_canonical_c_native_target": copy.deepcopy(
            proof["original_canonical_native"],
        ),
    })
    validate_snapshot(snap)
    manifest = {
        "schema": SCHEMA + "-inputs",
        "version": 21,
        "python": "3.14.6",
        "renderer": pin(SELF, source_sha),
        "previous_overview": {
            name: pin(path, sha) for name, (path, sha) in sorted(V20.items())
        },
        "original_correctness_manifest": copy.deepcopy(
            previous_inputs["original_correctness_manifest"],
        ),
        "original_source_freeze": copy.deepcopy(
            previous_inputs["original_source_freeze"],
        ),
        "repaired_c_original_campaign": copy.deepcopy(proof),
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "candidate_families": [
            "python", "rust", "c", "zig", "cpp", "go", "fortran",
        ],
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "candidate_qualified_count": 0,
        "preserved_v20_repository_evidence_owner_count": 73,
        "new_repaired_c_campaign_repository_evidence_owner_count": 30,
        "repository_evidence_owner_count": 103,
        "preserved_v20_digest_addressed_history_path_count": 78,
        "all_digest_addressed_history_path_count": 108,
        "verified_activation_v4_actual_activation_count": 3,
        "verified_activation_v4_current_active_target_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    manifest_raw = canonical(manifest)
    manifest_sha = digest(manifest_raw)
    svg = make_svg(snap, source_sha, manifest_sha)
    families = copy.deepcopy(old_summary["families"])
    for row in families:
        if row.get("family") == "c":
            row["current_repaired_original_campaign"] = copy.deepcopy(proof)
            row["current_repaired_matching_test_status"] = (
                "TEST-RUNNER FAILED; MATCHING NOT MEASURED"
            )
            row["current_repaired_observed_matching_case_count"] = 0
            row["current_repaired_semantic_mismatch_count"] = "NOT MEASURED"
            row["current_repaired_infrastructure_failure_count"] = 13
            row["current_repaired_canonical_native_promoted"] = False
            row["current_repaired_canonical_native_restored"] = True
            row["current_repaired_candidate_activated"] = True
    summary = {
        "schema": SCHEMA + "-summary",
        "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_sha),
        "inputs": pin(OUTPUT + ".inputs.json", manifest_sha),
        "svg": pin(OUTPUT + ".svg", digest(svg)),
        "previous_overview": {
            name: pin(path, sha) for name, (path, sha) in sorted(V20.items())
        },
        "snapshot": snap,
        "families": families,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "repository_evidence_owner_count": 103,
        "authenticated_digest_addressed_history_paths": 108,
        "qualified_candidate_count": 0,
        "verified_activation_v4_current_active_target_count": 0,
        "historical_compiler_process_count_before_v8": 169,
        "actual_v8_compiler_process_count": 14,
        "historical_compiler_process_count_including_v8": 183,
        "c_repaired_build_status": "PASS",
        "c_repaired_matching_test_status":
            "TEST-RUNNER FAILED; MATCHING NOT MEASURED",
        "c_repaired_observed_matching_case_count": 0,
        "c_repaired_semantic_mismatch_count": "NOT MEASURED",
        "c_repaired_infrastructure_failure_count": 13,
        "c_repaired_original_campaign_status": "FAIL",
        "c_repaired_native_promoted": False,
        "existing_canonical_native_present": True,
        "original_canonical_native_restored": True,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    return manifest, snap, (
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
            raise GraphError("source-only graph effect blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "unlink", "remove", "replace", "rename",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "mkdir", "unlink",
                    "rename", "replace", "resolve")),
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

    def __exit__(self, _type: object, _value: object,
                 _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_snapshot() -> dict:
    workers = [{
        "suite": name,
        "case_execution_denominator": denominator,
        "status": "FAIL",
        "failure_class": "INFRASTRUCTURE FAILURE",
        "observed_matching_case_count": 0,
        "semantic_mismatches": "NOT MEASURED",
    } for name, denominator in SUITES]
    return {
        "full_case_denominator": 31237,
        "suite_count": 13,
        "suite_ids": [name for name, _ in SUITES],
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "qualified_candidate_count": 0,
        "verified_activation_v4_actual_activation_count": 3,
        "verified_activation_v4_current_active_target_count": 0,
        "preserved_v20_repository_evidence_owner_count": 73,
        "new_repaired_c_campaign_repository_evidence_owner_count": 30,
        "all_actual_candidate_and_native_evidence_owner_count": 103,
        "preserved_v20_digest_addressed_history_path_count": 78,
        "all_digest_addressed_history_path_count": 108,
        "c_actual_semantic_mismatch_count": 2094,
        "c_verified_passing_case_executions": 7197,
        "rust_actual_semantic_mismatch_count": 2042,
        "rust_verified_passing_case_executions": 7461,
        "zig_actual_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_executions": 3583,
        "c_full_gate": {"gate_status": "FAIL",
                        "actual_semantic_mismatch_count": 2094,
                        "qualified_candidate_count": 0},
        "cpp_full_original_campaign": {"status": "FAIL",
                                        "semantic_mismatch_count": 2308,
                                        "verified_passing_case_count": 128},
        "go_v2_full_original_campaign": {
            "status": "FAIL", "semantic_mismatch_count": 4518,
            "infrastructure_failure_count": 4,
            "verified_passing_case_count": 128, "restoration_status": "PASS",
        },
        "c_v8_repaired_build": {
            "status": "PASS", "phase_count": 2,
            "compiler_process_count": 14,
            "native_sha256": REPAIRED_NATIVE_SHA,
            "complete_native_elf_byte_identical": True,
        },
        "historical_compiler_process_count_before_v8": 169,
        "historical_compiler_process_count_including_v8": 183,
        "c_v8_repaired_original_campaign": {
            "status": "FAIL", "suite_count": 13,
            "completed_suite_count": 13,
            "infrastructure_failure_count": 13,
            "observed_matching_case_count": 0,
            "verified_passing_case_count": 0,
            "semantic_mismatch_count": "NOT MEASURED",
            "failure_causes": {
                "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 12,
                "SAVED PYTHON REFERENCE DECODING": 1,
            },
            "new_repository_evidence_owner_count": 30,
            "qualified": False,
            "suite_results": workers,
        },
        "existing_canonical_c_native_target": {
            "path": ORIGINAL_NATIVE[0], "sha256": ORIGINAL_NATIVE[1],
            "bytes": ORIGINAL_NATIVE[2], "device": 2064, "inode": 430300,
            "mode": 0o755, "present": True, "is_repaired_v8_native": False,
        },
        "repaired_c_full_matching_test_status":
            "TEST-RUNNER FAILED; MATCHING NOT MEASURED",
        "repaired_c_native_promoted": False,
        "repaired_c_actual_verified_matching_case_count": 0,
        "repaired_c_semantic_mismatch_count": "NOT MEASURED",
        "repaired_c_infrastructure_failure_count": 13,
        "repaired_c_completed_suite_count": 13,
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
        rejected = 0

        def reject(changed: dict) -> None:
            nonlocal rejected
            try:
                validate_snapshot(changed)
            except (GraphError, TypeError, KeyError, ValueError):
                rejected += 1
                return
            raise GraphError("source-only synthetic mutation was accepted")

        wrong_top = {
            "full_case_denominator": 31238,
            "suite_count": 12,
            "baseline_passed": 31236,
            "frozen_independent_engine_family_count": 7,
            "current_source_owner_count": 24,
            "current_tested_candidate_family_count": 6,
            "qualified_candidate_count": 1,
            "verified_activation_v4_actual_activation_count": 4,
            "verified_activation_v4_current_active_target_count": 1,
            "preserved_v20_repository_evidence_owner_count": 72,
            "new_repaired_c_campaign_repository_evidence_owner_count": 29,
            "all_actual_candidate_and_native_evidence_owner_count": 104,
            "preserved_v20_digest_addressed_history_path_count": 77,
            "all_digest_addressed_history_path_count": 109,
            "c_actual_semantic_mismatch_count": 0,
            "c_verified_passing_case_executions": 0,
            "rust_actual_semantic_mismatch_count": 0,
            "rust_verified_passing_case_executions": 0,
            "zig_actual_semantic_mismatch_count": 0,
            "zig_verified_passing_case_executions": 0,
            "historical_compiler_process_count_before_v8": 168,
            "historical_compiler_process_count_including_v8": 182,
            "repaired_c_full_matching_test_status": "PASS",
            "repaired_c_native_promoted": True,
            "repaired_c_actual_verified_matching_case_count": 1,
            "repaired_c_semantic_mismatch_count": 0,
            "repaired_c_infrastructure_failure_count": 12,
            "repaired_c_completed_suite_count": 12,
            "performance": "1.5x",
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
        for key, wrong in wrong_top.items():
            altered = copy.deepcopy(base)
            altered[key] = wrong
            reject(altered)
        for parent, wrongs in (
            ("c_full_gate", {"gate_status": "PASS",
                              "actual_semantic_mismatch_count": 0,
                              "qualified_candidate_count": 1}),
            ("cpp_full_original_campaign", {"status": "PASS",
                                             "semantic_mismatch_count": 0,
                                             "verified_passing_case_count": 31237}),
            ("go_v2_full_original_campaign", {"status": "PASS",
                                               "semantic_mismatch_count": 0,
                                               "infrastructure_failure_count": 0,
                                               "verified_passing_case_count": 31237,
                                               "restoration_status": "FAIL"}),
            ("c_v8_repaired_build", {"status": "FAIL", "phase_count": 1,
                                    "compiler_process_count": 13,
                                    "native_sha256": ORIGINAL_NATIVE[1],
                                    "complete_native_elf_byte_identical": False}),
            ("c_v8_repaired_original_campaign", {
                "status": "PASS", "suite_count": 12,
                "completed_suite_count": 12,
                "infrastructure_failure_count": 0,
                "observed_matching_case_count": 1,
                "verified_passing_case_count": 1,
                "semantic_mismatch_count": 0,
                "failure_causes": {
                    "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 13,
                },
                "new_repository_evidence_owner_count": 29,
                "qualified": True,
            }),
            ("existing_canonical_c_native_target", {
                "path": "candidates/not-the-original.so",
                "sha256": REPAIRED_NATIVE_SHA,
                "bytes": 163136, "device": 2049, "inode": 430301,
                "mode": 0o600, "present": False,
                "is_repaired_v8_native": True,
            }),
        ):
            for key, wrong in wrongs.items():
                altered = copy.deepcopy(base)
                altered[parent][key] = wrong
                reject(altered)
        for index in range(13):
            for key, wrong in (("suite", "invented_suite"),
                               ("case_execution_denominator", 0),
                               ("status", "PASS"),
                               ("failure_class", "SEMANTIC MISMATCH"),
                               ("observed_matching_case_count", 1),
                               ("semantic_mismatches", 0)):
                altered = copy.deepcopy(base)
                altered["c_v8_repaired_original_campaign"]["suite_results"][index][key] = wrong
                reject(altered)
        reject({})
        picture = make_svg(base, "a" * 64, "b" * 64)
        for text in (b"RUNNER FAILED", b"NOT MEASURED", b"reference_a",
                     b"103", b"108", b"2,094", b"4,194,304"):
            need(text in picture, "synthetic graph omitted an essential honest headline")
        try:
            os.open("forbidden", os.O_RDONLY)
        except GraphError:
            pass
        else:
            raise GraphError("source-only wall allowed file reads")
        try:
            time.perf_counter()
        except GraphError:
            pass
        else:
            raise GraphError("source-only wall allowed timing")
        need(rejected >= 130 and wall.blocked == 2,
             "incomplete source-only V21 mutation or effects coverage")
        return {
            "schema": SCHEMA + "-self-test",
            "status": "PASS", "version": 21,
            "synthetic_rejected_mutation_count": rejected,
            "blocked_effect_count": wall.blocked,
            "repository_evidence_owner_count": 103,
            "authenticated_digest_addressed_history_paths": 108,
            "repaired_c_suite_count": 13,
            "repaired_c_infrastructure_failure_count": 13,
            "repaired_c_observed_matching_case_count": 0,
            "repaired_c_semantic_mismatch_count": "NOT MEASURED",
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "winner_selected": False,
            "synthetic_svg_sha256": digest(picture),
        }


def publish_output(path: str, raw: bytes, *, verify: bool) -> None:
    parts = checked_path(path)
    need(parts[:2] == ("docs", "evidence"),
         "V21 graph escaped its exclusive evidence output directory")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    try:
        fd = os.open(str(ROOT / path), flags)
    except FileNotFoundError:
        need(not verify, "missing already published reproducible V21 graph")
        fd = os.open(str(ROOT / path),
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | os.O_CLOEXEC | os.O_NOFOLLOW, 0o644)
        try:
            offset = 0
            while offset < len(raw):
                wrote = os.write(fd, raw[offset:])
                need(type(wrote) is int and wrote > 0,
                     "incomplete exclusive V21 graph output")
                offset += wrote
            os.fsync(fd)
        finally:
            os.close(fd)
        read_owner(path, digest(raw), size=len(raw))
        return
    try:
        info = os.fstat(fd)
        need(stat.S_ISREG(info.st_mode) and info.st_size == len(raw),
             "never overwrite a pre-existing independently owned graph")
        pieces: list[bytes] = []
        remaining = info.st_size
        while remaining:
            piece = os.read(fd, min(remaining, 1024 * 1024))
            need(bool(piece), "truncated previously published V21 graph")
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(fd, 1) == b"" and b"".join(pieces) == raw,
             "never replace or edit an independently owned graph")
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-inputs", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--campaign-archive-sha256")
    parser.add_argument("--campaign-receipt-sha256")
    parser.add_argument("--manifest-sha256")
    args = parser.parse_args()
    try:
        if args.self_test:
            need(args.source_sha256 is None
                 and args.campaign_archive_sha256 is None
                 and args.campaign_receipt_sha256 is None
                 and args.manifest_sha256 is None,
                 "synthetic source-only self-tests cannot read genuine owners")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked_digest(args.source_sha256, "V21 renderer")
        archive = checked_digest(args.campaign_archive_sha256,
                                 "recovered campaign archive")
        receipt = checked_digest(args.campaign_receipt_sha256,
                                 "recovered campaign receipt")
        manifest, snapshot, outputs = build(source, archive, receipt)
        manifest_raw = outputs[0][1]
        manifest_sha = digest(manifest_raw)
        if args.emit_inputs:
            need(args.manifest_sha256 is None,
                 "input emission cannot assume an existing graph manifest")
            sys.stdout.buffer.write(manifest_raw)
            return 0
        supplied = checked_digest(args.manifest_sha256, "V21 input manifest")
        need(supplied == manifest_sha,
             "caller must independently pin the exact complete V21 inputs")
        for path, raw in outputs:
            publish_output(path, raw, verify=args.verify)
        validate_snapshot(snapshot)
        result = {
            "schema": SCHEMA + ("-verified" if args.verify else "-rendered"),
            "status": "PASS", "version": 21,
            "source_sha256": source,
            "inputs_sha256": manifest_sha,
            "svg_sha256": digest(outputs[1][1]),
            "summary_sha256": digest(outputs[2][1]),
            "recovered_campaign_archive_sha256": archive,
            "recovered_campaign_receipt_sha256": receipt,
            "repository_evidence_owner_count": 103,
            "authenticated_digest_addressed_history_paths": 108,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "candidate_family_count": 6,
            "qualified_candidate_count": 0,
            "c_repaired_build_status": "PASS",
            "c_repaired_original_campaign_status": "FAIL",
            "c_repaired_matching_test_status":
                "TEST-RUNNER FAILED; MATCHING NOT MEASURED",
            "c_repaired_observed_matching_case_count": 0,
            "c_repaired_semantic_mismatch_count": "NOT MEASURED",
            "c_repaired_infrastructure_failure_count": 13,
            "c_repaired_distinct_infrastructure_cause_count": 2,
            "actual_c_v8_compiler_process_count": 14,
            "existing_canonical_native_present": True,
            "original_canonical_native_restored": True,
            "repaired_c_native_promoted": False,
            "verified_activation_v4_current_active_target_count": 0,
            "outputs_written": not args.verify,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GraphError, OSError, ValueError, TypeError,
            EOFError, gzip.BadGzipFile) as error:
        sys.stderr.write("current V21 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
