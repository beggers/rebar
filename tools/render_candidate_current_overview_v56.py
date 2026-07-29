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
SELF = "tools/render_candidate_current_overview_v56.py"
OUTPUT = "docs/evidence/candidate-current-overview-v56"
SCHEMA = "rebar-candidate-current-overview-v56"
V55 = {
    "source": ("tools/render_candidate_current_overview_v55.py",
               "75b0a1d1530aa99d914e2730ff99510bd7820716bb6c8d7d8376c03753625da8",
               69062),
    "inputs": ("docs/evidence/candidate-current-overview-v55.inputs.json",
               "845cebe4110369ff5b25165eb3b3b6e1df5ce507b9536f1c278b419a7daa8e8b",
               648992),
    "summary": ("docs/evidence/candidate-current-overview-v55.json",
                "14d4408e8791d212cf4976f4e4083674d1dc9563367a0cef829c6c8ca961b508",
                1794857),
    "svg": ("docs/evidence/candidate-current-overview-v55.svg",
            "43098acf7bb5240271d9bcec627f92bf80ebb2a7701d16221f8c419f342369f8",
            13997),
}


FAILURE = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v9-rust-phase2-v16-rust-buffer-"
    "shape-pickle-original-p0-entry-failure.json",
    "70b9089b16faa499da3688d466d0355b87ca42d0382c9da59e08f063a7990471",
    8075,
)


OBSERVATION = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v9-rust-phase2-v16-rust-buffer-"
    "shape-pickle-original-p0-entry-failure-observation.json",
    "687d401e1112218de26e5dd0525e8c60cb79b5f4b204272cd8c91b83182eb3f6",
    15992,
)


DEVICE = 2064
FAILURE_INODE = 525025
OBSERVATION_INODE = 525026
RUNNER_SOURCE = "629f6d361e2e3cd2eeb762223076d5511707d52241189fc4bd4c73045bb9287c"
RUNNER_PROTOCOL = "9dfec149359a2088e384da1b3b5851fc8ac0c5f6ed8bfdb1414671a7ecbf6850"
RUNNER_CONTRACT = "782576f45cbc7bc97775233051d82889778f095a4595e336ec4afb5f2ffc3a82"
BUILD_ARCHIVE_SHA = "c24c0e1544003b231bac3e45601faabfd1c1e5c181d89fce7d660a2df4a29270"
UNCOMPRESSED_ARCHIVE_SHA = "c89af182cdb8e98dc05a4538e620c1db8404fbd7a11a3d43fea54f9da609f9c5"
ERROR_MESSAGE = "never publish without a prepared and fully restored journal"
INNER_ERROR_MESSAGE = "accept only one exact owner-only Rust campaign root"
RETAINED_V9_SUITE_CASES = (
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
PUSHED_HEAD = "5f79b6c337c5644112e80875ecd448f13660dd84"
RECOVERY_ROOT = ("/tmp/rebar-phase2-repaired-rust-original-campaign-v9-"
                 "phase2-v16-rust-buffer-shape-pickle-original-p0")
RECOVERY_ROOT_DEVICE = 2049
RECOVERY_ROOT_INODE = 11673090
PUBLIC_COUNTS = {"PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
                 "NOT ESTABLISHED": 1, "NOT OPENED": 1}
LARGE_COUNTS = {"PASS": 22, "FAIL": 1, "NOT RUN": 3,
                "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1}
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]


def load_v55() -> tuple:
    path, fingerprint, size = V55["source"]
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
            raise ValueError("reject substituted pushed V55 graph renderer")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated pushed V55 graph renderer")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended pushed V55 graph renderer")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed pushed V55 graph renderer")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_actual_pushed_source_graph_v55")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v54()
    base = prior_modules[-1]
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v55"
              and previous.SELF == path
              and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
              and previous.LARGE_COUNTS == LARGE_COUNTS,
              "authenticate only the exact actually pushed V55 graph source")
    return previous, prior_modules, base


def failure_effects() -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v9-"
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
        "activated_target_roles": [],
        "canonical_target_replacements": 0,
        "recovery_journals_created": 0,
        "recovery_roots_created": 1,
        "recovery_locks_acquired": 0,
        "recovery_journal_announced": False,
        "recovery_journal_creation_attempted": False,
        "recovery_root_creation_attempted": True,
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
        "schema": "rebar-owned-repaired-rust-original-campaign-v9-entry-failure",
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
                  "reject forged actual V9 entry failure: " + key)
    actual = failure.get("actual_effects")
    base.need(type(actual) is dict,
              "preserve the complete real archive-read effect ledger")
    assert isinstance(actual, dict)
    for key, value in failure_effects().items():
        base.need(type(actual.get(key)) is type(value)
                  and actual[key] == value,
                  "reject hidden actual controller effect: " + key)
    expected_placeholders = [
        {
            "suite": suite,
            "case_execution_denominator": case_count,
            "worker_attempted": True,
            "actual_worker_started": False,
            "fully_observed": False,
            "process": None,
            "error_message": INNER_ERROR_MESSAGE,
            "failure_class": "INFRASTRUCTURE FAILURE",
            "mismatch_count": "NOT MEASURED",
            "verified_passing_case_count": 0,
        }
        for suite, case_count in RETAINED_V9_SUITE_CASES
    ]
    base.need(
        sum(case_count for _, case_count in RETAINED_V9_SUITE_CASES) == 31237
        and actual.get("retained_suite_results") == expected_placeholders
        and actual.get("attempted_suite_count") == 0
        and actual.get("started_suite_count") == 0
        and actual.get("fully_observed_suite_count") == 0
        and actual.get("actual_candidate_workers") == 0
        and actual.get("worker_attempts") == [],
        "preserve the original inner error in thirteen synthetic attempted "
        "rows without claiming any launched or observed candidate worker",
    )
    base.need(actual.get("canonical_target_reads") == "NOT MEASURED"
              and actual.get("canonical_target_stats") == "NOT MEASURED",
              "never invent exact canonical target read or stat counts")
    base.need(type(failure.get("traceback")) is str
              and ERROR_MESSAGE in failure["traceback"],
              "preserve complete real outer controller failure traceback")

def validate_observation(base: types.ModuleType,
                         observation: object) -> None:
    base.need(type(observation) is dict,
              "reject missing independent actual controller observation")
    assert isinstance(observation, dict)
    expected = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v9-"
                  "entry-failure-observation-v1",
        "version": 1,
        "status": "PASS",
        "observation_pass_means":
            "DURABLE INDEPENDENT OBSERVATION OF A FAILED CANDIDATE "
            "CONTROLLER; NOT A PASSING CANDIDATE",
        "observed_operation": "ONE AUTHORIZED RUST V9 ORIGINAL-CAMPAIGN RUN",
        "actual_pushed_runner_head": PUSHED_HEAD,
        "authenticated_evidence_owner_lower_bound_before_publication": 189,
        "authenticated_history_reference_lower_bound_before_publication": 194,
        "new_actual_observation_owner_count": 2,
        "resulting_authenticated_evidence_owner_lower_bound": 191,
        "resulting_authenticated_history_reference_lower_bound": 196,
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
                  "reject invented V9 controller observation: " + key)
    observed = observation.get("observed_failure")
    expected_observed = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v9-entry-failure",
        "status": "FAIL",
        "actual_operation_mode": "AUTHORIZED RUN",
        "error_type": "CampaignError",
        "error_message": ERROR_MESSAGE,
        "source_line": 3111,
        "failure_category":
            "OWNER-ONLY RECOVERY ROOT CREATED; INCOMPATIBLE HISTORICAL "
            "HELPER PREFIX REJECTS ROOT BEFORE LOCK OR ACTIVATION",
        "candidate_matching": "NOT RUN",
        "full_original_case_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "additional_private_waiver_count": 0,
        "attempted_suite_count": 0,
        "started_suite_count": 0,
        "completed_suite_count": 0,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "candidate_qualified": False,
    }
    base.need(observed == expected_observed,
              "distinguish V9 root-prefix failure from semantic matching")
    retained = observation.get("actual_failed_suite_placeholders")
    expected_retained = {
        "provenance":
            "ALL 13 RETAINED ROWS FROM THE AUTHENTICATED ACTUAL CONTROLLER "
            "FAILURE; NO ROW REPRESENTS A STARTED OR OBSERVED CANDIDATE WORKER",
        "retained_suite_count": 13,
        "case_execution_denominator": 31237,
        "shared_inner_error_message": INNER_ERROR_MESSAGE,
        "all_rows_are_synthetic_infrastructure_placeholders": True,
        "placeholder_worker_attempted_means_a_real_worker_was_attempted": False,
        "placeholder_verified_passing_count_is_a_real_observed_pass_count":
            False,
        "actual_ledger_attempted_suite_count": 0,
        "actual_ledger_started_suite_count": 0,
        "actual_ledger_fully_observed_suite_count": 0,
        "actual_ledger_candidate_workers": 0,
        "actual_ledger_worker_attempts": [],
        "actual_ledger_worker_process_ids": [],
        "rows": [
            {
                "suite": suite,
                "case_execution_denominator": case_count,
                "error_message": INNER_ERROR_MESSAGE,
                "failure_class": "INFRASTRUCTURE FAILURE",
                "worker_attempted": True,
                "actual_worker_started": False,
                "fully_observed": False,
                "process": None,
                "mismatch_count": "NOT MEASURED",
                "verified_passing_case_count": 0,
            }
            for suite, case_count in RETAINED_V9_SUITE_CASES
        ],
    }
    base.need(
        retained == expected_retained,
        "cross-authenticate all thirteen retained inner-error rows without "
        "mistaking synthetic worker-attempt flags for real workers",
    )
    recorded = observation.get("exact_recorded_controller_stdout")
    expected_recorded = {
        "path": FAILURE[0], "sha256": FAILURE[1], "bytes": FAILURE[2],
        "device": DEVICE, "inode": FAILURE_INODE, "mode": "0600",
        "nlink": 1,
        "schema": "rebar-owned-repaired-rust-original-campaign-v9-entry-failure",
        "status": "FAIL", "source_only_zero_effects_claimed": False,
    }
    base.need(recorded == expected_recorded,
              "bind authentic failed V9 stdout to its actual private inode")
    archive = observation.get("actual_build_archive_effects")
    expected_archive = {
        "compressed_build_archive_sha256": BUILD_ARCHIVE_SHA,
        "actual_archive_read_count": 1,
        "actual_archive_inflation_count": 1,
        "compressed_bytes_read": 109671,
        "uncompressed_bytes_read": 765382,
        "uncompressed_sha256": UNCOMPRESSED_ARCHIVE_SHA,
        "archive_read_by_independent_observer": False,
    }
    base.need(archive == expected_archive,
              "report one actual controller archive read without opening it")
    targets = observation.get("actual_target_effects")
    base.need(type(targets) is dict,
              "retain independently attested actual V9 target effects")
    assert isinstance(targets, dict)
    expected_target_values = {
        "canonical_target_replacements": 0,
        "actual_native_activations": 0,
        "activated_target_roles": [],
        "recovery_root_creation_attempted": True,
        "recovery_roots_created": 1,
        "recovery_lock_attempted": False,
        "recovery_locks_acquired": 0,
        "recovery_journal_creation_attempted": False,
        "recovery_journals_created": 0,
        "recovery_journal_announced": False,
        "restoration_attempted": False,
        "restored_target_roles": [],
        "all_four_original_targets_unchanged_without_recovery": True,
        "all_four_original_targets_restored_by_a_recovery": False,
        "all_four_original_targets_restored": False,
        "original_target_identity_provenance":
            "INDEPENDENTLY ATTESTED BY ROOT BEFORE AND AFTER THE RUN; "
            "OBSERVER DID NOT ACCESS THE CANDIDATE TARGETS",
    }
    for key, value in expected_target_values.items():
        base.need(type(targets.get(key)) is type(value)
                  and targets[key] == value,
                  "reject erased real V9 root or invented recovery: " + key)
    expected_root = {
        "path": RECOVERY_ROOT,
        "device": RECOVERY_ROOT_DEVICE,
        "inode": RECOVERY_ROOT_INODE,
        "mode": "0700",
        "directory_is_empty": True,
        "directory_identity_provenance":
            "INDEPENDENTLY ATTESTED BY ROOT; OBSERVER DID NOT OPEN, "
            "ENUMERATE, OR MODIFY THE DIRECTORY",
    }
    base.need(targets.get("recovery_root") == expected_root,
              "report root-attested empty V9 recovery root without opening it")
    original_targets = targets.get("original_targets")
    base.need(type(original_targets) is list and len(original_targets) == 4
              and all(type(item) is dict for item in original_targets),
              "preserve four unchanged independently attested original targets")
    historical = observation.get("historical_actual_candidate_matching")
    base.need(
        historical == {
            "status": "FAIL",
            "semantic_mismatch_count": 928,
            "verified_passing_case_count": 8965,
            "completed_suite_count": 13,
            "distinct_worker_process_id_count": 13,
            "passing_cases_derived_by_subtraction": False,
        },
        "preserve actual V7 matching separately from zero V9 workers",
    )
    frozen = observation.get("frozen_runner")
    expected_frozen = {
        "source": {"path": "tools/run_owned_repaired_rust_original_campaign_v9.py",
                   "sha256": RUNNER_SOURCE, "bytes": 173643},
        "protocol": {"path": "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V9.md",
                     "sha256": RUNNER_PROTOCOL, "bytes": 12690},
        "contract": {"path": "oracle/phase2/repaired-rust-original-campaign-v9.json",
                     "sha256": RUNNER_CONTRACT, "bytes": 15235},
    }
    base.need(frozen == expected_frozen,
              "bind exact actually executed independently frozen V9 runner")
    cause = observation.get("root_cause")
    expected_cause = {
        "summary":
            "The V9 campaign reuses the frozen V7 recovery helper without "
            "rebinding the frozen V2 helper's version-2-only private-directory "
            "prefix to the real version-9 recovery root.",
        "verified_source_cause":
            "V7 open_recovery_lock creates and counts the exact V9 root, "
            "then calls V2 private_directory before setting "
            "recovery_lock_attempted. V2 checked_private_root accepts "
            "only the incompatible "
            "rebar-phase2-repaired-rust-original-campaign-v2- prefix. "
            "V9 configures the historical V2 label and roles but never "
            "rebinds PRIVATE_PREFIX. The caller-provided V9 root "
            "therefore cannot pass the V2 directory check.",
        "historical_v2_source": {
            "path": "tools/run_owned_repaired_rust_original_campaign_v2.py",
            "sha256": "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3",
            "private_prefix_line": 55,
            "private_prefix": "rebar-phase2-repaired-rust-original-campaign-v2-",
            "root_validator_line": 1371,
        },
        "historical_v7_source": {
            "path": "tools/run_owned_repaired_rust_original_campaign_v7.py",
            "sha256": "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
            "recovery_lock_function_line": 7762,
        },
        "v9_historical_helper_configuration_line": 2334,
        "v9_final_masking_requirement_line": 3111,
        "verified_effect_sequence": [
            "ONE COMPLETE V16 BUILD ARCHIVE READ AND GZIP INFLATION",
            "GENUINE V16 PRIVATE BUILD AND FIRST-PARTY NATIVE "
            "PROVENANCE AUTHENTICATED",
            "HISTORICAL V2 HELPER SOURCE AND MODULE PREFLIGHT PASS",
            "EXACTLY ONE OWNER-ONLY V9 RECOVERY ROOT CREATED",
            "V2 VERSION-2-ONLY ROOT VALIDATOR REACHED BEFORE ANY LOCK ATTEMPT",
            "NO LOCK, NO JOURNAL, NO ACTIVATION, NO WORKER, "
            "NO TARGET REPLACEMENT",
            "FINAL PREPARED-AND-RESTORED-JOURNAL REQUIREMENT "
            "MASKS THE INNER TRACEBACK; ALL 13 SYNTHETIC FAILURE "
            "ROWS PRESERVE THE INNER ERROR MESSAGE",
        ],
        "original_inner_exception": INNER_ERROR_MESSAGE,
        "original_inner_exception_provenance":
            "IDENTICALLY RECORDED IN EACH OF THE 13 AUTHENTICATED "
            "SYNTHETIC RETAINED-SUITE ROWS; NONE REPRESENTS AN "
            "EXECUTED WORKER",
        "original_inner_traceback":
            "MASKED BY THE FINAL PREPARED-JOURNAL REQUIREMENT; NOT INVENTED",
        "outer_exception": ERROR_MESSAGE,
        "required_future_fix":
            "Freeze a new append-only campaign version that rebinds the "
            "historical V2 helper's private prefix before private_directory, "
            "verifies the exact caller-pinned owner-only versioned root, "
            "covers real helper prefix acceptance and rejection in "
            "source-only controls, and retains original-inode recovery "
            "and all complete original CPython cases.",
        "withdrawn_oracle_cases": 0,
        "new_private_waivers": 0,
    }
    base.need(cause == expected_cause,
              "preserve actual incompatible-prefix cause and complete oracle")

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
        "schema": SCHEMA + "-authenticated-actual-v9-pre-matching-failure",
        "failure": copy.deepcopy(failure_owner),
        "complete_actual_failure": copy.deepcopy(failure),
        "observation": copy.deepcopy(observation_owner),
        "complete_independent_observation": copy.deepcopy(observation),
        "controller_status": "FAIL",
        "controller_failure_stage": "RECOVERY-ROOT PREFLIGHT; NO MATCHING",
        "error_message": ERROR_MESSAGE,
        "observation_status": "PASS",
        "observation_pass_means":
            "DURABLE INDEPENDENT OBSERVATION OF A FAILED CANDIDATE "
            "CONTROLLER; "
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
        "synthetic_failed_worker_placeholder_count": 13,
        "recorded_original_inner_exception": INNER_ERROR_MESSAGE,
        "recorded_original_inner_exception_placeholder_count": 13,
        "synthetic_placeholder_worker_attempted_flags_are_real_attempts": False,
        "synthetic_placeholder_actual_worker_started_count": 0,
        "synthetic_placeholders_are_observed_workers": False,
        "actual_fully_observed_suite_count": 0,
        "actual_recovery_roots_created": 1,
        "retained_recovery_root": RECOVERY_ROOT,
        "retained_recovery_root_device": RECOVERY_ROOT_DEVICE,
        "retained_recovery_root_inode": RECOVERY_ROOT_INODE,
        "all_four_original_targets_unchanged": True,
        "all_four_original_targets_restored_by_recovery": False,
        "actual_build_archive_reads_by_controller": 1,
        "actual_build_archive_inflations_by_controller": 1,
        "actual_build_archive_compressed_bytes_read": 109671,
        "actual_build_archive_uncompressed_bytes_read": 765382,
        "build_archive_read_by_graph": False,
        "build_archive_inflated_by_graph": False,
        "build_archive_sha256_recomputed_by_graph": False,
        "failure_archive_read_by_graph": False,
        "reference_archive_read_by_graph": False,
        "actual_graph_predecessor_version": 55,
        "historical_source_contract_graph_version": 54,
        "historical_source_contract_evidence_lower_bound": 186,
        "historical_source_contract_history_lower_bound": 191,
        "historical_source_contract_resulting_evidence_lower_bound": 188,
        "historical_source_contract_resulting_history_lower_bound": 193,
        "actual_current_prepublication_evidence_lower_bound": 189,
        "actual_current_prepublication_history_lower_bound": 194,
        "new_exact_actual_plaintext_owner_count": 2,
        "actual_current_evidence_lower_bound_after_publication": 191,
        "actual_current_history_lower_bound_after_publication": 196,
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
    base.need(type(proof) is dict, "reject omitted actual V9 entry failure")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-actual-v9-pre-matching-failure",
        "controller_status": "FAIL",
        "controller_failure_stage": "RECOVERY-ROOT PREFLIGHT; NO MATCHING",
        "error_message": ERROR_MESSAGE,
        "observation_status": "PASS",
        "observation_pass_means":
            "DURABLE INDEPENDENT OBSERVATION OF A FAILED CANDIDATE "
            "CONTROLLER; "
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
        "synthetic_failed_worker_placeholder_count": 13,
        "recorded_original_inner_exception": INNER_ERROR_MESSAGE,
        "recorded_original_inner_exception_placeholder_count": 13,
        "synthetic_placeholder_worker_attempted_flags_are_real_attempts": False,
        "synthetic_placeholder_actual_worker_started_count": 0,
        "synthetic_placeholders_are_observed_workers": False,
        "actual_fully_observed_suite_count": 0,
        "actual_recovery_roots_created": 1,
        "retained_recovery_root": RECOVERY_ROOT,
        "retained_recovery_root_device": RECOVERY_ROOT_DEVICE,
        "retained_recovery_root_inode": RECOVERY_ROOT_INODE,
        "all_four_original_targets_unchanged": True,
        "all_four_original_targets_restored_by_recovery": False,
        "actual_build_archive_reads_by_controller": 1,
        "actual_build_archive_inflations_by_controller": 1,
        "actual_build_archive_compressed_bytes_read": 109671,
        "actual_build_archive_uncompressed_bytes_read": 765382,
        "build_archive_read_by_graph": False,
        "build_archive_inflated_by_graph": False,
        "build_archive_sha256_recomputed_by_graph": False,
        "failure_archive_read_by_graph": False,
        "reference_archive_read_by_graph": False,
        "actual_graph_predecessor_version": 55,
        "historical_source_contract_graph_version": 54,
        "historical_source_contract_evidence_lower_bound": 186,
        "historical_source_contract_history_lower_bound": 191,
        "historical_source_contract_resulting_evidence_lower_bound": 188,
        "historical_source_contract_resulting_history_lower_bound": 193,
        "actual_current_prepublication_evidence_lower_bound": 189,
        "actual_current_prepublication_history_lower_bound": 194,
        "new_exact_actual_plaintext_owner_count": 2,
        "actual_current_evidence_lower_bound_after_publication": 191,
        "actual_current_history_lower_bound_after_publication": 196,
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
                         "actual V9 " + role) == item[1]
            and getattr(options, role + "_bytes") == item[2]
            and getattr(options, role + "_inode") == inode
            and getattr(options, role + "_device") == DEVICE,
            "pin exact independently released plaintext V9 " + role,
        )
    failure_raw, failure_owner = base.read_owner(*FAILURE, private=True)
    observation_raw, observation_owner = base.read_owner(
        *OBSERVATION, private=True)
    return make_failure_proof(
        base, failure_owner,
        base.document(failure_raw, "lossless actual V9 controller stdout"),
        observation_owner,
        base.document(observation_raw,
                      "exact-hash-authenticated independent V9 observation",
                      exact=False),
    )


def v55_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V55["source"][1],
        source_bytes=V55["source"][2],
        previous_source_sha256=previous.V54["source"][1],
        previous_inputs_sha256=previous.V54["inputs"][1],
        previous_summary_sha256=previous.V54["summary"][1],
        previous_svg_sha256=previous.V54["svg"][1],
        runner_source_sha256=previous.V9["source"][1],
        runner_source_bytes=previous.V9["source"][2],
        runner_protocol_sha256=previous.V9["protocol"][1],
        runner_protocol_bytes=previous.V9["protocol"][2],
        runner_contract_sha256=previous.V9["contract"][1],
        runner_contract_bytes=previous.V9["contract"][2],
    )


def authenticate_v55(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V55.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V55 " + role)
            == item[1],
            "reject substituted actually pushed V55 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete actual pushed V55 summary")
    inputs = base.document(raw["inputs"], "complete actual pushed V55 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(
        prior_modules, v55_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v55-summary"
        and old.get("version") == 55
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V55["source"])
        and old.get("inputs") == base.pin(*V55["inputs"])
        and old.get("svg") == base.pin(*V55["svg"])
        and inputs.get("schema")
        == "rebar-candidate-current-overview-v55-inputs"
        and inputs.get("version") == 55
        and inputs.get("renderer") == base.pin(*V55["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V55["inputs"][0]]
        and raw["summary"] == expected[V55["summary"][0]]
        and raw["svg"] == expected[V55["svg"][0]]
        and old.get("authenticated_evidence_owner_lower_bound") == 189
        and old.get("authenticated_history_reference_lower_bound") == 194
        and old.get("actual_rust_v16_build_status") == "PASS"
        and old.get("actual_rust_v16_compiler_process_count") == 28
        and old.get("actual_rust_v8_controller_status") == "FAIL"
        and old.get("actual_rust_v8_matching_status") == "NOT RUN"
        and old.get("actual_rust_v8_semantic_mismatch_count") == "NOT MEASURED"
        and old.get("actual_rust_v8_candidate_workers") == 0
        and old.get("actual_rust_v8_build_archive_reads_by_controller") == 1
        and old.get("actual_rust_v8_build_archive_inflations_by_controller")
        == 1
        and old.get("rust_original_campaign_v9_source_freeze_status")
        == "SOURCE FROZEN; NOT RUN"
        and old.get("rust_original_campaign_v9_matching_status") == "NOT RUN"
        and old.get("actual_rust_v7_semantic_status") == "FAIL"
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("qualified_candidate_count") == 0
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce complete actual pushed V55 without opening any archive",
    )
    return old, inputs, raw["svg"]


def result_fields(proof: dict) -> dict:
    return {
        "actual_rust_v9_entry_failure": copy.deepcopy(proof),
        "actual_rust_v9_controller_status": "FAIL",
        "actual_rust_v9_controller_failure_stage":
            "RECOVERY-ROOT PREFLIGHT; NO MATCHING",
        "actual_rust_v9_controller_error": ERROR_MESSAGE,
        "actual_rust_v9_observation_status": "PASS",
        "actual_rust_v9_observation_pass_means":
            "DURABLE INDEPENDENT OBSERVATION OF A FAILED CANDIDATE "
            "CONTROLLER; "
            "NOT A PASSING CANDIDATE",
        "actual_rust_v9_failure_owner": copy.deepcopy(proof["failure"]),
        "actual_rust_v9_observation_owner":
            copy.deepcopy(proof["observation"]),
        "actual_rust_v9_failure_sha256": FAILURE[1],
        "actual_rust_v9_observation_sha256": OBSERVATION[1],
        "actual_rust_v9_matching_status": "NOT RUN",
        "actual_rust_v9_candidate_correctness": "NOT MEASURED",
        "actual_rust_v9_semantic_mismatch_count": "NOT MEASURED",
        "actual_rust_v9_verified_passing_case_count": "NOT MEASURED",
        "actual_rust_v9_candidate_qualified": False,
        "actual_rust_v9_candidate_workers": 0,
        "actual_rust_v9_started_suite_count": 0,
        "actual_rust_v9_attempted_suite_count": 0,
        "actual_rust_v9_completed_suite_count": 0,
        "actual_rust_v9_fully_observed_suite_count": 0,
        "actual_rust_v9_synthetic_failed_worker_placeholder_count": 13,
        "actual_rust_v9_recorded_original_inner_exception": INNER_ERROR_MESSAGE,
        "actual_rust_v9_recorded_original_inner_exception_placeholder_count": 13,
        "actual_rust_v9_placeholder_worker_flags_are_real_attempts": False,
        "actual_rust_v9_synthetic_placeholders_are_observed_workers": False,
        "actual_rust_v9_native_activations": 0,
        "actual_rust_v9_target_replacements": 0,
        "actual_rust_v9_recovery_journals_created": 0,
        "actual_rust_v9_recovery_roots_created": 1,
        "actual_rust_v9_recovery_locks_attempted": False,
        "actual_rust_v9_recovery_locks_acquired": 0,
        "actual_rust_v9_retained_recovery_root": RECOVERY_ROOT,
        "actual_rust_v9_retained_recovery_root_device": RECOVERY_ROOT_DEVICE,
        "actual_rust_v9_retained_recovery_root_inode": RECOVERY_ROOT_INODE,
        "actual_rust_v9_all_original_targets_unchanged": True,
        "actual_rust_v9_original_targets_restored_by_recovery": False,
        "actual_rust_v9_build_archive_reads_by_controller": 1,
        "actual_rust_v9_build_archive_inflations_by_controller": 1,
        "actual_rust_v9_build_archive_compressed_bytes_read": 109671,
        "actual_rust_v9_build_archive_uncompressed_bytes_read": 765382,
        "actual_rust_v9_build_archive_read_by_graph": False,
        "actual_rust_v9_build_archive_inflated_by_graph": False,
        "actual_rust_v9_build_archive_sha256_recomputed_by_graph": False,
        "actual_rust_v9_historical_contract_evidence_lower_bound": 186,
        "actual_rust_v9_historical_contract_history_lower_bound": 191,
        "actual_rust_v9_historical_contract_resulting_evidence_lower_bound":
            188,
        "actual_rust_v9_historical_contract_resulting_history_lower_bound":
            193,
        "actual_rust_v9_current_prepublication_evidence_lower_bound": 189,
        "actual_rust_v9_current_prepublication_history_lower_bound": 194,
        "actual_rust_v9_new_plaintext_outcome_owner_count": 2,
        "actual_current_graph_predecessor_version": 55,
        "authenticated_evidence_owner_lower_bound": 191,
        "authenticated_history_reference_lower_bound": 196,
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
    base.need(type(snapshot) is dict, "reject missing complete V56 snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("actual_rust_v9_entry_failure")
    validate_failure_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(snapshot.get(key) == value,
                  "reject invented actual V9 controller outcome: " + key)
    replaced = snapshot.get("preserved_v55_replaced_snapshot_fields")
    base.need(type(replaced) is dict,
              "preserve every replaced actual pushed V55 graph field")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v55_replaced_snapshot_fields", None)
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
        and snapshot.get("actual_rust_v8_controller_status") == "FAIL"
        and snapshot.get("actual_rust_v8_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v8_candidate_workers") == 0
        and snapshot.get("actual_rust_v8_build_archive_reads_by_controller")
        == 1
        and snapshot.get("actual_rust_v9_controller_status") == "FAIL"
        and snapshot.get("actual_rust_v9_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v9_semantic_mismatch_count")
        == "NOT MEASURED"
        and snapshot.get("actual_rust_v9_candidate_workers") == 0
        and snapshot.get("actual_rust_v9_attempted_suite_count") == 0
        and snapshot.get("actual_rust_v9_started_suite_count") == 0
        and snapshot.get("actual_rust_v9_completed_suite_count") == 0
        and snapshot.get("actual_rust_v9_fully_observed_suite_count") == 0
        and snapshot.get("actual_rust_v9_synthetic_failed_worker_placeholder_count")
        == 13
        and snapshot.get("actual_rust_v9_synthetic_placeholders_are_observed_workers")
        is False
        and snapshot.get("actual_rust_v9_recovery_roots_created") == 1
        and snapshot.get("actual_rust_v9_recovery_journals_created") == 0
        and snapshot.get("actual_rust_v9_recovery_locks_acquired") == 0
        and snapshot.get("actual_rust_v9_all_original_targets_unchanged")
        is True
        and snapshot.get("actual_rust_v9_original_targets_restored_by_recovery")
        is False
        and snapshot.get("actual_rust_v9_build_archive_reads_by_controller")
        == 1
        and snapshot.get("actual_rust_v9_build_archive_inflations_by_controller")
        == 1
        and snapshot.get("actual_rust_v9_build_archive_read_by_graph")
        is False
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("actually_tested_corrected_candidate_families")
        == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
        == 1
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 191
        and snapshot.get("authenticated_history_reference_lower_bound") == 196
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
        "preserve both real controller failures and synthetic-placeholder truth")


def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    v43 = prior_modules[1][1][9]
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact current V56 graph renderer")
    inputs_sha = base.checked(inputs_sha, "exact current V56 graph inputs")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v55-title", "v56-title")
    visible = visible.replace("v55-description", "v56-description")
    changes = (
        (
            "Rust test runner failed; corrected follow-up is frozen, "
            "not yet run</title>",
            "Rust test runner failed twice before matching; no "
            "replacement is ready</title>",
            "preserve both actual no-worker controller failures",
        ),
        (
            "The first-party V8 controller failed before activating any "
            "candidate. A corrected V9 full-suite runner is frozen but "
            "has not run.",
            "The V8 and corrected V9 test controllers both failed before "
            "starting any candidate. V9 left one empty recovery directory; "
            "it did not start a matching worker or restore targets.",
            "record V9 directory creation without inventing recovery",
        ),
        (
            "Three and only three independently authenticated V9 "
            "frozen-runner source owners raise actual current lower bounds "
            "from 186 and 191 to 189 and 194;",
            "Two and only two independently authenticated plaintext "
            "V9 controller-failure owners raise actual current lower "
            "bounds from 189 and 194 to 191 and 196;",
            "count only actual separate V9 failure and observation owners",
        ),
        (
            '<text x="65" y="398" class="heading">Rust test runner '
            'failed; corrected follow-up frozen, not run</text>',
            '<text x="65" y="398" class="heading">Rust test runner '
            'failed again before matching</text>',
            "report the actual corrected controller failure",
        ),
        (
            "The native build passed; V8 stopped before activation. "
            "The corrected V9 full-suite test is frozen, NOT RUN. "
            "New workers: 0.",
            "The native build passed. Both V8 and V9 stopped before "
            "matching. V9 left one empty recovery root. Real new "
            "workers: 0.",
            "distinguish two actual controller attempts and one root",
        ),
        (
            "Old test failed; V8 stopped; corrected V9 not run",
            "Old test failed; V8 and V9 both stopped before matching",
            "retain only the actual old 928-difference semantic test",
        ),
        (
            '<text x="64" y="1756" class="heading">Corrected '
            'full-suite test frozen; not yet run</text>',
            '<text x="64" y="1756" class="heading">Corrected V9 '
            'controller failed before matching</text>',
            "show real V9 pre-matching finalizer failure",
        ),
        (
            "Exactly three new frozen corrected-runner source files raise "
            "actual current lower bounds from 186 / 191 to 189 / 194.",
            "Exactly two new plaintext V9 failure records raise actual "
            "current lower bounds from 189 / 194 to 191 / 196.",
            "bind actual pushed V55 floor and exactly two new records",
        ),
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
        '<rect x="44" y="1858" width="1352" height="381" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact reproducible '
        'corrected-runner failure evidence</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V55 graph inputs SHA-256", V55["inputs"][1]),
        ("Historical V55 graph renderer SHA-256", V55["source"][1]),
        ("Historical V55 graph summary SHA-256", V55["summary"][1]),
        ("Historical V55 graph image SHA-256", V55["svg"][1]),
        ("Exact V9 failed-controller stdout SHA-256", FAILURE[1]),
        ("Independent V9 failure observation SHA-256", OBSERVATION[1]),
        ("Actually executed V9 runner source SHA-256", RUNNER_SOURCE),
        ("Actually executed V9 runner protocol SHA-256", RUNNER_PROTOCOL),
        ("Actually executed V9 runner contract SHA-256", RUNNER_CONTRACT),
        ("Recorded build archive SHA-256 (not opened by this graph)",
         BUILD_ARCHIVE_SHA),
        ("Retained empty recovery-root inode", str(RECOVERY_ROOT_INODE)),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + index * 18}" class="foot">'
            f'{label}: {value}</text>')
    lines.extend((
        '<text x="65" y="2167" class="small">V9 read and inflated '
        'the native-build archive once and created one empty recovery '
        'root; no journal or candidate worker.</text>',
        '<text x="65" y="2187" class="small">Recorded inner error: '
        'accept only one exact owner-only Rust campaign root.</text>',
        '<text x="65" y="2207" class="small">13 failed-worker '
        'exception records; worker-attempted flags are synthetic, '
        'not started suites or real workers.</text>',
        '<text x="65" y="2227" class="small">Matching: NOT RUN. '
        'Original targets unchanged. Holdout unopened. Faster '
        'compatible replacement: none.</text>',
        '<!-- One actual V9 archive read and one empty recovery root; '
        'this graph does not open archives, tmp, targets, native '
        'libraries, holdout or clocks. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V55 graph inputs SHA-256", V55["inputs"][1]),
        ("Historical V55 graph renderer SHA-256", V55["source"][1]),
        ("Historical V55 graph summary SHA-256", V55["summary"][1]),
        ("Historical V55 graph image SHA-256", V55["svg"][1]),
    ):
        base.need(raw.count((label + ": " + value).encode("ascii")) == 1,
                  "bind exact actual or explicitly historical V56 footer")
    base.need(
        ("Graph inputs SHA-256: " + V55["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V55["source"][1]).encode("ascii")
        not in raw,
        "never call historical V55 graph owners the current V56 graph")
    lower = raw.lower()
    for phrase in (
        b'height="2250"', b"building a faster python re",
        b"failed again before matching", b"v8 and v9",
        b"928 differences", b"8,965 explicitly verified",
        b"13 real workers", b"real new workers: 0",
        b"31,237", b"4.2m unopened", b"not measured",
        b"one empty recovery root", b"no journal",
        b"failed-worker", b"exception records",
        b"recorded inner error",
        b"accept only one exact owner-only rust campaign root",
        b"worker-attempted", b"synthetic", b"not started suites", b"original targets unchanged",
        b"matching: not run", b"189 / 194", b"191 / 196",
        b"signature checks", b"public-interface observations",
        b"large-input observations", b"17 pass", b"7 fail",
        b"22 pass", b"3 not run", b"2,147,483,648",
        b"1,087", b"1,036", b"1,262", b"1,230",
        b"2,172", b"1,764", b"not generated", b"not opened",
        b"not opened by this graph",
        b"independent v9 failure observation",
    ):
        base.need(phrase in lower,
                  "retain honest V9 no-worker failure: " + repr(phrase))
    for falsehood in (
        b"v9 matching passed", b"v9 matching failed",
        b"v9 semantic mismatches", b"13 actual v9 workers",
        b"13 observed v9 suites", b"all targets restored",
        b"recovery journal was written", b"zero recovery roots",
        b"no archive was read by the controller",
        b"corrected candidate passed", b"rust candidate qualified",
        b"28 unique compiler pids", b"winner selected",
        b"holdout opened", b"faster than python", b"32 repaired",
    ):
        base.need(falsehood not in lower,
                  "reject fabricated matching or erased effects: "
                  + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish complete truthful V56 chart with one exact linefeed")
    return raw


def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact independent V56 graph source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound actual independently owned V56 graph source")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                private=True)
    old, old_inputs, old_svg = authenticate_v55(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V55},
    )
    proof = authenticate_failure(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v55_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V55.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 56,
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
            "authenticated_evidence_owner_lower_bound": 191,
            "authenticated_history_reference_lower_bound": 196,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "actual_v9_entry_failure": copy.deepcopy(proof),
                "actual_v9_controller_status": "FAIL",
                "actual_v9_failure_stage":
                    "RECOVERY-ROOT PREFLIGHT; NO MATCHING",
                "actual_v9_matching_status": "NOT RUN",
                "actual_v9_semantic_mismatch_count": "NOT MEASURED",
                "actual_v9_verified_passing_case_count": "NOT MEASURED",
                "actual_v9_candidate_correctness": "NOT MEASURED",
                "actual_v9_candidate_workers": 0,
                "actual_v9_attempted_suite_count": 0,
                "actual_v9_started_suite_count": 0,
                "actual_v9_completed_suite_count": 0,
                "actual_v9_fully_observed_suite_count": 0,
                "actual_v9_synthetic_failed_worker_placeholder_count": 13,
                "actual_v9_recorded_original_inner_exception": INNER_ERROR_MESSAGE,
                "actual_v9_recorded_original_inner_exception_placeholder_count": 13,
                "actual_v9_placeholder_worker_flags_are_real_attempts": False,
                "actual_v9_synthetic_placeholders_are_observed_workers": False,
                "actual_v9_native_activations": 0,
                "actual_v9_recovery_roots_created": 1,
                "actual_v9_recovery_journals_created": 0,
                "actual_v9_recovery_locks_acquired": 0,
                "actual_v9_original_targets_restored_by_recovery": False,
                "actual_v9_controller_build_archive_reads": 1,
                "actual_v9_controller_build_archive_inflations": 1,
                "actual_v9_build_archive_read_by_graph": False,
                "actual_v9_candidate_qualified": False,
                "actual_v8_controller_status": "FAIL",
                "actual_v8_matching_status": "NOT RUN",
                "actual_v8_semantic_mismatch_count": "NOT MEASURED",
                "actual_v8_candidate_workers": 0,
                "actual_v8_controller_build_archive_reads": 1,
                "actual_v8_controller_build_archive_inflations": 1,
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
        "version": 56,
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
              "bound exactly three complete authorized V56 graph outputs")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )

def synthetic_failure() -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v9-entry-failure",
        "status": "FAIL",
        "family": "rust",
        "error_type": "CampaignError",
        "error_message": ERROR_MESSAGE,
        "traceback": "synthetic controller traceback: " + ERROR_MESSAGE,
        "actual_operation_mode": "AUTHORIZED RUN",
        "source_only_zero_effects_claimed": False,
        "actual_effects": {
            **failure_effects(),
            "retained_suite_results": [
                {
                    "suite": suite,
                    "case_execution_denominator": case_count,
                    "worker_attempted": True,
                    "actual_worker_started": False,
                    "fully_observed": False,
                    "process": None,
                    "error_message": INNER_ERROR_MESSAGE,
                    "failure_class": "INFRASTRUCTURE FAILURE",
                    "mismatch_count": "NOT MEASURED",
                    "verified_passing_case_count": 0,
                }
                for suite, case_count in RETAINED_V9_SUITE_CASES
            ],
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
        "schema": "rebar-owned-repaired-rust-original-campaign-v9-"
                  "entry-failure-observation-v1",
        "version": 1,
        "status": "PASS",
        "observation_pass_means":
            "DURABLE INDEPENDENT OBSERVATION OF A FAILED CANDIDATE "
            "CONTROLLER; NOT A PASSING CANDIDATE",
        "observed_operation": "ONE AUTHORIZED RUST V9 ORIGINAL-CAMPAIGN RUN",
        "actual_pushed_runner_head": PUSHED_HEAD,
        "authenticated_evidence_owner_lower_bound_before_publication": 189,
        "authenticated_history_reference_lower_bound_before_publication": 194,
        "new_actual_observation_owner_count": 2,
        "resulting_authenticated_evidence_owner_lower_bound": 191,
        "resulting_authenticated_history_reference_lower_bound": 196,
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
            "schema": "rebar-owned-repaired-rust-original-campaign-v9-entry-failure",
            "status": "FAIL",
            "actual_operation_mode": "AUTHORIZED RUN",
            "error_type": "CampaignError",
            "error_message": ERROR_MESSAGE,
            "source_line": 3111,
            "failure_category":
                "OWNER-ONLY RECOVERY ROOT CREATED; INCOMPATIBLE HISTORICAL "
                "HELPER PREFIX REJECTS ROOT BEFORE LOCK OR ACTIVATION",
            "candidate_matching": "NOT RUN",
            "full_original_case_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "additional_private_waiver_count": 0,
            "attempted_suite_count": 0,
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
            "device": DEVICE, "inode": FAILURE_INODE, "mode": "0600",
            "nlink": 1,
            "schema": "rebar-owned-repaired-rust-original-campaign-v9-entry-failure",
            "status": "FAIL", "source_only_zero_effects_claimed": False,
        },
        "actual_build_archive_effects": {
            "compressed_build_archive_sha256": BUILD_ARCHIVE_SHA,
            "actual_archive_read_count": 1,
            "actual_archive_inflation_count": 1,
            "compressed_bytes_read": 109671,
            "uncompressed_bytes_read": 765382,
            "uncompressed_sha256": UNCOMPRESSED_ARCHIVE_SHA,
            "archive_read_by_independent_observer": False,
        },
        "actual_target_effects": {
            "canonical_target_replacements": 0,
            "actual_native_activations": 0,
            "activated_target_roles": [],
            "recovery_root_creation_attempted": True,
            "recovery_roots_created": 1,
            "recovery_root": {
                "path": RECOVERY_ROOT,
                "device": RECOVERY_ROOT_DEVICE,
                "inode": RECOVERY_ROOT_INODE,
                "mode": "0700",
                "directory_is_empty": True,
                "directory_identity_provenance":
                    "INDEPENDENTLY ATTESTED BY ROOT; OBSERVER DID NOT OPEN, "
                    "ENUMERATE, OR MODIFY THE DIRECTORY",
            },
            "recovery_lock_attempted": False,
            "recovery_locks_acquired": 0,
            "recovery_journal_creation_attempted": False,
            "recovery_journals_created": 0,
            "recovery_journal_announced": False,
            "restoration_attempted": False,
            "restored_target_roles": [],
            "all_four_original_targets_unchanged_without_recovery": True,
            "all_four_original_targets_restored_by_a_recovery": False,
            "all_four_original_targets_restored": False,
            "original_target_identity_provenance":
                "INDEPENDENTLY ATTESTED BY ROOT BEFORE AND AFTER THE RUN; "
                "OBSERVER DID NOT ACCESS THE CANDIDATE TARGETS",
            "original_targets": [
                {"synthetic_role": "bridge-source"},
                {"synthetic_role": "adapter"},
                {"synthetic_role": "engine"},
                {"synthetic_role": "bridge"},
            ],
        },
        "actual_failed_suite_placeholders": {
            "provenance":
                "ALL 13 RETAINED ROWS FROM THE AUTHENTICATED ACTUAL "
                "CONTROLLER FAILURE; NO ROW REPRESENTS A STARTED OR "
                "OBSERVED CANDIDATE WORKER",
            "retained_suite_count": 13,
            "case_execution_denominator": 31237,
            "shared_inner_error_message": INNER_ERROR_MESSAGE,
            "all_rows_are_synthetic_infrastructure_placeholders": True,
            "placeholder_worker_attempted_means_a_real_worker_was_attempted":
                False,
            "placeholder_verified_passing_count_is_a_real_observed_pass_count":
                False,
            "actual_ledger_attempted_suite_count": 0,
            "actual_ledger_started_suite_count": 0,
            "actual_ledger_fully_observed_suite_count": 0,
            "actual_ledger_candidate_workers": 0,
            "actual_ledger_worker_attempts": [],
            "actual_ledger_worker_process_ids": [],
            "rows": [
                {
                    "suite": suite,
                    "case_execution_denominator": case_count,
                    "error_message": INNER_ERROR_MESSAGE,
                    "failure_class": "INFRASTRUCTURE FAILURE",
                    "worker_attempted": True,
                    "actual_worker_started": False,
                    "fully_observed": False,
                    "process": None,
                    "mismatch_count": "NOT MEASURED",
                    "verified_passing_case_count": 0,
                }
                for suite, case_count in RETAINED_V9_SUITE_CASES
            ],
        },
        "historical_actual_candidate_matching": {
            "status": "FAIL",
            "semantic_mismatch_count": 928,
            "verified_passing_case_count": 8965,
            "completed_suite_count": 13,
            "distinct_worker_process_id_count": 13,
            "passing_cases_derived_by_subtraction": False,
        },
        "frozen_runner": {
            "source": {
                "path": "tools/run_owned_repaired_rust_original_campaign_v9.py",
                "sha256": RUNNER_SOURCE, "bytes": 173643,
            },
            "protocol": {
                "path": "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V9.md",
                "sha256": RUNNER_PROTOCOL, "bytes": 12690,
            },
            "contract": {
                "path": "oracle/phase2/repaired-rust-original-campaign-v9.json",
                "sha256": RUNNER_CONTRACT, "bytes": 15235,
            },
        },
        "root_cause": {
            "summary":
                "The V9 campaign reuses the frozen V7 recovery helper without "
                "rebinding the frozen V2 helper's version-2-only "
                "private-directory prefix to the real version-9 recovery root.",
            "verified_source_cause":
                "V7 open_recovery_lock creates and counts the exact V9 root, "
                "then calls V2 private_directory before setting "
                "recovery_lock_attempted. V2 checked_private_root accepts "
                "only the incompatible "
                "rebar-phase2-repaired-rust-original-campaign-v2- prefix. "
                "V9 configures the historical V2 label and roles but never "
                "rebinds PRIVATE_PREFIX. The caller-provided V9 root "
                "therefore cannot pass the V2 directory check.",
            "historical_v2_source": {
                "path": "tools/run_owned_repaired_rust_original_campaign_v2.py",
                "sha256": "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3",
                "private_prefix_line": 55,
                "private_prefix": "rebar-phase2-repaired-rust-original-campaign-v2-",
                "root_validator_line": 1371,
            },
            "historical_v7_source": {
                "path": "tools/run_owned_repaired_rust_original_campaign_v7.py",
                "sha256": "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
                "recovery_lock_function_line": 7762,
            },
            "v9_historical_helper_configuration_line": 2334,
            "v9_final_masking_requirement_line": 3111,
            "verified_effect_sequence": [
                "ONE COMPLETE V16 BUILD ARCHIVE READ AND GZIP INFLATION",
                "GENUINE V16 PRIVATE BUILD AND FIRST-PARTY NATIVE "
                "PROVENANCE AUTHENTICATED",
                "HISTORICAL V2 HELPER SOURCE AND MODULE PREFLIGHT PASS",
                "EXACTLY ONE OWNER-ONLY V9 RECOVERY ROOT CREATED",
                "V2 VERSION-2-ONLY ROOT VALIDATOR REACHED BEFORE ANY LOCK ATTEMPT",
                "NO LOCK, NO JOURNAL, NO ACTIVATION, NO WORKER, "
                "NO TARGET REPLACEMENT",
                "FINAL PREPARED-AND-RESTORED-JOURNAL REQUIREMENT "
                "MASKS THE INNER TRACEBACK; ALL 13 SYNTHETIC FAILURE "
                "ROWS PRESERVE THE INNER ERROR MESSAGE",
            ],
            "original_inner_exception": INNER_ERROR_MESSAGE,
            "original_inner_exception_provenance":
                "IDENTICALLY RECORDED IN EACH OF THE 13 AUTHENTICATED "
                "SYNTHETIC RETAINED-SUITE ROWS; NONE REPRESENTS AN "
                "EXECUTED WORKER",
            "original_inner_traceback":
                "MASKED BY THE FINAL PREPARED-JOURNAL REQUIREMENT; "
                "NOT INVENTED",
            "outer_exception": ERROR_MESSAGE,
            "required_future_fix":
                "Freeze a new append-only campaign version that rebinds the "
                "historical V2 helper's private prefix before private_directory, "
                "verifies the exact caller-pinned owner-only versioned root, "
                "covers real helper prefix acceptance and rejection in "
                "source-only controls, and retains original-inode recovery "
                "and all complete original CPython cases.",
            "withdrawn_oracle_cases": 0,
            "new_private_waivers": 0,
        },
    }

def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_failure_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged actual V9 failure: " + description)


def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 3171
        and prior.get("actual_rust_v16_build_status") == "PASS"
        and prior.get("actual_rust_v16_compiler_process_count") == 28
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and prior.get("actual_rust_v7_candidate_workers") == 13
        and prior.get("actual_rust_v8_controller_status") == "FAIL"
        and prior.get("actual_rust_v8_matching_status") == "NOT RUN"
        and prior.get("actual_rust_v8_candidate_workers") == 0
        and prior.get("actual_rust_v8_build_archive_reads_by_controller") == 1
        and prior.get("rust_original_campaign_v9_matching_status") == "NOT RUN"
        and prior.get("authenticated_evidence_owner_lower_bound") == 189
        and prior.get("authenticated_history_reference_lower_bound") == 194
        and prior.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "preserve all 3,171 actually pushed V55 source-only controls",
    )
    v43 = prior_modules[1][1][9]
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
        for index, row in enumerate(
                proof["complete_actual_failure"]["actual_effects"][
                    "retained_suite_results"]):
            for key, value in row.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_actual_failure"]["actual_effects"][
                    "retained_suite_results"][index][key] = (
                        v43.forged_value(base, value))
                rejected += reject_control(
                    base, hostile, "real-retained-placeholder:"
                    + str(index) + ":" + key)
        for key, value in proof["complete_independent_observation"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_independent_observation"][key] = (
                v43.forged_value(base, value))
            rejected += reject_control(base, hostile, "observation:" + key)
        for section in (
                "observed_failure", "exact_recorded_controller_stdout",
                "actual_build_archive_effects", "actual_target_effects",
                "historical_actual_candidate_matching", "frozen_runner",
                "root_cause", "actual_failed_suite_placeholders"):
            nested = proof["complete_independent_observation"][section]
            for key, value in nested.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_observation"][section][key] = (
                    v43.forged_value(base, value))
                rejected += reject_control(
                    base, hostile, "observation:" + section + ":" + key)
        for index, row in enumerate(
                proof["complete_independent_observation"][
                    "actual_failed_suite_placeholders"]["rows"]):
            for key, value in row.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_observation"][
                    "actual_failed_suite_placeholders"]["rows"][
                        index][key] = v43.forged_value(base, value)
                rejected += reject_control(
                    base, hostile, "independent-retained-placeholder:"
                    + str(index) + ":" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v56")),
            ("filesystem", lambda: os.open("forbidden-v56", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v56")),
            ("write", lambda: os.mkdir("forbidden-v56")),
            ("process", lambda: subprocess.run(("forbidden-v56",))),
            ("process", lambda: subprocess.Popen(("forbidden-v56",))),
            ("process", lambda: os.execv("/forbidden-v56", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically forbid actual V56 graph " + kind)
            else:
                raise base.GraphError("forbidden V56 source-only effect escaped")
        base.need(rejected >= 175,
                  "reject every forged V9 outcome and erased real effect")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 56,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v55_hostile_controls": 3171,
            "new_v56_hostile_controls": rejected,
            "rejected_hostile_control_count": 3171 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_owners_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_receipts_read_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
            "actual_frozen_v9_source_files_read_by_self_test": 0,
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
            "actual_current_graph_predecessor_version": 55,
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
            "actual_rust_v8_build_archive_reads_by_controller": 1,
            "actual_rust_v9_controller_status": "FAIL",
            "actual_rust_v9_matching_status": "NOT RUN",
            "actual_rust_v9_semantic_mismatch_count": "NOT MEASURED",
            "actual_rust_v9_candidate_workers": 0,
            "actual_rust_v9_attempted_suite_count": 0,
            "actual_rust_v9_started_suite_count": 0,
            "actual_rust_v9_completed_suite_count": 0,
            "actual_rust_v9_fully_observed_suite_count": 0,
            "actual_rust_v9_synthetic_failed_worker_placeholder_count": 13,
            "actual_rust_v9_recorded_original_inner_exception": INNER_ERROR_MESSAGE,
            "actual_rust_v9_recorded_original_inner_exception_placeholder_count": 13,
            "actual_rust_v9_placeholder_worker_flags_are_real_attempts": False,
            "actual_rust_v9_synthetic_placeholders_are_observed_workers": False,
            "actual_rust_v9_native_activations": 0,
            "actual_rust_v9_recovery_roots_created": 1,
            "actual_rust_v9_recovery_journals_created": 0,
            "actual_rust_v9_recovery_locks_acquired": 0,
            "actual_rust_v9_original_targets_restored_by_recovery": False,
            "actual_rust_v9_build_archive_reads_by_controller": 1,
            "actual_rust_v9_build_archive_inflations_by_controller": 1,
            "actual_rust_v9_build_archive_read_by_graph": False,
            "actual_rust_v9_build_archive_inflated_by_graph": False,
            "actual_rust_v9_historical_contract_evidence_lower_bound": 186,
            "actual_rust_v9_historical_contract_history_lower_bound": 191,
            "actual_rust_v9_historical_contract_resulting_evidence_lower_bound":
                188,
            "actual_rust_v9_historical_contract_resulting_history_lower_bound":
                193,
            "actual_rust_v9_current_prepublication_evidence_lower_bound": 189,
            "actual_rust_v9_current_prepublication_history_lower_bound": 194,
            "authenticated_evidence_owner_lower_bound": 191,
            "authenticated_history_reference_lower_bound": 196,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "supplementary_signature_check_count": 50,
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts": copy.deepcopy(PUBLIC_COUNTS),
            "large_input_source_case_matrix_count": 32,
            "large_input_source_case_status_counts": copy.deepcopy(LARGE_COUNTS),
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
              "publish only the three authorized actual V56 graph outputs")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact authorized V56 graph byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid() and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish one private complete independently owned V56 asset")
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
    base.need(confirmed == raw, "re-authenticate complete V56 graph output")


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 56,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 55,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V55.items()},
        "actual_rust_v16_build_status": snapshot["actual_rust_v16_build_status"],
        "actual_rust_v16_compiler_process_count":
            snapshot["actual_rust_v16_compiler_process_count"],
        "actual_rust_v7_semantic_status": snapshot["actual_rust_v7_semantic_status"],
        "actual_rust_v7_semantic_mismatch_count":
            snapshot["actual_rust_v7_semantic_mismatch_count"],
        "actual_rust_v7_explicitly_verified_passing_case_count":
            snapshot["actual_rust_v7_explicitly_verified_passing_case_count"],
        "actual_rust_v7_candidate_workers": snapshot["actual_rust_v7_candidate_workers"],
        "actual_rust_v8_controller_status": snapshot["actual_rust_v8_controller_status"],
        "actual_rust_v8_matching_status": snapshot["actual_rust_v8_matching_status"],
        "actual_rust_v8_candidate_workers": snapshot["actual_rust_v8_candidate_workers"],
        "actual_rust_v8_build_archive_reads_by_controller":
            snapshot["actual_rust_v8_build_archive_reads_by_controller"],
        "actual_rust_v9_controller_status": snapshot["actual_rust_v9_controller_status"],
        "actual_rust_v9_matching_status": snapshot["actual_rust_v9_matching_status"],
        "actual_rust_v9_semantic_mismatch_count":
            snapshot["actual_rust_v9_semantic_mismatch_count"],
        "actual_rust_v9_candidate_workers": snapshot["actual_rust_v9_candidate_workers"],
        "actual_rust_v9_attempted_suite_count":
            snapshot["actual_rust_v9_attempted_suite_count"],
        "actual_rust_v9_started_suite_count":
            snapshot["actual_rust_v9_started_suite_count"],
        "actual_rust_v9_completed_suite_count":
            snapshot["actual_rust_v9_completed_suite_count"],
        "actual_rust_v9_fully_observed_suite_count":
            snapshot["actual_rust_v9_fully_observed_suite_count"],
        "actual_rust_v9_synthetic_failed_worker_placeholder_count":
            snapshot["actual_rust_v9_synthetic_failed_worker_placeholder_count"],
        "actual_rust_v9_recorded_original_inner_exception":
            snapshot["actual_rust_v9_recorded_original_inner_exception"],
        "actual_rust_v9_recorded_original_inner_exception_placeholder_count":
            snapshot["actual_rust_v9_recorded_original_inner_exception_placeholder_count"],
        "actual_rust_v9_placeholder_worker_flags_are_real_attempts":
            snapshot["actual_rust_v9_placeholder_worker_flags_are_real_attempts"],
        "actual_rust_v9_synthetic_placeholders_are_observed_workers":
            snapshot["actual_rust_v9_synthetic_placeholders_are_observed_workers"],
        "actual_rust_v9_recovery_roots_created":
            snapshot["actual_rust_v9_recovery_roots_created"],
        "actual_rust_v9_recovery_journals_created":
            snapshot["actual_rust_v9_recovery_journals_created"],
        "actual_rust_v9_original_targets_restored_by_recovery":
            snapshot["actual_rust_v9_original_targets_restored_by_recovery"],
        "actual_rust_v9_build_archive_reads_by_controller":
            snapshot["actual_rust_v9_build_archive_reads_by_controller"],
        "actual_rust_v9_build_archive_inflations_by_controller":
            snapshot["actual_rust_v9_build_archive_inflations_by_controller"],
        "actual_rust_v9_build_archive_read_by_graph":
            snapshot["actual_rust_v9_build_archive_read_by_graph"],
        "actual_rust_v9_current_prepublication_evidence_lower_bound":
            snapshot["actual_rust_v9_current_prepublication_evidence_lower_bound"],
        "actual_rust_v9_current_prepublication_history_lower_bound":
            snapshot["actual_rust_v9_current_prepublication_history_lower_bound"],
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
    for role in V55:
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
        modules = load_v55()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256" for role in V55)
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
                                  "actual complete V56 graph source")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render only the three root-authorized V56 assets")
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published")
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "actual exact V56 graph inputs"),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "actual exact V56 graph summary"),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "actual exact V56 graph chart"),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True)
                base.need(raw == outputs[path],
                          "reproduce one actual V56 graph asset: " + path)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context")
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V56 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V56 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
