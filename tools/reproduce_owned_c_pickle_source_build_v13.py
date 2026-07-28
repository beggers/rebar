#!/usr/bin/env python3
"""Freeze an offline, independently owned, two-phase C pickle-repair build.

Version 13 is deliberately unavailable until all four version-26 overview
owners have been independently released and caller-pinned. Source verification
never builds, imports a candidate, promotes a native target, samples a clock,
opens the holdout, or rewrites an existing source or evidence owner.
"""

from __future__ import annotations

import argparse
import builtins
import copy
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
import traceback
import types
from typing import Any
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/reproduce_owned_c_pickle_source_build_v13.py"
PROTOCOL = "oracle/phase2/C-PICKLE-SOURCE-BUILD-V13.md"
CONTRACT = "oracle/phase2/c-pickle-source-build-v13.json"
EVIDENCE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-c-pickle-source-build-v13"
VERSION = 13
FAMILY = "c"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
)
SUITES = (
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
MAX_SOURCE = 16 * 1024 * 1024
MAX_REPORT = 48 * 1024 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_LABEL = 48
ORIGINAL = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185,
)
ADAPTER = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707,
)
V1_DERIVED = (
    "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d",
    218308,
)
V2_DERIVED = (
    "8b35fba5b565ae18c5b9c180bec1dfbfb46b75bf3db7421626da4a73cdda2b94",
    219227,
)
V12 = {
    "source": (
        "tools/reproduce_owned_c_pickle_source_build_v12.py",
        "654e4dea29b9f687a27b53fa18b2f345e29042a03ea4b507594e87fa3e4a161f",
        61735,
    ),
    "protocol": (
        "oracle/phase2/C-PICKLE-SOURCE-BUILD-V12.md",
        "aecb2cacfc5397a46e2d123767d4b7bf39935d1bda95d3b0d0cf8058614769ac",
        3307,
    ),
    "contract": (
        "oracle/phase2/c-pickle-source-build-v12.json",
        "5c3bc3487962c9b66cd63155a0ca0d7fc18aa4debac47ee9a75123a678d800b3",
        8216,
    ),
}
REPAIR_V2 = {
    "source": (
        "tools/apply_owned_first_party_source_repair_v2.py",
        "1bb4f21cca20928b1c8993b3646825ac04ad46a231633105e5cb2469fd8434c0",
        65872,
    ),
    "protocol": (
        "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V2.md",
        "a91fd1615d25597109c11605fdbeadd1673137cdd819b326bfff5dfb5699b611",
        3530,
    ),
    "contract": (
        "oracle/phase2/first-party-source-repair-v2.json",
        "875b9402f535b94a1391bc3a1821ac347f67f09b2341c9a7a489a79b7dd9cf48",
        7986,
    ),
}
# All four owners were independently and explicitly released before use.
V26: dict[str, tuple[str, str, int]] = {
    "source": (
        "tools/render_candidate_current_overview_v26.py",
        "55c36e916f0da8b9ef7b6992724d1d1f98161e834f4d2d21729663d9671a3982",
        80805,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v26.inputs.json",
        "c29e8df08d9b5a03eaad283b625465ba6638f19f69d7d3ab4ea5512e83c37685",
        36434,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v26.json",
        "8ebf2ccb74ae2cf62196a1507f94bd39ff4b103122c450865121306accf71f48",
        186394,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v26.svg",
        "52b42c7ceccf45f80777d94820a812c7f8e0f790fba03a57aef28c11573dd9cc",
        12936,
    ),
}
ZIG_FAILURE_ARCHIVE_SHA256 = (
    "1cb38eb48a2d3305ea98d5103a27ce6ae758137168f68df07a408dec3d055a37"
)
ZIG_FAILURE_RECEIPT_SHA256 = (
    "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23"
)
ZIG_FAILURE_ARCHIVE = (
    "oracle/phase2/evidence/"
    "zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-"
    "original-p0-failures.json.gz",
    ZIG_FAILURE_ARCHIVE_SHA256,
    3711,
)
ZIG_FAILURE_RECEIPT = (
    "oracle/phase2/evidence/"
    "zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-"
    "original-p0-failures-publication-receipt.json",
    ZIG_FAILURE_RECEIPT_SHA256,
    1992,
)
ZIG_FAILURE_PLAIN_SHA256 = (
    "df0c3cff6b6f956b58fe43f828d6b8d26efc8b9b0dac8972ae4f9902dd58302d"
)
ZIG_FAILURE_PLAIN_BYTES = 9482
P0 = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
PUBLIC_ARCHIVE = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_types_v1.json.gz",
    "bd0f8ed8691785c33c0fdb4d0a506808c959d1e412d655d742d5a4ea46808ce4",
    206151,
)
PUBLIC_RECEIPT = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-"
    "public_types_v1-publication-receipt.json",
    "5548f27728cfb8e9d941aa9a3d6c4220d889d82707384d73f41f5a2ec92e3964",
    1471,
)
_BUILD_ACTIVE = False


class BuildError(Exception):
    """Reject an unproven V13 source, current graph, or actual build."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise BuildError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete original evidence bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, RecursionError,
            OverflowError) as error:
        raise BuildError("require exact finite first-party canonical JSON") from error


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require a released complete SHA-256: " + label)
    return value


def relative_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded exact first-party path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value
            and 0 < len(path.parts) <= 16
            and all(item not in {"", ".", ".."} for item in path.parts),
            "reject escaped, broad, noncanonical, or linked owner paths")
    return path.parts


def read_owner(relative: str, expected: str,
               exact_size: int | None = None,
               *, owner_only: bool = False) -> tuple[bytes, dict[str, Any]]:
    parts = relative_parts(relative)
    checked_digest(expected, relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    parent = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            child = os.open(part, flags | os.O_DIRECTORY, dir_fd=parent)
            os.close(parent)
            parent = child
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        try:
            first = os.fstat(descriptor)
            named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISREG(first.st_mode)
                    and (first.st_dev, first.st_ino, first.st_size)
                    == (named.st_dev, named.st_ino, named.st_size)
                    and 0 < first.st_size <= MAX_ARCHIVE
                    and (exact_size is None or first.st_size == exact_size)
                    and (not owner_only or stat.S_IMODE(first.st_mode) == 0o600),
                    "reject substituted, nonprivate, truncated, or oversized owner")
            blocks: list[bytes] = []
            remaining = first.st_size
            while remaining:
                block = os.read(descriptor, min(remaining, 1048576))
                require(type(block) is bytes and bool(block),
                        "require every exact first-party source or archive byte")
                blocks.append(block)
                remaining -= len(block)
            require(os.read(descriptor, 1) == b"",
                    "reject hidden bytes appended to authenticated evidence")
            raw = b"".join(blocks)
            last = os.fstat(descriptor)
            require((first.st_dev, first.st_ino, first.st_size,
                     first.st_mtime_ns, first.st_ctime_ns)
                    == (last.st_dev, last.st_ino, last.st_size,
                        last.st_mtime_ns, last.st_ctime_ns)
                    and digest(raw) == expected,
                    "reject a changed, substituted, or incorrectly hashed owner")
            return raw, {
                "path": relative, "sha256": expected,
                "bytes": first.st_size, "device": first.st_dev,
                "inode": first.st_ino, "mode": stat.S_IMODE(first.st_mode),
            }
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)


def unique_json(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        require(type(key) is str and key not in result,
                "reject repeated fields in immutable current evidence")
        result[key] = value
    return result


def document(raw: bytes, label: str,
             *, exact: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE,
            "bound complete first-party evidence: " + label)
    try:
        result = json.loads(raw.decode("utf-8", "strict"),
                            object_pairs_hook=unique_json,
                            parse_constant=lambda item: (_ for _ in ()).throw(
                                ValueError("nonfinite evidence: " + item)))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("reject malformed frozen evidence: " + label) from error
    require(type(result) is dict and (not exact or canonical(result) == raw),
            "reject noncanonical or changed actual evidence: " + label)
    return result


def pin(owner: tuple[str, str, int]) -> dict[str, Any]:
    path, fingerprint, size = owner
    checked_digest(fingerprint, path)
    require(type(size) is int and 0 < size <= MAX_ARCHIVE,
            "require one genuine exact first-party owner size")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def released_v26() -> dict[str, tuple[str, str, int]]:
    require(type(V26) is dict and set(V26) == {"source", "inputs", "summary", "svg"},
            "require exactly four independently published current V26 graph owners")
    result: dict[str, tuple[str, str, int]] = {}
    for role, row in V26.items():
        require(type(row) is tuple and len(row) == 3,
                "never run V13 before explicit four-owner V26 release")
        relative, fingerprint, size = row
        relative_parts(relative)
        checked_digest(fingerprint, "released V26 " + role)
        require(type(size) is int and 0 < size <= MAX_ARCHIVE,
                "require the actual independently published V26 owner byte count")
        result[role] = (relative, fingerprint, size)
    return result


def load_module(owner: tuple[str, str, int], name: str) -> types.ModuleType:
    raw, _ = read_owner(*owner)
    require(name not in sys.modules,
            "reject reused, substituted, or third-party build modules")
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / owner[0])
    module.__package__ = None
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    _, after = read_owner(*owner)
    require(after["sha256"] == owner[1]
            and os.path.abspath(str(module.__file__)) == str(ROOT / owner[0]),
            "reject a first-party source changed during authenticated load")
    return module


class SourceOnlyWall:
    """Block every genuine filesystem, compiler, candidate, and clock effect."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = 0
        self.modules: frozenset[str] = frozenset()

    def install(self, owner: Any, name: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def denied(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked += 1
            raise BuildError("source-only operation rejected: " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyWall:
        self.modules = frozenset(sys.modules)
        for owner, names in (
            (builtins, ("open",)), (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "unlink", "remove", "replace", "rename",
                  "system", "fork", "posix_spawn", "pipe", "fsync")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "resolve", "mkdir",
                    "unlink", "rename", "replace")),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: Any, _value: Any, _tb: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)
        require(frozenset(sys.modules) == self.modules,
                "source-only C V13 verification imported a module")


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL
            and all(character.isascii()
                    and (character.isalnum() or character in "-_")
                    for character in value),
            "require one bounded fresh first-party C build label")
    return value


def evidence_names(label: str, *, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool,
            "explicitly retain the true passing or failing C build")
    stem = "native-source-build-v13-c-" + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def synthetic_schedule(phases: Any, processes: Any) -> dict[str, Any]:
    require(type(phases) is list and len(phases) == 2
            and type(processes) is list and len(processes) == 14,
            "require exactly two first-party phases and fourteen real build observations")
    owners: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        require(type(phase) is dict and phase.get("name") == PHASES[index]
                and phase.get("source_sha256") == V2_DERIVED[0]
                and phase.get("source_bytes") == V2_DERIVED[1]
                and phase.get("adapter_sha256") == ADAPTER[1]
                and phase.get("source_apply_count") == 1
                and type(phase.get("source_device")) is int
                and type(phase.get("source_inode")) is int
                and (phase["source_device"], phase["source_inode"]) not in owners,
                "reject missing, cross-family, borrowed, or duplicate source overlays")
        owners.add((phase["source_device"], phase["source_inode"]))
    pids: set[int] = set()
    for index, process in enumerate(processes):
        require(type(process) is dict
                and process.get("phase") == PHASES[index // len(PROCESS_NAMES)]
                and process.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and type(process.get("pid")) is int
                and process["pid"] > 0 and process["pid"] not in pids
                and process.get("exit_status") == 0,
                "reject a missing, fake, external, reordered, or failed build process")
        pids.add(process["pid"])
    return {"phase_count": 2, "unique_process_count": 14,
            "source_apply_count": 2, "independent_source_owner_count": 2}


def synthetic_history(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("historical_v25_repository_evidence_owner_count") == 139
            and value.get("historical_v25_authenticated_reference_count") == 144
            and value.get("current_v26_repository_evidence_owner_count") == 141
            and value.get("current_v26_authenticated_reference_count") == 146
            and value.get("actual_zig_failure_archive_sha256")
            == ZIG_FAILURE_ARCHIVE_SHA256
            and value.get("actual_zig_failure_receipt_sha256")
            == ZIG_FAILURE_RECEIPT_SHA256
            and value.get("actual_zig_failure_status") == "FAIL"
            and value.get("historical_c_semantic_mismatch_count") == 1262
            and value.get("historical_c_candidate_worker_count") == 13
            and value.get("actual_original_pickle_record_count") == 96
            and value.get("actual_original_legacy_pickle_mismatch_count") == 32
            and value.get("actual_original_modern_pickle_record_count") == 64
            and value.get("qualified_candidate_count") == 0
            and value.get("holdout") == "NOT OPENED",
            "preserve distinct actual V25/V26 history, Zig failure, and C pickle losses")
    return value


def self_test() -> dict[str, Any]:
    graph = released_v26()
    phases = [{"name": phase,
               "source_sha256": V2_DERIVED[0],
               "source_bytes": V2_DERIVED[1],
               "adapter_sha256": ADAPTER[1],
               "source_apply_count": 1,
               "source_device": 17,
               "source_inode": index + 101}
              for index, phase in enumerate(PHASES)]
    processes = [{"phase": PHASES[index // len(PROCESS_NAMES)],
                  "name": PROCESS_NAMES[index % len(PROCESS_NAMES)],
                  "pid": index + 1,
                  "exit_status": 0}
                 for index in range(14)]
    history = {
        "historical_v25_repository_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "current_v26_repository_evidence_owner_count": 141,
        "current_v26_authenticated_reference_count": 146,
        "actual_zig_failure_archive_sha256": ZIG_FAILURE_ARCHIVE_SHA256,
        "actual_zig_failure_receipt_sha256": ZIG_FAILURE_RECEIPT_SHA256,
        "actual_zig_failure_status": "FAIL",
        "historical_c_semantic_mismatch_count": 1262,
        "historical_c_candidate_worker_count": 13,
        "actual_original_pickle_record_count": 96,
        "actual_original_legacy_pickle_mismatch_count": 32,
        "actual_original_modern_pickle_record_count": 64,
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
    }
    accepted = 0
    rejected = 0
    with SourceOnlyWall() as wall:
        require(synthetic_schedule(phases, processes)
                == {"phase_count": 2, "unique_process_count": 14,
                    "source_apply_count": 2,
                    "independent_source_owner_count": 2},
                "authenticate both first-party overlays and fourteen synthetic observations")
        synthetic_history(history)
        accepted += 2

        def reject(operation: Any, label: str) -> None:
            nonlocal rejected
            try:
                operation()
            except (BuildError, OSError, ValueError, TypeError, KeyError, zlib.error):
                rejected += 1
                return
            raise BuildError("accepted hostile C V13 source-only control: " + label)

        for index in range(2):
            for key, replacement in (
                ("name", "cross-family-phase"),
                ("source_sha256", "0" * 64),
                ("source_bytes", V1_DERIVED[1]),
                ("adapter_sha256", "0" * 64),
                ("source_apply_count", 0),
                ("source_apply_count", 2),
            ):
                hostile = copy.deepcopy(phases)
                hostile[index][key] = replacement
                reject(lambda value=hostile: synthetic_schedule(value, processes), key)
        repeated_owner = copy.deepcopy(phases)
        repeated_owner[1]["source_inode"] = repeated_owner[0]["source_inode"]
        reject(lambda: synthetic_schedule(repeated_owner, processes), "reused overlay")
        for index in range(14):
            for key, replacement in (("phase", "foreign"),
                                     ("name", "build_external_regex"),
                                     ("pid", 0), ("exit_status", 1)):
                hostile = copy.deepcopy(processes)
                hostile[index][key] = replacement
                reject(lambda value=hostile: synthetic_schedule(phases, value), key)
        duplicate_pid = copy.deepcopy(processes)
        duplicate_pid[1]["pid"] = duplicate_pid[0]["pid"]
        reject(lambda: synthetic_schedule(phases, duplicate_pid), "duplicate PID")
        reject(lambda: synthetic_schedule(phases[:-1], processes), "omitted phase")
        reject(lambda: synthetic_schedule(phases, processes[:-1]), "omitted process")
        for key, actual in history.items():
            hostile = copy.deepcopy(history)
            hostile[key] = (actual + 1 if type(actual) is int
                            else actual + "-fabricated")
            reject(lambda value=hostile: synthetic_history(value), key)
        for suffix in (False, True):
            archive, receipt = evidence_names("synthetic", failure=suffix)
            require(archive.startswith("native-source-build-v13-c-")
                    and archive.endswith(".json.gz")
                    and receipt.endswith("-publication-receipt.json"),
                    "preserve distinct version-correct future C V13 evidence owners")
            accepted += 1
        for item in ("", "../escape", "/tmp/escape", "a/../b", "a//b",
                     "./owner", "x" * 513):
            reject(lambda value=item: relative_parts(value), "unsafe owner")
        for item in ("", "0" * 63, "0" * 65, "X" * 64):
            reject(lambda value=item: checked_digest(value, "hostile"), "false hash")
        for item in ("", "../../escape", "bad label", "x" * (MAX_LABEL + 1)):
            reject(lambda value=item: checked_label(value), "unsafe future evidence")
        probes = (
            lambda: builtins.open("/tmp/forbidden"),
            lambda: io.open("/tmp/forbidden"),
            lambda: os.open("/tmp/forbidden", os.O_RDONLY),
            lambda: os.read(0, 1),
            lambda: os.write(1, b"x"),
            lambda: os.stat("/tmp"),
            lambda: os.lstat("/tmp"),
            lambda: os.mkdir("/tmp/forbidden"),
            lambda: os.unlink("/tmp/forbidden"),
            lambda: os.replace("/tmp/a", "/tmp/b"),
            lambda: Path("/tmp/x").read_bytes(),
            lambda: Path("/tmp/x").write_bytes(b"x"),
            lambda: Path("/tmp").resolve(),
            lambda: subprocess.run(("true",)),
            lambda: subprocess.Popen(("true",)),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: tempfile.mkstemp(),
            lambda: importlib.import_module("candidates.vm_candidate"),
            lambda: importlib.import_module("re"),
            lambda: threading.Thread().start(),
            lambda: time.time(),
            lambda: time.monotonic(),
            lambda: time.perf_counter(),
            lambda: time.perf_counter_ns(),
            lambda: time.sleep(0),
        )
        for index, probe in enumerate(probes):
            reject(probe, "real forbidden operation " + str(index))
        require(wall.blocked == len(probes) and rejected >= 105,
                "prove all first-party source-only effects and fake histories are blocked")
    return {
        "schema": SCHEMA + "-source-only-self-test", "version": VERSION,
        "family": FAMILY, "status": "PASS",
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_controls": len(probes),
        "released_v26_owner_count": len(graph),
        "historical_v25_repository_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "repository_evidence_owner_count": 141,
        "authenticated_digest_addressed_history_paths": 146,
        "actual_zig_failure_archive_sha256": ZIG_FAILURE_ARCHIVE_SHA256,
        "actual_zig_failure_receipt_sha256": ZIG_FAILURE_RECEIPT_SHA256,
        "future_phase_count": 2,
        "future_process_count_per_phase": 7,
        "future_total_compiler_process_count": 14,
        "future_source_apply_count": 2,
        "historical_c_semantic_mismatch_count": 1262,
        "historical_legacy_pickle_mismatch_count": 32,
        "actual_original_pickle_record_count": 96,
        "actual_original_modern_pickle_record_count": 64,
        "frozen_suite_count": 13,
        "frozen_case_execution_denominator": 31237,
        "frozen_private_waiver_count": 13,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "source_apply_count": 0,
        "workspace_mutations": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == str(ROOT / SELF)
            and os.path.realpath(__file__) == str(ROOT / SELF),
            "use only isolated no-bytecode exact stable CPython 3.14.6")
    require(not any(item == "candidates" or item.startswith("candidates.")
                    for item in sys.modules),
            "never import a C candidate in a frozen native-source context")


def find_exact_history_owner(value: Any, fingerprint: str) -> dict[str, Any]:
    found: list[dict[str, Any]] = []

    def visit(item: Any) -> None:
        if type(item) is dict:
            if item.get("sha256") == fingerprint:
                found.append(item)
            for child in item.values():
                if type(child) in (dict, list):
                    visit(child)
        elif type(item) is list:
            for child in item:
                if type(child) in (dict, list):
                    visit(child)

    visit(value)
    require(bool(found), "the actual Zig failure owner is missing from released V26")
    keys = {
        (item.get("path", item.get("relative")),
         item.get("sha256"), item.get("bytes", item.get("size_bytes")))
        for item in found
    }
    require(len(keys) == 1,
            "reject ambiguous or conflicting repeated V26 Zig failure references")
    relative, actual_hash, size = next(iter(keys))
    require(type(relative) is str and type(size) is int
            and checked_digest(actual_hash, "genuine Zig failure owner") == fingerprint,
            "require one complete authentic V26 Zig failure evidence owner")
    return {"path": relative, "sha256": actual_hash, "bytes": size}


def bounded_archive(raw: bytes, label: str) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE,
            "bound the independently published actual Zig failure archive")
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = inflater.decompress(raw, MAX_REPORT + 1)
    except zlib.error as error:
        raise BuildError("reject malformed actual gzip: " + label) from error
    require(len(plain) <= MAX_REPORT and inflater.eof
            and not inflater.unused_data and not inflater.unconsumed_tail,
            "reject oversized, truncated, chained, or trailing actual Zig evidence")
    return plain


def expected_contract(source_pin: str, protocol_pin: str,
                      previous_contract: dict[str, Any],
                      current: dict[str, Any]) -> dict[str, Any]:
    graph = released_v26()
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "family": FAMILY, "phase": "SOURCE FREEZE; NO ACTUAL BUILD",
        "source": {"path": SELF,
                   "sha256": checked_digest(source_pin, "C V13 source")},
        "protocol": {"path": PROTOCOL,
                     "sha256": checked_digest(protocol_pin, "C V13 protocol")},
        "runtime": {"implementation": "CPython", "version": "3.14.6",
                    "path": PYTHON, "sha256": PYTHON_SHA256},
        "oracle": {"manifest": pin(P0), "suite_count": 13,
                   "suite_ids": [name for name, _, _ in SUITES],
                   "case_execution_denominator": 31237,
                   "private_waiver_count": 13},
        "inherited_v12": {
            "owners": {role: pin(owner) for role, owner in V12.items()},
            "contract_sha256": V12["contract"][1],
            "published_v25_repository_evidence_owner_count": 139,
            "published_v25_authenticated_reference_count": 144,
            "historical_c_semantic_mismatch_count": 1262,
            "actual_c_candidate_worker_count": 13,
            "actual_c_completed_suite_count": 13,
            "actual_c_fully_passing_suite_count": 8,
            "actual_c_verified_passing_case_count": 7325,
            "actual_c_infrastructure_failure_count": 0,
        },
        "published_v26": {
            "graph": {role: pin(owner) for role, owner in graph.items()},
            "graph_owner_count": 4,
            "repository_evidence_owner_count": 141,
            "authenticated_digest_addressed_history_paths": 146,
            "actual_zig_failure_archive": current["zig_archive"],
            "actual_zig_failure_receipt": current["zig_receipt"],
            "actual_zig_failure_status": "FAIL",
            "qualified_candidate_count": 0,
        },
        "frozen_pickle_repair": {
            "owners": {role: pin(owner) for role, owner in REPAIR_V2.items()},
            "derived_source": {"sha256": V2_DERIVED[0],
                               "bytes": V2_DERIVED[1],
                               "materialized_during_source_freeze": False},
            "original_source": pin(ORIGINAL),
            "unchanged_adapter": pin(ADAPTER),
            "v1_buffer_repaired_source": {"sha256": V1_DERIVED[0],
                                           "bytes": V1_DERIVED[1]},
            "legacy_protocols": [0, 1],
            "modern_protocol_rejection_preserved": [2, 3, 4, 5],
            "actual_original_pickle_record_count": 96,
            "actual_original_legacy_pickle_mismatch_count": 32,
            "actual_original_legacy_protocol_counts": {"0": 16, "1": 16},
            "actual_original_modern_protocol_counts":
                {"2": 16, "3": 16, "4": 16, "5": 16},
            "actual_public_type_archive": pin(PUBLIC_ARCHIVE),
            "actual_public_type_receipt": pin(PUBLIC_RECEIPT),
            "actual_public_type_case_count": 6912,
            "actual_public_type_mismatch_count": 248,
            "owned_reconstructor": "VMModuleState.scanner_reconstructor",
            "owned_match_type": "VMModuleState.match_type",
        },
        "future_build_policy": {
            "explicit_build_required": True,
            "root_parent": "/tmp",
            "root_prefix": "rebar-phase2-native-build-v8-c-",
            "phase_names": list(PHASES), "phase_count": 2,
            "both_peer_phases_precreated_before_first_apply": True,
            "original_source_sha256": ORIGINAL[1],
            "adapter_source_sha256": ADAPTER[1],
            "private_compiler_input_sha256": V2_DERIVED[0],
            "private_compiler_input_bytes": V2_DERIVED[1],
            "source_owners_per_phase": 2,
            "v2_source_apply_count_per_phase": 1,
            "future_total_source_apply_count": 2,
            "process_names_per_phase": list(PROCESS_NAMES),
            "process_count_per_phase": 7,
            "future_total_compiler_process_count": 14,
            "directory_mode": "0700",
            "source_file_mode": "0600",
            "source_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "full_native_elf_forensics": True,
            "reproducibility": "TWO DISTINCT SOURCE OWNERS AND IDENTICAL ELF",
            "external_engine": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "network": "FORBIDDEN",
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "workspace_source_mutation": "FORBIDDEN",
        },
        "future_evidence": {
            "directory": EVIDENCE,
            "archive_prefix": "native-source-build-v13-c-",
            "archive_suffix": ".json.gz",
            "failure_suffix": "-failures",
            "receipt_suffix": "-publication-receipt.json",
            "owner_mode": "0600",
            "exclusive_creation": True,
            "archive_and_directory_fsync": True,
            "receipt_and_directory_fsync": True,
            "passing_build_does_not_qualify_candidate": True,
            "published_only_during_explicit_build": True,
        },
        "phase_boundary": {
            "candidate_correctness": "NOT MEASURED",
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "source_apply_count": 0,
            "workspace_mutations": 0,
            "network_requests": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def verify_released_graph() -> dict[str, Any]:
    graph = released_v26()
    owners: dict[str, dict[str, Any]] = {}
    raw_owners: dict[str, bytes] = {}
    decoded: dict[str, dict[str, Any]] = {}
    identities: set[tuple[int, int]] = set()
    for role, expected in graph.items():
        raw, owner = read_owner(*expected)
        identity = (owner["device"], owner["inode"])
        require(identity not in identities,
                "require four genuinely distinct released V26 overview owners")
        identities.add(identity)
        owners[role] = owner
        raw_owners[role] = raw
        if role in {"inputs", "summary"}:
            decoded[role] = document(raw, "released exact V26 " + role)
    renderer = load_module(graph["source"],
                           "_rebar_exact_released_v26_for_owned_c_pickle_v13")
    require(getattr(renderer, "SCHEMA", None)
            == "rebar-candidate-current-overview-v26"
            and getattr(renderer, "SELF", None) == graph["source"][0]
            and tuple(getattr(renderer, "FAILURE_ARCHIVE", ())[:3])
            == ZIG_FAILURE_ARCHIVE
            and tuple(getattr(renderer, "FAILURE_RECEIPT", ())[:3])
            == ZIG_FAILURE_RECEIPT,
            "use only the exact released first-party V26 renderer and genuine Zig owners")
    snapshot, output_rows = renderer.build(
        graph["source"][1], ZIG_FAILURE_ARCHIVE_SHA256,
        ZIG_FAILURE_RECEIPT_SHA256)
    require(type(snapshot) is dict
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 141
            and snapshot.get("all_digest_addressed_history_path_count") == 146
            and type(output_rows) is tuple and len(output_rows) == 3,
            "independently reproduce the genuine complete 141-owner, 146-reference graph")
    rebuilt = dict(output_rows)
    require(len(rebuilt) == 3
            and all(rebuilt.get(graph[role][0]) == raw_owners[role]
                    for role in ("inputs", "summary", "svg")),
            "independently reproduce all three exact released V26 overview outputs")
    inputs, summary = decoded["inputs"], decoded["summary"]
    require(inputs.get("version") == 26
            and inputs.get("repository_evidence_owner_count") == 141
            and inputs.get("all_digest_addressed_history_path_count") == 146
            and inputs.get("candidate_qualified_count") == 0
            and summary.get("repository_evidence_owner_count") == 141
            and summary.get("authenticated_digest_addressed_history_paths") == 146
            and summary.get("qualified_candidate_count") == 0,
            "reject fabricated V26 owners, obsolete V25 totals, or invented winners")
    archive_pin = find_exact_history_owner(inputs, ZIG_FAILURE_ARCHIVE_SHA256)
    receipt_pin = find_exact_history_owner(inputs, ZIG_FAILURE_RECEIPT_SHA256)
    require(archive_pin == pin(ZIG_FAILURE_ARCHIVE)
            and receipt_pin == pin(ZIG_FAILURE_RECEIPT),
            "pin the actual exact published Zig failure paths, hashes, and sizes")
    archive_raw, archive_owner = read_owner(
        archive_pin["path"], archive_pin["sha256"], archive_pin["bytes"],
        owner_only=True)
    receipt_raw, receipt_owner = read_owner(
        receipt_pin["path"], receipt_pin["sha256"], receipt_pin["bytes"],
        owner_only=True)
    require((archive_owner["device"], archive_owner["inode"])
            != (receipt_owner["device"], receipt_owner["inode"]),
            "preserve both distinct mode-0600 published Zig failure owners")
    receipt = document(receipt_raw, "genuine Zig failure publication receipt")
    plain = bounded_archive(archive_raw, "actual Zig failure")
    report = document(plain, "actual Zig failure archive")
    require(report.get("status") == "FAIL"
            and (report.get("family") == "zig"
                 or report.get("candidate_family") == "zig")
            and receipt.get("status") == "PASS"
            and receipt.get("preserved_failure_status") == "FAIL"
            and (receipt.get("family") == "zig"
                 or receipt.get("candidate_family") == "zig")
            and report.get("failure_class")
            == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
            and receipt.get("failure_class")
            == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
            and report.get("actual_candidate_workers") == 0
            and report.get("actual_matching_case_execution_count") == 0
            and receipt.get("actual_candidate_workers") == 0
            and receipt.get("actual_matching_case_execution_count") == 0
            and receipt.get("actual_native_activations") == 0
            and len(plain) == ZIG_FAILURE_PLAIN_BYTES
            and digest(plain) == ZIG_FAILURE_PLAIN_SHA256
            and receipt.get("uncompressed_bytes") == ZIG_FAILURE_PLAIN_BYTES
            and receipt.get("uncompressed_sha256") == ZIG_FAILURE_PLAIN_SHA256,
            "never reinterpret an authentic Zig candidate failure as a PASS")
    return {"owners": owners, "inputs": inputs, "summary": summary,
            "zig_archive": archive_pin, "zig_receipt": receipt_pin,
            "zig_archive_owner": archive_owner,
            "zig_receipt_owner": receipt_owner,
            "zig_failure_report": report,
            "zig_failure_publication_receipt": receipt}


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None
                   ) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    released_v26()
    read_owner(SELF, checked_digest(source_pin, "C V13 source"))
    read_owner(PROTOCOL, checked_digest(protocol_pin, "C V13 protocol"))
    previous = load_module(V12["source"],
                           "_rebar_exact_owned_c_pickle_v13_v12")
    require(previous.SCHEMA == "rebar-phase2-owned-c-pickle-source-build-v12"
            and previous.FAMILY == FAMILY
            and tuple(previous.PHASES) == PHASES
            and tuple(previous.PROCESS_NAMES) == PROCESS_NAMES
            and tuple(previous.SUITES) == SUITES
            and tuple(previous.ORIGINAL) == ORIGINAL
            and tuple(previous.ADAPTER) == ADAPTER
            and tuple(previous.V1_DERIVED) == V1_DERIVED
            and tuple(previous.V2_DERIVED) == V2_DERIVED
            and previous.V2 == REPAIR_V2,
            "independently inherit the complete immutable V12 two-overlay builder")
    inherited_contract, active = previous.verify_context(
        V12["source"][1], V12["protocol"][1], V12["contract"][1])
    require(type(inherited_contract) is dict
            and inherited_contract.get("schema") == previous.SCHEMA + "-source-freeze"
            and inherited_contract.get("version") == 12
            and digest(canonical(inherited_contract)) == V12["contract"][1]
            and inherited_contract.get("published_v25", {})
            .get("repository_evidence_owner_count") == 139
            and inherited_contract.get("published_v25", {})
            .get("authenticated_digest_addressed_history_paths") == 144
            and inherited_contract.get("published_v25", {})
            .get("actual_c_semantic_mismatch_count") == 1262
            and inherited_contract.get("published_v25", {})
            .get("actual_c_candidate_workers") == 13,
            "preserve the separately pinned authentic V25 history without revision")
    repair = active.get("repair")
    repair_contract = active.get("repair_contract")
    derived = active.get("derived")
    require(repair is not None
            and getattr(repair, "SCHEMA", None)
            == "rebar-phase2-owned-first-party-source-repair-v2"
            and type(repair_contract) is dict
            and digest(canonical(repair_contract)) == REPAIR_V2["contract"][1]
            and type(derived) is bytes and digest(derived) == V2_DERIVED[0]
            and len(derived) == V2_DERIVED[1],
            "require the exact independently authored two-stage private C overlay")
    history = repair_contract.get("current_history")
    observed = repair_contract.get("actual_public_type_evidence")
    require(type(history) is dict
            and history.get("published_graph_version") == 25
            and history.get("repository_evidence_owner_count") == 139
            and history.get("authenticated_digest_addressed_history_paths") == 144
            and history.get("actual_c_semantic_mismatch_count") == 1262
            and type(observed) is dict
            and observed.get("case_execution_denominator") == 6912
            and observed.get("complete_record_count") == 6912
            and observed.get("observed_mismatch_count") == 248
            and observed.get("pickle_record_count") == 96
            and observed.get("legacy_pickle_mismatch_count") == 32
            and observed.get("legacy_pickle_protocol_counts")
            == {"0": 16, "1": 16}
            and observed.get("preserved_modern_pickle_protocol_counts")
            == {"2": 16, "3": 16, "4": 16, "5": 16},
            "preserve every actual original C buffer and pickle defect")
    current = verify_released_graph()
    contract = expected_contract(source_pin, protocol_pin,
                                 inherited_contract, current)
    if contract_pin is not None:
        raw, _ = read_owner(CONTRACT,
                            checked_digest(contract_pin, "C V13 contract"))
        require(raw == canonical(contract)
                and document(raw, "genuinely frozen C V13 machine") == contract,
                "authenticate the complete released C V13 source/build freeze")
    require(not any(item == "candidates" or item.startswith("candidates.")
                    for item in sys.modules),
            "read-only verification must never import a candidate engine")
    return contract, {"v12": previous, "active": active,
                      "current_graph": current,
                      "inherited_v12_contract": inherited_contract}


def publish_report(kernel: types.ModuleType, report: dict[str, Any],
                   label: str) -> dict[str, Any]:
    require(type(report) is dict and report.get("status") in {"PASS", "FAIL"}
            and report.get("family") == FAMILY
            and report.get("label") == checked_label(label),
            "publish only an actual complete first-party V13 source build")
    archive_name, receipt_name = evidence_names(
        label, failure=report["status"] == "FAIL")
    directory = ROOT / EVIDENCE
    kernel.mkdir_private(directory)
    plain = canonical(report)
    require(0 < len(plain) <= MAX_REPORT,
            "preserve the entire authentic C V13 offline source-build report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_ARCHIVE,
            "bound deterministic actual first-party source-build gzip evidence")
    archive = kernel.write_fresh(directory / archive_name, compressed,
                                 synchronize=True)
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "version": VERSION, "status": "PASS",
        "build_status": report["status"],
        "family": FAMILY, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "archive_relative": EVIDENCE + "/" + archive_name,
        "archive_sha256": archive["sha256"],
        "archive_bytes": archive["bytes"],
        "archive_publication": archive,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "original_source_sha256": ORIGINAL[1],
        "v1_derived_source_sha256": V1_DERIVED[0],
        "v2_derived_source_sha256": V2_DERIVED[0],
        "v2_derived_source_bytes": V2_DERIVED[1],
        "expected_source_apply_count": 2,
        "actual_source_apply_count": report.get("source_apply_count", 0),
        "expected_compiler_process_count": 14,
        "actual_compiler_process_count": report.get("actual_compiler_process_count", 0),
        "historical_v25_repository_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "current_v26_repository_evidence_owner_count": 141,
        "current_v26_authenticated_reference_count": 146,
        "actual_zig_failure_archive_sha256": ZIG_FAILURE_ARCHIVE_SHA256,
        "actual_zig_failure_receipt_sha256": ZIG_FAILURE_RECEIPT_SHA256,
        "historical_c_semantic_mismatch_count": 1262,
        "targeted_legacy_pickle_mismatch_count": 32,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_raw = canonical(receipt)
    require(len(receipt_raw) <= MAX_SOURCE,
            "bound the complete independently owned source-build receipt")
    receipt_owner = kernel.write_fresh(directory / receipt_name,
                                       receipt_raw, synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    return {
        "schema": SCHEMA + "-published-build",
        "version": VERSION, "status": report["status"],
        "family": FAMILY, "label": label,
        "archive_relative": EVIDENCE + "/" + archive_name,
        "archive_sha256": archive["sha256"],
        "receipt_relative": EVIDENCE + "/" + receipt_name,
        "receipt_sha256": receipt_owner["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": report["status"] == "FAIL",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def run_build(options: argparse.Namespace) -> dict[str, Any]:
    global _BUILD_ACTIVE
    require(options.build is True and not _BUILD_ACTIVE,
            "require one explicit non-reentrant C V13 offline source build")
    contract, loaded = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256)
    label = checked_label(options.label)
    expected = {ORIGINAL[0] + "=" + ORIGINAL[1],
                ADAPTER[0] + "=" + ADAPTER[1]}
    require(type(options.owned_source_sha256) is list
            and len(options.owned_source_sha256) == 2
            and set(options.owned_source_sha256) == expected,
            "pin both unchanged original first-party C source owners")
    previous = loaded["v12"]
    inherited = loaded["active"]
    v8, v7, kernel = inherited["v8"], inherited["v7"], inherited["kernel"]
    for failed in (False, True):
        for name in evidence_names(label, failure=failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE / name)
    require(previous._ACTIVE is None and not previous._APPLIED,
            "reject reused inherited overlays or a concurrently active source build")
    _BUILD_ACTIVE = True
    previous._ACTIVE = inherited
    old_snapshot = getattr(kernel, "copy_snapshot", None)
    v8.install_v8_build_kernel(v7, kernel)
    kernel.copy_snapshot = previous.copy_snapshot
    workdir: str | None = None
    steps: list[dict[str, Any]] = []
    phases: list[dict[str, Any]] = []
    error: dict[str, Any] | None = None
    reproduction: dict[str, Any] | None = None
    try:
        workdir = tempfile.mkdtemp(prefix=v8.WORK_PREFIX + FAMILY + "-",
                                  dir="/tmp")
        v8.checked_workdir(workdir, FAMILY)
        v8.prepare_private_phases(kernel, workdir)
        sources = {ORIGINAL[0]: previous.read_owner(*ORIGINAL),
                   ADAPTER[0]: previous.read_owner(*ADAPTER)}
        for phase in PHASES:
            actual = kernel.exact_build_phase(
                workdir, FAMILY, phase, sources, steps)
            actual["native_forensics"] = v8.record_native_forensics(
                v7, kernel, workdir, phase, actual, steps)
            phases.append(actual)
        reproduction = previous.verify_reproducibility(
            v8, v7, workdir, phases, steps)
        require(reproduction.get("actual_compiler_process_count") == 14
                and reproduction.get("source_apply_count") == 2,
                "require fourteen actual genuine compile/inspection observations")
    except BaseException as failure:
        error = {
            "type": type(failure).__qualname__,
            "message": str(failure)[:8192],
            "traceback": traceback.format_exception(
                type(failure), failure, failure.__traceback__),
        }
    finally:
        try:
            read_owner(*ORIGINAL)
            read_owner(*ADAPTER)
        finally:
            previous._ACTIVE = None
            kernel.copy_snapshot = old_snapshot
            _BUILD_ACTIVE = False
    status = "PASS" if error is None else "FAIL"
    report = {
        "schema": SCHEMA + "-actual-native-build",
        "version": VERSION, "status": status,
        "family": FAMILY, "label": label,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "contract_sha256": options.contract_sha256,
        "frozen_context": contract,
        "root_prefix": "rebar-phase2-native-build-v8-c-",
        "historical_v25_repository_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "current_v26_repository_evidence_owner_count": 141,
        "current_v26_authenticated_reference_count": 146,
        "actual_zig_failure_archive_sha256": ZIG_FAILURE_ARCHIVE_SHA256,
        "actual_zig_failure_receipt_sha256": ZIG_FAILURE_RECEIPT_SHA256,
        "historical_c_semantic_mismatch_count": 1262,
        "historical_c_candidate_worker_count": 13,
        "targeted_legacy_pickle_mismatch_count": 32,
        "original_source_sha256": ORIGINAL[1],
        "v1_derived_source_sha256": V1_DERIVED[0],
        "v2_derived_source_sha256": V2_DERIVED[0],
        "v2_derived_source_bytes": V2_DERIVED[1],
        "source_apply_count": 0 if workdir is None else sum(
            (workdir, phase) in previous._APPLIED for phase in PHASES),
        "expected_compiler_process_count": 14,
        "actual_compiler_process_count": len(steps),
        "phase_count": len(phases),
        "phases": phases,
        "compiler_processes": steps,
        "reproducibility": reproduction,
        "actual_failure": error,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return publish_report(kernel, report, label)


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    if arguments is None:
        arguments = sys.argv[1:]
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require one exact independently authorized C V13 command")
    flags = [item for item in arguments if item.startswith("--")]
    require(all(flag == "--owned-source-sha256" or flags.count(flag) == 1
                for flag in flags),
            "reject duplicate, hidden, or ambiguous C V13 authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    options = parser.parse_args(arguments)
    checked_digest(options.source_sha256, "C V13 source")
    checked_digest(options.protocol_sha256, "C V13 protocol")
    if options.contract_sha256 is not None:
        checked_digest(options.contract_sha256, "C V13 contract")
    if options.self_test or options.render_contract:
        require(options.contract_sha256 is None and options.family is None
                and options.label is None and not options.owned_source_sha256,
                "source-only rendering never authorizes an actual source build")
    elif options.verify_frozen_context:
        require(options.contract_sha256 is not None and options.family is None
                and options.label is None and not options.owned_source_sha256,
                "read-only context never authorizes a build or native target")
    else:
        require(options.contract_sha256 is not None
                and options.family == FAMILY and options.label is not None,
                "explicitly authorize one bounded original C source build")
        checked_label(options.label)
        expected = {ORIGINAL[0] + "=" + ORIGINAL[1],
                    ADAPTER[0] + "=" + ADAPTER[1]}
        require(type(options.owned_source_sha256) is list
                and len(options.owned_source_sha256) == 2
                and set(options.owned_source_sha256) == expected,
                "pin the exact independently authored C source and adapter")
    return options


def main(arguments: list[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = self_test()
        elif options.build:
            result = run_build(options)
        else:
            frozen, active = verify_context(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256)
            if options.render_contract:
                result = frozen
            else:
                result = {
                    "schema": SCHEMA + "-read-only-frozen-context",
                    "status": "PASS", "version": VERSION,
                    "family": FAMILY,
                    "source_sha256": options.source_sha256,
                    "protocol_sha256": options.protocol_sha256,
                    "contract_sha256": options.contract_sha256,
                    "published_graph_version": 26,
                    "published_graph_owner_count": 4,
                    "historical_v25_repository_evidence_owner_count": 139,
                    "historical_v25_authenticated_reference_count": 144,
                    "repository_evidence_owner_count": 141,
                    "authenticated_digest_addressed_history_paths": 146,
                    "actual_zig_failure_archive_sha256": ZIG_FAILURE_ARCHIVE_SHA256,
                    "actual_zig_failure_receipt_sha256": ZIG_FAILURE_RECEIPT_SHA256,
                    "actual_zig_failure_status": "FAIL",
                    "historical_c_semantic_mismatch_count": 1262,
                    "historical_c_candidate_worker_count": 13,
                    "actual_legacy_pickle_mismatch_count": 32,
                    "actual_original_pickle_record_count": 96,
                    "actual_original_modern_pickle_record_count": 64,
                    "actual_rust_build_process_count": 28,
                    "actual_zig_build_process_count": 26,
                    "v1_derived_source_sha256": V1_DERIVED[0],
                    "v1_derived_source_bytes": V1_DERIVED[1],
                    "v2_derived_source_sha256": V2_DERIVED[0],
                    "v2_derived_source_bytes": V2_DERIVED[1],
                    "future_phase_count": 2,
                    "future_process_count_per_phase": 7,
                    "future_total_compiler_process_count": 14,
                    "future_total_source_apply_count": 2,
                    "frozen_suite_count": 13,
                    "frozen_case_execution_denominator": 31237,
                    "frozen_private_waiver_count": 13,
                    "candidate_correctness": "NOT MEASURED",
                    "candidate_imports": 0,
                    "candidate_processes_started": 0,
                    "compiler_processes_started": 0,
                    "native_libraries_loaded": 0,
                    "source_apply_count": 0,
                    "workspace_mutations": 0,
                    "network_requests": 0,
                    "hidden_cases_read": 0,
                    "clock_samples": 0,
                    "timing_trials_run": 0,
                    "performance": "NOT MEASURED",
                    "memory": "NOT MEASURED",
                    "holdout": "NOT OPENED",
                    "winner_selected": False,
                }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if options.render_contract or result.get("status") == "PASS" else 1
    except BaseException as error:
        result = {
            "schema": SCHEMA + "-entry-failure", "version": VERSION,
            "status": "FAIL", "error_type": type(error).__qualname__,
            "error_message": str(error),
            "candidate_correctness": "NOT MEASURED",
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "source_apply_count": 0,
            "workspace_mutations": 0,
            "network_requests": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        try:
            sys.stdout.buffer.write(canonical(result))
            sys.stdout.buffer.flush()
        except (OSError, ValueError, TypeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
