#!/usr/bin/env python3
"""Show the genuine corrected Python reference without unblocking candidates."""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import importlib.machinery
import io
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SELF = "tools/render_candidate_current_overview_v38.py"
OUTPUT = "docs/evidence/candidate-current-overview-v38"
SCHEMA = "rebar-candidate-current-overview-v38"
OWNER_LIMIT = 8 * 1024 * 1024
REPORT_LIMIT = 96 * 1024 * 1024
WORKER_STDOUT_LIMIT = 32 * 1024 * 1024
WORKER_STDERR_LIMIT = 2 * 1024 * 1024
LABEL = "cpython-3-14-6-candidate-context-p0"
SOURCE_PIN = (
    "tools/verify_owned_public_type_reference_context_v1.py",
    "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc",
    102474,
)
PROTOCOL_PIN = (
    "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md",
    "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018",
    10691,
)
CONTRACT_PIN = (
    "oracle/phase1/p0-public-type-reference-context-v1.json",
    "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b",
    13965,
)
ARCHIVE_PIN = (
    "oracle/phase1/evidence/"
    "public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0.json.gz",
    "c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05",
    1374913,
)
RECEIPT_PIN = (
    "oracle/phase1/evidence/"
    "public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0"
    "-publication-receipt.json",
    "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966",
    2509,
)
V37 = {
    "source": (
        "tools/render_candidate_current_overview_v37.py",
        "4dcd5c14a63adeb159e11c86802bb4080eea82dec9240afb2f910da7bd39ef07",
        73032,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v37.inputs.json",
        "c89e9c3a2250807e10b27abf33a9e2632344edaefb821a97d317b50944cd398b",
        155848,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v37.json",
        "c2cfbec3fb096b001e7642dee1a7dcc4bdbb4dc7710b5027295b9e1a8340d4ee",
        477696,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v37.svg",
        "db371864df0d2148d49be0f007195ab741b097a8c880505a8297ce383bda7ac8",
        10567,
    ),
}
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
)
STALE_PRODUCER = (
    "tools/run_owned_six_family_original_p0_producer_v3.py",
    "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    195555,
)
FALSIFICATION = (
    "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json",
    "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670",
    3892,
)
MATRIX_SHA = "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
FULL_RECORDS_SHA = "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
CACHE_RECORDS_SHA = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
OLD_CACHE_SHA = "df849727d5aa74cbec19950c2d56764bd592404b76c49abe87418bccd3a5013a"
CACHE_CASE_IDS_SHA = "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
UNCOMPRESSED_SHA = "bc6c0fc9b4e3ff57faecd7e6dda982c1099d170e09dd8ce5641c48872479bebd"
UNCOMPRESSED_BYTES = 73371145
SIGNATURE_VECTOR_SHA = "b32f2ea83213686a8b97d63a15ba5c83d323c2dee1f831bab41176544d6adb0a"
ORACLE_MODULE = "tools.independent_public_type_identity_serialization_v1"
CASE_COUNT = 6912
ORIGINAL_CASE_COUNT = 31237
SUITE_COUNT = 13
PRIVATE_WAIVERS = 13
CACHE_COUNT = 96
ROLES = ("reference-a", "reference-b")
PIDS = (81, 82)
BLOCK_REASON = (
    "The candidate case producer V3/V7/V9 still uses the obsolete "
    "script-context baseline. Freeze, commit, and push corrected V4 "
    "before running any replacement."
)


class GraphError(Exception):
    """Reject invented reference passes, candidate results, or measurements."""


def need(condition: object, explanation: str) -> None:
    if condition is not True:
        raise GraphError(explanation)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only complete independently owned bytes")
    return hashlib.sha256(raw).hexdigest()


def checked(value: object, label: str) -> str:
    need(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require one exact independently supplied SHA-256 for " + label,
    )
    return value


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GraphError("reject noncanonical complete V38 evidence") from error


def document(raw: bytes, label: str, *, exact: bool = True) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        observed: dict[str, object] = {}
        for key, value in pairs:
            need(key not in observed, "reject a duplicate JSON key in " + label)
            observed[key] = value
        return observed

    try:
        result = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("reject nonfinite JSON in " + label)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject incomplete or malformed " + label) from error
    need(
        type(result) is dict and (not exact or canonical(result) == raw),
        "authenticate every canonical byte of " + label,
    )
    return result


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "require the exact isolated stable CPython 3.14.6 baseline",
    )


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(
        type(size) is int and 0 <= size <= OWNER_LIMIT,
        "bound the exact independently owned " + path,
    )
    return {"path": path, "sha256": fingerprint, "bytes": size}


def read_owner(
    path: str, fingerprint: str, size: int, *, private: bool = False
) -> tuple[bytes, dict]:
    need(
        type(path) is str
        and bool(path)
        and not path.startswith("/")
        and "." not in Path(path).parts
        and ".." not in Path(path).parts,
        "reject an escaped, absolute, or substituted evidence owner",
    )
    checked(fingerprint, path)
    need(
        type(size) is int and 0 <= size <= OWNER_LIMIT,
        "reject an unbounded evidence owner: " + path,
    )
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    directories: list[int] = []
    handle: int | None = None
    try:
        directories.append(os.open(str(ROOT), directory_flags))
        for part in Path(path).parts[:-1]:
            directories.append(os.open(part, directory_flags, dir_fd=directories[-1]))
        handle = os.open(Path(path).parts[-1], file_flags, dir_fd=directories[-1])
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and before.st_size == size
            and (not private or stat.S_IMODE(before.st_mode) == 0o600),
            "reject a linked, replaced, nonprivate, or incomplete owner: " + path,
        )
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(handle, min(remaining, 256 * 1024))
            need(bool(piece), "reject a truncated evidence owner: " + path)
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(handle, 1) == b"", "reject extra evidence bytes: " + path)
        raw = b"".join(pieces)
        after = os.fstat(handle)
        need(
            (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_nlink,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_nlink,
                after.st_mtime_ns,
                after.st_ctime_ns,
            )
            and digest(raw) == fingerprint,
            "reject evidence replaced during authentication: " + path,
        )
        return raw, {
            "path": path,
            "sha256": fingerprint,
            "bytes": size,
            "device": after.st_dev,
            "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "nlink": after.st_nlink,
            "uid": after.st_uid,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for directory in reversed(directories):
            os.close(directory)


def authenticate_v37() -> tuple[dict, dict]:
    source_raw, _ = read_owner(*V37["source"])
    previous_renderer = types.ModuleType("_rebar_exact_published_v37_before_reference_fix")
    previous_renderer.__file__ = str(ROOT / V37["source"][0])
    previous_renderer.__package__ = ""
    exec(
        compile(source_raw, previous_renderer.__file__, "exec", dont_inherit=True),
        previous_renderer.__dict__,
    )
    need(
        previous_renderer.SCHEMA == "rebar-candidate-current-overview-v37"
        and previous_renderer.SELF == V37["source"][0],
        "load only the exact immutable previous V37 graph renderer",
    )
    inputs_raw, _ = read_owner(*V37["inputs"], private=True)
    summary_raw, _ = read_owner(*V37["summary"], private=True)
    svg_raw, _ = read_owner(*V37["svg"], private=True)
    inputs = document(inputs_raw, "immutable complete V37 inputs")
    summary = document(summary_raw, "immutable complete V37 summary")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "retain the entire actual previous V37 snapshot")
    previous_renderer.validate(snapshot)
    need(
        summary.get("schema") == previous_renderer.SCHEMA + "-summary"
        and summary.get("version") == 37
        and summary.get("status") == "PASS"
        and svg_raw
        == previous_renderer.make_svg(snapshot, V37["source"][1], V37["inputs"][1])
        and summary.get("full_case_denominator") == ORIGINAL_CASE_COUNT
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("private_waiver_count") == PRIVATE_WAIVERS
        and summary.get("qualified_candidate_count") == 0
        and summary.get("phase_one_reference_gate_status") == "FALSIFIED"
        and summary.get("candidate_facing_self_oracle_status") == "FAIL"
        and summary.get("reference_context_falsifying_case_count") == CACHE_COUNT
        and summary.get("same_context_reference_correction_status") == "NOT RUN"
        and summary.get("all_candidate_matching_blocked") is True
        and summary.get("authenticated_evidence_owner_lower_bound") == 162
        and summary.get("authenticated_history_reference_lower_bound") == 167
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
        and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 1764
        and summary.get("zig_original_campaign_verified_passing_case_count") == 3711
        and summary.get("additional_signature_reference_status") == "PASS"
        and summary.get("additional_signature_reference_cases_executed") == 50
        and summary.get("additional_signature_reference_process_ids") == [81, 82]
        and summary.get("additional_signature_record_vector_sha256")
        == SIGNATURE_VECTOR_SHA
        and summary.get("additional_signature_candidate_status") == "NOT RUN"
        and summary.get("final_comparison_planned_case_count") == 4194304
        and summary.get("final_holdout_opened") is False
        and summary.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("memory") == "NOT MEASURED"
        and inputs.get("authenticated_evidence_owner_lower_bound") == 162
        and inputs.get("authenticated_history_reference_lower_bound") == 167,
        "preserve the actual falsified reference, all genuine losses, and V37",
    )
    return summary, inputs


def authenticate_source_freeze() -> dict:
    goal_raw, goal_owner = read_owner(*GOAL, private=True)
    need(digest(goal_raw) == GOAL[1], "preserve the exact immutable user goal")
    _, source_owner = read_owner(*SOURCE_PIN, private=True)
    _, protocol_owner = read_owner(*PROTOCOL_PIN, private=True)
    contract_raw, contract_owner = read_owner(*CONTRACT_PIN, private=True)
    contract = document(contract_raw, "complete corrected reference source contract")
    source = contract.get("source")
    protocol = contract.get("protocol")
    python = contract.get("python")
    original = contract.get("original_oracle")
    correction = contract.get("prospective_correction")
    boundaries = contract.get("source_only_boundaries")
    need(
        contract.get("schema")
        == "rebar-phase1-owned-public-type-reference-context-v1-frozen-contract"
        and contract.get("version") == 1
        and contract.get("status")
        == "SOURCE FROZEN; CORRECTED TWO-REFERENCE BASELINE NOT RUN"
        and type(source) is dict
        and source.get("path") == SOURCE_PIN[0]
        and source.get("sha256") == SOURCE_PIN[1]
        and type(protocol) is dict
        and protocol.get("path") == PROTOCOL_PIN[0]
        and protocol.get("sha256") == PROTOCOL_PIN[1]
        and type(python) is dict
        and python.get("version") == "3.14.6"
        and python.get("sha256") == PYTHON_SHA
        and type(correction) is dict
        and correction.get("status") == "NOT RUN"
        and correction.get("required_actual_distinct_reference_process_count") == 2
        and correction.get("cases_per_reference_worker") == CASE_COUNT
        and correction.get("preserve_all_96_original_case_ids") is True
        and correction.get("load_any_candidate") is False
        and type(boundaries) is dict
        and boundaries.get("candidate_processes_started") == 0
        and boundaries.get("holdout") == "NOT OPENED",
        "distinguish the pushed source-only freeze from the later real reference",
    )
    if type(original) is dict:
        need(
            original.get("case_execution_denominator", ORIGINAL_CASE_COUNT)
            == ORIGINAL_CASE_COUNT,
            "never change the frozen original correctness denominator",
        )
    return {
        "goal": goal_owner,
        "source": source_owner,
        "protocol": protocol_owner,
        "contract": contract_owner,
        "source_freeze_status": "PASS",
        "source_contract_reference_status": "NOT RUN; FROZEN BEFORE REAL RUN",
    }


def case_ids() -> list[str]:
    return [f"cache-pattern-type-separation/{index:03d}" for index in range(CACHE_COUNT)]


def validate_receipt(receipt: object, archive_owner: dict) -> None:
    need(type(receipt) is dict, "reject a missing real reference receipt")
    need(
        receipt.get("schema")
        == "rebar-phase1-owned-public-type-reference-context-v1-durable-publication-receipt"
        and receipt.get("version") == 1
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("reference_status") == "PASS"
        and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and receipt.get("label") == LABEL
        and receipt.get("source_sha256") == SOURCE_PIN[1]
        and receipt.get("protocol_sha256") == PROTOCOL_PIN[1]
        and receipt.get("contract_sha256") == CONTRACT_PIN[1]
        and receipt.get("matrix_sha256") == MATRIX_SHA
        and receipt.get("public_case_count_per_reference") == CASE_COUNT
        and receipt.get("original_case_execution_denominator") == ORIGINAL_CASE_COUNT
        and receipt.get("attempted_reference_worker_count") == 2
        and receipt.get("actual_reference_worker_count") == 2
        and receipt.get("actual_started_reference_worker_count") == 2
        and receipt.get("completed_reference_worker_count") == 2
        and receipt.get("validated_reference_worker_count") == 2
        and receipt.get("actual_distinct_reference_process_ids") == list(PIDS)
        and receipt.get("full_reference_records_sha256") == FULL_RECORDS_SHA
        and receipt.get("cache_records_sha256") == CACHE_RECORDS_SHA
        and receipt.get("candidate_imports") == 0
        and receipt.get("candidate_workers_started") == 0
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("uncompressed_bytes") == UNCOMPRESSED_BYTES
        and receipt.get("uncompressed_sha256") == UNCOMPRESSED_SHA
        and receipt.get("gzip_mtime") == 0,
        "require real reference PASS separately from durable publication PASS",
    )
    archived = receipt.get("archive")
    need(
        type(archived) is dict
        and archived.get("path") == archive_owner.get("path")
        and archived.get("sha256") == archive_owner.get("sha256")
        and archived.get("bytes") == archive_owner.get("bytes")
        and archived.get("device") == archive_owner.get("device")
        and archived.get("inode") == archive_owner.get("inode")
        and archived.get("mode") == 0o600
        and archived.get("nlink") == 1
        and archived.get("exclusive_creation") is True
        and archived.get("file_fsync_completed") is True
        and archived.get("directory_fsync_completed") is True
        and archived.get("same_inode_readback_verified") is True,
        "bind the receipt to the exact exclusive real reference archive inode",
    )
    journal = receipt.get("private_recovery_journal")
    root = journal.get("root") if type(journal) is dict else None
    latest = journal.get("latest_snapshot") if type(journal) is dict else None
    need(
        type(journal) is dict
        and journal.get("snapshot_count") == 11
        and journal.get("attempted_reference_worker_count") == 2
        and journal.get("actual_started_reference_worker_count") == 2
        and journal.get("completed_reference_worker_count") == 2
        and journal.get("validated_reference_worker_count") == 2
        and type(root) is dict
        and root.get("path")
        == "/tmp/rebar-phase1-public-type-reference-context-v1-" + LABEL
        and root.get("mode") == 0o700
        and type(latest) is dict
        and latest.get("path")
        == root["path"] + "/journal-0010-archive-published.json"
        and latest.get("sha256")
        == "64396ef73f829ab583b18a7da1350f3b65a3be13e1c2cb517c79a67fc013ff86"
        and latest.get("bytes") == 41927968
        and latest.get("mode") == 0o600
        and latest.get("file_fsync_completed") is True
        and latest.get("directory_fsync_completed") is True,
        "retain the exact receipt-declared recovery journal without opening it",
    )


def decode_stream(value: object, limit: int, label: str) -> bytes:
    need(type(value) is dict, "retain the complete real " + label)
    need(
        value.get("complete") is True
        and type(value.get("bytes")) is int
        and 0 <= value["bytes"] <= limit
        and value.get("retained_bytes") == value["bytes"]
        and type(value.get("base64")) is str,
        "reject an omitted, oversized, or truncated real " + label,
    )
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise GraphError("reject malformed complete real " + label) from error
    need(
        len(raw) == value["bytes"] and digest(raw) == value.get("sha256"),
        "authenticate every observed byte of the genuine " + label,
    )
    return raw


def validate_actual_report(report: object, receipt: dict) -> list[dict]:
    need(type(report) is dict, "reject an invented corrected-reference report")
    need(
        report.get("schema")
        == "rebar-phase1-owned-public-type-reference-context-v1-actual-two-reference-report"
        and report.get("version") == 1
        and report.get("status") == "PASS"
        and report.get("label") == LABEL
        and report.get("python") == "3.14.6"
        and report.get("source_sha256") == SOURCE_PIN[1]
        and report.get("protocol_sha256") == PROTOCOL_PIN[1]
        and report.get("contract_sha256") == CONTRACT_PIN[1]
        and report.get("candidate_facing_oracle_module") == ORACLE_MODULE
        and report.get("public_case_count_per_reference") == CASE_COUNT
        and report.get("original_case_execution_denominator") == ORIGINAL_CASE_COUNT
        and report.get("original_suite_count") == SUITE_COUNT
        and report.get("private_waiver_count") == PRIVATE_WAIVERS
        and report.get("matrix_sha256") == MATRIX_SHA
        and report.get("published_seed_decimal") == "6077977430793212465"
        and report.get("cache_case_count") == CACHE_COUNT
        and report.get("cache_case_ids_canonical_sha256") == CACHE_CASE_IDS_SHA
        and report.get("cache_records_sha256") == CACHE_RECORDS_SHA
        and report.get("attempted_reference_worker_count") == 2
        and report.get("actual_reference_worker_count") == 2
        and report.get("actual_started_reference_worker_count") == 2
        and report.get("completed_reference_worker_count") == 2
        and report.get("validated_reference_worker_count") == 2
        and report.get("actual_distinct_reference_process_ids") == list(PIDS)
        and report.get("full_reference_records_sha256") == FULL_RECORDS_SHA
        and report.get("self_oracle_failure_repaired") is True
        and report.get("failure") is None
        and report.get("candidate_imports") == 0
        and report.get("candidate_workers_started") == 0
        and report.get("external_regex_packages_used") == 0
        and report.get("holdout") == "NOT OPENED"
        and report.get("performance") == "NOT MEASURED"
        and report.get("qualified_candidate_count") == 0
        and report.get("winner_selected") is False,
        "require two genuine complete Python results, not a receipt-only PASS",
    )
    for field in (
        "attempted_reference_worker_count",
        "actual_reference_worker_count",
        "actual_started_reference_worker_count",
        "completed_reference_worker_count",
        "validated_reference_worker_count",
        "actual_distinct_reference_process_ids",
        "full_reference_records_sha256",
        "cache_records_sha256",
    ):
        need(report.get(field) == receipt.get(field), "bind actual report and receipt: " + field)

    workers = report.get("complete_reference_workers")
    attempted = report.get("attempted_reference_roles")
    started = report.get("actual_started_reference_processes")
    envelopes = report.get("complete_reference_processes")
    validated = report.get("validated_reference_processes")
    need(
        all(type(group) is list and len(group) == 2 for group in (
            workers, attempted, started, envelopes, validated
        )),
        "retain both real attempted, started, completed, and validated references",
    )
    compact: list[dict] = []
    for index, (role, pid) in enumerate(zip(ROLES, PIDS, strict=True)):
        worker = workers[index]
        attempt = attempted[index]
        start = started[index]
        envelope = envelopes[index]
        validation = validated[index]
        need(
            type(worker) is dict
            and worker.get("schema")
            == "rebar-phase1-owned-public-type-reference-context-v1"
            "-actual-named-context-reference-worker"
            and worker.get("status") == "PASS"
            and worker.get("version") == 1
            and worker.get("role") == role
            and worker.get("pid") == pid
            and worker.get("python") == "3.14.6"
            and worker.get("source_sha256") == SOURCE_PIN[1]
            and worker.get("protocol_sha256") == PROTOCOL_PIN[1]
            and worker.get("contract_sha256") == CONTRACT_PIN[1]
            and worker.get("oracle_module") == ORACLE_MODULE
            and worker.get("matrix_sha256") == MATRIX_SHA
            and worker.get("published_seed_decimal") == "6077977430793212465"
            and worker.get("case_count") == CASE_COUNT
            and worker.get("records_sha256") == FULL_RECORDS_SHA
            and worker.get("cache_case_count") == CACHE_COUNT
            and worker.get("cache_records_sha256") == CACHE_RECORDS_SHA
            and worker.get("candidate_import_count") == 0
            and worker.get("candidate_workers_started") == 0
            and worker.get("external_regex_packages_used") == 0
            and worker.get("holdout") == "NOT OPENED"
            and worker.get("performance") == "NOT MEASURED",
            "authenticate every actual field of real reference " + role,
        )
        records = worker.get("records")
        need(
            type(records) is list
            and len(records) == CASE_COUNT
            and digest(canonical(records)) == FULL_RECORDS_SHA,
            "verify every one of the 6,912 genuine " + role + " observations",
        )
        selected = [
            record
            for record in records
            if type(record) is dict
            and record.get("cohort") == "cache-pattern-type-separation"
        ]
        need(
            len(selected) == CACHE_COUNT
            and [record.get("case") for record in selected] == case_ids()
            and digest(canonical(selected)) == CACHE_RECORDS_SHA,
            "retain all 96 real text-and-bytes reference records in " + role,
        )
        need(
            type(attempt) is dict
            and attempt.get("role") == role
            and type(attempt.get("arguments")) is list
            and attempt["arguments"][:3] == [PYTHON, "-I", "-B"]
            and type(start) is dict
            and start.get("role") == role
            and start.get("pid") == pid
            and type(envelope) is dict
            and envelope.get("role") == role
            and envelope.get("pid") == pid
            and envelope.get("returncode") == 0
            and envelope.get("timed_out") is False
            and type(validation) is dict
            and validation.get("role") == role
            and validation.get("pid") == pid
            and validation.get("records_sha256") == FULL_RECORDS_SHA,
            "bind the genuine attempted, started, complete, and validated " + role,
        )
        stdout = decode_stream(envelope.get("stdout"), WORKER_STDOUT_LIMIT, role + " stdout")
        stderr = decode_stream(envelope.get("stderr"), WORKER_STDERR_LIMIT, role + " stderr")
        need(
            stderr == b"" and stdout == canonical(worker),
            "bind every complete real " + role + " process byte to its observed worker",
        )
        compact.append({
            "role": role,
            "pid": pid,
            "status": "PASS",
            "case_count": CASE_COUNT,
            "cache_case_count": CACHE_COUNT,
            "records_sha256": FULL_RECORDS_SHA,
            "cache_records_sha256": CACHE_RECORDS_SHA,
            "stdout_bytes": len(stdout),
            "stdout_sha256": digest(stdout),
            "stderr_bytes": len(stderr),
            "stderr_sha256": digest(stderr),
            "candidate_import_count": 0,
            "candidate_workers_started": 0,
            "holdout": "NOT OPENED",
        })
        del stdout, stderr
    need(
        workers[0]["records"] == workers[1]["records"]
        and workers[0]["pid"] != workers[1]["pid"],
        "require both distinct real processes to agree on all 6,912 exact cases",
    )
    return compact


def validate_reference_proof(proof: object) -> None:
    need(type(proof) is dict, "reject a missing corrected-reference proof")
    need(
        proof.get("schema") == SCHEMA + "-authenticated-actual-two-reference"
        and proof.get("status") == "PASS"
        and proof.get("reference_status") == "PASS"
        and proof.get("publication_status") == "PASS"
        and proof.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and proof.get("source_sha256") == SOURCE_PIN[1]
        and proof.get("protocol_sha256") == PROTOCOL_PIN[1]
        and proof.get("contract_sha256") == CONTRACT_PIN[1]
        and proof.get("original_case_execution_denominator") == ORIGINAL_CASE_COUNT
        and proof.get("original_suite_count") == SUITE_COUNT
        and proof.get("private_waiver_count") == PRIVATE_WAIVERS
        and proof.get("matrix_sha256") == MATRIX_SHA
        and proof.get("reference_case_count_per_worker") == CASE_COUNT
        and proof.get("total_observed_reference_case_count") == 2 * CASE_COUNT
        and proof.get("attempted_reference_worker_count") == 2
        and proof.get("actual_started_reference_worker_count") == 2
        and proof.get("completed_reference_worker_count") == 2
        and proof.get("validated_reference_worker_count") == 2
        and proof.get("actual_distinct_reference_process_ids") == list(PIDS)
        and proof.get("full_reference_records_sha256") == FULL_RECORDS_SHA
        and proof.get("original_cache_case_count_per_worker") == CACHE_COUNT
        and proof.get("cache_records_sha256") == CACHE_RECORDS_SHA
        and proof.get("historical_falsified_script_context_sha256") == OLD_CACHE_SHA
        and proof.get("compressed_bytes_read") == ARCHIVE_PIN[2]
        and proof.get("archive_inflation_count") == 1
        and proof.get("uncompressed_bytes_read") == UNCOMPRESSED_BYTES
        and proof.get("uncompressed_sha256") == UNCOMPRESSED_SHA
        and proof.get("candidate_matching_archives_opened") == 0
        and proof.get("candidate_imports") == 0
        and proof.get("candidate_workers_started") == 0
        and proof.get("reference_workers_started_by_graph") == 0
        and proof.get("compiler_processes_started_by_graph") == 0
        and proof.get("private_recovery_journal_opened_by_graph") is False
        and proof.get("holdout") == "NOT OPENED"
        and proof.get("performance") == "NOT MEASURED"
        and proof.get("memory") == "NOT MEASURED"
        and proof.get("qualified_candidate_count") == 0
        and proof.get("winner_selected") is False,
        "reject any guessed, incomplete, receipt-only, or candidate-tainted baseline",
    )
    archive = proof.get("archive")
    receipt_owner = proof.get("receipt")
    need(
        type(archive) is dict
        and archive.get("path") == ARCHIVE_PIN[0]
        and archive.get("sha256") == ARCHIVE_PIN[1]
        and archive.get("bytes") == ARCHIVE_PIN[2]
        and archive.get("mode") == "0600"
        and archive.get("nlink") == 1
        and type(archive.get("inode")) is int
        and archive["inode"] > 0
        and type(receipt_owner) is dict
        and receipt_owner.get("path") == RECEIPT_PIN[0]
        and receipt_owner.get("sha256") == RECEIPT_PIN[1]
        and receipt_owner.get("bytes") == RECEIPT_PIN[2]
        and receipt_owner.get("mode") == "0600"
        and receipt_owner.get("nlink") == 1
        and type(receipt_owner.get("inode")) is int
        and receipt_owner["inode"] > 0,
        "authenticate both distinct genuinely private corrected-reference owners",
    )
    receipt = proof.get("complete_publication_receipt")
    validate_receipt(receipt, archive)
    workers = proof.get("complete_worker_observations")
    need(type(workers) is list and len(workers) == 2, "retain both actual worker summaries")
    for index, (role, pid) in enumerate(zip(ROLES, PIDS, strict=True)):
        worker = workers[index]
        need(
            type(worker) is dict
            and worker.get("role") == role
            and worker.get("pid") == pid
            and worker.get("status") == "PASS"
            and worker.get("case_count") == CASE_COUNT
            and worker.get("cache_case_count") == CACHE_COUNT
            and worker.get("records_sha256") == FULL_RECORDS_SHA
            and worker.get("cache_records_sha256") == CACHE_RECORDS_SHA
            and type(worker.get("stdout_bytes")) is int
            and 0 < worker["stdout_bytes"] <= WORKER_STDOUT_LIMIT
            and len(checked(worker.get("stdout_sha256"), role + " real stdout")) == 64
            and worker.get("stderr_bytes") == 0
            and worker.get("stderr_sha256") == digest(b"")
            and worker.get("candidate_import_count") == 0
            and worker.get("candidate_workers_started") == 0
            and worker.get("holdout") == "NOT OPENED",
            "reject a forged, incomplete, or shared-PID actual worker: " + role,
        )
    binding = proof.get("complete_actual_reference_binding_sha256")
    expected = digest(canonical({
        "archive": archive,
        "receipt": receipt_owner,
        "complete_publication_receipt": receipt,
        "complete_worker_observations": workers,
        "uncompressed_bytes": UNCOMPRESSED_BYTES,
        "uncompressed_sha256": UNCOMPRESSED_SHA,
    }))
    need(
        checked(binding, "complete actual two-reference proof") == expected,
        "bind real archive, receipt, workers, and every exact uncompressed byte",
    )


def authenticate_reference(archive_pin: str, receipt_pin: str) -> dict:
    need(
        checked(archive_pin, "actual corrected reference archive") == ARCHIVE_PIN[1]
        and checked(receipt_pin, "actual corrected reference receipt") == RECEIPT_PIN[1],
        "accept only the separately supplied genuine reference evidence pins",
    )
    receipt_raw, receipt_owner = read_owner(*RECEIPT_PIN, private=True)
    compressed, archive_owner = read_owner(*ARCHIVE_PIN, private=True)
    receipt = document(receipt_raw, "complete actual reference publication receipt")
    validate_receipt(receipt, archive_owner)
    need(
        compressed[:2] == b"\x1f\x8b" and compressed[4:8] == b"\0\0\0\0",
        "require the actual deterministic gzip evidence and zero gzip timestamp",
    )
    try:
        inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        raw = inflater.decompress(compressed, REPORT_LIMIT + 1)
        need(
            len(raw) <= REPORT_LIMIT
            and inflater.eof
            and not inflater.unconsumed_tail
            and not inflater.unused_data,
            "reject a truncated, concatenated, oversized, or incomplete reference archive",
        )
        need(inflater.flush() == b"", "reject concealed additional reference bytes")
    except zlib.error as error:
        raise GraphError("reject malformed real corrected-reference compression") from error
    need(
        len(raw) == UNCOMPRESSED_BYTES
        and digest(raw) == UNCOMPRESSED_SHA
        and len(raw) == receipt.get("uncompressed_bytes")
        and digest(raw) == receipt.get("uncompressed_sha256"),
        "authenticate all 73,371,145 real corrected-reference archive bytes",
    )
    report = document(raw, "complete actual two-reference canonical report")
    workers = validate_actual_report(report, receipt)
    proof = {
        "schema": SCHEMA + "-authenticated-actual-two-reference",
        "status": "PASS",
        "reference_status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "source_sha256": SOURCE_PIN[1],
        "protocol_sha256": PROTOCOL_PIN[1],
        "contract_sha256": CONTRACT_PIN[1],
        "archive": archive_owner,
        "receipt": receipt_owner,
        "complete_publication_receipt": copy.deepcopy(receipt),
        "complete_worker_observations": workers,
        "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
        "original_suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVERS,
        "matrix_sha256": MATRIX_SHA,
        "reference_case_count_per_worker": CASE_COUNT,
        "total_observed_reference_case_count": 2 * CASE_COUNT,
        "attempted_reference_worker_count": 2,
        "actual_started_reference_worker_count": 2,
        "completed_reference_worker_count": 2,
        "validated_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": list(PIDS),
        "full_reference_records_sha256": FULL_RECORDS_SHA,
        "original_cache_case_count_per_worker": CACHE_COUNT,
        "cache_records_sha256": CACHE_RECORDS_SHA,
        "historical_falsified_script_context_sha256": OLD_CACHE_SHA,
        "compressed_bytes_read": len(compressed),
        "archive_inflation_count": 1,
        "uncompressed_bytes_read": len(raw),
        "uncompressed_sha256": digest(raw),
        "candidate_matching_archives_opened": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "private_recovery_journal_opened_by_graph": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_actual_reference_binding_sha256"] = digest(canonical({
        "archive": archive_owner,
        "receipt": receipt_owner,
        "complete_publication_receipt": receipt,
        "complete_worker_observations": workers,
        "uncompressed_bytes": len(raw),
        "uncompressed_sha256": digest(raw),
    }))
    validate_reference_proof(proof)
    return proof


def validate_snapshot(snapshot: object) -> None:
    need(type(snapshot) is dict, "reject a missing corrected-reference snapshot")
    need(
        snapshot.get("full_case_denominator") == ORIGINAL_CASE_COUNT
        and snapshot.get("suite_count") == SUITE_COUNT
        and snapshot.get("private_waiver_count") == PRIVATE_WAIVERS
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("preserved_v37_evidence_owner_lower_bound") == 162
        and snapshot.get("preserved_v37_history_reference_lower_bound") == 167
        and snapshot.get("new_corrected_reference_evidence_owner_count") == 2
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 164
        and snapshot.get("authenticated_history_reference_lower_bound") == 169
        and snapshot.get("evidence_owner_count_is_authenticated_lower_bound") is True
        and snapshot.get("history_reference_count_is_authenticated_lower_bound") is True
        and snapshot.get("exact_whole_repository_evidence_owner_count") == "NOT MEASURED"
        and snapshot.get("exact_whole_repository_reference_count") == "NOT MEASURED",
        "preserve 31,237 cases and honest at-least-164/169 evidence bounds",
    )
    for name, mismatches, passes in (
        ("rust_v4_original_campaign", 1036, 8965),
        ("rust_v3_original_campaign", 1087, 7438),
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
        ("zig_v3_original_campaign", 1764, 3711),
    ):
        historical = snapshot.get(name)
        need(
            type(historical) is dict
            and historical.get("status") == "FAIL"
            and historical.get("actual_candidate_workers") == SUITE_COUNT
            and historical.get("completed_suite_count") == SUITE_COUNT
            and historical.get("semantic_mismatch_count") == mismatches
            and historical.get("verified_passing_case_count") == passes
            and historical.get("infrastructure_failure_count") == 0
            and historical.get("candidate_qualified") is False,
            "retain the genuine historical candidate loss: " + name,
        )
    historical_falsification = snapshot.get("reference_context_falsification")
    need(
        type(historical_falsification) is dict
        and historical_falsification.get("status") == "FALSIFIED"
        and historical_falsification.get("falsifying_case_count") == CACHE_COUNT
        and historical_falsification.get("text_subclass_case_count") == 48
        and historical_falsification.get("bytes_subclass_case_count") == 48
        and historical_falsification.get("published_script_context_records_sha256")
        == OLD_CACHE_SHA
        and historical_falsification.get("actual_candidate_facing_reference_records_sha256")
        == CACHE_RECORDS_SHA
        and historical_falsification.get("c_pattern_equality_failure_waived") is False
        and historical_falsification.get("zig_pattern_equality_failure_waived") is False,
        "retain the real previous 96-case falsification and genuine candidate failures",
    )
    actual_reference = snapshot.get("actual_corrected_two_reference")
    validate_reference_proof(actual_reference)
    for field, expected in shared_fields(actual_reference).items():
        need(
            snapshot.get(field) == expected,
            "reject a forged corrected-reference snapshot field: " + field,
        )
    need(
        snapshot.get("phase_one_reference_gate_status") == "PASS"
        and snapshot.get("candidate_facing_self_oracle_status") == "PASS"
        and snapshot.get("same_context_reference_correction_status") == "PASS"
        and snapshot.get("corrected_reference_status") == "PASS"
        and snapshot.get("corrected_reference_publication_status") == "PASS"
        and snapshot.get("corrected_reference_case_count_per_worker") == CASE_COUNT
        and snapshot.get("corrected_reference_total_observed_case_count") == 2 * CASE_COUNT
        and snapshot.get("corrected_reference_actual_worker_count") == 2
        and snapshot.get("corrected_reference_process_ids") == list(PIDS)
        and snapshot.get("corrected_reference_full_records_sha256") == FULL_RECORDS_SHA
        and snapshot.get("corrected_reference_cache_records_sha256") == CACHE_RECORDS_SHA
        and snapshot.get("corrected_reference_cache_cases_per_worker") == CACHE_COUNT
        and snapshot.get("reference_context_falsifying_case_count") == 0
        and snapshot.get("historical_reference_context_falsifying_case_count") == CACHE_COUNT
        and snapshot.get("historical_reference_context_text_case_count") == 48
        and snapshot.get("historical_reference_context_bytes_case_count") == 48
        and snapshot.get("all_candidate_matching_blocked") is True
        and snapshot.get("candidate_matching_block_reason") == BLOCK_REASON
        and snapshot.get("candidate_case_producer_status")
        == "STALE; CORRECTED V4 NOT FROZEN"
        and snapshot.get("candidate_case_producer_corrected_v4_status") == "NOT FROZEN"
        and snapshot.get("candidate_case_producer_source_sha256") == STALE_PRODUCER[1]
        and snapshot.get("additional_private_waivers") == 0
        and snapshot.get("original_cases_removed") == 0
        and snapshot.get("case_denominator_changed") is False
        and snapshot.get("c_pattern_equality_failure_waived") is False
        and snapshot.get("zig_pattern_equality_failure_waived") is False,
        "show a real corrected Python PASS without unblocking stale candidate V3/V7/V9",
    )
    need(
        snapshot.get("rust_v13_source_build_status") == "PASS"
        and snapshot.get("rust_v13_source_build_process_count") == 28
        and snapshot.get("rust_v13_matching_test_status") == "NOT RUN"
        and snapshot.get("rust_v13_candidate_worker_count") == 0
        and snapshot.get("additional_signature_frozen_case_count") == 50
        and snapshot.get("additional_signature_reference_status") == "PASS"
        and snapshot.get("additional_signature_reference_cases_executed") == 50
        and snapshot.get("additional_signature_reference_process_count") == 2
        and snapshot.get("additional_signature_reference_process_ids") == [81, 82]
        and snapshot.get("additional_signature_record_vector_sha256")
        == SIGNATURE_VECTOR_SHA
        and snapshot.get("additional_signature_candidate_status") == "NOT RUN"
        and snapshot.get("additional_signature_candidate_cases_executed") == 0
        and snapshot.get("additional_cases_included_in_original_denominator") is False,
        "preserve separate passing signature references without qualifying a candidate",
    )
    need(
        snapshot.get("reference_archive_gzip_inflation_count") == 1
        and snapshot.get("reference_archive_compressed_bytes_read") == ARCHIVE_PIN[2]
        and snapshot.get("reference_archive_uncompressed_bytes_read") == UNCOMPRESSED_BYTES
        and snapshot.get("reference_archive_uncompressed_sha256") == UNCOMPRESSED_SHA
        and snapshot.get("candidate_matching_archives_opened_by_graph") == 0
        and snapshot.get("matching_archive_gzip_inflation_count") == 0
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_reference_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("canonical_target_reads") == 0
        and snapshot.get("canonical_target_stats") == 0
        and snapshot.get("hidden_cases_read") == 0
        and snapshot.get("performance_files_read") == 0
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("production_runtime_delegation_audit") == "NOT ESTABLISHED"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "report exactly one real reference-archive inflation; touch no candidate or holdout",
    )


def xml(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate_snapshot(snapshot)
    checked(source, "actual V38 renderer")
    checked(inputs, "actual V38 graph inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1930" '
        'viewBox="0 0 1440 1930" role="img" '
        'aria-labelledby="v38-title v38-description">',
        '<title id="v38-title">Building a faster Python re: corrected Python '
        'baseline passes; replacement tests remain blocked</title>',
        '<desc id="v38-description">Two real isolated Python 3.14.6 processes '
        'independently passed the same complete 6,912 original reference cases, '
        'including all 96 previously misidentified text and bytes cases. The '
        'original denominator remains 31,237 cases in 13 suites. Rust, C, and '
        'Zig have preserved historical failures; Go, C++, and Fortran have not '
        'been retested. All six replacement families remain blocked because '
        'their V3/V7/V9 producer still uses the old baseline and corrected V4 '
        'is not frozen. No replacement is qualified, speed and memory are not '
        'measured, and the 4,194,304-case final holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        '"Segoe UI",sans-serif}.title{font-size:27px;font-weight:760;fill:'
        '#16324f}.heading{font-size:19px;font-weight:750;fill:#16324f}'
        '.body{font-size:14px;fill:#42556c}.name{font-size:14px;font-weight:'
        '720;fill:#16324f}.good{font-size:18px;font-weight:780;fill:#087a4b}'
        '.goodbody{font-size:14px;fill:#1d644b}.warning{font-size:16px;'
        'font-weight:760;fill:#905500}.warnbody{font-size:13px;fill:#74511e}'
        '.pass{font-size:12px;font-weight:760;fill:#087a4b}.fail{font-size:'
        '12px;font-weight:750;fill:#a75c13}.pending{font-size:12px;'
        'font-weight:740;fill:#53667b}.big{font-size:20px;font-weight:760;'
        'fill:#16324f}.small{font-size:11px;fill:#42556c}.foot{font-size:'
        '10px;fill:#53667b}</style>',
        '<rect width="1440" height="1930" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="54" class="title">Can we build a faster '
        'replacement for Python re?</text>',
        '<text x="46" y="81" class="body">Python now agrees with itself. '
        'Replacement testing still needs the corrected test runner.</text>',
        '<rect x="44" y="100" width="1352" height="91" rx="14" '
        'fill="#effaf4" stroke="#a9dbbd"/>',
        '<text x="65" y="136" class="good">PYTHON BASELINE FIXED AND '
        'VERIFIED — 2 INDEPENDENT PROCESSES PASS</text>',
        '<text x="67" y="166" class="goodbody">Each real Python process '
        'passed all 6,912 original cases, including all 96 previously '
        'misidentified text and byte cases.</text>',
        '<rect x="44" y="204" width="1352" height="86" rx="14" '
        'fill="#fff8e9" stroke="#ead5a3"/>',
        '<text x="65" y="238" class="warning">ALL REPLACEMENT RUNS '
        'REMAIN BLOCKED — CORRECTED V4 TEST RUNNER NOT FROZEN</text>',
        '<text x="67" y="265" class="warnbody">The existing V3/V7/V9 '
        'candidate producer still points to the old baseline. No replacement '
        'has been rerun or qualified.</text>',
    ]
    cards = (
        ("31,237", "unchanged original cases"),
        ("2 × 6,912", "real Python observations"),
        ("96 / 96", "old reference cases fixed"),
        ("6", "replacement families"),
        ("0", "qualified replacements"),
        ("0", "new replacement runs"),
        ("≥164 / 169", "authenticated lower bounds"),
    )
    for index, (number, label) in enumerate(cards):
        left = 44 + 195 * index
        lines.extend((
            f'<rect x="{left}" y="307" width="184" height="82" '
            'rx="11" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{left + 9}" y="340" class="big">{xml(number)}</text>',
            f'<text x="{left + 9}" y="365" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="407" width="1352" height="515" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="442" class="heading">1. Overall: the baseline '
        'passes; every replacement still waits</text>',
        '<text x="66" y="468" class="body">Historical replacement '
        'results are kept visible. They are not results against the newly '
        'corrected baseline.</text>',
    ))
    rows = (
        (
            "Python baseline — same context as replacements",
            "PASS — TWO REAL PROCESSES",
            0,
            "6,912 of 6,912 checks passed in each real process",
            "pass",
        ),
        (
            "Rust — previously tested version",
            "HISTORICAL FAILURE; NEW RUN BLOCKED",
            1036,
            "1,036 historical differences; 8,965 historical passes",
            "fail",
        ),
        (
            "C — previously tested version",
            "HISTORICAL FAILURE; NEW RUN BLOCKED",
            1230,
            "1,230 historical differences; 7,325 historical passes",
            "fail",
        ),
        (
            "Zig — previously tested version",
            "HISTORICAL FAILURE; NEW RUN BLOCKED",
            1764,
            "1,764 historical differences; 3,711 historical passes",
            "fail",
        ),
        (
            "Go — first-party replacement family",
            "NOT RUN; BLOCKED",
            None,
            "No current correctness result and no speed measurement",
            "pending",
        ),
        (
            "C++ — first-party replacement family",
            "NOT RUN; BLOCKED",
            None,
            "No current correctness result and no speed measurement",
            "pending",
        ),
        (
            "Fortran — first-party replacement family",
            "NOT RUN; BLOCKED",
            None,
            "No current correctness result and no speed measurement",
            "pending",
        ),
    )
    for index, (name, state, differences, detail, kind) in enumerate(rows):
        top = 493 + 56 * index
        lines.extend((
            f'<text x="67" y="{top + 14}" class="name">{xml(name)}</text>',
            f'<text x="1367" y="{top + 14}" class="{kind}" '
            f'text-anchor="end">{xml(state)}</text>',
            f'<rect x="68" y="{top + 25}" width="485" height="9" '
            'rx="4" fill="#edf1f5"/>',
        ))
        if differences is not None:
            width = 485 if differences == 0 else round(485 * differences / 1764)
            color = "#168653" if differences == 0 else "#b77a36"
            lines.append(
                f'<rect x="68" y="{top + 25}" width="{width}" '
                f'height="9" rx="4" fill="{color}"/>'
            )
        lines.append(
            f'<text x="569" y="{top + 34}" class="small">'
            f'{xml(detail)}</text>'
        )
    lines.extend((
        '<rect x="44" y="941" width="1352" height="264" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="976" class="heading">2. What the corrected '
        'Python reference actually proves</text>',
    ))
    findings = (
        "Two separately launched, isolated CPython 3.14.6 workers, process IDs 81 and 82, both passed.",
        "Each independently evaluated every one of the same 6,912 original public-behavior cases.",
        "Both complete result vectors agree, giving 13,824 observed reference operations.",
        "All 96 original text-and-bytes subclass cases are retained and now agree in the candidate-facing context.",
        "The earlier 96-case reference failure remains preserved; no case was removed or waived.",
        "The complete real archive and its separate durable receipt both independently report PASS.",
        "The other 50 Python signature checks remain separate; they are not added to the 31,237-case total.",
    )
    for index, line in enumerate(findings):
        lines.append(
            f'<text x="67" y="{1006 + 26 * index}" class="body">'
            f'{xml(line)}</text>'
        )
    lines.extend((
        '<rect x="44" y="1224" width="1352" height="274" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1259" class="heading">3. What remains '
        'blocked or unmeasured</text>',
    ))
    remaining = (
        (
            "Replacement test runner",
            "BLOCKED: V3/V7/V9 still uses the old reference; corrected V4 is NOT FROZEN.",
        ),
        (
            "Rust, C, Zig, Go, C++, Fortran",
            "BLOCKED: no candidate may run until corrected V4 is frozen, committed, and pushed.",
        ),
        (
            "Compatibility-qualified replacements",
            "NONE: a corrected Python baseline is not a passing replacement.",
        ),
        (
            "Runtime independence",
            "NOT ESTABLISHED; first-party source and builds are not a runtime audit.",
        ),
        (
            "Speed, memory, and confidence",
            "NOT MEASURED; no honest replacement benchmark has been started.",
        ),
        (
            "4,194,304-case final holdout",
            "NOT OPENED and NOT GENERATED; no hidden case has been accessed.",
        ),
        (
            "Winning faster replacement",
            "NONE: prove complete compatibility before measuring or selecting a winner.",
        ),
    )
    for index, (name, detail) in enumerate(remaining):
        top = 1292 + 28 * index
        lines.extend((
            f'<text x="67" y="{top}" class="name">{xml(name)}</text>',
            f'<text x="370" y="{top}" class="body">{xml(detail)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1517" width="1352" height="230" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1552" class="heading">4. Independently '
        'reproducible evidence</text>',
    ))
    notes = (
        "Replay and preserve the complete immutable V37 graph, including the actual old 96-case falsification.",
        "Authenticate the separately pushed corrected source contract and both exact actual reference owners.",
        "Inflate exactly the one new 1,374,913-byte reference archive and verify all 73,371,145 result bytes.",
        "Independently authenticate both distinct real worker IDs, all 13,824 observations, and both 96-case vectors.",
        "Preserve every historical Rust, C, and Zig failure and the genuine C subclass-equality mismatch.",
        "Two genuine new evidence owners raise authenticated lower bounds from 162/167 to at least 164/169.",
    )
    for index, line in enumerate(notes):
        lines.append(
            f'<text x="67" y="{1581 + 23 * index}" class="body">'
            f'{xml(line)}</text>'
        )
    lines.extend((
        f'<text x="47" y="1777" class="foot">Graph inputs SHA-256: '
        f'{xml(inputs)}</text>',
        f'<text x="47" y="1799" class="foot">Graph renderer SHA-256: '
        f'{xml(source)}</text>',
        f'<text x="47" y="1821" class="foot">Actual corrected reference '
        f'archive SHA-256: {xml(ARCHIVE_PIN[1])}</text>',
        f'<text x="47" y="1843" class="foot">Actual corrected reference '
        f'receipt SHA-256: {xml(RECEIPT_PIN[1])}</text>',
        f'<text x="47" y="1865" class="foot">Both complete Python '
        f'result vectors SHA-256: {xml(FULL_RECORDS_SHA)}</text>',
        f'<text x="47" y="1887" class="foot">All 96 retained corrected '
        f'cases SHA-256: {xml(CACHE_RECORDS_SHA)}</text>',
        "</svg>",
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def shared_fields(proof: dict) -> dict:
    return {
        "preserved_v37_evidence_owner_lower_bound": 162,
        "preserved_v37_history_reference_lower_bound": 167,
        "new_corrected_reference_evidence_owner_count": 2,
        "repository_evidence_owner_count": 164,
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "phase_one_reference_gate_status": "PASS",
        "candidate_facing_self_oracle_status": "PASS",
        "same_context_reference_correction_status": "PASS",
        "corrected_reference_status": "PASS",
        "corrected_reference_publication_status": "PASS",
        "corrected_reference_case_count_per_worker": CASE_COUNT,
        "corrected_reference_total_observed_case_count": 2 * CASE_COUNT,
        "corrected_reference_actual_worker_count": 2,
        "corrected_reference_process_ids": list(PIDS),
        "corrected_reference_full_records_sha256": FULL_RECORDS_SHA,
        "corrected_reference_cache_records_sha256": CACHE_RECORDS_SHA,
        "corrected_reference_cache_cases_per_worker": CACHE_COUNT,
        "reference_context_falsifying_case_count": 0,
        "historical_reference_context_falsifying_case_count": CACHE_COUNT,
        "historical_reference_context_text_case_count": 48,
        "historical_reference_context_bytes_case_count": 48,
        "published_script_context_records_sha256": OLD_CACHE_SHA,
        "actual_candidate_facing_reference_records_sha256": CACHE_RECORDS_SHA,
        "all_candidate_matching_blocked": True,
        "candidate_matching_block_reason": BLOCK_REASON,
        "candidate_case_producer_status": "STALE; CORRECTED V4 NOT FROZEN",
        "candidate_case_producer_corrected_v4_status": "NOT FROZEN",
        "candidate_case_producer_source_sha256": STALE_PRODUCER[1],
        "additional_private_waivers": 0,
        "original_cases_removed": 0,
        "case_denominator_changed": False,
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_compressed_bytes_read": ARCHIVE_PIN[2],
        "reference_archive_uncompressed_bytes_read": UNCOMPRESSED_BYTES,
        "reference_archive_uncompressed_sha256": UNCOMPRESSED_SHA,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "hidden_cases_read": 0,
        "performance_files_read": 0,
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
        "actual_corrected_two_reference": copy.deepcopy(proof),
    }


def build(
    source_sha: str, source_bytes: int, archive_sha: str, receipt_sha: str
) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_sha = checked(source_sha, "actual V38 graph renderer")
    need(
        type(source_bytes) is int and 0 < source_bytes <= OWNER_LIMIT,
        "require the exact independently supplied V38 source size",
    )
    own_raw, _ = read_owner(SELF, source_sha, source_bytes)
    previous, old_inputs = authenticate_v37()
    frozen = authenticate_source_freeze()
    _, stale_owner = read_owner(*STALE_PRODUCER, private=True)
    _, falsification_owner = read_owner(*FALSIFICATION, private=True)
    proof = authenticate_reference(archive_sha, receipt_sha)
    shared = shared_fields(proof)
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update(shared)
    snapshot.update({
        "full_case_denominator": ORIGINAL_CASE_COUNT,
        "suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVERS,
        "qualified_candidate_count": 0,
    })
    validate_snapshot(snapshot)
    earlier = {name: pin(*value) for name, value in V37.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 38,
        "python": "3.14.6",
        "renderer": pin(SELF, source_sha, len(own_raw)),
        "previous_overview": earlier,
        "corrected_reference_source_freeze": frozen,
        "actual_corrected_reference_archive": proof["archive"],
        "actual_corrected_reference_receipt": proof["receipt"],
        "preserved_actual_reference_falsification": falsification_owner,
        "stale_original_candidate_producer": stale_owner,
        "all_digest_addressed_history_path_count": 169,
        "candidate_qualified_count": 0,
        **shared,
    })
    inputs_raw = canonical(inputs)
    svg = make_svg(snapshot, source_sha, digest(inputs_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") != "python":
            family["matching_paused_for_reference_falsification"] = False
            family["matching_blocked_pending_corrected_v4_producer"] = True
            family["matching_block_reason"] = BLOCK_REASON
            family["candidate_run_under_corrected_reference"] = "NOT RUN"
            family["qualified"] = False
        if family.get("family") == "rust":
            family["v13_matching_test_status"] = "NOT RUN"
            family["v13_candidate_worker_count"] = 0
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 38,
        "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_sha, len(own_raw)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(inputs_raw), len(inputs_raw)),
        "svg": pin(OUTPUT + ".svg", digest(svg), len(svg)),
        "previous_overview": earlier,
        "snapshot": snapshot,
        "families": families,
        "corrected_reference_source_freeze": frozen,
        "preserved_actual_reference_falsification": falsification_owner,
        "stale_original_candidate_producer": stale_owner,
        "authenticated_digest_addressed_history_paths": 169,
        "qualified_candidate_count": 0,
        **shared,
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", inputs_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


class SourceOnlyWall:
    """Physically prevent source-only tests from doing real outside work."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = {
            kind: 0
            for kind in (
                "filesystem",
                "write",
                "process",
                "import",
                "native",
                "network",
                "thread",
                "clock",
                "lock",
                "signal",
                "decompression",
            )
        }

    def deny(self, owner: object, name: str, kind: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: object, **_kwargs: object) -> object:
            self.blocked[kind] += 1
            raise GraphError("physically blocked V38 source-only " + kind + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyWall:
        actions: list[tuple[object, tuple[str, ...], str]] = [
            (builtins, ("open",), "filesystem"),
            (builtins, ("__import__",), "import"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir", "listdir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "resolve"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename", "replace", "fsync", "symlink", "link"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename", "replace", "touch"), "write"),
            (tempfile, ("mkdtemp", "mkstemp", "TemporaryFile", "NamedTemporaryFile"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output", "_fork_exec"), "process"),
            (os, ("fork", "system", "posix_spawn", "posix_spawnp", "execv", "execve", "execl", "execle", "execlp", "execlpe", "execvp", "execvpe", "spawnv", "spawnve", "spawnvp", "spawnvpe"), "process"),
            (importlib, ("import_module",), "import"),
            (importlib.machinery.SourceFileLoader, ("create_module", "exec_module", "load_module"), "import"),
            (importlib.machinery.SourcelessFileLoader, ("create_module", "exec_module", "load_module"), "import"),
            (importlib.machinery.ExtensionFileLoader, ("create_module", "exec_module", "load_module"), "native"),
            (importlib.machinery.BuiltinImporter, ("create_module", "exec_module", "load_module"), "native"),
            (importlib.machinery.FrozenImporter, ("create_module", "exec_module", "load_module"), "import"),
            (ctypes, ("CDLL", "PyDLL", "_dlopen"), "native"),
            (socket, ("socket", "create_connection", "getaddrinfo"), "network"),
            (threading, ("_start_joinable_thread", "_start_new_thread"), "thread"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "process_time", "thread_time", "sleep"), "clock"),
            (fcntl, ("flock", "lockf"), "lock"),
            (signal, ("signal", "raise_signal", "pthread_sigmask"), "signal"),
            (gzip, ("open", "decompress", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        ]
        for module_name, names, kind in (
            ("_io", ("open",), "filesystem"),
            ("posix", ("open", "read", "stat", "lstat", "scandir", "listdir"), "filesystem"),
            ("posix", ("write", "mkdir", "unlink", "remove", "rename", "replace", "fsync", "symlink", "link"), "write"),
            ("posix", ("fork", "posix_spawn", "posix_spawnp", "execv", "execve", "spawnv", "spawnve"), "process"),
            ("_posixsubprocess", ("fork_exec",), "process"),
            ("_ctypes", ("dlopen",), "native"),
            ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin", "exec_builtin", "init_frozen"), "native"),
            ("_socket", ("socket", "getaddrinfo"), "network"),
            ("_thread", ("start_new_thread", "start_joinable_thread"), "thread"),
        ):
            module = sys.modules.get(module_name)
            if module is not None:
                actions.append((module, names, kind))
        for owner, names, kind in actions:
            for name in names:
                self.deny(owner, name, kind)
        return self

    def __exit__(self, *_errors: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_owner(item: tuple[str, str, int], inode: int) -> dict:
    return {
        "path": item[0],
        "sha256": item[1],
        "bytes": item[2],
        "device": 2064,
        "inode": inode,
        "mode": "0600",
        "nlink": 1,
        "uid": os.geteuid(),
    }


def synthetic_receipt(archive: dict) -> dict:
    latest = {
        "path": "/tmp/rebar-phase1-public-type-reference-context-v1-"
        + LABEL
        + "/journal-0010-archive-published.json",
        "sha256": "64396ef73f829ab583b18a7da1350f3b65a3be13e1c2cb517c79a67fc013ff86",
        "bytes": 41927968,
        "mode": 0o600,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
    }
    return {
        "schema": "rebar-phase1-owned-public-type-reference-context-v1"
        "-durable-publication-receipt",
        "version": 1,
        "status": "PASS",
        "publication_status": "PASS",
        "reference_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "label": LABEL,
        "source_sha256": SOURCE_PIN[1],
        "protocol_sha256": PROTOCOL_PIN[1],
        "contract_sha256": CONTRACT_PIN[1],
        "matrix_sha256": MATRIX_SHA,
        "public_case_count_per_reference": CASE_COUNT,
        "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
        "attempted_reference_worker_count": 2,
        "actual_reference_worker_count": 2,
        "actual_started_reference_worker_count": 2,
        "completed_reference_worker_count": 2,
        "validated_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": list(PIDS),
        "full_reference_records_sha256": FULL_RECORDS_SHA,
        "cache_records_sha256": CACHE_RECORDS_SHA,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "uncompressed_bytes": UNCOMPRESSED_BYTES,
        "uncompressed_sha256": UNCOMPRESSED_SHA,
        "gzip_mtime": 0,
        "archive": {
            "path": archive["path"],
            "sha256": archive["sha256"],
            "bytes": archive["bytes"],
            "device": archive["device"],
            "inode": archive["inode"],
            "mode": 0o600,
            "nlink": 1,
            "exclusive_creation": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "same_inode_readback_verified": True,
        },
        "private_recovery_journal": {
            "snapshot_count": 11,
            "attempted_reference_worker_count": 2,
            "actual_started_reference_worker_count": 2,
            "completed_reference_worker_count": 2,
            "validated_reference_worker_count": 2,
            "root": {
                "path": "/tmp/rebar-phase1-public-type-reference-context-v1-" + LABEL,
                "mode": 0o700,
            },
            "latest_snapshot": latest,
        },
    }


def synthetic_reference() -> dict:
    archive = synthetic_owner(ARCHIVE_PIN, 524768)
    receipt_owner = synthetic_owner(RECEIPT_PIN, 524769)
    receipt = synthetic_receipt(archive)
    workers = [
        {
            "role": role,
            "pid": pid,
            "status": "PASS",
            "case_count": CASE_COUNT,
            "cache_case_count": CACHE_COUNT,
            "records_sha256": FULL_RECORDS_SHA,
            "cache_records_sha256": CACHE_RECORDS_SHA,
            "stdout_bytes": 1024 + index,
            "stdout_sha256": digest(("synthetic-" + role).encode("ascii")),
            "stderr_bytes": 0,
            "stderr_sha256": digest(b""),
            "candidate_import_count": 0,
            "candidate_workers_started": 0,
            "holdout": "NOT OPENED",
        }
        for index, (role, pid) in enumerate(zip(ROLES, PIDS, strict=True))
    ]
    proof = {
        "schema": SCHEMA + "-authenticated-actual-two-reference",
        "status": "PASS",
        "reference_status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "source_sha256": SOURCE_PIN[1],
        "protocol_sha256": PROTOCOL_PIN[1],
        "contract_sha256": CONTRACT_PIN[1],
        "archive": archive,
        "receipt": receipt_owner,
        "complete_publication_receipt": receipt,
        "complete_worker_observations": workers,
        "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
        "original_suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVERS,
        "matrix_sha256": MATRIX_SHA,
        "reference_case_count_per_worker": CASE_COUNT,
        "total_observed_reference_case_count": 2 * CASE_COUNT,
        "attempted_reference_worker_count": 2,
        "actual_started_reference_worker_count": 2,
        "completed_reference_worker_count": 2,
        "validated_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": list(PIDS),
        "full_reference_records_sha256": FULL_RECORDS_SHA,
        "original_cache_case_count_per_worker": CACHE_COUNT,
        "cache_records_sha256": CACHE_RECORDS_SHA,
        "historical_falsified_script_context_sha256": OLD_CACHE_SHA,
        "compressed_bytes_read": ARCHIVE_PIN[2],
        "archive_inflation_count": 1,
        "uncompressed_bytes_read": UNCOMPRESSED_BYTES,
        "uncompressed_sha256": UNCOMPRESSED_SHA,
        "candidate_matching_archives_opened": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "private_recovery_journal_opened_by_graph": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_actual_reference_binding_sha256"] = digest(canonical({
        "archive": archive,
        "receipt": receipt_owner,
        "complete_publication_receipt": receipt,
        "complete_worker_observations": workers,
        "uncompressed_bytes": UNCOMPRESSED_BYTES,
        "uncompressed_sha256": UNCOMPRESSED_SHA,
    }))
    validate_reference_proof(proof)
    return proof


def historical(mismatches: int, passes: int) -> dict:
    return {
        "status": "FAIL",
        "actual_candidate_workers": SUITE_COUNT,
        "completed_suite_count": SUITE_COUNT,
        "semantic_mismatch_count": mismatches,
        "verified_passing_case_count": passes,
        "infrastructure_failure_count": 0,
        "candidate_qualified": False,
    }


def synthetic_snapshot() -> dict:
    proof = synthetic_reference()
    snapshot = {
        "full_case_denominator": ORIGINAL_CASE_COUNT,
        "suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVERS,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "rust_v4_original_campaign": historical(1036, 8965),
        "rust_v3_original_campaign": historical(1087, 7438),
        "c_v4_original_campaign": historical(1230, 7325),
        "zig_v2_original_campaign": historical(2172, 2847),
        "zig_v3_original_campaign": historical(1764, 3711),
        "reference_context_falsification": {
            "status": "FALSIFIED",
            "falsifying_case_count": CACHE_COUNT,
            "text_subclass_case_count": 48,
            "bytes_subclass_case_count": 48,
            "published_script_context_records_sha256": OLD_CACHE_SHA,
            "actual_candidate_facing_reference_records_sha256": CACHE_RECORDS_SHA,
            "c_pattern_equality_failure_waived": False,
            "zig_pattern_equality_failure_waived": False,
        },
        "rust_v13_source_build_status": "PASS",
        "rust_v13_source_build_process_count": 28,
        "rust_v13_matching_test_status": "NOT RUN",
        "rust_v13_candidate_worker_count": 0,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_record_vector_sha256": SIGNATURE_VECTOR_SHA,
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        **shared_fields(proof),
    }
    validate_snapshot(snapshot)
    return snapshot


def forged(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        if value == "PASS":
            return "FAIL"
        if value == "FAIL":
            return "PASS"
        if value in ("NOT RUN", "NOT FROZEN", "NOT MEASURED", "NOT ESTABLISHED"):
            return "VERIFIED"
        return value + "-forged"
    if type(value) is dict:
        return {}
    if type(value) is list:
        return value[:-1]
    return "forged"


def self_test() -> dict:
    runtime()
    with SourceOnlyWall() as wall:
        fixture = synthetic_snapshot()
        validate_snapshot(fixture)
        rejected = 0

        def reject(candidate: dict, label: str) -> None:
            nonlocal rejected
            try:
                validate_snapshot(candidate)
            except (GraphError, TypeError, ValueError, KeyError, AttributeError):
                rejected += 1
                return
            raise GraphError("accepted a forged V38 corrected-reference claim: " + label)

        nested = {
            "rust_v4_original_campaign",
            "rust_v3_original_campaign",
            "c_v4_original_campaign",
            "zig_v2_original_campaign",
            "zig_v3_original_campaign",
            "reference_context_falsification",
            "actual_corrected_two_reference",
        }
        for key, value in fixture.items():
            if key not in nested:
                changed = copy.deepcopy(fixture)
                changed[key] = forged(value)
                reject(changed, "snapshot-" + key)
        for name in nested:
            for key, value in fixture[name].items():
                changed = copy.deepcopy(fixture)
                changed[name][key] = forged(value)
                reject(changed, name + "-" + key)
        proof = fixture["actual_corrected_two_reference"]
        for group in ("archive", "receipt", "complete_publication_receipt"):
            for key, value in proof[group].items():
                changed = copy.deepcopy(fixture)
                changed["actual_corrected_two_reference"][group][key] = forged(value)
                reject(changed, group + "-" + key)
        actual_receipt = proof["complete_publication_receipt"]
        for group in ("archive", "private_recovery_journal"):
            for key, value in actual_receipt[group].items():
                changed = copy.deepcopy(fixture)
                changed["actual_corrected_two_reference"]["complete_publication_receipt"]\
                    [group][key] = forged(value)
                reject(changed, "receipt-" + group + "-" + key)
        for group in ("root", "latest_snapshot"):
            for key, value in actual_receipt["private_recovery_journal"][group].items():
                changed = copy.deepcopy(fixture)
                changed["actual_corrected_two_reference"]["complete_publication_receipt"]\
                    ["private_recovery_journal"][group][key] = forged(value)
                reject(changed, "journal-" + group + "-" + key)
        for index, observed in enumerate(proof["complete_worker_observations"]):
            for key, value in observed.items():
                changed = copy.deepcopy(fixture)
                changed["actual_corrected_two_reference"]\
                    ["complete_worker_observations"][index][key] = forged(value)
                reject(changed, "real-worker-" + str(index) + "-" + key)

        image = make_svg(fixture, "a" * 64, "b" * 64)
        for phrase in (
            b"PYTHON BASELINE FIXED AND VERIFIED",
            b"2 INDEPENDENT PROCESSES PASS",
            b"ALL REPLACEMENT RUNS REMAIN BLOCKED",
            b"V3/V7/V9",
            b"V4",
            b"NOT FROZEN",
            b"31,237",
            "2 × 6,912".encode("utf-8"),
            b"13,824",
            b"96 / 96",
            b"Rust",
            b"1,036",
            b"8,965",
            b"1,230",
            b"7,325",
            b"Zig",
            b"1,764",
            b"3,711",
            b"Go",
            b"C++",
            b"Fortran",
            b"HISTORICAL",
            b"0",
            b"NOT RUN",
            b"NOT ESTABLISHED",
            b"NOT MEASURED",
            b"4,194,304",
            b"NOT OPENED",
            b"NOT GENERATED",
            b"164 / 169",
            b"73,371,145",
        ):
            need(
                phrase.lower() in image.lower(),
                "reject an omitted or misleading visible V38 fact: " + repr(phrase),
            )

        probes: list[tuple[str, object]] = [
            ("filesystem", lambda: builtins.open("forbidden-v38")),
            ("filesystem", lambda: os.open("forbidden-v38", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v38")),
            ("write", lambda: os.mkdir("forbidden-v38")),
            ("process", lambda: subprocess.run(("forbidden-v38",))),
            ("process", lambda: subprocess.Popen(("forbidden-v38",))),
            ("process", lambda: os.execv("/forbidden-v38", [])),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("import", lambda: builtins.__import__("candidates.rust_candidate")),
            ("native", lambda: ctypes.CDLL("forbidden-v38.so")),
            ("native", lambda: ctypes.PyDLL("forbidden-v38.so")),
            ("native", lambda: importlib.machinery.ExtensionFileLoader.create_module(None, None)),
            ("native", lambda: importlib.machinery.ExtensionFileLoader.exec_module(None, None)),
            ("import", lambda: importlib.machinery.SourceFileLoader.create_module(None, None)),
            ("import", lambda: importlib.machinery.SourceFileLoader.exec_module(None, None)),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden-v38")),
            ("decompression", lambda: zlib.decompressobj()),
        ]
        for module_name, attribute, kind, args in (
            ("_io", "open", "filesystem", ("forbidden-v38",)),
            ("posix", "open", "filesystem", ("forbidden-v38", 0)),
            ("posix", "execv", "process", ("/forbidden-v38", [])),
            ("_posixsubprocess", "fork_exec", "process", ()),
            ("_ctypes", "dlopen", "native", ("forbidden-v38.so",)),
            ("_imp", "create_dynamic", "native", (None,)),
            ("_imp", "exec_dynamic", "native", (None,)),
            ("_imp", "create_builtin", "native", (None,)),
            ("_imp", "exec_builtin", "native", (None,)),
            ("_socket", "socket", "network", ()),
            ("_thread", "start_new_thread", "thread", (lambda: None, ())),
        ):
            module = sys.modules.get(module_name)
            if module is not None and hasattr(module, attribute):
                probes.append((
                    kind,
                    lambda owner=module, name=attribute, arguments=args:
                    getattr(owner, name)(*arguments),
                ))
        for kind, action in probes:
            previous = wall.blocked[kind]
            try:
                action()
            except GraphError:
                need(
                    wall.blocked[kind] == previous + 1,
                    "prove the actual source-only effect was physically blocked: " + kind,
                )
                continue
            raise GraphError("a genuine V38 source-only effect escaped: " + kind)
        need(
            rejected >= 175 and all(count > 0 for count in wall.blocked.values()),
            "reject all forged references and physically exercise every effect boundary",
        )
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 38,
            "status": "PASS",
            "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "full_case_denominator": ORIGINAL_CASE_COUNT,
            "suite_count": SUITE_COUNT,
            "private_waiver_count": PRIVATE_WAIVERS,
            "corrected_reference_status": "PASS; SYNTHETIC FIXTURE ONLY",
            "actual_reference_evidence_read_by_self_test": 0,
            "all_candidate_matching_blocked": True,
            "candidate_case_producer_corrected_v4_status": "NOT FROZEN",
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "candidate_matching_archives_opened_by_graph": 0,
            "matching_archive_gzip_inflation_count": 0,
            "reference_archive_gzip_inflation_count": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(
        path in allowed and type(raw) is bytes and 0 < len(raw) <= OWNER_LIMIT,
        "publish only the three exclusively authorized new V38 graph outputs",
    )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(handle, remaining)
            need(
                type(written) is int and written > 0,
                "reject an incompletely written genuine V38 graph owner",
            )
            remaining = remaining[written:]
        os.fsync(handle)
        observed = os.fstat(handle)
        need(
            observed.st_uid == os.geteuid()
            and observed.st_nlink == 1
            and observed.st_size == len(raw)
            and stat.S_IMODE(observed.st_mode) == 0o600,
            "require a unique, fully synchronized owner-only V38 graph output",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(observed == raw, "verify all durable independently generated V38 output bytes")


def result(source: str, outputs: dict[str, bytes], written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 38,
        "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_corrected_reference_archive_sha256": ARCHIVE_PIN[1],
        "actual_corrected_reference_archive_bytes": ARCHIVE_PIN[2],
        "actual_corrected_reference_receipt_sha256": RECEIPT_PIN[1],
        "actual_corrected_reference_receipt_bytes": RECEIPT_PIN[2],
        "phase_one_reference_gate_status": "PASS",
        "candidate_facing_self_oracle_status": "PASS",
        "same_context_reference_correction_status": "PASS",
        "corrected_reference_status": "PASS",
        "corrected_reference_publication_status": "PASS",
        "corrected_reference_actual_worker_count": 2,
        "corrected_reference_process_ids": list(PIDS),
        "corrected_reference_case_count_per_worker": CASE_COUNT,
        "corrected_reference_total_observed_case_count": 2 * CASE_COUNT,
        "corrected_reference_full_records_sha256": FULL_RECORDS_SHA,
        "corrected_reference_cache_cases_per_worker": CACHE_COUNT,
        "corrected_reference_cache_records_sha256": CACHE_RECORDS_SHA,
        "reference_context_falsifying_case_count": 0,
        "historical_reference_context_falsifying_case_count": CACHE_COUNT,
        "full_case_denominator": ORIGINAL_CASE_COUNT,
        "suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVERS,
        "original_cases_removed": 0,
        "additional_private_waivers": 0,
        "case_denominator_changed": False,
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "preserved_v37_evidence_owner_lower_bound": 162,
        "preserved_v37_history_reference_lower_bound": 167,
        "new_corrected_reference_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "all_candidate_matching_blocked": True,
        "candidate_matching_block_reason": BLOCK_REASON,
        "candidate_case_producer_status": "STALE; CORRECTED V4 NOT FROZEN",
        "candidate_case_producer_corrected_v4_status": "NOT FROZEN",
        "qualified_candidate_count": 0,
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_zig_semantic_mismatch_count": 1764,
        "rust_v13_source_build_status": "PASS",
        "rust_v13_source_build_process_count": 28,
        "rust_v13_matching_test_status": "NOT RUN",
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_candidate_status": "NOT RUN",
        "outputs_written": written,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_compressed_bytes_read": ARCHIVE_PIN[2],
        "reference_archive_uncompressed_bytes_read": UNCOMPRESSED_BYTES,
        "reference_archive_uncompressed_sha256": UNCOMPRESSED_SHA,
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
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
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--archive-sha256")
    parser.add_argument("--receipt-sha256")
    for name in ("inputs", "summary", "svg"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    try:
        runtime()
        if options.self_test:
            need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256",
                        "source_bytes",
                        "archive_sha256",
                        "receipt_sha256",
                        "inputs_sha256",
                        "summary_sha256",
                        "svg_sha256",
                    )
                ),
                "source-only synthetic tests must never accept real evidence pins",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(options.source_sha256, "actual V38 graph renderer")
        archive = checked(options.archive_sha256, "actual corrected reference archive")
        receipt = checked(options.receipt_sha256, "actual corrected reference receipt")
        _snapshot, pairs = build(source, options.source_bytes, archive, receipt)
        outputs = dict(pairs)
        if options.render:
            need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "render only the three genuinely new exclusively authorized V38 outputs",
            )
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(source, outputs, True, "-published")))
            return 0
        expected = {
            OUTPUT + ".inputs.json": checked(options.inputs_sha256, "frozen V38 graph inputs"),
            OUTPUT + ".json": checked(options.summary_sha256, "frozen V38 graph summary"),
            OUTPUT + ".svg": checked(options.svg_sha256, "frozen V38 graph image"),
        }
        for path, fingerprint in expected.items():
            observed, _ = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(observed == outputs[path], "independently reproduce every V38 output")
        sys.stdout.buffer.write(canonical(result(
            source, outputs, False, "-read-only-frozen-context"
        )))
        return 0
    except (
        GraphError,
        OSError,
        ValueError,
        TypeError,
        EOFError,
        KeyError,
        AttributeError,
        zlib.error,
        RecursionError,
    ) as error:
        sys.stderr.write("current V38 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
