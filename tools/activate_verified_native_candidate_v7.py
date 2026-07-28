#!/usr/bin/env python3
"""Normalize genuine mature owner metadata for immutable Zig V6 activation.

Verification is strictly source-only. Actual activation and recovery require
separate explicit authorization. The published V6 source, two-role hardlink
journal, original inode restoration, and failed V1 attempt are never rewritten.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import ctypes
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
from typing import Any, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v7.py"
PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V7.md"
CONTRACT_RELATIVE = "oracle/phase2/verified-native-activation-v7.json"
SCHEMA = "rebar-phase2-verified-native-activation-v7"
CONTRACT_SCHEMA = SCHEMA + "-owner-normalization-source-freeze"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
FAMILY = "zig"
BUILD_LABEL = "phase2-v11-zig-scanner"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
PREDECESSOR = {
    "source": (
        "tools/activate_verified_native_candidate_v6.py",
        "d3a9b08c1bf7e3408719a0e92b8c1965aa6160dd2e18ab1501bb8662aaf8e4a1",
        107982,
    ),
    "protocol": (
        "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V6.md",
        "0e736d575835fa22388841a527e22b62eef1ddf39eac9415bd7c518ba985b1d0",
        6688,
    ),
    "contract": (
        "oracle/phase2/verified-native-activation-v6.json",
        "e0d486cc6d621e963f8af5db1c4f7a47d590ad679837db1f53e11d05b670332e",
        12902,
    ),
}
FAILED_V1 = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v1.py",
        "ff4bc83173930c193de5984659aa6e8aca1848496d06f3d3dca3c28294c37c90",
        92313,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V1.md",
        "974c1cc09511c7a119a2ea0f59fab8c39e8d1887c948df19657de2458b5b9d67",
        5108,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v1.json",
        "f3f1bdfea41b8b4d5bce22b2b236c76f653e97268e500b951fbef262052718f0",
        9563,
    ),
}
MATURE = {
    "source": (
        "tools/activate_verified_native_candidate_v2.py",
        "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218",
        205006,
    ),
    "protocol": (
        "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md",
        "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529",
        10346,
    ),
}
ORIGINAL_PRODUCER = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v3.py",
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
        195555,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
        5522,
    ),
    "contract": (
        "oracle/phase2/six-family-p0-producer-v3.json",
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
        26909,
    ),
}
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
)
PHASE_ONE = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
BUILD_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz",
    "e4a1f369b647f588ac5b12585f7d0e30c4ee3409adc88f660081fb7a59a8df5c",
    48246,
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-zig-phase2-v11-zig-scanner-publication-receipt.json",
    "d53766d0dad571f8b72288cece15fb1ad0892db32c3b3b6b512027db94ca4fcc",
    1683,
)
ENGINE_SHA256 = "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
ENGINE_BYTES = 108888
BRIDGE_SHA256 = "75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681"
BRIDGE_BYTES = 133656
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
    ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)
MATURE_OWNER_FIELDS = (
    "relative", "path", "sha256", "size_bytes", "device", "inode", "mode",
)
NORMALIZED_OWNER_FIELDS = MATURE_OWNER_FIELDS + ("nlink", "uid")


class ActivationError(Exception):
    """Genuine normalized owner or original V6 activation is not proven."""


class SourceOnlyEffect(ActivationError):
    """A source-only normalization control attempted an external effect."""


def require(valid: Any, message: str) -> None:
    if valid is not True:
        raise ActivationError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value),
            "require one exact lowercase independently frozen SHA-256: " + label)
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and not value.startswith("/")
            and "\\" not in value and "\x00" not in value
            and all(item not in ("", ".", "..") for item in value.split("/")),
            "reject absolute, broad, parent, symlinked or ambiguous paths")
    return value


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete authentic byte streams")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=True, allow_nan=False,
                          sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise ActivationError("reject noncanonical V7 source evidence") from error


def strict_document(raw: bytes, label: str) -> dict[str, Any]:
    def unique(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            require(type(key) is str and key not in result,
                    "reject duplicate JSON keys in " + label)
            result[key] = value
        return result

    def invalid(value: str) -> Any:
        raise ActivationError("reject nonfinite JSON in " + label)

    try:
        document = json.loads(raw, object_pairs_hook=unique,
                              parse_constant=invalid)
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise ActivationError("reject invalid V7 evidence: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "require exact canonical frozen evidence: " + label)
    return document


def owner_record(item: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": item[0], "sha256": item[1], "bytes": item[2]}


def mapped_owners(group: dict[str, tuple[str, str, int]]) -> dict[str, Any]:
    return {name: owner_record(row) for name, row in sorted(group.items())}


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only isolated pinned no-bytecode stable CPython 3.14.6")


def read_source_owner(
    relative: str, expected: str, size: int, *,
    maximum: int = MAX_SOURCE_BYTES,
) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    checked_digest(expected, relative)
    require(type(size) is int and 0 < size <= maximum,
            "bound every exact V7 source-freeze support owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        parent = os.open(str(ROOT), directory_flags)
        opened.append(parent)
        parts = relative.split("/")
        for component in parts[:-1]:
            parent = os.open(component, directory_flags, dir_fd=parent)
            opened.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a redirected V7 support owner ancestor")
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode)
                and first.st_nlink == 1 and first.st_uid == os.geteuid()
                and first.st_size == size
                and (first.st_dev, first.st_ino, first.st_size)
                == (named.st_dev, named.st_ino, named.st_size),
                "reject linked, replaced, foreign or resized V7 support: "
                + relative)
        remaining = size
        blocks: list[bytes] = []
        while remaining:
            part = os.read(descriptor, min(remaining, 1048576))
            require(type(part) is bytes and bool(part),
                    "reject truncated V7 source owner: " + relative)
            remaining -= len(part)
            blocks.append(part)
        require(os.read(descriptor, 1) == b"",
                "reject hidden trailing V7 source-owner bytes")
        raw = b"".join(blocks)
        final = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
                == (final.st_dev, final.st_ino, final.st_size,
                    final.st_mtime_ns, final.st_ctime_ns)
                and (final.st_dev, final.st_ino, final.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and sha256(raw) == expected,
                "reject TOCTOU or false digest in V7 source owner: " + relative)
        return raw, {
            "relative": relative, "path": str(ROOT / relative),
            "sha256": expected, "size_bytes": final.st_size,
            "device": final.st_dev, "inode": final.st_ino,
            "mode": stat.S_IMODE(final.st_mode),
            "nlink": final.st_nlink, "uid": final.st_uid,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def source_effects() -> dict[str, Any]:
    return {
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "canonical_target_links": 0, "canonical_target_replacements": 0,
        "source_freeze_original_targets_read": 0,
        "source_freeze_original_targets_statted": 0,
        "source_freeze_original_targets_modified": 0,
        "candidate_imports": 0, "candidate_processes_started": 0,
        "native_activations_started": 0, "native_recoveries_started": 0,
        "native_libraries_loaded": 0, "native_builds_started": 0,
        "compiler_processes_started": 0, "network_requests": 0,
        "threads_started": 0, "private_activation_roots_opened": 0,
        "workspace_mutations": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False, "winner_selected": False,
    }


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "V7 owner-normalization source")
    checked_digest(protocol_pin, "V7 owner-normalization protocol")
    return {
        "schema": CONTRACT_SCHEMA, "version": 7,
        "phase": "CANDIDATES", "family": FAMILY,
        "status": "SOURCE FROZEN; NATIVE ACTIVATION NOT RUN",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "pinned_cpython": {"path": PYTHON, "sha256": PYTHON_SHA256,
                           "version": "3.14.6"},
        "goal": owner_record(GOAL), "phase_one": owner_record(PHASE_ONE),
        "unchanged_original_v3_producer": mapped_owners(ORIGINAL_PRODUCER),
        "unchanged_actual_v6_predecessor": {
            "owners": mapped_owners(PREDECESSOR),
            "source_bytes_not_modified": True,
            "source_loaded_only_after_exact_digest_verification": True,
            "complete_two_role_journal_inherited": True,
            "complete_same_device_original_hardlinks_inherited": True,
            "complete_reverse_order_recovery_inherited": True,
            "one_mature_owner_boundary_corrected": True,
            "semantic_parser_compiler_or_executor_changed": False,
        },
        "unchanged_mature_v2_primitives": {
            "owners": mapped_owners(MATURE),
            "documented_original_owner_fields": list(MATURE_OWNER_FIELDS),
            "original_source_modified": False,
            "original_returned_nlink": False,
            "original_returned_uid": False,
        },
        "actual_first_v1_campaign_attempt": {
            "owners": mapped_owners(FAILED_V1),
            "attempt_status": "FAIL",
            "failure_class": "INFRASTRUCTURE FAILURE",
            "failure_stage": "PRE-ACTIVATION ORIGINAL ENGINE OWNER METADATA",
            "failure_type": "ActivationError",
            "failure_message":
                "refuse an absent, linked, altered, or substituted original Zig engine inode",
            "root_cause":
                "mature V2 owner records omit genuine nlink and uid; V6 "
                "requires both fields before native activation",
            "actual_candidate_worker_count": 0,
            "actual_native_activation_count": 0,
            "actual_promotion_count": 0,
            "actual_restoration_count": 0,
            "original_matching": "NOT MEASURED",
            "candidate_qualified": False,
            "candidate_semantic_mismatch_count": "NOT MEASURED",
            "completed_original_suite_count": 0,
            "completed_case_execution_count": 0,
            "exact_canonical_read_count": "NOT RECORDED",
            "original_native_mutation_count": 0,
            "existing_campaign_archive": "NOT PUBLISHED",
            "existing_campaign_receipt": "NOT PUBLISHED",
            "actual_stdout_bytes": "NOT RECORDED",
            "actual_stderr_bytes": "NOT RECORDED",
            "actual_process_pid": "NOT RECORDED",
            "failure_evidence_preservation":
                "OWNED BY A SEPARATE IMMUTABLE FAILURE RECORDER",
            "actual_failure_removed_or_rewritten": False,
        },
        "published_v25_history": {
            "authoritative_evidence_owner_count": 139,
            "authenticated_reference_count": 144,
            "actual_c_candidate_workers": 13,
            "actual_c_semantic_mismatch_count": 1262,
            "actual_c_verified_passing_case_executions": 7325,
            "actual_rust_compiler_process_count": 28,
            "actual_rust_public_source_repairs": 2,
            "actual_rust_bridge_source_repairs": 2,
            "historical_original_zig_mismatch_count": 1764,
            "qualified_candidate_count": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
        },
        "actual_zig_v11_build": {
            "label": BUILD_LABEL, "archive": owner_record(BUILD_ARCHIVE),
            "receipt": owner_record(BUILD_RECEIPT),
            "actual_compiler_process_count": 26,
            "independent_source_phase_count": 2,
            "historical_evidence_owner_count_at_build": 135,
            "historical_reference_count_at_build": 140,
            "native_roles": [
                {
                    "role": "engine", "path": "candidates/_zig_probe.so",
                    "sha256": ENGINE_SHA256, "bytes": ENGINE_BYTES,
                    "original_device": 2064, "original_inode": 431260,
                    "original_mode": "0700", "original_nlink": 1,
                    "original_uid": 1000,
                },
                {
                    "role": "bridge",
                    "path": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                    "sha256": BRIDGE_SHA256, "bytes": BRIDGE_BYTES,
                    "original_device": 2064, "original_inode": 431274,
                    "original_mode": "0700", "original_nlink": 1,
                    "original_uid": 1000,
                },
            ],
            "original_native_targets_inspected_by_source_freeze": False,
        },
        "owner_normalization": {
            "mature_owner_fields": list(MATURE_OWNER_FIELDS),
            "normalized_owner_fields": list(NORMALIZED_OWNER_FIELDS),
            "one_mature_read_boundary": True,
            "stat_values_are_descriptor_observed": True,
            "require_o_nofollow_on_each_parent_and_file": True,
            "bind_named_and_descriptor_device_and_inode": True,
            "reauthenticate_complete_original_content": True,
            "require_exact_original_hash": True,
            "require_exact_owner_size": True,
            "require_exact_owner_mode": True,
            "require_actual_owner_uid": True,
            "require_actual_owner_nlink": True,
            "require_owner_only_regular_single_link": True,
            "reject_toc_tou": True,
            "reject_symlink": True,
            "reject_swapped_inode": True,
            "reject_short_or_changed_content": True,
            "normalize_original_user_targets": True,
            "normalize_private_source_built_native_phases": True,
            "normalize_promoted_native_targets": True,
            "normalize_original_inode_restoration": True,
            "invent_file_metadata": False,
            "use_path_only_stat": False,
        },
        "oracle": {
            "suite_count": 13,
            "case_execution_denominator": 31237,
            "named_private_waiver_count": 13,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "original_v1_attempt_was_not_a_correctness_result": True,
            "candidate_correctness": "NOT MEASURED",
        },
        "activation_policy": {
            "accepted_family": FAMILY,
            "explicit_operation_required": True,
            "canonical_target_count": 2,
            "fixed_role_order": ["engine", "bridge"],
            "fixed_restoration_order": ["bridge", "engine"],
            "exact_original_inode_hardlink_backup":
                "ADJACENT SAME-DEVICE HARDLINK",
            "preserve_complete_immutable_v6_journal": True,
            "promotion_intention_before_replacement": True,
            "each_file_replacement_individually_atomic": True,
            "group_atomic": False,
            "reportless_reverse_order_recovery": True,
            "restore_exact_device_inode_mode_bytes_uid_and_nlink": True,
            "source_only_private_root_access": "FORBIDDEN",
            "source_only_canonical_target_access": "FORBIDDEN",
            "c_native_target_touched": False,
            "rust_native_target_touched": False,
            "candidate_import": "FORBIDDEN",
            "external_regex_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "stdlib_regex_matching": "FORBIDDEN",
        },
        "source_only_effects": source_effects(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict and canonical(value)
            == canonical(protocol_document(source_pin, protocol_pin)),
            "reject altered V6 history, first failure, normalization or recovery")
    return value


def normalized_metadata(owner: Any, actual: Any,
                        current_uid: int) -> dict[str, Any]:
    require(type(owner) is dict and type(actual) is dict
            and type(current_uid) is int and current_uid >= 0
            and all(name in owner for name in MATURE_OWNER_FIELDS)
            and all(name in actual for name in
                    ("device", "inode", "size_bytes", "mode", "nlink", "uid"))
            and all(type(owner.get(name)) is int for name in
                    ("size_bytes", "device", "inode", "mode"))
            and all(type(actual.get(name)) is int for name in
                    ("size_bytes", "device", "inode", "mode", "nlink", "uid"))
            and owner["size_bytes"] > 0
            and actual["size_bytes"] == owner["size_bytes"]
            and actual["device"] == owner["device"]
            and actual["inode"] == owner["inode"]
            and actual["mode"] == owner["mode"]
            and actual["uid"] == current_uid
            and actual["nlink"] == 1,
            "refuse missing, fabricated, linked, foreign or changed mature metadata")
    checked_relative(owner["relative"])
    checked_digest(owner["sha256"], "normalized mature owner")
    require(type(owner["path"]) is str and owner["path"].startswith("/"),
            "bind normalized metadata to the exact mature absolute owner")
    result = dict(owner)
    result["nlink"] = actual["nlink"]
    result["uid"] = actual["uid"]
    return result


def normalize_mature_reader(mature: types.ModuleType) -> types.ModuleType:
    require(type(mature) is types.ModuleType
            and tuple(getattr(mature, "OWNER_FIELDS", ())) == MATURE_OWNER_FIELDS
            and callable(getattr(mature, "read_owned", None))
            and callable(getattr(mature, "open_root", None)),
            "authenticate the exact unchanged seven-field mature V2 boundary")
    original_reader = mature.read_owned

    def verified_read(
        root: str, relative: str, expected: str | None, *,
        maximum: int, exact_size: int | None = None,
        private: bool = False,
    ) -> tuple[bytes, dict[str, Any]]:
        raw, previous = original_reader(
            root, relative, expected, maximum=maximum,
            exact_size=exact_size, private=private)
        require(type(raw) is bytes and bool(raw) and type(previous) is dict
                and previous.get("relative") == relative
                and previous.get("path") == root + "/" + relative
                and previous.get("size_bytes") == len(raw)
                and previous.get("sha256") == sha256(raw),
                "retain exact complete bytes and true seven-field mature owner")
        if expected is not None:
            require(previous["sha256"] == checked_digest(expected, relative),
                    "bind descriptor normalization to the actual expected hash")
        if exact_size is not None:
            require(len(raw) == exact_size,
                    "bind descriptor normalization to the exact actual size")
        flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                 | getattr(os, "O_NOFOLLOW", 0))
        directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
        opened: list[int] = []
        try:
            parent = mature.open_root(root, private=private)
            opened.append(parent)
            parts = relative.split("/")
            for component in parts[:-1]:
                parent = os.open(component, directory_flags, dir_fd=parent)
                opened.append(parent)
                require(stat.S_ISDIR(os.fstat(parent).st_mode),
                        "reject redirected no-follow mature owner parent")
            descriptor = os.open(parts[-1], flags, dir_fd=parent)
            opened.append(descriptor)
            before = os.fstat(descriptor)
            named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            actual = {
                "device": before.st_dev,
                "inode": before.st_ino,
                "size_bytes": before.st_size,
                "mode": stat.S_IMODE(before.st_mode),
                "nlink": before.st_nlink,
                "uid": before.st_uid,
            }
            require(stat.S_ISREG(before.st_mode)
                    and stat.S_ISREG(named.st_mode)
                    and (before.st_dev, before.st_ino, before.st_size,
                         before.st_nlink, before.st_uid)
                    == (named.st_dev, named.st_ino, named.st_size,
                        named.st_nlink, named.st_uid),
                    "reject a symlinked, linked, foreign or replaced mature file")
            normalized = normalized_metadata(previous, actual, os.geteuid())
            remaining = before.st_size
            blocks: list[bytes] = []
            digest = hashlib.sha256()
            while remaining:
                part = os.read(descriptor, min(remaining, 1048576))
                require(type(part) is bytes and bool(part),
                        "reject truncated normalized native-owner bytes")
                remaining -= len(part)
                blocks.append(part)
                digest.update(part)
            require(os.read(descriptor, 1) == b"",
                    "reject hidden bytes during mature-owner normalization")
            final = os.fstat(descriptor)
            visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            require(
                (before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns,
                 before.st_nlink, before.st_uid)
                == (final.st_dev, final.st_ino, final.st_size,
                    final.st_mtime_ns, final.st_ctime_ns,
                    final.st_nlink, final.st_uid)
                and (final.st_dev, final.st_ino, final.st_size,
                     final.st_nlink, final.st_uid)
                == (visible.st_dev, visible.st_ino, visible.st_size,
                    visible.st_nlink, visible.st_uid)
                and digest.hexdigest() == previous["sha256"]
                and b"".join(blocks) == raw,
                "reject changed bytes, relink, ownership or TOCTOU mature owner")
            return raw, normalized
        finally:
            for descriptor in reversed(opened):
                os.close(descriptor)

    mature.read_owned = verified_read
    require(callable(mature.read_owned)
            and mature.read_owned is not original_reader,
            "install exactly one descriptor-bound mature normalization boundary")
    return mature


def load_normalized_predecessor() -> types.ModuleType:
    relative, digest, size = PREDECESSOR["source"]
    raw, first = read_source_owner(relative, digest, size)
    try:
        tree = ast.parse(raw.decode("utf-8", "strict"),
                         filename=str(ROOT / relative))
    except (SyntaxError, ValueError, UnicodeError,
            RecursionError) as error:
        raise ActivationError("reject the changed immutable V6 source") from error
    definitions = {node.name for node in tree.body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    require({"load_mature_primitives", "authenticate_context", "activate",
             "recover", "exact_current_original", "mature_owner_matches",
             "validated_phase_bytes", "restore_exact_inodes"}
            <= definitions, "retain all exact immutable V6 dual-role operations")
    name = "_rebar_owned_zig_v7_immutable_v6_" + digest[:20]
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = str(ROOT / relative)
        module.__package__ = ""
        sys.modules[name] = module
        try:
            exec(compile(raw, module.__file__, "exec", dont_inherit=True),
                 module.__dict__)
        except BaseException:
            sys.modules.pop(name, None)
            raise
        underlying_loader = module.load_mature_primitives

        def normalized_loader(source: bytes) -> types.ModuleType:
            return normalize_mature_reader(underlying_loader(source))

        module.load_mature_primitives = normalized_loader
    _, last = read_source_owner(relative, digest, size)
    require(type(module) is types.ModuleType and module.__name__ == name
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / relative)
            and (first["device"], first["inode"])
            == (last["device"], last["inode"])
            and module.SCHEMA == "rebar-phase2-verified-native-activation-v6"
            and module.FAMILY == FAMILY and module.BUILD_LABEL == BUILD_LABEL
            and tuple(module.ROLE_ORDER) == ("engine", "bridge")
            and tuple(module.RESTORATION_ORDER) == ("bridge", "engine"),
            "retain only the exact digest-pinned mature dual-role V6 predecessor")
    return module


def source_size(relative: str) -> int:
    checked_relative(relative)
    seen = os.stat(str(ROOT / relative), follow_symlinks=False)
    require(stat.S_ISREG(seen.st_mode) and seen.st_uid == os.geteuid()
            and seen.st_nlink == 1
            and 0 < seen.st_size <= MAX_SOURCE_BYTES,
            "reject a linked, changed or oversized V7 source owner")
    return seen.st_size


def verify_context(
    source_pin: str, protocol_pin: str, contract_pin: str | None,
    *, retain: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    checked_digest(source_pin, "V7 source")
    checked_digest(protocol_pin, "V7 protocol")
    _, own_source = read_source_owner(
        SOURCE_RELATIVE, source_pin, source_size(SOURCE_RELATIVE))
    _, own_protocol = read_source_owner(
        PROTOCOL_RELATIVE, protocol_pin, source_size(PROTOCOL_RELATIVE))
    predecessor = load_normalized_predecessor()
    for label in ("protocol", "contract"):
        read_source_owner(*PREDECESSOR[label])
    for label in ("source", "protocol"):
        read_source_owner(*MATURE[label])
    for label in ("source", "protocol", "contract"):
        read_source_owner(*FAILED_V1[label])
        read_source_owner(*ORIGINAL_PRODUCER[label])
    failed_raw, _ = read_source_owner(*FAILED_V1["contract"])
    failure_freeze = strict_document(failed_raw, "genuine frozen first V1 attempt")
    require(failure_freeze.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v1-source-freeze"
            and failure_freeze.get("version") == 1
            and failure_freeze.get("family") == FAMILY
            and failure_freeze.get("original_oracle", {}).get("suite_count") == 13
            and failure_freeze.get("original_oracle", {}).get(
                "case_execution_denominator") == 31237
            and failure_freeze.get("original_oracle", {}).get(
                "named_private_waiver_count") == 13,
            "preserve the actual failed immutable V1 thirteen-suite source freeze")
    v6, inherited = predecessor.authenticate_context(
        PREDECESSOR["source"][1], PREDECESSOR["protocol"][1],
        PREDECESSOR["contract"][1], retain=True)
    require(v6.get("status") == "PASS" and v6.get("family") == FAMILY
            and v6.get("published_v25_evidence_owner_count") == 139
            and v6.get("published_v25_authenticated_reference_count") == 144
            and v6.get("zig_build_historical_evidence_owner_count") == 135
            and v6.get("zig_build_historical_reference_count") == 140
            and v6.get("actual_zig_build_process_count") == 26
            and v6.get("actual_rust_build_process_count") == 28
            and v6.get("actual_rust_public_source_repair_count") == 2
            and v6.get("actual_rust_bridge_source_repair_count") == 2
            and v6.get("actual_c_semantic_mismatch_count") == 1262
            and v6.get("actual_c_candidate_worker_count") == 13
            and v6.get("actual_c_verified_passing_case_executions") == 7325
            and v6.get("frozen_case_execution_count") == 31237
            and v6.get("frozen_suite_count") == 13
            and v6.get("frozen_private_waiver_count") == 13
            and v6.get("native_role_count") == 2
            and v6.get("group_atomic") is False
            and v6.get("source_freeze_original_targets_read") == 0
            and v6.get("source_freeze_original_targets_statted") == 0
            and v6.get("source_freeze_original_targets_modified") == 0
            and v6.get("canonical_target_reads") == 0
            and v6.get("canonical_target_stats") == 0
            and v6.get("canonical_target_links") == 0
            and v6.get("canonical_target_replacements") == 0
            and v6.get("holdout") == "NOT OPENED",
            "authenticate untouched V6, all actual evidence, and zero source effects")
    mature = inherited["mature"]
    require(tuple(mature.OWNER_FIELDS) == MATURE_OWNER_FIELDS
            and callable(mature.read_owned),
            "retain one unchanged V2 owner schema under the V7 normalizer")
    original = predecessor.NATIVE_ROLES["engine"]["original"]
    seven = {
        "relative": original["relative"],
        "path": str(ROOT / original["relative"]),
        "sha256": original["sha256"],
        "size_bytes": original["bytes"],
        "device": original["device"],
        "inode": original["inode"],
        "mode": original["mode"],
    }
    observed = {
        "device": original["device"], "inode": original["inode"],
        "size_bytes": original["bytes"], "mode": original["mode"],
        "nlink": original["nlink"], "uid": original["uid"],
    }
    normalized = normalized_metadata(seven, observed, os.geteuid())
    require(predecessor.mature_owner_matches(seven, original) is False
            and predecessor.mature_owner_matches(normalized, original) is True
            and normalized["uid"] == original["uid"]
            and normalized["nlink"] == original["nlink"],
            "demonstrate the exact genuine first-run owner-shape defect and fix")
    final_owner = None
    if contract_pin is not None:
        checked_digest(contract_pin, "V7 machine contract")
        machine_raw, final_owner = read_source_owner(
            CONTRACT_RELATIVE, contract_pin, source_size(CONTRACT_RELATIVE))
        validate_contract(strict_document(machine_raw, "exact V7 contract"),
                          source_pin, protocol_pin)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "never import a candidate while verifying V7 source")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": 7, "family": FAMILY,
        "mode": "READ-ONLY V6 OWNER NORMALIZATION",
        "source": own_source, "protocol": own_protocol,
        "contract": final_owner,
        "published_v25_evidence_owner_count": 139,
        "published_v25_authenticated_reference_count": 144,
        "zig_build_historical_evidence_owner_count": 135,
        "zig_build_historical_reference_count": 140,
        "actual_zig_build_process_count": 26,
        "actual_rust_build_process_count": 28,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_c_candidate_worker_count": 13,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "native_role_count": 2,
        "mature_original_owner_field_count": 7,
        "normalized_owner_field_count": 9,
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_attempt_failure_class": "INFRASTRUCTURE FAILURE",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_native_activations": 0,
        "actual_first_v1_candidate_matching": "NOT MEASURED",
        "owner_shape_defect_proven_without_target_access": True,
        "uid_and_nlink_fabricated": False,
        "group_atomic": False, "restoration_order": ["bridge", "engine"],
        **source_effects(),
    }
    retained = {
        "v6": predecessor, "v6_context": v6, "inherited": inherited,
    } if retain else {}
    return result, retained


class SourceWall:
    """Keep every synthetic owner-normalization control effect-free."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked = {x: 0 for x in (
            "filesystem", "process", "clock", "network",
            "native", "thread", "import",
        )}

    def install(self, owner: Any, attribute: str, kind: str) -> None:
        if not hasattr(owner, attribute):
            return
        old = getattr(owner, attribute)

        def deny(*args: Any, **kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise SourceOnlyEffect("V7 source-only verification blocks " + kind)

        self.previous.append((owner, attribute, old))
        setattr(owner, attribute, deny)

    def __enter__(self) -> "SourceWall":
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (os, "read"), (os, "write"), (os, "stat"),
            (os, "lstat"), (os, "fstat"), (os, "scandir"),
            (os, "link"), (os, "replace"), (os, "rename"),
            (os, "unlink"), (os, "remove"), (os, "mkdir"),
            (os, "makedirs"), (os, "fsync"), (os, "fchmod"),
            (tempfile, "mkdtemp"),
        ):
            self.install(owner, name, "filesystem")
        for name in ("Popen", "run", "call", "check_output"):
            self.install(subprocess, name, "process")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "sleep"):
            self.install(time, name, "clock")
        self.install(socket, "create_connection", "network")
        self.install(socket.socket, "connect", "network")
        self.install(ctypes, "CDLL", "native")
        self.install(threading.Thread, "start", "thread")
        self.install(importlib, "import_module", "import")
        return self

    def __exit__(self, *_: Any) -> None:
        for owner, name, old in reversed(self.previous):
            setattr(owner, name, old)


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(contract_pin, "V7 frozen owner-normalization contract")
    accepted: list[str] = []
    rejected: list[str] = []
    current_uid = os.geteuid()
    with SourceWall() as wall:
        contract = protocol_document(source_pin, protocol_pin)

        def accept(name: str, valid: Any) -> None:
            require(valid is True, "positive normalization control failed: " + name)
            accepted.append(name)

        def reject(name: str, action: Any) -> None:
            try:
                action()
            except (ActivationError, SourceOnlyEffect, OSError, ValueError,
                    TypeError, UnicodeError, OverflowError, RecursionError):
                rejected.append(name)
                return
            raise ActivationError("hostile normalization was accepted: " + name)

        seven = {
            "relative": "candidates/_zig_probe.so",
            "path": "/home/dev-user/src/rebar/candidates/_zig_probe.so",
            "sha256":
                "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
            "size_bytes": 478432, "device": 2064,
            "inode": 431260, "mode": 0o700,
        }
        evidence = {
            "size_bytes": 478432, "device": 2064,
            "inode": 431260, "mode": 0o700,
            "nlink": 1, "uid": current_uid,
        }
        complete = normalized_metadata(seven, evidence, current_uid)
        accept("preserve-seven-authentic-mature-owner-fields",
               tuple(x for x in MATURE_OWNER_FIELDS if x in seven)
               == MATURE_OWNER_FIELDS)
        accept("never-invent-legacy-owner-uid-or-nlink",
               "uid" not in seven and "nlink" not in seven)
        accept("supply-only-real-descriptor-observed-fields",
               complete["uid"] == current_uid and complete["nlink"] == 1)
        accept("retain-original-mature-device-and-inode",
               complete["device"] == 2064 and complete["inode"] == 431260)
        accept("retain-exact-original-mature-content-digest",
               complete["sha256"] == seven["sha256"]
               and complete["size_bytes"] == 478432)
        accept("retain-exact-original-mature-native-mode",
               complete["mode"] == 0o700)
        accept("pin-all-three-immutable-v6-owners",
               contract["unchanged_actual_v6_predecessor"]["owners"]
               == mapped_owners(PREDECESSOR))
        accept("pin-all-three-actual-failed-v1-owners",
               contract["actual_first_v1_campaign_attempt"]["owners"]
               == mapped_owners(FAILED_V1))
        attempt = contract["actual_first_v1_campaign_attempt"]
        accept("preserve-real-failed-v1-infrastructure-status",
               attempt["attempt_status"] == "FAIL"
               and attempt["failure_class"] == "INFRASTRUCTURE FAILURE")
        accept("preserve-genuine-pre-activation-failure-stage",
               attempt["failure_stage"]
               == "PRE-ACTIVATION ORIGINAL ENGINE OWNER METADATA")
        accept("never-invent-first-run-workers",
               attempt["actual_candidate_worker_count"] == 0)
        accept("never-invent-first-run-activation",
               attempt["actual_native_activation_count"] == 0
               and attempt["actual_promotion_count"] == 0)
        accept("first-zig-matching-not-measured",
               attempt["original_matching"] == "NOT MEASURED"
               and attempt["candidate_semantic_mismatch_count"]
               == "NOT MEASURED")
        accept("never-invent-failed-v1-archive-or-receipt",
               attempt["existing_campaign_archive"] == "NOT PUBLISHED"
               and attempt["existing_campaign_receipt"] == "NOT PUBLISHED")
        accept("retain-not-recorded-pid-and-exact-read-count",
               attempt["actual_process_pid"] == "NOT RECORDED"
               and attempt["exact_canonical_read_count"] == "NOT RECORDED")
        history = contract["published_v25_history"]
        accept("retain-authentic-current-139-144-history",
               history["authoritative_evidence_owner_count"] == 139
               and history["authenticated_reference_count"] == 144)
        build = contract["actual_zig_v11_build"]
        accept("retain-distinct-genuine-zig-135-140-history",
               build["historical_evidence_owner_count_at_build"] == 135
               and build["historical_reference_count_at_build"] == 140)
        accept("retain-real-zig26-rust28-build-processes",
               build["actual_compiler_process_count"] == 26
               and history["actual_rust_compiler_process_count"] == 28)
        accept("preserve-all-actual-c-losses",
               history["actual_c_candidate_workers"] == 13
               and history["actual_c_semantic_mismatch_count"] == 1262)
        accept("preserve-real-dual-native-original-inodes",
               [x["original_inode"] for x in build["native_roles"]]
               == [431260, 431274])
        accept("retain-all-original-thirteen-suite-groups",
               len(SUITES) == 13 and sum(x for _, x in SUITES) == 31237)
        accept("retain-all-named-private-waivers",
               contract["oracle"]["named_private_waiver_count"] == 13)
        accept("normalize-exactly-one-mature-boundary",
               contract["owner_normalization"]["one_mature_read_boundary"]
               is True)
        accept("descriptor-fstat-and-complete-digest-required",
               contract["owner_normalization"]["stat_values_are_descriptor_observed"]
               is True and contract["owner_normalization"]
               ["reauthenticate_complete_original_content"] is True)
        accept("never-claim-two-role-group-atomicity",
               contract["activation_policy"]["group_atomic"] is False)
        accept("preserve-exact-bridge-before-engine-recovery",
               contract["activation_policy"]["fixed_restoration_order"]
               == ["bridge", "engine"])
        accept("canonical-full-v7-contract-roundtrip",
               strict_document(canonical(contract), "synthetic V7 contract")
               == contract)
        for name, changed in (
            ("missing-nlink", {"nlink": None}),
            ("missing-uid", {"uid": None}),
            ("zero-hardlinks", {"nlink": 0}),
            ("shared-hardlink", {"nlink": 2}),
            ("foreign-uid", {"uid": current_uid + 1}),
            ("changed-inode", {"inode": 431261}),
            ("changed-device", {"device": 2065}),
            ("changed-mode", {"mode": 0o600}),
            ("changed-size", {"size_bytes": 478433}),
            ("boolean-nlink", {"nlink": True}),
            ("boolean-uid", {"uid": True}),
            ("boolean-inode", {"inode": True}),
        ):
            def bad_identity(delta: dict[str, Any] = changed) -> None:
                candidate = dict(evidence)
                candidate.update(delta)
                normalized_metadata(seven, candidate, current_uid)
            reject("reject-" + name, bad_identity)
        for name, changed in (
            ("missing-owner-relative", {"relative": None}),
            ("changed-owner-digest", {"sha256": "z" * 64}),
            ("escaped-owner-path", {"relative": "../escaped"}),
            ("wrong-owner-size", {"size_bytes": 478433}),
            ("wrong-owner-device", {"device": 2065}),
            ("wrong-owner-inode", {"inode": 431261}),
            ("wrong-owner-mode", {"mode": 0o600}),
        ):
            def bad_owner(delta: dict[str, Any] = changed) -> None:
                owner = dict(seven)
                owner.update(delta)
                normalized_metadata(owner, evidence, current_uid)
            reject("reject-" + name, bad_owner)
        mutations = (
            ("erase-actual-v1-failure",
             lambda x: x["actual_first_v1_campaign_attempt"].update(
                 {"attempt_status": "PASS"})),
            ("invent-original-matching",
             lambda x: x["actual_first_v1_campaign_attempt"].update(
                 {"original_matching": "PASS"})),
            ("invent-first-worker",
             lambda x: x["actual_first_v1_campaign_attempt"].update(
                 {"actual_candidate_worker_count": 1})),
            ("invent-first-activation",
             lambda x: x["actual_first_v1_campaign_attempt"].update(
                 {"actual_native_activation_count": 1})),
            ("hide-missing-mature-fields",
             lambda x: x["unchanged_mature_v2_primitives"].update(
                 {"original_returned_nlink": True})),
            ("invent-descriptor-metadata",
             lambda x: x["owner_normalization"].update(
                 {"stat_values_are_descriptor_observed": False})),
            ("omit-hash-readback",
             lambda x: x["owner_normalization"].update(
                 {"reauthenticate_complete_original_content": False})),
            ("permit-shared-hardlink",
             lambda x: x["owner_normalization"].update(
                 {"require_owner_only_regular_single_link": False})),
            ("rewrite-current-history",
             lambda x: x["published_v25_history"].update(
                 {"authoritative_evidence_owner_count": 135})),
            ("hide-real-c-mismatches",
             lambda x: x["published_v25_history"].update(
                 {"actual_c_semantic_mismatch_count": 0})),
            ("claim-group-atomic-replacement",
             lambda x: x["activation_policy"].update({"group_atomic": True})),
            ("reverse-original-restoration",
             lambda x: x["activation_policy"].update(
                 {"fixed_restoration_order": ["engine", "bridge"]})),
            ("open-final-holdout",
             lambda x: x["source_only_effects"].update({"holdout": "OPENED"})),
        )
        for name, mutation in mutations:
            def bad_contract(change: Any = mutation) -> None:
                value = copy.deepcopy(contract)
                change(value)
                validate_contract(value, source_pin, protocol_pin)
            reject("reject-" + name, bad_contract)
        for name, action in (
            ("filesystem", lambda: os.open("/forbidden", os.O_RDONLY)),
            ("process", lambda: subprocess.run(["/usr/bin/true"])),
            ("clock", lambda: time.perf_counter_ns()),
            ("network", lambda: socket.create_connection(("invalid", 1))),
            ("native", lambda: ctypes.CDLL("external-regex.so")),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("import", lambda: importlib.import_module("candidates.zig_candidate")),
        ):
            reject("block-real-" + name, action)
        blocked = dict(wall.blocked)
    require(len(accepted) >= 24 and all(x > 0 for x in blocked.values()),
            "require every positive and hostile genuine source-only control")
    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "status": "PASS", "version": 7, "family": FAMILY,
        "mode": "SYNTHETIC OWNER NORMALIZATION ONLY",
        "accepted_control_count": len(accepted), "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_effects_by_kind": blocked,
        "published_v25_evidence_owner_count": 139,
        "published_v25_authenticated_reference_count": 144,
        "zig_build_historical_evidence_owner_count": 135,
        "zig_build_historical_reference_count": 140,
        "actual_zig_build_process_count": 26,
        "actual_rust_build_process_count": 28,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_c_candidate_worker_count": 13,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13, "native_role_count": 2,
        "mature_original_owner_field_count": 7,
        "normalized_owner_field_count": 9,
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_attempt_failure_class": "INFRASTRUCTURE FAILURE",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_native_activations": 0,
        "actual_first_v1_candidate_matching": "NOT MEASURED",
        "owner_shape_defect_proven_without_target_access": True,
        "uid_and_nlink_fabricated": False,
        "group_atomic": False, "restoration_order": ["bridge", "engine"],
        **source_effects(),
    }


def checked_predecessor_options(options: argparse.Namespace) -> None:
    require(options.predecessor_source_sha256 == PREDECESSOR["source"][1]
            and options.predecessor_protocol_sha256
            == PREDECESSOR["protocol"][1]
            and options.predecessor_contract_sha256
            == PREDECESSOR["contract"][1]
            and options.family == FAMILY,
            "independently caller-pin every immutable original V6 owner")


def activate(options: argparse.Namespace) -> dict[str, Any]:
    checked_predecessor_options(options)
    require(options.build_label == BUILD_LABEL
            and options.build_archive_sha256 == BUILD_ARCHIVE[1]
            and options.build_receipt_sha256 == BUILD_RECEIPT[1]
            and options.native_engine_sha256 == ENGINE_SHA256
            and options.native_bridge_sha256 == BRIDGE_SHA256
            and options.native_engine_bytes == ENGINE_BYTES
            and options.native_bridge_bytes == BRIDGE_BYTES,
            "pin both genuine source-built original V11 native roles")
    context, kept = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "authenticate the entire immutable V7 freeze before activation")
    v6 = kept["v6"]
    args = [
        "--activate",
        "--source-sha256", PREDECESSOR["source"][1],
        "--protocol-sha256", PREDECESSOR["protocol"][1],
        "--contract-sha256", PREDECESSOR["contract"][1],
        "--family", FAMILY, "--build-label", BUILD_LABEL,
        "--build-archive-sha256", BUILD_ARCHIVE[1],
        "--build-receipt-sha256", BUILD_RECEIPT[1],
        "--native-engine-sha256", ENGINE_SHA256,
        "--native-bridge-sha256", BRIDGE_SHA256,
        "--native-engine-bytes", str(ENGINE_BYTES),
        "--native-bridge-bytes", str(BRIDGE_BYTES),
    ]
    actual = v6.activate(v6.parse_arguments(args))
    require(type(actual) is dict
            and actual.get("schema") == v6.SCHEMA + "-activation-result"
            and actual.get("status") == "PASS"
            and actual.get("version") == 6 and actual.get("family") == FAMILY
            and actual.get("group_atomic") is False
            and actual.get("original_inodes_preserved_in_adjacent_backups")
            is True
            and type(actual.get("roles")) is dict
            and set(actual["roles"]) == {"engine", "bridge"},
            "preserve complete genuine V6 journal and both original hardlinks")
    return {
        **actual,
        "schema": SCHEMA + "-normalized-activation-result", "version": 7,
        "immutable_v6_predecessor_schema": v6.SCHEMA + "-activation-result",
        "immutable_v6_predecessor_source_sha256": PREDECESSOR["source"][1],
        "mature_owner_normalization": "DESCRIPTOR-BOUND TRUE UID AND NLINK",
        "original_v1_infrastructure_failure_preserved": True,
        "actual_first_v1_candidate_matching": "NOT MEASURED",
        "group_atomic": False,
    }


def recover(options: argparse.Namespace) -> dict[str, Any]:
    checked_predecessor_options(options)
    context, kept = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "authenticate the entire immutable V7 freeze before recovery")
    v6 = kept["v6"]
    root = v6.checked_private_root(options.activation_root)
    journal = checked_digest(
        options.recovery_journal_sha256, "actual inherited V6 recovery journal")
    args = [
        "--recover", "--source-sha256", PREDECESSOR["source"][1],
        "--protocol-sha256", PREDECESSOR["protocol"][1],
        "--contract-sha256", PREDECESSOR["contract"][1],
        "--family", FAMILY, "--activation-root", root,
        "--recovery-journal-sha256", journal,
    ]
    actual = v6.recover(v6.parse_arguments(args))
    require(type(actual) is dict
            and actual.get("schema") == v6.SCHEMA + "-recovery-result"
            and actual.get("status") == "PASS"
            and actual.get("version") == 6 and actual.get("family") == FAMILY
            and actual.get("activation_root") == root
            and actual.get("recovery_journal_sha256") == journal
            and actual.get("group_atomic") is False
            and actual.get("original_inode_preserved") is True
            and type(actual.get("restoration")) is dict
            and actual["restoration"].get("restoration_order")
            == ["bridge", "engine"]
            and set(actual["restoration"].get("restored_targets", {}))
            == {"engine", "bridge"},
            "preserve exact inherited reverse original-inode V6 recovery")
    return {
        **actual,
        "schema": SCHEMA + "-normalized-recovery-result", "version": 7,
        "immutable_v6_predecessor_schema": v6.SCHEMA + "-recovery-result",
        "immutable_v6_predecessor_source_sha256": PREDECESSOR["source"][1],
        "mature_owner_normalization": "DESCRIPTOR-BOUND TRUE UID AND NLINK",
        "original_v1_infrastructure_failure_preserved": True,
        "group_atomic": False,
    }


def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    require(all(type(x) is str for x in values),
            "provide exactly one complete V7 owner-normalization command")
    flags = [x for x in values if x.startswith("--")]
    require(len(flags) == len(set(flags)),
            "reject duplicate or shadowed actual activation authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--verify-frozen-context", action="store_true")
    mode.add_argument("--render-contract", action="store_true")
    mode.add_argument("--activate", action="store_true")
    mode.add_argument("--recover", action="store_true")
    mode.add_argument("--restore", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--predecessor-source-sha256")
    parser.add_argument("--predecessor-protocol-sha256")
    parser.add_argument("--predecessor-contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--build-label")
    parser.add_argument("--build-archive-sha256")
    parser.add_argument("--build-receipt-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    parser.add_argument("--activation-root")
    parser.add_argument("--recovery-journal-sha256")
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "V7 source")
    checked_digest(options.protocol_sha256, "V7 protocol")
    for name in (
        "contract_sha256", "predecessor_source_sha256",
        "predecessor_protocol_sha256", "predecessor_contract_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
        "recovery_journal_sha256",
    ):
        item = getattr(options, name)
        if item is not None:
            checked_digest(item, name)
    actual = (
        "predecessor_source_sha256", "predecessor_protocol_sha256",
        "predecessor_contract_sha256", "family", "build_label",
        "build_archive_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
        "native_engine_bytes", "native_bridge_bytes",
        "activation_root", "recovery_journal_sha256",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, x) is None for x in actual),
                "contract rendering cannot activate or inspect a native target")
        return options
    require(options.contract_sha256 is not None,
            "independently pin the exact canonical V7 machine contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, x) is None for x in actual),
                "source-only normalization cannot operate on native targets")
        return options
    checked_predecessor_options(options)
    if options.activate:
        required = (
            "build_label", "build_archive_sha256", "build_receipt_sha256",
            "native_engine_sha256", "native_bridge_sha256",
            "native_engine_bytes", "native_bridge_bytes",
        )
        require(all(getattr(options, x) is not None for x in required)
                and options.activation_root is None
                and options.recovery_journal_sha256 is None,
                "authorize only a fresh independently pinned V6-native activation")
    else:
        require(options.activation_root is not None
                and options.recovery_journal_sha256 is not None
                and all(getattr(options, x) is None for x in (
                    "build_label", "build_archive_sha256",
                    "build_receipt_sha256", "native_engine_sha256",
                    "native_bridge_sha256", "native_engine_bytes",
                    "native_bridge_bytes",
                )),
                "recover only the exact actual inherited V6 two-role journal")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
        if options.self_test:
            result = self_test(options.source_sha256,
                               options.protocol_sha256,
                               options.contract_sha256)
        elif options.verify_frozen_context:
            result, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256,
                                       options.contract_sha256)
        elif options.render_contract:
            verify_context(options.source_sha256,
                           options.protocol_sha256, None)
            result = protocol_document(options.source_sha256,
                                       options.protocol_sha256)
        elif options.activate:
            result = activate(options)
        else:
            result = recover(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0
    except Exception as error:
        sys.stderr.write("VERIFIED ZIG OWNER NORMALIZATION V7: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
