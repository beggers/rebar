#!/usr/bin/env python3
"""Authenticate the completed Rust V24 campaign and render an honest V100 chart."""

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
SELF = "tools/render_candidate_current_overview_v100.py"
OUTPUT = "docs/evidence/candidate-current-overview-v100"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
DENOMINATOR = 31_237
SUPPLEMENTAL = 8_244
PREVIOUS_PROPOSAL = 14_155_776
PROPOSAL = 141_557_760
UNMEASURED = "NOT MEASURED"
NATIVE_BRIDGE = "e0c26cb83fe35eb18297e7a9cd58b63be891d847479237d2ba972e4ba1b3b3bf"
NATIVE_ENGINE = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
BUILD_CONTRACT = "cd1a77792bbb9822bfe3e05f0005bb0629c05ecd16daa68a3e11337130a54876"
BUILD_RECEIPT = "da4edc2ff3352aab2a7b0c992286534b38dce422fd258f1fe1531464a277d6e4"
V4_CONTRACT = "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2"
RUST_ARCHIVE = "5d7a0342ab1060191d227a89d51fb53c77011e3840586efb07dea9b18ad84686"

PREVIOUS = {
    "source": ("tools/render_candidate_current_overview_v99.py", "f4e1e69dcd0e6e5c068165a4893d89ccc183c03eee59c0c99a654bc47ea88196", 43014),
    "inputs": ("docs/evidence/candidate-current-overview-v99.inputs.json", "f922882c1a00ae0fb8cd4dc81f498c6f5d785274246f1014759585d86e3387bd", 7953),
    "summary": ("docs/evidence/candidate-current-overview-v99.summary.json", "bbd38c44616adb8e35c3c98d64ed15e55560f938123c8c42569b30fc7597d5af", 15816),
    "svg": ("docs/evidence/candidate-current-overview-v99.svg", "c98a398357628201bb7b6d97ec4fd1bb32e8c770b8c5ba74850d6e4e1c0f6821", 7802),
}
RUST = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v24.py", "f855f73e320f4ec33063dac1f22c11b1977ba04a02e1f97dfddca1d0670f705d", 83262),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V24.md", "d482cf8d06f9f328c08fda43a63db79db408e2421bad24e6e047ad507ef70431", 6617),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v24.json", "605737aa5060b78eb3802c8b3e58954a680bdf08b6f62a402de453552a0cd8f4", 14607),
    "receipt": (
        "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v24-"
        "rust-capture-shape-v2-root-provenance-original-p0-v24-failures-publication-receipt.json",
        "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09", 11832,
    ),
}
C_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-"
    "c-original-match-semantics-original-p0-v12-failures-publication-receipt.json",
    "a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b", 10943,
)
HOLDOUT = {
    "source": ("tools/verify_expanded_sealed_holdout_v2.py", "48d39e0a39a835c9876344591f8b4b63cfad336c3b4e1b1dd2164255763b33f7", 50749),
    "protocol": ("oracle/phase3/EXPANDED-SEALED-HOLDOUT-V2.md", "96c6edae1fe959faa59079ada499bb98173101171c8c377e900eba7bb2673c38", 19395),
    "contract": ("oracle/phase3/expanded-sealed-holdout-v2.json", "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0", 15561),
}
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864), ("scanner_v3", 1024),
    ("buffer_v3", 768), ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
RUST_MISMATCHES = {"substitution_v2": 240, "shape_v2": 1112}
C_MISMATCHES = {"managed_v1": 16, "public_types_v1": 248,
                "substitution_v2": 224, "public_surface_v19": 114, "pep688_v4": 4}


class Rejected(ValueError):
    """An owner, public claim, or source-only boundary was not authentic."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def owner_specs() -> tuple[tuple[str, str, int], ...]:
    return tuple(PREVIOUS.values()) + tuple(RUST.values()) + (C_RECEIPT,) + tuple(HOLDOUT.values())


class SourceWall:
    """Allow only exact, public, digest-pinned source owners and render outputs."""

    def __init__(self, render: bool) -> None:
        self.render = render
        self.owners = frozenset(os.path.join(ROOT, path) for path, _, _ in owner_specs()) | {
            os.path.join(ROOT, SELF), os.path.join(ROOT, "GOAL.md")
        }
        self.outputs = frozenset(os.path.join(ROOT, OUTPUT + suffix)
                                 for suffix in (".inputs.json", ".summary.json", ".svg"))

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            if type(path) is not str:
                raise Rejected("source-only wall rejected an unapproved file descriptor")
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.render and path in self.outputs and flags & required == required,
                        "source-only wall rejected a write or nonexclusive output")
            else:
                require(path in self.owners and bool(flags & os.O_NOFOLLOW),
                        "source-only wall rejected an archive, candidate, native, private, or holdout")
            return
        if (event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn"))
                or event in {"os.system", "os.fork", "os.posix_spawn", "os.mkdir", "os.remove",
                             "os.rename", "os.rmdir", "os.chdir", "os.chmod", "os.link",
                             "os.symlink", "os.truncate", "os.putenv", "time.time",
                             "time.monotonic", "time.perf_counter", "_thread.start_new_thread"}):
            raise Rejected("source-only wall rejected a process, clock, network, native, or mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (name in {"re", "_sre", "ctypes", "subprocess"}
                                                or name.startswith(("candidates.", "rebar.")))),
                    "source-only wall rejected candidate, native, or matching imports")


def owner(relative: str, expected: str, size: int) -> bytes:
    allowed = {"GOAL.md", SELF} | {spec[0] for spec in owner_specs()}
    require(relative in allowed, "owner is outside the exact frozen public allowlist")
    descriptor = os.open(os.path.join(ROOT, relative), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode), "owner is not a regular file")
        require(stat.S_IMODE(metadata.st_mode) == 0o600, "owner is not private 0600")
        require(metadata.st_nlink == 1, "owner has an unexpected hard link")
        require(metadata.st_uid == os.getuid(), "owner belongs to a different user")
        require(metadata.st_size == size, "owner size does not match its frozen pin")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    result = b"".join(chunks)
    require(len(result) == size and digest(result) == expected, "complete owner fingerprint changed")
    return result


def parsed(raw: bytes, label: str) -> dict:
    try:
        value = json.loads(raw)
    except (UnicodeError, ValueError) as failure:
        raise Rejected("invalid authenticated JSON: " + label) from failure
    require(type(value) is dict, "authenticated JSON must be an object: " + label)
    return value


def same(mapping: object, expected: dict, label: str) -> None:
    require(type(mapping) is dict, label + " is not an object")
    for key, value in expected.items():
        require(mapping.get(key) == value, f"{label}: unexpected {key}")


def reference(spec: tuple[str, str, int]) -> dict:
    return {"path": spec[0], "sha256": spec[1], "bytes": spec[2]}


def verify_previous(inputs: dict, summary: dict, svg: bytes) -> None:
    shared = {
        "version": 99, "actual_current_graph_predecessor_version": 98,
        "goal_sha256": GOAL_SHA256, "python": "3.14.6",
        "original_case_execution_denominator": DENOMINATOR, "original_suite_count": 13,
        "named_private_waiver_count": 13, "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "authenticated_evidence_owner_lower_bound": 352,
        "authenticated_history_reference_lower_bound": 357,
        "expanded_holdout_proposed_case_count": PREVIOUS_PROPOSAL,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "candidate_source_owners_opened_by_graph": 0, "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0, "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0, "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0, "hidden_cases_read_by_graph": 0,
        "clock_samples_by_graph": 0, "final_holdout_opened": False,
        "performance": UNMEASURED, "memory": UNMEASURED, "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED", "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    same(inputs, shared, "complete V99 inputs")
    same(summary, shared, "complete V99 summary")
    same(inputs, {"schema": "rebar-candidate-current-overview-v99-inputs"}, "V99 inputs")
    same(summary, {"schema": "rebar-candidate-current-overview-v99-summary", "status": "PASS",
                   "c_v12_candidate_status": "FAIL", "c_v12_candidate_qualified": False},
         "V99 summary")
    require(inputs.get("headline") == summary.get("headline"), "V99 complete headlines differ")
    require(inputs.get("snapshot") == summary.get("snapshot"), "V99 complete snapshots differ")
    require(inputs.get("previous_overview") == summary.get("previous_overview"),
            "V99 complete historical references differ")
    same(inputs.get("renderer"), reference(PREVIOUS["source"]), "complete V99 renderer")
    history = inputs.get("previous_overview")
    require(type(history) is dict and set(history) == {"source", "inputs", "summary", "svg"},
            "V99 did not preserve every complete V98 owner")
    for record in history.values():
        require(type(record) is dict and set(record) == {"path", "sha256", "bytes"},
                "V99 omitted a complete historical owner fingerprint")
    same(inputs.get("headline"), {
        "original_python_check_count": DENOMINATOR,
        "c_current_verified_original_checks": 16_413,
        "rust_current_verified_original_checks": 14_725,
        "zig_current_verified_original_checks": 4_607,
        "speed_relative_to_python": UNMEASURED, "performance": UNMEASURED,
        "fully_compatible_candidate_count": 0,
        "proposed_final_comparison_case_count": PREVIOUS_PROPOSAL,
        "winner_selected": False,
    }, "V99 historical headline")
    same(inputs["headline"].get("verified_original_checks_by_candidate"), {
        "c": 16_413, "rust": 14_725, "zig": 4_607,
        "cpp": UNMEASURED, "go": UNMEASURED, "fortran": UNMEASURED,
    }, "V99 historical six-family counts")
    same(inputs.get("snapshot"), {
        "version": 99, "original_case_execution_denominator": DENOMINATOR,
        "c_v12_original_campaign_verified_passing_case_count": 16_413,
        "c_v12_original_campaign_completed_suite_count": 12,
        "c_v12_original_campaign_candidate_execution_failure_count": 1,
        "c_v12_original_campaign_complete_observed_individual_mismatch_record_count": 606,
        "rust_v22_original_campaign_verified_passing_case_count": 14_725,
        "zig_v12_original_campaign_verified_passing_case_count": 4_607,
    }, "V99 historical snapshot")
    same(inputs.get("c_v12_public_evidence", {}).get("receipt"), reference(C_RECEIPT),
         "V99 historical C receipt")
    require(svg.startswith(b"<svg ") and b"16,413 / 31,237" in svg
            and b"NOT MEASURED" in svg and b'role="img"' in svg,
            "V99 complete accessible correctness graphic was replaced")


def verify_c_receipt(receipt: dict, previous_summary: dict) -> None:
    same(receipt, {
        "schema": "rebar-owned-repaired-c-original-campaign-v12-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "case_execution_denominator": DENOMINATOR, "suite_count": 13,
        "attempted_suite_count": 13, "completed_suite_count": 12,
        "verified_passing_case_count": 16_413, "actual_candidate_workers": 13,
        "actual_worker_process_ids_are_distinct": True,
        "candidate_execution_failure_count": 1, "infrastructure_failure_count": 0,
        "worker_timeout_count": 0, "complete_observed_semantic_mismatch_record_count": 606,
        "complete_mismatch_chunk_count": 21,
        "all_observed_semantic_mismatch_records_preserved": True,
        "complete_original_source_method_count": 165,
        "complete_original_public_record_count": 152,
        "complete_original_executed_case_count": 151,
        "separate_reference_case_count": SUPPLEMENTAL,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "semantic_mismatch_count": UNMEASURED, "performance": UNMEASURED,
        "memory": UNMEASURED, "timing_trials_run": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "holdout": "NOT OPENED", "winner_selected": False,
        "expanded_holdout_proposed_case_count": PREVIOUS_PROPOSAL,
    }, "historical actual C12 publication")
    require(previous_summary.get("c_v12_suite_outcomes") == receipt.get("suite_outcomes"),
            "complete C12 suite outcomes were not preserved by the previous graph")
    require(previous_summary.get("c_v12_complete_mismatch_suite_vector_fingerprints")
            == receipt.get("complete_mismatch_suite_vector_fingerprints"),
            "complete C12 mismatch fingerprints were not preserved")
    outcomes = receipt.get("suite_outcomes")
    require(type(outcomes) is list and len(outcomes) == 13, "C12 omitted an original suite")
    for row, (suite, denominator) in zip(outcomes, SUITES, strict=True):
        same(row, {"suite": suite, "case_execution_denominator": denominator,
                   "actual_candidate_workers": 1}, "historical C12 suite")
        if suite == "subinterpreter_v2":
            same(row, {"status": "FAIL", "failure_class": "CANDIDATE EXECUTION FAILURE",
                       "mismatch_count": UNMEASURED}, "historical C12 execution failure")
        elif suite in C_MISMATCHES:
            same(row, {"status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
                       "mismatch_count": C_MISMATCHES[suite]}, "historical C12 mismatch")
        else:
            same(row, {"status": "PASS", "failure_class": "PASS", "mismatch_count": 0},
                 "historical C12 passing suite")
    same(receipt.get("archive"), {
        "sha256": "f6f68b5c7222f47734515e8570a048e2f449623f6fcbc99493abff4babb0c1a1",
        "bytes": 211493, "exclusive_creation": True,
        "file_fsync_completed": True, "directory_fsync_completed": True,
    }, "historical unopened C12 archive metadata")


def verify_rust_contract(contract: dict) -> None:
    same(contract, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v24-recoverable-source-freeze",
        "version": 24, "family": "rust", "goal_sha256": GOAL_SHA256,
        "status": "SOURCE FROZEN; V24 BUILD PASS; ORIGINAL CAMPAIGN NOT RUN",
    }, "frozen Rust V24 source contract")
    for key in ("source", "protocol"):
        same(contract.get(key), reference(RUST[key]), "frozen Rust V24 " + key)
    boundary = contract.get("original_correctness_boundary")
    same(boundary, {
        "case_execution_denominator": DENOMINATOR, "suite_count": 13,
        "corrected_reference_case_count": 6912,
        "corrected_reference_counted_in_original_denominator": False,
        "supplemental_reference_case_count": SUPPLEMENTAL,
        "supplemental_counted_in_original_denominator": False,
        "named_private_waiver_count": 13, "candidate_correctness": UNMEASURED,
        "candidate_qualified": False, "candidate_semantic_mismatch_count": UNMEASURED,
        "candidate_verified_passing_case_count": UNMEASURED,
    }, "frozen pre-run Rust V24 correctness boundary")
    require(type(boundary.get("named_private_waivers")) is list
            and len(boundary["named_private_waivers"]) == 13,
            "Rust V24 did not retain all named private waivers")
    suites = boundary.get("suites")
    require(type(suites) is list and len(suites) == 13, "Rust V24 suite boundary changed")
    for row, (suite, denominator) in zip(suites, SUITES, strict=True):
        same(row, {"id": suite, "case_execution_denominator": denominator,
                   "candidate_status": "NOT RUN", "candidate_workers_started": 0,
                   "semantic_mismatch_count": UNMEASURED}, "frozen Rust V24 source-only suite")
        require(type(row.get("immutable_v22_original_row_sha256")) is str
                and len(row["immutable_v22_original_row_sha256"]) == 64,
                "frozen Rust V24 original row identity disappeared")
    effects = contract.get("source_only_effects")
    same(effects, {
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
        "runtime_non_delegation": "NOT ESTABLISHED", "qualified_candidate_count": 0,
        "holdout": "NOT OPENED", "winner_selected": False,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "expanded_holdout_proposal_case_count": PREVIOUS_PROPOSAL,
    }, "historical frozen Rust V24 source-only guarantees")
    guard = contract.get("operational_runtime_guard_v4")
    same(guard, {"version": 4, "complete_contract_sha256": V4_CONTRACT,
                 "guard_installed_before_candidate_import": True,
                 "cross_candidate_engine": "FORBIDDEN", "external_regex_package": "FORBIDDEN",
                 "matching_fallback": "FORBIDDEN", "stdlib_re_engine": "FORBIDDEN",
                 "stdlib_sre_engine": "FORBIDDEN",
                 "runtime_non_delegation": "NOT ESTABLISHED"}, "Rust V24 operational V4 guard")
    native = contract.get("actual_v24_native_build")
    same(native, {
        "build_status": "PASS", "complete_contract_sha256": BUILD_CONTRACT,
        "native_bridge_sha256": NATIVE_BRIDGE, "native_engine_sha256": NATIVE_ENGINE,
        "actual_compiler_process_count": 28, "independent_native_artifact_count": 4,
        "independent_private_phase_count": 2, "archive_opened": False,
        "cross_candidate_engine": "FORBIDDEN",
        "external_regular_expression_engine": "FORBIDDEN",
        "external_cargo_dependency_count": 0, "matching_fallback": "FORBIDDEN",
    }, "first-party Rust V24 native build provenance")
    same(native.get("publication_receipt"), {"sha256": BUILD_RECEIPT},
         "first-party Rust V24 native build publication")
    previous = contract.get("immutable_actual_v22_failure")
    same(previous, {"candidate_status": "FAIL", "completed_suite_count": 12,
                    "actual_candidate_workers": 13, "verified_passing_case_count": 14_725,
                    "fully_observed_mismatch_lower_bound": 2018},
         "historical actual Rust V22 failure")
    same(previous.get("fully_observed_suite_mismatch_counts"),
         {"managed_v1": 42, "shape_v2": 1624, "substitution_v2": 352},
         "historical actual Rust V22 mismatches")


def verify_rust_receipt(receipt: dict, contract: dict) -> None:
    same(receipt, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v24-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY", "family": "rust",
        "label": "phase2-v24-rust-capture-shape-v2-root-provenance-original-p0-v24",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "case_execution_denominator": DENOMINATOR, "suite_count": 13,
        "attempted_suite_count": 13, "started_suite_count": 13,
        "completed_suite_count": 13, "verified_passing_case_count": 15_877,
        "semantic_mismatch_count": 1352, "actual_candidate_workers": 13,
        "distinct_worker_process_id_count": 13, "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0, "worker_failure_capture_count": 0,
        "all_worker_failure_capture_count": 0, "worker_failure_capture_complete": True,
        "infrastructure_failure_count": 0, "all_original_observation_vectors_complete": True,
        "all_original_suite_rows_validated_before_publication": True,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "campaign_source_sha256": RUST["source"][1],
        "campaign_protocol_sha256": RUST["protocol"][1],
        "campaign_contract_sha256": RUST["contract"][1],
        "actual_v24_build_contract_sha256": BUILD_CONTRACT,
        "actual_v24_build_receipt_sha256": BUILD_RECEIPT,
        "native_bridge_sha256": NATIVE_BRIDGE, "native_engine_sha256": NATIVE_ENGINE,
        "actual_v24_build_archive_read_count": 0,
        "actual_v24_build_archive_gzip_inflation_count": 0,
        "actual_v24_compiler_process_count": 28,
        "corrected_reference_case_count": 6912,
        "candidate_run_uses_both_complete_reference_vectors": True,
        "named_private_waiver_count": 13,
        "preserved_previous_rust_verified_passing_case_count": 14_853,
        "preserved_previous_rust_semantic_mismatch_count": 1440,
        "clock_samples": 0, "timing_trials_run": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": UNMEASURED, "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED, "holdout": "NOT OPENED",
        "winner_selected": False,
    }, "actual complete Rust V24 public publication")
    workers = receipt.get("actual_worker_process_ids")
    require(type(workers) is list and len(workers) == 13 and len(set(workers)) == 13,
            "actual Rust V24 did not use 13 distinct candidate workers")
    require(receipt.get("all_worker_failure_captures") == [],
            "actual Rust V24 worker failures were hidden")
    same(receipt.get("worker_failure_capture"), {
        "actual_failure_count": 0, "all_failure_metadata_preserved": True,
        "first_worker_failure": None, "suite_failure_summaries": [],
    }, "actual complete zero-worker-failure capture")
    suites = receipt.get("suite_integrity")
    require(type(suites) is list and len(suites) == 13,
            "actual Rust V24 omitted an original observed suite")
    passing = mismatches = passing_suites = 0
    observed_workers = []
    for row, (suite, denominator) in zip(suites, SUITES, strict=True):
        count = RUST_MISMATCHES.get(suite, 0)
        expected_passes = 0 if count else denominator
        same(row, {
            "suite": suite, "case_execution_denominator": denominator,
            "verified_passing_case_count": expected_passes, "mismatch_count": count,
            "failure_class": "SEMANTIC MISMATCH" if count else "PASS",
            "returncode": 1 if count else 0, "fully_observed": True,
            "worker_attempted": True, "actual_worker_started": True,
        }, "actual complete Rust V24 original suite")
        require(type(row.get("complete_original_row_sha256")) is str
                and len(row["complete_original_row_sha256"]) == 64,
                "actual Rust V24 complete suite fingerprint disappeared")
        require(row.get("pid") in workers, "actual Rust V24 suite used an unknown worker")
        observed_workers.append(row["pid"])
        passing += expected_passes
        mismatches += count
        passing_suites += not bool(count)
    require(len(set(observed_workers)) == 13, "actual Rust V24 reused a suite worker")
    require(passing == 15_877 and mismatches == 1352 and passing_suites == 11,
            "actual complete Rust V24 score, losses, or passing groups changed")
    same(suites[4], {"suite": "managed_v1", "verified_passing_case_count": 1024,
                     "mismatch_count": 0, "failure_class": "PASS"},
         "actual fully recovered managed Rust group")
    same(suites[10], {"suite": "subinterpreter_v2", "verified_passing_case_count": 128,
                      "mismatch_count": 0, "failure_class": "PASS"},
         "actual fully recovered real subinterpreter Rust group")
    same(receipt.get("archive"), {
        "sha256": RUST_ARCHIVE, "size_bytes": 3771994, "mode": 0o600,
        "exclusive_creation": True, "file_fsync_completed": True,
        "directory_fsync_completed": True, "same_inode_readback_verified": True,
        "streaming_readback_verified": True,
        "relative": "repaired-rust-original-campaign-v16-rust-phase2-v24-"
                    "rust-capture-shape-v2-root-provenance-original-p0-v24-failures.json.gz",
    }, "actual Rust V24 unopened compressed archive metadata")
    require(type(receipt.get("restored_original_targets")) is dict
            and set(receipt["restored_original_targets"])
            == {"adapter", "bridge", "engine", "bridge_source"},
            "actual Rust V24 original source or native targets were not restored")
    same(contract.get("actual_v24_native_build"), {
        "native_bridge_sha256": receipt["native_bridge_sha256"],
        "native_engine_sha256": receipt["native_engine_sha256"],
        "complete_contract_sha256": receipt["actual_v24_build_contract_sha256"],
    }, "cross-authenticated first-party Rust V24 native ownership")


def verify_proposal(contract: dict, protocol: bytes) -> None:
    same(contract, {
        "schema": "rebar-expanded-sealed-holdout-pre-phase3-proposal-v2",
        "proposal_status": "PRE-PHASE-3 PROPOSAL", "final_protocol_status": "NOT FROZEN",
        "generator_status": "NOT FROZEN", "secret_status": "NOT GENERATED",
        "case_status": "NOT GENERATED; NOT OPENED",
        "timing_status": "NOT RUN; NOT MEASURED",
        "memory_status": "NOT RUN; NOT MEASURED",
        "phase3_gate_status": "BLOCKED UNTIL THREE DISTINCT COMPLETE-P0 NO-DELEGATION PASSES",
        "runtime_independence_status": "NOT ESTABLISHED", "winner_status": "NOT SELECTED",
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "preserved_original_proposal_case_count": 4_194_304,
        "preserved_immediate_previous_proposal_case_count": PREVIOUS_PROPOSAL,
        "case_count": PROPOSAL, "timed_case_count": PROPOSAL,
        "operation_count": 96, "pattern_family_count": 48,
        "subject_representation_count": 10, "lifecycle_count": 8,
        "subject_scale_count": 6, "match_density_count": 4,
        "corpus_family_count": 16, "stratum_count": 8_847_360,
        "cases_per_stratum": 16, "original_p0_case_count": DENOMINATOR,
        "original_p0_suite_count": 13, "separate_differential_case_count": SUPPLEMENTAL,
        "named_private_waiver_count": 13,
        "pinned_python_path": PYTHON, "pinned_python_version": "3.14.6",
    }, "unfrozen, unopened V2 final-comparison proposal")
    product = (contract["operation_count"] * contract["pattern_family_count"]
               * contract["subject_representation_count"] * contract["lifecycle_count"]
               * contract["subject_scale_count"] * contract["match_density_count"]
               * contract["corpus_family_count"])
    require(product == PROPOSAL and contract["stratum_count"] * contract["cases_per_stratum"] == PROPOSAL,
            "unopened V2 comparison proposal denominator was inflated")
    axes = (("operations", 96), ("primary_pattern_families", 48),
            ("subject_representations", 10), ("lifecycle_slots", 8),
            ("subject_scales", 6), ("match_densities", 4), ("corpus_families", 16))
    for key, expected in axes:
        values = contract.get(key)
        require(type(values) is list and len(values) == expected
                and len({json.dumps(value, sort_keys=True) for value in values}) == expected,
                "unopened V2 comparison proposal has a duplicated or missing axis: " + key)
    owners = contract.get("required_public_source_pins")
    require(type(owners) is list and len(owners) == 12, "unopened V2 proposal lost public history")
    require(owners[0] == {"path": "GOAL.md", "sha256": GOAL_SHA256},
            "unopened V2 proposal lost the immutable experiment goal")
    require(owners[-1] == {
        "path": "oracle/phase3/expanded-sealed-holdout-v1.json",
        "sha256": "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
    }, "unopened V2 proposal lost its complete immutable V1 proposal")
    for token in (b"141,557,760", b"14,155,776", b"4,194,304", b"NOT FROZEN",
                  b"NOT GENERATED", b"NOT OPENED", b"NOT MEASURED", b"31,237", b"8,244"):
        require(token in protocol, "public unopened V2 proposal omitted " + token.decode())


def verify_context(context: dict) -> None:
    require(context["goal"].startswith(b"/goal ")
            and digest(context["goal"]) == GOAL_SHA256,
            "immutable GOAL.md no longer matches this experiment")
    verify_previous(context["previous_inputs"], context["previous_summary"], context["previous_svg"])
    verify_c_receipt(context["c_receipt"], context["previous_summary"])
    verify_rust_contract(context["rust_contract"])
    verify_rust_receipt(context["rust_receipt"], context["rust_contract"])
    verify_proposal(context["proposal_contract"], context["proposal_protocol"])
    require(context["previous_inputs"]["headline"]["rust_current_verified_original_checks"] + 1152
            == context["rust_receipt"]["verified_passing_case_count"],
            "actual Rust V24 improvement from the complete V99 graph was fabricated")


def escaped(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def render_svg() -> bytes:
    rows = (
        ("Python re", DENOMINATOR, "All 13 groups pass", "BASELINE", "#34d399"),
        ("C", 16_413, "12 groups complete; 1 execution failure", "NOT COMPATIBLE", "#fbbf24"),
        ("Rust", 15_877, "13 groups complete; 11 pass; 2 differ", "NOT COMPATIBLE", "#60a5fa"),
        ("Zig", 4_607, "Previously verified original checks", "NOT COMPATIBLE", "#fbbf24"),
        ("C++", None, "Complete original correctness not measured", UNMEASURED, "#94a3b8"),
        ("Go", None, "Complete original correctness not measured", UNMEASURED, "#94a3b8"),
        ("Fortran", None, "Complete original correctness not measured", UNMEASURED, "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1130" '
        'viewBox="0 0 1480 1130" role="img" aria-labelledby="title description">',
        '<title id="title">Python regular-expression correctness: Rust improves; speed not measured</title>',
        '<desc id="description">The fixed original correctness denominator is 31,237 checks. '
        'Python passes 31,237, C verifies 16,413, Rust verifies 15,877, and Zig verifies 4,607. '
        'Rust improves by 1,152 checks over the preceding graph and completes all thirteen groups '
        'with thirteen distinct workers and no worker failures. Eleven Rust groups pass. '
        'Exactly 1,352 semantic mismatches remain: 240 substitution and 1,112 shape. '
        'Managed cases and genuine subinterpreter cases both pass. Three other families are not '
        'measured. Bars show correctness, never speed. A 141,557,760-case future comparison is '
        'only a proposal: not frozen, generated, or opened. No candidate qualifies; no winner.</desc>',
        '<rect width="1480" height="1130" rx="24" fill="#0b1220"/>',
        '<text x="58" y="72" fill="#f8fafc" font-size="35" font-family="system-ui,sans-serif" '
        'font-weight="750">Can we build a faster, fully compatible Python re?</text>',
        '<text x="60" y="108" fill="#cbd5e1" font-size="19" font-family="system-ui,sans-serif">'
        'Correctness first. Speed has not been measured.</text>',
        '<rect x="56" y="133" width="1368" height="102" rx="16" fill="#12243a" stroke="#29445f"/>',
        '<text x="78" y="169" fill="#93c5fd" font-size="18" font-family="system-ui,sans-serif" '
        'font-weight="730">NEW: Rust completed all 13 original test groups</text>',
        '<text x="79" y="203" fill="#e2e8f0" font-size="17" font-family="system-ui,sans-serif">'
        '15,877 / 31,237 verified  ·  +1,152 since the previous graph  ·  1,352 mismatches remain</text>',
        '<text x="64" y="273" fill="#94a3b8" font-size="13" font-family="system-ui,sans-serif" '
        'font-weight="650">APPROACH</text>',
        '<text x="182" y="273" fill="#94a3b8" font-size="13" font-family="system-ui,sans-serif" '
        'font-weight="650">VERIFIED ORIGINAL CORRECTNESS CHECKS</text>',
        '<text x="762" y="273" fill="#94a3b8" font-size="13" font-family="system-ui,sans-serif" '
        'font-weight="650">WHAT THE RESULT MEANS</text>',
        '<text x="1290" y="273" fill="#94a3b8" font-size="13" font-family="system-ui,sans-serif" '
        'font-weight="650">SPEED</text>',
    ]
    for index, (label, count, detail, status, color) in enumerate(rows):
        top = 297 + index * 78
        baseline = top + 31
        row_fill = "#102136" if label == "Rust" else "#0f1929"
        parts.append(f'<rect x="57" y="{top}" width="1365" height="66" rx="12" fill="{row_fill}"/>')
        parts.append(f'<text x="76" y="{baseline}" fill="#f8fafc" font-size="18" '
                     f'font-family="system-ui,sans-serif" font-weight="670">{escaped(label)}</text>')
        parts.append(f'<rect x="182" y="{top + 13}" width="338" height="19" rx="7" fill="#243247"/>')
        if count is None:
            value = UNMEASURED
        else:
            width = round(338 * count / DENOMINATOR)
            parts.append(f'<rect x="182" y="{top + 13}" width="{width}" height="19" '
                         f'rx="7" fill="{color}"/>')
            percent = "100%" if count == DENOMINATOR else f"{100 * count / DENOMINATOR:.1f}%"
            value = f"{count:,} / {DENOMINATOR:,}  ·  {percent}"
        parts.append(f'<text x="532" y="{baseline}" fill="#e2e8f0" font-size="15" '
                     f'font-family="system-ui,sans-serif">{escaped(value)}</text>')
        parts.append(f'<text x="762" y="{baseline}" fill="#e2e8f0" font-size="14" '
                     f'font-family="system-ui,sans-serif">{escaped(detail)}</text>')
        parts.append(f'<text x="762" y="{top + 54}" fill="{color}" font-size="12" '
                     f'font-family="system-ui,sans-serif" font-weight="650">{escaped(status)}</text>')
        parts.append(f'<text x="1287" y="{baseline}" fill="#cbd5e1" font-size="13" '
                     f'font-family="system-ui,sans-serif">{UNMEASURED}</text>')
    parts.extend([
        '<rect x="58" y="870" width="669" height="173" rx="15" fill="#112036" stroke="#26384e"/>',
        '<text x="81" y="904" fill="#93c5fd" font-size="18" font-family="system-ui,sans-serif" '
        'font-weight="720">What improved in Rust?</text>',
        '<text x="82" y="938" fill="#e2e8f0" font-size="15" font-family="system-ui,sans-serif">'
        'All 13 groups completed; 11 passed; 13 workers were distinct.</text>',
        '<text x="82" y="968" fill="#e2e8f0" font-size="15" font-family="system-ui,sans-serif">'
        'Managed checks: 1,024 pass. Real subinterpreter checks: 128 pass.</text>',
        '<text x="82" y="998" fill="#fda4af" font-size="15" font-family="system-ui,sans-serif">'
        'Remaining exact losses: substitution 240 + shape 1,112 = 1,352.</text>',
        '<text x="82" y="1026" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        'Worker failures: 0. Infrastructure failures: 0. Candidate: FAIL.</text>',
        '<rect x="745" y="870" width="677" height="173" rx="15" fill="#112036" stroke="#26384e"/>',
        '<text x="768" y="904" fill="#fcd34d" font-size="18" font-family="system-ui,sans-serif" '
        'font-weight="720">What has NOT happened?</text>',
        '<text x="769" y="938" fill="#e2e8f0" font-size="15" font-family="system-ui,sans-serif">'
        'Speed, memory, runtime independence, and a winner are not established.</text>',
        '<text x="769" y="968" fill="#e2e8f0" font-size="15" font-family="system-ui,sans-serif">'
        '141,557,760 future comparison cases are only an unopened proposal.</text>',
        '<text x="769" y="998" fill="#fcd34d" font-size="15" font-family="system-ui,sans-serif">'
        'Final protocol: NOT FROZEN. Cases: NOT GENERATED; NOT OPENED.</text>',
        '<text x="769" y="1026" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        'The original denominator stays 31,237; 8,244 other checks stay separate.</text>',
        '<text x="63" y="1085" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        'Six independent candidate families are shown. None is fully qualified. '
        'Every bar measures correctness, never speed.</text>',
        '</svg>',
    ])
    return ("\n".join(parts) + "\n").encode("utf-8")


def build_assets(context: dict, source_sha256: str, source_size: int) -> dict[str, bytes]:
    previous = {key: reference(spec) for key, spec in PREVIOUS.items()}
    rust = {key: reference(spec) for key, spec in RUST.items()}
    proposal = {key: reference(spec) for key, spec in HOLDOUT.items()}
    receipt = context["rust_receipt"]
    headline = {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "python_version": "3.14.6", "bars_measure": "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED",
        "original_python_check_count": DENOMINATOR, "original_python_suite_count": 13,
        "separate_additional_differential_check_count": SUPPLEMENTAL,
        "separate_additional_checks_in_original_denominator": False,
        "verified_original_checks_by_candidate": {
            "c": 16_413, "rust": 15_877, "zig": 4_607,
            "cpp": UNMEASURED, "go": UNMEASURED, "fortran": UNMEASURED,
        },
        "c_current_verified_original_checks": 16_413,
        "rust_current_verified_original_checks": 15_877,
        "rust_previous_graph_verified_original_checks": 14_725,
        "rust_verified_check_change_from_previous_graph": 1152,
        "rust_previous_actual_campaign_verified_original_checks": 14_853,
        "rust_verified_check_change_from_previous_actual_campaign": 1024,
        "rust_current_original_group_count": 13,
        "rust_current_completed_original_group_count": 13,
        "rust_current_passing_original_group_count": 11,
        "rust_current_semantic_mismatch_group_count": 2,
        "rust_current_exact_semantic_mismatch_count": 1352,
        "rust_current_semantic_mismatches_by_group": dict(RUST_MISMATCHES),
        "rust_current_managed_verified_original_checks": 1024,
        "rust_current_subinterpreter_verified_original_checks": 128,
        "rust_current_distinct_candidate_worker_count": 13,
        "rust_current_worker_failure_count": 0,
        "rust_current_infrastructure_failure_count": 0,
        "rust_current_candidate_status": "FAIL",
        "rust_current_candidate_qualified": False,
        "c_current_candidate_status": "FAIL",
        "c_current_completed_original_group_count": 12,
        "c_current_candidate_execution_failure_count": 1,
        "c_current_observed_individual_mismatch_records": 606,
        "c_current_observed_individual_mismatch_chunks": 21,
        "c_complete_mismatch_total": UNMEASURED,
        "zig_current_verified_original_checks": 4_607,
        "independent_first_party_candidate_family_count": 6,
        "fully_compatible_candidate_count": 0,
        "performance": UNMEASURED, "speed_relative_to_python": UNMEASURED,
        "memory": UNMEASURED, "proposed_final_comparison_case_count": PROPOSAL,
        "proposed_final_comparison_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "winner_selected": False,
        "public_reporting_integrity": "EXACTLY 1,352 ACTUAL RUST V24 LOSSES; HISTORICAL C12 EVIDENCE PRESERVED",
    }
    snapshot = {
        "schema": "rebar-candidate-current-overview-v100-compact-current-snapshot", "version": 100,
        "actual_current_graph_predecessor_version": 99,
        "goal_sha256": GOAL_SHA256, "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": 13, "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": 13,
        "c_v12_original_campaign_candidate_status": "FAIL",
        "c_v12_original_campaign_candidate_qualified": False,
        "c_v12_original_campaign_verified_passing_case_count": 16_413,
        "c_v12_original_campaign_completed_suite_count": 12,
        "c_v12_original_campaign_distinct_worker_count": 13,
        "c_v12_original_campaign_candidate_execution_failure_count": 1,
        "c_v12_original_campaign_complete_observed_individual_mismatch_record_count": 606,
        "c_v12_original_campaign_complete_observed_mismatch_chunk_count": 21,
        "c_v12_all_observed_individual_mismatch_records_preserved": True,
        "rust_v22_original_campaign_verified_passing_case_count": 14_725,
        "rust_v23_original_campaign_verified_passing_case_count": 14_853,
        "rust_v23_original_campaign_exact_semantic_mismatch_count": 1440,
        "rust_v24_original_campaign_candidate_status": "FAIL",
        "rust_v24_original_campaign_candidate_qualified": False,
        "rust_v24_original_campaign_verified_passing_case_count": 15_877,
        "rust_v24_verified_passing_case_increase_from_v99": 1152,
        "rust_v24_verified_passing_case_increase_from_v23": 1024,
        "rust_v24_original_campaign_attempted_suite_count": 13,
        "rust_v24_original_campaign_completed_suite_count": 13,
        "rust_v24_original_campaign_passing_suite_count": 11,
        "rust_v24_original_campaign_semantic_mismatch_suite_count": 2,
        "rust_v24_original_campaign_semantic_mismatch_count": 1352,
        "rust_v24_original_campaign_semantic_mismatches_by_suite": dict(RUST_MISMATCHES),
        "rust_v24_original_campaign_managed_verified_passing_case_count": 1024,
        "rust_v24_original_campaign_subinterpreter_verified_passing_case_count": 128,
        "rust_v24_original_campaign_distinct_worker_count": 13,
        "rust_v24_original_campaign_worker_failure_count": 0,
        "rust_v24_original_campaign_infrastructure_failure_count": 0,
        "rust_v24_original_targets_restored": True,
        "rust_v24_native_bridge_sha256": NATIVE_BRIDGE,
        "rust_v24_native_engine_sha256": NATIVE_ENGINE,
        "rust_v24_runtime_guard_version": 4,
        "zig_v12_original_campaign_verified_passing_case_count": 4_607,
        "expanded_holdout_proposed_case_count": PROPOSAL,
        "expanded_holdout_previous_proposed_case_count": PREVIOUS_PROPOSAL,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "authenticated_evidence_owner_lower_bound": 359,
        "authenticated_history_reference_lower_bound": 364,
        "v100_new_directly_authenticated_evidence_owner_count": 7,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED", "timing_trials_run": 0,
        "qualified_candidate_count": 0, "winner_selected": False,
    }
    inputs = {
        "schema": "rebar-candidate-current-overview-v100-inputs", "version": 100,
        "actual_current_graph_predecessor_version": 99, "goal_sha256": GOAL_SHA256,
        "python": "3.14.6", "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": 13, "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": 13, "previous_overview": previous,
        "preserved_complete_history": "EXACT DIGEST-BOUND V99 SOURCE, INPUTS, SUMMARY, AND SVG; NEVER COPIED OR TRUNCATED",
        "rust_v24_public_evidence": rust,
        "historical_c_v12_publication_receipt": reference(C_RECEIPT),
        "expanded_holdout_v2_public_proposal": proposal,
        "renderer": {"path": SELF, "sha256": source_sha256, "bytes": source_size},
        "headline": headline, "snapshot": snapshot,
        "complete_original_suites": [
            {"suite": suite, "case_execution_denominator": denominator}
            for suite, denominator in SUITES
        ],
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0, "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "private_build_roots_statted_by_graph": 0,
        "native_binary_files_opened_by_graph": 0,
        "native_binary_metadata_probes_by_graph": 0,
        "hidden_cases_read_by_graph": 0, "clock_samples_by_graph": 0,
        "final_holdout_opened": False,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_proposed_case_count": PROPOSAL,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED", "timing_trials_run": 0,
        "qualified_candidate_count": 0, "winner_selected": False,
        "authenticated_evidence_owner_lower_bound": 359,
        "authenticated_history_reference_lower_bound": 364,
        "v100_new_directly_authenticated_evidence_owner_count": 7,
    }
    summary = dict(inputs)
    summary.update({
        "schema": "rebar-candidate-current-overview-v100-summary", "status": "PASS",
        "status_scope": "AUTHENTICATED CORRECTNESS GRAPH ONLY; RUST V24 CANDIDATE FAILED; SPEED NOT MEASURED",
        "rust_v24_publication_status": receipt["publication_status"],
        "rust_v24_publication_pass_means": receipt["publication_pass_means"],
        "rust_v24_candidate_status": receipt["candidate_status"],
        "rust_v24_candidate_qualified": receipt["candidate_qualified"],
        "rust_v24_suite_outcomes": receipt["suite_integrity"],
        "rust_v24_all_observed_original_suite_vectors_complete":
            receipt["all_original_observation_vectors_complete"],
        "rust_v24_all_worker_failure_captures": receipt["all_worker_failure_captures"],
        "rust_v24_worker_failure_capture": receipt["worker_failure_capture"],
        "rust_v24_restored_original_targets": receipt["restored_original_targets"],
        "rust_v24_unopened_archive_metadata": {
            "path": receipt["archive"]["path"], "sha256": receipt["archive"]["sha256"],
            "bytes": receipt["archive"]["size_bytes"], "opened_by_graph": False,
            "statted_by_graph": False,
        },
        "c_v12_candidate_status": context["c_receipt"]["candidate_status"],
        "c_v12_candidate_qualified": context["c_receipt"]["candidate_qualified"],
        "c_v12_suite_outcomes": context["c_receipt"]["suite_outcomes"],
        "c_v12_complete_mismatch_suite_vector_fingerprints":
            context["c_receipt"]["complete_mismatch_suite_vector_fingerprints"],
        "previous_complete_overview_sha256": PREVIOUS["summary"][1],
        "previous_complete_overview_bytes": PREVIOUS["summary"][2],
        "previous_expanded_holdout_proposal_case_count": PREVIOUS_PROPOSAL,
        "expanded_holdout_v2_gate_status": context["proposal_contract"]["phase3_gate_status"],
        "expanded_holdout_v2_timing_status": context["proposal_contract"]["timing_status"],
    })
    def encode(value: dict) -> bytes:
        return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return {"inputs": encode(inputs), "summary": encode(summary), "svg": render_svg()}


def mutation_controls(context: dict, source_sha256: str, source_size: int, wall: SourceWall) -> int:
    labels = []

    def reject(label: str, mutation) -> None:
        hostile = copy.deepcopy(context)
        mutation(hostile)
        try:
            verify_context(hostile)
        except (Rejected, KeyError, TypeError, ValueError):
            labels.append(label)
            return
        raise Rejected("hostile control accepted: " + label)

    reject("immutable goal edited", lambda x: x.__setitem__("goal", x["goal"] + b"!"))
    reject("V99 source pin replaced", lambda x: x["previous_inputs"]["renderer"].__setitem__("sha256", "0" * 64))
    reject("V99 summary headline split", lambda x: x["previous_summary"]["headline"].__setitem__("rust_current_verified_original_checks", 15_877))
    reject("V99 complete history truncated", lambda x: x["previous_inputs"]["previous_overview"].pop("svg"))
    reject("V99 historical C receipt replaced", lambda x: x["previous_inputs"]["c_v12_public_evidence"]["receipt"].__setitem__("sha256", "0" * 64))
    reject("V99 denominator silently inflated", lambda x: x["previous_summary"].__setitem__("original_case_execution_denominator", DENOMINATOR + SUPPLEMENTAL))
    reject("V99 speed invented", lambda x: x["previous_inputs"]["headline"].__setitem__("speed_relative_to_python", "1.5x"))
    reject("V99 accessible SVG replaced", lambda x: x.__setitem__("previous_svg", b"<svg>fabricated</svg>"))

    contract_changes = {
        "frozen Rust source falsely says campaign passed": ("status", "CAMPAIGN PASS"),
        "frozen Rust source goal changed": ("goal_sha256", "0" * 64),
    }
    for label, (key, value) in contract_changes.items():
        reject(label, lambda x, k=key, v=value: x["rust_contract"].__setitem__(k, v))
    reject("Rust campaign source pin replaced", lambda x: x["rust_contract"]["source"].__setitem__("sha256", "0" * 64))
    reject("Rust original denominator inflated", lambda x: x["rust_contract"]["original_correctness_boundary"].__setitem__("case_execution_denominator", DENOMINATOR + 6912))
    reject("Rust corrected references merged", lambda x: x["rust_contract"]["original_correctness_boundary"].__setitem__("corrected_reference_counted_in_original_denominator", True))
    reject("Rust named waiver removed", lambda x: x["rust_contract"]["original_correctness_boundary"]["named_private_waivers"].pop())
    reject("Rust original suite reordered", lambda x: x["rust_contract"]["original_correctness_boundary"]["suites"].reverse())
    reject("Rust source mode candidate started", lambda x: x["rust_contract"]["source_only_effects"].__setitem__("candidate_workers_started", 1))
    reject("Rust source mode clock sampled", lambda x: x["rust_contract"]["source_only_effects"].__setitem__("clock_samples", 1))
    reject("Rust source mode holdout opened", lambda x: x["rust_contract"]["source_only_effects"].__setitem__("holdout_cases_opened", 1))
    reject("Rust guard weakened", lambda x: x["rust_contract"]["operational_runtime_guard_v4"].__setitem__("matching_fallback", "ALLOWED"))
    reject("Rust guard substituted", lambda x: x["rust_contract"]["operational_runtime_guard_v4"].__setitem__("complete_contract_sha256", "0" * 64))
    reject("Rust first-party bridge substituted", lambda x: x["rust_contract"]["actual_v24_native_build"].__setitem__("native_bridge_sha256", "0" * 64))
    reject("Rust first-party engine substituted", lambda x: x["rust_contract"]["actual_v24_native_build"].__setitem__("native_engine_sha256", "0" * 64))
    reject("Rust external matching delegated", lambda x: x["rust_contract"]["actual_v24_native_build"].__setitem__("external_regular_expression_engine", "ALLOWED"))
    reject("Rust historical V22 failure hidden", lambda x: x["rust_contract"]["immutable_actual_v22_failure"].__setitem__("verified_passing_case_count", 15_877))

    receipt_changes = {
        "Rust candidate falsely passes": ("candidate_status", "PASS"),
        "Rust candidate falsely qualifies": ("candidate_qualified", True),
        "Rust publication pass redefined": ("publication_pass_means", "CANDIDATE CORRECTNESS"),
        "Rust correctness denominator changed": ("case_execution_denominator", DENOMINATOR + SUPPLEMENTAL),
        "Rust passing score inflated": ("verified_passing_case_count", 15_878),
        "Rust exact mismatch understated": ("semantic_mismatch_count", 1351),
        "Rust complete group hidden": ("completed_suite_count", 12),
        "Rust worker duplicated": ("distinct_worker_process_id_count", 12),
        "Rust worker failure hidden": ("worker_failure_capture_count", 1),
        "Rust infrastructure failure hidden": ("infrastructure_failure_count", 1),
        "Rust complete suite rows hidden": ("all_original_suite_rows_validated_before_publication", False),
        "Rust original targets not restored": ("all_four_original_targets_restored", False),
        "Rust native provenance substituted": ("native_bridge_sha256", "0" * 64),
        "Rust native engine substituted": ("native_engine_sha256", "0" * 64),
        "Rust archive opened": ("actual_v24_build_archive_read_count", 1),
        "Rust corrected references replaced": ("corrected_reference_case_count", 6913),
        "Rust prior actual campaign erased": ("preserved_previous_rust_verified_passing_case_count", 14_725),
        "Rust speed invented": ("performance", "1.5x"),
        "Rust timing trial invented": ("timing_trials_run", 1),
        "Rust clock sampled": ("clock_samples", 1),
        "Rust hidden case read": ("hidden_cases_read", 1),
        "Rust holdout opened": ("holdout", "OPENED"),
        "Rust winner selected": ("winner_selected", True),
    }
    for label, (key, value) in receipt_changes.items():
        reject(label, lambda x, k=key, v=value: x["rust_receipt"].__setitem__(k, v))
    reject("Rust worker PIDs duplicated", lambda x: x["rust_receipt"]["actual_worker_process_ids"].__setitem__(1, x["rust_receipt"]["actual_worker_process_ids"][0]))
    reject("Rust exact substitution loss hidden", lambda x: x["rust_receipt"]["suite_integrity"][7].__setitem__("mismatch_count", 239))
    reject("Rust exact shape loss hidden", lambda x: x["rust_receipt"]["suite_integrity"][8].__setitem__("mismatch_count", 1111))
    reject("Rust managed recovery fabricated", lambda x: x["rust_receipt"]["suite_integrity"][4].__setitem__("verified_passing_case_count", 1023))
    reject("Rust real subinterpreter recovery erased", lambda x: x["rust_receipt"]["suite_integrity"][10].__setitem__("failure_class", "CANDIDATE EXECUTION FAILURE"))
    reject("Rust original suite order changed", lambda x: x["rust_receipt"]["suite_integrity"].reverse())
    reject("Rust worker failure capture erased", lambda x: x["rust_receipt"]["worker_failure_capture"].__setitem__("all_failure_metadata_preserved", False))
    reject("Rust compressed archive substituted", lambda x: x["rust_receipt"]["archive"].__setitem__("sha256", "0" * 64))
    reject("Rust restored native owner removed", lambda x: x["rust_receipt"]["restored_original_targets"].pop("engine"))

    c_changes = {
        "historical C candidate falsely passes": ("candidate_status", "PASS"),
        "historical C score inflated": ("verified_passing_case_count", 16_414),
        "historical C execution failure hidden": ("candidate_execution_failure_count", 0),
        "historical C observed mismatch hidden": ("complete_observed_semantic_mismatch_record_count", 605),
        "historical C supplemental cases merged": ("separate_reference_cases_counted_as_candidate_cases", True),
        "historical C exact mismatch invented": ("semantic_mismatch_count", 606),
    }
    for label, (key, value) in c_changes.items():
        reject(label, lambda x, k=key, v=value: x["c_receipt"].__setitem__(k, v))
    reject("historical C suite outcomes hidden", lambda x: x["c_receipt"]["suite_outcomes"].pop())

    proposal_changes = {
        "proposal falsely frozen": ("final_protocol_status", "FROZEN"),
        "proposal secretly generated": ("secret_status", "GENERATED"),
        "proposal cases opened": ("case_status", "GENERATED; OPENED"),
        "proposal benchmark falsely run": ("timing_status", "RUN"),
        "proposal denominator inflated": ("case_count", PROPOSAL + 1),
        "proposal candidate gate weakened": ("minimum_qualified_independent_family_count", 2),
        "proposal candidate falsely qualified": ("qualified_independent_family_count", 1),
        "proposal previous history erased": ("preserved_immediate_previous_proposal_case_count", 4_194_304),
        "proposal original P0 denominator changed": ("original_p0_case_count", PROPOSAL),
        "proposal winner invented": ("winner_status", "SELECTED"),
    }
    for label, (key, value) in proposal_changes.items():
        reject(label, lambda x, k=key, v=value: x["proposal_contract"].__setitem__(k, v))
    reject("proposal axis duplicated", lambda x: x["proposal_contract"]["operations"].__setitem__(1, x["proposal_contract"]["operations"][0]))
    reject("proposal immutable goal removed", lambda x: x["proposal_contract"]["required_public_source_pins"].pop(0))
    reject("proposal public statement hides unopened status", lambda x: x.__setitem__("proposal_protocol", x["proposal_protocol"].replace(b"NOT OPENED", b"WITHHELD")))

    def wall_reject(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            labels.append(label)
            return
        raise Rejected("hostile source-only wall accepted: " + label)

    wall_reject("wall forbids candidate source read", "open",
                (os.path.join(ROOT, "candidates/rust_candidate.py"), None, os.O_RDONLY | os.O_NOFOLLOW))
    wall_reject("wall forbids native binary read", "open",
                (os.path.join(ROOT, "candidates/_rust_engine.so"), None, os.O_RDONLY | os.O_NOFOLLOW))
    wall_reject("wall forbids compressed campaign archive read", "open",
                (receipt_archive_path(context), None, os.O_RDONLY | os.O_NOFOLLOW))
    wall_reject("wall forbids private build-root read", "open",
                (context["rust_contract"]["actual_v24_native_build"]["private_root_path"], None,
                 os.O_RDONLY | os.O_NOFOLLOW))
    wall_reject("wall forbids hidden holdout read", "open",
                (os.path.join(ROOT, "oracle/phase3/hidden-cases.json"), None, os.O_RDONLY | os.O_NOFOLLOW))
    wall_reject("wall forbids source owner without no-follow", "open",
                (os.path.join(ROOT, "GOAL.md"), None, os.O_RDONLY))
    wall_reject("wall forbids ordinary output write", "open",
                (os.path.join(ROOT, OUTPUT + ".svg"), None, os.O_WRONLY | os.O_CREAT))
    wall_reject("wall forbids candidate process", "subprocess.Popen", (PYTHON,))
    wall_reject("wall forbids network", "socket.connect", ("example.invalid",))
    wall_reject("wall forbids native loading", "ctypes.dlopen", ("candidate.so",))
    wall_reject("wall forbids clock samples", "time.perf_counter", ())
    wall_reject("wall forbids worker threads", "_thread.start_new_thread", ())
    wall_reject("wall forbids matching candidate import", "import", ("candidates.rust_candidate",))
    wall_reject("wall forbids stdlib regex import", "import", ("re",))
    wall_reject("wall forbids destructive rename", "os.rename", ("a", "b"))

    assets = build_assets(context, source_sha256, source_size)
    require(assets == build_assets(context, source_sha256, source_size),
            "V100 public outputs are not deterministic")
    require(len(assets["summary"]) < 65_536 and len(assets["inputs"]) < 32_768,
            "V100 copied complete historical evidence instead of preserving pinned references")
    require(PREVIOUS["summary"][1].encode() in assets["summary"],
            "V100 compact summary omitted the complete V99 summary fingerprint")
    for token in (b"15,877 / 31,237", b"+1,152", b"1,352", b"141,557,760",
                  b"NOT MEASURED", b"NOT FROZEN", b"NOT GENERATED; NOT OPENED"):
        require(token in assets["svg"], "V100 readable graphic omitted " + token.decode())
    require(b'role="img"' in assets["svg"] and b'aria-labelledby="title description"' in assets["svg"],
            "V100 readable graphic omitted its accessible title or description")
    return len(labels)


def receipt_archive_path(context: dict) -> str:
    return context["rust_receipt"]["archive"]["path"]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    names = ("source", "previous-source", "previous-inputs", "previous-summary", "previous-svg",
             "rust-source", "rust-protocol", "rust-contract", "rust-receipt", "c-receipt",
             "proposal-source", "proposal-protocol", "proposal-contract")
    for name in names:
        parser.add_argument("--" + name + "-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    args = arguments()
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6),
            "the frozen stable CPython 3.14.6 interpreter is required")
    require(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode,
            "the frozen interpreter requires flags -I -B -S")
    for group, prefix in ((PREVIOUS, "previous"), (RUST, "rust"), (HOLDOUT, "proposal")):
        for key, spec in group.items():
            require(getattr(args, prefix + "_" + key + "_sha256") == spec[1],
                    f"frozen {prefix} {key} SHA-256 argument changed")
    require(args.c_receipt_sha256 == C_RECEIPT[1], "frozen historical C receipt SHA-256 changed")
    source_sha256 = args.source_sha256
    require(len(source_sha256) == 64 and all(char in "0123456789abcdef" for char in source_sha256),
            "V100 renderer source SHA-256 must be lowercase hexadecimal")
    wall = SourceWall(args.render)
    sys.addaudithook(wall.check)
    source_size = os.stat(os.path.join(ROOT, SELF), follow_symlinks=False).st_size
    source = owner(SELF, source_sha256, source_size)
    goal = owner("GOAL.md", GOAL_SHA256, 3756)
    previous = {key: owner(*spec) for key, spec in PREVIOUS.items()}
    rust = {key: owner(*spec) for key, spec in RUST.items()}
    c_receipt = owner(*C_RECEIPT)
    proposal = {key: owner(*spec) for key, spec in HOLDOUT.items()}
    context = {
        "goal": goal,
        "previous_inputs": parsed(previous["inputs"], "complete V99 inputs"),
        "previous_summary": parsed(previous["summary"], "complete V99 summary"),
        "previous_svg": previous["svg"],
        "rust_contract": parsed(rust["contract"], "frozen Rust V24 campaign contract"),
        "rust_receipt": parsed(rust["receipt"], "actual complete Rust V24 public receipt"),
        "c_receipt": parsed(c_receipt, "historical actual C12 public receipt"),
        "proposal_protocol": proposal["protocol"],
        "proposal_contract": parsed(proposal["contract"], "unopened V2 holdout proposal"),
    }
    verify_context(context)
    assets = build_assets(context, source_sha256, len(source))
    hostile_controls = mutation_controls(context, source_sha256, len(source), wall) if args.self_test else 0
    if args.render:
        for key, data in assets.items():
            suffix = ".svg" if key == "svg" else "." + key + ".json"
            descriptor = os.open(os.path.join(ROOT, OUTPUT + suffix),
                                 os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                position = 0
                while position < len(data):
                    written = os.write(descriptor, data[position:])
                    require(written > 0, "exclusive public output write was truncated")
                    position += written
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    report = {
        "status": "PASS",
        "mode": "self-test" if args.self_test else "render" if args.render else "verify-frozen-context",
        "source_sha256": source_sha256, "source_bytes": len(source),
        "hostile_control_count": hostile_controls,
        "candidate_status": "FAIL", "verified_original_checks": 15_877,
        "original_case_execution_denominator": DENOMINATOR,
        "verified_original_check_increase_from_previous_graph": 1152,
        "completed_original_suite_count": 13, "passing_original_suite_count": 11,
        "exact_semantic_mismatch_count": 1352,
        "exact_semantic_mismatches_by_suite": dict(RUST_MISMATCHES),
        "managed_original_checks_passed": 1024, "subinterpreter_original_checks_passed": 128,
        "distinct_candidate_worker_count": 13, "worker_failure_count": 0,
        "infrastructure_failure_count": 0, "performance": UNMEASURED,
        "proposed_unopened_final_case_count": PROPOSAL,
        "candidate_source_owners_opened": 0, "native_binary_files_opened": 0,
        "native_binary_metadata_probes": 0, "compressed_archives_opened": 0,
        "compressed_archives_statted": 0, "private_build_roots_opened": 0,
        "private_build_roots_statted": 0, "hidden_cases_read": 0,
        "candidate_workers_started": 0, "reference_workers_started": 0,
        "compiler_processes_started": 0, "clock_samples": 0,
        "workspace_mutations": 3 if args.render else 0,
        "predicted_outputs": {
            key: {"path": OUTPUT + (".svg" if key == "svg" else "." + key + ".json"),
                  "bytes": len(data), "sha256": digest(data)}
            for key, data in assets.items()
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
