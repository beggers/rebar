#!/usr/bin/env python3
"""Publish immutable V101 correctness evidence without touching candidates or archives."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_candidate_current_overview_v101.py"
OUTPUT = "docs/evidence/candidate-current-overview-v101"
UNMEASURED = "NOT MEASURED"
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
DENOMINATOR = 31_237
SUPPLEMENTAL = 8_244
PROPOSAL = 141_557_760
V25_BRIDGE = "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4"
V24_BRIDGE = "e0c26cb83fe35eb18297e7a9cd58b63be891d847479237d2ba972e4ba1b3b3bf"
ENGINE = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ARCHIVE_SHA256 = "dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7"
FINDING = "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"
PREVIOUS = {
    "source": ("tools/render_candidate_current_overview_v100.py",
               "c6514b88fafe06c18ee52a129a9b90f3a689ad74f3aa59ec6505d5405c866ed8", 67535),
    "inputs": ("docs/evidence/candidate-current-overview-v100.inputs.json",
               "5285437e8004f95c69806b482c08f40736ab03aff498c6047d3235ae444b064b", 9984),
    "summary": ("docs/evidence/candidate-current-overview-v100.summary.json",
                "249304de2735ec5a1c6602f888b9543a181c7c63fa84cca58285b807b3cd299b", 24073),
    "svg": ("docs/evidence/candidate-current-overview-v100.svg",
            "d8847686c8da69902cb9089e79d607028b4fceeb8919e8ac2ad8d8f3d1629fd1", 9612),
}
CURRENT = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v25.py",
               "09074713ee068a01dc91c07db68a7efcd4500f9b92990699f5e849fa77410edc", 100824),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V25.md",
                 "9a2d0a3a71e998750cc6213a7ad4c42c6a8bf8a022347af55723d2407aa345e1", 5638),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v25.json",
                 "230e4c98914b0ca2b1d4bc55eb9d7cf38474eed835626c2639916bd4ed581c1a", 57478),
    "receipt": (
        "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-"
        "rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json",
        "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832,
    ),
}
AUDIT = (
    "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json",
    "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19", 20985,
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864), ("scanner_v3", 1024),
    ("buffer_v3", 768), ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
LOSSES = {"substitution_v2": 240, "shape_v2": 1112}


class Rejected(ValueError):
    """Authenticity, history, or source-only isolation was violated."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("ascii")


def objects(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(type(key) is str and key not in result, "duplicate authenticated JSON field")
        result[key] = value
    return result


def parsed(raw: bytes, label: str) -> dict:
    try:
        document = json.loads(raw, object_pairs_hook=objects,
                              parse_constant=lambda _: (_ for _ in ()).throw(Rejected("nonfinite JSON")))
    except (ValueError, UnicodeError, TypeError) as failure:
        raise Rejected("invalid public source evidence: " + label) from failure
    require(type(document) is dict and canonical(document) == raw,
            "noncanonical public source evidence: " + label)
    return document


def same(actual: object, expected: dict, label: str) -> None:
    require(type(actual) is dict, "expected a complete object: " + label)
    for key, value in expected.items():
        require(actual.get(key) == value, label + ": changed " + key)


def reference(spec: tuple[str, str, int]) -> dict:
    return {"path": spec[0], "sha256": spec[1], "bytes": spec[2]}


def owners() -> tuple[tuple[str, str, int], ...]:
    return (GOAL, *PREVIOUS.values(), *CURRENT.values(), AUDIT)


class SourceWall:
    def __init__(self, render: bool) -> None:
        self.render = render
        self.owners = frozenset(os.path.join(ROOT, item[0]) for item in owners()) | {
            os.path.join(ROOT, SELF)
        }
        self.outputs = frozenset(os.path.join(ROOT, OUTPUT + suffix)
                                 for suffix in (".svg", ".inputs.json", ".json"))

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str, "source wall rejected an unapproved file descriptor")
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.render and path in self.outputs and flags & required == required,
                        "source wall rejected an unowned or nonexclusive V101 output mutation")
            else:
                require(path in self.owners and bool(flags & os.O_NOFOLLOW),
                        "source wall rejected candidate, native, gzip, archive, private, or holdout")
            return
        if (event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn"))
                or event in {"os.system", "os.fork", "os.posix_spawn", "os.mkdir", "os.remove",
                             "os.rename", "os.rmdir", "os.chdir", "os.chmod", "os.link",
                             "os.symlink", "os.truncate", "os.putenv", "time.time",
                             "time.monotonic", "time.perf_counter", "_thread.start_new_thread"}):
            raise Rejected("source wall rejected process, profiler, clock, network, or mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (name in {"re", "_sre", "gzip", "ctypes", "subprocess"}
                                                or name.startswith(("candidates.", "rebar.")))),
                    "source wall rejected candidate, decompressor, native, or matching import")


def owner(spec: tuple[str, str, int]) -> bytes:
    relative, expected, size = spec
    require(relative == SELF or spec in owners(), "owner escaped exact V101 plaintext allowlist")
    descriptor = os.open(os.path.join(ROOT, relative), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_nlink == 1 and identity.st_uid == os.getuid()
                and identity.st_size == size,
                "public evidence owner identity changed: " + relative)
        blocks = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
        payload = b"".join(blocks)
        require(digest(payload) == expected, "public evidence owner SHA-256 changed: " + relative)
        return payload
    finally:
        os.close(descriptor)


def verify_previous(inputs: dict, summary: dict, svg: bytes) -> None:
    shared = {
        "version": 100, "actual_current_graph_predecessor_version": 99,
        "goal_sha256": GOAL[1], "python": "3.14.6",
        "original_case_execution_denominator": DENOMINATOR, "original_suite_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": 13,
        "authenticated_evidence_owner_lower_bound": 359,
        "authenticated_history_reference_lower_bound": 364,
        "expanded_holdout_proposed_case_count": PROPOSAL,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0, "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0, "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0, "private_build_roots_statted_by_graph": 0,
        "native_binary_files_opened_by_graph": 0,
        "native_binary_metadata_probes_by_graph": 0,
        "hidden_cases_read_by_graph": 0, "clock_samples_by_graph": 0,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED", "timing_trials_run": 0,
        "final_holdout_opened": False, "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    same(inputs, shared, "complete immutable V100 inputs")
    same(summary, shared, "complete immutable V100 publication")
    same(inputs, {"schema": "rebar-candidate-current-overview-v100-inputs"}, "V100 inputs")
    same(summary, {"schema": "rebar-candidate-current-overview-v100-summary",
                   "status": "PASS", "rust_v24_candidate_status": "FAIL",
                   "rust_v24_candidate_qualified": False, "c_v12_candidate_status": "FAIL"},
         "V100 published correctness status")
    require(inputs.get("headline") == summary.get("headline")
            and inputs.get("snapshot") == summary.get("snapshot")
            and inputs.get("previous_overview") == summary.get("previous_overview"),
            "complete V100 inputs, summary, or immutable V99 history diverged")
    same(inputs.get("renderer"), reference(PREVIOUS["source"]), "immutable V100 renderer")
    headline = inputs.get("headline")
    same(headline, {
        "original_python_check_count": DENOMINATOR,
        "c_current_verified_original_checks": 16413,
        "rust_current_verified_original_checks": 15877,
        "zig_current_verified_original_checks": 4607,
        "rust_current_candidate_status": "FAIL", "rust_current_candidate_qualified": False,
        "rust_current_exact_semantic_mismatch_count": 1352,
        "rust_current_semantic_mismatches_by_group": LOSSES,
        "rust_current_completed_original_group_count": 13,
        "rust_current_distinct_candidate_worker_count": 13,
        "rust_current_worker_failure_count": 0,
        "c_current_candidate_execution_failure_count": 1,
        "c_current_observed_individual_mismatch_records": 606,
        "speed_relative_to_python": UNMEASURED, "performance": UNMEASURED,
        "fully_compatible_candidate_count": 0,
        "proposed_final_comparison_case_count": PROPOSAL, "winner_selected": False,
    }, "complete historical V100 current headline")
    same(headline.get("verified_original_checks_by_candidate"), {
        "c": 16413, "rust": 15877, "zig": 4607,
        "cpp": UNMEASURED, "go": UNMEASURED, "fortran": UNMEASURED,
    }, "immutable six-family V100 correctness counts")
    same(summary.get("snapshot"), {
        "version": 100, "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "rust_v23_original_campaign_verified_passing_case_count": 14853,
        "rust_v23_original_campaign_exact_semantic_mismatch_count": 1440,
        "rust_v24_original_campaign_verified_passing_case_count": 15877,
        "rust_v24_original_campaign_semantic_mismatch_count": 1352,
        "rust_v24_original_campaign_semantic_mismatches_by_suite": LOSSES,
        "rust_v24_native_bridge_sha256": V24_BRIDGE,
        "rust_v24_native_engine_sha256": ENGINE,
        "c_v12_original_campaign_verified_passing_case_count": 16413,
        "c_v12_original_campaign_candidate_execution_failure_count": 1,
        "c_v12_original_campaign_complete_observed_individual_mismatch_record_count": 606,
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
    }, "immutable V100 snapshot and historical losses")
    require(type(summary.get("rust_v24_suite_outcomes")) is list
            and len(summary["rust_v24_suite_outcomes"]) == 13,
            "complete V24 original suite outcomes disappeared from immutable V100")
    require(type(summary.get("c_v12_suite_outcomes")) is list
            and len(summary["c_v12_suite_outcomes"]) == 13,
            "complete C12 execution failure and observed outcomes disappeared")
    require(type(summary.get("c_v12_complete_mismatch_suite_vector_fingerprints")) is list
            and len(summary["c_v12_complete_mismatch_suite_vector_fingerprints"]) == 12,
            "complete C12 observed mismatch vector fingerprints disappeared")
    require(svg.startswith(b"<svg ") and b'role="img"' in svg
            and b"15,877 / 31,237" in svg and b"1,352" in svg,
            "the complete accessible V100 correctness overview was replaced")


def verify_contract(contract: dict, protocol: bytes, previous: dict) -> None:
    same(contract, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v25-recoverable-source-freeze",
        "version": 25, "family": "rust", "goal_sha256": GOAL[1],
        "status": "SOURCE FROZEN; V25 BUILD PASS; ORIGINAL CAMPAIGN NOT RUN",
    }, "frozen V25 public campaign sources")
    same(contract.get("source"), reference(CURRENT["source"]), "frozen V25 campaign source")
    same(contract.get("protocol"), reference(CURRENT["protocol"]), "frozen V25 campaign protocol")
    same(contract.get("original_correctness_boundary"), {
        "case_execution_denominator": DENOMINATOR, "suite_count": 13,
        "corrected_reference_case_count": 6912,
        "corrected_reference_counted_in_original_denominator": False,
        "supplemental_reference_case_count": SUPPLEMENTAL,
        "supplemental_counted_in_original_denominator": False,
        "named_private_waiver_count": 13, "candidate_correctness": UNMEASURED,
        "candidate_qualified": False,
        "candidate_semantic_mismatch_count": UNMEASURED,
        "candidate_verified_passing_case_count": UNMEASURED,
    }, "frozen pre-run V25 boundary remains distinct from actual V25 publication")
    frozen_suites = contract["original_correctness_boundary"].get("suites")
    require(type(frozen_suites) is list and len(frozen_suites) == 13,
            "frozen V25 source boundary omitted an original suite")
    for row, (suite, denominator) in zip(frozen_suites, SUITES, strict=True):
        same(row, {"id": suite, "case_execution_denominator": denominator,
                   "candidate_status": "NOT RUN", "candidate_workers_started": 0,
                   "semantic_mismatch_count": UNMEASURED}, "frozen V25 original suite")
    same(contract.get("source_only_effects"), {
        "candidate_correctness": UNMEASURED, "candidate_imports": 0,
        "candidate_workers_started": 0, "reference_workers_started": 0,
        "clock_samples": 0, "compiler_processes_started": 0,
        "compressed_archives_opened": 0, "compressed_archives_inflated": 0,
        "hidden_cases_read": 0, "holdout_cases_opened": 0,
        "native_binary_files_opened": 0, "native_binary_metadata_probes": 0,
        "native_libraries_loaded": 0, "private_roots_opened": 0,
        "private_roots_statted": 0, "subinterpreters_created": 0,
        "threads_started": 0, "timing_trials_run": 0, "network_requests": 0,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "confidence_intervals": UNMEASURED, "undefined_behavior": UNMEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0, "holdout": "NOT OPENED",
        "winner_selected": False,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "expanded_holdout_proposal_case_count": PROPOSAL,
    }, "frozen V25 source-only safety and unopened-holdout boundary")
    native = contract.get("actual_v25_native_build")
    same(native, {
        "build_status": "PASS", "complete_contract_sha256":
            "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a",
        "native_bridge_bytes": 148720, "native_bridge_sha256": V25_BRIDGE,
        "native_engine_bytes": 658344, "native_engine_sha256": ENGINE,
        "corrected_bridge_source_bytes": 178805,
        "corrected_bridge_source_sha256":
            "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54",
        "actual_compiler_process_count": 28,
        "independent_native_artifact_count": 4, "independent_private_phase_count": 2,
        "cross_candidate_engine": "FORBIDDEN",
        "external_regular_expression_engine": "FORBIDDEN",
        "external_cargo_dependency_count": 0, "matching_fallback": "FORBIDDEN",
        "archive_opened": False,
    }, "genuine capture-clamp native source build; private root never opened")
    same(native.get("publication_receipt"), {
        "sha256": "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc",
        "bytes": 5231,
    }, "complete authenticated capture-clamp build publication reference")
    same(contract.get("immutable_actual_v24_candidate_failure"), {
        "candidate_status": "FAIL", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "completed_suite_count": 13, "actual_candidate_workers": 13,
        "verified_passing_case_count": 15877, "semantic_mismatch_count": 1352,
        "fully_observed_suite_mismatch_counts": LOSSES,
        "receipt_sha256": previous["rust_v24_public_evidence"]["receipt"]["sha256"],
        "all_observation_vectors_complete": True,
    }, "V25 source contract preserves exact actual V24 failure")
    same(contract.get("immutable_previous_v24_correctness_campaign"), {
        "candidate_status": "FAIL", "actual_campaign_executed": True,
        "case_execution_denominator": DENOMINATOR,
        "completed_suite_count": 13, "candidate_worker_count": 13,
        "semantic_mismatch_count": 1352, "verified_passing_case_count": 15877,
    }, "actual V24 correctness is not mistaken for source-only V25 status")
    same(contract.get("operational_runtime_guard_v4"), {
        "version": 4, "complete_contract_sha256":
            "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
        "guard_installed_before_candidate_import": True,
        "cross_candidate_engine": "FORBIDDEN", "external_regex_package": "FORBIDDEN",
        "matching_fallback": "FORBIDDEN", "stdlib_re_engine": "FORBIDDEN",
        "stdlib_sre_engine": "FORBIDDEN", "runtime_non_delegation": "NOT ESTABLISHED",
    }, "operational guard does not magically establish non-delegation")
    investigation = contract.get("independent_runtime_non_delegation_v4_audit")
    same(investigation, {
        "status": "FAIL", "finding_count": 1, "finding_code": FINDING,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "public_matching_delegation": "NOT PROVEN", "candidate_qualified": False,
        "audit_is_separate_from_original_correctness": True,
    }, "independently frozen V4 static non-delegation FAIL-1")
    same(investigation.get("actual_failure_receipt_owner"), reference(AUDIT),
         "independently frozen complete static V4 audit failure owner")
    for token in (b"capture-clamp", b"1,352", b"240", b"1,112",
                  b"CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE", b"not\nproof",
                  b"NOT OPENED", b"141,557,760"):
        require(token in protocol, "complete V25 public protocol omitted " + token.decode())
    require(previous["snapshot"]["rust_v24_native_bridge_sha256"] != native["native_bridge_sha256"]
            and previous["snapshot"]["rust_v24_native_engine_sha256"] == native["native_engine_sha256"],
            "capture-clamp bridge did not change independently while first-party engine stayed fixed")


def verify_audit(audit: dict) -> None:
    same(audit, {
        "schema": "rebar-phase2-first-party-runtime-non-delegation-v4-root-static-audit",
        "status": "FAIL", "finding_count": 1, "candidate_family_count": 6,
        "runtime_non_delegation": "NOT ESTABLISHED; CANDIDATES NEVER EXECUTED",
        "candidate_qualified": False, "performance": UNMEASURED,
        "holdout": "NOT OPENED", "winner_selected": False,
        "phase": "ROOT-AUTHORIZED READ-ONLY SOURCE AND ELF AUDIT",
        "root_authorized": True,
    }, "actual complete independent V4 static audit FAIL-1")
    findings = audit.get("findings")
    require(type(findings) is list and len(findings) == 1,
            "independent V4 candidate-owned FAIL-1 was removed or inflated")
    same(findings[0], {
        "code": FINDING, "family": "rust", "path": "candidates/rust/py_bridge.c",
        "provenance": "CANDIDATE_OWNED", "severity": "FAIL",
        "reachability": "PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN",
        "import_chain": ["candidate native bridge", "inspect", "tokenize", "re", "re.compile"],
    }, "actual latent private bridge escape hatch; public matching delegation not proven")
    same(audit.get("rust_reachability"), {
        "classification": "LATENT_PRIVATE_BRIDGE_ESCAPE_HATCH; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN",
        "public_matching_delegation_proven": False,
        "bridge_exports_private_bind": True,
    }, "static reachability is not proof of actual public matching delegation")
    same(audit.get("effects"), {
        "candidate_executions": 0, "candidate_imports": 0, "candidate_workers": 0,
        "native_library_loads": 0, "archive_reads": 0, "archive_decompressions": 0,
        "benchmark_reads": 0, "holdout_reads": 0, "hidden_case_reads": 0,
        "clock_samples": 0, "compiler_processes": 0, "network_requests": 0,
        "workspace_mutations": 0,
    }, "historical non-delegation audit never executed matching or opened holdouts")


def verify_receipt(receipt: dict, contract: dict, previous: dict) -> None:
    same(receipt, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY", "family": "rust",
        "label": "phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "case_execution_denominator": DENOMINATOR, "suite_count": 13,
        "attempted_suite_count": 13, "started_suite_count": 13,
        "completed_suite_count": 13, "verified_passing_case_count": 15877,
        "semantic_mismatch_count": 1352, "actual_candidate_workers": 13,
        "distinct_worker_process_id_count": 13, "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "worker_failure_capture_count": 0, "all_worker_failure_capture_count": 0,
        "worker_failure_capture_complete": True, "infrastructure_failure_count": 0,
        "all_original_observation_vectors_complete": True,
        "all_original_suite_rows_validated_before_publication": True,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "campaign_source_sha256": CURRENT["source"][1],
        "campaign_protocol_sha256": CURRENT["protocol"][1],
        "campaign_contract_sha256": CURRENT["contract"][1],
        "actual_v25_build_contract_sha256":
            "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a",
        "actual_v25_build_receipt_sha256":
            "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc",
        "native_bridge_sha256": V25_BRIDGE, "native_bridge_bytes": 148720,
        "native_engine_sha256": ENGINE, "native_engine_bytes": 658344,
        "actual_v25_build_archive_read_count": 0,
        "actual_v25_build_archive_gzip_inflation_count": 0,
        "actual_v25_compiler_process_count": 28,
        "corrected_reference_case_count": 6912,
        "candidate_run_uses_both_complete_reference_vectors": True,
        "named_private_waiver_count": 13,
        "preserved_previous_rust_verified_passing_case_count": 14853,
        "preserved_previous_rust_semantic_mismatch_count": 1440,
        "clock_samples": 0, "timing_trials_run": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": UNMEASURED, "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED, "holdout": "NOT OPENED",
        "winner_selected": False,
    }, "actual complete V25 public publication passed; candidate correctness failed")
    processes = receipt.get("actual_worker_process_ids")
    require(type(processes) is list and len(processes) == len(set(processes)) == 13,
            "actual V25 original campaign lacked 13 distinct workers")
    require(receipt.get("all_worker_failure_captures") == [],
            "actual V25 bounded worker failure evidence was suppressed")
    same(receipt.get("worker_failure_capture"), {
        "actual_failure_count": 0, "all_failure_metadata_preserved": True,
        "first_worker_failure": None, "suite_failure_summaries": [],
    }, "complete actual V25 worker diagnostics")
    rows = receipt.get("suite_integrity")
    old = previous.get("rust_v24_suite_outcomes")
    require(type(rows) is list and type(old) is list and len(rows) == len(old) == 13,
            "actual complete V25/V24 suite vectors were omitted")
    passing = mismatch = passing_groups = 0
    seen = []
    for row, old_row, (suite, denominator) in zip(rows, old, SUITES, strict=True):
        failures = LOSSES.get(suite, 0)
        verified = 0 if failures else denominator
        expected = {
            "suite": suite, "case_execution_denominator": denominator,
            "verified_passing_case_count": verified,
            "mismatch_count": failures,
            "failure_class": "SEMANTIC MISMATCH" if failures else "PASS",
            "returncode": 1 if failures else 0,
            "fully_observed": True, "worker_attempted": True,
            "actual_worker_started": True,
        }
        same(row, expected, "actual complete V25 original suite " + suite)
        same(old_row, expected, "immutable complete V24 original suite " + suite)
        require(type(row.get("complete_original_row_sha256")) is str
                and len(row["complete_original_row_sha256"]) == 64,
                "actual V25 complete original suite vector fingerprint disappeared")
        require(row.get("pid") in processes, "actual V25 suite used an unknown process")
        seen.append(row["pid"])
        passing += verified
        mismatch += failures
        passing_groups += failures == 0
    require(len(set(seen)) == 13 and passing == 15877 and mismatch == 1352
            and passing_groups == 11,
            "capture-clamp candidate's unchanged compatibility or exact losses were fabricated")
    same(receipt.get("archive"), {
        "sha256": ARCHIVE_SHA256, "size_bytes": 3771743, "mode": 0o600,
        "exclusive_creation": True, "file_fsync_completed": True,
        "directory_fsync_completed": True, "same_inode_readback_verified": True,
        "streaming_readback_verified": True,
        "relative": "repaired-rust-original-campaign-v16-rust-phase2-v25-"
                    "rust-capture-clamp-v1-root-provenance-original-p0-v25-failures.json.gz",
    }, "complete unopened capture-clamp failure archive; metadata from receipt only")
    require(type(receipt.get("restored_original_targets")) is dict
            and set(receipt["restored_original_targets"])
            == {"adapter", "bridge", "engine", "bridge_source"},
            "actual V25 original candidate targets were not restored")
    same(contract["actual_v25_native_build"], {
        "native_bridge_sha256": receipt["native_bridge_sha256"],
        "native_engine_sha256": receipt["native_engine_sha256"],
        "complete_contract_sha256": receipt["actual_v25_build_contract_sha256"],
    }, "capture-clamp build and actual campaign bridge provenance diverged")
    require(previous["headline"]["rust_current_verified_original_checks"]
            == receipt["verified_passing_case_count"]
            and previous["headline"]["rust_current_exact_semantic_mismatch_count"]
            == receipt["semantic_mismatch_count"],
            "safety-only capture clamp falsely claimed improved original compatibility")


def verify(context: dict) -> None:
    require(context["goal"].startswith(b"/goal ") and digest(context["goal"]) == GOAL[1],
            "complete immutable experiment goal changed")
    verify_previous(context["previous_inputs"], context["previous_summary"], context["previous_svg"])
    verify_contract(context["contract"], context["protocol"], context["previous_inputs"])
    verify_audit(context["audit"])
    verify_receipt(context["receipt"], context["contract"], context["previous_summary"])


def escaped(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def graph() -> bytes:
    rows = (
        ("Python re", DENOMINATOR, "All 13 groups pass", "REFERENCE", "#34d399"),
        ("C", 16413, "12 groups complete; 1 execution failure", "NOT COMPATIBLE", "#fbbf24"),
        ("Rust", 15877, "13 groups complete; 1,352 cases differ", "NOT COMPATIBLE", "#60a5fa"),
        ("Zig", 4607, "Previously verified original checks", "NOT COMPATIBLE", "#fbbf24"),
        ("C++", None, "Complete original correctness not measured", UNMEASURED, "#94a3b8"),
        ("Go", None, "Complete original correctness not measured", UNMEASURED, "#94a3b8"),
        ("Fortran", None, "Complete original correctness not measured", UNMEASURED, "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1215" '
        'viewBox="0 0 1480 1215" role="img" aria-labelledby="title description">',
        '<title id="title">Candidate correctness: Rust safety changed, compatibility did not</title>',
        '<desc id="description">Original public correctness, not speed: Python passes 31,237 '
        'of 31,237 checks, C verifies 16,413, Rust verifies 15,877, and Zig verifies 4,607. '
        'C++, Go, and Fortran remain unmeasured. Rust V25 changed its native capture-clamp bridge '
        'but improved zero compatibility checks over Rust V24: the same 1,352 semantic losses '
        'remain, 240 substitution and 1,112 shape. All 13 groups completed in 13 distinct workers '
        'and 11 groups passed. A separate non-delegation audit failed with one latent private '
        'candidate-owned import-chain finding; actual public matching delegation was not proven. '
        'No candidate qualifies. Speed and final memory are not measured. The proposed '
        '141,557,760-case final comparison is not frozen, generated, or opened.</desc>',
        '<rect width="1480" height="1215" rx="24" fill="#0b1220"/>',
        '<text x="57" y="77" fill="#f8fafc" font-size="35" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        'Can a replacement match Python re exactly?</text>',
        '<text x="60" y="112" fill="#cbd5e1" font-size="19" '
        'font-family="system-ui,sans-serif">These bars measure correctness, never speed.</text>',
        '<rect x="57" y="139" width="1365" height="106" rx="15" fill="#132238" stroke="#30445e"/>',
        '<text x="79" y="174" fill="#93c5fd" font-size="19" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'Rust V25 safety change: compatibility stayed exactly the same</text>',
        '<text x="80" y="208" fill="#f8fafc" font-size="17" '
        'font-family="system-ui,sans-serif">'
        '15,877 / 31,237 verified  ·  +0 checks versus V24  ·  1,352 failures remain</text>',
        '<text x="67" y="280" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="650">APPROACH</text>',
        '<text x="180" y="280" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="650">ORIGINAL CHECKS PASSED</text>',
        '<text x="758" y="280" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="650">WHAT IT MEANS</text>',
        '<text x="1272" y="280" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="650">SPEED</text>',
    ]
    for number, (label, count, detail, status, color) in enumerate(rows):
        top = 303 + number * 79
        bottom = top + 34
        fill = "#11243a" if label == "Rust" else "#101b2b"
        parts.append(f'<rect x="57" y="{top}" width="1365" height="67" rx="11" fill="{fill}"/>')
        parts.append(f'<text x="76" y="{bottom}" fill="#f8fafc" font-size="18" '
                     f'font-family="system-ui,sans-serif" font-weight="680">{escaped(label)}</text>')
        parts.append(f'<rect x="180" y="{top + 14}" width="330" height="18" rx="6" fill="#29384e"/>')
        if count is None:
            value = UNMEASURED
        else:
            width = round(330 * count / DENOMINATOR)
            parts.append(f'<rect x="180" y="{top + 14}" width="{width}" height="18" '
                         f'rx="6" fill="{color}"/>')
            percentage = "100%" if count == DENOMINATOR else f"{100 * count / DENOMINATOR:.1f}%"
            value = f"{count:,} / {DENOMINATOR:,}  ·  {percentage}"
        parts.append(f'<text x="522" y="{bottom}" fill="#e2e8f0" font-size="15" '
                     f'font-family="system-ui,sans-serif">{escaped(value)}</text>')
        parts.append(f'<text x="758" y="{bottom}" fill="#e2e8f0" font-size="14" '
                     f'font-family="system-ui,sans-serif">{escaped(detail)}</text>')
        parts.append(f'<text x="758" y="{top + 56}" fill="{color}" font-size="12" '
                     f'font-family="system-ui,sans-serif" font-weight="690">{escaped(status)}</text>')
        parts.append(f'<text x="1267" y="{bottom}" fill="#cbd5e1" font-size="13" '
                     f'font-family="system-ui,sans-serif">{UNMEASURED}</text>')
    parts.extend([
        '<rect x="58" y="880" width="669" height="185" rx="14" fill="#142135" stroke="#354459"/>',
        '<text x="82" y="912" fill="#93c5fd" font-size="18" '
        'font-family="system-ui,sans-serif" font-weight="730">What changed — and what did not</text>',
        '<text x="82" y="945" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">Capture-clamp bridge changed; the engine stayed the same.</text>',
        '<text x="82" y="974" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">13 of 13 groups ran; 11 passed; 13 workers were distinct.</text>',
        '<text x="82" y="1004" fill="#fda4af" font-size="14" '
        'font-family="system-ui,sans-serif">Exact unchanged losses: 240 substitution + 1,112 shape = 1,352.</text>',
        '<text x="82" y="1034" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">Rust candidate: FAIL. Compatibility improvement: ZERO.</text>',
        '<rect x="746" y="880" width="676" height="185" rx="14" fill="#291923" stroke="#754453"/>',
        '<text x="769" y="912" fill="#fda4af" font-size="18" '
        'font-family="system-ui,sans-serif" font-weight="730">'
        'Independent non-delegation audit: FAIL</text>',
        '<text x="769" y="945" fill="#f8fafc" font-size="14" '
        'font-family="system-ui,sans-serif">One candidate-owned private import-chain finding remains.</text>',
        '<text x="769" y="974" fill="#e2e8f0" font-size="13" '
        'font-family="system-ui,sans-serif">bridge → inspect → tokenize → re → re.compile</text>',
        '<text x="769" y="1004" fill="#e2e8f0" font-size="13" '
        'font-family="system-ui,sans-serif">Latent reachability; actual matching delegation: NOT PROVEN.</text>',
        '<text x="769" y="1034" fill="#fda4af" font-size="14" '
        'font-family="system-ui,sans-serif">Runtime independence: NOT ESTABLISHED. No qualification.</text>',
        '<rect x="59" y="1080" width="1363" height="89" rx="13" fill="#142237" stroke="#30445e"/>',
        '<text x="81" y="1116" fill="#fcd34d" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'FINAL SPEED: NOT MEASURED  ·  FINAL MEMORY: NOT MEASURED  ·  NO WINNER</text>',
        '<text x="81" y="1147" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">'
        '141,557,760-case final comparison: NOT FROZEN; NOT GENERATED; NOT OPENED.</text>',
        '<text x="65" y="1195" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'Original denominator: 31,237. Separate supplemental checks: 8,244. '
        'No correctness loss or failed independence finding is hidden.</text>',
        '</svg>',
    ])
    return ("\n".join(parts) + "\n").encode("utf-8")


def assets(context: dict, source_sha: str, source_size: int) -> dict[str, bytes]:
    receipt = context["receipt"]
    before = context["previous_inputs"]
    old = context["previous_summary"]
    headline = {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "python_version": "3.14.6",
        "bars_measure": "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED",
        "original_python_check_count": DENOMINATOR,
        "original_python_suite_count": 13,
        "separate_additional_differential_check_count": SUPPLEMENTAL,
        "separate_additional_checks_in_original_denominator": False,
        "verified_original_checks_by_candidate": {
            "c": 16413, "rust": 15877, "zig": 4607,
            "cpp": UNMEASURED, "go": UNMEASURED, "fortran": UNMEASURED,
        },
        "c_current_verified_original_checks": 16413,
        "c_current_candidate_status": "FAIL",
        "c_current_candidate_execution_failure_count": 1,
        "c_current_observed_individual_mismatch_records": 606,
        "rust_current_verified_original_checks": 15877,
        "rust_previous_graph_verified_original_checks": 15877,
        "rust_verified_check_change_from_previous_graph": 0,
        "rust_previous_actual_v24_verified_original_checks": 15877,
        "rust_verified_check_change_from_actual_v24": 0,
        "rust_current_candidate_status": "FAIL",
        "rust_current_candidate_qualified": False,
        "rust_current_original_group_count": 13,
        "rust_current_completed_original_group_count": 13,
        "rust_current_passing_original_group_count": 11,
        "rust_current_exact_semantic_mismatch_count": 1352,
        "rust_previous_actual_v24_exact_semantic_mismatch_count": 1352,
        "rust_semantic_mismatch_change_from_actual_v24": 0,
        "rust_current_semantic_mismatches_by_group": dict(LOSSES),
        "rust_current_distinct_candidate_worker_count": 13,
        "rust_current_worker_failure_count": 0,
        "rust_current_infrastructure_failure_count": 0,
        "rust_capture_clamp_bridge_changed": True,
        "rust_native_engine_changed": False,
        "rust_capture_clamp_status": "BUILT; UNDEFINED-BEHAVIOR SAFETY NOT MEASURED",
        "rust_capture_clamp_compatibility_improvement": "NONE",
        "independent_nondelegation_audit_status": "FAIL",
        "independent_nondelegation_finding_count": 1,
        "independent_nondelegation_finding_code": FINDING,
        "runtime_no_delegation": "NOT ESTABLISHED; INDEPENDENT V4 STATIC AUDIT FAIL",
        "actual_public_matching_delegation_proven": False,
        "zig_current_verified_original_checks": 4607,
        "independent_first_party_candidate_family_count": 6,
        "fully_compatible_candidate_count": 0,
        "performance": UNMEASURED, "speed_relative_to_python": UNMEASURED,
        "memory": UNMEASURED, "undefined_behavior": UNMEASURED,
        "proposed_final_comparison_case_count": PROPOSAL,
        "proposed_final_comparison_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "winner_selected": False,
        "public_reporting_integrity":
            "EXACT V25/V24 LOSS VECTORS UNCHANGED; STATIC FAIL-1 SEPARATE; C12 FAILURE PRESERVED",
    }
    snapshot = {
        "schema": "rebar-candidate-current-overview-v101-compact-current-snapshot",
        "version": 101, "actual_current_graph_predecessor_version": 100,
        "goal_sha256": GOAL[1],
        "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": 13,
        "c_v12_original_campaign_candidate_status": "FAIL",
        "c_v12_original_campaign_verified_passing_case_count": 16413,
        "c_v12_original_campaign_completed_suite_count": 12,
        "c_v12_original_campaign_candidate_execution_failure_count": 1,
        "c_v12_original_campaign_complete_observed_individual_mismatch_record_count": 606,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "rust_v23_original_campaign_verified_passing_case_count": 14853,
        "rust_v23_original_campaign_semantic_mismatch_count": 1440,
        "rust_v24_original_campaign_candidate_status": "FAIL",
        "rust_v24_original_campaign_verified_passing_case_count": 15877,
        "rust_v24_original_campaign_semantic_mismatch_count": 1352,
        "rust_v24_original_campaign_semantic_mismatches_by_suite": dict(LOSSES),
        "rust_v24_native_bridge_sha256": V24_BRIDGE,
        "rust_v25_original_campaign_candidate_status": "FAIL",
        "rust_v25_original_campaign_candidate_qualified": False,
        "rust_v25_original_campaign_verified_passing_case_count": 15877,
        "rust_v25_verified_passing_case_change_from_v100": 0,
        "rust_v25_verified_passing_case_change_from_v24": 0,
        "rust_v25_original_campaign_completed_suite_count": 13,
        "rust_v25_original_campaign_passing_suite_count": 11,
        "rust_v25_original_campaign_semantic_mismatch_count": 1352,
        "rust_v25_original_campaign_semantic_mismatch_change_from_v24": 0,
        "rust_v25_original_campaign_semantic_mismatches_by_suite": dict(LOSSES),
        "rust_v25_original_campaign_distinct_worker_count": 13,
        "rust_v25_original_campaign_worker_failure_count": 0,
        "rust_v25_original_campaign_infrastructure_failure_count": 0,
        "rust_v25_native_bridge_sha256": V25_BRIDGE,
        "rust_v25_native_engine_sha256": ENGINE,
        "rust_v25_native_bridge_changed_from_v24": True,
        "rust_v25_native_engine_changed_from_v24": False,
        "rust_v25_capture_clamp_compatibility_improvement": "NONE",
        "rust_v25_undefined_behavior": UNMEASURED,
        "independent_v4_nondelegation_status": "FAIL",
        "independent_v4_nondelegation_finding_count": 1,
        "independent_v4_nondelegation_finding_code": FINDING,
        "actual_public_matching_delegation_proven": False,
        "runtime_no_delegation": "NOT ESTABLISHED; INDEPENDENT V4 STATIC AUDIT FAIL",
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
        "expanded_holdout_proposed_case_count": PROPOSAL,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "authenticated_evidence_owner_lower_bound": 359,
        "authenticated_history_reference_lower_bound": 364,
        "v101_new_directly_authenticated_public_owner_count": 5,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "timing_trials_run": 0, "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    previous = {name: reference(spec) for name, spec in PREVIOUS.items()}
    current = {name: reference(spec) for name, spec in CURRENT.items()}
    boundary = {
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "compressed_archives_inflated_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "private_build_roots_statted_by_graph": 0,
        "native_binary_files_opened_by_graph": 0,
        "native_binary_metadata_probes_by_graph": 0,
        "native_libraries_loaded_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "clock_samples_by_graph": 0,
        "timing_trials_run": 0,
        "final_holdout_opened": False,
    }
    inputs = {
        "schema": "rebar-candidate-current-overview-v101-inputs",
        "version": 101, "actual_current_graph_predecessor_version": 100,
        "goal_sha256": GOAL[1], "python": "3.14.6",
        "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": 13,
        "previous_overview": previous,
        "preserved_complete_history":
            "EXACT DIGEST-BOUND V100 SOURCE, INPUTS, SUMMARY, AND SVG; ALL V99 HISTORY RETAINED",
        "rust_v25_public_evidence": current,
        "independent_v4_nondelegation_failure": reference(AUDIT),
        "expanded_holdout_v2_public_proposal": before["expanded_holdout_v2_public_proposal"],
        "renderer": {"path": SELF, "sha256": source_sha, "bytes": source_size},
        "headline": headline, "snapshot": snapshot,
        "complete_original_suites": [
            {"suite": suite, "case_execution_denominator": count}
            for suite, count in SUITES
        ],
        **boundary,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_proposed_case_count": PROPOSAL,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED; INDEPENDENT V4 STATIC AUDIT FAIL",
        "independent_nondelegation_audit_status": "FAIL",
        "independent_nondelegation_finding_count": 1,
        "qualified_candidate_count": 0, "winner_selected": False,
        "authenticated_evidence_owner_lower_bound": 359,
        "authenticated_history_reference_lower_bound": 364,
        "v101_new_directly_authenticated_public_owner_count": 5,
    }
    publication = dict(inputs)
    publication.update({
        "schema": "rebar-candidate-current-overview-v101-summary",
        "status": "PASS",
        "status_scope":
            "AUTHENTICATED CORRECTNESS GRAPH ONLY; V25 CANDIDATE FAIL; INDEPENDENT V4 AUDIT FAIL-1",
        "rust_v25_publication_status": receipt["publication_status"],
        "rust_v25_publication_pass_means": receipt["publication_pass_means"],
        "rust_v25_candidate_status": receipt["candidate_status"],
        "rust_v25_candidate_qualified": receipt["candidate_qualified"],
        "rust_v25_suite_outcomes": receipt["suite_integrity"],
        "rust_v25_all_observed_original_suite_vectors_complete":
            receipt["all_original_observation_vectors_complete"],
        "rust_v25_all_worker_failure_captures": receipt["all_worker_failure_captures"],
        "rust_v25_worker_failure_capture": receipt["worker_failure_capture"],
        "rust_v25_restored_original_targets": receipt["restored_original_targets"],
        "rust_v25_unopened_archive_metadata": {
            "path": receipt["archive"]["path"],
            "sha256": receipt["archive"]["sha256"],
            "bytes": receipt["archive"]["size_bytes"],
            "opened_by_graph": False, "statted_by_graph": False,
            "inflated_by_graph": False,
        },
        "rust_v24_preserved_candidate_status": old["rust_v24_candidate_status"],
        "rust_v24_preserved_suite_outcomes": old["rust_v24_suite_outcomes"],
        "rust_v24_preserved_unopened_archive_metadata": old["rust_v24_unopened_archive_metadata"],
        "c_v12_candidate_status": old["c_v12_candidate_status"],
        "c_v12_candidate_qualified": old["c_v12_candidate_qualified"],
        "c_v12_suite_outcomes": old["c_v12_suite_outcomes"],
        "c_v12_complete_mismatch_suite_vector_fingerprints":
            old["c_v12_complete_mismatch_suite_vector_fingerprints"],
        "independent_v4_nondelegation_status": context["audit"]["status"],
        "independent_v4_nondelegation_finding_count": context["audit"]["finding_count"],
        "independent_v4_nondelegation_findings": context["audit"]["findings"],
        "independent_v4_nondelegation_rust_reachability": context["audit"]["rust_reachability"],
        "independent_v4_nondelegation_audit_effects": context["audit"]["effects"],
        "previous_complete_overview_sha256": PREVIOUS["summary"][1],
        "previous_complete_overview_bytes": PREVIOUS["summary"][2],
        "expanded_holdout_v2_gate_status": old["expanded_holdout_v2_gate_status"],
        "expanded_holdout_v2_timing_status": old["expanded_holdout_v2_timing_status"],
    })
    return {"svg": graph(), "inputs": canonical(inputs), "summary": canonical(publication)}


def validate_outputs(context: dict, result: dict, source_sha: str, source_size: int) -> None:
    require(result == assets(context, source_sha, source_size),
            "V101 publication is nondeterministic or lost exact historical evidence")
    inputs = parsed(result["inputs"], "V101 authenticated inputs")
    summary = parsed(result["summary"], "V101 complete publication")
    shared = {
        "version": 101, "actual_current_graph_predecessor_version": 100,
        "original_case_execution_denominator": DENOMINATOR,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED; INDEPENDENT V4 STATIC AUDIT FAIL",
        "independent_nondelegation_audit_status": "FAIL",
        "independent_nondelegation_finding_count": 1,
        "expanded_holdout_proposed_case_count": PROPOSAL,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "final_holdout_opened": False, "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    same(inputs, shared, "honest complete V101 public inputs")
    same(summary, shared, "honest complete V101 public publication")
    same(summary, {"status": "PASS", "rust_v25_candidate_status": "FAIL",
                   "rust_v25_candidate_qualified": False,
                   "independent_v4_nondelegation_status": "FAIL",
                   "independent_v4_nondelegation_finding_count": 1},
         "V101 publication PASS is not a candidate or independence PASS")
    require(inputs["headline"] == summary["headline"]
            and inputs["snapshot"] == summary["snapshot"]
            and inputs["previous_overview"] == summary["previous_overview"],
            "complete immutable V101 publication and inputs diverge")
    require(len(summary.get("rust_v25_suite_outcomes", [])) == 13
            and len(summary.get("rust_v24_preserved_suite_outcomes", [])) == 13
            and len(summary.get("c_v12_suite_outcomes", [])) == 13
            and len(summary.get("independent_v4_nondelegation_findings", [])) == 1,
            "V101 lost V25, V24, historical C12, or static FAIL-1 evidence")
    same(summary["rust_v25_unopened_archive_metadata"], {
        "sha256": ARCHIVE_SHA256, "bytes": 3771743,
        "opened_by_graph": False, "statted_by_graph": False, "inflated_by_graph": False,
    }, "V101 must preserve compressed failure evidence without opening the gzip")
    tokens = (b"15,877 / 31,237", b"+0 checks versus V24", b"1,352", b"240 substitution",
              b"1,112 shape", b"13 of 13", b"Independent non-delegation audit: FAIL",
              b"One candidate-owned", b"NOT PROVEN", b"NOT ESTABLISHED",
              b"FINAL SPEED: NOT MEASURED", b"FINAL MEMORY: NOT MEASURED",
              b"141,557,760", b"NOT FROZEN; NOT GENERATED; NOT OPENED",
              b"16,413 / 31,237", b"4,607 / 31,237")
    for token in tokens:
        require(token in result["svg"], "readable V101 correctness graph omitted " + token.decode())
    require(b'role="img"' in result["svg"]
            and b'aria-labelledby="title description"' in result["svg"],
            "readable V101 correctness graph lost its accessible title or description")


def self_test(context: dict, result: dict, source_sha: str, source_size: int,
              wall: SourceWall) -> int:
    labels = []

    def reject(label: str, mutation) -> None:
        hostile = copy.deepcopy(context)
        mutation(hostile)
        try:
            verify(hostile)
        except (Rejected, TypeError, ValueError, KeyError, IndexError):
            labels.append(label)
            return
        raise Rejected("hostile immutable correctness evidence was accepted: " + label)

    reject("immutable goal changed", lambda x: x.__setitem__("goal", x["goal"] + b"!"))
    reject("V100 renderer pin replaced", lambda x: x["previous_inputs"]["renderer"].__setitem__("sha256", "0" * 64))
    reject("V100 complete history dropped", lambda x: x["previous_inputs"]["previous_overview"].pop("svg"))
    reject("V100 original denominator inflated", lambda x: x["previous_summary"].__setitem__("original_case_execution_denominator", DENOMINATOR + SUPPLEMENTAL))
    reject("V100 Rust current loss hidden", lambda x: x["previous_summary"]["headline"].__setitem__("rust_current_exact_semantic_mismatch_count", 1351))
    reject("V100 C execution failure hidden", lambda x: x["previous_summary"]["snapshot"].__setitem__("c_v12_original_campaign_candidate_execution_failure_count", 0))
    reject("V100 historical Rust suite hidden", lambda x: x["previous_summary"]["rust_v24_suite_outcomes"].pop())
    reject("V100 historical C mismatch vector hidden", lambda x: x["previous_summary"]["c_v12_complete_mismatch_suite_vector_fingerprints"].pop())
    reject("V100 accessible SVG fabricated", lambda x: x.__setitem__("previous_svg", b"<svg/>"))
    for label, key, value in (
        ("V25 frozen contract goal replaced", "goal_sha256", "0" * 64),
        ("V25 frozen contract falsely passed candidate", "status", "CANDIDATE PASS"),
    ):
        reject(label, lambda x, k=key, v=value: x["contract"].__setitem__(k, v))
    reject("V25 contract source pin replaced", lambda x: x["contract"]["source"].__setitem__("sha256", "0" * 64))
    reject("V25 corrected references counted as original", lambda x: x["contract"]["original_correctness_boundary"].__setitem__("corrected_reference_counted_in_original_denominator", True))
    reject("V25 supplemental references counted as original", lambda x: x["contract"]["original_correctness_boundary"].__setitem__("supplemental_counted_in_original_denominator", True))
    reject("V25 frozen suite hidden", lambda x: x["contract"]["original_correctness_boundary"]["suites"].pop())
    reject("V25 source gate opened gzip", lambda x: x["contract"]["source_only_effects"].__setitem__("compressed_archives_opened", 1))
    reject("V25 source gate started candidate", lambda x: x["contract"]["source_only_effects"].__setitem__("candidate_workers_started", 1))
    reject("V25 source gate opened holdout", lambda x: x["contract"]["source_only_effects"].__setitem__("holdout_cases_opened", 1))
    reject("V25 capture-clamp bridge unchanged", lambda x: x["contract"]["actual_v25_native_build"].__setitem__("native_bridge_sha256", V24_BRIDGE))
    reject("V25 first-party native engine replaced", lambda x: x["contract"]["actual_v25_native_build"].__setitem__("native_engine_sha256", "0" * 64))
    reject("V25 previous exact losses hidden", lambda x: x["contract"]["immutable_actual_v24_candidate_failure"].__setitem__("semantic_mismatch_count", 1351))
    reject("V25 independent audit falsely passes", lambda x: x["contract"]["independent_runtime_non_delegation_v4_audit"].__setitem__("status", "PASS"))
    reject("V25 independent audit finding hidden", lambda x: x["contract"]["independent_runtime_non_delegation_v4_audit"].__setitem__("finding_count", 0))
    reject("V25 matching delegation falsely proven", lambda x: x["contract"]["independent_runtime_non_delegation_v4_audit"].__setitem__("public_matching_delegation", "PROVEN"))
    reject("V25 static failure owner substituted", lambda x: x["contract"]["independent_runtime_non_delegation_v4_audit"]["actual_failure_receipt_owner"].__setitem__("sha256", "0" * 64))
    for label, key, value in (
        ("V25 candidate falsely passes", "candidate_status", "PASS"),
        ("V25 candidate falsely qualifies", "candidate_qualified", True),
        ("V25 publication PASS redefined", "publication_pass_means", "CANDIDATE CORRECTNESS"),
        ("V25 score falsely improved", "verified_passing_case_count", 15878),
        ("V25 exact loss hidden", "semantic_mismatch_count", 1351),
        ("V25 denominator inflated", "case_execution_denominator", DENOMINATOR + SUPPLEMENTAL),
        ("V25 complete suite lost", "completed_suite_count", 12),
        ("V25 candidate worker duplicated", "distinct_worker_process_id_count", 12),
        ("V25 worker failure hidden", "worker_failure_capture_count", 1),
        ("V25 corrected references changed", "corrected_reference_case_count", 6913),
        ("V25 previous Rust loss erased", "preserved_previous_rust_semantic_mismatch_count", 1352),
        ("V25 native engine provenance changed", "native_engine_sha256", "0" * 64),
        ("V25 build archive secretly opened", "actual_v25_build_archive_read_count", 1),
        ("V25 speed invented", "performance", "1.5x"),
        ("V25 hidden case opened", "hidden_cases_read", 1),
        ("V25 holdout opened", "holdout", "OPENED"),
        ("V25 winner invented", "winner_selected", True),
    ):
        reject(label, lambda x, k=key, v=value: x["receipt"].__setitem__(k, v))
    reject("V25 exact substitution loss understated", lambda x: x["receipt"]["suite_integrity"][7].__setitem__("mismatch_count", 239))
    reject("V25 exact shape loss understated", lambda x: x["receipt"]["suite_integrity"][8].__setitem__("mismatch_count", 1111))
    reject("V25 distinct worker reused", lambda x: x["receipt"]["actual_worker_process_ids"].__setitem__(1, x["receipt"]["actual_worker_process_ids"][0]))
    reject("V25 failure gzip digest replaced", lambda x: x["receipt"]["archive"].__setitem__("sha256", "0" * 64))
    reject("V25 failure gzip size truncated", lambda x: x["receipt"]["archive"].__setitem__("size_bytes", 3771742))
    reject("V25 restored native owner removed", lambda x: x["receipt"]["restored_original_targets"].pop("engine"))
    reject("independent V4 audit falsely passes", lambda x: x["audit"].__setitem__("status", "PASS"))
    reject("independent V4 audit finding erased", lambda x: x["audit"].__setitem__("finding_count", 0))
    reject("independent V4 finding list erased", lambda x: x["audit"]["findings"].pop())
    reject("independent V4 candidate-owned chain hidden", lambda x: x["audit"]["findings"][0]["import_chain"].pop())
    reject("independent V4 public matching delegation invented", lambda x: x["audit"]["rust_reachability"].__setitem__("public_matching_delegation_proven", True))
    reject("independent V4 runtime independence falsely established", lambda x: x["audit"].__setitem__("runtime_non_delegation", "ESTABLISHED"))
    reject("independent V4 historical candidate execution invented", lambda x: x["audit"]["effects"].__setitem__("candidate_executions", 1))
    reject("V25 public protocol final holdout status removed", lambda x: x.__setitem__("protocol", x["protocol"].replace(b"NOT OPENED", b"WITHHELD")))

    def reject_output(label: str, key: str, mutation) -> None:
        altered = dict(result)
        value = parsed(altered[key], "hostile generated V101 output")
        mutation(value)
        altered[key] = canonical(value)
        try:
            validate_outputs(context, altered, source_sha, source_size)
        except (Rejected, TypeError, ValueError, KeyError):
            labels.append(label)
            return
        raise Rejected("hostile V101 public output was accepted: " + label)

    reject_output("V101 publication candidate passes", "summary", lambda x: x.__setitem__("rust_v25_candidate_status", "PASS"))
    reject_output("V101 publication static finding hidden", "summary", lambda x: x["independent_v4_nondelegation_findings"].pop())
    reject_output("V101 publication history erased", "summary", lambda x: x["rust_v24_preserved_suite_outcomes"].pop())
    reject_output("V101 publication gzip falsely opened", "summary", lambda x: x["rust_v25_unopened_archive_metadata"].__setitem__("opened_by_graph", True))
    reject_output("V101 input runtime independence falsely proven", "inputs", lambda x: x.__setitem__("runtime_no_delegation", "ESTABLISHED"))
    reject_output("V101 input speed invented", "inputs", lambda x: x.__setitem__("performance", "2x"))
    reject_output("V101 input final holdout opened", "inputs", lambda x: x.__setitem__("final_holdout_opened", True))
    reject_output("V101 input qualified candidate fabricated", "inputs", lambda x: x.__setitem__("qualified_candidate_count", 1))

    def reject_wall(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            labels.append(label)
            return
        raise Rejected("hostile V101 source-only effect accepted: " + label)

    forbidden = (
        ("wall forbids candidate source", os.path.join(ROOT, "candidates/rust_candidate.py")),
        ("wall forbids native engine", os.path.join(ROOT, "candidates/_rust_engine.so")),
        ("wall forbids candidate bridge", os.path.join(ROOT, "candidates/rust/py_bridge.c")),
        ("wall forbids V25 gzip archive", context["receipt"]["archive"]["path"]),
        ("wall forbids private build root", context["contract"]["actual_v25_native_build"]["private_root_path"]),
        ("wall forbids final hidden cases", os.path.join(ROOT, "oracle/phase3/hidden-cases.json")),
    )
    for label, path in forbidden:
        reject_wall(label, "open", (path, None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("wall forbids reading evidence without no-follow", "open",
                (os.path.join(ROOT, AUDIT[0]), None, os.O_RDONLY))
    reject_wall("wall forbids source-only output write", "open",
                (os.path.join(ROOT, OUTPUT + ".svg"), None, os.O_WRONLY | os.O_CREAT))
    reject_wall("wall forbids candidate process", "subprocess.Popen", (PYTHON,))
    reject_wall("wall forbids native profiler", "subprocess.Popen", ("/usr/bin/gprofng",))
    reject_wall("wall forbids gzip import", "import", ("gzip",))
    reject_wall("wall forbids candidate import", "import", ("candidates.rust_candidate",))
    reject_wall("wall forbids matching import", "import", ("re",))
    reject_wall("wall forbids native load", "ctypes.dlopen", ("candidate.so",))
    reject_wall("wall forbids clock sampling", "time.perf_counter", ())
    reject_wall("wall forbids network", "socket.connect", ("example.invalid",))
    reject_wall("wall forbids thread", "_thread.start_new_thread", ())
    reject_wall("wall forbids destructive rename", "os.rename", ("a", "b"))
    validate_outputs(context, result, source_sha, source_size)
    require(len(result["summary"]) < 65536 and len(result["inputs"]) < 32768,
            "V101 copied entire history instead of preserving immutable digest-bound references")
    return len(labels)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    for name in ("source", "previous-source", "previous-inputs", "previous-summary",
                 "previous-svg", "v25-source", "v25-protocol", "v25-contract",
                 "v25-receipt", "nondelegation-receipt"):
        parser.add_argument("--" + name + "-sha256", required=True)
    return parser.parse_args()


def write(relative: str, payload: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, relative),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        index = 0
        while index < len(payload):
            written = os.write(descriptor, payload[index:])
            require(written > 0, "exclusive V101 public output write was interrupted")
            index += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main() -> int:
    args = arguments()
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode,
            "the frozen isolated, no-site, no-bytecode CPython 3.14.6 is required")
    for prefix, items in (("previous", PREVIOUS), ("v25", CURRENT)):
        for key, spec in items.items():
            require(getattr(args, prefix + "_" + key + "_sha256") == spec[1],
                    "frozen V101 public owner SHA-256 changed: " + spec[0])
    require(args.nondelegation_receipt_sha256 == AUDIT[1],
            "frozen V4 independent non-delegation FAIL-1 evidence changed")
    source_sha = args.source_sha256
    require(len(source_sha) == 64 and all(item in "0123456789abcdef" for item in source_sha),
            "V101 renderer source pin must be lowercase SHA-256")
    wall = SourceWall(args.render)
    sys.addaudithook(wall.check)
    source_size = os.stat(os.path.join(ROOT, SELF), follow_symlinks=False).st_size
    source = owner((SELF, source_sha, source_size))
    before = {key: owner(spec) for key, spec in PREVIOUS.items()}
    current = {key: owner(spec) for key, spec in CURRENT.items()}
    context = {
        "goal": owner(GOAL),
        "previous_inputs": parsed(before["inputs"], "complete V100 public inputs"),
        "previous_summary": parsed(before["summary"], "complete V100 public publication"),
        "previous_svg": before["svg"],
        "protocol": current["protocol"],
        "contract": parsed(current["contract"], "complete frozen V25 public campaign contract"),
        "receipt": parsed(current["receipt"], "complete actual V25 public campaign receipt"),
        "audit": parsed(owner(AUDIT), "complete actual separate static V4 audit failure"),
    }
    verify(context)
    result = assets(context, source_sha, len(source))
    validate_outputs(context, result, source_sha, len(source))
    hostile = self_test(context, result, source_sha, len(source), wall) if args.self_test else 0
    if args.render:
        for key, suffix in (("svg", ".svg"), ("inputs", ".inputs.json"), ("summary", ".json")):
            write(OUTPUT + suffix, result[key])
    report = {
        "status": "PASS", "mode": "self-test" if args.self_test else
            "render" if args.render else "verify-frozen-context",
        "source_sha256": source_sha, "source_bytes": len(source),
        "hostile_control_count": hostile,
        "candidate_status": "FAIL", "verified_original_checks": 15877,
        "original_case_execution_denominator": DENOMINATOR,
        "verified_original_check_change_from_previous_graph": 0,
        "completed_original_suite_count": 13,
        "passing_original_suite_count": 11,
        "exact_semantic_mismatch_count": 1352,
        "exact_semantic_mismatches_by_suite": dict(LOSSES),
        "distinct_candidate_worker_count": 13,
        "worker_failure_count": 0, "infrastructure_failure_count": 0,
        "capture_clamp_bridge_changed": True, "native_engine_changed": False,
        "capture_clamp_compatibility_improvement": "NONE",
        "independent_nondelegation_audit_status": "FAIL",
        "independent_nondelegation_finding_count": 1,
        "actual_public_matching_delegation_proven": False,
        "runtime_no_delegation": "NOT ESTABLISHED; INDEPENDENT V4 STATIC AUDIT FAIL",
        "performance": UNMEASURED, "memory": UNMEASURED,
        "proposed_unopened_final_case_count": PROPOSAL,
        "candidate_source_owners_opened": 0, "native_binary_files_opened": 0,
        "native_binary_metadata_probes": 0,
        "compressed_archives_opened": 0, "compressed_archives_statted": 0,
        "compressed_archives_inflated": 0,
        "private_build_roots_opened": 0, "private_build_roots_statted": 0,
        "hidden_cases_read": 0, "candidate_workers_started": 0,
        "reference_workers_started": 0, "compiler_processes_started": 0,
        "clock_samples": 0, "workspace_mutations": 3 if args.render else 0,
        "outputs": {
            key: {"path": OUTPUT + suffix, "bytes": len(result[key]),
                  "sha256": digest(result[key])}
            for key, suffix in (("svg", ".svg"), ("inputs", ".inputs.json"),
                                ("summary", ".json"))
        },
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, Rejected) as failure:
        print("FAIL: " + str(failure), file=sys.stderr)
        raise SystemExit(2)
