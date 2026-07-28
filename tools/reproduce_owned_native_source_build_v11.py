#!/usr/bin/env python3
"""Freeze the latest Rust build plan without losing the real Zig build."""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import ctypes
import gzip
import hashlib
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
import types
from typing import Any, Iterator, Mapping, Sequence

ROOT = Path("/home/dev-user/src/rebar")
SOURCE_PATH = "tools/reproduce_owned_native_source_build_v11.py"
PROTOCOL_PATH = "oracle/phase2/NATIVE-SOURCE-BUILD-V11.md"
CONTRACT_PATH = "oracle/phase2/native-source-build-v11.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-native-source-build-v11"
VERSION = 11
FAMILY = "rust"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
WORK_PREFIX = "rebar-phase2-native-build-v9-"
ROOT_PREFIX = WORK_PREFIX + "rust-"
PHASES = ("reference-a", "reference-b")
MAX_SOURCE = 16 * 1024 * 1024
MAX_ZIG_EXPANDED = 512 * 1024
MAX_REPORT = 16 * 1024 * 1024
BASE_EVIDENCE_OWNER_COUNT = 135
BASE_AUTHENTICATED_REFERENCE_COUNT = 140
NEW_ZIG_OWNER_COUNT = 2
CURRENT_EVIDENCE_OWNER_COUNT = 137
CURRENT_AUTHENTICATED_REFERENCE_COUNT = 142
BASE_SIGNED_EVIDENCE_PATH_COUNT = 138
CURRENT_SIGNED_EVIDENCE_PATH_COUNT = 140
CASE_COUNT = 31237
SUITE_COUNT = 13
PRIVATE_WAIVERS = 13
C_OWNER_COUNT = 30
C_WORKER_COUNT = 13
C_PASS_COUNT = 7325
C_MISMATCH_COUNT = 1262
RUST_MISMATCH_COUNT = 2042
RUST_PASS_COUNT = 7461
BRIDGE_DERIVED_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
BRIDGE_DERIVED_BYTES = 176118
PUBLIC_DERIVED_SHA256 = "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
PUBLIC_DERIVED_BYTES = 31464
V10_OWNERS = {
    "source": (
        "tools/reproduce_owned_native_source_build_v10.py",
        "e2e9163968aa8c07dfa2cd5d05451e580eab1a1641edc4c53fd804ba51840d7b",
        96363,
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V10.md",
        "1edd8ebf3705cd58d27b78b9ff14a751ae0efe4471f1eb2ad25895380448485a",
        4265,
    ),
    "contract": (
        "oracle/phase2/native-source-build-v10.json",
        "0ba4cf203f876cd9c75a5d76b88186e571c8963eba83f6ccecad3f03d662e7f4",
        9925,
    ),
}
V23_OWNERS = {
    "source": (
        "tools/render_candidate_current_overview_v23.py",
        "a7f90986e1020d4cccd0b7eac19779a68a5dac28a33a2a7b5776a5508c91b213",
        74868,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v23.inputs.json",
        "e203be81e2ebafa23bd91e41902dd1949fa2245cb8d818e76444982021bfba68",
        29567,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v23.json",
        "6368a2c900e2ed656830ba773bd454a603f547f3f21f9eabac3490140d687098",
        127100,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v23.svg",
        "853d3084beb85df634437f3e9198f85c3d28f455c82c94550ae98cb453e561a4",
        11462,
    ),
}
V24_OWNERS = {
    "source": (
        "tools/render_candidate_current_overview_v24.py",
        "a639a39a2b476777e47aecb6850617213491d99698b391a4f905dc1653f25b4e",
        80389,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v24.inputs.json",
        "9a01881fca3d090d0b0a95b392b73d2941b330a5acd5144ffaf6a865e5f0cc34",
        33092,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v24.json",
        "719a3dec863e5f7c78c1c2bc37f7ee06057f9de0ed9cefca74dee0c6dceeceac",
        135202,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v24.svg",
        "44f56757ca5c908412668c7679006dab288655ab0a419da59ac9265e7cb3aed1",
        12712,
    ),
}
ZIG_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz",
    "e4a1f369b647f588ac5b12585f7d0e30c4ee3409adc88f660081fb7a59a8df5c",
    48246,
)
ZIG_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-zig-phase2-v11-zig-scanner-publication-receipt.json",
    "d53766d0dad571f8b72288cece15fb1ad0892db32c3b3b6b512027db94ca4fcc",
    1683,
)
ZIG_EXPANDED_SHA256 = "943c46bda393159604d60efe17c597a2c3c20660e6f9e8b926295c8ad3127f68"
ZIG_EXPANDED_BYTES = 300582
ZIG_LABEL = "phase2-v11-zig-scanner"
ZIG_FROZEN_SOURCE_SHA256 = "b908f12d14fb8ebc5f17c62dfc00d48a1a5ee3717a3144aed437059e21c0f097"
ZIG_FROZEN_PROTOCOL_SHA256 = "15fd222876407be72d36c0b9cf2ce581d8b73a954358df192c2a083a08973539"
ZIG_FROZEN_CONTRACT_SHA256 = "92979e4bfacd6d23e7f54f4fdce7a7707cc54dba2512753029fdcd479150464c"
ZIG_FROZEN_OWNERS = {
    "source": (
        "tools/reproduce_owned_zig_scanner_source_build_v11.py",
        ZIG_FROZEN_SOURCE_SHA256,
        207444,
    ),
    "protocol": (
        "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md",
        ZIG_FROZEN_PROTOCOL_SHA256,
        6144,
    ),
    "contract": (
        "oracle/phase2/zig-scanner-source-build-v11.json",
        ZIG_FROZEN_CONTRACT_SHA256,
        44636,
    ),
}
ZIG_ENGINE_SHA256 = "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
ZIG_ENGINE_BYTES = 108888
ZIG_BRIDGE_SHA256 = "75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681"
ZIG_BRIDGE_BYTES = 133656
ZIG_PROCESS_NAMES = (
    "readelf_version",
    "gcc_version",
    "zig_version",
    "build_zig_engine",
    "build_zig_bridge",
    "engine_dynamic",
    "engine_symbols",
    "engine_sections",
    "engine_notes",
    "bridge_dynamic",
    "bridge_symbols",
    "bridge_sections",
    "bridge_notes",
)
RUST_PROCESS_NAMES = (
    "readelf_version",
    "gcc_version",
    "rustc_version",
    "cargo_version",
    "build_rust_engine",
    "build_rust_bridge",
    "engine_dynamic",
    "engine_symbols",
    "bridge_dynamic",
    "bridge_symbols",
    "engine_sections",
    "engine_notes",
    "bridge_sections",
    "bridge_notes",
)
RUST_FAILED_SUITES = (
    "public_types_v1",
    "substitution_v2",
    "shape_v2",
    "public_surface_v19",
    "subinterpreter_v2",
)
BOUNDARY = {
    "candidate_correctness": "NOT MEASURED",
    "qualified_candidate_count": 0,
    "candidate_imports": 0,
    "candidate_processes_started": 0,
    "reference_processes_started": 0,
    "compiler_processes_started": 0,
    "native_builds_started": 0,
    "native_libraries_loaded": 0,
    "native_activations": 0,
    "source_apply_count": 0,
    "workspace_mutations": 0,
    "network_requests": 0,
    "clock_samples": 0,
    "timing_trials_run": 0,
    "hidden_cases_read": 0,
    "benchmark_files_read": 0,
    "performance": "NOT MEASURED",
    "memory": "NOT MEASURED",
    "undefined_behavior": "NOT MEASURED",
    "holdout": "NOT OPENED",
    "winner_selected": False,
}


class BuildFreezeError(Exception):
    """A signed first-party build source or historical owner changed."""


class SourceOnlyError(BuildFreezeError):
    """A synthetic source-only control attempted an external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildFreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete authenticated owner bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise BuildFreezeError("reject noncanonical Rust V11 source evidence") from error


def checked_digest(value: Any, name: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require an exact independently pinned SHA-256: " + name,
    )
    return value


def checked_relative(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "reject an unsafe first-party owner path")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute()
        and str(parsed) == value
        and all(piece not in ("", ".", "..") for piece in parsed.parts)
        and all("\\" not in piece and "\x00" not in piece for piece in parsed.parts),
        "reject an escaped, ambiguous, or noncanonical first-party path",
    )
    return parsed.parts


def read_owned(
    relative: str,
    expected: str,
    expected_bytes: int | None = None,
    *,
    private: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    parts = checked_relative(relative)
    checked_digest(expected, relative)
    if expected_bytes is not None:
        require(
            type(expected_bytes) is int and 0 < expected_bytes <= MAX_SOURCE,
            "reject a changed or unbounded exact owner size",
        )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    folders: list[int] = []
    descriptor: int | None = None
    try:
        parent = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
        folders.append(parent)
        for piece in parts[:-1]:
            parent = os.open(
                piece,
                flags | getattr(os, "O_DIRECTORY", 0),
                dir_fd=parent,
            )
            folders.append(parent)
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        before = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_nlink == 1
            and 0 < before.st_size <= MAX_SOURCE
            and (before.st_dev, before.st_ino, before.st_size)
            == (visible.st_dev, visible.st_ino, visible.st_size),
            "reject a linked, replaced, or oversized owner: " + relative,
        )
        if expected_bytes is not None:
            require(before.st_size == expected_bytes,
                    "reject changed exact owner bytes: " + relative)
        if private:
            require(
                before.st_uid == os.geteuid()
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require the owner-only mode-0600 genuine published evidence",
            )
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(block) is bytes and bool(block),
                    "reject incomplete source evidence: " + relative)
            pieces.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject trailing source evidence: " + relative)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size, before.st_mode)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mode)
            and digest(raw) == expected,
            "reject a substituted complete first-party owner: " + relative,
        )
        return raw, {
            "path": relative,
            "sha256": expected,
            "bytes": len(raw),
            "device": after.st_dev,
            "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for folder in reversed(folders):
            os.close(folder)


def reject_constant(value: str) -> Any:
    raise BuildFreezeError("reject non-finite JSON source evidence: " + value)


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in items:
        require(key not in output, "reject duplicate signed JSON source keys")
        output[key] = value
    return output


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE,
            "reject an unbounded signed owner: " + label)
    try:
        result = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise BuildFreezeError("reject malformed complete source evidence: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "reject a substituted noncanonical evidence owner: " + label)
    return result


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_PATH),
        "use only isolated, bytecode-free, pinned CPython 3.14.6",
    )


def owner_document(owner: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def boundary() -> dict[str, Any]:
    return copy.deepcopy(BOUNDARY)


def checked_root(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded private Rust snapshot root")
    parsed = PurePosixPath(value)
    pieces = parsed.parts
    require(
        parsed.is_absolute()
        and str(parsed) == value
        and len(pieces) == 3
        and pieces[0] == "/"
        and pieces[1] == "tmp"
        and pieces[2].startswith(ROOT_PREFIX)
        and len(pieces[2]) > len(ROOT_PREFIX)
        and all(
            item.isascii() and (item.isalnum() or item in "-_")
            for item in pieces[2]
        ),
        "preserve the literal V9-root-compatible dual Rust source overlay",
    )
    return value


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "V11 Rust source")
    checked_digest(protocol_pin, "V11 Rust protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "phase": "RUST DUAL-OVERLAY SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "family": FAMILY,
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "runtime": {
            "implementation": "CPython",
            "version": "3.14.6",
            "path": PYTHON,
            "sha256": PYTHON_SHA256,
        },
        "oracle": {
            "suite_count": SUITE_COUNT,
            "case_execution_count": CASE_COUNT,
            "private_waiver_count": PRIVATE_WAIVERS,
        },
        "inherited_audited_v10": {
            "owners": {
                name: owner_document(owner)
                for name, owner in sorted(V10_OWNERS.items())
            },
            "source_family": FAMILY,
            "immutable_v9_private_root_prefix": ROOT_PREFIX,
            "phase_names": list(PHASES),
            "unchanged_sources_per_phase": 7,
            "bridge_overlays_per_phase": 1,
            "public_overlays_per_phase": 1,
            "complete_sources_per_phase": 9,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "bridge_derived_bytes": BRIDGE_DERIVED_BYTES,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "public_derived_bytes": PUBLIC_DERIVED_BYTES,
            "future_processes_per_phase": len(RUST_PROCESS_NAMES),
            "future_total_compiler_processes": 2 * len(RUST_PROCESS_NAMES),
            "cargo_required_flags": [
                "--release", "--locked", "--offline", "--frozen", "--target-dir"
            ],
            "external_dependency_count": 0,
            "network": "FORBIDDEN",
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "cross_family_engine": "FORBIDDEN",
            "candidate_execution": "FORBIDDEN",
        },
        "published_v23_base": {
            "owners": {
                name: owner_document(owner)
                for name, owner in sorted(V23_OWNERS.items())
            },
            "evidence_owner_count": BASE_EVIDENCE_OWNER_COUNT,
            "authenticated_reference_count": BASE_AUTHENTICATED_REFERENCE_COUNT,
            "direct_graph_signed_evidence_path_count": BASE_SIGNED_EVIDENCE_PATH_COUNT,
            "complete_c_campaign": {
                "status": "FAIL",
                "actual_evidence_owner_count": C_OWNER_COUNT,
                "actual_candidate_workers": C_WORKER_COUNT,
                "completed_suite_count": SUITE_COUNT,
                "observed_matching_case_count": CASE_COUNT,
                "verified_passing_case_count": C_PASS_COUNT,
                "semantic_mismatch_count": C_MISMATCH_COUNT,
                "infrastructure_failure_count": 0,
                "original_native_restored": True,
                "candidate_qualified": False,
            },
            "original_rust": {
                "status": "FAILED; NOT QUALIFIED",
                "semantic_mismatch_count": RUST_MISMATCH_COUNT,
                "verified_passing_case_count": RUST_PASS_COUNT,
                "failed_suite_ids": list(RUST_FAILED_SUITES),
                "candidate_qualified": False,
            },
        },
        "published_zig_v11": {
            "frozen_source_owners": {
                name: owner_document(owner)
                for name, owner in sorted(ZIG_FROZEN_OWNERS.items())
            },
            "archive": owner_document(ZIG_ARCHIVE),
            "receipt": owner_document(ZIG_RECEIPT),
            "archive_uncompressed_sha256": ZIG_EXPANDED_SHA256,
            "archive_uncompressed_bytes": ZIG_EXPANDED_BYTES,
            "maximum_uncompressed_bytes": MAX_ZIG_EXPANDED,
            "label": ZIG_LABEL,
            "family": "zig",
            "build_status": "PASS",
            "source_sha256": ZIG_FROZEN_SOURCE_SHA256,
            "protocol_sha256": ZIG_FROZEN_PROTOCOL_SHA256,
            "contract_sha256": ZIG_FROZEN_CONTRACT_SHA256,
            "actual_evidence_owner_count": NEW_ZIG_OWNER_COUNT,
            "actual_compiler_process_count": 2 * len(ZIG_PROCESS_NAMES),
            "actual_phase_count": len(PHASES),
            "actual_source_apply_count": len(PHASES),
            "reproducible_native_role_count": 2,
            "engine_sha256": ZIG_ENGINE_SHA256,
            "engine_bytes": ZIG_ENGINE_BYTES,
            "bridge_sha256": ZIG_BRIDGE_SHA256,
            "bridge_bytes": ZIG_BRIDGE_BYTES,
            "candidate_correctness": "NOT MEASURED",
        },
        "published_v24_current": {
            "owners": {
                name: owner_document(owner)
                for name, owner in sorted(V24_OWNERS.items())
            },
            "evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
            "authenticated_reference_count": CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "new_actual_zig_evidence_owner_count": NEW_ZIG_OWNER_COUNT,
            "actual_zig_process_count": 2 * len(ZIG_PROCESS_NAMES),
            "actual_c_worker_count": C_WORKER_COUNT,
            "actual_c_semantic_mismatch_count": C_MISMATCH_COUNT,
            "actual_c_verified_passing_case_count": C_PASS_COUNT,
            "actual_c_infrastructure_failure_count": 0,
            "graph_reproduced_from_pinned_snapshot": True,
        },
        "current_history": {
            "base_v23_evidence_owner_count": BASE_EVIDENCE_OWNER_COUNT,
            "new_actual_zig_evidence_owner_count": NEW_ZIG_OWNER_COUNT,
            "evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
            "base_v23_authenticated_reference_count": BASE_AUTHENTICATED_REFERENCE_COUNT,
            "new_actual_zig_authenticated_reference_count": NEW_ZIG_OWNER_COUNT,
            "authenticated_reference_count": CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "direct_signed_evidence_path_count": CURRENT_SIGNED_EVIDENCE_PATH_COUNT,
            "independently_authenticated_current_graph_reference_count": 2,
            "direct_authenticated_reference_path_count": CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "stale_v10_current_accounting": "FORBIDDEN",
            "prospective_v24_graph_probing": "FORBIDDEN",
        },
        "future_evidence": {
            "directory": EVIDENCE_PATH,
            "archive_prefix": "native-source-build-v11-rust-",
            "failure_suffix": "-failures",
            "archive_suffix": ".json.gz",
            "receipt_suffix": "-publication-receipt.json",
            "exclusive_creation": True,
            "archive_and_directory_fsync": True,
            "passing_build_does_not_qualify_candidate": True,
        },
        "phase_boundary": boundary(),
    }


def validate_contract(document: Any, source_pin: str, protocol_pin: str) -> None:
    require(
        type(document) is dict
        and canonical(document)
        == canonical(contract_document(source_pin, protocol_pin)),
        "reject changed V23 accounting, authentic Zig owners, or frozen Rust overlays",
    )


@contextlib.contextmanager
def source_only_wall() -> Iterator[dict[str, int]]:
    effects = {
        "blocked_reads": 0,
        "blocked_writes": 0,
        "blocked_processes": 0,
        "blocked_network": 0,
        "blocked_clocks": 0,
        "blocked_native_loads": 0,
        "blocked_candidate_imports": 0,
        "blocked_threads": 0,
        "blocked_snapshot_creation": 0,
    }
    originals: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def forbidden(*_arguments: Any, **_keywords: Any) -> Any:
            effects[category] += 1
            raise SourceOnlyError("source-only Rust V11 rejected " + category)

        originals.append((owner, name, original))
        setattr(owner, name, forbidden)

    previous_import = builtins.__import__

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name in ("re", "_sre", "regex", "_rust_bridge", "_rust_engine") or (
            name.startswith("candidates.") or name.startswith("rebar")
        ):
            effects["blocked_candidate_imports"] += 1
            raise SourceOnlyError("reject candidate or external regex import")
        return previous_import(name, *args, **kwargs)

    try:
        for owner, name in ((builtins, "open"), (io, "open")):
            install(owner, name, "blocked_reads")
        for name in ("open", "read", "stat", "lstat", "listdir", "scandir"):
            install(os, name, "blocked_reads")
        for name in (
            "write", "mkdir", "makedirs", "remove", "unlink",
            "rename", "replace", "fsync", "putenv", "unsetenv",
        ):
            install(os, name, "blocked_writes")
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, "blocked_processes")
        for name in ("socket", "create_connection"):
            install(socket, name, "blocked_network")
        for name in ("CDLL", "PyDLL"):
            install(ctypes, name, "blocked_native_loads")
        install(threading.Thread, "start", "blocked_threads")
        install(tempfile, "mkdtemp", "blocked_snapshot_creation")
        install(tempfile, "mkstemp", "blocked_snapshot_creation")
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns", "thread_time", "thread_time_ns", "sleep",
        ):
            install(time, name, "blocked_clocks")
        originals.append((builtins, "__import__", previous_import))
        builtins.__import__ = guarded_import
        yield effects
    finally:
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)


def expect_rejected(action: Any, label: str) -> int:
    try:
        action()
    except (
        BuildFreezeError, TypeError, ValueError, KeyError,
        IndexError, OSError, AttributeError, SyntaxError,
    ):
        return 1
    raise BuildFreezeError("accepted an unsafe V11 source-only control: " + label)


def synthetic_processes() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pid = 5000
    for phase in PHASES:
        for name in ZIG_PROCESS_NAMES:
            pid += 1
            rows.append(
                {"name": name, "phase": phase, "pid": pid, "returncode": 0}
            )
    return rows


def validate_processes(rows: Any) -> None:
    require(
        type(rows) is list and len(rows) == 2 * len(ZIG_PROCESS_NAMES),
        "require all 26 independently recorded actual Zig processes",
    )
    pids: set[int] = set()
    for index, row in enumerate(rows):
        require(
            type(row) is dict
            and row.get("phase") == PHASES[index // len(ZIG_PROCESS_NAMES)]
            and row.get("name") == ZIG_PROCESS_NAMES[index % len(ZIG_PROCESS_NAMES)]
            and type(row.get("pid")) is int
            and row["pid"] > 0
            and row["pid"] not in pids
            and row.get("returncode") == 0,
            "reject an omitted, reused, reordered, or failed actual Zig process",
        )
        pids.add(row["pid"])


def self_test() -> dict[str, Any]:
    source_pin = "a" * 64
    protocol_pin = "b" * 64
    frozen = contract_document(source_pin, protocol_pin)
    rows = synthetic_processes()
    rejected = 0
    with source_only_wall() as effects:
        validate_contract(frozen, source_pin, protocol_pin)
        validate_processes(rows)
        require(
            BASE_EVIDENCE_OWNER_COUNT + NEW_ZIG_OWNER_COUNT
            == CURRENT_EVIDENCE_OWNER_COUNT
            and BASE_AUTHENTICATED_REFERENCE_COUNT + NEW_ZIG_OWNER_COUNT
            == CURRENT_AUTHENTICATED_REFERENCE_COUNT
            and BASE_SIGNED_EVIDENCE_PATH_COUNT + NEW_ZIG_OWNER_COUNT
            == CURRENT_SIGNED_EVIDENCE_PATH_COUNT
            and CURRENT_SIGNED_EVIDENCE_PATH_COUNT + 2
            == CURRENT_AUTHENTICATED_REFERENCE_COUNT
            and len(RUST_PROCESS_NAMES) == 14
            and len(ZIG_PROCESS_NAMES) == 13
            and len(set(RUST_PROCESS_NAMES)) == 14
            and len(set(ZIG_PROCESS_NAMES)) == 13
            and 0 < ZIG_EXPANDED_BYTES <= MAX_ZIG_EXPANDED,
            "preserve exact current 137/142 history and both genuine process counts",
        )
        mutations = (
            (("version",), 10),
            (("family",), "zig"),
            (("oracle", "case_execution_count"), CASE_COUNT - 1),
            (("oracle", "suite_count"), SUITE_COUNT - 1),
            (("oracle", "private_waiver_count"), PRIVATE_WAIVERS + 1),
            (("inherited_audited_v10", "immutable_v9_private_root_prefix"),
             "rebar-phase2-native-build-v11-rust-"),
            (("inherited_audited_v10", "unchanged_sources_per_phase"), 8),
            (("inherited_audited_v10", "bridge_overlays_per_phase"), 0),
            (("inherited_audited_v10", "public_overlays_per_phase"), 0),
            (("inherited_audited_v10", "complete_sources_per_phase"), 8),
            (("inherited_audited_v10", "future_total_compiler_processes"), 26),
            (("inherited_audited_v10", "external_dependency_count"), 1),
            (("inherited_audited_v10", "network"), "ALLOWED"),
            (("inherited_audited_v10", "stdlib_regex_engine"), "ALLOWED"),
            (("inherited_audited_v10", "external_regex_engine"), "ALLOWED"),
            (("published_v23_base", "evidence_owner_count"), 137),
            (("published_v23_base", "authenticated_reference_count"), 142),
            (("published_v23_base", "complete_c_campaign",
              "actual_evidence_owner_count"), 29),
            (("published_v23_base", "complete_c_campaign",
              "actual_candidate_workers"), 12),
            (("published_v23_base", "complete_c_campaign",
              "verified_passing_case_count"), CASE_COUNT),
            (("published_v23_base", "complete_c_campaign",
              "semantic_mismatch_count"), 0),
            (("published_v23_base", "complete_c_campaign",
              "infrastructure_failure_count"), 1),
            (("published_v23_base", "original_rust",
              "semantic_mismatch_count"), 0),
            (("published_zig_v11", "actual_evidence_owner_count"), 1),
            (("published_zig_v11", "actual_compiler_process_count"), 25),
            (("published_zig_v11", "actual_source_apply_count"), 1),
            (("published_zig_v11", "reproducible_native_role_count"), 1),
            (("published_zig_v11", "archive_uncompressed_bytes"),
             MAX_ZIG_EXPANDED + 1),
            (("published_zig_v11", "engine_sha256"), "0" * 64),
            (("published_zig_v11", "bridge_sha256"), "0" * 64),
            (("published_zig_v11", "candidate_correctness"), "PASS"),
            (("published_v24_current", "evidence_owner_count"), 135),
            (("published_v24_current", "authenticated_reference_count"), 140),
            (("published_v24_current", "new_actual_zig_evidence_owner_count"), 0),
            (("published_v24_current", "actual_zig_process_count"), 25),
            (("published_v24_current", "actual_c_worker_count"), 12),
            (("published_v24_current", "actual_c_semantic_mismatch_count"), 0),
            (("published_v24_current", "graph_reproduced_from_pinned_snapshot"), False),
            (("current_history", "evidence_owner_count"), 135),
            (("current_history", "evidence_owner_count"), 138),
            (("current_history", "authenticated_reference_count"), 140),
            (("current_history", "authenticated_reference_count"), 141),
            (("current_history", "direct_signed_evidence_path_count"), 138),
            (("current_history", "direct_authenticated_reference_path_count"), 140),
            (("current_history", "stale_v10_current_accounting"), "ALLOWED"),
            (("current_history", "prospective_v24_graph_probing"), "ALLOWED"),
            (("phase_boundary", "clock_samples"), 1),
            (("phase_boundary", "hidden_cases_read"), 1),
            (("phase_boundary", "source_apply_count"), 1),
            (("phase_boundary", "compiler_processes_started"), 1),
            (("phase_boundary", "native_builds_started"), 1),
            (("phase_boundary", "winner_selected"), True),
        )
        for path, value in mutations:
            hostile = copy.deepcopy(frozen)
            location: Any = hostile
            for part in path[:-1]:
                location = location[part]
            location[path[-1]] = value
            rejected += expect_rejected(
                lambda item=hostile: validate_contract(item, source_pin, protocol_pin),
                ".".join(path),
            )
        process_mutations = (
            (0, "name", "build_external_regex"),
            (0, "phase", "reference-b"),
            (0, "pid", 0),
            (0, "returncode", 1),
            (13, "phase", "reference-a"),
            (25, "name", "read_holdout"),
            (25, "returncode", 1),
        )
        for position, key, value in process_mutations:
            hostile = copy.deepcopy(rows)
            hostile[position][key] = value
            rejected += expect_rejected(
                lambda item=hostile: validate_processes(item),
                "genuine process " + str(position) + "." + key,
            )
        repeated = copy.deepcopy(rows)
        repeated[1]["pid"] = repeated[0]["pid"]
        rejected += expect_rejected(
            lambda: validate_processes(repeated), "reused actual process identity",
        )
        for value in (
            "/tmp/rebar-phase2-native-build-v10-rust-x",
            "/tmp/rebar-phase2-native-build-v11-rust-x",
            "/tmp/rebar-phase2-native-build-v9-zig-x",
            "/tmp/" + ROOT_PREFIX,
            "/tmp/" + ROOT_PREFIX + "x/reference-a",
            "/tmp/" + ROOT_PREFIX + "../escape",
            str(ROOT),
            ROOT_PREFIX + "relative",
        ):
            rejected += expect_rejected(
                lambda item=value: checked_root(item), "unsafe private root",
            )
        for value in ("", "0" * 63, "0" * 65, "A" * 64, "z" * 64, None):
            rejected += expect_rejected(
                lambda item=value: checked_digest(item, "hostile"),
                "altered owner fingerprint",
            )
        for value in (
            b'{"x":1,"x":2}\n',
            b'{"x":NaN}\n',
            b"[]\n",
            b'{"x":1}',
        ):
            rejected += expect_rejected(
                lambda item=value: strict_json(item, "hostile source JSON"),
                "substituted signed JSON",
            )
        probes = (
            ("read", lambda: builtins.open("/tmp/rebar-rust-v11-forbidden", "rb")),
            ("read", lambda: io.open("/tmp/rebar-rust-v11-forbidden", "rb")),
            ("read", lambda: os.open("/tmp/rebar-rust-v11-forbidden", os.O_RDONLY)),
            ("write", lambda: os.write(1, b"forbidden")),
            ("write", lambda: os.mkdir("/tmp/rebar-rust-v11-forbidden")),
            ("process", lambda: subprocess.run(["cargo", "--version"])),
            ("network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("clock", lambda: time.perf_counter()),
            ("clock", lambda: time.time()),
            ("native", lambda: ctypes.CDLL("_rust_bridge.so")),
            ("candidate", lambda: builtins.__import__("candidates.rust_candidate")),
            ("stdlib regex", lambda: builtins.__import__("re")),
            ("snapshot", lambda: tempfile.mkdtemp(prefix=ROOT_PREFIX)),
            ("thread", lambda: threading.Thread().start()),
        )
        for name, probe in probes:
            rejected += expect_rejected(probe, "blocked " + name)
        blocked = dict(effects)
    require(rejected >= 75, "require complete hostile current-history source controls")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_source_controls": 3,
        "rejected_hostile_controls": rejected,
        "source_only_blocked_effects": blocked,
        "historical_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count": CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "published_v23_base_evidence_owner_count": BASE_EVIDENCE_OWNER_COUNT,
        "published_v23_base_reference_count": BASE_AUTHENTICATED_REFERENCE_COUNT,
        "new_actual_zig_evidence_owner_count": NEW_ZIG_OWNER_COUNT,
        "future_rust_compiler_process_count": 2 * len(RUST_PROCESS_NAMES),
        "historical_actual_zig_process_count": 2 * len(ZIG_PROCESS_NAMES),
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVERS,
        **boundary(),
    }


def load_v10() -> types.ModuleType:
    owner = V10_OWNERS["source"]
    raw, _ = read_owned(*owner)
    name = "_rebar_phase2_owned_v11_exact_frozen_rust_v10"
    require(name not in sys.modules,
            "reject substituted, imported, or repeated V10 native source kernel")
    try:
        tree = ast.parse(raw.decode("utf-8", "strict"), filename=owner[0])
        require(isinstance(tree, ast.Module), "require the entire frozen V10 source")
        module = types.ModuleType(name)
        module.__dict__["__file__"] = str(ROOT / owner[0])
        module.__dict__["__package__"] = None
        exec(compile(tree, str(ROOT / owner[0]), "exec"), module.__dict__)
    except (SyntaxError, UnicodeError, RecursionError, ValueError) as error:
        raise BuildFreezeError("reject the substituted original Rust V10 kernel") from error
    require(
        module.SCHEMA == "rebar-phase2-owned-native-source-build-v10"
        and module.VERSION == 10
        and module.SOURCE_PATH == V10_OWNERS["source"][0]
        and module.PROTOCOL_PATH == V10_OWNERS["protocol"][0]
        and module.CONTRACT_PATH == V10_OWNERS["contract"][0]
        and module.FAMILY == FAMILY
        and module.WORK_PREFIX == WORK_PREFIX
        and module.ROOT_PREFIX == ROOT_PREFIX
        and tuple(module.PHASES) == PHASES
        and tuple(module.PROCESS_NAMES) == RUST_PROCESS_NAMES
        and module.GRAPH_OWNER_COUNT == BASE_EVIDENCE_OWNER_COUNT
        and module.GRAPH_REFERENCE_COUNT == BASE_AUTHENTICATED_REFERENCE_COUNT
        and module.GRAPH_EVIDENCE_CLAIM_COUNT == BASE_SIGNED_EVIDENCE_PATH_COUNT
        and module.BRIDGE_DERIVED_SHA256 == BRIDGE_DERIVED_SHA256
        and module.BRIDGE_DERIVED_BYTES == BRIDGE_DERIVED_BYTES
        and module.PUBLIC_DERIVED_SHA256 == PUBLIC_DERIVED_SHA256
        and module.PUBLIC_DERIVED_BYTES == PUBLIC_DERIVED_BYTES
        and module.V23_OWNERS == V23_OWNERS,
        "preserve every independently audited V10 dual-overlay and V23 graph owner",
    )
    return module


def load_v24() -> types.ModuleType:
    owner = V24_OWNERS["source"]
    raw, _ = read_owned(*owner)
    name = "_rebar_phase2_owned_v11_exact_released_graph_v24"
    require(name not in sys.modules,
            "reject a changed or reused current V24 evidence renderer")
    try:
        tree = ast.parse(raw.decode("utf-8", "strict"), filename=owner[0])
        require(isinstance(tree, ast.Module), "require the complete current V24 source")
        renderer = types.ModuleType(name)
        renderer.__dict__["__file__"] = str(ROOT / owner[0])
        renderer.__dict__["__package__"] = None
        exec(compile(tree, str(ROOT / owner[0]), "exec"), renderer.__dict__)
    except (SyntaxError, UnicodeError, RecursionError, ValueError) as error:
        raise BuildFreezeError("reject a changed released V24 evidence graph") from error
    require(
        renderer.SCHEMA == "rebar-candidate-current-overview-v24"
        and renderer.SELF == V24_OWNERS["source"][0]
        and renderer.PREVIOUS_OWNERS == BASE_EVIDENCE_OWNER_COUNT
        and renderer.PREVIOUS_REFERENCES == BASE_AUTHENTICATED_REFERENCE_COUNT
        and renderer.NEW_OWNERS == NEW_ZIG_OWNER_COUNT
        and renderer.TOTAL_OWNERS == CURRENT_EVIDENCE_OWNER_COUNT
        and renderer.TOTAL_REFERENCES == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and tuple((item[0], item[1], item[2]) for item in renderer.SUITES)
        == (
            ("original_bounded_v5", 151, 0),
            ("public_v3", 864, 0),
            ("scanner_v3", 1024, 0),
            ("buffer_v3", 768, 0),
            ("managed_v1", 1024, 0),
            ("scanner_verbose_v1", 2854, 0),
            ("public_types_v1", 6912, 248),
            ("substitution_v2", 5120, 224),
            ("shape_v2", 10240, 672),
            ("public_surface_v19", 1376, 114),
            ("subinterpreter_v2", 128, 0),
            ("pep688_v4", 264, 4),
            ("threaded_pattern_v1", 512, 0),
        ),
        "require the exact released V24 denominator and actual 137/142 graph",
    )
    return renderer


def validate_zig_build(
    report: Any,
    receipt: Any,
    archive_owner: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(report) is dict and type(receipt) is dict,
            "require both complete independently signed Zig build documents")
    claimed = receipt.get("archive")
    require(
        receipt.get("schema")
        == "rebar-phase2-owned-zig-scanner-source-build-v11-durable-publication-receipt"
        and receipt.get("version") == 11
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == "zig"
        and receipt.get("label") == ZIG_LABEL
        and receipt.get("source_sha256") == ZIG_FROZEN_SOURCE_SHA256
        and receipt.get("protocol_sha256") == ZIG_FROZEN_PROTOCOL_SHA256
        and receipt.get("contract_sha256") == ZIG_FROZEN_CONTRACT_SHA256
        and receipt.get("actual_build_process_count") == 26
        and receipt.get("expected_build_process_count_only_after_success") == 26
        and receipt.get("actual_source_apply_count") == 2
        and receipt.get("current_evidence_owner_count_before_publication")
        == BASE_EVIDENCE_OWNER_COUNT
        and receipt.get("current_authenticated_reference_count_before_publication")
        == BASE_AUTHENTICATED_REFERENCE_COUNT
        and receipt.get("new_evidence_owner_count_after_receipt_publication")
        == NEW_ZIG_OWNER_COUNT
        and receipt.get("uncompressed_bytes") == ZIG_EXPANDED_BYTES
        and receipt.get("uncompressed_sha256") == ZIG_EXPANDED_SHA256
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("candidate_imports") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False
        and type(claimed) is dict
        and claimed.get("path") == archive_owner["path"]
        and claimed.get("sha256") == archive_owner["sha256"]
        and claimed.get("bytes") == archive_owner["bytes"]
        and claimed.get("device") == archive_owner["device"]
        and claimed.get("inode") == archive_owner["inode"]
        and claimed.get("mode") == "0600"
        and claimed.get("link_count") == 1
        and claimed.get("file_fsync") is True
        and claimed.get("directory_fsync") is True,
        "authenticate the actual same-inode durable Zig V11 archive and receipt",
    )
    require(
        report.get("schema") == "rebar-phase2-owned-zig-scanner-source-build-v11"
        and report.get("version") == 11
        and report.get("status") == "PASS"
        and report.get("family") == "zig"
        and report.get("label") == ZIG_LABEL
        and report.get("source_sha256") == ZIG_FROZEN_SOURCE_SHA256
        and report.get("protocol_sha256") == ZIG_FROZEN_PROTOCOL_SHA256
        and report.get("contract_sha256") == ZIG_FROZEN_CONTRACT_SHA256
        and report.get("current_evidence_owner_count") == BASE_EVIDENCE_OWNER_COUNT
        and report.get("current_authenticated_reference_count")
        == BASE_AUTHENTICATED_REFERENCE_COUNT
        and report.get("actual_build_process_count") == 26
        and report.get("actual_source_apply_count") == 2
        and report.get("candidate_correctness") == "NOT MEASURED"
        and report.get("candidate_imports") == 0
        and report.get("candidate_processes_started") == 0
        and report.get("native_libraries_loaded") == 0
        and report.get("network_requests") == 0
        and report.get("hidden_cases_read") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("performance") == "NOT MEASURED"
        and report.get("memory") == "NOT MEASURED"
        and report.get("holdout") == "NOT OPENED"
        and report.get("winner_selected") is False,
        "retain the complete genuine unactivated 26-process Zig build",
    )
    validate_processes(report.get("processes"))
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2,
            "require both actual independent Zig build phases")
    identities: dict[str, set[tuple[int, int]]] = {
        "engine": set(),
        "bridge": set(),
    }
    for index, phase in enumerate(phases):
        require(
            type(phase) is dict and phase.get("name") == PHASES[index],
            "reject a missing, repeated, or reordered actual Zig phase",
        )
        overlay = phase.get("overlay_application")
        require(
            type(overlay) is dict
            and overlay.get("schema")
            == "rebar-phase2-owned-zig-scanner-capture-source-repair-v1"
            and overlay.get("status") == "PASS"
            and overlay.get("phase") == PHASES[index]
            and overlay.get("source_apply_count") == 1,
            "preserve one genuine first-party Zig overlay in each actual phase",
        )
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                "preserve both actual independently built Zig native roles")
        for role, expected_sha, expected_bytes in (
            ("engine", ZIG_ENGINE_SHA256, ZIG_ENGINE_BYTES),
            ("bridge", ZIG_BRIDGE_SHA256, ZIG_BRIDGE_BYTES),
        ):
            item = outputs.get(role)
            require(type(item) is dict, "require an actual Zig role: " + role)
            native = item.get("owner")
            audit = item.get("independence_audit")
            require(
                type(native) is dict
                and native.get("sha256") == expected_sha
                and native.get("bytes") == expected_bytes
                and type(native.get("path")) is str
                and ("/" + PHASES[index] + "/native/") in native["path"]
                and type(native.get("device")) is int
                and type(native.get("inode")) is int
                and native.get("link_count") == 1
                and native.get("mode") == "0700"
                and (native["device"], native["inode"]) not in identities[role]
                and type(audit) is dict
                and audit.get("cross_family_engine_count") == 0
                and audit.get("external_regex_engine_count") == 0
                and audit.get("stdlib_regex_engine_count") == 0
                and audit.get("network_symbol_count") == 0
                and audit.get("native_loader_symbol_count") == 0,
                "reject a borrowed, delegated, or repeated Zig native owner: " + role,
            )
            identities[role].add((native["device"], native["inode"]))
    reproducibility = report.get("reproducibility")
    require(
        type(reproducibility) is dict
        and reproducibility.get("status") == "PASS"
        and reproducibility.get("independent_phase_count") == 2
        and reproducibility.get("byte_identical_native_role_count") == 2
        and reproducibility.get("compiler_process_count") == 26
        and reproducibility.get("source_apply_count") == 2,
        "require two genuine reproducible Zig engine and bridge outputs",
    )
    roles = reproducibility.get("roles")
    require(type(roles) is dict and set(roles) == {"engine", "bridge"},
            "retain both independently reproducible real native roles")
    for name, sha, size in (
        ("engine", ZIG_ENGINE_SHA256, ZIG_ENGINE_BYTES),
        ("bridge", ZIG_BRIDGE_SHA256, ZIG_BRIDGE_BYTES),
    ):
        role = roles.get(name)
        require(
            type(role) is dict
            and role.get("byte_identical") is True
            and role.get("phase_owner_count") == 2
            and role.get("sha256") == sha
            and role.get("bytes") == size
            and len(identities[name]) == 2,
            "retain two actual distinct byte-identical Zig owners: " + name,
        )
    differences = report.get("raw_elf_differences")
    require(
        type(differences) is dict
        and differences.get("schema")
        == "rebar-phase2-owned-zig-scanner-source-build-v11-all-phase-raw-elf-differences"
        and differences.get("independent_phase_count") == 2
        and differences.get("native_role_count") == 2
        and differences.get("all_native_artifacts_byte_identical") is True
        and differences.get("additional_compiler_or_inspector_processes") == 0
        and differences.get("comparison_completed_before_reproducibility_classification")
        is True,
        "preserve complete real Zig ELF reproducibility without extra processes",
    )
    return {
        "status": "PASS",
        "family": "zig",
        "label": ZIG_LABEL,
        "actual_evidence_owner_count": NEW_ZIG_OWNER_COUNT,
        "actual_build_process_count": 26,
        "actual_source_apply_count": 2,
        "independent_phase_count": 2,
        "byte_identical_native_role_count": 2,
        "engine_sha256": ZIG_ENGINE_SHA256,
        "bridge_sha256": ZIG_BRIDGE_SHA256,
        "candidate_correctness": "NOT MEASURED",
    }


def verify_context(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    for label, value in (
        ("source", source_pin),
        ("protocol", protocol_pin),
        ("contract", contract_pin),
    ):
        checked_digest(value, "Rust V11 " + label)
    current_owners: dict[str, dict[str, Any]] = {}
    for path, sha in (
        (SOURCE_PATH, source_pin),
        (PROTOCOL_PATH, protocol_pin),
        (CONTRACT_PATH, contract_pin),
    ):
        raw, owner = read_owned(path, sha)
        current_owners[path] = owner
        if path == CONTRACT_PATH:
            validate_contract(
                strict_json(raw, "exact Rust V11 machine contract"),
                source_pin,
                protocol_pin,
            )
    for owner in V10_OWNERS.values():
        _, current_owners[owner[0]] = read_owned(*owner)
    v10 = load_v10()
    base, state = v10.verify_context(
        V10_OWNERS["source"][1],
        V10_OWNERS["protocol"][1],
        V10_OWNERS["contract"][1],
    )
    require(
        type(base) is dict
        and base.get("schema")
        == "rebar-phase2-owned-native-source-build-v10-read-only-context"
        and base.get("status") == "PASS"
        and base.get("read_only") is True
        and base.get("family") == FAMILY
        and base.get("historical_evidence_owner_count") == BASE_EVIDENCE_OWNER_COUNT
        and base.get("historical_authenticated_reference_count")
        == BASE_AUTHENTICATED_REFERENCE_COUNT
        and base.get("direct_signed_graph_evidence_owner_count")
        == BASE_SIGNED_EVIDENCE_PATH_COUNT
        and base.get("direct_authenticated_reference_path_count")
        == BASE_AUTHENTICATED_REFERENCE_COUNT
        and base.get("independently_authenticated_current_graph_reference_count") == 2
        and base.get("suite_count") == SUITE_COUNT
        and base.get("case_execution_denominator") == CASE_COUNT
        and base.get("named_private_waiver_count") == PRIVATE_WAIVERS
        and base.get("rust_historical_semantic_mismatch_count") == RUST_MISMATCH_COUNT
        and base.get("rust_historical_verified_passing_case_count") == RUST_PASS_COUNT
        and base.get("rust_historical_failed_suite_ids") == list(RUST_FAILED_SUITES)
        and base.get("rust_original_source_owner_count") == 9
        and base.get("preserved_v9_root_prefix") == ROOT_PREFIX
        and base.get("future_phase_count") == 2
        and base.get("future_unchanged_sources_per_phase") == 7
        and base.get("future_bridge_overlays_per_phase") == 1
        and base.get("future_public_overlays_per_phase") == 1
        and base.get("future_complete_sources_per_phase") == 9
        and base.get("future_compiler_process_count") == 28
        and base.get("bridge_derived_source_sha256") == BRIDGE_DERIVED_SHA256
        and base.get("bridge_derived_source_bytes") == BRIDGE_DERIVED_BYTES
        and base.get("public_derived_source_sha256") == PUBLIC_DERIVED_SHA256
        and base.get("public_derived_source_bytes") == PUBLIC_DERIVED_BYTES
        and base.get("derived_sources_materialized") is False
        and base.get("candidate_correctness") == "NOT MEASURED"
        and base.get("qualified_candidate_count") == 0
        and base.get("source_apply_count") == 0
        and base.get("compiler_processes_started") == 0
        and base.get("native_builds_started") == 0
        and base.get("clock_samples") == 0
        and base.get("hidden_cases_read") == 0
        and base.get("holdout") == "NOT OPENED",
        "authenticate the full unchanged V10 dual-overlay V23 base, not stale history",
    )
    campaign = base.get("actual_c_campaign")
    package = base.get("rust_package")
    require(
        type(campaign) is dict
        and campaign.get("status") == "FAIL"
        and campaign.get("actual_evidence_owner_count") == C_OWNER_COUNT
        and campaign.get("actual_candidate_workers") == C_WORKER_COUNT
        and campaign.get("completed_suite_count") == SUITE_COUNT
        and campaign.get("observed_matching_case_count") == CASE_COUNT
        and campaign.get("verified_passing_case_count") == C_PASS_COUNT
        and campaign.get("semantic_mismatch_count") == C_MISMATCH_COUNT
        and campaign.get("infrastructure_failure_count") == 0
        and campaign.get("original_native_restored") is True
        and campaign.get("qualified") is False
        and type(package) is dict
        and package.get("status") == "PASS"
        and package.get("package_count") == 1
        and package.get("external_dependency_count") == 0
        and package.get("network_requests") == 0,
        "preserve all real C failures and the dependency-free owned Rust package",
    )
    graph_documents: dict[str, Any] = {}
    for name, owner in V24_OWNERS.items():
        raw, current_owners[owner[0]] = read_owned(*owner)
        graph_documents[name] = (
            raw
            if name in ("source", "svg")
            else strict_json(raw, "released current V24 " + name)
        )
    for owner in ZIG_FROZEN_OWNERS.values():
        _, current_owners[owner[0]] = read_owned(*owner)
    graph_inputs = graph_documents["inputs"]
    graph_summary = graph_documents["summary"]
    snapshot = graph_summary.get("snapshot")
    require(type(snapshot) is dict,
            "require the full authorized immutable version-24 snapshot")
    renderer = load_v24()
    renderer.validate_snapshot(snapshot)
    require(
        graph_inputs.get("schema") == "rebar-candidate-current-overview-v24-inputs"
        and graph_inputs.get("version") == 24
        and graph_inputs.get("repository_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and graph_inputs.get("all_digest_addressed_history_path_count")
        == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and graph_inputs.get("preserved_v23_repository_evidence_owner_count")
        == BASE_EVIDENCE_OWNER_COUNT
        and graph_inputs.get("preserved_v23_digest_addressed_history_path_count")
        == BASE_AUTHENTICATED_REFERENCE_COUNT
        and graph_inputs.get("new_zig_v11_build_repository_evidence_owner_count")
        == NEW_ZIG_OWNER_COUNT
        and graph_inputs.get("suite_count") == SUITE_COUNT
        and graph_inputs.get("full_case_denominator") == CASE_COUNT
        and graph_inputs.get("private_waiver_count") == PRIVATE_WAIVERS
        and graph_inputs.get("candidate_qualified_count") == 0
        and graph_inputs.get("performance") == "NOT MEASURED"
        and graph_inputs.get("memory") == "NOT MEASURED"
        and graph_inputs.get("final_holdout_opened") is False
        and graph_inputs.get("winner_selected") is False,
        "reject an outdated or unverified current 137-owner, 142-reference graph",
    )
    require(
        graph_summary.get("schema") == "rebar-candidate-current-overview-v24-summary"
        and graph_summary.get("status") == "PASS"
        and graph_summary.get("repository_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and graph_summary.get("authenticated_digest_addressed_history_paths")
        == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and graph_summary.get("preserved_v23_repository_evidence_owner_count")
        == BASE_EVIDENCE_OWNER_COUNT
        and graph_summary.get("preserved_v23_authenticated_reference_path_count")
        == BASE_AUTHENTICATED_REFERENCE_COUNT
        and graph_summary.get("new_zig_v11_build_repository_evidence_owner_count")
        == NEW_ZIG_OWNER_COUNT
        and graph_summary.get("zig_scanner_repaired_build_status") == "PASS"
        and graph_summary.get("zig_scanner_repaired_build_process_count") == 26
        and graph_summary.get("zig_scanner_repaired_source_apply_count") == 2
        and graph_summary.get("zig_scanner_repaired_reproducibility") == "PASS"
        and graph_summary.get("zig_scanner_repaired_matching_test_status")
        == "NOT MEASURED"
        and graph_summary.get("zig_scanner_repaired_candidate_worker_count") == 0
        and graph_summary.get("zig_scanner_repaired_candidate_qualified") is False
        and graph_summary.get("c_repaired_candidate_worker_count") == C_WORKER_COUNT
        and graph_summary.get("c_repaired_completed_suite_count") == SUITE_COUNT
        and graph_summary.get("c_repaired_verified_passing_case_count") == C_PASS_COUNT
        and graph_summary.get("c_repaired_semantic_mismatch_count") == C_MISMATCH_COUNT
        and graph_summary.get("c_repaired_infrastructure_failure_count") == 0
        and graph_summary.get("qualified_candidate_count") == 0
        and graph_summary.get("performance") == "NOT MEASURED"
        and graph_summary.get("memory") == "NOT MEASURED"
        and graph_summary.get("final_holdout_opened") is False
        and graph_summary.get("winner_selected") is False,
        "preserve every real Zig build, C mismatch and current published graph",
    )
    for name in ("source", "inputs", "svg"):
        item = graph_summary.get(name)
        expected = V24_OWNERS[name]
        require(
            type(item) is dict
            and item.get("path") == expected[0]
            and item.get("sha256") == expected[1],
            "reject a substituted current version-24 graph owner: " + name,
        )
    for document in (
        graph_inputs.get("previous_overview"),
        graph_summary.get("previous_overview"),
    ):
        require(type(document) is dict,
                "retain all four independently signed V23 graph owners")
        for name, expected in V23_OWNERS.items():
            item = document.get(name)
            require(
                type(item) is dict
                and item.get("path") == expected[0]
                and item.get("sha256") == expected[1]
                and item.get("bytes") == expected[2],
                "reject changed signed V23 graph history: " + name,
            )
    require(
        graph_documents["svg"]
        == renderer.make_svg(
            snapshot,
            V24_OWNERS["source"][1],
            V24_OWNERS["inputs"][1],
        ),
        "independently reproduce the exact complete current V24 chart",
    )
    graph_zig = snapshot.get("zig_v11_scanner_repaired_source_build")
    require(
        type(graph_zig) is dict
        and graph_zig == graph_inputs.get("current_repaired_zig_source_build")
        and graph_zig.get("schema")
        == "rebar-candidate-current-overview-v24-authenticated-zig-v11-source-build"
        and graph_zig.get("status") == "PASS"
        and graph_zig.get("build_status") == "PASS"
        and graph_zig.get("family") == "zig"
        and graph_zig.get("label") == ZIG_LABEL
        and graph_zig.get("archive") == owner_document(ZIG_ARCHIVE)
        and graph_zig.get("receipt") == owner_document(ZIG_RECEIPT)
        and graph_zig.get("uncompressed_sha256") == ZIG_EXPANDED_SHA256
        and graph_zig.get("uncompressed_bytes") == ZIG_EXPANDED_BYTES
        and graph_zig.get("actual_build_process_count") == 26
        and graph_zig.get("actual_source_apply_count") == 2
        and graph_zig.get("independent_phase_count") == 2
        and graph_zig.get("reproducibility") == "PASS"
        and graph_zig.get("byte_identical_native_role_count") == 2
        and graph_zig.get("historical_zig_semantic_mismatch_count") == 1764
        and graph_zig.get("historical_v23_evidence_owner_count")
        == BASE_EVIDENCE_OWNER_COUNT
        and graph_zig.get("historical_v23_authenticated_reference_count")
        == BASE_AUTHENTICATED_REFERENCE_COUNT
        and graph_zig.get("new_repository_evidence_owner_count")
        == NEW_ZIG_OWNER_COUNT
        and graph_zig.get("original_candidate_sources_modified") is False
        and graph_zig.get("external_regex_engine_count") == 0
        and graph_zig.get("stdlib_regex_engine_count") == 0
        and graph_zig.get("cross_family_engine_count") == 0
        and graph_zig.get("matching_test_status") == "NOT MEASURED"
        and graph_zig.get("actual_candidate_workers") == 0
        and graph_zig.get("candidate_qualified") is False
        and graph_zig.get("holdout") == "NOT OPENED",
        "bind the real Zig evidence directly to the current published graph",
    )
    for name, expected in ZIG_FROZEN_OWNERS.items():
        require(
            graph_zig.get(name) == owner_document(expected),
            "reject a forged committed Zig source owner: " + name,
        )
    graph_c = graph_inputs.get("current_complete_c_campaign")
    require(
        type(graph_c) is dict
        and graph_c == snapshot.get("c_v10_repaired_original_campaign")
        and graph_c.get("status") == "FAIL"
        and graph_c.get("actual_candidate_workers") == C_WORKER_COUNT
        and graph_c.get("completed_suite_count") == SUITE_COUNT
        and graph_c.get("verified_passing_case_count") == C_PASS_COUNT
        and graph_c.get("semantic_mismatch_count") == C_MISMATCH_COUNT
        and graph_c.get("infrastructure_failure_count") == 0
        and graph_c.get("new_repository_evidence_owner_count") == C_OWNER_COUNT
        and graph_c.get("original_canonical_native_restored") is True,
        "preserve the actual all-suite C campaign in the current V24 graph",
    )
    archive_raw, archive_owner = read_owned(*ZIG_ARCHIVE, private=True)
    receipt_raw, receipt_owner = read_owned(*ZIG_RECEIPT, private=True)
    require(
        (archive_owner["device"], archive_owner["inode"])
        != (receipt_owner["device"], receipt_owner["inode"]),
        "require two genuinely distinct independently published Zig evidence owners",
    )
    receipt = strict_json(receipt_raw, "complete real Zig V11 durable receipt")
    require(
        receipt.get("uncompressed_bytes") == ZIG_EXPANDED_BYTES
        and 0 < ZIG_EXPANDED_BYTES <= MAX_ZIG_EXPANDED
        and receipt.get("uncompressed_sha256") == ZIG_EXPANDED_SHA256,
        "bound and independently pin the complete actual Zig build report",
    )
    try:
        expanded = gzip.decompress(archive_raw)
    except (OSError, EOFError, ValueError) as error:
        raise BuildFreezeError("reject a damaged real Zig native-build archive") from error
    require(
        len(expanded) == ZIG_EXPANDED_BYTES
        and digest(expanded) == ZIG_EXPANDED_SHA256,
        "authenticate all 300,582 real bytes of the successful Zig build",
    )
    report = strict_json(expanded, "complete published actual Zig build")
    zig = validate_zig_build(report, receipt, archive_owner)
    current_owners[ZIG_ARCHIVE[0]] = archive_owner
    current_owners[ZIG_RECEIPT[0]] = receipt_owner
    require(
        BASE_EVIDENCE_OWNER_COUNT + len((archive_owner, receipt_owner))
        == CURRENT_EVIDENCE_OWNER_COUNT
        and BASE_AUTHENTICATED_REFERENCE_COUNT
        + len((archive_owner, receipt_owner))
        == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and BASE_SIGNED_EVIDENCE_PATH_COUNT
        + len((archive_owner, receipt_owner))
        == CURRENT_SIGNED_EVIDENCE_PATH_COUNT
        and CURRENT_SIGNED_EVIDENCE_PATH_COUNT + 2
        == CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "reject stale V10 counters or altered 137-owner, 142-reference current history",
    )
    result = {
        "schema": SCHEMA + "-read-only-context",
        "version": VERSION,
        "status": "PASS",
        "read_only": True,
        "family": FAMILY,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVERS,
        "historical_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "published_v23_base_evidence_owner_count": BASE_EVIDENCE_OWNER_COUNT,
        "published_v23_base_reference_count": BASE_AUTHENTICATED_REFERENCE_COUNT,
        "published_v24_graph_owner_count": len(V24_OWNERS),
        "published_v24_graph_reproduced": True,
        "direct_signed_graph_and_zig_evidence_owner_count":
            CURRENT_SIGNED_EVIDENCE_PATH_COUNT,
        "direct_authenticated_reference_path_count":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "independently_authenticated_current_graph_reference_count": 2,
        "new_actual_zig_evidence_owner_count": NEW_ZIG_OWNER_COUNT,
        "actual_zig_build": zig,
        "actual_c_campaign": campaign,
        "rust_historical_semantic_mismatch_count": RUST_MISMATCH_COUNT,
        "rust_historical_verified_passing_case_count": RUST_PASS_COUNT,
        "rust_historical_failed_suite_ids": list(RUST_FAILED_SUITES),
        "rust_original_source_owner_count": 9,
        "rust_package": package,
        "preserved_v9_root_prefix": ROOT_PREFIX,
        "future_phase_count": 2,
        "future_unchanged_sources_per_phase": 7,
        "future_bridge_overlays_per_phase": 1,
        "future_public_overlays_per_phase": 1,
        "future_complete_sources_per_phase": 9,
        "bridge_derived_source_sha256": BRIDGE_DERIVED_SHA256,
        "bridge_derived_source_bytes": BRIDGE_DERIVED_BYTES,
        "public_derived_source_sha256": PUBLIC_DERIVED_SHA256,
        "public_derived_source_bytes": PUBLIC_DERIVED_BYTES,
        "derived_sources_materialized": False,
        "future_compiler_process_count": 2 * len(RUST_PROCESS_NAMES),
        "authenticated_owner_count": base["authenticated_owner_count"] + 12,
        **boundary(),
    }
    return result, {
        "v10": v10,
        "v10_state": state,
    }


def checked_label(value: Any) -> str:
    require(
        type(value) is str
        and 0 < len(value) <= 48
        and all(item.isascii() and (item.isalnum() or item in "-_") for item in value),
        "require one safe, explicit, independently owned Rust build label",
    )
    return value


def evidence_names(label: str, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "select one genuine Rust build status")
    base = "native-source-build-v11-rust-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def publish_report(kernel: types.ModuleType, report: dict[str, Any]) -> dict[str, Any]:
    require(type(report) is dict and report.get("status") in ("PASS", "FAIL"),
            "publish only an honest separately authorized Rust build result")
    label = checked_label(report.get("label"))
    archive_name, receipt_name = evidence_names(label, report["status"] == "FAIL")
    directory = ROOT / EVIDENCE_PATH
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT, "bound the complete genuine Rust build report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_REPORT, "bound the actual Rust evidence archive")
    publication = kernel.write_fresh(
        directory / archive_name, archive, synchronize=True,
    )
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS",
        "build_status": report["status"],
        "family": FAMILY,
        "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": publication["sha256"],
        "archive_bytes": publication["bytes"],
        "archive_publication": publication,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "historical_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
        "public_derived_sha256": PUBLIC_DERIVED_SHA256,
        "bridge_overlay_apply_count": report.get("bridge_overlay_apply_count", 0),
        "public_overlay_apply_count": report.get("public_overlay_apply_count", 0),
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": report.get("actual_compiler_process_count", 0),
        "candidate_correctness": "NOT MEASURED",
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    receipt_raw = canonical(receipt)
    require(len(receipt_raw) <= MAX_SOURCE, "bound the authentic Rust build receipt")
    recorded = kernel.write_fresh(
        directory / receipt_name, receipt_raw, synchronize=True,
    )
    receipt_sync = kernel.fsync_directory(directory)
    return {
        "schema": SCHEMA + "-published-build",
        "status": report["status"],
        "family": FAMILY,
        "label": label,
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": publication["sha256"],
        "receipt_relative": EVIDENCE_PATH + "/" + receipt_name,
        "receipt_sha256": recorded["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": report["status"] == "FAIL",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def run_build(arguments: argparse.Namespace) -> dict[str, Any]:
    context, loaded = verify_context(
        arguments.source_sha256,
        arguments.protocol_sha256,
        arguments.contract_sha256,
    )
    v10 = loaded["v10"]
    state = loaded["v10_state"]
    expected = {
        path + "=" + sha
        for path, (sha, _size) in v10.RUST_OWNERS.items()
    }
    require(
        type(arguments.owned_source_sha256) is list
        and len(arguments.owned_source_sha256) == 9
        and set(arguments.owned_source_sha256) == expected,
        "explicitly pin all nine unchanged first-party Rust sources",
    )
    label = checked_label(arguments.label)
    v9 = state["v9"]
    v7 = v9.load_frozen_module(
        "_rebar_phase2_exact_frozen_v11_rust_build_v7",
        v9.V7_OWNERS["source"],
    )
    kernel = v7.load_frozen_v4()
    require(
        v10._ACTIVE is None and not v10._APPLIED,
        "reject a reused, nested, or cross-family Rust build state",
    )
    state["kernel"] = kernel
    v10._ACTIVE = state
    v9.install_v9_build_kernel(v7, kernel)
    kernel.copy_snapshot = v10.copy_dual_snapshot
    for failed in (False, True):
        for name in evidence_names(label, failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE_PATH / name)
    workdir = tempfile.mkdtemp(prefix=ROOT_PREFIX, dir="/tmp")
    checked_root(workdir)
    steps: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []
    try:
        v9.prepare_private_phases(kernel, workdir)
        for phase in PHASES:
            result = kernel.exact_build_phase(
                workdir,
                FAMILY,
                phase,
                state["originals"],
                steps,
            )
            result["native_forensics"] = v9.record_native_forensics(
                v7,
                kernel,
                workdir,
                phase,
                result,
                steps,
            )
            completed.append(result)
        reproduction = v10.verify_reproduced_phases(
            v9, v7, workdir, completed, steps,
        )
        require(
            len(steps) == 28
            and len(v10._APPLIED) == 2
            and reproduction.get("status") == "PASS"
            and reproduction.get("unique_process_count") == 28
            and reproduction.get("bridge_overlay_count") == 2
            and reproduction.get("public_overlay_count") == 2,
            "require both real dual-overlay phases and 28 actual native processes",
        )
        report = {
            "schema": SCHEMA + "-actual-dual-overlay-build",
            "version": VERSION,
            "status": "PASS",
            "family": FAMILY,
            "label": label,
            "source_sha256": arguments.source_sha256,
            "protocol_sha256": arguments.protocol_sha256,
            "contract_sha256": arguments.contract_sha256,
            "frozen_context": context,
            "root_prefix": ROOT_PREFIX,
            "historical_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
            "historical_authenticated_reference_count":
                CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "bridge_overlay_apply_count": len(v10._APPLIED),
            "public_overlay_apply_count": len(v10._APPLIED),
            "expected_actual_compiler_process_count": 28,
            "actual_compiler_process_count": len(steps),
            "phase_count": len(completed),
            "phases": completed,
            "compiler_processes": steps,
            "reproducibility": reproduction,
            "candidate_correctness": "NOT MEASURED",
            "candidate_processes_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        return publish_report(kernel, report)
    except Exception as error:
        for path, (sha, count) in sorted(v10.RUST_OWNERS.items()):
            v10.read_owned(path, sha, count)
        report = {
            "schema": SCHEMA + "-actual-dual-overlay-build",
            "version": VERSION,
            "status": "FAIL",
            "family": FAMILY,
            "label": label,
            "source_sha256": arguments.source_sha256,
            "protocol_sha256": arguments.protocol_sha256,
            "contract_sha256": arguments.contract_sha256,
            "frozen_context": context,
            "root_prefix": ROOT_PREFIX,
            "historical_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
            "historical_authenticated_reference_count":
                CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "bridge_overlay_apply_count": sum(
                (workdir, phase) in v10._APPLIED for phase in PHASES
            ),
            "public_overlay_apply_count": sum(
                (workdir, phase) in v10._APPLIED for phase in PHASES
            ),
            "expected_actual_compiler_process_count": 28,
            "actual_compiler_process_count": len(steps),
            "phase_count": len(completed),
            "phases": completed,
            "compiler_processes": steps,
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            "candidate_correctness": "NOT MEASURED",
            "candidate_processes_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        return publish_report(kernel, report)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", action="store_true")
    modes.add_argument("--verify-context", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    parser.add_argument("--owned-source-sha256", action="append")
    result = parser.parse_args(arguments)
    if result.self_test:
        require(
            all(
                getattr(result, name) is None
                for name in (
                    "source_sha256", "protocol_sha256", "contract_sha256",
                    "label", "owned_source_sha256",
                )
            ),
            "synthetic source tests cannot authorize real files or a native build",
        )
        return result
    checked_digest(result.source_sha256, "V11 Rust source")
    checked_digest(result.protocol_sha256, "V11 Rust protocol")
    if result.emit_contract:
        require(
            result.contract_sha256 is None
            and result.label is None
            and result.owned_source_sha256 is None,
            "pure contract emission cannot apply, build, or read candidate cases",
        )
        return result
    checked_digest(result.contract_sha256, "V11 Rust contract")
    if result.verify_context:
        require(
            result.label is None and result.owned_source_sha256 is None,
            "read-only verification cannot authorize a real native Rust build",
        )
        return result
    checked_label(result.label)
    require(
        type(result.owned_source_sha256) is list
        and len(result.owned_source_sha256) == 9,
        "a genuine Rust build requires nine explicitly pinned source owners",
    )
    return result


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = self_test()
        elif options.emit_contract:
            with source_only_wall() as effects:
                result = contract_document(
                    options.source_sha256,
                    options.protocol_sha256,
                )
                require(
                    all(value == 0 for value in effects.values()),
                    "pure V11 contract generation attempted an external effect",
                )
        elif options.verify_context:
            result, _ = verify_context(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
        else:
            result = run_build(options)
        raw = canonical(result)
        require(len(raw) <= MAX_REPORT, "reject an unbounded Rust V11 gate result")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status", "PASS") == "PASS" else 1
    except BaseException as error:
        result = {
            "schema": SCHEMA + "-gate-failure",
            "version": VERSION,
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            **boundary(),
        }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
