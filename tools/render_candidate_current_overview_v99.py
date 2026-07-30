#!/usr/bin/env python3
"""Render the authenticated C12 improvement without measuring speed or holdout."""

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
SELF = "tools/render_candidate_current_overview_v99.py"
OUTPUT = "docs/evidence/candidate-current-overview-v99"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
DENOMINATOR = 31237
SUPPLEMENTAL = 8244
HOLDOUT_PROPOSAL = 14155776
UNMEASURED = "NOT MEASURED"
PREVIOUS = {
    "source": ("tools/render_candidate_current_overview_v98.py", "39c7d058e0462f614ff81e9240f9c19690b8b43582a75a0fe80b460ba85a21ac", 121628),
    "inputs": ("docs/evidence/candidate-current-overview-v98.inputs.json", "e8dbcf9271fc39690739f6d93b1832181a0125abf65bd7ce14d6fb3fe248e102", 30861),
    "summary": ("docs/evidence/candidate-current-overview-v98.summary.json", "5eb2cb4146c608a0c2593d5fd7056bf5aa822ca6cbe4e7f70c972b62b4ed96d6", 4185586),
    "svg": ("docs/evidence/candidate-current-overview-v98.svg", "937c8cd420dbafdc7906d749288e1b56ed376617e6304c8fa61ce364acb87fa0", 10452),
}
C12 = {
    "source": ("tools/run_owned_repaired_c_original_campaign_v12.py", "80af52f1df9c2787df858afef4addb1597fb87845225554d258f4c9173dabb17", 78137),
    "protocol": ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V12.md", "6f7c81007f78eb6435204521548f238b531d6bcb9f517f1c35e395e0e2b82344", 7712),
    "contract": ("oracle/phase2/repaired-c-original-campaign-v12.json", "758578965291c0b8cf251d7ec46267de7400935e30d4388a126c22821b85090b", 76691),
    "receipt": (
        "oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-"
        "c-original-match-semantics-original-p0-v12-failures-publication-receipt.json",
        "a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b",
        10943,
    ),
}
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864), ("scanner_v3", 1024),
    ("buffer_v3", 768), ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)
MISMATCHES = {"managed_v1": 16, "public_types_v1": 248,
              "substitution_v2": 224, "public_surface_v19": 114, "pep688_v4": 4}
CHUNKS = {"managed_v1": 1, "public_types_v1": 8,
          "substitution_v2": 7, "public_surface_v19": 4, "pep688_v4": 1}
ZERO_VECTOR = "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
VECTOR_DIGESTS = {
    "managed_v1": "3488267b9c2a5aff58a0917adb142d26d482526536b71ceb8e3a39e5d5ed4352",
    "public_types_v1": "b278976e7d01f2c56359bcdc442fefa1ee6cef899275f1cf5ef00de2fd7e2eff",
    "substitution_v2": "2ba4b132a4f84ba43fb1a87b1b5c0ab2c8cceffc8f5937bebc285af9da11044a",
    "public_surface_v19": "443312e6ef63ea99dcf0553ec2e251a40f7221f75697139d85c52084cd0fee22",
    "pep688_v4": "9377c56ba63c694fd0ce4839ad802cbc1e821ce708c4fbde5f5d7c8d7e5c26cc",
}
PREVIOUS_C_RECEIPT = "3db5daf9352f5c9837f4f7134bead6c0a05b2bddf9815a9cf134ea953b0ecd3e"
REFERENCE_VECTOR = "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
ARCHIVE_SHA256 = "f6f68b5c7222f47734515e8570a048e2f449623f6fcbc99493abff4babb0c1a1"


class Rejected(ValueError):
    """A frozen owner or its authenticated public claim was altered."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def owner(relative: str, expected_sha256: str, expected_size: int) -> bytes:
    """Read precisely one permitted, private, regular, digest-bound owner."""
    allowed = {"GOAL.md", SELF}
    allowed.update(spec[0] for spec in PREVIOUS.values())
    allowed.update(spec[0] for spec in C12.values())
    require(relative in allowed, "owner outside the public frozen allowlist")
    descriptor = os.open(os.path.join(ROOT, relative), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode), "owner must be a regular file")
        require(stat.S_IMODE(metadata.st_mode) == 0o600, "owner must be private")
        require(metadata.st_nlink == 1, "owner must have exactly one hard link")
        require(metadata.st_uid == os.getuid(), "owner must belong to this user")
        require(metadata.st_size == expected_size, "owner size does not match its pin")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    data = b"".join(chunks)
    require(len(data) == expected_size and sha256(data) == expected_sha256,
            "complete owner digest does not match its pin")
    return data


def parsed(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data)
    except (UnicodeError, ValueError) as failure:
        raise Rejected(f"invalid authenticated JSON: {label}") from failure
    require(type(value) is dict, f"authenticated JSON must be an object: {label}")
    return value


def same(mapping: dict, expected: dict, label: str) -> None:
    for key, value in expected.items():
        require(mapping.get(key) == value, f"{label}: unexpected {key}")


def verify_previous(inputs: dict, summary: dict, previous_svg: bytes) -> None:
    shared = {
        "version": 98, "python": "3.14.6", "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": 13, "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "performance": UNMEASURED, "memory": UNMEASURED, "timing_trials_run": 0,
        "winner_selected": False, "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED", "final_holdout_opened": False,
        "hidden_cases_read_by_graph": 0, "compressed_archives_opened_by_graph": 0,
        "c_v11_original_campaign_candidate_status": "FAIL",
        "c_v11_original_campaign_candidate_qualified": False,
        "c_v11_original_campaign_verified_passing_case_count": 16262,
        "c_v11_original_campaign_completed_suite_count": 11,
        "c_v11_original_campaign_distinct_worker_count": 13,
        "c_v11_original_campaign_candidate_execution_failure_count": 2,
        "c_v11_original_campaign_complete_observed_individual_mismatch_record_count": 606,
        "c_v11_original_campaign_complete_observed_mismatch_chunk_count": 21,
        "c_v11_all_observed_individual_mismatch_records_preserved": True,
        "authenticated_evidence_owner_lower_bound": 348,
        "authenticated_history_reference_lower_bound": 353,
    }
    same(inputs, shared, "previous inputs")
    same(summary, shared, "previous summary")
    same(inputs, {"schema": "rebar-candidate-current-overview-v98-inputs"}, "previous inputs")
    same(summary, {"schema": "rebar-candidate-current-overview-v98-summary", "status": "PASS"},
         "previous summary")
    require(inputs.get("headline") == summary.get("headline"), "previous headlines differ")
    require(inputs.get("snapshot") == summary.get("snapshot"), "previous snapshots differ")
    require(inputs.get("previous_overview") == summary.get("previous_overview"),
            "previous history references differ")
    previous_history = inputs.get("previous_overview")
    require(type(previous_history) is dict and set(previous_history) == set(PREVIOUS),
            "previous complete history is not represented by four owners")
    for reference in previous_history.values():
        require(type(reference) is dict and set(reference) == {"bytes", "path", "sha256"},
                "previous historical owner is not complete")
    source_path, source_digest, source_size = PREVIOUS["source"]
    same(inputs.get("renderer", {}),
         {"path": source_path, "sha256": source_digest, "bytes": source_size},
         "previous renderer")
    headline = inputs.get("headline", {})
    same(headline, {
        "original_python_check_count": DENOMINATOR,
        "c_current_verified_original_checks": 16262,
        "rust_current_verified_original_checks": 14725,
        "zig_corrected_matching": UNMEASURED,
        "speed_relative_to_python": UNMEASURED,
        "performance": UNMEASURED,
        "fully_compatible_candidate_count": 0,
        "winner_selected": False,
    }, "previous headline")
    same(headline.get("verified_original_checks_by_candidate", {}),
         {"c": 16262, "rust": 14725, "zig": 4607}, "previous candidate counts")
    same(summary.get("snapshot", {}), {
        "version": 98,
        "c_v11_original_campaign_verified_passing_case_count": 16262,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
    }, "previous snapshot")
    require(previous_svg.startswith(b"<svg ") and b"NOT MEASURED" in previous_svg,
            "previous graphic is not the frozen accessible correctness graphic")


def verify_contract(contract: dict) -> None:
    same(contract, {
        "schema": "rebar-owned-repaired-c-original-campaign-v12-source-freeze",
        "version": 12, "family": "c", "goal_sha256": GOAL_SHA256,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED", "holdout": "NOT OPENED",
        "qualified_candidate_count": 0, "candidate_correctness": UNMEASURED,
        "candidate_qualification": "NOT ESTABLISHED", "winner_selected": False,
    }, "C12 contract")
    same(contract.get("pinned_cpython", {}),
         {"path": PYTHON, "version": "3.14.6", "required_flags": ["-I", "-B", "-S"]},
         "C12 pinned interpreter")
    for name in ("source", "protocol"):
        relative, digest, size = C12[name]
        same(contract.get(name, {}), {"path": relative, "sha256": digest, "bytes": size},
             f"C12 contract {name}")
    effects = contract.get("source_only_effects")
    require(type(effects) is dict and effects and all(value == 0 for value in effects.values()),
            "C12 source-only contract records a side effect")
    same(contract.get("expanded_holdout", {}), {
        "case_status": "NOT GENERATED; NOT OPENED", "final_protocol_status": "NOT FROZEN",
        "proposed_case_count": HOLDOUT_PROPOSAL, "source_mode_holdout_files_read": 0,
    }, "C12 holdout proposal")
    original = contract.get("lossless_original_public_case_evidence_v12", {})
    same(original, {
        "source_method_count": 165, "public_record_count": 152,
        "case_execution_denominator": 151, "named_private_waiver_count": 13,
        "authentic_debug_skip_count": 1, "actual_candidate_digest_forced_to_reference": False,
        "normalization_before_original_comparison": False,
        "original_reference_records_sha256": REFERENCE_VECTOR,
        "performance": UNMEASURED, "candidate_correctness": UNMEASURED,
    }, "C12 source-owned original counts")
    require(len(original.get("named_private_waivers", [])) == 13,
            "C12 named private waivers were not individually preserved")
    historical = contract.get("preserved_actual_c_v11_campaign", {})
    same(historical, {
        "candidate_status": "FAIL", "candidate_qualified": False,
        "case_execution_denominator": DENOMINATOR, "verified_passing_case_count": 16262,
        "completed_suite_count": 11, "actual_candidate_workers": 13,
        "candidate_execution_failure_count": 2,
        "complete_observed_semantic_mismatch_record_count": 606,
        "complete_mismatch_chunk_count": 21,
        "all_observed_semantic_mismatch_records_preserved": True,
    }, "C12 preserved C11 campaign")
    same(historical.get("actual_failure_receipt", {}),
         {"sha256": PREVIOUS_C_RECEIPT}, "C12 preserved C11 receipt")


def verify_receipt(receipt: dict) -> None:
    same(receipt, {
        "schema": "rebar-owned-repaired-c-original-campaign-v12-durable-publication-receipt",
        "version": 12, "family": "c", "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "case_execution_denominator": DENOMINATOR, "suite_count": 13,
        "attempted_suite_count": 13, "completed_suite_count": 12,
        "verified_passing_case_count": 16413, "actual_candidate_workers": 13,
        "actual_worker_process_ids_are_distinct": True,
        "candidate_execution_failure_count": 1, "infrastructure_failure_count": 0,
        "worker_timeout_count": 0, "observed_semantic_mismatch_lower_bound": 606,
        "complete_observed_semantic_mismatch_record_count": 606,
        "complete_mismatch_chunk_count": 21, "complete_mismatch_suite_count": 12,
        "all_observed_semantic_mismatch_records_preserved": True,
        "complete_original_case_records_preserved": True,
        "complete_original_source_method_count": 165,
        "complete_original_public_record_count": 152,
        "complete_original_executed_case_count": 151,
        "complete_original_case_vector_sha256": REFERENCE_VECTOR,
        "named_private_waiver_count": 13,
        "source_sha256": C12["source"][1], "protocol_sha256": C12["protocol"][1],
        "contract_sha256": C12["contract"][1],
        "preserved_actual_v11_failure_receipt_sha256": PREVIOUS_C_RECEIPT,
        "separate_reference_case_count": SUPPLEMENTAL,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "semantic_mismatch_count": UNMEASURED, "performance": UNMEASURED,
        "memory": UNMEASURED, "undefined_behavior": UNMEASURED,
        "clock_samples": 0, "timing_trials_run": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "holdout": "NOT OPENED", "winner_selected": False,
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL,
        "counterexample_preview_only": False,
        "counterexample_normalization_before_original_comparison": False,
        "original_source_targets_modified": 0,
    }, "C12 public publication receipt")
    workers = receipt.get("actual_worker_process_ids")
    require(type(workers) is list and len(workers) == 13 and len(set(workers)) == 13,
            "C12 did not use exactly 13 distinct real workers")
    archive = receipt.get("archive", {})
    same(archive, {
        "sha256": ARCHIVE_SHA256, "bytes": 211493, "mode": "0600", "nlink": 1,
        "exclusive_creation": True, "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "path": "oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-"
                "c-original-match-semantics-original-p0-v12-failures.json.gz",
    }, "C12 unopened archive metadata")
    outcomes = receipt.get("suite_outcomes")
    require(type(outcomes) is list and len(outcomes) == 13, "C12 must publish 13 suite outcomes")
    for outcome, (suite, denominator) in zip(outcomes, SUITES, strict=True):
        same(outcome, {"suite": suite, "case_execution_denominator": denominator,
                       "actual_candidate_workers": 1}, "C12 suite outcome")
        require(outcome.get("worker_process_id") in workers, "C12 suite used an unknown worker")
        if suite == "subinterpreter_v2":
            same(outcome, {"status": "FAIL", "failure_class": "CANDIDATE EXECUTION FAILURE",
                           "mismatch_count": UNMEASURED}, "C12 genuine lifecycle failure")
        elif suite in MISMATCHES:
            same(outcome, {"status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
                           "mismatch_count": MISMATCHES[suite]}, "C12 mismatch outcome")
        else:
            same(outcome, {"status": "PASS", "failure_class": "PASS", "mismatch_count": 0},
                 "C12 passing outcome")
    vectors = receipt.get("complete_mismatch_suite_vector_fingerprints")
    require(type(vectors) is list and len(vectors) == 12,
            "C12 must preserve exactly 12 complete source-ordered suite vectors")
    completed = [suite for suite in SUITES if suite[0] != "subinterpreter_v2"]
    for vector, (suite, denominator) in zip(vectors, completed, strict=True):
        same(vector, {
            "suite": suite, "case_execution_denominator": denominator,
            "all_observed_records_preserved": True,
            "complete_record_count": MISMATCHES.get(suite, 0),
            "complete_chunk_count": CHUNKS.get(suite, 0),
            "complete_vector_sha256": VECTOR_DIGESTS.get(suite, ZERO_VECTOR),
        }, "C12 complete preserved mismatch vector")
    require(sum(vector["complete_record_count"] for vector in vectors) == 606,
            "C12 lost an observed mismatch record")
    require(sum(vector["complete_chunk_count"] for vector in vectors) == 21,
            "C12 lost an observed mismatch chunk")


def verify_context(context: dict) -> None:
    require(context["goal"].startswith(b"/goal ") and sha256(context["goal"]) == GOAL_SHA256,
            "immutable GOAL.md does not match the frozen experiment")
    verify_previous(context["previous_inputs"], context["previous_summary"],
                    context["previous_svg"])
    verify_contract(context["contract"])
    verify_receipt(context["receipt"])
    require(context["previous_summary"]["c_v11_original_campaign_verified_passing_case_count"]
            + 151 == context["receipt"]["verified_passing_case_count"],
            "C12 improvement must be exactly 151 original correctness cases")


def owner_reference(spec: tuple[str, str, int]) -> dict:
    relative, digest, size = spec
    return {"path": relative, "sha256": digest, "bytes": size}


def svg_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def render_svg() -> bytes:
    rows = (
        ("Python re", DENOMINATOR, "All 13 original groups passed", "BASELINE", "#34d399"),
        ("C", 16413, "7 passed; 5 differ; 1 genuine execution failure", "NOT YET COMPATIBLE", "#fbbf24"),
        ("Rust", 14725, "Earlier measured correctness; 1 incomplete original group", "NOT YET COMPATIBLE", "#fb7185"),
        ("Zig", 4607, "Earlier measured correctness; newer matching not measured", "NOT YET COMPATIBLE", "#fbbf24"),
        ("C++", None, "Full current matching result not measured", UNMEASURED, "#94a3b8"),
        ("Go", None, "Full current matching result not measured", UNMEASURED, "#94a3b8"),
        ("Fortran", None, "Full current matching result not measured", UNMEASURED, "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="970" '
        'viewBox="0 0 1440 970" role="img" aria-labelledby="title description">',
        '<title id="title">Original Python regular-expression correctness; speed not measured</title>',
        '<desc id="description">C failed after verifying 16,413 of 31,237 original checks, '
        'an increase of 151. Twelve of thirteen suites completed using thirteen distinct workers. '
        'All 606 observed mismatch records are preserved in 21 chunks. Rust verified 14,725 checks '
        'and Zig verified 4,607 checks. These bars measure correctness, never speed. Performance, '
        'memory, and holdout are not measured; no candidate qualifies and no winner is selected.</desc>',
        '<rect width="1440" height="970" rx="24" fill="#0b1220"/>',
        '<text x="50" y="68" fill="#f8fafc" font-size="32" font-family="system-ui,sans-serif" '
        'font-weight="740">Building a faster Python re, from scratch</text>',
        '<text x="51" y="105" fill="#cbd5e1" font-size="17" font-family="system-ui,sans-serif">'
        'C improved by 151 original checks; compatibility is incomplete; speed is not measured</text>',
        '<rect x="46" y="129" width="1348" height="76" rx="12" fill="#172338"/>',
        '<text x="67" y="159" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" '
        'font-weight="680">Bars show verified original correctness checks, not speed.</text>',
        '<text x="67" y="185" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        'The fixed denominator is 31,237; supplemental checks are separate.</text>',
        '<text x="55" y="248" fill="#94a3b8" font-size="12">APPROACH</text>',
        '<text x="171" y="248" fill="#94a3b8" font-size="12">VERIFIED ORIGINAL CHECKS</text>',
        '<text x="691" y="248" fill="#94a3b8" font-size="12">ACTUAL OUTCOME</text>',
        '<text x="1220" y="248" fill="#94a3b8" font-size="12">SPEED</text>',
    ]
    for index, (name, count, detail, result, color) in enumerate(rows):
        y = 300 + index * 70
        parts.append(f'<text x="55" y="{y}" fill="#f8fafc" font-size="16" '
                     f'font-family="system-ui,sans-serif">{svg_escape(name)}</text>')
        parts.append(f'<rect x="170" y="{y - 17}" width="306" height="20" '
                     'rx="6" fill="#1e293b"/>')
        if count is None:
            label = UNMEASURED
        else:
            width = round(306 * count / DENOMINATOR)
            parts.append(f'<rect x="170" y="{y - 17}" width="{width}" height="20" '
                         f'rx="6" fill="{color}"/>')
            percentage = "100%" if count == DENOMINATOR else f"{100 * count / DENOMINATOR:.1f}%"
            label = f"{count:,} / {DENOMINATOR:,} ({percentage})"
        parts.append(f'<text x="487" y="{y}" fill="#e2e8f0" font-size="12" '
                     f'font-family="system-ui,sans-serif">{svg_escape(label)}</text>')
        parts.append(f'<text x="691" y="{y}" fill="#cbd5e1" font-size="11" '
                     f'font-family="system-ui,sans-serif">{svg_escape(detail)}</text>')
        parts.append(f'<text x="1220" y="{y}" fill="#94a3b8" font-size="11" '
                     f'font-family="system-ui,sans-serif">{UNMEASURED}</text>')
        parts.append(f'<text x="1387" y="{y + 19}" text-anchor="end" fill="{color}" '
                     f'font-size="10" font-family="system-ui,sans-serif">{svg_escape(result)}</text>')
    notes = (
        "Actual C12 candidate status: FAIL; 12 completed suites; 13 distinct workers; 1 execution failure.",
        "All 606 observed mismatch records and all 21 chunks are preserved; total mismatch count is NOT MEASURED.",
        "Original source counts remain distinct: 165 source methods; 152 public records; 151 executed cases.",
        "Earlier C11: 16,262 verified checks. Current C12: 16,413 verified checks (+151).",
        "Holdout: NOT FROZEN, NOT GENERATED, NOT OPENED. Speed and memory: NOT MEASURED.",
        "No fully compatible candidate; runtime independence not established; no winner.",
    )
    parts.append('<line x1="48" y1="785" x2="1390" y2="785" stroke="#334155"/>')
    for index, note in enumerate(notes):
        parts.append(f'<text x="53" y="{812 + 24 * index}" fill="#cbd5e1" font-size="12" '
                     f'font-family="system-ui,sans-serif">{svg_escape(note)}</text>')
    parts.append("</svg>")
    return ("\n".join(parts) + "\n").encode("utf-8")


def build_assets(context: dict, source_digest: str, source_size: int) -> dict[str, bytes]:
    receipt = context["receipt"]
    previous = {name: owner_reference(spec) for name, spec in PREVIOUS.items()}
    current_evidence = {name: owner_reference(spec) for name, spec in C12.items()}
    headline = {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "python_version": "3.14.6", "bars_measure": "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED",
        "original_python_check_count": DENOMINATOR, "original_python_suite_count": 13,
        "separate_additional_differential_check_count": SUPPLEMENTAL,
        "separate_additional_checks_in_original_denominator": False,
        "verified_original_checks_by_candidate": {
            "c": 16413, "rust": 14725, "zig": 4607,
            "cpp": UNMEASURED, "go": UNMEASURED, "fortran": UNMEASURED,
        },
        "c_current_verified_original_checks": 16413,
        "c_previous_verified_original_checks": 16262,
        "c_verified_check_change_from_previous_graph": 151,
        "c_current_candidate_worker_count": 13,
        "c_current_distinct_candidate_worker_count": 13,
        "c_current_completed_original_suite_count": 12,
        "c_candidate_execution_failure_count": 1,
        "c_current_complete_observed_individual_mismatch_records": 606,
        "c_current_complete_observed_mismatch_chunks": 21,
        "c_current_complete_observed_mismatch_vector_count": 12,
        "c_current_observed_individual_records_preserved": True,
        "c_observed_mismatch_lower_bound": 606,
        "c_complete_mismatch_total": UNMEASURED,
        "c_infrastructure_failure_count": 0, "c_worker_timeout_count": 0,
        "c_original_source_method_count": 165,
        "c_original_public_record_count": 152,
        "c_original_executed_case_count": 151,
        "rust_current_verified_original_checks": 14725,
        "zig_current_verified_original_checks": 4607,
        "independent_first_party_candidate_family_count": 6,
        "fully_compatible_candidate_count": 0,
        "performance": UNMEASURED, "speed_relative_to_python": UNMEASURED,
        "memory": UNMEASURED,
        "proposed_final_comparison_case_count": HOLDOUT_PROPOSAL,
        "proposed_final_comparison_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "winner_selected": False,
        "public_reporting_integrity": "ALL 606 OBSERVED C12 RECORDS PRESERVED; HISTORICAL C10 COMPLETENESS NOT ESTABLISHED BY THIS GRAPH",
    }
    snapshot = {
        "schema": "rebar-candidate-current-overview-v99-compact-current-snapshot", "version": 99,
        "actual_current_graph_predecessor_version": 98,
        "goal_sha256": GOAL_SHA256, "original_case_execution_denominator": DENOMINATOR,
        "original_suite_count": 13, "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": 13,
        "c_v12_original_campaign_candidate_status": "FAIL",
        "c_v12_original_campaign_candidate_qualified": False,
        "c_v12_original_campaign_verified_passing_case_count": 16413,
        "c_v12_original_campaign_previous_verified_passing_case_count": 16262,
        "c_v12_verified_passing_case_increase_from_v98": 151,
        "c_v12_original_campaign_attempted_suite_count": 13,
        "c_v12_original_campaign_completed_suite_count": 12,
        "c_v12_original_campaign_actual_worker_count": 13,
        "c_v12_original_campaign_distinct_worker_count": 13,
        "c_v12_original_campaign_candidate_execution_failure_count": 1,
        "c_v12_original_campaign_infrastructure_failure_count": 0,
        "c_v12_original_campaign_worker_timeout_count": 0,
        "c_v12_original_campaign_complete_observed_individual_mismatch_record_count": 606,
        "c_v12_original_campaign_complete_observed_mismatch_chunk_count": 21,
        "c_v12_original_campaign_complete_observed_mismatch_vector_count": 12,
        "c_v12_all_observed_individual_mismatch_records_preserved": True,
        "c_v12_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v12_original_campaign_semantic_mismatch_count": UNMEASURED,
        "c_v12_complete_original_source_method_count": 165,
        "c_v12_complete_original_public_record_count": 152,
        "c_v12_complete_original_executed_case_count": 151,
        "c_v11_original_campaign_verified_passing_case_count": 16262,
        "c_v11_original_campaign_candidate_status": "FAIL",
        "c_v11_original_campaign_completed_suite_count": 11,
        "c_v11_original_campaign_candidate_execution_failure_count": 2,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
        "authenticated_evidence_owner_lower_bound": 352,
        "authenticated_history_reference_lower_bound": 357,
        "v99_new_directly_authenticated_evidence_owner_count": 4,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED", "timing_trials_run": 0,
        "qualified_candidate_count": 0, "winner_selected": False,
    }
    inputs = {
        "schema": "rebar-candidate-current-overview-v99-inputs", "version": 99,
        "actual_current_graph_predecessor_version": 98,
        "goal_sha256": GOAL_SHA256, "python": "3.14.6",
        "original_case_execution_denominator": DENOMINATOR, "original_suite_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": 13,
        "previous_overview": previous,
        "preserved_complete_history": "EXACT DIGEST-BOUND PREVIOUS SOURCE, INPUTS, SUMMARY, AND SVG; NEVER COPIED OR TRUNCATED",
        "c_v12_public_evidence": current_evidence,
        "renderer": {"path": SELF, "sha256": source_digest, "bytes": source_size},
        "headline": headline, "snapshot": snapshot,
        "complete_original_suites": [
            {"suite": suite, "case_execution_denominator": denominator}
            for suite, denominator in SUITES
        ],
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0, "clock_samples_by_graph": 0,
        "final_holdout_opened": False,
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL,
        "performance": UNMEASURED, "memory": UNMEASURED,
        "runtime_no_delegation": "NOT ESTABLISHED", "timing_trials_run": 0,
        "qualified_candidate_count": 0, "winner_selected": False,
        "authenticated_evidence_owner_lower_bound": 352,
        "authenticated_history_reference_lower_bound": 357,
        "v99_new_directly_authenticated_evidence_owner_count": 4,
    }
    summary = dict(inputs)
    summary.update({
        "schema": "rebar-candidate-current-overview-v99-summary", "status": "PASS",
        "status_scope": "AUTHENTICATED CORRECTNESS GRAPH ONLY; C12 CANDIDATE FAILED; SPEED NOT MEASURED",
        "c_v12_publication_status": receipt["publication_status"],
        "c_v12_publication_pass_means": receipt["publication_pass_means"],
        "c_v12_candidate_status": receipt["candidate_status"],
        "c_v12_candidate_qualified": receipt["candidate_qualified"],
        "c_v12_suite_outcomes": receipt["suite_outcomes"],
        "c_v12_complete_mismatch_suite_vector_fingerprints":
            receipt["complete_mismatch_suite_vector_fingerprints"],
        "c_v12_unopened_archive_metadata": {
            "path": receipt["archive"]["path"], "sha256": receipt["archive"]["sha256"],
            "bytes": receipt["archive"]["bytes"], "opened_by_graph": False,
            "statted_by_graph": False,
        },
        "previous_complete_overview_sha256": PREVIOUS["summary"][1],
        "previous_complete_overview_bytes": PREVIOUS["summary"][2],
        "historical_c10_audit_evidence_status":
            "EARLIER RECORDED AUDIT ONLY; NOT INDEPENDENTLY ESTABLISHED BY THIS GRAPH",
        "historical_c10_records_independently_established_by_graph": False,
        "historical_c10_records_repaired": False,
    })
    encode = lambda value: (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return {"inputs": encode(inputs), "summary": encode(summary), "svg": render_svg()}


def mutation_controls(context: dict, source_digest: str, source_size: int) -> int:
    controls = []

    def reject(label: str, mutate) -> None:
        hostile = copy.deepcopy(context)
        mutate(hostile)
        try:
            verify_context(hostile)
        except (Rejected, KeyError, TypeError):
            controls.append(label)
            return
        raise Rejected(f"hostile control accepted: {label}")

    reject("goal edited", lambda x: x.__setitem__("goal", x["goal"] + b"!"))
    reject("previous denominator changed", lambda x: x["previous_inputs"].__setitem__(
        "original_case_execution_denominator", DENOMINATOR + 1))
    reject("previous history removed", lambda x: x["previous_inputs"]["previous_overview"].pop("source"))
    reject("previous C11 result fabricated", lambda x: x["previous_summary"].__setitem__(
        "c_v11_original_campaign_verified_passing_case_count", 16413))
    reject("previous snapshot Rust result fabricated", lambda x: x["previous_summary"]["snapshot"].__setitem__(
        "rust_v22_original_campaign_verified_passing_case_count", 14726))
    reject("previous headline speed invented", lambda x: x["previous_inputs"]["headline"].__setitem__(
        "speed_relative_to_python", "1.5x"))
    reject("previous SVG replaced", lambda x: x.__setitem__("previous_svg", b"not an SVG"))
    contract_mutations = {
        "contract GOAL changed": ("goal_sha256", "0" * 64),
        "contract candidate qualified": ("qualified_candidate_count", 1),
        "contract speed invented": ("performance", "1.5x"),
        "contract holdout opened": ("holdout", "OPENED"),
    }
    for label, (key, value) in contract_mutations.items():
        reject(label, lambda x, k=key, v=value: x["contract"].__setitem__(k, v))
    reject("contract interpreter substituted", lambda x: x["contract"]["pinned_cpython"].__setitem__(
        "path", "/usr/bin/python3"))
    reject("contract source pin substituted", lambda x: x["contract"]["source"].__setitem__(
        "sha256", "0" * 64))
    reject("contract source effect invented", lambda x: x["contract"]["source_only_effects"].__setitem__(
        "actual_workspace_mutations", 1))
    reject("contract holdout read", lambda x: x["contract"]["expanded_holdout"].__setitem__(
        "source_mode_holdout_files_read", 1))
    reject("contract original case denominator weakened", lambda x: x["contract"]
           ["lossless_original_public_case_evidence_v12"].__setitem__("case_execution_denominator", 150))
    reject("contract prior C11 failure erased", lambda x: x["contract"]
           ["preserved_actual_c_v11_campaign"].__setitem__("candidate_execution_failure_count", 1))
    receipt_mutations = {
        "candidate falsely passes": ("candidate_status", "PASS"),
        "candidate falsely qualifies": ("candidate_qualified", True),
        "publication pass redefined": ("publication_pass_means", "CANDIDATE CORRECTNESS"),
        "denominator inflated": ("case_execution_denominator", DENOMINATOR + SUPPLEMENTAL),
        "passing checks inflated": ("verified_passing_case_count", 16414),
        "completed suite fabricated": ("completed_suite_count", 13),
        "distinct worker assertion erased": ("actual_worker_process_ids_are_distinct", False),
        "execution failure erased": ("candidate_execution_failure_count", 0),
        "observed record lost": ("complete_observed_semantic_mismatch_record_count", 605),
        "mismatch chunk lost": ("complete_mismatch_chunk_count", 20),
        "mismatch preservation denied": ("all_observed_semantic_mismatch_records_preserved", False),
        "source method count conflated": ("complete_original_source_method_count", 152),
        "public record count conflated": ("complete_original_public_record_count", 151),
        "executed case count inflated": ("complete_original_executed_case_count", 152),
        "reference vector substituted": ("complete_original_case_vector_sha256", "0" * 64),
        "receipt source pin substituted": ("source_sha256", "0" * 64),
        "previous C11 receipt substituted": ("preserved_actual_v11_failure_receipt_sha256", "0" * 64),
        "supplemental cases merged": ("separate_reference_cases_counted_as_candidate_cases", True),
        "exact mismatch total invented": ("semantic_mismatch_count", 606),
        "speed invented": ("performance", "1.5x"),
        "timing trial invented": ("timing_trials_run", 1),
        "hidden holdout case read": ("hidden_cases_read", 1),
        "holdout opened": ("holdout", "OPENED"),
        "winner selected": ("winner_selected", True),
        "original comparison normalized": ("counterexample_normalization_before_original_comparison", True),
    }
    for label, (key, value) in receipt_mutations.items():
        reject(label, lambda x, k=key, v=value: x["receipt"].__setitem__(k, v))
    reject("duplicate workers", lambda x: x["receipt"]["actual_worker_process_ids"].__setitem__(
        1, x["receipt"]["actual_worker_process_ids"][0]))
    reject("compressed archive substituted", lambda x: x["receipt"]["archive"].__setitem__(
        "sha256", "0" * 64))
    reject("suite source order changed", lambda x: x["receipt"]["suite_outcomes"].reverse())
    reject("genuine execution failure relabeled", lambda x: x["receipt"]["suite_outcomes"][10].__setitem__(
        "failure_class", "PASS"))
    reject("mismatch record removed", lambda x: x["receipt"]
           ["complete_mismatch_suite_vector_fingerprints"][4].__setitem__("complete_record_count", 15))
    reject("mismatch vector reordered", lambda x: x["receipt"]
           ["complete_mismatch_suite_vector_fingerprints"].reverse())
    reject("mismatch vector digest substituted", lambda x: x["receipt"]
           ["complete_mismatch_suite_vector_fingerprints"][4].__setitem__("complete_vector_sha256", "0" * 64))
    assets = build_assets(context, source_digest, source_size)
    require(assets == build_assets(context, source_digest, source_size),
            "outputs are not deterministic")
    require(len(assets["summary"]) < 65536 and len(assets["inputs"]) < 32768,
            "compact outputs copied rather than referenced historical evidence")
    require(PREVIOUS["summary"][1].encode() in assets["summary"],
            "compact summary omitted the exact complete previous summary digest")
    require(b"16,413 / 31,237" in assets["svg"] and b"NOT MEASURED" in assets["svg"],
            "graphic omitted the actual correctness count or speed disclaimer")
    require(b"role=\"img\"" in assets["svg"] and b"aria-labelledby=" in assets["svg"],
            "graphic lost accessible title and description")
    return len(controls)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    for name in ("source", "previous-source", "previous-inputs", "previous-summary",
                 "previous-svg", "c-source", "c-protocol", "c-contract", "c-receipt"):
        parser.add_argument(f"--{name}-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    args = arguments()
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6),
            "the frozen stable CPython 3.14.6 interpreter is required")
    require(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode,
            "frozen interpreter flags -I -B -S are required")
    for name, spec in PREVIOUS.items():
        require(getattr(args, f"previous_{name}_sha256") == spec[1],
                f"previous {name} SHA-256 pin does not match")
    for name, spec in C12.items():
        require(getattr(args, f"c_{name}_sha256") == spec[1],
                f"C12 {name} SHA-256 pin does not match")
    source_digest = args.source_sha256
    require(len(source_digest) == 64 and all(char in "0123456789abcdef" for char in source_digest),
            "source SHA-256 pin is not lowercase hexadecimal")
    source_size = os.stat(os.path.join(ROOT, SELF), follow_symlinks=False).st_size
    source = owner(SELF, source_digest, source_size)
    goal = owner("GOAL.md", GOAL_SHA256, 3756)
    previous = {name: owner(*spec) for name, spec in PREVIOUS.items()}
    evidence = {name: owner(*spec) for name, spec in C12.items()}
    context = {
        "goal": goal, "previous_inputs": parsed(previous["inputs"], "V98 inputs"),
        "previous_summary": parsed(previous["summary"], "complete V98 summary"),
        "previous_svg": previous["svg"],
        "contract": parsed(evidence["contract"], "C12 contract"),
        "receipt": parsed(evidence["receipt"], "complete C12 plaintext receipt"),
    }
    verify_context(context)
    assets = build_assets(context, source_digest, len(source))
    hostile_control_count = mutation_controls(context, source_digest, len(source)) if args.self_test else 0
    if args.render:
        for name, data in assets.items():
            descriptor = os.open(os.path.join(ROOT, OUTPUT + f".{name}.json" if name != "svg"
                                               else OUTPUT + ".svg"),
                                 os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                total = 0
                while total < len(data):
                    written = os.write(descriptor, data[total:])
                    require(written > 0, "short output write")
                    total += written
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    report = {
        "status": "PASS",
        "mode": "self-test" if args.self_test else "render" if args.render else "verify-frozen-context",
        "source_sha256": source_digest, "hostile_control_count": hostile_control_count,
        "candidate_status": "FAIL", "verified_original_checks": 16413,
        "original_case_execution_denominator": DENOMINATOR,
        "completed_original_suite_count": 12, "distinct_candidate_worker_count": 13,
        "observed_mismatch_records_preserved": 606, "preserved_mismatch_chunk_count": 21,
        "candidate_execution_failure_count": 1,
        "compressed_archives_opened": 0, "hidden_cases_read": 0,
        "candidate_workers_started": 0, "clock_samples": 0,
        "workspace_mutations": 3 if args.render else 0,
        "predicted_outputs": {
            name: {"path": OUTPUT + (f".{name}.json" if name != "svg" else ".svg"),
                   "bytes": len(data), "sha256": sha256(data)}
            for name, data in assets.items()
        },
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, Rejected) as failure:
        print(f"FAIL: {failure}", file=sys.stderr)
        raise SystemExit(2)
