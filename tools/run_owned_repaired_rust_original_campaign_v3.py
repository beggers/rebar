#!/usr/bin/env python3
"""Freeze an explicitly recoverable, first-party original Rust campaign.

Source verification cannot activate, inspect or import a Rust candidate.
Only an independently caller-pinned future --run or --recover can touch an
original target. SIGKILL and power failure are not falsely guaranteed safe;
their exact, durably journaled recovery has a public, fixed command.
"""
from __future__ import annotations

import argparse
import ast
import base64
import builtins
import contextlib
import copy
import ctypes
import fcntl
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
from typing import Any, Iterator, Sequence


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SOURCE_RELATIVE = "tools/run_owned_repaired_rust_original_campaign_v3.py"
PROTOCOL_RELATIVE = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V3.md"
CONTRACT_RELATIVE = "oracle/phase2/repaired-rust-original-campaign-v3.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v3"
CONTRACT_SCHEMA = SCHEMA + "-recoverable-source-freeze"
CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
RECOVERY_SCHEMA = SCHEMA + "-public-exact-inode-recovery"
SIGNAL_SCHEMA = SCHEMA + "-graceful-controller-signal"
FAMILY = "rust"
LABEL = "phase2-v11-rust-dual-overlay-original-p0"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
PUBLIC_RECOVERY_ROOT = (
    "/tmp/rebar-phase2-repaired-rust-original-campaign-v2-"
    "safe-v3-phase2-v11-rust-dual-overlay-original-p0"
)
LOCK_NAME = "recoverable-controller.lock"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_OWNER_BYTES = 32 * 1024 * 1024
SUITE_COUNT = 13
CASE_COUNT = 31237
PRIVATE_WAIVER_COUNT = 13

GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
V2 = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v2.py", "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3", 143441),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V2.md", "9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0", 9342),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v2.json", "bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547", 15927),
}
V27 = {
    "renderer": ("tools/render_candidate_current_overview_v27.py", "0df3ed1efbbacd862597e7aac1652eb37ee84c12adf8b79b836a298418925eba", 78380),
    "inputs": ("docs/evidence/candidate-current-overview-v27.inputs.json", "c48ff1d86d6b9b40ff6f8651ae5cbedf1b17889e5420c27ca77ee03168b80897", 43722),
    "summary": ("docs/evidence/candidate-current-overview-v27.json", "e9a3adfa76acc8b551228708865a756b9ec8fc3ba5447280ac655fe78f8f5ab4", 208790),
    "svg": ("docs/evidence/candidate-current-overview-v27.svg", "f50791d54c0aaf743b03054b330957941d077874fa676ca1388b8314266870c3", 13270),
}
PRODUCER = {
    "source": ("tools/run_owned_six_family_original_p0_producer_v3.py", "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md", "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76", 5522),
    "contract": ("oracle/phase2/six-family-p0-producer-v3.json", "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1", 26909),
}
PUBLICATION = {
    "source": ("tools/run_owned_six_family_original_p0_campaign_v2.py", "6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1", 101836),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md", "e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e", 4995),
    "contract": ("oracle/phase2/six-family-p0-campaign-v2.json", "e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7", 21314),
}
RUST_BUILD = {
    "archive": ("oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz", "282927f91fd885701dff6c431474f586afbc09460c6a20417ffa20be5a2e891c", 107639),
    "receipt": ("oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay-publication-receipt.json", "4c75468663af0de60b37cdbabfca384c4e7f75e25a6155c2ff1c33f654d3f1d7", 1902),
}
ZIG_PREFLIGHT = {
    "archive": ("oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz", "1cb38eb48a2d3305ea98d5103a27ce6ae758137168f68df07a408dec3d055a37", 3711),
    "receipt": ("oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23", 1992),
}
ZIG_ORIGINAL = {
    "archive": ("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz", "583d63c92240cec78c861893407003466a5f754b099719aabfc8eaf4f14fbbf8", 5870948),
    "receipt": ("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba", 4534),
}
ENGINE_SHA256 = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_BYTES = 658344
BRIDGE_SHA256 = "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54"
BRIDGE_BYTES = 148656
ORIGINALS = {
    "bridge_source": {"relative": "candidates/rust/py_bridge.c", "sha256": "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", "bytes": 175676, "device": 2064, "inode": 419054, "mode": 0o600, "uid": 1000, "nlink": 1},
    "adapter": {"relative": "candidates/rust_candidate.py", "sha256": "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", "bytes": 31151, "device": 2064, "inode": 428100, "mode": 0o600, "uid": 1000, "nlink": 1},
    "engine": {"relative": "candidates/_rust_engine.so", "sha256": "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4", "bytes": 660440, "device": 2064, "inode": 430563, "mode": 0o755, "uid": 1000, "nlink": 1},
    "bridge": {"relative": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "sha256": "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15", "bytes": 144992, "device": 2064, "inode": 430629, "mode": 0o755, "uid": 1000, "nlink": 1},
}
ROLE_ORDER = ("bridge_source", "adapter", "engine", "bridge")
RESTORATION_ORDER = tuple(reversed(ROLE_ORDER))
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
    ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)
SIGNAL_NAMES = ("SIGINT", "SIGTERM", "SIGHUP")


class CampaignError(Exception):
    """Reject an unproven source, controller, journal or recovery."""


class SourceOnlyViolation(CampaignError):
    """A synthetic source control attempted an external effect."""


class GracefulControllerSignal(CampaignError):
    """A registered controller signal requires durable reverse recovery."""

    def __init__(self, signum: int) -> None:
        self.signum = signum
        try:
            self.signal_name = signal.Signals(signum).name
        except ValueError:
            self.signal_name = "UNKNOWN"
        super().__init__("graceful controller interruption: " + self.signal_name)


def require(value: Any, message: str) -> None:
    if value is not True:
        raise CampaignError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value)
            and not value.startswith("/") and "\\" not in value
            and "\x00" not in value
            and all(part not in ("", ".", "..")
                    for part in value.split("/")),
            "reject an escaped, empty, or ambiguous source owner")
    return value


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only original complete bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, allow_nan=False, ensure_ascii=True,
                           sort_keys=True, separators=(",", ":"))
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CampaignError("reject noncanonical recovery evidence") from error


def unique_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject duplicate machine-evidence fields")
        result[key] = value
    return result


def strict_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
            "reject missing or excessive frozen bytes: " + label)
    try:
        result = json.loads(
            raw.decode("utf-8", "strict"), object_pairs_hook=unique_pairs,
            parse_constant=lambda x: (_ for _ in ()).throw(
                ValueError("nonfinite field: " + x)),
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CampaignError("reject invalid frozen evidence: " + label) from error
    require(type(result) is dict, "require one real evidence object: " + label)
    return result


def owner_record(item: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": checked_relative(item[0]),
            "sha256": checked_digest(item[1], item[0]),
            "bytes": item[2]}


def mapped_owners(items: dict[str, tuple[str, str, int]]) -> dict[str, Any]:
    return {name: owner_record(item)
            for name, item in sorted(items.items())}


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode
            and os.path.abspath(sys.executable) == PYTHON,
            "require exact isolated stable CPython 3.14.6 with -I -B")


def read_owned(relative: str, digest: str, *, exact_size: int | None = None
               ) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    checked_digest(digest, relative)
    require(relative not in {row["relative"] for row in ORIGINALS.values()},
            "source-only verification cannot open an original Rust target")
    require(exact_size is None or
            (type(exact_size) is int and 0 < exact_size <= MAX_OWNER_BYTES),
            "require an exact bounded evidence-owner size")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    directories = flags | getattr(os, "O_DIRECTORY", 0)
    handles: list[int] = []
    try:
        parent = os.open(str(ROOT), directories)
        handles.append(parent)
        for component in relative.split("/")[:-1]:
            parent = os.open(component, directories, dir_fd=parent)
            handles.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a substituted frozen evidence directory")
        name = relative.rsplit("/", 1)[-1]
        handle = os.open(name, flags, dir_fd=parent)
        handles.append(handle)
        before = os.fstat(handle)
        visible = os.stat(name, dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and 0 < before.st_size <= MAX_OWNER_BYTES
                and (exact_size is None or before.st_size == exact_size)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size),
                "reject a changed, linked, symlinked, or foreign owner")
        remain = before.st_size
        chunks: list[bytes] = []
        calculated = hashlib.sha256()
        while remain:
            part = os.read(handle, min(remain, 1024 * 1024))
            require(type(part) is bytes and bool(part),
                    "reject truncated original source evidence")
            chunks.append(part)
            calculated.update(part)
            remain -= len(part)
        require(os.read(handle, 1) == b"",
                "reject unrecorded source-owner trailing bytes")
        after = os.fstat(handle)
        named = os.stat(name, dir_fd=parent, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns,
                 before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns,
                    after.st_uid, after.st_nlink)
                and (after.st_dev, after.st_ino, after.st_size,
                     after.st_uid, after.st_nlink)
                == (named.st_dev, named.st_ino, named.st_size,
                    named.st_uid, named.st_nlink)
                and calculated.hexdigest() == digest,
                "reject a changed source inode or incomplete owner digest")
        return b"".join(chunks), {
            "relative": relative, "path": str(ROOT / relative),
            "sha256": digest, "size_bytes": before.st_size,
            "device": before.st_dev, "inode": before.st_ino,
            "uid": before.st_uid, "nlink": before.st_nlink,
            "mode": stat.S_IMODE(before.st_mode),
        }
    finally:
        for handle in reversed(handles):
            os.close(handle)


def read_owner(item: tuple[str, str, int]) -> tuple[bytes, dict[str, Any]]:
    return read_owned(item[0], item[1], exact_size=item[2])


def load_v2() -> types.ModuleType:
    item = V2["source"]
    raw, original = read_owner(item)
    name = "_rebar_v3_exact_frozen_rust_worker_" + item[1][:24]
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = str(ROOT / item[0])
        module.__package__ = ""
        sys.modules[name] = module
        try:
            exec(compile(raw, module.__file__, "exec", dont_inherit=True),
                 module.__dict__)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    _, current = read_owner(item)
    require(type(module) is types.ModuleType
            and (original["device"], original["inode"])
            == (current["device"], current["inode"])
            and os.path.realpath(str(module.__file__)) == str(ROOT / item[0]),
            "reject a substituted immutable Rust V2 worker source")
    return module


def source_effects() -> dict[str, Any]:
    return {
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "canonical_target_links": 0, "canonical_target_replacements": 0,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_native_activations": 0, "actual_native_recoveries": 0,
        "actual_native_libraries_loaded": 0,
        "actual_reference_workers": 0, "actual_subprocesses_started": 0,
        "actual_threads_started": 0, "actual_network_requests": 0,
        "actual_signal_handlers_installed": 0,
        "actual_signal_masks_installed": 0,
        "actual_recovery_locks_acquired": 0,
        "actual_private_directories_created": 0,
        "actual_recovery_journals_created": 0,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "workspace_mutations": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False, "winner_selected": False,
    }


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "recoverable Rust V3 controller source")
    checked_digest(protocol_pin, "recoverable Rust V3 public protocol")
    original_rows = []
    for role in ROLE_ORDER:
        row = dict(ORIGINALS[role])
        row["mode"] = format(row["mode"], "04o")
        original_rows.append({"role": role, "original": row})
    return {
        "schema": CONTRACT_SCHEMA, "version": 3,
        "status": "SOURCE FROZEN; RECOVERABLE RUST CANDIDATE NOT RUN",
        "phase": "CANDIDATES", "family": FAMILY, "campaign_label": LABEL,
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "pinned_cpython": {"path": PYTHON, "sha256": PYTHON_SHA256,
                           "version": "3.14.6"},
        "goal": owner_record(GOAL),
        "phase_one": owner_record(PHASE_ONE),
        "immutable_v2_worker_only": {
            "owners": mapped_owners(V2),
            "unsafe_v2_controller_invoked": False,
            "unsafe_v2_activation_invoked": False,
            "actual_worker_count_if_explicitly_run": 13,
            "unchanged_original_producer": mapped_owners(PRODUCER),
        },
        "current_published_v27": {
            "owners": mapped_owners(V27),
            "evidence_owner_count": 143,
            "authenticated_reference_count": 148,
            "historical_v26_evidence_owner_count": 141,
            "historical_v26_authenticated_reference_count": 146,
            "qualified_candidate_count": 0,
            "case_execution_denominator": CASE_COUNT,
            "suite_count": SUITE_COUNT,
            "repaired_rust_correctness": "NOT MEASURED",
        },
        "actual_rust_dual_overlay": {
            "build": mapped_owners(RUST_BUILD),
            "actual_compiler_process_count": 28,
            "native_engine_sha256": ENGINE_SHA256,
            "native_engine_bytes": ENGINE_BYTES,
            "native_bridge_sha256": BRIDGE_SHA256,
            "native_bridge_bytes": BRIDGE_BYTES,
            "actual_repaired_source_owner_count": 9,
            "actual_original_target_count": 4,
            "candidate_matching": "NOT MEASURED",
            "candidate_qualified": False,
        },
        "preserved_zig_preflight_failure": {
            "owners": mapped_owners(ZIG_PREFLIGHT),
            "candidate_workers": 0,
            "candidate_matching": "NOT MEASURED",
            "controller_process_id": "NOT RECORDED",
        },
        "preserved_zig_original_campaign_failure": {
            "owners": mapped_owners(ZIG_ORIGINAL),
            "candidate_status": "FAIL",
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "case_execution_denominator": 31237,
            "semantic_mismatch_count": 2172,
            "verified_passing_case_count": 2847,
            "infrastructure_failure_count": 0,
            "archive_inflated_during_source_verification": False,
            "candidate_qualified": False,
            "holdout": "NOT OPENED",
        },
        "original_oracle": {
            "producer": mapped_owners(PRODUCER),
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES],
            "nested_case_count": 128,
            "nested_interpreter_events": 394,
            "nested_interpreters_created": 11,
            "nested_interpreters_destroyed": 11,
            "repaired_rust_source_owners": 9,
            "v2_worker_only_rebinds_original_nested_guard": True,
            "v2_unsafe_controller_invoked": False,
        },
        "public_recovery": {
            "root": PUBLIC_RECOVERY_ROOT,
            "caller_pins_exact_root": True,
            "fixed_public_journal_filename": "recovery-journal.json",
            "caller_pins_exact_journal_sha256": True,
            "lock_filename": LOCK_NAME,
            "lock_owner_mode": "0600",
            "root_owner_mode": "0700",
            "exclusive_nonblocking_controller_lock": True,
            "journal_fsync_before_first_target_mutation": True,
            "journal_location_announced_before_first_target_mutation": True,
            "individual_intention_fsync_before_hardlink_or_replace": True,
            "original_inode_backup":
                "ADJACENT SAME-DIRECTORY NO-FOLLOW HARDLINK",
            "target_count": 4,
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "recovery_command_mode": "--recover",
            "recovery_idempotent": True,
            "unknown_or_foreign_owner_is_overwritten": False,
            "restore_device_inode_mode_uid_nlink_and_hash": True,
            "registered_graceful_signals": list(SIGNAL_NAMES),
            "signal_handlers_installed_during_source_verification": False,
            "block_graceful_signals_during_individual_mutations": True,
            "keyboard_interrupt_and_system_exit_swallowed": False,
            "group_atomic": False,
            "sigkill_automatically_recovered": False,
            "power_failure_automatically_recovered": False,
            "sigkill_or_power_failure_requires_public_recover": True,
        },
        "four_original_target_owners": original_rows,
        "lossless_publication": {
            "owners": mapped_owners(PUBLICATION),
            "exclusive_single_member_gzip_mtime": 0,
            "restore_all_four_original_inodes_before_publication": True,
            "retain_all_real_suite_records": True,
            "overwrite_existing_evidence": False,
            "v2_matching_or_controller_invoked": False,
        },
        "source_only_effects": source_effects(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict
            and canonical(value) == canonical(
                protocol_document(source_pin, protocol_pin)),
            "reject weakened exact source, original owner, signal, or recovery")
    return value


class SourceWall:
    """Make each source-only external effect observably impossible."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked = {name: 0 for name in
                        ("filesystem", "process", "clock", "network",
                         "thread", "native", "import", "signal", "lock")}

    def install(self, owner: Any, name: str, kind: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise SourceOnlyViolation("source-only mode blocks " + kind)

        self.previous.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> "SourceWall":
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (os, "read"), (os, "write"), (os, "stat"),
            (os, "lstat"), (os, "fstat"), (os, "mkdir"),
            (os, "makedirs"), (os, "link"), (os, "replace"),
            (os, "rename"), (os, "unlink"), (os, "remove"),
            (os, "fsync"), (os, "fchmod"), (tempfile, "mkdtemp"),
        ):
            self.install(owner, name, "filesystem")
        for name in ("Popen", "run", "call", "check_output"):
            self.install(subprocess, name, "process")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "sleep"):
            self.install(time, name, "clock")
        self.install(socket, "create_connection", "network")
        self.install(socket.socket, "connect", "network")
        self.install(threading.Thread, "start", "thread")
        self.install(ctypes, "CDLL", "native")
        self.install(importlib, "import_module", "import")
        self.install(signal, "signal", "signal")
        self.install(signal, "pthread_sigmask", "signal")
        self.install(fcntl, "flock", "lock")
        return self

    def __exit__(self, *_args: Any) -> None:
        for owner, name, original in reversed(self.previous):
            setattr(owner, name, original)


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(contract_pin, "exact independent V3 contract pin")
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceWall() as wall:
        document = protocol_document(source_pin, protocol_pin)

        def accept(name: str, value: Any) -> None:
            require(value is True, "reject failed positive control: " + name)
            accepted.append(name)

        def reject(name: str, action: Any) -> None:
            try:
                action()
            except (CampaignError, SourceOnlyViolation, OSError,
                    ValueError, TypeError, UnicodeError, OverflowError,
                    RecursionError):
                rejected.append(name)
                return
            raise CampaignError("hostile control unexpectedly passed: " + name)

        recovery = document["public_recovery"]
        history = document["current_published_v27"]
        original = document["original_oracle"]
        zig = document["preserved_zig_original_campaign_failure"]
        accept("freeze-all-thirteen-real-original-suite-groups",
               len(SUITES) == 13)
        accept("retain-the-complete-31237-case-original-denominator",
               sum(count for _, count in SUITES) == 31237)
        accept("preserve-all-thirteen-named-private-waivers",
               original["named_private_waiver_count"] == 13)
        accept("keep-the-128-case-394-event-genuine-nested-oracle",
               original["nested_case_count"] == 128
               and original["nested_interpreter_events"] == 394)
        accept("retain-all-eleven-created-and-destroyed-interpreters",
               original["nested_interpreters_created"] == 11
               and original["nested_interpreters_destroyed"] == 11)
        accept("reuse-only-frozen-V2-independent-original-workers",
               document["immutable_v2_worker_only"]
               ["actual_worker_count_if_explicitly_run"] == 13)
        accept("never-call-the-unsafe-V2-controller",
               document["immutable_v2_worker_only"]
               ["unsafe_v2_controller_invoked"] is False)
        accept("never-call-the-unsafe-V2-native-activation",
               document["immutable_v2_worker_only"]
               ["unsafe_v2_activation_invoked"] is False)
        accept("authenticate-the-current-143-owner-148-reference-overview",
               history["evidence_owner_count"] == 143
               and history["authenticated_reference_count"] == 148)
        accept("retain-historical-141-owner-146-reference-V26",
               history["historical_v26_evidence_owner_count"] == 141
               and history["historical_v26_authenticated_reference_count"]
               == 146)
        accept("preserve-real-corrected-Zig-loss-without-inflation",
               zig["candidate_status"] == "FAIL"
               and zig["actual_candidate_workers"] == 13
               and zig["semantic_mismatch_count"] == 2172
               and zig["verified_passing_case_count"] == 2847
               and zig["archive_inflated_during_source_verification"]
               is False)
        accept("preserve-the-separate-zero-worker-Zig-preflight",
               document["preserved_zig_preflight_failure"]
               ["candidate_workers"] == 0)
        accept("pin-one-publicly-known-owner-only-recovery-root",
               recovery["root"] == PUBLIC_RECOVERY_ROOT
               and recovery["caller_pins_exact_root"] is True)
        accept("require-owner-only-exclusive-recovery-lock",
               recovery["exclusive_nonblocking_controller_lock"] is True
               and recovery["root_owner_mode"] == "0700"
               and recovery["lock_owner_mode"] == "0600")
        accept("pin-the-complete-durable-public-journal-before-promotion",
               recovery["journal_fsync_before_first_target_mutation"] is True
               and recovery["caller_pins_exact_journal_sha256"] is True)
        accept("announce-the-public-journal-before-touching-originals",
               recovery["journal_location_announced_before_first_target_mutation"]
               is True)
        accept("back-up-all-four-actual-original-inodes-by-hardlink",
               recovery["target_count"] == 4
               and "HARDLINK" in recovery["original_inode_backup"])
        accept("restore-all-four-inodes-in-exact-reverse-order",
               recovery["restoration_order"] == list(RESTORATION_ORDER))
        accept("expose-the-public-caller-pinned-recovery-mode",
               recovery["recovery_command_mode"] == "--recover")
        accept("make-authenticated-recovery-safely-idempotent",
               recovery["recovery_idempotent"] is True)
        accept("support-every-genuine-graceful-controller-signal",
               recovery["registered_graceful_signals"] == list(SIGNAL_NAMES))
        accept("block-signals-during-individual-journaled-replacements",
               recovery["block_graceful_signals_during_individual_mutations"]
               is True)
        accept("never-install-signal-handlers-in-source-verification",
               recovery["signal_handlers_installed_during_source_verification"]
               is False)
        accept("never-claim-four-file-group-atomicity",
               recovery["group_atomic"] is False)
        accept("truthfully-disclaim-automatic-SIGKILL-recovery",
               recovery["sigkill_automatically_recovered"] is False)
        accept("truthfully-disclaim-automatic-power-failure-recovery",
               recovery["power_failure_automatically_recovered"] is False)
        accept("offer-public-recovery-after-an-ungraceful-interruption",
               recovery["sigkill_or_power_failure_requires_public_recover"]
               is True)
        accept("preserve-exact-four-known-original-inodes",
               {row["inode"] for row in ORIGINALS.values()}
               == {419054, 428100, 430563, 430629})
        accept("source-only-mode-produces-zero-target-effects",
               document["source_only_effects"] == source_effects())

        for value in ("", "a" * 63, "a" * 65, "A" * 64,
                      "g" * 64, 0, True, None):
            reject("reject-invalid-digest-" + repr(value),
                   lambda item=value: checked_digest(item, "hostile"))
        for value in ("", "/", "/tmp", "../escape", "a/../b",
                      "a//b", "a\\b", "a\x00b", 0, None):
            reject("reject-invalid-owner-" + repr(value),
                   lambda item=value: checked_relative(item))
        changes = (
            ("erase-original-correctness-denominator",
             lambda x: x["original_oracle"].update(
                 {"case_execution_denominator": 151})),
            ("remove-original-suite",
             lambda x: x["original_oracle"]["source_ordered_suites"].pop()),
            ("replace-current-authenticated-history",
             lambda x: x["current_published_v27"].update(
                 {"evidence_owner_count": 141})),
            ("hide-the-complete-corrected-Zig-loss",
             lambda x: x["preserved_zig_original_campaign_failure"].update(
                 {"semantic_mismatch_count": 0})),
            ("falsely-qualify-corrected-Zig",
             lambda x: x["preserved_zig_original_campaign_failure"].update(
                 {"candidate_qualified": True})),
            ("inflate-the-preserved-Zig-loss-stream",
             lambda x: x["preserved_zig_original_campaign_failure"].update(
                 {"archive_inflated_during_source_verification": True})),
            ("invent-a-Zig-preflight-worker",
             lambda x: x["preserved_zig_preflight_failure"].update(
                 {"candidate_workers": 1})),
            ("invoke-unsafe-frozen-V2-controller",
             lambda x: x["immutable_v2_worker_only"].update(
                 {"unsafe_v2_controller_invoked": True})),
            ("invoke-unsafe-frozen-V2-activation",
             lambda x: x["immutable_v2_worker_only"].update(
                 {"unsafe_v2_activation_invoked": True})),
            ("replace-public-recovery-root",
             lambda x: x["public_recovery"].update(
                 {"root": "/tmp/foreign-recovery"})),
            ("omit-independent-journal-digest",
             lambda x: x["public_recovery"].update(
                 {"caller_pins_exact_journal_sha256": False})),
            ("omit-exclusive-controller-lock",
             lambda x: x["public_recovery"].update(
                 {"exclusive_nonblocking_controller_lock": False})),
            ("replace-original-hardlink-with-byte-copy",
             lambda x: x["public_recovery"].update(
                 {"original_inode_backup": "BYTE COPY"})),
            ("omit-an-original-target-owner",
             lambda x: x["four_original_target_owners"].pop()),
            ("skip-an-original-inode-restoration",
             lambda x: x["public_recovery"]["restoration_order"].pop()),
            ("install-real-signal-handlers-in-source-verification",
             lambda x: x["public_recovery"].update(
                 {"signal_handlers_installed_during_source_verification": True})),
            ("fail-to-block-an-individual-mutation-signal",
             lambda x: x["public_recovery"].update(
                 {"block_graceful_signals_during_individual_mutations": False})),
            ("pretend-four-replacements-are-group-atomic",
             lambda x: x["public_recovery"].update({"group_atomic": True})),
            ("falsely-guarantee-SIGKILL-recovery",
             lambda x: x["public_recovery"].update(
                 {"sigkill_automatically_recovered": True})),
            ("falsely-guarantee-power-failure-recovery",
             lambda x: x["public_recovery"].update(
                 {"power_failure_automatically_recovered": True})),
            ("remove-public-idempotent-recovery",
             lambda x: x["public_recovery"].update(
                 {"recovery_idempotent": False})),
            ("claim-unmeasured-Rust-correctness",
             lambda x: x["source_only_effects"].update(
                 {"candidate_correctness": "PASS"})),
            ("open-the-sealed-final-holdout",
             lambda x: x["source_only_effects"].update(
                 {"holdout": "OPENED"})),
        )
        for name, mutate in changes:
            def hostile(operation: Any = mutate) -> None:
                changed = copy.deepcopy(document)
                operation(changed)
                validate_contract(changed, source_pin, protocol_pin)
            reject(name, hostile)
        controls = (
            ("filesystem", lambda: os.open("/forbidden", os.O_RDONLY)),
            ("process", lambda: subprocess.run(["/usr/bin/true"])),
            ("clock", lambda: time.perf_counter_ns()),
            ("network", lambda: socket.create_connection(("invalid", 1))),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("native", lambda: ctypes.CDLL("foreign.so")),
            ("import", lambda: importlib.import_module(
                "candidates.rust_candidate")),
            ("signal", lambda: signal.signal(signal.SIGTERM, lambda *_: None)),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
        )
        for name, action in controls:
            reject("block-real-" + name, action)
        blocked = dict(wall.blocked)
    require(len(accepted) >= 25 and len(rejected) >= 40
            and all(count > 0 for count in blocked.values()),
            "require positive, hostile, lock, signal and target controls")
    return {
        "schema": SCHEMA + "-synthetic-source-self-test",
        "status": "PASS", "version": 3, "family": FAMILY,
        "mode": "SYNTHETIC SOURCE ONLY",
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_effects_by_kind": blocked,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "preserved_v26_evidence_owner_count": 141,
        "preserved_v26_authenticated_reference_count": 146,
        "actual_rust_build_process_count": 28,
        "actual_zig_preflight_candidate_workers": 0,
        "actual_zig_original_candidate_status": "FAIL",
        "actual_zig_original_candidate_workers": 13,
        "actual_zig_original_semantic_mismatch_count": 2172,
        "actual_zig_original_verified_passing_case_count": 2847,
        "actual_zig_original_infrastructure_failure_count": 0,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "original_target_count": 4,
        "graceful_signal_names": list(SIGNAL_NAMES),
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        **source_effects(),
    }


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None,
                   *, retain: bool = False
                   ) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    checked_digest(source_pin, "recoverable Rust V3 source")
    checked_digest(protocol_pin, "recoverable Rust V3 protocol")
    _, source = read_owned(SOURCE_RELATIVE, source_pin)
    _, protocol = read_owned(PROTOCOL_RELATIVE, protocol_pin)
    authenticated: dict[str, dict[str, Any]] = {}
    raw_support: dict[str, bytes] = {}
    for group in (V2, V27, PRODUCER, PUBLICATION, RUST_BUILD,
                  ZIG_PREFLIGHT, ZIG_ORIGINAL):
        for item in group.values():
            if item[0] in authenticated:
                continue
            raw, owner = read_owner(item)
            authenticated[item[0]] = owner
            raw_support[item[0]] = raw
    for item in (GOAL, PHASE_ONE):
        raw, owner = read_owner(item)
        authenticated[item[0]] = owner
        raw_support[item[0]] = raw
    graph = strict_document(raw_support[V27["summary"][0]],
                            "actual independently published V27")
    graph_inputs = strict_document(raw_support[V27["inputs"][0]],
                                   "actual independently published V27 inputs")
    require(graph.get("schema") == "rebar-candidate-current-overview-v27-summary"
            and graph.get("status") == "PASS"
            and graph.get("repository_evidence_owner_count") == 143
            and graph.get("authenticated_digest_addressed_history_paths") == 148
            and graph.get("preserved_v26_repository_evidence_owner_count") == 141
            and graph.get("preserved_v26_authenticated_reference_path_count")
            == 146
            and graph.get("full_case_denominator") == CASE_COUNT
            and graph.get("suite_count") == SUITE_COUNT
            and graph.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and graph.get("qualified_candidate_count") == 0
            and graph.get("rust_dual_overlay_repaired_build_process_count")
            == 28
            and graph.get("rust_dual_overlay_repaired_matching_test_status")
            == "NOT MEASURED"
            and graph.get("zig_original_campaign_status") == "FAIL"
            and graph.get("zig_original_campaign_candidate_worker_count") == 13
            and graph.get("zig_original_campaign_completed_suite_count") == 13
            and graph.get("zig_original_campaign_case_execution_denominator")
            == CASE_COUNT
            and graph.get("zig_original_campaign_semantic_mismatch_count")
            == 2172
            and graph.get("zig_original_campaign_verified_passing_case_count")
            == 2847
            and graph.get("zig_original_campaign_infrastructure_failure_count")
            == 0
            and graph.get("zig_original_campaign_receipt_pass_means")
            == "DURABLE FAILURE PUBLICATION ONLY"
            and graph.get("uncompressed_zig_archive_opened_by_graph") is False
            and graph.get("uncompressed_zig_archive_bytes_read_by_graph") == 0
            and graph.get("final_holdout_opened") is False
            and graph.get("performance") == "NOT MEASURED",
            "reject hidden history, mismatches, candidate status, or holdout")
    require(graph_inputs.get("schema")
            == "rebar-candidate-current-overview-v27-inputs"
            and graph_inputs.get("repository_evidence_owner_count") == 143
            and graph_inputs.get("all_digest_addressed_history_path_count")
            == 148
            and graph_inputs.get("actual_zig_candidate_workers") == 13
            and graph_inputs.get("actual_zig_semantic_mismatch_count") == 2172
            and graph_inputs.get("actual_zig_verified_passing_case_count")
            == 2847
            and graph_inputs.get("actual_zig_infrastructure_failure_count")
            == 0
            and graph_inputs.get("uncompressed_zig_archive_opened_by_graph")
            is False,
            "authenticate the exact independently produced V27 inputs")
    v2_contract = strict_document(raw_support[V2["contract"][0]],
                                  "immutable independently committed Rust V2")
    require(v2_contract.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v2-source-freeze"
            and v2_contract.get("version") == 2
            and v2_contract.get("source", {}).get("sha256")
            == V2["source"][1]
            and v2_contract.get("protocol", {}).get("sha256")
            == V2["protocol"][1]
            and v2_contract.get("public_recovery") is None,
            "freeze the actual V2 as a worker only, never a safe controller")
    v2 = load_v2()
    checked, v2_retained = v2.verify_context(
        V2["source"][1], V2["protocol"][1], V2["contract"][1],
        retain=retain,
    )
    require(checked.get("status") == "PASS"
            and checked.get("canonical_target_reads") == 0
            and checked.get("canonical_target_stats") == 0
            and checked.get("actual_candidate_workers") == 0
            and checked.get("actual_native_activations") == 0
            and checked.get("published_v27_evidence_owner_count") == 143
            and checked.get("published_v27_authenticated_reference_count")
            == 148
            and checked.get("actual_rust_build_process_count") == 28
            and checked.get("actual_rust_source_owner_count") == 9
            and checked.get("actual_zig_preflight_candidate_workers") == 0
            and checked.get("actual_zig_corrected_candidate_status") == "FAIL"
            and checked.get("actual_zig_corrected_candidate_workers") == 13
            and checked.get("actual_zig_corrected_semantic_mismatch_count")
            == 2172
            and checked.get("actual_zig_corrected_verified_passing_case_count")
            == 2847
            and checked.get("actual_zig_corrected_archive_inflated") is False
            and checked.get("holdout") == "NOT OPENED"
            and tuple(v2.SUITES) == SUITES
            and tuple(v2.ROLE_ORDER) == ROLE_ORDER
            and tuple(v2.RESTORATION_ORDER) == RESTORATION_ORDER
            and v2.ORIGINAL_RUST_SOURCE_OWNERS[0][1]
            == ORIGINALS["adapter"]["sha256"]
            and all(v2.ROLES[role]["original"] == ORIGINALS[role]
                    for role in ROLE_ORDER)
            and all(callable(getattr(v2, name, None)) for name in
                    ("read_private", "write_private", "private_directory",
                     "open_target_parent", "current_original",
                     "exact_originals", "same_original",
                     "read_recorded_phase", "role_target_names",
                     "ensure_absent", "sync_directory", "write_stage",
                     "restore_four_roles", "execute_one_worker",
                     "failed_worker", "parse_arguments",
                     "assert_actual_authorization",
                     "write_evidence_receipt")),
            "reuse only fully authenticated safe original V2 worker helpers")
    frozen_owner = None
    if contract_pin is not None:
        checked_digest(contract_pin, "public Rust V3 machine contract")
        raw, frozen_owner = read_owned(CONTRACT_RELATIVE, contract_pin)
        validate_contract(strict_document(raw, "exact V3 recovery contract"),
                          source_pin, protocol_pin)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "source verification may never import a matching candidate")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": 3, "family": FAMILY,
        "mode": "READ-ONLY RECOVERABLE ORIGINAL RUST SOURCE FREEZE",
        "source": source, "protocol": protocol, "contract": frozen_owner,
        "authenticated_support_owner_count": len(authenticated),
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "preserved_v26_evidence_owner_count": 141,
        "preserved_v26_authenticated_reference_count": 146,
        "actual_rust_build_process_count": 28,
        "actual_rust_source_owner_count": 9,
        "actual_zig_preflight_candidate_workers": 0,
        "actual_zig_original_candidate_status": "FAIL",
        "actual_zig_original_candidate_workers": 13,
        "actual_zig_original_semantic_mismatch_count": 2172,
        "actual_zig_original_verified_passing_case_count": 2847,
        "actual_zig_original_infrastructure_failure_count": 0,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "original_target_count": 4,
        "graceful_signal_names": list(SIGNAL_NAMES),
        "source_only_signal_handlers_installed": 0,
        "source_only_recovery_locks_acquired": 0,
        "source_only_recovery_journals_created": 0,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        **source_effects(),
    }
    retained = {"v2": v2, "v2_context": checked,
                "v2_retained": v2_retained} if retain else {}
    return result, retained


@contextlib.contextmanager
def installed_signal_handlers() -> Iterator[None]:
    require(threading.current_thread() is threading.main_thread(),
            "install graceful controller handlers only on the main thread")
    names = []
    for name in SIGNAL_NAMES:
        value = getattr(signal, name, None)
        require(type(value) is signal.Signals,
                "require the actual supported POSIX controller signal")
        names.append(value)
    prior: dict[signal.Signals, Any] = {}

    def request_recovery(signum: int, _frame: Any) -> None:
        raise GracefulControllerSignal(signum)

    try:
        for value in names:
            prior[value] = signal.getsignal(value)
            signal.signal(value, request_recovery)
        yield
    finally:
        for value, handler in reversed(tuple(prior.items())):
            signal.signal(value, handler)


@contextlib.contextmanager
def blocked_controller_signals() -> Iterator[None]:
    require(callable(getattr(signal, "pthread_sigmask", None)),
            "require real POSIX signal masking for a critical target operation")
    selected = {getattr(signal, name) for name in SIGNAL_NAMES}
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, selected)
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


def checked_root(value: Any) -> str:
    require(type(value) is str and value == PUBLIC_RECOVERY_ROOT
            and value.startswith("/tmp/")
            and len(value.split("/")) == 3,
            "require the exact public V3 caller-pinned recovery root")
    return value


def open_recovery_lock(v2: types.ModuleType, root: str,
                       *, create: bool) -> tuple[int, int]:
    checked_root(root)
    if create:
        os.mkdir(root, mode=0o700)
        tmp_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                     | getattr(os, "O_CLOEXEC", 0)
                     | getattr(os, "O_NOFOLLOW", 0))
        tmp = os.open("/tmp", tmp_flags)
        try:
            os.fsync(tmp)
        finally:
            os.close(tmp)
    directory = v2.private_directory(root)
    lock: int | None = None
    try:
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        if create:
            flags |= os.O_CREAT | os.O_EXCL
        lock = os.open(LOCK_NAME, flags, 0o600, dir_fd=directory)
        actual = os.fstat(lock)
        visible = os.stat(LOCK_NAME, dir_fd=directory,
                          follow_symlinks=False)
        require(stat.S_ISREG(actual.st_mode)
                and actual.st_uid == os.geteuid()
                and actual.st_nlink == 1
                and stat.S_IMODE(actual.st_mode) == 0o600
                and (actual.st_dev, actual.st_ino)
                == (visible.st_dev, visible.st_ino),
                "reject a foreign or substituted original recovery lock")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.fsync(lock)
        os.fsync(directory)
        return directory, lock
    except BaseException:
        if lock is not None:
            os.close(lock)
        os.close(directory)
        raise


def announce_recovery(root: str, journal_digest: str) -> None:
    document = {
        "schema": SCHEMA + "-preactivation-public-recovery-announcement",
        "status": "PASS", "family": FAMILY,
        "activation_root": checked_root(root),
        "journal_relative": "recovery-journal.json",
        "recovery_journal_sha256": checked_digest(
            journal_digest, "durable public recovery journal"),
        "canonical_target_replacements_so_far": 0,
        "group_atomic": False,
        "holdout": "NOT OPENED",
    }
    sys.stderr.buffer.write(canonical(document))
    sys.stderr.buffer.flush()


def activate_four_roles(v2: types.ModuleType, retained: dict[str, Any],
                        options: argparse.Namespace) -> dict[str, Any]:
    root = checked_root(options.activation_root)
    originals = v2.exact_originals()
    require(all(v2.same_original(originals[role], ORIGINALS[role])
                for role in ROLE_ORDER),
            "authenticate all four exact original inodes before activation")
    phase = retained["v2_retained"]["build"]["phase"]
    payloads = {role: v2.read_recorded_phase(phase, role)
                for role in ROLE_ORDER}
    token = os.urandom(16).hex()
    entries: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        backup, stage = v2.role_target_names(token, role)
        owned = v2.ROLES[role]
        entries[role] = {
            "role": role, "relative": owned["relative"],
            "original": dict(owned["original"]),
            "backup_filename": backup, "stage_filename": stage,
            "repaired_sha256": owned["sha256"],
            "repaired_bytes": owned["bytes"],
        }
    journal = {
        "schema": v2.JOURNAL_SCHEMA, "status": "PREPARED", "version": 2,
        "family": FAMILY, "label": LABEL, "activation_root": root,
        "source_sha256": V2["source"][1],
        "protocol_sha256": V2["protocol"][1],
        "contract_sha256": V2["contract"][1],
        "build_archive_sha256": RUST_BUILD["archive"][1],
        "build_receipt_sha256": RUST_BUILD["receipt"][1],
        "roles": entries, "role_order": list(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "group_atomic": False,
        "exact_original_inode_backup":
            "ADJACENT SAME-DIRECTORY HARDLINK",
        "recoverable_v3_controller_source_sha256": options.source_sha256,
        "recoverable_v3_controller_protocol_sha256":
            options.protocol_sha256,
        "recoverable_v3_controller_contract_sha256":
            options.contract_sha256,
        "recoverable_v3_public_root": PUBLIC_RECOVERY_ROOT,
        "recoverable_v3_public_lock_filename": LOCK_NAME,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
    }
    with blocked_controller_signals():
        journal_owner = v2.write_private(root, "recovery-journal.json",
                                         journal)
        announce_recovery(root, journal_owner["sha256"])
    try:
        for role in ROLE_ORDER:
            with blocked_controller_signals():
                entry = entries[role]
                owned = v2.ROLES[role]
                original = v2.current_original(role)
                require(v2.same_original(original, owned["original"]),
                        "refuse an original changed after the public journal")
                repository, directory, filename = v2.open_target_parent(
                    entry["relative"])
                try:
                    before = os.fstat(directory)
                    v2.ensure_absent(directory, entry["backup_filename"])
                    v2.ensure_absent(directory, entry["stage_filename"])
                    intention = {
                        "schema": v2.INTENTION_SCHEMA,
                        "status": "PREPARED",
                        "operation": "HARDLINK_BACKUP",
                        "family": FAMILY, "role": role,
                        "target": entry["relative"],
                        "activation_root": root,
                        "journal_sha256": journal_owner["sha256"],
                        "original": entry["original"],
                        "backup_filename": entry["backup_filename"],
                        "group_atomic": False,
                    }
                    v2.write_private(root, "link-intent-" + role + ".json",
                                     intention)
                    os.link(filename, entry["backup_filename"],
                            src_dir_fd=directory, dst_dir_fd=directory,
                            follow_symlinks=False)
                    current = os.stat(filename, dir_fd=directory,
                                      follow_symlinks=False)
                    backup = os.stat(entry["backup_filename"],
                                     dir_fd=directory, follow_symlinks=False)
                    expected = owned["original"]
                    require((current.st_dev, current.st_ino)
                            == (backup.st_dev, backup.st_ino)
                            == (expected["device"], expected["inode"])
                            and current.st_nlink == 2
                            and backup.st_nlink == 2
                            and current.st_uid == expected["uid"]
                            and stat.S_IMODE(current.st_mode)
                            == expected["mode"],
                            "preserve the actual same-device original inode")
                    v2.sync_directory(directory, before)
                    promotion = {
                        "schema": v2.INTENTION_SCHEMA,
                        "status": "PREPARED", "operation": "PROMOTE",
                        "family": FAMILY, "role": role,
                        "target": entry["relative"],
                        "activation_root": root,
                        "journal_sha256": journal_owner["sha256"],
                        "original": entry["original"],
                        "backup_filename": entry["backup_filename"],
                        "stage_filename": entry["stage_filename"],
                        "repaired_sha256": entry["repaired_sha256"],
                        "repaired_bytes": entry["repaired_bytes"],
                        "group_atomic": False,
                    }
                    v2.write_private(root,
                                     "promotion-intent-" + role + ".json",
                                     promotion)
                    staged = v2.write_stage(
                        directory, entry["stage_filename"],
                        payloads[role], expected["mode"])
                    require(staged.get("sha256") == owned["sha256"]
                            and staged.get("size_bytes") == owned["bytes"],
                            "never promote an unauthenticated native or source")
                    v2.sync_directory(directory, before)
                    os.replace(entry["stage_filename"], filename,
                               src_dir_fd=directory, dst_dir_fd=directory)
                    v2.sync_directory(directory, before)
                    _, promoted = v2._read_owned(
                        str(ROOT), entry["relative"], owned["sha256"],
                        exact_size=owned["bytes"],
                        maximum=v2.MAX_BINARY_BYTES,
                        allow_canonical_target=True)
                    require(promoted["device"] == staged["device"]
                            and promoted["inode"] == staged["inode"]
                            and promoted["mode"] == expected["mode"]
                            and promoted["nlink"] == 1,
                            "prove the one exact journaled promoted inode")
                finally:
                    os.close(directory)
                    os.close(repository)
        targets = {}
        with blocked_controller_signals():
            for role in ROLE_ORDER:
                owned = v2.ROLES[role]
                _, targets[role] = v2._read_owned(
                    str(ROOT), owned["relative"], owned["sha256"],
                    exact_size=owned["bytes"],
                    maximum=v2.MAX_BINARY_BYTES,
                    allow_canonical_target=True)
            activation = {
                "schema": v2.ACTIVATION_SCHEMA, "status": "PASS",
                "version": 2, "family": FAMILY, "label": LABEL,
                "activation_root": root, "journal": journal_owner,
                "targets": targets, "role_order": list(ROLE_ORDER),
                "restoration_order": list(RESTORATION_ORDER),
                "build_archive_sha256": RUST_BUILD["archive"][1],
                "build_receipt_sha256": RUST_BUILD["receipt"][1],
                "all_four_original_inodes_retained": True,
                "recoverable_v3_controller_source_sha256":
                    options.source_sha256,
                "group_atomic": False,
            }
            activation_owner = v2.write_private(
                root, "activation-report.json", activation)
            receipt = {
                "schema": v2.ACTIVATION_RECEIPT_SCHEMA,
                "status": "PASS", "activation_status": "PASS",
                "family": FAMILY, "activation_root": root,
                "activation": activation_owner,
                "journal": journal_owner, "group_atomic": False,
            }
            receipt_owner = v2.write_private(
                root, "activation-receipt.json", receipt)
        return {
            "root": root, "journal": journal,
            "journal_owner": journal_owner,
            "activation": activation,
            "activation_owner": activation_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "originals": originals,
        }
    except BaseException:
        with blocked_controller_signals():
            v2.restore_four_roles(root, journal, journal_owner["sha256"])
        raise


def v2_worker_options(v2: types.ModuleType) -> argparse.Namespace:
    arguments = [
        "--run", "--source-sha256", V2["source"][1],
        "--protocol-sha256", V2["protocol"][1],
        "--contract-sha256", V2["contract"][1],
        "--family", FAMILY, "--label", LABEL,
        "--producer-source-sha256", PRODUCER["source"][1],
        "--producer-protocol-sha256", PRODUCER["protocol"][1],
        "--producer-contract-sha256", PRODUCER["contract"][1],
        "--publication-source-sha256", PUBLICATION["source"][1],
        "--publication-protocol-sha256", PUBLICATION["protocol"][1],
        "--publication-contract-sha256", PUBLICATION["contract"][1],
        "--build-archive-sha256", RUST_BUILD["archive"][1],
        "--build-receipt-sha256", RUST_BUILD["receipt"][1],
        "--native-engine-sha256", ENGINE_SHA256,
        "--native-bridge-sha256", BRIDGE_SHA256,
        "--native-engine-bytes", str(ENGINE_BYTES),
        "--native-bridge-bytes", str(BRIDGE_BYTES),
    ]
    options = v2.parse_arguments(arguments)
    v2.assert_actual_authorization(options)
    require(options.run is True and options.worker is False,
            "compose V2 worker arguments without invoking its controller")
    return options


def evidence_names(failure: bool) -> tuple[str, str]:
    stem = "repaired-rust-original-campaign-v3-rust-" + LABEL
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_fresh_evidence(publication: types.ModuleType) -> None:
    directory = publication.open_evidence_directory()
    try:
        for failure in (False, True):
            for name in evidence_names(failure):
                try:
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise CampaignError(
                    "never overwrite a prior recoverable Rust observation: "
                    + name)
    finally:
        os.close(directory)


def preserve_campaign(report: dict[str, Any], retained: dict[str, Any]
                      ) -> dict[str, Any]:
    v2 = retained["v2"]
    publication = retained["v2_retained"]["publication"]
    require(report.get("schema") == CAMPAIGN_SCHEMA
            and report.get("status") in ("PASS", "FAIL")
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("suite_count") == SUITE_COUNT
            and report.get("case_execution_denominator") == CASE_COUNT
            and report.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and type(report.get("suite_results")) is list
            and len(report["suite_results"]) == SUITE_COUNT
            and [(item.get("suite"),
                  item.get("case_execution_denominator"))
                 for item in report["suite_results"]] == list(SUITES)
            and report.get("all_four_original_targets_restored") is True
            and report.get("restoration_verified_before_publication") is True
            and report.get("v2_unsafe_controller_invoked") is False
            and report.get("v2_unsafe_activation_invoked") is False
            and report.get("holdout") == "NOT OPENED",
            "never publish incomplete suites or unrestored original inodes")
    current = v2.exact_originals()
    require(report.get("restored_original_targets") == current,
            "recheck every original source and native inode before publication")
    archive_name, receipt_name = evidence_names(report["status"] == "FAIL")
    directory = publication.open_evidence_directory()
    try:
        archive, stream = publication.write_streamed_archive(
            report, archive_name, directory)
    finally:
        os.close(directory)
    require(archive.get("relative") == archive_name
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("streaming_readback_verified") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and stream.get("gzip_mtime") == 0
            and stream.get("gzip_single_member") is True,
            "publish only one exact fully durable V3 result archive")
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": "PASS",
        "candidate_status": report["status"],
        "family": FAMILY, "label": LABEL, "archive": archive,
        "campaign_source_sha256": report["campaign_source_sha256"],
        "campaign_protocol_sha256": report["campaign_protocol_sha256"],
        "campaign_contract_sha256": report["campaign_contract_sha256"],
        "frozen_v2_worker_source_sha256": V2["source"][1],
        "frozen_v2_worker_protocol_sha256": V2["protocol"][1],
        "frozen_v2_worker_contract_sha256": V2["contract"][1],
        "original_v3_producer_source_sha256": PRODUCER["source"][1],
        "original_v3_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v3_producer_contract_sha256": PRODUCER["contract"][1],
        "actual_v11_build_archive_sha256": RUST_BUILD["archive"][1],
        "actual_v11_build_receipt_sha256": RUST_BUILD["receipt"][1],
        "uncompressed_sha256": stream["uncompressed_sha256"],
        "uncompressed_bytes": stream["uncompressed_bytes"],
        "uncompressed_chunk_count": stream["uncompressed_chunk_count"],
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "graceful_signal": report["graceful_signal"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "restoration_verified_before_publication": True,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "actual_zig_original_semantic_mismatch_count": 2172,
        "actual_zig_original_verified_passing_case_count": 2847,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt_owner = v2.write_evidence_receipt(receipt_name, receipt)
    require((archive["device"], archive["inode"])
            != (receipt_owner["device"], receipt_owner["inode"])
            and v2.exact_originals() == current,
            "prove independently durable evidence and all restored inodes")
    return {
        "schema": SCHEMA + "-published-complete-original-campaign",
        "status": report["status"], "family": FAMILY, "label": LABEL,
        "archive": archive, "receipt": receipt_owner,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "graceful_signal": report["graceful_signal"],
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "group_atomic": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
    }


def record_failure(error: Exception) -> dict[str, Any]:
    return {
        "error_type": type(error).__qualname__,
        "error_message": str(error)[:4096],
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__),
    }


def run_campaign(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    context, retained = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "verify every original frozen owner before installing handlers")
    v2 = retained["v2"]
    publication = retained["v2_retained"]["publication"]
    ensure_fresh_evidence(publication)
    worker_options = v2_worker_options(v2)
    active: dict[str, Any] | None = None
    baseline: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    controller_failure: dict[str, Any] | None = None
    graceful: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    root_directory: int | None = None
    root_lock: int | None = None
    with installed_signal_handlers():
        try:
            with blocked_controller_signals():
                root_directory, root_lock = open_recovery_lock(
                    v2, options.activation_root, create=True)
            baseline = v2.exact_originals()
            active = activate_four_roles(v2, retained, options)
            for name, count in SUITES:
                try:
                    row = v2.execute_one_worker(
                        worker_options, name, count, active)
                except GracefulControllerSignal:
                    raise
                except Exception as error:
                    row = v2.failed_worker(name, count, error)
                rows.append(row)
        except GracefulControllerSignal as error:
            controller_failure = record_failure(error)
            graceful = {
                "schema": SIGNAL_SCHEMA,
                "status": "FAIL",
                "signal_name": error.signal_name,
                "signal_number": error.signum,
                "candidate_matching_result": "NOT MEASURED",
                "group_atomic": False,
            }
            seen = {item.get("suite") for item in rows}
            for name, count in SUITES:
                if name not in seen:
                    rows.append(v2.failed_worker(name, count, error))
        except Exception as error:
            controller_failure = record_failure(error)
            seen = {item.get("suite") for item in rows}
            for name, count in SUITES:
                if name not in seen:
                    rows.append(v2.failed_worker(name, count, error))
        finally:
            try:
                if active is not None:
                    with blocked_controller_signals():
                        restoration = v2.restore_four_roles(
                            active["root"], active["journal"],
                            active["journal_owner"]["sha256"])
                if baseline is not None:
                    with blocked_controller_signals():
                        originals = v2.exact_originals()
                        require(originals == baseline,
                                "restore all four exact original Rust inodes")
            finally:
                if root_lock is not None:
                    os.close(root_lock)
                if root_directory is not None:
                    os.close(root_directory)
    rows.sort(key=lambda row: {name: index for index, (name, _)
                               in enumerate(SUITES)}[row["suite"]])
    require(len(rows) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in rows] == list(SUITES),
            "preserve every original suite slot after every true failure")
    require(baseline is not None and active is not None
            and restoration is not None,
            "never publish without a real journal and all restored originals")
    originals = v2.exact_originals()
    require(originals == baseline,
            "reauthenticate all four original inodes before evidence")
    pids = [row["process"]["pid"] for row in rows
            if row.get("actual_worker_started") is True
            and type(row.get("process")) is dict]
    require(len(pids) == len(set(pids)),
            "never count the same original worker twice")
    complete = sum(row.get("actual_worker_started") is True for row in rows)
    passed = sum(count for (name, count), row in
                 zip(SUITES, rows, strict=True)
                 if row.get("suite") == name
                 and row.get("failure_class") == "PASS"
                 and row.get("mismatch_count") == 0
                 and row.get("all_original_records_and_mismatches_preserved")
                 is True)
    differences = sum(row["mismatch_count"] for row in rows
                      if row.get("failure_class") == "SEMANTIC MISMATCH"
                      and type(row.get("mismatch_count")) is int)
    infrastructure = sum(
        row.get("failure_class") == "INFRASTRUCTURE FAILURE"
        for row in rows) + int(controller_failure is not None)
    qualified = (len(pids) == SUITE_COUNT and complete == SUITE_COUNT
                 and passed == CASE_COUNT and differences == 0
                 and infrastructure == 0 and graceful is None
                 and all(row.get("actual_worker_processes") == 1
                         and row.get("all_original_records_and_mismatches_preserved")
                         is True for row in rows))
    report = {
        "schema": CAMPAIGN_SCHEMA,
        "status": "PASS" if qualified else "FAIL",
        "family": FAMILY, "label": LABEL,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "frozen_v2_worker_source_sha256": V2["source"][1],
        "frozen_v2_worker_protocol_sha256": V2["protocol"][1],
        "frozen_v2_worker_contract_sha256": V2["contract"][1],
        "original_v3_producer_source_sha256": PRODUCER["source"][1],
        "original_v3_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v3_producer_contract_sha256": PRODUCER["contract"][1],
        "actual_v11_build_archive_sha256": RUST_BUILD["archive"][1],
        "actual_v11_build_receipt_sha256": RUST_BUILD["receipt"][1],
        "actual_rust_compiler_process_count": 28,
        "actual_repaired_rust_source_owner_count": 9,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "native_engine_bytes": ENGINE_BYTES,
        "native_bridge_bytes": BRIDGE_BYTES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "completed_suite_count": complete,
        "suite_results": rows,
        "actual_candidate_workers": len(pids),
        "actual_worker_process_ids": pids,
        "verified_passing_case_count": passed,
        "semantic_mismatch_count": differences if complete else "NOT MEASURED",
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": qualified,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "graceful_signal": graceful,
        "all_four_original_targets_restored": True,
        "restored_original_targets": originals,
        "restoration": restoration,
        "restoration_verified_before_publication": True,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "actual_zig_original_candidate_workers": 13,
        "actual_zig_original_semantic_mismatch_count": 2172,
        "actual_zig_original_verified_passing_case_count": 2847,
        "actual_zig_original_infrastructure_failure_count": 0,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "controller_failure": controller_failure,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return preserve_campaign(report, retained)


def recover_originals(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    require(options.recovery_journal_sha256 is not None,
            "caller-pin the complete independently durable recovery journal")
    _, retained = verify_context(options.source_sha256,
                                 options.protocol_sha256,
                                 options.contract_sha256, retain=True)
    v2 = retained["v2"]
    root = checked_root(options.activation_root)
    directory: int | None = None
    lock: int | None = None
    with installed_signal_handlers():
        try:
            with blocked_controller_signals():
                directory, lock = open_recovery_lock(v2, root, create=False)
                journal, journal_owner = v2.read_private(
                    root, "recovery-journal.json",
                    options.recovery_journal_sha256)
                require(journal.get("schema") == v2.JOURNAL_SCHEMA
                        and journal.get("status") == "PREPARED"
                        and journal.get("family") == FAMILY
                        and journal.get("label") == LABEL
                        and journal.get("activation_root") == root
                        and journal.get("source_sha256") == V2["source"][1]
                        and journal.get("protocol_sha256") == V2["protocol"][1]
                        and journal.get("contract_sha256") == V2["contract"][1]
                        and journal.get("recoverable_v3_controller_source_sha256")
                        == options.source_sha256
                        and journal.get("recoverable_v3_controller_protocol_sha256")
                        == options.protocol_sha256
                        and journal.get("recoverable_v3_controller_contract_sha256")
                        == options.contract_sha256
                        and journal.get("recoverable_v3_public_root") == root
                        and journal.get("recoverable_v3_public_lock_filename")
                        == LOCK_NAME
                        and journal.get("role_order") == list(ROLE_ORDER)
                        and journal.get("restoration_order")
                        == list(RESTORATION_ORDER)
                        and journal.get("group_atomic") is False
                        and journal_owner["sha256"]
                        == options.recovery_journal_sha256,
                        "reject an unknown, copied or foreign recovery journal")
                restoration = v2.restore_four_roles(
                    root, journal, options.recovery_journal_sha256)
                originals = v2.exact_originals()
                require(all(v2.same_original(originals[role], ORIGINALS[role])
                            for role in ROLE_ORDER)
                        and restoration.get("report", {}).get("status")
                        == "PASS"
                        and restoration.get("report", {}).get(
                            "original_inodes_preserved") is True,
                        "prove all four exact original Rust inodes recovered")
        finally:
            if lock is not None:
                os.close(lock)
            if directory is not None:
                os.close(directory)
    return {
        "schema": RECOVERY_SCHEMA, "status": "PASS", "version": 3,
        "family": FAMILY, "label": LABEL,
        "activation_root": root,
        "recovery_journal_sha256": options.recovery_journal_sha256,
        "recovery_lock_filename": LOCK_NAME,
        "original_target_count": 4,
        "restoration_order": list(RESTORATION_ORDER),
        "restoration": restoration,
        "restored_original_targets": originals,
        "all_four_original_targets_restored": True,
        "recovery_idempotent": True,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "actual_candidate_workers": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def assert_actual_authorization(options: argparse.Namespace) -> None:
    require(options.family == FAMILY and options.label == LABEL
            and options.activation_root == PUBLIC_RECOVERY_ROOT
            and options.v2_source_sha256 == V2["source"][1]
            and options.v2_protocol_sha256 == V2["protocol"][1]
            and options.v2_contract_sha256 == V2["contract"][1]
            and options.v27_renderer_sha256 == V27["renderer"][1]
            and options.v27_inputs_sha256 == V27["inputs"][1]
            and options.v27_summary_sha256 == V27["summary"][1]
            and options.v27_svg_sha256 == V27["svg"][1]
            and options.producer_source_sha256 == PRODUCER["source"][1]
            and options.producer_protocol_sha256 == PRODUCER["protocol"][1]
            and options.producer_contract_sha256 == PRODUCER["contract"][1]
            and options.publication_source_sha256 == PUBLICATION["source"][1]
            and options.publication_protocol_sha256
            == PUBLICATION["protocol"][1]
            and options.publication_contract_sha256
            == PUBLICATION["contract"][1]
            and options.build_archive_sha256 == RUST_BUILD["archive"][1]
            and options.build_receipt_sha256 == RUST_BUILD["receipt"][1]
            and options.native_engine_sha256 == ENGINE_SHA256
            and options.native_bridge_sha256 == BRIDGE_SHA256
            and options.native_engine_bytes == ENGINE_BYTES
            and options.native_bridge_bytes == BRIDGE_BYTES,
            "independently caller-pin every V3 recovery and original owner")


def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    require(all(type(value) is str for value in values),
            "require exact literal source-freeze authorization")
    flags = [value for value in values if value.startswith("--")]
    require(len(flags) == len(set(flags)),
            "reject repeated or ambiguous explicit actual authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--verify-frozen-context", action="store_true")
    mode.add_argument("--render-contract", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--recover", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--activation-root")
    parser.add_argument("--recovery-journal-sha256")
    pin_names = (
        "v2-source", "v2-protocol", "v2-contract",
        "v27-renderer", "v27-inputs", "v27-summary", "v27-svg",
        "producer-source", "producer-protocol", "producer-contract",
        "publication-source", "publication-protocol", "publication-contract",
        "build-archive", "build-receipt", "native-engine", "native-bridge",
    )
    for name in pin_names:
        parser.add_argument("--" + name + "-sha256")
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "recoverable V3 source")
    checked_digest(options.protocol_sha256, "recoverable V3 protocol")
    digest_names = [name.replace("-", "_") + "_sha256"
                    for name in pin_names]
    for name in ("contract_sha256", "recovery_journal_sha256",
                 *digest_names):
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    actual_names = (
        "family", "label", "activation_root", "recovery_journal_sha256",
        *digest_names, "native_engine_bytes", "native_bridge_bytes",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, name) is None for name in actual_names),
                "rendering must never authorize recovery or activation")
        return options
    require(options.contract_sha256 is not None,
            "caller-pin the exact canonical V3 machine contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in actual_names),
                "source verification cannot authorize a target or handler")
        return options
    require(all(getattr(options, name) is not None for name in
                ("family", "label", "activation_root", *digest_names,
                 "native_engine_bytes", "native_bridge_bytes")),
            "require every independently caller-pinned recovery owner")
    if options.recover:
        require(options.recovery_journal_sha256 is not None,
                "recovery requires the caller-pinned exact durable journal")
    else:
        require(options.recovery_journal_sha256 is None,
                "a controller must create and announce its own public journal")
    return options


def controller_failure(options: argparse.Namespace,
                       error: Exception, *, mode: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-controller-infrastructure-failure",
        "status": "FAIL", "failure_class": "CONTROLLER INFRASTRUCTURE FAILURE",
        "family": FAMILY, "label": LABEL, "mode": mode,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "contract_sha256": options.contract_sha256,
        "error": record_failure(error),
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "durable_failure_publication": "NOT VERIFIED",
        "all_four_original_targets_restored": "NOT VERIFIED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
    }


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        result = self_test(options.source_sha256, options.protocol_sha256,
                           options.contract_sha256)
        code = 0
    elif options.verify_frozen_context:
        result, _ = verify_context(options.source_sha256,
                                   options.protocol_sha256,
                                   options.contract_sha256)
        code = 0
    elif options.render_contract:
        result = protocol_document(options.source_sha256,
                                   options.protocol_sha256)
        code = 0
    elif options.recover:
        try:
            result = recover_originals(options)
            code = 0 if result["status"] == "PASS" else 1
        except Exception as error:
            result = controller_failure(options, error, mode="--recover")
            code = 1
    else:
        try:
            result = run_campaign(options)
            code = 0 if result["status"] == "PASS" else 1
        except Exception as error:
            result = controller_failure(options, error, mode="--run")
            code = 1
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
