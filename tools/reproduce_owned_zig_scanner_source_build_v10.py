#!/usr/bin/env python3
"""Freeze a future, two-phase, first-party Zig scanner source build.

``--self-test`` is wholly synthetic and effect-blocked.  ``--verify-context``
only reads independently pinned, already published files.  Neither mode creates
a private directory, applies the scanner repair, starts a compiler, imports a
candidate, opens the holdout, or samples a clock.  Only the separately and
explicitly requested ``--build`` mode may create two fresh private phase trees,
apply the independently frozen scanner overlay, and start the exact 26 frozen
compiler and inspection processes.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import ctypes
import errno
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


ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
SOURCE_RELATIVE = "tools/reproduce_owned_zig_scanner_source_build_v10.py"
PROTOCOL_RELATIVE = "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V10.md"
CONTRACT_RELATIVE = "oracle/phase2/zig-scanner-source-build-v10.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-zig-scanner-source-build-v10"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
OVERLAY_SCHEMA = "rebar-phase2-owned-zig-scanner-capture-source-repair-v1"
PRIVATE_ROOT_PREFIX = "rebar-phase2-zig-scanner-capture-source-build-v1-"
PHASE_NAMES = ("reference-a", "reference-b")
ENGINE_FILENAME = "_zig_probe.so"
BRIDGE_FILENAME = "_zig_bridge.cpython-314-x86_64-linux-gnu.so"
CANONICAL_SOURCE_PREFIX = "/rebar-phase2-v6-owned-source"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_COMPILER_BYTES = 256 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48
EXPECTED_PROCESS_COUNT = 26
EXPECTED_PHASE_PROCESS_COUNT = 13
FINAL_PLANNED_CASE_COUNT = 4_194_304
HISTORICAL_V21_EVIDENCE_OWNER_COUNT = 103
HISTORICAL_V21_REFERENCE_COUNT = 108
ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT = 2
CURRENT_EVIDENCE_OWNER_COUNT = 105
CURRENT_AUTHENTICATED_REFERENCE_COUNT = 110

PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
PINNED_ZIG = "/tmp/zig-x86_64-linux-0.16.0/zig"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"

OVERLAY_SOURCE = "tools/apply_owned_zig_scanner_capture_source_repair_v1.py"
OVERLAY_PROTOCOL = "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md"
OVERLAY_CONTRACT = "oracle/phase2/zig-scanner-capture-source-repair-v1.json"
OVERLAY_SOURCE_SHA256 = (
    "963f306373753b9fef84c9a9784668f42067cb905b84347a0bcc99e1e8692515"
)
OVERLAY_PROTOCOL_SHA256 = (
    "7a40b58bcc69744fc6b749368ec307be7d05d742de3d921410fd2753a4f5c8d0"
)
OVERLAY_CONTRACT_SHA256 = (
    "c48fcd9cb40cbe15442c2dd197627d7f4ccc341b3edfbbe0c645405015c8ea87"
)

ORIGINAL_ENGINE = "candidates/zig/mini_regex.zig"
ORIGINAL_BRIDGE = "candidates/zig/py_bridge.c"
ORIGINAL_ADAPTER = "candidates/zig_candidate.py"
ORIGINAL_ENGINE_SHA256 = (
    "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
)
ORIGINAL_BRIDGE_SHA256 = (
    "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
)
ORIGINAL_ADAPTER_SHA256 = (
    "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862"
)
DERIVED_BRIDGE_SHA256 = (
    "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
)
DERIVED_BRIDGE_BYTES = 173_082

RECOVERED_C_ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures.json.gz"
)
RECOVERED_C_ARCHIVE_SHA256 = (
    "a37a70f7ab9e4dcc72b176ca51fb1bfe8514d906431e8f02f269871a8b946810"
)
RECOVERED_C_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v2-c-"
    "phase2-v9-original-p0-failures-publication-receipt.json"
)
RECOVERED_C_RECEIPT_SHA256 = (
    "8a16520de9ac80aac1a6ea6d9a6cec3778379d35a611a52a2bca692685645c81"
)

SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)

SOURCE_OWNERS: dict[str, tuple[str, int]] = {
    ORIGINAL_ADAPTER: (ORIGINAL_ADAPTER_SHA256, 68_422),
    ORIGINAL_ENGINE: (ORIGINAL_ENGINE_SHA256, 186_915),
    ORIGINAL_BRIDGE: (ORIGINAL_BRIDGE_SHA256, 173_026),
}

SUPPORT_OWNERS: dict[str, tuple[str, int]] = {
    "GOAL.md": (
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3_756,
    ),
    "oracle/phase1/p0-completeness-v1.json": (
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        45_632,
    ),
    "docs/evidence/candidate-current-overview-v21.inputs.json": (
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
        14_631,
    ),
    "docs/evidence/candidate-current-overview-v21.json": (
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
        96_376,
    ),
    "docs/evidence/candidate-current-overview-v21.svg": (
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
        8_074,
    ),
    "tools/render_candidate_current_overview_v21.py": (
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
        75_566,
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
    OVERLAY_SOURCE: (OVERLAY_SOURCE_SHA256, 65_531),
    OVERLAY_PROTOCOL: (OVERLAY_PROTOCOL_SHA256, 5_198),
    OVERLAY_CONTRACT: (OVERLAY_CONTRACT_SHA256, 9_236),
    "tools/reproduce_owned_native_source_build_v7.py": (
        "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
        300_624,
    ),
    "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md": (
        "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
        8_063,
    ),
    "oracle/phase2/native-source-build-v7.json": (
        "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
        28_924,
    ),
    "toolchains/zig-0.16.0.lock.json": (
        "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
        628,
    ),
    RECOVERED_C_ARCHIVE: (RECOVERED_C_ARCHIVE_SHA256, 2_496),
    RECOVERED_C_RECEIPT: (RECOVERED_C_RECEIPT_SHA256, 934),
}

TOOLCHAIN_OWNERS: dict[str, tuple[str, str, int, bool]] = {
    "python": (
        PINNED_PYTHON,
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        32_387_816,
        True,
    ),
    "python_header": (
        PYTHON_INCLUDE + "/Python.h",
        "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
        4_399,
        False,
    ),
    "python_patchlevel": (
        PYTHON_INCLUDE + "/patchlevel.h",
        "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
        1_773,
        False,
    ),
    "gcc": (
        PINNED_GCC,
        "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        1_023_032,
        True,
    ),
    "readelf": (
        PINNED_READELF,
        "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        789_280,
        True,
    ),
    "zig": (
        PINNED_ZIG,
        "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
        172_641_672,
        True,
    ),
}

PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version",
    "build_zig_engine", "build_zig_bridge",
    "engine_dynamic", "engine_symbols", "engine_sections", "engine_notes",
    "bridge_dynamic", "bridge_symbols", "bridge_sections", "bridge_notes",
)

REQUIRED_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
})

REQUIRED_BRIDGE_ENGINE_IMPORTS = frozenset({
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
})

ALLOWED_ENGINE_UNICODE_HELPERS = frozenset({
    "_PyUnicode_IsWhitespace", "_PyUnicode_IsDecimalDigit",
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDigit", "_PyUnicode_IsNumeric",
    "_PyUnicode_ToLowercase", "_PyUnicode_ToUppercase",
})

FORBIDDEN_SYMBOL_PREFIXES = (
    "_sre", "sre_", "pcre", "onig", "re2_", "hs_", "hyperscan",
    "rebar_rust_", "rebar_c_", "rebar_vm_", "rebar_cpp_",
    "rebar_go_", "rebar_fortran_",
)
FORBIDDEN_SYMBOLS = frozenset({
    "regcomp", "regexec", "regerror", "regfree", "dlopen", "dlmopen",
    "dlsym", "system", "execve", "posix_spawn", "socket", "connect",
    "getaddrinfo", "PyImport_Import", "PyImport_ImportModule",
    "PyImport_ExecCodeModule",
})


class FreezeError(Exception):
    """A source-freeze, authenticated owner, or actual future build failed."""


class SourceOnlyError(FreezeError):
    """A synthetic control attempted a real external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only genuine, complete byte strings")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, RecursionError, UnicodeError) as error:
        raise FreezeError("require one finite, canonical JSON object") from error


def valid_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(part in "0123456789abcdef" for part in value),
        "require one exact lowercase SHA-256 for " + label,
    )
    return value


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicated or non-string JSON object fields")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str, *, canonical_required: bool = True) -> dict:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "bound the complete authenticated JSON: " + label)

    def reject_nonfinite(value: str) -> Any:
        raise FreezeError("reject a non-finite JSON number: " + value)

    try:
        result = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=unique_json_pairs,
            parse_constant=reject_nonfinite,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise FreezeError("reject malformed JSON: " + label) from error
    require(type(result) is dict, "require a complete JSON object: " + label)
    if canonical_required:
        require(canonical(result) == raw,
                "reject substituted or noncanonical JSON: " + label)
    return result


def checked_relative(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require a bounded repository-relative owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value
            and 0 < len(parsed.parts) <= 12
            and all(part not in ("", ".", "..")
                    and "\\" not in part and "\x00" not in part
                    for part in parsed.parts),
            "reject an absolute, traversing, redirected, or malformed owner")
    return parsed.parts


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for char in value)
            and "--" not in value and not value.endswith("-"),
            "require one bounded, fresh, lowercase evidence label")
    return value


def checked_workdir(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded fresh Zig build root")
    parsed = PurePosixPath(value)
    require(parsed.is_absolute() and str(parsed) == value,
            "require one exact absolute private Zig build root")
    parts = parsed.parts
    require(len(parts) == 3 and parts[1] == "tmp"
            and parts[2].startswith(PRIVATE_ROOT_PREFIX),
            "use only the independently frozen Zig overlay root prefix")
    suffix = parts[2][len(PRIVATE_ROOT_PREFIX):]
    require(len(suffix) >= 8
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in suffix),
            "reject an unsafe, reused, unresolved, or predictable phase root")
    return value


def phase_paths(workdir: str, phase: str) -> dict[str, Path]:
    root = Path(checked_workdir(workdir))
    require(type(phase) is str and phase in PHASE_NAMES,
            "require exactly reference-a or reference-b")
    base = root / phase
    source = base / "source"
    native = base / "native"
    return {
        "base": base,
        "source": source,
        "native": native,
        "temporary": base / "temporary",
        "zig_local_cache": base / "zig-local-cache",
        "zig_global_cache": base / "zig-global-cache",
        "source_candidates": source / "candidates",
        "source_zig": source / "candidates" / "zig",
        "source_adapter": source / "candidates" / "zig_candidate.py",
        "source_engine": source / "candidates" / "zig" / "mini_regex.zig",
        "source_bridge": source / "candidates" / "zig" / "py_bridge.c",
        "artifact_engine": native / ENGINE_FILENAME,
        "artifact_bridge": native / BRIDGE_FILENAME,
    }


def prefix_flags(workdir: str) -> list[str]:
    checked_workdir(workdir)
    return [
        "-ffile-prefix-map=" + str(phase_paths(workdir, phase)["source"])
        + "=" + CANONICAL_SOURCE_PREFIX
        for phase in PHASE_NAMES
    ]


def build_environment(workdir: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, phase)
    return {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
        "ZIG_LOCAL_CACHE_DIR": str(paths["zig_local_cache"]),
        "ZIG_GLOBAL_CACHE_DIR": str(paths["zig_global_cache"]),
    }


def planned_commands(workdir: str, phase: str) -> dict[str, list[str]]:
    paths = phase_paths(workdir, phase)
    commands: dict[str, list[str]] = {
        "readelf_version": [PINNED_READELF, "--version"],
        "gcc_version": [PINNED_GCC, "--version"],
        "zig_version": [PINNED_ZIG, "version"],
        "build_zig_engine": [
            PINNED_ZIG,
            "build-lib",
            str(paths["source_engine"]),
            "-dynamic",
            "-lc",
            "-O",
            "ReleaseFast",
            "-fstrip",
            "-fallow-shlib-undefined",
            "-fsoname=" + ENGINE_FILENAME,
            "--cache-dir",
            str(paths["zig_local_cache"]),
            "--global-cache-dir",
            str(paths["zig_global_cache"]),
            "-femit-bin=" + str(paths["artifact_engine"]),
        ],
        "build_zig_bridge": [
            PINNED_GCC,
            "-std=c11",
            "-shared",
            "-fPIC",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wl,--build-id=sha1",
            *prefix_flags(workdir),
            "-I" + PYTHON_INCLUDE,
            str(paths["source_bridge"]),
            "-L" + str(paths["native"]),
            "-l:" + ENGINE_FILENAME,
            "-Wl,-rpath,$ORIGIN",
            "-o",
            str(paths["artifact_bridge"]),
        ],
    }
    for role in ("engine", "bridge"):
        target = str(paths["artifact_" + role])
        commands[role + "_dynamic"] = [
            PINNED_READELF, "--dynamic", "--wide", target,
        ]
        commands[role + "_symbols"] = [
            PINNED_READELF, "--dyn-syms", "--wide", target,
        ]
        commands[role + "_sections"] = [
            PINNED_READELF, "--sections", "--wide", target,
        ]
        commands[role + "_notes"] = [
            PINNED_READELF, "--notes", "--wide", target,
        ]
    require(tuple(commands) == PROCESS_ROLES
            and len(commands) == EXPECTED_PHASE_PROCESS_COUNT,
            "freeze exactly the thirteen direct V7-derived Zig phase processes")
    return commands


def checked_command(name: Any, argv: Any, workdir: str, phase: str) -> list[str]:
    commands = planned_commands(workdir, phase)
    require(type(name) is str and name in commands and type(argv) is list
            and all(type(item) is str and "\x00" not in item for item in argv)
            and argv == commands[name]
            and argv[0] in (PINNED_READELF, PINNED_GCC, PINNED_ZIG),
            "reject an unpinned, modified, networked, delegated, or shell command")
    return list(argv)


def sanitized(value: Any, workdir: str) -> Any:
    root = checked_workdir(workdir)
    if type(value) is str:
        return value.replace(root, "<FRESH_PRIVATE_ROOT>")
    if type(value) is list:
        return [sanitized(item, root) for item in value]
    if type(value) is dict:
        return {key: sanitized(item, root) for key, item in value.items()}
    return value


def expected_phase_boundary() -> dict[str, Any]:
    return {
        "source_apply_count": 0,
        "native_builds_started": 0,
        "compiler_processes_started": 0,
        "actual_build_process_count": 0,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "reference_processes_started": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "final_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "qualified_candidate_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "final_comparison_planned_case_count": FINAL_PLANNED_CASE_COUNT,
        "final_comparison_cases_generated": False,
        "holdout": "NOT OPENED",
        "holdout_opened": False,
        "winner_selected": False,
    }


def owner_document(path: str, owner: tuple[str, int]) -> dict[str, Any]:
    checked_relative(path)
    valid_digest(owner[0], path)
    require(type(owner[1]) is int and 0 < owner[1] <= MAX_SOURCE_BYTES,
            "bound an exact frozen first-party source owner")
    return {"path": path, "sha256": owner[0], "bytes": owner[1]}


def command_templates() -> list[dict[str, Any]]:
    root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v10"
    return [
        {
            "phase": phase,
            "working_directory": sanitized(str(phase_paths(root, phase)["base"]), root),
            "environment": sanitized(build_environment(root, phase), root),
            "commands": [
                {"name": name, "argv": sanitized(argv, root)}
                for name, argv in planned_commands(root, phase).items()
            ],
        }
        for phase in PHASE_NAMES
    ]


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    valid_digest(source_pin, "V10 source")
    valid_digest(protocol_pin, "V10 protocol")
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 10,
        "phase": "ZIG SCANNER NATIVE BUILD SOURCE FREEZE; NO BUILD EXECUTED",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "oracle": {
            "implementation": "CPython",
            "version": "3.14.6",
            "manifest_path": "oracle/phase1/p0-completeness-v1.json",
            "manifest_sha256": SUPPORT_OWNERS[
                "oracle/phase1/p0-completeness-v1.json"
            ][0],
            "suite_count": 13,
            "suite_ids": list(SUITE_IDS),
            "case_execution_count": 31_237,
            "private_waiver_count": 13,
        },
        "frozen_overlay": {
            "schema": OVERLAY_SCHEMA,
            "source": owner_document(OVERLAY_SOURCE, SUPPORT_OWNERS[OVERLAY_SOURCE]),
            "protocol": owner_document(
                OVERLAY_PROTOCOL, SUPPORT_OWNERS[OVERLAY_PROTOCOL],
            ),
            "contract": owner_document(
                OVERLAY_CONTRACT, SUPPORT_OWNERS[OVERLAY_CONTRACT],
            ),
            "application": "AUTHENTICATED IN-PROCESS; EXPLICIT BUILD ONLY",
            "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
            "phase_names": list(PHASE_NAMES),
            "both_phase_trees_created_before_first_apply": True,
            "existing_destination": "FORBIDDEN",
            "destination": "source/candidates/zig/py_bridge.c",
            "private_directory_mode": "0700",
            "private_source_mode": "0600",
            "source_write_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "expected_actual_apply_count_only_after_build": 2,
            "actual_source_apply_count": 0,
            "derived_bridge_sha256": DERIVED_BRIDGE_SHA256,
            "derived_bridge_bytes": DERIVED_BRIDGE_BYTES,
            "derived_bridge_materialized": False,
        },
        "first_party_zig_owners": [
            owner_document(path, owner)
            for path, owner in sorted(SOURCE_OWNERS.items())
        ],
        "original_zig_source_owner_count": 3,
        "total_first_party_source_owner_count": 25,
        "independent_engine_family_count": 6,
        "external_regex_engine": "FORBIDDEN",
        "stdlib_regex_delegation": "FORBIDDEN",
        "cross_family_matching_engine": "FORBIDDEN",
        "source_fallback": "FORBIDDEN",
        "frozen_v7_source_build": {
            "source": owner_document(
                "tools/reproduce_owned_native_source_build_v7.py",
                SUPPORT_OWNERS["tools/reproduce_owned_native_source_build_v7.py"],
            ),
            "protocol": owner_document(
                "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md",
                SUPPORT_OWNERS["oracle/phase2/NATIVE-SOURCE-BUILD-V7.md"],
            ),
            "contract": owner_document(
                "oracle/phase2/native-source-build-v7.json",
                SUPPORT_OWNERS["oracle/phase2/native-source-build-v7.json"],
            ),
            "compiler_command_policy": "EXACT V7 ZIG ARGV; SEALED OVERLAY ROOT",
            "canonical_source_prefix": CANONICAL_SOURCE_PREFIX,
            "raw_elf_parser": "AUTHENTICATED FIRST-PARTY V7 parse_owned_elf64",
            "raw_elf_comparator": "AUTHENTICATED FIRST-PARTY V7 compare_owned_elf64",
            "modified": False,
        },
        "frozen_corrected_v3": {
            "source": owner_document(
                "tools/run_owned_six_family_original_p0_producer_v3.py",
                SUPPORT_OWNERS[
                    "tools/run_owned_six_family_original_p0_producer_v3.py"
                ],
            ),
            "protocol": owner_document(
                "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
                SUPPORT_OWNERS["oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md"],
            ),
            "contract": owner_document(
                "oracle/phase2/six-family-p0-producer-v3.json",
                SUPPORT_OWNERS["oracle/phase2/six-family-p0-producer-v3.json"],
            ),
            "modified": False,
        },
        "toolchains": [
            {
                "id": name,
                "path": value[0],
                "sha256": value[1],
                "bytes": value[2],
                "executable": value[3],
            }
            for name, value in sorted(TOOLCHAIN_OWNERS.items())
        ],
        "official_zig_lock": owner_document(
            "toolchains/zig-0.16.0.lock.json",
            SUPPORT_OWNERS["toolchains/zig-0.16.0.lock.json"],
        ),
        "published_v21_history": {
            "version": 21,
            "authoritative_counted_evidence_owner_count":
                HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths":
                HISTORICAL_V21_REFERENCE_COUNT,
            "current_qualified_candidate_count": 0,
            "historical_zig_semantic_mismatch_count": 1_764,
            "historical_zig_verified_passing_case_executions": 3_583,
            "historical_zig_gate_status": "FAIL",
            "scanner_verbose_mismatch_count": 620,
            "overview_inputs": owner_document(
                "docs/evidence/candidate-current-overview-v21.inputs.json",
                SUPPORT_OWNERS[
                    "docs/evidence/candidate-current-overview-v21.inputs.json"
                ],
            ),
            "overview": owner_document(
                "docs/evidence/candidate-current-overview-v21.json",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v21.json"],
            ),
            "new_v10_evidence_owners": 0,
            "planned_new_evidence_owners_only_after_publication": 2,
            "file_owners_are_not_compiler_processes": True,
        },
        "current_published_history": {
            "historical_v21_evidence_owner_count":
                HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
            "historical_v21_authenticated_reference_count":
                HISTORICAL_V21_REFERENCE_COUNT,
            "additional_recovered_c_failure_evidence_owner_count":
                ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT,
            "authoritative_counted_evidence_owner_count":
                CURRENT_EVIDENCE_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths":
                CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "recovered_c_failure": {
                "archive": owner_document(
                    RECOVERED_C_ARCHIVE, SUPPORT_OWNERS[RECOVERED_C_ARCHIVE],
                ),
                "receipt": owner_document(
                    RECOVERED_C_RECEIPT, SUPPORT_OWNERS[RECOVERED_C_RECEIPT],
                ),
                "archive_status": "FAIL",
                "receipt_status": "PASS",
                "actual_aggregate_process_count": 1,
                "actual_candidate_worker_count": 0,
                "infrastructure_failure_count": 1,
                "semantic_mismatch_count": "NOT MEASURED",
                "verified_passing_case_count": "NOT MEASURED",
                "original_native_restored": True,
                "candidate_qualified": False,
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
            },
            "new_v10_evidence_owners": 0,
            "qualified_candidate_count": 0,
        },
        "future_build_policy": {
            "authorization": "EXPLICIT --build AFTER INDEPENDENT SOURCE FREEZE",
            "actual_status": "NOT RUN",
            "phase_names": list(PHASE_NAMES),
            "phase_count_started": 0,
            "expected_phase_count_only_after_success": 2,
            "expected_process_count_per_completed_phase":
                EXPECTED_PHASE_PROCESS_COUNT,
            "expected_total_process_count_only_after_success":
                EXPECTED_PROCESS_COUNT,
            "actual_process_count": 0,
            "command_role_order": list(PROCESS_ROLES),
            "frozen_command_templates": command_templates(),
            "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
            "private_directory_mode": "0700",
            "private_source_mode": "0600",
            "distinct_phase_sources": True,
            "distinct_phase_caches": True,
            "distinct_phase_output_inodes": True,
            "network_requests": 0,
            "shell": "FORBIDDEN",
            "prebuilt_native_artifact": "FORBIDDEN",
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_delegation": "FORBIDDEN",
            "cross_family_matching_dependency": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "engine_soname": ENGINE_FILENAME,
            "bridge_needed_engine": ENGINE_FILENAME,
            "bridge_runpath": "$ORIGIN",
            "legacy_rpath": "FORBIDDEN",
            "allowed_engine_unicode_helpers": sorted(
                ALLOWED_ENGINE_UNICODE_HELPERS,
            ),
            "required_engine_exports": sorted(REQUIRED_ENGINE_EXPORTS),
            "required_bridge_engine_imports": sorted(
                REQUIRED_BRIDGE_ENGINE_IMPORTS,
            ),
            "native_outputs": {
                "engine": {"filename": ENGINE_FILENAME,
                           "sha256": "NOT MEASURED", "bytes": "NOT MEASURED"},
                "bridge": {"filename": BRIDGE_FILENAME,
                           "sha256": "NOT MEASURED", "bytes": "NOT MEASURED"},
            },
            "reproducibility": "NOT MEASURED",
            "raw_elf_audit": "NOT MEASURED",
        },
        "future_publication_policy": {
            "success_archive_template":
                "oracle/phase2/evidence/native-source-build-v10-zig-"
                "<FRESH_LABEL>.json.gz",
            "success_receipt_template":
                "oracle/phase2/evidence/native-source-build-v10-zig-"
                "<FRESH_LABEL>-publication-receipt.json",
            "failure_archive_template":
                "oracle/phase2/evidence/native-source-build-v10-zig-"
                "<FRESH_LABEL>-failures.json.gz",
            "failure_receipt_template":
                "oracle/phase2/evidence/native-source-build-v10-zig-"
                "<FRESH_LABEL>-failures-publication-receipt.json",
            "receipt_schema": RECEIPT_SCHEMA,
            "archive_compression": "SINGLE-MEMBER GZIP; LEVEL 9; MTIME 0",
            "write_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "owner_mode": "0600",
            "full_same_inode_readback": True,
            "file_fsync": True,
            "parent_directory_fsync": True,
            "preserve_failure": True,
            "archives_published": 0,
            "receipts_published": 0,
        },
        "pinned_support": [
            owner_document(path, owner)
            for path, owner in sorted(SUPPORT_OWNERS.items())
        ],
        "phase_boundary": expected_phase_boundary(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict,
            "require the complete independently frozen V10 machine contract")
    expected = contract_document(source_pin, protocol_pin)
    require(value == expected,
            "reject a missing, altered, invented, or silently weakened V10 contract")
    require(len(value["future_build_policy"]["frozen_command_templates"]) == 2
            and value["phase_boundary"] == expected_phase_boundary(),
            "never count a future Zig source build as an actual experiment")
    return value


def source_owner_metadata(path: str, owner: os.stat_result,
                          observed_digest: str) -> dict[str, Any]:
    return {
        "path": path,
        "sha256": observed_digest,
        "bytes": owner.st_size,
        "device": owner.st_dev,
        "inode": owner.st_ino,
        "link_count": owner.st_nlink,
        "mode": format(stat.S_IMODE(owner.st_mode), "04o"),
    }


def read_descriptor(descriptor: int, expected: str, expected_size: int,
                    limit: int, label: str, *, executable: bool = False,
                    private: bool = False) -> tuple[dict[str, Any], bytes]:
    valid_digest(expected, label)
    require(type(expected_size) is int and 0 < expected_size <= limit,
            "bound the exact authenticated owner: " + label)
    before = os.fstat(descriptor)
    require(stat.S_ISREG(before.st_mode)
            and before.st_size == expected_size
            and before.st_nlink == 1,
            "reject an aliased, nonregular, or incorrectly sized owner: " + label)
    if executable:
        require(before.st_mode & 0o111,
                "require the pinned genuine compiler executable: " + label)
    if private:
        require(before.st_uid == os.geteuid()
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require a fresh owner-only mode-0600 private snapshot: " + label)
    total = 0
    chunks: list[bytes] = []
    while True:
        part = os.read(descriptor, min(1024 * 1024, limit + 1 - total))
        if not part:
            break
        total += len(part)
        require(total <= limit, "reject an oversized owner: " + label)
        chunks.append(part)
    after = os.fstat(descriptor)
    require(
        (before.st_dev, before.st_ino, before.st_size, before.st_nlink,
         before.st_mtime_ns, before.st_ctime_ns)
        == (after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns),
        "the authenticated owner changed during its complete read: " + label,
    )
    raw = b"".join(chunks)
    require(total == expected_size and len(raw) == expected_size
            and digest(raw) == expected,
            "the independently frozen owner digest changed: " + label)
    return source_owner_metadata(label, after, expected), raw


def read_repository_owner(relative: str, expected: str, expected_size: int,
                          *, limit: int = MAX_SOURCE_BYTES) -> tuple[dict, bytes]:
    parts = checked_relative(relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            return read_descriptor(descriptor, expected, expected_size,
                                   limit, relative)
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def read_absolute_owner(path: str, expected: str, expected_size: int,
                        executable: bool) -> tuple[dict, bytes]:
    require(type(path) is str and path.startswith("/")
            and "\x00" not in path and "\\" not in path,
            "require one exact authenticated absolute compiler owner")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        return read_descriptor(descriptor, expected, expected_size,
                               MAX_COMPILER_BYTES, path,
                               executable=executable)
    finally:
        os.close(descriptor)


def load_authenticated_module(name: str, relative: str,
                              raw: bytes) -> types.ModuleType:
    require(type(name) is str and name.startswith("_rebar_owned_v10_"),
            "load only an independently authenticated first-party source tool")
    checked_relative(relative)
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "load only the exact already authenticated source bytes")
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    return module


def validate_zig_lock(value: dict[str, Any]) -> None:
    require(value.get("schema") == "rebar-official-language-toolchain-v1"
            and value.get("language") == "Zig"
            and value.get("version") == "0.16.0"
            and value.get("release_channel") == "stable"
            and value.get("platform") == "x86_64-linux"
            and value.get("archive_root") == "zig-x86_64-linux-0.16.0"
            and value.get("compiler_relative_path")
            == "zig-x86_64-linux-0.16.0/zig"
            and value.get("compiler_sha256")
            == TOOLCHAIN_OWNERS["zig"][1]
            and value.get("archive_sha256")
            == "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00"
            and value.get("archive_bytes") == 55_478_392,
            "reject an unofficial, substituted, or network-fetched Zig toolchain")


def validate_phase_one(value: dict[str, Any]) -> None:
    denominator = value.get("denominator")
    gate = value.get("phase_gate")
    runtime = value.get("runtime")
    boundaries = value.get("audit_boundaries")
    require(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and value.get("version") == 1
            and type(denominator) is dict
            and denominator.get("available_frozen_vector_case_executions") == 31_237
            and denominator.get("final_required_case_execution_denominator") == 31_237
            and tuple(denominator.get("counted_suite_ids", ())) == SUITE_IDS
            and denominator.get("private_upstream_methods_outside_public_denominator")
            == 13
            and type(gate) is dict and gate.get("status") == "PASS"
            and gate.get("all_obligations_mapped") is True
            and gate.get("final_holdout_authorized") is False
            and type(runtime) is dict
            and runtime.get("python_implementation") == "CPython"
            and runtime.get("python_version") == "3.14.6"
            and type(boundaries) is dict
            and boundaries.get("hidden_cases_read") == 0
            and boundaries.get("final_cases_read") == 0,
            "preserve all 13 original suites, 31,237 cases, and 13 private waivers")


def validate_corrected_v3(value: dict[str, Any]) -> None:
    history = value.get("frozen_v21_history")
    effects = value.get("verification_effects")
    families = value.get("families")
    phase = value.get("phase_one")
    require(value.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and value.get("version") == 3
            and value.get("family_count") == 6
            and value.get("source_owner_count") == 25
            and value.get("suite_count") == 13
            and value.get("case_execution_denominator") == 31_237
            and value.get("pairwise_shared_semantic_source_count") == 0
            and type(phase) is dict
            and phase.get("named_private_waiver_count") == 13,
            "preserve the exact independent, corrected six-family V3 producer")
    require(type(history) is dict
            and history.get("actual_evidence_owner_count") == 103
            and history.get("authenticated_reference_path_count") == 108
            and history.get("new_actual_campaign_owner_count") == 30,
            "preserve 103 actual V21 evidence owners and 108 history references")
    require(type(effects) is dict
            and effects.get("actual_candidate_imports") == 0
            and effects.get("actual_candidate_workers") == 0
            and effects.get("actual_source_builds") == 0
            and effects.get("actual_native_activations") == 0
            and effects.get("actual_native_libraries_loaded") == 0
            and effects.get("actual_network_requests") == 0
            and effects.get("actual_subprocesses_started") == 0
            and effects.get("clock_samples") == 0
            and effects.get("hidden_cases_read") == 0
            and effects.get("candidate_qualified_count") == 0
            and effects.get("holdout") == "NOT OPENED"
            and effects.get("performance") == "NOT MEASURED",
            "do not turn corrected V3 source verification into an experiment")
    require(type(families) is list,
            "require every independently frozen candidate family")
    zig = [item for item in families
           if type(item) is dict and item.get("family") == "zig"]
    require(len(zig) == 1 and zig[0].get("owned_source_count") == 3
            and zig[0].get("adapter_relative") == ORIGINAL_ADAPTER,
            "retain exactly the original independent three-owner Zig family")
    actual = zig[0].get("sources")
    expected = [
        {"relative": path, "sha256": owner[0], "size_bytes": owner[1]}
        for path, owner in sorted(SOURCE_OWNERS.items())
    ]
    require(type(actual) is list and sorted(
        actual, key=lambda item: item.get("relative", ""),
    ) == expected,
        "reject cross-family, missing, repeated, or altered Zig semantic owners")


def validate_v21(inputs: dict[str, Any], summary: dict[str, Any]) -> None:
    require(inputs.get("schema") == "rebar-candidate-current-overview-v21-inputs"
            and inputs.get("version") == 21
            and inputs.get("repository_evidence_owner_count") == 103
            and inputs.get("all_digest_addressed_history_path_count") == 108
            and inputs.get("current_source_owner_count") == 25
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("suite_count") == 13
            and inputs.get("full_case_denominator") == 31_237
            and inputs.get("private_waiver_count") == 13
            and inputs.get("python") == "3.14.6",
            "retain the exact counted current V21 evidence graph")
    require(summary.get("schema") == "rebar-candidate-current-overview-v21-summary"
            and summary.get("status") == "PASS"
            and summary.get("repository_evidence_owner_count") == 103
            and summary.get("authenticated_digest_addressed_history_paths") == 108
            and summary.get("qualified_candidate_count") == 0
            and summary.get("suite_count") == 13
            and summary.get("full_case_denominator") == 31_237
            and summary.get("private_waiver_count") == 13,
            "do not change either V21 evidence denominator")
    snapshot = summary.get("snapshot")
    require(type(snapshot) is dict
            and snapshot.get("frozen_independent_engine_family_count") == 6
            and snapshot.get("current_source_owner_count") == 25
            and snapshot.get("zig_actual_semantic_mismatch_count") == 1_764
            and snapshot.get("zig_verified_passing_case_executions") == 3_583
            and snapshot.get("qualified_candidate_count") == 0
            and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS,
            "never erase the actual 1,764 original Zig matching failures")
    zig_gate = snapshot.get("zig_full_gate")
    require(type(zig_gate) is dict
            and zig_gate.get("gate_status") == "FAIL"
            and zig_gate.get("actual_semantic_mismatch_count") == 1_764
            and zig_gate.get("qualified_candidate_case_executions") == 0,
            "an unbuilt scanner repair cannot qualify the failed Zig candidate")
    for label, value in (("V21 inputs", inputs),
                         ("V21 summary", summary),
                         ("V21 snapshot", snapshot)):
        require(value.get("final_holdout_opened") is False
                and value.get("final_comparison_cases_generated") is False
                and value.get("final_comparison_planned_case_count")
                == FINAL_PLANNED_CASE_COUNT
                and value.get("performance") == "NOT MEASURED"
                and value.get("memory") == "NOT MEASURED",
                "preserve unopened and unmeasured " + label)
    require(summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False,
            "a Zig build source freeze cannot time or select a candidate")


def validate_v7(value: dict[str, Any]) -> None:
    require(value.get("schema")
            == "rebar-phase2-owned-native-source-build-v7-source-freeze"
            and value.get("version") == 7
            and value.get("family_count") == 6
            and value.get("source_owner_count") == 25
            and value.get("qualified_candidate_count") == 0,
            "preserve the exact independent first-party V7 builder")
    policy = value.get("build_policy")
    require(type(policy) is dict
            and policy.get("phase_names") == list(PHASE_NAMES)
            and policy.get("private_root_prefix")
            == "/tmp/rebar-phase2-native-build-v7-"
            and policy.get("bridge_runpath") == "$ORIGIN"
            and policy.get("rpath") == "FORBIDDEN"
            and policy.get("zig_engine_strip_flag") == "-fstrip"
            and policy.get("network_requests") == 0
            and policy.get("external_regular_expression_packages") == 0
            and policy.get("cross_family_matching_dependencies") == 0
            and policy.get("stdlib_matching_delegation") == 0
            and policy.get("fallback") == "FORBIDDEN"
            and policy.get("prebuilt_artifact") == "FORBIDDEN"
            and type(policy.get("v7_future_process_count_by_family")) is dict
            and policy["v7_future_process_count_by_family"].get("zig")
            == EXPECTED_PROCESS_COUNT,
            "preserve all original V7 first-party Zig process and engine rules")
    oracle = value.get("oracle")
    require(type(oracle) is dict
            and oracle.get("implementation") == "CPython"
            and oracle.get("version") == "3.14.6"
            and oracle.get("suite_count") == 13
            and oracle.get("case_execution_count") == 31_237,
            "preserve the unchanged V7 original correctness denominator")
    families = value.get("families")
    require(type(families) is list, "require the complete V7 owner inventory")
    found = [item for item in families
             if type(item) is dict and item.get("id") == "zig"]
    expected = [owner_document(path, owner)
                for path, owner in sorted(SOURCE_OWNERS.items())]
    require(len(found) == 1
            and found[0].get("language") == "Zig"
            and found[0].get("artifacts")
            == {"bridge": BRIDGE_FILENAME, "engine": ENGINE_FILENAME}
            and type(found[0].get("owners")) is list
            and sorted(found[0]["owners"], key=lambda item: item.get("path", ""))
            == expected,
            "never replace the authenticated V7 first-party Zig semantic family")
    raw = value.get("raw_elf_forensics")
    require(type(raw) is dict
            and raw.get("format") == "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN"
            and raw.get("full_binary_maximum_bytes") == MAX_BINARY_BYTES
            and raw.get("record_before_reproducibility_classification") is True
            and raw.get("additional_process_count") == 0
            and raw.get("actual_v7_builds") == "NOT RUN",
            "retain authenticated complete-byte V7 ELF source forensics")
    boundary = value.get("phase_boundary")
    require(type(boundary) is dict
            and boundary.get("compiler_processes_started") == 0
            and boundary.get("candidate_imports") == 0
            and boundary.get("clock_samples") == 0
            and boundary.get("holdout") == "NOT OPENED",
            "do not count an inherited V7 build plan as executed")


def validate_overlay(value: dict[str, Any], derived: bytes) -> None:
    require(value.get("schema") == OVERLAY_SCHEMA
            and value.get("version") == 1,
            "authenticate the exact separately published Zig scanner overlay")
    policy = value.get("apply_policy")
    repair = value.get("repair")
    history = value.get("published_history")
    boundary = value.get("phase_boundary")
    require(type(policy) is dict
            and policy.get("private_root_parent") == "/tmp"
            and policy.get("private_root_prefix") == PRIVATE_ROOT_PREFIX
            and policy.get("phase_names") == list(PHASE_NAMES)
            and policy.get("relative_destination")
            == "candidates/zig/py_bridge.c"
            and policy.get("existing_destination") == "FORBIDDEN"
            and policy.get("workspace_destination") == "FORBIDDEN"
            and policy.get("candidate_source_mutation") == "FORBIDDEN"
            and policy.get("private_directory_mode") == "0700"
            and policy.get("private_file_mode") == "0600"
            and policy.get("explicit_apply_required") is True,
            "retain the sealed sibling-phase overlay prefix and exclusive destination")
    require(type(repair) is dict
            and type(repair.get("derived_source")) is dict
            and repair["derived_source"].get("sha256") == DERIVED_BRIDGE_SHA256
            and repair["derived_source"].get("bytes") == DERIVED_BRIDGE_BYTES
            and repair["derived_source"].get("materialized") is False
            and repair.get("proposed_repair_tested") is False
            and type(derived) is bytes
            and len(derived) == DERIVED_BRIDGE_BYTES
            and digest(derived) == DERIVED_BRIDGE_SHA256,
            "derive only the exact committed one-block private Zig bridge")
    require(type(history) is dict
            and history.get("authoritative_counted_evidence_owner_count") == 103
            and history.get("authenticated_digest_addressed_history_paths") == 108
            and history.get("qualified_candidate_count") == 0,
            "preserve every previously authenticated genuine evidence owner")
    require(type(boundary) is dict
            and boundary.get("source_apply_count") == 0
            and boundary.get("compiler_processes_started") == 0
            and boundary.get("candidate_imports") == 0
            and boundary.get("clock_samples") == 0
            and boundary.get("holdout") == "NOT OPENED",
            "do not execute the separately frozen scanner repair in source mode")


def validate_recovered_c_failure(
    protected: dict[str, bytes],
    protected_owners: dict[str, dict[str, Any]],
    overlay: types.ModuleType,
) -> dict[str, Any]:
    archive_raw = protected[RECOVERED_C_ARCHIVE]
    receipt = strict_json(protected[RECOVERED_C_RECEIPT],
                          "actual recovered C failure receipt")
    try:
        plain = gzip.decompress(archive_raw)
    except (OSError, EOFError, ValueError) as error:
        raise FreezeError("reject altered recovered C failure archive") from error
    require(len(plain) == 5_941
            and digest(plain)
            == "5aa8b513eec30c7ab13bc4b638a5b5026a6f03821f8cd411f6ea3201b0813cfd",
            "authenticate every preserved byte of the genuine C failure")
    report = strict_json(plain, "actual recovered C failure report")
    failure = report.get("failure")
    aggregate = failure.get("actual_aggregate_process") \
        if type(failure) is dict else None
    require(report.get("schema")
            == "rebar-owned-repaired-c-original-campaign-v2-actual-recovered-campaign"
            and report.get("status") == "FAIL"
            and report.get("family") == "c"
            and report.get("label") == "phase2-v9-original-p0"
            and report.get("case_execution_denominator") == 31_237
            and report.get("suite_count") == 13
            and report.get("named_private_waiver_count") == 13
            and report.get("historical_evidence_owner_count")
            == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
            and report.get("historical_authenticated_reference_count")
            == HISTORICAL_V21_REFERENCE_COUNT
            and report.get("infrastructure_failure_count") == 1
            and report.get("candidate_qualified") is False
            and report.get("all_original_suite_evidence_preserved") is False
            and report.get("semantic_mismatch_count") == "NOT MEASURED"
            and report.get("verified_passing_case_count") == "NOT MEASURED"
            and report.get("completed_suite_count") == "NOT MEASURED"
            and report.get("original_native_restored") is True
            and report.get("hidden_cases_read") == 0
            and report.get("benchmark_files_read") == 0
            and report.get("clock_samples") == 0
            and report.get("timing_trials_run") == 0
            and report.get("holdout") == "NOT OPENED"
            and report.get("performance") == "NOT MEASURED"
            and report.get("memory") == "NOT MEASURED",
            "preserve the real failed C run; never invent C matching results")
    require(type(aggregate) is dict
            and aggregate.get("actual_aggregate_processes") == 1
            and aggregate.get("returncode") == 1
            and aggregate.get("timed_out") is False
            and aggregate.get("stdout_bytes") == 517
            and aggregate.get("stdout_sha256")
            == "93899f2cfc24a638785af66e683ca2f0866488be9cfbcdc2ffdd73be1b8e3f65"
            and aggregate.get("stderr_bytes") == 0
            and aggregate.get("stderr_sha256") == digest(b""),
            "preserve the sole actual failed C aggregate process")
    try:
        stdout = base64.b64decode(
            aggregate["stdout_base64"].encode("ascii"), validate=True,
        )
        stderr = base64.b64decode(
            aggregate["stderr_base64"].encode("ascii"), validate=True,
        )
    except (ValueError, UnicodeError) as error:
        raise FreezeError("reject altered actual C failure process streams") from error
    require(len(stdout) == aggregate["stdout_bytes"]
            and digest(stdout) == aggregate["stdout_sha256"]
            and stderr == b"",
            "bind the actual failing C process to every original output byte")
    entry = strict_json(stdout, "preserved C V9 entry infrastructure failure")
    require(entry.get("schema") == "rebar-frozen-python-re-p0-candidate-v9-entry-failure"
            and entry.get("status") == "FAIL"
            and entry.get("error_type") == "AttributeError"
            and entry.get("error_message")
            == "'Namespace' object has no attribute 'runner_source_sha256'"
            and entry.get("actual_candidate_workers") == 0
            and entry.get("actual_reference_workers") == 0
            and entry.get("actual_source_builds") == 0
            and entry.get("actual_native_activations") == 0
            and entry.get("candidate_qualified") is False
            and entry.get("hidden_cases_read") == 0
            and entry.get("clock_samples") == 0
            and entry.get("holdout") == "NOT OPENED",
            "distinguish the failed C entry from a completed matching campaign")
    actual_archive = receipt.get("archive")
    observed_archive = protected_owners[RECOVERED_C_ARCHIVE]
    observed_receipt = protected_owners[RECOVERED_C_RECEIPT]
    require(type(actual_archive) is dict
            and receipt.get("schema")
            == "rebar-owned-repaired-c-original-campaign-v2-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("family") == "c"
            and receipt.get("label") == "phase2-v9-original-p0"
            and receipt.get("historical_evidence_owner_count")
            == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
            and receipt.get("historical_authenticated_reference_count")
            == HISTORICAL_V21_REFERENCE_COUNT
            and receipt.get("uncompressed_bytes") == len(plain)
            and receipt.get("uncompressed_sha256") == digest(plain)
            and receipt.get("original_native_restored") is True
            and receipt.get("holdout") == "NOT OPENED"
            and actual_archive.get("relative") == RECOVERED_C_ARCHIVE
            and actual_archive.get("sha256") == RECOVERED_C_ARCHIVE_SHA256
            and actual_archive.get("size_bytes") == len(archive_raw)
            and actual_archive.get("device") == observed_archive["device"]
            and actual_archive.get("inode") == observed_archive["inode"]
            and actual_archive.get("mode") == 0o600
            and actual_archive.get("exclusive_creation") is True
            and actual_archive.get("same_inode_readback_verified") is True
            and actual_archive.get("file_fsync_completed") is True
            and actual_archive.get("directory_fsync_completed") is True
            and (observed_archive["device"], observed_archive["inode"])
            != (observed_receipt["device"], observed_receipt["inode"]),
            "authenticate both distinct durable recovered C failure owners")

    require(callable(getattr(overlay, "discover_evidence", None))
            and callable(getattr(overlay, "checked_read", None))
            and callable(getattr(overlay, "strict_json", None))
            and type(getattr(overlay, "SUPPORT", None)) is dict,
            "use only the committed overlay's authenticated historical graph")
    history: dict[str, str] = {}
    for path in (
        "docs/evidence/candidate-current-overview-v19.inputs.json",
        "docs/evidence/candidate-current-overview-v19.json",
    ):
        valid_digest(overlay.SUPPORT.get(path), path)
        value = overlay.strict_json(
            overlay.checked_read(path, overlay.SUPPORT[path]), path,
        )
        overlay.discover_evidence(value, history)
    require(len(history) == 76,
            "independently preserve the complete historical V19 evidence graph")
    old_summary_path = "docs/evidence/candidate-current-overview-v20.json"
    valid_digest(overlay.SUPPORT.get(old_summary_path), old_summary_path)
    old_summary = overlay.strict_json(
        overlay.checked_read(old_summary_path,
                             overlay.SUPPORT[old_summary_path]),
        old_summary_path,
    )
    old_snapshot = old_summary.get("snapshot")
    old_build = old_snapshot.get("c_v8_repaired_build") \
        if type(old_snapshot) is dict else None
    require(type(old_build) is dict and old_build.get("status") == "PASS",
            "retain the two real V20 source-build history owners")
    for role in ("archive", "receipt"):
        item = old_build.get(role)
        require(type(item) is dict and type(item.get("path")) is str
                and item["path"].startswith("oracle/phase2/evidence/")
                and item["path"] not in history,
                "retain each distinct, previously published V20 evidence owner")
        history[item["path"]] = valid_digest(item.get("sha256"), item["path"])
    require(len(history) == 78,
            "preserve exactly the 78 genuinely authenticated V20 references")
    current_inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v21.inputs.json"],
        "historical V21 inputs",
    )
    campaign = current_inputs.get("repaired_c_original_campaign")
    require(type(campaign) is dict,
            "retain all previously frozen V21 C campaign evidence")
    additional: dict[str, str] = {}
    overlay.discover_evidence(campaign, additional)
    require(len(additional) == 30
            and not (set(additional) & set(history)),
            "preserve exactly the 30 distinct V21 campaign history references")
    history.update(additional)
    require(len(history) == HISTORICAL_V21_REFERENCE_COUNT
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 78
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "reconstruct the exact 108-reference historical V21 denominator")
    require(RECOVERED_C_ARCHIVE not in history
            and RECOVERED_C_RECEIPT not in history,
            "never silently recount a historical evidence file as new")
    history[RECOVERED_C_ARCHIVE] = RECOVERED_C_ARCHIVE_SHA256
    history[RECOVERED_C_RECEIPT] = RECOVERED_C_RECEIPT_SHA256
    require(len(history) == CURRENT_AUTHENTICATED_REFERENCE_COUNT
            and HISTORICAL_V21_EVIDENCE_OWNER_COUNT
            + ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT
            == CURRENT_EVIDENCE_OWNER_COUNT
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 80
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "authenticate 105 genuine current evidence owners and 110 references")
    return {
        "archive": observed_archive,
        "receipt": observed_receipt,
        "archive_status": "FAIL",
        "receipt_status": "PASS",
        "actual_aggregate_process_count": 1,
        "actual_candidate_worker_count": 0,
        "infrastructure_failure_count": 1,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "original_native_restored": True,
        "historical_v21_evidence_owner_count":
            HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
        "historical_v21_authenticated_reference_count":
            HISTORICAL_V21_REFERENCE_COUNT,
        "current_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "current_authenticated_reference_count":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def check_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PINNED_PYTHON
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "run only isolated, bytecode-free, independently pinned CPython 3.14.6")


def authenticate_context(source_pin: str, protocol_pin: str,
                         contract_pin: str | None = None,
                         *, retain: bool = False) -> tuple[dict[str, Any], dict]:
    check_runtime()
    valid_digest(source_pin, "V10 source")
    valid_digest(protocol_pin, "V10 protocol")
    source_owner, source_raw = read_repository_owner(
        SOURCE_RELATIVE, source_pin,
        _checked_repository_size(SOURCE_RELATIVE),
    )
    protocol_owner, _protocol_raw = read_repository_owner(
        PROTOCOL_RELATIVE, protocol_pin,
        _checked_repository_size(PROTOCOL_RELATIVE),
    )

    protected: dict[str, bytes] = {}
    protected_owners: dict[str, dict[str, Any]] = {}
    for relative, (expected, size) in sorted(SUPPORT_OWNERS.items()):
        owner, raw = read_repository_owner(relative, expected, size)
        protected[relative] = raw
        protected_owners[relative] = owner

    originals: dict[str, bytes] = {}
    original_owners: dict[str, dict[str, Any]] = {}
    for relative, (expected, size) in sorted(SOURCE_OWNERS.items()):
        owner, raw = read_repository_owner(relative, expected, size)
        originals[relative] = raw
        original_owners[relative] = owner
    require(len({(item["device"], item["inode"])
                 for item in original_owners.values()}) == 3,
            "require three genuinely distinct independently owned Zig sources")

    tools: dict[str, dict[str, Any]] = {}
    for name, (path, expected, size, executable) in sorted(
            TOOLCHAIN_OWNERS.items()):
        owner, _raw = read_absolute_owner(path, expected, size, executable)
        tools[name] = owner

    validate_phase_one(strict_json(
        protected["oracle/phase1/p0-completeness-v1.json"],
        "original phase-one oracle",
    ))
    validate_zig_lock(strict_json(
        protected["toolchains/zig-0.16.0.lock.json"],
        "official stable Zig lock",
        canonical_required=False,
    ))
    validate_corrected_v3(strict_json(
        protected["oracle/phase2/six-family-p0-producer-v3.json"],
        "independently corrected V3 source producer",
    ))
    validate_v7(strict_json(
        protected["oracle/phase2/native-source-build-v7.json"],
        "original generic V7 source build",
    ))
    validate_v21(
        strict_json(protected[
            "docs/evidence/candidate-current-overview-v21.inputs.json"
        ], "published V21 inputs"),
        strict_json(protected[
            "docs/evidence/candidate-current-overview-v21.json"
        ], "published V21 summary"),
    )

    overlay = load_authenticated_module(
        "_rebar_owned_v10_zig_scanner_overlay", OVERLAY_SOURCE,
        protected[OVERLAY_SOURCE],
    )
    require(getattr(overlay, "SCHEMA", None) == OVERLAY_SCHEMA
            and getattr(overlay, "PRIVATE_ROOT_PREFIX", None)
            == PRIVATE_ROOT_PREFIX
            and getattr(overlay, "SOURCE_PATH", None) == OVERLAY_SOURCE
            and getattr(overlay, "PROTOCOL_PATH", None) == OVERLAY_PROTOCOL
            and getattr(overlay, "CONTRACT_PATH", None) == OVERLAY_CONTRACT
            and callable(getattr(overlay, "verify_context", None))
            and callable(getattr(overlay, "apply_private", None)),
            "load only the hash-authenticated exact first-party overlay interface")
    overlay_value, derived = overlay.verify_context(
        OVERLAY_SOURCE_SHA256, OVERLAY_PROTOCOL_SHA256,
        OVERLAY_CONTRACT_SHA256,
    )
    require(canonical(overlay_value) == protected[OVERLAY_CONTRACT],
            "bind the overlay context to its exact independently frozen contract")
    validate_overlay(overlay_value, derived)
    recovered_c = validate_recovered_c_failure(
        protected, protected_owners, overlay,
    )

    contract_owner: dict[str, Any] | None = None
    if contract_pin is not None:
        valid_digest(contract_pin, "V10 contract")
        contract_owner, raw = read_repository_owner(
            CONTRACT_RELATIVE, contract_pin,
            _checked_repository_size(CONTRACT_RELATIVE),
        )
        document = strict_json(raw, "frozen V10 Zig scanner build contract")
        validate_contract(document, source_pin, protocol_pin)

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PASS",
        "mode": "READ-ONLY FROZEN CONTEXT",
        "version": 10,
        "source": source_owner,
        "protocol": protocol_owner,
        "contract": contract_owner,
        "authenticated_support_owner_count": len(protected_owners),
        "authenticated_zig_source_owner_count": len(original_owners),
        "authenticated_toolchain_owner_count": len(tools),
        "frozen_case_execution_count": 31_237,
        "frozen_suite_count": 13,
        "frozen_private_waiver_count": 13,
        "frozen_independent_family_count": 6,
        "frozen_source_owner_count": 25,
        "historical_v21_evidence_owner_count":
            HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
        "historical_v21_authenticated_reference_count":
            HISTORICAL_V21_REFERENCE_COUNT,
        "authoritative_counted_evidence_owner_count":
            CURRENT_EVIDENCE_OWNER_COUNT,
        "authenticated_digest_addressed_history_paths":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "additional_recovered_c_failure_evidence_owner_count":
            ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT,
        "recovered_c_failure": recovered_c,
        "historical_zig_semantic_mismatch_count": 1_764,
        "historical_zig_gate_status": "FAIL",
        "preserved_scanner_verbose_mismatch_count": 620,
        "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
        "derived_source_sha256": DERIVED_BRIDGE_SHA256,
        "derived_source_bytes": DERIVED_BRIDGE_BYTES,
        "derived_source_materialized": False,
        "expected_build_process_count_only_after_success":
            EXPECTED_PROCESS_COUNT,
        "workspace_mutations": 0,
        **expected_phase_boundary(),
    }
    retained: dict[str, Any] = {}
    if retain:
        retained = {
            "overlay": overlay,
            "overlay_contract": overlay_value,
            "derived": derived,
            "protected": protected,
            "protected_owners": protected_owners,
            "originals": originals,
            "original_owners": original_owners,
            "toolchains": tools,
        }
    return result, retained


def _checked_repository_size(relative: str) -> int:
    parts = checked_relative(relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            owner = os.fstat(descriptor)
            require(stat.S_ISREG(owner.st_mode)
                    and 0 < owner.st_size <= MAX_SOURCE_BYTES
                    and owner.st_nlink == 1,
                    "require a bounded, exact, nonlinked V10 freeze owner")
            return owner.st_size
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def dynamic_and_symbols(parsed: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    require(type(parsed) is dict
            and parsed.get("format") == "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN",
            "audit only an authenticated complete first-party ELF64 artifact")
    dynamic = parsed.get("dynamic_tables")
    require(type(dynamic) is list and len(dynamic) == 1
            and type(dynamic[0]) is dict
            and type(dynamic[0].get("entries")) is list,
            "require one complete authenticated native dynamic table")
    symbol_record = parsed.get("symbol_tables")
    require(type(symbol_record) is dict
            and type(symbol_record.get("tables")) is list,
            "require complete authenticated first-party native symbol tables")
    tables = [item for item in symbol_record["tables"]
              if type(item) is dict and item.get("section_name") == ".dynsym"]
    require(len(tables) == 1 and type(tables[0].get("symbols")) is list,
            "require exactly one genuine, linked dynamic symbol table")
    return dynamic[0]["entries"], tables[0]["symbols"]


def audit_native_role(role: str, parsed: dict[str, Any]) -> dict[str, Any]:
    require(role in ("engine", "bridge"),
            "audit only an independently built owned Zig engine or bridge")
    entries, symbols = dynamic_and_symbols(parsed)
    require(all(type(item) is dict for item in entries)
            and all(type(item) is dict for item in symbols),
            "require real, individually authenticated native owners")
    needed = [item.get("name") for item in entries if item.get("tag") == 1]
    sonames = [item.get("name") for item in entries if item.get("tag") == 14]
    legacy_rpaths = [item.get("name") for item in entries if item.get("tag") == 15]
    runpaths = [item.get("name") for item in entries if item.get("tag") == 29]
    require(all(type(item) is str for item in needed + sonames
                + legacy_rpaths + runpaths)
            and len(set(needed)) == len(needed)
            and len(sonames) <= 1 and len(runpaths) <= 1
            and not legacy_rpaths,
            "reject ambiguous, repeated, redirected, or legacy native dependencies")
    defined: set[str] = set()
    undefined: set[str] = set()
    for item in symbols:
        name = item.get("name")
        index = item.get("section_index")
        require(type(name) is str and type(index) is int and index >= 0,
                "reject a malformed or unbound dynamic symbol")
        if not name:
            continue
        target = undefined if index == 0 else defined
        require(name not in target,
                "reject an aliased first-party dynamic symbol: " + name)
        target.add(name)
        lowered = name.lower()
        require(name not in FORBIDDEN_SYMBOLS
                and not any(lowered.startswith(prefix)
                            for prefix in FORBIDDEN_SYMBOL_PREFIXES),
                "reject stdlib regex, external engine, loader, or foreign candidate: "
                + name)
    require(not (defined & undefined),
            "reject one symbol simultaneously owned and imported")
    if role == "engine":
        require(needed == ["libc.so.6"]
                and sonames == [ENGINE_FILENAME]
                and not runpaths,
                "require one own-soname Zig engine with only libc dependency")
        require(REQUIRED_ENGINE_EXPORTS.issubset(defined),
                "preserve every first-party native Zig engine export")
        unicode = {item for item in undefined if item.startswith("_PyUnicode_")}
        require(unicode == ALLOWED_ENGINE_UNICODE_HELPERS,
                "permit only the original seven CPython Unicode data helpers")
        require(not any(item.startswith("rebar_") for item in undefined),
                "the owned Zig engine cannot delegate matching to another engine")
    else:
        require(needed == [ENGINE_FILENAME, "libc.so.6"]
                and not sonames
                and runpaths == ["$ORIGIN"],
                "bind the extension only to its own adjacent Zig engine and libc")
        require("PyInit__zig_bridge" in defined
                and REQUIRED_BRIDGE_ENGINE_IMPORTS.issubset(undefined),
                "preserve the real CPython bridge and its own native Zig calls")
        require({item for item in undefined if item.startswith("rebar_")}
                == REQUIRED_BRIDGE_ENGINE_IMPORTS,
                "reject an indirect or cross-family semantic engine dependency")
    return {
        "role": role,
        "needed": needed,
        "soname": sonames[0] if sonames else None,
        "runpath": runpaths[0] if runpaths else None,
        "legacy_rpath_count": len(legacy_rpaths),
        "defined_dynamic_symbol_count": len(defined),
        "undefined_dynamic_symbol_count": len(undefined),
        "defined_first_party_symbols": sorted(
            item for item in defined if item.startswith("rebar_zig_")
        ),
        "imported_first_party_symbols": sorted(
            item for item in undefined if item.startswith("rebar_zig_")
        ),
        "allowed_engine_unicode_helpers": sorted(
            item for item in undefined if item in ALLOWED_ENGINE_UNICODE_HELPERS
        ),
        "external_regex_engine_count": 0,
        "stdlib_regex_engine_count": 0,
        "cross_family_engine_count": 0,
        "network_symbol_count": 0,
        "native_loader_symbol_count": 0,
    }


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve every bounded byte from an actual compiler process")
    return {
        "bytes": len(raw),
        "sha256": digest(raw),
        "base64": base64.b64encode(raw).decode("ascii"),
        "complete": True,
    }


def decode_stream(value: Any) -> bytes:
    require(type(value) is dict and value.get("complete") is True
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and type(value.get("base64")) is str,
            "require one complete bounded actual process stream")
    valid_digest(value.get("sha256"), "actual compiler stream")
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise FreezeError("reject a truncated or fabricated compiler stream") from error
    require(len(raw) == value["bytes"] and digest(raw) == value["sha256"],
            "bind compiler output to all of its actual original bytes")
    return raw


def validate_process_schedule(records: Any, workdir: str,
                              *, complete: bool = True) -> list[dict]:
    root = checked_workdir(workdir)
    require(type(records) is list,
            "require actual individually captured compiler processes")
    schedule = [(phase, name) for phase in PHASE_NAMES for name in PROCESS_ROLES]
    if complete:
        require(len(records) == len(schedule) == EXPECTED_PROCESS_COUNT,
                "count 26 processes only after both phases actually complete")
    else:
        require(len(records) <= len(schedule),
                "reject invented processes beyond the frozen actual schedule")
    identifiers: set[int] = set()
    for index, item in enumerate(records):
        require(type(item) is dict,
                "reject a missing or malformed actual process owner")
        phase, name = schedule[index]
        require(item.get("phase") == phase and item.get("name") == name,
                "reject missing, reordered, substituted, or cross-phase processes")
        checked_command(name, item.get("argv"), root, phase)
        require(item.get("working_directory")
                == str(phase_paths(root, phase)["base"])
                and item.get("environment") == build_environment(root, phase),
                "preserve the exact clean environment and private working root")
        pid = item.get("pid")
        require(type(pid) is int and pid > 0 and pid not in identifiers,
                "require one genuine, unique process identity per actual command")
        identifiers.add(pid)
        require(item.get("returncode") == 0
                and item.get("signal") is None,
                "reject a crashed, signalled, or failed actual compiler process")
        decode_stream(item.get("stdout"))
        decode_stream(item.get("stderr"))
    return records


def check_directory_descriptor(descriptor: int, label: str) -> dict[str, Any]:
    owner = os.fstat(descriptor)
    require(stat.S_ISDIR(owner.st_mode)
            and owner.st_uid == os.geteuid()
            and stat.S_IMODE(owner.st_mode) == 0o700,
            "require a fresh owned, non-symlinked mode-0700 directory: " + label)
    return {
        "path": label,
        "device": owner.st_dev,
        "inode": owner.st_ino,
        "mode": "0700",
    }


def private_directory(workdir: str, phase: str,
                      components: tuple[str, ...]) -> tuple[int, dict[str, Any]]:
    root = checked_workdir(workdir)
    require(phase in PHASE_NAMES,
            "open only an independently owned reference phase")
    require(type(components) is tuple
            and all(type(item) is str and item not in ("", ".", "..")
                    and "/" not in item and "\\" not in item
                    and "\x00" not in item for item in components),
            "reject escaped, substituted, or broad private phase components")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    tmp = os.open("/tmp", flags)
    current: int | None = None
    try:
        current = os.open(PurePosixPath(root).parts[2], flags, dir_fd=tmp)
        check_directory_descriptor(current, root)
        for part in (phase, *components):
            following = os.open(part, flags, dir_fd=current)
            check_directory_descriptor(following, part)
            os.close(current)
            current = following
        require(current is not None, "require an authenticated private directory")
        result = check_directory_descriptor(
            current, str(Path(root) / phase / Path(*components)),
        )
        descriptor = current
        current = None
        return descriptor, result
    finally:
        if current is not None:
            os.close(current)
        os.close(tmp)


def checked_private_child(path: Any, workdir: str,
                          phase: str | None = None) -> Path:
    root = Path(checked_workdir(workdir))
    require(isinstance(path, Path) and path.is_absolute()
            and path != root and path.is_relative_to(root)
            and all(part not in (".", "..")
                    and "\\" not in part and "\x00" not in part
                    for part in path.parts),
            "create only an exact descendant of the fresh private build root")
    if phase is not None:
        require(phase in PHASE_NAMES
                and path.is_relative_to(root / phase),
                "reject a reused or cross-phase private source directory")
    return path


def create_private_directory(path: Path, workdir: str,
                             phase: str | None = None) -> dict[str, Any]:
    path = checked_private_child(path, workdir, phase)
    os.mkdir(str(path), 0o700)
    descriptor = os.open(str(path),
                         os.O_RDONLY | os.O_CLOEXEC
                         | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return check_directory_descriptor(descriptor, str(path))
    finally:
        os.close(descriptor)


def prepare_private_phases(workdir: str) -> list[dict[str, Any]]:
    root = checked_workdir(workdir)
    prepared: list[dict[str, Any]] = []
    for phase in PHASE_NAMES:
        paths = phase_paths(root, phase)
        directories: dict[str, dict[str, Any]] = {}
        for key in ("base", "source", "source_candidates", "source_zig",
                    "native", "temporary", "zig_local_cache",
                    "zig_global_cache"):
            directories[key] = create_private_directory(
                paths[key], root, phase,
            )
        prepared.append({"name": phase, "directories": directories})
    identities = [item["directories"]["base"] for item in prepared]
    require(len({(item["device"], item["inode"]) for item in identities}) == 2,
            "the two source-build phases must be genuinely independent owners")
    return prepared


def assert_bridge_absent(workdir: str, phase: str) -> None:
    directory, _owner = private_directory(
        workdir, phase, ("source", "candidates", "zig"),
    )
    try:
        try:
            os.stat("py_bridge.c", dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise FreezeError(
            "never copy, replace, or pre-create the frozen private Zig bridge"
        )
    finally:
        os.close(directory)


def write_private_source(workdir: str, phase: str, relative: str,
                         raw: bytes, expected: str) -> dict[str, Any]:
    require(relative in (ORIGINAL_ENGINE, ORIGINAL_ADAPTER)
            and type(raw) is bytes and digest(raw) == expected
            and SOURCE_OWNERS[relative] == (expected, len(raw)),
            "snapshot only an exact immutable original Zig engine or adapter")
    components = tuple(checked_relative(relative))
    directory, _owner = private_directory(
        workdir, phase, ("source", *components[:-1]),
    )
    descriptor: int | None = None
    try:
        descriptor = os.open(
            components[-1],
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require one freshly created private phase-source owner")
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(type(count) is int and count > 0,
                    "complete every byte of the fresh private source snapshot")
            offset += count
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == len(raw),
                "reject a swapped or incomplete private source snapshot")
        os.close(descriptor)
        descriptor = None
        verify = os.open(components[-1],
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                         dir_fd=directory)
        try:
            result, repeated = read_descriptor(
                verify, expected, len(raw), MAX_SOURCE_BYTES,
                str(phase_paths(workdir, phase)["source"] / relative),
                private=True,
            )
        finally:
            os.close(verify)
        require(repeated == raw and result["device"] == after.st_dev
                and result["inode"] == after.st_ino,
                "authenticate the exact same newly owned phase-source inode")
        os.fsync(directory)
        return result
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def authenticate_private_bridge(workdir: str, phase: str) -> dict[str, Any]:
    directory, _owner = private_directory(
        workdir, phase, ("source", "candidates", "zig"),
    )
    try:
        descriptor = os.open("py_bridge.c",
                             os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=directory)
        try:
            owner, _raw = read_descriptor(
                descriptor, DERIVED_BRIDGE_SHA256, DERIVED_BRIDGE_BYTES,
                MAX_SOURCE_BYTES,
                str(phase_paths(workdir, phase)["source_bridge"]),
                private=True,
            )
            return owner
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def capture_native_artifact(workdir: str, phase: str,
                            role: str) -> tuple[dict[str, Any], bytes]:
    require(role in ("engine", "bridge"),
            "capture only an exact independently compiled Zig native role")
    directory, _owner = private_directory(workdir, phase, ("native",))
    filename = ENGINE_FILENAME if role == "engine" else BRIDGE_FILENAME
    try:
        descriptor = os.open(filename,
                             os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and before.st_uid == os.geteuid()
                    and before.st_nlink == 1
                    and 0 < before.st_size <= MAX_BINARY_BYTES,
                    "require one genuine freshly linked private ELF owner")
            chunks: list[bytes] = []
            total = 0
            while True:
                piece = os.read(descriptor,
                                min(1024 * 1024,
                                    MAX_BINARY_BYTES + 1 - total))
                if not piece:
                    break
                total += len(piece)
                require(total <= MAX_BINARY_BYTES,
                        "bound the complete independently built native artifact")
                chunks.append(piece)
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_nlink, after.st_mtime_ns, after.st_ctime_ns),
                    "reject a replaced or altered private native artifact")
            raw = b"".join(chunks)
            require(len(raw) == before.st_size,
                    "capture every byte of the genuine native artifact")
            return source_owner_metadata(
                str(phase_paths(workdir, phase)["artifact_" + role]),
                after,
                digest(raw),
            ), raw
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def run_process(name: str, workdir: str, phase: str,
                records: list[dict[str, Any]]) -> dict[str, Any]:
    commands = planned_commands(workdir, phase)
    argv = checked_command(name, commands[name], workdir, phase)
    cwd = str(phase_paths(workdir, phase)["base"])
    environment = build_environment(workdir, phase)
    process = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=environment,
        shell=False,
        close_fds=True,
    )
    stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes,
            "capture complete original process output without a shell")
    record = {
        "phase": phase,
        "name": name,
        "argv": argv,
        "working_directory": cwd,
        "environment": environment,
        "pid": process.pid,
        "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    records.append(record)
    require(process.returncode == 0,
            "preserve a genuine failed native process: " + phase + "/" + name)
    if name == "zig_version":
        require(stdout == b"0.16.0\n",
                "reject an unofficial or substituted stable Zig compiler")
    if name in ("readelf_version", "gcc_version"):
        require(bool(stdout), "capture the genuine pinned native tool version")
    if name.endswith(("_dynamic", "_symbols", "_sections")):
        require(bool(stdout),
                "retain the complete real native ELF forensic output")
    return record


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    selected = checked_label(label)
    suffix = "-failures" if failed else ""
    base = "native-source-build-v10-zig-" + selected + suffix
    return base + ".json.gz", base + "-publication-receipt.json"


def evidence_directory() -> int:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    current = os.open(str(ROOT), flags)
    try:
        for part in checked_relative(EVIDENCE_RELATIVE):
            following = os.open(part, flags, dir_fd=current)
            check_directory_descriptor(following, part)
            os.close(current)
            current = following
        result = current
        current = -1
        return result
    finally:
        if current >= 0:
            os.close(current)


def require_fresh_evidence(label: str) -> None:
    selected = checked_label(label)
    directory = evidence_directory()
    try:
        for failed in (False, True):
            for name in evidence_names(selected, failed):
                try:
                    descriptor = os.open(
                        name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                        dir_fd=directory,
                    )
                except OSError as error:
                    if error.errno == errno.ENOENT:
                        continue
                    raise
                os.close(descriptor)
                raise FreezeError(
                    "never overwrite or reuse a published Zig evidence owner: "
                    + name
                )
    finally:
        os.close(directory)


def exclusive_publication(directory: int, name: str,
                          raw: bytes) -> dict[str, Any]:
    require(type(name) is str and "/" not in name and "\\" not in name
            and name not in ("", ".", "..")
            and type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "publish only one exact bounded, exclusive Zig evidence owner")
    descriptor: int | None = None
    try:
        descriptor = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require a newly owned nonlinked mode-0600 evidence owner")
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(type(count) is int and count > 0,
                    "publish every original evidence byte")
            offset += count
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == len(raw),
                "reject swapped or incompletely synchronized native evidence")
        os.close(descriptor)
        descriptor = None
        verify = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                         dir_fd=directory)
        try:
            owner, repeated = read_descriptor(
                verify, digest(raw), len(raw), MAX_ARCHIVE_BYTES,
                EVIDENCE_RELATIVE + "/" + name,
                private=True,
            )
        finally:
            os.close(verify)
        require(repeated == raw and owner["device"] == after.st_dev
                and owner["inode"] == after.st_ino,
                "prove a complete same-inode fresh evidence readback")
        os.fsync(directory)
        owner["file_fsync"] = True
        owner["directory_fsync"] = True
        return owner
    finally:
        if descriptor is not None:
            os.close(descriptor)


def publish_report(report: dict[str, Any], label: str) -> dict[str, Any]:
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(label, failed)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "bound the complete actual native build and forensic report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_ARCHIVE_BYTES,
            "bound the deterministic actual source-build evidence archive")
    directory = evidence_directory()
    try:
        archive_owner = exclusive_publication(directory, archive_name, archive)
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "version": 10,
            "status": "PASS",
            "build_status": report["status"],
            "family": "zig",
            "label": checked_label(label),
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "contract_sha256": report["contract_sha256"],
            "archive": archive_owner,
            "uncompressed_sha256": digest(plain),
            "uncompressed_bytes": len(plain),
            "historical_v21_evidence_owner_count":
                HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
            "historical_v21_authenticated_reference_count":
                HISTORICAL_V21_REFERENCE_COUNT,
            "current_evidence_owner_count_before_publication":
                CURRENT_EVIDENCE_OWNER_COUNT,
            "current_authenticated_reference_count_before_publication":
                CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "new_evidence_owner_count_after_receipt_publication": 2,
            "expected_build_process_count_only_after_success":
                EXPECTED_PROCESS_COUNT,
            "actual_build_process_count": report["actual_build_process_count"],
            "actual_source_apply_count": report["actual_source_apply_count"],
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "native_libraries_loaded": 0,
            "network_requests": 0,
            "hidden_cases_read": 0,
            "final_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
            "failure_preserved": failed,
            "receipt_self_publication": "NOT CLAIMED",
        }
        raw_receipt = canonical(receipt)
        require(len(raw_receipt) <= MAX_SOURCE_BYTES,
                "bound the complete independent durable build receipt")
        receipt_owner = exclusive_publication(
            directory, receipt_name, raw_receipt,
        )
        return {
            "schema": SCHEMA + "-publication-result",
            "status": report["status"],
            "family": "zig",
            "label": checked_label(label),
            "archive": archive_owner,
            "receipt": receipt_owner,
            "failure_preserved": failed,
            "expected_build_process_count_only_after_success":
                EXPECTED_PROCESS_COUNT,
            "actual_build_process_count": report["actual_build_process_count"],
            "actual_source_apply_count": report["actual_source_apply_count"],
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }
    finally:
        os.close(directory)


def authenticate_v7_parser(raw: bytes) -> types.ModuleType:
    module = load_authenticated_module(
        "_rebar_owned_v10_zig_v7_elf",
        "tools/reproduce_owned_native_source_build_v7.py",
        raw,
    )
    require(getattr(module, "SCHEMA", None)
            == "rebar-phase2-owned-native-source-build-v7"
            and getattr(module, "SOURCE_RELATIVE", None)
            == "tools/reproduce_owned_native_source_build_v7.py"
            and callable(getattr(module, "parse_owned_elf64", None))
            and callable(getattr(module, "compare_owned_elf64", None))
            and getattr(module, "MAX_BINARY_BYTES", None) == MAX_BINARY_BYTES,
            "use only the exact frozen first-party V7 complete-byte ELF parser")
    return module


def run_build(source_pin: str, protocol_pin: str, contract_pin: str,
              label: str) -> tuple[int, dict[str, Any]]:
    selected_label = checked_label(label)
    context, retained = authenticate_context(
        source_pin, protocol_pin, contract_pin, retain=True,
    )
    require(context["status"] == "PASS",
            "authenticate the complete independent V10 source freeze first")
    require_fresh_evidence(selected_label)
    overlay = retained["overlay"]
    derived = retained["derived"]
    v7 = authenticate_v7_parser(
        retained["protected"]["tools/reproduce_owned_native_source_build_v7.py"],
    )
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": 10,
        "status": "FAIL",
        "family": "zig",
        "label": selected_label,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "frozen_correctness": {
            "python": "3.14.6",
            "suite_count": 13,
            "case_execution_count": 31_237,
            "private_waiver_count": 13,
        },
        "historical_v21_evidence_owner_count":
            HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
        "historical_v21_authenticated_reference_count":
            HISTORICAL_V21_REFERENCE_COUNT,
        "current_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "current_authenticated_reference_count":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "historical_zig_semantic_mismatch_count": 1_764,
        "expected_build_process_count_only_after_success":
            EXPECTED_PROCESS_COUNT,
        "actual_build_process_count": 0,
        "actual_source_apply_count": 0,
        "processes": [],
        "build_phases": [],
        "reproducibility": "NOT MEASURED",
        "raw_elf_differences": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "reference_processes_started": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "final_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
        "owned_original_sources_before": retained["original_owners"],
        "owned_original_sources_after": "NOT MEASURED",
    }
    actual_raw: dict[tuple[str, str], bytes] = {}
    try:
        root = tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX, dir="/tmp")
        checked_workdir(root)
        descriptor = os.open(root,
                             os.O_RDONLY | os.O_CLOEXEC
                             | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            report["private_root"] = check_directory_descriptor(descriptor, root)
        finally:
            os.close(descriptor)

        phases = prepare_private_phases(root)
        report["build_phases"] = phases
        for item in phases:
            phase = item["name"]
            item["source_snapshots"] = {
                relative: write_private_source(
                    root, phase, relative,
                    retained["originals"][relative],
                    SOURCE_OWNERS[relative][0],
                )
                for relative in (ORIGINAL_ADAPTER, ORIGINAL_ENGINE)
            }
            assert_bridge_absent(root, phase)

        for item in phases:
            phase = item["name"]
            applied = overlay.apply_private(
                str(phase_paths(root, phase)["source"]), derived,
            )
            report["actual_source_apply_count"] += 1
            require(type(applied) is dict
                    and applied.get("schema") == OVERLAY_SCHEMA
                    and applied.get("status") == "PASS"
                    and applied.get("phase") == phase
                    and applied.get("source_apply_count") == 1
                    and applied.get("candidate_original_modified") is False
                    and applied.get("derived_sha256") == DERIVED_BRIDGE_SHA256
                    and applied.get("derived_bytes") == DERIVED_BRIDGE_BYTES
                    and applied.get("snapshot_root")
                    == str(phase_paths(root, phase)["source"]),
                    "reject an altered, repeated, failed, or cross-phase overlay")
            item["overlay_application"] = applied
            item["source_snapshots"][ORIGINAL_BRIDGE] = (
                authenticate_private_bridge(root, phase)
            )

        require(report["actual_source_apply_count"] == 2,
                "apply the committed source overlay exactly once to each phase")
        for relative in SOURCE_OWNERS:
            identities = [item["source_snapshots"][relative]
                          for item in phases]
            require(len({(item["device"], item["inode"])
                         for item in identities}) == 2,
                    "reject source snapshots shared between independent phases")

        for item in phases:
            phase = item["name"]
            for name in PROCESS_ROLES[:5]:
                try:
                    run_process(name, root, phase, report["processes"])
                finally:
                    report["actual_build_process_count"] = len(
                        report["processes"]
                    )
            outputs: dict[str, Any] = {}
            for role in ("engine", "bridge"):
                owner, raw = capture_native_artifact(root, phase, role)
                parsed = v7.parse_owned_elf64(raw)
                require(type(parsed) is dict
                        and parsed.get("file_sha256") == owner["sha256"]
                        and parsed.get("file_size") == owner["bytes"],
                        "bind V7 ELF forensics to actual full same-inode bytes")
                outputs[role] = {
                    "owner": owner,
                    "raw_elf64": parsed,
                    "independence_audit": audit_native_role(role, parsed),
                }
                key = (phase, role)
                require(key not in actual_raw,
                        "never alias, replace, or reuse a phase native output")
                actual_raw[key] = raw
            item["native_outputs"] = outputs
            for name in PROCESS_ROLES[5:]:
                try:
                    run_process(name, root, phase, report["processes"])
                finally:
                    report["actual_build_process_count"] = len(
                        report["processes"]
                    )
            for role in ("engine", "bridge"):
                owner, repeated = capture_native_artifact(root, phase, role)
                original = outputs[role]["owner"]
                require(repeated == actual_raw[(phase, role)]
                        and (owner["device"], owner["inode"], owner["sha256"])
                        == (original["device"], original["inode"],
                            original["sha256"]),
                        "preserve the identical native inode after all ELF inspections")

        validate_process_schedule(report["processes"], root, complete=True)
        require(report["actual_build_process_count"] == EXPECTED_PROCESS_COUNT,
                "claim twenty-six processes only after all twenty-six exist")
        differences: dict[str, Any] = {}
        for role in ("engine", "bridge"):
            first = phases[0]["native_outputs"][role]
            second = phases[1]["native_outputs"][role]
            require((first["owner"]["device"], first["owner"]["inode"])
                    != (second["owner"]["device"],
                        second["owner"]["inode"]),
                    "require independently owned native artifact phase inodes")
            difference = v7.compare_owned_elf64(
                actual_raw[(PHASE_NAMES[0], role)],
                actual_raw[(PHASE_NAMES[1], role)],
                first["raw_elf64"], second["raw_elf64"],
            )
            differences[role] = difference
        report["raw_elf_differences"] = {
            "schema": SCHEMA + "-all-phase-raw-elf-differences",
            "independent_phase_count": 2,
            "native_role_count": 2,
            "roles": differences,
            "all_native_artifacts_byte_identical": all(
                value.get("byte_identical") is True
                for value in differences.values()
            ),
            "additional_compiler_or_inspector_processes": 0,
            "comparison_completed_before_reproducibility_classification": True,
        }
        require(report["raw_elf_differences"][
            "all_native_artifacts_byte_identical"
        ], "preserve a genuine two-phase native reproducibility failure")
        report["reproducibility"] = {
            "status": "PASS",
            "independent_phase_count": 2,
            "byte_identical_native_role_count": 2,
            "compiler_process_count": len(report["processes"]),
            "source_apply_count": report["actual_source_apply_count"],
            "roles": {
                role: {
                    "sha256": phases[0]["native_outputs"][role]["owner"][
                        "sha256"
                    ],
                    "bytes": phases[0]["native_outputs"][role]["owner"][
                        "bytes"
                    ],
                    "phase_owner_count": 2,
                    "byte_identical": True,
                }
                for role in ("engine", "bridge")
            },
        }
        after: dict[str, dict[str, Any]] = {}
        for relative, (expected, size) in sorted(SOURCE_OWNERS.items()):
            owner, raw = read_repository_owner(relative, expected, size)
            before = retained["original_owners"][relative]
            require((owner["device"], owner["inode"], owner["sha256"])
                    == (before["device"], before["inode"], before["sha256"])
                    and raw == retained["originals"][relative],
                    "never change any original independently owned Zig source")
            after[relative] = owner
        report["owned_original_sources_after"] = after
        renewed, _discard = authenticate_context(
            source_pin, protocol_pin, contract_pin,
        )
        require(renewed["status"] == "PASS"
                and renewed["source"]["sha256"] == source_pin
                and renewed["protocol"]["sha256"] == protocol_pin
                and type(renewed["contract"]) is dict
                and renewed["contract"]["sha256"] == contract_pin,
                "the complete independently frozen context changed during the build")
        report["status"] = "PASS"
    except Exception as error:
        report["actual_build_process_count"] = len(report["processes"])
        report["status"] = "FAIL"
        report["error"] = {
            "type": type(error).__name__,
            "message": str(error),
        }
    publication = publish_report(report, selected_label)
    return (0 if report["status"] == "PASS" else 1), publication


class SyntheticBoundary:
    """Reject filesystem, compiler, candidate, native, network, and clock effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, Any]] = []
        self.blocked: dict[str, int] = {
            "filesystem": 0,
            "process": 0,
            "temporary": 0,
            "network": 0,
            "native": 0,
            "candidate_import": 0,
            "thread": 0,
            "clock": 0,
        }

    def install(self, owner: object, name: str, kind: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def reject(*_arguments: Any, **_keywords: Any) -> Any:
            self.blocked[kind] += 1
            raise SourceOnlyError(
                "synthetic source-only boundary blocked " + kind + ": " + name
            )

        self.saved.append((owner, name, original))
        setattr(owner, name, reject)

    def __enter__(self) -> SyntheticBoundary:
        groups: tuple[tuple[object, tuple[str, ...], str], ...] = (
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "write", "fstat", "stat", "lstat",
                  "mkdir", "makedirs", "listdir", "scandir", "unlink",
                  "remove", "rename", "replace", "link", "symlink",
                  "chmod", "fchmod", "fsync", "chdir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "exists", "is_file",
                    "is_dir", "mkdir", "unlink", "rename", "replace",
                    "resolve", "iterdir"), "filesystem"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output"), "process"),
            (os, ("system", "popen", "fork", "posix_spawn"), "process"),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile",
                        "TemporaryDirectory"), "temporary"),
            (socket, ("socket", "create_connection", "getaddrinfo"),
             "network"),
            (ctypes, ("CDLL", "PyDLL", "WinDLL", "OleDLL"), "native"),
            (importlib, ("import_module",), "candidate_import"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns",
                    "clock_gettime", "clock_gettime_ns", "sleep"), "clock"),
        )
        for owner, names, kind in groups:
            for name in names:
                self.install(owner, name, kind)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_native(role: str) -> dict[str, Any]:
    require(role in ("engine", "bridge"),
            "construct only in-memory synthetic native audit controls")
    if role == "engine":
        entries = [
            {"tag": 1, "name": "libc.so.6"},
            {"tag": 14, "name": ENGINE_FILENAME},
        ]
        symbols = [
            {"name": name, "section_index": 1}
            for name in sorted(REQUIRED_ENGINE_EXPORTS)
        ] + [
            {"name": name, "section_index": 0}
            for name in sorted(ALLOWED_ENGINE_UNICODE_HELPERS)
        ]
    else:
        entries = [
            {"tag": 1, "name": ENGINE_FILENAME},
            {"tag": 1, "name": "libc.so.6"},
            {"tag": 29, "name": "$ORIGIN"},
        ]
        symbols = [
            {"name": "PyInit__zig_bridge", "section_index": 1},
            *({"name": name, "section_index": 0}
              for name in sorted(REQUIRED_BRIDGE_ENGINE_IMPORTS)),
        ]
    return {
        "format": "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN",
        "dynamic_tables": [{"entries": entries}],
        "symbol_tables": {"tables": [
            {"section_name": ".dynsym", "symbols": symbols},
        ]},
    }


def synthetic_records(workdir: str) -> list[dict[str, Any]]:
    root = checked_workdir(workdir)
    empty = encode_stream(b"")
    records: list[dict[str, Any]] = []
    for phase in PHASE_NAMES:
        for name, argv in planned_commands(root, phase).items():
            records.append({
                "phase": phase,
                "name": name,
                "argv": list(argv),
                "working_directory": str(phase_paths(root, phase)["base"]),
                "environment": build_environment(root, phase),
                "pid": 1_000_000 + len(records),
                "returncode": 0,
                "signal": None,
                "stdout": dict(empty),
                "stderr": dict(empty),
            })
    return records


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    check_runtime()
    valid_digest(source_pin, "V10 source")
    valid_digest(protocol_pin, "V10 protocol")
    valid_digest(contract_pin, "V10 contract")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected
                and bool(value),
                "a unique positive source-only control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected
                and callable(action),
                "require one unique genuine hostile source-only control")
        try:
            action()
        except (FreezeError, SourceOnlyError, OSError, ValueError, TypeError,
                UnicodeError, OverflowError, RecursionError, KeyError):
            rejected.append(name)
            return
        raise FreezeError("a hostile source-only control was accepted: " + name)

    with SyntheticBoundary() as boundary:
        root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v10"
        accept("exact-lowercase-digest", valid_digest("a" * 64, "synthetic"))
        accept("exact-lowercase-label", checked_label("phase2-v10-zig"))
        accept("exact-sealed-overlay-root", checked_workdir(root) == root)
        accept("both-sibling-phase-names", PHASE_NAMES
               == ("reference-a", "reference-b"))
        accept("distinct-phase-source-paths",
               phase_paths(root, "reference-a")["source"]
               != phase_paths(root, "reference-b")["source"])
        accept("accept-real-concrete-posix-phase-path",
               checked_private_child(
                   phase_paths(root, "reference-a")["base"],
                   root, "reference-a",
               ) == phase_paths(root, "reference-a")["base"])
        accept("accept-real-concrete-posix-source-path",
               checked_private_child(
                   phase_paths(root, "reference-a")["source_zig"],
                   root, "reference-a",
               ) == phase_paths(root, "reference-a")["source_zig"])
        accept("distinct-phase-local-cache-paths",
               phase_paths(root, "reference-a")["zig_local_cache"]
               != phase_paths(root, "reference-b")["zig_local_cache"])
        accept("distinct-phase-global-cache-paths",
               phase_paths(root, "reference-a")["zig_global_cache"]
               != phase_paths(root, "reference-b")["zig_global_cache"])
        accept("both-exact-reproducible-source-prefix-flags",
               len(prefix_flags(root)) == 2
               and all(flag.endswith("=" + CANONICAL_SOURCE_PREFIX)
                       for flag in prefix_flags(root)))
        accept("thirteen-exact-first-phase-roles",
               tuple(planned_commands(root, "reference-a")) == PROCESS_ROLES)
        accept("thirteen-exact-second-phase-roles",
               tuple(planned_commands(root, "reference-b")) == PROCESS_ROLES)
        accept("pinned-releasefast-zig-engine",
               "ReleaseFast" in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"])
        accept("exact-explicit-both-zig-caches",
               "--cache-dir" in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"]
               and "--global-cache-dir" in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"])
        accept("exact-own-zig-engine-soname",
               "-fsoname=" + ENGINE_FILENAME in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"])
        accept("exact-pinned-gcc-bridge",
               planned_commands(root, "reference-a")["build_zig_bridge"][0]
               == PINNED_GCC)
        accept("exact-own-adjacent-engine-link",
               "-l:" + ENGINE_FILENAME in planned_commands(
                   root, "reference-a",
               )["build_zig_bridge"])
        accept("exact-own-origin-runpath",
               "-Wl,-rpath,$ORIGIN" in planned_commands(
                   root, "reference-a",
               )["build_zig_bridge"])
        accept("eight-exact-first-party-elf-inspections",
               sum(name.endswith(("_dynamic", "_symbols", "_sections", "_notes"))
                   for name in planned_commands(root, "reference-a")) == 8)
        accept("no-home-variable-in-clean-build-environment",
               "HOME" not in build_environment(root, "reference-a")
               and "home" not in build_environment(root, "reference-a"))
        accept("exact-private-environment",
               len(build_environment(root, "reference-a")) == 8
               and build_environment(root, "reference-a")["PATH"]
               == "/usr/bin:/bin")
        accept("authenticated-synthetic-engine-symbols",
               audit_native_role("engine", synthetic_native("engine"))["soname"]
               == ENGINE_FILENAME)
        accept("allowed-cpython-unicode-is-not-regex-delegation",
               set(audit_native_role(
                   "engine", synthetic_native("engine"),
               )["allowed_engine_unicode_helpers"])
               == ALLOWED_ENGINE_UNICODE_HELPERS)
        accept("authenticated-synthetic-bridge-symbols",
               audit_native_role("bridge", synthetic_native("bridge"))["runpath"]
               == "$ORIGIN")
        records = synthetic_records(root)
        accept("twenty-six-in-memory-only-synthetic-process-records",
               len(validate_process_schedule(records, root))
               == EXPECTED_PROCESS_COUNT)
        accept("canonical-complete-empty-process-stream",
               decode_stream(encode_stream(b"")) == b"")
        accept("canonical-complete-byte-process-stream",
               decode_stream(encode_stream(b"synthetic\x00\xff"))
               == b"synthetic\x00\xff")
        contract = contract_document(source_pin, protocol_pin)
        accept("complete-independent-source-freeze-contract",
               validate_contract(contract, source_pin, protocol_pin)["schema"]
               == CONTRACT_SCHEMA)
        accept("exact-103-counted-108-authenticated-history",
               contract["published_v21_history"][
                   "authoritative_counted_evidence_owner_count"
               ] == 103
               and contract["published_v21_history"][
                   "authenticated_digest_addressed_history_paths"
               ] == 108)
        accept("preserve-real-current-105-owner-110-reference-history",
               contract["current_published_history"][
                   "authoritative_counted_evidence_owner_count"
               ] == 105
               and contract["current_published_history"][
                   "authenticated_digest_addressed_history_paths"
               ] == 110)
        accept("preserve-failed-c-infrastructure-without-fake-matching",
               contract["current_published_history"]["recovered_c_failure"][
                   "archive_status"
               ] == "FAIL"
               and contract["current_published_history"][
                   "recovered_c_failure"
               ]["actual_candidate_worker_count"] == 0
               and contract["current_published_history"][
                   "recovered_c_failure"
               ]["semantic_mismatch_count"] == "NOT MEASURED")
        accept("preserve-actual-original-zig-failures",
               contract["published_v21_history"][
                   "historical_zig_semantic_mismatch_count"
               ] == 1_764)
        accept("planned-processes-are-not-actual-processes",
               contract["future_build_policy"]["actual_process_count"] == 0
               and contract["future_build_policy"][
                   "expected_total_process_count_only_after_success"
               ] == 26)
        accept("planned-overlay-is-not-actual-overlay",
               contract["frozen_overlay"]["actual_source_apply_count"] == 0)
        accept("native-output-digests-are-not-invented",
               all(item["sha256"] == "NOT MEASURED"
                   and item["bytes"] == "NOT MEASURED"
                   for item in contract["future_build_policy"][
                       "native_outputs"
                   ].values()))
        accept("preserve-frozen-original-case-denominator",
               contract["oracle"]["case_execution_count"] == 31_237
               and contract["oracle"]["suite_count"] == 13
               and contract["oracle"]["private_waiver_count"] == 13)
        accept("no-source-freeze-side-effects",
               contract["phase_boundary"] == expected_phase_boundary())
        accept("canonical-finite-round-trip",
               strict_json(canonical(contract), "synthetic contract") == contract)
        accept("distinct-exclusive-success-evidence",
               evidence_names("synthetic-v10", False)
               != evidence_names("synthetic-v10", True))

        for value in (
            "", "a" * 63, "a" * 65, "A" * 64, "z" * 64,
            "0" * 63 + "\n", 1, None,
        ):
            reject("reject-digest-" + repr(value),
                   lambda value=value: valid_digest(value, "hostile"))
        for value in (
            "", "Upper", "-leading", "trailing-", "double--dash",
            "with/slash", "with_under", "a" * 49, "a\x00b", None, 1,
        ):
            reject("reject-evidence-label-" + repr(value),
                   lambda value=value: checked_label(value))
        for value in (
            "", "/", "/tmp", "/tmp/", str(ROOT),
            "/tmp/rebar-phase2-native-build-v10-zig-synthetic",
            "/tmp/rebar-phase2-native-build-v7-zig-synthetic",
            "/tmp/" + PRIVATE_ROOT_PREFIX,
            "/tmp/" + PRIVATE_ROOT_PREFIX + "short",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "../escaped",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "bad.dot.value",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v10/extra",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v10/",
            None,
        ):
            reject("reject-private-root-" + repr(value),
                   lambda value=value: checked_workdir(value))
        for value in ("", "/tmp/escape", "../escape", "a/../b",
                      "a//b", "a/./b", "a\\b", "a\x00b", None):
            reject("reject-relative-owner-" + repr(value),
                   lambda value=value: checked_relative(value))
        for value in ("", "reference-c", "reference-a/..", "zig", None):
            reject("reject-cross-phase-" + repr(value),
                   lambda value=value: phase_paths(root, value))
        reject("reject-private-child-raw-string",
               lambda: checked_private_child(
                   str(phase_paths(root, "reference-a")["base"]),
                   root, "reference-a",
               ))
        reject("reject-private-child-root",
               lambda: checked_private_child(Path(root), root, "reference-a"))
        reject("reject-private-child-tmp-root",
               lambda: checked_private_child(Path("/tmp"), root, "reference-a"))
        reject("reject-private-child-cross-phase",
               lambda: checked_private_child(
                   phase_paths(root, "reference-b")["source"],
                   root, "reference-a",
               ))
        reject("reject-private-child-dotdot-escape",
               lambda: checked_private_child(
                   Path(root) / "reference-a" / ".." / "reference-b",
                   root, "reference-a",
               ))
        reject("reject-repeated-json-object-key",
               lambda: strict_json(b'{"x":1,"x":2}\n', "hostile"))
        reject("reject-noncanonical-json",
               lambda: strict_json(b'{ "x":1 }\n', "hostile"))
        reject("reject-json-nan",
               lambda: strict_json(b'{"x":NaN}\n', "hostile"))
        reject("reject-json-infinity",
               lambda: strict_json(b'{"x":Infinity}\n', "hostile"))
        reject("reject-json-array",
               lambda: strict_json(b'[]\n', "hostile"))
        reject("reject-truncated-json",
               lambda: strict_json(b'{"x":', "hostile"))
        reject("reject-unowned-command-role",
               lambda: checked_command(
                   "build_rust_engine", [PINNED_ZIG], root, "reference-a",
               ))
        reject("reject-shell-substitution",
               lambda: checked_command(
                   "build_zig_engine", ["/bin/sh", "-c", "zig build-lib"],
                   root, "reference-a",
               ))
        reject("reject-replaced-compiler",
               lambda: checked_command(
                   "build_zig_engine",
                   ["/usr/bin/zig"]
                   + planned_commands(root, "reference-a")[
                       "build_zig_engine"
                   ][1:],
                   root, "reference-a",
               ))
        reject("reject-cross-phase-compiler-argv",
               lambda: checked_command(
                   "build_zig_engine",
                   planned_commands(root, "reference-b")["build_zig_engine"],
                   root, "reference-a",
               ))
        reject("reject-truncated-compiler-argv",
               lambda: checked_command(
                   "build_zig_bridge",
                   planned_commands(root, "reference-a")[
                       "build_zig_bridge"
                   ][:-1],
                   root, "reference-a",
               ))
        reject("reject-mutated-compiler-argv",
               lambda: checked_command(
                   "build_zig_engine",
                   planned_commands(root, "reference-a")[
                       "build_zig_engine"
                   ] + ["--fetch"],
                   root, "reference-a",
               ))

        def mutated_native(role: str, mutation: Any) -> dict[str, Any]:
            value = strict_json(canonical(synthetic_native(role)), "synthetic ELF")
            mutation(value)
            return value

        reject("reject-external-engine-library",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["dynamic_tables"][0]["entries"].append(
                           {"tag": 1, "name": "libpcre2-8.so.0"}
                       )),
               ))
        reject("reject-wrong-engine-soname",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["dynamic_tables"][0]["entries"][1].update(
                           {"name": "_rust_engine.so"}
                       )),
               ))
        reject("reject-legacy-bridge-rpath",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["dynamic_tables"][0]["entries"].append(
                           {"tag": 15, "name": "/tmp/unowned"}
                       )),
               ))
        reject("reject-foreign-bridge-engine",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["dynamic_tables"][0]["entries"][0].update(
                           {"name": "_rust_engine.so"}
                       )),
               ))
        reject("reject-escaped-bridge-runpath",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["dynamic_tables"][0]["entries"][2].update(
                           {"name": "/tmp"}
                       )),
               ))
        reject("reject-stdlib-sre-symbol",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "_sre_compile", "section_index": 0}
                       )),
               ))
        reject("reject-external-pcre-symbol",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "pcre2_match", "section_index": 0}
                       )),
               ))
        reject("reject-cross-family-engine-symbol",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "rebar_rust_match", "section_index": 0}
                       )),
               ))
        reject("reject-dynamic-loader-symbol",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "dlopen", "section_index": 0}
                       )),
               ))
        reject("reject-python-module-import-symbol",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "PyImport_ImportModule", "section_index": 0}
                       )),
               ))
        reject("reject-missing-owned-engine-export",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].pop(0)
                   ),
               ))
        reject("reject-missing-owned-bridge-import",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].pop()
                   ),
               ))
        reject("reject-missing-module-initializer",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].pop(0)
                   ),
               ))
        reject("reject-substituted-unicode-helper",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "_PyUnicode_RegexMatch", "section_index": 0}
                       )),
               ))
        reject("reject-duplicate-dynamic-table",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["dynamic_tables"].append(
                           value["dynamic_tables"][0]
                       )),
               ))
        reject("reject-duplicate-symbol-table",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"].append(
                           value["symbol_tables"]["tables"][0]
                       )),
               ))
        reject("reject-truncated-process-schedule",
               lambda: validate_process_schedule(records[:-1], root))

        def mutate_records(mutation: Any) -> list[dict]:
            value = json.loads(canonical(records).decode("ascii"))
            mutation(value)
            return value

        reject("reject-repeated-process-pid",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[1].update({"pid": value[0]["pid"]})), root,
               ))
        reject("reject-swapped-process-order",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value.__setitem__(0, value[1])), root,
               ))
        reject("reject-contaminated-process-environment",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[0]["environment"].update(
                           {"HOME": "/tmp/unowned"}
                       )), root,
               ))
        reject("reject-signalled-process",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[0].update({"returncode": -11, "signal": 11})),
                   root,
               ))
        reject("reject-fabricated-stdout-digest",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[0]["stdout"].update({"sha256": "a" * 64})),
                   root,
               ))
        reject("reject-truncated-process-base64",
               lambda: decode_stream({
                   "bytes": 1,
                   "sha256": digest(b"x"),
                   "base64": "eA",
                   "complete": True,
               }))
        reject("reject-omitted-evidence-label",
               lambda: evidence_names("", False))

        def mutate_contract(mutation: Any) -> dict:
            value = strict_json(canonical(contract), "synthetic V10 contract")
            mutation(value)
            return value

        reject("reject-invented-actual-compiler-process",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["phase_boundary"].update(
                       {"compiler_processes_started": 1}
                   )), source_pin, protocol_pin))
        reject("reject-invented-actual-overlay-application",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["frozen_overlay"].update(
                       {"actual_source_apply_count": 1}
                   )), source_pin, protocol_pin))
        reject("reject-invented-native-output-hash",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["future_build_policy"]["native_outputs"][
                       "engine"
                   ].update({"sha256": "a" * 64})), source_pin, protocol_pin))
        reject("reject-weakened-case-denominator",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["oracle"].update({"case_execution_count": 31_236})),
                   source_pin, protocol_pin))
        reject("reject-hidden-original-zig-failure",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["published_v21_history"].update(
                       {"historical_zig_semantic_mismatch_count": 0}
                   )), source_pin, protocol_pin))
        reject("reject-changed-evidence-owner-denominator",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["published_v21_history"].update(
                       {"authoritative_counted_evidence_owner_count": 105}
                   )), source_pin, protocol_pin))
        reject("reject-hidden-new-c-failure-owners",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"].update(
                       {"authoritative_counted_evidence_owner_count": 103}
                   )), source_pin, protocol_pin))
        reject("reject-invented-c-matching-results",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"][
                       "recovered_c_failure"
                   ].update({"semantic_mismatch_count": 0})),
                   source_pin, protocol_pin))
        reject("reject-claimed-open-holdout",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["phase_boundary"].update(
                       {"holdout_opened": True}
                   )), source_pin, protocol_pin))
        reject("reject-claimed-performance-timing",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["phase_boundary"].update({"clock_samples": 1})),
                   source_pin, protocol_pin))

        probes: tuple[tuple[str, Any], ...] = (
            ("block-built-in-file-open",
             lambda: builtins.open("/tmp/rebar-v10-forbidden", "rb")),
            ("block-io-file-open",
             lambda: io.open("/tmp/rebar-v10-forbidden", "rb")),
            ("block-descriptor-open",
             lambda: os.open("/tmp", os.O_RDONLY)),
            ("block-descriptor-read", lambda: os.read(0, 1)),
            ("block-descriptor-write", lambda: os.write(1, b"x")),
            ("block-filesystem-stat", lambda: os.stat("/tmp")),
            ("block-filesystem-lstat", lambda: os.lstat("/tmp")),
            ("block-directory-creation",
             lambda: os.mkdir("/tmp/rebar-v10-forbidden")),
            ("block-filesystem-unlink",
             lambda: os.unlink("/tmp/rebar-v10-forbidden")),
            ("block-filesystem-replacement",
             lambda: os.replace("/tmp/a", "/tmp/b")),
            ("block-filesystem-sync", lambda: os.fsync(1)),
            ("block-path-source-read", lambda: Path("/tmp").read_bytes()),
            ("block-path-source-write",
             lambda: Path("/tmp/rebar-v10-forbidden").write_bytes(b"x")),
            ("block-path-resolution", lambda: Path("/tmp").resolve()),
            ("block-compiler-process",
             lambda: subprocess.Popen((PINNED_ZIG, "version"))),
            ("block-external-process",
             lambda: subprocess.run((PINNED_READELF, "--version"))),
            ("block-shell-process", lambda: os.system("true")),
            ("block-private-root-creation",
             lambda: tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX,
                                      dir="/tmp")),
            ("block-temporary-source", lambda: tempfile.mkstemp()),
            ("block-network-socket", lambda: socket.socket()),
            ("block-network-dns", lambda: socket.getaddrinfo("example.com", 443)),
            ("block-native-library-load", lambda: ctypes.CDLL(ENGINE_FILENAME)),
            ("block-native-python-library-load",
             lambda: ctypes.PyDLL(BRIDGE_FILENAME)),
            ("block-zig-candidate-import",
             lambda: importlib.import_module("candidates.zig_candidate")),
            ("block-cross-family-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("block-stdlib-regex-import",
             lambda: importlib.import_module("re")),
            ("block-candidate-thread", lambda: threading.Thread().start()),
            ("block-performance-clock", lambda: time.perf_counter()),
            ("block-performance-nanoclock", lambda: time.perf_counter_ns()),
            ("block-monotonic-clock", lambda: time.monotonic()),
            ("block-wall-clock", lambda: time.time()),
            ("block-wait", lambda: time.sleep(0)),
        )
        for name, operation in probes:
            reject(name, operation)
        blocked = dict(boundary.blocked)

    require(sum(blocked.values()) == len(probes),
            "every external-effect probe must be individually blocked")
    require(all(blocked[key] > 0 for key in (
        "filesystem", "process", "temporary", "network", "native",
        "candidate_import", "thread", "clock",
    )), "exercise every frozen source-only effect boundary")
    return {
        "schema": SCHEMA,
        "version": 10,
        "status": "PASS",
        "mode": "SOURCE-ONLY SYNTHETIC SELF-TEST",
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_effect_control_count": sum(blocked.values()),
        "blocked_effects_by_kind": blocked,
        "actual_synthetic_processes_started": 0,
        "synthetic_process_record_count": EXPECTED_PROCESS_COUNT,
        "actual_synthetic_private_roots_created": 0,
        "actual_synthetic_source_applications": 0,
        "workspace_mutations": 0,
        **expected_phase_boundary(),
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    selected = parser.parse_args(arguments)
    valid_digest(selected.source_sha256, "V10 source")
    valid_digest(selected.protocol_sha256, "V10 protocol")
    if selected.contract_sha256 is not None:
        valid_digest(selected.contract_sha256, "V10 contract")
    if selected.render_contract:
        require(selected.contract_sha256 is None and selected.label is None,
                "contract rendering is strictly read-only and has no build label")
    else:
        require(selected.contract_sha256 is not None,
                "independently pin the exact published V10 machine contract")
        if selected.build:
            require(selected.label is not None,
                    "a real native build requires one explicit fresh label")
            checked_label(selected.label)
        else:
            require(selected.label is None,
                    "a safe source-only gate cannot request a native build label")
    return selected


def main(arguments: list[str] | None = None) -> int:
    try:
        selected = parse_arguments(
            list(sys.argv[1:] if arguments is None else arguments)
        )
        if selected.self_test:
            result = self_test(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256,
            )
            exit_code = 0
        elif selected.verify_context:
            result, _retained = authenticate_context(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256,
            )
            exit_code = 0
        elif selected.render_contract:
            authenticate_context(selected.source_sha256,
                                 selected.protocol_sha256)
            result = contract_document(selected.source_sha256,
                                       selected.protocol_sha256)
            exit_code = 0
        else:
            exit_code, result = run_build(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256, selected.label,
            )
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return exit_code
    except (FreezeError, OSError, ValueError, TypeError, UnicodeError,
            OverflowError, RecursionError, subprocess.SubprocessError) as error:
        sys.stderr.write("OWNED ZIG SOURCE BUILD V10: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
