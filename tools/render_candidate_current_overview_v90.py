#!/usr/bin/env python3
"""Render the measured progress toward a from-scratch Python re replacement."""

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
SELF = "tools/render_candidate_current_overview_v90.py"
OUTPUT = "docs/evidence/candidate-current-overview-v90"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v90"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 316
HISTORY_FLOOR = 321

V89 = {
    "source": (
        "tools/render_candidate_current_overview_v89.py",
        "da15d1e4b58bdc04d83df3ebcc18995f1b5ffe662504dbdbd128e706f0371f09",
        74653,
        431417,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v89.inputs.json",
        "77a6cb593906c342faa7266e4a8118b414605a2977968dcbdb30a8d547dc25fe",
        10835,
        431447,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v89.summary.json",
        "951e13cb42d638a58bfd01621f682a4a3336c03b769179194d6120ff046a1f4d",
        3007567,
        431448,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v89.svg",
        "f2b58c8ad9eb41b7e266371f5d8a82430697ee3bc81b516d04e8f6d70ae79fa0",
        8858,
        431449,
    ),
}

ZIG_SOURCE = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v10.py",
        "514c00a001c78bded833e6752f995986d3f7f1ac1535cddfb641fe0c5ec9ddd2",
        219644,
        431416,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V10.md",
        "411c9c7cb62c4851ddcf58da8568f994420abcd2095cb1ec582203839c6f1e15",
        5943,
        525352,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v10.json",
        "5635b3e87a4b3158b107219c037fc13448dd92cc2296143024be825cfe1b4ffd",
        39991,
        525354,
    ),
}

ZIG_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v10-phase2-v13-zig-guard-clean-v1-"
    "original-p0-v10-failures-publication-receipt.json",
    "a13fad7e8e55af47235ddabd8f12d607a2c352b4d5b5d22f9422627381a10da7",
    89102,
    525391,
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
        "lossless_family_evidence_pool",
        126464,
        "5e82ece260c65c1b651512bf82cc952f6b5c9219e2baf5526148fc254b9a0570",
        9,
    ),
    (
        "lossless_actual_outcome_evidence_pool",
        33507,
        "8adefd9ea0901086064674c4a9ba1300792a15ba381ffe93a0ef85c372dd345a",
        1,
    ),
    (
        "lossless_zig_source_evidence_pool",
        23792,
        "1c4694aae8738a74713ddca5f9e88a83b4fdc0c81ddeac7bbfa30eb5db65f029",
        1,
    ),
    (
        "lossless_zig_actual_build_evidence_pool",
        248256,
        "437c0d0f2f80e841fa7091d50b2094f9054e82c0e792f5db9de817cf2609dcae",
        1,
    ),
    (
        "lossless_v87_source_evidence_pool",
        71364,
        "c4acf498232c0e95b3bb6c7425acb2258915e9fc369e66bd27b8e6bfd8c389ff",
        6,
    ),
    (
        "lossless_v87_rust_actual_build_evidence_pool",
        11169,
        "7dadc62631aa838cfaa2a0c96d978b1457de11a4d3501fc2a6b456b319a30c21",
        1,
    ),
    (
        "lossless_v88_captured_source_evidence_pool",
        19857,
        "ea9c5c1778e361c58e684e2d5e139a276af7751887f8a0e671df260080e2afa9",
        1,
    ),
    (
        "lossless_v88_captured_actual_build_evidence_pool",
        11916,
        "01ee89ebdcf462cc2fc61721110bc94d4177deb1949e66d6c350909992cc58e9",
        1,
    ),
    (
        "lossless_v88_c_source_evidence_pool",
        19315,
        "2818bd96e62af5aa82b3ee0e0f03f8cbe56ac54955599e32379755e8dd366d1b",
        1,
    ),
    (
        "lossless_v88_c_actual_build_evidence_pool",
        14406,
        "264678f27d7ee4d2965d42f3129941ee49a5b041f66b16d090e629675bd3dd00",
        1,
    ),
    (
        "lossless_v89_original_campaign_receipt_reference_pool",
        19205,
        "5627d67752d6efaefea4c77d2904c32d568b32eaeed06ad721727f3753f632d7",
        3,
    ),
)

POOL_KEY = "lossless_v90_zig_v10_original_campaign_evidence_pool"
POOL_SCHEMA = SCHEMA + "-lossless-complete-zig-original-campaign-pool-v1"
ENTRY_SCHEMA = SCHEMA + "-lossless-complete-zig-original-campaign-entry-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-zig-original-campaign-reference-v1"
LATEST_KEY = "zig_v10_actual_original_campaign"


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject unbounded V90 evidence: " + label)
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
            raise ValueError("reject substituted complete V90 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V90 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V90 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_nlink,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_nlink,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("reject changed complete V90 owner: " + label)
        return raw
    finally:
        os.close(handle)


FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen",
    "os.system",
    "os.posix_spawn",
    "os.posix_spawnp",
    "os.fork",
    "os.forkpty",
    "ctypes.dlopen",
    "ctypes.dlsym",
    "socket.__new__",
    "socket.connect",
    "socket.bind",
    "socket.sendto",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex",
    "ctypes",
    "subprocess",
    "multiprocessing",
    "socket",
    "time",
    "gzip",
    "bz2",
    "lzma",
    "tarfile",
    "zipfile",
})


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V90 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V90 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V90 rejected an unverifiable file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V90 rejected an unverified descriptor or file owner")
    if mode not in (None, "r", "rb"):
        raise ValueError("V90 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V90 source-only operation cannot create or modify files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V90 rejected private-root or holdout access")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V90 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v90." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V90 rejected outputs, archives, benchmarks, or native code")


def load_previous() -> tuple[
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
    raw = read_fixed(V89["source"], "whole published V89 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v89")
    previous.__file__ = str(ROOT / V89["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v88, v87, v86, v85, v84, v83, v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v89"
        and previous.SELF == V89["source"][0]
        and len(chain) == 15
        and sum(count for _, count in SUITES) == CASE_COUNT,
        "require pinned isolated CPython, exact V89 history, and all original checks",
    )
    return previous, v88, v87, v86, v85, v84, v83, v82, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V89["source"][1],
        "source_bytes": V89["source"][2],
    }
    for role, item in previous.V88.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for family, item in previous.RECEIPTS.items():
        pins[family + "_receipt_sha256"] = item[1]
        for role, expected in previous.CAMPAIGN_SOURCE_PINS[family].items():
            pins[family + "_" + role + "_sha256"] = expected
    return argparse.Namespace(**pins)


def authenticate_previous(
    previous: types.ModuleType,
    v88: types.ModuleType,
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
        v88,
        v87,
        v86,
        v85,
        v84,
        v83,
        v82,
        chain,
        base,
        previous_options(previous),
    )
    for role in ("inputs", "summary", "svg"):
        item = V89[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole published V89 " + role),
            "reproduce every byte of the committed V89 " + role,
        )
    old = base.document(assets[V89["summary"][0]], "whole immutable V89 summary")
    old_inputs = base.document(assets[V89["inputs"][0]], "whole immutable V89 inputs")
    historical = old["previous_v88_snapshot"]
    base.need(
        old["version"] == 89
        and old_inputs["version"] == 89
        and old["snapshot"] == snapshot
        and old["authenticated_evidence_owner_lower_bound"] == 312
        and old["authenticated_history_reference_lower_bound"] == 317
        and [row.get("family") for row in old["families"]]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and old["families"][0]["correctness"] == "BASELINE PASS"
        and historical["actual_rust_semantic_mismatch_count"] == 1440
        and historical["actual_rust_verified_passing_case_count"] == 14853
        and historical["actual_c_semantic_mismatch_count"] == 1230
        and historical["actual_c_verified_passing_case_count"] == 7325
        and historical["actual_zig_semantic_mismatch_count"] == 1764
        and historical["rust_captured_v21_actual_build_status"] == "PASS"
        and historical["rust_captured_v21_actual_compiler_process_count"] == 28
        and historical["c_subject_v18_actual_build_status"] == "PASS"
        and historical["c_subject_v18_actual_compiler_process_count"] == 14
        and old["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and old["c_v7_original_campaign_observed_mismatch_lower_bound"] == 236
        and old["c_v7_original_campaign_completed_suite_count"] == 5
        and old["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and old["rust_v19_original_campaign_observed_mismatch_lower_bound"] == 1296
        and old["rust_v19_original_campaign_completed_suite_count"] == 8
        and old["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and old["zig_v9_original_campaign_completed_suite_count"] == 3
        and old["zig_v9_original_campaign_infrastructure_failure_count"] == 10
        and old["zig_v9_original_campaign_individually_proven_guarded_import_count"]
        == 7
        and old["zig_v9_original_campaign_unknown_guarded_import_count"] == 6
        and old["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and old["preserved_previous_holdout_proposal_case_count"]
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and old["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
        and old["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and old["qualified_candidate_count"] == 0
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["performance"] == "NOT MEASURED"
        and old["memory"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False
        and old["winner_selected"] is False,
        "retain all proven current and historical outcomes and the sealed holdout",
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
            "retain every complete, lossless published V89 proof pool: " + key,
        )
    return old, old_inputs


def validate_source_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and len(value) == 43,
        "authenticate every field of the complete first-party Zig V10 contract",
    )
    assert isinstance(value, dict)
    oracle = value["original_oracle"]
    effects = value["source_only_effects"]
    pinned = value["pinned_cpython"]
    base.need(
        value["schema"]
        == "rebar-owned-repaired-zig-original-campaign-v10-guard-clean-source-freeze"
        and value["version"] == 10
        and value["status"] == "SOURCE FROZEN; CORRECTED ZIG MATCHING NOT RUN"
        and value["family"] == "zig"
        and value["label"] == "phase2-v13-zig-guard-clean-v1-original-p0-v10"
        and type(pinned) is dict
        and pinned["path"] == PYTHON
        and pinned["version"] == "3.14.6"
        and pinned["flags"] == ["-I", "-B", "-S"]
        and value["holdout"] == "NOT OPENED"
        and value["holdout_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and value["holdout_case_status"]
        == "PROPOSED; NOT FROZEN; NOT GENERATED; NOT OPENED"
        and value["historical_holdout_case_count"] == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and value["runtime_non_delegation"] == "NOT ESTABLISHED"
        and value["qualified_candidate_count"] == 0
        and value["current_qualified_candidates"] == 0
        and value["winner_selected"] is False
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED",
        "reject invented Zig compatibility, speed, independence, or holdout access",
    )
    for role in ("source", "protocol"):
        item = ZIG_SOURCE[role]
        expected_owner = base.synthetic_owner(item[:3], item[3])
        expected_owner.pop("uid")
        base.need(
            base.canonical(value[role])
            == base.canonical(expected_owner),
            "authenticate the whole first-party Zig V10 " + role + " owner",
        )
    base.need(
        type(oracle) is dict
        and len(oracle) == 12
        and oracle["case_execution_denominator"] == CASE_COUNT
        and oracle["suite_count"] == 13
        and oracle["named_private_waiver_count"] == 13
        and oracle["crosswalk_count"] == 34
        and oracle["obligation_count"] == 73
        and oracle["supplemental_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and oracle["supplemental_cases_added_to_original_denominator"] is False
        and oracle["supplemental_candidate_matching"] == "NOT RUN"
        and oracle["supplemental_reference_workers"] == 2
        and type(oracle["suites"]) is list
        and len(oracle["suites"]) == 13,
        "preserve the full frozen original denominator and separate reference cases",
    )
    for row, (suite, count) in zip(oracle["suites"], SUITES, strict=True):
        base.need(
            type(row) is dict
            and row["id"] == suite
            and row["case_execution_count"] == count,
            "reject a missing or replaced original Zig V10 suite: " + suite,
        )
    base.need(
        type(effects) is dict
        and len(effects) == 20
        and all(type(number) is int and number == 0 for number in effects.values()),
        "reject candidate runs, native loads, hidden cases, writes, or timing",
    )
    return value


def validate_zig_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and len(value) == 42,
        "authenticate every field of the actual complete Zig V10 receipt",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-zig-original-campaign-v10-durable-publication-receipt"
        and value["status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and value["family"] == "zig"
        and value["label"] == "phase2-v13-zig-guard-clean-v1-original-p0-v10"
        and value["source_sha256"] == ZIG_SOURCE["source"][1]
        and value["protocol_sha256"] == ZIG_SOURCE["protocol"][1]
        and value["contract_sha256"] == ZIG_SOURCE["contract"][1]
        and value["actual_candidate_workers"] == 13
        and value["unique_candidate_worker_count"] == 13
        and value["all_original_suites_attempted"] is True
        and value["suite_count"] == 13
        and value["completed_suite_count"] == 9
        and value["verified_passing_case_count"] == 3583
        and value["infrastructure_failure_count"] == 4
        and value["observed_semantic_mismatch_lower_bound"] == 1540
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["original_campaign_passed"] is False
        and value["case_execution_denominator"] == CASE_COUNT
        and value["all_three_original_targets_restored"] is True
        and value["maximum_serial_worker_timeout_seconds"] == 1560
        and value["per_suite_timeout_seconds"] == 120
        and value["timeout_classification"] == "INFRASTRUCTURE FAILURE"
        and value["timeout_count"] == 0
        and value["timed_out_suites"] == []
        and value["hidden_cases_read"] == 0
        and value["timing_trials_run"] == 0
        and value["benchmark_files_read"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["supplemental_candidate_matching"] == "NOT RUN"
        and value["winner_selected"] is False
        and value["uncompressed_bytes"] == 169321651
        and value["uncompressed_sha256"]
        == "7f08147141a0aefd2f47a77379ec9121fe21b8afa4633270edb3e3e874a0b2ff",
        "reject claimed Zig qualification, full mismatch count, speed, or timing",
    )
    rows = value["original_suite_diagnostics"]
    base.need(
        type(rows) is list and len(rows) == 13,
        "authenticate every complete original Zig V10 suite diagnostic",
    )
    for row, (suite, count) in zip(rows, SUITES, strict=True):
        base.need(
            type(row) is dict
            and len(row) == 26
            and row["suite"] == suite
            and row["case_execution_denominator"] == count
            and row["timed_out"] is False,
            "reject a missing, changed, timed-out, or substituted Zig suite: " + suite,
        )
    clean = [row for row in rows if row["status"] == "PASS"]
    mismatch = [
        row for row in rows
        if row["status"] == "FAIL" and row["infrastructure_failure"] is False
    ]
    infrastructure = [row for row in rows if row["infrastructure_failure"] is True]
    proven = [
        row for row in rows
        if row.get("candidate_imported") is True
        and row.get("guard_installed_before_candidate_import") is True
    ]
    unknown = [
        row for row in rows
        if row.get("candidate_imported") is None
        and row.get("guard_installed_before_candidate_import") is None
    ]
    base.need(
        len(clean) == 6
        and len(mismatch) == 3
        and len(infrastructure) == 4
        and len(clean) + len(mismatch) == value["completed_suite_count"]
        and len(clean) + len(mismatch) + len(infrastructure) == len(rows)
        and sum(row["case_execution_denominator"] for row in clean) == 3583
        and all(row["infrastructure_failure"] is False for row in clean)
        and all(row["observed_semantic_mismatch_count"] == 0 for row in clean)
        and all(
            type(row["observed_semantic_mismatch_count"]) is int
            and row["observed_semantic_mismatch_count"] > 0
            for row in mismatch
        )
        and sum(row["observed_semantic_mismatch_count"] for row in mismatch)
        == 1540
        and all(row["status"] == "FAIL" for row in infrastructure)
        and all(
            row["observed_semantic_mismatch_count"] == "NOT MEASURED"
            for row in infrastructure
        )
        and len(proven) == 10
        and len(unknown) == 3
        and len(proven) + len(unknown) == len(rows)
        and sum(
            1 for row in infrastructure
            if row.get("candidate_imported") is True
            and row.get("guard_installed_before_candidate_import") is True
        ) == 1
        and value["failed_suites"]
        == [row["suite"] for row in rows if row["status"] == "FAIL"]
        and value["infrastructure_failure_suites"]
        == [row["suite"] for row in infrastructure],
        "derive clean, differing, failed, proven-import, and unknown Zig results",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and len(archive) == 8
        and archive["bytes"] == 5006573
        and archive["device"] == 2064
        and archive["inode"] == 525390
        and archive["mode"] == 0o600
        and archive["nlink"] == 1
        and archive["uid"] == os.geteuid()
        and archive["sha256"]
        == "d32590e3a718be024c8016c741ca12321f66f8cc545bc3d1321286d4f3fe6ba4"
        and archive["name"].endswith(".json.gz"),
        "preserve archive metadata exclusively from the public plaintext receipt",
    )
    return {
        "family": "zig",
        "display_name": "Zig",
        "actual_candidate_worker_count": 13,
        "unique_candidate_worker_count": 13,
        "attempted_suite_count": 13,
        "clean_suite_count": 6,
        "completed_suite_count": 9,
        "mismatch_suite_count": 3,
        "infrastructure_failure_count": 4,
        "verified_passing_case_count": 3583,
        "observed_semantic_mismatch_lower_bound": 1540,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "individually_proven_guarded_candidate_import_count": 10,
        "candidate_import_status_unknown_count": 3,
        "infrastructure_failure_with_individually_proven_guarded_import_count": 1,
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": ZIG_SOURCE["source"][1],
        "protocol_sha256": ZIG_SOURCE["protocol"][1],
        "contract_sha256": ZIG_SOURCE["contract"][1],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["bytes"],
        "archive_opened_by_graph": False,
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
    }


def load_zig_evidence(base: types.ModuleType) -> tuple[dict, dict, dict]:
    raws = {
        role: read_fixed(item, "whole first-party Zig V10 " + role)
        for role, item in ZIG_SOURCE.items()
    }
    contract = base.document(raws["contract"], "whole first-party Zig V10 contract")
    base.need(
        base.canonical(contract) == raws["contract"],
        "reject incomplete or noncanonical first-party Zig V10 source contract",
    )
    validate_source_contract(base, contract)
    receipt_raw = read_fixed(ZIG_RECEIPT, "whole actual first-party Zig V10 receipt")
    receipt = base.document(receipt_raw, "whole actual first-party Zig V10 receipt")
    base.need(
        base.canonical(receipt) == receipt_raw,
        "reject incomplete or noncanonical Zig V10 public receipt",
    )
    facts = validate_zig_receipt(base, receipt)
    return contract, receipt, facts


def compact_suite_proof(base: types.ModuleType, row: dict) -> dict:
    raw = base.canonical(row)
    return {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_public_suite_row_sha256": base.digest(raw),
        "complete_public_suite_row_canonical_bytes": len(raw),
        "status": row["status"],
        "infrastructure_failure": row["infrastructure_failure"],
        "observed_semantic_mismatch_count": row[
            "observed_semantic_mismatch_count"
        ],
        "candidate_imported": row.get("candidate_imported"),
        "guard_installed_before_candidate_import": row.get(
            "guard_installed_before_candidate_import"
        ),
        "timed_out": row["timed_out"],
    }


def make_evidence_pool(
    base: types.ModuleType,
    contract: dict,
    receipt: dict,
    facts: dict,
) -> dict:
    entry = {
        "schema": ENTRY_SCHEMA,
        "family": "zig",
        "complete_plaintext_receipt_owner": base.synthetic_owner(
            ZIG_RECEIPT[:3], ZIG_RECEIPT[3]
        ),
        "complete_plaintext_receipt_sha256": ZIG_RECEIPT[1],
        "complete_plaintext_receipt_bytes": ZIG_RECEIPT[2],
        "complete_plaintext_receipt_field_count": 42,
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt": copy.deepcopy(receipt),
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in ZIG_SOURCE.items()
        },
        "complete_source_contract_embedded": True,
        "complete_source_contract": copy.deepcopy(contract),
        "complete_original_suite_count": 13,
        "complete_original_suite_rows": [
            compact_suite_proof(base, row)
            for row in receipt["original_suite_diagnostics"]
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
        "entries": {ZIG_RECEIPT[1]: entry},
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
            "schema",
            "version",
            "hash_algorithm",
            "complete_public_receipt_count",
            "complete_first_party_source_owner_count",
            "entries",
        }
        and pool["schema"] == POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and pool["complete_public_receipt_count"] == 1
        and pool["complete_first_party_source_owner_count"] == 3
        and type(pool["entries"]) is dict
        and set(pool["entries"]) == {ZIG_RECEIPT[1]},
        "require the one complete digest-addressed actual Zig V10 receipt",
    )
    assert isinstance(pool, dict)
    entry = pool["entries"][ZIG_RECEIPT[1]]
    base.need(
        type(entry) is dict
        and entry["schema"] == ENTRY_SCHEMA
        and entry["family"] == "zig"
        and base.canonical(entry["complete_plaintext_receipt_owner"])
        == base.canonical(base.synthetic_owner(ZIG_RECEIPT[:3], ZIG_RECEIPT[3]))
        and entry["complete_plaintext_receipt_sha256"] == ZIG_RECEIPT[1]
        and entry["complete_plaintext_receipt_bytes"] == ZIG_RECEIPT[2]
        and entry["complete_plaintext_receipt_field_count"] == 42
        and entry["complete_plaintext_receipt_embedded"] is True
        and base.canonical(entry["complete_plaintext_receipt"])
        == base.canonical(receipt)
        and entry["complete_first_party_source_owner_count"] == 3
        and entry["complete_source_contract_embedded"] is True
        and base.canonical(entry["complete_source_contract"])
        == base.canonical(contract)
        and entry["complete_original_suite_count"] == 13
        and base.canonical(entry["complete_original_suite_rows"])
        == base.canonical([
            compact_suite_proof(base, row)
            for row in receipt["original_suite_diagnostics"]
        ])
        and base.canonical(entry["validated_campaign_outcome"])
        == base.canonical(facts)
        and entry["compressed_archive_opened_by_graph"] is False
        and entry["private_build_root_opened_by_graph"] is False
        and entry["complete_failure_diagnostics_available_without_archive"] is True,
        "reject omitted, changed, partial, or invented complete Zig V10 evidence",
    )
    owners = entry["complete_first_party_source_owners"]
    base.need(
        type(owners) is dict and set(owners) == set(ZIG_SOURCE),
        "preserve exactly three independently authenticated Zig source owners",
    )
    for role, item in ZIG_SOURCE.items():
        base.need(
            base.canonical(owners[role])
            == base.canonical(base.synthetic_owner(item[:3], item[3])),
            "preserve every actual whole first-party Zig " + role + " owner",
        )


def make_reference(base: types.ModuleType, pool: dict) -> dict:
    entry = pool["entries"][ZIG_RECEIPT[1]]
    raw = base.canonical(entry)
    return {
        "schema": REFERENCE_SCHEMA,
        "family": "zig",
        "complete_plaintext_receipt_sha256": ZIG_RECEIPT[1],
        "complete_plaintext_receipt_bytes": ZIG_RECEIPT[2],
        "complete_first_party_source_owner_count": 3,
        "complete_reference_sha256": base.digest(raw),
        "complete_reference_canonical_bytes": len(raw),
    }


def resolve_reference(
    base: types.ModuleType,
    pool: dict,
    reference: object,
) -> dict:
    base.need(
        type(reference) is dict
        and set(reference) == {
            "schema",
            "family",
            "complete_plaintext_receipt_sha256",
            "complete_plaintext_receipt_bytes",
            "complete_first_party_source_owner_count",
            "complete_reference_sha256",
            "complete_reference_canonical_bytes",
        }
        and reference["schema"] == REFERENCE_SCHEMA
        and reference["family"] == "zig"
        and reference["complete_plaintext_receipt_sha256"] == ZIG_RECEIPT[1]
        and reference["complete_plaintext_receipt_bytes"] == ZIG_RECEIPT[2]
        and reference["complete_first_party_source_owner_count"] == 3,
        "reject an omitted, truncated, or substituted actual Zig V10 reference",
    )
    assert isinstance(reference, dict)
    entry = pool["entries"].get(ZIG_RECEIPT[1])
    base.need(
        type(entry) is dict
        and base.checked(reference["complete_reference_sha256"], "Zig V10 proof")
        == base.digest(base.canonical(entry))
        and reference["complete_reference_canonical_bytes"]
        == len(base.canonical(entry)),
        "reject changed complete first-party Zig V10 proof",
    )
    return copy.deepcopy(entry)


def make_changes(old: dict, facts: dict, reference: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 89,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v90_new_directly_authenticated_owner_count": 4,
        "v90_new_directly_authenticated_zig_source_owner_count": 3,
        "v90_new_directly_authenticated_zig_plaintext_receipt_owner_count": 1,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v7_original_campaign_clean_suite_count": 2,
        "c_v7_original_campaign_completed_suite_count": 5,
        "c_v7_original_campaign_verified_passing_case_count": 13094,
        "c_v7_original_campaign_observed_mismatch_lower_bound": 236,
        "c_v7_original_campaign_candidate_execution_failure_count": 7,
        "c_v7_original_campaign_infrastructure_failure_count": 1,
        "c_v7_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v7_original_campaign_candidate_status": "FAIL",
        "rust_v19_original_campaign_clean_suite_count": 6,
        "rust_v19_original_campaign_completed_suite_count": 8,
        "rust_v19_original_campaign_verified_passing_case_count": 12942,
        "rust_v19_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v19_original_campaign_infrastructure_failure_count": 5,
        "rust_v19_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v19_original_campaign_candidate_status": "FAIL",
        "zig_v9_original_campaign_clean_suite_count": 3,
        "zig_v9_original_campaign_completed_suite_count": 3,
        "zig_v9_original_campaign_verified_passing_case_count": 927,
        "zig_v9_original_campaign_infrastructure_failure_count": 10,
        "zig_v9_original_campaign_observed_mismatch_lower_bound": 0,
        "zig_v9_original_campaign_individually_proven_guarded_import_count": 7,
        "zig_v9_original_campaign_unknown_guarded_import_count": 6,
        "zig_v9_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v9_original_campaign_candidate_status": "FAIL",
        "zig_v10_original_campaign_actual_worker_count": 13,
        "zig_v10_original_campaign_unique_worker_count": 13,
        "zig_v10_original_campaign_attempted_suite_count": 13,
        "zig_v10_original_campaign_clean_suite_count": 6,
        "zig_v10_original_campaign_completed_suite_count": 9,
        "zig_v10_original_campaign_mismatch_suite_count": 3,
        "zig_v10_original_campaign_verified_passing_case_count": 3583,
        "zig_v10_original_campaign_observed_mismatch_lower_bound": 1540,
        "zig_v10_original_campaign_infrastructure_failure_count": 4,
        "zig_v10_original_campaign_individually_proven_guarded_import_count": 10,
        "zig_v10_original_campaign_unknown_guarded_import_count": 3,
        "zig_v10_original_campaign_infrastructure_failure_with_guarded_import_count":
        1,
        "zig_v10_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v10_original_campaign_candidate_status": "FAIL",
        "zig_v10_original_campaign_candidate_qualified": False,
        "zig_v10_original_campaign_archive_opened_by_graph": False,
        "current_aggregate_semantic_mismatch_counts": "NOT MEASURED",
        "historical_original_rust_semantic_mismatch_count": 1440,
        "historical_original_rust_verified_passing_case_count": 14853,
        "historical_original_c_semantic_mismatch_count": 1230,
        "historical_original_c_verified_passing_case_count": 7325,
        "historical_original_zig_semantic_mismatch_count": 1764,
        "rust_captured_v21_actual_build_status": "PASS",
        "rust_captured_v21_actual_compiler_process_count": 28,
        "c_subject_v18_actual_build_status": "PASS",
        "c_subject_v18_actual_compiler_process_count": 14,
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
            "C",
            13094,
            "2 clean · 3 differ · 7 errors · 1 infrastructure failure",
            "NOT COMPATIBLE",
            "#fbbf24",
        ),
        (
            "Rust",
            12942,
            "6 clean · 2 differ · 5 infrastructure failures",
            "NOT COMPATIBLE",
            "#fbbf24",
        ),
        (
            "Zig",
            3583,
            "6 clean · 3 differ · 4 infrastructure failures",
            "NOT COMPATIBLE",
            "#fbbf24",
        ),
        (
            "C++",
            None,
            "Historical differences; current complete result not measured",
            "NOT COMPATIBLE",
            "#fb7185",
        ),
        (
            "Go",
            None,
            "Historical differences; current complete result not measured",
            "NOT COMPATIBLE",
            "#fb7185",
        ),
        (
            "Fortran",
            None,
            "Two builds disagreed; compatibility not measured",
            "BUILD FAILED",
            "#fb7185",
        ),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="970" '
        'viewBox="0 0 1440 970" role="img" aria-labelledby="title description">',
        '<title id="title">Progress toward a faster, fully compatible Python re</title>',
        '<desc id="description">Six independent first-party engines are compared '
        'against unchanged Python 3.14.6. The original compatibility test '
        'contains 31,237 checks in 13 groups. A separate set of 8,244 '
        'differential checks is not included in that denominator. C has 13,094 '
        'verified checks from two clean groups, three differing groups containing '
        'at least 236 observed differences, seven candidate execution failures, '
        'and one infrastructure failure. Rust has 12,942 verified checks from '
        'six clean groups, two differing groups containing at least 1,296 observed '
        'differences, and five infrastructure failures. The latest Zig run has '
        '3,583 verified checks from six clean groups, three differing groups '
        'containing at least 1,540 observed differences, and four infrastructure '
        'failures. Ten Zig worker imports are individually proven guarded and '
        'three remain genuinely unknown; one infrastructure failure occurred '
        'after a proven guarded import. The complete mismatch totals for all '
        'three latest runs are not measured. The previous Zig run and C++, Go, '
        'and Fortran are preserved. No engine is fully compatible, no speed or '
        'memory has been measured, and the proposed 14,155,776-case final '
        'comparison is not frozen, generated, opened, or run.</desc>',
        '<rect width="1440" height="970" rx="22" fill="#0b1220"/>',
        '<text x="44" y="60" fill="#f8fafc" font-size="31" '
        'font-family="system-ui,sans-serif" font-weight="730">'
        'Building a faster Python re, from scratch</text>',
        '<text x="44" y="97" fill="#cbd5e1" font-size="17" '
        'font-family="system-ui,sans-serif">6 independent engines · '
        '0 fully compatible · speed NOT MEASURED</text>',
        '<rect x="44" y="119" width="1352" height="57" rx="11" '
        'fill="#172338"/>',
        '<text x="62" y="144" fill="#f8fafc" font-size="15" '
        'font-family="system-ui,sans-serif" font-weight="650">'
        'What the bars mean: checks actually confirmed against Python, '
        'out of 31,237.</text>',
        '<text x="62" y="165" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">Unfinished checks are unknown, '
        'not passes. The separate 8,244-check test is not counted.</text>',
        '<text x="45" y="211" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="650">ENGINE</text>',
        '<text x="161" y="211" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="650">'
        'CONFIRMED ORIGINAL CHECKS</text>',
        '<text x="724" y="211" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="650">'
        'WHAT ACTUALLY HAPPENED</text>',
        '<text x="1386" y="211" text-anchor="end" fill="#94a3b8" '
        'font-size="12" font-family="system-ui,sans-serif" '
        'font-weight="650">RESULT</text>',
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
        '<text x="48" y="709" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="670">'
        'Compatibility, not just a successful build</text>',
        '<text x="48" y="738" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">C completed 5 of 13 groups; '
        'Rust completed 8 of 13; Zig completed 9 of 13.</text>',
        '<text x="48" y="761" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">Observed differences: '
        'C at least 236; Rust at least 1,296; Zig at least 1,540. '
        'Complete totals: NOT MEASURED.</text>',
        '<text x="48" y="784" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">Zig: 10 worker imports '
        'individually proven; 3 unknown. Four test groups remain incomplete.</text>',
        '<text x="48" y="807" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">A published test report or '
        'successful native build does not mean an engine passed.</text>',
        '<rect x="44" y="830" width="1352" height="91" rx="12" '
        'fill="#172338"/>',
        '<text x="62" y="858" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="670">'
        'Proposed final speed comparison: 14,155,776 cases</text>',
        '<text x="62" y="882" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">Not frozen, not generated, '
        'not opened, and not run. Speed, memory, confidence, and rankings: '
        'NOT MEASURED.</text>',
        '<text x="62" y="905" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">The earlier 4,194,304-case '
        'proposal and previous Zig results remain preserved; '
        'no winner has been selected.</text>',
        '<text x="48" y="951" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif">Overview 90 · '
        'all previous evidence preserved · no external regex wrapper · '
        'no fully compatible replacement.</text>',
        "</svg>",
        "",
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
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain Python and exactly six independently implemented engine families",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row["family"] == family,
            "reject a missing, invented, or substituted engine: " + family,
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
            "reject invented compatibility, independence, or speed for " + family,
        )
        restored = copy.deepcopy(row)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if family == "zig":
            proof = resolve_reference(base, pool, row.get(LATEST_KEY))
            base.need(
                base.canonical(proof["validated_campaign_outcome"])
                == base.canonical(facts)
                and base.canonical(row["v90_latest_original_campaign"])
                == base.canonical(facts)
                and base.canonical(row[LATEST_KEY]) == base.canonical(reference)
                and base.canonical(row["v89_latest_original_campaign"])
                == base.canonical(original["v89_latest_original_campaign"]),
                "preserve both the latest measured and complete historical Zig run",
            )
            restored.pop(LATEST_KEY)
            restored.pop("v90_latest_original_campaign")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore every byte of the published V89 engine: " + family,
        )


def build(
    previous: types.ModuleType,
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
        "caller-pin the whole immutable V90 renderer source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole immutable V90 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V89.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the complete committed V89 " + role,
        )
    for role, item in ZIG_SOURCE.items():
        base.need(
            getattr(options, "zig_" + role + "_sha256") == item[1],
            "caller-pin the complete first-party Zig V10 " + role,
        )
    base.need(
        options.zig_receipt_sha256 == ZIG_RECEIPT[1],
        "caller-pin the complete actual Zig V10 public plaintext receipt",
    )
    old, _ = authenticate_previous(
        previous,
        v88,
        v87,
        v86,
        v85,
        v84,
        v83,
        v82,
        chain,
        base,
    )
    contract, receipt, facts = load_zig_evidence(base)
    pool = make_evidence_pool(base, contract, receipt, facts)
    reference = make_reference(base, pool)
    changes = make_changes(old, facts, reference)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V89.items()
    }
    snapshot = {
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 90,
        "previous_complete_snapshot_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_overview_sha256": V89["summary"][1],
        "previous_complete_overview_bytes": V89["summary"][2],
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
            "zig": 3583,
            "cpp": "NOT MEASURED",
            "go": "NOT MEASURED",
            "fortran": "NOT MEASURED",
        },
        "latest_complete_candidate_mismatch_totals": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "proposed_final_comparison_case_count": HOLDOUT_PROPOSAL_COUNT,
        "proposed_final_comparison_status":
        "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "winner_selected": False,
    }
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 90,
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
        if family == "zig":
            row[LATEST_KEY] = copy.deepcopy(reference)
            row["v90_latest_original_campaign"] = copy.deepcopy(facts)
    validate_families(base, old, families, pool, reference, facts)
    latest_campaigns = copy.deepcopy(old["latest_original_campaigns"])
    latest_campaigns["zig"] = copy.deepcopy(facts)
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = {
        "schema": SCHEMA + "-summary",
        "version": 90,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v89_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v89_snapshot_canonical_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_v89_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "previous_v88_snapshot": copy.deepcopy(old["previous_v88_snapshot"]),
        "previous_v88_snapshot_canonical_sha256": old[
            "previous_v88_snapshot_canonical_sha256"
        ],
        "previous_v88_snapshot_canonical_bytes": old[
            "previous_v88_snapshot_canonical_bytes"
        ],
        "lossless_v89_snapshot_identity_status": "PASS",
        "lossless_v89_family_identity_status": "PASS",
        "lossless_v89_all_eleven_previous_pool_identity_status": "PASS",
        "lossless_v89_original_campaign_receipt_reference_pool_entry_count": 3,
        "lossless_v89_complete_original_suite_reference_count": 39,
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v90_zig_v10_complete_plaintext_receipt_count": 1,
        "lossless_v90_zig_v10_complete_source_owner_count": 3,
        "lossless_v90_zig_v10_complete_original_suite_count": 13,
        "previous_v89_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": latest_campaigns,
        **{key: copy.deepcopy(old[key]) for key, _, _, _ in OLD_POOLS},
        **copy.deepcopy(changes),
    }
    for key, size, digest, count in OLD_POOLS:
        raw = base.canonical(summary[key])
        base.need(
            len(raw) == size
            and base.digest(raw) == digest
            and base.canonical(summary[key]) == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "preserve the exact complete V89 proof pool in V90: " + key,
        )
    historical = summary["previous_v88_snapshot"]
    base.need(
        base.canonical(summary["previous_v89_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(historical)
        == base.canonical(old["previous_v88_snapshot"])
        and base.canonical(families[0]) == base.canonical(old["families"][0])
        and summary["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
        and summary["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
        and historical["actual_rust_semantic_mismatch_count"] == 1440
        and historical["actual_rust_verified_passing_case_count"] == 14853
        and historical["actual_c_semantic_mismatch_count"] == 1230
        and historical["actual_c_verified_passing_case_count"] == 7325
        and historical["actual_zig_semantic_mismatch_count"] == 1764
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False
        and summary["winner_selected"] is False,
        "preserve baseline, all history, unread holdout and absence of a winner",
    )
    validate_evidence_pool(base, summary[POOL_KEY], contract, receipt, facts)
    recovered = resolve_reference(base, pool, reference)
    base.need(
        base.canonical(recovered["validated_campaign_outcome"])
        == base.canonical(facts)
        and base.canonical(recovered["complete_plaintext_receipt"])
        == base.canonical(receipt)
        and base.canonical(recovered["complete_source_contract"])
        == base.canonical(contract)
        and base.canonical(summary[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(snapshot[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(inputs[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(summary["latest_original_campaigns"]["zig"])
        == base.canonical(facts)
        and base.canonical(summary["previous_v89_latest_original_campaigns"])
        == base.canonical(old["latest_original_campaigns"]),
        "preserve every complete current Zig result and every historical campaign",
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
            "reject an oversized whole V90 output before publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
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
        v88,
        v87,
        v86,
        v85,
        v84,
        v83,
        v82,
        chain,
        base,
        previous_options(previous),
    )
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 89
        and prior["rejected_hostile_control_count"] == 9957
        and prior["authenticated_evidence_owner_lower_bound"] == 312
        and prior["authenticated_history_reference_lower_bound"] == 317
        and prior["lossless_previous_v88_proof_pool_count"] == 10
        and prior["lossless_v88_all_ten_previous_pool_identity_status"] == "PASS"
        and prior["lossless_v89_original_campaign_receipt_reference_pool_entry_count"]
        == 3
        and prior["lossless_v89_complete_original_suite_reference_count"] == 39
        and prior["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and prior["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and prior["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and prior["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and prior["qualified_candidate_count"] == 0
        and prior["performance"] == "NOT MEASURED"
        and prior["outputs_written"] is False,
        "preserve all 9,957 historical hostile controls and complete V89 evidence",
    )
    _, assets = build(
        previous,
        v88,
        v87,
        v86,
        v85,
        v84,
        v83,
        v82,
        chain,
        base,
        options,
    )
    summary = base.document(assets[SUMMARY_PATH], "whole in-memory V90 summary")
    contract, receipt, facts = load_zig_evidence(base)
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
            base.need(False, "V90 accepted fabricated source evidence: " + label)

    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        reject(
            "omitted complete Zig V10 source contract field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-source-contract"),
        ("version", 9),
        ("family", "external-regex"),
        ("status", "PASS"),
        ("qualified_candidate_count", 1),
        ("current_qualified_candidates", 1),
        ("runtime_non_delegation", "PASS"),
        ("holdout", "OPENED"),
        ("holdout_case_count", CASE_COUNT),
        ("historical_holdout_case_count", HOLDOUT_PROPOSAL_COUNT),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = wrong
        reject(
            "invented Zig V10 source outcome: " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key in sorted(receipt):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        reject(
            "omitted complete Zig V10 public receipt field " + key,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-public-receipt"),
        ("status", "FAIL"),
        ("publication_pass_means", "CANDIDATE QUALIFIED"),
        ("family", "external-regex"),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("actual_candidate_workers", 12),
        ("unique_candidate_worker_count", 12),
        ("suite_count", 12),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", CASE_COUNT),
        ("infrastructure_failure_count", 0),
        ("observed_semantic_mismatch_lower_bound", 0),
        ("semantic_mismatch_count", 1540),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("original_campaign_passed", True),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("hidden_cases_read", 1),
        ("timing_trials_run", 1),
        ("benchmark_files_read", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("supplemental_candidate_matching", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = wrong
        reject(
            "invented Zig V10 measured outcome: " + key,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for index, (suite, _) in enumerate(SUITES):
        for key, wrong in (
            ("suite", "invented-original-suite"),
            ("case_execution_denominator", CASE_COUNT),
            ("timed_out", True),
        ):
            forged = copy.deepcopy(receipt)
            forged["original_suite_diagnostics"][index][key] = wrong
            reject(
                "changed complete Zig V10 suite " + suite + ": " + key,
                lambda value=forged: validate_zig_receipt(base, value),
            )
    for index, row in enumerate(receipt["original_suite_diagnostics"]):
        for key, wrong in (
            ("candidate_imported", not row.get("candidate_imported")),
            (
                "guard_installed_before_candidate_import",
                not row.get("guard_installed_before_candidate_import"),
            ),
            ("infrastructure_failure", not row["infrastructure_failure"]),
        ):
            forged = copy.deepcopy(receipt)
            forged["original_suite_diagnostics"][index][key] = wrong
            reject(
                "changed guarded Zig V10 suite evidence "
                + row["suite"]
                + ": "
                + key,
                lambda value=forged: validate_zig_receipt(base, value),
            )
    for key, wrong in (
        ("schema", "fabricated-reference"),
        ("family", "borrowed-engine"),
        ("complete_plaintext_receipt_sha256", "0" * 64),
        ("complete_plaintext_receipt_bytes", 1),
        ("complete_first_party_source_owner_count", 2),
        ("complete_reference_sha256", "0" * 64),
        ("complete_reference_canonical_bytes", 1),
    ):
        forged = copy.deepcopy(reference)
        forged[key] = wrong
        reject(
            "fabricated complete Zig V10 evidence reference: " + key,
            lambda value=forged: resolve_reference(base, pool, value),
        )
    for key in sorted(pool):
        forged = copy.deepcopy(pool)
        forged.pop(key)
        reject(
            "omitted complete Zig V10 evidence pool field " + key,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    genuine_entry = pool["entries"][ZIG_RECEIPT[1]]
    for key in sorted(genuine_entry):
        forged = copy.deepcopy(pool)
        forged["entries"][ZIG_RECEIPT[1]].pop(key)
        reject(
            "omitted complete Zig V10 proof entry field " + key,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    for role in ZIG_SOURCE:
        forged = copy.deepcopy(pool)
        forged["entries"][ZIG_RECEIPT[1]][
            "complete_first_party_source_owners"
        ].pop(role)
        reject(
            "omitted complete first-party Zig V10 owner " + role,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    old, _ = authenticate_previous(
        previous,
        v88,
        v87,
        v86,
        v85,
        v84,
        v83,
        v82,
        chain,
        base,
    )
    for index, row in enumerate(summary["families"]):
        if row["family"] == "python":
            forged = copy.deepcopy(summary["families"])
            forged[index]["correctness"] = "INVENTED"
            reject(
                "changed unchanged Python baseline",
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
                "invented compatible or faster " + row["family"] + ": " + key,
                lambda value=forged: validate_families(
                    base, old, value, pool, reference, facts
                ),
            )
    for event, arguments in (
        ("open", (str(ROOT / "hidden.gz"), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / INPUT_PATH), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / SVG_PATH), "rb", os.O_RDONLY)),
        ("open", ("/tmp/rebar-private-root", "rb", os.O_RDONLY)),
        (
            "open",
            (str(ROOT / "safe.json"), "wb", os.O_WRONLY | os.O_CREAT),
        ),
        ("subprocess.Popen", ("candidate",)),
        ("ctypes.dlopen", ("external-regex.so",)),
        ("socket.connect", ("example.invalid",)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
    ):
        reject(
            "forbidden V90 source-only side effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    base.need(
        rejected >= 245,
        "require complete independent Zig V10 source, receipt, and suite controls",
    )
    return result_payload(
        base,
        options,
        assets,
        False,
        {
            "schema": SCHEMA + "-source-only-self-test",
            "inherited_rejected_hostile_control_count": prior[
                "rejected_hostile_control_count"
            ],
            "new_rejected_hostile_control_count": rejected,
            "rejected_hostile_control_count": prior[
                "rejected_hostile_control_count"
            ] + rejected,
        },
    )


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
        "version": 90,
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
        "v90_new_directly_authenticated_owner_count": 4,
        "v90_new_directly_authenticated_zig_source_owner_count": 3,
        "v90_new_directly_authenticated_zig_plaintext_receipt_owner_count": 1,
        "lossless_previous_v89_proof_pool_count": len(OLD_POOLS),
        "lossless_v89_all_eleven_previous_pool_identity_status": "PASS",
        "lossless_v89_snapshot_identity_status": "PASS",
        "lossless_v89_family_identity_status": "PASS",
        "lossless_v89_original_campaign_receipt_reference_pool_entry_count": 3,
        "lossless_v89_complete_original_suite_reference_count": 39,
        "lossless_v90_zig_v10_complete_plaintext_receipt_count": 1,
        "lossless_v90_zig_v10_complete_source_owner_count": 3,
        "lossless_v90_zig_v10_complete_original_suite_count": 13,
        "original_case_execution_denominator": CASE_COUNT,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v7_original_campaign_completed_suite_count": 5,
        "c_v7_original_campaign_verified_passing_case_count": 13094,
        "c_v7_original_campaign_observed_mismatch_lower_bound": 236,
        "rust_v19_original_campaign_completed_suite_count": 8,
        "rust_v19_original_campaign_verified_passing_case_count": 12942,
        "rust_v19_original_campaign_observed_mismatch_lower_bound": 1296,
        "zig_v9_original_campaign_completed_suite_count": 3,
        "zig_v9_original_campaign_verified_passing_case_count": 927,
        "zig_v9_original_campaign_infrastructure_failure_count": 10,
        "zig_v9_original_campaign_individually_proven_guarded_import_count": 7,
        "zig_v9_original_campaign_unknown_guarded_import_count": 6,
        "zig_v10_original_campaign_actual_worker_count": 13,
        "zig_v10_original_campaign_clean_suite_count": 6,
        "zig_v10_original_campaign_completed_suite_count": 9,
        "zig_v10_original_campaign_mismatch_suite_count": 3,
        "zig_v10_original_campaign_verified_passing_case_count": 3583,
        "zig_v10_original_campaign_observed_mismatch_lower_bound": 1540,
        "zig_v10_original_campaign_infrastructure_failure_count": 4,
        "zig_v10_original_campaign_individually_proven_guarded_import_count": 10,
        "zig_v10_original_campaign_unknown_guarded_import_count": 3,
        "zig_v10_original_campaign_infrastructure_failure_with_guarded_import_count":
        1,
        "zig_v10_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "historical_original_rust_semantic_mismatch_count": 1440,
        "historical_original_rust_verified_passing_case_count": 14853,
        "historical_original_c_semantic_mismatch_count": 1230,
        "historical_original_c_verified_passing_case_count": 7325,
        "historical_original_zig_semantic_mismatch_count": 1764,
        "rust_captured_v21_actual_build_status": "PASS",
        "rust_captured_v21_actual_compiler_process_count": 28,
        "c_subject_v18_actual_build_status": "PASS",
        "c_subject_v18_actual_compiler_process_count": 14,
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
        "publish only one authorized, new and bounded V90 evidence owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "publish complete V90 bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate the complete, exclusive published V90 owner",
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
    base.need(actual == raw, "reauthenticate every byte of final V90 evidence")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V89:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in ZIG_SOURCE:
        parser.add_argument("--zig-" + role + "-sha256", required=True)
    parser.add_argument("--zig-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, v88, v87, v86, v85, v84, v83, v82, chain, base = load_previous()
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(
                previous,
                v88,
                v87,
                v86,
                v85,
                v84,
                v83,
                v82,
                chain,
                base,
                options,
            )
        else:
            _, assets = build(
                previous,
                v88,
                v87,
                v86,
                v85,
                v84,
                v83,
                v82,
                chain,
                base,
                options,
            )
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V90 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
