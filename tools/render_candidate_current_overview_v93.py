#!/usr/bin/env python3
"""Show the measured progress of six from-scratch Python re replacements."""

from __future__ import annotations

import argparse
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v93.py"
OUTPUT = "docs/evidence/candidate-current-overview-v93"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v93"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 328
HISTORY_FLOOR = 333

V92 = {
    "source": (
        "tools/render_candidate_current_overview_v92.py",
        "752abbfbf6df750a66aa4419e32d4d66d8ee592405a76b28a649f3cadf98627d",
        96987,
        430553,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v92.inputs.json",
        "6c1e0a270ed5db1b6e7ebf389cc4448118eed633a946f8001404a11653f57306",
        14142,
        430560,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v92.summary.json",
        "7b00073b538f584d5f65cd1e05dbd8f3201ebfbcff119f8bead922ec95c90272",
        3402902,
        430561,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v92.svg",
        "9a3e3d84a8681d73ebf529e243c80fd142db34a36438d763f250e75eb1b986c1",
        9076,
        430738,
    ),
}

C_SOURCE = {
    "source": (
        "tools/run_owned_repaired_c_original_campaign_v9.py",
        "4796ba3c5e03a1341aa35f700679107a8bf835f0ebf582b02be59955ae211563",
        68216,
        430552,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V9.md",
        "7749e636b9adda7f28b5cfbe03c2895f45e3bbe8510c856bd8cdb9f441242997",
        7761,
        524983,
    ),
    "contract": (
        "oracle/phase2/repaired-c-original-campaign-v9.json",
        "b7afd2e67dfd9031b63628f87f68aa1e6e8759e60eeef26dec76419e75144eaa",
        28202,
        524987,
    ),
}

C_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v9-c-phase2-v21-c-original-match-semantics-"
    "original-p0-v9-failures-publication-receipt.json",
    "54b690fa487670dd0cb18cbc35e36f684666d7fb547c1aa30c48b244788effb6",
    7332,
    525075,
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

OLD_POOLS = (
    (
        "lossless_family_evidence_pool", 126464,
        "5e82ece260c65c1b651512bf82cc952f6b5c9219e2baf5526148fc254b9a0570", 9,
    ),
    (
        "lossless_actual_outcome_evidence_pool", 33507,
        "8adefd9ea0901086064674c4a9ba1300792a15ba381ffe93a0ef85c372dd345a", 1,
    ),
    (
        "lossless_zig_source_evidence_pool", 23792,
        "1c4694aae8738a74713ddca5f9e88a83b4fdc0c81ddeac7bbfa30eb5db65f029", 1,
    ),
    (
        "lossless_zig_actual_build_evidence_pool", 248256,
        "437c0d0f2f80e841fa7091d50b2094f9054e82c0e792f5db9de817cf2609dcae", 1,
    ),
    (
        "lossless_v87_source_evidence_pool", 71364,
        "c4acf498232c0e95b3bb6c7425acb2258915e9fc369e66bd27b8e6bfd8c389ff", 6,
    ),
    (
        "lossless_v87_rust_actual_build_evidence_pool", 11169,
        "7dadc62631aa838cfaa2a0c96d978b1457de11a4d3501fc2a6b456b319a30c21", 1,
    ),
    (
        "lossless_v88_captured_source_evidence_pool", 19857,
        "ea9c5c1778e361c58e684e2d5e139a276af7751887f8a0e671df260080e2afa9", 1,
    ),
    (
        "lossless_v88_captured_actual_build_evidence_pool", 11916,
        "01ee89ebdcf462cc2fc61721110bc94d4177deb1949e66d6c350909992cc58e9", 1,
    ),
    (
        "lossless_v88_c_source_evidence_pool", 19315,
        "2818bd96e62af5aa82b3ee0e0f03f8cbe56ac54955599e32379755e8dd366d1b", 1,
    ),
    (
        "lossless_v88_c_actual_build_evidence_pool", 14406,
        "264678f27d7ee4d2965d42f3129941ee49a5b041f66b16d090e629675bd3dd00", 1,
    ),
    (
        "lossless_v89_original_campaign_receipt_reference_pool", 19205,
        "5627d67752d6efaefea4c77d2904c32d568b32eaeed06ad721727f3753f632d7", 3,
    ),
    (
        "lossless_v90_zig_v10_original_campaign_evidence_pool", 137388,
        "28e58f4d3ce45cf90eaac4e5e6698c603fd6b128b6ca6b799d79e200884d432f", 1,
    ),
    (
        "lossless_v91_rust_v20_original_campaign_evidence_pool", 83702,
        "8346e978978f837f092f2030f26522847cbbd5f473da96eab062212304d52a18", 1,
    ),
    (
        "lossless_v92_zig_v12_original_campaign_evidence_pool", 135207,
        "38e9595f620c3de41d18bafd39ad7711e222dc8d913a488ec095cb9bd76166f5", 1,
    ),
)

POOL_KEY = "lossless_v93_c_v9_original_campaign_evidence_pool"
POOL_SCHEMA = SCHEMA + "-lossless-complete-c-original-campaign-pool-v1"
ENTRY_SCHEMA = SCHEMA + "-lossless-complete-c-original-campaign-entry-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-c-original-campaign-reference-v1"
LATEST_KEY = "c_v9_actual_original_campaign"

MISMATCHES = {
    "managed_v1": 16,
    "public_types_v1": 248,
    "substitution_v2": 224,
    "pep688_v4": 4,
}

EXECUTION_FAILURES = {
    "original_bounded_v5": (
        "ActualSuiteFailure",
        "OBSERVE COMPLETE ORIGINAL SUITE",
        "the guarded literal original upstream test failed",
    ),
    "public_v3": (
        "ActualSuiteFailure",
        "OBSERVE COMPLETE ORIGINAL SUITE",
        "the guarded original source-owned suite failed: public_v3",
    ),
    "scanner_v3": (
        "ActualSuiteFailure",
        "OBSERVE COMPLETE ORIGINAL SUITE",
        "the guarded original source-owned suite failed: scanner_v3",
    ),
    "buffer_v3": (
        "ActualSuiteFailure",
        "OBSERVE COMPLETE ORIGINAL SUITE",
        "the guarded original source-owned suite failed: buffer_v3",
    ),
    "public_surface_v19": (
        "CampaignError",
        "ENCODE COMPLETE GUARDED RESULT",
        "reject a forged function whose filename imitates frozen source: "
        "tools.python_re_public_surface_oracle_stage19.digest",
    ),
    "subinterpreter_v2": (
        "ActualSuiteFailure",
        "OBSERVE COMPLETE ORIGINAL SUITE",
        "preserve the actual guarded original child lifecycle failure",
    ),
}

ACTUAL_WORKER_PIDS = (
    81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 187, 188, 189,
)

CONTRACT_KEYS = frozenset({
    "actual_first_party_c21_build", "actual_operation_policy",
    "authenticated_cumulative_controller_transform", "candidate_correctness",
    "candidate_qualification", "expanded_holdout", "family",
    "first_party_match_semantics", "frozen_original_producer", "goal_sha256",
    "holdout", "label", "memory", "original_reference_manifest_v1", "performance",
    "phase", "phase_one_v4", "pinned_cpython", "preserved_actual_c_v6_campaign",
    "preserved_actual_c_v7_campaign", "preserved_full_v8_reporting_freeze",
    "protocol", "qualified_candidate_count", "runtime_non_delegation", "schema",
    "source", "source_only_effects", "source_wall", "status", "status_scope",
    "strict_runtime_guard", "supplemental_candidate_correctness",
    "undefined_behavior", "version", "winner_selected",
})

RECEIPT_KEYS = frozenset({
    "actual_c21_build_receipt_sha256", "actual_c21_root_receipt_sha256",
    "actual_candidate_workers", "actual_worker_process_ids",
    "actual_worker_process_ids_are_distinct", "archive", "attempted_suite_count",
    "benchmark_files_read", "candidate_execution_failure_count",
    "candidate_qualified", "candidate_status", "case_execution_denominator",
    "clock_samples", "completed_suite_count", "contract_sha256",
    "corrected_source_sha256", "expanded_holdout_proposed_case_count", "family",
    "hidden_cases_read", "holdout", "infrastructure_failure_count", "label",
    "memory", "named_private_waiver_count", "native_bridge_sha256",
    "native_engine_sha256", "observed_semantic_mismatch_lower_bound",
    "original_native_inode_restored", "original_source_targets_modified",
    "performance", "preserved_actual_v6_failure_receipt_sha256",
    "preserved_actual_v7_failure_receipt_sha256", "protocol_sha256",
    "publication_pass_means", "publication_status", "schema",
    "semantic_mismatch_count", "separate_reference_case_count",
    "separate_reference_cases_counted_as_candidate_cases", "source_sha256",
    "status", "suite_count", "suite_outcomes", "timing_trials_run",
    "unchanged_adapter_sha256", "uncompressed_bytes", "uncompressed_sha256",
    "undefined_behavior", "verified_passing_case_count", "version",
    "winner_selected", "worker_timeout_count", "worker_timeout_seconds",
})

ROW_KEYS = frozenset({
    "actual_candidate_workers", "case_execution_denominator", "error_type",
    "failure_class", "failure_phase", "mismatch_count", "plain_failure_diagnostic",
    "status", "suite", "worker_process_id",
})


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject unbounded complete V93 evidence: " + label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(handle)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted complete V93 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V93 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V93 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject changed complete V93 owner: " + label)
        return raw
    finally:
        os.close(handle)


FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
    "os.fork", "os.forkpty", "ctypes.dlopen", "ctypes.dlsym", "socket.__new__",
    "socket.connect", "socket.bind", "socket.sendto",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex", "re", "_sre", "ctypes", "subprocess", "multiprocessing", "socket",
    "time", "gzip", "bz2", "lzma", "tarfile", "zipfile", "candidates", "rebar",
})


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V93 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V93 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V93 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V93 rejected an unverified descriptor or file owner")
    if mode not in (None, "r", "rb"):
        raise ValueError("V93 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V93 source-only operation cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V93 rejected private roots or unopened holdout cases")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V93 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v93." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V93 rejected outputs, archives, or benchmarks: " + normalized)


def load_previous() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, tuple, types.ModuleType,
]:
    raw = read_fixed(V92["source"], "whole actually published V92 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v92")
    previous.__file__ = str(ROOT / V92["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v91, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base = (
        previous.load_previous()
    )
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v92"
        and previous.SELF == V92["source"][0]
        and tuple(previous.SUITES) == SUITES
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 15,
        "require pinned isolated CPython, immutable V92 history and exact P0",
    )
    return previous, v91, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V92["source"][1],
        "source_bytes": V92["source"][2],
        "zig_receipt_sha256": previous.ZIG_RECEIPT[1],
    }
    for role, item in previous.V91.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.ZIG_SOURCE.items():
        pins["zig_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def authenticate_previous(
    previous: types.ModuleType,
    v91: types.ModuleType,
    v90: types.ModuleType,
    v89: types.ModuleType,
    v88: types.ModuleType,
    v87: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    snapshot, assets = previous.build(
        v91, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
        previous_options(previous),
    )
    for role in ("inputs", "summary", "svg"):
        item = V92[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole pushed V92 " + role),
            "reconstruct every complete byte of the published V92 " + role,
        )
    old = base.document(assets[V92["summary"][0]], "whole immutable V92 summary")
    historical = old["previous_v88_snapshot"]
    base.need(
        old["version"] == 92
        and old["snapshot"] == snapshot
        and old["authenticated_evidence_owner_lower_bound"] == 324
        and old["authenticated_history_reference_lower_bound"] == 329
        and [row.get("family") for row in old["families"]]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and old["families"][0]["correctness"] == "BASELINE PASS"
        and old["lossless_v89_all_eleven_previous_pool_identity_status"] == "PASS"
        and old["lossless_v90_all_twelve_previous_pool_identity_status"] == "PASS"
        and old["lossless_v91_all_thirteen_previous_pool_identity_status"] == "PASS"
        and old["lossless_v89_complete_original_suite_reference_count"] == 39
        and old["lossless_v90_zig_v10_complete_plaintext_receipt_count"] == 1
        and old["lossless_v90_zig_v10_complete_source_owner_count"] == 3
        and old["lossless_v90_zig_v10_complete_original_suite_count"] == 13
        and old["lossless_v91_rust_v20_complete_plaintext_receipt_count"] == 1
        and old["lossless_v91_rust_v20_complete_source_owner_count"] == 3
        and old["lossless_v91_rust_v20_complete_original_suite_count"] == 13
        and old["lossless_v92_zig_v12_complete_plaintext_receipt_count"] == 1
        and old["lossless_v92_zig_v12_complete_source_owner_count"] == 3
        and old["lossless_v92_zig_v12_complete_original_suite_count"] == 13
        and old["original_case_execution_denominator"] == CASE_COUNT
        and old["original_suite_count"] == 13
        and old["named_private_waiver_count"] == 13
        and old["separate_additional_reference_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and old["additional_cases_included_in_original_denominator"] is False
        and old["c_v7_original_campaign_clean_suite_count"] == 2
        and old["c_v7_original_campaign_completed_suite_count"] == 5
        and old["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and old["c_v7_original_campaign_observed_mismatch_lower_bound"] == 236
        and old["c_v7_original_campaign_candidate_execution_failure_count"] == 7
        and old["c_v7_original_campaign_infrastructure_failure_count"] == 1
        and old["rust_v19_original_campaign_clean_suite_count"] == 6
        and old["rust_v19_original_campaign_completed_suite_count"] == 8
        and old["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and old["rust_v19_original_campaign_observed_mismatch_lower_bound"] == 1296
        and old["rust_v19_original_campaign_infrastructure_failure_count"] == 5
        and old["rust_v19_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
        and old["rust_v20_original_campaign_actual_worker_count"] == 13
        and old["rust_v20_original_campaign_distinct_worker_count"] == 13
        and old["rust_v20_original_campaign_clean_suite_count"] == 10
        and old["rust_v20_original_campaign_completed_suite_count"] == 12
        and old["rust_v20_original_campaign_mismatch_suite_count"] == 2
        and old["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and old["rust_v20_original_campaign_observed_mismatch_lower_bound"] == 1296
        and old["rust_v20_original_campaign_infrastructure_failure_count"] == 1
        and old["rust_v20_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
        and old["rust_v20_original_campaign_all_four_original_targets_restored"]
        is True
        and old["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and old["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and old["zig_v10_original_campaign_observed_mismatch_lower_bound"] == 1540
        and old["zig_v12_original_campaign_actual_worker_count"] == 13
        and old["zig_v12_original_campaign_distinct_worker_count"] == 13
        and old["zig_v12_original_campaign_individually_proven_guarded_candidate_import_count"]
        == 13
        and old["zig_v12_original_campaign_candidate_import_status_unknown_count"] == 0
        and old["zig_v12_original_campaign_clean_suite_count"] == 7
        and old["zig_v12_original_campaign_completed_suite_count"] == 12
        and old["zig_v12_original_campaign_mismatch_suite_count"] == 5
        and old["zig_v12_original_campaign_verified_passing_case_count"] == 4607
        and old["zig_v12_original_campaign_observed_mismatch_lower_bound"] == 1700
        and old["zig_v12_original_campaign_infrastructure_failure_count"] == 1
        and old["zig_v12_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
        and old["zig_v12_original_campaign_all_three_original_targets_restored"]
        is True
        and historical["actual_rust_semantic_mismatch_count"] == 1440
        and historical["actual_rust_verified_passing_case_count"] == 14853
        and historical["actual_c_semantic_mismatch_count"] == 1230
        and historical["actual_c_verified_passing_case_count"] == 7325
        and historical["actual_zig_semantic_mismatch_count"] == 1764
        and old["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and old["preserved_previous_holdout_proposal_case_count"]
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and old["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
        and old["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and old["qualified_candidate_count"] == 0
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["performance"] == "NOT MEASURED"
        and old["memory"] == "NOT MEASURED"
        and old["undefined_behavior"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False
        and old["winner_selected"] is False,
        "preserve exact C, Rust, guarded Zig, all previous history and sealed P0",
    )
    for key, size, digest, count in OLD_POOLS:
        value = old.get(key)
        whole = base.canonical(value)
        base.need(
            type(value) is dict
            and len(whole) == size
            and base.digest(whole) == digest
            and type(value.get("entries")) is dict
            and len(value["entries"]) == count,
            "preserve complete exact historical V92 proof pool: " + key,
        )
    return old


def validate_source_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == CONTRACT_KEYS,
        "authenticate all 35 fields of the complete actual C V9 source contract",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"] == "rebar-owned-repaired-c-original-campaign-v9-source-freeze"
        and value["version"] == 9
        and value["family"] == "c"
        and value["phase"] == "PHASE 2: CANDIDATES"
        and value["label"] == "phase2-v21-c-original-match-semantics-original-p0-v9"
        and value["status"]
        == "SOURCE FROZEN; ACTUAL C21 V9 ORIGINAL CAMPAIGN NOT RUN"
        and value["status_scope"]
        == "CUMULATIVE V8 REPORTING, AUTHENTIC C21 BUILD, AND EXPLICIT ORIGINAL "
        "RUN AUTHORIZATION; NOT A CANDIDATE RESULT"
        and value["candidate_correctness"] == "NOT MEASURED"
        and value["candidate_qualification"] == "NOT ESTABLISHED"
        and value["supplemental_candidate_correctness"] == "NOT MEASURED"
        and value["qualified_candidate_count"] == 0
        and value["runtime_non_delegation"] == "NOT ESTABLISHED"
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject source-freeze-as-pass, fake C compatibility or speed claims",
    )
    for role in ("source", "protocol"):
        item = C_SOURCE[role]
        base.need(
            base.canonical(value[role])
            == base.canonical(base.pin(item[0], item[1], item[2])),
            "authenticate the exact complete C V9 " + role,
        )
    phase_one = value["phase_one_v4"]
    base.need(
        type(phase_one) is dict
        and phase_one["status"] == "PASS"
        and phase_one["original_case_execution_denominator"] == CASE_COUNT
        and phase_one["original_suite_count"] == len(SUITES)
        and phase_one["named_private_waiver_count"] == len(SUITES)
        and phase_one["separate_reference_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and phase_one["separate_reference_cases_counted_in_original_denominator"]
        is False,
        "retain the unchanged original Python oracle and separately counted checks",
    )
    producer = value["frozen_original_producer"]
    base.need(
        type(producer) is dict
        and producer["version"] == 5
        and producer["family_count"] == 6
        and producer["suite_count"] == len(SUITES)
        and producer["case_execution_denominator"] == CASE_COUNT
        and producer["candidate_source_file_modified"] is False
        and producer["authenticated_corrected_family_overlay_in_memory_only"] is True
        and type(producer["suites"]) is list
        and len(producer["suites"]) == len(SUITES),
        "retain all thirteen frozen original source-owned candidate observations",
    )
    for row, (suite, count) in zip(producer["suites"], SUITES, strict=True):
        base.need(
            type(row) is dict
            and row.get("suite") == suite
            and row.get("case_execution_count") == count,
            "reject an invented or weakened original C suite: " + suite,
        )
    first_party = value["first_party_match_semantics"]
    base.need(
        type(first_party) is dict
        and first_party["another_candidate_engine"] == "FORBIDDEN"
        and first_party["cpython_sre_engine"] == "FORBIDDEN"
        and first_party["external_regex_engine"] == "FORBIDDEN"
        and first_party["fallback"] == "FORBIDDEN"
        and first_party["source_path_materialized_in_workspace"] is False,
        "reject third-party wrappers, CPython regex, sibling engines and fallback",
    )
    guard = value["strict_runtime_guard"]
    base.need(
        type(guard) is dict
        and guard["version"] == 2
        and guard["guard_installed_before_candidate_import"] is True
        and guard["nested_original_case_count"] == 128
        and guard["required_child_interpreters"] == 11
        and guard["required_nested_case_executions"] == 394
        and guard["runtime_non_delegation"] == "NOT ESTABLISHED",
        "preserve the strict source-frozen guard without inventing C worker proofs",
    )
    proposal = value["expanded_holdout"]
    base.need(
        type(proposal) is dict
        and proposal["proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and proposal["case_status"] == "NOT GENERATED; NOT OPENED"
        and proposal["final_protocol_status"] == "NOT FROZEN"
        and proposal["source_mode_holdout_files_read"] == 0,
        "keep the proposed final performance comparison frozen and unopened",
    )
    effects = value["source_only_effects"]
    base.need(
        type(effects) is dict and len(effects) == 16
        and all(type(number) is int and number == 0 for number in effects.values()),
        "reject source-mode candidate execution, compilation, clocks or file changes",
    )
    policy = value["actual_operation_policy"]
    base.need(
        type(policy) is dict
        and policy["all_original_candidate_cases_required"] == CASE_COUNT
        and policy["all_original_suite_workers_required"] == len(SUITES)
        and policy["actual_worker_process_ids_required"] is True
        and policy["actual_original_inode_restoration_required"] is True
        and policy["worker_timeout_seconds"] == 120
        and policy["fallback"] == "FORBIDDEN",
        "preserve separate explicit matching authority and original restoration",
    )
    build = value["actual_first_party_c21_build"]
    base.need(
        type(build) is dict
        and build["build_status"] == "PASS"
        and build["build_pass_means"] == "DURABLE FIRST-PARTY C MATCH-SOURCE BUILD ONLY"
        and build["candidate_correctness"] == "NOT MEASURED"
        and build["candidate_matching"] == "NOT RUN"
        and build["corrected_c_source_sha256"]
        == "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
        and build["corrected_native_sha256"]
        == "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60"
        and build["native_opened_in_source_mode"] is False
        and build["root_opened_in_source_mode"] is False,
        "distinguish historical first-party build evidence from candidate success",
    )
    pinned = value["pinned_cpython"]
    base.need(
        type(pinned) is dict
        and pinned["path"] == PYTHON
        and pinned["version"] == "3.14.6"
        and pinned["required_flags"] == ["-I", "-B", "-S"],
        "retain the exact pinned isolated CPython correctness baseline",
    )
    return value


def validate_c_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == RECEIPT_KEYS,
        "authenticate all 53 fields of the actual complete C V9 public receipt",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-c-original-campaign-v9-durable-publication-receipt"
        and value["version"] == 9
        and value["family"] == "c"
        and value["label"] == "phase2-v21-c-original-match-semantics-original-p0-v9"
        and value["status"] == "PASS"
        and value["publication_status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE CORRECTNESS PUBLICATION ONLY"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["source_sha256"] == C_SOURCE["source"][1]
        and value["protocol_sha256"] == C_SOURCE["protocol"][1]
        and value["contract_sha256"] == C_SOURCE["contract"][1]
        and value["suite_count"] == len(SUITES)
        and value["attempted_suite_count"] == len(SUITES)
        and value["named_private_waiver_count"] == len(SUITES)
        and value["case_execution_denominator"] == CASE_COUNT
        and value["actual_candidate_workers"] == 13
        and value["actual_worker_process_ids_are_distinct"] is True
        and value["actual_worker_process_ids"] == list(ACTUAL_WORKER_PIDS)
        and value["completed_suite_count"] == 7
        and value["verified_passing_case_count"] == 13606
        and value["observed_semantic_mismatch_lower_bound"] == 492
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["candidate_execution_failure_count"] == 6
        and value["infrastructure_failure_count"] == 0
        and value["worker_timeout_count"] == 0
        and value["worker_timeout_seconds"] == 120
        and value["original_native_inode_restored"] is True
        and value["original_source_targets_modified"] == 0
        and value["separate_reference_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and value["separate_reference_cases_counted_as_candidate_cases"] is False
        and value["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and value["hidden_cases_read"] == 0
        and value["benchmark_files_read"] == 0
        and value["clock_samples"] == 0
        and value["timing_trials_run"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject publication-as-success, fake C qualification or measured speed",
    )
    base.need(
        value["actual_c21_build_receipt_sha256"]
        == "9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df"
        and value["actual_c21_root_receipt_sha256"]
        == "8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2"
        and value["corrected_source_sha256"]
        == "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
        and value["native_bridge_sha256"]
        == "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60"
        and value["native_engine_sha256"] == value["native_bridge_sha256"]
        and value["unchanged_adapter_sha256"]
        == "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
        and value["preserved_actual_v6_failure_receipt_sha256"]
        == "868fdd4df9ed960113c324c1dda82d12d2e700d5c32213a4d8c147384b64b081"
        and value["preserved_actual_v7_failure_receipt_sha256"]
        == "bba4b8498a37db0bf9651c0bb040deaf96f9eef363ba6f2e2c923379d7fa5080",
        "preserve actual first-party build and historical C outcomes as metadata",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and archive["path"]
        == "oracle/phase2/evidence/"
        "repaired-c-original-campaign-v9-c-phase2-v21-c-original-match-semantics-"
        "original-p0-v9-failures.json.gz"
        and archive["sha256"]
        == "b6222960cf7b2945d0e0dec738269bf4bab3179bf01f3d00772e5de0c1a8ce6d"
        and archive["bytes"] == 40353
        and archive["device"] == 2064
        and archive["inode"] == 525074
        and archive["mode"] == "0600"
        and archive["nlink"] == 1
        and archive["exclusive_creation"] is True
        and archive["file_fsync_completed"] is True
        and archive["directory_fsync_completed"] is True
        and value["uncompressed_bytes"] == 1085585
        and value["uncompressed_sha256"]
        == "2e3258bc64672dc6e91e2b8e196790c7ac831651b3b02e8bb02af066b9d608ce",
        "retain archive metadata exclusively from the complete public C receipt",
    )
    rows = value["suite_outcomes"]
    base.need(
        type(rows) is list and len(rows) == len(SUITES),
        "preserve all thirteen complete real C V9 worker observations",
    )
    clean: list[dict] = []
    mismatches: list[dict] = []
    failures: list[dict] = []
    process_ids: set[int] = set()
    for index, (row, (suite, denominator)) in enumerate(
        zip(rows, SUITES, strict=True)
    ):
        base.need(
            type(row) is dict and set(row) == ROW_KEYS
            and row["suite"] == suite
            and row["case_execution_denominator"] == denominator
            and row["actual_candidate_workers"] == 1
            and type(row["worker_process_id"]) is int
            and row["worker_process_id"] == ACTUAL_WORKER_PIDS[index]
            and row["worker_process_id"] not in process_ids,
            "reject omitted, duplicated or invented actual C worker: " + suite,
        )
        process_ids.add(row["worker_process_id"])
        if suite in EXECUTION_FAILURES:
            error, phase, diagnostic = EXECUTION_FAILURES[suite]
            base.need(
                row["status"] == "FAIL"
                and row["failure_class"] == "CANDIDATE EXECUTION FAILURE"
                and row["error_type"] == error
                and row["failure_phase"] == phase
                and row["plain_failure_diagnostic"] == diagnostic
                and row["mismatch_count"] == "NOT MEASURED",
                "reject a hidden genuine C candidate execution failure: " + suite,
            )
            failures.append(row)
        elif suite in MISMATCHES:
            base.need(
                row["status"] == "FAIL"
                and row["failure_class"] == "SEMANTIC MISMATCH"
                and row["failure_phase"] == "OBSERVE COMPLETE ORIGINAL SUITE"
                and row["error_type"] == "NOT APPLICABLE"
                and row["plain_failure_diagnostic"]
                == "original C suite reported a semantic mismatch"
                and row["mismatch_count"] == MISMATCHES[suite],
                "reject concealed genuine C semantic differences: " + suite,
            )
            mismatches.append(row)
        else:
            base.need(
                row["status"] == "PASS"
                and row["failure_class"] == "PASS"
                and row["failure_phase"] == "NOT APPLICABLE"
                and row["error_type"] == "NOT APPLICABLE"
                and row["plain_failure_diagnostic"] == ""
                and row["mismatch_count"] == 0,
                "reject an invented complete passing original C group: " + suite,
            )
            clean.append(row)
    base.need(
        len(process_ids) == 13
        and len(clean) == 3
        and len(mismatches) == 4
        and len(failures) == 6
        and len(clean) + len(mismatches) == value["completed_suite_count"]
        and sum(row["case_execution_denominator"] for row in clean) == 13606
        and sum(row["mismatch_count"] for row in mismatches) == 492
        and {row["suite"]: row["mismatch_count"] for row in mismatches}
        == MISMATCHES
        and [row["worker_process_id"] for row in rows]
        == value["actual_worker_process_ids"],
        "derive three clean, four differing and six genuinely failing C groups",
    )
    return {
        "family": "c",
        "display_name": "C",
        "actual_candidate_worker_count": 13,
        "unique_candidate_worker_count": 13,
        "attempted_suite_count": 13,
        "clean_suite_count": 3,
        "completed_suite_count": 7,
        "mismatch_suite_count": 4,
        "candidate_execution_failure_count": 6,
        "infrastructure_failure_count": 0,
        "worker_timeout_count": 0,
        "verified_passing_case_count": 13606,
        "observed_semantic_mismatch_lower_bound": 492,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "all_original_suite_rows_validated": True,
        "all_original_observation_vectors_complete": False,
        "original_native_inode_restored": True,
        "original_source_targets_modified": 0,
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": C_SOURCE["source"][1],
        "protocol_sha256": C_SOURCE["protocol"][1],
        "contract_sha256": C_SOURCE["contract"][1],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["bytes"],
        "archive_opened_by_graph": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def load_c_evidence(base: types.ModuleType) -> tuple[dict, dict, dict]:
    raws = {
        role: read_fixed(item, "whole first-party C V9 " + role)
        for role, item in C_SOURCE.items()
    }
    contract = base.document(raws["contract"], "whole actual C V9 source contract")
    base.need(
        base.canonical(contract) == raws["contract"],
        "reject noncanonical or partial C V9 source-freeze contract",
    )
    validate_source_contract(base, contract)
    raw = read_fixed(C_RECEIPT, "whole actually pushed C V9 public receipt")
    receipt = base.document(raw, "whole actual pushed C V9 public receipt")
    base.need(
        base.canonical(receipt) == raw,
        "reject noncanonical or partial actual C V9 plaintext public receipt",
    )
    return contract, receipt, validate_c_receipt(base, receipt)


def compact_suite_proof(base: types.ModuleType, row: dict) -> dict:
    raw = base.canonical(row)
    return {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_public_suite_row_sha256": base.digest(raw),
        "complete_public_suite_row_canonical_bytes": len(raw),
        "actual_candidate_workers": row["actual_candidate_workers"],
        "worker_process_id": row["worker_process_id"],
        "status": row["status"],
        "failure_class": row["failure_class"],
        "failure_phase": row["failure_phase"],
        "error_type": row["error_type"],
        "mismatch_count": row["mismatch_count"],
        "plain_failure_diagnostic": row["plain_failure_diagnostic"],
    }


def make_evidence_pool(
    base: types.ModuleType, contract: dict, receipt: dict, facts: dict,
) -> dict:
    entry = {
        "schema": ENTRY_SCHEMA,
        "family": "c",
        "complete_plaintext_receipt_owner": base.synthetic_owner(
            C_RECEIPT[:3], C_RECEIPT[3]
        ),
        "complete_plaintext_receipt_sha256": C_RECEIPT[1],
        "complete_plaintext_receipt_bytes": C_RECEIPT[2],
        "complete_plaintext_receipt_field_count": len(RECEIPT_KEYS),
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt": copy.deepcopy(receipt),
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in C_SOURCE.items()
        },
        "complete_source_contract_field_count": len(CONTRACT_KEYS),
        "complete_source_contract_embedded": True,
        "complete_source_contract": copy.deepcopy(contract),
        "complete_original_suite_count": 13,
        "complete_original_suite_rows": [
            compact_suite_proof(base, row) for row in receipt["suite_outcomes"]
        ],
        "validated_campaign_outcome": copy.deepcopy(facts),
        "compressed_archive_opened_by_graph": False,
        "private_build_root_opened_by_graph": False,
        "complete_failure_diagnostics_available_without_archive": True,
    }
    pool = {
        "schema": POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "complete_public_receipt_count": 1,
        "complete_first_party_source_owner_count": 3,
        "entries": {C_RECEIPT[1]: entry},
    }
    validate_evidence_pool(base, pool, contract, receipt, facts)
    return pool


def validate_evidence_pool(
    base: types.ModuleType,
    pool: object,
    contract: dict,
    receipt: dict,
    facts: dict,
) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {
            "schema", "version", "hash_algorithm", "complete_public_receipt_count",
            "complete_first_party_source_owner_count", "entries",
        }
        and pool["schema"] == POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and pool["complete_public_receipt_count"] == 1
        and pool["complete_first_party_source_owner_count"] == 3
        and type(pool["entries"]) is dict
        and set(pool["entries"]) == {C_RECEIPT[1]},
        "require one complete actual C V9 owner-addressed campaign outcome",
    )
    assert isinstance(pool, dict)
    entry = pool["entries"][C_RECEIPT[1]]
    rows = [compact_suite_proof(base, row) for row in receipt["suite_outcomes"]]
    base.need(
        type(entry) is dict
        and entry["schema"] == ENTRY_SCHEMA
        and entry["family"] == "c"
        and base.canonical(entry["complete_plaintext_receipt_owner"])
        == base.canonical(base.synthetic_owner(C_RECEIPT[:3], C_RECEIPT[3]))
        and entry["complete_plaintext_receipt_sha256"] == C_RECEIPT[1]
        and entry["complete_plaintext_receipt_bytes"] == C_RECEIPT[2]
        and entry["complete_plaintext_receipt_field_count"] == len(RECEIPT_KEYS)
        and entry["complete_plaintext_receipt_embedded"] is True
        and base.canonical(entry["complete_plaintext_receipt"])
        == base.canonical(receipt)
        and entry["complete_first_party_source_owner_count"] == 3
        and entry["complete_source_contract_field_count"] == len(CONTRACT_KEYS)
        and entry["complete_source_contract_embedded"] is True
        and base.canonical(entry["complete_source_contract"])
        == base.canonical(contract)
        and entry["complete_original_suite_count"] == 13
        and base.canonical(entry["complete_original_suite_rows"])
        == base.canonical(rows)
        and base.canonical(entry["validated_campaign_outcome"])
        == base.canonical(facts)
        and entry["compressed_archive_opened_by_graph"] is False
        and entry["private_build_root_opened_by_graph"] is False
        and entry["complete_failure_diagnostics_available_without_archive"] is True,
        "reject omitted, fabricated or partial genuine C V9 campaign evidence",
    )
    owners = entry["complete_first_party_source_owners"]
    base.need(
        type(owners) is dict and set(owners) == set(C_SOURCE),
        "retain exactly three individually authenticated C V9 source owners",
    )
    for role, item in C_SOURCE.items():
        base.need(
            base.canonical(owners[role])
            == base.canonical(base.synthetic_owner(item[:3], item[3])),
            "retain exact complete authenticated C V9 source owner: " + role,
        )


def make_reference(base: types.ModuleType, pool: dict) -> dict:
    raw = base.canonical(pool["entries"][C_RECEIPT[1]])
    return {
        "schema": REFERENCE_SCHEMA,
        "family": "c",
        "complete_plaintext_receipt_sha256": C_RECEIPT[1],
        "complete_plaintext_receipt_bytes": C_RECEIPT[2],
        "complete_first_party_source_owner_count": 3,
        "complete_reference_sha256": base.digest(raw),
        "complete_reference_canonical_bytes": len(raw),
    }


def resolve_reference(base: types.ModuleType, pool: dict, value: object) -> dict:
    base.need(
        type(value) is dict
        and set(value) == {
            "schema", "family", "complete_plaintext_receipt_sha256",
            "complete_plaintext_receipt_bytes", "complete_first_party_source_owner_count",
            "complete_reference_sha256", "complete_reference_canonical_bytes",
        }
        and value["schema"] == REFERENCE_SCHEMA
        and value["family"] == "c"
        and value["complete_plaintext_receipt_sha256"] == C_RECEIPT[1]
        and value["complete_plaintext_receipt_bytes"] == C_RECEIPT[2]
        and value["complete_first_party_source_owner_count"] == 3,
        "reject a missing or invented complete actual C V9 owner reference",
    )
    assert isinstance(value, dict)
    entry = pool["entries"].get(C_RECEIPT[1])
    base.need(
        type(entry) is dict
        and base.checked(value["complete_reference_sha256"], "whole C V9 proof")
        == base.digest(base.canonical(entry))
        and value["complete_reference_canonical_bytes"]
        == len(base.canonical(entry)),
        "reject fabricated complete C V9 receipt, source or worker evidence",
    )
    return copy.deepcopy(entry)


def make_changes(reference: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 92,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v93_new_directly_authenticated_owner_count": 4,
        "v93_new_directly_authenticated_c_source_owner_count": 3,
        "v93_new_directly_authenticated_c_plaintext_receipt_owner_count": 1,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v9_original_campaign_actual_worker_count": 13,
        "c_v9_original_campaign_distinct_worker_count": 13,
        "c_v9_original_campaign_attempted_suite_count": 13,
        "c_v9_original_campaign_clean_suite_count": 3,
        "c_v9_original_campaign_completed_suite_count": 7,
        "c_v9_original_campaign_mismatch_suite_count": 4,
        "c_v9_original_campaign_verified_passing_case_count": 13606,
        "c_v9_original_campaign_observed_mismatch_lower_bound": 492,
        "c_v9_original_campaign_candidate_execution_failure_count": 6,
        "c_v9_original_campaign_infrastructure_failure_count": 0,
        "c_v9_original_campaign_worker_timeout_count": 0,
        "c_v9_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v9_original_campaign_original_native_inode_restored": True,
        "c_v9_original_campaign_original_source_targets_modified": 0,
        "c_v9_original_campaign_candidate_status": "FAIL",
        "c_v9_original_campaign_candidate_qualified": False,
        "current_aggregate_semantic_mismatch_counts": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "timing_trials_run": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "final_holdout_opened": False,
        "winner_selected": False,
        LATEST_KEY: copy.deepcopy(reference),
    }


def make_svg() -> bytes:
    rows = (
        ("Python re", CASE_COUNT, "13 of 13 groups", "BASELINE", "#34d399"),
        (
            "Rust", 15749,
            "10 clean · 2 differ · 1 incomplete",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "C", 13606,
            "3 clean · 4 differ · 6 candidate errors",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "Zig", 4607,
            "7 clean · 5 differ · 1 incomplete",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "C++", None,
            "Earlier differences; complete current result not measured",
            "NOT COMPATIBLE", "#fb7185",
        ),
        (
            "Go", None,
            "Earlier differences; complete current result not measured",
            "NOT COMPATIBLE", "#fb7185",
        ),
        (
            "Fortran", None,
            "Two builds disagreed; compatibility not measured",
            "BUILD FAILED", "#fb7185",
        ),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="970" viewBox="0 0 1440 970" role="img" aria-labelledby="title description">',
        '<title id="title">Progress toward a faster, fully compatible Python re</title>',
        '<desc id="description">Six independent first-party regular-expression engines are compared with unchanged Python 3.14.6 on the same original 31,237 checks in thirteen groups. The separate 8,244 differential checks are not included. Rust verified 15,749 checks across ten clean groups, with at least 1,296 observed differences and one genuine infrastructure failure. The latest real C campaign started thirteen distinct workers. C verified 13,606 checks in three clean groups, observed exactly 16, 248, 224, and 4 differences across four further complete groups, and recorded six actual candidate execution failures. Seven C groups completed. C had no infrastructure failure or timeout, its complete mismatch count remains unknown, and the original native inode was restored. Zig verified 4,607 checks in seven clean groups, recorded at least 1,700 differences across five groups, and retained one incomplete guarded lifecycle test and all thirteen individually proven guarded candidate imports. Historical C results, all Rust and Zig history, C++, Go, and Fortran remain intact. No candidate is fully compatible. Speed, memory and confidence are not measured. The proposed 14,155,776-case final comparison is not frozen, generated, opened or run.</desc>',
        '<rect width="1440" height="970" rx="22" fill="#0b1220"/>',
        '<text x="44" y="60" fill="#f8fafc" font-size="31" font-family="system-ui,sans-serif" font-weight="730">Building a faster Python re, from scratch</text>',
        '<text x="44" y="97" fill="#cbd5e1" font-size="17" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<rect x="44" y="119" width="1352" height="57" rx="11" fill="#172338"/>',
        '<text x="62" y="144" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">What the bars mean: checks actually confirmed against Python, out of 31,237.</text>',
        '<text x="62" y="165" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Unfinished checks are unknown, not passes. The separate 8,244-check comparison is not included.</text>',
        '<text x="45" y="211" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">ENGINE</text>',
        '<text x="161" y="211" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">CONFIRMED ORIGINAL CHECKS</text>',
        '<text x="724" y="211" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">WHAT ACTUALLY HAPPENED</text>',
        '<text x="1386" y="211" text-anchor="end" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">RESULT</text>',
        '<line x1="44" y1="226" x2="1396" y2="226" stroke="#334155"/>',
    ]
    for index, (name, passed, details, result, colour) in enumerate(rows):
        y = 267 + 62 * index
        parts.append(
            f'<text x="48" y="{y}" fill="#f8fafc" font-size="16" '
            f'font-family="system-ui,sans-serif" font-weight="650">{name}</text>'
        )
        parts.append(
            f'<rect x="161" y="{y - 16}" width="365" height="20" '
            'rx="6" fill="#1e293b"/>'
        )
        if passed is None:
            label = "NOT MEASURED"
        else:
            width = max(3, round(365 * passed / CASE_COUNT))
            parts.append(
                f'<rect x="161" y="{y - 16}" width="{width}" height="20" '
                f'rx="6" fill="{colour}"/>'
            )
            label = f"{passed:,} / {CASE_COUNT:,}"
        parts.append(
            f'<text x="540" y="{y}" fill="#e2e8f0" font-size="13" '
            f'font-family="system-ui,sans-serif">{label}</text>'
        )
        parts.append(
            f'<text x="724" y="{y}" fill="#cbd5e1" font-size="12" '
            f'font-family="system-ui,sans-serif">{details}</text>'
        )
        parts.append(
            f'<text x="1386" y="{y}" text-anchor="end" fill="{colour}" '
            f'font-size="11" font-family="system-ui,sans-serif" '
            f'font-weight="700">{result}</text>'
        )
    parts.extend((
        '<line x1="44" y1="677" x2="1396" y2="677" stroke="#334155"/>',
        '<text x="48" y="709" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="670">Progress is not the same as full compatibility</text>',
        '<text x="48" y="738" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">C completed 7 of 13 groups: 3 clean, 4 with real differences, and 6 actual candidate errors.</text>',
        '<text x="48" y="761" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Observed differences: Rust at least 1,296; C at least 492; Zig at least 1,700. Complete totals: NOT MEASURED.</text>',
        '<text x="48" y="784" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Every earlier Rust, C, and Zig result is preserved. Standard Python remains the unchanged baseline.</text>',
        '<text x="48" y="807" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">A successfully published result is not proof that a replacement is compatible or faster.</text>',
        '<rect x="44" y="830" width="1352" height="91" rx="12" fill="#172338"/>',
        '<text x="62" y="858" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="670">Proposed final speed comparison: 14,155,776 cases</text>',
        '<text x="62" y="882" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Not frozen, not generated, not opened, and not run. Speed, memory, confidence, and rankings: NOT MEASURED.</text>',
        '<text x="62" y="905" fill="#cbd5e1" font-size="12" font-family="system-ui,sans-serif">The earlier 4,194,304-case proposal and every prior result remain preserved; no winner has been selected.</text>',
        '<text x="48" y="951" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 93 · complete previous evidence preserved · no external regex wrapper · no fully compatible replacement.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def validate_families(
    base: types.ModuleType,
    old: dict,
    families: object,
    pool: dict,
    reference: dict,
    facts: dict,
) -> None:
    base.need(
        type(families) is list and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain the unchanged Python baseline and six first-party engine families",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row["family"] == family,
            "reject a missing, invented or substituted engine family: " + family,
        )
        if family == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "retain every byte of the unchanged standard Python baseline",
            )
            continue
        base.need(
            row["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
            and row["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "reject fabricated compatibility, independence or speed: " + family,
        )
        restored = copy.deepcopy(row)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if family == "c":
            proof = resolve_reference(base, pool, row.get(LATEST_KEY))
            base.need(
                base.canonical(proof["validated_campaign_outcome"])
                == base.canonical(facts)
                and base.canonical(row["v93_latest_original_campaign"])
                == base.canonical(facts)
                and base.canonical(row[LATEST_KEY]) == base.canonical(reference)
                and base.canonical(row["v89_latest_original_campaign"])
                == base.canonical(original["v89_latest_original_campaign"])
                and row["v89_latest_original_campaign"]
                ["verified_passing_case_count"] == 13094,
                "retain both exact historical C V7 and actual latest C V9",
            )
            restored.pop(LATEST_KEY)
            restored.pop("v93_latest_original_campaign")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore the exact complete V92 first-party engine family: " + family,
        )


def build(
    previous: types.ModuleType,
    v91: types.ModuleType,
    v90: types.ModuleType,
    v89: types.ModuleType,
    v88: types.ModuleType,
    v87: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None
        and type(options.source_bytes) is int
        and 0 < options.source_bytes <= OWNER_LIMIT,
        "caller-pin the complete immutable V93 renderer source",
    )
    own, _ = base.read_owner(
        SELF, base.checked(options.source_sha256, "whole immutable V93 renderer"),
        options.source_bytes, private=True,
    )
    for role, item in V92.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the exact entire pushed V92 " + role,
        )
    for role, item in C_SOURCE.items():
        base.need(
            getattr(options, "c_" + role + "_sha256") == item[1],
            "caller-pin the complete exact first-party C V9 " + role,
        )
    base.need(
        options.c_receipt_sha256 == C_RECEIPT[1],
        "caller-pin the whole actually pushed C V9 public outcome receipt",
    )
    old = authenticate_previous(
        previous, v91, v90, v89, v88, v87, v86, v85, v84, v83, v82,
        chain, base,
    )
    contract, receipt, facts = load_c_evidence(base)
    pool = make_evidence_pool(base, contract, receipt, facts)
    reference = make_reference(base, pool)
    changes = make_changes(reference)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V92.items()
    }
    source_owners = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in C_SOURCE.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 93,
        "previous_complete_snapshot_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_overview_sha256": V92["summary"][1],
        "previous_complete_overview_bytes": V92["summary"][2],
        **copy.deepcopy(changes),
    })
    headline = copy.deepcopy(old["headline"])
    headline["verified_original_checks_by_candidate"]["c"] = 13606
    headline["latest_complete_candidate_mismatch_totals"] = "NOT MEASURED"
    headline["fully_compatible_candidate_count"] = 0
    headline["performance"] = "NOT MEASURED"
    headline["memory"] = "NOT MEASURED"
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 93,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": copy.deepcopy(predecessor),
        "c_v9_source_owners": copy.deepcopy(source_owners),
        "c_v9_plaintext_receipt_owner": base.pin(
            C_RECEIPT[0], C_RECEIPT[1], C_RECEIPT[2]
        ),
        "headline": copy.deepcopy(headline),
        "snapshot": copy.deepcopy(snapshot),
        "complete_original_suites": [
            {"suite": suite, "case_execution_denominator": count}
            for suite, count in SUITES
        ],
        **copy.deepcopy(changes),
    }
    families = copy.deepcopy(old["families"])
    for row in families:
        family = row["family"]
        if family == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = EVIDENCE_FLOOR
        row["authenticated_history_reference_lower_bound"] = HISTORY_FLOOR
        if family == "c":
            row[LATEST_KEY] = copy.deepcopy(reference)
            row["v93_latest_original_campaign"] = copy.deepcopy(facts)
    validate_families(base, old, families, pool, reference, facts)
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 93,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v92_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v92_snapshot_canonical_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_v92_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "lossless_v92_snapshot_identity_status": "PASS",
        "lossless_v92_family_identity_status": "PASS",
        "lossless_v92_all_fourteen_previous_pool_identity_status": "PASS",
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v93_c_v9_complete_plaintext_receipt_count": 1,
        "lossless_v93_c_v9_complete_source_owner_count": 3,
        "lossless_v93_c_v9_complete_original_suite_count": 13,
        "preserved_v92_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": {
            **copy.deepcopy(old["latest_original_campaigns"]),
            "c": copy.deepcopy(facts),
        },
        **copy.deepcopy(changes),
    })
    for key, size, digest, count in OLD_POOLS:
        whole = base.canonical(summary[key])
        base.need(
            len(whole) == size
            and base.digest(whole) == digest
            and base.canonical(summary[key]) == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "retain every byte of the complete historical V92 proof pool: " + key,
        )
    base.need(
        base.canonical(summary["previous_v92_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v91_snapshot"])
        == base.canonical(old["previous_v91_snapshot"])
        and base.canonical(summary["previous_v90_snapshot"])
        == base.canonical(old["previous_v90_snapshot"])
        and base.canonical(summary["previous_v89_snapshot"])
        == base.canonical(old["previous_v89_snapshot"])
        and base.canonical(summary["previous_v88_snapshot"])
        == base.canonical(old["previous_v88_snapshot"])
        and base.canonical(families[0]) == base.canonical(old["families"][0])
        and base.canonical(summary["latest_original_campaigns"]["rust"])
        == base.canonical(old["latest_original_campaigns"]["rust"])
        and base.canonical(summary["latest_original_campaigns"]["zig"])
        == base.canonical(old["latest_original_campaigns"]["zig"])
        and base.canonical(summary["preserved_v92_latest_original_campaigns"]["c"])
        == base.canonical(old["latest_original_campaigns"]["c"])
        and summary["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and summary["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and summary["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and summary["c_v9_original_campaign_verified_passing_case_count"] == 13606
        and summary["c_v9_original_campaign_observed_mismatch_lower_bound"] == 492
        and summary["c_v9_original_campaign_candidate_execution_failure_count"] == 6
        and summary["c_v9_original_campaign_infrastructure_failure_count"] == 0
        and summary["c_v9_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
        and summary["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and summary["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and summary["zig_v12_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v12_original_campaign_observed_mismatch_lower_bound"] == 1700
        and summary["zig_v12_original_campaign_individually_proven_guarded_candidate_import_count"]
        == 13
        and summary["historical_original_rust_verified_passing_case_count"] == 14853
        and summary["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
        and summary["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["undefined_behavior"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False,
        "preserve all C, Rust, guarded Zig, unchanged baseline and sealed holdout",
    )
    validate_evidence_pool(base, summary[POOL_KEY], contract, receipt, facts)
    recovered = resolve_reference(base, pool, reference)
    base.need(
        base.canonical(recovered["validated_campaign_outcome"])
        == base.canonical(facts)
        and base.canonical(summary[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(snapshot[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(inputs[LATEST_KEY]) == base.canonical(reference),
        "retain complete independently verifiable actual C V9 campaign evidence",
    )
    assets = {
        INPUT_PATH: inputs_raw,
        SUMMARY_PATH: base.canonical(summary),
        SVG_PATH: svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized complete V93 evidence before publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
    v91: types.ModuleType,
    v90: types.ModuleType,
    v89: types.ModuleType,
    v88: types.ModuleType,
    v87: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    prior = previous.self_test(
        v91, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
        previous_options(previous),
    )
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 92
        and type(prior["rejected_hostile_control_count"]) is int
        and prior["rejected_hostile_control_count"] >= 10777
        and prior["authenticated_evidence_owner_lower_bound"] == 324
        and prior["authenticated_history_reference_lower_bound"] == 329
        and prior["lossless_previous_v91_proof_pool_count"] == 13
        and prior["lossless_v91_all_thirteen_previous_pool_identity_status"] == "PASS"
        and prior["lossless_v89_complete_original_suite_reference_count"] == 39
        and prior["lossless_v90_zig_v10_complete_original_suite_count"] == 13
        and prior["lossless_v91_rust_v20_complete_original_suite_count"] == 13
        and prior["lossless_v92_zig_v12_complete_plaintext_receipt_count"] == 1
        and prior["lossless_v92_zig_v12_complete_source_owner_count"] == 3
        and prior["lossless_v92_zig_v12_complete_original_suite_count"] == 13
        and prior["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and prior["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and prior["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and prior["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and prior["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and prior["zig_v12_original_campaign_verified_passing_case_count"] == 4607
        and prior["zig_v12_original_campaign_observed_mismatch_lower_bound"] == 1700
        and prior["zig_v12_original_campaign_individually_proven_guarded_candidate_import_count"]
        == 13
        and prior["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and prior["qualified_candidate_count"] == 0
        and prior["performance"] == "NOT MEASURED"
        and prior["outputs_written"] is False,
        "retain every actual inherited V92 control without guessing its full count",
    )
    _, assets = build(
        previous, v91, v90, v89, v88, v87, v86, v85, v84, v83, v82,
        chain, base, options,
    )
    summary = base.document(assets[SUMMARY_PATH], "whole in-memory V93 summary")
    contract, receipt, facts = load_c_evidence(base)
    pool = summary[POOL_KEY]
    reference = summary[LATEST_KEY]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            assert callable(callback)
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V93 accepted fabricated source evidence: " + label)

    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        reject(
            "omitted complete C V9 source contract field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-source"),
        ("version", 8),
        ("family", "external-regex"),
        ("phase", "PHASE 3"),
        ("label", "fabricated-campaign"),
        ("status", "CANDIDATE PASS"),
        ("status_scope", "CANDIDATE QUALIFIED"),
        ("candidate_correctness", "PASS"),
        ("candidate_qualification", "PASS"),
        ("supplemental_candidate_correctness", "PASS"),
        ("qualified_candidate_count", 1),
        ("runtime_non_delegation", "PASS"),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = wrong
        reject(
            "fabricated actual C V9 source result:" + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for role in ("source", "protocol"):
        for field, wrong in (
            ("path", "fabricated.py"),
            ("sha256", "0" * 64),
            ("bytes", 1),
        ):
            forged = copy.deepcopy(contract)
            forged[role][field] = wrong
            reject(
                "substituted actual C V9 " + role + ":" + field,
                lambda value=forged: validate_source_contract(base, value),
            )
    for index, (suite, _) in enumerate(SUITES):
        forged = copy.deepcopy(contract)
        forged["frozen_original_producer"]["suites"][index]["suite"] = "invented"
        reject(
            "omitted frozen original C V9 obligation:" + suite,
            lambda value=forged: validate_source_contract(base, value),
        )
    for field, wrong in (
        ("original_case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("original_suite_count", 12),
        ("named_private_waiver_count", 12),
        ("separate_reference_case_count", 0),
        ("separate_reference_cases_counted_in_original_denominator", True),
    ):
        forged = copy.deepcopy(contract)
        forged["phase_one_v4"][field] = wrong
        reject(
            "fabricated frozen original C V9 denominator:" + field,
            lambda value=forged: validate_source_contract(base, value),
        )
    for field in (
        "another_candidate_engine", "cpython_sre_engine", "external_regex_engine",
        "fallback",
    ):
        forged = copy.deepcopy(contract)
        forged["first_party_match_semantics"][field] = "ALLOWED"
        reject(
            "forged third-party C V9 fallback:" + field,
            lambda value=forged: validate_source_contract(base, value),
        )
    for field in sorted(contract["source_only_effects"]):
        forged = copy.deepcopy(contract)
        forged["source_only_effects"][field] = 1
        reject(
            "forbidden actual C V9 source-mode side effect:" + field,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key in sorted(receipt):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        reject(
            "omitted complete actual C V9 receipt field " + key,
            lambda value=forged: validate_c_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-receipt"),
        ("version", 8),
        ("family", "external-regex"),
        ("label", "fabricated-campaign"),
        ("status", "FAIL"),
        ("publication_status", "FAIL"),
        ("publication_pass_means", "CANDIDATE QUALIFIED"),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("suite_count", 12),
        ("attempted_suite_count", 12),
        ("named_private_waiver_count", 12),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("actual_candidate_workers", 12),
        ("actual_worker_process_ids_are_distinct", False),
        ("actual_worker_process_ids", list(ACTUAL_WORKER_PIDS[:-1])),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", CASE_COUNT),
        ("observed_semantic_mismatch_lower_bound", 0),
        ("semantic_mismatch_count", 492),
        ("candidate_execution_failure_count", 0),
        ("infrastructure_failure_count", 1),
        ("worker_timeout_count", 1),
        ("worker_timeout_seconds", 0),
        ("original_native_inode_restored", False),
        ("original_source_targets_modified", 1),
        ("separate_reference_case_count", 0),
        ("separate_reference_cases_counted_as_candidate_cases", True),
        ("expanded_holdout_proposed_case_count", CASE_COUNT),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("clock_samples", 1),
        ("timing_trials_run", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
        ("uncompressed_bytes", 1),
        ("uncompressed_sha256", "0" * 64),
        ("actual_c21_build_receipt_sha256", "0" * 64),
        ("actual_c21_root_receipt_sha256", "0" * 64),
        ("corrected_source_sha256", "0" * 64),
        ("native_bridge_sha256", "0" * 64),
        ("native_engine_sha256", "0" * 64),
        ("unchanged_adapter_sha256", "0" * 64),
        ("preserved_actual_v6_failure_receipt_sha256", "0" * 64),
        ("preserved_actual_v7_failure_receipt_sha256", "0" * 64),
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = wrong
        reject(
            "fabricated actual C V9 campaign result:" + key,
            lambda value=forged: validate_c_receipt(base, value),
        )
    for field, wrong in (
        ("path", "fabricated.json.gz"),
        ("sha256", "0" * 64),
        ("bytes", 1),
        ("device", 1),
        ("inode", 1),
        ("mode", "0777"),
        ("nlink", 2),
        ("exclusive_creation", False),
        ("file_fsync_completed", False),
        ("directory_fsync_completed", False),
    ):
        forged = copy.deepcopy(receipt)
        forged["archive"][field] = wrong
        reject(
            "forged actual C V9 archive metadata:" + field,
            lambda value=forged: validate_c_receipt(base, value),
        )
    for index, (suite, _) in enumerate(SUITES):
        for field in sorted(ROW_KEYS):
            forged = copy.deepcopy(receipt)
            forged["suite_outcomes"][index].pop(field)
            reject(
                "omitted complete C V9 worker " + suite + ":" + field,
                lambda value=forged: validate_c_receipt(base, value),
            )
        for field, wrong in (
            ("suite", "invented-suite"),
            ("case_execution_denominator", CASE_COUNT),
            ("actual_candidate_workers", 0),
            ("worker_process_id", 0),
            ("status", "INVENTED"),
            ("failure_class", "INVENTED"),
            ("failure_phase", "INVENTED"),
            ("error_type", "INVENTED"),
            ("mismatch_count", "INVENTED"),
            ("plain_failure_diagnostic", "INVENTED"),
        ):
            forged = copy.deepcopy(receipt)
            forged["suite_outcomes"][index][field] = wrong
            reject(
                "forged actual C V9 worker " + suite + ":" + field,
                lambda value=forged: validate_c_receipt(base, value),
            )
    for suite in MISMATCHES:
        forged = copy.deepcopy(receipt)
        for row in forged["suite_outcomes"]:
            if row["suite"] == suite:
                row["mismatch_count"] = 0
        reject(
            "concealed actual C V9 semantic mismatch:" + suite,
            lambda value=forged: validate_c_receipt(base, value),
        )
    for suite in EXECUTION_FAILURES:
        forged = copy.deepcopy(receipt)
        for row in forged["suite_outcomes"]:
            if row["suite"] == suite:
                row["failure_class"] = "INFRASTRUCTURE FAILURE"
        reject(
            "relabeled genuine C candidate execution failure:" + suite,
            lambda value=forged: validate_c_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-reference"),
        ("family", "external-regex"),
        ("complete_plaintext_receipt_sha256", "0" * 64),
        ("complete_plaintext_receipt_bytes", 1),
        ("complete_first_party_source_owner_count", 2),
        ("complete_reference_sha256", "0" * 64),
        ("complete_reference_canonical_bytes", 1),
    ):
        forged = copy.deepcopy(reference)
        forged[key] = wrong
        reject(
            "fabricated complete actual C V9 reference:" + key,
            lambda value=forged: resolve_reference(base, pool, value),
        )
    for field in sorted(pool):
        forged = copy.deepcopy(pool)
        forged.pop(field)
        reject(
            "omitted complete actual C V9 evidence pool field:" + field,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    forged = copy.deepcopy(pool)
    forged["entries"].pop(C_RECEIPT[1])
    reject(
        "omitted complete actual C V9 evidence pool entry",
        lambda value=forged: validate_evidence_pool(
            base, value, contract, receipt, facts
        ),
    )
    entry = pool["entries"][C_RECEIPT[1]]
    for field in sorted(entry):
        forged = copy.deepcopy(pool)
        forged["entries"][C_RECEIPT[1]].pop(field)
        reject(
            "omitted complete actual C V9 evidence entry field:" + field,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    for index, (suite, _) in enumerate(SUITES):
        forged = copy.deepcopy(pool)
        forged["entries"][C_RECEIPT[1]]["complete_original_suite_rows"].pop(index)
        reject(
            "omitted complete genuine C V9 original worker proof:" + suite,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    old = authenticate_previous(
        previous, v91, v90, v89, v88, v87, v86, v85, v84, v83, v82,
        chain, base,
    )
    for index, row in enumerate(summary["families"]):
        if row["family"] == "python":
            forged = copy.deepcopy(summary["families"])
            forged[index]["correctness"] = "INVENTED"
            reject(
                "changed exact unchanged Python baseline",
                lambda value=forged: validate_families(
                    base, old, value, pool, reference, facts
                ),
            )
            continue
        for key, wrong in (
            ("qualified", True),
            ("runtime_no_delegation", "PASS"),
            ("performance", "1.5x"),
            ("authenticated_evidence_owner_lower_bound", EVIDENCE_FLOOR - 1),
            ("authenticated_history_reference_lower_bound", HISTORY_FLOOR + 1),
        ):
            forged = copy.deepcopy(summary["families"])
            forged[index][key] = wrong
            reject(
                "fabricated compatible or faster engine " + row["family"] + ":" + key,
                lambda value=forged: validate_families(
                    base, old, value, pool, reference, facts
                ),
            )
    for event, arguments in (
        ("open", (str(ROOT / "hidden.gz"), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / INPUT_PATH), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / SVG_PATH), "rb", os.O_RDONLY)),
        ("open", ("/tmp/rebar-private-root", "rb", os.O_RDONLY)),
        ("open", (str(ROOT / "safe.json"), "wb", os.O_WRONLY | os.O_CREAT)),
        ("subprocess.Popen", ("candidate",)),
        ("ctypes.dlopen", ("external-regex.so",)),
        ("socket.connect", ("example.invalid",)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("re", None, None, None, None)),
        ("import", ("_sre", None, None, None, None)),
        ("import", ("candidates.c_candidate", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
    ):
        reject(
            "forbidden source-only side effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    base.need(rejected >= 450, "require complete actual C V9 hostile controls")
    return result_payload(base, options, assets, False, {
        "schema": SCHEMA + "-source-only-self-test",
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ] + rejected,
    })


def result_payload(
    base: types.ModuleType,
    options: argparse.Namespace,
    assets: dict[str, bytes],
    outputs_written: bool,
    additional: dict | None = None,
) -> dict:
    result = {
        "schema": SCHEMA + (
            "-published" if outputs_written else "-source-only-frozen-context"
        ),
        "version": 93,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inputs_sha256": base.digest(assets[INPUT_PATH]),
        "inputs_bytes": len(assets[INPUT_PATH]),
        "summary_sha256": base.digest(assets[SUMMARY_PATH]),
        "summary_bytes": len(assets[SUMMARY_PATH]),
        "svg_sha256": base.digest(assets[SVG_PATH]),
        "svg_bytes": len(assets[SVG_PATH]),
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v93_new_directly_authenticated_owner_count": 4,
        "v93_new_directly_authenticated_c_source_owner_count": 3,
        "v93_new_directly_authenticated_c_plaintext_receipt_owner_count": 1,
        "lossless_previous_v92_proof_pool_count": len(OLD_POOLS),
        "lossless_v92_all_fourteen_previous_pool_identity_status": "PASS",
        "lossless_v92_snapshot_identity_status": "PASS",
        "lossless_v92_family_identity_status": "PASS",
        "lossless_v89_complete_original_suite_reference_count": 39,
        "lossless_v90_zig_v10_complete_original_suite_count": 13,
        "lossless_v91_rust_v20_complete_original_suite_count": 13,
        "lossless_v92_zig_v12_complete_original_suite_count": 13,
        "lossless_v93_c_v9_complete_plaintext_receipt_count": 1,
        "lossless_v93_c_v9_complete_source_owner_count": 3,
        "lossless_v93_c_v9_complete_original_suite_count": 13,
        "original_case_execution_denominator": CASE_COUNT,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v7_original_campaign_clean_suite_count": 2,
        "c_v7_original_campaign_completed_suite_count": 5,
        "c_v7_original_campaign_verified_passing_case_count": 13094,
        "c_v7_original_campaign_observed_mismatch_lower_bound": 236,
        "c_v7_original_campaign_candidate_execution_failure_count": 7,
        "c_v7_original_campaign_infrastructure_failure_count": 1,
        "c_v9_original_campaign_actual_worker_count": 13,
        "c_v9_original_campaign_distinct_worker_count": 13,
        "c_v9_original_campaign_clean_suite_count": 3,
        "c_v9_original_campaign_completed_suite_count": 7,
        "c_v9_original_campaign_mismatch_suite_count": 4,
        "c_v9_original_campaign_verified_passing_case_count": 13606,
        "c_v9_original_campaign_observed_mismatch_lower_bound": 492,
        "c_v9_original_campaign_candidate_execution_failure_count": 6,
        "c_v9_original_campaign_infrastructure_failure_count": 0,
        "c_v9_original_campaign_worker_timeout_count": 0,
        "c_v9_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v9_original_campaign_original_native_inode_restored": True,
        "c_v9_original_campaign_original_source_targets_modified": 0,
        "rust_v19_original_campaign_clean_suite_count": 6,
        "rust_v19_original_campaign_completed_suite_count": 8,
        "rust_v19_original_campaign_verified_passing_case_count": 12942,
        "rust_v19_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v19_original_campaign_infrastructure_failure_count": 5,
        "rust_v20_original_campaign_actual_worker_count": 13,
        "rust_v20_original_campaign_clean_suite_count": 10,
        "rust_v20_original_campaign_completed_suite_count": 12,
        "rust_v20_original_campaign_mismatch_suite_count": 2,
        "rust_v20_original_campaign_verified_passing_case_count": 15749,
        "rust_v20_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v20_original_campaign_infrastructure_failure_count": 1,
        "rust_v20_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v20_original_campaign_all_four_original_targets_restored": True,
        "zig_v9_original_campaign_verified_passing_case_count": 927,
        "zig_v10_original_campaign_clean_suite_count": 6,
        "zig_v10_original_campaign_completed_suite_count": 9,
        "zig_v10_original_campaign_verified_passing_case_count": 3583,
        "zig_v10_original_campaign_observed_mismatch_lower_bound": 1540,
        "zig_v10_original_campaign_infrastructure_failure_count": 4,
        "zig_v12_original_campaign_actual_worker_count": 13,
        "zig_v12_original_campaign_distinct_worker_count": 13,
        "zig_v12_original_campaign_individually_proven_guarded_candidate_import_count": 13,
        "zig_v12_original_campaign_candidate_import_status_unknown_count": 0,
        "zig_v12_original_campaign_clean_suite_count": 7,
        "zig_v12_original_campaign_completed_suite_count": 12,
        "zig_v12_original_campaign_mismatch_suite_count": 5,
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
        "zig_v12_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v12_original_campaign_infrastructure_failure_count": 1,
        "zig_v12_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v12_original_campaign_all_three_original_targets_restored": True,
        "historical_original_rust_semantic_mismatch_count": 1440,
        "historical_original_rust_verified_passing_case_count": 14853,
        "historical_original_c_semantic_mismatch_count": 1230,
        "historical_original_c_verified_passing_case_count": 7325,
        "historical_original_zig_semantic_mismatch_count": 1764,
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "compressed_archives_opened_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
        "outputs_written": outputs_written,
    }
    if additional:
        result.update(additional)
    return result


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {INPUT_PATH, SUMMARY_PATH, SVG_PATH}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only one bounded, exclusively created new V93 graph owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "publish complete V93 bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate the whole exclusively published V93 evidence owner",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "reauthenticate every complete final V93 evidence byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V92:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in C_SOURCE:
        parser.add_argument("--c-" + role + "-sha256", required=True)
    parser.add_argument("--c-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, v91, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base = (
            load_previous()
        )
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(
                previous, v91, v90, v89, v88, v87, v86, v85, v84, v83, v82,
                chain, base, options,
            )
        else:
            _, assets = build(
                previous, v91, v90, v89, v88, v87, v86, v85, v84, v83, v82,
                chain, base, options,
            )
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V93 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
