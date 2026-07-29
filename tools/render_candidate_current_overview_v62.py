#!/usr/bin/env python3
"""Reconcile the corrected Python reference without inventing a passing suite."""

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
SELF = "tools/render_candidate_current_overview_v62.py"
OUTPUT = "docs/evidence/candidate-current-overview-v62"
SCHEMA = "rebar-candidate-current-overview-v62"
V61 = {
    "source": (
        "tools/render_candidate_current_overview_v61.py",
        "07d0df394407ad1c6496ac837a7c55304bda68602a57c017e8d06deb3f45dd52",
        97292,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v61.inputs.json",
        "9be09cfe487efde257116ddd4e58e7ff78152394c6fc3d5e2b95356f7b56f2e2",
        953178,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v61.json",
        "0a71008327f2212d3e337b7c3f265904fe65bba10e5a43133eaaed7cb6367b24",
        2612089,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v61.svg",
        "fd40f66d731185151dad7d692c1abab7d15e98a29e2df63eade3bb9d86d03fb0",
        14766,
    ),
}
REFERENCE = {
    "source": (
        "tools/run_owned_differential_fuzz_reference_v3.py",
        "9367bf224996296a9c8a0e01040d0776b292984e1a8b7a6362c8e943c27438ac",
        43757,
    ),
    "protocol": (
        "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
        "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
        3929,
    ),
    "contract": (
        "oracle/phase1/p0-differential-fuzz-reference-v3.json",
        "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
        5288,
    ),
}
REFERENCE_INODES = {
    "source": 432216,
    "protocol": 525081,
    "contract": 525082,
}
STALE_PREDECESSOR_OUTPUTS = {
    "inputs": (
        "docs/evidence/candidate-current-overview-v62.inputs.json",
        "f30d5125735358aaaeed85f7d48c9c52c545c4f916fec2ac4e9176ae6b9c77f2",
        960530,
        432219,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v62.json",
        "3b833f20623e2ab439cf2d4667baec988278ba50d56edad940a035c96bf709cf",
        2637263,
        432220,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v62.svg",
        "adc209f8e91d09a9738cc5c7d8c08ca5e457772cc1124eb0090570b0ce6d8aff",
        14649,
        432221,
    ),
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
REFERENCE_CONTRACT_EXPECTATIONS = {
    "authenticated_inherited_source_owner_count": 61,
    "case_denominator_included_in_original_31237": False,
    "frozen_manifest": {
        "bytes": 1359,
        "device": 2064,
        "inode": 428246,
        "mode": "0600",
        "path": "oracle/v2/manifest.json",
        "sha256": "91ce7da8cd0ebcdf2861fbb82cd531855631e52815aa8c1684f6a798da6563f6",
    },
    "frozen_seeds": {
        "bytes": 210,
        "device": 2064,
        "inode": 428245,
        "mode": "0600",
        "path": "oracle/v2/seeds.json",
        "sha256": "761d074856c36880db60965583207c78a46b8fced204e0f3b4e03e744fed74c7",
    },
    "historical_single_context_worker_provenance": "NOT CAPTURED",
    "original_case_execution_denominator": 31237,
    "original_crosswalk_count": 34,
    "original_named_module_runner": {
        "bytes": 14248,
        "device": 2064,
        "inode": 428240,
        "mode": "0600",
        "path": "tools/oracle_v2.py",
        "sha256": "f038145dc0527f802203e18556f03b4bba636bb219105dc38c675c52a23e0fbb",
    },
    "original_named_private_waiver_count": 13,
    "original_obligation_count": 73,
    "original_suite_count": 13,
    "p0_completeness_v2": {
        "bytes": 28440,
        "device": 2064,
        "inode": 525073,
        "mode": "0600",
        "path": "oracle/phase1/p0-completeness-v2.json",
        "sha256": "fcd7abac619a6a4733e090cf49acbb958f8162eeb7dc6909a9d14501809e8237",
    },
    "p0_source_crosswalk_status": "PASS",
    "phase": "CORRECTNESS ORACLE",
    "phase1_canonical_candidate_context_crosswalk": "PASS",
    "phase_gate": {
        "candidate_evaluation_authorized": False,
        "final_holdout_authorized": False,
        "native_build_authorized": False,
        "performance_oracle_authorized": False,
        "qualified_candidate_count": 0,
        "status": "BLOCKED",
        "winner_selected": False,
    },
    "pinned_cpython": {
        "bytes": 32387816,
        "device": 2049,
        "inode": 9594007,
        "mode": "0711",
        "path": "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
        "sha256": "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
    },
    "planned_original_worker_command": [
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
        "-I",
        "-B",
        "/home/dev-user/src/rebar/tools/oracle_v2.py",
        "verify",
        "--module",
        "re",
    ],
    "planned_reference_roles": [
        "independent-reference-a",
        "independent-reference-b",
    ],
    "planned_reference_worker_count": 2,
    "planned_worker_context": {
        "locale": "C",
        "module": "re",
        "original_v1_named_module": "rebar_oracle_v1_runner",
        "process_start": "two actual independently observed os.posix_spawn PIDs",
        "result": "complete original result including all failures",
        "runner": "original unchanged tools/oracle_v2.py",
        "stdout_stderr": "both workers concurrently bounded and fully drained",
        "warnings": "original unchanged oracle warnings",
        "worker_output": "separate fresh exclusive result-directory files",
    },
    "protocol": {
        "bytes": 3929,
        "device": 2064,
        "inode": 525081,
        "mode": "0600",
        "path": "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
        "sha256": "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
    },
    "schema": "rebar-owned-differential-fuzz-reference-v3",
    "seeds": {
        "deep_bytes": 1979121302,
        "deep_str": 1979121301,
        "invalid_patterns": 1511506921,
        "invalid_templates": 1511506922,
        "properties": 1511506920,
        "valid_bytes": 1511506919,
        "valid_str": 1511506918,
    },
    "source": {
        "bytes": 43757,
        "device": 2064,
        "inode": 432216,
        "mode": "0600",
        "path": "tools/run_owned_differential_fuzz_reference_v3.py",
        "sha256": "9367bf224996296a9c8a0e01040d0776b292984e1a8b7a6362c8e943c27438ac",
    },
    "source_only_effects": {
        "actual_candidate_worker_count": 0,
        "actual_compiler_process_count": 0,
        "actual_native_activation_count": 0,
        "actual_reference_worker_count": 0,
        "actual_reference_worker_process_ids": [],
        "candidate_qualified": False,
        "candidate_status": "NOT RUN",
        "clock_sample_count": 0,
        "compressed_archive_open_count": 0,
        "hidden_holdout_open_count": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "network_operation_count": 0,
        "performance": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "two_independent_reference_process_status": "NOT RUN",
        "undefined_behavior": "NOT MEASURED",
    },
    "status": "BLOCKED",
    "supplemental_corpus": {
        "bytes": 7602476,
        "case_count": 8244,
        "device": 2064,
        "inode": 428243,
        "maximum_observed_record_bytes": 83668,
        "mode": "0600",
        "path": "oracle/v2/expected.jsonl",
        "per_record_limit_bytes": 262144,
        "plaintext_corpus_loaded_whole": False,
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
        "record_mapped_obligation_ids": [
            "API-BYTESLIKE",
            "API-COMPILE",
            "API-ESCAPE",
            "API-EXPORTS",
            "API-FINDALL",
            "API-FINDITER",
            "API-FLAGS",
            "API-FULLMATCH",
            "API-GENERIC",
            "API-MATCH",
            "API-MATCH-COPY",
            "API-MATCH-OBJECT",
            "API-PATTERN",
            "API-REPRESENTATION",
            "API-SCANNER",
            "API-SEARCH",
            "API-SPLIT",
            "API-SUB",
            "API-SUBN",
            "E-DEBUG",
            "E-DEPRECATION",
            "E-PATTERN",
            "E-TEMPLATE",
            "E-TYPE",
            "E-WARNING",
            "S-ALTERNATION",
            "S-ANCHOR",
            "S-ASCII",
            "S-ATOMIC",
            "S-BACKREF",
            "S-CONDITIONAL",
            "S-DEEP-FUZZ",
            "S-DOT-CLASS",
            "S-EMPTY",
            "S-GROUP",
            "S-INLINE",
            "S-LITERAL",
            "S-LOCALE",
            "S-LOOKAROUND",
            "S-LOOKBEHIND-REF",
            "S-POSSESSIVE",
            "S-QUANTIFIER",
            "S-UNICODE",
            "S-VERBOSE",
            "S-WINDOW",
        ],
        "sha256": "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
        "unique_record_case_count": 8244,
    },
    "v1_parent_corpus": {
        "bytes": 1203505,
        "case_count": 2048,
        "device": 2064,
        "inode": 427910,
        "maximum_observed_record_bytes": 40442,
        "mode": "0600",
        "path": "oracle/v1/expected.jsonl",
        "per_record_limit_bytes": 262144,
        "plaintext_corpus_loaded_whole": False,
        "sha256": "983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed",
    },
    "version": 3,
}


def load_v61() -> tuple:
    path, fingerprint, size = V61["source"]
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
            raise ValueError("reject substituted exact pushed V61 source")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated pushed V61 source")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended pushed V61 source")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed exact pushed V61 source")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v61")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v60()
    base = prior_modules[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v61"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS
        and previous.WORKERS == WORKERS,
        "authenticate only exact pushed current V61 graph source",
    )
    return previous, prior_modules, base



def v61_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V61["source"][1],
        source_bytes=V61["source"][2],
        previous_source_sha256=previous.V60["source"][1],
        previous_inputs_sha256=previous.V60["inputs"][1],
        previous_summary_sha256=previous.V60["summary"][1],
        previous_svg_sha256=previous.V60["svg"][1],
        oracle_source_sha256=previous.ORACLE["source"][1],
        oracle_protocol_sha256=previous.ORACLE["protocol"][1],
        oracle_contract_sha256=previous.ORACLE["contract"][1],
        inputs_sha256=None,
        summary_sha256=None,
        svg_sha256=None,
    )

def authenticate_v61(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V61.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V61 " + role)
            == item[1],
            "reject substituted actual pushed V61 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete actual pushed V61 summary")
    inputs = base.document(raw["inputs"], "complete actual pushed V61 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(prior_modules, v61_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v61-summary"
        and old.get("version") == 61
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V61["source"])
        and old.get("inputs") == base.pin(*V61["inputs"])
        and old.get("svg") == base.pin(*V61["svg"])
        and inputs.get("schema")
            == "rebar-candidate-current-overview-v61-inputs"
        and inputs.get("version") == 61
        and inputs.get("renderer") == base.pin(*V61["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V61["inputs"][0]]
        and raw["summary"] == expected[V61["summary"][0]]
        and raw["svg"] == expected[V61["svg"][0]]
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
        and old.get("phase1_v2_supplemental_fuzz_stream_status")
            == "VERIFIED"
        and old.get("phase1_v2_supplemental_fuzz_unique_record_count")
            == 8244
        and old.get(
            "phase1_v2_supplemental_independently_referenced_case_count")
            == 0
        and old.get("phase1_v2_supplemental_dual_reference_status")
            == "NOT RUN"
        and old.get("phase1_v2_supplemental_candidate_status") == "NOT RUN"
        and len(old.get("phase1_v2_correctness_gate_blockers", [])) == 7
        and old.get("candidate_evaluation_authorized") is False
        and old.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and old.get("rust_buffer_shape_v2_matching_status") == "NOT RUN"
        and old.get("rust_native_build_v17_status") == "NOT RUN"
        and old.get("rust_native_build_v17_authorization_status") == "BLOCKED"
        and old.get("rust_native_build_v17_compiler_process_count") == 0
        and old.get("rust_native_build_v17_native_binary_count") == 0
        and old.get("authenticated_evidence_owner_lower_bound") == 207
        and old.get("authenticated_history_reference_lower_bound") == 212
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("qualified_candidate_count") == 0
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce exact narrow V61 PASS, all blockers and failed Rust",
    )
    return old, inputs, raw["svg"]

def reference_expectations() -> dict:
    return copy.deepcopy(REFERENCE_CONTRACT_EXPECTATIONS)


def make_reference_proof(base: types.ModuleType, owners: dict,
                         contract: dict) -> dict:
    return {
        "schema": SCHEMA + "-authenticated-differential-fuzz-reference-v3",
        "version": 3,
        "source_status": "SOURCE FROZEN",
        "execution_status": "NOT RUN",
        "reference_worker_count": 0,
        "reference_process_ids": [],
        "attempted_reference_worker_count": 0,
        "completed_reference_worker_count": 0,
        "independently_referenced_case_count": 0,
        "supplemental_fuzz_case_count": 8244,
        "supplemental_fuzz_record_stream": "VERIFIED",
        "supplemental_fuzz_dual_reference_status": "NOT RUN",
        "candidate_case_count": 0,
        "candidate_execution_status": "NOT RUN",
        "candidate_evaluation_authorized": False,
        "candidate_qualified": False,
        "reference_workers_started_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "holdout_files_opened_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "native_libraries_loaded_by_graph": 0,
        "clock_samples_by_graph": 0,
        "owners": copy.deepcopy(owners),
        "complete_reference_contract": copy.deepcopy(contract),
    }

def validate_reference_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject missing complete frozen fuzz-reference proof")
    assert isinstance(proof, dict)
    expected_contract = reference_expectations()
    expected_owners = {
        role: base.synthetic_owner(item, REFERENCE_INODES[role])
        for role, item in REFERENCE.items()
    }
    expected = make_reference_proof(base, expected_owners, expected_contract)
    base.need(
        set(proof) == set(expected),
        "reject deleted or invented fuzz-reference source-proof fields",
    )
    for key, value in expected.items():
        base.need(
            type(proof.get(key)) is type(value)
            and proof.get(key) == value,
            "reject forged source-freeze, worker or contract: " + key,
        )
    base.need(
        proof["source_status"] == "SOURCE FROZEN"
        and proof["execution_status"] == "NOT RUN"
        and proof["reference_worker_count"] == 0
        and proof["reference_process_ids"] == []
        and proof["attempted_reference_worker_count"] == 0
        and proof["completed_reference_worker_count"] == 0
        and proof["independently_referenced_case_count"] == 0
        and proof["supplemental_fuzz_case_count"] == 8244
        and proof["supplemental_fuzz_record_stream"] == "VERIFIED"
        and proof["supplemental_fuzz_dual_reference_status"] == "NOT RUN"
        and proof["candidate_case_count"] == 0
        and proof["candidate_execution_status"] == "NOT RUN"
        and proof["candidate_evaluation_authorized"] is False
        and proof["candidate_qualified"] is False
        and proof["reference_workers_started_by_graph"] == 0
        and proof["candidate_workers_started_by_graph"] == 0
        and proof["compressed_archives_opened_by_graph"] == 0
        and proof["holdout_files_opened_by_graph"] == 0
        and proof["compiler_processes_started_by_graph"] == 0
        and proof["native_libraries_loaded_by_graph"] == 0
        and proof["clock_samples_by_graph"] == 0,
        "freeze the 8,244-case two-worker test without executing it",
    )

def authenticate_reference(base: types.ModuleType,
                           options: argparse.Namespace) -> dict:
    owners = {}
    actual_contract = None
    for role, item in REFERENCE.items():
        supplied = getattr(options, "reference_" + role + "_sha256")
        base.need(
            base.checked(supplied, "exact frozen fuzz reference " + role)
            == item[1],
            "reject substituted source-frozen fuzz reference " + role,
        )
        raw, meta = base.read_owner(*item, private=True)
        base.need(
            meta["device"] == 2064
            and meta["inode"] == REFERENCE_INODES[role],
            "reject substituted exact private reference inode: " + role,
        )
        owners[role] = base.synthetic_owner(item, REFERENCE_INODES[role])
        if role == "contract":
            actual_contract = base.document(
                raw, "complete source-frozen dual-reference contract")
    base.need(
        actual_contract == reference_expectations(),
        "reject incomplete or modified full fuzz-reference contract",
    )
    assert isinstance(actual_contract, dict)
    proof = make_reference_proof(base, owners, actual_contract)
    validate_reference_proof(base, proof)
    return proof

def result_fields(proof: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 61,
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
        "phase1_v2_supplemental_independently_referenced_case_count": 0,
        "phase1_v2_supplemental_dual_reference_status": "NOT RUN",
        "phase1_v2_supplemental_candidate_status": "NOT RUN",
        "supplemental_differential_fuzz_candidate_gate": "BLOCKED",
        "supplemental_differential_fuzz_case_count": 8244,
        "phase1_differential_fuzz_reference_v3_source_status":
            "SOURCE FROZEN",
        "phase1_differential_fuzz_reference_v3_execution_status": "NOT RUN",
        "phase1_differential_fuzz_reference_v3_worker_count": 0,
        "phase1_differential_fuzz_reference_v3_worker_process_ids": [],
        "phase1_differential_fuzz_reference_v3_reference_case_count": 0,
        "phase1_differential_fuzz_reference_v3_candidate_case_count": 0,
        "phase1_differential_fuzz_reference_v3_source_freeze":
            copy.deepcopy(proof),
        "genuine_2gib_candidate_search": "NOT RUN",
        "genuine_2gib_candidate_substitution": "NOT RUN",
        "candidate_evaluation_authorized": False,
        "rust_native_build_v17_source_status": "SOURCE FROZEN",
        "rust_native_build_v17_status": "NOT RUN",
        "rust_native_build_v17_authorization_status": "BLOCKED",
        "rust_native_build_v17_blocking_reason":
            "PHASE 1 SUPPLEMENTAL DUAL REFERENCE NOT ESTABLISHED",
        "rust_native_build_v17_matching_status": "NOT RUN",
        "rust_native_build_v17_candidate_correctness": "NOT MEASURED",
        "rust_native_build_v17_candidate_qualified": False,
        "rust_native_build_v17_compiler_process_count": 0,
        "rust_native_build_v17_compiler_process_ids": [],
        "rust_native_build_v17_native_binary_count": 0,
        "rust_native_build_v17_native_artifact_hashes": [],
        "rust_native_build_v17_candidate_workers_started": 0,
        "rust_native_build_v17_independent_source_owner_count": 3,
        "authenticated_evidence_owner_lower_bound": 210,
        "authenticated_history_reference_lower_bound": 215,
        "actual_fuzz_reference_source_owners_read_by_graph": 3,
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
              "reject missing complete source-frozen V62 graph snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("phase1_differential_fuzz_reference_v3_source_freeze")
    validate_reference_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(
            type(snapshot.get(key)) is type(value)
            and snapshot.get(key) == value,
            "reject invented fuzz source, worker, P0 or timing: " + key,
        )
    replaced = snapshot.get("preserved_v61_replaced_snapshot_fields")
    base.need(type(replaced) is dict and set(replaced).issubset(updates),
              "preserve all exact replaced actual pushed V61 fields")
    assert isinstance(replaced, dict)
    base.need(
        replaced.get("actual_current_graph_predecessor_version") == 57,
        "preserve predecessor 57 only as exact immutable V61 history",
    )
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v61_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(prior_modules, history)
    base.need(
        snapshot.get("actual_rust_semantic_mismatch_count") == 1440
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
        "preserve all V61 blockers, actual Rust witnesses and sealed holdout",
    )

def replace_once(base: types.ModuleType, visible: str,
                 before: str, after: str, description: str) -> str:
    base.need(type(visible) is str and type(before) is str
              and type(after) is str and visible.count(before) == 1,
              "reject substituted pushed V61 chart section: " + description)
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
        forged["__forged_v62__"] = True
        return forged
    if value is None:
        return "FORGED"
    return object()



def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact source-only V62 renderer")
    inputs_sha = base.checked(inputs_sha, "exact source-only V62 inputs")
    visible = old_svg.decode("utf-8").replace(
        "v61-title", "v62-title").replace(
        "v61-description", "v62-description")
    lines = visible.splitlines()
    base.need(
        len(lines) > 10
        and lines[1].startswith('<title id="v62-title">')
        and lines[2].startswith('<desc id="v62-description">'),
        "preserve the exact actual accessible V61 chart",
    )
    lines[1] = (
        '<title id="v62-title">Building a faster Python re: Python '
        'reference fixed; additional 8,244-case reference test '
        'frozen, not yet run</title>'
    )
    lines[2] = (
        '<desc id="v62-description">Pinned stable Python 3.14.6 '
        'remains the baseline. Two real Python workers confirmed '
        'the corrected 6,912-case public-type reference. Complete '
        'first-party source and a reproducible protocol for testing '
        'all 8,244 checksum-verified supplemental fuzz cases using '
        'two separate Python reference processes are SOURCE FROZEN. '
        'This future reference test has NOT RUN: zero workers, '
        'zero process IDs and zero independently referenced fuzz '
        'cases. The full correctness oracle remains BLOCKED; all '
        'seven existing blockers remain unchanged. No replacement '
        'is authorized or qualified. The old public-type reference '
        'remains FALSIFIED. The latest actual from-scratch Rust '
        'test has 1,440 compatibility differences, 14,853 '
        'explicitly verified passes, 13 real workers, 13 complete '
        'suites and six exact genuine first mismatches. Historical '
        'V7 had 928 differences and 8,965 verified passes; the '
        'regression is 512 differences. Exactly three independent '
        'reference-source owners raise current evidence and history '
        'floors from 207 / 212 to 210 / 215. Six first-party '
        'candidate families and zero compatible replacements '
        'remain. Original 31,237 cases, 50 signature checks, '
        '32 public-interface observations, 32 large-input '
        'observations and 8,244 fuzz cases remain separately '
        'counted. The exporter repair is NOT BUILT and NOT RUN. '
        'Its SOURCE FROZEN native build remains BLOCKED and '
        'NOT RUN, with 0 compilers and 0 binaries. The '
        '4,194,304-case final holdout is NOT OPENED and not '
        'generated. Performance, memory, confidence intervals '
        'and undefined behavior are NOT MEASURED; runtime '
        'independence is NOT ESTABLISHED.</desc>'
    )
    visible = "\n".join(lines)
    replacements = (
        (
            '<text x="65" y="398" class="heading">Python reference '
            'corrected; full test suite still blocked</text>',
            '<text x="65" y="398" class="heading">Python reference '
            'fixed; next 8,244-case test not yet run</text>',
            "show an unrun test, not a complete passing oracle",
        ),
        (
            'Two Python runs confirm 6,912 reference cases. Another '
            '8,244 fuzz cases still need two independent Python runs.',
            'Two Python runs confirm 6,912 reference cases. The '
            '8,244-case follow-up is SOURCE FROZEN and NOT RUN.',
            "keep the real reference and source-only freeze separate",
        ),
        (
            '<text x="64" y="1756" class="heading">Corrected Python '
            'reference passed; full suite and build remain blocked</text>',
            '<text x="64" y="1756" class="heading">Next Python '
            'reference test frozen; zero workers have run</text>',
            "forbid reporting a reference run or passing suite",
        ),
        (
            'Exactly three phase-one source owners raise current '
            'lower bounds from 204 / 209 to 207 / 212.',
            'Exactly three reference-source owners raise current '
            'lower bounds from 207 / 212 to 210 / 215.',
            "count exactly three independent frozen-source owners",
        ),
        (
            'Real Rust failures remain proven. Full correctness and '
            'the source-only build are BLOCKED; zero compilers, '
            'binaries, candidate runs or speed results exist.',
            'Real Rust failures remain proven. Full correctness '
            'stays BLOCKED; the next reference test has zero '
            'workers, candidate runs or speed results.',
            "forbid invented worker, matching and timing execution",
        ),
    )
    for before, after, why in replacements:
        visible = replace_once(base, visible, before, after, why)
    lines = visible.splitlines()
    start = next(
        (index for index, line in enumerate(lines)
         if line.startswith('<rect x="44" y="1858" width="1352"')),
        None,
    )
    base.need(type(start) is int, "retain the exact V61 evidence chart")
    assert isinstance(start, int)
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="381" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact prior results '
        'and unrun first-party Python reference source</text>',
    ))
    v58 = prior_modules[1][1][0]
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V61 graph inputs SHA-256", V61["inputs"][1]),
        ("Historical V61 graph renderer SHA-256", V61["source"][1]),
        ("Historical V61 graph summary SHA-256", V61["summary"][1]),
        ("Historical V61 graph image SHA-256", V61["svg"][1]),
        ("Small actual failed Rust receipt SHA-256", v58.RECEIPT[1]),
        ("Complete independent Rust failure summary SHA-256",
         v58.FORENSIC[1]),
        ("Frozen fuzz-reference runner source SHA-256",
         REFERENCE["source"][1]),
        ("Frozen fuzz-reference protocol SHA-256",
         REFERENCE["protocol"][1]),
        ("Frozen unrun fuzz-reference contract SHA-256",
         REFERENCE["contract"][1]),
        ("Historical compressed failure SHA-256 (not opened)",
         v58.ARCHIVE_SHA),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + index * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2139" class="small">Corrected Python '
        'reference: PASS; 6,912 cases; two genuine workers.</text>',
        '<text x="65" y="2158" class="small">Additional 8,244-case '
        'reference: SOURCE FROZEN; NOT RUN; 0 workers.</text>',
        '<text x="65" y="2177" class="small">Actual Rust: '
        '1,440 differences; 14,853 verified passes; '
        '13 real workers.</text>',
        '<text x="65" y="2196" class="small">Correctness: BLOCKED. '
        'Build: NOT RUN. Speed: NOT MEASURED.</text>',
        '<text x="65" y="2215" class="small">Six first-party families; '
        '0 compatible replacements; final holdout NOT OPENED.</text>',
        '<!-- This graph never opens, stats, hashes or inflates a '
        'compressed archive, starts a reference worker, imports or '
        'runs a candidate, loads a native library, starts a compiler, '
        'reads a clock, measures performance or opens the holdout. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in footers:
        base.need(
            raw.count((label + ": " + value).encode("ascii")) == 1,
            "bind exactly one source-only V62 footer: " + label,
        )
    lower = raw.lower()
    for phrase in (
            b'height="2250"', b"building a faster python re",
            b"python reference", b"reference fixed", b"additional",
            b"8,244", b"source frozen", b"not yet run", b"not run",
            b"0 workers", b"6,912", b"two genuine workers",
            b"blocked", b"1,440", b"14,853", b"13 real workers",
            b"512", b"928", b"8,965",
            b"managed 16", b"substitution 368", b"shape 1,056",
            b"31,237", b"4.2m unopened", b"not opened",
            b"not built", b"0 compilers", b"0 binaries",
            b"not measured", b"not established",
            b"207 / 212", b"210 / 215",
            b"signature checks", b"public-interface observations",
            b"large-input observations", b"17 pass", b"7 fail",
            b"22 pass", b"3 not run", b"2,147,483,648",
            b"1,087", b"1,036", b"1,262", b"1,230",
            b"2,172", b"1,764", b"not generated"):
        base.need(phrase in lower,
                  "preserve actual reference and failures: " + repr(phrase))
    for falsehood in (
            b"full test suite passed", b"phase-one gate passed",
            b"all fuzz cases independently passed",
            b"8,244 reference cases passed",
            b"dual-reference execution passed",
            b"reference workers started",
            b"candidate qualified", b"three qualified candidates",
            b"holdout opened", b"holdout generated",
            b"benchmark speedup", b"winner selected",
            b"verify_p0_completeness_v2.py"):
        base.need(falsehood not in lower,
                  "reject invented V62 result: " + repr(falsehood))
    return raw

def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact current source-only V62 renderer")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound actual complete private V62 source")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                private=True)
    old, old_inputs, old_svg = authenticate_v61(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V61},
    )
    proof = authenticate_reference(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v61_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V61.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 62,
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
        "preserve one baseline and six independent first-party families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 210,
            "authenticated_history_reference_lower_bound": 215,
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
            "differential_fuzz_reference_execution_status": "NOT RUN",
            "differential_fuzz_reference_worker_count": 0,
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
                "differential_fuzz_reference_source_freeze":
                    copy.deepcopy(proof),
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 62,
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
    base.need(
        inputs.get("actual_current_graph_predecessor_version") == 61
        and summary.get("actual_current_graph_predecessor_version") == 61
        and summary["snapshot"].get("actual_current_graph_predecessor_version")
            == 61
        and summary["snapshot"]["preserved_v61_replaced_snapshot_fields"][
            "actual_current_graph_predecessor_version"] == 57
        and summary["previous_overview"]["source"]["path"]
            == V61["source"][0],
        "bind actual V61 predecessor to graph inputs and complete summary",
    )
    summary_raw = base.canonical(summary)
    base.need(
        max(len(input_raw), len(summary_raw), len(svg)) <= base.OWNER_LIMIT,
        "bound only three root-authorized source-only V62 graph owners",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )

def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_reference_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged source-only fuzz reference: "
                          + description)

def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 4967
        and prior.get("actual_rust_semantic_mismatch_count") == 1440
        and prior.get("actual_rust_verified_passing_case_count") == 14853
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get("actual_rust_v10_candidate_status") == "FAIL"
        and prior.get("actual_rust_v10_candidate_workers") == 13
        and prior.get("phase1_corrected_crosswalk_status") == "PASS"
        and prior.get("phase1_completeness_status") == "BLOCKED"
        and prior.get("phase1_v2_corrected_reference_case_count") == 6912
        and prior.get("phase1_v2_corrected_reference_process_ids")
            == [81, 82]
        and prior.get("phase1_v2_supplemental_fuzz_unique_record_count")
            == 8244
        and prior.get(
            "phase1_v2_supplemental_independently_referenced_case_count")
            == 0
        and prior.get("phase1_v2_supplemental_dual_reference_status")
            == "NOT RUN"
        and prior.get("candidate_evaluation_authorized") is False
        and prior.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and prior.get("rust_native_build_v17_status") == "NOT RUN"
        and prior.get("rust_native_build_v17_compiler_process_count") == 0
        and prior.get("authenticated_evidence_owner_lower_bound") == 207
        and prior.get("authenticated_history_reference_lower_bound") == 212
        and prior.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and prior.get("actual_failure_archives_opened_by_self_test") == 0
        and prior.get("actual_phase1_oracle_source_owners_read_by_self_test")
            == 0,
        "preserve all 4,967 V61 controls and actual blocked full P0",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item, REFERENCE_INODES[role])
            for role, item in REFERENCE.items()
        }
        proof = make_reference_proof(base, owners, reference_expectations())
        validate_reference_proof(base, proof)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = forged_value(value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for role, owner in proof["owners"].items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = forged_value(value)
                rejected += reject_control(
                    base, hostile, "owner:" + role + ":" + key)
        for key, value in proof["complete_reference_contract"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_reference_contract"][key] = (
                forged_value(value))
            rejected += reject_control(base, hostile, "contract:" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v62")),
            ("filesystem", lambda: os.open("forbidden-v62", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v62")),
            ("write", lambda: os.mkdir("forbidden-v62")),
            ("process", lambda: subprocess.run(("forbidden-v62",))),
            ("process", lambda: subprocess.Popen(("forbidden-v62",))),
            ("process", lambda: os.execv("/forbidden-v62", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically forbid source-only V62 " + kind,
                )
            else:
                raise base.GraphError("allowed V62 source effect: " + kind)
        base.need(rejected >= 45,
                  "reject forged source contract, reference and owner claims")
        updates = result_fields(proof)
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 62,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v61_hostile_controls": 4967,
            "new_v62_hostile_controls": rejected,
            "rejected_hostile_control_count": 4967 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
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
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_current_graph_predecessor_version": 61,
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
              "publish only three root-authorized complete V62 graph files")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact independently owned V62 byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid()
                  and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish exactly one private complete V62 graph owner")
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
              "reauthenticate exactly one complete current V62 graph owner")



def repair_predecessor_outputs(base: types.ModuleType,
                               pairs: tuple) -> None:
    expected_paths = {
        item[0] for item in STALE_PREDECESSOR_OUTPUTS.values()
    }
    actual_pairs = dict(pairs)
    base.need(
        len(actual_pairs) == 3
        and set(actual_pairs) == expected_paths,
        "repair only the three exact self-created stale V62 assets",
    )
    stale = {}
    for role, (path, fingerprint, size, inode) in (
            STALE_PREDECESSOR_OUTPUTS.items()):
        raw, owner = base.read_owner(path, fingerprint, size, private=True)
        base.need(
            owner["device"] == 2064
            and owner["inode"] == inode
            and owner["nlink"] == 1,
            "reject changed exact stale V62 owner: " + role,
        )
        if role in {"inputs", "summary"}:
            document = base.document(raw, "exact stale V62 " + role)
            base.need(
                document.get("actual_current_graph_predecessor_version")
                    == 57,
                "repair only the authenticated stale predecessor: " + role,
            )
            if role == "summary":
                base.need(
                    document.get("snapshot", {}).get(
                        "actual_current_graph_predecessor_version") == 57
                    and document.get("previous_overview", {}).get(
                        "source", {}).get("path") == V61["source"][0],
                    "repair only the exact stale graph with V61 predecessor",
                )
        stale[path] = (fingerprint, size, inode)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(str(ROOT / "docs/evidence"), flags)
    try:
        prepared = []
        create_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create_flags |= (
            getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        for path, raw in pairs:
            old_hash, _, _ = stale[path]
            basename = Path(path).name
            temporary = (
                basename + ".predecessor61-" + old_hash[:16] + ".tmp"
            )
            handle = os.open(
                temporary, create_flags, 0o600, dir_fd=directory,
            )
            try:
                remaining = memoryview(raw)
                while remaining:
                    count = os.write(handle, remaining)
                    base.need(
                        type(count) is int and count > 0,
                        "write each complete predecessor-recovery byte",
                    )
                    remaining = remaining[count:]
                os.fsync(handle)
                meta = os.fstat(handle)
                base.need(
                    meta.st_dev == 2064
                    and meta.st_uid == os.geteuid()
                    and meta.st_nlink == 1
                    and meta.st_size == len(raw)
                    and stat.S_IMODE(meta.st_mode) == 0o600,
                    "require an exclusively created private recovery owner",
                )
            finally:
                os.close(handle)
            prepared.append((path, raw, basename, temporary))
        os.fsync(directory)
        for path, raw, basename, temporary in prepared:
            old_hash, old_size, old_inode = stale[path]
            _, owner = base.read_owner(
                path, old_hash, old_size, private=True,
            )
            base.need(
                owner["device"] == 2064
                and owner["inode"] == old_inode
                and owner["nlink"] == 1,
                "refuse replacement of a changed old graph: " + path,
            )
            os.replace(
                temporary, basename,
                src_dir_fd=directory, dst_dir_fd=directory,
            )
            os.fsync(directory)
            confirmed, _ = base.read_owner(
                path, base.digest(raw), len(raw), private=True,
            )
            base.need(
                confirmed == raw,
                "bind exact atomic predecessor-recovery asset: " + path,
            )
    finally:
        os.close(directory)


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
        "version": 62,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 61,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V61.items()},
        **{"reference_" + role + "_sha256": item[1]
           for role, item in REFERENCE.items()},
        **{key: copy.deepcopy(snapshot[key]) for key in fields},
        "outputs_written": written,
    }

def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--repair-predecessor", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V61:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in REFERENCE:
        parser.add_argument("--reference-" + role + "-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v61()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256" for role in V61)
            forbidden.extend(
                "reference_" + role + "_sha256" for role in REFERENCE)
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(
                all(getattr(options, name) is None for name in forbidden),
                "source-only V62 self-test receives no actual pins",
            )
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256,
                                  "complete exact V62 graph renderer")
        if options.render or options.repair_predecessor:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "render only three root-authorized complete V62 outputs",
            )
            if options.repair_predecessor:
                repair_predecessor_outputs(base, pairs)
            else:
                for path, raw in pairs:
                    publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published")
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "exact actual V62 graph inputs"),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "exact actual V62 graph summary"),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "exact actual V62 graph image"),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True)
                base.need(raw == outputs[path],
                          "reproduce complete source-only V62 output: "
                          + path)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context")
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V62 overview rejected: "
                         + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V62 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
