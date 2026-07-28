#!/usr/bin/env python3
"""Freeze and durably run two original Python callable-signature references."""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import ctypes
from dataclasses import dataclass
import errno
import fcntl
import gzip
import hashlib
import importlib
import io
import json
import locale
import os
from pathlib import Path, PurePosixPath
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Mapping, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-owned-callable-introspection-reference-v2"
V1_SCHEMA = "rebar-python-re-callable-introspection-v1"
SOURCE_RELATIVE = "tools/run_owned_callable_introspection_reference_v2.py"
PROTOCOL_RELATIVE = "oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md"
CONTRACT_RELATIVE = "oracle/phase1/callable-introspection-reference-v2.json"
EVIDENCE_DIRECTORY = "oracle/phase1/evidence"
EVIDENCE_BASENAME = "callable-introspection-reference-v2-cpython-3.14.6"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
MAX_OWNER_BYTES = 2 * 1024 * 1024
MAX_EXECUTABLE_BYTES = 64 * 1024 * 1024
MAX_STREAM_BYTES = 1024 * 1024
MAX_REPORT_BYTES = 4 * 1024 * 1024
MATRIX_SHA256 = "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
REFERENCE_ROLES = ("reference-a", "reference-b")
CORE_CASE_COUNT = 31_237
CORE_SUITE_COUNT = 13
CORE_PRIVATE_WAIVER_COUNT = 13
ADDITIONAL_CASE_COUNT = 50
V33_OWNER_COUNT = 155
V33_REFERENCE_COUNT = 160
ZIG_V3_LABEL = "phase2-v12-zig-scanner-v2-original-p0"
ZIG_V3_RECEIPT_BASENAME = "repaired-zig-original-campaign-v3-zig-" + ZIG_V3_LABEL


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int


GOAL = Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
CORE_INVENTORY = Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
CORE_PROTOCOL = Owner("oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392)
V1_SOURCE = Owner("tools/verify_python_re_callable_introspection_v1.py", "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653", 75608)
V1_PROTOCOL = Owner("oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md", "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8", 8952)
V1_CONTRACT = Owner("oracle/phase1/p0-callable-introspection-v1.json", "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749)
V33_RENDERER = Owner("tools/render_candidate_current_overview_v33.py", "e81a1c032c550475c4a4ece9ae11b903d105d62e8666ce46b69138b260ca91d5", 75615)
V33_INPUTS = Owner("docs/evidence/candidate-current-overview-v33.inputs.json", "1f98790a6a31d8cdf298bf5fd13c6d4d14cfb44785e1e445d791c83557de921e", 106942)
V33_SUMMARY = Owner("docs/evidence/candidate-current-overview-v33.json", "b56b5f0e09ff3aa3990b210934e1d73d1989bd03c6bb479a8a7abd66eb93a9a6", 380577)
V33_SVG = Owner("docs/evidence/candidate-current-overview-v33.svg", "203c15b16b74cf1dd8be3308677ddd67fa94a7a8411e5de38b43186647ccf858", 13068)
ZIG_ARCHIVE = Owner("oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2.json.gz", "3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d", 48371)
ZIG_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2-publication-receipt.json", "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b", 2029)
INSTALLED_RE = Owner("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py", "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35", 17876)


class ReferenceError(Exception):
    """An independently frozen reference or publication failed closed."""


class SourceOnlyViolation(ReferenceError):
    """A physically forbidden source-only effect was intercepted."""


def need(condition: object, reason: str) -> None:
    if condition is not True:
        raise ReferenceError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only complete original bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: object, name: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(character in "0123456789abcdef" for character in value),
         "require an independently supplied canonical SHA-256: " + name)
    return value


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise ReferenceError("reject noncanonical reference data") from error


def strict_document(raw: object, name: str, *, exact: bool = True) -> dict[str, Any]:
    need(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
         "reject empty, truncated, or oversized JSON: " + name)

    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            need(type(key) is str and key not in result,
                 "reject duplicate JSON keys: " + name)
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise ReferenceError("reject nonfinite JSON: " + value)

    try:
        value = json.loads(raw.decode("utf-8", "strict"),
                           object_pairs_hook=unique, parse_constant=reject_constant)
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise ReferenceError("reject malformed reference JSON: " + name) from error
    need(type(value) is dict, "require a reference JSON object: " + name)
    if exact:
        need(canonical(value) == raw, "reject noncanonical frozen JSON: " + name)
    return value


def relative_parts(value: str) -> tuple[str, ...]:
    need(type(value) is str and 0 < len(value) <= 512
         and "\\" not in value and "\x00" not in value,
         "reject an ambiguous frozen owner path")
    parsed = PurePosixPath(value)
    parts = parsed.parts
    need(not parsed.is_absolute() and str(parsed) == value and 0 < len(parts) <= 12
         and all(part not in ("", ".", "..") for part in parts)
         and not any(part == "candidates" or part == "performance"
                     or "holdout" in part.lower() or "hidden" in part.lower()
                     for part in parts),
         "never open a candidate, performance result, holdout, or escaped path")
    return parts


def read_owner(owner: Owner, *, external: bool = False) -> bytes:
    checked_digest(owner.sha256, owner.path)
    need(type(owner.size) is int and 0 < owner.size <= MAX_OWNER_BYTES,
         "reject an oversized frozen reference owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handles: list[int] = []
    descriptor: int | None = None
    try:
        if external:
            need(owner == INSTALLED_RE, "reject an unapproved external oracle owner")
            descriptor = os.open(owner.path, flags)
            visible = os.stat(owner.path, follow_symlinks=False)
        else:
            parts = relative_parts(owner.path)
            directory = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
            handles.append(directory)
            for part in parts[:-1]:
                directory = os.open(part, flags | getattr(os, "O_DIRECTORY", 0),
                                    dir_fd=directory)
                handles.append(directory)
            descriptor = os.open(parts[-1], flags, dir_fd=directory)
            visible = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
             and before.st_nlink == 1 and before.st_size == owner.size
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_uid, before.st_nlink)
             == (visible.st_dev, visible.st_ino, visible.st_size,
                 visible.st_uid, visible.st_nlink),
             "reject a linked, replaced, foreign, or partial owner: " + owner.path)
        blocks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            need(type(block) is bytes and bool(block),
                 "reject truncated descriptor-bound reference bytes")
            remaining -= len(block)
            blocks.append(block)
        need(os.read(descriptor, 1) == b"", "reject appended reference bytes")
        actual = b"".join(blocks)
        after = os.fstat(descriptor)
        need((before.st_dev, before.st_ino, before.st_size, before.st_uid,
              before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                 after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
             and digest(actual) == owner.sha256,
             "reject frozen bytes changed during verification: " + owner.path)
        return actual
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for handle in reversed(handles):
            os.close(handle)


def read_optional_receipt(relative: str) -> tuple[dict[str, Any], Owner] | None:
    """Authenticate an appended receipt without opening its matching archive."""
    pieces = relative_parts(relative)
    need(pieces[:3] == ("oracle", "phase2", "evidence")
         and pieces[-1].endswith("-publication-receipt.json"),
         "inspect only an exact append-only matching publication receipt")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories: list[int] = []
    descriptor: int | None = None
    try:
        directory = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
        directories.append(directory)
        for piece in pieces[:-1]:
            directory = os.open(piece, flags | getattr(os, "O_DIRECTORY", 0),
                                dir_fd=directory)
            directories.append(directory)
        try:
            descriptor = os.open(pieces[-1], flags, dir_fd=directory)
        except FileNotFoundError:
            return None
        before = os.fstat(descriptor)
        visible = os.stat(pieces[-1], dir_fd=directory, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
             and before.st_nlink == 1 and 0 < before.st_size <= MAX_OWNER_BYTES
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_uid, before.st_nlink)
             == (visible.st_dev, visible.st_ino, visible.st_size,
                 visible.st_uid, visible.st_nlink),
             "reject a linked, changed, or unowned later matching receipt")
        blocks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            need(type(block) is bytes and bool(block),
                 "reject a truncated append-only matching receipt")
            remaining -= len(block)
            blocks.append(block)
        need(os.read(descriptor, 1) == b"",
             "reject appended bytes in a later matching receipt")
        raw = b"".join(blocks)
        after = os.fstat(descriptor)
        need((before.st_dev, before.st_ino, before.st_size, before.st_uid,
              before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                 after.st_nlink, after.st_mtime_ns, after.st_ctime_ns),
             "reject a later matching receipt changed during authentication")
        document = strict_document(raw, "append-only corrected Zig V3 receipt")
        return document, Owner(relative, digest(raw), len(raw))
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for directory in reversed(directories):
            os.close(directory)


def verify_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.abspath(sys.executable) == PINNED_PYTHON
         and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "require the pinned isolated Python 3.14.6; never import a candidate")


def owner_document(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size}


def boundaries() -> dict[str, Any]:
    return {
        "actual_reference_processes_started": 0,
        "actual_candidate_processes_started": 0,
        "actual_candidate_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_source_builds_started": 0,
        "actual_files_written": 0,
        "actual_network_requests": 0,
        "actual_threads_started": 0,
        "actual_clock_samples": 0,
        "actual_matching_archives_opened": 0,
        "actual_source_build_archives_decompressed": 0,
        "actual_holdout_cases_read": 0,
        "actual_final_cases_read": 0,
        "timing_trials_run": 0,
        "reference_status": "NOT RUN",
        "candidate_introspection": "NOT MEASURED",
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "final_holdout_opened": False,
        "final_cases_generated": False,
        "winner_selected": False,
    }


def validate_matrix(matrix: object) -> str:
    need(type(matrix) is list and len(matrix) == ADDITIONAL_CASE_COUNT,
         "preserve exactly 50 separately counted frozen signature cases")
    identifiers: set[str] = set()
    counts = {"module": 0, "pattern": 0, "match": 0, "scanner": 0}
    for item in matrix:
        need(type(item) is dict
             and set(item) == {"id", "category", "owner", "binding", "member"}
             and all(type(item[key]) is str for key in item)
             and item["id"] not in identifiers and item["category"] in counts,
             "reject a forged, duplicate, partial, or unknown frozen case")
        identifiers.add(item["id"])
        counts[item["category"]] += 1
    need(counts == {"module": 11, "pattern": 18, "match": 14, "scanner": 7}
         and digest(canonical(matrix)) == MATRIX_SHA256,
         "reject reordered, omitted, hardcoded, or invented signature cases")
    return MATRIX_SHA256


def validate_observations(records: object, matrix: list[dict[str, Any]]) -> str:
    need(type(records) is list and len(records) == ADDITIONAL_CASE_COUNT,
         "require every separately frozen signature observation")
    for index, (case, item) in enumerate(zip(matrix, records, strict=True)):
        need(type(item) is dict and set(item) == set(case) | {"observation"}
             and all(item.get(key) == value for key, value in case.items())
             and type(item.get("observation")) is dict,
             "reject an omitted, reordered, or substituted observation " + str(index))
        observed = item["observation"]
        need(type(observed.get("text_signature_present")) is bool
             and (observed.get("raw_text_signature") is None
                  or type(observed.get("raw_text_signature")) is str),
             "retain the exact public callable text signature")
        if observed.get("status") == "INSPECTABLE":
            need(set(observed) == {"status", "parameters", "return_annotation",
                                   "text_signature_present", "raw_text_signature"}
                 and type(observed.get("parameters")) is list
                 and type(observed.get("return_annotation")) is dict,
                 "reject incomplete public signature parameters")
            for parameter in observed["parameters"]:
                need(type(parameter) is dict
                     and set(parameter) == {"parameter_name", "parameter_kind",
                                            "normalized_default", "annotation"}
                     and type(parameter.get("parameter_name")) is str
                     and parameter.get("parameter_kind") in
                     {"POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD", "VAR_POSITIONAL",
                      "KEYWORD_ONLY", "VAR_KEYWORD"}
                     and type(parameter.get("normalized_default")) is dict
                     and type(parameter.get("annotation")) is dict,
                     "reject missing positional-only, default, or annotation metadata")
        else:
            need(observed.get("status") == "UNINSPECTABLE"
                 and set(observed) == {"status", "signature_error_class",
                                       "text_signature_present", "raw_text_signature"}
                 and observed.get("signature_error_class") in {"TypeError", "ValueError"},
                 "reject an invented uninspectable callable observation")
    return digest(canonical(records))


def validate_worker(worker: object, role: str,
                    matrix: list[dict[str, Any]]) -> str:
    need(type(worker) is dict
         and worker.get("schema") == V1_SCHEMA + "-reference-worker"
         and worker.get("status") == "PASS" and worker.get("role") == role
         and type(worker.get("actual_process_id")) is int
         and worker["actual_process_id"] > 0
         and worker.get("original_case_denominator") == CORE_CASE_COUNT
         and worker.get("additional_case_count") == ADDITIONAL_CASE_COUNT
         and worker.get("candidate_imports") == 0
         and worker.get("hidden_cases_read") == 0
         and worker.get("performance") == "NOT MEASURED",
         "reject a forged, incomplete, or candidate-tainted Python reference")
    vector = validate_observations(worker.get("records"), matrix)
    need(worker.get("record_vector_sha256") == vector,
         "reject a forged complete reference-vector fingerprint")
    return vector


def validate_pair(workers: object, matrix: list[dict[str, Any]]) -> str:
    need(type(workers) is list and len(workers) == 2,
         "require exactly two genuinely separate standard-library workers")
    first = validate_worker(workers[0], REFERENCE_ROLES[0], matrix)
    second = validate_worker(workers[1], REFERENCE_ROLES[1], matrix)
    need(workers[0]["actual_process_id"] != workers[1]["actual_process_id"]
         and first == second and workers[0]["records"] == workers[1]["records"],
         "reject reused process IDs or unequal complete 50-case references")
    return first


def validate_streams(streams: object, workers: list[dict[str, Any]]) -> None:
    need(type(streams) is list and len(streams) == 2,
         "retain both complete original reference stdout and stderr streams")
    for index, stream in enumerate(streams):
        need(type(stream) is dict and stream.get("role") == REFERENCE_ROLES[index]
             and stream.get("exit_code") == 0,
             "reject a reordered or failed complete reference stream")
        for channel in ("stdout", "stderr"):
            encoded = stream.get(channel + "_base64")
            need(type(encoded) is str, "retain every exact reference output byte")
            try:
                raw = base64.b64decode(encoded.encode("ascii"), validate=True)
            except (ValueError, UnicodeError) as error:
                raise ReferenceError("reject forged complete reference output") from error
            need(len(raw) <= MAX_STREAM_BYTES
                 and stream.get(channel + "_bytes") == len(raw)
                 and stream.get(channel + "_sha256") == digest(raw),
                 "reject truncated or substituted reference " + channel)
            if channel == "stdout":
                need(raw == canonical(workers[index]),
                     "bind the entire worker vector to its original stdout")


def validate_core(value: Mapping[str, Any]) -> None:
    need(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
         and value.get("version") == 1
         and type(value.get("denominator")) is dict
         and value["denominator"].get("final_required_case_execution_denominator")
         == CORE_CASE_COUNT and type(value.get("original_upstream")) is dict
         and value["original_upstream"].get("private_waiver_count")
         == CORE_PRIVATE_WAIVER_COUNT,
         "never alter the frozen 31,237 cases or 13 named private waivers")
    suites = value.get("suites")
    need(type(suites) is list and len(suites) == CORE_SUITE_COUNT
         and sum(row.get("case_execution_count", 0) for row in suites
                 if type(row) is dict) == CORE_CASE_COUNT
         and all(type(row) is dict and type(row.get("baseline")) is dict
                 and row["baseline"].get("status") == "PASS" for row in suites),
         "preserve all 13 independently passing original Python suites")


def validate_v1(value: Mapping[str, Any]) -> list[dict[str, Any]]:
    need(value.get("schema") == V1_SCHEMA + "-source-freeze"
         and value.get("version") == 1
         and value.get("status") == "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN"
         and value.get("source") == {"path": V1_SOURCE.path, "sha256": V1_SOURCE.sha256}
         and value.get("protocol") == {"path": V1_PROTOCOL.path,
                                      "sha256": V1_PROTOCOL.sha256},
         "reject a replaced frozen additive signature oracle")
    additional = value.get("additional_obligation")
    need(type(additional) is dict
         and additional.get("id") == "API-PUBLIC-CALLABLE-INTROSPECTION"
         and additional.get("included_in_original_31237_denominator") is False
         and additional.get("case_count") == ADDITIONAL_CASE_COUNT
         and additional.get("matrix_sha256") == MATRIX_SHA256,
         "keep the 50 original signature cases separate from the core")
    matrix = additional.get("case_matrix")
    need(validate_matrix(matrix) == MATRIX_SHA256,
         "reject an unpinned additional signature matrix")
    policy = value.get("future_reference_policy")
    need(type(policy) is dict and policy.get("reference_roles") == list(REFERENCE_ROLES)
         and policy.get("independent_isolated_worker_process_count") == 2
         and policy.get("different_actual_process_ids_required") is True
         and policy.get("exact_complete_case_vectors_required") is True
         and policy.get("complete_stdout_and_stderr_required") is True
         and policy.get("executed_in_source_freeze") is False,
         "never replace the frozen two-reference standard-library contract")
    history_container = value.get("actual_published_history")
    need(type(history_container) is dict, "preserve exact historical V1 evidence")
    historical = history_container.get("actual_history")
    need(type(historical) is dict and historical.get("repository_evidence_owner_count") == 151
         and historical.get("authenticated_history_reference_count") == 156
         and historical.get("rust_semantic_mismatch_count") == 1087
         and historical.get("c_semantic_mismatch_count") == 1230
         and historical.get("zig_semantic_mismatch_count") == 2172
         and historical.get("original_case_denominator") == CORE_CASE_COUNT
         and historical.get("additional_introspection_case_count") == ADDITIONAL_CASE_COUNT
         and historical.get("additional_cases_included_in_original_denominator") is False
         and historical.get("introspection_reference") == "NOT RUN",
         "preserve V1 151/156 and Rust 1,087 as historical, never current")
    return matrix


def validate_current(inputs: Mapping[str, Any], summary: Mapping[str, Any],
                     receipt: Mapping[str, Any]) -> None:
    need(inputs.get("schema") == "rebar-candidate-current-overview-v33-inputs"
         and inputs.get("version") == 33
         and summary.get("schema") == "rebar-candidate-current-overview-v33-summary"
         and summary.get("version") == 33 and summary.get("status") == "PASS",
         "authenticate the actual published version-33 compatibility snapshot")
    for value, reference_field in (
        (inputs, "all_digest_addressed_history_path_count"),
        (summary, "authenticated_digest_addressed_history_paths"),
    ):
        need(value.get("python") == "3.14.6"
             and value.get("suite_count") == CORE_SUITE_COUNT
             and value.get("full_case_denominator") == CORE_CASE_COUNT
             and value.get("private_waiver_count") == CORE_PRIVATE_WAIVER_COUNT
             and value.get("repository_evidence_owner_count") == V33_OWNER_COUNT
             and value.get(reference_field) == V33_REFERENCE_COUNT
             and value.get("performance") == "NOT MEASURED"
             and value.get("memory") == "NOT MEASURED"
             and value.get("undefined_behavior") == "NOT MEASURED"
             and value.get("final_holdout_opened") is False
             and value.get("final_comparison_cases_generated") is False
             and value.get("final_comparison_planned_case_count") == 4_194_304
             and value.get("winner_selected") is False,
             "reject forged current counts, performance claims, or holdout access")
    need(inputs.get("candidate_qualified_count") == 0
         and summary.get("qualified_candidate_count") == 0
         and inputs.get("rust_original_campaign_semantic_mismatch_count") == 1036
         and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
         and inputs.get("rust_original_campaign_verified_passing_case_count") == 8965
         and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
         and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
         and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
         and inputs.get("actual_zig_semantic_mismatch_count") == 2172
         and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
         and summary.get("additional_signature_frozen_case_count") == ADDITIONAL_CASE_COUNT
         and summary.get("additional_signature_reference_cases_executed") == 0
         and summary.get("additional_signature_reference_status") == "NOT RUN",
         "never promote a replacement or call the 50-case reference already run")
    need(inputs.get("renderer") == owner_document(V33_RENDERER)
         and summary.get("source") == owner_document(V33_RENDERER)
         and summary.get("inputs") == owner_document(V33_INPUTS)
         and summary.get("svg") == owner_document(V33_SVG),
         "bind all four distinct exact version-33 graph owners")
    need(inputs.get("zig_v12_source_build_status") == "PASS"
         and inputs.get("zig_v12_source_build_process_count") == 26
         and inputs.get("zig_v12_source_build_independent_phase_count") == 2
         and inputs.get("zig_v12_source_build_matching_test_status") == "NOT MEASURED"
         and summary.get("zig_v12_source_build_status") == "PASS"
         and summary.get("zig_v12_source_build_process_count") == 26
         and summary.get("zig_v12_source_build_phase_count") == 2
         and summary.get("zig_v12_source_build_candidate_worker_count") == 0
         and summary.get("zig_v12_source_build_matching_test_status") == "NOT MEASURED",
         "distinguish a real corrected Zig source build from unrun compatibility")
    archive = receipt.get("archive")
    need(receipt.get("schema")
         == "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt"
         and receipt.get("status") == "PASS" and receipt.get("build_status") == "PASS"
         and receipt.get("family") == "zig"
         and receipt.get("label") == "phase2-v12-zig-scanner-v2"
         and receipt.get("actual_compiler_process_count") == 26
         and receipt.get("actual_source_apply_count") == 2
         and receipt.get("actual_evidence_owner_count_before_publication") == 153
         and receipt.get("actual_authenticated_reference_count_before_publication") == 158
         and receipt.get("new_actual_evidence_owner_count") == 2
         and receipt.get("repository_evidence_owner_count_after_publication") == 155
         and receipt.get("authenticated_history_reference_count_after_publication") == 160
         and receipt.get("candidate_correctness") == "NOT MEASURED"
         and receipt.get("candidate_processes_started") == 0
         and receipt.get("candidate_imports") == 0
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("memory") == "NOT MEASURED"
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("winner_selected") is False
         and type(archive) is dict and archive.get("path") == ZIG_ARCHIVE.path
         and archive.get("sha256") == ZIG_ARCHIVE.sha256
         and archive.get("bytes") == ZIG_ARCHIVE.size
         and archive.get("exclusive_creation") is True
         and archive.get("same_inode_readback_verified") is True
         and archive.get("file_fsync_completed") is True
         and archive.get("directory_fsync_completed") is True,
         "authenticate corrected Zig receipt and raw archive without inflating it")


def observe_later_zig_matching() -> dict[str, Any] | None:
    """Preserve a real subsequently published V3 result, never its archive."""
    observed: list[tuple[dict[str, Any], Owner, bool]] = []
    for failed in (False, True):
        suffix = "-failures" if failed else ""
        relative = ("oracle/phase2/evidence/" + ZIG_V3_RECEIPT_BASENAME
                    + suffix + "-publication-receipt.json")
        item = read_optional_receipt(relative)
        if item is not None:
            observed.append((item[0], item[1], failed))
    need(len(observed) <= 1,
         "reject conflicting successful and failed corrected Zig outcomes")
    if not observed:
        return None
    receipt, owner, failed_name = observed[0]
    return validate_later_zig_receipt(receipt, owner, failed_name)


def validate_later_zig_receipt(receipt: Mapping[str, Any], owner: Owner,
                               failed_name: bool) -> dict[str, Any]:
    """Preserve complete matching or an honest partial infrastructure failure."""
    need(type(receipt) is dict and isinstance(owner, Owner)
         and type(failed_name) is bool,
         "require exact independently observed corrected Zig evidence")
    archive = receipt.get("archive")
    candidate_status = receipt.get("candidate_status")
    completed = receipt.get("completed_suite_count")
    actual_workers = receipt.get("actual_candidate_workers")
    mismatches = receipt.get("semantic_mismatch_count")
    infrastructure = receipt.get("infrastructure_failure_count")
    expected_archive_name = (ZIG_V3_RECEIPT_BASENAME
                             + ("-failures" if failed_name else "") + ".json.gz")
    need(receipt.get("schema")
         == "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt"
         and receipt.get("status") == "PASS"
         and receipt.get("publication_status") == "PASS"
         and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
         and candidate_status in {"PASS", "FAIL"}
         and (candidate_status == "FAIL") == failed_name
         and receipt.get("family") == "zig"
         and receipt.get("label") == ZIG_V3_LABEL
         and receipt.get("actual_v12_build_receipt_sha256") == ZIG_RECEIPT.sha256
         and receipt.get("suite_count") == CORE_SUITE_COUNT
         and receipt.get("case_execution_denominator") == CORE_CASE_COUNT
         and receipt.get("named_private_waiver_count") == CORE_PRIVATE_WAIVER_COUNT
         and type(completed) is int and 0 <= completed <= CORE_SUITE_COUNT
         and type(actual_workers) is int and 0 <= actual_workers <= CORE_SUITE_COUNT
         and completed == actual_workers
         and type(receipt.get("verified_passing_case_count")) is int
         and receipt["verified_passing_case_count"] >= 0
         and ((completed == CORE_SUITE_COUNT
               and type(mismatches) is int and mismatches >= 0)
              or (completed < CORE_SUITE_COUNT
                  and mismatches == "NOT MEASURED"))
         and type(infrastructure) is int and infrastructure >= 0
         and ((candidate_status == "PASS"
               and completed == CORE_SUITE_COUNT
               and actual_workers == CORE_SUITE_COUNT
               and mismatches == 0 and infrastructure == 0
               and receipt["verified_passing_case_count"] == CORE_CASE_COUNT
               and receipt.get("candidate_qualified") is True)
              or (candidate_status == "FAIL"
                  and receipt.get("candidate_qualified") is False))
         and receipt.get("historical_evidence_owner_count_before_publication")
         == V33_OWNER_COUNT
         and receipt.get("historical_authenticated_reference_count_before_publication")
         == V33_REFERENCE_COUNT
         and receipt.get("new_repository_evidence_owner_count") == 2
         and receipt.get("resulting_repository_evidence_owner_count")
         == V33_OWNER_COUNT + 2
         and receipt.get("resulting_authenticated_reference_count")
         == V33_REFERENCE_COUNT + 2
         and receipt.get("actual_corrected_rust_semantic_mismatch_count") == 1036
         and receipt.get("actual_c_semantic_mismatch_count") == 1230
         and receipt.get("historical_zig_semantic_mismatch_count") == 2172
         and receipt.get("all_original_native_targets_restored") is True
         and receipt.get("restoration_verified_before_publication") is True
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("memory") == "NOT MEASURED"
         and receipt.get("undefined_behavior") == "NOT MEASURED"
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("winner_selected") is False
         and type(archive) is dict and archive.get("relative") == expected_archive_name
         and type(archive.get("sha256")) is str
         and checked_digest(archive["sha256"], "later matching archive metadata")
         == archive["sha256"]
         and archive.get("exclusive_creation") is True
         and archive.get("same_inode_readback_verified") is True
         and archive.get("file_fsync_completed") is True
         and archive.get("directory_fsync_completed") is True,
         "reject forged or incomplete appended corrected Zig matching evidence")
    return {
        "receipt": owner_document(owner),
        "candidate_status": candidate_status,
        "completed_suite_count": completed,
        "actual_candidate_workers": actual_workers,
        "verified_passing_case_count": receipt["verified_passing_case_count"],
        "semantic_mismatch_count": mismatches,
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": receipt.get("candidate_qualified"),
        "all_original_native_targets_restored": True,
        "matching_archive_metadata_sha256": archive["sha256"],
        "matching_archive_opened": False,
        "matching_archive_decompressed": False,
        "evidence_owner_lower_bound": V33_OWNER_COUNT + 2,
        "history_reference_lower_bound": V33_REFERENCE_COUNT + 2,
    }


def history_snapshot(context: Mapping[str, Any]) -> dict[str, Any]:
    later = context.get("later_zig_matching")
    return {
        "pinned_v33_evidence_owner_count": V33_OWNER_COUNT,
        "pinned_v33_history_reference_count": V33_REFERENCE_COUNT,
        "authenticated_evidence_owner_lower_bound":
            later["evidence_owner_lower_bound"] if later else V33_OWNER_COUNT,
        "authenticated_history_reference_lower_bound":
            later["history_reference_lower_bound"] if later else V33_REFERENCE_COUNT,
        "appended_corrected_zig_matching": later,
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "source freeze")
    checked_digest(protocol_pin, "reference protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 2,
        "status": "SOURCE FREEZE ONLY; TWO REFERENCES NOT RUN",
        "phase": "ADDITIVE PYTHON CORRECTNESS ORACLE; NO BENCHMARK",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "goal": owner_document(GOAL),
        "pinned_runtime": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PINNED_PYTHON,
            "executable_sha256": PINNED_PYTHON_SHA256,
            "isolated": True, "bytecode_writes": False,
            "installed_re": owner_document(INSTALLED_RE),
        },
        "original_core": {
            "inventory": owner_document(CORE_INVENTORY),
            "protocol": owner_document(CORE_PROTOCOL),
            "case_execution_denominator": CORE_CASE_COUNT,
            "suite_count": CORE_SUITE_COUNT,
            "named_private_waiver_count": CORE_PRIVATE_WAIVER_COUNT,
            "denominator_modified": False,
        },
        "frozen_additional_oracle": {
            "source": owner_document(V1_SOURCE),
            "protocol": owner_document(V1_PROTOCOL),
            "contract": owner_document(V1_CONTRACT),
            "matrix_sha256": MATRIX_SHA256,
            "separately_counted_case_count": ADDITIONAL_CASE_COUNT,
            "included_in_original_core_denominator": False,
            "category_counts": {"module": 11, "pattern": 18,
                                "match": 14, "scanner": 7},
            "reference_status": "NOT RUN",
            "candidate_status": "NOT MEASURED",
        },
        "historical_frozen_v1_snapshot": {
            "repository_evidence_owner_count": 151,
            "authenticated_history_reference_count": 156,
            "rust_semantic_mismatch_count": 1087,
            "is_current": False,
        },
        "authenticated_historical_v33_lower_bound": {
            "overview_version": 33,
            "overview_owners": [owner_document(owner) for owner in
                                (V33_RENDERER, V33_INPUTS, V33_SUMMARY, V33_SVG)],
            "repository_evidence_owner_count": V33_OWNER_COUNT,
            "authenticated_history_reference_count": V33_REFERENCE_COUNT,
            "snapshot_is_not_asserted_latest": True,
            "rust_semantic_mismatch_count": 1036,
            "rust_verified_passing_case_count": 8965,
            "c_semantic_mismatch_count": 1230,
            "previous_zig_semantic_mismatch_count": 2172,
            "qualified_candidate_count": 0,
            "zig_corrected_source_build_status": "PASS",
            "zig_corrected_source_build_process_count": 26,
            "zig_corrected_matching_status": "NOT MEASURED",
            "zig_corrected_source_build_archive": owner_document(ZIG_ARCHIVE),
            "zig_corrected_source_build_receipt": owner_document(ZIG_RECEIPT),
            "source_build_archive_decompression_required": False,
            "candidate_matching_archive_access_required": False,
        },
        "append_only_later_zig_matching_policy": {
            "optional_receipt_schema":
                "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt",
            "candidate_label": ZIG_V3_LABEL,
            "success_receipt": ("oracle/phase2/evidence/"
                                + ZIG_V3_RECEIPT_BASENAME
                                + "-publication-receipt.json"),
            "failure_receipt": ("oracle/phase2/evidence/"
                                + ZIG_V3_RECEIPT_BASENAME
                                + "-failures-publication-receipt.json"),
            "matching_archive_opened": False,
            "matching_archive_decompressed": False,
            "candidate_worker_started_by_source_freeze": False,
        },
        "future_reference_policy": {
            "explicit_mode": "--run-reference",
            "accepted_explicit_alias": "--run",
            "reference_roles": list(REFERENCE_ROLES),
            "exact_distinct_isolated_worker_process_count": 2,
            "orchestrator_subprocess_count": 0,
            "source_owned_worker": owner_document(V1_SOURCE),
            "different_actual_process_ids_required": True,
            "identical_complete_case_vectors_required": True,
            "complete_stdout_and_stderr_required": True,
            "shell": False,
            "candidate_execution_allowed": False,
            "executed_during_source_freeze": False,
        },
        "future_durable_publication": {
            "directory": EVIDENCE_DIRECTORY,
            "success_archive": EVIDENCE_BASENAME + ".json.gz",
            "success_receipt": EVIDENCE_BASENAME + "-publication-receipt.json",
            "failure_archive": EVIDENCE_BASENAME + "-failures.json.gz",
            "failure_receipt": EVIDENCE_BASENAME + "-failures-publication-receipt.json",
            "new_evidence_owner_count": 2,
            "pinned_v33_evidence_owner_lower_bound_before_publication": V33_OWNER_COUNT,
            "pinned_v33_history_reference_lower_bound_before_publication": V33_REFERENCE_COUNT,
            "minimum_evidence_owner_count_after_publication": V33_OWNER_COUNT + 2,
            "minimum_history_reference_count_after_publication": V33_REFERENCE_COUNT + 2,
            "exclusive_creation": True,
            "symlink_following_allowed": False,
            "private_mode": "0600",
            "file_fsync_required": True,
            "directory_fsync_required": True,
            "same_inode_readback_required": True,
            "gzip_mtime": 0,
            "durable_receipt_pass_means": "EVIDENCE PUBLICATION ONLY",
            "reference_failure_preserved": True,
            "created_during_source_freeze": False,
        },
        "phase_boundary": boundaries(),
    }


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None
                   ) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    checked_digest(source_pin, "source")
    checked_digest(protocol_pin, "protocol")
    source = Owner(SOURCE_RELATIVE, source_pin, _source_size())
    protocol = Owner(PROTOCOL_RELATIVE, protocol_pin, _protocol_size())
    read_owner(source)
    read_owner(protocol)
    expected = contract_document(source_pin, protocol_pin)
    if contract_pin is not None:
        checked_digest(contract_pin, "contract")
        contract = Owner(CONTRACT_RELATIVE, contract_pin, _contract_size())
        observed = strict_document(read_owner(contract), "frozen V2 contract")
        need(observed == expected, "reject a stale, substituted, or unpinned V2 contract")
    for owner in (GOAL, CORE_PROTOCOL, V1_SOURCE, V1_PROTOCOL,
                  V33_RENDERER, V33_SVG):
        read_owner(owner)
    core = strict_document(read_owner(CORE_INVENTORY), "original 31,237-case inventory")
    validate_core(core)
    v1 = strict_document(read_owner(V1_CONTRACT), "frozen historical V1 oracle")
    matrix = validate_v1(v1)
    inputs = strict_document(read_owner(V33_INPUTS), "actual V33 graph inputs")
    summary = strict_document(read_owner(V33_SUMMARY), "actual V33 graph summary")
    receipt = strict_document(read_owner(ZIG_RECEIPT), "actual corrected Zig receipt")
    read_owner(ZIG_ARCHIVE)
    validate_current(inputs, summary, receipt)
    later_matching = observe_later_zig_matching()
    installed = read_owner(INSTALLED_RE, external=True)
    need(all(item in installed for item in
             (b"sub.__text_signature__", b"subn.__text_signature__",
              b"split.__text_signature__")),
         "retain the pinned CPython public-signature source witnesses")
    return expected, matrix, {
        "core": core, "v1": v1, "inputs": inputs,
        "summary": summary, "zig_receipt": receipt,
        "later_zig_matching": later_matching,
    }


def _source_size() -> int:
    value = os.stat(str(ROOT / SOURCE_RELATIVE), follow_symlinks=False).st_size
    need(0 < value <= MAX_OWNER_BYTES, "bound the exact caller-pinned source")
    return value


def _protocol_size() -> int:
    value = os.stat(str(ROOT / PROTOCOL_RELATIVE), follow_symlinks=False).st_size
    need(0 < value <= MAX_OWNER_BYTES, "bound the exact caller-pinned protocol")
    return value


def _contract_size() -> int:
    value = os.stat(str(ROOT / CONTRACT_RELATIVE), follow_symlinks=False).st_size
    need(0 < value <= MAX_OWNER_BYTES, "bound the exact caller-pinned contract")
    return value


class SourceWall:
    """Make every claimed zero source-only effect physically observable."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {name: 0 for name in
                        ("filesystem", "write", "process", "import", "network",
                         "thread", "clock", "native", "lock", "signal",
                         "decompression", "locale", "regex_matching")}

    def deny(self, owner: Any, name: str, category: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise SourceOnlyViolation("physically blocked " + category + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceWall:
        groups: list[tuple[Any, tuple[str, ...], str]] = [
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir", "listdir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename",
                  "replace", "fsync", "fork", "system", "posix_spawn"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename",
                    "replace", "touch"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output"), "process"),
            (importlib, ("import_module",), "import"),
            (socket, ("socket", "create_connection"), "network"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                    "perf_counter_ns", "process_time", "process_time_ns", "sleep"), "clock"),
            (ctypes, ("CDLL", "PyDLL"), "native"),
            (fcntl, ("flock",), "lock"),
            (signal, ("signal", "pthread_sigmask"), "signal"),
            (gzip, ("open", "decompress", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
            (locale, ("setlocale",), "locale"),
        ]
        original_re = sys.modules.get("re")
        if original_re is not None:
            groups.append((original_re,
                           ("compile", "match", "fullmatch", "search", "sub", "subn",
                            "split", "findall", "finditer"), "regex_matching"))
        for owner, names, category in groups:
            for name in names:
                self.deny(owner, name, category)
        return self

    def __exit__(self, *_arguments: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def synthetic_worker(role: str, process_id: int,
                     matrix: list[dict[str, Any]]) -> dict[str, Any]:
    records = [{**case, "observation": {
        "status": "INSPECTABLE", "parameters": [],
        "return_annotation": {"kind": "empty"},
        "text_signature_present": False, "raw_text_signature": None,
    }} for case in matrix]
    return {
        "schema": V1_SCHEMA + "-reference-worker", "status": "PASS",
        "role": role, "actual_process_id": process_id,
        "original_case_denominator": CORE_CASE_COUNT,
        "additional_case_count": ADDITIONAL_CASE_COUNT,
        "record_vector_sha256": validate_observations(records, matrix),
        "records": records, "candidate_imports": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def capture_stream(role: str, exit_code: int,
                   stdout: bytes, stderr: bytes) -> dict[str, Any]:
    need(role in REFERENCE_ROLES and type(exit_code) is int,
         "require one genuine named reference process")
    result: dict[str, Any] = {"role": role, "exit_code": exit_code}
    for channel, value in (("stdout", stdout), ("stderr", stderr)):
        need(type(value) is bytes and len(value) <= MAX_STREAM_BYTES,
             "bound and preserve every byte of reference " + channel)
        result[channel + "_base64"] = base64.b64encode(value).decode("ascii")
        result[channel + "_sha256"] = digest(value)
        result[channel + "_bytes"] = len(value)
    return result


def synthetic_stream(worker: dict[str, Any]) -> dict[str, Any]:
    return capture_stream(worker["role"], 0, canonical(worker), b"")


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    _, matrix, context = verify_context(source_pin, protocol_pin, contract_pin)
    snapshot = history_snapshot(context)
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: bool) -> None:
        need(value, "reject required source-only control: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (ReferenceError, OSError, ValueError, TypeError,
                UnicodeError, RecursionError, OverflowError):
            rejected.append(name)
            return
        raise ReferenceError("accepted hostile source-only control: " + name)

    with SourceWall() as wall:
        accept("preserve exactly 50 separately counted cases", len(matrix) == 50)
        accept("preserve immutable 13-suite 31,237-case core",
               context["summary"]["full_case_denominator"] == 31237
               and context["summary"]["suite_count"] == 13)
        accept("preserve the historical V33 lower bound of 155 owners and 160 references",
               context["summary"]["repository_evidence_owner_count"] == 155
               and context["summary"]["authenticated_digest_addressed_history_paths"] == 160)
        accept("label historical V1 151 owners and 156 references as historical",
               context["v1"]["actual_published_history"]["actual_history"]
               ["repository_evidence_owner_count"] == 151
               and context["v1"]["actual_published_history"]["actual_history"]
               ["authenticated_history_reference_count"] == 156)
        accept("preserve V33 Rust 1,036 differences and 8,965 verified passes",
               context["summary"]["rust_original_campaign_semantic_mismatch_count"] == 1036
               and context["summary"]["rust_original_campaign_verified_passing_case_count"] == 8965)
        accept("distinguish the historical corrected Zig build from V33 matching",
               context["summary"]["zig_v12_source_build_process_count"] == 26
               and context["summary"]["zig_v12_source_build_matching_test_status"]
               == "NOT MEASURED")
        accept("retain append-only later matching without opening its archive",
               snapshot["authenticated_evidence_owner_lower_bound"] >= 155
               and snapshot["authenticated_history_reference_lower_bound"] >= 160
               and (context["later_zig_matching"] is None
                    or (context["later_zig_matching"]["matching_archive_opened"] is False
                        and context["later_zig_matching"]
                        ["matching_archive_decompressed"] is False)))
        first = synthetic_worker("reference-a", 101, matrix)
        second = synthetic_worker("reference-b", 202, matrix)
        workers = [first, second]
        streams = [synthetic_stream(first), synthetic_stream(second)]
        accept("validate two complete distinct synthetic reference vectors",
               validate_pair(workers, matrix) == first["record_vector_sha256"])
        validate_streams(streams, workers)
        accept("bind complete synthetic stdout and stderr", True)

        for index in range(ADDITIONAL_CASE_COUNT):
            changed = copy.deepcopy(first)
            del changed["records"][index]
            reject("reject missing frozen observation " + str(index),
                   lambda item=changed: validate_worker(item, "reference-a", matrix))
        for field, value in (
            ("schema", "forged"), ("status", "FAIL"), ("role", "reference-b"),
            ("actual_process_id", 0), ("original_case_denominator", 31287),
            ("additional_case_count", 49), ("record_vector_sha256", "0" * 64),
            ("candidate_imports", 1), ("hidden_cases_read", 1),
            ("performance", "FASTER"),
        ):
            changed = copy.deepcopy(first)
            changed[field] = value
            reject("reject forged reference " + field,
                   lambda item=changed: validate_worker(item, "reference-a", matrix))
        for index in (0, 12, 25, 37, 49):
            changed = copy.deepcopy(first)
            changed["records"][index]["member"] = "external_regex_fallback"
            reject("reject replaced frozen signature case " + str(index),
                   lambda item=changed: validate_worker(item, "reference-a", matrix))
        repeated = copy.deepcopy(second)
        repeated["actual_process_id"] = 101
        reject("reject reused worker process IDs",
               lambda: validate_pair([first, repeated], matrix))
        changed = copy.deepcopy(second)
        changed["records"][0]["observation"]["raw_text_signature"] = "(forged)"
        changed["record_vector_sha256"] = validate_observations(changed["records"], matrix)
        reject("reject unequal complete worker vectors",
               lambda: validate_pair([first, changed], matrix))
        reject("reject a third supposed reference worker",
               lambda: validate_pair([first, second, first], matrix))
        reject("reject a single reference worker",
               lambda: validate_pair([first], matrix))
        reject("reject missing original stdout and stderr",
               lambda: validate_streams(streams[:1], workers))
        for field, value in (
            ("role", "reference-b"), ("exit_code", 1),
            ("stdout_sha256", "0" * 64), ("stdout_bytes", 0),
            ("stdout_base64", "Zm9yZ2Vk"),
            ("stderr_sha256", "0" * 64), ("stderr_bytes", 1),
            ("stderr_base64", "!invalid!"),
        ):
            hostile = copy.deepcopy(streams)
            hostile[0][field] = value
            reject("reject forged complete process stream " + field,
                   lambda item=hostile: validate_streams(item, workers))

        partial_archive_name = ZIG_V3_RECEIPT_BASENAME + "-failures.json.gz"
        partial_owner = Owner(
            "oracle/phase2/evidence/" + ZIG_V3_RECEIPT_BASENAME
            + "-failures-publication-receipt.json", "f" * 64, 512,
        )
        partial_receipt = {
            "schema": "rebar-owned-repaired-zig-original-campaign-v3-"
                      "durable-publication-receipt",
            "status": "PASS", "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL", "family": "zig",
            "label": ZIG_V3_LABEL,
            "actual_v12_build_receipt_sha256": ZIG_RECEIPT.sha256,
            "suite_count": CORE_SUITE_COUNT,
            "case_execution_denominator": CORE_CASE_COUNT,
            "named_private_waiver_count": CORE_PRIVATE_WAIVER_COUNT,
            "completed_suite_count": 3, "actual_candidate_workers": 3,
            "verified_passing_case_count": 128,
            "semantic_mismatch_count": "NOT MEASURED",
            "infrastructure_failure_count": 10, "candidate_qualified": False,
            "historical_evidence_owner_count_before_publication": V33_OWNER_COUNT,
            "historical_authenticated_reference_count_before_publication":
                V33_REFERENCE_COUNT,
            "new_repository_evidence_owner_count": 2,
            "resulting_repository_evidence_owner_count": V33_OWNER_COUNT + 2,
            "resulting_authenticated_reference_count": V33_REFERENCE_COUNT + 2,
            "actual_corrected_rust_semantic_mismatch_count": 1036,
            "actual_c_semantic_mismatch_count": 1230,
            "historical_zig_semantic_mismatch_count": 2172,
            "all_original_native_targets_restored": True,
            "restoration_verified_before_publication": True,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
            "archive": {
                "relative": partial_archive_name, "sha256": "a" * 64,
                "exclusive_creation": True, "same_inode_readback_verified": True,
                "file_fsync_completed": True, "directory_fsync_completed": True,
            },
        }
        retained_partial = validate_later_zig_receipt(
            partial_receipt, partial_owner, True,
        )
        accept("preserve an actual partial infrastructure failure without inventing matches",
               retained_partial["completed_suite_count"] == 3
               and retained_partial["actual_candidate_workers"] == 3
               and retained_partial["semantic_mismatch_count"] == "NOT MEASURED"
               and retained_partial["infrastructure_failure_count"] == 10
               and retained_partial["candidate_status"] == "FAIL"
               and retained_partial["matching_archive_opened"] is False)
        for field, value in (
            ("candidate_status", "PASS"),
            ("completed_suite_count", 13),
            ("actual_candidate_workers", 13),
            ("semantic_mismatch_count", 0),
            ("candidate_qualified", True),
            ("infrastructure_failure_count", -1),
            ("publication_pass_means", "CANDIDATE QUALIFIED"),
            ("actual_v12_build_receipt_sha256", "0" * 64),
            ("resulting_repository_evidence_owner_count", 155),
        ):
            forged_partial = copy.deepcopy(partial_receipt)
            forged_partial[field] = value
            reject("reject invented partial matching outcome " + field,
                   lambda item=forged_partial: validate_later_zig_receipt(
                       item, partial_owner, True,
                   ))

        actual_inputs = context["inputs"]
        actual_summary = context["summary"]
        actual_receipt = context["zig_receipt"]
        for target, field, value in (
            ("inputs", "version", 32),
            ("summary", "version", 32),
            ("inputs", "repository_evidence_owner_count", 151),
            ("summary", "repository_evidence_owner_count", 153),
            ("inputs", "all_digest_addressed_history_path_count", 156),
            ("summary", "authenticated_digest_addressed_history_paths", 158),
            ("inputs", "rust_original_campaign_semantic_mismatch_count", 1087),
            ("summary", "rust_original_campaign_semantic_mismatch_count", 0),
            ("summary", "rust_original_campaign_verified_passing_case_count", 7438),
            ("summary", "qualified_candidate_count", 1),
            ("summary", "additional_signature_frozen_case_count", 49),
            ("summary", "additional_signature_reference_cases_executed", 50),
            ("summary", "additional_signature_reference_status", "PASS"),
            ("summary", "full_case_denominator", 31287),
            ("summary", "private_waiver_count", 12),
            ("summary", "zig_v12_source_build_process_count", 25),
            ("summary", "zig_v12_source_build_matching_test_status", "PASS"),
            ("summary", "performance", "FASTER"),
            ("summary", "memory", "MEASURED"),
            ("summary", "final_holdout_opened", True),
            ("summary", "winner_selected", True),
            ("receipt", "actual_compiler_process_count", 25),
            ("receipt", "candidate_correctness", "PASS"),
            ("receipt", "repository_evidence_owner_count_after_publication", 153),
        ):
            changed_inputs = copy.deepcopy(actual_inputs)
            changed_summary = copy.deepcopy(actual_summary)
            changed_receipt = copy.deepcopy(actual_receipt)
            {"inputs": changed_inputs, "summary": changed_summary,
             "receipt": changed_receipt}[target][field] = value
            reject("reject forged current " + target + "." + field,
                   lambda left=changed_inputs, right=changed_summary,
                   receipt=changed_receipt: validate_current(left, right, receipt))

        real_re = sys.modules.get("re")
        probes: list[tuple[str, Any]] = [
            ("filesystem", lambda: os.open(str(ROOT), os.O_RDONLY)),
            ("write", lambda: os.fsync(0)),
            ("process", lambda: subprocess.run((PINNED_PYTHON, "-V"))),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("native", lambda: ctypes.CDLL(None)),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forged")),
            ("locale", lambda: locale.setlocale(locale.LC_ALL)),
        ]
        if real_re is not None:
            probes.append(("regex_matching", lambda: real_re.compile("forged")))
        for category, operation in probes:
            before = wall.blocked[category]
            reject("physically block source-only " + category, operation)
            need(wall.blocked[category] == before + 1,
                 "prove the forbidden source-only effect was intercepted")
        blocked = dict(wall.blocked)
    need(len(rejected) >= 105,
         "require extensive hostile reference, context, and no-effect controls")
    need(all(count > 0 for count in blocked.values()),
         "prove every source-only external-effect barrier")
    return {
        "schema": SCHEMA + "-source-only-self-test", "status": "PASS", "version": 2,
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin, "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "blocked_effects_by_kind": blocked,
        "original_case_denominator": CORE_CASE_COUNT,
        "original_suite_count": CORE_SUITE_COUNT,
        "original_private_waiver_count": CORE_PRIVATE_WAIVER_COUNT,
        "additional_case_count": ADDITIONAL_CASE_COUNT,
        "additional_matrix_sha256": MATRIX_SHA256,
        "historical_v1_evidence_owner_count": 151,
        "historical_v1_authenticated_reference_count": 156,
        "historical_v1_rust_semantic_mismatch_count": 1087,
        "historical_v33_evidence_owner_count": V33_OWNER_COUNT,
        "historical_v33_authenticated_reference_count": V33_REFERENCE_COUNT,
        "historical_v33_rust_semantic_mismatch_count": 1036,
        "historical_v33_rust_verified_passing_case_count": 8965,
        "historical_v33_c_semantic_mismatch_count": 1230,
        "historical_v33_previous_zig_semantic_mismatch_count": 2172,
        "authenticated_evidence_owner_lower_bound":
            snapshot["authenticated_evidence_owner_lower_bound"],
        "authenticated_history_reference_lower_bound":
            snapshot["authenticated_history_reference_lower_bound"],
        "appended_corrected_zig_matching": snapshot["appended_corrected_zig_matching"],
        "corrected_zig_build_process_count": 26,
        "corrected_zig_matching_status":
            context["later_zig_matching"]["candidate_status"]
            if context["later_zig_matching"] else "NOT MEASURED",
        **boundaries(),
    }


def evidence_names(failed: bool) -> tuple[str, str]:
    base = EVIDENCE_BASENAME + ("-failures" if failed else "")
    return base + ".json.gz", base + "-publication-receipt.json"


def open_evidence_directory(*, create: bool) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    root = phase = phase1 = evidence = None
    try:
        root = os.open(str(ROOT), flags)
        phase = os.open("oracle", flags, dir_fd=root)
        phase1 = os.open("phase1", flags, dir_fd=phase)
        try:
            evidence = os.open("evidence", flags, dir_fd=phase1)
        except FileNotFoundError:
            need(create, "require an existing exact private evidence directory")
            try:
                os.mkdir("evidence", 0o700, dir_fd=phase1)
            except FileExistsError:
                pass
            os.fsync(phase1)
            evidence = os.open("evidence", flags, dir_fd=phase1)
        info = os.fstat(evidence)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o700,
             "require a no-follow, owner-only reference evidence directory")
        result, evidence = evidence, None
        return result
    finally:
        for handle in (evidence, phase1, phase, root):
            if handle is not None:
                os.close(handle)


def require_fresh_evidence(directory: int) -> None:
    for failed in (False, True):
        for name in evidence_names(failed):
            try:
                visible = os.stat(name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                continue
            need(False, "never overwrite pre-existing reference evidence: " + name)


def exclusive_publication(directory: int, name: str,
                          raw: bytes) -> dict[str, Any]:
    need(type(directory) is int and directory >= 0
         and type(name) is str and name not in ("", ".", "..")
         and "/" not in name and "\\" not in name
         and type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
         "publish only one bounded, private, explicitly named evidence owner")
    descriptor: int | None = None
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(name, flags, 0o600, dir_fd=directory)
        initial = os.fstat(descriptor)
        need(stat.S_ISREG(initial.st_mode) and initial.st_uid == os.geteuid()
             and initial.st_nlink == 1 and stat.S_IMODE(initial.st_mode) == 0o600,
             "create only a fresh owner-only, unlinked evidence inode")
        cursor = 0
        while cursor < len(raw):
            amount = os.write(descriptor, raw[cursor:])
            need(type(amount) is int and amount > 0,
                 "publish every original evidence byte")
            cursor += amount
        os.fsync(descriptor)
        complete = os.fstat(descriptor)
        need((initial.st_dev, initial.st_ino, initial.st_uid, initial.st_nlink)
             == (complete.st_dev, complete.st_ino, complete.st_uid, complete.st_nlink)
             and complete.st_size == len(raw),
             "reject substituted or incomplete synchronized reference evidence")
        os.close(descriptor)
        descriptor = None
        verify = os.open(name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        try:
            observed = os.fstat(verify)
            need((observed.st_dev, observed.st_ino, observed.st_size,
                  observed.st_uid, observed.st_nlink)
                 == (complete.st_dev, complete.st_ino, complete.st_size,
                     complete.st_uid, complete.st_nlink),
                 "require exact same-inode publication readback")
            hasher = hashlib.sha256()
            total = 0
            while True:
                part = os.read(verify, 65536)
                if not part:
                    break
                total += len(part)
                need(total <= MAX_REPORT_BYTES, "bound durable evidence readback")
                hasher.update(part)
            need(total == len(raw) and hasher.hexdigest() == digest(raw),
                 "reject incomplete or substituted durable reference bytes")
        finally:
            os.close(verify)
        os.fsync(directory)
        return {
            "path": EVIDENCE_DIRECTORY + "/" + name,
            "sha256": digest(raw), "bytes": len(raw),
            "device": complete.st_dev, "inode": complete.st_ino,
            "uid": complete.st_uid, "nlink": complete.st_nlink,
            "mode": "0600", "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)


def build_reference_report(source_pin: str, protocol_pin: str,
                           contract_pin: str,
                           matrix: list[dict[str, Any]],
                           snapshot: Mapping[str, Any]) -> dict[str, Any]:
    workers: list[dict[str, Any]] = []
    streams: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    environment = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "PYTHONHASHSEED": "0"}
    for role in REFERENCE_ROLES:
        arguments = (PINNED_PYTHON, "-I", "-B", str(ROOT / V1_SOURCE.path),
                     "--reference-worker", "--reference-role", role,
                     "--source-sha256", V1_SOURCE.sha256,
                     "--protocol-sha256", V1_PROTOCOL.sha256,
                     "--contract-sha256", V1_CONTRACT.sha256)
        try:
            process = subprocess.run(arguments, capture_output=True,
                                     check=False, env=environment, timeout=60)
            stdout, stderr = process.stdout, process.stderr
            streams.append(capture_stream(role, process.returncode, stdout, stderr))
            need(process.returncode == 0,
                 "isolated standard-library reference exited unsuccessfully")
            worker = strict_document(stdout, role + " complete canonical stdout")
            validate_worker(worker, role, matrix)
            workers.append(worker)
        except (ReferenceError, OSError, subprocess.SubprocessError,
                ValueError, TypeError, UnicodeError, RecursionError) as error:
            if isinstance(error, subprocess.TimeoutExpired):
                stdout = error.stdout if type(error.stdout) is bytes else b""
                stderr = error.stderr if type(error.stderr) is bytes else b""
                streams.append(capture_stream(role, 124, stdout, stderr))
            failures.append({"role": role, "error_class": type(error).__name__,
                             "error": str(error)})
    vector: str | None = None
    if not failures:
        try:
            vector = validate_pair(workers, matrix)
            validate_streams(streams, workers)
        except (ReferenceError, ValueError, TypeError, UnicodeError) as error:
            failures.append({"role": "reference-pair",
                             "error_class": type(error).__name__,
                             "error": str(error)})
    passed = not failures
    return {
        "schema": SCHEMA + "-actual-two-reference-baseline",
        "version": 2, "status": "PASS" if passed else "FAIL",
        "python": "3.14.6", "source_sha256": source_pin,
        "protocol_sha256": protocol_pin, "contract_sha256": contract_pin,
        "frozen_v1_source_sha256": V1_SOURCE.sha256,
        "frozen_v1_protocol_sha256": V1_PROTOCOL.sha256,
        "frozen_v1_contract_sha256": V1_CONTRACT.sha256,
        "original_case_denominator": CORE_CASE_COUNT,
        "original_suite_count": CORE_SUITE_COUNT,
        "original_private_waiver_count": CORE_PRIVATE_WAIVER_COUNT,
        "additional_case_count": ADDITIONAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "matrix_sha256": MATRIX_SHA256,
        "reference_roles": list(REFERENCE_ROLES),
        "actual_reference_processes_started": len(streams),
        "actual_distinct_process_ids": [worker["actual_process_id"] for worker in workers],
        "record_vector_sha256": vector,
        "reference_workers": workers,
        "complete_reference_streams": streams,
        "failures": failures,
        "historical_v1_evidence_owner_count": 151,
        "historical_v1_authenticated_reference_count": 156,
        "historical_v1_rust_semantic_mismatch_count": 1087,
        "historical_v33_evidence_owner_count": V33_OWNER_COUNT,
        "historical_v33_history_reference_count": V33_REFERENCE_COUNT,
        "historical_v33_rust_semantic_mismatch_count": 1036,
        "historical_v33_rust_verified_passing_case_count": 8965,
        "authenticated_evidence_owner_lower_bound_before_publication":
            snapshot["authenticated_evidence_owner_lower_bound"],
        "authenticated_history_reference_lower_bound_before_publication":
            snapshot["authenticated_history_reference_lower_bound"],
        "appended_corrected_zig_matching":
            snapshot["appended_corrected_zig_matching"],
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "matching_archives_opened": 0,
        "source_build_archives_decompressed": 0,
        "hidden_cases_read": 0,
        "holdout_cases_read": 0,
        "final_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "candidate_introspection": "NOT MEASURED",
        "candidate_qualified": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def publish_report(report: dict[str, Any], directory: int) -> dict[str, Any]:
    need(report.get("status") in {"PASS", "FAIL"},
         "never hide the actual Python-reference result")
    failed = report["status"] == "FAIL"
    archive_name, receipt_name = evidence_names(failed)
    plain = canonical(report)
    need(len(plain) <= MAX_REPORT_BYTES,
         "bound the full independently observed reference report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    need(0 < len(compressed) <= MAX_REPORT_BYTES,
         "bound deterministic compressed reference publication")
    archive = exclusive_publication(directory, archive_name, compressed)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt", "version": 2,
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "EVIDENCE PUBLICATION ONLY",
        "reference_status": report["status"],
        "failure_preserved": failed,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "frozen_v1_source_sha256": V1_SOURCE.sha256,
        "frozen_v1_protocol_sha256": V1_PROTOCOL.sha256,
        "frozen_v1_contract_sha256": V1_CONTRACT.sha256,
        "archive": archive,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "gzip_mtime": 0,
        "original_case_denominator": CORE_CASE_COUNT,
        "original_suite_count": CORE_SUITE_COUNT,
        "original_private_waiver_count": CORE_PRIVATE_WAIVER_COUNT,
        "additional_case_count": ADDITIONAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "matrix_sha256": MATRIX_SHA256,
        "actual_reference_processes_started": report["actual_reference_processes_started"],
        "actual_distinct_process_ids": report["actual_distinct_process_ids"],
        "reference_failure_count": len(report["failures"]),
        "historical_v1_evidence_owner_count": 151,
        "historical_v1_authenticated_reference_count": 156,
        "historical_v1_rust_semantic_mismatch_count": 1087,
        "historical_v33_evidence_owner_count": V33_OWNER_COUNT,
        "historical_v33_history_reference_count": V33_REFERENCE_COUNT,
        "authenticated_evidence_owner_lower_bound_before_publication":
            report["authenticated_evidence_owner_lower_bound_before_publication"],
        "authenticated_history_reference_lower_bound_before_publication":
            report["authenticated_history_reference_lower_bound_before_publication"],
        "new_actual_evidence_owner_count": 2,
        "minimum_evidence_owner_count_after_publication":
            report["authenticated_evidence_owner_lower_bound_before_publication"] + 2,
        "minimum_history_reference_count_after_publication":
            report["authenticated_history_reference_lower_bound_before_publication"] + 2,
        "historical_v33_rust_semantic_mismatch_count": 1036,
        "historical_v33_rust_verified_passing_case_count": 8965,
        "appended_corrected_zig_matching": report["appended_corrected_zig_matching"],
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "matching_archives_opened": 0,
        "source_build_archives_decompressed": 0,
        "holdout_cases_read": 0, "final_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "candidate_introspection": "NOT MEASURED", "candidate_qualified": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False, "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_owner = exclusive_publication(directory, receipt_name, canonical(receipt))
    return {
        "schema": SCHEMA + "-actual-publication-result", "version": 2,
        "status": report["status"], "publication_status": "PASS",
        "publication_pass_means": "EVIDENCE PUBLICATION ONLY",
        "reference_status": report["status"],
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "original_case_denominator": CORE_CASE_COUNT,
        "additional_case_count": ADDITIONAL_CASE_COUNT,
        "actual_reference_processes_started": report["actual_reference_processes_started"],
        "actual_distinct_process_ids": report["actual_distinct_process_ids"],
        "reference_failure_count": len(report["failures"]),
        "record_vector_sha256": report["record_vector_sha256"],
        "archive": archive, "receipt": receipt_owner,
        "new_actual_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound_before_publication":
            report["authenticated_evidence_owner_lower_bound_before_publication"],
        "authenticated_history_reference_lower_bound_before_publication":
            report["authenticated_history_reference_lower_bound_before_publication"],
        "minimum_evidence_owner_count_after_publication":
            report["authenticated_evidence_owner_lower_bound_before_publication"] + 2,
        "minimum_history_reference_count_after_publication":
            report["authenticated_history_reference_lower_bound_before_publication"] + 2,
        "appended_corrected_zig_matching": report["appended_corrected_zig_matching"],
        "candidate_processes_started": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def run_reference(source_pin: str, protocol_pin: str,
                  contract_pin: str) -> tuple[int, dict[str, Any]]:
    _, matrix, context = verify_context(source_pin, protocol_pin, contract_pin)
    snapshot = history_snapshot(context)
    directory = open_evidence_directory(create=True)
    try:
        require_fresh_evidence(directory)
        report = build_reference_report(source_pin, protocol_pin, contract_pin,
                                        matrix, snapshot)
        result = publish_report(report, directory)
        return (0 if report["status"] == "PASS" else 1), result
    finally:
        os.close(directory)


def context_result(source_pin: str, protocol_pin: str,
                   contract_pin: str) -> dict[str, Any]:
    _, matrix, context = verify_context(source_pin, protocol_pin, contract_pin)
    snapshot = history_snapshot(context)
    return {
        "schema": SCHEMA + "-actual-read-only-frozen-context",
        "version": 2, "status": "PASS",
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "authenticated_frozen_v2_owner_count": 3,
        "authenticated_frozen_v1_owner_count": 3,
        "authenticated_v33_graph_owner_count": 4,
        "authenticated_corrected_zig_receipt_owner_count": 1,
        "authenticated_raw_corrected_zig_archive_owner_count": 1,
        "original_case_denominator": CORE_CASE_COUNT,
        "original_suite_count": CORE_SUITE_COUNT,
        "original_private_waiver_count": CORE_PRIVATE_WAIVER_COUNT,
        "additional_case_count": ADDITIONAL_CASE_COUNT,
        "additional_matrix_sha256": validate_matrix(matrix),
        "historical_v1_evidence_owner_count": 151,
        "historical_v1_authenticated_reference_count": 156,
        "historical_v1_rust_semantic_mismatch_count": 1087,
        "historical_v33_evidence_owner_count": V33_OWNER_COUNT,
        "historical_v33_authenticated_reference_count": V33_REFERENCE_COUNT,
        "historical_v33_rust_semantic_mismatch_count": 1036,
        "historical_v33_rust_verified_passing_case_count": 8965,
        "historical_v33_c_semantic_mismatch_count": 1230,
        "historical_v33_previous_zig_semantic_mismatch_count": 2172,
        "authenticated_evidence_owner_lower_bound":
            snapshot["authenticated_evidence_owner_lower_bound"],
        "authenticated_history_reference_lower_bound":
            snapshot["authenticated_history_reference_lower_bound"],
        "appended_corrected_zig_matching": snapshot["appended_corrected_zig_matching"],
        "corrected_zig_build_status": "PASS",
        "corrected_zig_build_process_count": 26,
        "corrected_zig_matching_status":
            context["later_zig_matching"]["candidate_status"]
            if context["later_zig_matching"] else "NOT MEASURED",
        **boundaries(),
    }


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    switches = [value for value in values if value.startswith("--")]
    need(len(switches) == len(set(switches)),
         "reject repeated or ambiguous reference authorizations")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run-reference", "--run", action="store_true",
                       dest="run_reference")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "V2 source")
    checked_digest(options.protocol_sha256, "V2 protocol")
    if options.emit_contract:
        need(options.contract_sha256 is None,
             "never guess a machine contract's own digest")
    else:
        checked_digest(options.contract_sha256, "V2 contract")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.emit_contract:
            result, _, _ = verify_context(options.source_sha256,
                                          options.protocol_sha256)
            exit_code = 0
        elif options.self_test:
            result = self_test(options.source_sha256, options.protocol_sha256,
                               options.contract_sha256)
            exit_code = 0
        elif options.verify_frozen_context:
            result = context_result(options.source_sha256, options.protocol_sha256,
                                    options.contract_sha256)
            exit_code = 0
        else:
            exit_code, result = run_reference(options.source_sha256,
                                              options.protocol_sha256,
                                              options.contract_sha256)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return exit_code
    except (ReferenceError, OSError, subprocess.SubprocessError,
            ValueError, TypeError, UnicodeError, RecursionError,
            OverflowError, AttributeError, KeyError) as error:
        sys.stderr.write("OWNED CALLABLE REFERENCE V2: FAIL: "
                         + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
