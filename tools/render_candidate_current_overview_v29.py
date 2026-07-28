#!/usr/bin/env python3
"""Show actual C source-build progress without claiming untested compatibility."""
from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_candidate_current_overview_v29.py"
OUTPUT = "docs/evidence/candidate-current-overview-v29"
SCHEMA = "rebar-candidate-current-overview-v29"
LIMIT = 8 * 1024 * 1024
V28 = {
    "source": ("tools/render_candidate_current_overview_v28.py", "bd0f3311157128dcb4d9d17e79353bbd73d50ad08a61cce8bde65b17beef08bf", 53951),
    "inputs": ("docs/evidence/candidate-current-overview-v28.inputs.json", "6d64de8b7b364afd1281d0c4be2a444bf7146a2a232df4c8bc27dd77895dc97d", 43879),
    "summary": ("docs/evidence/candidate-current-overview-v28.json", "8ec3034aff9c4830686a6946f340be729f2eb2b606b74cdf18c9a7f816a0d754", 232881),
    "svg": ("docs/evidence/candidate-current-overview-v28.svg", "dd78e23ad42599da713f2f204967f981ce694f91e4e70a8da341b7aa91f9c597", 12961),
}
C_ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v15-c-phase2-v15-c-pickle-original-p0.json.gz",
    "7e95decc5937b76b2f1aa86706663a57edcea8d3a705ad9b3710c4ec2b61a4de",
    41716,
    2064,
    524634,
)
C_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v15-c-phase2-v15-c-pickle-original-p0-publication-receipt.json",
    "ad196290f8f08b1547ffefc02bd1cdaff52557f792b8a32ea93c67f6ee857643",
    4052,
    2064,
    524635,
)
C_PLAIN_SHA = "55faf4490917b60c174fe120419f64fea2bc9171f4321f880bd89172b6b1693a"
C_PLAIN_BYTES = 322399
C_NATIVE_SHA = "aed6e9c2fbe31ee3798c74bc6fe896494f1a3bfed41ff25dcfef6905e7b8e610"
C_NATIVE_BYTES = 163176
C_PHASE_INODES = (10601081, 10601084)
C_PROCESS_NAMES = frozenset((
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
))
RUST_JOURNAL = "b28862fc1433af8c2897299cf6d64fb672f452f011c68fe887714dc09b60ea65"


class GraphError(Exception):
    """Reject a missing, misleading, substituted, or unsafe graph input."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only exact evidence bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V29 evidence") from error


def checked(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value), "pin " + label)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6) and sys.flags.isolated == 1 and sys.dont_write_bytecode is True and os.path.realpath(sys.executable) == PYTHON, "require exact isolated stable CPython 3.14.6")


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        result: dict[str, object] = {}
        for key, value in items:
            need(key not in result, "reject duplicate JSON key in " + label)
            result[key] = value
        return result
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(GraphError("reject nonfinite JSON in " + label)))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed JSON in " + label) from error
    need(type(obj) is dict and canonical(obj) == raw, "require canonical " + label)
    return obj


def read_owner(path: str, fingerprint: str, size: int | None = None, *, private: bool = False, device: int | None = None, inode: int | None = None) -> tuple[bytes, dict]:
    need(type(path) is str and bool(path) and not path.startswith("/") and ".." not in Path(path).parts, "require exact relative owner")
    checked(fingerprint, path)
    fd = os.open(str(ROOT / path), os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 <= before.st_size <= LIMIT and (size is None or before.st_size == size) and (not private or stat.S_IMODE(before.st_mode) == 0o600) and (device is None or before.st_dev == device) and (inode is None or before.st_ino == inode), "reject changed, linked, or substituted owner " + path)
        remaining = before.st_size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(fd, min(remaining, 1024 * 1024))
            need(bool(piece), "reject truncated owner " + path)
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(fd, 1) == b"", "reject trailing bytes in " + path)
        raw = b"".join(pieces)
        after = os.fstat(fd)
        need((before.st_dev, before.st_ino, before.st_size, before.st_nlink) == (after.st_dev, after.st_ino, after.st_size, after.st_nlink) and digest(raw) == fingerprint, "reject owner changed during authentication " + path)
        return raw, {"path": path, "sha256": fingerprint, "bytes": len(raw), "device": after.st_dev, "inode": after.st_ino, "mode": f"{stat.S_IMODE(after.st_mode):04o}", "nlink": after.st_nlink, "uid": after.st_uid}
    finally:
        os.close(fd)


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT, "bound actual graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def load_v28() -> types.ModuleType:
    raw, _ = read_owner(*V28["source"])
    previous = types.ModuleType("_rebar_exact_v28_for_actual_c15_graph_v29")
    previous.__file__ = str(ROOT / V28["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    need(previous.SCHEMA == "rebar-candidate-current-overview-v28" and previous.SELF == V28["source"][0], "authenticate exact committed V28 renderer")
    return previous


def authenticate_v28() -> tuple[types.ModuleType, dict, dict, dict[str, str]]:
    previous = load_v28()
    _v27, _v27_summary, _v27_inputs, references = previous.authenticate_v27()
    rust, added = previous.authenticate_rust(previous.ARCHIVE[1], previous.RECEIPT[1], references)
    need(len(references) == 148 and len(added) == 2 and not (set(references) & set(added)), "reproduce independently authenticated V28 actual Rust evidence")
    references = dict(references)
    references.update(added)
    need(len(references) == 150, "derive 150 preserved actual V28 references")
    owners: dict[str, bytes] = {}
    for key, frozen in sorted(V28.items()):
        owners[key], _ = read_owner(*frozen)
    old = document(owners["summary"], "exact actual V28 summary")
    inputs = document(owners["inputs"], "exact actual V28 inputs")
    snapshot = old.get("snapshot")
    need(type(snapshot) is dict, "preserve exact full V28 snapshot")
    previous.validate(snapshot)
    need(old.get("schema") == previous.SCHEMA + "-summary" and old.get("status") == "PASS" and old.get("repository_evidence_owner_count") == 145 and old.get("authenticated_digest_addressed_history_paths") == 150 and old.get("full_case_denominator") == 31237 and old.get("suite_count") == 13 and old.get("qualified_candidate_count") == 0 and old.get("rust_original_campaign_status") == "FAIL" and old.get("rust_original_campaign_semantic_mismatch_count") == 1087 and old.get("rust_original_campaign_verified_passing_case_count") == 7438 and old.get("rust_original_campaign_recovery_journal_sha256") == RUST_JOURNAL and old.get("actual_rust_original_campaign") == rust and old.get("zig_original_campaign_status") == "FAIL" and old.get("zig_original_campaign_semantic_mismatch_count") == 2172 and old.get("zig_original_campaign_verified_passing_case_count") == 2847 and old.get("c_repaired_semantic_mismatch_count") == 1262 and old.get("c_repaired_verified_passing_case_count") == 7325 and inputs.get("repository_evidence_owner_count") == 145 and inputs.get("all_digest_addressed_history_path_count") == 150 and owners["svg"] == previous.make_svg(snapshot, V28["source"][1], V28["inputs"][1]), "independently reproduce all four V28 owners and genuine C, Rust, and Zig matching failures")
    return previous, old, inputs, references


def inflate_only_small_c_archive(raw: bytes) -> bytes:
    need(len(raw) == C_ARCHIVE[2] and raw[:3] == b"\x1f\x8b\x08" and struct.unpack("<I", raw[4:8])[0] == 0 and struct.unpack("<I", raw[-4:])[0] == C_PLAIN_BYTES, "authenticate exact bounded small C source-build gzip before decoding")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    result = decoder.decompress(raw, C_PLAIN_BYTES + 1)
    need(decoder.eof is True and decoder.unconsumed_tail == b"" and decoder.unused_data == b"" and len(result) == C_PLAIN_BYTES and digest(result) == C_PLAIN_SHA, "reject excess, truncated, concatenated, or substituted 322,399-byte C source evidence")
    return result


def authenticate_c15(archive_sha: str, receipt_sha: str, previous: dict, refs: dict[str, str]) -> tuple[dict, dict[str, str]]:
    need(checked(archive_sha, "actual C source-build archive") == C_ARCHIVE[1] and checked(receipt_sha, "actual C source-build receipt") == C_RECEIPT[1], "caller-pin both actual C15 evidence owners")
    compressed, archive_owner = read_owner(C_ARCHIVE[0], archive_sha, C_ARCHIVE[2], private=True, device=C_ARCHIVE[3], inode=C_ARCHIVE[4])
    receipt_raw, receipt_owner = read_owner(C_RECEIPT[0], receipt_sha, C_RECEIPT[2], private=True, device=C_RECEIPT[3], inode=C_RECEIPT[4])
    need((archive_owner["device"], archive_owner["inode"]) != (receipt_owner["device"], receipt_owner["inode"]) and archive_owner["uid"] == receipt_owner["uid"] == 1000 and archive_owner["path"] not in refs and receipt_owner["path"] not in refs, "derive two distinct new actual C source-build evidence owners")
    receipt = document(receipt_raw, "actual C15 durable source-build receipt")
    publication = receipt.get("archive_publication")
    directory = receipt.get("archive_directory_fsync")
    need(type(publication) is dict and type(directory) is dict and receipt.get("schema") == "rebar-phase2-owned-c-pickle-source-build-v15-durable-publication-receipt" and receipt.get("version") == 15 and receipt.get("family") == "c" and receipt.get("label") == "phase2-v15-c-pickle-original-p0" and receipt.get("status") == "PASS" and receipt.get("build_status") == "PASS" and receipt.get("candidate_correctness") == "NOT MEASURED" and receipt.get("archive_relative") == C_ARCHIVE[0] and receipt.get("archive_sha256") == archive_owner["sha256"] and receipt.get("archive_bytes") == archive_owner["bytes"] and publication.get("path") == str(ROOT / C_ARCHIVE[0]) and publication.get("sha256") == archive_owner["sha256"] and publication.get("bytes") == archive_owner["bytes"] and publication.get("device") == archive_owner["device"] and publication.get("inode") == archive_owner["inode"] and publication.get("exclusive_creation") is True and publication.get("file_fsync_completed") is True and publication.get("same_inode_readback_verified") is True and type(publication.get("write_calls")) is int and publication["write_calls"] > 0 and directory.get("completed") is True, "authenticate genuine durable C15 source-build publication without confusing build with matching")
    rust = previous["actual_rust_original_campaign"]
    zig = previous["actual_zig_original_campaign"]
    need(receipt.get("actual_source_apply_count") == 2 and receipt.get("expected_source_apply_count") == 2 and receipt.get("actual_compiler_process_count") == 14 and receipt.get("expected_compiler_process_count") == 14 and receipt.get("current_v28_repository_evidence_owner_count") == 145 and receipt.get("current_v28_authenticated_reference_count") == 150 and receipt.get("historical_c_semantic_mismatch_count") == 1262 and receipt.get("historical_zig_preflight_candidate_worker_count") == 0 and receipt.get("actual_complete_rust_candidate_status") == "FAIL" and receipt.get("actual_complete_rust_candidate_worker_count") == 13 and receipt.get("actual_complete_rust_completed_suite_count") == 13 and receipt.get("actual_complete_rust_semantic_mismatch_count") == 1087 and receipt.get("actual_complete_rust_verified_passing_case_count") == 7438 and receipt.get("actual_complete_rust_infrastructure_failure_count") == 0 and receipt.get("actual_complete_rust_recovery_journal_sha256") == RUST_JOURNAL and receipt.get("actual_complete_rust_failure_archive_sha256") == rust["archive"]["sha256"] and receipt.get("actual_complete_rust_failure_receipt_sha256") == rust["receipt"]["sha256"] and receipt.get("actual_complete_zig_candidate_status") == "FAIL" and receipt.get("actual_complete_zig_candidate_worker_count") == 13 and receipt.get("actual_complete_zig_semantic_mismatch_count") == 2172 and receipt.get("actual_complete_zig_failure_archive_sha256") == zig["archive"]["sha256"] and receipt.get("actual_complete_zig_failure_receipt_sha256") == zig["receipt"]["sha256"], "preserve actual prior Rust and Zig failures, zero-worker Zig preflight, and exact prior evidence counts")
    need(receipt.get("uncompressed_bytes") == C_PLAIN_BYTES and receipt.get("uncompressed_sha256") == C_PLAIN_SHA and receipt.get("candidate_imports") == 0 and receipt.get("candidate_processes_started") == 0 and receipt.get("native_libraries_loaded") == 0 and receipt.get("hidden_cases_read") == 0 and receipt.get("clock_samples") == 0 and receipt.get("timing_trials_run") == 0 and receipt.get("uncompressed_rust_archive_opened") is False and receipt.get("uncompressed_rust_archive_bytes_read") == 0 and receipt.get("uncompressed_zig_archive_opened") is False and receipt.get("uncompressed_zig_archive_bytes_read") == 0 and receipt.get("performance") == "NOT MEASURED" and receipt.get("memory") == "NOT MEASURED" and receipt.get("holdout") == "NOT OPENED" and receipt.get("winner_selected") is False, "reject actual C candidate activation, holdout access, measurements, or large-archive inflation")
    raw = inflate_only_small_c_archive(compressed)
    actual = document(raw, "bounded actual 322,399-byte C15 source-build archive")
    phases = actual.get("phases")
    processes = actual.get("compiler_processes")
    reproducibility = actual.get("reproducibility")
    need(type(phases) is list and len(phases) == 2 and type(processes) is list and len(processes) == 14 and type(reproducibility) is dict and actual.get("schema") == "rebar-phase2-owned-c-pickle-source-build-v15-actual-native-build" and actual.get("version") == 15 and actual.get("status") == "PASS" and actual.get("family") == "c" and actual.get("label") == receipt["label"] and actual.get("phase_count") == 2 and actual.get("source_apply_count") == 2 and actual.get("actual_compiler_process_count") == 14 and actual.get("candidate_correctness") == "NOT MEASURED" and actual.get("candidate_imports") == 0 and actual.get("candidate_processes_started") == 0 and actual.get("native_libraries_loaded") == 0 and actual.get("historical_c_semantic_mismatch_count") == 1262 and actual.get("actual_complete_rust_semantic_mismatch_count") == 1087 and actual.get("actual_complete_zig_semantic_mismatch_count") == 2172, "require actual full archive, not receipt-reported observations")
    need(reproducibility.get("status") == "PASS" and reproducibility.get("phase_count") == 2 and reproducibility.get("source_apply_count") == 2 and reproducibility.get("actual_compiler_process_count") == 14 and reproducibility.get("byte_identical") is True and reproducibility.get("independent_source_owner_count") == 4 and reproducibility.get("source_owner_count_per_phase") == 2 and reproducibility.get("prebuilt_artifact_count") == 0 and reproducibility.get("native_libraries_loaded") == 0 and reproducibility.get("original_adapter_modified") is False and reproducibility.get("original_source_modified") is False and reproducibility.get("derived_source_sha256") == receipt.get("v2_derived_source_sha256") and reproducibility.get("derived_source_bytes") == receipt.get("v2_derived_source_bytes"), "verify two first-party source phases and unchanged original source and adapter")
    native = reproducibility.get("native_outputs", {}).get("extension")
    need(type(native) is dict and native.get("sha256") == C_NATIVE_SHA and native.get("size_bytes") == C_NATIVE_BYTES and native.get("independent_phase_owner_count") == 2 and native.get("file_name") == "_vm_native.cpython-314-x86_64-linux-gnu.so", "verify two genuinely independent, byte-identical first-party native outputs")
    audit = native.get("audit")
    comparison = reproducibility.get("raw_elf_comparison")
    need(type(audit) is dict and audit.get("needed") == ["libc.so.6"] and audit.get("exports") == ["PyInit__vm_native"] and audit.get("required_exports") == ["PyInit__vm_native"] and audit.get("external_regex_dependency_count") == 0 and audit.get("cross_family_dependency_count") == 0 and audit.get("runpath") == [] and audit.get("soname") == [] and type(comparison) is dict and comparison.get("byte_identical") is True and comparison.get("phase_a_sha256") == C_NATIVE_SHA and comparison.get("phase_b_sha256") == C_NATIVE_SHA and comparison.get("phase_a_bytes") == C_NATIVE_BYTES and comparison.get("phase_b_bytes") == C_NATIVE_BYTES and comparison.get("changed_section_count") == 0 and comparison.get("total_differing_byte_count") == 0 and comparison.get("total_difference_span_count") == 0 and comparison.get("report_truncated") is False, "reject hidden external regex, reused family engine, fallback, or nonidentical actual ELF")
    expected_phases = ("reference-a", "reference-b")
    records: list[dict] = []
    phase_results: list[dict] = []
    seen_pids: set[int] = set()
    for index, (phase, name) in enumerate(zip(phases, expected_phases, strict=True)):
        need(type(phase) is dict and phase.get("name") == name and phase.get("candidate_imports") == 0 and phase.get("candidate_processes_started") == 0 and phase.get("native_libraries_loaded") == 0 and phase.get("hidden_cases_read") == 0 and phase.get("timing_trials_run") == 0 and type(phase.get("fresh_source_owners")) is dict and len(phase["fresh_source_owners"]) == 2 and type(phase.get("native_outputs")) is dict and set(phase["native_outputs"]) == {"extension"}, "require two distinct private source-build phases with no candidate execution")
        owner = phase["native_outputs"]["extension"]
        need(type(owner) is dict and owner.get("device") == 2049 and owner.get("inode") == C_PHASE_INODES[index] and owner.get("sha256") == C_NATIVE_SHA and owner.get("size_bytes") == C_NATIVE_BYTES and owner.get("file_name") == native["file_name"] and type(owner.get("path")) is str and owner["path"].startswith("<FRESH_PRIVATE_TMP>/" + name + "/"), "verify actual distinct private native output identities without inspecting native targets")
        selected = [item for item in processes if type(item) is dict and type(item.get("working_directory")) is str and item["working_directory"].endswith("/" + name)]
        need(len(selected) == 7 and {item.get("name") for item in selected} == C_PROCESS_NAMES, "require seven actual compiler or ELF inspection processes per source-build phase")
        for observation in selected:
            pid = observation.get("pid")
            need(type(pid) is int and pid > 0 and pid not in seen_pids and observation.get("exit_status") == 0 and observation.get("shell") is False, "require 14 unique successful real process observations")
            seen_pids.add(pid)
            records.append({"phase": name, "name": observation["name"], "pid": pid, "exit_status": 0, "shell": False})
        phase_results.append({"name": name, "source_owner_count": 2, "actual_process_observation_count": 7, "native_output": {"file_name": owner["file_name"], "device": owner["device"], "inode": owner["inode"], "sha256": owner["sha256"], "bytes": owner["size_bytes"]}, "candidate_imports": 0, "candidate_processes_started": 0, "native_libraries_loaded": 0, "hidden_cases_read": 0, "timing_trials_run": 0})
    need(len(records) == 14 and len(seen_pids) == 14, "count all actual unique compiler-process observations")
    added = {archive_owner["path"]: archive_owner["sha256"], receipt_owner["path"]: receipt_owner["sha256"]}
    need(len(added) == 2 and not (set(added) & set(refs)), "count exactly two new distinct C15 evidence owners")
    proof = {"schema": SCHEMA + "-authenticated-actual-c-source-build", "status": "PASS", "build_status": "PASS", "candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "family": "c", "label": receipt["label"], "archive": archive_owner, "receipt": receipt_owner, "publication_receipt": receipt, "phase_count": 2, "source_apply_count": 2, "actual_compiler_process_count": 14, "actual_unique_process_id_count": 14, "actual_process_observations": records, "phase_results": phase_results, "derived_source_sha256": reproducibility["derived_source_sha256"], "derived_source_bytes": reproducibility["derived_source_bytes"], "independent_source_owner_count": 4, "source_owner_count_per_phase": 2, "prebuilt_artifact_count": 0, "native_outputs_byte_identical": True, "native_output_sha256": C_NATIVE_SHA, "native_output_bytes": C_NATIVE_BYTES, "native_phase_owner_count": 2, "native_phase_device": 2049, "native_phase_inodes": list(C_PHASE_INODES), "external_regex_dependency_count": 0, "cross_family_dependency_count": 0, "needed": ["libc.so.6"], "exports": ["PyInit__vm_native"], "original_source_modified": False, "original_adapter_modified": False, "canonical_native_targets_inspected_by_graph": False, "canonical_native_targets_activated_by_graph": False, "candidate_imports": 0, "candidate_processes_started": 0, "native_libraries_loaded": 0, "new_repository_evidence_owner_count": 2, "uncompressed_c_source_build_archive_bytes_read_by_graph": C_PLAIN_BYTES, "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "uncompressed_zig_archive_opened_by_graph": False, "uncompressed_zig_archive_bytes_read_by_graph": 0, "historical_c_semantic_mismatch_count": 1262, "actual_rust_semantic_mismatch_count": 1087, "actual_zig_semantic_mismatch_count": 2172, "historical_zig_preflight_candidate_worker_count": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}
    return proof, added


def validate(snapshot: object) -> None:
    need(type(snapshot) is dict and snapshot.get("full_case_denominator") == 31237 and snapshot.get("suite_count") == 13 and snapshot.get("baseline_passed") == 31237 and snapshot.get("frozen_independent_engine_family_count") == 6 and snapshot.get("qualified_candidate_count") == 0 and snapshot.get("preserved_v28_repository_evidence_owner_count") == 145 and snapshot.get("preserved_v28_digest_addressed_history_path_count") == 150 and snapshot.get("new_c15_source_build_repository_evidence_owner_count") == 2 and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 147 and snapshot.get("all_digest_addressed_history_path_count") == 152, "derive real 145+2 evidence owners and 150+2 references with zero qualified candidates")
    c = snapshot.get("c_v10_repaired_original_campaign")
    need(type(c) is dict and c.get("status") == "FAIL" and c.get("actual_candidate_workers") == 13 and c.get("semantic_mismatch_count") == 1262 and c.get("verified_passing_case_count") == 7325 and c.get("completed_suite_count") == 13 and c.get("infrastructure_failure_count") == 0 and type(c.get("suite_results")) is list and len(c["suite_results"]) == 13, "preserve last actually matching-tested C failure and all 13 original C groups")
    rust = snapshot.get("rust_v3_original_campaign")
    need(type(rust) is dict and rust.get("status") == "FAIL" and rust.get("publication_status") == "PASS" and rust.get("publication_pass_means") == "DURABLE FAILURE PUBLICATION ONLY" and rust.get("actual_candidate_workers") == 13 and rust.get("completed_suite_count") == 13 and rust.get("semantic_mismatch_count") == 1087 and rust.get("verified_passing_case_count") == 7438 and rust.get("infrastructure_failure_count") == 0 and rust.get("candidate_qualified") is False and rust.get("recovery_journal_sha256") == RUST_JOURNAL and rust.get("all_four_original_targets_restored") is True and rust.get("uncompressed_archive_opened_by_graph") is False and rust.get("uncompressed_archive_bytes_read_by_graph") == 0, "retain actual 13-worker Rust failure, durable receipt distinction, and original recovery")
    zig = snapshot.get("zig_v2_original_campaign")
    preflight = snapshot.get("zig_original_campaign_preflight_failure")
    need(type(zig) is dict and zig.get("status") == "FAIL" and zig.get("actual_candidate_workers") == 13 and zig.get("semantic_mismatch_count") == 2172 and zig.get("verified_passing_case_count") == 2847 and zig.get("infrastructure_failure_count") == 0 and type(preflight) is dict and preflight.get("status") == "FAIL" and preflight.get("actual_candidate_workers") == 0 and preflight.get("actual_matching_case_execution_count") == 0, "preserve both genuine full Zig failure and separate earlier zero-worker failure")
    proof = snapshot.get("c_v15_actual_source_build")
    need(type(proof) is dict and proof.get("schema") == SCHEMA + "-authenticated-actual-c-source-build" and proof.get("status") == "PASS" and proof.get("build_status") == "PASS" and proof.get("candidate_correctness") == "NOT MEASURED" and proof.get("candidate_qualified") is False and proof.get("phase_count") == 2 and proof.get("source_apply_count") == 2 and proof.get("actual_compiler_process_count") == 14 and proof.get("actual_unique_process_id_count") == 14 and type(proof.get("actual_process_observations")) is list and len(proof["actual_process_observations"]) == 14 and type(proof.get("phase_results")) is list and len(proof["phase_results"]) == 2 and proof.get("independent_source_owner_count") == 4 and proof.get("source_owner_count_per_phase") == 2 and proof.get("prebuilt_artifact_count") == 0, "never mistake actual two-phase C build for matching-test success")
    need(proof.get("native_outputs_byte_identical") is True and proof.get("native_output_sha256") == C_NATIVE_SHA and proof.get("native_output_bytes") == C_NATIVE_BYTES and proof.get("native_phase_owner_count") == 2 and proof.get("native_phase_device") == 2049 and proof.get("native_phase_inodes") == list(C_PHASE_INODES) and proof.get("needed") == ["libc.so.6"] and proof.get("exports") == ["PyInit__vm_native"] and proof.get("external_regex_dependency_count") == 0 and proof.get("cross_family_dependency_count") == 0 and proof.get("original_source_modified") is False and proof.get("original_adapter_modified") is False and proof.get("canonical_native_targets_inspected_by_graph") is False and proof.get("canonical_native_targets_activated_by_graph") is False, "require actually proved identical independent first-party C binaries without touching canonical native owners")
    need(proof.get("candidate_imports") == 0 and proof.get("candidate_processes_started") == 0 and proof.get("native_libraries_loaded") == 0 and proof.get("new_repository_evidence_owner_count") == 2 and proof.get("uncompressed_c_source_build_archive_bytes_read_by_graph") == C_PLAIN_BYTES and proof.get("uncompressed_rust_archive_opened_by_graph") is False and proof.get("uncompressed_rust_archive_bytes_read_by_graph") == 0 and proof.get("uncompressed_zig_archive_opened_by_graph") is False and proof.get("uncompressed_zig_archive_bytes_read_by_graph") == 0 and proof.get("historical_c_semantic_mismatch_count") == 1262 and proof.get("actual_rust_semantic_mismatch_count") == 1087 and proof.get("actual_zig_semantic_mismatch_count") == 2172 and proof.get("historical_zig_preflight_candidate_worker_count") == 0, "preserve actual old results and inflate only bounded C build evidence")
    archive, receipt = proof.get("archive"), proof.get("receipt")
    need(type(archive) is dict and archive.get("sha256") == C_ARCHIVE[1] and archive.get("bytes") == C_ARCHIVE[2] and archive.get("device") == C_ARCHIVE[3] and archive.get("inode") == C_ARCHIVE[4] and archive.get("mode") == "0600" and archive.get("nlink") == 1 and type(receipt) is dict and receipt.get("sha256") == C_RECEIPT[1] and receipt.get("bytes") == C_RECEIPT[2] and receipt.get("device") == C_RECEIPT[3] and receipt.get("inode") == C_RECEIPT[4] and receipt.get("mode") == "0600" and receipt.get("nlink") == 1 and (archive.get("device"), archive.get("inode")) != (receipt.get("device"), receipt.get("inode")), "bind distinct actual compressed C source archive and durable receipt")
    for index, phase in enumerate(proof["phase_results"]):
        native = phase.get("native_output") if type(phase) is dict else None
        need(type(phase) is dict and phase.get("name") == ("reference-a", "reference-b")[index] and phase.get("source_owner_count") == 2 and phase.get("actual_process_observation_count") == 7 and type(native) is dict and native.get("device") == 2049 and native.get("inode") == C_PHASE_INODES[index] and native.get("sha256") == C_NATIVE_SHA and native.get("bytes") == C_NATIVE_BYTES and phase.get("candidate_imports") == 0 and phase.get("candidate_processes_started") == 0 and phase.get("native_libraries_loaded") == 0 and phase.get("hidden_cases_read") == 0 and phase.get("timing_trials_run") == 0, "preserve genuine seven-process independently owned C phase")
    pids: set[int] = set()
    for item in proof["actual_process_observations"]:
        need(type(item) is dict and item.get("phase") in ("reference-a", "reference-b") and item.get("name") in C_PROCESS_NAMES and type(item.get("pid")) is int and item["pid"] > 0 and item["pid"] not in pids and item.get("exit_status") == 0 and item.get("shell") is False, "preserve 14 unique successful recorded C process observations")
        pids.add(item["pid"])
    need(len(pids) == 14 and snapshot.get("c_v15_source_build_status") == "PASS" and snapshot.get("c_v15_source_build_candidate_correctness") == "NOT MEASURED" and snapshot.get("c_v15_source_build_candidate_qualified") is False and snapshot.get("c_v15_source_build_process_count") == 14 and snapshot.get("c_v15_source_build_source_apply_count") == 2 and snapshot.get("c_v15_source_build_byte_identical") is True, "separate successful C setup from unknown C correctness")
    need(snapshot.get("performance") == "NOT MEASURED" and snapshot.get("memory") == "NOT MEASURED" and snapshot.get("confidence_intervals") == "NOT MEASURED" and snapshot.get("hidden_cases_read") == 0 and snapshot.get("performance_files_read") == 0 and snapshot.get("clock_samples") == 0 and snapshot.get("timing_trials_run") == 0 and snapshot.get("final_comparison_planned_case_count") == 4194304 and snapshot.get("final_comparison_cases_generated") is False and snapshot.get("final_holdout_opened") is False and snapshot.get("winner_selected") is False, "never claim timing, memory, hidden cases, a winner, or an opened final holdout")


def xml(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "V29 renderer")
    checked(inputs, "V29 graph inputs")
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="2180" viewBox="0 0 1440 2180" role="img" aria-labelledby="v29-title v29-description">',
        '<title id="v29-title">Building a faster Python re: C builds reproducibly, but no replacement has passed the tests</title>',
        '<desc id="v29-description">Python passes 31,237 original checks. The improved first-party C source was really built twice, using 14 independently recorded successful processes, and produced byte-identical independent native binaries. The improved C candidate has not yet been matching-tested: its correctness is NOT MEASURED. The most recently tested C engine had 1,262 differences. Actual full tests found 1,087 Rust differences and 2,172 Zig differences. The earlier failed Zig setup started zero tests. Zero replacements are fully compatible. The evidence contains 147 actual owner files and 152 authenticated references. Only the bounded 322,399-byte C build archive is decoded; the much larger Rust and Zig archives are not. Speed, memory, uncertainty, and undefined behavior are NOT MEASURED. The 4,194,304-case final comparison remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:29px;font-weight:760;fill:#16324f}.heading{font-size:21px;font-weight:740;fill:#16324f}.body{font-size:14px;fill:#42556c}.name{font-size:15px;font-weight:720;fill:#16324f}.pass{font-size:13px;font-weight:760;fill:#00794c}.fail{font-size:13px;font-weight:740;fill:#a15e00}.pending{font-size:13px;font-weight:740;fill:#53667b}.big{font-size:22px;font-weight:760;fill:#16324f}.small{font-size:12px;fill:#42556c}.foot{font-size:10px;fill:#53667b}</style>',
        '<rect width="1440" height="2180" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="57" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="46" y="86" class="body">The latest C source builds reproducibly. Whether that new version works like Python is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0", "compatible replacements"),
        ("14 / 2", "real processes / C builds"),
        ("1,087", "tested Rust differences"),
        ("2,172", "tested Zig differences"),
        ("147 / 152", "evidence / references"),
    )
    for index, (value, label) in enumerate(cards):
        x = 44 + index * 226
        out.extend((f'<rect x="{x}" y="103" width="216" height="90" rx="12" fill="#fff" stroke="#dae4ee"/>', f'<text x="{x + 11}" y="140" class="big">{xml(value)}</text>', f'<text x="{x + 11}" y="169" class="small">{xml(label)}</text>'))
    out.extend((
        '<rect x="44" y="211" width="1352" height="584" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="248" class="heading">1. Where does each replacement stand?</text>',
        '<text x="65" y="273" class="body">A successful source build is not a successful matching test.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 frozen original checks pass.", "pass"),
        ("C — improved new source", "BUILD PASSED; CORRECTNESS NOT MEASURED", "Two real independent builds; 14 successful processes; byte-identical first-party outputs; 0 matching tests.", "pending"),
        ("C — last actually tested version", "NOT COMPATIBLE", "13 real matching workers; 1,262 differences; 7,325 verified passing checks.", "fail"),
        ("Rust — last actually tested version", "NOT COMPATIBLE", "13 real matching workers; 1,087 differences; 7,438 verified passing checks.", "fail"),
        ("Zig — last actually tested version", "NOT COMPATIBLE", "13 real matching workers; 2,172 differences; 2,847 verified passing checks.", "fail"),
        ("Zig — earlier setup attempt", "SETUP STOPPED; 0 TESTS", "A separate real controller failure. No matching workers started.", "fail"),
        ("Rust — earlier tested version", "NOT COMPATIBLE", "A historical engine had 2,042 matching differences.", "fail"),
        ("Zig — earlier tested version", "NOT COMPATIBLE", "A historical engine had 1,764 matching differences.", "fail"),
    )
    for index, (name, status, detail, kind) in enumerate(rows):
        y = 291 + index * 59
        out.extend((f'<rect x="63" y="{y}" width="1314" height="52" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>', f'<text x="79" y="{y + 20}" class="name">{xml(name)}</text>', f'<text x="1358" y="{y + 20}" class="{kind}" text-anchor="end">{xml(status)}</text>', f'<text x="80" y="{y + 40}" class="small">{xml(detail)}</text>'))
    out.extend((
        '<rect x="44" y="812" width="1352" height="454" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="850" class="heading">2. What actually happened in the two C builds?</text>',
        '<text x="65" y="874" class="body">These are 14 distinct recorded successful processes, seven per independent source-build phase.</text>',
        '<text x="82" y="898" class="small">BUILD PHASE</text>',
        '<text x="290" y="898" class="small">REAL OBSERVED ACTION</text>',
        '<text x="1070" y="898" class="small" text-anchor="end">PROCESS ID</text>',
        '<text x="1354" y="898" class="small" text-anchor="end">RESULT</text>',
    ))
    for index, item in enumerate(snapshot["c_v15_actual_source_build"]["actual_process_observations"]):
        y = 906 + index * 23
        shade = "#f8fafd" if index % 2 == 0 else "#ffffff"
        label = item["name"].replace("_", " ")
        out.extend((f'<rect x="64" y="{y}" width="1312" height="22" rx="4" fill="{shade}"/>', f'<text x="81" y="{y + 16}" class="small">{xml(item["phase"])}</text>', f'<text x="290" y="{y + 16}" class="small">{xml(label)}</text>', f'<text x="1070" y="{y + 16}" class="small" text-anchor="end">{item["pid"]:,}</text>', f'<text x="1354" y="{y + 16}" class="pass" text-anchor="end">PASSED</text>'))
    out.extend((
        '<rect x="44" y="1282" width="1352" height="423" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1320" class="heading">3. What did the most recent complete C matching test show?</text>',
        '<text x="65" y="1344" class="body">These 13 rows are the actual previous C test. They are not results for the newly built, still untested version.</text>',
        '<text x="80" y="1367" class="small">ORIGINAL PYTHON TEST GROUP</text>',
        '<text x="1040" y="1367" class="small" text-anchor="end">CHECKS</text>',
        '<text x="1355" y="1367" class="small" text-anchor="end">PREVIOUS C RESULT</text>',
    ))
    for index, row in enumerate(snapshot["c_v10_repaired_original_campaign"]["suite_results"]):
        y = 1375 + index * 23
        shade = "#f8fafd" if index % 2 == 0 else "#ffffff"
        value = "PASSED" if row["mismatch_count"] == 0 else f'{row["mismatch_count"]:,} DIFFERENCES'
        kind = "pass" if row["mismatch_count"] == 0 else "fail"
        out.extend((f'<rect x="64" y="{y}" width="1312" height="22" rx="4" fill="{shade}"/>', f'<text x="80" y="{y + 16}" class="small">{xml(row["display_name"])}</text>', f'<text x="1040" y="{y + 16}" class="small" text-anchor="end">{row["case_execution_denominator"]:,}</text>', f'<text x="1355" y="{y + 16}" class="{kind}" text-anchor="end">{xml(value)}</text>'))
    out.extend((
        '<rect x="44" y="1721" width="1352" height="313" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1759" class="heading">4. Is any replacement actually faster?</text>',
        '<text x="66" y="1789" class="body">NOT MEASURED. No candidate has passed every original Python matching check.</text>',
        '<text x="66" y="1815" class="body">There is no timing, memory comparison, uncertainty estimate, ranking, or winner.</text>',
        '<text x="66" y="1841" class="body">The 4,194,304-case final comparison is not generated and has not been opened.</text>',
        '<text x="66" y="1867" class="body">145 previous evidence files + one actual C build archive + one separate receipt = 147 files; 152 references.</text>',
        '<text x="66" y="1893" class="body">The two C outputs match byte-for-byte and use only Python and libc; no external regex engine or fallback is used.</text>',
        '<text x="66" y="1919" class="body">Only the small C build archive is decoded. Large Rust and Zig failure archives remain compressed.</text>',
        '<text x="66" y="1945" class="body">Build passed means the program was created, not that the improved C version passed matching checks.</text>',
        '<text x="66" y="1971" class="body">Original source and adapter were not modified; graph verification does not inspect or activate native targets.</text>',
        f'<text x="47" y="2062" class="foot">Inputs SHA-256: {xml(inputs)}</text>',
        f'<text x="47" y="2084" class="foot">Renderer SHA-256: {xml(source)}</text>',
        f'<text x="47" y="2106" class="foot">Actual bounded C source-build archive: {xml(C_ARCHIVE[1])}</text>',
        f'<text x="47" y="2128" class="foot">Two independently built C outputs: {xml(C_NATIVE_SHA)}</text>',
        '</svg>',
    ))
    return ("\n".join(out) + "\n").encode("utf-8")


def build(source: str, archive: str, receipt: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked(source, "V29 source")
    own, _ = read_owner(SELF, source)
    _previous, old, old_inputs, refs = authenticate_v28()
    c, added = authenticate_c15(archive, receipt, old, refs)
    need(len(refs) == 150 and len(added) == 2 and not (set(refs) & set(added)), "derive V29 evidence from full authenticated V28 and actual C build only")
    all_refs = dict(refs)
    all_refs.update(added)
    owners = old["repository_evidence_owner_count"] + len(added)
    need(owners == 147 and len(all_refs) == 152, "derive exact actual 147 evidence owners and 152 references")
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({"preserved_v28_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v28_digest_addressed_history_path_count": len(refs), "new_c15_source_build_repository_evidence_owner_count": len(added), "all_actual_candidate_and_native_evidence_owner_count": owners, "all_digest_addressed_history_path_count": len(all_refs), "c_v15_actual_source_build": copy.deepcopy(c), "c_v15_source_build_status": "PASS", "c_v15_source_build_candidate_correctness": "NOT MEASURED", "c_v15_source_build_candidate_qualified": False, "c_v15_source_build_process_count": 14, "c_v15_source_build_source_apply_count": 2, "c_v15_source_build_byte_identical": True})
    validate(snapshot)
    prior = {key: pin(*frozen) for key, frozen in sorted(V28.items())}
    manifest = copy.deepcopy(old_inputs)
    manifest.update({"schema": SCHEMA + "-inputs", "version": 29, "python": "3.14.6", "renderer": pin(SELF, source, len(own)), "previous_overview": prior, "actual_c_v15_source_build": copy.deepcopy(c), "current_complete_c_campaign": copy.deepcopy(snapshot["c_v10_repaired_original_campaign"]), "actual_complete_zig_campaign": copy.deepcopy(snapshot["zig_v2_original_campaign"]), "actual_complete_rust_campaign": copy.deepcopy(snapshot["rust_v3_original_campaign"]), "historical_zig_preflight_failure": copy.deepcopy(snapshot["zig_original_campaign_preflight_failure"]), "preserved_v28_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v28_digest_addressed_history_path_count": len(refs), "new_c15_source_build_repository_evidence_owner_count": len(added), "repository_evidence_owner_count": owners, "all_digest_addressed_history_path_count": len(all_refs), "candidate_qualified_count": 0, "c_v15_build_status": "PASS", "c_v15_candidate_correctness": "NOT MEASURED", "c_v15_actual_compiler_process_count": 14, "c_v15_source_apply_count": 2, "c_v15_native_outputs_byte_identical": True, "c_v15_uncompressed_archive_bytes_read_by_graph": C_PLAIN_BYTES, "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "uncompressed_zig_archive_opened_by_graph": False, "uncompressed_zig_archive_bytes_read_by_graph": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False})
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source, digest(manifest_raw))
    families = copy.deepcopy(old["families"])
    found = 0
    for family in families:
        if family.get("family") == "c":
            found += 1
            family.update({"current_v15_source_build": copy.deepcopy(c), "current_v15_source_build_status": "PASS", "current_v15_source_build_candidate_correctness": "NOT MEASURED", "current_v15_source_build_candidate_worker_count": 0, "current_v15_source_build_compiler_process_count": 14, "current_v15_source_build_source_apply_count": 2, "current_v15_source_build_native_outputs_byte_identical": True, "qualified": False})
    need(found == 1, "retain exactly one independent first-party C engine family")
    summary = copy.deepcopy(old)
    summary.update({"schema": SCHEMA + "-summary", "status": "PASS", "python": "3.14.6", "source": pin(SELF, source, len(own)), "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw), len(manifest_raw)), "svg": pin(OUTPUT + ".svg", digest(image), len(image)), "previous_overview": prior, "snapshot": snapshot, "families": families, "preserved_v28_repository_evidence_owner_count": old["repository_evidence_owner_count"], "preserved_v28_authenticated_reference_path_count": len(refs), "new_c15_source_build_repository_evidence_owner_count": len(added), "repository_evidence_owner_count": owners, "authenticated_digest_addressed_history_paths": len(all_refs), "qualified_candidate_count": 0, "actual_c_v15_source_build": copy.deepcopy(c), "c_v15_source_build_status": "PASS", "c_v15_source_build_candidate_correctness": "NOT MEASURED", "c_v15_source_build_candidate_qualified": False, "c_v15_source_build_candidate_worker_count": 0, "c_v15_source_build_process_count": 14, "c_v15_source_build_source_apply_count": 2, "c_v15_source_build_byte_identical": True, "c_v15_source_build_unique_pid_count": 14, "c_v15_native_output_sha256": C_NATIVE_SHA, "c_v15_native_output_bytes": C_NATIVE_BYTES, "c_v15_native_phase_inodes": list(C_PHASE_INODES), "c_v15_external_regex_dependency_count": 0, "c_v15_cross_family_dependency_count": 0, "c_v15_candidate_imports": 0, "c_v15_candidate_processes_started": 0, "c_v15_original_source_modified": False, "c_v15_original_adapter_modified": False, "c_v15_uncompressed_archive_bytes_read_by_graph": C_PLAIN_BYTES, "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "uncompressed_zig_archive_opened_by_graph": False, "uncompressed_zig_archive_bytes_read_by_graph": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False})
    return snapshot, ((OUTPUT + ".inputs.json", manifest_raw), (OUTPUT + ".json", canonical(summary)), (OUTPUT + ".svg", image))


class Wall:
    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, obj: object, name: str) -> None:
        previous = getattr(obj, name, None)
        if previous is None:
            return
        def deny(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GraphError("V29 source-only effect blocked: " + name)
        self.saved.append((obj, name, previous))
        setattr(obj, name, deny)

    def __enter__(self) -> Wall:
        groups = ((builtins, ("open",)), (os, ("open", "read", "write", "stat", "lstat", "unlink", "remove", "rename", "replace", "mkdir", "makedirs", "system", "fork", "posix_spawn")), (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text", "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")), (subprocess, ("run", "Popen", "call", "check_call", "check_output")), (socket, ("socket", "create_connection")), (importlib, ("import_module",)), (tempfile, ("mkdtemp", "mkstemp")), (threading.Thread, ("start",)), (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "sleep")), (zlib, ("decompress", "decompressobj")))
        for obj, names in groups:
            for name in names:
                self.install(obj, name)
        return self

    def __exit__(self, _kind: object, _error: object, _trace: object) -> None:
        for obj, name, previous in reversed(self.saved):
            setattr(obj, name, previous)


def synthetic() -> dict:
    rows = [{"suite": f"group-{i}", "display_name": f"Original group {i + 1}", "case_execution_denominator": 2000, "mismatch_count": 1262 if i == 0 else 0} for i in range(13)]
    c = {"status": "FAIL", "actual_candidate_workers": 13, "semantic_mismatch_count": 1262, "verified_passing_case_count": 7325, "completed_suite_count": 13, "infrastructure_failure_count": 0, "suite_results": rows}
    rust = {"status": "FAIL", "publication_status": "PASS", "publication_pass_means": "DURABLE FAILURE PUBLICATION ONLY", "actual_candidate_workers": 13, "completed_suite_count": 13, "semantic_mismatch_count": 1087, "verified_passing_case_count": 7438, "infrastructure_failure_count": 0, "candidate_qualified": False, "recovery_journal_sha256": RUST_JOURNAL, "all_four_original_targets_restored": True, "uncompressed_archive_opened_by_graph": False, "uncompressed_archive_bytes_read_by_graph": 0}
    zig = {"status": "FAIL", "actual_candidate_workers": 13, "semantic_mismatch_count": 2172, "verified_passing_case_count": 2847, "infrastructure_failure_count": 0}
    old_zig = {"status": "FAIL", "actual_candidate_workers": 0, "actual_matching_case_execution_count": 0}
    archive = {"sha256": C_ARCHIVE[1], "bytes": C_ARCHIVE[2], "device": C_ARCHIVE[3], "inode": C_ARCHIVE[4], "mode": "0600", "nlink": 1}
    receipt = {"sha256": C_RECEIPT[1], "bytes": C_RECEIPT[2], "device": C_RECEIPT[3], "inode": C_RECEIPT[4], "mode": "0600", "nlink": 1}
    names = sorted(C_PROCESS_NAMES)
    observations: list[dict] = []
    phases: list[dict] = []
    for index, phase in enumerate(("reference-a", "reference-b")):
        for offset, name in enumerate(names):
            observations.append({"phase": phase, "name": name, "pid": 1000 + index * 7 + offset, "exit_status": 0, "shell": False})
        phases.append({"name": phase, "source_owner_count": 2, "actual_process_observation_count": 7, "native_output": {"device": 2049, "inode": C_PHASE_INODES[index], "sha256": C_NATIVE_SHA, "bytes": C_NATIVE_BYTES}, "candidate_imports": 0, "candidate_processes_started": 0, "native_libraries_loaded": 0, "hidden_cases_read": 0, "timing_trials_run": 0})
    proof = {"schema": SCHEMA + "-authenticated-actual-c-source-build", "status": "PASS", "build_status": "PASS", "candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "phase_count": 2, "source_apply_count": 2, "actual_compiler_process_count": 14, "actual_unique_process_id_count": 14, "actual_process_observations": observations, "phase_results": phases, "independent_source_owner_count": 4, "source_owner_count_per_phase": 2, "prebuilt_artifact_count": 0, "native_outputs_byte_identical": True, "native_output_sha256": C_NATIVE_SHA, "native_output_bytes": C_NATIVE_BYTES, "native_phase_owner_count": 2, "native_phase_device": 2049, "native_phase_inodes": list(C_PHASE_INODES), "needed": ["libc.so.6"], "exports": ["PyInit__vm_native"], "external_regex_dependency_count": 0, "cross_family_dependency_count": 0, "original_source_modified": False, "original_adapter_modified": False, "canonical_native_targets_inspected_by_graph": False, "canonical_native_targets_activated_by_graph": False, "candidate_imports": 0, "candidate_processes_started": 0, "native_libraries_loaded": 0, "new_repository_evidence_owner_count": 2, "uncompressed_c_source_build_archive_bytes_read_by_graph": C_PLAIN_BYTES, "uncompressed_rust_archive_opened_by_graph": False, "uncompressed_rust_archive_bytes_read_by_graph": 0, "uncompressed_zig_archive_opened_by_graph": False, "uncompressed_zig_archive_bytes_read_by_graph": 0, "historical_c_semantic_mismatch_count": 1262, "actual_rust_semantic_mismatch_count": 1087, "actual_zig_semantic_mismatch_count": 2172, "historical_zig_preflight_candidate_worker_count": 0, "archive": archive, "receipt": receipt}
    return {"full_case_denominator": 31237, "suite_count": 13, "baseline_passed": 31237, "frozen_independent_engine_family_count": 6, "qualified_candidate_count": 0, "preserved_v28_repository_evidence_owner_count": 145, "preserved_v28_digest_addressed_history_path_count": 150, "new_c15_source_build_repository_evidence_owner_count": 2, "all_actual_candidate_and_native_evidence_owner_count": 147, "all_digest_addressed_history_path_count": 152, "c_v10_repaired_original_campaign": c, "rust_v3_original_campaign": rust, "zig_v2_original_campaign": zig, "zig_original_campaign_preflight_failure": old_zig, "c_v15_actual_source_build": proof, "c_v15_source_build_status": "PASS", "c_v15_source_build_candidate_correctness": "NOT MEASURED", "c_v15_source_build_candidate_qualified": False, "c_v15_source_build_process_count": 14, "c_v15_source_build_source_apply_count": 2, "c_v15_source_build_byte_identical": True, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "hidden_cases_read": 0, "performance_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}


def self_test() -> dict:
    runtime()
    with Wall() as wall:
        base = synthetic()
        validate(base)
        rejected = 0
        hostile_snapshot = {"full_case_denominator": 31236, "suite_count": 12, "baseline_passed": 0, "frozen_independent_engine_family_count": 5, "qualified_candidate_count": 1, "preserved_v28_repository_evidence_owner_count": 144, "preserved_v28_digest_addressed_history_path_count": 149, "new_c15_source_build_repository_evidence_owner_count": 1, "all_actual_candidate_and_native_evidence_owner_count": 146, "all_digest_addressed_history_path_count": 151, "c_v15_source_build_status": "FAIL", "c_v15_source_build_candidate_correctness": "PASS", "c_v15_source_build_candidate_qualified": True, "c_v15_source_build_process_count": 13, "c_v15_source_build_source_apply_count": 1, "c_v15_source_build_byte_identical": False, "performance": "2x faster", "memory": "zero", "confidence_intervals": "95%", "hidden_cases_read": 1, "performance_files_read": 1, "clock_samples": 1, "timing_trials_run": 1, "final_comparison_planned_case_count": 4194303, "final_comparison_cases_generated": True, "final_holdout_opened": True, "winner_selected": True}
        for key, forgery in hostile_snapshot.items():
            bad = copy.deepcopy(base)
            bad[key] = forgery
            try:
                validate(bad)
            except (GraphError, KeyError, TypeError, ValueError):
                rejected += 1
            else:
                raise GraphError("accepted forged V29 snapshot field " + key)
        hostile_c = {"status": "FAIL", "build_status": "FAIL", "candidate_correctness": "PASS", "candidate_qualified": True, "phase_count": 1, "source_apply_count": 1, "actual_compiler_process_count": 13, "actual_unique_process_id_count": 13, "independent_source_owner_count": 2, "source_owner_count_per_phase": 1, "prebuilt_artifact_count": 1, "native_outputs_byte_identical": False, "native_output_sha256": "0" * 64, "native_output_bytes": 1, "native_phase_owner_count": 1, "native_phase_device": 0, "native_phase_inodes": [C_PHASE_INODES[0], C_PHASE_INODES[0]], "needed": ["libpcre2.so"], "exports": ["PyInit_external_regex"], "external_regex_dependency_count": 1, "cross_family_dependency_count": 1, "original_source_modified": True, "original_adapter_modified": True, "canonical_native_targets_inspected_by_graph": True, "canonical_native_targets_activated_by_graph": True, "candidate_imports": 1, "candidate_processes_started": 1, "native_libraries_loaded": 1, "new_repository_evidence_owner_count": 1, "uncompressed_c_source_build_archive_bytes_read_by_graph": C_PLAIN_BYTES + 1, "uncompressed_rust_archive_opened_by_graph": True, "uncompressed_rust_archive_bytes_read_by_graph": 1, "uncompressed_zig_archive_opened_by_graph": True, "uncompressed_zig_archive_bytes_read_by_graph": 1, "historical_c_semantic_mismatch_count": 0, "actual_rust_semantic_mismatch_count": 0, "actual_zig_semantic_mismatch_count": 0, "historical_zig_preflight_candidate_worker_count": 1}
        for key, forgery in hostile_c.items():
            bad = copy.deepcopy(base)
            bad["c_v15_actual_source_build"][key] = forgery
            try:
                validate(bad)
            except (GraphError, KeyError, TypeError, ValueError):
                rejected += 1
            else:
                raise GraphError("accepted forged actual C build proof " + key)
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (b"31,237", b"14 / 2", b"147 / 152", b"1,087", b"2,172", b"1,262", b"7,438", b"2,847", b"NOT MEASURED", b"BUILD PASSED; CORRECTNESS NOT MEASURED", b"SETUP STOPPED; 0 TESTS", b"byte-for-byte", b"not been opened"):
            need(phrase.lower() in picture.lower(), "graph invents speed or omits actual build and matching outcomes")
        effects = (lambda: builtins.open("forbidden-v29"), lambda: os.open("forbidden-v29", os.O_RDONLY), lambda: os.stat("forbidden-v29-native"), lambda: subprocess.run(("forbidden-v29",)), lambda: importlib.import_module("candidates.c_candidate"), lambda: socket.socket(), lambda: tempfile.mkdtemp(), lambda: time.perf_counter(), lambda: threading.Thread(target=lambda: None).start(), lambda: zlib.decompressobj())
        for effect in effects:
            try:
                effect()
            except GraphError:
                continue
            raise GraphError("source-only side effect was not physically blocked")
        need(wall.blocked == len(effects), "require a physical zero-I/O source-only boundary")
        return {"schema": SCHEMA + "-source-only-self-test", "status": "PASS", "version": 29, "synthetic_only": True, "rejected_hostile_control_count": rejected, "blocked_effect_count": wall.blocked, "full_case_denominator": 31237, "suite_count": 13, "repository_evidence_owner_count": 147, "authenticated_digest_addressed_history_paths": 152, "c_source_build_status": "PASS", "improved_c_candidate_correctness": "NOT MEASURED", "actual_c_source_apply_count": 2, "actual_c_compiler_process_count": 14, "actual_c_unique_process_id_count": 14, "actual_c_native_outputs_byte_identical": True, "historical_c_semantic_mismatch_count": 1262, "actual_rust_semantic_mismatch_count": 1087, "actual_zig_semantic_mismatch_count": 2172, "historical_zig_preflight_candidate_workers": 0, "actual_candidate_workers_started_by_graph": 0, "canonical_target_reads": 0, "canonical_target_stats": 0, "uncompressed_c_archive_bytes_read": 0, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_zig_archive_bytes_read": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "workspace_mutations": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}


def publish(path: str, raw: bytes) -> None:
    need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"} and type(raw) is bytes and 0 < len(raw) <= LIMIT, "publish only one bounded new V29 owner")
    fd = os.open(str(ROOT / path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    try:
        position = 0
        while position < len(raw):
            written = os.write(fd, raw[position:])
            need(type(written) is int and written > 0, "reject incomplete exclusive V29 graph")
            position += written
        os.fsync(fd)
        state = os.fstat(fd)
        need(state.st_size == len(raw) and state.st_nlink == 1 and stat.S_IMODE(state.st_mode) == 0o600, "reject altered published V29 owner")
    finally:
        os.close(fd)


def result(source: str, archive: str, receipt: str, outputs: dict[str, bytes], written: bool, suffix: str) -> dict:
    return {"schema": SCHEMA + suffix, "version": 29, "status": "PASS", "source_sha256": source, "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]), "summary_sha256": digest(outputs[OUTPUT + ".json"]), "svg_sha256": digest(outputs[OUTPUT + ".svg"]), "actual_c_source_build_archive_sha256": archive, "actual_c_source_build_receipt_sha256": receipt, "suite_count": 13, "full_case_denominator": 31237, "private_waiver_count": 13, "qualified_candidate_count": 0, "preserved_v28_repository_evidence_owner_count": 145, "preserved_v28_authenticated_reference_count": 150, "new_actual_c_source_build_evidence_owner_count": 2, "repository_evidence_owner_count": 147, "authenticated_digest_addressed_history_paths": 152, "c_source_build_status": "PASS", "improved_c_candidate_correctness": "NOT MEASURED", "c_actual_source_apply_count": 2, "c_actual_compiler_process_count": 14, "c_actual_unique_process_id_count": 14, "c_native_outputs_byte_identical": True, "c_native_output_sha256": C_NATIVE_SHA, "c_native_phase_inodes": list(C_PHASE_INODES), "c_external_regex_dependency_count": 0, "c_cross_family_dependency_count": 0, "historical_c_semantic_mismatch_count": 1262, "actual_rust_candidate_workers": 13, "actual_rust_semantic_mismatch_count": 1087, "actual_rust_verified_passing_case_count": 7438, "actual_zig_candidate_workers": 13, "actual_zig_semantic_mismatch_count": 2172, "actual_zig_verified_passing_case_count": 2847, "historical_zig_preflight_candidate_workers": 0, "outputs_written": written, "actual_candidate_workers_started_by_graph": 0, "actual_candidate_imports": 0, "actual_native_activations": 0, "canonical_target_reads": 0, "canonical_target_stats": 0, "uncompressed_c_source_build_archive_bytes_read": C_PLAIN_BYTES, "uncompressed_rust_archive_opened": False, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_zig_archive_opened": False, "uncompressed_zig_archive_bytes_read": 0, "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "final_comparison_planned_case_count": 4194304, "final_comparison_cases_generated": False, "final_holdout_opened": False, "winner_selected": False}


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    choices = parser.add_mutually_exclusive_group(required=True)
    choices.add_argument("--self-test", action="store_true")
    choices.add_argument("--render", action="store_true")
    choices.add_argument("--verify-frozen-context", action="store_true")
    for name in ("--source-sha256", "--campaign-archive-sha256", "--campaign-receipt-sha256", "--inputs-sha256", "--summary-sha256", "--svg-sha256"):
        parser.add_argument(name)
    args = parser.parse_args(args)
    try:
        runtime()
        if args.self_test:
            need(all(getattr(args, key) is None for key in ("source_sha256", "campaign_archive_sha256", "campaign_receipt_sha256", "inputs_sha256", "summary_sha256", "svg_sha256")), "source-only synthetic test cannot authorize actual evidence")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "V29 source")
        archive = checked(args.campaign_archive_sha256, "actual C15 source-build archive")
        receipt = checked(args.campaign_receipt_sha256, "actual C15 source-build receipt")
        _snapshot, values = build(source, archive, receipt)
        outputs = dict(values)
        if args.render:
            need(args.inputs_sha256 is None and args.summary_sha256 is None and args.svg_sha256 is None, "reject substituted once-only rendering pins")
            for path, raw in values:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, True, "-published")))
            return 0
        frozen = {OUTPUT + ".inputs.json": checked(args.inputs_sha256, "V29 inputs"), OUTPUT + ".json": checked(args.summary_sha256, "V29 summary"), OUTPUT + ".svg": checked(args.svg_sha256, "V29 SVG")}
        for path, fingerprint in frozen.items():
            raw, _ = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(raw == outputs[path], "independently reproduce every frozen actual V29 graph owner")
        sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, False, "-read-only-frozen-context")))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError, KeyError, AttributeError, struct.error, zlib.error) as error:
        sys.stderr.write("current V29 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
