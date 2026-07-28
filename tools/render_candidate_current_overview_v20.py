#!/usr/bin/env python3
"""Render the actual repaired C build without claiming matching or speed."""

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
from pathlib import Path, PurePosixPath
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SCHEMA = "rebar-candidate-current-overview-v20"
SELF = "tools/render_candidate_current_overview_v20.py"
OUTPUT = "docs/evidence/candidate-current-overview-v20"
MAX_FILE = 64 * 1024 * 1024
MAX_REPORT = 4 * 1024 * 1024
PRIOR = {
    "source": ("tools/render_candidate_current_overview_v19.py", "8144272f7c91e3821306a4d3963c8e201c68b275cecacf80d5000dd98c502494"),
    "inputs": ("docs/evidence/candidate-current-overview-v19.inputs.json", "8f1eb51ff477f0b59934ee503d9bf795f472fd6674180e2af244c7ad4504560c"),
    "summary": ("docs/evidence/candidate-current-overview-v19.json", "504de87d091c555eb53d664fbfaaa70660ff4dd2f9abc22803246f8a5e18287f"),
    "svg": ("docs/evidence/candidate-current-overview-v19.svg", "7dea68622d7c360f9d2af83f97d76210889b2aeda6662e06178009a1127cf3d6"),
}
V8 = {
    "source": ("tools/reproduce_owned_native_source_build_v8.py", "afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4"),
    "protocol": ("oracle/phase2/NATIVE-SOURCE-BUILD-V8.md", "376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2"),
    "contract": ("oracle/phase2/native-source-build-v8.json", "7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b"),
}
ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v8-c-phase2-v8.json.gz",
    "69a795af6c407c0719b68dfa9fd4cb6dcfca2595271f72b83bc43678521f2598",
    37452,
)
RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v8-c-phase2-v8-publication-receipt.json",
    "3b0983af9729b3150ae239a83dd0fdb37c6e790b3c03ebea48c77215f51456b8",
    1848,
)
P0 = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
)
V7 = (
    "oracle/phase2/native-source-build-v7.json",
    "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
)
ORIGINAL = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185,
)
ADAPTER = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707,
)
EXISTING_NATIVE = (
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd",
    149976,
)
DERIVED_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
DERIVED_BYTES = 218308
NATIVE_SHA256 = "60e50499c34267927e8d312908d7d86b536106b32f418f76453833df7e91694f"
NATIVE_BYTES = 163136
EXPANDED_SHA256 = "504e8535f23eb71ed643cc71d48d1b289c304536c487729aaba40c8df8fe522b"
EXPANDED_BYTES = 306580
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
)
SUITES = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)


class GraphError(Exception):
    """Reject substituted evidence or an unsupported headline."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "digest only complete genuine bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise GraphError("invalid canonical graph value") from error


def checked_digest(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "invalid " + label + " SHA-256")
    return value


def checked_path(value: object) -> tuple[str, ...]:
    need(type(value) is str and 0 < len(value) <= 512
         and "\\" not in value and "\x00" not in value,
         "invalid evidence path")
    parsed = PurePosixPath(value)
    need(not parsed.is_absolute() and str(parsed) == value
         and 0 < len(parsed.parts) <= 12
         and all(part not in ("", ".", "..") for part in parsed.parts),
         "evidence escaped its repository owner")
    return parsed.parts


def read_owner(path: str, expected: str, *, size: int | None = None,
               private: bool = False, maximum: int = MAX_FILE) -> tuple[bytes, dict]:
    checked_digest(expected, path)
    parts = checked_path(path)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        fd = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(fd)
            named = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
            need(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                 and (before.st_dev, before.st_ino)
                 == (named.st_dev, named.st_ino)
                 and 0 < before.st_size <= maximum,
                 "substituted, missing, or oversized owner: " + path)
            if size is not None:
                need(before.st_size == size, "changed exact owner size: " + path)
            if private:
                need(stat.S_IMODE(before.st_mode) == 0o600
                     and before.st_uid == os.geteuid() and before.st_nlink == 1,
                     "build evidence must be an independent private owner")
            pieces: list[bytes] = []
            remaining = before.st_size
            while remaining:
                part = os.read(fd, min(remaining, 1024 * 1024))
                need(bool(part), "truncated graph evidence")
                pieces.append(part)
                remaining -= len(part)
            need(os.read(fd, 1) == b"", "concealed trailing evidence")
            after = os.fstat(fd)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "evidence owner changed during authenticated read")
            raw = b"".join(pieces)
            need(digest(raw) == expected, "changed genuine evidence: " + path)
            return raw, {
                "path": path, "sha256": expected, "bytes": before.st_size,
                "device": before.st_dev, "inode": before.st_ino,
            }
        finally:
            os.close(fd)
    finally:
        os.close(directory)


def unique(pairs: list[tuple[str, object]]) -> dict:
    result: dict[str, object] = {}
    for key, value in pairs:
        need(type(key) is str and key not in result,
             "duplicate signed graph JSON key")
        result[key] = value
    return result


def document(raw: bytes, name: str) -> dict:
    try:
        result = json.loads(
            raw, object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("non-finite signed graph JSON")),
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise GraphError("invalid signed graph JSON: " + name) from error
    need(type(result) is dict and canonical(result) == raw,
         "noncanonical signed graph owner: " + name)
    return result


def pin(path: str, sha: str, size: int | None = None) -> dict:
    checked_path(path)
    checked_digest(sha, path)
    result = {"path": path, "sha256": sha}
    if size is not None:
        need(type(size) is int and size > 0, "invalid frozen evidence size")
        result["bytes"] = size
    return result


def discover_history(value: object, found: dict[str, str]) -> None:
    if type(value) is dict:
        path = value.get("path")
        sha = value.get("sha256")
        if (type(path) is str and type(sha) is str
                and path.startswith(("oracle/phase2/evidence/",
                                     "experiments/rust_public_practice_v1/"))):
            checked_path(path)
            checked_digest(sha, path)
            need(path not in found or found[path] == sha,
                 "conflicting historical evidence owner")
            found[path] = sha
        for child in value.values():
            discover_history(child, found)
    elif type(value) is list:
        for child in value:
            discover_history(child, found)


def validate_v19(summary: dict, inputs: dict) -> None:
    need(summary.get("schema") == "rebar-candidate-current-overview-v19-summary"
         and summary.get("status") == "PASS"
         and summary.get("repository_evidence_owner_count") == 71
         and summary.get("full_case_denominator") == 31237
         and summary.get("suite_count") == 13,
         "the complete published V19 history was changed")
    need(inputs.get("schema") == "rebar-candidate-current-overview-v19-inputs"
         and inputs.get("repository_evidence_owner_count") == 71
         and inputs.get("full_case_denominator") == 31237
         and inputs.get("suite_count") == 13,
         "the prior signed overview manifest was changed")
    snap = summary.get("snapshot")
    need(type(snap) is dict
         and snap.get("all_actual_candidate_and_native_evidence_owner_count") == 71
         and snap.get("current_source_owner_count") == 25
         and snap.get("frozen_independent_engine_family_count") == 6
         and snap.get("current_tested_candidate_family_count") == 5
         and snap.get("qualified_candidate_count") == 0
         and snap.get("verified_activation_v4_actual_activation_count") == 3
         and snap.get("verified_activation_v4_current_active_target_count") == 0
         and snap.get("baseline_passed") == 31237
         and tuple(snap.get("suite_ids", ())) == SUITES,
         "never erase the original baseline, families, or activation history")
    need(snap.get("c_actual_semantic_mismatch_count") == 2094
         and snap.get("c_verified_passing_case_executions") == 7197
         and snap.get("rust_actual_semantic_mismatch_count") == 2042
         and snap.get("rust_verified_passing_case_executions") == 7461
         and snap.get("zig_actual_semantic_mismatch_count") == 1764
         and snap.get("zig_verified_passing_case_executions") == 3583,
         "never erase genuine first-party matching failures")
    c = snap.get("c_full_gate")
    cpp = snap.get("cpp_full_original_campaign")
    go = snap.get("go_v2_full_original_campaign")
    need(type(c) is dict and c.get("gate_status") == "FAIL"
         and c.get("actual_semantic_mismatch_count") == 2094
         and c.get("qualified_candidate_count") == 0,
         "the last fully tested C version still failed")
    need(type(cpp) is dict and cpp.get("status") == "FAIL"
         and cpp.get("completed_suite_count") == 13
         and cpp.get("semantic_mismatch_count") == 2308
         and cpp.get("verified_passing_case_count") == 128,
         "never erase the original full C++ failure")
    need(type(go) is dict and go.get("status") == "FAIL"
         and go.get("completed_suite_count") == 13
         and go.get("semantic_mismatch_count") == 4518
         and go.get("infrastructure_failure_count") == 4
         and go.get("verified_passing_case_count") == 128
         and go.get("restoration_status") == "PASS",
         "never erase the complete Go failure or restoration")
    for obj in (summary, inputs, snap):
        need(obj.get("performance") == "NOT MEASURED"
             and obj.get("memory") == "NOT MEASURED"
             and obj.get("confidence_intervals") == "NOT MEASURED"
             and obj.get("final_comparison_planned_case_count") == 4194304
             and obj.get("final_comparison_cases_generated") is False
             and obj.get("final_holdout_opened") is False,
             "the preserved graph cannot invent performance or open the holdout")
    need(snap.get("hidden_cases_read") == 0
         and snap.get("performance_files_read") == 0
         and snap.get("clock_samples") == 0
         and snap.get("timing_trials_run") == 0
         and snap.get("winner_selected") is False,
         "the preserved graph crossed the original performance boundary")
    families = summary.get("families")
    need(type(families) is list
         and [row.get("family") for row in families]
         == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
         "the original seven displayed family rows were changed")


def validate_actual_build(report: dict, receipt: dict,
                          archive: dict, receipt_owner: dict) -> dict:
    need(report.get("schema") == "rebar-phase2-owned-native-source-build-v8"
         and report.get("version") == 8 and report.get("status") == "PASS"
         and report.get("family") == "c"
         and report.get("label") == "phase2-v8"
         and report.get("source_sha256") == V8["source"][1]
         and report.get("protocol_sha256") == V8["protocol"][1]
         and report.get("contract_sha256") == V8["contract"][1]
         and report.get("original_source_sha256") == ORIGINAL[1]
         and report.get("derived_source_sha256") == DERIVED_SHA256
         and report.get("derived_source_apply_count") == 2
         and report.get("expected_v8_compiler_process_count") == 14
         and report.get("actual_v8_compiler_process_count") == 14
         and report.get("phase_count") == 2,
         "require the genuine complete successful corrected C build")
    need(receipt.get("schema")
         == "rebar-phase2-owned-native-source-build-v8-durable-publication-receipt"
         and receipt.get("status") == "PASS"
         and receipt.get("build_status") == "PASS"
         and receipt.get("family") == "c"
         and receipt.get("label") == "phase2-v8"
         and receipt.get("source_sha256") == V8["source"][1]
         and receipt.get("protocol_sha256") == V8["protocol"][1]
         and receipt.get("contract_sha256") == V8["contract"][1]
         and receipt.get("phase1_manifest_sha256") == P0[1]
         and receipt.get("archive_relative") == ARCHIVE[0]
         and receipt.get("archive_sha256") == ARCHIVE[1]
         and receipt.get("archive_bytes") == ARCHIVE[2]
         and receipt.get("uncompressed_sha256") == EXPANDED_SHA256
         and receipt.get("uncompressed_bytes") == EXPANDED_BYTES
         and receipt.get("derived_source_sha256") == DERIVED_SHA256
         and receipt.get("derived_source_apply_count") == 2
         and receipt.get("expected_v8_compiler_process_count") == 14
         and receipt.get("actual_v8_compiler_process_count") == 14,
         "reject missing, fabricated, or substituted durable C build evidence")
    published = receipt.get("archive_publication")
    synchronized = receipt.get("archive_directory_fsync")
    need(type(published) is dict
         and published.get("sha256") == archive["sha256"]
         and published.get("bytes") == archive["bytes"]
         and published.get("device") == archive["device"]
         and published.get("inode") == archive["inode"]
         and published.get("exclusive_creation") is True
         and published.get("same_inode_readback_verified") is True
         and published.get("file_fsync_completed") is True
         and type(synchronized) is dict
         and synchronized.get("completed") is True
         and (archive["device"], archive["inode"])
         != (receipt_owner["device"], receipt_owner["inode"]),
         "require two genuinely separate, synchronized evidence owners")
    for obj in (report, receipt):
        need(obj.get("candidate_correctness") == "NOT MEASURED"
             and obj.get("candidate_processes_started") == 0
             and obj.get("candidate_imports") == 0
             and obj.get("native_libraries_loaded") == 0
             and obj.get("hidden_cases_read") == 0
             and obj.get("clock_samples") == 0
             and obj.get("timing_trials_run") == 0
             and obj.get("performance") == "NOT MEASURED"
             and obj.get("memory") == "NOT MEASURED"
             and obj.get("holdout") == "NOT OPENED"
             and obj.get("winner_selected") is False,
             "a C source build is not a compatibility or speed result")
    steps = report.get("compiler_processes")
    need(type(steps) is list and len(steps) == 14,
         "require all 14 genuine successful build and inspection processes")
    pids: set[int] = set()
    for index, step in enumerate(steps):
        need(type(step) is dict
             and step.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
             and type(step.get("pid")) is int and step["pid"] > 0
             and step["pid"] not in pids and step.get("exit_status") == 0,
             "reject a missing, fake, failed, or repeated actual process")
        pids.add(step["pid"])
    phases = report.get("phases")
    need(type(phases) is list and len(phases) == 2
         and [phase.get("name") for phase in phases] == list(PHASES),
         "require both independently owned actual build phases")
    source_ids: set[tuple[int, int]] = set()
    native_ids: set[tuple[int, int]] = set()
    outputs: list[dict] = []
    source_proofs: list[dict] = []
    for index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        need(type(owners) is dict and set(owners) == {ORIGINAL[0], ADAPTER[0]},
             "require only the actual first-party C and adapter sources")
        for path, sha, count in (
            (ORIGINAL[0], DERIVED_SHA256, DERIVED_BYTES),
            (ADAPTER[0], ADAPTER[1], ADAPTER[2]),
        ):
            owner = owners.get(path)
            need(type(owner) is dict and owner.get("sha256") == sha
                 and owner.get("bytes") == count
                 and type(owner.get("device")) is int
                 and type(owner.get("inode")) is int
                 and (owner["device"], owner["inode"]) not in source_ids,
                 "reject linked or cross-phase private C source snapshots")
            source_ids.add((owner["device"], owner["inode"]))
        overlay = owners[ORIGINAL[0]].get("source_overlay")
        need(type(overlay) is dict and overlay.get("status") == "PASS"
             and overlay.get("phase") == PHASES[index]
             and overlay.get("source_apply_count") == 1
             and overlay.get("derived_sha256") == DERIVED_SHA256
             and overlay.get("derived_bytes") == DERIVED_BYTES
             and overlay.get("candidate_original_modified") is False,
             "the exact corrected source must be applied once in each phase")
        native = phase.get("native_outputs", {}).get("extension")
        need(type(native) is dict
             and native.get("file_name")
             == "_vm_native.cpython-314-x86_64-linux-gnu.so"
             and native.get("sha256") == NATIVE_SHA256
             and native.get("size_bytes") == NATIVE_BYTES
             and type(native.get("device")) is int
             and type(native.get("inode")) is int
             and (native["device"], native["inode"]) not in native_ids,
             "both actual repaired native files must have unique equal bytes")
        native_ids.add((native["device"], native["inode"]))
        audit = native.get("audit")
        need(type(audit) is dict and audit.get("role") == "extension"
             and audit.get("cross_family_dependency_count") == 0
             and audit.get("external_regex_dependency_count") == 0
             and audit.get("exports") == ["PyInit__vm_native"],
             "the corrected C native file must be independent and first-party")
        forensic = phase.get("native_forensics", {}).get("extension", {})
        raw = forensic.get("raw_elf64")
        need(type(raw) is dict
             and raw.get("format") == "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN"
             and raw.get("file_sha256") == NATIVE_SHA256
             and raw.get("file_size") == NATIVE_BYTES,
             "require complete actual raw native ELF proof for both phases")
        for kind in ("sections", "notes"):
            detail = forensic.get(kind)
            need(type(detail) is dict
                 and detail.get("command") == "extension_" + kind
                 and type(detail.get("process_pid")) is int
                 and detail["process_pid"] in pids
                 and type(detail.get("stdout_bytes")) is int
                 and detail["stdout_bytes"] >= 0,
                 "require actual independently recorded ELF inspector output")
        outputs.append(native)
        source_proofs.append({
            "name": PHASES[index],
            "source_device": owners[ORIGINAL[0]]["device"],
            "source_inode": owners[ORIGINAL[0]]["inode"],
            "adapter_device": owners[ADAPTER[0]]["device"],
            "adapter_inode": owners[ADAPTER[0]]["inode"],
            "native_device": native["device"],
            "native_inode": native["inode"],
        })
    reproduction = report.get("reproducibility")
    need(type(reproduction) is dict
         and reproduction.get("independent_fresh_phase_count") == 2
         and reproduction.get("derived_source_apply_count") == 2
         and reproduction.get("derived_source_sha256") == DERIVED_SHA256
         and reproduction.get("derived_source_bytes") == DERIVED_BYTES
         and reproduction.get("original_source_modified") is False
         and reproduction.get("byte_identical") is True
         and reproduction.get("unique_process_count") == 14
         and reproduction.get("prebuilt_artifact_count") == 0
         and reproduction.get("native_libraries_loaded") == 0,
         "the complete actual build must reproduce from independent sources")
    comparison = reproduction.get("raw_elf_comparison")
    final_native = reproduction.get("native_outputs", {}).get("extension")
    need(type(comparison) is dict
         and comparison.get("byte_identical") is True
         and comparison.get("total_differing_byte_count") == 0
         and comparison.get("total_difference_span_count") == 0
         and type(final_native) is dict
         and final_native.get("sha256") == NATIVE_SHA256
         and final_native.get("size_bytes") == NATIVE_BYTES
         and final_native.get("fresh_independent_inode_count") == 2
         and final_native.get("reproduced_in_two_fresh_directories") is True,
         "the complete two-phase native comparison must actually pass")
    return {
        "status": "PASS",
        "label": "phase2-v8",
        "phase_count": 2,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        "derived_source_apply_count": 2,
        "compiler_process_count": 14,
        "unique_compiler_process_count": len(pids),
        "process_names": [step["name"] for step in steps],
        "native_sha256": NATIVE_SHA256,
        "native_bytes": NATIVE_BYTES,
        "native_independent_inode_count": len(native_ids),
        "complete_native_elf_byte_identical": True,
        "phase_proofs": source_proofs,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "candidate_correctness": "NOT YET RETESTED",
        "candidate_activated": False,
        "canonical_native_promoted": False,
        "performance": "NOT MEASURED",
        "archive": dict(archive),
        "receipt": dict(receipt_owner),
    }


def validate_snapshot(snap: dict) -> None:
    need(type(snap) is dict
         and snap.get("full_case_denominator") == 31237
         and snap.get("suite_count") == 13
         and tuple(snap.get("suite_ids", ())) == SUITES
         and snap.get("baseline_passed") == 31237
         and snap.get("frozen_independent_engine_family_count") == 6
         and snap.get("current_source_owner_count") == 25
         and snap.get("current_tested_candidate_family_count") == 5
         and snap.get("qualified_candidate_count") == 0
         and snap.get("verified_activation_v4_actual_activation_count") == 3
         and snap.get("verified_activation_v4_current_active_target_count") == 0
         and snap.get("preserved_v19_repository_evidence_owner_count") == 71
         and snap.get("new_c_v8_repository_evidence_owner_count") == 2
         and snap.get("all_actual_candidate_and_native_evidence_owner_count") == 73
         and snap.get("preserved_v19_digest_addressed_history_path_count") == 76
         and snap.get("all_digest_addressed_history_path_count") == 78,
         "reject changed families, denominators, evidence, or activation history")
    need(snap.get("c_actual_semantic_mismatch_count") == 2094
         and snap.get("c_verified_passing_case_executions") == 7197
         and snap.get("rust_actual_semantic_mismatch_count") == 2042
         and snap.get("rust_verified_passing_case_executions") == 7461
         and snap.get("zig_actual_semantic_mismatch_count") == 1764
         and snap.get("zig_verified_passing_case_executions") == 3583,
         "reject erased C, Rust, or Zig matching failures")
    c = snap.get("c_full_gate")
    cpp = snap.get("cpp_full_original_campaign")
    go = snap.get("go_v2_full_original_campaign")
    need(type(c) is dict and c.get("gate_status") == "FAIL"
         and c.get("actual_semantic_mismatch_count") == 2094
         and c.get("qualified_candidate_count") == 0
         and type(cpp) is dict and cpp.get("status") == "FAIL"
         and cpp.get("semantic_mismatch_count") == 2308
         and cpp.get("verified_passing_case_count") == 128
         and type(go) is dict and go.get("status") == "FAIL"
         and go.get("semantic_mismatch_count") == 4518
         and go.get("infrastructure_failure_count") == 4
         and go.get("verified_passing_case_count") == 128
         and go.get("restoration_status") == "PASS",
         "reject an invented C, C++, or Go compatibility improvement")
    build = snap.get("c_v8_repaired_build")
    need(type(build) is dict and build.get("status") == "PASS"
         and build.get("label") == "phase2-v8"
         and build.get("phase_count") == 2
         and build.get("derived_source_sha256") == DERIVED_SHA256
         and build.get("derived_source_apply_count") == 2
         and build.get("compiler_process_count") == 14
         and build.get("unique_compiler_process_count") == 14
         and build.get("native_sha256") == NATIVE_SHA256
         and build.get("native_bytes") == NATIVE_BYTES
         and build.get("native_independent_inode_count") == 2
         and build.get("complete_native_elf_byte_identical") is True
         and build.get("candidate_correctness") == "NOT YET RETESTED"
         and build.get("candidate_activated") is False
         and build.get("canonical_native_promoted") is False,
         "a real reproducible C build is not a retested or activated candidate")
    existing = snap.get("existing_canonical_c_native_target")
    need(type(existing) is dict and existing.get("present") is True
         and existing.get("sha256") == EXISTING_NATIVE[1]
         and existing.get("bytes") == EXISTING_NATIVE[2]
         and existing.get("sha256") != NATIVE_SHA256
         and snap.get("repaired_c_native_promoted") is False
         and snap.get("repaired_c_full_matching_test_status") == "NOT YET RETESTED"
         and snap.get("c_v8_actual_build_process_count") == 14
         and snap.get("historical_compiler_process_count_before_v8") == 169
         and snap.get("historical_compiler_process_count_including_v8") == 183,
         "do not claim an existing canonical binary was absent or promoted")
    need(snap.get("performance") == "NOT MEASURED"
         and snap.get("memory") == "NOT MEASURED"
         and snap.get("confidence_intervals") == "NOT MEASURED"
         and snap.get("hidden_cases_read") == 0
         and snap.get("performance_files_read") == 0
         and snap.get("clock_samples") == 0
         and snap.get("timing_trials_run") == 0
         and snap.get("final_comparison_planned_case_count") == 4194304
         and snap.get("final_comparison_cases_generated") is False
         and snap.get("final_holdout_opened") is False
         and snap.get("winner_selected") is False,
         "reject invented speed, matching, clocks, winner, or opened holdout")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def make_svg(snap: dict, source_sha: str, manifest_sha: str) -> bytes:
    validate_snapshot(snap)
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1660" height="1650" viewBox="0 0 1660 1650" role="img" aria-labelledby="v20-title v20-description">',
        '<title id="v20-title">Building a faster Python re: honest compatibility and repaired C build</title>',
        '<desc id="v20-description">Python passes all 31,237 original checks. None of six replacements is yet fully compatible. The original C, Rust, Zig, C++, and Go failures are preserved. The corrected C engine was genuinely built twice with identical native bytes, but its full matching tests have not yet been rerun and its existing canonical binary has not been replaced. There are 73 distinct evidence owners. Speed, memory, and confidence are not measured, and the proposed 4,194,304-case holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:34px;font-weight:760;fill:#16324f}.heading{font-size:25px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:18px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.pending{font-size:15px;font-weight:740;fill:#53667b}.big{font-size:27px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}</style>',
        '<rect width="1660" height="1650" rx="22" fill="#f4f7fb"/>',
        '<text x="54" y="69" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="56" y="100" class="body">The C repair now builds reproducibly. Whether it matches Python is not yet known.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0 of 6", "fully compatible replacements"),
        ("2 of 2", "identical repaired C builds"),
        ("73", "actual evidence files"),
        ("NOT MEASURED", "speed and memory"),
    )
    for index, (number, label) in enumerate(cards):
        x = 54 + index * 320
        lines.extend((
            f'<rect x="{x}" y="124" width="304" height="104" rx="13" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 14}" y="168" class="big">{xml(number)}</text>',
            f'<text x="{x + 14}" y="203" class="body">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="54" y="248" width="1552" height="910" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="76" y="290" class="heading">1. Does it behave like Python?</text>',
        '<text x="77" y="318" class="body">Every last-tested result below uses the same 13 original groups and 31,237 Python checks.</text>',
    ))
    rows = (
        ("Python re", "PASSED", "31,237 of 31,237 original reference checks passed.", "pass"),
        ("C - last fully tested version", "FAILED", "7,197 verified passes; 2,094 recorded matching differences. This failure is preserved.", "fail"),
        ("C repair - new reproducible build", "NOT YET RETESTED", "Built twice with identical first-party native bytes; full matching and speed have not been tested.", "pending"),
        ("Rust", "FAILED", "7,461 verified passes; 2,042 recorded matching differences.", "fail"),
        ("Zig", "FAILED", "3,583 verified passes; 1,764 recorded matching differences.", "fail"),
        ("C++", "FAILED", "128 verified passes; 2,308 recorded matching differences and five infrastructure failures.", "fail"),
        ("Go", "FAILED", "128 verified passes; 4,518 recorded matching differences and four infrastructure failures.", "fail"),
        ("Fortran", "NOT READY", "Its two native builds differed; matching remains NOT MEASURED.", "pending"),
    )
    for index, (name, outcome, detail, category) in enumerate(rows):
        y = 343 + index * 84
        lines.extend((
            f'<rect x="75" y="{y}" width="1510" height="73" rx="9" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="94" y="{y + 27}" class="name">{xml(name)}</text>',
            f'<text x="1564" y="{y + 27}" class="{category}" text-anchor="end">{xml(outcome)}</text>',
            f'<text x="96" y="{y + 54}" class="body">{xml(detail)}</text>',
        ))
    lines.extend((
        '<text x="77" y="1047" class="body">No repaired C candidate has been activated or run. The different existing canonical C binary remains in place.</text>',
        '<text x="77" y="1076" class="body">All five previous failed matching results remain unchanged; 0 of 6 replacements is qualified.</text>',
        '<text x="77" y="1105" class="body">73 actual evidence owners = 71 previous owners + the new build report and receipt.</text>',
        '<rect x="54" y="1176" width="1552" height="278" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="76" y="1219" class="heading">2. Is it faster than Python?</text>',
        '<text x="78" y="1250" class="body">NOT MEASURED. No candidate speed, memory result, confidence interval, or ranking exists.</text>',
        '<text x="78" y="1285" class="body">A successful build proves that the C source compiles; it does not prove matching, safety, or speed.</text>',
        '<text x="78" y="1320" class="body">The proposed 4,194,304-case final comparison has not been generated or opened.</text>',
        '<text x="78" y="1355" class="body">The next step is to retest the repaired C build against all 31,237 frozen checks.</text>',
        '<text x="78" y="1390" class="body">Recorded build: 2 fresh private phases, 14 actual processes, identical native bytes.</text>',
        f'<text x="58" y="1502" class="foot">Inputs SHA-256: {xml(manifest_sha)}</text>',
        f'<text x="58" y="1528" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="58" y="1554" class="foot">C build archive SHA-256: {ARCHIVE[1]}</text>',
        f'<text x="58" y="1580" class="foot">C build receipt SHA-256: {RECEIPT[1]}</text>',
        '</svg>',
        '',
    ))
    return "\n".join(lines).encode("utf-8")


def authenticate(source_sha: str, archive_sha: str,
                 receipt_sha: str) -> tuple[dict, dict, dict]:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode
         and sys.executable == PYTHON,
         "use only isolated pinned CPython 3.14.6")
    read_owner(SELF, checked_digest(source_sha, "V20 renderer"))
    need(archive_sha == ARCHIVE[1] and receipt_sha == RECEIPT[1],
         "caller must independently pin both actual corrected-C evidence owners")
    previous_raw: dict[str, bytes] = {}
    for name, (path, sha) in PRIOR.items():
        previous_raw[name], _ = read_owner(path, sha)
    inputs = document(previous_raw["inputs"], "V19 inputs")
    old = document(previous_raw["summary"], "V19 summary")
    validate_v19(old, inputs)
    p0_raw, _ = read_owner(*P0)
    p0 = document(p0_raw, "original P0")
    denominator = p0.get("denominator")
    gate = p0.get("phase_gate")
    need(type(denominator) is dict
         and denominator.get("final_required_case_execution_denominator") == 31237
         and denominator.get("private_upstream_methods_outside_public_denominator") == 13
         and tuple(denominator.get("counted_suite_ids", ())) == SUITES
         and type(gate) is dict and gate.get("status") == "PASS"
         and gate.get("final_holdout_authorized") is False,
         "the original 13-suite, 31,237-case, 13-waiver oracle changed")
    v7_raw, _ = read_owner(*V7)
    v7 = document(v7_raw, "V7 owners")
    need(v7.get("family_count") == 6 and v7.get("source_owner_count") == 25,
         "the six independent first-party families changed")
    owners: set[str] = set()
    for family in v7.get("families", []):
        need(type(family) is dict and type(family.get("owners")) is list,
             "invalid original source family")
        for owner in family["owners"]:
            need(type(owner) is dict and type(owner.get("path")) is str
                 and owner["path"] not in owners,
                 "missing or repeated original candidate source owner")
            read_owner(owner["path"], owner["sha256"], size=owner["bytes"])
            owners.add(owner["path"])
    need(len(owners) == 25, "authenticate all 25 independent original owners")
    read_owner(ORIGINAL[0], ORIGINAL[1], size=ORIGINAL[2])
    read_owner(ADAPTER[0], ADAPTER[1], size=ADAPTER[2])
    original_native_raw, original_native_owner = read_owner(
        EXISTING_NATIVE[0], EXISTING_NATIVE[1], size=EXISTING_NATIVE[2],
    )
    need(digest(original_native_raw) != NATIVE_SHA256,
         "the existing canonical native target was incorrectly promoted")
    for path, sha in V8.values():
        read_owner(path, sha)
    history: dict[str, str] = {}
    discover_history(inputs, history)
    discover_history(old, history)
    need(len(history) == 76, "the prior 76-reference history was changed")
    for path, sha in sorted(history.items()):
        read_owner(path, sha)
    need(ARCHIVE[0] not in history and RECEIPT[0] not in history,
         "the two real new owners were already counted")
    compressed, archive_owner = read_owner(
        ARCHIVE[0], archive_sha, size=ARCHIVE[2], private=True,
    )
    receipt_raw, receipt_owner = read_owner(
        RECEIPT[0], receipt_sha, size=RECEIPT[2], private=True,
    )
    receipt = document(receipt_raw, "actual V8 durable receipt")
    try:
        expanded = gzip.decompress(compressed)
    except (EOFError, OSError, gzip.BadGzipFile) as error:
        raise GraphError("invalid actual bounded C build archive") from error
    need(len(expanded) == EXPANDED_BYTES
         and len(expanded) <= MAX_REPORT
         and digest(expanded) == EXPANDED_SHA256
         and gzip.compress(expanded, compresslevel=9, mtime=0) == compressed,
         "the actual complete C build report is not one deterministic archive")
    report = document(expanded, "actual full C build report")
    proof = validate_actual_build(report, receipt, archive_owner, receipt_owner)
    snap = copy.deepcopy(old["snapshot"])
    snap.update({
        "preserved_v19_repository_evidence_owner_count": 71,
        "new_c_v8_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 73,
        "preserved_v19_digest_addressed_history_path_count": 76,
        "all_digest_addressed_history_path_count": 78,
        "historical_compiler_process_count_before_v8": 169,
        "c_v8_actual_build_process_count": 14,
        "historical_compiler_process_count_including_v8": 183,
        "c_v8_repaired_build": proof,
        "repaired_c_full_matching_test_status": "NOT YET RETESTED",
        "repaired_c_native_promoted": False,
        "existing_canonical_c_native_target": {
            "path": EXISTING_NATIVE[0],
            "sha256": original_native_owner["sha256"],
            "bytes": original_native_owner["bytes"],
            "device": original_native_owner["device"],
            "inode": original_native_owner["inode"],
            "present": True,
            "is_repaired_v8_native": False,
        },
    })
    validate_snapshot(snap)
    return old, snap, proof


def build(source_sha: str, archive_sha: str,
          receipt_sha: str) -> tuple[dict, dict, tuple[tuple[str, bytes], ...]]:
    old, snap, proof = authenticate(source_sha, archive_sha, receipt_sha)
    manifest = {
        "schema": SCHEMA + "-inputs",
        "version": 20,
        "python": "3.14.6",
        "renderer": pin(SELF, source_sha),
        "previous_overview": {
            name: pin(path, sha) for name, (path, sha) in sorted(PRIOR.items())
        },
        "frozen_c_v8_build": {
            name: pin(path, sha) for name, (path, sha) in sorted(V8.items())
        },
        "actual_c_v8_build": {
            "label": "phase2-v8",
            "archive": pin(ARCHIVE[0], archive_sha, ARCHIVE[2]),
            "receipt": pin(RECEIPT[0], receipt_sha, RECEIPT[2]),
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_bytes": DERIVED_BYTES,
            "actual_phase_count": 2,
            "actual_compiler_process_count": 14,
            "native_sha256": NATIVE_SHA256,
            "native_bytes": NATIVE_BYTES,
            "native_fresh_inode_count": 2,
            "matching_test_status": "NOT YET RETESTED",
            "candidate_activated": False,
            "canonical_native_promoted": False,
        },
        "existing_canonical_c_native": pin(*EXISTING_NATIVE),
        "original_correctness_manifest": pin(*P0),
        "original_source_freeze": pin(*V7),
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "candidate_families": ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "candidate_qualified_count": 0,
        "preserved_v19_repository_evidence_owner_count": 71,
        "new_c_v8_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": 73,
        "preserved_v19_digest_addressed_history_path_count": 76,
        "all_digest_addressed_history_path_count": 78,
        "historical_compiler_process_count_before_v8": 169,
        "actual_v8_compiler_process_count": 14,
        "historical_compiler_process_count_including_v8": 183,
        "verified_activation_v4_actual_activation_count": 3,
        "verified_activation_v4_current_active_target_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    manifest_raw = canonical(manifest)
    manifest_sha = digest(manifest_raw)
    svg = make_svg(snap, source_sha, manifest_sha)
    families = copy.deepcopy(old["families"])
    for row in families:
        if row.get("family") == "c":
            row["current_repaired_build"] = copy.deepcopy(proof)
            row["current_repaired_matching_test_status"] = "NOT YET RETESTED"
            row["current_repaired_candidate_activated"] = False
            row["current_repaired_canonical_native_promoted"] = False
    summary = {
        "schema": SCHEMA + "-summary",
        "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_sha),
        "inputs": pin(OUTPUT + ".inputs.json", manifest_sha),
        "svg": pin(OUTPUT + ".svg", digest(svg)),
        "previous_overview": {
            name: pin(path, sha) for name, (path, sha) in sorted(PRIOR.items())
        },
        "snapshot": snap,
        "families": families,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "repository_evidence_owner_count": 73,
        "authenticated_digest_addressed_history_paths": 78,
        "qualified_candidate_count": 0,
        "verified_activation_v4_current_active_target_count": 0,
        "historical_compiler_process_count_before_v8": 169,
        "actual_v8_compiler_process_count": 14,
        "historical_compiler_process_count_including_v8": 183,
        "c_repaired_build_status": "PASS",
        "c_repaired_matching_test_status": "NOT YET RETESTED",
        "c_repaired_native_promoted": False,
        "existing_canonical_native_present": True,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    return manifest, snap, (
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
            raise GraphError("source-only graph effect blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "unlink", "remove", "replace", "rename",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "mkdir", "unlink",
                    "rename", "replace", "resolve")),
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

    def __exit__(self, _type: object, _value: object,
                 _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_snapshot() -> dict:
    return {
        "full_case_denominator": 31237,
        "suite_count": 13,
        "suite_ids": list(SUITES),
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "qualified_candidate_count": 0,
        "verified_activation_v4_actual_activation_count": 3,
        "verified_activation_v4_current_active_target_count": 0,
        "preserved_v19_repository_evidence_owner_count": 71,
        "new_c_v8_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 73,
        "preserved_v19_digest_addressed_history_path_count": 76,
        "all_digest_addressed_history_path_count": 78,
        "c_actual_semantic_mismatch_count": 2094,
        "c_verified_passing_case_executions": 7197,
        "rust_actual_semantic_mismatch_count": 2042,
        "rust_verified_passing_case_executions": 7461,
        "zig_actual_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_executions": 3583,
        "c_full_gate": {
            "gate_status": "FAIL", "actual_semantic_mismatch_count": 2094,
            "qualified_candidate_count": 0,
        },
        "cpp_full_original_campaign": {
            "status": "FAIL", "semantic_mismatch_count": 2308,
            "verified_passing_case_count": 128,
        },
        "go_v2_full_original_campaign": {
            "status": "FAIL", "semantic_mismatch_count": 4518,
            "infrastructure_failure_count": 4,
            "verified_passing_case_count": 128,
            "restoration_status": "PASS",
        },
        "c_v8_repaired_build": {
            "status": "PASS", "label": "phase2-v8", "phase_count": 2,
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_apply_count": 2,
            "compiler_process_count": 14,
            "unique_compiler_process_count": 14,
            "native_sha256": NATIVE_SHA256,
            "native_bytes": NATIVE_BYTES,
            "native_independent_inode_count": 2,
            "complete_native_elf_byte_identical": True,
            "candidate_correctness": "NOT YET RETESTED",
            "candidate_activated": False,
            "canonical_native_promoted": False,
        },
        "existing_canonical_c_native_target": {
            "present": True, "sha256": EXISTING_NATIVE[1],
            "bytes": EXISTING_NATIVE[2],
        },
        "repaired_c_native_promoted": False,
        "repaired_c_full_matching_test_status": "NOT YET RETESTED",
        "c_v8_actual_build_process_count": 14,
        "historical_compiler_process_count_before_v8": 169,
        "historical_compiler_process_count_including_v8": 183,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def self_test() -> dict:
    accepted = 0
    rejected = 0
    with SourceOnlyWall() as wall:
        snap = synthetic_snapshot()
        validate_snapshot(snap)
        accepted += 1
        picture = make_svg(snap, digest(b"synthetic-v20-renderer"),
                           digest(b"synthetic-v20-manifest"))
        for phrase in (
            b'role="img"', b'aria-labelledby="v20-title v20-description"',
            b"31,237", b"0 of 6", b"2 of 2", b"73",
            b"2,094", b"2,042", b"1,764", b"2,308", b"4,518",
            b"NOT YET RETESTED", b"NOT MEASURED", b"4,194,304",
            b"canonical C binary remains in place",
        ):
            need(phrase in picture, "truthful accessible headline is missing")
            accepted += 1

        def reject(callback: object, description: str) -> None:
            nonlocal rejected
            try:
                callback()  # type: ignore[operator]
            except (GraphError, OSError, TypeError, ValueError,
                    UnicodeError, OverflowError):
                rejected += 1
            else:
                raise GraphError("accepted forged graph control: " + description)

        mutations = (
            ("full_case_denominator", 31236), ("suite_count", 12),
            ("suite_ids", list(SUITES[:-1])), ("baseline_passed", 31236),
            ("frozen_independent_engine_family_count", 5),
            ("current_source_owner_count", 24),
            ("current_tested_candidate_family_count", 6),
            ("qualified_candidate_count", 1),
            ("verified_activation_v4_actual_activation_count", 4),
            ("verified_activation_v4_current_active_target_count", 1),
            ("preserved_v19_repository_evidence_owner_count", 70),
            ("new_c_v8_repository_evidence_owner_count", 1),
            ("all_actual_candidate_and_native_evidence_owner_count", 72),
            ("preserved_v19_digest_addressed_history_path_count", 75),
            ("all_digest_addressed_history_path_count", 77),
            ("c_actual_semantic_mismatch_count", 2093),
            ("c_verified_passing_case_executions", 7198),
            ("rust_actual_semantic_mismatch_count", 2041),
            ("rust_verified_passing_case_executions", 7462),
            ("zig_actual_semantic_mismatch_count", 1763),
            ("zig_verified_passing_case_executions", 3584),
            ("repaired_c_native_promoted", True),
            ("repaired_c_full_matching_test_status", "PASS"),
            ("c_v8_actual_build_process_count", 13),
            ("historical_compiler_process_count_before_v8", 168),
            ("historical_compiler_process_count_including_v8", 182),
            ("performance", "PASS"), ("memory", "PASS"),
            ("confidence_intervals", "PASS"), ("hidden_cases_read", 1),
            ("performance_files_read", 1), ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("final_comparison_planned_case_count", 4194303),
            ("final_comparison_cases_generated", True),
            ("final_holdout_opened", True), ("winner_selected", True),
        )
        for key, changed in mutations:
            forged = copy.deepcopy(snap)
            forged[key] = changed
            reject(lambda value=forged: validate_snapshot(value), key)
        for container, changes in (
            ("c_full_gate", (("gate_status", "PASS"),
                             ("actual_semantic_mismatch_count", 2093),
                             ("qualified_candidate_count", 1))),
            ("cpp_full_original_campaign", (("status", "PASS"),
                                             ("semantic_mismatch_count", 2307),
                                             ("verified_passing_case_count", 129))),
            ("go_v2_full_original_campaign", (("status", "PASS"),
                                               ("semantic_mismatch_count", 4517),
                                               ("infrastructure_failure_count", 3),
                                               ("verified_passing_case_count", 129),
                                               ("restoration_status", "FAIL"))),
            ("c_v8_repaired_build", (("status", "FAIL"), ("label", "fake"),
                                     ("phase_count", 1),
                                     ("derived_source_sha256", "0" * 64),
                                     ("derived_source_apply_count", 1),
                                     ("compiler_process_count", 13),
                                     ("unique_compiler_process_count", 13),
                                     ("native_sha256", "0" * 64),
                                     ("native_bytes", NATIVE_BYTES - 1),
                                     ("native_independent_inode_count", 1),
                                     ("complete_native_elf_byte_identical", False),
                                     ("candidate_correctness", "PASS"),
                                     ("candidate_activated", True),
                                     ("canonical_native_promoted", True))),
            ("existing_canonical_c_native_target", (("present", False),
                                                     ("sha256", NATIVE_SHA256),
                                                     ("bytes", NATIVE_BYTES))),
        ):
            for key, changed in changes:
                forged = copy.deepcopy(snap)
                forged[container][key] = changed
                reject(lambda value=forged: validate_snapshot(value),
                       container + "." + key)
        for hostile in ("", "/absolute", "../escape", "a/../b", "a//b",
                        "./owner", "a/", "a\\b", "a" * 513):
            reject(lambda path=hostile: checked_path(path), "unsafe path")
        for hostile in ("", "0" * 63, "0" * 65, "A" * 64, "g" * 64):
            reject(lambda sha=hostile: checked_digest(sha, "hostile"),
                   "unsafe digest")
        for hostile in (b'{"a":1,"a":2}\n', b'{"a":NaN}\n', b"[]\n"):
            reject(lambda raw=hostile: document(raw, "hostile"),
                   "forged canonical JSON")
        effects = (
            (lambda: builtins.open("/tmp/forbidden"), "file read"),
            (lambda: os.open("/tmp/forbidden", os.O_RDONLY), "descriptor"),
            (lambda: os.write(1, b"x"), "graph write"),
            (lambda: Path("/tmp/forbidden").write_bytes(b"x"), "file write"),
            (lambda: subprocess.run(("true",)), "compiler process"),
            (lambda: socket.socket(), "network"),
            (lambda: importlib.import_module("candidates.vm_candidate"),
             "candidate import"),
            (lambda: importlib.import_module("re"), "reference import"),
            (lambda: tempfile.mkdtemp(), "build root"),
            (lambda: threading.Thread().start(), "thread"),
            (lambda: time.perf_counter(), "performance clock"),
            (lambda: time.time(), "wall clock"),
        )
        for callback, label in effects:
            reject(callback, label)
        blocked = wall.blocked
        need(blocked == len(effects), "source-only graph effects escaped")
        need(rejected >= 75, "require substantial hostile evidence controls")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "version": 20,
        "synthetic_acceptance_count": accepted,
        "synthetic_rejection_count": rejected,
        "blocked_effect_controls": blocked,
        "repository_evidence_owner_count": 73,
        "authenticated_digest_addressed_history_paths": 78,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "qualified_candidate_count": 0,
        "actual_source_reads": 0,
        "actual_evidence_reads": 0,
        "actual_output_writes": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
        "synthetic_svg_sha256": digest(picture),
    }


def publish_output(path: str, raw: bytes, *, verify: bool) -> None:
    parts = checked_path(path)
    need(parts[:2] == ("docs", "evidence"),
         "graph output escaped its exclusive directory")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    try:
        fd = os.open(str(ROOT / path), flags)
    except FileNotFoundError:
        need(not verify, "missing already published reproducible graph")
        fd = os.open(str(ROOT / path),
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | os.O_CLOEXEC | os.O_NOFOLLOW, 0o644)
        try:
            offset = 0
            while offset < len(raw):
                wrote = os.write(fd, raw[offset:])
                need(type(wrote) is int and wrote > 0,
                     "incomplete exclusive graph output")
                offset += wrote
            os.fsync(fd)
        finally:
            os.close(fd)
        read_owner(path, digest(raw), size=len(raw))
        return
    try:
        info = os.fstat(fd)
        need(stat.S_ISREG(info.st_mode) and info.st_size == len(raw),
             "never overwrite a pre-existing changed graph")
        pieces: list[bytes] = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(fd, min(remaining, 1024 * 1024))
            need(bool(chunk), "truncated previously published graph")
            pieces.append(chunk)
            remaining -= len(chunk)
        need(os.read(fd, 1) == b"" and b"".join(pieces) == raw,
             "never replace an independently owned existing graph")
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-inputs", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--v8-archive-sha256")
    parser.add_argument("--v8-receipt-sha256")
    parser.add_argument("--manifest-sha256")
    args = parser.parse_args()
    try:
        if args.self_test:
            need(args.source_sha256 is None and args.v8_archive_sha256 is None
                 and args.v8_receipt_sha256 is None
                 and args.manifest_sha256 is None,
                 "synthetic source-only checks must not touch real owners")
            result = self_test()
            sys.stdout.buffer.write(canonical(result))
            return 0
        source = checked_digest(args.source_sha256, "V20 renderer")
        archive = checked_digest(args.v8_archive_sha256, "actual V8 archive")
        receipt = checked_digest(args.v8_receipt_sha256, "actual V8 receipt")
        manifest, snapshot, outputs = build(source, archive, receipt)
        manifest_raw = outputs[0][1]
        manifest_sha = digest(manifest_raw)
        if args.emit_inputs:
            need(args.manifest_sha256 is None,
                 "input emission cannot assume an existing graph")
            sys.stdout.buffer.write(manifest_raw)
            return 0
        supplied = checked_digest(args.manifest_sha256, "V20 inputs")
        need(supplied == manifest_sha,
             "caller must pin the exact complete deterministic input manifest")
        for path, raw in outputs:
            publish_output(path, raw, verify=args.verify)
        result = {
            "schema": SCHEMA + ("-verified" if args.verify else "-rendered"),
            "status": "PASS", "version": 20,
            "source_sha256": source,
            "inputs_sha256": manifest_sha,
            "svg_sha256": digest(outputs[1][1]),
            "summary_sha256": digest(outputs[2][1]),
            "v8_build_archive_sha256": archive,
            "v8_build_receipt_sha256": receipt,
            "repository_evidence_owner_count": 73,
            "authenticated_digest_addressed_history_paths": 78,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "candidate_family_count": 6,
            "qualified_candidate_count": 0,
            "c_repaired_build_status": "PASS",
            "c_repaired_matching_test_status": "NOT YET RETESTED",
            "actual_c_v8_compiler_process_count": 14,
            "existing_canonical_native_present": True,
            "repaired_c_native_promoted": False,
            "verified_activation_v4_current_active_target_count": 0,
            "outputs_written": not args.verify,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "winner_selected": False,
        }
        validate_snapshot(snapshot)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GraphError, OSError, ValueError, TypeError,
            EOFError, gzip.BadGzipFile) as error:
        sys.stderr.write("current V20 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
