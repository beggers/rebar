#!/usr/bin/env python3
"""Freeze a private, first-party C-source repair before any V8 native build."""

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
import types
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/reproduce_owned_native_source_build_v8.py"
PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V8.md"
CONTRACT_RELATIVE = "oracle/phase2/native-source-build-v8.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-native-source-build-v8"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
WORK_PREFIX = "rebar-phase2-native-build-v8-"
FAMILY = "c"
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
EXTENSION_NAME = "_vm_native.cpython-314-x86_64-linux-gnu.so"
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
REPAIR_OWNERS = {
    "source": (
        "tools/apply_owned_first_party_source_repair_v1.py",
        "c04bbc8e7bc45bdbe1fb9eb93942286f5b32b39aef554db15b8b1acd9cc8cd99",
        45783,
    ),
    "protocol": (
        "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md",
        "1a2e83caaca5cb43fc82445c2a4fc3097bc3d51bdfc568783b8815797b8c63f5",
        4308,
    ),
    "contract": (
        "oracle/phase2/first-party-source-repair-v1.json",
        "8f1a5676bbef5f2ef560d03fef910bf4ed3a4df029ecc0c638e3fa971206dab5",
        5650,
    ),
}
ORIGINAL_PATH = "candidates/_vm_native.c"
ORIGINAL_SHA256 = (
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
)
ORIGINAL_BYTES = 218185
ADAPTER_PATH = "candidates/vm_candidate.py"
ADAPTER_SHA256 = (
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
)
ADAPTER_BYTES = 60707
DERIVED_SHA256 = (
    "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
)
DERIVED_BYTES = 218308
OLD_BLOCK = b"""    Subject subject;
    if (!pattern_subject(pattern,string,&subject)) return NULL;
    PyObject *result=NULL;
    PyObject *template_parts=NULL;
    if (PyCallable_Check(replacement)) {
        result=substitute_callable(pattern,&subject,replacement,limit,
                                  return_count);
        goto done;
    }

    int template_byte_mode=0,literal_replacement=0;
    template_parts=substitution_template(
        pattern,replacement,&template_byte_mode,&literal_replacement);
    if (!template_parts) goto done;
"""
NEW_BLOCK = b"""    Subject subject={0};
    PyObject *result=NULL;
    PyObject *template_parts=NULL;
    int template_byte_mode=0,literal_replacement=0;
    int callable=PyCallable_Check(replacement);
    if (!callable) {
        template_parts=substitution_template(
            pattern,replacement,&template_byte_mode,&literal_replacement);
        if (!template_parts) return NULL;
    }
    if (!pattern_subject(pattern,string,&subject)) {
        Py_XDECREF(template_parts);
        return NULL;
    }
    if (callable) {
        result=substitute_callable(pattern,&subject,replacement,limit,
                                  return_count);
        goto done;
    }
"""
SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols",
    "extension_sections", "extension_notes",
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
    """An owned V8 source-freeze or actual build failed."""


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
        "version": 8,
        "phase": "SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
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
            "original_c_source": {
                "path": ORIGINAL_PATH, "sha256": ORIGINAL_SHA256,
                "bytes": ORIGINAL_BYTES, "modified": False,
            },
            "original_adapter": {
                "path": ADAPTER_PATH, "sha256": ADAPTER_SHA256,
                "bytes": ADAPTER_BYTES, "modified": False,
            },
            "v7": {name: owner(item) for name, item in sorted(V7_OWNERS.items())},
        },
        "first_party_source_repair": {
            "owners": {
                name: owner(item) for name, item in sorted(REPAIR_OWNERS.items())
            },
            "derived_source": {
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
            "transformation": "EXACTLY ONE ANCHORED FIRST-PARTY C SOURCE BLOCK",
            "subject_failure_cleanup": "ONE TEMPLATE DECREF; NO SECOND SUBJECT RELEASE",
            "template_failure_cleanup": "NO SUBJECT ACQUIRED",
            "successful_subject_cleanup": "EXISTING SINGLE DONE LABEL; UNCHANGED",
            "callable_semantics": "PRESERVED",
            "pybuf_simple_semantics": "PRESERVED",
            "apply_function": "apply_private",
            "application": "EXACTLY ONCE IN EACH FUTURE PRIVATE SOURCE PHASE",
            "existing_destination": "FORBIDDEN",
        },
        "published_history": {
            "authenticated_digest_addressed_history_paths": 76,
            "authoritative_counted_evidence_owner_count": 71,
            "historical_compiler_process_count": 169,
            "current_active_target_count": 0,
            "current_tested_candidate_family_count": 5,
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
            "directory_mode": "0700",
            "source_file_mode": "0600",
            "source_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "adapter_source_sha256": ADAPTER_SHA256,
            "private_compiler_input_sha256": DERIVED_SHA256,
            "compiler": PINNED_GCC,
            "elf_inspector": PINNED_READELF,
            "python_include": PYTHON_INCLUDE,
            "extension_name": EXTENSION_NAME,
            "compiler_flags": [
                "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
                "-fPIC", "-shared", "-Wl,--build-id=sha1",
            ],
            "phase_prefix_map_target": "/rebar-phase2-v6-owned-source",
            "process_names_per_phase": list(PROCESS_NAMES),
            "processes_per_phase": 7,
            "total_future_processes": 14,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "external_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "network": "FORBIDDEN",
            "original_v4_reproducibility_verifier": "FORBIDDEN FOR DERIVED SOURCE",
            "raw_elf_forensics": "COMPLETE AUTHENTICATED PHASE BYTES",
            "reproducibility": "DERIVED C, ORIGINAL ADAPTER, AND COMPLETE RAW ELF",
        },
        "future_evidence": {
            "directory": EVIDENCE_RELATIVE,
            "archive_prefix": "native-source-build-v8-c-",
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


def validate_contract(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict and canonical(value) == canonical(expected_contract()),
        "reject an altered, weakened, incomplete, or non-frozen V8 contract",
    )
    return value


class SourceOnlyWall:
    """Block every filesystem, process, clock, network, and loader effect."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked_effect_count = 0

    def forbidden(self, *_args: Any, **_kwargs: Any) -> Any:
        self.blocked_effect_count += 1
        raise SourceOnlyError("a V8 source-only control attempted an external effect")

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
    require(type(phases) is list and len(phases) == 2, "require two synthetic phases")
    require(type(steps) is list and len(steps) == 14, "require exactly 14 process roles")
    identities: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        require(
            type(phase) is dict and phase.get("name") == PHASES[index]
            and phase.get("source_sha256") == DERIVED_SHA256
            and phase.get("source_bytes") == DERIVED_BYTES
            and phase.get("adapter_sha256") == ADAPTER_SHA256
            and phase.get("adapter_bytes") == ADAPTER_BYTES
            and phase.get("source_apply_count") == 1
            and phase.get("source_mode") == 0o600
            and phase.get("directory_mode") == 0o700,
            "reject a missing, original, reused, or non-private derived phase",
        )
        for key in ("source_identity", "adapter_identity", "output_identity"):
            identity = phase.get(key)
            require(
                type(identity) is tuple and len(identity) == 2
                and all(type(item) is int and item > 0 for item in identity)
                and identity not in identities,
                "reject an absent, forged, shared, or linked phase identity",
            )
            identities.add(identity)
    pids: set[int] = set()
    for index, step in enumerate(steps):
        require(
            type(step) is dict
            and step.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
            and step.get("phase") == PHASES[index // len(PROCESS_NAMES)]
            and type(step.get("pid")) is int and step["pid"] > 0
            and step["pid"] not in pids and step.get("exit_status") == 0,
            "reject a missing, reordered, repeated, failed, or fake compiler process",
        )
        pids.add(step["pid"])
    require(
        phases[0].get("output_sha256") == phases[1].get("output_sha256")
        and type(phases[0].get("output_sha256")) is str
        and len(phases[0]["output_sha256"]) == 64,
        "require complete byte-identical independently owned synthetic outputs",
    )
    return {"independent_phase_count": 2, "unique_process_count": 14}


def expect_rejected(function: Any, *arguments: Any) -> None:
    try:
        function(*arguments)
    except (BuildError, TypeError, ValueError, KeyError, IndexError):
        return
    raise BuildError("a negative V8 source-freeze control was silently accepted")


def self_test() -> dict[str, Any]:
    with SourceOnlyWall() as wall:
        frozen = validate_contract(expected_contract())
        phases = [
            {
                "name": phase,
                "source_sha256": DERIVED_SHA256,
                "source_bytes": DERIVED_BYTES,
                "adapter_sha256": ADAPTER_SHA256,
                "adapter_bytes": ADAPTER_BYTES,
                "source_apply_count": 1,
                "source_mode": 0o600,
                "directory_mode": 0o700,
                "source_identity": (1, 10 + index),
                "adapter_identity": (1, 20 + index),
                "output_identity": (1, 30 + index),
                "output_sha256": "a" * 64,
            }
            for index, phase in enumerate(PHASES)
        ]
        steps = [
            {
                "name": role, "phase": phase,
                "pid": 1000 + phase_index * len(PROCESS_NAMES) + index,
                "exit_status": 0,
            }
            for phase_index, phase in enumerate(PHASES)
            for index, role in enumerate(PROCESS_NAMES)
        ]
        synthetic_phase_gate(phases, steps)
        controls = 0
        mutations: list[tuple[tuple[str, ...], Any]] = [
            (("schema",), SCHEMA), (("version",), 7),
            (("phase",), "PASS"), (("family",), "rust"),
            (("oracle", "case_execution_count"), 31236),
            (("oracle", "private_waiver_count"), 12),
            (("oracle", "suite_count"), 12),
            (("oracle", "version"), "3.14.5"),
            (("oracle", "implementation"), "PyPy"),
            (("source_baseline", "family_count"), 5),
            (("source_baseline", "original_source_owner_count"), 24),
            (("source_baseline", "candidate_source_mutation"), "ALLOWED"),
            (("first_party_source_repair", "apply_function"), "copy_snapshot"),
            (("first_party_source_repair", "existing_destination"), "ALLOWED"),
            (("first_party_source_repair", "application"), "ONCE"),
            (("published_history", "authenticated_digest_addressed_history_paths"), 71),
            (("published_history", "authoritative_counted_evidence_owner_count"), 76),
            (("published_history", "historical_compiler_process_count"), 168),
            (("published_history", "go_full_campaign_status"), "PASS"),
            (("published_history", "go_full_campaign_suite_count"), 12),
            (("published_history", "go_full_campaign_semantic_mismatch_count"), 0),
            (("published_history", "go_full_campaign_infrastructure_failure_count"), 0),
            (("published_history", "go_restoration_status"), "FAIL"),
            (("published_history", "qualified_candidate_count"), 1),
            (("future_build_policy", "root_parent"), "/"),
            (("future_build_policy", "root_prefix"), "rebar-phase2-native-build-v7-c-"),
            (("future_build_policy", "both_peer_phases_precreated_before_first_apply"), False),
            (("future_build_policy", "directory_mode"), "0755"),
            (("future_build_policy", "source_file_mode"), "0644"),
            (("future_build_policy", "source_creation"), "O_CREAT"),
            (("future_build_policy", "private_compiler_input_sha256"), ORIGINAL_SHA256),
            (("future_build_policy", "processes_per_phase"), 6),
            (("future_build_policy", "total_future_processes"), 13),
            (("future_build_policy", "external_engine"), "ALLOWED"),
            (("future_build_policy", "fallback"), "ALLOWED"),
            (("future_build_policy", "network"), "ALLOWED"),
            (("future_build_policy", "original_v4_reproducibility_verifier"), "ALLOWED"),
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
            replacements: tuple[Any, ...]
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
            for key, replacement in (
                ("name", "reference-c"), ("source_sha256", ORIGINAL_SHA256),
                ("source_bytes", ORIGINAL_BYTES), ("adapter_sha256", "f" * 64),
                ("adapter_bytes", ADAPTER_BYTES + 1), ("source_apply_count", 0),
                ("source_mode", 0o644), ("directory_mode", 0o755),
                ("source_identity", (1, 20)), ("adapter_identity", (1, 10)),
                ("output_identity", (1, 10)),
            ):
                changed = copy.deepcopy(phases)
                changed[phase_index][key] = replacement
                expect_rejected(synthetic_phase_gate, changed, steps)
                controls += 1
        for index in range(len(steps)):
            for key, replacement in (
                ("pid", steps[0]["pid"] if index else 0),
                ("exit_status", 1), ("name", "build_foreign_engine"),
            ):
                changed_steps = copy.deepcopy(steps)
                changed_steps[index][key] = replacement
                expect_rejected(synthetic_phase_gate, phases, changed_steps)
                controls += 1
        for forbidden in (
            lambda: builtins.open("/tmp/rebar-v8-self-test-forbidden", "wb"),
            lambda: os.open("/tmp/rebar-v8-self-test-forbidden", os.O_RDONLY),
            lambda: subprocess.run(["/usr/bin/true"]),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(prefix=WORK_PREFIX),
            lambda: time.perf_counter_ns(),
            lambda: importlib.import_module("re"),
        ):
            expect_rejected(forbidden)
            controls += 1
        require(controls >= 175, "exercise all V8 source-freeze negative controls")
        require(wall.blocked_effect_count == 7, "block every synthetic effect attempt")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 8, "status": "PASS",
            "negative_controls": controls,
            "blocked_effect_attempts": wall.blocked_effect_count,
            "synthetic_independent_phase_count": 2,
            "synthetic_unique_process_count": 14,
            "frozen_contract": frozen,
            **copy.deepcopy(BOUNDARY),
            "filesystem_reads": 0, "filesystem_writes": 0,
            "processes_started": 0, "read_only": True,
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
    require(type(arguments) is dict, "require independently pinned V8 source owners")
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
                raise BuildError("reject non-JSON V8 machine contract") from error
            validate_contract(document)
            require(raw == canonical(document), "require canonical V8 contract bytes")
    repair = load_frozen_module(
        "_rebar_phase2_exact_frozen_v8_repair_v1", REPAIR_OWNERS["source"],
    )
    require(
        repair.SCHEMA == "rebar-phase2-owned-first-party-source-repair-v1"
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
        "the exact frozen first-party repair semantic kernel changed",
    )
    repair_contract, derived = repair.verify_context(
        REPAIR_OWNERS["source"][1], REPAIR_OWNERS["protocol"][1],
        REPAIR_OWNERS["contract"][1],
    )
    require(
        type(repair_contract) is dict
        and repair_contract.get("schema")
        == "rebar-phase2-owned-first-party-source-repair-v1"
        and type(derived) is bytes and len(derived) == DERIVED_BYTES
        and sha256(derived) == DERIVED_SHA256,
        "reject an altered, approximated, or incomplete frozen C repair",
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
        "preserve all actual V19 evidence owners and failed Go results",
    )
    repair_boundary = repair_contract.get("phase_boundary")
    require(
        type(repair_boundary) is dict
        and repair_boundary.get("source_apply_count") == 0
        and repair_boundary.get("compiler_processes_started") == 0
        and repair_boundary.get("candidate_processes_started") == 0
        and repair_boundary.get("clock_samples") == 0
        and repair_boundary.get("holdout") == "NOT OPENED"
        and repair_boundary.get("holdout_opened") is False
        and repair_boundary.get("winner_selected") is False,
        "the pure frozen repair crossed the build or hidden-holdout boundary",
    )
    v7 = load_frozen_module(
        "_rebar_phase2_exact_frozen_v8_v7_kernel", V7_OWNERS["source"],
    )
    require(
        v7.SCHEMA == "rebar-phase2-owned-native-source-build-v7"
        and v7.SOURCE_OWNERS[FAMILY][ORIGINAL_PATH]
        == (ORIGINAL_SHA256, ORIGINAL_BYTES)
        and v7.SOURCE_OWNERS[FAMILY][ADAPTER_PATH]
        == (ADAPTER_SHA256, ADAPTER_BYTES),
        "reject an altered authentic six-family V7 semantic kernel",
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
        "the exact complete V7 context is blocked, changed, or no longer read-only",
    )
    correctness = inherited.get("frozen_correctness")
    require(
        type(correctness) is dict and correctness.get("status") == "PASS"
        and correctness.get("suite_count") == 13
        and correctness.get("case_execution_count") == 31237
        and correctness.get("candidate_qualified_count") == 0,
        "preserve the exact complete original 13-suite correctness oracle",
    )
    accounting = inherited.get("evidence_accounting")
    require(
        type(accounting) is dict
        and accounting.get("all_historical_versions_actual_compiler_process_count")
        == 169
        and accounting.get("distinct_evidence_file_owner_count") == 65,
        "preserve the actual historical V7 compiler and historical owner accounting",
    )
    kernel = v7.load_frozen_v4()
    kernel.audit_native_source(derived, family=FAMILY, location=ORIGINAL_PATH)
    auditor = v7.load_frozen_independence_v2()
    native_audit = auditor.inspect_native(
        derived.decode("utf-8", "strict"),
        auditor.FAMILY_BY_NAME["c_vm"], ORIGINAL_PATH, "c",
    )
    require(type(native_audit) is dict, "require a complete independent native audit")
    read_owned(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    read_owned(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    return {
        "schema": SCHEMA + "-read-only-context",
        "version": 8, "status": "PASS",
        "source": owners["source"], "protocol": owners["protocol"],
        "contract": owners["contract"], "family": FAMILY,
        "frozen_correctness": {
            "status": "PASS", "suite_count": 13,
            "case_execution_count": 31237, "private_waiver_count": 13,
            "manifest_sha256": P0_MANIFEST[1],
        },
        "source_family_count": 6,
        "original_source_owner_count": 25,
        "authenticated_digest_addressed_history_paths": 76,
        "authoritative_counted_evidence_owner_count": 71,
        "historical_compiler_process_count": 169,
        "go_full_campaign_status": "FAIL",
        "go_full_campaign_semantic_mismatch_count": 4518,
        "go_full_campaign_infrastructure_failure_count": 4,
        "go_restoration_status": "PASS",
        "original_source_sha256": ORIGINAL_SHA256,
        "original_source_bytes": ORIGINAL_BYTES,
        "original_adapter_sha256": ADAPTER_SHA256,
        "original_adapter_bytes": ADAPTER_BYTES,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        "derived_source_materialized": False,
        "derived_source_static_audit": "PASS",
        "frozen_v7_context": "PASS",
        "frozen_first_party_source_repair": "PASS",
        "future_compiler_process_count": 14,
        **copy.deepcopy(BOUNDARY), "read_only": True,
    }


def checked_workdir(value: Any, family: str) -> str:
    require(
        family == FAMILY and type(value) is str
        and value.startswith("/tmp/" + WORK_PREFIX + FAMILY + "-")
        and len(value) <= 512 and value == value.rstrip("/")
        and len(value.split("/")) == 3
        and all(
            character.isascii() and
            (character.isalnum() or character in "-_")
            for character in value.rsplit("/", 1)[1]
        ),
        "reject an unsafe, cross-version, non-private, or non-C V8 build root",
    )
    return value


def phase_paths(workdir: str, family: str, phase: str) -> dict[str, Path]:
    checked_workdir(workdir, family)
    require(phase in PHASES, "require exactly the two frozen V8 private phases")
    base = Path(workdir) / phase
    source, native = base / "source", base / "native"
    return {
        "base": base, "source": source, "native": native,
        "temporary": base / "temporary",
        "artifact_extension": native / EXTENSION_NAME,
    }


def sanitized(value: str, workdir: str, family: str) -> str:
    require(type(value) is str, "sanitize only a complete genuine V8 path")
    return value.replace(checked_workdir(workdir, family), "<FRESH_PRIVATE_TMP>")


def reproducible_prefix_flags(workdir: str, family: str) -> tuple[list[str], str]:
    return (
        [
            "-ffile-prefix-map="
            + str(phase_paths(workdir, family, phase)["source"])
            + "=/rebar-phase2-v6-owned-source"
            for phase in PHASES
        ],
        "",
    )


def build_environment(workdir: str, family: str, phase: str) -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C",
        "TZ": "UTC", "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(phase_paths(workdir, family, phase)["temporary"]),
    }


def planned_commands(
    workdir: str, family: str, phase: str,
) -> dict[str, list[str]]:
    paths = phase_paths(workdir, family, phase)
    prefixes, _ = reproducible_prefix_flags(workdir, family)
    artifact = str(paths["artifact_extension"])
    return {
        "readelf_version": [PINNED_READELF, "--version"],
        "gcc_version": [PINNED_GCC, "--version"],
        "build_c_extension": [
            PINNED_GCC, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefixes,
            "-I" + PYTHON_INCLUDE, str(paths["source"] / ORIGINAL_PATH),
            "-o", artifact,
        ],
        "extension_dynamic": [PINNED_READELF, "--dynamic", "--wide", artifact],
        "extension_symbols": [PINNED_READELF, "--dyn-syms", "--wide", artifact],
        "extension_sections": [PINNED_READELF, "--sections", "--wide", artifact],
        "extension_notes": [PINNED_READELF, "--notes", "--wide", artifact],
    }


def checked_command(
    name: Any, argv: Any, workdir: str, family: str, phase: str,
) -> list[str]:
    commands = planned_commands(workdir, family, phase)
    require(
        type(name) is str and name in PROCESS_NAMES and type(argv) is list
        and all(type(part) is str and "\x00" not in part for part in argv)
        and argv == commands.get(name)
        and argv[0] in (PINNED_GCC, PINNED_READELF),
        "reject a changed, foreign, weakened, shell, or network V8 command",
    )
    return list(argv)


def command_working_directory(
    workdir: str, family: str, phase: str, name: str,
) -> Path:
    require(name in PROCESS_NAMES, "reject a foreign process working directory")
    return phase_paths(workdir, family, phase)["base"]


_ACTIVE_KERNEL: types.ModuleType | None = None
_ACTIVE_REPAIR: types.ModuleType | None = None
_ACTIVE_DERIVED: bytes | None = None
_APPLIED_PHASES: set[tuple[str, str]] = set()
_RAW_PHASE_ELF: dict[tuple[str, str], bytes] = {}


def active_parts() -> tuple[types.ModuleType, types.ModuleType, bytes]:
    require(
        _ACTIVE_KERNEL is not None and _ACTIVE_REPAIR is not None
        and type(_ACTIVE_DERIVED) is bytes,
        "source snapshot requires an independently pinned explicit V8 build",
    )
    return _ACTIVE_KERNEL, _ACTIVE_REPAIR, _ACTIVE_DERIVED


def prepare_private_phases(kernel: types.ModuleType, workdir: str) -> None:
    checked_workdir(workdir, FAMILY)
    root = os.lstat(workdir)
    require(
        stat.S_ISDIR(root.st_mode) and stat.S_IMODE(root.st_mode) == 0o700
        and root.st_uid == os.geteuid(),
        "require a fresh genuinely private owner-only V8 build root",
    )
    phase_identities: set[tuple[int, int]] = set()
    for phase in PHASES:
        paths = phase_paths(workdir, FAMILY, phase)
        for path in (
            paths["base"], paths["source"], paths["source"] / "candidates",
            paths["native"], paths["temporary"],
        ):
            kernel.mkdir_private(path)
            info = os.lstat(path)
            require(
                stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid(),
                "require owner-only, unswapped complete V8 phase directories",
            )
        identity = os.lstat(paths["base"])
        item = (identity.st_dev, identity.st_ino)
        require(item not in phase_identities, "reject aliased V8 peer phases")
        phase_identities.add(item)
        kernel.require_fresh_absent(paths["source"] / ORIGINAL_PATH)
        kernel.require_fresh_absent(paths["source"] / ADAPTER_PATH)
        kernel.require_fresh_absent(paths["artifact_extension"])


def copy_snapshot(
    workdir: str, family: str, phase: str, sources: dict[str, bytes],
) -> dict[str, dict[str, Any]]:
    kernel, repair, derived = active_parts()
    paths = phase_paths(workdir, family, phase)
    require(
        family == FAMILY and type(sources) is dict
        and set(sources) == {ORIGINAL_PATH, ADAPTER_PATH}
        and sha256(sources[ORIGINAL_PATH]) == ORIGINAL_SHA256
        and len(sources[ORIGINAL_PATH]) == ORIGINAL_BYTES
        and sha256(sources[ADAPTER_PATH]) == ADAPTER_SHA256
        and len(sources[ADAPTER_PATH]) == ADAPTER_BYTES
        and sha256(derived) == DERIVED_SHA256 and len(derived) == DERIVED_BYTES
        and (workdir, phase) not in _APPLIED_PHASES,
        "reject omitted, repaired-in-place, foreign, repeated, or incomplete owners",
    )
    for peer in PHASES:
        peer_paths = phase_paths(workdir, family, peer)
        for path in (
            peer_paths["base"], peer_paths["source"],
            peer_paths["source"] / "candidates",
        ):
            info = os.lstat(path)
            require(
                stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid(),
                "precreate both complete owner-only phases before any source apply",
            )
    adapter = kernel.write_fresh(
        paths["source"] / ADAPTER_PATH, sources[ADAPTER_PATH],
        synchronize=False,
    )
    adapter["path"] = sanitized(adapter["path"], workdir, family)
    applied = repair.apply_private(str(paths["source"]), derived)
    require(
        type(applied) is dict and applied.get("status") == "PASS"
        and applied.get("phase") == phase
        and applied.get("source_apply_count") == 1
        and applied.get("derived_sha256") == DERIVED_SHA256
        and applied.get("derived_bytes") == DERIVED_BYTES
        and applied.get("candidate_original_modified") is False,
        "require exactly one genuine frozen private source repair per phase",
    )
    observed, raw = kernel.authenticate_file(
        paths["source"] / ORIGINAL_PATH, expected=DERIVED_SHA256,
        maximum=MAX_SOURCE_BYTES, exact_size=DERIVED_BYTES, capture=True,
    )
    require(
        type(raw) is bytes and raw == derived
        and stat.S_IMODE(os.lstat(paths["source"] / ORIGINAL_PATH).st_mode)
        == 0o600,
        "bind the compiler input to the complete exclusive frozen derived C bytes",
    )
    original = {
        "path": sanitized(observed["path"], workdir, family),
        "sha256": observed["sha256"], "bytes": observed["size_bytes"],
        "device": observed["device"], "inode": observed["inode"],
        "exclusive_creation": True, "same_inode_readback_verified": True,
        "file_fsync_completed": True, "source_overlay": applied,
    }
    _APPLIED_PHASES.add((workdir, phase))
    read_owned(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    read_owned(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    return {ORIGINAL_PATH: original, ADAPTER_PATH: adapter}


def install_v8_build_kernel(v7: types.ModuleType, kernel: types.ModuleType) -> None:
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
    v7: types.ModuleType, kernel: types.ModuleType, workdir: str,
    phase: str, completed: dict[str, Any], steps: list[dict[str, Any]],
) -> dict[str, Any]:
    output = completed.get("native_outputs", {}).get("extension")
    require(type(output) is dict, "require a complete authentic V8 native output")
    path = phase_paths(workdir, FAMILY, phase)["artifact_extension"]
    before, raw = kernel.authenticate_file(
        path, expected=output["sha256"], maximum=MAX_BINARY_BYTES,
        exact_size=output["size_bytes"], capture=True,
    )
    require(
        type(raw) is bytes and len(raw) == before["size_bytes"]
        and sha256(raw) == before["sha256"],
        "capture complete authenticated fresh V8 native ELF bytes",
    )
    parsed = v7.parse_owned_elf64(raw)
    require(
        parsed["file_sha256"] == before["sha256"]
        and parsed["file_size"] == before["size_bytes"]
        and (workdir, phase) not in _RAW_PHASE_ELF,
        "reject reused, incomplete, or unbound original native ELF bytes",
    )
    _RAW_PHASE_ELF[(workdir, phase)] = raw
    streams: dict[str, dict[str, Any]] = {}
    for operation in ("sections", "notes"):
        result = kernel.run_process(
            "extension_" + operation, workdir, FAMILY, phase, steps,
        )
        stdout = result["stdout"]
        require(
            type(stdout) is bytes and (operation != "sections" or bool(stdout)),
            "capture genuine complete V8 ELF inspector streams",
        )
        streams[operation] = {
            "command": "extension_" + operation,
            "stdout_sha256": sha256(stdout), "stdout_bytes": len(stdout),
            "process_pid": result["record"]["pid"],
        }
    after, repeated = kernel.authenticate_file(
        path, expected=before["sha256"], maximum=MAX_BINARY_BYTES,
        exact_size=before["size_bytes"], capture=True,
    )
    require(
        repeated == raw
        and (before["device"], before["inode"])
        == (after["device"], after["inode"]),
        "reject a swapped or changed complete V8 native ELF",
    )
    return {
        "extension": {
            "sections": streams["sections"], "notes": streams["notes"],
            "raw_elf64": parsed,
        },
    }


def verify_derived_reproducible_phases(
    v7: types.ModuleType, workdir: str,
    phases: list[dict[str, Any]], steps: list[dict[str, Any]],
) -> dict[str, Any]:
    require(
        type(phases) is list and len(phases) == 2
        and [phase.get("name") for phase in phases] == list(PHASES)
        and type(steps) is list and len(steps) == 14,
        "require exactly two fully completed seven-process derived-source phases",
    )
    source_identities: set[tuple[int, int]] = set()
    outputs: list[dict[str, Any]] = []
    for phase_index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        require(
            type(owners) is dict and set(owners) == {ORIGINAL_PATH, ADAPTER_PATH},
            "require both complete independently owned V8 source snapshots",
        )
        for relative, digest, size in (
            (ORIGINAL_PATH, DERIVED_SHA256, DERIVED_BYTES),
            (ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES),
        ):
            owner = owners.get(relative)
            require(
                type(owner) is dict and owner.get("sha256") == digest
                and owner.get("bytes") == size
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int
                and (owner["device"], owner["inode"]) not in source_identities,
                "reject original, changed, reused, or linked V8 phase source owners",
            )
            source_identities.add((owner["device"], owner["inode"]))
        overlay = owners[ORIGINAL_PATH].get("source_overlay")
        require(
            type(overlay) is dict and overlay.get("status") == "PASS"
            and overlay.get("phase") == PHASES[phase_index]
            and overlay.get("source_apply_count") == 1
            and overlay.get("derived_sha256") == DERIVED_SHA256
            and overlay.get("derived_bytes") == DERIVED_BYTES,
            "require one original frozen repair application in each actual phase",
        )
        output = phase.get("native_outputs", {}).get("extension")
        require(
            type(output) is dict and output.get("file_name") == EXTENSION_NAME,
            "require an authenticated fresh real C extension in both phases",
        )
        outputs.append(output)
    pids: set[int] = set()
    for index, step in enumerate(steps):
        require(
            type(step) is dict and step.get("name") == PROCESS_NAMES[index % 7]
            and type(step.get("pid")) is int and step["pid"] > 0
            and step["pid"] not in pids and step.get("exit_status") == 0,
            "reject fake, repeated, missing, failed, or reordered compiler processes",
        )
        pids.add(step["pid"])
    first, second = outputs
    require(
        first["sha256"] == second["sha256"]
        and first["size_bytes"] == second["size_bytes"]
        and first["path"] != second["path"]
        and (first["device"], first["inode"])
        != (second["device"], second["inode"])
        and first["audit"] == second["audit"],
        "reject changed or non-reproducible independently owned V8 native artifacts",
    )
    a, b = (
        _RAW_PHASE_ELF.get((workdir, PHASES[0])),
        _RAW_PHASE_ELF.get((workdir, PHASES[1])),
    )
    require(
        type(a) is bytes and type(b) is bytes
        and sha256(a) == first["sha256"]
        and sha256(b) == second["sha256"] and a == b,
        "compare only both complete authenticated exact actual native ELF artifacts",
    )
    compared = v7.compare_owned_elf64(a, b)
    require(
        compared.get("byte_identical") is True,
        "the complete owned raw V8 native ELF comparison was not identical",
    )
    read_owned(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    read_owned(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    return {
        "independent_fresh_phase_count": 2,
        "derived_source_apply_count": 2,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        "original_source_modified": False,
        "byte_identical": True,
        "unique_process_count": 14,
        "raw_elf_comparison": compared,
        "native_outputs": {
            "extension": {
                "file_name": EXTENSION_NAME, "sha256": first["sha256"],
                "size_bytes": first["size_bytes"],
                "fresh_independent_inode_count": 2,
                "reproduced_in_two_fresh_directories": True,
                "audit": first["audit"],
            },
        },
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
        "require an exact safe nonempty bounded V8 evidence label",
    )
    return value


def evidence_names(label: str, *, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "choose an actual V8 success or failure")
    base = "native-source-build-v8-c-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def publish_report(
    kernel: types.ModuleType, report: dict[str, Any], label: str,
) -> dict[str, Any]:
    require(
        type(report) is dict and report.get("status") in ("PASS", "FAIL"),
        "publish only an actual complete V8 build or an honest durable failure",
    )
    failed = report["status"] == "FAIL"
    archive_name, receipt_name = evidence_names(label, failure=failed)
    directory = ROOT / EVIDENCE_RELATIVE
    kernel.mkdir_private(directory)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES, "bound the complete V8 build report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(
        0 < len(archive) <= MAX_ARCHIVE_BYTES,
        "bound one complete deterministic V8 gzip evidence archive",
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
        "expected_v8_compiler_process_count": 14,
        "actual_v8_compiler_process_count": report.get(
            "actual_v8_compiler_process_count", 0,
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
        "bound the complete authentic V8 durable evidence receipt",
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
    require(type(arguments) is list, "require complete explicit V8 arguments")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(
        bool(arguments) and arguments[0] in ("--verify-context", "--build"),
        "select exactly --self-test, --verify-context, or --build",
    )
    mode = "verify-context" if arguments[0] == "--verify-context" else "build"
    scalar = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--family": "family", "--label": "label",
    }
    result: dict[str, Any] = {"mode": mode, "owned_source_sha256": []}
    cursor = 1
    while cursor < len(arguments):
        name = arguments[cursor]
        require(cursor + 1 < len(arguments), "reject a missing V8 flag value")
        value = arguments[cursor + 1]
        if name == "--owned-source-sha256":
            require(mode == "build", "source-owner pins require an explicit build")
            result["owned_source_sha256"].append(value)
        else:
            require(
                name in scalar and scalar[name] not in result,
                "reject a repeated, foreign, shell, or unsupported V8 argument",
            )
            result[scalar[name]] = value
        cursor += 2
    require(
        all(key in result for key in (
            "source_sha256", "protocol_sha256", "contract_sha256",
        )),
        "pin the exact independent V8 recorder, protocol, and machine contract",
    )
    if mode == "verify-context":
        require(
            "family" not in result and "label" not in result
            and not result["owned_source_sha256"],
            "verification cannot authorize a build, source apply, or evidence owner",
        )
    else:
        require(
            result.get("family") == FAMILY and "label" in result,
            "explicitly select the frozen C family and a fresh evidence label",
        )
        checked_label(result["label"])
        values = result["owned_source_sha256"]
        require(
            type(values) is list and len(values) == 2
            and set(values) == {
                ORIGINAL_PATH + "=" + ORIGINAL_SHA256,
                ADAPTER_PATH + "=" + ADAPTER_SHA256,
            },
            "independently pin both complete original first-party C source owners",
        )
    return result


def run_build(arguments: dict[str, Any]) -> dict[str, Any]:
    global _ACTIVE_KERNEL, _ACTIVE_REPAIR, _ACTIVE_DERIVED
    require(arguments.get("mode") == "build", "require an explicit V8 native build")
    context = verify_context(arguments)
    label = checked_label(arguments["label"])
    v7 = load_frozen_module(
        "_rebar_phase2_exact_frozen_v8_build_v7_kernel",
        V7_OWNERS["source"],
    )
    repair = load_frozen_module(
        "_rebar_phase2_exact_frozen_v8_build_repair_v1",
        REPAIR_OWNERS["source"],
    )
    kernel = v7.load_frozen_v4()
    original, _ = read_owned(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    adapter, _ = read_owned(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    derived = repair.repaired_source(original, ORIGINAL_SHA256, ORIGINAL_BYTES)
    require(
        len(derived) == DERIVED_BYTES and sha256(derived) == DERIVED_SHA256,
        "derive only the exact fully frozen first-party private C compiler input",
    )
    for failed in (False, True):
        for name in evidence_names(label, failure=failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE_RELATIVE / name)
    require(
        _ACTIVE_KERNEL is None and _ACTIVE_REPAIR is None and _ACTIVE_DERIVED is None,
        "reject a reused, nested, or re-entrant V8 private build kernel",
    )
    _ACTIVE_KERNEL, _ACTIVE_REPAIR, _ACTIVE_DERIVED = kernel, repair, derived
    install_v8_build_kernel(v7, kernel)
    workdir = tempfile.mkdtemp(prefix=WORK_PREFIX + FAMILY + "-", dir="/tmp")
    checked_workdir(workdir, FAMILY)
    steps: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []
    try:
        prepare_private_phases(kernel, workdir)
        sources = {ORIGINAL_PATH: original, ADAPTER_PATH: adapter}
        for phase in PHASES:
            result = kernel.exact_build_phase(
                workdir, FAMILY, phase, sources, steps,
            )
            result["native_forensics"] = record_native_forensics(
                v7, kernel, workdir, phase, result, steps,
            )
            completed.append(result)
        reproduction = verify_derived_reproducible_phases(
            v7, workdir, completed, steps,
        )
        report = {
            "schema": SCHEMA, "version": 8, "status": "PASS",
            "family": FAMILY, "label": label,
            "source_sha256": arguments["source_sha256"],
            "protocol_sha256": arguments["protocol_sha256"],
            "contract_sha256": arguments["contract_sha256"],
            "frozen_context": context,
            "original_source_sha256": ORIGINAL_SHA256,
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_apply_count": 2,
            "expected_v8_compiler_process_count": 14,
            "actual_v8_compiler_process_count": len(steps),
            "phase_count": 2, "phases": completed,
            "compiler_processes": steps, "reproducibility": reproduction,
            "candidate_correctness": "NOT MEASURED",
            "candidate_processes_started": 0, "candidate_imports": 0,
            "native_libraries_loaded": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }
        return publish_report(kernel, report, label)
    except Exception as error:
        read_owned(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        read_owned(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
        report = {
            "schema": SCHEMA, "version": 8, "status": "FAIL",
            "family": FAMILY, "label": label,
            "source_sha256": arguments["source_sha256"],
            "protocol_sha256": arguments["protocol_sha256"],
            "contract_sha256": arguments["contract_sha256"],
            "frozen_context": context,
            "original_source_sha256": ORIGINAL_SHA256,
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_apply_count": sum(
                (workdir, phase) in _APPLIED_PHASES for phase in PHASES
            ),
            "expected_v8_compiler_process_count": 14,
            "actual_v8_compiler_process_count": len(steps),
            "phase_count": len(completed), "phases": completed,
            "compiler_processes": steps,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "candidate_correctness": "NOT MEASURED",
            "candidate_processes_started": 0, "candidate_imports": 0,
            "native_libraries_loaded": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
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
