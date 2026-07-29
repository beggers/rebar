#!/usr/bin/env python3
"""Render an honest, reproducible comparison of first-party Python re engines."""

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
SELF = "tools/render_candidate_current_overview_v89.py"
OUTPUT = "docs/evidence/candidate-current-overview-v89"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v89"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 312
HISTORY_FLOOR = 317

V88 = {
    "source": (
        "tools/render_candidate_current_overview_v88.py",
        "b26143885163e913ec11d62f2d12bff1c8a85cbacbe0f16f242b01495f8fe46a",
        89262,
        430910,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v88.inputs.json",
        "3fed4008de0b2d1c7bbcb28661ab384e5b9ef39763e0a102659cf2798578e51d",
        1351447,
        430942,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v88.json",
        "85e826a424ea175f44cc639b1f0cfd61ed841059c43219e2cf96624316386e4d",
        4183967,
        430950,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v88.svg",
        "ac16cc09cd445707f334d02f5034bb382c9936c1383c9c3acc241a81ef584436",
        6748,
        430951,
    ),
}

RECEIPTS = {
    "c": (
        "oracle/phase2/evidence/"
        "repaired-c-original-campaign-v7-c-phase2-v18-c-subject-buffer-"
        "root-provenance-original-p0-v7-failures-publication-receipt.json",
        "bba4b8498a37db0bf9651c0bb040deaf96f9eef363ba6f2e2c923379d7fa5080",
        7375,
        525199,
    ),
    "rust": (
        "oracle/phase2/evidence/"
        "repaired-rust-original-campaign-v16-rust-phase2-v21-rust-"
        "captured-findall-root-provenance-original-p0-v19-failures-"
        "publication-receipt.json",
        "e48a4115a85d827cbf16a32b6b44390d2bf4b092e1823989c9bcafe874fa04fe",
        29374,
        525287,
    ),
    "zig": (
        "oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v9-phase2-v13-zig-guard-clean-v1-"
        "original-p0-v9-failures-publication-receipt.json",
        "9df60f301c11e16231483b5444b246196f906ea7eb6072a2c227feeb0b6e8dc8",
        88186,
        525312,
    ),
}

CAMPAIGN_SOURCE_PINS = {
    "c": {
        "source": "42d27c321a54cbe2a730ce20967f786bc354340c35501e9d2a4cd37b4948884e",
        "protocol": "99b3321a54cc36ad065f0d4178e34e0baf60349b4c85fb22794dbf26b33b9b0a",
        "contract": "ce59aa6e7b900095dad4875d6e911dd9983fa6834c7d810f2e8c729c1c880811",
    },
    "rust": {
        "source": "146a47218b87ba15fbfdd357db6d10b101a2869f30b51413ef8f5d5df79a5b48",
        "protocol": "e54bfacda42669e35e7052b058d41cb230aa128a4b2f8568316c03766de908d1",
        "contract": "d97ab35ea90761a01d343648c1701e56140f81f27e0a7fc9a39cc5f7ff9f81c8",
    },
    "zig": {
        "source": "5c894208a3bab5358cc84dcbf4ebeb2c17c47a381b00698618e8e23a2e39d38d",
        "protocol": "61fc1547a9b36dbb0aac90315a5bdaec544e8d599cb73dd51436153e995440dc",
        "contract": "f1b651f3ca7a55ae16543301b4a31ef8e4ff8701318d06b25a94bf70cccf0fee",
    },
}

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
        "5e82ece260c65c1b651512bf82cc952f6b5c9219e2baf5526148fc254b9a0570",
        9,
    ),
    (
        "lossless_actual_outcome_evidence_pool", 33507,
        "8adefd9ea0901086064674c4a9ba1300792a15ba381ffe93a0ef85c372dd345a",
        1,
    ),
    (
        "lossless_zig_source_evidence_pool", 23792,
        "1c4694aae8738a74713ddca5f9e88a83b4fdc0c81ddeac7bbfa30eb5db65f029",
        1,
    ),
    (
        "lossless_zig_actual_build_evidence_pool", 248256,
        "437c0d0f2f80e841fa7091d50b2094f9054e82c0e792f5db9de817cf2609dcae",
        1,
    ),
    (
        "lossless_v87_source_evidence_pool", 71364,
        "c4acf498232c0e95b3bb6c7425acb2258915e9fc369e66bd27b8e6bfd8c389ff",
        6,
    ),
    (
        "lossless_v87_rust_actual_build_evidence_pool", 11169,
        "7dadc62631aa838cfaa2a0c96d978b1457de11a4d3501fc2a6b456b319a30c21",
        1,
    ),
    (
        "lossless_v88_captured_source_evidence_pool", 19857,
        "ea9c5c1778e361c58e684e2d5e139a276af7751887f8a0e671df260080e2afa9",
        1,
    ),
    (
        "lossless_v88_captured_actual_build_evidence_pool", 11916,
        "01ee89ebdcf462cc2fc61721110bc94d4177deb1949e66d6c350909992cc58e9",
        1,
    ),
    (
        "lossless_v88_c_source_evidence_pool", 19315,
        "2818bd96e62af5aa82b3ee0e0f03f8cbe56ac54955599e32379755e8dd366d1b",
        1,
    ),
    (
        "lossless_v88_c_actual_build_evidence_pool", 14406,
        "264678f27d7ee4d2965d42f3129941ee49a5b041f66b16d090e629675bd3dd00",
        1,
    ),
)

POOL_KEY = "lossless_v89_original_campaign_receipt_reference_pool"
POOL_SCHEMA = SCHEMA + "-whole-receipt-owner-reference-pool-v1"
REFERENCE_SCHEMA = SCHEMA + "-whole-receipt-owner-reference-v1"
LATEST_KEYS = {
    "c": "c_v7_actual_original_campaign",
    "rust": "rust_v19_actual_original_campaign",
    "zig": "zig_v9_actual_original_campaign",
}


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject unbounded V89 evidence: " + label)
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
            raise ValueError("reject substituted complete V89 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V89 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V89 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject changed complete V89 owner: " + label)
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
        raise ValueError("V89 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V89 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V89 rejected an unverifiable file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V89 rejected an unverified descriptor or file owner")
    if mode not in (None, "r", "rb"):
        raise ValueError("V89 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V89 source-only operation cannot create or modify files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V89 rejected private-root or holdout access")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V89 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v89." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V89 rejected outputs, archives, benchmarks, or native code")


def load_previous() -> tuple[
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
    raw = read_fixed(V88["source"], "whole published V88 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v88")
    previous.__file__ = str(ROOT / V88["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v87, v86, v85, v84, v83, v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v88"
        and previous.SELF == V88["source"][0]
        and len(chain) == 15
        and sum(count for _, count in SUITES) == CASE_COUNT,
        "require pinned isolated CPython, exact V88 history, and all original checks",
    )
    return previous, v87, v86, v85, v84, v83, v82, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V88["source"][1],
        "source_bytes": V88["source"][2],
        "build_receipt_sha256": previous.BUILD_RECEIPT[1],
        "root_receipt_sha256": previous.ROOT_RECEIPT[1],
        "c_build_receipt_sha256": previous.C_BUILD_RECEIPT[1],
        "c_root_receipt_sha256": previous.C_ROOT_RECEIPT[1],
    }
    for role, item in previous.V87.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        pins["feature_" + role + "_sha256"] = item[1]
    for role, item in previous.C_FEATURE.items():
        pins["c_feature_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def authenticate_previous(
    previous: types.ModuleType,
    v87: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    snapshot, assets = previous.build(
        v87, v86, v85, v84, v83, v82, chain, base, previous_options(previous)
    )
    for role in ("inputs", "summary", "svg"):
        item = V88[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole published V88 " + role),
            "reproduce every byte of the committed V88 " + role,
        )
    old = base.document(assets[V88["summary"][0]], "whole immutable V88 summary")
    old_inputs = base.document(assets[V88["inputs"][0]], "whole immutable V88 inputs")
    base.need(
        old["version"] == 88
        and old_inputs["version"] == 88
        and old["snapshot"] == snapshot
        and old["authenticated_evidence_owner_lower_bound"] == 309
        and old["authenticated_history_reference_lower_bound"] == 314
        and [row.get("family") for row in old["families"]]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and old["families"][0]["correctness"] == "BASELINE PASS"
        and old["actual_rust_semantic_mismatch_count"] == 1440
        and old["actual_rust_verified_passing_case_count"] == 14853
        and old["actual_c_semantic_mismatch_count"] == 1230
        and old["actual_c_verified_passing_case_count"] == 7325
        and old["actual_zig_semantic_mismatch_count"] == 1764
        and old["rust_captured_v21_actual_build_status"] == "PASS"
        and old["rust_captured_v21_actual_compiler_process_count"] == 28
        and old["c_subject_v18_actual_build_status"] == "PASS"
        and old["c_subject_v18_actual_compiler_process_count"] == 14
        and old["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and old["preserved_previous_holdout_proposal_case_count"]
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and old["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
        and old["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and old["qualified_candidate_count"] == 0
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "retain exact previous builds, historical failures, baseline and sealed holdout",
    )
    for key, size, digest, count in OLD_POOLS:
        value = old.get(key)
        raw = base.canonical(value)
        base.need(
            type(value) is dict
            and len(raw) == size
            and base.digest(raw) == digest
            and type(value.get("entries")) is dict
            and len(value["entries"]) == count,
            "retain every complete, lossless published V88 proof pool: " + key,
        )
    return old, old_inputs


def suite_rows(base: types.ModuleType, rows: object, family: str) -> list[dict]:
    base.need(
        type(rows) is list and len(rows) == len(SUITES),
        "authenticate all thirteen complete original rows for " + family,
    )
    assert isinstance(rows, list)
    for row, (suite, case_count) in zip(rows, SUITES, strict=True):
        base.need(
            type(row) is dict
            and row.get("suite") == suite
            and row.get("case_execution_denominator") == case_count,
            "reject a missing, reordered, or changed " + family + " suite: " + suite,
        )
    return rows


def validate_c_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and len(value) == 52,
        "authenticate every field in the actual complete C V7 receipt",
    )
    assert isinstance(value, dict)
    pins = CAMPAIGN_SOURCE_PINS["c"]
    base.need(
        value["schema"]
        == "rebar-owned-repaired-c-original-campaign-v7-durable-publication-receipt"
        and value["version"] == 7
        and value["status"] == "PASS"
        and value["publication_status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE CORRECTNESS PUBLICATION ONLY"
        and value["family"] == "c"
        and value["label"]
        == "phase2-v18-c-subject-buffer-root-provenance-original-p0-v7"
        and value["source_sha256"] == pins["source"]
        and value["protocol_sha256"] == pins["protocol"]
        and value["contract_sha256"] == pins["contract"]
        and value["actual_candidate_workers"] == 13
        and value["actual_worker_process_ids_are_distinct"] is True
        and type(value["actual_worker_process_ids"]) is list
        and len(value["actual_worker_process_ids"]) == 13
        and value["attempted_suite_count"] == 13
        and value["suite_count"] == 13
        and value["completed_suite_count"] == 5
        and value["verified_passing_case_count"] == 13094
        and value["candidate_execution_failure_count"] == 7
        and value["infrastructure_failure_count"] == 1
        and value["observed_semantic_mismatch_lower_bound"] == 236
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["case_execution_denominator"] == CASE_COUNT
        and value["named_private_waiver_count"] == 13
        and value["separate_reference_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and value["separate_reference_cases_counted_as_candidate_cases"] is False
        and value["original_native_inode_restored"] is True
        and value["original_source_targets_modified"] == 0
        and value["worker_timeout_count"] == 0
        and value["hidden_cases_read"] == 0
        and value["clock_samples"] == 0
        and value["timing_trials_run"] == 0
        and value["benchmark_files_read"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and value["winner_selected"] is False,
        "reject a claimed C qualification, speedup, altered denominator or full result",
    )
    rows = suite_rows(base, value["suite_outcomes"], "c")
    clean = [row for row in rows if row["failure_class"] == "PASS"]
    mismatch = [row for row in rows if row["failure_class"] == "SEMANTIC MISMATCH"]
    execution = [
        row for row in rows if row["failure_class"] == "CANDIDATE EXECUTION FAILURE"
    ]
    infrastructure = [
        row for row in rows if row["failure_class"] == "WORKER INFRASTRUCTURE FAILURE"
    ]
    base.need(
        len(clean) == 2
        and len(mismatch) == 3
        and len(execution) == 7
        and len(infrastructure) == 1
        and len(clean) + len(mismatch) == value["completed_suite_count"]
        and sum(row["case_execution_denominator"] for row in clean) == 13094
        and all(row["status"] == "PASS" and row["mismatch_count"] == 0 for row in clean)
        and all(row["status"] == "FAIL" for row in mismatch + execution + infrastructure)
        and sum(row["mismatch_count"] for row in mismatch) == 236
        and all(row["mismatch_count"] == "NOT MEASURED" for row in execution + infrastructure),
        "derive C clean passes, observed differences and unfinished groups independently",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and archive["sha256"]
        == "5975fb4549ee6d848b2fc94dc58217982efcaf8ffc839c75d0e98430aa1eaab7"
        and archive["bytes"] == 26603
        and archive["path"].endswith(".json.gz"),
        "retain C archive metadata without opening the archive",
    )
    return {
        "family": "c",
        "display_name": "C",
        "attempted_suite_count": 13,
        "clean_suite_count": 2,
        "completed_suite_count": 5,
        "mismatch_suite_count": 3,
        "candidate_execution_failure_count": 7,
        "infrastructure_failure_count": 1,
        "verified_passing_case_count": 13094,
        "observed_semantic_mismatch_lower_bound": 236,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": pins["source"],
        "protocol_sha256": pins["protocol"],
        "contract_sha256": pins["contract"],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["bytes"],
    }


def validate_rust_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and len(value) == 93,
        "authenticate every field in the actual complete Rust V19 receipt",
    )
    assert isinstance(value, dict)
    pins = CAMPAIGN_SOURCE_PINS["rust"]
    base.need(
        value["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v19-durable-publication-receipt"
        and value["status"] == "PASS"
        and value["publication_status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and value["family"] == "rust"
        and value["label"]
        == "phase2-v21-rust-captured-findall-root-provenance-original-p0-v19"
        and value["campaign_source_sha256"] == pins["source"]
        and value["campaign_protocol_sha256"] == pins["protocol"]
        and value["campaign_contract_sha256"] == pins["contract"]
        and value["actual_candidate_workers"] == 13
        and type(value["actual_worker_process_ids"]) is list
        and len(value["actual_worker_process_ids"]) == 13
        and value["distinct_worker_process_id_count"] == 13
        and value["duplicate_worker_process_id_count"] == 0
        and value["missing_worker_process_id_count"] == 0
        and value["attempted_suite_count"] == 13
        and value["started_suite_count"] == 13
        and value["suite_count"] == 13
        and value["completed_suite_count"] == 8
        and value["verified_passing_case_count"] == 12942
        and value["infrastructure_failure_count"] == 5
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["case_execution_denominator"] == CASE_COUNT
        and value["named_private_waiver_count"] == 13
        and value["all_original_suite_rows_validated_before_publication"] is True
        and value["all_four_original_targets_restored"] is True
        and value["hidden_cases_read"] == 0
        and value["clock_samples"] == 0
        and value["timing_trials_run"] == 0
        and value["benchmark_files_read"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject claimed Rust qualification, speed, complete mismatch, or worker results",
    )
    rows = suite_rows(base, value["suite_integrity"], "rust")
    clean = [row for row in rows if row["failure_class"] == "PASS"]
    mismatch = [row for row in rows if row["failure_class"] == "SEMANTIC MISMATCH"]
    infrastructure = [
        row for row in rows if row["failure_class"] == "INFRASTRUCTURE FAILURE"
    ]
    base.need(
        len(clean) == 6
        and len(mismatch) == 2
        and len(infrastructure) == 5
        and len(clean) + len(mismatch) == value["completed_suite_count"]
        and all(row["fully_observed"] is True for row in clean + mismatch)
        and all(row["fully_observed"] is False for row in infrastructure)
        and all(row["mismatch_count"] == 0 for row in clean)
        and sum(row["verified_passing_case_count"] for row in clean) == 12942
        and sum(row["case_execution_denominator"] for row in clean) == 12942
        and sum(row["mismatch_count"] for row in mismatch) == 1296
        and all(row["mismatch_count"] == "NOT MEASURED" for row in infrastructure),
        "derive all real Rust clean, differing and incomplete suite results",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and archive["sha256"]
        == "403566c1b4d280f9f15cab57e637562c32b018c6f2a848bedb0fccf7af3ea23c"
        and archive["size_bytes"] == 3409969
        and archive["relative"].endswith(".json.gz"),
        "retain Rust archive metadata without opening the archive",
    )
    return {
        "family": "rust",
        "display_name": "Rust",
        "attempted_suite_count": 13,
        "clean_suite_count": 6,
        "completed_suite_count": 8,
        "mismatch_suite_count": 2,
        "candidate_execution_failure_count": 0,
        "infrastructure_failure_count": 5,
        "verified_passing_case_count": 12942,
        "observed_semantic_mismatch_lower_bound": 1296,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": pins["source"],
        "protocol_sha256": pins["protocol"],
        "contract_sha256": pins["contract"],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["size_bytes"],
    }


def validate_zig_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and len(value) == 42,
        "authenticate every field in the actual complete Zig V9 receipt",
    )
    assert isinstance(value, dict)
    pins = CAMPAIGN_SOURCE_PINS["zig"]
    base.need(
        value["schema"]
        == "rebar-owned-repaired-zig-original-campaign-v9-durable-publication-receipt"
        and value["status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and value["family"] == "zig"
        and value["label"] == "phase2-v13-zig-guard-clean-v1-original-p0-v9"
        and value["source_sha256"] == pins["source"]
        and value["protocol_sha256"] == pins["protocol"]
        and value["contract_sha256"] == pins["contract"]
        and value["actual_candidate_workers"] == 13
        and value["unique_candidate_worker_count"] == 13
        and value["all_original_suites_attempted"] is True
        and value["suite_count"] == 13
        and value["completed_suite_count"] == 3
        and value["verified_passing_case_count"] == 927
        and value["infrastructure_failure_count"] == 10
        and value["observed_semantic_mismatch_lower_bound"] == 0
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["case_execution_denominator"] == CASE_COUNT
        and value["all_three_original_targets_restored"] is True
        and value["timeout_count"] == 0
        and value["timed_out_suites"] == []
        and value["hidden_cases_read"] == 0
        and value["timing_trials_run"] == 0
        and value["benchmark_files_read"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["supplemental_candidate_matching"] == "NOT RUN"
        and value["winner_selected"] is False,
        "reject invented Zig compatibility, speed, complete imports or full result",
    )
    rows = suite_rows(base, value["original_suite_diagnostics"], "zig")
    clean = [row for row in rows if row["status"] == "PASS"]
    infrastructure = [row for row in rows if row["infrastructure_failure"] is True]
    proven = [row for row in rows if row.get("candidate_imported") is True]
    unknown = [row for row in rows if row.get("candidate_imported") is None]
    base.need(
        len(clean) == 3
        and len(infrastructure) == 10
        and len(proven) == 7
        and len(unknown) == 6
        and len(clean) == value["completed_suite_count"]
        and all(row["infrastructure_failure"] is False for row in clean)
        and all(row["observed_semantic_mismatch_count"] == 0 for row in clean)
        and sum(row["case_execution_denominator"] for row in clean) == 927
        and all(row["observed_semantic_mismatch_count"] == "NOT MEASURED"
                for row in infrastructure)
        and all(row.get("guard_installed_before_candidate_import") is True
                for row in proven)
        and all(row.get("guard_installed_before_candidate_import") is None
                for row in unknown)
        and all(row["timed_out"] is False for row in rows),
        "distinguish seven proven Zig imports from six genuinely unknown imports",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and archive["sha256"]
        == "370fbb7096c10dc4a06abe38a36e0a606eb1844742e1d2d2dc15884b7108a54f"
        and archive["bytes"] == 3501630
        and archive["name"].endswith(".json.gz"),
        "retain actual Zig archive metadata without opening the archive",
    )
    return {
        "family": "zig",
        "display_name": "Zig",
        "attempted_suite_count": 13,
        "clean_suite_count": 3,
        "completed_suite_count": 3,
        "mismatch_suite_count": 0,
        "candidate_execution_failure_count": "NOT MEASURED",
        "infrastructure_failure_count": 10,
        "verified_passing_case_count": 927,
        "observed_semantic_mismatch_lower_bound": 0,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "individually_proven_guarded_candidate_import_count": 7,
        "candidate_import_status_unknown_count": 6,
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": pins["source"],
        "protocol_sha256": pins["protocol"],
        "contract_sha256": pins["contract"],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["bytes"],
    }


VALIDATORS = {
    "c": validate_c_receipt,
    "rust": validate_rust_receipt,
    "zig": validate_zig_receipt,
}
ROW_KEYS = {
    "c": "suite_outcomes",
    "rust": "suite_integrity",
    "zig": "original_suite_diagnostics",
}


def load_campaigns(base: types.ModuleType) -> tuple[dict[str, dict], dict[str, dict]]:
    documents: dict[str, dict] = {}
    facts: dict[str, dict] = {}
    for family, item in RECEIPTS.items():
        raw = read_fixed(item, "whole actual " + family + " original-campaign receipt")
        value = base.document(raw, "whole actual " + family + " campaign receipt")
        base.need(
            base.canonical(value) == raw,
            "reject a noncanonical or partially authenticated " + family + " receipt",
        )
        documents[family] = value
        facts[family] = VALIDATORS[family](base, value)
    return documents, facts


def compact_suite_proof(base: types.ModuleType, family: str, row: dict) -> dict:
    common = {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_public_suite_row_sha256": base.digest(base.canonical(row)),
        "complete_public_suite_row_canonical_bytes": len(base.canonical(row)),
    }
    if family == "c":
        common.update({
            "status": row["status"],
            "failure_class": row["failure_class"],
            "observed_semantic_mismatch_count": row["mismatch_count"],
        })
    elif family == "rust":
        common.update({
            "failure_class": row["failure_class"],
            "fully_observed": row["fully_observed"],
            "observed_semantic_mismatch_count": row["mismatch_count"],
            "verified_passing_case_count": row["verified_passing_case_count"],
        })
    else:
        common.update({
            "status": row["status"],
            "infrastructure_failure": row["infrastructure_failure"],
            "observed_semantic_mismatch_count": row["observed_semantic_mismatch_count"],
            "candidate_imported": row.get("candidate_imported"),
            "guard_installed_before_candidate_import": row.get(
                "guard_installed_before_candidate_import"
            ),
            "timed_out": row["timed_out"],
        })
    return common


def make_campaign_pool(
    base: types.ModuleType,
    documents: dict[str, dict],
    facts: dict[str, dict],
) -> dict:
    entries = {}
    for family, item in RECEIPTS.items():
        document = documents[family]
        rows = document[ROW_KEYS[family]]
        entries[item[1]] = {
            "schema": SCHEMA + "-lossless-public-receipt-reference-v1",
            "family": family,
            "complete_plaintext_receipt_owner": base.synthetic_owner(
                item[:3], item[3]
            ),
            "complete_plaintext_receipt_sha256": item[1],
            "complete_plaintext_receipt_bytes": item[2],
            "complete_plaintext_receipt_field_count": len(document),
            "complete_plaintext_receipt_embedded": False,
            "complete_original_suite_count": len(rows),
            "complete_original_suite_rows": [
                compact_suite_proof(base, family, row) for row in rows
            ],
            "validated_campaign_outcome": copy.deepcopy(facts[family]),
            "compressed_archive_opened_by_graph": False,
            "complete_failure_diagnostics_available_at_public_receipt_owner": True,
        }
    pool = {
        "schema": POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "complete_public_receipt_reference_count": 3,
        "entries": entries,
    }
    validate_campaign_pool(base, pool, documents, facts)
    return pool


def validate_campaign_pool(
    base: types.ModuleType,
    pool: object,
    documents: dict[str, dict],
    facts: dict[str, dict],
) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {
            "schema", "version", "hash_algorithm",
            "complete_public_receipt_reference_count", "entries",
        }
        and pool["schema"] == POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and pool["complete_public_receipt_reference_count"] == 3
        and type(pool["entries"]) is dict
        and set(pool["entries"]) == {item[1] for item in RECEIPTS.values()},
        "require three complete digest-addressed original campaign receipt owners",
    )
    assert isinstance(pool, dict)
    for family, item in RECEIPTS.items():
        entry = pool["entries"][item[1]]
        document = documents[family]
        rows = document[ROW_KEYS[family]]
        base.need(
            type(entry) is dict
            and entry["schema"] == SCHEMA + "-lossless-public-receipt-reference-v1"
            and entry["family"] == family
            and base.canonical(entry["complete_plaintext_receipt_owner"])
            == base.canonical(base.synthetic_owner(item[:3], item[3]))
            and entry["complete_plaintext_receipt_sha256"] == item[1]
            and entry["complete_plaintext_receipt_bytes"] == item[2]
            and entry["complete_plaintext_receipt_field_count"] == len(document)
            and entry["complete_plaintext_receipt_embedded"] is False
            and entry["complete_original_suite_count"] == 13
            and base.canonical(entry["complete_original_suite_rows"])
            == base.canonical([
                compact_suite_proof(base, family, row) for row in rows
            ])
            and base.canonical(entry["validated_campaign_outcome"])
            == base.canonical(facts[family])
            and entry["compressed_archive_opened_by_graph"] is False
            and entry["complete_failure_diagnostics_available_at_public_receipt_owner"]
            is True,
            "reject omitted, swapped, guessed or truncated " + family + " evidence",
        )


def campaign_reference(base: types.ModuleType, family: str, pool: dict) -> dict:
    item = RECEIPTS[family]
    entry = pool["entries"][item[1]]
    return {
        "schema": REFERENCE_SCHEMA,
        "family": family,
        "complete_plaintext_receipt_sha256": item[1],
        "complete_plaintext_receipt_bytes": item[2],
        "complete_reference_sha256": base.digest(base.canonical(entry)),
        "complete_reference_canonical_bytes": len(base.canonical(entry)),
    }


def resolve_campaign_reference(
    base: types.ModuleType, pool: dict, reference: object, family: str,
) -> dict:
    item = RECEIPTS[family]
    base.need(
        type(reference) is dict
        and set(reference) == {
            "schema", "family", "complete_plaintext_receipt_sha256",
            "complete_plaintext_receipt_bytes", "complete_reference_sha256",
            "complete_reference_canonical_bytes",
        }
        and reference["schema"] == REFERENCE_SCHEMA
        and reference["family"] == family
        and reference["complete_plaintext_receipt_sha256"] == item[1]
        and reference["complete_plaintext_receipt_bytes"] == item[2],
        "reject an omitted or swapped complete " + family + " evidence reference",
    )
    assert isinstance(reference, dict)
    entry = pool["entries"].get(item[1])
    base.need(
        type(entry) is dict
        and base.checked(reference["complete_reference_sha256"], family + " proof")
        == base.digest(base.canonical(entry))
        and reference["complete_reference_canonical_bytes"]
        == len(base.canonical(entry)),
        "reject changed complete " + family + " suite proof",
    )
    return copy.deepcopy(entry)


def make_changes(facts: dict[str, dict], references: dict[str, dict]) -> dict:
    return {
        "actual_current_graph_predecessor_version": 88,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v89_new_directly_authenticated_public_receipt_owner_count": 3,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v7_original_campaign_actual_worker_count": 13,
        "c_v7_original_campaign_clean_suite_count": facts["c"]["clean_suite_count"],
        "c_v7_original_campaign_completed_suite_count": 5,
        "c_v7_original_campaign_verified_passing_case_count": 13094,
        "c_v7_original_campaign_mismatch_suite_count": 3,
        "c_v7_original_campaign_observed_mismatch_lower_bound": 236,
        "c_v7_original_campaign_candidate_execution_failure_count": 7,
        "c_v7_original_campaign_infrastructure_failure_count": 1,
        "c_v7_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v7_original_campaign_candidate_status": "FAIL",
        "rust_v19_original_campaign_actual_worker_count": 13,
        "rust_v19_original_campaign_clean_suite_count": 6,
        "rust_v19_original_campaign_completed_suite_count": 8,
        "rust_v19_original_campaign_verified_passing_case_count": 12942,
        "rust_v19_original_campaign_mismatch_suite_count": 2,
        "rust_v19_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v19_original_campaign_infrastructure_failure_count": 5,
        "rust_v19_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v19_original_campaign_candidate_status": "FAIL",
        "zig_v9_original_campaign_actual_worker_count": 13,
        "zig_v9_original_campaign_clean_suite_count": 3,
        "zig_v9_original_campaign_completed_suite_count": 3,
        "zig_v9_original_campaign_verified_passing_case_count": 927,
        "zig_v9_original_campaign_infrastructure_failure_count": 10,
        "zig_v9_original_campaign_observed_mismatch_lower_bound": 0,
        "zig_v9_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v9_original_campaign_individually_proven_guarded_import_count": 7,
        "zig_v9_original_campaign_unknown_guarded_import_count": 6,
        "zig_v9_original_campaign_candidate_status": "FAIL",
        "current_aggregate_semantic_mismatch_counts": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
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
        **{
            LATEST_KEYS[family]: copy.deepcopy(reference)
            for family, reference in references.items()
        },
    }


def make_svg() -> bytes:
    rows = (
        ("Python re", CASE_COUNT, "13 of 13 groups", "BASELINE", "#34d399"),
        (
            "C", 13094,
            "2 clean · 3 differ · 7 errors · 1 infrastructure failure",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "Rust", 12942,
            "6 clean · 2 differ · 5 infrastructure failures",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "Zig", 927,
            "3 clean · 10 infrastructure failures",
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
        '<desc id="description">Six independent first-party engines are compared against unchanged Python 3.14.6. The original compatibility test contains 31,237 checks in 13 groups. A separate set of 8,244 differential checks is not included in that denominator. C has 13,094 verified checks from two clean groups, three observed differing groups containing at least 236 differences, seven candidate execution failures, and one infrastructure failure. Rust has 12,942 verified checks from six clean groups, two observed differing groups containing at least 1,296 differences, and five infrastructure failures. Zig has 927 verified checks from three clean groups and ten infrastructure failures; candidate import is individually proven for seven workers and remains unknown for six. The complete mismatch totals for all three latest runs are not measured. C++, Go, and Fortran are retained as distinct first-party families. No engine is fully compatible, no speed or memory has been measured, and the proposed 14,155,776-case final comparison is sealed and has not been generated or run.</desc>',
        '<rect width="1440" height="970" rx="22" fill="#0b1220"/>',
        '<text x="44" y="60" fill="#f8fafc" font-size="31" font-family="system-ui,sans-serif" font-weight="730">Building a faster Python re, from scratch</text>',
        '<text x="44" y="97" fill="#cbd5e1" font-size="17" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<rect x="44" y="119" width="1352" height="57" rx="11" fill="#172338"/>',
        '<text x="62" y="144" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">What the bars mean: checks actually confirmed against Python, out of 31,237.</text>',
        '<text x="62" y="165" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Unfinished checks are unknown, not passes. The separate 8,244-check differential set is not counted.</text>',
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
            f'<rect x="161" y="{y-16}" width="365" height="20" '
            'rx="6" fill="#1e293b"/>'
        )
        if passed is not None:
            width = max(3, round(365 * passed / CASE_COUNT))
            parts.append(
                f'<rect x="161" y="{y-16}" width="{width}" height="20" '
                f'rx="6" fill="{colour}"/>'
            )
            label = f"{passed:,} / {CASE_COUNT:,}"
        else:
            label = "NOT MEASURED"
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
        '<text x="48" y="709" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="670">Compatibility, not just a successful build</text>',
        '<text x="48" y="738" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">C completed 5 of 13 groups; Rust completed 8 of 13; Zig completed 3 of 13.</text>',
        '<text x="48" y="761" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Observed differences: C at least 236; Rust at least 1,296. Complete totals remain NOT MEASURED.</text>',
        '<text x="48" y="784" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Zig: 7 worker imports individually proven; 6 unknown. Zero observed differences applies only to its 3 clean groups.</text>',
        '<text x="48" y="807" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">A published test report or reproducible native build does not mean the candidate passed.</text>',
        '<rect x="44" y="830" width="1352" height="91" rx="12" fill="#172338"/>',
        '<text x="62" y="858" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="670">Proposed final speed comparison: 14,155,776 cases</text>',
        '<text x="62" y="882" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Not frozen, not generated, not opened, and not run. Speed, memory, confidence, and rankings: NOT MEASURED.</text>',
        '<text x="62" y="905" fill="#cbd5e1" font-size="12" font-family="system-ui,sans-serif">The earlier 4,194,304-case proposal remains preserved as history; no winner has been selected.</text>',
        '<text x="48" y="951" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 89 · complete previous evidence preserved · no external regex wrapper · no fully compatible replacement.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def validate_families(
    base: types.ModuleType,
    old: dict,
    families: object,
    pool: dict,
    references: dict[str, dict],
    facts: dict[str, dict],
) -> None:
    base.need(
        type(families) is list and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain unchanged Python and exactly six independent first-party families",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row["family"] == family,
            "reject a missing, fabricated, or substituted family: " + family,
        )
        if family == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "preserve every byte of the unchanged Python baseline",
            )
            continue
        base.need(
            row["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
            and row["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "reject an invented compatible, independent, or faster " + family,
        )
        restored = copy.deepcopy(row)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if family in RECEIPTS:
            proof = resolve_campaign_reference(
                base, pool, row.get(LATEST_KEYS[family]), family
            )
            base.need(
                base.canonical(proof["validated_campaign_outcome"])
                == base.canonical(facts[family])
                and base.canonical(row["v89_latest_original_campaign"])
                == base.canonical(facts[family])
                and base.canonical(row[LATEST_KEYS[family]])
                == base.canonical(references[family]),
                "recover complete proven latest results for " + family,
            )
            restored.pop(LATEST_KEYS[family])
            restored.pop("v89_latest_original_campaign")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore every byte of the historical V88 family: " + family,
        )


def build(
    previous: types.ModuleType,
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
        "caller-pin the whole immutable V89 renderer source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole immutable V89 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V88.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the complete committed V88 " + role,
        )
    for family, item in RECEIPTS.items():
        base.need(
            getattr(options, family + "_receipt_sha256") == item[1],
            "caller-pin the complete actual " + family + " original receipt",
        )
        for role, expected in CAMPAIGN_SOURCE_PINS[family].items():
            base.need(
                getattr(options, family + "_" + role + "_sha256") == expected,
                "caller-pin the receipt-proven " + family + " " + role,
            )
    old, _ = authenticate_previous(
        previous, v87, v86, v85, v84, v83, v82, chain, base
    )
    documents, facts = load_campaigns(base)
    pool = make_campaign_pool(base, documents, facts)
    references = {
        family: campaign_reference(base, family, pool) for family in RECEIPTS
    }
    changes = make_changes(facts, references)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V88.items()
    }
    snapshot = {
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 89,
        "previous_complete_snapshot_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_overview_sha256": V88["summary"][1],
        "previous_complete_overview_bytes": V88["summary"][2],
        **copy.deepcopy(changes),
    }
    headline = {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "python_version": "3.14.6",
        "independent_first_party_candidate_family_count": 6,
        "fully_compatible_candidate_count": 0,
        "original_python_check_count": CASE_COUNT,
        "original_python_suite_count": 13,
        "separate_additional_differential_check_count": SUPPLEMENTAL_CASE_COUNT,
        "separate_additional_checks_in_original_denominator": False,
        "verified_original_checks_by_candidate": {
            "c": 13094,
            "rust": 12942,
            "zig": 927,
            "cpp": "NOT MEASURED",
            "go": "NOT MEASURED",
            "fortran": "NOT MEASURED",
        },
        "latest_complete_candidate_mismatch_totals": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "proposed_final_comparison_case_count": HOLDOUT_PROPOSAL_COUNT,
        "proposed_final_comparison_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "winner_selected": False,
    }
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 89,
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
        if family in RECEIPTS:
            row[LATEST_KEYS[family]] = copy.deepcopy(references[family])
            row["v89_latest_original_campaign"] = copy.deepcopy(facts[family])
    validate_families(base, old, families, pool, references, facts)
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = {
        "schema": SCHEMA + "-summary",
        "version": 89,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v88_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v88_snapshot_canonical_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_v88_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "lossless_v88_snapshot_identity_status": "PASS",
        "lossless_v88_family_identity_status": "PASS",
        "lossless_v88_all_ten_previous_pool_identity_status": "PASS",
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v89_original_campaign_receipt_reference_pool_entry_count": 3,
        "lossless_v89_complete_original_suite_reference_count": 39,
        "latest_original_campaigns": copy.deepcopy(facts),
        **{
            key: copy.deepcopy(old[key]) for key, _, _, _ in OLD_POOLS
        },
        **copy.deepcopy(changes),
    }
    for key, size, digest, count in OLD_POOLS:
        raw = base.canonical(summary[key])
        base.need(
            len(raw) == size
            and base.digest(raw) == digest
            and base.canonical(summary[key]) == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "preserve the exact complete V88 proof pool in V89: " + key,
        )
    base.need(
        base.canonical(summary["previous_v88_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(families[0]) == base.canonical(old["families"][0])
        and summary["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
        and summary["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
        and summary["qualified_candidate_count"] == 0
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False,
        "preserve baseline, all history, unread holdout and absence of a winner",
    )
    validate_campaign_pool(base, summary[POOL_KEY], documents, facts)
    for family, reference in references.items():
        recovered = resolve_campaign_reference(base, pool, reference, family)
        base.need(
            base.canonical(recovered["validated_campaign_outcome"])
            == base.canonical(facts[family])
            and base.canonical(summary[LATEST_KEYS[family]])
            == base.canonical(reference)
            and base.canonical(snapshot[LATEST_KEYS[family]])
            == base.canonical(reference)
            and base.canonical(inputs[LATEST_KEYS[family]])
            == base.canonical(reference),
            "preserve every complete, nonembedded " + family + " outcome reference",
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
            "reject an oversized whole V89 output before any publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
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
        v87, v86, v85, v84, v83, v82, chain, base, previous_options(previous)
    )
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 88
        and prior["rejected_hostile_control_count"] == 9622
        and prior["authenticated_evidence_owner_lower_bound"] == 309
        and prior["authenticated_history_reference_lower_bound"] == 314
        and prior["lossless_family_evidence_pool_entry_count"] == 9
        and prior["lossless_v87_source_evidence_pool_entry_count"] == 6
        and prior["lossless_v88_captured_source_evidence_pool_entry_count"] == 1
        and prior["lossless_v88_captured_actual_build_evidence_pool_entry_count"] == 1
        and prior["lossless_v88_c_source_evidence_pool_entry_count"] == 1
        and prior["lossless_v88_c_actual_build_evidence_pool_entry_count"] == 1
        and prior["actual_v20_build_status"] == "PASS"
        and prior["actual_v21_captured_build_status"] == "PASS"
        and prior["actual_v18_c_build_status"] == "PASS"
        and prior["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and prior["qualified_candidate_count"] == 0
        and prior["performance"] == "NOT MEASURED"
        and prior["outputs_written"] is False,
        "preserve all 9,622 independent hostile controls and the entire V88 evidence",
    )
    _, assets = build(
        previous, v87, v86, v85, v84, v83, v82, chain, base, options
    )
    summary = base.document(assets[SUMMARY_PATH], "whole in-memory V89 summary")
    documents, facts = load_campaigns(base)
    pool = summary[POOL_KEY]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            assert callable(callback)
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V89 accepted fabricated source evidence: " + label)

    for family, genuine in documents.items():
        validator = VALIDATORS[family]
        for key in sorted(genuine):
            forged = copy.deepcopy(genuine)
            forged.pop(key)
            reject(
                "omitted complete " + family + " receipt field " + key,
                lambda value=forged, validate=validator: validate(base, value),
            )
        for key, wrong in (
            ("status", "FAIL"),
            ("family", "external-regex"),
            ("candidate_status", "PASS"),
            ("candidate_qualified", True),
            ("semantic_mismatch_count", 0),
            ("verified_passing_case_count", CASE_COUNT),
            ("infrastructure_failure_count", 0),
            ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
            ("holdout", "OPENED"),
            ("performance", "1.5x"),
            ("memory", "FASTER"),
            ("timing_trials_run", 1),
            ("hidden_cases_read", 1),
            ("winner_selected", True),
        ):
            forged = copy.deepcopy(genuine)
            forged[key] = wrong
            reject(
                "invented " + family + " outcome:" + key,
                lambda value=forged, validate=validator: validate(base, value),
            )
        rows = genuine[ROW_KEYS[family]]
        for index in range(len(rows)):
            forged = copy.deepcopy(genuine)
            forged[ROW_KEYS[family]][index]["suite"] = "invented-suite"
            reject(
                "missing actual " + family + " complete row:" + str(index),
                lambda value=forged, validate=validator: validate(base, value),
            )
        reference = summary[LATEST_KEYS[family]]
        for key, wrong in (
            ("schema", "fabricated-reference"),
            ("family", "borrowed-engine"),
            ("complete_plaintext_receipt_sha256", "0" * 64),
            ("complete_plaintext_receipt_bytes", 1),
            ("complete_reference_sha256", "0" * 64),
            ("complete_reference_canonical_bytes", 1),
        ):
            forged = copy.deepcopy(reference)
            forged[key] = wrong
            reject(
                "fabricated complete " + family + " owner reference:" + key,
                lambda value=forged, role=family:
                resolve_campaign_reference(base, pool, value, role),
            )
        base.need(
            base.canonical(resolve_campaign_reference(base, pool, reference, family)
                           ["validated_campaign_outcome"])
            == base.canonical(facts[family]),
            "reconstruct every exact source-only " + family + " campaign result",
        )
    for family in RECEIPTS:
        forged = copy.deepcopy(pool)
        forged["entries"].pop(RECEIPTS[family][1])
        reject(
            "omitted whole public " + family + " receipt proof",
            lambda value=forged: validate_campaign_pool(base, value, documents, facts),
        )
        forged = copy.deepcopy(pool)
        forged["entries"][RECEIPTS[family][1]]["complete_original_suite_rows"].pop()
        reject(
            "omitted authentic " + family + " complete suite proof",
            lambda value=forged: validate_campaign_pool(base, value, documents, facts),
        )
    old, _ = authenticate_previous(
        previous, v87, v86, v85, v84, v83, v82, chain, base
    )
    references = {
        family: copy.deepcopy(summary[LATEST_KEYS[family]]) for family in RECEIPTS
    }
    for index, row in enumerate(summary["families"]):
        if row["family"] == "python":
            forged = copy.deepcopy(summary["families"])
            forged[index]["correctness"] = "INVENTED"
            reject(
                "changed whole baseline",
                lambda value=forged:
                validate_families(base, old, value, pool, references, facts),
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
                "invented winning " + row["family"] + ":" + key,
                lambda value=forged:
                validate_families(base, old, value, pool, references, facts),
            )
    for event, arguments in (
        ("open", (str(ROOT / "hidden.gz"), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / INPUT_PATH), "rb", os.O_RDONLY)),
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
            "forbidden V89 source-only side effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    base.need(rejected >= 300, "require complete hostile original campaign controls")
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
        "version": 89,
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
        "lossless_previous_v88_proof_pool_count": len(OLD_POOLS),
        "lossless_v88_all_ten_previous_pool_identity_status": "PASS",
        "lossless_v88_snapshot_identity_status": "PASS",
        "lossless_v88_family_identity_status": "PASS",
        "lossless_v89_original_campaign_receipt_reference_pool_entry_count": 3,
        "lossless_v89_complete_original_suite_reference_count": 39,
        "original_case_execution_denominator": CASE_COUNT,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v7_original_campaign_clean_suite_count": 2,
        "c_v7_original_campaign_completed_suite_count": 5,
        "c_v7_original_campaign_verified_passing_case_count": 13094,
        "c_v7_original_campaign_observed_mismatch_lower_bound": 236,
        "c_v7_original_campaign_candidate_execution_failure_count": 7,
        "c_v7_original_campaign_infrastructure_failure_count": 1,
        "c_v7_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v19_original_campaign_clean_suite_count": 6,
        "rust_v19_original_campaign_completed_suite_count": 8,
        "rust_v19_original_campaign_verified_passing_case_count": 12942,
        "rust_v19_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v19_original_campaign_infrastructure_failure_count": 5,
        "rust_v19_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v9_original_campaign_clean_suite_count": 3,
        "zig_v9_original_campaign_completed_suite_count": 3,
        "zig_v9_original_campaign_verified_passing_case_count": 927,
        "zig_v9_original_campaign_infrastructure_failure_count": 10,
        "zig_v9_original_campaign_observed_mismatch_lower_bound": 0,
        "zig_v9_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v9_original_campaign_individually_proven_guarded_import_count": 7,
        "zig_v9_original_campaign_unknown_guarded_import_count": 6,
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
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
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
        "publish only one authorized, new and bounded V89 evidence owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "publish complete V89 bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate the complete, exclusive published V89 owner",
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
    base.need(actual == raw, "reauthenticate every byte of final V89 evidence")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V88:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for family in RECEIPTS:
        parser.add_argument("--" + family + "-receipt-sha256", required=True)
        for role in CAMPAIGN_SOURCE_PINS[family]:
            parser.add_argument("--" + family + "-" + role + "-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, v87, v86, v85, v84, v83, v82, chain, base = load_previous()
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(
                previous, v87, v86, v85, v84, v83, v82, chain, base, options
            )
        else:
            _, assets = build(
                previous, v87, v86, v85, v84, v83, v82, chain, base, options
            )
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V89 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
