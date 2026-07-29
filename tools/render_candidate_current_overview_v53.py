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
SELF = "tools/render_candidate_current_overview_v53.py"
OUTPUT = "docs/evidence/candidate-current-overview-v53"
SCHEMA = "rebar-candidate-current-overview-v53"
V52 = {
    "source": (
        "tools/render_candidate_current_overview_v52.py",
        "08f510f86c70505e37db560f57fbc550d1f72fbd7408eab809e8bcdb5701c426",
        64494,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v52.inputs.json",
        "7d8731e70fcd510dc2c2e3a4fb3ebdf5d05941eb8bcb23ae9bfc37203186671a",
        592900,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v52.json",
        "8d4b54dba7989b2627ebee17cd1bd07bf39ec855824ce6339cfa7e45821a2488",
        1630637,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v52.svg",
        "fd6d95314b593878764a653eb07c81678cb57ba137fd5539ba892e44f3621397",
        13968,
    ),
}
V8 = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v8.py",
        "eb36dd1b16775e00525f9d0ad4d1bab46318d4c652c0cf6653bd1aa8776265aa",
        164002,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V8.md",
        "9afa6f964bceaa950e4031bcd00b27a615635a6bb6ed3eb66cd60ba1f123ec30",
        10563,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v8.json",
        "7780c4d14fe043ebe25ff50b4a437e6a0c9ba975f6d4cc47a833bbfbe3cdcf80",
        13749,
    ),
}
V8_CONTRACT_SCHEMA = "rebar-owned-repaired-rust-original-campaign-v8-recoverable-source-freeze"
V8_CONTRACT_STATUS = "SOURCE FROZEN; CORRECTED RUST V16 CANDIDATE NOT RUN"
V8_CAMPAIGN_LABEL = "phase2-v16-rust-buffer-shape-pickle-original-p0"
V8_OVERVIEW_KEY = "current_v52_graph"
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


def load_v52() -> tuple:
    path, fingerprint, size = V52["source"]
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
            raise ValueError("reject substituted actual pushed V52 renderer")
        chunks = []
        remaining = size
        while remaining:
            chunk = os.read(descriptor, min(262144, remaining))
            if not chunk:
                raise ValueError("reject truncated actual pushed V52 renderer")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject appended actual pushed V52 renderer")
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
            raise ValueError("reject changed actual pushed V52 renderer")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_actual_pushed_build_graph_v52")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    chain = previous.load_v51()
    base = chain[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v52"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS,
        "load only the exact complete actual pushed V52 build graph",
    )
    return (previous, *chain)


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
        "reject substituted complete V8 reference: " + description,
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
        "bind one genuine private independently owned V8 " + description,
    )


def validate_v8_contract(base: types.ModuleType, contract: object) -> None:
    base.need(type(contract) is dict,
              "reject missing complete frozen V8 runner machine contract")
    assert isinstance(contract, dict)
    base.need(
        contract.get("schema") == V8_CONTRACT_SCHEMA
        and contract.get("version") == 8
        and contract.get("status") == V8_CONTRACT_STATUS
        and contract.get("family") == "rust"
        and contract.get("campaign_label", contract.get("label"))
        == V8_CAMPAIGN_LABEL,
        "bind the actual frozen V8 source; never claim its run occurred",
    )
    validate_pin_reference(base, contract.get("source"), V8["source"],
                           "candidate runner source")
    validate_pin_reference(base, contract.get("protocol"), V8["protocol"],
                           "candidate runner protocol")
    overview = contract.get(V8_OVERVIEW_KEY)
    base.need(
        type(overview) is dict
        and overview.get("overview_version",
                         overview.get("version", overview.get("graph_version")))
        == 52
        and overview.get("authenticated_evidence_owner_lower_bound") == 181
        and overview.get("authenticated_history_reference_lower_bound") == 186
        and overview.get("qualified_candidate_count", 0) == 0,
        "bind only actual pushed V52 and actual historical 181/186 floors",
    )
    overview_owners = overview.get("owners")
    base.need(
        type(overview_owners) in (dict, list),
        "require all four complete genuine pushed V52 graph owners",
    )
    if type(overview_owners) is dict:
        base.need(set(overview_owners) == set(V52),
                  "reject missing or extra independently pinned V52 graph roles")
        for role, item in V52.items():
            validate_pin_reference(
                base, overview_owners.get(role), item, "pushed V52 " + role,
            )
    else:
        assert isinstance(overview_owners, list)
        base.need(
            len(overview_owners) == len(V52)
            and all(type(owner) is dict for owner in overview_owners),
            "require exactly four complete distinct pushed V52 list owners",
        )
        for role, item in V52.items():
            matched = [
                owner for owner in overview_owners
                if owner.get("path") == item[0]
            ]
            base.need(
                len(matched) == 1,
                "reject missing or duplicate pushed V52 graph owner: " + role,
            )
            validate_pin_reference(
                base, matched[0], item, "pushed V52 " + role,
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
            "reject invented V8 source-only effect or result: " + name,
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
    validate_v8_contract(base, contract)
    base.need(type(owners) is dict and set(owners) == set(V8),
              "authenticate three and only three actual V8 source owners")
    for role, item in V8.items():
        validate_owner(base, owners.get(role), item, role)
    identities = [
        (owners[role]["device"], owners[role]["inode"]) for role in V8
    ]
    base.need(len(set(identities)) == len(V8),
              "reject exchanged, hardlinked, duplicate V8 source owners")
    proof = {
        "schema": SCHEMA + "-authenticated-rust-v8-full-suite-source-freeze",
        "version": 8,
        "family": "rust",
        "status": "SOURCE FROZEN; NOT RUN",
        "contract_status": V8_CONTRACT_STATUS,
        "campaign_label": V8_CAMPAIGN_LABEL,
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
        "previous_graph_version": 52,
        "prepublication_evidence_owner_lower_bound": 181,
        "prepublication_history_reference_lower_bound": 186,
        "resulting_evidence_owner_lower_bound": 184,
        "resulting_history_reference_lower_bound": 189,
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
              "reject absent complete frozen V8 source-only evidence")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-rust-v8-full-suite-source-freeze",
        "version": 8,
        "family": "rust",
        "status": "SOURCE FROZEN; NOT RUN",
        "contract_status": V8_CONTRACT_STATUS,
        "campaign_label": V8_CAMPAIGN_LABEL,
        "source_owner_count": 3,
        "new_candidate_family_count": 0,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "suite_sizes": list(SUITE_SIZES),
        "candidate_case_producer_version": 4,
        "previous_graph_version": 52,
        "prepublication_evidence_owner_lower_bound": 181,
        "prepublication_history_reference_lower_bound": 186,
        "resulting_evidence_owner_lower_bound": 184,
        "resulting_history_reference_lower_bound": 189,
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
                  "reject invented V8 source freeze or matching result: " + key)
    owners = proof.get("owners")
    base.need(type(owners) is dict and set(owners) == set(V8),
              "require exactly three independent actual source owners")
    assert isinstance(owners, dict)
    for role, item in V8.items():
        validate_owner(base, owners.get(role), item, role)
        base.need(proof.get(role) == owners[role],
                  "reject mismatched complete V8 source owner: " + role)
    base.need(
        len({(owner["device"], owner["inode"]) for owner in owners.values()})
        == len(V8),
        "reject duplicate source-owner device and inode pairs",
    )
    validate_v8_contract(base, proof.get("complete_frozen_source_contract"))
    body = {key: value for key, value in proof.items()
            if key != "complete_frozen_source_binding_sha256"}
    base.need(
        proof.get("complete_frozen_source_binding_sha256")
        == base.digest(base.canonical(body)),
        "bind every exact frozen V8 owner, source-only outcome and actual floor",
    )


def authenticate_v8(base: types.ModuleType,
                    options: argparse.Namespace) -> dict:
    owners = {}
    raw = {}
    for role, item in V8.items():
        base.need(
            base.checked(
                getattr(options, "runner_" + role + "_sha256"),
                "actual frozen V8 " + role,
            ) == item[1]
            and getattr(options, "runner_" + role + "_bytes") == item[2],
            "require root-released exact V8 source owner: " + role,
        )
        raw[role], owners[role] = base.read_owner(*item, private=True)
    contract = base.document(
        raw["contract"], "complete actual frozen V8 machine contract"
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


def v52_reproduction_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V52["source"][1],
        source_bytes=V52["source"][2],
        previous_source_sha256=previous.V51["source"][1],
        previous_inputs_sha256=previous.V51["inputs"][1],
        previous_summary_sha256=previous.V51["summary"][1],
        previous_svg_sha256=previous.V51["svg"][1],
        receipt_sha256=previous.RECEIPT[1],
        receipt_bytes=previous.RECEIPT[2],
        receipt_inode=previous.RECEIPT_INODE,
        receipt_device=previous.DEVICE,
        archive_sha256=previous.ARCHIVE[1],
        archive_bytes=previous.ARCHIVE[2],
        archive_inode=previous.ARCHIVE_INODE,
        archive_device=previous.DEVICE,
    )


def authenticate_v52(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, *chain, base = modules
    raw = {}
    for role, item in V52.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V52 " + role)
            == item[1],
            "reject substituted actual pushed V52 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete actual pushed V52 summary")
    inputs = base.document(raw["inputs"], "complete actual pushed V52 inputs")
    previous.validate_snapshot(*chain, base, old.get("snapshot"))
    reconstructed, pairs = previous.build(
        *chain, base, v52_reproduction_options(previous)
    )
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v52-summary"
        and old.get("version") == 52
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V52["source"])
        and old.get("inputs") == base.pin(*V52["inputs"])
        and old.get("svg") == base.pin(*V52["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v52-inputs"
        and inputs.get("version") == 52
        and inputs.get("renderer") == base.pin(*V52["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V52["inputs"][0]]
        and raw["summary"] == expected[V52["summary"][0]]
        and raw["svg"] == expected[V52["svg"][0]]
        and old.get("actual_rust_v16_build_status") == "PASS"
        and old.get("actual_rust_v16_compiler_process_count") == 28
        and old.get("actual_rust_v16_compiler_pid_vector_present_in_receipt")
        is False
        and old.get("actual_rust_v16_phase_vector_present_in_receipt") is False
        and old.get("actual_rust_v16_native_artifact_digests_present_in_receipt")
        is False
        and old.get("actual_rust_v16_candidate_matching_status") == "NOT RUN"
        and old.get("actual_rust_v7_semantic_status") == "FAIL"
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and old.get("actual_rust_v7_candidate_workers") == 13
        and old.get("actual_rust_worker_process_ids") == WORKERS
        and old.get("authenticated_evidence_owner_lower_bound") == 181
        and old.get("authenticated_history_reference_lower_bound") == 186
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("actually_tested_corrected_candidate_families") == ["rust"]
        and old.get("qualified_candidate_count") == 0
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce every actual pushed V52 byte without reading an archive",
    )
    return old, inputs, raw["svg"]


def result_fields(proof: dict) -> dict:
    owners = proof["owners"]
    return {
        "rust_original_campaign_v8_source_freeze": copy.deepcopy(proof),
        "rust_original_campaign_v8_source_freeze_status":
            "SOURCE FROZEN; NOT RUN",
        "rust_original_campaign_v8_source": copy.deepcopy(owners["source"]),
        "rust_original_campaign_v8_protocol": copy.deepcopy(owners["protocol"]),
        "rust_original_campaign_v8_contract": copy.deepcopy(owners["contract"]),
        "rust_original_campaign_v8_source_sha256": V8["source"][1],
        "rust_original_campaign_v8_protocol_sha256": V8["protocol"][1],
        "rust_original_campaign_v8_contract_sha256": V8["contract"][1],
        "rust_original_campaign_v8_label": V8_CAMPAIGN_LABEL,
        "rust_original_campaign_v8_source_owner_count": 3,
        "rust_original_campaign_v8_new_candidate_family_count": 0,
        "rust_original_campaign_v8_full_case_denominator": 31237,
        "rust_original_campaign_v8_suite_count": 13,
        "rust_original_campaign_v8_private_waiver_count": 13,
        "rust_original_campaign_v8_candidate_case_producer_version": 4,
        "rust_original_campaign_v8_matching_status": "NOT RUN",
        "rust_original_campaign_v8_candidate_correctness": "NOT MEASURED",
        "rust_original_campaign_v8_semantic_mismatch_count": "NOT MEASURED",
        "rust_original_campaign_v8_verified_passing_case_count": "NOT MEASURED",
        "rust_original_campaign_v8_candidate_qualified": False,
        "rust_original_campaign_v8_candidate_workers_started": 0,
        "rust_original_campaign_v8_candidate_processes_started": 0,
        "rust_original_campaign_v8_prepublication_evidence_owner_lower_bound":
            181,
        "rust_original_campaign_v8_prepublication_history_reference_lower_bound":
            186,
        "rust_original_campaign_v8_resulting_evidence_owner_lower_bound": 184,
        "rust_original_campaign_v8_resulting_history_reference_lower_bound": 189,
        "rust_original_campaign_v8_archive_opened_by_graph": False,
        "rust_original_campaign_v8_archive_inflated_by_graph": False,
        "rust_original_campaign_v8_archive_sha256_recomputed_by_graph": False,
        "actual_current_graph_predecessor_version": 52,
        "authenticated_evidence_owner_lower_bound": 184,
        "authenticated_history_reference_lower_bound": 189,
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
    previous, *chain, base = modules
    base.need(type(snapshot) is dict, "reject absent complete V53 snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_original_campaign_v8_source_freeze")
    validate_runner_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, expected in updates.items():
        base.need(snapshot.get(key) == expected,
                  "reject forged V8 frozen-source outcome: " + key)
    replaced = snapshot.get("preserved_v52_replaced_snapshot_fields")
    base.need(type(replaced) is dict,
              "preserve all replaced actual pushed V52 snapshot fields")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v52_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(*chain, base, history)
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
        and snapshot.get("actual_rust_v16_candidate_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_v7_semantic_status") == "FAIL"
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and snapshot.get("actual_rust_v7_candidate_workers") == 13
        and snapshot.get("actual_rust_worker_process_ids") == WORKERS
        and snapshot.get("actual_rust_original_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 928
        and snapshot.get("actual_complete_rust_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 928
        and snapshot.get("current_complete_rust_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 928
        and snapshot.get("historical_rust_v3_original_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 1087
        and snapshot.get("historical_rust_v4_original_campaign", {}).get(
            "semantic_mismatch_count"
        ) == 1036
        and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
        and snapshot.get("c_v4_original_campaign_semantic_mismatch_count") == 1230
        and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count")
        == 2172
        and snapshot.get("zig_v3_original_campaign_semantic_mismatch_count")
        == 1764
        and snapshot.get("actually_tested_corrected_candidate_families")
        == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
        == 1
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 184
        and snapshot.get("authenticated_history_reference_lower_bound") == 189
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
        "preserve actual matching, native build, original suites and sealed holdout",
    )


def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, *chain, base = modules
    v43 = chain[8]
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact current V53 renderer footer")
    inputs_sha = base.checked(inputs_sha, "exact current V53 inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v52-title", "v53-title")
    visible = visible.replace("v52-description", "v53-description")
    changes = (
        (
            "Rust native build passes; full compatibility is not yet proved"
            "</title>",
            "Rust build passes; the next complete compatibility test is frozen, "
            "not run</title>",
            "show actual build and the separately frozen full-suite runner",
        ),
        (
            "The rebuilt candidate has not been matching-tested.",
            "A first-party runner for all 31,237 original checks and all 13 "
            "suites is now frozen; its new matching run has not happened.",
            "identify the frozen V8 runner as not yet executed",
        ),
        (
            "Two and only two genuine durable build-result owners raise "
            "actual current lower bounds from 179 and 184 to 181 and 186;",
            "Three and only three independently authenticated frozen-runner "
            "source owners raise current lower bounds from 181 and 186 to "
            "184 and 189;",
            "count exactly three actual new plaintext source owners",
        ),
        (
            "Rust native build: PASS — candidate matching NOT RUN",
            "Rust build: PASS — next full-suite test: FROZEN, NOT RUN",
            "distinguish build PASS from unrun candidate correctness",
        ),
        (
            "The combined first-party Rust bridge was successfully built "
            "offline. Matching is NOT RUN; it is the same Rust family, "
            "not a seventh replacement.",
            "The first-party Rust build passed. Its 31,237-check, 13-suite "
            "matching runner is frozen, NOT RUN; it remains the same Rust "
            "family.",
            "report the actual native build and honest runner-only freeze",
        ),
        (
            "Old matching failed; rebuilt candidate not matching-tested",
            "Old test failed; new full-suite runner frozen, not run",
            "keep the latest real V7 failure distinct from unrun V8",
        ),
        (
            "Actual offline native build passed; matching still not run",
            "Native build passed; new full-suite test frozen, not run",
            "report the frozen campaign without inventing a candidate result",
        ),
        (
            "Exactly two new durable build-result owners raise actual "
            "current lower bounds from 179 / 184 to 181 / 186.",
            "Exactly three frozen full-suite runner source files raise actual "
            "current lower bounds from 181 / 186 to 184 / 189.",
            "advance only by three genuine distinct V8 plaintext owners",
        ),
    )
    for before, after, reason in changes:
        visible = v43.replace_once(base, visible, before, after, reason)
    lines = visible.splitlines()
    start = next(
        i for i, line in enumerate(lines)
        if line.startswith('<rect x="44" y="1858" width="1352"')
    )
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="361" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact reproducible '
        'build and frozen-test evidence</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V52 graph inputs SHA-256", V52["inputs"][1]),
        ("Historical V52 graph renderer SHA-256", V52["source"][1]),
        ("Historical V52 graph summary SHA-256", V52["summary"][1]),
        ("Historical V52 graph image SHA-256", V52["svg"][1]),
        ("Frozen V8 full-suite runner source SHA-256", V8["source"][1]),
        ("Frozen V8 full-suite runner protocol SHA-256", V8["protocol"][1]),
        ("Frozen V8 full-suite runner contract SHA-256", V8["contract"][1]),
        ("Actual V16 native-build receipt SHA-256", previous.RECEIPT[1]),
        ("Actual V16 build archive SHA-256 (receipt-attested; not opened)",
         previous.ARCHIVE[1]),
        ("Actual V16 native-build source SHA-256", previous.BUILD["source"][1]),
        ("Same first-party Rust bridge source SHA-256", previous.COMBINED_SHA),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + index * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2167" class="small">The 28-operation native '
        'build passed. The new 31,237-case runner is frozen only; no '
        'candidate test has run.</text>',
        '<text x="65" y="2187" class="small">Historical V52 lower '
        'bounds 181 / 186; current authenticated lower bounds 184 / '
        '189.</text>',
        '<text x="65" y="2207" class="small">Candidate matching: '
        'NOT RUN. Holdout: unopened. Winning faster replacement: none.</text>',
        '<!-- Build PASS; runner SOURCE FROZEN only. No archive content, '
        'candidate process, native load, clock or holdout is accessed. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, fingerprint in (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V52 graph inputs SHA-256", V52["inputs"][1]),
        ("Historical V52 graph renderer SHA-256", V52["source"][1]),
        ("Historical V52 graph summary SHA-256", V52["summary"][1]),
        ("Historical V52 graph image SHA-256", V52["svg"][1]),
    ):
        token = (label + ": " + fingerprint).encode("ascii")
        base.need(raw.count(token) == 1,
                  "bind exact current or historical V53 footer: " + label)
    base.need(
        ("Graph inputs SHA-256: " + V52["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V52["source"][1]).encode("ascii")
        not in raw,
        "never present historical V52 footer as the current V53 graph",
    )
    lower = raw.lower()
    for truth in (
        b'height="2250"', b"building a faster python re",
        b"928 differences", b"8,965 explicitly verified", b"13 real workers",
        b"compatible replacements", b"not measured", b"4.2m unopened",
        b"31,237", b"13-suite", b"source", b"frozen", b"not run",
        b"rust build: pass", b"same rust family",
        b"signature checks", b"public-interface observations",
        b"large-input observations", b"17 pass", b"7 fail", b"22 pass",
        b"3 not run", b"2,147,483,648", b"1,087", b"1,036",
        b"1,262", b"1,230", b"2,172", b"1,764",
        b"181 / 186", b"184 / 189", b"not generated", b"not opened",
        b"winning faster replacement: none", b"receipt-attested; not opened",
    ):
        base.need(truth in lower,
                  "preserve actual frozen-runner graph truth: " + repr(truth))
    for falsehood in (
        b"candidate matching passed", b"corrected candidate passed",
        b"rust replacement qualified", b"v8 matching passed",
        b"v8 matching failed", b"v8 worker started",
        b"28 unique compiler pids", b"phase vector in receipt",
        b"native binary digest in receipt", b"30,309 verified passes",
        b"30309 verified passes", b"896 repaired", b"672 repaired",
        b"224 repaired", b"32 repaired", b"seventh candidate family",
        b"winner selected", b"holdout opened", b"faster than python",
        b"archive inflated by graph",
    ):
        base.need(falsehood not in lower,
                  "reject invented frozen-runner result: " + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish compact reproducible V53 chart with one linefeed")
    return raw


def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, *chain, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact independently owned V53 renderer")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "bound exact root-released independently owned V53 renderer",
    )
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                 private=True)
    old, old_inputs, old_svg = authenticate_v52(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V52},
    )
    proof = authenticate_v8(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v52_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key]) for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V52.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 53,
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
        "preserve verified Python plus exactly six first-party families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 184,
            "authenticated_history_reference_lower_bound": 189,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "v8_full_suite_source_freeze": copy.deepcopy(proof),
                "v8_full_suite_source_status": "SOURCE FROZEN; NOT RUN",
                "v8_full_case_denominator": 31237,
                "v8_suite_count": 13,
                "v8_candidate_matching_status": "NOT RUN",
                "v8_candidate_correctness": "NOT MEASURED",
                "v8_semantic_mismatch_count": "NOT MEASURED",
                "v8_verified_passing_case_count": "NOT MEASURED",
                "v8_candidate_workers_started": 0,
                "v8_candidate_qualified": False,
                "actual_v16_build_status": "PASS",
                "actual_v16_candidate_matching_status": "NOT RUN",
                "actual_v16_candidate_correctness": "NOT MEASURED",
                "actual_v16_compiler_process_count": 28,
                "actual_v16_expected_compiler_process_count": 28,
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
        "version": 53,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(input_raw),
                           len(input_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(
        max(len(input_raw), len(summary_raw), len(svg)) <= base.OWNER_LIMIT,
        "keep all complete V53 plaintext graph owners deterministically bounded",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_contract(base: types.ModuleType) -> dict:
    return {
        "schema": V8_CONTRACT_SCHEMA,
        "version": 8,
        "status": V8_CONTRACT_STATUS,
        "family": "rust",
        "label": V8_CAMPAIGN_LABEL,
        "source": {"path": V8["source"][0], "sha256": V8["source"][1]},
        "protocol": {
            "path": V8["protocol"][0], "sha256": V8["protocol"][1],
        },
        V8_OVERVIEW_KEY: {
            "overview_version": 52,
            "authenticated_evidence_owner_lower_bound": 181,
            "authenticated_history_reference_lower_bound": 186,
            "qualified_candidate_count": 0,
            "owners": {role: base.pin(*item) for role, item in V52.items()},
        },
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
                {"id": "synthetic-v53-suite-" + str(index),
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
        "accepted a forged frozen V8 source-only control: " + description
    )


def self_test(modules: tuple) -> dict:
    previous, *chain, base = modules
    v43 = chain[8]
    prior = previous.self_test(*chain, base)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 2648
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get("actual_rust_v7_explicitly_verified_passing_case_count")
        == 8965
        and prior.get("actual_rust_v7_candidate_workers") == 13
        and prior.get("actual_rust_v16_build_status") == "PASS"
        and prior.get("actual_rust_v16_compiler_process_count") == 28
        and prior.get("actual_rust_v16_candidate_matching_status") == "NOT RUN"
        and prior.get("source_build_archive_gzip_inflation_count_by_graph") == 0
        and prior.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts") == LARGE_COUNTS,
        "preserve all 2,648 physically isolated genuine V52 hostility controls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item, 953001 + index)
            for index, (role, item) in enumerate(V8.items())
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
                    base, hostile, "owner:" + role + ":" + key
                )
        for role in V8:
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
                row["case_execution_count"] + 1
            )
            rejected += reject_control(
                base, hostile, "complete-original-suite:" + str(index)
            )
        for role in V52:
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_source_contract"][V8_OVERVIEW_KEY][
                "owners"
            ][role]["sha256"] = "0" * 64
            rejected += reject_control(
                base, hostile, "actual-pushed-v52:" + role
            )
        hostile = copy.deepcopy(proof)
        hostile["owners"]["protocol"]["inode"] = (
            hostile["owners"]["source"]["inode"]
        )
        rejected += reject_control(base, hostile, "duplicate-independent-owner")
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v53")),
            ("filesystem", lambda: os.open("forbidden-v53", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v53")),
            ("write", lambda: os.mkdir("forbidden-v53")),
            ("process", lambda: subprocess.run(("forbidden-v53",))),
            ("process", lambda: subprocess.Popen(("forbidden-v53",))),
            ("process", lambda: os.execv("/forbidden-v53", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically forbid V53 graph " + kind)
            else:
                raise base.GraphError(
                    "a forbidden V53 physical action escaped its wall"
                )
        base.need(rejected >= 110,
                  "reject all fake V8 owners, complete suites and false runs")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 53,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v52_hostile_controls": 2648,
            "new_v53_hostile_controls": rejected,
            "rejected_hostile_control_count": 2648 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_receipts_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_receipts_read_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
            "actual_feature_source_files_read_by_self_test": 0,
            "actual_frozen_v8_source_files_read_by_self_test": 0,
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
            "actual_current_graph_predecessor_version": 52,
            "actual_rust_v7_semantic_status": "FAIL",
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v16_build_status": "PASS",
            "actual_rust_v16_compiler_process_count": 28,
            "actual_rust_v16_candidate_matching_status": "NOT RUN",
            "rust_original_campaign_v8_source_freeze_status":
                "SOURCE FROZEN; NOT RUN",
            "rust_original_campaign_v8_matching_status": "NOT RUN",
            "rust_original_campaign_v8_candidate_correctness": "NOT MEASURED",
            "rust_original_campaign_v8_candidate_workers_started": 0,
            "rust_original_campaign_v8_source_owner_count": 3,
            "rust_original_campaign_v8_full_case_denominator": 31237,
            "rust_original_campaign_v8_suite_count": 13,
            "authenticated_evidence_owner_lower_bound": 184,
            "authenticated_history_reference_lower_bound": 189,
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
            "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
            "actually_tested_corrected_candidate_families": ["rust"],
            "actually_tested_corrected_candidate_family_count": 1,
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
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
        "publish only three authorized complete V53 graph outputs",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete independently owned V53 graph output")
            remaining = remaining[count:]
        os.fsync(descriptor)
        meta = os.fstat(descriptor)
        base.need(
            meta.st_uid == os.geteuid()
            and meta.st_nlink == 1
            and meta.st_size == len(raw)
            and stat.S_IMODE(meta.st_mode) == 0o600,
            "publish complete private single-link V53 output",
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
              "re-authenticate every durably published exact V53 graph byte")


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 53,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 52,
        **{
            "previous_overview_" + role + "_sha256": item[1]
            for role, item in V52.items()
        },
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
        "rust_original_campaign_v8_source_freeze_status":
            snapshot["rust_original_campaign_v8_source_freeze_status"],
        "rust_original_campaign_v8_matching_status":
            snapshot["rust_original_campaign_v8_matching_status"],
        "rust_original_campaign_v8_candidate_correctness":
            snapshot["rust_original_campaign_v8_candidate_correctness"],
        "rust_original_campaign_v8_candidate_workers_started":
            snapshot["rust_original_campaign_v8_candidate_workers_started"],
        "rust_original_campaign_v8_full_case_denominator":
            snapshot["rust_original_campaign_v8_full_case_denominator"],
        "rust_original_campaign_v8_suite_count":
            snapshot["rust_original_campaign_v8_suite_count"],
        "rust_original_campaign_v8_source_owner_count":
            snapshot["rust_original_campaign_v8_source_owner_count"],
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
    for role in V52:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in V8:
        parser.add_argument("--runner-" + role + "-sha256")
        parser.add_argument("--runner-" + role + "-bytes", type=int)
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v52()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend(
                "previous_" + role + "_sha256" for role in V52
            )
            for role in V8:
                forbidden.extend((
                    "runner_" + role + "_sha256",
                    "runner_" + role + "_bytes",
                ))
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(
                all(getattr(options, name) is None for name in forbidden),
                "source-only V53 self-test never accepts real source owner pins",
            )
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256,
                                  "exact complete actual V53 graph renderer")
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "publish only the independently authorized three V53 outputs",
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
                    options.inputs_sha256, "exact actual V53 graph inputs"
                ),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "exact actual V53 graph summary"
                ),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "exact compact V53 graph chart"
                ),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True
                )
                base.need(
                    raw == outputs[path],
                    "reproduce every frozen-source V53 graph byte: " + path,
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
        sys.stderr.write("current V53 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write(
                "current V53 overview rejected: " + str(error) + "\n"
            )
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
