#!/usr/bin/env python3
"""Show an independently rebuilt Zig engine without claiming untested matching."""

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
SELF = "tools/render_candidate_current_overview_v33.py"
OUTPUT = "docs/evidence/candidate-current-overview-v33"
SCHEMA = "rebar-candidate-current-overview-v33"
LIMIT = 8 * 1024 * 1024
SOURCE_REPORT_LIMIT = 2 * 1024 * 1024
V32 = {
    "source": (
        "tools/render_candidate_current_overview_v32.py",
        "998c8589cd1fb5a2d309603991e4b377c75cfb3dc85057ea597c6b08e9045df7",
        75889,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v32.inputs.json",
        "1739b0c1b785b93f9f47522a22bc844e9ce5c898bd6580ec01157ce7bdd9a82d",
        100773,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v32.json",
        "394ba794ce6bcad9d04da271d45f4465adcada8c4e00e3a75138ae9c257c71d2",
        362246,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v32.svg",
        "6366260bf300fab10893d9be20f1b5a2e181acb64db9776ee9e0fce3fcb699aa",
        13753,
    ),
}
ZIG_SOURCE = (
    "tools/reproduce_owned_zig_scanner_source_build_v12.py",
    "5192fa35dd0b13cb3bdddfc8f24c37d7e797d0b8463d000c4692c8131f33d1b6",
    124781,
)
ZIG_PROTOCOL = (
    "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V12.md",
    "f80743d8109402e5876792b6713237b1ab770e3286874dd5ae47fb56381131b1",
    6531,
)
ZIG_CONTRACT = (
    "oracle/phase2/zig-scanner-source-build-v12.json",
    "5abb6f60c7a9672e32d6f2980a109ccb15b7ef56e5cc3a81abda458109552c1a",
    23611,
)
ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2.json.gz",
    "3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d",
    48371,
    2064,
    524663,
)
RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2-publication-receipt.json",
    "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b",
    2029,
    2064,
    524664,
)
EXPANDED_SHA = "7a912e1221412e969e21400703bb95d15746a07b5776ee4530493cc3c8512b32"
EXPANDED_BYTES = 299800
CORRECTED_BRIDGE = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
PHASES = ("reference-a", "reference-b")
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version",
    "build_zig_engine", "build_zig_bridge",
    "engine_dynamic", "engine_symbols", "engine_sections", "engine_notes",
    "bridge_dynamic", "bridge_symbols", "bridge_sections", "bridge_notes",
)


class GraphError(Exception):
    """Reject a fabricated build, candidate result, owner, or measurement."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only bounded authenticated owner bytes")
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
        raise GraphError("reject noncanonical V33 evidence") from error


def checked(value: object, label: str) -> str:
    need(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "require an exact lowercase SHA-256 for " + label,
    )
    return value


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "require exact isolated stable CPython 3.14.6",
    )


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        result: dict[str, object] = {}
        for key, value in items:
            need(key not in result, "reject duplicate JSON keys in " + label)
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
        "reject an escaped or substituted first-party owner",
    )
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT, "bound authentic owner " + path)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    handle: int | None = None
    try:
        descriptors.append(os.open(str(ROOT), directory_flags))
        parts = Path(path).parts
        for part in parts[:-1]:
            descriptors.append(os.open(part, directory_flags, dir_fd=descriptors[-1]))
        handle = os.open(parts[-1], file_flags, dir_fd=descriptors[-1])
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid() and before.st_nlink == 1
            and before.st_size == size
            and (not private or stat.S_IMODE(before.st_mode) == 0o600)
            and (device is None or before.st_dev == device)
            and (inode is None or before.st_ino == inode),
            "reject a replaced, foreign, linked, or unprivate owner " + path,
        )
        remaining = size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            need(bool(piece), "reject incomplete exact owner " + path)
            pieces.append(piece)
            remaining -= len(piece)
        need(os.read(handle, 1) == b"", "reject trailing owner bytes " + path)
        raw = b"".join(pieces)
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_size, after.st_nlink)
            and digest(raw) == fingerprint,
            "reject an actual owner changed during authenticated reading " + path,
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
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT, "bound a frozen graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def load_v32() -> types.ModuleType:
    raw, _ = read_owner(*V32["source"])
    old = types.ModuleType("_rebar_exact_v32_for_actual_zig_v12_source_build_v33")
    old.__file__ = str(ROOT / V32["source"][0])
    old.__package__ = ""
    exec(compile(raw, old.__file__, "exec", dont_inherit=True), old.__dict__)
    need(
        old.SCHEMA == "rebar-candidate-current-overview-v32"
        and old.SELF == V32["source"][0],
        "load only the exact separately committed V32 matching overview",
    )
    return old


def authenticate_v32() -> tuple[dict, dict, dict[str, str]]:
    old = load_v32()
    previous, _, refs = old.authenticate_v31()
    rust, added = old.authenticate_rust_v4(
        old.ARCHIVE[1], old.RECEIPT[1], previous, refs,
    )
    need(
        len(refs) == 156 and len(added) == 2
        and not (set(refs) & set(added)),
        "reconstruct all genuine corrected Rust matching evidence before Zig evidence",
    )
    refs = {**refs, **added}
    need(len(refs) == 158, "retain all 158 independently authenticated V32 references")
    inputs_raw, _ = read_owner(*V32["inputs"], private=True)
    summary_raw, _ = read_owner(*V32["summary"], private=True)
    svg_raw, _ = read_owner(*V32["svg"], private=True)
    inputs = document(inputs_raw, "exact committed V32 graph inputs")
    summary = document(summary_raw, "exact committed V32 graph summary")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict, "preserve the exact V32 complete matching snapshot")
    old.validate(snapshot)
    need(
        summary.get("schema") == old.SCHEMA + "-summary"
        and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count") == 153
        and summary.get("authenticated_digest_addressed_history_paths") == 158
        and summary.get("suite_count") == 13
        and summary.get("full_case_denominator") == 31237
        and summary.get("private_waiver_count") == 13
        and summary.get("qualified_candidate_count") == 0
        and summary.get("actual_rust_v4_original_campaign") == rust
        and summary.get("rust_original_campaign_status") == "FAIL"
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
        and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
        and summary.get("c_original_campaign_status") == "FAIL"
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_status") == "FAIL"
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
        and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
        and summary.get("additional_signature_frozen_case_count") == 50
        and summary.get("additional_signature_reference_status") == "NOT RUN"
        and inputs.get("repository_evidence_owner_count") == 153
        and inputs.get("all_digest_addressed_history_path_count") == 158
        and svg_raw == old.make_svg(snapshot, V32["source"][1], V32["inputs"][1]),
        "independently reproduce all four V32 graph owners and actual matching outcomes",
    )
    return summary, inputs, refs


def inflate_zig_source_report(compressed: bytes) -> dict:
    need(
        type(compressed) is bytes and len(compressed) == ARCHIVE[2]
        and compressed[:3] == b"\x1f\x8b\x08"
        and struct.unpack("<I", compressed[4:8])[0] == 0
        and struct.unpack("<I", compressed[-4:])[0] == EXPANDED_BYTES
        and EXPANDED_BYTES < SOURCE_REPORT_LIMIT,
        "expand only the exact 299,800-byte Zig source-build report",
    )
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        raw = decoder.decompress(compressed, SOURCE_REPORT_LIMIT + 1)
    except zlib.error as error:
        raise GraphError("reject invalid bounded Zig source-build gzip") from error
    need(
        decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
        and len(raw) == EXPANDED_BYTES and digest(raw) == EXPANDED_SHA,
        "reject excess, concatenated, truncated, or replaced Zig build evidence",
    )
    return document(raw, "canonical complete actual Zig V12 source-build report")


def authenticate_zig_v12(
    archive_pin: str, receipt_pin: str, refs: dict[str, str],
) -> tuple[dict, dict[str, str]]:
    need(
        checked(archive_pin, "actual Zig V12 source-build archive") == ARCHIVE[1]
        and checked(receipt_pin, "actual Zig V12 source-build receipt") == RECEIPT[1],
        "caller-pin the exact two independently published Zig source-build owners",
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
        != (receipt_owner["device"], receipt_owner["inode"])
        and archive["path"] not in refs and receipt_owner["path"] not in refs,
        "count exactly two distinct new, owner-only actual Zig build records",
    )
    receipt = document(receipt_raw, "actual durable Zig V12 source-build receipt")
    publication = receipt.get("archive")
    need(
        type(publication) is dict
        and receipt.get("schema")
        == "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt"
        and receipt.get("version") == 12
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == "zig"
        and receipt.get("label") == "phase2-v12-zig-scanner-v2"
        and receipt.get("source_sha256") == ZIG_SOURCE[1]
        and receipt.get("protocol_sha256") == ZIG_PROTOCOL[1]
        and receipt.get("contract_sha256") == ZIG_CONTRACT[1]
        and publication.get("path") == archive["path"]
        and publication.get("sha256") == archive["sha256"]
        and publication.get("bytes") == archive["bytes"]
        and publication.get("device") == archive["device"]
        and publication.get("inode") == archive["inode"]
        and publication.get("mode") == "0600"
        and publication.get("uid") == archive["uid"]
        and publication.get("nlink") == 1
        and publication.get("exclusive_creation") is True
        and publication.get("file_fsync_completed") is True
        and publication.get("directory_fsync_completed") is True
        and publication.get("same_inode_readback_verified") is True,
        "bind the actual Zig build receipt to a distinct, durable, private archive",
    )
    need(
        receipt.get("actual_evidence_owner_count_before_publication") == 153
        and receipt.get("actual_authenticated_reference_count_before_publication") == 158
        and receipt.get("new_actual_evidence_owner_count") == 2
        and receipt.get("repository_evidence_owner_count_after_publication") == 155
        and receipt.get("authenticated_history_reference_count_after_publication") == 160
        and receipt.get("historical_v31_evidence_owner_count") == 151
        and receipt.get("historical_v31_authenticated_reference_count") == 156
        and receipt.get("expected_compiler_process_count_only_after_success") == 26
        and receipt.get("actual_compiler_process_count") == 26
        and receipt.get("actual_source_apply_count") == 2
        and receipt.get("corrected_bridge_sha256") == CORRECTED_BRIDGE
        and receipt.get("corrected_bridge_bytes") == 173026
        and receipt.get("v1_overlay_used") is False
        and receipt.get("uncompressed_sha256") == EXPANDED_SHA
        and receipt.get("uncompressed_bytes") == EXPANDED_BYTES
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
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "a genuine source build is not Zig matching, performance, or holdout evidence",
    )
    _, source = read_owner(*ZIG_SOURCE)
    _, protocol = read_owner(*ZIG_PROTOCOL)
    frozen_raw, contract_owner = read_owner(*ZIG_CONTRACT)
    frozen = document(frozen_raw, "exact independently frozen Zig V12 source contract")
    oracle = frozen.get("oracle")
    ownership = frozen.get("first_party_ownership")
    history = frozen.get("published_history")
    matching = frozen.get("preserved_matching_results")
    overlay = frozen.get("corrected_v2_overlay")
    policy = frozen.get("future_build_policy")
    need(
        frozen.get("schema")
        == "rebar-phase2-owned-zig-scanner-source-build-v12-source-freeze"
        and frozen.get("version") == 12
        and frozen.get("source") == {"path": ZIG_SOURCE[0], "sha256": ZIG_SOURCE[1]}
        and frozen.get("protocol")
        == {"path": ZIG_PROTOCOL[0], "sha256": ZIG_PROTOCOL[1]}
        and type(oracle) is dict and oracle.get("case_execution_count") == 31237
        and oracle.get("suite_count") == 13 and oracle.get("private_waiver_count") == 13
        and oracle.get("denominator_modified") is False
        and type(history) is dict
        and history.get("authoritative_evidence_owner_count") == 153
        and history.get("authenticated_reference_count") == 158,
        "bind the Zig source build to exact V32 evidence and the complete original oracle",
    )
    need(
        type(ownership) is dict
        and ownership.get("independent_engine_family_count") == 6
        and ownership.get("first_party_semantic_source_owner_count") == 25
        and ownership.get("zig_source_owner_count") == 3
        and ownership.get("external_regex_engine") == "FORBIDDEN"
        and ownership.get("cross_family_matching_engine") == "FORBIDDEN"
        and ownership.get("stdlib_regex_delegation") == "FORBIDDEN"
        and ownership.get("matching_fallback") == "FORBIDDEN"
        and type(ownership.get("zig_sources")) is list
        and len(ownership["zig_sources"]) == 3
        and type(matching) is dict
        and matching.get("rust_status") == "FAIL"
        and matching.get("rust_semantic_mismatch_count") == 1036
        and matching.get("rust_verified_passing_case_count") == 8965
        and matching.get("c_status") == "FAIL"
        and matching.get("c_semantic_mismatch_count") == 1230
        and matching.get("c_verified_passing_case_count") == 7325
        and matching.get("zig_status") == "FAIL"
        and matching.get("zig_semantic_mismatch_count") == 2172
        and matching.get("zig_verified_passing_case_count") == 2847
        and matching.get("qualified_candidate_count") == 0,
        "preserve actual Rust, C, and prior Zig matching without an external engine",
    )
    need(
        type(overlay) is dict
        and overlay.get("derived_bridge_sha256") == CORRECTED_BRIDGE
        and overlay.get("derived_bridge_bytes") == 173026
        and overlay.get("byte_identical_to_canonical_original") is True
        and overlay.get("phase_names") == list(PHASES)
        and overlay.get("v1_conditional_overlay_used") is False
        and type(policy) is dict
        and policy.get("phase_names") == list(PHASES)
        and policy.get("command_role_order") == list(PROCESS_ROLES)
        and policy.get("expected_phase_count_only_after_success") == 2
        and policy.get("expected_process_count_per_completed_phase") == 13
        and policy.get("expected_total_process_count_only_after_success") == 26
        and policy.get("offline") is True
        and policy.get("network") == "FORBIDDEN"
        and policy.get("cross_family_matching_dependency") == "FORBIDDEN"
        and policy.get("external_regex_engine") == "FORBIDDEN"
        and policy.get("fallback") == "FORBIDDEN",
        "authenticate two first-party, offline Zig source phases and the V2 bridge",
    )
    report = inflate_zig_source_report(compressed)
    phases = report.get("build_phases")
    processes = report.get("processes")
    reproduced = report.get("reproducibility")
    raw_elf = report.get("raw_elf_differences")
    need(
        report.get("schema") == "rebar-phase2-owned-zig-scanner-source-build-v12"
        and report.get("version") == 12
        and report.get("status") == "PASS"
        and report.get("family") == "zig"
        and report.get("label") == receipt["label"]
        and report.get("source_sha256") == ZIG_SOURCE[1]
        and report.get("protocol_sha256") == ZIG_PROTOCOL[1]
        and report.get("contract_sha256") == ZIG_CONTRACT[1]
        and report.get("frozen_case_execution_count") == 31237
        and report.get("suite_count") == 13
        and report.get("private_waiver_count") == 13
        and report.get("actual_evidence_owner_count_before_publication") == 153
        and report.get("actual_authenticated_reference_count_before_publication") == 158
        and report.get("historical_zig_semantic_mismatch_count") == 2172
        and report.get("historical_zig_verified_passing_case_count") == 2847
        and report.get("current_rust_semantic_mismatch_count") == 1036
        and report.get("current_rust_verified_passing_case_count") == 8965
        and report.get("historical_c_semantic_mismatch_count") == 1230
        and report.get("additive_frozen_case_count") == 50
        and report.get("additive_reference_status") == "NOT RUN"
        and report.get("expected_build_process_count_only_after_success") == 26
        and report.get("actual_build_process_count") == 26
        and report.get("actual_source_apply_count") == 2
        and report.get("corrected_bridge_sha256") == CORRECTED_BRIDGE
        and report.get("corrected_bridge_bytes") == 173026
        and report.get("v1_overlay_used") is False
        and type(processes) is list and len(processes) == 26
        and type(phases) is list and len(phases) == 2
        and [phase.get("name") for phase in phases] == list(PHASES)
        and type(reproduced) is dict and type(raw_elf) is dict,
        "authenticate the complete actually run two-phase Zig build, not only a receipt",
    )
    need(
        report.get("candidate_correctness") == "NOT MEASURED"
        and report.get("candidate_imports") == 0
        and report.get("candidate_processes_started") == 0
        and report.get("reference_processes_started") == 0
        and report.get("native_libraries_loaded") == 0
        and report.get("network_requests") == 0
        and report.get("hidden_cases_read") == 0
        and report.get("final_cases_read") == 0
        and report.get("benchmark_files_read") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("performance") == "NOT MEASURED"
        and report.get("memory") == "NOT MEASURED"
        and report.get("holdout") == "NOT OPENED"
        and report.get("winner_selected") is False,
        "never treat Zig source compilation as candidate execution or performance",
    )
    seen_pids: set[int] = set()
    for index, process in enumerate(processes):
        need(
            type(process) is dict
            and process.get("phase") == PHASES[index // len(PROCESS_ROLES)]
            and process.get("name") == PROCESS_ROLES[index % len(PROCESS_ROLES)]
            and type(process.get("pid")) is int and process["pid"] > 0
            and process["pid"] not in seen_pids
            and process.get("returncode") == 0
            and process.get("signal") is None,
            "require all 26 distinct, correctly ordered, successful compiler processes",
        )
        seen_pids.add(process["pid"])
    need(
        reproduced.get("status") == "PASS"
        and reproduced.get("independent_phase_count") == 2
        and reproduced.get("byte_identical_native_role_count") == 2
        and reproduced.get("compiler_process_count") == 26
        and reproduced.get("source_apply_count") == 2
        and type(reproduced.get("roles")) is dict
        and set(reproduced["roles"]) == {"engine", "bridge"}
        and raw_elf.get("independent_phase_count") == 2
        and raw_elf.get("native_role_count") == 2
        and raw_elf.get("all_native_artifacts_byte_identical") is True
        and raw_elf.get("additional_compiler_or_inspector_processes") == 0
        and raw_elf.get("comparison_completed_before_reproducibility_classification") is True,
        "verify genuine raw-ELF-first Zig reproducibility and no fabricated process roles",
    )
    source_owners = {
        owner["path"]: owner for owner in ownership["zig_sources"]
    }
    need(len(source_owners) == 3, "retain all three independent original Zig source owners")
    identities: set[tuple[int, int]] = set()
    for phase in phases:
        snapshots = phase.get("source_snapshots")
        native = phase.get("native_outputs")
        need(
            type(snapshots) is dict and set(snapshots) == set(source_owners)
            and type(native) is dict and set(native) == {"engine", "bridge"},
            "require all independent Zig source and native owners in both phases",
        )
        for path, original in source_owners.items():
            owner = snapshots[path]
            need(
                type(owner) is dict and owner.get("sha256") == original["sha256"]
                and owner.get("bytes") == original["bytes"]
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int
                and (owner["device"], owner["inode"]) not in identities,
                "reject missing, borrowed, or shared first-party Zig phase sources",
            )
            identities.add((owner["device"], owner["inode"]))
    roles: dict[str, dict] = {}
    for role, filename in (
        ("engine", "_zig_probe.so"),
        ("bridge", "_zig_bridge.cpython-314-x86_64-linux-gnu.so"),
    ):
        left = phases[0]["native_outputs"][role]
        right = phases[1]["native_outputs"][role]
        need(type(left) is dict and type(right) is dict,
             "require genuine independent Zig native role observations")
        one, two = left.get("owner"), right.get("owner")
        recorded = reproduced["roles"].get(role)
        need(
            type(one) is dict and type(two) is dict and type(recorded) is dict
            and one.get("sha256") == two.get("sha256") == recorded.get("sha256")
            and one.get("bytes") == two.get("bytes") == recorded.get("bytes")
            and (one.get("device"), one.get("inode"))
            != (two.get("device"), two.get("inode"))
            and recorded.get("phase_owner_count") == 2
            and recorded.get("byte_identical") is True
            and type(left.get("independence_audit")) is dict
            and left.get("independence_audit") == right.get("independence_audit"),
            "verify two distinct, byte-identical, independently audited Zig native outputs",
        )
        roles[role] = {
            "file_name": filename, "sha256": recorded["sha256"],
            "bytes": recorded["bytes"], "independent_phase_owner_count": 2,
            "phase_a_device": one["device"], "phase_a_inode": one["inode"],
            "phase_b_device": two["device"], "phase_b_inode": two["inode"],
            "byte_identical": True,
        }
    added = {archive["path"]: archive["sha256"], receipt_owner["path"]: receipt_owner["sha256"]}
    need(len(added) == 2 and not (set(added) & set(refs)),
         "count exactly two authentic and previously absent Zig build evidence owners")
    proof = {
        "schema": SCHEMA + "-authenticated-actual-zig-v12-source-build",
        "status": "PASS", "build_status": "PASS", "family": "zig",
        "label": receipt["label"], "source": source,
        "protocol": protocol, "contract": contract_owner,
        "archive": archive, "receipt": receipt_owner,
        "publication_receipt": receipt,
        "historical_evidence_owner_count": 153,
        "historical_authenticated_reference_count": 158,
        "new_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count_after_publication": 155,
        "authenticated_reference_count_after_publication": 160,
        "actual_compiler_process_count": 26,
        "actual_unique_compiler_process_id_count": len(seen_pids),
        "independent_phase_count": 2,
        "source_owner_count_per_phase": 3,
        "actual_source_apply_count": 2,
        "corrected_bridge_sha256": CORRECTED_BRIDGE,
        "corrected_bridge_bytes": 173026,
        "v1_overlay_used": False,
        "native_role_count": 2,
        "byte_identical_native_role_count": 2,
        "native_roles": roles,
        "reproducibility": "PASS",
        "first_party_zig_source_owner_count": 3,
        "external_regex_dependency_count": 0,
        "cross_family_engine_count": 0,
        "stdlib_regex_engine_count": 0,
        "network_requests": 0,
        "candidate_correctness": "NOT MEASURED",
        "matching_test_status": "NOT MEASURED",
        "actual_candidate_workers": 0,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "candidate_qualified": False,
        "source_archive_uncompressed_sha256": EXPANDED_SHA,
        "source_archive_uncompressed_bytes_verified": EXPANDED_BYTES,
        "candidate_matching_archive_opened_by_graph": False,
        "candidate_matching_archive_bytes_read_by_graph": 0,
        "hidden_cases_read": 0, "final_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
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
        and snapshot.get("preserved_v32_repository_evidence_owner_count") == 153
        and snapshot.get("preserved_v32_digest_addressed_history_path_count") == 158
        and snapshot.get("new_zig_v12_source_build_repository_evidence_owner_count") == 2
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 155
        and snapshot.get("all_digest_addressed_history_path_count") == 160,
        "derive exactly 153 + 2 owners and 158 + 2 digest-addressed references",
    )
    current_rust = snapshot.get("rust_v4_original_campaign")
    historical_rust = snapshot.get("rust_v3_original_campaign")
    need(
        type(current_rust) is dict and current_rust.get("status") == "FAIL"
        and current_rust.get("actual_candidate_workers") == 13
        and current_rust.get("completed_suite_count") == 13
        and current_rust.get("semantic_mismatch_count") == 1036
        and current_rust.get("verified_passing_case_count") == 8965
        and current_rust.get("infrastructure_failure_count") == 0
        and current_rust.get("candidate_qualified") is False
        and type(historical_rust) is dict
        and historical_rust.get("status") == "FAIL"
        and historical_rust.get("actual_candidate_workers") == 13
        and historical_rust.get("completed_suite_count") == 13
        and historical_rust.get("semantic_mismatch_count") == 1087
        and historical_rust.get("verified_passing_case_count") == 7438
        and historical_rust.get("infrastructure_failure_count") == 0
        and historical_rust.get("candidate_qualified") is False,
        "keep current corrected Rust 1,036 distinct from historical 1,087",
    )
    for name, mismatches, passes in (
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
    ):
        current = snapshot.get(name)
        need(
            type(current) is dict and current.get("status") == "FAIL"
            and current.get("actual_candidate_workers") == 13
            and current.get("completed_suite_count") == 13
            and current.get("semantic_mismatch_count") == mismatches
            and current.get("verified_passing_case_count") == passes
            and current.get("infrastructure_failure_count") == 0
            and current.get("candidate_qualified") is False,
            "preserve the actual completely tested matching result " + name,
        )
    old_c = snapshot.get("c_v10_repaired_original_campaign")
    need(
        type(old_c) is dict and old_c.get("status") == "FAIL"
        and old_c.get("semantic_mismatch_count") == 1262
        and old_c.get("verified_passing_case_count") == 7325
        and type(old_c.get("suite_results")) is list
        and len(old_c["suite_results"]) == 13,
        "preserve the 13 real older C suite rows without inventing new rows",
    )
    actual = snapshot.get("zig_v12_corrected_scanner_source_build")
    need(
        type(actual) is dict
        and actual.get("schema") == SCHEMA + "-authenticated-actual-zig-v12-source-build"
        and actual.get("status") == "PASS" and actual.get("build_status") == "PASS"
        and actual.get("family") == "zig"
        and actual.get("label") == "phase2-v12-zig-scanner-v2"
        and actual.get("historical_evidence_owner_count") == 153
        and actual.get("historical_authenticated_reference_count") == 158
        and actual.get("new_repository_evidence_owner_count") == 2
        and actual.get("repository_evidence_owner_count_after_publication") == 155
        and actual.get("authenticated_reference_count_after_publication") == 160
        and actual.get("actual_compiler_process_count") == 26
        and actual.get("actual_unique_compiler_process_id_count") == 26
        and actual.get("independent_phase_count") == 2
        and actual.get("source_owner_count_per_phase") == 3
        and actual.get("actual_source_apply_count") == 2
        and actual.get("corrected_bridge_sha256") == CORRECTED_BRIDGE
        and actual.get("corrected_bridge_bytes") == 173026
        and actual.get("v1_overlay_used") is False
        and actual.get("native_role_count") == 2
        and actual.get("byte_identical_native_role_count") == 2
        and actual.get("reproducibility") == "PASS"
        and actual.get("external_regex_dependency_count") == 0
        and actual.get("cross_family_engine_count") == 0
        and actual.get("stdlib_regex_engine_count") == 0
        and actual.get("network_requests") == 0,
        "verify only the actual corrected, independent, offline Zig source build",
    )
    archive, receipt = actual.get("archive"), actual.get("receipt")
    need(
        type(archive) is dict and archive.get("path") == ARCHIVE[0]
        and archive.get("sha256") == ARCHIVE[1]
        and archive.get("bytes") == ARCHIVE[2]
        and archive.get("device") == ARCHIVE[3]
        and archive.get("inode") == ARCHIVE[4]
        and archive.get("mode") == "0600" and archive.get("nlink") == 1
        and type(receipt) is dict and receipt.get("path") == RECEIPT[0]
        and receipt.get("sha256") == RECEIPT[1]
        and receipt.get("bytes") == RECEIPT[2]
        and receipt.get("device") == RECEIPT[3]
        and receipt.get("inode") == RECEIPT[4]
        and receipt.get("mode") == "0600" and receipt.get("nlink") == 1
        and (archive.get("device"), archive.get("inode"))
        != (receipt.get("device"), receipt.get("inode")),
        "require two genuinely distinct owner-only actual Zig source-build records",
    )
    publication = actual.get("publication_receipt")
    need(
        type(publication) is dict and publication.get("status") == "PASS"
        and publication.get("build_status") == "PASS"
        and publication.get("candidate_correctness") == "NOT MEASURED"
        and publication.get("actual_compiler_process_count") == 26
        and publication.get("candidate_processes_started") == 0
        and publication.get("candidate_imports") == 0,
        "a Zig build receipt can never establish matching compatibility",
    )
    need(
        actual.get("candidate_correctness") == "NOT MEASURED"
        and actual.get("matching_test_status") == "NOT MEASURED"
        and actual.get("actual_candidate_workers") == 0
        and actual.get("candidate_processes_started") == 0
        and actual.get("candidate_imports") == 0
        and actual.get("native_libraries_loaded") == 0
        and actual.get("candidate_qualified") is False
        and actual.get("source_archive_uncompressed_sha256") == EXPANDED_SHA
        and actual.get("source_archive_uncompressed_bytes_verified") == EXPANDED_BYTES
        and actual.get("candidate_matching_archive_opened_by_graph") is False
        and actual.get("candidate_matching_archive_bytes_read_by_graph") == 0
        and actual.get("hidden_cases_read") == 0
        and actual.get("final_cases_read") == 0
        and actual.get("clock_samples") == 0
        and actual.get("timing_trials_run") == 0
        and actual.get("performance") == "NOT MEASURED"
        and actual.get("memory") == "NOT MEASURED"
        and actual.get("holdout") == "NOT OPENED"
        and actual.get("winner_selected") is False,
        "report zero actual new Zig candidate workers and no invented speed or matching",
    )
    need(
        snapshot.get("additional_signature_frozen_case_count") == 50
        and snapshot.get("additional_signature_reference_status") == "NOT RUN"
        and snapshot.get("additional_signature_reference_cases_executed") == 0
        and snapshot.get("performance") == "NOT MEASURED"
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
        "leave all 50 future signature cases, speed, and final holdout genuinely unrun",
    )


def xml(value: object) -> str:
    return (
        str(value).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
    )


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "actual V33 renderer")
    checked(inputs, "actual V33 graph inputs")
    rows = (
        ("Python re — reference", "PASSED", "All 31,237 original Python reference checks pass.", "pass"),
        ("Rust — corrected and actually tested", "NOT COMPATIBLE", "13 matching workers; 1,036 differences; 8,965 verified passes.", "fail"),
        ("C — actually tested current version", "NOT COMPATIBLE", "13 matching workers; 1,230 differences; 7,325 verified passes.", "fail"),
        ("Zig — last actually tested version", "NOT COMPATIBLE", "13 matching workers; 2,172 differences; 2,847 verified passes.", "fail"),
        ("Zig — newly corrected, independently built twice", "BUILT; MATCHING NOT TESTED", "Two private source phases; 26 observed build processes; 0 new matching workers.", "pending"),
        ("Rust — previously tested historical version", "NOT COMPATIBLE", "Historical only: 1,087 differences and 7,438 verified passes.", "fail"),
        ("Additional Python signature checks", "REFERENCE NOT RUN", "50 frozen future checks; 0 reference executions; not added to the original denominator.", "pending"),
        ("Speed, memory, and final comparison", "NOT MEASURED", "No fully compatible replacement, speed comparison, confidence interval, or winner.", "pending"),
        ("Final hidden holdout", "NOT OPENED", "All 4,194,304 planned final comparison cases remain ungenerated and sealed.", "pending"),
    )
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1810" viewBox="0 0 1440 1810" role="img" aria-labelledby="v33-title v33-description">',
        '<title id="v33-title">Building a faster Python re: corrected Zig builds successfully, but matching has not been tested</title>',
        '<desc id="v33-description">The corrected first-party Zig engine and bridge were built in two independent private phases and 26 successful observed compiler and inspection processes. The corrected Zig candidate has run zero matching workers; compatibility has not been tested. The last fully tested Zig version had 2,172 differences and 2,847 verified passes. The current Rust and C matching results have 1,036 and 1,230 differences. All 31,237 original Python reference checks pass. Exactly 155 evidence owners and 160 history references are authenticated. Fifty additional signature checks have not run. Speed, memory, and confidence are not measured, and the 4,194,304-case holdout remains unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.title{font-size:26px;font-weight:760;fill:#16324f}.heading{font-size:20px;font-weight:740;fill:#16324f}.body{font-size:14px;fill:#42556c}.name{font-size:15px;font-weight:720;fill:#16324f}.pass{font-size:13px;font-weight:750;fill:#00794c}.fail{font-size:13px;font-weight:740;fill:#a15e00}.pending{font-size:13px;font-weight:740;fill:#53667b}.big{font-size:20px;font-weight:760;fill:#16324f}.small{font-size:12px;fill:#42556c}.foot{font-size:10px;fill:#53667b}</style>',
        '<rect width="1440" height="1810" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="54" class="title">Can we build a faster replacement for Python re?</text>',
        '<text x="46" y="81" class="body">New Zig: built twice from our own source; full compatibility test not yet run. Speed is NOT MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original Python checks"),
        ("0", "compatible replacements"),
        ("1,036", "tested Rust differences"),
        ("1,230", "tested C differences"),
        ("2,172", "last tested Zig differences"),
        ("26", "new Zig build processes"),
        ("155 / 160", "evidence / references"),
    )
    for index, (number, label) in enumerate(cards):
        x = 44 + index * 195
        lines.extend((
            f'<rect x="{x}" y="98" width="184" height="82" rx="11" fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{x + 10}" y="132" class="big">{xml(number)}</text>',
            f'<text x="{x + 10}" y="158" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="197" width="1352" height="630" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="232" class="heading">1. Which versions actually match Python?</text>',
        '<text x="65" y="257" class="body">A passing source build never means that the new Zig candidate passed or even started a compatibility test.</text>',
    ))
    for index, (name, status, detail, kind) in enumerate(rows):
        y = 273 + index * 55
        lines.extend((
            f'<rect x="63" y="{y}" width="1314" height="49" rx="8" fill="#f8fafd" stroke="#e5ecf2"/>',
            f'<text x="79" y="{y + 19}" class="name">{xml(name)}</text>',
            f'<text x="1358" y="{y + 19}" class="{kind}" text-anchor="end">{xml(status)}</text>',
            f'<text x="80" y="{y + 38}" class="small">{xml(detail)}</text>',
        ))
    lines.append('<text x="65" y="799" class="body">The corrected Zig build has no matching result; the 2,172 differences belong only to the earlier actually tested version.</text>')
    lines.extend((
        '<rect x="44" y="845" width="1352" height="408" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="881" class="heading">2. What did the previously recorded C test show?</text>',
        '<text x="65" y="905" class="body">These 13 recorded groups belong only to the historical C run with 1,262 differences.</text>',
        '<text x="80" y="929" class="small">HISTORICAL ORIGINAL PYTHON TEST GROUP</text>',
        '<text x="1040" y="929" class="small" text-anchor="end">CHECKS</text>',
        '<text x="1355" y="929" class="small" text-anchor="end">HISTORICAL C RESULT ONLY</text>',
    ))
    for index, row in enumerate(snapshot["c_v10_repaired_original_campaign"]["suite_results"]):
        need(type(row) is dict, "retain each genuine historical C result")
        count, mismatches = row.get("case_execution_denominator"), row.get("mismatch_count")
        label = row.get("display_name", row.get("suite"))
        need(
            type(label) is str and bool(label)
            and type(count) is int and count >= 0
            and type(mismatches) is int and mismatches >= 0,
            "reject invented historical test-group counts",
        )
        y = 937 + index * 22
        colour = "#f8fafd" if index % 2 == 0 else "#ffffff"
        outcome = "PASSED" if mismatches == 0 else f"{mismatches:,} DIFFERENCES"
        kind = "pass" if mismatches == 0 else "fail"
        lines.extend((
            f'<rect x="64" y="{y}" width="1312" height="21" rx="4" fill="{colour}"/>',
            f'<text x="80" y="{y + 15}" class="small">{xml(label)}</text>',
            f'<text x="1040" y="{y + 15}" class="small" text-anchor="end">{count:,}</text>',
            f'<text x="1355" y="{y + 15}" class="{kind}" text-anchor="end">{xml(outcome)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1270" width="1352" height="400" rx="15" fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1306" class="heading">3. What did the new Zig build actually prove?</text>',
    ))
    notes = (
        "Two separately owned source phases each built both first-party Zig native roles.",
        "All 26 recorded offline compiler and inspection processes succeeded.",
        "The engine and bridge were byte-identical across independently owned phase outputs.",
        "The corrected Zig candidate ran 0 matching workers: compatibility remains NOT MEASURED.",
        "The last actually tested Zig still has 2,172 differences and 2,847 verified passes.",
        "Current actually tested Rust and C still have 1,036 and 1,230 differences.",
        "153 previous evidence owners + one actual Zig build archive + one receipt = 155; 160 references.",
        "All large Rust, C, and Zig matching-failure archives stay compressed.",
        "The 50 separately frozen signature checks have not run against the Python reference.",
        "Speed, memory, confidence intervals, and undefined behavior remain NOT MEASURED.",
        "The 4,194,304-case final holdout is sealed; no replacement or winner is qualified.",
    )
    for index, note in enumerate(notes):
        lines.append(f'<text x="66" y="{1338 + index * 26}" class="body">{xml(note)}</text>')
    lines.extend((
        f'<text x="47" y="1720" class="foot">Inputs SHA-256: {xml(inputs)}</text>',
        f'<text x="47" y="1740" class="foot">Renderer SHA-256: {xml(source)}</text>',
        f'<text x="47" y="1760" class="foot">Actual Zig source-build archive: {xml(ARCHIVE[1])}</text>',
        f'<text x="47" y="1780" class="foot">Actual distinct Zig source-build receipt: {xml(RECEIPT[1])}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(source_pin: str, archive_pin: str, receipt_pin: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_pin = checked(source_pin, "actual V33 renderer")
    own, _ = read_owner(SELF, source_pin, os.path.getsize(ROOT / SELF))
    previous, previous_inputs, refs = authenticate_v32()
    proof, added = authenticate_zig_v12(archive_pin, receipt_pin, refs)
    need(len(refs) == 158 and len(added) == 2 and not (set(refs) & set(added)),
         "authenticate new Zig evidence only after every historical reference")
    all_refs = {**refs, **added}
    count = previous["repository_evidence_owner_count"] + len(added)
    need(count == 155 and len(all_refs) == 160,
         "derive exactly 155 actual evidence owners and 160 references")
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update({
        "preserved_v32_repository_evidence_owner_count": 153,
        "preserved_v32_digest_addressed_history_path_count": 158,
        "new_zig_v12_source_build_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": len(all_refs),
        "zig_v12_corrected_scanner_source_build": copy.deepcopy(proof),
        "zig_v12_source_build_status": "PASS",
        "zig_v12_source_build_candidate_correctness": "NOT MEASURED",
        "zig_v12_source_build_matching_test_status": "NOT MEASURED",
        "zig_v12_source_build_candidate_worker_count": 0,
        "zig_v12_source_build_process_count": 26,
        "zig_v12_source_build_phase_count": 2,
        "zig_v12_source_build_apply_count": 2,
        "zig_v12_source_build_candidate_qualified": False,
    })
    validate(snapshot)
    prior = {name: pin(*owner) for name, owner in V32.items()}
    manifest = copy.deepcopy(previous_inputs)
    manifest.update({
        "schema": SCHEMA + "-inputs", "version": 33, "python": "3.14.6",
        "renderer": pin(SELF, source_pin, len(own)), "previous_overview": prior,
        "actual_zig_v12_corrected_source_build": copy.deepcopy(proof),
        "current_complete_rust_campaign": copy.deepcopy(snapshot["rust_v4_original_campaign"]),
        "historical_complete_rust_v3_campaign": copy.deepcopy(snapshot["rust_v3_original_campaign"]),
        "current_complete_c_campaign": copy.deepcopy(snapshot["c_v4_original_campaign"]),
        "actual_complete_zig_campaign": copy.deepcopy(snapshot["zig_v2_original_campaign"]),
        "preserved_v32_repository_evidence_owner_count": 153,
        "preserved_v32_digest_addressed_history_path_count": 158,
        "new_zig_v12_source_build_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": len(all_refs),
        "candidate_qualified_count": 0,
        "zig_v12_source_build_status": "PASS",
        "zig_v12_source_build_matching_test_status": "NOT MEASURED",
        "zig_v12_source_build_candidate_workers": 0,
        "zig_v12_source_build_process_count": 26,
        "zig_v12_source_build_independent_phase_count": 2,
        "zig_v12_source_build_apply_count": 2,
        "zig_v12_source_build_candidate_qualified": False,
        "zig_v12_source_build_external_regex_dependency_count": 0,
        "zig_v12_source_build_cross_family_engine_count": 0,
        "source_build_archive_uncompressed_bytes_verified": EXPANDED_BYTES,
    })
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source_pin, digest(manifest_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") == "zig":
            family.update({
                "v12_corrected_source_build": copy.deepcopy(proof),
                "v12_source_build_status": "PASS",
                "v12_matching_test_status": "NOT MEASURED",
                "v12_candidate_worker_count": 0,
                "v12_candidate_qualified": False,
                "qualified": False,
            })
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 33,
        "status": "PASS", "python": "3.14.6",
        "source": pin(SELF, source_pin, len(own)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw), len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(image), len(image)),
        "previous_overview": prior, "snapshot": snapshot, "families": families,
        "preserved_v32_repository_evidence_owner_count": 153,
        "preserved_v32_authenticated_reference_path_count": 158,
        "new_zig_v12_source_build_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "authenticated_digest_addressed_history_paths": len(all_refs),
        "qualified_candidate_count": 0,
        "actual_zig_v12_corrected_source_build": copy.deepcopy(proof),
        "zig_v12_source_build_status": "PASS",
        "zig_v12_source_build_candidate_correctness": "NOT MEASURED",
        "zig_v12_source_build_matching_test_status": "NOT MEASURED",
        "zig_v12_source_build_candidate_worker_count": 0,
        "zig_v12_source_build_process_count": 26,
        "zig_v12_source_build_unique_process_count": 26,
        "zig_v12_source_build_phase_count": 2,
        "zig_v12_source_build_source_apply_count": 2,
        "zig_v12_source_build_candidate_qualified": False,
        "zig_v12_source_build_external_regex_dependency_count": 0,
        "zig_v12_source_build_cross_family_engine_count": 0,
        "zig_v12_source_build_stdlib_regex_engine_count": 0,
        "zig_v12_source_build_network_requests": 0,
        "zig_v12_source_build_candidate_imports": 0,
        "zig_v12_source_build_candidate_processes_started": 0,
        "zig_v12_source_build_native_libraries_loaded": 0,
        "source_build_archive_uncompressed_bytes_verified": EXPANDED_BYTES,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0, "actual_native_activations": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", image),
    )


class Wall:
    """Physically prevent actual effects inside source-only hostile tests."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def __enter__(self) -> Wall:
        def forbid(name: str):
            def blocked(*_args: object, **_kwargs: object) -> object:
                self.blocked += 1
                raise GraphError("V33 source-only effect blocked: " + name)
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

    def __exit__(self, *_errors: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic() -> dict:
    campaign = lambda mismatches, passes: {
        "status": "FAIL", "actual_candidate_workers": 13,
        "completed_suite_count": 13, "semantic_mismatch_count": mismatches,
        "verified_passing_case_count": passes,
        "infrastructure_failure_count": 0, "candidate_qualified": False,
    }
    archive = {
        "path": ARCHIVE[0], "sha256": ARCHIVE[1], "bytes": ARCHIVE[2],
        "device": ARCHIVE[3], "inode": ARCHIVE[4], "mode": "0600", "nlink": 1,
    }
    receipt_owner = {
        "path": RECEIPT[0], "sha256": RECEIPT[1], "bytes": RECEIPT[2],
        "device": RECEIPT[3], "inode": RECEIPT[4], "mode": "0600", "nlink": 1,
    }
    publication = {
        "status": "PASS", "build_status": "PASS",
        "candidate_correctness": "NOT MEASURED",
        "actual_compiler_process_count": 26,
        "candidate_processes_started": 0, "candidate_imports": 0,
    }
    proof = {
        "schema": SCHEMA + "-authenticated-actual-zig-v12-source-build",
        "status": "PASS", "build_status": "PASS", "family": "zig",
        "label": "phase2-v12-zig-scanner-v2",
        "historical_evidence_owner_count": 153,
        "historical_authenticated_reference_count": 158,
        "new_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count_after_publication": 155,
        "authenticated_reference_count_after_publication": 160,
        "actual_compiler_process_count": 26,
        "actual_unique_compiler_process_id_count": 26,
        "independent_phase_count": 2, "source_owner_count_per_phase": 3,
        "actual_source_apply_count": 2,
        "corrected_bridge_sha256": CORRECTED_BRIDGE,
        "corrected_bridge_bytes": 173026, "v1_overlay_used": False,
        "native_role_count": 2, "byte_identical_native_role_count": 2,
        "reproducibility": "PASS", "external_regex_dependency_count": 0,
        "cross_family_engine_count": 0, "stdlib_regex_engine_count": 0,
        "network_requests": 0, "archive": archive, "receipt": receipt_owner,
        "publication_receipt": publication,
        "candidate_correctness": "NOT MEASURED",
        "matching_test_status": "NOT MEASURED",
        "actual_candidate_workers": 0, "candidate_processes_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "candidate_qualified": False,
        "source_archive_uncompressed_sha256": EXPANDED_SHA,
        "source_archive_uncompressed_bytes_verified": EXPANDED_BYTES,
        "candidate_matching_archive_opened_by_graph": False,
        "candidate_matching_archive_bytes_read_by_graph": 0,
        "hidden_cases_read": 0, "final_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    rows = [
        {"suite": f"historical-{i}",
         "display_name": f"Historical Python test group {i + 1}",
         "case_execution_denominator": 2000,
         "mismatch_count": 1262 if i == 0 else 0}
        for i in range(13)
    ]
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "baseline_passed": 31237, "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v32_repository_evidence_owner_count": 153,
        "preserved_v32_digest_addressed_history_path_count": 158,
        "new_zig_v12_source_build_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 155,
        "all_digest_addressed_history_path_count": 160,
        "rust_v4_original_campaign": campaign(1036, 8965),
        "rust_v3_original_campaign": campaign(1087, 7438),
        "c_v4_original_campaign": campaign(1230, 7325),
        "zig_v2_original_campaign": campaign(2172, 2847),
        "c_v10_repaired_original_campaign": {
            **campaign(1262, 7325), "suite_results": rows,
        },
        "zig_v12_corrected_scanner_source_build": proof,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
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
        return "PASS" if value == "FAIL" else (
            "MEASURED" if value in ("NOT RUN", "NOT MEASURED") else value + "-forged"
        )
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
            raise GraphError("accepted hostile synthetic V33 evidence: " + label)

        top = (
            "full_case_denominator", "suite_count", "baseline_passed",
            "frozen_independent_engine_family_count", "qualified_candidate_count",
            "preserved_v32_repository_evidence_owner_count",
            "preserved_v32_digest_addressed_history_path_count",
            "new_zig_v12_source_build_repository_evidence_owner_count",
            "all_actual_candidate_and_native_evidence_owner_count",
            "all_digest_addressed_history_path_count",
            "additional_signature_frozen_case_count",
            "additional_signature_reference_status",
            "additional_signature_reference_cases_executed",
            "performance", "memory", "confidence_intervals",
            "hidden_cases_read", "performance_files_read",
            "clock_samples", "timing_trials_run",
            "final_comparison_planned_case_count",
            "final_comparison_cases_generated", "final_holdout_opened",
            "winner_selected",
        )
        for name in top:
            attack = copy.deepcopy(base)
            attack[name] = forged(attack[name])
            reject(attack, "top-" + name)
        for name in (
            "rust_v4_original_campaign", "rust_v3_original_campaign",
            "c_v4_original_campaign", "zig_v2_original_campaign",
        ):
            for key, value in base[name].items():
                attack = copy.deepcopy(base)
                attack[name][key] = forged(value)
                reject(attack, name + "-" + key)
        proof = base["zig_v12_corrected_scanner_source_build"]
        for key, value in proof.items():
            attack = copy.deepcopy(base)
            attack["zig_v12_corrected_scanner_source_build"][key] = forged(value)
            reject(attack, "actual-zig-build-" + key)
        for name in ("archive", "receipt", "publication_receipt"):
            for key, value in proof[name].items():
                attack = copy.deepcopy(base)
                attack["zig_v12_corrected_scanner_source_build"][name][key] = forged(value)
                reject(attack, name + "-" + key)
        collision = copy.deepcopy(base)
        collision["zig_v12_corrected_scanner_source_build"]["receipt"]["device"] = ARCHIVE[3]
        collision["zig_v12_corrected_scanner_source_build"]["receipt"]["inode"] = ARCHIVE[4]
        reject(collision, "archive-receipt-inode-collision")
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"31,237", b"155 / 160", b"1,036", b"8,965", b"1,230",
            b"7,325", b"2,172", b"2,847", b"26", b"0 new matching workers",
            b"BUILT; MATCHING NOT TESTED", b"REFERENCE NOT RUN",
            b"NOT MEASURED", b"4,194,304", b"last actually tested",
            b"stay compressed",
        ):
            need(phrase.lower() in picture.lower(), "reject a dishonest build-only Zig graph")
        effects = (
            lambda: builtins.open("forbidden-v33"),
            lambda: os.open("forbidden-v33", os.O_RDONLY),
            lambda: os.stat("forbidden-v33-native"),
            lambda: subprocess.run(("forbidden-v33",)),
            lambda: importlib.import_module("candidates.zig_candidate"),
            lambda: socket.socket(), lambda: tempfile.mkdtemp(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for action in effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("V33 source-only self-test leaked an external effect")
        need(wall.blocked == len(effects), "block all nine actual source-only effects")
        need(rejected >= 110, "exercise all owner, process, matching, holdout and build forgeries")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 33, "status": "PASS", "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "suite_count": 13, "full_case_denominator": 31237,
            "private_waiver_count": 13, "qualified_candidate_count": 0,
            "preserved_v32_repository_evidence_owner_count": 153,
            "preserved_v32_authenticated_reference_count": 158,
            "new_zig_v12_source_build_evidence_owner_count": 2,
            "repository_evidence_owner_count": 155,
            "authenticated_digest_addressed_history_paths": 160,
            "rust_candidate_status": "FAIL",
            "rust_semantic_mismatch_count": 1036,
            "rust_verified_passing_case_count": 8965,
            "c_candidate_status": "FAIL", "c_semantic_mismatch_count": 1230,
            "c_verified_passing_case_count": 7325,
            "last_tested_zig_candidate_status": "FAIL",
            "last_tested_zig_semantic_mismatch_count": 2172,
            "last_tested_zig_verified_passing_case_count": 2847,
            "corrected_zig_build_status": "PASS",
            "corrected_zig_matching_test_status": "NOT MEASURED",
            "corrected_zig_candidate_worker_count": 0,
            "actual_zig_compiler_process_count": 26,
            "actual_zig_independent_phase_count": 2,
            "actual_zig_source_apply_count": 2,
            "additional_signature_frozen_case_count": 50,
            "additional_signature_reference_status": "NOT RUN",
            "additional_signature_reference_cases_executed": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_candidate_imports": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_activations": 0,
            "canonical_target_reads": 0, "canonical_target_stats": 0,
            "uncompressed_c_matching_archive_bytes_read": 0,
            "uncompressed_rust_matching_archive_bytes_read": 0,
            "uncompressed_zig_matching_archive_bytes_read": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "workspace_mutations": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(path in allowed and type(raw) is bytes and 0 < len(raw) <= LIMIT,
         "write only the three exclusively reserved generated V33 graph owners")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(handle, remaining)
            need(type(written) is int and written > 0, "reject incomplete exclusive V33 output")
            remaining = remaining[written:]
        os.fsync(handle)
        observed = os.fstat(handle)
        need(
            observed.st_uid == os.geteuid() and observed.st_nlink == 1
            and observed.st_size == len(raw)
            and stat.S_IMODE(observed.st_mode) == 0o600,
            "reject a non-private, altered, or linked generated V33 owner",
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
    actual, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(actual == raw, "re-read and prove the exact durably published V33 graph owner")


def result(
    source: str, archive: str, receipt: str,
    outputs: dict[str, bytes], written: bool, suffix: str,
) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 33, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_zig_v12_source_build_archive_sha256": archive,
        "actual_zig_v12_source_build_receipt_sha256": receipt,
        "suite_count": 13, "full_case_denominator": 31237,
        "private_waiver_count": 13, "qualified_candidate_count": 0,
        "preserved_v32_repository_evidence_owner_count": 153,
        "preserved_v32_authenticated_reference_count": 158,
        "new_actual_zig_v12_source_build_evidence_owner_count": 2,
        "repository_evidence_owner_count": 155,
        "authenticated_digest_addressed_history_paths": 160,
        "rust_matching_status": "FAIL", "rust_semantic_mismatch_count": 1036,
        "rust_verified_passing_case_count": 8965,
        "c_matching_status": "FAIL", "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "last_tested_zig_matching_status": "FAIL",
        "last_tested_zig_semantic_mismatch_count": 2172,
        "last_tested_zig_verified_passing_case_count": 2847,
        "zig_v12_source_build_status": "PASS",
        "zig_v12_candidate_correctness": "NOT MEASURED",
        "zig_v12_matching_test_status": "NOT MEASURED",
        "zig_v12_candidate_worker_count": 0,
        "zig_v12_source_build_process_count": 26,
        "zig_v12_independent_phase_count": 2,
        "zig_v12_source_apply_count": 2,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "outputs_written": written,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "source_build_archive_uncompressed_bytes_verified": EXPANDED_BYTES,
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
                "source-only self-tests never accept real archive paths or output writes",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "actual V33 renderer")
        archive = checked(args.build_archive_sha256, "actual Zig source-build archive")
        receipt = checked(args.build_receipt_sha256, "actual Zig source-build receipt")
        _snapshot, pairs = build(source, archive, receipt)
        outputs = dict(pairs)
        if args.render:
            need(
                args.inputs_sha256 is None and args.summary_sha256 is None
                and args.svg_sha256 is None,
                "render only the exactly reproduced V33 graph outputs once",
            )
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, True, "-published")))
            return 0
        frozen = {
            OUTPUT + ".inputs.json": checked(args.inputs_sha256, "frozen V33 inputs"),
            OUTPUT + ".json": checked(args.summary_sha256, "frozen V33 summary"),
            OUTPUT + ".svg": checked(args.svg_sha256, "frozen V33 graph"),
        }
        for path, fingerprint in frozen.items():
            raw, _ = read_owner(path, fingerprint, len(outputs[path]), private=True)
            need(raw == outputs[path], "independently reproduce the exact authentic V33 graph")
        sys.stdout.buffer.write(canonical(result(source, archive, receipt, outputs, False, "-read-only-frozen-context")))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError, KeyError,
            AttributeError, struct.error, zlib.error) as error:
        sys.stderr.write("current V33 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
