#!/usr/bin/env python3
"""Render the measured progress of six independent Python re replacements."""

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
SELF = "tools/render_candidate_current_overview_v91.py"
OUTPUT = "docs/evidence/candidate-current-overview-v91"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v91"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 320
HISTORY_FLOOR = 325

V90 = {
    "source": (
        "tools/render_candidate_current_overview_v90.py",
        "be8322ca4ebc0f76a71ecf0c13e37bb2c367a065acf5d69c1b3c4d34b18f0aa8",
        79370,
        428929,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v90.inputs.json",
        "77f1f751682c245e5f62a3f0ff292718bad570e1fe3cdc5df597b4c5f1ce874a",
        11911,
        429058,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v90.summary.json",
        "4c602a4879b1f65fb1482e8504ec2dfc32fa5448ff3a9ee19110854929022fa7",
        3155233,
        429059,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v90.svg",
        "4a81e160eef4ea731f4e723e4c8c90272249ee730babcfb4519edec612963807",
        8999,
        429060,
    ),
}

RUST_SOURCE = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v20.py",
        "d8434087da84e6d537f04023a95750297dc558a109c606e5863a2e7ac4177b13",
        66438,
        431433,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V20.md",
        "19c3d742887784ab7054c1a63031077a9742c041d6f98c4e91452db1a51f505d",
        6017,
        525356,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v20.json",
        "9c973d53a62f3948537cf7471f5fdde7403490053c2b304b6b192d784abeb414",
        29199,
        525357,
    ),
}

RUST_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v16-rust-phase2-v21-rust-"
    "captured-findall-root-provenance-original-p0-v20-failures-"
    "publication-receipt.json",
    "ad9e04aa3595a4e44a5bbc12b6413fde08b926c9e73b23aa6b3eedacd35e4a36",
    45973,
    524829,
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
)

POOL_KEY = "lossless_v91_rust_v20_original_campaign_evidence_pool"
POOL_SCHEMA = SCHEMA + "-lossless-complete-rust-original-campaign-pool-v1"
ENTRY_SCHEMA = SCHEMA + "-lossless-complete-rust-original-campaign-entry-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-rust-original-campaign-reference-v1"
LATEST_KEY = "rust_v20_actual_original_campaign"


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject unbounded complete V91 evidence: " + label)
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
            raise ValueError("reject substituted complete V91 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V91 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V91 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject changed complete V91 owner: " + label)
        return raw
    finally:
        os.close(handle)


FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
    "os.fork", "os.forkpty", "ctypes.dlopen", "ctypes.dlsym",
    "socket.__new__", "socket.connect", "socket.bind", "socket.sendto",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex", "ctypes", "subprocess", "multiprocessing", "socket", "time",
    "gzip", "bz2", "lzma", "tarfile", "zipfile",
})


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V91 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V91 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V91 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V91 rejected an unverified descriptor or file owner")
    if mode not in (None, "r", "rb"):
        raise ValueError("V91 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V91 source-only operation cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V91 rejected private roots or unopened holdout cases")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V91 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v91." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V91 rejected outputs, archives, benchmarks, or native code")


def load_previous() -> tuple[
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    tuple,
    types.ModuleType,
]:
    raw = read_fixed(V90["source"], "whole actually published V90 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v90")
    previous.__file__ = str(ROOT / V90["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v89, v88, v87, v86, v85, v84, v83, v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v90"
        and previous.SELF == V90["source"][0]
        and tuple(previous.SUITES) == SUITES
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 15,
        "require pinned isolated CPython, immutable V90 history, and exact P0",
    )
    return previous, v89, v88, v87, v86, v85, v84, v83, v82, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V90["source"][1],
        "source_bytes": V90["source"][2],
        "zig_receipt_sha256": previous.ZIG_RECEIPT[1],
    }
    for role, item in previous.V89.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.ZIG_SOURCE.items():
        pins["zig_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def authenticate_previous(
    previous: types.ModuleType,
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
        v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
        previous_options(previous),
    )
    for role in ("inputs", "summary", "svg"):
        item = V90[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole pushed V90 " + role),
            "reconstruct every complete byte of the published V90 " + role,
        )
    old = base.document(assets[V90["summary"][0]], "whole immutable V90 summary")
    historical = old["previous_v88_snapshot"]
    base.need(
        old["version"] == 90
        and old["snapshot"] == snapshot
        and old["authenticated_evidence_owner_lower_bound"] == 316
        and old["authenticated_history_reference_lower_bound"] == 321
        and [row.get("family") for row in old["families"]]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and old["families"][0]["correctness"] == "BASELINE PASS"
        and old["lossless_v89_all_eleven_previous_pool_identity_status"] == "PASS"
        and old["lossless_v89_original_campaign_receipt_reference_pool_entry_count"]
        == 3
        and old["lossless_v89_complete_original_suite_reference_count"] == 39
        and old["lossless_v90_zig_v10_complete_plaintext_receipt_count"] == 1
        and old["lossless_v90_zig_v10_complete_source_owner_count"] == 3
        and old["lossless_v90_zig_v10_complete_original_suite_count"] == 13
        and old["original_case_execution_denominator"] == CASE_COUNT
        and old["separate_additional_reference_case_count"]
        == SUPPLEMENTAL_CASE_COUNT
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
        and old["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and old["zig_v9_original_campaign_infrastructure_failure_count"] == 10
        and old["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and old["zig_v10_original_campaign_completed_suite_count"] == 9
        and old["zig_v10_original_campaign_mismatch_suite_count"] == 3
        and old["zig_v10_original_campaign_observed_mismatch_lower_bound"] == 1540
        and old["zig_v10_original_campaign_infrastructure_failure_count"] == 4
        and old["zig_v10_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
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
        "preserve every exact C, Rust V19, Zig V9 and V10 outcome and unopened P0",
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
            "preserve complete exact historical V90 proof pool: " + key,
        )
    return old


def validate_source_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and len(value) == 320,
        "authenticate every field of the complete Rust V20 source contract",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v20-recoverable-source-freeze"
        and value["version"] == 20
        and value["status"] == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and value["source_sha256"] == RUST_SOURCE["source"][1]
        and value["protocol_sha256"] == RUST_SOURCE["protocol"][1]
        and value["case_execution_denominator"] == CASE_COUNT
        and value["suite_count"] == 13
        and value["private_waiver_count"] == 13
        and value["qualified_candidate_count"] == 0
        and value["candidate_qualified"] is False
        and value["candidate_correctness"] == "NOT MEASURED"
        and value["candidate_matching"] == "NOT RUN"
        and value["phase2_candidate_qualification"] == "BLOCKED"
        and value["runtime_non_delegation"] == "NOT ESTABLISHED"
        and value["external_regex_packages_allowed"] is False
        and value["stdlib_regex_engine_allowed"] is False
        and value["matching_fallback_allowed"] is False
        and value["supplemental_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and value["supplemental_cases_counted_in_original_denominator"] is False
        and value["supplemental_candidate_case_count"] == 0
        and value["supplemental_candidate_status"] == "NOT RUN"
        and value["expanded_holdout_proposal_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and value["expanded_holdout_cases_generated"] == 0
        and value["expanded_holdout_cases_opened"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["corrected_rust_source_owner_count"] == 9
        and type(value["corrected_rust_source_owners"]) is list
        and len(value["corrected_rust_source_owners"]) == 9
        and value["actual_v19_actual_candidate_workers"] == 13
        and value["actual_v19_completed_suite_count"] == 8
        and value["actual_v19_verified_passing_case_count"] == 12942
        and value["actual_v19_fully_observed_semantic_mismatch_lower_bound"] == 1296
        and value["actual_v19_infrastructure_failure_count"] == 5
        and value["actual_v19_failure_receipt_sha256"]
        == "e48a4115a85d827cbf16a32b6b44390d2bf4b092e1823989c9bcafe874fa04fe"
        and value["actual_v19_total_semantic_mismatch_count"] == "NOT MEASURED"
        and value["actual_v20_candidate_semantic_mismatch_count"] == "NOT MEASURED"
        and value["actual_v20_original_campaign_attempted"] is False
        and value["actual_candidate_imports"] == 0
        and value["actual_candidate_workers_started"] == 0
        and value["actual_reference_workers_started"] == 0
        and value["actual_clock_samples"] == 0
        and value["actual_compiler_processes_started"] == 0
        and value["actual_native_libraries_loaded"] == 0
        and value["actual_hidden_cases_read"] == 0
        and value["actual_build_archive_opens"] == 0
        and value["actual_build_archive_inflations"] == 0
        and value["actual_private_build_root_opens"] == 0
        and value["timing_trials_run"] == 0
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject invented source-only matching, fallback, hidden cases or timing",
    )
    rows = value["suites"]
    base.need(
        type(rows) is list and len(rows) == len(SUITES),
        "preserve every frozen Rust V20 original-suite source obligation",
    )
    for row, (suite, count) in zip(rows, SUITES, strict=True):
        base.need(
            type(row) is dict
            and row["id"] == suite
            and row["case_execution_count"] == count,
            "reject a missing or changed Rust V20 source suite: " + suite,
        )
    return value


def validate_rust_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and len(value) == 96,
        "authenticate every field of the actual complete Rust V20 receipt",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v20-durable-publication-receipt"
        and value["status"] == "PASS"
        and value["publication_status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and value["family"] == "rust"
        and value["label"]
        == "phase2-v21-rust-captured-findall-root-provenance-original-p0-v20"
        and value["campaign_source_sha256"] == RUST_SOURCE["source"][1]
        and value["campaign_protocol_sha256"] == RUST_SOURCE["protocol"][1]
        and value["campaign_contract_sha256"] == RUST_SOURCE["contract"][1]
        and value["actual_candidate_workers"] == 13
        and type(value["actual_worker_process_ids"]) is list
        and len(value["actual_worker_process_ids"]) == 13
        and value["distinct_worker_process_id_count"] == 13
        and value["duplicate_worker_process_id_count"] == 0
        and value["missing_worker_process_id_count"] == 0
        and value["attempted_suite_count"] == 13
        and value["started_suite_count"] == 13
        and value["suite_count"] == 13
        and value["completed_suite_count"] == 12
        and value["verified_passing_case_count"] == 15749
        and value["infrastructure_failure_count"] == 1
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["case_execution_denominator"] == CASE_COUNT
        and value["named_private_waiver_count"] == 13
        and value["all_original_observation_vectors_complete"] is False
        and value["all_original_suite_rows_validated_before_publication"] is True
        and value["all_four_original_targets_restored"] is True
        and value["restoration_verified_before_publication"] is True
        and value["actual_v21_compiler_process_count"] == 28
        and value["actual_v21_build_receipt_sha256"]
        == "bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102"
        and value["combined_bridge_source_sha256"]
        == "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
        and value["combined_bridge_source_bytes"] == 179520
        and value["preserved_previous_rust_semantic_mismatch_count"] == 1440
        and value["preserved_previous_rust_verified_passing_case_count"] == 14853
        and value["worker_failure_capture_count"] == 1
        and value["worker_failure_capture_complete"] is True
        and value["all_worker_failure_capture_count"] == 1
        and value["hidden_cases_read"] == 0
        and value["clock_samples"] == 0
        and value["timing_trials_run"] == 0
        and value["benchmark_files_read"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject invented Rust qualification, complete outcomes, speed or restoration",
    )
    rows = value["suite_integrity"]
    base.need(
        type(rows) is list and len(rows) == len(SUITES),
        "authenticate every real Rust V20 original-suite outcome",
    )
    assert isinstance(rows, list)
    for row, (suite, count) in zip(rows, SUITES, strict=True):
        base.need(
            type(row) is dict
            and row["suite"] == suite
            and row["case_execution_denominator"] == count
            and row["worker_attempted"] is True
            and row["actual_worker_started"] is True,
            "reject a missing or fabricated actual Rust V20 worker: " + suite,
        )
    clean = [row for row in rows if row["failure_class"] == "PASS"]
    mismatch = [
        row for row in rows if row["failure_class"] == "SEMANTIC MISMATCH"
    ]
    infrastructure = [
        row for row in rows if row["failure_class"] == "INFRASTRUCTURE FAILURE"
    ]
    base.need(
        len(clean) == 10
        and len(mismatch) == 2
        and len(infrastructure) == 1
        and len(clean) + len(mismatch) == value["completed_suite_count"]
        and len(clean) + len(mismatch) + len(infrastructure) == len(rows)
        and all(row["fully_observed"] is True for row in clean + mismatch)
        and all(row["fully_observed"] is False for row in infrastructure)
        and all(row["mismatch_count"] == 0 for row in clean)
        and sum(row["verified_passing_case_count"] for row in clean) == 15749
        and sum(row["case_execution_denominator"] for row in clean) == 15749
        and {
            row["suite"]: row["mismatch_count"] for row in mismatch
        } == {"substitution_v2": 240, "shape_v2": 1056}
        and sum(row["mismatch_count"] for row in mismatch) == 1296
        and infrastructure[0]["suite"] == "subinterpreter_v2"
        and infrastructure[0]["mismatch_count"] == "NOT MEASURED"
        and all(row["returncode"] == 0 for row in clean)
        and all(row["returncode"] == 1 for row in mismatch)
        and infrastructure[0]["returncode"] == 2,
        "derive actual ten clean, two differing and one incomplete Rust groups",
    )
    captures = value["all_worker_failure_captures"]
    base.need(
        type(captures) is list and len(captures) == 1,
        "preserve the complete actual nested-lifecycle Rust infrastructure failure",
    )
    restored = value["restored_original_targets"]
    base.need(
        type(restored) is dict
        and set(restored) == {"adapter", "bridge", "bridge_source", "engine"}
        and all(
            type(owner) is dict
            and owner["device"] == 2064
            and owner["uid"] == os.geteuid()
            and owner["nlink"] == 1
            for owner in restored.values()
        ),
        "preserve all four actual restored first-party native targets as metadata",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and archive["sha256"]
        == "22b2d20ef194299fe15a5a4d5962828cc3967242d9a15a3a006cbc03a860d7e6"
        and archive["size_bytes"] == 3674347
        and archive["device"] == 2064
        and archive["inode"] == 524824
        and archive["relative"].endswith(".json.gz"),
        "preserve Rust archive metadata exclusively from its whole public receipt",
    )
    return {
        "family": "rust",
        "display_name": "Rust",
        "actual_candidate_worker_count": 13,
        "unique_candidate_worker_count": 13,
        "attempted_suite_count": 13,
        "clean_suite_count": 10,
        "completed_suite_count": 12,
        "mismatch_suite_count": 2,
        "infrastructure_failure_count": 1,
        "infrastructure_failure_suite": "subinterpreter_v2",
        "verified_passing_case_count": 15749,
        "observed_semantic_mismatch_lower_bound": 1296,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "all_original_suite_rows_validated": True,
        "all_original_observation_vectors_complete": False,
        "all_four_original_targets_restored": True,
        "worker_failure_capture_count": 1,
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": RUST_SOURCE["source"][1],
        "protocol_sha256": RUST_SOURCE["protocol"][1],
        "contract_sha256": RUST_SOURCE["contract"][1],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["size_bytes"],
        "archive_opened_by_graph": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def load_rust_evidence(base: types.ModuleType) -> tuple[dict, dict, dict]:
    raws = {
        role: read_fixed(item, "whole first-party Rust V20 " + role)
        for role, item in RUST_SOURCE.items()
    }
    contract = base.document(raws["contract"], "whole actual Rust V20 source contract")
    base.need(
        base.canonical(contract) == raws["contract"],
        "reject noncanonical or partial Rust V20 source-freeze contract",
    )
    validate_source_contract(base, contract)
    raw = read_fixed(RUST_RECEIPT, "whole actual pushed Rust V20 public receipt")
    receipt = base.document(raw, "whole actual pushed Rust V20 public receipt")
    base.need(
        base.canonical(receipt) == raw,
        "reject noncanonical or partial actual Rust V20 public receipt",
    )
    return contract, receipt, validate_rust_receipt(base, receipt)


def compact_suite_proof(base: types.ModuleType, row: dict) -> dict:
    raw = base.canonical(row)
    return {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_public_suite_row_sha256": base.digest(raw),
        "complete_public_suite_row_canonical_bytes": len(raw),
        "failure_class": row["failure_class"],
        "fully_observed": row["fully_observed"],
        "observed_semantic_mismatch_count": row["mismatch_count"],
        "verified_passing_case_count": row["verified_passing_case_count"],
        "actual_worker_started": row["actual_worker_started"],
        "worker_attempted": row["worker_attempted"],
        "returncode": row["returncode"],
    }


def make_evidence_pool(
    base: types.ModuleType, contract: dict, receipt: dict, facts: dict,
) -> dict:
    entry = {
        "schema": ENTRY_SCHEMA,
        "family": "rust",
        "complete_plaintext_receipt_owner": base.synthetic_owner(
            RUST_RECEIPT[:3], RUST_RECEIPT[3]
        ),
        "complete_plaintext_receipt_sha256": RUST_RECEIPT[1],
        "complete_plaintext_receipt_bytes": RUST_RECEIPT[2],
        "complete_plaintext_receipt_field_count": 96,
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt": copy.deepcopy(receipt),
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in RUST_SOURCE.items()
        },
        "complete_source_contract_field_count": 320,
        "complete_source_contract_embedded": True,
        "complete_source_contract": copy.deepcopy(contract),
        "complete_original_suite_count": 13,
        "complete_original_suite_rows": [
            compact_suite_proof(base, row) for row in receipt["suite_integrity"]
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
        "entries": {RUST_RECEIPT[1]: entry},
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
            "schema", "version", "hash_algorithm",
            "complete_public_receipt_count", "complete_first_party_source_owner_count",
            "entries",
        }
        and pool["schema"] == POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and pool["complete_public_receipt_count"] == 1
        and pool["complete_first_party_source_owner_count"] == 3
        and type(pool["entries"]) is dict
        and set(pool["entries"]) == {RUST_RECEIPT[1]},
        "require one complete actual Rust V20 owner-addressed outcome",
    )
    assert isinstance(pool, dict)
    entry = pool["entries"][RUST_RECEIPT[1]]
    rows = [
        compact_suite_proof(base, row) for row in receipt["suite_integrity"]
    ]
    base.need(
        type(entry) is dict
        and entry["schema"] == ENTRY_SCHEMA
        and entry["family"] == "rust"
        and base.canonical(entry["complete_plaintext_receipt_owner"])
        == base.canonical(base.synthetic_owner(RUST_RECEIPT[:3], RUST_RECEIPT[3]))
        and entry["complete_plaintext_receipt_sha256"] == RUST_RECEIPT[1]
        and entry["complete_plaintext_receipt_bytes"] == RUST_RECEIPT[2]
        and entry["complete_plaintext_receipt_field_count"] == 96
        and entry["complete_plaintext_receipt_embedded"] is True
        and base.canonical(entry["complete_plaintext_receipt"])
        == base.canonical(receipt)
        and entry["complete_first_party_source_owner_count"] == 3
        and entry["complete_source_contract_field_count"] == 320
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
        "reject omitted, fabricated or partial actual Rust V20 evidence",
    )
    owners = entry["complete_first_party_source_owners"]
    base.need(
        type(owners) is dict and set(owners) == set(RUST_SOURCE),
        "preserve exactly three distinct authenticated Rust V20 source owners",
    )
    for role, item in RUST_SOURCE.items():
        base.need(
            base.canonical(owners[role])
            == base.canonical(base.synthetic_owner(item[:3], item[3])),
            "retain exact complete authenticated Rust V20 source owner: " + role,
        )


def make_reference(base: types.ModuleType, pool: dict) -> dict:
    entry = pool["entries"][RUST_RECEIPT[1]]
    raw = base.canonical(entry)
    return {
        "schema": REFERENCE_SCHEMA,
        "family": "rust",
        "complete_plaintext_receipt_sha256": RUST_RECEIPT[1],
        "complete_plaintext_receipt_bytes": RUST_RECEIPT[2],
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
        and value["family"] == "rust"
        and value["complete_plaintext_receipt_sha256"] == RUST_RECEIPT[1]
        and value["complete_plaintext_receipt_bytes"] == RUST_RECEIPT[2]
        and value["complete_first_party_source_owner_count"] == 3,
        "reject missing or false complete actual Rust V20 owner reference",
    )
    assert isinstance(value, dict)
    entry = pool["entries"].get(RUST_RECEIPT[1])
    base.need(
        type(entry) is dict
        and base.checked(value["complete_reference_sha256"], "whole Rust V20 proof")
        == base.digest(base.canonical(entry))
        and value["complete_reference_canonical_bytes"]
        == len(base.canonical(entry)),
        "reject fabricated complete Rust V20 receipt, source, or suite evidence",
    )
    return copy.deepcopy(entry)


def make_changes(reference: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 90,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v91_new_directly_authenticated_owner_count": 4,
        "v91_new_directly_authenticated_rust_source_owner_count": 3,
        "v91_new_directly_authenticated_rust_plaintext_receipt_owner_count": 1,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "rust_v20_original_campaign_actual_worker_count": 13,
        "rust_v20_original_campaign_distinct_worker_count": 13,
        "rust_v20_original_campaign_attempted_suite_count": 13,
        "rust_v20_original_campaign_clean_suite_count": 10,
        "rust_v20_original_campaign_completed_suite_count": 12,
        "rust_v20_original_campaign_mismatch_suite_count": 2,
        "rust_v20_original_campaign_verified_passing_case_count": 15749,
        "rust_v20_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v20_original_campaign_infrastructure_failure_count": 1,
        "rust_v20_original_campaign_infrastructure_failure_suite":
        "subinterpreter_v2",
        "rust_v20_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v20_original_campaign_all_four_original_targets_restored": True,
        "rust_v20_original_campaign_candidate_status": "FAIL",
        "rust_v20_original_campaign_candidate_qualified": False,
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
            "10 clean · 2 differ · 1 infrastructure failure",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "C", 13094,
            "2 clean · 3 differ · 7 errors · 1 infrastructure failure",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "Zig", 3583,
            "6 clean · 3 differ · 4 infrastructure failures",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "C++", None,
            "Historical differences; current complete result not measured",
            "NOT COMPATIBLE", "#fb7185",
        ),
        (
            "Go", None,
            "Historical differences; current complete result not measured",
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
        '<desc id="description">Six independent first-party regular-expression engines are compared with unchanged Python 3.14.6 on the same original 31,237 checks in thirteen groups. The separate 8,244 differential checks are not counted in that denominator. The actual latest Rust campaign started thirteen distinct workers, verified 15,749 checks across ten clean groups, observed 240 and 1,056 differences in two further groups, and recorded one genuine nested-lifecycle infrastructure failure. Twelve Rust groups completed, the full mismatch count remains unknown, all four original native targets were restored, and the candidate failed. C verified 13,094 checks in two clean groups, with three differing groups containing at least 236 differences, seven candidate errors, and one infrastructure failure. Zig verified 3,583 checks in six clean groups, with three differing groups containing at least 1,540 differences and four infrastructure failures. Historical Rust V19, historical Rust 14,853 passes, both prior Zig campaigns, C++, Go, and Fortran remain intact. No candidate is fully compatible, no speed or memory was measured, and the proposed 14,155,776-case holdout remains unfrozen, ungenerated, unopened, and unrun.</desc>',
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
        '<text x="48" y="738" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Rust completed 12 of 13 groups: 10 clean, 2 with real differences, and 1 incomplete lifecycle test.</text>',
        '<text x="48" y="761" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Observed differences: Rust at least 1,296; C at least 236; Zig at least 1,540. Complete totals: NOT MEASURED.</text>',
        '<text x="48" y="784" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Every earlier Rust, C, and Zig result is preserved. The standard Python engine remains the unchanged baseline.</text>',
        '<text x="48" y="807" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">A successful build or published report is not proof that an engine is compatible or faster.</text>',
        '<rect x="44" y="830" width="1352" height="91" rx="12" fill="#172338"/>',
        '<text x="62" y="858" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="670">Proposed final speed comparison: 14,155,776 cases</text>',
        '<text x="62" y="882" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Not frozen, not generated, not opened, and not run. Speed, memory, confidence, and rankings: NOT MEASURED.</text>',
        '<text x="62" y="905" fill="#cbd5e1" font-size="12" font-family="system-ui,sans-serif">The earlier 4,194,304-case proposal and every prior result remain preserved; no winner has been selected.</text>',
        '<text x="48" y="951" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 91 · complete previous evidence preserved · no external regex wrapper · no fully compatible replacement.</text>',
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
        "retain the unchanged baseline and exactly six independent engine families",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row["family"] == family,
            "reject a missing, invented, or substituted engine family: " + family,
        )
        if family == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "retain every byte of the immutable standard Python baseline",
            )
            continue
        base.need(
            row["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
            and row["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "reject fabricated compatibility, independence, or speed: " + family,
        )
        restored = copy.deepcopy(row)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if family == "rust":
            proof = resolve_reference(base, pool, row.get(LATEST_KEY))
            base.need(
                base.canonical(proof["validated_campaign_outcome"])
                == base.canonical(facts)
                and base.canonical(row["v91_latest_original_campaign"])
                == base.canonical(facts)
                and base.canonical(row[LATEST_KEY]) == base.canonical(reference)
                and base.canonical(row["v89_latest_original_campaign"])
                == base.canonical(original["v89_latest_original_campaign"])
                and row["v89_latest_original_campaign"]
                ["verified_passing_case_count"] == 12942,
                "retain both whole historical Rust V19 and actual latest Rust V20",
            )
            restored.pop(LATEST_KEY)
            restored.pop("v91_latest_original_campaign")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore the exact full V90 first-party engine family: " + family,
        )


def build(
    previous: types.ModuleType,
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
        "caller-pin the whole immutable V91 renderer source",
    )
    own, _ = base.read_owner(
        SELF, base.checked(options.source_sha256, "whole immutable V91 renderer"),
        options.source_bytes, private=True,
    )
    for role, item in V90.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the exact entire published V90 " + role,
        )
    for role, item in RUST_SOURCE.items():
        base.need(
            getattr(options, "rust_" + role + "_sha256") == item[1],
            "caller-pin the complete exact first-party Rust V20 " + role,
        )
    base.need(
        options.rust_receipt_sha256 == RUST_RECEIPT[1],
        "caller-pin the whole actually pushed Rust V20 public outcome receipt",
    )
    old = authenticate_previous(
        previous, v89, v88, v87, v86, v85, v84, v83, v82, chain, base
    )
    contract, receipt, facts = load_rust_evidence(base)
    pool = make_evidence_pool(base, contract, receipt, facts)
    reference = make_reference(base, pool)
    changes = make_changes(reference)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V90.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 91,
        "previous_complete_snapshot_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_overview_sha256": V90["summary"][1],
        "previous_complete_overview_bytes": V90["summary"][2],
        **copy.deepcopy(changes),
    })
    headline = copy.deepcopy(old["headline"])
    headline["verified_original_checks_by_candidate"]["rust"] = 15749
    headline["latest_complete_candidate_mismatch_totals"] = "NOT MEASURED"
    headline["fully_compatible_candidate_count"] = 0
    headline["performance"] = "NOT MEASURED"
    headline["memory"] = "NOT MEASURED"
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 91,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": copy.deepcopy(predecessor),
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
        if family == "rust":
            row[LATEST_KEY] = copy.deepcopy(reference)
            row["v91_latest_original_campaign"] = copy.deepcopy(facts)
    validate_families(base, old, families, pool, reference, facts)
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 91,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v90_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v90_snapshot_canonical_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_v90_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "lossless_v90_snapshot_identity_status": "PASS",
        "lossless_v90_family_identity_status": "PASS",
        "lossless_v90_all_twelve_previous_pool_identity_status": "PASS",
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v91_rust_v20_complete_plaintext_receipt_count": 1,
        "lossless_v91_rust_v20_complete_source_owner_count": 3,
        "lossless_v91_rust_v20_complete_original_suite_count": 13,
        "preserved_v90_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": {
            **copy.deepcopy(old["latest_original_campaigns"]),
            "rust": copy.deepcopy(facts),
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
            "retain every byte of the complete historical V90 proof pool: " + key,
        )
    base.need(
        base.canonical(summary["previous_v90_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v89_snapshot"])
        == base.canonical(old["previous_v89_snapshot"])
        and base.canonical(summary["previous_v88_snapshot"])
        == base.canonical(old["previous_v88_snapshot"])
        and base.canonical(families[0]) == base.canonical(old["families"][0])
        and summary["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and summary["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and summary["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and summary["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and summary["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and summary["historical_original_rust_verified_passing_case_count"] == 14853
        and summary["rust_v20_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
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
        "preserve all Rust histories, C and Zig, Python baseline, and sealed holdout",
    )
    validate_evidence_pool(base, summary[POOL_KEY], contract, receipt, facts)
    recovered = resolve_reference(base, pool, reference)
    base.need(
        base.canonical(recovered["validated_campaign_outcome"])
        == base.canonical(facts)
        and base.canonical(summary[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(snapshot[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(inputs[LATEST_KEY]) == base.canonical(reference),
        "retain complete externally verifiable actual Rust V20 evidence",
    )
    assets = {
        INPUT_PATH: inputs_raw,
        SUMMARY_PATH: base.canonical(summary),
        SVG_PATH: svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes
            and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized full V91 evidence before publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
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
        v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
        previous_options(previous),
    )
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 90
        and prior["rejected_hostile_control_count"] == 10239
        and prior["authenticated_evidence_owner_lower_bound"] == 316
        and prior["authenticated_history_reference_lower_bound"] == 321
        and prior["lossless_previous_v89_proof_pool_count"] == 11
        and prior["lossless_v89_all_eleven_previous_pool_identity_status"] == "PASS"
        and prior["lossless_v89_complete_original_suite_reference_count"] == 39
        and prior["lossless_v90_zig_v10_complete_plaintext_receipt_count"] == 1
        and prior["lossless_v90_zig_v10_complete_source_owner_count"] == 3
        and prior["lossless_v90_zig_v10_complete_original_suite_count"] == 13
        and prior["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and prior["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and prior["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and prior["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and prior["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and prior["qualified_candidate_count"] == 0
        and prior["performance"] == "NOT MEASURED"
        and prior["outputs_written"] is False,
        "preserve all 10,239 independent prior controls and complete V90 history",
    )
    _, assets = build(
        previous, v89, v88, v87, v86, v85, v84, v83, v82,
        chain, base, options,
    )
    summary = base.document(assets[SUMMARY_PATH], "whole in-memory V91 summary")
    contract, receipt, facts = load_rust_evidence(base)
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
            base.need(False, "V91 accepted fabricated source evidence: " + label)

    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        reject(
            "omitted whole Rust V20 source contract field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-source"),
        ("version", 19),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("suite_count", 12),
        ("qualified_candidate_count", 1),
        ("candidate_qualified", True),
        ("candidate_correctness", "PASS"),
        ("candidate_matching", "PASS"),
        ("runtime_non_delegation", "PASS"),
        ("stdlib_regex_engine_allowed", True),
        ("external_regex_packages_allowed", True),
        ("matching_fallback_allowed", True),
        ("supplemental_cases_counted_in_original_denominator", True),
        ("expanded_holdout_cases_opened", 1),
        ("holdout", "OPENED"),
        ("actual_candidate_workers_started", 1),
        ("actual_native_libraries_loaded", 1),
        ("actual_build_archive_opens", 1),
        ("actual_private_build_root_opens", 1),
        ("actual_clock_samples", 1),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = wrong
        reject(
            "fabricated Rust V20 source outcome:" + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key in sorted(receipt):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        reject(
            "omitted whole actual Rust V20 receipt field " + key,
            lambda value=forged: validate_rust_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-receipt"),
        ("status", "FAIL"),
        ("publication_pass_means", "CANDIDATE QUALIFIED"),
        ("family", "external-regex"),
        ("campaign_source_sha256", "0" * 64),
        ("campaign_protocol_sha256", "0" * 64),
        ("campaign_contract_sha256", "0" * 64),
        ("actual_candidate_workers", 12),
        ("distinct_worker_process_id_count", 12),
        ("attempted_suite_count", 12),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", CASE_COUNT),
        ("infrastructure_failure_count", 0),
        ("semantic_mismatch_count", 1296),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("all_original_observation_vectors_complete", True),
        ("all_four_original_targets_restored", False),
        ("worker_failure_capture_count", 0),
        ("hidden_cases_read", 1),
        ("clock_samples", 1),
        ("timing_trials_run", 1),
        ("benchmark_files_read", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = wrong
        reject(
            "fabricated actual Rust V20 result:" + key,
            lambda value=forged: validate_rust_receipt(base, value),
        )
    for index, (suite, _) in enumerate(SUITES):
        forged = copy.deepcopy(receipt)
        forged["suite_integrity"][index]["suite"] = "invented-suite"
        reject(
            "omitted actual original Rust worker:" + suite,
            lambda value=forged: validate_rust_receipt(base, value),
        )
    for suite in ("substitution_v2", "shape_v2"):
        forged = copy.deepcopy(receipt)
        for row in forged["suite_integrity"]:
            if row["suite"] == suite:
                row["mismatch_count"] = 0
        reject(
            "concealed actual Rust semantic mismatch:" + suite,
            lambda value=forged: validate_rust_receipt(base, value),
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
            "fabricated complete actual Rust V20 reference:" + key,
            lambda value=forged: resolve_reference(base, pool, value),
        )
    forged = copy.deepcopy(pool)
    forged["entries"].pop(RUST_RECEIPT[1])
    reject(
        "omitted complete actual Rust V20 evidence pool entry",
        lambda value=forged:
        validate_evidence_pool(base, value, contract, receipt, facts),
    )
    forged = copy.deepcopy(pool)
    forged["entries"][RUST_RECEIPT[1]]["complete_original_suite_rows"].pop()
    reject(
        "omitted whole actual Rust V20 original suite proof",
        lambda value=forged:
        validate_evidence_pool(base, value, contract, receipt, facts),
    )
    old = authenticate_previous(
        previous, v89, v88, v87, v86, v85, v84, v83, v82, chain, base
    )
    for index, row in enumerate(summary["families"]):
        if row["family"] == "python":
            forged = copy.deepcopy(summary["families"])
            forged[index]["correctness"] = "INVENTED"
            reject(
                "changed exact Python baseline",
                lambda value=forged:
                validate_families(base, old, value, pool, reference, facts),
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
                "fabricated winner " + row["family"] + ":" + key,
                lambda value=forged:
                validate_families(base, old, value, pool, reference, facts),
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
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
    ):
        reject(
            "forbidden source-only side effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    base.need(rejected >= 450, "require complete hostile actual Rust V20 controls")
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
        "version": 91,
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
        "v91_new_directly_authenticated_owner_count": 4,
        "v91_new_directly_authenticated_rust_source_owner_count": 3,
        "v91_new_directly_authenticated_rust_plaintext_receipt_owner_count": 1,
        "lossless_previous_v90_proof_pool_count": len(OLD_POOLS),
        "lossless_v90_all_twelve_previous_pool_identity_status": "PASS",
        "lossless_v90_snapshot_identity_status": "PASS",
        "lossless_v90_family_identity_status": "PASS",
        "lossless_v89_complete_original_suite_reference_count": 39,
        "lossless_v90_zig_v10_complete_original_suite_count": 13,
        "lossless_v91_rust_v20_complete_plaintext_receipt_count": 1,
        "lossless_v91_rust_v20_complete_source_owner_count": 3,
        "lossless_v91_rust_v20_complete_original_suite_count": 13,
        "original_case_execution_denominator": CASE_COUNT,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v7_original_campaign_clean_suite_count": 2,
        "c_v7_original_campaign_completed_suite_count": 5,
        "c_v7_original_campaign_verified_passing_case_count": 13094,
        "c_v7_original_campaign_observed_mismatch_lower_bound": 236,
        "c_v7_original_campaign_candidate_execution_failure_count": 7,
        "c_v7_original_campaign_infrastructure_failure_count": 1,
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
        "rust_v20_original_campaign_infrastructure_failure_suite":
        "subinterpreter_v2",
        "rust_v20_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v20_original_campaign_all_four_original_targets_restored": True,
        "zig_v9_original_campaign_verified_passing_case_count": 927,
        "zig_v10_original_campaign_clean_suite_count": 6,
        "zig_v10_original_campaign_completed_suite_count": 9,
        "zig_v10_original_campaign_verified_passing_case_count": 3583,
        "zig_v10_original_campaign_observed_mismatch_lower_bound": 1540,
        "zig_v10_original_campaign_infrastructure_failure_count": 4,
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
        "publish only one bounded, exclusively created new V91 graph owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "publish complete V91 bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate the whole exclusively published V91 evidence owner",
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
    base.need(actual == raw, "reauthenticate every complete final V91 evidence byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V90:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in RUST_SOURCE:
        parser.add_argument("--rust-" + role + "-sha256", required=True)
    parser.add_argument("--rust-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, v89, v88, v87, v86, v85, v84, v83, v82, chain, base = load_previous()
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(
                previous, v89, v88, v87, v86, v85, v84, v83, v82,
                chain, base, options,
            )
        else:
            _, assets = build(
                previous, v89, v88, v87, v86, v85, v84, v83, v82,
                chain, base, options,
            )
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V91 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
