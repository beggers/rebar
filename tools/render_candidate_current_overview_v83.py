#!/usr/bin/env python3
"""Freeze a precise Rust repair without losing a single historical result."""

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
SELF = "tools/render_candidate_current_overview_v83.py"
OUTPUT = "docs/evidence/candidate-current-overview-v83"
SCHEMA = "rebar-candidate-current-overview-v83"
POOL_SCHEMA = SCHEMA + "-lossless-complete-family-proof-pool-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-family-proof-reference-v1"
CONTRACT_SCHEMA = (
    "rebar-owned-repaired-rust-original-campaign-v15-"
    "recoverable-source-freeze"
)
EXPECTED_GOAL = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
V82 = {
    "source": (
        "tools/render_candidate_current_overview_v82.py",
        "9c6bfd10a8a1663e4490f3b0a34acff6b0c90b92c6d39a34b35a20cf102f3b75",
        63759,
        431583,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v82.inputs.json",
        "5d589797ecb24fc7de7aa4fdbe67c28196309c53d4e3dce26a0fd7e08055e507",
        1269829,
        431584,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v82.json",
        "2a43659f9c2d8df3c25e7cd536abf8f9181513642bd05e456352ed6e87ee0212",
        4167573,
        431585,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v82.svg",
        "89cfda78296840200fb4e55bcd04dc45f1966456ad2991d339bb9b997c8c5c51",
        5500,
        431586,
    ),
}
FEATURE = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v15.py",
        "4fae63c422ba57770a7dc3b514828eef2e714b83f4f27899450eafa45ab3e9cf",
        119006,
        431608,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V15.md",
        "0c3de861493026b9a2e09713c39dd5018d320c06956006f0568babf61a8bdb24",
        11921,
        525100,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v15.json",
        "ef01910b0ac165965631a9349f0fffa94c7881145f37d705f3f494bcd6ce5d6b",
        13079,
        525101,
    ),
}
HISTORICAL_PROOF_KEYS = (
    "clean_original_producer_v5_source_freeze",
    "candidate_runtime_independence_v2_source_freeze",
    "rust_v12_original_campaign_source_freeze",
    "actual_rust_v12_original_campaign",
    "rust_v13_original_campaign_source_freeze",
    "actual_rust_v13_original_campaign",
    "rust_v14_original_campaign_source_freeze",
    "actual_rust_v14_original_campaign",
)
V15_PROOF_KEY = "rust_v15_original_campaign_source_freeze"
PROOF_KEYS = HISTORICAL_PROOF_KEYS + (V15_PROOF_KEY,)
V15_ADDITIONAL_CONTRACT_KEYS = frozenset({
    "native_stage_mode_active_native_mode",
    "native_stage_mode_controller_route",
    "native_stage_mode_guarded_worker_route",
    "native_stage_mode_native_owners_opened",
    "native_stage_mode_patch_site_count",
    "native_stage_mode_patch_sites",
    "native_stage_mode_preserved_original_native_mode",
    "native_stage_mode_recovery_route",
    "native_stage_mode_repair_status",
    "native_stage_mode_source_sha256",
    "native_stage_mode_target_roles",
    "native_stage_mode_transformations_executed",
    "previous_v14_contract_sha256",
    "previous_v14_protocol_sha256",
    "previous_v14_source_sha256",
    "v14_actual_all_four_original_targets_restored",
    "v14_actual_candidate_qualified",
    "v14_actual_candidate_worker_count",
    "v14_actual_completed_suite_count",
    "v14_actual_failure_receipt_bytes",
    "v14_actual_failure_receipt_inode",
    "v14_actual_failure_receipt_sha256",
    "v14_actual_first_child_returncode",
    "v14_actual_first_child_stderr_bytes",
    "v14_actual_first_child_stderr_sha256",
    "v14_actual_infrastructure_failure_count",
    "v14_actual_root_cause",
    "v14_actual_semantic_mismatch_count",
    "v14_actual_verified_passing_case_count",
    "v14_failure_archive_inflated",
    "v14_failure_archive_opened",
    "worker_failure_capture_public_first_full_streams",
    "worker_failure_capture_public_first_full_traceback",
})
PATCH_SITES = (
    ("restoration-promoted-native", "restore_corrected_four_roles", 7936),
    ("activation-native-write-stage", "activate_four_roles", 8132),
    ("activation-promoted-native", "activate_four_roles", 8151),
)


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    """Read one complete, already released owner without following links."""
    relative, expected, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(descriptor)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted complete V83 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V83 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject extended complete V83 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
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
            raise ValueError("reject changed complete V83 owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple[types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V82["source"], "exact pushed V82 graph renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v82")
    previous.__file__ = str(ROOT / V82["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    chain = previous.load_previous()
    base = chain[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v82"
        and previous.SELF == V82["source"][0]
        and len(chain) == 15,
        "require the exact whole committed V82 graph and complete history chain",
    )
    return previous, chain, base


def authenticate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V82["source"][1],
        "source_bytes": V82["source"][2],
        "receipt_sha256": previous.RECEIPT[1],
    }
    for role, item in previous.V81.items():
        pins["previous_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(*chain, argparse.Namespace(**pins))
    for role in ("inputs", "summary", "svg"):
        item = V82[role]
        base.need(
            assets[item[0]] == read_fixed(item, "actual whole V82 " + role),
            "reproduce every byte of the complete committed V82 " + role,
        )
    old = base.document(assets[V82["summary"][0]], "whole pushed V82 summary")
    inputs = base.document(assets[V82["inputs"][0]], "whole pushed V82 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 82
        and inputs["version"] == 82
        and old["actual_current_graph_predecessor_version"] == 81
        and old["authenticated_evidence_owner_lower_bound"] == 267
        and old["authenticated_history_reference_lower_bound"] == 272
        and old["rust_v12_original_campaign_actual_worker_count"] == 13
        and old["rust_v12_original_campaign_completed_suite_count"] == 0
        and old["rust_v12_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v12_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old["rust_v13_original_campaign_actual_worker_count"] == 13
        and old["rust_v13_original_campaign_completed_suite_count"] == 0
        and old["rust_v13_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v13_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old["rust_v14_original_campaign_candidate_matching"] == "FAIL"
        and old["rust_v14_original_campaign_actual_worker_count"] == 13
        and old["rust_v14_original_campaign_completed_suite_count"] == 0
        and old["rust_v14_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v14_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["qualified_candidate_count"] == 0
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "preserve all three real 13-worker losses and the exact V82 diagnosis",
    )
    return old, inputs


def validate_contract(
    base: types.ModuleType,
    previous: types.ModuleType,
    chain: tuple,
    old: dict,
    contract: object,
) -> None:
    v81, v80, v79, v78, v77 = chain[:5]
    expected_keys = v81.CONTRACT_KEYS | V15_ADDITIONAL_CONTRACT_KEYS
    base.need(
        len(expected_keys) == 170
        and len(V15_ADDITIONAL_CONTRACT_KEYS) == 33
        and type(contract) is dict
        and set(contract) == expected_keys,
        "reject missing, extra, substituted, or provisional whole V15 fields",
    )
    assert isinstance(contract, dict)
    base.need(
        contract["schema"] == CONTRACT_SCHEMA
        and contract["version"] == 15
        and contract["status"]
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and contract["source_sha256"] == FEATURE["source"][1]
        and contract["protocol_sha256"] == FEATURE["protocol"][1]
        and contract["goal_sha256"] == EXPECTED_GOAL
        and contract["cpython_version"] == "3.14.6"
        and contract["cpython_executable"] == PYTHON
        and contract["cpython_executable_sha256"] == PYTHON_SHA256,
        "pin the immutable goal, stable Python, and three released V15 owners",
    )
    base.need(
        contract["frozen_graph_version"] == 82
        and all(
            contract["frozen_graph_" + role + "_sha256"] == item[1]
            for role, item in V82.items()
        )
        and contract["current_evidence_owner_lower_bound"] == 267
        and contract["current_history_reference_lower_bound"] == 272
        and contract["prospective_evidence_owner_lower_bound"] == 270
        and contract["prospective_history_reference_lower_bound"] == 275,
        "pin every whole V82 owner and exactly three new V15 source owners",
    )
    base.need(
        contract["corrected_original_producer_version"] == 5
        and all(
            contract["corrected_original_producer_" + role + "_sha256"]
            == item[1]
            for role, item in v77.PRODUCER.items()
        )
        and all(
            contract["runtime_guard_" + role + "_sha256"] == item[1]
            for role, item in v77.GUARD.items()
        )
        and contract["runtime_guard_installation"]
        == "REQUIRED BEFORE ANY ACTUAL CANDIDATE IMPORT",
        "retain the original oracle and the byte-identical fail-closed guard",
    )
    suites = contract["suites"]
    base.need(
        contract["suite_count"] == 13
        and contract["case_execution_denominator"] == 31237
        and contract["planned_actual_original_candidate_worker_count"] == 13
        and contract["private_waiver_count"] == 13
        and type(contract["named_private_waivers"]) is list
        and len(contract["named_private_waivers"]) == 13
        and contract["supplemental_case_count"] == 8244
        and contract["supplemental_cases_counted_in_original_denominator"]
        is False
        and type(suites) is list
        and len(suites) == 13
        and [
            (
                row.get("suite", row.get("name", row.get("id"))),
                row.get("case_count", row.get("case_execution_count")),
            )
            for row in suites
        ] == list(v77.SUITES),
        "preserve all 31,237 original checks, all 13 suites, and 8,244 extras",
    )
    base.need(
        contract["native_stage_mode_repair_status"]
        == "SOURCE FROZEN; AUTHENTICATED V7 STAGE REPAIR NOT RUN"
        and contract["native_stage_mode_source_sha256"]
        == "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104"
        and contract["native_stage_mode_target_roles"] == ["engine", "bridge"]
        and contract["native_stage_mode_active_native_mode"] == 0o600
        and contract["native_stage_mode_preserved_original_native_mode"] == 0o755
        and contract["native_stage_mode_patch_site_count"] == 3
        and type(contract["native_stage_mode_patch_sites"]) is list
        and len(contract["native_stage_mode_patch_sites"]) == 3,
        "require exactly three native-only repair sites and unchanged recovery",
    )
    for actual, (description, function, line) in zip(
        contract["native_stage_mode_patch_sites"], PATCH_SITES, strict=True
    ):
        base.need(
            type(actual) is dict
            and set(actual)
            == {
                "all_other_roles",
                "description",
                "function",
                "native_role_mode",
                "original_line",
            }
            and actual["description"] == description
            and actual["function"] == function
            and actual["original_line"] == line
            and actual["native_role_mode"] == 0o600
            and actual["all_other_roles"] == "PRESERVE ORIGINAL MODE",
            "reject an invented or weakened original native repair: " + description,
        )
    base.need(
        contract["native_stage_mode_controller_route"]
        == "AUTHENTICATED V7; EXACT THREE IN-MEMORY AST SITES"
        and contract["native_stage_mode_guarded_worker_route"]
        == "AUDIT FIRST; FOUR CTYPES PROXIES; EXACT THREE V7 AST SITES"
        and contract["native_stage_mode_recovery_route"]
        == "AUTHENTICATED V7; EXACT ORIGINAL FOUR INODES AND MODES"
        and contract["native_stage_mode_transformations_executed"] == 0
        and contract["native_stage_mode_native_owners_opened"] == 0,
        "never execute an original native transformation in a source-only graph",
    )
    base.need(
        all(
            contract["previous_v14_" + role + "_sha256"] == item[1]
            for role, item in v81.FEATURE.items()
        )
        and contract["v14_actual_failure_receipt_sha256"] == previous.RECEIPT[1]
        and contract["v14_actual_failure_receipt_bytes"] == previous.RECEIPT[2]
        and contract["v14_actual_failure_receipt_inode"] == previous.RECEIPT[3]
        and contract["v14_actual_candidate_worker_count"] == 13
        and contract["v14_actual_completed_suite_count"] == 0
        and contract["v14_actual_infrastructure_failure_count"] == 13
        and contract["v14_actual_semantic_mismatch_count"] == "NOT MEASURED"
        and contract["v14_actual_verified_passing_case_count"] == 0
        and contract["v14_actual_candidate_qualified"] is False
        and contract["v14_actual_all_four_original_targets_restored"] is True
        and contract["v14_actual_first_child_stderr_sha256"]
        == previous.FORENSIC_STDERR_SHA256
        and contract["v14_actual_first_child_stderr_bytes"]
        == len(previous.FORENSIC_STDERR)
        and contract["v14_actual_first_child_returncode"] == 2
        and contract["v14_actual_root_cause"]
        == previous.FORENSIC_STDERR.decode("utf-8", "strict")
        and contract["v14_failure_archive_opened"] is False
        and contract["v14_failure_archive_inflated"] is False,
        "retain the actual third loss and separately hash-verified child witness",
    )
    for version, module in ((12, v78), (13, v80)):
        prefix = "v" + str(version) + "_actual_"
        base.need(
            contract[prefix + "failure_receipt_sha256"] == module.RECEIPT[1]
            and contract[prefix + "failure_receipt_bytes"] == module.RECEIPT[2]
            and contract[prefix + "failure_receipt_inode"] == module.RECEIPT[3]
            and contract[prefix + "candidate_worker_count"] == 13
            and contract[prefix + "completed_suite_count"] == 0
            and contract[prefix + "infrastructure_failure_count"] == 13
            and contract[prefix + "semantic_mismatch_count"] == "NOT MEASURED"
            and contract[prefix + "verified_passing_case_count"] == 0
            and contract[prefix + "candidate_qualified"] is False
            and contract[prefix + "all_four_original_targets_restored"] is True
            and contract["v" + str(version) + "_failure_archive_opened"]
            is False
            and contract["v" + str(version) + "_failure_archive_inflated"]
            is False,
            "preserve the complete actual unopened V" + str(version) + " loss",
        )
    base.need(
        contract["worker_failure_capture_mode"]
        == "SCOPED AUTHENTIC CONTROLLER; FIRST COMPLETE BOUNDED PUBLIC "
        "STDOUT, STDERR, BASE64, EXIT AND ACTIVE TRACEBACK"
        and contract["worker_failure_capture_stream_limit_bytes"] == 65536
        and contract["worker_failure_capture_traceback_limit_bytes"] == 65536
        and contract["worker_failure_capture_total_budget_bytes"] == 4194304
        and contract["worker_failure_capture_public_first_full_streams"] is True
        and contract["worker_failure_capture_public_first_full_traceback"] is True
        and contract["worker_failure_capture_attempts"] == 0
        and contract["worker_failure_capture_complete"] == "NOT RUN"
        and contract["worker_failure_capture_processes_started"] == 0
        and contract["worker_failure_capture_native_loads"] == 0,
        "retain recoverable complete bounded diagnostics without running Rust",
    )
    base.need(
        contract["historical_ctypes_source_count"] == 4
        and type(contract["historical_ctypes_sources"]) is list
        and len(contract["historical_ctypes_sources"]) == 4
        and contract["historical_ctypes_proxy_native_load_permitted"] is False
        and contract["historical_ctypes_preloaded"] is False
        and contract["historical_ctypes_transforms_executed"] == 0
        and contract["recovery_role_order"] == list(v77.ROLE_ORDER)
        and contract["recovery_restoration_order"]
        == list(reversed(v77.ROLE_ORDER)),
        "retain the four fail-closed original worker proxies and recovery order",
    )
    for actual, expected in zip(
        contract["historical_ctypes_sources"], v81.HISTORICAL_CTYPES, strict=True
    ):
        role, path, digest, size, inode, import_line = expected
        base.need(
            type(actual) is dict
            and set(actual)
            == {
                "role",
                "path",
                "sha256",
                "bytes",
                "inode",
                "exact_top_level_import_line",
                "transformation",
            }
            and actual["role"] == role
            and actual["path"] == path
            and actual["sha256"] == digest
            and actual["bytes"] == size
            and actual["inode"] == inode
            and actual["exact_top_level_import_line"] == import_line
            and actual["transformation"]
            == "AUTHENTICATE RAW; REPLACE ONLY TOP-LEVEL IMPORT WITH "
            "A FAIL-CLOSED MODULE-LOCAL PROXY",
            "reject an altered frozen historical worker source: " + role,
        )
    base.need(
        contract["historical_rust_semantic_mismatch_count"] == 1440
        and contract["historical_rust_verified_passing_case_count"] == 14853
        and contract["actual_c_semantic_mismatch_count"] == 1230
        and contract["actual_c_verified_passing_case_count"] == 7325
        and contract["phase1_v4_reference_readiness"] == "PASS"
        and contract["phase2_candidate_qualification"] == "BLOCKED"
        and contract["reference_records_sha256"]
        == "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
        and contract["reference_cache_records_sha256"]
        == "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
        and contract["reference_worker_process_ids"] == [81, 82]
        and contract["candidate_correctness"] == "NOT MEASURED"
        and contract["candidate_matching"] == "NOT RUN"
        and contract["candidate_qualified"] is False
        and contract["qualified_candidate_count"] == 0
        and contract["runtime_non_delegation"] == "NOT ESTABLISHED"
        and contract["holdout"] == "NOT OPENED"
        and contract["performance"] == "NOT MEASURED"
        and contract["memory"] == "NOT MEASURED"
        and contract["undefined_behavior"] == "NOT MEASURED"
        and contract["confidence_intervals"] == "NOT MEASURED"
        and contract["winner_selected"] is False,
        "never hide historical differences or invent compatibility or speed",
    )
    for key in (
        "actual_candidate_workers_started",
        "actual_candidate_imports",
        "actual_native_libraries_loaded",
        "actual_private_build_root_opens",
        "actual_private_build_root_stats",
        "actual_build_archive_opens",
        "actual_build_archive_inflations",
        "actual_hidden_cases_read",
        "actual_clock_samples",
        "actual_compiler_processes_started",
        "timing_trials_run",
    ):
        base.need(contract[key] == 0, "forbid a source-only side effect: " + key)
    v14 = old["rust_v14_original_campaign_source_freeze"][
        "complete_feature_contract"
    ]
    v81.validate_contract(base, v80, v79, v78, v77, v14)
    v78.validate_receipt(
        base,
        v77,
        old["actual_rust_v12_original_campaign"]["complete_publication_receipt"],
    )
    v80.validate_receipt(
        base,
        v79,
        v78,
        v77,
        old["actual_rust_v13_original_campaign"]["complete_publication_receipt"],
    )
    previous.validate_receipt(
        base,
        v81,
        v79,
        v77,
        old["actual_rust_v14_original_campaign"]["complete_publication_receipt"],
    )


def make_pool(base: types.ModuleType, full_documents: dict) -> dict:
    base.need(
        type(full_documents) is dict and set(full_documents) == set(PROOF_KEYS),
        "pool exactly nine complete historical and new source proof objects",
    )
    entries: dict[str, dict] = {}
    for key in PROOF_KEYS:
        document = full_documents[key]
        base.need(
            type(document) is dict
            and type(document.get("schema")) is str
            and bool(document["schema"]),
            "reject an incomplete pooled family proof: " + key,
        )
        canonical = base.canonical(document)
        digest = base.digest(canonical)
        base.need(digest not in entries, "reject a duplicate pooled proof digest")
        entries[digest] = {
            "proof_key": key,
            "proof_schema": document["schema"],
            "canonical_sha256": digest,
            "canonical_bytes": len(canonical),
            "complete_proof": copy.deepcopy(document),
        }
    pool = {
        "schema": POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "entries": entries,
    }
    validate_pool(base, pool, full_documents)
    return pool


def validate_pool(base: types.ModuleType, pool: object, full_documents: dict) -> None:
    base.need(
        type(full_documents) is dict
        and set(full_documents) == set(PROOF_KEYS)
        and type(pool) is dict
        and set(pool) == {"schema", "version", "hash_algorithm", "entries"}
        and pool["schema"] == POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and type(pool["entries"]) is dict
        and len(pool["entries"]) == len(PROOF_KEYS),
        "reject an omitted, duplicate, extra, or wrong-schema full proof pool",
    )
    assert isinstance(pool, dict)
    observed: set[str] = set()
    for digest, entry in pool["entries"].items():
        base.need(
            type(entry) is dict
            and set(entry)
            == {
                "proof_key",
                "proof_schema",
                "canonical_sha256",
                "canonical_bytes",
                "complete_proof",
            }
            and type(digest) is str
            and base.checked(digest, "complete pooled proof digest") == digest
            and entry["canonical_sha256"] == digest
            and entry["proof_key"] in PROOF_KEYS
            and entry["proof_key"] not in observed
            and type(entry["complete_proof"]) is dict,
            "reject unbound, duplicate, or foreign complete family pool entry",
        )
        key = entry["proof_key"]
        canonical = base.canonical(entry["complete_proof"])
        base.need(
            entry["proof_schema"] == entry["complete_proof"].get("schema")
            and entry["canonical_bytes"] == len(canonical)
            and base.digest(canonical) == digest
            and base.canonical(full_documents[key]) == canonical,
            "reject substituted complete canonical pooled evidence: " + key,
        )
        observed.add(key)
    base.need(
        observed == set(PROOF_KEYS),
        "require one and only one complete canonical owner for all nine proofs",
    )


def make_reference(
    base: types.ModuleType, pool: dict, document: dict, key: str
) -> dict:
    base.need(key in PROOF_KEYS, "reject an unknown complete evidence reference")
    canonical = base.canonical(document)
    digest = base.digest(canonical)
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == key
        and entry.get("canonical_bytes") == len(canonical)
        and base.canonical(entry.get("complete_proof")) == canonical,
        "bind a family reference to its exact complete canonical proof: " + key,
    )
    return {
        "schema": REFERENCE_SCHEMA,
        "proof_key": key,
        "sha256": digest,
        "canonical_bytes": len(canonical),
    }


def resolve_reference(
    base: types.ModuleType, pool: dict, reference: object, expected_key: str
) -> dict:
    base.need(
        expected_key in PROOF_KEYS
        and type(reference) is dict
        and set(reference) == {"schema", "proof_key", "sha256", "canonical_bytes"}
        and reference["schema"] == REFERENCE_SCHEMA
        and reference["proof_key"] == expected_key
        and type(reference["canonical_bytes"]) is int
        and reference["canonical_bytes"] > 0,
        "reject a missing, wrong-schema, or cross-family proof reference",
    )
    assert isinstance(reference, dict)
    digest = base.checked(reference["sha256"], "whole family proof reference")
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == expected_key
        and entry.get("canonical_sha256") == digest
        and entry.get("canonical_bytes") == reference["canonical_bytes"]
        and type(entry.get("complete_proof")) is dict,
        "reject an unbound, swapped, truncated, or fabricated proof reference",
    )
    canonical = base.canonical(entry["complete_proof"])
    base.need(
        len(canonical) == reference["canonical_bytes"]
        and base.digest(canonical) == digest
        and entry["proof_schema"] == entry["complete_proof"].get("schema"),
        "recompute every canonical byte of a resolved whole family proof",
    )
    return copy.deepcopy(entry["complete_proof"])


def expand_family(base: types.ModuleType, row: object, pool: dict) -> dict:
    base.need(
        type(row) is dict
        and row.get("family") in {"rust", "c", "zig", "cpp", "go", "fortran"},
        "expand only an authentic independently implemented candidate family",
    )
    assert isinstance(row, dict)
    expanded = copy.deepcopy(row)
    for key in PROOF_KEYS:
        base.need(key in row, "reject an omitted complete family proof: " + key)
        expanded[key] = resolve_reference(base, pool, row[key], key)
    return expanded


def validate_families(
    base: types.ModuleType,
    families: object,
    previous_families: list,
    pool: dict,
    full_documents: dict,
    rust_changes: dict,
) -> None:
    validate_pool(base, pool, full_documents)
    base.need(
        type(families) is list
        and type(previous_families) is list
        and [row.get("family") for row in families if type(row) is dict]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and len(families) == len(previous_families) == 7,
        "preserve the Python baseline and all six independent engine families",
    )
    for row, original in zip(families, previous_families, strict=True):
        base.need(
            type(row) is dict
            and type(original) is dict
            and row["family"] == original["family"],
            "reject an invented, omitted, repeated, or reordered engine family",
        )
        if row["family"] == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "preserve the entire exact original Python baseline byte-for-byte",
            )
            continue
        expected = copy.deepcopy(original)
        expected["authenticated_evidence_owner_lower_bound"] = 270
        expected["authenticated_history_reference_lower_bound"] = 275
        expected[V15_PROOF_KEY] = copy.deepcopy(full_documents[V15_PROOF_KEY])
        if row["family"] == "rust":
            for key, value in rust_changes.items():
                expected[key] = copy.deepcopy(value)
        expanded = expand_family(base, row, pool)
        base.need(
            base.canonical(expanded) == base.canonical(expected),
            "prove exact lossless full evidence expansion for " + row["family"],
        )
        restored = copy.deepcopy(expanded)
        restored.pop(V15_PROOF_KEY)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if row["family"] == "rust":
            for key in rust_changes:
                base.need(
                    key not in original,
                    "reject overwriting previous exact Rust evidence: " + key,
                )
                restored.pop(key)
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore every canonical committed V82 family byte: " + row["family"],
        )
        base.need(
            row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "never promote source-only evidence into a passing candidate: "
            + row["family"],
        )


def make_svg() -> bytes:
    rows = (
        ("Python re", "Original compatibility reference", "BASELINE", "#22c55e"),
        (
            "Rust",
            "Three failed retests; exact startup repair prepared",
            "REPAIR NOT RETESTED",
            "#f59e0b",
        ),
        ("C", "1,230 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "1,764 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("C++", "2,308 differences; five startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Complete Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="704" viewBox="0 0 1200 704" role="img" aria-labelledby="title description">',
        '<title id="title">How six from-scratch regular-expression engines compare with Python</title>',
        '<desc id="description">Python is the compatibility baseline. Rust, C, Zig, C++, Go and Fortran are separate from-scratch candidates. All three real Rust retests failed to start thirteen workers each. A hash-verified child diagnostic identified the native bridge mode; an exact three-site repair is frozen but has not been retested. Every original result is preserved through lossless, canonical hash-verified evidence references. No candidate has passed, no speed has been measured, and the expanded final holdout remains unopened.</desc>',
        '<rect width="1200" height="704" rx="18" fill="#0b1220"/>',
        '<text x="34" y="48" fill="#f8fafc" font-size="26" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="81" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="104" x2="1166" y2="104" stroke="#334155"/>',
    ]
    for index, (name, description, verdict, colour) in enumerate(rows):
        y = 142 + 47 * index
        parts.extend((
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{description}</text>',
            f'<text x="1148" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{verdict}</text>',
        ))
    parts.extend((
        '<line x1="34" y1="462" x2="1166" y2="462" stroke="#334155"/>',
        '<text x="34" y="493" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate extra checks.</text>',
        '<text x="34" y="522" fill="#fda4af" font-size="14" font-family="system-ui,sans-serif">Three real Rust retests: 13 startup failures and 0 completed groups each.</text>',
        '<text x="34" y="550" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Verified cause: the safety guard rejected the native bridge mode. No safety check was relaxed.</text>',
        '<text x="34" y="578" fill="#fcd34d" font-size="14" font-family="system-ui,sans-serif">Exact three-site native-only correction: FROZEN. Corrected complete retest: NOT RUN.</text>',
        '<text x="34" y="606" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Every past test and failure remains available through complete, verified, lossless references.</text>',
        '<text x="34" y="634" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Speed, memory, and runtime independence: NOT MEASURED or NOT ESTABLISHED.</text>',
        '<text x="34" y="662" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Final 4,194,304-case comparison: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="691" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 83 · no erased history · no selected winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def load_contract(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    old: dict,
) -> dict:
    for role, item in FEATURE.items():
        read_fixed(item, "complete final released V15 " + role)
    raw = read_fixed(FEATURE["contract"], "complete canonical released V15 proof")
    contract = base.document(raw, "complete canonical released V15 proof")
    base.need(
        base.canonical(contract) == raw,
        "reject partial, noncanonical, or duplicate-key V15 source proof",
    )
    validate_contract(base, previous, chain, old, contract)
    return contract


def make_proof(base: types.ModuleType, contract: dict) -> dict:
    return {
        "schema": SCHEMA + "-guarded-rust-original-campaign-v15-source",
        "version": 15,
        "complete_feature_contract": copy.deepcopy(contract),
        "owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        },
        "independent_source_owner_count": 3,
        "actual_original_candidate_workers_started": 0,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "native_stage_mode_repair_status": contract[
            "native_stage_mode_repair_status"
        ],
        "native_stage_mode_patch_site_count": 3,
        "native_stage_mode_patch_sites": copy.deepcopy(
            contract["native_stage_mode_patch_sites"]
        ),
        "actual_v12_candidate_worker_count": 13,
        "actual_v13_candidate_worker_count": 13,
        "actual_v14_candidate_worker_count": 13,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "compressed_archives_opened": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def make_changes(proof: dict, contract: dict) -> tuple[dict, dict]:
    rust_changes = {
        "rust_v15_original_campaign_candidate_matching": "NOT RUN",
        "rust_v15_original_campaign_actual_worker_count": 0,
        "rust_v15_original_campaign_completed_suite_count": 0,
        "rust_v15_original_campaign_infrastructure_failure_count": 0,
        "rust_v15_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v15_original_campaign_verified_passing_case_count": 0,
        "rust_v15_original_campaign_candidate_qualified": False,
        "rust_v15_original_campaign_runtime_no_delegation": "NOT ESTABLISHED",
        "rust_v15_original_campaign_native_stage_mode_repair_status": contract[
            "native_stage_mode_repair_status"
        ],
        "rust_v15_original_campaign_native_stage_mode_patch_site_count": 3,
        "rust_v15_original_campaign_worker_failure_capture_complete": "NOT RUN",
        "rust_v15_original_campaign_outcome_archive_opened_by_graph": False,
    }
    changes = {
        "actual_current_graph_predecessor_version": 82,
        "authenticated_evidence_owner_lower_bound": 270,
        "authenticated_history_reference_lower_bound": 275,
        V15_PROOF_KEY: copy.deepcopy(proof),
        **copy.deepcopy(rust_changes),
    }
    return changes, rust_changes


def build(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None and options.source_bytes is not None,
        "require an independently supplied hash and length of the V83 source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole V83 renderer source"),
        options.source_bytes,
        private=True,
    )
    for role, item in V82.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin every exact complete committed V82 " + role,
        )
    for role, item in FEATURE.items():
        base.need(
            getattr(options, "feature_" + role + "_sha256") == item[1],
            "caller-pin every complete independently released V15 " + role,
        )
    old, previous_inputs = authenticate_previous(previous, chain, base)
    contract = load_contract(previous, chain, base, old)
    proof = make_proof(base, contract)
    full_documents = {
        key: copy.deepcopy(old[key]) for key in HISTORICAL_PROOF_KEYS
    }
    full_documents[V15_PROOF_KEY] = copy.deepcopy(proof)
    pool = make_pool(base, full_documents)
    changes, rust_changes = make_changes(proof, contract)
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v82_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V82.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 83,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        for key in HISTORICAL_PROOF_KEYS:
            base.need(
                base.canonical(row[key])
                == base.canonical(full_documents[key]),
                "preserve every exact historical family proof before compacting "
                + row["family"]
                + ": "
                + key,
            )
            row[key] = make_reference(base, pool, full_documents[key], key)
        row[V15_PROOF_KEY] = make_reference(
            base, pool, full_documents[V15_PROOF_KEY], V15_PROOF_KEY
        )
        row["authenticated_evidence_owner_lower_bound"] = 270
        row["authenticated_history_reference_lower_bound"] = 275
        if row["family"] == "rust":
            row.update(copy.deepcopy(rust_changes))
    validate_families(
        base,
        families,
        old["families"],
        pool,
        full_documents,
        rust_changes,
    )
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 83,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        "lossless_family_evidence_pool": pool,
        "lossless_family_evidence_pool_schema": POOL_SCHEMA,
        "lossless_family_evidence_pool_entry_count": len(PROOF_KEYS),
        "lossless_family_references_per_family": len(PROOF_KEYS),
        "lossless_family_reconstruction_status": "PASS",
        "lossless_family_previous_byte_identity_status": "PASS",
        "lossless_family_deduplication":
            "CANONICAL SHA-256 REFERENCES; LOSSLESS EXPANSION",
        **copy.deepcopy(changes),
    })
    suites = old["actual_complete_rust_campaign"][
        "complete_independently_authenticated_suite_results"
    ]
    witnesses = old["actual_complete_rust_campaign"][
        "earliest_genuine_mismatch_witnesses"
    ]
    base.need(
        len(suites) == 13 and len(witnesses) == 6,
        "preserve all original suite vectors and all six real mismatch witnesses",
    )
    for label, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        observed = layer["actual_complete_rust_campaign"]
        base.need(
            observed["complete_independently_authenticated_suite_results"]
            == suites
            and observed["earliest_genuine_mismatch_witnesses"] == witnesses
            and all(
                base.canonical(layer[key]) == base.canonical(full_documents[key])
                for key in PROOF_KEYS
            )
            and layer["rust_v12_original_campaign_actual_worker_count"] == 13
            and layer["rust_v12_original_campaign_completed_suite_count"] == 0
            and layer["rust_v12_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v13_original_campaign_actual_worker_count"] == 13
            and layer["rust_v13_original_campaign_completed_suite_count"] == 0
            and layer["rust_v13_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v14_original_campaign_actual_worker_count"] == 13
            and layer["rust_v14_original_campaign_completed_suite_count"] == 0
            and layer["rust_v14_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v14_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["rust_v15_original_campaign_candidate_matching"]
            == "NOT RUN"
            and layer["rust_v15_original_campaign_actual_worker_count"] == 0
            and layer["rust_v15_original_campaign_candidate_qualified"] is False,
            "retain all complete proofs, historical losses, and witnesses in "
            + label,
        )
    base.need(
        summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_rust_verified_passing_case_count"] == 14853
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_c_verified_passing_case_count"] == 7325
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["actual_zig_verified_passing_case_count"] == 3711
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["final_holdout_opened"] is False
        and summary["lossless_family_evidence_pool_entry_count"] == 9
        and summary["lossless_family_references_per_family"] == 9,
        "never erase observed differences, fabricate a speedup, or open holdout",
    )
    summary_raw = base.canonical(summary)
    assets = {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": summary_raw,
        OUTPUT + ".svg": svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
            "reject oversized or partial V83 evidence BEFORE any write: " + path,
        )
    return snapshot, assets


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only a complete exclusively created bounded V83 graph owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(
                type(count) is int and count > 0,
                "publish every complete exclusively created V83 output byte",
            )
            remaining = remaining[count:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "authenticate the complete uniquely created V83 output owner",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(confirmed == raw, "reauthenticate every complete V83 output byte")


def self_test(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(*chain)
    base.need(
        prior["status"] == "PASS"
        and prior["previous_overview_version"] == 81
        and prior["authenticated_evidence_owner_lower_bound"] == 267
        and prior["authenticated_history_reference_lower_bound"] == 272
        and prior["previous_v12_actual_rust_infrastructure_failure_count"] == 13
        and prior["previous_v13_actual_rust_infrastructure_failure_count"] == 13
        and prior["actual_diagnostic_rust_candidate_worker_count_from_receipt"]
        == 13
        and prior["actual_diagnostic_rust_completed_suite_count_from_receipt"]
        == 0
        and prior[
            "actual_diagnostic_rust_infrastructure_failure_count_from_receipt"
        ] == 13
        and prior["actual_candidate_workers_started_by_graph"] == 0
        and prior["actual_compressed_evidence_owners_opened_by_graph"] == 0
        and prior["actual_clock_samples_by_graph"] == 0
        and prior["runtime_no_delegation"] == "NOT ESTABLISHED"
        and prior["qualified_candidate_count"] == 0
        and prior["final_holdout_opened"] is False
        and prior["performance"] == "NOT MEASURED",
        "inherit all prior actual failures and the complete V82 hostile controls",
    )
    old, _ = authenticate_previous(previous, chain, base)
    contract = load_contract(previous, chain, base, old)
    proof = make_proof(base, contract)
    full_documents = {
        key: copy.deepcopy(old[key]) for key in HISTORICAL_PROOF_KEYS
    }
    full_documents[V15_PROOF_KEY] = copy.deepcopy(proof)
    pool = make_pool(base, full_documents)
    _, rust_changes = make_changes(proof, contract)
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        for key in PROOF_KEYS:
            row[key] = make_reference(base, pool, full_documents[key], key)
        row["authenticated_evidence_owner_lower_bound"] = 270
        row["authenticated_history_reference_lower_bound"] = 275
        if row["family"] == "rust":
            row.update(copy.deepcopy(rust_changes))
    validate_families(
        base, families, old["families"], pool, full_documents, rust_changes
    )
    rejected = 0

    def reject(label: str, check: object) -> None:
        nonlocal rejected
        try:
            assert callable(check)
            check()
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted fabricated V83 source evidence: " + label)

    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        reject(
            "omitted exact V15 contract key " + key,
            lambda candidate=forged: validate_contract(
                base, previous, chain, old, candidate
            ),
        )
    for key, value in (
        ("version", 14),
        ("status", "CANDIDATE PASS"),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("goal_sha256", "0" * 64),
        ("frozen_graph_version", 81),
        ("frozen_graph_source_sha256", "0" * 64),
        ("frozen_graph_summary_sha256", "0" * 64),
        ("current_evidence_owner_lower_bound", 268),
        ("prospective_evidence_owner_lower_bound", 271),
        ("prospective_history_reference_lower_bound", 276),
        ("suite_count", 12),
        ("case_execution_denominator", 31236),
        ("supplemental_cases_counted_in_original_denominator", True),
        ("native_stage_mode_patch_site_count", 2),
        ("native_stage_mode_active_native_mode", 0o755),
        ("native_stage_mode_preserved_original_native_mode", 0o600),
        ("native_stage_mode_native_owners_opened", 1),
        ("native_stage_mode_transformations_executed", 1),
        ("runtime_guard_source_sha256", "0" * 64),
        ("v12_actual_candidate_worker_count", 0),
        ("v13_actual_candidate_worker_count", 0),
        ("v14_actual_candidate_worker_count", 0),
        ("v14_actual_first_child_stderr_sha256", "0" * 64),
        ("v14_actual_first_child_returncode", 0),
        ("v14_actual_root_cause", "candidate passes\n"),
        ("v14_failure_archive_opened", True),
        ("worker_failure_capture_public_first_full_streams", False),
        ("worker_failure_capture_public_first_full_traceback", False),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("qualified_candidate_count", 1),
        ("runtime_non_delegation", "PASS"),
        ("performance", "1.5x"),
        ("holdout", "OPENED"),
        ("winner_selected", True),
        ("actual_candidate_workers_started", 1),
        ("actual_build_archive_opens", 1),
        ("actual_hidden_cases_read", 1),
        ("actual_clock_samples", 1),
        ("timing_trials_run", 1),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = value
        reject(
            "fabricated V15 contract value " + key,
            lambda candidate=forged: validate_contract(
                base, previous, chain, old, candidate
            ),
        )
    for index, (_, _, _) in enumerate(PATCH_SITES):
        for key, value in (
            ("native_role_mode", 0o755),
            ("all_other_roles", "REPLACE ALL ORIGINAL MODES"),
            ("original_line", 0),
            ("function", "invented_worker"),
        ):
            forged = copy.deepcopy(contract)
            forged["native_stage_mode_patch_sites"][index][key] = value
            reject(
                "fabricated native repair site " + str(index) + ": " + key,
                lambda candidate=forged: validate_contract(
                    base, previous, chain, old, candidate
                ),
            )
    reject("absent complete proof pool", lambda: validate_pool(base, None, full_documents))
    for key, value in (
        ("schema", "invented-pool"),
        ("version", 2),
        ("hash_algorithm", "sha1"),
    ):
        forged_pool = copy.deepcopy(pool)
        forged_pool[key] = value
        reject(
            "fabricated complete proof pool " + key,
            lambda candidate=forged_pool: validate_pool(
                base, candidate, full_documents
            ),
        )
    for digest, entry in pool["entries"].items():
        removed = copy.deepcopy(pool)
        removed["entries"].pop(digest)
        reject(
            "omitted whole family proof " + entry["proof_key"],
            lambda candidate=removed: validate_pool(base, candidate, full_documents),
        )
        for key, value in (
            ("proof_key", "foreign-family-proof"),
            ("proof_schema", "invented-proof-schema"),
            ("canonical_sha256", "0" * 64),
            ("canonical_bytes", entry["canonical_bytes"] + 1),
        ):
            forged_pool = copy.deepcopy(pool)
            forged_pool["entries"][digest][key] = value
            reject(
                "fabricated pooled proof " + entry["proof_key"] + ": " + key,
                lambda candidate=forged_pool: validate_pool(
                    base, candidate, full_documents
                ),
            )
    foreign = copy.deepcopy(pool)
    first_digest = next(iter(foreign["entries"]))
    foreign["entries"]["0" * 64] = copy.deepcopy(
        foreign["entries"][first_digest]
    )
    reject(
        "extra duplicate or foreign canonical pool owner",
        lambda: validate_pool(base, foreign, full_documents),
    )
    for family_index, original in enumerate(families):
        if original["family"] == "python":
            forged_families = copy.deepcopy(families)
            forged_families[family_index]["family"] = "python-invented"
            reject(
                "modified exact Python baseline",
                lambda candidate=forged_families: validate_families(
                    base,
                    candidate,
                    old["families"],
                    pool,
                    full_documents,
                    rust_changes,
                ),
            )
            continue
        for key in PROOF_KEYS:
            for reference_key, value in (
                ("schema", "foreign-reference-schema"),
                ("proof_key", "foreign-family-proof"),
                ("sha256", "0" * 64),
                ("canonical_bytes", original[key]["canonical_bytes"] + 1),
            ):
                forged_reference = copy.deepcopy(original[key])
                forged_reference[reference_key] = value
                reject(
                    "substituted complete family reference "
                    + original["family"]
                    + ": "
                    + key
                    + ": "
                    + reference_key,
                    lambda candidate=forged_reference, proof_key=key:
                        resolve_reference(base, pool, candidate, proof_key),
                )
        forged_families = copy.deepcopy(families)
        forged_families[family_index].pop(V15_PROOF_KEY)
        reject(
            "removed exact new full proof from " + original["family"],
            lambda candidate=forged_families: validate_families(
                base,
                candidate,
                old["families"],
                pool,
                full_documents,
                rust_changes,
            ),
        )
    base.need(
        rejected >= 400,
        "reject omitted histories, swapped canonical refs, fake repairs and speed",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 83,
        "status": "PASS",
        "previous_overview_version": 82,
        "actual_current_graph_predecessor_version": 82,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ] + rejected,
        "authenticated_evidence_owner_lower_bound": 270,
        "authenticated_history_reference_lower_bound": 275,
        "lossless_family_evidence_pool_schema": POOL_SCHEMA,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_family_references_per_family": 9,
        "lossless_family_reconstruction_status": "PASS",
        "lossless_family_previous_byte_identity_status": "PASS",
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "previous_v12_actual_rust_candidate_worker_count": 13,
        "previous_v12_actual_rust_infrastructure_failure_count": 13,
        "previous_v13_actual_rust_candidate_worker_count": 13,
        "previous_v13_actual_rust_infrastructure_failure_count": 13,
        "previous_v14_actual_rust_candidate_worker_count": 13,
        "previous_v14_actual_rust_infrastructure_failure_count": 13,
        "actual_v15_candidate_worker_count": 0,
        "actual_v15_candidate_matching": "NOT RUN",
        "actual_native_stage_repair_transformations": 0,
        "native_stage_mode_patch_site_count": 3,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_compressed_evidence_inflations_by_graph": 0,
        "actual_private_build_root_opens_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V82:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, chain, base = load_previous()
        if options.self_test:
            base.need(
                all(
                    getattr(options, key) is None
                    for key in (
                        "source_sha256",
                        "source_bytes",
                        "inputs_sha256",
                        "summary_sha256",
                        "svg_sha256",
                    )
                )
                and all(
                    getattr(options, "previous_" + role + "_sha256") is None
                    for role in V82
                )
                and all(
                    getattr(options, "feature_" + role + "_sha256") is None
                    for role in FEATURE
                ),
                "source self-test never publishes, runs candidates, or measures",
            )
            result = self_test(previous, chain, base)
        else:
            _, assets = build(previous, chain, base, options)
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject invented or preexisting V83 output identities",
                )
                for path, raw in assets.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (
                    ("inputs", ".inputs.json"),
                    ("summary", ".json"),
                    ("svg", ".svg"),
                ):
                    path = OUTPUT + suffix
                    actual, _ = base.read_owner(
                        path,
                        base.checked(
                            getattr(options, role + "_sha256"),
                            "complete read-only V83 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reconstruct every exact canonical V83 byte: " + role,
                    )
            result = {
                "schema": SCHEMA
                + ("-published" if options.render else "-read-only-frozen-context"),
                "version": 83,
                "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{
                    role + "_sha256": base.digest(raw)
                    for role, raw in (
                        ("inputs", assets[OUTPUT + ".inputs.json"]),
                        ("summary", assets[OUTPUT + ".json"]),
                        ("svg", assets[OUTPUT + ".svg"]),
                    )
                },
                **{
                    "feature_" + role + "_sha256": item[1]
                    for role, item in FEATURE.items()
                },
                "previous_overview_version": 82,
                "actual_current_graph_predecessor_version": 82,
                "authenticated_evidence_owner_lower_bound": 270,
                "authenticated_history_reference_lower_bound": 275,
                "lossless_family_evidence_pool_schema": POOL_SCHEMA,
                "lossless_family_evidence_pool_entry_count": 9,
                "lossless_family_references_per_family": 9,
                "lossless_family_reconstruction_status": "PASS",
                "lossless_family_previous_byte_identity_status": "PASS",
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "previous_v12_actual_rust_candidate_worker_count": 13,
                "previous_v13_actual_rust_candidate_worker_count": 13,
                "previous_v14_actual_rust_candidate_worker_count": 13,
                "actual_v15_candidate_worker_count": 0,
                "actual_v15_candidate_matching": "NOT RUN",
                "native_stage_mode_patch_site_count": 3,
                "actual_candidate_workers_started_by_graph": 0,
                "actual_compiler_processes_started_by_graph": 0,
                "actual_compressed_evidence_owners_opened_by_graph": 0,
                "actual_compressed_evidence_inflations_by_graph": 0,
                "actual_private_build_root_opens_by_graph": 0,
                "actual_clock_samples_by_graph": 0,
                "actual_hidden_cases_read_by_graph": 0,
                "runtime_no_delegation": "NOT ESTABLISHED",
                "qualified_candidate_count": 0,
                "final_holdout_opened": False,
                "performance": "NOT MEASURED",
                "outputs_written": bool(options.render),
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V83 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
