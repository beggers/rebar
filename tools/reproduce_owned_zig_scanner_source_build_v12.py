#!/usr/bin/env python3
"""Freeze and, only when explicitly requested, reproduce a first-party Zig build."""

from __future__ import annotations

import argparse
import builtins
import copy
import errno
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


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
PYTHON_INCLUDE = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
PINNED_ZIG = "/tmp/zig-x86_64-linux-0.16.0/zig"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
SCHEMA = "rebar-phase2-owned-zig-scanner-source-build-v12"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
SOURCE_PATH = "tools/reproduce_owned_zig_scanner_source_build_v12.py"
PROTOCOL_PATH = "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V12.md"
CONTRACT_PATH = "oracle/phase2/zig-scanner-source-build-v12.json"
EVIDENCE_DIRECTORY = "oracle/phase2/evidence"
PRIVATE_ROOT_PREFIX = "rebar-phase2-zig-scanner-capture-source-build-v2-"
PHASE_NAMES = ("reference-a", "reference-b")
ENGINE_FILENAME = "_zig_probe.so"
BRIDGE_FILENAME = "_zig_bridge.cpython-314-x86_64-linux-gnu.so"
CANONICAL_SOURCE_PREFIX = "/rebar-phase2-v6-owned-source"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_COMPILER_BYTES = 256 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
EXPECTED_PHASE_PROCESS_COUNT = 13
EXPECTED_PROCESS_COUNT = 26
FINAL_PLANNED_CASE_COUNT = 4_194_304
HISTORICAL_V31_EVIDENCE_OWNERS = 151
HISTORICAL_V31_HISTORY_REFERENCES = 156
CURRENT_EVIDENCE_OWNERS = 153
CURRENT_HISTORY_REFERENCES = 158
ORIGINAL_ENGINE = "candidates/zig/mini_regex.zig"
ORIGINAL_BRIDGE = "candidates/zig/py_bridge.c"
ORIGINAL_ADAPTER = "candidates/zig_candidate.py"
SOURCE_OWNERS = {
    ORIGINAL_ENGINE: (
        "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
        186915,
    ),
    ORIGINAL_BRIDGE: (
        "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
        173026,
    ),
    ORIGINAL_ADAPTER: (
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        68422,
    ),
}
V2_SOURCE = "tools/apply_owned_zig_scanner_capture_source_repair_v2.py"
V2_PROTOCOL = "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V2.md"
V2_CONTRACT = "oracle/phase2/zig-scanner-capture-source-repair-v2.json"
V11_SOURCE = "tools/reproduce_owned_zig_scanner_source_build_v11.py"
V11_PROTOCOL = "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md"
V11_CONTRACT = "oracle/phase2/zig-scanner-source-build-v11.json"
V7_SOURCE = "tools/reproduce_owned_native_source_build_v7.py"
V7_PROTOCOL = "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md"
V7_CONTRACT = "oracle/phase2/native-source-build-v7.json"
V31_SOURCE = "tools/render_candidate_current_overview_v31.py"
V31_INPUTS = "docs/evidence/candidate-current-overview-v31.inputs.json"
V31_SUMMARY = "docs/evidence/candidate-current-overview-v31.json"
V31_SVG = "docs/evidence/candidate-current-overview-v31.svg"
ADDITIVE_SOURCE = "tools/verify_python_re_callable_introspection_v1.py"
ADDITIVE_PROTOCOL = "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md"
ADDITIVE_CONTRACT = "oracle/phase1/p0-callable-introspection-v1.json"
RUST_BUILD_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz"
)
RUST_BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-"
    "publication-receipt.json"
)
RUST_MATCH_ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-"
    "original-p0-failures.json.gz"
)
RUST_MATCH_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-"
    "original-p0-failures-publication-receipt.json"
)
SUPPORT = {
    "GOAL.md": (
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3756,
    ),
    "oracle/phase1/p0-completeness-v1.json": (
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        45632,
    ),
    "oracle/phase1/P0-COMPLETENESS-V1.md": (
        "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
        10392,
    ),
    "tools/verify_p0_completeness_v1.py": (
        "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
        118040,
    ),
    "tools/run_owned_six_family_original_p0_producer_v3.py": (
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
        195555,
    ),
    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md": (
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
        5522,
    ),
    "oracle/phase2/six-family-p0-producer-v3.json": (
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
        26909,
    ),
    "toolchains/zig-0.16.0.lock.json": (
        "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
        628,
    ),
    V2_SOURCE: (
        "87a4cf8895b5d52c346213ef8277c17b66af44eba695bc37fac5198e0169b6ff",
        96716,
    ),
    V2_PROTOCOL: (
        "eb71f594968a497ddeef5aaf0ab9f221d46153be47e69402a1f0090fa6597879",
        6336,
    ),
    V2_CONTRACT: (
        "3afc80a62a50ee55d059b6a19fc74915ca0a8cbdeddd9efa723722b2629ee85e",
        11215,
    ),
    V11_SOURCE: (
        "b908f12d14fb8ebc5f17c62dfc00d48a1a5ee3717a3144aed437059e21c0f097",
        207444,
    ),
    V11_PROTOCOL: (
        "15fd222876407be72d36c0b9cf2ce581d8b73a954358df192c2a083a08973539",
        6144,
    ),
    V11_CONTRACT: (
        "92979e4bfacd6d23e7f54f4fdce7a7707cc54dba2512753029fdcd479150464c",
        44636,
    ),
    V7_SOURCE: (
        "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
        300624,
    ),
    V7_PROTOCOL: (
        "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
        8063,
    ),
    V7_CONTRACT: (
        "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
        28924,
    ),
    V31_SOURCE: (
        "daea5423d47bc84ec0ff503c14bae17ecdff392a60db14c5c66c575e978de588",
        75072,
    ),
    V31_INPUTS: (
        "25f1ef2cdf7f3443f5924b9c9814c4f0864148ebdf243c92a1df12d1c5754900",
        80376,
    ),
    V31_SUMMARY: (
        "6d6f8fa23022b9198255cd0836961d4f78cd2d4c5d4041734a82a1d9f9d2ec90",
        314023,
    ),
    V31_SVG: (
        "23f89b7983d5154d9275dcfa029bfe2a5599ad339c80675efb7c5eabda587d1a",
        12509,
    ),
    RUST_BUILD_ARCHIVE: (
        "840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d",
        108325,
    ),
    RUST_BUILD_RECEIPT: (
        "1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f",
        2109,
    ),
    RUST_MATCH_ARCHIVE: (
        "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f",
        3663299,
    ),
    RUST_MATCH_RECEIPT: (
        "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3",
        4674,
    ),
    ADDITIVE_SOURCE: (
        "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653",
        75608,
    ),
    ADDITIVE_PROTOCOL: (
        "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
        8952,
    ),
    ADDITIVE_CONTRACT: (
        "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
        14749,
    ),
}
TOOLCHAINS = {
    "zig": (PINNED_ZIG,
            "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
            172641672, True),
    "gcc": (PINNED_GCC,
            "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
            1023032, True),
    "readelf": (PINNED_READELF,
                "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
                789280, True),
    "python_header": (PYTHON_INCLUDE + "/Python.h",
                      "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
                      4399, False),
    "python_patchlevel": (PYTHON_INCLUDE + "/patchlevel.h",
                          "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
                          1773, False),
}
SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version",
    "build_zig_engine", "build_zig_bridge",
    "engine_dynamic", "engine_symbols", "engine_sections", "engine_notes",
    "bridge_dynamic", "bridge_symbols", "bridge_sections", "bridge_notes",
)


class BuildError(Exception):
    """The exact independently frozen first-party Zig build failed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise BuildError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def valid_digest(value: object, label: str) -> str:
    require(isinstance(value, str) and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "reject an invalid " + label + " SHA-256")
    return value


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError) as error:
        raise BuildError("require one finite canonical source-build document") from error


def strict_json(raw: bytes, label: str, *, canonical_required: bool = False) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        result: dict[str, object] = {}
        for key, value in pairs:
            require(key not in result, "reject duplicate JSON key in " + label)
            result[key] = value
        return result

    def nonfinite(_value: str) -> object:
        raise BuildError("reject nonfinite JSON number in " + label)

    try:
        result = json.loads(raw.decode("utf-8", "strict"),
                            object_pairs_hook=unique, parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise BuildError("reject malformed authenticated JSON: " + label) from error
    require(isinstance(result, dict), "require an object for " + label)
    if canonical_required:
        require(canonical(result) == raw,
                "reject noncanonical authenticated JSON: " + label)
    return result


def relative_parts(value: object, *, allow_rust_build_archive: bool = False) -> tuple[str, ...]:
    require(isinstance(allow_rust_build_archive, bool),
            "reject a nonboolean compressed Rust build policy")
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "require a bounded repository-relative source owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value
            and 0 < len(parsed.parts) <= 12
            and all(part not in ("", ".", "..")
                    and "\\" not in part and "\x00" not in part
                    for part in parsed.parts)
            and not value.endswith((".so", ".dylib", ".dll"))
            and (not value.endswith(".gz")
                 or (allow_rust_build_archive
                     and value in (RUST_BUILD_ARCHIVE, RUST_MATCH_ARCHIVE)))
            and (not allow_rust_build_archive
                 or value in (RUST_BUILD_ARCHIVE, RUST_MATCH_ARCHIVE))
            and "holdout" not in value.casefold()
            and "benchmark" not in value.casefold(),
            "reject a native target, hidden case, escaped path, or other archive")
    return parsed.parts


def checked_read(relative: str, fingerprint: str, size: int | None = None,
                 *, allow_rust_build_archive: bool = False) -> bytes:
    parts = relative_parts(relative,
                           allow_rust_build_archive=allow_rust_build_archive)
    valid_digest(fingerprint, relative)
    require(size is None or (isinstance(size, int)
                             and 0 <= size <= MAX_SOURCE_BYTES),
            "reject an oversized authenticated repository source owner")
    if allow_rust_build_archive:
        require(relative in (RUST_BUILD_ARCHIVE, RUST_MATCH_ARCHIVE)
                and (fingerprint, size) == SUPPORT[relative],
                "permit compressed bytes only from the two exact real Rust owners")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and 0 <= before.st_size <= MAX_SOURCE_BYTES
                    and (size is None or before.st_size == size)
                    and (not allow_rust_build_archive
                         or (before.st_dev == 2064
                             and before.st_ino
                             == (524643 if relative == RUST_BUILD_ARCHIVE else 524655)
                             and before.st_uid == os.geteuid()
                             and before.st_nlink == 1
                             and stat.S_IMODE(before.st_mode) == 0o600)),
                    "reject an altered or substituted authenticated source inode")
            chunks: list[bytes] = []
            total = 0
            while True:
                piece = os.read(descriptor, min(1024 * 1024,
                                                MAX_SOURCE_BYTES + 1 - total))
                if not piece:
                    break
                total += len(piece)
                require(total <= MAX_SOURCE_BYTES,
                        "bound the entire authenticated source-owner read")
                chunks.append(piece)
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns),
                    "reject an authenticated source changed during its read")
            raw = b"".join(chunks)
            require(len(raw) == before.st_size
                    and (size is None or len(raw) == size)
                    and digest(raw) == fingerprint,
                    "reject an incomplete or substituted source: " + relative)
            if allow_rust_build_archive:
                require(raw[:3] == b"\x1f\x8b\x08"
                        and int.from_bytes(raw[-4:], "little")
                        == (757826 if relative == RUST_BUILD_ARCHIVE else 5280314),
                        "authenticate exact compressed Rust bytes without inflation")
            return raw
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def read_external(path: str, fingerprint: str, size: int,
                  executable: bool) -> dict:
    require(isinstance(path, str) and PurePosixPath(path).is_absolute()
            and valid_digest(fingerprint, "external toolchain") == fingerprint
            and isinstance(size, int) and 0 < size <= MAX_COMPILER_BYTES
            and isinstance(executable, bool),
            "reject an invalid pinned offline toolchain owner")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_size == size
                and (not executable or before.st_mode & stat.S_IXUSR != 0),
                "reject a missing, substituted, or nonexecutable offline tool")
        hasher = hashlib.sha256()
        count = 0
        while True:
            piece = os.read(descriptor, 1024 * 1024)
            if not piece:
                break
            count += len(piece)
            require(count <= size, "reject an oversized pinned offline tool")
            hasher.update(piece)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and count == size and hasher.hexdigest() == fingerprint,
                "reject offline compiler or header substitution")
        return {"path": path, "sha256": fingerprint,
                "bytes": size, "executable": executable}
    finally:
        os.close(descriptor)


def checked_label(value: object) -> str:
    require(isinstance(value, str) and 0 < len(value) <= 48
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for char in value)
            and "--" not in value and not value.endswith("-"),
            "require a bounded, lowercase, fresh V12 evidence label")
    return value


def checked_workdir(value: object) -> str:
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "require one exact fresh private Zig V2 build root")
    parsed = PurePosixPath(value)
    require(parsed.is_absolute() and str(parsed) == value,
            "reject a noncanonical private Zig V2 build root")
    parts = parsed.parts
    require(len(parts) == 3 and parts[1] == "tmp"
            and parts[2].startswith(PRIVATE_ROOT_PREFIX),
            "never reuse a V1, workspace, broad, or cross-family phase root")
    suffix = parts[2][len(PRIVATE_ROOT_PREFIX):]
    require(len(suffix) >= 8
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in suffix),
            "reject an unsafe, predictable, or malformed private phase suffix")
    return value


def phase_paths(workdir: str, phase: str) -> dict[str, Path]:
    root = Path(checked_workdir(workdir))
    require(isinstance(phase, str) and phase in PHASE_NAMES,
            "require exactly one of two genuinely independent Zig phases")
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
        "source_adapter": source / ORIGINAL_ADAPTER,
        "source_engine": source / ORIGINAL_ENGINE,
        "source_bridge": source / ORIGINAL_BRIDGE,
        "artifact_engine": native / ENGINE_FILENAME,
        "artifact_bridge": native / BRIDGE_FILENAME,
    }


def prefix_flags(workdir: str) -> list[str]:
    root = checked_workdir(workdir)
    return ["-ffile-prefix-map="
            + str(phase_paths(root, phase)["source"])
            + "=" + CANONICAL_SOURCE_PREFIX
            for phase in PHASE_NAMES]


def build_environment(workdir: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, phase)
    return {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
        "ZIG_LOCAL_CACHE_DIR": str(paths["zig_local_cache"]),
        "ZIG_GLOBAL_CACHE_DIR": str(paths["zig_global_cache"]),
    }


def planned_commands(workdir: str, phase: str) -> dict[str, list[str]]:
    paths = phase_paths(workdir, phase)
    result = {
        "readelf_version": [PINNED_READELF, "--version"],
        "gcc_version": [PINNED_GCC, "--version"],
        "zig_version": [PINNED_ZIG, "version"],
        "build_zig_engine": [
            PINNED_ZIG, "build-lib", str(paths["source_engine"]),
            "-dynamic", "-lc", "-O", "ReleaseFast", "-fstrip",
            "-fallow-shlib-undefined", "-fsoname=" + ENGINE_FILENAME,
            "--cache-dir", str(paths["zig_local_cache"]),
            "--global-cache-dir", str(paths["zig_global_cache"]),
            "-femit-bin=" + str(paths["artifact_engine"]),
        ],
        "build_zig_bridge": [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=sha1",
            *prefix_flags(workdir), "-I" + PYTHON_INCLUDE,
            str(paths["source_bridge"]), "-L" + str(paths["native"]),
            "-l:" + ENGINE_FILENAME, "-Wl,-rpath,$ORIGIN",
            "-o", str(paths["artifact_bridge"]),
        ],
    }
    for role in ("engine", "bridge"):
        target = str(paths["artifact_" + role])
        result[role + "_dynamic"] = [PINNED_READELF, "--dynamic", "--wide", target]
        result[role + "_symbols"] = [PINNED_READELF, "--dyn-syms", "--wide", target]
        result[role + "_sections"] = [PINNED_READELF, "--sections", "--wide", target]
        result[role + "_notes"] = [PINNED_READELF, "--notes", "--wide", target]
    require(tuple(result) == PROCESS_ROLES
            and len(result) == EXPECTED_PHASE_PROCESS_COUNT,
            "freeze exactly thirteen independently pinned V12 phase processes")
    return result


def checked_command(name: object, argv: object,
                    workdir: str, phase: str) -> list[str]:
    planned = planned_commands(workdir, phase)
    require(isinstance(name, str) and name in planned
            and isinstance(argv, list)
            and all(isinstance(part, str) and "\x00" not in part for part in argv)
            and argv == planned[name]
            and argv[0] in (PINNED_ZIG, PINNED_GCC, PINNED_READELF),
            "reject an unpinned, networked, shell, or cross-phase build process")
    return list(argv)


def sanitized(value: object, workdir: str) -> object:
    root = checked_workdir(workdir)
    if isinstance(value, str):
        return value.replace(root, "<FRESH_PRIVATE_ROOT>")
    if isinstance(value, list):
        return [sanitized(item, root) for item in value]
    if isinstance(value, dict):
        return {key: sanitized(item, root) for key, item in value.items()}
    return value


def command_templates() -> list[dict]:
    root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v12-freeze"
    result = []
    for phase in PHASE_NAMES:
        result.append({
            "phase": phase,
            "working_directory": sanitized(str(phase_paths(root, phase)["base"]), root),
            "environment": sanitized(build_environment(root, phase), root),
            "commands": [
                {"name": role, "argv": sanitized(argv, root)}
                for role, argv in planned_commands(root, phase).items()
            ],
        })
    return result


def expected_boundary() -> dict:
    return {
        "actual_build_process_count": 0,
        "actual_source_apply_count": 0,
        "compiler_processes_started": 0,
        "native_builds_started": 0,
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
        "compressed_build_archive_raw_bytes_read": 108325,
        "compressed_matching_failure_archive_files_opened": 1,
        "compressed_matching_failure_archive_raw_bytes_read": 3663299,
        "decompressed_archive_bytes_read": 0,
        "gzip_inflation_count": 0,
        "qualified_candidate_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": FINAL_PLANNED_CASE_COUNT,
        "final_comparison_cases_generated": False,
        "holdout": "NOT OPENED",
        "holdout_opened": False,
        "winner_selected": False,
    }


def owner_document(path: str, pin: tuple[str, int]) -> dict:
    relative_parts(
        path, allow_rust_build_archive=path in (RUST_BUILD_ARCHIVE, RUST_MATCH_ARCHIVE),
    )
    fingerprint, count = pin
    valid_digest(fingerprint, path)
    require(isinstance(count, int) and 0 <= count <= MAX_SOURCE_BYTES,
            "reject an unbounded frozen support owner")
    return {"path": path, "sha256": fingerprint, "bytes": count}


def contract_document(source_pin: str, protocol_pin: str) -> dict:
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 12,
        "status": "SOURCE FROZEN; CORRECTED ZIG BUILD NOT RUN",
        "phase": "CORRECTED FIRST-PARTY ZIG SCANNER SOURCE BUILD; NO BUILD EXECUTED",
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "oracle": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PYTHON, "executable_sha256": PYTHON_SHA256,
            "manifest_path": "oracle/phase1/p0-completeness-v1.json",
            "manifest_sha256": SUPPORT["oracle/phase1/p0-completeness-v1.json"][0],
            "suite_count": 13, "suite_ids": list(SUITE_IDS),
            "case_execution_count": 31237, "private_waiver_count": 13,
            "denominator_modified": False,
        },
        "additive_callable_introspection": {
            "source": owner_document(ADDITIVE_SOURCE, SUPPORT[ADDITIVE_SOURCE]),
            "protocol": owner_document(ADDITIVE_PROTOCOL, SUPPORT[ADDITIVE_PROTOCOL]),
            "contract": owner_document(ADDITIVE_CONTRACT, SUPPORT[ADDITIVE_CONTRACT]),
            "additive_case_count": 50,
            "original_core_case_execution_count": 31237,
            "reference_status": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_workers_started": 0,
            "included_in_original_denominator": False,
        },
        "published_history": {
            "historical_overview_version": 31,
            "overview_source": owner_document(V31_SOURCE, SUPPORT[V31_SOURCE]),
            "overview_inputs": owner_document(V31_INPUTS, SUPPORT[V31_INPUTS]),
            "overview_summary": owner_document(V31_SUMMARY, SUPPORT[V31_SUMMARY]),
            "overview_svg": owner_document(V31_SVG, SUPPORT[V31_SVG]),
            "historical_v30_evidence_owner_count": 149,
            "historical_v30_authenticated_reference_count": 154,
            "historical_v31_evidence_owner_count": HISTORICAL_V31_EVIDENCE_OWNERS,
            "historical_v31_authenticated_reference_count":
                HISTORICAL_V31_HISTORY_REFERENCES,
            "historical_rust_v12_build_evidence_owner_count": 2,
            "new_actual_rust_v4_matching_evidence_owner_count": 2,
            "authoritative_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
            "authenticated_reference_count": CURRENT_HISTORY_REFERENCES,
            "oracle_evidence_reference_count": 128,
            "experiment_evidence_reference_count": 30,
            "new_zig_v12_evidence_owner_count": 0,
            "candidate_qualified_count": 0,
        },
        "actual_rust_v12_source_build": {
            "build_status": "PASS",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "actual_compiler_process_count": 28,
            "archive": owner_document(RUST_BUILD_ARCHIVE,
                                       SUPPORT[RUST_BUILD_ARCHIVE]),
            "receipt": owner_document(RUST_BUILD_RECEIPT,
                                       SUPPORT[RUST_BUILD_RECEIPT]),
            "archive_decompressed": False,
            "historical_tested_rust_semantic_mismatch_count": 1087,
        },
        "actual_rust_v4_matching_campaign": {
            "status": "FAIL",
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_qualified": False,
            "family": "rust",
            "label": "phase2-v12-rust-flag-original-p0",
            "suite_count": 13,
            "completed_suite_count": 13,
            "case_execution_denominator": 31237,
            "private_waiver_count": 13,
            "actual_candidate_workers": 13,
            "semantic_mismatch_count": 1036,
            "verified_passing_case_count": 8965,
            "infrastructure_failure_count": 0,
            "historical_rust_semantic_mismatch_count": 1087,
            "historical_rust_verified_passing_case_count": 7438,
            "historical_v31_evidence_owner_count": 151,
            "historical_v31_authenticated_reference_count": 156,
            "new_repository_evidence_owner_count": 2,
            "resulting_repository_evidence_owner_count": 153,
            "resulting_authenticated_reference_count": 158,
            "archive": owner_document(RUST_MATCH_ARCHIVE,
                                       SUPPORT[RUST_MATCH_ARCHIVE]),
            "receipt": owner_document(RUST_MATCH_RECEIPT,
                                       SUPPORT[RUST_MATCH_RECEIPT]),
            "compressed_archive_raw_bytes_read": 3663299,
            "decompressed_archive_bytes_read": 0,
            "gzip_inflation_count": 0,
            "recovery_journal_sha256":
                "726e81e5d2ee255e1f46d3029290ae9486fbd23711c9a45a691d091d088f3278",
            "all_four_original_targets_restored": True,
            "matching_passed": False,
        },
        "preserved_matching_results": {
            "zig_status": "FAIL",
            "zig_semantic_mismatch_count": 2172,
            "zig_verified_passing_case_count": 2847,
            "zig_candidate_worker_count": 13,
            "zig_completed_suite_count": 13,
            "zig_infrastructure_failure_count": 0,
            "historical_first_zig_candidate_worker_count": 0,
            "historical_first_zig_matching_case_executions": 0,
            "rust_status": "FAIL",
            "rust_semantic_mismatch_count": 1036,
            "rust_verified_passing_case_count": 8965,
            "rust_candidate_worker_count": 13,
            "rust_completed_suite_count": 13,
            "rust_infrastructure_failure_count": 0,
            "historical_rust_semantic_mismatch_count": 1087,
            "historical_rust_verified_passing_case_count": 7438,
            "c_status": "FAIL",
            "c_semantic_mismatch_count": 1230,
            "c_verified_passing_case_count": 7325,
            "qualified_candidate_count": 0,
            "corrected_zig_build_status": "NOT RUN",
            "corrected_zig_candidate_correctness": "NOT MEASURED",
        },
        "first_party_ownership": {
            "independent_engine_family_count": 6,
            "first_party_semantic_source_owner_count": 25,
            "zig_source_owner_count": 3,
            "zig_sources": [
                owner_document(path, pin)
                for path, pin in sorted(SOURCE_OWNERS.items())
            ],
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_delegation": "FORBIDDEN",
            "cross_family_matching_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
        },
        "corrected_v2_overlay": {
            "schema": "rebar-phase2-owned-zig-scanner-capture-source-repair-v2",
            "source": owner_document(V2_SOURCE, SUPPORT[V2_SOURCE]),
            "protocol": owner_document(V2_PROTOCOL, SUPPORT[V2_PROTOCOL]),
            "contract": owner_document(V2_CONTRACT, SUPPORT[V2_CONTRACT]),
            "derived_bridge_sha256": SOURCE_OWNERS[ORIGINAL_BRIDGE][0],
            "derived_bridge_bytes": SOURCE_OWNERS[ORIGINAL_BRIDGE][1],
            "byte_identical_to_canonical_original": True,
            "v1_conditional_overlay_used": False,
            "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
            "phase_names": list(PHASE_NAMES),
            "both_phase_trees_created_before_first_apply": True,
            "expected_source_apply_count_only_after_build": 2,
            "actual_source_apply_count": 0,
            "private_directory_mode": "0700",
            "private_source_mode": "0600",
            "source_write_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
        },
        "preserved_v11_low_level_build_mechanism": {
            "source": owner_document(V11_SOURCE, SUPPORT[V11_SOURCE]),
            "protocol": owner_document(V11_PROTOCOL, SUPPORT[V11_PROTOCOL]),
            "contract": owner_document(V11_CONTRACT, SUPPORT[V11_CONTRACT]),
            "v11_source_mutated": False,
            "v11_run_build_invoked": False,
            "v11_overlay_invoked": False,
            "v11_history_used_as_current": False,
            "preserved_process_role_count_per_phase": EXPECTED_PHASE_PROCESS_COUNT,
        },
        "preserved_v7_raw_elf_audit": {
            "source": owner_document(V7_SOURCE, SUPPORT[V7_SOURCE]),
            "protocol": owner_document(V7_PROTOCOL, SUPPORT[V7_PROTOCOL]),
            "contract": owner_document(V7_CONTRACT, SUPPORT[V7_CONTRACT]),
            "parser": "AUTHENTICATED FIRST-PARTY parse_owned_elf64",
            "comparator": "AUTHENTICATED FIRST-PARTY compare_owned_elf64",
            "foreign_matcher_symbols": "FORBIDDEN",
        },
        "toolchains": [
            {"id": role, "path": pin[0], "sha256": pin[1],
             "bytes": pin[2], "executable": pin[3]}
            for role, pin in sorted(TOOLCHAINS.items())
        ],
        "official_zig_lock": owner_document(
            "toolchains/zig-0.16.0.lock.json",
            SUPPORT["toolchains/zig-0.16.0.lock.json"],
        ),
        "future_build_policy": {
            "authorization": "EXPLICIT --build AFTER SOURCE FREEZE COMMIT",
            "actual_status": "NOT RUN",
            "actual_process_count": 0,
            "actual_source_apply_count": 0,
            "expected_phase_count_only_after_success": 2,
            "expected_process_count_per_completed_phase": EXPECTED_PHASE_PROCESS_COUNT,
            "expected_total_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
            "phase_names": list(PHASE_NAMES),
            "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
            "private_directory_mode": "0700",
            "private_source_mode": "0600",
            "distinct_phase_sources": True,
            "distinct_phase_caches": True,
            "distinct_phase_output_inodes": True,
            "offline": True,
            "shell": False,
            "network": "FORBIDDEN",
            "command_role_order": list(PROCESS_ROLES),
            "frozen_command_templates": command_templates(),
            "engine_soname": ENGINE_FILENAME,
            "bridge_needed_engine": ENGINE_FILENAME,
            "bridge_runpath": "$ORIGIN",
            "raw_elf_audit": "REQUIRED BEFORE REPRODUCIBILITY CLASSIFICATION",
            "both_native_roles_byte_identical": "NOT MEASURED",
            "external_regex_engine": "FORBIDDEN",
            "cross_family_matching_dependency": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "candidate_correctness": "NOT MEASURED",
        },
        "future_publication_policy": {
            "actual_publications": 0,
            "successful_archive_pattern":
                "native-source-build-v12-zig-LABEL.json.gz",
            "failed_archive_pattern":
                "native-source-build-v12-zig-LABEL-failures.json.gz",
            "distinct_receipt_required": True,
            "preserve_build_failures": True,
            "source_evidence_owner_count_before_publication": CURRENT_EVIDENCE_OWNERS,
            "source_authenticated_reference_count_before_publication":
                CURRENT_HISTORY_REFERENCES,
            "new_actual_owners_only_after_publication": 2,
            "candidate_correctness": "NOT MEASURED",
        },
        "phase_boundary": expected_boundary(),
        "pinned_support": [owner_document(path, pin)
                            for path, pin in sorted(SUPPORT.items())],
    }


def validate_v31(inputs: dict, summary: dict) -> None:
    require(inputs.get("schema") == "rebar-candidate-current-overview-v31-inputs"
            and inputs.get("version") == 31
            and inputs.get("repository_evidence_owner_count") == 151
            and inputs.get("all_digest_addressed_history_path_count") == 156
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("suite_count") == 13
            and inputs.get("full_case_denominator") == 31237
            and inputs.get("private_waiver_count") == 13
            and inputs.get("actual_zig_candidate_workers") == 13
            and inputs.get("actual_zig_semantic_mismatch_count") == 2172
            and inputs.get("actual_rust_candidate_workers") == 13
            and inputs.get("actual_rust_semantic_mismatch_count") == 1087
            and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
            and inputs.get("rust_v12_build_status") == "PASS"
            and inputs.get("rust_v12_candidate_correctness") == "NOT MEASURED"
            and inputs.get("rust_v12_matching_test_status") == "NOT MEASURED"
            and inputs.get("rust_v12_actual_candidate_workers") == 0
            and inputs.get("rust_v12_actual_compiler_process_count") == 28
            and inputs.get("rust_v12_candidate_qualified") is False
            and inputs.get("rust_v12_independent_phase_count") == 2
            and inputs.get("preserved_v30_repository_evidence_owner_count") == 149
            and inputs.get("preserved_v30_digest_addressed_history_path_count") == 154
            and inputs.get("new_rust_v12_source_build_repository_evidence_owner_count") == 2,
            "retain the exact current V31 151/156 and real untested Rust build")
    require(summary.get("schema") == "rebar-candidate-current-overview-v31-summary"
            and summary.get("status") == "PASS"
            and summary.get("repository_evidence_owner_count") == 151
            and summary.get("authenticated_digest_addressed_history_paths") == 156
            and summary.get("qualified_candidate_count") == 0
            and summary.get("suite_count") == 13
            and summary.get("full_case_denominator") == 31237
            and summary.get("private_waiver_count") == 13
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
            and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
            and summary.get("zig_original_campaign_candidate_worker_count") == 13
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087
            and summary.get("rust_original_campaign_verified_passing_case_count") == 7438
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7325
            and summary.get("rust_v12_source_build_status") == "PASS"
            and summary.get("rust_v12_source_build_candidate_correctness")
            == "NOT MEASURED"
            and summary.get("rust_v12_source_build_matching_test_status")
            == "NOT MEASURED",
            "never turn the prior Zig, Rust, or C matching failures into successes")
    snapshot = summary.get("snapshot")
    require(isinstance(snapshot, dict)
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 151
            and snapshot.get("all_digest_addressed_history_path_count") == 156
            and snapshot.get("current_source_owner_count") == 25
            and snapshot.get("frozen_independent_engine_family_count") == 6
            and snapshot.get("qualified_candidate_count") == 0
            and snapshot.get("full_case_denominator") == 31237
            and snapshot.get("suite_count") == 13
            and snapshot.get("baseline_passed") == 31237
            and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS
            and snapshot.get("zig_v2_original_campaign_status") == "FAIL"
            and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count") == 2172
            and snapshot.get("zig_v2_original_campaign_verified_passing_case_count") == 2847
            and snapshot.get("zig_v2_original_campaign_actual_candidate_workers") == 13
            and snapshot.get("zig_v2_original_campaign_completed_suite_count") == 13
            and snapshot.get("zig_v2_original_campaign_infrastructure_failure_count") == 0
            and snapshot.get("rust_v3_original_campaign_semantic_mismatch_count") == 1087
            and snapshot.get("c_v4_original_campaign_semantic_mismatch_count") == 1230
            and snapshot.get("rust_v12_source_build_status") == "PASS"
            and snapshot.get("rust_v12_source_build_candidate_correctness") == "NOT MEASURED"
            and snapshot.get("rust_v12_source_build_matching_test_status") == "NOT MEASURED"
            and snapshot.get("rust_v12_source_build_process_count") == 28
            and snapshot.get("rust_v12_source_build_independent_phase_count") == 2
            and snapshot.get("rust_v12_source_build_candidate_qualified") is False,
            "preserve all actual current first-party source and matching evidence")
    rust = inputs.get("actual_rust_v12_corrected_source_build")
    require(isinstance(rust, dict)
            and rust.get("status") == "PASS"
            and rust.get("build_status") == "PASS"
            and rust.get("candidate_correctness") == "NOT MEASURED"
            and rust.get("candidate_qualified") is False
            and rust.get("actual_compiler_process_count") == 28,
            "require a genuine Rust source-build PASS, not a compatibility result")
    for role, path in (("archive", RUST_BUILD_ARCHIVE),
                       ("receipt", RUST_BUILD_RECEIPT)):
        owner = rust.get(role)
        require(isinstance(owner, dict)
                and owner.get("path") == path
                and owner.get("sha256") == SUPPORT[path][0]
                and owner.get("bytes") == SUPPORT[path][1]
                and owner.get("device") == 2064
                and owner.get("inode") == (524643 if role == "archive" else 524644)
                and owner.get("mode") == "0600"
                and owner.get("nlink") == 1,
                "bind each genuinely published Rust archive and distinct receipt")
    for document in (inputs, summary, snapshot):
        require(document.get("final_comparison_planned_case_count")
                == FINAL_PLANNED_CASE_COUNT
                and document.get("final_comparison_cases_generated") is False
                and document.get("final_holdout_opened") is False
                and document.get("performance") == "NOT MEASURED"
                and document.get("memory") == "NOT MEASURED",
                "reject invented speed, changed holdout, or memory claims")
    require(summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False,
            "reject candidate execution, clocks, hidden cases, or a winner")


def validate_additive(value: dict) -> None:
    obligation, original = value.get("additional_obligation"), value.get("original_correctness")
    boundary = value.get("phase_boundary")
    require(value.get("schema") == "rebar-python-re-callable-introspection-v1-source-freeze"
            and value.get("version") == 1
            and value.get("status")
            == "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN"
            and isinstance(obligation, dict)
            and obligation.get("case_count") == 50
            and isinstance(obligation.get("case_matrix"), list)
            and len(obligation["case_matrix"]) == 50
            and isinstance(original, dict)
            and original.get("case_execution_denominator") == 31237
            and original.get("suite_count") == 13
            and original.get("private_waiver_count") == 13
            and original.get("denominator_modified") is False
            and isinstance(boundary, dict)
            and boundary.get("introspection_reference") == "NOT RUN"
            and boundary.get("candidate_introspection") == "NOT MEASURED"
            and boundary.get("actual_reference_roles_started") == 0
            and boundary.get("actual_candidate_workers_started") == 0
            and boundary.get("actual_source_builds") == 0
            and boundary.get("actual_holdout_cases_read") == 0
            and boundary.get("actual_clock_samples") == 0
            and boundary.get("holdout") == "NOT OPENED"
            and boundary.get("candidate_qualified") is False
            and boundary.get("performance") == "NOT MEASURED"
            and boundary.get("memory") == "NOT MEASURED"
            and boundary.get("winner_selected") is False,
            "keep the 50 additive cases unrun and outside the frozen 31,237 core")


def validate_v11_policy(value: dict) -> None:
    future, overlay = value.get("future_build_policy"), value.get("frozen_overlay")
    require(value.get("schema")
            == "rebar-phase2-owned-zig-scanner-source-build-v11-source-freeze"
            and value.get("version") == 11
            and isinstance(future, dict)
            and future.get("actual_status") == "NOT RUN"
            and future.get("actual_process_count") == 0
            and future.get("expected_phase_count_only_after_success") == 2
            and future.get("expected_process_count_per_completed_phase") == 13
            and future.get("expected_total_process_count_only_after_success") == 26
            and tuple(future.get("command_role_order", ())) == PROCESS_ROLES
            and future.get("engine_soname") == ENGINE_FILENAME
            and future.get("bridge_needed_engine") == ENGINE_FILENAME
            and future.get("bridge_runpath") == "$ORIGIN"
            and future.get("external_regex_engine") == "FORBIDDEN"
            and future.get("cross_family_matching_dependency") == "FORBIDDEN"
            and future.get("fallback") == "FORBIDDEN"
            and isinstance(overlay, dict)
            and overlay.get("schema")
            == "rebar-phase2-owned-zig-scanner-capture-source-repair-v1"
            and overlay.get("derived_bridge_sha256")
            == "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148",
            "preserve V11 build mechanics while explicitly rejecting its old V1 repair")


def validate_rust_matching(receipt: dict, history: dict[str, str]) -> dict[str, str]:
    require(isinstance(history, dict)
            and len(history) == HISTORICAL_V31_HISTORY_REFERENCES
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 126
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "retain all 156 independently authenticated historical V31 references")
    require(isinstance(receipt, dict)
            and receipt.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("candidate_qualified") is False
            and receipt.get("family") == "rust"
            and receipt.get("label") == "phase2-v12-rust-flag-original-p0"
            and receipt.get("suite_count") == 13
            and receipt.get("completed_suite_count") == 13
            and receipt.get("case_execution_denominator") == 31237
            and receipt.get("named_private_waiver_count") == 13
            and receipt.get("actual_candidate_workers") == 13
            and receipt.get("semantic_mismatch_count") == 1036
            and receipt.get("verified_passing_case_count") == 8965
            and receipt.get("infrastructure_failure_count") == 0
            and receipt.get("historical_evidence_owner_count_before_publication")
            == HISTORICAL_V31_EVIDENCE_OWNERS
            and receipt.get("historical_authenticated_reference_count_before_publication")
            == HISTORICAL_V31_HISTORY_REFERENCES
            and receipt.get("new_repository_evidence_owner_count") == 2
            and receipt.get("resulting_repository_evidence_owner_count")
            == CURRENT_EVIDENCE_OWNERS
            and receipt.get("resulting_authenticated_reference_count")
            == CURRENT_HISTORY_REFERENCES
            and receipt.get("uncompressed_bytes") == 5280314
            and receipt.get("uncompressed_sha256")
            == "a7b2dfbe5d1a8ddf8b1c3de48c24085d43260084c4a48e4a8394f1cc5b66600b"
            and receipt.get("recovery_journal_sha256")
            == "726e81e5d2ee255e1f46d3029290ae9486fbd23711c9a45a691d091d088f3278"
            and receipt.get("actual_v12_build_archive_sha256")
            == SUPPORT[RUST_BUILD_ARCHIVE][0]
            and receipt.get("actual_v12_build_receipt_sha256")
            == SUPPORT[RUST_BUILD_RECEIPT][0]
            and receipt.get("corrected_public_adapter_sha256")
            == "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
            and receipt.get("corrected_bridge_source_sha256")
            == "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257",
            "retain all 13 genuine corrected Rust failures and current 153/158 history")
    archive = receipt.get("archive")
    require(isinstance(archive, dict)
            and archive.get("path") == str(ROOT / RUST_MATCH_ARCHIVE)
            and archive.get("relative") == RUST_MATCH_ARCHIVE.rsplit("/", 1)[-1]
            and archive.get("sha256") == SUPPORT[RUST_MATCH_ARCHIVE][0]
            and archive.get("size_bytes") == SUPPORT[RUST_MATCH_ARCHIVE][1]
            and archive.get("device") == 2064
            and archive.get("inode") == 524655
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("streaming_readback_verified") is True
            and isinstance(archive.get("write_calls"), int)
            and archive["write_calls"] > 0,
            "bind the exact compressed restored Rust failure without inflating it")
    require(receipt.get("all_four_original_targets_restored") is True
            and receipt.get("restoration_verified_before_publication") is True
            and receipt.get("v2_unsafe_activation_invoked") is False
            and receipt.get("v2_unsafe_controller_invoked") is False
            and receipt.get("v7_zig_only_activation_invoked") is False
            and receipt.get("v9_c_only_runner_invoked") is False
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("benchmark_files_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("winner_selected") is False,
            "reject unsafe activation, missing restoration, hidden timing, or winner")
    additions = {
        RUST_MATCH_ARCHIVE: SUPPORT[RUST_MATCH_ARCHIVE][0],
        RUST_MATCH_RECEIPT: SUPPORT[RUST_MATCH_RECEIPT][0],
    }
    require(len(additions) == 2 and not (set(additions) & set(history)),
            "never double-count or omit the two real current Rust failure owners")
    current = dict(history)
    current.update(additions)
    require(len(current) == CURRENT_HISTORY_REFERENCES
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in current) == 128
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in current) == 30,
            "derive exactly 158 digest-addressed current references")
    return current


def load_module(name: str, relative: str, raw: bytes) -> types.ModuleType:
    require(isinstance(name, str) and name.startswith("_rebar_owned_zig_v12_")
            and isinstance(raw, bytes)
            and relative in (V2_SOURCE, V11_SOURCE, V7_SOURCE)
            and digest(raw) == SUPPORT[relative][0]
            and len(raw) == SUPPORT[relative][1],
            "execute only an exact authenticated first-party source module")
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None,
                   *, retain: bool = False) -> tuple[dict, dict]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "run only under isolated independently pinned CPython 3.14.6")
    own = checked_read(SOURCE_PATH, valid_digest(source_pin, "Zig V12 source"))
    protocol = checked_read(PROTOCOL_PATH,
                            valid_digest(protocol_pin, "Zig V12 protocol"))
    protected = {
        path: checked_read(path, pin[0], pin[1],
                           allow_rust_build_archive=
                           path in (RUST_BUILD_ARCHIVE, RUST_MATCH_ARCHIVE))
        for path, pin in SUPPORT.items()
    }
    originals = {
        path: checked_read(path, pin[0], pin[1])
        for path, pin in SOURCE_OWNERS.items()
    }
    v2 = load_module("_rebar_owned_zig_v12_corrected_v2_overlay",
                     V2_SOURCE, protected[V2_SOURCE])
    require(v2.SCHEMA == "rebar-phase2-owned-zig-scanner-capture-source-repair-v2"
            and v2.PRIVATE_ROOT_PREFIX == PRIVATE_ROOT_PREFIX
            and v2.CORRECTED_SHA256 == SOURCE_OWNERS[ORIGINAL_BRIDGE][0]
            and v2.CORRECTED_BYTES == SOURCE_OWNERS[ORIGINAL_BRIDGE][1],
            "load only the exact genuine V2 canonical scanner correction")
    corrected_contract, derived = v2.verify_context(
        SUPPORT[V2_SOURCE][0], SUPPORT[V2_PROTOCOL][0], SUPPORT[V2_CONTRACT][0],
    )
    require(derived == originals[ORIGINAL_BRIDGE]
            and corrected_contract.get("version") == 2
            and corrected_contract.get("published_history", {}).get(
                "authoritative_counted_evidence_owner_count")
            == HISTORICAL_V31_EVIDENCE_OWNERS
            and corrected_contract.get("published_history", {}).get(
                "authenticated_digest_addressed_history_paths")
            == HISTORICAL_V31_HISTORY_REFERENCES,
            "derive exact canonical 173,026-byte bridge from frozen V2, never V1")

    p0 = strict_json(protected["oracle/phase1/p0-completeness-v1.json"],
                     "original frozen CPython correctness oracle")
    denominator, runtime = p0.get("denominator"), p0.get("runtime")
    gate = p0.get("phase_gate")
    require(p0.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and p0.get("version") == 1
            and isinstance(denominator, dict)
            and tuple(denominator.get("counted_suite_ids", ())) == SUITE_IDS
            and denominator.get("final_required_case_execution_denominator") == 31237
            and denominator.get("private_upstream_methods_outside_public_denominator") == 13
            and isinstance(runtime, dict)
            and runtime.get("python_implementation") == "CPython"
            and runtime.get("python_version") == "3.14.6"
            and isinstance(runtime.get("executable"), dict)
            and runtime["executable"].get("path") == PYTHON
            and runtime["executable"].get("sha256") == PYTHON_SHA256
            and isinstance(gate, dict)
            and gate.get("status") == "PASS"
            and gate.get("all_obligations_mapped") is True
            and gate.get("final_holdout_authorized") is False,
            "retain exactly the original 31,237-case, 13-suite stable oracle")
    freeze = strict_json(
        protected["oracle/phase2/six-family-p0-producer-v3.json"],
        "six-family first-party source independence",
    )
    require(freeze.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and freeze.get("version") == 3 and freeze.get("family_count") == 6
            and freeze.get("source_owner_count") == 25
            and freeze.get("pairwise_shared_semantic_source_count") == 0
            and freeze.get("suite_count") == 13
            and freeze.get("case_execution_denominator") == 31237,
            "retain six genuinely separate from-scratch matching-engine families")
    families = freeze.get("families")
    require(isinstance(families, list) and len(families) == 6,
            "reject missing or substituted independent candidate families")
    identifiers: set[str] = set()
    owners: set[str] = set()
    for family in families:
        require(isinstance(family, dict)
                and isinstance(family.get("family"), str)
                and family["family"] not in identifiers,
                "reject repeated or forged independent family ownership")
        identifiers.add(family["family"])
        sources = family.get("sources")
        require(isinstance(sources, list)
                and len(sources) == family.get("owned_source_count")
                and len(sources) > 0,
                "reject incomplete first-party semantic engine ownership")
        for owner in sources:
            require(isinstance(owner, dict)
                    and isinstance(owner.get("relative"), str)
                    and owner["relative"] not in owners
                    and isinstance(owner.get("size_bytes"), int),
                    "reject duplicated, cross-family, or external source ownership")
            checked_read(owner["relative"],
                         valid_digest(owner.get("sha256"), "first-party source"),
                         owner["size_bytes"])
            owners.add(owner["relative"])
    require(identifiers == {"c", "rust", "zig", "cpp", "go", "fortran"}
            and len(owners) == 25
            and set(SOURCE_OWNERS).issubset(owners),
            "reject a wrapper or another candidate as the Zig semantic engine")

    inputs = strict_json(protected[V31_INPUTS], "actual current V31 graph inputs")
    summary = strict_json(protected[V31_SUMMARY], "actual current V31 graph summary")
    validate_v31(inputs, summary)
    rust_receipt = strict_json(protected[RUST_BUILD_RECEIPT],
                               "actual Rust V12 source-build publication receipt")
    v2.validate_rust_build_receipt(rust_receipt)
    old_inputs = strict_json(v2.checked_read(
        "docs/evidence/candidate-current-overview-v30.inputs.json",
        v2.SUPPORT["docs/evidence/candidate-current-overview-v30.inputs.json"],
    ), "historical V30 graph inputs")
    old_summary = strict_json(v2.checked_read(
        "docs/evidence/candidate-current-overview-v30.json",
        v2.SUPPORT["docs/evidence/candidate-current-overview-v30.json"],
    ), "historical V30 graph summary")
    historical = v2.load_history(old_inputs, old_summary)
    v31_history = v2.extend_current_evidence(historical, rust_receipt)
    require(len(historical) == 154
            and len(v31_history) == HISTORICAL_V31_HISTORY_REFERENCES
            and v31_history.get(RUST_BUILD_ARCHIVE) == SUPPORT[RUST_BUILD_ARCHIVE][0]
            and v31_history.get(RUST_BUILD_RECEIPT) == SUPPORT[RUST_BUILD_RECEIPT][0],
            "independently preserve all 156 historical V31 graph references")
    matching_receipt = strict_json(
        protected[RUST_MATCH_RECEIPT],
        "actual corrected Rust V4 complete matching failure receipt",
    )
    current = validate_rust_matching(matching_receipt, v31_history)
    require(len(current) == CURRENT_HISTORY_REFERENCES
            and current.get(RUST_MATCH_ARCHIVE) == SUPPORT[RUST_MATCH_ARCHIVE][0]
            and current.get(RUST_MATCH_RECEIPT) == SUPPORT[RUST_MATCH_RECEIPT][0],
            "derive current 158 references from all actual Rust V4 failure owners")

    additive = strict_json(protected[ADDITIVE_CONTRACT],
                           "frozen additive 50-case callable-introspection oracle")
    validate_additive(additive)
    legacy_contract = strict_json(protected[V11_CONTRACT],
                                  "historical V11 low-level Zig build policy")
    validate_v11_policy(legacy_contract)
    raw_v7 = strict_json(protected[V7_CONTRACT],
                         "frozen first-party V7 raw-ELF parser contract")
    require(raw_v7.get("schema")
            == "rebar-phase2-owned-native-source-build-v7-source-freeze"
            and raw_v7.get("version") == 7
            and raw_v7.get("family_count") == 6
            and raw_v7.get("source_owner_count") == 25
            and isinstance(raw_v7.get("raw_elf_forensics"), dict)
            and raw_v7["raw_elf_forensics"].get("format")
            == "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN",
            "require genuine first-party complete-byte ELF64 independence forensics")
    lock = strict_json(protected["toolchains/zig-0.16.0.lock.json"],
                       "exact stable Zig compiler lock")
    require(lock.get("schema") == "rebar-official-language-toolchain-v1"
            and lock.get("language") == "Zig"
            and lock.get("version") == "0.16.0"
            and lock.get("release_channel") == "stable"
            and lock.get("compiler_sha256") == TOOLCHAINS["zig"][1]
            and lock.get("compiler_relative_path")
            == "zig-x86_64-linux-0.16.0/zig",
            "reject a substituted or unstable offline Zig compiler")
    tools = {
        role: read_external(pin[0], pin[1], pin[2], pin[3])
        for role, pin in TOOLCHAINS.items()
    }
    require(tools["zig"]["sha256"] == TOOLCHAINS["zig"][1],
            "authenticate the complete exact stable Zig compiler bytes")
    contract = contract_document(source_pin, protocol_pin)
    if contract_pin is not None:
        raw = checked_read(CONTRACT_PATH,
                           valid_digest(contract_pin, "Zig V12 build contract"))
        require(raw == canonical(contract),
                "reject a forged or noncanonical frozen V12 build contract")
    retained = ({"protected": protected, "originals": originals,
                 "derived": derived, "overlay": v2, "toolchains": tools}
                if retain else {})
    return contract, retained


class SyntheticBoundary:
    """Make every real build, source, network, native, and clock effect fail."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def deny(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise BuildError("source-only Zig V12 effect denied: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, deny)

    def __enter__(self) -> SyntheticBoundary:
        groups = (
            (builtins, ("open",)), (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "remove", "unlink", "rename", "replace",
                  "fsync", "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "mkdir", "unlink", "rename", "replace",
                    "stat", "lstat", "resolve")),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (importlib, ("import_module",)),
            (threading.Thread, ("start",)),
            (gzip, ("decompress", "open", "compress")),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "thread_time", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object,
                 _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_v31() -> tuple[dict, dict]:
    boundary = {
        "final_comparison_planned_case_count": FINAL_PLANNED_CASE_COUNT,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
    }
    rust_owner = {
        "schema": "rebar-candidate-current-overview-v31-authenticated-actual-rust-v12-source-build",
        "status": "PASS", "build_status": "PASS",
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "actual_compiler_process_count": 28,
        "archive": {
            "path": RUST_BUILD_ARCHIVE, "sha256": SUPPORT[RUST_BUILD_ARCHIVE][0],
            "bytes": SUPPORT[RUST_BUILD_ARCHIVE][1], "device": 2064,
            "inode": 524643, "mode": "0600", "nlink": 1,
        },
        "receipt": {
            "path": RUST_BUILD_RECEIPT, "sha256": SUPPORT[RUST_BUILD_RECEIPT][0],
            "bytes": SUPPORT[RUST_BUILD_RECEIPT][1], "device": 2064,
            "inode": 524644, "mode": "0600", "nlink": 1,
        },
    }
    inputs = {
        **boundary,
        "schema": "rebar-candidate-current-overview-v31-inputs",
        "version": 31,
        "repository_evidence_owner_count": 151,
        "all_digest_addressed_history_path_count": 156,
        "candidate_qualified_count": 0,
        "suite_count": 13, "full_case_denominator": 31237,
        "private_waiver_count": 13,
        "actual_zig_candidate_workers": 13,
        "actual_zig_semantic_mismatch_count": 2172,
        "actual_rust_candidate_workers": 13,
        "actual_rust_semantic_mismatch_count": 1087,
        "c_original_campaign_semantic_mismatch_count": 1230,
        "rust_v12_build_status": "PASS",
        "rust_v12_candidate_correctness": "NOT MEASURED",
        "rust_v12_matching_test_status": "NOT MEASURED",
        "rust_v12_actual_candidate_workers": 0,
        "rust_v12_actual_compiler_process_count": 28,
        "rust_v12_candidate_qualified": False,
        "rust_v12_independent_phase_count": 2,
        "preserved_v30_repository_evidence_owner_count": 149,
        "preserved_v30_digest_addressed_history_path_count": 154,
        "new_rust_v12_source_build_repository_evidence_owner_count": 2,
        "actual_rust_v12_corrected_source_build": rust_owner,
    }
    snapshot = {
        **boundary,
        "all_actual_candidate_and_native_evidence_owner_count": 151,
        "all_digest_addressed_history_path_count": 156,
        "current_source_owner_count": 25,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "baseline_passed": 31237,
        "suite_ids": list(SUITE_IDS),
        "zig_v2_original_campaign_status": "FAIL",
        "zig_v2_original_campaign_semantic_mismatch_count": 2172,
        "zig_v2_original_campaign_verified_passing_case_count": 2847,
        "zig_v2_original_campaign_actual_candidate_workers": 13,
        "zig_v2_original_campaign_completed_suite_count": 13,
        "zig_v2_original_campaign_infrastructure_failure_count": 0,
        "rust_v3_original_campaign_semantic_mismatch_count": 1087,
        "c_v4_original_campaign_semantic_mismatch_count": 1230,
        "rust_v12_source_build_status": "PASS",
        "rust_v12_source_build_candidate_correctness": "NOT MEASURED",
        "rust_v12_source_build_matching_test_status": "NOT MEASURED",
        "rust_v12_source_build_process_count": 28,
        "rust_v12_source_build_independent_phase_count": 2,
        "rust_v12_source_build_candidate_qualified": False,
    }
    summary = {
        **boundary,
        "schema": "rebar-candidate-current-overview-v31-summary",
        "status": "PASS",
        "repository_evidence_owner_count": 151,
        "authenticated_digest_addressed_history_paths": 156,
        "qualified_candidate_count": 0,
        "suite_count": 13, "full_case_denominator": 31237,
        "private_waiver_count": 13,
        "zig_original_campaign_status": "FAIL",
        "zig_original_campaign_semantic_mismatch_count": 2172,
        "zig_original_campaign_verified_passing_case_count": 2847,
        "zig_original_campaign_candidate_worker_count": 13,
        "rust_original_campaign_status": "FAIL",
        "rust_original_campaign_semantic_mismatch_count": 1087,
        "rust_original_campaign_verified_passing_case_count": 7438,
        "c_original_campaign_status": "FAIL",
        "c_original_campaign_semantic_mismatch_count": 1230,
        "c_original_campaign_verified_passing_case_count": 7325,
        "rust_v12_source_build_status": "PASS",
        "rust_v12_source_build_candidate_correctness": "NOT MEASURED",
        "rust_v12_source_build_matching_test_status": "NOT MEASURED",
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "winner_selected": False,
        "snapshot": snapshot,
    }
    return inputs, summary


def synthetic_additive() -> dict:
    return {
        "schema": "rebar-python-re-callable-introspection-v1-source-freeze",
        "version": 1,
        "status": "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN",
        "additional_obligation": {
            "case_count": 50,
            "case_matrix": [{"id": f"synthetic-callable-{number:02d}"}
                            for number in range(50)],
        },
        "original_correctness": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "denominator_modified": False,
        },
        "phase_boundary": {
            "introspection_reference": "NOT RUN",
            "candidate_introspection": "NOT MEASURED",
            "actual_reference_roles_started": 0,
            "actual_candidate_workers_started": 0,
            "actual_source_builds": 0,
            "actual_holdout_cases_read": 0,
            "actual_clock_samples": 0,
            "holdout": "NOT OPENED",
            "candidate_qualified": False,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "winner_selected": False,
        },
    }


def synthetic_rust_matching() -> tuple[dict[str, str], dict]:
    history = {
        f"oracle/phase2/evidence/zig-v12-v31-history-{number:03d}.json":
            "a" * 64
        for number in range(124)
    }
    history[RUST_BUILD_ARCHIVE] = SUPPORT[RUST_BUILD_ARCHIVE][0]
    history[RUST_BUILD_RECEIPT] = SUPPORT[RUST_BUILD_RECEIPT][0]
    history.update({
        ("experiments/rust_public_practice_v1/"
         f"zig-v12-v31-history-{number:03d}.json"): "b" * 64
        for number in range(30)
    })
    receipt = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt",
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "family": "rust",
        "label": "phase2-v12-rust-flag-original-p0",
        "suite_count": 13,
        "completed_suite_count": 13,
        "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "actual_candidate_workers": 13,
        "semantic_mismatch_count": 1036,
        "verified_passing_case_count": 8965,
        "infrastructure_failure_count": 0,
        "historical_evidence_owner_count_before_publication":
            HISTORICAL_V31_EVIDENCE_OWNERS,
        "historical_authenticated_reference_count_before_publication":
            HISTORICAL_V31_HISTORY_REFERENCES,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "resulting_authenticated_reference_count": CURRENT_HISTORY_REFERENCES,
        "uncompressed_bytes": 5280314,
        "uncompressed_sha256":
            "a7b2dfbe5d1a8ddf8b1c3de48c24085d43260084c4a48e4a8394f1cc5b66600b",
        "recovery_journal_sha256":
            "726e81e5d2ee255e1f46d3029290ae9486fbd23711c9a45a691d091d088f3278",
        "actual_v12_build_archive_sha256": SUPPORT[RUST_BUILD_ARCHIVE][0],
        "actual_v12_build_receipt_sha256": SUPPORT[RUST_BUILD_RECEIPT][0],
        "corrected_public_adapter_sha256":
            "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5",
        "corrected_bridge_source_sha256":
            "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257",
        "archive": {
            "path": str(ROOT / RUST_MATCH_ARCHIVE),
            "relative": RUST_MATCH_ARCHIVE.rsplit("/", 1)[-1],
            "sha256": SUPPORT[RUST_MATCH_ARCHIVE][0],
            "size_bytes": SUPPORT[RUST_MATCH_ARCHIVE][1],
            "device": 2064,
            "inode": 524655,
            "mode": 0o600,
            "exclusive_creation": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "same_inode_readback_verified": True,
            "streaming_readback_verified": True,
            "write_calls": 20,
        },
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "v2_unsafe_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v9_c_only_runner_invoked": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return history, receipt


def self_test() -> dict:
    accepted = rejected = 0
    root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v12-freeze"
    with SyntheticBoundary() as boundary:
        inputs, summary = synthetic_v31()
        additive = synthetic_additive()
        validate_v31(inputs, summary)
        validate_additive(additive)
        synthetic_history, synthetic_match = synthetic_rust_matching()
        current_history = validate_rust_matching(synthetic_match,
                                                 synthetic_history)
        templates = command_templates()
        phase_a, phase_b = (phase_paths(root, phase) for phase in PHASE_NAMES)
        contract = contract_document("a" * 64, "b" * 64)
        checks = (
            (checked_workdir(root) == root, "accept only the genuine V2 root"),
            (len(templates) == 2, "freeze two independent source-build phases"),
            (phase_a["source"] != phase_b["source"], "distinct phase source trees"),
            (phase_a["native"] != phase_b["native"], "distinct native outputs"),
            (phase_a["zig_local_cache"] != phase_b["zig_local_cache"],
             "distinct local compiler caches"),
            (phase_a["zig_global_cache"] != phase_b["zig_global_cache"],
             "distinct global compiler caches"),
            (len(planned_commands(root, "reference-a")) == 13,
             "freeze thirteen first-phase compiler and audit roles"),
            (len(planned_commands(root, "reference-b")) == 13,
             "freeze thirteen second-phase compiler and audit roles"),
            (tuple(planned_commands(root, "reference-a")) == PROCESS_ROLES,
             "preserve exact authentic V11 low-level process order"),
            (planned_commands(root, "reference-a")["build_zig_engine"][0]
             == PINNED_ZIG, "freeze the genuine stable Zig compiler"),
            ("ReleaseFast" in planned_commands(root, "reference-a")["build_zig_engine"],
             "freeze a native optimized first-party Zig engine"),
            (planned_commands(root, "reference-a")["build_zig_bridge"][0]
             == PINNED_GCC, "freeze the pinned CPython C bridge compiler"),
            ("-Wl,-rpath,$ORIGIN"
             in planned_commands(root, "reference-a")["build_zig_bridge"],
             "bind the bridge only to its own adjacent first-party Zig engine"),
            (len(build_environment(root, "reference-a")) == 8,
             "freeze a minimal offline deterministic build environment"),
            ("HOME" not in build_environment(root, "reference-a")
             and "home" not in build_environment(root, "reference-a"),
             "do not repurpose or read the user home directory"),
            (contract["published_history"]["historical_v31_evidence_owner_count"] == 151
             and contract["published_history"]["historical_v31_authenticated_reference_count"]
             == 156,
             "preserve signed V31 strictly as historical evidence"),
            (contract["published_history"]["authoritative_evidence_owner_count"] == 153
             and contract["published_history"]["authenticated_reference_count"] == 158,
             "derive the genuine current 153-owner, 158-reference history"),
            (len(synthetic_history) == 156 and len(current_history) == 158,
             "add exactly two distinct corrected Rust matching evidence owners"),
            (synthetic_match["candidate_status"] == "FAIL"
             and synthetic_match["semantic_mismatch_count"] == 1036
             and synthetic_match["verified_passing_case_count"] == 8965,
             "preserve all actual corrected Rust matching failures and passes"),
            (contract["preserved_matching_results"]["rust_semantic_mismatch_count"]
             == 1036
             and contract["preserved_matching_results"][
                 "historical_rust_semantic_mismatch_count"] == 1087,
             "distinguish current corrected Rust matching from its historical result"),
            (contract["corrected_v2_overlay"]["derived_bridge_sha256"]
             == SOURCE_OWNERS[ORIGINAL_BRIDGE][0],
             "freeze the canonical corrected 173,026-byte Zig bridge"),
            (contract["corrected_v2_overlay"]["v1_conditional_overlay_used"] is False,
             "never build the failed V1 conditional scanner overlay"),
            (contract["future_build_policy"]["actual_status"] == "NOT RUN"
             and contract["future_build_policy"]["actual_process_count"] == 0,
             "distinguish frozen future compiler steps from executed builds"),
            (contract["additive_callable_introspection"]["additive_case_count"] == 50
             and contract["additive_callable_introspection"]["reference_status"]
             == "NOT RUN",
             "retain 50 additional frozen, genuinely unrun test cases"),
            (contract["oracle"]["case_execution_count"] == 31237,
             "do not change the original correctness denominator"),
            (contract["actual_rust_v12_source_build"]["build_status"] == "PASS"
             and contract["actual_rust_v12_source_build"]["candidate_correctness"]
             == "NOT MEASURED",
             "distinguish genuine prior Rust building from untested matching"),
            (contract["preserved_matching_results"]["zig_semantic_mismatch_count"]
             == 2172,
             "preserve the actual full Zig matching failure"),
        )
        for condition, label in checks:
            require(condition, "source-only Zig V12 positive control failed: " + label)
            accepted += 1

        def reject(action: object, label: str) -> None:
            nonlocal rejected
            try:
                action()  # type: ignore[operator]
            except (BuildError, OSError, TypeError, ValueError, OverflowError,
                    UnicodeError, RecursionError, KeyError):
                rejected += 1
            else:
                raise BuildError("accepted hostile Zig V12 source control: " + label)

        for value in ("", "/", "../source", "a/../source", "a/./source",
                      "a//source", "a/", "./source", "x" * 513,
                      "/home/dev-user/src/rebar/candidates/zig/py_bridge.c",
                      "oracle/phase2/evidence/forged.json.gz",
                      "candidates/_zig_probe.so", "secret/holdout.json",
                      "benchmarks/final.json", RUST_BUILD_ARCHIVE,
                      RUST_MATCH_ARCHIVE):
            reject(lambda path=value: relative_parts(path),
                   "reject escaped, native, hidden, or unapproved compressed owner")
        reject(lambda: relative_parts("oracle/phase2/evidence/forged.gz",
                                     allow_rust_build_archive=True),
               "reject arbitrary gzip under the exact Rust-only exception")
        reject(lambda: relative_parts(RUST_BUILD_ARCHIVE,
                                     allow_rust_build_archive=1),
               "reject a substituted nonboolean gzip authorization")
        for value in ("", "/", "/tmp", "/home/dev-user/src/rebar",
                      "/tmp/rebar-phase2-zig-scanner-capture-source-build-v1-synthetic",
                      "/tmp/rebar-phase2-rust-source-build-v12-synthetic",
                      "/tmp/" + PRIVATE_ROOT_PREFIX,
                      "/tmp/" + PRIVATE_ROOT_PREFIX + "tiny",
                      root + "/reference-a", root + "/../escape"):
            reject(lambda path=value: checked_workdir(path),
                   "reject reused V1, shared, escaped, or cross-family root")
        for phase in ("", "reference-c", "reference-a/..", "zig", None):
            reject(lambda value=phase: phase_paths(root, value),
                   "reject a missing or cross-family compiler phase")
        for value in ("", "0" * 63, "0" * 65, "F" * 64, "g" * 64):
            reject(lambda fingerprint=value: valid_digest(fingerprint, "synthetic"),
                   "reject an invalid independently supplied digest")
        for value in ("", "../build", "UPPERCASE", "phase--bad",
                      "phase-ending-", "a" * 49):
            reject(lambda label=value: checked_label(label),
                   "reject reused, escaping, or noncanonical evidence label")
        for raw in (b'{"a":1,"a":2}\n', b'{"a":NaN}\n', b"[]\n",
                    b'{"a": 1}\n', b'{"a":1}'):
            reject(lambda value=raw: strict_json(value, "synthetic",
                                                canonical_required=True),
                   "reject duplicate, nonfinite, or noncanonical JSON")
        first = planned_commands(root, "reference-a")
        second = planned_commands(root, "reference-b")
        reject(lambda: checked_command("build_zig_engine", ["/bin/sh", "-c", "zig"],
                                       root, "reference-a"),
               "reject shell-based compiler delegation")
        reject(lambda: checked_command("build_zig_engine",
                                       second["build_zig_engine"],
                                       root, "reference-a"),
               "reject a cross-phase Zig engine command")
        reject(lambda: checked_command("build_zig_bridge",
                                       first["build_zig_bridge"][:-1],
                                       root, "reference-a"),
               "reject a truncated CPython bridge build")
        changed = list(first["build_zig_engine"])
        changed[0] = "/usr/bin/zig"
        reject(lambda: checked_command("build_zig_engine", changed,
                                       root, "reference-a"),
               "reject an unpinned Zig compiler")
        reject(lambda: checked_command("build_rust_engine", [PINNED_ZIG],
                                       root, "reference-a"),
               "reject a cross-family matching engine")

        overview_mutations = (
            (0, ("repository_evidence_owner_count",), 149),
            (0, ("all_digest_addressed_history_path_count",), 154),
            (0, ("candidate_qualified_count",), 1),
            (0, ("suite_count",), 12),
            (0, ("full_case_denominator",), 31287),
            (0, ("actual_zig_semantic_mismatch_count",), 0),
            (0, ("actual_rust_semantic_mismatch_count",), 0),
            (0, ("c_original_campaign_semantic_mismatch_count",), 0),
            (0, ("rust_v12_build_status",), "FAIL"),
            (0, ("rust_v12_candidate_correctness",), "PASS"),
            (0, ("rust_v12_matching_test_status",), "PASS"),
            (0, ("rust_v12_actual_candidate_workers",), 1),
            (0, ("rust_v12_actual_compiler_process_count",), 27),
            (0, ("rust_v12_candidate_qualified",), True),
            (0, ("new_rust_v12_source_build_repository_evidence_owner_count",), 1),
            (0, ("final_holdout_opened",), True),
            (0, ("actual_rust_v12_corrected_source_build", "candidate_correctness"),
             "PASS"),
            (0, ("actual_rust_v12_corrected_source_build", "archive", "sha256"),
             "0" * 64),
            (0, ("actual_rust_v12_corrected_source_build", "archive", "inode"), 0),
            (0, ("actual_rust_v12_corrected_source_build", "receipt", "inode"),
             524643),
            (1, ("repository_evidence_owner_count",), 149),
            (1, ("authenticated_digest_addressed_history_paths",), 154),
            (1, ("qualified_candidate_count",), 1),
            (1, ("zig_original_campaign_status",), "PASS"),
            (1, ("zig_original_campaign_semantic_mismatch_count",), 0),
            (1, ("rust_original_campaign_semantic_mismatch_count",), 0),
            (1, ("c_original_campaign_semantic_mismatch_count",), 0),
            (1, ("rust_v12_source_build_candidate_correctness",), "PASS"),
            (1, ("snapshot", "current_source_owner_count"), 24),
            (1, ("snapshot", "frozen_independent_engine_family_count"), 5),
            (1, ("snapshot", "all_digest_addressed_history_path_count"), 154),
            (1, ("snapshot", "zig_v2_original_campaign_status"), "PASS"),
            (1, ("snapshot", "zig_v2_original_campaign_semantic_mismatch_count"), 0),
            (1, ("snapshot", "rust_v12_source_build_matching_test_status"), "PASS"),
            (1, ("snapshot", "final_comparison_cases_generated"), True),
            (1, ("hidden_cases_read",), 1),
            (1, ("clock_samples",), 1),
            (1, ("winner_selected",), True),
        )
        for index, route, forged in overview_mutations:
            pair = copy.deepcopy((inputs, summary))
            node = pair[index]
            for key in route[:-1]:
                node = node[key]
            node[route[-1]] = forged
            reject(lambda values=pair: validate_v31(*values),
                   "reject stale history, fake engine qualification, or fabricated Rust match")
        matching_mutations = (
            (("status",), "FAIL"),
            (("publication_status",), "FAIL"),
            (("publication_pass_means",), "CANDIDATE PASS"),
            (("candidate_status",), "PASS"),
            (("candidate_qualified",), True),
            (("family",), "zig"),
            (("suite_count",), 12),
            (("completed_suite_count",), 12),
            (("case_execution_denominator",), 31287),
            (("actual_candidate_workers",), 0),
            (("semantic_mismatch_count",), 0),
            (("semantic_mismatch_count",), 1087),
            (("verified_passing_case_count",), 7438),
            (("infrastructure_failure_count",), 1),
            (("historical_evidence_owner_count_before_publication",), 149),
            (("historical_authenticated_reference_count_before_publication",), 154),
            (("new_repository_evidence_owner_count",), 1),
            (("resulting_repository_evidence_owner_count",), 151),
            (("resulting_authenticated_reference_count",), 156),
            (("actual_v12_build_archive_sha256",), "0" * 64),
            (("actual_v12_build_receipt_sha256",), "0" * 64),
            (("archive", "sha256"), "0" * 64),
            (("archive", "size_bytes"), SUPPORT[RUST_MATCH_ARCHIVE][1] - 1),
            (("archive", "inode"), 524643),
            (("archive", "mode"), 0o644),
            (("archive", "streaming_readback_verified"), False),
            (("all_four_original_targets_restored",), False),
            (("v2_unsafe_activation_invoked",), True),
            (("hidden_cases_read",), 1),
            (("benchmark_files_read",), 1),
            (("clock_samples",), 1),
            (("performance",), "FASTER"),
            (("holdout",), "OPENED"),
            (("winner_selected",), True),
        )
        for route, forged in matching_mutations:
            altered = copy.deepcopy(synthetic_match)
            node = altered
            for key in route[:-1]:
                node = node[key]
            node[route[-1]] = forged
            reject(lambda value=altered: validate_rust_matching(
                value, synthetic_history),
                "reject stale 151/156, invented Rust PASS, or substituted matching owner")
        for duplicate, fingerprint in (
            (RUST_MATCH_ARCHIVE, SUPPORT[RUST_MATCH_ARCHIVE][0]),
            (RUST_MATCH_RECEIPT, SUPPORT[RUST_MATCH_RECEIPT][0]),
        ):
            history = dict(synthetic_history)
            history.pop("oracle/phase2/evidence/zig-v12-v31-history-000.json")
            history[duplicate] = fingerprint
            reject(lambda value=history: validate_rust_matching(
                synthetic_match, value),
                "reject duplicate actual Rust matching archives or receipts")
        additive_mutations = (
            (("status",), "PASS"),
            (("additional_obligation", "case_count"), 49),
            (("additional_obligation", "case_matrix"), []),
            (("original_correctness", "case_execution_denominator"), 31287),
            (("original_correctness", "denominator_modified"), True),
            (("phase_boundary", "introspection_reference"), "PASS"),
            (("phase_boundary", "candidate_introspection"), "PASS"),
            (("phase_boundary", "actual_reference_roles_started"), 1),
            (("phase_boundary", "actual_candidate_workers_started"), 1),
            (("phase_boundary", "actual_holdout_cases_read"), 1),
            (("phase_boundary", "actual_clock_samples"), 1),
            (("phase_boundary", "winner_selected"), True),
        )
        for route, forged in additive_mutations:
            altered = copy.deepcopy(additive)
            node = altered
            for key in route[:-1]:
                node = node[key]
            node[route[-1]] = forged
            reject(lambda value=altered: validate_additive(value),
                   "reject a run or silently counted additive 50-case oracle")
        effect_probes = (
            (lambda: builtins.open("/tmp/forbidden-zig-v12"), "built-in source open"),
            (lambda: io.open("/tmp/forbidden-zig-v12"), "I/O source open"),
            (lambda: os.open("/tmp/forbidden-zig-v12", os.O_RDONLY),
             "descriptor source read"),
            (lambda: os.read(0, 1), "real source descriptor read"),
            (lambda: os.write(1, b"forbidden"), "real source descriptor write"),
            (lambda: os.stat("/tmp"), "filesystem stat"),
            (lambda: os.lstat("/tmp"), "symlink traversal"),
            (lambda: os.mkdir("/tmp/forbidden-zig-v12"), "private phase creation"),
            (lambda: os.unlink("/tmp/forbidden-zig-v12"), "owner removal"),
            (lambda: os.replace("/tmp/a-zig-v12", "/tmp/b-zig-v12"),
             "owner replacement"),
            (lambda: Path("/tmp/forbidden-zig-v12").read_bytes(), "path source read"),
            (lambda: Path("/tmp/forbidden-zig-v12").write_bytes(b"x"),
             "path source write"),
            (lambda: subprocess.Popen((PINNED_ZIG, "version")), "Zig compiler"),
            (lambda: subprocess.run((PINNED_GCC, "--version")), "C compiler"),
            (lambda: subprocess.run((PINNED_READELF, "--version")), "ELF inspector"),
            (lambda: builtins.open("candidates/_zig_probe.so"), "native engine"),
            (lambda: builtins.open("benchmarks/holdout.json"), "held-out cases"),
            (lambda: gzip.decompress(b"forbidden"), "compressed archive inflation"),
            (lambda: gzip.open("forbidden.gz"), "matching failure archive"),
            (lambda: gzip.compress(b"forbidden"), "build report publication"),
            (lambda: tempfile.mkdtemp(), "private phase root"),
            (lambda: tempfile.mkstemp(), "private source inode"),
            (lambda: importlib.import_module("candidates.zig_candidate"),
             "first-party candidate import"),
            (lambda: importlib.import_module("candidates.rust_candidate"),
             "cross-family candidate import"),
            (lambda: importlib.import_module("re"), "stdlib matching delegation"),
            (lambda: importlib.import_module("_sre"), "CPython matching delegation"),
            (lambda: socket.socket(), "network connection"),
            (lambda: threading.Thread().start(), "matching worker"),
            (lambda: time.perf_counter(), "performance clock"),
            (lambda: time.perf_counter_ns(), "nanosecond clock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.sleep(0), "waiting"),
        )
        for action, label in effect_probes:
            reject(action, label)
        blocked = boundary.blocked
    require(blocked == len(effect_probes),
            "physically block every compiler, matching, archive, native, and clock")
    return {
        "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
        "version": 12,
        "accepted_source_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_controls": blocked,
        "actual_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "authenticated_history_reference_count": CURRENT_HISTORY_REFERENCES,
        "frozen_case_execution_count": 31237,
        "additive_frozen_case_count": 50,
        "additive_reference_status": "NOT RUN",
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_zig_verified_passing_case_count": 2847,
        "historical_rust_semantic_mismatch_count": 1087,
        "current_rust_semantic_mismatch_count": 1036,
        "current_rust_verified_passing_case_count": 8965,
        "current_rust_candidate_worker_count": 13,
        "historical_c_semantic_mismatch_count": 1230,
        "actual_rust_v12_source_build_status": "PASS",
        "actual_rust_v12_source_build_candidate_correctness": "NOT MEASURED",
        "actual_rust_v12_matching_status": "FAIL",
        "zig_v12_build_status": "NOT RUN",
        "corrected_bridge_sha256": SOURCE_OWNERS[ORIGINAL_BRIDGE][0],
        "corrected_bridge_bytes": SOURCE_OWNERS[ORIGINAL_BRIDGE][1],
        "actual_build_process_count": 0,
        "actual_source_apply_count": 0,
        "compressed_matching_failure_archive_files_opened": 0,
        "decompressed_archive_bytes_read": 0,
        "gzip_inflation_count": 0,
        "candidate_imports": 0, "candidate_processes_started": 0,
        "native_libraries_loaded": 0, "network_requests": 0,
        "clock_samples": 0, "workspace_mutations": 0,
        "holdout_opened": False, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "winner_selected": False,
    }


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    selected = checked_label(label)
    base = "native-source-build-v12-zig-" + selected
    if failed:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def evidence_directory_descriptor() -> int:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    current = os.open(str(ROOT), flags)
    try:
        for part in relative_parts(EVIDENCE_DIRECTORY):
            following = os.open(part, flags, dir_fd=current)
            os.close(current)
            current = following
        result = current
        current = -1
        return result
    finally:
        if current >= 0:
            os.close(current)


def require_fresh_evidence(label: str) -> None:
    directory = evidence_directory_descriptor()
    try:
        for failed in (False, True):
            for name in evidence_names(label, failed):
                try:
                    descriptor = os.open(name,
                                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                                         dir_fd=directory)
                except OSError as error:
                    if error.errno == errno.ENOENT:
                        continue
                    raise
                os.close(descriptor)
                raise BuildError("reject reused or preexisting V12 evidence: " + name)
    finally:
        os.close(directory)


def exclusive_publication(directory: int, name: str, raw: bytes) -> dict:
    require(isinstance(directory, int) and directory >= 0
            and isinstance(name, str) and name not in ("", ".", "..")
            and "/" not in name and "\\" not in name
            and isinstance(raw, bytes) and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "publish only an exact bounded owner-only V12 evidence file")
    descriptor: int | None = None
    try:
        descriptor = os.open(
            name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600, dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require a new, private, unlinked V12 evidence inode")
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(isinstance(count, int) and count > 0,
                    "preserve every actual source-build report byte")
            offset += count
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == len(raw),
                "reject an altered or incomplete synchronized evidence owner")
        os.close(descriptor)
        descriptor = None
        verify = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                         dir_fd=directory)
        try:
            visible = os.fstat(verify)
            require((visible.st_dev, visible.st_ino, visible.st_size)
                    == (after.st_dev, after.st_ino, after.st_size),
                    "reject evidence substitution before same-inode readback")
            hasher = hashlib.sha256()
            total = 0
            while True:
                piece = os.read(verify, 1024 * 1024)
                if not piece:
                    break
                total += len(piece)
                require(total <= MAX_ARCHIVE_BYTES,
                        "bound the complete exclusive evidence readback")
                hasher.update(piece)
            require(total == len(raw) and hasher.hexdigest() == digest(raw),
                    "reject incomplete durable same-inode build evidence")
        finally:
            os.close(verify)
        os.fsync(directory)
        return {
            "path": EVIDENCE_DIRECTORY + "/" + name,
            "sha256": digest(raw), "bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
            "uid": after.st_uid, "nlink": after.st_nlink,
            "mode": "0600", "exclusive_creation": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "same_inode_readback_verified": True,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)


def publish_report(report: dict, label: str) -> dict:
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(label, failed)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "bound the complete V12 source-build process and native report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_ARCHIVE_BYTES,
            "bound the deterministic actual compressed V12 source-build report")
    directory = evidence_directory_descriptor()
    try:
        archive = exclusive_publication(directory, archive_name, compressed)
        receipt = {
            "schema": RECEIPT_SCHEMA, "version": 12,
            "status": "PASS", "build_status": report["status"],
            "family": "zig", "label": checked_label(label),
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "contract_sha256": report["contract_sha256"],
            "archive": archive,
            "uncompressed_sha256": digest(plain),
            "uncompressed_bytes": len(plain),
            "historical_v31_evidence_owner_count": HISTORICAL_V31_EVIDENCE_OWNERS,
            "historical_v31_authenticated_reference_count":
                HISTORICAL_V31_HISTORY_REFERENCES,
            "actual_evidence_owner_count_before_publication":
                CURRENT_EVIDENCE_OWNERS,
            "actual_authenticated_reference_count_before_publication":
                CURRENT_HISTORY_REFERENCES,
            "new_actual_evidence_owner_count": 2,
            "repository_evidence_owner_count_after_publication":
                CURRENT_EVIDENCE_OWNERS + 2,
            "authenticated_history_reference_count_after_publication":
                CURRENT_HISTORY_REFERENCES + 2,
            "expected_compiler_process_count_only_after_success":
                EXPECTED_PROCESS_COUNT,
            "actual_compiler_process_count": report["actual_build_process_count"],
            "actual_source_apply_count": report["actual_source_apply_count"],
            "corrected_bridge_sha256": SOURCE_OWNERS[ORIGINAL_BRIDGE][0],
            "corrected_bridge_bytes": SOURCE_OWNERS[ORIGINAL_BRIDGE][1],
            "v1_overlay_used": False,
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "network_requests": 0,
            "hidden_cases_read": 0, "final_cases_read": 0,
            "benchmark_files_read": 0, "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
            "failure_preserved": failed,
            "receipt_self_publication": "NOT CLAIMED",
        }
        raw_receipt = canonical(receipt)
        require(len(raw_receipt) <= MAX_SOURCE_BYTES,
                "bound the exact independent V12 source-build receipt")
        published_receipt = exclusive_publication(directory, receipt_name,
                                                  raw_receipt)
        return {
            "schema": SCHEMA + "-publication-result",
            "status": report["status"],
            "family": "zig", "label": checked_label(label),
            "archive": archive, "receipt": published_receipt,
            "failure_preserved": failed,
            "actual_build_process_count": report["actual_build_process_count"],
            "actual_source_apply_count": report["actual_source_apply_count"],
            "expected_build_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
            "historical_v31_evidence_owner_count": HISTORICAL_V31_EVIDENCE_OWNERS,
            "historical_v31_authenticated_reference_count":
                HISTORICAL_V31_HISTORY_REFERENCES,
            "actual_evidence_owner_count_before_publication":
                CURRENT_EVIDENCE_OWNERS,
            "actual_authenticated_reference_count_before_publication":
                CURRENT_HISTORY_REFERENCES,
            "new_actual_evidence_owner_count": 2,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }
    finally:
        os.close(directory)


def load_legacy(retained: dict) -> tuple[types.ModuleType, types.ModuleType]:
    legacy = load_module("_rebar_owned_zig_v12_low_level_v11",
                         V11_SOURCE, retained["protected"][V11_SOURCE])
    require(legacy.SCHEMA == "rebar-phase2-owned-zig-scanner-source-build-v11"
            and legacy.SOURCE_RELATIVE == V11_SOURCE
            and tuple(legacy.PROCESS_ROLES) == PROCESS_ROLES
            and legacy.EXPECTED_PROCESS_COUNT == EXPECTED_PROCESS_COUNT
            and legacy.EXPECTED_PHASE_PROCESS_COUNT == EXPECTED_PHASE_PROCESS_COUNT
            and legacy.ORIGINAL_ENGINE == ORIGINAL_ENGINE
            and legacy.ORIGINAL_BRIDGE == ORIGINAL_BRIDGE
            and legacy.ORIGINAL_ADAPTER == ORIGINAL_ADAPTER
            and legacy.PINNED_ZIG == PINNED_ZIG
            and legacy.PINNED_GCC == PINNED_GCC
            and legacy.PINNED_READELF == PINNED_READELF,
            "load only frozen V11 compiler, private phase, and raw-ELF primitives")
    legacy.PRIVATE_ROOT_PREFIX = PRIVATE_ROOT_PREFIX
    legacy.OVERLAY_SCHEMA = retained["overlay"].SCHEMA
    legacy.DERIVED_BRIDGE_SHA256 = SOURCE_OWNERS[ORIGINAL_BRIDGE][0]
    legacy.DERIVED_BRIDGE_BYTES = SOURCE_OWNERS[ORIGINAL_BRIDGE][1]
    parser = legacy.authenticate_v7_parser(retained["protected"][V7_SOURCE])
    require(callable(getattr(parser, "parse_owned_elf64", None))
            and callable(getattr(parser, "compare_owned_elf64", None)),
            "retain exact first-party complete-native-byte ELF independence audits")
    return legacy, parser


def run_build(source_pin: str, protocol_pin: str,
              contract_pin: str, label: str) -> tuple[int, dict]:
    selected = checked_label(label)
    _contract, retained = verify_context(source_pin, protocol_pin, contract_pin,
                                        retain=True)
    require_fresh_evidence(selected)
    legacy, parser = load_legacy(retained)
    overlay = retained["overlay"]
    report: dict = {
        "schema": SCHEMA, "version": 12, "status": "FAIL",
        "family": "zig", "label": selected,
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "frozen_case_execution_count": 31237,
        "suite_count": 13, "private_waiver_count": 13,
        "historical_v31_evidence_owner_count": HISTORICAL_V31_EVIDENCE_OWNERS,
        "historical_v31_authenticated_reference_count":
            HISTORICAL_V31_HISTORY_REFERENCES,
        "actual_evidence_owner_count_before_publication": CURRENT_EVIDENCE_OWNERS,
        "actual_authenticated_reference_count_before_publication":
            CURRENT_HISTORY_REFERENCES,
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_zig_verified_passing_case_count": 2847,
        "historical_rust_semantic_mismatch_count": 1087,
        "current_rust_semantic_mismatch_count": 1036,
        "current_rust_verified_passing_case_count": 8965,
        "historical_c_semantic_mismatch_count": 1230,
        "additive_frozen_case_count": 50,
        "additive_reference_status": "NOT RUN",
        "expected_build_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
        "actual_build_process_count": 0,
        "actual_source_apply_count": 0,
        "corrected_bridge_sha256": SOURCE_OWNERS[ORIGINAL_BRIDGE][0],
        "corrected_bridge_bytes": SOURCE_OWNERS[ORIGINAL_BRIDGE][1],
        "v1_overlay_used": False,
        "processes": [], "build_phases": [],
        "reproducibility": "NOT MEASURED",
        "raw_elf_differences": "NOT MEASURED",
        "candidate_imports": 0, "candidate_processes_started": 0,
        "reference_processes_started": 0,
        "native_libraries_loaded": 0, "network_requests": 0,
        "hidden_cases_read": 0, "final_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    raw_outputs: dict[tuple[str, str], bytes] = {}
    try:
        root = tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX, dir="/tmp")
        checked_workdir(root)
        descriptor = os.open(root,
                             os.O_RDONLY | os.O_CLOEXEC
                             | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            report["private_root"] = legacy.check_directory_descriptor(
                descriptor, root,
            )
        finally:
            os.close(descriptor)
        phases = legacy.prepare_private_phases(root)
        report["build_phases"] = phases
        for item in phases:
            phase = item["name"]
            require(tuple(legacy.planned_commands(root, phase)) == PROCESS_ROLES
                    and legacy.planned_commands(root, phase)
                    == planned_commands(root, phase),
                    "require exact V12 root-bound first-party low-level build commands")
            item["source_snapshots"] = {
                path: legacy.write_private_source(
                    root, phase, path, retained["originals"][path],
                    SOURCE_OWNERS[path][0],
                )
                for path in (ORIGINAL_ENGINE, ORIGINAL_ADAPTER)
            }
            legacy.assert_bridge_absent(root, phase)
        for item in phases:
            phase = item["name"]
            applied = overlay.apply_private(
                str(phase_paths(root, phase)["source"]), retained["derived"],
            )
            report["actual_source_apply_count"] += 1
            require(isinstance(applied, dict)
                    and applied.get("schema") == overlay.SCHEMA
                    and applied.get("status") == "PASS"
                    and applied.get("phase") == phase
                    and applied.get("source_apply_count") == 1
                    and applied.get("candidate_original_modified") is False
                    and applied.get("derived_source_sha256")
                    == SOURCE_OWNERS[ORIGINAL_BRIDGE][0]
                    and applied.get("derived_source_bytes")
                    == SOURCE_OWNERS[ORIGINAL_BRIDGE][1]
                    and applied.get("byte_identical_to_original") is True
                    and applied.get("snapshot_root")
                    == str(phase_paths(root, phase)["source"]),
                    "apply only the exact V2 whole-branch scanner correction")
            item["overlay_application"] = applied
            item["source_snapshots"][ORIGINAL_BRIDGE] = (
                legacy.authenticate_private_bridge(root, phase)
            )
        require(report["actual_source_apply_count"] == 2,
                "apply the V2 bridge once to each independent private phase")
        for path in SOURCE_OWNERS:
            identities = [phase["source_snapshots"][path] for phase in phases]
            require(len({(item["device"], item["inode"])
                         for item in identities}) == 2,
                    "never share source inodes between independent build phases")
        for item in phases:
            phase = item["name"]
            for role in PROCESS_ROLES[:5]:
                try:
                    legacy.run_process(role, root, phase, report["processes"])
                finally:
                    report["actual_build_process_count"] = len(report["processes"])
            native = {}
            for role in ("engine", "bridge"):
                owner, raw = legacy.capture_native_artifact(root, phase, role)
                parsed = parser.parse_owned_elf64(raw)
                require(isinstance(parsed, dict)
                        and parsed.get("file_sha256") == owner["sha256"]
                        and parsed.get("file_size") == owner["bytes"],
                        "authenticate complete first-party ELF bytes, not an outside matcher")
                native[role] = {
                    "owner": owner, "raw_elf64": parsed,
                    "independence_audit": legacy.audit_native_role(role, parsed),
                }
                require((phase, role) not in raw_outputs,
                        "reject reused independent native output roles")
                raw_outputs[(phase, role)] = raw
            item["native_outputs"] = native
            for role in PROCESS_ROLES[5:]:
                try:
                    legacy.run_process(role, root, phase, report["processes"])
                finally:
                    report["actual_build_process_count"] = len(report["processes"])
            for role in ("engine", "bridge"):
                owner, repeated = legacy.capture_native_artifact(root, phase, role)
                initial = native[role]["owner"]
                require(repeated == raw_outputs[(phase, role)]
                        and (owner["device"], owner["inode"], owner["sha256"])
                        == (initial["device"], initial["inode"], initial["sha256"]),
                        "reject native artifact replacement after exact ELF inspection")
        legacy.validate_process_schedule(report["processes"], root, complete=True)
        require(report["actual_build_process_count"] == EXPECTED_PROCESS_COUNT,
                "claim 26 native steps only after all 26 really complete")
        comparisons = {}
        for role in ("engine", "bridge"):
            first = phases[0]["native_outputs"][role]
            second = phases[1]["native_outputs"][role]
            require((first["owner"]["device"], first["owner"]["inode"])
                    != (second["owner"]["device"], second["owner"]["inode"]),
                    "reject shared output inodes in purported independent phases")
            comparisons[role] = parser.compare_owned_elf64(
                raw_outputs[(PHASE_NAMES[0], role)],
                raw_outputs[(PHASE_NAMES[1], role)],
                first["raw_elf64"], second["raw_elf64"],
            )
        report["raw_elf_differences"] = {
            "schema": SCHEMA + "-all-phase-raw-elf-differences",
            "independent_phase_count": 2,
            "native_role_count": 2,
            "roles": comparisons,
            "all_native_artifacts_byte_identical": all(
                item.get("byte_identical") is True
                for item in comparisons.values()
            ),
            "additional_compiler_or_inspector_processes": 0,
            "comparison_completed_before_reproducibility_classification": True,
        }
        require(report["raw_elf_differences"]["all_native_artifacts_byte_identical"],
                "preserve a real two-phase reproducibility failure instead of hiding it")
        report["reproducibility"] = {
            "status": "PASS",
            "independent_phase_count": 2,
            "byte_identical_native_role_count": 2,
            "compiler_process_count": len(report["processes"]),
            "source_apply_count": report["actual_source_apply_count"],
            "roles": {
                role: {
                    "sha256": phases[0]["native_outputs"][role]["owner"]["sha256"],
                    "bytes": phases[0]["native_outputs"][role]["owner"]["bytes"],
                    "phase_owner_count": 2,
                    "byte_identical": True,
                }
                for role in ("engine", "bridge")
            },
        }
        for path, pin in SOURCE_OWNERS.items():
            require(checked_read(path, pin[0], pin[1]) == retained["originals"][path],
                    "never change the original first-party Zig engine or bridge")
        renewed, _ = verify_context(source_pin, protocol_pin, contract_pin)
        require(renewed == _contract,
                "reject an independently frozen context changed during native build")
        report["status"] = "PASS"
    except Exception as error:
        report["actual_build_process_count"] = len(report["processes"])
        report["status"] = "FAIL"
        report["error"] = {
            "type": type(error).__name__, "message": str(error),
        }
    publication = publish_report(report, selected)
    return (0 if report["status"] == "PASS" else 1), publication


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    options = parser.parse_args()
    try:
        require(sys.implementation.name == "cpython"
                and tuple(sys.version_info[:3]) == (3, 14, 6)
                and sys.executable == PYTHON
                and sys.flags.isolated == 1
                and sys.dont_write_bytecode is True,
                "run only under isolated stable CPython 3.14.6")
        valid_digest(options.source_sha256, "Zig V12 source")
        valid_digest(options.protocol_sha256, "Zig V12 protocol")
        if options.contract_sha256 is not None:
            valid_digest(options.contract_sha256, "Zig V12 contract")
        if options.self_test:
            require(options.contract_sha256 is not None and options.label is None,
                    "fully caller-pin the wholly synthetic V12 source-only test")
            result = self_test()
            exit_code = 0
        elif options.render_contract:
            require(options.contract_sha256 is None and options.label is None,
                    "read-only contract rendering cannot run a source build")
            result, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256)
            exit_code = 0
        elif options.verify_frozen_context:
            require(options.contract_sha256 is not None and options.label is None,
                    "fully pin source-only context without supplying a build label")
            contract, _ = verify_context(options.source_sha256,
                                         options.protocol_sha256,
                                         options.contract_sha256)
            require(contract["phase_boundary"] == expected_boundary(),
                    "reject a build, candidate, archive inflation, or holdout access")
            result = {
                "schema": SCHEMA + "-read-only-frozen-context",
                "status": "PASS", "version": 12,
                "source_sha256": options.source_sha256,
                "protocol_sha256": options.protocol_sha256,
                "contract_sha256": options.contract_sha256,
                "historical_overview_version": 31,
                "historical_v30_evidence_owner_count": 149,
                "historical_v30_authenticated_reference_count": 154,
                "historical_v31_evidence_owner_count":
                    HISTORICAL_V31_EVIDENCE_OWNERS,
                "historical_v31_authenticated_reference_count":
                    HISTORICAL_V31_HISTORY_REFERENCES,
                "actual_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
                "authenticated_history_reference_count": CURRENT_HISTORY_REFERENCES,
                "historical_rust_v12_build_evidence_owner_count": 2,
                "new_actual_rust_v4_matching_evidence_owner_count": 2,
                "actual_rust_v12_build_status": "PASS",
                "actual_rust_v12_build_process_count": 28,
                "actual_rust_v12_source_build_candidate_correctness":
                    "NOT MEASURED",
                "actual_rust_v12_matching_status": "FAIL",
                "actual_rust_v12_semantic_mismatch_count": 1036,
                "actual_rust_v12_verified_passing_case_count": 8965,
                "actual_rust_v12_candidate_worker_count": 13,
                "actual_rust_v12_completed_suite_count": 13,
                "actual_rust_v12_infrastructure_failure_count": 0,
                "actual_rust_v12_original_native_targets_restored": True,
                "actual_rust_v4_matching_archive_sha256":
                    SUPPORT[RUST_MATCH_ARCHIVE][0],
                "actual_rust_v4_matching_receipt_sha256":
                    SUPPORT[RUST_MATCH_RECEIPT][0],
                "original_frozen_case_execution_count": 31237,
                "original_frozen_suite_count": 13,
                "original_frozen_private_waiver_count": 13,
                "additive_frozen_case_count": 50,
                "additive_reference_status": "NOT RUN",
                "additive_candidate_status": "NOT MEASURED",
                "frozen_independent_family_count": 6,
                "frozen_semantic_source_owner_count": 25,
                "frozen_zig_source_owner_count": 3,
                "historical_zig_semantic_mismatch_count": 2172,
                "historical_zig_verified_passing_case_count": 2847,
                "historical_zig_candidate_worker_count": 13,
                "historical_rust_semantic_mismatch_count": 1087,
                "historical_rust_verified_passing_case_count": 7438,
                "historical_c_semantic_mismatch_count": 1230,
                "corrected_bridge_sha256": SOURCE_OWNERS[ORIGINAL_BRIDGE][0],
                "corrected_bridge_bytes": SOURCE_OWNERS[ORIGINAL_BRIDGE][1],
                "corrected_bridge_byte_identical_to_original": True,
                "v1_conditional_overlay_used": False,
                "zig_v12_build_status": "NOT RUN",
                "future_phase_count": 2,
                "future_phase_process_count": EXPECTED_PHASE_PROCESS_COUNT,
                "future_total_process_count": EXPECTED_PROCESS_COUNT,
                **expected_boundary(),
                "workspace_mutations": 0,
            }
            exit_code = 0
        else:
            require(options.contract_sha256 is not None and options.label is not None,
                    "a real native build needs all frozen pins and a fresh explicit label")
            exit_code, result = run_build(options.source_sha256,
                                          options.protocol_sha256,
                                          options.contract_sha256,
                                          options.label)
        sys.stdout.buffer.write(canonical(result))
        return exit_code
    except (BuildError, OSError, TypeError, ValueError, OverflowError,
            UnicodeError, RecursionError, subprocess.SubprocessError) as error:
        sys.stderr.write("OWNED ZIG SCANNER SOURCE BUILD V12: FAIL: "
                         + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
