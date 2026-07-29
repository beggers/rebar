#!/usr/bin/env python3
"""Freeze diagnostic-preserving Rust workers without hiding either real failure."""

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
SELF = "tools/render_candidate_current_overview_v81.py"
OUTPUT = "docs/evidence/candidate-current-overview-v81"
SCHEMA = "rebar-candidate-current-overview-v81"
V80 = {
    "source": (
        "tools/render_candidate_current_overview_v80.py",
        "8454705356bffd9e3c576b24df9ab8e572aff96c401ed60bd74657c8b5a1dd5a",
        57094,
        431526,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v80.inputs.json",
        "5f881e270b5080f1579e79ac16e79a5a53a905d1e708b7b47e2ea1c68a02ea19",
        1229041,
        431527,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v80.json",
        "21d0e0fc7c9603d7a2e83a66deb549947481334a8b51d65fff2d82038628f19d",
        3852490,
        431528,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v80.svg",
        "28fbe95147ca9dbf9d4a5874f6efa0d8d0f5ffc439c61d1f7bb361224a907547",
        5298,
        431529,
    ),
}
FEATURE = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v14.py",
        "8115b05911d47c0d22a6cb85a405e91b26c00921112494d6317e5a5853d5c99e",
        88399,
        431547,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V14.md",
        "ac7700fab0576a2856ff38e6ac7ad1d0f2a5f0c6e5a0207012518f13f8fe11a2",
        13686,
        525068,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v14.json",
        "fc1ecfaa8eb9663c874bffe70746d6aa76d9de21ad49552ace65dd9f46da15e3",
        10502,
        525069,
    ),
}
CONTRACT_SCHEMA = (
    "rebar-owned-repaired-rust-original-campaign-v14-"
    "recoverable-source-freeze"
)
CONTRACT_KEYS: frozenset[str] = frozenset({
    "actual_build_archive_inflations",
    "actual_build_archive_opens",
    "actual_c_semantic_mismatch_count",
    "actual_c_verified_passing_case_count",
    "actual_candidate_imports",
    "actual_candidate_workers_started",
    "actual_clock_samples",
    "actual_compiler_processes_started",
    "actual_controller_dispatch",
    "actual_hidden_cases_read",
    "actual_native_libraries_loaded",
    "actual_private_build_root_opens",
    "actual_private_build_root_stats",
    "actual_recovery_dispatch",
    "actual_v19_build_archive_metadata_bytes",
    "actual_v19_build_archive_metadata_sha256",
    "actual_v19_build_contract_sha256",
    "actual_v19_build_label",
    "actual_v19_build_protocol_sha256",
    "actual_v19_build_receipt_sha256",
    "actual_v19_build_source_sha256",
    "actual_v19_compiler_process_count",
    "actual_v19_native_bridge_bytes",
    "actual_v19_native_bridge_sha256",
    "actual_v19_native_engine_bytes",
    "actual_v19_native_engine_sha256",
    "actual_v19_private_build_root",
    "actual_v19_private_build_root_device",
    "actual_v19_private_build_root_inode",
    "actual_v19_private_build_root_provenance",
    "actual_v19_root_receipt_sha256",
    "actual_v19_source_build_phase_count",
    "actual_worker_bootstrap",
    "actual_worker_dispatch",
    "candidate_correctness",
    "candidate_matching",
    "candidate_qualified",
    "case_execution_denominator",
    "confidence_intervals",
    "corrected_original_producer_contract_sha256",
    "corrected_original_producer_protocol_sha256",
    "corrected_original_producer_source_sha256",
    "corrected_original_producer_version",
    "cpython_executable",
    "cpython_executable_sha256",
    "cpython_version",
    "current_evidence_owner_lower_bound",
    "current_history_reference_lower_bound",
    "frozen_graph_inputs_sha256",
    "frozen_graph_source_sha256",
    "frozen_graph_summary_sha256",
    "frozen_graph_svg_sha256",
    "frozen_graph_version",
    "frozen_worker_implementation_source",
    "frozen_worker_implementation_source_sha256",
    "goal_sha256",
    "historical_ctypes_preloaded",
    "historical_ctypes_proxy_native_load_permitted",
    "historical_ctypes_source_count",
    "historical_ctypes_sources",
    "historical_ctypes_transforms_executed",
    "historical_original_v4_producer_source_sha256",
    "historical_rust_semantic_mismatch_count",
    "historical_rust_verified_passing_case_count",
    "holdout",
    "memory",
    "named_private_waivers",
    "performance",
    "phase1_v4_reference_readiness",
    "phase2_candidate_qualification",
    "planned_actual_original_candidate_worker_count",
    "previous_v13_contract_sha256",
    "previous_v13_protocol_sha256",
    "previous_v13_source_sha256",
    "private_waiver_count",
    "prospective_evidence_owner_lower_bound",
    "prospective_history_reference_lower_bound",
    "protocol_sha256",
    "public_recovery_root",
    "qualified_candidate_count",
    "recovery_lock_filename",
    "recovery_restoration_order",
    "recovery_role_order",
    "reference_cache_records_sha256",
    "reference_records_sha256",
    "reference_worker_process_ids",
    "runtime_guard_contract_sha256",
    "runtime_guard_installation",
    "runtime_guard_protocol_sha256",
    "runtime_guard_source_sha256",
    "runtime_non_delegation",
    "schema",
    "source_sha256",
    "status",
    "suite_count",
    "suites",
    "supplemental_case_count",
    "supplemental_cases_counted_in_original_denominator",
    "timing_trials_run",
    "undefined_behavior",
    "v12_actual_all_four_original_targets_restored",
    "v12_actual_candidate_qualified",
    "v12_actual_candidate_worker_count",
    "v12_actual_completed_suite_count",
    "v12_actual_failure_receipt_bytes",
    "v12_actual_failure_receipt_inode",
    "v12_actual_failure_receipt_sha256",
    "v12_actual_infrastructure_failure_count",
    "v12_actual_semantic_mismatch_count",
    "v12_actual_verified_passing_case_count",
    "v12_contract_sha256",
    "v12_failure_archive_inflated",
    "v12_failure_archive_opened",
    "v12_protocol_sha256",
    "v12_source_sha256",
    "v13_actual_all_four_original_targets_restored",
    "v13_actual_candidate_qualified",
    "v13_actual_candidate_worker_count",
    "v13_actual_completed_suite_count",
    "v13_actual_failure_receipt_bytes",
    "v13_actual_failure_receipt_inode",
    "v13_actual_failure_receipt_sha256",
    "v13_actual_infrastructure_failure_count",
    "v13_actual_semantic_mismatch_count",
    "v13_actual_verified_passing_case_count",
    "v13_failure_archive_inflated",
    "v13_failure_archive_opened",
    "version",
    "winner_selected",
    "worker_failure_capture_attempts",
    "worker_failure_capture_complete",
    "worker_failure_capture_mode",
    "worker_failure_capture_native_loads",
    "worker_failure_capture_processes_started",
    "worker_failure_capture_stream_limit_bytes",
    "worker_failure_capture_total_budget_bytes",
    "worker_failure_capture_traceback_limit_bytes",
})
EXPECTED_GOAL = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
HISTORICAL_CTYPES = (
    (
        "v11",
        "tools/run_owned_repaired_rust_original_campaign_v11.py",
        "27bf88358d5a45a5b487680e70f5fa5b5192a05f053f33f6ddb651c972c94f2d",
        310760,
        430525,
        18,
    ),
    (
        "v7",
        "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        505616,
        431856,
        16,
    ),
    (
        "v2",
        "tools/run_owned_repaired_rust_original_campaign_v2.py",
        "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3",
        143441,
        429079,
        15,
    ),
    (
        "v4",
        "tools/run_owned_six_family_original_p0_producer_v4.py",
        "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        230782,
        431710,
        21,
    ),
)


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
            raise ValueError("reject substituted complete owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject extended complete owner: " + label)
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
            raise ValueError("reject changed complete owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple:
    raw = read_fixed(V80["source"], "actually pushed full V80 actual-loss graph")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v80")
    previous.__file__ = str(ROOT / V80["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    (
        v79, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69,
        modules, base,
    ) = previous.load_previous()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v80"
        and previous.SELF == V80["source"][0],
        "authenticate only the actually pushed complete V80 two-loss graph",
    )
    return (
        previous, v79, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69,
        modules, base,
    )


def authenticate_previous(
    previous: types.ModuleType,
    v79: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    v76: types.ModuleType,
    v75: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V80["source"][1],
        "source_bytes": V80["source"][2],
        "receipt_sha256": previous.RECEIPT[1],
    }
    for role, item in previous.V79.items():
        pins["previous_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v79, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69, modules,
        base, argparse.Namespace(**pins),
    )
    for role in ("inputs", "summary", "svg"):
        item = V80[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole actual V80 " + role),
            "reproduce the actual complete pushed V80 loss " + role,
        )
    old = base.document(assets[V80["summary"][0]], "complete pushed V80")
    inputs = base.document(assets[V80["inputs"][0]], "complete V80 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 80
        and old["actual_current_graph_predecessor_version"] == 79
        and old["authenticated_evidence_owner_lower_bound"] == 262
        and old["authenticated_history_reference_lower_bound"] == 267
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
        and old["rust_v13_original_campaign_candidate_matching"] == "FAIL"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["qualified_candidate_count"] == 0
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "preserve both real 13-worker failures and every prior complete result",
    )
    return old, inputs


def validate_contract(
    base: types.ModuleType,
    previous: types.ModuleType,
    v79: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    contract: object,
) -> None:
    base.need(
        len(CONTRACT_KEYS) >= 95
        and type(contract) is dict
        and set(contract) == CONTRACT_KEYS,
        "reject provisional, omitted, added, or weakened worker-diagnostic proof",
    )
    assert isinstance(contract, dict)
    base.need(
        contract["schema"] == CONTRACT_SCHEMA
        and contract["version"] == 14
        and contract["status"]
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and contract["source_sha256"] == FEATURE["source"][1]
        and contract["protocol_sha256"] == FEATURE["protocol"][1]
        and contract["goal_sha256"] == EXPECTED_GOAL
        and contract["cpython_version"] == "3.14.6"
        and contract["cpython_executable"] == PYTHON
        and contract["cpython_executable_sha256"] == PYTHON_SHA256,
        "require the whole genuine independent V14 diagnostics controller",
    )
    base.need(
        contract["frozen_graph_version"] == 80
        and contract["frozen_graph_source_sha256"] == V80["source"][1]
        and contract["frozen_graph_inputs_sha256"] == V80["inputs"][1]
        and contract["frozen_graph_summary_sha256"] == V80["summary"][1]
        and contract["frozen_graph_svg_sha256"] == V80["svg"][1]
        and contract["current_evidence_owner_lower_bound"] == 262
        and contract["current_history_reference_lower_bound"] == 267
        and contract["prospective_evidence_owner_lower_bound"] == 265
        and contract["prospective_history_reference_lower_bound"] == 270,
        "pin the whole pushed second-failure graph and exactly three source owners",
    )
    base.need(
        contract["corrected_original_producer_version"] == 5
        and contract["corrected_original_producer_source_sha256"]
        == v77.PRODUCER["source"][1]
        and contract["corrected_original_producer_protocol_sha256"]
        == v77.PRODUCER["protocol"][1]
        and contract["corrected_original_producer_contract_sha256"]
        == v77.PRODUCER["contract"][1]
        and contract["runtime_guard_source_sha256"]
        == v77.GUARD["source"][1]
        and contract["runtime_guard_protocol_sha256"]
        == v77.GUARD["protocol"][1]
        and contract["runtime_guard_contract_sha256"]
        == v77.GUARD["contract"][1]
        and contract["runtime_guard_installation"]
        == "REQUIRED BEFORE ANY ACTUAL CANDIDATE IMPORT",
        "retain the complete original oracle and physically unchanged strict guard",
    )
    base.need(
        contract["suite_count"] == 13
        and contract["case_execution_denominator"] == 31237
        and contract["planned_actual_original_candidate_worker_count"] == 13
        and contract["private_waiver_count"] == 13
        and type(contract["named_private_waivers"]) is list
        and len(contract["named_private_waivers"]) == 13
        and contract["supplemental_case_count"] == 8244
        and contract["supplemental_cases_counted_in_original_denominator"]
        is False,
        "retain every original obligation and the separate differential cases",
    )
    suites = contract["suites"]
    base.need(
        type(suites) is list
        and len(suites) == 13
        and [
            (
                row.get("suite", row.get("name", row.get("id"))),
                row.get("case_count", row.get("case_execution_count")),
            )
            for row in suites
        ] == list(v77.SUITES),
        "retain every complete original Python suite and original denominator",
    )
    base.need(
        contract["historical_ctypes_source_count"] == 4
        and type(contract["historical_ctypes_sources"]) is list
        and len(contract["historical_ctypes_sources"]) == 4
        and contract["historical_ctypes_proxy_native_load_permitted"] is False
        and contract["historical_ctypes_preloaded"] is False
        and contract["historical_ctypes_transforms_executed"] == 0,
        "retain all four exact fail-closed historical import transformations",
    )
    for actual, expected in zip(
        contract["historical_ctypes_sources"], HISTORICAL_CTYPES, strict=True
    ):
        role, path, digest, size, inode, import_line = expected
        base.need(
            type(actual) is dict
            and set(actual) == {
                "role", "path", "sha256", "bytes", "inode",
                "exact_top_level_import_line", "transformation",
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
            "reject an altered historical worker-source transformation: " + role,
        )
    base.need(
        contract["previous_v13_source_sha256"] == v79.FEATURE["source"][1]
        and contract["previous_v13_protocol_sha256"]
        == v79.FEATURE["protocol"][1]
        and contract["previous_v13_contract_sha256"]
        == v79.FEATURE["contract"][1]
        and contract["v13_actual_failure_receipt_sha256"]
        == previous.RECEIPT[1]
        and contract["v13_actual_failure_receipt_bytes"]
        == previous.RECEIPT[2]
        and contract["v13_actual_failure_receipt_inode"]
        == previous.RECEIPT[3]
        and contract["v13_actual_candidate_worker_count"] == 13
        and contract["v13_actual_completed_suite_count"] == 0
        and contract["v13_actual_infrastructure_failure_count"] == 13
        and contract["v13_actual_semantic_mismatch_count"] == "NOT MEASURED"
        and contract["v13_actual_verified_passing_case_count"] == 0
        and contract["v13_actual_candidate_qualified"] is False
        and contract["v13_actual_all_four_original_targets_restored"] is True
        and contract["v13_failure_archive_opened"] is False
        and contract["v13_failure_archive_inflated"] is False,
        "retain every actual V13 worker loss without opening its archive",
    )
    base.need(
        contract["v12_source_sha256"] == v77.FEATURE["source"][1]
        and contract["v12_protocol_sha256"] == v77.FEATURE["protocol"][1]
        and contract["v12_contract_sha256"] == v77.FEATURE["contract"][1]
        and contract["v12_actual_failure_receipt_sha256"] == v78.RECEIPT[1]
        and contract["v12_actual_failure_receipt_bytes"] == v78.RECEIPT[2]
        and contract["v12_actual_failure_receipt_inode"] == v78.RECEIPT[3]
        and contract["v12_actual_candidate_worker_count"] == 13
        and contract["v12_actual_completed_suite_count"] == 0
        and contract["v12_actual_infrastructure_failure_count"] == 13
        and contract["v12_actual_semantic_mismatch_count"] == "NOT MEASURED"
        and contract["v12_actual_verified_passing_case_count"] == 0
        and contract["v12_actual_candidate_qualified"] is False
        and contract["v12_actual_all_four_original_targets_restored"] is True
        and contract["v12_failure_archive_opened"] is False
        and contract["v12_failure_archive_inflated"] is False,
        "retain the complete genuine V12 failure and untouched archive",
    )
    base.need(
        contract["worker_failure_capture_mode"]
        == "SCOPED AUTHENTIC CONTROLLER; COMPLETE BOUNDED STDOUT, STDERR, "
        "EXIT AND ACTIVE TRACEBACK"
        and contract["worker_failure_capture_stream_limit_bytes"] == 65536
        and contract["worker_failure_capture_traceback_limit_bytes"] == 65536
        and contract["worker_failure_capture_total_budget_bytes"] == 4194304
        and contract["worker_failure_capture_attempts"] == 0
        and contract["worker_failure_capture_complete"] == "NOT RUN"
        and contract["worker_failure_capture_processes_started"] == 0
        and contract["worker_failure_capture_native_loads"] == 0,
        "require bounded original stdout, stderr, exit and traceback capture",
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
        and contract["historical_original_v4_producer_source_sha256"]
        == HISTORICAL_CTYPES[3][2]
        and contract["frozen_worker_implementation_source"]
        == HISTORICAL_CTYPES[0][1]
        and contract["frozen_worker_implementation_source_sha256"]
        == HISTORICAL_CTYPES[0][2],
        "preserve all historical losses, actual vectors, and exact original source",
    )
    base.need(
        contract["actual_controller_dispatch"]
        == "AUTHENTICATED V11 run_campaign"
        and contract["actual_worker_dispatch"]
        == "AUTHENTICATED V11 run_original_worker"
        and contract["actual_recovery_dispatch"]
        == "AUTHENTICATED V11 recover_originals"
        and contract["actual_worker_bootstrap"]
        == "CPython -I -B -S; audit hook before candidate import"
        and contract["recovery_role_order"] == list(v77.ROLE_ORDER)
        and contract["recovery_restoration_order"]
        == list(reversed(v77.ROLE_ORDER))
        and contract["public_recovery_root"]
        == "/tmp/rebar-phase2-repaired-rust-original-campaign-v14-"
        "phase2-v19-rust-buffer-shape-root-provenance-original-p0"
        and contract["recovery_lock_filename"]
        == "recoverable-controller-v14.lock",
        "preserve all exact historical original workers and four-role recovery",
    )
    base.need(
        contract["actual_v19_build_source_sha256"]
        == "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c"
        and contract["actual_v19_build_protocol_sha256"]
        == "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5"
        and contract["actual_v19_build_contract_sha256"]
        == "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46"
        and contract["actual_v19_build_receipt_sha256"]
        == "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc"
        and contract["actual_v19_root_receipt_sha256"]
        == "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99"
        and contract["actual_v19_build_archive_metadata_sha256"]
        == "c4e3971fc207af50081d920a98d29dc06b5bdce07c5e1fb19e3e6fdf99a1c1bb"
        and contract["actual_v19_build_archive_metadata_bytes"] == 108250
        and contract["actual_v19_build_label"]
        == "phase2-v19-rust-buffer-shape-root-provenance"
        and contract["actual_v19_compiler_process_count"] == 28
        and contract["actual_v19_source_build_phase_count"] == 2
        and contract["actual_v19_private_build_root_provenance"]
        == "AUTHENTICATED RECEIPT ONLY; NOT OPENED"
        and contract["actual_v19_private_build_root"]
        == "/tmp/rebar-phase2-native-build-v9-rust-9m_y1apm"
        and contract["actual_v19_private_build_root_device"] == 2049
        and contract["actual_v19_private_build_root_inode"] == 11673243
        and contract["actual_v19_native_engine_sha256"]
        == "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
        and contract["actual_v19_native_engine_bytes"] == 658344
        and contract["actual_v19_native_bridge_sha256"]
        == "7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4"
        and contract["actual_v19_native_bridge_bytes"] == 148832,
        "require the genuine independent native build by receipt only",
    )
    base.need(
        contract["candidate_correctness"] == "NOT MEASURED"
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
        "never portray diagnostic source as real matching, speed, or runtime proof",
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
        base.need(contract[key] == 0, "source-only actual effect: " + key)


def make_svg() -> bytes:
    rows = (
        ("Python re", "All original reference checks pass", "BASELINE", "#22c55e"),
        (
            "Rust",
            "Two retests each had 13 startup failures; diagnostics fix ready",
            "NOT RETESTED",
            "#f59e0b",
        ),
        ("C", "1,230 earlier differences; corrected build passes", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "1,764 earlier differences; scanner fix not retested", "NOT COMPATIBLE", "#f59e0b"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility has not been tested", "NOT TESTED", "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="670" viewBox="0 0 1160 670" role="img" aria-labelledby="title description">',
        '<title id="title">Python and six independently written regular-expression engines</title>',
        '<desc id="description">Two actual Rust retests each produced thirteen worker failures with no recorded child error. A diagnostics-preserving source fix is ready but has not run. All six independent candidates remain unqualified; speed is unmeasured and the expanded holdout remains closed.</desc>',
        '<rect width="1160" height="670" rx="18" fill="#0b1220"/>',
        '<text x="34" y="48" fill="#f8fafc" font-size="26" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="81" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully qualified · speed NOT MEASURED</text>',
        '<line x1="34" y1="104" x2="1126" y2="104" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 142 + 47 * index
        parts.extend((
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1108" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ))
    parts.extend((
        '<line x1="34" y1="462" x2="1126" y2="462" stroke="#334155"/>',
        '<text x="34" y="493" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate extra checks.</text>',
        '<text x="34" y="521" fill="#fda4af" font-size="14" font-family="system-ui,sans-serif">Both actual Rust retests: 13 startup failures; 0 completed test groups each.</text>',
        '<text x="34" y="549" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Original child failure: NOT RECORDED. Diagnostics-preserving correction: SOURCE READY.</text>',
        '<text x="34" y="577" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Corrected complete retest: NOT RUN. No relaxed guard or Python or external matcher.</text>',
        '<text x="34" y="605" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Compatibility, speed, and memory: NOT MEASURED. Runtime independence: NOT ESTABLISHED.</text>',
        '<text x="34" y="633" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final 4,194,304-case speed test: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="660" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 81 · complete failure history preserved · no winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def build(
    previous: types.ModuleType,
    v79: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    v76: types.ModuleType,
    v75: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None and options.source_bytes is not None,
        "require complete caller-pinned diagnostic-fix graph source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole actual V81 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V80.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin complete actually pushed V80 " + role,
        )
    for role, item in FEATURE.items():
        base.need(
            getattr(options, "feature_" + role + "_sha256") == item[1],
            "caller-pin the complete actual V14 diagnostic source " + role,
        )
        read_fixed(item, "complete actual V14 diagnostic source " + role)
    raw = read_fixed(FEATURE["contract"], "whole authentic V14 machine proof")
    contract = base.document(raw, "whole diagnostic-preserving V14 contract")
    base.need(
        base.canonical(contract) == raw,
        "reject incomplete or duplicate-key V14 machine proof",
    )
    validate_contract(base, previous, v79, v78, v77, contract)
    old, previous_inputs = authenticate_previous(
        previous, v79, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69,
        modules, base,
    )
    v5 = old["clean_original_producer_v5_source_freeze"][
        "complete_feature_contract"
    ]
    v2 = old["candidate_runtime_independence_v2_source_freeze"][
        "complete_feature_contract"
    ]
    v12 = old["rust_v12_original_campaign_source_freeze"][
        "complete_feature_contract"
    ]
    v13 = old["rust_v13_original_campaign_source_freeze"][
        "complete_feature_contract"
    ]
    prior_v12 = old["actual_rust_v12_original_campaign"][
        "complete_publication_receipt"
    ]
    prior_v13 = old["actual_rust_v13_original_campaign"][
        "complete_publication_receipt"
    ]
    v78.validate_receipt(base, v77, prior_v12)
    previous.validate_receipt(base, v79, v78, v77, prior_v13)
    proof = {
        "schema": SCHEMA + "-guarded-rust-original-campaign-v14-source",
        "version": 14,
        "status": contract["status"],
        "complete_feature_contract": copy.deepcopy(contract),
        "owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        },
        "independent_source_owner_count": 3,
        "planned_actual_original_candidate_worker_count": 13,
        "original_case_execution_denominator": 31237,
        "actual_candidate_workers_started": 0,
        "actual_build_archive_opens": 0,
        "actual_native_libraries_loaded": 0,
        "previous_v12_actual_candidate_worker_count": 13,
        "previous_v12_actual_infrastructure_failure_count": 13,
        "previous_v13_actual_candidate_worker_count": 13,
        "previous_v13_actual_infrastructure_failure_count": 13,
        "previous_actual_child_failure_recorded": False,
        "worker_failure_capture_mode": contract["worker_failure_capture_mode"],
        "worker_failure_capture_stream_limit_bytes":
            contract["worker_failure_capture_stream_limit_bytes"],
        "worker_failure_capture_traceback_limit_bytes":
            contract["worker_failure_capture_traceback_limit_bytes"],
        "worker_failure_capture_total_budget_bytes":
            contract["worker_failure_capture_total_budget_bytes"],
        "worker_failure_capture_attempts": 0,
        "worker_failure_capture_complete": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    changes = {
        "actual_current_graph_predecessor_version": 80,
        "authenticated_evidence_owner_lower_bound": 265,
        "authenticated_history_reference_lower_bound": 270,
        "rust_v14_original_campaign_source_freeze": proof,
        "rust_v14_original_campaign_source_status": contract["status"],
        "rust_v14_original_campaign_source_owner_count": 3,
        "rust_v14_original_campaign_planned_worker_count": 13,
        "rust_v14_original_campaign_original_case_count": 31237,
        "rust_v14_original_campaign_actual_worker_count": 0,
        "rust_v14_original_campaign_actual_native_load_count": 0,
        "rust_v14_original_campaign_actual_archive_open_count": 0,
        "rust_v14_original_campaign_worker_failure_capture_mode":
            contract["worker_failure_capture_mode"],
        "rust_v14_original_campaign_worker_failure_capture_attempts": 0,
        "rust_v14_original_campaign_worker_failure_capture_complete":
            "NOT RUN",
        "rust_v14_original_campaign_candidate_matching": "NOT RUN",
        "rust_v14_original_campaign_runtime_no_delegation": "NOT ESTABLISHED",
        "rust_v14_original_campaign_candidate_qualified": False,
        "rust_v14_original_campaign_previous_v12_failure_receipt_sha256":
            v78.RECEIPT[1],
        "rust_v14_original_campaign_previous_v13_failure_receipt_sha256":
            previous.RECEIPT[1],
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v80_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V80.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 81,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve baseline and all six truly independent engine families",
    )
    for row in families:
        if row["family"] == "python":
            continue
        base.need(
            row["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ] == v5
            and row["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ] == v2
            and row["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v12
            and row["rust_v13_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v13
            and row["actual_rust_v12_original_campaign"][
                "complete_publication_receipt"
            ] == prior_v12
            and row["actual_rust_v13_original_campaign"][
                "complete_publication_receipt"
            ] == prior_v13,
            "retain all complete prior contracts and both real losses in "
            + row["family"],
        )
        row["authenticated_evidence_owner_lower_bound"] = 265
        row["authenticated_history_reference_lower_bound"] = 270
        row["rust_v14_original_campaign_source_freeze"] = copy.deepcopy(proof)
        if row["family"] == "rust":
            for key, value in changes.items():
                if key.startswith("rust_v14_original_campaign_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 81,
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
        "preserve all historical original suite vectors and six real witnesses",
    )
    for name, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        observed = layer["actual_complete_rust_campaign"]
        base.need(
            observed["complete_independently_authenticated_suite_results"]
            == suites
            and observed["earliest_genuine_mismatch_witnesses"] == witnesses
            and layer["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ] == v5
            and layer["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ] == v2
            and layer["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v12
            and layer["rust_v13_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v13
            and layer["actual_rust_v12_original_campaign"][
                "complete_publication_receipt"
            ] == prior_v12
            and layer["actual_rust_v13_original_campaign"][
                "complete_publication_receipt"
            ] == prior_v13
            and layer["rust_v12_original_campaign_actual_worker_count"] == 13
            and layer["rust_v12_original_campaign_completed_suite_count"] == 0
            and layer["rust_v12_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v12_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["rust_v13_original_campaign_actual_worker_count"] == 13
            and layer["rust_v13_original_campaign_completed_suite_count"] == 0
            and layer["rust_v13_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v13_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["actual_rust_v13_original_campaign"][
                "failure_details_in_public_receipt"
            ] is False
            and layer["rust_v14_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == contract
            and layer["rust_v14_original_campaign_actual_worker_count"] == 0
            and layer["rust_v14_original_campaign_candidate_matching"]
            == "NOT RUN",
            "retain complete actual failure and unrun diagnostics proof in "
            + name,
        )
    for row in families:
        if row["family"] == "python":
            continue
        base.need(
            row["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ] == v5
            and row["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ] == v2
            and row["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v12
            and row["rust_v13_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == v13
            and row["rust_v14_original_campaign_source_freeze"][
                "complete_feature_contract"
            ] == contract
            and row["actual_rust_v12_original_campaign"][
                "complete_publication_receipt"
            ] == prior_v12
            and row["actual_rust_v13_original_campaign"][
                "complete_publication_receipt"
            ] == prior_v13
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "retain all five whole contracts and both real results in "
            + row["family"],
        )
    base.need(
        summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_rust_verified_passing_case_count"] == 14853
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_c_verified_passing_case_count"] == 7325
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["actual_zig_verified_passing_case_count"] == 3711
        and summary["qualified_candidate_count"] == 0
        and summary["final_holdout_opened"] is False
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED",
        "never hide historical mismatch or substitute diagnostics for matching",
    )
    summary_raw = base.canonical(summary)
    for role, raw_asset in (
        ("complete loss-preserving V81 inputs", input_raw),
        ("complete loss-preserving V81 summary", summary_raw),
        ("complete readable V81 SVG", svg_raw),
    ):
        base.need(
            0 < len(raw_asset) <= base.OWNER_LIMIT,
            "reject overflow without truncation or publishing any owner: "
            + role,
        )
    return snapshot, {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": summary_raw,
        OUTPUT + ".svg": svg_raw,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"
        }
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only three complete bounded diagnostic-source graph owners",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0, "write whole V81 owner")
            remaining = remaining[count:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "require exact exclusively created whole diagnostic graph owner",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(
        path, base.digest(raw), len(raw), private=True
    )
    base.need(confirmed == raw, "reauthenticate complete final V81 evidence")


def self_test(
    previous: types.ModuleType,
    v79: types.ModuleType,
    v78: types.ModuleType,
    v77: types.ModuleType,
    v76: types.ModuleType,
    v75: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(
        v79, v78, v77, v76, v75, v74, v73, v72, v71, v70, v69, modules,
        base,
    )
    base.need(
        prior["status"] == "PASS"
        and prior["actual_current_graph_predecessor_version"] == 79
        and prior["authenticated_evidence_owner_lower_bound"] == 262
        and prior["authenticated_history_reference_lower_bound"] == 267
        and prior["previous_actual_rust_candidate_worker_count"] == 13
        and prior["previous_actual_rust_infrastructure_failure_count"] == 13
        and prior["actual_corrected_rust_candidate_worker_count_from_receipt"]
        == 13
        and prior["actual_corrected_rust_completed_suite_count_from_receipt"]
        == 0
        and prior["actual_corrected_rust_infrastructure_failure_count_from_receipt"]
        == 13
        and prior["actual_corrected_rust_semantic_mismatch_count_from_receipt"]
        == "NOT MEASURED"
        and prior["runtime_no_delegation"] == "NOT ESTABLISHED",
        "inherit both actual 13-worker losses and complete unchanged guard proof",
    )
    raw = read_fixed(FEATURE["contract"], "complete final V14 diagnosis proof")
    contract = base.document(raw, "complete diagnostic V14 machine contract")
    base.need(base.canonical(contract) == raw, "reject altered V14 contract")
    validate_contract(base, previous, v79, v78, v77, contract)
    cases: list[tuple[str, object]] = [("missing complete V14 source", None)]
    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        cases.append(("removed actual V14 diagnostics field " + key, forged))
    for name, wrong in (
        ("version", 13),
        ("frozen_graph_version", 79),
        ("current_evidence_owner_lower_bound", 261),
        ("current_history_reference_lower_bound", 266),
        ("prospective_evidence_owner_lower_bound", 264),
        ("prospective_history_reference_lower_bound", 269),
        ("suite_count", 12),
        ("case_execution_denominator", 31236),
        ("planned_actual_original_candidate_worker_count", 12),
        ("private_waiver_count", 14),
        ("supplemental_cases_counted_in_original_denominator", True),
        ("corrected_original_producer_version", 4),
        ("historical_ctypes_source_count", 3),
        ("historical_ctypes_proxy_native_load_permitted", True),
        ("historical_ctypes_preloaded", True),
        ("historical_ctypes_transforms_executed", 1),
        ("worker_failure_capture_mode", "DISCARD CHILD STDERR AND EXIT"),
        ("worker_failure_capture_stream_limit_bytes", 65535),
        ("worker_failure_capture_traceback_limit_bytes", 65535),
        ("worker_failure_capture_total_budget_bytes", 4194305),
        ("worker_failure_capture_attempts", 1),
        ("worker_failure_capture_complete", "PASS"),
        ("worker_failure_capture_native_loads", 1),
        ("worker_failure_capture_processes_started", 1),
        ("v13_actual_failure_receipt_bytes", 6743),
        ("v13_actual_failure_receipt_inode", 525048),
        ("v13_actual_candidate_worker_count", 12),
        ("v13_actual_completed_suite_count", 13),
        ("v13_actual_infrastructure_failure_count", 0),
        ("v13_actual_semantic_mismatch_count", 0),
        ("v13_actual_verified_passing_case_count", 31237),
        ("v13_actual_candidate_qualified", True),
        ("v13_actual_all_four_original_targets_restored", False),
        ("v13_failure_archive_opened", True),
        ("v13_failure_archive_inflated", True),
        ("v12_actual_failure_receipt_bytes", 6743),
        ("v12_actual_failure_receipt_inode", 524988),
        ("v12_actual_candidate_worker_count", 12),
        ("v12_actual_completed_suite_count", 13),
        ("v12_actual_infrastructure_failure_count", 0),
        ("v12_actual_semantic_mismatch_count", 0),
        ("v12_actual_verified_passing_case_count", 31237),
        ("v12_actual_candidate_qualified", True),
        ("v12_actual_all_four_original_targets_restored", False),
        ("v12_failure_archive_opened", True),
        ("v12_failure_archive_inflated", True),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("qualified_candidate_count", 1),
        ("runtime_non_delegation", "PASS"),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[name] = wrong
        cases.append(("fabricated diagnostics outcome or safety " + name, forged))
    for key in (
        "source_sha256", "protocol_sha256", "frozen_graph_source_sha256",
        "frozen_graph_inputs_sha256", "frozen_graph_summary_sha256",
        "frozen_graph_svg_sha256", "corrected_original_producer_source_sha256",
        "corrected_original_producer_protocol_sha256",
        "corrected_original_producer_contract_sha256",
        "runtime_guard_source_sha256", "runtime_guard_protocol_sha256",
        "runtime_guard_contract_sha256",
        "previous_v13_source_sha256", "previous_v13_protocol_sha256",
        "previous_v13_contract_sha256",
        "v13_actual_failure_receipt_sha256",
        "v12_source_sha256", "v12_protocol_sha256", "v12_contract_sha256",
        "v12_actual_failure_receipt_sha256",
        "actual_v19_build_source_sha256", "actual_v19_build_contract_sha256",
        "actual_v19_build_receipt_sha256", "actual_v19_root_receipt_sha256",
        "actual_v19_native_engine_sha256", "actual_v19_native_bridge_sha256",
    ):
        forged = copy.deepcopy(contract)
        forged[key] = "0" * 64
        cases.append(("substituted whole first-party provenance " + key, forged))
    for key in (
        "actual_candidate_workers_started", "actual_candidate_imports",
        "actual_native_libraries_loaded", "actual_private_build_root_opens",
        "actual_private_build_root_stats", "actual_build_archive_opens",
        "actual_build_archive_inflations", "actual_hidden_cases_read",
        "actual_clock_samples", "actual_compiler_processes_started",
        "timing_trials_run",
    ):
        forged = copy.deepcopy(contract)
        forged[key] = 1
        cases.append(("invented source-only operation " + key, forged))
    for role, _, _, _, _, _ in HISTORICAL_CTYPES:
        forged = copy.deepcopy(contract)
        forged["historical_ctypes_sources"] = [
            item for item in forged["historical_ctypes_sources"]
            if item["role"] != role
        ]
        cases.append(("removed fail-closed historical loader " + role, forged))
    for index, (role, _, _, _, _, _) in enumerate(HISTORICAL_CTYPES):
        for name, wrong in (
            ("sha256", "0" * 64),
            ("inode", 0),
            ("exact_top_level_import_line", 0),
            ("transformation", "PRELOAD CTYPES; WEAKEN GUARD"),
        ):
            forged = copy.deepcopy(contract)
            forged["historical_ctypes_sources"][index][name] = wrong
            cases.append(("altered historical fix " + role + "/" + name, forged))
    for suite, _ in v77.SUITES:
        forged = copy.deepcopy(contract)
        forged["suites"] = [
            row for row in forged["suites"]
            if row.get("suite", row.get("name", row.get("id"))) != suite
        ]
        cases.append(("removed original test group " + suite, forged))
    rejected = 0
    for label, forged in cases:
        try:
            validate_contract(base, previous, v79, v78, v77, forged)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted forged diagnostics repair: " + label)
    base.need(rejected == len(cases) and rejected >= 145,
              "reject omitted losses, weakened guards, and fake diagnosed runs")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 81,
        "status": "PASS",
        "previous_overview_version": 80,
        "actual_current_graph_predecessor_version": 80,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": (
            prior["rejected_hostile_control_count"] + rejected
        ),
        "authenticated_evidence_owner_lower_bound": 265,
        "authenticated_history_reference_lower_bound": 270,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "previous_v12_actual_rust_candidate_worker_count": 13,
        "previous_v12_actual_rust_infrastructure_failure_count": 13,
        "previous_v13_actual_rust_candidate_worker_count": 13,
        "previous_v13_actual_rust_infrastructure_failure_count": 13,
        "previous_actual_child_failure_recorded": False,
        "planned_diagnostics_candidate_worker_count": 13,
        "actual_diagnostics_candidate_workers_started": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_compressed_evidence_inflations_by_graph": 0,
        "actual_private_build_root_opens_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "candidate_matching": "NOT RUN",
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
    for role in V80:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        (
            previous, v79, v78, v77, v76, v75, v74, v73, v72, v71, v70,
            v69, modules, base,
        ) = load_previous()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256", "source_bytes", "inputs_sha256",
                        "summary_sha256", "svg_sha256",
                    )
                )
                and all(
                    getattr(options, "previous_" + role + "_sha256") is None
                    for role in V80
                )
                and all(
                    getattr(options, "feature_" + role + "_sha256") is None
                    for role in FEATURE
                ),
                "self-test must not execute workers or publish result graphs",
            )
            result = self_test(
                previous, v79, v78, v77, v76, v75, v74, v73, v72, v71,
                v70, v69, modules, base,
            )
        else:
            _, assets = build(
                previous, v79, v78, v77, v76, v75, v74, v73, v72, v71,
                v70, v69, modules, base, options,
            )
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject invented complete V81 output identities",
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
                            "complete V81 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(actual == assets[path],
                              "reproduce whole exact diagnostics " + role)
            result = {
                "schema": SCHEMA + (
                    "-published" if options.render
                    else "-read-only-frozen-context"
                ),
                "version": 81,
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
                "previous_overview_version": 80,
                "actual_current_graph_predecessor_version": 80,
                "authenticated_evidence_owner_lower_bound": 265,
                "authenticated_history_reference_lower_bound": 270,
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "previous_v12_actual_rust_candidate_worker_count": 13,
                "previous_v12_actual_rust_infrastructure_failure_count": 13,
                "previous_v13_actual_rust_candidate_worker_count": 13,
                "previous_v13_actual_rust_infrastructure_failure_count": 13,
                "previous_actual_child_failure_recorded": False,
                "planned_diagnostics_candidate_worker_count": 13,
                "actual_diagnostics_candidate_workers_started": 0,
                "actual_candidate_workers_started_by_graph": 0,
                "actual_compiler_processes_started_by_graph": 0,
                "actual_compressed_evidence_owners_opened_by_graph": 0,
                "actual_compressed_evidence_inflations_by_graph": 0,
                "actual_private_build_root_opens_by_graph": 0,
                "actual_clock_samples_by_graph": 0,
                "actual_hidden_cases_read_by_graph": 0,
                "candidate_matching": "NOT RUN",
                "runtime_no_delegation": "NOT ESTABLISHED",
                "qualified_candidate_count": 0,
                "final_holdout_opened": False,
                "performance": "NOT MEASURED",
                "outputs_written": bool(options.render),
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V81 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
