#!/usr/bin/env python3
"""Show the latest failed real test and one unbuilt from-scratch source repair."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import types

ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v59.py"
OUTPUT = "docs/evidence/candidate-current-overview-v59"
SCHEMA = "rebar-candidate-current-overview-v59"
V58 = {
    "source": (
        "tools/render_candidate_current_overview_v58.py",
        "98658308205a0dc25e1bf7cc5d8295408f248c1e4fdf62e1dee5782decb82c70",
        119240,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v58.inputs.json",
        "3c58f7aa410ce287e1a718a2eb93e5cf9c7b6121bd1f0d404fbc7e67c9f6fd30",
        892497,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v58.json",
        "5d94286c55bce81a2b12fb54b39cb04e543cdad2588e21f3a13ade3adb03fd9a",
        2426500,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v58.svg",
        "25477c207348b7cdfee3aa24071b27354f31553fde55033dc7eff5852e81e04d",
        14539,
    ),
}
FEATURE = {
    "bridge_source": (
        "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c",
        "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740",
        179961,
    ),
    "applicator": (
        "tools/apply_owned_rust_buffer_shape_pickle_source_repair_v2.py",
        "7f22016b20da990b0ddb85114bf76a187918612ef68aae97c94d81518d3eb322",
        47145,
    ),
    "protocol": (
        "oracle/phase2/RUST-BUFFER-SHAPE-PICKLE-SOURCE-REPAIR-V2.md",
        "79ad2b88f7542c791cdf48956d432e6d9f2dad00a485056972eea1664e41ff66",
        4060,
    ),
    "contract": (
        "oracle/phase2/rust-buffer-shape-pickle-source-repair-v2.json",
        "0d5fe2ca190df54366b73850ce316a9d27f77c527bd5ddd8d5420d62dcb33be0",
        7486,
    ),
}
FEATURE_INODES = {
    "bridge_source": 525057,
    "applicator": 432135,
    "protocol": 525058,
    "contract": 525059,
}
PUBLIC_COUNTS = {
    "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1, "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22, "FAIL": 1, "NOT RUN": 3,
    "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1,
}
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]


def load_v58() -> tuple:
    path, fingerprint, size = V58["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(handle)
        if (not stat.S_ISREG(before.st_mode)
                or before.st_uid != os.geteuid()
                or before.st_nlink != 1
                or stat.S_IMODE(before.st_mode) != 0o600
                or before.st_size != size):
            raise ValueError("reject substituted exact pushed V58 source")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated exact pushed V58 source")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended exact pushed V58 source")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed exact pushed V58 source")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_actual_pushed_source_graph_v58")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v57()
    base = prior_modules[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v58"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS
        and previous.WORKERS == WORKERS,
        "authenticate only actual current pushed V58 graph renderer",
    )
    return previous, prior_modules, base


def v58_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V58["source"][1],
        source_bytes=V58["source"][2],
        previous_source_sha256=previous.V57["source"][1],
        previous_inputs_sha256=previous.V57["inputs"][1],
        previous_summary_sha256=previous.V57["summary"][1],
        previous_svg_sha256=previous.V57["svg"][1],
        receipt_sha256=previous.RECEIPT[1],
        receipt_bytes=previous.RECEIPT[2],
        receipt_inode=previous.RECEIPT_INODE,
        receipt_device=previous.DEVICE,
        forensic_sha256=previous.FORENSIC[1],
        forensic_bytes=previous.FORENSIC[2],
        forensic_inode=previous.FORENSIC_INODE,
        forensic_device=previous.DEVICE,
        inputs_sha256=None,
        summary_sha256=None,
        svg_sha256=None,
    )


def authenticate_v58(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V58.items():
        base.need(
            base.checked(supplied.get(role), "actually pushed V58 " + role)
            == item[1],
            "reject substituted actually pushed V58 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete actual V58 graph summary")
    inputs = base.document(raw["inputs"], "complete actual V58 graph inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(prior_modules, v58_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v58-summary"
        and old.get("version") == 58
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V58["source"])
        and old.get("inputs") == base.pin(*V58["inputs"])
        and old.get("svg") == base.pin(*V58["svg"])
        and inputs.get("schema")
            == "rebar-candidate-current-overview-v58-inputs"
        and inputs.get("version") == 58
        and inputs.get("renderer") == base.pin(*V58["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V58["inputs"][0]]
        and raw["summary"] == expected[V58["summary"][0]]
        and raw["svg"] == expected[V58["svg"][0]]
        and old.get("actual_rust_semantic_mismatch_count") == 928
        and old.get("actual_rust_verified_passing_case_count") == 8965
        and old.get("rust_original_campaign_semantic_mismatch_count") == 928
        and old.get("rust_original_campaign_verified_passing_case_count")
            == 8965
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get(
            "actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and old.get("actual_rust_v10_candidate_status") == "FAIL"
        and old.get("actual_rust_v10_semantic_mismatch_count") == 1440
        and old.get("actual_rust_v10_verified_passing_case_count") == 14853
        and old.get("actual_rust_v10_semantic_mismatch_regression_against_v7")
            == 512
        and old.get("actual_rust_v10_candidate_workers") == 13
        and old.get("actual_rust_v10_worker_process_ids") == WORKERS
        and old.get("actual_rust_v10_infrastructure_failure_count") == 0
        and old.get("actual_rust_v10_all_four_original_targets_restored")
            is True
        and len(old.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results",
            [],
        )) == 13
        and len(old.get("actual_rust_v10_earliest_genuine_mismatch_witnesses",
                        [])) == 6
        and old.get("authenticated_evidence_owner_lower_bound") == 197
        and old.get("authenticated_history_reference_lower_bound") == 202
        and old.get("qualified_candidate_count") == 0
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce exact actual V58, complete failed campaign and stale aliases",
    )
    return old, inputs, raw["svg"]




FEATURE_CONTRACT_EXPECTATIONS = {
    "actual_previous_candidate_failure": {
        "actual_mismatch_count": 1440,
        "candidate_qualified": False,
        "explicitly_verified_passing_case_count": 14853,
        "failed_suite_cases_counted_as_passing": False,
        "genuine_failure_categories": {
            "managed_v1": 16,
            "shape_v2": 1056,
            "substitution_v2": 368,
        },
        "infrastructure_failure_count": 0,
        "mismatch_regression_against_v7": 512,
        "named_private_waiver_count": 13,
        "original_case_denominator": 31237,
        "original_suite_count": 13,
        "previous_v7_explicitly_verified_passing_case_count": 8965,
        "previous_v7_mismatch_count": 928,
        "real_candidate_worker_count": 13,
        "real_witnesses": [
            {
                "actual_events_complete": True,
                "case": "managed-buffer-lifetime.v1.0453",
                "expected_events_complete": True,
                "suite": "managed_v1",
            },
            {
                "actual_events_complete": True,
                "case": "managed-buffer-lifetime.v1.0454",
                "expected_events_complete": True,
                "suite": "managed_v1",
            },
            {
                "actual_events_complete": True,
                "case": "substitution-buffer-semantics.v1.03521",
                "expected_events_complete": False,
                "suite": "substitution_v2",
            },
            {
                "actual_events_complete": True,
                "case": "substitution-buffer-semantics.v1.03522",
                "expected_events_complete": False,
                "suite": "substitution_v2",
            },
            {
                "actual_events_complete": False,
                "case": "shape-changing-buffer-semantics.v1.00020",
                "expected_events_complete": False,
                "suite": "shape_v2",
            },
            {
                "actual_events_complete": False,
                "case": "shape-changing-buffer-semantics.v1.00021",
                "expected_events_complete": False,
                "suite": "shape_v2",
            },
        ],
        "real_worker_process_ids": [
            81,
            87,
            88,
            89,
            90,
            91,
            92,
            93,
            94,
            95,
            196,
            197,
            198,
        ],
        "status": "FAIL",
        "suite_results": [
            {
                "cases": 151,
                "explicitly_verified_passes": 151,
                "mismatches": 0,
                "suite": "original_bounded_v5",
                "worker_process_id": 81,
            },
            {
                "cases": 864,
                "explicitly_verified_passes": 864,
                "mismatches": 0,
                "suite": "public_v3",
                "worker_process_id": 87,
            },
            {
                "cases": 1024,
                "explicitly_verified_passes": 1024,
                "mismatches": 0,
                "suite": "scanner_v3",
                "worker_process_id": 88,
            },
            {
                "cases": 768,
                "explicitly_verified_passes": 768,
                "mismatches": 0,
                "suite": "buffer_v3",
                "worker_process_id": 89,
            },
            {
                "cases": 1024,
                "explicitly_verified_passes": 0,
                "mismatches": 16,
                "suite": "managed_v1",
                "worker_process_id": 90,
            },
            {
                "cases": 2854,
                "explicitly_verified_passes": 2854,
                "mismatches": 0,
                "suite": "scanner_verbose_v1",
                "worker_process_id": 91,
            },
            {
                "cases": 6912,
                "explicitly_verified_passes": 6912,
                "mismatches": 0,
                "suite": "public_types_v1",
                "worker_process_id": 92,
            },
            {
                "cases": 5120,
                "explicitly_verified_passes": 0,
                "mismatches": 368,
                "suite": "substitution_v2",
                "worker_process_id": 93,
            },
            {
                "cases": 10240,
                "explicitly_verified_passes": 0,
                "mismatches": 1056,
                "suite": "shape_v2",
                "worker_process_id": 94,
            },
            {
                "cases": 1376,
                "explicitly_verified_passes": 1376,
                "mismatches": 0,
                "suite": "public_surface_v19",
                "worker_process_id": 95,
            },
            {
                "cases": 128,
                "explicitly_verified_passes": 128,
                "mismatches": 0,
                "suite": "subinterpreter_v2",
                "worker_process_id": 196,
            },
            {
                "cases": 264,
                "explicitly_verified_passes": 264,
                "mismatches": 0,
                "suite": "pep688_v4",
                "worker_process_id": 197,
            },
            {
                "cases": 512,
                "explicitly_verified_passes": 512,
                "mismatches": 0,
                "suite": "threaded_pattern_v1",
                "worker_process_id": 198,
            },
        ],
        "unprojected_witness_vectors": "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION",
        "verified_passes_derived_by_subtraction": False,
    },
    "authenticated_previous_owners": [
        {
            "bytes": 3756,
            "device": 2064,
            "inode": 31364044,
            "name": "goal",
            "path": "GOAL.md",
            "sha256": "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        },
        {
            "bytes": 181004,
            "device": 2064,
            "inode": 524972,
            "name": "tested_rust_bridge",
            "path": "candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c",
            "sha256": "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335",
        },
        {
            "bytes": 119240,
            "device": 2064,
            "inode": 432117,
            "name": "previous_graph_source",
            "path": "tools/render_candidate_current_overview_v58.py",
            "sha256": "98658308205a0dc25e1bf7cc5d8295408f248c1e4fdf62e1dee5782decb82c70",
        },
        {
            "bytes": 892497,
            "device": 2064,
            "inode": 432118,
            "name": "previous_graph_inputs",
            "path": "docs/evidence/candidate-current-overview-v58.inputs.json",
            "sha256": "3c58f7aa410ce287e1a718a2eb93e5cf9c7b6121bd1f0d404fbc7e67c9f6fd30",
        },
        {
            "bytes": 2426500,
            "device": 2064,
            "inode": 432120,
            "name": "previous_graph_summary",
            "path": "docs/evidence/candidate-current-overview-v58.json",
            "sha256": "5d94286c55bce81a2b12fb54b39cb04e543cdad2588e21f3a13ade3adb03fd9a",
        },
        {
            "bytes": 14539,
            "device": 2064,
            "inode": 432121,
            "name": "previous_graph_svg",
            "path": "docs/evidence/candidate-current-overview-v58.svg",
            "sha256": "25477c207348b7cdfee3aa24071b27354f31553fde55033dc7eff5852e81e04d",
        },
        {
            "bytes": 6708,
            "device": 2064,
            "inode": 525044,
            "name": "failure_publication_receipt",
            "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-publication-receipt.json",
            "sha256": "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2",
        },
        {
            "bytes": 24701,
            "device": 2064,
            "inode": 525045,
            "name": "independent_failure_forensics",
            "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-forensic-summary.json",
            "sha256": "6e04771a48b4a460ad58ac9795ef91a697a33fa0aeae4671c9b3c9b35e4820cd",
        },
    ],
    "candidate_variant": {
        "bytes": 179961,
        "bytes_outside_substitution_function_sha256": "1a4e1713e2ea2dd6a42d56baac4e66907392b1971b94a1f5007fecab5c25830b",
        "derived_from_actually_tested_source": True,
        "device": 2064,
        "inode": 525057,
        "live_exporter_release_exit_count": 8,
        "live_original_exporter_open_count": 1,
        "new_candidate_family": False,
        "new_external_package": False,
        "path": "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c",
        "premature_bytes_snapshot_count": 0,
        "retained_original_subject_match_allocation_count": 2,
        "sha256": "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740",
        "status": "SOURCE FROZEN; NOT BUILT; NOT RUN",
    },
    "current_previous_graph": {
        "authenticated_evidence_owner_lower_bound": 197,
        "authenticated_history_reference_lower_bound": 202,
        "explicit_current_v10_mismatch_count": 1440,
        "explicit_current_v10_verified_passes": 14853,
        "historical_generic_mismatch_alias": 928,
        "qualified_candidate_count": 0,
        "version": 58,
    },
    "family": "rust",
    "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS",
    "phase_boundary": {
        "archive_inflations": 0,
        "archive_opens": 0,
        "benchmark_files_read": 0,
        "candidate_processes_started": 0,
        "candidate_variant_build": "NOT RUN",
        "candidate_variant_correctness": "NOT MEASURED",
        "candidate_variant_matching": "NOT RUN",
        "candidate_variant_qualified": False,
        "clock_samples": 0,
        "compiler_processes_started": 0,
        "confidence_intervals": "NOT MEASURED",
        "first_party_candidate_family_count": 6,
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "native_libraries_loaded": 0,
        "performance": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    },
    "protocol": {
        "bytes": 4060,
        "path": "oracle/phase2/RUST-BUFFER-SHAPE-PICKLE-SOURCE-REPAIR-V2.md",
        "sha256": "79ad2b88f7542c791cdf48956d432e6d9f2dad00a485056972eea1664e41ff66",
    },
    "resulting_source_evidence_lower_bounds": {
        "authenticated_evidence_owner_lower_bound": 201,
        "authenticated_history_reference_lower_bound": 206,
        "global_evidence_owner_census": "NOT MEASURED",
        "new_focused_source_owners": 4,
        "previous_authenticated_evidence_owner_lower_bound": 197,
        "previous_authenticated_history_reference_lower_bound": 202,
    },
    "schema": "rebar-phase2-owned-rust-buffer-shape-pickle-source-repair-v2-source-freeze",
    "source": {
        "bytes": 47145,
        "path": "tools/apply_owned_rust_buffer_shape_pickle_source_repair_v2.py",
        "sha256": "7f22016b20da990b0ddb85114bf76a187918612ef68aae97c94d81518d3eb322",
    },
    "status": "SOURCE FROZEN; FIRST-PARTY RUST BUFFER-LIFETIME VARIANT NOT BUILT OR RUN",
    "version": 2,
}

def feature_source_expectations() -> dict:
    return copy.deepcopy(FEATURE_CONTRACT_EXPECTATIONS)

def validate_feature_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject missing actual four-owner unbuilt V2 source feature")
    assert isinstance(proof, dict)
    owners = proof.get("owners")
    base.need(type(owners) is dict and set(owners) == set(FEATURE),
              "bind exactly four independent first-party source owners")
    assert isinstance(owners, dict)
    for role, item in FEATURE.items():
        previous = owners.get(role)
        base.need(
            type(previous) is dict
            and previous.get("path") == item[0]
            and previous.get("sha256") == item[1]
            and previous.get("bytes") == item[2]
            and previous.get("device") == 2064
            and previous.get("inode") == FEATURE_INODES[role]
            and previous.get("uid") == os.geteuid()
            and previous.get("nlink") == 1
            and previous.get("mode") == "0600",
            "reject forged independent V2 source owner: " + role,
        )
    contract = proof.get("complete_source_contract")
    base.need(type(contract) is dict,
              "reject missing independently authenticated V2 source contract")
    assert isinstance(contract, dict)
    for key, value in feature_source_expectations().items():
        base.need(type(contract.get(key)) is type(value)
                  and contract.get(key) == value,
                  "reject forged frozen source contract field: " + key)
    expected = {
        "schema": SCHEMA + "-authenticated-v2-source-feature",
        "family": "rust",
        "feature_status": "SOURCE FROZEN",
        "candidate_build_status": "NOT BUILT",
        "candidate_matching_status": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "new_independent_source_owner_count": 4,
        "historical_evidence_owner_lower_bound": 197,
        "historical_history_reference_lower_bound": 202,
        "resulting_evidence_owner_lower_bound": 201,
        "resulting_history_reference_lower_bound": 206,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    base.need(
        set(proof) == set(expected) | {"owners", "complete_source_contract"},
        "reject erased or invented complete first-party V2 feature fields",
    )
    for key, value in expected.items():
        base.need(type(proof.get(key)) is type(value)
                  and proof.get(key) == value,
                  "reject invented V2 source feature or execution: " + key)


def make_feature_proof(base: types.ModuleType,
                       owners: dict[str, dict],
                       contract: dict) -> dict:
    expected = feature_source_expectations()
    base.need(type(contract) is dict, "reject missing frozen V2 source contract")
    for key, value in expected.items():
        base.need(type(contract.get(key)) is type(value)
                  and contract.get(key) == value,
                  "reject substituted frozen V2 source contract: " + key)
    proof = {
        "schema": SCHEMA + "-authenticated-v2-source-feature",
        "family": "rust",
        "feature_status": "SOURCE FROZEN",
        "candidate_build_status": "NOT BUILT",
        "candidate_matching_status": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "owners": copy.deepcopy(owners),
        "complete_source_contract": copy.deepcopy(contract),
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "new_independent_source_owner_count": 4,
        "historical_evidence_owner_lower_bound": 197,
        "historical_history_reference_lower_bound": 202,
        "resulting_evidence_owner_lower_bound": 201,
        "resulting_history_reference_lower_bound": 206,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    validate_feature_proof(base, proof)
    return proof


def authenticate_feature(base: types.ModuleType,
                         options: argparse.Namespace) -> dict:
    owners = {}
    contract = None
    for role, item in FEATURE.items():
        supplied = getattr(options, "feature_" + role + "_sha256")
        base.need(
            base.checked(supplied, "exact V2 feature owner " + role)
            == item[1],
            "reject substituted V2 source-only feature owner: " + role,
        )
        raw, owner = base.read_owner(*item, private=True)
        owners[role] = owner
        if role == "contract":
            contract = base.document(
                raw, "complete frozen V2 feature source contract",
                exact=False,
            )
    base.need(type(contract) is dict,
              "authenticate one complete frozen V2 source contract")
    assert isinstance(contract, dict)
    return make_feature_proof(base, owners, contract)


def result_fields(proof: dict) -> dict:
    return {
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_rust_verified_passing_case_count": 14853,
        "rust_actual_semantic_mismatch_count": 1440,
        "rust_original_campaign_semantic_mismatch_count": 1440,
        "rust_original_campaign_verified_passing_case_count": 14853,
        "rust_verified_passing_case_executions": 14853,
        "rust_original_campaign_v10_matching_status": "FAIL",
        "rust_original_campaign_v10_source_freeze_status":
            "COMPLETED; CANDIDATE FAIL",
        "rust_original_campaign_v10_candidate_workers_started": 13,
        "rust_original_campaign_v10_semantic_mismatch_count": 1440,
        "rust_original_campaign_v10_verified_passing_case_count": 14853,
        "rust_buffer_shape_v2_source_feature": copy.deepcopy(proof),
        "rust_buffer_shape_v2_feature_status": "SOURCE FROZEN",
        "rust_buffer_shape_v2_build_status": "NOT BUILT",
        "rust_buffer_shape_v2_matching_status": "NOT RUN",
        "rust_buffer_shape_v2_candidate_correctness": "NOT MEASURED",
        "rust_buffer_shape_v2_semantic_mismatch_count": "NOT MEASURED",
        "rust_buffer_shape_v2_verified_passing_case_count": "NOT MEASURED",
        "rust_buffer_shape_v2_candidate_qualified": False,
        "rust_buffer_shape_v2_candidate_workers_started": 0,
        "rust_buffer_shape_v2_independent_source_owner_count": 4,
        "authenticated_evidence_owner_lower_bound": 201,
        "authenticated_history_reference_lower_bound": 206,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(modules: tuple, snapshot: object) -> None:
    previous, prior_modules, base = modules
    base.need(type(snapshot) is dict,
              "reject missing normalized complete source-only V59 snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_buffer_shape_v2_source_feature")
    validate_feature_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(type(snapshot.get(key)) is type(value)
                  and snapshot.get(key) == value,
                  "reject invented V59 result or stale alias: " + key)
    replaced = snapshot.get("preserved_v58_replaced_snapshot_fields")
    base.need(type(replaced) is dict and set(replaced).issubset(updates),
              "preserve every exact replaced pushed V58 field")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v58_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(prior_modules, history)
    base.need(
        snapshot.get("actual_rust_semantic_mismatch_count") == 1440
        and snapshot.get("actual_rust_verified_passing_case_count") == 14853
        and snapshot.get("rust_original_campaign_semantic_mismatch_count")
            == 1440
        and snapshot.get("rust_original_campaign_verified_passing_case_count")
            == 14853
        and snapshot.get("rust_original_campaign_v10_matching_status")
            == "FAIL"
        and snapshot.get("rust_original_campaign_v10_candidate_workers_started")
            == 13
        and snapshot.get("rust_original_campaign_v10_semantic_mismatch_count")
            == 1440
        and snapshot.get("rust_original_campaign_v10_verified_passing_case_count")
            == 14853
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get(
            "actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and snapshot.get("actual_rust_v7_candidate_workers") == 13
        and snapshot.get("actual_rust_v10_candidate_status") == "FAIL"
        and snapshot.get("actual_rust_v10_semantic_mismatch_count") == 1440
        and snapshot.get("actual_rust_v10_verified_passing_case_count")
            == 14853
        and snapshot.get(
            "actual_rust_v10_semantic_mismatch_regression_against_v7") == 512
        and snapshot.get("actual_rust_v10_candidate_workers") == 13
        and snapshot.get("actual_rust_v10_worker_process_ids") == WORKERS
        and snapshot.get("actual_rust_v10_infrastructure_failure_count") == 0
        and snapshot.get("actual_rust_v10_all_four_original_targets_restored")
            is True
        and len(snapshot.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results",
            [],
        )) == 13
        and len(snapshot.get(
            "actual_rust_v10_earliest_genuine_mismatch_witnesses", [])) == 6
        and snapshot.get("actual_rust_v8_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v8_candidate_workers") == 0
        and snapshot.get("actual_rust_v9_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v9_candidate_workers") == 0
        and snapshot.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and snapshot.get("rust_buffer_shape_v2_matching_status") == "NOT RUN"
        and snapshot.get("rust_buffer_shape_v2_candidate_correctness")
            == "NOT MEASURED"
        and snapshot.get("rust_buffer_shape_v2_candidate_workers_started")
            == 0
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_status_counts")
            == PUBLIC_COUNTS
        and snapshot.get("large_input_source_case_matrix_count") == 32
        and snapshot.get("large_input_source_case_status_counts")
            == LARGE_COUNTS
        and snapshot.get("large_input_upstream_original_case_count") == 2
        and snapshot.get("large_input_upstream_original_subject_bytes")
            == 2147483648
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("actually_tested_corrected_candidate_families")
            == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
            == 1
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 201
        and snapshot.get("authenticated_history_reference_lower_bound")
            == 206
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("actual_native_libraries_loaded_by_graph") == 0
        and snapshot.get(
            "source_build_archive_gzip_inflation_count_by_graph") == 0
        and snapshot.get("actual_clock_samples_by_graph") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("winner_selected") is False,
        "preserve actual failed V10, normalize aliases and never run V2",
    )


def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    v43 = prior_modules[1][1][1][1][1][9]
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact current V59 graph renderer")
    inputs_sha = base.checked(inputs_sha, "exact current V59 graph inputs")
    visible = old_svg.decode("utf-8").replace(
        "v58-title", "v59-title").replace(
        "v58-description", "v59-description")
    lines = visible.splitlines()
    base.need(len(lines) > 10
              and lines[1].startswith('<title id="v59-title">')
              and lines[2].startswith('<desc id="v59-description">'),
              "preserve exact visible current pushed V58 graph")
    lines[1] = (
        '<title id="v59-title">Building a faster Python re: latest real '
        'Rust test found 1,440 differences; next repair is not yet '
        'built or tested</title>'
    )
    lines[2] = (
        '<desc id="v59-description">Pinned stable Python 3.14.6 remains '
        'the verified baseline. The latest genuinely executed Rust '
        'replacement ran all 31,237 original cases in 13 real workers, '
        'failed 1,440 compatibility checks and explicitly verified '
        '14,853 passing observations. That is 512 more failures than '
        'the explicitly preserved historical V7 result of 928 failures '
        'and 8,965 verified passes. Independently authenticated failed '
        'cohorts are managed 16, substitution 368 and shape 1,056. '
        'All 13 suite vectors, all six specific mismatch witnesses and '
        'the premature exporter-release root cause come from the '
        'independently authenticated small forensic summary, never '
        'from opening compressed evidence in this graph. Four new '
        'first-party Rust exporter-lifetime source files represent one '
        'unbuilt, untested source-only repair: NOT BUILT, NOT RUN, '
        'compatibility NOT MEASURED. They are not a new engine family, '
        'a passing candidate or a measured speedup. Exactly four '
        'independent source owners raise authenticated lower bounds '
        'from 197 / 202 to 201 / 206. Six first-party replacement '
        'families and zero qualified candidates remain. The 31,237 '
        'original cases, 50 signature checks, 32 public-interface '
        'observations and 32 large-input observations remain separate. '
        'The 4,194,304-case holdout has not been generated or opened. '
        'Speed, memory, confidence intervals and undefined behavior are '
        'NOT MEASURED; runtime independence is NOT ESTABLISHED.</desc>'
    )
    visible = "\n".join(lines)
    changes = (
        (
            '<text x="65" y="398" class="heading">Latest corrected Rust '
            'test ran and failed</text>',
            '<text x="65" y="398" class="heading">Rust failed; '
            'next exporter repair is not yet run</text>',
            "distinguish actual failed V10 from unbuilt V2 source",
        ),
        (
            'Native build passed; V8/V9 stopped. V10 ran 13 genuine '
            'workers and failed; all four original targets restored.',
            'V10 really failed in 13 workers; all targets were restored. '
            'The new exporter repair is NOT BUILT and NOT RUN.',
            "retain real campaign and forbid invented V2 execution",
        ),
        (
            '<text x="64" y="1756" class="heading">Corrected V10 actually '
            'ran: FAIL, 512 more differences</text>',
            '<text x="64" y="1756" class="heading">Four-file Rust '
            'exporter repair frozen; not built or tested</text>',
            "label the new feature strictly as untested source",
        ),
        (
            'Exactly three V10 evidence owners raise actual current '
            'lower bounds from 194 / 199 to 197 / 202.',
            'Exactly four source-only owners raise actual current '
            'lower bounds from 197 / 202 to 201 / 206.',
            "count exactly four independently authenticated source owners",
        ),
        (
            'Cohorts are INDEPENDENTLY AUTHENTICATED; the small receipt '
            'does not itself prove their breakdown.',
            'Real V10 cohorts are independently authenticated. The new '
            'source has no build, workers, correctness or speed result.',
            "preserve forensic proof without inventing repair effectiveness",
        ),
    )
    for before, after, why in changes:
        visible = v43.replace_once(base, visible, before, after, why)
    lines = visible.splitlines()
    start = next(
        (index for index, line in enumerate(lines)
         if line.startswith('<rect x="44" y="1858" width="1352"')),
        None,
    )
    base.need(type(start) is int,
              "retain exact current graph and regenerate evidence footer")
    assert isinstance(start, int)
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="381" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact failed-test '
        'history and untested source-only evidence</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V58 graph inputs SHA-256", V58["inputs"][1]),
        ("Historical V58 graph renderer SHA-256", V58["source"][1]),
        ("Historical V58 graph summary SHA-256", V58["summary"][1]),
        ("Historical V58 graph image SHA-256", V58["svg"][1]),
        ("Small actual V10 durable receipt SHA-256", previous.RECEIPT[1]),
        ("Complete independent V10 forensic summary SHA-256",
         previous.FORENSIC[1]),
        ("V10 compressed report SHA-256 (not opened by this graph)",
         previous.ARCHIVE_SHA),
        ("Unbuilt V2 first-party bridge source SHA-256",
         FEATURE["bridge_source"][1]),
        ("Unexecuted V2 first-party applicator source SHA-256",
         FEATURE["applicator"][1]),
        ("V2 source-only protocol SHA-256", FEATURE["protocol"][1]),
        ("V2 source-only contract SHA-256", FEATURE["contract"][1]),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + index * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2145" class="small">Latest actual Rust test: '
        '1,440 mismatches; 14,853 explicitly verified passes; 13 real '
        'workers; 512 more mismatches than V7.</text>',
        '<text x="65" y="2164" class="small">Historical V7: 928 '
        'mismatches and 8,965 verified passes. Authentic failed '
        'cohorts: 16, 368 and 1,056.</text>',
        '<text x="65" y="2183" class="small">New V2 exporter repair: '
        'SOURCE ONLY, NOT BUILT, NOT RUN; compatibility and speed '
        'NOT MEASURED.</text>',
        '<text x="65" y="2202" class="small">Six first-party families. '
        'Zero compatible candidates. Final holdout NOT OPENED.</text>',
        '<!-- This graph only authenticates bounded historical graph, '
        'small forensic and four source owners. It never opens, stats, '
        'hashes or inflates compressed evidence, candidates, native '
        'libraries, recovery roots, clocks, benchmarks or the holdout. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in footers:
        base.need(
            raw.count((label + ": " + value).encode("ascii")) == 1,
            "bind exactly one truthful V59 graph/source footer: " + label,
        )
    lower = raw.lower()
    for phrase in (
            b'height="2250"', b"building a faster python re",
            b"1,440 differences", b"1,440 mismatches",
            b"14,853 explicitly verified", b"13 real workers",
            b"512 more", b"historical", b"928", b"8,965",
            b"managed 16", b"substitution 368", b"shape 1,056",
            b"31,237", b"4.2m unopened", b"not opened",
            b"not built", b"not run", b"source only",
            b"compatibility and speed", b"not measured",
            b"not established", b"197 / 202", b"201 / 206",
            b"signature checks", b"public-interface observations",
            b"large-input observations", b"17 pass", b"7 fail",
            b"22 pass", b"3 not run", b"2,147,483,648",
            b"1,087", b"1,036", b"1,262", b"1,230",
            b"2,172", b"1,764", b"not generated",
            b"not opened by this graph"):
        base.need(phrase in lower,
                  "preserve honest source-only V59 evidence: "
                  + repr(phrase))
    for falsehood in (
            b"v2 candidate passed", b"v2 candidate failed",
            b"v2 actual workers", b"v2 benchmark",
            b"v2 built successfully", b"v2 matching completed",
            b"counts as a new engine family",
            b"rust candidate qualified",
            b"winner selected", b"holdout opened",
            b"faster than python", b"candidate correctness: pass"):
        base.need(falsehood not in lower,
                  "reject invented V2 build, result or speed: "
                  + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish honest complete V59 chart with exactly one linefeed")
    return raw


def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact independently owned V59 source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound exact independently owned V59 source")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                private=True)
    old, old_inputs, old_svg = authenticate_v58(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V58},
    )
    proof = authenticate_feature(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v58_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V58.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 59,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessor,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(modules, snapshot, old_svg, source_sha,
                   base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve baseline Python and exactly six first-party families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 201,
            "authenticated_history_reference_lower_bound": 206,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "current_original_campaign_semantic_mismatch_count": 1440,
                "current_original_campaign_verified_passing_case_count":
                    14853,
                "current_original_campaign_candidate_worker_count": 13,
                "actual_candidate_workers": 13,
                "actual_v10_candidate_correctness": "FAIL",
                "actual_v10_candidate_status": "FAIL",
                "actual_v10_matching_status": "FAIL",
                "actual_v10_semantic_mismatch_count": 1440,
                "actual_v10_verified_passing_case_count": 14853,
                "actual_v10_semantic_mismatch_regression_against_v7": 512,
                "actual_v10_candidate_workers": 13,
                "buffer_shape_v2_source_feature": copy.deepcopy(proof),
                "buffer_shape_v2_feature_status": "SOURCE FROZEN",
                "buffer_shape_v2_build_status": "NOT BUILT",
                "buffer_shape_v2_matching_status": "NOT RUN",
                "buffer_shape_v2_candidate_correctness": "NOT MEASURED",
                "buffer_shape_v2_semantic_mismatch_count": "NOT MEASURED",
                "buffer_shape_v2_verified_passing_case_count":
                    "NOT MEASURED",
                "buffer_shape_v2_candidate_qualified": False,
                "buffer_shape_v2_candidate_workers_started": 0,
                "buffer_shape_v2_independent_source_owner_count": 4,
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 59,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json",
                           base.digest(input_raw), len(input_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(max(len(input_raw), len(summary_raw), len(svg))
              <= base.OWNER_LIMIT,
              "bound only the three authorized complete V59 graph outputs")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_feature_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged V2 source feature: " + description)


def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 4672
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get(
            "actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and prior.get("actual_rust_v10_candidate_status") == "FAIL"
        and prior.get("actual_rust_v10_semantic_mismatch_count") == 1440
        and prior.get("actual_rust_v10_verified_passing_case_count") == 14853
        and prior.get("actual_rust_v10_semantic_mismatch_regression_against_v7")
            == 512
        and prior.get("actual_rust_v10_candidate_workers") == 13
        and prior.get("authenticated_evidence_owner_lower_bound") == 197
        and prior.get("authenticated_history_reference_lower_bound") == 202
        and prior.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and prior.get("actual_forensic_summary_owners_read_by_self_test") == 0
        and prior.get("actual_failure_archives_opened_by_self_test") == 0,
        "preserve all 4,672 actual V58 hostile controls and real failed result",
    )
    v43 = prior_modules[1][1][1][1][1][9]
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item, FEATURE_INODES[role])
            for role, item in FEATURE.items()
        }
        contract = feature_source_expectations()
        proof = make_feature_proof(base, owners, contract)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for role, owner in proof["owners"].items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = v43.forged_value(base, value)
                rejected += reject_control(
                    base, hostile, "owner:" + role + ":" + key)
        for key, value in proof["complete_source_contract"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_source_contract"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "contract:" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v59")),
            ("filesystem", lambda: os.open("forbidden-v59", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v59")),
            ("write", lambda: os.mkdir("forbidden-v59")),
            ("process", lambda: subprocess.run(("forbidden-v59",))),
            ("process", lambda: subprocess.Popen(("forbidden-v59",))),
            ("process", lambda: os.execv("/forbidden-v59", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically forbid V59 source-only " + kind)
            else:
                raise base.GraphError("forbidden V59 source-only side effect")
        base.need(rejected >= 60,
                  "reject forged V2 source pins and invented execution")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 59,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v58_hostile_controls": 4672,
            "new_v59_hostile_controls": rejected,
            "rejected_hostile_control_count": 4672 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_feature_source_owners_read_by_self_test": 0,
            "actual_forensic_summary_owners_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_current_graph_predecessor_version": 58,
            "actual_rust_semantic_mismatch_count": 1440,
            "actual_rust_verified_passing_case_count": 14853,
            "rust_original_campaign_semantic_mismatch_count": 1440,
            "rust_original_campaign_verified_passing_case_count": 14853,
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v8_matching_status": "NOT RUN",
            "actual_rust_v8_candidate_workers": 0,
            "actual_rust_v9_matching_status": "NOT RUN",
            "actual_rust_v9_candidate_workers": 0,
            "actual_rust_v10_candidate_status": "FAIL",
            "actual_rust_v10_semantic_mismatch_count": 1440,
            "actual_rust_v10_verified_passing_case_count": 14853,
            "actual_rust_v10_semantic_mismatch_regression_against_v7": 512,
            "actual_rust_v10_candidate_workers": 13,
            "actual_rust_v10_infrastructure_failure_count": 0,
            "actual_rust_v10_all_four_original_targets_restored": True,
            "rust_buffer_shape_v2_feature_status": "SOURCE FROZEN",
            "rust_buffer_shape_v2_build_status": "NOT BUILT",
            "rust_buffer_shape_v2_matching_status": "NOT RUN",
            "rust_buffer_shape_v2_candidate_correctness": "NOT MEASURED",
            "rust_buffer_shape_v2_candidate_workers_started": 0,
            "rust_buffer_shape_v2_independent_source_owner_count": 4,
            "authenticated_evidence_owner_lower_bound": 201,
            "authenticated_history_reference_lower_bound": 206,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "supplementary_signature_check_count": 50,
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts":
                copy.deepcopy(PUBLIC_COUNTS),
            "large_input_source_case_matrix_count": 32,
            "large_input_source_case_status_counts":
                copy.deepcopy(LARGE_COUNTS),
            "large_input_upstream_original_case_count": 2,
            "large_input_upstream_original_subject_bytes": 2147483648,
            "first_party_source_inventory_family_count": 6,
            "actually_tested_corrected_candidate_families": ["rust"],
            "actually_tested_corrected_candidate_family_count": 1,
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json",
                       OUTPUT + ".svg"}
              and type(raw) is bytes
              and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only three authorized complete V59 graph assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact authorized V59 graph byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid() and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish a private independent complete V59 graph owner")
    finally:
        os.close(handle)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(str(ROOT / Path(path).parent), flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(path, base.digest(raw), len(raw),
                                  private=True)
    base.need(confirmed == raw,
              "re-authenticate one complete actual V59 graph owner")


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    fields = (
        "actual_rust_semantic_mismatch_count",
        "actual_rust_verified_passing_case_count",
        "rust_original_campaign_semantic_mismatch_count",
        "rust_original_campaign_verified_passing_case_count",
        "actual_rust_v7_semantic_mismatch_count",
        "actual_rust_v7_explicitly_verified_passing_case_count",
        "actual_rust_v7_candidate_workers",
        "actual_rust_v8_matching_status",
        "actual_rust_v8_candidate_workers",
        "actual_rust_v9_matching_status",
        "actual_rust_v9_candidate_workers",
        "actual_rust_v10_candidate_status",
        "actual_rust_v10_semantic_mismatch_count",
        "actual_rust_v10_verified_passing_case_count",
        "actual_rust_v10_semantic_mismatch_regression_against_v7",
        "actual_rust_v10_candidate_workers",
        "actual_rust_v10_worker_process_ids",
        "actual_rust_v10_infrastructure_failure_count",
        "actual_rust_v10_all_four_original_targets_restored",
        "actual_rust_v10_complete_independently_authenticated_suite_results",
        "actual_rust_v10_earliest_genuine_mismatch_witnesses",
        "rust_buffer_shape_v2_feature_status",
        "rust_buffer_shape_v2_build_status",
        "rust_buffer_shape_v2_matching_status",
        "rust_buffer_shape_v2_candidate_correctness",
        "rust_buffer_shape_v2_semantic_mismatch_count",
        "rust_buffer_shape_v2_verified_passing_case_count",
        "rust_buffer_shape_v2_candidate_qualified",
        "rust_buffer_shape_v2_candidate_workers_started",
        "rust_buffer_shape_v2_independent_source_owner_count",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
        "public_entrypoint_case_status_counts",
        "large_input_source_case_status_counts",
        "first_party_source_inventory_family_count",
        "actually_tested_corrected_candidate_families",
        "currently_activated_candidate_family_count",
        "actually_runnable_candidate_family_count",
        "qualified_candidate_count",
        "final_comparison_planned_case_count",
        "final_comparison_cases_generated",
        "final_holdout_opened",
        "runtime_no_delegation",
        "performance",
        "memory",
        "confidence_intervals",
        "undefined_behavior",
        "winner_selected",
    )
    return {
        "schema": SCHEMA + suffix,
        "version": 59,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 58,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V58.items()},
        **{"feature_" + role + "_sha256": item[1]
           for role, item in FEATURE.items()},
        **{key: copy.deepcopy(snapshot[key]) for key in fields},
        "outputs_written": written,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V58:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role.replace("_", "-")
                            + "-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v58()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256" for role in V58)
            forbidden.extend(
                "feature_" + role + "_sha256" for role in FEATURE
            )
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(all(getattr(options, name) is None
                          for name in forbidden),
                      "source-only V59 self-test receives no actual pins")
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256,
                                  "complete current V59 graph source")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render only the three root-authorized V59 assets")
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(base, snapshot, outputs, source_sha,
                                    written=True, suffix="-published")
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "exact current V59 graph inputs"),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "exact current V59 graph summary"),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "exact current V59 graph image"),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True)
                base.need(raw == outputs[path],
                          "reproduce exact frozen V59 graph asset: " + path)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context")
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V59 overview rejected: "
                         + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V59 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
