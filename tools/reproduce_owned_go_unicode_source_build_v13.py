#!/usr/bin/env python3
"""Freeze and, only when explicitly requested, build the owned Go repair."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
from dataclasses import dataclass
import errno
import fcntl
import gzip
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Sequence
import ctypes
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-go-unicode-source-build-v13"
SOURCE_RELATIVE = "tools/reproduce_owned_go_unicode_source_build_v13.py"
PROTOCOL_RELATIVE = "oracle/phase2/GO-UNICODE-SOURCE-BUILD-V13.md"
CONTRACT_RELATIVE = "oracle/phase2/go-unicode-source-build-v13.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
WORK_PREFIX = "rebar-phase2-native-build-v13-go-"
PHASE_NAMES = ("reference-a", "reference-b")
SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
PRIVATE_WAIVER_COUNT = 13
V33_EVIDENCE_OWNER_LOWER_BOUND = 155
V33_AUTHENTICATED_REFERENCE_LOWER_BOUND = 160
FINAL_PLANNED_HOLDOUT_CASES = 4_194_304
MAX_OWNER_BYTES = 64 * 1024 * 1024
MAX_PROCESS_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_INCLUDE = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
PINNED_GO = "/home/dev-user/.openai/go/bin/go"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
GO_ORIGINAL_SHA256 = "6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192"
GO_ORIGINAL_BYTES = 53_782
GO_DERIVED_SHA256 = "095fd5a69ab8c3667ba92dc1934bf91b650260f6e55f1ac876fd267f0d8bcf1a"
GO_DERIVED_BYTES = 53_803
ORIGINAL_BLOCK_SHA256 = "acae2de40ef8cdb23d07d68b6226015420809df6ba8b6eaee96ffa3baa5004d5"
CORRECTED_BLOCK_SHA256 = "07908b618132c14c8815feaf4e860274c7bedeefeddc45185533f18a8abb49ec"


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int | None


@dataclass(frozen=True, slots=True)
class Toolchain:
    identity: str
    path: str
    sha256: str
    size: int
    version: str
    executable: bool


GOAL = Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
GO_OWNERS = (
    Owner("candidates/go/engine.go", GO_ORIGINAL_SHA256, GO_ORIGINAL_BYTES),
    Owner("candidates/go/go.mod", "9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b", 44),
    Owner("candidates/go/py_bridge.c", "52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a", 39373),
    Owner("candidates/go_candidate.py", "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20", 31049),
)
GO_UNICODE_V1 = (
    Owner("tools/apply_owned_go_unicode_name_source_repair_v1.py", "a32f1062ef507903edc3a7cb5d0462853528e57582dd61e24e97fd1cc7737561", 89730),
    Owner("oracle/phase2/GO-UNICODE-NAME-SOURCE-REPAIR-V1.md", "fa738f2365a087d07d3860b23278fb20da00300e0d3eb3df09b6d3584f3b4c95", 7151),
    Owner("oracle/phase2/go-unicode-name-source-repair-v1.json", "b48d52c712288b037f2b2f88a69e658d8a389fd9ab469fb1999f80debc582d33", 13246),
)
V33 = (
    Owner("tools/render_candidate_current_overview_v33.py", "e81a1c032c550475c4a4ece9ae11b903d105d62e8666ce46b69138b260ca91d5", 75615),
    Owner("docs/evidence/candidate-current-overview-v33.inputs.json", "1f98790a6a31d8cdf298bf5fd13c6d4d14cfb44785e1e445d791c83557de921e", 106942),
    Owner("docs/evidence/candidate-current-overview-v33.json", "b56b5f0e09ff3aa3990b210934e1d73d1989bd03c6bb479a8a7abd66eb93a9a6", 380577),
    Owner("docs/evidence/candidate-current-overview-v33.svg", "203c15b16b74cf1dd8be3308677ddd67fa94a7a8411e5de38b43186647ccf858", 13068),
)
V34 = (
    Owner("tools/render_candidate_current_overview_v34.py", "cf4f7b0749d0e3aa6c15d4e5444762441265773fbb90c1ebbceff0f65e3e841f", 79364),
    Owner("docs/evidence/candidate-current-overview-v34.inputs.json", "d191ad36dd230b97c3d017f0d775a185c0a7f449adb27f7412c54c4d4308c8fc", 133398),
    Owner("docs/evidence/candidate-current-overview-v34.json", "09236e77646160009b322bb02f60652eeb0b13f2b1f9440bfef2e176644e9df4", 426458),
    Owner("docs/evidence/candidate-current-overview-v34.svg", "59ff6affa120980c8d25206a71d2b2377619e93796a6ca0f15a65229a87dffce", 10367),
)
NATIVE_V6 = (
    Owner("tools/reproduce_owned_native_source_build_v6.py", "2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc", 196660),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V6.md", "108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d", 10297),
    Owner("oracle/phase2/native-source-build-v6.json", "0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4", 29292),
)
CALLABLE_V1 = (
    Owner("tools/verify_python_re_callable_introspection_v1.py", "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653", 75608),
    Owner("oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md", "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8", 8952),
    Owner("oracle/phase1/p0-callable-introspection-v1.json", "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749),
)
CALLABLE_REFERENCE_V2 = (
    Owner("tools/run_owned_callable_introspection_reference_v2.py", "00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4", 86258),
    Owner("oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md", "1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f", 7487),
    Owner("oracle/phase1/callable-introspection-reference-v2.json", "0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42", 7253),
)
ZIG_V12 = (
    Owner("tools/reproduce_owned_zig_scanner_source_build_v12.py", "5192fa35dd0b13cb3bdddfc8f24c37d7e797d0b8463d000c4692c8131f33d1b6", 124781),
    Owner("oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V12.md", "f80743d8109402e5876792b6713237b1ab770e3286874dd5ae47fb56381131b1", 6531),
    Owner("oracle/phase2/zig-scanner-source-build-v12.json", "5abb6f60c7a9672e32d6f2980a109ccb15b7ef56e5cc3a81abda458109552c1a", 23611),
)
GO_BUILD_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v6-go-phase2-v6-publication-receipt.json", "f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca", 3262)
GO_MATCH_RECEIPT = Owner("oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures-publication-receipt.json", "a7352b7028348941cf0655ddc0e973ae43c6498be91139d47eb4d3555f90b3da", 4615)
RUST_MATCH_RECEIPT = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json", "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3", 4674)
C_MATCH_RECEIPT = Owner("oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json", "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9", 3482)
ZIG_MATCH_RECEIPT = Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba", 4534)
ZIG_BUILD_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2-publication-receipt.json", "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b", 2029)
ZIG_CORRECTED_MATCH_RECEIPT = Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures-publication-receipt.json", "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96", 4111)
CALLABLE_REFERENCE_RECEIPT = Owner("oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json", "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334", 3533)

TOOLCHAINS = (
    Toolchain("python", PINNED_PYTHON, "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016", 32387816, "CPython 3.14.6", True),
    Toolchain("python_header", PYTHON_INCLUDE + "/Python.h", "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f", 4399, "CPython 3.14.6", False),
    Toolchain("python_patchlevel", PYTHON_INCLUDE + "/patchlevel.h", "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95", 1773, "CPython 3.14.6", False),
    Toolchain("go", PINNED_GO, "d68b7abbc40d0844f673f6cf06ae3cded225c50437c6454fa37ef178d079fe65", 15434598, "go1.26.3 linux/amd64", True),
    Toolchain("gcc", PINNED_GCC, "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26", 1023032, "GCC 13", True),
    Toolchain("readelf", PINNED_READELF, "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0", 789280, "GNU readelf", True),
)

GO_EXPORTS = (
    "rebar_go_compile", "rebar_go_release", "rebar_go_group_count",
    "rebar_go_flags", "rebar_go_name_count", "rebar_go_name_group",
    "rebar_go_name_length", "rebar_go_copy_name", "rebar_go_execute",
)
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "go_version", "build_go_engine",
    "build_go_bridge", "engine_dynamic", "engine_symbols", "engine_sections",
    "engine_notes", "bridge_dynamic", "bridge_symbols", "bridge_sections",
    "bridge_notes",
)
EXPECTED_PHASE_PROCESS_COUNT = len(PROCESS_ROLES)
EXPECTED_PROCESS_COUNT = len(PHASE_NAMES) * EXPECTED_PHASE_PROCESS_COUNT
GO_INFRASTRUCTURE_SUITES = (
    "scanner_verbose_v1", "public_types_v1", "shape_v2", "threaded_pattern_v1",
)
FORBIDDEN_ENGINE_TOKENS = (
    b'"regexp"', b'"regexp/syntax"', b"github.com/", b"golang.org/x/",
    b"pcre", b"oniguruma", b"hyperscan", b"_sre",
    b"candidates/rust", b"candidates/zig", b"candidates/cpp",
    b"candidates/fortran", b'PyImport_ImportModule("re")',
    b'PyImport_ImportModule("_sre")',
)
ORIGINAL_COPY_BLOCK = b'''//export rebar_go_copy_name
func rebar_go_copy_name(
\traw C.uint64_t,
\tindex C.size_t,
\tdestination *C.uint8_t,
\tcapacity C.size_t,
) C.size_t {
\tvalue, ok := programFromHandle(raw)
\tif !ok || uint64(index) >= uint64(len(value.names)) {
\t\treturn 0
\t}
\tname := value.names[int(index)].name
\tif uint64(capacity) < uint64(len(name)) ||
\t\t(len(name) != 0 && destination == nil) {
\t\treturn 0
\t}
\tif len(name) != 0 {
\t\ttarget := unsafe.Slice(destination, len(name))
\t\tfor offset := range name {
\t\t\ttarget[offset] = C.uint8_t(name[offset])
\t\t}
\t}
\treturn C.size_t(len(name))
}

'''
CORRECTED_COPY_BLOCK = ORIGINAL_COPY_BLOCK.replace(
    b"\t\tfor offset := range name {\n",
    b"\t\tfor offset := 0; offset < len(name); offset++ {\n", 1,
)


class BuildError(Exception):
    """An independently checked frozen build obligation failed."""


class ForbiddenEffect(BuildError):
    """A source-only operation attempted a physically prohibited effect."""


def require(condition: object, explanation: str) -> None:
    if not condition:
        raise BuildError(explanation)


def digest(data: bytes) -> str:
    require(type(data) is bytes, "hash only exact owned bytes")
    return hashlib.sha256(data).hexdigest()


def checked_digest(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require an exact lowercase SHA-256 for " + label)
    return value


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                           allow_nan=False, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise BuildError("reject noncanonical or nonfinite frozen JSON") from error


def strict_json(data: bytes, label: str) -> dict[str, Any]:
    require(type(data) is bytes and 0 < len(data) <= MAX_OWNER_BYTES,
            "bound exact JSON owner: " + label)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "reject a duplicate JSON field: " + key)
            result[key] = value
        return result

    def constant(value: str) -> None:
        raise BuildError("reject a nonfinite JSON value: " + value)

    try:
        result = json.loads(data.decode("utf-8", "strict"),
                            object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise BuildError("reject invalid JSON owner: " + label) from error
    require(type(result) is dict, "require a JSON object: " + label)
    return result


def checked_relative(value: object) -> tuple[str, ...]:
    require(type(value) is str and value and "\\" not in value
            and "\x00" not in value and not value.startswith("/"),
            "require a safe owned repository-relative path")
    parsed = PurePosixPath(value)
    parts = parsed.parts
    require(str(parsed) == value and parts
            and all(part not in ("", ".", "..") for part in parts),
            "reject traversal, broad, normalized, or alternate owner paths")
    require(not value.endswith(".gz"), "never open or inspect a matching or source-build archive")
    return parts


def owner_document(owner: Owner) -> dict[str, Any]:
    result: dict[str, Any] = {"path": owner.path, "sha256": owner.sha256}
    if owner.size is not None:
        result["bytes"] = owner.size
    return result


def toolchain_document(tool: Toolchain) -> dict[str, Any]:
    return {"id": tool.identity, "path": tool.path, "sha256": tool.sha256,
            "bytes": tool.size, "version": tool.version,
            "executable": tool.executable}


def read_owner(owner: Owner) -> tuple[bytes, dict[str, Any]]:
    checked_digest(owner.sha256, owner.path)
    parts = checked_relative(owner.path)
    if parts[0] == "candidates":
        require(owner.path in {item.path for item in GO_OWNERS},
                "never inspect another candidate or a canonical native target")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    folders: list[int] = []
    handle: int | None = None
    try:
        folder = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
        folders.append(folder)
        for part in parts[:-1]:
            folder = os.open(part, flags | getattr(os, "O_DIRECTORY", 0), dir_fd=folder)
            folders.append(folder)
        handle = os.open(parts[-1], flags, dir_fd=folder)
        visible = os.stat(parts[-1], dir_fd=folder, follow_symlinks=False)
        before = os.fstat(handle)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
                and before.st_nlink == 1 and 0 < before.st_size <= MAX_OWNER_BYTES
                and (owner.size is None or before.st_size == owner.size)
                and not (stat.S_IMODE(before.st_mode) & 0o022)
                and (before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink)
                == (visible.st_dev, visible.st_ino, visible.st_size, visible.st_uid, visible.st_nlink),
                "reject a substituted, mutable, linked, or foreign repository owner: " + owner.path)
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(handle, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk), "reject a truncated descriptor-bound owner")
            pieces.append(chunk)
            remaining -= len(chunk)
        require(os.read(handle, 1) == b"", "reject an appended owner")
        data = b"".join(pieces)
        after = os.fstat(handle)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and digest(data) == owner.sha256,
                "reject an owner changed during complete descriptor-bound authentication: " + owner.path)
        return data, {**owner_document(Owner(owner.path, owner.sha256, after.st_size)),
                      "device": after.st_dev, "inode": after.st_ino,
                      "mode": stat.S_IMODE(after.st_mode), "uid": after.st_uid,
                      "nlink": after.st_nlink}
    except OSError as error:
        raise BuildError("cannot authenticate frozen repository owner: " + owner.path) from error
    finally:
        if handle is not None:
            os.close(handle)
        for folder in reversed(folders):
            os.close(folder)


def read_toolchain(tool: Toolchain) -> dict[str, Any]:
    checked_digest(tool.sha256, tool.identity)
    require(type(tool.path) is str and tool.path.startswith("/")
            and "\x00" not in tool.path and not tool.path.endswith(".gz"),
            "require the exact frozen absolute toolchain owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle: int | None = None
    try:
        handle = os.open(tool.path, flags)
        before = os.fstat(handle)
        visible = os.stat(tool.path, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                and before.st_size == tool.size
                and not (stat.S_IMODE(before.st_mode) & 0o022)
                and (not tool.executable or bool(before.st_mode & 0o111))
                and (before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink)
                == (visible.st_dev, visible.st_ino, visible.st_size, visible.st_uid, visible.st_nlink),
                "reject a substituted, linked, writable, or nonexecutable toolchain: " + tool.identity)
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(handle, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk), "reject a truncated pinned toolchain")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(handle, 1) == b"", "reject a growing pinned toolchain")
        after = os.fstat(handle)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and hasher.hexdigest() == tool.sha256,
                "reject changed complete pinned toolchain bytes: " + tool.identity)
        return {**toolchain_document(tool), "device": after.st_dev,
                "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
                "uid": after.st_uid, "nlink": after.st_nlink}
    except OSError as error:
        raise BuildError("cannot authenticate pinned toolchain: " + tool.identity) from error
    finally:
        if handle is not None:
            os.close(handle)


def runtime() -> None:
    require(sys.implementation.name == "cpython"
            and sys.version_info[:3] == (3, 14, 6)
            and sys.executable == PINNED_PYTHON
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "use only the pinned isolated CPython 3.14.6 with bytecode disabled")


def phase_boundary() -> dict[str, Any]:
    return {
        "actual_build_process_count": 0,
        "actual_source_apply_count": 0,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_reference_processes_started": 0,
        "actual_network_requests": 0,
        "actual_matching_archives_opened": 0,
        "actual_matching_archive_bytes_read": 0,
        "actual_source_build_archives_opened": 0,
        "actual_source_build_archive_bytes_read": 0,
        "actual_hidden_cases_read": 0,
        "actual_holdout_cases_read": 0,
        "actual_benchmark_files_read": 0,
        "actual_clock_samples": 0,
        "actual_timing_trials_run": 0,
        "actual_threads_started": 0,
        "actual_workspace_mutations": 0,
        "candidate_correctness": "NOT MEASURED",
        "corrected_go_matching": "NOT MEASURED",
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "final_comparison_cases_generated": False,
        "winner_selected": False,
    }


def checked_workdir(value: object) -> str:
    require(type(value) is str and value.startswith("/tmp/" + WORK_PREFIX)
            and value == value.rstrip("/") and "\\" not in value and "\x00" not in value
            and len(value.split("/")) == 3
            and all(part not in ("", ".", "..") for part in value.split("/")[1:])
            and len(value) <= 240
            and bool(value[len("/tmp/" + WORK_PREFIX):])
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789_-"
                    for ch in value[len("/tmp/" + WORK_PREFIX):]),
            "require one fresh bounded Go-only V13 private root directly under /tmp")
    return value


def checked_label(value: object) -> str:
    require(type(value) is str and 1 <= len(value) <= 80
            and value[0].isalnum() and value[-1].isalnum()
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in value),
            "require an exact lowercase, bounded, nontraversing publication label")
    return value


def phase_paths(workdir: str, phase: str) -> dict[str, Path]:
    checked_workdir(workdir)
    require(phase in PHASE_NAMES, "require exactly the two independent Go phases")
    base = Path(workdir) / phase
    source = base / "source"
    native = base / "native"
    return {
        "base": base, "source": source, "native": native,
        "temporary": base / "temporary",
        "go_build_cache": base / "go-build-cache",
        "go_module_cache": base / "go-module-cache",
        "go_module_directory": base / "go-engine-package",
        "original_go_directory": source / "candidates" / "go",
        "artifact_engine": native / "_go_engine.so",
        "artifact_generated_header": native / "_go_engine.h",
        "artifact_bridge": native / "_go_bridge.cpython-314-x86_64-linux-gnu.so",
    }


def prefix_flags(workdir: str) -> list[str]:
    return ["-ffile-prefix-map=" + str(phase_paths(workdir, phase)["source"])
            + "=/rebar-phase2-v13-owned-go-source" for phase in PHASE_NAMES]


def build_environment(workdir: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, phase)
    return {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1", "TMPDIR": str(paths["temporary"]),
        "GOPROXY": "off", "GOSUMDB": "off", "GOWORK": "off", "GOENV": "off",
        "GOTOOLCHAIN": "local", "CGO_ENABLED": "1", "CC": PINNED_GCC,
        "GOCACHE": str(paths["go_build_cache"]),
        "GOMODCACHE": str(paths["go_module_cache"]), "GOFLAGS": "-mod=readonly",
    }


def planned_commands(workdir: str, phase: str) -> dict[str, list[str]]:
    paths = phase_paths(workdir, phase)
    engine = str(paths["artifact_engine"])
    bridge = str(paths["artifact_bridge"])
    header = str(paths["artifact_generated_header"])
    commands: dict[str, list[str]] = {
        "readelf_version": [PINNED_READELF, "--version"],
        "gcc_version": [PINNED_GCC, "--version"],
        "go_version": [PINNED_GO, "version"],
        "build_go_engine": [PINNED_GO, "build", "-buildmode=c-shared", "-trimpath",
                            "-buildvcs=false", "-ldflags=-buildid=", "-o", engine, "."],
        "build_go_bridge": [PINNED_GCC, "-D_GNU_SOURCE", "-std=c11", "-shared",
                            "-fPIC", "-O3", "-Wall", "-Wextra", "-Werror",
                            "-Wl,--build-id=sha1", *prefix_flags(workdir),
                            "-I" + PYTHON_INCLUDE, "-I" + str(paths["native"]),
                            "-include", header,
                            str(paths["source"] / "candidates/go/py_bridge.c"),
                            "-L" + str(paths["native"]), "-l:_go_engine.so",
                            "-Wl,-rpath,$ORIGIN", "-o", bridge],
    }
    for kind, artifact in (("engine", engine), ("bridge", bridge)):
        for role, option in (("dynamic", "--dynamic"), ("symbols", "--dyn-syms"),
                             ("sections", "--sections"), ("notes", "--notes")):
            commands[kind + "_" + role] = [PINNED_READELF, option, "--wide", artifact]
    require(tuple(commands) == PROCESS_ROLES,
            "freeze the exact ordered 13 original Go cgo build and ELF-inspection roles")
    return commands


def checked_command(name: object, argv: object, workdir: str, phase: str) -> list[str]:
    commands = planned_commands(workdir, phase)
    require(type(name) is str and name in commands and type(argv) is list
            and all(type(item) is str and "\x00" not in item for item in argv)
            and argv == commands[name]
            and argv[0] in (PINNED_GO, PINNED_GCC, PINNED_READELF),
            "reject a substituted, shell, network, third-party, or cross-phase compiler command")
    if name == "build_go_bridge":
        header = str(phase_paths(workdir, phase)["artifact_generated_header"])
        require(argv.count("-D_GNU_SOURCE") == 1 and argv.count("-include") == 1
                and argv.count(header) == 1
                and argv.index("-D_GNU_SOURCE") < argv.index("-include")
                and argv[argv.index("-include") + 1] == header
                and all(flag in argv for flag in ("-Wall", "-Wextra", "-Werror"))
                and "-Wl,-rpath,$ORIGIN" in argv,
                "force-include only this phase's genuine generated Go header")
    return list(argv)


def command_working_directory(workdir: str, phase: str, role: str) -> Path:
    paths = phase_paths(workdir, phase)
    require(role in PROCESS_ROLES, "reject an invented process role")
    return paths["go_module_directory"] if role == "build_go_engine" else paths["base"]


def sanitized(value: str, workdir: str) -> str:
    require(type(value) is str, "sanitize only an exact string")
    return value.replace(checked_workdir(workdir), "<FRESH_PRIVATE_TMP>")


def command_templates() -> dict[str, Any]:
    example = "/tmp/" + WORK_PREFIX + "frozen-example"
    return {phase: {
        "working_directories": {
            role: sanitized(str(command_working_directory(example, phase, role)), example)
            for role in PROCESS_ROLES
        },
        "commands": {
            role: [sanitized(part, example) for part in planned_commands(example, phase)[role]]
            for role in PROCESS_ROLES
        },
        "environment": {
            key: sanitized(value, example)
            for key, value in sorted(build_environment(example, phase).items())
        },
    } for phase in PHASE_NAMES}


def validate_no_delegation(data: bytes, label: str) -> None:
    lower = data.lower()
    for token in FORBIDDEN_ENGINE_TOKENS:
        require(token.lower() not in lower,
                "reject external, stdlib, or cross-family matching in " + label)


def corrected_source(data: bytes) -> bytes:
    require(type(data) is bytes and len(data) == GO_ORIGINAL_BYTES
            and digest(data) == GO_ORIGINAL_SHA256,
            "require the exact authenticated original first-party Go engine")
    require(len(ORIGINAL_COPY_BLOCK) == 571
            and digest(ORIGINAL_COPY_BLOCK) == ORIGINAL_BLOCK_SHA256
            and len(CORRECTED_COPY_BLOCK) == 592
            and digest(CORRECTED_COPY_BLOCK) == CORRECTED_BLOCK_SHA256
            and data.count(ORIGINAL_COPY_BLOCK) == 1
            and data.count(CORRECTED_COPY_BLOCK) == 0,
            "anchor exactly one complete authenticated Go Unicode-name export")
    for name in GO_EXPORTS:
        require(data.count(("//export " + name + "\n").encode("ascii")) == 1,
                "preserve each of the nine independently owned Go cgo exports")
    validate_no_delegation(data, "original Go engine")
    derived = data.replace(ORIGINAL_COPY_BLOCK, CORRECTED_COPY_BLOCK, 1)
    require(len(derived) == GO_DERIVED_BYTES and digest(derived) == GO_DERIVED_SHA256
            and derived.count(CORRECTED_COPY_BLOCK) == 1
            and derived.count(ORIGINAL_COPY_BLOCK) == 0,
            "derive only the exact frozen byte-wise Go Unicode-name correction")
    validate_no_delegation(derived, "corrected Go engine")
    return derived


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    source_pin = checked_digest(source_pin, "V13 source")
    protocol_pin = checked_digest(protocol_pin, "V13 protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 13,
        "phase": "SOURCE FREEZE; CORRECTED GO BUILD NOT RUN",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "goal": owner_document(GOAL),
        "phase_one": owner_document(PHASE_ONE),
        "runtime": {"implementation": "cpython", "version": "3.14.6",
                    "python": PINNED_PYTHON,
                    "python_sha256": TOOLCHAINS[0].sha256,
                    "isolated": True, "bytecode_writes": False},
        "first_party_go": {
            "family": "go", "owner_count": len(GO_OWNERS),
            "owners": [owner_document(owner) for owner in GO_OWNERS],
            "required_cgo_exports": list(GO_EXPORTS),
            "required_cgo_export_count": len(GO_EXPORTS),
            "go_module_dependencies": 0, "external_regex_dependencies": 0,
            "cross_family_engine_dependencies": 0,
            "stdlib_regex_engine_dependencies": 0,
            "go_regexp_delegation_allowed": False,
            "python_re_delegation_allowed": False,
            "original_adapter_modified": False,
            "original_engine_modified": False,
        },
        "authenticated_unicode_repair": {
            "source_freeze": [owner_document(owner) for owner in GO_UNICODE_V1],
            "original_engine_sha256": GO_ORIGINAL_SHA256,
            "original_engine_bytes": GO_ORIGINAL_BYTES,
            "derived_engine_sha256": GO_DERIVED_SHA256,
            "derived_engine_bytes": GO_DERIVED_BYTES,
            "original_complete_export_sha256": ORIGINAL_BLOCK_SHA256,
            "corrected_complete_export_sha256": CORRECTED_BLOCK_SHA256,
            "original_complete_export_bytes": len(ORIGINAL_COPY_BLOCK),
            "corrected_complete_export_bytes": len(CORRECTED_COPY_BLOCK),
            "original_statement": "for offset := range name {",
            "corrected_statement": "for offset := 0; offset < len(name); offset++ {",
            "anchored_complete_export_count": 1,
            "matching_proven": False,
        },
        "pinned_toolchains": [toolchain_document(tool) for tool in TOOLCHAINS],
        "historical_v6_first_party_go_source_build": {
            "source_freeze": [owner_document(owner) for owner in NATIVE_V6],
            "receipt": owner_document(GO_BUILD_RECEIPT),
            "actual_process_count": 26, "matching_test_status": "NOT MEASURED",
            "archive_opened_by_v13": False,
        },
        "historical_v33_immutable_lower_bound": {
            "overview": [owner_document(owner) for owner in V33],
            "repository_evidence_owner_count_at_v33": V33_EVIDENCE_OWNER_LOWER_BOUND,
            "authenticated_reference_count_at_v33": V33_AUTHENTICATED_REFERENCE_LOWER_BOUND,
            "counts_describe_immutable_v33_not_current_head": True,
            "append_only_later_evidence_permitted": True,
            "original_case_denominator": CASE_DENOMINATOR,
            "suite_count": SUITE_COUNT,
            "private_waiver_count": PRIVATE_WAIVER_COUNT,
            "historical_go_mismatch_count": 4518,
            "historical_go_verified_passing_case_count": 128,
            "historical_go_infrastructure_failure_suites": list(GO_INFRASTRUCTURE_SUITES),
            "historical_go_native_crash_proven": False,
            "historical_rust_mismatch_count": 1036,
            "historical_c_mismatch_count": 1230,
            "historical_zig_mismatch_count": 2172,
            "v12_zig_corrected_build_process_count": 26,
            "v12_zig_corrected_matching_at_v33": "NOT MEASURED",
            "v12_zig_corrected_candidate_workers_at_v33": 0,
            "v12_zig_source_freeze": [owner_document(owner) for owner in ZIG_V12],
            "v12_zig_build_receipt": owner_document(ZIG_BUILD_RECEIPT),
            "matching_receipts_read_without_opening_archives": [
                owner_document(owner) for owner in
                (GO_MATCH_RECEIPT, RUST_MATCH_RECEIPT, C_MATCH_RECEIPT, ZIG_MATCH_RECEIPT)
            ],
        },
        "historical_v34_immutable_lower_bound": {
            "overview": [owner_document(owner) for owner in V34],
            "repository_evidence_owner_count_at_v34": 157,
            "authenticated_reference_count_at_v34": 162,
            "counts_describe_immutable_v34_not_current_head": True,
            "append_only_later_evidence_permitted": True,
            "corrected_zig_matching_status_at_v34": "FAIL",
            "corrected_zig_semantic_mismatch_count_at_v34": 1764,
            "corrected_zig_verified_passing_case_count_at_v34": 3711,
            "corrected_zig_actual_candidate_workers_at_v34": 13,
            "corrected_zig_infrastructure_failure_count_at_v34": 0,
            "callable_reference_status_at_immutable_v34": "NOT RUN",
            "callable_reference_case_executions_at_immutable_v34": 0,
        },
        "latest_authenticated_corrected_zig_v3_at_freeze": {
            "receipt": owner_document(ZIG_CORRECTED_MATCH_RECEIPT),
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1764,
            "verified_passing_case_count": 3711,
            "actual_candidate_workers": 13,
            "infrastructure_failure_count": 0,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "resulting_evidence_owner_lower_bound": 157,
            "resulting_authenticated_reference_lower_bound": 162,
            "archive_sha256_authenticated_from_receipt_only":
                "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b",
            "archive_compressed_bytes_authenticated_from_receipt_only": 3722337,
            "archive_opened_by_v13": False,
            "append_only_later_results_permitted": True,
        },
        "separately_frozen_callable_obligations": {
            "source_freeze": [owner_document(owner) for owner in CALLABLE_V1],
            "case_count": 50, "included_in_original_denominator": False,
            "reference": "PASS", "verified_reference_case_count": 50,
            "actual_independent_reference_process_count": 2,
            "actual_independent_reference_process_ids": [81, 82],
            "candidate_execution": "NOT RUN", "candidate": "NOT MEASURED",
        },
        "latest_authenticated_callable_reference_v2_at_freeze": {
            "source_freeze": [owner_document(owner) for owner in CALLABLE_REFERENCE_V2],
            "actual_reference_receipt": owner_document(CALLABLE_REFERENCE_RECEIPT),
            "reference_status": "PASS",
            "additional_reference_case_count": 50,
            "reference_failure_count": 0,
            "actual_independent_reference_process_count": 2,
            "actual_distinct_reference_process_ids": [81, 82],
            "original_case_denominator": CASE_DENOMINATOR,
            "additional_cases_included_in_original_denominator": False,
            "original_suite_count": SUITE_COUNT,
            "original_named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "candidate_execution": "NOT RUN",
            "candidate_introspection": "NOT MEASURED",
            "candidate_processes_started": 0,
            "actual_evidence_owner_lower_bound": 159,
            "actual_authenticated_reference_lower_bound": 164,
            "archive_sha256_authenticated_from_receipt_only":
                "7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c",
            "archive_compressed_bytes_authenticated_from_receipt_only": 8538,
            "archive_opened_by_v13": False,
            "append_only_later_results_permitted": True,
        },
        "future_explicit_build_only": {
            "requires_explicit_build_flag": True,
            "private_root_parent": "/tmp",
            "private_root_prefix": WORK_PREFIX,
            "phase_names": list(PHASE_NAMES),
            "phase_count_only_after_success": len(PHASE_NAMES),
            "ordered_process_roles_per_phase": list(PROCESS_ROLES),
            "phase_process_count_only_after_success": EXPECTED_PHASE_PROCESS_COUNT,
            "total_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
            "actual_process_count_in_source_freeze": 0,
            "actual_source_apply_count_in_source_freeze": 0,
            "separate_private_go_build_and_module_caches_required": True,
            "go_proxy_network_allowed": False,
            "go_module_package_per_phase_required": True,
            "force_include_real_phase_local_go_header": True,
            "strict_bridge_warnings_are_errors": True,
            "all_three_native_outputs_must_be_byte_identical": True,
            "actual_candidate_processes_allowed": False,
            "deterministic_exclusive_durable_publication_required": True,
            "failure_evidence_must_be_preserved": True,
            "command_templates": command_templates(),
        },
        "phase_boundary": phase_boundary(),
    }


class SourceWall:
    """Physically disable I/O, process, native, time, and network effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.categories: set[str] = set()

    def __enter__(self) -> SourceWall:
        targets: tuple[tuple[Any, str, str], ...] = (
            (builtins, "open", "filesystem"),
            (builtins, "__import__", "imports"),
            (os, "open", "filesystem"), (os, "stat", "filesystem"),
            (os, "lstat", "filesystem"), (os, "listdir", "filesystem"),
            (os, "scandir", "filesystem"), (os, "mkdir", "workspace-mutations"),
            (os, "makedirs", "workspace-mutations"),
            (os, "unlink", "workspace-mutations"),
            (os, "remove", "workspace-mutations"),
            (os, "rmdir", "workspace-mutations"),
            (os, "rename", "workspace-mutations"),
            (os, "replace", "workspace-mutations"),
            (os, "chmod", "workspace-mutations"),
            (os, "system", "processes"),
            (os, "posix_spawn", "processes"),
            (os, "posix_spawnp", "processes"),
            (os, "fork", "processes"),
            (Path, "open", "filesystem"), (Path, "read_bytes", "filesystem"),
            (Path, "read_text", "filesystem"), (Path, "write_bytes", "workspace-mutations"),
            (Path, "write_text", "workspace-mutations"),
            (Path, "stat", "filesystem"), (Path, "lstat", "filesystem"),
            (Path, "mkdir", "workspace-mutations"),
            (Path, "unlink", "workspace-mutations"),
            (Path, "rename", "workspace-mutations"),
            (Path, "replace", "workspace-mutations"),
            (subprocess, "run", "processes"),
            (subprocess, "Popen", "processes"),
            (socket, "socket", "network"),
            (socket, "create_connection", "network"),
            (ctypes, "CDLL", "native-loads"),
            (ctypes, "PyDLL", "native-loads"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clocks"), (time, "time_ns", "clocks"),
            (time, "monotonic", "clocks"), (time, "monotonic_ns", "clocks"),
            (time, "perf_counter", "clocks"),
            (time, "perf_counter_ns", "clocks"), (time, "sleep", "clocks"),
            (gzip, "open", "archives"), (gzip, "compress", "archives"),
            (gzip, "decompress", "archives"), (gzip, "GzipFile", "archives"),
            (zlib, "compress", "archives"), (zlib, "decompress", "archives"),
            (zlib, "compressobj", "archives"), (zlib, "decompressobj", "archives"),
            (tempfile, "mkdtemp", "workspace-mutations"),
            (tempfile, "mkstemp", "workspace-mutations"),
            (tempfile, "NamedTemporaryFile", "workspace-mutations"),
            (importlib, "import_module", "imports"),
            (signal, "signal", "signals"), (fcntl, "flock", "locks"),
        )
        try:
            for owner, name, category in targets:
                if not hasattr(owner, name):
                    continue
                original = getattr(owner, name)

                def deny(*args: Any, _category: str = category,
                         _name: str = name, **kwargs: Any) -> Any:
                    raise ForbiddenEffect("source-only wall blocked " + _category + ": " + _name)

                self.saved.append((owner, name, original))
                setattr(owner, name, deny)
                self.categories.add(category)
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, kind: Any, value: Any, traceback: Any) -> bool:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)
        self.saved.clear()
        return False


def read_contract_owners(source_pin: str, protocol_pin: str,
                         contract_pin: str) -> dict[str, Any]:
    runtime()
    pins = (
        Owner(SOURCE_RELATIVE, checked_digest(source_pin, "source"), None),
        Owner(PROTOCOL_RELATIVE, checked_digest(protocol_pin, "protocol"), None),
        Owner(CONTRACT_RELATIVE, checked_digest(contract_pin, "contract"), None),
    )
    raw: dict[str, bytes] = {}
    for owner in pins:
        data, _ = read_owner(owner)
        raw[owner.path] = data
    result = strict_json(raw[CONTRACT_RELATIVE], "V13 canonical contract")
    require(canonical(result) == raw[CONTRACT_RELATIVE]
            and result == contract_document(source_pin, protocol_pin),
            "require the exact caller-pinned, complete canonical V13 source contract")
    return result


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    read_contract_owners(source_pin, protocol_pin, contract_pin)
    private = "/tmp/" + WORK_PREFIX + "synthetic-self-test"
    first = planned_commands(private, PHASE_NAMES[0])
    second = planned_commands(private, PHASE_NAMES[1])
    positive_count = 0
    negative_count = 0

    def accept(condition: object, explanation: str) -> None:
        nonlocal positive_count
        require(condition, explanation)
        positive_count += 1

    def reject(operation: Any, explanation: str) -> None:
        nonlocal negative_count
        try:
            operation()
        except (BuildError, ForbiddenEffect, OSError, TypeError, ValueError):
            negative_count += 1
            return
        raise BuildError("negative self-test unexpectedly passed: " + explanation)

    accept(len(PROCESS_ROLES) == 13, "freeze exactly 13 Go roles per phase")
    accept(EXPECTED_PROCESS_COUNT == 26, "derive 26 only from two complete future phases")
    accept(len(set(PROCESS_ROLES)) == len(PROCESS_ROLES), "reject duplicate process roles")
    accept(len(set(GO_EXPORTS)) == 9, "preserve exactly nine Go exports")
    accept(digest(ORIGINAL_COPY_BLOCK) == ORIGINAL_BLOCK_SHA256, "pin the original full export")
    accept(digest(CORRECTED_COPY_BLOCK) == CORRECTED_BLOCK_SHA256, "pin the corrected full export")
    accept(len(ORIGINAL_COPY_BLOCK) == 571, "pin complete original export bytes")
    accept(len(CORRECTED_COPY_BLOCK) == 592, "pin complete corrected export bytes")
    accept(tuple(first) == PROCESS_ROLES, "freeze reference-a exact roles")
    accept(tuple(second) == PROCESS_ROLES, "freeze reference-b exact roles")
    for role in PROCESS_ROLES:
        accept(checked_command(role, first[role], private, "reference-a") == first[role],
               "accept every exact reference-a role")
        accept(checked_command(role, second[role], private, "reference-b") == second[role],
               "accept every exact reference-b role")
        if first[role] != second[role]:
            reject(lambda r=role: checked_command(r, second[r], private, "reference-a"),
                   "reject a phase-swapped " + role)
        else:
            accept(role in ("readelf_version", "gcc_version", "go_version"),
                   "only phase-independent version commands can match")
    for phase in PHASE_NAMES:
        paths = phase_paths(private, phase)
        environment = build_environment(private, phase)
        accept(environment["GOPROXY"] == "off", "disable Go proxy traffic")
        accept(environment["GOSUMDB"] == "off", "disable Go checksum traffic")
        accept(environment["GOWORK"] == "off", "disable parent workspaces")
        accept(environment["GOENV"] == "off", "disable inherited Go environment")
        accept(environment["GOTOOLCHAIN"] == "local", "forbid downloading a compiler")
        accept(environment["GOFLAGS"] == "-mod=readonly", "forbid module resolution changes")
        accept(environment["CC"] == PINNED_GCC, "use the exact pinned cgo compiler")
        accept(command_working_directory(private, phase, "build_go_engine")
               == paths["go_module_directory"], "compile inside this phase's private module")
        accept(paths["artifact_generated_header"].parent == paths["native"],
               "generate the header in the phase-local native directory")
    accept(phase_paths(private, "reference-a")["go_build_cache"]
           != phase_paths(private, "reference-b")["go_build_cache"],
           "separate both Go build caches")
    accept(phase_paths(private, "reference-a")["go_module_cache"]
           != phase_paths(private, "reference-b")["go_module_cache"],
           "separate both Go module caches")
    accept(phase_boundary()["actual_build_process_count"] == 0,
           "never manufacture a source-freeze build count")
    accept(phase_boundary()["holdout"] == "NOT OPENED", "do not open the holdout")
    accept(strict_json(canonical({"a": 1, "b": [2]}), "synthetic") == {"a": 1, "b": [2]},
           "accept canonical strict JSON")
    for invalid in (
        "", "/", "/tmp", "/tmp/" + WORK_PREFIX,
        "/tmp/" + WORK_PREFIX + "x/child", "/tmp/other-go-x",
        "/tmp/" + WORK_PREFIX + "../escape", "/tmp/" + WORK_PREFIX + "x\\bad",
    ):
        reject(lambda item=invalid: checked_workdir(item), "reject unsafe work root")
    for invalid in ("", ".", "..", "../x", "/x", "a//b", "a/../b", "x.gz", "x\\y"):
        reject(lambda item=invalid: checked_relative(item), "reject unsafe or archive path")
    for invalid in ("", "-bad", "bad-", "UPPER", "../escape", "two_words", "a" * 81):
        reject(lambda item=invalid: checked_label(item), "reject unsafe evidence label")
    reject(lambda: strict_json(b'{"a":1,"a":2}\n', "duplicates"), "reject duplicate JSON keys")
    reject(lambda: strict_json(b'{"a":NaN}\n', "nonfinite"), "reject nonfinite JSON")
    reject(lambda: checked_command("build_go_engine", first["build_go_engine"][:-1], private,
                                  "reference-a"), "reject truncated Go build")
    reject(lambda: checked_command("shell", ["/bin/sh", "-c", "go build"], private,
                                  "reference-a"), "reject a shell build")
    for token in FORBIDDEN_ENGINE_TOKENS:
        reject(lambda item=token: validate_no_delegation(b"safe\n" + item, "synthetic"),
               "reject every independently frozen delegation token")
    controls: tuple[tuple[str, Any], ...] = (
        ("filesystem-open", lambda: builtins.open("/tmp/rebar-v13-forbidden", "rb")),
        ("filesystem-os-open", lambda: os.open("/tmp/rebar-v13-forbidden", os.O_RDONLY)),
        ("filesystem-stat", lambda: os.stat("/tmp")),
        ("filesystem-path-read", lambda: Path("/tmp").read_bytes()),
        ("filesystem-path-open", lambda: Path("/tmp").open("rb")),
        ("filesystem-list", lambda: os.listdir("/tmp")),
        ("workspace-mkdir", lambda: os.mkdir("/tmp/rebar-v13-forbidden")),
        ("workspace-unlink", lambda: os.unlink("/tmp/rebar-v13-forbidden")),
        ("workspace-rename", lambda: os.rename("/tmp/rebar-v13-a", "/tmp/rebar-v13-b")),
        ("workspace-path-write", lambda: Path("/tmp/rebar-v13-forbidden").write_bytes(b"x")),
        ("workspace-temp", lambda: tempfile.mkdtemp(prefix="rebar-v13-forbidden-")),
        ("process-run", lambda: subprocess.run([PINNED_GO, "version"])),
        ("process-popen", lambda: subprocess.Popen([PINNED_GO, "version"])),
        ("process-system", lambda: os.system("go version")),
        ("network-socket", lambda: socket.socket()),
        ("network-connect", lambda: socket.create_connection(("127.0.0.1", 1))),
        ("native-cdll", lambda: ctypes.CDLL("libc.so.6")),
        ("native-pydll", lambda: ctypes.PyDLL(None)),
        ("thread-start", lambda: threading.Thread(target=lambda: None).start()),
        ("clock-time", lambda: time.time()),
        ("clock-monotonic", lambda: time.monotonic()),
        ("clock-perf", lambda: time.perf_counter()),
        ("clock-sleep", lambda: time.sleep(0)),
        ("gzip-open", lambda: gzip.open("/tmp/rebar-v13-forbidden.gz", "rb")),
        ("gzip-compress", lambda: gzip.compress(b"forbidden")),
        ("gzip-decompress", lambda: gzip.decompress(b"forbidden")),
        ("zlib-decompress", lambda: zlib.decompress(b"forbidden")),
        ("zlib-object", lambda: zlib.decompressobj()),
        ("module-import", lambda: importlib.import_module("re")),
        ("builtin-import", lambda: builtins.__import__("re")),
        ("signal", lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL)),
        ("lock", lambda: fcntl.flock(-1, fcntl.LOCK_EX)),
    )
    with SourceWall() as wall:
        for repetition in range(4):
            for name, operation in controls:
                reject(operation, name + "-" + str(repetition))
        accept(len(wall.categories) >= 10, "physically guard every independent effect boundary")
        accept(canonical({"source_only": True}) == b'{"source_only":true}\n',
               "allow pure deterministic computation inside the source wall")
    accept(positive_count >= 50, "run comprehensive pure positive controls")
    accept(negative_count >= 150, "run comprehensive independently blocked hostile controls")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules), "do not import any candidate during a source-only test")
    return {"schema": SCHEMA + "-source-only-self-test", "version": 13,
            "status": "PASS", "positive_control_count": positive_count,
            "negative_control_count": negative_count,
            "physically_blocked_effect_categories": sorted(wall.categories),
            "future_phase_process_count_only_after_success": EXPECTED_PHASE_PROCESS_COUNT,
            "future_total_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
            **phase_boundary()}


def validate_phase_one(data: bytes) -> None:
    value = strict_json(data, "frozen P0 completeness matrix")
    denominator = value.get("denominator")
    gate = value.get("phase_gate")
    require(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and value.get("version") == 1 and type(denominator) is dict
            and denominator.get("final_required_case_execution_denominator") == CASE_DENOMINATOR
            and denominator.get("frozen_planned_case_execution_denominator") == CASE_DENOMINATOR
            and len(denominator.get("counted_suite_ids", [])) == SUITE_COUNT
            and denominator.get("private_upstream_methods_outside_public_denominator")
            == PRIVATE_WAIVER_COUNT
            and type(value.get("suites")) is list and len(value["suites"]) == SUITE_COUNT
            and type(gate) is dict and gate.get("status") == "PASS"
            and gate.get("all_obligations_mapped") is True,
            "preserve the exact frozen 31,237-case, 13-suite, 13-waiver P0 matrix")


def validate_callable(data: bytes) -> None:
    value = strict_json(data, "separately frozen callable obligations")
    obligation = value.get("additional_obligation")
    boundary = value.get("phase_boundary")
    require(value.get("schema") == "rebar-python-re-callable-introspection-v1-source-freeze"
            and value.get("version") == 1
            and value.get("status") == "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN"
            and type(obligation) is dict and obligation.get("case_count") == 50
            and obligation.get("included_in_original_31237_denominator") is False
            and obligation.get("status") == "FROZEN; TWO INDEPENDENT REFERENCES NOT RUN"
            and type(boundary) is dict and boundary.get("introspection_reference") == "NOT RUN"
            and boundary.get("candidate_introspection") == "NOT MEASURED"
            and boundary.get("actual_reference_roles_started") == 0
            and boundary.get("actual_candidate_workers_started") == 0
            and boundary.get("holdout") == "NOT OPENED",
            "preserve the immutable pre-execution V1 callable source freeze without changing the original denominator")


def validate_callable_reference_v2(raw: dict[str, bytes]) -> dict[str, Any]:
    frozen = strict_json(raw[CALLABLE_REFERENCE_V2[2].path],
                         "immutable V2 callable-reference source freeze")
    core = frozen.get("original_core")
    additional = frozen.get("frozen_additional_oracle")
    policy = frozen.get("future_reference_policy")
    require(frozen.get("schema")
            == "rebar-owned-callable-introspection-reference-v2-source-freeze"
            and frozen.get("version") == 2
            and frozen.get("status") == "SOURCE FREEZE ONLY; TWO REFERENCES NOT RUN"
            and frozen.get("source") == {
                "path": CALLABLE_REFERENCE_V2[0].path,
                "sha256": CALLABLE_REFERENCE_V2[0].sha256,
            }
            and frozen.get("protocol") == {
                "path": CALLABLE_REFERENCE_V2[1].path,
                "sha256": CALLABLE_REFERENCE_V2[1].sha256,
            }
            and type(core) is dict
            and core.get("case_execution_denominator") == CASE_DENOMINATOR
            and core.get("denominator_modified") is False
            and core.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and core.get("suite_count") == SUITE_COUNT
            and type(additional) is dict
            and additional.get("separately_counted_case_count") == 50
            and additional.get("included_in_original_core_denominator") is False
            and additional.get("matrix_sha256")
            == "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
            and type(policy) is dict
            and policy.get("exact_distinct_isolated_worker_process_count") == 2
            and policy.get("different_actual_process_ids_required") is True
            and policy.get("candidate_execution_allowed") is False,
            "authenticate the unchanged frozen V2 two-reference callable policy")
    receipt = strict_json(raw[CALLABLE_REFERENCE_RECEIPT.path],
                          "actual completed two-process callable-reference receipt")
    process_ids = receipt.get("actual_distinct_process_ids")
    archive = receipt.get("archive")
    appended = receipt.get("appended_corrected_zig_matching")
    require(receipt.get("schema")
            == "rebar-owned-callable-introspection-reference-v2-durable-publication-receipt"
            and receipt.get("version") == 2
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means") == "EVIDENCE PUBLICATION ONLY"
            and receipt.get("reference_status") == "PASS"
            and receipt.get("reference_failure_count") == 0
            and receipt.get("actual_reference_processes_started") == 2
            and type(process_ids) is list and process_ids == [81, 82]
            and len(set(process_ids)) == 2
            and receipt.get("additional_case_count") == 50
            and receipt.get("additional_cases_included_in_original_denominator") is False
            and receipt.get("original_case_denominator") == CASE_DENOMINATOR
            and receipt.get("original_suite_count") == SUITE_COUNT
            and receipt.get("original_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and receipt.get("candidate_introspection") == "NOT MEASURED"
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_qualified") is False
            and receipt.get("authenticated_evidence_owner_lower_bound_before_publication") == 157
            and receipt.get("authenticated_history_reference_lower_bound_before_publication") == 162
            and receipt.get("new_actual_evidence_owner_count") == 2
            and receipt.get("minimum_evidence_owner_count_after_publication") == 159
            and receipt.get("minimum_history_reference_count_after_publication") == 164
            and receipt.get("frozen_v1_source_sha256") == CALLABLE_V1[0].sha256
            and receipt.get("frozen_v1_protocol_sha256") == CALLABLE_V1[1].sha256
            and receipt.get("frozen_v1_contract_sha256") == CALLABLE_V1[2].sha256
            and receipt.get("source_sha256") == CALLABLE_REFERENCE_V2[0].sha256
            and receipt.get("protocol_sha256") == CALLABLE_REFERENCE_V2[1].sha256
            and receipt.get("contract_sha256") == CALLABLE_REFERENCE_V2[2].sha256
            and receipt.get("matrix_sha256")
            == "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
            and type(archive) is dict
            and archive.get("sha256")
            == "7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c"
            and archive.get("bytes") == 8538
            and archive.get("mode") == "0600"
            and archive.get("nlink") == 1
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and type(appended) is dict
            and appended.get("candidate_status") == "FAIL"
            and appended.get("semantic_mismatch_count") == 1764
            and appended.get("verified_passing_case_count") == 3711
            and appended.get("actual_candidate_workers") == 13
            and appended.get("infrastructure_failure_count") == 0
            and appended.get("matching_archive_opened") is False
            and appended.get("matching_archive_decompressed") is False
            and type(appended.get("receipt")) is dict
            and appended["receipt"].get("sha256") == ZIG_CORRECTED_MATCH_RECEIPT.sha256
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("holdout_cases_read") == 0
            and receipt.get("final_cases_read") == 0
            and receipt.get("matching_archives_opened") == 0
            and receipt.get("source_build_archives_decompressed") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("undefined_behavior") == "NOT MEASURED"
            and receipt.get("winner_selected") is False,
            "authenticate the actual 50-case two-PID passing reference from its small durable receipt only")
    return receipt


def validate_python_adapter(data: bytes) -> None:
    try:
        module = ast.parse(data.decode("utf-8", "strict"),
                           filename=GO_OWNERS[3].path, mode="exec")
    except (UnicodeError, SyntaxError, ValueError) as error:
        raise BuildError("reject a changed original first-party Go Python adapter") from error
    names: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            require(node.level == 0, "reject a substituted relative Go-adapter import")
            if node.module == "candidates":
                require(len(node.names) == 1 and node.names[0].name == "_go_bridge",
                        "allow only the owned native Go bridge")
                names.add("candidates._go_bridge")
            elif node.module == "__future__":
                names.add("__future__")
            else:
                require(False, "reject an external or other-family Go adapter import")
    require(names == {"__future__", "copyreg", "enum", "operator", "types",
                      "warnings", "candidates._go_bridge"},
            "freeze the exact original stdlib utility and owned Go-bridge import closure")
    validate_no_delegation(data, "original Go adapter")


def validate_go_repair(raw: dict[str, bytes]) -> bytes:
    derived = corrected_source(raw[GO_OWNERS[0].path])
    require(raw[GO_OWNERS[1].path] == b"module rebar.local/candidates/go\n\ngo 1.26.0\n",
            "require the exact dependency-free first-party Go module")
    bridge = raw[GO_OWNERS[2].path]
    for marker in (b"#include <Python.h>", b"PyUnicode_DecodeUTF8(",
                   b"Py_MOD_PER_INTERPRETER_GIL_SUPPORTED", b"Py_MOD_GIL_USED"):
        require(marker in bridge, "preserve the complete original interpreter-local Go bridge")
    for name in GO_EXPORTS:
        require((name + "(").encode("ascii") in bridge,
                "preserve all nine genuine first-party Go bridge imports")
    validate_no_delegation(bridge, "original Go bridge")
    validate_python_adapter(raw[GO_OWNERS[3].path])
    value = strict_json(raw[GO_UNICODE_V1[2].path], "committed Unicode source repair")
    repair = value.get("repair")
    go = value.get("go_source")
    require(value.get("schema") == "rebar-phase2-owned-go-unicode-name-source-repair-v1-source-freeze"
            and value.get("version") == 1 and type(repair) is dict and type(go) is dict
            and repair.get("candidate_matching_proven") is False
            and type(repair.get("original")) is dict
            and repair["original"].get("sha256") == GO_ORIGINAL_SHA256
            and type(repair.get("derived")) is dict
            and repair["derived"].get("sha256") == GO_DERIVED_SHA256
            and repair["derived"].get("materialized") is False
            and type(repair.get("block")) is dict
            and repair["block"].get("original_sha256") == ORIGINAL_BLOCK_SHA256
            and repair["block"].get("corrected_sha256") == CORRECTED_BLOCK_SHA256
            and go.get("external_regex_dependency_count") == 0
            and go.get("cross_family_dependency_count") == 0
            and go.get("go_module_dependency_count") == 0,
            "authenticate the complete previously committed first-party Go Unicode repair")
    return derived


def validate_v6_contract(data: bytes) -> None:
    value = strict_json(data, "historical V6 native build contract")
    families = value.get("families")
    tools = value.get("toolchains")
    require(value.get("schema") == "rebar-phase2-owned-native-source-build-v6-source-freeze"
            and value.get("version") == 6 and type(families) is list
            and type(tools) is list, "authenticate the genuine original six-family native build")
    family = [item for item in families if type(item) is dict and item.get("id") == "go"]
    require(len(family) == 1 and family[0].get("artifacts") == {
        "engine": "_go_engine.so",
        "bridge": "_go_bridge.cpython-314-x86_64-linux-gnu.so",
        "generated_header": "_go_engine.h",
    }, "preserve the exact historical first-party Go artifact ABI")
    expected = sorted((owner_document(owner) for owner in GO_OWNERS), key=lambda item: item["path"])
    require(sorted(family[0].get("owners", []), key=lambda item: item.get("path", "")) == expected,
            "preserve exactly the four historical independently owned Go sources")
    lookup = {entry.get("id"): entry for entry in tools if type(entry) is dict}
    for tool in TOOLCHAINS:
        require(lookup.get(tool.identity) == toolchain_document(tool),
                "preserve the historical exact pinned Go, compiler, ELF, and Python toolchains")


def validate_v33(summary: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    require(summary.get("schema") == "rebar-candidate-current-overview-v33-summary"
            and summary.get("status") == "PASS" and summary.get("version") == 33
            and summary.get("full_case_denominator") == CASE_DENOMINATOR
            and summary.get("suite_count") == SUITE_COUNT
            and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and summary.get("repository_evidence_owner_count") == V33_EVIDENCE_OWNER_LOWER_BOUND
            and summary.get("authenticated_digest_addressed_history_paths")
            == V33_AUTHENTICATED_REFERENCE_LOWER_BOUND
            and summary.get("qualified_candidate_count") == 0
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
            and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
            and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
            and summary.get("zig_v12_source_build_status") == "PASS"
            and summary.get("zig_v12_source_build_process_count") == 26
            and summary.get("zig_v12_source_build_phase_count") == 2
            and summary.get("zig_v12_source_build_source_apply_count") == 2
            and summary.get("zig_v12_source_build_matching_test_status") == "NOT MEASURED"
            and summary.get("zig_v12_source_build_candidate_worker_count") == 0
            and summary.get("zig_v12_source_build_candidate_correctness") == "NOT MEASURED"
            and summary.get("final_comparison_planned_case_count") == FINAL_PLANNED_HOLDOUT_CASES
            and summary.get("final_comparison_cases_generated") is False
            and summary.get("final_holdout_opened") is False
            and summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("confidence_intervals") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED"
            and summary.get("winner_selected") is False,
            "authenticate immutable V33 history without calling its 155/160 lower bound current")
    require(inputs.get("schema") == "rebar-candidate-current-overview-v33-inputs"
            and inputs.get("version") == 33
            and inputs.get("full_case_denominator") == CASE_DENOMINATOR
            and inputs.get("suite_count") == SUITE_COUNT
            and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and inputs.get("repository_evidence_owner_count") == V33_EVIDENCE_OWNER_LOWER_BOUND
            and inputs.get("all_digest_addressed_history_path_count")
            == V33_AUTHENTICATED_REFERENCE_LOWER_BOUND
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("actual_rust_semantic_mismatch_count") == 1036
            and inputs.get("actual_rust_verified_passing_case_count") == 8965
            and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
            and inputs.get("actual_zig_semantic_mismatch_count") == 2172
            and inputs.get("zig_v12_source_build_status") == "PASS"
            and inputs.get("zig_v12_source_build_process_count") == 26
            and inputs.get("zig_v12_source_build_independent_phase_count") == 2
            and inputs.get("zig_v12_source_build_apply_count") == 2
            and inputs.get("zig_v12_source_build_matching_test_status") == "NOT MEASURED"
            and inputs.get("zig_v12_source_build_candidate_workers") == 0
            and inputs.get("final_holdout_opened") is False
            and inputs.get("performance") == "NOT MEASURED",
            "authenticate the separate original V33 input graph as immutable lower-bound history")
    families = summary.get("families")
    require(type(families) is list, "preserve the authenticated independent family graph")
    go = [item for item in families if type(item) is dict and item.get("family") == "go"]
    require(len(go) == 1, "preserve exactly one first-party Go candidate family")
    family = go[0]
    campaign = family.get("complete_v2_original_campaign")
    build = family.get("build_evidence")
    require(family.get("build_status") == "PASS"
            and family.get("matching_test_status") == "FAIL"
            and family.get("qualified") is False
            and family.get("performance") == "NOT MEASURED"
            and family.get("owned_sources") == [
                {"path": owner.path, "sha256": owner.sha256} for owner in GO_OWNERS]
            and type(build) is dict and build.get("actual_process_count") == 26
            and build.get("cross_family_dependency_count") == 0
            and build.get("external_regex_dependency_count") == 0
            and type(campaign) is dict and campaign.get("status") == "FAIL"
            and campaign.get("completed_suite_count") == SUITE_COUNT
            and campaign.get("semantic_mismatch_count") == 4518
            and campaign.get("verified_passing_case_count") == 128
            and campaign.get("infrastructure_failure_count") == 4
            and campaign.get("infrastructure_failure_suites") == list(GO_INFRASTRUCTURE_SUITES)
            and campaign.get("intentional_output_overflow_suite") == "shape_v2"
            and campaign.get("native_crash_proven") is False
            and campaign.get("crash_count") == 0
            and campaign.get("timeout_count") == 0
            and campaign.get("candidate_qualified") is False,
            "preserve actual Go mismatches and infrastructure failures without claiming a native crash")
    return campaign


def validate_v34(summary: dict[str, Any], inputs: dict[str, Any]) -> None:
    require(summary.get("schema") == "rebar-candidate-current-overview-v34-summary"
            and summary.get("version") == 34 and summary.get("status") == "PASS"
            and summary.get("full_case_denominator") == CASE_DENOMINATOR
            and summary.get("suite_count") == SUITE_COUNT
            and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and summary.get("repository_evidence_owner_count") == 157
            and summary.get("authenticated_digest_addressed_history_paths") == 162
            and summary.get("qualified_candidate_count") == 0
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
            and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 1764
            and summary.get("zig_original_campaign_verified_passing_case_count") == 3711
            and summary.get("zig_original_campaign_candidate_worker_count") == 13
            and summary.get("zig_original_campaign_infrastructure_failure_count") == 0
            and summary.get("historical_zig_semantic_mismatch_count") == 2172
            and summary.get("additional_signature_frozen_case_count") == 50
            and summary.get("additional_signature_reference_cases_executed") == 0
            and summary.get("additional_signature_reference_status") == "NOT RUN"
            and summary.get("final_comparison_planned_case_count") == FINAL_PLANNED_HOLDOUT_CASES
            and summary.get("final_comparison_cases_generated") is False
            and summary.get("final_holdout_opened") is False
            and summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("uncompressed_new_zig_matching_archive_opened_by_graph") is False
            and summary.get("uncompressed_new_zig_matching_archive_bytes_read_by_graph") == 0
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("confidence_intervals") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED"
            and summary.get("winner_selected") is False,
            "authenticate exact V34 as immutable 157/162 pre-reference history, never current state")
    require(inputs.get("schema") == "rebar-candidate-current-overview-v34-inputs"
            and inputs.get("version") == 34
            and inputs.get("full_case_denominator") == CASE_DENOMINATOR
            and inputs.get("suite_count") == SUITE_COUNT
            and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and inputs.get("repository_evidence_owner_count") == 157
            and inputs.get("all_digest_addressed_history_path_count") == 162
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("rust_original_campaign_semantic_mismatch_count") == 1036
            and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
            and inputs.get("zig_original_campaign_status") == "FAIL"
            and inputs.get("zig_original_campaign_semantic_mismatch_count") == 1764
            and inputs.get("zig_original_campaign_verified_passing_case_count") == 3711
            and inputs.get("zig_original_campaign_candidate_worker_count") == 13
            and inputs.get("zig_original_campaign_infrastructure_failure_count") == 0
            and inputs.get("historical_zig_semantic_mismatch_count") == 2172
            and inputs.get("additional_signature_frozen_case_count") == 50
            and inputs.get("additional_signature_reference_cases_executed") == 0
            and inputs.get("additional_signature_reference_status") == "NOT RUN"
            and inputs.get("final_comparison_planned_case_count") == FINAL_PLANNED_HOLDOUT_CASES
            and inputs.get("final_comparison_cases_generated") is False
            and inputs.get("final_holdout_opened") is False
            and inputs.get("uncompressed_new_zig_matching_archive_opened_by_graph") is False
            and inputs.get("uncompressed_new_zig_matching_archive_bytes_read_by_graph") == 0
            and inputs.get("performance") == "NOT MEASURED"
            and inputs.get("memory") == "NOT MEASURED"
            and inputs.get("winner_selected") is False,
            "authenticate separate immutable V34 inputs without mistaking later reference execution")


def validate_receipts(raw: dict[str, bytes]) -> None:
    go_build = strict_json(raw[GO_BUILD_RECEIPT.path], "original Go build receipt")
    require(go_build.get("schema") == "rebar-phase2-owned-native-source-build-v6-durable-publication-receipt"
            and go_build.get("status") == "PASS" and go_build.get("family") == "go"
            and go_build.get("build_status") == "PASS"
            and go_build.get("actual_v6_compiler_process_count") == 26
            and go_build.get("expected_v6_compiler_process_count") == 26
            and go_build.get("owned_source_sha256")
            == {owner.path: owner.sha256 for owner in GO_OWNERS}
            and go_build.get("candidate_correctness") == "NOT MEASURED"
            and go_build.get("holdout") == "NOT OPENED",
            "authenticate the real original Go build through its small receipt only")
    go = strict_json(raw[GO_MATCH_RECEIPT.path], "historical failing Go receipt")
    archive = go.get("archive")
    require(go.get("schema") == "rebar-owned-six-family-original-p0-campaign-v2-durable-publication-receipt"
            and go.get("status") == "PASS" and go.get("candidate_family") == "go"
            and go.get("candidate_status") == "FAIL"
            and go.get("suite_count") == SUITE_COUNT
            and go.get("completed_suite_count") == SUITE_COUNT
            and go.get("case_execution_denominator") == CASE_DENOMINATOR
            and go.get("verified_passing_case_count") == 128
            and go.get("all_mismatches_crashes_and_timeouts_preserved") is True
            and type(archive) is dict
            and archive.get("sha256") == "af971b3387382862ebf084b1d48ff0a21f37084cb234fd9e776d721b3ca5aae0"
            and archive.get("size_bytes") == 9139062
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and go.get("holdout") == "NOT OPENED",
            "authenticate the failing Go campaign exclusively through its small durable receipt")
    rust = strict_json(raw[RUST_MATCH_RECEIPT.path], "actual Rust matching receipt")
    rust_archive = rust.get("archive")
    require(rust.get("schema") == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
            and rust.get("status") == "PASS" and rust.get("family") == "rust"
            and rust.get("candidate_status") == "FAIL"
            and rust.get("actual_candidate_workers") == SUITE_COUNT
            and rust.get("semantic_mismatch_count") == 1036
            and rust.get("verified_passing_case_count") == 8965
            and rust.get("infrastructure_failure_count") == 0
            and rust.get("case_execution_denominator") == CASE_DENOMINATOR
            and rust.get("candidate_qualified") is False
            and type(rust_archive) is dict
            and rust_archive.get("sha256") == "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f"
            and rust_archive.get("size_bytes") == 3663299
            and rust.get("holdout") == "NOT OPENED",
            "preserve the actual 1,036-mismatch Rust result without opening its archive")
    for owner, family, mismatch, verified in (
        (C_MATCH_RECEIPT, "c", 1230, 7325),
        (ZIG_MATCH_RECEIPT, "zig", 2172, 2847),
    ):
        result = strict_json(raw[owner.path], family + " matching receipt")
        require(result.get("status") == "PASS"
                and result.get("family") == family
                and result.get("candidate_status") == "FAIL"
                and result.get("actual_candidate_workers") == SUITE_COUNT
                and result.get("completed_suite_count") == SUITE_COUNT
                and result.get("case_execution_denominator") == CASE_DENOMINATOR
                and result.get("semantic_mismatch_count") == mismatch
                and result.get("verified_passing_case_count") == verified
                and result.get("infrastructure_failure_count") == 0
                and result.get("candidate_qualified") is False
                and result.get("holdout") == "NOT OPENED",
                "preserve the historical " + family + " failure through its receipt only")
    zig = strict_json(raw[ZIG_BUILD_RECEIPT.path], "actual corrected Zig build receipt")
    require(zig.get("schema") == "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt"
            and zig.get("version") == 12 and zig.get("status") == "PASS"
            and zig.get("family") == "zig" and zig.get("build_status") == "PASS"
            and zig.get("actual_compiler_process_count") == 26
            and zig.get("actual_source_apply_count") == 2
            and zig.get("repository_evidence_owner_count_after_publication")
            == V33_EVIDENCE_OWNER_LOWER_BOUND
            and zig.get("authenticated_history_reference_count_after_publication")
            == V33_AUTHENTICATED_REFERENCE_LOWER_BOUND
            and zig.get("candidate_correctness") == "NOT MEASURED"
            and zig.get("candidate_processes_started") == 0
            and zig.get("candidate_imports") == 0
            and zig.get("holdout") == "NOT OPENED",
            "authenticate V12's genuine 26-process Zig build as immutable history, not matching")
    corrected = strict_json(raw[ZIG_CORRECTED_MATCH_RECEIPT.path],
                            "latest corrected V12 Zig original-P0 matching receipt")
    corrected_archive = corrected.get("archive")
    require(corrected.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt"
            and corrected.get("status") == "PASS"
            and corrected.get("publication_status") == "PASS"
            and corrected.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and corrected.get("family") == "zig"
            and corrected.get("candidate_status") == "FAIL"
            and corrected.get("suite_count") == SUITE_COUNT
            and corrected.get("completed_suite_count") == SUITE_COUNT
            and corrected.get("case_execution_denominator") == CASE_DENOMINATOR
            and corrected.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and corrected.get("actual_candidate_workers") == SUITE_COUNT
            and corrected.get("semantic_mismatch_count") == 1764
            and corrected.get("verified_passing_case_count") == 3711
            and corrected.get("infrastructure_failure_count") == 0
            and corrected.get("candidate_qualified") is False
            and corrected.get("historical_zig_semantic_mismatch_count") == 2172
            and corrected.get("historical_evidence_owner_count_before_publication")
            == V33_EVIDENCE_OWNER_LOWER_BOUND
            and corrected.get("historical_authenticated_reference_count_before_publication")
            == V33_AUTHENTICATED_REFERENCE_LOWER_BOUND
            and corrected.get("new_repository_evidence_owner_count") == 2
            and corrected.get("resulting_repository_evidence_owner_count") == 157
            and corrected.get("resulting_authenticated_reference_count") == 162
            and type(corrected_archive) is dict
            and corrected_archive.get("sha256")
            == "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b"
            and corrected_archive.get("size_bytes") == 3722337
            and corrected_archive.get("exclusive_creation") is True
            and corrected_archive.get("same_inode_readback_verified") is True
            and corrected_archive.get("streaming_readback_verified") is True
            and corrected.get("holdout") == "NOT OPENED"
            and corrected.get("performance") == "NOT MEASURED"
            and corrected.get("hidden_cases_read") == 0
            and corrected.get("clock_samples") == 0
            and corrected.get("timing_trials_run") == 0
            and corrected.get("winner_selected") is False,
            "authenticate the actual 1,764-mismatch corrected Zig campaign through its small receipt only")


def verify_frozen_context(source_pin: str, protocol_pin: str,
                          contract_pin: str) -> tuple[dict[str, Any], bytes]:
    read_contract_owners(source_pin, protocol_pin, contract_pin)
    support = (
        GOAL, PHASE_ONE, *GO_OWNERS, *GO_UNICODE_V1, *V33, *V34, *NATIVE_V6,
        *CALLABLE_V1, *CALLABLE_REFERENCE_V2, *ZIG_V12,
        GO_BUILD_RECEIPT, GO_MATCH_RECEIPT,
        RUST_MATCH_RECEIPT, C_MATCH_RECEIPT, ZIG_MATCH_RECEIPT, ZIG_BUILD_RECEIPT,
        ZIG_CORRECTED_MATCH_RECEIPT, CALLABLE_REFERENCE_RECEIPT,
    )
    require(len({owner.path for owner in support}) == len(support),
            "reject duplicated repository evidence or inflated owner accounting")
    raw: dict[str, bytes] = {}
    authenticated: list[dict[str, Any]] = []
    for owner in support:
        data, document = read_owner(owner)
        raw[owner.path] = data
        authenticated.append(document)
    toolchains = [read_toolchain(tool) for tool in TOOLCHAINS]
    validate_phase_one(raw[PHASE_ONE.path])
    validate_callable(raw[CALLABLE_V1[2].path])
    callable_reference = validate_callable_reference_v2(raw)
    derived = validate_go_repair(raw)
    validate_v6_contract(raw[NATIVE_V6[2].path])
    summary = strict_json(raw[V33[2].path], "immutable V33 graph")
    inputs = strict_json(raw[V33[1].path], "immutable V33 graph inputs")
    campaign = validate_v33(summary, inputs)
    validate_v34(strict_json(raw[V34[2].path], "immutable V34 graph"),
                 strict_json(raw[V34[1].path], "immutable V34 graph inputs"))
    validate_receipts(raw)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "authenticate frozen source without importing or activating a candidate")
    return {
        "schema": SCHEMA + "-read-only-frozen-context", "version": 13,
        "status": "PASS", "mode": "SOURCE FROZEN; BUILD NOT RUN",
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "authenticated_support_owner_count": len(authenticated),
        "authenticated_toolchain_count": len(toolchains),
        "authenticated_support_owners": authenticated,
        "authenticated_toolchains": toolchains,
        "original_engine_sha256": GO_ORIGINAL_SHA256,
        "original_engine_bytes": GO_ORIGINAL_BYTES,
        "derived_engine_sha256": GO_DERIVED_SHA256,
        "derived_engine_bytes": GO_DERIVED_BYTES,
        "historical_v33_repository_evidence_owner_lower_bound":
            V33_EVIDENCE_OWNER_LOWER_BOUND,
        "historical_v33_authenticated_reference_lower_bound":
            V33_AUTHENTICATED_REFERENCE_LOWER_BOUND,
        "v33_counts_claimed_current": False,
        "historical_v34_repository_evidence_owner_lower_bound": 157,
        "historical_v34_authenticated_reference_lower_bound": 162,
        "v34_counts_claimed_current": False,
        "append_only_later_evidence_permitted": True,
        "case_execution_denominator": CASE_DENOMINATOR,
        "suite_count": SUITE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "historical_go_semantic_mismatch_count": campaign["semantic_mismatch_count"],
        "historical_go_verified_passing_case_count": campaign["verified_passing_case_count"],
        "historical_go_infrastructure_failure_count": campaign["infrastructure_failure_count"],
        "historical_go_infrastructure_failure_suites": campaign["infrastructure_failure_suites"],
        "historical_go_native_crash_proven": False,
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_v12_zig_build_process_count": 26,
        "historical_v12_zig_matching_test_status_at_v33": "NOT MEASURED",
        "latest_authenticated_corrected_zig_matching_status": "FAIL",
        "latest_authenticated_corrected_zig_semantic_mismatch_count": 1764,
        "latest_authenticated_corrected_zig_verified_passing_case_count": 3711,
        "latest_authenticated_corrected_zig_candidate_worker_count": 13,
        "latest_authenticated_corrected_zig_infrastructure_failure_count": 0,
        "latest_authenticated_repository_evidence_owner_lower_bound": 159,
        "latest_authenticated_reference_lower_bound": 164,
        "separately_frozen_callable_obligation_count": 50,
        "callable_reference_status": "PASS",
        "callable_reference_verified_case_count": callable_reference["additional_case_count"],
        "callable_reference_failure_count": callable_reference["reference_failure_count"],
        "historical_actual_callable_reference_process_count":
            callable_reference["actual_reference_processes_started"],
        "historical_actual_callable_reference_process_ids":
            callable_reference["actual_distinct_process_ids"],
        "callable_candidate_execution": "NOT RUN",
        "callable_candidate_status": "NOT MEASURED",
        "final_planned_holdout_case_count": FINAL_PLANNED_HOLDOUT_CASES,
        "future_phase_process_count_only_after_success": EXPECTED_PHASE_PROCESS_COUNT,
        "future_total_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
        **phase_boundary(),
    }, derived


def create_private_directory(path: Path) -> dict[str, Any]:
    require(type(path) is Path and str(path).startswith("/tmp/" + WORK_PREFIX),
            "create only exact independently owned V13 Go private directories")
    try:
        os.mkdir(path, 0o700)
        actual = os.stat(path, follow_symlinks=False)
    except OSError as error:
        raise BuildError("cannot exclusively create private phase directory: " + str(path)) from error
    require(stat.S_ISDIR(actual.st_mode) and stat.S_IMODE(actual.st_mode) == 0o700
            and actual.st_uid == os.geteuid(),
            "require an independently owned mode-0700 nonsymlink private directory")
    return {"path": str(path), "device": actual.st_dev, "inode": actual.st_ino,
            "mode": stat.S_IMODE(actual.st_mode), "uid": actual.st_uid}


def exclusive_private_file(path: Path, data: bytes, *, synchronize: bool = True) -> dict[str, Any]:
    require(type(path) is Path and type(data) is bytes and 0 < len(data) <= MAX_BINARY_BYTES,
            "write only exact bounded exclusive owned bytes")
    value = str(path)
    require(value.startswith("/tmp/" + WORK_PREFIX)
            or value.startswith(str(ROOT / EVIDENCE_RELATIVE) + "/"),
            "never write outside the exact private build root or owned evidence directory")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    handle: int | None = None
    try:
        handle = os.open(value, flags, 0o600)
        offset = 0
        while offset < len(data):
            amount = os.write(handle, data[offset:])
            require(type(amount) is int and amount > 0, "reject a short exclusive private write")
            offset += amount
        if synchronize:
            os.fsync(handle)
        actual = os.fstat(handle)
        require(stat.S_ISREG(actual.st_mode) and stat.S_IMODE(actual.st_mode) == 0o600
                and actual.st_uid == os.geteuid() and actual.st_nlink == 1
                and actual.st_size == len(data),
                "require a unique mode-0600 fully written private source or receipt")
    except OSError as error:
        raise BuildError("cannot exclusively publish fresh private bytes: " + value) from error
    finally:
        if handle is not None:
            os.close(handle)
    observed, snapshot = read_private_artifact(path, expected=digest(data), exact_size=len(data))
    require(observed == data, "verify every exact private write by descriptor-bound readback")
    return {**snapshot, "exclusive_creation": True, "file_fsync_completed": synchronize,
            "same_inode_readback_verified": True}


def read_private_artifact(path: Path, *, expected: str | None = None,
                          exact_size: int | None = None) -> tuple[bytes, dict[str, Any]]:
    value = str(path)
    require(value.startswith("/tmp/" + WORK_PREFIX)
            or value.startswith(str(ROOT / EVIDENCE_RELATIVE) + "/"),
            "read only an exact owned future artifact or newly published evidence")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle: int | None = None
    try:
        handle = os.open(value, flags)
        before = os.fstat(handle)
        visible = os.stat(value, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
                and before.st_nlink == 1 and 0 < before.st_size <= MAX_BINARY_BYTES
                and not (stat.S_IMODE(before.st_mode) & 0o022)
                and (exact_size is None or before.st_size == exact_size)
                and (before.st_dev, before.st_ino, before.st_size, before.st_uid)
                == (visible.st_dev, visible.st_ino, visible.st_size, visible.st_uid),
                "reject a linked, mutable, exchanged, or oversized private artifact")
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(handle, min(remaining, 1024 * 1024))
            require(bool(chunk), "reject a truncated private native artifact")
            pieces.append(chunk)
            remaining -= len(chunk)
        require(os.read(handle, 1) == b"", "reject an appended private artifact")
        data = b"".join(pieces)
        after = os.fstat(handle)
        actual_digest = digest(data)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and (expected is None or actual_digest == checked_digest(expected, value)),
                "reject private artifact bytes changed during readback")
        return data, {"path": value, "sha256": actual_digest, "bytes": len(data),
                      "device": after.st_dev, "inode": after.st_ino,
                      "mode": stat.S_IMODE(after.st_mode), "uid": after.st_uid,
                      "nlink": after.st_nlink}
    except OSError as error:
        raise BuildError("cannot authenticate actual private artifact: " + value) from error
    finally:
        if handle is not None:
            os.close(handle)


def record_stream(data: bytes, label: str) -> dict[str, Any]:
    require(type(data) is bytes and len(data) <= MAX_PROCESS_OUTPUT_BYTES,
            "bound complete actual compiler output: " + label)
    return {"base64": base64.b64encode(data).decode("ascii"),
            "sha256": digest(data), "bytes": len(data)}


def run_process(workdir: str, phase: str, role: str) -> dict[str, Any]:
    argv = checked_command(role, planned_commands(workdir, phase)[role], workdir, phase)
    try:
        process = subprocess.run(argv,
                                 cwd=str(command_working_directory(workdir, phase, role)),
                                 env=build_environment(workdir, phase),
                                 stdin=subprocess.DEVNULL, capture_output=True,
                                 check=False, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise BuildError("actual frozen compiler or ELF process failed: " + role) from error
    require(type(process.returncode) is int and process.returncode == 0,
            "preserve and reject unsuccessful actual frozen compiler role: " + role)
    stdout = record_stream(process.stdout, role + " stdout")
    stderr = record_stream(process.stderr, role + " stderr")
    return {"role": role, "phase": phase,
            "argv": [sanitized(item, workdir) for item in argv],
            "working_directory": sanitized(str(command_working_directory(workdir, phase, role)), workdir),
            "returncode": process.returncode,
            "stdout": stdout, "stderr": stderr,
            "stdout_bytes_for_audit": process.stdout}


def validate_version_output(role: str, output: bytes) -> None:
    expected = {
        "go_version": b"go version go1.26.3 linux/amd64",
        "gcc_version": b"13.3.0",
        "readelf_version": b"GNU readelf",
    }
    require(role in expected and expected[role] in output,
            "validate the actual complete pinned compiler or ELF tool version")


def audit_header(data: bytes) -> None:
    require(b"Code generated by cmd/cgo" in data
            and b"DO NOT EDIT" in data and b"GoUint64" in data,
            "require a genuine compiler-generated owned Go cgo header")
    for name in GO_EXPORTS:
        require((name + "(").encode("ascii") in data,
                "require each genuine owned export in the generated Go cgo header")
    validate_no_delegation(data, "generated Go cgo header")


def audit_elf(kind: str, observations: dict[str, bytes]) -> dict[str, Any]:
    require(kind in ("engine", "bridge") and set(observations)
            == {"dynamic", "symbols", "sections", "notes"},
            "require all four independently recorded ELF inspection outputs")
    dynamic = observations["dynamic"]
    symbols = observations["symbols"]
    sections = observations["sections"]
    notes = observations["notes"]
    require(bool(dynamic) and bool(symbols) and bool(sections)
            and b".dynsym" in sections,
            "require genuine complete native ELF dynamic, symbols, and sections")
    for token in (b"libpcre", b"onig", b"hyperscan", b"_rust_engine",
                  b"_zig_probe", b"_cpp_bridge", b"_fortran_engine", b"_sre"):
        require(token not in dynamic.lower() and token not in symbols.lower(),
                "reject external-regex or cross-family dynamic native dependencies")
    required = []
    if kind == "engine":
        for name in GO_EXPORTS:
            require(any(line.split() and line.split()[-1] == name.encode("ascii")
                        for line in symbols.splitlines()),
                    "require all nine actual first-party Go engine ELF exports")
            required.append(name)
    else:
        require(b"_go_engine.so" in dynamic and b"$ORIGIN" in dynamic,
                "require only the original phase-local Go engine and $ORIGIN RUNPATH")
        require(b"PyInit__go_bridge" in symbols,
                "preserve the authentic owned Python 3.14 Go bridge initializer")
    return {"kind": kind, "required_owned_exports": required,
            "required_owned_export_count": len(required),
            "dynamic_sha256": digest(dynamic),
            "symbols_sha256": digest(symbols),
            "sections_sha256": digest(sections),
            "notes_sha256": digest(notes),
            "external_regex_dependencies": 0,
            "cross_family_engine_dependencies": 0,
            "stdlib_regex_engine_dependencies": 0}


def evidence_names(label: str, *, failed: bool) -> tuple[str, str]:
    checked_label(label)
    middle = "native-source-build-v13-go-" + label
    if failed:
        middle += "-failures"
    return middle + ".json.gz", middle + "-publication-receipt.json"


def fsync_directory(path: Path) -> dict[str, Any]:
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    handle: int | None = None
    try:
        handle = os.open(str(path), flags)
        before = os.fstat(handle)
        require(stat.S_ISDIR(before.st_mode) and before.st_uid == os.geteuid()
                and stat.S_IMODE(before.st_mode) == 0o700,
                "require the authentic private mode-0700 evidence directory")
        os.fsync(handle)
        return {"path": str(path), "device": before.st_dev,
                "inode": before.st_ino, "directory_fsync_completed": True}
    except OSError as error:
        raise BuildError("cannot durably synchronize the owned evidence directory") from error
    finally:
        if handle is not None:
            os.close(handle)


def publish_report(report: dict[str, Any], label: str) -> dict[str, Any]:
    checked_label(label)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "bound the complete future success or preserved failure report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_REPORT_BYTES,
            "bound the deterministic future single-member source-build archive")
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(label, failed=failed)
    directory = ROOT / EVIDENCE_RELATIVE
    archive = exclusive_private_file(directory / archive_name, compressed)
    archive_sync = fsync_directory(directory)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt", "version": 13,
        "status": "PASS", "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": report.get("status"), "family": "go", "label": label,
        "source_sha256": report.get("source_sha256"),
        "protocol_sha256": report.get("protocol_sha256"),
        "contract_sha256": report.get("contract_sha256"),
        "archive": {**archive,
                    "relative": EVIDENCE_RELATIVE + "/" + archive_name,
                    "directory_fsync_completed": archive_sync["directory_fsync_completed"]},
        "uncompressed_sha256": digest(plain), "uncompressed_bytes": len(plain),
        "actual_compiler_process_count": report.get("actual_compiler_process_count"),
        "expected_compiler_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
        "actual_source_apply_count": report.get("actual_source_apply_count"),
        "actual_candidate_workers_started": 0,
        "candidate_correctness": "NOT MEASURED",
        "corrected_go_matching": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "winner_selected": False,
        "failure_preserved": failed, "receipt_self_publication": "NOT CLAIMED",
    }
    published_receipt = exclusive_private_file(directory / receipt_name, canonical(receipt))
    receipt_sync = fsync_directory(directory)
    return {"schema": SCHEMA + "-published-build", "version": 13,
            "status": report.get("status"), "family": "go", "label": label,
            "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
            "archive_sha256": archive["sha256"],
            "receipt_relative": EVIDENCE_RELATIVE + "/" + receipt_name,
            "receipt_sha256": published_receipt["sha256"],
            "archive_directory_fsync_completed": archive_sync["directory_fsync_completed"],
            "receipt_directory_fsync_completed": receipt_sync["directory_fsync_completed"],
            "failure_preserved": failed,
            "actual_compiler_process_count": report.get("actual_compiler_process_count"),
            "actual_source_apply_count": report.get("actual_source_apply_count"),
            "candidate_correctness": "NOT MEASURED", "performance": "NOT MEASURED",
            "holdout": "NOT OPENED"}


def run_build(source_pin: str, protocol_pin: str, contract_pin: str,
              label: str) -> tuple[int, dict[str, Any]]:
    checked_label(label)
    context, derived = verify_frozen_context(source_pin, protocol_pin, contract_pin)
    raw = {owner.path: read_owner(owner)[0] for owner in GO_OWNERS}
    workdir = tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/tmp")
    checked_workdir(workdir)
    root_stat = os.stat(workdir, follow_symlinks=False)
    require(stat.S_ISDIR(root_stat.st_mode) and stat.S_IMODE(root_stat.st_mode) == 0o700
            and root_stat.st_uid == os.geteuid(),
            "require a genuinely fresh mode-0700 independently owned private root")
    processes: list[dict[str, Any]] = []
    source_applies = 0
    phases: list[dict[str, Any]] = []
    try:
        for phase in PHASE_NAMES:
            paths = phase_paths(workdir, phase)
            create_private_directory(paths["base"])
            for key in ("source", "native", "temporary", "go_build_cache",
                        "go_module_cache", "go_module_directory"):
                create_private_directory(paths[key])
            create_private_directory(paths["source"] / "candidates")
            create_private_directory(paths["original_go_directory"])
        for phase in PHASE_NAMES:
            paths = phase_paths(workdir, phase)
            snapshots: list[dict[str, Any]] = []
            for owner in GO_OWNERS:
                snapshots.append(exclusive_private_file(paths["source"] / owner.path,
                                                        raw[owner.path]))
            snapshots.append(exclusive_private_file(paths["go_module_directory"] / "go.mod",
                                                    raw[GO_OWNERS[1].path]))
            snapshots.append(exclusive_private_file(paths["go_module_directory"] / "engine.go",
                                                    derived))
            source_applies += 1
            outputs: dict[str, dict[str, Any]] = {}
            inspections: dict[str, dict[str, bytes]] = {"engine": {}, "bridge": {}}
            phase_processes: list[dict[str, Any]] = []
            for role in PROCESS_ROLES:
                record = run_process(workdir, phase, role)
                output = record.pop("stdout_bytes_for_audit")
                processes.append(record)
                phase_processes.append(record)
                if role in ("readelf_version", "gcc_version", "go_version"):
                    validate_version_output(role, output)
                elif role == "build_go_engine":
                    header, header_snapshot = read_private_artifact(paths["artifact_generated_header"])
                    audit_header(header)
                    _, outputs["engine"] = read_private_artifact(paths["artifact_engine"])
                    outputs["generated_header"] = header_snapshot
                elif role == "build_go_bridge":
                    _, outputs["bridge"] = read_private_artifact(paths["artifact_bridge"])
                else:
                    kind, operation = role.split("_", 1)
                    inspections[kind][operation] = output
            audits = {kind: audit_elf(kind, observations)
                      for kind, observations in inspections.items()}
            require(len(phase_processes) == EXPECTED_PHASE_PROCESS_COUNT,
                    "count a complete future phase only after all 13 actual roles pass")
            phases.append({"phase": phase, "source_snapshots": snapshots,
                           "artifacts": outputs, "elf_audits": audits,
                           "actual_process_count": len(phase_processes),
                           "actual_source_apply_count": 1})
        require(len(phases) == len(PHASE_NAMES)
                and len(processes) == EXPECTED_PROCESS_COUNT
                and source_applies == len(PHASE_NAMES),
                "require exactly two completed independent 13-process Go build phases")
        for kind in ("engine", "generated_header", "bridge"):
            first = phases[0]["artifacts"][kind]
            second = phases[1]["artifacts"][kind]
            require(first["sha256"] == second["sha256"]
                    and first["bytes"] == second["bytes"]
                    and first["inode"] != second["inode"],
                    "require separately created byte-identical Go native " + kind)
        report: dict[str, Any] = {
            "schema": SCHEMA + "-actual-build-report", "version": 13,
            "status": "PASS", "family": "go", "label": label,
            "source_sha256": source_pin, "protocol_sha256": protocol_pin,
            "contract_sha256": contract_pin,
            "historical_v33_repository_evidence_owner_lower_bound":
                V33_EVIDENCE_OWNER_LOWER_BOUND,
            "historical_v33_authenticated_reference_lower_bound":
                V33_AUTHENTICATED_REFERENCE_LOWER_BOUND,
            "append_only_later_evidence_permitted": True,
            "actual_compiler_process_count": len(processes),
            "expected_compiler_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
            "actual_source_apply_count": source_applies,
            "actual_completed_phase_count": len(phases),
            "actual_processes": processes, "phases": phases,
            "original_engine_sha256": GO_ORIGINAL_SHA256,
            "derived_engine_sha256": GO_DERIVED_SHA256,
            "actual_candidate_workers_started": 0,
            "actual_candidate_imports": 0,
            "actual_native_libraries_loaded": 0,
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "stdlib_regex_engine_dependency_count": 0,
            "corrected_go_matching": "NOT MEASURED",
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "winner_selected": False,
            "source_context_sha256": digest(canonical(context)),
        }
        return 0, publish_report(report, label)
    except (BuildError, OSError, ValueError, subprocess.SubprocessError) as error:
        report = {
            "schema": SCHEMA + "-actual-build-report", "version": 13,
            "status": "FAIL", "family": "go", "label": label,
            "source_sha256": source_pin, "protocol_sha256": protocol_pin,
            "contract_sha256": contract_pin,
            "historical_v33_repository_evidence_owner_lower_bound":
                V33_EVIDENCE_OWNER_LOWER_BOUND,
            "historical_v33_authenticated_reference_lower_bound":
                V33_AUTHENTICATED_REFERENCE_LOWER_BOUND,
            "append_only_later_evidence_permitted": True,
            "actual_compiler_process_count": len(processes),
            "expected_compiler_process_count_only_after_success": EXPECTED_PROCESS_COUNT,
            "actual_source_apply_count": source_applies,
            "actual_completed_phase_count": len(phases),
            "actual_processes": processes, "phases": phases,
            "failure_class": type(error).__name__, "failure": str(error),
            "actual_candidate_workers_started": 0,
            "corrected_go_matching": "NOT MEASURED",
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "winner_selected": False,
        }
        return 1, publish_report(report, label)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--verify-frozen-context", action="store_true")
    mode.add_argument("--emit-contract", "--render-contract", dest="emit_contract",
                      action="store_true")
    mode.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    result = parser.parse_args(arguments)
    checked_digest(result.source_sha256, "V13 source")
    checked_digest(result.protocol_sha256, "V13 protocol")
    if result.emit_contract:
        require(result.contract_sha256 is None and result.label is None,
                "contract emission accepts only the two independent source pins")
    else:
        checked_digest(result.contract_sha256, "V13 contract")
        if result.build:
            checked_label(result.label)
        else:
            require(result.label is None, "reserve publication labels for explicit builds")
    return result


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        runtime()
        args = parse_arguments(arguments)
        if args.emit_contract:
            source, _ = read_owner(Owner(SOURCE_RELATIVE, args.source_sha256, None))
            protocol, _ = read_owner(Owner(PROTOCOL_RELATIVE, args.protocol_sha256, None))
            require(bool(source) and bool(protocol), "authenticate both caller-pinned contract owners")
            result = contract_document(args.source_sha256, args.protocol_sha256)
            code = 0
        elif args.self_test:
            result = self_test(args.source_sha256, args.protocol_sha256, args.contract_sha256)
            code = 0
        elif args.verify_frozen_context:
            result, _ = verify_frozen_context(args.source_sha256, args.protocol_sha256,
                                              args.contract_sha256)
            code = 0
        else:
            code, result = run_build(args.source_sha256, args.protocol_sha256,
                                     args.contract_sha256, args.label)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return code
    except (BuildError, OSError, ValueError, TypeError, UnicodeError) as error:
        sys.stderr.write("go-unicode-source-build-v13: " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
