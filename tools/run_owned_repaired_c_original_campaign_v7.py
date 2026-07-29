#!/usr/bin/env python3
"""Freeze and run fully diagnosed, first-party C original correctness cases.

The three source modes cannot inspect a native image, a private build root,
compressed evidence, a performance case, or a candidate.  Real execution is a
separately and fully pinned operation.  Each real suite receives one guarded
worker and a complete, bounded, plain-language failure record.
"""

from __future__ import annotations

import ast
import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_owned_repaired_c_original_campaign_v7.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V7.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v7.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v7"
LABEL = "phase2-v18-c-subject-buffer-root-provenance-original-p0-v7"
DEVICE = 2064
MAX_WORKER_STDOUT = 3 * 1024 * 1024
MAX_WORKER_STDERR = 1024 * 1024
MAX_STORED_DIAGNOSTIC = 128 * 1024
MAX_SUMMARY_DIAGNOSTIC = 4096
MAX_VECTOR_PREFIX = 24
WORKER_TIMEOUT_SECONDS = 120
V6 = (
    (
        "tools/run_owned_repaired_c_original_campaign_v6.py",
        "2f259e81c56e6ba8e3264709ae36187c7e0659020a5c398c68b0a7bf1d2be999",
        97043,
        431024,
    ),
    (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V6.md",
        "a0e856f4fa94369340f0794f9ae34355aca6cdc7f4cb5ab13ec56e9c91b04778",
        7278,
        525103,
    ),
    (
        "oracle/phase2/repaired-c-original-campaign-v6.json",
        "124e6ef03136aec2249809f09a57185813c86fc1c78c8b1063971af0a34ccf64",
        15623,
        525104,
    ),
)
V6_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v6-c-"
    "phase2-v18-c-subject-buffer-root-provenance-original-p0-v6-"
    "failures-publication-receipt.json",
    "868fdd4df9ed960113c324c1dda82d12d2e700d5c32213a4d8c147384b64b081",
    2596,
    525136,
)
V6_PROCESS_IDS = (81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 187, 188, 189)
EARLY_PHASES = (
    "AUTHORIZE AND AUTHENTICATE SOURCE",
    "AUTHENTICATE FROZEN ORIGINAL CONTEXT",
    "AUTHENTICATE RECOVERY JOURNAL",
    "INSTALL FIRST-PARTY GUARD",
    "IMPORT ONLY FIRST-PARTY C ENGINE",
    "OBSERVE COMPLETE ORIGINAL SUITE",
    "ENCODE COMPLETE GUARDED RESULT",
)


class CampaignError(Exception):
    """A frozen owner, a candidate run, or an evidence boundary was rejected."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise CampaignError(reason)


def clean_runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and os.path.realpath(sys.executable) == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "require clean, pinned CPython 3.14.6 -I -B -S before the guard",
    )


def bootstrap_v6() -> types.ModuleType:
    clean_runtime()
    relative, digest, length, inode = V6[0]
    descriptor = os.open(
        ROOT + "/" + relative,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_dev == DEVICE
            and before.st_ino == inode
            and before.st_size == length
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "reject a changed, substituted, or unowned complete C V6 source",
        )
        pieces = []
        remaining = length
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            need(bool(piece), "reject a truncated complete C V6 source")
            pieces.append(piece)
            remaining -= len(piece)
        need(not os.read(descriptor, 1), "reject appended C V6 source")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need(
            hashlib.sha256(raw).hexdigest() == digest
            and (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
                before.st_nlink,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
                after.st_nlink,
            ),
            "reject a concurrently modified frozen C V6 predecessor",
        )
    finally:
        os.close(descriptor)
    module = types.ModuleType("_rebar_owned_c_v7_authenticated_v6")
    module.__file__ = ROOT + "/" + relative
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(
        module.SCHEMA == "rebar-owned-repaired-c-original-campaign-v6"
        and module.SOURCE == V6[0][0]
        and module.PROTOCOL == V6[1][0]
        and module.CONTRACT == V6[2][0]
        and module.ORIGINAL_CASE_COUNT == 31237
        and module.SEPARATE_REFERENCE_CASE_COUNT == 8244
        and module.EXPANDED_PROPOSED_CASE_COUNT == 14155776
        and module.WORKER_TIMEOUT_SECONDS == WORKER_TIMEOUT_SECONDS
        and len(module.SUITES) == 13
        and sum(count for _, count in module.SUITES) == 31237,
        "reject incomplete or semantically replaced first-party C V6 source",
    )
    clean_runtime()
    return module


def exact_digest(value: object, role: str) -> str:
    need(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "require a complete lowercase SHA-256: " + role,
    )
    return value


def options(arguments: list[str], previous: types.ModuleType) -> dict:
    need(type(arguments) is list and all(type(item) is str for item in arguments),
         "reject malformed C V7 authorization")
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover")
    selected = [mode for mode in modes if arguments.count(mode) == 1]
    need(len(selected) == 1 and sum(arguments.count(mode) for mode in modes) == 1,
         "choose exactly one source-only or explicitly pinned actual mode")
    mode = selected[0]
    accepted = {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
    actual = mode in ("--run", "--worker", "--recover")
    if actual:
        accepted.update("--" + key.replace("_", "-")
                        for key in previous.actual_authority())
        if mode == "--worker":
            accepted.update({"--suite", "--activation-inode",
                             "--recovery-journal-sha256"})
        if mode == "--recover":
            accepted.add("--recovery-journal-sha256")
    parsed = {"mode": mode}
    index = 0
    while index < len(arguments):
        flag = arguments[index]
        if flag == mode:
            index += 1
            continue
        need(flag in accepted and flag not in parsed and index + 1 < len(arguments),
             "reject duplicate, incomplete, guessed-root, or hidden authorization")
        parsed[flag] = arguments[index + 1]
        index += 2
    exact_digest(parsed.get("--source-sha256"), "C V7 source")
    exact_digest(parsed.get("--protocol-sha256"), "C V7 protocol")
    if mode == "--render-contract":
        need("--contract-sha256" not in parsed,
             "render a new contract without pretending it is already frozen")
    else:
        exact_digest(parsed.get("--contract-sha256"), "C V7 contract")
    if actual:
        for key, expected in previous.actual_authority().items():
            flag = "--" + key.replace("_", "-")
            need(parsed.get(flag) == expected,
                 "require independently pinned C18 actual authority: " + flag)
        if mode == "--worker":
            need(parsed.get("--suite") in dict(previous.SUITES),
                 "pin exactly one complete original C suite")
            active = parsed.get("--activation-inode")
            need(type(active) is str and active.isdigit() and int(active) > 0,
                 "pin the exact promoted first-party native inode")
            exact_digest(parsed.get("--recovery-journal-sha256"),
                         "durable original-native recovery journal")
        elif mode == "--recover":
            exact_digest(parsed.get("--recovery-journal-sha256"),
                         "durable original-native recovery journal")
    else:
        need(set(parsed) <= {"mode", "--source-sha256", "--protocol-sha256",
                             "--contract-sha256"},
             "source modes cannot authorize roots, workers, natives, or candidates")
    return parsed


def validate_v6_receipt(value: dict, previous: types.ModuleType) -> dict:
    expected = {
        "schema": "rebar-owned-repaired-c-original-campaign-v6-"
                  "durable-publication-receipt",
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "version": 6,
        "family": "c",
        "label": "phase2-v18-c-subject-buffer-root-provenance-original-p0-v6",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": V6[0][1],
        "protocol_sha256": V6[1][1],
        "contract_sha256": V6[2][1],
        "actual_c18_build_receipt_sha256": previous.BUILD_RECEIPT[1],
        "actual_c18_root_receipt_sha256": previous.ROOT_RECEIPT[1],
        "corrected_source_sha256": previous.CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256": previous.ADAPTER[1],
        "native_engine_sha256": previous.NATIVE_SHA256,
        "native_bridge_sha256": previous.NATIVE_SHA256,
        "suite_count": 13,
        "attempted_suite_count": 13,
        "completed_suite_count": 3,
        "case_execution_denominator": 31237,
        "actual_candidate_workers": 13,
        "actual_worker_process_ids_are_distinct": True,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": 3366,
        "infrastructure_failure_count": 5,
        "candidate_execution_failure_count": 5,
        "worker_timeout_count": 0,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "named_private_waiver_count": 13,
        "separate_reference_case_count": 8244,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "original_source_targets_modified": 0,
        "original_native_inode_restored": True,
        "expanded_holdout_proposed_case_count": 14155776,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    need(type(value) is dict and all(value.get(key) == item
                                    for key, item in expected.items()),
         "preserve every genuine, published C V6 failure and every honest boundary")
    need(value.get("actual_worker_process_ids") == list(V6_PROCESS_IDS)
         and len(set(V6_PROCESS_IDS)) == 13,
         "preserve the 13 distinct actual C V6 worker process identities")
    archive = value.get("archive")
    need(type(archive) is dict
         and archive.get("sha256")
         == "ecfd95c5f739999a6f39f06c2d11ed62594913803cec3809b7475dfa811f1afa"
         and archive.get("bytes") == 3337518
         and archive.get("mode") == "0600"
         and archive.get("nlink") == 1
         and archive.get("exclusive_creation") is True
         and archive.get("file_fsync_completed") is True
         and archive.get("directory_fsync_completed") is True,
         "authenticate archived C V6 evidence by its small receipt without opening it")
    return value


def bounded_plaintext(raw: bytes, limit: int = MAX_STORED_DIAGNOSTIC) -> dict:
    need(type(raw) is bytes and type(limit) is int and limit > 0,
         "require genuine bounded worker bytes")
    prefix = raw[:limit]
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "plaintext": prefix.decode("utf-8", "backslashreplace"),
        "stored_bytes": len(prefix),
        "truncated": len(raw) > limit,
    }


def canonical_vector(records: object, producer: types.ModuleType,
                     *, expected: str | None = None) -> dict:
    need(type(records) in (list, tuple),
         "require the authentic complete original candidate record vector")
    digest = hashlib.sha256()
    digest.update(b"[")
    for index, record in enumerate(records):
        if index:
            digest.update(b",")
        encoded = producer.canonical(record)
        need(encoded.endswith(b"\n"),
             "preserve exact complete canonical original vector framing")
        digest.update(encoded[:-1])
    digest.update(b"]\n")
    fingerprint = digest.hexdigest()
    if expected is not None:
        need(fingerprint == exact_digest(expected, "actual complete original vector"),
             "reject a candidate vector whose complete digest does not match observation")
    prefix = [safe_detail(item, 1, producer)
              for item in records[:MAX_VECTOR_PREFIX]]
    return {
        "total_count": len(records),
        "complete_vector_sha256": fingerprint,
        "prefix": prefix,
        "prefix_count": len(prefix),
        "truncated": len(records) > len(prefix),
        "complete_vector_digest_preserved": True,
        "complete_vector_embedded": len(records) == len(prefix),
    }


def safe_detail(value: object, depth: int = 0,
                producer: types.ModuleType | None = None) -> object:
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        return str(value)
    if type(value) is bytes:
        return {"kind": "bytes", "bytes": len(value),
                "sha256": hashlib.sha256(value).hexdigest(),
                "hex_prefix": value[:1024].hex(),
                "truncated": len(value) > 1024}
    if depth >= 12:
        return {"kind": type(value).__qualname__, "reason": "DEPTH LIMIT"}
    if type(value) in (list, tuple):
        if producer is not None and len(value) > MAX_VECTOR_PREFIX:
            return canonical_vector(value, producer)
        return [safe_detail(item, depth + 1, producer) for item in value]
    if type(value) is dict:
        return {str(key): safe_detail(item, depth + 1, producer)
                for key, item in value.items()}
    return {"kind": type(value).__qualname__, "plaintext": str(value)[:4096]}


def early_worker_failure(parsed: dict, error: BaseException,
                         phase: str, previous: types.ModuleType,
                         *, worker_process_id: int | None = None) -> dict:
    suite = parsed.get("--suite", "NOT AUTHENTICATED")
    suite_count = dict(previous.SUITES).get(suite, "NOT AUTHENTICATED")
    message = type(error).__qualname__ + ": " + str(error)
    traceback = []
    frame = error.__traceback__
    while frame is not None and len(traceback) < 32:
        traceback.append({
            "source": frame.tb_frame.f_code.co_filename,
            "function": frame.tb_frame.f_code.co_name,
            "line": frame.tb_lineno,
        })
        frame = frame.tb_next
    return {
        "schema": SCHEMA + "-actual-original-worker",
        "status": "FAIL",
        "failure_class": "CANDIDATE EXECUTION FAILURE",
        "failure_phase": phase,
        "candidate_family": "c",
        "label": LABEL,
        "suite": suite,
        "case_execution_denominator": suite_count,
        "mismatch_count": "NOT MEASURED",
        "observed_semantic_mismatch_lower_bound": 0,
        "error_type": type(error).__qualname__,
        "error_message": str(error),
        "plain_failure_diagnostic": message[:MAX_SUMMARY_DIAGNOSTIC],
        "plain_traceback": traceback,
        "traceback_truncated": frame is not None,
        "complete_genuine_failure_details": safe_detail(
            getattr(error, "details", None)
        ),
        "actual_candidate_workers": 1,
        "worker_process_id": os.getpid() if worker_process_id is None
                             else worker_process_id,
        "runtime_guard_installed_before_candidate_import":
            phase in ("OBSERVE COMPLETE ORIGINAL SUITE",
                      "ENCODE COMPLETE GUARDED RESULT"),
        "actual_c18_build_receipt_sha256": previous.BUILD_RECEIPT[1],
        "actual_c18_root_receipt_sha256": previous.ROOT_RECEIPT[1],
        "native_engine_sha256": previous.NATIVE_SHA256,
        "native_bridge_sha256": previous.NATIVE_SHA256,
        "corrected_source_sha256": previous.CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256": previous.ADAPTER[1],
        "original_source_targets_modified": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def suite_vector_summary(rows: list[dict], previous: types.ModuleType) -> dict:
    need(type(rows) is list and len(rows) == len(previous.SUITES),
         "preserve exactly one named outcome for every original C suite")
    output = []
    complete = []
    infrastructure = []
    executions = []
    worker_ids = []
    for row, (name, count) in zip(rows, previous.SUITES, strict=True):
        need(type(row) is dict and row.get("suite") == name
             and row.get("case_execution_denominator") == count,
             "reject reordered, omitted, fabricated, or denominator-changed C suite")
        failure = row.get("failure_class", "PASS")
        need(failure in ("PASS", "SEMANTIC MISMATCH",
                         "CANDIDATE EXECUTION FAILURE",
                         "WORKER TIMEOUT", "WORKER OUTPUT LIMIT",
                         "WORKER INFRASTRUCTURE FAILURE"),
             "classify every actual original C suite without hiding failures")
        if failure in ("PASS", "SEMANTIC MISMATCH"):
            need(type(row.get("mismatch_count")) is int
                 and row["mismatch_count"] >= 0,
                 "require an observed whole-suite mismatch count")
            complete.append(row)
        elif failure == "CANDIDATE EXECUTION FAILURE":
            executions.append(row)
        else:
            infrastructure.append(row)
        worker_id = row.get("worker_process_id")
        if row.get("actual_candidate_workers") == 1:
            need(type(worker_id) is int and worker_id > 0,
                 "bind every actual C suite to a real worker process")
            worker_ids.append(worker_id)
        diagnostic = row.get("plain_failure_diagnostic", "")
        output.append({
            "suite": name,
            "case_execution_denominator": count,
            "status": row.get("status"),
            "failure_class": failure,
            "failure_phase": row.get("failure_phase", "NOT APPLICABLE"),
            "mismatch_count": row.get("mismatch_count", "NOT MEASURED"),
            "worker_process_id": worker_id,
            "actual_candidate_workers": row.get("actual_candidate_workers", 0),
            "error_type": row.get("error_type", "NOT APPLICABLE"),
            "plain_failure_diagnostic": str(diagnostic)[:MAX_SUMMARY_DIAGNOSTIC],
        })
    lower_bound = sum(row["mismatch_count"] for row in complete)
    total = lower_bound if len(complete) == len(previous.SUITES) else "NOT MEASURED"
    verified = sum(row["case_execution_denominator"]
                   for row in complete if row.get("status") == "PASS"
                   and row.get("mismatch_count") == 0)
    distinct = len(worker_ids) == len(set(worker_ids))
    qualified = (len(complete) == len(previous.SUITES)
                 and len(worker_ids) == len(previous.SUITES)
                 and distinct and lower_bound == 0
                 and not infrastructure and not executions)
    return {
        "suite_outcomes": output,
        "attempted_suite_count": len(rows),
        "completed_suite_count": len(complete),
        "actual_candidate_workers": len(worker_ids),
        "actual_worker_process_ids": worker_ids,
        "actual_worker_process_ids_are_distinct": distinct,
        "semantic_mismatch_count": total,
        "observed_semantic_mismatch_lower_bound": lower_bound,
        "verified_passing_case_count": verified,
        "infrastructure_failure_count": len(infrastructure),
        "candidate_execution_failure_count": len(executions),
        "worker_timeout_count": sum(
            row.get("failure_class") == "WORKER TIMEOUT" for row in rows
        ),
        "candidate_qualified": qualified,
    }


def configure_previous(previous: types.ModuleType) -> tuple[types.ModuleType, object]:
    original_contract = previous.contract_document
    original_authority = previous.actual_authority

    def pinned_v7_authority() -> dict:
        authority = original_authority()
        authority["previous_failure_receipt_sha256"] = V6_RECEIPT[1]
        return authority

    previous.SOURCE = SOURCE
    previous.PROTOCOL = PROTOCOL
    previous.CONTRACT = CONTRACT
    previous.SCHEMA = SCHEMA
    previous.LABEL = LABEL
    previous.RECOVERY_ROOT = "/tmp/rebar-phase2-repaired-c-original-campaign-v7"
    previous.BACKUP_NAME = ".rebar-c-original-campaign-v7-original-native"
    previous.STAGE_NAME = ".rebar-c-original-campaign-v7-staged-native"
    previous.JOURNAL_NAME = "original-native-recovery-journal-v7.json"
    previous.MAX_WORKER_STDOUT = MAX_WORKER_STDOUT
    previous.MAX_WORKER_STDERR = MAX_WORKER_STDERR
    previous.WORKER_TIMEOUT_SECONDS = WORKER_TIMEOUT_SECONDS
    previous.actual_authority = pinned_v7_authority
    old = previous.bootstrap_previous()
    old.STATIC_OWNERS = tuple(old.STATIC_OWNERS) + V6 + (V6_RECEIPT,)
    old.OWNED_PATHS = frozenset(old.OWNED_PATHS) | {
        SOURCE, PROTOCOL, CONTRACT,
        *(item[0] for item in V6), V6_RECEIPT[0],
    }
    return old, original_contract


def preserved_v6(previous: types.ModuleType, old: types.ModuleType,
                 state: dict) -> dict:
    producer = old.load_producer(state["producer_raw"])
    raw = old.read_owner(V6_RECEIPT)
    receipt = validate_v6_receipt(
        previous.parse_document(producer, raw, "small authentic C V6 receipt"),
        previous,
    )
    predecessor = previous.parse_document(
        producer, old.read_owner(V6[2]), "complete historical frozen C V6 contract"
    )
    need(predecessor.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v6-source-freeze"
         and predecessor.get("version") == 6
         and predecessor.get("source", {}).get("sha256") == V6[0][1]
         and predecessor.get("protocol", {}).get("sha256") == V6[1][1]
         and predecessor.get("goal_sha256") == old.GOAL[1]
         and predecessor.get("holdout") == "NOT OPENED"
         and predecessor.get("performance") == "NOT MEASURED",
         "preserve the actual immutable complete C V6 source-freeze contract")
    return {
        "source_freeze_owners": [previous.record(item) for item in V6],
        "actual_failure_receipt": previous.record(V6_RECEIPT),
        "publication_status": receipt["publication_status"],
        "publication_pass_means": receipt["publication_pass_means"],
        "candidate_status": receipt["candidate_status"],
        "candidate_qualified": receipt["candidate_qualified"],
        "attempted_suite_count": receipt["attempted_suite_count"],
        "completed_suite_count": receipt["completed_suite_count"],
        "actual_candidate_workers": receipt["actual_candidate_workers"],
        "actual_worker_process_ids": receipt["actual_worker_process_ids"],
        "actual_worker_process_ids_are_distinct":
            receipt["actual_worker_process_ids_are_distinct"],
        "case_execution_denominator": receipt["case_execution_denominator"],
        "verified_passing_case_count": receipt["verified_passing_case_count"],
        "semantic_mismatch_count": receipt["semantic_mismatch_count"],
        "observed_semantic_mismatch_lower_bound":
            "NOT ESTABLISHED BY THE SMALL PUBLIC RECEIPT",
        "infrastructure_failure_count": receipt["infrastructure_failure_count"],
        "candidate_execution_failure_count":
            receipt["candidate_execution_failure_count"],
        "worker_timeout_count": receipt["worker_timeout_count"],
        "original_native_inode_restored": receipt["original_native_inode_restored"],
        "complete_suite_failure_causes": "NOT ESTABLISHED BY THE SMALL PUBLIC RECEIPT",
        "historical_archive_opened": False,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def contract_document(parsed: dict, old: types.ModuleType, state: dict,
                      previous: types.ModuleType, original_contract: object) -> dict:
    result = original_contract(parsed, old, state)
    result["version"] = 7
    result["status"] = "SOURCE FROZEN; ACTUAL C18 V7 ORIGINAL CAMPAIGN NOT RUN"
    result["status_scope"] = (
        "SOURCE FREEZE, PRESERVED ACTUAL V6 FAILURE AND V7 RUN AUTHORIZATION; "
        "NOT A V7 CANDIDATE RESULT"
    )
    result["original_reference_manifest_v1"]["candidate_authorization"] = (
        "LATEST P0 V4 AND EXPLICIT C V7 ONLY"
    )
    result["preserved_actual_c_v6_campaign"] = preserved_v6(previous, old, state)
    policy = result["actual_operation_policy"]
    policy.update({
        "max_worker_stdout_bytes": MAX_WORKER_STDOUT,
        "max_worker_stderr_bytes": MAX_WORKER_STDERR,
        "frozen_original_json_reader_maximum_bytes": 4 * 1024 * 1024,
        "worker_stdout_strictly_below_frozen_json_reader_maximum": True,
        "maximum_complete_vector_prefix_count": MAX_VECTOR_PREFIX,
        "complete_original_vector_digests_streamed_without_large_worker_json": True,
        "max_stored_plaintext_diagnostic_bytes": MAX_STORED_DIAGNOSTIC,
        "max_receipt_plaintext_diagnostic_bytes": MAX_SUMMARY_DIAGNOSTIC,
        "complete_named_suite_outcomes_in_small_receipt": True,
        "preserve_all_actual_worker_process_ids": True,
        "guard_bootstrap_failure_emits_canonical_worker_document": True,
        "worker_missing_stdout_preserves_bounded_plaintext_stderr": True,
        "worker_malformed_stdout_preserves_bounded_plaintext_stderr": True,
        "worker_oversized_stdout_preserves_bounded_plaintext_stderr": True,
        "semantic_mismatch_lower_bound_preserved_on_incomplete_campaign": True,
        "exact_semantic_mismatch_total_requires_all_13_complete_suites": True,
        "failure_phases": list(EARLY_PHASES),
    })
    result["actual_first_party_c18_build"]["candidate_matching"] = "NOT RUN BY V7"
    result["v7_candidate_correctness"] = "NOT MEASURED"
    return result


def source_controls(previous: types.ModuleType, wall: object,
                    old: types.ModuleType) -> list:
    answers = previous.hostile_controls(wall, old)
    suite = previous.SUITES[0][0]
    fake = {"--suite": suite}
    early = early_worker_failure(
        fake, RuntimeError("synthetic guard bootstrap denied"),
        "INSTALL FIRST-PARTY GUARD", previous, worker_process_id=943,
    )
    need(early["status"] == "FAIL"
         and early["failure_class"] == "CANDIDATE EXECUTION FAILURE"
         and early["failure_phase"] == "INSTALL FIRST-PARTY GUARD"
         and "synthetic guard bootstrap denied" in early["plain_failure_diagnostic"]
         and early["runtime_guard_installed_before_candidate_import"] is False,
         "emit an honest synthetic pre-observer guard/bootstrap failure")
    missing = bounded_plaintext(b"")
    oversized = bounded_plaintext(b"synthetic oversized diagnostics", 9)
    stderr = bounded_plaintext(b"RuntimeError: exact worker stderr\n")
    need(missing["bytes"] == 0 and missing["plaintext"] == ""
         and missing["truncated"] is False
         and oversized["truncated"] is True and oversized["stored_bytes"] == 9
         and oversized["plaintext"] == "synthetic"
         and "exact worker stderr" in stderr["plaintext"],
         "preserve missing, oversized, and literal stderr worker diagnostics")
    synthetic = []
    for index, (name, count) in enumerate(previous.SUITES, start=1):
        if name == "pep688_v4":
            synthetic.append({"suite": name, "case_execution_denominator": count,
                              "status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
                              "mismatch_count": 4, "actual_candidate_workers": 1,
                              "worker_process_id": 10000 + index})
        elif name == "public_v3":
            synthetic.append({"suite": name, "case_execution_denominator": count,
                              "status": "FAIL",
                              "failure_class": "WORKER INFRASTRUCTURE FAILURE",
                              "mismatch_count": "NOT MEASURED",
                              "actual_candidate_workers": 1,
                              "worker_process_id": 10000 + index,
                              "plain_failure_diagnostic": "synthetic empty stdout"})
        else:
            synthetic.append({"suite": name, "case_execution_denominator": count,
                              "status": "PASS", "failure_class": "PASS",
                              "mismatch_count": 0, "actual_candidate_workers": 1,
                              "worker_process_id": 10000 + index})
    summary = suite_vector_summary(synthetic, previous)
    need(summary["attempted_suite_count"] == 13
         and summary["completed_suite_count"] == 12
         and summary["observed_semantic_mismatch_lower_bound"] == 4
         and summary["semantic_mismatch_count"] == "NOT MEASURED"
         and summary["infrastructure_failure_count"] == 1
         and summary["actual_candidate_workers"] == 13
         and summary["actual_worker_process_ids_are_distinct"] is True
         and summary["candidate_qualified"] is False
         and len(summary["suite_outcomes"]) == 13,
         "preserve every synthetic suite and the real distinction between lower bound and total")
    producer = old.load_producer(old.read_owner(old.PRODUCER[0]))
    records = [{"case": index, "value": "authentic synthetic vector"}
               for index in range(MAX_VECTOR_PREFIX + 9)]
    expected = hashlib.sha256(producer.canonical(records)).hexdigest()
    compact = canonical_vector(records, producer, expected=expected)
    compact_raw = producer.canonical({"vector": compact, "summary": summary})
    decoded = producer.JsonReader(compact_raw).parse()
    need(producer.MAX_JSON_BYTES == 4 * 1024 * 1024
         and MAX_WORKER_STDOUT < producer.MAX_JSON_BYTES
         and len(compact_raw) < MAX_WORKER_STDOUT
         and compact["complete_vector_sha256"] == expected
         and compact["total_count"] == len(records)
         and compact["prefix_count"] == MAX_VECTOR_PREFIX
         and compact["truncated"] is True
         and decoded["vector"]["complete_vector_sha256"] == expected,
         "prove complete-vector integrity and a real worker document below the frozen 4 MiB reader")
    answers.extend((
        "synthetic guard/bootstrap failure emits canonical diagnostic",
        "synthetic empty worker stdout is preserved",
        "synthetic oversized worker output is bounded",
        "synthetic literal worker stderr is preserved",
        "synthetic all-13 named suite failure vector is preserved",
        "synthetic observed mismatch lower bound is not a fabricated total",
        "synthetic complete original vector digest is preserved",
        "synthetic canonical worker fits the frozen 4 MiB JSON reader",
    ))
    return answers


def stream_diagnostic(raw: bytes, limit: int) -> dict:
    record = bounded_plaintext(raw)
    record["limit_bytes"] = limit
    record["exceeds_worker_limit"] = len(raw) > limit
    return record


def worker_failure_result(name: str, count: int, process_id: int,
                          failure_class: str, output: bytes, errors: bytes,
                          returncode: object, error: BaseException | None = None,
                          *, phase: str = "ENCODE COMPLETE GUARDED RESULT") -> dict:
    stdout = stream_diagnostic(output, MAX_WORKER_STDOUT)
    stderr = stream_diagnostic(errors, MAX_WORKER_STDERR)
    if error is not None:
        detail = type(error).__qualname__ + ": " + str(error)
    elif stderr["plaintext"]:
        detail = stderr["plaintext"]
    elif stdout["plaintext"]:
        detail = stdout["plaintext"]
    else:
        detail = "worker produced no stdout and no stderr"
    return {
        "schema": SCHEMA + "-bounded-worker-result",
        "status": "FAIL",
        "failure_class": failure_class,
        "failure_phase": phase,
        "suite": name,
        "case_execution_denominator": count,
        "worker_process_id": process_id,
        "returncode": returncode,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "stdout": stdout,
        "stderr": stderr,
        "error_type": type(error).__qualname__ if error is not None
                       else "NOT ESTABLISHED",
        "error_message": str(error) if error is not None else "NOT ESTABLISHED",
        "plain_failure_diagnostic": detail[:MAX_SUMMARY_DIAGNOSTIC],
        "mismatch_count": "NOT MEASURED",
        "observed_semantic_mismatch_lower_bound": 0,
        "actual_candidate_workers": 1,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def execute_worker(parsed: dict, producer: types.ModuleType, active: dict,
                   name: str, count: int, previous: types.ModuleType) -> dict:
    subprocess = __import__("subprocess")
    environment = dict(os.environ)
    environment["LOCPATH"] = previous.LOCALE_ROOT
    environment["LC_ALL"] = "C"
    child = subprocess.Popen(
        previous.worker_arguments(parsed, name, active),
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env=environment, cwd=ROOT,
    )
    process_id = child.pid
    need(type(process_id) is int and process_id > 0,
         "require a real operating-system C V7 suite worker")
    try:
        output, errors = child.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        child.kill()
        output, errors = child.communicate()
        row = worker_failure_result(name, count, process_id, "WORKER TIMEOUT",
                                    output, errors, child.returncode, error,
                                    phase="OBSERVE COMPLETE ORIGINAL SUITE")
        row["worker_terminated"] = True
        return row
    except Exception as error:
        try:
            if child.poll() is None:
                child.kill()
            output, errors = child.communicate()
        except Exception as cleanup:
            output = b""
            errors = (type(cleanup).__qualname__ + ": " + str(cleanup)).encode(
                "utf-8", "backslashreplace"
            )
        return worker_failure_result(
            name, count, process_id, "WORKER INFRASTRUCTURE FAILURE",
            output, errors, child.returncode, error,
        )
    if len(output) > MAX_WORKER_STDOUT or len(errors) > MAX_WORKER_STDERR:
        return worker_failure_result(
            name, count, process_id, "WORKER OUTPUT LIMIT",
            output, errors, child.returncode,
        )
    try:
        document = previous.parse_document(
            producer, output, "complete guarded C V7 worker " + name
        )
        need(document.get("schema") == SCHEMA + "-actual-original-worker"
             and document.get("status") in ("PASS", "FAIL")
             and child.returncode == (0 if document["status"] == "PASS" else 1)
             and document.get("suite") == name
             and document.get("case_execution_denominator") == count
             and document.get("actual_candidate_workers") == 1,
             "reject incomplete, substituted, or ambiguous C V7 worker " + name)
    except Exception as error:
        return worker_failure_result(
            name, count, process_id, "WORKER INFRASTRUCTURE FAILURE",
            output, errors, child.returncode, error,
        )
    document["worker_process_id"] = process_id
    document["worker_process_returncode"] = child.returncode
    document["worker_stdout"] = {
        "bytes": len(output), "sha256": hashlib.sha256(output).hexdigest()
    }
    document["worker_stderr"] = bounded_plaintext(errors)
    document["worker_timeout_seconds"] = WORKER_TIMEOUT_SECONDS
    if document["status"] == "FAIL":
        detail = document.get("error_message") or errors.decode(
            "utf-8", "backslashreplace"
        ) or "original C suite reported a semantic mismatch"
        document["plain_failure_diagnostic"] = str(detail)[:MAX_SUMMARY_DIAGNOSTIC]
    return document


def publish_evidence(document: dict, producer: types.ModuleType,
                     previous: types.ModuleType) -> dict:
    gzip = __import__("gzip")
    raw = producer.canonical(document)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    suffix = "results" if document["candidate_status"] == "PASS" else "failures"
    stem = "repaired-c-original-campaign-v7-c-" + LABEL + "-" + suffix
    evidence = ROOT + "/oracle/phase2/evidence"

    def publish(name: str, payload: bytes) -> dict:
        parent = previous.directory(evidence, device=DEVICE)
        handle = None
        try:
            handle = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL
                | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
                0o600, dir_fd=parent,
            )
            before = os.fstat(handle)
            need(stat.S_ISREG(before.st_mode)
                 and before.st_dev == DEVICE and before.st_uid == os.geteuid()
                 and before.st_nlink == 1
                 and stat.S_IMODE(before.st_mode) == 0o600,
                 "publish only a new exclusive first-party C V7 evidence owner")
            previous.write_all(handle, payload)
            os.fsync(handle)
            after = os.fstat(handle)
            need((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
                 and after.st_size == len(payload),
                 "reject incomplete or substituted C V7 durable publication")
            os.close(handle)
            handle = None
            os.fsync(parent)
            return {
                "path": "oracle/phase2/evidence/" + name,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload), "device": after.st_dev,
                "inode": after.st_ino, "mode": "0600", "nlink": 1,
                "exclusive_creation": True,
                "file_fsync_completed": True,
                "directory_fsync_completed": True,
            }
        finally:
            if handle is not None:
                os.close(handle)
            os.close(parent)

    archive = publish(stem + ".json.gz", compressed)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "version": 7, "family": "c", "label": LABEL,
        "candidate_status": document["candidate_status"],
        "candidate_qualified": document["candidate_qualified"],
        "source_sha256": document["source_sha256"],
        "protocol_sha256": document["protocol_sha256"],
        "contract_sha256": document["contract_sha256"],
        "preserved_actual_v6_failure_receipt_sha256": V6_RECEIPT[1],
        "actual_c18_build_receipt_sha256": previous.BUILD_RECEIPT[1],
        "actual_c18_root_receipt_sha256": previous.ROOT_RECEIPT[1],
        "corrected_source_sha256": previous.CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256": previous.ADAPTER[1],
        "native_engine_sha256": previous.NATIVE_SHA256,
        "native_bridge_sha256": previous.NATIVE_SHA256,
        "suite_count": len(previous.SUITES),
        "case_execution_denominator": previous.ORIGINAL_CASE_COUNT,
        "named_private_waiver_count": 13,
        "separate_reference_case_count": previous.SEPARATE_REFERENCE_CASE_COUNT,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "original_source_targets_modified": 0,
        "original_native_inode_restored": document["original_native_inode_restored"],
        "archive": archive,
        "uncompressed_bytes": len(raw),
        "uncompressed_sha256": hashlib.sha256(raw).hexdigest(),
        "expanded_holdout_proposed_case_count":
            previous.EXPANDED_PROPOSED_CASE_COUNT,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    for key in ("suite_outcomes", "attempted_suite_count", "completed_suite_count",
                "actual_candidate_workers", "actual_worker_process_ids",
                "actual_worker_process_ids_are_distinct",
                "semantic_mismatch_count", "observed_semantic_mismatch_lower_bound",
                "verified_passing_case_count", "infrastructure_failure_count",
                "candidate_execution_failure_count", "worker_timeout_count"):
        receipt[key] = document[key]
    receipt_owner = publish(stem + "-publication-receipt.json",
                            producer.canonical(receipt))
    return {"archive": archive, "receipt": receipt, "receipt_owner": receipt_owner}


def protected_worker(parsed: dict, producer: types.ModuleType, state: dict,
                     previous: types.ModuleType) -> dict:
    try:
        row = previous.actual_worker(parsed, producer, state)
        observed = row.get("original_observation")
        if type(observed) is dict:
            compact = dict(observed)
            records = compact.get("candidate_records")
            if type(records) in (list, tuple):
                compact["candidate_records"] = canonical_vector(
                    records, producer,
                    expected=compact.get("candidate_records_sha256"),
                )
                need(compact["candidate_records"]["total_count"]
                     == compact.get("actual_candidate_case_count",
                                    compact["candidate_records"]["total_count"]),
                     "preserve the complete actual original candidate case denominator")
            mismatches = compact.get("all_mismatches")
            if type(mismatches) in (list, tuple):
                need(len(mismatches) == row.get("mismatch_count"),
                     "preserve the exact number of genuine original semantic mismatches")
                compact["all_mismatches"] = canonical_vector(mismatches, producer)
            row["original_observation"] = safe_detail(compact, 0, producer)
            row["all_original_records_and_mismatches_preserved"] = False
            row["all_original_record_and_mismatch_digests_preserved"] = True
            row["original_record_prefix_explicitly_truncated"] = bool(
                type(records) in (list, tuple) and len(records) > MAX_VECTOR_PREFIX
            )
        if row.get("status") == "FAIL":
            row["complete_genuine_failure_details"] = safe_detail(
                row.get("complete_genuine_failure_details"), 0, producer
            )
            row["plain_failure_diagnostic"] = (
                str(row.get("error_type", "CandidateError")) + ": "
                + str(row.get("error_message", "guarded original case failed"))
            )[:MAX_SUMMARY_DIAGNOSTIC]
            row.setdefault("failure_phase", "OBSERVE COMPLETE ORIGINAL SUITE")
        row.setdefault("observed_semantic_mismatch_lower_bound",
                       row.get("mismatch_count", 0)
                       if type(row.get("mismatch_count")) is int else 0)
        encoded = producer.canonical(row)
        need(len(encoded) <= MAX_WORKER_STDOUT
             and len(encoded) < producer.MAX_JSON_BYTES,
             "require a canonical whole-suite worker result below the frozen 4 MiB reader")
        return row
    except Exception as error:
        return early_worker_failure(
            parsed, error, "INSTALL FIRST-PARTY GUARD", previous
        )


def run_campaign(parsed: dict, producer: types.ModuleType, state: dict,
                 previous: types.ModuleType) -> dict:
    active = previous.activate_native(parsed, producer, state)
    original = active["original"]
    journal = active["journal_document"]
    rows = []
    recovery = None
    try:
        confirmed, _ = previous.read_private(
            previous.JOURNAL_NAME, active["journal"]["sha256"], producer
        )
        need(confirmed == journal,
             "require the durable exact-inode recovery journal before any worker")
        for index, (name, count) in enumerate(previous.SUITES, start=1):
            os.write(2, producer.canonical({
                "schema": SCHEMA + "-actual-suite-progress", "status": "START",
                "suite": name, "suite_index": index,
                "suite_count": len(previous.SUITES),
                "case_execution_denominator": count,
                "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            }))
            try:
                row = execute_worker(parsed, producer, active, name, count, previous)
            except Exception as error:
                row = {
                    "schema": SCHEMA + "-bounded-worker-result", "status": "FAIL",
                    "failure_class": "WORKER INFRASTRUCTURE FAILURE",
                    "failure_phase": "AUTHORIZE AND AUTHENTICATE SOURCE",
                    "suite": name, "case_execution_denominator": count,
                    "error_type": type(error).__qualname__,
                    "error_message": str(error),
                    "plain_failure_diagnostic": (
                        type(error).__qualname__ + ": " + str(error)
                    )[:MAX_SUMMARY_DIAGNOSTIC],
                    "mismatch_count": "NOT MEASURED",
                    "actual_candidate_workers": 0,
                    "holdout": "NOT OPENED", "performance": "NOT MEASURED",
                }
            rows.append(row)
            os.write(2, producer.canonical({
                "schema": SCHEMA + "-actual-suite-progress",
                "status": row["status"], "suite": name,
                "suite_index": index, "suite_count": len(previous.SUITES),
                "case_execution_denominator": count,
                "failure_class": row.get("failure_class", "PASS"),
                "failure_phase": row.get("failure_phase", "NOT APPLICABLE"),
                "mismatch_count": row.get("mismatch_count", "NOT MEASURED"),
                "actual_candidate_workers": row["actual_candidate_workers"],
                "worker_process_id": row.get("worker_process_id"),
                "plain_failure_diagnostic": str(
                    row.get("plain_failure_diagnostic", "")
                )[:MAX_SUMMARY_DIAGNOSTIC],
                "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            }))
    finally:
        recovery = previous.restore_native(
            journal, active["journal"]["sha256"], producer
        )
    need(recovery is not None and recovery.get("status") == "PASS"
         and recovery.get("restored_original") == original,
         "restore the exact original native inode before C V7 publication")
    summary = suite_vector_summary(rows, previous)
    qualified = summary["candidate_qualified"]
    report = {
        "schema": SCHEMA + "-actual-original-campaign",
        "status": "PASS" if qualified else "FAIL",
        "candidate_status": "PASS" if qualified else "FAIL",
        "version": 7, "family": "c", "label": LABEL,
        "source_sha256": parsed["--source-sha256"],
        "protocol_sha256": parsed["--protocol-sha256"],
        "contract_sha256": parsed["--contract-sha256"],
        "preserved_actual_v6_failure_receipt_sha256": V6_RECEIPT[1],
        "actual_c18_build_receipt_sha256": previous.BUILD_RECEIPT[1],
        "actual_c18_root_receipt_sha256": previous.ROOT_RECEIPT[1],
        "original_observer_source_sha256":
            previous.actual_authority()["producer_source_sha256"],
        "original_reference_manifest_sha256": previous.V1_MANIFEST[1],
        "runtime_guard_source_sha256":
            previous.actual_authority()["guard_source_sha256"],
        "corrected_source_sha256": previous.CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256": previous.ADAPTER[1],
        "native_engine_sha256": previous.NATIVE_SHA256,
        "native_bridge_sha256": previous.NATIVE_SHA256,
        "suite_count": len(previous.SUITES),
        "case_execution_denominator": previous.ORIGINAL_CASE_COUNT,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "suite_results": rows,
        "named_private_waiver_count": 13,
        "separate_reference_case_count": previous.SEPARATE_REFERENCE_CASE_COUNT,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "original_source_targets_modified": 0,
        "original_native_inode_restored": True,
        "native_recovery": recovery,
        "expanded_holdout_proposed_case_count":
            previous.EXPANDED_PROPOSED_CASE_COUNT,
        "runtime_non_delegation": "ESTABLISHED FOR THIS CANDIDATE RUN"
            if qualified else "NOT ESTABLISHED",
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    report.update(summary)
    publication = publish_evidence(report, producer, previous)
    return {
        "schema": SCHEMA + "-actual-publication", "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "candidate_status": report["candidate_status"],
        "candidate_qualified": qualified,
        "suite_count": len(previous.SUITES),
        "case_execution_denominator": previous.ORIGINAL_CASE_COUNT,
        **summary,
        "original_native_inode_restored": True,
        "archive_owner": publication["archive"],
        "receipt_owner": publication["receipt_owner"],
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "winner_selected": False,
    }


def fallback_quote(value: str) -> str:
    pieces = ['"']
    escapes = {
        "\\": "\\\\", '"': '\\"', "\b": "\\b", "\f": "\\f",
        "\n": "\\n", "\r": "\\r", "\t": "\\t",
    }
    for character in value:
        if character in escapes:
            pieces.append(escapes[character])
        elif ord(character) < 32:
            pieces.append("\\u" + format(ord(character), "04x"))
        elif ord(character) > 127:
            encoded = character.encode("utf-16-be", "surrogatepass")
            for offset in range(0, len(encoded), 2):
                pieces.append("\\u" + format(
                    int.from_bytes(encoded[offset:offset + 2], "big"), "04x"
                ))
        else:
            pieces.append(character)
    pieces.append('"')
    return "".join(pieces)


def fallback_canonical(value: object) -> bytes:
    def encode(item: object, depth: int) -> str:
        need(depth <= 48, "bound clean bootstrap failure JSON nesting")
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is int:
            return str(item)
        if type(item) is str:
            return fallback_quote(item)
        if type(item) in (list, tuple):
            return "[" + ",".join(encode(child, depth + 1)
                                    for child in item) + "]"
        if type(item) is dict:
            need(all(type(key) is str for key in item),
                 "require exact clean bootstrap failure document keys")
            return "{" + ",".join(
                fallback_quote(key) + ":" + encode(item[key], depth + 1)
                for key in sorted(item)
            ) + "}"
        raise CampaignError("reject unencodable clean bootstrap failure")

    return (encode(value, 0) + "\n").encode("ascii")


def main(arguments: list[str]) -> int:
    previous = None
    parsed = {}
    phase = "AUTHORIZE AND AUTHENTICATE SOURCE"
    worker_requested = type(arguments) is list and arguments.count("--worker") == 1
    try:
        clean_runtime()
        previous = bootstrap_v6()
        old, original_contract = configure_previous(previous)
        parsed = options(arguments, previous)

        def frozen_contract(selected: dict, frozen: types.ModuleType,
                            state: dict) -> dict:
            return contract_document(
                selected, frozen, state, previous, original_contract
            )

        previous.contract_document = frozen_contract
        original_controls = previous.hostile_controls

        def guarded_controls(wall: object, frozen: types.ModuleType) -> list:
            previous.hostile_controls = original_controls
            try:
                return source_controls(previous, wall, frozen)
            finally:
                previous.hostile_controls = guarded_controls

        previous.hostile_controls = guarded_controls
        phase = "AUTHENTICATE FROZEN ORIGINAL CONTEXT"
        producer, state, result = previous.collect_context(
            old, parsed, controls=parsed["mode"] == "--self-test"
        )
        mode = parsed["mode"]
        if mode == "--render-contract":
            sys.stdout.buffer.write(producer.canonical(
                frozen_contract(parsed, old, state)
            ))
            return 0
        if mode == "--self-test":
            result["schema"] = SCHEMA + "-self-test"
            result["hostile_control_count"] = len(result["hostile_controls"])
        elif mode == "--worker":
            phase = "INSTALL FIRST-PARTY GUARD"
            result = protected_worker(parsed, producer, state, previous)
        elif mode == "--run":
            result = run_campaign(parsed, producer, state, previous)
        elif mode == "--recover":
            result = previous.perform_recovery(parsed, producer)
        phase = "ENCODE COMPLETE GUARDED RESULT"
        encoded = producer.canonical(result)
        if mode == "--worker":
            need(len(encoded) <= MAX_WORKER_STDOUT
                 and len(encoded) < producer.MAX_JSON_BYTES,
                 "bound actual worker JSON below the frozen 4 MiB original reader")
        sys.stdout.buffer.write(encoded)
        return 0 if result.get("status") == "PASS" else 1
    except Exception as error:
        if worker_requested and previous is not None:
            if "--suite" not in parsed and arguments.count("--suite") == 1:
                index = arguments.index("--suite")
                if index + 1 < len(arguments):
                    parsed["--suite"] = arguments[index + 1]
            result = early_worker_failure(parsed, error, phase, previous)
            output = fallback_canonical(result)
            need(len(output) <= MAX_WORKER_STDOUT,
                 "bound early guard/bootstrap worker failure below the original reader")
            os.write(2, ("C18 V7 guarded worker: "
                         + result["plain_failure_diagnostic"] + "\n")
                     .encode("utf-8", "backslashreplace"))
            sys.stdout.buffer.write(output)
            return 1
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        os.write(2, ("C18 original campaign V7: "
                     + type(error).__qualname__ + ": " + str(error) + "\n")
                 .encode("utf-8", "backslashreplace"))
        raise SystemExit(2)
