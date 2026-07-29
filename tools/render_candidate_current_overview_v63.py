#!/usr/bin/env python3
"""Reconcile the corrected Python reference without inventing a passing suite."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import types

ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v63.py"
OUTPUT = "docs/evidence/candidate-current-overview-v63"
SCHEMA = "rebar-candidate-current-overview-v63"
V62 = {
    "source": (
        "tools/render_candidate_current_overview_v62.py",
        "f36b72ceb617487c8f49083364d13bcb53dd45380979ea193db8cedcc0d28233",
        69780,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v62.inputs.json",
        "c90559020a86e6c5805e22bc363e5731435db9d1acc079d4ac50c36a61ccd043",
        960530,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v62.json",
        "5877ac4b94e531e14b50b58c540e0e5b9334af8281328edb64b7633f079ab759",
        2637309,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v62.svg",
        "8c3a2261326fcec9944b57347bccb7c8553062e863792da8c5e106cf65389c57",
        14649,
    ),
}
EVIDENCE = {
    "reference_one": (
        "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-1.json",
        "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
        270,
    ),
    "reference_two": (
        "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-2.json",
        "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
        270,
    ),
    "aggregate": (
        "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/two-independent-reference-result.json",
        "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096",
        3658,
    ),
}
EVIDENCE_INODES = {
    "reference_one": 524693,
    "reference_two": 524692,
    "aggregate": 524707,
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
EVIDENCE_EXPECTATIONS = {
    "reference_one": {
        "cases": 8244,
        "expected_sha256": "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
        "failed": 0,
        "failures": [],
        "mapped_obligations": 45,
        "module": "re",
        "obligations": 45,
        "passed": 8244,
        "schema": "rebar-correctness-result-v2",
    },
    "reference_two": {
        "cases": 8244,
        "expected_sha256": "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
        "failed": 0,
        "failures": [],
        "mapped_obligations": 45,
        "module": "re",
        "obligations": 45,
        "passed": 8244,
        "schema": "rebar-correctness-result-v2",
    },
    "aggregate": {
        "actual_candidate_worker_count": 0,
        "actual_reference_worker_count": 2,
        "actual_reference_worker_process_ids": [
            81,
            82,
        ],
        "candidate_qualified": False,
        "candidate_status": "NOT RUN",
        "case_denominator_included_in_original_31237": False,
        "corpus_sha256": "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
        "frozen_seeds": {
            "deep_bytes": 1979121302,
            "deep_str": 1979121301,
            "invalid_patterns": 1511506921,
            "invalid_templates": 1511506922,
            "properties": 1511506920,
            "valid_bytes": 1511506919,
            "valid_str": 1511506918,
        },
        "holdout": "NOT OPENED",
        "label": "cpython-3146-two-worker-8244-v3",
        "mapped_obligation_count": 45,
        "memory": "NOT MEASURED",
        "native_build_status": "NOT RUN",
        "original_case_execution_denominator": 31237,
        "p0_completeness_v2": {
            "bytes": 28440,
            "device": 2064,
            "inode": 525073,
            "mode": "0600",
            "path": "oracle/phase1/p0-completeness-v2.json",
            "sha256": "fcd7abac619a6a4733e090cf49acbb958f8162eeb7dc6909a9d14501809e8237",
        },
        "performance": "NOT MEASURED",
        "pinned_cpython": {
            "bytes": 32387816,
            "device": 2049,
            "inode": 9594007,
            "mode": "0711",
            "path": "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
            "sha256": "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        },
        "protocol_sha256": "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
        "qualified_candidate_count": 0,
        "record_kind_counts": {
            "byteslike": 11,
            "byteslike-escape": 2,
            "cache": 1,
            "call": 7359,
            "compile": 2,
            "debug": 1,
            "error": 456,
            "escape": 2,
            "exports": 1,
            "flags": 1,
            "generic": 4,
            "match-copy": 3,
            "pattern-equality": 1,
            "positional-warning": 3,
            "property": 384,
            "representation": 5,
            "roundtrip": 1,
            "scanner": 2,
            "warning": 5,
        },
        "schema": "rebar-owned-differential-fuzz-reference-v3-actual-reference",
        "source_sha256": "9367bf224996296a9c8a0e01040d0776b292984e1a8b7a6362c8e943c27438ac",
        "status": "PASS",
        "supplemental_case_count": 8244,
        "winner_selected": False,
        "workers": [
            {
                "case_count": 8244,
                "exit_code": 0,
                "failed": 0,
                "failures": [],
                "module": "re",
                "passed": 8244,
                "pid": 81,
                "result": {
                    "bytes": 270,
                    "device": 2064,
                    "inode": 524693,
                    "mode": "0600",
                    "path": "/home/dev-user/src/rebar/oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-1.json",
                    "sha256": "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
                },
                "result_schema": "rebar-correctness-result-v2",
                "role": "independent-reference-a",
                "stderr": {
                    "bytes": 0,
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "text": "",
                },
                "stdout": {
                    "bytes": 234,
                    "sha256": "c8e57eba27a87f84adf0667fc5111e20894f21d4b39353dc5c490ffb41b691c7",
                    "text": "{\"cases\": 8244, \"expected_sha256\": \"ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2\", \"failed\": 0, \"mapped_obligations\": 45, \"module\": \"re\", \"obligations\": 45, \"passed\": 8244, \"schema\": \"rebar-correctness-result-v2\"}\n",
                },
            },
            {
                "case_count": 8244,
                "exit_code": 0,
                "failed": 0,
                "failures": [],
                "module": "re",
                "passed": 8244,
                "pid": 82,
                "result": {
                    "bytes": 270,
                    "device": 2064,
                    "inode": 524692,
                    "mode": "0600",
                    "path": "/home/dev-user/src/rebar/oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-2.json",
                    "sha256": "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
                },
                "result_schema": "rebar-correctness-result-v2",
                "role": "independent-reference-b",
                "stderr": {
                    "bytes": 0,
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "text": "",
                },
                "stdout": {
                    "bytes": 234,
                    "sha256": "c8e57eba27a87f84adf0667fc5111e20894f21d4b39353dc5c490ffb41b691c7",
                    "text": "{\"cases\": 8244, \"expected_sha256\": \"ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2\", \"failed\": 0, \"mapped_obligations\": 45, \"module\": \"re\", \"obligations\": 45, \"passed\": 8244, \"schema\": \"rebar-correctness-result-v2\"}\n",
                },
            },
        ],
    },
}


def load_v62() -> tuple:
    path, fingerprint, size = V62["source"]
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
            raise ValueError("reject substituted exact pushed V62 source")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated pushed V62 source")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended pushed V62 source")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed exact pushed V62 source")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v62")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v61()
    base = prior_modules[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v62"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS
        and previous.WORKERS == WORKERS,
        "authenticate only exact pushed current V62 graph source",
    )
    return previous, prior_modules, base



def v62_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V62["source"][1],
        source_bytes=V62["source"][2],
        previous_source_sha256=previous.V61["source"][1],
        previous_inputs_sha256=previous.V61["inputs"][1],
        previous_summary_sha256=previous.V61["summary"][1],
        previous_svg_sha256=previous.V61["svg"][1],
        reference_source_sha256=previous.REFERENCE["source"][1],
        reference_protocol_sha256=previous.REFERENCE["protocol"][1],
        reference_contract_sha256=previous.REFERENCE["contract"][1],
        inputs_sha256=None,
        summary_sha256=None,
        svg_sha256=None,
    )

def authenticate_v62(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V62.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V62 " + role)
            == item[1],
            "reject substituted corrected pushed V62 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete genuine V62 summary")
    inputs = base.document(raw["inputs"], "complete genuine V62 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(prior_modules, v62_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v62-summary"
        and old.get("version") == 62
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V62["source"])
        and old.get("inputs") == base.pin(*V62["inputs"])
        and old.get("svg") == base.pin(*V62["svg"])
        and inputs.get("schema")
            == "rebar-candidate-current-overview-v62-inputs"
        and inputs.get("version") == 62
        and inputs.get("renderer") == base.pin(*V62["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V62["inputs"][0]]
        and raw["summary"] == expected[V62["summary"][0]]
        and raw["svg"] == expected[V62["svg"][0]]
        and old.get("actual_current_graph_predecessor_version") == 61
        and old["snapshot"].get("actual_current_graph_predecessor_version")
            == 61
        and inputs.get("actual_current_graph_predecessor_version") == 61
        and old.get("actual_rust_semantic_mismatch_count") == 1440
        and old.get("actual_rust_verified_passing_case_count") == 14853
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count")
            == 8965
        and old.get("actual_rust_v10_candidate_status") == "FAIL"
        and old.get("actual_rust_v10_candidate_workers") == 13
        and old.get("actual_rust_v10_worker_process_ids") == WORKERS
        and old.get("actual_rust_v10_semantic_mismatch_regression_against_v7")
            == 512
        and old.get("actual_rust_v10_infrastructure_failure_count") == 0
        and old.get("actual_rust_v10_all_four_original_targets_restored")
            is True
        and len(old.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results",
            [],
        )) == 13
        and len(old.get("actual_rust_v10_earliest_genuine_mismatch_witnesses",
                        [])) == 6
        and old.get("candidate_facing_self_oracle_status") == "BLOCKED"
        and old.get("phase1_completeness_status") == "BLOCKED"
        and old.get("phase1_corrected_crosswalk_status") == "PASS"
        and old.get("phase1_canonical_candidate_context_crosswalk") == "PASS"
        and old.get("phase1_v2_reconciliation") == "BLOCKED"
        and old.get("phase1_v1_public_type_reference_status") == "FALSIFIED"
        and old.get("phase1_v2_corrected_reference_case_count") == 6912
        and old.get("phase1_v2_corrected_reference_process_ids") == [81, 82]
        and old.get("phase1_v2_supplemental_fuzz_unique_record_count")
            == 8244
        and len(old.get("phase1_v2_correctness_gate_blockers", [])) == 7
        and old.get("candidate_evaluation_authorized") is False
        and old.get("phase1_differential_fuzz_reference_v3_execution_status")
            == "NOT RUN"
        and old.get("phase1_differential_fuzz_reference_v3_worker_count") == 0
        and old.get(
            "phase1_differential_fuzz_reference_v3_worker_process_ids") == []
        and old.get("rust_native_build_v17_status") == "NOT RUN"
        and old.get("rust_native_build_v17_authorization_status") == "BLOCKED"
        and old.get("authenticated_evidence_owner_lower_bound") == 210
        and old.get("authenticated_history_reference_lower_bound") == 215
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("qualified_candidate_count") == 0
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce pushed V62, true predecessor and all genuine Rust evidence",
    )
    return old, inputs, raw["svg"]

def evidence_expectations() -> dict:
    return copy.deepcopy(EVIDENCE_EXPECTATIONS)


def make_evidence_proof(base: types.ModuleType, owners: dict,
                        documents: dict) -> dict:
    aggregate = documents["aggregate"]
    return {
        "schema": SCHEMA + "-authenticated-actual-fuzz-reference-v3",
        "version": 3,
        "status": "PASS",
        "actual_outcome": "PASS",
        "label": "cpython-3146-two-worker-8244-v3",
        "actual_reference_worker_count": 2,
        "actual_reference_worker_process_ids": [81, 82],
        "actual_reference_worker_exit_codes": [0, 0],
        "actual_reference_cases_per_worker": [8244, 8244],
        "actual_reference_failures_per_worker": [0, 0],
        "actual_distinct_reference_owner_inodes": [524693, 524692],
        "actual_reference_corpus_sha256":
            "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
        "actual_frozen_seed_count": len(aggregate["frozen_seeds"]),
        "actual_record_kind_count": len(aggregate["record_kind_counts"]),
        "actual_mapped_obligation_count": aggregate["mapped_obligation_count"],
        "candidate_status": "NOT RUN",
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "workers_started_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "holdout_files_opened_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "native_libraries_loaded_by_graph": 0,
        "clock_samples_by_graph": 0,
        "owners": copy.deepcopy(owners),
        "complete_actual_reference_documents": copy.deepcopy(documents),
    }

def validate_evidence_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject missing independently executed two-reference evidence")
    assert isinstance(proof, dict)
    documents = evidence_expectations()
    owners = {
        role: base.synthetic_owner(item, EVIDENCE_INODES[role])
        for role, item in EVIDENCE.items()
    }
    expected = make_evidence_proof(base, owners, documents)
    base.need(set(proof) == set(expected),
              "reject omitted or invented actual-reference evidence")
    for key, value in expected.items():
        base.need(
            type(proof.get(key)) is type(value)
            and proof.get(key) == value,
            "reject fabricated current reference evidence: " + key,
        )
    aggregate = proof["complete_actual_reference_documents"]["aggregate"]
    first = proof["complete_actual_reference_documents"]["reference_one"]
    second = proof["complete_actual_reference_documents"]["reference_two"]
    workers = aggregate["workers"]
    base.need(
        aggregate["schema"]
            == "rebar-owned-differential-fuzz-reference-v3-actual-reference"
        and aggregate["label"] == "cpython-3146-two-worker-8244-v3"
        and aggregate["status"] == "PASS"
        and aggregate["actual_reference_worker_count"] == 2
        and aggregate["actual_reference_worker_process_ids"] == [81, 82]
        and len(workers) == 2
        and workers[0]["role"] == "independent-reference-a"
        and workers[1]["role"] == "independent-reference-b"
        and workers[0]["pid"] == 81
        and workers[1]["pid"] == 82
        and workers[0]["exit_code"] == 0
        and workers[1]["exit_code"] == 0
        and workers[0]["case_count"] == 8244
        and workers[1]["case_count"] == 8244
        and workers[0]["passed"] == 8244
        and workers[1]["passed"] == 8244
        and workers[0]["failed"] == 0
        and workers[1]["failed"] == 0
        and workers[0]["result"]["inode"] == 524693
        and workers[1]["result"]["inode"] == 524692
        and workers[0]["result"]["inode"]
            != workers[1]["result"]["inode"]
        and workers[0]["result"]["sha256"] == EVIDENCE["reference_one"][1]
        and workers[1]["result"]["sha256"] == EVIDENCE["reference_two"][1]
        and first["passed"] == 8244 and first["failed"] == 0
        and second["passed"] == 8244 and second["failed"] == 0
        and first["expected_sha256"] == second["expected_sha256"]
        and first["expected_sha256"] == aggregate["corpus_sha256"]
        and aggregate["supplemental_case_count"] == 8244
        and len(aggregate["record_kind_counts"]) == 19
        and aggregate["mapped_obligation_count"] == 45
        and len(aggregate["frozen_seeds"]) == 7
        and aggregate["original_case_execution_denominator"] == 31237
        and aggregate["case_denominator_included_in_original_31237"]
            is False
        and aggregate["candidate_status"] == "NOT RUN"
        and aggregate["actual_candidate_worker_count"] == 0
        and aggregate["qualified_candidate_count"] == 0
        and aggregate["candidate_qualified"] is False
        and aggregate["holdout"] == "NOT OPENED"
        and aggregate["performance"] == "NOT MEASURED"
        and aggregate["memory"] == "NOT MEASURED"
        and aggregate["winner_selected"] is False,
        "bind two genuinely distinct current workers, never historical aliases",
    )

def authenticate_evidence(base: types.ModuleType,
                          options: argparse.Namespace) -> dict:
    owners = {}
    documents = {}
    for role, item in EVIDENCE.items():
        supplied = getattr(options, "evidence_" + role + "_sha256")
        base.need(
            base.checked(supplied, "exact actual reference " + role)
            == item[1],
            "reject substituted actual reference evidence: " + role,
        )
        raw, meta = base.read_owner(*item, private=True)
        base.need(
            meta["device"] == 2064
            and meta["inode"] == EVIDENCE_INODES[role]
            and meta["nlink"] == 1,
            "reject non-distinct actual worker evidence: " + role,
        )
        owners[role] = base.synthetic_owner(item, EVIDENCE_INODES[role])
        if role == "aggregate":
            documents[role] = base.document(
                raw, "complete canonical actual aggregate",
            )
        else:
            documents[role] = json.loads(raw.decode("utf-8"))
    base.need(
        documents == evidence_expectations(),
        "reject incomplete genuine two-worker reference observations",
    )
    proof = make_evidence_proof(base, owners, documents)
    validate_evidence_proof(base, proof)
    return proof

def result_fields(proof: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 62,
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_rust_verified_passing_case_count": 14853,
        "rust_actual_semantic_mismatch_count": 1440,
        "rust_original_campaign_semantic_mismatch_count": 1440,
        "rust_original_campaign_verified_passing_case_count": 14853,
        "rust_verified_passing_case_executions": 14853,
        "candidate_facing_self_oracle_status": "BLOCKED",
        "phase1_completeness_status": "BLOCKED",
        "phase1_corrected_crosswalk_status": "PASS",
        "phase1_canonical_candidate_context_crosswalk": "PASS",
        "phase1_v2_reconciliation": "BLOCKED",
        "phase1_v1_public_type_reference_status": "FALSIFIED",
        "phase1_v2_corrected_reference_case_count": 6912,
        "phase1_v2_corrected_reference_process_ids": [81, 82],
        "phase1_v2_supplemental_fuzz_stream_status": "VERIFIED",
        "phase1_v2_supplemental_fuzz_unique_record_count": 8244,
        "phase1_v2_supplemental_independently_referenced_case_count": 8244,
        "phase1_v2_supplemental_dual_reference_status": "PASS",
        "phase1_v2_supplemental_candidate_status": "NOT RUN",
        "supplemental_differential_fuzz_candidate_gate": "BLOCKED",
        "supplemental_differential_fuzz_case_count": 8244,
        "phase1_differential_fuzz_reference_v3_source_status":
            "SOURCE FROZEN",
        "phase1_differential_fuzz_reference_v3_execution_status": "PASS",
        "phase1_differential_fuzz_reference_v3_worker_count": 2,
        "phase1_differential_fuzz_reference_v3_worker_process_ids":
            [81, 82],
        "phase1_differential_fuzz_reference_v3_reference_case_count": 8244,
        "phase1_differential_fuzz_reference_v3_candidate_case_count": 0,
        "phase1_differential_fuzz_reference_v3_actual_result":
            copy.deepcopy(proof),
        "phase1_differential_fuzz_reference_v3_actual_worker_result_count": 2,
        "phase1_differential_fuzz_reference_v3_actual_worker_exit_codes":
            [0, 0],
        "phase1_differential_fuzz_reference_v3_actual_worker_case_counts":
            [8244, 8244],
        "phase1_differential_fuzz_reference_v3_actual_worker_failure_counts":
            [0, 0],
        "phase1_differential_fuzz_reference_v3_actual_worker_owner_inodes":
            [524693, 524692],
        "phase1_differential_fuzz_reference_v3_actual_run_label":
            "cpython-3146-two-worker-8244-v3",
        "genuine_2gib_candidate_search": "NOT RUN",
        "genuine_2gib_candidate_substitution": "NOT RUN",
        "candidate_evaluation_authorized": False,
        "rust_native_build_v17_source_status": "SOURCE FROZEN",
        "rust_native_build_v17_status": "NOT RUN",
        "rust_native_build_v17_authorization_status": "BLOCKED",
        "rust_native_build_v17_blocking_reason":
            "PHASE 1 CANDIDATE CORRECTNESS NOT ESTABLISHED",
        "rust_native_build_v17_matching_status": "NOT RUN",
        "rust_native_build_v17_candidate_correctness": "NOT MEASURED",
        "rust_native_build_v17_candidate_qualified": False,
        "rust_native_build_v17_compiler_process_count": 0,
        "rust_native_build_v17_compiler_process_ids": [],
        "rust_native_build_v17_native_binary_count": 0,
        "rust_native_build_v17_native_artifact_hashes": [],
        "rust_native_build_v17_candidate_workers_started": 0,
        "rust_native_build_v17_independent_source_owner_count": 3,
        "authenticated_evidence_owner_lower_bound": 213,
        "authenticated_history_reference_lower_bound": 218,
        "actual_reference_evidence_owners_read_by_graph": 3,
        "actual_reference_workers_started_by_graph": 0,
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
              "reject missing genuine two-reference V63 graph snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("phase1_differential_fuzz_reference_v3_actual_result")
    validate_evidence_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(
            type(snapshot.get(key)) is type(value)
            and snapshot.get(key) == value,
            "reject invented genuine reference or candidate result: " + key,
        )
    replaced = snapshot.get("preserved_v62_replaced_snapshot_fields")
    base.need(type(replaced) is dict and set(replaced).issubset(updates),
              "preserve every exact replaced pushed V62 evidence field")
    assert isinstance(replaced, dict)
    base.need(
        replaced.get("actual_current_graph_predecessor_version") == 61
        and replaced.get(
            "phase1_differential_fuzz_reference_v3_execution_status")
            == "NOT RUN"
        and replaced.get(
            "phase1_differential_fuzz_reference_v3_worker_count") == 0
        and replaced.get(
            "phase1_differential_fuzz_reference_v3_worker_process_ids")
            == [],
        "retain immutable V62 predecessor and previously unrun reference",
    )
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v62_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(prior_modules, history)
    base.need(
        snapshot.get("actual_current_graph_predecessor_version") == 62
        and snapshot.get("actual_rust_semantic_mismatch_count") == 1440
        and snapshot.get("actual_rust_verified_passing_case_count") == 14853
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get("actual_rust_v7_explicitly_verified_passing_case_count")
            == 8965
        and snapshot.get("actual_rust_v10_candidate_status") == "FAIL"
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
        and snapshot.get("phase1_v2_correctness_gate_blockers")
            == history.get("phase1_v2_correctness_gate_blockers")
        and len(snapshot.get("phase1_v2_correctness_gate_blockers", [])) == 7
        and snapshot.get("phase1_v2_oracle_reconciliation")
            == history.get("phase1_v2_oracle_reconciliation")
        and snapshot.get("phase1_completeness_status") == "BLOCKED"
        and snapshot.get("phase1_v2_reconciliation") == "BLOCKED"
        and snapshot.get("rust_buffer_shape_v2_feature_status")
            == "SOURCE FROZEN"
        and snapshot.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and snapshot.get("rust_buffer_shape_v2_matching_status") == "NOT RUN"
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
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False,
        "preserve full V62 history and qualify no unrun candidate",
    )

def replace_once(base: types.ModuleType, visible: str,
                 before: str, after: str, description: str) -> str:
    base.need(type(visible) is str and type(before) is str
              and type(after) is str and visible.count(before) == 1,
              "reject substituted pushed V62 chart section: " + description)
    return visible.replace(before, after, 1)


def forged_value(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " [FORGED]"
    if type(value) is list:
        return copy.deepcopy(value) + ["FORGED"]
    if type(value) is dict:
        forged = copy.deepcopy(value)
        forged["__forged_v63__"] = True
        return forged
    if value is None:
        return "FORGED"
    return object()



def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact source-only V63 renderer")
    inputs_sha = base.checked(inputs_sha, "exact source-only V63 inputs")
    visible = old_svg.decode("utf-8").replace(
        "v62-title", "v63-title").replace(
        "v62-description", "v63-description")
    lines = visible.splitlines()
    base.need(
        len(lines) > 10
        and lines[1].startswith('<title id="v63-title">')
        and lines[2].startswith('<desc id="v63-description">'),
        "preserve exact pushed accessible V62 graph",
    )
    lines[1] = (
        '<title id="v63-title">Building a faster Python re: two '
        'independent Python runs pass all 8,244 fuzz tests; '
        'replacement engines are not yet compatible</title>'
    )
    lines[2] = (
        '<desc id="v63-description">The pinned Python 3.14.6 '
        'baseline has now genuinely passed all 8,244 separately '
        'counted fuzz, differential and property cases in two '
        'independent subprocesses. Actual current-run PIDs 81 and '
        '82, separately owned output inodes 524693 and 524692, '
        'two observed exit codes of zero, 8,244 explicit passes '
        'per worker, the aggregate record, the exact corpus '
        'checksum, seven seeds, 19 categories and 45 mapped '
        'obligations are independently authenticated. Matching '
        'historical PID numbers or identical result bytes are '
        'not used as evidence of independence. This result is a '
        'Python-reference PASS only. The historically published '
        'phase-one V2 contract remains BLOCKED. Candidate fuzz '
        'tests are NOT RUN; no replacement is compatible or '
        'qualified. The latest actual from-scratch Rust test '
        'still has 1,440 compatibility differences, 14,853 '
        'explicitly verified passes, 13 real workers, 13 suites '
        'and six exact genuine mismatch witnesses. Historical '
        'V7 has 928 differences and 8,965 verified passes; the '
        'current regression is 512 differences. Exactly three '
        'actual current reference evidence owners raise evidence '
        'and historical lower bounds from 210 / 215 to 213 / '
        '218. Original 31,237 cases, 50 signature checks, 32 '
        'public-interface observations, 32 large-input '
        'observations and the 8,244 fuzz cases retain separate '
        'denominators. Six first-party families and zero '
        'qualified replacements remain. Native builds and '
        'the native repair is NOT BUILT; candidate matching '
        'is NOT RUN; 0 compilers and '
        '0 binaries exist. The final '
        '4,194,304-case holdout is NOT OPENED and not generated. '
        'Performance, memory, confidence intervals and undefined '
        'behavior are NOT MEASURED; runtime independence is '
        'NOT ESTABLISHED.</desc>'
    )
    visible = "\n".join(lines)
    replacements = (
        (
            '<text x="65" y="398" class="heading">Python reference '
            'fixed; next 8,244-case test not yet run</text>',
            '<text x="65" y="398" class="heading">Two Python runs '
            'pass 8,244 tests; engines still unproven</text>',
            "show the actual reference PASS without qualifying candidates",
        ),
        (
            'Two Python runs confirm 6,912 reference cases. The '
            '8,244-case follow-up is SOURCE FROZEN and NOT RUN.',
            'Two real Python processes each pass all 8,244 tests. '
            'Replacement-engine tests remain NOT RUN.',
            "separate two genuine Python workers from candidate execution",
        ),
        (
            '<text x="64" y="1756" class="heading">Next Python '
            'reference test frozen; zero workers have run</text>',
            '<text x="64" y="1756" class="heading">Two genuine '
            'Python reference workers passed; candidates have not run</text>',
            "report authenticated reference outcome and zero candidates",
        ),
        (
            'Exactly three reference-source owners raise current '
            'lower bounds from 207 / 212 to 210 / 215.',
            'Exactly three actual reference-result owners raise '
            'lower bounds from 210 / 215 to 213 / 218.',
            "count only the genuine current-run three evidence owners",
        ),
        (
            'Real Rust failures remain proven. Full correctness '
            'stays BLOCKED; the next reference test has zero '
            'workers, candidate runs or speed results.',
            'Real Rust failures remain proven. Two Python '
            'reference workers passed; candidate correctness '
            'remains BLOCKED and speed is NOT MEASURED.',
            "retain historical failures and never invent candidate results",
        ),
    )
    for before, after, why in replacements:
        visible = replace_once(base, visible, before, after, why)
    lines = visible.splitlines()
    start = next(
        (i for i, line in enumerate(lines)
         if line.startswith('<rect x="44" y="1858" width="1352"')),
        None,
    )
    base.need(type(start) is int, "preserve pushed V62 graph evidence panel")
    assert isinstance(start, int)
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="381" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact two-process '
        'Python results and preserved replacement-engine evidence</text>',
    ))
    v58 = prior_modules[1][1][1][0]
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V62 graph inputs SHA-256", V62["inputs"][1]),
        ("Historical V62 graph renderer SHA-256", V62["source"][1]),
        ("Historical V62 graph summary SHA-256", V62["summary"][1]),
        ("Historical V62 graph image SHA-256", V62["svg"][1]),
        ("Actual first Python worker output SHA-256",
         EVIDENCE["reference_one"][1]),
        ("Actual second distinct Python worker output SHA-256",
         EVIDENCE["reference_two"][1]),
        ("Actual two-worker reference result SHA-256",
         EVIDENCE["aggregate"][1]),
        ("Small actual failed Rust receipt SHA-256", v58.RECEIPT[1]),
        ("Complete independent Rust failure summary SHA-256",
         v58.FORENSIC[1]),
        ("Historical compressed failure SHA-256 (not opened)",
         v58.ARCHIVE_SHA),
    )
    for i, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + i * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2139" class="small">Actual Python workers: '
        '2; PIDs 81 and 82; both pass 8,244 cases.</text>',
        '<text x="65" y="2158" class="small">Distinct output '
        'inodes: 524693 and 524692. Candidate tests: NOT RUN.</text>',
        '<text x="65" y="2177" class="small">Actual Rust: '
        '1,440 differences; 14,853 verified passes; '
        '13 real workers.</text>',
        '<text x="65" y="2196" class="small">Historical P0: '
        'BLOCKED. Qualified engines: 0. Speed: NOT MEASURED.</text>',
        '<text x="65" y="2215" class="small">Six first-party '
        'families. Final holdout: NOT OPENED.</text>',
        '<!-- Graph only authenticates actual existing worker records; '
        'it does not run another reference, open an archive or corpus, '
        'start a candidate or compiler, read clocks, measure speed, '
        'load native libraries or access the hidden holdout. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in footers:
        base.need(
            raw.count((label + ": " + value).encode("ascii")) == 1,
            "bind one authenticated actual V63 graph footer: " + label,
        )
    lower = raw.lower()
    for phrase in (
            b'height="2250"', b"building a faster python re",
            b"two independent python runs", b"8,244", b"2",
            b"pids 81 and 82", b"524693", b"524692",
            b"exit codes of zero", b"seven seeds", b"19 categories",
            b"45 mapped", b"candidate", b"not run",
            b"blocked", b"1,440", b"14,853", b"13 real workers",
            b"512", b"928", b"8,965",
            b"managed 16", b"substitution 368", b"shape 1,056",
            b"31,237", b"4.2m unopened", b"not opened",
            b"not built", b"0 compilers", b"0 binaries",
            b"not measured", b"not established",
            b"210 / 215", b"213 / 218",
            b"signature checks", b"public-interface observations",
            b"large-input observations", b"17 pass", b"7 fail",
            b"22 pass", b"3 not run", b"2,147,483,648",
            b"1,087", b"1,036", b"1,262", b"1,230",
            b"2,172", b"1,764", b"not generated"):
        base.need(phrase in lower,
                  "preserve genuine two-worker outcome: " + repr(phrase))
    for falsehood in (
            b"candidate qualified", b"three qualified candidates",
            b"candidate fuzz tests passed",
            b"full test suite passed", b"phase-one v2 passed",
            b"holdout opened", b"holdout generated",
            b"benchmark speedup", b"winner selected",
            b"verify_p0_completeness_v2.py"):
        base.need(falsehood not in lower,
                  "reject invented V63 result: " + repr(falsehood))
    return raw

def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact actual-reference V63 graph renderer")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "bound the exact independent V63 source owner",
    )
    own_raw, _ = base.read_owner(
        SELF, source_sha, options.source_bytes, private=True,
    )
    old, old_inputs, old_svg = authenticate_v62(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V62},
    )
    proof = authenticate_evidence(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v62_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V62.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 63,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessor,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(
        modules, snapshot, old_svg, source_sha, base.digest(input_raw),
    )
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve Python and exactly six independently owned engine families",
    )
    for row in families:
        if row.get("family") == "python":
            row.update({
                "supplemental_reference_status": "PASS",
                "supplemental_reference_worker_count": 2,
                "supplemental_reference_case_count": 8244,
            })
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 213,
            "authenticated_history_reference_lower_bound": 218,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
            "phase1_completeness_status": "BLOCKED",
            "phase1_corrected_crosswalk_status": "PASS",
            "candidate_evaluation_authorized": False,
            "differential_fuzz_reference_source_status": "SOURCE FROZEN",
            "differential_fuzz_reference_execution_status": "PASS",
            "differential_fuzz_reference_worker_count": 2,
            "differential_fuzz_candidate_status": "NOT RUN",
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
                "native_build_v17_source_status": "SOURCE FROZEN",
                "native_build_v17_status": "NOT RUN",
                "native_build_v17_candidate_matching_status": "NOT RUN",
                "native_build_v17_candidate_correctness": "NOT MEASURED",
                "native_build_v17_compiler_process_count": 0,
                "native_build_v17_native_binary_count": 0,
                "native_build_v17_candidate_workers_started": 0,
                "native_build_v17_independent_source_owner_count": 3,
                "differential_fuzz_actual_reference":
                    copy.deepcopy(proof),
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 63,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    base.need(
        inputs["actual_current_graph_predecessor_version"] == 62
        and summary["actual_current_graph_predecessor_version"] == 62
        and snapshot["actual_current_graph_predecessor_version"] == 62
        and snapshot["preserved_v62_replaced_snapshot_fields"][
            "actual_current_graph_predecessor_version"] == 61
        and summary["previous_overview"]["source"]["path"]
            == V62["source"][0],
        "bind true V62 predecessor in every complete V63 graph owner",
    )
    summary_raw = base.canonical(summary)
    base.need(
        max(len(input_raw), len(summary_raw), len(svg))
        <= base.OWNER_LIMIT,
        "bound exactly three independently owned V63 graph outputs",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )

def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_evidence_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted fabricated two-worker evidence: "
                          + description)

def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 5046
        and prior.get("actual_current_graph_predecessor_version") == 61
        and prior.get("actual_rust_semantic_mismatch_count") == 1440
        and prior.get("actual_rust_verified_passing_case_count") == 14853
        and prior.get("actual_rust_v10_candidate_status") == "FAIL"
        and prior.get("actual_rust_v10_candidate_workers") == 13
        and prior.get("phase1_completeness_status") == "BLOCKED"
        and prior.get("phase1_corrected_crosswalk_status") == "PASS"
        and prior.get("phase1_v2_corrected_reference_case_count") == 6912
        and prior.get("phase1_differential_fuzz_reference_v3_execution_status")
            == "NOT RUN"
        and prior.get("phase1_differential_fuzz_reference_v3_worker_count")
            == 0
        and prior.get("candidate_evaluation_authorized") is False
        and prior.get("authenticated_evidence_owner_lower_bound") == 210
        and prior.get("authenticated_history_reference_lower_bound") == 215
        and prior.get("actual_failure_archives_opened_by_self_test") == 0,
        "preserve exactly 5,046 V62 controls and immutable frozen history",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item, EVIDENCE_INODES[role])
            for role, item in EVIDENCE.items()
        }
        proof = make_evidence_proof(base, owners, evidence_expectations())
        validate_evidence_proof(base, proof)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = forged_value(value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for role, owner in proof["owners"].items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = forged_value(value)
                rejected += reject_control(
                    base, hostile, "owner:" + role + ":" + key,
                )
        for key, value in proof["complete_actual_reference_documents"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_actual_reference_documents"][key] = (
                forged_value(value)
            )
            rejected += reject_control(base, hostile, "result:" + key)
        for key, value in proof[
                "complete_actual_reference_documents"]["aggregate"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_actual_reference_documents"][
                "aggregate"][key] = forged_value(value)
            rejected += reject_control(base, hostile, "aggregate:" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v63")),
            ("filesystem", lambda: os.open("forbidden-v63", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v63")),
            ("write", lambda: os.mkdir("forbidden-v63")),
            ("process", lambda: subprocess.run(("forbidden-v63",))),
            ("process", lambda: subprocess.Popen(("forbidden-v63",))),
            ("process", lambda: os.execv("/forbidden-v63", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically forbid actual-result V63 " + kind,
                )
            else:
                raise base.GraphError("allowed forbidden V63 " + kind)
        base.need(rejected >= 50,
                  "reject forged actual workers, corpus and aggregate")
        updates = result_fields(proof)
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 63,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v62_hostile_controls": 5046,
            "new_v63_hostile_controls": rejected,
            "rejected_hostile_control_count": 5046 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_reference_evidence_owners_read_by_self_test": 0,
            "actual_fuzz_reference_source_owners_read_by_self_test": 0,
            "actual_phase1_oracle_source_owners_read_by_self_test": 0,
            "actual_feature_source_owners_read_by_self_test": 0,
            "actual_build_source_owners_read_by_self_test": 0,
            "actual_forensic_summary_owners_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            **updates,
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
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
            "holdout": "NOT OPENED",
        }

def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json",
                       OUTPUT + ".svg"}
              and type(raw) is bytes
              and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only three root-authorized complete V63 graph files")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact independently owned V63 byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid()
                  and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish exactly one private complete V63 graph owner")
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
              "reauthenticate exactly one complete current V63 graph owner")



def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    fields = (
        "actual_current_graph_predecessor_version",
        "actual_rust_semantic_mismatch_count",
        "actual_rust_verified_passing_case_count",
        "rust_original_campaign_semantic_mismatch_count",
        "rust_original_campaign_verified_passing_case_count",
        "actual_rust_v7_semantic_mismatch_count",
        "actual_rust_v7_explicitly_verified_passing_case_count",
        "actual_rust_v10_candidate_status",
        "actual_rust_v10_semantic_mismatch_count",
        "actual_rust_v10_verified_passing_case_count",
        "actual_rust_v10_semantic_mismatch_regression_against_v7",
        "actual_rust_v10_candidate_workers",
        "actual_rust_v10_worker_process_ids",
        "actual_rust_v10_infrastructure_failure_count",
        "actual_rust_v10_all_four_original_targets_restored",
        "rust_buffer_shape_v2_feature_status",
        "rust_buffer_shape_v2_build_status",
        "rust_buffer_shape_v2_matching_status",
        "candidate_facing_self_oracle_status",
        "phase1_completeness_status",
        "phase1_corrected_crosswalk_status",
        "phase1_canonical_candidate_context_crosswalk",
        "phase1_v2_reconciliation",
        "phase1_v1_public_type_reference_status",
        "phase1_v2_corrected_reference_case_count",
        "phase1_v2_corrected_reference_process_ids",
        "phase1_v2_supplemental_fuzz_stream_status",
        "phase1_v2_supplemental_fuzz_unique_record_count",
        "phase1_v2_supplemental_independently_referenced_case_count",
        "phase1_v2_supplemental_dual_reference_status",
        "phase1_v2_supplemental_candidate_status",
        "phase1_v2_correctness_gate_blockers",
        "supplemental_differential_fuzz_candidate_gate",
        "supplemental_differential_fuzz_case_count",
        "phase1_differential_fuzz_reference_v3_source_status",
        "phase1_differential_fuzz_reference_v3_execution_status",
        "phase1_differential_fuzz_reference_v3_worker_count",
        "phase1_differential_fuzz_reference_v3_worker_process_ids",
        "phase1_differential_fuzz_reference_v3_reference_case_count",
        "phase1_differential_fuzz_reference_v3_candidate_case_count",
        "phase1_differential_fuzz_reference_v3_actual_worker_result_count",
        "phase1_differential_fuzz_reference_v3_actual_worker_exit_codes",
        "phase1_differential_fuzz_reference_v3_actual_worker_case_counts",
        "phase1_differential_fuzz_reference_v3_actual_worker_failure_counts",
        "phase1_differential_fuzz_reference_v3_actual_worker_owner_inodes",
        "phase1_differential_fuzz_reference_v3_actual_run_label",
        "genuine_2gib_candidate_search",
        "genuine_2gib_candidate_substitution",
        "candidate_evaluation_authorized",
        "rust_native_build_v17_source_status",
        "rust_native_build_v17_status",
        "rust_native_build_v17_authorization_status",
        "rust_native_build_v17_blocking_reason",
        "rust_native_build_v17_matching_status",
        "rust_native_build_v17_candidate_correctness",
        "rust_native_build_v17_candidate_qualified",
        "rust_native_build_v17_compiler_process_count",
        "rust_native_build_v17_compiler_process_ids",
        "rust_native_build_v17_native_binary_count",
        "rust_native_build_v17_native_artifact_hashes",
        "rust_native_build_v17_candidate_workers_started",
        "rust_native_build_v17_independent_source_owner_count",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
        "public_entrypoint_case_status_counts",
        "large_input_source_case_status_counts",
        "first_party_source_inventory_family_count",
        "actually_tested_corrected_candidate_families",
        "actually_tested_corrected_candidate_family_count",
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
        "version": 63,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 62,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V62.items()},
        **{"evidence_" + role + "_sha256": item[1]
           for role, item in EVIDENCE.items()},
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
    for role in V62:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in EVIDENCE:
        parser.add_argument(
            "--evidence-" + role.replace("_", "-") + "-sha256",
        )
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v62()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256"
                             for role in V62)
            forbidden.extend("evidence_" + role + "_sha256"
                             for role in EVIDENCE)
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(
                all(getattr(options, name) is None for name in forbidden),
                "actual-result source-only V63 self-test uses no real owners",
            )
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(
            options.source_sha256, "exact complete actual-result renderer",
        )
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "publish exactly three root-authorized V63 graph assets",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "actual complete V63 inputs",
                ),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "actual complete V63 summary",
                ),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "actual complete V63 chart",
                ),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True,
                )
                base.need(
                    raw == outputs[path],
                    "reproduce complete actual V63 graph output: " + path,
                )
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context",
            )
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V63 overview rejected: "
                         + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V63 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
