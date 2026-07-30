#!/usr/bin/env python3
"""Render the observed Rust original-suite result without inspecting candidates."""

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
SELF = "tools/render_latest_rust_original_correctness_v103.py"
OUTPUT = "docs/evidence/candidate-current-overview-v103"
VERSION = 103
DENOMINATOR = 31_237
SUPPLEMENTAL = 8_244
UNMEASURED = "NOT MEASURED"
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
PREVIOUS = {
    "source": (
        "tools/render_candidate_current_overview_v101.py",
        "90d43057cc8f1d6cf168055000fc03b8779c3282948c7f5958363e8bbefc97d4",
        69_905,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v101.inputs.json",
        "157e2e63b154bf0360b9160ce110e0d97534a9bc1da3f57a3e98a2b1d532bda8",
        10_788,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v101.json",
        "d0d2ee8e550fdd3198c6d946b67dfc8c3caed3ea97484334fbd12ea2eef2abdd",
        31_471,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v101.svg",
        "6665fa945dc06db57755304294433f103291c92e0b650c771584621fc84c4188",
        10_053,
    ),
}
CAMPAIGN = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v26.py",
        "37d3edd69f93c33defaaeb8a1473e39b0563f06af57e6038340679dd8c61091d",
        97_746,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V26.md",
        "aefd84daf141fc92e73c6fedec82a9c179b9d67db6f67f93bcaf6d8cca40b42d",
        7_501,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v26.json",
        "8493afcb087e79b0b2419711746fb82dd5c09785fe086fa627ea99af41365eaa",
        22_874,
    ),
}
V25_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-"
    "failures-publication-receipt.json",
    "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59",
    11_832,
)
AUDIT = (
    "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json",
    "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19",
    20_985,
)
RECEIPT_PREFIX = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v30-rust-complete-semantic-source-root-provenance-original-p0-v26"
)
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1_024),
    ("buffer_v3", 768),
    ("managed_v1", 1_024),
    ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912),
    ("substitution_v2", 5_120),
    ("shape_v2", 10_240),
    ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
COLORS = {
    "background": "#0b1220",
    "surface": "#101b2b",
    "line": "#30445e",
    "muted": "#cbd5e1",
    "faint": "#94a3b8",
    "white": "#f8fafc",
    "python": "#34d399",
    "rust": "#60a5fa",
    "unfinished": "#fbbf24",
    "danger": "#fda4af",
}


class Rejected(ValueError):
    """A public owner, historical result, or rendering boundary changed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise Rejected(message)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False,
                   separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def pairs(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject duplicate authenticated public JSON fields")
        result[key] = value
    return result


def document(payload: bytes, label: str) -> dict:
    try:
        value = json.loads(
            payload,
            object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(
                Rejected("reject nonfinite public JSON")),
        )
    except (ValueError, UnicodeError, TypeError) as failure:
        raise Rejected("reject invalid authenticated public JSON: " + label) from failure
    require(type(value) is dict and canonical(value) == payload,
            "reject noncanonical authenticated public JSON: " + label)
    return value


def same(actual: object, expected: dict, label: str) -> None:
    require(type(actual) is dict, "require authenticated object: " + label)
    for key, value in expected.items():
        require(actual.get(key) == value,
                "authenticated public evidence changed: " + label + ": " + key)


def reference(spec: tuple[str, str, int]) -> dict:
    return {"path": spec[0], "sha256": spec[1], "bytes": spec[2]}


def pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(letter in "0123456789abcdef" for letter in value),
            "require a complete lowercase SHA-256 pin: " + label)
    return value


def exact_receipt(path: object, digest: object, size: object) -> tuple[str, str, int]:
    require(type(path) is str and path.startswith(RECEIPT_PREFIX)
            and path.endswith("-publication-receipt.json")
            and path.count("/") == RECEIPT_PREFIX.count("/")
            and ".." not in path.split("/")
            and len(path) < 300,
            "accept only the actual immutable V26 original-campaign public receipt")
    require(type(size) is int and 1 <= size <= 262_144,
            "reject absent, truncated, compressed, or oversized V26 receipt")
    return path, pin(digest, "V26 actual public receipt"), size


def specifications(receipt: tuple[str, str, int]) -> tuple[tuple[str, str, int], ...]:
    return (GOAL, *PREVIOUS.values(), *CAMPAIGN.values(), V25_RECEIPT, AUDIT, receipt)


class SourceWall:
    """Deny every file except explicitly authenticated public plaintext owners."""

    def __init__(self, receipt: tuple[str, str, int], render: bool) -> None:
        self.render = render
        self.owners = frozenset(
            os.path.join(ROOT, owner[0]) for owner in specifications(receipt)
        ) | {os.path.join(ROOT, SELF)}
        self.outputs = frozenset(
            os.path.join(ROOT, OUTPUT + suffix)
            for suffix in (".svg", ".inputs.json", ".json")
        )

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str,
                    "reject descriptor-only, relative, candidate, or hidden file access")
            writes = bool(flags & (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
            ))
            if writes:
                exclusive = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.render and path in self.outputs
                        and flags & exclusive == exclusive,
                        "reject unowned, nonexclusive, or source-only graph mutation")
            else:
                require(path in self.owners and flags & os.O_NOFOLLOW != 0,
                        "reject candidate, native, archive, proposal, seed, or holdout")
            return
        forbidden_prefixes = (
            "subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn",
        )
        forbidden_events = {
            "os.system", "os.fork", "os.posix_spawn", "os.mkdir", "os.remove",
            "os.rename", "os.rmdir", "os.chdir", "os.chmod", "os.link",
            "os.symlink", "os.truncate", "os.putenv", "time.time",
            "time.monotonic", "time.perf_counter", "_thread.start_new_thread",
        }
        if event.startswith(forbidden_prefixes) or event in forbidden_events:
            raise Rejected("reject process, clock, native load, network, thread, or mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (
                type(name) is str
                and (name in {"re", "_sre", "regex", "re2", "gzip", "ctypes"}
                     or name.startswith(("candidates.", "rebar.")))
            ), "reject candidate, decompressor, native binding, or matching import")


def read_owner(spec: tuple[str, str, int], allowed: tuple[tuple[str, str, int], ...]) -> bytes:
    relative, expected, size = spec
    require(spec in allowed, "reject public owner outside the exact V103 allowlist")
    descriptor = os.open(
        os.path.join(ROOT, relative), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
    )
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_uid == os.getuid()
                and identity.st_nlink == 1
                and identity.st_size == size,
                "authenticated public evidence owner changed: " + relative)
        blocks = []
        while True:
            block = os.read(descriptor, 1_048_576)
            if not block:
                break
            blocks.append(block)
        result = b"".join(blocks)
        require(sha256(result) == expected,
                "authenticated public evidence digest changed: " + relative)
        return result
    finally:
        os.close(descriptor)


def verify_history(context: dict) -> None:
    inputs = context["previous_inputs"]
    summary = context["previous_summary"]
    expected = {
        "version": 101,
        "actual_current_graph_predecessor_version": 100,
        "goal_sha256": GOAL[1],
        "python": "3.14.6",
        "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": len(SUITES),
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": len(SUITES),
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    same(inputs, expected, "immutable V101 inputs")
    same(summary, expected, "immutable V101 summary")
    same(summary, {
        "schema": "rebar-candidate-current-overview-v101-summary",
        "status": "PASS",
        "rust_v25_candidate_status": "FAIL",
        "rust_v25_candidate_qualified": False,
        "c_v12_candidate_status": "FAIL",
        "c_v12_candidate_qualified": False,
        "independent_v4_nondelegation_status": "FAIL",
        "independent_v4_nondelegation_finding_count": 1,
    }, "historical V101 publication is not candidate qualification")
    require(inputs.get("headline") == summary.get("headline")
            and inputs.get("snapshot") == summary.get("snapshot")
            and inputs.get("previous_overview") == summary.get("previous_overview"),
            "immutable previous inputs and summary no longer describe the same history")
    same(inputs.get("renderer"), reference(PREVIOUS["source"]),
         "immutable V101 renderer")
    same(summary.get("headline"), {
        "original_python_check_count": DENOMINATOR,
        "original_python_suite_count": len(SUITES),
        "c_current_verified_original_checks": 16_413,
        "rust_current_verified_original_checks": 15_877,
        "zig_current_verified_original_checks": 4_607,
        "rust_current_candidate_status": "FAIL",
        "rust_current_candidate_qualified": False,
        "rust_current_exact_semantic_mismatch_count": 1_352,
        "rust_current_semantic_mismatches_by_group": {
            "shape_v2": 1_112,
            "substitution_v2": 240,
        },
        "rust_current_completed_original_group_count": len(SUITES),
        "rust_current_distinct_candidate_worker_count": len(SUITES),
        "c_current_candidate_execution_failure_count": 1,
        "c_current_observed_individual_mismatch_records": 606,
        "speed_relative_to_python": UNMEASURED,
        "performance": UNMEASURED,
        "winner_selected": False,
    }, "preserve all previously observed Python, C, Rust, and Zig results")
    same(summary.get("snapshot"), {
        "c_v12_original_campaign_candidate_execution_failure_count": 1,
        "c_v12_original_campaign_complete_observed_individual_mismatch_record_count": 606,
        "c_v12_original_campaign_verified_passing_case_count": 16_413,
        "rust_v25_original_campaign_verified_passing_case_count": 15_877,
        "rust_v25_original_campaign_semantic_mismatch_count": 1_352,
        "zig_v12_original_campaign_verified_passing_case_count": 4_607,
        "winner_selected": False,
    }, "preserve historical C and Zig observations and all Rust losses")
    require(type(summary.get("c_v12_suite_outcomes")) is list
            and len(summary["c_v12_suite_outcomes"]) == len(SUITES)
            and type(summary.get("c_v12_complete_mismatch_suite_vector_fingerprints"))
            is list
            and len(summary["c_v12_complete_mismatch_suite_vector_fingerprints"]) == 12
            and type(summary.get("rust_v25_suite_outcomes")) is list
            and len(summary["rust_v25_suite_outcomes"]) == len(SUITES),
            "preserve every previous observed original Rust and C outcome")
    require(context["previous_svg"].startswith(b"<svg ")
            and b'role="img"' in context["previous_svg"]
            and b"15,877 / 31,237" in context["previous_svg"]
            and b"16,413 / 31,237" in context["previous_svg"]
            and b"4,607 / 31,237" in context["previous_svg"],
            "preserve the complete predecessor graph without republishing stale metadata")
    historical = context["historical_receipt"]
    same(historical, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "case_execution_denominator": DENOMINATOR,
        "suite_count": len(SUITES),
        "completed_suite_count": len(SUITES),
        "verified_passing_case_count": 15_877,
        "semantic_mismatch_count": 1_352,
        "actual_candidate_workers": len(SUITES),
        "distinct_worker_process_id_count": len(SUITES),
        "all_four_original_targets_restored": True,
        "winner_selected": False,
    }, "authenticate the exact previous actual Rust FAIL-1352 receipt")
    require(type(historical.get("suite_integrity")) is list
            and len(historical["suite_integrity"]) == len(SUITES),
            "preserve every historical Rust failure and successful suite")


def verify_frozen_campaign(context: dict) -> None:
    contract = context["contract"]
    same(contract, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v26-recoverable-source-freeze",
        "version": 26,
        "family": "rust",
        "goal_sha256": GOAL[1],
        "status": "SOURCE FROZEN; ACTUAL V30 BUILD PASS; ORIGINAL CAMPAIGN NOT RUN",
    }, "independently frozen V26 campaign is not its later actual outcome")
    same(contract.get("source"), reference(CAMPAIGN["source"]),
         "frozen V26 campaign source")
    same(contract.get("protocol"), reference(CAMPAIGN["protocol"]),
         "frozen V26 campaign protocol")
    same(contract.get("original_correctness_boundary"), {
        "case_execution_denominator": DENOMINATOR,
        "suite_count": len(SUITES),
        "named_private_waiver_count": len(SUITES),
        "supplemental_reference_case_count": SUPPLEMENTAL,
        "supplemental_counted_in_original_denominator": False,
        "candidate_correctness": UNMEASURED,
        "candidate_semantic_mismatch_count": UNMEASURED,
        "candidate_verified_passing_case_count": UNMEASURED,
        "candidate_original_oracle_pass": UNMEASURED,
        "original_suite_correctness_qualified": UNMEASURED,
        "candidate_qualified": False,
    }, "frozen original boundary remains distinct from the actual V26 receipt")
    rows = contract["original_correctness_boundary"].get("suites")
    require(type(rows) is list and len(rows) == len(SUITES),
            "frozen V26 contract must include every original suite")
    for actual, (name, denominator) in zip(rows, SUITES, strict=True):
        same(actual, {
            "id": name,
            "case_execution_denominator": denominator,
            "candidate_status": "NOT RUN",
            "candidate_workers_started": 0,
            "semantic_mismatch_count": UNMEASURED,
        }, "immutable V26 original suite " + name)
    same(contract.get("actual_v30_native_build"), {
        "build_status": "PASS",
        "label": "phase2-v30-rust-complete-semantic-source-root-provenance",
        "actual_compiler_process_count": 28,
        "independent_native_artifact_count": 4,
        "independent_private_phase_count": 2,
        "native_engine_sha256":
            "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237",
        "native_bridge_sha256":
            "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256",
        "corrected_bridge_source_sha256":
            "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55",
        "corrected_public_adapter_sha256":
            "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e",
        "optimized_engine_source_sha256":
            "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee",
        "optimized_search_source_sha256":
            "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7",
        "external_cargo_dependency_count": 0,
        "external_regular_expression_engine": "FORBIDDEN",
        "cross_candidate_engine": "FORBIDDEN",
        "matching_fallback": "FORBIDDEN",
        "archive_opened": False,
    }, "preserve the independently built first-party optimized Rust engine")
    same(contract.get("immutable_previous_v25_campaign"), {
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL",
        "semantic_mismatch_count": 1_352,
        "verified_passing_case_count": 15_877,
        "actual_candidate_workers": len(SUITES),
    }, "preserve the exact earlier Rust candidate failure")
    same(contract.get("independent_runtime_non_delegation_v4_audit"), {
        "status": "FAIL",
        "finding_count": 1,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
        "historical_finding_is_not_new_corrected_bridge_audit": True,
        "new_corrected_runtime_audit": "NOT RUN",
    }, "historical non-delegation audit remains separate from original correctness")
    same(contract.get("source_only_effects"), {
        "candidate_workers_started": 0,
        "candidate_imports": 0,
        "reference_workers_started": 0,
        "native_binary_files_opened": 0,
        "native_libraries_loaded": 0,
        "compressed_archives_opened": 0,
        "compressed_archives_inflated": 0,
        "hidden_cases_read": 0,
        "holdout_cases_opened": 0,
        "retired_final_proposal_opens": 0,
        "successor_final_proposal_opens": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }, "frozen public campaign source has no timing, candidate, or holdout effects")
    audit = context["audit"]
    same(audit, {
        "status": "FAIL",
        "finding_count": 1,
        "runtime_non_delegation": "NOT ESTABLISHED; CANDIDATES NEVER EXECUTED",
    }, "preserve the separate historical V4 audit failure")
    require(type(audit.get("findings")) is list and len(audit["findings"]) == 1,
            "preserve the separately recorded historical no-delegation finding")


def verify_actual(context: dict) -> None:
    result = context["receipt"]
    same(result, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v26-durable-publication-receipt",
        "family": "rust",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "suite_count": len(SUITES),
        "completed_suite_count": len(SUITES),
        "attempted_suite_count": len(SUITES),
        "started_suite_count": len(SUITES),
        "case_execution_denominator": DENOMINATOR,
        "actual_candidate_workers": len(SUITES),
        "distinct_worker_process_id_count": len(SUITES),
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "all_original_observation_vectors_complete": True,
        "all_original_suite_rows_validated_before_publication": True,
        "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "historical_runtime_non_delegation_v4_status": "FAIL",
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "winner_selected": False,
        "named_private_waiver_count": len(SUITES),
        "campaign_source_sha256": CAMPAIGN["source"][1],
        "campaign_protocol_sha256": CAMPAIGN["protocol"][1],
        "campaign_contract_sha256": CAMPAIGN["contract"][1],
        "native_engine_sha256":
            "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237",
        "native_bridge_sha256":
            "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256",
        "combined_bridge_source_sha256":
            "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55",
        "corrected_public_adapter_sha256":
            "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e",
    }, "authenticate the complete actual root-executed Rust V26 campaign")
    status = result.get("candidate_status")
    require(status in {"PASS", "FAIL"},
            "the actual candidate outcome must be an observed PASS or FAIL")
    require(result.get("status") == "PASS",
            "publication success is required separately from candidate success")
    original_pass = status == "PASS"
    require(result.get("candidate_original_oracle_pass") is original_pass
            and result.get("original_suite_correctness_qualified") is original_pass,
            "keep an original-suite PASS separate from full replacement qualification")
    rows = result.get("suite_integrity")
    require(type(rows) is list and len(rows) == len(SUITES),
            "the actual outcome must preserve all 13 individually observed suites")
    identifiers = result.get("actual_worker_process_ids")
    require(type(identifiers) is list and len(identifiers) == len(SUITES)
            and all(type(identity) is int and identity > 0 for identity in identifiers)
            and len(set(identifiers)) == len(SUITES),
            "require all 13 genuinely distinct original candidate processes")
    total_cases = 0
    verified_cases = 0
    mismatches = 0
    for row, (name, count) in zip(rows, SUITES, strict=True):
        same(row, {
            "suite": name,
            "case_execution_denominator": count,
            "fully_observed": True,
            "actual_worker_started": True,
            "worker_attempted": True,
        }, "actual original candidate suite " + name)
        require(type(row.get("pid")) is int and row["pid"] in identifiers,
                "every actual suite must record its distinct real worker")
        failure = row.get("failure_class")
        require(failure in {"PASS", "SEMANTIC MISMATCH"},
                "reject an unexplained candidate execution or infrastructure failure")
        match_count = row.get("verified_passing_case_count")
        mismatch_count = row.get("mismatch_count")
        require(type(match_count) is int and type(mismatch_count) is int
                and 0 <= match_count <= count and 0 <= mismatch_count <= count,
                "reject invented, negative, or overcounted original results")
        if failure == "PASS":
            require(match_count == count and mismatch_count == 0
                    and row.get("returncode") == 0,
                    "a passed original suite must actually verify all its cases")
        else:
            require(match_count == 0 and mismatch_count > 0
                    and row.get("returncode") != 0,
                    "an unfinished or failing original group cannot count as passed")
        total_cases += count
        verified_cases += match_count
        mismatches += mismatch_count
    require(total_cases == DENOMINATOR
            and result.get("verified_passing_case_count") == verified_cases
            and result.get("semantic_mismatch_count") == mismatches
            and result.get("infrastructure_failure_count") == 0
            and result.get("worker_failure_capture_count") == 0,
            "the complete exact original loss vector and denominator must balance")
    if original_pass:
        require(verified_cases == DENOMINATOR and mismatches == 0
                and all(row.get("failure_class") == "PASS" for row in rows),
                "a Rust original PASS requires all 31,237 genuine checks")
    else:
        require(mismatches > 0 and verified_cases < DENOMINATOR,
                "never hide an actual candidate original failure")


def verify(context: dict) -> None:
    require(sha256(context["goal"]) == GOAL[1],
            "the immutable /goal objective changed")
    for key, expected in (
        ("previous_inputs", PREVIOUS["inputs"][1]),
        ("previous_summary", PREVIOUS["summary"][1]),
        ("contract", CAMPAIGN["contract"][1]),
        ("historical_receipt", V25_RECEIPT[1]),
        ("audit", AUDIT[1]),
        ("receipt", context["receipt_owner"][1]),
    ):
        require(sha256(canonical(context[key])) == expected,
                "complete authenticated public document changed: " + key)
    require(sha256(context["previous_svg"]) == PREVIOUS["svg"][1],
            "complete immutable V101 SVG changed")
    verify_history(context)
    verify_frozen_campaign(context)
    verify_actual(context)


def escape(value: object) -> str:
    text = str(value)
    return (text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def percentage(value: int) -> str:
    if value == DENOMINATOR:
        return "100%"
    return f"{value * 100 / DENOMINATOR:.1f}%"


def svg(context: dict) -> bytes:
    result = context["receipt"]
    passed = result["candidate_status"] == "PASS"
    rust_count = result["verified_passing_case_count"]
    mismatches = result["semantic_mismatch_count"]
    title = "Can a new engine match Python re?"
    status_line = (
        "Rust now matches all 31,237 original Python checks"
        if passed else
        f"Rust still differs on {mismatches:,} original Python checks"
    )
    qualification_line = (
        "Original checks: PASS  ·  Complete drop-in replacement: NOT YET PROVEN"
        if passed else
        "Original checks: FAIL  ·  Complete drop-in replacement: NOT YET PROVEN"
    )
    description = (
        f"Original correctness only, not speed. Python passes {DENOMINATOR:,} of "
        f"{DENOMINATOR:,} checks. Rust verifies {rust_count:,}, C verifies 16,413, "
        "and Zig verifies 4,607. C++, Go, and Fortran remain unmeasured. "
        f"Rust has {mismatches:,} mismatches across 13 independently observed groups. "
        "A complete replacement and its independent no-delegation proof remain "
        "unestablished. Final speed and memory are not measured. No winner."
    )
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="1090" '
        'viewBox="0 0 1380 1090" role="img" aria-labelledby="title description">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="description">{escape(description)}</desc>',
        f'<rect width="1380" height="1090" rx="24" fill="{COLORS["background"]}"/>',
        '<text x="56" y="75" fill="#f8fafc" font-size="36" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        + escape(title) + '</text>',
        '<text x="58" y="108" fill="#cbd5e1" font-size="18" '
        'font-family="system-ui,sans-serif">'
        'The bars show compatibility, not performance.</text>',
        '<rect x="55" y="136" width="1270" height="102" rx="15" '
        'fill="#132238" stroke="#30445e"/>',
        '<text x="76" y="174" fill="'
        + (COLORS["python"] if passed else COLORS["danger"])
        + '" font-size="22" font-family="system-ui,sans-serif" '
        'font-weight="750">' + escape(status_line) + '</text>',
        '<text x="77" y="208" fill="#e2e8f0" font-size="16" '
        'font-family="system-ui,sans-serif">'
        + escape(qualification_line) + '</text>',
        '<text x="67" y="275" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="680">APPROACH</text>',
        '<text x="185" y="275" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'ORIGINAL CHECKS PASSED</text>',
        '<text x="744" y="275" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="680">WHAT THIS MEANS</text>',
    ]
    rows = (
        ("Python re", DENOMINATOR, COLORS["python"],
         "The reference: all 13 groups pass", "REFERENCE"),
        ("Rust", rust_count, COLORS["rust"],
         "All 13 groups pass" if passed else f"{mismatches:,} differences remain",
         "ORIGINAL CHECKS PASS; MORE TESTS REQUIRED" if passed else "NOT COMPATIBLE"),
        ("C", 16_413, COLORS["unfinished"],
         "12 groups complete; 1 execution failure", "NOT COMPATIBLE"),
        ("Zig", 4_607, COLORS["unfinished"],
         "Previously observed original checks", "NOT COMPATIBLE"),
        ("C++", None, COLORS["faint"],
         "Complete original correctness not measured", UNMEASURED),
        ("Go", None, COLORS["faint"],
         "Complete original correctness not measured", UNMEASURED),
        ("Fortran", None, COLORS["faint"],
         "Complete original correctness not measured", UNMEASURED),
    )
    for index, (name, count, color, explanation, state) in enumerate(rows):
        top = 296 + index * 78
        middle = top + 33
        background = "#11243a" if name == "Rust" else COLORS["surface"]
        elements.append(
            f'<rect x="55" y="{top}" width="1270" height="66" rx="11" '
            f'fill="{background}"/>'
        )
        elements.append(
            f'<text x="74" y="{middle}" fill="#f8fafc" font-size="18" '
            f'font-family="system-ui,sans-serif" font-weight="690">'
            f'{escape(name)}</text>'
        )
        elements.append(
            f'<rect x="184" y="{top + 14}" width="320" height="18" rx="6" '
            'fill="#29384e"/>'
        )
        if count is not None:
            width = round(320 * count / DENOMINATOR)
            elements.append(
                f'<rect x="184" y="{top + 14}" width="{width}" height="18" '
                f'rx="6" fill="{color}"/>'
            )
            score = f"{count:,} / {DENOMINATOR:,}  ·  {percentage(count)}"
        else:
            score = UNMEASURED
        elements.append(
            f'<text x="518" y="{middle}" fill="#e2e8f0" font-size="15" '
            f'font-family="system-ui,sans-serif">{escape(score)}</text>'
        )
        elements.append(
            f'<text x="743" y="{middle}" fill="#e2e8f0" font-size="14" '
            f'font-family="system-ui,sans-serif">{escape(explanation)}</text>'
        )
        elements.append(
            f'<text x="743" y="{top + 53}" fill="{color}" font-size="11" '
            f'font-family="system-ui,sans-serif" font-weight="700">'
            f'{escape(state)}</text>'
        )
    elements += [
        '<rect x="55" y="858" width="617" height="147" rx="14" '
        'fill="#142135" stroke="#354459"/>',
        '<text x="76" y="892" fill="#93c5fd" font-size="18" '
        'font-family="system-ui,sans-serif" font-weight="735">'
        'What the Rust result proves</text>',
        '<text x="77" y="925" fill="#f8fafc" font-size="14" '
        'font-family="system-ui,sans-serif">'
        + ('All 31,237 original checks passed in 13 real workers.' if passed
           else f'{rust_count:,} checks verified; {mismatches:,} differences remain.')
        + '</text>',
        '<text x="77" y="954" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Previous Rust result: 15,877 passed; 1,352 differed.</text>',
        '<text x="77" y="982" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'No existing regular-expression package performs matching.</text>',
        '<rect x="690" y="858" width="635" height="147" rx="14" '
        'fill="#291923" stroke="#754453"/>',
        '<text x="711" y="892" fill="#fda4af" font-size="18" '
        'font-family="system-ui,sans-serif" font-weight="735">'
        'Still needed before a replacement can win</text>',
        '<text x="712" y="925" fill="#f8fafc" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'More compatibility tests and an independent no-delegation audit.</text>',
        '<text x="712" y="954" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Three genuinely independent engines must qualify.</text>',
        '<text x="712" y="982" fill="#fcd34d" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'FINAL SPEED: NOT MEASURED  ·  NO WINNER</text>',
        '<text x="58" y="1048" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'Each result uses exactly 31,237 original Python checks. '
        'The separate hidden final test remains unopened.</text>',
        '</svg>',
    ]
    return ("\n".join(elements) + "\n").encode("utf-8")


def assets(context: dict, own_sha: str, own_size: int) -> dict:
    result = context["receipt"]
    original_pass = result["candidate_status"] == "PASS"
    previous = context["previous_summary"]
    counts = {
        "python": DENOMINATOR,
        "rust": result["verified_passing_case_count"],
        "c": previous["headline"]["c_current_verified_original_checks"],
        "zig": previous["headline"]["zig_current_verified_original_checks"],
        "cpp": UNMEASURED,
        "go": UNMEASURED,
        "fortran": UNMEASURED,
    }
    suites = [
        {
            "suite": row["suite"],
            "case_execution_denominator": row["case_execution_denominator"],
            "verified_passing_case_count": row["verified_passing_case_count"],
            "semantic_mismatch_count": row["mismatch_count"],
            "candidate_status": row["failure_class"],
            "actual_worker_process_id": row["pid"],
            "complete_original_row_sha256": row["complete_original_row_sha256"],
        }
        for row in result["suite_integrity"]
    ]
    headline = {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "bars_measure": "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED",
        "python_version": "3.14.6",
        "original_python_check_count": DENOMINATOR,
        "original_python_suite_count": len(SUITES),
        "verified_original_checks_by_candidate": counts,
        "rust_current_verified_original_checks": result["verified_passing_case_count"],
        "rust_current_exact_semantic_mismatch_count": result["semantic_mismatch_count"],
        "rust_current_candidate_status": result["candidate_status"],
        "rust_current_original_oracle_pass": original_pass,
        "rust_current_original_suite_correctness_qualified": original_pass,
        "rust_current_candidate_qualified": False,
        "rust_current_completed_original_group_count": len(SUITES),
        "rust_current_distinct_candidate_worker_count": len(SUITES),
        "rust_current_infrastructure_failure_count": 0,
        "rust_previous_verified_original_checks": 15_877,
        "rust_previous_exact_semantic_mismatch_count": 1_352,
        "rust_verified_check_change_from_previous_graph":
            result["verified_passing_case_count"] - 15_877,
        "rust_semantic_mismatch_change_from_previous_graph":
            result["semantic_mismatch_count"] - 1_352,
        "c_current_verified_original_checks": 16_413,
        "c_current_observed_individual_mismatch_records": 606,
        "c_current_candidate_execution_failure_count": 1,
        "zig_current_verified_original_checks": 4_607,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "historical_independent_nondelegation_audit_status": "FAIL",
        "historical_independent_nondelegation_finding_count": 1,
        "independent_first_party_candidate_family_count": 6,
        "fully_compatible_candidate_count": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "speed_relative_to_python": UNMEASURED,
        "winner_selected": False,
    }
    shared = {
        "version": VERSION,
        "actual_current_graph_predecessor_version": 101,
        "goal_sha256": GOAL[1],
        "python": "3.14.6",
        "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": len(SUITES),
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": len(SUITES),
        "headline": headline,
        "renderer": {"path": SELF, "sha256": own_sha, "bytes": own_size},
        "previous_overview": {
            key: reference(value) for key, value in PREVIOUS.items()
        },
        "rust_v26_public_evidence": {
            **{key: reference(value) for key, value in CAMPAIGN.items()},
            "receipt": reference(context["receipt_owner"]),
        },
        "preserved_previous_rust_failure": reference(V25_RECEIPT),
        "historical_nondelegation_audit": reference(AUDIT),
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "native_binary_files_opened_by_graph": 0,
        "native_binary_metadata_probes_by_graph": 0,
        "native_libraries_loaded_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "private_build_roots_statted_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "compressed_archives_inflated_by_graph": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "seed_files_opened_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_holdout_opened": False,
        "clock_samples_by_graph": 0,
        "timing_trials_run": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "preserved_complete_history":
            "IMMUTABLE V101 SOURCE, INPUTS, SUMMARY, SVG, AND V25 ACTUAL FAILURE",
    }
    inputs = {
        **shared,
        "schema": "rebar-candidate-current-overview-v103-inputs",
    }
    summary = {
        **shared,
        "schema": "rebar-candidate-current-overview-v103-summary",
        "status": "PASS",
        "status_scope": "AUTHENTICATED ORIGINAL CORRECTNESS GRAPH ONLY",
        "candidate_status": result["candidate_status"],
        "candidate_original_oracle_pass": original_pass,
        "original_suite_correctness_qualified": original_pass,
        "candidate_qualified": False,
        "verified_passing_case_count": result["verified_passing_case_count"],
        "semantic_mismatch_count": result["semantic_mismatch_count"],
        "distinct_candidate_worker_count": len(SUITES),
        "worker_failure_capture_count": 0,
        "infrastructure_failure_count": 0,
        "complete_original_suite_results": suites,
        "previous_complete_original_suite_results":
            context["historical_receipt"]["suite_integrity"],
        "preserved_c_original_suite_results": previous["c_v12_suite_outcomes"],
        "preserved_c_observed_mismatch_vector_fingerprints":
            previous["c_v12_complete_mismatch_suite_vector_fingerprints"],
        "previous_rust_verified_passing_case_count": 15_877,
        "previous_rust_semantic_mismatch_count": 1_352,
    }
    return {
        "svg": svg(context),
        "inputs": canonical(inputs),
        "summary": canonical(summary),
    }


def verify_outputs(context: dict, value: dict, own_sha: str, own_size: int) -> None:
    require(value == assets(context, own_sha, own_size),
            "the correctness graph lost evidence or is not reproducible")
    inputs = document(value["inputs"], "V103 public graph inputs")
    summary = document(value["summary"], "V103 public graph summary")
    require(inputs["headline"] == summary["headline"]
            and inputs["previous_overview"] == summary["previous_overview"]
            and inputs["rust_v26_public_evidence"] == summary["rust_v26_public_evidence"],
            "the complete graph inputs and published summary disagree")
    same(summary, {
        "version": VERSION,
        "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": len(SUITES),
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "timing_trials_run": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_holdout_opened": False,
        "winner_selected": False,
    }, "publish an honest original-suite result without candidate qualification")
    actual = context["receipt"]
    same(summary, {
        "candidate_status": actual["candidate_status"],
        "candidate_original_oracle_pass": actual["candidate_original_oracle_pass"],
        "original_suite_correctness_qualified":
            actual["original_suite_correctness_qualified"],
        "verified_passing_case_count": actual["verified_passing_case_count"],
        "semantic_mismatch_count": actual["semantic_mismatch_count"],
    }, "the graph must preserve the exact actual root-executed candidate result")
    expected_tokens = (
        b'role="img"',
        b'aria-labelledby="title description"',
        b"31,237 / 31,237",
        b"16,413 / 31,237",
        b"4,607 / 31,237",
        b"15,877 passed; 1,352 differed",
        b"Complete drop-in replacement: NOT YET PROVEN",
        b"FINAL SPEED: NOT MEASURED",
        b"NO WINNER",
        b"Three genuinely independent engines",
        b"hidden final test remains unopened",
    )
    for token in expected_tokens:
        require(token in value["svg"],
                "the clear accessible public graph lost " + token.decode("ascii"))
    if actual["candidate_status"] == "PASS":
        require(b"Rust now matches all 31,237 original Python checks" in value["svg"]
                and b"All 31,237 original checks passed" in value["svg"],
                "never suppress a complete observed original Rust PASS")
    else:
        require(b"differences remain" in value["svg"],
                "never suppress an actual original candidate failure")
    require(b"141,557,760" not in value["svg"]
            and b"141557760" not in value["inputs"]
            and b"141557760" not in value["summary"],
            "never repeat the retired proposal in the current graph")
    require(b"226,492,416" not in value["svg"]
            and b"226492416" not in value["inputs"]
            and b"226492416" not in value["summary"],
            "never inspect or assert successor proposal details in a correctness graph")


def different(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " CHANGED"
    if type(value) is list:
        return value + ["CHANGED"]
    if type(value) is dict:
        return {**value, "__v103_hostile": True}
    if value is None:
        return "CHANGED"
    raise Rejected("unsupported adversarial public JSON value")


def self_test(context: dict, result: dict, own_sha: str, own_size: int,
              wall: SourceWall) -> int:
    checks = []

    def reject_context(label: str, change) -> None:
        hostile = copy.deepcopy(context)
        change(hostile)
        try:
            verify(hostile)
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            checks.append(label)
            return
        raise Rejected("hostile public correctness evidence was accepted: " + label)

    for name in ("previous_inputs", "previous_summary", "contract",
                 "historical_receipt", "audit", "receipt"):
        for key in sorted(context[name]):
            reject_context(
                name + " changed " + key,
                lambda candidate, owner=name, field=key:
                    candidate[owner].__setitem__(field,
                                                 different(candidate[owner][field])),
            )
    for index in range(len(SUITES)):
        reject_context(
            f"actual original suite {index} omitted",
            lambda candidate, position=index:
                candidate["receipt"]["suite_integrity"].pop(position),
        )
        reject_context(
            f"previous Rust failure suite {index} omitted",
            lambda candidate, position=index:
                candidate["historical_receipt"]["suite_integrity"].pop(position),
        )
        reject_context(
            f"historical C suite {index} omitted",
            lambda candidate, position=index:
                candidate["previous_summary"]["c_v12_suite_outcomes"].pop(position),
        )
        for key in ("suite", "case_execution_denominator", "fully_observed",
                    "actual_worker_started", "mismatch_count",
                    "verified_passing_case_count"):
            reject_context(
                f"actual original suite {index} changed {key}",
                lambda candidate, position=index, field=key:
                    candidate["receipt"]["suite_integrity"][position].__setitem__(
                        field,
                        different(candidate["receipt"]["suite_integrity"][position][field]),
                    ),
            )

    def reject_output(label: str, name: str, change) -> None:
        hostile = dict(result)
        payload = document(hostile[name], "hostile generated V103 graph")
        change(payload)
        hostile[name] = canonical(payload)
        try:
            verify_outputs(context, hostile, own_sha, own_size)
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            checks.append(label)
            return
        raise Rejected("hostile V103 graph output was accepted: " + label)

    for name in ("inputs", "summary"):
        for key, value in (
            ("original_case_execution_denominator", DENOMINATOR + SUPPLEMENTAL),
            ("qualified_candidate_count", 1),
            ("runtime_no_delegation", "ESTABLISHED"),
            ("performance", "1.5x"),
            ("memory", "42 bytes"),
            ("timing_trials_run", 1),
            ("holdout_proposal_files_opened_by_graph", 1),
            ("holdout_cases_opened_by_graph", 1),
            ("hidden_cases_read_by_graph", 1),
            ("final_holdout_opened", True),
            ("winner_selected", True),
        ):
            reject_output(
                name + " dishonestly changed " + key,
                name,
                lambda document, field=key, replacement=value:
                    document.__setitem__(field, replacement),
            )
    for key, value in (("candidate_qualified", True),
                       ("semantic_mismatch_count", -1),
                       ("verified_passing_case_count", DENOMINATOR + 1)):
        reject_output(
            "summary fabricated " + key,
            "summary",
            lambda document, field=key, replacement=value:
                document.__setitem__(field, replacement),
        )

    def reject_wall(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            checks.append(label)
            return
        raise Rejected("hostile source-only graph effect was accepted: " + label)

    for label, relative in (
        ("canonical Rust adapter", "candidates/rust_candidate.py"),
        ("canonical Rust engine", "candidates/rust/src/lib.rs"),
        ("canonical Rust bridge", "candidates/rust/py_bridge.c"),
        ("installed native engine", "candidates/_rust_engine.so"),
        ("compressed actual observations", "oracle/phase2/evidence/observations.json.gz"),
        ("retired public proposal", "oracle/phase3/expanded-sealed-holdout-v2.json"),
        ("successor public proposal", "oracle/phase3/expanded-sealed-holdout-v3.json"),
        ("future secret seed", "oracle/phase3/final-holdout.seed"),
        ("future hidden cases", "oracle/phase3/final-hidden-cases.json"),
        ("private native build root", "/tmp/rebar-phase2-native-build-v9-rust-hc4z0w7m"),
    ):
        absolute = relative if relative.startswith("/") else os.path.join(ROOT, relative)
        reject_wall(label, "open", (absolute, None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("source-only output creation", "open",
                (os.path.join(ROOT, OUTPUT + ".svg"), None,
                 os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW))
    reject_wall("candidate process", "subprocess.Popen", (PYTHON,))
    reject_wall("native matcher load", "ctypes.dlopen", ("_rust_engine.so",))
    reject_wall("matching import", "import", ("re",))
    reject_wall("candidate import", "import", ("candidates.rust_candidate",))
    reject_wall("compressed archive import", "import", ("gzip",))
    reject_wall("timing sample", "time.perf_counter", ())
    reject_wall("network connection", "socket.connect", ("example.invalid",))
    reject_wall("thread start", "_thread.start_new_thread", ())
    reject_wall("destructive rename", "os.rename", ("old", "new"))
    reject_wall("nofollow owner omitted", "open",
                (os.path.join(ROOT, AUDIT[0]), None, os.O_RDONLY))
    verify_outputs(context, result, own_sha, own_size)
    require(len(checks) >= 250,
            "require comprehensive immutable evidence and physical-wall hostile controls")
    return len(checks)


def write_exclusively(path: str, payload: bytes) -> None:
    descriptor = os.open(
        os.path.join(ROOT, path),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
        0o600,
    )
    try:
        offset = 0
        while offset < len(payload):
            count = os.write(descriptor, payload[offset:])
            require(count > 0, "exclusive graph publication was interrupted")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for name in ("source", "inputs", "summary", "svg"):
        parser.add_argument("--previous-" + name + "-sha256", required=True)
    for name in ("source", "protocol", "contract"):
        parser.add_argument("--v26-" + name + "-sha256", required=True)
    parser.add_argument("--v26-receipt-path", required=True)
    parser.add_argument("--v26-receipt-sha256", required=True)
    parser.add_argument("--v26-receipt-bytes", required=True, type=int)
    parser.add_argument("--v25-receipt-sha256", required=True)
    parser.add_argument("--nondelegation-receipt-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "use only isolated, no-site, bytecode-disabled pinned CPython 3.14.6")
    own_sha = pin(options.source_sha256, "V103 graph renderer")
    require(type(options.source_bytes) is int and 1 <= options.source_bytes <= 262_144,
            "independently pin the complete V103 graph renderer bytes")
    for name, owner in PREVIOUS.items():
        require(getattr(options, "previous_" + name + "_sha256") == owner[1],
                "immutable previous V101 public owner digest changed: " + name)
    for name, owner in CAMPAIGN.items():
        require(getattr(options, "v26_" + name + "_sha256") == owner[1],
                "frozen V26 public campaign owner digest changed: " + name)
    require(options.v25_receipt_sha256 == V25_RECEIPT[1],
            "the actual previous Rust FAIL-1352 receipt changed")
    require(options.nondelegation_receipt_sha256 == AUDIT[1],
            "the separate historical non-delegation failure receipt changed")
    receipt_owner = exact_receipt(
        options.v26_receipt_path, options.v26_receipt_sha256,
        options.v26_receipt_bytes,
    )
    wall = SourceWall(receipt_owner, options.render)
    sys.addaudithook(wall.check)
    allowed = specifications(receipt_owner)
    source_owner = (SELF, own_sha, options.source_bytes)
    own_source = read_owner(source_owner, (*allowed, source_owner))
    previous = {name: read_owner(owner, allowed)
                for name, owner in PREVIOUS.items()}
    campaign = {name: read_owner(owner, allowed)
                for name, owner in CAMPAIGN.items()}
    context = {
        "goal": read_owner(GOAL, allowed),
        "previous_inputs": document(previous["inputs"], "immutable V101 inputs"),
        "previous_summary": document(previous["summary"], "immutable V101 summary"),
        "previous_svg": previous["svg"],
        "contract": document(campaign["contract"], "frozen V26 contract"),
        "historical_receipt": document(read_owner(V25_RECEIPT, allowed),
                                       "actual prior Rust FAIL-1352 receipt"),
        "audit": document(read_owner(AUDIT, allowed), "historical static audit"),
        "receipt_owner": receipt_owner,
        "receipt": document(read_owner(receipt_owner, allowed),
                            "actual published complete original Rust outcome"),
    }
    verify(context)
    output = assets(context, own_sha, len(own_source))
    verify_outputs(context, output, own_sha, len(own_source))
    hostile = (self_test(context, output, own_sha, len(own_source), wall)
               if options.self_test else 0)
    if options.render:
        for name, suffix in (("svg", ".svg"),
                             ("inputs", ".inputs.json"),
                             ("summary", ".json")):
            write_exclusively(OUTPUT + suffix, output[name])
    result = context["receipt"]
    report = {
        "status": "PASS",
        "mode": ("self-test" if options.self_test else
                 "render" if options.render else "verify-frozen-context"),
        "source_sha256": own_sha,
        "source_bytes": len(own_source),
        "hostile_control_count": hostile,
        "candidate_status": result["candidate_status"],
        "candidate_original_oracle_pass": result["candidate_original_oracle_pass"],
        "original_suite_correctness_qualified":
            result["original_suite_correctness_qualified"],
        "candidate_qualified": False,
        "original_case_execution_denominator": DENOMINATOR,
        "verified_passing_case_count": result["verified_passing_case_count"],
        "semantic_mismatch_count": result["semantic_mismatch_count"],
        "distinct_candidate_worker_count": len(SUITES),
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_source_owners_opened": 0,
        "candidate_workers_started": 0,
        "native_binary_files_opened": 0,
        "compressed_archives_opened": 0,
        "holdout_proposal_files_opened": 0,
        "holdout_proposal_files_statted": 0,
        "seed_files_opened": 0,
        "hidden_cases_read": 0,
        "holdout_cases_opened": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "winner_selected": False,
    }
    if options.render:
        report.update({
            name + "_sha256": sha256(value)
            for name, value in output.items()
        })
    print(json.dumps(report, ensure_ascii=True, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Rejected, ValueError, TypeError, OSError) as failure:
        print("REJECTED: " + str(failure), file=sys.stderr)
        raise SystemExit(1)
