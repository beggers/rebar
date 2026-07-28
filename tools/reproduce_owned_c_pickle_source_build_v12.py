#!/usr/bin/env python3
"""Freeze an offline, two-phase, first-party C buffer-and-pickle source build."""

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
import types
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/reproduce_owned_c_pickle_source_build_v12.py"
PROTOCOL = "oracle/phase2/C-PICKLE-SOURCE-BUILD-V12.md"
CONTRACT = "oracle/phase2/c-pickle-source-build-v12.json"
EVIDENCE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-c-pickle-source-build-v12"
VERSION = 12
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
V8 = {
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
V2 = {
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
GRAPH = {
    "source": (
        "tools/render_candidate_current_overview_v25.py",
        "9b1eabba4a3bd991c4359af4ab1482fe6f1ce848bb9e5df6fdd9e8bdafb21204",
        98948,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v25.inputs.json",
        "123210219fac109506c03c2f76f89fda33aa5e08b0628fef43b9236d05bc1abe",
        37281,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v25.json",
        "8e4101c896e316190928d0710ca4442488c925ee5ef421507ba4dd08ff10a6d9",
        144980,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v25.svg",
        "db2f1a11e49fd58701ad89111aa422e619431eb9834d3fb5ae66deffcd75f0bb",
        13188,
    ),
}
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
_ACTIVE: dict[str, Any] | None = None
_APPLIED: set[tuple[str, str]] = set()


class BuildError(Exception):
    """An actual first-party source-build owner or effect boundary changed."""


def require(value: Any, message: str) -> None:
    if value is not True:
        raise BuildError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete first-party source bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise BuildError("reject noncanonical C V12 evidence") from error


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require an exact separately pinned SHA-256: " + label)
    return value


def relative_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require a bounded canonical relative source owner")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value
            and 0 < len(path.parts) <= 16
            and all(piece not in ("", ".", "..") for piece in path.parts),
            "reject linked, escaped, or noncanonical source owners")
    return path.parts


def read_owner(path: str, fingerprint: str, size: int | None = None) -> bytes:
    parts = relative_parts(path)
    checked_digest(fingerprint, path)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    parent = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for piece in parts[:-1]:
            child = os.open(piece, flags | os.O_DIRECTORY, dir_fd=parent)
            os.close(parent)
            parent = child
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and 0 <= before.st_size <= MAX_ARCHIVE,
                    "authenticate only bounded original regular source owners")
            if size is not None:
                require(before.st_size == size,
                        "reject a truncated or substituted exact owner")
            blocks: list[bytes] = []
            left = before.st_size
            while left:
                block = os.read(descriptor, min(left, 1024 * 1024))
                require(bool(block), "reject an incompletely read source owner")
                blocks.append(block)
                left -= len(block)
            require(os.read(descriptor, 1) == b"",
                    "reject hidden owner bytes")
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns),
                    "reject a source owner changed during authentication")
            raw = b"".join(blocks)
            require(len(raw) == before.st_size and digest(raw) == fingerprint,
                    "independently authenticate exact owner: " + path)
            return raw
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)


def document(raw: bytes, label: str) -> dict[str, Any]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "reject a repeated JSON key: " + label)
            result[key] = value
        return result

    try:
        result = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda item: (_ for _ in ()).throw(
                BuildError("reject nonfinite JSON: " + item)),
        )
    except (json.JSONDecodeError, UnicodeError, RecursionError) as error:
        raise BuildError("reject incomplete source evidence: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "require exact canonical source evidence: " + label)
    return result


def pin(owner: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def load_module(owner: tuple[str, str, int], name: str) -> types.ModuleType:
    raw = read_owner(*owner)
    require(name not in sys.modules, "reject a reused frozen build module")
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / owner[0])
    module.__package__ = None
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    return module


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = 0

    def install(self, owner: Any, name: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked += 1
            raise BuildError("source-only operation rejected: " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)), (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "unlink", "remove", "replace", "rename",
                  "system", "fork", "posix_spawn")),
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

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL
            and all(character.isascii()
                    and (character.isalnum() or character in "-_")
                    for character in value),
            "require a bounded, exact, fresh C V12 evidence label")
    return value


def evidence_names(label: str, *, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool,
            "choose only an actual complete build or a genuine build failure")
    base = "native-source-build-v12-c-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def synthetic_schedule(phases: Any, processes: Any) -> dict[str, Any]:
    require(type(phases) is list and len(phases) == 2
            and type(processes) is list and len(processes) == 14,
            "require exactly two phases and fourteen actual scheduled processes")
    ids: set[int] = set()
    for index, phase in enumerate(phases):
        require(type(phase) is dict and phase.get("name") == PHASES[index]
                and phase.get("source_sha256") == V2_DERIVED[0]
                and phase.get("source_bytes") == V2_DERIVED[1]
                and phase.get("adapter_sha256") == ADAPTER[1]
                and phase.get("overlay_count") == 1,
                "reject a missing, reused, foreign, or wrongly repaired phase")
    for index, process in enumerate(processes):
        require(type(process) is dict
                and process.get("phase") == PHASES[index // len(PROCESS_NAMES)]
                and process.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and type(process.get("pid")) is int
                and process["pid"] > 0 and process["pid"] not in ids
                and process.get("exit_status") == 0,
                "reject fake, duplicated, omitted, or reordered C build processes")
        ids.add(process["pid"])
    return {"phase_count": 2, "unique_process_count": len(ids),
            "source_apply_count": 2}


def self_test() -> dict[str, Any]:
    accepted = 0
    rejected = 0
    phases = [
        {"name": phase, "source_sha256": V2_DERIVED[0],
         "source_bytes": V2_DERIVED[1], "adapter_sha256": ADAPTER[1],
         "overlay_count": 1}
        for phase in PHASES
    ]
    processes = [
        {"phase": PHASES[index // len(PROCESS_NAMES)],
         "name": PROCESS_NAMES[index % len(PROCESS_NAMES)],
         "pid": index + 1, "exit_status": 0}
        for index in range(14)
    ]
    with SourceOnlyWall() as wall:
        result = synthetic_schedule(phases, processes)
        require(result == {"phase_count": 2, "unique_process_count": 14,
                           "source_apply_count": 2},
                "require one complete synthetic two-phase schedule")
        accepted += 1
        for suffix in (False, True):
            archive, receipt = evidence_names("synthetic", failure=suffix)
            require(archive.startswith("native-source-build-v12-c-")
                    and archive.endswith(".json.gz")
                    and receipt.endswith("-publication-receipt.json"),
                    "keep exact distinct future V12 publication owners")
            accepted += 1

        def reject(call: Any, label: str) -> None:
            nonlocal rejected
            try:
                call()
            except (BuildError, OSError, TypeError, ValueError):
                rejected += 1
            else:
                raise BuildError("accepted a hostile C V12 control: " + label)

        for index in range(2):
            for key, replacement in (
                ("name", "foreign-phase"),
                ("source_sha256", "0" * 64),
                ("source_bytes", V1_DERIVED[1]),
                ("adapter_sha256", "0" * 64),
                ("overlay_count", 0),
                ("overlay_count", 2),
            ):
                hostile = copy.deepcopy(phases)
                hostile[index][key] = replacement
                reject(lambda value=hostile: synthetic_schedule(value, processes),
                       "altered exact phase owner")
        for index in range(14):
            for key, replacement in (
                ("phase", "foreign"), ("name", "build_external_engine"),
                ("pid", 0), ("exit_status", 1),
            ):
                hostile = copy.deepcopy(processes)
                hostile[index][key] = replacement
                reject(lambda value=hostile: synthetic_schedule(phases, value),
                       "fake or reordered process")
        reject(lambda: synthetic_schedule(phases[:1], processes), "partial phase")
        reject(lambda: synthetic_schedule(phases, processes[:-1]),
               "partial process schedule")
        copied = copy.deepcopy(processes)
        copied[1]["pid"] = copied[0]["pid"]
        reject(lambda: synthetic_schedule(phases, copied), "reused process")
        for value in ("", "../escape", "/tmp/escape", "a/../b", "a//b",
                      "./owner", "x" * 513):
            reject(lambda item=value: relative_parts(item), "unsafe relative owner")
        for value in ("", "0" * 63, "0" * 65, "X" * 64):
            reject(lambda item=value: checked_digest(item, "hostile"),
                   "wrong exact owner pin")
        for value in ("", "../../escape", "bad label", "x" * (MAX_LABEL + 1)):
            reject(lambda item=value: checked_label(item), "unsafe evidence label")
        effects = (
            (lambda: builtins.open("/tmp/forbidden"), "builtin file"),
            (lambda: io.open("/tmp/forbidden"), "io file"),
            (lambda: os.open("/tmp/forbidden", os.O_RDONLY), "private root"),
            (lambda: os.read(0, 1), "source read"),
            (lambda: os.write(1, b"x"), "source application"),
            (lambda: os.stat("/tmp"), "private root inspection"),
            (lambda: os.lstat("/tmp"), "private root lstat"),
            (lambda: os.mkdir("/tmp/forbidden"), "phase creation"),
            (lambda: os.unlink("/tmp/forbidden"), "destructive unlink"),
            (lambda: os.replace("/tmp/a", "/tmp/b"), "native replacement"),
            (lambda: Path("/tmp/x").read_bytes(), "Path read"),
            (lambda: Path("/tmp/x").write_bytes(b"x"), "Path write"),
            (lambda: Path("/tmp").resolve(), "private-root resolution"),
            (lambda: subprocess.run(("true",)), "compiler process"),
            (lambda: subprocess.Popen(("true",)), "candidate process"),
            (lambda: socket.socket(), "external network"),
            (lambda: tempfile.mkdtemp(), "build root"),
            (lambda: tempfile.mkstemp(), "temporary compiler input"),
            (lambda: importlib.import_module("candidates.vm_candidate"),
             "candidate import"),
            (lambda: importlib.import_module("re"), "stdlib regex import"),
            (lambda: threading.Thread().start(), "background thread"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.perf_counter(), "benchmark clock"),
            (lambda: time.perf_counter_ns(), "benchmark nanoclock"),
            (lambda: time.sleep(0), "hidden wait"),
        )
        for probe, label in effects:
            reject(probe, label)
        require(wall.blocked == len(effects),
                "independently count every blocked source-only operation")
    return {
        "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
        "version": VERSION, "family": FAMILY,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_controls": len(effects),
        "future_phase_count": 2,
        "future_process_count_per_phase": len(PROCESS_NAMES),
        "future_total_compiler_process_count": 14,
        "future_source_apply_count": 2,
        "repository_evidence_owner_count": 139,
        "authenticated_digest_addressed_history_paths": 144,
        "historical_c_semantic_mismatch_count": 1262,
        "historical_legacy_pickle_mismatch_count": 32,
        "frozen_suite_count": 13,
        "frozen_case_execution_denominator": 31237,
        "frozen_private_waiver_count": 13,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0, "candidate_processes_started": 0,
        "compiler_processes_started": 0, "native_libraries_loaded": 0,
        "source_apply_count": 0, "workspace_mutations": 0,
        "network_requests": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PYTHON,
            "require exact isolated, bytecode-free CPython 3.14.6")


def expected_contract(source_pin: str, protocol_pin: str,
                      repair_contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "family": FAMILY, "phase": "SOURCE FREEZE; NO ACTUAL BUILD",
        "source": {"path": SELF,
                   "sha256": checked_digest(source_pin, "C V12 source")},
        "protocol": {"path": PROTOCOL,
                     "sha256": checked_digest(protocol_pin, "C V12 protocol")},
        "runtime": {"implementation": "CPython", "version": "3.14.6",
                    "path": PYTHON, "sha256": PYTHON_SHA256},
        "oracle": {"manifest": pin(P0), "suite_count": 13,
                   "suite_ids": [name for name, _, _ in SUITES],
                   "case_execution_denominator": 31237,
                   "private_waiver_count": 13},
        "published_v25": {
            "graph": {role: pin(owner) for role, owner in GRAPH.items()},
            "graph_owner_count": 4,
            "repository_evidence_owner_count": 139,
            "authenticated_digest_addressed_history_paths": 144,
            "actual_c_campaign_evidence_owner_count": 30,
            "actual_c_completed_suite_count": 13,
            "actual_c_candidate_workers": 13,
            "actual_c_fully_passing_suite_count": 8,
            "actual_c_verified_passing_case_count": 7325,
            "actual_c_semantic_mismatch_count": 1262,
            "actual_c_infrastructure_failure_count": 0,
            "actual_rust_build_process_count": 28,
            "actual_rust_matching_test_status": "NOT MEASURED",
            "actual_zig_build_process_count": 26,
            "actual_zig_matching_test_status": "NOT MEASURED",
            "qualified_candidate_count": 0,
        },
        "inherited_v8_builder": {
            "owners": {role: pin(owner) for role, owner in V8.items()},
            "root_prefix": "rebar-phase2-native-build-v8-c-",
            "original_first_party_source": pin(ORIGINAL),
            "unchanged_first_party_adapter": pin(ADAPTER),
            "v1_buffer_repaired_source": {"sha256": V1_DERIVED[0],
                                          "bytes": V1_DERIVED[1]},
            "compiler": "/usr/bin/x86_64-linux-gnu-gcc-13",
            "elf_inspector": "/usr/bin/x86_64-linux-gnu-readelf",
            "python_include":
                "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14",
            "compiler_flags": ["-std=c11", "-O3", "-Wall", "-Wextra",
                               "-Werror", "-fPIC", "-shared",
                               "-Wl,--build-id=sha1"],
            "prefix_map_target": "/rebar-phase2-v6-owned-source",
            "extension_name": "_vm_native.cpython-314-x86_64-linux-gnu.so",
            "process_names_per_phase": list(PROCESS_NAMES),
            "process_count_per_phase": 7,
            "future_total_compiler_process_count": 14,
            "complete_native_elf_forensics": True,
        },
        "frozen_pickle_repair": {
            "owners": {role: pin(owner) for role, owner in V2.items()},
            "contract_sha256": V2["contract"][1],
            "derived_source": {"sha256": V2_DERIVED[0],
                               "bytes": V2_DERIVED[1],
                               "materialized_during_source_freeze": False},
            "v1_buffer_repair_preserved": True,
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
            "actual_repair_contract_sha256": digest(canonical(repair_contract)),
        },
        "future_build_policy": {
            "explicit_build_required": True,
            "family": FAMILY,
            "root_parent": "/tmp",
            "root_prefix": "rebar-phase2-native-build-v8-c-",
            "phase_names": list(PHASES),
            "phase_count": 2,
            "both_peer_phases_precreated_before_first_apply": True,
            "source_owners_per_phase": 2,
            "original_source_sha256": ORIGINAL[1],
            "adapter_source_sha256": ADAPTER[1],
            "private_compiler_input_sha256": V2_DERIVED[0],
            "private_compiler_input_bytes": V2_DERIVED[1],
            "v2_source_apply_count_per_phase": 1,
            "future_total_source_apply_count": 2,
            "process_names_per_phase": list(PROCESS_NAMES),
            "process_count_per_phase": 7,
            "future_total_compiler_process_count": 14,
            "directory_mode": "0700",
            "source_file_mode": "0600",
            "source_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "raw_elf_forensics": "COMPLETE AUTHENTICATED PHASE BYTES",
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
            "archive_prefix": "native-source-build-v12-c-",
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
            "candidate_imports": 0, "candidate_processes_started": 0,
            "compiler_processes_started": 0, "native_libraries_loaded": 0,
            "source_apply_count": 0, "workspace_mutations": 0,
            "network_requests": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "holdout": "NOT OPENED", "holdout_opened": False,
            "qualified_candidate_count": 0, "winner_selected": False,
        },
    }


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None
                   ) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    before = frozenset(item for item in sys.modules
                       if item == "candidates" or item.startswith("candidates."))
    require(not before, "never import a candidate during a C V12 source freeze")
    read_owner(SELF, checked_digest(source_pin, "C V12 source"))
    read_owner(PROTOCOL, checked_digest(protocol_pin, "C V12 protocol"))
    v8 = load_module(V8["source"], "_rebar_exact_owned_c_pickle_v12_v8")
    require(v8.SCHEMA == "rebar-phase2-owned-native-source-build-v8"
            and v8.FAMILY == FAMILY and tuple(v8.PHASES) == PHASES
            and tuple(v8.PROCESS_NAMES) == PROCESS_NAMES
            and v8.WORK_PREFIX == "rebar-phase2-native-build-v8-"
            and v8.PINNED_GCC == "/usr/bin/x86_64-linux-gnu-gcc-13"
            and v8.PINNED_READELF == "/usr/bin/x86_64-linux-gnu-readelf"
            and v8.PINNED_PYTHON == PYTHON
            and v8.PINNED_PYTHON_SHA256 == PYTHON_SHA256
            and v8.ORIGINAL_PATH == ORIGINAL[0]
            and v8.ORIGINAL_SHA256 == ORIGINAL[1]
            and v8.ORIGINAL_BYTES == ORIGINAL[2]
            and v8.ADAPTER_PATH == ADAPTER[0]
            and v8.ADAPTER_SHA256 == ADAPTER[1]
            and v8.ADAPTER_BYTES == ADAPTER[2]
            and v8.DERIVED_SHA256 == V1_DERIVED[0]
            and v8.DERIVED_BYTES == V1_DERIVED[1]
            and tuple(v8.SUITE_IDS) == tuple(item[0] for item in SUITES),
            "freeze the exact first-party V8 compiler and original C source closure")
    previous = v8.verify_context({
        "mode": "verify-context",
        "source_sha256": V8["source"][1],
        "protocol_sha256": V8["protocol"][1],
        "contract_sha256": V8["contract"][1],
    })
    require(type(previous) is dict and previous.get("status") == "PASS"
            and previous.get("family") == FAMILY
            and previous.get("source_family_count") == 6
            and previous.get("original_source_owner_count") == 25
            and previous.get("derived_source_sha256") == V1_DERIVED[0]
            and previous.get("derived_source_bytes") == V1_DERIVED[1]
            and previous.get("future_compiler_process_count") == 14
            and previous.get("candidate_imports") == 0
            and previous.get("compiler_processes_started") == 0
            and previous.get("source_apply_count") == 0
            and previous.get("clock_samples") == 0
            and previous.get("holdout") == "NOT OPENED",
            "independently reproduce the immutable no-build V8 compiler context")
    repair = load_module(V2["source"], "_rebar_exact_owned_c_pickle_v12_repair")
    require(repair.SCHEMA == "rebar-phase2-owned-first-party-source-repair-v2"
            and repair.SELF == V2["source"][0]
            and repair.PROTOCOL == V2["protocol"][0]
            and repair.CONTRACT == V2["contract"][0]
            and repair.PYTHON == PYTHON
            and repair.PYTHON_SHA256 == PYTHON_SHA256
            and tuple(repair.SUITES) == SUITES
            and tuple(repair.ORIGINAL_SOURCE) == ORIGINAL
            and tuple(repair.ADAPTER) == ADAPTER
            and repair.V1_DERIVED_SHA256 == V1_DERIVED[0]
            and repair.V1_DERIVED_BYTES == V1_DERIVED[1]
            and repair.GRAPH == GRAPH,
            "preserve the complete independently frozen V2 pickle repair")
    repair_contract, derived = repair.verify_context(
        V2["source"][1], V2["protocol"][1], V2["contract"][1],
    )
    require(type(repair_contract) is dict
            and repair_contract.get("schema") == repair.SCHEMA
            and repair_contract.get("version") == 2
            and digest(canonical(repair_contract)) == V2["contract"][1]
            and type(derived) is bytes and digest(derived) == V2_DERIVED[0]
            and len(derived) == V2_DERIVED[1],
            "reproduce complete deterministic V1-plus-V2 compiler input")
    history = repair_contract.get("current_history")
    evidence = repair_contract.get("actual_public_type_evidence")
    boundary = repair_contract.get("phase_boundary")
    require(type(history) is dict
            and history.get("published_graph_version") == 25
            and history.get("repository_evidence_owner_count") == 139
            and history.get("authenticated_digest_addressed_history_paths") == 144
            and history.get("actual_c_campaign_evidence_owner_count") == 30
            and history.get("actual_c_campaign_status") == "FAIL"
            and history.get("actual_c_candidate_worker_count") == 13
            and history.get("actual_c_completed_suite_count") == 13
            and history.get("actual_c_fully_passing_suite_count") == 8
            and history.get("actual_c_verified_passing_case_count") == 7325
            and history.get("actual_c_semantic_mismatch_count") == 1262
            and history.get("actual_c_infrastructure_failure_count") == 0
            and history.get("actual_c_original_native_restored") is True
            and history.get("actual_rust_build_process_count") == 28
            and history.get("actual_rust_matching") == "NOT MEASURED"
            and history.get("actual_zig_build_process_count") == 26
            and history.get("actual_zig_matching") == "NOT MEASURED"
            and history.get("qualified_candidate_count") == 0,
            "preserve exact V25, complete actual C losses, and real Rust/Zig builds")
    require(type(evidence) is dict
            and evidence.get("suite") == "public_types_v1"
            and evidence.get("status") == "FAIL"
            and evidence.get("case_execution_denominator") == 6912
            and evidence.get("complete_record_count") == 6912
            and evidence.get("observed_mismatch_count") == 248
            and evidence.get("pickle_record_count") == 96
            and evidence.get("legacy_pickle_mismatch_count") == 32
            and evidence.get("legacy_pickle_protocol_counts") == {"0": 16, "1": 16}
            and evidence.get("preserved_modern_pickle_protocol_counts")
            == {"2": 16, "3": 16, "4": 16, "5": 16}
            and evidence.get("archive") == pin(PUBLIC_ARCHIVE)
            and evidence.get("receipt") == pin(PUBLIC_RECEIPT),
            "build only the observed, complete, signed original pickle defect")
    require(type(boundary) is dict
            and boundary.get("candidate_correctness") == "NOT MEASURED"
            and boundary.get("candidate_imports") == 0
            and boundary.get("candidate_processes_started") == 0
            and boundary.get("compiler_processes_started") == 0
            and boundary.get("native_libraries_loaded") == 0
            and boundary.get("source_apply_count") == 0
            and boundary.get("clock_samples") == 0
            and boundary.get("timing_trials_run") == 0
            and boundary.get("holdout") == "NOT OPENED"
            and boundary.get("holdout_opened") is False
            and boundary.get("winner_selected") is False,
            "never turn a source freeze into a build, benchmark, or candidate")
    for role, owner in GRAPH.items():
        require(history.get("graph", {}).get(role) == pin(owner),
                "bind all four independent published V25 graph owners")
        read_owner(*owner)
    for owner in (P0, ORIGINAL, ADAPTER, PUBLIC_ARCHIVE, PUBLIC_RECEIPT):
        read_owner(*owner)
    v7 = v8.load_frozen_module(
        "_rebar_exact_owned_c_pickle_v12_v7", v8.V7_OWNERS["source"],
    )
    require(v7.SCHEMA == "rebar-phase2-owned-native-source-build-v7"
            and v7.SOURCE_OWNERS[FAMILY][ORIGINAL[0]]
            == (ORIGINAL[1], ORIGINAL[2])
            and v7.SOURCE_OWNERS[FAMILY][ADAPTER[0]]
            == (ADAPTER[1], ADAPTER[2]),
            "bind exact C source snapshots to the authentic native build kernel")
    kernel = v7.load_frozen_v4()
    kernel.audit_native_source(derived, family=FAMILY, location=ORIGINAL[0])
    auditor = v7.load_frozen_independence_v2()
    audit = auditor.inspect_native(
        derived.decode("utf-8", "strict"),
        auditor.FAMILY_BY_NAME["c_vm"], ORIGINAL[0], FAMILY,
    )
    require(type(audit) is dict,
            "statically audit the complete owned C V12 engine for delegation")
    result = expected_contract(source_pin, protocol_pin, repair_contract)
    if contract_pin is not None:
        raw = read_owner(CONTRACT, checked_digest(contract_pin, "C V12 contract"))
        require(raw == canonical(result)
                and document(raw, "exact C V12 machine contract") == result,
                "independently reproduce the exact C V12 source-build contract")
    after = frozenset(item for item in sys.modules
                      if item == "candidates" or item.startswith("candidates."))
    require(before == after and not after,
            "never import, build, or activate a regex candidate in verification")
    read_owner(*ORIGINAL)
    read_owner(*ADAPTER)
    return result, {"v8": v8, "v7": v7, "kernel": kernel,
                    "repair": repair, "derived": derived,
                    "v8_context": previous, "repair_contract": repair_contract,
                    "static_audit": audit}


def active_parts() -> dict[str, Any]:
    require(type(_ACTIVE) is dict,
            "require an explicit independently pinned V12 build authorization")
    assert _ACTIVE is not None
    return _ACTIVE


def copy_snapshot(workdir: str, family: str, phase: str,
                  sources: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    active = active_parts()
    v8, repair = active["v8"], active["repair"]
    kernel, derived = active["kernel"], active["derived"]
    paths = v8.phase_paths(workdir, family, phase)
    require(family == FAMILY and phase in PHASES
            and type(sources) is dict and set(sources) == {ORIGINAL[0], ADAPTER[0]}
            and digest(sources[ORIGINAL[0]]) == ORIGINAL[1]
            and len(sources[ORIGINAL[0]]) == ORIGINAL[2]
            and digest(sources[ADAPTER[0]]) == ADAPTER[1]
            and len(sources[ADAPTER[0]]) == ADAPTER[2]
            and type(derived) is bytes and digest(derived) == V2_DERIVED[0]
            and len(derived) == V2_DERIVED[1]
            and (workdir, phase) not in _APPLIED,
            "reject repeated, omitted, foreign, or unrepaired C source snapshots")
    identities: set[tuple[int, int]] = set()
    for peer in PHASES:
        peer_paths = v8.phase_paths(workdir, family, peer)
        for directory in (peer_paths["base"], peer_paths["source"],
                          peer_paths["source"] / "candidates"):
            owner = os.lstat(directory)
            require(stat.S_ISDIR(owner.st_mode)
                    and stat.S_IMODE(owner.st_mode) == 0o700
                    and owner.st_uid == os.geteuid(),
                    "precreate both exact owner-only C build phases before applying")
        info = os.lstat(peer_paths["base"])
        identity = (info.st_dev, info.st_ino)
        require(identity not in identities,
                "require independently owned private source-build phases")
        identities.add(identity)
    adapter = kernel.write_fresh(paths["source"] / ADAPTER[0],
                                 sources[ADAPTER[0]], synchronize=False)
    adapter["path"] = v8.sanitized(adapter["path"], workdir, family)
    applied = repair.apply_private(str(paths["source"]), derived)
    require(type(applied) is dict
            and applied.get("schema")
            == "rebar-phase2-owned-first-party-source-repair-v2-private-snapshot-application"
            and applied.get("status") == "PASS"
            and applied.get("version") == 2 and applied.get("family") == FAMILY
            and applied.get("phase") == phase
            and applied.get("source_apply_count") == 1
            and applied.get("derived_source_sha256") == V2_DERIVED[0]
            and applied.get("derived_source_bytes") == V2_DERIVED[1]
            and applied.get("original_candidate_modified") is False
            and applied.get("original_adapter_modified") is False
            and applied.get("candidate_correctness") == "NOT MEASURED"
            and applied.get("actual_candidate_workers") == 0,
            "apply exactly one genuine V1-plus-V2 private repair per phase")
    observed, raw = kernel.authenticate_file(
        paths["source"] / ORIGINAL[0], expected=V2_DERIVED[0],
        maximum=MAX_SOURCE, exact_size=V2_DERIVED[1], capture=True,
    )
    require(type(raw) is bytes and raw == derived
            and stat.S_IMODE(os.lstat(paths["source"] / ORIGINAL[0]).st_mode)
            == 0o600,
            "bind the actual compiler to the exact exclusive repaired source")
    original = {
        "path": v8.sanitized(observed["path"], workdir, family),
        "sha256": observed["sha256"], "bytes": observed["size_bytes"],
        "device": observed["device"], "inode": observed["inode"],
        "exclusive_creation": True,
        "same_inode_readback_verified": True,
        "file_fsync_completed": True,
        "source_overlay": applied,
    }
    _APPLIED.add((workdir, phase))
    read_owner(*ORIGINAL)
    read_owner(*ADAPTER)
    return {ORIGINAL[0]: original, ADAPTER[0]: adapter}


def verify_reproducibility(v8: types.ModuleType, v7: types.ModuleType,
                           workdir: str, phases: list[dict[str, Any]],
                           steps: list[dict[str, Any]]) -> dict[str, Any]:
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases] == list(PHASES)
            and type(steps) is list and len(steps) == 14,
            "require two genuine V2 source phases and fourteen native processes")
    source_owners: set[tuple[int, int]] = set()
    outputs: list[dict[str, Any]] = []
    for index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        require(type(owners) is dict and set(owners) == {ORIGINAL[0], ADAPTER[0]},
                "require the complete independently owned C source closure")
        for relative, fingerprint, count in (
            (ORIGINAL[0], V2_DERIVED[0], V2_DERIVED[1]),
            (ADAPTER[0], ADAPTER[1], ADAPTER[2]),
        ):
            owner = owners.get(relative)
            require(type(owner) is dict and owner.get("sha256") == fingerprint
                    and owner.get("bytes") == count
                    and type(owner.get("device")) is int
                    and type(owner.get("inode")) is int
                    and (owner["device"], owner["inode"]) not in source_owners,
                    "require four distinct genuine owner-only source snapshots")
            source_owners.add((owner["device"], owner["inode"]))
        overlay = owners[ORIGINAL[0]].get("source_overlay")
        require(type(overlay) is dict and overlay.get("status") == "PASS"
                and overlay.get("phase") == PHASES[index]
                and overlay.get("source_apply_count") == 1
                and overlay.get("derived_source_sha256") == V2_DERIVED[0]
                and overlay.get("derived_source_bytes") == V2_DERIVED[1],
                "require exactly one authentic V2 source application per phase")
        output = phase.get("native_outputs", {}).get("extension")
        require(type(output) is dict
                and output.get("file_name") == v8.EXTENSION_NAME,
                "require both actual first-party native C extension outputs")
        outputs.append(output)
    pids: set[int] = set()
    for index, step in enumerate(steps):
        require(type(step) is dict
                and step.get("name") == PROCESS_NAMES[index % 7]
                and type(step.get("pid")) is int
                and step["pid"] > 0 and step["pid"] not in pids
                and step.get("exit_status") == 0,
                "reject fake, duplicate, foreign, failed, or unordered processes")
        pids.add(step["pid"])
    first, second = outputs
    require(first.get("sha256") == second.get("sha256")
            and first.get("size_bytes") == second.get("size_bytes")
            and first.get("path") != second.get("path")
            and (first.get("device"), first.get("inode"))
            != (second.get("device"), second.get("inode"))
            and first.get("audit") == second.get("audit"),
            "require byte-identical independently owned native C builds")
    left = v8._RAW_PHASE_ELF.get((workdir, PHASES[0]))
    right = v8._RAW_PHASE_ELF.get((workdir, PHASES[1]))
    require(type(left) is bytes and type(right) is bytes
            and digest(left) == first.get("sha256")
            and digest(right) == second.get("sha256") and left == right,
            "compare only independently authenticated complete genuine ELF bytes")
    comparison = v7.compare_owned_elf64(left, right)
    require(type(comparison) is dict
            and comparison.get("byte_identical") is True,
            "independently compare all native ELF provenance")
    read_owner(*ORIGINAL)
    read_owner(*ADAPTER)
    return {
        "status": "PASS", "phase_count": 2,
        "source_owner_count_per_phase": 2,
        "independent_source_owner_count": len(source_owners),
        "source_apply_count": 2,
        "derived_source_sha256": V2_DERIVED[0],
        "derived_source_bytes": V2_DERIVED[1],
        "original_source_modified": False,
        "original_adapter_modified": False,
        "actual_compiler_process_count": len(pids),
        "byte_identical": True,
        "raw_elf_comparison": comparison,
        "native_outputs": {
            "extension": {
                "file_name": v8.EXTENSION_NAME,
                "sha256": first["sha256"],
                "size_bytes": first["size_bytes"],
                "independent_phase_owner_count": 2,
                "audit": first["audit"],
            }
        },
        "prebuilt_artifact_count": 0,
        "native_libraries_loaded": 0,
    }


def publish_report(kernel: types.ModuleType, report: dict[str, Any],
                   label: str) -> dict[str, Any]:
    require(type(report) is dict and report.get("status") in ("PASS", "FAIL")
            and report.get("family") == FAMILY
            and report.get("label") == checked_label(label),
            "publish only an honest, actual C V12 build result")
    archive_name, receipt_name = evidence_names(
        label, failure=report["status"] == "FAIL",
    )
    directory = ROOT / EVIDENCE
    kernel.mkdir_private(directory)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT,
            "retain the complete bounded C V12 process and ELF report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_ARCHIVE,
            "bound the exclusive deterministic actual C build archive")
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
        "historical_evidence_owner_count": 139,
        "historical_authenticated_reference_count": 144,
        "historical_c_semantic_mismatch_count": 1262,
        "historical_c_candidate_worker_count": 13,
        "targeted_legacy_pickle_mismatch_count": 32,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0, "candidate_processes_started": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    encoded = canonical(receipt)
    require(len(encoded) <= MAX_SOURCE,
            "bound the complete actual durable C V12 publication receipt")
    recorded = kernel.write_fresh(directory / receipt_name, encoded,
                                  synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    return {
        "schema": SCHEMA + "-published-build", "version": VERSION,
        "status": report["status"], "family": FAMILY, "label": label,
        "archive_relative": EVIDENCE + "/" + archive_name,
        "archive_sha256": archive["sha256"],
        "receipt_relative": EVIDENCE + "/" + receipt_name,
        "receipt_sha256": recorded["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": report["status"] == "FAIL",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def run_build(options: argparse.Namespace) -> dict[str, Any]:
    global _ACTIVE
    require(options.build is True, "require one explicit C V12 native build")
    contract, active = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256,
    )
    label = checked_label(options.label)
    v8, v7, kernel = active["v8"], active["v7"], active["kernel"]
    expected = {ORIGINAL[0] + "=" + ORIGINAL[1],
                ADAPTER[0] + "=" + ADAPTER[1]}
    require(type(options.owned_source_sha256) is list
            and len(options.owned_source_sha256) == 2
            and set(options.owned_source_sha256) == expected,
            "independently pin both complete unchanged original C source owners")
    require(_ACTIVE is None and not _APPLIED,
            "reject a reused, nested, or already executed C V12 build")
    for failed in (False, True):
        for name in evidence_names(label, failure=failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE / name)
    _ACTIVE = active
    v8.install_v8_build_kernel(v7, kernel)
    kernel.copy_snapshot = copy_snapshot
    workdir = tempfile.mkdtemp(prefix=v8.WORK_PREFIX + FAMILY + "-", dir="/tmp")
    v8.checked_workdir(workdir, FAMILY)
    steps: list[dict[str, Any]] = []
    phases: list[dict[str, Any]] = []
    try:
        v8.prepare_private_phases(kernel, workdir)
        sources = {ORIGINAL[0]: read_owner(*ORIGINAL),
                   ADAPTER[0]: read_owner(*ADAPTER)}
        for phase in PHASES:
            result = kernel.exact_build_phase(
                workdir, FAMILY, phase, sources, steps,
            )
            result["native_forensics"] = v8.record_native_forensics(
                v7, kernel, workdir, phase, result, steps,
            )
            phases.append(result)
        reproduction = verify_reproducibility(v8, v7, workdir, phases, steps)
        require(reproduction.get("actual_compiler_process_count") == 14
                and reproduction.get("source_apply_count") == 2,
                "require the exact genuine two-phase source-build schedule")
        report = {
            "schema": SCHEMA + "-actual-native-build", "version": VERSION,
            "status": "PASS", "family": FAMILY, "label": label,
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "contract_sha256": options.contract_sha256,
            "frozen_context": contract,
            "root_prefix": "rebar-phase2-native-build-v8-c-",
            "historical_evidence_owner_count": 139,
            "historical_authenticated_reference_count": 144,
            "historical_c_semantic_mismatch_count": 1262,
            "historical_c_candidate_worker_count": 13,
            "historical_rust_build_process_count": 28,
            "historical_zig_build_process_count": 26,
            "targeted_legacy_pickle_mismatch_count": 32,
            "original_source_sha256": ORIGINAL[1],
            "v1_derived_source_sha256": V1_DERIVED[0],
            "v2_derived_source_sha256": V2_DERIVED[0],
            "v2_derived_source_bytes": V2_DERIVED[1],
            "source_apply_count": len(_APPLIED),
            "expected_compiler_process_count": 14,
            "actual_compiler_process_count": len(steps),
            "phase_count": len(phases), "phases": phases,
            "compiler_processes": steps,
            "reproducibility": reproduction,
            "candidate_correctness": "NOT MEASURED",
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }
        return publish_report(kernel, report, label)
    except Exception as error:
        read_owner(*ORIGINAL)
        read_owner(*ADAPTER)
        report = {
            "schema": SCHEMA + "-actual-native-build", "version": VERSION,
            "status": "FAIL", "family": FAMILY, "label": label,
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "contract_sha256": options.contract_sha256,
            "frozen_context": contract,
            "root_prefix": "rebar-phase2-native-build-v8-c-",
            "historical_evidence_owner_count": 139,
            "historical_authenticated_reference_count": 144,
            "historical_c_semantic_mismatch_count": 1262,
            "historical_c_candidate_worker_count": 13,
            "historical_rust_build_process_count": 28,
            "historical_zig_build_process_count": 26,
            "targeted_legacy_pickle_mismatch_count": 32,
            "original_source_sha256": ORIGINAL[1],
            "v1_derived_source_sha256": V1_DERIVED[0],
            "v2_derived_source_sha256": V2_DERIVED[0],
            "v2_derived_source_bytes": V2_DERIVED[1],
            "source_apply_count": sum((workdir, phase) in _APPLIED
                                      for phase in PHASES),
            "expected_compiler_process_count": 14,
            "actual_compiler_process_count": len(steps),
            "phase_count": len(phases), "phases": phases,
            "compiler_processes": steps,
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            "candidate_correctness": "NOT MEASURED",
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }
        return publish_report(kernel, report, label)


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    if arguments is None:
        arguments = sys.argv[1:]
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require one exact C V12 build-source command")
    flags = [item for item in arguments if item.startswith("--")]
    for flag in set(flags):
        require(flag == "--owned-source-sha256" or flags.count(flag) == 1,
                "reject duplicated or ambiguous C V12 authorizations")
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
    checked_digest(options.source_sha256, "C V12 source")
    checked_digest(options.protocol_sha256, "C V12 protocol")
    if options.contract_sha256 is not None:
        checked_digest(options.contract_sha256, "C V12 machine contract")
    if options.self_test or options.render_contract:
        require(options.contract_sha256 is None and options.family is None
                and options.label is None and not options.owned_source_sha256,
                "source-only modes never authorize a native phase or evidence")
    elif options.verify_frozen_context:
        require(options.contract_sha256 is not None and options.family is None
                and options.label is None and not options.owned_source_sha256,
                "read-only verification never authorizes a private source build")
    else:
        require(options.contract_sha256 is not None
                and options.family == FAMILY and options.label is not None,
                "independently authorize the exact C family, contract, and label")
        checked_label(options.label)
        expected = {ORIGINAL[0] + "=" + ORIGINAL[1],
                    ADAPTER[0] + "=" + ADAPTER[1]}
        require(type(options.owned_source_sha256) is list
                and len(options.owned_source_sha256) == 2
                and set(options.owned_source_sha256) == expected,
                "independently pin both unchanged original C source owners")
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
            frozen, loaded = verify_context(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256,
            )
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
                    "published_graph_version": 25,
                    "published_graph_owner_count": 4,
                    "published_graph_reproduced": True,
                    "repository_evidence_owner_count": 139,
                    "authenticated_digest_addressed_history_paths": 144,
                    "actual_c_campaign_evidence_owner_count": 30,
                    "actual_c_candidate_workers": 13,
                    "actual_c_completed_suite_count": 13,
                    "actual_c_fully_passing_suite_count": 8,
                    "actual_c_verified_passing_case_count": 7325,
                    "actual_c_semantic_mismatch_count": 1262,
                    "actual_c_infrastructure_failure_count": 0,
                    "actual_public_type_case_count": 6912,
                    "actual_public_type_mismatch_count": 248,
                    "actual_legacy_pickle_mismatch_count": 32,
                    "preserved_modern_pickle_protocol_counts":
                        {"2": 16, "3": 16, "4": 16, "5": 16},
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
        return 0
    except (BuildError, OSError, ValueError, TypeError, AttributeError,
            KeyError, EOFError, gzip.BadGzipFile) as error:
        sys.stderr.write("C PICKLE SOURCE BUILD V12: FAIL: "
                         + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
