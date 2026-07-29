#!/usr/bin/env python3
"""Show one frozen, untested first-party C repair without claiming a speedup."""

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
SELF = "tools/render_candidate_current_overview_v65.py"
OUTPUT = "docs/evidence/candidate-current-overview-v65"
SCHEMA = "rebar-candidate-current-overview-v65"
V64 = {
    "source": ("tools/render_candidate_current_overview_v64.py",
               "6e8364972fe69c4e6074df14ce69369d962773de64bedf576515744cf44e488f",
               120686, 428928),
    "inputs": ("docs/evidence/candidate-current-overview-v64.inputs.json",
               "6566c57fe58b501b54b056aae528d1e1087bec279718e5d175d99baca703cd76",
               1004674, 428932),
    "summary": ("docs/evidence/candidate-current-overview-v64.json",
                "feaf43cb6eeeb0d61f60ede20925d559cdafb66d8110f9607192dac542f51ae0",
                2775659, 428934),
    "svg": ("docs/evidence/candidate-current-overview-v64.svg",
            "1106fa228c5cf9ed3df94be344c58acf8513ac3be4b01b9c1a0bf058f76bb95f",
            14807, 428935),
}
FEATURE = {
    "variant": ("candidates/c/variants/subject_buffer_ownership_v1/vm_native.c",
                "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962",
                222212, 524723),
    "source": ("tools/apply_owned_c_subject_buffer_ownership_v1.py",
               "8262295a9e84c5fa30fe4e83102236fbaa233c914fb0c570d5fce3cdaf8605d2",
               80090, 428938),
    "protocol": ("oracle/phase2/C-SUBJECT-BUFFER-OWNERSHIP-V1.md",
                 "997af2edeced019663886aa7e20873506e4b13ee361bf5ce8d533e3ad2ea7393",
                 5527, 524724),
    "contract": ("oracle/phase2/c-subject-buffer-ownership-v1.json",
                 "b2ef8b9f5f9c7262be0e639d17436d0e1e8637d5649741bf2aa1538ebef3eb6a",
                 12435, 524726),
}
CONTRACT_KEYS = frozenset((
    "complete_first_party_c_variant", "corrected_c_only_v10_runner",
    "corrected_original_v4_producer", "corrected_p0_v4_readiness",
    "current_rust_v10_history", "delegation_policy", "family", "goal",
    "historical_c_observation", "independent_rust_history",
    "large_input_history", "original_first_party_c_owners", "phase",
    "phase_one", "pinned_cpython", "protocol", "published_v64",
    "pure_first_party_derivation", "schema", "source",
    "source_only_effects", "version",
))
EFFECTS = {
    "actual_candidate_workers": 0,
    "actual_reference_workers": 0,
    "benchmark_files_read": 0,
    "build_archive_bytes_read": 0,
    "build_archives_inflated": 0,
    "build_archives_opened": 0,
    "candidate_correctness": "NOT MEASURED",
    "candidate_imports": 0,
    "candidate_processes_started": 0,
    "clock_samples": 0,
    "compiler_processes_started": 0,
    "hidden_cases_read": 0,
    "holdout": "NOT OPENED",
    "large_subject_allocations": 0,
    "matching_archive_bytes_read": 0,
    "matching_archives_inflated": 0,
    "matching_archives_opened": 0,
    "memory": "NOT MEASURED",
    "native_activations_started": 0,
    "native_builds_started": 0,
    "native_libraries_loaded": 0,
    "network_requests": 0,
    "original_native_targets_read": 0,
    "original_source_targets_modified": 0,
    "performance": "NOT MEASURED",
    "qualified_candidate_count": 0,
    "recovery_roots_opened": 0,
    "reference_archive_bytes_read": 0,
    "reference_archives_inflated": 0,
    "reference_archives_opened": 0,
    "reference_processes_started": 0,
    "runtime_non_delegation": "NOT ESTABLISHED",
    "threads_started": 0,
    "timing_trials_run": 0,
    "undefined_behavior": "NOT MEASURED",
    "winner_selected": False,
    "workspace_mutations": 0,
}
VARIANT_FIELDS = {
    "actual_activation": "NOT RUN",
    "actual_build": "NOT RUN",
    "actual_candidate_matching": "NOT RUN",
    "all_native_changes_reversibly_anchored": True,
    "append_only_new_variant": True,
    "callable_replacement_path_preserved": True,
    "candidate_correctness": "NOT MEASURED",
    "candidate_qualified": False,
    "checked_exact_buffer_allocation": True,
    "independent_parser_compiler_executor_and_engine": True,
    "indirect_and_strided_buffer_safe_by_construction": True,
    "language": "C",
    "layout": "owned Python parser and first-party C bytecode engine and CPython bridge",
    "normal_replacement_buffer_flags": "PyBUF_SIMPLE",
    "original_exporter_error_context_preserved": True,
    "original_replacement_hash_observed": True,
    "preserves_zero_length_buffer": True,
    "previous_match_pickle_repair_preserved": True,
    "replacement_full_readonly_buffer_flags": "PyBUF_FULL_RO",
    "replacement_subject_released_before_materialization": True,
    "safe_contiguous_copy_order": "C",
    "shape_and_pep688_result": "NOT MEASURED",
    "subject_buffer_released_exactly_once": True,
}


def _read_exact(item: tuple, label: str) -> bytes:
    relative, fingerprint, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(handle)
        if (not stat.S_ISREG(before.st_mode)
                or before.st_uid != os.geteuid()
                or before.st_dev != 2064
                or before.st_ino != inode
                or before.st_nlink != 1
                or stat.S_IMODE(before.st_mode) != 0o600
                or before.st_size != size):
            raise ValueError("reject substituted private " + label)
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated " + label)
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended " + label)
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed private " + label)
        return raw
    finally:
        os.close(handle)


def load_v64() -> tuple:
    raw = _read_exact(V64["source"], "pushed V64 graph source")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v64")
    previous.__file__ = str(ROOT / V64["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    modules = previous.load_v63()
    base = modules[-1]
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v64"
              and previous.SELF == V64["source"][0],
              "authenticate only the exact corrected pushed V64 graph")
    return previous, modules, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    values = {
        "source_sha256": V64["source"][1],
        "source_bytes": V64["source"][2],
        "inputs_sha256": None,
        "summary_sha256": None,
        "svg_sha256": None,
    }
    for role, item in previous.V63.items():
        values["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.READINESS.items():
        values["readiness_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**values)


def synthetic_contract(base: types.ModuleType, previous: types.ModuleType) -> dict:
    contract = {key: {} for key in CONTRACT_KEYS}
    variant_owner = base.pin(*FEATURE["variant"][:3])
    contract.update({
        "schema": "rebar-phase2-owned-c-subject-buffer-ownership-v1",
        "version": 1,
        "family": "c",
        "phase": "SOURCE FREEZE; FIRST-PARTY C SUBJECT BUFFER VARIANT NOT BUILT OR RUN",
        "source": {"path": FEATURE["source"][0],
                   "sha256": FEATURE["source"][1]},
        "protocol": {"path": FEATURE["protocol"][0],
                     "sha256": FEATURE["protocol"][1]},
        "complete_first_party_c_variant": {
            **copy.deepcopy(VARIANT_FIELDS), "owner": variant_owner,
        },
        "historical_c_observation": {
            "historical_c_semantic_mismatch_count": 1230,
            "explicitly_verified_historical_c_passing_cases": 7325,
            "historical_c_case_execution_denominator": 31237,
            "historical_c_worker_count": 13,
        },
        "current_rust_v10_history": {
            "actual_candidate_workers": 13,
            "candidate_status": "FAIL",
            "case_execution_denominator": 31237,
            "completed_suite_count": 13,
            "semantic_mismatch_count": 1440,
            "verified_passing_case_count": 14853,
            "rust_parser_compiler_executor_or_engine_reused": False,
        },
        "corrected_c_only_v10_runner": {
            "suite_count": 13,
            "case_execution_denominator": 31237,
            "private_waiver_count": 13,
            "source_dispatch_families": ["c"],
            "matching_started": False,
        },
        "corrected_p0_v4_readiness": {
            "candidate_qualification_status": "BLOCKED",
            "owners": {role: base.pin(*item)
                       for role, item in previous.READINESS.items()},
        },
        "phase_one": {
            "case_execution_denominator": 31237,
            "cases_removed": 0,
            "named_private_waiver_count": 13,
            "suite_count": 13,
            "waivers_added": 0,
        },
        "published_v64": {
            "version": 64,
            "authenticated_evidence_owner_lower_bound": 216,
            "authenticated_history_reference_lower_bound": 221,
            "qualified_candidate_count": 0,
            "owners": {role: base.pin(*item[:3])
                       for role, item in V64.items()},
        },
        "delegation_policy": {
            "benchmark_or_holdout": "FORBIDDEN",
            "candidate_fallback": "FORBIDDEN",
            "candidate_or_reference_execution": "FORBIDDEN",
            "case_ids_in_native_variant": "FORBIDDEN",
            "clock_or_network": "FORBIDDEN",
            "cpython_regular_expression_engine": "FORBIDDEN",
            "external_regular_expression_packages": "FORBIDDEN",
            "hardcoded_oracle_answers": "FORBIDDEN",
            "historical_archive_open_or_inflation": "FORBIDDEN",
            "native_build_or_loading": "FORBIDDEN",
            "other_candidate_parser_compiler_executor_or_engine": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "stdlib__sre": "FORBIDDEN",
            "stdlib_re": "FORBIDDEN",
        },
        "source_only_effects": copy.deepcopy(EFFECTS),
    })
    return contract


def validate_contract(base: types.ModuleType, previous: types.ModuleType,
                      contract: object) -> None:
    base.need(type(contract) is dict and set(contract) == CONTRACT_KEYS,
              "reject omitted or invented complete first-party C contract")
    assert isinstance(contract, dict)
    expected = synthetic_contract(base, previous)
    for key in ("schema", "version", "family", "phase", "source",
                "protocol", "delegation_policy", "source_only_effects"):
        base.need(type(contract.get(key)) is type(expected[key])
                  and contract.get(key) == expected[key],
                  "reject forged exact C feature contract: " + key)
    variant = contract.get("complete_first_party_c_variant")
    base.need(type(variant) is dict
              and set(variant) == set(expected["complete_first_party_c_variant"]),
              "reject missing first-party C buffer ownership fields")
    assert isinstance(variant, dict)
    for key, value in expected["complete_first_party_c_variant"].items():
        base.need(type(variant.get(key)) is type(value)
                  and variant.get(key) == value,
                  "reject forged C buffer feature or build claim: " + key)
    for group in ("historical_c_observation", "current_rust_v10_history",
                  "corrected_c_only_v10_runner", "corrected_p0_v4_readiness",
                  "phase_one", "published_v64"):
        actual = contract.get(group)
        base.need(type(actual) is dict,
                  "reject incomplete C source-freeze history: " + group)
        assert isinstance(actual, dict)
        for key, value in expected[group].items():
            base.need(type(actual.get(key)) is type(value)
                      and actual.get(key) == value,
                      "reject forged exact C feature history: "
                      + group + ":" + key)


def feature_proof(base: types.ModuleType, previous: types.ModuleType,
                  owners: dict, contract: dict) -> dict:
    validate_contract(base, previous, contract)
    return {
        "schema": SCHEMA + "-first-party-c-subject-buffer-ownership-v1",
        "version": 1,
        "status": "SOURCE FROZEN",
        "family": "c",
        "independent_feature_source_owner_count": 4,
        "owners": copy.deepcopy(owners),
        "complete_feature_contract": copy.deepcopy(contract),
        "previous_c_matching_status": "FAIL",
        "previous_c_semantic_mismatch_count": 1230,
        "previous_c_explicitly_verified_passing_case_count": 7325,
        "current_rust_matching_status": "FAIL",
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_explicitly_verified_passing_case_count": 14853,
        "candidate_matching_status": "NOT RUN",
        "candidate_build_status": "NOT BUILT",
        "candidate_activation_status": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "actual_compiler_process_count": 0,
        "actual_native_binary_count": 0,
        "actual_candidate_workers_started": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "source_only_effects": copy.deepcopy(EFFECTS),
    }


def validate_proof(base: types.ModuleType, previous: types.ModuleType,
                   proof: object) -> None:
    base.need(type(proof) is dict,
              "reject omitted complete first-party C source freeze")
    assert isinstance(proof, dict)
    contract = proof.get("complete_feature_contract")
    validate_contract(base, previous, contract)
    assert isinstance(contract, dict)
    owners = {role: base.synthetic_owner(item[:3], item[3])
              for role, item in FEATURE.items()}
    expected = feature_proof(base, previous, owners, contract)
    base.need(set(proof) == set(expected),
              "reject missing exact C source-freeze graph proof fields")
    for key, value in expected.items():
        base.need(type(proof.get(key)) is type(value)
                  and proof.get(key) == value,
                  "reject invented C build, qualification, or result: " + key)


def forged(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " [FORGED]"
    if type(value) is list:
        return copy.deepcopy(value) + ["FORGED"]
    if type(value) is dict:
        changed = copy.deepcopy(value)
        changed["__forged_v65__"] = True
        return changed
    return "FORGED"


def reject_control(base: types.ModuleType, previous: types.ModuleType,
                   proof: dict, label: str) -> int:
    try:
        validate_proof(base, previous, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted hostile first-party C control: " + label)


def updates(proof: dict, historical_c: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 64,
        "authenticated_evidence_owner_lower_bound": 220,
        "authenticated_history_reference_lower_bound": 225,
        "actual_c_v4_original_campaign": copy.deepcopy(historical_c),
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "actual_c_v4_original_campaign_semantic_mismatch_count": 1230,
        "actual_c_v4_original_campaign_verified_passing_case_count": 7325,
        "actual_c_v4_original_campaign_status": "FAIL",
        "c_subject_buffer_ownership_v1_source_freeze": copy.deepcopy(proof),
        "c_subject_buffer_ownership_v1_feature_status": "SOURCE FROZEN",
        "c_subject_buffer_ownership_v1_build_status": "NOT BUILT",
        "c_subject_buffer_ownership_v1_matching_status": "NOT RUN",
        "c_subject_buffer_ownership_v1_activation_status": "NOT RUN",
        "c_subject_buffer_ownership_v1_candidate_correctness": "NOT MEASURED",
        "c_subject_buffer_ownership_v1_candidate_qualified": False,
        "c_subject_buffer_ownership_v1_compiler_process_count": 0,
        "c_subject_buffer_ownership_v1_native_binary_count": 0,
        "c_subject_buffer_ownership_v1_candidate_workers_started": 0,
        "c_subject_buffer_ownership_v1_independent_source_owner_count": 4,
        "actual_feature_source_owners_read_by_graph": 4,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(previous: types.ModuleType, modules: tuple,
                      base: types.ModuleType, snapshot: object) -> None:
    base.need(type(snapshot) is dict,
              "reject omitted complete first-party C feature snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("c_subject_buffer_ownership_v1_source_freeze")
    validate_proof(base, previous, proof)
    historical = snapshot.get("actual_c_v4_original_campaign")
    base.need(type(historical) is dict
              and historical.get("status") == "FAIL"
              and historical.get("semantic_mismatch_count") == 1230
              and historical.get("verified_passing_case_count") == 7325,
              "preserve actual independently observed failed C campaign")
    assert isinstance(proof, dict) and isinstance(historical, dict)
    changes = updates(proof, historical)
    for key, value in changes.items():
        base.need(type(snapshot.get(key)) is type(value)
                  and snapshot.get(key) == value,
                  "reject invented first-party C feature result: " + key)
    replaced = snapshot.get("preserved_v64_replaced_snapshot_fields")
    base.need(type(replaced) is dict
              and set(replaced).issubset(changes)
              and replaced.get("actual_current_graph_predecessor_version") == 63
              and replaced.get("authenticated_evidence_owner_lower_bound") == 216
              and replaced.get("authenticated_history_reference_lower_bound") == 221,
              "preserve immutable true V64 predecessor and owner lower bounds")
    assert isinstance(replaced, dict)
    original = copy.deepcopy(snapshot)
    original.pop("preserved_v64_replaced_snapshot_fields", None)
    for key in changes:
        if key in replaced:
            original[key] = copy.deepcopy(replaced[key])
        else:
            original.pop(key, None)
    previous.validate_snapshot(modules, original)
    base.need(snapshot.get("phase1_v4_oracle_readiness_status") == "PASS"
              and snapshot.get("candidate_evaluation_authorized") is True
              and snapshot.get("candidate_qualification_status") == "BLOCKED"
              and len(snapshot.get("candidate_qualification_blockers", ())) == 7
              and snapshot.get("qualified_candidate_count") == 0
              and snapshot.get("rust_native_build_v17_authorization_status")
                  == "BLOCKED"
              and snapshot.get("rust_native_build_v17_blocking_reason")
                  == "FROZEN V17 REQUIRES HISTORICAL BLOCKED P0 V2"
              and snapshot.get("rust_native_build_v17_status") == "NOT RUN"
              and snapshot.get("actual_rust_semantic_mismatch_count") == 1440
              and snapshot.get("actual_rust_verified_passing_case_count") == 14853
              and snapshot.get("actual_rust_v10_candidate_status") == "FAIL"
              and snapshot.get("actual_rust_v10_candidate_workers") == 13
              and len(snapshot.get(
                  "actual_rust_v10_complete_independently_authenticated_suite_results", ())) == 13
              and len(snapshot.get(
                  "actual_rust_v10_earliest_genuine_mismatch_witnesses", ())) == 6
              and snapshot.get("full_case_denominator") == 31237
              and snapshot.get("suite_count") == 13
              and snapshot.get("private_waiver_count") == 13
              and snapshot.get("first_party_source_inventory_family_count") == 6
              and snapshot.get("final_comparison_planned_case_count") == 4194304
              and snapshot.get("final_comparison_cases_generated") is False
              and snapshot.get("final_holdout_opened") is False,
              "separate one unbuilt C source feature from actual candidate results")


def authenticate_previous(previous: types.ModuleType, modules: tuple,
                          base: types.ModuleType,
                          options: argparse.Namespace) -> tuple:
    for role, item in V64.items():
        supplied = getattr(options, "previous_" + role + "_sha256")
        base.need(base.checked(supplied, "actual pushed V64 " + role) == item[1],
                  "reject substituted true V64 predecessor: " + role)
    for role, item in previous.READINESS.items():
        supplied = getattr(options, "readiness_" + role + "_sha256")
        base.need(base.checked(supplied, "actual PASS V4 readiness " + role)
                  == item[1], "reject substituted corrected phase-one readiness")
    raw = {role: _read_exact(item, "pushed V64 " + role)
           for role, item in V64.items()}
    old = base.document(raw["summary"], "complete corrected V64 summary")
    old_inputs = base.document(raw["inputs"], "complete corrected V64 inputs")
    reconstructed, pairs = previous.build(modules, previous_options(previous))
    rendered = dict(pairs)
    previous.validate_snapshot(modules, old.get("snapshot"))
    c = old.get("actual_c_v4_original_campaign")
    base.need(type(c) is dict and c.get("status") == "FAIL"
              and c.get("semantic_mismatch_count") == 1230
              and c.get("verified_passing_case_count") == 7325
              and old.get("version") == 64
              and old.get("status") == "PASS"
              and old.get("actual_current_graph_predecessor_version") == 63
              and old.get("snapshot") == reconstructed
              and old.get("phase1_v4_oracle_readiness_status") == "PASS"
              and old.get("candidate_evaluation_authorized") is True
              and old.get("candidate_qualification_status") == "BLOCKED"
              and len(old.get("candidate_qualification_blockers", ())) == 7
              and old.get("qualified_candidate_count") == 0
              and old.get("authenticated_evidence_owner_lower_bound") == 216
              and old.get("authenticated_history_reference_lower_bound") == 221
              and old.get("rust_native_build_v17_authorization_status") == "BLOCKED"
              and old.get("rust_native_build_v17_status") == "NOT RUN"
              and old.get("actual_rust_semantic_mismatch_count") == 1440
              and old.get("actual_rust_verified_passing_case_count") == 14853
              and len(old.get(
                  "actual_rust_v10_complete_independently_authenticated_suite_results", ())) == 13
              and len(old.get("actual_rust_v10_earliest_genuine_mismatch_witnesses", ())) == 6
              and old.get("final_holdout_opened") is False
              and old.get("final_comparison_cases_generated") is False
              and raw["inputs"] == rendered[V64["inputs"][0]]
              and raw["summary"] == rendered[V64["summary"][0]]
              and raw["svg"] == rendered[V64["svg"][0]],
              "reproduce real V64, actual C and Rust failures, and sealed holdout")
    return old, old_inputs, raw["svg"]


def authenticate_feature(previous: types.ModuleType, base: types.ModuleType,
                         options: argparse.Namespace) -> dict:
    owners = {}
    contract = None
    for role, item in FEATURE.items():
        supplied = getattr(options, "feature_" + role + "_sha256")
        base.need(base.checked(supplied, "exact first-party C " + role) == item[1],
                  "reject substituted private first-party C feature: " + role)
        raw = _read_exact(item, "first-party C feature " + role)
        owners[role] = base.synthetic_owner(item[:3], item[3])
        if role == "contract":
            contract = base.document(raw, "complete first-party C feature contract")
    base.need(type(contract) is dict,
              "reject omitted complete C source-only feature contract")
    assert isinstance(contract, dict)
    proof = feature_proof(base, previous, owners, contract)
    validate_proof(base, previous, proof)
    return proof


def make_svg(previous: types.ModuleType, modules: tuple,
             base: types.ModuleType, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(previous, modules, base, snapshot)
    source_sha = base.checked(source_sha, "exact first-party C V65 renderer")
    inputs_sha = base.checked(inputs_sha, "exact first-party C V65 inputs")
    visible = old_svg.decode("utf-8")
    base.need(visible.count('aria-labelledby="v64-title v64-description"') == 1,
              "preserve exact accessible current V64 chart")
    visible = visible.replace("v64-title", "v65-title").replace(
        "v64-description", "v65-description")
    lines = visible.splitlines()
    base.need(len(lines) > 100
              and lines[1].startswith('<title id="v65-title">')
              and lines[2].startswith('<desc id="v65-description">'),
              "preserve the genuine current accessible V64 overview")
    lines[1] = (
        '<title id="v65-title">Building a faster Python re: Python '
        'verified; six from-scratch engines; none yet compatible or '
        'measured faster</title>'
    )
    lines[2] = (
        '<desc id="v65-description">The pinned stable Python 3.14.6 '
        'reference is verified. Two independent Python workers each passed '
        'all 8,244 additional checks. The original 31,237 compatibility '
        'checks remain separate. Six independently implemented replacement '
        'families exist; none is qualified and no speed is measured. '
        'An actual earlier C run failed with 1,230 differences and 7,325 '
        'independently verified passes. A complete new, from-scratch C '
        'subject-buffer ownership repair has been frozen as source only; '
        'it has NOT BEEN BUILT, NOT BEEN TESTED, and has no measured '
        'result. The actual Rust run failed with 1,440 differences and '
        '14,853 independently verified passes across all 13 original '
        'suites and six genuine failure witnesses. Earlier Zig results '
        'included 1,764 and 2,172 differences; Zig has not been retested. '
        'The historical Rust V17 build remains BLOCKED because it requires '
        'the historical blocked P0 V2. The version-4 Python oracle is '
        'PASS and authorizes candidate tests, but seven candidate '
        'qualification blockers remain. Exactly four new independently '
        'authenticated C feature owners raise lower bounds from 216 / 221 '
        'to 220 / 225. Runtime independence is NOT ESTABLISHED. Speed, '
        'memory, uncertainty, and undefined behavior are NOT MEASURED. '
        'The 4,194,304-case holdout is NOT GENERATED and NOT OPENED.</desc>'
    )
    visible = "\n".join(lines)
    replacements = (
        ('<text x="218" y="701" class="body amber strong">Not retested</text>',
         '<text x="218" y="701" class="body amber strong">New source; not built or tested</text>'),
        ('<text x="525" y="701" class="body">Earlier attempts: 1,262 and 1,230 differences</text>',
         '<text x="525" y="701" class="body">Earlier real test: 1,230 differences, 7,325 verified passes</text>'),
        ('<text x="67" y="909" class="small">One Rust family has actually been tested. Currently active: 0. Compatible: 0. No replacement has a measured speed.</text>',
         '<text x="67" y="909" class="small">Six from-scratch families; C repair not built or tested; compatible: 0; every replacement speed: NOT MEASURED.</text>'),
        ('<text x="67" y="1450" class="body"><tspan class="strong">C:</tspan> historical 1,230 and 1,262.</text>',
         '<text x="67" y="1450" class="body"><tspan class="strong">C:</tspan> real earlier test: 1,230 differences, 7,325 verified passes; new repair not built.</text>'),
        ('<text x="64" y="1756" class="heading">Oracle ready; all seven candidate qualification blockers remain</text>',
         '<text x="64" y="1756" class="heading">New C repair frozen; all seven compatibility blockers remain</text>'),
        ('<text x="67" y="1787" class="body">Exactly three new readiness-source owners raise lower bounds from 213 / 218 to 216 / 221.</text>',
         '<text x="67" y="1787" class="body">Four exact first-party C source owners raise evidence lower bounds from 216 / 221 to 220 / 225.</text>'),
        ('<text x="67" y="1814" class="small">Real Rust failures remain proven. Python is verified; candidate qualification remains BLOCKED and speed is NOT MEASURED.</text>',
         '<text x="67" y="1814" class="small">Python is verified; actual C and Rust still fail; the new C repair is untested; speed remains NOT MEASURED.</text>'),
    )
    for before, after in replacements:
        base.need(visible.count(before) == 1,
                  "preserve exact prior chart without inventing a C result")
        visible = visible.replace(before, after, 1)
    lines = visible.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.startswith('<rect x="44" y="1858" width="1352"')), None)
    base.need(type(start) is int, "retain real V64 chart and evidence footer")
    assert isinstance(start, int)
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="381" rx="16" fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">First-party C source frozen; real compatibility and speed still unproven</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V64 graph renderer SHA-256", V64["source"][1]),
        ("Historical V64 graph summary SHA-256", V64["summary"][1]),
        ("First-party C native source SHA-256", FEATURE["variant"][1]),
        ("First-party C source verifier SHA-256", FEATURE["source"][1]),
        ("First-party C source protocol SHA-256", FEATURE["protocol"][1]),
        ("First-party C complete source contract SHA-256", FEATURE["contract"][1]),
        ("Verified Python oracle contract SHA-256", previous.READINESS["contract"][1]),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(f'<text x="65" y="{1914 + index * 18}" class="foot">'
                     f'{label}: {value}</text>')
    lines.extend((
        '<text x="65" y="2090" class="small">Python: VERIFIED. New C repair: SOURCE FROZEN; NOT BUILT; NOT TESTED.</text>',
        '<text x="65" y="2110" class="small">Actual earlier C: FAIL; 1,230 differences; 7,325 verified passes.</text>',
        '<text x="65" y="2130" class="small">Actual Rust: FAIL; 1,440 differences; 14,853 verified passes; 13 suites; six witnesses.</text>',
        '<text x="65" y="2150" class="small">Oracle: PASS. Candidate qualification: BLOCKED; seven blockers. Rust V17: BLOCKED.</text>',
        '<text x="65" y="2170" class="small">Six from-scratch families; qualified: 0; speed and memory: NOT MEASURED.</text>',
        '<text x="65" y="2190" class="small">Evidence lower bounds: 220 / 225. Runtime independence: NOT ESTABLISHED.</text>',
        '<text x="65" y="2210" class="small">Final 4,194,304-case holdout: NOT GENERATED and NOT OPENED.</text>',
        '<!-- First-party graph reads authenticated source only; no candidate, compiler, native library, clock, benchmark, archive, or hidden holdout is executed or opened. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in footers:
        base.need(raw.count((label + ": " + value).encode("ascii")) == 1,
                  "authenticate one complete V65 chart evidence footer")
    lower = raw.lower()
    for phrase in (b"building a faster python re", b"six from-scratch",
                   b"verified", b"source frozen", b"not built", b"not tested",
                   b"1,230", b"7,325", b"1,440", b"14,853", b"1,764",
                   b"2,172", b"13 suites", b"six witnesses", b"31,237",
                   b"8,244", b"220 / 225", b"216 / 221", b"rust v17",
                   b"blocked", b"seven", b"not measured", b"not established",
                   b"4,194,304", b"not generated", b"not opened"):
        base.need(phrase in lower, "reject missing honest C feature: " + repr(phrase))
    for falsehood in (b"v17 authorized", b"c repair passed", b"new c passed",
                      b"candidate qualified", b"three qualified candidates",
                      b"all candidate tests passed", b"holdout opened",
                      b"holdout generated", b"benchmark speedup",
                      b"winner selected", b"c engine built"):
        base.need(falsehood not in lower,
                  "reject invented native build or performance: " + repr(falsehood))
    return raw


def build(previous: types.ModuleType, modules: tuple, base: types.ModuleType,
          options: argparse.Namespace) -> tuple:
    own_sha = base.checked(options.source_sha256, "exact exclusive V65 renderer")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound exact independently owned V65 source")
    own_raw, _ = base.read_owner(SELF, own_sha, options.source_bytes, private=True)
    old, old_inputs, old_svg = authenticate_previous(previous, modules, base, options)
    proof = authenticate_feature(previous, base, options)
    historical = old["actual_c_v4_original_campaign"]
    changes = updates(proof, historical)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(changes)
    snapshot["preserved_v64_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in changes if key in original
    }
    validate_snapshot(previous, modules, base, snapshot)
    predecessor = {role: base.pin(*item[:3]) for role, item in V64.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({"schema": SCHEMA + "-inputs", "version": 65,
                   "python": "3.14.6",
                   "renderer": base.pin(SELF, own_sha, len(own_raw)),
                   "previous_overview": predecessor, **changes})
    input_raw = base.canonical(inputs)
    svg = make_svg(previous, modules, base, snapshot, old_svg,
                   own_sha, base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "preserve exactly six independently authored engine families")
    for row in families:
        if row.get("family") != "python":
            row.update({"authenticated_evidence_owner_lower_bound": 220,
                        "authenticated_history_reference_lower_bound": 225,
                        "qualified": False,
                        "performance": "NOT MEASURED"})
        if row.get("family") == "c":
            row.update({
                "current_original_campaign_candidate_status": "FAIL",
                "current_original_campaign_semantic_mismatch_count": 1230,
                "current_original_campaign_verified_passing_case_count": 7325,
                "c_subject_buffer_ownership_v1_feature_status": "SOURCE FROZEN",
                "c_subject_buffer_ownership_v1_build_status": "NOT BUILT",
                "c_subject_buffer_ownership_v1_matching_status": "NOT RUN",
                "c_subject_buffer_ownership_v1_candidate_correctness": "NOT MEASURED",
                "c_subject_buffer_ownership_v1_candidate_qualified": False,
                "c_subject_buffer_ownership_v1_compiler_process_count": 0,
                "c_subject_buffer_ownership_v1_candidate_workers_started": 0,
                "c_subject_buffer_ownership_v1_independent_source_owner_count": 4,
                "c_subject_buffer_ownership_v1_source_freeze": copy.deepcopy(proof),
            })
    summary = copy.deepcopy(old)
    summary.update({"schema": SCHEMA + "-summary", "version": 65,
                    "status": "PASS", "python": "3.14.6",
                    "source": base.pin(SELF, own_sha, len(own_raw)),
                    "inputs": base.pin(OUTPUT + ".inputs.json",
                                       base.digest(input_raw), len(input_raw)),
                    "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
                    "previous_overview": predecessor, "snapshot": snapshot,
                    "families": families, **changes})
    base.need(inputs["actual_current_graph_predecessor_version"] == 64
              and summary["actual_current_graph_predecessor_version"] == 64
              and snapshot["actual_current_graph_predecessor_version"] == 64
              and snapshot["preserved_v64_replaced_snapshot_fields"]
                  ["actual_current_graph_predecessor_version"] == 63
              and summary["phase1_v4_oracle_readiness_status"] == "PASS"
              and summary["candidate_evaluation_authorized"] is True
              and summary["candidate_qualification_status"] == "BLOCKED"
              and len(summary["candidate_qualification_blockers"]) == 7
              and summary["qualified_candidate_count"] == 0
              and summary["rust_native_build_v17_authorization_status"] == "BLOCKED"
              and summary["rust_native_build_v17_status"] == "NOT RUN"
              and summary["c_subject_buffer_ownership_v1_build_status"] == "NOT BUILT"
              and summary["c_subject_buffer_ownership_v1_matching_status"] == "NOT RUN"
              and summary["authenticated_evidence_owner_lower_bound"] == 220
              and summary["authenticated_history_reference_lower_bound"] == 225,
              "bind true V64 history without claiming C build or qualification")
    summary_raw = base.canonical(summary)
    base.need(max(len(input_raw), len(summary_raw), len(svg)) <= base.OWNER_LIMIT,
              "bound only the three authorized complete V65 graph assets")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def self_test(previous: types.ModuleType, modules: tuple,
              base: types.ModuleType) -> dict:
    prior = previous.self_test(modules)
    base.need(prior.get("status") == "PASS"
              and prior.get("rejected_hostile_control_count") == 5228
              and prior.get("actual_current_graph_predecessor_version") == 63
              and prior.get("phase1_v4_oracle_readiness_status") == "PASS"
              and prior.get("candidate_qualification_status") == "BLOCKED"
              and prior.get("rust_native_build_v17_authorization_status") == "BLOCKED"
              and prior.get("actual_rust_semantic_mismatch_count") == 1440
              and prior.get("authenticated_evidence_owner_lower_bound") == 216
              and prior.get("authenticated_history_reference_lower_bound") == 221,
              "preserve all 5,228 genuine V64 adversarial controls")
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {role: base.synthetic_owner(item[:3], item[3])
                  for role, item in FEATURE.items()}
        contract = synthetic_contract(base, previous)
        proof = feature_proof(base, previous, owners, contract)
        validate_proof(base, previous, proof)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = forged(value)
            rejected += reject_control(base, previous, hostile, "proof:" + key)
        for role, owner in owners.items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = forged(value)
                rejected += reject_control(base, previous, hostile,
                                           "owner:" + role + ":" + key)
        for key in ("schema", "version", "family", "phase", "source",
                    "protocol", "delegation_policy", "source_only_effects"):
            hostile = copy.deepcopy(proof)
            hostile["complete_feature_contract"][key] = forged(contract[key])
            rejected += reject_control(base, previous, hostile,
                                       "contract:" + key)
        for group in ("complete_first_party_c_variant", "historical_c_observation",
                      "current_rust_v10_history", "corrected_c_only_v10_runner",
                      "corrected_p0_v4_readiness", "phase_one", "published_v64"):
            expected = synthetic_contract(base, previous)[group]
            for key, value in expected.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_feature_contract"][group][key] = forged(value)
                rejected += reject_control(base, previous, hostile,
                                           group + ":" + key)
        for key, value in EFFECTS.items():
            hostile = copy.deepcopy(proof)
            hostile["source_only_effects"][key] = forged(value)
            rejected += reject_control(base, previous, hostile,
                                       "effect:" + key)
        base.need(rejected >= 130,
                  "require complete independent hostile C feature controls")
        result = {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 65,
            "status": "PASS",
            "previous_v64_hostile_controls": 5228,
            "new_v65_hostile_controls": rejected,
            "rejected_hostile_control_count": 5228 + rejected,
            "source_only_controls_blocked_by_kind": dict(wall.blocked),
            "actual_current_graph_predecessor_version": 64,
            "authenticated_evidence_owner_lower_bound": 220,
            "authenticated_history_reference_lower_bound": 225,
            "actual_c_semantic_mismatch_count": 1230,
            "actual_c_verified_passing_case_count": 7325,
            "actual_rust_semantic_mismatch_count": 1440,
            "actual_rust_verified_passing_case_count": 14853,
            "phase1_v4_oracle_readiness_status": "PASS",
            "candidate_evaluation_authorized": True,
            "candidate_qualification_status": "BLOCKED",
            "candidate_qualification_blocker_count": 7,
            "rust_native_build_v17_authorization_status": "BLOCKED",
            "rust_native_build_v17_blocking_reason":
                "FROZEN V17 REQUIRES HISTORICAL BLOCKED P0 V2",
            "c_subject_buffer_ownership_v1_feature_status": "SOURCE FROZEN",
            "c_subject_buffer_ownership_v1_build_status": "NOT BUILT",
            "c_subject_buffer_ownership_v1_matching_status": "NOT RUN",
            "c_subject_buffer_ownership_v1_independent_source_owner_count": 4,
            "actual_feature_source_owners_read_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "first_party_source_inventory_family_count": 6,
            "qualified_candidate_count": 0,
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        }
    return result


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json",
                       OUTPUT + ".svg"}
              and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only three exclusively authorized V65 graph assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact exclusive V65 graph byte")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(owner.st_uid == os.geteuid() and owner.st_dev == 2064
                  and owner.st_nlink == 1 and owner.st_size == len(raw)
                  and stat.S_IMODE(owner.st_mode) == 0o600,
                  "publish one complete privately owned V65 graph asset")
    finally:
        os.close(handle)
    confirmed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(confirmed == raw, "reauthenticate exact new V65 graph owner")


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict, source_sha: str, written: bool) -> dict:
    fields = ("actual_current_graph_predecessor_version",
              "authenticated_evidence_owner_lower_bound",
              "authenticated_history_reference_lower_bound",
              "actual_c_semantic_mismatch_count",
              "actual_c_verified_passing_case_count",
              "actual_rust_semantic_mismatch_count",
              "actual_rust_verified_passing_case_count",
              "phase1_v4_oracle_readiness_status",
              "candidate_evaluation_authorized",
              "candidate_qualification_status", "candidate_qualification_blockers",
              "rust_native_build_v17_authorization_status",
              "rust_native_build_v17_blocking_reason", "rust_native_build_v17_status",
              "c_subject_buffer_ownership_v1_feature_status",
              "c_subject_buffer_ownership_v1_build_status",
              "c_subject_buffer_ownership_v1_matching_status",
              "c_subject_buffer_ownership_v1_candidate_correctness",
              "c_subject_buffer_ownership_v1_independent_source_owner_count",
              "actual_compiler_processes_started_by_graph",
              "actual_candidate_workers_started_by_graph",
              "actual_clock_samples_by_graph", "actual_hidden_cases_read_by_graph",
              "full_case_denominator", "suite_count",
              "first_party_source_inventory_family_count", "qualified_candidate_count",
              "final_comparison_planned_case_count", "final_comparison_cases_generated",
              "final_holdout_opened", "runtime_no_delegation", "performance",
              "memory", "confidence_intervals", "undefined_behavior", "winner_selected")
    return {"schema": SCHEMA + ("-published" if written
                                 else "-read-only-frozen-context"),
            "version": 65, "status": "PASS", "source_sha256": source_sha,
            "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
            "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
            "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
            "previous_overview_version": 64,
            **{"previous_overview_" + role + "_sha256": item[1]
               for role, item in V64.items()},
            **{"feature_" + role + "_sha256": item[1]
               for role, item in FEATURE.items()},
            **{key: copy.deepcopy(snapshot[key]) for key in fields},
            "outputs_written": written}


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V64:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("source", "protocol", "contract"):
        parser.add_argument("--readiness-" + role + "-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, modules, base = load_v64()
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes", "inputs_sha256",
                         "summary_sha256", "svg_sha256"]
            forbidden += ["previous_" + role + "_sha256" for role in V64]
            forbidden += ["feature_" + role + "_sha256" for role in FEATURE]
            forbidden += ["readiness_" + role + "_sha256"
                          for role in previous.READINESS]
            base.need(all(getattr(options, key) is None for key in forbidden),
                      "source-only V65 self-test never reads feature owners")
            sys.stdout.buffer.write(base.canonical(self_test(previous, modules, base)))
            return 0
        snapshot, pairs = build(previous, modules, base, options)
        outputs = dict(pairs)
        own_sha = base.checked(options.source_sha256, "exact authorized V65 source")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "publish only the exact three newly authorized V65 assets")
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(base, snapshot, outputs, own_sha, True)
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(options.inputs_sha256,
                                                       "exact complete V65 inputs"),
                OUTPUT + ".json": base.checked(options.summary_sha256,
                                                "exact complete V65 summary"),
                OUTPUT + ".svg": base.checked(options.svg_sha256,
                                               "exact complete V65 SVG"),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                         private=True)
                base.need(raw == outputs[path],
                          "reproduce complete source-only V65 owner: " + path)
            result = compact_result(base, snapshot, outputs, own_sha, False)
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V65 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V65 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
