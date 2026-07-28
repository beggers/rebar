#!/usr/bin/env python3
"""Show two real extra Python references without changing original test totals."""

from __future__ import annotations

import argparse
import base64
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
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_candidate_current_overview_v35.py"
OUTPUT = "docs/evidence/candidate-current-overview-v35"
SCHEMA = "rebar-candidate-current-overview-v35"
LIMIT = 8 * 1024 * 1024
REFERENCE_LIMIT = 256 * 1024
V34 = {
    "source": (
        "tools/render_candidate_current_overview_v34.py",
        "cf4f7b0749d0e3aa6c15d4e5444762441265773fbb90c1ebbceff0f65e3e841f",
        79364,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v34.inputs.json",
        "d191ad36dd230b97c3d017f0d775a185c0a7f449adb27f7412c54c4d4308c8fc",
        133398,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v34.json",
        "09236e77646160009b322bb02f60652eeb0b13f2b1f9440bfef2e176644e9df4",
        426458,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v34.svg",
        "59ff6affa120980c8d25206a71d2b2377619e93796a6ca0f15a65229a87dffce",
        10367,
    ),
}
REFERENCE_SOURCE = (
    "tools/run_owned_callable_introspection_reference_v2.py",
    "00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4",
    86258,
)
REFERENCE_PROTOCOL = (
    "oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md",
    "1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f",
    7487,
)
REFERENCE_CONTRACT = (
    "oracle/phase1/callable-introspection-reference-v2.json",
    "0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42",
    7253,
)
FROZEN_MATRIX = (
    "oracle/phase1/p0-callable-introspection-v1.json",
    "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
    14749,
)
FROZEN_SOURCE = (
    "tools/verify_python_re_callable_introspection_v1.py",
    "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653",
    75608,
)
FROZEN_PROTOCOL = (
    "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
    "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
    8952,
)
ARCHIVE = (
    "oracle/phase1/evidence/"
    "callable-introspection-reference-v2-cpython-3.14.6.json.gz",
    "7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c",
    8538,
    2064,
    524689,
)
RECEIPT = (
    "oracle/phase1/evidence/"
    "callable-introspection-reference-v2-cpython-3.14.6-"
    "publication-receipt.json",
    "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334",
    3533,
    2064,
    524690,
)
PLAIN_SHA = "cacf306a64fc4e68686b64895ee24b076b9be87efd778b94967c5e2adb662ef0"
PLAIN_BYTES = 152530
MATRIX_SHA = "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
VECTOR_SHA = "b32f2ea83213686a8b97d63a15ba5c83d323c2dee1f831bab41176544d6adb0a"
REFERENCE_ROLES = ("reference-a", "reference-b")
REFERENCE_PIDS = (81, 82)
ZIG_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-"
    "v2-original-p0-failures-publication-receipt.json",
    "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96",
    4111,
)
ZIG_MATCHING_ARCHIVE_SHA = (
    "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b"
)


class GraphError(Exception):
    """Reject fabricated references, changed denominators, or measurements."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)


def digest(value: bytes) -> str:
    need(type(value) is bytes, "hash only exact evidence or matrix bytes")
    return hashlib.sha256(value).hexdigest()


def checked(value: object, label: str) -> str:
    need(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "require an exact lowercase SHA-256 for " + label,
    )
    return value


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                separators=(",", ":"),
            ) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GraphError("reject noncanonical V35 reference evidence") from error


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        observed: dict[str, object] = {}
        for key, value in items:
            need(key not in observed, "reject duplicate JSON keys in " + label)
            observed[key] = value
        return observed

    try:
        decoded = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("reject nonfinite JSON in " + label)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed " + label) from error
    need(type(decoded) is dict and canonical(decoded) == raw,
         "require the complete original canonical " + label)
    return decoded


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "require the exact isolated stable CPython 3.14.6 reference",
    )


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "bound a pinned first-party graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def read_owner(
    path: str, fingerprint: str, size: int, *, private: bool = False,
    device: int | None = None, inode: int | None = None,
) -> tuple[bytes, dict]:
    need(
        type(path) is str and bool(path) and not path.startswith("/")
        and "." not in Path(path).parts and ".." not in Path(path).parts,
        "reject an absolute, escaped or replaced first-party owner",
    )
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "bound authentic owner bytes for " + path)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directories: list[int] = []
    handle: int | None = None
    try:
        directories.append(os.open(str(ROOT), directory_flags))
        for part in Path(path).parts[:-1]:
            directories.append(os.open(part, directory_flags,
                                       dir_fd=directories[-1]))
        handle = os.open(Path(path).parts[-1], file_flags,
                         dir_fd=directories[-1])
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1 and before.st_size == size
            and (not private or stat.S_IMODE(before.st_mode) == 0o600)
            and (device is None or before.st_dev == device)
            and (inode is None or before.st_ino == inode),
            "reject partial, foreign, linked or nonprivate owner " + path,
        )
        parts: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            need(bool(piece), "reject an incomplete exact owner " + path)
            parts.append(piece)
            remaining -= len(piece)
        need(os.read(handle, 1) == b"", "reject trailing exact owner " + path)
        raw = b"".join(parts)
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
            and digest(raw) == fingerprint,
            "reject owner bytes or inode changed while reading " + path,
        )
        return raw, {
            "path": path, "sha256": fingerprint, "bytes": size,
            "device": after.st_dev, "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "nlink": after.st_nlink, "uid": after.st_uid,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for directory in reversed(directories):
            os.close(directory)


def load_v34() -> types.ModuleType:
    raw, _ = read_owner(*V34["source"])
    previous = types.ModuleType("_rebar_immutable_v34_for_reference_graph_v35")
    previous.__file__ = str(ROOT / V34["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    need(
        previous.SCHEMA == "rebar-candidate-current-overview-v34"
        and previous.SELF == V34["source"][0]
        and previous.RECEIPT[1] == ZIG_RECEIPT[1]
        and previous.ARCHIVE[1] == ZIG_MATCHING_ARCHIVE_SHA,
        "load only the actual immutable corrected-Zig compatibility graph",
    )
    return previous


def authenticate_v34() -> tuple[dict, dict]:
    previous = load_v34()
    inputs_raw, _ = read_owner(*V34["inputs"], private=True)
    summary_raw, _ = read_owner(*V34["summary"], private=True)
    image_raw, _ = read_owner(*V34["svg"], private=True)
    inputs = document(inputs_raw, "committed V34 graph inputs")
    summary = document(summary_raw, "committed V34 graph summary")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "retain the complete authentic V34 snapshot")
    previous.validate(snapshot)
    need(
        image_raw == previous.make_svg(snapshot, V34["source"][1],
                                       V34["inputs"][1])
        and summary.get("schema") == previous.SCHEMA + "-summary"
        and summary.get("version") == 34 and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count") == 157
        and summary.get("authenticated_digest_addressed_history_paths") == 162
        and summary.get("suite_count") == 13
        and summary.get("full_case_denominator") == 31237
        and summary.get("private_waiver_count") == 13
        and summary.get("qualified_candidate_count") == 0
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
        and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 1764
        and summary.get("zig_original_campaign_verified_passing_case_count") == 3711
        and summary.get("zig_original_campaign_candidate_worker_count") == 13
        and summary.get("zig_original_campaign_infrastructure_failure_count") == 0
        and summary.get("historical_zig_semantic_mismatch_count") == 2172
        and summary.get("zig_semantic_mismatch_reduction") == 408
        and summary.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and summary.get("native_source_build_independence") == "VERIFIED"
        and summary.get("additional_signature_frozen_case_count") == 50
        and summary.get("additional_signature_reference_status") == "NOT RUN"
        and inputs.get("repository_evidence_owner_count") == 157
        and inputs.get("all_digest_addressed_history_path_count") == 162,
        "authenticate all immutable V34 claims without opening matching archives",
    )
    return summary, inputs


def validate_matrix(matrix: object) -> list[dict]:
    need(type(matrix) is list and len(matrix) == 50,
         "require exactly 50 separately frozen public-signature cases")
    identifiers: set[str] = set()
    counts = {"module": 0, "pattern": 0, "match": 0, "scanner": 0}
    for item in matrix:
        need(
            type(item) is dict
            and set(item) == {"id", "category", "owner", "binding", "member"}
            and all(type(item[key]) is str for key in item)
            and item["id"] not in identifiers
            and item["category"] in counts,
            "reject a duplicate, omitted or forged additional signature case",
        )
        identifiers.add(item["id"])
        counts[item["category"]] += 1
    need(
        counts == {"module": 11, "pattern": 18, "match": 14, "scanner": 7}
        and digest(canonical(matrix)) == MATRIX_SHA,
        "bind all 50 cases to the exact independently frozen matrix",
    )
    return matrix


def validate_observations(records: object, matrix: list[dict]) -> str:
    need(type(records) is list and len(records) == 50,
         "retain all 50 genuine reference observations")
    for index, (case, item) in enumerate(zip(matrix, records, strict=True)):
        need(
            type(item) is dict
            and set(item) == set(case) | {"observation"}
            and all(item.get(key) == value for key, value in case.items())
            and type(item.get("observation")) is dict,
            "reject forged or reordered signature observation " + str(index),
        )
        observed = item["observation"]
        need(
            type(observed.get("text_signature_present")) is bool
            and (observed.get("raw_text_signature") is None
                 or type(observed.get("raw_text_signature")) is str),
            "preserve the complete Python callable text signature",
        )
        if observed.get("status") == "INSPECTABLE":
            need(
                set(observed)
                == {"status", "parameters", "return_annotation",
                    "text_signature_present", "raw_text_signature"}
                and type(observed.get("parameters")) is list
                and type(observed.get("return_annotation")) is dict,
                "reject incomplete callable signature metadata",
            )
            for parameter in observed["parameters"]:
                need(
                    type(parameter) is dict
                    and set(parameter)
                    == {"parameter_name", "parameter_kind",
                        "normalized_default", "annotation"}
                    and type(parameter.get("parameter_name")) is str
                    and parameter.get("parameter_kind")
                    in {"POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD",
                        "VAR_POSITIONAL", "KEYWORD_ONLY", "VAR_KEYWORD"}
                    and type(parameter.get("normalized_default")) is dict
                    and type(parameter.get("annotation")) is dict,
                    "preserve every real positional and annotated parameter",
                )
        else:
            need(
                observed.get("status") == "UNINSPECTABLE"
                and set(observed)
                == {"status", "signature_error_class",
                    "text_signature_present", "raw_text_signature"}
                and observed.get("signature_error_class")
                in {"TypeError", "ValueError"},
                "reject fabricated uninspectable public-callable outcomes",
            )
    actual = digest(canonical(records))
    need(actual == VECTOR_SHA,
         "compute the real 50-case signature vector from complete observations")
    return actual


def authenticate_reference_report(compressed: bytes) -> tuple[dict, list[dict]]:
    need(
        type(compressed) is bytes and len(compressed) == ARCHIVE[2]
        and compressed[:3] == b"\x1f\x8b\x08"
        and struct.unpack("<I", compressed[4:8])[0] == 0
        and struct.unpack("<I", compressed[-4:])[0] == PLAIN_BYTES
        and PLAIN_BYTES < REFERENCE_LIMIT,
        "inflate only the frozen 152,530-byte Python-reference gzip",
    )
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        raw = decoder.decompress(compressed, REFERENCE_LIMIT + 1)
    except zlib.error as error:
        raise GraphError("reject corrupted bounded reference evidence") from error
    need(
        decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
        and len(raw) == PLAIN_BYTES and digest(raw) == PLAIN_SHA,
        "reject concatenated, truncated or oversized signature-reference gzip",
    )
    report = document(raw, "complete actual two-process reference report")
    matrix_raw, _ = read_owner(*FROZEN_MATRIX)
    frozen = document(matrix_raw, "separately frozen original signature matrix")
    obligation = frozen.get("additional_obligation")
    need(
        type(obligation) is dict and obligation.get("case_count") == 50
        and obligation.get("matrix_sha256") == MATRIX_SHA
        and obligation.get("included_in_original_31237_denominator") is False,
        "keep the separately frozen signature matrix outside the original total",
    )
    matrix = validate_matrix(obligation.get("case_matrix"))
    workers = report.get("reference_workers")
    streams = report.get("complete_reference_streams")
    need(
        type(workers) is list and len(workers) == 2
        and type(streams) is list and len(streams) == 2
        and report.get("reference_roles") == list(REFERENCE_ROLES)
        and report.get("actual_distinct_process_ids") == list(REFERENCE_PIDS),
        "require the two actually recorded independent reference workers",
    )
    vectors: list[str] = []
    for index, (worker, stream) in enumerate(zip(workers, streams, strict=True)):
        role = REFERENCE_ROLES[index]
        need(
            type(worker) is dict
            and worker.get("schema")
            == "rebar-python-re-callable-introspection-v1-reference-worker"
            and worker.get("status") == "PASS"
            and worker.get("role") == role
            and worker.get("actual_process_id") == REFERENCE_PIDS[index]
            and worker.get("original_case_denominator") == 31237
            and worker.get("additional_case_count") == 50
            and worker.get("candidate_imports") == 0
            and worker.get("hidden_cases_read") == 0
            and worker.get("performance") == "NOT MEASURED",
            "authenticate actual reference process " + role,
        )
        vector = validate_observations(worker.get("records"), matrix)
        need(worker.get("record_vector_sha256") == vector,
             "reject a reference vector not backed by all 50 cases")
        vectors.append(vector)
        need(
            type(stream) is dict and stream.get("role") == role
            and stream.get("exit_code") == 0,
            "retain successful complete original reference process streams",
        )
        for channel in ("stdout", "stderr"):
            encoded = stream.get(channel + "_base64")
            need(type(encoded) is str, "retain the original reference stream")
            try:
                observed = base64.b64decode(encoded.encode("ascii"),
                                            validate=True)
            except (ValueError, UnicodeError) as error:
                raise GraphError("reject fabricated reference process output") from error
            need(
                stream.get(channel + "_bytes") == len(observed)
                and stream.get(channel + "_sha256") == digest(observed),
                "bind every original Python-reference output byte",
            )
            if channel == "stdout":
                need(observed == canonical(worker),
                     "bind the full observed signature worker to its stdout")
            else:
                need(observed == b"",
                     "reject concealed Python-reference worker failures")
    need(
        vectors == [VECTOR_SHA, VECTOR_SHA]
        and workers[0]["actual_process_id"] != workers[1]["actual_process_id"]
        and workers[0]["records"] == workers[1]["records"],
        "prove 50 agreeing observations from two distinct real processes",
    )
    return report, workers


def authenticate_reference_v2(
    archive_pin: str, receipt_pin: str, previous: dict,
) -> tuple[dict, dict[str, str]]:
    need(
        checked(archive_pin, "actual additional Python reference archive")
        == ARCHIVE[1]
        and checked(receipt_pin, "actual additional Python reference receipt")
        == RECEIPT[1],
        "caller-pin both actually published additional-reference owners",
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
        != (receipt_owner["device"], receipt_owner["inode"]),
        "require two genuinely distinct private Python-reference owners",
    )
    receipt = document(receipt_raw, "actual additional-reference publication receipt")
    claimed = receipt.get("archive")
    need(
        type(claimed) is dict and claimed.get("path") == ARCHIVE[0]
        and claimed.get("sha256") == archive["sha256"]
        and claimed.get("bytes") == archive["bytes"]
        and claimed.get("device") == archive["device"]
        and claimed.get("inode") == archive["inode"]
        and claimed.get("mode") == "0600"
        and claimed.get("uid") == archive["uid"]
        and claimed.get("nlink") == 1
        and claimed.get("exclusive_creation") is True
        and claimed.get("same_inode_readback_verified") is True
        and claimed.get("file_fsync_completed") is True
        and claimed.get("directory_fsync_completed") is True,
        "bind the durable reference receipt to its exact private gzip owner",
    )
    need(
        receipt.get("schema")
        == "rebar-owned-callable-introspection-reference-v2-"
        "durable-publication-receipt"
        and receipt.get("version") == 2
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("publication_pass_means") == "EVIDENCE PUBLICATION ONLY"
        and receipt.get("reference_status") == "PASS"
        and receipt.get("failure_preserved") is False
        and receipt.get("source_sha256") == REFERENCE_SOURCE[1]
        and receipt.get("protocol_sha256") == REFERENCE_PROTOCOL[1]
        and receipt.get("contract_sha256") == REFERENCE_CONTRACT[1]
        and receipt.get("frozen_v1_source_sha256") == FROZEN_SOURCE[1]
        and receipt.get("frozen_v1_protocol_sha256") == FROZEN_PROTOCOL[1]
        and receipt.get("frozen_v1_contract_sha256") == FROZEN_MATRIX[1]
        and receipt.get("uncompressed_sha256") == PLAIN_SHA
        and receipt.get("uncompressed_bytes") == PLAIN_BYTES
        and receipt.get("gzip_mtime") == 0,
        "distinguish durable publication from the authentic Python reference result",
    )
    need(
        receipt.get("original_case_denominator") == 31237
        and receipt.get("original_suite_count") == 13
        and receipt.get("original_private_waiver_count") == 13
        and receipt.get("additional_case_count") == 50
        and receipt.get("additional_cases_included_in_original_denominator")
        is False
        and receipt.get("matrix_sha256") == MATRIX_SHA
        and receipt.get("actual_reference_processes_started") == 2
        and receipt.get("actual_distinct_process_ids") == list(REFERENCE_PIDS)
        and receipt.get("reference_failure_count") == 0
        and receipt.get("authenticated_evidence_owner_lower_bound_before_publication")
        == 157
        and receipt.get("authenticated_history_reference_lower_bound_before_publication")
        == 162
        and receipt.get("new_actual_evidence_owner_count") == 2
        and receipt.get("minimum_evidence_owner_count_after_publication") == 159
        and receipt.get("minimum_history_reference_count_after_publication") == 164
        and "record_vector_sha256" not in receipt,
        "keep 50 additive Python-only checks outside the original denominator",
    )
    need(
        receipt.get("candidate_introspection") == "NOT MEASURED"
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("candidate_imports") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("matching_archives_opened") == 0
        and receipt.get("source_build_archives_decompressed") == 0
        and receipt.get("holdout_cases_read") == 0
        and receipt.get("final_cases_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("undefined_behavior") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "never confuse a Python reference with candidate execution or performance",
    )
    appended = receipt.get("appended_corrected_zig_matching")
    need(
        type(appended) is dict
        and appended.get("candidate_status") == "FAIL"
        and appended.get("semantic_mismatch_count") == 1764
        and appended.get("verified_passing_case_count") == 3711
        and appended.get("actual_candidate_workers") == 13
        and appended.get("completed_suite_count") == 13
        and appended.get("infrastructure_failure_count") == 0
        and appended.get("candidate_qualified") is False
        and appended.get("matching_archive_opened") is False
        and appended.get("matching_archive_decompressed") is False
        and appended.get("matching_archive_metadata_sha256")
        == ZIG_MATCHING_ARCHIVE_SHA
        and appended.get("evidence_owner_lower_bound") == 157
        and appended.get("history_reference_lower_bound") == 162
        and type(appended.get("receipt")) is dict
        and appended["receipt"].get("path") == ZIG_RECEIPT[0]
        and appended["receipt"].get("sha256") == ZIG_RECEIPT[1]
        and appended["receipt"].get("bytes") == ZIG_RECEIPT[2],
        "bind additional references to the actual latest corrected Zig failure",
    )
    _, source = read_owner(*REFERENCE_SOURCE)
    _, protocol = read_owner(*REFERENCE_PROTOCOL)
    frozen_raw, contract = read_owner(*REFERENCE_CONTRACT)
    frozen = document(frozen_raw, "exact separately frozen Python-reference contract")
    core = frozen.get("original_core")
    extra = frozen.get("frozen_additional_oracle")
    policy = frozen.get("future_reference_policy")
    publication = frozen.get("future_durable_publication")
    need(
        frozen.get("schema")
        == "rebar-owned-callable-introspection-reference-v2-source-freeze"
        and frozen.get("version") == 2
        and frozen.get("source")
        == {"path": REFERENCE_SOURCE[0], "sha256": REFERENCE_SOURCE[1]}
        and frozen.get("protocol")
        == {"path": REFERENCE_PROTOCOL[0], "sha256": REFERENCE_PROTOCOL[1]}
        and type(core) is dict
        and core.get("case_execution_denominator") == 31237
        and core.get("suite_count") == 13
        and core.get("named_private_waiver_count") == 13
        and core.get("denominator_modified") is False
        and type(extra) is dict
        and extra.get("matrix_sha256") == MATRIX_SHA
        and extra.get("separately_counted_case_count") == 50
        and extra.get("included_in_original_core_denominator") is False,
        "preserve the immutable 31,237-case oracle and the separate 50-case matrix",
    )
    need(
        type(policy) is dict
        and policy.get("reference_roles") == list(REFERENCE_ROLES)
        and policy.get("exact_distinct_isolated_worker_process_count") == 2
        and policy.get("different_actual_process_ids_required") is True
        and policy.get("identical_complete_case_vectors_required") is True
        and policy.get("candidate_execution_allowed") is False
        and type(publication) is dict
        and publication.get("gzip_mtime") == 0
        and publication.get("new_evidence_owner_count") == 2
        and publication.get("durable_receipt_pass_means")
        == "EVIDENCE PUBLICATION ONLY",
        "require the frozen independent-reference and durable-publication policy",
    )
    report, workers = authenticate_reference_report(compressed)
    need(
        report.get("schema")
        == "rebar-owned-callable-introspection-reference-v2-"
        "actual-two-reference-baseline"
        and report.get("version") == 2
        and report.get("status") == "PASS"
        and report.get("python") == "3.14.6"
        and report.get("source_sha256") == REFERENCE_SOURCE[1]
        and report.get("protocol_sha256") == REFERENCE_PROTOCOL[1]
        and report.get("contract_sha256") == REFERENCE_CONTRACT[1]
        and report.get("frozen_v1_source_sha256") == FROZEN_SOURCE[1]
        and report.get("frozen_v1_protocol_sha256") == FROZEN_PROTOCOL[1]
        and report.get("frozen_v1_contract_sha256") == FROZEN_MATRIX[1]
        and report.get("original_case_denominator") == 31237
        and report.get("original_suite_count") == 13
        and report.get("original_private_waiver_count") == 13
        and report.get("additional_case_count") == 50
        and report.get("additional_cases_included_in_original_denominator")
        is False
        and report.get("matrix_sha256") == MATRIX_SHA
        and report.get("record_vector_sha256") == VECTOR_SHA
        and report.get("actual_reference_processes_started") == 2
        and report.get("actual_distinct_process_ids") == list(REFERENCE_PIDS)
        and report.get("failures") == []
        and report.get("appended_corrected_zig_matching") == appended,
        "prove the complete authentic two-process reference and vector",
    )
    need(
        report.get("candidate_processes_started") == 0
        and report.get("candidate_imports") == 0
        and report.get("native_libraries_loaded") == 0
        and report.get("matching_archives_opened") == 0
        and report.get("source_build_archives_decompressed") == 0
        and report.get("hidden_cases_read") == 0
        and report.get("holdout_cases_read") == 0
        and report.get("final_cases_read") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("candidate_introspection") == "NOT MEASURED"
        and report.get("candidate_qualified") is False
        and report.get("performance") == "NOT MEASURED"
        and report.get("memory") == "NOT MEASURED"
        and report.get("undefined_behavior") == "NOT MEASURED"
        and report.get("confidence_intervals") == "NOT MEASURED"
        and report.get("holdout") == "NOT OPENED"
        and report.get("winner_selected") is False,
        "authenticate the reference without claiming any candidate or benchmark",
    )
    need(
        previous.get("repository_evidence_owner_count") == 157
        and previous.get("authenticated_digest_addressed_history_paths") == 162
        and previous.get("zig_original_campaign_semantic_mismatch_count") == 1764,
        "append actual reference evidence to independently authenticated V34",
    )
    proof = {
        "schema": SCHEMA + "-authenticated-additive-python-reference-v2",
        "status": "PASS",
        "reference_status": "PASS",
        "family": "python-reference",
        "source": source,
        "protocol": protocol,
        "contract": contract,
        "archive": archive,
        "receipt": receipt_owner,
        "publication_receipt": receipt,
        "publication_status": "PASS",
        "publication_pass_means": "EVIDENCE PUBLICATION ONLY",
        "original_case_denominator": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_case_count": 50,
        "additional_cases_included_in_original_denominator": False,
        "matrix_sha256": MATRIX_SHA,
        "record_vector_sha256": VECTOR_SHA,
        "record_vector_authenticated_from_full_reference_report": True,
        "record_vector_present_in_small_receipt": False,
        "actual_reference_processes_started": 2,
        "actual_distinct_process_ids": list(REFERENCE_PIDS),
        "reference_roles": list(REFERENCE_ROLES),
        "complete_reference_worker_count": len(workers),
        "complete_reference_observations_per_worker": 50,
        "reference_failure_count": 0,
        "candidate_signature_status": "NOT RUN",
        "candidate_introspection": "NOT MEASURED",
        "actual_candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "matching_archives_opened": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_compressed_bytes_read": ARCHIVE[2],
        "reference_archive_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_uncompressed_sha256": PLAIN_SHA,
        "hidden_cases_read": 0,
        "holdout_cases_read": 0,
        "final_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
        "historical_evidence_owner_lower_bound": 157,
        "historical_history_reference_lower_bound": 162,
        "new_distinct_reference_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 159,
        "authenticated_history_reference_lower_bound": 164,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
    }
    return proof, {ARCHIVE[0]: ARCHIVE[1], RECEIPT[0]: RECEIPT[1]}


def validate(snapshot: object) -> None:
    need(
        type(snapshot) is dict
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("baseline_passed") == 31237
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("preserved_v34_repository_evidence_owner_count") == 157
        and snapshot.get("preserved_v34_digest_addressed_history_path_count") == 162
        and snapshot.get("new_additive_reference_evidence_owner_count") == 2
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 159
        and snapshot.get("all_digest_addressed_history_path_count") == 164
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 159
        and snapshot.get("authenticated_history_reference_lower_bound") == 164
        and snapshot.get("evidence_owner_count_is_authenticated_lower_bound")
        is True,
        "preserve the V34 closure and derive only a 159/164 lower bound",
    )
    for name, mismatches, passes in (
        ("rust_v4_original_campaign", 1036, 8965),
        ("rust_v3_original_campaign", 1087, 7438),
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
        ("zig_v3_original_campaign", 1764, 3711),
    ):
        actual = snapshot.get(name)
        need(
            type(actual) is dict and actual.get("status") == "FAIL"
            and actual.get("actual_candidate_workers") == 13
            and actual.get("completed_suite_count") == 13
            and actual.get("semantic_mismatch_count") == mismatches
            and actual.get("verified_passing_case_count") == passes
            and actual.get("infrastructure_failure_count") == 0
            and actual.get("candidate_qualified") is False,
            "retain all authentic tested current and historical candidates: "
            + name,
        )
    actual = snapshot.get("additional_callable_reference_v2")
    need(
        type(actual) is dict
        and actual.get("schema")
        == SCHEMA + "-authenticated-additive-python-reference-v2"
        and actual.get("status") == "PASS"
        and actual.get("reference_status") == "PASS"
        and actual.get("family") == "python-reference"
        and actual.get("publication_status") == "PASS"
        and actual.get("publication_pass_means") == "EVIDENCE PUBLICATION ONLY"
        and actual.get("original_case_denominator") == 31237
        and actual.get("original_suite_count") == 13
        and actual.get("original_private_waiver_count") == 13
        and actual.get("additional_case_count") == 50
        and actual.get("additional_cases_included_in_original_denominator")
        is False
        and actual.get("matrix_sha256") == MATRIX_SHA
        and actual.get("record_vector_sha256") == VECTOR_SHA
        and actual.get("record_vector_authenticated_from_full_reference_report")
        is True
        and actual.get("record_vector_present_in_small_receipt") is False,
        "derive the real 50-case vector from the complete reference report only",
    )
    need(
        actual.get("actual_reference_processes_started") == 2
        and actual.get("actual_distinct_process_ids") == list(REFERENCE_PIDS)
        and actual.get("reference_roles") == list(REFERENCE_ROLES)
        and actual.get("complete_reference_worker_count") == 2
        and actual.get("complete_reference_observations_per_worker") == 50
        and actual.get("reference_failure_count") == 0
        and actual.get("candidate_signature_status") == "NOT RUN"
        and actual.get("candidate_introspection") == "NOT MEASURED"
        and actual.get("actual_candidate_processes_started") == 0
        and actual.get("candidate_imports") == 0
        and actual.get("native_libraries_loaded") == 0,
        "require 50 agreeing checks from the two real Python reference workers",
    )
    archive, receipt = actual.get("archive"), actual.get("receipt")
    need(
        type(archive) is dict and archive.get("path") == ARCHIVE[0]
        and archive.get("sha256") == ARCHIVE[1]
        and archive.get("bytes") == ARCHIVE[2]
        and archive.get("device") == ARCHIVE[3]
        and archive.get("inode") == ARCHIVE[4]
        and archive.get("mode") == "0600" and archive.get("nlink") == 1
        and archive.get("uid") == os.geteuid()
        and type(receipt) is dict and receipt.get("path") == RECEIPT[0]
        and receipt.get("sha256") == RECEIPT[1]
        and receipt.get("bytes") == RECEIPT[2]
        and receipt.get("device") == RECEIPT[3]
        and receipt.get("inode") == RECEIPT[4]
        and receipt.get("mode") == "0600" and receipt.get("nlink") == 1
        and receipt.get("uid") == os.geteuid()
        and (archive.get("device"), archive.get("inode"))
        != (receipt.get("device"), receipt.get("inode")),
        "require exactly two distinct durable private reference evidence owners",
    )
    published = actual.get("publication_receipt")
    need(
        type(published) is dict and published.get("status") == "PASS"
        and published.get("publication_status") == "PASS"
        and published.get("publication_pass_means")
        == "EVIDENCE PUBLICATION ONLY"
        and published.get("reference_status") == "PASS"
        and published.get("actual_reference_processes_started") == 2
        and published.get("actual_distinct_process_ids")
        == list(REFERENCE_PIDS)
        and published.get("additional_case_count") == 50
        and published.get("additional_cases_included_in_original_denominator")
        is False
        and published.get("candidate_introspection") == "NOT MEASURED"
        and "record_vector_sha256" not in published,
        "never attribute full-report reference evidence to the small receipt",
    )
    need(
        actual.get("matching_archives_opened") == 0
        and actual.get("matching_archive_gzip_inflation_count") == 0
        and actual.get("reference_archive_gzip_inflation_count") == 1
        and actual.get("reference_archive_compressed_bytes_read") == ARCHIVE[2]
        and actual.get("reference_archive_uncompressed_bytes_read") == PLAIN_BYTES
        and actual.get("reference_archive_uncompressed_sha256") == PLAIN_SHA
        and actual.get("hidden_cases_read") == 0
        and actual.get("holdout_cases_read") == 0
        and actual.get("final_cases_read") == 0
        and actual.get("clock_samples") == 0
        and actual.get("timing_trials_run") == 0
        and actual.get("performance") == "NOT MEASURED"
        and actual.get("memory") == "NOT MEASURED"
        and actual.get("confidence_intervals") == "NOT MEASURED"
        and actual.get("undefined_behavior") == "NOT MEASURED"
        and actual.get("holdout") == "NOT OPENED"
        and actual.get("winner_selected") is False
        and actual.get("historical_evidence_owner_lower_bound") == 157
        and actual.get("historical_history_reference_lower_bound") == 162
        and actual.get("new_distinct_reference_evidence_owner_count") == 2
        and actual.get("authenticated_evidence_owner_lower_bound") == 159
        and actual.get("authenticated_history_reference_lower_bound") == 164
        and actual.get("evidence_owner_count_is_authenticated_lower_bound")
        is True
        and actual.get("history_reference_count_is_authenticated_lower_bound")
        is True,
        "decompress only one bounded reference archive; preserve honest lower bounds",
    )
    need(
        snapshot.get("additional_signature_frozen_case_count") == 50
        and snapshot.get("additional_signature_reference_status") == "PASS"
        and snapshot.get("additional_signature_reference_cases_executed") == 50
        and snapshot.get("additional_signature_reference_process_count") == 2
        and snapshot.get("additional_signature_reference_process_ids")
        == list(REFERENCE_PIDS)
        and snapshot.get("additional_signature_candidate_status") == "NOT RUN"
        and snapshot.get("additional_signature_candidate_cases_executed") == 0
        and snapshot.get("additional_cases_included_in_original_denominator")
        is False
        and snapshot.get("additional_signature_matrix_sha256") == MATRIX_SHA
        and snapshot.get("additional_signature_record_vector_sha256") == VECTOR_SHA
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("production_runtime_delegation_audit")
        == "NOT ESTABLISHED"
        and snapshot.get("native_source_build_independence") == "VERIFIED",
        "distinguish successful Python references from untested candidate signatures",
    )
    need(
        snapshot.get("matching_archive_gzip_inflation_count") == 0
        and snapshot.get("reference_archive_gzip_inflation_count") == 1
        and snapshot.get("reference_archive_uncompressed_bytes_read")
        == PLAIN_BYTES
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("hidden_cases_read") == 0
        and snapshot.get("performance_files_read") == 0
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "leave candidate matching, runtime proof, speed and hidden holdout untouched",
    )


def xml(value: object) -> str:
    return (
        str(value).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
    )


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "actual V35 renderer")
    checked(inputs, "actual V35 inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1725" '
        'viewBox="0 0 1440 1725" role="img" '
        'aria-labelledby="v35-title v35-description">',
        '<title id="v35-title">Building a faster Python re: 50 extra '
        'Python API checks now independently verified</title>',
        '<desc id="v35-description">The original Python reference still '
        'has exactly 31,237 checks across 13 suites. Two independently '
        'observed reference processes, PIDs 81 and 82, agree on all 50 '
        'separately counted callable-signature checks. Candidate signature '
        'checks have not run. Current Rust, C and Zig still have 1,036, '
        '1,230 and 1,764 compatibility differences; no replacement '
        'qualifies. Source independence is verified but full runtime '
        'no-delegation remains NOT ESTABLISHED. Speed, memory and confidence '
        'are NOT MEASURED. At least 159 evidence owners and 164 history '
        'references are authenticated. Exactly one bounded additional '
        'Python-reference report was decompressed; no candidate matching '
        'archive was inflated. The 4,194,304-case holdout remains unopened '
        'and ungenerated.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        '"Segoe UI",sans-serif}.title{font-size:26px;font-weight:760;fill:'
        '#16324f}.heading{font-size:19px;font-weight:750;fill:#16324f}'
        '.body{font-size:14px;fill:#42556c}.name{font-size:14px;font-weight:'
        '720;fill:#16324f}.pass{font-size:12px;font-weight:760;fill:#00794c}'
        '.fail{font-size:12px;font-weight:750;fill:#a75c13}.pending{font-size:'
        '12px;font-weight:740;fill:#53667b}.big{font-size:20px;font-weight:'
        '760;fill:#16324f}.small{font-size:11px;fill:#42556c}.foot{font-size:'
        '10px;fill:#53667b}</style>',
        '<rect width="1440" height="1725" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="53" class="title">Can we build a faster '
        'replacement for Python re?</text>',
        '<text x="46" y="81" class="body">Two independent Python '
        'references now confirm 50 extra API checks. No candidate has '
        'passed full compatibility; speed is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "unchanged original checks"),
        ("50 / 50", "extra Python checks pass"),
        ("2", "independent reference workers"),
        ("0", "compatible replacements"),
        ("1,764", "current Zig differences"),
        ("0", "candidate extra checks run"),
        ("≥159 / 164", "authenticated lower bounds"),
    )
    for index, (number, label) in enumerate(cards):
        left = 44 + 195 * index
        lines.extend((
            f'<rect x="{left}" y="99" width="184" height="83" rx="11" '
            'fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{left + 9}" y="132" class="big">{xml(number)}</text>',
            f'<text x="{left + 9}" y="157" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="201" width="1352" height="357" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="235" class="heading">1. Overall: can a '
        'candidate yet replace Python re?</text>',
        '<text x="66" y="259" class="body">Same frozen 31,237-case '
        'original reference; lower differences are better, and only '
        'zero qualifies.</text>',
    ))
    candidates = (
        ("Python re — original reference", "REFERENCE PASS", 0, 31237, "pass"),
        ("Rust — current from-scratch candidate", "NOT COMPATIBLE", 1036, 8965, "fail"),
        ("C — current from-scratch candidate", "NOT COMPATIBLE", 1230, 7325, "fail"),
        ("Zig — corrected and actually tested", "NOT COMPATIBLE", 1764, 3711, "fail"),
    )
    for index, (name, outcome, differences, confirmed, kind) in enumerate(candidates):
        top = 284 + 62 * index
        width = round(590 * differences / 1764) if differences else 0
        color = "#0b8d61" if not differences else "#b77a36"
        lines.extend((
            f'<text x="67" y="{top + 16}" class="name">{xml(name)}</text>',
            f'<text x="1370" y="{top + 16}" class="{kind}" '
            f'text-anchor="end">{xml(outcome)}</text>',
            f'<rect x="68" y="{top + 27}" width="590" height="10" '
            'rx="5" fill="#edf1f5"/>',
            f'<rect x="68" y="{top + 27}" width="{width}" height="10" '
            f'rx="5" fill="{color}"/>',
            f'<text x="674" y="{top + 37}" class="small">'
            f'{differences:,} differences; {confirmed:,} independently '
            'confirmed passes</text>',
        ))
    lines.extend((
        '<rect x="44" y="577" width="1352" height="285" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="611" class="heading">2. What the 50 new '
        'reference checks actually prove</text>',
    ))
    reference_notes = (
        "Python itself passed all 50 separately frozen public callable-signature checks.",
        "Two actual isolated Python reference workers, PIDs 81 and 82, independently agreed.",
        "Both workers recorded and preserved all 50 complete signature observations.",
        "The shared record fingerprint is independently verified from the full reference report.",
        "These 50 checks are additional: the original compatibility denominator remains 31,237.",
        "Candidate signature checks are NOT RUN; a Python pass is not a candidate pass.",
        "Exactly one 152,530-byte Python-reference report was bounded and authenticated.",
        "No C, Rust, Zig or other candidate matching archive was decompressed.",
    )
    for index, note in enumerate(reference_notes):
        lines.append(
            f'<text x="67" y="{641 + 25 * index}" class="body">'
            f'{xml(note)}</text>'
        )
    lines.extend((
        '<rect x="44" y="880" width="1352" height="282" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="914" class="heading">3. What remains '
        'unproven or unmeasured</text>',
    ))
    remaining = (
        ("Compatible replacement", "NONE: Rust, C and Zig still differ from Python re."),
        ("Candidates on the 50 extra checks", "NOT RUN: only the two Python reference processes have run."),
        ("Faster than Python re", "NOT MEASURED: no candidate is correctness-qualified."),
        ("Runtime no-delegation", "NOT ESTABLISHED: first-party source is not a complete runtime audit."),
        ("Memory and statistical confidence", "NOT MEASURED: no eligible performance comparison."),
        ("4,194,304-case final holdout", "NOT OPENED and NOT GENERATED; zero hidden cases read."),
        ("Winner", "NONE: compatibility, runtime independence and speed are not established."),
    )
    for index, (name, detail) in enumerate(remaining):
        top = 945 + 30 * index
        lines.extend((
            f'<text x="68" y="{top}" class="name">{xml(name)}</text>',
            f'<text x="379" y="{top}" class="body">{xml(detail)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1180" width="1352" height="354" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1214" class="heading">4. How to read '
        'the independently recorded evidence</text>',
    ))
    audit = (
        "The original reference remains exactly 31,237 checks, 13 suites and 13 named private waivers.",
        "50 additional checks passed in each of two actual, separately identified Python processes.",
        "Their agreement fingerprint comes from the bounded full reference report, not the small receipt.",
        "V34 independently authenticated 157 evidence owners and 162 historical references.",
        "Two distinct new reference records establish lower bounds of 159 owners and 164 references.",
        "These are authenticated lower bounds, not a claim to have counted the whole workspace.",
        "The corrected Zig remains at 1,764 differences; Rust has 1,036 and C has 1,230.",
        "First-party source and build independence are verified; runtime no-delegation is NOT ESTABLISHED.",
        "Exactly one reference gzip was inflated; candidate matching archive inflation remains zero.",
        "No graph ran a reference worker, candidate, compiler, benchmark, clock or hidden holdout.",
    )
    for index, note in enumerate(audit):
        lines.append(
            f'<text x="67" y="{1245 + 25 * index}" class="body">'
            f'{xml(note)}</text>'
        )
    lines.extend((
        f'<text x="47" y="1568" class="foot">Inputs SHA-256: '
        f'{xml(inputs)}</text>',
        f'<text x="47" y="1590" class="foot">Renderer SHA-256: '
        f'{xml(source)}</text>',
        f'<text x="47" y="1612" class="foot">Actual additional reference '
        f'archive SHA-256: {xml(ARCHIVE[1])}</text>',
        f'<text x="47" y="1634" class="foot">Actual additional reference '
        f'receipt SHA-256: {xml(RECEIPT[1])}</text>',
        f'<text x="47" y="1656" class="foot">Actual 50-observation '
        f'vector SHA-256: {xml(VECTOR_SHA)}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(
    source_pin: str, archive_pin: str, receipt_pin: str,
) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_pin = checked(source_pin, "actual V35 graph renderer")
    own, _ = read_owner(SELF, source_pin, os.path.getsize(ROOT / SELF))
    previous, previous_inputs = authenticate_v34()
    proof, additions = authenticate_reference_v2(
        archive_pin, receipt_pin, previous,
    )
    need(
        len(additions) == 2 and len(set(additions)) == 2
        and all(name.startswith("oracle/phase1/evidence/")
                for name in additions),
        "append exactly two distinct phase-one Python-reference records",
    )
    count = previous["repository_evidence_owner_count"] + len(additions)
    reference_count = (
        previous["authenticated_digest_addressed_history_paths"]
        + len(additions)
    )
    need(count == 159 and reference_count == 164,
         "derive only the authenticated append-only 159/164 lower bound")
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update({
        "preserved_v34_repository_evidence_owner_count": 157,
        "preserved_v34_digest_addressed_history_path_count": 162,
        "new_additive_reference_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": reference_count,
        "authenticated_evidence_owner_lower_bound": count,
        "authenticated_history_reference_lower_bound": reference_count,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "additional_callable_reference_v2": copy.deepcopy(proof),
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": list(REFERENCE_PIDS),
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        "additional_signature_matrix_sha256": MATRIX_SHA,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_uncompressed_bytes_read": PLAIN_BYTES,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "native_source_build_independence": "VERIFIED",
    })
    validate(snapshot)
    prior = {name: pin(*owner) for name, owner in V34.items()}
    manifest = copy.deepcopy(previous_inputs)
    manifest.update({
        "schema": SCHEMA + "-inputs",
        "version": 35,
        "python": "3.14.6",
        "renderer": pin(SELF, source_pin, len(own)),
        "previous_overview": prior,
        "actual_additional_callable_reference_v2": copy.deepcopy(proof),
        "preserved_v34_repository_evidence_owner_count": 157,
        "preserved_v34_digest_addressed_history_path_count": 162,
        "new_additive_reference_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": reference_count,
        "authenticated_evidence_owner_lower_bound": count,
        "authenticated_history_reference_lower_bound": reference_count,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "candidate_qualified_count": 0,
        "full_case_denominator": 31237,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": list(REFERENCE_PIDS),
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        "additional_signature_matrix_sha256": MATRIX_SHA,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "additional_signature_vector_authenticated_from_full_report": True,
        "additional_signature_vector_present_in_small_receipt": False,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_uncompressed_sha256": PLAIN_SHA,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    })
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source_pin, digest(manifest_raw))
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 35,
        "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_pin, len(own)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw),
                      len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(image), len(image)),
        "previous_overview": prior,
        "snapshot": snapshot,
        "preserved_v34_repository_evidence_owner_count": 157,
        "preserved_v34_authenticated_reference_path_count": 162,
        "new_additive_reference_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "authenticated_digest_addressed_history_paths": reference_count,
        "authenticated_evidence_owner_lower_bound": count,
        "authenticated_history_reference_lower_bound": reference_count,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "qualified_candidate_count": 0,
        "actual_additional_callable_reference_v2": copy.deepcopy(proof),
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": list(REFERENCE_PIDS),
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        "additional_signature_matrix_sha256": MATRIX_SHA,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "additional_signature_vector_authenticated_from_full_report": True,
        "additional_signature_vector_present_in_small_receipt": False,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_compressed_bytes_read": ARCHIVE[2],
        "reference_archive_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_uncompressed_sha256": PLAIN_SHA,
        "matching_archive_gzip_inflation_count": 0,
        "candidate_matching_archive_opened_by_graph": False,
        "uncompressed_c_matching_archive_bytes_read_by_graph": 0,
        "uncompressed_rust_matching_archive_bytes_read_by_graph": 0,
        "uncompressed_zig_matching_archive_bytes_read_by_graph": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
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
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", image),
    )


class Wall:
    """Physically forbid reference execution and effects in source-only tests."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def __enter__(self) -> Wall:
        def forbid(name: str):
            def blocked(*_args: object, **_kwargs: object) -> object:
                self.blocked += 1
                raise GraphError("V35 source-only effect blocked: " + name)

            return blocked

        groups = (
            (builtins, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "unlink",
                  "remove", "rename", "replace", "mkdir", "makedirs",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "mkdir", "unlink",
                    "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call",
                          "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp")),
            (threading.Thread, ("start",)),
            (zlib, ("decompress", "decompressobj")),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                if hasattr(owner, name):
                    self.saved.append((owner, name, getattr(owner, name)))
                    setattr(owner, name, forbid(name))
        return self

    def __exit__(self, *_errors: object) -> None:
        for owner, name, value in reversed(self.saved):
            setattr(owner, name, value)


def synthetic() -> dict:
    def campaign(mismatches: int, passes: int) -> dict:
        return {
            "status": "FAIL",
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "semantic_mismatch_count": mismatches,
            "verified_passing_case_count": passes,
            "infrastructure_failure_count": 0,
            "candidate_qualified": False,
        }

    archive = {
        "path": ARCHIVE[0], "sha256": ARCHIVE[1], "bytes": ARCHIVE[2],
        "device": ARCHIVE[3], "inode": ARCHIVE[4], "mode": "0600",
        "nlink": 1, "uid": 1000,
    }
    receipt = {
        "path": RECEIPT[0], "sha256": RECEIPT[1], "bytes": RECEIPT[2],
        "device": RECEIPT[3], "inode": RECEIPT[4], "mode": "0600",
        "nlink": 1, "uid": 1000,
    }
    published = {
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "EVIDENCE PUBLICATION ONLY",
        "reference_status": "PASS",
        "actual_reference_processes_started": 2,
        "actual_distinct_process_ids": list(REFERENCE_PIDS),
        "additional_case_count": 50,
        "additional_cases_included_in_original_denominator": False,
        "candidate_introspection": "NOT MEASURED",
    }
    proof = {
        "schema": SCHEMA + "-authenticated-additive-python-reference-v2",
        "status": "PASS", "reference_status": "PASS",
        "family": "python-reference", "archive": archive,
        "receipt": receipt, "publication_receipt": published,
        "publication_status": "PASS",
        "publication_pass_means": "EVIDENCE PUBLICATION ONLY",
        "original_case_denominator": 31237,
        "original_suite_count": 13, "original_private_waiver_count": 13,
        "additional_case_count": 50,
        "additional_cases_included_in_original_denominator": False,
        "matrix_sha256": MATRIX_SHA,
        "record_vector_sha256": VECTOR_SHA,
        "record_vector_authenticated_from_full_reference_report": True,
        "record_vector_present_in_small_receipt": False,
        "actual_reference_processes_started": 2,
        "actual_distinct_process_ids": list(REFERENCE_PIDS),
        "reference_roles": list(REFERENCE_ROLES),
        "complete_reference_worker_count": 2,
        "complete_reference_observations_per_worker": 50,
        "reference_failure_count": 0,
        "candidate_signature_status": "NOT RUN",
        "candidate_introspection": "NOT MEASURED",
        "actual_candidate_processes_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "matching_archives_opened": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_compressed_bytes_read": ARCHIVE[2],
        "reference_archive_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_uncompressed_sha256": PLAIN_SHA,
        "hidden_cases_read": 0, "holdout_cases_read": 0,
        "final_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
        "historical_evidence_owner_lower_bound": 157,
        "historical_history_reference_lower_bound": 162,
        "new_distinct_reference_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 159,
        "authenticated_history_reference_lower_bound": 164,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
    }
    return {
        "full_case_denominator": 31237,
        "suite_count": 13,
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v34_repository_evidence_owner_count": 157,
        "preserved_v34_digest_addressed_history_path_count": 162,
        "new_additive_reference_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 159,
        "all_digest_addressed_history_path_count": 164,
        "authenticated_evidence_owner_lower_bound": 159,
        "authenticated_history_reference_lower_bound": 164,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "rust_v4_original_campaign": campaign(1036, 8965),
        "rust_v3_original_campaign": campaign(1087, 7438),
        "c_v4_original_campaign": campaign(1230, 7325),
        "zig_v2_original_campaign": campaign(2172, 2847),
        "zig_v3_original_campaign": campaign(1764, 3711),
        "additional_callable_reference_v2": proof,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": list(REFERENCE_PIDS),
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        "additional_signature_matrix_sha256": MATRIX_SHA,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_uncompressed_bytes_read": PLAIN_BYTES,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
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
        if value in ("NOT RUN", "NOT MEASURED", "NOT ESTABLISHED"):
            return "VERIFIED"
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

        def reject(snapshot: dict, label: str) -> None:
            nonlocal rejected
            try:
                validate(snapshot)
            except (GraphError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise GraphError("accepted hostile synthetic V35 evidence: " + label)

        groups = (
            "rust_v4_original_campaign", "rust_v3_original_campaign",
            "c_v4_original_campaign", "zig_v2_original_campaign",
            "zig_v3_original_campaign", "additional_callable_reference_v2",
        )
        for key, value in base.items():
            if key in groups:
                continue
            attack = copy.deepcopy(base)
            attack[key] = forged(value)
            reject(attack, "snapshot-" + key)
        for name in groups:
            for key, value in base[name].items():
                attack = copy.deepcopy(base)
                attack[name][key] = forged(value)
                reject(attack, name + "-" + key)
        proof = base["additional_callable_reference_v2"]
        for name in ("archive", "receipt", "publication_receipt"):
            for key, value in proof[name].items():
                attack = copy.deepcopy(base)
                attack["additional_callable_reference_v2"][name][key] = forged(value)
                reject(attack, name + "-" + key)
        forged_receipt = copy.deepcopy(base)
        forged_receipt["additional_callable_reference_v2"]["publication_receipt"]\
            ["record_vector_sha256"] = VECTOR_SHA
        reject(forged_receipt, "invent-record-vector-in-small-publication-receipt")
        collision = copy.deepcopy(base)
        collision["additional_callable_reference_v2"]["receipt"]["device"] = ARCHIVE[3]
        collision["additional_callable_reference_v2"]["receipt"]["inode"] = ARCHIVE[4]
        reject(collision, "reference-archive-and-receipt-inode-collision")
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"31,237", b"50 / 50", b"81 and 82", b"1,036", b"8,965",
            b"1,230", b"7,325", b"1,764", b"3,711",
            b"NOT COMPATIBLE", b"NOT ESTABLISHED", b"NOT RUN",
            b"152,530", b"candidate matching archive", b"lower bounds",
            b"4,194,304", b"NOT GENERATED",
        ):
            need(phrase.lower() in picture.lower(),
                 "reject a misleading additional-reference V35 graph")
        effects = (
            lambda: builtins.open("forbidden-v35"),
            lambda: os.open("forbidden-v35", os.O_RDONLY),
            lambda: os.stat("forbidden-v35-native"),
            lambda: subprocess.run(("forbidden-v35",)),
            lambda: importlib.import_module("candidates.zig_candidate"),
            lambda: importlib.import_module("re"),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: zlib.decompressobj(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for action in effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("V35 source-only test leaked a real external effect")
        need(wall.blocked == len(effects),
             "physically block all 11 actual source-only side effects")
        need(rejected >= 140,
             "exercise all forged reference, worker, lower-bound and archive fields")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 35, "status": "PASS", "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "preserved_v34_authenticated_evidence_owner_count": 157,
            "preserved_v34_authenticated_reference_count": 162,
            "new_reference_evidence_owner_count": 2,
            "authenticated_evidence_owner_lower_bound": 159,
            "authenticated_history_reference_lower_bound": 164,
            "evidence_owner_count_is_authenticated_lower_bound": True,
            "qualified_candidate_count": 0,
            "current_rust_semantic_mismatch_count": 1036,
            "current_c_semantic_mismatch_count": 1230,
            "current_zig_semantic_mismatch_count": 1764,
            "current_zig_verified_passing_case_count": 3711,
            "additional_signature_frozen_case_count": 50,
            "additional_signature_reference_status": "PASS",
            "additional_signature_reference_cases_executed": 50,
            "additional_signature_reference_process_count": 2,
            "additional_signature_reference_process_ids": list(REFERENCE_PIDS),
            "additional_signature_candidate_status": "NOT RUN",
            "additional_signature_candidate_cases_executed": 0,
            "additional_cases_included_in_original_denominator": False,
            "additional_signature_matrix_sha256": MATRIX_SHA,
            "additional_signature_record_vector_sha256": VECTOR_SHA,
            "native_source_build_independence": "VERIFIED",
            "runtime_no_delegation": "NOT ESTABLISHED",
            "production_runtime_delegation_audit": "NOT ESTABLISHED",
            "actual_candidate_workers_started_by_graph": 0,
            "actual_candidate_imports": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_activations": 0,
            "canonical_target_reads": 0, "canonical_target_stats": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "uncompressed_candidate_matching_archive_bytes_read": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(path in allowed and type(raw) is bytes and 0 < len(raw) <= LIMIT,
         "write only the three exclusively reserved V35 graph owners")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(handle, remaining)
            need(type(written) is int and written > 0,
                 "reject an incomplete exclusive V35 output")
            remaining = remaining[written:]
        os.fsync(handle)
        observed = os.fstat(handle)
        need(
            observed.st_uid == os.geteuid() and observed.st_nlink == 1
            and observed.st_size == len(raw)
            and stat.S_IMODE(observed.st_mode) == 0o600,
            "reject an altered, linked or nonprivate generated V35 owner",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(actual == raw,
         "independently re-read each durably published V35 owner")


def result(
    source: str, archive: str, receipt: str,
    outputs: dict[str, bytes], written: bool, suffix: str,
) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 35,
        "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_additional_reference_archive_sha256": archive,
        "actual_additional_reference_receipt_sha256": receipt,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "preserved_v34_authenticated_evidence_owner_count": 157,
        "preserved_v34_authenticated_reference_count": 162,
        "new_reference_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 159,
        "authenticated_history_reference_lower_bound": 164,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "qualified_candidate_count": 0,
        "rust_matching_status": "FAIL",
        "rust_semantic_mismatch_count": 1036,
        "rust_verified_passing_case_count": 8965,
        "c_matching_status": "FAIL",
        "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_matching_status": "FAIL",
        "zig_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_count": 3711,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": list(REFERENCE_PIDS),
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        "additional_signature_matrix_sha256": MATRIX_SHA,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "additional_signature_vector_authenticated_from_full_report": True,
        "additional_signature_vector_present_in_small_receipt": False,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "outputs_written": written,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_compressed_bytes_read": ARCHIVE[2],
        "reference_archive_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_uncompressed_sha256": PLAIN_SHA,
        "matching_archive_gzip_inflation_count": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "uncompressed_c_matching_archive_bytes_read": 0,
        "uncompressed_rust_matching_archive_bytes_read": 0,
        "uncompressed_zig_matching_archive_bytes_read": 0,
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
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    for name in (
        "--source-sha256", "--reference-archive-sha256",
        "--reference-receipt-sha256", "--inputs-sha256",
        "--summary-sha256", "--svg-sha256",
    ):
        parser.add_argument(name)
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(
                all(getattr(args, name) is None for name in (
                    "source_sha256", "reference_archive_sha256",
                    "reference_receipt_sha256", "inputs_sha256",
                    "summary_sha256", "svg_sha256",
                )),
                "source-only self-tests never accept archive pins or write outputs",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "actual V35 graph renderer")
        archive = checked(args.reference_archive_sha256,
                          "actual additional Python reference archive")
        receipt = checked(args.reference_receipt_sha256,
                          "actual additional Python reference receipt")
        _snapshot, pairs = build(source, archive, receipt)
        outputs = dict(pairs)
        if args.render:
            need(
                args.inputs_sha256 is None and args.summary_sha256 is None
                and args.svg_sha256 is None,
                "publish only the three exact exclusively reserved V35 owners",
            )
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(
                canonical(result(source, archive, receipt, outputs,
                                 True, "-published"))
            )
            return 0
        frozen = {
            OUTPUT + ".inputs.json": checked(args.inputs_sha256,
                                               "frozen V35 graph inputs"),
            OUTPUT + ".json": checked(args.summary_sha256,
                                         "frozen V35 graph summary"),
            OUTPUT + ".svg": checked(args.svg_sha256,
                                        "frozen V35 graph image"),
        }
        for path, fingerprint in frozen.items():
            raw, _ = read_owner(path, fingerprint, len(outputs[path]),
                                private=True)
            need(raw == outputs[path],
                 "independently reproduce every exact authenticated V35 owner")
        sys.stdout.buffer.write(
            canonical(result(source, archive, receipt, outputs,
                             False, "-read-only-frozen-context"))
        )
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            KeyError, AttributeError, struct.error, zlib.error) as error:
        sys.stderr.write("current V35 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
