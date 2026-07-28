#!/usr/bin/env python3
"""Freeze and, only when separately authorized, build the corrected owned Rust."""

from __future__ import annotations

import argparse
import builtins
import contextlib
import copy
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import io
import json
import os
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-rust-flag-source-build-v12"
VERSION = 12
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_flag_source_build_v12.py"
PROTOCOL_PATH = "oracle/phase2/RUST-FLAG-SOURCE-BUILD-V12.md"
CONTRACT_PATH = "oracle/phase2/rust-flag-source-build-v12.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_TOOLCHAIN_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
PHASES = ("reference-a", "reference-b")
SUITE_COUNT = 13
CASE_COUNT = 31237
PRIVATE_WAIVERS = 13
CURRENT_EVIDENCE_OWNERS = 149
CURRENT_HISTORY_REFERENCES = 154
BRIDGE_PATH = "candidates/rust/py_bridge.c"
BRIDGE_DERIVED_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
BRIDGE_DERIVED_BYTES = 176118
PUBLIC_PATH = "candidates/rust_candidate.py"
PUBLIC_DERIVED_SHA256 = "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
PUBLIC_DERIVED_BYTES = 31464
HISTORICAL_PUBLIC_DERIVED_SHA256 = "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
ENGINE_NAME = "_rust_engine.so"
BRIDGE_NAME = "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True, slots=True)
class ToolOwner:
    path: str
    sha256: str
    size: int
    device: int
    inode: int
    mode: int
    uid: int
    nlink: int = 1


GOAL = Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
RUST_OWNERS = (
    Owner("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    Owner("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    Owner(BRIDGE_PATH, "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
    Owner("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    Owner("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    Owner("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    Owner("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    Owner("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    Owner(PUBLIC_PATH, "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
)
BRIDGE_REPAIR = (
    Owner("tools/apply_owned_rust_source_repair_v1.py", "1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851", 59388),
    Owner("oracle/phase2/RUST-SOURCE-REPAIR-V1.md", "df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b", 5496),
    Owner("oracle/phase2/rust-source-repair-v1.json", "1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b", 8306),
)
PUBLIC_REPAIR_V2 = (
    Owner("tools/apply_owned_rust_public_contract_source_repair_v2.py", "d0f90145195e9978482a7797956ef916adb1d0612118c2fc6343c4f38b823fa8", 74140),
    Owner("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V2.md", "3f469ca7298b08cc1d50d18aff5029ae17a3f4f318c4fc7a2d8f8f45cc16e239", 5505),
    Owner("oracle/phase2/rust-public-contract-source-repair-v2.json", "b87c876e16041b0e08619aec0a86a069598b54478a1fa55cc9baa220c2c1f53b", 13826),
)
PREVIOUS_BUILD_V11 = (
    Owner("tools/reproduce_owned_native_source_build_v11.py", "3fb0ca1b6914617eb8a6f491072fcb40b15a364afacbaec2d4caac1e9b6f5d10", 80171),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V11.md", "bd6bce6b14bebe55691900e4a48bb8acf89197660e1d5ebd4c8c38e979c05fe6", 3868),
    Owner("oracle/phase2/native-source-build-v11.json", "7b1f8941444e942a85eb9f9df9dc23244112763ca92381fe22f76fd87c95a87a", 7676),
)
PREVIOUS_BUILD_ARCHIVE = Owner("oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz", "282927f91fd885701dff6c431474f586afbc09460c6a20417ffa20be5a2e891c", 107639)
PREVIOUS_BUILD_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay-publication-receipt.json", "4c75468663af0de60b37cdbabfca384c4e7f75e25a6155c2ff1c33f654d3f1d7", 1902)
V9_KERNEL = (
    Owner("tools/reproduce_owned_native_source_build_v9.py", "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f", 81124),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V9.md", "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc", 4960),
    Owner("oracle/phase2/native-source-build-v9.json", "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da", 9134),
)
V7_KERNEL = (
    Owner("tools/reproduce_owned_native_source_build_v7.py", "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7", 300624),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V7.md", "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313", 8063),
    Owner("oracle/phase2/native-source-build-v7.json", "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819", 28924),
)
V30 = (
    Owner("tools/render_candidate_current_overview_v30.py", "a8c2bb2e0ccfab0b76b5387437fe48279e01ca1034739a67967f543f1930c507", 60771),
    Owner("docs/evidence/candidate-current-overview-v30.inputs.json", "ea2ea381a22a9a23344ff40505d975aba8d25704d2ad90e03b58018fda44ca0f", 65902),
    Owner("docs/evidence/candidate-current-overview-v30.json", "b04db4e93dc74bb9200c13133c0a33bd33961b5f35e5810e74de65b29fcab534", 293980),
    Owner("docs/evidence/candidate-current-overview-v30.svg", "a3dbbb69c5140d15588463e0e3579d5bea5d95587f1abf444b6679cd3361d4c6", 12987),
)
TOOLCHAIN = (
    ToolOwner("/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/rustc", "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6", 644784, 2064, 31359570, 0o755, 1000),
    ToolOwner("/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/cargo", "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66", 42185192, 2064, 31359488, 0o755, 1000),
    ToolOwner("/usr/bin/x86_64-linux-gnu-gcc-13", "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26", 1023032, 1048708, 10445975, 0o755, 65534),
    ToolOwner("/usr/bin/x86_64-linux-gnu-readelf", "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0", 789280, 1048708, 10446013, 0o755, 65534),
)


class GateError(Exception):
    """Reject a substituted owner, unsafe operation, or unproved build."""


class ForbiddenEffect(GateError):
    """A source-only self-test physically blocked a real outside effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise GateError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact, complete bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                           allow_nan=False, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise GateError("reject noncanonical machine evidence") from error


def checked_sha256(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require an exact, lowercase caller-pinned SHA-256: " + label)
    return value


def owner_document(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size}


def tool_document(owner: ToolOwner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size,
            "device": owner.device, "inode": owner.inode, "mode": owner.mode,
            "uid": owner.uid, "nlink": owner.nlink}


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "reject a duplicate JSON key in " + label)
            result[key] = value
        return result

    def constant(_value: str) -> Any:
        raise GateError("reject a nonfinite JSON number in " + label)

    try:
        document = json.loads(raw.decode("utf-8", "strict"),
                              object_pairs_hook=unique, parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GateError("reject malformed JSON: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "require an exact canonical JSON object: " + label)
    return document


def verify_runtime() -> None:
    require(sys.executable == PYTHON
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "require the pinned, isolated, bytecode-free CPython 3.14.6 oracle")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "never import or activate a candidate in a Rust build source gate")


def checked_relative(value: str) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one exact bounded repository-relative owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value
            and all(piece not in ("", ".", "..") for piece in parsed.parts)
            and "\\" not in value,
            "reject an escaped, redirected, or ambiguous repository owner")
    return parsed.parts


def read_owner(owner: Owner) -> tuple[bytes, dict[str, Any]]:
    require(type(owner) is Owner and 0 < owner.size <= MAX_SOURCE_BYTES,
            "bound every immutable, first-party repository owner")
    checked_sha256(owner.sha256, owner.path)
    parts = checked_relative(owner.path)
    directory_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_NOFOLLOW", 0))
    file_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                  | getattr(os, "O_NOFOLLOW", 0))
    folders: list[int] = []
    handle: int | None = None
    try:
        folders.append(os.open(str(ROOT), directory_flags))
        for part in parts[:-1]:
            visible = os.stat(part, dir_fd=folders[-1], follow_symlinks=False)
            child = os.open(part, directory_flags, dir_fd=folders[-1])
            folders.append(child)
            found = os.fstat(child)
            require(stat.S_ISDIR(found.st_mode)
                    and (found.st_dev, found.st_ino)
                    == (visible.st_dev, visible.st_ino),
                    "reject a substituted or symlinked source-owner parent")
        visible = os.stat(parts[-1], dir_fd=folders[-1], follow_symlinks=False)
        handle = os.open(parts[-1], file_flags, dir_fd=folders[-1])
        before = os.fstat(handle)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and before.st_size == owner.size
                and (before.st_dev, before.st_ino, before.st_size,
                     before.st_uid, before.st_nlink)
                == (visible.st_dev, visible.st_ino, visible.st_size,
                    visible.st_uid, visible.st_nlink),
                "reject a linked, foreign, truncated, or exchanged owner: "
                + owner.path)
        chunks: list[bytes] = []
        remaining = owner.size
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            require(type(piece) is bytes and bool(piece),
                    "reject a truncated descriptor-bound immutable owner")
            chunks.append(piece)
            remaining -= len(piece)
        require(os.read(handle, 1) == b"", "reject an appended immutable owner")
        raw = b"".join(chunks)
        after = os.fstat(handle)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and digest(raw) == owner.sha256,
                "reject an owner changed during complete authentication: "
                + owner.path)
        return raw, {**owner_document(owner), "device": after.st_dev,
                     "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
                     "uid": after.st_uid, "nlink": after.st_nlink}
    finally:
        if handle is not None:
            os.close(handle)
        for folder in reversed(folders):
            os.close(folder)


def read_toolchain(owner: ToolOwner) -> dict[str, Any]:
    require(type(owner) is ToolOwner and 0 < owner.size <= MAX_TOOLCHAIN_BYTES,
            "bound every separately authenticated native tool")
    checked_sha256(owner.sha256, owner.path)
    require(PurePosixPath(owner.path).is_absolute(),
            "pin every compiler and inspector to an exact absolute owner")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    visible = os.stat(owner.path, follow_symlinks=False)
    descriptor = os.open(owner.path, flags)
    try:
        before = os.fstat(descriptor)
        expected = (owner.device, owner.inode, owner.size, owner.uid,
                    owner.nlink, owner.mode)
        actual = (before.st_dev, before.st_ino, before.st_size, before.st_uid,
                  before.st_nlink, stat.S_IMODE(before.st_mode))
        require(stat.S_ISREG(before.st_mode) and actual == expected
                and (visible.st_dev, visible.st_ino, visible.st_size,
                     visible.st_uid, visible.st_nlink,
                     stat.S_IMODE(visible.st_mode)) == expected,
                "reject a substituted, linked, or unpinned compiler: " + owner.path)
        hashed = hashlib.sha256()
        remaining = owner.size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(piece) is bytes and bool(piece),
                    "reject truncated streaming toolchain authentication")
            hashed.update(piece)
            remaining -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "reject an appended compiler or native inspector")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and hashed.hexdigest() == owner.sha256,
                "reject a tool altered during complete streaming authentication")
        return tool_document(owner)
    finally:
        os.close(descriptor)


def boundary() -> dict[str, Any]:
    return {
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "qualified_candidate_count": 0, "candidate_imports": 0,
        "candidate_workers_started": 0, "candidate_processes_started": 0,
        "reference_processes_started": 0, "compiler_processes_started": 0,
        "native_builds_started": 0, "source_builds_started": 0,
        "native_libraries_loaded": 0, "native_activations": 0,
        "canonical_native_target_reads": 0,
        "canonical_native_target_stats": 0, "source_apply_count": 0,
        "workspace_mutations": 0, "network_requests": 0,
        "threads_started": 0, "signal_handlers_installed": 0,
        "signal_masks_installed": 0, "recovery_locks_acquired": 0,
        "recovery_journals_created": 0, "clock_samples": 0,
        "timing_trials_run": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "uncompressed_c_archive_bytes_read": 0,
        "uncompressed_rust_archive_bytes_read": 0,
        "uncompressed_zig_archive_bytes_read": 0,
        "upstream_test_processes_started": 0,
        "upstream_unittest_methods_executed": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
    }


def current_history() -> dict[str, Any]:
    return {
        "graph_version": 30,
        "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "authenticated_digest_addressed_history_paths": CURRENT_HISTORY_REFERENCES,
        "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVERS,
        "rust_status": "FAIL", "rust_semantic_mismatch_count": 1087,
        "rust_verified_passing_case_count": 7438,
        "c_status": "FAIL", "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "historical_c_semantic_mismatch_count": 1262,
        "zig_status": "FAIL", "zig_semantic_mismatch_count": 2172,
        "zig_verified_passing_case_count": 2847,
        "historical_zig_preflight_candidate_workers": 0,
        "qualified_candidate_count": 0,
        "corrected_rust_candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "final_holdout_opened": False, "winner_selected": False,
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    source_pin = checked_sha256(source_pin, "V12 source")
    protocol_pin = checked_sha256(protocol_pin, "V12 protocol")
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "phase": "CORRECTED FIRST-PARTY RUST SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "goal": owner_document(GOAL),
        "phase_one": owner_document(PHASE_ONE),
        "runtime": {"implementation": "CPython", "version": "3.14.6",
                    "path": PYTHON, "sha256": PYTHON_SHA256,
                    "isolated": True, "bytecode_writes": False},
        "oracle": {"suite_count": SUITE_COUNT,
                   "case_execution_denominator": CASE_COUNT,
                   "named_private_waiver_count": PRIVATE_WAIVERS,
                   "manifest": owner_document(PHASE_ONE)},
        "current_history": current_history(),
        "current_graph_v30": [owner_document(item) for item in V30],
        "preserved_v11": {
            "owners": [owner_document(item) for item in PREVIOUS_BUILD_V11],
            "actual_archive": owner_document(PREVIOUS_BUILD_ARCHIVE),
            "actual_receipt": owner_document(PREVIOUS_BUILD_RECEIPT),
            "actual_status": "PASS", "actual_process_count": 28,
            "actual_bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "actual_historical_public_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "historical_public_adapter_reused": False,
            "historical_archive_decompressed": False,
            "historical_source_modified": False,
            "historical_protocol_modified": False,
            "historical_contract_modified": False,
            "v10_high_level_context_called": False,
            "v10_snapshot_called": False,
            "v10_reproduction_called": False,
            "v11_build_called": False,
        },
        "first_party_rust_source": {
            "family": FAMILY, "owners": [owner_document(item)
                                             for item in RUST_OWNERS],
            "owner_count": len(RUST_OWNERS),
            "cargo_package_count": 1, "external_dependency_count": 0,
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "stdlib_re_engine": "FORBIDDEN", "cpython_sre_engine": "FORBIDDEN",
            "third_party_regex_engine": "FORBIDDEN",
            "other_candidate_engine": "FORBIDDEN", "fallback": "FORBIDDEN",
            "canonical_source_mutation": "FORBIDDEN",
        },
        "first_party_bridge_overlay": {
            "owners": [owner_document(item) for item in BRIDGE_REPAIR],
            "original": owner_document(RUST_OWNERS[2]),
            "derived": {"path": BRIDGE_PATH,
                        "sha256": BRIDGE_DERIVED_SHA256,
                        "bytes": BRIDGE_DERIVED_BYTES,
                        "materialized": False},
            "application": "EXACTLY ONCE PER EXPLICIT FUTURE PRIVATE PHASE",
        },
        "corrected_first_party_public_overlay": {
            "owners": [owner_document(item) for item in PUBLIC_REPAIR_V2],
            "original": owner_document(RUST_OWNERS[-1]),
            "derived": {"path": PUBLIC_PATH,
                        "sha256": PUBLIC_DERIVED_SHA256,
                        "bytes": PUBLIC_DERIVED_BYTES,
                        "materialized": False},
            "historical_v1_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "historical_v1_reused": False,
            "application": "EXACTLY ONCE PER EXPLICIT FUTURE PRIVATE PHASE",
        },
        "low_level_first_party_kernels": {
            "v9": [owner_document(item) for item in V9_KERNEL],
            "v7": [owner_document(item) for item in V7_KERNEL],
            "v9_high_level_context_called": False,
            "v10_high_level_context_called": False,
            "v10_dual_snapshot_called": False,
            "v10_reproduction_called": False,
            "v11_high_level_build_called": False,
            "v12_owns_snapshot_and_reproduction": True,
        },
        "future_private_snapshot": {
            "explicit_build_required": True, "root_parent": "/tmp",
            "interoperable_previous_root_prefix": ROOT_PREFIX,
            "phase_names": list(PHASES),
            "both_distinct_phases_precreated": True,
            "directory_mode": "0700", "file_mode": "0600",
            "creation_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "complete_source_owners_per_phase": 9,
            "unchanged_source_owners_per_phase": 7,
            "bridge_overlays_per_phase": 1,
            "corrected_public_overlays_per_phase": 1,
            "existing_destinations": "FORBIDDEN",
            "borrowed_phase_inodes": "FORBIDDEN",
            "canonical_workspace_writes": "FORBIDDEN",
        },
        "future_native_build": {
            "explicit_build_required": True,
            "independent_nine_original_owner_pins_required": True,
            "independent_bridge_derived_pin_required": True,
            "independent_corrected_public_derived_pin_required": True,
            "phase_count": len(PHASES),
            "processes_per_phase": len(PROCESS_NAMES),
            "total_actual_processes_required": 2 * len(PROCESS_NAMES),
            "ordered_process_names_per_phase": list(PROCESS_NAMES),
            "unique_successful_process_ids_required": True,
            "toolchain": [tool_document(item) for item in TOOLCHAIN],
            "cargo_required_flags": ["--release", "--locked", "--offline",
                                      "--frozen", "--target-dir"],
            "cargo_net_offline": True, "network": "FORBIDDEN",
            "engine_name": ENGINE_NAME, "bridge_name": BRIDGE_NAME,
            "independent_phase_elf_inodes_required": True,
            "complete_raw_phase_elf_comparison_required": True,
            "native_loading": "FORBIDDEN", "candidate_execution": "FORBIDDEN",
            "prebuilt_artifacts": "FORBIDDEN",
            "passing_build_qualifies_candidate": False,
        },
        "future_evidence": {
            "explicit_build_required": True, "directory": EVIDENCE_PATH,
            "archive_prefix": "native-source-build-v12-rust-",
            "archive_suffix": ".json.gz", "failure_suffix": "-failures",
            "receipt_suffix": "-publication-receipt.json",
            "exclusive_creation": True, "no_follow": True,
            "file_mode": "0600", "zero_mtime_single_member_gzip": True,
            "same_inode_complete_readback": True,
            "archive_and_directory_fsync": True,
            "prebuild_repository_evidence_owner_count":
                CURRENT_EVIDENCE_OWNERS,
            "prebuild_authenticated_history_reference_count":
                CURRENT_HISTORY_REFERENCES,
            "new_actual_owners_after_successful_publication_only": 2,
            "publication_qualifies_candidate": False,
        },
        "phase_boundary": boundary(),
    }


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {kind: 0 for kind in (
            "filesystem", "write", "process", "import", "network", "thread",
            "clock", "native", "lock", "signal", "decompression")}

    def deny(self, owner: Any, name: str, kind: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise ForbiddenEffect("physically blocked source-only " + kind
                                  + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names, kind in (
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat",
                    "resolve"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename",
                  "replace", "fsync"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename",
                    "replace"), "write"),
            (tempfile, ("mkdtemp", "mkstemp"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output"), "process"),
            (importlib, ("import_module",), "import"),
            (socket, ("socket", "create_connection"), "network"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time"),
             "clock"),
            (ctypes, ("CDLL", "PyDLL"), "native"),
            (fcntl, ("flock", "lockf"), "lock"),
            (signal, ("signal", "pthread_sigmask"), "signal"),
            (gzip, ("decompress", "open", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        ):
            for name in names:
                self.deny(owner, name, kind)
        return self

    def __exit__(self, *_details: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def expected_source_owner(path: str) -> tuple[str, int]:
    matches = [item for item in RUST_OWNERS if item.path == path]
    require(len(matches) == 1, "require one unique canonical Rust source owner")
    item = matches[0]
    if path == BRIDGE_PATH:
        return BRIDGE_DERIVED_SHA256, BRIDGE_DERIVED_BYTES
    if path == PUBLIC_PATH:
        return PUBLIC_DERIVED_SHA256, PUBLIC_DERIVED_BYTES
    return item.sha256, item.size


def synthetic_plan() -> dict[str, Any]:
    phases: list[dict[str, Any]] = []
    for index, name in enumerate(PHASES):
        sources: dict[str, Any] = {}
        for offset, owner in enumerate(RUST_OWNERS):
            expected_sha, expected_bytes = expected_source_owner(owner.path)
            sources[owner.path] = {
                "sha256": expected_sha, "bytes": expected_bytes,
                "device": 9001, "inode": 10000 + 100 * index + offset,
                "mode": 0o600, "nlink": 1,
                "overlay_count": int(owner.path in (BRIDGE_PATH, PUBLIC_PATH)),
            }
        phases.append({
            "name": name, "directory_mode": 0o700,
            "directory_device": 9001, "directory_inode": 11000 + index,
            "fresh_source_owners": sources,
            "native_outputs": {
                "engine": {"file_name": ENGINE_NAME,
                           "sha256": digest(b"synthetic-owned-rust-engine"),
                           "size_bytes": 8192, "device": 9001,
                           "inode": 12000 + 10 * index},
                "bridge": {"file_name": BRIDGE_NAME,
                           "sha256": digest(b"synthetic-owned-rust-bridge"),
                           "size_bytes": 16384, "device": 9001,
                           "inode": 12001 + 10 * index},
            },
        })
    return {"family": FAMILY, "root_prefix": ROOT_PREFIX,
            "history_owner_count": CURRENT_EVIDENCE_OWNERS,
            "history_reference_count": CURRENT_HISTORY_REFERENCES,
            "phases": phases,
            "processes": [{"name": name, "pid": 20000 + index,
                           "exit_status": 0}
                          for index, name in enumerate(PROCESS_NAMES * 2)],
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "cargo_external_dependency_count": 0,
            "network_requests": 0, "native_libraries_loaded": 0,
            "candidate_processes_started": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "holdout": "NOT OPENED", "candidate_qualified": False,
            "winner_selected": False}


def validate_synthetic_plan(plan: Any) -> dict[str, Any]:
    require(type(plan) is dict and plan.get("family") == FAMILY
            and plan.get("root_prefix") == ROOT_PREFIX
            and plan.get("history_owner_count") == CURRENT_EVIDENCE_OWNERS
            and plan.get("history_reference_count") == CURRENT_HISTORY_REFERENCES
            and plan.get("bridge_derived_sha256") == BRIDGE_DERIVED_SHA256
            and plan.get("public_derived_sha256") == PUBLIC_DERIVED_SHA256
            and plan.get("cargo_external_dependency_count") == 0
            and plan.get("network_requests") == 0
            and plan.get("native_libraries_loaded") == 0
            and plan.get("candidate_processes_started") == 0
            and plan.get("hidden_cases_read") == 0
            and plan.get("clock_samples") == 0
            and plan.get("holdout") == "NOT OPENED"
            and plan.get("candidate_qualified") is False
            and plan.get("winner_selected") is False,
            "reject stale history, delegation, activation, timing, or holdout")
    phases = plan.get("phases")
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases] == list(PHASES),
            "require exactly two ordered independent private Rust phases")
    phase_identities: set[tuple[int, int]] = set()
    source_identities: set[tuple[int, int]] = set()
    for phase in phases:
        require(type(phase) is dict and phase.get("directory_mode") == 0o700
                and type(phase.get("directory_device")) is int
                and type(phase.get("directory_inode")) is int,
                "require genuine private owner-only phase directories")
        identity = (phase["directory_device"], phase["directory_inode"])
        require(identity not in phase_identities,
                "reject aliased independent phase directories")
        phase_identities.add(identity)
        sources = phase.get("fresh_source_owners")
        require(type(sources) is dict
                and set(sources) == {item.path for item in RUST_OWNERS},
                "require seven originals and both complete private Rust overlays")
        for item in RUST_OWNERS:
            row = sources.get(item.path)
            expected_sha, expected_bytes = expected_source_owner(item.path)
            require(type(row) is dict and row.get("sha256") == expected_sha
                    and row.get("bytes") == expected_bytes
                    and row.get("mode") == 0o600 and row.get("nlink") == 1
                    and row.get("overlay_count")
                    == int(item.path in (BRIDGE_PATH, PUBLIC_PATH))
                    and type(row.get("device")) is int
                    and type(row.get("inode")) is int,
                    "reject an unowned or substituted source: " + item.path)
            identity = (row["device"], row["inode"])
            require(identity not in source_identities,
                    "reject a shared, linked, or reused phase source inode")
            source_identities.add(identity)
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                "require both first-party reproducible native output roles")
        for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
            output = outputs[role]
            expected = digest(("synthetic-owned-rust-" + role).encode("ascii"))
            require(type(output) is dict and output.get("file_name") == filename
                    and output.get("sha256") == expected
                    and type(output.get("size_bytes")) is int
                    and output["size_bytes"] > 0
                    and type(output.get("device")) is int
                    and type(output.get("inode")) is int,
                    "reject an incomplete or foreign synthetic ELF role")
    for role in ("engine", "bridge"):
        left = phases[0]["native_outputs"][role]
        right = phases[1]["native_outputs"][role]
        require(left["sha256"] == right["sha256"]
                and left["size_bytes"] == right["size_bytes"]
                and (left["device"], left["inode"])
                != (right["device"], right["inode"]),
                "reject irreproducible bytes or a borrowed phase-native inode")
    processes = plan.get("processes")
    require(type(processes) is list
            and len(processes) == 2 * len(PROCESS_NAMES),
            "require exactly 28 real ordered process slots")
    pids: set[int] = set()
    for index, row in enumerate(processes):
        require(type(row) is dict
                and row.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and type(row.get("pid")) is int and row["pid"] > 0
                and row["pid"] not in pids and row.get("exit_status") == 0,
                "reject a reordered, failed, invented, or reused build process")
        pids.add(row["pid"])
    return {"phase_count": len(phases), "source_owner_count_per_phase": 9,
            "unique_source_inode_count": len(source_identities),
            "native_roles_per_phase": 2,
            "unique_process_count": len(pids)}


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    expected_contract = contract_document(source_pin, protocol_pin)
    require(digest(canonical(expected_contract))
            == checked_sha256(contract_pin, "V12 canonical contract"),
            "reject a substituted canonical source-only contract")
    accepted: list[str] = []
    rejected: list[str] = []
    plan = synthetic_plan()

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except GateError:
            rejected.append(name)
            return
        raise GateError("accepted a hostile synthetic control: " + name)

    with SourceOnlyWall() as wall:
        witness = validate_synthetic_plan(plan)
        accepted.append("complete-corrected-owned-two-phase-synthetic-plan")
        require(witness == {"phase_count": 2,
                           "source_owner_count_per_phase": 9,
                           "unique_source_inode_count": 18,
                           "native_roles_per_phase": 2,
                           "unique_process_count": 28},
                "close the complete independent synthetic build denominator")
        accepted.append("exact-nine-owners-and-twenty-eight-processes")

        def mutated(name: str, change: Any) -> None:
            def operation() -> None:
                candidate = copy.deepcopy(plan)
                change(candidate)
                validate_synthetic_plan(candidate)
            reject(name, operation)

        for key, bad in (
            ("family", "zig"), ("root_prefix", "rebar-phase2-native-build-v12-rust-"),
            ("history_owner_count", 137), ("history_reference_count", 142),
            ("bridge_derived_sha256", "0" * 64),
            ("public_derived_sha256", HISTORICAL_PUBLIC_DERIVED_SHA256),
            ("cargo_external_dependency_count", 1), ("network_requests", 1),
            ("native_libraries_loaded", 1), ("candidate_processes_started", 1),
            ("hidden_cases_read", 1), ("clock_samples", 1),
            ("holdout", "OPENED"), ("candidate_qualified", True),
            ("winner_selected", True),
        ):
            mutated("reject-" + key,
                    lambda candidate, k=key, value=bad:
                    candidate.__setitem__(k, value))
        for phase_index in range(2):
            mutated("reject-phase-name-" + str(phase_index),
                    lambda candidate, i=phase_index:
                    candidate["phases"][i].__setitem__("name", "reference-c"))
            mutated("reject-phase-mode-" + str(phase_index),
                    lambda candidate, i=phase_index:
                    candidate["phases"][i].__setitem__("directory_mode", 0o755))
            for owner in RUST_OWNERS:
                for field, bad in (("sha256", "0" * 64),
                                   ("bytes", 0), ("mode", 0o644),
                                   ("nlink", 2)):
                    mutated("reject-source-" + str(phase_index) + "-"
                            + owner.path + "-" + field,
                            lambda candidate, i=phase_index, path=owner.path,
                            k=field, value=bad:
                            candidate["phases"][i]["fresh_source_owners"]
                            [path].__setitem__(k, value))
            for role in ("engine", "bridge"):
                mutated("reject-native-" + str(phase_index) + "-" + role,
                        lambda candidate, i=phase_index, r=role:
                        candidate["phases"][i]["native_outputs"]
                        [r].__setitem__("sha256", "0" * 64))
        mutated("reject-reused-phase-source-inode",
                lambda candidate: candidate["phases"][1]
                ["fresh_source_owners"][RUST_OWNERS[0].path].__setitem__(
                    "inode", candidate["phases"][0]
                    ["fresh_source_owners"][RUST_OWNERS[0].path]["inode"]))
        mutated("reject-reused-phase-directory-inode",
                lambda candidate: candidate["phases"][1].__setitem__(
                    "directory_inode", candidate["phases"][0]
                    ["directory_inode"]))
        for index in range(2 * len(PROCESS_NAMES)):
            mutated("reject-process-order-" + str(index),
                    lambda candidate, i=index:
                    candidate["processes"][i].__setitem__("name", "borrowed"))
            mutated("reject-process-status-" + str(index),
                    lambda candidate, i=index:
                    candidate["processes"][i].__setitem__("exit_status", 1))
        mutated("reject-reused-process-id",
                lambda candidate: candidate["processes"][1].__setitem__(
                    "pid", candidate["processes"][0]["pid"]))
        effect_probes = (
            ("filesystem", lambda: os.stat(str(ROOT))),
            ("write", lambda: os.mkdir("v12-forbidden")),
            ("process", lambda: subprocess.run(["false"])),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("native", lambda: ctypes.CDLL("v12-forbidden.so")),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden")),
        )
        for kind, action in effect_probes:
            previous = wall.blocked[kind]
            reject("physically-block-" + kind, action)
            require(wall.blocked[kind] == previous + 1,
                    "prove that each real forbidden source effect was blocked")
        require(len(rejected) >= 150
                and all(count > 0 for count in wall.blocked.values()),
                "exercise every hostile owner and physical source-only boundary")
        blocked = dict(wall.blocked)
    return {"schema": SCHEMA + "-source-only-self-test", "version": VERSION,
            "status": "PASS", "source_sha256": source_pin,
            "protocol_sha256": protocol_pin, "contract_sha256": contract_pin,
            "mode": "PHYSICALLY STERILE SYNTHETIC SOURCE ONLY",
            "accepted_control_count": len(accepted),
            "rejected_hostile_control_count": len(rejected),
            "blocked_effects_by_kind": blocked,
            "synthetic_independent_phase_count": witness["phase_count"],
            "synthetic_source_owner_count_per_phase":
                witness["source_owner_count_per_phase"],
            "synthetic_unique_source_inode_count":
                witness["unique_source_inode_count"],
            "synthetic_unique_process_count": witness["unique_process_count"],
            "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
            "authenticated_digest_addressed_history_paths":
                CURRENT_HISTORY_REFERENCES,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVERS,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "corrected_public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "historical_public_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "filesystem_reads": 0, "filesystem_writes": 0,
            "archive_decompressions": 0, **boundary()}


def load_frozen_module(name: str, owner: Owner,
                       raw: bytes) -> types.ModuleType:
    require(type(name) is str and name.startswith("_rebar_v12_frozen_")
            and name not in sys.modules and type(raw) is bytes
            and len(raw) == owner.size and digest(raw) == owner.sha256,
            "load only an exact privately named independently frozen source")
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / owner.path)
    module.__package__ = ""
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    require(not any(item == "candidates" or item.startswith("candidates.")
                    for item in sys.modules),
            "never load a candidate while inspecting first-party build tools")
    return module


def validate_previous_receipt(receipt: dict[str, Any],
                              archive_owner: dict[str, Any]) -> None:
    require(receipt.get("schema")
            == "rebar-phase2-owned-native-source-build-v11-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == "phase2-v11-rust-dual-overlay"
            and receipt.get("source_sha256") == PREVIOUS_BUILD_V11[0].sha256
            and receipt.get("protocol_sha256") == PREVIOUS_BUILD_V11[1].sha256
            and receipt.get("contract_sha256") == PREVIOUS_BUILD_V11[2].sha256
            and receipt.get("archive_relative") == PREVIOUS_BUILD_ARCHIVE.path
            and receipt.get("archive_sha256") == PREVIOUS_BUILD_ARCHIVE.sha256
            and receipt.get("archive_bytes") == PREVIOUS_BUILD_ARCHIVE.size
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("bridge_derived_sha256") == BRIDGE_DERIVED_SHA256
            and receipt.get("public_derived_sha256")
            == HISTORICAL_PUBLIC_DERIVED_SHA256
            and receipt.get("bridge_overlay_apply_count") == 2
            and receipt.get("public_overlay_apply_count") == 2
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("winner_selected") is False,
            "preserve the real immutable V11 build and its historical adapter")
    publication = receipt.get("archive_publication")
    directory = receipt.get("archive_directory_fsync")
    require(type(publication) is dict and type(directory) is dict
            and publication.get("path") == str(ROOT / PREVIOUS_BUILD_ARCHIVE.path)
            and publication.get("sha256") == PREVIOUS_BUILD_ARCHIVE.sha256
            and publication.get("bytes") == PREVIOUS_BUILD_ARCHIVE.size
            and publication.get("device") == archive_owner["device"]
            and publication.get("inode") == archive_owner["inode"]
            and publication.get("exclusive_creation") is True
            and publication.get("file_fsync_completed") is True
            and publication.get("same_inode_readback_verified") is True
            and directory.get("completed") is True,
            "bind historical V11 publication to its actual durable archive inode")


def validate_current_summary(summary: dict[str, Any]) -> None:
    require(summary.get("schema") == "rebar-candidate-current-overview-v30-summary"
            and summary.get("status") == "PASS"
            and summary.get("full_case_denominator") == CASE_COUNT
            and summary.get("suite_count") == SUITE_COUNT
            and summary.get("private_waiver_count") == PRIVATE_WAIVERS
            and summary.get("repository_evidence_owner_count")
            == CURRENT_EVIDENCE_OWNERS
            and summary.get("authenticated_digest_addressed_history_paths")
            == CURRENT_HISTORY_REFERENCES
            and summary.get("qualified_candidate_count") == 0
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7325
            and summary.get("historical_c_semantic_mismatch_count") == 1262
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087
            and summary.get("rust_original_campaign_verified_passing_case_count") == 7438
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
            and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
            and summary.get("historical_zig_preflight_failure", {}).get(
                "actual_candidate_workers") == 0
            and summary.get("final_comparison_planned_case_count") == 4194304
            and summary.get("final_comparison_cases_generated") is False
            and summary.get("final_holdout_opened") is False
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("confidence_intervals") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED"
            and summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False,
            "preserve exact V30 149/154 history and every actual family failure")


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    source_pin = checked_sha256(source_pin, "V12 source")
    protocol_pin = checked_sha256(protocol_pin, "V12 protocol")
    contract_pin = checked_sha256(contract_pin, "V12 contract")
    source_path = ROOT / SOURCE_PATH
    protocol_path = ROOT / PROTOCOL_PATH
    source_size = os.stat(source_path, follow_symlinks=False).st_size
    protocol_size = os.stat(protocol_path, follow_symlinks=False).st_size
    require(0 < source_size <= MAX_SOURCE_BYTES
            and 0 < protocol_size <= MAX_SOURCE_BYTES,
            "bound independently pinned V12 source and protocol owners")
    frozen_source = Owner(SOURCE_PATH, source_pin, source_size)
    frozen_protocol = Owner(PROTOCOL_PATH, protocol_pin, protocol_size)
    expected_contract = canonical(contract_document(source_pin, protocol_pin))
    frozen_contract = Owner(CONTRACT_PATH, contract_pin, len(expected_contract))
    raw: dict[str, bytes] = {}
    authenticated: dict[str, dict[str, Any]] = {}
    groups = (
        (frozen_source, frozen_protocol, frozen_contract, GOAL, PHASE_ONE),
        RUST_OWNERS, BRIDGE_REPAIR, PUBLIC_REPAIR_V2,
        PREVIOUS_BUILD_V11, (PREVIOUS_BUILD_ARCHIVE, PREVIOUS_BUILD_RECEIPT),
        V9_KERNEL, V7_KERNEL, V30,
    )
    for group in groups:
        for owner in group:
            payload, observed = read_owner(owner)
            raw[owner.path] = payload
            authenticated[owner.path] = observed
    require(raw[CONTRACT_PATH] == expected_contract
            and digest(expected_contract) == contract_pin,
            "reject an incomplete, noncanonical, or substituted V12 contract")
    require(strict_json(raw[CONTRACT_PATH], "V12 contract")
            == contract_document(source_pin, protocol_pin),
            "bind the exact three independently pinned V12 owners")
    summary = strict_json(raw[V30[2].path], "actual V30 current summary")
    validate_current_summary(summary)
    matrix = strict_json(raw[PHASE_ONE.path], "immutable original P0 matrix")
    denominator = matrix.get("denominator")
    require(matrix.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and type(denominator) is dict
            and denominator.get("final_required_case_execution_denominator")
            == CASE_COUNT
            and denominator.get("frozen_planned_case_execution_denominator")
            == CASE_COUNT
            and denominator.get("private_upstream_methods_outside_public_denominator")
            == PRIVATE_WAIVERS
            and type(denominator.get("counted_suite_ids")) is list
            and len(denominator["counted_suite_ids"]) == SUITE_COUNT,
            "retain all 31,237 original checks and the 13 named private waivers")
    receipt = strict_json(raw[PREVIOUS_BUILD_RECEIPT.path],
                          "actual V11 durable build receipt")
    validate_previous_receipt(receipt,
                              authenticated[PREVIOUS_BUILD_ARCHIVE.path])
    toolchain = [read_toolchain(item) for item in TOOLCHAIN]
    bridge = load_frozen_module("_rebar_v12_frozen_bridge_v1",
                                BRIDGE_REPAIR[0], raw[BRIDGE_REPAIR[0].path])
    bridge_contract = strict_json(raw[BRIDGE_REPAIR[2].path],
                                  "frozen first-party bridge V1")
    require(bridge.SCHEMA == "rebar-phase2-owned-rust-source-repair-v1"
            and bridge.ORIGINAL_PATH == BRIDGE_PATH
            and bridge.ORIGINAL_SHA256 == RUST_OWNERS[2].sha256
            and bridge.ORIGINAL_BYTES == RUST_OWNERS[2].size
            and bridge.DERIVED_SHA256 == BRIDGE_DERIVED_SHA256
            and bridge.DERIVED_BYTES == BRIDGE_DERIVED_BYTES
            and bridge_contract == bridge.contract_document(
                BRIDGE_REPAIR[0].sha256, BRIDGE_REPAIR[1].sha256),
            "authenticate the immutable first-party V9-compatible bridge repair")
    derived_bridge = bridge.repaired_source(
        raw[BRIDGE_PATH], RUST_OWNERS[2].sha256, RUST_OWNERS[2].size)
    require(type(derived_bridge) is bytes
            and len(derived_bridge) == BRIDGE_DERIVED_BYTES
            and digest(derived_bridge) == BRIDGE_DERIVED_SHA256,
            "derive the exact anchored first-party Rust bridge in memory only")
    public = load_frozen_module("_rebar_v12_frozen_public_v2",
                                PUBLIC_REPAIR_V2[0],
                                raw[PUBLIC_REPAIR_V2[0].path])
    public_contract = strict_json(raw[PUBLIC_REPAIR_V2[2].path],
                                  "frozen corrected first-party public V2")
    require(public.SCHEMA
            == "rebar-phase2-owned-rust-public-contract-source-repair-v2"
            and public.ORIGINAL_SHA256 == RUST_OWNERS[-1].sha256
            and public.ORIGINAL_BYTES == RUST_OWNERS[-1].size
            and public.DERIVED_SHA256 == PUBLIC_DERIVED_SHA256
            and public.DERIVED_BYTES == PUBLIC_DERIVED_BYTES
            and public.V1_DERIVED_SHA256 == HISTORICAL_PUBLIC_DERIVED_SHA256
            and public_contract == public.contract_document(
                PUBLIC_REPAIR_V2[0].sha256, PUBLIC_REPAIR_V2[1].sha256),
            "reject the stale V1 adapter or a substituted corrected V2 repair")
    public_context, derived_public = public.verify_context(
        PUBLIC_REPAIR_V2[0].sha256, PUBLIC_REPAIR_V2[1].sha256,
        PUBLIC_REPAIR_V2[2].sha256)
    require(type(public_context) is dict
            and public_context.get("schema")
            == "rebar-phase2-owned-rust-public-contract-source-repair-v2-read-only-frozen-context"
            and public_context.get("status") == "PASS"
            and public_context.get("corrected_derived_sha256")
            == PUBLIC_DERIVED_SHA256
            and public_context.get("corrected_derived_bytes")
            == PUBLIC_DERIVED_BYTES
            and public_context.get("repository_evidence_owner_count")
            == CURRENT_EVIDENCE_OWNERS
            and public_context.get("authenticated_digest_addressed_history_paths")
            == CURRENT_HISTORY_REFERENCES
            and public_context.get("candidate_workers_started") == 0
            and public_context.get("compiler_processes_started") == 0
            and public_context.get("native_libraries_loaded") == 0
            and public_context.get("uncompressed_rust_archive_bytes_read") == 0
            and public_context.get("clock_samples") == 0
            and public_context.get("final_holdout_opened") is False
            and public_context.get("winner_selected") is False
            and type(derived_public) is bytes
            and len(derived_public) == PUBLIC_DERIVED_BYTES
            and digest(derived_public) == PUBLIC_DERIVED_SHA256,
            "require the full genuinely corrected, read-only V2 provenance")
    v9 = load_frozen_module("_rebar_v12_frozen_low_level_v9", V9_KERNEL[0],
                            raw[V9_KERNEL[0].path])
    expected_originals = {item.path: (item.sha256, item.size)
                          for item in RUST_OWNERS}
    require(v9.SCHEMA == "rebar-phase2-owned-native-source-build-v9"
            and v9.FAMILY == FAMILY and tuple(v9.PHASES) == PHASES
            and tuple(v9.PROCESS_NAMES) == PROCESS_NAMES
            and v9.WORK_PREFIX + FAMILY + "-" == ROOT_PREFIX
            and v9.RUST_OWNERS == expected_originals
            and tuple(v9.V7_OWNERS["source"])
            == (V7_KERNEL[0].path, V7_KERNEL[0].sha256, V7_KERNEL[0].size)
            and v9.PINNED_RUSTC == TOOLCHAIN[0].path
            and v9.PINNED_CARGO == TOOLCHAIN[1].path
            and v9.PINNED_GCC == TOOLCHAIN[2].path
            and v9.PINNED_READELF == TOOLCHAIN[3].path
            and v9.ENGINE_NAME == ENGINE_NAME
            and v9.BRIDGE_NAME == BRIDGE_NAME,
            "authenticate only exact V9 low-level offline build primitives")
    cargo = raw[RUST_OWNERS[1].path].decode("utf-8", "strict")
    lock = raw[RUST_OWNERS[0].path].decode("utf-8", "strict")
    require("[dependencies" not in cargo
            and "[dev-dependencies" not in cargo
            and "[build-dependencies" not in cargo
            and lock.count("[[package]]") == 1
            and 'name = "rebar-rust-continuation"' in lock,
            "reject any third-party regex, borrowed engine, or external package")
    for owner in RUST_OWNERS:
        _, again = read_owner(owner)
        require(again == authenticated[owner.path],
                "never modify any canonical first-party Rust source")
    verify_runtime()
    outcome = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "version": VERSION, "status": "PASS", "read_only": True,
        "family": FAMILY, "source_sha256": source_pin,
        "protocol_sha256": protocol_pin, "contract_sha256": contract_pin,
        "authenticated_source_owner_count": len(authenticated),
        "authenticated_toolchain_owner_count": len(toolchain),
        "streamed_toolchain_bytes": sum(item.size for item in TOOLCHAIN),
        "toolchain": toolchain,
        "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "authenticated_digest_addressed_history_paths":
            CURRENT_HISTORY_REFERENCES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVERS,
        "actual_rust_semantic_mismatch_count": 1087,
        "actual_rust_verified_passing_case_count": 7438,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "historical_c_semantic_mismatch_count": 1262,
        "actual_zig_semantic_mismatch_count": 2172,
        "actual_zig_verified_passing_case_count": 2847,
        "historical_zig_preflight_candidate_workers": 0,
        "actual_previous_v11_process_count": 28,
        "actual_previous_v11_archive_sha256": PREVIOUS_BUILD_ARCHIVE.sha256,
        "actual_previous_v11_archive_compressed_bytes_read":
            PREVIOUS_BUILD_ARCHIVE.size,
        "actual_previous_v11_archive_decompressed": False,
        "historical_public_derived_sha256":
            HISTORICAL_PUBLIC_DERIVED_SHA256,
        "bridge_derived_source_sha256": BRIDGE_DERIVED_SHA256,
        "bridge_derived_source_bytes": BRIDGE_DERIVED_BYTES,
        "corrected_public_derived_source_sha256": PUBLIC_DERIVED_SHA256,
        "corrected_public_derived_source_bytes": PUBLIC_DERIVED_BYTES,
        "derived_sources_materialized": False,
        "cargo_package_count": 1, "external_dependency_count": 0,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "future_phase_count": 2,
        "future_complete_sources_per_phase": 9,
        "future_unchanged_sources_per_phase": 7,
        "future_bridge_overlays_per_phase": 1,
        "future_corrected_public_overlays_per_phase": 1,
        "future_compiler_process_count": 2 * len(PROCESS_NAMES),
        "v9_high_level_context_called": False,
        "v10_high_level_context_called": False,
        "v10_snapshot_called": False,
        "v10_reproduction_called": False,
        "v11_build_called": False,
        **boundary(),
    }
    return outcome, {"v9": v9, "bridge": bridge, "public": public,
                     "bridge_bytes": derived_bridge,
                     "public_bytes": derived_public,
                     "originals": {item.path: raw[item.path]
                                   for item in RUST_OWNERS}}


_ACTIVE: dict[str, Any] | None = None
_APPLIED: set[tuple[str, str]] = set()


def checked_workdir(value: str) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require an explicitly owned private Rust root")
    path = PurePosixPath(value)
    require(path.is_absolute() and str(path) == value
            and len(path.parts) == 3 and path.parts[1] == "tmp"
            and path.parts[2].startswith(ROOT_PREFIX)
            and len(path.parts[2]) > len(ROOT_PREFIX)
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in path.parts[2]),
            "reject an escaped or bridge-incompatible V9 private Rust root")
    return value


def copy_dual_snapshot(workdir: str, family: str, phase: str,
                       sources: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    require(_ACTIVE is not None, "require an explicitly pinned V12 actual build")
    state = _ACTIVE
    v9 = state["v9"]
    kernel = state["kernel"]
    checked_workdir(workdir)
    expected = {item.path for item in RUST_OWNERS}
    require(family == FAMILY and phase in PHASES and type(sources) is dict
            and set(sources) == expected and (workdir, phase) not in _APPLIED,
            "require a fresh V12 phase with exactly nine original source owners")
    paths = v9.phase_paths(workdir, family, phase)
    for peer in PHASES:
        peer_paths = v9.phase_paths(workdir, family, peer)
        for directory in (peer_paths["base"], peer_paths["source"],
                          peer_paths["source"] / "candidates",
                          peer_paths["source"] / "candidates/rust"):
            observed = os.lstat(directory)
            require(stat.S_ISDIR(observed.st_mode)
                    and stat.S_IMODE(observed.st_mode) == 0o700
                    and observed.st_uid == os.geteuid(),
                    "precreate both owner-only independent Rust phase trees")
    for item in RUST_OWNERS:
        require(type(sources[item.path]) is bytes
                and len(sources[item.path]) == item.size
                and digest(sources[item.path]) == item.sha256,
                "reject substituted canonical first-party Rust source")
    copies: dict[str, dict[str, Any]] = {}
    for item in sorted(RUST_OWNERS, key=lambda entry: entry.path):
        if item.path in (BRIDGE_PATH, PUBLIC_PATH):
            continue
        target = paths["source"] / item.path
        kernel.mkdir_private(target.parent)
        observed = kernel.write_fresh(target, sources[item.path],
                                      synchronize=False)
        observed["path"] = v9.sanitized(observed["path"], workdir, family)
        copies[item.path] = observed
    require(len(copies) == 7, "leave exactly both overlay destinations absent")
    bridge_result = state["bridge"].apply_private(
        str(paths["source"]), state["bridge_bytes"])
    public_result = state["public"].apply_private(
        str(paths["source"]), state["public_bytes"],
        PUBLIC_REPAIR_V2[0].sha256, PUBLIC_REPAIR_V2[1].sha256,
        PUBLIC_REPAIR_V2[2].sha256)
    require(type(bridge_result) is dict
            and bridge_result.get("status") == "PASS"
            and bridge_result.get("phase") == phase
            and bridge_result.get("source_apply_count") == 1
            and bridge_result.get("derived_sha256") == BRIDGE_DERIVED_SHA256
            and bridge_result.get("derived_bytes") == BRIDGE_DERIVED_BYTES
            and bridge_result.get("candidate_original_modified") is False,
            "apply the exact first-party bridge once to this private phase")
    require(type(public_result) is dict
            and public_result.get("status") == "PASS"
            and public_result.get("phase") == phase
            and public_result.get("source_apply_count") == 1
            and public_result.get("derived_source_sha256")
            == PUBLIC_DERIVED_SHA256
            and public_result.get("derived_source_bytes")
            == PUBLIC_DERIVED_BYTES
            and public_result.get("canonical_candidate_modified") is False,
            "apply the corrected V2 public adapter exactly once to this phase")
    for path, expected_sha, expected_size, expected_raw, overlay in (
        (BRIDGE_PATH, BRIDGE_DERIVED_SHA256, BRIDGE_DERIVED_BYTES,
         state["bridge_bytes"], bridge_result),
        (PUBLIC_PATH, PUBLIC_DERIVED_SHA256, PUBLIC_DERIVED_BYTES,
         state["public_bytes"], public_result),
    ):
        observed, actual = kernel.authenticate_file(
            paths["source"] / path, expected=expected_sha,
            maximum=MAX_SOURCE_BYTES, exact_size=expected_size, capture=True)
        require(type(actual) is bytes and actual == expected_raw
                and stat.S_IMODE(os.lstat(paths["source"] / path).st_mode)
                == 0o600,
                "reauthenticate the exact complete exclusive private overlay")
        copies[path] = {
            "path": v9.sanitized(observed["path"], workdir, family),
            "sha256": observed["sha256"], "bytes": observed["size_bytes"],
            "device": observed["device"], "inode": observed["inode"],
            "exclusive_creation": True, "same_inode_readback_verified": True,
            "file_fsync_completed": True, "source_overlay": overlay,
        }
    require(set(copies) == expected,
            "close the exact seven-original, two-overlay first-party snapshot")
    for item in RUST_OWNERS:
        read_owner(item)
    _APPLIED.add((workdir, phase))
    return copies


def verify_reproduced_phases(v9: types.ModuleType, v7: types.ModuleType,
                             workdir: str, phases: list[dict[str, Any]],
                             steps: list[dict[str, Any]]) -> dict[str, Any]:
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases] == list(PHASES)
            and type(steps) is list and len(steps) == 2 * len(PROCESS_NAMES),
            "require two actually completed ordered first-party Rust phases")
    identities: set[tuple[int, int]] = set()
    expected_paths = {item.path for item in RUST_OWNERS}
    for phase_index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        require(type(owners) is dict and set(owners) == expected_paths,
                "require all nine independently identified phase source owners")
        for item in RUST_OWNERS:
            expected_sha, expected_bytes = expected_source_owner(item.path)
            observed = owners.get(item.path)
            require(type(observed) is dict
                    and observed.get("sha256") == expected_sha
                    and observed.get("bytes") == expected_bytes
                    and type(observed.get("device")) is int
                    and type(observed.get("inode")) is int
                    and (observed["device"], observed["inode"])
                    not in identities,
                    "reject omitted, stale, linked, or reused phase source")
            identities.add((observed["device"], observed["inode"]))
        for path in (BRIDGE_PATH, PUBLIC_PATH):
            applied = owners[path].get("source_overlay")
            require(type(applied) is dict and applied.get("status") == "PASS"
                    and applied.get("phase") == PHASES[phase_index]
                    and applied.get("source_apply_count") == 1,
                    "require exactly one genuine overlay per private phase")
            observed_digest = (applied.get("derived_sha256")
                               if path == BRIDGE_PATH
                               else applied.get("derived_source_sha256"))
            require(observed_digest == expected_source_owner(path)[0],
                    "reject the historical V1 adapter or substituted bridge")
    pids: set[int] = set()
    for index, process in enumerate(steps):
        require(type(process) is dict
                and process.get("name")
                == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in pids
                and process.get("exit_status") == 0,
                "require 28 distinct actually successful ordered processes")
        pids.add(process["pid"])
    outputs: dict[str, Any] = {}
    comparisons: dict[str, Any] = {}
    for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
        left = phases[0].get("native_outputs", {}).get(role)
        right = phases[1].get("native_outputs", {}).get(role)
        require(type(left) is dict and type(right) is dict
                and left.get("file_name") == right.get("file_name") == filename
                and left.get("sha256") == right.get("sha256")
                and left.get("size_bytes") == right.get("size_bytes")
                and left.get("path") != right.get("path")
                and (left.get("device"), left.get("inode"))
                != (right.get("device"), right.get("inode"))
                and left.get("audit") == right.get("audit"),
                "reject an irreproducible or borrowed native Rust output")
        first = v9._RAW_PHASE_ELF.get((workdir, PHASES[0], role))
        second = v9._RAW_PHASE_ELF.get((workdir, PHASES[1], role))
        require(type(first) is bytes and type(second) is bytes
                and digest(first) == left["sha256"]
                and digest(second) == right["sha256"] and first == second,
                "compare complete actual bytes from both independent phases")
        compared = v7.compare_owned_elf64(first, second)
        require(type(compared) is dict
                and compared.get("byte_identical") is True,
                "prove that both independently owned ELF outputs reproduce")
        comparisons[role] = compared
        outputs[role] = {"file_name": filename, "sha256": left["sha256"],
                         "size_bytes": left["size_bytes"],
                         "fresh_independent_inode_count": 2,
                         "audit": left["audit"]}
    for item in RUST_OWNERS:
        read_owner(item)
    return {"status": "PASS", "independent_fresh_phase_count": 2,
            "source_owners_per_phase": 9,
            "unchanged_source_owners_per_phase": 7,
            "bridge_overlay_count": 2, "corrected_public_overlay_count": 2,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "byte_identical": True, "unique_process_count": len(pids),
            "native_role_count": 2, "raw_elf_comparisons": comparisons,
            "native_outputs": outputs, "prebuilt_artifact_count": 0,
            "native_libraries_loaded": 0, "original_sources_modified": False}


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in value),
            "require one exact safe independently authorized V12 evidence label")
    return value


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(type(failed) is bool, "require a real, explicit build outcome")
    base = "native-source-build-v12-rust-" + checked_label(label)
    if failed:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def publish_report(kernel: types.ModuleType,
                   report: dict[str, Any]) -> dict[str, Any]:
    require(type(report) is dict and report.get("status") in ("PASS", "FAIL"),
            "publish only a genuinely executed and separately authorized build")
    label = checked_label(report.get("label"))
    archive_name, receipt_name = evidence_names(label,
                                                 report["status"] == "FAIL")
    directory = ROOT / EVIDENCE_PATH
    plain = canonical(report)
    require(0 < len(plain) <= MAX_REPORT_BYTES,
            "bound the actual complete corrected Rust build report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_REPORT_BYTES,
            "bound the deterministic single-member V12 evidence archive")
    published = kernel.write_fresh(directory / archive_name, archive,
                                   synchronize=True)
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "build_status": report["status"],
        "family": FAMILY, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": published["sha256"],
        "archive_bytes": published["bytes"],
        "archive_publication": published,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "historical_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "historical_authenticated_reference_count":
            CURRENT_HISTORY_REFERENCES,
        "new_actual_evidence_owner_count": 2,
        "repository_evidence_owner_count_after_publication":
            CURRENT_EVIDENCE_OWNERS + 2,
        "authenticated_history_reference_count_after_publication":
            CURRENT_HISTORY_REFERENCES + 2,
        "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
        "public_derived_sha256": PUBLIC_DERIVED_SHA256,
        "bridge_overlay_apply_count": report.get("bridge_overlay_apply_count", 0),
        "corrected_public_overlay_apply_count":
            report.get("corrected_public_overlay_apply_count", 0),
        "expected_actual_compiler_process_count": 2 * len(PROCESS_NAMES),
        "actual_compiler_process_count":
            report.get("actual_compiler_process_count", 0),
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt_raw = canonical(receipt)
    require(len(receipt_raw) <= MAX_SOURCE_BYTES,
            "bound the independently durable actual V12 build receipt")
    recorded = kernel.write_fresh(directory / receipt_name, receipt_raw,
                                  synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    return {"schema": SCHEMA + "-published-build",
            "status": report["status"], "family": FAMILY, "label": label,
            "archive_relative": EVIDENCE_PATH + "/" + archive_name,
            "archive_sha256": published["sha256"],
            "receipt_relative": EVIDENCE_PATH + "/" + receipt_name,
            "receipt_sha256": recorded["sha256"],
            "receipt_directory_fsync": receipt_sync,
            "failure_preserved": report["status"] == "FAIL",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False, "performance": "NOT MEASURED",
            "memory": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False}


def run_build(arguments: argparse.Namespace) -> dict[str, Any]:
    global _ACTIVE
    context, state = verify_context(arguments.source_sha256,
                                    arguments.protocol_sha256,
                                    arguments.contract_sha256)
    expected_pins = {item.path + "=" + item.sha256 for item in RUST_OWNERS}
    require(type(arguments.owned_source_sha256) is list
            and len(arguments.owned_source_sha256) == len(RUST_OWNERS)
            and set(arguments.owned_source_sha256) == expected_pins,
            "independently and explicitly pin all nine original Rust sources")
    require(arguments.bridge_derived_sha256 == BRIDGE_DERIVED_SHA256
            and arguments.bridge_derived_bytes == BRIDGE_DERIVED_BYTES
            and arguments.public_derived_sha256 == PUBLIC_DERIVED_SHA256
            and arguments.public_derived_bytes == PUBLIC_DERIVED_BYTES,
            "explicitly pin both exact independent corrected private overlays")
    label = checked_label(arguments.label)
    v9 = state["v9"]
    v7 = v9.load_frozen_module("_rebar_v12_frozen_actual_low_level_v7",
                               v9.V7_OWNERS["source"])
    require(v7.SCHEMA == "rebar-phase2-owned-native-source-build-v7",
            "load only the exactly pinned first-party V7 low-level kernel")
    kernel = v7.load_frozen_v4()
    require(_ACTIVE is None and not _APPLIED,
            "reject a reused, nested, or cross-family corrected V12 build")
    state["kernel"] = kernel
    _ACTIVE = state
    v9.install_v9_build_kernel(v7, kernel)
    kernel.copy_snapshot = copy_dual_snapshot
    for failed in (False, True):
        for name in evidence_names(label, failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE_PATH / name)
    workdir = tempfile.mkdtemp(prefix=ROOT_PREFIX, dir="/tmp")
    checked_workdir(workdir)
    steps: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []

    def make_report(status: str, *, reproduction: Any = None,
                    error: Exception | None = None) -> dict[str, Any]:
        report: dict[str, Any] = {
            "schema": SCHEMA + "-actual-corrected-dual-overlay-build",
            "version": VERSION, "status": status, "family": FAMILY,
            "label": label, "source_sha256": arguments.source_sha256,
            "protocol_sha256": arguments.protocol_sha256,
            "contract_sha256": arguments.contract_sha256,
            "frozen_context": context, "root_prefix": ROOT_PREFIX,
            "historical_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
            "historical_authenticated_reference_count":
                CURRENT_HISTORY_REFERENCES,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "historical_public_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "bridge_overlay_apply_count": len(_APPLIED),
            "corrected_public_overlay_apply_count": len(_APPLIED),
            "expected_actual_compiler_process_count": 2 * len(PROCESS_NAMES),
            "actual_compiler_process_count": len(steps),
            "phase_count": len(completed), "phases": completed,
            "compiler_processes": steps,
            "reproducibility": reproduction,
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False, "candidate_processes_started": 0,
            "candidate_imports": 0, "native_libraries_loaded": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "performance": "NOT MEASURED",
            "memory": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        if error is not None:
            report["error_type"] = type(error).__name__
            report["error_message"] = str(error)[:8192]
        return report

    try:
        v9.prepare_private_phases(kernel, workdir)
        for phase in PHASES:
            result = kernel.exact_build_phase(workdir, FAMILY, phase,
                                              state["originals"], steps)
            result["native_forensics"] = v9.record_native_forensics(
                v7, kernel, workdir, phase, result, steps)
            completed.append(result)
        reproduction = verify_reproduced_phases(v9, v7, workdir,
                                                 completed, steps)
        require(len(steps) == 2 * len(PROCESS_NAMES) and len(_APPLIED) == 2
                and reproduction.get("status") == "PASS"
                and reproduction.get("unique_process_count") == 28
                and reproduction.get("bridge_overlay_count") == 2
                and reproduction.get("corrected_public_overlay_count") == 2,
                "require two real corrected phases and 28 actual unique processes")
        return publish_report(kernel, make_report("PASS",
                                                   reproduction=reproduction))
    except Exception as error:
        for item in RUST_OWNERS:
            read_owner(item)
        return publish_report(kernel, make_report("FAIL", error=error))


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    option_names = [item for item in values if item.startswith("--")
                    and item != "--owned-source-sha256"]
    require(len(option_names) == len(set(option_names)),
            "reject repeated or ambiguous V12 source-build authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", "--render-contract",
                       dest="emit_contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    parser.add_argument("--owned-source-sha256", action="append")
    parser.add_argument("--bridge-derived-sha256")
    parser.add_argument("--bridge-derived-bytes", type=int)
    parser.add_argument("--public-derived-sha256")
    parser.add_argument("--public-derived-bytes", type=int)
    options = parser.parse_args(values)
    checked_sha256(options.source_sha256, "V12 source")
    checked_sha256(options.protocol_sha256, "V12 protocol")
    build_values = (options.label, options.owned_source_sha256,
                    options.bridge_derived_sha256,
                    options.bridge_derived_bytes,
                    options.public_derived_sha256,
                    options.public_derived_bytes)
    if options.emit_contract:
        require(options.contract_sha256 is None
                and all(value is None for value in build_values),
                "contract emission never authorizes a snapshot, build, or run")
    else:
        checked_sha256(options.contract_sha256, "V12 canonical contract")
        if options.build:
            checked_label(options.label)
            checked_sha256(options.bridge_derived_sha256,
                           "independent bridge-derived source")
            checked_sha256(options.public_derived_sha256,
                           "independent corrected public-derived source")
            require(type(options.owned_source_sha256) is list
                    and len(options.owned_source_sha256) == len(RUST_OWNERS)
                    and type(options.bridge_derived_bytes) is int
                    and type(options.public_derived_bytes) is int,
                    "require all independently pinned original and derived owners")
        else:
            require(all(value is None for value in build_values),
                    "source-only gates can never authorize a build or snapshot")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.emit_contract:
            with SourceOnlyWall() as wall:
                result = contract_document(options.source_sha256,
                                           options.protocol_sha256)
                require(all(count == 0 for count in wall.blocked.values()),
                        "contract emission attempted a real source-only effect")
        elif options.self_test:
            result = self_test(options.source_sha256,
                               options.protocol_sha256,
                               options.contract_sha256)
        elif options.verify_frozen_context:
            result, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256,
                                       options.contract_sha256)
        else:
            result = run_build(options)
        output = canonical(result)
        require(len(output) <= MAX_REPORT_BYTES,
                "reject an unbounded corrected Rust source-build result")
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()
        return 0 if result.get("status", "PASS") == "PASS" else 1
    except (GateError, OSError, ValueError, TypeError, UnicodeError,
            RecursionError, SyntaxError, OverflowError, KeyError,
            AttributeError) as error:
        sys.stderr.write("owned Rust flag source build v12 rejected: "
                         + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
