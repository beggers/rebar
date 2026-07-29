#!/usr/bin/env python3
"""Show a real Rust build and a separately frozen, still-unrun full-suite test."""

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
SELF = "tools/render_candidate_current_overview_v57.py"
OUTPUT = "docs/evidence/candidate-current-overview-v57"
SCHEMA = "rebar-candidate-current-overview-v57"
V56 = {
    "source": (
        "tools/render_candidate_current_overview_v56.py",
        "991dee73be4c847eab8ebeaf27e04992d38310e8b0bcb97b4a6405ccc149b8a2",
        100748,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v56.inputs.json",
        "63446b32a01b2a731ed8f6ddf4ffbb7077fa1bc1ede3ad081012ba7a0611b554",
        678752,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v56.json",
        "cceb572a6daf4683fd01bd758cbc4206b2dfc5b5eb8f5c45bd2de07b9934c1fe",
        1882551,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v56.svg",
        "7ea80defb808389c1b00f58731e0b74b3958c72e2814368d94b9ef44e6a1a5b1",
        14225,
    ),
}


V10 = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v10.py",
        "038870e88e9dfbe2f9d97892fb98558787d1142bb94559e3060023c8e562a81c",
        211733,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V10.md",
        "cf425c2517f7fa066a30a340b830d8782e0000872efa3eaf00c764ce45ef0659",
        16618,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v10.json",
        "57c36f414d052e798fc1f9ccfcd10aeddd5f6571d95679a995c6935d86f3dda7",
        17426,
    ),
}


V10_CONTRACT_SCHEMA = "rebar-owned-repaired-rust-original-campaign-v10-recoverable-source-freeze"
V10_CONTRACT_STATUS = "SOURCE FROZEN; CORRECTED RUST V16 CANDIDATE NOT RUN"
V10_CAMPAIGN_LABEL = "phase2-v16-rust-buffer-shape-pickle-original-p0-v10"
V10_OVERVIEW_KEY = "current_v56_graph"
SUITE_SIZES = (151, 864, 1024, 768, 1024, 2854, 6912, 5120,
               10240, 1376, 128, 264, 512)
PUBLIC_COUNTS = {
    "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1, "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22, "FAIL": 1, "NOT RUN": 3,
    "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1,
}
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]


def load_v56() -> tuple:
    path, fingerprint, size = V56["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
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
            raise ValueError("reject substituted actual pushed V56 renderer")
        chunks = []
        remaining = size
        while remaining:
            chunk = os.read(descriptor, min(262144, remaining))
            if not chunk:
                raise ValueError("reject truncated actual pushed V56 renderer")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject appended actual pushed V56 renderer")
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (
                before.st_dev, before.st_ino, before.st_size,
                before.st_nlink, before.st_mtime_ns, before.st_ctime_ns,
            ) != (
                after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns, after.st_ctime_ns,
            )
        ):
            raise ValueError("reject changed actual pushed V56 renderer")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_actual_pushed_build_graph_v56")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v55()
    base = prior_modules[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v56"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS,
        "load only the exact complete actual pushed V56 build graph",
    )
    return previous, prior_modules, base


def source_effect_expectations() -> dict:
    return {
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_compiler_processes": 0,
        "actual_native_activations": 0,
        "actual_native_library_loads": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "benchmark_files_read": 0,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "canonical_target_reads": 0,
        "canonical_target_replacements": 0,
        "canonical_target_stats": 0,
        "clock_samples": 0,
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0,
        "historical_build_archive_reads": 0,
        "historical_matching_archive_reads": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "network_requests": 0,
        "performance": "NOT MEASURED",
        "private_build_root_enumerations": 0,
        "private_build_root_reads": 0,
        "recovery_journals_created": 0,
        "recovery_locks_acquired": 0,
        "recovery_roots_created": 0,
        "reference_archive_reads": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "threads_started": 0,
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "v16_build_archive_gzip_inflations": 0,
        "v16_build_archive_reads": 0,
        "winner_selected": False,
        "workspace_mutations": 0,
    }


def validate_pin_reference(base: types.ModuleType, reference: object,
                           item: tuple[str, str, int], description: str) -> None:
    base.need(
        type(reference) is dict
        and reference.get("path") == item[0]
        and reference.get("sha256") == item[1]
        and ("bytes" not in reference or reference.get("bytes") == item[2])
        and ("size_bytes" not in reference
             or reference.get("size_bytes") == item[2]),
        "reject substituted complete V10 reference: " + description,
    )


def validate_owner(base: types.ModuleType, owner: object,
                   item: tuple[str, str, int], description: str) -> None:
    base.need(
        type(owner) is dict
        and owner.get("path") == item[0]
        and owner.get("sha256") == item[1]
        and owner.get("bytes") == item[2]
        and owner.get("device") == 2064
        and type(owner.get("inode")) is int
        and owner["inode"] > 0
        and owner.get("mode") == "0600"
        and owner.get("nlink") == 1
        and owner.get("uid") == os.geteuid(),
        "bind one genuine private independently owned V10 " + description,
    )


def historical_v9_source_expectations() -> dict:
    return {
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actually_attempted_suite_count": 0,
        "additional_private_waivers": 0,
        "archive_inflations_by_v10_source_gate": 0,
        "archive_reads_by_v10_source_gate": 0,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "controller_status": "FAIL",
        "failure_owner": {
            "device": 2064,
            "inode": 525025,
            "path":
                "oracle/phase2/evidence/"
                "repaired-rust-original-campaign-v9-rust-phase2-v16-rust-"
                "buffer-shape-pickle-original-p0-entry-failure.json",
            "sha256":
                "70b9089b16faa499da3688d466d0355b87ca42d0382c9da59e08f063a7990471",
            "size_bytes": 8075,
        },
        "fake_unstarted_retained_suite_row_count": 13,
        "frozen_campaign_contract_sha256":
            "782576f45cbc7bc97775233051d82889778f095a4595e336ec4afb5f2ffc3a82",
        "frozen_campaign_protocol_sha256":
            "9dfec149359a2088e384da1b3b5851fc8ac0c5f6ed8bfdb1414671a7ecbf6850",
        "frozen_campaign_source_sha256":
            "629f6d361e2e3cd2eeb762223076d5511707d52241189fc4bd4c73045bb9287c",
        "historical_archive_inflations_by_authorized_v9_controller": 1,
        "historical_archive_reads_by_authorized_v9_controller": 1,
        "historical_v2_prefix":
            "rebar-phase2-repaired-rust-original-campaign-v2-",
        "historical_v9_failure_root_left_untouched": True,
        "historical_v9_recovery_root":
            "/tmp/rebar-phase2-repaired-rust-original-campaign-v9-"
            "phase2-v16-rust-buffer-shape-pickle-original-p0",
        "holdout": "NOT OPENED",
        "independent_observation_owner": {
            "device": 2064,
            "inode": 525026,
            "path":
                "oracle/phase2/evidence/"
                "repaired-rust-original-campaign-v9-rust-phase2-v16-rust-"
                "buffer-shape-pickle-original-p0-entry-failure-observation.json",
            "sha256":
                "687d401e1112218de26e5dd0525e8c60cb79b5f4b204272cd8c91b83182eb3f6",
            "size_bytes": 15992,
        },
        "memory": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "recovery_journals_created": 0,
        "recovery_lock_attempts": 0,
        "recovery_locks_acquired": 0,
        "recovery_roots_created": 1,
        "started_suite_count": 0,
        "target_replacements": 0,
        "v10_fabricates_preactivation_suite_rows": False,
        "v10_preserves_original_preactivation_exception": True,
        "v10_rebind_occurs_before_first_mkdir": True,
        "versioned_v10_recovery_prefix":
            "rebar-phase2-repaired-rust-original-campaign-v10-",
        "winner_selected": False,
        "withdrawn_original_cases": 0,
    }


def validate_v10_contract(base: types.ModuleType, contract: object) -> None:
    base.need(type(contract) is dict,
              "reject missing complete frozen V10 runner machine contract")
    assert isinstance(contract, dict)
    base.need(
        contract.get("schema") == V10_CONTRACT_SCHEMA
        and contract.get("version") == 10
        and contract.get("status") == V10_CONTRACT_STATUS
        and contract.get("family") == "rust"
        and contract.get("campaign_label", contract.get("label"))
        == V10_CAMPAIGN_LABEL,
        "bind the actual frozen V10 source; never claim its run occurred",
    )
    validate_pin_reference(base, contract.get("source"), V10["source"],
                           "candidate runner source")
    validate_pin_reference(base, contract.get("protocol"), V10["protocol"],
                           "candidate runner protocol")
    overview = contract.get(V10_OVERVIEW_KEY)
    base.need(
        type(overview) is dict
        and overview.get("overview_version",
                         overview.get("version", overview.get("graph_version")))
        == 56
        and overview.get("authenticated_evidence_owner_lower_bound") == 191
        and overview.get("authenticated_history_reference_lower_bound") == 196
        and overview.get("qualified_candidate_count", 0) == 0,
        "bind only actual pushed V56 and actual historical 191/196 floors",
    )
    overview_owners = overview.get("owners")
    base.need(
        type(overview_owners) in (dict, list),
        "require all four complete genuine pushed V56 graph owners",
    )
    if type(overview_owners) is dict:
        base.need(set(overview_owners) == set(V56),
                  "reject missing or extra independently pinned V56 graph roles")
        for role, item in V56.items():
            validate_pin_reference(
                base, overview_owners.get(role), item, "pushed V56 " + role,
            )
    else:
        assert isinstance(overview_owners, list)
        base.need(
            len(overview_owners) == len(V56)
            and all(type(owner) is dict for owner in overview_owners),
            "require exactly four complete distinct pushed V56 list owners",
        )
        for role, item in V56.items():
            matched = [
                owner for owner in overview_owners
                if owner.get("path") == item[0]
            ]
            base.need(
                len(matched) == 1,
                "reject missing or duplicate pushed V56 graph owner: " + role,
            )
            validate_pin_reference(
                base, matched[0], item, "pushed V56 " + role,
            )
    base.need(
        contract.get("historical_actual_v9_pre_activation_failure")
        == historical_v9_source_expectations(),
        "preserve the authentic V9 controller failure, real empty root, "
        "thirteen synthetic rows and unmodified original exception",
    )
    original = contract.get("original_oracle")
    base.need(type(original) is dict,
              "require the complete original upstream 13-suite oracle")
    assert isinstance(original, dict)
    base.need(
        original.get("case_execution_denominator") == 31237
        and original.get("suite_count") == 13
        and original.get("named_private_waiver_count") == 13
        and original.get("candidate_case_producer_version", 4) == 4
        and original.get(
            "candidate_run_uses_both_complete_reference_vectors", True
        ) is True
        and original.get("candidate_wrapper_allowed", False) is False
        and original.get("stdlib_re_fallback_allowed", False) is False
        and original.get("cross_family_matching_allowed", False) is False
        and original.get("external_regex_dependency_allowed", False) is False,
        "freeze all actual original cases without wrappers or external engines",
    )
    suites = original.get("source_ordered_suites")
    base.need(
        type(suites) is list
        and len(suites) == len(SUITE_SIZES)
        and all(type(row) is dict for row in suites)
        and tuple(row.get("case_execution_count") for row in suites)
        == SUITE_SIZES
        and sum(SUITE_SIZES) == 31237,
        "preserve all 31,237 cases in their exact 13 original suites",
    )
    effects = contract.get("source_only_effects")
    base.need(type(effects) is dict,
              "require a real explicit zero-effect source-only freeze ledger")
    assert isinstance(effects, dict)
    for name, expected in source_effect_expectations().items():
        base.need(
            effects.get(name) == expected,
            "reject invented V10 source-only effect or result: " + name,
        )
    for name in (
        "phase1_reference_archive_bytes_read",
        "v16_source_build_archive_compressed_bytes_read",
        "v16_source_build_archive_gzip_inflation_count",
        "v16_source_build_archive_read_count",
        "v16_source_build_archive_uncompressed_bytes_read",
    ):
        if name in effects:
            base.need(effects[name] == 0,
                      "never open or inflate any archive: " + name)
    for name in (
        "phase1_reference_archive_decompressed",
        "v16_source_build_archive_gzip_inflation_attempted",
        "v16_source_build_archive_read_attempted",
    ):
        if name in effects:
            base.need(effects[name] is False,
                      "reject any real archive side effect: " + name)


def make_runner_proof(base: types.ModuleType, owners: dict,
                      contract: dict) -> dict:
    validate_v10_contract(base, contract)
    base.need(type(owners) is dict and set(owners) == set(V10),
              "authenticate three and only three actual V10 source owners")
    for role, item in V10.items():
        validate_owner(base, owners.get(role), item, role)
    identities = [
        (owners[role]["device"], owners[role]["inode"]) for role in V10
    ]
    base.need(len(set(identities)) == len(V10),
              "reject exchanged, hardlinked, duplicate V10 source owners")
    proof = {
        "schema": SCHEMA + "-authenticated-rust-v10-full-suite-source-freeze",
        "version": 10,
        "family": "rust",
        "status": "SOURCE FROZEN; NOT RUN",
        "contract_status": V10_CONTRACT_STATUS,
        "campaign_label": V10_CAMPAIGN_LABEL,
        "owners": copy.deepcopy(owners),
        "source": copy.deepcopy(owners["source"]),
        "protocol": copy.deepcopy(owners["protocol"]),
        "contract": copy.deepcopy(owners["contract"]),
        "complete_frozen_source_contract": copy.deepcopy(contract),
        "source_owner_count": 3,
        "new_candidate_family_count": 0,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "suite_sizes": list(SUITE_SIZES),
        "candidate_case_producer_version": 4,
        "previous_graph_version": 56,
        "prepublication_evidence_owner_lower_bound": 191,
        "prepublication_history_reference_lower_bound": 196,
        "resulting_evidence_owner_lower_bound": 194,
        "resulting_history_reference_lower_bound": 199,
        "historical_actual_v9_controller_status": "FAIL",
        "historical_actual_v9_matching_status": "NOT RUN",
        "historical_actual_v9_recorded_original_inner_exception":
            "accept only one exact owner-only Rust campaign root",
        "historical_actual_v9_recorded_inner_exception_placeholder_count": 13,
        "historical_actual_v9_synthetic_failed_worker_placeholder_count": 13,
        "historical_actual_v9_synthetic_placeholder_flags_are_real_attempts":
            False,
        "historical_actual_v9_actual_candidate_workers": 0,
        "historical_actual_v9_attempted_suite_count": 0,
        "historical_actual_v9_started_suite_count": 0,
        "historical_actual_v9_fully_observed_suite_count": 0,
        "historical_actual_v9_recovery_roots_created": 1,
        "historical_actual_v9_recovery_journals_created": 0,
        "historical_actual_v9_targets_restored_by_recovery": False,
        "historical_actual_v9_build_archive_reads_by_controller": 1,
        "historical_v7_matching_status": "FAIL",
        "historical_v7_semantic_mismatch_count": 928,
        "historical_v7_explicitly_verified_passing_case_count": 8965,
        "historical_v7_candidate_workers": 13,
        "actual_v16_native_build_status": "PASS",
        "actual_v16_compiler_process_count": 28,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_semantic_mismatch_count": "NOT MEASURED",
        "candidate_verified_passing_case_count": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "reference_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "source_build_archive_opened_by_graph": False,
        "source_build_archive_inflated_by_graph": False,
        "source_build_archive_sha256_recomputed_by_graph": False,
        "matching_archive_opened_by_graph": False,
        "matching_archive_inflated_by_graph": False,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_frozen_source_binding_sha256"] = base.digest(
        base.canonical(proof)
    )
    validate_runner_proof(base, proof)
    return proof


def validate_runner_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject absent complete frozen V10 source-only evidence")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-rust-v10-full-suite-source-freeze",
        "version": 10,
        "family": "rust",
        "status": "SOURCE FROZEN; NOT RUN",
        "contract_status": V10_CONTRACT_STATUS,
        "campaign_label": V10_CAMPAIGN_LABEL,
        "source_owner_count": 3,
        "new_candidate_family_count": 0,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "suite_sizes": list(SUITE_SIZES),
        "candidate_case_producer_version": 4,
        "previous_graph_version": 56,
        "prepublication_evidence_owner_lower_bound": 191,
        "prepublication_history_reference_lower_bound": 196,
        "resulting_evidence_owner_lower_bound": 194,
        "resulting_history_reference_lower_bound": 199,
        "historical_actual_v9_controller_status": "FAIL",
        "historical_actual_v9_matching_status": "NOT RUN",
        "historical_actual_v9_recorded_original_inner_exception":
            "accept only one exact owner-only Rust campaign root",
        "historical_actual_v9_recorded_inner_exception_placeholder_count": 13,
        "historical_actual_v9_synthetic_failed_worker_placeholder_count": 13,
        "historical_actual_v9_synthetic_placeholder_flags_are_real_attempts":
            False,
        "historical_actual_v9_actual_candidate_workers": 0,
        "historical_actual_v9_attempted_suite_count": 0,
        "historical_actual_v9_started_suite_count": 0,
        "historical_actual_v9_fully_observed_suite_count": 0,
        "historical_actual_v9_recovery_roots_created": 1,
        "historical_actual_v9_recovery_journals_created": 0,
        "historical_actual_v9_targets_restored_by_recovery": False,
        "historical_actual_v9_build_archive_reads_by_controller": 1,
        "historical_v7_matching_status": "FAIL",
        "historical_v7_semantic_mismatch_count": 928,
        "historical_v7_explicitly_verified_passing_case_count": 8965,
        "historical_v7_candidate_workers": 13,
        "actual_v16_native_build_status": "PASS",
        "actual_v16_compiler_process_count": 28,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_semantic_mismatch_count": "NOT MEASURED",
        "candidate_verified_passing_case_count": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "reference_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "source_build_archive_opened_by_graph": False,
        "source_build_archive_inflated_by_graph": False,
        "source_build_archive_sha256_recomputed_by_graph": False,
        "matching_archive_opened_by_graph": False,
        "matching_archive_inflated_by_graph": False,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
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
        base.need(proof.get(key) == value,
                  "reject invented V10 source freeze or matching result: " + key)
    owners = proof.get("owners")
    base.need(type(owners) is dict and set(owners) == set(V10),
              "require exactly three independent actual source owners")
    assert isinstance(owners, dict)
    for role, item in V10.items():
        validate_owner(base, owners.get(role), item, role)
        base.need(proof.get(role) == owners[role],
                  "reject mismatched complete V10 source owner: " + role)
    base.need(
        len({(owner["device"], owner["inode"]) for owner in owners.values()})
        == len(V10),
        "reject duplicate source-owner device and inode pairs",
    )
    validate_v10_contract(base, proof.get("complete_frozen_source_contract"))
    body = {key: value for key, value in proof.items()
            if key != "complete_frozen_source_binding_sha256"}
    base.need(
        proof.get("complete_frozen_source_binding_sha256")
        == base.digest(base.canonical(body)),
        "bind every exact frozen V10 owner, source-only outcome and actual floor",
    )


def authenticate_v10(base: types.ModuleType,
                    options: argparse.Namespace) -> dict:
    owners = {}
    raw = {}
    for role, item in V10.items():
        base.need(
            base.checked(
                getattr(options, "runner_" + role + "_sha256"),
                "actual frozen V10 " + role,
            ) == item[1]
            and getattr(options, "runner_" + role + "_bytes") == item[2],
            "require root-released exact V10 source owner: " + role,
        )
        raw[role], owners[role] = base.read_owner(*item, private=True)
    contract = base.document(
        raw["contract"], "complete actual frozen V10 machine contract"
    )
    protocol_words = raw["protocol"].lower()
    base.need(
        b"31,237" in protocol_words
        and b"13" in protocol_words
        and any(
            phrase in protocol_words
            for phrase in (
                b"not run", b"not yet run", b"not been run",
                b"not executed", b"no candidate", b"source freeze",
                b"source-only", b"frozen",
            )
        ),
        "retain a truthful full-suite source protocol without executing it",
    )
    return make_runner_proof(base, owners, contract)


def v56_reproduction_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V56["source"][1],
        source_bytes=V56["source"][2],
        previous_source_sha256=previous.V55["source"][1],
        previous_inputs_sha256=previous.V55["inputs"][1],
        previous_summary_sha256=previous.V55["summary"][1],
        previous_svg_sha256=previous.V55["svg"][1],
        failure_sha256=previous.FAILURE[1],
        failure_bytes=previous.FAILURE[2],
        failure_inode=previous.FAILURE_INODE,
        failure_device=previous.DEVICE,
        observation_sha256=previous.OBSERVATION[1],
        observation_bytes=previous.OBSERVATION[2],
        observation_inode=previous.OBSERVATION_INODE,
        observation_device=previous.DEVICE,
    )

def authenticate_v56(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V56.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V56 " + role)
            == item[1],
            "reject substituted actual pushed V56 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete actual pushed V56 summary")
    inputs = base.document(raw["inputs"], "complete actual pushed V56 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(
        prior_modules, v56_reproduction_options(previous)
    )
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v56-summary"
        and old.get("version") == 56
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V56["source"])
        and old.get("inputs") == base.pin(*V56["inputs"])
        and old.get("svg") == base.pin(*V56["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v56-inputs"
        and inputs.get("version") == 56
        and inputs.get("renderer") == base.pin(*V56["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V56["inputs"][0]]
        and raw["summary"] == expected[V56["summary"][0]]
        and raw["svg"] == expected[V56["svg"][0]]
        and old.get("authenticated_evidence_owner_lower_bound") == 191
        and old.get("authenticated_history_reference_lower_bound") == 196
        and old.get("actual_rust_v16_build_status") == "PASS"
        and old.get("actual_rust_v16_compiler_process_count") == 28
        and old.get("actual_rust_v16_compiler_pid_vector_present_in_receipt")
        is False
        and old.get("actual_rust_v16_phase_vector_present_in_receipt") is False
        and old.get("actual_rust_v16_native_artifact_digests_present_in_receipt")
        is False
        and old.get("actual_rust_v8_controller_status") == "FAIL"
        and old.get("actual_rust_v8_matching_status") == "NOT RUN"
        and old.get("actual_rust_v8_candidate_workers") == 0
        and old.get("actual_rust_v8_build_archive_reads_by_controller") == 1
        and old.get("actual_rust_v9_controller_status") == "FAIL"
        and old.get("actual_rust_v9_matching_status") == "NOT RUN"
        and old.get("actual_rust_v9_candidate_workers") == 0
        and old.get("actual_rust_v9_attempted_suite_count") == 0
        and old.get("actual_rust_v9_started_suite_count") == 0
        and old.get("actual_rust_v9_completed_suite_count") == 0
        and old.get("actual_rust_v9_fully_observed_suite_count") == 0
        and old.get("actual_rust_v9_recorded_original_inner_exception")
        == "accept only one exact owner-only Rust campaign root"
        and old.get("actual_rust_v9_recorded_original_inner_exception_placeholder_count")
        == 13
        and old.get("actual_rust_v9_synthetic_failed_worker_placeholder_count")
        == 13
        and old.get("actual_rust_v9_synthetic_placeholders_are_observed_workers")
        is False
        and old.get("actual_rust_v9_placeholder_worker_flags_are_real_attempts")
        is False
        and old.get("actual_rust_v9_recovery_roots_created") == 1
        and old.get("actual_rust_v9_recovery_journals_created") == 0
        and old.get("actual_rust_v9_original_targets_restored_by_recovery")
        is False
        and old.get("actual_rust_v9_build_archive_reads_by_controller") == 1
        and old.get("actual_rust_v9_build_archive_inflations_by_controller")
        == 1
        and old.get("actual_rust_v9_build_archive_read_by_graph") is False
        and old.get("actual_rust_v7_semantic_status") == "FAIL"
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("actually_tested_corrected_candidate_families") == ["rust"]
        and old.get("qualified_candidate_count") == 0
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce every pushed genuine V56 V9 failure byte without an archive",
    )
    return old, inputs, raw["svg"]

def result_fields(proof: dict) -> dict:
    owners = proof["owners"]
    return {
        "rust_original_campaign_v10_source_freeze": copy.deepcopy(proof),
        "rust_original_campaign_v10_source_freeze_status":
            "SOURCE FROZEN; NOT RUN",
        "rust_original_campaign_v10_source": copy.deepcopy(owners["source"]),
        "rust_original_campaign_v10_protocol": copy.deepcopy(owners["protocol"]),
        "rust_original_campaign_v10_contract": copy.deepcopy(owners["contract"]),
        "rust_original_campaign_v10_source_sha256": V10["source"][1],
        "rust_original_campaign_v10_protocol_sha256": V10["protocol"][1],
        "rust_original_campaign_v10_contract_sha256": V10["contract"][1],
        "rust_original_campaign_v10_label": V10_CAMPAIGN_LABEL,
        "rust_original_campaign_v10_source_owner_count": 3,
        "rust_original_campaign_v10_new_candidate_family_count": 0,
        "rust_original_campaign_v10_full_case_denominator": 31237,
        "rust_original_campaign_v10_suite_count": 13,
        "rust_original_campaign_v10_private_waiver_count": 13,
        "rust_original_campaign_v10_candidate_case_producer_version": 4,
        "rust_original_campaign_v10_matching_status": "NOT RUN",
        "rust_original_campaign_v10_candidate_correctness": "NOT MEASURED",
        "rust_original_campaign_v10_semantic_mismatch_count": "NOT MEASURED",
        "rust_original_campaign_v10_verified_passing_case_count": "NOT MEASURED",
        "rust_original_campaign_v10_candidate_qualified": False,
        "rust_original_campaign_v10_candidate_workers_started": 0,
        "rust_original_campaign_v10_candidate_processes_started": 0,
        "rust_original_campaign_v10_prepublication_evidence_owner_lower_bound":
            191,
        "rust_original_campaign_v10_prepublication_history_reference_lower_bound":
            196,
        "rust_original_campaign_v10_resulting_evidence_owner_lower_bound": 194,
        "rust_original_campaign_v10_resulting_history_reference_lower_bound": 199,
        "rust_original_campaign_v10_archive_opened_by_graph": False,
        "rust_original_campaign_v10_archive_inflated_by_graph": False,
        "rust_original_campaign_v10_archive_sha256_recomputed_by_graph": False,
        "actual_current_graph_predecessor_version": 56,
        "authenticated_evidence_owner_lower_bound": 194,
        "authenticated_history_reference_lower_bound": 199,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
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
    base.need(type(snapshot) is dict, "reject absent complete V57 snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_original_campaign_v10_source_freeze")
    validate_runner_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, expected in updates.items():
        base.need(snapshot.get(key) == expected,
                  "reject forged V10 frozen-source outcome: " + key)
    replaced = snapshot.get("preserved_v56_replaced_snapshot_fields")
    base.need(type(replaced) is dict,
              "preserve all replaced actual pushed V56 snapshot fields")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v56_replaced_snapshot_fields", None)
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
        and snapshot.get("actual_rust_v8_controller_status") == "FAIL"
        and snapshot.get("actual_rust_v8_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v8_semantic_mismatch_count")
        == "NOT MEASURED"
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
        and snapshot.get("actual_rust_v9_recorded_original_inner_exception")
        == "accept only one exact owner-only Rust campaign root"
        and snapshot.get(
            "actual_rust_v9_recorded_original_inner_exception_placeholder_count"
        ) == 13
        and snapshot.get("actual_rust_v9_synthetic_failed_worker_placeholder_count")
        == 13
        and snapshot.get("actual_rust_v9_synthetic_placeholders_are_observed_workers")
        is False
        and snapshot.get("actual_rust_v9_placeholder_worker_flags_are_real_attempts")
        is False
        and snapshot.get("actual_rust_v9_recovery_roots_created") == 1
        and snapshot.get("actual_rust_v9_recovery_journals_created") == 0
        and snapshot.get("actual_rust_v9_original_targets_restored_by_recovery")
        is False
        and snapshot.get("actual_rust_v9_build_archive_reads_by_controller") == 1
        and snapshot.get("actual_rust_v9_build_archive_inflations_by_controller")
        == 1
        and snapshot.get("actual_rust_v9_build_archive_read_by_graph") is False
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
        and snapshot.get("c_v4_original_campaign_semantic_mismatch_count") == 1230
        and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count")
        == 2172
        and snapshot.get("zig_v3_original_campaign_semantic_mismatch_count")
        == 1764
        and snapshot.get("rust_original_campaign_v10_source_freeze_status")
        == "SOURCE FROZEN; NOT RUN"
        and snapshot.get("rust_original_campaign_v10_matching_status")
        == "NOT RUN"
        and snapshot.get("rust_original_campaign_v10_candidate_workers_started")
        == 0
        and snapshot.get("rust_original_campaign_v10_candidate_qualified")
        is False
        and snapshot.get("actually_tested_corrected_candidate_families")
        == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count") == 1
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 194
        and snapshot.get("authenticated_history_reference_lower_bound") == 199
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and snapshot.get("actual_clock_samples_by_graph") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("winner_selected") is False,
        "retain real V8/V9 failures and freeze V10 without running matching",
    )

def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    v43 = prior_modules[1][1][1][9]
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "actual V57 renderer footer")
    inputs_sha = base.checked(inputs_sha, "actual V57 graph inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v56-title", "v57-title")
    visible = visible.replace("v56-description", "v57-description")
    changes = (
        (
            "Rust test runner failed twice before matching; no "
            "replacement is ready</title>",
            "Rust test runner failed twice; corrected follow-up is "
            "frozen, not run</title>",
            "preserve real V8/V9 failures and genuinely unrun V10",
        ),
        (
            "The V8 and corrected V9 test controllers both failed before "
            "starting any candidate. V9 left one empty recovery directory; "
            "it did not start a matching worker or restore targets.",
            "The V8 and V9 test controllers both failed before starting any "
            "candidate. V9 left one empty recovery directory and thirteen "
            "synthetic error records, not real workers. A corrected V10 "
            "full-suite runner is source frozen and has not run.",
            "never count actual V9 synthetic records as tested V10 workers",
        ),
        (
            "Two and only two independently authenticated plaintext "
            "V9 controller-failure owners raise actual current lower "
            "bounds from 189 and 194 to 191 and 196;",
            "Three and only three independently authenticated V10 "
            "source-only owners raise actual current lower bounds "
            "from 191 and 196 to 194 and 199;",
            "count only three genuinely independent frozen V10 source owners",
        ),
        (
            '<text x="65" y="398" class="heading">Rust test runner '
            'failed again before matching</text>',
            '<text x="65" y="398" class="heading">Two Rust test runners '
            'failed; corrected follow-up frozen</text>',
            "preserve two actual failures without fabricating a V10 run",
        ),
        (
            "The native build passed. Both V8 and V9 stopped before "
            "matching. V9 left one empty recovery root. Real new "
            "workers: 0.",
            "The native build passed. V8 and V9 stopped before matching. "
            "V10 is source frozen, NOT RUN. Real new workers: 0.",
            "never mistake source-only V10 freeze for activated matching",
        ),
        (
            "Old test failed; V8 and V9 both stopped before matching",
            "V7 failed; V8/V9 stopped; corrected V10 not yet run",
            "retain the actual old 928-difference semantic result",
        ),
        (
            '<text x="64" y="1756" class="heading">Corrected V9 '
            'controller failed before matching</text>',
            '<text x="64" y="1756" class="heading">Corrected V10 '
            'full-suite test frozen; not yet run</text>',
            "report three source-only owners and no new matching execution",
        ),
        (
            "Exactly two new plaintext V9 failure records raise actual "
            "current lower bounds from 189 / 194 to 191 / 196.",
            "Exactly three new V10 source files raise actual current "
            "lower bounds from 191 / 196 to 194 / 199.",
            "bind actual pushed V56 and exactly three independent V10 files",
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
        '<text x="64" y="1888" class="heading">Exact real failure '
        'and frozen follow-up evidence</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V56 graph inputs SHA-256", V56["inputs"][1]),
        ("Historical V56 graph renderer SHA-256", V56["source"][1]),
        ("Historical V56 graph summary SHA-256", V56["summary"][1]),
        ("Historical V56 graph image SHA-256", V56["svg"][1]),
        ("Frozen corrected V10 runner source SHA-256", V10["source"][1]),
        ("Frozen corrected V10 runner protocol SHA-256", V10["protocol"][1]),
        ("Frozen corrected V10 runner contract SHA-256", V10["contract"][1]),
        ("Real failed V9 controller stdout SHA-256", previous.FAILURE[1]),
        ("Independent real V9 failure observation SHA-256",
         previous.OBSERVATION[1]),
        ("Recorded V16 build archive SHA-256 (not opened by this graph)",
         previous.BUILD_ARCHIVE_SHA),
        ("Retained real empty V9 recovery-root inode",
         str(previous.RECOVERY_ROOT_INODE)),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + index * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2167" class="small">V9 read and inflated '
        'the build archive once; one empty recovery root, no journal '
        'and zero candidate workers.</text>',
        '<text x="65" y="2187" class="small">Recorded V9 inner error: '
        'accept only one exact owner-only Rust campaign root.</text>',
        '<text x="65" y="2207" class="small">All 13 V9 '
        'worker-attempted error records are synthetic; no suite '
        'or candidate worker actually started.</text>',
        '<text x="65" y="2227" class="small">V10 source frozen; '
        'matching NOT RUN. Holdout unopened. Faster compatible '
        'replacement: none.</text>',
        '<!-- Preserve real V8/V9 controller effects. This source-only '
        'V10 graph opens no archive, private recovery root, candidate, '
        'native library, clock or hidden holdout. -->',
        '</svg>',
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, fingerprint in (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V56 graph inputs SHA-256", V56["inputs"][1]),
        ("Historical V56 graph renderer SHA-256", V56["source"][1]),
        ("Historical V56 graph summary SHA-256", V56["summary"][1]),
        ("Historical V56 graph image SHA-256", V56["svg"][1]),
    ):
        base.need(raw.count((label + ": " + fingerprint).encode("ascii"))
                  == 1, "bind current and historical V57 owner: " + label)
    base.need(
        ("Graph inputs SHA-256: " + V56["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V56["source"][1]).encode("ascii")
        not in raw,
        "never describe historical V56 owners as current V57 evidence",
    )
    lower = raw.lower()
    for phrase in (
        b'height="2250"', b"building a faster python re",
        b"928 differences", b"8,965 explicitly verified",
        b"13 real workers", b"compatible replacements",
        b"not measured", b"4.2m unopened", b"31,237",
        b"signature checks", b"public-interface observations",
        b"large-input observations", b"17 pass", b"7 fail",
        b"22 pass", b"3 not run", b"2,147,483,648", b"1,087",
        b"1,036", b"1,262", b"1,230", b"2,172", b"1,764",
        b"v8 and v9", b"corrected", b"v10",
        b"frozen", b"not run", b"new workers: 0",
        b"191 / 196", b"194 / 199", b"not generated",
        b"not opened", b"not opened by this graph",
        b"one empty recovery root", b"no journal",
        b"recorded v9 inner error", b"accept only one exact owner-only",
        b"all 13 v9", b"synthetic",
        b"independent real v9 failure observation",
    ):
        base.need(phrase in lower,
                  "retain true V57 plain-language outcome: " + repr(phrase))
    for falsehood in (
        b"v10 matching passed", b"v10 matching failed",
        b"v10 semantic mismatches", b"v10 candidate workers started",
        b"v9 candidate passed", b"13 observed v9 suites",
        b"13 actual v9 workers", b"all targets restored",
        b"recovery journal was written", b"zero recovery roots",
        b"corrected candidate passed", b"qualified rust replacement",
        b"v8 controller succeeded", b"v9 controller succeeded",
        b"no archive was read by the controller",
        b"28 unique compiler pids", b"phase vector in receipt",
        b"native binary digest in receipt", b"winner selected",
        b"holdout opened", b"faster than python", b"32 repaired",
    ):
        base.need(falsehood not in lower,
                  "reject invented V10 result or V9 worker: " + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish V57 graph with exactly one actual linefeed")
    return raw

def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "actual independently owned V57 renderer")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound actual corrected-source V57 graph renderer")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                 private=True)
    old, old_inputs, old_svg = authenticate_v56(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V56},
    )
    proof = authenticate_v10(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v56_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key]) for key in updates
        if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V56.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 57,
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
        "preserve actual Python plus exactly six from-scratch families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 194,
            "authenticated_history_reference_lower_bound": 199,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "v10_full_suite_source_freeze": copy.deepcopy(proof),
                "v10_full_suite_source_status": "SOURCE FROZEN; NOT RUN",
                "v10_full_case_denominator": 31237,
                "v10_suite_count": 13,
                "v10_candidate_matching_status": "NOT RUN",
                "v10_candidate_correctness": "NOT MEASURED",
                "v10_semantic_mismatch_count": "NOT MEASURED",
                "v10_verified_passing_case_count": "NOT MEASURED",
                "v10_candidate_workers_started": 0,
                "v10_candidate_qualified": False,
                "actual_v9_controller_status": "FAIL",
                "actual_v9_matching_status": "NOT RUN",
                "actual_v9_semantic_mismatch_count": "NOT MEASURED",
                "actual_v9_candidate_workers": 0,
                "actual_v9_attempted_suite_count": 0,
                "actual_v9_started_suite_count": 0,
                "actual_v9_completed_suite_count": 0,
                "actual_v9_fully_observed_suite_count": 0,
                "actual_v9_recorded_original_inner_exception":
                    "accept only one exact owner-only Rust campaign root",
                "actual_v9_recorded_original_inner_exception_placeholder_count":
                    13,
                "actual_v9_synthetic_failed_worker_placeholder_count": 13,
                "actual_v9_synthetic_placeholders_are_observed_workers": False,
                "actual_v9_placeholder_worker_flags_are_real_attempts": False,
                "actual_v9_recovery_roots_created": 1,
                "actual_v9_recovery_journals_created": 0,
                "actual_v9_original_targets_restored_by_recovery": False,
                "actual_v9_controller_build_archive_reads": 1,
                "actual_v9_controller_build_archive_inflations": 1,
                "actual_v9_build_archive_read_by_graph": False,
                "actual_v8_controller_status": "FAIL",
                "actual_v8_matching_status": "NOT RUN",
                "actual_v8_semantic_mismatch_count": "NOT MEASURED",
                "actual_v8_candidate_workers": 0,
                "actual_v8_controller_build_archive_reads": 1,
                "actual_v8_controller_build_archive_inflations": 1,
                "actual_v8_build_archive_read_by_graph": False,
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
        "version": 57,
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
              "bound all complete frozen-correction V57 graph owners")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_contract(base: types.ModuleType) -> dict:
    return {
        "schema": V10_CONTRACT_SCHEMA,
        "version": 10,
        "status": V10_CONTRACT_STATUS,
        "family": "rust",
        "label": V10_CAMPAIGN_LABEL,
        "source": {"path": V10["source"][0], "sha256": V10["source"][1]},
        "protocol": {
            "path": V10["protocol"][0], "sha256": V10["protocol"][1],
        },
        V10_OVERVIEW_KEY: {
            "version": 56,
            "authenticated_evidence_owner_lower_bound": 191,
            "authenticated_history_reference_lower_bound": 196,
            "qualified_candidate_count": 0,
            "owners": {role: base.pin(*item)
                       for role, item in V56.items()},
        },
        "historical_actual_v9_pre_activation_failure":
            historical_v9_source_expectations(),
        "original_oracle": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "candidate_case_producer_version": 4,
            "candidate_run_uses_both_complete_reference_vectors": True,
            "candidate_wrapper_allowed": False,
            "stdlib_re_fallback_allowed": False,
            "cross_family_matching_allowed": False,
            "external_regex_dependency_allowed": False,
            "source_ordered_suites": [
                {"id": "synthetic-v57-suite-" + str(index),
                 "case_execution_count": size}
                for index, size in enumerate(SUITE_SIZES)
            ],
        },
        "source_only_effects": source_effect_expectations(),
    }


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_runner_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError(
        "accepted a forged frozen V10 source-only control: " + description
    )


def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    v43 = prior_modules[1][1][1][9]
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 3711
        and prior.get("actual_rust_v16_build_status") == "PASS"
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and prior.get("actual_rust_v7_candidate_workers") == 13
        and prior.get("actual_rust_v9_controller_status") == "FAIL"
        and prior.get("actual_rust_v9_matching_status") == "NOT RUN"
        and prior.get("actual_rust_v9_semantic_mismatch_count") == "NOT MEASURED"
        and prior.get("actual_rust_v9_candidate_workers") == 0
        and prior.get("actual_rust_v9_attempted_suite_count") == 0
        and prior.get("actual_rust_v9_started_suite_count") == 0
        and prior.get("actual_rust_v9_completed_suite_count") == 0
        and prior.get("actual_rust_v9_fully_observed_suite_count") == 0
        and prior.get("actual_rust_v9_recorded_original_inner_exception")
        == "accept only one exact owner-only Rust campaign root"
        and prior.get(
            "actual_rust_v9_recorded_original_inner_exception_placeholder_count"
        ) == 13
        and prior.get("actual_rust_v9_synthetic_failed_worker_placeholder_count")
        == 13
        and prior.get("actual_rust_v9_synthetic_placeholders_are_observed_workers")
        is False
        and prior.get("actual_rust_v9_placeholder_worker_flags_are_real_attempts")
        is False
        and prior.get("actual_rust_v9_recovery_roots_created") == 1
        and prior.get("actual_rust_v9_recovery_journals_created") == 0
        and prior.get("actual_rust_v9_original_targets_restored_by_recovery")
        is False
        and prior.get("actual_rust_v9_build_archive_reads_by_controller") == 1
        and prior.get("actual_rust_v9_build_archive_inflations_by_controller")
        == 1
        and prior.get("actual_rust_v9_build_archive_read_by_graph") is False
        and prior.get("actual_rust_v8_controller_status") == "FAIL"
        and prior.get("actual_rust_v8_matching_status") == "NOT RUN"
        and prior.get("actual_rust_v8_candidate_workers") == 0
        and prior.get("actual_rust_v8_build_archive_reads_by_controller") == 1
        and prior.get("authenticated_evidence_owner_lower_bound") == 191
        and prior.get("authenticated_history_reference_lower_bound") == 196
        and prior.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and prior.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "preserve all 3,711 truthful V56 actual-failure source-only controls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item, 955001 + index)
            for index, (role, item) in enumerate(V10.items())
        }
        proof = make_runner_proof(base, owners, synthetic_contract(base))
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
        for role in V10:
            hostile = copy.deepcopy(proof)
            hostile[role]["inode"] = hostile["owners"][role]["inode"] + 37
            rejected += reject_control(base, hostile, "owner-copy:" + role)
        contract = proof["complete_frozen_source_contract"]
        for key, value in contract.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_source_contract"][key] = (
                v43.forged_value(base, value)
            )
            rejected += reject_control(base, hostile, "contract:" + key)
        for key, value in contract[
                "historical_actual_v9_pre_activation_failure"
        ].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_source_contract"][
                "historical_actual_v9_pre_activation_failure"
            ][key] = v43.forged_value(base, value)
            rejected += reject_control(
                base, hostile, "genuine-v9-preactivation-failure:" + key)
        for role in ("failure_owner", "independent_observation_owner"):
            for key, value in contract[
                    "historical_actual_v9_pre_activation_failure"
            ][role].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_frozen_source_contract"][
                    "historical_actual_v9_pre_activation_failure"
                ][role][key] = v43.forged_value(base, value)
                rejected += reject_control(
                    base, hostile, "genuine-v9-owner:" + role + ":" + key)
        for key, value in contract["source_only_effects"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_source_contract"][
                "source_only_effects"
            ][key] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "effect:" + key)
        for index, row in enumerate(
                contract["original_oracle"]["source_ordered_suites"]):
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_source_contract"]["original_oracle"][
                "source_ordered_suites"
            ][index]["case_execution_count"] = (
                row["case_execution_count"] + 1)
            rejected += reject_control(
                base, hostile, "complete-original-suite:" + str(index))
        for role in V56:
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_source_contract"][V10_OVERVIEW_KEY][
                "owners"
            ][role]["sha256"] = "0" * 64
            rejected += reject_control(
                base, hostile, "actual-pushed-v56:" + role)
        hostile = copy.deepcopy(proof)
        hostile["owners"]["protocol"]["inode"] = (
            hostile["owners"]["source"]["inode"])
        rejected += reject_control(
            base, hostile, "duplicate-independent-source-owner")
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v57")),
            ("filesystem", lambda: os.open("forbidden-v57", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v57")),
            ("write", lambda: os.mkdir("forbidden-v57")),
            ("process", lambda: subprocess.run(("forbidden-v57",))),
            ("process", lambda: subprocess.Popen(("forbidden-v57",))),
            ("process", lambda: os.execv("/forbidden-v57", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically forbid V57 graph " + kind)
            else:
                raise base.GraphError(
                    "forbidden V57 source-only graph effect escaped")
        base.need(rejected >= 110,
                  "reject forged V10 source, archive effects and fake results")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 57,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v56_hostile_controls": 3711,
            "new_v57_hostile_controls": rejected,
            "rejected_hostile_control_count": 3711 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_receipts_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_receipts_read_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
            "actual_feature_source_files_read_by_self_test": 0,
            "actual_frozen_v10_source_files_read_by_self_test": 0,
            "actual_restored_original_files_read_by_self_test": 0,
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
            "actual_current_graph_predecessor_version": 56,
            "actual_rust_v16_build_status": "PASS",
            "actual_rust_v16_compiler_process_count": 28,
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v9_controller_status": "FAIL",
            "actual_rust_v9_matching_status": "NOT RUN",
            "actual_rust_v9_semantic_mismatch_count": "NOT MEASURED",
            "actual_rust_v9_candidate_workers": 0,
            "actual_rust_v9_attempted_suite_count": 0,
            "actual_rust_v9_started_suite_count": 0,
            "actual_rust_v9_completed_suite_count": 0,
            "actual_rust_v9_fully_observed_suite_count": 0,
            "actual_rust_v9_recorded_original_inner_exception":
                "accept only one exact owner-only Rust campaign root",
            "actual_rust_v9_recorded_original_inner_exception_placeholder_count":
                13,
            "actual_rust_v9_synthetic_failed_worker_placeholder_count": 13,
            "actual_rust_v9_synthetic_placeholders_are_observed_workers": False,
            "actual_rust_v9_placeholder_worker_flags_are_real_attempts": False,
            "actual_rust_v9_recovery_roots_created": 1,
            "actual_rust_v9_recovery_journals_created": 0,
            "actual_rust_v9_original_targets_restored_by_recovery": False,
            "actual_rust_v9_build_archive_reads_by_controller": 1,
            "actual_rust_v9_build_archive_inflations_by_controller": 1,
            "actual_rust_v9_build_archive_read_by_graph": False,
            "actual_rust_v8_controller_status": "FAIL",
            "actual_rust_v8_matching_status": "NOT RUN",
            "actual_rust_v8_semantic_mismatch_count": "NOT MEASURED",
            "actual_rust_v8_candidate_workers": 0,
            "actual_rust_v8_build_archive_reads_by_controller": 1,
            "actual_rust_v8_build_archive_inflations_by_controller": 1,
            "actual_rust_v8_build_archive_read_by_graph": False,
            "rust_original_campaign_v10_source_freeze_status":
                "SOURCE FROZEN; NOT RUN",
            "rust_original_campaign_v10_matching_status": "NOT RUN",
            "rust_original_campaign_v10_candidate_correctness": "NOT MEASURED",
            "rust_original_campaign_v10_candidate_workers_started": 0,
            "rust_original_campaign_v10_source_owner_count": 3,
            "rust_original_campaign_v10_full_case_denominator": 31237,
            "rust_original_campaign_v10_suite_count": 13,
            "authenticated_evidence_owner_lower_bound": 194,
            "authenticated_history_reference_lower_bound": 199,
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
            "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
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
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg",
        }
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only three authorized complete V57 graph outputs",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete independently owned V57 graph output")
            remaining = remaining[count:]
        os.fsync(descriptor)
        meta = os.fstat(descriptor)
        base.need(
            meta.st_uid == os.geteuid()
            and meta.st_nlink == 1
            and meta.st_size == len(raw)
            and stat.S_IMODE(meta.st_mode) == 0o600,
            "publish complete private single-link V57 output",
        )
    finally:
        os.close(descriptor)
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
              "re-authenticate every durably published exact V57 graph byte")


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 57,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 56,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V56.items()},
        "actual_rust_v16_build_status":
            snapshot["actual_rust_v16_build_status"],
        "actual_rust_v16_compiler_process_count":
            snapshot["actual_rust_v16_compiler_process_count"],
        "actual_rust_v7_semantic_status":
            snapshot["actual_rust_v7_semantic_status"],
        "actual_rust_v7_semantic_mismatch_count":
            snapshot["actual_rust_v7_semantic_mismatch_count"],
        "actual_rust_v7_explicitly_verified_passing_case_count":
            snapshot["actual_rust_v7_explicitly_verified_passing_case_count"],
        "actual_rust_v9_controller_status":
            snapshot["actual_rust_v9_controller_status"],
        "actual_rust_v9_matching_status":
            snapshot["actual_rust_v9_matching_status"],
        "actual_rust_v9_semantic_mismatch_count":
            snapshot["actual_rust_v9_semantic_mismatch_count"],
        "actual_rust_v9_candidate_workers":
            snapshot["actual_rust_v9_candidate_workers"],
        "actual_rust_v9_attempted_suite_count":
            snapshot["actual_rust_v9_attempted_suite_count"],
        "actual_rust_v9_started_suite_count":
            snapshot["actual_rust_v9_started_suite_count"],
        "actual_rust_v9_completed_suite_count":
            snapshot["actual_rust_v9_completed_suite_count"],
        "actual_rust_v9_fully_observed_suite_count":
            snapshot["actual_rust_v9_fully_observed_suite_count"],
        "actual_rust_v9_recorded_original_inner_exception":
            snapshot["actual_rust_v9_recorded_original_inner_exception"],
        "actual_rust_v9_recorded_original_inner_exception_placeholder_count":
            snapshot["actual_rust_v9_recorded_original_inner_exception_placeholder_count"],
        "actual_rust_v9_synthetic_failed_worker_placeholder_count":
            snapshot["actual_rust_v9_synthetic_failed_worker_placeholder_count"],
        "actual_rust_v9_synthetic_placeholders_are_observed_workers":
            snapshot["actual_rust_v9_synthetic_placeholders_are_observed_workers"],
        "actual_rust_v9_placeholder_worker_flags_are_real_attempts":
            snapshot["actual_rust_v9_placeholder_worker_flags_are_real_attempts"],
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
        "actual_rust_v8_controller_status":
            snapshot["actual_rust_v8_controller_status"],
        "actual_rust_v8_matching_status":
            snapshot["actual_rust_v8_matching_status"],
        "actual_rust_v8_candidate_workers":
            snapshot["actual_rust_v8_candidate_workers"],
        "actual_rust_v8_build_archive_reads_by_controller":
            snapshot["actual_rust_v8_build_archive_reads_by_controller"],
        "actual_rust_v8_build_archive_inflations_by_controller":
            snapshot["actual_rust_v8_build_archive_inflations_by_controller"],
        "actual_rust_v8_build_archive_read_by_graph":
            snapshot["actual_rust_v8_build_archive_read_by_graph"],
        "rust_original_campaign_v10_source_freeze_status":
            snapshot["rust_original_campaign_v10_source_freeze_status"],
        "rust_original_campaign_v10_matching_status":
            snapshot["rust_original_campaign_v10_matching_status"],
        "rust_original_campaign_v10_candidate_correctness":
            snapshot["rust_original_campaign_v10_candidate_correctness"],
        "rust_original_campaign_v10_candidate_workers_started":
            snapshot["rust_original_campaign_v10_candidate_workers_started"],
        "rust_original_campaign_v10_full_case_denominator":
            snapshot["rust_original_campaign_v10_full_case_denominator"],
        "rust_original_campaign_v10_suite_count":
            snapshot["rust_original_campaign_v10_suite_count"],
        "rust_original_campaign_v10_source_owner_count":
            snapshot["rust_original_campaign_v10_source_owner_count"],
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
    for role in V56:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in V10:
        parser.add_argument("--runner-" + role + "-sha256")
        parser.add_argument("--runner-" + role + "-bytes", type=int)
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v56()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend(
                "previous_" + role + "_sha256" for role in V56
            )
            for role in V10:
                forbidden.extend((
                    "runner_" + role + "_sha256",
                    "runner_" + role + "_bytes",
                ))
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(
                all(getattr(options, name) is None for name in forbidden),
                "source-only V57 self-test never accepts real source owner pins",
            )
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256,
                                  "exact complete actual V57 graph renderer")
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "publish only the independently authorized three V57 outputs",
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
                    options.inputs_sha256, "exact actual V57 graph inputs"
                ),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "exact actual V57 graph summary"
                ),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "exact compact V57 graph chart"
                ),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True
                )
                base.need(
                    raw == outputs[path],
                    "reproduce every frozen-source V57 graph byte: " + path,
                )
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context",
            )
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError, UnicodeError,
    ) as error:
        sys.stderr.write("current V57 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write(
                "current V57 overview rejected: " + str(error) + "\n"
            )
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
