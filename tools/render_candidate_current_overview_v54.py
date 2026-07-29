#!/usr/bin/env python3
"""Show the real Rust controller failure without inventing a matching result."""

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
SELF = "tools/render_candidate_current_overview_v54.py"
OUTPUT = "docs/evidence/candidate-current-overview-v54"
SCHEMA = "rebar-candidate-current-overview-v54"
V53 = {
    "source": ("tools/render_candidate_current_overview_v53.py",
               "db189f1363344ea60246856bf99bb16a1716121402bd3cae441ff285729dfa26",
               66130),
    "inputs": ("docs/evidence/candidate-current-overview-v53.inputs.json",
               "6091b9af13a5b3b20a0f6f8748c2924302befa18ce7f4a61966dc1941299f7aa",
               612623),
    "summary": ("docs/evidence/candidate-current-overview-v53.json",
                "f77af624365ca510c750c529787500429a831cf1f4b478ceb5f614f6802579e6",
                1688446),
    "svg": ("docs/evidence/candidate-current-overview-v53.svg",
            "f44910f17160e1e22958424b9627151cbdd2ebbd364d138490c67640d0b877c4",
            14069),
}
FAILURE = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v8-rust-phase2-v16-rust-buffer-"
    "shape-pickle-original-p0-entry-failure.json",
    "6a955d8ce361650395d1d7a4090a9bb1a6348b135143e2d65e63c8f5e196f9d0",
    4348,
)
OBSERVATION = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v8-rust-phase2-v16-rust-buffer-"
    "shape-pickle-original-p0-entry-failure-observation.json",
    "76e476bd4d61dd0dc456c796953f024f98d6c581910ce9d30b6379f6ec8cac23",
    5739,
)
DEVICE = 2064
FAILURE_INODE = 525012
OBSERVATION_INODE = 525013
RUNNER_SOURCE = "eb36dd1b16775e00525f9d0ad4d1bab46318d4c652c0cf6653bd1aa8776265aa"
RUNNER_PROTOCOL = "9afa6f964bceaa950e4031bcd00b27a615635a6bb6ed3eb66cd60ba1f123ec30"
RUNNER_CONTRACT = "7780c4d14fe043ebe25ff50b4a437e6a0c9ba975f6d4cc47a833bbfbe3cdcf80"
BUILD_ARCHIVE_SHA = "c24c0e1544003b231bac3e45601faabfd1c1e5c181d89fce7d660a2df4a29270"
UNCOMPRESSED_ARCHIVE_SHA = "c89af182cdb8e98dc05a4538e620c1db8404fbd7a11a3d43fea54f9da609f9c5"
ERROR_MESSAGE = "reject a missing, invented, crossed, or duplicate build PID"
PUSHED_HEAD = "32d737e9b8642da92399c414a8f87a4c7c9ae5e7"
PUBLIC_COUNTS = {"PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
                 "NOT ESTABLISHED": 1, "NOT OPENED": 1}
LARGE_COUNTS = {"PASS": 22, "FAIL": 1, "NOT RUN": 3,
                "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1}
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]


def load_v53() -> tuple:
    path, fingerprint, size = V53["source"]
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
            raise ValueError("reject substituted pushed V53 graph renderer")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated pushed V53 graph renderer")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended pushed V53 graph renderer")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed pushed V53 graph renderer")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_actual_pushed_source_graph_v53")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v52()
    base = prior_modules[-1]
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v53"
              and previous.SELF == path
              and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
              and previous.LARGE_COUNTS == LARGE_COUNTS,
              "authenticate only the exact actually pushed V53 graph source")
    return previous, prior_modules, base


def failure_effects() -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v8-"
                  "authorized-real-run-effect-ledger",
        "campaign_mode": "AUTHORIZED RUN",
        "campaign_source_sha256": RUNNER_SOURCE,
        "campaign_protocol_sha256": RUNNER_PROTOCOL,
        "campaign_contract_sha256": RUNNER_CONTRACT,
        "v16_build_archive_read_attempted": True,
        "v16_build_archive_read_count": 1,
        "v16_build_archive_compressed_bytes_read": 109671,
        "v16_build_archive_gzip_inflation_attempted": True,
        "v16_build_archive_gzip_inflation_count": 1,
        "v16_build_archive_uncompressed_bytes_read": 765382,
        "v16_build_archive_uncompressed_sha256": UNCOMPRESSED_ARCHIVE_SHA,
        "actual_candidate_workers": 0,
        "actual_worker_process_ids": [],
        "actual_native_activations": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "attempted_suite_count": 0,
        "started_suite_count": 0,
        "fully_observed_suite_count": 0,
        "worker_attempts": [],
        "retained_suite_results": [],
        "activated_target_roles": [],
        "canonical_target_replacements": 0,
        "recovery_journals_created": 0,
        "recovery_roots_created": 0,
        "recovery_locks_acquired": 0,
        "recovery_journal_announced": False,
        "recovery_journal_creation_attempted": False,
        "recovery_root_creation_attempted": False,
        "recovery_lock_attempted": False,
        "publication_attempted": False,
        "publication_status": "NOT ATTEMPTED",
        "archive_publication_attempted": False,
        "archive_publication_status": "NOT ATTEMPTED",
        "receipt_publication_attempted": False,
        "receipt_publication_status": "NOT ATTEMPTED",
        "archive_owner": None,
        "receipt_owner": None,
        "candidate_qualified": False,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_failure(base: types.ModuleType, failure: object) -> None:
    base.need(type(failure) is dict, "reject missing real controller stdout")
    assert isinstance(failure, dict)
    expected = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v8-entry-failure",
        "status": "FAIL",
        "family": "rust",
        "error_type": "CampaignError",
        "error_message": ERROR_MESSAGE,
        "actual_operation_mode": "AUTHORIZED RUN",
        "source_only_zero_effects_claimed": False,
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    for key, value in expected.items():
        base.need(type(failure.get(key)) is type(value)
                  and failure[key] == value,
                  "reject forged actual V8 entry failure: " + key)
    actual = failure.get("actual_effects")
    base.need(type(actual) is dict,
              "preserve the complete real archive-read effect ledger")
    assert isinstance(actual, dict)
    for key, value in failure_effects().items():
        base.need(type(actual.get(key)) is type(value)
                  and actual[key] == value,
                  "reject hidden actual controller effect: " + key)
    base.need(actual.get("canonical_target_reads") == "NOT MEASURED"
              and actual.get("canonical_target_stats") == "NOT MEASURED",
              "never invent exact canonical target read or stat counts")
    base.need(type(failure.get("traceback")) is str
              and ERROR_MESSAGE in failure["traceback"],
              "preserve the complete actual controller failure traceback")


def validate_observation(base: types.ModuleType,
                         observation: object) -> None:
    base.need(type(observation) is dict,
              "reject missing independent actual controller observation")
    assert isinstance(observation, dict)
    expected = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v8-"
                  "entry-failure-observation-v1",
        "version": 1,
        "status": "PASS",
        "observation_pass_means":
            "DURABLE OBSERVATION OF A FAILED CANDIDATE CONTROLLER; "
            "NOT A PASSING CANDIDATE",
        "observed_operation": "ONE AUTHORIZED RUST V8 ORIGINAL-CAMPAIGN RUN",
        "actual_pushed_runner_head": PUSHED_HEAD,
        "authenticated_evidence_owner_lower_bound_before_publication": 184,
        "authenticated_history_reference_lower_bound_before_publication": 189,
        "new_actual_observation_owner_count": 2,
        "resulting_authenticated_evidence_owner_lower_bound": 186,
        "resulting_authenticated_history_reference_lower_bound": 191,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "actual_timing_trials": 0,
        "winner_selected": False,
    }
    for key, value in expected.items():
        base.need(type(observation.get(key)) is type(value)
                  and observation[key] == value,
                  "reject invented V8 controller observation: " + key)
    failure = observation.get("observed_failure")
    expected_failure = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v8-entry-failure",
        "status": "FAIL",
        "error_type": "CampaignError",
        "error_message": ERROR_MESSAGE,
        "failure_category":
            "AUTHENTIC BUILD-PROCESS SHAPE REJECTED BEFORE CANDIDATE ACTIVATION",
        "candidate_matching": "NOT RUN",
        "full_original_case_denominator": 31237,
        "original_suite_count": 13,
        "started_suite_count": 0,
        "completed_suite_count": 0,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "candidate_qualified": False,
    }
    base.need(type(failure) is dict,
              "retain an independently observed failed controller")
    assert isinstance(failure, dict)
    for key, value in expected_failure.items():
        base.need(type(failure.get(key)) is type(value)
                  and failure[key] == value,
                  "reject false observed candidate outcome: " + key)
    recorded = observation.get("exact_recorded_controller_stdout")
    base.need(
        type(recorded) is dict
        and recorded.get("path") == FAILURE[0]
        and recorded.get("sha256") == FAILURE[1]
        and recorded.get("bytes") == FAILURE[2]
        and recorded.get("device") == DEVICE
        and recorded.get("inode") == FAILURE_INODE
        and recorded.get("mode") == "600"
        and recorded.get("nlink") == 1
        and recorded.get("lossless_original_controller_json") is True,
        "bind lossless failed controller stdout to its exact genuine inode",
    )
    archive = observation.get("actual_build_archive_effects")
    expected_archive = {
        "compressed_build_archive_sha256": BUILD_ARCHIVE_SHA,
        "actual_archive_read_count": 1,
        "actual_archive_inflation_count": 1,
        "compressed_bytes_read": 109671,
        "uncompressed_bytes_read": 765382,
        "uncompressed_sha256": UNCOMPRESSED_ARCHIVE_SHA,
    }
    base.need(type(archive) is dict,
              "preserve one actual archive read without opening any archive")
    assert isinstance(archive, dict)
    for key, value in expected_archive.items():
        base.need(type(archive.get(key)) is type(value)
                  and archive[key] == value,
                  "reject erased genuine controller archive effect: " + key)
    targets = observation.get("actual_target_effects")
    base.need(
        type(targets) is dict
        and targets.get("canonical_target_replacements") == 0
        and targets.get("recovery_roots_created") == 0
        and targets.get("recovery_journals_created") == 0
        and targets.get("activated_target_roles") == []
        and targets.get("restored_target_roles") == []
        and targets.get("all_four_original_targets_unchanged_without_recovery")
        is True
        and targets.get("all_four_original_targets_restored_by_a_recovery")
        is False
        and type(targets.get("original_targets")) is list
        and len(targets["original_targets"]) == 4,
        "distinguish four untouched targets from nonexistent recovery")
    historical = observation.get("historical_actual_candidate_matching")
    base.need(
        type(historical) is dict
        and historical.get("status") == "FAIL"
        and historical.get("semantic_mismatch_count") == 928
        and historical.get("verified_passing_case_count") == 8965
        and historical.get("completed_suite_count") == 13
        and historical.get("distinct_worker_process_id_count") == 13,
        "keep genuine V7 candidate matching distinct from a V8 controller failure",
    )
    frozen = observation.get("frozen_runner")
    base.need(
        type(frozen) is dict
        and frozen.get("source", {}).get("sha256") == RUNNER_SOURCE
        and frozen.get("source", {}).get("bytes") == 164002
        and frozen.get("protocol", {}).get("sha256") == RUNNER_PROTOCOL
        and frozen.get("protocol", {}).get("bytes") == 10563
        and frozen.get("contract", {}).get("sha256") == RUNNER_CONTRACT
        and frozen.get("contract", {}).get("bytes") == 13749,
        "bind the exact actually executed pushed V8 controller")
    cause = observation.get("root_cause")
    base.need(
        type(cause) is dict
        and cause.get("validator_function") == "validate_build_report"
        and cause.get("authoritative_build_function")
        == "verify_reproduced_phases"
        and cause.get("withdrawn_oracle_cases") == 0
        and cause.get("new_private_waivers") == 0
        and type(cause.get("required_future_fix")) is str
        and "phase" in cause["required_future_fix"].lower(),
        "preserve the real process-shape validator cause and unchanged oracle")


def validate_owner(base: types.ModuleType, owner: object,
                   item: tuple[str, str, int], inode: int,
                   description: str) -> None:
    base.need(
        type(owner) is dict
        and owner.get("path") == item[0]
        and owner.get("sha256") == item[1]
        and owner.get("bytes") == item[2]
        and owner.get("device") == DEVICE
        and owner.get("inode") == inode
        and owner.get("mode") == "0600"
        and owner.get("nlink") == 1
        and owner.get("uid") == os.geteuid(),
        "authenticate only a released bounded plaintext " + description,
    )


def make_failure_proof(base: types.ModuleType,
                       failure_owner: dict, failure: dict,
                       observation_owner: dict, observation: dict) -> dict:
    validate_owner(base, failure_owner, FAILURE, FAILURE_INODE, "entry failure")
    validate_owner(base, observation_owner, OBSERVATION, OBSERVATION_INODE,
                   "independent observation")
    base.need(
        (failure_owner["device"], failure_owner["inode"])
        != (observation_owner["device"], observation_owner["inode"]),
        "require two genuinely separate actual plaintext outcome owners",
    )
    validate_failure(base, failure)
    validate_observation(base, observation)
    proof = {
        "schema": SCHEMA + "-authenticated-actual-v8-pre-matching-failure",
        "failure": copy.deepcopy(failure_owner),
        "complete_actual_failure": copy.deepcopy(failure),
        "observation": copy.deepcopy(observation_owner),
        "complete_independent_observation": copy.deepcopy(observation),
        "controller_status": "FAIL",
        "controller_failure_stage": "BUILD-PROCESS PREFLIGHT; NO MATCHING",
        "error_message": ERROR_MESSAGE,
        "observation_status": "PASS",
        "observation_pass_means":
            "DURABLE OBSERVATION OF A FAILED CANDIDATE CONTROLLER; "
            "NOT A PASSING CANDIDATE",
        "publication_candidate_status": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_semantic_mismatch_count": "NOT MEASURED",
        "candidate_verified_passing_case_count": "NOT MEASURED",
        "candidate_qualified": False,
        "actual_candidate_workers": 0,
        "started_suite_count": 0,
        "completed_suite_count": 0,
        "actual_native_activations": 0,
        "actual_target_replacements": 0,
        "actual_recovery_journals_created": 0,
        "all_four_original_targets_unchanged": True,
        "actual_build_archive_reads_by_controller": 1,
        "actual_build_archive_inflations_by_controller": 1,
        "actual_build_archive_compressed_bytes_read": 109671,
        "actual_build_archive_uncompressed_bytes_read": 765382,
        "build_archive_read_by_graph": False,
        "build_archive_inflated_by_graph": False,
        "build_archive_sha256_recomputed_by_graph": False,
        "failure_archive_read_by_graph": False,
        "reference_archive_read_by_graph": False,
        "actual_graph_predecessor_version": 53,
        "historical_source_contract_graph_version": 52,
        "historical_source_contract_evidence_lower_bound": 181,
        "historical_source_contract_history_lower_bound": 186,
        "historical_source_contract_resulting_evidence_lower_bound": 183,
        "historical_source_contract_resulting_history_lower_bound": 188,
        "actual_current_prepublication_evidence_lower_bound": 184,
        "actual_current_prepublication_history_lower_bound": 189,
        "new_exact_actual_plaintext_owner_count": 2,
        "actual_current_evidence_lower_bound_after_publication": 186,
        "actual_current_history_lower_bound_after_publication": 191,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "preserved_v7_status": "FAIL",
        "preserved_v7_semantic_mismatch_count": 928,
        "preserved_v7_verified_passing_case_count": 8965,
        "preserved_v7_candidate_workers": 13,
        "actual_v16_build_status": "PASS",
        "actual_v16_compiler_process_count": 28,
        "hidden_cases_read": 0,
        "clock_samples_by_graph": 0,
        "timing_trials_run_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_actual_failure_binding_sha256"] = base.digest(
        base.canonical(proof))
    validate_failure_proof(base, proof)
    return proof


def validate_failure_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject omitted actual V8 entry failure")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-actual-v8-pre-matching-failure",
        "controller_status": "FAIL",
        "controller_failure_stage": "BUILD-PROCESS PREFLIGHT; NO MATCHING",
        "error_message": ERROR_MESSAGE,
        "observation_status": "PASS",
        "observation_pass_means":
            "DURABLE OBSERVATION OF A FAILED CANDIDATE CONTROLLER; "
            "NOT A PASSING CANDIDATE",
        "publication_candidate_status": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_semantic_mismatch_count": "NOT MEASURED",
        "candidate_verified_passing_case_count": "NOT MEASURED",
        "candidate_qualified": False,
        "actual_candidate_workers": 0,
        "started_suite_count": 0,
        "completed_suite_count": 0,
        "actual_native_activations": 0,
        "actual_target_replacements": 0,
        "actual_recovery_journals_created": 0,
        "all_four_original_targets_unchanged": True,
        "actual_build_archive_reads_by_controller": 1,
        "actual_build_archive_inflations_by_controller": 1,
        "actual_build_archive_compressed_bytes_read": 109671,
        "actual_build_archive_uncompressed_bytes_read": 765382,
        "build_archive_read_by_graph": False,
        "build_archive_inflated_by_graph": False,
        "build_archive_sha256_recomputed_by_graph": False,
        "failure_archive_read_by_graph": False,
        "reference_archive_read_by_graph": False,
        "actual_graph_predecessor_version": 53,
        "historical_source_contract_graph_version": 52,
        "historical_source_contract_evidence_lower_bound": 181,
        "historical_source_contract_history_lower_bound": 186,
        "historical_source_contract_resulting_evidence_lower_bound": 183,
        "historical_source_contract_resulting_history_lower_bound": 188,
        "actual_current_prepublication_evidence_lower_bound": 184,
        "actual_current_prepublication_history_lower_bound": 189,
        "new_exact_actual_plaintext_owner_count": 2,
        "actual_current_evidence_lower_bound_after_publication": 186,
        "actual_current_history_lower_bound_after_publication": 191,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "preserved_v7_status": "FAIL",
        "preserved_v7_semantic_mismatch_count": 928,
        "preserved_v7_verified_passing_case_count": 8965,
        "preserved_v7_candidate_workers": 13,
        "actual_v16_build_status": "PASS",
        "actual_v16_compiler_process_count": 28,
        "hidden_cases_read": 0,
        "clock_samples_by_graph": 0,
        "timing_trials_run_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    for key, value in expected.items():
        base.need(type(proof.get(key)) is type(value)
                  and proof[key] == value,
                  "reject invented actual controller outcome: " + key)
    validate_owner(base, proof.get("failure"), FAILURE, FAILURE_INODE,
                   "actual failed controller")
    validate_owner(base, proof.get("observation"), OBSERVATION,
                   OBSERVATION_INODE, "independent failure observation")
    validate_failure(base, proof.get("complete_actual_failure"))
    validate_observation(base, proof.get("complete_independent_observation"))
    body = {key: value for key, value in proof.items()
            if key != "complete_actual_failure_binding_sha256"}
    base.need(proof.get("complete_actual_failure_binding_sha256")
              == base.digest(base.canonical(body)),
              "bind every actual failed-controller byte and independent outcome")


def authenticate_failure(base: types.ModuleType,
                         options: argparse.Namespace) -> dict:
    for role, item, inode in (
        ("failure", FAILURE, FAILURE_INODE),
        ("observation", OBSERVATION, OBSERVATION_INODE),
    ):
        base.need(
            base.checked(getattr(options, role + "_sha256"),
                         "actual V8 " + role) == item[1]
            and getattr(options, role + "_bytes") == item[2]
            and getattr(options, role + "_inode") == inode
            and getattr(options, role + "_device") == DEVICE,
            "pin exact independently released plaintext V8 " + role,
        )
    failure_raw, failure_owner = base.read_owner(*FAILURE, private=True)
    observation_raw, observation_owner = base.read_owner(
        *OBSERVATION, private=True)
    return make_failure_proof(
        base, failure_owner,
        base.document(failure_raw, "lossless actual V8 controller stdout"),
        observation_owner,
        base.document(observation_raw, "independent actual V8 observation",
                      exact=False),
    )


def v53_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V53["source"][1],
        source_bytes=V53["source"][2],
        previous_source_sha256=previous.V52["source"][1],
        previous_inputs_sha256=previous.V52["inputs"][1],
        previous_summary_sha256=previous.V52["summary"][1],
        previous_svg_sha256=previous.V52["svg"][1],
        runner_source_sha256=previous.V8["source"][1],
        runner_source_bytes=previous.V8["source"][2],
        runner_protocol_sha256=previous.V8["protocol"][1],
        runner_protocol_bytes=previous.V8["protocol"][2],
        runner_contract_sha256=previous.V8["contract"][1],
        runner_contract_bytes=previous.V8["contract"][2],
    )


def authenticate_v53(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raws = {}
    for role, item in V53.items():
        base.need(base.checked(supplied.get(role),
                               "actual pushed V53 " + role) == item[1],
                  "pin the exact actually pushed V53 " + role)
        raws[role], _ = base.read_owner(*item, private=True)
    old = base.document(raws["summary"], "actual pushed V53 summary")
    inputs = base.document(raws["inputs"], "actual pushed V53 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(prior_modules, v53_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v53-summary"
        and old.get("version") == 53
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V53["source"])
        and old.get("inputs") == base.pin(*V53["inputs"])
        and old.get("svg") == base.pin(*V53["svg"])
        and inputs.get("schema")
        == "rebar-candidate-current-overview-v53-inputs"
        and inputs.get("renderer") == base.pin(*V53["source"])
        and old.get("snapshot") == reconstructed
        and raws["inputs"] == expected[V53["inputs"][0]]
        and raws["summary"] == expected[V53["summary"][0]]
        and raws["svg"] == expected[V53["svg"][0]]
        and old.get("authenticated_evidence_owner_lower_bound") == 184
        and old.get("authenticated_history_reference_lower_bound") == 189
        and old.get("actual_rust_v16_build_status") == "PASS"
        and old.get("actual_rust_v16_compiler_process_count") == 28
        and old.get("actual_rust_v7_semantic_status") == "FAIL"
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("rust_original_campaign_v8_matching_status") == "NOT RUN"
        and old.get("qualified_candidate_count") == 0
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce complete actual pushed V53 without opening any archive",
    )
    return old, inputs, raws["svg"]


def result_fields(proof: dict) -> dict:
    return {
        "actual_rust_v8_entry_failure": copy.deepcopy(proof),
        "actual_rust_v8_controller_status": "FAIL",
        "actual_rust_v8_controller_failure_stage":
            "BUILD-PROCESS PREFLIGHT; NO MATCHING",
        "actual_rust_v8_controller_error": ERROR_MESSAGE,
        "actual_rust_v8_observation_status": "PASS",
        "actual_rust_v8_observation_pass_means":
            "DURABLE OBSERVATION OF A FAILED CANDIDATE CONTROLLER; "
            "NOT A PASSING CANDIDATE",
        "actual_rust_v8_failure_owner": copy.deepcopy(proof["failure"]),
        "actual_rust_v8_observation_owner":
            copy.deepcopy(proof["observation"]),
        "actual_rust_v8_failure_sha256": FAILURE[1],
        "actual_rust_v8_observation_sha256": OBSERVATION[1],
        "actual_rust_v8_matching_status": "NOT RUN",
        "actual_rust_v8_candidate_correctness": "NOT MEASURED",
        "actual_rust_v8_semantic_mismatch_count": "NOT MEASURED",
        "actual_rust_v8_verified_passing_case_count": "NOT MEASURED",
        "actual_rust_v8_candidate_qualified": False,
        "actual_rust_v8_candidate_workers": 0,
        "actual_rust_v8_started_suite_count": 0,
        "actual_rust_v8_completed_suite_count": 0,
        "actual_rust_v8_native_activations": 0,
        "actual_rust_v8_target_replacements": 0,
        "actual_rust_v8_recovery_journals_created": 0,
        "actual_rust_v8_all_original_targets_unchanged": True,
        "actual_rust_v8_build_archive_reads_by_controller": 1,
        "actual_rust_v8_build_archive_inflations_by_controller": 1,
        "actual_rust_v8_build_archive_compressed_bytes_read": 109671,
        "actual_rust_v8_build_archive_uncompressed_bytes_read": 765382,
        "actual_rust_v8_build_archive_read_by_graph": False,
        "actual_rust_v8_build_archive_inflated_by_graph": False,
        "actual_rust_v8_build_archive_sha256_recomputed_by_graph": False,
        "actual_rust_v8_historical_contract_evidence_lower_bound": 181,
        "actual_rust_v8_historical_contract_history_lower_bound": 186,
        "actual_rust_v8_historical_contract_resulting_evidence_lower_bound":
            183,
        "actual_rust_v8_historical_contract_resulting_history_lower_bound":
            188,
        "actual_rust_v8_current_prepublication_evidence_lower_bound": 184,
        "actual_rust_v8_current_prepublication_history_lower_bound": 189,
        "actual_rust_v8_new_plaintext_outcome_owner_count": 2,
        "actual_current_graph_predecessor_version": 53,
        "authenticated_evidence_owner_lower_bound": 186,
        "authenticated_history_reference_lower_bound": 191,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
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
    base.need(type(snapshot) is dict, "reject missing complete V54 snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("actual_rust_v8_entry_failure")
    validate_failure_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(snapshot.get(key) == value,
                  "reject invented actual controller result: " + key)
    replaced = snapshot.get("preserved_v53_replaced_snapshot_fields")
    base.need(type(replaced) is dict,
              "preserve every replaced actually pushed V53 field")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v53_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(prior_modules, history)
    base.need(
        set(replaced).issubset(updates)
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and snapshot.get("large_input_source_case_matrix_count") == 32
        and snapshot.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and snapshot.get("large_input_upstream_original_case_count") == 2
        and snapshot.get("large_input_upstream_original_subject_bytes")
        == 2147483648
        and snapshot.get("actual_rust_v16_build_status") == "PASS"
        and snapshot.get("actual_rust_v16_compiler_process_count") == 28
        and snapshot.get("actual_rust_v16_compiler_pid_vector_present_in_receipt")
        is False
        and snapshot.get("actual_rust_v16_phase_vector_present_in_receipt")
        is False
        and snapshot.get("actual_rust_v16_native_artifact_digests_present_in_receipt")
        is False
        and snapshot.get("actual_rust_v7_semantic_status") == "FAIL"
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and snapshot.get("actual_rust_v7_candidate_workers") == 13
        and snapshot.get("actual_rust_worker_process_ids") == WORKERS
        and snapshot.get("actual_rust_original_campaign", {}).get(
            "semantic_mismatch_count") == 928
        and snapshot.get("actual_complete_rust_campaign", {}).get(
            "semantic_mismatch_count") == 928
        and snapshot.get("current_complete_rust_campaign", {}).get(
            "semantic_mismatch_count") == 928
        and snapshot.get("historical_rust_v3_original_campaign", {}).get(
            "semantic_mismatch_count") == 1087
        and snapshot.get("historical_rust_v4_original_campaign", {}).get(
            "semantic_mismatch_count") == 1036
        and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
        and snapshot.get("c_v4_original_campaign_semantic_mismatch_count")
        == 1230
        and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count")
        == 2172
        and snapshot.get("zig_v3_original_campaign_semantic_mismatch_count")
        == 1764
        and snapshot.get("rust_original_campaign_v8_matching_status")
        == "NOT RUN"
        and snapshot.get("actual_rust_v8_controller_status") == "FAIL"
        and snapshot.get("actual_rust_v8_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v8_semantic_mismatch_count")
        == "NOT MEASURED"
        and snapshot.get("actual_rust_v8_candidate_workers") == 0
        and snapshot.get("actual_rust_v8_build_archive_reads_by_controller")
        == 1
        and snapshot.get("actual_rust_v8_build_archive_inflations_by_controller")
        == 1
        and snapshot.get("actual_rust_v8_build_archive_read_by_graph")
        is False
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("actually_tested_corrected_candidate_families")
        == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
        == 1
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 186
        and snapshot.get("authenticated_history_reference_lower_bound") == 191
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("actual_native_libraries_loaded_by_graph") == 0
        and snapshot.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
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
        "preserve a pre-matching controller failure and all original evidence")


def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    v43 = prior_modules[9]
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact V54 renderer footer")
    inputs_sha = base.checked(inputs_sha, "exact V54 inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v53-title", "v54-title")
    visible = visible.replace("v53-description", "v54-description")
    changes = (
        ("Rust build passes; the next complete compatibility test is frozen, "
         "not run</title>",
         "Rust test runner failed before matching; no compatible replacement "
         "yet</title>",
         "report a controller failure, not a new semantic test"),
        ("A first-party runner for all 31,237 original checks and all 13 "
         "suites is now frozen; its new matching run has not happened.",
         "The new first-party test controller failed while checking the "
         "recorded native build, before starting any matching worker.",
         "distinguish the actual zero-worker controller failure"),
        ("Three and only three independently authenticated frozen-runner "
         "source owners raise current lower bounds from 181 and 186 to "
         "184 and 189;",
         "Two and only two independently authenticated plaintext failure "
         "owners raise actual current lower bounds from 184 and 189 to "
         "186 and 191;",
         "count only the real failure output and independent observation"),
        ("Rust build: PASS — next full-suite test: FROZEN, NOT RUN",
         "Rust test runner failed before matching",
         "give the user an honest controller-failure headline"),
        ("The first-party Rust build passed. Its 31,237-check, 13-suite "
         "matching runner is frozen, NOT RUN; it remains the same Rust "
         "family.",
         "The native build passed, but the test runner rejected its process "
         "record before activation. Matching: NOT RUN. New workers: 0.",
         "preserve both the valid build and genuinely untested candidate"),
        ("Old test failed; new full-suite runner frozen, not run",
         "Old test failed; new runner stopped before matching",
         "keep the last genuine 928-difference matching result"),
        ("Native build passed; new full-suite test frozen, not run",
         "Rust test runner failed before matching",
         "show the actual separately observed controller failure"),
        ("Exactly three frozen full-suite runner source files raise actual "
         "current lower bounds from 181 / 186 to 184 / 189.",
         "Exactly two real plaintext failure records raise actual current "
         "lower bounds from 184 / 189 to 186 / 191.",
         "use actual V53 current floors rather than historical contract floors"),
    )
    for before, after, reason in changes:
        visible = v43.replace_once(base, visible, before, after, reason)
    lines = visible.splitlines()
    start = next(
        index for index, line in enumerate(lines)
        if line.startswith('<rect x="44" y="1858" width="1352"')
    )
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="361" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact reproducible '
        'controller-failure evidence</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V53 graph inputs SHA-256", V53["inputs"][1]),
        ("Historical V53 graph renderer SHA-256", V53["source"][1]),
        ("Historical V53 graph summary SHA-256", V53["summary"][1]),
        ("Historical V53 graph image SHA-256", V53["svg"][1]),
        ("Exact V8 failed-controller stdout SHA-256", FAILURE[1]),
        ("Independent failure observation SHA-256", OBSERVATION[1]),
        ("Actually executed V8 runner source SHA-256", RUNNER_SOURCE),
        ("Actually executed V8 runner protocol SHA-256", RUNNER_PROTOCOL),
        ("Actually executed V8 runner contract SHA-256", RUNNER_CONTRACT),
        ("Recorded build archive SHA-256 (not opened by this graph)",
         BUILD_ARCHIVE_SHA),
        ("Recorded build uncompressed SHA-256 (observation only)",
         UNCOMPRESSED_ARCHIVE_SHA),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + 18 * index}" class="foot">'
            f'{label}: {value}</text>')
    lines.extend((
        '<text x="65" y="2167" class="small">The failed controller '
        'read and inflated its native-build archive once. This graph '
        'does not open any archive.</text>',
        '<text x="65" y="2187" class="small">Historical contract '
        '181 / 186 → 183 / 188; actual pushed V53 184 / 189 → '
        '186 / 191.</text>',
        '<text x="65" y="2207" class="small">New candidate matching: '
        'NOT RUN. Hidden comparison: unopened. Faster compatible '
        'replacement: none.</text>',
        '<!-- Controller failure before matching. No archive, candidate, '
        'native library, clock, or holdout is opened by this graph. -->',
        '</svg>',
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, fingerprint in (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V53 graph inputs SHA-256", V53["inputs"][1]),
        ("Historical V53 graph renderer SHA-256", V53["source"][1]),
        ("Historical V53 graph summary SHA-256", V53["summary"][1]),
        ("Historical V53 graph image SHA-256", V53["svg"][1]),
    ):
        base.need(raw.count((label + ": " + fingerprint).encode("ascii"))
                  == 1, "authenticate the current or historical graph footer")
    base.need(
        ("Graph inputs SHA-256: " + V53["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V53["source"][1]).encode("ascii")
        not in raw,
        "never call the historical pushed V53 graph the current V54 graph")
    lower = raw.lower()
    for word in (
        b'height="2250"', b"building a faster python re",
        b"rust test runner failed before matching", b"928 differences",
        b"8,965 explicitly verified", b"13 real workers",
        b"31,237", b"4.2m unopened", b"not measured",
        b"new workers: 0", b"matching: not run",
        b"184 / 189", b"186 / 191", b"181 / 186", b"183 / 188",
        b"signature checks", b"public-interface observations",
        b"large-input observations", b"17 pass", b"7 fail",
        b"22 pass", b"3 not run", b"2,147,483,648",
        b"1,087", b"1,036", b"1,262", b"1,230", b"2,172", b"1,764",
        b"not generated", b"not opened",
        b"not opened by this graph", b"independent failure observation",
    ):
        base.need(word in lower, "preserve visible actual failure truth: "
                  + repr(word))
    for falsehood in (
        b"v8 matching passed", b"v8 matching failed",
        b"v8 semantic mismatches", b"corrected candidate passed",
        b"qualified rust replacement", b"controller succeeded",
        b"zero build archive reads by controller",
        b"no build archive was read", b"28 unique compiler pids",
        b"phase vector in receipt", b"native binary digest in receipt",
        b"winner selected", b"holdout opened", b"faster than python",
        b"archive inflated by this graph", b"32 repaired",
    ):
        base.need(falsehood not in lower,
                  "reject invented matching or erased archive effect: "
                  + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish compact truthful V54 graph with one exact linefeed")
    return raw


def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact independent V54 graph source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound actual independently owned V54 graph source")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                 private=True)
    old, inputs, old_svg = authenticate_v53(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V53},
    )
    proof = authenticate_failure(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v53_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V53.items()}
    inputs = copy.deepcopy(inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 54,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessor,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(modules, snapshot, old_svg, source_sha,
                   base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "keep baseline Python and exactly six first-party families")
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 186,
            "authenticated_history_reference_lower_bound": 191,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "actual_v8_entry_failure": copy.deepcopy(proof),
                "actual_v8_controller_status": "FAIL",
                "actual_v8_failure_stage":
                    "BUILD-PROCESS PREFLIGHT; NO MATCHING",
                "actual_v8_matching_status": "NOT RUN",
                "actual_v8_semantic_mismatch_count": "NOT MEASURED",
                "actual_v8_verified_passing_case_count": "NOT MEASURED",
                "actual_v8_candidate_correctness": "NOT MEASURED",
                "actual_v8_candidate_workers": 0,
                "actual_v8_native_activations": 0,
                "actual_v8_controller_build_archive_reads": 1,
                "actual_v8_controller_build_archive_inflations": 1,
                "actual_v8_build_archive_read_by_graph": False,
                "actual_v8_candidate_qualified": False,
                "actual_v16_build_status": "PASS",
                "actual_v16_compiler_process_count": 28,
                "actual_v16_unique_pid_vector_in_receipt": False,
                "actual_v16_phase_vector_in_receipt": False,
                "actual_v16_native_hashes_in_receipt": False,
                "current_original_campaign_semantic_mismatch_count": 928,
                "current_original_campaign_verified_passing_case_count": 8965,
                "current_original_campaign_candidate_worker_count": 13,
                "actual_candidate_workers": 13,
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 54,
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
              "bound all genuine actual-controller graph outputs")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_failure() -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v8-entry-failure",
        "status": "FAIL",
        "family": "rust",
        "error_type": "CampaignError",
        "error_message": ERROR_MESSAGE,
        "traceback": "synthetic controller traceback: " + ERROR_MESSAGE,
        "actual_operation_mode": "AUTHORIZED RUN",
        "source_only_zero_effects_claimed": False,
        "actual_effects": {
            **failure_effects(),
            "canonical_target_reads": "NOT MEASURED",
            "canonical_target_stats": "NOT MEASURED",
        },
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def synthetic_observation() -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v8-"
                  "entry-failure-observation-v1",
        "version": 1,
        "status": "PASS",
        "observation_pass_means":
            "DURABLE OBSERVATION OF A FAILED CANDIDATE CONTROLLER; "
            "NOT A PASSING CANDIDATE",
        "observed_operation": "ONE AUTHORIZED RUST V8 ORIGINAL-CAMPAIGN RUN",
        "actual_pushed_runner_head": PUSHED_HEAD,
        "authenticated_evidence_owner_lower_bound_before_publication": 184,
        "authenticated_history_reference_lower_bound_before_publication": 189,
        "new_actual_observation_owner_count": 2,
        "resulting_authenticated_evidence_owner_lower_bound": 186,
        "resulting_authenticated_history_reference_lower_bound": 191,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "actual_timing_trials": 0,
        "winner_selected": False,
        "observed_failure": {
            "schema":
                "rebar-owned-repaired-rust-original-campaign-v8-entry-failure",
            "status": "FAIL",
            "error_type": "CampaignError",
            "error_message": ERROR_MESSAGE,
            "failure_category":
                "AUTHENTIC BUILD-PROCESS SHAPE REJECTED BEFORE CANDIDATE "
                "ACTIVATION",
            "candidate_matching": "NOT RUN",
            "full_original_case_denominator": 31237,
            "original_suite_count": 13,
            "started_suite_count": 0,
            "completed_suite_count": 0,
            "actual_candidate_workers": 0,
            "actual_native_activations": 0,
            "semantic_mismatch_count": "NOT MEASURED",
            "verified_passing_case_count": "NOT MEASURED",
            "candidate_qualified": False,
        },
        "exact_recorded_controller_stdout": {
            "path": FAILURE[0], "sha256": FAILURE[1], "bytes": FAILURE[2],
            "device": DEVICE, "inode": FAILURE_INODE,
            "mode": "600", "nlink": 1,
            "lossless_original_controller_json": True,
        },
        "actual_build_archive_effects": {
            "compressed_build_archive_sha256": BUILD_ARCHIVE_SHA,
            "actual_archive_read_count": 1,
            "actual_archive_inflation_count": 1,
            "compressed_bytes_read": 109671,
            "uncompressed_bytes_read": 765382,
            "uncompressed_sha256": UNCOMPRESSED_ARCHIVE_SHA,
        },
        "actual_target_effects": {
            "canonical_target_replacements": 0,
            "recovery_roots_created": 0,
            "recovery_journals_created": 0,
            "activated_target_roles": [],
            "restored_target_roles": [],
            "all_four_original_targets_unchanged_without_recovery": True,
            "all_four_original_targets_restored_by_a_recovery": False,
            "original_targets": [
                {"synthetic_role": "bridge-source"},
                {"synthetic_role": "adapter"},
                {"synthetic_role": "engine"},
                {"synthetic_role": "bridge"},
            ],
        },
        "historical_actual_candidate_matching": {
            "status": "FAIL", "semantic_mismatch_count": 928,
            "verified_passing_case_count": 8965,
            "completed_suite_count": 13,
            "distinct_worker_process_id_count": 13,
        },
        "frozen_runner": {
            "source": {"sha256": RUNNER_SOURCE, "bytes": 164002},
            "protocol": {"sha256": RUNNER_PROTOCOL, "bytes": 10563},
            "contract": {"sha256": RUNNER_CONTRACT, "bytes": 13749},
        },
        "root_cause": {
            "validator_function": "validate_build_report",
            "authoritative_build_function": "verify_reproduced_phases",
            "withdrawn_oracle_cases": 0,
            "new_private_waivers": 0,
            "required_future_fix": "derive the authenticated ordered phase",
        },
    }


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_failure_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged actual V8 failure: " + description)


def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 2797
        and prior.get("actual_rust_v16_build_status") == "PASS"
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and prior.get("rust_original_campaign_v8_matching_status") == "NOT RUN"
        and prior.get("authenticated_evidence_owner_lower_bound") == 184
        and prior.get("authenticated_history_reference_lower_bound") == 189,
        "preserve all 2,797 actually pushed V53 synthetic controls")
    v43 = prior_modules[9]
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = make_failure_proof(
            base, base.synthetic_owner(FAILURE, FAILURE_INODE),
            synthetic_failure(),
            base.synthetic_owner(OBSERVATION, OBSERVATION_INODE),
            synthetic_observation(),
        )
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for role in ("failure", "observation"):
            for key, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][key] = v43.forged_value(base, value)
                rejected += reject_control(
                    base, hostile, "owner:" + role + ":" + key)
        for key, value in proof["complete_actual_failure"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_actual_failure"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "failure:" + key)
        for key, value in (
                proof["complete_actual_failure"]["actual_effects"].items()):
            hostile = copy.deepcopy(proof)
            hostile["complete_actual_failure"]["actual_effects"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "actual-effect:" + key)
        for key, value in proof["complete_independent_observation"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_independent_observation"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "observation:" + key)
        for section in (
                "observed_failure", "exact_recorded_controller_stdout",
                "actual_build_archive_effects", "actual_target_effects",
                "historical_actual_candidate_matching", "frozen_runner",
                "root_cause"):
            nested = proof["complete_independent_observation"][section]
            for key, value in nested.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_observation"][section][key] = (
                    v43.forged_value(base, value))
                rejected += reject_control(
                    base, hostile, "observation:" + section + ":" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v54")),
            ("filesystem", lambda: os.open("forbidden-v54", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v54")),
            ("write", lambda: os.mkdir("forbidden-v54")),
            ("process", lambda: subprocess.run(("forbidden-v54",))),
            ("process", lambda: subprocess.Popen(("forbidden-v54",))),
            ("process", lambda: os.execv("/forbidden-v54", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically forbid an actual V54 graph " + kind)
            else:
                raise base.GraphError("forbidden actual V54 effect escaped")
        base.need(rejected >= 175,
                  "reject every false outcome and erased real archive effect")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 54,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v53_hostile_controls": 2797,
            "new_v54_hostile_controls": rejected,
            "rejected_hostile_control_count": 2797 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_owners_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_receipts_read_by_self_test": 0,
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
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_current_graph_predecessor_version": 53,
            "actual_rust_v16_build_status": "PASS",
            "actual_rust_v16_compiler_process_count": 28,
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v8_controller_status": "FAIL",
            "actual_rust_v8_matching_status": "NOT RUN",
            "actual_rust_v8_semantic_mismatch_count": "NOT MEASURED",
            "actual_rust_v8_candidate_workers": 0,
            "actual_rust_v8_native_activations": 0,
            "actual_rust_v8_build_archive_reads_by_controller": 1,
            "actual_rust_v8_build_archive_inflations_by_controller": 1,
            "actual_rust_v8_build_archive_read_by_graph": False,
            "actual_rust_v8_build_archive_inflated_by_graph": False,
            "actual_rust_v8_historical_contract_evidence_lower_bound": 181,
            "actual_rust_v8_historical_contract_history_lower_bound": 186,
            "actual_rust_v8_historical_contract_resulting_evidence_lower_bound":
                183,
            "actual_rust_v8_historical_contract_resulting_history_lower_bound":
                188,
            "authenticated_evidence_owner_lower_bound": 186,
            "authenticated_history_reference_lower_bound": 191,
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
            "frozen_corrected_runner_source_family_count": 3,
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
              "publish only the three authorized actual V54 graph outputs")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact authorized V54 graph byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid() and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish one private complete independently owned V54 asset")
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
    base.need(confirmed == raw, "re-authenticate complete V54 graph output")


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 54,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 53,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V53.items()},
        "actual_rust_v16_build_status":
            snapshot["actual_rust_v16_build_status"],
        "actual_rust_v7_semantic_status":
            snapshot["actual_rust_v7_semantic_status"],
        "actual_rust_v7_semantic_mismatch_count":
            snapshot["actual_rust_v7_semantic_mismatch_count"],
        "actual_rust_v7_explicitly_verified_passing_case_count":
            snapshot["actual_rust_v7_explicitly_verified_passing_case_count"],
        "actual_rust_v8_controller_status":
            snapshot["actual_rust_v8_controller_status"],
        "actual_rust_v8_matching_status":
            snapshot["actual_rust_v8_matching_status"],
        "actual_rust_v8_semantic_mismatch_count":
            snapshot["actual_rust_v8_semantic_mismatch_count"],
        "actual_rust_v8_candidate_workers":
            snapshot["actual_rust_v8_candidate_workers"],
        "actual_rust_v8_build_archive_reads_by_controller":
            snapshot["actual_rust_v8_build_archive_reads_by_controller"],
        "actual_rust_v8_build_archive_inflations_by_controller":
            snapshot["actual_rust_v8_build_archive_inflations_by_controller"],
        "actual_rust_v8_build_archive_read_by_graph":
            snapshot["actual_rust_v8_build_archive_read_by_graph"],
        "authenticated_evidence_owner_lower_bound":
            snapshot["authenticated_evidence_owner_lower_bound"],
        "authenticated_history_reference_lower_bound":
            snapshot["authenticated_history_reference_lower_bound"],
        "first_party_source_inventory_family_count":
            snapshot["first_party_source_inventory_family_count"],
        "actually_tested_corrected_candidate_families":
            snapshot["actually_tested_corrected_candidate_families"],
        "actually_runnable_candidate_family_count":
            snapshot["actually_runnable_candidate_family_count"],
        "qualified_candidate_count": snapshot["qualified_candidate_count"],
        "final_comparison_planned_case_count":
            snapshot["final_comparison_planned_case_count"],
        "final_comparison_cases_generated":
            snapshot["final_comparison_cases_generated"],
        "final_holdout_opened": snapshot["final_holdout_opened"],
        "performance": snapshot["performance"],
        "memory": snapshot["memory"],
        "confidence_intervals": snapshot["confidence_intervals"],
        "undefined_behavior": snapshot["undefined_behavior"],
        "winner_selected": snapshot["winner_selected"],
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
    for role in V53:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in ("failure", "observation"):
        parser.add_argument("--" + role + "-sha256")
        parser.add_argument("--" + role + "-bytes", type=int)
        parser.add_argument("--" + role + "-inode", type=int)
        parser.add_argument("--" + role + "-device", type=int)
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v53()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256" for role in V53)
            for role in ("failure", "observation"):
                forbidden.extend(role + "_" + field
                                 for field in ("sha256", "bytes", "inode",
                                               "device"))
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(all(getattr(options, name) is None
                          for name in forbidden),
                      "source-only graph never receives actual outcome pins")
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256,
                                  "actual complete V54 graph source")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render only the three root-authorized V54 assets")
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published")
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "actual exact V54 graph inputs"),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "actual exact V54 graph summary"),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "actual exact V54 graph chart"),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True)
                base.need(raw == outputs[path],
                          "reproduce one actual V54 graph asset: " + path)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context")
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V54 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V54 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
