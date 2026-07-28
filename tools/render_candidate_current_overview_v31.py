#!/usr/bin/env python3
"""Render the actual Rust source build without claiming untested matching."""

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
SELF = "tools/render_candidate_current_overview_v31.py"
OUTPUT = "docs/evidence/candidate-current-overview-v31"
SCHEMA = "rebar-candidate-current-overview-v31"
OWNER_LIMIT = 8 * 1024 * 1024
SOURCE_REPORT_LIMIT = 2 * 1024 * 1024
V30 = {
    "source": (
        "tools/render_candidate_current_overview_v30.py",
        "a8c2bb2e0ccfab0b76b5387437fe48279e01ca1034739a67967f543f1930c507",
        60771,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v30.inputs.json",
        "ea2ea381a22a9a23344ff40505d975aba8d25704d2ad90e03b58018fda44ca0f",
        65902,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v30.json",
        "b04db4e93dc74bb9200c13133c0a33bd33961b5f35e5810e74de65b29fcab534",
        293980,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v30.svg",
        "a3dbbb69c5140d15588463e0e3579d5bea5d95587f1abf444b6679cd3361d4c6",
        12987,
    ),
}
RUST_SOURCE = (
    "tools/reproduce_owned_rust_flag_source_build_v12.py",
    "1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6",
    86933,
)
RUST_PROTOCOL = (
    "oracle/phase2/RUST-FLAG-SOURCE-BUILD-V12.md",
    "822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950",
    5567,
)
RUST_CONTRACT = (
    "oracle/phase2/rust-flag-source-build-v12.json",
    "c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592",
    13038,
)
RUST_ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz",
    "840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d",
    108325,
    2064,
    524643,
)
RUST_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-publication-receipt.json",
    "1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f",
    2109,
    2064,
    524644,
)
RUST_EXPANDED = (
    "a69fe5a873891c3aee51cf8e711877125b06c079057b04daeb86720bbd2dc75f",
    757826,
)
PUBLIC_DERIVED = "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
BRIDGE_DERIVED = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
ENGINE_SHA = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
PHASE_NAMES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols",
    "engine_sections", "engine_notes", "bridge_sections", "bridge_notes",
)


class GraphError(Exception):
    """Reject invented matching, substituted evidence, or external effects."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only actual bounded owner bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise GraphError("reject noncanonical V31 evidence") from error


def checked(value: object, label: str) -> str:
    need(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "require the exact lowercase SHA-256 for " + label,
    )
    return value


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "require exact isolated stable CPython 3.14.6",
    )


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        result: dict[str, object] = {}
        for key, value in items:
            need(key not in result, "reject duplicate JSON key in " + label)
            result[key] = value
        return result

    try:
        result = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("reject nonfinite JSON in " + label)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed JSON in " + label) from error
    need(type(result) is dict and canonical(result) == raw, "require canonical " + label)
    return result


def read_owner(
    path: str, fingerprint: str, size: int, *, private: bool = False,
    device: int | None = None, inode: int | None = None,
) -> tuple[bytes, dict]:
    need(
        type(path) is str and bool(path) and not path.startswith("/")
        and ".." not in Path(path).parts and "." not in Path(path).parts,
        "require an exact first-party relative owner",
    )
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= OWNER_LIMIT, "bound exact owner " + path)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories: list[int] = []
    handle: int | None = None
    try:
        directories.append(os.open(str(ROOT), directory_flags))
        parts = Path(path).parts
        for part in parts[:-1]:
            directories.append(os.open(part, directory_flags, dir_fd=directories[-1]))
        handle = os.open(parts[-1], file_flags, dir_fd=directories[-1])
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and before.st_size == size
            and (not private or stat.S_IMODE(before.st_mode) == 0o600)
            and (device is None or before.st_dev == device)
            and (inode is None or before.st_ino == inode),
            "reject a substituted, foreign, linked, or unprivate owner " + path,
        )
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            need(bool(piece), "reject a truncated exact owner " + path)
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(handle, 1) == b"", "reject trailing owner bytes " + path)
        raw = b"".join(pieces)
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_size, after.st_nlink)
            and digest(raw) == fingerprint,
            "reject exact owner changed during authenticated reading " + path,
        )
        return raw, {
            "path": path, "sha256": fingerprint, "bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "nlink": after.st_nlink, "uid": after.st_uid,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for descriptor in reversed(directories):
            os.close(descriptor)


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= OWNER_LIMIT, "bound a frozen graph pin")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def load_v30() -> types.ModuleType:
    raw, _ = read_owner(*V30["source"])
    previous = types.ModuleType("_rebar_actual_v30_for_corrected_rust_build_v31")
    previous.__file__ = str(ROOT / V30["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    need(
        previous.SCHEMA == "rebar-candidate-current-overview-v30"
        and previous.SELF == V30["source"][0],
        "load only the exact independently committed V30 renderer",
    )
    return previous


def authenticate_v30() -> tuple[dict, dict, dict[str, str]]:
    old = load_v30()
    _, earlier, _, references = old.authenticate_v29()
    actual_c, added = old.authenticate_c_original(
        old.C_ARCHIVE[1], old.C_RECEIPT[1], earlier, references,
    )
    need(
        len(references) == 152 and len(added) == 2
        and not (set(references) & set(added)),
        "independently recover the genuine V30 evidence history",
    )
    references = {**references, **added}
    need(len(references) == 154, "preserve every one of 154 real V30 references")
    raw_inputs, _ = read_owner(*V30["inputs"], private=True)
    raw_summary, _ = read_owner(*V30["summary"], private=True)
    raw_svg, _ = read_owner(*V30["svg"], private=True)
    inputs = document(raw_inputs, "actual V30 frozen graph inputs")
    summary = document(raw_summary, "actual V30 frozen graph summary")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "retain the actual complete V30 snapshot")
    old.validate(snapshot)
    need(
        summary.get("schema") == old.SCHEMA + "-summary"
        and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count") == 149
        and summary.get("authenticated_digest_addressed_history_paths") == 154
        and summary.get("suite_count") == 13
        and summary.get("full_case_denominator") == 31237
        and summary.get("private_waiver_count") == 13
        and summary.get("qualified_candidate_count") == 0
        and summary.get("actual_c_v4_original_campaign") == actual_c
        and summary.get("rust_original_campaign_status") == "FAIL"
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087
        and summary.get("rust_original_campaign_verified_passing_case_count") == 7438
        and summary.get("c_original_campaign_status") == "FAIL"
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_status") == "FAIL"
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
        and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
        and inputs.get("repository_evidence_owner_count") == 149
        and inputs.get("all_digest_addressed_history_path_count") == 154
        and raw_svg == old.make_svg(snapshot, V30["source"][1], V30["inputs"][1]),
        "independently reproduce the exact four truthful V30 graph owners",
    )
    return summary, inputs, references


def expand_source_report(compressed: bytes) -> dict:
    need(
        len(compressed) == RUST_ARCHIVE[2]
        and compressed[:3] == b"\x1f\x8b\x08"
        and struct.unpack("<I", compressed[4:8])[0] == 0
        and struct.unpack("<I", compressed[-4:])[0] == RUST_EXPANDED[1]
        and RUST_EXPANDED[1] < SOURCE_REPORT_LIMIT,
        "accept only the exact bounded deterministic Rust source-build archive",
    )
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = inflater.decompress(compressed, SOURCE_REPORT_LIMIT + 1)
    except zlib.error as error:
        raise GraphError("reject an invalid bounded V12 source-build archive") from error
    need(
        inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail
        and len(plain) == RUST_EXPANDED[1]
        and digest(plain) == RUST_EXPANDED[0],
        "reject an excessive, concatenated, altered, or truncated source report",
    )
    return document(plain, "complete bounded actual Rust V12 source-build report")


def authenticate_rust_v12(
    archive_pin: str, receipt_pin: str, references: dict[str, str],
) -> tuple[dict, dict[str, str]]:
    need(
        checked(archive_pin, "actual V12 source-build archive") == RUST_ARCHIVE[1]
        and checked(receipt_pin, "actual V12 source-build receipt") == RUST_RECEIPT[1],
        "caller-pin both actually published and distinct Rust V12 build owners",
    )
    compressed, archive = read_owner(
        RUST_ARCHIVE[0], RUST_ARCHIVE[1], RUST_ARCHIVE[2], private=True,
        device=RUST_ARCHIVE[3], inode=RUST_ARCHIVE[4],
    )
    receipt_raw, receipt_owner = read_owner(
        RUST_RECEIPT[0], RUST_RECEIPT[1], RUST_RECEIPT[2], private=True,
        device=RUST_RECEIPT[3], inode=RUST_RECEIPT[4],
    )
    need(
        (archive["device"], archive["inode"])
        != (receipt_owner["device"], receipt_owner["inode"])
        and archive["path"] not in references
        and receipt_owner["path"] not in references,
        "count only two genuinely new, private, independently owned V12 files",
    )
    receipt = document(receipt_raw, "genuine Rust V12 durable source-build receipt")
    publication = receipt.get("archive_publication")
    synced = receipt.get("archive_directory_fsync")
    need(
        type(publication) is dict and type(synced) is dict
        and receipt.get("schema")
        == "rebar-phase2-owned-rust-flag-source-build-v12-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == "rust"
        and receipt.get("label") == "phase2-v12-rust-flag-original-p0"
        and receipt.get("source_sha256") == RUST_SOURCE[1]
        and receipt.get("protocol_sha256") == RUST_PROTOCOL[1]
        and receipt.get("contract_sha256") == RUST_CONTRACT[1]
        and receipt.get("archive_relative") == archive["path"]
        and receipt.get("archive_sha256") == archive["sha256"]
        and receipt.get("archive_bytes") == archive["bytes"]
        and publication.get("path") == str(ROOT / archive["path"])
        and publication.get("sha256") == archive["sha256"]
        and publication.get("bytes") == archive["bytes"]
        and publication.get("device") == archive["device"]
        and publication.get("inode") == archive["inode"]
        and publication.get("exclusive_creation") is True
        and publication.get("file_fsync_completed") is True
        and publication.get("same_inode_readback_verified") is True
        and synced.get("completed") is True,
        "authenticate the actual independently synced V12 source-build receipt",
    )
    need(
        receipt.get("historical_evidence_owner_count") == 149
        and receipt.get("historical_authenticated_reference_count") == 154
        and receipt.get("new_actual_evidence_owner_count") == 2
        and receipt.get("repository_evidence_owner_count_after_publication") == 151
        and receipt.get("authenticated_history_reference_count_after_publication") == 156
        and receipt.get("bridge_derived_sha256") == BRIDGE_DERIVED
        and receipt.get("public_derived_sha256") == PUBLIC_DERIVED
        and receipt.get("bridge_overlay_apply_count") == 2
        and receipt.get("corrected_public_overlay_apply_count") == 2
        and receipt.get("expected_actual_compiler_process_count") == 28
        and receipt.get("actual_compiler_process_count") == 28
        and receipt.get("uncompressed_sha256") == RUST_EXPANDED[0]
        and receipt.get("uncompressed_bytes") == RUST_EXPANDED[1]
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("candidate_qualified") is False
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("candidate_imports") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "a source build is not a matching, speed, or compatibility experiment",
    )
    _, source = read_owner(*RUST_SOURCE)
    _, protocol = read_owner(*RUST_PROTOCOL)
    contract_raw, contract_owner = read_owner(*RUST_CONTRACT)
    frozen = document(contract_raw, "exact separately frozen Rust V12 source contract")
    history = frozen.get("current_history")
    family = frozen.get("first_party_rust_source")
    policy = frozen.get("future_native_build")
    corrected = frozen.get("corrected_first_party_public_overlay")
    bridge = frozen.get("first_party_bridge_overlay")
    need(
        frozen.get("schema")
        == "rebar-phase2-owned-rust-flag-source-build-v12-source-freeze"
        and frozen.get("version") == 12
        and frozen.get("source") == {"path": RUST_SOURCE[0], "sha256": RUST_SOURCE[1]}
        and frozen.get("protocol")
        == {"path": RUST_PROTOCOL[0], "sha256": RUST_PROTOCOL[1]}
        and type(history) is dict
        and history.get("repository_evidence_owner_count") == 149
        and history.get("authenticated_digest_addressed_history_paths") == 154
        and history.get("suite_count") == 13
        and history.get("case_execution_denominator") == 31237
        and history.get("named_private_waiver_count") == 13
        and history.get("rust_semantic_mismatch_count") == 1087
        and history.get("c_semantic_mismatch_count") == 1230
        and history.get("zig_semantic_mismatch_count") == 2172
        and history.get("qualified_candidate_count") == 0,
        "bind the V12 freeze to actual V30 matching and its unchanged denominator",
    )
    expected_graph = [pin(*V30[name]) for name in ("source", "inputs", "summary", "svg")]
    need(
        frozen.get("current_graph_v30") == expected_graph
        and type(family) is dict
        and family.get("family") == "rust"
        and len(family.get("owners", [])) == 9
        and family.get("cargo_package_count") == 1
        and family.get("external_dependency_count") == 0
        and family.get("external_regex_dependency_count") == 0
        and family.get("stdlib_re_engine") == "FORBIDDEN"
        and family.get("cpython_sre_engine") == "FORBIDDEN"
        and family.get("third_party_regex_engine") == "FORBIDDEN"
        and family.get("other_candidate_engine") == "FORBIDDEN"
        and family.get("fallback") == "FORBIDDEN"
        and family.get("canonical_source_mutation") == "FORBIDDEN"
        and type(corrected) is dict
        and corrected.get("derived", {}).get("sha256") == PUBLIC_DERIVED
        and corrected.get("derived", {}).get("bytes") == 31464
        and type(bridge) is dict
        and bridge.get("derived", {}).get("sha256") == BRIDGE_DERIVED
        and bridge.get("derived", {}).get("bytes") == 176118
        and type(policy) is dict
        and policy.get("phase_count") == 2
        and policy.get("processes_per_phase") == 14
        and policy.get("total_actual_processes_required") == 28
        and policy.get("ordered_process_names_per_phase") == list(PROCESS_NAMES)
        and policy.get("cargo_net_offline") is True
        and policy.get("network") == "FORBIDDEN"
        and policy.get("native_loading") == "FORBIDDEN"
        and policy.get("candidate_execution") == "FORBIDDEN",
        "reject an external regex, guessed flags, swapped source, or unsafe Rust build",
    )
    actual = expand_source_report(compressed)
    phases = actual.get("phases")
    processes = actual.get("compiler_processes")
    reproduction = actual.get("reproducibility")
    need(
        actual.get("schema")
        == "rebar-phase2-owned-rust-flag-source-build-v12-actual-corrected-dual-overlay-build"
        and actual.get("version") == 12
        and actual.get("status") == "PASS"
        and actual.get("family") == "rust"
        and actual.get("label") == receipt["label"]
        and actual.get("source_sha256") == RUST_SOURCE[1]
        and actual.get("protocol_sha256") == RUST_PROTOCOL[1]
        and actual.get("contract_sha256") == RUST_CONTRACT[1]
        and actual.get("historical_evidence_owner_count") == 149
        and actual.get("historical_authenticated_reference_count") == 154
        and actual.get("bridge_derived_sha256") == BRIDGE_DERIVED
        and actual.get("public_derived_sha256") == PUBLIC_DERIVED
        and actual.get("bridge_overlay_apply_count") == 2
        and actual.get("corrected_public_overlay_apply_count") == 2
        and actual.get("phase_count") == 2
        and actual.get("expected_actual_compiler_process_count") == 28
        and actual.get("actual_compiler_process_count") == 28
        and type(phases) is list and len(phases) == 2
        and [phase.get("name") for phase in phases] == list(PHASE_NAMES)
        and type(processes) is list and len(processes) == 28
        and type(reproduction) is dict,
        "require the complete actual corrected Rust report, not receipt-only claims",
    )
    need(
        actual.get("candidate_correctness") == "NOT MEASURED"
        and actual.get("candidate_qualified") is False
        and actual.get("candidate_processes_started") == 0
        and actual.get("candidate_imports") == 0
        and actual.get("native_libraries_loaded") == 0
        and actual.get("hidden_cases_read") == 0
        and actual.get("clock_samples") == 0
        and actual.get("timing_trials_run") == 0
        and actual.get("performance") == "NOT MEASURED"
        and actual.get("memory") == "NOT MEASURED"
        and actual.get("holdout") == "NOT OPENED"
        and actual.get("winner_selected") is False,
        "reject candidate matching, timing, native loading, or hidden holdout use",
    )
    pids: set[int] = set()
    for index, process in enumerate(processes):
        need(
            type(process) is dict
            and process.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
            and type(process.get("pid")) is int and process["pid"] > 0
            and process["pid"] not in pids
            and process.get("exit_status") == 0,
            "require all 28 ordered, distinct, successful actual compiler processes",
        )
        pids.add(process["pid"])
    need(
        reproduction.get("status") == "PASS"
        and reproduction.get("independent_fresh_phase_count") == 2
        and reproduction.get("source_owners_per_phase") == 9
        and reproduction.get("unchanged_source_owners_per_phase") == 7
        and reproduction.get("bridge_overlay_count") == 2
        and reproduction.get("corrected_public_overlay_count") == 2
        and reproduction.get("bridge_derived_sha256") == BRIDGE_DERIVED
        and reproduction.get("public_derived_sha256") == PUBLIC_DERIVED
        and reproduction.get("unique_process_count") == 28
        and reproduction.get("byte_identical") is True
        and reproduction.get("native_role_count") == 2
        and reproduction.get("prebuilt_artifact_count") == 0
        and reproduction.get("native_libraries_loaded") == 0
        and reproduction.get("original_sources_modified") is False,
        "require two independently reproduced first-party source-build phases",
    )
    frozen_owners = {owner["path"]: owner for owner in family["owners"]}
    fresh_identities: set[tuple[int, int]] = set()
    phase_outputs: list[dict] = []
    for phase_index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        need(
            type(owners) is dict and set(owners) == set(frozen_owners),
            "preserve all nine original source identities in each actual Rust phase",
        )
        for path, original in frozen_owners.items():
            owner = owners[path]
            expected_sha = (
                BRIDGE_DERIVED if path == "candidates/rust/py_bridge.c"
                else PUBLIC_DERIVED if path == "candidates/rust_candidate.py"
                else original["sha256"]
            )
            expected_bytes = (
                176118 if path == "candidates/rust/py_bridge.c"
                else 31464 if path == "candidates/rust_candidate.py"
                else original["bytes"]
            )
            need(
                type(owner) is dict
                and owner.get("sha256") == expected_sha
                and owner.get("bytes") == expected_bytes
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int
                and (owner["device"], owner["inode"]) not in fresh_identities,
                "reject a reused, missing, uncorrected, or substituted private source",
            )
            fresh_identities.add((owner["device"], owner["inode"]))
            if path in ("candidates/rust/py_bridge.c", "candidates/rust_candidate.py"):
                overlay = owner.get("source_overlay")
                field = (
                    "derived_sha256" if path == "candidates/rust/py_bridge.c"
                    else "derived_source_sha256"
                )
                need(
                    type(overlay) is dict
                    and overlay.get("status") == "PASS"
                    and overlay.get("phase") == PHASE_NAMES[phase_index]
                    and overlay.get("source_apply_count") == 1
                    and overlay.get(field) == expected_sha,
                    "verify the real corrected Python adapter and bridge provenance",
                )
        outputs = phase.get("native_outputs")
        need(
            type(outputs) is dict and set(outputs) == {"engine", "bridge"},
            "require both actual independently produced Rust native roles",
        )
        phase_outputs.append(outputs)
    roles: dict[str, dict] = {}
    reproductions = reproduction.get("native_outputs")
    comparisons = reproduction.get("raw_elf_comparisons")
    need(
        type(reproductions) is dict and set(reproductions) == {"engine", "bridge"}
        and type(comparisons) is dict and set(comparisons) == {"engine", "bridge"},
        "retain complete actual native-role and raw-ELF reproduction evidence",
    )
    for role, filename in (
        ("engine", "_rust_engine.so"),
        ("bridge", "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
    ):
        left, right = phase_outputs[0][role], phase_outputs[1][role]
        recorded = reproductions[role]
        compared = comparisons[role]
        need(
            type(left) is dict and type(right) is dict and type(recorded) is dict
            and type(compared) is dict
            and left.get("file_name") == right.get("file_name") == filename
            and left.get("sha256") == right.get("sha256") == recorded.get("sha256")
            and left.get("size_bytes") == right.get("size_bytes")
            == recorded.get("size_bytes")
            and (left.get("device"), left.get("inode"))
            != (right.get("device"), right.get("inode"))
            and left.get("audit") == right.get("audit") == recorded.get("audit")
            and recorded.get("fresh_independent_inode_count") == 2
            and compared.get("byte_identical") is True,
            "authenticate both distinct, byte-identical actual native source outputs",
        )
        if role == "engine":
            need(
                recorded.get("sha256") == ENGINE_SHA,
                "never claim the corrected Python adapter changed historical engine bytes",
            )
        roles[role] = {
            "file_name": filename, "sha256": recorded["sha256"],
            "bytes": recorded["size_bytes"],
            "independent_phase_owner_count": 2,
            "phase_a_device": left["device"], "phase_a_inode": left["inode"],
            "phase_b_device": right["device"], "phase_b_inode": right["inode"],
            "byte_identical": True,
        }
    added = {archive["path"]: archive["sha256"], receipt_owner["path"]: receipt_owner["sha256"]}
    need(
        len(added) == 2 and not (set(added) & set(references)),
        "derive exactly two actual Rust source-build evidence owners",
    )
    proof = {
        "schema": SCHEMA + "-authenticated-actual-rust-v12-source-build",
        "status": "PASS", "build_status": "PASS", "family": "rust",
        "label": receipt["label"],
        "source": source, "protocol": protocol, "contract": contract_owner,
        "archive": archive, "receipt": receipt_owner,
        "publication_receipt": receipt,
        "historical_evidence_owner_count": 149,
        "historical_authenticated_reference_count": 154,
        "new_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count_after_publication": 151,
        "authenticated_reference_count_after_publication": 156,
        "actual_compiler_process_count": 28,
        "actual_unique_compiler_process_id_count": len(pids),
        "independent_phase_count": 2,
        "source_owner_count_per_phase": 9,
        "unchanged_source_owner_count_per_phase": 7,
        "corrected_public_overlay_apply_count": 2,
        "bridge_overlay_apply_count": 2,
        "corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "corrected_bridge_source_sha256": BRIDGE_DERIVED,
        "native_role_count": 2,
        "byte_identical_native_role_count": 2,
        "native_engine_bytes_changed": False,
        "native_roles": roles,
        "reproducibility": "PASS",
        "first_party_rust_source_owner_count": 9,
        "external_dependency_count": 0,
        "external_regex_dependency_count": 0,
        "cross_family_engine_count": 0,
        "stdlib_regex_engine_count": 0,
        "prebuilt_artifact_count": 0,
        "original_source_targets_modified": False,
        "candidate_correctness": "NOT MEASURED",
        "matching_test_status": "NOT MEASURED",
        "actual_candidate_workers": 0,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "candidate_qualified": False,
        "source_archive_uncompressed_sha256": RUST_EXPANDED[0],
        "source_archive_uncompressed_bytes_verified": RUST_EXPANDED[1],
        "candidate_matching_archive_opened_by_graph": False,
        "candidate_matching_archive_bytes_read_by_graph": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, added


def validate(snapshot: object) -> None:
    need(
        type(snapshot) is dict
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("baseline_passed") == 31237
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("preserved_v30_repository_evidence_owner_count") == 149
        and snapshot.get("preserved_v30_digest_addressed_history_path_count") == 154
        and snapshot.get("new_rust_v12_source_build_repository_evidence_owner_count") == 2
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 151
        and snapshot.get("all_digest_addressed_history_path_count") == 156,
        "derive exactly 149 + 2 evidence owners and 154 + 2 actual references",
    )
    for key, mismatches, passes in (
        ("rust_v3_original_campaign", 1087, 7438),
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
    ):
        actual = snapshot.get(key)
        need(
            type(actual) is dict
            and actual.get("status") == "FAIL"
            and actual.get("actual_candidate_workers") == 13
            and actual.get("completed_suite_count") == 13
            and actual.get("semantic_mismatch_count") == mismatches
            and actual.get("verified_passing_case_count") == passes
            and actual.get("infrastructure_failure_count") == 0
            and actual.get("candidate_qualified") is False,
            "preserve the genuine current complete original matching failure " + key,
        )
    old_c = snapshot.get("c_v10_repaired_original_campaign")
    need(
        type(old_c) is dict and old_c.get("status") == "FAIL"
        and old_c.get("semantic_mismatch_count") == 1262
        and old_c.get("verified_passing_case_count") == 7325
        and type(old_c.get("suite_results")) is list
        and len(old_c["suite_results"]) == 13,
        "never invent new per-suite rows from historical C matching results",
    )
    rust = snapshot.get("rust_v12_corrected_flag_source_build")
    need(
        type(rust) is dict
        and rust.get("schema") == SCHEMA + "-authenticated-actual-rust-v12-source-build"
        and rust.get("status") == "PASS"
        and rust.get("build_status") == "PASS"
        and rust.get("family") == "rust"
        and rust.get("label") == "phase2-v12-rust-flag-original-p0"
        and rust.get("historical_evidence_owner_count") == 149
        and rust.get("historical_authenticated_reference_count") == 154
        and rust.get("new_repository_evidence_owner_count") == 2
        and rust.get("repository_evidence_owner_count_after_publication") == 151
        and rust.get("authenticated_reference_count_after_publication") == 156
        and rust.get("actual_compiler_process_count") == 28
        and rust.get("actual_unique_compiler_process_id_count") == 28
        and rust.get("independent_phase_count") == 2
        and rust.get("source_owner_count_per_phase") == 9
        and rust.get("unchanged_source_owner_count_per_phase") == 7
        and rust.get("corrected_public_overlay_apply_count") == 2
        and rust.get("bridge_overlay_apply_count") == 2
        and rust.get("corrected_public_adapter_sha256") == PUBLIC_DERIVED
        and rust.get("corrected_bridge_source_sha256") == BRIDGE_DERIVED
        and rust.get("native_role_count") == 2
        and rust.get("byte_identical_native_role_count") == 2
        and rust.get("native_engine_bytes_changed") is False
        and rust.get("reproducibility") == "PASS"
        and rust.get("external_dependency_count") == 0
        and rust.get("external_regex_dependency_count") == 0
        and rust.get("cross_family_engine_count") == 0
        and rust.get("stdlib_regex_engine_count") == 0
        and rust.get("prebuilt_artifact_count") == 0
        and rust.get("original_source_targets_modified") is False,
        "reject a forged actual first-party corrected Rust source build",
    )
    archive, receipt = rust.get("archive"), rust.get("receipt")
    need(
        type(archive) is dict and archive.get("path") == RUST_ARCHIVE[0]
        and archive.get("sha256") == RUST_ARCHIVE[1]
        and archive.get("bytes") == RUST_ARCHIVE[2]
        and archive.get("device") == RUST_ARCHIVE[3]
        and archive.get("inode") == RUST_ARCHIVE[4]
        and archive.get("mode") == "0600" and archive.get("nlink") == 1
        and type(receipt) is dict and receipt.get("path") == RUST_RECEIPT[0]
        and receipt.get("sha256") == RUST_RECEIPT[1]
        and receipt.get("bytes") == RUST_RECEIPT[2]
        and receipt.get("device") == RUST_RECEIPT[3]
        and receipt.get("inode") == RUST_RECEIPT[4]
        and receipt.get("mode") == "0600" and receipt.get("nlink") == 1
        and (archive.get("device"), archive.get("inode"))
        != (receipt.get("device"), receipt.get("inode")),
        "reject aliased or invented actual owner-only Rust build evidence",
    )
    publication = rust.get("publication_receipt")
    need(
        type(publication) is dict and publication.get("status") == "PASS"
        and publication.get("build_status") == "PASS"
        and publication.get("candidate_correctness") == "NOT MEASURED"
        and publication.get("candidate_qualified") is False
        and publication.get("actual_compiler_process_count") == 28
        and publication.get("archive_sha256") == RUST_ARCHIVE[1],
        "never represent source-build receipt PASS as matching PASS",
    )
    need(
        rust.get("candidate_correctness") == "NOT MEASURED"
        and rust.get("matching_test_status") == "NOT MEASURED"
        and rust.get("actual_candidate_workers") == 0
        and rust.get("candidate_processes_started") == 0
        and rust.get("candidate_imports") == 0
        and rust.get("native_libraries_loaded") == 0
        and rust.get("candidate_qualified") is False
        and rust.get("source_archive_uncompressed_sha256") == RUST_EXPANDED[0]
        and rust.get("source_archive_uncompressed_bytes_verified") == RUST_EXPANDED[1]
        and rust.get("candidate_matching_archive_opened_by_graph") is False
        and rust.get("candidate_matching_archive_bytes_read_by_graph") == 0
        and rust.get("hidden_cases_read") == 0
        and rust.get("clock_samples") == 0
        and rust.get("timing_trials_run") == 0
        and rust.get("performance") == "NOT MEASURED"
        and rust.get("memory") == "NOT MEASURED"
        and rust.get("holdout") == "NOT OPENED"
        and rust.get("winner_selected") is False,
        "never infer Rust compatibility, speed, memory, or holdout results from a build",
    )
    need(
        snapshot.get("performance") == "NOT MEASURED"
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
        "reject false timing, confidence, hidden cases, winner, or opened holdout",
    )


def xml(value: object) -> str:
    return (
        str(value).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
    )


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "V31 graph source")
    checked(inputs, "V31 graph inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1750" viewBox="0 0 1440 1750" role="img" aria-labelledby="v31-title v31-description">',
        '<title id="v31-title">Building a faster Python re: the new Rust version is built but has not passed the full compatibility test</title>',
        '<desc id="v31-description">The newly corrected first-party Rust adapter was built in two independent phases and 28 observed compiler processes. Its compatibility has not been tested. The last fully tested Rust version had 1,087 differences; the tested C version had 1,230; the tested Zig version had 2,172. All 31,237 original Python reference checks pass. No replacement has qualified. Exactly 151 actual evidence owners and 156 references are authenticated. Speed, memory, and confidence are not measured; the 4,194,304-case final holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:27px;font-weight:760;fill:#16324f}.heading{font-size:20px;font-weight:740;fill:#16324f}.body{font-size:14px;fill:#42556c}.name{font-size:15px;font-weight:720;fill:#16324f}.pass{font-size:13px;font-weight:750;fill:#00794c}.fail{font-size:13px;font-weight:740;fill:#a15e00}.pending{font-size:13px;font-weight:740;fill:#53667b}.big{font-size:20px;font-weight:760;fill:#16324f}.small{font-size:12px;fill:#42556c}.foot{font-size:10px;fill:#53667b}</style>',
        '<rect width="1440" height="1750" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="54" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="46" y="81" class="body">New Rust version built; full compatibility test not yet run. Speed is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0", "compatible replacements"),
        ("1,087", "last tested Rust differences"),
        ("1,230", "tested C differences"),
        ("2,172", "tested Zig differences"),
        ("28", "new Rust build processes"),
        ("151 / 156", "evidence / references"),
    )
    for index, (number, label) in enumerate(cards):
        x = 44 + index * 195
        lines.extend((
            f'<rect x="{x}" y="98" width="184" height="82" rx="11" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 10}" y="132" class="big">{xml(number)}</text>',
            f'<text x="{x + 10}" y="158" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="197" width="1352" height="552" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="232" class="heading">1. Which versions actually match Python?</text>',
        '<text x="65" y="257" class="body">A successful build does not mean a matching test has run or that the new version is compatible.</text>',
    ))
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original reference checks pass.", "pass"),
        ("Rust — last fully tested version", "NOT COMPATIBLE", "13 completed original test groups; 1,087 differences; 7,438 verified passes.", "fail"),
        ("Rust — new corrected adapter and reproducible build", "BUILT; NOT YET TESTED", "Two private builds; 28 observed processes; 0 matching workers. Compatibility NOT MEASURED.", "pending"),
        ("C — fully tested current version", "NOT COMPATIBLE", "13 completed original test groups; 1,230 differences; 7,325 verified passes.", "fail"),
        ("C — fully tested earlier version", "NOT COMPATIBLE", "1,262 historical differences; the same 7,325 verified passes.", "fail"),
        ("Zig — fully tested current version", "NOT COMPATIBLE", "13 completed original test groups; 2,172 differences; 2,847 verified passes.", "fail"),
        ("Zig — earlier setup attempt", "SETUP STOPPED; 0 TESTS", "A separately preserved historical attempt started no matching workers.", "fail"),
        ("Speed, memory, and final ranking", "NOT MEASURED", "No compatible replacement, final speed comparison, confidence interval, or winner.", "pending"),
    )
    for index, (name, status, detail, kind) in enumerate(rows):
        y = 273 + index * 53
        lines.extend((
            f'<rect x="63" y="{y}" width="1314" height="47" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="79" y="{y + 19}" class="name">{xml(name)}</text>',
            f'<text x="1358" y="{y + 19}" class="{kind}" text-anchor="end">{xml(status)}</text>',
            f'<text x="80" y="{y + 37}" class="small">{xml(detail)}</text>',
        ))
    lines.append('<text x="65" y="727" class="body">Rust build success records an independently corrected Python adapter; it does not claim that the native engine changed or matching improved.</text>')
    lines.extend((
        '<rect x="44" y="766" width="1352" height="410" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="802" class="heading">2. What did the previous C test show in each group?</text>',
        '<text x="65" y="826" class="body">These are the recorded 13 groups for the historical 1,262-difference C run, not invented groups for a newer result.</text>',
        '<text x="80" y="850" class="small">HISTORICAL ORIGINAL PYTHON TEST GROUP</text>',
        '<text x="1040" y="850" class="small" text-anchor="end">CHECKS</text>',
        '<text x="1355" y="850" class="small" text-anchor="end">HISTORICAL C RESULT ONLY</text>',
    ))
    for index, row in enumerate(snapshot["c_v10_repaired_original_campaign"]["suite_results"]):
        need(type(row) is dict, "preserve each actual historical C test group")
        count = row.get("case_execution_denominator")
        mismatches = row.get("mismatch_count")
        need(
            type(count) is int and count >= 0
            and type(mismatches) is int and mismatches >= 0,
            "reject invented or malformed historical C test-group outcomes",
        )
        label = row.get("display_name", row.get("suite"))
        need(type(label) is str and bool(label), "preserve real historical group names")
        y = 858 + index * 22
        colour = "#f8fafd" if index % 2 == 0 else "#ffffff"
        result = "PASSED" if mismatches == 0 else f"{mismatches:,} DIFFERENCES"
        kind = "pass" if mismatches == 0 else "fail"
        lines.extend((
            f'<rect x="64" y="{y}" width="1312" height="21" rx="4" fill="{colour}"/>',
            f'<text x="80" y="{y + 15}" class="small">{xml(label)}</text>',
            f'<text x="1040" y="{y + 15}" class="small" text-anchor="end">{count:,}</text>',
            f'<text x="1355" y="{y + 15}" class="{kind}" text-anchor="end">{xml(result)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1193" width="1352" height="438" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1228" class="heading">3. What did the new Rust build prove?</text>',
    ))
    notes = (
        "Its corrected Python adapter and C bridge were independently rebuilt in two private phases.",
        "All 28 recorded build and inspection processes succeeded; both native roles reproduced.",
        "The existing Rust native engine has the same observed bytes; no native-engine improvement is claimed.",
        "The new Rust version ran 0 compatibility workers: its matching result is NOT MEASURED.",
        "The last actually tested Rust still has 1,087 differences; tested C and Zig still have 1,230 and 2,172.",
        "149 previous evidence files + one actual Rust build archive + one receipt = 151; 156 references.",
        "No large C, Rust, or Zig matching failure archive is decompressed.",
        "Speed, memory, confidence intervals, and undefined behavior are NOT MEASURED.",
        "The 4,194,304-case final comparison has not been generated or opened.",
        "No replacement is qualified, ranked, or selected as a winner.",
    )
    for index, note in enumerate(notes):
        lines.append(f'<text x="66" y="{1260 + index * 29}" class="body">{xml(note)}</text>')
    lines.extend((
        f'<text x="47" y="1660" class="foot">Inputs SHA-256: {xml(inputs)}</text>',
        f'<text x="47" y="1680" class="foot">Renderer SHA-256: {xml(source)}</text>',
        f'<text x="47" y="1700" class="foot">Actual Rust source-build archive: {xml(RUST_ARCHIVE[1])}</text>',
        f'<text x="47" y="1720" class="foot">Actual distinct Rust source-build receipt: {xml(RUST_RECEIPT[1])}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(source_sha: str, archive_sha: str, receipt_sha: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_sha = checked(source_sha, "actual V31 graph source")
    raw_source, _ = read_owner(SELF, source_sha, os.path.getsize(ROOT / SELF))
    previous, prior_inputs, references = authenticate_v30()
    actual, added = authenticate_rust_v12(archive_sha, receipt_sha, references)
    need(
        len(references) == 154 and len(added) == 2
        and not (set(references) & set(added)),
        "derive new Rust build evidence only after reproducing all V30 references",
    )
    combined = {**references, **added}
    owner_count = previous["repository_evidence_owner_count"] + len(added)
    need(owner_count == 151 and len(combined) == 156, "derive exactly 151 owners and 156 references")
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update({
        "preserved_v30_repository_evidence_owner_count": 149,
        "preserved_v30_digest_addressed_history_path_count": 154,
        "new_rust_v12_source_build_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": owner_count,
        "all_digest_addressed_history_path_count": len(combined),
        "rust_v12_corrected_flag_source_build": copy.deepcopy(actual),
        "rust_v12_source_build_status": "PASS",
        "rust_v12_source_build_candidate_correctness": "NOT MEASURED",
        "rust_v12_source_build_matching_test_status": "NOT MEASURED",
        "rust_v12_source_build_candidate_worker_count": 0,
        "rust_v12_source_build_process_count": 28,
        "rust_v12_source_build_independent_phase_count": 2,
        "rust_v12_source_build_candidate_qualified": False,
        "rust_v12_corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "rust_v12_corrected_bridge_source_sha256": BRIDGE_DERIVED,
    })
    validate(snapshot)
    prior = {name: pin(*value) for name, value in V30.items()}
    manifest = copy.deepcopy(prior_inputs)
    manifest.update({
        "schema": SCHEMA + "-inputs", "version": 31, "python": "3.14.6",
        "renderer": pin(SELF, source_sha, len(raw_source)),
        "previous_overview": prior,
        "actual_rust_v12_corrected_source_build": copy.deepcopy(actual),
        "current_complete_rust_campaign": copy.deepcopy(snapshot["rust_v3_original_campaign"]),
        "current_complete_c_campaign": copy.deepcopy(snapshot["c_v4_original_campaign"]),
        "actual_complete_zig_campaign": copy.deepcopy(snapshot["zig_v2_original_campaign"]),
        "preserved_v30_repository_evidence_owner_count": 149,
        "preserved_v30_digest_addressed_history_path_count": 154,
        "new_rust_v12_source_build_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": owner_count,
        "all_digest_addressed_history_path_count": len(combined),
        "candidate_qualified_count": 0,
        "rust_v12_build_status": "PASS",
        "rust_v12_candidate_correctness": "NOT MEASURED",
        "rust_v12_matching_test_status": "NOT MEASURED",
        "rust_v12_actual_candidate_workers": 0,
        "rust_v12_actual_compiler_process_count": 28,
        "rust_v12_independent_phase_count": 2,
        "rust_v12_corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "rust_v12_corrected_bridge_source_sha256": BRIDGE_DERIVED,
        "rust_v12_native_engine_bytes_changed": False,
        "rust_v12_candidate_qualified": False,
        "source_build_archive_uncompressed_bytes_verified": RUST_EXPANDED[1],
    })
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source_sha, digest(manifest_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") == "rust":
            family.update({
                "v12_corrected_source_build": copy.deepcopy(actual),
                "v12_source_build_status": "PASS",
                "v12_matching_test_status": "NOT MEASURED",
                "v12_candidate_worker_count": 0,
                "v12_candidate_qualified": False,
                "qualified": False,
            })
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 31, "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_sha, len(raw_source)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw), len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(image), len(image)),
        "previous_overview": prior, "snapshot": snapshot, "families": families,
        "preserved_v30_repository_evidence_owner_count": 149,
        "preserved_v30_authenticated_reference_path_count": 154,
        "new_rust_v12_source_build_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": owner_count,
        "authenticated_digest_addressed_history_paths": len(combined),
        "qualified_candidate_count": 0,
        "actual_rust_v12_corrected_source_build": copy.deepcopy(actual),
        "rust_v12_source_build_status": "PASS",
        "rust_v12_source_build_candidate_correctness": "NOT MEASURED",
        "rust_v12_source_build_matching_test_status": "NOT MEASURED",
        "rust_v12_source_build_candidate_worker_count": 0,
        "rust_v12_source_build_process_count": 28,
        "rust_v12_source_build_unique_process_count": 28,
        "rust_v12_source_build_phase_count": 2,
        "rust_v12_corrected_public_overlay_apply_count": 2,
        "rust_v12_bridge_overlay_apply_count": 2,
        "rust_v12_corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "rust_v12_corrected_bridge_source_sha256": BRIDGE_DERIVED,
        "rust_v12_native_engine_bytes_changed": False,
        "rust_v12_source_build_candidate_qualified": False,
        "rust_v12_source_build_external_regex_dependency_count": 0,
        "rust_v12_source_build_cross_family_engine_count": 0,
        "rust_v12_source_build_stdlib_regex_engine_count": 0,
        "rust_v12_source_build_candidate_imports": 0,
        "rust_v12_source_build_candidate_processes_started": 0,
        "rust_v12_source_build_native_libraries_loaded": 0,
        "source_build_archive_uncompressed_bytes_verified": RUST_EXPANDED[1],
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
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
    """Physically prevent synthetic tests from accessing the outside world."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def __enter__(self) -> Wall:
        def forbid(name: str):
            def blocked(*_args: object, **_kwargs: object) -> object:
                self.blocked += 1
                raise GraphError("V31 source-only side effect blocked: " + name)
            return blocked

        groups = (
            (builtins, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "unlink", "remove", "rename", "replace", "mkdir", "makedirs", "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text", "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                if hasattr(owner, name):
                    self.saved.append((owner, name, getattr(owner, name)))
                    setattr(owner, name, forbid(name))
        return self

    def __exit__(self, *_error: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic() -> dict:
    old_rows = [
        {"suite": f"historical-{index}",
         "display_name": f"Previous test group {index + 1}",
         "case_execution_denominator": 2000,
         "mismatch_count": 1262 if index == 0 else 0}
        for index in range(13)
    ]
    campaign = lambda mismatches, passes: {
        "status": "FAIL", "actual_candidate_workers": 13,
        "completed_suite_count": 13,
        "semantic_mismatch_count": mismatches,
        "verified_passing_case_count": passes,
        "infrastructure_failure_count": 0, "candidate_qualified": False,
    }
    archive = {
        "path": RUST_ARCHIVE[0], "sha256": RUST_ARCHIVE[1],
        "bytes": RUST_ARCHIVE[2], "device": RUST_ARCHIVE[3],
        "inode": RUST_ARCHIVE[4], "mode": "0600", "nlink": 1,
    }
    receipt_owner = {
        "path": RUST_RECEIPT[0], "sha256": RUST_RECEIPT[1],
        "bytes": RUST_RECEIPT[2], "device": RUST_RECEIPT[3],
        "inode": RUST_RECEIPT[4], "mode": "0600", "nlink": 1,
    }
    receipt = {
        "status": "PASS", "build_status": "PASS",
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "actual_compiler_process_count": 28,
        "archive_sha256": RUST_ARCHIVE[1],
    }
    proof = {
        "schema": SCHEMA + "-authenticated-actual-rust-v12-source-build",
        "status": "PASS", "build_status": "PASS", "family": "rust",
        "label": "phase2-v12-rust-flag-original-p0",
        "historical_evidence_owner_count": 149,
        "historical_authenticated_reference_count": 154,
        "new_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count_after_publication": 151,
        "authenticated_reference_count_after_publication": 156,
        "actual_compiler_process_count": 28,
        "actual_unique_compiler_process_id_count": 28,
        "independent_phase_count": 2,
        "source_owner_count_per_phase": 9,
        "unchanged_source_owner_count_per_phase": 7,
        "corrected_public_overlay_apply_count": 2,
        "bridge_overlay_apply_count": 2,
        "corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "corrected_bridge_source_sha256": BRIDGE_DERIVED,
        "native_role_count": 2, "byte_identical_native_role_count": 2,
        "native_engine_bytes_changed": False, "reproducibility": "PASS",
        "external_dependency_count": 0, "external_regex_dependency_count": 0,
        "cross_family_engine_count": 0, "stdlib_regex_engine_count": 0,
        "prebuilt_artifact_count": 0, "original_source_targets_modified": False,
        "archive": archive, "receipt": receipt_owner,
        "publication_receipt": receipt,
        "candidate_correctness": "NOT MEASURED",
        "matching_test_status": "NOT MEASURED",
        "actual_candidate_workers": 0,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "candidate_qualified": False,
        "source_archive_uncompressed_sha256": RUST_EXPANDED[0],
        "source_archive_uncompressed_bytes_verified": RUST_EXPANDED[1],
        "candidate_matching_archive_opened_by_graph": False,
        "candidate_matching_archive_bytes_read_by_graph": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "baseline_passed": 31237, "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v30_repository_evidence_owner_count": 149,
        "preserved_v30_digest_addressed_history_path_count": 154,
        "new_rust_v12_source_build_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 151,
        "all_digest_addressed_history_path_count": 156,
        "rust_v3_original_campaign": campaign(1087, 7438),
        "c_v4_original_campaign": campaign(1230, 7325),
        "zig_v2_original_campaign": campaign(2172, 2847),
        "c_v10_repaired_original_campaign": {
            **campaign(1262, 7325), "suite_results": old_rows,
        },
        "rust_v12_corrected_flag_source_build": proof,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED", "hidden_cases_read": 0,
        "performance_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
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
        return ("PASS" if value == "FAIL" else "MEASURED"
                if value == "NOT MEASURED" else value + "-forged")
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
            raise GraphError("accepted forged V31 control: " + label)

        top = (
            "full_case_denominator", "suite_count", "baseline_passed",
            "frozen_independent_engine_family_count", "qualified_candidate_count",
            "preserved_v30_repository_evidence_owner_count",
            "preserved_v30_digest_addressed_history_path_count",
            "new_rust_v12_source_build_repository_evidence_owner_count",
            "all_actual_candidate_and_native_evidence_owner_count",
            "all_digest_addressed_history_path_count", "performance", "memory",
            "confidence_intervals", "hidden_cases_read", "performance_files_read",
            "clock_samples", "timing_trials_run",
            "final_comparison_planned_case_count", "final_comparison_cases_generated",
            "final_holdout_opened", "winner_selected",
        )
        for key in top:
            attack = copy.deepcopy(base)
            attack[key] = forged(attack[key])
            reject(attack, "top-level-" + key)
        for family in (
            "rust_v3_original_campaign", "c_v4_original_campaign",
            "zig_v2_original_campaign",
        ):
            for key in base[family]:
                attack = copy.deepcopy(base)
                attack[family][key] = forged(attack[family][key])
                reject(attack, family + "-" + key)
        for key in base["rust_v12_corrected_flag_source_build"]:
            attack = copy.deepcopy(base)
            attack["rust_v12_corrected_flag_source_build"][key] = forged(
                attack["rust_v12_corrected_flag_source_build"][key]
            )
            reject(attack, "actual-rust-source-build-" + key)
        for owner_name in ("archive", "receipt", "publication_receipt"):
            fixture = base["rust_v12_corrected_flag_source_build"][owner_name]
            for key in fixture:
                attack = copy.deepcopy(base)
                attack["rust_v12_corrected_flag_source_build"][owner_name][key] = forged(
                    fixture[key]
                )
                reject(attack, owner_name + "-" + key)
        collision = copy.deepcopy(base)
        collision["rust_v12_corrected_flag_source_build"]["receipt"]["device"] = RUST_ARCHIVE[3]
        collision["rust_v12_corrected_flag_source_build"]["receipt"]["inode"] = RUST_ARCHIVE[4]
        reject(collision, "aliased-build-archive-and-receipt")
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"31,237", b"151 / 156", b"1,087", b"7,438", b"1,230",
            b"7,325", b"2,172", b"2,847", b"28", b"0 matching workers",
            b"BUILT; NOT YET TESTED", b"NOT MEASURED", b"historical",
            b"does not claim", b"not been generated or opened",
        ):
            need(phrase.lower() in picture.lower(), "reject dishonest Rust build graph text")
        effects = (
            lambda: builtins.open("forbidden-v31"),
            lambda: os.open("forbidden-v31", os.O_RDONLY),
            lambda: os.stat("forbidden-v31-native"),
            lambda: subprocess.run(("forbidden-v31",)),
            lambda: importlib.import_module("candidates.rust_candidate"),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for action in effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("source-only V31 external effect was not physically blocked")
        need(wall.blocked == len(effects), "physically block all nine external-effect probes")
        need(rejected >= 90, "independently reject build, owner, history, and holdout forgery")
        return {
            "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
            "version": 31, "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "preserved_v30_repository_evidence_owner_count": 149,
            "preserved_v30_authenticated_reference_count": 154,
            "new_actual_rust_v12_source_build_evidence_owner_count": 2,
            "repository_evidence_owner_count": 151,
            "authenticated_digest_addressed_history_paths": 156,
            "qualified_candidate_count": 0,
            "rust_matching_status": "FAIL", "rust_semantic_mismatch_count": 1087,
            "rust_verified_passing_case_count": 7438,
            "c_matching_status": "FAIL", "c_semantic_mismatch_count": 1230,
            "c_verified_passing_case_count": 7325,
            "zig_matching_status": "FAIL", "zig_semantic_mismatch_count": 2172,
            "zig_verified_passing_case_count": 2847,
            "rust_v12_source_build_status": "PASS",
            "rust_v12_candidate_correctness": "NOT MEASURED",
            "rust_v12_candidate_worker_count": 0,
            "rust_v12_compiler_process_count": 28,
            "rust_v12_independent_phase_count": 2,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_candidate_imports": 0, "actual_native_activations": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "canonical_target_reads": 0, "canonical_target_stats": 0,
            "uncompressed_c_matching_archive_bytes_read": 0,
            "uncompressed_rust_matching_archive_bytes_read": 0,
            "uncompressed_zig_matching_archive_bytes_read": 0,
            "source_build_archive_bytes_read": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "workspace_mutations": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(path in allowed and type(raw) is bytes and 0 < len(raw) <= OWNER_LIMIT,
         "write only the three exclusively reserved generated V31 graph owners")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        view = memoryview(raw)
        while view:
            count = os.write(descriptor, view)
            need(type(count) is int and count > 0, "reject incomplete V31 publication")
            view = view[count:]
        os.fsync(descriptor)
        state = os.fstat(descriptor)
        need(
            state.st_size == len(raw) and state.st_uid == os.geteuid()
            and state.st_nlink == 1 and stat.S_IMODE(state.st_mode) == 0o600,
            "reject altered, linked, or unprivate generated V31 graph owner",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(observed == raw, "independently re-read exact generated V31 graph owner")


def result(
    source: str, archive: str, receipt: str,
    outputs: dict[str, bytes], written: bool, suffix: str,
) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 31, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_rust_v12_source_build_archive_sha256": archive,
        "actual_rust_v12_source_build_receipt_sha256": receipt,
        "suite_count": 13, "full_case_denominator": 31237,
        "private_waiver_count": 13, "qualified_candidate_count": 0,
        "preserved_v30_repository_evidence_owner_count": 149,
        "preserved_v30_authenticated_reference_count": 154,
        "new_actual_rust_v12_source_build_evidence_owner_count": 2,
        "repository_evidence_owner_count": 151,
        "authenticated_digest_addressed_history_paths": 156,
        "rust_matching_status": "FAIL", "rust_semantic_mismatch_count": 1087,
        "rust_verified_passing_case_count": 7438,
        "c_matching_status": "FAIL", "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_matching_status": "FAIL", "zig_semantic_mismatch_count": 2172,
        "zig_verified_passing_case_count": 2847,
        "actual_candidate_workers_per_tested_family": 13,
        "rust_v12_source_build_status": "PASS",
        "rust_v12_candidate_correctness": "NOT MEASURED",
        "rust_v12_matching_test_status": "NOT MEASURED",
        "rust_v12_candidate_worker_count": 0,
        "rust_v12_source_build_process_count": 28,
        "rust_v12_independent_phase_count": 2,
        "rust_v12_corrected_public_adapter_sha256": PUBLIC_DERIVED,
        "rust_v12_corrected_bridge_source_sha256": BRIDGE_DERIVED,
        "rust_v12_native_engine_bytes_changed": False,
        "outputs_written": written,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_native_activations": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "source_build_archive_uncompressed_bytes_verified": RUST_EXPANDED[1],
        "uncompressed_c_matching_archive_opened": False,
        "uncompressed_c_matching_archive_bytes_read": 0,
        "uncompressed_rust_matching_archive_opened": False,
        "uncompressed_rust_matching_archive_bytes_read": 0,
        "uncompressed_zig_matching_archive_opened": False,
        "uncompressed_zig_matching_archive_bytes_read": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    for name in (
        "--source-sha256", "--build-archive-sha256", "--build-receipt-sha256",
        "--inputs-sha256", "--summary-sha256", "--svg-sha256",
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
                "source-only controls never accept paths, real evidence, or rendering",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "actual V31 graph source")
        archive = checked(args.build_archive_sha256, "actual Rust V12 source-build archive")
        receipt = checked(args.build_receipt_sha256, "actual Rust V12 source-build receipt")
        _snapshot, pairs = build(source, archive, receipt)
        outputs = dict(pairs)
        if args.render:
            need(
                args.inputs_sha256 is None and args.summary_sha256 is None
                and args.svg_sha256 is None,
                "render only once with independently generated graph output digests",
            )
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, True, "-published")))
            return 0
        frozen = {
            OUTPUT + ".inputs.json": checked(args.inputs_sha256, "frozen V31 inputs"),
            OUTPUT + ".json": checked(args.summary_sha256, "frozen V31 summary"),
            OUTPUT + ".svg": checked(args.svg_sha256, "frozen V31 graph"),
        }
        for path, fingerprint in frozen.items():
            raw, _ = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(raw == outputs[path], "independently recreate the exact frozen V31 owner")
        sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, False, "-read-only-frozen-context")))
        return 0
    except (
        GraphError, OSError, ValueError, TypeError, EOFError, KeyError,
        AttributeError, struct.error, zlib.error,
    ) as error:
        sys.stderr.write("current V31 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
