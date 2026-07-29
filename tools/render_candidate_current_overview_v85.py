#!/usr/bin/env python3
"""Record independently owned Zig source without claiming a native build."""

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
SELF = "tools/render_candidate_current_overview_v85.py"
OUTPUT = "docs/evidence/candidate-current-overview-v85"
SCHEMA = "rebar-candidate-current-overview-v85"
ZIG_KEY = "zig_v13_first_party_scanner_source_build_source_freeze"
ZIG_POOL_SCHEMA = SCHEMA + "-lossless-complete-zig-source-pool-v1"
ZIG_REFERENCE_SCHEMA = SCHEMA + "-complete-zig-source-reference-v1"
V84 = {
    "source": (
        "tools/render_candidate_current_overview_v84.py",
        "00f9767cf82571ae10246f80a12d2c87a221f1a97f8d8c3baecce32e8eda3a8d",
        72026,
        430945,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v84.inputs.json",
        "08a83e53458e457f9cc62ca876a25e9291c58f048a5f9bbe93a4784b82ff027a",
        1320360,
        431664,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v84.json",
        "9f801745dbed779b2cd02aacd5fc6aaeecf016a8e33c37ae1eee043ffab18bca",
        3798003,
        431665,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v84.svg",
        "8f140d26cfc0759abd5599c8604d143d1e9da660f91d3dc5a72da1749a175d03",
        6100,
        431666,
    ),
}
FEATURE = {
    "source": (
        "tools/reproduce_owned_zig_scanner_phrase_source_build_v13.py",
        "673cb1a5a1b2b70d36e77032e01312fda2887828a8898900f1c91378fde8687e",
        123672,
        431366,
    ),
    "protocol": (
        "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-BUILD-V13.md",
        "b8c3622d64041386c6202f0d980632c9e03a8c90c08455d1c38a50260ae68a40",
        8765,
        524873,
    ),
    "contract": (
        "oracle/phase2/zig-scanner-phrase-source-build-v13.json",
        "6b0b918da55d55144c1384d915027f9ba360048c910a4225568abce6fd3efd15",
        21331,
        524874,
    ),
}
CONTRACT_KEYS = frozenset({
    "current_graph",
    "first_party_phrase_repair",
    "from_scratch_policy",
    "frozen_source_owners",
    "future_native_build",
    "holdout",
    "memory",
    "offline_toolchain",
    "original_oracle",
    "performance",
    "phase",
    "preserved_actual_history",
    "protocol",
    "qualified_candidate_count",
    "schema",
    "source",
    "source_only_effects",
    "status",
    "undefined_behavior",
    "version",
    "winner_selected",
})
OWNER_KEYS = frozenset({
    "bytes", "device", "inode", "mode", "nlink", "path", "sha256", "uid"
})
GRAPH_KEYS = frozenset({
    "authenticated_evidence_owner_lower_bound",
    "authenticated_history_reference_lower_bound",
    "lower_bounds_are_complete_repository_census",
    "owners",
    "prospective_evidence_owner_lower_bound",
    "prospective_history_reference_lower_bound",
    "prospective_independent_feature_source_owner_count",
    "source_freeze_new_evidence_owner_count",
    "version",
})
PHRASE_KEYS = frozenset({
    "additional_candidate_family_count",
    "complete_corrected_adapter",
    "complete_original_scanner_matrix_case_count",
    "contract",
    "corrected_candidate_matching",
    "corrected_source_witness_count",
    "corrected_source_witness_ids_sha256",
    "family",
    "first_party_cpython_c_api_bridge",
    "first_party_zig_parser_compiler_executor",
    "original_adapter_modified",
    "original_bridge_modified",
    "original_engine_modified",
    "preserved_original_scanner_case_count",
    "protocol",
    "scanner_matrix_sha256",
    "source",
    "unchanged_original_adapter",
    "version",
})
POLICY_KEYS = frozenset({
    "cross_candidate_engine",
    "external_regex_package",
    "matching_fallback",
    "network_fetch",
    "prebuilt_matching_engine",
    "runtime_non_delegation",
    "stdlib_regex_engine",
    "stdlib_sre_engine",
})
EFFECT_KEYS = frozenset({
    "benchmark_files_opened",
    "build_receipts_published",
    "candidate_imports",
    "candidate_workers_started",
    "clock_samples",
    "compiler_binaries_executed",
    "compiler_processes_started",
    "files_written",
    "holdout_files_opened",
    "matching_archives_inflated",
    "matching_archives_opened",
    "native_activations",
    "native_libraries_loaded",
    "network_requests",
    "private_phase_directories_created",
    "private_root_receipts_published",
    "private_roots_created",
    "private_source_files_written",
    "reference_archives_opened",
    "reference_workers_started",
})
FUTURE_KEYS = frozenset({
    "actual_build_receipt_count",
    "actual_private_root_receipt_count",
    "actual_process_count",
    "actual_source_snapshot_count",
    "authorization",
    "build_receipt_schema",
    "build_receipt_template",
    "byte_identical_engine_and_bridge",
    "candidate_correctness",
    "candidate_matching",
    "candidate_qualified",
    "compressed_evidence_owner_count",
    "expected_process_count_only_after_both_phases",
    "expected_process_count_per_phase",
    "failure_cleanup_restricts_exact_owned_private_root",
    "full_native_elf_audit",
    "independent_phase_count",
    "independent_source_owners_per_phase",
    "native_roles_per_phase",
    "phase_names",
    "planned_commands",
    "private_root_mode",
    "private_root_prefix",
    "private_root_receipt_schema",
    "private_root_receipt_template",
    "private_source_mode",
    "process_roles_per_phase",
    "receipts_are_exclusive_plaintext_json",
    "status",
})
PROCESS_ROLES = (
    "readelf_version",
    "gcc_version",
    "zig_version",
    "build_zig_engine",
    "build_zig_bridge",
    "engine_dynamic",
    "engine_symbols",
    "engine_sections",
    "engine_notes",
    "bridge_dynamic",
    "bridge_symbols",
    "bridge_sections",
    "bridge_notes",
)
EXPECTED_SOURCE_OWNER_PATHS = frozenset({
    "GOAL.md",
    "oracle/phase1/p0-completeness-v1.json",
    "oracle/phase1/p0-completeness-v4.json",
    "oracle/phase2/six-family-p0-producer-v4.json",
    "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-"
    "two-worker-8244-v3/two-independent-reference-result.json",
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v15-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-"
    "original-p0-v15-failures-publication-receipt.json",
    "tools/apply_owned_zig_scanner_phrase_source_repair_v4.py",
    "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md",
    "oracle/phase2/zig-scanner-phrase-source-repair-v4.json",
    "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py",
    "candidates/zig/mini_regex.zig",
    "candidates/zig/py_bridge.c",
    "candidates/zig_candidate.py",
    "toolchains/zig-0.16.0.lock.json",
    "tools/render_candidate_current_overview_v84.py",
    "docs/evidence/candidate-current-overview-v84.inputs.json",
    "docs/evidence/candidate-current-overview-v84.json",
    "docs/evidence/candidate-current-overview-v84.svg",
})


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
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
            raise ValueError("reject substituted complete V85 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V85 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject extended complete V85 owner: " + label)
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
            raise ValueError("reject changed complete V85 owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple[
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    tuple,
    types.ModuleType,
]:
    raw = read_fixed(V84["source"], "whole actually pushed V84 actual graph")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v84")
    previous.__file__ = str(ROOT / V84["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v83, v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v84"
        and previous.SELF == V84["source"][0]
        and len(chain) == 15,
        "require the entire actually pushed V84 graph and history chain",
    )
    return previous, v83, v82, chain, base


def authenticate_previous(
    previous: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V84["source"][1],
        "source_bytes": V84["source"][2],
        "receipt_sha256": previous.RECEIPT[1],
    }
    for role, item in previous.V83.items():
        pins["previous_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v83, v82, chain, base, argparse.Namespace(**pins)
    )
    for role in ("inputs", "summary", "svg"):
        item = V84[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole actual V84 " + role),
            "reconstruct every byte of the committed V84 " + role,
        )
    old = base.document(assets[V84["summary"][0]], "whole pushed V84 summary")
    inputs = base.document(assets[V84["inputs"][0]], "whole pushed V84 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 84
        and inputs["version"] == 84
        and old["actual_current_graph_predecessor_version"] == 83
        and old["authenticated_evidence_owner_lower_bound"] == 272
        and old["authenticated_history_reference_lower_bound"] == 277
        and old["lossless_family_evidence_pool_entry_count"] == 9
        and old["lossless_family_references_per_family"] == 9
        and old["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and old["lossless_actual_outcome_references_per_family"] == 1
        and old["lossless_v83_family_previous_byte_identity_status"] == "PASS"
        and old["rust_v12_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v13_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v14_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v15_original_campaign_candidate_matching"] == "FAIL"
        and old["rust_v15_original_campaign_actual_worker_count"] == 13
        and old["rust_v15_original_campaign_completed_suite_count"] == 8
        and old["rust_v15_original_campaign_verified_passing_case_count"]
        == 12942
        and old["rust_v15_original_campaign_infrastructure_failure_count"] == 5
        and old["rust_v15_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old[
            "rust_v15_original_campaign_pattern_destructor_proven_failure_cause"
        ] is False
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["qualified_candidate_count"] == 0
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "retain all real Rust cases, failures, causes, and both exact V84 pools",
    )
    full_documents = {key: copy.deepcopy(old[key]) for key in v83.PROOF_KEYS}
    v83.validate_pool(base, old["lossless_family_evidence_pool"], full_documents)
    previous.validate_actual_pool(
        base,
        old["lossless_actual_outcome_evidence_pool"],
        old[previous.ACTUAL_KEY],
    )
    return old, inputs


def validate_owner(
    base: types.ModuleType,
    value: object,
    item: tuple[str, str, int, int],
    label: str,
) -> None:
    path, digest, size, inode = item
    base.need(
        type(value) is dict
        and set(value) == OWNER_KEYS
        and value["path"] == path
        and value["sha256"] == digest
        and value["bytes"] == size
        and value["device"] == 2064
        and value["inode"] == inode
        and value["mode"] == "0600"
        and value["nlink"] == 1
        and value["uid"] == os.geteuid(),
        "reject an altered complete first-party Zig source owner: " + label,
    )


def validate_contract(
    base: types.ModuleType,
    previous: types.ModuleType,
    v83: types.ModuleType,
    old: dict,
    contract: object,
) -> None:
    base.need(
        type(contract) is dict and set(contract) == CONTRACT_KEYS,
        "reject provisional, incomplete, or foreign complete Zig V13 source",
    )
    assert isinstance(contract, dict)
    base.need(
        contract["schema"]
        == "rebar-owned-zig-scanner-phrase-source-build-v13-source-freeze"
        and contract["version"] == 13
        and contract["status"] == "SOURCE FROZEN; CORRECTED ZIG BUILD NOT RUN"
        and contract["phase"]
        == "PHASE 2 FIRST-PARTY ZIG V4 PHRASE NATIVE BUILD SOURCE FREEZE",
        "distinguish independently frozen Zig source from an actual native build",
    )
    validate_owner(base, contract["source"], FEATURE["source"], "controller")
    validate_owner(base, contract["protocol"], FEATURE["protocol"], "protocol")
    graph = contract["current_graph"]
    base.need(
        type(graph) is dict
        and set(graph) == GRAPH_KEYS
        and graph["version"] == 84
        and graph["authenticated_evidence_owner_lower_bound"] == 272
        and graph["authenticated_history_reference_lower_bound"] == 277
        and graph["prospective_evidence_owner_lower_bound"] == 275
        and graph["prospective_history_reference_lower_bound"] == 280
        and graph["prospective_independent_feature_source_owner_count"] == 3
        and graph["source_freeze_new_evidence_owner_count"] == 0
        and graph["lower_bounds_are_complete_repository_census"] is False
        and type(graph["owners"]) is list
        and len(graph["owners"]) == 4,
        "derive exact 275/280 exclusively from three frozen first-party owners",
    )
    for actual, (role, item) in zip(
        graph["owners"], V84.items(), strict=True
    ):
        validate_owner(base, actual, item, "complete current graph " + role)
    phrase = contract["first_party_phrase_repair"]
    base.need(
        type(phrase) is dict
        and set(phrase) == PHRASE_KEYS
        and phrase["family"] == "zig"
        and phrase["version"] == 4
        and phrase["additional_candidate_family_count"] == 0
        and phrase["corrected_candidate_matching"] == "NOT RUN"
        and phrase["original_adapter_modified"] is False
        and phrase["original_bridge_modified"] is False
        and phrase["original_engine_modified"] is False
        and phrase["complete_original_scanner_matrix_case_count"] == 1024
        and phrase["preserved_original_scanner_case_count"] == 960
        and phrase["corrected_source_witness_count"] == 64
        and phrase["scanner_matrix_sha256"]
        == "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c"
        and phrase["corrected_source_witness_ids_sha256"]
        == "e1b75493de4be5ea1583e30077737405112b22fdb072cd8b0e38e2770a2959e6",
        "preserve the entire first-party source-only scanner variant and witness",
    )
    for field, item in (
        (
            "first_party_zig_parser_compiler_executor",
            (
                "candidates/zig/mini_regex.zig",
                "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
                186915,
                429377,
            ),
        ),
        (
            "first_party_cpython_c_api_bridge",
            (
                "candidates/zig/py_bridge.c",
                "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
                173026,
                429075,
            ),
        ),
        (
            "complete_corrected_adapter",
            (
                "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py",
                "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b",
                68530,
                428966,
            ),
        ),
        (
            "unchanged_original_adapter",
            (
                "candidates/zig_candidate.py",
                "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
                68422,
                429360,
            ),
        ),
        (
            "source",
            (
                "tools/apply_owned_zig_scanner_phrase_source_repair_v4.py",
                "31dafa08a8f394a8803fa352dd31c806fdac7aa6ee9160e67f2d5f60b2736a63",
                65425,
                428967,
            ),
        ),
        (
            "protocol",
            (
                "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md",
                "e17a46e13652e2950171d84096a0bf812020c88168589c17e50e1bab187339cf",
                6919,
                524729,
            ),
        ),
        (
            "contract",
            (
                "oracle/phase2/zig-scanner-phrase-source-repair-v4.json",
                "5c8f9a220bf93fc56e9d8054002ea4358323c23a9a951d3ce28201b59947b19c",
                11500,
                524730,
            ),
        ),
    ):
        validate_owner(base, phrase[field], item, field)
    policy = contract["from_scratch_policy"]
    base.need(
        type(policy) is dict
        and set(policy) == POLICY_KEYS
        and all(
            policy[key] == "FORBIDDEN"
            for key in POLICY_KEYS - {"runtime_non_delegation"}
        )
        and policy["runtime_non_delegation"] == "NOT ESTABLISHED",
        "forbid external packages, stdlib engines, fallback and borrowed matchers",
    )
    oracle = contract["original_oracle"]
    base.need(
        type(oracle) is dict
        and set(oracle)
        == {
            "mapped_original_obligation_count",
            "original_case_execution_denominator",
            "original_crosswalk_count",
            "original_named_private_waiver_count",
            "original_suite_count",
            "python_implementation",
            "python_version",
            "supplemental_candidate_status",
            "supplemental_cases_added_to_original_denominator",
            "supplemental_reference_case_count",
            "supplemental_reference_worker_count",
        }
        and oracle["mapped_original_obligation_count"] == 73
        and oracle["original_crosswalk_count"] == 34
        and oracle["original_case_execution_denominator"] == 31237
        and oracle["original_named_private_waiver_count"] == 13
        and oracle["original_suite_count"] == 13
        and oracle["python_implementation"] == "CPython"
        and oracle["python_version"] == "3.14.6"
        and oracle["supplemental_candidate_status"] == "NOT RUN"
        and oracle["supplemental_cases_added_to_original_denominator"] is False
        and oracle["supplemental_reference_case_count"] == 8244
        and oracle["supplemental_reference_worker_count"] == 2,
        "retain all original cases and genuinely separate differential checks",
    )
    history = contract["preserved_actual_history"]
    base.need(
        type(history) is dict
        and set(history)
        == {
            "actual_rust_v15_original_matching",
            "c_native_build",
            "c_original_matching",
            "complete_proof_references_across_six_families",
            "lossless_actual_outcome_evidence_pool",
            "lossless_family_evidence_pool",
            "rust_original_matching",
            "rust_v11_original_campaign",
            "rust_v19_native_build",
            "zig_original_matching",
        }
        and history["complete_proof_references_across_six_families"] == 60
        and history["lossless_family_evidence_pool"]
        == {
            "entry_count": 9,
            "references_per_family": 9,
            "schema": old["lossless_family_evidence_pool"]["schema"],
        }
        and history["lossless_actual_outcome_evidence_pool"]
        == {
            "entry_count": 1,
            "references_per_family": 1,
            "schema": old["lossless_actual_outcome_evidence_pool"]["schema"],
        },
        "preserve all 60 genuine canonical prior-family proof references",
    )
    rust = history["actual_rust_v15_original_matching"]
    expected_rust_keys = {
        "actual_candidate_worker_count",
        "all_original_observation_vectors_complete",
        "all_original_targets_restored",
        "attempted_suite_count",
        "candidate_qualified",
        "candidate_status",
        "completed_suite_count",
        "infrastructure_failure_count",
        "matching_archive_inflated",
        "matching_archive_opened",
        "plaintext_receipt",
        "publication_is_candidate_correctness",
        "publication_pass_means",
        "publication_status",
        "semantic_mismatch_count",
        "started_suite_count",
        "verified_passing_case_count",
        "worker_failure_capture_complete",
        "worker_failure_capture_count",
    }
    base.need(
        type(rust) is dict
        and set(rust) == expected_rust_keys
        and rust["actual_candidate_worker_count"] == 13
        and rust["attempted_suite_count"] == 13
        and rust["started_suite_count"] == 13
        and rust["completed_suite_count"] == 8
        and rust["verified_passing_case_count"] == 12942
        and rust["infrastructure_failure_count"] == 5
        and rust["semantic_mismatch_count"] == "NOT MEASURED"
        and rust["candidate_status"] == "FAIL"
        and rust["candidate_qualified"] is False
        and rust["all_original_observation_vectors_complete"] is False
        and rust["all_original_targets_restored"] is True
        and rust["matching_archive_opened"] is False
        and rust["matching_archive_inflated"] is False
        and rust["publication_is_candidate_correctness"] is False
        and rust["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and rust["publication_status"] == "PASS"
        and rust["worker_failure_capture_complete"] is True
        and rust["worker_failure_capture_count"] == 5,
        "preserve the actual 13-worker, 8-completion, 12,942-case Rust failure",
    )
    validate_owner(base, rust["plaintext_receipt"], previous.RECEIPT, "V15 receipt")
    future = contract["future_native_build"]
    base.need(
        type(future) is dict
        and set(future) == FUTURE_KEYS
        and future["status"] == "NOT RUN"
        and future["authorization"]
        == "EXPLICIT --build --label AFTER COMMITTED SOURCE FREEZE"
        and future["actual_build_receipt_count"] == 0
        and future["actual_private_root_receipt_count"] == 0
        and future["actual_process_count"] == 0
        and future["actual_source_snapshot_count"] == 0
        and future["candidate_correctness"] == "NOT MEASURED"
        and future["candidate_matching"] == "NOT RUN"
        and future["candidate_qualified"] is False
        and future["compressed_evidence_owner_count"] == 0
        and future["independent_phase_count"] == 2
        and future["expected_process_count_per_phase"] == 13
        and future["expected_process_count_only_after_both_phases"] == 26
        and future["independent_source_owners_per_phase"] == 3
        and future["native_roles_per_phase"] == ["engine", "bridge"]
        and future["phase_names"] == ["reference-a", "reference-b"]
        and future["process_roles_per_phase"] == list(PROCESS_ROLES)
        and future["full_native_elf_audit"] == "NOT RUN"
        and future["byte_identical_engine_and_bridge"] == "NOT MEASURED"
        and future["receipts_are_exclusive_plaintext_json"] is True
        and future["private_root_mode"] == "0700"
        and future["private_source_mode"] == "0600"
        and future["failure_cleanup_restricts_exact_owned_private_root"] is True
        and type(future["planned_commands"]) is list,
        "show 26 native processes as future plans, never as completed evidence",
    )
    effects = contract["source_only_effects"]
    base.need(
        type(effects) is dict
        and set(effects) == EFFECT_KEYS
        and all(effects[key] == 0 for key in EFFECT_KEYS),
        "forbid any compiler, candidate, archive, timer, holdout, or network",
    )
    toolchain = contract["offline_toolchain"]
    base.need(
        type(toolchain) is dict
        and set(toolchain)
        == {
            "compiler_binaries_executed",
            "lock",
            "network_requests",
            "owners",
            "zig_exact_executable",
            "zig_version",
        }
        and toolchain["compiler_binaries_executed"] == 0
        and toolchain["network_requests"] == 0
        and toolchain["zig_exact_executable"]
        == "/tmp/zig-x86_64-linux-0.16.0/zig"
        and toolchain["zig_version"] == "0.16.0",
        "retain exact offline compiler provenance without running a compiler",
    )
    owners = contract["frozen_source_owners"]
    base.need(
        type(owners) is list
        and len(owners) == 18
        and all(type(owner) is dict and set(owner) == OWNER_KEYS for owner in owners)
        and {owner["path"] for owner in owners} == EXPECTED_SOURCE_OWNER_PATHS
        and len({owner["path"] for owner in owners}) == 18
        and all(
            owner["device"] == 2064
            and owner["nlink"] == 1
            and owner["mode"] == "0600"
            and owner["uid"] == os.geteuid()
            for owner in owners
        ),
        "retain all exact first-party source descriptions without opening them",
    )
    owner_map = {owner["path"]: owner for owner in owners}
    base.need(
        owner_map["GOAL.md"]["sha256"]
        == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        "retain the complete immutable objective without modifying or reading it",
    )
    for role, item in V84.items():
        validate_owner(base, owner_map[item[0]], item, "frozen graph " + role)
    validate_owner(
        base,
        owner_map[previous.RECEIPT[0]],
        previous.RECEIPT,
        "actual V15 full receipt provenance",
    )
    base.need(
        contract["holdout"] == "NOT OPENED"
        and contract["memory"] == "NOT MEASURED"
        and contract["performance"] == "NOT MEASURED"
        and contract["undefined_behavior"] == "NOT MEASURED"
        and contract["qualified_candidate_count"] == 0
        and contract["winner_selected"] is False,
        "never invent a source-only winner, complete matcher, or speed claim",
    )


def load_contract(
    base: types.ModuleType,
    previous: types.ModuleType,
    v83: types.ModuleType,
    old: dict,
) -> dict:
    for role, item in FEATURE.items():
        read_fixed(item, "whole final independently released Zig V13 " + role)
    raw = read_fixed(FEATURE["contract"], "complete final Zig V13 contract")
    contract = base.document(raw, "whole canonical first-party Zig V13 contract")
    base.need(
        base.canonical(contract) == raw,
        "reject truncated, duplicate-key, or noncanonical Zig source proof",
    )
    validate_contract(base, previous, v83, old, contract)
    return contract


def make_zig_proof(base: types.ModuleType, contract: dict) -> dict:
    phrase = contract["first_party_phrase_repair"]
    future = contract["future_native_build"]
    return {
        "schema": SCHEMA + "-zig-first-party-scanner-source-build-v13",
        "version": 13,
        "complete_feature_contract": copy.deepcopy(contract),
        "owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        },
        "independent_feature_source_owner_count": 3,
        "first_party_zig_parser_compiler_executor": copy.deepcopy(
            phrase["first_party_zig_parser_compiler_executor"]
        ),
        "first_party_cpython_c_api_bridge": copy.deepcopy(
            phrase["first_party_cpython_c_api_bridge"]
        ),
        "candidate_family": "zig",
        "additional_candidate_family_count": 0,
        "source_status": contract["status"],
        "future_build_status": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "actual_native_build_process_count": 0,
        "actual_native_activations": 0,
        "planned_independent_build_phase_count": future[
            "independent_phase_count"
        ],
        "planned_process_count_after_both_phases_only": future[
            "expected_process_count_only_after_both_phases"
        ],
        "first_party_only": True,
        "external_regex_packages": 0,
        "cross_candidate_regex_engines": 0,
        "stdlib_regex_engine_dependencies": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def make_zig_pool(base: types.ModuleType, proof: dict) -> dict:
    raw = base.canonical(proof)
    digest = base.digest(raw)
    return {
        "schema": ZIG_POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "entries": {
            digest: {
                "proof_key": ZIG_KEY,
                "proof_schema": proof["schema"],
                "canonical_sha256": digest,
                "canonical_bytes": len(raw),
                "complete_proof": copy.deepcopy(proof),
            },
        },
    }


def validate_zig_pool(base: types.ModuleType, pool: object, proof: dict) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {"schema", "version", "hash_algorithm", "entries"}
        and pool["schema"] == ZIG_POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and type(pool["entries"]) is dict
        and len(pool["entries"]) == 1,
        "require exactly one complete canonical first-party Zig source proof",
    )
    assert isinstance(pool, dict)
    digest, entry = next(iter(pool["entries"].items()))
    raw = base.canonical(proof)
    base.need(
        base.checked(digest, "complete canonical first-party Zig proof")
        == base.digest(raw)
        and type(entry) is dict
        and set(entry)
        == {
            "proof_key",
            "proof_schema",
            "canonical_sha256",
            "canonical_bytes",
            "complete_proof",
        }
        and entry["proof_key"] == ZIG_KEY
        and entry["proof_schema"] == proof["schema"]
        and entry["canonical_sha256"] == digest
        and entry["canonical_bytes"] == len(raw)
        and base.canonical(entry["complete_proof"]) == raw,
        "reject omitted, invented, swapped, or incomplete Zig source evidence",
    )


def make_zig_reference(base: types.ModuleType, pool: dict, proof: dict) -> dict:
    validate_zig_pool(base, pool, proof)
    raw = base.canonical(proof)
    return {
        "schema": ZIG_REFERENCE_SCHEMA,
        "proof_key": ZIG_KEY,
        "sha256": base.digest(raw),
        "canonical_bytes": len(raw),
    }


def resolve_zig_reference(
    base: types.ModuleType,
    pool: dict,
    reference: object,
) -> dict:
    base.need(
        type(reference) is dict
        and set(reference) == {"schema", "proof_key", "sha256", "canonical_bytes"}
        and reference["schema"] == ZIG_REFERENCE_SCHEMA
        and reference["proof_key"] == ZIG_KEY
        and type(reference["canonical_bytes"]) is int
        and reference["canonical_bytes"] > 0,
        "reject an omitted or cross-family whole first-party Zig reference",
    )
    assert isinstance(reference, dict)
    digest = base.checked(reference["sha256"], "whole first-party Zig reference")
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == ZIG_KEY
        and entry.get("canonical_sha256") == digest
        and entry.get("canonical_bytes") == reference["canonical_bytes"]
        and type(entry.get("complete_proof")) is dict,
        "reject unbound, miscounted, or fabricated full Zig source proof",
    )
    raw = base.canonical(entry["complete_proof"])
    base.need(
        len(raw) == reference["canonical_bytes"]
        and base.digest(raw) == digest
        and entry["proof_schema"] == entry["complete_proof"].get("schema"),
        "recompute every byte of the whole independent Zig source reference",
    )
    return copy.deepcopy(entry["complete_proof"])


def make_changes(proof: dict) -> tuple[dict, dict]:
    zig = {
        "zig_v13_first_party_source_build_status":
            "SOURCE FROZEN; CORRECTED ZIG BUILD NOT RUN",
        "zig_v13_first_party_source_build_candidate_matching": "NOT RUN",
        "zig_v13_first_party_source_build_candidate_qualified": False,
        "zig_v13_first_party_source_build_actual_process_count": 0,
        "zig_v13_first_party_source_build_actual_build_receipt_count": 0,
        "zig_v13_first_party_source_build_actual_native_activations": 0,
        "zig_v13_first_party_source_build_planned_phase_count": 2,
        "zig_v13_first_party_source_build_planned_total_process_count": 26,
        "zig_v13_first_party_source_build_planned_processes_are_actual": False,
        "zig_v13_first_party_source_build_runtime_no_delegation":
            "NOT ESTABLISHED",
        "zig_v13_first_party_source_build_external_regex_packages": 0,
        "zig_v13_first_party_source_build_cross_candidate_engines": 0,
        "zig_v13_first_party_source_build_stdlib_regex_engine_dependencies": 0,
        "zig_v13_first_party_source_build_performance": "NOT MEASURED",
        "zig_v13_first_party_source_build_holdout": "NOT OPENED",
    }
    changes = {
        "actual_current_graph_predecessor_version": 84,
        "authenticated_evidence_owner_lower_bound": 275,
        "authenticated_history_reference_lower_bound": 280,
        ZIG_KEY: copy.deepcopy(proof),
        **copy.deepcopy(zig),
    }
    return changes, zig


def validate_families(
    base: types.ModuleType,
    previous: types.ModuleType,
    v83: types.ModuleType,
    families: object,
    originals: list,
    historical_pool: dict,
    actual_pool: dict,
    zig_pool: dict,
    historical_documents: dict,
    actual: dict,
    proof: dict,
    zig_changes: dict,
) -> None:
    v83.validate_pool(base, historical_pool, historical_documents)
    previous.validate_actual_pool(base, actual_pool, actual)
    validate_zig_pool(base, zig_pool, proof)
    base.need(
        type(families) is list
        and type(originals) is list
        and len(families) == len(originals) == 7
        and [row.get("family") for row in families if type(row) is dict]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve Python and all six genuinely independently built families",
    )
    for row, original in zip(families, originals, strict=True):
        base.need(
            type(row) is dict
            and type(original) is dict
            and row["family"] == original["family"],
            "reject added, removed, reordered, or aliased candidate families",
        )
        if row["family"] == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "retain the exact unmodified Python compatibility baseline",
            )
            continue
        for key in v83.PROOF_KEYS:
            base.need(
                base.canonical(row[key]) == base.canonical(original[key])
                and base.canonical(
                    v83.resolve_reference(base, historical_pool, row[key], key)
                ) == base.canonical(historical_documents[key]),
                "preserve all 54 canonical historical references in "
                + row["family"]
                + ": "
                + key,
            )
        base.need(
            base.canonical(row[previous.ACTUAL_KEY])
            == base.canonical(original[previous.ACTUAL_KEY])
            and base.canonical(
                previous.resolve_actual_reference(
                    base, actual_pool, row[previous.ACTUAL_KEY]
                )
            ) == base.canonical(actual),
            "retain every complete real Rust-result reference in " + row["family"],
        )
        base.need(
            base.canonical(resolve_zig_reference(base, zig_pool, row.get(ZIG_KEY)))
            == base.canonical(proof),
            "bind the complete unbuilt first-party Zig source in " + row["family"],
        )
        expected = copy.deepcopy(original)
        expected["authenticated_evidence_owner_lower_bound"] = 275
        expected["authenticated_history_reference_lower_bound"] = 280
        expected[ZIG_KEY] = make_zig_reference(base, zig_pool, proof)
        if row["family"] == "zig":
            expected.update(copy.deepcopy(zig_changes))
        base.need(
            base.canonical(row) == base.canonical(expected),
            "prove complete exact V85 family reconstruction: " + row["family"],
        )
        restored = copy.deepcopy(row)
        restored.pop(ZIG_KEY)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if row["family"] == "zig":
            for key in zig_changes:
                if key in original:
                    restored[key] = copy.deepcopy(original[key])
                else:
                    restored.pop(key)
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore every complete pushed V84 family byte: " + row["family"],
        )
        base.need(
            row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "never qualify or benchmark an unbuilt first-party family: "
            + row["family"],
        )


def make_svg() -> bytes:
    rows = (
        ("Python re", "Original compatibility reference", "BASELINE", "#22c55e"),
        (
            "Rust",
            "12,942 verified checks; 8 of 13 groups completed",
            "5 GROUPS FAILED",
            "#fb7185",
        ),
        ("C", "1,230 previously observed differences", "NOT COMPATIBLE", "#f59e0b"),
        (
            "Zig",
            "Own Zig engine and Python bridge; corrected build not run",
            "SOURCE FROZEN",
            "#60a5fa",
        ),
        ("C++", "2,308 differences; five startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Complete Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="748" viewBox="0 0 1260 748" role="img" aria-labelledby="title description">',
        '<title id="title">Python compared with six from-scratch regular-expression engines</title>',
        '<desc id="description">Python is the reference. Zig has its own first-party parser, compiler and execution engine and its own Python C-API bridge. Its corrected source has been frozen, but the native engine has not yet been built or tested; two build phases and twenty-six processes are future plans only. The real Rust result remains thirteen distinct workers, eight completed test groups, twelve thousand nine hundred forty-two explicitly verified original checks, and five infrastructure failures. An observed cleanup warning is not presented as the underlying cause. Every prior test, receipt, and independent engine is retained. No engine is qualified and no speed measurement or final holdout has been opened.</desc>',
        '<rect width="1260" height="748" rx="18" fill="#0b1220"/>',
        '<text x="34" y="48" fill="#f8fafc" font-size="26" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="81" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="104" x2="1226" y2="104" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 142 + 47 * index
        parts.extend((
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1208" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ))
    parts.extend((
        '<line x1="34" y1="462" x2="1226" y2="462" stroke="#334155"/>',
        '<text x="34" y="493" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate additional checks.</text>',
        '<text x="34" y="522" fill="#93c5fd" font-size="14" font-family="system-ui,sans-serif">Zig: independently written parser, compiler, matcher, and Python bridge; source frozen.</text>',
        '<text x="34" y="550" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Corrected Zig native build and compatibility checks: NOT RUN. No external regex engine or fallback.</text>',
        '<text x="34" y="578" fill="#fcd34d" font-size="13" font-family="system-ui,sans-serif">Actual Rust: 12,942 explicitly verified cases, 8/13 completed groups, and 5 failures.</text>',
        '<text x="34" y="606" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Observed Rust cleanup warning is not proof of the underlying original-test failure cause.</text>',
        '<text x="34" y="634" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">All original results and complete outcome receipts remain independently reproducible.</text>',
        '<text x="34" y="662" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Speed, memory, and runtime independence: NOT MEASURED or NOT ESTABLISHED.</text>',
        '<text x="34" y="691" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Final 4,194,304-case comparison: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="728" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 85 · genuine first-party Zig source · no selected winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def build(
    previous: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None and options.source_bytes is not None,
        "caller-pin the complete exact first-party Zig V85 graph source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "complete actual V85 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V84.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin exact whole committed V84 " + role,
        )
    for role, item in FEATURE.items():
        base.need(
            getattr(options, "feature_" + role + "_sha256") == item[1],
            "caller-pin complete independent Zig V13 " + role,
        )
    old, previous_inputs = authenticate_previous(previous, v83, v82, chain, base)
    contract = load_contract(base, previous, v83, old)
    proof = make_zig_proof(base, contract)
    zig_pool = make_zig_pool(base, proof)
    validate_zig_pool(base, zig_pool, proof)
    historical_pool = copy.deepcopy(old["lossless_family_evidence_pool"])
    actual_pool = copy.deepcopy(old["lossless_actual_outcome_evidence_pool"])
    historical_documents = {
        key: copy.deepcopy(old[key]) for key in v83.PROOF_KEYS
    }
    actual = copy.deepcopy(old[previous.ACTUAL_KEY])
    v83.validate_pool(base, historical_pool, historical_documents)
    previous.validate_actual_pool(base, actual_pool, actual)
    base.need(
        base.canonical(historical_pool)
        == base.canonical(old["lossless_family_evidence_pool"])
        and base.canonical(actual_pool)
        == base.canonical(old["lossless_actual_outcome_evidence_pool"]),
        "preserve every byte of both complete independently owned V84 pools",
    )
    changes, zig_changes = make_changes(proof)
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v84_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V84.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 85,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 275
        row["authenticated_history_reference_lower_bound"] = 280
        row[ZIG_KEY] = make_zig_reference(base, zig_pool, proof)
        if row["family"] == "zig":
            row.update(copy.deepcopy(zig_changes))
    validate_families(
        base,
        previous,
        v83,
        families,
        old["families"],
        historical_pool,
        actual_pool,
        zig_pool,
        historical_documents,
        actual,
        proof,
        zig_changes,
    )
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 85,
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
        "lossless_family_evidence_pool": historical_pool,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_family_references_per_family": 9,
        "lossless_actual_outcome_evidence_pool": actual_pool,
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_actual_outcome_references_per_family": 1,
        "lossless_zig_source_evidence_pool": zig_pool,
        "lossless_zig_source_evidence_pool_schema": ZIG_POOL_SCHEMA,
        "lossless_zig_source_evidence_pool_entry_count": 1,
        "lossless_zig_source_references_per_family": 1,
        "lossless_zig_source_reconstruction_status": "PASS",
        "lossless_v84_family_previous_byte_identity_status": "PASS",
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
        "retain every original historical Rust suite and real mismatch witness",
    )
    for label, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        campaign = layer["actual_complete_rust_campaign"]
        base.need(
            campaign["complete_independently_authenticated_suite_results"]
            == suites
            and campaign["earliest_genuine_mismatch_witnesses"] == witnesses
            and all(
                base.canonical(layer[key])
                == base.canonical(historical_documents[key])
                for key in v83.PROOF_KEYS
            )
            and base.canonical(layer[previous.ACTUAL_KEY])
            == base.canonical(actual)
            and base.canonical(layer[ZIG_KEY]) == base.canonical(proof)
            and layer["rust_v12_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v13_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v14_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v15_original_campaign_candidate_matching"] == "FAIL"
            and layer["rust_v15_original_campaign_actual_worker_count"] == 13
            and layer["rust_v15_original_campaign_completed_suite_count"] == 8
            and layer["rust_v15_original_campaign_verified_passing_case_count"]
            == 12942
            and layer["rust_v15_original_campaign_infrastructure_failure_count"]
            == 5
            and layer["rust_v15_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer[
                "rust_v15_original_campaign_pattern_destructor_proven_failure_cause"
            ] is False
            and layer["zig_v13_first_party_source_build_candidate_matching"]
            == "NOT RUN"
            and layer["zig_v13_first_party_source_build_candidate_qualified"]
            is False
            and layer["zig_v13_first_party_source_build_actual_process_count"]
            == 0,
            "retain the entire actual history and unbuilt Zig truth in " + label,
        )
    base.need(
        base.canonical(summary["lossless_family_evidence_pool"])
        == base.canonical(old["lossless_family_evidence_pool"])
        and base.canonical(summary["lossless_actual_outcome_evidence_pool"])
        == base.canonical(old["lossless_actual_outcome_evidence_pool"])
        and summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_rust_verified_passing_case_count"] == 14853
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_c_verified_passing_case_count"] == 7325
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["actual_zig_verified_passing_case_count"] == 3711
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["final_holdout_opened"] is False,
        "never remove actual results or fabricate Zig compatibility or speed",
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
            "reject partial or oversized Zig evidence BEFORE publishing " + path,
        )
    return snapshot, assets


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only complete, bounded, and uniquely created V85 owners",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0, "write every V85 byte")
            remaining = remaining[count:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "authenticate the exact complete V85 output identity",
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
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "verify all complete first-party V85 graph bytes")


def self_test(
    previous: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(v83, v82, chain, base)
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 84
        and prior["authenticated_evidence_owner_lower_bound"] == 272
        and prior["authenticated_history_reference_lower_bound"] == 277
        and prior["lossless_family_evidence_pool_entry_count"] == 9
        and prior["lossless_family_references_per_family"] == 9
        and prior["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and prior["lossless_actual_outcome_references_per_family"] == 1
        and prior["previous_v12_actual_rust_infrastructure_failure_count"] == 13
        and prior["previous_v13_actual_rust_infrastructure_failure_count"] == 13
        and prior["previous_v14_actual_rust_infrastructure_failure_count"] == 13
        and prior["actual_v15_candidate_worker_count"] == 13
        and prior["actual_v15_completed_suite_count"] == 8
        and prior["actual_v15_verified_passing_case_count"] == 12942
        and prior["actual_v15_infrastructure_failure_count"] == 5
        and prior["actual_v15_semantic_mismatch_count"] == "NOT MEASURED"
        and prior["actual_v15_pattern_destructor_proven_failure_cause"] is False
        and prior["actual_candidate_workers_started_by_graph"] == 0
        and prior["actual_compressed_evidence_owners_opened_by_graph"] == 0
        and prior["actual_clock_samples_by_graph"] == 0
        and prior["runtime_no_delegation"] == "NOT ESTABLISHED"
        and prior["qualified_candidate_count"] == 0
        and prior["final_holdout_opened"] is False,
        "inherit all 8,298 adversarial checks and complete V84 actual results",
    )
    old, _ = authenticate_previous(previous, v83, v82, chain, base)
    contract = load_contract(base, previous, v83, old)
    proof = make_zig_proof(base, contract)
    zig_pool = make_zig_pool(base, proof)
    historical_pool = copy.deepcopy(old["lossless_family_evidence_pool"])
    actual_pool = copy.deepcopy(old["lossless_actual_outcome_evidence_pool"])
    historical_documents = {key: copy.deepcopy(old[key]) for key in v83.PROOF_KEYS}
    actual = copy.deepcopy(old[previous.ACTUAL_KEY])
    _, zig_changes = make_changes(proof)
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 275
        row["authenticated_history_reference_lower_bound"] = 280
        row[ZIG_KEY] = make_zig_reference(base, zig_pool, proof)
        if row["family"] == "zig":
            row.update(copy.deepcopy(zig_changes))
    validate_families(
        base,
        previous,
        v83,
        families,
        old["families"],
        historical_pool,
        actual_pool,
        zig_pool,
        historical_documents,
        actual,
        proof,
        zig_changes,
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
            base.need(False, "accepted fabricated first-party Zig proof: " + label)

    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        reject(
            "removed complete Zig contract field " + key,
            lambda candidate=forged: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    for key, value in (
        ("schema", "external-regex-wrapper"),
        ("version", 12),
        ("status", "NATIVE BUILD PASS"),
        ("phase", "COMPLETED NATIVE MATCHING"),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("qualified_candidate_count", 1),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = value
        reject(
            "invented source-only Zig result " + key,
            lambda candidate=forged: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    for key, value in (
        ("version", 83),
        ("authenticated_evidence_owner_lower_bound", 273),
        ("authenticated_history_reference_lower_bound", 278),
        ("prospective_evidence_owner_lower_bound", 276),
        ("prospective_history_reference_lower_bound", 281),
        ("prospective_independent_feature_source_owner_count", 4),
        ("source_freeze_new_evidence_owner_count", 1),
        ("lower_bounds_are_complete_repository_census", True),
    ):
        forged = copy.deepcopy(contract)
        forged["current_graph"][key] = value
        reject(
            "fabricated pushed V84 graph context " + key,
            lambda candidate=forged: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    for key in sorted(POLICY_KEYS - {"runtime_non_delegation"}):
        forged = copy.deepcopy(contract)
        forged["from_scratch_policy"][key] = "PERMITTED"
        reject(
            "weakened independent no-delegation boundary " + key,
            lambda candidate=forged: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    forged = copy.deepcopy(contract)
    forged["from_scratch_policy"]["runtime_non_delegation"] = "PASS"
    reject(
        "fabricated runtime independence",
        lambda: validate_contract(base, previous, v83, old, forged),
    )
    for key in sorted(EFFECT_KEYS):
        forged_effect = copy.deepcopy(contract)
        forged_effect["source_only_effects"][key] = 1
        reject(
            "executed forbidden source-only Zig effect " + key,
            lambda candidate=forged_effect: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    for key, value in (
        ("status", "PASS"),
        ("authorization", "AUTOMATIC"),
        ("actual_build_receipt_count", 1),
        ("actual_private_root_receipt_count", 1),
        ("actual_process_count", 26),
        ("actual_source_snapshot_count", 1),
        ("candidate_correctness", "PASS"),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("compressed_evidence_owner_count", 1),
        ("independent_phase_count", 1),
        ("expected_process_count_per_phase", 26),
        ("expected_process_count_only_after_both_phases", 13),
        ("independent_source_owners_per_phase", 1),
        ("full_native_elf_audit", "PASS"),
        ("byte_identical_engine_and_bridge", True),
        ("receipts_are_exclusive_plaintext_json", False),
        ("failure_cleanup_restricts_exact_owned_private_root", False),
    ):
        forged_future = copy.deepcopy(contract)
        forged_future["future_native_build"][key] = value
        reject(
            "fabricated unrun future Zig native build " + key,
            lambda candidate=forged_future: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    for key, value in (
        ("family", "python"),
        ("version", 3),
        ("additional_candidate_family_count", 1),
        ("corrected_candidate_matching", "PASS"),
        ("original_adapter_modified", True),
        ("original_bridge_modified", True),
        ("original_engine_modified", True),
        ("complete_original_scanner_matrix_case_count", 1023),
        ("preserved_original_scanner_case_count", 959),
        ("corrected_source_witness_count", 63),
        ("scanner_matrix_sha256", "0" * 64),
    ):
        forged_phrase = copy.deepcopy(contract)
        forged_phrase["first_party_phrase_repair"][key] = value
        reject(
            "weakened first-party Zig source or oracle " + key,
            lambda candidate=forged_phrase: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    for field in (
        "first_party_zig_parser_compiler_executor",
        "first_party_cpython_c_api_bridge",
        "complete_corrected_adapter",
        "unchanged_original_adapter",
    ):
        forged_owner = copy.deepcopy(contract)
        forged_owner["first_party_phrase_repair"][field]["sha256"] = "0" * 64
        reject(
            "substituted independent first-party native source " + field,
            lambda candidate=forged_owner: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    for key, value in (
        ("actual_candidate_worker_count", 8),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", 31237),
        ("infrastructure_failure_count", 0),
        ("semantic_mismatch_count", 0),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("publication_is_candidate_correctness", True),
        ("publication_pass_means", "CANDIDATE PASS"),
        ("matching_archive_opened", True),
    ):
        forged_rust = copy.deepcopy(contract)
        forged_rust["preserved_actual_history"][
            "actual_rust_v15_original_matching"
        ][key] = value
        reject(
            "fabricated real Rust actual evidence " + key,
            lambda candidate=forged_rust: validate_contract(
                base, previous, v83, old, candidate
            ),
        )
    reject("removed complete Zig source pool", lambda: validate_zig_pool(base, None, proof))
    zig_digest = next(iter(zig_pool["entries"]))
    for key, value in (
        ("schema", "invented-zig-pool"),
        ("version", 2),
        ("hash_algorithm", "sha1"),
    ):
        forged_pool = copy.deepcopy(zig_pool)
        forged_pool[key] = value
        reject(
            "fabricated complete source pool " + key,
            lambda candidate=forged_pool: validate_zig_pool(base, candidate, proof),
        )
    for key, value in (
        ("proof_key", "borrowed-engine"),
        ("proof_schema", "external-package"),
        ("canonical_sha256", "0" * 64),
        ("canonical_bytes", 1),
    ):
        forged_pool = copy.deepcopy(zig_pool)
        forged_pool["entries"][zig_digest][key] = value
        reject(
            "swapped complete first-party Zig proof " + key,
            lambda candidate=forged_pool: validate_zig_pool(base, candidate, proof),
        )
    for row in families:
        if row["family"] == "python":
            continue
        for key, value in (
            ("schema", "borrowed-source-reference"),
            ("proof_key", "python-regex"),
            ("sha256", "0" * 64),
            ("canonical_bytes", 1),
        ):
            forged_reference = copy.deepcopy(row[ZIG_KEY])
            forged_reference[key] = value
            reject(
                "foreign first-party family source reference "
                + row["family"]
                + ": "
                + key,
                lambda candidate=forged_reference: resolve_zig_reference(
                    base, zig_pool, candidate
                ),
            )
        forged_families = copy.deepcopy(families)
        forged_row = next(
            item for item in forged_families if item["family"] == row["family"]
        )
        forged_row[previous.ACTUAL_KEY]["sha256"] = "0" * 64
        reject(
            "erased complete actual Rust evidence from " + row["family"],
            lambda candidate=forged_families: validate_families(
                base,
                previous,
                v83,
                candidate,
                old["families"],
                historical_pool,
                actual_pool,
                zig_pool,
                historical_documents,
                actual,
                proof,
                zig_changes,
            ),
        )
    base.need(
        rejected >= 125,
        "reject invented candidate passes, borrowed engines, and hidden losses",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 85,
        "status": "PASS",
        "previous_overview_version": 84,
        "actual_current_graph_predecessor_version": 84,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ] + rejected,
        "authenticated_evidence_owner_lower_bound": 275,
        "authenticated_history_reference_lower_bound": 280,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_family_references_per_family": 9,
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_actual_outcome_references_per_family": 1,
        "lossless_zig_source_evidence_pool_entry_count": 1,
        "lossless_zig_source_references_per_family": 1,
        "lossless_zig_source_reconstruction_status": "PASS",
        "lossless_v84_family_previous_byte_identity_status": "PASS",
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "supplemental_reference_case_count": 8244,
        "previous_v12_actual_rust_infrastructure_failure_count": 13,
        "previous_v13_actual_rust_infrastructure_failure_count": 13,
        "previous_v14_actual_rust_infrastructure_failure_count": 13,
        "actual_v15_candidate_matching": "FAIL",
        "actual_v15_candidate_worker_count": 13,
        "actual_v15_completed_suite_count": 8,
        "actual_v15_verified_passing_case_count": 12942,
        "actual_v15_infrastructure_failure_count": 5,
        "actual_v15_semantic_mismatch_count": "NOT MEASURED",
        "actual_v15_pattern_destructor_proven_failure_cause": False,
        "actual_zig_source_owner_count": 3,
        "actual_zig_build_process_count": 0,
        "actual_zig_candidate_matching": "NOT RUN",
        "actual_zig_candidate_qualified": False,
        "planned_zig_build_phase_count": 2,
        "planned_zig_process_count_after_both_phases_only": 26,
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
    for role in V84:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v83, v82, chain, base = load_previous()
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
                    for role in V84
                )
                and all(
                    getattr(options, "feature_" + role + "_sha256") is None
                    for role in FEATURE
                ),
                "source-only graph self-test must not run Zig or publish owners",
            )
            result = self_test(previous, v83, v82, chain, base)
        else:
            _, assets = build(previous, v83, v82, chain, base, options)
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject fabricated or preexisting first-party V85 owners",
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
                            "complete read-only first-party V85 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reproduce every complete first-party V85 byte: " + role,
                    )
            result = {
                "schema": SCHEMA
                + ("-published" if options.render else "-read-only-frozen-context"),
                "version": 85,
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
                "previous_overview_version": 84,
                "actual_current_graph_predecessor_version": 84,
                "authenticated_evidence_owner_lower_bound": 275,
                "authenticated_history_reference_lower_bound": 280,
                "lossless_family_evidence_pool_entry_count": 9,
                "lossless_family_references_per_family": 9,
                "lossless_actual_outcome_evidence_pool_entry_count": 1,
                "lossless_actual_outcome_references_per_family": 1,
                "lossless_zig_source_evidence_pool_entry_count": 1,
                "lossless_zig_source_references_per_family": 1,
                "lossless_zig_source_reconstruction_status": "PASS",
                "lossless_v84_family_previous_byte_identity_status": "PASS",
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "supplemental_reference_case_count": 8244,
                "actual_v15_candidate_worker_count": 13,
                "actual_v15_completed_suite_count": 8,
                "actual_v15_verified_passing_case_count": 12942,
                "actual_v15_infrastructure_failure_count": 5,
                "actual_v15_semantic_mismatch_count": "NOT MEASURED",
                "actual_zig_source_owner_count": 3,
                "actual_zig_build_process_count": 0,
                "actual_zig_candidate_matching": "NOT RUN",
                "actual_zig_candidate_qualified": False,
                "planned_zig_build_phase_count": 2,
                "planned_zig_process_count_after_both_phases_only": 26,
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
        sys.stderr.write("current V85 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
