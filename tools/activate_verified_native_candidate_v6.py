#!/usr/bin/env python3
"""Freeze and explicitly, reversibly activate the actual two-role V11 Zig build.

Self-tests are synthetic and effect-blocked. Frozen-context verification only
authenticates named, already published evidence. Neither source-only mode opens,
stats, hashes, links, replaces, or otherwise touches either original Zig native
target. Activation and reportless exact-inode recovery are separate explicit
operations.
"""

from __future__ import annotations

import argparse
import base64
import builtins
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
import zlib
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v6.py"
PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V6.md"
CONTRACT_RELATIVE = "oracle/phase2/verified-native-activation-v6.json"
SCHEMA = "rebar-phase2-verified-native-activation-v6"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
JOURNAL_SCHEMA = SCHEMA + "-exact-inode-recovery-journal"
INTENTION_SCHEMA = SCHEMA + "-durable-role-intention"
REPORT_SCHEMA = SCHEMA + "-actual-activation"
RECEIPT_SCHEMA = SCHEMA + "-durable-activation-receipt"
RESTORATION_SCHEMA = SCHEMA + "-exact-inode-restoration"
FAMILY = "zig"
BUILD_LABEL = "phase2-v11-zig-scanner"
PRIVATE_PREFIX = "rebar-phase2-verified-native-activation-v6-zig-"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_REPORT_BYTES = 8 * 1024 * 1024
MAX_TOOLCHAIN_BYTES = 64 * 1024 * 1024
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_PYTHON_BYTES = 32_387_816
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1_024),
    ("buffer_v3", 768),
    ("managed_v1", 1_024),
    ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912),
    ("substitution_v2", 5_120),
    ("shape_v2", 10_240),
    ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
PHASE_NAMES = ("reference-a", "reference-b")
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version",
    "build_zig_engine", "build_zig_bridge",
    "engine_dynamic", "engine_symbols", "engine_sections", "engine_notes",
    "bridge_dynamic", "bridge_symbols", "bridge_sections", "bridge_notes",
)
ORIGINAL_SOURCES: dict[str, tuple[str, int]] = {
    "candidates/zig_candidate.py": (
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        68_422,
    ),
    "candidates/zig/mini_regex.zig": (
        "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
        186_915,
    ),
    "candidates/zig/py_bridge.c": (
        "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
        173_026,
    ),
}
DERIVED_BRIDGE_SHA256 = (
    "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
)
DERIVED_BRIDGE_BYTES = 173_082
NATIVE_ROLES: dict[str, dict[str, Any]] = {
    "engine": {
        "filename": "_zig_probe.so",
        "relative": "candidates/_zig_probe.so",
        "sha256":
            "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071",
        "bytes": 108_888,
        "original": {
            "relative": "candidates/_zig_probe.so",
            "sha256":
                "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
            "bytes": 478_432,
            "device": 2_064,
            "inode": 431_260,
            "mode": 0o700,
            "nlink": 1,
            "uid": 1_000,
        },
    },
    "bridge": {
        "filename": "_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "relative": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256":
            "75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681",
        "bytes": 133_656,
        "original": {
            "relative":
                "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
            "sha256":
                "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b",
            "bytes": 134_112,
            "device": 2_064,
            "inode": 431_274,
            "mode": 0o700,
            "nlink": 1,
            "uid": 1_000,
        },
    },
}
ROLE_ORDER = ("engine", "bridge")
RESTORATION_ORDER = ("bridge", "engine")
V11_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz"
)
V11_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v11-zig-"
    "phase2-v11-zig-scanner-publication-receipt.json"
)
RUST_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz"
)
RUST_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v11-rust-"
    "phase2-v11-rust-dual-overlay-publication-receipt.json"
)
MATURE_SOURCE = "tools/activate_verified_native_candidate_v2.py"
MATURE_PROTOCOL = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md"
SUPPORT_OWNERS: dict[str, tuple[str, int]] = {
    "GOAL.md": (
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3_756,
    ),
    "oracle/phase1/p0-completeness-v1.json": (
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        45_632,
    ),
    MATURE_SOURCE: (
        "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218",
        205_006,
    ),
    MATURE_PROTOCOL: (
        "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529",
        10_346,
    ),
    "tools/render_candidate_current_overview_v25.py": (
        "9b1eabba4a3bd991c4359af4ab1482fe6f1ce848bb9e5df6fdd9e8bdafb21204",
        98_948,
    ),
    "docs/evidence/candidate-current-overview-v25.inputs.json": (
        "123210219fac109506c03c2f76f89fda33aa5e08b0628fef43b9236d05bc1abe",
        37_281,
    ),
    "docs/evidence/candidate-current-overview-v25.json": (
        "8e4101c896e316190928d0710ca4442488c925ee5ef421507ba4dd08ff10a6d9",
        144_980,
    ),
    "docs/evidence/candidate-current-overview-v25.svg": (
        "db2f1a11e49fd58701ad89111aa422e619431eb9834d3fb5ae66deffcd75f0bb",
        13_188,
    ),
    "tools/reproduce_owned_zig_scanner_source_build_v11.py": (
        "b908f12d14fb8ebc5f17c62dfc00d48a1a5ee3717a3144aed437059e21c0f097",
        207_444,
    ),
    "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md": (
        "15fd222876407be72d36c0b9cf2ce581d8b73a954358df192c2a083a08973539",
        6_144,
    ),
    "oracle/phase2/zig-scanner-source-build-v11.json": (
        "92979e4bfacd6d23e7f54f4fdce7a7707cc54dba2512753029fdcd479150464c",
        44_636,
    ),
    V11_ARCHIVE: (
        "e4a1f369b647f588ac5b12585f7d0e30c4ee3409adc88f660081fb7a59a8df5c",
        48_246,
    ),
    V11_RECEIPT: (
        "d53766d0dad571f8b72288cece15fb1ad0892db32c3b3b6b512027db94ca4fcc",
        1_683,
    ),
    "tools/apply_owned_zig_scanner_capture_source_repair_v1.py": (
        "963f306373753b9fef84c9a9784668f42067cb905b84347a0bcc99e1e8692515",
        65_531,
    ),
    "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md": (
        "7a40b58bcc69744fc6b749368ec307be7d05d742de3d921410fd2753a4f5c8d0",
        5_198,
    ),
    "oracle/phase2/zig-scanner-capture-source-repair-v1.json": (
        "c48fcd9cb40cbe15442c2dd197627d7f4ccc341b3edfbbe0c645405015c8ea87",
        9_236,
    ),
    "tools/run_owned_six_family_original_p0_producer_v3.py": (
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
        195_555,
    ),
    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md": (
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
        5_522,
    ),
    "oracle/phase2/six-family-p0-producer-v3.json": (
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
        26_909,
    ),
    "tools/reproduce_owned_native_source_build_v11.py": (
        "3fb0ca1b6914617eb8a6f491072fcb40b15a364afacbaec2d4caac1e9b6f5d10",
        80_171,
    ),
    "oracle/phase2/NATIVE-SOURCE-BUILD-V11.md": (
        "bd6bce6b14bebe55691900e4a48bb8acf89197660e1d5ebd4c8c38e979c05fe6",
        3_868,
    ),
    "oracle/phase2/native-source-build-v11.json": (
        "7b1f8941444e942a85eb9f9df9dc23244112763ca92381fe22f76fd87c95a87a",
        7_676,
    ),
    RUST_ARCHIVE: (
        "282927f91fd885701dff6c431474f586afbc09460c6a20417ffa20be5a2e891c",
        107_639,
    ),
    RUST_RECEIPT: (
        "4c75468663af0de60b37cdbabfca384c4e7f75e25a6155c2ff1c33f654d3f1d7",
        1_902,
    ),
}
SUPPORT_OWNERS.update(ORIGINAL_SOURCES)


class ActivationError(Exception):
    """Reject altered, unsafe, incomplete, or non-first-party activation."""


class SourceOnlyEffect(ActivationError):
    """A synthetic source-only check attempted an external effect."""


def require(condition: Any, reason: str) -> None:
    if condition is not True:
        raise ActivationError(reason)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete authenticated bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(part in "0123456789abcdef" for part in value),
        "require one exact lowercase SHA-256: " + label,
    )
    return value


def checked_relative(value: Any) -> str:
    require(
        type(value) is str and value and "\x00" not in value
        and "\\" not in value and not value.startswith("/")
        and str(PurePosixPath(value)) == value
        and all(part not in ("", ".", "..") for part in value.split("/")),
        "reject an absolute, traversing, empty, or ambiguous relative owner",
    )
    return value


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise ActivationError("reject noncanonical activation evidence") from error


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject a duplicate or non-string JSON field")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
        "bound complete canonical JSON: " + label,
    )
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique_pairs,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ActivationError("reject nonfinite JSON: " + item)
            ),
        )
    except (json.JSONDecodeError, UnicodeError, ValueError,
            RecursionError) as error:
        raise ActivationError("reject malformed JSON: " + label) from error
    require(type(value) is dict and canonical(value) == raw,
            "reject changed canonical JSON bytes: " + label)
    return value


def owner_document(path: str, specification: tuple[str, int]) -> dict[str, Any]:
    return {"path": path, "sha256": specification[0],
            "bytes": specification[1]}


def role_contract(role: str) -> dict[str, Any]:
    selected = NATIVE_ROLES[role]
    original = selected["original"]
    return {
        "role": role,
        "filename": selected["filename"],
        "canonical_target": selected["relative"],
        "actual_build_sha256": selected["sha256"],
        "actual_build_bytes": selected["bytes"],
        "originally_present": True,
        "original": {
            **original,
            "mode": "0700",
        },
        "original_target_inspected_in_source_freeze": False,
        "hardlink_backup_required": True,
        "stage_creation_mode": "0600",
        "promoted_mode": "0700",
        "restore_exact_original_device_and_inode": True,
    }


def phase_boundary() -> dict[str, Any]:
    return {
        "native_activations_started": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "canonical_target_links": 0,
        "canonical_target_replacements": 0,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "native_builds_started": 0,
        "compiler_processes_started": 0,
        "native_source_applications": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "final_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "qualified_candidate_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
        "workspace_mutations": 0,
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "V6 activation source")
    checked_digest(protocol_pin, "V6 activation protocol")
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 6,
        "phase": "ZIG DUAL-NATIVE ACTIVATION SOURCE FREEZE; NO ACTIVATION",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "family": FAMILY,
        "oracle": {
            "implementation": "CPython",
            "version": "3.14.6",
            "python_path": PINNED_PYTHON,
            "python_sha256": PINNED_PYTHON_SHA256,
            "suite_count": 13,
            "suite_ids": [name for name, _ in SUITES],
            "case_execution_denominator": 31_237,
            "named_private_waiver_count": 13,
            "holdout": "NOT OPENED",
        },
        "published_v25_history": {
            "version": 25,
            "authoritative_evidence_owner_count": 139,
            "authenticated_reference_count": 144,
            "preserved_v24_evidence_owner_count": 137,
            "preserved_v24_reference_count": 142,
            "current_qualified_candidate_count": 0,
            "actual_c_candidate_workers": 13,
            "actual_c_verified_passing_case_executions": 7_325,
            "actual_c_semantic_mismatches": 1_262,
            "actual_c_infrastructure_failures": 0,
            "actual_rust_compiler_processes": 28,
            "actual_rust_public_source_repairs": 2,
            "actual_rust_bridge_source_repairs": 2,
            "historical_original_zig_semantic_mismatches": 1_764,
            "overview_renderer": owner_document(
                "tools/render_candidate_current_overview_v25.py",
                SUPPORT_OWNERS["tools/render_candidate_current_overview_v25.py"],
            ),
            "overview_inputs": owner_document(
                "docs/evidence/candidate-current-overview-v25.inputs.json",
                SUPPORT_OWNERS[
                    "docs/evidence/candidate-current-overview-v25.inputs.json"
                ],
            ),
            "overview_summary": owner_document(
                "docs/evidence/candidate-current-overview-v25.json",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v25.json"],
            ),
            "overview_svg": owner_document(
                "docs/evidence/candidate-current-overview-v25.svg",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v25.svg"],
            ),
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
        },
        "actual_zig_v11_build": {
            "family": FAMILY,
            "label": BUILD_LABEL,
            "historical_evidence_owner_count_at_build": 135,
            "historical_reference_count_at_build": 140,
            "source": owner_document(
                "tools/reproduce_owned_zig_scanner_source_build_v11.py",
                SUPPORT_OWNERS[
                    "tools/reproduce_owned_zig_scanner_source_build_v11.py"
                ],
            ),
            "protocol": owner_document(
                "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md",
                SUPPORT_OWNERS["oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md"],
            ),
            "contract": owner_document(
                "oracle/phase2/zig-scanner-source-build-v11.json",
                SUPPORT_OWNERS["oracle/phase2/zig-scanner-source-build-v11.json"],
            ),
            "archive": owner_document(V11_ARCHIVE, SUPPORT_OWNERS[V11_ARCHIVE]),
            "receipt": owner_document(V11_RECEIPT, SUPPORT_OWNERS[V11_RECEIPT]),
            "report_status": "PASS",
            "receipt_status": "PASS",
            "receipt_build_status": "PASS",
            "actual_compiler_process_count": 26,
            "actual_source_repair_application_count": 2,
            "independent_source_phase_count": 2,
            "byte_identical_native_role_count": 2,
            "scanner_derived_bridge_sha256": DERIVED_BRIDGE_SHA256,
            "scanner_derived_bridge_bytes": DERIVED_BRIDGE_BYTES,
            "roles": [role_contract(role) for role in ROLE_ORDER],
            "matching": "NOT MEASURED",
        },
        "actual_rust_v11_build": {
            "archive": owner_document(RUST_ARCHIVE, SUPPORT_OWNERS[RUST_ARCHIVE]),
            "receipt": owner_document(RUST_RECEIPT, SUPPORT_OWNERS[RUST_RECEIPT]),
            "actual_compiler_process_count": 28,
            "public_overlay_application_count": 2,
            "bridge_overlay_application_count": 2,
            "public_derived_sha256":
                "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c",
            "bridge_derived_sha256":
                "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257",
            "matching": "NOT MEASURED",
        },
        "immutable_dual_role_predecessor": {
            "source": owner_document(MATURE_SOURCE, SUPPORT_OWNERS[MATURE_SOURCE]),
            "protocol": owner_document(
                MATURE_PROTOCOL, SUPPORT_OWNERS[MATURE_PROTOCOL],
            ),
            "loaded_as_isolated_source_module": True,
            "candidate_import": False,
            "v2_activation_or_cli_invoked": False,
            "inherited_private_journal_primitives": True,
            "v2_byte_copy_restoration_allowed": False,
            "exact_original_inode_preservation": "SAME-DEVICE ADJACENT HARDLINK",
        },
        "activation_policy": {
            "explicit_operation_required": True,
            "accepted_family": FAMILY,
            "fixed_role_order": list(ROLE_ORDER),
            "fixed_restoration_order": list(RESTORATION_ORDER),
            "canonical_target_count": 2,
            "canonical_targets":
                [NATIVE_ROLES[role]["relative"] for role in ROLE_ORDER],
            "group_atomic": False,
            "group_atomic_claim": "FORBIDDEN",
            "candidate_source_mutation": "FORBIDDEN",
            "candidate_import": "FORBIDDEN",
            "other_family_target_access": "FORBIDDEN",
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "cross_family_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "network": "FORBIDDEN",
            "private_root_prefix": "/tmp/" + PRIVATE_PREFIX,
            "private_directory_mode": "0700",
            "private_journal_and_intention_mode": "0600",
            "initial_adjacent_stage_mode": "0600",
            "original_canonical_mode": "0700",
            "original_hardlink_count_before_backup": 1,
            "original_hardlink_count_during_backup": 2,
            "original_hardlink_count_after_promotion": 1,
            "original_hardlink_count_after_restoration": 1,
            "backup": "EXCLUSIVE SAME-DIRECTORY O_NOFOLLOW HARDLINK",
            "backup_before_replacement": True,
            "link_intention_before_link": True,
            "promotion_intention_before_stage_and_replace": True,
            "each_file_replacement_individually_atomic": True,
            "fsync_journal_before_any_target_operation": True,
            "fsync_candidate_directory_after_each_link_and_replace": True,
            "restore_exact_device_inode_bytes_mode_uid_and_link_count": True,
            "reportless_reverse_order_recovery": True,
            "refuse_unrelated_or_changed_target": True,
            "c_native_target_touched": False,
            "rust_native_target_touched": False,
            "restoration_before_correctness_publication": True,
        },
        "pinned_support": [
            owner_document(path, specification)
            for path, specification in sorted(SUPPORT_OWNERS.items())
        ],
        "phase_boundary": phase_boundary(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict, "require the exact V6 canonical contract")
    expected = contract_document(source_pin, protocol_pin)
    require(value == expected,
            "reject altered evidence, targets, original inodes, or source freeze")
    require(
        value["activation_policy"]["group_atomic"] is False
        and value["phase_boundary"] == phase_boundary()
        and len(value["actual_zig_v11_build"]["roles"]) == 2,
        "never count a planned two-role activation as an actual effect",
    )
    return value


def owner_metadata(relative: str, observed: os.stat_result,
                   expected_sha256: str) -> dict[str, Any]:
    return {
        "path": relative,
        "sha256": expected_sha256,
        "bytes": observed.st_size,
        "device": observed.st_dev,
        "inode": observed.st_ino,
        "mode": format(stat.S_IMODE(observed.st_mode), "04o"),
        "link_count": observed.st_nlink,
        "uid": observed.st_uid,
    }


def read_repository_owner(
    relative: str, expected: str, expected_size: int,
    *, maximum: int = MAX_SOURCE_BYTES,
) -> tuple[dict[str, Any], bytes]:
    checked_relative(relative)
    checked_digest(expected, relative)
    require(
        type(expected_size) is int and 0 < expected_size <= maximum,
        "require the exact bounded published owner size: " + relative,
    )
    descriptor_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directory_flags = descriptor_flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        parent = os.open(str(ROOT), directory_flags)
        opened.append(parent)
        for part in relative.split("/")[:-1]:
            parent = os.open(part, directory_flags, dir_fd=parent)
            opened.append(parent)
            info = os.fstat(parent)
            require(stat.S_ISDIR(info.st_mode),
                    "reject a substituted published-owner parent")
        name = relative.rsplit("/", 1)[-1]
        descriptor = os.open(name, descriptor_flags, dir_fd=parent)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        named = os.stat(name, dir_fd=parent, follow_symlinks=False)
        require(
            stat.S_ISREG(first.st_mode)
            and first.st_nlink == 1
            and first.st_uid == os.geteuid()
            and first.st_size == expected_size
            and (first.st_dev, first.st_ino) == (named.st_dev, named.st_ino),
            "reject a substituted, linked, foreign, or truncated owner: "
            + relative,
        )
        pieces: list[bytes] = []
        remaining = first.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 64 * 1024))
            require(type(piece) is bytes and bool(piece),
                    "reject a truncated authenticated owner: " + relative)
            remaining -= len(piece)
            pieces.append(piece)
        require(os.read(descriptor, 1) == b"",
                "reject trailing authenticated owner bytes: " + relative)
        raw = b"".join(pieces)
        last = os.fstat(descriptor)
        visible = os.stat(name, dir_fd=parent, follow_symlinks=False)
        require(
            len(raw) == expected_size and digest(raw) == expected
            and (first.st_dev, first.st_ino, first.st_size)
            == (last.st_dev, last.st_ino, last.st_size)
            and (first.st_dev, first.st_ino)
            == (visible.st_dev, visible.st_ino),
            "reject changed published owner bytes or identity: " + relative,
        )
        return owner_metadata(relative, first, expected), raw
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def checked_source_size(relative: str) -> int:
    checked_relative(relative)
    info = os.stat(ROOT / relative, follow_symlinks=False)
    require(
        stat.S_ISREG(info.st_mode) and info.st_nlink == 1
        and info.st_uid == os.geteuid()
        and 0 < info.st_size <= MAX_SOURCE_BYTES,
        "reject an unsafe V6 source-freeze owner",
    )
    return info.st_size


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and os.path.abspath(sys.executable) == PINNED_PYTHON,
        "use only the exact pinned stable CPython 3.14.6 interpreter",
    )


def decode_gzip_report(
    compressed: bytes, expected_size: int, expected_sha256: str,
    label: str,
) -> dict[str, Any]:
    require(
        type(compressed) is bytes and len(compressed) >= 10
        and compressed[:2] == b"\x1f\x8b"
        and compressed[4:8] == b"\x00\x00\x00\x00"
        and type(expected_size) is int
        and 0 < expected_size <= MAX_REPORT_BYTES,
        "require one bounded, deterministic, complete gzip report: " + label,
    )
    checked_digest(expected_sha256, label + " uncompressed digest")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        plain = decoder.decompress(compressed, MAX_REPORT_BYTES + 1)
        plain += decoder.flush()
    except (zlib.error, OSError, EOFError, ValueError) as error:
        raise ActivationError("reject altered source-build gzip: " + label) from error
    require(
        decoder.eof and not decoder.unused_data
        and not decoder.unconsumed_tail
        and len(plain) == expected_size
        and digest(plain) == expected_sha256,
        "reject truncated, concatenated, or changed source-build report: " + label,
    )
    return strict_json(plain, label)


def decode_process_stream(value: Any, label: str) -> bytes:
    require(
        type(value) is dict and value.get("complete") is True
        and type(value.get("bytes")) is int
        and 0 <= value["bytes"] <= MAX_REPORT_BYTES,
        "require a complete genuine compiler stream: " + label,
    )
    checked_digest(value.get("sha256"), label + " stream digest")
    encoded = value.get("base64")
    require(type(encoded) is str, "require the complete original process stream")
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise ActivationError("reject altered compiler stream: " + label) from error
    require(
        len(raw) == value["bytes"] and digest(raw) == value["sha256"],
        "authenticate every original compiler output byte: " + label,
    )
    return raw


def validate_phase_one(value: dict[str, Any]) -> None:
    denominator = value.get("denominator")
    runtime = value.get("runtime")
    gate = value.get("phase_gate")
    require(
        value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and type(denominator) is dict
        and denominator.get("final_required_case_execution_denominator") == 31_237
        and tuple(denominator.get("counted_suite_ids", ()))
        == tuple(name for name, _ in SUITES)
        and denominator.get(
            "private_upstream_methods_outside_public_denominator"
        ) == 13
        and type(runtime) is dict
        and runtime.get("python_implementation") == "CPython"
        and runtime.get("python_version") == "3.14.6"
        and type(gate) is dict and gate.get("status") == "PASS"
        and gate.get("final_holdout_authorized") is False,
        "preserve all 13 original suites, 31,237 cases, and 13 private waivers",
    )


def validate_native_phase_owner(
    value: Any, role: str, phase: str,
) -> dict[str, Any]:
    expected = NATIVE_ROLES[role]
    require(
        type(value) is dict
        and value.get("sha256") == expected["sha256"]
        and value.get("bytes") == expected["bytes"]
        and value.get("link_count") == 1
        and value.get("mode") == "0700"
        and type(value.get("device")) is int
        and type(value.get("inode")) is int
        and value["device"] > 0 and value["inode"] > 0
        and type(value.get("path")) is str
        and value["path"].startswith("/tmp/")
        and value["path"].endswith("/" + expected["filename"])
        and ("/" + phase + "/") in value["path"],
        "require the exact authenticated source-built " + role + " in " + phase,
    )
    return value


def validate_zig_report(
    protected: dict[str, bytes],
    owners: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    receipt = strict_json(protected[V11_RECEIPT], "actual Zig V11 durable receipt")
    archive = receipt.get("archive")
    recorded = owners[V11_ARCHIVE]
    require(
        receipt.get("schema")
        == "rebar-phase2-owned-zig-scanner-source-build-v11-"
           "durable-publication-receipt"
        and receipt.get("version") == 11
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == FAMILY
        and receipt.get("label") == BUILD_LABEL
        and receipt.get("source_sha256")
        == SUPPORT_OWNERS[
            "tools/reproduce_owned_zig_scanner_source_build_v11.py"
        ][0]
        and receipt.get("protocol_sha256")
        == SUPPORT_OWNERS[
            "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md"
        ][0]
        and receipt.get("contract_sha256")
        == SUPPORT_OWNERS[
            "oracle/phase2/zig-scanner-source-build-v11.json"
        ][0]
        and receipt.get("current_evidence_owner_count_before_publication") == 135
        and receipt.get("current_authenticated_reference_count_before_publication")
        == 140
        and receipt.get("expected_build_process_count_only_after_success") == 26
        and receipt.get("actual_build_process_count") == 26
        and receipt.get("actual_source_apply_count") == 2
        and receipt.get("candidate_imports") == 0
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("network_requests") == 0
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False
        and receipt.get("failure_preserved") is False
        and type(archive) is dict
        and archive.get("path") == V11_ARCHIVE
        and archive.get("sha256") == recorded["sha256"]
        and archive.get("bytes") == recorded["bytes"]
        and archive.get("device") == recorded["device"]
        and archive.get("inode") == recorded["inode"]
        and archive.get("mode") == "0600"
        and archive.get("link_count") == 1
        and archive.get("file_fsync") is True
        and archive.get("directory_fsync") is True,
        "require the real independently durable passing V11 Zig build",
    )
    report = decode_gzip_report(
        protected[V11_ARCHIVE],
        receipt["uncompressed_bytes"],
        receipt["uncompressed_sha256"],
        "actual complete two-role V11 Zig source-build report",
    )
    correctness = report.get("frozen_correctness")
    reproducibility = report.get("reproducibility")
    raw_elf = report.get("raw_elf_differences")
    processes = report.get("processes")
    phases = report.get("build_phases")
    require(
        report.get("schema") == "rebar-phase2-owned-zig-scanner-source-build-v11"
        and report.get("version") == 11
        and report.get("status") == "PASS"
        and report.get("family") == FAMILY
        and report.get("label") == BUILD_LABEL
        and report.get("source_sha256") == receipt["source_sha256"]
        and report.get("protocol_sha256") == receipt["protocol_sha256"]
        and report.get("contract_sha256") == receipt["contract_sha256"]
        and report.get("current_evidence_owner_count") == 135
        and report.get("current_authenticated_reference_count") == 140
        and report.get("historical_v21_evidence_owner_count") == 103
        and report.get("historical_v21_authenticated_reference_count") == 108
        and report.get("historical_zig_semantic_mismatch_count") == 1_764
        and report.get("expected_build_process_count_only_after_success") == 26
        and report.get("actual_build_process_count") == 26
        and report.get("actual_source_apply_count") == 2
        and type(correctness) is dict
        and correctness.get("python") == "3.14.6"
        and correctness.get("suite_count") == 13
        and correctness.get("case_execution_count") == 31_237
        and correctness.get("private_waiver_count") == 13
        and type(processes) is list and len(processes) == 26
        and type(phases) is list and len(phases) == 2
        and type(reproducibility) is dict
        and reproducibility.get("status") == "PASS"
        and reproducibility.get("independent_phase_count") == 2
        and reproducibility.get("byte_identical_native_role_count") == 2
        and reproducibility.get("compiler_process_count") == 26
        and reproducibility.get("source_apply_count") == 2
        and type(raw_elf) is dict
        and raw_elf.get("all_native_artifacts_byte_identical") is True
        and raw_elf.get("native_role_count") == 2
        and report.get("candidate_imports") == 0
        and report.get("candidate_processes_started") == 0
        and report.get("native_libraries_loaded") == 0
        and report.get("network_requests") == 0
        and report.get("hidden_cases_read") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("candidate_correctness") == "NOT MEASURED"
        and report.get("performance") == "NOT MEASURED"
        and report.get("memory") == "NOT MEASURED"
        and report.get("holdout") == "NOT OPENED"
        and report.get("winner_selected") is False,
        "verify complete original Zig success without claiming matching results",
    )
    pids: set[int] = set()
    for index, process in enumerate(processes):
        phase = PHASE_NAMES[index // len(PROCESS_ROLES)]
        role = PROCESS_ROLES[index % len(PROCESS_ROLES)]
        require(
            type(process) is dict
            and process.get("name") == role
            and process.get("phase") == phase
            and process.get("returncode") == 0
            and process.get("signal") is None
            and type(process.get("pid")) is int
            and process["pid"] > 0
            and process["pid"] not in pids
            and type(process.get("argv")) is list
            and bool(process["argv"])
            and all(type(part) is str for part in process["argv"])
            and type(process.get("environment")) is dict,
            "preserve all 26 real, correctly ordered Zig compiler processes",
        )
        pids.add(process["pid"])
        decode_process_stream(process.get("stdout"), phase + ":" + role + ":stdout")
        decode_process_stream(process.get("stderr"), phase + ":" + role + ":stderr")
    phase_roles: dict[str, dict[str, dict[str, Any]]] = {}
    for index, phase in enumerate(phases):
        phase_name = PHASE_NAMES[index]
        require(
            type(phase) is dict and phase.get("name") == phase_name,
            "preserve both independent original V11 source phases",
        )
        applied = phase.get("overlay_application")
        require(
            type(applied) is dict
            and applied.get("schema")
            == "rebar-phase2-owned-zig-scanner-capture-source-repair-v1"
            and applied.get("status") == "PASS"
            and applied.get("phase") == phase_name
            and applied.get("source_apply_count") == 1
            and applied.get("candidate_original_modified") is False
            and applied.get("derived_sha256") == DERIVED_BRIDGE_SHA256
            and applied.get("derived_bytes") == DERIVED_BRIDGE_BYTES,
            "authenticate each separately applied first-party scanner repair",
        )
        snapshots = phase.get("source_snapshots")
        outputs = phase.get("native_outputs")
        require(
            type(snapshots) is dict
            and set(snapshots) == set(ORIGINAL_SOURCES)
            and type(outputs) is dict and set(outputs) == set(ROLE_ORDER),
            "require the complete original first-party source and native closure",
        )
        for relative, (expected_sha256, expected_size) in ORIGINAL_SOURCES.items():
            snapshot = snapshots.get(relative)
            derived = relative == "candidates/zig/py_bridge.c"
            require(
                type(snapshot) is dict
                and snapshot.get("sha256")
                == (DERIVED_BRIDGE_SHA256 if derived else expected_sha256)
                and snapshot.get("bytes")
                == (DERIVED_BRIDGE_BYTES if derived else expected_size)
                and snapshot.get("link_count") == 1,
                "preserve the exact immutable or privately repaired Zig source",
            )
        phase_roles[phase_name] = {}
        for role in ROLE_ORDER:
            output = outputs[role]
            require(type(output) is dict,
                    "require a complete first-party native output: " + role)
            actual = validate_native_phase_owner(
                output.get("owner"), role, phase_name,
            )
            audit = output.get("independence_audit")
            require(
                type(audit) is dict
                and audit.get("role") == role
                and audit.get("external_regex_engine_count") == 0
                and audit.get("cross_family_engine_count") == 0
                and audit.get("stdlib_regex_engine_count") == 0
                and audit.get("legacy_rpath_count") == 0
                and audit.get("network_symbol_count") == 0,
                "reject regex delegation or unsafe native linkage: " + role,
            )
            if role == "engine":
                require(
                    audit.get("soname") == "_zig_probe.so"
                    and audit.get("native_loader_symbol_count") == 0,
                    "require the actual first-party Zig engine SONAME",
                )
            else:
                require(
                    audit.get("runpath") == "$ORIGIN"
                    and "_zig_probe.so" in audit.get("needed", [])
                    and audit.get("native_loader_symbol_count") == 0,
                    "require the authentic own-engine Zig bridge linkage",
                )
            phase_roles[phase_name][role] = actual
    reproducible_roles = reproducibility.get("roles")
    require(type(reproducible_roles) is dict,
            "authenticate the original independent reproducibility proof")
    for role in ROLE_ORDER:
        a = phase_roles["reference-a"][role]
        b = phase_roles["reference-b"][role]
        measured = reproducible_roles.get(role)
        require(
            (a["device"], a["inode"]) != (b["device"], b["inode"])
            and type(measured) is dict
            and measured.get("byte_identical") is True
            and measured.get("sha256") == NATIVE_ROLES[role]["sha256"]
            and measured.get("bytes") == NATIVE_ROLES[role]["bytes"]
            and measured.get("phase_owner_count") == 2,
            "require two genuinely reproduced distinct native " + role + " owners",
        )
    return {
        "receipt": receipt,
        "report": report,
        "phase_roles": phase_roles,
        "actual_build_process_count": 26,
        "actual_source_apply_count": 2,
        "historical_evidence_owner_count": 135,
        "historical_reference_count": 140,
    }


def validate_rust_report(
    protected: dict[str, bytes],
    owners: dict[str, dict[str, Any]],
) -> None:
    receipt = strict_json(protected[RUST_RECEIPT],
                          "actual Rust dual-overlay publication receipt")
    actual = owners[RUST_ARCHIVE]
    require(
        receipt.get("schema")
        == "rebar-phase2-owned-native-source-build-v11-"
           "durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == "rust"
        and receipt.get("label") == "phase2-v11-rust-dual-overlay"
        and receipt.get("source_sha256")
        == SUPPORT_OWNERS["tools/reproduce_owned_native_source_build_v11.py"][0]
        and receipt.get("protocol_sha256")
        == SUPPORT_OWNERS["oracle/phase2/NATIVE-SOURCE-BUILD-V11.md"][0]
        and receipt.get("contract_sha256")
        == SUPPORT_OWNERS["oracle/phase2/native-source-build-v11.json"][0]
        and receipt.get("archive_relative") == RUST_ARCHIVE
        and receipt.get("archive_sha256") == actual["sha256"]
        and receipt.get("archive_bytes") == actual["bytes"]
        and receipt.get("expected_actual_compiler_process_count") == 28
        and receipt.get("actual_compiler_process_count") == 28
        and receipt.get("public_overlay_apply_count") == 2
        and receipt.get("bridge_overlay_apply_count") == 2
        and receipt.get("public_derived_sha256")
        == "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
        and receipt.get("bridge_derived_sha256")
        == "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
        and receipt.get("historical_evidence_owner_count") == 137
        and receipt.get("historical_authenticated_reference_count") == 142
        and receipt.get("candidate_imports") == 0
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "preserve the actual 28-process independently repaired Rust result",
    )
    publication = receipt.get("archive_publication")
    require(
        type(publication) is dict
        and publication.get("bytes") == actual["bytes"]
        and publication.get("sha256") == actual["sha256"]
        and publication.get("device") == actual["device"]
        and publication.get("inode") == actual["inode"]
        and publication.get("exclusive_creation") is True
        and publication.get("file_fsync_completed") is True
        and publication.get("same_inode_readback_verified") is True,
        "authenticate independently published Rust evidence without touching Rust",
    )
    report = decode_gzip_report(
        protected[RUST_ARCHIVE],
        receipt["uncompressed_bytes"], receipt["uncompressed_sha256"],
        "actual original Rust dual-overlay source build",
    )
    processes = report.get("compiler_processes")
    require(
        report.get("schema")
        == "rebar-phase2-owned-native-source-build-v11-actual-dual-overlay-build"
        and report.get("version") == 11
        and report.get("status") == "PASS"
        and report.get("family") == "rust"
        and report.get("label") == "phase2-v11-rust-dual-overlay"
        and report.get("source_sha256") == receipt["source_sha256"]
        and report.get("protocol_sha256") == receipt["protocol_sha256"]
        and report.get("contract_sha256") == receipt["contract_sha256"]
        and report.get("expected_actual_compiler_process_count") == 28
        and report.get("actual_compiler_process_count") == 28
        and report.get("public_overlay_apply_count") == 2
        and report.get("bridge_overlay_apply_count") == 2
        and report.get("public_derived_sha256")
        == receipt["public_derived_sha256"]
        and report.get("bridge_derived_sha256")
        == receipt["bridge_derived_sha256"]
        and report.get("phase_count") == 2
        and type(processes) is list and len(processes) == 28
        and report.get("historical_evidence_owner_count") == 137
        and report.get("historical_authenticated_reference_count") == 142
        and report.get("candidate_imports") == 0
        and report.get("candidate_processes_started") == 0
        and report.get("native_libraries_loaded") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("hidden_cases_read") == 0
        and report.get("candidate_correctness") == "NOT MEASURED"
        and report.get("performance") == "NOT MEASURED"
        and report.get("memory") == "NOT MEASURED"
        and report.get("holdout") == "NOT OPENED"
        and report.get("winner_selected") is False,
        "preserve both genuinely independently applied Rust source repairs",
    )


def validate_published_v25(
    protected: dict[str, bytes],
    zig: dict[str, Any],
) -> None:
    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v25.inputs.json"],
        "published V25 inputs",
    )
    overview = strict_json(
        protected["docs/evidence/candidate-current-overview-v25.json"],
        "published V25 overview",
    )
    require(
        inputs.get("schema") == "rebar-candidate-current-overview-v25-inputs"
        and inputs.get("version") == 25
        and inputs.get("repository_evidence_owner_count") == 139
        and inputs.get("all_digest_addressed_history_path_count") == 144
        and inputs.get("preserved_v24_repository_evidence_owner_count") == 137
        and inputs.get("preserved_v24_digest_addressed_history_path_count") == 142
        and inputs.get("full_case_denominator") == 31_237
        and inputs.get("private_waiver_count") == 13
        and inputs.get("suite_count") == 13
        and inputs.get("candidate_qualified_count") == 0
        and inputs.get("final_holdout_opened") is False
        and inputs.get("final_comparison_cases_generated") is False
        and inputs.get("final_comparison_planned_case_count") == 4_194_304
        and inputs.get("performance") == "NOT MEASURED"
        and inputs.get("memory") == "NOT MEASURED"
        and inputs.get("winner_selected") is False,
        "authenticate exact current published V25, never a prior build snapshot",
    )
    snapshot = overview.get("snapshot")
    require(
        overview.get("schema") == "rebar-candidate-current-overview-v25-summary"
        and overview.get("status") == "PASS"
        and overview.get("repository_evidence_owner_count") == 139
        and overview.get("authenticated_digest_addressed_history_paths") == 144
        and overview.get("preserved_v24_repository_evidence_owner_count") == 137
        and overview.get("full_case_denominator") == 31_237
        and overview.get("suite_count") == 13
        and overview.get("private_waiver_count") == 13
        and overview.get("qualified_candidate_count") == 0
        and overview.get("c_repaired_semantic_mismatch_count") == 1_262
        and overview.get("c_repaired_verified_passing_case_count") == 7_325
        and overview.get("c_repaired_candidate_worker_count") == 13
        and overview.get("c_repaired_infrastructure_failure_count") == 0
        and overview.get("zig_scanner_repaired_build_process_count") == 26
        and overview.get("zig_scanner_repaired_source_apply_count") == 2
        and overview.get("rust_dual_overlay_repaired_build_process_count") == 28
        and overview.get("rust_dual_overlay_repaired_public_source_apply_count") == 2
        and overview.get("rust_dual_overlay_repaired_bridge_source_apply_count") == 2
        and overview.get("hidden_cases_read") == 0
        and overview.get("clock_samples") == 0
        and overview.get("timing_trials_run") == 0
        and overview.get("final_holdout_opened") is False
        and overview.get("final_comparison_cases_generated") is False
        and overview.get("performance") == "NOT MEASURED"
        and overview.get("memory") == "NOT MEASURED"
        and overview.get("winner_selected") is False
        and type(snapshot) is dict
        and snapshot.get("all_digest_addressed_history_path_count") == 144
        and snapshot.get("preserved_v24_repository_evidence_owner_count") == 137
        and snapshot.get("preserved_v24_digest_addressed_history_path_count") == 142
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("current_source_owner_count") == 25
        and snapshot.get("zig_actual_semantic_mismatch_count") == 1_764
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0,
        "preserve all actually published C, Zig, and Rust V25 evidence",
    )
    for document in (inputs, overview, snapshot):
        require(
            document.get("final_comparison_cases_generated") is False
            and document.get("final_comparison_planned_case_count") == 4_194_304
            and document.get("performance") == "NOT MEASURED"
            and document.get("memory") == "NOT MEASURED"
            and document.get("winner_selected") is False,
            "preserve the sealed holdout and unmeasured results in V25",
        )
    source_build = snapshot.get("zig_v11_scanner_repaired_source_build")
    input_build = inputs.get("current_repaired_zig_source_build")
    for value in (source_build, input_build):
        require(
            type(value) is dict
            and value.get("status") == "PASS"
            and value.get("build_status") == "PASS"
            and value.get("family") == FAMILY
            and value.get("label") == BUILD_LABEL
            and value.get("actual_build_process_count") == 26
            and value.get("actual_source_apply_count") == 2
            and value.get("independent_phase_count") == 2
            and value.get("byte_identical_native_role_count") == 2
            and type(value.get("archive")) is dict
            and value["archive"].get("path") == V11_ARCHIVE
            and value["archive"].get("sha256") == SUPPORT_OWNERS[V11_ARCHIVE][0]
            and type(value.get("receipt")) is dict
            and value["receipt"].get("path") == V11_RECEIPT
            and value["receipt"].get("sha256") == SUPPORT_OWNERS[V11_RECEIPT][0]
            and type(value.get("roles")) is dict,
            "bind both current V25 views to the actual passing Zig V11 build",
        )
        for role in ROLE_ORDER:
            recorded = value["roles"].get(role)
            require(
                type(recorded) is dict
                and recorded.get("sha256") == NATIVE_ROLES[role]["sha256"]
                and recorded.get("bytes") == NATIVE_ROLES[role]["bytes"]
                and recorded.get("byte_identical") is True
                and recorded.get("independent_phase_owner_count") == 2,
                "bind V25 to both real reproducible native roles: " + role,
            )
    rust = snapshot.get("rust_v11_dual_overlay_repaired_source_build")
    rust_input = inputs.get("current_repaired_rust_source_build")
    for value in (rust, rust_input):
        require(
            type(value) is dict
            and value.get("status") == "PASS"
            and value.get("build_status") == "PASS"
            and value.get("family") == "rust"
            and value.get("actual_build_process_count") == 28
            and value.get("actual_public_source_apply_count") == 2
            and value.get("actual_bridge_source_apply_count") == 2,
            "preserve both independent Rust source repairs without touching Rust",
        )
    campaign = inputs.get("current_complete_c_campaign")
    require(
        type(campaign) is dict
        and campaign.get("status") == "FAIL"
        and campaign.get("semantic_mismatch_count") == 1_262
        and campaign.get("verified_passing_case_count") == 7_325
        and campaign.get("actual_candidate_workers") == 13
        and campaign.get("infrastructure_failure_count") == 0
        and campaign.get("all_original_suite_evidence_preserved") is True,
        "preserve every actual completed C result without touching its target",
    )


def load_mature_primitives(raw: bytes) -> types.ModuleType:
    require(
        type(raw) is bytes and digest(raw) == SUPPORT_OWNERS[MATURE_SOURCE][0],
        "load only the exact committed mature dual-role activation source",
    )
    module = types.ModuleType("_rebar_owned_zig_v6_mature_v2_primitives")
    module.__file__ = str(ROOT / MATURE_SOURCE)
    module.__package__ = ""
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
    except (SyntaxError, ValueError, TypeError) as error:
        raise ActivationError("reject changed mature V2 source primitives") from error
    family = getattr(module, "FAMILIES", {}).get(FAMILY)
    require(
        getattr(module, "SCHEMA", None)
        == "rebar-phase2-verified-native-candidate-activation-v2"
        and getattr(module, "SOURCE_RELATIVE", None) == MATURE_SOURCE
        and getattr(module, "PROTOCOL_RELATIVE", None) == MATURE_PROTOCOL
        and type(family) is dict
        and family.get("binaries") == {
            "engine": "_zig_probe.so",
            "bridge": "_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        }
        and all(
            callable(getattr(module, name, None))
            for name in (
                "read_owned", "open_root", "write_fresh", "same_owner",
                "canonical_candidate_directory", "synchronize_directory",
            )
        )
        and getattr(module, "__name__", None)
        == "_rebar_owned_zig_v6_mature_v2_primitives",
        "authenticate only exact V2 no-follow durable journal primitives",
    )
    return module


def authenticate_context(
    source_pin: str, protocol_pin: str,
    contract_pin: str | None = None, *, retain: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    checked_digest(source_pin, "V6 source")
    checked_digest(protocol_pin, "V6 protocol")
    source_owner, _ = read_repository_owner(
        SOURCE_RELATIVE, source_pin, checked_source_size(SOURCE_RELATIVE),
    )
    protocol_owner, _ = read_repository_owner(
        PROTOCOL_RELATIVE, protocol_pin, checked_source_size(PROTOCOL_RELATIVE),
    )
    protected: dict[str, bytes] = {}
    owners: dict[str, dict[str, Any]] = {}
    for relative, (expected, expected_size) in sorted(SUPPORT_OWNERS.items()):
        owner, raw = read_repository_owner(relative, expected, expected_size)
        protected[relative] = raw
        owners[relative] = owner
    require(
        not any(
            target["relative"] in protected
            for target in NATIVE_ROLES.values()
        ),
        "never stat, open, hash, or touch either user-owned Zig native target",
    )
    validate_phase_one(strict_json(
        protected["oracle/phase1/p0-completeness-v1.json"],
        "unchanged original phase-one oracle",
    ))
    producer = strict_json(
        protected["oracle/phase2/six-family-p0-producer-v3.json"],
        "corrected immutable six-family original P0 producer",
    )
    require(
        producer.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
        and producer.get("version") == 3
        and producer.get("family_count") == 6
        and producer.get("source_owner_count") == 25
        and producer.get("suite_count") == 13
        and producer.get("case_execution_denominator") == 31_237,
        "bind future matching only to the unchanged corrected V3 P0 oracle",
    )
    zig = validate_zig_report(protected, owners)
    validate_rust_report(protected, owners)
    validate_published_v25(protected, zig)
    mature = load_mature_primitives(protected[MATURE_SOURCE])
    contract_owner = None
    if contract_pin is not None:
        checked_digest(contract_pin, "V6 contract")
        contract_owner, raw = read_repository_owner(
            CONTRACT_RELATIVE, contract_pin,
            checked_source_size(CONTRACT_RELATIVE),
        )
        validate_contract(
            strict_json(raw, "canonical V6 activation contract"),
            source_pin, protocol_pin,
        )
    result = {
        "schema": SCHEMA,
        "status": "PASS",
        "version": 6,
        "mode": "READ-ONLY DUAL-ROLE FROZEN CONTEXT",
        "family": FAMILY,
        "source": source_owner,
        "protocol": protocol_owner,
        "contract": contract_owner,
        "authenticated_support_owner_count": len(owners),
        "published_v25_evidence_owner_count": 139,
        "published_v25_authenticated_reference_count": 144,
        "zig_build_historical_evidence_owner_count": 135,
        "zig_build_historical_reference_count": 140,
        "actual_zig_build_process_count": 26,
        "actual_zig_source_repair_application_count": 2,
        "actual_rust_build_process_count": 28,
        "actual_rust_public_source_repair_count": 2,
        "actual_rust_bridge_source_repair_count": 2,
        "actual_c_semantic_mismatch_count": 1_262,
        "actual_c_candidate_worker_count": 13,
        "actual_c_verified_passing_case_executions": 7_325,
        "frozen_case_execution_count": 31_237,
        "frozen_suite_count": 13,
        "frozen_private_waiver_count": 13,
        "historical_zig_semantic_mismatch_count": 1_764,
        "native_role_count": 2,
        "source_freeze_original_targets_read": 0,
        "source_freeze_original_targets_statted": 0,
        "source_freeze_original_targets_modified": 0,
        "group_atomic": False,
        "exact_original_inode_hardlink_backup": "FUTURE EXPLICIT ACTIVATION ONLY",
        "restoration_order": list(RESTORATION_ORDER),
        **phase_boundary(),
    }
    retained = {
        "mature": mature, "protected": protected,
        "owners": owners, "zig": zig,
    } if retain else {}
    return result, retained


def checked_private_root(value: Any) -> str:
    require(
        type(value) is str
        and value.startswith("/tmp/" + PRIVATE_PREFIX)
        and "\x00" not in value and "\\" not in value
        and value == value.rstrip("/")
        and len(value.split("/")) == 3
        and len(value) > len("/tmp/" + PRIVATE_PREFIX)
        and len(value) <= 255,
        "use only one exact owner-only Zig V6 activation root",
    )
    return value


def mature_owner_matches(
    observed: Any, expected: dict[str, Any],
) -> bool:
    return (
        type(observed) is dict
        and observed.get("relative") == expected["relative"]
        and observed.get("sha256") == expected["sha256"]
        and observed.get("size_bytes") == expected["bytes"]
        and observed.get("device") == expected["device"]
        and observed.get("inode") == expected["inode"]
        and observed.get("mode") == expected["mode"]
        and observed.get("nlink") == expected["nlink"]
        and observed.get("uid") == expected["uid"]
    )


def exact_current_original(mature: types.ModuleType,
                           role: str) -> tuple[bytes, dict[str, Any]]:
    definition = NATIVE_ROLES[role]
    raw, owner = mature.read_owned(
        str(ROOT), definition["relative"], definition["original"]["sha256"],
        maximum=MAX_BINARY_BYTES, exact_size=definition["original"]["bytes"],
    )
    require(
        mature_owner_matches(owner, definition["original"]),
        "refuse an absent, linked, altered, or substituted original Zig "
        + role + " inode",
    )
    return raw, owner


def ensure_absent(directory: int, name: str) -> None:
    require(
        type(name) is str and "/" not in name
        and "\x00" not in name and name and len(name) < 240,
        "allow only an exact adjacent Zig-only staging filename",
    )
    try:
        os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise ActivationError(
        "refuse an existing, redirected, or user-owned adjacent native name"
    )


def private_control(
    mature: types.ModuleType, root: str, filename: str, document: dict[str, Any],
) -> dict[str, Any]:
    checked_private_root(root)
    checked_relative(filename)
    require("/" not in filename, "create only one exact private control owner")
    return mature.write_fresh(root, filename, canonical(document))


def validated_phase_bytes(
    mature: types.ModuleType, owner: dict[str, Any], role: str,
) -> bytes:
    require(
        type(owner) is dict and type(owner.get("path")) is str
        and owner["path"].startswith("/tmp/")
        and owner["path"].endswith("/" + NATIVE_ROLES[role]["filename"]),
        "read only the recorded first-phase source-built native artifact",
    )
    recorded_path = Path(owner["path"])
    require(
        recorded_path.name == NATIVE_ROLES[role]["filename"]
        and str(recorded_path.parent).startswith("/tmp/"),
        "read only the exact recorded private build-phase role owner",
    )
    raw, observed = mature.read_owned(
        str(recorded_path.parent), recorded_path.name,
        NATIVE_ROLES[role]["sha256"],
        maximum=MAX_BINARY_BYTES, exact_size=NATIVE_ROLES[role]["bytes"],
    )
    require(
        observed["device"] == owner["device"]
        and observed["inode"] == owner["inode"]
        and observed["nlink"] == 1
        and observed["mode"] == 0o700,
        "reject a replaced original source-phase native " + role,
    )
    return raw


def sync_candidate_directory(directory: int,
                             before: os.stat_result) -> None:
    os.fsync(directory)
    after = os.fstat(directory)
    require(
        stat.S_ISDIR(after.st_mode)
        and (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
        "reject a swapped candidate directory during durable Zig promotion",
    )


def write_adjacent_stage(
    directory: int, filename: str, data: bytes, final_mode: int,
) -> dict[str, Any]:
    ensure_absent(directory, filename)
    descriptor = os.open(
        filename,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        0o600,
        dir_fd=directory,
    )
    try:
        first = os.fstat(descriptor)
        require(
            stat.S_ISREG(first.st_mode)
            and first.st_uid == os.geteuid()
            and first.st_nlink == 1
            and stat.S_IMODE(first.st_mode) == 0o600,
            "create only an exclusive, no-follow, mode-0600 native stage",
        )
        offset = 0
        while offset < len(data):
            amount = os.write(descriptor, data[offset:])
            require(type(amount) is int and amount > 0,
                    "reject incomplete source-built staged bytes")
            offset += amount
        if final_mode != 0o600:
            os.fchmod(descriptor, final_mode)
        os.fsync(descriptor)
        last = os.fstat(descriptor)
        require(
            (first.st_dev, first.st_ino) == (last.st_dev, last.st_ino)
            and last.st_nlink == 1
            and last.st_size == len(data)
            and stat.S_IMODE(last.st_mode) == final_mode,
            "reject a swapped, partial, linked, or incorrectly moded native stage",
        )
        return {
            "device": last.st_dev,
            "inode": last.st_ino,
            "bytes": last.st_size,
            "mode": last.st_mode & 0o777,
            "nlink": last.st_nlink,
            "uid": last.st_uid,
            "sha256": digest(data),
            "filename": filename,
        }
    finally:
        os.close(descriptor)


def validate_actual_activation_options(options: argparse.Namespace) -> None:
    require(
        options.family == FAMILY
        and options.build_label == BUILD_LABEL
        and options.build_archive_sha256 == SUPPORT_OWNERS[V11_ARCHIVE][0]
        and options.build_receipt_sha256 == SUPPORT_OWNERS[V11_RECEIPT][0]
        and options.native_engine_sha256 == NATIVE_ROLES["engine"]["sha256"]
        and options.native_bridge_sha256 == NATIVE_ROLES["bridge"]["sha256"]
        and options.native_engine_bytes == NATIVE_ROLES["engine"]["bytes"]
        and options.native_bridge_bytes == NATIVE_ROLES["bridge"]["bytes"],
        "independently caller-pin both real V11 native roles and build owners",
    )


def restore_exact_inodes(
    mature: types.ModuleType, root: str, journal: dict[str, Any],
    journal_sha256: str,
) -> dict[str, Any]:
    checked_private_root(root)
    checked_digest(journal_sha256, "exact-inode private journal")
    require(
        journal.get("schema") == JOURNAL_SCHEMA
        and journal.get("status") == "PREPARED"
        and journal.get("family") == FAMILY
        and journal.get("activation_root") == root
        and journal.get("group_atomic") is False
        and journal.get("build_archive_sha256") == SUPPORT_OWNERS[V11_ARCHIVE][0]
        and journal.get("build_receipt_sha256") == SUPPORT_OWNERS[V11_RECEIPT][0]
        and type(journal.get("roles")) is dict
        and set(journal["roles"]) == set(ROLE_ORDER),
        "recover only the complete V6 two-target durable Zig journal",
    )
    repository, directory = mature.canonical_candidate_directory()
    restored: dict[str, dict[str, Any]] = {}
    try:
        directory_before = os.fstat(directory)
        for role in RESTORATION_ORDER:
            definition = NATIVE_ROLES[role]
            entry = journal["roles"][role]
            target = definition["filename"]
            backup = entry.get("backup_filename")
            require(
                type(entry) is dict and entry.get("role") == role
                and entry.get("relative") == definition["relative"]
                and entry.get("original") == definition["original"]
                and entry.get("native_sha256") == definition["sha256"]
                and entry.get("native_bytes") == definition["bytes"]
                and type(backup) is str
                and backup.startswith(".rebar-v6-zig-original-")
                and backup.endswith("-" + target)
                and "/" not in backup,
                "reject a substituted cross-family recovery role: " + role,
            )
            try:
                current = os.stat(
                    target, dir_fd=directory, follow_symlinks=False,
                )
            except FileNotFoundError as error:
                raise ActivationError(
                    "refuse a missing originally present Zig target: " + role
                ) from error
            require(
                stat.S_ISREG(current.st_mode)
                and current.st_uid == os.geteuid(),
                "refuse a symlinked, unrelated, or foreign native target",
            )
            original = definition["original"]
            if (
                current.st_dev == original["device"]
                and current.st_ino == original["inode"]
                and current.st_nlink == 2
                and current.st_uid == original["uid"]
                and current.st_size == original["bytes"]
                and stat.S_IMODE(current.st_mode) == original["mode"]
            ):
                link_raw, _ = mature.read_owned(
                    root, "link-intent-" + role + ".json", None,
                    maximum=MAX_SOURCE_BYTES, private=True,
                )
                link_intent = strict_json(
                    link_raw, "durable exact-original hardlink intention",
                )
                require(
                    link_intent.get("schema") == INTENTION_SCHEMA
                    and link_intent.get("status") == "PREPARED"
                    and link_intent.get("operation") == "HARDLINK_BACKUP"
                    and link_intent.get("family") == FAMILY
                    and link_intent.get("activation_root") == root
                    and link_intent.get("recovery_journal_sha256")
                    == journal_sha256
                    and link_intent.get("role") == role
                    and link_intent.get("target") == definition["relative"]
                    and link_intent.get("backup_filename") == backup
                    and link_intent.get("original") == original
                    and link_intent.get("group_atomic") is False,
                    "refuse an unauthenticated original-inode hardlink",
                )
                linked_backup = os.stat(
                    backup, dir_fd=directory, follow_symlinks=False,
                )
                require(
                    stat.S_ISREG(linked_backup.st_mode)
                    and linked_backup.st_dev == current.st_dev
                    and linked_backup.st_ino == current.st_ino
                    and linked_backup.st_nlink == 2
                    and linked_backup.st_uid == original["uid"]
                    and linked_backup.st_size == original["bytes"]
                    and stat.S_IMODE(linked_backup.st_mode)
                    == original["mode"],
                    "refuse to remove any unauthenticated original hardlink",
                )
                os.unlink(backup, dir_fd=directory)
                sync_candidate_directory(directory, directory_before)
                _, observed = exact_current_original(mature, role)
                restored[role] = observed
                continue
            if (
                current.st_dev == original["device"]
                and current.st_ino == original["inode"]
                and current.st_nlink == 1
                and stat.S_IMODE(current.st_mode) == original["mode"]
            ):
                try:
                    os.stat(backup, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    _, observed = exact_current_original(mature, role)
                    restored[role] = observed
                    continue
                raise ActivationError(
                    "refuse an unexplained duplicate original Zig inode"
                )
            intent_name = "promotion-intent-" + role + ".json"
            intent_raw, _ = mature.read_owned(
                root, intent_name, None,
                maximum=MAX_SOURCE_BYTES, private=True,
            )
            intent = strict_json(intent_raw, "durable promotion intention")
            require(
                intent.get("schema") == INTENTION_SCHEMA
                and intent.get("status") == "PREPARED"
                and intent.get("operation") == "PROMOTE"
                and intent.get("family") == FAMILY
                and intent.get("activation_root") == root
                and intent.get("recovery_journal_sha256") == journal_sha256
                and intent.get("role") == role
                and intent.get("target") == definition["relative"]
                and intent.get("native_sha256") == definition["sha256"]
                and intent.get("native_bytes") == definition["bytes"]
                and intent.get("original") == original
                and current.st_nlink == 1
                and current.st_size == definition["bytes"]
                and stat.S_IMODE(current.st_mode) == original["mode"],
                "refuse recovery of an unjournaled or altered promoted target",
            )
            promoted_raw, promoted_owner = mature.read_owned(
                str(ROOT), definition["relative"], definition["sha256"],
                maximum=MAX_BINARY_BYTES, exact_size=definition["bytes"],
            )
            require(
                digest(promoted_raw) == definition["sha256"]
                and promoted_owner["device"] == current.st_dev
                and promoted_owner["inode"] == current.st_ino,
                "never overwrite user-modified promoted native bytes",
            )
            try:
                retained = os.stat(
                    backup, dir_fd=directory, follow_symlinks=False,
                )
            except FileNotFoundError as error:
                raise ActivationError(
                    "refuse exact-inode recovery without its genuine backup"
                ) from error
            require(
                stat.S_ISREG(retained.st_mode)
                and retained.st_dev == original["device"]
                and retained.st_ino == original["inode"]
                and retained.st_nlink == 1
                and retained.st_uid == original["uid"]
                and stat.S_IMODE(retained.st_mode) == original["mode"]
                and retained.st_size == original["bytes"],
                "never restore a copied, substituted, or linked original inode",
            )
            restore_intention = {
                "schema": INTENTION_SCHEMA,
                "status": "PREPARED",
                "operation": "RESTORE",
                "family": FAMILY,
                "activation_root": root,
                "recovery_journal_sha256": journal_sha256,
                "role": role,
                "target": definition["relative"],
                "backup_filename": backup,
                "original": original,
                "group_atomic": False,
            }
            private_control(
                mature, root, "restore-intent-" + role + ".json",
                restore_intention,
            )
            mature.synchronize_directory(root)
            os.replace(
                backup, target, src_dir_fd=directory, dst_dir_fd=directory,
            )
            sync_candidate_directory(directory, directory_before)
            _, observed = exact_current_original(mature, role)
            restored[role] = observed
        require(
            set(restored) == set(ROLE_ORDER),
            "restore both exact original Zig target inodes",
        )
    finally:
        os.close(directory)
        os.close(repository)
    document = {
        "schema": RESTORATION_SCHEMA,
        "status": "PASS",
        "version": 6,
        "family": FAMILY,
        "activation_root": root,
        "recovery_journal_sha256": journal_sha256,
        "group_atomic": False,
        "restoration_order": list(RESTORATION_ORDER),
        "restored_targets": restored,
        "original_inode_preserved": True,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    owner = private_control(
        mature, root, "restoration-receipt.json", document,
    )
    return {
        "schema": SCHEMA + "-recovery-result",
        "status": "PASS",
        "version": 6,
        "family": FAMILY,
        "activation_root": root,
        "recovery_journal_sha256": journal_sha256,
        "restoration_receipt": owner,
        "restoration": document,
        "group_atomic": False,
        "original_inode_preserved": True,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def activate(options: argparse.Namespace) -> dict[str, Any]:
    validate_actual_activation_options(options)
    context, retained = authenticate_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True,
    )
    require(context.get("status") == "PASS",
            "authenticate the full published source freeze before activation")
    mature = retained["mature"]
    report = retained["zig"]["report"]
    phase = retained["zig"]["phase_roles"]["reference-a"]
    payload: dict[str, bytes] = {}
    originals: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        payload[role] = validated_phase_bytes(mature, phase[role], role)
        _, originals[role] = exact_current_original(mature, role)
    root = tempfile.mkdtemp(prefix=PRIVATE_PREFIX, dir="/tmp")
    checked_private_root(root)
    descriptor = mature.open_root(root, private=True)
    os.close(descriptor)
    token = os.urandom(18).hex()
    require(
        len(token) == 36
        and all(part in "0123456789abcdef" for part in token),
        "require unpredictable owner-only adjacent Zig backup names",
    )
    entries: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        filename = NATIVE_ROLES[role]["filename"]
        entries[role] = {
            "role": role,
            "relative": NATIVE_ROLES[role]["relative"],
            "original": dict(NATIVE_ROLES[role]["original"]),
            "backup_filename":
                ".rebar-v6-zig-original-" + token + "-" + filename,
            "stage_filename":
                ".rebar-v6-zig-stage-" + token + "-" + filename,
            "native_sha256": NATIVE_ROLES[role]["sha256"],
            "native_bytes": NATIVE_ROLES[role]["bytes"],
        }
    journal = {
        "schema": JOURNAL_SCHEMA,
        "status": "PREPARED",
        "version": 6,
        "family": FAMILY,
        "activation_root": root,
        "build_label": BUILD_LABEL,
        "build_source_sha256": report["source_sha256"],
        "build_protocol_sha256": report["protocol_sha256"],
        "build_contract_sha256": report["contract_sha256"],
        "build_archive_sha256": SUPPORT_OWNERS[V11_ARCHIVE][0],
        "build_receipt_sha256": SUPPORT_OWNERS[V11_RECEIPT][0],
        "activation_source_sha256": options.source_sha256,
        "activation_protocol_sha256": options.protocol_sha256,
        "activation_contract_sha256": options.contract_sha256,
        "roles": entries,
        "role_order": list(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "group_atomic": False,
        "exact_original_inode_backup": "ADJACENT SAME-DEVICE HARDLINK",
        "reportless_recovery": True,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "winner_selected": False,
    }
    journal_owner = private_control(
        mature, root, "recovery-journal.json", journal,
    )
    mature.synchronize_directory(root)
    repository, directory = mature.canonical_candidate_directory()
    created_links: list[str] = []
    try:
        before = os.fstat(directory)
        for role in ROLE_ORDER:
            entry = entries[role]
            definition = NATIVE_ROLES[role]
            filename = definition["filename"]
            backup = entry["backup_filename"]
            stage = entry["stage_filename"]
            ensure_absent(directory, backup)
            ensure_absent(directory, stage)
            _, current_owner = exact_current_original(mature, role)
            require(
                mature_owner_matches(current_owner, definition["original"]),
                "refuse a changed user-owned original before hardlink backup",
            )
            link_intent = {
                "schema": INTENTION_SCHEMA,
                "status": "PREPARED",
                "operation": "HARDLINK_BACKUP",
                "family": FAMILY,
                "activation_root": root,
                "recovery_journal_sha256": journal_owner["sha256"],
                "role": role,
                "target": definition["relative"],
                "backup_filename": backup,
                "original": dict(definition["original"]),
                "group_atomic": False,
            }
            private_control(
                mature, root, "link-intent-" + role + ".json", link_intent,
            )
            mature.synchronize_directory(root)
            os.link(
                filename, backup, src_dir_fd=directory,
                dst_dir_fd=directory, follow_symlinks=False,
            )
            linked = os.stat(
                filename, dir_fd=directory, follow_symlinks=False,
            )
            backup_link = os.stat(
                backup, dir_fd=directory, follow_symlinks=False,
            )
            require(
                (linked.st_dev, linked.st_ino)
                == (definition["original"]["device"],
                    definition["original"]["inode"])
                and (backup_link.st_dev, backup_link.st_ino)
                == (linked.st_dev, linked.st_ino)
                and linked.st_nlink == 2
                and backup_link.st_nlink == 2
                and stat.S_IMODE(linked.st_mode)
                == definition["original"]["mode"],
                "retain the exact genuine same-device original Zig inode",
            )
            created_links.append(role)
            sync_candidate_directory(directory, before)
            promotion_intent = {
                "schema": INTENTION_SCHEMA,
                "status": "PREPARED",
                "operation": "PROMOTE",
                "family": FAMILY,
                "activation_root": root,
                "recovery_journal_sha256": journal_owner["sha256"],
                "role": role,
                "target": definition["relative"],
                "backup_filename": backup,
                "stage_filename": stage,
                "original": dict(definition["original"]),
                "native_sha256": definition["sha256"],
                "native_bytes": definition["bytes"],
                "group_atomic": False,
                "initial_stage_mode": "0600",
                "promoted_mode": "0700",
            }
            private_control(
                mature, root, "promotion-intent-" + role + ".json",
                promotion_intent,
            )
            mature.synchronize_directory(root)
            staged = write_adjacent_stage(
                directory, stage, payload[role], definition["original"]["mode"],
            )
            require(
                staged["sha256"] == definition["sha256"]
                and staged["bytes"] == definition["bytes"],
                "never promote an unauthenticated Zig stage",
            )
            sync_candidate_directory(directory, before)
            os.replace(
                stage, filename, src_dir_fd=directory, dst_dir_fd=directory,
            )
            sync_candidate_directory(directory, before)
            _, promoted = mature.read_owned(
                str(ROOT), definition["relative"], definition["sha256"],
                maximum=MAX_BINARY_BYTES, exact_size=definition["bytes"],
            )
            require(
                promoted["device"] == staged["device"]
                and promoted["inode"] == staged["inode"]
                and promoted["nlink"] == 1
                and promoted["mode"] == definition["original"]["mode"],
                "prove the promoted exact stage inode and original native mode",
            )
        final_targets: dict[str, dict[str, Any]] = {}
        for role in ROLE_ORDER:
            definition = NATIVE_ROLES[role]
            _, selected = mature.read_owned(
                str(ROOT), definition["relative"], definition["sha256"],
                maximum=MAX_BINARY_BYTES, exact_size=definition["bytes"],
            )
            final_targets[role] = selected
    except BaseException:
        os.close(directory)
        os.close(repository)
        restore_exact_inodes(mature, root, journal, journal_owner["sha256"])
        raise
    os.close(directory)
    os.close(repository)
    actual = {
        "schema": REPORT_SCHEMA,
        "status": "PASS",
        "version": 6,
        "family": FAMILY,
        "build_label": BUILD_LABEL,
        "activation_root": root,
        "recovery_journal": journal_owner,
        "canonical_targets": final_targets,
        "original_targets": originals,
        "build_archive_sha256": SUPPORT_OWNERS[V11_ARCHIVE][0],
        "build_receipt_sha256": SUPPORT_OWNERS[V11_RECEIPT][0],
        "actual_compiler_process_count": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "group_atomic": False,
        "exact_original_inode_backups_retained": True,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    try:
        report_owner = private_control(
            mature, root, "activation-report.json", actual,
        )
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "status": "PASS",
            "activation_status": "PASS",
            "version": 6,
            "family": FAMILY,
            "activation_root": root,
            "activation_report": report_owner,
            "recovery_journal": journal_owner,
            "group_atomic": False,
            "exact_original_inode_backups_retained": True,
            "candidate_qualified": False,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "winner_selected": False,
        }
        receipt_owner = private_control(
            mature, root, "activation-receipt.json", receipt,
        )
    except BaseException:
        restore_exact_inodes(mature, root, journal, journal_owner["sha256"])
        raise
    return {
        "schema": SCHEMA + "-activation-result",
        "status": "PASS",
        "version": 6,
        "family": FAMILY,
        "activation_root": root,
        "report": report_owner,
        "receipt": receipt_owner,
        "recovery_journal": journal_owner,
        "roles": final_targets,
        "group_atomic": False,
        "original_inodes_preserved_in_adjacent_backups": True,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def recover(options: argparse.Namespace) -> dict[str, Any]:
    context, retained = authenticate_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True,
    )
    require(context.get("status") == "PASS" and options.family == FAMILY,
            "authenticate the published V6 freeze before Zig recovery")
    root = checked_private_root(options.activation_root)
    checked_digest(options.recovery_journal_sha256, "actual recovery journal")
    mature = retained["mature"]
    raw, owner = mature.read_owned(
        root, "recovery-journal.json", options.recovery_journal_sha256,
        maximum=MAX_REPORT_BYTES, private=True,
    )
    journal = strict_json(raw, "actual durable two-role recovery journal")
    return restore_exact_inodes(mature, root, journal, owner["sha256"])


class SyntheticSandbox:
    """Block all external effects while evaluating hostile synthetic controls."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {
            "filesystem": 0,
            "process": 0,
            "thread": 0,
            "clock": 0,
            "network": 0,
            "native": 0,
            "import": 0,
        }

    def deny(self, kind: str) -> Any:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise SourceOnlyEffect(
                "source-only Zig activation cannot access " + kind
            )
        return blocked

    def install(self, owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            self.previous.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def __enter__(self) -> "SyntheticSandbox":
        for owner, name in (
            (builtins, "open"), (io, "open"),
            (os, "open"), (os, "read"), (os, "write"),
            (os, "stat"), (os, "lstat"), (os, "fstat"),
            (os, "mkdir"), (os, "makedirs"), (os, "link"),
            (os, "replace"), (os, "rename"), (os, "unlink"),
            (os, "remove"), (os, "fsync"), (os, "fchmod"),
            (os, "urandom"), (tempfile, "mkdtemp"),
        ):
            self.install(owner, name, self.deny("filesystem"))
        for owner, name in (
            (subprocess, "run"), (subprocess, "Popen"),
            (subprocess, "call"), (subprocess, "check_output"),
        ):
            self.install(owner, name, self.deny("process"))
        for owner, name in (
            (time, "time"), (time, "time_ns"),
            (time, "monotonic"), (time, "monotonic_ns"),
            (time, "perf_counter"), (time, "perf_counter_ns"),
            (time, "sleep"), (time, "clock_gettime"),
        ):
            self.install(owner, name, self.deny("clock"))
        for owner, name in (
            (socket, "socket"), (socket, "create_connection"),
            (socket, "getaddrinfo"),
        ):
            self.install(owner, name, self.deny("network"))
        self.install(ctypes, "CDLL", self.deny("native"))
        self.install(importlib, "import_module", self.deny("import"))
        self.install(threading.Thread, "start", self.deny("thread"))
        return self

    def __exit__(self, *_: Any) -> None:
        for owner, name, previous in reversed(self.previous):
            setattr(owner, name, previous)


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "V6 source")
    checked_digest(protocol_pin, "V6 protocol")
    checked_digest(contract_pin, "V6 contract")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(label: str, value: Any) -> None:
        require(value is True, "a genuine V6 synthetic control failed: " + label)
        accepted.append(label)

    def reject(label: str, operation: Any) -> None:
        try:
            operation()
        except (ActivationError, SourceOnlyEffect, TypeError, ValueError,
                UnicodeError, OverflowError, OSError, RecursionError,
                zlib.error):
            rejected.append(label)
            return
        raise ActivationError("a hostile V6 synthetic control escaped: " + label)

    with SyntheticSandbox() as sandbox:
        contract = contract_document(source_pin, protocol_pin)
        accept(
            "complete-canonical-v6-dual-role-contract",
            validate_contract(contract, source_pin, protocol_pin) == contract,
        )
        accept("exact-original-thirteen-suite-denominator",
               len(SUITES) == 13
               and len({name for name, _ in SUITES}) == 13
               and sum(count for _, count in SUITES) == 31_237)
        accept("exact-current-v25-history-139-144",
               contract["published_v25_history"][
                   "authoritative_evidence_owner_count"
               ] == 139
               and contract["published_v25_history"][
                   "authenticated_reference_count"
               ] == 144)
        accept("preserve-distinct-actual-zig-build-history-135-140",
               contract["actual_zig_v11_build"][
                   "historical_evidence_owner_count_at_build"
               ] == 135
               and contract["actual_zig_v11_build"][
                   "historical_reference_count_at_build"
               ] == 140)
        accept("preserve-real-26-process-two-phase-zig-build",
               contract["actual_zig_v11_build"][
                   "actual_compiler_process_count"
               ] == 26
               and contract["actual_zig_v11_build"][
                   "independent_source_phase_count"
               ] == 2)
        accept("preserve-real-28-process-dual-overlay-rust-build",
               contract["actual_rust_v11_build"][
                   "actual_compiler_process_count"
               ] == 28
               and contract["actual_rust_v11_build"][
                   "public_overlay_application_count"
               ] == 2
               and contract["actual_rust_v11_build"][
                   "bridge_overlay_application_count"
               ] == 2)
        accept("preserve-all-actual-original-c-losses",
               contract["published_v25_history"][
                   "actual_c_semantic_mismatches"
               ] == 1_262
               and contract["published_v25_history"][
                   "actual_c_candidate_workers"
               ] == 13)
        accept("exact-two-owned-zig-native-targets",
               contract["activation_policy"]["canonical_targets"]
               == [NATIVE_ROLES[role]["relative"] for role in ROLE_ORDER])
        accept(
            "exact-owner-only-private-root-shape",
            checked_private_root(
                "/tmp/" + PRIVATE_PREFIX + "synthetic-token"
            ) == "/tmp/" + PRIVATE_PREFIX + "synthetic-token",
        )
        accept("two-present-original-exact-user-inodes",
               tuple(
                   item["original"]["inode"]
                   for item in contract["actual_zig_v11_build"]["roles"]
               ) == (431_260, 431_274))
        accept("no-original-zig-native-target-inspected",
               all(
                   item["original_target_inspected_in_source_freeze"] is False
                   for item in contract["actual_zig_v11_build"]["roles"]
               ))
        accept("truthful-individually-atomic-dual-target-promotion",
               contract["activation_policy"]["group_atomic"] is False
               and contract["activation_policy"][
                   "each_file_replacement_individually_atomic"
               ] is True)
        accept("real-adjacent-original-inode-hardlink-required",
               contract["activation_policy"][
                   "original_hardlink_count_before_backup"
               ] == 1
               and contract["activation_policy"][
                   "original_hardlink_count_during_backup"
               ] == 2
               and contract["activation_policy"][
                   "original_hardlink_count_after_restoration"
               ] == 1)
        accept("reverse-bridge-before-engine-recovery",
               contract["activation_policy"]["fixed_restoration_order"]
               == ["bridge", "engine"])
        accept("no-stale-byte-copy-restoration",
               contract["immutable_dual_role_predecessor"][
                   "v2_byte_copy_restoration_allowed"
               ] is False)
        accept("exact-derived-owned-scanner-bridge",
               contract["actual_zig_v11_build"][
                   "scanner_derived_bridge_sha256"
               ] == DERIVED_BRIDGE_SHA256)
        accept("all-synthetic-source-boundary-effects-zero",
               contract["phase_boundary"] == phase_boundary())
        accept("finite-canonical-roundtrip",
               strict_json(canonical(contract), "synthetic V6 contract")
               == contract)
        for value in (
            "", "/", "/tmp", "../escape", "a/../b", "a//b",
            "a\\b", "a\x00b", None, 1,
        ):
            reject("reject-relative-owner-" + repr(value),
                   lambda item=value: checked_relative(item))
        for value in ("", "a" * 63, "a" * 65, "A" * 64,
                      "z" * 64, None, 1):
            reject("reject-digest-" + repr(value),
                   lambda item=value: checked_digest(item, "hostile"))
        for value in (
            "", "/tmp", "/tmp/" + PRIVATE_PREFIX,
            "/tmp/" + PRIVATE_PREFIX + "bad/child",
            "/tmp/" + PRIVATE_PREFIX + "../escaped",
            str(ROOT), None,
        ):
            reject("reject-private-root-" + repr(value),
                   lambda item=value: checked_private_root(item))
        mutations = (
            ("invent-group-atomic",
             lambda item: item["activation_policy"].update({"group_atomic": True})),
            ("erase-exact-inode-backup",
             lambda item: item["activation_policy"].update({
                 "exact_original_inode_preservation": "BYTE COPY",
             })),
            ("substitute-current-history",
             lambda item: item["published_v25_history"].update({
                 "authoritative_evidence_owner_count": 135,
             })),
            ("rewrite-actual-zig-build-history",
             lambda item: item["actual_zig_v11_build"].update({
                 "historical_evidence_owner_count_at_build": 139,
             })),
            ("invent-candidate-qualification",
             lambda item: item["phase_boundary"].update({
                 "qualified_candidate_count": 1,
             })),
            ("remove-one-native-role",
             lambda item: item["actual_zig_v11_build"]["roles"].pop()),
            ("substitute-original-user-inode",
             lambda item: item["actual_zig_v11_build"]["roles"][0][
                 "original"
             ].update({"inode": 431_261})),
            ("reverse-recovery-order",
             lambda item: item["activation_policy"].update({
                 "fixed_restoration_order": ["engine", "bridge"],
             })),
            ("invent-source-only-canonical-stat",
             lambda item: item["phase_boundary"].update({
                 "canonical_target_stats": 1,
             })),
            ("invent-source-only-activation",
             lambda item: item["phase_boundary"].update({
                 "native_activations_started": 1,
             })),
            ("weaken-real-zig-process-count",
             lambda item: item["actual_zig_v11_build"].update({
                 "actual_compiler_process_count": 25,
             })),
            ("erase-real-rust-overlay",
             lambda item: item["actual_rust_v11_build"].update({
                 "public_overlay_application_count": 1,
             })),
            ("erase-real-c-semantic-failures",
             lambda item: item["published_v25_history"].update({
                 "actual_c_semantic_mismatches": 0,
             })),
            ("claim-open-holdout",
             lambda item: item["phase_boundary"].update({
                 "holdout": "OPENED",
             })),
        )
        for label, mutation in mutations:
            def forged(edit: Any = mutation) -> None:
                value = strict_json(
                    canonical(contract), "synthetic contract mutation",
                )
                edit(value)
                validate_contract(value, source_pin, protocol_pin)
            reject(label, forged)
        probes = (
            ("block-builtin-open",
             lambda: builtins.open("forbidden", "rb")),
            ("block-io-open",
             lambda: io.open("forbidden", "rb")),
            ("block-canonical-target-stat",
             lambda: os.stat(NATIVE_ROLES["engine"]["relative"])),
            ("block-canonical-target-open",
             lambda: os.open(NATIVE_ROLES["bridge"]["relative"], os.O_RDONLY)),
            ("block-source-read",
             lambda: os.read(-1, 1)),
            ("block-file-write",
             lambda: os.write(-1, b"x")),
            ("block-source-only-hardlink",
             lambda: os.link("x", "y")),
            ("block-source-only-replacement",
             lambda: os.replace("x", "y")),
            ("block-source-only-unlink",
             lambda: os.unlink("x")),
            ("block-source-only-directory",
             lambda: os.mkdir("x")),
            ("block-source-only-fsync",
             lambda: os.fsync(-1)),
            ("block-source-only-random",
             lambda: os.urandom(8)),
            ("block-source-only-private-root",
             lambda: tempfile.mkdtemp(prefix=PRIVATE_PREFIX)),
            ("block-source-only-process",
             lambda: subprocess.run(("forbidden",))),
            ("block-source-only-process-spawn",
             lambda: subprocess.Popen(("forbidden",))),
            ("block-source-only-network",
             lambda: socket.create_connection(("invalid", 1))),
            ("block-source-only-dns",
             lambda: socket.getaddrinfo("invalid", 1)),
            ("block-source-only-native-library",
             lambda: ctypes.CDLL("forbidden")),
            ("block-zig-candidate-import",
             lambda: importlib.import_module("candidates.zig_candidate")),
            ("block-cross-family-candidate-import",
             lambda: importlib.import_module("candidates.vm_candidate")),
            ("block-source-only-thread",
             lambda: threading.Thread(target=lambda: None).start()),
            ("block-wall-clock",
             lambda: time.time()),
            ("block-nanosecond-clock",
             lambda: time.time_ns()),
            ("block-performance-clock",
             lambda: time.perf_counter()),
            ("block-monotonic-clock",
             lambda: time.monotonic()),
            ("block-clock-sleep",
             lambda: time.sleep(0)),
        )
        for label, operation in probes:
            reject(label, operation)
        blocked = dict(sandbox.blocked)
    require(
        all(count > 0 for count in blocked.values()),
        "exercise and block every source-only external effect category",
    )
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "version": 6,
        "mode": "SYNTHETIC EFFECT-BLOCKED SELF-TEST",
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_effects_by_kind": blocked,
        "published_v25_evidence_owner_count": 139,
        "published_v25_authenticated_reference_count": 144,
        "actual_zig_build_process_count": 26,
        "actual_rust_build_process_count": 28,
        "native_role_count": 2,
        "source_freeze_original_targets_read": 0,
        "source_freeze_original_targets_statted": 0,
        "source_freeze_original_targets_modified": 0,
        "group_atomic": False,
        **phase_boundary(),
    }


def parse_arguments(
    arguments: list[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, allow_abbrev=False,
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--activate", action="store_true")
    modes.add_argument("--recover", action="store_true")
    modes.add_argument("--restore", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
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
    options = parser.parse_args(
        list(sys.argv[1:] if arguments is None else arguments),
    )
    checked_digest(options.source_sha256, "V6 source")
    checked_digest(options.protocol_sha256, "V6 protocol")
    if options.contract_sha256 is not None:
        checked_digest(options.contract_sha256, "V6 contract")
    actual_values = (
        options.family, options.build_label,
        options.build_archive_sha256, options.build_receipt_sha256,
        options.native_engine_sha256, options.native_bridge_sha256,
        options.native_engine_bytes, options.native_bridge_bytes,
        options.activation_root, options.recovery_journal_sha256,
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(value is None for value in actual_values),
                "contract rendering cannot activate, inspect, or recover a target")
    else:
        require(options.contract_sha256 is not None,
                "independently pin the complete canonical V6 machine contract")
    if options.self_test or options.verify_frozen_context:
        require(all(value is None for value in actual_values),
                "source-only modes accept no candidate, root, or native operation")
    elif options.activate:
        require(
            options.activation_root is None
            and options.recovery_journal_sha256 is None,
            "generate a fresh owner-only activation root only during activation",
        )
        validate_actual_activation_options(options)
    elif options.recover or options.restore:
        require(
            options.family == FAMILY
            and options.build_label is None
            and options.build_archive_sha256 is None
            and options.build_receipt_sha256 is None
            and options.native_engine_sha256 is None
            and options.native_bridge_sha256 is None
            and options.native_engine_bytes is None
            and options.native_bridge_bytes is None
            and options.activation_root is not None
            and options.recovery_journal_sha256 is not None,
            "pin only the exact durable Zig recovery root and journal",
        )
        checked_private_root(options.activation_root)
        checked_digest(
            options.recovery_journal_sha256, "actual recovery journal",
        )
    return options


def main(arguments: list[str] | None = None) -> int:
    try:
        selected = parse_arguments(arguments)
        if selected.self_test:
            result = self_test(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256,
            )
        elif selected.verify_frozen_context:
            result, _ = authenticate_context(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256,
            )
        elif selected.render_contract:
            authenticate_context(
                selected.source_sha256, selected.protocol_sha256,
            )
            result = contract_document(
                selected.source_sha256, selected.protocol_sha256,
            )
        elif selected.activate:
            result = activate(selected)
        else:
            result = recover(selected)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0
    except (ActivationError, SourceOnlyEffect, OSError, ValueError,
            TypeError, UnicodeError, OverflowError, RecursionError,
            subprocess.SubprocessError, zlib.error) as error:
        sys.stderr.write(
            "ZIG NATIVE ACTIVATION V6: FAIL: "
            + type(error).__name__ + ": " + str(error) + "\n"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
