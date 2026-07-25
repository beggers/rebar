#!/usr/bin/env python3
"""Reproducibly explain the current, independently proved regex results."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import html
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "rebar-current-native-correctness-v1"
SVG_PATH = "docs/evidence/current-native-correctness-v1.svg"
MANIFEST_PATH = "docs/evidence/current-native-correctness-v1.json"
REFERENCE_PATH = "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
REFERENCE_SHA256 = "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
FAILURE_SUMMARY_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v12-rust-failures-production-summary.json"
)
FAILURE_SUMMARY_SHA256 = (
    "a9dec1d4798472773a54cb164c6a68d8026e09bc6edd2ab640916fadc5f10dff"
)
FAILURE_PATH = "oracle/cpython-3.14.6/evidence/postfinal-locale-v12-rust-failures.json"
FAILURE_SHA256 = "fda1204c92f843f3610231f33f1271e113374a5dec8fcfa30e1778658655439e"
V21_PINS = {
    "actual_v21_audit_source_sha256": (
        "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
    ),
    "actual_v21_protocol_sha256": (
        "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
    ),
    "actual_v21_base_report_sha256": (
        "4c1de720abb53a5baee56c36a09039e48137e83b2db103cb0d6e77866b496ce4"
    ),
    "actual_v21_strict_report_sha256": (
        "6e742e2e10cde837cb4c39ffe6d1ab12634d672924e109a727e9a558ad22194d"
    ),
}
SPECS = (
    {
        "family": "rust", "label": "Rust", "kind": "original",
        "summary_path": "candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v24-qualified-pass-production-summary.json",
        "summary_sha256": "120c020972607591554f8bcd51f1cb1306ced6d3018b2129ecca038bd5be44d6",
        "proof_path": "candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v24-qualified-pass-proof.json",
        "proof_sha256": "882c712bfed8d0a355bda14847dc78feb2b59b3609ed5f48bd0daccb4e9c33c6",
        "archive_path": "candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v24-qualified-pass.json.gz",
        "archive_sha256": "37de9f254dc3edb72bfe04f51cea8c528449064fba62df273032bb5d7b58b419",
    },
    {
        "family": "vm", "label": "C", "kind": "original",
        "summary_path": "candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v24-qualified-pass-production-summary.json",
        "summary_sha256": "57dc21815ae089cd07023d87055c6df3849d2911f94c1e9cffa400d1c85cee2c",
        "proof_path": "candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v24-qualified-pass-proof.json",
        "proof_sha256": "736e044815a3896d7f45cd1e6b442a03d6196099d9e72aa1dc40b74aa8008f3b",
        "archive_path": "candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v24-qualified-pass.json.gz",
        "archive_sha256": "a389c79cded04db478c624c5f4335ea73c7f6c1984d252b8170c323e1233f54a",
    },
    {
        "family": "zig", "label": "Zig", "kind": "original",
        "summary_path": "candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v24-qualified-pass-production-summary.json",
        "summary_sha256": "4bd885b48666936f1e2613fc5f84ade8d335b62ed21728d0d8b813aba1e20786",
        "proof_path": "candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v24-qualified-pass-proof.json",
        "proof_sha256": "240970ee474cc5f7693d9e080067aa38b481ed003abc48dd8da4738c8cb33e0c",
        "archive_path": "candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v24-qualified-pass.json.gz",
        "archive_sha256": "872070799b77708f6ac16c64de1ae6eb8d18b050133c8a67357f0592babee179",
    },
    {
        "family": "rust", "label": "Rust", "kind": "deeper",
        "summary_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V24-PASS-PRODUCTION-SUMMARY.json",
        "summary_sha256": "59c53b699c20f463c7280a6e39cb37d0a270a21894094dee60002820f26e31e1",
        "proof_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json",
        "proof_sha256": "a26f0659a746838d9af72ff1beff22b91c76d83e7a426b0cc47dbe0400ce67f7",
        "archive_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V24-PASS.json.gz",
        "archive_sha256": "ace3fa8d10725f71881107ace3d9e7d7132a6200723e4f1897e1d5ae6d3d0037",
    },
    {
        "family": "vm", "label": "C", "kind": "deeper",
        "summary_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V24-PASS-PRODUCTION-SUMMARY.json",
        "summary_sha256": "d6e77b025a2b1179a91e3b6b024217522d165207f1c075b7f882e91f8effa9da",
        "proof_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json",
        "proof_sha256": "8695063d5cad48e80ea186315d315d5b8e96c80967e33cac62487c0eef2a4364",
        "archive_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V24-PASS.json.gz",
        "archive_sha256": "b3ede5c0d8a72f2c5cd112b1a03a0827652ad151880645d99213257065e11e0c",
    },
    {
        "family": "zig", "label": "Zig", "kind": "deeper",
        "summary_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V24-PASS-PRODUCTION-SUMMARY.json",
        "summary_sha256": "593ae12d4714f27e6ce264201f59db88571cc8d84068b36c26ddd331ca54ec69",
        "proof_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json",
        "proof_sha256": "09a8b871f96a89b0f3b2e18238116235c6cf377fcbc35eee8e31fec539571c02",
        "archive_path": "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V24-PASS.json.gz",
        "archive_sha256": "8707fb23fa4c47978b2f827673b2559fada0cd052c4a343d8cbf7c6b8306b4b5",
    },
)


class ChartError(Exception):
    """The current chart's authenticated evidence is missing or inconsistent."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ChartError(message)


def canonical(document: Any) -> bytes:
    return (
        json.dumps(document, ensure_ascii=True, allow_nan=False,
                   sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")


def _checked_bytes(relative: str, expected: str) -> bytes:
    require(type(relative) is str and "\\" not in relative,
            "a chart evidence path must be a clean repository-relative path")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts,
            "chart evidence cannot escape the repository")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode),
                "chart evidence must be a genuine regular file: " + relative)
        require(information.st_size <= 32 * 1024 * 1024,
                "chart evidence exceeds its bounded size: " + relative)
        parts: list[bytes] = []
        while True:
            piece = os.read(descriptor, 1024 * 1024)
            if not piece:
                break
            parts.append(piece)
        raw = b"".join(parts)
    finally:
        os.close(descriptor)
    require(len(raw) == information.st_size
            and hashlib.sha256(raw).hexdigest() == expected,
            "the exact published chart evidence changed: " + relative)
    return raw


def _checked_json(relative: str, expected: str) -> dict[str, Any]:
    try:
        document = json.loads(_checked_bytes(relative, expected))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ChartError("the chart evidence is not genuine JSON: " + relative) from error
    require(type(document) is dict,
            "the chart evidence must contain a complete object: " + relative)
    return document


def _validate_owner(owner: Any, family: str, module: str) -> None:
    require(type(owner) is dict
            and owner.get("family") == family
            and owner.get("candidate_module") == module
            and owner.get("status") == "PASS"
            and owner.get("result") == "PASS"
            and owner.get("passed") is True
            and owner.get("genuine_matching_executed") is True
            and owner.get("benchmark_or_timing_executed") is False
            and owner.get("holdout_or_case_fixture_access") is False
            and owner.get("external_regex_packages") == 0
            and owner.get("native_loader_guard_count") == 5
            and owner.get("regex_guard_count") == 13
            and owner.get("standard_pickle_check_count") == 16
            and owner.get("standard_pickle_failure_count") == 0,
            "a genuine, same-family from-scratch native owner is missing: " + family)


def _validate_receipt(summary: dict[str, Any], spec: dict[str, str]) -> None:
    receipt = summary.get("complete_syscall_publication_receipt")
    require(type(receipt) is dict and receipt.get("family") == spec["family"]
            and receipt.get("deep") is (spec["kind"] == "deeper")
            and receipt.get("passed") is True,
            "the actual original evidence publication receipt is missing")
    artifacts = receipt.get("artifacts")
    require(type(artifacts) is dict
            and set(artifacts) == {"archive", "proof", "failure", "invalidated"},
            "the complete actual evidence-publication ledger is missing")
    for kind in ("archive", "proof"):
        observed = artifacts[kind]
        require(type(observed) is dict and len(observed) == 18
                and observed.get("path") == spec[kind + "_path"]
                and observed.get("expected_sha256") == spec[kind + "_sha256"]
                and observed.get("observed_sha256") == spec[kind + "_sha256"]
                and observed.get("created") is True
                and observed.get("write_complete") is True
                and observed.get("file_fsynced") is True
                and observed.get("directory_fsynced") is True
                and observed.get("validated") is True
                and type(observed.get("actual_write_calls")) is list
                and bool(observed["actual_write_calls"]),
                "an actual exclusively published archive or proof is missing: " + kind)
    for kind in ("failure", "invalidated"):
        observed = artifacts[kind]
        require(type(observed) is dict and observed.get("created") is False,
                "passing evidence incorrectly concealed a created failure")


def _validate_pair(
    summary: dict[str, Any], proof: dict[str, Any], spec: dict[str, str],
) -> dict[str, Any]:
    deep = spec["kind"] == "deeper"
    count = 393 if deep else 223_198
    name = spec["label"].upper()
    mode = "qualified-deep" if deep else "qualified-edge"
    module = "candidates." + (
        "vm_candidate" if spec["family"] == "vm" else spec["family"] + "_candidate"
    )
    require(all(summary.get(key) == value for key, value in V21_PINS.items()),
            "the current summary lost its independently frozen native ownership")
    require(summary.get("schema") ==
            "rebar-postfinal-current-build-proofs-v24-" + mode + "-durable-summary"
            and summary.get("status") == "PASS"
            and summary.get("result") == "PASS"
            and summary.get("campaign_qualified") is True
            and summary.get("candidate_family") == name
            and summary.get("candidate_module") == module
            and summary.get("mode") == mode
            and summary.get("checks") == count
            and summary.get("public_mismatch_count") == 0
            and summary.get("original_archive_path") == spec["archive_path"]
            and summary.get("original_archive_sha256") == spec["archive_sha256"]
            and summary.get("complete_owner_proof_path") == spec["proof_path"]
            and summary.get("complete_owner_proof_sha256") == spec["proof_sha256"]
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("holdout") == "NOT ACCESSED",
            "the independently published zero-mismatch result is invalid: "
            + spec["label"] + " " + spec["kind"])
    require((summary.get("seeded_case_count") == 64 if deep
             else summary.get("category_count") == 49),
            "the fixed original denominator or seeded coverage changed")
    _validate_receipt(summary, spec)
    require(proof.get("schema") ==
            "rebar-postfinal-current-build-proofs-v24-" + mode + "-durable-proof"
            and proof.get("status") == "PASS"
            and proof.get("result") == "PASS"
            and proof.get("campaign_qualified") is True
            and proof.get("candidate_family") == name
            and proof.get("candidate_module") == module
            and proof.get("mode") == mode
            and proof.get("checks") == count
            and proof.get("proof_path") == spec["proof_path"]
            and proof.get("original_archive_path") == spec["archive_path"]
            and proof.get("original_archive_sha256") == spec["archive_sha256"]
            and proof.get("original_worker_returncode") == 0
            and proof.get("production_observations_invented") is False
            and proof.get("performance") == "NOT MEASURED"
            and proof.get("holdout") == "NOT ACCESSED",
            "the original independent native-owner proof was changed")
    require((proof.get("public_mismatch_count") == 0
             and proof.get("seeded_case_count") == 64 if deep
             else proof.get("failure_count") == 0
             and proof.get("complete_failure_row_count") == 0
             and proof.get("category_count") == 49),
            "a real candidate mismatch or fixed correctness category was concealed")
    for key in ("current_v21_native_owner_before", "current_v21_native_owner_after"):
        _validate_owner(proof.get(key), spec["family"], module)
    if deep:
        edge_spec = next(item for item in SPECS
                         if item["family"] == spec["family"]
                         and item["kind"] == "original")
        edge = proof.get("qualified_edge")
        require(type(edge) is dict and edge.get("status") == "PASS"
                and edge.get("campaign_qualified") is True
                and edge.get("archive_path") == edge_spec["archive_path"]
                and edge.get("archive_sha256") == edge_spec["archive_sha256"]
                and edge.get("proof_path") == edge_spec["proof_path"]
                and edge.get("proof_sha256") == edge_spec["proof_sha256"],
                "a deeper result is not bound to its own genuine original results")
    return {
        "family": spec["family"], "label": spec["label"],
        "kind": spec["kind"], "status": "PASS", "passed": count,
        "total": count, "mismatches": 0,
        "categories": None if deep else 49,
        "seeded_cases": 64 if deep else None,
        "independent_native_owners": 2,
        "summary_path": spec["summary_path"],
        "summary_sha256": spec["summary_sha256"],
        "proof_path": spec["proof_path"],
        "proof_sha256": spec["proof_sha256"],
        "archive_path": spec["archive_path"],
        "archive_sha256": spec["archive_sha256"],
    }


def _validate_failure(summary: dict[str, Any], failure: dict[str, Any]) -> dict[str, Any]:
    require(summary.get("schema") ==
            "rebar-postfinal-cpython-full-public-locale-v12-actual-role-failure"
            and summary.get("status") == "FAIL"
            and summary.get("role") == "rust"
            and summary.get("synthetic") is False
            and summary.get("production_observations_invented") is False
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("holdout") == "NOT ACCESSED"
            and summary.get("immutable_v6_reference_sha256") == REFERENCE_SHA256,
            "Rust's real first upstream failure was concealed or replaced")
    details = summary.get("details")
    require(type(details) is dict and details.get("returncode") == 2,
            "the real upstream worker's failing return code was lost")
    original = details.get("actual_worker_failure_details")
    require(type(original) is dict
            and original.get("completed_original_method_count") == 0
            and original.get("actual_native_owner_method_guard_checks") == 0
            and original.get("actual_cached_matcher_method_guard_checks") == 0
            and original.get("actual_error") ==
            "the current independently owned native bridge is not authenticated",
            "the actual pre-test harness failure was mistaken for a regex mismatch")
    preserved = summary.get("actual_exclusively_preserved_failure_reports")
    require(type(preserved) is list and len(preserved) == 1,
            "the genuinely published original failure was concealed")
    entry = preserved[0]
    require(type(entry) is dict and entry.get("path") == FAILURE_PATH
            and entry.get("sha256") == FAILURE_SHA256,
            "the first genuine upstream failure has been replaced")
    receipt = entry.get("actual_exclusive_publication_receipt")
    require(type(receipt) is dict and receipt.get("path") == FAILURE_PATH
            and receipt.get("expected_payload_sha256") == FAILURE_SHA256
            and receipt.get("actual_file_created") is True
            and receipt.get("actual_file_fsync") is True
            and receipt.get("actual_directory_fsync") is True
            and receipt.get("fully_durable_publication") is True
            and receipt.get("canonical_reread_succeeded") is True,
            "the real upstream failure's durable receipt is incomplete")
    require(failure.get("schema") == summary["schema"]
            and failure.get("status") == "FAIL"
            and failure.get("role") == "rust"
            and failure.get("actual_failure_destination") == FAILURE_PATH
            and failure.get("details") == details,
            "the preserved original failure is not the actual complete failure")
    return {
        "family": "rust", "label": "Rust", "status": "STOPPED BEFORE TESTS",
        "completed_methods": 0, "total_methods": 152,
        "cause": "test-harness bridge wiring",
        "observed_regex_mismatches": 0,
        "candidate_compatibility_established": False,
        "failure_summary_path": FAILURE_SUMMARY_PATH,
        "failure_summary_sha256": FAILURE_SUMMARY_SHA256,
        "failure_path": FAILURE_PATH, "failure_sha256": FAILURE_SHA256,
    }


def _validate_reference(reference: dict[str, Any]) -> None:
    require(reference.get("schema") ==
            "rebar-postfinal-cpython-full-public-locale-v6-self-oracle"
            and reference.get("status") == "PASS"
            and reference.get("python") == "3.14.6"
            and reference.get("actual_independent_reference_count") == 2
            and reference.get("public_original_methods") == 152
            and reference.get("official_support_module_count") == 26
            and reference.get("actual_upstream_corpus_cases") == 403
            and reference.get("actual_external_fixture_assertion_cases") == 11
            and reference.get("reference_candidate_imports") == 0
            and reference.get("reference_holdout_cases_read") == 0
            and reference.get("performance") == "NOT MEASURED"
            and reference.get("holdout") == "NOT ACCESSED",
            "the pinned genuine two-process Python baseline is incomplete")
    roles = reference.get("roles")
    require(type(roles) is dict and set(roles) == {"reference_a", "reference_b"},
            "both actual independent Python references are required")
    for role in roles.values():
        require(type(role) is dict and role.get("applicable") == 151
                and role.get("passed") == 151
                and role.get("named_private_debug_skips") == 1
                and type(role.get("records")) is list
                and len(role["records"]) == 152,
                "a real complete Python reference or its sole private skip is missing")


def _load_snapshot() -> tuple[dict[str, Any], list[dict[str, str]]]:
    identities: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []
    for spec in SPECS:
        summary = _checked_json(spec["summary_path"], spec["summary_sha256"])
        proof = _checked_json(spec["proof_path"], spec["proof_sha256"])
        _checked_bytes(spec["archive_path"], spec["archive_sha256"])
        rows.append(_validate_pair(summary, proof, spec))
        for kind in ("summary", "proof", "archive"):
            identities.append({
                "purpose": spec["family"] + "-" + spec["kind"] + "-" + kind,
                "path": spec[kind + "_path"],
                "sha256": spec[kind + "_sha256"],
            })
    reference = _checked_json(REFERENCE_PATH, REFERENCE_SHA256)
    _validate_reference(reference)
    failure_summary = _checked_json(FAILURE_SUMMARY_PATH, FAILURE_SUMMARY_SHA256)
    failure = _checked_json(FAILURE_PATH, FAILURE_SHA256)
    stopped = _validate_failure(failure_summary, failure)
    identities.extend((
        {"purpose": "python-two-process-reference", "path": REFERENCE_PATH,
         "sha256": REFERENCE_SHA256},
        {"purpose": "rust-actual-upstream-failure-summary",
         "path": FAILURE_SUMMARY_PATH, "sha256": FAILURE_SUMMARY_SHA256},
        {"purpose": "rust-actual-upstream-failure",
         "path": FAILURE_PATH, "sha256": FAILURE_SHA256},
    ))
    snapshot = {
        "baseline": "CPython 3.14.6 re",
        "independently_executed_python_references": 2,
        "candidate_count": 3,
        "original_case_count_per_candidate": 223_198,
        "original_candidate_checks": 669_594,
        "deeper_case_count_per_candidate": 393,
        "deeper_candidate_checks": 1_179,
        "observed_original_or_deeper_mismatches": 0,
        "rows": rows,
        "full_python_suite": [
            stopped,
            {"family": "vm", "label": "C", "status": "NOT RUN",
             "completed_methods": None, "total_methods": 152,
             "candidate_compatibility_established": False},
            {"family": "zig", "label": "Zig", "status": "NOT RUN",
             "completed_methods": None, "total_methods": 152,
             "candidate_compatibility_established": False},
        ],
        "full_drop_in_compatibility": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return snapshot, sorted(identities, key=lambda item: item["path"])


def _text(x: int, y: int, value: str, css: str = "body", **extra: str) -> str:
    attributes = "".join(
        ' ' + key.replace("_", "-") + '="' + html.escape(value, quote=True) + '"'
        for key, value in extra.items()
    )
    return (f'<text x="{x}" y="{y}" class="{css}"{attributes}>'
            + html.escape(value) + "</text>")


def render_svg(snapshot: dict[str, Any]) -> bytes:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1110" '
        'viewBox="0 0 1200 1110" role="img" aria-labelledby="title description">',
        '<title id="title">How close are we to replacing Python’s re?</title>',
        '<desc id="description">Three independently written Rust, C and Zig '
        'engines each passed all 223,198 original and 393 deeper correctness '
        'checks. The complete official Python suite has not passed: Rust '
        'stopped before its first test because of test-harness bridge wiring; '
        'C and Zig have not run it. Speed has not been measured.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        "'Segoe UI',sans-serif}.title{font-size:36px;font-weight:760;fill:#10223b}"
        '.subtitle{font-size:17px;fill:#43536b}.metric{font-size:31px;'
        'font-weight:750;fill:#10223b}.metric-label{font-size:15px;fill:#43536b}'
        '.heading{font-size:22px;font-weight:720;fill:#10223b}.body{font-size:'
        '16px;fill:#25364e}.small{font-size:14px;fill:#43536b}.strong{font-size:'
        '16px;font-weight:720;fill:#10223b}.pass{font-size:14px;font-weight:700;'
        'fill:#116139}.warning{font-size:14px;font-weight:720;fill:#8a4b08}'
        '.pending{font-size:14px;font-weight:720;fill:#485870}.footer{font-size:'
        '15px;font-weight:650;fill:#25364e}</style>',
        '<rect width="1200" height="1110" rx="20" fill="#f5f8fc"/>',
        _text(54, 76, "How close are we to replacing Python’s re?", "title"),
        _text(56, 109,
              "Current from-scratch engines · checked against Python 3.14.6",
              "subtitle"),
    ]
    cards = ((54, "3", "independently written engines"),
             (338, "669,594", "original candidate-checks"),
             (622, "1,179", "deeper candidate-checks"),
             (906, "0", "observed correctness mismatches"))
    for x, number, label in cards:
        parts.extend((f'<rect x="{x}" y="143" width="240" height="100" '
                      'rx="14" fill="#ffffff" stroke="#dce5ef"/>',
                      _text(x + 17, 184, number, "metric"),
                      _text(x + 17, 215, label, "metric-label")))
    parts.extend((
        _text(56, 288, "Original correctness checks", "heading"),
        _text(56, 313, "The same 223,198 cases for each engine · 49 categories",
              "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 345 + index * 54
        parts.extend((
            _text(66, y + 22, label, "strong"),
            f'<rect x="158" y="{y}" width="700" height="29" '
            'rx="8" fill="#d9efe4"/>',
            f'<rect x="158" y="{y}" width="700" height="29" '
            'rx="8" fill="#17844e"/>',
            _text(875, y + 20, "223,198 / 223,198", "strong"),
            _text(1080, y + 20, "100%", "pass"),
        ))
    parts.extend((
        _text(56, 557, "Deeper correctness checks", "heading"),
        _text(56, 582, "The same 393 difficult cases for each engine · "
              "including 64 fixed-seed cases", "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 611 + index * 54
        parts.extend((
            _text(66, y + 22, label, "strong"),
            f'<rect x="158" y="{y}" width="700" height="29" '
            'rx="8" fill="#d9efe4"/>',
            f'<rect x="158" y="{y}" width="700" height="29" '
            'rx="8" fill="#17844e"/>',
            _text(875, y + 20, "393 / 393", "strong"),
            _text(1080, y + 20, "100%", "pass"),
        ))
    parts.extend((
        _text(56, 820, "Complete Python test suite", "heading"),
        _text(56, 844, "Passing these 152 original tests is still required "
              "before claiming a drop-in replacement.", "small"),
    ))
    suites = (
        (54, "Rust", "STOPPED BEFORE TESTS", "0 / 152 reached",
         "Test-harness bridge wiring", "#fff8eb", "#f2d199", "warning"),
        (437, "C", "NOT RUN", "152 tests remain", "No result claimed",
         "#f1f4f9", "#d9e1ec", "pending"),
        (820, "Zig", "NOT RUN", "152 tests remain", "No result claimed",
         "#f1f4f9", "#d9e1ec", "pending"),
    )
    for x, label, status, count, explanation, fill, stroke, css in suites:
        parts.extend((
            f'<rect x="{x}" y="862" width="326" height="121" rx="13" '
            f'fill="{fill}" stroke="{stroke}"/>',
            _text(x + 17, 892, label, "strong"),
            _text(x + 17, 918, status, css),
            _text(x + 17, 945, count, "body"),
            _text(x + 17, 969, explanation, "small"),
        ))
    parts.extend((
        '<rect x="54" y="1002" width="1092" height="73" rx="12" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(72, 1030,
              "Overall: promising correctness; complete compatibility NOT ESTABLISHED.",
              "footer"),
        _text(72, 1054,
              "Speed and memory: NOT MEASURED · final holdout: NOT ACCESSED.",
              "small"),
        '</svg>\n',
    ))
    require(snapshot.get("candidate_count") == 3
            and snapshot.get("original_candidate_checks") == 669_594
            and snapshot.get("deeper_candidate_checks") == 1_179
            and snapshot.get("observed_original_or_deeper_mismatches") == 0
            and snapshot.get("full_drop_in_compatibility") == "NOT ESTABLISHED"
            and snapshot.get("performance") == "NOT MEASURED"
            and snapshot.get("holdout") == "NOT ACCESSED",
            "the generated chart would misstate its authenticated observations")
    rows = snapshot.get("rows")
    require(type(rows) is list and len(rows) == 6
            and all(type(row) is dict and row.get("status") == "PASS"
                    and row.get("passed") == row.get("total")
                    and row.get("mismatches") == 0 for row in rows),
            "the generated chart cannot claim unproved candidate successes")
    suites_snapshot = snapshot.get("full_python_suite")
    require(type(suites_snapshot) is list
            and [(item.get("family"), item.get("status"))
                 for item in suites_snapshot]
            == [("rust", "STOPPED BEFORE TESTS"),
                ("vm", "NOT RUN"), ("zig", "NOT RUN")],
            "the generated chart would misstate the actual upstream status")
    return "\n".join(parts).encode("utf-8")


def _bundle() -> tuple[bytes, bytes, dict[str, Any]]:
    snapshot, identities = _load_snapshot()
    svg = render_svg(snapshot)
    manifest = {
        "schema": SCHEMA + "-manifest", "status": "PASS",
        "generator_path": "tools/render_current_correctness_v1.py",
        "chart_path": SVG_PATH,
        "chart_sha256": hashlib.sha256(svg).hexdigest(),
        "chart_bytes": len(svg),
        "validated_input_count": len(identities),
        "validated_inputs": identities,
        "snapshot": snapshot,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return svg, canonical(manifest), manifest


def _exclusive_publish(name: str, payload: bytes, directory: int) -> str:
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = os.open(name, flags, 0o644, dir_fd=directory)
    except FileExistsError:
        descriptor = os.open(
            name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory,
        )
        try:
            require(stat.S_ISREG(os.fstat(descriptor).st_mode),
                    "an existing generated chart is not a regular file")
            pieces: list[bytes] = []
            while True:
                piece = os.read(descriptor, 1024 * 1024)
                if not piece:
                    break
                pieces.append(piece)
            require(b"".join(pieces) == payload,
                    "an existing generated chart differs; refusing to overwrite")
        finally:
            os.close(descriptor)
        return "EXISTING IDENTICAL"
    try:
        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            require(type(count) is int and count > 0,
                    "an actual exclusive chart write did not complete")
            written += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.fsync(directory)
    return "EXCLUSIVELY CREATED"


def _write(svg: bytes, manifest: bytes) -> dict[str, str]:
    flags = (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    root = os.open(str(ROOT), flags)
    docs = -1
    evidence = -1
    try:
        docs = os.open("docs", flags, dir_fd=root)
        try:
            evidence = os.open("evidence", flags, dir_fd=docs)
        except FileNotFoundError:
            try:
                os.mkdir("evidence", 0o755, dir_fd=docs)
            except FileExistsError:
                pass
            os.fsync(docs)
            evidence = os.open("evidence", flags, dir_fd=docs)
        return {
            "chart": _exclusive_publish("current-native-correctness-v1.svg",
                                         svg, evidence),
            "manifest": _exclusive_publish("current-native-correctness-v1.json",
                                            manifest, evidence),
        }
    finally:
        if evidence != -1:
            os.close(evidence)
        if docs != -1:
            os.close(docs)
        os.close(root)


def _self_test() -> dict[str, Any]:
    effects = {"file_reads": 0, "file_writes": 0, "directory_creations": 0,
               "candidate_imports": 0, "workers": 0, "clock_samples": 0,
               "holdout_cases_read": 0, "performance_fixtures_read": 0}
    saved_open = builtins.open
    saved_os_open = os.open
    saved_os_write = os.write
    saved_os_mkdir = os.mkdir

    def block_read(*args: Any, **kwargs: Any) -> Any:
        effects["file_reads"] += 1
        raise ChartError("candidate-free chart self-test must not open files")

    def block_write(*args: Any, **kwargs: Any) -> Any:
        effects["file_writes"] += 1
        raise ChartError("candidate-free chart self-test must not write files")

    def block_mkdir(*args: Any, **kwargs: Any) -> Any:
        effects["directory_creations"] += 1
        raise ChartError("candidate-free chart self-test must not create directories")

    accepted = 0
    rejected = 0
    builtins.open = block_read
    os.open = block_read
    os.write = block_write
    os.mkdir = block_mkdir
    try:
        rows = [
            {"family": item["family"], "label": item["label"],
             "kind": item["kind"], "status": "PASS",
             "passed": 393 if item["kind"] == "deeper" else 223_198,
             "total": 393 if item["kind"] == "deeper" else 223_198,
             "mismatches": 0}
            for item in SPECS
        ]
        snapshot = {
            "candidate_count": 3, "original_candidate_checks": 669_594,
            "deeper_candidate_checks": 1_179,
            "observed_original_or_deeper_mismatches": 0,
            "rows": rows,
            "full_python_suite": [
                {"family": "rust", "status": "STOPPED BEFORE TESTS"},
                {"family": "vm", "status": "NOT RUN"},
                {"family": "zig", "status": "NOT RUN"},
            ],
            "full_drop_in_compatibility": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }
        svg = render_svg(snapshot)
        require(svg == render_svg(copy.deepcopy(snapshot)),
                "the synthetic chart is not byte-for-byte reproducible")
        require(svg.startswith(b'<svg ') and svg.endswith(b'</svg>\n')
                and b"669,594" in svg and b"1,179" in svg
                and svg.count(b"223,198 / 223,198") == 3
                and svg.count(b"393 / 393") == 3
                and b"STOPPED BEFORE TESTS" in svg
                and svg.count(b">NOT RUN</text>") == 2
                and b"NOT MEASURED" in svg
                and b"NOT ACCESSED" in svg,
                "the deterministic chart omits an actual result or disclosure")
        accepted += 10
        changes: tuple[tuple[str, Any], ...] = (
            ("candidate_count", 2),
            ("original_candidate_checks", 669_593),
            ("deeper_candidate_checks", 1_178),
            ("observed_original_or_deeper_mismatches", 1),
            ("full_drop_in_compatibility", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "ACCESSED"),
        )
        for field, value in changes:
            broken = copy.deepcopy(snapshot)
            broken[field] = value
            try:
                render_svg(broken)
            except ChartError:
                rejected += 1
            else:
                raise ChartError("accepted a fabricated chart field: " + field)
        for index in range(6):
            for field, value in (("status", "FAIL"), ("mismatches", 1),
                                 ("passed", rows[index]["total"] - 1)):
                broken = copy.deepcopy(snapshot)
                broken["rows"][index][field] = value
                try:
                    render_svg(broken)
                except ChartError:
                    rejected += 1
                else:
                    raise ChartError("concealed an actual candidate mismatch")
        for index, status in enumerate(("PASS", "PASS", "PASS")):
            broken = copy.deepcopy(snapshot)
            broken["full_python_suite"][index]["status"] = status
            try:
                render_svg(broken)
            except ChartError:
                rejected += 1
            else:
                raise ChartError("falsely qualified the complete upstream suite")
        require(all(value == 0 for value in effects.values()),
                "the pure synthetic chart controls had actual external effects")
    finally:
        builtins.open = saved_open
        os.open = saved_os_open
        os.write = saved_os_write
        os.mkdir = saved_os_mkdir
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "accepted_controls": accepted, "rejected_controls": rejected,
        "total_controls": accepted + rejected, "effects": effects,
        "production_observations_invented": False,
        "candidate_results_qualified": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the current from-scratch regex correctness chart."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            result = _self_test()
        else:
            svg, manifest, document = _bundle()
            if options.write:
                publication = _write(svg, manifest)
            else:
                require(_checked_bytes(SVG_PATH, document["chart_sha256"]) == svg,
                        "the committed chart is not reproducible")
                require(_checked_bytes(
                    MANIFEST_PATH, hashlib.sha256(manifest).hexdigest(),
                ) == manifest, "the committed evidence manifest is not reproducible")
                publication = {"chart": "VERIFIED", "manifest": "VERIFIED"}
            result = {
                "schema": SCHEMA + ("-write" if options.write else "-check"),
                "status": "PASS", "chart_path": SVG_PATH,
                "chart_sha256": document["chart_sha256"],
                "manifest_path": MANIFEST_PATH,
                "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
                "validated_input_count": document["validated_input_count"],
                "publication": publication,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            }
    except (ChartError, OSError, ValueError, TypeError, MemoryError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-failure", "status": "FAIL",
            "error_type": type(error).__name__, "reason": str(error),
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
              file=sys.stderr)
        return 2
    print(canonical(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
