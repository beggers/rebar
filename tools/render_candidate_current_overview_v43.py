#!/usr/bin/env python3
"""Report the genuine first Rust preflight failure without inventing a run."""

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
SELF = "tools/render_candidate_current_overview_v43.py"
OUTPUT = "docs/evidence/candidate-current-overview-v43"
SCHEMA = "rebar-candidate-current-overview-v43"
V42 = {
    "source": (
        "tools/render_candidate_current_overview_v42.py",
        "8e4783f7c61340ce8f291f84e2dfa802189a66353edd7a89026934d9863d1ce2",
        51652,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v42.inputs.json",
        "ca11b1d4d7e7cd483a8ebf81fe12f36037a22608cf8ab459ce9d97d16f86dda2",
        271354,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v42.json",
        "30b7ba546209796f950ea6720a19acb16972bf8d984841f74d45c00d4c639838",
        787504,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v42.svg",
        "3d1f05706861d662f3113dc7340ceb09731c66b137df99637819a3e8b4cbd781",
        12837,
    ),
}
RUST = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v6.py",
        "c25cbdf3674fc3e054c388e53de3ed38d4b1dab0a820808c42848e1803909f5e",
        374429,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V6.md",
        "ddc5c212d3e188bc1d1cdde992bf872a38962e64d3b07d6ec7c275ba4f55f13c",
        8551,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v6.json",
        "ce044f18be388ab0608d0bd3bb68751e6970973f8e6ef758971e75e6d6b584a5",
        33386,
    ),
}
FAILURE = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v6-rust-phase2-v13-rust-pattern-repr-"
    "original-p0-entry-failure.json",
    "88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7",
    3175,
)
OBSERVATION = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v6-rust-phase2-v13-rust-pattern-repr-"
    "original-p0-entry-failure-observation.json",
    "51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6",
    3061,
)
# Both exact, independently reviewed failure owners were expressly released.
ACTUAL_FAILURE_PINS_RELEASED = True
HELPER = (
    "tools/run_owned_repaired_rust_original_campaign_v2.py",
    "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3",
    143441,
)
ACTUAL_V2_ADAPTER = (
    "candidates/rust_candidate.py",
    "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c",
    31464,
)
WRONG_EXPECTED_ADAPTER = (
    "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
)
BUILD_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0.json.gz",
    "c201c014f55a51454baab77d2148dc39d6024bae3273242d6eb1f1b43f419f6a",
    108985,
)
BUILD_PLAIN_SHA = (
    "7bf86cbaec1df17548a0989d03db896036a86b0671d32e82f12ce4c3fae630db"
)
BUILD_PLAIN_BYTES = 760477
ERROR_MESSAGE = "authenticate immutable historical helpers without running V2"
ATTEMPT_STATUS = "FAIL; RUST CONTROLLER PREFLIGHT FAILED BEFORE ANY SUITE"
MATCHING_STATUS = "NOT RUN; RUST CONTROLLER PREFLIGHT FAILED"
BLOCK_REASON = (
    "One authorized Rust controller genuinely failed its historical-helper "
    "check before activating a native engine or starting any original-suite "
    "worker. Its context inflated one historical Rust source-build archive, "
    "an effect omitted from the frozen controller ledger. No Rust matching "
    "archive or corrected-reference archive was read. The C candidate and "
    "the other four source designs have not been run."
)


def load_v42() -> tuple[types.ModuleType, types.ModuleType,
                        types.ModuleType, types.ModuleType]:
    path, fingerprint, size = V42["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject a substituted or nonprivate pushed V42 renderer")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            if not piece:
                raise ValueError("reject a truncated exact pushed V42 renderer")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended bytes after the pushed V42 renderer")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            raise ValueError("reject V42 renderer replacement during graph loading")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_exact_pushed_v42_for_real_rust_failure")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    v41, v40, base = previous.load_v41()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v42"
              and previous.SELF == path,
              "load only the actually pushed exact independent C/Rust V42 graph")
    return previous, v41, v40, base


def authenticate_v42(previous: types.ModuleType, v41: types.ModuleType,
                     v40: types.ModuleType, base: types.ModuleType
                     ) -> tuple[dict, dict]:
    for item in V42.values():
        base.read_owner(*item, private=True)
    inputs_raw, _ = base.read_owner(*V42["inputs"], private=True)
    summary_raw, _ = base.read_owner(*V42["summary"], private=True)
    svg_raw, _ = base.read_owner(*V42["svg"], private=True)
    inputs = base.document(inputs_raw, "complete independently pushed V42 inputs")
    summary = base.document(summary_raw, "complete independently pushed V42 summary")
    snapshot = summary.get("snapshot")
    previous.validate_snapshot(v41, v40, base, snapshot)
    base.need(
        summary.get("schema") == "rebar-candidate-current-overview-v42-summary"
        and summary.get("version") == 42
        and summary.get("status") == "PASS"
        and summary.get("source") == base.pin(*V42["source"])
        and summary.get("inputs") == base.pin(*V42["inputs"])
        and summary.get("svg") == base.pin(*V42["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v42-inputs"
        and inputs.get("version") == 42
        and inputs.get("renderer") == base.pin(*V42["source"])
        and svg_raw == previous.make_svg(
            v41, v40, base, snapshot,
            V42["source"][1], V42["inputs"][1],
        ),
        "authenticate and reproduce every complete pushed V42 predecessor byte",
    )
    return summary, inputs


def validate_failure(base: types.ModuleType, value: object) -> None:
    base.need(type(value) is dict, "reject a missing genuine Rust entry failure")
    assert isinstance(value, dict)
    base.need(
        value.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v6-entry-failure"
        and value.get("status") == "FAIL"
        and value.get("family") == "rust"
        and value.get("effect_ledger_schema")
        == "rebar-owned-repaired-rust-original-campaign-v6-"
           "authorized-run-actual-effect-ledger"
        and value.get("campaign_mode") == "AUTHORIZED RUN"
        and value.get("campaign_source_sha256") == RUST["source"][1]
        and value.get("campaign_protocol_sha256") == RUST["protocol"][1]
        and value.get("campaign_contract_sha256") == RUST["contract"][1]
        and value.get("error_type") == "CampaignError"
        and value.get("error_message") == ERROR_MESSAGE
        and value.get("case_execution_denominator") == 31237
        and value.get("suite_count") == 13,
        "bind the real authorized Rust V6 failure to its exact first-party source",
    )
    for key in (
        "attempted_suite_count", "started_suite_count",
        "fully_observed_suite_count", "actual_candidate_workers",
        "actual_native_activations", "actual_reference_workers",
        "actual_source_builds", "canonical_target_read_lower_bound",
        "canonical_target_replacements", "recovery_roots_created",
        "recovery_locks_acquired", "recovery_journals_created",
        "hidden_cases_read", "benchmark_files_read", "clock_samples",
        "timing_trials_run",
    ):
        base.need(type(value.get(key)) is int and value[key] == 0,
                  "never invent an actual Rust preflight effect: " + key)
    for key in (
        "activated_target_roles", "actual_worker_process_ids",
        "restored_target_roles", "retained_suite_results", "worker_attempts",
    ):
        base.need(value.get(key) == [],
                  "never invent an actual Rust suite, process or recovery: " + key)
    for key in (
        "all_four_original_targets_restored",
        "all_original_observation_vectors_complete",
        "archive_publication_attempted", "bounded_report_attempted",
        "candidate_qualified", "original_case_archive_durably_published",
        "publication_attempted", "receipt_publication_attempted",
        "recovery_journal_announced", "recovery_journal_creation_attempted",
        "recovery_lock_attempted", "recovery_root_creation_attempted",
        "restoration_attempted", "restoration_verified",
        "source_only_zero_effects_claimed", "winner_selected",
    ):
        base.need(value.get(key) is False,
                  "reject an invented successful Rust preflight effect: " + key)
    for key in ("archive_owner", "receipt_owner", "publication_failure",
                "recovery_journal_sha256"):
        base.need(value.get(key) is None,
                  "never fabricate a Rust matching archive or receipt: " + key)
    for key in ("archive_publication_status", "receipt_publication_status",
                "publication_status"):
        base.need(value.get(key) == "NOT ATTEMPTED",
                  "never confuse preflight with durable publication: " + key)
    for key in ("semantic_mismatch_count", "canonical_target_reads",
                "canonical_target_stats", "performance", "memory",
                "undefined_behavior"):
        base.need(value.get(key) == "NOT MEASURED",
                  "never measure an unstarted actual Rust worker: " + key)
    trace = value.get("traceback")
    base.need(
        type(trace) is list and 2 <= len(trace) <= 34
        and all(type(line) is str for line in trace)
        and any("patched_v2_helpers" in line for line in trace)
        and any("run_campaign" in line for line in trace)
        and trace[-1] == "CampaignError: " + ERROR_MESSAGE + "\n"
        and value.get("holdout") == "NOT OPENED"
        and value.get("actual_evidence_owner_count_before_new_campaign") == 164
        and value.get("actual_authenticated_reference_count_before_new_campaign")
        == 169,
        "retain the complete real helper failure and historical evidence bounds",
    )


def validate_observation(base: types.ModuleType, value: object) -> None:
    base.need(type(value) is dict,
              "reject a missing independent record of the omitted build effect")
    assert isinstance(value, dict)
    base.need(
        value.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v6-"
           "entry-failure-independent-observation-v1"
        and value.get("observation_status")
        == "PASS; FAILURE AND OMITTED SOURCE-BUILD EFFECT PRESERVED",
        "authenticate the actual observed failure, not a candidate pass",
    )
    predecessor = value.get("published_predecessor")
    base.need(
        type(predecessor) is dict
        and predecessor.get("commit") == "2a85610e"
        and predecessor.get("overview_version") == 42
        and predecessor.get("overview_summary_sha256") == V42["summary"][1],
        "bind the one actual Rust attempt to the pushed V42 predecessor",
    )
    invocation = value.get("actual_invocation")
    base.need(
        type(invocation) is dict
        and type(invocation.get("count")) is int
        and invocation["count"] == 1
        and invocation.get("mode") == "AUTHORIZED RUN"
        and invocation.get("family") == "rust"
        and invocation.get("exit_code") == 1
        and invocation.get("source_sha256") == RUST["source"][1]
        and invocation.get("protocol_sha256") == RUST["protocol"][1]
        and invocation.get("contract_sha256") == RUST["contract"][1]
        and invocation.get("stdout") == base.pin(*FAILURE)
        and invocation.get("error_type") == "CampaignError"
        and invocation.get("error_message") == ERROR_MESSAGE,
        "require exactly one genuine failing Rust controller and its full stdout",
    )
    cause = value.get("root_cause")
    base.need(
        type(cause) is dict
        and cause.get("kind")
        == "IMMUTABLE HISTORICAL HELPER ADAPTER FINGERPRINT MISMATCH"
        and cause.get("helper_source") == base.pin(*HELPER)
        and type(cause.get("actual_v2_repaired_adapter")) is dict
        and cause["actual_v2_repaired_adapter"].get("path")
        == ACTUAL_V2_ADAPTER[0]
        and cause["actual_v2_repaired_adapter"].get("sha256")
        == ACTUAL_V2_ADAPTER[1]
        and cause["actual_v2_repaired_adapter"].get("bytes")
        == ACTUAL_V2_ADAPTER[2]
        and cause["actual_v2_repaired_adapter"].get("identity")
        == "historical V2 source-owner tuple, not a current target read"
        and cause.get("incorrect_v6_expected_historical_adapter_sha256")
        == WRONG_EXPECTED_ADAPTER
        and cause.get("failed_function") == "patched_v2_helpers"
        and cause.get("failed_condition")
        == "v2.REPAIRED_SOURCE_OWNERS[0][1] == "
           "HISTORICAL_DERIVED_PUBLIC_SHA256",
        "prove the precise immutable 81089-vs-f8afb historical adapter failure",
    )
    effect = value.get("source_build_archive_effect")
    base.need(type(effect) is dict,
              "never hide the genuine source-build archive inflation")
    archive = effect.get("archive")
    base.need(
        type(effect.get("observation_basis")) is str
        and "before patched_v2_helpers raises" in effect["observation_basis"]
        and effect.get("controller_failure_ledger_records_effect") is False
        and effect.get("archive_read_count") == 1
        and effect.get("gzip_inflation_count") == 1
        and effect.get("matching_archive_read_count") == 0
        and effect.get("reference_archive_read_count") == 0
        and effect.get("nested_matching_archive_read_count") == 0
        and type(archive) is dict
        and archive.get("path") == BUILD_ARCHIVE[0]
        and archive.get("sha256") == BUILD_ARCHIVE[1]
        and archive.get("compressed_bytes") == BUILD_ARCHIVE[2]
        and archive.get("uncompressed_sha256") == BUILD_PLAIN_SHA
        and archive.get("uncompressed_bytes") == BUILD_PLAIN_BYTES,
        "report the one real, ledger-omitted V13 build archive exactly",
    )
    actual = value.get("actual_candidate_effects")
    base.need(
        type(actual) is dict
        and actual.get("case_execution_denominator") == 31237
        and actual.get("suite_count") == 13
        and actual.get("attempted_suite_count") == 0
        and actual.get("started_suite_count") == 0
        and actual.get("fully_observed_suite_count") == 0
        and actual.get("candidate_workers") == 0
        and actual.get("reference_workers") == 0
        and actual.get("native_activations") == 0
        and actual.get("recovery_roots_created") == 0
        and actual.get("recovery_journals_created") == 0
        and actual.get("archive_publication_status") == "NOT ATTEMPTED"
        and actual.get("receipt_publication_status") == "NOT ATTEMPTED"
        and actual.get("semantic_mismatch_count") == "NOT MEASURED"
        and actual.get("candidate_qualified") is False
        and actual.get("performance") == "NOT MEASURED"
        and actual.get("memory") == "NOT MEASURED"
        and actual.get("undefined_behavior") == "NOT MEASURED"
        and actual.get("holdout") == "NOT OPENED",
        "keep all original Rust suite outcomes unmeasured before activation",
    )


def validate_failure_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject a missing independently observed real Rust failure")
    assert isinstance(proof, dict)
    for role, expected in (("failure", FAILURE), ("observation", OBSERVATION)):
        owner = proof.get(role)
        base.need(
            type(owner) is dict
            and owner.get("path") == expected[0]
            and owner.get("sha256") == expected[1]
            and owner.get("bytes") == expected[2]
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "authenticate the one private actual Rust " + role + " owner",
        )
    validate_failure(base, proof.get("complete_actual_failure"))
    validate_observation(base, proof.get("complete_independent_observation"))
    base.need(
        proof.get("schema") == SCHEMA + "-authenticated-real-rust-preflight-failure"
        and proof.get("status") == "FAIL"
        and proof.get("actual_controller_process_count") == 1
        and proof.get("actual_rust_candidate_workers") == 0
        and proof.get("actual_rust_native_activations") == 0
        and proof.get("actual_source_build_archive_read_count") == 1
        and proof.get("actual_source_build_archive_gzip_inflation_count") == 1
        and proof.get("actual_matching_archive_read_count") == 0
        and proof.get("actual_reference_archive_read_count") == 0
        and proof.get("controller_failure_ledger_omits_build_archive_effect")
        is True
        and proof.get("actual_rust_semantic_mismatch_count") == "NOT MEASURED"
        and proof.get("actually_runnable_candidate_family_count") == 0
        and proof.get("candidate_qualified") is False
        and proof.get("performance") == "NOT MEASURED"
        and proof.get("holdout") == "NOT OPENED",
        "reject invented worker runs, missing build effects or a Rust pass",
    )
    binding = base.digest(base.canonical({
        "failure": proof["failure"],
        "observation": proof["observation"],
        "complete_actual_failure": proof["complete_actual_failure"],
        "complete_independent_observation":
            proof["complete_independent_observation"],
    }))
    base.need(proof.get("complete_actual_failure_binding_sha256") == binding,
              "bind all actual failure and independent observation bytes")


def make_failure_proof(base: types.ModuleType, failure_owner: dict,
                       failure: dict, observation_owner: dict,
                       observation: dict) -> dict:
    proof = {
        "schema": SCHEMA + "-authenticated-real-rust-preflight-failure",
        "status": "FAIL",
        "failure": failure_owner,
        "observation": observation_owner,
        "complete_actual_failure": failure,
        "complete_independent_observation": observation,
        "actual_controller_process_count": 1,
        "actual_rust_candidate_workers": 0,
        "actual_rust_native_activations": 0,
        "actual_source_build_archive_read_count": 1,
        "actual_source_build_archive_gzip_inflation_count": 1,
        "actual_matching_archive_read_count": 0,
        "actual_reference_archive_read_count": 0,
        "controller_failure_ledger_omits_build_archive_effect": True,
        "actual_rust_semantic_mismatch_count": "NOT MEASURED",
        "actually_runnable_candidate_family_count": 0,
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_actual_failure_binding_sha256"] = base.digest(
        base.canonical({
            "failure": failure_owner,
            "observation": observation_owner,
            "complete_actual_failure": failure,
            "complete_independent_observation": observation,
        })
    )
    validate_failure_proof(base, proof)
    return proof


def authenticate_failure(base: types.ModuleType, supplied_failure: str,
                         supplied_observation: str) -> dict:
    base.need(ACTUAL_FAILURE_PINS_RELEASED is True,
              "block V43 until both independently observed failure owners")
    base.need(base.checked(supplied_failure, "exact actual Rust failure")
              == FAILURE[1],
              "reject a substituted or guessed actual Rust failure")
    base.need(base.checked(supplied_observation, "exact independent observation")
              == OBSERVATION[1],
              "reject a missing observed omitted source-build archive effect")
    failure_raw, failure_owner = base.read_owner(*FAILURE, private=True)
    observation_raw, observation_owner = base.read_owner(*OBSERVATION,
                                                         private=True)
    failure = base.document(failure_raw, "complete actual Rust controller stdout")
    observation = base.document(
        observation_raw,
        "complete original-byte independently observed actual build effect",
        exact=False,
    )
    return make_failure_proof(
        base, failure_owner, failure, observation_owner, observation,
    )


def actual_fields(proof: dict) -> dict:
    return {
        "actual_rust_preflight_failure": copy.deepcopy(proof),
        "actual_rust_controller_status": "FAIL",
        "actual_rust_controller_process_count": 1,
        "actual_rust_failure_class":
            "PRE-ACTIVATION HISTORICAL HELPER FINGERPRINT MISMATCH",
        "actual_rust_error_type": "CampaignError",
        "actual_rust_error_message": ERROR_MESSAGE,
        "actual_rust_attempted_suite_count": 0,
        "actual_rust_started_suite_count": 0,
        "actual_rust_completed_suite_count": 0,
        "actual_rust_candidate_workers": 0,
        "actual_rust_worker_process_ids": [],
        "actual_rust_native_activations": 0,
        "actual_rust_source_build_archive_read_count": 1,
        "actual_rust_source_build_archive_gzip_inflation_count": 1,
        "actual_rust_source_build_archive_compressed_bytes": BUILD_ARCHIVE[2],
        "actual_rust_source_build_archive_uncompressed_bytes":
            BUILD_PLAIN_BYTES,
        "actual_rust_source_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_rust_source_build_archive_uncompressed_sha256":
            BUILD_PLAIN_SHA,
        "actual_rust_controller_ledger_omits_source_build_archive_effect": True,
        "actual_rust_matching_archive_read_count": 0,
        "actual_rust_reference_archive_read_count": 0,
        "actual_rust_semantic_mismatch_count": "NOT MEASURED",
        "actual_rust_candidate_qualified": False,
        "actual_rust_failure_evidence_sha256": FAILURE[1],
        "actual_rust_observed_effects_sha256": OBSERVATION[1],
        "corrected_rust_matching_status": "NOT RUN",
        "corrected_rust_candidate_workers_started": 0,
        "corrected_rust_candidate_qualified": False,
        "corrected_rust_matching_mismatch_reduction": "NOT MEASURED",
        "corrected_rust_matching_speedup": "NOT MEASURED",
        "corrected_c_matching_status": "NOT RUN",
        "corrected_c_candidate_workers_started": 0,
        "corrected_c_candidate_qualified": False,
        "frozen_corrected_runner_source_family_count": 2,
        "frozen_corrected_runner_source_families": ["c", "rust"],
        "dedicated_corrected_runnable_family_count": 0,
        "dedicated_corrected_runnable_families": [],
        "actually_runnable_candidate_family_count": 0,
        "actually_runnable_candidate_families": [],
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 4,
        "other_corrected_candidate_matching_status": "NOT RUN",
        "pending_corrected_candidate_families":
            ["zig", "cpp", "go", "fortran"],
        "candidate_case_producer_status":
            "V4 SOURCE FROZEN; RUST PREFLIGHT FAIL; ZERO RUNNABLE CANDIDATES",
        "candidate_matching_block_reason": BLOCK_REASON,
        "all_candidate_matching_blocked": True,
        "qualified_candidate_count": 0,
        "rust_v6_runner_status":
            "SOURCE FROZEN; NOT RUNNABLE; PREFLIGHT FAILED",
        "rust_v6_actual_runner_status":
            "NOT RUNNABLE; AUTHORIZED PREFLIGHT FAILED",
        "required_corrected_candidate_runner_versions": [],
        "stale_candidate_worker_versions": [],
        "historical_v42_dedicated_runner_source_family_count": 2,
        "historical_v42_dedicated_runner_source_families": ["c", "rust"],
        "historical_evidence_owner_lower_bound_before_actual_failure": 164,
        "historical_reference_lower_bound_before_actual_failure": 169,
        "new_actual_failure_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "all_digest_addressed_history_path_count": 171,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def project_v42_snapshot(previous: types.ModuleType,
                         snapshot: dict) -> dict:
    historical = copy.deepcopy(snapshot)
    rust = historical.get("corrected_rust_only_runner_v6")
    assert isinstance(rust, dict)
    for key, value in previous.dual_runner_fields(rust).items():
        historical[key] = copy.deepcopy(value)
    historical["authenticated_evidence_owner_lower_bound"] = 164
    historical["authenticated_history_reference_lower_bound"] = 169
    historical["all_digest_addressed_history_path_count"] = 169
    historical["reference_archive_gzip_inflation_count"] = 1
    return historical


def validate_snapshot(previous: types.ModuleType, v41: types.ModuleType,
                      v40: types.ModuleType, base: types.ModuleType,
                      snapshot: object) -> None:
    base.need(type(snapshot) is dict,
              "reject a missing actual-failure and zero-runnable V43 snapshot")
    assert isinstance(snapshot, dict)
    previous.validate_snapshot(
        v41, v40, base, project_v42_snapshot(previous, snapshot),
    )
    proof = snapshot.get("actual_rust_preflight_failure")
    validate_failure_proof(base, proof)
    assert isinstance(proof, dict)
    for key, value in actual_fields(proof).items():
        base.need(snapshot.get(key) == value,
                  "reject an invented or omitted actual Rust effect: " + key)
    base.need(
        snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("corrected_reference_actual_worker_count") == 2
        and snapshot.get("corrected_reference_process_ids") == [81, 82]
        and snapshot.get("zig_scanner_phrase_prospective_case_count") == 64
        and snapshot.get("zig_scanner_phrase_correction_applied") is False
        and snapshot.get("zig_scanner_phrase_corrected_matching_status")
        == "NOT RUN",
        "retain every real original case, Python reference and unapplied Zig fix",
    )


def replace_once(base: types.ModuleType, visible: str,
                 before: str, after: str, label: str) -> str:
    base.need(visible.count(before) == 1,
              "reject a missing or duplicated inherited V42 graph claim: " + label)
    return visible.replace(before, after, 1)


def make_svg(previous: types.ModuleType, v41: types.ModuleType,
             v40: types.ModuleType, base: types.ModuleType,
             snapshot: dict, source: str, inputs: str) -> bytes:
    validate_snapshot(previous, v41, v40, base, snapshot)
    old = project_v42_snapshot(previous, snapshot)
    visible = previous.make_svg(v41, v40, base, old, source, inputs).decode("utf-8")
    visible = visible.replace("v42-title", "v43-title")
    visible = visible.replace("v42-description", "v43-description")
    replacements = (
        (
            "baseline passes; separate C and Rust runners are frozen, untested</title>",
            "baseline passes; Rust preflight fails before any candidate test</title>",
            "actual failure title",
        ),
        (
            "Separate C-only V8/V10 and Rust-only V6 runners are source frozen. "
            "Neither complete candidate test has been run; Zig, Go, C++ and "
            "Fortran remain source-only designs.",
            "C and Rust have frozen runner sources but zero candidates are "
            "actually runnable. One real Rust controller failed its historical "
            "helper check before activating a candidate or starting a test; "
            "C, Zig, Go, C++ and Fortran remain untested.",
            "complete actual failure description",
        ),
        (
            "Six first-party source designs; separate C and Rust test runners "
            "are frozen, not tested.",
            "Six first-party source designs; two frozen runner sources; "
            "zero actually runnable replacements.",
            "source versus genuinely runnable headline",
        ),
        (
            "C AND RUST RUNNERS FROZEN — NEITHER COMPLETE MATCHING TEST HAS RUN",
            "RUST PREFLIGHT FAILED — ZERO CANDIDATE TEST WORKERS STARTED",
            "genuine pre-activation controller failure",
        ),
        (
            "C and Rust each have a separately frozen first-party test runner; "
            "neither 31,237-case matching campaign has run.",
            "The actual Rust controller failed before any of the 31,237 "
            "compatibility tests. C matching has not run.",
            "actual zero original suite execution",
        ),
        (
            "SEPARATE C AND RUST TEST RUNNERS FROZEN; BOTH FULL MATCHING "
            "CAMPAIGNS NOT RUN",
            "RUST SOURCE RUNNER FAILED BEFORE ACTIVATION; "
            "ZERO CANDIDATES RUNNABLE",
            "source-freeze is not runnable status",
        ),
        (
            "Two dedicated first-party runner paths; six source designs; "
            "zero qualified replacements. No compatibility or speed result "
            "has been measured.",
            "Two frozen first-party runner sources; six source designs; "
            "zero runnable or qualified replacements. Rust matching and "
            "speed are not measured.",
            "honest frozen source inventory",
        ),
        (
            "Six first-party engines are source designs, not six runnable or "
            "passing replacements. The separate C and Rust runners have not "
            "been used.",
            "One real Rust preflight failed. C remains untested; the other "
            "four remain source-only. No matching worker started.",
            "actual single controller versus matching workers",
        ),
        (
            '<text x="1028" y="670" class="big">0</text>',
            '<text x="1028" y="670" class="big">1</text>',
            "actual authorized Rust controller count",
        ),
        (
            "new replacement runs</text>",
            "failed Rust preflights</text>",
            "one attempt is not a matching run",
        ),
        (
            "≥164 / 169",
            "≥166 / 171",
            "two individually authenticated actual failure owners",
        ),
        (
            "1. Overall: the baseline passes; every replacement still waits",
            "1. Overall: Rust preflight failed; no replacement is runnable",
            "lay-readable actual candidate state",
        ),
        (
            "Rust — previously tested version",
            "Rust — actual preflight failed; historical failures preserved",
            "distinguish the new Rust failure from old matching",
        ),
        (
            '<text x="1367" y="893" class="fail" text-anchor="end">'
            'HISTORICAL FAILURE; NEW RUN BLOCKED</text>',
            '<text x="1367" y="893" class="fail" text-anchor="end">'
            'PREFLIGHT FAILED; ZERO TEST WORKERS</text>',
            "actual Rust infrastructure failure",
        ),
        (
            "1,036 historical differences; 8,965 historical passes",
            "0 new workers; current differences NOT MEASURED; "
            "old 1,036 differences / 8,965 passes",
            "preserve old Rust losses without inventing new mismatches",
        ),
        (
            "V4 plus separate C-only V8/V10 and Rust-only V6 runner sources "
            "are frozen.",
            "Two runner sources are frozen, but Rust preflight failed and "
            "zero candidates are runnable.",
            "frozen-source-only machine semantics",
        ),
        (
            "C and Rust matching NOT RUN; Zig, Go, C++ and Fortran runners "
            "NOT FROZEN.",
            "Rust matching NOT RUN after preflight failure; C NOT RUN; "
            "four other runners NOT FROZEN.",
            "all six honest current family outcomes",
        ),
        (
            "Two genuine new evidence owners raise authenticated lower bounds "
            "from 162/167 to at least 164/169.",
            "Two new exact failure-observation owners raise the authenticated "
            "lower bounds from 164/169 to at least 166/171.",
            "exact lower bounds without an invented repository census",
        ),
    )
    for before, after, label in replacements:
        visible = replace_once(base, visible, before, after, label)
    visible = replace_once(
        base, visible,
        'height="2260" viewBox="0 0 1440 2260"',
        'height="2370" viewBox="0 0 1440 2370"',
        "complete visible failure observation",
    )
    lines = [previous.move_y(line, 110) for line in visible.splitlines()]
    index = next(
        position + 1 for position, line in enumerate(lines)
        if "C matching has not run." in line
    )
    lines[index:index] = [
        '<rect x="44" y="302" width="1352" height="91" rx="14" '
        'fill="#fff1ed" stroke="#e6b3a6"/>',
        '<text x="65" y="337" class="warning">ONE HISTORICAL BUILD ARCHIVE '
        'WAS READ; THE RUST FAILURE LEDGER OMITTED THAT EFFECT</text>',
        '<text x="67" y="365" class="body">Actual build: 108,985 compressed '
        'bytes → 760,477 verified bytes. Matching/reference archives: 0. '
        'Candidate workers: 0.</text>',
    ]
    image = ("\n".join(lines) + "\n").encode("utf-8")
    for phrase in (
        b"rust preflight fail", b"zero candidate",
        b"zero actually runnable", b"zero runnable",
        b"two frozen", b"six source designs",
        b"ledger omitted", b"108,985", b"760,477",
        b"matching/reference archives: 0",
        b"candidate workers: 0", b"not measured",
        b"31,237", b"96 / 96", b"1,036",
        b"8,965", b"1,230", b"7,325",
        b"1,764", b"3,711", b"64 of 1,024",
        b"not applied or tested", b"4,194,304",
        b"not opened", b"166 / 171",
    ):
        base.need(phrase.lower() in image.lower(),
                  "reject an omitted actual Rust failure claim: " + repr(phrase))
    for stale in (
        b"two dedicated first-party runner paths",
        b"two runnable replacements",
        b"2 runnable candidates",
        b"rust matching pass",
        b"rust matching passed",
        b"rust candidate qualified",
        b"neither complete candidate test has been run",
        b"the separate c and rust runners have not been used",
        b"both full matching campaigns not run",
        b"all archives read: 0",
    ):
        base.need(stale not in image.lower(),
                  "reject an inherited or invented V43 candidate claim")
    base.need(image.endswith(b"\n") and not image.endswith(b"\n\n"),
              "render exactly one final V43 image linefeed")
    return image


def build(previous: types.ModuleType, v41: types.ModuleType,
          v40: types.ModuleType, base: types.ModuleType,
          source_sha: str, source_bytes: int,
          failure_sha: str, observation_sha: str
          ) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    base.need(ACTUAL_FAILURE_PINS_RELEASED is True,
              "require independently released genuine actual failure owners")
    source_sha = base.checked(source_sha, "exact final V43 graph source")
    base.need(type(source_bytes) is int
              and 0 < source_bytes <= base.OWNER_LIMIT,
              "require the exact independently supplied V43 renderer size")
    own_raw, _ = base.read_owner(SELF, source_sha, source_bytes, private=True)
    old, old_inputs = authenticate_v42(previous, v41, v40, base)
    proof = authenticate_failure(base, failure_sha, observation_sha)
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(actual_fields(proof))
    validate_snapshot(previous, v41, v40, base, snapshot)
    predecessors = {
        role: base.pin(*owner) for role, owner in V42.items()
    }
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 43,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **actual_fields(proof),
    })
    inputs_raw = base.canonical(inputs)
    svg = make_svg(
        previous, v41, v40, base, snapshot,
        source_sha, base.digest(inputs_raw),
    )
    families = copy.deepcopy(old["families"])
    current_policy = {
        key: copy.deepcopy(snapshot[key])
        for key in (
            "frozen_corrected_runner_source_family_count",
            "frozen_corrected_runner_source_families",
            "dedicated_corrected_runnable_family_count",
            "dedicated_corrected_runnable_families",
            "actually_runnable_candidate_family_count",
            "actually_runnable_candidate_families",
            "first_party_source_inventory_family_count",
            "other_corrected_candidate_family_count",
            "other_corrected_candidate_matching_status",
            "pending_corrected_candidate_families",
            "candidate_case_producer_status",
            "candidate_matching_block_reason",
            "all_candidate_matching_blocked",
            "qualified_candidate_count",
            "corrected_c_matching_status",
            "corrected_rust_matching_status",
            "rust_v6_runner_status",
            "required_corrected_candidate_runner_versions",
            "stale_candidate_worker_versions",
            "runtime_no_delegation",
            "performance",
        )
    }
    for family in families:
        name = family.get("family")
        if name == "python":
            continue
        family.update(copy.deepcopy(current_policy))
        family.update({
            "candidate_run_under_corrected_reference": "NOT RUN",
            "qualified": False,
            "matching_blocked_pending_corrected_v4_producer": False,
            "matching_paused_for_reference_falsification": False,
        })
        if name == "rust":
            family.update({
                "corrected_runner_status":
                    "SOURCE FROZEN; NOT RUNNABLE; PREFLIGHT FAILED",
                "matching_block_reason": BLOCK_REASON,
                "matching_blocked_pending_corrected_candidate_runners": True,
                "actual_preflight_status": "FAIL",
                "actual_controller_process_count": 1,
                "actual_candidate_workers": 0,
                "actual_native_activations": 0,
                "actual_semantic_mismatch_count": "NOT MEASURED",
                "actual_source_build_archive_read_count": 1,
                "actual_source_build_archive_gzip_inflation_count": 1,
                "actual_controller_ledger_omits_source_build_archive_effect":
                    True,
                "actual_matching_archive_read_count": 0,
                "actual_reference_archive_read_count": 0,
                "actual_rust_preflight_failure": copy.deepcopy(proof),
            })
        elif name == "c":
            family.update({
                "corrected_runner_status":
                    "SOURCE FROZEN; NOT RUNNABLE; C MATCHING NOT RUN",
                "matching_block_reason":
                    "The C runner source is frozen but its original native "
                    "target is restored, activation is not committed, and "
                    "no C candidate worker has run.",
                "matching_blocked_pending_corrected_candidate_runners": True,
                "actual_candidate_workers": 0,
                "actual_native_activations": 0,
            })
        else:
            family.update({
                "corrected_runner_status": "NOT FROZEN; NOT RUNNABLE",
                "matching_block_reason":
                    "This first-party source design has no committed runnable "
                    "corrected runner and no candidate matching has run.",
                "matching_blocked_pending_corrected_candidate_runners": True,
                "actual_candidate_workers": 0,
                "actual_native_activations": 0,
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 43,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json",
            base.digest(inputs_raw), len(inputs_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessors,
        "snapshot": snapshot,
        "families": families,
        **actual_fields(proof),
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", inputs_raw),
        (OUTPUT + ".json", base.canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


def synthetic_failure() -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v6-entry-failure",
        "status": "FAIL",
        "family": "rust",
        "effect_ledger_schema":
            "rebar-owned-repaired-rust-original-campaign-v6-"
            "authorized-run-actual-effect-ledger",
        "campaign_mode": "AUTHORIZED RUN",
        "campaign_source_sha256": RUST["source"][1],
        "campaign_protocol_sha256": RUST["protocol"][1],
        "campaign_contract_sha256": RUST["contract"][1],
        "error_type": "CampaignError",
        "error_message": ERROR_MESSAGE,
        "case_execution_denominator": 31237,
        "suite_count": 13,
        **{
            name: 0 for name in (
                "attempted_suite_count", "started_suite_count",
                "fully_observed_suite_count", "actual_candidate_workers",
                "actual_native_activations", "actual_reference_workers",
                "actual_source_builds", "canonical_target_read_lower_bound",
                "canonical_target_replacements", "recovery_roots_created",
                "recovery_locks_acquired", "recovery_journals_created",
                "hidden_cases_read", "benchmark_files_read", "clock_samples",
                "timing_trials_run",
            )
        },
        **{
            name: [] for name in (
                "activated_target_roles", "actual_worker_process_ids",
                "restored_target_roles", "retained_suite_results",
                "worker_attempts",
            )
        },
        **{
            name: False for name in (
                "all_four_original_targets_restored",
                "all_original_observation_vectors_complete",
                "archive_publication_attempted", "bounded_report_attempted",
                "candidate_qualified", "original_case_archive_durably_published",
                "publication_attempted", "receipt_publication_attempted",
                "recovery_journal_announced",
                "recovery_journal_creation_attempted",
                "recovery_lock_attempted", "recovery_root_creation_attempted",
                "restoration_attempted", "restoration_verified",
                "source_only_zero_effects_claimed", "winner_selected",
            )
        },
        **{
            name: None for name in (
                "archive_owner", "receipt_owner",
                "publication_failure", "recovery_journal_sha256",
            )
        },
        **{
            name: "NOT ATTEMPTED" for name in (
                "archive_publication_status", "receipt_publication_status",
                "publication_status",
            )
        },
        **{
            name: "NOT MEASURED" for name in (
                "semantic_mismatch_count", "canonical_target_reads",
                "canonical_target_stats", "performance",
                "memory", "undefined_behavior",
            )
        },
        "traceback": [
            "Traceback (most recent call last):\n",
            '  File "synthetic-v43", line 6786, in run_campaign\n',
            '  File "synthetic-v43", line 4894, in patched_v2_helpers\n',
            "CampaignError: " + ERROR_MESSAGE + "\n",
        ],
        "holdout": "NOT OPENED",
        "actual_evidence_owner_count_before_new_campaign": 164,
        "actual_authenticated_reference_count_before_new_campaign": 169,
    }


def synthetic_observation(base: types.ModuleType) -> dict:
    return {
        "schema":
            "rebar-owned-repaired-rust-original-campaign-v6-"
            "entry-failure-independent-observation-v1",
        "observation_status":
            "PASS; FAILURE AND OMITTED SOURCE-BUILD EFFECT PRESERVED",
        "published_predecessor": {
            "commit": "2a85610e",
            "overview_version": 42,
            "overview_summary_sha256": V42["summary"][1],
        },
        "actual_invocation": {
            "count": 1,
            "mode": "AUTHORIZED RUN",
            "family": "rust",
            "exit_code": 1,
            "source_sha256": RUST["source"][1],
            "protocol_sha256": RUST["protocol"][1],
            "contract_sha256": RUST["contract"][1],
            "stdout": base.pin(*FAILURE),
            "error_type": "CampaignError",
            "error_message": ERROR_MESSAGE,
        },
        "root_cause": {
            "kind": "IMMUTABLE HISTORICAL HELPER ADAPTER FINGERPRINT MISMATCH",
            "helper_source": base.pin(*HELPER),
            "actual_v2_repaired_adapter": {
                **base.pin(*ACTUAL_V2_ADAPTER),
                "identity": "historical V2 source-owner tuple, not a current target read",
            },
            "incorrect_v6_expected_historical_adapter_sha256":
                WRONG_EXPECTED_ADAPTER,
            "failed_function": "patched_v2_helpers",
            "failed_condition":
                "v2.REPAIRED_SOURCE_OWNERS[0][1] == "
                "HISTORICAL_DERIVED_PUBLIC_SHA256",
        },
        "source_build_archive_effect": {
            "observation_basis":
                "Digest-authenticated frozen V6 call order: run_campaign "
                "verifies retained V13 context and inflates the source-build "
                "archive before patched_v2_helpers raises.",
            "controller_failure_ledger_records_effect": False,
            "archive_read_count": 1,
            "gzip_inflation_count": 1,
            "archive": {
                "path": BUILD_ARCHIVE[0],
                "sha256": BUILD_ARCHIVE[1],
                "compressed_bytes": BUILD_ARCHIVE[2],
                "uncompressed_sha256": BUILD_PLAIN_SHA,
                "uncompressed_bytes": BUILD_PLAIN_BYTES,
            },
            "matching_archive_read_count": 0,
            "reference_archive_read_count": 0,
            "nested_matching_archive_read_count": 0,
        },
        "actual_candidate_effects": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "attempted_suite_count": 0,
            "started_suite_count": 0,
            "fully_observed_suite_count": 0,
            "candidate_workers": 0,
            "reference_workers": 0,
            "native_activations": 0,
            "recovery_roots_created": 0,
            "recovery_journals_created": 0,
            "archive_publication_status": "NOT ATTEMPTED",
            "receipt_publication_status": "NOT ATTEMPTED",
            "semantic_mismatch_count": "NOT MEASURED",
            "candidate_qualified": False,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
        },
    }


def forged_value(base: types.ModuleType, value: object) -> object:
    candidate = base.forged(value)
    if candidate == value and type(value) is list:
        return ["forged-v43"]
    if candidate == value and type(value) is dict:
        return {"forged-v43": True}
    return candidate


def self_test(previous: types.ModuleType, v41: types.ModuleType,
              v40: types.ModuleType, base: types.ModuleType) -> dict:
    historical = previous.self_test(v41, v40, base)
    base.need(
        historical.get("status") == "PASS"
        and historical.get("reference_archive_gzip_inflation_count") == 0
        and historical.get("matching_archive_gzip_inflation_count") == 0,
        "first authenticate all source-only V42/V41/V40/V39 physical walls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        failure = synthetic_failure()
        observation = synthetic_observation(base)
        failure_owner = base.synthetic_owner(FAILURE, 943001)
        observation_owner = base.synthetic_owner(OBSERVATION, 943002)
        proof = make_failure_proof(
            base, failure_owner, failure, observation_owner, observation,
        )
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = forged_value(base, value)
            try:
                validate_failure_proof(base, hostile)
            except (base.GraphError, TypeError, ValueError,
                    AttributeError, KeyError):
                rejected += 1
            else:
                raise base.GraphError("accepted a forged real Rust proof: " + key)
        for role in ("failure", "observation"):
            for key, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][key] = forged_value(base, value)
                try:
                    validate_failure_proof(base, hostile)
                except (base.GraphError, TypeError, ValueError,
                        AttributeError, KeyError):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a substituted Rust " + role + " owner",
                    )
        for group in ("complete_actual_failure",
                      "complete_independent_observation"):
            for key, value in proof[group].items():
                hostile = copy.deepcopy(proof)
                hostile[group][key] = forged_value(base, value)
                try:
                    validate_failure_proof(base, hostile)
                except (base.GraphError, TypeError, ValueError,
                        AttributeError, KeyError):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a forged genuine Rust failure field: " + key,
                    )
        for group in (
            "published_predecessor", "actual_invocation", "root_cause",
            "source_build_archive_effect", "actual_candidate_effects",
        ):
            for key, value in observation[group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_observation"][group][key] = (
                    forged_value(base, value)
                )
                try:
                    validate_failure_proof(base, hostile)
                except (base.GraphError, TypeError, ValueError,
                        AttributeError, KeyError):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a hidden actual Rust " + group + " effect",
                    )
        for group, name in (
            ("actual_invocation", "stdout"),
            ("root_cause", "helper_source"),
            ("root_cause", "actual_v2_repaired_adapter"),
            ("source_build_archive_effect", "archive"),
        ):
            nested = observation[group][name]
            for key, value in nested.items():
                hostile = copy.deepcopy(proof)
                hostile["complete_independent_observation"][group][name][key] = (
                    forged_value(base, value)
                )
                try:
                    validate_failure_proof(base, hostile)
                except (base.GraphError, TypeError, ValueError,
                        AttributeError, KeyError):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a forged actual V43 archive or adapter owner",
                    )
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v43")),
            ("filesystem", lambda: os.open("forbidden-v43", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v43")),
            ("write", lambda: os.mkdir("forbidden-v43")),
            ("process", lambda: subprocess.run(("forbidden-v43",))),
            ("process", lambda: subprocess.Popen(("forbidden-v43",))),
            ("process", lambda: os.execv("/forbidden-v43", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically block real V43 source-only " + kind)
            else:
                raise base.GraphError("a V43 synthetic source effect escaped")
        base.need(rejected >= 100,
                  "reject all forged actual failure, worker and archive claims")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 43,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v42_hostile_controls":
                historical["rejected_hostile_control_count"],
            "actual_failure_hostile_controls": rejected,
            "rejected_hostile_control_count":
                historical["rejected_hostile_control_count"] + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_evidence_read_by_self_test": 0,
            "actual_observation_evidence_read_by_self_test": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "candidate_matching_archives_opened_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "frozen_corrected_runner_source_family_count": 2,
            "frozen_corrected_runner_source_families": ["c", "rust"],
            "actually_runnable_candidate_family_count": 0,
            "dedicated_corrected_runnable_family_count": 0,
            "actual_rust_controller_status": "FAIL",
            "actual_rust_controller_process_count": 1,
            "actual_rust_candidate_workers": 0,
            "actual_rust_source_build_archive_read_count": 1,
            "actual_rust_controller_ledger_omits_source_build_archive_effect":
                True,
            "actual_rust_matching_archive_read_count": 0,
            "actual_rust_reference_archive_read_count": 0,
            "actual_rust_semantic_mismatch_count": "NOT MEASURED",
            "corrected_c_matching_status": "NOT RUN",
            "corrected_rust_matching_status": "NOT RUN",
            "qualified_candidate_count": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    base.need(
        ACTUAL_FAILURE_PINS_RELEASED is True
        and path in allowed and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only the three newly authorized actual-failure V43 graph files",
    )
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete actual-failure graph publication")
            remaining = remaining[count:]
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        base.need(
            owner.st_uid == os.geteuid() and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "publish only one uniquely owned exact actual-failure graph",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "independently preserve the exact V43 graph bytes")


def result(base: types.ModuleType, snapshot: dict,
           outputs: dict[str, bytes], source: str,
           *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 43,
        "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 42,
        **{
            "previous_overview_" + role + "_sha256": owner[1]
            for role, owner in V42.items()
        },
        "actual_failure_sha256": FAILURE[1],
        "actual_observation_sha256": OBSERVATION[1],
        "outputs_written": written,
        "failure_evidence_owners_authenticated_by_graph": 2,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_controller_status": "FAIL",
        "actual_controller_process_count": 1,
        "actual_candidate_workers": 0,
        "actual_source_build_archive_read_count": 1,
        "actual_source_build_archive_gzip_inflation_count": 1,
        "actual_source_build_archive_compressed_bytes": BUILD_ARCHIVE[2],
        "actual_source_build_archive_uncompressed_bytes": BUILD_PLAIN_BYTES,
        "actual_controller_ledger_omits_source_build_archive_effect": True,
        "actual_matching_archive_read_count": 0,
        "actual_reference_archive_read_count": 0,
        **{
            key: copy.deepcopy(snapshot[key])
            for key in (
                "frozen_corrected_runner_source_family_count",
                "frozen_corrected_runner_source_families",
                "actually_runnable_candidate_family_count",
                "actually_runnable_candidate_families",
                "dedicated_corrected_runnable_family_count",
                "dedicated_corrected_runnable_families",
                "first_party_source_inventory_family_count",
                "other_corrected_candidate_family_count",
                "pending_corrected_candidate_families",
                "corrected_c_matching_status",
                "corrected_rust_matching_status",
                "actual_rust_error_type",
                "actual_rust_error_message",
                "actual_rust_attempted_suite_count",
                "actual_rust_started_suite_count",
                "actual_rust_completed_suite_count",
                "actual_rust_semantic_mismatch_count",
                "qualified_candidate_count",
                "authenticated_evidence_owner_lower_bound",
                "authenticated_history_reference_lower_bound",
                "exact_whole_repository_evidence_owner_count",
                "exact_whole_repository_reference_count",
                "full_case_denominator",
                "suite_count",
                "private_waiver_count",
                "hidden_cases_read",
                "clock_samples",
                "timing_trials_run",
                "runtime_no_delegation",
                "performance",
                "memory",
                "confidence_intervals",
                "undefined_behavior",
                "final_comparison_planned_case_count",
                "final_comparison_cases_generated",
                "final_holdout_opened",
                "winner_selected",
            )
        },
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--failure-sha256")
    parser.add_argument("--observation-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v41, v40, base = load_v42()
        if options.self_test:
            base.need(
                all(
                    getattr(options, key) is None
                    for key in (
                        "source_sha256", "source_bytes",
                        "failure_sha256", "observation_sha256",
                        "inputs_sha256", "summary_sha256", "svg_sha256",
                    )
                ),
                "synthetic source gates never accept a real failure or graph pin",
            )
            sys.stdout.buffer.write(
                base.canonical(self_test(previous, v41, v40, base)),
            )
            return 0
        base.need(ACTUAL_FAILURE_PINS_RELEASED is True,
                  "block real graph work without both independent failure pins")
        source = base.checked(options.source_sha256, "exact final V43 renderer")
        failure = base.checked(options.failure_sha256, "actual Rust stdout owner")
        observation = base.checked(
            options.observation_sha256,
            "independent actual omitted build-effect owner",
        )
        snapshot, pairs = build(
            previous, v41, v40, base,
            source, options.source_bytes, failure, observation,
        )
        outputs = dict(pairs)
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "render only three genuinely new actual-failure graph owners",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source,
                written=True, suffix="-published",
            )))
            return 0
        expected = {
            OUTPUT + ".inputs.json":
                base.checked(options.inputs_sha256, "exact V43 inputs"),
            OUTPUT + ".json":
                base.checked(options.summary_sha256, "exact V43 summary"),
            OUTPUT + ".svg":
                base.checked(options.svg_sha256, "exact V43 visible graph"),
        }
        for path, fingerprint in expected.items():
            observed, _ = base.read_owner(
                path, fingerprint, len(outputs[path]), private=True,
            )
            base.need(
                observed == outputs[path],
                "independently reproduce every actual-failure graph byte",
            )
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError,
    ) as error:
        sys.stderr.write("current V43 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write(
                "current V43 overview rejected: " + str(error) + "\n",
            )
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
