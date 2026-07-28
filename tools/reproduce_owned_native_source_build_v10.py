#!/usr/bin/env python3
"""Freeze a two-overlay, independently built, first-party Rust candidate."""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import ctypes
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
import tomllib
import types
from typing import Any, Iterator, Mapping, Sequence

ROOT = Path("/home/dev-user/src/rebar")
SOURCE_PATH = "tools/reproduce_owned_native_source_build_v10.py"
PROTOCOL_PATH = "oracle/phase2/NATIVE-SOURCE-BUILD-V10.md"
CONTRACT_PATH = "oracle/phase2/native-source-build-v10.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-native-source-build-v10"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
FAMILY = "rust"
VERSION = 10
WORK_PREFIX = "rebar-phase2-native-build-v9-"
ROOT_PREFIX = WORK_PREFIX + "rust-"
PHASES = ("reference-a", "reference-b")
MAX_SOURCE = 16 * 1024 * 1024
MAX_COMPRESSED = 16 * 1024 * 1024
MAX_EXPANDED = 256 * 1024
MAX_REPORT = 16 * 1024 * 1024
SUITE_COUNT = 13
CASE_COUNT = 31237
PRIVATE_WAIVERS = 13
GRAPH_OWNER_COUNT = 135
GRAPH_REFERENCE_COUNT = 140
GRAPH_EVIDENCE_CLAIM_COUNT = 138
C_OWNER_COUNT = 30
C_WORKER_COUNT = 13
C_PASS_COUNT = 7325
C_MISMATCH_COUNT = 1262
C_LABEL = "phase2-v10-live-original-p0"
RUST_MISMATCH_COUNT = 2042
RUST_PASS_COUNT = 7461
BRIDGE_DERIVED_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
BRIDGE_DERIVED_BYTES = 176118
PUBLIC_DERIVED_SHA256 = "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
PUBLIC_DERIVED_BYTES = 31464
BRIDGE_PATH = "candidates/rust/py_bridge.c"
PUBLIC_PATH = "candidates/rust_candidate.py"
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
PINNED_RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
PINNED_CARGO = RUST_TOOLCHAIN + "/bin/cargo"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
ENGINE_NAME = "_rust_engine.so"
BRIDGE_NAME = "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
ORIGINAL_NATIVE = (
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd",
    149976,
)
GOAL_OWNER = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
)
PHASE_ONE = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
PHASE_ONE_PROTOCOL = (
    "oracle/phase1/P0-COMPLETENESS-V1.md",
    "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
    10392,
)
V9_OWNERS = {
    "source": (
        "tools/reproduce_owned_native_source_build_v9.py",
        "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f",
        81124,
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V9.md",
        "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc",
        4960,
    ),
    "contract": (
        "oracle/phase2/native-source-build-v9.json",
        "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da",
        9134,
    ),
}
BRIDGE_OWNERS = {
    "source": (
        "tools/apply_owned_rust_source_repair_v1.py",
        "1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851",
        59388,
    ),
    "protocol": (
        "oracle/phase2/RUST-SOURCE-REPAIR-V1.md",
        "df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b",
        5496,
    ),
    "contract": (
        "oracle/phase2/rust-source-repair-v1.json",
        "1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b",
        8306,
    ),
}
PUBLIC_OWNERS = {
    "source": (
        "tools/apply_owned_rust_public_contract_source_repair_v1.py",
        "ac98ad24c6a4962fb38535cbaa470ae5cd4983643e7e8962e9fc9a1b6a0e12a0",
        91232,
    ),
    "protocol": (
        "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V1.md",
        "a297cbccfe4d4a2a321e7f8fe518662f451fd84f90e17bf86c62cf579875955f",
        4027,
    ),
    "contract": (
        "oracle/phase2/rust-public-contract-source-repair-v1.json",
        "a3b4670c3e321cefd6a1ec65ba80b9aa1a06534a73e30ba56654cc75f6f11431",
        13450,
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
V22_OWNERS = {
    "source": (
        "tools/render_candidate_current_overview_v22.py",
        "a07bf3d6e6d8dc28c206218f14e2ed6f6089e31c66dbab2961979409b30fc955",
        59289,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v22.inputs.json",
        "6843292a1f1d62d4635be4737a1565554cee8ec9f359506bc95a94cb80af7b58",
        16526,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v22.json",
        "5dc6229696e5aba546c38e3d1d1bd4ce422a892a57ec562ccea8cb75cbbfb21f",
        100772,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v22.svg",
        "7314d28286b90ee8161c02fee175904ba2ddd2c67dd78163f93b04fef2d0a26c",
        7898,
    ),
}
RUST_OWNERS = {
    "candidates/rust/Cargo.lock": (
        "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
        167,
    ),
    "candidates/rust/Cargo.toml": (
        "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
        225,
    ),
    BRIDGE_PATH: (
        "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        175676,
    ),
    "candidates/rust/src/lib.rs": (
        "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d",
        177967,
    ),
    "candidates/rust/src/newline.rs": (
        "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
        14416,
    ),
    "candidates/rust/src/search.rs": (
        "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
        14773,
    ),
    "candidates/rust/src/stack.rs": (
        "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
        7269,
    ),
    "candidates/rust/src/unicode_tables.rs": (
        "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
        471989,
    ),
    PUBLIC_PATH: (
        "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        31151,
    ),
}
C_SUITES = (
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
)
RUST_FAILED_SUITES = (
    "public_types_v1",
    "substitution_v2",
    "shape_v2",
    "public_surface_v19",
    "subinterpreter_v2",
)
PROCESS_NAMES = (
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
    """A frozen owner, synthetic boundary, or genuine future build failed."""


class SourceOnlyError(BuildFreezeError):
    """A source-only operation attempted an externally observable effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildFreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete first-party owner bytes")
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
        raise BuildFreezeError("reject noncanonical V10 Rust source evidence") from error


def checked_digest(value: Any, name: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require an exact independently pinned SHA-256: " + name,
    )
    return value


def checked_relative(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512, "reject unsafe owner path")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute()
        and str(parsed) == value
        and all(part not in ("", ".", "..") for part in parsed.parts)
        and all("\\" not in part and "\x00" not in part for part in parsed.parts),
        "reject an escaped, normalized, or ambiguous owner path",
    )
    return parsed.parts


def read_owned(
    relative: str,
    expected: str,
    expected_bytes: int | None = None,
    *,
    private: bool = False,
    maximum: int = MAX_SOURCE,
) -> tuple[bytes, dict[str, Any]]:
    parts = checked_relative(relative)
    checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= 64 * 1024 * 1024,
            "reject an unbounded first-party owner")
    if expected_bytes is not None:
        require(type(expected_bytes) is int and 0 < expected_bytes <= maximum,
                "reject an invalid exact owner size")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    folders: list[int] = []
    descriptor: int | None = None
    try:
        parent = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
        folders.append(parent)
        for part in parts[:-1]:
            parent = os.open(
                part,
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
            and 0 < before.st_size <= maximum
            and (before.st_dev, before.st_ino, before.st_size)
            == (visible.st_dev, visible.st_ino, visible.st_size),
            "reject a linked, replaced, empty, or oversized owner: " + relative,
        )
        if expected_bytes is not None:
            require(before.st_size == expected_bytes,
                    "reject a changed exact owner size: " + relative)
        if private:
            require(
                before.st_uid == os.geteuid()
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require an exact owner-only 0600 evidence file: " + relative,
            )
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(block) is bytes and bool(block),
                    "reject a truncated complete owner: " + relative)
            pieces.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject concealed trailing owner bytes: " + relative)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size, before.st_mode)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mode)
            and digest(raw) == expected,
            "reject a substituted exact first-party owner: " + relative,
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


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "reject a duplicated source evidence key")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str, *, require_canonical: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE,
            "reject an oversized JSON owner: " + label)
    try:
        document = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise BuildFreezeError("reject malformed JSON owner: " + label) from error
    require(type(document) is dict, "require a complete JSON object: " + label)
    if require_canonical:
        require(canonical(document) == raw,
                "reject changed canonical JSON bytes: " + label)
    return document


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_PATH),
        "run only isolated, bytecode-free, pinned CPython 3.14.6",
    )


def owner_document(value: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": value[0], "sha256": value[1], "bytes": value[2]}


def rust_source_document() -> list[dict[str, Any]]:
    return [
        {"path": path, "sha256": data[0], "bytes": data[1]}
        for path, data in sorted(RUST_OWNERS.items())
    ]


def checked_root(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded private Rust V9-compatible root")
    parsed = PurePosixPath(value)
    parts = parsed.parts
    require(
        parsed.is_absolute()
        and str(parsed) == value
        and len(parts) == 3
        and parts[0] == "/"
        and parts[1] == "tmp"
        and parts[2].startswith(ROOT_PREFIX)
        and len(parts[2]) > len(ROOT_PREFIX)
        and all(
            part.isascii() and (part.isalnum() or part in "-_")
            for part in parts[2]
        ),
        "preserve the literal frozen V9 first-party Rust private root",
    )
    return value


def boundary() -> dict[str, Any]:
    return copy.deepcopy(BOUNDARY)


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "V10 source")
    checked_digest(protocol_pin, "V10 protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "phase": "RUST DUAL-OVERLAY SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "family": FAMILY,
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "goal": owner_document(GOAL_OWNER),
        "oracle": {
            "implementation": "CPython",
            "version": "3.14.6",
            "python": {"path": PYTHON, "sha256": PYTHON_SHA256},
            "manifest": owner_document(PHASE_ONE),
            "protocol": owner_document(PHASE_ONE_PROTOCOL),
            "suite_count": SUITE_COUNT,
            "case_execution_count": CASE_COUNT,
            "private_waiver_count": PRIVATE_WAIVERS,
            "suite_ids": [row[0] for row in C_SUITES],
        },
        "previous_native_build": {
            name: owner_document(value)
            for name, value in sorted(V9_OWNERS.items())
        },
        "published_v23": {
            "owners": {
                name: owner_document(value)
                for name, value in sorted(V23_OWNERS.items())
            },
            "repository_evidence_owner_count": GRAPH_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths": GRAPH_REFERENCE_COUNT,
            "direct_graph_signed_evidence_path_count": GRAPH_EVIDENCE_CLAIM_COUNT,
            "direct_signed_reference_closure": {
                "graph_signed_evidence_paths": GRAPH_EVIDENCE_CLAIM_COUNT,
                "independently_pinned_current_renderer_and_inputs": 2,
                "total_independently_authenticated_paths": GRAPH_REFERENCE_COUNT,
            },
            "previous_v22_evidence_owner_count": 105,
            "previous_v22_authenticated_reference_count": 110,
            "previous_v22_owners": {
                name: owner_document(value)
                for name, value in sorted(V22_OWNERS.items())
            },
            "complete_c_campaign": {
                "status": "FAIL",
                "new_evidence_owner_count": C_OWNER_COUNT,
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
        "rust_sources": {
            "source_owner_count": len(RUST_OWNERS),
            "originals": rust_source_document(),
            "original_source_mutation": "FORBIDDEN",
            "external_regex_dependency_count": 0,
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
        },
        "first_party_bridge_overlay": {
            "owners": {
                name: owner_document(value)
                for name, value in sorted(BRIDGE_OWNERS.items())
            },
            "original": {
                "path": BRIDGE_PATH,
                "sha256": RUST_OWNERS[BRIDGE_PATH][0],
                "bytes": RUST_OWNERS[BRIDGE_PATH][1],
            },
            "derived": {
                "path": BRIDGE_PATH,
                "sha256": BRIDGE_DERIVED_SHA256,
                "bytes": BRIDGE_DERIVED_BYTES,
                "materialized": False,
            },
            "application": "EXACTLY ONCE PER FUTURE PRIVATE PHASE",
        },
        "first_party_public_overlay": {
            "owners": {
                name: owner_document(value)
                for name, value in sorted(PUBLIC_OWNERS.items())
            },
            "original": {
                "path": PUBLIC_PATH,
                "sha256": RUST_OWNERS[PUBLIC_PATH][0],
                "bytes": RUST_OWNERS[PUBLIC_PATH][1],
            },
            "derived": {
                "path": PUBLIC_PATH,
                "sha256": PUBLIC_DERIVED_SHA256,
                "bytes": PUBLIC_DERIVED_BYTES,
                "materialized": False,
            },
            "application": "EXACTLY ONCE PER FUTURE PRIVATE PHASE",
        },
        "future_private_snapshot": {
            "explicit_build_required": True,
            "version": VERSION,
            "interoperable_previous_root_prefix": ROOT_PREFIX,
            "root_parent": "/tmp",
            "phase_names": list(PHASES),
            "both_distinct_phases_precreated": True,
            "directory_mode": "0700",
            "file_mode": "0600",
            "source_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "unchanged_sources_per_phase": 7,
            "exclusive_bridge_overlays_per_phase": 1,
            "exclusive_public_overlays_per_phase": 1,
            "complete_private_source_owner_count": 9,
            "existing_bridge_destination": "FORBIDDEN",
            "existing_public_destination": "FORBIDDEN",
        },
        "future_native_build": {
            "explicit_build_required": True,
            "engine_name": ENGINE_NAME,
            "bridge_name": BRIDGE_NAME,
            "rustc": PINNED_RUSTC,
            "cargo": PINNED_CARGO,
            "gcc": PINNED_GCC,
            "readelf": PINNED_READELF,
            "cargo_required_flags": [
                "--release", "--locked", "--offline", "--frozen", "--target-dir"
            ],
            "cargo_net_offline": True,
            "isolated_phase_cargo_home": True,
            "external_dependency_count": 0,
            "network": "FORBIDDEN",
            "process_names_per_phase": list(PROCESS_NAMES),
            "actual_processes_per_future_phase": len(PROCESS_NAMES),
            "actual_processes_per_future_build": 2 * len(PROCESS_NAMES),
            "phase_raw_native_elf_comparison": "REQUIRED",
            "prebuilt_artifacts": "FORBIDDEN",
            "native_loading": "FORBIDDEN",
            "candidate_execution": "FORBIDDEN",
        },
        "future_evidence": {
            "directory": EVIDENCE_PATH,
            "archive_prefix": "native-source-build-v10-rust-",
            "failure_suffix": "-failures",
            "archive_suffix": ".json.gz",
            "receipt_suffix": "-publication-receipt.json",
            "exclusive_creation": True,
            "archive_and_directory_fsync": True,
            "passing_receipt_does_not_qualify_candidate": True,
        },
        "phase_boundary": boundary(),
    }


def validate_contract(document: Any, source_pin: str, protocol_pin: str) -> None:
    require(
        type(document) is dict
        and canonical(document) == canonical(contract_document(source_pin, protocol_pin)),
        "reject altered V10 owners, evidence denominators, dual overlays, or boundaries",
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

    def install(obj: Any, name: str, bucket: str) -> None:
        if not hasattr(obj, name):
            return
        previous = getattr(obj, name)

        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            effects[bucket] += 1
            raise SourceOnlyError("a synthetic V10 control attempted " + bucket)

        originals.append((obj, name, previous))
        setattr(obj, name, blocked)

    previous_import = builtins.__import__

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name in ("re", "_sre", "regex", "_rust_bridge", "_rust_engine") or (
            name.startswith("candidates.") or name.startswith("rebar")
        ):
            effects["blocked_candidate_imports"] += 1
            raise SourceOnlyError("a synthetic control attempted candidate or regex import")
        return previous_import(name, *args, **kwargs)

    try:
        for obj, name in ((builtins, "open"), (io, "open")):
            install(obj, name, "blocked_reads")
        for name in ("open", "read", "stat", "lstat", "scandir", "listdir"):
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
        for obj, name, original in reversed(originals):
            setattr(obj, name, original)


def synthetic_plan() -> dict[str, Any]:
    unchanged = sorted(set(RUST_OWNERS) - {BRIDGE_PATH, PUBLIC_PATH})
    phases: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    identity = 1000
    pid = 8000
    for phase in PHASES:
        originals = []
        for path in unchanged:
            identity += 1
            originals.append(
                {
                    "path": path,
                    "sha256": RUST_OWNERS[path][0],
                    "bytes": RUST_OWNERS[path][1],
                    "inode": identity,
                    "mode": 0o600,
                }
            )
        identity += 1
        bridge = {
            "path": BRIDGE_PATH,
            "sha256": BRIDGE_DERIVED_SHA256,
            "bytes": BRIDGE_DERIVED_BYTES,
            "inode": identity,
            "mode": 0o600,
            "source_apply_count": 1,
        }
        identity += 1
        public = {
            "path": PUBLIC_PATH,
            "sha256": PUBLIC_DERIVED_SHA256,
            "bytes": PUBLIC_DERIVED_BYTES,
            "inode": identity,
            "mode": 0o600,
            "source_apply_count": 1,
        }
        identity += 1
        phases.append(
            {
                "name": phase,
                "root_mode": 0o700,
                "root_inode": identity,
                "originals": originals,
                "bridge": bridge,
                "public": public,
            }
        )
        for name in PROCESS_NAMES:
            pid += 1
            steps.append(
                {"phase": phase, "name": name, "pid": pid, "exit_status": 0}
            )
    return {
        "root": "/tmp/" + ROOT_PREFIX + "synthetic",
        "phases": phases,
        "steps": steps,
    }


def validate_synthetic_plan(plan: Any) -> dict[str, Any]:
    require(type(plan) is dict, "reject a missing synthetic Rust phase plan")
    checked_root(plan.get("root"))
    phases = plan.get("phases")
    steps = plan.get("steps")
    require(
        type(phases) is list
        and len(phases) == 2
        and type(steps) is list
        and len(steps) == 2 * len(PROCESS_NAMES),
        "require exactly two phases and twenty-eight planned native roles",
    )
    unchanged = sorted(set(RUST_OWNERS) - {BRIDGE_PATH, PUBLIC_PATH})
    phase_identities: set[int] = set()
    source_identities: set[int] = set()
    for index, phase in enumerate(phases):
        require(
            type(phase) is dict
            and phase.get("name") == PHASES[index]
            and phase.get("root_mode") == 0o700
            and type(phase.get("root_inode")) is int
            and phase["root_inode"] not in phase_identities,
            "require two genuinely distinct owner-only synthetic Rust phases",
        )
        phase_identities.add(phase["root_inode"])
        originals = phase.get("originals")
        require(
            type(originals) is list
            and len(originals) == 7
            and [item.get("path") for item in originals] == unchanged,
            "copy exactly seven unchanged sources and leave both overlays absent",
        )
        for item in originals:
            expected = RUST_OWNERS[item["path"]]
            require(
                item.get("sha256") == expected[0]
                and item.get("bytes") == expected[1]
                and item.get("mode") == 0o600
                and type(item.get("inode")) is int
                and item["inode"] not in source_identities,
                "reject forged, aliased, substituted, or reused Rust sources",
            )
            source_identities.add(item["inode"])
        for name, path, sha, count in (
            ("bridge", BRIDGE_PATH, BRIDGE_DERIVED_SHA256, BRIDGE_DERIVED_BYTES),
            ("public", PUBLIC_PATH, PUBLIC_DERIVED_SHA256, PUBLIC_DERIVED_BYTES),
        ):
            item = phase.get(name)
            require(
                type(item) is dict
                and item.get("path") == path
                and item.get("sha256") == sha
                and item.get("bytes") == count
                and item.get("mode") == 0o600
                and item.get("source_apply_count") == 1
                and type(item.get("inode")) is int
                and item["inode"] not in source_identities,
                "require exactly one independent exclusive " + name + " overlay",
            )
            source_identities.add(item["inode"])
    pids: set[int] = set()
    for index, step in enumerate(steps):
        require(
            type(step) is dict
            and step.get("phase") == PHASES[index // len(PROCESS_NAMES)]
            and step.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
            and type(step.get("pid")) is int
            and step["pid"] > 0
            and step["pid"] not in pids
            and step.get("exit_status") == 0,
            "reject omitted, borrowed, reordered, or fabricated native process roles",
        )
        pids.add(step["pid"])
    require(len(source_identities) == 18, "require eighteen independent source identities")
    return {
        "independent_phase_count": 2,
        "unchanged_source_count_per_phase": 7,
        "bridge_overlay_count_per_phase": 1,
        "public_overlay_count_per_phase": 1,
        "complete_source_count_per_phase": 9,
        "synthetic_planned_process_count": len(steps),
    }


def expect_rejected(action: Any, name: str) -> int:
    try:
        action()
    except (
        BuildFreezeError, TypeError, ValueError, OSError,
        KeyError, IndexError, AttributeError, SyntaxError,
    ):
        return 1
    raise BuildFreezeError("accepted an unsafe V10 source-only control: " + name)


def self_test() -> dict[str, Any]:
    accepted = 0
    rejected = 0
    source_pin = "a" * 64
    protocol_pin = "b" * 64
    frozen = contract_document(source_pin, protocol_pin)
    plan = synthetic_plan()
    with source_only_wall() as effects:
        validate_contract(frozen, source_pin, protocol_pin)
        phase_result = validate_synthetic_plan(plan)
        require(
            phase_result["synthetic_planned_process_count"] == 28
            and sum(row[1] for row in C_SUITES) == CASE_COUNT
            and sum(row[2] for row in C_SUITES) == C_MISMATCH_COUNT
            and sum(row[1] for row in C_SUITES if row[2] == 0) == C_PASS_COUNT
            and len(RUST_OWNERS) == 9
            and len(PROCESS_NAMES) == 14
            and len(set(PROCESS_NAMES)) == 14
            and C_OWNER_COUNT == 2 * SUITE_COUNT + 4,
            "preserve every original suite, actual C result, and genuine process role",
        )
        accepted += 2
        hostile_changes = (
            (("version",), 9),
            (("family",), "zig"),
            (("phase",), "BUILD PASS"),
            (("oracle", "case_execution_count"), CASE_COUNT - 1),
            (("oracle", "suite_count"), SUITE_COUNT - 1),
            (("oracle", "private_waiver_count"), PRIVATE_WAIVERS + 1),
            (("published_v23", "repository_evidence_owner_count"), 134),
            (("published_v23", "authenticated_digest_addressed_history_paths"), 139),
            (("published_v23", "direct_graph_signed_evidence_path_count"), 137),
            (("published_v23", "direct_signed_reference_closure",
              "total_independently_authenticated_paths"), 139),
            (("published_v23", "complete_c_campaign", "new_evidence_owner_count"), 29),
            (("published_v23", "complete_c_campaign", "actual_candidate_workers"), 12),
            (("published_v23", "complete_c_campaign", "completed_suite_count"), 12),
            (("published_v23", "complete_c_campaign", "verified_passing_case_count"), 31237),
            (("published_v23", "complete_c_campaign", "semantic_mismatch_count"), 0),
            (("published_v23", "complete_c_campaign", "infrastructure_failure_count"), 1),
            (("published_v23", "complete_c_campaign", "candidate_qualified"), True),
            (("published_v23", "original_rust", "semantic_mismatch_count"), 0),
            (("first_party_bridge_overlay", "derived", "sha256"), "0" * 64),
            (("first_party_public_overlay", "derived", "sha256"), "0" * 64),
            (("future_private_snapshot", "interoperable_previous_root_prefix"),
             "rebar-phase2-native-build-v10-rust-"),
            (("future_private_snapshot", "unchanged_sources_per_phase"), 8),
            (("future_private_snapshot", "exclusive_bridge_overlays_per_phase"), 0),
            (("future_private_snapshot", "exclusive_public_overlays_per_phase"), 0),
            (("future_private_snapshot", "complete_private_source_owner_count"), 8),
            (("future_native_build", "external_dependency_count"), 1),
            (("future_native_build", "cargo_net_offline"), False),
            (("future_native_build", "actual_processes_per_future_build"), 27),
            (("future_native_build", "candidate_execution"), "ALLOWED"),
            (("rust_sources", "stdlib_regex_engine"), "ALLOWED"),
            (("rust_sources", "external_regex_engine"), "ALLOWED"),
            (("phase_boundary", "clock_samples"), 1),
            (("phase_boundary", "source_apply_count"), 1),
            (("phase_boundary", "hidden_cases_read"), 1),
            (("phase_boundary", "winner_selected"), True),
        )
        for path, replacement in hostile_changes:
            hostile = copy.deepcopy(frozen)
            target = hostile
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = replacement
            rejected += expect_rejected(
                lambda item=hostile: validate_contract(item, source_pin, protocol_pin),
                ".".join(path),
            )
        mutations = (
            (("phases", 0, "name"), "reference-b"),
            (("phases", 1, "name"), "reference-a"),
            (("phases", 0, "root_mode"), 0o755),
            (("phases", 1, "root_inode"), plan["phases"][0]["root_inode"]),
            (("phases", 0, "bridge", "path"), PUBLIC_PATH),
            (("phases", 0, "bridge", "sha256"), "0" * 64),
            (("phases", 0, "bridge", "source_apply_count"), 2),
            (("phases", 1, "bridge", "source_apply_count"), 0),
            (("phases", 0, "public", "path"), BRIDGE_PATH),
            (("phases", 0, "public", "sha256"), "0" * 64),
            (("phases", 0, "public", "source_apply_count"), 2),
            (("phases", 1, "public", "mode"), 0o644),
            (("phases", 0, "originals", 0, "mode"), 0o644),
            (("phases", 0, "originals", 0, "sha256"), "0" * 64),
            (("phases", 0, "originals", 0, "bytes"), 0),
            (("steps", 0, "name"), "build_external_regex"),
            (("steps", 0, "phase"), "reference-b"),
            (("steps", 0, "exit_status"), 1),
            (("steps", 1, "pid"), plan["steps"][0]["pid"]),
        )
        for path, replacement in mutations:
            hostile = copy.deepcopy(plan)
            target: Any = hostile
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = replacement
            rejected += expect_rejected(
                lambda item=hostile: validate_synthetic_plan(item),
                "synthetic phase " + ".".join(map(str, path)),
            )
        for name, value in (
            ("wrong version", "/tmp/rebar-phase2-native-build-v10-rust-abc"),
            ("wrong family", "/tmp/rebar-phase2-native-build-v9-zig-abc"),
            ("missing suffix", "/tmp/" + ROOT_PREFIX),
            ("escaped root", "/tmp/" + ROOT_PREFIX + "../x"),
            ("nested root", "/tmp/" + ROOT_PREFIX + "x/reference-a"),
            ("workspace root", str(ROOT)),
            ("relative root", ROOT_PREFIX + "x"),
            ("backslash", "/tmp/" + ROOT_PREFIX + "x\\y"),
        ):
            rejected += expect_rejected(lambda item=value: checked_root(item), name)
        for value in ("", "0" * 63, "0" * 65, "A" * 64, "z" * 64, None):
            rejected += expect_rejected(
                lambda item=value: checked_digest(item, "hostile"),
                "hostile owner fingerprint",
            )
        for raw in (
            b'{"x":1,"x":2}\n',
            b'{"x":NaN}\n',
            b'[]\n',
            b'{"x":1}',
        ):
            rejected += expect_rejected(
                lambda item=raw: strict_json(item, "synthetic hostile owner"),
                "hostile canonical owner",
            )
        probes = (
            ("read", lambda: builtins.open("/tmp/rebar-v10-forbidden", "rb")),
            ("read", lambda: io.open("/tmp/rebar-v10-forbidden", "rb")),
            ("read", lambda: os.open("/tmp/rebar-v10-forbidden", os.O_RDONLY)),
            ("write", lambda: os.write(1, b"forbidden")),
            ("write", lambda: os.mkdir("/tmp/rebar-v10-forbidden")),
            ("process", lambda: subprocess.run(["cargo", "--version"])),
            ("network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("clock", lambda: time.perf_counter()),
            ("clock", lambda: time.time()),
            ("loader", lambda: ctypes.CDLL("_rust_bridge.so")),
            ("candidate", lambda: builtins.__import__("candidates.rust_candidate")),
            ("stdlib regex", lambda: builtins.__import__("re")),
            ("snapshot", lambda: tempfile.mkdtemp(prefix=ROOT_PREFIX)),
            ("thread", lambda: threading.Thread().start()),
        )
        for name, probe in probes:
            rejected += expect_rejected(probe, "blocked " + name)
        observed_effects = dict(effects)
    require(rejected >= 70, "require comprehensive independent negative source controls")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_source_controls": accepted,
        "rejected_hostile_controls": rejected,
        "synthetic_phase_plan": phase_result,
        "source_only_blocked_effects": observed_effects,
        "historical_evidence_owner_count": GRAPH_OWNER_COUNT,
        "historical_authenticated_reference_count": GRAPH_REFERENCE_COUNT,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVERS,
        **boundary(),
    }


def load_module(name: str, owner: tuple[str, str, int]) -> types.ModuleType:
    require(
        type(name) is str
        and name.startswith("_rebar_phase2_owned_v10_")
        and name not in sys.modules,
        "reject substituted, candidate, or reused private kernel modules",
    )
    raw, _ = read_owned(owner[0], owner[1], owner[2])
    try:
        parsed = ast.parse(raw.decode("utf-8", "strict"), filename=owner[0])
        require(isinstance(parsed, ast.Module), "reject an incomplete frozen source module")
        module = types.ModuleType(name)
        module.__dict__["__file__"] = str(ROOT / owner[0])
        module.__dict__["__package__"] = None
        exec(compile(parsed, str(ROOT / owner[0]), "exec"), module.__dict__)
        return module
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise BuildFreezeError("reject altered frozen first-party source: " + owner[0]) from error


def collect_evidence(value: Any, claims: dict[str, str]) -> None:
    if type(value) is list:
        for item in value:
            collect_evidence(item, claims)
        return
    if type(value) is not dict:
        return
    path = value.get("path")
    sha = value.get("sha256")
    if (
        type(path) is str
        and (
            path.startswith("oracle/phase2/evidence/")
            or path.startswith("experiments/")
        )
        and type(sha) is str
    ):
        checked_relative(path)
        checked_digest(sha, path)
        previous = claims.get(path)
        require(previous is None or previous == sha,
                "reject conflicting signed V23 evidence references: " + path)
        claims[path] = sha
    for item in value.values():
        collect_evidence(item, claims)


def claim_owner(
    claim: Any,
    label: str,
    observed: dict[str, dict[str, Any]],
) -> tuple[bytes, dict[str, Any]]:
    require(type(claim) is dict, "require a complete signed owner: " + label)
    path = claim.get("path")
    sha = claim.get("sha256")
    size = claim.get("bytes")
    require(
        type(path) is str
        and path.startswith("oracle/phase2/evidence/")
        and type(size) is int,
        "require a private signed actual evidence owner: " + label,
    )
    raw, owner = read_owned(path, checked_digest(sha, label), size, private=True)
    previous = observed.get(path)
    require(previous is None or previous["sha256"] == sha,
            "reject a conflicting actual C archive identity")
    observed[path] = owner
    return raw, owner


def require_receipt_archive(
    receipt: Mapping[str, Any],
    archive: Mapping[str, Any],
    label: str,
) -> None:
    actual = receipt.get("archive")
    require(
        type(actual) is dict
        and actual.get("relative") == archive["path"]
        and actual.get("sha256") == archive["sha256"]
        and actual.get("size_bytes") == archive["bytes"]
        and actual.get("exclusive_creation") is True
        and actual.get("file_fsync_completed") is True
        and actual.get("directory_fsync_completed") is True
        and actual.get("same_inode_readback_verified") is True,
        "reject an unsigned, substituted, or nondurable actual archive: " + label,
    )


def expanded_archive(raw: bytes, receipt: Mapping[str, Any], label: str) -> dict[str, Any]:
    expected_size = receipt.get("uncompressed_bytes")
    expected_sha = receipt.get("uncompressed_sha256")
    require(
        type(expected_size) is int and 0 < expected_size <= MAX_EXPANDED,
        "reject an oversized C aggregate archive: " + label,
    )
    try:
        expanded = gzip.decompress(raw)
    except (OSError, EOFError, ValueError) as error:
        raise BuildFreezeError("reject truncated genuine C archive: " + label) from error
    require(
        len(expanded) == expected_size
        and digest(expanded) == checked_digest(expected_sha, label),
        "reject altered complete C aggregate records: " + label,
    )
    return strict_json(expanded, label)


def verify_rust_package(raw_sources: Mapping[str, bytes]) -> dict[str, Any]:
    try:
        manifest = tomllib.loads(
            raw_sources["candidates/rust/Cargo.toml"].decode("utf-8", "strict")
        )
        lock = tomllib.loads(
            raw_sources["candidates/rust/Cargo.lock"].decode("utf-8", "strict")
        )
    except (tomllib.TOMLDecodeError, UnicodeError) as error:
        raise BuildFreezeError("reject non-owned Rust package metadata") from error
    package = manifest.get("package")
    library = manifest.get("lib")
    profile = manifest.get("profile", {}).get("release")
    packages = lock.get("package")
    require(
        type(package) is dict
        and package.get("name") == "rebar-rust-continuation"
        and package.get("version") == "0.1.0"
        and package.get("edition") == "2024"
        and package.get("rust-version") == "1.85"
        and package.get("publish") is False
        and type(library) is dict
        and library.get("crate-type") == ["cdylib"]
        and type(profile) is dict
        and profile.get("opt-level") == 3
        and profile.get("lto") is True
        and profile.get("codegen-units") == 1
        and profile.get("panic") == "abort"
        and all(
            item not in manifest
            for item in (
                "dependencies", "dev-dependencies", "build-dependencies",
                "workspace", "patch", "replace",
            )
        )
        and lock.get("version") == 4
        and type(packages) is list
        and len(packages) == 1
        and type(packages[0]) is dict
        and packages[0].get("name") == package["name"]
        and packages[0].get("version") == package["version"]
        and "dependencies" not in packages[0]
        and "source" not in packages[0],
        "require one independently owned offline Rust crate and zero dependencies",
    )
    return {
        "status": "PASS",
        "package_count": 1,
        "external_dependency_count": 0,
        "manifest_sha256": RUST_OWNERS["candidates/rust/Cargo.toml"][0],
        "lock_sha256": RUST_OWNERS["candidates/rust/Cargo.lock"][0],
        "network_requests": 0,
    }


def validate_c_campaign(
    campaign: Any,
    graph_snapshot: Mapping[str, Any],
    observed: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    require(type(campaign) is dict, "require the actual complete signed C campaign")
    require(
        campaign.get("family") == "c"
        and campaign.get("status") == "FAIL"
        and campaign.get("failure_class") == "SEMANTIC MISMATCH"
        and campaign.get("label") == C_LABEL
        and campaign.get("qualified") is False
        and campaign.get("suite_count") == SUITE_COUNT
        and campaign.get("completed_suite_count") == SUITE_COUNT
        and campaign.get("fully_passing_suite_count") == 8
        and campaign.get("actual_candidate_workers") == C_WORKER_COUNT
        and campaign.get("actual_aggregate_process_count") == 1
        and campaign.get("actual_aggregate_process_exit_status") == 1
        and campaign.get("observed_matching_case_count") == CASE_COUNT
        and campaign.get("verified_passing_case_count") == C_PASS_COUNT
        and campaign.get("semantic_mismatch_count") == C_MISMATCH_COUNT
        and campaign.get("infrastructure_failure_count") == 0
        and campaign.get("all_original_suite_evidence_preserved") is True
        and campaign.get("new_repository_evidence_owner_count") == C_OWNER_COUNT
        and campaign.get("original_canonical_native_restored") is True
        and campaign.get("restoration_status") == "PASS"
        and campaign.get("holdout") == "NOT OPENED"
        and campaign.get("performance") == "NOT MEASURED",
        "preserve all thirteen real C workers and all 1,262 real failures",
    )
    native = campaign.get("original_canonical_native")
    require(
        type(native) is dict
        and native.get("path") == ORIGINAL_NATIVE[0]
        and native.get("sha256") == ORIGINAL_NATIVE[1]
        and native.get("bytes") == ORIGINAL_NATIVE[2],
        "preserve the exact restored, not promoted, original C native owner",
    )
    require(
        graph_snapshot.get("c_v10_repaired_original_campaign") == campaign
        and graph_snapshot.get("repaired_c_actual_candidate_worker_count")
        == C_WORKER_COUNT
        and graph_snapshot.get("repaired_c_completed_suite_count") == SUITE_COUNT
        and graph_snapshot.get("repaired_c_actual_verified_matching_case_count")
        == CASE_COUNT
        and graph_snapshot.get("repaired_c_verified_passing_case_count")
        == C_PASS_COUNT
        and graph_snapshot.get("repaired_c_semantic_mismatch_count")
        == C_MISMATCH_COUNT
        and graph_snapshot.get("repaired_c_infrastructure_failure_count") == 0
        and graph_snapshot.get("repaired_c_native_promoted") is False,
        "bind the authentic complete current C result to the published graph",
    )
    archive_raw, archive_owner = claim_owner(
        campaign.get("archive"), "actual outer C report", observed,
    )
    receipt_raw, receipt_owner = claim_owner(
        campaign.get("receipt"), "actual outer C receipt", observed,
    )
    aggregate_raw, aggregate_owner = claim_owner(
        campaign.get("aggregate_archive"), "actual C aggregate", observed,
    )
    aggregate_receipt_raw, aggregate_receipt_owner = claim_owner(
        campaign.get("aggregate_receipt"), "actual C aggregate receipt", observed,
    )
    receipt = strict_json(receipt_raw, "durable outer C receipt")
    aggregate_receipt = strict_json(aggregate_receipt_raw, "durable C aggregate receipt")
    require_receipt_archive(receipt, archive_owner, "outer C campaign")
    require_receipt_archive(aggregate_receipt, aggregate_owner, "C candidate aggregate")
    require(
        receipt.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v3-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("family") == "c"
        and receipt.get("label") == C_LABEL
        and receipt.get("historical_evidence_owner_count") == 105
        and receipt.get("historical_authenticated_reference_count") == 110
        and receipt.get("original_native_restored") is True
        and aggregate_receipt.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v9-durable-publication-receipt"
        and aggregate_receipt.get("status") == "PASS"
        and aggregate_receipt.get("candidate_status") == "FAIL"
        and aggregate_receipt.get("candidate_family") == "c"
        and aggregate_receipt.get("label") == C_LABEL
        and aggregate_receipt.get("suite_count") == SUITE_COUNT
        and aggregate_receipt.get("completed_suite_count") == SUITE_COUNT,
        "never treat a durable receipt as passing candidate correctness",
    )
    outer = expanded_archive(archive_raw, receipt, "genuine complete C campaign")
    inner = expanded_archive(
        aggregate_raw, aggregate_receipt, "genuine complete thirteen-worker C result",
    )
    require(
        outer.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v3-actual-recovered-campaign"
        and outer.get("status") == "FAIL"
        and outer.get("family") == "c"
        and outer.get("suite_count") == SUITE_COUNT
        and outer.get("completed_suite_count") == SUITE_COUNT
        and outer.get("verified_passing_case_count") == C_PASS_COUNT
        and outer.get("semantic_mismatch_count") == C_MISMATCH_COUNT
        and outer.get("infrastructure_failure_count") == 0
        and outer.get("candidate_qualified") is False
        and outer.get("original_native_restored") is True
        and inner.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v9-complete-original-candidate-evaluation"
        and inner.get("status") == "FAIL"
        and inner.get("candidate_family") == "c"
        and inner.get("suite_count") == SUITE_COUNT
        and inner.get("completed_suite_count") == SUITE_COUNT
        and inner.get("actual_candidate_workers") == C_WORKER_COUNT
        and inner.get("verified_passing_case_count") == C_PASS_COUNT
        and inner.get("semantic_mismatch_count") == C_MISMATCH_COUNT
        and inner.get("infrastructure_failure_count") == 0
        and inner.get("candidate_qualified") is False,
        "preserve both real all-suite C failures and every actual matching count",
    )
    rows = campaign.get("suite_results")
    outer_rows = outer.get("original_suite_results")
    inner_rows = inner.get("suite_results")
    require(
        type(rows) is list
        and type(outer_rows) is list
        and type(inner_rows) is list
        and len(rows) == len(outer_rows) == len(inner_rows) == SUITE_COUNT,
        "retain all thirteen genuine signed C suite workers",
    )
    for signed, outside, inside, expected in zip(
        rows, outer_rows, inner_rows, C_SUITES, strict=True
    ):
        suite, count, mismatches = expected
        result = "PASS" if mismatches == 0 else "FAIL"
        require(
            all(type(row) is dict for row in (signed, outside, inside))
            and all(row.get("suite") == suite for row in (signed, outside, inside))
            and all(
                row.get("case_execution_denominator") == count
                for row in (signed, outside, inside)
            )
            and all(row.get("mismatch_count") == mismatches
                    for row in (signed, outside, inside))
            and all(row.get("status") == result for row in (signed, outside, inside))
            and signed.get("actual_worker_started") is True
            and signed.get("worker_returncode") == (0 if mismatches == 0 else 1),
            "preserve an actual independent C worker: " + suite,
        )
        _, worker_archive = claim_owner(signed.get("archive"), suite + " archive", observed)
        worker_receipt_raw, _ = claim_owner(
            signed.get("receipt"), suite + " receipt", observed,
        )
        worker_receipt = strict_json(worker_receipt_raw, suite + " durable receipt")
        require_receipt_archive(worker_receipt, worker_archive, suite)
        require(
            worker_receipt.get("schema")
            == "rebar-frozen-python-re-p0-candidate-worker-v7-durable-suite-publication-receipt"
            and worker_receipt.get("status") == "PASS"
            and worker_receipt.get("candidate_status") == result
            and worker_receipt.get("candidate_family") == "c"
            and worker_receipt.get("label") == C_LABEL
            and worker_receipt.get("suite") == suite
            and worker_receipt.get("case_execution_denominator") == count
            and worker_receipt.get("phase_one_case_execution_denominator")
            == CASE_COUNT
            and worker_receipt.get("genuine_original_suite") is True
            and worker_receipt.get("mismatch_count") == mismatches
            and worker_receipt.get("all_original_records_and_mismatches_preserved")
            is True
            and worker_receipt.get("candidate_qualified") is False
            and worker_receipt.get("uncompressed_bytes")
            == signed.get("uncompressed_bytes")
            and worker_receipt.get("uncompressed_sha256")
            == signed.get("uncompressed_sha256"),
            "reject a forged, omitted, or relabeled actual C worker: " + suite,
        )
    require(
        len(observed) == C_OWNER_COUNT,
        "require exactly thirty distinct real C archives and durable receipts",
    )
    return {
        "status": "FAIL",
        "actual_evidence_owner_count": len(observed),
        "actual_candidate_workers": C_WORKER_COUNT,
        "completed_suite_count": SUITE_COUNT,
        "observed_matching_case_count": CASE_COUNT,
        "verified_passing_case_count": C_PASS_COUNT,
        "semantic_mismatch_count": C_MISMATCH_COUNT,
        "infrastructure_failure_count": 0,
        "original_native_restored": True,
        "qualified": False,
    }


def verify_context(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    checked_digest(source_pin, "V10 source")
    checked_digest(protocol_pin, "V10 protocol")
    checked_digest(contract_pin, "V10 contract")
    verified: dict[str, dict[str, Any]] = {}
    for path, sha in (
        (SOURCE_PATH, source_pin),
        (PROTOCOL_PATH, protocol_pin),
        (CONTRACT_PATH, contract_pin),
    ):
        raw, owner = read_owned(path, sha)
        verified[path] = owner
        if path == CONTRACT_PATH:
            frozen = strict_json(raw, "frozen V10 dual-overlay build contract")
            validate_contract(frozen, source_pin, protocol_pin)
    goal_raw, verified[GOAL_OWNER[0]] = read_owned(*GOAL_OWNER)
    require(len(goal_raw) == GOAL_OWNER[2],
            "preserve the exact immutable user objective")
    phase_raw, verified[PHASE_ONE[0]] = read_owned(*PHASE_ONE)
    _, verified[PHASE_ONE_PROTOCOL[0]] = read_owned(*PHASE_ONE_PROTOCOL)
    matrix = strict_json(phase_raw, "unchanged complete CPython phase-one matrix")
    require(
        matrix.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and matrix.get("version") == 1
        and type(matrix.get("suites")) is list
        and [
            (item.get("id"), item.get("case_execution_count"))
            for item in matrix["suites"]
        ]
        == [(suite, count) for suite, count, _ in C_SUITES]
        and sum(item["case_execution_count"] for item in matrix["suites"])
        == CASE_COUNT,
        "preserve every original, counted CPython correctness case",
    )
    denominator = matrix.get("denominator")
    require(
        type(denominator) is dict
        and denominator.get("final_required_case_execution_denominator")
        == CASE_COUNT
        and denominator.get("frozen_planned_case_execution_denominator")
        == CASE_COUNT
        and denominator.get("private_upstream_methods_outside_public_denominator")
        == PRIVATE_WAIVERS
        and denominator.get("counted_suite_ids") == [row[0] for row in C_SUITES],
        "preserve all 13 suites, 31,237 cases, and 13 named private waivers",
    )
    source_bytes: dict[str, bytes] = {}
    for path, (sha, count) in sorted(RUST_OWNERS.items()):
        raw, verified[path] = read_owned(path, sha, count)
        source_bytes[path] = raw
    package = verify_rust_package(source_bytes)

    for group in (
        V9_OWNERS, BRIDGE_OWNERS, PUBLIC_OWNERS, V22_OWNERS, V23_OWNERS,
    ):
        for owner in group.values():
            raw, verified[owner[0]] = read_owned(*owner)
            if owner == V23_OWNERS["inputs"]:
                graph_inputs = strict_json(raw, "complete signed V23 graph inputs")
            elif owner == V23_OWNERS["summary"]:
                graph_summary = strict_json(raw, "complete signed V23 graph summary")
            elif owner == V23_OWNERS["svg"]:
                graph_svg = raw
            elif owner == V9_OWNERS["contract"]:
                previous_contract = strict_json(raw, "immutable V9 Rust freeze")
            elif owner == BRIDGE_OWNERS["contract"]:
                bridge_contract = strict_json(raw, "immutable first-party bridge repair")
            elif owner == PUBLIC_OWNERS["contract"]:
                public_contract = strict_json(raw, "immutable first-party public repair")

    v9 = load_module("_rebar_phase2_owned_v10_v9_kernel", V9_OWNERS["source"])
    bridge = load_module(
        "_rebar_phase2_owned_v10_bridge_overlay", BRIDGE_OWNERS["source"],
    )
    public = load_module(
        "_rebar_phase2_owned_v10_public_overlay", PUBLIC_OWNERS["source"],
    )
    renderer = load_module(
        "_rebar_phase2_owned_v10_v23_renderer", V23_OWNERS["source"],
    )
    require(
        v9.SCHEMA == "rebar-phase2-owned-native-source-build-v9"
        and v9.WORK_PREFIX == WORK_PREFIX
        and v9.FAMILY == FAMILY
        and tuple(v9.PHASES) == PHASES
        and tuple(v9.PROCESS_NAMES) == PROCESS_NAMES
        and v9.RUST_OWNERS == RUST_OWNERS
        and v9.PINNED_CARGO == PINNED_CARGO
        and v9.PINNED_RUSTC == PINNED_RUSTC
        and v9.PINNED_GCC == PINNED_GCC
        and v9.PINNED_READELF == PINNED_READELF
        and previous_contract == v9.expected_contract(),
        "authenticate the complete immutable V9 kernel without rerunning history",
    )
    require(
        bridge.SCHEMA == "rebar-phase2-owned-rust-source-repair-v1"
        and bridge.ORIGINAL_PATH == BRIDGE_PATH
        and bridge.ORIGINAL_SHA256 == RUST_OWNERS[BRIDGE_PATH][0]
        and bridge.ORIGINAL_BYTES == RUST_OWNERS[BRIDGE_PATH][1]
        and bridge.ADAPTER_PATH == PUBLIC_PATH
        and bridge.ADAPTER_SHA256 == RUST_OWNERS[PUBLIC_PATH][0]
        and bridge.ADAPTER_BYTES == RUST_OWNERS[PUBLIC_PATH][1]
        and bridge.DERIVED_SHA256 == BRIDGE_DERIVED_SHA256
        and bridge.DERIVED_BYTES == BRIDGE_DERIVED_BYTES
        and bridge_contract
        == bridge.contract_document(
            BRIDGE_OWNERS["source"][1],
            BRIDGE_OWNERS["protocol"][1],
        ),
        "authenticate the unique V9-prefix-compatible first-party bridge overlay",
    )
    require(
        public.SCHEMA == "rebar-phase2-owned-rust-public-contract-source-repair-v1"
        and public.ORIGINAL_RELATIVE == PUBLIC_PATH
        and public.ORIGINAL_SHA256 == RUST_OWNERS[PUBLIC_PATH][0]
        and public.ORIGINAL_BYTES == RUST_OWNERS[PUBLIC_PATH][1]
        and public.DERIVED_SHA256 == PUBLIC_DERIVED_SHA256
        and public.DERIVED_BYTES == PUBLIC_DERIVED_BYTES
        and public.PRIVATE_ROOT_PREFIX == "rebar-phase2-native-build-"
        and public.PRIVATE_ROOT_FAMILY == "-rust-"
        and tuple(public.PHASE_NAMES) == PHASES
        and len(public.REPAIR_BLOCKS) == 3
        and public_contract
        == public.contract_document(
            PUBLIC_OWNERS["source"][1],
            PUBLIC_OWNERS["protocol"][1],
        ),
        "authenticate all three exact privately owned Python public-contract changes",
    )
    derived_bridge = bridge.repaired_source(
        source_bytes[BRIDGE_PATH],
        RUST_OWNERS[BRIDGE_PATH][0],
        RUST_OWNERS[BRIDGE_PATH][1],
    )
    derived_public = public.repaired_source(
        source_bytes[PUBLIC_PATH],
        RUST_OWNERS[PUBLIC_PATH][0],
        RUST_OWNERS[PUBLIC_PATH][1],
    )
    require(
        type(derived_bridge) is bytes
        and len(derived_bridge) == BRIDGE_DERIVED_BYTES
        and digest(derived_bridge) == BRIDGE_DERIVED_SHA256
        and type(derived_public) is bytes
        and len(derived_public) == PUBLIC_DERIVED_BYTES
        and digest(derived_public) == PUBLIC_DERIVED_SHA256,
        "derive both uniquely pinned first-party private overlays in memory only",
    )
    require(
        renderer.SCHEMA == "rebar-candidate-current-overview-v23"
        and renderer.TOTAL_OWNERS == GRAPH_OWNER_COUNT
        and renderer.TOTAL_REFERENCES == GRAPH_REFERENCE_COUNT
        and renderer.NEW_OWNERS == C_OWNER_COUNT
        and tuple((row[0], row[1], row[2]) for row in renderer.SUITES)
        == C_SUITES,
        "pin the genuine latest V23 renderer and every original C test group",
    )
    snapshot = graph_summary.get("snapshot")
    require(type(snapshot) is dict, "require the complete signed V23 snapshot")
    renderer.validate_snapshot(snapshot)
    require(
        graph_inputs.get("schema") == "rebar-candidate-current-overview-v23-inputs"
        and graph_inputs.get("version") == 23
        and graph_inputs.get("repository_evidence_owner_count") == GRAPH_OWNER_COUNT
        and graph_inputs.get("all_digest_addressed_history_path_count")
        == GRAPH_REFERENCE_COUNT
        and graph_inputs.get("preserved_v22_repository_evidence_owner_count") == 105
        and graph_inputs.get("preserved_v22_digest_addressed_history_path_count")
        == 110
        and graph_inputs.get("new_v10_c_campaign_repository_evidence_owner_count")
        == C_OWNER_COUNT
        and graph_inputs.get("current_source_owner_count") == 25
        and graph_inputs.get("suite_count") == SUITE_COUNT
        and graph_inputs.get("full_case_denominator") == CASE_COUNT
        and graph_inputs.get("candidate_qualified_count") == 0
        and graph_inputs.get("performance") == "NOT MEASURED"
        and graph_inputs.get("memory") == "NOT MEASURED"
        and graph_inputs.get("final_holdout_opened") is False
        and graph_inputs.get("winner_selected") is False,
        "reject stale V19/V22 history or changed exact V23 135/140 accounting",
    )
    require(
        graph_summary.get("schema") == "rebar-candidate-current-overview-v23-summary"
        and graph_summary.get("status") == "PASS"
        and graph_summary.get("repository_evidence_owner_count") == GRAPH_OWNER_COUNT
        and graph_summary.get("authenticated_digest_addressed_history_paths")
        == GRAPH_REFERENCE_COUNT
        and graph_summary.get("new_v10_c_campaign_repository_evidence_owner_count")
        == C_OWNER_COUNT
        and graph_summary.get("qualified_candidate_count") == 0
        and graph_summary.get("c_repaired_candidate_worker_count") == C_WORKER_COUNT
        and graph_summary.get("c_repaired_completed_suite_count") == SUITE_COUNT
        and graph_summary.get("c_repaired_verified_passing_case_count") == C_PASS_COUNT
        and graph_summary.get("c_repaired_semantic_mismatch_count") == C_MISMATCH_COUNT
        and graph_summary.get("c_repaired_infrastructure_failure_count") == 0
        and graph_summary.get("original_canonical_native_restored") is True
        and graph_summary.get("performance") == "NOT MEASURED"
        and graph_summary.get("memory") == "NOT MEASURED"
        and graph_summary.get("final_holdout_opened") is False
        and graph_summary.get("winner_selected") is False,
        "preserve the genuine current C result without declaring a winner",
    )
    for key, expected in (
        ("source", V23_OWNERS["source"]),
        ("inputs", V23_OWNERS["inputs"]),
        ("svg", V23_OWNERS["svg"]),
    ):
        item = graph_summary.get(key)
        require(
            type(item) is dict
            and item.get("path") == expected[0]
            and item.get("sha256") == expected[1],
            "reject changed current V23 graph owner: " + key,
        )
    for document, label in (
        (graph_inputs.get("previous_overview"), "V23 input history"),
        (graph_summary.get("previous_overview"), "V23 graph history"),
    ):
        require(type(document) is dict,
                "require all four independently published V22 owners: " + label)
        for key, expected in V22_OWNERS.items():
            item = document.get(key)
            require(
                type(item) is dict
                and item.get("path") == expected[0]
                and item.get("sha256") == expected[1],
                "reject a changed complete V22 predecessor: " + label + "/" + key,
            )
    require(
        graph_svg
        == renderer.make_svg(
            snapshot,
            V23_OWNERS["source"][1],
            V23_OWNERS["inputs"][1],
        ),
        "independently reproduce the exact published readable V23 graph",
    )
    rust = [
        item for item in graph_summary.get("families", [])
        if type(item) is dict and item.get("family") == FAMILY
    ]
    require(len(rust) == 1, "require one independently owned historical Rust family")
    historic = rust[0].get("correctness_evidence")
    require(
        rust[0].get("correctness") == "FAILED; NOT QUALIFIED"
        and rust[0].get("performance") == "NOT MEASURED"
        and type(historic) is dict
        and historic.get("actual_semantic_mismatch_count") == RUST_MISMATCH_COUNT
        and historic.get("verified_passing_case_executions") == RUST_PASS_COUNT
        and historic.get("qualified_case_executions") == 0
        and historic.get("passed_suite_count") == 8
        and historic.get("failed_suite_ids") == list(RUST_FAILED_SUITES)
        and type(rust[0].get("subordinate_evidence")) is list
        and len(rust[0]["subordinate_evidence"]) == 12
        and rust[0].get("owned_sources")
        == [
            {"path": path, "sha256": data[0]}
            for path, data in sorted(RUST_OWNERS.items())
        ],
        "preserve all original Rust failures, successes, and nine independent owners",
    )
    c_observed: dict[str, dict[str, Any]] = {}
    c_campaign = validate_c_campaign(
        graph_inputs.get("current_complete_c_campaign"),
        snapshot,
        c_observed,
    )
    claims: dict[str, str] = {}
    collect_evidence(graph_inputs, claims)
    collect_evidence(graph_summary, claims)
    require(
        len(claims) == GRAPH_EVIDENCE_CLAIM_COUNT
        and all(
            claims.get(path) == owner["sha256"]
            for path, owner in c_observed.items()
        ),
        "preserve every unique signed V23 evidence claim and all thirty C owners",
    )
    for path, sha in sorted(claims.items()):
        if path not in c_observed:
            _, verified[path] = read_owned(
                path, sha, private=True, maximum=MAX_COMPRESSED,
            )
        else:
            verified[path] = c_observed[path]
    reference_paths = dict(claims)
    for name in ("source", "inputs"):
        path, sha, _ = V23_OWNERS[name]
        require(path not in reference_paths,
                "never silently count a graph evidence reference twice")
        require(
            verified[path]["sha256"] == sha,
            "independently authenticate each remaining signed graph owner",
        )
        reference_paths[path] = sha
    require(
        len(reference_paths) == GRAPH_REFERENCE_COUNT,
        "require all 138 signed evidence paths and both real graph references",
    )
    for path, (sha, count) in sorted(RUST_OWNERS.items()):
        _, after = read_owned(path, sha, count)
        require(
            after == verified[path],
            "never mutate an original first-party Rust owner during verification",
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
        "historical_evidence_owner_count": GRAPH_OWNER_COUNT,
        "historical_authenticated_reference_count": GRAPH_REFERENCE_COUNT,
        "direct_signed_graph_evidence_owner_count": len(claims),
        "direct_authenticated_reference_path_count": len(reference_paths),
        "independently_authenticated_current_graph_reference_count": 2,
        "actual_c_campaign": c_campaign,
        "rust_historical_semantic_mismatch_count": RUST_MISMATCH_COUNT,
        "rust_historical_verified_passing_case_count": RUST_PASS_COUNT,
        "rust_historical_failed_suite_ids": list(RUST_FAILED_SUITES),
        "rust_original_source_owner_count": len(RUST_OWNERS),
        "rust_package": package,
        "preserved_v9_root_prefix": ROOT_PREFIX,
        "future_phase_count": len(PHASES),
        "future_unchanged_sources_per_phase": 7,
        "future_bridge_overlays_per_phase": 1,
        "future_public_overlays_per_phase": 1,
        "future_complete_sources_per_phase": len(RUST_OWNERS),
        "bridge_derived_source_sha256": BRIDGE_DERIVED_SHA256,
        "bridge_derived_source_bytes": BRIDGE_DERIVED_BYTES,
        "public_derived_source_sha256": PUBLIC_DERIVED_SHA256,
        "public_derived_source_bytes": PUBLIC_DERIVED_BYTES,
        "derived_sources_materialized": False,
        "future_compiler_process_count": 2 * len(PROCESS_NAMES),
        "authenticated_owner_count": len(verified),
        **boundary(),
    }
    return result, {
        "v9": v9,
        "bridge": bridge,
        "public": public,
        "bridge_bytes": derived_bridge,
        "public_bytes": derived_public,
        "originals": source_bytes,
    }


_ACTIVE: dict[str, Any] | None = None
_APPLIED: set[tuple[str, str]] = set()


def copy_dual_snapshot(
    workdir: str,
    family: str,
    phase: str,
    sources: dict[str, bytes],
) -> dict[str, dict[str, Any]]:
    require(_ACTIVE is not None, "require one independently pinned explicit V10 build")
    state = _ACTIVE
    v9 = state["v9"]
    kernel = state["kernel"]
    checked_root(workdir)
    require(
        family == FAMILY
        and phase in PHASES
        and type(sources) is dict
        and set(sources) == set(RUST_OWNERS)
        and (workdir, phase) not in _APPLIED,
        "require a fresh exact two-overlay Rust phase and nine original owners",
    )
    paths = v9.phase_paths(workdir, family, phase)
    for peer in PHASES:
        peer_paths = v9.phase_paths(workdir, family, peer)
        for item in (
            peer_paths["base"],
            peer_paths["source"],
            peer_paths["source"] / "candidates",
            peer_paths["source"] / "candidates/rust",
        ):
            found = os.lstat(item)
            require(
                stat.S_ISDIR(found.st_mode)
                and stat.S_IMODE(found.st_mode) == 0o700
                and found.st_uid == os.geteuid(),
                "precreate both genuine owner-only Rust peers before any overlay",
            )
    for path, (sha, count) in sorted(RUST_OWNERS.items()):
        require(
            type(sources[path]) is bytes
            and digest(sources[path]) == sha
            and len(sources[path]) == count,
            "reject changed original Rust source: " + path,
        )
    copies: dict[str, dict[str, Any]] = {}
    for path in sorted(RUST_OWNERS):
        if path in (BRIDGE_PATH, PUBLIC_PATH):
            continue
        target = paths["source"] / path
        kernel.mkdir_private(target.parent)
        owner = kernel.write_fresh(target, sources[path], synchronize=False)
        owner["path"] = v9.sanitized(owner["path"], workdir, family)
        copies[path] = owner
    require(len(copies) == 7, "leave both exclusive overlay destinations absent")
    bridge_result = state["bridge"].apply_private(
        str(paths["source"]), state["bridge_bytes"],
    )
    public_result = state["public"].apply_private(
        str(paths["source"]), state["public_bytes"],
    )
    require(
        type(bridge_result) is dict
        and bridge_result.get("status") == "PASS"
        and bridge_result.get("phase") == phase
        and bridge_result.get("source_apply_count") == 1
        and bridge_result.get("derived_sha256") == BRIDGE_DERIVED_SHA256
        and bridge_result.get("derived_bytes") == BRIDGE_DERIVED_BYTES
        and bridge_result.get("candidate_original_modified") is False,
        "apply the exact independently frozen private bridge once",
    )
    require(
        type(public_result) is dict
        and public_result.get("status") == "PASS"
        and public_result.get("phase") == phase
        and public_result.get("source_apply_count") == 1
        and public_result.get("derived_source_sha256") == PUBLIC_DERIVED_SHA256
        and public_result.get("derived_source_bytes") == PUBLIC_DERIVED_BYTES
        and public_result.get("original_candidate_modified") is False,
        "apply the exact independently frozen private public adapter once",
    )
    for path, expected_sha, expected_size, expected_raw, overlay in (
        (
            BRIDGE_PATH, BRIDGE_DERIVED_SHA256, BRIDGE_DERIVED_BYTES,
            state["bridge_bytes"], bridge_result,
        ),
        (
            PUBLIC_PATH, PUBLIC_DERIVED_SHA256, PUBLIC_DERIVED_BYTES,
            state["public_bytes"], public_result,
        ),
    ):
        owner, raw = kernel.authenticate_file(
            paths["source"] / path,
            expected=expected_sha,
            maximum=MAX_SOURCE,
            exact_size=expected_size,
            capture=True,
        )
        require(
            type(raw) is bytes
            and raw == expected_raw
            and stat.S_IMODE(os.lstat(paths["source"] / path).st_mode) == 0o600,
            "authenticate the complete exclusive same-inode private overlay: " + path,
        )
        copies[path] = {
            "path": v9.sanitized(owner["path"], workdir, family),
            "sha256": owner["sha256"],
            "bytes": owner["size_bytes"],
            "device": owner["device"],
            "inode": owner["inode"],
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "source_overlay": overlay,
        }
    require(set(copies) == set(RUST_OWNERS),
            "close every seven-original-plus-two-overlay private Rust source")
    for path, (sha, count) in sorted(RUST_OWNERS.items()):
        read_owned(path, sha, count)
    _APPLIED.add((workdir, phase))
    return copies


def verify_reproduced_phases(
    v9: types.ModuleType,
    v7: types.ModuleType,
    workdir: str,
    phases: list[dict[str, Any]],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    require(
        type(phases) is list
        and len(phases) == 2
        and [item.get("name") for item in phases] == list(PHASES)
        and type(steps) is list
        and len(steps) == 2 * len(PROCESS_NAMES),
        "require both real fourteen-process first-party Rust source phases",
    )
    identities: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        require(
            type(owners) is dict and set(owners) == set(RUST_OWNERS),
            "preserve nine independently identified private Rust owners",
        )
        for path, (sha, count) in sorted(RUST_OWNERS.items()):
            if path == BRIDGE_PATH:
                sha, count = BRIDGE_DERIVED_SHA256, BRIDGE_DERIVED_BYTES
            elif path == PUBLIC_PATH:
                sha, count = PUBLIC_DERIVED_SHA256, PUBLIC_DERIVED_BYTES
            item = owners.get(path)
            require(
                type(item) is dict
                and item.get("sha256") == sha
                and item.get("bytes") == count
                and type(item.get("device")) is int
                and type(item.get("inode")) is int
                and (item["device"], item["inode"]) not in identities,
                "reject omitted, linked, substituted, or reused phase owner: " + path,
            )
            identities.add((item["device"], item["inode"]))
        for path in (BRIDGE_PATH, PUBLIC_PATH):
            applied = owners[path].get("source_overlay")
            expected_sha = (
                BRIDGE_DERIVED_SHA256 if path == BRIDGE_PATH else PUBLIC_DERIVED_SHA256
            )
            reported_sha = (
                applied.get("derived_sha256")
                if path == BRIDGE_PATH
                else applied.get("derived_source_sha256")
            ) if type(applied) is dict else None
            require(
                type(applied) is dict
                and applied.get("status") == "PASS"
                and applied.get("phase") == PHASES[index]
                and applied.get("source_apply_count") == 1
                and reported_sha == expected_sha,
                "require exactly one genuine independent phase overlay: " + path,
            )
    pids: set[int] = set()
    for index, step in enumerate(steps):
        require(
            type(step) is dict
            and step.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
            and type(step.get("pid")) is int
            and step["pid"] > 0
            and step["pid"] not in pids
            and step.get("exit_status") == 0,
            "require 28 actual distinct successful compiler and inspection processes",
        )
        pids.add(step["pid"])
    outputs: dict[str, Any] = {}
    comparisons: dict[str, Any] = {}
    for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
        left = phases[0].get("native_outputs", {}).get(role)
        right = phases[1].get("native_outputs", {}).get(role)
        require(
            type(left) is dict
            and type(right) is dict
            and left.get("file_name") == right.get("file_name") == filename
            and left.get("sha256") == right.get("sha256")
            and left.get("size_bytes") == right.get("size_bytes")
            and left.get("path") != right.get("path")
            and (left.get("device"), left.get("inode"))
            != (right.get("device"), right.get("inode"))
            and left.get("audit") == right.get("audit"),
            "reject a borrowed or irreproducible first-party Rust ELF: " + role,
        )
        first = v9._RAW_PHASE_ELF.get((workdir, PHASES[0], role))
        second = v9._RAW_PHASE_ELF.get((workdir, PHASES[1], role))
        require(
            type(first) is bytes
            and type(second) is bytes
            and digest(first) == left["sha256"]
            and digest(second) == right["sha256"]
            and first == second,
            "compare complete real bytes from both independent phases: " + role,
        )
        compared = v7.compare_owned_elf64(first, second)
        require(
            type(compared) is dict and compared.get("byte_identical") is True,
            "require reproducible real first-party Rust ELF evidence: " + role,
        )
        comparisons[role] = compared
        outputs[role] = {
            "file_name": filename,
            "sha256": left["sha256"],
            "size_bytes": left["size_bytes"],
            "fresh_independent_inode_count": 2,
            "audit": left["audit"],
        }
    for path, (sha, count) in sorted(RUST_OWNERS.items()):
        read_owned(path, sha, count)
    return {
        "status": "PASS",
        "independent_fresh_phase_count": 2,
        "source_owners_per_phase": 9,
        "unchanged_source_owners_per_phase": 7,
        "bridge_overlay_count": 2,
        "public_overlay_count": 2,
        "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
        "public_derived_sha256": PUBLIC_DERIVED_SHA256,
        "byte_identical": True,
        "unique_process_count": len(steps),
        "native_role_count": 2,
        "raw_elf_comparisons": comparisons,
        "native_outputs": outputs,
        "prebuilt_artifact_count": 0,
        "native_libraries_loaded": 0,
        "original_sources_modified": False,
    }


def checked_label(value: Any) -> str:
    require(
        type(value) is str
        and 0 < len(value) <= 48
        and all(item.isascii() and (item.isalnum() or item in "-_") for item in value),
        "require one bounded explicit independently owned build label",
    )
    return value


def evidence_names(label: str, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "require an exact actual pass or failure")
    base = "native-source-build-v10-rust-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def publish_report(kernel: types.ModuleType, report: dict[str, Any]) -> dict[str, Any]:
    require(type(report) is dict and report.get("status") in ("PASS", "FAIL"),
            "publish only one real independent build result")
    label = checked_label(report.get("label"))
    archive_name, receipt_name = evidence_names(label, report["status"] == "FAIL")
    directory = ROOT / EVIDENCE_PATH
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT, "bound complete independently recorded build data")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_REPORT, "bound authentic real build evidence")
    published = kernel.write_fresh(directory / archive_name, archive, synchronize=True)
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
        "phase_one_manifest_sha256": PHASE_ONE[1],
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": published["sha256"],
        "archive_bytes": published["bytes"],
        "archive_publication": published,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
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
    require(len(receipt_raw) <= MAX_SOURCE, "bound independently signed build receipt")
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
        "archive_sha256": published["sha256"],
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
    global _ACTIVE
    context, state = verify_context(
        arguments.source_sha256,
        arguments.protocol_sha256,
        arguments.contract_sha256,
    )
    label = checked_label(arguments.label)
    expected = {
        path + "=" + sha
        for path, (sha, _size) in RUST_OWNERS.items()
    }
    require(
        type(arguments.owned_source_sha256) is list
        and len(arguments.owned_source_sha256) == len(RUST_OWNERS)
        and set(arguments.owned_source_sha256) == expected,
        "explicitly pin all nine real original Rust source owners before building",
    )
    v9 = state["v9"]
    v7 = v9.load_frozen_module(
        "_rebar_phase2_exact_frozen_v10_rust_build_v7",
        v9.V7_OWNERS["source"],
    )
    kernel = v7.load_frozen_v4()
    require(_ACTIVE is None, "reject reused, nested, or substituted native build state")
    state["kernel"] = kernel
    _ACTIVE = state
    v9.install_v9_build_kernel(v7, kernel)
    kernel.copy_snapshot = copy_dual_snapshot
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
                v7, kernel, workdir, phase, result, steps,
            )
            completed.append(result)
        reproduction = verify_reproduced_phases(
            v9, v7, workdir, completed, steps,
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
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "bridge_overlay_apply_count": len(_APPLIED),
            "public_overlay_apply_count": len(_APPLIED),
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
        require(len(steps) == 28 and len(_APPLIED) == 2,
                "require all 28 real processes and both complete private phases")
        return publish_report(kernel, report)
    except Exception as error:
        for path, (sha, count) in sorted(RUST_OWNERS.items()):
            read_owned(path, sha, count)
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
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "bridge_overlay_apply_count": sum(
                (workdir, phase) in _APPLIED for phase in PHASES
            ),
            "public_overlay_apply_count": sum(
                (workdir, phase) in _APPLIED for phase in PHASES
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
    options = parser.parse_args(arguments)
    if options.self_test:
        require(
            all(
                getattr(options, name) is None
                for name in (
                    "source_sha256", "protocol_sha256", "contract_sha256",
                    "label", "owned_source_sha256",
                )
            ),
            "a synthetic source-only test never authorizes a real owner or build",
        )
        return options
    checked_digest(options.source_sha256, "V10 source")
    checked_digest(options.protocol_sha256, "V10 protocol")
    if options.emit_contract:
        require(
            options.contract_sha256 is None
            and options.label is None
            and options.owned_source_sha256 is None,
            "contract emission cannot read, publish, apply, or build",
        )
        return options
    checked_digest(options.contract_sha256, "V10 contract")
    if options.verify_context:
        require(
            options.label is None and options.owned_source_sha256 is None,
            "read-only verification cannot select a label or authorize a build",
        )
        return options
    checked_label(options.label)
    require(
        type(options.owned_source_sha256) is list
        and len(options.owned_source_sha256) == len(RUST_OWNERS),
        "actual building requires all nine independently pinned Rust owners",
    )
    return options


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
                    all(count == 0 for count in effects.values()),
                    "pure contract emission attempted a real source-only effect",
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
        require(len(raw) <= MAX_REPORT, "reject an unbounded Rust V10 result")
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
