#!/usr/bin/env python3
"""Show the real Rust and Zig builds without inventing matching or speed."""

from __future__ import annotations

import argparse
import base64
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
SCHEMA = "rebar-candidate-current-overview-v25"
SELF = "tools/render_candidate_current_overview_v25.py"
OUTPUT = "docs/evidence/candidate-current-overview-v25"
PREVIOUS_OWNERS = 137
PREVIOUS_REFERENCES = 142
NEW_OWNERS = 2
TOTAL_OWNERS = 139
TOTAL_REFERENCES = 144
V24 = {
    "source": ("tools/render_candidate_current_overview_v24.py",
               "a639a39a2b476777e47aecb6850617213491d99698b391a4f905dc1653f25b4e", 80389),
    "inputs": ("docs/evidence/candidate-current-overview-v24.inputs.json",
               "9a01881fca3d090d0b0a95b392b73d2941b330a5acd5144ffaf6a865e5f0cc34", 33092),
    "summary": ("docs/evidence/candidate-current-overview-v24.json",
                "719a3dec863e5f7c78c1c2bc37f7ee06057f9de0ed9cefca74dee0c6dceeceac", 135202),
    "svg": ("docs/evidence/candidate-current-overview-v24.svg",
            "44f56757ca5c908412668c7679006dab288655ab0a419da59ac9265e7cb3aed1", 12712),
}
RUST_SOURCE = (
    "tools/reproduce_owned_native_source_build_v11.py",
    "3fb0ca1b6914617eb8a6f491072fcb40b15a364afacbaec2d4caac1e9b6f5d10", 80171,
)
RUST_PROTOCOL = (
    "oracle/phase2/NATIVE-SOURCE-BUILD-V11.md",
    "bd6bce6b14bebe55691900e4a48bb8acf89197660e1d5ebd4c8c38e979c05fe6", 3868,
)
RUST_CONTRACT = (
    "oracle/phase2/native-source-build-v11.json",
    "7b1f8941444e942a85eb9f9df9dc23244112763ca92381fe22f76fd87c95a87a", 7676,
)
RUST_ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz",
    "282927f91fd885701dff6c431474f586afbc09460c6a20417ffa20be5a2e891c", 107639,
)
RUST_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-rust-phase2-v11-rust-dual-overlay-publication-receipt.json",
    "4c75468663af0de60b37cdbabfca384c4e7f75e25a6155c2ff1c33f654d3f1d7", 1902,
)
RUST_EXPANDED = (
    "8e770b979c197f97e281b06f8c65ab9f22e47d692b0b651b6bf02d4f3e62cf6b", 756221,
)
RUST_NATIVE_ROLES = {
    "engine": ("_rust_engine.so",
               "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
               658344, 0o600),
    "bridge": ("_rust_bridge.cpython-314-x86_64-linux-gnu.so",
               "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54",
               148656, 0o700),
}
BRIDGE_OVERLAY = (
    "candidates/rust/py_bridge.c",
    "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257", 176118,
)
PUBLIC_OVERLAY = (
    "candidates/rust_candidate.py",
    "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c", 31464,
)
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
    """A frozen graph, source build, or original correctness record changed."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise GraphError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only exact authenticated original bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V25 evidence") from error


def checked_digest(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require an independently pinned SHA-256: " + label)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON,
         "use only the exact isolated bytecode-free CPython 3.14.6")


def load_v24() -> types.ModuleType:
    path, fingerprint, expected_size = V24["source"]
    descriptor = os.open(str(ROOT / path),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_size == expected_size,
             "load only the exact frozen V24 graph renderer")
        pieces: list[bytes] = []
        remaining = expected_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            need(bool(block), "reject a truncated V24 graph source")
            pieces.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"", "reject concealed V24 source bytes")
        raw = b"".join(pieces)
        need(digest(raw) == fingerprint, "reject a substituted frozen V24 renderer")
    finally:
        os.close(descriptor)
    module = types.ModuleType("_rebar_exact_candidate_overview_v24_for_v25")
    module.__file__ = str(ROOT / path)
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(module.SCHEMA == "rebar-candidate-current-overview-v24"
         and module.SELF == path and tuple(module.SUITES) == SUITES
         and module.TOTAL_OWNERS == PREVIOUS_OWNERS
         and module.TOTAL_REFERENCES == PREVIOUS_REFERENCES,
         "retain every original Python case and exact published V24 137/142 history")
    return module


def authenticate_history() -> tuple[types.ModuleType, types.ModuleType, dict, dict, dict[str, str]]:
    v24 = load_v24()
    _v23, previous, _v23_summary, _v23_inputs, references = v24.authenticate_history()
    zig, additions = v24.authenticate_zig(
        previous, v24.ZIG_ARCHIVE[1], v24.ZIG_RECEIPT[1],
    )
    need(len(references) == 140 and len(additions) == 2
         and not (set(references) & set(additions)),
         "preserve all genuine published C evidence and both actual Zig owners")
    references = dict(references)
    references.update(additions)
    need(len(references) == PREVIOUS_REFERENCES,
         "preserve all 142 distinct published V24 signed history references")
    old: dict[str, bytes] = {}
    for key, (path, fingerprint, length) in sorted(V24.items()):
        old[key], _ = previous.read_owner(path, fingerprint, size=length)
    summary = previous.document(old["summary"], "exact published V24 graph summary")
    inputs = previous.document(old["inputs"], "exact published V24 graph inputs")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "preserve the exact complete V24 test snapshot")
    v24.validate_snapshot(snapshot)
    need(summary.get("schema") == "rebar-candidate-current-overview-v24-summary"
         and summary.get("status") == "PASS"
         and summary.get("repository_evidence_owner_count") == PREVIOUS_OWNERS
         and summary.get("authenticated_digest_addressed_history_paths")
         == PREVIOUS_REFERENCES
         and summary.get("qualified_candidate_count") == 0
         and summary.get("full_case_denominator") == 31237
         and summary.get("suite_count") == 13
         and type(summary.get("families")) is list
         and inputs.get("repository_evidence_owner_count") == PREVIOUS_OWNERS
         and inputs.get("all_digest_addressed_history_path_count") == PREVIOUS_REFERENCES
         and snapshot.get("zig_v11_scanner_repaired_source_build") == zig
         and old["svg"] == v24.make_svg(snapshot, V24["source"][1], V24["inputs"][1]),
         "independently reproduce all four published V24 owners and genuine Zig history")
    for path, fingerprint in sorted(references.items()):
        previous.read_owner(path, fingerprint)
    return v24, previous, summary, inputs, references


def load_authenticated(previous: types.ModuleType,
                       pin: tuple[str, str, int], name: str) -> types.ModuleType:
    raw, _ = previous.read_owner(pin[0], pin[1], size=pin[2])
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / pin[0])
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


def read_private_exact(path: str, fingerprint: str, length: int,
                       mode: int) -> tuple[dict, bytes]:
    need(type(path) is str and path.startswith("/tmp/")
         and "\x00" not in path and "\\" not in path
         and type(length) is int and 0 < length <= 4 * 1024 * 1024
         and mode in (0o600, 0o700),
         "open only one exact bounded first-party native or source snapshot")
    checked_digest(fingerprint, "private Rust snapshot")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        visible = os.stat(path, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode)
             and (before.st_dev, before.st_ino, before.st_size)
             == (visible.st_dev, visible.st_ino, visible.st_size)
             and before.st_size == length
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == mode,
             "reject a linked, substituted, wrong-mode, or truncated Rust phase owner")
        pieces: list[bytes] = []
        remaining = length
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            need(bool(block), "reject a truncated actual Rust compiler output")
            pieces.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"", "reject hidden actual Rust artifact bytes")
        after = os.fstat(descriptor)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns),
             "reject a Rust private owner changed during authentication")
        raw = b"".join(pieces)
        need(digest(raw) == fingerprint,
             "authenticate every actual byte of the independently built Rust artifact")
        return {"path": path, "sha256": fingerprint, "bytes": length,
                "device": before.st_dev, "inode": before.st_ino,
                "mode": f"{mode:04o}", "link_count": before.st_nlink}, raw
    finally:
        os.close(descriptor)


def process_stream(process: dict, channel: str) -> bytes:
    encoded = process.get(channel + "_base64")
    count = process.get(channel + "_bytes")
    fingerprint = process.get(channel + "_sha256")
    need(type(encoded) is str and type(count) is int
         and 0 <= count <= 8 * 1024 * 1024,
         "require the complete original " + channel + " compiler stream")
    checked_digest(fingerprint, "actual Rust " + channel + " stream")
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise GraphError("reject a malformed actual compiler stream") from error
    need(len(raw) == count and digest(raw) == fingerprint,
         "reject hidden or invented real Rust compiler output")
    return raw


def restore_path(value: str, root: str) -> str:
    need(type(value) is str and "\x00" not in value,
         "restore only an exact bounded redacted Rust private path")
    return value.replace("<FRESH_PRIVATE_TMP>", root)


def authenticate_rust(previous: types.ModuleType, archive_pin: str,
                      receipt_pin: str) -> tuple[dict, dict[str, str]]:
    need(archive_pin == RUST_ARCHIVE[1] and receipt_pin == RUST_RECEIPT[1],
         "require independent caller pins for the actually published Rust build")
    compressed, archive_owner = previous.read_owner(
        RUST_ARCHIVE[0], archive_pin, size=RUST_ARCHIVE[2], private=True,
    )
    receipt_raw, receipt_owner = previous.read_owner(
        RUST_RECEIPT[0], receipt_pin, size=RUST_RECEIPT[2], private=True,
    )
    receipt = previous.document(receipt_raw, "genuine durable Rust V11 build receipt")
    previous.boundary(receipt, "actual Rust V11 source-build receipt")
    publication = receipt.get("archive_publication")
    synced = receipt.get("archive_directory_fsync")
    need(type(publication) is dict and type(synced) is dict
         and receipt.get("archive_relative") == archive_owner["path"]
         and receipt.get("archive_sha256") == archive_owner["sha256"]
         and receipt.get("archive_bytes") == archive_owner["bytes"]
         and publication.get("path") == str(ROOT / RUST_ARCHIVE[0])
         and publication.get("sha256") == archive_owner["sha256"]
         and publication.get("bytes") == archive_owner["bytes"]
         and publication.get("device") == archive_owner["device"]
         and publication.get("inode") == archive_owner["inode"]
         and publication.get("exclusive_creation") is True
         and publication.get("file_fsync_completed") is True
         and publication.get("same_inode_readback_verified") is True
         and synced.get("completed") is True
         and archive_owner["mode"] == 0o600 and archive_owner["nlink"] == 1,
         "bind the Rust receipt to the genuine exclusive durable actual archive owner")
    need(receipt.get("schema")
         == "rebar-phase2-owned-native-source-build-v11-durable-publication-receipt"
         and receipt.get("status") == "PASS"
         and receipt.get("build_status") == "PASS"
         and receipt.get("family") == "rust"
         and receipt.get("label") == "phase2-v11-rust-dual-overlay"
         and receipt.get("source_sha256") == RUST_SOURCE[1]
         and receipt.get("protocol_sha256") == RUST_PROTOCOL[1]
         and receipt.get("contract_sha256") == RUST_CONTRACT[1]
         and receipt.get("uncompressed_sha256") == RUST_EXPANDED[0]
         and receipt.get("uncompressed_bytes") == RUST_EXPANDED[1]
         and receipt.get("historical_evidence_owner_count") == PREVIOUS_OWNERS
         and receipt.get("historical_authenticated_reference_count")
         == PREVIOUS_REFERENCES
         and receipt.get("bridge_derived_sha256") == BRIDGE_OVERLAY[1]
         and receipt.get("public_derived_sha256") == PUBLIC_OVERLAY[1]
         and receipt.get("bridge_overlay_apply_count") == 2
         and receipt.get("public_overlay_apply_count") == 2
         and receipt.get("expected_actual_compiler_process_count") == 28
         and receipt.get("actual_compiler_process_count") == 28
         and receipt.get("candidate_correctness") == "NOT MEASURED"
         and receipt.get("candidate_imports") == 0
         and receipt.get("candidate_processes_started") == 0
         and receipt.get("native_libraries_loaded") == 0
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("winner_selected") is False,
         "a genuine passing Rust source build is not a passing matching experiment")
    report = previous.expand_archive(compressed, expected_sha=RUST_EXPANDED[0],
                                     expected_bytes=RUST_EXPANDED[1],
                                     label="actual complete Rust V11 dual-overlay build")
    previous.boundary(report, "actual complete Rust V11 dual-overlay source build")
    need(report.get("schema")
         == "rebar-phase2-owned-native-source-build-v11-actual-dual-overlay-build"
         and report.get("version") == 11 and report.get("status") == "PASS"
         and report.get("family") == "rust"
         and report.get("label") == "phase2-v11-rust-dual-overlay"
         and report.get("source_sha256") == RUST_SOURCE[1]
         and report.get("protocol_sha256") == RUST_PROTOCOL[1]
         and report.get("contract_sha256") == RUST_CONTRACT[1]
         and report.get("root_prefix") == "rebar-phase2-native-build-v9-rust-"
         and report.get("historical_evidence_owner_count") == PREVIOUS_OWNERS
         and report.get("historical_authenticated_reference_count")
         == PREVIOUS_REFERENCES
         and report.get("bridge_derived_sha256") == BRIDGE_OVERLAY[1]
         and report.get("public_derived_sha256") == PUBLIC_OVERLAY[1]
         and report.get("bridge_overlay_apply_count") == 2
         and report.get("public_overlay_apply_count") == 2
         and report.get("expected_actual_compiler_process_count") == 28
         and report.get("actual_compiler_process_count") == 28
         and report.get("phase_count") == 2
         and report.get("candidate_correctness") == "NOT MEASURED"
         and report.get("candidate_imports") == 0
         and report.get("candidate_processes_started") == 0
         and report.get("native_libraries_loaded") == 0
         and report.get("hidden_cases_read") == 0
         and report.get("clock_samples") == 0
         and report.get("timing_trials_run") == 0
         and report.get("winner_selected") is False,
         "reject false Rust matching, invented build processes, or changed history")
    rust = load_authenticated(
        previous, RUST_SOURCE, "_rebar_exact_rust_v11_actual_source_for_v25",
    )
    _protocol, _ = previous.read_owner(
        RUST_PROTOCOL[0], RUST_PROTOCOL[1], size=RUST_PROTOCOL[2],
    )
    frozen_raw, _ = previous.read_owner(
        RUST_CONTRACT[0], RUST_CONTRACT[1], size=RUST_CONTRACT[2],
    )
    need(canonical(rust.contract_document(RUST_SOURCE[1], RUST_PROTOCOL[1]))
         == frozen_raw,
         "independently reproduce the separately frozen Rust V11 build contract")
    frozen_context, loaded = rust.verify_context(
        RUST_SOURCE[1], RUST_PROTOCOL[1], RUST_CONTRACT[1],
    )
    need(frozen_context == report.get("frozen_context")
         and frozen_context.get("status") == "PASS"
         and frozen_context.get("historical_evidence_owner_count") == PREVIOUS_OWNERS
         and frozen_context.get("historical_authenticated_reference_count")
         == PREVIOUS_REFERENCES
         and frozen_context.get("published_v24_graph_owner_count") == 4
         and frozen_context.get("published_v24_graph_reproduced") is True
         and frozen_context.get("rust_historical_semantic_mismatch_count") == 2042
         and frozen_context.get("rust_historical_verified_passing_case_count") == 7461
         and frozen_context.get("qualified_candidate_count") == 0
         and frozen_context.get("rust_package", {}).get("external_dependency_count") == 0
         and frozen_context.get("rust_package", {}).get("package_count") == 1
         and frozen_context.get("rust_package", {}).get("network_requests") == 0,
         "independently authenticate the exact no-delegation full frozen Rust context")
    c = frozen_context.get("actual_c_campaign")
    zig = frozen_context.get("actual_zig_build")
    need(type(c) is dict and c.get("status") == "FAIL"
         and c.get("actual_evidence_owner_count") == 30
         and c.get("actual_candidate_workers") == 13
         and c.get("completed_suite_count") == 13
         and c.get("observed_matching_case_count") == 31237
         and c.get("verified_passing_case_count") == 7325
         and c.get("semantic_mismatch_count") == 1262
         and c.get("infrastructure_failure_count") == 0
         and c.get("original_native_restored") is True
         and c.get("qualified") is False
         and type(zig) is dict and zig.get("status") == "PASS"
         and zig.get("actual_evidence_owner_count") == 2
         and zig.get("actual_build_process_count") == 26
         and zig.get("actual_source_apply_count") == 2
         and zig.get("independent_phase_count") == 2
         and zig.get("byte_identical_native_role_count") == 2
         and zig.get("candidate_correctness") == "NOT MEASURED",
         "preserve every real C loss and actual first-party Zig source build")
    v10 = loaded["v10"]
    v9 = loaded["v10_state"]["v9"]
    v7 = v9.load_frozen_module(
        "_rebar_phase2_exact_frozen_v25_rust_native_v7", v9.V7_OWNERS["source"],
    )
    phases = report.get("phases")
    need(type(phases) is list and len(phases) == 2
         and [item.get("name") for item in phases if type(item) is dict]
         == list(rust.PHASES),
         "require exactly two separate genuinely completed Rust source phases")
    expected_sources = dict(v10.RUST_OWNERS)
    expected_sources[BRIDGE_OVERLAY[0]] = (BRIDGE_OVERLAY[1], BRIDGE_OVERLAY[2])
    expected_sources[PUBLIC_OVERLAY[0]] = (PUBLIC_OVERLAY[1], PUBLIC_OVERLAY[2])
    need(len(expected_sources) == 9,
         "require seven original Rust sources and exactly two first-party overlays")
    source_ids: set[tuple[int, int]] = set()
    phase_roots: list[str] = []
    native: dict[str, list[tuple[dict, bytes]]] = {"engine": [], "bridge": []}
    for phase, name in zip(phases, rust.PHASES, strict=True):
        owners = phase.get("fresh_source_owners")
        need(type(owners) is dict and set(owners) == set(expected_sources),
             "authenticate all nine unique original or repaired phase source owners")
        bridge = owners.get(BRIDGE_OVERLAY[0])
        public = owners.get(PUBLIC_OVERLAY[0])
        need(type(bridge) is dict and type(public) is dict,
             "require both genuine separately frozen Rust repair outputs")
        first_overlay = bridge.get("source_overlay")
        second_overlay = public.get("source_overlay")
        need(type(first_overlay) is dict and type(second_overlay) is dict
             and first_overlay.get("status") == "PASS"
             and first_overlay.get("phase") == name
             and first_overlay.get("schema") == "rebar-phase2-owned-rust-source-repair-v1"
             and first_overlay.get("source_apply_count") == 1
             and first_overlay.get("derived_sha256") == BRIDGE_OVERLAY[1]
             and first_overlay.get("derived_bytes") == BRIDGE_OVERLAY[2]
             and first_overlay.get("candidate_original_modified") is False
             and second_overlay.get("status") == "PASS"
             and second_overlay.get("phase") == name
             and second_overlay.get("schema")
             == "rebar-phase2-owned-rust-public-contract-source-repair-v1-private-snapshot-application"
             and second_overlay.get("source_apply_count") == 1
             and second_overlay.get("derived_source_sha256") == PUBLIC_OVERLAY[1]
             and second_overlay.get("derived_source_bytes") == PUBLIC_OVERLAY[2]
             and second_overlay.get("original_candidate_modified") is False
             and second_overlay.get("candidate_correctness") == "NOT MEASURED"
             and second_overlay.get("actual_candidate_workers") == 0,
             "require both exact exclusive first-party Rust overlays once per real phase")
        source_root = first_overlay.get("snapshot_root")
        need(type(source_root) is str
             and source_root == second_overlay.get("snapshot_root"),
             "bind both first-party overlays to one authentic phase source root")
        workdir = str(Path(source_root).parent.parent)
        need(rust.checked_root(workdir) == workdir
             and source_root == str(Path(workdir) / name / "source")
             and phase.get("fresh_source_directory")
             == "<FRESH_PRIVATE_TMP>/" + name + "/source"
             and phase.get("fresh_native_directory")
             == "<FRESH_PRIVATE_TMP>/" + name + "/native"
             and phase.get("candidate_imports") == 0
             and phase.get("candidate_processes_started") == 0
             and phase.get("native_libraries_loaded") == 0
             and phase.get("hidden_cases_read") == 0
             and phase.get("timing_trials_run") == 0,
             "preserve the exact owner-only V9-compatible private phase root")
        phase_roots.append(workdir)
        for relative, (fingerprint, count) in sorted(expected_sources.items()):
            recorded = owners.get(relative)
            need(type(recorded) is dict
                 and recorded.get("path")
                 == "<FRESH_PRIVATE_TMP>/" + name + "/source/" + relative
                 and recorded.get("sha256") == fingerprint
                 and recorded.get("bytes") == count
                 and recorded.get("exclusive_creation") is True
                 and recorded.get("same_inode_readback_verified") is True,
                 "reject a substituted or reused private Rust source: " + relative)
            owner, raw = read_private_exact(
                str(Path(source_root) / relative), fingerprint, count, 0o600,
            )
            need(owner["device"] == recorded.get("device")
                 and owner["inode"] == recorded.get("inode")
                 and (owner["device"], owner["inode"]) not in source_ids,
                 "require eighteen separately owned actual Rust source snapshots")
            source_ids.add((owner["device"], owner["inode"]))
            if relative == BRIDGE_OVERLAY[0]:
                need(recorded.get("file_fsync_completed") is True
                     and raw == loaded["v10_state"]["bridge_bytes"],
                     "reproduce every actual bridge repair byte and durable write")
            if relative == PUBLIC_OVERLAY[0]:
                need(recorded.get("file_fsync_completed") is True
                     and raw == loaded["v10_state"]["public_bytes"],
                     "reproduce every actual public-contract repair byte and durable write")
        outputs = phase.get("native_outputs")
        forensic = phase.get("native_forensics")
        need(type(outputs) is dict and set(outputs) == set(RUST_NATIVE_ROLES)
             and type(forensic) is dict and set(forensic) == set(RUST_NATIVE_ROLES),
             "require complete original native Rust output and raw ELF forensics")
        for role, (filename, fingerprint, count, mode) in sorted(RUST_NATIVE_ROLES.items()):
            recorded = outputs.get(role)
            proof = forensic.get(role)
            need(type(recorded) is dict and type(proof) is dict
                 and recorded.get("role") == role
                 and recorded.get("family") == "rust"
                 and recorded.get("file_name") == filename
                 and recorded.get("path")
                 == "<FRESH_PRIVATE_TMP>/" + name + "/native/" + filename
                 and recorded.get("sha256") == fingerprint
                 and recorded.get("size_bytes") == count
                 and recorded.get("candidate_imported") is False
                 and recorded.get("prebuilt_artifact_read") is False,
                 "require independently compiled original first-party Rust " + role)
            owner, raw = read_private_exact(
                str(Path(workdir) / name / "native" / filename),
                fingerprint, count, mode,
            )
            need(owner["device"] == recorded.get("device")
                 and owner["inode"] == recorded.get("inode")
                 and proof.get("raw_elf64") == v7.parse_owned_elf64(raw),
                 "independently parse every byte of the authentic Rust " + role + " ELF")
            audit = recorded.get("audit")
            need(type(audit) is dict and audit.get("role") == role
                 and audit.get("external_regex_dependency_count") == 0
                 and audit.get("cross_family_dependency_count") == 0
                 and type(audit.get("exports")) is list
                 and type(audit.get("required_exports")) is list
                 and set(audit["required_exports"]).issubset(audit["exports"])
                 and audit.get("needed")
                 == (["ld-linux-x86-64.so.2", "libc.so.6", "libgcc_s.so.1"]
                     if role == "engine" else ["_rust_engine.so", "libc.so.6"])
                 and audit.get("soname")
                 == (["_rust_engine.so"] if role == "engine" else [])
                 and audit.get("runpath")
                 == ([] if role == "engine" else ["$ORIGIN"]),
                 "reject an external regex engine, stdlib delegation, or another candidate")
            native[role].append((owner, raw))
    need(len(set(phase_roots)) == 1,
         "require both genuinely distinct phases within the exact private Rust root")
    workdir = phase_roots[0]
    processes = report.get("compiler_processes")
    need(type(processes) is list
         and len(processes) == 2 * len(rust.RUST_PROCESS_NAMES) == 28,
         "count twenty-eight compiler processes only from the actual completed report")
    identifiers: set[int] = set()
    for index, item in enumerate(processes):
        need(type(item) is dict, "reject an incomplete original compiler process")
        phase = rust.PHASES[index // len(rust.RUST_PROCESS_NAMES)]
        name = rust.RUST_PROCESS_NAMES[index % len(rust.RUST_PROCESS_NAMES)]
        pid = item.get("pid")
        need(item.get("name") == name and type(pid) is int
             and pid > 0 and pid not in identifiers
             and item.get("exit_status") == 0
             and item.get("shell") is False
             and item.get("working_directory")
             == "<FRESH_PRIVATE_TMP>/" + phase,
             "reject omitted, reused, reordered, failed, or shell-based Rust processes")
        identifiers.add(pid)
        arguments = item.get("argv")
        environment = item.get("environment")
        need(type(arguments) is list and type(environment) is dict,
             "require exact actual compiler command and clean offline environment")
        restored_args = [restore_path(value, workdir) for value in arguments]
        restored_env = {
            key: restore_path(value, workdir) for key, value in environment.items()
        }
        v9.checked_command(name, restored_args, workdir, "rust", phase)
        need(restored_env == v9.build_environment(workdir, "rust", phase)
             and restore_path(item["working_directory"], workdir)
             == str(v9.command_working_directory(workdir, "rust", phase, name)),
             "authenticate the genuinely offline, frozen, zero-dependency Cargo schedule")
        process_stream(item, "stdout")
        process_stream(item, "stderr")
    reproduced = report.get("reproducibility")
    need(type(reproduced) is dict and reproduced.get("status") == "PASS"
         and reproduced.get("independent_fresh_phase_count") == 2
         and reproduced.get("source_owners_per_phase") == 9
         and reproduced.get("unchanged_source_owners_per_phase") == 7
         and reproduced.get("bridge_overlay_count") == 2
         and reproduced.get("public_overlay_count") == 2
         and reproduced.get("bridge_derived_sha256") == BRIDGE_OVERLAY[1]
         and reproduced.get("public_derived_sha256") == PUBLIC_OVERLAY[1]
         and reproduced.get("byte_identical") is True
         and reproduced.get("unique_process_count") == 28
         and reproduced.get("native_role_count") == 2
         and reproduced.get("prebuilt_artifact_count") == 0
         and reproduced.get("native_libraries_loaded") == 0
         and reproduced.get("original_sources_modified") is False
         and type(reproduced.get("native_outputs")) is dict
         and set(reproduced["native_outputs"]) == set(RUST_NATIVE_ROLES)
         and type(reproduced.get("raw_elf_comparisons")) is dict
         and set(reproduced["raw_elf_comparisons"]) == set(RUST_NATIVE_ROLES),
         "require genuine complete source and raw-binary reproducibility")
    role_proof: dict[str, dict] = {}
    for role, (filename, fingerprint, count, _mode) in sorted(RUST_NATIVE_ROLES.items()):
        first, second = native[role]
        recorded = reproduced["native_outputs"].get(role)
        compared = reproduced["raw_elf_comparisons"].get(role)
        first_audit = phases[0]["native_outputs"][role]["audit"]
        second_audit = phases[1]["native_outputs"][role]["audit"]
        need(type(recorded) is dict and recorded.get("file_name") == filename
             and recorded.get("sha256") == fingerprint
             and recorded.get("size_bytes") == count
             and recorded.get("fresh_independent_inode_count") == 2
             and recorded.get("audit") == first_audit == second_audit
             and (first[0]["device"], first[0]["inode"])
             != (second[0]["device"], second[0]["inode"])
             and first[1] == second[1]
             and compared == v7.compare_owned_elf64(first[1], second[1])
             and compared.get("byte_identical") is True
             and compared.get("phase_a_sha256") == fingerprint
             and compared.get("phase_b_sha256") == fingerprint
             and compared.get("phase_a_bytes") == count
             and compared.get("phase_b_bytes") == count
             and compared.get("total_differing_byte_count") == 0
             and compared.get("changed_section_count") == 0
             and compared.get("report_truncated") is False,
             "compare complete authentic separate Rust " + role + " phase binaries")
        role_proof[role] = {
            "file_name": filename, "sha256": fingerprint, "bytes": count,
            "independent_phase_owner_count": 2, "byte_identical": True,
            "phase_a_owner": copy.deepcopy(first[0]),
            "phase_b_owner": copy.deepcopy(second[0]),
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
        }
    proof = {
        "schema": SCHEMA + "-authenticated-rust-v11-source-build",
        "status": "PASS", "build_status": "PASS", "family": "rust",
        "label": "phase2-v11-rust-dual-overlay",
        "source": previous.pin(*RUST_SOURCE),
        "protocol": previous.pin(*RUST_PROTOCOL),
        "contract": previous.pin(*RUST_CONTRACT),
        "archive": previous.pin(*RUST_ARCHIVE),
        "receipt": previous.pin(*RUST_RECEIPT),
        "uncompressed_sha256": RUST_EXPANDED[0],
        "uncompressed_bytes": RUST_EXPANDED[1],
        "actual_build_process_count": 28,
        "actual_bridge_source_apply_count": 2,
        "actual_public_source_apply_count": 2,
        "actual_total_source_apply_count": 4,
        "independent_phase_count": 2,
        "source_owners_per_phase": 9,
        "unchanged_source_owners_per_phase": 7,
        "reproducibility": "PASS",
        "byte_identical_native_role_count": 2,
        "roles": role_proof,
        "bridge_overlay": previous.pin(*BRIDGE_OVERLAY),
        "public_overlay": previous.pin(*PUBLIC_OVERLAY),
        "historical_rust_semantic_mismatch_count": 2042,
        "historical_rust_verified_passing_case_count": 7461,
        "historical_v24_evidence_owner_count": PREVIOUS_OWNERS,
        "historical_v24_authenticated_reference_count": PREVIOUS_REFERENCES,
        "new_repository_evidence_owner_count": NEW_OWNERS,
        "original_candidate_sources_modified": False,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "external_package_dependency_count": 0,
        "offline_frozen_cargo": True,
        "matching_test_status": "NOT MEASURED",
        "actual_candidate_workers": 0,
        "candidate_qualified": False,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, {archive_owner["path"]: archive_owner["sha256"],
                   receipt_owner["path"]: receipt_owner["sha256"]}


def validate_snapshot(snapshot: dict) -> None:
    need(type(snapshot) is dict and snapshot.get("full_case_denominator") == 31237
         and snapshot.get("suite_count") == 13
         and tuple(snapshot.get("suite_ids", ()))
         == tuple(name for name, _count, _differences, _display in SUITES)
         and snapshot.get("baseline_passed") == 31237
         and snapshot.get("frozen_independent_engine_family_count") == 6
         and snapshot.get("current_source_owner_count") == 25
         and snapshot.get("qualified_candidate_count") == 0
         and snapshot.get("preserved_v24_repository_evidence_owner_count") == PREVIOUS_OWNERS
         and snapshot.get("preserved_v24_digest_addressed_history_path_count")
         == PREVIOUS_REFERENCES
         and snapshot.get("new_rust_v11_build_repository_evidence_owner_count") == NEW_OWNERS
         and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == TOTAL_OWNERS
         and snapshot.get("all_digest_addressed_history_path_count") == TOTAL_REFERENCES,
         "preserve the original oracle and exactly 137+2/142+2 actual evidence owners")
    first = snapshot.get("c_v8_repaired_original_campaign")
    second = snapshot.get("c_v9_repaired_original_campaign")
    current = snapshot.get("c_v10_repaired_original_campaign")
    need(type(first) is dict and first.get("status") == "FAIL"
         and first.get("completed_suite_count") == 13
         and first.get("infrastructure_failure_count") == 13
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
         "never hide real C semantic failures or either older infrastructure failure")
    rows = current.get("suite_results")
    need(type(rows) is list and len(rows) == len(SUITES),
         "preserve all thirteen exact original C case groups")
    for row, (name, count, differences, display) in zip(rows, SUITES, strict=True):
        need(type(row) is dict and row.get("suite") == name
             and row.get("display_name") == display
             and row.get("case_execution_denominator") == count
             and row.get("mismatch_count") == differences
             and row.get("status") == ("PASS" if differences == 0 else "FAIL")
             and row.get("actual_worker_started") is True
             and row.get("all_original_records_and_mismatches_preserved") is True,
             "reject a changed original C case group: " + name)
    need(snapshot.get("c_actual_semantic_mismatch_count") == 2094
         and snapshot.get("c_verified_passing_case_executions") == 7197
         and snapshot.get("rust_actual_semantic_mismatch_count") == 2042
         and snapshot.get("rust_verified_passing_case_executions") == 7461
         and snapshot.get("zig_actual_semantic_mismatch_count") == 1764
         and snapshot.get("zig_verified_passing_case_executions") == 3583
         and snapshot.get("cpp_full_original_campaign", {}).get("semantic_mismatch_count") == 2308
         and snapshot.get("go_v2_full_original_campaign", {}).get("semantic_mismatch_count") == 4518,
         "preserve every historical Rust, Zig, C, C++, and Go correctness loss")
    zig = snapshot.get("zig_v11_scanner_repaired_source_build")
    need(type(zig) is dict and zig.get("status") == "PASS"
         and zig.get("build_status") == "PASS"
         and zig.get("actual_build_process_count") == 26
         and zig.get("actual_source_apply_count") == 2
         and zig.get("independent_phase_count") == 2
         and zig.get("byte_identical_native_role_count") == 2
         and zig.get("historical_zig_semantic_mismatch_count") == 1764
         and zig.get("new_repository_evidence_owner_count") == 2
         and zig.get("matching_test_status") == "NOT MEASURED"
         and zig.get("actual_candidate_workers") == 0
         and zig.get("candidate_qualified") is False
         and zig.get("external_regex_engine_count") == 0
         and zig.get("stdlib_regex_engine_count") == 0
         and zig.get("cross_family_engine_count") == 0
         and snapshot.get("zig_scanner_repaired_build_status") == "PASS"
         and snapshot.get("zig_scanner_repaired_build_process_count") == 26
         and snapshot.get("zig_scanner_repaired_source_apply_count") == 2
         and snapshot.get("zig_scanner_repaired_reproducibility") == "PASS"
         and snapshot.get("zig_scanner_repaired_matching_status") == "NOT MEASURED"
         and snapshot.get("zig_scanner_repaired_candidate_worker_count") == 0
         and snapshot.get("zig_scanner_repaired_candidate_qualified") is False,
         "preserve the independently authenticated real, untested Zig source build")
    proof = snapshot.get("rust_v11_dual_overlay_repaired_source_build")
    need(type(proof) is dict and proof.get("schema")
         == SCHEMA + "-authenticated-rust-v11-source-build"
         and proof.get("status") == "PASS" and proof.get("build_status") == "PASS"
         and proof.get("family") == "rust"
         and proof.get("label") == "phase2-v11-rust-dual-overlay"
         and proof.get("source")
         == {"path": RUST_SOURCE[0], "sha256": RUST_SOURCE[1], "bytes": RUST_SOURCE[2]}
         and proof.get("protocol")
         == {"path": RUST_PROTOCOL[0], "sha256": RUST_PROTOCOL[1], "bytes": RUST_PROTOCOL[2]}
         and proof.get("contract")
         == {"path": RUST_CONTRACT[0], "sha256": RUST_CONTRACT[1], "bytes": RUST_CONTRACT[2]}
         and proof.get("archive")
         == {"path": RUST_ARCHIVE[0], "sha256": RUST_ARCHIVE[1], "bytes": RUST_ARCHIVE[2]}
         and proof.get("receipt")
         == {"path": RUST_RECEIPT[0], "sha256": RUST_RECEIPT[1], "bytes": RUST_RECEIPT[2]}
         and proof.get("uncompressed_sha256") == RUST_EXPANDED[0]
         and proof.get("uncompressed_bytes") == RUST_EXPANDED[1]
         and proof.get("actual_build_process_count") == 28
         and proof.get("actual_bridge_source_apply_count") == 2
         and proof.get("actual_public_source_apply_count") == 2
         and proof.get("actual_total_source_apply_count") == 4
         and proof.get("independent_phase_count") == 2
         and proof.get("source_owners_per_phase") == 9
         and proof.get("unchanged_source_owners_per_phase") == 7
         and proof.get("reproducibility") == "PASS"
         and proof.get("byte_identical_native_role_count") == 2
         and proof.get("bridge_overlay")
         == {"path": BRIDGE_OVERLAY[0], "sha256": BRIDGE_OVERLAY[1], "bytes": BRIDGE_OVERLAY[2]}
         and proof.get("public_overlay")
         == {"path": PUBLIC_OVERLAY[0], "sha256": PUBLIC_OVERLAY[1], "bytes": PUBLIC_OVERLAY[2]}
         and proof.get("historical_rust_semantic_mismatch_count") == 2042
         and proof.get("historical_rust_verified_passing_case_count") == 7461
         and proof.get("historical_v24_evidence_owner_count") == PREVIOUS_OWNERS
         and proof.get("historical_v24_authenticated_reference_count") == PREVIOUS_REFERENCES
         and proof.get("new_repository_evidence_owner_count") == NEW_OWNERS
         and proof.get("original_candidate_sources_modified") is False
         and proof.get("external_regex_dependency_count") == 0
         and proof.get("cross_family_dependency_count") == 0
         and proof.get("external_package_dependency_count") == 0
         and proof.get("offline_frozen_cargo") is True
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
         "show a real from-scratch Rust build, never an invented passing candidate")
    roles = proof.get("roles")
    need(type(roles) is dict and set(roles) == set(RUST_NATIVE_ROLES),
         "require both actual first-party Rust native roles")
    for role, (filename, fingerprint, count, mode) in sorted(RUST_NATIVE_ROLES.items()):
        item = roles.get(role)
        need(type(item) is dict and item.get("file_name") == filename
             and item.get("sha256") == fingerprint and item.get("bytes") == count
             and item.get("independent_phase_owner_count") == 2
             and item.get("byte_identical") is True
             and item.get("external_regex_dependency_count") == 0
             and item.get("cross_family_dependency_count") == 0,
             "preserve complete actual Rust " + role + " independence evidence")
        first, second = item.get("phase_a_owner"), item.get("phase_b_owner")
        need(type(first) is dict and type(second) is dict
             and first.get("sha256") == second.get("sha256") == fingerprint
             and first.get("bytes") == second.get("bytes") == count
             and first.get("mode") == second.get("mode") == f"{mode:04o}"
             and first.get("link_count") == second.get("link_count") == 1
             and (first.get("device"), first.get("inode"))
             != (second.get("device"), second.get("inode")),
             "require genuinely separate byte-identical first-party Rust native owners")
    need(snapshot.get("rust_dual_overlay_repaired_build_status") == "PASS"
         and snapshot.get("rust_dual_overlay_repaired_build_process_count") == 28
         and snapshot.get("rust_dual_overlay_repaired_bridge_source_apply_count") == 2
         and snapshot.get("rust_dual_overlay_repaired_public_source_apply_count") == 2
         and snapshot.get("rust_dual_overlay_repaired_reproducibility") == "PASS"
         and snapshot.get("rust_dual_overlay_repaired_matching_status") == "NOT MEASURED"
         and snapshot.get("rust_dual_overlay_repaired_candidate_worker_count") == 0
         and snapshot.get("rust_dual_overlay_repaired_candidate_qualified") is False
         and snapshot.get("repaired_c_full_matching_test_status")
         == "FAIL: 1,262 SEMANTIC MISMATCHES"
         and snapshot.get("repaired_c_actual_verified_matching_case_count") == 31237
         and snapshot.get("repaired_c_verified_passing_case_count") == 7325
         and snapshot.get("repaired_c_semantic_mismatch_count") == 1262
         and snapshot.get("repaired_c_infrastructure_failure_count") == 0
         and snapshot.get("repaired_c_completed_suite_count") == 13
         and snapshot.get("repaired_c_actual_candidate_worker_count") == 13
         and snapshot.get("repaired_c_native_promoted") is False,
         "keep successful Rust and Zig builds separate from actual failed C matching")
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
         "never invent speed, memory, confidence intervals, ranking, or final holdout data")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))


def make_svg(snapshot: dict, source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(snapshot)
    current = snapshot["c_v10_repaired_original_campaign"]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1660" height="2260" viewBox="0 0 1660 2260" role="img" aria-labelledby="v25-title v25-description">',
        '<title id="v25-title">Building a faster Python re: Rust and Zig now build, but matching and speed remain untested</title>',
        '<desc id="v25-description">Python passes all 31,237 original reference checks. The new from-scratch Rust engine completed 28 genuine offline compiler and inspection steps; both first-party repairs were applied in each of two private builds, producing byte-identical engine and Python bridge outputs. The new Zig engine completed 26 genuine build steps. Neither new build has run the Python matching suite. The older Rust and Zig attempts still have 2,042 and 1,764 recorded differences. The latest C attempt genuinely ran all 13 original groups and recorded 1,262 matching differences. No replacement has qualified. All 139 actual evidence files and 144 distinct signed references are authenticated. Speed, memory, rankings, confidence intervals and undefined behavior have not been measured. The 4,194,304-case final holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:33px;font-weight:760;fill:#16324f}.heading{font-size:24px;font-weight:740;fill:#16324f}.body{font-size:15px;fill:#42556c}.name{font-size:17px;font-weight:720;fill:#16324f}.pass{font-size:15px;font-weight:750;fill:#00794c}.fail{font-size:15px;font-weight:740;fill:#a15e00}.pending{font-size:15px;font-weight:740;fill:#53667b}.big{font-size:25px;font-weight:760;fill:#16324f}.foot{font-size:12px;fill:#53667b}.small{font-size:13px;fill:#42556c}</style>',
        '<rect width="1660" height="2260" rx="22" fill="#f4f7fb"/>',
        '<text x="54" y="66" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="56" y="96" class="body">New from-scratch Rust and Zig engines both build. Whether either matches Python or is faster is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python reference checks"),
        ("28 of 28", "real Rust build steps succeeded"),
        ("26 of 26", "real Zig build steps succeeded"),
        ("0", "fully compatible replacements"),
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
        '<rect x="54" y="241" width="1552" height="850" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="282" class="heading">1. Does each replacement behave exactly like Python?</text>',
        '<text x="78" y="309" class="body">A successful source build is not a passing matching test. A replacement qualifies only after every original check agrees.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original Python reference checks pass.", "pass"),
        ("Rust — newly repaired engine", "BUILT; MATCHING NOT MEASURED", "28 real offline build and inspection steps; both private repairs; two identical engine and bridge builds.", "pending"),
        ("Zig — newly repaired engine", "BUILT; MATCHING NOT MEASURED", "26 real build and inspection steps; two separate byte-identical engine and bridge builds.", "pending"),
        ("C — latest repaired engine", "NOT COMPATIBLE", "All 13 groups ran: 8 completely passed (7,325 checks); 1,262 matching differences; 0 runner failures.", "fail"),
        ("Rust — previously tested engine", "NOT COMPATIBLE", "7,461 fully verified passing checks; 2,042 recorded matching differences.", "fail"),
        ("Zig — previously tested engine", "NOT COMPATIBLE", "3,583 fully verified passing checks; 1,764 recorded matching differences.", "fail"),
        ("C — earlier matching engine", "NOT COMPATIBLE", "7,197 fully verified passing checks; 2,094 recorded matching differences.", "fail"),
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
        '<text x="78" y="1060" class="body">Earlier C attempts remain visible: 13 old runner failures, followed by one runner failure before matching.</text>',
        '<rect x="54" y="1108" width="1552" height="648" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="1149" class="heading">2. Which C test groups still differ?</text>',
        '<text x="78" y="1176" class="body">All 13 original groups and case records are preserved. Neither newly built engine has run these matching tests.</text>',
        '<text x="92" y="1203" class="small">TEST GROUP</text>',
        '<text x="1225" y="1203" class="small" text-anchor="end">ORIGINAL CHECKS</text>',
        '<text x="1562" y="1203" class="small" text-anchor="end">RESULT</text>',
    ))
    for index, row in enumerate(current["suite_results"]):
        y = 1216 + index * 35
        background = "#f8fafd" if index % 2 == 0 else "#ffffff"
        result = ("PASSED" if row["mismatch_count"] == 0
                  else f'{row["mismatch_count"]:,} DIFFERENCES')
        color = "pass" if row["mismatch_count"] == 0 else "fail"
        lines.extend((
            f'<rect x="77" y="{y}" width="1506" height="31" rx="5" fill="{background}"/>',
            f'<text x="95" y="{y + 21}" class="body">{xml(row["display_name"])}</text>',
            f'<text x="1225" y="{y + 21}" class="body" text-anchor="end">{row["case_execution_denominator"]:,}</text>',
            f'<text x="1562" y="{y + 21}" class="{color}" text-anchor="end">{xml(result)}</text>',
        ))
    lines.extend((
        '<text x="79" y="1700" class="body">Eight complete C groups pass. The 7,325 checks count only those completely passing groups.</text>',
        '<text x="79" y="1726" class="body">Five C groups contain 1,262 recorded differences. No historical failure has been hidden.</text>',
        '<rect x="54" y="1772" width="1552" height="282" rx="16" fill="#fff" stroke="#dae4ee"/>',
        '<text x="77" y="1813" class="heading">3. Is any replacement faster?</text>',
        '<text x="79" y="1845" class="body">NOT MEASURED. No replacement has yet passed every Python correctness check.</text>',
        '<text x="79" y="1875" class="body">There is no speed or memory comparison, confidence interval, ranking, winner, or opened final holdout.</text>',
        '<text x="79" y="1905" class="body">Real evidence: 137 earlier files + 2 actual Rust build files = 139 verified files; 144 signed references.</text>',
        '<text x="79" y="1935" class="body">Rust was built offline from our own source and two private first-party repairs; no external regex package.</text>',
        '<text x="79" y="1965" class="body">Both Rust native outputs were byte-identical across independently owned phase files.</text>',
        '<text x="79" y="1995" class="body">The original C binary, its exact inode, and its 0755 permissions remain restored.</text>',
        f'<text x="58" y="2088" class="foot">Inputs SHA-256: {xml(inputs_sha)}</text>',
        f'<text x="58" y="2113" class="foot">Renderer SHA-256: {xml(source_sha)}</text>',
        f'<text x="58" y="2138" class="foot">Actual Rust build archive SHA-256: {RUST_ARCHIVE[1]}</text>',
        f'<text x="58" y="2163" class="foot">Actual Rust build receipt SHA-256: {RUST_RECEIPT[1]}</text>',
        f'<text x="58" y="2188" class="foot">Independently built Rust engine SHA-256: {RUST_NATIVE_ROLES["engine"][1]}</text>',
        f'<text x="58" y="2213" class="foot">Independently built Rust bridge SHA-256: {RUST_NATIVE_ROLES["bridge"][1]}</text>',
        '</svg>', '',
    ))
    return "\n".join(lines).encode("utf-8")


def build(source_sha: str, archive_sha: str, receipt_sha: str
          ) -> tuple[types.ModuleType, dict, dict, tuple[tuple[str, bytes], ...]]:
    runtime()
    checked_digest(source_sha, "V25 graph renderer")
    _v24, previous, old_summary, old_inputs, references = authenticate_history()
    previous.read_owner(SELF, source_sha)
    actual, additions = authenticate_rust(previous, archive_sha, receipt_sha)
    need(len(references) == PREVIOUS_REFERENCES and len(additions) == NEW_OWNERS
         and not (set(references) & set(additions)),
         "count exactly the two separately published genuine Rust evidence owners")
    references.update(additions)
    need(len(references) == TOTAL_REFERENCES,
         "authenticate all 144 distinct signed current-history references")
    snapshot = copy.deepcopy(old_summary["snapshot"])
    snapshot.update({
        "preserved_v24_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v24_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "new_rust_v11_build_repository_evidence_owner_count": NEW_OWNERS,
        "all_actual_candidate_and_native_evidence_owner_count": TOTAL_OWNERS,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "rust_v11_dual_overlay_repaired_source_build": copy.deepcopy(actual),
        "rust_dual_overlay_repaired_build_status": "PASS",
        "rust_dual_overlay_repaired_build_process_count": 28,
        "rust_dual_overlay_repaired_bridge_source_apply_count": 2,
        "rust_dual_overlay_repaired_public_source_apply_count": 2,
        "rust_dual_overlay_repaired_reproducibility": "PASS",
        "rust_dual_overlay_repaired_matching_status": "NOT MEASURED",
        "rust_dual_overlay_repaired_candidate_worker_count": 0,
        "rust_dual_overlay_repaired_candidate_qualified": False,
    })
    validate_snapshot(snapshot)
    manifest = {
        "schema": SCHEMA + "-inputs", "version": 25, "python": "3.14.6",
        "renderer": previous.pin(SELF, source_sha),
        "previous_overview": {
            key: previous.pin(path, fingerprint, length)
            for key, (path, fingerprint, length) in sorted(V24.items())
        },
        "original_correctness_manifest": copy.deepcopy(old_inputs["original_correctness_manifest"]),
        "original_source_freeze": copy.deepcopy(old_inputs["original_source_freeze"]),
        "first_failed_c_campaign": copy.deepcopy(snapshot["c_v8_repaired_original_campaign"]),
        "second_failed_c_campaign": copy.deepcopy(snapshot["c_v9_repaired_original_campaign"]),
        "current_complete_c_campaign": copy.deepcopy(snapshot["c_v10_repaired_original_campaign"]),
        "current_repaired_zig_source_build": copy.deepcopy(
            snapshot["zig_v11_scanner_repaired_source_build"]),
        "current_repaired_rust_source_build": copy.deepcopy(actual),
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "candidate_families": ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "current_source_owner_count": 25,
        "current_tested_candidate_family_count": 5,
        "candidate_qualified_count": 0,
        "preserved_v24_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "new_rust_v11_build_repository_evidence_owner_count": NEW_OWNERS,
        "repository_evidence_owner_count": TOTAL_OWNERS,
        "preserved_v24_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }
    manifest_raw = canonical(manifest)
    manifest_sha = digest(manifest_raw)
    picture = make_svg(snapshot, source_sha, manifest_sha)
    families = copy.deepcopy(old_summary["families"])
    rust_count = 0
    for family in families:
        if family.get("family") == "rust":
            rust_count += 1
            family["current_dual_overlay_repaired_build"] = copy.deepcopy(actual)
            family["current_dual_overlay_repaired_build_status"] = "PASS"
            family["current_dual_overlay_repaired_matching_test_status"] = "NOT MEASURED"
            family["current_dual_overlay_repaired_candidate_worker_count"] = 0
            family["current_dual_overlay_repaired_candidate_qualified"] = False
            family["qualified"] = False
    need(rust_count == 1, "retain exactly one original first-party Rust engine family")
    summary = {
        "schema": SCHEMA + "-summary", "status": "PASS", "python": "3.14.6",
        "source": previous.pin(SELF, source_sha),
        "inputs": previous.pin(OUTPUT + ".inputs.json", manifest_sha),
        "svg": previous.pin(OUTPUT + ".svg", digest(picture)),
        "previous_overview": {
            key: previous.pin(path, fingerprint, length)
            for key, (path, fingerprint, length) in sorted(V24.items())
        },
        "snapshot": snapshot, "families": families,
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "repository_evidence_owner_count": TOTAL_OWNERS,
        "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
        "preserved_v24_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v24_authenticated_reference_path_count": PREVIOUS_REFERENCES,
        "new_rust_v11_build_repository_evidence_owner_count": NEW_OWNERS,
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
        "rust_dual_overlay_repaired_build_status": "PASS",
        "rust_dual_overlay_repaired_build_process_count": 28,
        "rust_dual_overlay_repaired_bridge_source_apply_count": 2,
        "rust_dual_overlay_repaired_public_source_apply_count": 2,
        "rust_dual_overlay_repaired_reproducibility": "PASS",
        "rust_dual_overlay_repaired_matching_test_status": "NOT MEASURED",
        "rust_dual_overlay_repaired_candidate_worker_count": 0,
        "rust_dual_overlay_repaired_candidate_qualified": False,
        "rust_historical_semantic_mismatch_count": 2042,
        "rust_historical_verified_passing_case_count": 7461,
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
        (OUTPUT + ".svg", picture),
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

        def block(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GraphError("V25 source-only side effect blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, block)

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
        "status": "PASS" if differences == 0 else "FAIL",
        "failure_class": "PASS" if differences == 0 else "SEMANTIC MISMATCH",
        "case_execution_denominator": count, "mismatch_count": differences,
        "actual_worker_started": True,
        "worker_returncode": 0 if differences == 0 else 1,
        "all_original_records_and_mismatches_preserved": True,
    } for name, count, differences, display in SUITES]
    first = {"status": "FAIL", "completed_suite_count": 13,
             "infrastructure_failure_count": 13,
             "semantic_mismatch_count": "NOT MEASURED"}
    second = {"status": "FAIL", "actual_candidate_workers": 0,
              "infrastructure_failure_count": 1,
              "semantic_mismatch_count": "NOT MEASURED"}
    current = {"status": "FAIL", "failure_class": "SEMANTIC MISMATCH",
               "actual_candidate_workers": 13, "completed_suite_count": 13,
               "fully_passing_suite_count": 8,
               "observed_matching_case_count": 31237,
               "verified_passing_case_count": 7325,
               "semantic_mismatch_count": 1262,
               "infrastructure_failure_count": 0,
               "all_original_suite_evidence_preserved": True,
               "original_canonical_native_restored": True,
               "qualified": False, "suite_results": rows}
    zig = {"status": "PASS", "build_status": "PASS",
           "actual_build_process_count": 26, "actual_source_apply_count": 2,
           "independent_phase_count": 2, "byte_identical_native_role_count": 2,
           "historical_zig_semantic_mismatch_count": 1764,
           "new_repository_evidence_owner_count": 2,
           "matching_test_status": "NOT MEASURED", "actual_candidate_workers": 0,
           "candidate_qualified": False, "external_regex_engine_count": 0,
           "stdlib_regex_engine_count": 0, "cross_family_engine_count": 0}
    roles: dict[str, dict] = {}
    for index, (role, (filename, fingerprint, count, mode)) in enumerate(
            sorted(RUST_NATIVE_ROLES.items())):
        first_owner = {
            "path": "/tmp/rebar-v25-synthetic/reference-a/native/" + filename,
            "sha256": fingerprint, "bytes": count, "device": 2049,
            "inode": 1000 + index, "mode": f"{mode:04o}", "link_count": 1,
        }
        second_owner = {
            "path": "/tmp/rebar-v25-synthetic/reference-b/native/" + filename,
            "sha256": fingerprint, "bytes": count, "device": 2049,
            "inode": 2000 + index, "mode": f"{mode:04o}", "link_count": 1,
        }
        roles[role] = {
            "file_name": filename, "sha256": fingerprint, "bytes": count,
            "independent_phase_owner_count": 2, "byte_identical": True,
            "phase_a_owner": first_owner, "phase_b_owner": second_owner,
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
        }
    proof = {
        "schema": SCHEMA + "-authenticated-rust-v11-source-build",
        "status": "PASS", "build_status": "PASS", "family": "rust",
        "label": "phase2-v11-rust-dual-overlay",
        "source": {"path": RUST_SOURCE[0], "sha256": RUST_SOURCE[1], "bytes": RUST_SOURCE[2]},
        "protocol": {"path": RUST_PROTOCOL[0], "sha256": RUST_PROTOCOL[1], "bytes": RUST_PROTOCOL[2]},
        "contract": {"path": RUST_CONTRACT[0], "sha256": RUST_CONTRACT[1], "bytes": RUST_CONTRACT[2]},
        "archive": {"path": RUST_ARCHIVE[0], "sha256": RUST_ARCHIVE[1], "bytes": RUST_ARCHIVE[2]},
        "receipt": {"path": RUST_RECEIPT[0], "sha256": RUST_RECEIPT[1], "bytes": RUST_RECEIPT[2]},
        "uncompressed_sha256": RUST_EXPANDED[0], "uncompressed_bytes": RUST_EXPANDED[1],
        "actual_build_process_count": 28,
        "actual_bridge_source_apply_count": 2,
        "actual_public_source_apply_count": 2,
        "actual_total_source_apply_count": 4,
        "independent_phase_count": 2, "source_owners_per_phase": 9,
        "unchanged_source_owners_per_phase": 7,
        "reproducibility": "PASS", "byte_identical_native_role_count": 2,
        "roles": roles,
        "bridge_overlay": {"path": BRIDGE_OVERLAY[0], "sha256": BRIDGE_OVERLAY[1], "bytes": BRIDGE_OVERLAY[2]},
        "public_overlay": {"path": PUBLIC_OVERLAY[0], "sha256": PUBLIC_OVERLAY[1], "bytes": PUBLIC_OVERLAY[2]},
        "historical_rust_semantic_mismatch_count": 2042,
        "historical_rust_verified_passing_case_count": 7461,
        "historical_v24_evidence_owner_count": PREVIOUS_OWNERS,
        "historical_v24_authenticated_reference_count": PREVIOUS_REFERENCES,
        "new_repository_evidence_owner_count": NEW_OWNERS,
        "original_candidate_sources_modified": False,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "external_package_dependency_count": 0,
        "offline_frozen_cargo": True,
        "matching_test_status": "NOT MEASURED",
        "actual_candidate_workers": 0, "candidate_qualified": False,
        "candidate_imports": 0, "candidate_processes_started": 0,
        "native_libraries_loaded": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "suite_ids": [name for name, _count, _differences, _display in SUITES],
        "baseline_passed": 31237, "frozen_independent_engine_family_count": 6,
        "current_source_owner_count": 25, "qualified_candidate_count": 0,
        "preserved_v24_repository_evidence_owner_count": PREVIOUS_OWNERS,
        "preserved_v24_digest_addressed_history_path_count": PREVIOUS_REFERENCES,
        "new_rust_v11_build_repository_evidence_owner_count": NEW_OWNERS,
        "all_actual_candidate_and_native_evidence_owner_count": TOTAL_OWNERS,
        "all_digest_addressed_history_path_count": TOTAL_REFERENCES,
        "c_v8_repaired_original_campaign": first,
        "c_v9_repaired_original_campaign": second,
        "c_v10_repaired_original_campaign": current,
        "c_actual_semantic_mismatch_count": 2094,
        "c_verified_passing_case_executions": 7197,
        "rust_actual_semantic_mismatch_count": 2042,
        "rust_verified_passing_case_executions": 7461,
        "zig_actual_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_executions": 3583,
        "cpp_full_original_campaign": {"semantic_mismatch_count": 2308},
        "go_v2_full_original_campaign": {"semantic_mismatch_count": 4518},
        "zig_v11_scanner_repaired_source_build": zig,
        "zig_scanner_repaired_build_status": "PASS",
        "zig_scanner_repaired_build_process_count": 26,
        "zig_scanner_repaired_source_apply_count": 2,
        "zig_scanner_repaired_reproducibility": "PASS",
        "zig_scanner_repaired_matching_status": "NOT MEASURED",
        "zig_scanner_repaired_candidate_worker_count": 0,
        "zig_scanner_repaired_candidate_qualified": False,
        "rust_v11_dual_overlay_repaired_source_build": proof,
        "rust_dual_overlay_repaired_build_status": "PASS",
        "rust_dual_overlay_repaired_build_process_count": 28,
        "rust_dual_overlay_repaired_bridge_source_apply_count": 2,
        "rust_dual_overlay_repaired_public_source_apply_count": 2,
        "rust_dual_overlay_repaired_reproducibility": "PASS",
        "rust_dual_overlay_repaired_matching_status": "NOT MEASURED",
        "rust_dual_overlay_repaired_candidate_worker_count": 0,
        "rust_dual_overlay_repaired_candidate_qualified": False,
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
            raise GraphError("accepted forged V25 Rust build or matching evidence")

        changed = {
            "full_case_denominator": 31236, "suite_count": 12,
            "baseline_passed": 31236, "frozen_independent_engine_family_count": 5,
            "current_source_owner_count": 24, "qualified_candidate_count": 1,
            "preserved_v24_repository_evidence_owner_count": 136,
            "preserved_v24_digest_addressed_history_path_count": 141,
            "new_rust_v11_build_repository_evidence_owner_count": 1,
            "all_actual_candidate_and_native_evidence_owner_count": 138,
            "all_digest_addressed_history_path_count": 143,
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
            "rust_dual_overlay_repaired_build_status": "FAIL",
            "rust_dual_overlay_repaired_build_process_count": 27,
            "rust_dual_overlay_repaired_bridge_source_apply_count": 1,
            "rust_dual_overlay_repaired_public_source_apply_count": 1,
            "rust_dual_overlay_repaired_reproducibility": "FAIL",
            "rust_dual_overlay_repaired_matching_status": "PASS",
            "rust_dual_overlay_repaired_candidate_worker_count": 1,
            "rust_dual_overlay_repaired_candidate_qualified": True,
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
            "timing_trials_run": 1,
            "final_comparison_planned_case_count": 4194303,
            "final_comparison_cases_generated": True,
            "final_holdout_opened": True, "winner_selected": True,
        }
        for key, forged in changed.items():
            altered = copy.deepcopy(base)
            altered[key] = forged
            reject(altered)
        proof_changes = {
            "schema": "forged", "status": "FAIL", "build_status": "FAIL",
            "family": "zig", "label": "forged",
            "uncompressed_sha256": "0" * 64, "uncompressed_bytes": 756220,
            "actual_build_process_count": 27,
            "actual_bridge_source_apply_count": 1,
            "actual_public_source_apply_count": 1,
            "actual_total_source_apply_count": 3,
            "independent_phase_count": 1, "source_owners_per_phase": 8,
            "unchanged_source_owners_per_phase": 6,
            "reproducibility": "FAIL", "byte_identical_native_role_count": 1,
            "historical_rust_semantic_mismatch_count": 0,
            "historical_rust_verified_passing_case_count": 0,
            "historical_v24_evidence_owner_count": 136,
            "historical_v24_authenticated_reference_count": 141,
            "new_repository_evidence_owner_count": 1,
            "original_candidate_sources_modified": True,
            "external_regex_dependency_count": 1,
            "cross_family_dependency_count": 1,
            "external_package_dependency_count": 1,
            "offline_frozen_cargo": False,
            "matching_test_status": "PASS", "actual_candidate_workers": 1,
            "candidate_qualified": True, "candidate_imports": 1,
            "candidate_processes_started": 1, "native_libraries_loaded": 1,
            "performance": "1.5x faster", "memory": "0 bytes",
            "undefined_behavior": "PASS", "holdout": "OPENED",
            "winner_selected": True,
        }
        for key, forged in proof_changes.items():
            altered = copy.deepcopy(base)
            altered["rust_v11_dual_overlay_repaired_source_build"][key] = forged
            reject(altered)
        for name in ("source", "protocol", "contract", "archive", "receipt",
                     "bridge_overlay", "public_overlay"):
            for key, forged in (("sha256", "0" * 64), ("bytes", 1), ("path", "forged")):
                altered = copy.deepcopy(base)
                altered["rust_v11_dual_overlay_repaired_source_build"][name][key] = forged
                reject(altered)
        for role in RUST_NATIVE_ROLES:
            for key, forged in (("sha256", "0" * 64), ("bytes", 1),
                                ("independent_phase_owner_count", 1),
                                ("byte_identical", False),
                                ("external_regex_dependency_count", 1),
                                ("cross_family_dependency_count", 1)):
                altered = copy.deepcopy(base)
                altered["rust_v11_dual_overlay_repaired_source_build"]["roles"][role][key] = forged
                reject(altered)
            for owner_name in ("phase_a_owner", "phase_b_owner"):
                for key, forged in (("sha256", "0" * 64), ("bytes", 1),
                                    ("mode", "0755"), ("link_count", 2)):
                    altered = copy.deepcopy(base)
                    altered["rust_v11_dual_overlay_repaired_source_build"]["roles"][role][owner_name][key] = forged
                    reject(altered)
        zig_changes = {
            "status": "FAIL", "build_status": "FAIL",
            "actual_build_process_count": 25, "actual_source_apply_count": 1,
            "independent_phase_count": 1,
            "byte_identical_native_role_count": 1,
            "historical_zig_semantic_mismatch_count": 0,
            "new_repository_evidence_owner_count": 1,
            "matching_test_status": "PASS", "actual_candidate_workers": 1,
            "candidate_qualified": True, "external_regex_engine_count": 1,
            "stdlib_regex_engine_count": 1, "cross_family_engine_count": 1,
        }
        for key, forged in zig_changes.items():
            altered = copy.deepcopy(base)
            altered["zig_v11_scanner_repaired_source_build"][key] = forged
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
        for index, (name, _count, _differences, _display) in enumerate(SUITES):
            for key, forged in (("suite", name + "-forged"),
                                ("mismatch_count", -1),
                                ("actual_worker_started", False)):
                altered = copy.deepcopy(base)
                altered["c_v10_repaired_original_campaign"]["suite_results"][index][key] = forged
                reject(altered)
        reject({})
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (b"28 of 28", b"26 of 26", b"2,042", b"1,764",
                       b"1,262", b"7,325", b"NOT MEASURED", b"139", b"144",
                       b"BUILT; MATCHING NOT MEASURED",
                       b"13 old runner failures", b"one runner failure",
                       b"no external regex package", b"two private first-party repairs",
                       b"Public types and serialization", b"672 DIFFERENCES"):
            need(phrase in picture, "the accessible graph hides genuine Rust, Zig, or C evidence")
        probes = (
            lambda: builtins.open("/tmp/rebar-v25-forbidden", "rb"),
            lambda: os.open("/tmp/rebar-v25-forbidden", os.O_RDONLY),
            lambda: os.write(-1, b"forbidden"),
            lambda: subprocess.run(("forbidden-v25-candidate",)),
            lambda: importlib.import_module("candidates.rust_candidate"),
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
                     "independently reject each actual source-only side effect")
                rejected += 1
            else:
                raise GraphError("V25 source-only verification caused a real side effect")
        need(rejected >= 160,
             "require extensive hostile controls for both actual native source builds")
        return {
            "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
            "version": 25, "synthetic_only": True,
            "accepted_synthetic_controls": 1,
            "rejected_hostile_controls": rejected,
            "blocked_effect_count": wall.blocked,
            "repository_evidence_owner_count": TOTAL_OWNERS,
            "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
            "preserved_v24_evidence_owner_count": PREVIOUS_OWNERS,
            "preserved_v24_history_path_count": PREVIOUS_REFERENCES,
            "new_actual_evidence_owner_count": NEW_OWNERS,
            "suite_count": 13, "full_case_denominator": 31237,
            "rust_repaired_build_process_count": 28,
            "rust_repaired_bridge_source_apply_count": 2,
            "rust_repaired_public_source_apply_count": 2,
            "rust_repaired_independent_phase_count": 2,
            "rust_repaired_matching_test_status": "NOT MEASURED",
            "rust_repaired_candidate_worker_count": 0,
            "historical_rust_semantic_mismatch_count": 2042,
            "zig_repaired_build_process_count": 26,
            "zig_repaired_matching_test_status": "NOT MEASURED",
            "historical_zig_semantic_mismatch_count": 1764,
            "current_repaired_c_candidate_worker_count": 13,
            "current_repaired_c_passing_suite_count": 8,
            "current_repaired_c_verified_passing_case_count": 7325,
            "current_repaired_c_semantic_mismatch_count": 1262,
            "current_repaired_c_infrastructure_failure_count": 0,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "actual_reference_workers": 0, "actual_source_builds": 0,
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
         "publish only the three exclusively assigned canonical V25 graph outputs")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        position = 0
        while position < len(raw):
            count = os.write(descriptor, raw[position:])
            need(type(count) is int and count > 0,
                 "reject incomplete deterministic V25 graph evidence")
            position += count
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        need(stat.S_ISREG(owner.st_mode)
             and stat.S_IMODE(owner.st_mode) == 0o600
             and owner.st_nlink == 1 and owner.st_size == len(raw),
             "publish only an exclusive complete private V25 graph output")
    finally:
        os.close(descriptor)
    directory = os.open(str(ROOT / "docs/evidence"),
                        os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
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
    parser.add_argument("--rust-build-archive-sha256")
    parser.add_argument("--rust-build-receipt-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(all(getattr(args, key) is None for key in (
                "source_sha256", "rust_build_archive_sha256",
                "rust_build_receipt_sha256", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            )), "synthetic self-tests cannot authorize any source or evidence owner")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked_digest(args.source_sha256, "V25 renderer source")
        archive = checked_digest(args.rust_build_archive_sha256,
                                 "genuine Rust V11 build archive")
        receipt = checked_digest(args.rust_build_receipt_sha256,
                                 "genuine Rust V11 durable build receipt")
        previous, _manifest, snapshot, outputs = build(source, archive, receipt)
        expected = {path: raw for path, raw in outputs}
        if args.render:
            need(args.inputs_sha256 is None and args.summary_sha256 is None
                 and args.svg_sha256 is None,
                 "source-frozen rendering cannot accept substituted graph output pins")
            for path, raw in outputs:
                publish_output(path, raw)
            result = {
                "schema": SCHEMA + "-published", "status": "PASS", "version": 25,
                "source_sha256": source,
                "inputs_sha256": digest(expected[OUTPUT + ".inputs.json"]),
                "summary_sha256": digest(expected[OUTPUT + ".json"]),
                "svg_sha256": digest(expected[OUTPUT + ".svg"]),
                "actual_rust_build_archive_sha256": archive,
                "actual_rust_build_receipt_sha256": receipt,
                "repository_evidence_owner_count": TOTAL_OWNERS,
                "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
                "new_actual_evidence_owner_count": NEW_OWNERS,
                "rust_repaired_build_status": "PASS",
                "rust_repaired_build_process_count": 28,
                "rust_repaired_bridge_source_apply_count": 2,
                "rust_repaired_public_source_apply_count": 2,
                "rust_repaired_reproducibility": "PASS",
                "rust_repaired_matching_test_status": "NOT MEASURED",
                "rust_repaired_candidate_worker_count": 0,
                "historical_rust_semantic_mismatch_count": 2042,
                "zig_repaired_build_process_count": 26,
                "zig_repaired_matching_test_status": "NOT MEASURED",
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
        pinned = {
            OUTPUT + ".inputs.json": checked_digest(args.inputs_sha256, "V25 inputs"),
            OUTPUT + ".json": checked_digest(args.summary_sha256, "V25 summary"),
            OUTPUT + ".svg": checked_digest(args.svg_sha256, "V25 accessible SVG"),
        }
        for path, fingerprint in pinned.items():
            raw, _ = previous.read_owner(path, fingerprint,
                                         size=len(expected[path]), private=True)
            need(raw == expected[path] and digest(raw) == fingerprint,
                 "independently reproduce every immutable published V25 graph byte")
        validate_snapshot(snapshot)
        result = {
            "schema": SCHEMA + "-read-only-frozen-context", "status": "PASS",
            "version": 25, "read_only": True,
            "source_sha256": source,
            "inputs_sha256": pinned[OUTPUT + ".inputs.json"],
            "summary_sha256": pinned[OUTPUT + ".json"],
            "svg_sha256": pinned[OUTPUT + ".svg"],
            "actual_rust_build_archive_sha256": archive,
            "actual_rust_build_receipt_sha256": receipt,
            "suite_count": 13, "full_case_denominator": 31237,
            "candidate_family_count": 6,
            "repository_evidence_owner_count": TOTAL_OWNERS,
            "authenticated_digest_addressed_history_paths": TOTAL_REFERENCES,
            "preserved_v24_evidence_owner_count": PREVIOUS_OWNERS,
            "preserved_v24_history_path_count": PREVIOUS_REFERENCES,
            "new_actual_evidence_owner_count": NEW_OWNERS,
            "rust_repaired_build_status": "PASS",
            "rust_repaired_build_process_count": 28,
            "rust_repaired_bridge_source_apply_count": 2,
            "rust_repaired_public_source_apply_count": 2,
            "rust_repaired_reproducibility": "PASS",
            "rust_repaired_matching_test_status": "NOT MEASURED",
            "rust_repaired_candidate_worker_count": 0,
            "historical_rust_semantic_mismatch_count": 2042,
            "historical_rust_verified_passing_case_count": 7461,
            "zig_repaired_build_status": "PASS",
            "zig_repaired_build_process_count": 26,
            "zig_repaired_matching_test_status": "NOT MEASURED",
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
            "actual_reference_workers": 0, "actual_source_builds": 0,
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
        sys.stderr.write("current V25 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
