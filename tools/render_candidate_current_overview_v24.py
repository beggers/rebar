#!/usr/bin/env python3
"""Show the real repaired Zig build without mistaking a build for a match."""

from __future__ import annotations

import argparse
import builtins
import copy
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SCHEMA = "rebar-candidate-current-overview-v24"
SELF = "tools/render_candidate_current_overview_v24.py"
OUTPUT = "docs/evidence/candidate-current-overview-v24"
PREVIOUS_OWNERS = 135
PREVIOUS_REFERENCES = 140
NEW_OWNERS = 2
TOTAL_OWNERS = 137
TOTAL_REFERENCES = 142
V23 = {
    "source": ("tools/render_candidate_current_overview_v23.py",
               "a7f90986e1020d4cccd0b7eac19779a68a5dac28a33a2a7b5776a5508c91b213", 74868),
    "inputs": ("docs/evidence/candidate-current-overview-v23.inputs.json",
               "e203be81e2ebafa23bd91e41902dd1949fa2245cb8d818e76444982021bfba68", 29567),
    "summary": ("docs/evidence/candidate-current-overview-v23.json",
                "6368a2c900e2ed656830ba773bd454a603f547f3f21f9eabac3490140d687098", 127100),
    "svg": ("docs/evidence/candidate-current-overview-v23.svg",
            "853d3084beb85df634437f3e9198f85c3d28f455c82c94550ae98cb453e561a4", 11462),
}
ZIG_SOURCE = (
    "tools/reproduce_owned_zig_scanner_source_build_v11.py",
    "b908f12d14fb8ebc5f17c62dfc00d48a1a5ee3717a3144aed437059e21c0f097", 207444,
)
ZIG_PROTOCOL = (
    "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md",
    "15fd222876407be72d36c0b9cf2ce581d8b73a954358df192c2a083a08973539", 6144,
)
ZIG_CONTRACT = (
    "oracle/phase2/zig-scanner-source-build-v11.json",
    "92979e4bfacd6d23e7f54f4fdce7a7707cc54dba2512753029fdcd479150464c", 44636,
)
ZIG_ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz",
    "e4a1f369b647f588ac5b12585f7d0e30c4ee3409adc88f660081fb7a59a8df5c", 48246,
)
ZIG_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-zig-phase2-v11-zig-scanner-publication-receipt.json",
    "d53766d0dad571f8b72288cece15fb1ad0892db32c3b3b6b512027db94ca4fcc", 1683,
)
ZIG_EXPANDED = (
    "943c46bda393159604d60efe17c597a2c3c20660e6f9e8b926295c8ad3127f68", 300582,
)
NATIVE_ROLES = {
    "engine": ("caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071", 108888),
    "bridge": ("75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681", 133656),
}
SUITES = (
    ("original_bounded_v5", 151, 0, "Core Python behavior"),
    ("public_v3", 864, 0, "Everyday public methods"),
    ("scanner_v3", 1024, 0, "Scanning and callbacks"),
    ("buffer_v3", 768, 0, "Buffers and memory views"),
    ("managed_v1", 1024, 0, "Buffer lifetime"),
    ("scanner_verbose_v1", 2854, 0, "Verbose patterns"),
    ("public_types_v1", 6912, 248, "Public types and serialization"),
    ("substitution_v2", 5120, 224, "Substitutions"),
    ("shape_v2", 10240, 672, "Result shapes"),
    ("public_surface_v19", 1376, 114, "Full public interface"),
    ("subinterpreter_v2", 128, 0, "Subinterpreters"),
    ("pep688_v4", 264, 4, "Python buffer exporters"),
    ("threaded_pattern_v1", 512, 0, "Patterns across threads"),
)


class GraphError(Exception):
    """The published history, genuine Zig build, or graph is not authentic."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(value: bytes) -> str:
    need(type(value) is bytes, "hash only exact authenticated evidence bytes")
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V24 evidence") from error


def checked_digest(value: object, name: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(part in "0123456789abcdef" for part in value),
         "require a separately pinned SHA-256: " + name)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON,
         "use only isolated, bytecode-free pinned CPython 3.14.6")


def load_module(previous: types.ModuleType, pin: tuple[str, str, int],
                name: str) -> types.ModuleType:
    raw, _ = previous.read_owner(pin[0], pin[1], size=pin[2])
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / pin[0])
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


def load_v23() -> types.ModuleType:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(str(ROOT / V23["source"][0]), flags)
    try:
        owner = os.fstat(descriptor)
        need(stat.S_ISREG(owner.st_mode) and owner.st_size == V23["source"][2],
             "require the exact independently frozen V23 source owner")
        pieces: list[bytes] = []
        remaining = owner.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            need(bool(block), "reject truncated frozen V23 graph source")
            pieces.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"", "reject hidden frozen V23 source bytes")
        raw = b"".join(pieces)
        need(digest(raw) == V23["source"][1], "reject substituted frozen V23 graph source")
    finally:
        os.close(descriptor)
    module = types.ModuleType("_rebar_exact_candidate_overview_v23_for_v24")
    module.__file__ = str(ROOT / V23["source"][0])
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(module.SCHEMA == "rebar-candidate-current-overview-v23"
         and module.SELF == V23["source"][0]
         and tuple(module.SUITES) == SUITES,
         "preserve the exact complete previous graph and its original test cases")
    return module


def authenticate_history() -> tuple[types.ModuleType, types.ModuleType, dict, dict, dict[str, str]]:
    v23 = load_v23()
    v22, previous, _v22_summary, _v22_inputs, references = v23.authenticate_previous()
    need(len(references) == 110, "preserve every exact earlier signed history owner")
    current_c, additions = v23.authenticate_campaign(
        previous, v22, v23.OUTER_ARCHIVE[1], v23.OUTER_RECEIPT[1],
    )
    need(len(additions) == 30 and not (set(references) & set(additions)),
         "preserve exactly the thirty independently authenticated real C campaign owners")
    references = dict(references)
    references.update(additions)
    need(len(references) == PREVIOUS_REFERENCES,
         "never omit one of the 140 previously authenticated signed history references")
    old: dict[str, bytes] = {}
    for key, pin in sorted(V23.items()):
        old[key], _ = previous.read_owner(pin[0], pin[1], size=pin[2])
    summary = previous.document(old["summary"], "exact complete V23 graph summary")
    inputs = previous.document(old["inputs"], "exact complete V23 graph inputs")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "require the exact complete V23 test snapshot")
    v23.validate_snapshot(snapshot)
    need(summary.get("schema") == "rebar-candidate-current-overview-v23-summary"
         and summary.get("status") == "PASS"
         and summary.get("repository_evidence_owner_count") == PREVIOUS_OWNERS
         and summary.get("authenticated_digest_addressed_history_paths") == PREVIOUS_REFERENCES
         and summary.get("qualified_candidate_count") == 0
         and summary.get("full_case_denominator") == 31237
         and summary.get("suite_count") == 13
         and type(summary.get("families")) is list
         and inputs.get("repository_evidence_owner_count") == PREVIOUS_OWNERS
         and inputs.get("all_digest_addressed_history_path_count") == PREVIOUS_REFERENCES
         and snapshot.get("c_v10_repaired_original_campaign") == current_c
         and old["svg"] == v23.make_svg(snapshot, V23["source"][1], V23["inputs"][1]),
         "independently reproduce every previous graph and preserve all genuine C failures")
    for path, fingerprint in sorted(references.items()):
        previous.read_owner(path, fingerprint)
    return v23, previous, summary, inputs, references


def authenticate_zig(previous: types.ModuleType, archive_pin: str,
                     receipt_pin: str) -> tuple[dict, dict[str, str]]:
    need(archive_pin == ZIG_ARCHIVE[1] and receipt_pin == ZIG_RECEIPT[1],
         "require independently supplied hashes for the actual successful Zig build")
    compressed, archive_owner = previous.read_owner(
        ZIG_ARCHIVE[0], archive_pin, size=ZIG_ARCHIVE[2], private=True,
    )
    receipt_raw, receipt_owner = previous.read_owner(
        ZIG_RECEIPT[0], receipt_pin, size=ZIG_RECEIPT[2], private=True,
    )
    receipt = previous.document(receipt_raw, "actual Zig V11 durable build receipt")
    signed = receipt.get("archive")
    need(type(signed) is dict
         and signed.get("path") == archive_owner["path"]
         and signed.get("sha256") == archive_owner["sha256"]
         and signed.get("bytes") == archive_owner["bytes"]
         and signed.get("device") == archive_owner["device"]
         and signed.get("inode") == archive_owner["inode"]
         and signed.get("link_count") == archive_owner["nlink"] == 1
         and signed.get("mode") == "0600"
         and archive_owner["mode"] == 0o600
         and signed.get("file_fsync") is True
         and signed.get("directory_fsync") is True,
         "bind the successful Zig receipt to the real exclusive, durable archive owner")
    previous.boundary(receipt, "actual Zig build publication receipt")
    need(receipt.get("schema")
         == "rebar-phase2-owned-zig-scanner-source-build-v11-durable-publication-receipt"
         and receipt.get("version") == 11 and receipt.get("status") == "PASS"
         and receipt.get("build_status") == "PASS"
         and receipt.get("family") == "zig"
         and receipt.get("label") == "phase2-v11-zig-scanner"
         and receipt.get("source_sha256") == ZIG_SOURCE[1]
         and receipt.get("protocol_sha256") == ZIG_PROTOCOL[1]
         and receipt.get("contract_sha256") == ZIG_CONTRACT[1]
         and receipt.get("uncompressed_sha256") == ZIG_EXPANDED[0]
         and receipt.get("uncompressed_bytes") == ZIG_EXPANDED[1]
         and receipt.get("historical_v21_evidence_owner_count") == 103
         and receipt.get("historical_v21_authenticated_reference_count") == 108
         and receipt.get("current_evidence_owner_count_before_publication") == PREVIOUS_OWNERS
         and receipt.get("current_authenticated_reference_count_before_publication")
         == PREVIOUS_REFERENCES
         and receipt.get("new_evidence_owner_count_after_receipt_publication") == NEW_OWNERS
         and receipt.get("expected_build_process_count_only_after_success") == 26
         and receipt.get("actual_build_process_count") == 26
         and receipt.get("actual_source_apply_count") == 2
         and receipt.get("candidate_correctness") == "NOT MEASURED"
         and receipt.get("candidate_imports") == 0
         and receipt.get("candidate_processes_started") == 0
         and receipt.get("native_libraries_loaded") == 0
         and receipt.get("network_requests") == 0
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("final_cases_read") == 0
         and receipt.get("benchmark_files_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("undefined_behavior") == "NOT MEASURED"
         and receipt.get("failure_preserved") is False
         and receipt.get("winner_selected") is False,
         "a real successful source build is not a correctness test or benchmark")
    report = previous.expand_archive(compressed, expected_sha=ZIG_EXPANDED[0],
                                     expected_bytes=ZIG_EXPANDED[1],
                                     label="actual complete Zig V11 source build")
    previous.boundary(report, "actual complete Zig V11 source build")
    need(report.get("schema") == "rebar-phase2-owned-zig-scanner-source-build-v11"
         and report.get("version") == 11 and report.get("status") == "PASS"
         and report.get("family") == "zig"
         and report.get("label") == "phase2-v11-zig-scanner"
         and report.get("source_sha256") == ZIG_SOURCE[1]
         and report.get("protocol_sha256") == ZIG_PROTOCOL[1]
         and report.get("contract_sha256") == ZIG_CONTRACT[1]
         and report.get("historical_v21_evidence_owner_count") == 103
         and report.get("historical_v21_authenticated_reference_count") == 108
         and report.get("current_evidence_owner_count") == PREVIOUS_OWNERS
         and report.get("current_authenticated_reference_count") == PREVIOUS_REFERENCES
         and report.get("historical_zig_semantic_mismatch_count") == 1764
         and report.get("frozen_correctness")
         == {"case_execution_count": 31237, "private_waiver_count": 13,
             "python": "3.14.6", "suite_count": 13}
         and report.get("expected_build_process_count_only_after_success") == 26
         and report.get("actual_build_process_count") == 26
         and report.get("actual_source_apply_count") == 2
         and report.get("candidate_correctness") == "NOT MEASURED"
         and report.get("candidate_imports") == 0
         and report.get("candidate_processes_started") == 0
         and report.get("reference_processes_started") == 0
         and report.get("native_libraries_loaded") == 0
         and report.get("network_requests") == 0
         and report.get("final_cases_read") == 0
         and report.get("benchmark_files_read") == 0
         and report.get("undefined_behavior") == "NOT MEASURED"
         and report.get("winner_selected") is False,
         "reject invented Zig correctness, process counts, timings, or holdout access")
    zig = load_module(previous, ZIG_SOURCE, "_rebar_exact_zig_v11_build_for_v24")
    protocol_raw, _ = previous.read_owner(ZIG_PROTOCOL[0], ZIG_PROTOCOL[1], size=ZIG_PROTOCOL[2])
    contract_raw, _ = previous.read_owner(ZIG_CONTRACT[0], ZIG_CONTRACT[1], size=ZIG_CONTRACT[2])
    need(bool(protocol_raw)
         and canonical(zig.contract_document(ZIG_SOURCE[1], ZIG_PROTOCOL[1])) == contract_raw,
         "independently reproduce the exact frozen Zig build contract")
    root = report.get("private_root")
    need(type(root) is dict and root.get("mode") == "0700"
         and type(root.get("device")) is int and type(root.get("inode")) is int
         and zig.checked_workdir(root.get("path")) == root.get("path"),
         "require the exact isolated owner-only genuine Zig build root")
    zig.validate_process_schedule(report.get("processes"), root["path"], complete=True)
    phases = report.get("build_phases")
    need(type(phases) is list and len(phases) == 2
         and [phase.get("name") for phase in phases if type(phase) is dict]
         == list(zig.PHASE_NAMES),
         "require both genuine independently isolated completed source builds")
    expected_sources = dict(zig.SOURCE_OWNERS)
    expected_sources["candidates/zig/py_bridge.c"] = (
        zig.DERIVED_BRIDGE_SHA256, zig.DERIVED_BRIDGE_BYTES,
    )
    observed_roles: dict[str, list[tuple[dict, bytes]]] = {"engine": [], "bridge": []}
    source_inodes: set[tuple[int, int]] = set()
    for phase, name in zip(phases, zig.PHASE_NAMES, strict=True):
        overlay = phase.get("overlay_application")
        need(type(overlay) is dict and overlay.get("schema") == zig.OVERLAY_SCHEMA
             and overlay.get("status") == "PASS" and overlay.get("phase") == name
             and overlay.get("derived_sha256") == zig.DERIVED_BRIDGE_SHA256
             and overlay.get("derived_bytes") == zig.DERIVED_BRIDGE_BYTES
             and overlay.get("source_apply_count") == 1
             and overlay.get("candidate_original_modified") is False
             and overlay.get("mode") == "EXCLUSIVE PRIVATE ZIG SCANNER SNAPSHOT APPLY"
             and overlay.get("snapshot_root") == str(Path(root["path"]) / name / "source"),
             "require one real repaired private source overlay in each independent phase")
        snapshots = phase.get("source_snapshots")
        need(type(snapshots) is dict and set(snapshots) == set(expected_sources),
             "preserve all three exact first-party Zig source snapshots")
        for relative, (expected_sha, expected_size) in sorted(expected_sources.items()):
            recorded = snapshots.get(relative)
            need(type(recorded) is dict and recorded.get("sha256") == expected_sha
                 and recorded.get("bytes") == expected_size
                 and recorded.get("mode") == "0600" and recorded.get("link_count") == 1
                 and recorded.get("path")
                 == str(Path(root["path"]) / name / "source" / relative),
                 "reject a substituted first-party Zig private source snapshot")
            observed, _raw = zig.read_absolute_owner(
                recorded["path"], expected_sha, expected_size, False,
            )
            need(observed == recorded
                 and (recorded["device"], recorded["inode"]) not in source_inodes,
                 "require unique, real, independently owned private source files")
            source_inodes.add((recorded["device"], recorded["inode"]))
        outputs = phase.get("native_outputs")
        need(type(outputs) is dict and set(outputs) == set(NATIVE_ROLES),
             "require both complete actual Zig engine and Python bridge outputs")
        for role, (expected_sha, expected_size) in sorted(NATIVE_ROLES.items()):
            item = outputs.get(role)
            need(type(item) is dict and set(item) == {"owner", "raw_elf64", "independence_audit"},
                 "require full actual native bytes and first-party dependency evidence")
            owner = item.get("owner")
            need(type(owner) is dict and owner.get("sha256") == expected_sha
                 and owner.get("bytes") == expected_size
                 and owner.get("mode") == "0700" and owner.get("link_count") == 1
                 and owner.get("path")
                 == str(Path(root["path"]) / name / "native" /
                        (zig.ENGINE_FILENAME if role == "engine" else zig.BRIDGE_FILENAME)),
                 "bind each compiler output to its exact private genuine native owner")
            observed, raw = zig.read_absolute_owner(
                owner["path"], expected_sha, expected_size, True,
            )
            need(observed == owner and digest(raw) == expected_sha
                 and len(raw) == expected_size,
                 "independently read every real compiled engine and bridge byte")
            need(zig.audit_native_role(role, item.get("raw_elf64"))
                 == item.get("independence_audit"),
                 "independently reject stdlib regex, external packages, and cross-engine delegation")
            audit = item["independence_audit"]
            need(audit.get("role") == role
                 and audit.get("external_regex_engine_count") == 0
                 and audit.get("stdlib_regex_engine_count") == 0
                 and audit.get("cross_family_engine_count") == 0
                 and audit.get("native_loader_symbol_count") == 0
                 and audit.get("network_symbol_count") == 0,
                 "the genuine Zig engine must implement matching from scratch")
            observed_roles[role].append((owner, raw))
    reproducibility = report.get("reproducibility")
    need(type(reproducibility) is dict and reproducibility.get("status") == "PASS"
         and reproducibility.get("independent_phase_count") == 2
         and reproducibility.get("byte_identical_native_role_count") == 2
         and reproducibility.get("compiler_process_count") == 26
         and reproducibility.get("source_apply_count") == 2
         and type(reproducibility.get("roles")) is dict
         and set(reproducibility["roles"]) == set(NATIVE_ROLES),
         "require two completed independently reproducible native source builds")
    differences = report.get("raw_elf_differences")
    need(type(differences) is dict
         and differences.get("all_native_artifacts_byte_identical") is True
         and differences.get("independent_phase_count") == 2
         and differences.get("native_role_count") == 2
         and differences.get("additional_compiler_or_inspector_processes") == 0
         and differences.get("comparison_completed_before_reproducibility_classification") is True
         and type(differences.get("roles")) is dict
         and set(differences["roles"]) == set(NATIVE_ROLES),
         "verify complete raw native differences before claiming reproducibility")
    role_proof: dict[str, dict] = {}
    for role, (expected_sha, expected_size) in sorted(NATIVE_ROLES.items()):
        first, second = observed_roles[role]
        claimed = reproducibility["roles"].get(role)
        difference = differences["roles"].get(role)
        need(type(claimed) is dict and claimed.get("sha256") == expected_sha
             and claimed.get("bytes") == expected_size
             and claimed.get("phase_owner_count") == 2
             and claimed.get("byte_identical") is True
             and (first[0]["device"], first[0]["inode"])
             != (second[0]["device"], second[0]["inode"])
             and first[1] == second[1]
             and type(difference) is dict
             and difference.get("byte_identical") is True
             and difference.get("phase_a_sha256") == expected_sha
             and difference.get("phase_b_sha256") == expected_sha
             and difference.get("phase_a_bytes") == expected_size
             and difference.get("phase_b_bytes") == expected_size
             and difference.get("total_differing_byte_count") == 0
             and difference.get("changed_section_count") == 0
             and difference.get("reported_span_count") == 0
             and difference.get("omitted_span_count") == 0
             and difference.get("report_truncated") is False,
             "require genuinely distinct, byte-identical independently built native owners")
        role_proof[role] = {
            "sha256": expected_sha, "bytes": expected_size,
            "independent_phase_owner_count": 2, "byte_identical": True,
            "phase_a_owner": copy.deepcopy(first[0]),
            "phase_b_owner": copy.deepcopy(second[0]),
        }
    before = report.get("owned_original_sources_before")
    after = report.get("owned_original_sources_after")
    need(type(before) is dict and before == after
         and set(before) == set(zig.SOURCE_OWNERS),
         "preserve all original repository Zig source owners without modification")
    for relative, (expected_sha, expected_size) in sorted(zig.SOURCE_OWNERS.items()):
        recorded = before.get(relative)
        need(type(recorded) is dict and recorded.get("path") == relative
             and recorded.get("sha256") == expected_sha
             and recorded.get("bytes") == expected_size
             and recorded.get("mode") == "0600"
             and recorded.get("link_count") == 1,
             "preserve each unmodified original first-party Zig source owner")
        _raw, current_owner = previous.read_owner(
            relative, expected_sha, size=expected_size, private=True,
        )
        need(recorded.get("device") == current_owner["device"]
             and recorded.get("inode") == current_owner["inode"],
             "reject original candidate source mutation or inode substitution")
    proof = {
        "schema": SCHEMA + "-authenticated-zig-v11-source-build",
        "status": "PASS", "build_status": "PASS", "family": "zig",
        "label": "phase2-v11-zig-scanner",
        "source": previous.pin(*ZIG_SOURCE),
        "protocol": previous.pin(*ZIG_PROTOCOL),
        "contract": previous.pin(*ZIG_CONTRACT),
        "archive": previous.pin(*ZIG_ARCHIVE),
        "receipt": previous.pin(*ZIG_RECEIPT),
        "uncompressed_sha256": ZIG_EXPANDED[0],
        "uncompressed_bytes": ZIG_EXPANDED[1],
        "actual_build_process_count": 26,
        "actual_source_apply_count": 2,
        "independent_phase_count": 2,
        "reproducibility": "PASS",
        "byte_identical_native_role_count": 2,
        "roles": role_proof,
        "historical_zig_semantic_mismatch_count": 1764,
        "historical_v23_evidence_owner_count": PREVIOUS_OWNERS,
        "historical_v23_authenticated_reference_count": PREVIOUS_REFERENCES,
        "new_repository_evidence_owner_count": NEW_OWNERS,
        "original_candidate_sources_modified": False,
        "external_regex_engine_count": 0,
        "stdlib_regex_engine_count": 0,
        "cross_family_engine_count": 0,
        "matching_test_status": "NOT MEASURED",
        "actual_candidate_workers": 0,
        "candidate_qualified": False,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, {archive_owner["path"]: archive_owner["sha256"],
                   receipt_owner["path"]: receipt_owner["sha256"]}


def validate_snapshot(snapshot: dict) -> None:
    need(type(snapshot) is dict and snapshot.get("full_case_denominator") == 31237
         and snapshot.get("suite_count") == 13
         and tuple(snapshot.get("suite_ids", ()))
         == tuple(name for name, _count, _mismatch, _display in SUITES)
         and snapshot.get("baseline_passed") == 31237
         and snapshot.get("frozen_independent_engine_family_count") == 6
         and snapshot.get("current_source_owner_count") == 25
         and snapshot.get("qualified_candidate_count") == 0
         and snapshot.get("preserved_v23_repository_evidence_owner_count") == PREVIOUS_OWNERS
         and snapshot.get("preserved_v23_digest_addressed_history_path_count")
         == PREVIOUS_REFERENCES
         and snapshot.get("new_zig_v11_build_repository_evidence_owner_count") == NEW_OWNERS
         and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == TOTAL_OWNERS
         and snapshot.get("all_digest_addressed_history_path_count") == TOTAL_REFERENCES,
         "preserve the frozen denominator and authenticate exactly 135+2/140+2 owners")
    first = snapshot.get("c_v8_repaired_original_campaign")
    second = snapshot.get("c_v9_repaired_original_campaign")
    current = snapshot.get("c_v10_repaired_original_campaign")
    need(type(first) is dict and first.get("status") == "FAIL"
         and first.get("infrastructure_failure_count") == 13
         and first.get("completed_suite_count") == 13
         and type(second) is dict and second.get("status") == "FAIL"
         and second.get("actual_candidate_workers") == 0
         and second.get("infrastructure_failure_count") == 1
         and second.get("semantic_mismatch_count") == "NOT MEASURED"
         and type(current) is dict and current.get("status") == "FAIL"
         and current.get("failure_class") == "SEMANTIC MISMATCH"
         and current.get("actual_candidate_workers") == 13
         and current.get("completed_suite_count") == 13
         and current.get("fully_passing_suite_count") == 8
         and current.get("observed_matching_case_count") == 31237
         and current.get("verified_passing_case_count") == 7325
         and current.get("semantic_mismatch_count") == 1262
         and current.get("infrastructure_failure_count") == 0
         and current.get("all_original_suite_evidence_preserved") is True
         and current.get("original_canonical_native_restored") is True
         and current.get("qualified") is False,
         "preserve every real old C infrastructure failure and all current C mismatches")
    rows = current.get("suite_results")
    need(type(rows) is list and len(rows) == len(SUITES),
         "preserve all thirteen original C test groups")
    for row, (name, count, mismatches, display) in zip(rows, SUITES, strict=True):
        need(type(row) is dict and row.get("suite") == name
             and row.get("display_name") == display
             and row.get("case_execution_denominator") == count
             and row.get("mismatch_count") == mismatches
             and row.get("status") == ("PASS" if mismatches == 0 else "FAIL")
             and row.get("actual_worker_started") is True
             and row.get("all_original_records_and_mismatches_preserved") is True,
             "never omit or relabel a genuine C matching result: " + name)
    need(snapshot.get("c_actual_semantic_mismatch_count") == 2094
         and snapshot.get("c_verified_passing_case_executions") == 7197
         and snapshot.get("rust_actual_semantic_mismatch_count") == 2042
         and snapshot.get("rust_verified_passing_case_executions") == 7461
         and snapshot.get("zig_actual_semantic_mismatch_count") == 1764
         and snapshot.get("zig_verified_passing_case_executions") == 3583
         and snapshot.get("cpp_full_original_campaign", {}).get("semantic_mismatch_count") == 2308
         and snapshot.get("go_v2_full_original_campaign", {}).get("semantic_mismatch_count") == 4518,
         "preserve every historical independent language and all previous Zig mismatches")
    proof = snapshot.get("zig_v11_scanner_repaired_source_build")
    need(type(proof) is dict and proof.get("schema")
         == SCHEMA + "-authenticated-zig-v11-source-build"
         and proof.get("status") == "PASS" and proof.get("build_status") == "PASS"
         and proof.get("family") == "zig"
         and proof.get("label") == "phase2-v11-zig-scanner"
         and proof.get("source") == {"path": ZIG_SOURCE[0], "sha256": ZIG_SOURCE[1], "bytes": ZIG_SOURCE[2]}
         and proof.get("protocol") == {"path": ZIG_PROTOCOL[0], "sha256": ZIG_PROTOCOL[1], "bytes": ZIG_PROTOCOL[2]}
         and proof.get("contract") == {"path": ZIG_CONTRACT[0], "sha256": ZIG_CONTRACT[1], "bytes": ZIG_CONTRACT[2]}
         and proof.get("archive") == {"path": ZIG_ARCHIVE[0], "sha256": ZIG_ARCHIVE[1], "bytes": ZIG_ARCHIVE[2]}
         and proof.get("receipt") == {"path": ZIG_RECEIPT[0], "sha256": ZIG_RECEIPT[1], "bytes": ZIG_RECEIPT[2]}
         and proof.get("uncompressed_sha256") == ZIG_EXPANDED[0]
         and proof.get("uncompressed_bytes") == ZIG_EXPANDED[1]
         and proof.get("actual_build_process_count") == 26
         and proof.get("actual_source_apply_count") == 2
         and proof.get("independent_phase_count") == 2
         and proof.get("reproducibility") == "PASS"
         and proof.get("byte_identical_native_role_count") == 2
         and proof.get("historical_zig_semantic_mismatch_count") == 1764
         and proof.get("historical_v23_evidence_owner_count") == PREVIOUS_OWNERS
         and proof.get("historical_v23_authenticated_reference_count") == PREVIOUS_REFERENCES
         and proof.get("new_repository_evidence_owner_count") == NEW_OWNERS
         and proof.get("original_candidate_sources_modified") is False
         and proof.get("external_regex_engine_count") == 0
         and proof.get("stdlib_regex_engine_count") == 0
         and proof.get("cross_family_engine_count") == 0
         and proof.get("matching_test_status") == "NOT MEASURED"
         and proof.get("actual_candidate_workers") == 0
         and proof.get("candidate_qualified") is False
         and proof.get("candidate_imports") == 0
         and proof.get("candidate_processes_started") == 0
         and proof.get("native_libraries_loaded") == 0
         and proof.get("performance") == "NOT MEASURED"
         and proof.get("memory") == "NOT MEASURED"
         and proof.get("undefined_behavior") == "NOT MEASURED"
         and proof.get("holdout") == "NOT OPENED"
         and proof.get("winner_selected") is False,
         "never claim that the genuine repaired Zig build ran matching or benchmarks")
    roles = proof.get("roles")
    need(type(roles) is dict and set(roles) == set(NATIVE_ROLES),
         "show both independently built, from-scratch Zig native roles")
    for role, (expected_sha, expected_size) in sorted(NATIVE_ROLES.items()):
        item = roles.get(role)
        need(type(item) is dict and item.get("sha256") == expected_sha
             and item.get("bytes") == expected_size
             and item.get("independent_phase_owner_count") == 2
             and item.get("byte_identical") is True,
             "reject incomplete independently reproducible native Zig build proof")
        phase_a, phase_b = item.get("phase_a_owner"), item.get("phase_b_owner")
        need(type(phase_a) is dict and type(phase_b) is dict
             and phase_a.get("sha256") == phase_b.get("sha256") == expected_sha
             and phase_a.get("bytes") == phase_b.get("bytes") == expected_size
             and phase_a.get("mode") == phase_b.get("mode") == "0700"
             and phase_a.get("link_count") == phase_b.get("link_count") == 1
             and (phase_a.get("device"), phase_a.get("inode"))
             != (phase_b.get("device"), phase_b.get("inode")),
             "require two separate genuine compiled native output owners")
    need(snapshot.get("zig_scanner_repaired_build_status") == "PASS"
         and snapshot.get("zig_scanner_repaired_build_process_count") == 26
         and snapshot.get("zig_scanner_repaired_source_apply_count") == 2
         and snapshot.get("zig_scanner_repaired_reproducibility") == "PASS"
         and snapshot.get("zig_scanner_repaired_matching_status") == "NOT MEASURED"
         and snapshot.get("zig_scanner_repaired_candidate_worker_count") == 0
         and snapshot.get("zig_scanner_repaired_candidate_qualified") is False
         and snapshot.get("repaired_c_full_matching_test_status")
         == "FAIL: 1,262 SEMANTIC MISMATCHES"
         and snapshot.get("repaired_c_actual_verified_matching_case_count") == 31237
         and snapshot.get("repaired_c_verified_passing_case_count") == 7325
         and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
         and snapshot.get("repaired_c_infrastructure_failure_count") == 0
         and snapshot.get("repaired_c_completed_suite_count") == 13
         and snapshot.get("repaired_c_actual_candidate_worker_count") == 13
         and snapshot.get("repaired_c_native_promoted") is False,
         "distinguish the untested new Zig build from all completed actual C matching")
    need(snapshot.get("performance") == "NOT MEASURED"
         and snapshot.get("memory") == "NOT MEASURED"
         and snapshot.get("confidence_intervals") == "NOT MEASURED"
         and snapshot.get("hidden_cases_read") == 0
         and snapshot.get("performance_files_read") == 0
         and snapshot.get("clock_samples") == 0
         and snapshot.get("timing_trials_run") == 0
         and snapshot.get("final_comparison_planned_case_count") == 4194304
         and snapshot.get("final_comparison_cases_generated") is False
         and snapshot.get("final_holdout_opened") is False
         and snapshot.get("winner_selected") is False,
         "never invent a speedup, winner, uncertainty, memory result, or opened holdout")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))


def make_svg(snapshot: dict, source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(snapshot)
    current = snapshot["c_v10_repaired_original_campaign"]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1660" height="2180" viewBox="0 0 1660 2180" role="img" aria-labelledby="v24-title v24-description">',
        '<title id="v24-title">Building a faster Python re: the repaired Zig engine builds, but matching and speed have not been tested</title>',
        '<desc id="v24-description">Python passes all 31,237 original reference checks. The newly repaired, independently implemented Zig engine completed 26 real build and inspection steps and produced byte-identical engine and bridge files in two separate builds. This new Zig engine has not run matching tests and is not a qualified candidate. The previously tested Zig engine still has 1,764 recorded differences. The latest C engine really ran all 13 test groups and has 1,262 real matching differences and no infrastructure failures. No replacement qualifies. The complete record contains 137 actual evidence files and 142 distinct signed history references. Speed, memory, confidence intervals and rankings have not been measured. The final holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:33px;font-weight:760;fill:#16324f}.heading{font-size:24px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:17px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.pending{font-size:15px;font-weight:740;fill:#53667b}.big{font-size:25px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}.small{font-size:13px;fill:#42556c}</style>',
        '<rect width="1660" height="2180" rx="22" fill="#f4f7fb"/>',
        '<text x="54" y="66" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="56" y="96" class="body">The repaired Zig engine now genuinely builds twice. Whether it matches Python is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python reference checks"),
        ("26 of 26", "real Zig build steps succeeded"),
        ("2 of 2", "separate identical Zig builds"),
        ("1,262", "recorded C matching differences"),
        ("NOT MEASURED", "speed and memory"),
    )
    for index, (value, label) in enumerate(cards):
        x = 54 + index * 320
        lines.extend((
            f'<rect x="{x}" y="120" width="304" height="104" rx="13" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 14}" y="163" class="big">{xml(value)}</text>',
            f'<text x="{x + 14}" y="198" class="body">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="54" y="241" width="1552" height="782" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="282" class="heading">1. Does each replacement behave exactly like Python?</text>',
        '<text x="78" y="309" class="body">Building successfully is not passing a matching test. A replacement qualifies only after every original check agrees.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original Python reference checks pass.", "pass"),
        ("Zig — newly repaired engine", "BUILT; MATCHING NOT MEASURED", "26 real build and inspection steps; two separate byte-identical engine and bridge builds; no matching tests yet.", "pending"),
        ("Zig — previously tested engine", "NOT COMPATIBLE", "3,583 fully verified passing checks; 1,764 recorded matching differences.", "fail"),
        ("C — latest repaired engine", "NOT COMPATIBLE", "All 13 groups ran: 8 completely passed (7,325 checks); 1,262 differences; 0 runner failures.", "fail"),
        ("C — earlier matching engine", "NOT COMPATIBLE", "7,197 fully verified passing checks; 2,094 matching differences.", "fail"),
        ("Rust", "NOT COMPATIBLE", "7,461 fully verified passing checks; 2,042 matching differences.", "fail"),
        ("C++", "NOT COMPATIBLE", "128 fully verified passing checks; 2,308 matching differences and 5 earlier runner failures.", "fail"),
        ("Go", "NOT COMPATIBLE", "128 fully verified passing checks; 4,518 matching differences and 4 runner failures.", "fail"),
        ("Fortran", "NOT READY", "Its independently built engine is not yet compatible. Matching: NOT MEASURED.", "pending"),
    )
    for index, (name, result, detail, category) in enumerate(rows):
        y = 326 + index * 69
        lines.extend((
            f'<rect x="75" y="{y}" width="1510" height="60" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="94" y="{y + 23}" class="name">{xml(name)}</text>',
            f'<text x="1564" y="{y + 23}" class="{category}" text-anchor="end">{xml(result)}</text>',
            f'<text x="96" y="{y + 46}" class="small">{xml(detail)}</text>',
        ))
    lines.extend((
        '<text x="78" y="983" class="body">Earlier C attempts remain recorded separately: 13 old runner failures, then one runner failure before matching.</text>',
        '<rect x="54" y="1040" width="1552" height="648" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="1081" class="heading">2. Which C test groups still differ?</text>',
        '<text x="78" y="1108" class="body">All 13 groups and original case records are preserved; these are observed matching results, not build results.</text>',
        '<text x="92" y="1135" class="small">TEST GROUP</text>',
        '<text x="1225" y="1135" class="small" text-anchor="end">ORIGINAL CHECKS</text>',
        '<text x="1562" y="1135" class="small" text-anchor="end">RESULT</text>',
    ))
    for index, row in enumerate(current["suite_results"]):
        y = 1148 + index * 35
        even = "#f8fafd" if index % 2 == 0 else "#ffffff"
        result = ("PASSED" if row["mismatch_count"] == 0
                  else f'{row["mismatch_count"]:,} DIFFERENCES')
        category = "pass" if row["mismatch_count"] == 0 else "fail"
        lines.extend((
            f'<rect x="77" y="{y}" width="1506" height="31" rx="5" fill="{even}"/>',
            f'<text x="95" y="{y + 21}" class="body">{xml(row["display_name"])}</text>',
            f'<text x="1225" y="{y + 21}" class="body" text-anchor="end">{row["case_execution_denominator"]:,}</text>',
            f'<text x="1562" y="{y + 21}" class="{category}" text-anchor="end">{xml(result)}</text>',
        ))
    lines.extend((
        '<text x="79" y="1632" class="body">Eight complete C groups pass. The 7,325 checks count only those completely passing groups.</text>',
        '<text x="79" y="1658" class="body">Five C groups contain 1,262 recorded differences. The newly built Zig engine has not run these groups.</text>',
        '<rect x="54" y="1704" width="1552" height="275" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="1745" class="heading">3. Is any replacement faster?</text>',
        '<text x="79" y="1777" class="body">NOT MEASURED. No candidate has first passed every correctness test.</text>',
        '<text x="79" y="1807" class="body">There is no speed or memory comparison, confidence interval, ranking, winner, or opened final holdout.</text>',
        '<text x="79" y="1837" class="body">Real evidence: 135 earlier files + 2 new genuine Zig build files = 137 verified files; 142 signed references.</text>',
        '<text x="79" y="1867" class="body">Zig source was repaired only in separate private build snapshots; the original candidate files were not changed.</text>',
        '<text x="79" y="1897" class="body">Engine and Python bridge were independently verified to use no external or standard-library regex engine.</text>',
        '<text x="79" y="1927" class="body">The original C binary, its exact inode, and its 0755 permissions remain restored.</text>',
        f'<text x="58" y="2016" class="foot">Inputs SHA-256: {xml(inputs_sha)}</text>',
        f'<text x="58" y="2041" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="58" y="2066" class="foot">Actual Zig build archive SHA-256: {ZIG_ARCHIVE[1]}</text>',
        f'<text x="58" y="2091" class="foot">Actual Zig build receipt SHA-256: {ZIG_RECEIPT[1]}</text>',
        f'<text x="58" y="2116" class="foot">Independently rebuilt Zig engine SHA-256: {NATIVE_ROLES["engine"][0]}</text>',
        f'<text x="58" y="2141" class="foot">Independently rebuilt Zig bridge SHA-256: {NATIVE_ROLES["bridge"][0]}</text>',
        '</svg>', '',
    ))
    return "\n".join(lines).encode("utf-8")


def build(source_sha: str, archive_sha: str, receipt_sha: str
          ) -> tuple[types.ModuleType, dict, dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked_digest(source_sha, "V24 renderer source")
    _v23, previous, old_summary, old_inputs, references = authenticate_history()
    previous.read_owner(SELF, source_sha)
    proof, additions = authenticate_zig(previous, archive_sha, receipt_sha)
    need(len(references) == PREVIOUS_REFERENCES and len(additions) == NEW_OWNERS
         and not (set(references) & set(additions)),
         "count exactly the two genuine new Zig build evidence owners")
    references.update(additions)
    need(len(references) == TOTAL_REFERENCES,
         "preserve all 142 individually authenticated distinct signed history paths")
    snapshot = copy.deepcopy(old_summary["snapshot"])
    snapshot.update({
        "preserved_v23_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v23_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "new_zig_v11_build_repository_evidence_owner_count": NEW_OWNERS,
        "all_actual_candidate_and_native_evidence_owner_count": TOTAL_OWNERS,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "zig_v11_scanner_repaired_source_build": copy.deepcopy(proof),
        "zig_scanner_repaired_build_status": "PASS",
        "zig_scanner_repaired_build_process_count": 26,
        "zig_scanner_repaired_source_apply_count": 2,
        "zig_scanner_repaired_reproducibility": "PASS",
        "zig_scanner_repaired_matching_status": "NOT MEASURED",
        "zig_scanner_repaired_candidate_worker_count": 0,
        "zig_scanner_repaired_candidate_qualified": False,
    })
    validate_snapshot(snapshot)
    manifest = {
        "schema": SCHEMA + "-inputs", "version": 24, "python": "3.14.6",
        "renderer": previous.pin(SELF, source_sha),
        "previous_overview": {
            key: previous.pin(path, sha, size)
            for key, (path, sha, size) in sorted(V23.items())
        },
        "original_correctness_manifest": copy.deepcopy(old_inputs["original_correctness_manifest"]),
        "original_source_freeze": copy.deepcopy(old_inputs["original_source_freeze"]),
        "first_failed_c_campaign": copy.deepcopy(snapshot["c_v8_repaired_original_campaign"]),
        "second_failed_c_campaign": copy.deepcopy(snapshot["c_v9_repaired_original_campaign"]),
        "current_complete_c_campaign": copy.deepcopy(snapshot["c_v10_repaired_original_campaign"]),
        "current_repaired_zig_source_build": copy.deepcopy(proof),
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "candidate_families": ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "candidate_qualified_count": 0,
        "preserved_v23_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "new_zig_v11_build_repository_evidence_owner_count": NEW_OWNERS,
        "repository_evidence_owner_count": TOTAL_OWNERS,
        "preserved_v23_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }
    manifest_raw = canonical(manifest)
    manifest_sha = digest(manifest_raw)
    svg = make_svg(snapshot, source_sha, manifest_sha)
    families = copy.deepcopy(old_summary["families"])
    found_zig = 0
    for family in families:
        if family.get("family") == "zig":
            found_zig += 1
            family["current_scanner_repaired_build"] = copy.deepcopy(proof)
            family["current_scanner_repaired_build_status"] = "PASS"
            family["current_scanner_repaired_matching_test_status"] = "NOT MEASURED"
            family["current_scanner_repaired_candidate_worker_count"] = 0
            family["current_scanner_repaired_candidate_qualified"] = False
            family["qualified"] = False
    need(found_zig == 1, "retain exactly one independent historical Zig engine family")
    summary = {
        "schema": SCHEMA + "-summary", "status": "PASS", "python": "3.14.6",
        "source": previous.pin(SELF, source_sha),
        "inputs": previous.pin(OUTPUT + ".inputs.json", manifest_sha),
        "svg": previous.pin(OUTPUT + ".svg", digest(svg)),
        "previous_overview": {
            key: previous.pin(path, sha, size)
            for key, (path, sha, size) in sorted(V23.items())
        },
        "snapshot": snapshot, "families": families,
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "repository_evidence_owner_count": TOTAL_OWNERS,
        "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
        "preserved_v23_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v23_authenticated_reference_path_count": PREVIOUS_REFERENCES,
        "new_zig_v11_build_repository_evidence_owner_count": NEW_OWNERS,
        "qualified_candidate_count": 0,
        "c_repaired_build_status": "PASS",
        "c_repaired_matching_test_status": "FAIL: 1,262 SEMANTIC MISMATCHES",
        "c_repaired_observed_matching_case_count": 31237,
        "c_repaired_verified_passing_case_count": 7325,
        "c_repaired_semantic_mismatch_count": 1262,
        "c_repaired_infrastructure_failure_count": 0,
        "c_repaired_completed_suite_count": 13,
        "c_repaired_candidate_worker_count": 13,
        "c_repaired_fully_passing_suite_count": 8,
        "c_repaired_original_campaign_status": "FAIL",
        "c_repaired_native_promoted": False,
        "existing_canonical_native_present": True,
        "original_canonical_native_restored": True,
        "zig_scanner_repaired_build_status": "PASS",
        "zig_scanner_repaired_build_process_count": 26,
        "zig_scanner_repaired_source_apply_count": 2,
        "zig_scanner_repaired_reproducibility": "PASS",
        "zig_scanner_repaired_matching_test_status": "NOT MEASURED",
        "zig_scanner_repaired_candidate_worker_count": 0,
        "zig_scanner_repaired_candidate_qualified": False,
        "zig_historical_semantic_mismatch_count": 1764,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }
    return previous, manifest, snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".svg", svg),
        (OUTPUT + ".json", canonical(summary)),
    )


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def blocked(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GraphError("V24 source-only operation blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)), (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir", "makedirs",
                  "unlink", "remove", "replace", "rename", "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text",
                    "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object, _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_snapshot() -> dict:
    rows = [{
        "suite": name, "display_name": display,
        "status": "PASS" if mismatches == 0 else "FAIL",
        "failure_class": "PASS" if mismatches == 0 else "SEMANTIC MISMATCH",
        "case_execution_denominator": count, "mismatch_count": mismatches,
        "actual_worker_started": True,
        "worker_returncode": 0 if mismatches == 0 else 1,
        "all_original_records_and_mismatches_preserved": True,
    } for name, count, mismatches, display in SUITES]
    old_first = {"status": "FAIL", "completed_suite_count": 13,
                 "infrastructure_failure_count": 13,
                 "semantic_mismatch_count": "NOT MEASURED",
                 "suite_results": [{"suite": name, "case_execution_denominator": count}
                                   for name, count, _mismatch, _display in SUITES]}
    old_second = {"status": "FAIL", "actual_candidate_workers": 0,
                  "infrastructure_failure_count": 1,
                  "semantic_mismatch_count": "NOT MEASURED",
                  "infrastructure_failure_type": "AttributeError"}
    current = {"status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
               "label": "phase2-v10-live-original-p0", "actual_candidate_workers": 13,
               "full_case_denominator": 31237, "suite_count": 13,
               "completed_suite_count": 13, "fully_passing_suite_count": 8,
               "observed_matching_case_count": 31237,
               "verified_passing_case_count": 7325, "semantic_mismatch_count": 1262,
               "infrastructure_failure_count": 0,
               "all_original_suite_evidence_preserved": True,
               "original_canonical_native_restored": True,
               "qualified": False, "suite_results": rows}
    roles: dict[str, dict] = {}
    for index, (role, (expected_sha, expected_size)) in enumerate(sorted(NATIVE_ROLES.items())):
        first = {"path": "/tmp/rebar-v24-synthetic/reference-a/native/" + role,
                 "sha256": expected_sha, "bytes": expected_size, "device": 2049,
                 "inode": 1100 + index, "link_count": 1, "mode": "0700"}
        second = {"path": "/tmp/rebar-v24-synthetic/reference-b/native/" + role,
                  "sha256": expected_sha, "bytes": expected_size, "device": 2049,
                  "inode": 1200 + index, "link_count": 1, "mode": "0700"}
        roles[role] = {"sha256": expected_sha, "bytes": expected_size,
                       "independent_phase_owner_count": 2, "byte_identical": True,
                       "phase_a_owner": first, "phase_b_owner": second}
    proof = {
        "schema": SCHEMA + "-authenticated-zig-v11-source-build",
        "status": "PASS", "build_status": "PASS", "family": "zig",
        "label": "phase2-v11-zig-scanner",
        "source": {"path": ZIG_SOURCE[0], "sha256": ZIG_SOURCE[1], "bytes": ZIG_SOURCE[2]},
        "protocol": {"path": ZIG_PROTOCOL[0], "sha256": ZIG_PROTOCOL[1], "bytes": ZIG_PROTOCOL[2]},
        "contract": {"path": ZIG_CONTRACT[0], "sha256": ZIG_CONTRACT[1], "bytes": ZIG_CONTRACT[2]},
        "archive": {"path": ZIG_ARCHIVE[0], "sha256": ZIG_ARCHIVE[1], "bytes": ZIG_ARCHIVE[2]},
        "receipt": {"path": ZIG_RECEIPT[0], "sha256": ZIG_RECEIPT[1], "bytes": ZIG_RECEIPT[2]},
        "uncompressed_sha256": ZIG_EXPANDED[0], "uncompressed_bytes": ZIG_EXPANDED[1],
        "actual_build_process_count": 26, "actual_source_apply_count": 2,
        "independent_phase_count": 2, "reproducibility": "PASS",
        "byte_identical_native_role_count": 2, "roles": roles,
        "historical_zig_semantic_mismatch_count": 1764,
        "historical_v23_evidence_owner_count": PREVIOUS_OWNERS,
        "historical_v23_authenticated_reference_count": PREVIOUS_REFERENCES,
        "new_repository_evidence_owner_count": NEW_OWNERS,
        "original_candidate_sources_modified": False,
        "external_regex_engine_count": 0, "stdlib_regex_engine_count": 0,
        "cross_family_engine_count": 0,
        "matching_test_status": "NOT MEASURED", "actual_candidate_workers": 0,
        "candidate_qualified": False, "candidate_imports": 0,
        "candidate_processes_started": 0, "native_libraries_loaded": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "suite_ids": [name for name, _count, _mismatch, _display in SUITES],
        "baseline_passed": 31237, "frozen_independent_engine_family_count": 6,
        "current_source_owner_count": 25, "qualified_candidate_count": 0,
        "preserved_v23_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v23_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "new_zig_v11_build_repository_evidence_owner_count": NEW_OWNERS,
        "all_actual_candidate_and_native_evidence_owner_count": TOTAL_OWNERS,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "c_v8_repaired_original_campaign": old_first,
        "c_v9_repaired_original_campaign": old_second,
        "c_v10_repaired_original_campaign": current,
        "c_actual_semantic_mismatch_count": 2094,
        "c_verified_passing_case_executions": 7197,
        "rust_actual_semantic_mismatch_count": 2042,
        "rust_verified_passing_case_executions": 7461,
        "zig_actual_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_executions": 3583,
        "cpp_full_original_campaign": {"semantic_mismatch_count": 2308},
        "go_v2_full_original_campaign": {"semantic_mismatch_count": 4518},
        "zig_v11_scanner_repaired_source_build": proof,
        "zig_scanner_repaired_build_status": "PASS",
        "zig_scanner_repaired_build_process_count": 26,
        "zig_scanner_repaired_source_apply_count": 2,
        "zig_scanner_repaired_reproducibility": "PASS",
        "zig_scanner_repaired_matching_status": "NOT MEASURED",
        "zig_scanner_repaired_candidate_worker_count": 0,
        "zig_scanner_repaired_candidate_qualified": False,
        "repaired_c_full_matching_test_status": "FAIL: 1,262 SEMANTIC MISMATCHES",
        "repaired_c_actual_verified_matching_case_count": 31237,
        "repaired_c_verified_passing_case_count": 7325,
        "repaired_c_semantic_mismatch_count": 1262,
        "repaired_c_infrastructure_failure_count": 0,
        "repaired_c_completed_suite_count": 13,
        "repaired_c_actual_candidate_worker_count": 13,
        "repaired_c_native_promoted": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED", "hidden_cases_read": 0,
        "performance_files_read": 0, "clock_samples": 0, "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def self_test() -> dict:
    with SourceOnlyWall() as wall:
        base = synthetic_snapshot()
        validate_snapshot(base)
        rejected = 0

        def reject(value: object) -> None:
            nonlocal rejected
            try:
                validate_snapshot(value)  # type: ignore[arg-type]
            except (GraphError, KeyError, TypeError, ValueError, AttributeError):
                rejected += 1
                return
            raise GraphError("accepted forged synthetic V24 Zig build or matching evidence")

        top_changes = {
            "full_case_denominator": 31236, "suite_count": 12,
            "baseline_passed": 31236, "frozen_independent_engine_family_count": 5,
            "current_source_owner_count": 24, "qualified_candidate_count": 1,
            "preserved_v23_repository_evidence_owner_count": 134,
            "preserved_v23_digest_addressed_history_path_count": 139,
            "new_zig_v11_build_repository_evidence_owner_count": 1,
            "all_actual_candidate_and_native_evidence_owner_count": 136,
            "all_digest_addressed_history_path_count": 141,
            "c_actual_semantic_mismatch_count": 0,
            "c_verified_passing_case_executions": 0,
            "rust_actual_semantic_mismatch_count": 0,
            "rust_verified_passing_case_executions": 0,
            "zig_actual_semantic_mismatch_count": 0,
            "zig_verified_passing_case_executions": 0,
            "zig_scanner_repaired_build_status": "FAIL",
            "zig_scanner_repaired_build_process_count": 25,
            "zig_scanner_repaired_source_apply_count": 1,
            "zig_scanner_repaired_reproducibility": "FAIL",
            "zig_scanner_repaired_matching_status": "PASS",
            "zig_scanner_repaired_candidate_worker_count": 1,
            "zig_scanner_repaired_candidate_qualified": True,
            "repaired_c_full_matching_test_status": "PASS",
            "repaired_c_actual_verified_matching_case_count": 7325,
            "repaired_c_verified_passing_case_count": 31237,
            "repaired_c_semantic_mismatch_count": 0,
            "repaired_c_infrastructure_failure_count": 1,
            "repaired_c_completed_suite_count": 12,
            "repaired_c_actual_candidate_worker_count": 12,
            "repaired_c_native_promoted": True,
            "performance": "1.5x faster", "memory": "0 bytes",
            "confidence_intervals": "95%", "hidden_cases_read": 1,
            "performance_files_read": 1, "clock_samples": 1,
            "timing_trials_run": 1, "final_comparison_planned_case_count": 4194303,
            "final_comparison_cases_generated": True,
            "final_holdout_opened": True, "winner_selected": True,
        }
        for key, forged in top_changes.items():
            altered = copy.deepcopy(base)
            altered[key] = forged
            reject(altered)
        proof_changes = {
            "schema": "forged", "status": "FAIL", "build_status": "FAIL",
            "family": "c", "label": "forged",
            "uncompressed_sha256": "0" * 64, "uncompressed_bytes": 300581,
            "actual_build_process_count": 25, "actual_source_apply_count": 1,
            "independent_phase_count": 1, "reproducibility": "FAIL",
            "byte_identical_native_role_count": 1,
            "historical_zig_semantic_mismatch_count": 0,
            "historical_v23_evidence_owner_count": 134,
            "historical_v23_authenticated_reference_count": 139,
            "new_repository_evidence_owner_count": 1,
            "original_candidate_sources_modified": True,
            "external_regex_engine_count": 1,
            "stdlib_regex_engine_count": 1,
            "cross_family_engine_count": 1,
            "matching_test_status": "PASS", "actual_candidate_workers": 1,
            "candidate_qualified": True, "candidate_imports": 1,
            "candidate_processes_started": 1, "native_libraries_loaded": 1,
            "performance": "1.5x faster", "memory": "0 bytes",
            "undefined_behavior": "PASS", "holdout": "OPENED",
            "winner_selected": True,
        }
        for key, forged in proof_changes.items():
            altered = copy.deepcopy(base)
            altered["zig_v11_scanner_repaired_source_build"][key] = forged
            reject(altered)
        for owner_name in ("source", "protocol", "contract", "archive", "receipt"):
            for key, forged in (("sha256", "0" * 64), ("bytes", 1), ("path", "forged")):
                altered = copy.deepcopy(base)
                altered["zig_v11_scanner_repaired_source_build"][owner_name][key] = forged
                reject(altered)
        for role in NATIVE_ROLES:
            for key, forged in (("sha256", "0" * 64), ("bytes", 1),
                                ("independent_phase_owner_count", 1),
                                ("byte_identical", False)):
                altered = copy.deepcopy(base)
                altered["zig_v11_scanner_repaired_source_build"]["roles"][role][key] = forged
                reject(altered)
            for owner_name in ("phase_a_owner", "phase_b_owner"):
                for key, forged in (("sha256", "0" * 64), ("bytes", 1),
                                    ("mode", "0755"), ("link_count", 2)):
                    altered = copy.deepcopy(base)
                    altered["zig_v11_scanner_repaired_source_build"]["roles"][role][owner_name][key] = forged
                    reject(altered)
        c_changes = {
            "status": "PASS", "failure_class": "INFRASTRUCTURE FAILURE",
            "actual_candidate_workers": 12, "completed_suite_count": 12,
            "fully_passing_suite_count": 13, "observed_matching_case_count": 7325,
            "verified_passing_case_count": 31237, "semantic_mismatch_count": 0,
            "infrastructure_failure_count": 1,
            "all_original_suite_evidence_preserved": False,
            "original_canonical_native_restored": False, "qualified": True,
        }
        for key, forged in c_changes.items():
            altered = copy.deepcopy(base)
            altered["c_v10_repaired_original_campaign"][key] = forged
            reject(altered)
        for key, forged in (("status", "PASS"), ("infrastructure_failure_count", 0),
                            ("completed_suite_count", 12)):
            altered = copy.deepcopy(base)
            altered["c_v8_repaired_original_campaign"][key] = forged
            reject(altered)
        for key, forged in (("status", "PASS"), ("infrastructure_failure_count", 0),
                            ("actual_candidate_workers", 1),
                            ("semantic_mismatch_count", 0)):
            altered = copy.deepcopy(base)
            altered["c_v9_repaired_original_campaign"][key] = forged
            reject(altered)
        for index, (name, _count, _mismatches, _display) in enumerate(SUITES):
            for key, forged in (("suite", name + "-forged"),
                                ("mismatch_count", -1),
                                ("actual_worker_started", False)):
                altered = copy.deepcopy(base)
                altered["c_v10_repaired_original_campaign"]["suite_results"][index][key] = forged
                reject(altered)
        reject({})
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (b"26 of 26", b"2 of 2", b"1,764", b"1,262",
                       b"7,325", b"NOT MEASURED", b"137", b"142",
                       b"BUILT; MATCHING NOT MEASURED",
                       b"13 old runner failures", b"one runner failure",
                       b"no external or standard-library regex engine",
                       b"Public types and serialization", b"672 DIFFERENCES"):
            need(phrase in picture, "the accessible graph omits genuine Zig or C evidence")
        probes = (
            lambda: builtins.open("/tmp/rebar-v24-forbidden", "rb"),
            lambda: os.open("/tmp/rebar-v24-forbidden", os.O_RDONLY),
            lambda: os.write(-1, b"forbidden"),
            lambda: subprocess.run(("forbidden-v24-candidate",)),
            lambda: importlib.import_module("candidates.zig_candidate"),
            lambda: threading.Thread(target=lambda: None).start(),
            lambda: socket.create_connection(("127.0.0.1", 1)),
            lambda: time.perf_counter(),
            lambda: tempfile.mkdtemp(),
        )
        for probe in probes:
            before = wall.blocked
            try:
                probe()
            except GraphError:
                need(wall.blocked == before + 1,
                     "independently block every forbidden source-only side effect")
                rejected += 1
            else:
                raise GraphError("V24 source-only verification caused a real external effect")
        need(rejected >= 130, "require comprehensive hostile Zig-build truth controls")
        return {
            "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
            "version": 24, "synthetic_only": True,
            "accepted_synthetic_controls": 1,
            "rejected_hostile_controls": rejected,
            "blocked_effect_count": wall.blocked,
            "repository_evidence_owner_count": TOTAL_OWNERS,
            "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
            "preserved_v23_evidence_owner_count": PREVIOUS_OWNERS,
            "preserved_v23_history_path_count": PREVIOUS_REFERENCES,
            "new_actual_evidence_owner_count": NEW_OWNERS,
            "suite_count": 13, "full_case_denominator": 31237,
            "zig_repaired_build_process_count": 26,
            "zig_repaired_source_apply_count": 2,
            "zig_repaired_independent_phase_count": 2,
            "zig_repaired_matching_test_status": "NOT MEASURED",
            "zig_repaired_candidate_worker_count": 0,
            "historical_zig_semantic_mismatch_count": 1764,
            "current_repaired_c_candidate_worker_count": 13,
            "current_repaired_c_passing_suite_count": 8,
            "current_repaired_c_verified_passing_case_count": 7325,
            "current_repaired_c_semantic_mismatch_count": 1262,
            "current_repaired_c_infrastructure_failure_count": 0,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_holdout_opened": False, "winner_selected": False,
            "synthetic_svg_sha256": digest(picture),
        }


def publish_output(path: str, raw: bytes) -> None:
    need(path in (OUTPUT + ".inputs.json", OUTPUT + ".svg", OUTPUT + ".json")
         and type(raw) is bytes and raw.endswith(b"\n")
         and not raw.endswith(b"\n\n"),
         "publish only the three exact canonical assigned V24 graph outputs")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        position = 0
        while position < len(raw):
            written = os.write(descriptor, raw[position:])
            need(type(written) is int and written > 0,
                 "reject incomplete deterministic V24 graph output")
            position += written
        os.fsync(descriptor)
        recorded = os.fstat(descriptor)
        need(stat.S_ISREG(recorded.st_mode)
             and stat.S_IMODE(recorded.st_mode) == 0o600
             and recorded.st_nlink == 1 and recorded.st_size == len(raw),
             "require one exclusive complete V24 graph output owner")
    finally:
        os.close(descriptor)
    directory = os.open(str(ROOT / "docs/evidence"),
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_CLOEXEC", 0)
                        | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--zig-build-archive-sha256")
    parser.add_argument("--zig-build-receipt-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(all(getattr(args, key) is None for key in (
                "source_sha256", "zig_build_archive_sha256",
                "zig_build_receipt_sha256", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            )), "synthetic self-tests cannot authorize evidence or graph publication")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked_digest(args.source_sha256, "V24 graph source")
        archive = checked_digest(args.zig_build_archive_sha256,
                                 "genuine Zig V11 source build archive")
        receipt = checked_digest(args.zig_build_receipt_sha256,
                                 "genuine Zig V11 durable source build receipt")
        previous, _manifest, snapshot, outputs = build(source, archive, receipt)
        expected = {path: raw for path, raw in outputs}
        if args.render:
            need(args.inputs_sha256 is None and args.summary_sha256 is None
                 and args.svg_sha256 is None,
                 "source-frozen rendering cannot accept substituted output pins")
            for path, raw in outputs:
                publish_output(path, raw)
            result = {
                "schema": SCHEMA + "-published", "status": "PASS", "version": 24,
                "source_sha256": source,
                "inputs_sha256": digest(expected[OUTPUT + ".inputs.json"]),
                "summary_sha256": digest(expected[OUTPUT + ".json"]),
                "svg_sha256": digest(expected[OUTPUT + ".svg"]),
                "actual_zig_build_archive_sha256": archive,
                "actual_zig_build_receipt_sha256": receipt,
                "repository_evidence_owner_count": TOTAL_OWNERS,
                "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
                "new_actual_evidence_owner_count": NEW_OWNERS,
                "zig_repaired_build_status": "PASS",
                "zig_repaired_build_process_count": 26,
                "zig_repaired_source_apply_count": 2,
                "zig_repaired_reproducibility": "PASS",
                "zig_repaired_matching_test_status": "NOT MEASURED",
                "zig_repaired_candidate_worker_count": 0,
                "historical_zig_semantic_mismatch_count": 1764,
                "current_repaired_c_candidate_worker_count": 13,
                "current_repaired_c_passing_suite_count": 8,
                "current_repaired_c_verified_passing_case_count": 7325,
                "current_repaired_c_semantic_mismatch_count": 1262,
                "current_repaired_c_infrastructure_failure_count": 0,
                "outputs_written": True,
                "actual_candidate_imports": 0,
                "actual_candidate_processes_started": 0,
                "hidden_cases_read": 0, "clock_samples": 0,
                "timing_trials_run": 0,
                "performance": "NOT MEASURED", "memory": "NOT MEASURED",
                "final_holdout_opened": False, "winner_selected": False,
            }
            sys.stdout.buffer.write(canonical(result))
            return 0
        pinned_outputs = {
            OUTPUT + ".inputs.json": checked_digest(args.inputs_sha256, "V24 inputs"),
            OUTPUT + ".json": checked_digest(args.summary_sha256, "V24 summary"),
            OUTPUT + ".svg": checked_digest(args.svg_sha256, "V24 accessible graph"),
        }
        for path, fingerprint in pinned_outputs.items():
            raw, _ = previous.read_owner(path, fingerprint,
                                         size=len(expected[path]), private=True)
            need(raw == expected[path] and digest(raw) == fingerprint,
                 "independently reproduce each exact immutable V24 graph owner")
        validate_snapshot(snapshot)
        result = {
            "schema": SCHEMA + "-read-only-frozen-context", "status": "PASS",
            "version": 24, "read_only": True,
            "source_sha256": source,
            "inputs_sha256": pinned_outputs[OUTPUT + ".inputs.json"],
            "summary_sha256": pinned_outputs[OUTPUT + ".json"],
            "svg_sha256": pinned_outputs[OUTPUT + ".svg"],
            "actual_zig_build_archive_sha256": archive,
            "actual_zig_build_receipt_sha256": receipt,
            "suite_count": 13, "full_case_denominator": 31237,
            "candidate_family_count": 6,
            "repository_evidence_owner_count": TOTAL_OWNERS,
            "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
            "preserved_v23_evidence_owner_count": PREVIOUS_OWNERS,
            "preserved_v23_history_path_count": PREVIOUS_REFERENCES,
            "new_actual_evidence_owner_count": NEW_OWNERS,
            "zig_repaired_build_status": "PASS",
            "zig_repaired_build_process_count": 26,
            "zig_repaired_source_apply_count": 2,
            "zig_repaired_reproducibility": "PASS",
            "zig_repaired_matching_test_status": "NOT MEASURED",
            "zig_repaired_candidate_worker_count": 0,
            "historical_zig_semantic_mismatch_count": 1764,
            "earliest_repaired_c_infrastructure_failure_count": 13,
            "previous_repaired_c_infrastructure_failure_count": 1,
            "current_repaired_c_candidate_worker_count": 13,
            "current_repaired_c_passing_suite_count": 8,
            "current_repaired_c_verified_passing_case_count": 7325,
            "current_repaired_c_semantic_mismatch_count": 1262,
            "current_repaired_c_infrastructure_failure_count": 0,
            "original_canonical_native_restored": True,
            "original_canonical_native_inode": 430300,
            "original_canonical_native_mode": "0755",
            "qualified_candidate_count": 0,
            "outputs_written": False,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False, "winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            gzip.BadGzipFile, KeyError, AttributeError) as error:
        sys.stderr.write("current V24 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
