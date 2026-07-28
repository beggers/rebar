#!/usr/bin/env python3
"""Show a real rebuilt Rust engine without claiming untested compatibility."""

from __future__ import annotations

import argparse
import base64
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
SELF = "tools/render_candidate_current_overview_v36.py"
OUTPUT = "docs/evidence/candidate-current-overview-v36"
SCHEMA = "rebar-candidate-current-overview-v36"
LIMIT = 8 * 1024 * 1024
BUILD_REPORT_LIMIT = 1024 * 1024
V35 = {
    "source": (
        "tools/render_candidate_current_overview_v35.py",
        "390373ef8d196c54301ba6917b15b847708359dd27724f7463d9497e706aa618",
        86043,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v35.inputs.json",
        "e90ba3ac5bce1b4c73e1005e740d36c1d24d94a065f71d154ae50075895cf73a",
        141446,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v35.json",
        "5cf793bbd79a65720b4081809c53333b028f133f51143ee22acb3ce43b805367",
        442601,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v35.svg",
        "bc4ec953b521973d4f2ee69db36e75d4e9ec539b4025e1cef3ad90a7c18315a3",
        9905,
    ),
}
BUILD_SOURCE = (
    "tools/reproduce_owned_rust_pattern_repr_source_build_v13.py",
    "2ec050c9902cbb3a239ed3a2dce3258344300b40546e37aea374cf18a9c8b797",
    133023,
)
BUILD_PROTOCOL = (
    "oracle/phase2/RUST-PATTERN-REPR-SOURCE-BUILD-V13.md",
    "3c486fdb63041b4f6060a6147186dd93c8339cbdff5f8060f597ab156ff05701",
    5894,
)
BUILD_CONTRACT = (
    "oracle/phase2/rust-pattern-repr-source-build-v13.json",
    "15023a0a484715f2d97ae5ea9649bb16fe3d30781d601635bda40c246c5906aa",
    20519,
)
ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v13-rust-phase2-v13-rust-pattern-repr-"
    "original-p0.json.gz",
    "c201c014f55a51454baab77d2148dc39d6024bae3273242d6eb1f1b43f419f6a",
    108985,
    2064,
    524714,
)
RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v13-rust-phase2-v13-rust-pattern-repr-"
    "original-p0-publication-receipt.json",
    "4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805",
    2437,
    2064,
    524715,
)
PLAIN_SHA = "7bf86cbaec1df17548a0989d03db896036a86b0671d32e82f12ce4c3fae630db"
PLAIN_BYTES = 760477
BRIDGE_SOURCE_SHA = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
BRIDGE_SOURCE_BYTES = 176118
PUBLIC_SOURCE_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
PUBLIC_SOURCE_BYTES = 31934
ENGINE_NATIVE_SHA = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_NATIVE_BYTES = 658344
BRIDGE_NATIVE_SHA = "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54"
BRIDGE_NATIVE_BYTES = 148656
VECTOR_SHA = "b32f2ea83213686a8b97d63a15ba5c83d323c2dee1f831bab41176544d6adb0a"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols",
    "engine_sections", "engine_notes", "bridge_sections", "bridge_notes",
)


class GraphError(Exception):
    """Reject invented Rust matching, fake build owners, or measurements."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only exact authentic owner bytes")
    return hashlib.sha256(raw).hexdigest()


def checked(value: object, label: str) -> str:
    need(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "require an independently supplied SHA-256 for " + label,
    )
    return value


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GraphError("reject noncanonical V36 build evidence") from error


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        found: dict[str, object] = {}
        for key, value in items:
            need(key not in found, "reject duplicate JSON keys in " + label)
            found[key] = value
        return found

    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("reject nonfinite JSON in " + label)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed " + label) from error
    need(type(value) is dict and canonical(value) == raw,
         "require complete canonical " + label)
    return value


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "require the exact isolated stable CPython 3.14.6 oracle",
    )


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "bound an exact frozen graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def read_owner(
    path: str, fingerprint: str, size: int, *, private: bool = False,
    device: int | None = None, inode: int | None = None,
) -> tuple[bytes, dict]:
    need(
        type(path) is str and bool(path) and not path.startswith("/")
        and "." not in Path(path).parts and ".." not in Path(path).parts,
        "reject escaped, absolute, or substituted owner path",
    )
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "reject an unbounded owner " + path)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directories: list[int] = []
    handle: int | None = None
    try:
        directories.append(os.open(str(ROOT), directory_flags))
        for part in Path(path).parts[:-1]:
            directories.append(os.open(part, directory_flags,
                                       dir_fd=directories[-1]))
        handle = os.open(Path(path).parts[-1], file_flags,
                         dir_fd=directories[-1])
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid() and before.st_nlink == 1
            and before.st_size == size
            and (not private or stat.S_IMODE(before.st_mode) == 0o600)
            and (device is None or before.st_dev == device)
            and (inode is None or before.st_ino == inode),
            "reject foreign, linked, changed or nonprivate owner " + path,
        )
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            need(bool(piece), "reject truncated exact owner " + path)
            chunks.append(piece)
            remaining -= len(piece)
        need(os.read(handle, 1) == b"", "reject excess owner bytes " + path)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
            and digest(raw) == fingerprint,
            "reject owner changes during bounded authentication " + path,
        )
        return raw, {
            "path": path, "sha256": fingerprint, "bytes": size,
            "device": after.st_dev, "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "nlink": after.st_nlink, "uid": after.st_uid,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for directory in reversed(directories):
            os.close(directory)


def load_v35() -> types.ModuleType:
    raw, _ = read_owner(*V35["source"])
    old = types.ModuleType("_rebar_immutable_v35_before_owned_rust_build_v36")
    old.__file__ = str(ROOT / V35["source"][0])
    old.__package__ = ""
    exec(compile(raw, old.__file__, "exec", dont_inherit=True),
         old.__dict__)
    need(
        old.SCHEMA == "rebar-candidate-current-overview-v35"
        and old.SELF == V35["source"][0],
        "load only the actual committed additive Python-reference graph",
    )
    return old


def authenticate_v35() -> tuple[dict, dict]:
    old = load_v35()
    inputs_raw, _ = read_owner(*V35["inputs"], private=True)
    summary_raw, _ = read_owner(*V35["summary"], private=True)
    image_raw, _ = read_owner(*V35["svg"], private=True)
    inputs = document(inputs_raw, "exact immutable V35 graph inputs")
    summary = document(summary_raw, "exact immutable V35 graph summary")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "retain the actual full V35 snapshot")
    old.validate(snapshot)
    need(
        image_raw == old.make_svg(snapshot, V35["source"][1],
                                  V35["inputs"][1])
        and summary.get("schema") == old.SCHEMA + "-summary"
        and summary.get("version") == 35 and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count") == 159
        and summary.get("authenticated_digest_addressed_history_paths") == 164
        and summary.get("authenticated_evidence_owner_lower_bound") == 159
        and summary.get("authenticated_history_reference_lower_bound") == 164
        and summary.get("evidence_owner_count_is_authenticated_lower_bound")
        is True
        and summary.get("full_case_denominator") == 31237
        and summary.get("suite_count") == 13
        and summary.get("private_waiver_count") == 13
        and summary.get("qualified_candidate_count") == 0
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
        and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 1764
        and summary.get("zig_original_campaign_verified_passing_case_count") == 3711
        and summary.get("additional_signature_reference_status") == "PASS"
        and summary.get("additional_signature_reference_cases_executed") == 50
        and summary.get("additional_signature_reference_process_count") == 2
        and summary.get("additional_signature_reference_process_ids") == [81, 82]
        and summary.get("additional_signature_record_vector_sha256") == VECTOR_SHA
        and summary.get("additional_signature_candidate_status") == "NOT RUN"
        and summary.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and inputs.get("repository_evidence_owner_count") == 159
        and inputs.get("all_digest_addressed_history_path_count") == 164,
        "reproduce V35 without touching candidate or reference archives",
    )
    return summary, inputs


def decode_stream(record: dict, channel: str) -> None:
    encoded = record.get(channel + "_base64")
    need(type(encoded) is str,
         "retain the complete actual Rust compiler " + channel)
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (UnicodeError, ValueError) as error:
        raise GraphError("reject a forged Rust compiler " + channel) from error
    need(
        record.get(channel + "_bytes") == len(raw)
        and record.get(channel + "_sha256") == digest(raw),
        "bind complete observed compiler " + channel + " to its original digest",
    )


def inflate_build_report(compressed: bytes) -> dict:
    need(
        type(compressed) is bytes and len(compressed) == ARCHIVE[2]
        and compressed[:3] == b"\x1f\x8b\x08"
        and struct.unpack("<I", compressed[4:8])[0] == 0
        and struct.unpack("<I", compressed[-4:])[0] == PLAIN_BYTES
        and PLAIN_BYTES < BUILD_REPORT_LIMIT,
        "inflate only the exact 760,477-byte first-party Rust build report",
    )
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        raw = decoder.decompress(compressed, BUILD_REPORT_LIMIT + 1)
    except zlib.error as error:
        raise GraphError("reject malformed bounded Rust build evidence") from error
    need(
        decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
        and len(raw) == PLAIN_BYTES and digest(raw) == PLAIN_SHA,
        "reject truncated, concatenated or oversized Rust source-build gzip",
    )
    return document(raw, "complete authentic corrected Rust V13 build report")


def validate_build_phases(report: dict, frozen: dict) -> dict:
    phases = report.get("phases")
    steps = report.get("compiler_processes")
    reproduction = report.get("reproducibility")
    source = frozen.get("first_party_rust_source")
    need(
        type(phases) is list and len(phases) == 2
        and [item.get("name") for item in phases] == list(PHASES)
        and type(steps) is list and len(steps) == 28
        and type(reproduction) is dict
        and type(source) is dict
        and type(source.get("owners")) is list and len(source["owners"]) == 9,
        "require two separately sourced Rust phases and all 28 actual processes",
    )
    seen: set[int] = set()
    for index, row in enumerate(steps):
        phase = PHASES[index // len(PROCESS_NAMES)]
        need(
            type(row) is dict
            and row.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
            and type(row.get("pid")) is int and row["pid"] > 0
            and row["pid"] not in seen
            and row.get("exit_status") == 0
            and row.get("shell") is False
            and row.get("working_directory")
            == "<FRESH_PRIVATE_TMP>/" + phase
            and type(row.get("argv")) is list and bool(row["argv"])
            and type(row.get("environment")) is dict,
            "reject failed, duplicated or reordered actual Rust build processes",
        )
        decode_stream(row, "stdout")
        decode_stream(row, "stderr")
        seen.add(row["pid"])
    frozen_owners = {
        owner["path"]: owner
        for owner in source["owners"]
        if type(owner) is dict and type(owner.get("path")) is str
    }
    need(len(frozen_owners) == 9,
         "retain all nine independently pinned first-party Rust sources")
    identities: dict[str, set[tuple[int, int]]] = {
        "engine": set(), "bridge": set(),
    }
    source_identities: dict[str, set[tuple[int, int]]] = {
        path: set() for path in frozen_owners
    }
    native_expected = {
        "engine": ("_rust_engine.so", ENGINE_NATIVE_SHA,
                   ENGINE_NATIVE_BYTES),
        "bridge": ("_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                   BRIDGE_NATIVE_SHA, BRIDGE_NATIVE_BYTES),
    }
    for phase in phases:
        owners = phase.get("fresh_source_owners")
        outputs = phase.get("native_outputs")
        need(
            type(owners) is dict and set(owners) == set(frozen_owners)
            and type(outputs) is dict and set(outputs) == {"engine", "bridge"}
            and phase.get("candidate_imports") == 0
            and phase.get("candidate_processes_started") == 0
            and phase.get("native_libraries_loaded") == 0
            and phase.get("hidden_cases_read") == 0
            and phase.get("timing_trials_run") == 0,
            "require all nine privately recreated sources without candidate use",
        )
        for path, original in frozen_owners.items():
            item = owners[path]
            privately_applied = path in {
                "candidates/rust/py_bridge.c",
                "candidates/rust_candidate.py",
            }
            if path == "candidates/rust/py_bridge.c":
                expected_sha, expected_bytes = BRIDGE_SOURCE_SHA, BRIDGE_SOURCE_BYTES
            elif path == "candidates/rust_candidate.py":
                expected_sha, expected_bytes = PUBLIC_SOURCE_SHA, PUBLIC_SOURCE_BYTES
            else:
                expected_sha, expected_bytes = original["sha256"], original["bytes"]
            need(
                type(item) is dict
                and item.get("sha256") == expected_sha
                and item.get("bytes") == expected_bytes
                and item.get("exclusive_creation") is True
                and item.get("same_inode_readback_verified") is True
                and item.get("file_fsync_completed") is privately_applied
                and type(item.get("device")) is int
                and type(item.get("inode")) is int and item["inode"] > 0,
                "authenticate the exact independent private Rust source " + path,
            )
            source_identities[path].add((item["device"], item["inode"]))
            overlay = item.get("source_overlay")
            if path == "candidates/rust/py_bridge.c":
                need(
                    type(overlay) is dict and overlay.get("status") == "PASS"
                    and overlay.get("phase") == phase["name"]
                    and overlay.get("source_apply_count") == 1
                    and overlay.get("derived_sha256") == BRIDGE_SOURCE_SHA
                    and overlay.get("derived_bytes") == BRIDGE_SOURCE_BYTES
                    and overlay.get("candidate_original_modified") is False,
                    "verify the genuine once-per-phase private bridge overlay",
                )
            elif path == "candidates/rust_candidate.py":
                need(
                    type(overlay) is dict and overlay.get("status") == "PASS"
                    and overlay.get("phase") == phase["name"]
                    and overlay.get("source_apply_count") == 1
                    and overlay.get("derived_source_sha256") == PUBLIC_SOURCE_SHA
                    and overlay.get("derived_source_bytes") == PUBLIC_SOURCE_BYTES
                    and overlay.get("canonical_candidate_modified") is False
                    and overlay.get("candidate_workers_started") == 0
                    and overlay.get("candidate_imports") == 0,
                    "verify the genuine once-per-phase private public adapter",
                )
            else:
                need(overlay is None,
                     "reject an invented overlay on an unchanged Rust source")
        for role, (filename, fingerprint, size) in native_expected.items():
            native = outputs[role]
            audit = native.get("audit") if type(native) is dict else None
            need(
                type(native) is dict and native.get("role") == role
                and native.get("family") == "rust"
                and native.get("file_name") == filename
                and native.get("sha256") == fingerprint
                and native.get("size_bytes") == size
                and type(native.get("device")) is int
                and type(native.get("inode")) is int
                and native["inode"] > 0
                and native.get("candidate_imported") is False
                and native.get("prebuilt_artifact_read") is False
                and type(audit) is dict and audit.get("role") == role
                and audit.get("external_regex_dependency_count") == 0
                and audit.get("cross_family_dependency_count") == 0,
                "require independently compiled first-party Rust native " + role,
            )
            identities[role].add((native["device"], native["inode"]))
    need(
        all(len(items) == 2 for items in identities.values())
        and all(len(items) == 2 for items in source_identities.values())
        and len(seen) == 28,
        "prove genuinely distinct private native inodes and all process IDs",
    )
    outputs = reproduction.get("native_outputs")
    comparisons = reproduction.get("raw_elf_comparisons")
    need(
        reproduction.get("status") == "PASS"
        and reproduction.get("byte_identical") is True
        and reproduction.get("independent_fresh_phase_count") == 2
        and reproduction.get("unique_process_count") == 28
        and reproduction.get("native_role_count") == 2
        and reproduction.get("source_owners_per_phase") == 9
        and reproduction.get("unchanged_source_owners_per_phase") == 7
        and reproduction.get("bridge_overlay_count") == 2
        and reproduction.get("corrected_public_overlay_count") == 2
        and reproduction.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA
        and reproduction.get("public_derived_sha256") == PUBLIC_SOURCE_SHA
        and reproduction.get("native_libraries_loaded") == 0
        and reproduction.get("prebuilt_artifact_count") == 0
        and reproduction.get("original_sources_modified") is False
        and type(outputs) is dict and set(outputs) == {"engine", "bridge"}
        and type(comparisons) is dict
        and set(comparisons) == {"engine", "bridge"},
        "prove byte-identical from-scratch raw-ELF Rust reproducibility",
    )
    for role, (filename, fingerprint, size) in native_expected.items():
        native = outputs[role]
        comparison = comparisons[role]
        audit = native.get("audit") if type(native) is dict else None
        need(
            type(native) is dict and native.get("file_name") == filename
            and native.get("sha256") == fingerprint
            and native.get("size_bytes") == size
            and native.get("fresh_independent_inode_count") == 2
            and type(audit) is dict and audit.get("role") == role
            and audit.get("external_regex_dependency_count") == 0
            and audit.get("cross_family_dependency_count") == 0
            and type(comparison) is dict
            and comparison.get("byte_identical") is True
            and comparison.get("changed_section_count") == 0
            and comparison.get("total_differing_byte_count") == 0
            and comparison.get("omitted_span_count") == 0
            and comparison.get("phase_a_bytes") == size
            and comparison.get("phase_b_bytes") == size
            and comparison.get("phase_a_sha256") == fingerprint
            and comparison.get("phase_b_sha256") == fingerprint,
            "verify every recorded complete raw-ELF comparison for " + role,
        )
    return {
        "actual_unique_compiler_process_count": len(seen),
        "actual_independent_phase_count": 2,
        "actual_source_owner_count_per_phase": 9,
        "actual_unchanged_source_owner_count_per_phase": 7,
        "actual_native_role_count": 2,
        "actual_independent_native_inode_count_per_role": 2,
        "native_artifacts_byte_identical": True,
        "native_reproducibility": "PASS",
        "native_engine_sha256": ENGINE_NATIVE_SHA,
        "native_engine_bytes": ENGINE_NATIVE_BYTES,
        "native_bridge_sha256": BRIDGE_NATIVE_SHA,
        "native_bridge_bytes": BRIDGE_NATIVE_BYTES,
        "external_regex_native_dependency_count": 0,
        "cross_family_native_dependency_count": 0,
    }


def authenticate_build(
    archive_pin: str, receipt_pin: str, previous: dict,
) -> tuple[dict, dict[str, str]]:
    need(
        checked(archive_pin, "actual corrected Rust V13 source-build archive")
        == ARCHIVE[1]
        and checked(receipt_pin, "actual corrected Rust V13 source-build receipt")
        == RECEIPT[1],
        "pin only the authentic two separately published Rust V13 build owners",
    )
    compressed, archive = read_owner(
        ARCHIVE[0], ARCHIVE[1], ARCHIVE[2], private=True,
        device=ARCHIVE[3], inode=ARCHIVE[4],
    )
    receipt_raw, receipt_owner = read_owner(
        RECEIPT[0], RECEIPT[1], RECEIPT[2], private=True,
        device=RECEIPT[3], inode=RECEIPT[4],
    )
    need(
        (archive["device"], archive["inode"])
        != (receipt_owner["device"], receipt_owner["inode"]),
        "require distinct durable owner-only Rust source-build evidence",
    )
    receipt = document(receipt_raw, "actual corrected Rust V13 build receipt")
    published = receipt.get("archive_publication")
    directory = receipt.get("archive_directory_fsync")
    need(
        type(published) is dict
        and published.get("path") == str(ROOT / ARCHIVE[0])
        and published.get("sha256") == archive["sha256"]
        and published.get("bytes") == archive["bytes"]
        and published.get("device") == archive["device"]
        and published.get("inode") == archive["inode"]
        and published.get("exclusive_creation") is True
        and published.get("same_inode_readback_verified") is True
        and published.get("file_fsync_completed") is True
        and type(published.get("write_calls")) is int
        and published["write_calls"] > 0
        and type(directory) is dict
        and directory.get("completed") is True,
        "bind the exact fsynced private Rust build receipt to its actual archive",
    )
    need(
        receipt.get("schema")
        == "rebar-phase2-owned-rust-pattern-repr-source-build-v13-"
        "durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == "rust"
        and receipt.get("label") == "phase2-v13-rust-pattern-repr-original-p0"
        and receipt.get("source_sha256") == BUILD_SOURCE[1]
        and receipt.get("protocol_sha256") == BUILD_PROTOCOL[1]
        and receipt.get("contract_sha256") == BUILD_CONTRACT[1]
        and receipt.get("archive_relative") == ARCHIVE[0]
        and receipt.get("archive_sha256") == ARCHIVE[1]
        and receipt.get("archive_bytes") == ARCHIVE[2]
        and receipt.get("uncompressed_sha256") == PLAIN_SHA
        and receipt.get("uncompressed_bytes") == PLAIN_BYTES,
        "authenticate a real Rust source build, not a candidate matching pass",
    )
    need(
        receipt.get("expected_actual_compiler_process_count") == 28
        and receipt.get("actual_compiler_process_count") == 28
        and receipt.get("bridge_overlay_apply_count") == 2
        and receipt.get("corrected_public_overlay_apply_count") == 2
        and receipt.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA
        and receipt.get("public_derived_sha256") == PUBLIC_SOURCE_SHA
        and receipt.get("prepublication_repository_evidence_owner_lower_bound")
        == 159
        and receipt.get("prepublication_authenticated_reference_lower_bound")
        == 164
        and receipt.get("new_actual_evidence_owner_count") == 2
        and receipt.get("repository_evidence_owner_lower_bound_after_publication")
        == 161
        and receipt.get("authenticated_reference_lower_bound_after_publication")
        == 166
        and receipt.get("repository_evidence_owner_count_after_publication")
        == "NOT MEASURED"
        and receipt.get("authenticated_history_reference_count_after_publication")
        == "NOT MEASURED",
        "report only actual compiler counts and the 161/166 lower bounds",
    )
    need(
        receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("candidate_imports") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("candidate_qualified") is False
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "never treat a successful source build as Rust correctness or speed",
    )
    _, source = read_owner(*BUILD_SOURCE)
    _, protocol = read_owner(*BUILD_PROTOCOL)
    contract_raw, contract = read_owner(*BUILD_CONTRACT)
    frozen = document(contract_raw, "exact independently frozen Rust V13 build")
    oracle = frozen.get("oracle")
    original = frozen.get("first_party_rust_source")
    bridge = frozen.get("first_party_bridge_overlay")
    public = frozen.get("corrected_first_party_public_overlay")
    history = frozen.get("current_history")
    plan = frozen.get("future_native_build")
    evidence = frozen.get("future_evidence")
    need(
        frozen.get("schema")
        == "rebar-phase2-owned-rust-pattern-repr-source-build-v13-source-freeze"
        and frozen.get("version") == 13
        and frozen.get("source")
        == {"path": BUILD_SOURCE[0], "sha256": BUILD_SOURCE[1]}
        and frozen.get("protocol")
        == {"path": BUILD_PROTOCOL[0], "sha256": BUILD_PROTOCOL[1]}
        and type(oracle) is dict
        and oracle.get("case_execution_denominator") == 31237
        and oracle.get("suite_count") == 13
        and oracle.get("named_private_waiver_count") == 13
        and oracle.get("supplementary_signature_case_count") == 50
        and oracle.get("supplementary_signature_reference_status") == "PASS"
        and oracle.get("supplementary_signature_reference_cases_executed") == 50
        and oracle.get("supplementary_signature_reference_process_count") == 2
        and oracle.get("supplementary_signature_candidate_status") == "NOT RUN"
        and oracle.get("supplementary_signature_candidate_cases_executed") == 0
        and oracle.get("supplementary_signature_cases_included_in_original_denominator")
        is False,
        "bind the build to original 31,237 cases and 50 passing Python references",
    )
    need(
        type(original) is dict and original.get("family") == "rust"
        and original.get("owner_count") == 9
        and original.get("cargo_package_count") == 1
        and original.get("external_dependency_count") == 0
        and original.get("external_regex_dependency_count") == 0
        and original.get("cross_family_dependency_count") == 0
        and original.get("fallback") == "FORBIDDEN"
        and original.get("third_party_regex_engine") == "FORBIDDEN"
        and original.get("other_candidate_engine") == "FORBIDDEN"
        and type(bridge) is dict and type(bridge.get("derived")) is dict
        and bridge["derived"].get("sha256") == BRIDGE_SOURCE_SHA
        and bridge["derived"].get("bytes") == BRIDGE_SOURCE_BYTES
        and type(public) is dict and type(public.get("derived")) is dict
        and public["derived"].get("sha256") == PUBLIC_SOURCE_SHA
        and public["derived"].get("bytes") == PUBLIC_SOURCE_BYTES,
        "authenticate nine owned sources and both genuine private overlays",
    )
    need(
        type(history) is dict
        and history.get("repository_evidence_owner_lower_bound") == 159
        and history.get("authenticated_reference_lower_bound") == 164
        and history.get("rust_semantic_mismatch_count") == 1036
        and history.get("rust_verified_passing_case_count") == 8965
        and history.get("actual_zig_v3_semantic_mismatch_count") == 1764
        and history.get("c_semantic_mismatch_count") == 1230
        and type(plan) is dict
        and plan.get("phase_count") == 2
        and plan.get("processes_per_phase") == 14
        and plan.get("total_actual_processes_required") == 28
        and plan.get("ordered_process_names_per_phase") == list(PROCESS_NAMES)
        and plan.get("passing_build_qualifies_candidate") is False
        and plan.get("candidate_execution") == "FORBIDDEN"
        and plan.get("network") == "FORBIDDEN"
        and type(evidence) is dict
        and evidence.get("prebuild_repository_evidence_owner_lower_bound") == 159
        and evidence.get("prebuild_authenticated_reference_lower_bound") == 164,
        "preserve actual matching failures and the explicit offline build boundary",
    )
    report = inflate_build_report(compressed)
    need(
        report.get("schema")
        == "rebar-phase2-owned-rust-pattern-repr-source-build-v13-"
        "actual-corrected-dual-overlay-build"
        and report.get("version") == 13 and report.get("status") == "PASS"
        and report.get("family") == "rust"
        and report.get("label") == receipt["label"]
        and report.get("source_sha256") == BUILD_SOURCE[1]
        and report.get("protocol_sha256") == BUILD_PROTOCOL[1]
        and report.get("contract_sha256") == BUILD_CONTRACT[1]
        and report.get("phase_count") == 2
        and report.get("expected_actual_compiler_process_count") == 28
        and report.get("actual_compiler_process_count") == 28
        and report.get("bridge_overlay_apply_count") == 2
        and report.get("corrected_public_overlay_apply_count") == 2
        and report.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA
        and report.get("public_derived_sha256") == PUBLIC_SOURCE_SHA,
        "require the full 28-process independently observed Rust build report",
    )
    need(
        report.get("prepublication_repository_evidence_owner_lower_bound") == 159
        and report.get("prepublication_authenticated_reference_lower_bound") == 164
        and report.get("candidate_correctness") == "NOT MEASURED"
        and report.get("candidate_processes_started") == 0
        and report.get("candidate_imports") == 0
        and report.get("native_libraries_loaded") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("performance") == "NOT MEASURED"
        and report.get("memory") == "NOT MEASURED"
        and report.get("hidden_cases_read") == 0
        and report.get("holdout") == "NOT OPENED"
        and report.get("winner_selected") is False,
        "distinguish real source compilation from matching, runtime and speed",
    )
    proven = validate_build_phases(report, frozen)
    context = report.get("frozen_context")
    need(
        type(context) is dict and context.get("status") == "PASS"
        and context.get("case_execution_denominator") == 31237
        and context.get("suite_count") == 13
        and context.get("named_private_waiver_count") == 13
        and context.get("authenticated_source_owner_count") == 53
        and context.get("cargo_package_count") == 1
        and context.get("external_dependency_count") == 0
        and context.get("external_regex_dependency_count") == 0
        and context.get("cross_family_dependency_count") == 0
        and context.get("repository_evidence_owner_lower_bound") == 159
        and context.get("authenticated_reference_lower_bound") == 164
        and context.get("actual_rust_semantic_mismatch_count") == 1036
        and context.get("actual_rust_verified_passing_case_count") == 8965
        and context.get("actual_c_semantic_mismatch_count") == 1230
        and context.get("actual_zig_v3_semantic_mismatch_count") == 1764
        and context.get("supplementary_signature_case_count") == 50
        and context.get("supplementary_signature_reference_status") == "PASS"
        and context.get("supplementary_signature_reference_cases_executed") == 50
        and context.get("supplementary_signature_reference_process_ids") == [81, 82]
        and context.get("supplementary_signature_candidate_status") == "NOT RUN"
        and context.get("supplementary_signature_candidate_cases_executed") == 0
        and context.get("qualified_candidate_count") == 0,
        "validate actual frozen build context and preserve all prior evidence",
    )
    need(
        previous.get("authenticated_evidence_owner_lower_bound") == 159
        and previous.get("authenticated_history_reference_lower_bound") == 164,
        "append actual Rust build only to the independently frozen V35 lower bound",
    )
    proof = {
        "schema": SCHEMA + "-authenticated-corrected-rust-v13-source-build",
        "status": "PASS", "build_status": "PASS",
        "family": "rust",
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "source": source, "protocol": protocol, "contract": contract,
        "archive": archive, "receipt": receipt_owner,
        "publication_receipt": receipt,
        "actual_compiler_process_count": 28,
        **proven,
        "bridge_overlay_apply_count": 2,
        "corrected_public_overlay_apply_count": 2,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA,
        "bridge_derived_bytes": BRIDGE_SOURCE_BYTES,
        "public_derived_sha256": PUBLIC_SOURCE_SHA,
        "public_derived_bytes": PUBLIC_SOURCE_BYTES,
        "prepublication_evidence_owner_lower_bound": 159,
        "prepublication_history_reference_lower_bound": 164,
        "new_distinct_build_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 161,
        "authenticated_history_reference_lower_bound": 166,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "new_rust_matching_test_status": "NOT RUN",
        "new_rust_matching_case_executions": 0,
        "new_rust_candidate_worker_count": 0,
        "candidate_qualified": False,
        "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "build_report_gzip_inflation_count": 1,
        "build_report_compressed_bytes_read": ARCHIVE[2],
        "build_report_uncompressed_bytes_read": PLAIN_BYTES,
        "build_report_uncompressed_sha256": PLAIN_SHA,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "matching_archives_opened_by_graph": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, {ARCHIVE[0]: ARCHIVE[1], RECEIPT[0]: RECEIPT[1]}


def validate(snapshot: object) -> None:
    need(
        type(snapshot) is dict
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("baseline_passed") == 31237
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("preserved_v35_evidence_owner_lower_bound") == 159
        and snapshot.get("preserved_v35_history_reference_lower_bound") == 164
        and snapshot.get("new_rust_v13_build_evidence_owner_count") == 2
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 161
        and snapshot.get("all_digest_addressed_history_path_count") == 166
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 161
        and snapshot.get("authenticated_history_reference_lower_bound") == 166
        and snapshot.get("evidence_owner_count_is_authenticated_lower_bound")
        is True,
        "derive only genuine lower bounds: 159 + 2 and 164 + 2",
    )
    for name, mismatches, passes in (
        ("rust_v4_original_campaign", 1036, 8965),
        ("rust_v3_original_campaign", 1087, 7438),
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
        ("zig_v3_original_campaign", 1764, 3711),
    ):
        tested = snapshot.get(name)
        need(
            type(tested) is dict and tested.get("status") == "FAIL"
            and tested.get("actual_candidate_workers") == 13
            and tested.get("completed_suite_count") == 13
            and tested.get("semantic_mismatch_count") == mismatches
            and tested.get("verified_passing_case_count") == passes
            and tested.get("infrastructure_failure_count") == 0
            and tested.get("candidate_qualified") is False,
            "preserve the genuine previous completed matching outcome " + name,
        )
    actual = snapshot.get("rust_v13_corrected_source_build")
    need(
        type(actual) is dict
        and actual.get("schema")
        == SCHEMA + "-authenticated-corrected-rust-v13-source-build"
        and actual.get("status") == "PASS"
        and actual.get("build_status") == "PASS"
        and actual.get("family") == "rust"
        and actual.get("label") == "phase2-v13-rust-pattern-repr-original-p0"
        and actual.get("actual_compiler_process_count") == 28
        and actual.get("actual_unique_compiler_process_count") == 28
        and actual.get("actual_independent_phase_count") == 2
        and actual.get("actual_source_owner_count_per_phase") == 9
        and actual.get("actual_unchanged_source_owner_count_per_phase") == 7
        and actual.get("actual_native_role_count") == 2
        and actual.get("actual_independent_native_inode_count_per_role") == 2
        and actual.get("native_artifacts_byte_identical") is True
        and actual.get("native_reproducibility") == "PASS",
        "claim a 28-process reproducible Rust build only from full actual evidence",
    )
    need(
        actual.get("bridge_overlay_apply_count") == 2
        and actual.get("corrected_public_overlay_apply_count") == 2
        and actual.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA
        and actual.get("bridge_derived_bytes") == BRIDGE_SOURCE_BYTES
        and actual.get("public_derived_sha256") == PUBLIC_SOURCE_SHA
        and actual.get("public_derived_bytes") == PUBLIC_SOURCE_BYTES
        and actual.get("native_engine_sha256") == ENGINE_NATIVE_SHA
        and actual.get("native_engine_bytes") == ENGINE_NATIVE_BYTES
        and actual.get("native_bridge_sha256") == BRIDGE_NATIVE_SHA
        and actual.get("native_bridge_bytes") == BRIDGE_NATIVE_BYTES
        and actual.get("external_regex_native_dependency_count") == 0
        and actual.get("cross_family_native_dependency_count") == 0,
        "verify both privately applied overlays and independently owned native roles",
    )
    archive, receipt = actual.get("archive"), actual.get("receipt")
    need(
        type(archive) is dict and archive.get("path") == ARCHIVE[0]
        and archive.get("sha256") == ARCHIVE[1]
        and archive.get("bytes") == ARCHIVE[2]
        and archive.get("device") == ARCHIVE[3]
        and archive.get("inode") == ARCHIVE[4]
        and archive.get("mode") == "0600" and archive.get("nlink") == 1
        and archive.get("uid") == os.geteuid()
        and type(receipt) is dict and receipt.get("path") == RECEIPT[0]
        and receipt.get("sha256") == RECEIPT[1]
        and receipt.get("bytes") == RECEIPT[2]
        and receipt.get("device") == RECEIPT[3]
        and receipt.get("inode") == RECEIPT[4]
        and receipt.get("mode") == "0600" and receipt.get("nlink") == 1
        and receipt.get("uid") == os.geteuid()
        and (archive.get("device"), archive.get("inode"))
        != (receipt.get("device"), receipt.get("inode")),
        "require two genuinely separate private Rust source-build owners",
    )
    published = actual.get("publication_receipt")
    need(
        type(published) is dict
        and published.get("status") == "PASS"
        and published.get("build_status") == "PASS"
        and published.get("actual_compiler_process_count") == 28
        and published.get("bridge_overlay_apply_count") == 2
        and published.get("corrected_public_overlay_apply_count") == 2
        and published.get("candidate_correctness") == "NOT MEASURED"
        and published.get("candidate_processes_started") == 0
        and published.get("candidate_qualified") is False,
        "distinguish source-build PASS from unmeasured Rust matching",
    )
    need(
        actual.get("prepublication_evidence_owner_lower_bound") == 159
        and actual.get("prepublication_history_reference_lower_bound") == 164
        and actual.get("new_distinct_build_evidence_owner_count") == 2
        and actual.get("authenticated_evidence_owner_lower_bound") == 161
        and actual.get("authenticated_history_reference_lower_bound") == 166
        and actual.get("evidence_owner_count_is_authenticated_lower_bound")
        is True
        and actual.get("history_reference_count_is_authenticated_lower_bound")
        is True
        and actual.get("exact_whole_repository_evidence_owner_count")
        == "NOT MEASURED"
        and actual.get("exact_whole_repository_reference_count")
        == "NOT MEASURED",
        "label 161/166 as proven lower bounds and never invent a repo census",
    )
    need(
        actual.get("candidate_correctness") == "NOT MEASURED"
        and actual.get("new_rust_matching_test_status") == "NOT RUN"
        and actual.get("new_rust_matching_case_executions") == 0
        and actual.get("new_rust_candidate_worker_count") == 0
        and actual.get("candidate_qualified") is False
        and actual.get("actual_candidate_imports") == 0
        and actual.get("actual_candidate_processes_started") == 0
        and actual.get("native_libraries_loaded") == 0
        and actual.get("build_report_gzip_inflation_count") == 1
        and actual.get("build_report_compressed_bytes_read") == ARCHIVE[2]
        and actual.get("build_report_uncompressed_bytes_read") == PLAIN_BYTES
        and actual.get("build_report_uncompressed_sha256") == PLAIN_SHA
        and actual.get("reference_archive_gzip_inflation_count") == 0
        and actual.get("matching_archive_gzip_inflation_count") == 0
        and actual.get("matching_archives_opened_by_graph") == 0,
        "never fabricate candidate workers or inflate a candidate matching archive",
    )
    need(
        actual.get("hidden_cases_read") == 0
        and actual.get("clock_samples") == 0
        and actual.get("timing_trials_run") == 0
        and actual.get("native_source_build_independence") == "VERIFIED"
        and actual.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and actual.get("production_runtime_delegation_audit")
        == "NOT ESTABLISHED"
        and actual.get("performance") == "NOT MEASURED"
        and actual.get("memory") == "NOT MEASURED"
        and actual.get("confidence_intervals") == "NOT MEASURED"
        and actual.get("undefined_behavior") == "NOT MEASURED"
        and actual.get("holdout") == "NOT OPENED"
        and actual.get("winner_selected") is False,
        "leave runtime delegation, speed and hidden holdout genuinely unmeasured",
    )
    need(
        snapshot.get("additional_signature_frozen_case_count") == 50
        and snapshot.get("additional_signature_reference_status") == "PASS"
        and snapshot.get("additional_signature_reference_cases_executed") == 50
        and snapshot.get("additional_signature_reference_process_count") == 2
        and snapshot.get("additional_signature_reference_process_ids") == [81, 82]
        and snapshot.get("additional_signature_candidate_status") == "NOT RUN"
        and snapshot.get("additional_signature_candidate_cases_executed") == 0
        and snapshot.get("additional_cases_included_in_original_denominator")
        is False
        and snapshot.get("additional_signature_record_vector_sha256")
        == VECTOR_SHA
        and snapshot.get("rust_v13_source_build_status") == "PASS"
        and snapshot.get("rust_v13_candidate_correctness") == "NOT MEASURED"
        and snapshot.get("rust_v13_matching_test_status") == "NOT RUN"
        and snapshot.get("rust_v13_candidate_worker_count") == 0
        and snapshot.get("rust_v13_source_build_process_count") == 28
        and snapshot.get("rust_v13_independent_phase_count") == 2
        and snapshot.get("native_source_build_independence") == "VERIFIED"
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("production_runtime_delegation_audit")
        == "NOT ESTABLISHED",
        "preserve all additional Python references and mark new Rust matching NOT RUN",
    )
    need(
        snapshot.get("build_report_gzip_inflation_count") == 1
        and snapshot.get("build_report_uncompressed_bytes_read") == PLAIN_BYTES
        and snapshot.get("reference_archive_gzip_inflation_count") == 0
        and snapshot.get("matching_archive_gzip_inflation_count") == 0
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("hidden_cases_read") == 0
        and snapshot.get("performance_files_read") == 0
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "run no candidates, no extra references, no clocks and no holdout",
    )


def xml(value: object) -> str:
    return (
        str(value).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
    )


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "actual V36 renderer")
    checked(inputs, "actual V36 graph inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1755" '
        'viewBox="0 0 1440 1755" role="img" '
        'aria-labelledby="v36-title v36-description">',
        '<title id="v36-title">Building a faster Python re: corrected Rust '
        'builds reproducibly, but compatibility remains untested</title>',
        '<desc id="v36-description">A new first-party Rust engine was built '
        'in two independently owned private phases with 28 distinct successful '
        'compiler and inspection processes. Both native outputs reproduce '
        'byte-for-byte. Matching has NOT RUN for this corrected Rust engine: '
        'the last tested Rust still has 1,036 differences and 8,965 '
        'confirmed passes. C has 1,230 differences; corrected Zig has 1,764. '
        'The frozen Python baseline remains 31,237 checks, and 50 additional '
        'Python signature references passed in processes 81 and 82. '
        'Candidate signature checks are NOT RUN. At least 161 evidence owners '
        'and 166 history references are authenticated. Runtime no-delegation '
        'is NOT ESTABLISHED. Speed and memory are NOT MEASURED; the '
        '4,194,304-case holdout is unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        '"Segoe UI",sans-serif}.title{font-size:26px;font-weight:760;fill:'
        '#16324f}.heading{font-size:19px;font-weight:750;fill:#16324f}'
        '.body{font-size:14px;fill:#42556c}.name{font-size:14px;font-weight:'
        '720;fill:#16324f}.pass{font-size:12px;font-weight:760;fill:#00794c}'
        '.fail{font-size:12px;font-weight:750;fill:#a75c13}.pending{font-size:'
        '12px;font-weight:740;fill:#53667b}.big{font-size:20px;font-weight:'
        '760;fill:#16324f}.small{font-size:11px;fill:#42556c}.foot{font-size:'
        '10px;fill:#53667b}</style>',
        '<rect width="1440" height="1755" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="53" class="title">Can we build a faster '
        'replacement for Python re?</text>',
        '<text x="46" y="81" class="body">New Rust built twice from '
        'project-owned source. Its compatibility has NOT RUN; no candidate '
        'is yet qualified or benchmarked.</text>',
    ]
    cards = (
        ("31,237", "unchanged original checks"),
        ("50 / 50", "extra Python checks pass"),
        ("28", "actual Rust build processes"),
        ("2", "independent Rust builds"),
        ("1,036", "last tested Rust differences"),
        ("0", "compatible replacements"),
        ("≥161 / 166", "authenticated lower bounds"),
    )
    for index, (number, label) in enumerate(cards):
        left = 44 + index * 195
        lines.extend((
            f'<rect x="{left}" y="100" width="184" height="82" rx="11" '
            'fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{left + 9}" y="133" class="big">{xml(number)}</text>',
            f'<text x="{left + 9}" y="157" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="201" width="1352" height="437" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="235" class="heading">1. Overall: which '
        'implementations have actually passed?</text>',
        '<text x="66" y="260" class="body">Only fully tested candidates '
        'can be compared for compatibility. Building new Rust is not a '
        'matching result or a speed result.</text>',
    ))
    rows = (
        ("Python re — original reference", "REFERENCE PASS", 0, 31237, "pass"),
        ("Rust — last fully tested version", "NOT COMPATIBLE", 1036, 8965, "fail"),
        ("C — current fully tested version", "NOT COMPATIBLE", 1230, 7325, "fail"),
        ("Zig — corrected and fully tested", "NOT COMPATIBLE", 1764, 3711, "fail"),
    )
    for index, (name, outcome, differences, confirmed, kind) in enumerate(rows):
        top = 284 + index * 60
        width = round(560 * differences / 1764) if differences else 0
        color = "#0b8d61" if differences == 0 else "#b77a36"
        lines.extend((
            f'<text x="67" y="{top + 16}" class="name">{xml(name)}</text>',
            f'<text x="1370" y="{top + 16}" class="{kind}" '
            f'text-anchor="end">{xml(outcome)}</text>',
            f'<rect x="68" y="{top + 27}" width="560" height="10" '
            'rx="5" fill="#edf1f5"/>',
            f'<rect x="68" y="{top + 27}" width="{width}" height="10" '
            f'rx="5" fill="{color}"/>',
            f'<text x="645" y="{top + 37}" class="small">'
            f'{differences:,} differences; {confirmed:,} confirmed passes</text>',
        ))
    lines.extend((
        '<rect x="67" y="543" width="1304" height="67" rx="10" '
        'fill="#f3f6fb" stroke="#dae4ee"/>',
        '<text x="83" y="570" class="name">Rust — newly corrected V13, '
        'independently built twice</text>',
        '<text x="1355" y="570" class="pending" text-anchor="end">'
        'BUILT; MATCHING NOT RUN</text>',
        '<text x="84" y="593" class="small">28 real build processes; '
        '0 new candidate workers; build success does not prove '
        'compatibility or speed.</text>',
        '<rect x="44" y="655" width="1352" height="262" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="689" class="heading">2. What the new '
        'Rust build really established</text>',
    ))
    build_notes = (
        "Two separate, privately owned build phases each started from all nine project-owned Rust sources.",
        "All 28 distinct compiler and native-inspection processes completed successfully.",
        "Both phases independently applied the corrected public adapter and corrected Python bridge.",
        "The Rust engine and Python bridge reproduced byte-for-byte across distinct native inodes.",
        "The recorded native dependency audit found no external regular-expression engine.",
        "Source and native-build independence are verified; complete runtime no-delegation is NOT ESTABLISHED.",
        "The corrected Rust candidate ran 0 matching workers: full compatibility is NOT RUN.",
    )
    for index, note in enumerate(build_notes):
        lines.append(
            f'<text x="67" y="{718 + 25 * index}" class="body">'
            f'{xml(note)}</text>'
        )
    lines.extend((
        '<rect x="44" y="936" width="1352" height="270" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="970" class="heading">3. What remains '
        'unproven or unmeasured</text>',
    ))
    remaining = (
        ("Corrected Rust compatibility", "NOT RUN: last actually tested Rust still has 1,036 differences."),
        ("50 additional Python signature checks", "REFERENCE PASS in two Python processes; candidate checks NOT RUN."),
        ("Fully compatible replacement", "NONE: current fully tested Rust, C and Zig all have differences."),
        ("Runtime no-delegation", "NOT ESTABLISHED: native/source independence is not a runtime proof."),
        ("Speed, memory and confidence", "NOT MEASURED: no correctness-qualified candidate exists."),
        ("4,194,304-case final holdout", "NOT OPENED and NOT GENERATED; zero hidden cases read."),
        ("Winner", "NONE: the new Rust build has not yet passed matching or performance."),
    )
    for index, (name, note) in enumerate(remaining):
        top = 1002 + index * 28
        lines.extend((
            f'<text x="68" y="{top}" class="name">{xml(name)}</text>',
            f'<text x="394" y="{top}" class="body">{xml(note)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1225" width="1352" height="326" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1259" class="heading">4. Reading the '
        'actual evidence correctly</text>',
    ))
    details = (
        "The original correctness denominator stays exactly 31,237, with 13 suites and 13 private waivers.",
        "The separately recorded 50 Python-reference checks remain PASS; no candidate ran those checks.",
        "V35 established at least 159 evidence owners and 164 authenticated history references.",
        "The two new actual Rust source-build records establish lower bounds of 161 owners and 166 references.",
        "These are explicitly authenticated lower bounds; the complete workspace count is NOT MEASURED.",
        "Only the bounded 760,477-byte Rust source-build report was decompressed by this graph.",
        "No candidate matching archive and no additional Python-reference archive was decompressed.",
        "No graph worker ran a candidate, compiler, Python reference, benchmark, clock or holdout.",
        "Rust matching remains NOT RUN; speed, runtime delegation and undefined behavior remain unproven.",
    )
    for index, note in enumerate(details):
        lines.append(
            f'<text x="67" y="{1289 + 26 * index}" class="body">'
            f'{xml(note)}</text>'
        )
    lines.extend((
        f'<text x="47" y="1584" class="foot">Inputs SHA-256: '
        f'{xml(inputs)}</text>',
        f'<text x="47" y="1606" class="foot">Renderer SHA-256: '
        f'{xml(source)}</text>',
        f'<text x="47" y="1628" class="foot">Actual Rust source-build '
        f'archive SHA-256: {xml(ARCHIVE[1])}</text>',
        f'<text x="47" y="1650" class="foot">Actual distinct Rust '
        f'source-build receipt SHA-256: {xml(RECEIPT[1])}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(
    source_pin: str, archive_pin: str, receipt_pin: str,
) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_pin = checked(source_pin, "actual V36 graph renderer")
    own, _ = read_owner(SELF, source_pin, os.path.getsize(ROOT / SELF))
    previous, previous_inputs = authenticate_v35()
    proof, additional = authenticate_build(archive_pin, receipt_pin, previous)
    need(
        len(additional) == 2 and len(set(additional)) == 2
        and all(path.startswith("oracle/phase2/evidence/")
                for path in additional),
        "append exactly two genuine first-party Rust source-build owners",
    )
    evidence_bound = previous["authenticated_evidence_owner_lower_bound"] + 2
    history_bound = previous["authenticated_history_reference_lower_bound"] + 2
    need(evidence_bound == 161 and history_bound == 166,
         "derive only authenticated append-only lower bounds")
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update({
        "preserved_v35_evidence_owner_lower_bound": 159,
        "preserved_v35_history_reference_lower_bound": 164,
        "new_rust_v13_build_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": evidence_bound,
        "all_digest_addressed_history_path_count": history_bound,
        "authenticated_evidence_owner_lower_bound": evidence_bound,
        "authenticated_history_reference_lower_bound": history_bound,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "rust_v13_corrected_source_build": copy.deepcopy(proof),
        "rust_v13_source_build_status": "PASS",
        "rust_v13_candidate_correctness": "NOT MEASURED",
        "rust_v13_matching_test_status": "NOT RUN",
        "rust_v13_candidate_worker_count": 0,
        "rust_v13_source_build_process_count": 28,
        "rust_v13_independent_phase_count": 2,
        "build_report_gzip_inflation_count": 1,
        "build_report_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
    })
    validate(snapshot)
    prior = {name: pin(*owner) for name, owner in V35.items()}
    manifest = copy.deepcopy(previous_inputs)
    manifest.update({
        "schema": SCHEMA + "-inputs", "version": 36,
        "python": "3.14.6",
        "renderer": pin(SELF, source_pin, len(own)),
        "previous_overview": prior,
        "actual_rust_v13_corrected_source_build": copy.deepcopy(proof),
        "preserved_v35_evidence_owner_lower_bound": 159,
        "preserved_v35_history_reference_lower_bound": 164,
        "new_rust_v13_build_evidence_owner_count": 2,
        "repository_evidence_owner_count": evidence_bound,
        "all_digest_addressed_history_path_count": history_bound,
        "authenticated_evidence_owner_lower_bound": evidence_bound,
        "authenticated_history_reference_lower_bound": history_bound,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "candidate_qualified_count": 0,
        "rust_v13_source_build_status": "PASS",
        "rust_v13_source_build_process_count": 28,
        "rust_v13_source_build_unique_process_count": 28,
        "rust_v13_independent_phase_count": 2,
        "rust_v13_source_owners_per_phase": 9,
        "rust_v13_native_outputs_byte_identical": True,
        "rust_v13_bridge_overlay_apply_count": 2,
        "rust_v13_corrected_public_overlay_apply_count": 2,
        "rust_v13_candidate_correctness": "NOT MEASURED",
        "rust_v13_matching_test_status": "NOT RUN",
        "rust_v13_candidate_worker_count": 0,
        "rust_v13_source_build_candidate_qualified": False,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "build_report_gzip_inflation_count": 1,
        "build_report_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    })
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source_pin, digest(manifest_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") == "rust":
            family.update({
                "current_v13_corrected_source_build": copy.deepcopy(proof),
                "v13_source_build_status": "PASS",
                "v13_source_build_process_count": 28,
                "v13_matching_test_status": "NOT RUN",
                "v13_candidate_worker_count": 0,
                "v13_candidate_correctness": "NOT MEASURED",
                "v13_source_build_candidate_qualified": False,
                "qualified": False,
                "runtime_no_delegation": "NOT ESTABLISHED",
            })
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 36,
        "status": "PASS", "python": "3.14.6",
        "source": pin(SELF, source_pin, len(own)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw),
                      len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(image), len(image)),
        "previous_overview": prior,
        "snapshot": snapshot, "families": families,
        "preserved_v35_evidence_owner_lower_bound": 159,
        "preserved_v35_history_reference_lower_bound": 164,
        "new_rust_v13_build_evidence_owner_count": 2,
        "repository_evidence_owner_count": evidence_bound,
        "authenticated_digest_addressed_history_paths": history_bound,
        "authenticated_evidence_owner_lower_bound": evidence_bound,
        "authenticated_history_reference_lower_bound": history_bound,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "actual_rust_v13_corrected_source_build": copy.deepcopy(proof),
        "rust_v13_source_build_status": "PASS",
        "rust_v13_source_build_process_count": 28,
        "rust_v13_source_build_unique_process_count": 28,
        "rust_v13_independent_phase_count": 2,
        "rust_v13_source_owners_per_phase": 9,
        "rust_v13_native_outputs_byte_identical": True,
        "rust_v13_bridge_overlay_apply_count": 2,
        "rust_v13_corrected_public_overlay_apply_count": 2,
        "rust_v13_candidate_correctness": "NOT MEASURED",
        "rust_v13_matching_test_status": "NOT RUN",
        "rust_v13_candidate_worker_count": 0,
        "rust_v13_source_build_candidate_qualified": False,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "build_report_gzip_inflation_count": 1,
        "build_report_compressed_bytes_read": ARCHIVE[2],
        "build_report_uncompressed_bytes_read": PLAIN_BYTES,
        "build_report_uncompressed_sha256": PLAIN_SHA,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "uncompressed_c_matching_archive_bytes_read_by_graph": 0,
        "uncompressed_rust_matching_archive_bytes_read_by_graph": 0,
        "uncompressed_zig_matching_archive_bytes_read_by_graph": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", image),
    )


class Wall:
    """Physically prevent real compilation and matching during self-tests."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def __enter__(self) -> Wall:
        def forbid(name: str):
            def blocked(*_args: object, **_kwargs: object) -> object:
                self.blocked += 1
                raise GraphError("V36 source-only effect blocked: " + name)

            return blocked

        groups = (
            (builtins, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "unlink",
                  "remove", "rename", "replace", "mkdir", "makedirs",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "mkdir", "unlink",
                    "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call",
                          "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp")),
            (threading.Thread, ("start",)),
            (zlib, ("decompress", "decompressobj")),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                if hasattr(owner, name):
                    self.saved.append((owner, name, getattr(owner, name)))
                    setattr(owner, name, forbid(name))
        return self

    def __exit__(self, *_errors: object) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def synthetic() -> dict:
    def campaign(mismatches: int, passes: int) -> dict:
        return {
            "status": "FAIL", "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "semantic_mismatch_count": mismatches,
            "verified_passing_case_count": passes,
            "infrastructure_failure_count": 0,
            "candidate_qualified": False,
        }

    archive = {
        "path": ARCHIVE[0], "sha256": ARCHIVE[1], "bytes": ARCHIVE[2],
        "device": ARCHIVE[3], "inode": ARCHIVE[4], "mode": "0600",
        "nlink": 1, "uid": 1000,
    }
    receipt = {
        "path": RECEIPT[0], "sha256": RECEIPT[1], "bytes": RECEIPT[2],
        "device": RECEIPT[3], "inode": RECEIPT[4], "mode": "0600",
        "nlink": 1, "uid": 1000,
    }
    published = {
        "status": "PASS", "build_status": "PASS",
        "actual_compiler_process_count": 28,
        "bridge_overlay_apply_count": 2,
        "corrected_public_overlay_apply_count": 2,
        "candidate_correctness": "NOT MEASURED",
        "candidate_processes_started": 0,
        "candidate_qualified": False,
    }
    proof = {
        "schema": SCHEMA + "-authenticated-corrected-rust-v13-source-build",
        "status": "PASS", "build_status": "PASS", "family": "rust",
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "archive": archive, "receipt": receipt,
        "publication_receipt": published,
        "actual_compiler_process_count": 28,
        "actual_unique_compiler_process_count": 28,
        "actual_independent_phase_count": 2,
        "actual_source_owner_count_per_phase": 9,
        "actual_unchanged_source_owner_count_per_phase": 7,
        "actual_native_role_count": 2,
        "actual_independent_native_inode_count_per_role": 2,
        "native_artifacts_byte_identical": True,
        "native_reproducibility": "PASS",
        "native_engine_sha256": ENGINE_NATIVE_SHA,
        "native_engine_bytes": ENGINE_NATIVE_BYTES,
        "native_bridge_sha256": BRIDGE_NATIVE_SHA,
        "native_bridge_bytes": BRIDGE_NATIVE_BYTES,
        "external_regex_native_dependency_count": 0,
        "cross_family_native_dependency_count": 0,
        "bridge_overlay_apply_count": 2,
        "corrected_public_overlay_apply_count": 2,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA,
        "bridge_derived_bytes": BRIDGE_SOURCE_BYTES,
        "public_derived_sha256": PUBLIC_SOURCE_SHA,
        "public_derived_bytes": PUBLIC_SOURCE_BYTES,
        "prepublication_evidence_owner_lower_bound": 159,
        "prepublication_history_reference_lower_bound": 164,
        "new_distinct_build_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 161,
        "authenticated_history_reference_lower_bound": 166,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "new_rust_matching_test_status": "NOT RUN",
        "new_rust_matching_case_executions": 0,
        "new_rust_candidate_worker_count": 0,
        "candidate_qualified": False,
        "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "build_report_gzip_inflation_count": 1,
        "build_report_compressed_bytes_read": ARCHIVE[2],
        "build_report_uncompressed_bytes_read": PLAIN_BYTES,
        "build_report_uncompressed_sha256": PLAIN_SHA,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "matching_archives_opened_by_graph": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v35_evidence_owner_lower_bound": 159,
        "preserved_v35_history_reference_lower_bound": 164,
        "new_rust_v13_build_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 161,
        "all_digest_addressed_history_path_count": 166,
        "authenticated_evidence_owner_lower_bound": 161,
        "authenticated_history_reference_lower_bound": 166,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "rust_v4_original_campaign": campaign(1036, 8965),
        "rust_v3_original_campaign": campaign(1087, 7438),
        "c_v4_original_campaign": campaign(1230, 7325),
        "zig_v2_original_campaign": campaign(2172, 2847),
        "zig_v3_original_campaign": campaign(1764, 3711),
        "rust_v13_corrected_source_build": proof,
        "rust_v13_source_build_status": "PASS",
        "rust_v13_candidate_correctness": "NOT MEASURED",
        "rust_v13_matching_test_status": "NOT RUN",
        "rust_v13_candidate_worker_count": 0,
        "rust_v13_source_build_process_count": 28,
        "rust_v13_independent_phase_count": 2,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "build_report_gzip_inflation_count": 1,
        "build_report_uncompressed_bytes_read": PLAIN_BYTES,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def forged(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        if value == "FAIL":
            return "PASS"
        if value in ("NOT RUN", "NOT MEASURED", "NOT ESTABLISHED"):
            return "VERIFIED"
        return value + "-forged"
    if type(value) is dict:
        return {}
    if type(value) is list:
        return value[:-1]
    return "forged"


def self_test() -> dict:
    runtime()
    with Wall() as wall:
        base = synthetic()
        validate(base)
        rejected = 0

        def reject(snapshot: dict, label: str) -> None:
            nonlocal rejected
            try:
                validate(snapshot)
            except (GraphError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise GraphError("accepted hostile synthetic V36 evidence: " + label)

        groups = (
            "rust_v4_original_campaign", "rust_v3_original_campaign",
            "c_v4_original_campaign", "zig_v2_original_campaign",
            "zig_v3_original_campaign", "rust_v13_corrected_source_build",
        )
        for key, value in base.items():
            if key in groups:
                continue
            attack = copy.deepcopy(base)
            attack[key] = forged(value)
            reject(attack, "snapshot-" + key)
        for name in groups:
            for key, value in base[name].items():
                attack = copy.deepcopy(base)
                attack[name][key] = forged(value)
                reject(attack, name + "-" + key)
        proof = base["rust_v13_corrected_source_build"]
        for name in ("archive", "receipt", "publication_receipt"):
            for key, value in proof[name].items():
                attack = copy.deepcopy(base)
                attack["rust_v13_corrected_source_build"][name][key] = forged(value)
                reject(attack, name + "-" + key)
        collision = copy.deepcopy(base)
        collision["rust_v13_corrected_source_build"]["receipt"]["device"] = ARCHIVE[3]
        collision["rust_v13_corrected_source_build"]["receipt"]["inode"] = ARCHIVE[4]
        reject(collision, "rust-build-archive-receipt-inode-collision")
        image = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"31,237", b"50 / 50", b"28", b"1,036", b"8,965",
            b"1,230", b"7,325", b"1,764", b"3,711",
            b"BUILT; MATCHING NOT RUN", b"NOT COMPATIBLE",
            b"NOT ESTABLISHED", b"NOT RUN", b"760,477",
            b"lower bounds", b"4,194,304", b"NOT GENERATED",
        ):
            need(phrase.lower() in image.lower(),
                 "reject a misleading build-only Rust overview")
        effects = (
            lambda: builtins.open("forbidden-v36"),
            lambda: os.open("forbidden-v36", os.O_RDONLY),
            lambda: os.stat("forbidden-v36-native"),
            lambda: subprocess.run(("forbidden-v36",)),
            lambda: importlib.import_module("candidates.rust_candidate"),
            lambda: importlib.import_module("re"),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: zlib.decompressobj(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for action in effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("V36 source-only test leaked an actual side effect")
        need(wall.blocked == len(effects),
             "physically block all 11 native-build and matching side effects")
        need(rejected >= 155,
             "exercise forged build, runtime, count, archive and holdout controls")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 36, "status": "PASS", "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13, "qualified_candidate_count": 0,
            "preserved_v35_evidence_owner_lower_bound": 159,
            "preserved_v35_history_reference_lower_bound": 164,
            "new_rust_v13_build_evidence_owner_count": 2,
            "authenticated_evidence_owner_lower_bound": 161,
            "authenticated_history_reference_lower_bound": 166,
            "evidence_owner_count_is_authenticated_lower_bound": True,
            "last_tested_rust_semantic_mismatch_count": 1036,
            "last_tested_rust_verified_passing_case_count": 8965,
            "current_c_semantic_mismatch_count": 1230,
            "current_zig_semantic_mismatch_count": 1764,
            "rust_v13_source_build_status": "PASS",
            "rust_v13_source_build_process_count": 28,
            "rust_v13_independent_phase_count": 2,
            "rust_v13_matching_test_status": "NOT RUN",
            "rust_v13_candidate_correctness": "NOT MEASURED",
            "rust_v13_candidate_worker_count": 0,
            "additional_signature_reference_status": "PASS",
            "additional_signature_reference_cases_executed": 50,
            "additional_signature_reference_process_ids": [81, 82],
            "additional_signature_candidate_status": "NOT RUN",
            "native_source_build_independence": "VERIFIED",
            "runtime_no_delegation": "NOT ESTABLISHED",
            "production_runtime_delegation_audit": "NOT ESTABLISHED",
            "actual_candidate_workers_started_by_graph": 0,
            "actual_candidate_imports": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_activations": 0,
            "canonical_target_reads": 0, "canonical_target_stats": 0,
            "build_report_gzip_inflation_count": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "candidate_matching_archives_opened_by_graph": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(path in allowed and type(raw) is bytes and 0 < len(raw) <= LIMIT,
         "write only the three exclusively reserved V36 graph owners")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(handle, remaining)
            need(type(written) is int and written > 0,
                 "reject a partial exclusive V36 owner")
            remaining = remaining[written:]
        os.fsync(handle)
        observed = os.fstat(handle)
        need(
            observed.st_uid == os.geteuid() and observed.st_nlink == 1
            and observed.st_size == len(raw)
            and stat.S_IMODE(observed.st_mode) == 0o600,
            "reject nonprivate, partial or linked V36 graph output",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    verified, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(verified == raw,
         "re-read exact exclusively durable generated V36 evidence")


def result(
    source: str, archive: str, receipt: str,
    outputs: dict[str, bytes], written: bool, suffix: str,
) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 36, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_rust_v13_build_archive_sha256": archive,
        "actual_rust_v13_build_receipt_sha256": receipt,
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13, "qualified_candidate_count": 0,
        "preserved_v35_evidence_owner_lower_bound": 159,
        "preserved_v35_history_reference_lower_bound": 164,
        "new_rust_v13_build_evidence_owner_count": 2,
        "authenticated_evidence_owner_lower_bound": 161,
        "authenticated_history_reference_lower_bound": 166,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "last_tested_rust_matching_status": "FAIL",
        "last_tested_rust_semantic_mismatch_count": 1036,
        "last_tested_rust_verified_passing_case_count": 8965,
        "c_matching_status": "FAIL", "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_matching_status": "FAIL",
        "zig_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_count": 3711,
        "rust_v13_source_build_status": "PASS",
        "rust_v13_source_build_process_count": 28,
        "rust_v13_source_build_unique_process_count": 28,
        "rust_v13_independent_phase_count": 2,
        "rust_v13_source_owners_per_phase": 9,
        "rust_v13_native_outputs_byte_identical": True,
        "rust_v13_bridge_overlay_apply_count": 2,
        "rust_v13_corrected_public_overlay_apply_count": 2,
        "rust_v13_candidate_correctness": "NOT MEASURED",
        "rust_v13_matching_test_status": "NOT RUN",
        "rust_v13_candidate_worker_count": 0,
        "rust_v13_source_build_candidate_qualified": False,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "outputs_written": written,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "build_report_gzip_inflation_count": 1,
        "build_report_compressed_bytes_read": ARCHIVE[2],
        "build_report_uncompressed_bytes_read": PLAIN_BYTES,
        "build_report_uncompressed_sha256": PLAIN_SHA,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "uncompressed_c_matching_archive_bytes_read": 0,
        "uncompressed_rust_matching_archive_bytes_read": 0,
        "uncompressed_zig_matching_archive_bytes_read": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    for name in (
        "--source-sha256", "--build-archive-sha256",
        "--build-receipt-sha256", "--inputs-sha256",
        "--summary-sha256", "--svg-sha256",
    ):
        parser.add_argument(name)
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(
                all(getattr(args, name) is None for name in (
                    "source_sha256", "build_archive_sha256",
                    "build_receipt_sha256", "inputs_sha256",
                    "summary_sha256", "svg_sha256",
                )),
                "source-only self-tests cannot accept real build owner pins",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "actual V36 graph renderer")
        archive = checked(args.build_archive_sha256,
                          "actual corrected Rust V13 source-build archive")
        receipt = checked(args.build_receipt_sha256,
                          "actual corrected Rust V13 source-build receipt")
        _snapshot, pairs = build(source, archive, receipt)
        outputs = dict(pairs)
        if args.render:
            need(
                args.inputs_sha256 is None and args.summary_sha256 is None
                and args.svg_sha256 is None,
                "publish exactly the three exclusively reserved V36 graph owners",
            )
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(
                canonical(result(source, archive, receipt, outputs,
                                 True, "-published"))
            )
            return 0
        frozen = {
            OUTPUT + ".inputs.json": checked(args.inputs_sha256,
                                               "frozen V36 graph inputs"),
            OUTPUT + ".json": checked(args.summary_sha256,
                                         "frozen V36 graph summary"),
            OUTPUT + ".svg": checked(args.svg_sha256,
                                        "frozen V36 graph image"),
        }
        for path, fingerprint in frozen.items():
            raw, _ = read_owner(path, fingerprint, len(outputs[path]),
                                private=True)
            need(raw == outputs[path],
                 "independently reproduce every generated V36 graph owner")
        sys.stdout.buffer.write(
            canonical(result(source, archive, receipt, outputs,
                             False, "-read-only-frozen-context"))
        )
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            KeyError, AttributeError, struct.error, zlib.error) as error:
        sys.stderr.write("current V36 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
