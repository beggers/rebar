#!/usr/bin/env python3
"""Freeze a first-party Rust engine and private bridge before any V9 build."""

from __future__ import annotations

import base64
import builtins
import copy
import ctypes
import gzip
import hashlib
import importlib
import io
import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import types
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/reproduce_owned_native_source_build_v9.py"
PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V9.md"
CONTRACT_RELATIVE = "oracle/phase2/native-source-build-v9.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-native-source-build-v9"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
WORK_PREFIX = "rebar-phase2-native-build-v9-"
FAMILY = "rust"
PHASES = ("reference-a", "reference-b")
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
ENGINE_NAME = "_rust_engine.so"
BRIDGE_NAME = "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
PINNED_RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
PINNED_CARGO = RUST_TOOLCHAIN + "/bin/cargo"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48

P0_MANIFEST = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
V7_OWNERS = {
    "source": (
        "tools/reproduce_owned_native_source_build_v7.py",
        "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
        300624,
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md",
        "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
        8063,
    ),
    "contract": (
        "oracle/phase2/native-source-build-v7.json",
        "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
        28924,
    ),
}
C_V8_OWNERS = {
    "source": (
        "tools/reproduce_owned_native_source_build_v8.py",
        "afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4",
        63656,
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V8.md",
        "376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2",
        4498,
    ),
    "contract": (
        "oracle/phase2/native-source-build-v8.json",
        "7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b",
        6207,
    ),
}
REPAIR_OWNERS = {
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
RUST_OWNERS = {
    "candidates/rust_candidate.py": (
        "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        31151,
    ),
    "candidates/rust/py_bridge.c": (
        "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        175676,
    ),
    "candidates/rust/Cargo.toml": (
        "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
        225,
    ),
    "candidates/rust/Cargo.lock": (
        "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
        167,
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
}

ORIGINAL_PATH = "candidates/rust/py_bridge.c"
ORIGINAL_SHA256 = "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b"
ORIGINAL_BYTES = 175676
ADAPTER_PATH = "candidates/rust_candidate.py"
ADAPTER_SHA256 = "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"
ADAPTER_BYTES = 31151
DERIVED_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
DERIVED_BYTES = 176118
OLD_BLOCK = b"""    RustSubject subject;
    if (!rust_subject_open(&subject, pattern_value, value, 1)) return NULL;
    int callback = PyCallable_Check(replacement);
    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (!callback) {
        if (rust_replacement_cache(pattern, templates, replacement, value, (Py_ssize_t)subject.length, &raw, &tokens) < 0) {
            rust_subject_release(&subject);
            return NULL;
        }
    }
"""
NEW_BLOCK = b"""    RustSubject subject = {0};
    int callback = PyCallable_Check(replacement);
    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (!callback) {
        Py_ssize_t validation_length = 0;
        if (PyUnicode_Check(value)) {
            validation_length = PyUnicode_GET_LENGTH(value);
        } else if (PyBytes_Check(value)) {
            validation_length = PyBytes_GET_SIZE(value);
        } else if (PyByteArray_Check(value)) {
            validation_length = PyByteArray_GET_SIZE(value);
        }
        if (rust_replacement_cache(pattern, templates, replacement, value, validation_length, &raw, &tokens) < 0) {
            Py_XDECREF(raw);
            Py_XDECREF(tokens);
            return NULL;
        }
    }
    if (!rust_subject_open(&subject, pattern_value, value, 1)) {
        Py_XDECREF(raw);
        Py_XDECREF(tokens);
        return NULL;
    }
"""

SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
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
    "candidate_imports": 0,
    "candidate_processes_started": 0,
    "clock_samples": 0,
    "compiler_processes_started": 0,
    "final_comparison_cases_generated": False,
    "final_comparison_planned_case_count": 4194304,
    "final_holdout_authorized": False,
    "hidden_cases_read": 0,
    "holdout": "NOT OPENED",
    "holdout_opened": False,
    "memory": "NOT MEASURED",
    "native_builds_started": 0,
    "native_libraries_loaded": 0,
    "network_requests": 0,
    "performance": "NOT MEASURED",
    "performance_files_read": 0,
    "qualified_candidate_count": 0,
    "reference_processes_started": 0,
    "source_apply_count": 0,
    "subinterpreter_isolation": "NOT MEASURED",
    "timing_trials_run": 0,
    "undefined_behavior": "NOT MEASURED",
    "winner_selected": False,
}


class BuildError(Exception):
    """An owned V9 source-freeze or actual build failed."""


class SourceOnlyError(BuildError):
    """A source-only control attempted an external effect."""


def require(condition: Any, reason: str) -> None:
    if not condition:
        raise BuildError(reason)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only genuine complete bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("require one complete finite canonical JSON record") from error


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "require an exact lowercase SHA-256: " + label,
    )
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512, "invalid owner path")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute() and str(parsed) == value
        and all(piece not in ("", ".", "..") for piece in parsed.parts)
        and len(parsed.parts) <= 12,
        "require a canonical repository-relative, non-traversing owner",
    )
    return value


def read_owned(
    relative: str, digest: str, size: int | None = None,
    *, maximum: int = MAX_SOURCE_BYTES,
) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    checked_digest(digest, relative)
    require(
        type(maximum) is int and 0 < maximum <= MAX_ARCHIVE_BYTES
        and (size is None or type(size) is int and 0 <= size <= maximum),
        "bound every complete authenticated source owner",
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
    descriptor: int | None = None
    try:
        for component in PurePosixPath(relative).parts[:-1]:
            following = os.open(
                component, flags | getattr(os, "O_DIRECTORY", 0), dir_fd=directory,
            )
            os.close(directory)
            directory = following
        descriptor = os.open(
            PurePosixPath(relative).parts[-1], flags, dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and before.st_size <= maximum
            and (size is None or before.st_size == size),
            "reject a non-regular, changed, oversized, or incomplete owner: "
            + relative,
        )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, maximum + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            require(total <= maximum, "an authenticated owner exceeded its bound")
            chunks.append(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require(
            len(raw) == before.st_size == after.st_size
            and (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_ctime_ns)
            and sha256(raw) == digest,
            "reject a substituted or changed frozen source owner: " + relative,
        )
        return raw, {
            "path": relative, "sha256": digest, "bytes": len(raw),
            "device": before.st_dev, "inode": before.st_ino,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def expected_contract() -> dict[str, Any]:
    def owner(item: tuple[str, str, int]) -> dict[str, Any]:
        return {"path": item[0], "sha256": item[1], "bytes": item[2]}

    return {
        "schema": CONTRACT_SCHEMA,
        "version": 9,
        "phase": "RUST SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "family": FAMILY,
        "oracle": {
            "case_execution_count": 31237,
            "implementation": "CPython",
            "manifest": owner(P0_MANIFEST),
            "private_waiver_count": 13,
            "suite_count": 13,
            "suite_ids": list(SUITE_IDS),
            "version": "3.14.6",
            "python": {"path": PINNED_PYTHON, "sha256": PINNED_PYTHON_SHA256},
        },
        "source_baseline": {
            "candidate_source_mutation": "FORBIDDEN",
            "family_count": 6,
            "original_source_owner_count": 25,
            "rust_source_owner_count": 9,
            "rust_sources": [
                {"path": path, "sha256": item[0], "bytes": item[1]}
                for path, item in sorted(RUST_OWNERS.items())
            ],
            "original_bridge": {
                "path": ORIGINAL_PATH, "sha256": ORIGINAL_SHA256,
                "bytes": ORIGINAL_BYTES, "modified": False,
            },
            "original_adapter": {
                "path": ADAPTER_PATH, "sha256": ADAPTER_SHA256,
                "bytes": ADAPTER_BYTES, "modified": False,
            },
            "v7": {name: owner(item) for name, item in sorted(V7_OWNERS.items())},
            "independent_c_v8": {
                name: owner(item) for name, item in sorted(C_V8_OWNERS.items())
            },
            "c_v8_build_run_by_v9": False,
        },
        "first_party_rust_source_repair": {
            "owners": {
                name: owner(item) for name, item in sorted(REPAIR_OWNERS.items())
            },
            "derived_bridge": {
                "path": ORIGINAL_PATH, "sha256": DERIVED_SHA256,
                "bytes": DERIVED_BYTES,
                "materialized_during_source_freeze": False,
            },
            "old_block": {
                "sha256": sha256(OLD_BLOCK), "bytes": len(OLD_BLOCK),
                "occurrence_count_before": 1, "occurrence_count_after": 0,
            },
            "new_block": {
                "sha256": sha256(NEW_BLOCK), "bytes": len(NEW_BLOCK),
                "occurrence_count_before": 0, "occurrence_count_after": 1,
            },
            "transformation": "EXACTLY ONE ANCHORED FIRST-PARTY RUST BRIDGE BLOCK",
            "subject_failure_cleanup":
                "ONE RAW DECREF; ONE TOKEN DECREF; NO SUBJECT DOUBLE RELEASE",
            "template_failure_cleanup":
                "NO SUBJECT ACQUIRED; ONE RAW/TOKEN CLEANUP",
            "successful_subject_cleanup":
                "EXISTING SINGLE SUCCESSFUL BUFFER RELEASE; UNCHANGED",
            "error_subject_cleanup":
                "EXISTING SINGLE ERROR-LABEL BUFFER RELEASE; UNCHANGED",
            "callable_semantics": "PRESERVED",
            "pybuf_simple_semantics": "PRESERVED",
            "apply_function": "apply_private",
            "application": "EXACTLY ONCE IN EACH FUTURE PRIVATE SOURCE PHASE",
            "existing_destination": "FORBIDDEN",
        },
        "rust_package": {
            "name": "rebar-rust-continuation",
            "version": "0.1.0",
            "edition": "2024",
            "rust_version": "1.85",
            "package_count": 1,
            "external_dependency_count": 0,
            "crate_type": ["cdylib"],
            "publish": False,
            "release_opt_level": 3,
            "release_lto": True,
            "release_codegen_units": 1,
            "release_panic": "abort",
            "lock_format_version": 4,
            "network": "FORBIDDEN",
        },
        "published_history": {
            "authenticated_digest_addressed_history_paths": 76,
            "authoritative_counted_evidence_owner_count": 71,
            "historical_compiler_process_count": 169,
            "current_active_target_count": 0,
            "current_tested_candidate_family_count": 5,
            "rust_actual_semantic_mismatch_count": 2042,
            "go_full_campaign_status": "FAIL",
            "go_full_campaign_suite_count": 13,
            "go_full_campaign_semantic_mismatch_count": 4518,
            "go_full_campaign_infrastructure_failure_count": 4,
            "go_restoration_status": "PASS",
            "qualified_candidate_count": 0,
        },
        "future_build_policy": {
            "explicit_build_required": True,
            "family": FAMILY,
            "root_parent": "/tmp",
            "root_prefix": WORK_PREFIX + FAMILY + "-",
            "phase_names": list(PHASES),
            "both_peer_phases_precreated_before_first_apply": True,
            "nested_candidates_rust_precreated": True,
            "directory_mode": "0700",
            "source_file_mode": "0600",
            "source_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "original_sources_per_phase": 8,
            "repaired_bridges_per_phase": 1,
            "private_compiler_input_sha256": DERIVED_SHA256,
            "rustc": PINNED_RUSTC,
            "cargo": PINNED_CARGO,
            "compiler": PINNED_GCC,
            "elf_inspector": PINNED_READELF,
            "python_include": PYTHON_INCLUDE,
            "engine_name": ENGINE_NAME,
            "bridge_name": BRIDGE_NAME,
            "cargo_flags": [
                "build", "--manifest-path", "--release",
                "--locked", "--offline", "--frozen", "--target-dir",
            ],
            "gcc_flags": [
                "-pthread", "-std=c11", "-shared", "-fPIC", "-O3",
                "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack",
                "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1",
            ],
            "cargo_net_offline": True,
            "independent_cargo_home": True,
            "independent_target": True,
            "phase_prefix_map_target": "/rebar-phase2-v6-owned-source",
            "bridge_runpath": "$ORIGIN",
            "process_names_per_phase": list(PROCESS_NAMES),
            "processes_per_phase": 14,
            "total_future_processes": 28,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "external_engine": "FORBIDDEN",
            "external_cargo_dependencies": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "network": "FORBIDDEN",
            "original_v4_reproducibility_verifier":
                "FORBIDDEN FOR DERIVED RUST BRIDGE",
            "raw_elf_forensics":
                "COMPLETE AUTHENTICATED RUST ENGINE AND C BRIDGE PHASE BYTES",
            "reproducibility":
                "EIGHT ORIGINAL OWNERS, DERIVED BRIDGE, AND BOTH COMPLETE RAW ELF FILES",
        },
        "future_evidence": {
            "directory": EVIDENCE_RELATIVE,
            "archive_prefix": "native-source-build-v9-rust-",
            "failure_suffix": "-failures",
            "archive_suffix": ".json.gz",
            "receipt_suffix": "-publication-receipt.json",
            "exclusive_creation": True,
            "file_fsync": True,
            "directory_fsync": True,
            "failure_preserved": True,
            "canonical_json": True,
            "gzip_single_member": True,
            "gzip_mtime": 0,
        },
        "phase_boundary": copy.deepcopy(BOUNDARY),
    }


def verify_rust_package() -> dict[str, Any]:
    manifest_path = "candidates/rust/Cargo.toml"
    lock_path = "candidates/rust/Cargo.lock"
    manifest_raw, _ = read_owned(
        manifest_path, *RUST_OWNERS[manifest_path],
    )
    lock_raw, _ = read_owned(lock_path, *RUST_OWNERS[lock_path])
    try:
        manifest = tomllib.loads(manifest_raw.decode("utf-8", "strict"))
        lock = tomllib.loads(lock_raw.decode("utf-8", "strict"))
    except (tomllib.TOMLDecodeError, UnicodeError, ValueError) as error:
        raise BuildError(
            "reject altered or invalid frozen Rust package ownership"
        ) from error
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
            name not in manifest
            for name in (
                "dependencies", "dev-dependencies", "build-dependencies",
                "workspace", "patch", "replace",
            )
        )
        and lock.get("version") == 4
        and type(packages) is list
        and len(packages) == 1
        and type(packages[0]) is dict
        and packages[0].get("name") == "rebar-rust-continuation"
        and packages[0].get("version") == "0.1.0"
        and "dependencies" not in packages[0],
        "require exactly one owned offline Rust package and zero dependencies",
    )
    return {
        "status": "PASS",
        "package_count": 1,
        "external_dependency_count": 0,
        "manifest_sha256": RUST_OWNERS[manifest_path][0],
        "lock_sha256": RUST_OWNERS[lock_path][0],
        "cargo_network_requests": 0,
    }

def validate_contract(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict and canonical(value) == canonical(expected_contract()),
        "reject an altered, weakened, incomplete, or non-frozen V9 contract",
    )
    return value


class SourceOnlyWall:
    """Block every filesystem, process, clock, network, and loader effect."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked_effect_count = 0

    def forbidden(self, *_args: Any, **_kwargs: Any) -> Any:
        self.blocked_effect_count += 1
        raise SourceOnlyError("a V9 source-only control attempted an external effect")

    def __enter__(self) -> "SourceOnlyWall":
        targets = (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "system"),
            (os, "popen"), (os, "mkdir"), (os, "makedirs"), (os, "remove"),
            (os, "unlink"), (os, "rename"), (os, "replace"), (os, "putenv"),
            (os, "unsetenv"), (subprocess, "Popen"), (subprocess, "run"),
            (subprocess, "call"), (subprocess, "check_call"),
            (subprocess, "check_output"), (socket, "socket"),
            (socket, "create_connection"), (tempfile, "mkdtemp"),
            (tempfile, "mkstemp"), (threading.Thread, "start"),
            (ctypes, "CDLL"), (ctypes, "PyDLL"), (time, "time"),
            (time, "time_ns"), (time, "monotonic"), (time, "monotonic_ns"),
            (time, "perf_counter"), (time, "perf_counter_ns"),
            (importlib, "import_module"),
        )
        for owner, name in targets:
            if hasattr(owner, name):
                self.previous.append((owner, name, getattr(owner, name)))
                setattr(owner, name, self.forbidden)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> bool:
        for owner, name, original in reversed(self.previous):
            setattr(owner, name, original)
        return False


def synthetic_phase_gate(phases: Any, steps: Any) -> dict[str, Any]:
    require(type(phases) is list and len(phases) == 2,
            "require exactly two synthetic Rust source phases")
    require(type(steps) is list and len(steps) == 28,
            "require exactly 28 planned synthetic Rust process roles")
    identities: set[tuple[int, int]] = set()
    output_identities: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        require(
            type(phase) is dict
            and phase.get("name") == PHASES[index]
            and phase.get("source_apply_count") == 1
            and phase.get("source_mode") == 0o600
            and phase.get("directory_mode") == 0o700,
            "reject a missing, repeated, non-private, or foreign Rust phase",
        )
        owners = phase.get("owners")
        require(
            type(owners) is dict and set(owners) == set(RUST_OWNERS),
            "require all nine independent Rust source owners",
        )
        for path, (original_digest, original_size) in sorted(RUST_OWNERS.items()):
            item = owners.get(path)
            digest = DERIVED_SHA256 if path == ORIGINAL_PATH else original_digest
            size = DERIVED_BYTES if path == ORIGINAL_PATH else original_size
            require(
                type(item) is dict
                and item.get("sha256") == digest
                and item.get("bytes") == size
                and type(item.get("identity")) is tuple
                and len(item["identity"]) == 2
                and all(type(value) is int and value > 0 for value in item["identity"])
                and item["identity"] not in identities,
                "reject missing, original, borrowed, repeated, or linked Rust source",
            )
            identities.add(item["identity"])
        outputs = phase.get("outputs")
        require(
            type(outputs) is dict and set(outputs) == {"engine", "bridge"},
            "require both distinct actual Rust and native bridge output roles",
        )
        for role in ("engine", "bridge"):
            item = outputs[role]
            require(
                type(item) is dict
                and item.get("name")
                == (ENGINE_NAME if role == "engine" else BRIDGE_NAME)
                and type(item.get("sha256")) is str
                and len(item["sha256"]) == 64
                and type(item.get("identity")) is tuple
                and item["identity"] not in output_identities,
                "reject an omitted, shared, foreign, or substituted native Rust output",
            )
            output_identities.add(item["identity"])
    require(
        all(
            phases[0]["outputs"][role]["sha256"]
            == phases[1]["outputs"][role]["sha256"]
            for role in ("engine", "bridge")
        ),
        "require byte-identical synthetic Rust engine and bridge outputs",
    )
    pids: set[int] = set()
    for index, step in enumerate(steps):
        require(
            type(step) is dict
            and step.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
            and step.get("phase") == PHASES[index // len(PROCESS_NAMES)]
            and type(step.get("pid")) is int
            and step["pid"] > 0
            and step["pid"] not in pids
            and step.get("exit_status") == 0,
            "reject reordered, omitted, forged, repeated, or failed Rust roles",
        )
        pids.add(step["pid"])
    return {
        "independent_phase_count": 2,
        "synthetic_source_owner_count_per_phase": 9,
        "synthetic_native_output_count_per_phase": 2,
        "unique_process_count": 28,
    }

def expect_rejected(function: Any, *arguments: Any) -> None:
    try:
        function(*arguments)
    except (BuildError, TypeError, ValueError, KeyError, IndexError):
        return
    raise BuildError("a negative V9 source-freeze control was silently accepted")


def self_test() -> dict[str, Any]:
    with SourceOnlyWall() as wall:
        frozen = validate_contract(expected_contract())
        ordered = sorted(RUST_OWNERS)
        phases = []
        for phase_index, phase_name in enumerate(PHASES):
            owners = {}
            for owner_index, path in enumerate(ordered):
                digest, size = RUST_OWNERS[path]
                owners[path] = {
                    "sha256": DERIVED_SHA256 if path == ORIGINAL_PATH else digest,
                    "bytes": DERIVED_BYTES if path == ORIGINAL_PATH else size,
                    "identity": (1, 100 + phase_index * len(ordered) + owner_index),
                }
            phases.append({
                "name": phase_name,
                "source_apply_count": 1,
                "source_mode": 0o600,
                "directory_mode": 0o700,
                "owners": owners,
                "outputs": {
                    "engine": {
                        "name": ENGINE_NAME,
                        "sha256": "a" * 64,
                        "identity": (1, 1000 + phase_index),
                    },
                    "bridge": {
                        "name": BRIDGE_NAME,
                        "sha256": "b" * 64,
                        "identity": (1, 2000 + phase_index),
                    },
                },
            })
        steps = [
            {
                "name": role,
                "phase": phase,
                "pid": 10000 + phase_index * len(PROCESS_NAMES) + role_index,
                "exit_status": 0,
            }
            for phase_index, phase in enumerate(PHASES)
            for role_index, role in enumerate(PROCESS_NAMES)
        ]
        synthetic_phase_gate(phases, steps)
        controls = 0
        mutations: list[tuple[tuple[str, ...], Any]] = [
            (("schema",), SCHEMA),
            (("version",), 8),
            (("phase",), "PASS"),
            (("family",), "c"),
            (("oracle", "case_execution_count"), 31236),
            (("oracle", "private_waiver_count"), 12),
            (("oracle", "suite_count"), 12),
            (("oracle", "version"), "3.14.5"),
            (("oracle", "implementation"), "PyPy"),
            (("source_baseline", "family_count"), 5),
            (("source_baseline", "original_source_owner_count"), 24),
            (("source_baseline", "rust_source_owner_count"), 8),
            (("source_baseline", "candidate_source_mutation"), "ALLOWED"),
            (("source_baseline", "c_v8_build_run_by_v9"), True),
            (("first_party_rust_source_repair", "apply_function"), "copy_snapshot"),
            (("first_party_rust_source_repair", "existing_destination"), "ALLOWED"),
            (("first_party_rust_source_repair", "application"), "ONCE"),
            (("rust_package", "package_count"), 2),
            (("rust_package", "external_dependency_count"), 1),
            (("rust_package", "publish"), True),
            (("rust_package", "network"), "ALLOWED"),
            (("rust_package", "release_lto"), False),
            (("published_history", "authenticated_digest_addressed_history_paths"), 71),
            (("published_history", "authoritative_counted_evidence_owner_count"), 76),
            (("published_history", "historical_compiler_process_count"), 168),
            (("published_history", "rust_actual_semantic_mismatch_count"), 0),
            (("published_history", "go_full_campaign_status"), "PASS"),
            (("published_history", "go_full_campaign_suite_count"), 12),
            (("published_history", "go_full_campaign_semantic_mismatch_count"), 0),
            (("published_history", "go_full_campaign_infrastructure_failure_count"), 0),
            (("published_history", "go_restoration_status"), "FAIL"),
            (("published_history", "qualified_candidate_count"), 1),
            (("future_build_policy", "root_parent"), "/"),
            (("future_build_policy", "root_prefix"),
             "rebar-phase2-native-build-v8-c-"),
            (("future_build_policy", "both_peer_phases_precreated_before_first_apply"),
             False),
            (("future_build_policy", "nested_candidates_rust_precreated"), False),
            (("future_build_policy", "directory_mode"), "0755"),
            (("future_build_policy", "source_file_mode"), "0644"),
            (("future_build_policy", "source_creation"), "O_CREAT"),
            (("future_build_policy", "original_sources_per_phase"), 7),
            (("future_build_policy", "repaired_bridges_per_phase"), 2),
            (("future_build_policy", "private_compiler_input_sha256"),
             ORIGINAL_SHA256),
            (("future_build_policy", "cargo_net_offline"), False),
            (("future_build_policy", "processes_per_phase"), 13),
            (("future_build_policy", "total_future_processes"), 27),
            (("future_build_policy", "external_engine"), "ALLOWED"),
            (("future_build_policy", "external_cargo_dependencies"), "ALLOWED"),
            (("future_build_policy", "fallback"), "ALLOWED"),
            (("future_build_policy", "network"), "ALLOWED"),
            (("future_build_policy", "original_v4_reproducibility_verifier"),
             "ALLOWED"),
            (("future_evidence", "exclusive_creation"), False),
            (("future_evidence", "file_fsync"), False),
            (("future_evidence", "directory_fsync"), False),
            (("future_evidence", "failure_preserved"), False),
        ]
        for path, replacement in mutations:
            changed = copy.deepcopy(frozen)
            cursor = changed
            for component in path[:-1]:
                cursor = cursor[component]
            cursor[path[-1]] = replacement
            expect_rejected(validate_contract, changed)
            controls += 1
        for key, value in BOUNDARY.items():
            if type(value) is bool:
                replacements = (not value, 1, None)
            elif type(value) is int:
                replacements = (value + 1, True, None)
            else:
                replacements = ("PASS", "MEASURED", None)
            for replacement in replacements:
                changed = copy.deepcopy(frozen)
                changed["phase_boundary"][key] = replacement
                expect_rejected(validate_contract, changed)
                controls += 1
        for phase_index in range(2):
            for path, (_digest, size) in sorted(RUST_OWNERS.items()):
                for key, replacement in (
                    ("sha256",
                     ORIGINAL_SHA256 if path == ORIGINAL_PATH else "f" * 64),
                    ("bytes", ORIGINAL_BYTES if path == ORIGINAL_PATH else size + 1),
                    ("identity",
                     phases[1 - phase_index]["owners"][path]["identity"]),
                ):
                    changed = copy.deepcopy(phases)
                    changed[phase_index]["owners"][path][key] = replacement
                    expect_rejected(synthetic_phase_gate, changed, steps)
                    controls += 1
            for role in ("engine", "bridge"):
                for key, replacement in (
                    ("name", "_foreign_regex.so"),
                    ("sha256", "f" * 64),
                    ("identity",
                     phases[1 - phase_index]["outputs"][role]["identity"]),
                ):
                    changed = copy.deepcopy(phases)
                    changed[phase_index]["outputs"][role][key] = replacement
                    expect_rejected(synthetic_phase_gate, changed, steps)
                    controls += 1
            for key, replacement in (
                ("name", "reference-c"),
                ("source_apply_count", 0),
                ("source_mode", 0o644),
                ("directory_mode", 0o755),
            ):
                changed = copy.deepcopy(phases)
                changed[phase_index][key] = replacement
                expect_rejected(synthetic_phase_gate, changed, steps)
                controls += 1
        for index in range(len(steps)):
            for key, replacement in (
                ("pid", steps[0]["pid"] if index else 0),
                ("exit_status", 1),
                ("name", "build_foreign_regex_engine"),
            ):
                changed = copy.deepcopy(steps)
                changed[index][key] = replacement
                expect_rejected(synthetic_phase_gate, phases, changed)
                controls += 1
        for forbidden in (
            lambda: builtins.open(
                "/tmp/rebar-v9-rust-self-test-forbidden", "wb",
            ),
            lambda: os.open(
                "/tmp/rebar-v9-rust-self-test-forbidden", os.O_RDONLY,
            ),
            lambda: subprocess.run([PINNED_CARGO, "--version"]),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(prefix=WORK_PREFIX),
            lambda: time.perf_counter_ns(),
            lambda: importlib.import_module("re"),
        ):
            expect_rejected(forbidden)
            controls += 1
        require(
            controls >= 250,
            "exercise complete Rust owner, process, and boundary controls",
        )
        require(
            wall.blocked_effect_count == 7,
            "block every attempted Rust source-only external effect",
        )
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 9,
            "status": "PASS",
            "negative_controls": controls,
            "blocked_effect_attempts": wall.blocked_effect_count,
            "synthetic_independent_phase_count": 2,
            "synthetic_source_owner_count_per_phase": 9,
            "synthetic_native_output_count_per_phase": 2,
            "synthetic_unique_process_count": 28,
            "frozen_contract": frozen,
            **copy.deepcopy(BOUNDARY),
            "filesystem_reads": 0,
            "filesystem_writes": 0,
            "processes_started": 0,
            "read_only": True,
        }

def load_frozen_module(
    name: str, owner: tuple[str, str, int],
) -> types.ModuleType:
    raw, _ = read_owned(owner[0], owner[1], owner[2])
    require(name not in sys.modules, "reject an imported or substituted frozen kernel")
    module = types.ModuleType(name)
    module.__dict__["__file__"] = str(ROOT / owner[0])
    module.__dict__["__package__"] = None
    exec(compile(raw, str(ROOT / owner[0]), "exec"), module.__dict__)
    return module


def verify_runtime() -> None:
    require(
        sys.executable == PINNED_PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and sys.version_info[:3] == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True,
        "use only isolated, bytecode-free, pinned CPython 3.14.6",
    )


def verify_context(arguments: dict[str, Any]) -> dict[str, Any]:
    verify_runtime()
    require(type(arguments) is dict,
            "require independently pinned V9 Rust source owners")
    owners: dict[str, dict[str, Any]] = {}
    for name, relative in (
        ("source", SOURCE_RELATIVE),
        ("protocol", PROTOCOL_RELATIVE),
        ("contract", CONTRACT_RELATIVE),
    ):
        pin = checked_digest(arguments.get(name + "_sha256"), name)
        raw, observed = read_owned(relative, pin)
        owners[name] = observed
        if name == "contract":
            try:
                document = json.loads(raw)
            except (json.JSONDecodeError, UnicodeError, ValueError) as error:
                raise BuildError("reject non-JSON V9 Rust machine contract") from error
            validate_contract(document)
            require(raw == canonical(document),
                    "require the complete exact canonical V9 Rust contract")
    repair = load_frozen_module(
        "_rebar_phase2_exact_frozen_v9_rust_repair_v1",
        REPAIR_OWNERS["source"],
    )
    require(
        repair.SCHEMA == "rebar-phase2-owned-rust-source-repair-v1"
        and repair.ORIGINAL_PATH == ORIGINAL_PATH
        and repair.ORIGINAL_SHA256 == ORIGINAL_SHA256
        and repair.ORIGINAL_BYTES == ORIGINAL_BYTES
        and repair.ADAPTER_PATH == ADAPTER_PATH
        and repair.ADAPTER_SHA256 == ADAPTER_SHA256
        and repair.ADAPTER_BYTES == ADAPTER_BYTES
        and repair.DERIVED_SHA256 == DERIVED_SHA256
        and repair.DERIVED_BYTES == DERIVED_BYTES
        and repair.OLD_BLOCK == OLD_BLOCK
        and repair.NEW_BLOCK == NEW_BLOCK,
        "the separately frozen first-party Rust bridge kernel changed",
    )
    repair_contract, derived = repair.verify_context(
        REPAIR_OWNERS["source"][1],
        REPAIR_OWNERS["protocol"][1],
        REPAIR_OWNERS["contract"][1],
    )
    require(
        type(repair_contract) is dict
        and repair_contract.get("schema")
        == "rebar-phase2-owned-rust-source-repair-v1"
        and type(derived) is bytes
        and len(derived) == DERIVED_BYTES
        and sha256(derived) == DERIVED_SHA256,
        "reject altered, approximate, external, or incomplete Rust bridge repair",
    )
    baseline = repair_contract.get("source_baseline")
    require(
        type(baseline) is dict
        and baseline.get("frozen_family_count") == 6
        and baseline.get("frozen_source_owner_count") == 25
        and baseline.get("frozen_rust_owner_count") == 9
        and baseline.get("rust_external_package_count") == 0
        and baseline.get("shared_semantic_owner_count") == 0,
        "preserve nine independently owned zero-dependency Rust sources",
    )
    history = repair_contract.get("published_history")
    require(
        type(history) is dict
        and history.get("authenticated_digest_addressed_history_paths") == 76
        and history.get("authoritative_counted_evidence_owner_count") == 71
        and history.get("go_full_campaign_status") == "FAIL"
        and history.get("go_full_campaign_suite_count") == 13
        and history.get("go_full_campaign_semantic_mismatch_count") == 4518
        and history.get("go_full_campaign_infrastructure_failure_count") == 4
        and history.get("go_restoration_status") == "PASS"
        and history.get("qualified_candidate_count") == 0,
        "preserve exact V19 owners, Rust history, and failed Go results",
    )
    boundary = repair_contract.get("phase_boundary")
    require(
        type(boundary) is dict
        and boundary.get("source_apply_count") == 0
        and boundary.get("compiler_processes_started") == 0
        and boundary.get("candidate_processes_started") == 0
        and boundary.get("clock_samples") == 0
        and boundary.get("holdout") == "NOT OPENED"
        and boundary.get("holdout_opened") is False
        and boundary.get("winner_selected") is False,
        "the frozen Rust repair crossed its build or holdout boundary",
    )
    v7 = load_frozen_module(
        "_rebar_phase2_exact_frozen_v9_v7_kernel",
        V7_OWNERS["source"],
    )
    require(
        v7.SCHEMA == "rebar-phase2-owned-native-source-build-v7"
        and v7.SOURCE_OWNERS[FAMILY] == RUST_OWNERS
        and v7.FAMILIES[FAMILY]["artifacts"]
        == {"engine": ENGINE_NAME, "bridge": BRIDGE_NAME}
        and v7.PINNED_RUSTC == PINNED_RUSTC
        and v7.PINNED_CARGO == PINNED_CARGO
        and v7.PINNED_GCC == PINNED_GCC
        and v7.PINNED_READELF == PINNED_READELF,
        "reject changed Rust source, native role, or toolchain ownership",
    )
    inherited = v7.verify_context({
        "source_sha256": V7_OWNERS["source"][1],
        "protocol_sha256": V7_OWNERS["protocol"][1],
        "contract_sha256": V7_OWNERS["contract"][1],
    })
    require(
        inherited.get("status") == "PASS"
        and inherited.get("family_count") == 6
        and inherited.get("source_owner_count") == 25
        and inherited.get("pairwise_shared_source_count") == 0
        and inherited.get("qualified_candidate_count") == 0
        and inherited.get("native_builds_started") == 0
        and inherited.get("compiler_processes_started") == 0
        and inherited.get("candidate_processes_started") == 0
        and inherited.get("clock_samples") == 0
        and inherited.get("holdout") == "NOT OPENED",
        "the complete independent V7 context is blocked or not read-only",
    )
    correctness = inherited.get("frozen_correctness")
    require(
        type(correctness) is dict
        and correctness.get("status") == "PASS"
        and correctness.get("suite_count") == 13
        and correctness.get("case_execution_count") == 31237
        and correctness.get("candidate_qualified_count") == 0,
        "retain the complete original CPython correctness oracle",
    )
    accounting = inherited.get("evidence_accounting")
    require(
        type(accounting) is dict
        and accounting.get("all_historical_versions_actual_compiler_process_count")
        == 169
        and accounting.get("distinct_evidence_file_owner_count") == 65,
        "preserve the genuine historical V7 compiler process evidence",
    )
    c_v8 = load_frozen_module(
        "_rebar_phase2_exact_frozen_v9_independent_c_v8",
        C_V8_OWNERS["source"],
    )
    c_context = c_v8.verify_context({
        "source_sha256": C_V8_OWNERS["source"][1],
        "protocol_sha256": C_V8_OWNERS["protocol"][1],
        "contract_sha256": C_V8_OWNERS["contract"][1],
    })
    require(
        c_context.get("status") == "PASS"
        and c_context.get("family") == "c"
        and c_context.get("source_apply_count") == 0
        and c_context.get("native_builds_started") == 0
        and c_context.get("compiler_processes_started") == 0
        and c_context.get("clock_samples") == 0
        and c_context.get("holdout") == "NOT OPENED",
        "preserve the separate unrun repaired C V8 source freeze",
    )
    package = verify_rust_package()
    kernel = v7.load_frozen_v4()
    kernel.audit_native_source(derived, family=FAMILY, location=ORIGINAL_PATH)
    auditor = v7.load_frozen_independence_v2()
    audit = auditor.inspect_native(
        derived.decode("utf-8", "strict"),
        auditor.FAMILY_BY_NAME["rust"],
        ORIGINAL_PATH,
        "c",
    )
    require(type(audit) is dict,
            "require a complete independent derived-bridge no-delegation audit")
    for path, (digest, size) in sorted(RUST_OWNERS.items()):
        read_owned(path, digest, size)
    return {
        "schema": SCHEMA + "-read-only-context",
        "version": 9,
        "status": "PASS",
        "source": owners["source"],
        "protocol": owners["protocol"],
        "contract": owners["contract"],
        "family": FAMILY,
        "frozen_correctness": {
            "status": "PASS",
            "suite_count": 13,
            "case_execution_count": 31237,
            "private_waiver_count": 13,
            "manifest_sha256": P0_MANIFEST[1],
        },
        "source_family_count": 6,
        "original_source_owner_count": 25,
        "rust_source_owner_count": 9,
        "rust_package": package,
        "authenticated_digest_addressed_history_paths": 76,
        "authoritative_counted_evidence_owner_count": 71,
        "historical_compiler_process_count": 169,
        "rust_actual_semantic_mismatch_count": 2042,
        "go_full_campaign_status": "FAIL",
        "go_full_campaign_semantic_mismatch_count": 4518,
        "go_full_campaign_infrastructure_failure_count": 4,
        "go_restoration_status": "PASS",
        "original_bridge_sha256": ORIGINAL_SHA256,
        "original_bridge_bytes": ORIGINAL_BYTES,
        "original_adapter_sha256": ADAPTER_SHA256,
        "original_adapter_bytes": ADAPTER_BYTES,
        "derived_bridge_sha256": DERIVED_SHA256,
        "derived_bridge_bytes": DERIVED_BYTES,
        "derived_bridge_materialized": False,
        "derived_bridge_static_audit": "PASS",
        "frozen_v7_context": "PASS",
        "frozen_independent_c_v8_context": "PASS",
        "frozen_first_party_rust_repair": "PASS",
        "future_compiler_process_count": 28,
        **copy.deepcopy(BOUNDARY),
        "read_only": True,
    }

def checked_workdir(value: Any, family: str) -> str:
    require(
        family == FAMILY
        and type(value) is str
        and value.startswith("/tmp/" + WORK_PREFIX + FAMILY + "-")
        and len(value) <= 512
        and value == value.rstrip("/")
        and len(value.split("/")) == 3
        and all(
            character.isascii()
            and (character.isalnum() or character in "-_")
            for character in value.rsplit("/", 1)[1]
        ),
        "reject an unsafe, cross-version, or non-Rust private V9 root",
    )
    return value


def phase_paths(workdir: str, family: str, phase: str) -> dict[str, Path]:
    checked_workdir(workdir, family)
    require(phase in PHASES,
            "require exactly two independent private Rust source phases")
    base = Path(workdir) / phase
    source = base / "source"
    native = base / "native"
    target = base / "target"
    return {
        "base": base,
        "source": source,
        "native": native,
        "temporary": base / "temporary",
        "target": target,
        "cargo_home": base / "cargo-home",
        "rust_manifest": source / "candidates/rust/Cargo.toml",
        "rust_target_engine":
            target / "release/librebar_rust_continuation.so",
        "artifact_engine": native / ENGINE_NAME,
        "artifact_bridge": native / BRIDGE_NAME,
    }


def sanitized(value: str, workdir: str, family: str) -> str:
    require(type(value) is str, "sanitize only an exact private Rust phase path")
    return value.replace(checked_workdir(workdir, family), "<FRESH_PRIVATE_TMP>")


def reproducible_prefix_flags(
    workdir: str, family: str,
) -> tuple[list[str], str]:
    gcc_flags: list[str] = []
    rust_flags: list[str] = []
    for phase in PHASES:
        source = str(phase_paths(workdir, family, phase)["source"])
        gcc_flags.append(
            "-ffile-prefix-map=" + source + "=/rebar-phase2-v6-owned-source"
        )
        rust_flags.append(
            "--remap-path-prefix=" + source + "=/rebar-phase2-v6-owned-source"
        )
    rust_flags.append("-Clink-arg=-Wl,-soname,_rust_engine.so")
    return gcc_flags, " ".join(rust_flags)


def build_environment(
    workdir: str, family: str, phase: str,
) -> dict[str, str]:
    paths = phase_paths(workdir, family, phase)
    _, rust_flags = reproducible_prefix_flags(workdir, family)
    return {
        "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
        "CARGO_HOME": str(paths["cargo_home"]),
        "CARGO_NET_OFFLINE": "true",
        "CARGO_INCREMENTAL": "0",
        "CARGO_BUILD_JOBS": "1",
        "RUSTC": PINNED_RUSTC,
        "RUSTFLAGS": rust_flags,
    }


def planned_commands(
    workdir: str, family: str, phase: str,
) -> dict[str, list[str]]:
    paths = phase_paths(workdir, family, phase)
    prefixes, _ = reproducible_prefix_flags(workdir, family)
    engine = str(paths["artifact_engine"])
    bridge = str(paths["artifact_bridge"])
    return {
        "readelf_version": [PINNED_READELF, "--version"],
        "gcc_version": [PINNED_GCC, "--version"],
        "rustc_version": [PINNED_RUSTC, "--version", "--verbose"],
        "cargo_version": [PINNED_CARGO, "--version"],
        "build_rust_engine": [
            PINNED_CARGO,
            "build",
            "--manifest-path",
            str(paths["rust_manifest"]),
            "--release",
            "--locked",
            "--offline",
            "--frozen",
            "--target-dir",
            str(paths["target"]),
        ],
        "build_rust_bridge": [
            PINNED_GCC,
            "-pthread",
            "-std=c11",
            "-shared",
            "-fPIC",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wl,-z,noexecstack",
            "-Wl,--exclude-libs,ALL",
            "-Wl,--build-id=sha1",
            *prefixes,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / ORIGINAL_PATH),
            "-L" + str(paths["native"]),
            "-l:_rust_engine.so",
            "-Wl,-rpath,$ORIGIN",
            "-o",
            bridge,
        ],
        "engine_dynamic": [PINNED_READELF, "--dynamic", "--wide", engine],
        "engine_symbols": [PINNED_READELF, "--dyn-syms", "--wide", engine],
        "bridge_dynamic": [PINNED_READELF, "--dynamic", "--wide", bridge],
        "bridge_symbols": [PINNED_READELF, "--dyn-syms", "--wide", bridge],
        "engine_sections": [PINNED_READELF, "--sections", "--wide", engine],
        "engine_notes": [PINNED_READELF, "--notes", "--wide", engine],
        "bridge_sections": [PINNED_READELF, "--sections", "--wide", bridge],
        "bridge_notes": [PINNED_READELF, "--notes", "--wide", bridge],
    }


def checked_command(
    name: Any, argv: Any, workdir: str, family: str, phase: str,
) -> list[str]:
    commands = planned_commands(workdir, family, phase)
    require(
        type(name) is str
        and name in PROCESS_NAMES
        and type(argv) is list
        and all(type(value) is str and "\x00" not in value for value in argv)
        and argv == commands.get(name)
        and argv[0] in (
            PINNED_GCC, PINNED_READELF, PINNED_RUSTC, PINNED_CARGO
        ),
        "reject a changed, external, networked, or non-frozen Rust command",
    )
    if name == "build_rust_engine":
        require(
            all(flag in argv for flag in (
                "--release", "--locked", "--offline", "--frozen", "--target-dir",
            )),
            "forbid unfrozen, networked, externally dependent Rust Cargo builds",
        )
    return list(argv)


def command_working_directory(
    workdir: str, family: str, phase: str, name: str,
) -> Path:
    require(name in PROCESS_NAMES,
            "reject an unapproved Rust process working directory")
    return phase_paths(workdir, family, phase)["base"]

_ACTIVE_KERNEL: types.ModuleType | None = None
_ACTIVE_REPAIR: types.ModuleType | None = None
_ACTIVE_DERIVED: bytes | None = None
_APPLIED_PHASES: set[tuple[str, str]] = set()
_RAW_PHASE_ELF: dict[tuple[str, str, str], bytes] = {}


def active_parts() -> tuple[types.ModuleType, types.ModuleType, bytes]:
    require(
        _ACTIVE_KERNEL is not None and _ACTIVE_REPAIR is not None
        and type(_ACTIVE_DERIVED) is bytes,
        "source snapshot requires an independently pinned explicit V9 build",
    )
    return _ACTIVE_KERNEL, _ACTIVE_REPAIR, _ACTIVE_DERIVED


def prepare_private_phases(kernel: types.ModuleType, workdir: str) -> None:
    checked_workdir(workdir, FAMILY)
    root = os.lstat(workdir)
    require(
        stat.S_ISDIR(root.st_mode)
        and stat.S_IMODE(root.st_mode) == 0o700
        and root.st_uid == os.geteuid(),
        "require a genuine fresh owner-only private Rust build root",
    )
    identities: set[tuple[int, int]] = set()
    for phase in PHASES:
        paths = phase_paths(workdir, FAMILY, phase)
        for path in (
            paths["base"],
            paths["source"],
            paths["source"] / "candidates",
            paths["source"] / "candidates/rust",
            paths["source"] / "candidates/rust/src",
            paths["native"],
            paths["temporary"],
            paths["target"],
            paths["cargo_home"],
        ):
            kernel.mkdir_private(path)
            current = os.lstat(path)
            require(
                stat.S_ISDIR(current.st_mode)
                and stat.S_IMODE(current.st_mode) == 0o700
                and current.st_uid == os.geteuid(),
                "precreate genuine owner-only complete private Rust directories",
            )
        current = os.lstat(paths["base"])
        identity = (current.st_dev, current.st_ino)
        require(identity not in identities, "reject linked Rust peer roots")
        identities.add(identity)
        for path in RUST_OWNERS:
            kernel.require_fresh_absent(paths["source"] / path)
        kernel.require_fresh_absent(paths["artifact_engine"])
        kernel.require_fresh_absent(paths["artifact_bridge"])
        kernel.require_fresh_absent(paths["rust_target_engine"])


def copy_snapshot(
    workdir: str, family: str, phase: str, sources: dict[str, bytes],
) -> dict[str, dict[str, Any]]:
    kernel, repair, derived = active_parts()
    paths = phase_paths(workdir, family, phase)
    require(
        family == FAMILY
        and type(sources) is dict
        and set(sources) == set(RUST_OWNERS)
        and sha256(derived) == DERIVED_SHA256
        and len(derived) == DERIVED_BYTES
        and (workdir, phase) not in _APPLIED_PHASES,
        "require all nine independently pinned original Rust sources",
    )
    for relative, (digest, size) in sorted(RUST_OWNERS.items()):
        require(
            type(sources[relative]) is bytes
            and sha256(sources[relative]) == digest
            and len(sources[relative]) == size,
            "reject changed, foreign, repaired-in-place, or omitted Rust source",
        )
    for peer in PHASES:
        peer_paths = phase_paths(workdir, family, peer)
        for path in (
            peer_paths["base"],
            peer_paths["source"],
            peer_paths["source"] / "candidates",
            peer_paths["source"] / "candidates/rust",
        ):
            current = os.lstat(path)
            require(
                stat.S_ISDIR(current.st_mode)
                and stat.S_IMODE(current.st_mode) == 0o700
                and current.st_uid == os.geteuid(),
                "precreate both nested Rust peer phases before any repair",
            )
    copies: dict[str, dict[str, Any]] = {}
    for relative in sorted(RUST_OWNERS):
        if relative == ORIGINAL_PATH:
            continue
        destination = paths["source"] / relative
        kernel.mkdir_private(destination.parent)
        observed = kernel.write_fresh(
            destination, sources[relative], synchronize=False,
        )
        observed["path"] = sanitized(observed["path"], workdir, family)
        copies[relative] = observed
    applied = repair.apply_private(str(paths["source"]), derived)
    require(
        type(applied) is dict
        and applied.get("status") == "PASS"
        and applied.get("phase") == phase
        and applied.get("source_apply_count") == 1
        and applied.get("derived_sha256") == DERIVED_SHA256
        and applied.get("derived_bytes") == DERIVED_BYTES
        and applied.get("candidate_original_modified") is False,
        "invoke the exact frozen private Rust repair once in each phase",
    )
    observed, private = kernel.authenticate_file(
        paths["source"] / ORIGINAL_PATH,
        expected=DERIVED_SHA256,
        maximum=MAX_SOURCE_BYTES,
        exact_size=DERIVED_BYTES,
        capture=True,
    )
    require(
        type(private) is bytes
        and private == derived
        and stat.S_IMODE(os.lstat(paths["source"] / ORIGINAL_PATH).st_mode)
        == 0o600,
        "bind the Rust bridge compiler to complete exclusive derived bytes",
    )
    copies[ORIGINAL_PATH] = {
        "path": sanitized(observed["path"], workdir, family),
        "sha256": observed["sha256"],
        "bytes": observed["size_bytes"],
        "device": observed["device"],
        "inode": observed["inode"],
        "exclusive_creation": True,
        "same_inode_readback_verified": True,
        "file_fsync_completed": True,
        "source_overlay": applied,
    }
    _APPLIED_PHASES.add((workdir, phase))
    for relative, (digest, size) in sorted(RUST_OWNERS.items()):
        read_owned(relative, digest, size)
    require(
        set(copies) == set(RUST_OWNERS),
        "retain every independently identifiable original Rust source",
    )
    return copies

def install_v9_build_kernel(v7: types.ModuleType, kernel: types.ModuleType) -> None:
    v7.install_v7_build_kernel(kernel)
    kernel.WORK_PREFIX = WORK_PREFIX
    kernel.checked_workdir = checked_workdir
    kernel.phase_paths = phase_paths
    kernel.reproducible_prefix_flags = reproducible_prefix_flags
    kernel.build_environment = build_environment
    kernel.planned_commands = planned_commands
    kernel.checked_command = checked_command
    kernel.sanitized = sanitized
    kernel.command_working_directory = command_working_directory
    kernel.copy_snapshot = copy_snapshot


def record_native_forensics(
    v7: types.ModuleType,
    kernel: types.ModuleType,
    workdir: str,
    phase: str,
    completed: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    outputs = completed.get("native_outputs")
    require(
        type(outputs) is dict and set(outputs) == {"engine", "bridge"},
        "authenticate both complete independently owned Rust native outputs",
    )
    paths = phase_paths(workdir, FAMILY, phase)
    forensic: dict[str, Any] = {}
    for role in ("engine", "bridge"):
        output = outputs[role]
        require(type(output) is dict, "require every authentic Rust ELF role")
        path = paths["artifact_" + role]
        before, raw = kernel.authenticate_file(
            path,
            expected=output["sha256"],
            maximum=MAX_BINARY_BYTES,
            exact_size=output["size_bytes"],
            capture=True,
        )
        require(
            type(raw) is bytes
            and len(raw) == before["size_bytes"]
            and sha256(raw) == before["sha256"],
            "capture every complete exact authenticated Rust native ELF byte",
        )
        parsed = v7.parse_owned_elf64(raw)
        key = (workdir, phase, role)
        require(
            parsed["file_sha256"] == before["sha256"]
            and parsed["file_size"] == before["size_bytes"]
            and key not in _RAW_PHASE_ELF,
            "reject reused, borrowed, incomplete, or unbound Rust ELF bytes",
        )
        _RAW_PHASE_ELF[key] = raw
        streams = {}
        for operation in ("sections", "notes"):
            result = kernel.run_process(
                role + "_" + operation,
                workdir,
                FAMILY,
                phase,
                steps,
            )
            stdout = result["stdout"]
            require(
                type(stdout) is bytes
                and (operation != "sections" or bool(stdout)),
                "capture complete genuine Rust ELF inspection output",
            )
            streams[operation] = {
                "command": role + "_" + operation,
                "stdout_sha256": sha256(stdout),
                "stdout_bytes": len(stdout),
                "process_pid": result["record"]["pid"],
            }
        after, repeated = kernel.authenticate_file(
            path,
            expected=before["sha256"],
            maximum=MAX_BINARY_BYTES,
            exact_size=before["size_bytes"],
            capture=True,
        )
        require(
            repeated == raw
            and (before["device"], before["inode"])
            == (after["device"], after["inode"]),
            "reject an altered or swapped genuine complete Rust ELF role",
        )
        forensic[role] = {
            "sections": streams["sections"],
            "notes": streams["notes"],
            "raw_elf64": parsed,
        }
    return forensic


def verify_derived_reproducible_phases(
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
        and len(steps) == 28,
        "require two complete independent actual fourteen-process Rust phases",
    )
    identities: set[tuple[int, int]] = set()
    for phase_index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        require(
            type(owners) is dict and set(owners) == set(RUST_OWNERS),
            "authenticate all nine first-party Rust source snapshots",
        )
        for path, (original_digest, original_size) in sorted(RUST_OWNERS.items()):
            digest = DERIVED_SHA256 if path == ORIGINAL_PATH else original_digest
            size = DERIVED_BYTES if path == ORIGINAL_PATH else original_size
            owner = owners.get(path)
            require(
                type(owner) is dict
                and owner.get("sha256") == digest
                and owner.get("bytes") == size
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int
                and (owner["device"], owner["inode"]) not in identities,
                "reject linked, repeated, replaced, or borrowed Rust source",
            )
            identities.add((owner["device"], owner["inode"]))
        applied = owners[ORIGINAL_PATH].get("source_overlay")
        require(
            type(applied) is dict
            and applied.get("status") == "PASS"
            and applied.get("phase") == PHASES[phase_index]
            and applied.get("source_apply_count") == 1
            and applied.get("derived_sha256") == DERIVED_SHA256
            and applied.get("derived_bytes") == DERIVED_BYTES,
            "require the exact frozen bridge repair once in each phase",
        )
        outputs = phase.get("native_outputs")
        require(
            type(outputs) is dict and set(outputs) == {"engine", "bridge"},
            "retain both genuine independently owned Rust ELF outputs",
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
            "reject fake, omitted, reordered, failed, or reused Rust processes",
        )
        pids.add(step["pid"])
    native_outputs: dict[str, Any] = {}
    comparisons: dict[str, Any] = {}
    for role, filename in (
        ("engine", ENGINE_NAME),
        ("bridge", BRIDGE_NAME),
    ):
        left = phases[0]["native_outputs"][role]
        right = phases[1]["native_outputs"][role]
        require(
            left["file_name"] == right["file_name"] == filename
            and left["sha256"] == right["sha256"]
            and left["size_bytes"] == right["size_bytes"]
            and left["path"] != right["path"]
            and (left["device"], left["inode"])
            != (right["device"], right["inode"])
            and left["audit"] == right["audit"],
            "reject a non-reproducible fresh Rust native output role",
        )
        first = _RAW_PHASE_ELF.get((workdir, PHASES[0], role))
        second = _RAW_PHASE_ELF.get((workdir, PHASES[1], role))
        require(
            type(first) is bytes
            and type(second) is bytes
            and sha256(first) == left["sha256"]
            and sha256(second) == right["sha256"]
            and first == second,
            "compare both authentic full independently owned Rust ELF files",
        )
        compared = v7.compare_owned_elf64(first, second)
        require(
            compared.get("byte_identical") is True,
            "a complete genuine Rust ELF role differs between private phases",
        )
        comparisons[role] = compared
        native_outputs[role] = {
            "file_name": filename,
            "sha256": left["sha256"],
            "size_bytes": left["size_bytes"],
            "fresh_independent_inode_count": 2,
            "reproduced_in_two_fresh_directories": True,
            "audit": left["audit"],
        }
    for path, (digest, size) in sorted(RUST_OWNERS.items()):
        read_owned(path, digest, size)
    return {
        "independent_fresh_phase_count": 2,
        "source_owners_per_phase": 9,
        "original_source_owners_per_phase": 8,
        "derived_source_apply_count": 2,
        "derived_bridge_sha256": DERIVED_SHA256,
        "derived_bridge_bytes": DERIVED_BYTES,
        "original_source_modified": False,
        "byte_identical": True,
        "unique_process_count": 28,
        "native_role_count": 2,
        "raw_elf_comparisons": comparisons,
        "native_outputs": native_outputs,
        "prebuilt_artifact_count": 0,
        "native_libraries_loaded": 0,
    }

def checked_label(value: Any) -> str:
    require(
        type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
        and all(
            character.isascii()
            and (character.isalnum() or character in "-_")
            for character in value
        ),
        "require an exact safe nonempty bounded V9 evidence label",
    )
    return value


def evidence_names(label: str, *, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "choose an actual V9 success or failure")
    base = "native-source-build-v9-rust-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def publish_report(
    kernel: types.ModuleType, report: dict[str, Any], label: str,
) -> dict[str, Any]:
    require(
        type(report) is dict and report.get("status") in ("PASS", "FAIL"),
        "publish only an actual complete V9 build or an honest durable failure",
    )
    failed = report["status"] == "FAIL"
    archive_name, receipt_name = evidence_names(label, failure=failed)
    directory = ROOT / EVIDENCE_RELATIVE
    kernel.mkdir_private(directory)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES, "bound the complete V9 build report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(
        0 < len(archive) <= MAX_ARCHIVE_BYTES,
        "bound one complete deterministic V9 gzip evidence archive",
    )
    published = kernel.write_fresh(
        directory / archive_name, archive, synchronize=True,
    )
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "build_status": report["status"],
        "family": FAMILY,
        "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "phase1_manifest_sha256": P0_MANIFEST[1],
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": published["sha256"],
        "archive_bytes": published["bytes"],
        "uncompressed_sha256": sha256(plain),
        "uncompressed_bytes": len(plain),
        "archive_publication": published,
        "archive_directory_fsync": archive_sync,
        "original_source_sha256": ORIGINAL_SHA256,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_apply_count": report.get("derived_source_apply_count", 0),
        "expected_v9_compiler_process_count": 28,
        "actual_v9_compiler_process_count": report.get(
            "actual_v9_compiler_process_count", 0,
        ),
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_raw = canonical(receipt)
    require(
        len(receipt_raw) <= MAX_SOURCE_BYTES,
        "bound the complete authentic V9 durable evidence receipt",
    )
    recorded = kernel.write_fresh(
        directory / receipt_name, receipt_raw, synchronize=True,
    )
    receipt_sync = kernel.fsync_directory(directory)
    return {
        "schema": SCHEMA + "-published-build",
        "status": report["status"], "family": FAMILY, "label": label,
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": published["sha256"],
        "receipt_relative": EVIDENCE_RELATIVE + "/" + receipt_name,
        "receipt_sha256": recorded["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": failed,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def parse_arguments(arguments: list[str]) -> dict[str, Any]:
    require(type(arguments) is list,
            "require complete explicit V9 Rust source-freeze arguments")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(
        bool(arguments) and arguments[0] in ("--verify-context", "--build"),
        "select exactly V9 --self-test, --verify-context, or --build",
    )
    mode = "verify-context" if arguments[0] == "--verify-context" else "build"
    scalar = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--family": "family",
        "--label": "label",
    }
    result: dict[str, Any] = {"mode": mode, "owned_source_sha256": []}
    cursor = 1
    while cursor < len(arguments):
        flag = arguments[cursor]
        require(cursor + 1 < len(arguments),
                "reject an omitted V9 Rust argument value")
        value = arguments[cursor + 1]
        if flag == "--owned-source-sha256":
            require(mode == "build",
                    "read-only verification cannot authorize Rust snapshots")
            result["owned_source_sha256"].append(value)
        else:
            require(
                flag in scalar and scalar[flag] not in result,
                "reject duplicate, foreign, or unknown V9 Rust arguments",
            )
            result[scalar[flag]] = value
        cursor += 2
    require(
        all(
            key in result
            for key in ("source_sha256", "protocol_sha256", "contract_sha256")
        ),
        "pin the exact independent V9 Rust recorder, protocol, and contract",
    )
    if mode == "verify-context":
        require(
            "family" not in result
            and "label" not in result
            and not result["owned_source_sha256"],
            "V9 verification cannot authorize build or candidate publication",
        )
    else:
        require(
            result.get("family") == FAMILY and "label" in result,
            "explicitly select only the frozen Rust family and evidence label",
        )
        checked_label(result["label"])
        values = result["owned_source_sha256"]
        require(
            type(values) is list
            and len(values) == len(RUST_OWNERS)
            and set(values) == {
                path + "=" + digest
                for path, (digest, _size) in RUST_OWNERS.items()
            },
            "independently pin all nine original first-party Rust owners",
        )
    return result

def run_build(arguments: dict[str, Any]) -> dict[str, Any]:
    global _ACTIVE_KERNEL, _ACTIVE_REPAIR, _ACTIVE_DERIVED
    require(
        arguments.get("mode") == "build",
        "require a separate explicit independently pinned V9 Rust build",
    )
    context = verify_context(arguments)
    label = checked_label(arguments["label"])
    v7 = load_frozen_module(
        "_rebar_phase2_exact_frozen_v9_rust_build_v7",
        V7_OWNERS["source"],
    )
    repair = load_frozen_module(
        "_rebar_phase2_exact_frozen_v9_rust_build_repair",
        REPAIR_OWNERS["source"],
    )
    kernel = v7.load_frozen_v4()
    sources: dict[str, bytes] = {}
    for path, (digest, size) in sorted(RUST_OWNERS.items()):
        sources[path], _ = read_owned(path, digest, size)
    derived = repair.repaired_source(
        sources[ORIGINAL_PATH],
        ORIGINAL_SHA256,
        ORIGINAL_BYTES,
    )
    require(
        type(derived) is bytes
        and len(derived) == DERIVED_BYTES
        and sha256(derived) == DERIVED_SHA256,
        "derive only the unique frozen first-party private Rust bridge",
    )
    for failed in (False, True):
        for name in evidence_names(label, failure=failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE_RELATIVE / name)
    require(
        _ACTIVE_KERNEL is None
        and _ACTIVE_REPAIR is None
        and _ACTIVE_DERIVED is None,
        "reject reused, nested, or substituted private Rust kernels",
    )
    _ACTIVE_KERNEL, _ACTIVE_REPAIR, _ACTIVE_DERIVED = kernel, repair, derived
    install_v9_build_kernel(v7, kernel)
    workdir = tempfile.mkdtemp(
        prefix=WORK_PREFIX + FAMILY + "-",
        dir="/tmp",
    )
    checked_workdir(workdir, FAMILY)
    steps: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []
    try:
        prepare_private_phases(kernel, workdir)
        for phase in PHASES:
            result = kernel.exact_build_phase(
                workdir,
                FAMILY,
                phase,
                sources,
                steps,
            )
            result["native_forensics"] = record_native_forensics(
                v7,
                kernel,
                workdir,
                phase,
                result,
                steps,
            )
            completed.append(result)
        reproduction = verify_derived_reproducible_phases(
            v7,
            workdir,
            completed,
            steps,
        )
        report = {
            "schema": SCHEMA,
            "version": 9,
            "status": "PASS",
            "family": FAMILY,
            "label": label,
            "source_sha256": arguments["source_sha256"],
            "protocol_sha256": arguments["protocol_sha256"],
            "contract_sha256": arguments["contract_sha256"],
            "frozen_context": context,
            "original_source_sha256": ORIGINAL_SHA256,
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_apply_count": 2,
            "expected_v9_compiler_process_count": 28,
            "actual_v9_compiler_process_count": len(steps),
            "phase_count": 2,
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
        return publish_report(kernel, report, label)
    except Exception as error:
        for path, (digest, size) in sorted(RUST_OWNERS.items()):
            read_owned(path, digest, size)
        report = {
            "schema": SCHEMA,
            "version": 9,
            "status": "FAIL",
            "family": FAMILY,
            "label": label,
            "source_sha256": arguments["source_sha256"],
            "protocol_sha256": arguments["protocol_sha256"],
            "contract_sha256": arguments["contract_sha256"],
            "frozen_context": context,
            "original_source_sha256": ORIGINAL_SHA256,
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_apply_count": sum(
                (workdir, phase) in _APPLIED_PHASES for phase in PHASES
            ),
            "expected_v9_compiler_process_count": 28,
            "actual_v9_compiler_process_count": len(steps),
            "phase_count": len(completed),
            "phases": completed,
            "compiler_processes": steps,
            "error_type": type(error).__name__,
            "error_message": str(error),
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
        return publish_report(kernel, report, label)

def main(arguments: list[str] | None = None) -> int:
    try:
        parsed = parse_arguments(
            list(sys.argv[1:] if arguments is None else arguments),
        )
        if parsed["mode"] == "self-test":
            verify_runtime()
            result = self_test()
        elif parsed["mode"] == "verify-context":
            result = verify_context(parsed)
        else:
            result = run_build(parsed)
        sys.stdout.buffer.write(canonical(result))
        return 0 if result.get("status") == "PASS" else 1
    except (
        BuildError, OSError, ValueError, UnicodeError,
        subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-gate-failure", "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
