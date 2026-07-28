#!/usr/bin/env python3
"""Run the frozen original CPython P0 suites against the first-party C15 build.

The original candidate adapter and original C source are never promoted.  The
only mutable public candidate owner is its native shared-object inode.  Source
inspection modes do not inspect that inode, a candidate source, or a build root.
"""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import collections
import contextlib
import copy
import ctypes
import dataclasses
import fcntl
import gzip
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
from typing import Any, Iterator, Mapping, NoReturn


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "rebar-owned-repaired-c-original-campaign-v4"
FAMILY = "c"
LABEL = "phase2-v15-c-pickle-original-p0"
SOURCE_PATH = "tools/run_owned_repaired_c_original_campaign_v4.py"
PROTOCOL_PATH = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V4.md"
CONTRACT_PATH = "oracle/phase2/repaired-c-original-campaign-v4.json"
PUBLIC_ROOT = "/tmp/rebar-phase2-repaired-c-original-campaign-v4-phase2-v15-c-pickle-original-p0"
BUILD_ROOT = "/tmp/rebar-phase2-native-build-v8-c-6khmorpw"
NATIVE_NAME = "_vm_native.cpython-314-x86_64-linux-gnu.so"
NATIVE_PATH = "candidates/" + NATIVE_NAME
STAGE_NAME = ".rebar-repaired-c-v4-stage.so"
BACKUP_NAME = ".rebar-repaired-c-v4-original.so"
JOURNAL_NAME = "recovery-journal-v4.json"
REPORT_NAME = "activation-report-v4.json"
RECEIPT_NAME = "activation-receipt-v4.json"
PROMOTION_INTENT_NAME = "promotion-intent-v4.json"
STAGE_INTENT_NAME = "stage-intent-v4.json"
MAX_OWNED_BYTES = 32 * 1024 * 1024
MAX_WORKER_STDOUT = 64 * 1024 * 1024
MAX_WORKER_STDERR = 4 * 1024 * 1024


@dataclasses.dataclass(frozen=True, slots=True)
class Owner:
    relative_path: str
    sha256: str
    size: int


GOAL_OWNER = Owner(
    "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756
)
P0_OWNER = Owner(
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
PRODUCER_OWNERS = (
    Owner("tools/run_owned_six_family_original_p0_producer_v3.py", "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555),
    Owner("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md", "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76", 5522),
    Owner("oracle/phase2/six-family-p0-producer-v3.json", "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1", 26909),
)
PUBLICATION_OWNERS = (
    Owner("tools/run_owned_six_family_original_p0_campaign_v2.py", "6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1", 101836),
    Owner("oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md", "e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e", 4995),
    Owner("oracle/phase2/six-family-p0-campaign-v2.json", "e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7", 21314),
)
C15_OWNERS = (
    Owner("tools/reproduce_owned_c_pickle_source_build_v15.py", "91bc1985ac1edad757a3b027840db3f08aa97a781df1542e33b39d39f04aa7d8", 93667),
    Owner("oracle/phase2/C-PICKLE-SOURCE-BUILD-V15.md", "fab2219a4c4a0cf78acfe8adbb039aba591a450409d9cc75347d552d9d0e4727", 2803),
    Owner("oracle/phase2/c-pickle-source-build-v15.json", "7fb1409eb228deb034626efb9b5bb1781c1cd139343d18e87acdac6deab97285", 15255),
    Owner("oracle/phase2/evidence/native-source-build-v15-c-phase2-v15-c-pickle-original-p0.json.gz", "7e95decc5937b76b2f1aa86706663a57edcea8d3a705ad9b3710c4ec2b61a4de", 41716),
    Owner("oracle/phase2/evidence/native-source-build-v15-c-phase2-v15-c-pickle-original-p0-publication-receipt.json", "ad196290f8f08b1547ffefc02bd1cdaff52557f792b8a32ea93c67f6ee857643", 4052),
)
OVERVIEW_OWNERS = (
    Owner("tools/render_candidate_current_overview_v29.py", "788ea53f59b77a1670d4617ab1dde21aef0a5b5e2528a48a46b0e2315ac03c27", 65559),
    Owner("docs/evidence/candidate-current-overview-v29.inputs.json", "f6d306dfc08b89604d9d89896a899049c1ba03b0ebfe674ebba036cc80898894", 52975),
    Owner("docs/evidence/candidate-current-overview-v29.json", "48eaf71facc4e7bba79e6b8c6c2ad45ed56eaeecf553afd82e8fe402c0aa6160", 260569),
    Owner("docs/evidence/candidate-current-overview-v29.svg", "58725ecef05a1adf01d6c354512bf7101c212bf87f63c40cfdd9e225267f91ff", 17253),
)
HISTORICAL_OWNERS = (
    Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures.json.gz", "3ac7736c127d13d3fad579c4ab9974c6a83612b4253f7921ed3e44269f3a82ad", 5710284),
    Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures-publication-receipt.json", "97f0b8c47823b20cd04740e3fe2883189cc648d49769015800c0998e6698c281", 4447),
    Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz", "583d63c92240cec78c861893407003466a5f754b099719aabfc8eaf4f14fbbf8", 5870948),
    Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba", 4534),
    Owner("oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz", "1cb38eb48a2d3305ea98d5103a27ce6ae758137168f68df07a408dec3d055a37", 3711),
    Owner("oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23", 1992),
)
ORIGINAL_ADAPTER = Owner("candidates/vm_candidate.py", "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707)
ORIGINAL_C_SOURCE = Owner("candidates/_vm_native.c", "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185)
ORIGINAL_NATIVE_SHA256 = "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
ORIGINAL_NATIVE_BYTES = 149976
ORIGINAL_NATIVE_DEVICE = 2064
ORIGINAL_NATIVE_INODE = 430300
ORIGINAL_NATIVE_MODE = 0o755
ORIGINAL_NATIVE_UID = 1000
C15_NATIVE_SHA256 = "aed6e9c2fbe31ee3798c74bc6fe896494f1a3bfed41ff25dcfef6905e7b8e610"
C15_NATIVE_BYTES = 163176
C15_PHASE_DEVICE = 2049
C15_PHASE_NATIVE_INODE = 10601081
C15_PHASE_NATIVE_MODE = 0o700
C15_REPAIRED_SOURCE_SHA256 = "8b35fba5b565ae18c5b9c180bec1dfbfb46b75bf3db7421626da4a73cdda2b94"
C15_REPAIRED_SOURCE_BYTES = 219227
C15_REPAIRED_SOURCE_INODE = 10601075
C15_ARCHIVE_DECOMPRESSED_SHA256 = "55faf4490917b60c174fe120419f64fea2bc9171f4321f880bd89172b6b1693a"
C15_ARCHIVE_DECOMPRESSED_BYTES = 322399
ORACLE_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
ORACLE_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
P0_CASES = 31237
SUITE_COUNT = 13
PRIVATE_WAIVERS = 13
CURRENT_OVERVIEW_OWNERS = 147
CURRENT_OVERVIEW_REFERENCES = 152
SUITES: tuple[tuple[str, int], ...] = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
SIGNAL_NAMES = ("SIGINT", "SIGTERM", "SIGHUP")


class GateError(Exception):
    """A frozen owner, safety gate, or truthful publication did not verify."""


class ControllerSignal(BaseException):
    """An external termination request requiring original-inode recovery."""

    def __init__(self, signum: int) -> None:
        self.signum = signum
        try:
            self.signal_name = signal.Signals(signum).name
        except ValueError:
            self.signal_name = "UNKNOWN"
        super().__init__("graceful controller interruption: " + self.signal_name)


def require(condition: object, message: str) -> None:
    if not condition:
        raise GateError(message)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


def parse_object(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeError, ValueError, TypeError) as exc:
        raise GateError(f"invalid {label}: {exc}") from exc
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def owner_dict(owner: Owner) -> dict[str, object]:
    return {"path": owner.relative_path, "sha256": owner.sha256, "bytes": owner.size}


def checked_digest(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64 and all(character in "0123456789abcdef" for character in value), "require an exact lowercase SHA-256 for " + label)
    return value


def checked_relative(value: object) -> str:
    require(type(value) is str and bool(value) and not value.startswith("/") and "\\" not in value and "\x00" not in value and all(part not in ("", ".", "..") for part in value.split("/")), "reject an escaped or ambiguous relative owner")
    return value


def checked_document_size(size: object, maximum: object = MAX_OWNED_BYTES) -> int:
    require(type(maximum) is int and 0 < maximum <= MAX_WORKER_STDOUT, "require a separately bounded authentic document limit")
    require(type(size) is int and 0 < size <= maximum, "reject a missing, negative, oversized, or falsely bounded document")
    return size


def strict_document(payload: bytes, label: str, *, maximum: int = MAX_OWNED_BYTES) -> dict[str, Any]:
    require(type(payload) is bytes, "reject non-byte document evidence: " + label)
    checked_document_size(len(payload), maximum)

    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(type(key) is str and key not in result, "reject duplicate fields in " + label)
            result[key] = value
        return result

    try:
        result = json.loads(payload.decode("utf-8", "strict"), object_pairs_hook=unique, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("reject nonfinite " + value)))
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise GateError("reject invalid document " + label) from exc
    require(type(result) is dict, "require a JSON object: " + label)
    return result


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6) and sys.flags.isolated == 1 and sys.dont_write_bytecode is True and os.path.abspath(sys.executable) == ORACLE_PYTHON, "require exact isolated stable CPython 3.14.6 with -I -B")


def read_owned(owner: Owner, *, root: Path = ROOT, allow_canonical_target: bool = False, expected_device: int | None = None, expected_inode: int | None = None, expected_mode: int | None = None, expected_nlink: int = 1) -> tuple[bytes, dict[str, Any]]:
    relative = checked_relative(owner.relative_path)
    checked_digest(owner.sha256, relative)
    require(type(owner.size) is int and 0 < owner.size <= MAX_OWNED_BYTES, "require a bounded exact owner size")
    require(root != ROOT or not relative.startswith("candidates/") or allow_canonical_target, "source-only verification cannot inspect a canonical candidate")
    require(root == ROOT or str(root) == BUILD_ROOT, "read only an explicitly caller-pinned actual build root")
    handles: list[int] = []
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories = flags | getattr(os, "O_DIRECTORY", 0)
    try:
        directory = os.open(str(root), directories)
        handles.append(directory)
        for component in relative.split("/")[:-1]:
            directory = os.open(component, directories, dir_fd=directory)
            handles.append(directory)
            require(stat.S_ISDIR(os.fstat(directory).st_mode), "reject a substituted owner directory")
        filename = relative.rsplit("/", 1)[-1]
        handle = os.open(filename, flags, dir_fd=directory)
        handles.append(handle)
        before = os.fstat(handle)
        visible = os.stat(filename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid() and before.st_nlink == expected_nlink and before.st_size == owner.size and (before.st_dev, before.st_ino, before.st_size) == (visible.st_dev, visible.st_ino, visible.st_size), "reject a substituted, linked, symlinked, truncated, or foreign owner: " + relative)
        require(expected_device is None or before.st_dev == expected_device, "reject a source on the wrong filesystem: " + relative)
        require(expected_inode is None or before.st_ino == expected_inode, "reject an unrecorded owner inode: " + relative)
        require(expected_mode is None or stat.S_IMODE(before.st_mode) == expected_mode, "reject an incorrect original or phase mode: " + relative)
        chunks: list[bytes] = []
        remaining = owner.size
        calculated = hashlib.sha256()
        while remaining:
            chunk = os.read(handle, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk), "reject a truncated owner: " + relative)
            chunks.append(chunk)
            calculated.update(chunk)
            remaining -= len(chunk)
        require(os.read(handle, 1) == b"", "reject extra owner bytes: " + relative)
        after = os.fstat(handle)
        named = os.stat(filename, dir_fd=directory, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_uid, after.st_nlink, after.st_mtime_ns, after.st_ctime_ns) and (after.st_dev, after.st_ino, after.st_size, after.st_uid, after.st_nlink) == (named.st_dev, named.st_ino, named.st_size, named.st_uid, named.st_nlink) and calculated.hexdigest() == owner.sha256, "reject an owner changed during full digest verification: " + relative)
        return b"".join(chunks), {"relative": relative, "path": str(root / relative), "sha256": owner.sha256, "bytes": owner.size, "size_bytes": owner.size, "device": before.st_dev, "inode": before.st_ino, "mode": stat.S_IMODE(before.st_mode), "uid": before.st_uid, "nlink": before.st_nlink}
    finally:
        for handle in reversed(handles):
            os.close(handle)


def mapped_owners(owners: tuple[Owner, ...]) -> list[dict[str, object]]:
    return [owner_dict(owner) for owner in owners]


def source_effects() -> dict[str, Any]:
    return {"canonical_target_reads": 0, "canonical_target_stats": 0, "canonical_source_reads": 0, "canonical_source_stats": 0, "canonical_target_links": 0, "canonical_target_replacements": 0, "actual_candidate_workers": 0, "actual_candidate_imports": 0, "actual_native_activations": 0, "actual_native_recoveries": 0, "actual_native_libraries_loaded": 0, "actual_subprocesses_started": 0, "actual_threads_started": 0, "actual_network_requests": 0, "actual_signal_handlers_installed": 0, "actual_signal_masks_installed": 0, "actual_recovery_locks_acquired": 0, "actual_private_directories_created": 0, "actual_recovery_journals_created": 0, "actual_build_root_opens": 0, "original_producer_legacy_controller_invoked": False, "publication_family_dispatch_invoked": False, "workspace_mutations": 0, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "uncompressed_rust_archive_opened": False, "uncompressed_rust_archive_bytes_read": 0, "uncompressed_zig_archive_opened": False, "uncompressed_zig_archive_bytes_read": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "winner_selected": False}


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "version 4 source")
    checked_digest(protocol_pin, "version 4 protocol")
    return {
        "schema": SCHEMA + "-recoverable-source-freeze",
        "version": 4,
        "status": "SOURCE FROZEN; FIRST-PARTY C15 ORIGINAL CAMPAIGN NOT RUN",
        "phase": "CANDIDATES",
        "family": FAMILY,
        "label": LABEL,
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "runtime": {"implementation": "CPython", "version": "3.14.6", "path": ORACLE_PYTHON, "sha256": ORACLE_PYTHON_SHA256},
        "goal": owner_dict(GOAL_OWNER),
        "phase_one": owner_dict(P0_OWNER),
        "original_oracle": {"producer": mapped_owners(PRODUCER_OWNERS), "suite_count": SUITE_COUNT, "case_execution_denominator": P0_CASES, "named_private_waiver_count": PRIVATE_WAIVERS, "source_ordered_suites": [{"suite": name, "case_execution_count": count} for name, count in SUITES], "actual_worker_process_count_if_explicitly_run": SUITE_COUNT, "nested_case_count": 128, "nested_interpreter_events": 394, "nested_interpreters_created": 11, "nested_interpreters_destroyed": 11, "original_producer_legacy_controller_invoked": False, "direct_unchanged_observers_only": True, "actual_worker_inserts_exact_repository_root_only": True},
        "immutable_original_c_sources": {"adapter": owner_dict(ORIGINAL_ADAPTER), "engine_source": owner_dict(ORIGINAL_C_SOURCE), "source_target_count": 0, "adapter_promoted": False, "engine_source_promoted": False, "family_spec_rebound": False},
        "original_native": {"relative": NATIVE_PATH, "sha256": ORIGINAL_NATIVE_SHA256, "bytes": ORIGINAL_NATIVE_BYTES, "device": ORIGINAL_NATIVE_DEVICE, "inode": ORIGINAL_NATIVE_INODE, "mode": "0755", "uid": ORIGINAL_NATIVE_UID, "nlink": 1},
        "actual_c15_source_build": {"owners": mapped_owners(C15_OWNERS), "archive_decompressed_sha256": C15_ARCHIVE_DECOMPRESSED_SHA256, "archive_decompressed_bytes": C15_ARCHIVE_DECOMPRESSED_BYTES, "compiler_process_count": 14, "phase_count": 2, "source_apply_count": 2, "native_outputs_byte_identical": True, "native_sha256": C15_NATIVE_SHA256, "native_bytes": C15_NATIVE_BYTES, "phase_a_native_device": C15_PHASE_DEVICE, "phase_a_native_inode": C15_PHASE_NATIVE_INODE, "phase_a_native_mode": "0700", "phase_a_source_sha256": C15_REPAIRED_SOURCE_SHA256, "phase_a_source_bytes": C15_REPAIRED_SOURCE_BYTES, "phase_a_source_device": C15_PHASE_DEVICE, "phase_a_source_inode": C15_REPAIRED_SOURCE_INODE, "build_root": BUILD_ROOT, "phase_a_source_snapshot_root": BUILD_ROOT + "/reference-a/source", "build_status": "PASS", "candidate_matching": "NOT MEASURED", "candidate_qualified": False},
        "current_published_v29": {"owners": mapped_owners(OVERVIEW_OWNERS), "repository_evidence_owner_count": CURRENT_OVERVIEW_OWNERS, "authenticated_digest_addressed_history_paths": CURRENT_OVERVIEW_REFERENCES, "case_execution_denominator": P0_CASES, "suite_count": SUITE_COUNT, "named_private_waiver_count": PRIVATE_WAIVERS, "qualified_candidate_count": 0, "c15_source_build_status": "PASS", "c15_candidate_matching": "NOT MEASURED", "historical_c_semantic_mismatch_count": 1262, "historical_c_verified_passing_case_count": 7325, "rust_semantic_mismatch_count": 1087, "rust_verified_passing_case_count": 7438, "zig_semantic_mismatch_count": 2172, "zig_verified_passing_case_count": 2847, "zig_preflight_worker_count": 0, "holdout": "NOT OPENED"},
        "preserved_actual_history": {"owners": mapped_owners(HISTORICAL_OWNERS), "rust_candidate_status": "FAIL", "rust_candidate_workers": 13, "rust_semantic_mismatches": 1087, "rust_verified_passing_cases": 7438, "zig_candidate_status": "FAIL", "zig_candidate_workers": 13, "zig_semantic_mismatches": 2172, "zig_verified_passing_cases": 2847, "zig_preflight_candidate_workers": 0, "rust_archive_inflated": False, "zig_archive_inflated": False},
        "public_recovery": {"root": PUBLIC_ROOT, "build_root": BUILD_ROOT, "caller_pins_exact_root": True, "caller_pins_exact_build_root": True, "exclusive_nonblocking_controller_lock": True, "root_owner_mode": "0700", "lock_owner_mode": "0600", "target_count": 1, "target_relative": NATIVE_PATH, "original_inode_backup": "ADJACENT SAME-DIRECTORY HARDLINK", "cross_device_promotion_strategy": "STREAM COPY INTO NEW OWNER-ONLY SAME-DEVICE STAGE", "cross_device_rename_permitted": False, "cross_device_link_permitted": False, "original_device": ORIGINAL_NATIVE_DEVICE, "build_device": C15_PHASE_DEVICE, "phase_output_promoted_directly": False, "stage_device": ORIGINAL_NATIVE_DEVICE, "stage_owner_must_be_new": True, "journal_filename": JOURNAL_NAME, "journal_fsync_before_first_target_mutation": True, "journal_location_announced_before_first_target_mutation": True, "caller_pins_exact_journal_sha256": True, "promotion_intent_filename": PROMOTION_INTENT_NAME, "promotion_intent_durable_before_stage_creation": True, "stage_intent_filename": STAGE_INTENT_NAME, "stage_intent_atomically_published": True, "stage_intent_pending_owner_private": True, "stage_inode_intent_durable_before_streaming": True, "stage_creation_before_inode_intent_gap_recoverable": True, "partial_stage_recovery_requires_journal_bound_promotion_intent": True, "partial_stage_recovery_requires_exact_authenticated_phase_prefix": True, "partial_stage_recovery_requires_stable_nofollow_owner": True, "partial_stage_allowed_modes": ["0600", "0755"], "partial_stage_minimum_bytes": 0, "partial_stage_maximum_bytes": C15_NATIVE_BYTES, "partial_stage_removed_only_after_original_restoration": True, "partial_stage_directory_fsync_verified": True, "recovery_command_mode": "--recover", "recovery_idempotent": True, "registered_graceful_signals": list(SIGNAL_NAMES), "block_graceful_signals_during_individual_mutations": True, "signal_handlers_installed_during_source_verification": False, "group_atomic": False, "sigkill_automatically_recovered": False, "power_failure_automatically_recovered": False, "sigkill_or_power_failure_requires_public_recover": True},
        "document_size_limits": {"support_document_maximum_bytes": MAX_OWNED_BYTES, "actual_worker_stdout_maximum_bytes": MAX_WORKER_STDOUT, "worker_streams_above_support_limit_accepted": True, "worker_stream_above_declared_maximum_rejected": True, "synthetic_size_controls_allocate_no_large_streams": True},
        "durable_publication": {"frozen_low_level_publisher": mapped_owners(PUBLICATION_OWNERS), "only_allowed_helpers": ["open_evidence_directory", "write_streamed_archive"], "publisher_evidence_names_invoked": False, "publisher_freshness_gate_invoked": False, "publisher_high_level_controller_invoked": False, "exclusive_c_specific_basenames": True, "original_native_inode_restored_before_publication": True, "publication_pass_means": "DURABLE PUBLICATION ONLY", "candidate_status_recorded_separately": True},
        "source_only_effects": source_effects(),
    }


def validate_contract(value: object, source_pin: str, protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict and canonical_json(value) == canonical_json(protocol_document(source_pin, protocol_pin)), "reject a changed owner, source-only boundary, original source, cross-device stage, worker, history, or recovery contract")
    return value


class SourceOnlyViolation(GateError):
    """A source-only synthetic control attempted a real external effect."""


class SourceWall:
    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {key: 0 for key in ("filesystem", "process", "clock", "network", "thread", "native", "import", "signal", "lock")}

    def install(self, owner: Any, name: str, kind: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def reject(*_args: Any, **_kwargs: Any) -> NoReturn:
            self.blocked[kind] += 1
            raise SourceOnlyViolation("source-only inspection blocks " + kind)

        self.previous.append((owner, name, previous))
        setattr(owner, name, reject)

    def __enter__(self) -> "SourceWall":
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"), (os, "read"), (os, "write"), (os, "stat"), (os, "lstat"), (os, "fstat"), (os, "mkdir"), (os, "makedirs"), (os, "link"), (os, "replace"), (os, "rename"), (os, "unlink"), (os, "remove"), (os, "fsync"), (os, "fchmod"), (os, "listdir"), (os, "scandir"), (tempfile, "mkdtemp")):
            self.install(owner, name, "filesystem")
        for name in ("Popen", "run", "call", "check_output"):
            self.install(subprocess, name, "process")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "sleep"):
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
        for owner, name, previous in reversed(self.previous):
            setattr(owner, name, previous)


def validate_stage_prefix_evidence(owner: object, stage_bytes: object, phase_payload: object, *, promotion_intent_authenticated: object, phase_payload_authenticated: object, stage_inode_intent_authenticated: bool | None) -> dict[str, Any]:
    require(type(owner) is dict and type(stage_bytes) is bytes and type(phase_payload) is bytes, "require exact descriptor-backed stage and authenticated phase bytes")
    require(promotion_intent_authenticated is True, "reject a stage without its exact durable journal-bound precreation promotion intention")
    require(phase_payload_authenticated is True, "reject a stage prefix from an unauthenticated selected C15 build phase")
    require(stage_inode_intent_authenticated is None or stage_inode_intent_authenticated is True, "reject a substituted or invalid durable stage-inode intention")
    require(owner.get("regular") is True and owner.get("visible_regular") is True and owner.get("stable") is True, "reject a symlink, nonregular, or unstable staged owner")
    require(type(owner.get("device")) is int and owner["device"] == ORIGINAL_NATIVE_DEVICE and owner.get("visible_device") == ORIGINAL_NATIVE_DEVICE, "reject a staged owner on the wrong target device")
    require(type(owner.get("inode")) is int and owner["inode"] > 0 and owner["inode"] not in (ORIGINAL_NATIVE_INODE, C15_PHASE_NATIVE_INODE) and owner.get("visible_inode") == owner["inode"], "reject an original, phase, swapped, or non-fresh staging inode")
    require(type(owner.get("uid")) is int and owner["uid"] == ORIGINAL_NATIVE_UID and owner["uid"] == os.geteuid(), "reject a foreign staged owner")
    require(type(owner.get("nlink")) is int and owner["nlink"] == 1 and owner.get("visible_nlink") == 1, "reject a hard-linked or substituted staged owner")
    require(type(owner.get("mode")) is int and owner["mode"] in (0o600, ORIGINAL_NATIVE_MODE), "reject an unsafe partial-stage file mode")
    require(type(owner.get("size")) is int and 0 <= owner["size"] <= C15_NATIVE_BYTES and owner["size"] == len(stage_bytes) and owner.get("visible_size") == owner["size"], "reject an oversized, truncated, or changed staged byte count")
    require(0 < len(phase_payload) <= C15_NATIVE_BYTES and phase_payload.startswith(stage_bytes), "reject staged bytes that are not an exact authenticated C15 binary prefix")
    return {"status": "PASS", "device": owner["device"], "inode": owner["inode"], "uid": owner["uid"], "nlink": 1, "mode": owner["mode"], "bytes": owner["size"], "stable_nofollow_owner": True, "exact_authenticated_phase_prefix": True, "promotion_intent_authenticated": True, "durable_stage_inode_intent_authenticated": stage_inode_intent_authenticated is True, "creation_to_inode_intent_gap_recovered": stage_inode_intent_authenticated is None}


def self_test(source_pin: str, protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(contract_pin, "independently pinned version 4 contract")
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceWall() as wall:
        document = protocol_document(source_pin, protocol_pin)

        def accept(name: str, condition: bool) -> None:
            require(condition is True, "failed positive control: " + name)
            accepted.append(name)

        def reject(name: str, operation: Any) -> None:
            try:
                operation()
            except (GateError, OSError, ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
                rejected.append(name)
                return
            raise GateError("a hostile control was accepted: " + name)

        original = document["original_oracle"]
        recovery = document["public_recovery"]
        build = document["actual_c15_source_build"]
        history = document["current_published_v29"]
        accept("preserve all thirteen original suites", len(SUITES) == 13)
        accept("preserve every original case", sum(count for _, count in SUITES) == P0_CASES)
        accept("preserve thirteen named private waivers", original["named_private_waiver_count"] == 13)
        accept("preserve the real 128 nested cases", original["nested_case_count"] == 128)
        accept("preserve all 394 interpreter events", original["nested_interpreter_events"] == 394)
        accept("preserve all eleven interpreter creations", original["nested_interpreters_created"] == 11)
        accept("preserve all eleven interpreter destructions", original["nested_interpreters_destroyed"] == 11)
        accept("require thirteen independent actual workers", original["actual_worker_process_count_if_explicitly_run"] == 13)
        accept("call only unchanged original producer observers", original["direct_unchanged_observers_only"] is True)
        accept("reject the producer legacy controller", original["original_producer_legacy_controller_invoked"] is False)
        accept("make the exact repository import root actual-worker-only", original["actual_worker_inserts_exact_repository_root_only"] is True)
        accept("preserve the exact original C adapter", document["immutable_original_c_sources"]["adapter"] == owner_dict(ORIGINAL_ADAPTER))
        accept("preserve the exact original C source", document["immutable_original_c_sources"]["engine_source"] == owner_dict(ORIGINAL_C_SOURCE))
        accept("never promote the original C sources", document["immutable_original_c_sources"]["source_target_count"] == 0)
        accept("never rebind the original C family", document["immutable_original_c_sources"]["family_spec_rebound"] is False)
        accept("preserve the actual fourteen C compiler processes", build["compiler_process_count"] == 14)
        accept("preserve both byte-identical build phases", build["phase_count"] == 2 and build["native_outputs_byte_identical"] is True)
        accept("pin the exact build root", build["build_root"] == BUILD_ROOT)
        accept("derive the exact phase root from actual source evidence", build["phase_a_source_snapshot_root"] == BUILD_ROOT + "/reference-a/source")
        accept("keep the source phase on device 2049", build["phase_a_native_device"] == 2049)
        accept("keep the original native on device 2064", recovery["original_device"] == 2064)
        accept("require a new same-device staged native", recovery["stage_owner_must_be_new"] is True and recovery["stage_device"] == 2064)
        accept("forbid cross-device renames", recovery["cross_device_rename_permitted"] is False)
        accept("forbid cross-device hard links", recovery["cross_device_link_permitted"] is False)
        accept("protect exactly one canonical native", recovery["target_count"] == 1 and recovery["target_relative"] == NATIVE_PATH)
        accept("journal the original before replacement", recovery["journal_fsync_before_first_target_mutation"] is True)
        accept("announce the journal before replacement", recovery["journal_location_announced_before_first_target_mutation"] is True)
        accept("hard-link the exact original inode", recovery["original_inode_backup"] == "ADJACENT SAME-DIRECTORY HARDLINK")
        accept("require owner-only recovery and locking", recovery["root_owner_mode"] == "0700" and recovery["lock_owner_mode"] == "0600")
        accept("retain all three graceful signals", recovery["registered_graceful_signals"] == list(SIGNAL_NAMES))
        accept("do not claim automatic SIGKILL recovery", recovery["sigkill_automatically_recovered"] is False)
        accept("do not claim automatic power-failure recovery", recovery["power_failure_automatically_recovered"] is False)
        accept("preserve all 147 actual evidence owners", history["repository_evidence_owner_count"] == 147)
        accept("preserve all 152 authenticated references", history["authenticated_digest_addressed_history_paths"] == 152)
        accept("preserve all C mismatches", history["historical_c_semantic_mismatch_count"] == 1262)
        accept("preserve all Rust mismatches", history["rust_semantic_mismatch_count"] == 1087)
        accept("preserve all Zig mismatches", history["zig_semantic_mismatch_count"] == 2172)
        accept("retain the zero-worker Zig preflight", history["zig_preflight_worker_count"] == 0)
        accept("never call C++ or Go publication dispatch", document["durable_publication"]["publisher_evidence_names_invoked"] is False)
        accept("keep successful publication separate from matching", document["durable_publication"]["publication_pass_means"] == "DURABLE PUBLICATION ONLY")
        accept("keep source verification free of candidate effects", document["source_only_effects"] == source_effects())
        accept("keep support documents bounded at 32 MiB", checked_document_size(MAX_OWNED_BYTES, MAX_OWNED_BYTES) == MAX_OWNED_BYTES)
        accept("accept actual worker streams above the 32 MiB support bound", checked_document_size(MAX_OWNED_BYTES + 1, MAX_WORKER_STDOUT) == MAX_OWNED_BYTES + 1)
        accept("accept the complete declared 64 MiB worker bound", checked_document_size(MAX_WORKER_STDOUT, MAX_WORKER_STDOUT) == MAX_WORKER_STDOUT)
        accept("freeze separately bounded actual worker and support documents", document["document_size_limits"]["support_document_maximum_bytes"] == 32 * 1024 * 1024 and document["document_size_limits"]["actual_worker_stdout_maximum_bytes"] == 64 * 1024 * 1024)

        phase_prefix = b"genuine-first-party-c15-native-prefix"
        synthetic_stage = {"regular": True, "visible_regular": True, "stable": True, "device": ORIGINAL_NATIVE_DEVICE, "visible_device": ORIGINAL_NATIVE_DEVICE, "inode": ORIGINAL_NATIVE_INODE + 7919, "visible_inode": ORIGINAL_NATIVE_INODE + 7919, "uid": ORIGINAL_NATIVE_UID, "nlink": 1, "visible_nlink": 1, "mode": 0o600, "size": 0, "visible_size": 0}

        def synthetic_prefix(payload: bytes, *, inode_intent: bool | None = True, changes: dict[str, Any] | None = None, promotion: bool = True, authenticated: bool = True) -> dict[str, Any]:
            item = dict(synthetic_stage)
            item.update(size=len(payload), visible_size=len(payload))
            if changes is not None:
                item.update(changes)
            return validate_stage_prefix_evidence(item, payload, phase_prefix, promotion_intent_authenticated=promotion, phase_payload_authenticated=authenticated, stage_inode_intent_authenticated=inode_intent)

        accept("recover the durable zero-byte stage without matching", synthetic_prefix(b"")["status"] == "PASS")
        accept("recover a durable interrupted native prefix", synthetic_prefix(phase_prefix[:9])["status"] == "PASS")
        accept("recover the complete native prefix at private mode 0600", synthetic_prefix(phase_prefix)["status"] == "PASS")
        accept("recover a completely streamed native prefix", synthetic_prefix(phase_prefix, changes={"mode": ORIGINAL_NATIVE_MODE})["status"] == "PASS")
        accept("recover an interrupted prefix at executable mode 0755", synthetic_prefix(phase_prefix[:9], changes={"mode": ORIGINAL_NATIVE_MODE})["status"] == "PASS")
        accept("recover the power-loss stage-creation gap", synthetic_prefix(b"", inode_intent=None)["creation_to_inode_intent_gap_recovered"] is True)
        accept("require a durable promotion intention before stage creation", recovery["promotion_intent_durable_before_stage_creation"] is True)
        accept("publish the complete stage intention atomically", recovery["stage_intent_atomically_published"] is True)
        accept("record the exact new stage inode before streaming", recovery["stage_inode_intent_durable_before_streaming"] is True)
        accept("authenticate incomplete bytes against the actual private phase", recovery["partial_stage_recovery_requires_exact_authenticated_phase_prefix"] is True)
        accept("restore the original before cleaning an interrupted stage", recovery["partial_stage_removed_only_after_original_restoration"] is True)

        for value in ("", "a" * 63, "a" * 65, "A" * 64, "g" * 64, 0, True, None):
            reject("invalid digest " + repr(value), lambda item=value: checked_digest(item, "hostile"))
        for value in ("", "/", "/tmp", "../escape", "a/../b", "a//b", "a\\b", "a\x00b", 0, None):
            reject("invalid relative owner " + repr(value), lambda item=value: checked_relative(item))
        reject("reject a support document one byte above 32 MiB", lambda: checked_document_size(MAX_OWNED_BYTES + 1, MAX_OWNED_BYTES))
        reject("reject a worker stream one byte above 64 MiB", lambda: checked_document_size(MAX_WORKER_STDOUT + 1, MAX_WORKER_STDOUT))
        reject("reject an invented worker limit above 64 MiB", lambda: checked_document_size(1, MAX_WORKER_STDOUT + 1))
        reject("reject a boolean document size", lambda: checked_document_size(True, MAX_WORKER_STDOUT))
        reject("reject a negative document size", lambda: checked_document_size(-1, MAX_WORKER_STDOUT))
        reject("reject an empty machine document", lambda: checked_document_size(0, MAX_WORKER_STDOUT))
        reject("reject a nonprefix abandoned stage", lambda: synthetic_prefix(b"foreign"))
        reject("reject a stage without a durable promotion intent", lambda: synthetic_prefix(b"", promotion=False))
        reject("reject a substituted durable stage inode intention", lambda: synthetic_prefix(b"", inode_intent=False))
        reject("reject an unauthenticated private build phase", lambda: synthetic_prefix(b"", authenticated=False))
        reject("reject a symlinked stage", lambda: synthetic_prefix(b"", changes={"regular": False, "visible_regular": False}))
        reject("reject a stage changed after descriptor open", lambda: synthetic_prefix(b"", changes={"stable": False}))
        reject("reject a stage on the source filesystem", lambda: synthetic_prefix(b"", changes={"device": C15_PHASE_DEVICE}))
        reject("reject a stage with a swapped visible device", lambda: synthetic_prefix(b"", changes={"visible_device": C15_PHASE_DEVICE}))
        reject("reject the original inode as a stage", lambda: synthetic_prefix(b"", changes={"inode": ORIGINAL_NATIVE_INODE, "visible_inode": ORIGINAL_NATIVE_INODE}))
        reject("reject the source phase inode as a stage", lambda: synthetic_prefix(b"", changes={"inode": C15_PHASE_NATIVE_INODE, "visible_inode": C15_PHASE_NATIVE_INODE}))
        reject("reject a stage with a swapped visible inode", lambda: synthetic_prefix(b"", changes={"visible_inode": ORIGINAL_NATIVE_INODE}))
        reject("reject a foreign staged owner", lambda: synthetic_prefix(b"", changes={"uid": ORIGINAL_NATIVE_UID + 1}))
        reject("reject a hard-linked staged inode", lambda: synthetic_prefix(b"", changes={"nlink": 2, "visible_nlink": 2}))
        reject("reject a linked visible staged owner", lambda: synthetic_prefix(b"", changes={"visible_nlink": 2}))
        reject("reject a public partial staging mode", lambda: synthetic_prefix(b"", changes={"mode": 0o644}))
        reject("reject an oversized staging record", lambda: synthetic_prefix(b"", changes={"size": C15_NATIVE_BYTES + 1, "visible_size": C15_NATIVE_BYTES + 1}))
        reject("reject truncated staged byte evidence", lambda: synthetic_prefix(phase_prefix[:3], changes={"size": 4, "visible_size": 4}))
        reject("reject a stage with changed visible bytes", lambda: synthetic_prefix(phase_prefix[:3], changes={"visible_size": 4}))
        hostile_changes: tuple[tuple[str, Any], ...] = (
            ("erase original denominator", lambda item: item["original_oracle"].update(case_execution_denominator=151)),
            ("omit original suite", lambda item: item["original_oracle"]["source_ordered_suites"].pop()),
            ("omit named private waiver", lambda item: item["original_oracle"].update(named_private_waiver_count=12)),
            ("omit nested interpreter event", lambda item: item["original_oracle"].update(nested_interpreter_events=393)),
            ("reuse one worker", lambda item: item["original_oracle"].update(actual_worker_process_count_if_explicitly_run=1)),
            ("invoke rejected producer controller", lambda item: item["original_oracle"].update(original_producer_legacy_controller_invoked=True)),
            ("insert repository path in source-only mode", lambda item: item["original_oracle"].update(actual_worker_inserts_exact_repository_root_only=False)),
            ("promote adapter", lambda item: item["immutable_original_c_sources"].update(adapter_promoted=True)),
            ("promote original C source", lambda item: item["immutable_original_c_sources"].update(engine_source_promoted=True)),
            ("rebind family spec", lambda item: item["immutable_original_c_sources"].update(family_spec_rebound=True)),
            ("invent candidate matching from source build", lambda item: item["actual_c15_source_build"].update(candidate_matching="PASS")),
            ("alter phase root", lambda item: item["actual_c15_source_build"].update(build_root="/tmp/foreign")),
            ("alter original target device", lambda item: item["public_recovery"].update(original_device=2049)),
            ("alter phase target device", lambda item: item["public_recovery"].update(build_device=2064)),
            ("rename the phase across filesystems", lambda item: item["public_recovery"].update(cross_device_rename_permitted=True)),
            ("link the phase across filesystems", lambda item: item["public_recovery"].update(cross_device_link_permitted=True)),
            ("reuse an old stage inode", lambda item: item["public_recovery"].update(stage_owner_must_be_new=False)),
            ("stage on the source device", lambda item: item["public_recovery"].update(stage_device=2049)),
            ("omit durable preactivation journal", lambda item: item["public_recovery"].update(journal_fsync_before_first_target_mutation=False)),
            ("omit early public journal announcement", lambda item: item["public_recovery"].update(journal_location_announced_before_first_target_mutation=False)),
            ("omit precreation promotion intention", lambda item: item["public_recovery"].update(promotion_intent_durable_before_stage_creation=False)),
            ("omit durable stage-inode intention", lambda item: item["public_recovery"].update(stage_inode_intent_durable_before_streaming=False)),
            ("publish a truncated final stage intention", lambda item: item["public_recovery"].update(stage_intent_atomically_published=False)),
            ("hide the stage-creation power-loss gap", lambda item: item["public_recovery"].update(stage_creation_before_inode_intent_gap_recoverable=False)),
            ("accept an unauthenticated partial-stage prefix", lambda item: item["public_recovery"].update(partial_stage_recovery_requires_exact_authenticated_phase_prefix=False)),
            ("remove a stage before restoring the original", lambda item: item["public_recovery"].update(partial_stage_removed_only_after_original_restoration=False)),
            ("silently cap a declared 64 MiB worker at 32 MiB", lambda item: item["document_size_limits"].update(actual_worker_stdout_maximum_bytes=MAX_OWNED_BYTES)),
            ("silently expand a 32 MiB support document", lambda item: item["document_size_limits"].update(support_document_maximum_bytes=MAX_WORKER_STDOUT)),
            ("replace original inode backup with byte copy", lambda item: item["public_recovery"].update(original_inode_backup="BYTE COPY")),
            ("weaken recovery lock", lambda item: item["public_recovery"].update(exclusive_nonblocking_controller_lock=False)),
            ("install source-only signal handlers", lambda item: item["public_recovery"].update(signal_handlers_installed_during_source_verification=True)),
            ("falsely promise SIGKILL recovery", lambda item: item["public_recovery"].update(sigkill_automatically_recovered=True)),
            ("falsely promise power-failure recovery", lambda item: item["public_recovery"].update(power_failure_automatically_recovered=True)),
            ("hide a historic C mismatch", lambda item: item["current_published_v29"].update(historical_c_semantic_mismatch_count=0)),
            ("hide a historic Rust mismatch", lambda item: item["current_published_v29"].update(rust_semantic_mismatch_count=0)),
            ("hide a historic Zig mismatch", lambda item: item["current_published_v29"].update(zig_semantic_mismatch_count=0)),
            ("invent a preflight worker", lambda item: item["current_published_v29"].update(zig_preflight_worker_count=1)),
            ("remove authenticated evidence history", lambda item: item["current_published_v29"].update(repository_evidence_owner_count=145)),
            ("call unsupported publication dispatch", lambda item: item["durable_publication"].update(publisher_evidence_names_invoked=True)),
            ("misreport publication as candidate correctness", lambda item: item["durable_publication"].update(publication_pass_means="CANDIDATE CORRECTNESS PASS")),
            ("read a source-only target", lambda item: item["source_only_effects"].update(canonical_target_reads=1)),
            ("read a source-only build root", lambda item: item["source_only_effects"].update(actual_build_root_opens=1)),
            ("open the final holdout", lambda item: item["source_only_effects"].update(holdout="OPENED")),
            ("invent a speed measurement", lambda item: item["source_only_effects"].update(performance="PASS")),
        )
        for name, mutate in hostile_changes:

            def changed(operation: Any = mutate) -> None:
                value = copy.deepcopy(document)
                operation(value)
                validate_contract(value, source_pin, protocol_pin)

            reject(name, changed)
        controls = (
            ("filesystem", lambda: os.open("/forbidden", os.O_RDONLY)),
            ("process", lambda: subprocess.run(("/usr/bin/true",))),
            ("clock", lambda: time.perf_counter_ns()),
            ("network", lambda: socket.create_connection(("invalid", 1))),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("native", lambda: ctypes.CDLL("foreign.so")),
            ("import", lambda: importlib.import_module("candidates.vm_candidate")),
            ("signal", lambda: signal.signal(signal.SIGTERM, lambda *_: None)),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
        )
        for name, action in controls:
            reject("block real " + name, action)
        blocked = dict(wall.blocked)
    require(len(accepted) >= 30 and len(rejected) >= 50 and all(value > 0 for value in blocked.values()), "require positive, hostile, cross-device, signal, and no-effect controls")
    return {"schema": SCHEMA + "-synthetic-source-self-test", "status": "PASS", "version": 4, "family": FAMILY, "mode": "SYNTHETIC SOURCE ONLY", "source_sha256": source_pin, "protocol_sha256": protocol_pin, "contract_sha256": contract_pin, "accepted_control_count": len(accepted), "accepted_controls": accepted, "rejected_hostile_control_count": len(rejected), "rejected_hostile_controls": rejected, "blocked_effects_by_kind": blocked, "suite_count": SUITE_COUNT, "case_execution_denominator": P0_CASES, "named_private_waiver_count": PRIVATE_WAIVERS, "repository_evidence_owner_count": CURRENT_OVERVIEW_OWNERS, "authenticated_digest_addressed_history_paths": CURRENT_OVERVIEW_REFERENCES, "actual_c15_build_process_count": 14, "actual_c15_build_candidate_correctness": "NOT MEASURED", "historical_c_semantic_mismatch_count": 1262, "actual_rust_semantic_mismatch_count": 1087, "actual_zig_semantic_mismatch_count": 2172, "actual_zig_preflight_candidate_workers": 0, "public_recovery_root": PUBLIC_ROOT, "caller_pinned_build_root": BUILD_ROOT, "original_target_count": 1, "original_native_device": ORIGINAL_NATIVE_DEVICE, "source_phase_device": C15_PHASE_DEVICE, "graceful_signal_names": list(SIGNAL_NAMES), "group_atomic": False, "sigkill_automatically_recovered": False, "power_failure_automatically_recovered": False, **source_effects()}


def read_caller_owner(relative: str, digest: str) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    checked_digest(digest, relative)
    require(not relative.startswith("candidates/"), "do not inspect a candidate in source-only verification")
    visible = os.stat(str(ROOT / relative), follow_symlinks=False)
    require(stat.S_ISREG(visible.st_mode) and 0 < visible.st_size <= MAX_OWNED_BYTES, "require a bounded regular caller-pinned source owner")
    return read_owned(Owner(relative, digest, visible.st_size))


def verify_context(source_pin: str, protocol_pin: str, contract_pin: str | None = None, *, retain: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    _, source = read_caller_owner(SOURCE_PATH, source_pin)
    _, protocol = read_caller_owner(PROTOCOL_PATH, protocol_pin)
    authenticated: dict[str, dict[str, Any]] = {}
    retained_raw: dict[str, bytes] = {}
    for group in ((GOAL_OWNER, P0_OWNER), PRODUCER_OWNERS, PUBLICATION_OWNERS, C15_OWNERS, OVERVIEW_OWNERS, HISTORICAL_OWNERS):
        for item in group:
            if item.relative_path in authenticated:
                continue
            raw, record = read_owned(item)
            authenticated[item.relative_path] = record
            if item in (P0_OWNER, PRODUCER_OWNERS[0], PUBLICATION_OWNERS[0], C15_OWNERS[3], C15_OWNERS[4], OVERVIEW_OWNERS[1], OVERVIEW_OWNERS[2], HISTORICAL_OWNERS[1], HISTORICAL_OWNERS[3], HISTORICAL_OWNERS[5]):
                retained_raw[item.relative_path] = raw

    p0 = strict_document(retained_raw[P0_OWNER.relative_path], "frozen original phase-one oracle")
    denominator = p0.get("denominator")
    upstream = p0.get("original_upstream")
    gate = p0.get("phase_gate")
    require(type(denominator) is dict and type(upstream) is dict and type(gate) is dict and denominator.get("final_required_case_execution_denominator") == P0_CASES and denominator.get("available_frozen_vector_case_executions") == P0_CASES and tuple(denominator.get("counted_suite_ids", ())) == tuple(name for name, _ in SUITES) and type(p0.get("suites")) is list and [(row.get("id", row.get("suite_id", row.get("suite"))), row.get("case_execution_count", row.get("case_count"))) for row in p0["suites"]] == list(SUITES) and upstream.get("private_waiver_count") == PRIVATE_WAIVERS and gate.get("status") == "PASS" and gate.get("all_obligations_mapped") is True and gate.get("final_holdout_authorized") is False, "preserve every original 31,237/13/13 oracle obligation without opening the holdout")

    compressed = retained_raw[C15_OWNERS[3].relative_path]
    try:
        expanded = gzip.decompress(compressed)
    except (OSError, EOFError, ValueError) as exc:
        raise GateError("reject an invalid C15 source-build archive") from exc
    require(len(expanded) == C15_ARCHIVE_DECOMPRESSED_BYTES and sha256_bytes(expanded) == C15_ARCHIVE_DECOMPRESSED_SHA256, "verify the complete bounded genuine C15 source-build archive")
    build = strict_document(expanded, "genuine C15 source-build evidence")
    phases = build.get("phases")
    proof = build.get("reproducibility")
    require(type(phases) is list and len(phases) == 2 and type(proof) is dict, "require both genuine C15 build phases")
    phase_a = phases[0]
    phase_b = phases[1]
    require(type(phase_a) is dict and type(phase_b) is dict and phase_a.get("name") == "reference-a" and phase_b.get("name") == "reference-b", "preserve both source-ordered independent C15 phases")
    source_owner = phase_a.get("fresh_source_owners", {}).get(ORIGINAL_C_SOURCE.relative_path)
    native_owner = phase_a.get("native_outputs", {}).get("extension")
    require(type(source_owner) is dict and type(native_owner) is dict and type(source_owner.get("source_overlay")) is dict and source_owner["source_overlay"].get("snapshot_root") == BUILD_ROOT + "/reference-a/source" and source_owner.get("sha256") == C15_REPAIRED_SOURCE_SHA256 and source_owner.get("bytes") == C15_REPAIRED_SOURCE_BYTES and source_owner.get("device") == C15_PHASE_DEVICE and source_owner.get("inode") == C15_REPAIRED_SOURCE_INODE and native_owner.get("sha256") == C15_NATIVE_SHA256 and native_owner.get("size_bytes") == C15_NATIVE_BYTES and native_owner.get("device") == C15_PHASE_DEVICE and native_owner.get("inode") == C15_PHASE_NATIVE_INODE and native_owner.get("file_name") == NATIVE_NAME, "derive the exact cross-device phase owners from the actual nested C15 evidence")
    require(build.get("status") == "PASS" and build.get("family") == FAMILY and build.get("label") == LABEL and build.get("actual_compiler_process_count") == 14 and build.get("candidate_correctness") == "NOT MEASURED" and build.get("holdout") == "NOT OPENED" and proof.get("status") == "PASS" and proof.get("byte_identical") is True and proof.get("phase_count") == 2 and proof.get("source_apply_count") == 2 and proof.get("actual_compiler_process_count") == 14 and proof.get("derived_source_sha256") == C15_REPAIRED_SOURCE_SHA256 and proof.get("derived_source_bytes") == C15_REPAIRED_SOURCE_BYTES and proof.get("original_adapter_modified") is False and proof.get("original_source_modified") is False, "never mistake a genuine reproducible C15 source build for candidate correctness")

    receipt = strict_document(retained_raw[C15_OWNERS[4].relative_path], "genuine C15 source-build publication receipt")
    require(receipt.get("schema") == "rebar-phase2-owned-c-pickle-source-build-v15-durable-publication-receipt" and receipt.get("version") == 15 and receipt.get("status") == "PASS" and receipt.get("build_status") == "PASS" and receipt.get("candidate_correctness") == "NOT MEASURED" and receipt.get("family") == FAMILY and receipt.get("label") == LABEL and receipt.get("archive_relative") == C15_OWNERS[3].relative_path and receipt.get("archive_sha256") == C15_OWNERS[3].sha256 and receipt.get("archive_bytes") == C15_OWNERS[3].size and receipt.get("actual_compiler_process_count") == 14, "authenticate genuine C15 publication without inventing a matching result")

    graph = strict_document(retained_raw[OVERVIEW_OWNERS[2].relative_path], "published candidate overview version 29")
    graph_inputs = strict_document(retained_raw[OVERVIEW_OWNERS[1].relative_path], "published candidate overview version 29 inputs")
    require(graph.get("schema") == "rebar-candidate-current-overview-v29-summary" and graph.get("status") == "PASS" and graph.get("repository_evidence_owner_count") == CURRENT_OVERVIEW_OWNERS and graph.get("authenticated_digest_addressed_history_paths") == CURRENT_OVERVIEW_REFERENCES and graph.get("full_case_denominator") == P0_CASES and graph.get("suite_count") == SUITE_COUNT and graph.get("private_waiver_count") == PRIVATE_WAIVERS and graph.get("qualified_candidate_count") == 0 and graph.get("c_v15_source_build_status") == "PASS" and graph.get("c_v15_source_build_candidate_correctness") == "NOT MEASURED" and graph.get("c_repaired_semantic_mismatch_count") == 1262 and graph.get("c_repaired_verified_passing_case_count") == 7325 and graph.get("rust_original_campaign_semantic_mismatch_count") == 1087 and graph.get("rust_original_campaign_verified_passing_case_count") == 7438 and graph.get("zig_original_campaign_semantic_mismatch_count") == 2172 and graph.get("zig_original_campaign_verified_passing_case_count") == 2847 and graph.get("final_holdout_opened") is False and graph.get("performance") == "NOT MEASURED", "preserve the actual 147/152 overview and every published C, Rust, and Zig loss")
    require(graph_inputs.get("schema") == "rebar-candidate-current-overview-v29-inputs" and graph_inputs.get("repository_evidence_owner_count") == CURRENT_OVERVIEW_OWNERS and graph_inputs.get("all_digest_addressed_history_path_count") == CURRENT_OVERVIEW_REFERENCES and graph_inputs.get("full_case_denominator") == P0_CASES and graph_inputs.get("suite_count") == SUITE_COUNT and graph_inputs.get("actual_rust_semantic_mismatch_count") == 1087 and graph_inputs.get("actual_zig_semantic_mismatch_count") == 2172 and graph_inputs.get("final_holdout_opened") is False, "authenticate the full current published graph inputs")

    for owner, candidate, expected in ((HISTORICAL_OWNERS[1], "rust", 1087), (HISTORICAL_OWNERS[3], "zig", 2172)):
        previous = strict_document(retained_raw[owner.relative_path], "complete published " + candidate + " failure receipt")
        require(previous.get("status") == "PASS" and previous.get("candidate_status") == "FAIL" and previous.get("family") == candidate and previous.get("semantic_mismatch_count") == expected and previous.get("case_execution_denominator") == P0_CASES and previous.get("actual_candidate_workers") == 13, "retain a genuine complete published " + candidate + " loss")
    preflight = strict_document(retained_raw[HISTORICAL_OWNERS[5].relative_path], "historical zero-worker Zig preflight")
    require(preflight.get("status") == "PASS" and preflight.get("family") == "zig" and preflight.get("actual_candidate_workers") == 0 and preflight.get("semantic_mismatch_count") == "NOT MEASURED", "preserve the separate zero-worker Zig preflight")

    producer_tree = ast.parse(retained_raw[PRODUCER_OWNERS[0].relative_path], filename=PRODUCER_OWNERS[0].relative_path)
    publication_tree = ast.parse(retained_raw[PUBLICATION_OWNERS[0].relative_path], filename=PUBLICATION_OWNERS[0].relative_path)
    producer_functions = {node.name for node in producer_tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    publisher_functions = {node.name for node in publication_tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    require({"family_spec", "suite_spec", "exact_native_owners", "observe_direct_suite", "observe_original_upstream", "observe_subinterpreters", "interpreter_bootstrap_source"} <= producer_functions, "require the original direct C and subinterpreter producer observers")
    require({"open_evidence_directory", "write_streamed_archive"} <= publisher_functions, "require only the exact low-level streaming publication primitives")
    frozen_owner: dict[str, Any] | None = None
    if contract_pin is not None:
        raw_contract, frozen_owner = read_caller_owner(CONTRACT_PATH, contract_pin)
        validate_contract(strict_document(raw_contract, "exact C campaign version 4 contract"), source_pin, protocol_pin)
    require(not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "source-only verification must never import a candidate")
    result = {"schema": SCHEMA + "-read-only-frozen-context", "status": "PASS", "version": 4, "family": FAMILY, "mode": "READ-ONLY RECOVERABLE FIRST-PARTY C15 SOURCE FREEZE", "source": source, "protocol": protocol, "contract": frozen_owner, "authenticated_support_owner_count": len(authenticated), "suite_count": SUITE_COUNT, "case_execution_denominator": P0_CASES, "named_private_waiver_count": PRIVATE_WAIVERS, "repository_evidence_owner_count": CURRENT_OVERVIEW_OWNERS, "authenticated_digest_addressed_history_paths": CURRENT_OVERVIEW_REFERENCES, "actual_c15_build_process_count": 14, "c15_candidate_correctness": "NOT MEASURED", "historical_c_semantic_mismatch_count": 1262, "actual_rust_semantic_mismatch_count": 1087, "actual_zig_semantic_mismatch_count": 2172, "actual_zig_preflight_candidate_workers": 0, "public_recovery_root": PUBLIC_ROOT, "caller_pinned_build_root": BUILD_ROOT, "original_target_count": 1, "original_native_device": ORIGINAL_NATIVE_DEVICE, "source_phase_device": C15_PHASE_DEVICE, "uncompressed_c15_source_build_archive_bytes_read": len(expanded), "graceful_signal_names": list(SIGNAL_NAMES), "group_atomic": False, "sigkill_automatically_recovered": False, "power_failure_automatically_recovered": False, **source_effects()}
    return result, ({"phase_one": p0, "producer_source": retained_raw[PRODUCER_OWNERS[0].relative_path], "publication_source": retained_raw[PUBLICATION_OWNERS[0].relative_path], "c15_build": build} if retain else {})


@contextlib.contextmanager
def installed_signal_handlers() -> Iterator[None]:
    require(threading.current_thread() is threading.main_thread(), "install actual recovery handlers only on the controller main thread")
    previous: dict[signal.Signals, Any] = {}

    def interrupted(signum: int, _frame: Any) -> NoReturn:
        raise ControllerSignal(signum)

    try:
        for name in SIGNAL_NAMES:
            selected = getattr(signal, name)
            require(isinstance(selected, signal.Signals), "require a genuine supported POSIX recovery signal")
            previous[selected] = signal.getsignal(selected)
            signal.signal(selected, interrupted)
        yield
    finally:
        for selected, handler in reversed(tuple(previous.items())):
            signal.signal(selected, handler)


@contextlib.contextmanager
def blocked_controller_signals() -> Iterator[None]:
    require(callable(getattr(signal, "pthread_sigmask", None)), "require genuine POSIX signal masking for recovery-critical mutation")
    chosen = {getattr(signal, name) for name in SIGNAL_NAMES}
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, chosen)
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


def checked_public_root(value: object) -> str:
    require(type(value) is str and value == PUBLIC_ROOT and value.startswith("/tmp/") and len(value.split("/")) == 3, "require the exact caller-pinned public owner-only recovery root")
    return value


def open_private_directory(root: str) -> int:
    checked_public_root(root)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    handle = os.open(root, flags)
    try:
        actual = os.fstat(handle)
        visible = os.stat(root, follow_symlinks=False)
        require(stat.S_ISDIR(actual.st_mode) and actual.st_uid == os.geteuid() and stat.S_IMODE(actual.st_mode) == 0o700 and (actual.st_dev, actual.st_ino) == (visible.st_dev, visible.st_ino), "reject a foreign, redirected, or non-private recovery root")
        return handle
    except BaseException:
        os.close(handle)
        raise


def write_all(descriptor: int, payload: bytes) -> int:
    require(type(payload) is bytes, "write only exact canonical bytes")
    cursor = 0
    while cursor < len(payload):
        count = os.write(descriptor, payload[cursor:])
        require(type(count) is int and count > 0, "reject an incomplete durable owner write")
        cursor += count
    return cursor


def write_private(root: str, name: str, document: dict[str, Any]) -> dict[str, Any]:
    require(type(name) is str and bool(name) and "/" not in name, "require one exact exclusive private owner basename")
    directory = open_private_directory(root)
    descriptor: int | None = None
    reader: int | None = None
    try:
        payload = canonical_json(document)
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory)
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid() and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600, "reject a foreign or reused private owner")
        write_all(descriptor, payload)
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino) and after.st_size == len(payload), "reject a swapped or truncated private owner")
        os.close(descriptor)
        descriptor = None
        os.fsync(directory)
        reader = os.open(name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        first = os.fstat(reader)
        visible = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size) == (after.st_dev, after.st_ino, len(payload)) and (first.st_dev, first.st_ino, first.st_size) == (visible.st_dev, visible.st_ino, visible.st_size), "reject private owner substitution before readback")
        chunks: list[bytes] = []
        remaining = len(payload)
        while remaining:
            piece = os.read(reader, min(remaining, 1024 * 1024))
            require(bool(piece), "reject a truncated private owner readback")
            chunks.append(piece)
            remaining -= len(piece)
        require(os.read(reader, 1) == b"" and b"".join(chunks) == payload, "verify every durable private owner byte")
        os.fsync(directory)
        return {"relative": name, "path": root + "/" + name, "sha256": sha256_bytes(payload), "bytes": len(payload), "size_bytes": len(payload), "device": first.st_dev, "inode": first.st_ino, "mode": 0o600, "exclusive_creation": True, "same_inode_readback_verified": True, "file_fsync_completed": True, "directory_fsync_completed": True}
    finally:
        if reader is not None:
            os.close(reader)
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def read_private(root: str, name: str, expected_sha256: str) -> tuple[dict[str, Any], dict[str, Any]]:
    require(type(name) is str and bool(name) and "/" not in name, "require one exact recovery basename")
    checked_digest(expected_sha256, "private recovery owner")
    directory = open_private_directory(root)
    descriptor: int | None = None
    try:
        descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        before = os.fstat(descriptor)
        visible = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid() and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600 and 0 < before.st_size <= MAX_OWNED_BYTES and (before.st_dev, before.st_ino, before.st_size) == (visible.st_dev, visible.st_ino, visible.st_size), "reject a foreign, linked, truncated, or substituted recovery owner")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(piece), "reject truncated recovery bytes")
            chunks.append(piece)
            remaining -= len(piece)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        named = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require(os.read(descriptor, 1) == b"" and sha256_bytes(payload) == expected_sha256 and (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) and (after.st_dev, after.st_ino, after.st_size) == (named.st_dev, named.st_ino, named.st_size), "reject an incomplete or changed caller-pinned recovery owner")
        return strict_document(payload, name), {"relative": name, "path": root + "/" + name, "sha256": expected_sha256, "bytes": len(payload), "size_bytes": len(payload), "device": before.st_dev, "inode": before.st_ino, "mode": 0o600, "exclusive_creation": True, "same_inode_readback_verified": True, "file_fsync_completed": True, "directory_fsync_completed": True}
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def private_owner_exists(root: str, name: str) -> bool:
    require(type(name) is str and bool(name) and "/" not in name, "inspect only one exact private recovery-intention basename")
    directory = open_private_directory(root)
    try:
        try:
            os.stat(name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            return False
        return True
    finally:
        os.close(directory)


def write_stage_inode_intention(root: str, journal_sha256: str, *, device: int, inode: int, uid: int) -> dict[str, Any]:
    document = stage_inode_intention(root, journal_sha256, device=device, inode=inode, uid=uid)
    pending_name = STAGE_INTENT_NAME + ".pending"
    pending = write_private(root, pending_name, document)
    directory = open_private_directory(root)
    try:
        ensure_absent(directory, STAGE_INTENT_NAME)
        visible = os.stat(pending_name, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(visible.st_mode) and visible.st_uid == os.geteuid() and visible.st_nlink == 1 and stat.S_IMODE(visible.st_mode) == 0o600 and (visible.st_dev, visible.st_ino, visible.st_size) == (pending["device"], pending["inode"], pending["size_bytes"]), "authenticate the exclusive fully durable pending stage intention before publication")
        os.replace(pending_name, STAGE_INTENT_NAME, src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
    finally:
        os.close(directory)
    restored, owner = read_private(root, STAGE_INTENT_NAME, pending["sha256"])
    require(canonical_json(restored) == canonical_json(document) and (owner["device"], owner["inode"], owner["size_bytes"]) == (pending["device"], pending["inode"], pending["size_bytes"]), "publish the complete stage intention atomically without exposing a truncated final intention")
    return owner


def open_recovery_lock(root: str, *, create: bool) -> tuple[int, int]:
    checked_public_root(root)
    if create:
        os.mkdir(root, mode=0o700)
        parent = os.open("/tmp", os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    directory = open_private_directory(root)
    lock: int | None = None
    try:
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if create:
            flags |= os.O_CREAT | os.O_EXCL
        lock = os.open("controller.lock", flags, 0o600, dir_fd=directory)
        actual = os.fstat(lock)
        visible = os.stat("controller.lock", dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(actual.st_mode) and actual.st_uid == os.geteuid() and actual.st_nlink == 1 and stat.S_IMODE(actual.st_mode) == 0o600 and (actual.st_dev, actual.st_ino) == (visible.st_dev, visible.st_ino), "reject a substituted or non-private actual recovery lock")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.fsync(lock)
        os.fsync(directory)
        return directory, lock
    except BaseException:
        if lock is not None:
            os.close(lock)
        os.close(directory)
        raise


def exact_original_native(*, nlink: int = 1) -> dict[str, Any]:
    _, owner = read_owned(Owner(NATIVE_PATH, ORIGINAL_NATIVE_SHA256, ORIGINAL_NATIVE_BYTES), allow_canonical_target=True, expected_device=ORIGINAL_NATIVE_DEVICE, expected_inode=ORIGINAL_NATIVE_INODE, expected_mode=ORIGINAL_NATIVE_MODE, expected_nlink=nlink)
    require(owner["uid"] == ORIGINAL_NATIVE_UID, "restore the exact original native owner UID")
    return owner


def open_native_directory() -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    root = os.open(str(ROOT), flags)
    try:
        directory = os.open("candidates", flags, dir_fd=root)
    finally:
        os.close(root)
    try:
        current = os.fstat(directory)
        require(stat.S_ISDIR(current.st_mode) and current.st_uid == os.geteuid() and current.st_dev == ORIGINAL_NATIVE_DEVICE, "require the exact original native filesystem")
        return directory
    except BaseException:
        os.close(directory)
        raise


def ensure_absent(directory: int, name: str) -> None:
    require(type(name) is str and bool(name) and "/" not in name, "reject an escaped staging basename")
    try:
        os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise GateError("never replace or reuse an existing native staging owner: " + name)


def promotion_intention(root: str, journal_sha256: str) -> dict[str, Any]:
    return {"schema": SCHEMA + "-mutation-intention", "status": "PREPARED", "operation": "PROMOTE NEW SAME-DEVICE STREAMED NATIVE", "activation_root": checked_public_root(root), "journal_sha256": checked_digest(journal_sha256, "journal-bound precreation promotion intention"), "target_relative": NATIVE_PATH, "backup_filename": BACKUP_NAME, "stage_filename": STAGE_NAME, "phase_device": C15_PHASE_DEVICE, "phase_inode": C15_PHASE_NATIVE_INODE, "phase_sha256": C15_NATIVE_SHA256, "phase_bytes": C15_NATIVE_BYTES, "target_device": ORIGINAL_NATIVE_DEVICE, "original_inode": ORIGINAL_NATIVE_INODE, "repaired_sha256": C15_NATIVE_SHA256, "repaired_bytes": C15_NATIVE_BYTES, "cross_device_rename_permitted": False, "cross_device_link_permitted": False, "promotion_intent_durable_before_stage_creation": True, "holdout": "NOT OPENED"}


def stage_inode_intention(root: str, journal_sha256: str, *, device: int, inode: int, uid: int) -> dict[str, Any]:
    require(type(device) is int and device == ORIGINAL_NATIVE_DEVICE and type(inode) is int and inode > 0 and inode not in (ORIGINAL_NATIVE_INODE, C15_PHASE_NATIVE_INODE) and type(uid) is int and uid == ORIGINAL_NATIVE_UID and uid == os.geteuid(), "record only the genuinely fresh owner-only same-device stage inode")
    return {"schema": SCHEMA + "-mutation-intention", "status": "PREPARED", "operation": "AUTHENTICATE NEW EXCLUSIVE STAGE INODE BEFORE STREAMING", "activation_root": checked_public_root(root), "journal_sha256": checked_digest(journal_sha256, "journal-bound durable stage inode intention"), "target_relative": NATIVE_PATH, "stage_filename": STAGE_NAME, "stage_device": device, "stage_inode": inode, "stage_uid": uid, "stage_creation_mode": "0600", "stage_creation_nlink": 1, "stage_creation_bytes": 0, "phase_device": C15_PHASE_DEVICE, "phase_inode": C15_PHASE_NATIVE_INODE, "phase_sha256": C15_NATIVE_SHA256, "phase_bytes": C15_NATIVE_BYTES, "durable_before_streaming": True, "holdout": "NOT OPENED"}


def announce_journal(root: str, journal_sha256: str) -> None:
    document = {"schema": SCHEMA + "-preactivation-public-recovery-announcement", "status": "PASS", "family": FAMILY, "label": LABEL, "activation_root": checked_public_root(root), "journal_relative": JOURNAL_NAME, "recovery_journal_sha256": checked_digest(journal_sha256, "durable original native journal"), "canonical_target_replacements_so_far": 0, "target_count": 1, "build_device": C15_PHASE_DEVICE, "target_device": ORIGINAL_NATIVE_DEVICE, "holdout": "NOT OPENED"}
    sys.stderr.buffer.write(canonical_json(document))
    sys.stderr.buffer.flush()


def recover_abandoned_stage(directory: int, root: str, journal: dict[str, Any], journal_sha256: str) -> dict[str, Any] | None:
    require(exact_original_native()["inode"] == ORIGINAL_NATIVE_INODE, "restore the exact original native inode before inspecting any abandoned stage")
    try:
        initial_visible = os.stat(STAGE_NAME, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return None

    expected_promotion = promotion_intention(root, journal_sha256)
    promotion_digest = sha256_bytes(canonical_json(expected_promotion))
    verified_promotion, _ = read_private(root, PROMOTION_INTENT_NAME, promotion_digest)
    require(canonical_json(verified_promotion) == canonical_json(expected_promotion), "reject a missing or substituted precreation native-promotion intention")
    require(journal.get("build_root") == BUILD_ROOT, "recover a stage only from the exact caller-pinned actual C15 phase root")
    expected_phase = Owner("reference-a/native/" + NATIVE_NAME, C15_NATIVE_SHA256, C15_NATIVE_BYTES)
    payload, phase = read_owned(expected_phase, root=Path(BUILD_ROOT), expected_device=C15_PHASE_DEVICE, expected_inode=C15_PHASE_NATIVE_INODE, expected_mode=C15_PHASE_NATIVE_MODE)
    recorded_phase = journal.get("phase_native")
    require(type(recorded_phase) is dict and recorded_phase == phase, "bind abandoned-stage recovery to the exact authenticated phase-A native inode and bytes")

    descriptor: int | None = None
    try:
        descriptor = os.open(STAGE_NAME, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        before = os.fstat(descriptor)
        visible = os.stat(STAGE_NAME, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(visible.st_mode) and 0 <= before.st_size <= C15_NATIVE_BYTES and (before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink) == (visible.st_dev, visible.st_ino, visible.st_size, visible.st_uid, visible.st_nlink) and (before.st_dev, before.st_ino, before.st_size) == (initial_visible.st_dev, initial_visible.st_ino, initial_visible.st_size), "reject a symlinked, oversized, exchanged, or nonregular abandoned staging inode")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(part) is bytes and bool(part), "reject an incomplete abandoned-stage descriptor read")
            chunks.append(part)
            remaining -= len(part)
        stage_bytes = b"".join(chunks)
        require(os.read(descriptor, 1) == b"", "reject extra abandoned-stage bytes")
        after = os.fstat(descriptor)
        final_visible = os.stat(STAGE_NAME, dir_fd=directory, follow_symlinks=False)
        stable = ((before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_uid, after.st_nlink, after.st_mtime_ns, after.st_ctime_ns) and (after.st_dev, after.st_ino, after.st_size, after.st_uid, after.st_nlink) == (final_visible.st_dev, final_visible.st_ino, final_visible.st_size, final_visible.st_uid, final_visible.st_nlink))
        owner = {"regular": stat.S_ISREG(after.st_mode), "visible_regular": stat.S_ISREG(final_visible.st_mode), "stable": stable, "device": after.st_dev, "visible_device": final_visible.st_dev, "inode": after.st_ino, "visible_inode": final_visible.st_ino, "uid": after.st_uid, "nlink": after.st_nlink, "visible_nlink": final_visible.st_nlink, "mode": stat.S_IMODE(after.st_mode), "size": after.st_size, "visible_size": final_visible.st_size}

        has_intent = private_owner_exists(root, STAGE_INTENT_NAME)
        authenticated_intent: bool | None = None
        if has_intent:
            expected_stage = stage_inode_intention(root, journal_sha256, device=after.st_dev, inode=after.st_ino, uid=after.st_uid)
            expected_stage_sha256 = sha256_bytes(canonical_json(expected_stage))
            actual_intent, _ = read_private(root, STAGE_INTENT_NAME, expected_stage_sha256)
            require(canonical_json(actual_intent) == canonical_json(expected_stage), "reject an unrelated, replaced, or falsely pinned durable stage inode intention")
            authenticated_intent = True
        proof = validate_stage_prefix_evidence(owner, stage_bytes, payload, promotion_intent_authenticated=True, phase_payload_authenticated=True, stage_inode_intent_authenticated=authenticated_intent)
        require(exact_original_native()["inode"] == ORIGINAL_NATIVE_INODE, "never clean a partial stage before the original native is restored")
        last = os.stat(STAGE_NAME, dir_fd=directory, follow_symlinks=False)
        require((last.st_dev, last.st_ino, last.st_size, last.st_uid, last.st_nlink, last.st_mtime_ns, last.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_uid, after.st_nlink, after.st_mtime_ns, after.st_ctime_ns), "reject a staged inode exchanged immediately before cleanup")
        os.unlink(STAGE_NAME, dir_fd=directory)
        os.fsync(directory)
        require(exact_original_native()["inode"] == ORIGINAL_NATIVE_INODE, "verify the exact original inode after descriptor-bound abandoned-stage cleanup")
        proof.update({"stage_filename": STAGE_NAME, "phase_native": phase, "removed_only_after_original_restoration": True, "directory_fsync_completed": True})
        return proof
    finally:
        if descriptor is not None:
            os.close(descriptor)


def restore_native(root: str, journal: dict[str, Any], journal_sha256: str) -> dict[str, Any]:
    require(journal.get("schema") == SCHEMA + "-durable-original-native-recovery-journal" and journal.get("family") == FAMILY and journal.get("label") == LABEL and journal.get("activation_root") == checked_public_root(root) and journal.get("build_root") == BUILD_ROOT and journal.get("target_relative") == NATIVE_PATH and journal.get("backup_filename") == BACKUP_NAME and journal.get("stage_filename") == STAGE_NAME and journal.get("original_sha256") == ORIGINAL_NATIVE_SHA256 and journal.get("original_device") == ORIGINAL_NATIVE_DEVICE and journal.get("original_inode") == ORIGINAL_NATIVE_INODE and journal.get("repaired_sha256") == C15_NATIVE_SHA256 and sha256_bytes(canonical_json(journal)) == checked_digest(journal_sha256, "caller-pinned recovery journal"), "reject a substituted, broadened, or unauthenticated recovery journal")
    directory = open_native_directory()
    operations: list[str] = []
    try:
        try:
            target = os.stat(NATIVE_NAME, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError as exc:
            raise GateError("refuse recovery of a missing canonical native target") from exc
        try:
            backup = os.stat(BACKUP_NAME, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            backup = None
        if backup is not None:
            require(stat.S_ISREG(backup.st_mode) and backup.st_uid == ORIGINAL_NATIVE_UID and stat.S_IMODE(backup.st_mode) == ORIGINAL_NATIVE_MODE and (backup.st_dev, backup.st_ino) == (ORIGINAL_NATIVE_DEVICE, ORIGINAL_NATIVE_INODE), "refuse a foreign original-native backup")
            if (target.st_dev, target.st_ino) == (ORIGINAL_NATIVE_DEVICE, ORIGINAL_NATIVE_INODE):
                require(target.st_nlink == 2 and backup.st_nlink == 2, "reject unexpected original-backup link ownership")
                os.unlink(BACKUP_NAME, dir_fd=directory)
                operations.append("REMOVE AUTHENTICATED ADJACENT ORIGINAL HARDLINK")
            else:
                repaired = read_owned(Owner(NATIVE_PATH, C15_NATIVE_SHA256, C15_NATIVE_BYTES), allow_canonical_target=True, expected_device=ORIGINAL_NATIVE_DEVICE, expected_mode=ORIGINAL_NATIVE_MODE)[1]
                require(repaired["device"] == target.st_dev and repaired["inode"] == target.st_ino and backup.st_nlink == 1, "refuse to replace an unverified active C15 native")
                os.replace(BACKUP_NAME, NATIVE_NAME, src_dir_fd=directory, dst_dir_fd=directory)
                operations.append("RESTORE AUTHENTICATED EXACT ORIGINAL INODE")
            os.fsync(directory)
        else:
            require((target.st_dev, target.st_ino) == (ORIGINAL_NATIVE_DEVICE, ORIGINAL_NATIVE_INODE), "a promoted native without its exact durable original backup is not recoverable")
        staged = recover_abandoned_stage(directory, root, journal, journal_sha256)
        if staged is not None:
            operations.append("REMOVE AUTHENTICATED JOURNAL-BOUND C15 PREFIX STAGE")
        original = exact_original_native()
        os.fsync(directory)
        return {"schema": SCHEMA + "-exact-original-native-restoration", "status": "PASS", "family": FAMILY, "label": LABEL, "activation_root": root, "recovery_journal_sha256": journal_sha256, "operations": operations, "abandoned_stage": staged, "original_native": original, "exact_original_inode_restored": True, "directory_fsync_completed": True, "group_atomic": False, "holdout": "NOT OPENED"}
    finally:
        os.close(directory)


def activate_native(options: argparse.Namespace) -> dict[str, Any]:
    root = checked_public_root(options.activation_root)
    baseline = exact_original_native()
    phase_source = Owner("reference-a/source/candidates/_vm_native.c", C15_REPAIRED_SOURCE_SHA256, C15_REPAIRED_SOURCE_BYTES)
    _, actual_source = read_owned(phase_source, root=Path(options.build_root), expected_device=C15_PHASE_DEVICE, expected_inode=C15_REPAIRED_SOURCE_INODE)
    phase_native = Owner("reference-a/native/" + NATIVE_NAME, C15_NATIVE_SHA256, C15_NATIVE_BYTES)
    payload, actual_phase = read_owned(phase_native, root=Path(options.build_root), expected_device=C15_PHASE_DEVICE, expected_inode=C15_PHASE_NATIVE_INODE, expected_mode=C15_PHASE_NATIVE_MODE)
    require(actual_phase["device"] != baseline["device"], "require the recorded actual cross-device C15 build phase")
    journal = {"schema": SCHEMA + "-durable-original-native-recovery-journal", "status": "PREPARED", "version": 4, "family": FAMILY, "label": LABEL, "activation_root": root, "build_root": options.build_root, "target_relative": NATIVE_PATH, "backup_filename": BACKUP_NAME, "stage_filename": STAGE_NAME, "original_sha256": ORIGINAL_NATIVE_SHA256, "original_bytes": ORIGINAL_NATIVE_BYTES, "original_device": ORIGINAL_NATIVE_DEVICE, "original_inode": ORIGINAL_NATIVE_INODE, "original_mode": "0755", "original_uid": ORIGINAL_NATIVE_UID, "repaired_sha256": C15_NATIVE_SHA256, "repaired_bytes": C15_NATIVE_BYTES, "phase_source": actual_source, "phase_native": actual_phase, "controller_source_sha256": options.source_sha256, "controller_protocol_sha256": options.protocol_sha256, "controller_contract_sha256": options.contract_sha256, "producer_source_sha256": PRODUCER_OWNERS[0].sha256, "build_archive_sha256": C15_OWNERS[3].sha256, "build_receipt_sha256": C15_OWNERS[4].sha256, "original_inode_backup": "ADJACENT SAME-DIRECTORY HARDLINK", "cross_device_promotion": "NEW SAME-DEVICE EXCLUSIVE STREAM COPY", "cross_device_rename_performed": False, "source_targets_modified": 0, "group_atomic": False, "holdout": "NOT OPENED"}
    journal_owner: dict[str, Any] | None = None
    try:
        with blocked_controller_signals():
            journal_owner = write_private(root, JOURNAL_NAME, journal)
            announce_journal(root, journal_owner["sha256"])
            directory = open_native_directory()
            stage_descriptor: int | None = None
            try:
                ensure_absent(directory, BACKUP_NAME)
                ensure_absent(directory, STAGE_NAME)
                require(exact_original_native() == baseline, "the original native changed after durable journal publication")
                write_private(root, "link-intent-v4.json", {"schema": SCHEMA + "-mutation-intention", "status": "PREPARED", "operation": "ADJACENT ORIGINAL HARDLINK", "activation_root": root, "journal_sha256": journal_owner["sha256"], "target_relative": NATIVE_PATH, "backup_filename": BACKUP_NAME, "original_device": ORIGINAL_NATIVE_DEVICE, "original_inode": ORIGINAL_NATIVE_INODE})
                os.link(NATIVE_NAME, BACKUP_NAME, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
                current = os.stat(NATIVE_NAME, dir_fd=directory, follow_symlinks=False)
                backup = os.stat(BACKUP_NAME, dir_fd=directory, follow_symlinks=False)
                require((current.st_dev, current.st_ino) == (backup.st_dev, backup.st_ino) == (ORIGINAL_NATIVE_DEVICE, ORIGINAL_NATIVE_INODE) and current.st_nlink == backup.st_nlink == 2, "retain the exact same-directory original native inode")
                os.fsync(directory)
                promotion_owner = write_private(root, PROMOTION_INTENT_NAME, promotion_intention(root, journal_owner["sha256"]))
                require(promotion_owner["sha256"] == sha256_bytes(canonical_json(promotion_intention(root, journal_owner["sha256"]))), "durably authenticate the exact journal-bound promotion intention before creating any stage")
                stage_descriptor = os.open(STAGE_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory)
                stage_before = os.fstat(stage_descriptor)
                require(stat.S_ISREG(stage_before.st_mode) and stage_before.st_dev == ORIGINAL_NATIVE_DEVICE and stage_before.st_ino not in (ORIGINAL_NATIVE_INODE, C15_PHASE_NATIVE_INODE) and stage_before.st_uid == ORIGINAL_NATIVE_UID and stage_before.st_uid == os.geteuid() and stage_before.st_nlink == 1 and stage_before.st_size == 0 and stat.S_IMODE(stage_before.st_mode) == 0o600, "create one genuinely fresh, empty, exclusive owner-only native inode on the target filesystem")
                os.fsync(stage_descriptor)
                os.fsync(directory)
                persisted_empty = os.fstat(stage_descriptor)
                require((persisted_empty.st_dev, persisted_empty.st_ino, persisted_empty.st_uid, persisted_empty.st_nlink, persisted_empty.st_size) == (stage_before.st_dev, stage_before.st_ino, stage_before.st_uid, 1, 0) and stat.S_IMODE(persisted_empty.st_mode) == 0o600, "durably establish the fresh empty staging inode before recording its exact owner")
                stage_intent = stage_inode_intention(root, journal_owner["sha256"], device=stage_before.st_dev, inode=stage_before.st_ino, uid=stage_before.st_uid)
                stage_intent_owner = write_stage_inode_intention(root, journal_owner["sha256"], device=stage_before.st_dev, inode=stage_before.st_ino, uid=stage_before.st_uid)
                require(stage_intent_owner["sha256"] == sha256_bytes(canonical_json(stage_intent)), "durably record the exact exclusive staging device, inode, owner, and journal before streaming")
                write_all(stage_descriptor, payload)
                os.fchmod(stage_descriptor, ORIGINAL_NATIVE_MODE)
                os.fsync(stage_descriptor)
                stage_after = os.fstat(stage_descriptor)
                require((stage_after.st_dev, stage_after.st_ino) == (stage_before.st_dev, stage_before.st_ino) and stage_after.st_size == C15_NATIVE_BYTES and stat.S_IMODE(stage_after.st_mode) == ORIGINAL_NATIVE_MODE and stage_after.st_nlink == 1, "fully fsync the exact newly streamed same-device stage")
                os.close(stage_descriptor)
                stage_descriptor = None
                _, verified_stage = read_owned(Owner("candidates/" + STAGE_NAME, C15_NATIVE_SHA256, C15_NATIVE_BYTES), allow_canonical_target=True, expected_device=ORIGINAL_NATIVE_DEVICE, expected_inode=stage_before.st_ino, expected_mode=ORIGINAL_NATIVE_MODE)
                os.fsync(directory)
                os.replace(STAGE_NAME, NATIVE_NAME, src_dir_fd=directory, dst_dir_fd=directory)
                os.fsync(directory)
                _, promoted = read_owned(Owner(NATIVE_PATH, C15_NATIVE_SHA256, C15_NATIVE_BYTES), allow_canonical_target=True, expected_device=ORIGINAL_NATIVE_DEVICE, expected_inode=verified_stage["inode"], expected_mode=ORIGINAL_NATIVE_MODE)
                require(promoted["inode"] != C15_PHASE_NATIVE_INODE and promoted["inode"] != ORIGINAL_NATIVE_INODE, "promote only the newly proven target-filesystem stage")
            finally:
                if stage_descriptor is not None:
                    os.close(stage_descriptor)
                os.close(directory)
            activation = {"schema": SCHEMA + "-native-activation-report", "status": "PASS", "version": 4, "family": FAMILY, "label": LABEL, "activation_root": root, "build_root": options.build_root, "journal": journal_owner, "promotion_intention": promotion_owner, "stage_inode_intention": stage_intent_owner, "native": promoted, "phase_native": actual_phase, "phase_source": actual_source, "original_native": baseline, "original_source_targets_modified": 0, "source_family_spec_rebound": False, "combined_native_engine_bridge": True, "cross_device_rename_performed": False, "cross_device_link_performed": False, "same_device_stream_copy": True, "original_inode_retained_by_adjacent_hardlink": True, "stage_inode_intent_durable_before_streaming": True, "stage_creation_to_intent_gap_recoverable": True, "controller_source_sha256": options.source_sha256, "controller_protocol_sha256": options.protocol_sha256, "controller_contract_sha256": options.contract_sha256, "holdout": "NOT OPENED"}
            activation_owner = write_private(root, REPORT_NAME, activation)
            receipt = {"schema": SCHEMA + "-native-activation-receipt", "status": "PASS", "activation_status": "PASS", "family": FAMILY, "label": LABEL, "activation_root": root, "activation": activation_owner, "journal": journal_owner, "target_count": 1, "source_target_count": 0, "holdout": "NOT OPENED"}
            receipt_owner = write_private(root, RECEIPT_NAME, receipt)
            return {"root": root, "journal": journal, "journal_owner": journal_owner, "activation": activation, "activation_owner": activation_owner, "receipt": receipt, "receipt_owner": receipt_owner, "original_native": baseline}
    except BaseException:
        if journal_owner is not None:
            with blocked_controller_signals():
                restore_native(root, journal, journal_owner["sha256"])
        raise


def original_source_pins() -> dict[str, str]:
    return {ORIGINAL_ADAPTER.relative_path: ORIGINAL_ADAPTER.sha256, ORIGINAL_C_SOURCE.relative_path: ORIGINAL_C_SOURCE.sha256}


def native_pins() -> dict[str, str]:
    return {"source": ORIGINAL_ADAPTER.sha256, "native_engine": C15_NATIVE_SHA256, "native_bridge": C15_NATIVE_SHA256}


def validate_actual_authorization(options: argparse.Namespace) -> None:
    require(options.family == FAMILY and options.label == LABEL and options.activation_root == PUBLIC_ROOT and options.build_root == BUILD_ROOT and options.producer_source_sha256 == PRODUCER_OWNERS[0].sha256 and options.producer_protocol_sha256 == PRODUCER_OWNERS[1].sha256 and options.producer_contract_sha256 == PRODUCER_OWNERS[2].sha256 and options.publication_source_sha256 == PUBLICATION_OWNERS[0].sha256 and options.publication_protocol_sha256 == PUBLICATION_OWNERS[1].sha256 and options.publication_contract_sha256 == PUBLICATION_OWNERS[2].sha256 and options.build_source_sha256 == C15_OWNERS[0].sha256 and options.build_protocol_sha256 == C15_OWNERS[1].sha256 and options.build_contract_sha256 == C15_OWNERS[2].sha256 and options.build_archive_sha256 == C15_OWNERS[3].sha256 and options.build_receipt_sha256 == C15_OWNERS[4].sha256 and options.v29_renderer_sha256 == OVERVIEW_OWNERS[0].sha256 and options.v29_inputs_sha256 == OVERVIEW_OWNERS[1].sha256 and options.v29_summary_sha256 == OVERVIEW_OWNERS[2].sha256 and options.v29_svg_sha256 == OVERVIEW_OWNERS[3].sha256 and options.native_engine_sha256 == C15_NATIVE_SHA256 and options.native_bridge_sha256 == C15_NATIVE_SHA256 and options.native_engine_bytes == C15_NATIVE_BYTES and options.native_bridge_bytes == C15_NATIVE_BYTES, "independently caller-pin every immutable original producer, C15, overview, cross-device root, combined native, and publisher owner")


def load_actual_producer(source: bytes) -> types.ModuleType:
    require(sha256_bytes(source) == PRODUCER_OWNERS[0].sha256, "pin every original producer source byte before loading")
    require(not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "refuse a candidate imported before actual worker provenance")
    exact_root = str(ROOT)
    if not sys.path or sys.path[0] != exact_root:
        sys.path.insert(0, exact_root)
    module = importlib.import_module("tools.run_owned_six_family_original_p0_producer_v3")
    require(type(module) is types.ModuleType and os.path.abspath(str(module.__file__)) == str(ROOT / PRODUCER_OWNERS[0].relative_path), "load only the caller-pinned original producer from the exact repository root")
    current, _ = read_owned(PRODUCER_OWNERS[0])
    require(current == source, "reject a changed original producer after import")
    return module


def verify_active_worker(options: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    require(options.activation_report_sha256 is not None and options.activation_receipt_sha256 is not None and options.recovery_journal_sha256 is not None, "require all three independently caller-pinned actual C15 activation owners")
    journal, journal_owner = read_private(options.activation_root, JOURNAL_NAME, options.recovery_journal_sha256)
    activation, activation_owner = read_private(options.activation_root, REPORT_NAME, options.activation_report_sha256)
    receipt, _ = read_private(options.activation_root, RECEIPT_NAME, options.activation_receipt_sha256)
    recorded = activation.get("native")
    require(type(recorded) is dict and activation.get("schema") == SCHEMA + "-native-activation-report" and activation.get("status") == "PASS" and activation.get("family") == FAMILY and activation.get("label") == LABEL and activation.get("activation_root") == PUBLIC_ROOT and activation.get("build_root") == BUILD_ROOT and activation.get("journal") == journal_owner and activation.get("source_family_spec_rebound") is False and activation.get("original_source_targets_modified") == 0 and activation.get("combined_native_engine_bridge") is True and activation.get("cross_device_rename_performed") is False and activation.get("cross_device_link_performed") is False and activation.get("same_device_stream_copy") is True and recorded.get("sha256") == C15_NATIVE_SHA256 and recorded.get("bytes") == C15_NATIVE_BYTES and recorded.get("device") == ORIGINAL_NATIVE_DEVICE and type(recorded.get("inode")) is int and recorded["inode"] not in (ORIGINAL_NATIVE_INODE, C15_PHASE_NATIVE_INODE), "authenticate only the actual journaled newly streamed native stage")
    require(receipt.get("schema") == SCHEMA + "-native-activation-receipt" and receipt.get("status") == "PASS" and receipt.get("family") == FAMILY and receipt.get("label") == LABEL and receipt.get("activation") == activation_owner and receipt.get("journal") == journal_owner and receipt.get("target_count") == 1 and receipt.get("source_target_count") == 0, "authenticate the complete durable one-native activation receipt")
    current = read_owned(Owner(NATIVE_PATH, C15_NATIVE_SHA256, C15_NATIVE_BYTES), allow_canonical_target=True, expected_device=ORIGINAL_NATIVE_DEVICE, expected_inode=recorded["inode"], expected_mode=ORIGINAL_NATIVE_MODE)[1]
    require(current == recorded, "refuse an active native replaced after journaled promotion")
    require(journal.get("target_relative") == NATIVE_PATH and journal.get("original_inode") == ORIGINAL_NATIVE_INODE and journal.get("repaired_sha256") == C15_NATIVE_SHA256, "preserve the exact original-inode recovery journal in every actual worker")
    expected_promotion = promotion_intention(options.activation_root, journal_owner["sha256"])
    promotion_sha256 = sha256_bytes(canonical_json(expected_promotion))
    promotion, promotion_owner = read_private(options.activation_root, PROMOTION_INTENT_NAME, promotion_sha256)
    require(promotion == expected_promotion and activation.get("promotion_intention") == promotion_owner, "authenticate the exact durable precreation promotion intention in each actual worker")
    expected_stage = stage_inode_intention(options.activation_root, journal_owner["sha256"], device=recorded["device"], inode=recorded["inode"], uid=recorded["uid"])
    stage_sha256 = sha256_bytes(canonical_json(expected_stage))
    stage_intent, stage_owner = read_private(options.activation_root, STAGE_INTENT_NAME, stage_sha256)
    require(stage_intent == expected_stage and activation.get("stage_inode_intention") == stage_owner and activation.get("stage_inode_intent_durable_before_streaming") is True and activation.get("stage_creation_to_intent_gap_recoverable") is True, "authenticate the exact durable new stage inode before trusting an original C15 worker")
    return activation, current


def error_record(error: BaseException) -> dict[str, Any]:
    return {"error_type": type(error).__qualname__, "error_message": str(error)[:8192], "traceback": traceback.format_exception(type(error), error, error.__traceback__)}


def run_worker(options: argparse.Namespace) -> dict[str, Any]:
    validate_actual_authorization(options)
    context, retained = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256, retain=True)
    require(context.get("status") == "PASS", "require the full frozen original context in each actual worker")
    require(options.suite in {name for name, _ in SUITES}, "select one exact original source-ordered suite")
    activation, current = verify_active_worker(options)
    producer = load_actual_producer(retained["producer_source"])
    spec = producer.family_spec(FAMILY)
    require(spec.name == FAMILY and spec.module == "candidates.vm_candidate" and spec.adapter_relative == ORIGINAL_ADAPTER.relative_path and spec.engine_relative == NATIVE_PATH and spec.bridge_relative == NATIVE_PATH and spec.combined_native is True and tuple(spec.source_owners) == ((ORIGINAL_ADAPTER.relative_path, ORIGINAL_ADAPTER.sha256, ORIGINAL_ADAPTER.size), (ORIGINAL_C_SOURCE.relative_path, ORIGINAL_C_SOURCE.sha256, ORIGINAL_C_SOURCE.size)), "use the untouched original producer C family and both unchanged semantic source owners")
    pins = native_pins()
    sources = original_source_pins()
    owners = producer.exact_native_owners(spec, pins, sources)
    require(owners.get("source", {}).get("sha256") == ORIGINAL_ADAPTER.sha256 and owners.get("native_engine") == owners.get("native_bridge") and owners.get("native_engine", {}).get("sha256") == C15_NATIVE_SHA256 and owners.get("native_engine", {}).get("device") == ORIGINAL_NATIVE_DEVICE and owners.get("native_engine", {}).get("inode") == current["inode"], "authenticate both original semantic sources and the one true combined C15 native")
    suite = producer.suite_spec(options.suite)
    expected = dict(SUITES)[options.suite]
    require(suite.name == options.suite and suite.case_count == expected, "reject an altered original suite denominator")
    try:
        if options.suite == "original_bounded_v5":
            observed = producer.observe_original_upstream(suite, spec, pins, sources)
        elif options.suite == "subinterpreter_v2":
            observed = producer.observe_subinterpreters(suite, spec, pins, sources, producer_sha256=PRODUCER_OWNERS[0].sha256)
        else:
            observed = producer.observe_direct_suite(suite, spec, pins, sources, retained["phase_one"])
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit, ControllerSignal)):
            raise
        details = getattr(exc, "details", None)
        return {"schema": SCHEMA + "-actual-original-worker", "status": "FAIL", "failure_class": "CANDIDATE EXECUTION FAILURE", "candidate_family": FAMILY, "label": LABEL, "suite": options.suite, "case_execution_denominator": expected, "mismatch_count": "NOT MEASURED", "all_original_records_and_mismatches_preserved": False, "original_observer_source_sha256": PRODUCER_OWNERS[0].sha256, "actual_c15_build_archive_sha256": C15_OWNERS[3].sha256, "native_engine_sha256": C15_NATIVE_SHA256, "native_bridge_sha256": C15_NATIVE_SHA256, "actual_candidate_workers": 1, "active_native": current, "actual_original_failure_details": details, "error": error_record(exc), "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "holdout": "NOT OPENED", "candidate_qualified": False}
    require(type(observed) is dict and observed.get("schema") == producer.SCHEMA + "-actual-original-suite" and observed.get("status") in ("PASS", "FAIL") and observed.get("suite") == options.suite and observed.get("candidate_family") == FAMILY and observed.get("candidate_module") == "candidates.vm_candidate" and observed.get("case_execution_denominator") == expected and observed.get("actual_candidate_case_count") == expected and observed.get("actual_candidate_workers") == 1 and type(observed.get("mismatch_count")) is int and observed["mismatch_count"] >= 0 and type(observed.get("all_mismatches")) is list and len(observed["all_mismatches"]) == observed["mismatch_count"] and type(observed.get("candidate_records")) is list and observed.get("holdout") == "NOT OPENED" and observed.get("hidden_cases_read") == 0 and observed.get("benchmark_files_read") == 0 and observed.get("clock_samples") == 0, "preserve every real original-suite observation and mismatch")
    if options.suite == "subinterpreter_v2":
        require(observed.get("actual_case_interpreter_exec_calls") == 394 and observed.get("actual_interpreters_created") == 11 and observed.get("actual_interpreters_destroyed") == 11 and observed.get("all_real_pipes_read_to_eof") is True and observed.get("all_real_pipe_descriptors_closed") is True and observed.get("interpreter_live_set_restored") is True and observed.get("locale_restored") is True, "preserve the complete genuine 128-case, 394-event, eleven-interpreter original lifecycle")
    passed = observed["status"] == "PASS" and observed["mismatch_count"] == 0
    require((observed["status"] == "PASS") is (observed["mismatch_count"] == 0), "classify the actual complete semantic observation truthfully")
    return {"schema": SCHEMA + "-actual-original-worker", "status": "PASS" if passed else "FAIL", "failure_class": "PASS" if passed else "SEMANTIC MISMATCH", "candidate_family": FAMILY, "label": LABEL, "suite": options.suite, "case_execution_denominator": expected, "mismatch_count": observed["mismatch_count"], "all_original_records_and_mismatches_preserved": True, "original_observer_source_sha256": PRODUCER_OWNERS[0].sha256, "actual_c15_build_archive_sha256": C15_OWNERS[3].sha256, "native_engine_sha256": C15_NATIVE_SHA256, "native_bridge_sha256": C15_NATIVE_SHA256, "actual_candidate_workers": 1, "active_native": current, "original_observation": observed, "source_family_spec_rebound": False, "original_source_targets_modified": 0, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "holdout": "NOT OPENED", "candidate_qualified": False}


def encode_stream(payload: bytes) -> dict[str, Any]:
    require(type(payload) is bytes, "retain the complete exact actual worker stream")
    return {"base64": base64.b64encode(payload).decode("ascii"), "sha256": sha256_bytes(payload), "size_bytes": len(payload)}


PIN_FLAGS: tuple[tuple[str, str], ...] = (
    ("producer-source", PRODUCER_OWNERS[0].sha256), ("producer-protocol", PRODUCER_OWNERS[1].sha256), ("producer-contract", PRODUCER_OWNERS[2].sha256),
    ("publication-source", PUBLICATION_OWNERS[0].sha256), ("publication-protocol", PUBLICATION_OWNERS[1].sha256), ("publication-contract", PUBLICATION_OWNERS[2].sha256),
    ("build-source", C15_OWNERS[0].sha256), ("build-protocol", C15_OWNERS[1].sha256), ("build-contract", C15_OWNERS[2].sha256), ("build-archive", C15_OWNERS[3].sha256), ("build-receipt", C15_OWNERS[4].sha256),
    ("v29-renderer", OVERVIEW_OWNERS[0].sha256), ("v29-inputs", OVERVIEW_OWNERS[1].sha256), ("v29-summary", OVERVIEW_OWNERS[2].sha256), ("v29-svg", OVERVIEW_OWNERS[3].sha256),
    ("native-engine", C15_NATIVE_SHA256), ("native-bridge", C15_NATIVE_SHA256),
)


def worker_arguments(options: argparse.Namespace, name: str, active: dict[str, Any]) -> list[str]:
    arguments = [ORACLE_PYTHON, "-I", "-B", str(ROOT / SOURCE_PATH), "--worker", "--source-sha256", options.source_sha256, "--protocol-sha256", options.protocol_sha256, "--contract-sha256", options.contract_sha256, "--family", FAMILY, "--label", LABEL, "--activation-root", PUBLIC_ROOT, "--build-root", BUILD_ROOT, "--suite", name, "--activation-report-sha256", active["activation_owner"]["sha256"], "--activation-receipt-sha256", active["receipt_owner"]["sha256"], "--recovery-journal-sha256", active["journal_owner"]["sha256"]]
    for flag, value in PIN_FLAGS:
        arguments.extend(("--" + flag + "-sha256", value))
    arguments.extend(("--native-engine-bytes", str(C15_NATIVE_BYTES), "--native-bridge-bytes", str(C15_NATIVE_BYTES)))
    return arguments


def execute_worker(options: argparse.Namespace, name: str, count: int, active: dict[str, Any]) -> dict[str, Any]:
    arguments = worker_arguments(options, name, active)
    child = subprocess.Popen(arguments, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeout = False
    try:
        stdout, stderr = child.communicate(timeout=3600)
    except subprocess.TimeoutExpired:
        timeout = True
        child.kill()
        stdout, stderr = child.communicate()
    except BaseException:
        if child.poll() is None:
            child.kill()
        child.communicate()
        raise
    require(type(stdout) is bytes and type(stderr) is bytes and len(stdout) <= MAX_WORKER_STDOUT and len(stderr) <= MAX_WORKER_STDERR, "preserve every bounded complete original worker output")
    process = {"argv": arguments, "pid": child.pid, "returncode": child.returncode, "timed_out": timeout, "stdout": encode_stream(stdout), "stderr": encode_stream(stderr), "actual_worker_processes": 1}
    observed: dict[str, Any] | None = None
    decoding_failure: dict[str, Any] | None = None
    try:
        observed = strict_document(stdout, "actual original C15 worker output", maximum=MAX_WORKER_STDOUT)
    except Exception as exc:
        decoding_failure = error_record(exc)
    complete = (type(observed) is dict and observed.get("schema") == SCHEMA + "-actual-original-worker" and observed.get("candidate_family") == FAMILY and observed.get("label") == LABEL and observed.get("suite") == name and observed.get("case_execution_denominator") == count and observed.get("original_observer_source_sha256") == PRODUCER_OWNERS[0].sha256 and observed.get("actual_c15_build_archive_sha256") == C15_OWNERS[3].sha256 and observed.get("native_engine_sha256") == C15_NATIVE_SHA256 and observed.get("native_bridge_sha256") == C15_NATIVE_SHA256 and observed.get("all_original_records_and_mismatches_preserved") is True and observed.get("actual_candidate_workers") == 1 and observed.get("holdout") == "NOT OPENED" and observed.get("status") in ("PASS", "FAIL") and type(observed.get("mismatch_count")) is int and observed["mismatch_count"] >= 0 and not timeout and child.returncode == (0 if observed["status"] == "PASS" else 1))
    if complete:
        assert observed is not None
        return {"suite": name, "status": observed["status"], "case_execution_denominator": count, "failure_class": observed["failure_class"], "mismatch_count": observed["mismatch_count"], "actual_worker_started": True, "actual_worker_processes": 1, "all_original_records_and_mismatches_preserved": True, "original_observer": observed, "process": process}
    return {"suite": name, "status": "FAIL", "case_execution_denominator": count, "failure_class": "CANDIDATE EXECUTION FAILURE" if type(observed) is dict and observed.get("failure_class") == "CANDIDATE EXECUTION FAILURE" else "INFRASTRUCTURE FAILURE", "mismatch_count": "NOT MEASURED", "actual_worker_started": True, "actual_worker_processes": 1, "all_original_records_and_mismatches_preserved": False, "worker_decoding_failure": decoding_failure, "actual_worker_output": observed, "process": process}


def failed_worker(name: str, count: int, error: BaseException) -> dict[str, Any]:
    return {"suite": name, "status": "FAIL", "case_execution_denominator": count, "failure_class": "INFRASTRUCTURE FAILURE", "mismatch_count": "NOT MEASURED", "actual_worker_started": False, "actual_worker_processes": 0, "all_original_records_and_mismatches_preserved": False, "error": error_record(error), "process": None}


def load_actual_publication(source: bytes) -> types.ModuleType:
    require(sha256_bytes(source) == PUBLICATION_OWNERS[0].sha256, "authenticate the immutable exact streaming publication source")
    name = "_rebar_owned_c_v4_frozen_streaming_publication_" + PUBLICATION_OWNERS[0].sha256[:24]
    existing = sys.modules.get(name)
    if existing is not None:
        require(type(existing) is types.ModuleType and os.path.abspath(str(existing.__file__)) == str(ROOT / PUBLICATION_OWNERS[0].relative_path), "reject a substituted actual streaming publisher")
        return existing
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / PUBLICATION_OWNERS[0].relative_path)
    module.__package__ = ""
    sys.modules[name] = module
    try:
        exec(compile(source, module.__file__, "exec", dont_inherit=True), module.__dict__)
        require(callable(getattr(module, "open_evidence_directory", None)) and callable(getattr(module, "write_streamed_archive", None)), "load only the frozen low-level streaming publication primitives")
        current, _ = read_owned(PUBLICATION_OWNERS[0])
        require(current == source, "reject a changed streaming publication source")
        return module
    except BaseException:
        sys.modules.pop(name, None)
        raise


def evidence_names(*, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "select one exact C-specific immutable evidence stem")
    stem = "repaired-c-original-campaign-v4-c-" + LABEL
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_fresh_c_evidence(publication: types.ModuleType) -> None:
    directory = publication.open_evidence_directory()
    try:
        for failure in (False, True):
            for name in evidence_names(failure=failure):
                try:
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise GateError("never replace an existing C15 campaign archive or receipt: " + name)
    finally:
        os.close(directory)


def write_evidence_receipt(publication: types.ModuleType, name: str, document: dict[str, Any]) -> dict[str, Any]:
    require(type(name) is str and bool(name) and "/" not in name, "publish only one exclusive first-party C campaign receipt")
    payload = canonical_json(document)
    directory = publication.open_evidence_directory()
    descriptor: int | None = None
    try:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=directory)
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid() and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600, "require an exclusive owner-only C15 receipt inode")
        write_all(descriptor, payload)
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino) and after.st_size == len(payload), "reject a truncated or replaced C15 evidence receipt")
        os.close(descriptor)
        descriptor = None
        os.fsync(directory)
        relative = "oracle/phase2/evidence/" + name
        reread, owner = read_owned(Owner(relative, sha256_bytes(payload), len(payload)))
        require(reread == payload and (owner["device"], owner["inode"]) == (after.st_dev, after.st_ino), "reread all bytes from the exact durable C15 receipt inode")
        owner.update({"exclusive_creation": True, "same_inode_readback_verified": True, "file_fsync_completed": True, "directory_fsync_completed": True})
        return owner
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def preserve_campaign(report: dict[str, Any], publication: types.ModuleType) -> dict[str, Any]:
    require(report.get("schema") == SCHEMA + "-complete-original-campaign" and report.get("status") in ("PASS", "FAIL") and report.get("family") == FAMILY and report.get("label") == LABEL and report.get("suite_count") == SUITE_COUNT and report.get("case_execution_denominator") == P0_CASES and report.get("named_private_waiver_count") == PRIVATE_WAIVERS and type(report.get("suite_results")) is list and len(report["suite_results"]) == SUITE_COUNT and [(item.get("suite"), item.get("case_execution_denominator")) for item in report["suite_results"]] == list(SUITES) and report.get("exact_original_native_restored") is True and report.get("restoration_verified_before_publication") is True and report.get("original_source_targets_modified") == 0 and report.get("source_family_spec_rebound") is False and report.get("holdout") == "NOT OPENED", "never publish an incomplete original denominator or an unrestored native inode")
    original = exact_original_native()
    require(report.get("restored_original_native") == original, "reauthenticate the exact original native inode before publication")
    archive_name, receipt_name = evidence_names(failure=report["status"] == "FAIL")
    directory = publication.open_evidence_directory()
    try:
        archive, stream = publication.write_streamed_archive(report, archive_name, directory)
    finally:
        os.close(directory)
    require(archive.get("relative") == archive_name and archive.get("mode") == 0o600 and archive.get("exclusive_creation") is True and archive.get("same_inode_readback_verified") is True and archive.get("streaming_readback_verified") is True and archive.get("file_fsync_completed") is True and archive.get("directory_fsync_completed") is True and stream.get("gzip_mtime") == 0 and stream.get("gzip_single_member") is True, "publish only a complete durable first-party C-specific streamed original archive")
    receipt = {"schema": SCHEMA + "-durable-publication-receipt", "status": "PASS", "publication_status": "PASS", "publication_pass_means": "DURABLE PUBLICATION ONLY", "candidate_status": report["status"], "family": FAMILY, "label": LABEL, "archive": archive, "archive_relative": "oracle/phase2/evidence/" + archive_name, "archive_sha256": archive["sha256"], "archive_bytes": archive["size_bytes"], "campaign_source_sha256": report["campaign_source_sha256"], "campaign_protocol_sha256": report["campaign_protocol_sha256"], "campaign_contract_sha256": report["campaign_contract_sha256"], "original_producer_source_sha256": PRODUCER_OWNERS[0].sha256, "original_producer_protocol_sha256": PRODUCER_OWNERS[1].sha256, "original_producer_contract_sha256": PRODUCER_OWNERS[2].sha256, "actual_c15_build_archive_sha256": C15_OWNERS[3].sha256, "actual_c15_build_receipt_sha256": C15_OWNERS[4].sha256, "uncompressed_sha256": stream["uncompressed_sha256"], "uncompressed_bytes": stream["uncompressed_bytes"], "uncompressed_chunk_count": stream["uncompressed_chunk_count"], "suite_count": SUITE_COUNT, "case_execution_denominator": P0_CASES, "named_private_waiver_count": PRIVATE_WAIVERS, "completed_suite_count": report["completed_suite_count"], "actual_candidate_workers": report["actual_candidate_workers"], "verified_passing_case_count": report["verified_passing_case_count"], "semantic_mismatch_count": report["semantic_mismatch_count"], "infrastructure_failure_count": report["infrastructure_failure_count"], "candidate_execution_failure_count": report["candidate_execution_failure_count"], "candidate_qualified": report["candidate_qualified"], "public_recovery_root": PUBLIC_ROOT, "build_root": BUILD_ROOT, "recovery_journal_sha256": report["recovery_journal_sha256"], "exact_original_native_restored": True, "restored_original_native": original, "restoration_verified_before_publication": True, "original_source_targets_modified": 0, "source_family_spec_rebound": False, "legacy_original_producer_controller_invoked": False, "legacy_publisher_family_dispatch_invoked": False, "repository_evidence_owner_count_before_publication": CURRENT_OVERVIEW_OWNERS, "authenticated_reference_count_before_publication": CURRENT_OVERVIEW_REFERENCES, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}
    receipt_owner = write_evidence_receipt(publication, receipt_name, receipt)
    require((archive["device"], archive["inode"]) != (receipt_owner["device"], receipt_owner["inode"]) and exact_original_native() == original, "prove independent durable C evidence and the exact restored original inode")
    return {"schema": SCHEMA + "-published-complete-original-campaign", "status": report["status"], "publication_status": "PASS", "family": FAMILY, "label": LABEL, "archive": archive, "receipt": receipt_owner, "suite_count": SUITE_COUNT, "case_execution_denominator": P0_CASES, "completed_suite_count": report["completed_suite_count"], "actual_candidate_workers": report["actual_candidate_workers"], "verified_passing_case_count": report["verified_passing_case_count"], "semantic_mismatch_count": report["semantic_mismatch_count"], "infrastructure_failure_count": report["infrastructure_failure_count"], "candidate_execution_failure_count": report["candidate_execution_failure_count"], "candidate_qualified": report["candidate_qualified"], "public_recovery_root": PUBLIC_ROOT, "recovery_journal_sha256": report["recovery_journal_sha256"], "exact_original_native_restored": True, "restored_original_native": original, "legacy_original_producer_controller_invoked": False, "legacy_publisher_family_dispatch_invoked": False, "holdout": "NOT OPENED", "performance": "NOT MEASURED", "memory": "NOT MEASURED"}


def run_campaign(options: argparse.Namespace) -> dict[str, Any]:
    validate_actual_authorization(options)
    context, retained = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256, retain=True)
    require(context.get("status") == "PASS", "verify the complete original and C15 frozen context before any actual activation")
    publication = load_actual_publication(retained["publication_source"])
    ensure_fresh_c_evidence(publication)
    rows: list[dict[str, Any]] = []
    baseline: dict[str, Any] | None = None
    active: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    controller_error: dict[str, Any] | None = None
    graceful: dict[str, Any] | None = None
    directory: int | None = None
    lock: int | None = None
    with installed_signal_handlers():
        try:
            with blocked_controller_signals():
                directory, lock = open_recovery_lock(options.activation_root, create=True)
            baseline = exact_original_native()
            active = activate_native(options)
            for name, count in SUITES:
                try:
                    rows.append(execute_worker(options, name, count, active))
                except ControllerSignal:
                    raise
                except Exception as exc:
                    rows.append(failed_worker(name, count, exc))
        except ControllerSignal as exc:
            controller_error = error_record(exc)
            graceful = {"schema": SCHEMA + "-graceful-controller-signal", "status": "FAIL", "signal_name": exc.signal_name, "signal_number": exc.signum, "candidate_matching_result": "NOT MEASURED", "holdout": "NOT OPENED"}
            done = {row["suite"] for row in rows}
            for name, count in SUITES:
                if name not in done:
                    rows.append(failed_worker(name, count, exc))
        except Exception as exc:
            controller_error = error_record(exc)
            done = {row["suite"] for row in rows}
            for name, count in SUITES:
                if name not in done:
                    rows.append(failed_worker(name, count, exc))
        finally:
            try:
                if active is not None:
                    with blocked_controller_signals():
                        restoration = restore_native(active["root"], active["journal"], active["journal_owner"]["sha256"])
                if baseline is not None:
                    with blocked_controller_signals():
                        require(exact_original_native() == baseline, "restore the exact original C native inode before leaving the actual campaign")
            finally:
                if lock is not None:
                    os.close(lock)
                if directory is not None:
                    os.close(directory)
    require(baseline is not None and active is not None and restoration is not None, "never publish without genuine activation and a fully restored original native inode")
    order = {name: index for index, (name, _) in enumerate(SUITES)}
    rows.sort(key=lambda row: order[row["suite"]])
    require(len(rows) == SUITE_COUNT and [(row.get("suite"), row.get("case_execution_denominator")) for row in rows] == list(SUITES), "retain exactly thirteen original suite slots and all 31,237 obligations")
    pids = [row["process"]["pid"] for row in rows if row.get("actual_worker_started") is True and type(row.get("process")) is dict]
    require(len(pids) == len(set(pids)), "never count one actual worker process as multiple candidate families or suites")
    completed = sum(row.get("all_original_records_and_mismatches_preserved") is True for row in rows)
    passed = sum(count for (name, count), row in zip(SUITES, rows, strict=True) if row.get("suite") == name and row.get("failure_class") == "PASS" and row.get("mismatch_count") == 0 and row.get("all_original_records_and_mismatches_preserved") is True)
    mismatches = sum(row["mismatch_count"] for row in rows if row.get("failure_class") == "SEMANTIC MISMATCH" and type(row.get("mismatch_count")) is int)
    infrastructure = sum(row.get("failure_class") == "INFRASTRUCTURE FAILURE" for row in rows) + int(controller_error is not None)
    executions = sum(row.get("failure_class") == "CANDIDATE EXECUTION FAILURE" for row in rows)
    qualified = len(pids) == SUITE_COUNT and completed == SUITE_COUNT and passed == P0_CASES and mismatches == 0 and infrastructure == 0 and executions == 0 and graceful is None and all(row.get("actual_worker_processes") == 1 and row.get("all_original_records_and_mismatches_preserved") is True for row in rows)
    original = exact_original_native()
    require(original == baseline and restoration.get("exact_original_inode_restored") is True, "reauthenticate the exact restored C native before any publication")
    report = {"schema": SCHEMA + "-complete-original-campaign", "status": "PASS" if qualified else "FAIL", "family": FAMILY, "label": LABEL, "campaign_source_sha256": options.source_sha256, "campaign_protocol_sha256": options.protocol_sha256, "campaign_contract_sha256": options.contract_sha256, "original_producer_source_sha256": PRODUCER_OWNERS[0].sha256, "original_producer_protocol_sha256": PRODUCER_OWNERS[1].sha256, "original_producer_contract_sha256": PRODUCER_OWNERS[2].sha256, "actual_c15_build_source_sha256": C15_OWNERS[0].sha256, "actual_c15_build_protocol_sha256": C15_OWNERS[1].sha256, "actual_c15_build_contract_sha256": C15_OWNERS[2].sha256, "actual_c15_build_archive_sha256": C15_OWNERS[3].sha256, "actual_c15_build_receipt_sha256": C15_OWNERS[4].sha256, "actual_c15_build_process_count": 14, "native_engine_sha256": C15_NATIVE_SHA256, "native_bridge_sha256": C15_NATIVE_SHA256, "native_engine_bytes": C15_NATIVE_BYTES, "native_bridge_bytes": C15_NATIVE_BYTES, "suite_count": SUITE_COUNT, "case_execution_denominator": P0_CASES, "named_private_waiver_count": PRIVATE_WAIVERS, "suite_results": rows, "completed_suite_count": completed, "actual_candidate_workers": len(pids), "actual_worker_process_ids": pids, "verified_passing_case_count": passed, "semantic_mismatch_count": mismatches if completed == SUITE_COUNT else "NOT MEASURED", "infrastructure_failure_count": infrastructure, "candidate_execution_failure_count": executions, "candidate_qualified": qualified, "public_recovery_root": PUBLIC_ROOT, "build_root": BUILD_ROOT, "recovery_journal_sha256": active["journal_owner"]["sha256"], "restoration": restoration, "restored_original_native": original, "exact_original_native_restored": True, "restoration_verified_before_publication": True, "original_source_targets_modified": 0, "source_family_spec_rebound": False, "combined_native_engine_bridge": True, "cross_device_rename_performed": False, "cross_device_link_performed": False, "legacy_original_producer_controller_invoked": False, "legacy_publisher_family_dispatch_invoked": False, "repository_evidence_owner_count_before_publication": CURRENT_OVERVIEW_OWNERS, "authenticated_reference_count_before_publication": CURRENT_OVERVIEW_REFERENCES, "historical_c_semantic_mismatch_count": 1262, "historical_rust_semantic_mismatch_count": 1087, "historical_zig_semantic_mismatch_count": 2172, "historical_zig_preflight_candidate_workers": 0, "controller_failure": controller_error, "graceful_signal": graceful, "group_atomic": False, "sigkill_automatically_recovered": False, "power_failure_automatically_recovered": False, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}
    return preserve_campaign(report, publication)


def recover_native(options: argparse.Namespace) -> dict[str, Any]:
    validate_actual_authorization(options)
    require(options.recovery_journal_sha256 is not None, "independently caller-pin the exact public original-native recovery journal")
    context, _ = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256)
    require(context.get("status") == "PASS", "authenticate every immutable original owner before recovery")
    directory: int | None = None
    lock: int | None = None
    with installed_signal_handlers():
        try:
            with blocked_controller_signals():
                directory, lock = open_recovery_lock(options.activation_root, create=False)
                journal, owner = read_private(options.activation_root, JOURNAL_NAME, options.recovery_journal_sha256)
                require(owner["sha256"] == options.recovery_journal_sha256, "authenticate the caller-pinned exact durable recovery journal")
                result = restore_native(options.activation_root, journal, owner["sha256"])
                require(result.get("exact_original_inode_restored") is True and result.get("original_native") == exact_original_native(), "complete exact original-native public recovery")
                return result
        finally:
            if lock is not None:
                os.close(lock)
            if directory is not None:
                os.close(directory)


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    require(all(type(value) is str for value in values), "require unambiguous literal controller arguments")
    flags = [value for value in values if value.startswith("--")]
    require(len(flags) == len(set(flags)), "reject repeated or ambiguous actual authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--verify-frozen-context", action="store_true")
    mode.add_argument("--render-contract", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--worker", action="store_true")
    mode.add_argument("--recover", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    for name in ("family", "label", "activation-root", "build-root", "suite"):
        parser.add_argument("--" + name)
    for name in ("activation-report", "activation-receipt", "recovery-journal"):
        parser.add_argument("--" + name + "-sha256")
    for name, _ in PIN_FLAGS:
        parser.add_argument("--" + name + "-sha256")
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "version 4 controller source")
    checked_digest(options.protocol_sha256, "version 4 public protocol")
    digest_names = tuple(name.replace("-", "_") + "_sha256" for name, _ in PIN_FLAGS)
    for name in ("contract_sha256", "activation_report_sha256", "activation_receipt_sha256", "recovery_journal_sha256", *digest_names):
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    actual_names = ("family", "label", "activation_root", "build_root", "suite", "activation_report_sha256", "activation_receipt_sha256", "recovery_journal_sha256", *digest_names, "native_engine_bytes", "native_bridge_bytes")
    if options.render_contract:
        require(options.contract_sha256 is None and all(getattr(options, name) is None for name in actual_names), "contract rendering may not authorize source owners, candidates, recovery, or workers")
        return options
    require(options.contract_sha256 is not None, "independently caller-pin the exact machine contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in actual_names), "source-only gates cannot authorize actual handlers, recovery, targets, build roots, or workers")
        return options
    mandatory = ("family", "label", "activation_root", "build_root", *digest_names, "native_engine_bytes", "native_bridge_bytes")
    require(all(getattr(options, name) is not None for name in mandatory), "require every independently caller-pinned actual C15 and original owner")
    if options.worker:
        require(options.suite is not None and options.activation_report_sha256 is not None and options.activation_receipt_sha256 is not None and options.recovery_journal_sha256 is not None, "independently authorize exactly one journaled original C suite worker")
    elif options.recover:
        require(options.recovery_journal_sha256 is not None and options.suite is None and options.activation_report_sha256 is None and options.activation_receipt_sha256 is None, "require only an independently caller-pinned public native-recovery journal")
    else:
        require(options.suite is None and options.activation_report_sha256 is None and options.activation_receipt_sha256 is None and options.recovery_journal_sha256 is None, "a fresh campaign must announce and create its own exclusive recovery journal")
    return options


def infrastructure_failure(options: argparse.Namespace, error: Exception, mode: str) -> dict[str, Any]:
    return {"schema": SCHEMA + "-controller-infrastructure-failure", "status": "FAIL", "failure_class": "CONTROLLER INFRASTRUCTURE FAILURE", "family": FAMILY, "label": LABEL, "mode": mode, "source_sha256": options.source_sha256, "protocol_sha256": options.protocol_sha256, "contract_sha256": options.contract_sha256, "error": error_record(error), "public_recovery_root": PUBLIC_ROOT, "build_root": BUILD_ROOT, "durable_failure_publication": "NOT VERIFIED", "exact_original_native_restored": "NOT VERIFIED", "candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "holdout": "NOT OPENED", "performance": "NOT MEASURED", "sigkill_automatically_recovered": False, "power_failure_automatically_recovered": False}


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.render_contract:
        result = protocol_document(options.source_sha256, options.protocol_sha256)
        code = 0
    elif options.self_test:
        result = self_test(options.source_sha256, options.protocol_sha256, options.contract_sha256)
        code = 0
    elif options.verify_frozen_context:
        result, _ = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256)
        code = 0
    elif options.worker:
        try:
            result = run_worker(options)
            code = 0 if result.get("status") == "PASS" else 1
        except Exception as exc:
            result = infrastructure_failure(options, exc, "--worker")
            code = 1
    elif options.recover:
        try:
            result = recover_native(options)
            code = 0 if result.get("status") == "PASS" else 1
        except Exception as exc:
            result = infrastructure_failure(options, exc, "--recover")
            code = 1
    else:
        try:
            result = run_campaign(options)
            code = 0 if result.get("status") == "PASS" else 1
        except Exception as exc:
            result = infrastructure_failure(options, exc, "--run")
            code = 1
    sys.stdout.buffer.write(canonical_json(result))
    sys.stdout.buffer.flush()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
