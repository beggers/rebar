#!/usr/bin/env python3
"""Freeze and, only when separately authorized, build the corrected owned Rust."""

from __future__ import annotations

import argparse
import builtins
import contextlib
import copy
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import io
import json
import os
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-rust-pattern-repr-source-build-v13"
VERSION = 13
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_pattern_repr_source_build_v13.py"
PROTOCOL_PATH = "oracle/phase2/RUST-PATTERN-REPR-SOURCE-BUILD-V13.md"
CONTRACT_PATH = "oracle/phase2/rust-pattern-repr-source-build-v13.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_TOOLCHAIN_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 2 * 1024 * 1024
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
PHASES = ("reference-a", "reference-b")
SUITE_COUNT = 13
CASE_COUNT = 31237
PRIVATE_WAIVERS = 13
CURRENT_EVIDENCE_OWNERS = 155
CURRENT_HISTORY_REFERENCES = 160
HISTORICAL_V34_EVIDENCE_OWNERS = 157
HISTORICAL_V34_HISTORY_REFERENCES = 162
ACTUAL_EVIDENCE_OWNERS = 159
ACTUAL_HISTORY_REFERENCES = 164
HISTORICAL_V33_ZIG_MISMATCHES = 2172
HISTORICAL_V33_ZIG_VERIFIED_PASSES = 2847
ACTUAL_ZIG_V3_MISMATCHES = 1764
ACTUAL_ZIG_V3_VERIFIED_PASSES = 3711
SUPPLEMENT_CASE_COUNT = 50
SUPPLEMENT_REFERENCE_PROCESS_COUNT = 2
SUPPLEMENT_MATRIX_SHA256 = "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
BRIDGE_PATH = "candidates/rust/py_bridge.c"
BRIDGE_DERIVED_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
BRIDGE_DERIVED_BYTES = 176118
PUBLIC_PATH = "candidates/rust_candidate.py"
PUBLIC_DERIVED_SHA256 = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
PUBLIC_DERIVED_BYTES = 31934
HISTORICAL_PUBLIC_DERIVED_SHA256 = "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
ENGINE_NAME = "_rust_engine.so"
BRIDGE_NAME = "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True, slots=True)
class ToolOwner:
    path: str
    sha256: str
    size: int
    device: int
    inode: int
    mode: int
    uid: int
    nlink: int = 1


GOAL = Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
RUST_OWNERS = (
    Owner("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    Owner("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    Owner(BRIDGE_PATH, "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
    Owner("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    Owner("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    Owner("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    Owner("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    Owner("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    Owner(PUBLIC_PATH, "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
)
BRIDGE_REPAIR = (
    Owner("tools/apply_owned_rust_source_repair_v1.py", "1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851", 59388),
    Owner("oracle/phase2/RUST-SOURCE-REPAIR-V1.md", "df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b", 5496),
    Owner("oracle/phase2/rust-source-repair-v1.json", "1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b", 8306),
)
PUBLIC_REPAIR_V3 = (
    Owner("tools/apply_owned_rust_public_contract_source_repair_v3.py", "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060),
    Owner("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md", "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405),
    Owner("oracle/phase2/rust-public-contract-source-repair-v3.json", "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817),
)

PREVIOUS_BUILD_V12 = (
    Owner("tools/reproduce_owned_rust_flag_source_build_v12.py", "1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6", 86933),
    Owner("oracle/phase2/RUST-FLAG-SOURCE-BUILD-V12.md", "822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950", 5567),
    Owner("oracle/phase2/rust-flag-source-build-v12.json", "c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592", 13038),
)
PREVIOUS_BUILD_ARCHIVE = Owner("oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz", "840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d", 108325)
PREVIOUS_BUILD_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-publication-receipt.json", "1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f", 2109)
RUST_MATCH_ARCHIVE = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures.json.gz", "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f", 3663299)
RUST_MATCH_RECEIPT = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json", "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3", 4674)
ZIG_V12_ARCHIVE = Owner("oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2.json.gz", "3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d", 48371)
ZIG_V12_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2-publication-receipt.json", "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b", 2029)
ZIG_V3_MATCH_ARCHIVE = Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures.json.gz", "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b", 3722337)
ZIG_V3_MATCH_RECEIPT = Owner("oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures-publication-receipt.json", "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96", 4111)
SUPPLEMENT = Owner("oracle/phase1/p0-callable-introspection-v1.json", "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749)
SUPPLEMENT_SOURCE = Owner("tools/verify_python_re_callable_introspection_v1.py", "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653", 75608)
SUPPLEMENT_PROTOCOL = Owner("oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md", "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8", 8952)
SUPPLEMENT_REFERENCE_V2 = (
    Owner("tools/run_owned_callable_introspection_reference_v2.py", "00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4", 86258),
    Owner("oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md", "1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f", 7487),
    Owner("oracle/phase1/callable-introspection-reference-v2.json", "0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42", 7253),
)
SUPPLEMENT_REFERENCE_ARCHIVE = Owner("oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6.json.gz", "7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c", 8538)
SUPPLEMENT_REFERENCE_RECEIPT = Owner("oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json", "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334", 3533)
ACTUAL_FIRST_MISMATCH = "pattern-and-match-representation/058"
ACTUAL_FIRST_MISMATCH_SHA256 = "1130da7818fe8b27a0d74f607bd4531c43f5f12ec9d6674419aa448786884d75"

V9_KERNEL = (
    Owner("tools/reproduce_owned_native_source_build_v9.py", "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f", 81124),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V9.md", "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc", 4960),
    Owner("oracle/phase2/native-source-build-v9.json", "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da", 9134),
)
V7_KERNEL = (
    Owner("tools/reproduce_owned_native_source_build_v7.py", "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7", 300624),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V7.md", "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313", 8063),
    Owner("oracle/phase2/native-source-build-v7.json", "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819", 28924),
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

TOOLCHAIN = (
    ToolOwner("/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/rustc", "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6", 644784, 2064, 31359570, 0o755, 1000),
    ToolOwner("/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/cargo", "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66", 42185192, 2064, 31359488, 0o755, 1000),
    ToolOwner("/usr/bin/x86_64-linux-gnu-gcc-13", "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26", 1023032, 1048708, 10445975, 0o755, 65534),
    ToolOwner("/usr/bin/x86_64-linux-gnu-readelf", "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0", 789280, 1048708, 10446013, 0o755, 65534),
)


class GateError(Exception):
    """Reject a substituted owner, unsafe operation, or unproved build."""


class ForbiddenEffect(GateError):
    """A source-only self-test physically blocked a real outside effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise GateError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact, complete bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                           allow_nan=False, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise GateError("reject noncanonical machine evidence") from error


def checked_sha256(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require an exact, lowercase caller-pinned SHA-256: " + label)
    return value


def owner_document(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size}


def tool_document(owner: ToolOwner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size,
            "device": owner.device, "inode": owner.inode, "mode": owner.mode,
            "uid": owner.uid, "nlink": owner.nlink}


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "reject a duplicate JSON key in " + label)
            result[key] = value
        return result

    def constant(_value: str) -> Any:
        raise GateError("reject a nonfinite JSON number in " + label)

    try:
        document = json.loads(raw.decode("utf-8", "strict"),
                              object_pairs_hook=unique, parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GateError("reject malformed JSON: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "require an exact canonical JSON object: " + label)
    return document


def verify_runtime() -> None:
    require(sys.executable == PYTHON
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "require the pinned, isolated, bytecode-free CPython 3.14.6 oracle")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "never import or activate a candidate in a Rust build source gate")


def checked_relative(value: str) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one exact bounded repository-relative owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value
            and all(piece not in ("", ".", "..") for piece in parsed.parts)
            and "\\" not in value,
            "reject an escaped, redirected, or ambiguous repository owner")
    return parsed.parts


def read_owner(owner: Owner) -> tuple[bytes, dict[str, Any]]:
    require(type(owner) is Owner and 0 < owner.size <= MAX_SOURCE_BYTES,
            "bound every immutable, first-party repository owner")
    checked_sha256(owner.sha256, owner.path)
    parts = checked_relative(owner.path)
    directory_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_NOFOLLOW", 0))
    file_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                  | getattr(os, "O_NOFOLLOW", 0))
    folders: list[int] = []
    handle: int | None = None
    try:
        folders.append(os.open(str(ROOT), directory_flags))
        for part in parts[:-1]:
            visible = os.stat(part, dir_fd=folders[-1], follow_symlinks=False)
            child = os.open(part, directory_flags, dir_fd=folders[-1])
            folders.append(child)
            found = os.fstat(child)
            require(stat.S_ISDIR(found.st_mode)
                    and (found.st_dev, found.st_ino)
                    == (visible.st_dev, visible.st_ino),
                    "reject a substituted or symlinked source-owner parent")
        visible = os.stat(parts[-1], dir_fd=folders[-1], follow_symlinks=False)
        handle = os.open(parts[-1], file_flags, dir_fd=folders[-1])
        before = os.fstat(handle)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and before.st_size == owner.size
                and (before.st_dev, before.st_ino, before.st_size,
                     before.st_uid, before.st_nlink)
                == (visible.st_dev, visible.st_ino, visible.st_size,
                    visible.st_uid, visible.st_nlink),
                "reject a linked, foreign, truncated, or exchanged owner: "
                + owner.path)
        chunks: list[bytes] = []
        remaining = owner.size
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            require(type(piece) is bytes and bool(piece),
                    "reject a truncated descriptor-bound immutable owner")
            chunks.append(piece)
            remaining -= len(piece)
        require(os.read(handle, 1) == b"", "reject an appended immutable owner")
        raw = b"".join(chunks)
        after = os.fstat(handle)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and digest(raw) == owner.sha256,
                "reject an owner changed during complete authentication: "
                + owner.path)
        return raw, {**owner_document(owner), "device": after.st_dev,
                     "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
                     "uid": after.st_uid, "nlink": after.st_nlink}
    finally:
        if handle is not None:
            os.close(handle)
        for folder in reversed(folders):
            os.close(folder)


def read_toolchain(owner: ToolOwner) -> dict[str, Any]:
    require(type(owner) is ToolOwner and 0 < owner.size <= MAX_TOOLCHAIN_BYTES,
            "bound every separately authenticated native tool")
    checked_sha256(owner.sha256, owner.path)
    require(PurePosixPath(owner.path).is_absolute(),
            "pin every compiler and inspector to an exact absolute owner")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    visible = os.stat(owner.path, follow_symlinks=False)
    descriptor = os.open(owner.path, flags)
    try:
        before = os.fstat(descriptor)
        expected = (owner.device, owner.inode, owner.size, owner.uid,
                    owner.nlink, owner.mode)
        actual = (before.st_dev, before.st_ino, before.st_size, before.st_uid,
                  before.st_nlink, stat.S_IMODE(before.st_mode))
        require(stat.S_ISREG(before.st_mode) and actual == expected
                and (visible.st_dev, visible.st_ino, visible.st_size,
                     visible.st_uid, visible.st_nlink,
                     stat.S_IMODE(visible.st_mode)) == expected,
                "reject a substituted, linked, or unpinned compiler: " + owner.path)
        hashed = hashlib.sha256()
        remaining = owner.size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(piece) is bytes and bool(piece),
                    "reject truncated streaming toolchain authentication")
            hashed.update(piece)
            remaining -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "reject an appended compiler or native inspector")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and hashed.hexdigest() == owner.sha256,
                "reject a tool altered during complete streaming authentication")
        return tool_document(owner)
    finally:
        os.close(descriptor)


def boundary() -> dict[str, Any]:
    return {
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "qualified_candidate_count": 0, "candidate_imports": 0,
        "candidate_workers_started": 0, "candidate_processes_started": 0,
        "reference_processes_started": 0, "compiler_processes_started": 0,
        "native_builds_started": 0, "source_builds_started": 0,
        "native_libraries_loaded": 0, "native_activations": 0,
        "canonical_native_target_reads": 0,
        "canonical_native_target_stats": 0, "source_apply_count": 0,
        "workspace_mutations": 0, "network_requests": 0,
        "threads_started": 0, "signal_handlers_installed": 0,
        "signal_masks_installed": 0, "recovery_locks_acquired": 0,
        "recovery_journals_created": 0, "clock_samples": 0,
        "timing_trials_run": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "uncompressed_c_archive_bytes_read": 0,
        "uncompressed_rust_archive_bytes_read": 0,
        "uncompressed_zig_archive_bytes_read": 0,
        "uncompressed_phase1_reference_archive_bytes_read": 0,
        "upstream_test_processes_started": 0,
        "upstream_unittest_methods_executed": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
    }


def current_history() -> dict[str, Any]:
    return {
        "historical_graph_version": 33,
        "historical_graph_versions": [33, 34],
        "historical_v33_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "historical_v33_reference_count": CURRENT_HISTORY_REFERENCES,
        "historical_v34_evidence_owner_count":
            HISTORICAL_V34_EVIDENCE_OWNERS,
        "historical_v34_reference_count":
            HISTORICAL_V34_HISTORY_REFERENCES,
        "historical_v34_supplementary_signature_reference_status": "NOT RUN",
        "historical_v34_supplementary_signature_reference_cases_executed": 0,
        "repository_evidence_owner_lower_bound": ACTUAL_EVIDENCE_OWNERS,
        "authenticated_reference_lower_bound": ACTUAL_HISTORY_REFERENCES,
        "later_append_only_evidence_allowed": True,
        "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVERS,
        "rust_status": "FAIL", "rust_semantic_mismatch_count": 1036,
        "rust_verified_passing_case_count": 8965,
        "rust_actual_candidate_workers": 13,
        "rust_infrastructure_failure_count": 0,
        "actual_first_failure_case": ACTUAL_FIRST_MISMATCH,
        "actual_first_failure_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
        "actual_first_failure_suite": "public_types_v1",
        "actual_first_failure_suite_mismatches": 140,
        "c_status": "FAIL", "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "historical_v33_zig_status": "FAIL",
        "historical_v33_zig_semantic_mismatch_count":
            HISTORICAL_V33_ZIG_MISMATCHES,
        "historical_v33_zig_verified_passing_case_count":
            HISTORICAL_V33_ZIG_VERIFIED_PASSES,
        "last_tested_zig_status": "FAIL",
        "last_tested_zig_semantic_mismatch_count": ACTUAL_ZIG_V3_MISMATCHES,
        "last_tested_zig_verified_passing_case_count":
            ACTUAL_ZIG_V3_VERIFIED_PASSES,
        "actual_zig_v3_matching_status": "FAIL",
        "actual_zig_v3_semantic_mismatch_count": ACTUAL_ZIG_V3_MISMATCHES,
        "actual_zig_v3_verified_passing_case_count":
            ACTUAL_ZIG_V3_VERIFIED_PASSES,
        "actual_zig_v3_candidate_worker_count": SUITE_COUNT,
        "actual_zig_v3_infrastructure_failure_count": 0,
        "zig_v12_build_status": "PASS",
        "zig_v12_compiler_process_count": 26,
        "zig_v12_source_apply_count": 2,
        "zig_v12_matching": "FAIL",
        "zig_v12_matching_campaign_version": 3,
        "supplementary_signature_case_count": SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_status": "PASS",
        "supplementary_signature_reference_cases_executed":
            SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_process_count":
            SUPPLEMENT_REFERENCE_PROCESS_COUNT,
        "supplementary_signature_reference_failure_count": 0,
        "supplementary_signature_candidate_status": "NOT RUN",
        "supplementary_signature_candidate_cases_executed": 0,
        "supplementary_signature_cases_included_in_original_denominator":
            False,
        "qualified_candidate_count": 0,
        "corrected_rust_candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_holdout_opened": False, "winner_selected": False,
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    source_pin = checked_sha256(source_pin, "V13 source")
    protocol_pin = checked_sha256(protocol_pin, "V13 protocol")
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "phase": "CORRECTED FIRST-PARTY RUST SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "goal": owner_document(GOAL),
        "phase_one": owner_document(PHASE_ONE),
        "runtime": {"implementation": "CPython", "version": "3.14.6",
                    "path": PYTHON, "sha256": PYTHON_SHA256,
                    "isolated": True, "bytecode_writes": False},
        "oracle": {"suite_count": SUITE_COUNT,
                   "case_execution_denominator": CASE_COUNT,
                   "named_private_waiver_count": PRIVATE_WAIVERS,
                   "manifest": owner_document(PHASE_ONE),
                   "supplement": owner_document(SUPPLEMENT),
                   "supplementary_signature_case_count": SUPPLEMENT_CASE_COUNT,
                   "supplementary_signature_reference_status": "PASS",
                   "supplementary_signature_reference_cases_executed":
                       SUPPLEMENT_CASE_COUNT,
                   "supplementary_signature_reference_process_count":
                       SUPPLEMENT_REFERENCE_PROCESS_COUNT,
                   "supplementary_signature_candidate_status": "NOT RUN",
                   "supplementary_signature_candidate_cases_executed": 0,
                   "supplementary_signature_cases_included_in_original_denominator":
                       False},
        "current_history": current_history(),
        "historical_graph_v33": [owner_document(item) for item in V33],
        "historical_graph_v34": [owner_document(item) for item in V34],
        "actual_v4_rust_matching": {
            "archive": owner_document(RUST_MATCH_ARCHIVE),
            "receipt": owner_document(RUST_MATCH_RECEIPT),
            "candidate_status": "FAIL", "semantic_mismatch_count": 1036,
            "verified_passing_case_count": 8965,
            "first_actual_case": ACTUAL_FIRST_MISMATCH,
            "first_actual_case_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
            "archive_decompressed": False},
        "actual_zig_v12_build": {
            "archive": owner_document(ZIG_V12_ARCHIVE),
            "receipt": owner_document(ZIG_V12_RECEIPT),
            "actual_compiler_process_count": 26,
            "actual_source_apply_count": 2,
            "candidate_matching": "FAIL",
            "matching_campaign_version": 3,
            "matching_semantic_mismatch_count": ACTUAL_ZIG_V3_MISMATCHES,
            "matching_verified_passing_case_count":
                ACTUAL_ZIG_V3_VERIFIED_PASSES,
            "archive_decompressed": False},
        "actual_v3_zig_matching": {
            "archive": owner_document(ZIG_V3_MATCH_ARCHIVE),
            "receipt": owner_document(ZIG_V3_MATCH_RECEIPT),
            "candidate_status": "FAIL",
            "semantic_mismatch_count": ACTUAL_ZIG_V3_MISMATCHES,
            "verified_passing_case_count": ACTUAL_ZIG_V3_VERIFIED_PASSES,
            "actual_candidate_worker_count": SUITE_COUNT,
            "completed_suite_count": SUITE_COUNT,
            "infrastructure_failure_count": 0,
            "resulting_repository_evidence_owner_count":
                HISTORICAL_V34_EVIDENCE_OWNERS,
            "resulting_authenticated_reference_count":
                HISTORICAL_V34_HISTORY_REFERENCES,
            "archive_decompressed": False},
        "actual_v2_callable_introspection_reference": {
            "frozen_v1_source": owner_document(SUPPLEMENT_SOURCE),
            "frozen_v1_protocol": owner_document(SUPPLEMENT_PROTOCOL),
            "frozen_v1_contract": owner_document(SUPPLEMENT),
            "frozen_v2_owners": [owner_document(item)
                                  for item in SUPPLEMENT_REFERENCE_V2],
            "archive": owner_document(SUPPLEMENT_REFERENCE_ARCHIVE),
            "receipt": owner_document(SUPPLEMENT_REFERENCE_RECEIPT),
            "reference_status": "PASS",
            "reference_failure_count": 0,
            "additional_case_count": SUPPLEMENT_CASE_COUNT,
            "additional_cases_included_in_original_denominator": False,
            "actual_reference_process_count":
                SUPPLEMENT_REFERENCE_PROCESS_COUNT,
            "actual_distinct_process_ids": [81, 82],
            "matrix_sha256": SUPPLEMENT_MATRIX_SHA256,
            "candidate_status": "NOT RUN",
            "candidate_cases_executed": 0,
            "resulting_evidence_owner_lower_bound": ACTUAL_EVIDENCE_OWNERS,
            "resulting_reference_lower_bound": ACTUAL_HISTORY_REFERENCES,
            "archive_decompressed": False,
            "holdout": "NOT OPENED"},
        "preserved_actual_v12": {
            "owners": [owner_document(item) for item in PREVIOUS_BUILD_V12],
            "actual_archive": owner_document(PREVIOUS_BUILD_ARCHIVE),
            "actual_receipt": owner_document(PREVIOUS_BUILD_RECEIPT),
            "actual_status": "PASS", "actual_process_count": 28,
            "actual_bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "actual_historical_public_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "historical_public_adapter_reused": False,
            "historical_archive_decompressed": False,
            "historical_source_modified": False,
            "historical_protocol_modified": False,
            "historical_contract_modified": False,
            "v10_high_level_context_called": False,
            "v10_snapshot_called": False,
            "v10_reproduction_called": False,
            "v11_build_called": False,
        },
        "first_party_rust_source": {
            "family": FAMILY, "owners": [owner_document(item)
                                             for item in RUST_OWNERS],
            "owner_count": len(RUST_OWNERS),
            "cargo_package_count": 1, "external_dependency_count": 0,
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "stdlib_re_engine": "FORBIDDEN", "cpython_sre_engine": "FORBIDDEN",
            "third_party_regex_engine": "FORBIDDEN",
            "other_candidate_engine": "FORBIDDEN", "fallback": "FORBIDDEN",
            "canonical_source_mutation": "FORBIDDEN",
        },
        "first_party_bridge_overlay": {
            "owners": [owner_document(item) for item in BRIDGE_REPAIR],
            "original": owner_document(RUST_OWNERS[2]),
            "derived": {"path": BRIDGE_PATH,
                        "sha256": BRIDGE_DERIVED_SHA256,
                        "bytes": BRIDGE_DERIVED_BYTES,
                        "materialized": False},
            "application": "EXACTLY ONCE PER EXPLICIT FUTURE PRIVATE PHASE",
        },
        "corrected_first_party_public_overlay": {
            "owners": [owner_document(item) for item in PUBLIC_REPAIR_V3],
            "original": owner_document(RUST_OWNERS[-1]),
            "derived": {"path": PUBLIC_PATH,
                        "sha256": PUBLIC_DERIVED_SHA256,
                        "bytes": PUBLIC_DERIVED_BYTES,
                        "materialized": False},
            "actual_previously_tested_v12_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "actual_first_failure_case": ACTUAL_FIRST_MISMATCH,
            "actual_first_failure_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
            "preserved_standalone_flag_vector_count": 5128,
            "historical_v1_reused": False,
            "application": "EXACTLY ONCE PER EXPLICIT FUTURE PRIVATE PHASE",
        },
        "low_level_first_party_kernels": {
            "v9": [owner_document(item) for item in V9_KERNEL],
            "v7": [owner_document(item) for item in V7_KERNEL],
            "v9_high_level_context_called": False,
            "v10_high_level_context_called": False,
            "v10_dual_snapshot_called": False,
            "v10_reproduction_called": False,
            "v11_high_level_build_called": False,
            "v13_owns_snapshot_and_reproduction": True,
        },
        "future_private_snapshot": {
            "explicit_build_required": True, "root_parent": "/tmp",
            "interoperable_previous_root_prefix": ROOT_PREFIX,
            "phase_names": list(PHASES),
            "both_distinct_phases_precreated": True,
            "directory_mode": "0700", "file_mode": "0600",
            "creation_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "complete_source_owners_per_phase": 9,
            "unchanged_source_owners_per_phase": 7,
            "bridge_overlays_per_phase": 1,
            "corrected_public_overlays_per_phase": 1,
            "existing_destinations": "FORBIDDEN",
            "borrowed_phase_inodes": "FORBIDDEN",
            "canonical_workspace_writes": "FORBIDDEN",
        },
        "future_native_build": {
            "explicit_build_required": True,
            "independent_nine_original_owner_pins_required": True,
            "independent_bridge_derived_pin_required": True,
            "independent_corrected_public_derived_pin_required": True,
            "phase_count": len(PHASES),
            "processes_per_phase": len(PROCESS_NAMES),
            "total_actual_processes_required": 2 * len(PROCESS_NAMES),
            "ordered_process_names_per_phase": list(PROCESS_NAMES),
            "unique_successful_process_ids_required": True,
            "toolchain": [tool_document(item) for item in TOOLCHAIN],
            "cargo_required_flags": ["--release", "--locked", "--offline",
                                      "--frozen", "--target-dir"],
            "cargo_net_offline": True, "network": "FORBIDDEN",
            "engine_name": ENGINE_NAME, "bridge_name": BRIDGE_NAME,
            "independent_phase_elf_inodes_required": True,
            "complete_raw_phase_elf_comparison_required": True,
            "native_loading": "FORBIDDEN", "candidate_execution": "FORBIDDEN",
            "prebuilt_artifacts": "FORBIDDEN",
            "passing_build_qualifies_candidate": False,
        },
        "future_evidence": {
            "explicit_build_required": True, "directory": EVIDENCE_PATH,
            "archive_prefix": "native-source-build-v13-rust-",
            "archive_suffix": ".json.gz", "failure_suffix": "-failures",
            "receipt_suffix": "-publication-receipt.json",
            "exclusive_creation": True, "no_follow": True,
            "file_mode": "0600", "zero_mtime_single_member_gzip": True,
            "same_inode_complete_readback": True,
            "archive_and_directory_fsync": True,
            "prebuild_repository_evidence_owner_lower_bound":
                ACTUAL_EVIDENCE_OWNERS,
            "prebuild_authenticated_reference_lower_bound":
                ACTUAL_HISTORY_REFERENCES,
            "later_append_only_evidence_allowed": True,
            "maximum_complete_uncompressed_report_bytes": MAX_REPORT_BYTES,
            "maximum_complete_compressed_report_bytes": MAX_REPORT_BYTES,
            "new_actual_owners_after_successful_publication_only": 2,
            "publication_qualifies_candidate": False,
        },
        "phase_boundary": boundary(),
    }


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {kind: 0 for kind in (
            "filesystem", "write", "process", "import", "network", "thread",
            "clock", "native", "lock", "signal", "decompression")}

    def deny(self, owner: Any, name: str, kind: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise ForbiddenEffect("physically blocked source-only " + kind
                                  + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names, kind in (
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat",
                    "resolve"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename",
                  "replace", "fsync"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename",
                    "replace"), "write"),
            (tempfile, ("mkdtemp", "mkstemp"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output"), "process"),
            (importlib, ("import_module",), "import"),
            (socket, ("socket", "create_connection"), "network"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time"),
             "clock"),
            (ctypes, ("CDLL", "PyDLL"), "native"),
            (fcntl, ("flock", "lockf"), "lock"),
            (signal, ("signal", "pthread_sigmask"), "signal"),
            (gzip, ("decompress", "open", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        ):
            for name in names:
                self.deny(owner, name, kind)
        return self

    def __exit__(self, *_details: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def expected_source_owner(path: str) -> tuple[str, int]:
    matches = [item for item in RUST_OWNERS if item.path == path]
    require(len(matches) == 1, "require one unique canonical Rust source owner")
    item = matches[0]
    if path == BRIDGE_PATH:
        return BRIDGE_DERIVED_SHA256, BRIDGE_DERIVED_BYTES
    if path == PUBLIC_PATH:
        return PUBLIC_DERIVED_SHA256, PUBLIC_DERIVED_BYTES
    return item.sha256, item.size


def synthetic_plan() -> dict[str, Any]:
    phases: list[dict[str, Any]] = []
    for index, name in enumerate(PHASES):
        sources: dict[str, Any] = {}
        for offset, owner in enumerate(RUST_OWNERS):
            expected_sha, expected_bytes = expected_source_owner(owner.path)
            sources[owner.path] = {
                "sha256": expected_sha, "bytes": expected_bytes,
                "device": 9001, "inode": 10000 + 100 * index + offset,
                "mode": 0o600, "nlink": 1,
                "overlay_count": int(owner.path in (BRIDGE_PATH, PUBLIC_PATH)),
            }
        phases.append({
            "name": name, "directory_mode": 0o700,
            "directory_device": 9001, "directory_inode": 11000 + index,
            "fresh_source_owners": sources,
            "native_outputs": {
                "engine": {"file_name": ENGINE_NAME,
                           "sha256": digest(b"synthetic-owned-rust-engine"),
                           "size_bytes": 8192, "device": 9001,
                           "inode": 12000 + 10 * index},
                "bridge": {"file_name": BRIDGE_NAME,
                           "sha256": digest(b"synthetic-owned-rust-bridge"),
                           "size_bytes": 16384, "device": 9001,
                           "inode": 12001 + 10 * index},
            },
        })
    return {"family": FAMILY, "root_prefix": ROOT_PREFIX,
            "history_owner_count": ACTUAL_EVIDENCE_OWNERS,
            "history_reference_count": ACTUAL_HISTORY_REFERENCES,
            "actual_zig_v3_receipt_sha256": ZIG_V3_MATCH_RECEIPT.sha256,
            "actual_zig_v3_archive_sha256": ZIG_V3_MATCH_ARCHIVE.sha256,
            "actual_zig_v3_semantic_mismatch_count":
                ACTUAL_ZIG_V3_MISMATCHES,
            "actual_zig_v3_verified_passing_case_count":
                ACTUAL_ZIG_V3_VERIFIED_PASSES,
            "actual_zig_v3_candidate_worker_count": SUITE_COUNT,
            "supplementary_reference_receipt_sha256":
                SUPPLEMENT_REFERENCE_RECEIPT.sha256,
            "supplementary_reference_archive_sha256":
                SUPPLEMENT_REFERENCE_ARCHIVE.sha256,
            "supplementary_reference_status": "PASS",
            "supplementary_reference_case_count": SUPPLEMENT_CASE_COUNT,
            "supplementary_reference_process_count":
                SUPPLEMENT_REFERENCE_PROCESS_COUNT,
            "supplementary_candidate_status": "NOT RUN",
            "phases": phases,
            "processes": [{"name": name, "pid": 20000 + index,
                           "exit_status": 0}
                          for index, name in enumerate(PROCESS_NAMES * 2)],
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "cargo_external_dependency_count": 0,
            "network_requests": 0, "native_libraries_loaded": 0,
            "candidate_processes_started": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "holdout": "NOT OPENED", "candidate_qualified": False,
            "winner_selected": False}


def validate_synthetic_plan(plan: Any) -> dict[str, Any]:
    require(type(plan) is dict and plan.get("family") == FAMILY
            and plan.get("root_prefix") == ROOT_PREFIX
            and plan.get("history_owner_count") == ACTUAL_EVIDENCE_OWNERS
            and plan.get("history_reference_count") == ACTUAL_HISTORY_REFERENCES
            and plan.get("actual_zig_v3_receipt_sha256")
            == ZIG_V3_MATCH_RECEIPT.sha256
            and plan.get("actual_zig_v3_archive_sha256")
            == ZIG_V3_MATCH_ARCHIVE.sha256
            and plan.get("actual_zig_v3_semantic_mismatch_count")
            == ACTUAL_ZIG_V3_MISMATCHES
            and plan.get("actual_zig_v3_verified_passing_case_count")
            == ACTUAL_ZIG_V3_VERIFIED_PASSES
            and plan.get("actual_zig_v3_candidate_worker_count") == SUITE_COUNT
            and plan.get("supplementary_reference_receipt_sha256")
            == SUPPLEMENT_REFERENCE_RECEIPT.sha256
            and plan.get("supplementary_reference_archive_sha256")
            == SUPPLEMENT_REFERENCE_ARCHIVE.sha256
            and plan.get("supplementary_reference_status") == "PASS"
            and plan.get("supplementary_reference_case_count")
            == SUPPLEMENT_CASE_COUNT
            and plan.get("supplementary_reference_process_count")
            == SUPPLEMENT_REFERENCE_PROCESS_COUNT
            and plan.get("supplementary_candidate_status") == "NOT RUN"
            and plan.get("bridge_derived_sha256") == BRIDGE_DERIVED_SHA256
            and plan.get("public_derived_sha256") == PUBLIC_DERIVED_SHA256
            and plan.get("cargo_external_dependency_count") == 0
            and plan.get("network_requests") == 0
            and plan.get("native_libraries_loaded") == 0
            and plan.get("candidate_processes_started") == 0
            and plan.get("hidden_cases_read") == 0
            and plan.get("clock_samples") == 0
            and plan.get("holdout") == "NOT OPENED"
            and plan.get("candidate_qualified") is False
            and plan.get("winner_selected") is False,
            "reject stale history, delegation, activation, timing, or holdout")
    phases = plan.get("phases")
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases] == list(PHASES),
            "require exactly two ordered independent private Rust phases")
    phase_identities: set[tuple[int, int]] = set()
    source_identities: set[tuple[int, int]] = set()
    for phase in phases:
        require(type(phase) is dict and phase.get("directory_mode") == 0o700
                and type(phase.get("directory_device")) is int
                and type(phase.get("directory_inode")) is int,
                "require genuine private owner-only phase directories")
        identity = (phase["directory_device"], phase["directory_inode"])
        require(identity not in phase_identities,
                "reject aliased independent phase directories")
        phase_identities.add(identity)
        sources = phase.get("fresh_source_owners")
        require(type(sources) is dict
                and set(sources) == {item.path for item in RUST_OWNERS},
                "require seven originals and both complete private Rust overlays")
        for item in RUST_OWNERS:
            row = sources.get(item.path)
            expected_sha, expected_bytes = expected_source_owner(item.path)
            require(type(row) is dict and row.get("sha256") == expected_sha
                    and row.get("bytes") == expected_bytes
                    and row.get("mode") == 0o600 and row.get("nlink") == 1
                    and row.get("overlay_count")
                    == int(item.path in (BRIDGE_PATH, PUBLIC_PATH))
                    and type(row.get("device")) is int
                    and type(row.get("inode")) is int,
                    "reject an unowned or substituted source: " + item.path)
            identity = (row["device"], row["inode"])
            require(identity not in source_identities,
                    "reject a shared, linked, or reused phase source inode")
            source_identities.add(identity)
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                "require both first-party reproducible native output roles")
        for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
            output = outputs[role]
            expected = digest(("synthetic-owned-rust-" + role).encode("ascii"))
            require(type(output) is dict and output.get("file_name") == filename
                    and output.get("sha256") == expected
                    and type(output.get("size_bytes")) is int
                    and output["size_bytes"] > 0
                    and type(output.get("device")) is int
                    and type(output.get("inode")) is int,
                    "reject an incomplete or foreign synthetic ELF role")
    for role in ("engine", "bridge"):
        left = phases[0]["native_outputs"][role]
        right = phases[1]["native_outputs"][role]
        require(left["sha256"] == right["sha256"]
                and left["size_bytes"] == right["size_bytes"]
                and (left["device"], left["inode"])
                != (right["device"], right["inode"]),
                "reject irreproducible bytes or a borrowed phase-native inode")
    processes = plan.get("processes")
    require(type(processes) is list
            and len(processes) == 2 * len(PROCESS_NAMES),
            "require exactly 28 real ordered process slots")
    pids: set[int] = set()
    for index, row in enumerate(processes):
        require(type(row) is dict
                and row.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and type(row.get("pid")) is int and row["pid"] > 0
                and row["pid"] not in pids and row.get("exit_status") == 0,
                "reject a reordered, failed, invented, or reused build process")
        pids.add(row["pid"])
    return {"phase_count": len(phases), "source_owner_count_per_phase": 9,
            "unique_source_inode_count": len(source_identities),
            "native_roles_per_phase": 2,
            "unique_process_count": len(pids)}


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    expected_contract = contract_document(source_pin, protocol_pin)
    require(digest(canonical(expected_contract))
            == checked_sha256(contract_pin, "V13 canonical contract"),
            "reject a substituted canonical source-only contract")
    accepted: list[str] = []
    rejected: list[str] = []
    plan = synthetic_plan()

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except GateError:
            rejected.append(name)
            return
        raise GateError("accepted a hostile synthetic control: " + name)

    with SourceOnlyWall() as wall:
        witness = validate_synthetic_plan(plan)
        accepted.append("complete-corrected-owned-two-phase-synthetic-plan")
        require(witness == {"phase_count": 2,
                           "source_owner_count_per_phase": 9,
                           "unique_source_inode_count": 18,
                           "native_roles_per_phase": 2,
                           "unique_process_count": 28},
                "close the complete independent synthetic build denominator")
        accepted.append("exact-nine-owners-and-twenty-eight-processes")

        def mutated(name: str, change: Any) -> None:
            def operation() -> None:
                candidate = copy.deepcopy(plan)
                change(candidate)
                validate_synthetic_plan(candidate)
            reject(name, operation)

        for key, bad in (
            ("family", "zig"), ("root_prefix", "rebar-phase2-native-build-v13-rust-"),
            ("history_owner_count", HISTORICAL_V34_EVIDENCE_OWNERS),
            ("history_reference_count", HISTORICAL_V34_HISTORY_REFERENCES),
            ("actual_zig_v3_receipt_sha256", "0" * 64),
            ("actual_zig_v3_archive_sha256", "0" * 64),
            ("actual_zig_v3_semantic_mismatch_count",
             HISTORICAL_V33_ZIG_MISMATCHES),
            ("actual_zig_v3_verified_passing_case_count",
             HISTORICAL_V33_ZIG_VERIFIED_PASSES),
            ("actual_zig_v3_candidate_worker_count", SUITE_COUNT - 1),
            ("supplementary_reference_receipt_sha256", "0" * 64),
            ("supplementary_reference_archive_sha256", "0" * 64),
            ("supplementary_reference_status", "NOT RUN"),
            ("supplementary_reference_case_count", SUPPLEMENT_CASE_COUNT - 1),
            ("supplementary_reference_process_count",
             SUPPLEMENT_REFERENCE_PROCESS_COUNT - 1),
            ("supplementary_candidate_status", "PASS"),
            ("bridge_derived_sha256", "0" * 64),
            ("public_derived_sha256", HISTORICAL_PUBLIC_DERIVED_SHA256),
            ("cargo_external_dependency_count", 1), ("network_requests", 1),
            ("native_libraries_loaded", 1), ("candidate_processes_started", 1),
            ("hidden_cases_read", 1), ("clock_samples", 1),
            ("holdout", "OPENED"), ("candidate_qualified", True),
            ("winner_selected", True),
        ):
            mutated("reject-" + key,
                    lambda candidate, k=key, value=bad:
                    candidate.__setitem__(k, value))
        for phase_index in range(2):
            mutated("reject-phase-name-" + str(phase_index),
                    lambda candidate, i=phase_index:
                    candidate["phases"][i].__setitem__("name", "reference-c"))
            mutated("reject-phase-mode-" + str(phase_index),
                    lambda candidate, i=phase_index:
                    candidate["phases"][i].__setitem__("directory_mode", 0o755))
            for owner in RUST_OWNERS:
                for field, bad in (("sha256", "0" * 64),
                                   ("bytes", 0), ("mode", 0o644),
                                   ("nlink", 2)):
                    mutated("reject-source-" + str(phase_index) + "-"
                            + owner.path + "-" + field,
                            lambda candidate, i=phase_index, path=owner.path,
                            k=field, value=bad:
                            candidate["phases"][i]["fresh_source_owners"]
                            [path].__setitem__(k, value))
            for role in ("engine", "bridge"):
                mutated("reject-native-" + str(phase_index) + "-" + role,
                        lambda candidate, i=phase_index, r=role:
                        candidate["phases"][i]["native_outputs"]
                        [r].__setitem__("sha256", "0" * 64))
        mutated("reject-reused-phase-source-inode",
                lambda candidate: candidate["phases"][1]
                ["fresh_source_owners"][RUST_OWNERS[0].path].__setitem__(
                    "inode", candidate["phases"][0]
                    ["fresh_source_owners"][RUST_OWNERS[0].path]["inode"]))
        mutated("reject-reused-phase-directory-inode",
                lambda candidate: candidate["phases"][1].__setitem__(
                    "directory_inode", candidate["phases"][0]
                    ["directory_inode"]))
        for index in range(2 * len(PROCESS_NAMES)):
            mutated("reject-process-order-" + str(index),
                    lambda candidate, i=index:
                    candidate["processes"][i].__setitem__("name", "borrowed"))
            mutated("reject-process-status-" + str(index),
                    lambda candidate, i=index:
                    candidate["processes"][i].__setitem__("exit_status", 1))
        mutated("reject-reused-process-id",
                lambda candidate: candidate["processes"][1].__setitem__(
                    "pid", candidate["processes"][0]["pid"]))
        effect_probes = (
            ("filesystem", lambda: os.stat(str(ROOT))),
            ("write", lambda: os.mkdir("v13-forbidden")),
            ("process", lambda: subprocess.run(["false"])),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("native", lambda: ctypes.CDLL("v13-forbidden.so")),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden")),
        )
        for kind, action in effect_probes:
            previous = wall.blocked[kind]
            reject("physically-block-" + kind, action)
            require(wall.blocked[kind] == previous + 1,
                    "prove that each real forbidden source effect was blocked")
        require(len(rejected) >= 150
                and all(count > 0 for count in wall.blocked.values()),
                "exercise every hostile owner and physical source-only boundary")
        blocked = dict(wall.blocked)
    return {"schema": SCHEMA + "-source-only-self-test", "version": VERSION,
            "status": "PASS", "source_sha256": source_pin,
            "protocol_sha256": protocol_pin, "contract_sha256": contract_pin,
            "mode": "PHYSICALLY STERILE SYNTHETIC SOURCE ONLY",
            "accepted_control_count": len(accepted),
            "rejected_hostile_control_count": len(rejected),
            "blocked_effects_by_kind": blocked,
            "synthetic_independent_phase_count": witness["phase_count"],
            "synthetic_source_owner_count_per_phase":
                witness["source_owner_count_per_phase"],
            "synthetic_unique_source_inode_count":
                witness["unique_source_inode_count"],
            "synthetic_unique_process_count": witness["unique_process_count"],
            "historical_v33_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
            "historical_v33_reference_count": CURRENT_HISTORY_REFERENCES,
            "historical_v34_evidence_owner_count":
                HISTORICAL_V34_EVIDENCE_OWNERS,
            "historical_v34_reference_count":
                HISTORICAL_V34_HISTORY_REFERENCES,
            "historical_v34_supplementary_signature_reference_status":
                "NOT RUN",
            "repository_evidence_owner_lower_bound": ACTUAL_EVIDENCE_OWNERS,
            "authenticated_reference_lower_bound": ACTUAL_HISTORY_REFERENCES,
            "later_append_only_evidence_allowed": True,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVERS,
            "actual_rust_semantic_mismatch_count": 1036,
            "actual_rust_verified_passing_case_count": 8965,
            "historical_v33_zig_semantic_mismatch_count":
                HISTORICAL_V33_ZIG_MISMATCHES,
            "historical_v33_zig_verified_passing_case_count":
                HISTORICAL_V33_ZIG_VERIFIED_PASSES,
            "last_tested_zig_semantic_mismatch_count":
                ACTUAL_ZIG_V3_MISMATCHES,
            "last_tested_zig_verified_passing_case_count":
                ACTUAL_ZIG_V3_VERIFIED_PASSES,
            "actual_zig_v3_semantic_mismatch_count":
                ACTUAL_ZIG_V3_MISMATCHES,
            "actual_zig_v3_verified_passing_case_count":
                ACTUAL_ZIG_V3_VERIFIED_PASSES,
            "actual_zig_v3_candidate_worker_count": SUITE_COUNT,
            "actual_zig_v3_infrastructure_failure_count": 0,
            "actual_zig_v12_matching": "FAIL",
            "actual_first_failure_case": ACTUAL_FIRST_MISMATCH,
            "actual_first_failure_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
            "preserved_standalone_flag_vector_count": 5128,
            "supplementary_signature_case_count": SUPPLEMENT_CASE_COUNT,
            "supplementary_signature_reference_status": "PASS",
            "supplementary_signature_reference_cases_executed":
                SUPPLEMENT_CASE_COUNT,
            "supplementary_signature_reference_process_count":
                SUPPLEMENT_REFERENCE_PROCESS_COUNT,
            "supplementary_signature_reference_failure_count": 0,
            "supplementary_signature_candidate_status": "NOT RUN",
            "supplementary_signature_candidate_cases_executed": 0,
            "supplementary_signature_cases_included_in_original_denominator":
                False,
            "supplementary_signature_reference_receipt_sha256":
                SUPPLEMENT_REFERENCE_RECEIPT.sha256,
            "maximum_complete_uncompressed_build_report_bytes": MAX_REPORT_BYTES,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "corrected_public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "historical_public_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "filesystem_reads": 0, "filesystem_writes": 0,
            "archive_decompressions": 0, **boundary()}


def load_frozen_module(name: str, owner: Owner,
                       raw: bytes) -> types.ModuleType:
    require(type(name) is str and name.startswith("_rebar_v13_frozen_")
            and name not in sys.modules and type(raw) is bytes
            and len(raw) == owner.size and digest(raw) == owner.sha256,
            "load only an exact privately named independently frozen source")
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / owner.path)
    module.__package__ = ""
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    require(not any(item == "candidates" or item.startswith("candidates.")
                    for item in sys.modules),
            "never load a candidate while inspecting first-party build tools")
    return module


def validate_previous_receipt(receipt: dict[str, Any],
                              archive_owner: dict[str, Any]) -> None:
    require(receipt.get("schema")
            == "rebar-phase2-owned-rust-flag-source-build-v12-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == "phase2-v12-rust-flag-original-p0"
            and receipt.get("source_sha256") == PREVIOUS_BUILD_V12[0].sha256
            and receipt.get("protocol_sha256") == PREVIOUS_BUILD_V12[1].sha256
            and receipt.get("contract_sha256") == PREVIOUS_BUILD_V12[2].sha256
            and receipt.get("archive_relative") == PREVIOUS_BUILD_ARCHIVE.path
            and receipt.get("archive_sha256") == PREVIOUS_BUILD_ARCHIVE.sha256
            and receipt.get("archive_bytes") == PREVIOUS_BUILD_ARCHIVE.size
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("bridge_derived_sha256") == BRIDGE_DERIVED_SHA256
            and receipt.get("public_derived_sha256")
            == HISTORICAL_PUBLIC_DERIVED_SHA256
            and receipt.get("bridge_overlay_apply_count") == 2
            and receipt.get("corrected_public_overlay_apply_count") == 2
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("winner_selected") is False,
            "preserve the actually completed 28-process Rust V12 build")
    publication, directory = (receipt.get("archive_publication"),
                              receipt.get("archive_directory_fsync"))
    require(type(publication) is dict and type(directory) is dict
            and publication.get("path") == str(ROOT / PREVIOUS_BUILD_ARCHIVE.path)
            and publication.get("sha256") == PREVIOUS_BUILD_ARCHIVE.sha256
            and publication.get("bytes") == PREVIOUS_BUILD_ARCHIVE.size
            and publication.get("device") == archive_owner["device"]
            and publication.get("inode") == archive_owner["inode"]
            and publication.get("exclusive_creation") is True
            and publication.get("file_fsync_completed") is True
            and publication.get("same_inode_readback_verified") is True
            and directory.get("completed") is True,
            "bind previous Rust V12 archive to its exact durable inode")


def validate_current_summary(summary: dict[str, Any]) -> None:
    require(summary.get("schema") == "rebar-candidate-current-overview-v33-summary"
            and summary.get("status") == "PASS"
            and summary.get("full_case_denominator") == CASE_COUNT
            and summary.get("suite_count") == SUITE_COUNT
            and summary.get("private_waiver_count") == PRIVATE_WAIVERS
            and summary.get("repository_evidence_owner_count")
            == CURRENT_EVIDENCE_OWNERS
            and summary.get("authenticated_digest_addressed_history_paths")
            == CURRENT_HISTORY_REFERENCES
            and summary.get("qualified_candidate_count") == 0
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
            and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count")
            == HISTORICAL_V33_ZIG_MISMATCHES
            and summary.get("zig_original_campaign_verified_passing_case_count")
            == HISTORICAL_V33_ZIG_VERIFIED_PASSES
            and summary.get("additional_signature_frozen_case_count") == 50
            and summary.get("additional_signature_reference_status") == "NOT RUN"
            and summary.get("additional_signature_reference_cases_executed") == 0
            and summary.get("final_comparison_planned_case_count") == 4194304
            and summary.get("final_comparison_cases_generated") is False
            and summary.get("final_holdout_opened") is False
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("confidence_intervals") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED"
            and summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False,
            "authenticate immutable V33 as history, never as latest evidence")


def validate_current_inputs(inputs: dict[str, Any]) -> None:
    require(inputs.get("schema") == "rebar-candidate-current-overview-v33-inputs"
            and inputs.get("version") == 33
            and inputs.get("repository_evidence_owner_count")
            == CURRENT_EVIDENCE_OWNERS
            and inputs.get("all_digest_addressed_history_path_count")
            == CURRENT_HISTORY_REFERENCES
            and inputs.get("full_case_denominator") == CASE_COUNT
            and inputs.get("suite_count") == SUITE_COUNT
            and inputs.get("private_waiver_count") == PRIVATE_WAIVERS
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("actual_rust_semantic_mismatch_count") == 1036
            and inputs.get("actual_rust_verified_passing_case_count") == 8965
            and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
            and inputs.get("actual_zig_semantic_mismatch_count")
            == HISTORICAL_V33_ZIG_MISMATCHES
            and inputs.get("additional_signature_frozen_case_count") == 50
            and inputs.get("additional_signature_reference_status") == "NOT RUN"
            and inputs.get("additional_signature_reference_cases_executed") == 0
            and inputs.get("final_holdout_opened") is False
            and inputs.get("winner_selected") is False,
            "preserve V33 inputs while permitting later append-only evidence")


def validate_historical_v34_summary(summary: dict[str, Any]) -> None:
    require(summary.get("schema")
            == "rebar-candidate-current-overview-v34-summary"
            and summary.get("version") == 34
            and summary.get("status") == "PASS"
            and summary.get("full_case_denominator") == CASE_COUNT
            and summary.get("suite_count") == SUITE_COUNT
            and summary.get("private_waiver_count") == PRIVATE_WAIVERS
            and summary.get("repository_evidence_owner_count")
            == HISTORICAL_V34_EVIDENCE_OWNERS
            and summary.get("authenticated_digest_addressed_history_paths")
            == HISTORICAL_V34_HISTORY_REFERENCES
            and summary.get("qualified_candidate_count") == 0
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_semantic_mismatch_count")
            == 1036
            and summary.get("rust_original_campaign_verified_passing_case_count")
            == 8965
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count")
            == 1230
            and summary.get("c_original_campaign_verified_passing_case_count")
            == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count")
            == ACTUAL_ZIG_V3_MISMATCHES
            and summary.get("zig_original_campaign_verified_passing_case_count")
            == ACTUAL_ZIG_V3_VERIFIED_PASSES
            and summary.get("zig_original_campaign_candidate_worker_count")
            == SUITE_COUNT
            and summary.get("zig_original_campaign_infrastructure_failure_count")
            == 0
            and summary.get("additional_signature_frozen_case_count")
            == SUPPLEMENT_CASE_COUNT
            and summary.get("additional_signature_reference_status")
            == "NOT RUN"
            and summary.get("additional_signature_reference_cases_executed")
            == 0
            and summary.get("final_comparison_planned_case_count") == 4194304
            and summary.get("final_comparison_cases_generated") is False
            and summary.get("final_holdout_opened") is False
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("confidence_intervals") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED"
            and summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False,
            "authenticate V34 as history before the real 50-case reference")


def validate_historical_v34_inputs(inputs: dict[str, Any]) -> None:
    require(inputs.get("schema")
            == "rebar-candidate-current-overview-v34-inputs"
            and inputs.get("version") == 34
            and inputs.get("repository_evidence_owner_count")
            == HISTORICAL_V34_EVIDENCE_OWNERS
            and inputs.get("all_digest_addressed_history_path_count")
            == HISTORICAL_V34_HISTORY_REFERENCES
            and inputs.get("full_case_denominator") == CASE_COUNT
            and inputs.get("suite_count") == SUITE_COUNT
            and inputs.get("private_waiver_count") == PRIVATE_WAIVERS
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("actual_rust_semantic_mismatch_count") == 1036
            and inputs.get("actual_rust_verified_passing_case_count") == 8965
            and inputs.get("c_original_campaign_semantic_mismatch_count")
            == 1230
            and inputs.get("c_original_campaign_verified_passing_case_count")
            == 7325
            and inputs.get("actual_zig_semantic_mismatch_count")
            == HISTORICAL_V33_ZIG_MISMATCHES
            and inputs.get("historical_zig_semantic_mismatch_count")
            == HISTORICAL_V33_ZIG_MISMATCHES
            and inputs.get("historical_zig_verified_passing_case_count")
            == HISTORICAL_V33_ZIG_VERIFIED_PASSES
            and inputs.get("zig_original_campaign_status") == "FAIL"
            and inputs.get("zig_original_campaign_semantic_mismatch_count")
            == ACTUAL_ZIG_V3_MISMATCHES
            and inputs.get("zig_original_campaign_verified_passing_case_count")
            == ACTUAL_ZIG_V3_VERIFIED_PASSES
            and inputs.get("zig_original_campaign_candidate_worker_count")
            == SUITE_COUNT
            and inputs.get("zig_original_campaign_infrastructure_failure_count")
            == 0
            and inputs.get("additional_signature_frozen_case_count")
            == SUPPLEMENT_CASE_COUNT
            and inputs.get("additional_signature_reference_status")
            == "NOT RUN"
            and inputs.get("additional_signature_reference_cases_executed")
            == 0
            and inputs.get("final_holdout_opened") is False
            and inputs.get("winner_selected") is False,
            "distinguish historical V34 inputs from the later 50-case result")


def validate_actual_matching(receipt: dict[str, Any],
                             archive: dict[str, Any]) -> None:
    attached = receipt.get("archive")
    require(receipt.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("family") == FAMILY
            and receipt.get("actual_candidate_workers") == 13
            and receipt.get("completed_suite_count") == SUITE_COUNT
            and receipt.get("case_execution_denominator") == CASE_COUNT
            and receipt.get("named_private_waiver_count") == PRIVATE_WAIVERS
            and receipt.get("semantic_mismatch_count") == 1036
            and receipt.get("verified_passing_case_count") == 8965
            and receipt.get("infrastructure_failure_count") == 0
            and receipt.get("candidate_qualified") is False
            and receipt.get("corrected_public_adapter_sha256")
            == HISTORICAL_PUBLIC_DERIVED_SHA256
            and receipt.get("corrected_bridge_source_sha256") == BRIDGE_DERIVED_SHA256
            and receipt.get("all_four_original_targets_restored") is True
            and receipt.get("restoration_verified_before_publication") is True
            and type(attached) is dict
            and attached.get("sha256") == archive["sha256"]
            and attached.get("size_bytes") == archive["bytes"]
            and attached.get("device") == archive["device"]
            and attached.get("inode") == archive["inode"]
            and receipt.get("holdout") == "NOT OPENED",
            "preserve every actually recorded Rust V4 matching failure")


def validate_zig_build(receipt: dict[str, Any],
                       archive: dict[str, Any]) -> None:
    attached = receipt.get("archive")
    require(receipt.get("schema")
            == "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == "zig"
            and receipt.get("actual_evidence_owner_count_before_publication") == 153
            and receipt.get("actual_authenticated_reference_count_before_publication")
            == 158
            and receipt.get("repository_evidence_owner_count_after_publication")
            == CURRENT_EVIDENCE_OWNERS
            and receipt.get("authenticated_history_reference_count_after_publication")
            == CURRENT_HISTORY_REFERENCES
            and receipt.get("new_actual_evidence_owner_count") == 2
            and receipt.get("actual_compiler_process_count") == 26
            and receipt.get("actual_source_apply_count") == 2
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("winner_selected") is False
            and type(attached) is dict
            and attached.get("sha256") == archive["sha256"]
            and attached.get("bytes") == archive["bytes"]
            and attached.get("inode") == archive["inode"],
            "authenticate historical Zig V12 build before its V3 matching run")


def validate_actual_zig_matching(receipt: dict[str, Any],
                                archive: dict[str, Any]) -> None:
    attached = receipt.get("archive")
    require(receipt.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means")
            == "DURABLE PUBLICATION ONLY"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("family") == "zig"
            and receipt.get("actual_candidate_workers") == SUITE_COUNT
            and receipt.get("completed_suite_count") == SUITE_COUNT
            and receipt.get("suite_count") == SUITE_COUNT
            and receipt.get("case_execution_denominator") == CASE_COUNT
            and receipt.get("named_private_waiver_count") == PRIVATE_WAIVERS
            and receipt.get("semantic_mismatch_count")
            == ACTUAL_ZIG_V3_MISMATCHES
            and receipt.get("verified_passing_case_count")
            == ACTUAL_ZIG_V3_VERIFIED_PASSES
            and receipt.get("infrastructure_failure_count") == 0
            and receipt.get("candidate_qualified") is False
            and receipt.get("historical_zig_semantic_mismatch_count")
            == HISTORICAL_V33_ZIG_MISMATCHES
            and receipt.get("historical_evidence_owner_count_before_publication")
            == CURRENT_EVIDENCE_OWNERS
            and receipt.get("historical_authenticated_reference_count_before_publication")
            == CURRENT_HISTORY_REFERENCES
            and receipt.get("new_repository_evidence_owner_count") == 2
            and receipt.get("resulting_repository_evidence_owner_count")
            == HISTORICAL_V34_EVIDENCE_OWNERS
            and receipt.get("resulting_authenticated_reference_count")
            == HISTORICAL_V34_HISTORY_REFERENCES
            and receipt.get("actual_v12_build_archive_sha256")
            == ZIG_V12_ARCHIVE.sha256
            and receipt.get("actual_v12_build_receipt_sha256")
            == ZIG_V12_RECEIPT.sha256
            and receipt.get("actual_corrected_rust_semantic_mismatch_count")
            == 1036
            and receipt.get("actual_c_semantic_mismatch_count") == 1230
            and receipt.get("all_original_native_targets_restored") is True
            and receipt.get("restoration_verified_before_publication") is True
            and type(attached) is dict
            and attached.get("path") == str(ROOT / ZIG_V3_MATCH_ARCHIVE.path)
            and attached.get("relative")
            == PurePosixPath(ZIG_V3_MATCH_ARCHIVE.path).name
            and attached.get("sha256") == archive["sha256"]
            and attached.get("size_bytes") == archive["bytes"]
            and attached.get("device") == archive["device"]
            and attached.get("inode") == archive["inode"]
            and attached.get("mode") == archive["mode"] == 0o600
            and attached.get("exclusive_creation") is True
            and attached.get("file_fsync_completed") is True
            and attached.get("directory_fsync_completed") is True
            and attached.get("same_inode_readback_verified") is True
            and attached.get("streaming_readback_verified") is True
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("benchmark_files_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("undefined_behavior") == "NOT MEASURED"
            and receipt.get("winner_selected") is False,
            "authenticate the real completed Zig V3 matching campaign "
            "and its exact compressed archive without inflating it")


def validate_supplement_reference_source(contract: dict[str, Any]) -> None:
    frozen = contract.get("frozen_additional_oracle")
    original = contract.get("original_core")
    policy = contract.get("future_reference_policy")
    wall = contract.get("phase_boundary")
    runtime = contract.get("pinned_runtime")
    require(contract.get("schema")
            == "rebar-owned-callable-introspection-reference-v2-source-freeze"
            and contract.get("version") == 2
            and contract.get("status")
            == "SOURCE FREEZE ONLY; TWO REFERENCES NOT RUN"
            and contract.get("source", {}).get("path")
            == SUPPLEMENT_REFERENCE_V2[0].path
            and contract.get("source", {}).get("sha256")
            == SUPPLEMENT_REFERENCE_V2[0].sha256
            and contract.get("protocol", {}).get("path")
            == SUPPLEMENT_REFERENCE_V2[1].path
            and contract.get("protocol", {}).get("sha256")
            == SUPPLEMENT_REFERENCE_V2[1].sha256
            and type(original) is dict
            and original.get("case_execution_denominator") == CASE_COUNT
            and original.get("suite_count") == SUITE_COUNT
            and original.get("named_private_waiver_count") == PRIVATE_WAIVERS
            and original.get("denominator_modified") is False
            and original.get("inventory") == owner_document(PHASE_ONE)
            and type(frozen) is dict
            and frozen.get("separately_counted_case_count")
            == SUPPLEMENT_CASE_COUNT
            and frozen.get("included_in_original_core_denominator") is False
            and frozen.get("matrix_sha256") == SUPPLEMENT_MATRIX_SHA256
            and frozen.get("source") == owner_document(SUPPLEMENT_SOURCE)
            and frozen.get("protocol") == owner_document(SUPPLEMENT_PROTOCOL)
            and frozen.get("contract") == owner_document(SUPPLEMENT)
            and frozen.get("reference_status") == "NOT RUN"
            and frozen.get("candidate_status") == "NOT MEASURED"
            and type(policy) is dict
            and policy.get("exact_distinct_isolated_worker_process_count")
            == SUPPLEMENT_REFERENCE_PROCESS_COUNT
            and policy.get("different_actual_process_ids_required") is True
            and policy.get("candidate_execution_allowed") is False
            and policy.get("source_owned_worker")
            == owner_document(SUPPLEMENT_SOURCE)
            and type(runtime) is dict
            and runtime.get("implementation") == "CPython"
            and runtime.get("version") == "3.14.6"
            and runtime.get("executable") == PYTHON
            and runtime.get("executable_sha256") == PYTHON_SHA256
            and type(wall) is dict
            and wall.get("reference_status") == "NOT RUN"
            and wall.get("actual_reference_processes_started") == 0
            and wall.get("actual_candidate_imports") == 0
            and wall.get("actual_candidate_processes_started") == 0
            and wall.get("actual_source_build_archives_decompressed") == 0
            and wall.get("holdout") == "NOT OPENED",
            "preserve the exact independently committed V2 source freeze "
            "as history before its subsequently executed two-reference run")


def validate_actual_supplement_reference(receipt: dict[str, Any],
                                         archive: dict[str, Any]) -> None:
    attached = receipt.get("archive")
    appended = receipt.get("appended_corrected_zig_matching")
    worker_pids = receipt.get("actual_distinct_process_ids")
    require(receipt.get("schema")
            == "rebar-owned-callable-introspection-reference-v2-durable-publication-receipt"
            and receipt.get("version") == 2
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means")
            == "EVIDENCE PUBLICATION ONLY"
            and receipt.get("source_sha256")
            == SUPPLEMENT_REFERENCE_V2[0].sha256
            and receipt.get("protocol_sha256")
            == SUPPLEMENT_REFERENCE_V2[1].sha256
            and receipt.get("contract_sha256")
            == SUPPLEMENT_REFERENCE_V2[2].sha256
            and receipt.get("frozen_v1_source_sha256")
            == SUPPLEMENT_SOURCE.sha256
            and receipt.get("frozen_v1_protocol_sha256")
            == SUPPLEMENT_PROTOCOL.sha256
            and receipt.get("frozen_v1_contract_sha256") == SUPPLEMENT.sha256
            and receipt.get("matrix_sha256") == SUPPLEMENT_MATRIX_SHA256
            and receipt.get("original_case_denominator") == CASE_COUNT
            and receipt.get("original_suite_count") == SUITE_COUNT
            and receipt.get("original_private_waiver_count") == PRIVATE_WAIVERS
            and receipt.get("additional_case_count") == SUPPLEMENT_CASE_COUNT
            and receipt.get("additional_cases_included_in_original_denominator")
            is False
            and receipt.get("reference_status") == "PASS"
            and receipt.get("reference_failure_count") == 0
            and receipt.get("actual_reference_processes_started")
            == SUPPLEMENT_REFERENCE_PROCESS_COUNT
            and type(worker_pids) is list
            and worker_pids == [81, 82]
            and len(set(worker_pids)) == SUPPLEMENT_REFERENCE_PROCESS_COUNT
            and receipt.get("candidate_introspection") == "NOT MEASURED"
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("candidate_qualified") is False
            and receipt.get("authenticated_evidence_owner_lower_bound_before_publication")
            == HISTORICAL_V34_EVIDENCE_OWNERS
            and receipt.get("authenticated_history_reference_lower_bound_before_publication")
            == HISTORICAL_V34_HISTORY_REFERENCES
            and receipt.get("new_actual_evidence_owner_count") == 2
            and receipt.get("minimum_evidence_owner_count_after_publication")
            == ACTUAL_EVIDENCE_OWNERS
            and receipt.get("minimum_history_reference_count_after_publication")
            == ACTUAL_HISTORY_REFERENCES
            and type(appended) is dict
            and appended.get("candidate_status") == "FAIL"
            and appended.get("semantic_mismatch_count")
            == ACTUAL_ZIG_V3_MISMATCHES
            and appended.get("verified_passing_case_count")
            == ACTUAL_ZIG_V3_VERIFIED_PASSES
            and appended.get("actual_candidate_workers") == SUITE_COUNT
            and appended.get("completed_suite_count") == SUITE_COUNT
            and appended.get("infrastructure_failure_count") == 0
            and appended.get("evidence_owner_lower_bound")
            == HISTORICAL_V34_EVIDENCE_OWNERS
            and appended.get("history_reference_lower_bound")
            == HISTORICAL_V34_HISTORY_REFERENCES
            and appended.get("receipt")
            == owner_document(ZIG_V3_MATCH_RECEIPT)
            and appended.get("matching_archive_metadata_sha256")
            == ZIG_V3_MATCH_ARCHIVE.sha256
            and appended.get("matching_archive_decompressed") is False
            and appended.get("matching_archive_opened") is False
            and type(attached) is dict
            and attached.get("path") == SUPPLEMENT_REFERENCE_ARCHIVE.path
            and attached.get("sha256") == archive["sha256"]
            and attached.get("bytes") == archive["bytes"]
            and attached.get("device") == archive["device"]
            and attached.get("inode") == archive["inode"]
            and attached.get("uid") == archive["uid"]
            and attached.get("nlink") == archive["nlink"] == 1
            and attached.get("mode") == "0600"
            and archive["mode"] == 0o600
            and attached.get("exclusive_creation") is True
            and attached.get("file_fsync_completed") is True
            and attached.get("directory_fsync_completed") is True
            and attached.get("same_inode_readback_verified") is True
            and receipt.get("source_build_archives_decompressed") == 0
            and receipt.get("matching_archives_opened") == 0
            and receipt.get("final_cases_read") == 0
            and receipt.get("holdout_cases_read") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("undefined_behavior") == "NOT MEASURED"
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("winner_selected") is False,
            "authenticate exactly two actual successful 50-case CPython "
            "reference workers and the compressed-only durable evidence")


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    source_pin = checked_sha256(source_pin, "V13 source")
    protocol_pin = checked_sha256(protocol_pin, "V13 protocol")
    contract_pin = checked_sha256(contract_pin, "V13 contract")
    source_size = os.stat(ROOT / SOURCE_PATH, follow_symlinks=False).st_size
    protocol_size = os.stat(ROOT / PROTOCOL_PATH,
                            follow_symlinks=False).st_size
    require(0 < source_size <= MAX_SOURCE_BYTES
            and 0 < protocol_size <= MAX_SOURCE_BYTES,
            "bound independently pinned V13 source and protocol")
    frozen_source = Owner(SOURCE_PATH, source_pin, source_size)
    frozen_protocol = Owner(PROTOCOL_PATH, protocol_pin, protocol_size)
    expected = canonical(contract_document(source_pin, protocol_pin))
    frozen_contract = Owner(CONTRACT_PATH, contract_pin, len(expected))
    raw: dict[str, bytes] = {}
    actual: dict[str, dict[str, Any]] = {}
    groups = (
        (frozen_source, frozen_protocol, frozen_contract, GOAL, PHASE_ONE,
         SUPPLEMENT, SUPPLEMENT_SOURCE, SUPPLEMENT_PROTOCOL),
        SUPPLEMENT_REFERENCE_V2,
        (SUPPLEMENT_REFERENCE_ARCHIVE, SUPPLEMENT_REFERENCE_RECEIPT),
        RUST_OWNERS, BRIDGE_REPAIR, PUBLIC_REPAIR_V3, PREVIOUS_BUILD_V12,
        (PREVIOUS_BUILD_ARCHIVE, PREVIOUS_BUILD_RECEIPT),
        (RUST_MATCH_ARCHIVE, RUST_MATCH_RECEIPT),
        (ZIG_V12_ARCHIVE, ZIG_V12_RECEIPT),
        (ZIG_V3_MATCH_ARCHIVE, ZIG_V3_MATCH_RECEIPT),
        V9_KERNEL, V7_KERNEL, V33, V34,
    )
    for group in groups:
        for owner in group:
            payload, observed = read_owner(owner)
            raw[owner.path] = payload
            actual[owner.path] = observed
    require(raw[CONTRACT_PATH] == expected and digest(expected) == contract_pin
            and strict_json(raw[CONTRACT_PATH], "canonical V13 contract")
            == contract_document(source_pin, protocol_pin),
            "authenticate only exact independent V13 source-freeze pins")
    validate_current_summary(strict_json(raw[V33[2].path],
                                         "historical V33 summary"))
    validate_current_inputs(strict_json(raw[V33[1].path],
                                        "historical V33 inputs"))
    validate_historical_v34_summary(strict_json(raw[V34[2].path],
                                                "historical V34 summary"))
    validate_historical_v34_inputs(strict_json(raw[V34[1].path],
                                               "historical V34 inputs"))
    matrix = strict_json(raw[PHASE_ONE.path], "complete P0 matrix")
    count = matrix.get("denominator")
    require(matrix.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and type(count) is dict
            and count.get("final_required_case_execution_denominator")
            == CASE_COUNT
            and count.get("frozen_planned_case_execution_denominator")
            == CASE_COUNT
            and count.get("private_upstream_methods_outside_public_denominator")
            == PRIVATE_WAIVERS
            and type(count.get("counted_suite_ids")) is list
            and len(count["counted_suite_ids"]) == SUITE_COUNT,
            "preserve exact original 31,237-case gate")
    supplement = strict_json(raw[SUPPLEMENT.path],
                             "historical V1 signature source freeze")
    added = supplement.get("additional_obligation")
    wall = supplement.get("phase_boundary")
    require(supplement.get("schema")
            == "rebar-python-re-callable-introspection-v1-source-freeze"
            and type(added) is dict and added.get("case_count") == 50
            and type(added.get("case_matrix")) is list
            and len(added["case_matrix"]) == 50
            and type(wall) is dict
            and wall.get("introspection_reference") == "NOT RUN"
            and wall.get("actual_reference_roles_started") == 0
            and wall.get("actual_candidate_imports") == 0
            and wall.get("holdout") == "NOT OPENED",
            "preserve the historical V1 source freeze and separate 50 cases")
    validate_supplement_reference_source(
        strict_json(raw[SUPPLEMENT_REFERENCE_V2[2].path],
                    "historical V2 two-reference source freeze"))
    validate_actual_supplement_reference(
        strict_json(raw[SUPPLEMENT_REFERENCE_RECEIPT.path],
                    "real successful two-worker 50-case CPython reference"),
        actual[SUPPLEMENT_REFERENCE_ARCHIVE.path])
    old = strict_json(raw[PREVIOUS_BUILD_V12[2].path],
                      "actual previous V12 source contract")
    require(old.get("schema")
            == "rebar-phase2-owned-rust-flag-source-build-v12-source-freeze"
            and old.get("version") == 12
            and old.get("source", {}).get("sha256")
            == PREVIOUS_BUILD_V12[0].sha256
            and old.get("protocol", {}).get("sha256")
            == PREVIOUS_BUILD_V12[1].sha256
            and old.get("corrected_first_party_public_overlay", {})
            .get("derived", {}).get("sha256")
            == HISTORICAL_PUBLIC_DERIVED_SHA256,
            "preserve actual pinned V12 high-level source without invoking it")
    validate_previous_receipt(
        strict_json(raw[PREVIOUS_BUILD_RECEIPT.path], "real V12 build receipt"),
        actual[PREVIOUS_BUILD_ARCHIVE.path])
    validate_actual_matching(
        strict_json(raw[RUST_MATCH_RECEIPT.path], "real Rust V4 failure"),
        actual[RUST_MATCH_ARCHIVE.path])
    validate_zig_build(
        strict_json(raw[ZIG_V12_RECEIPT.path], "real Zig V12 source build"),
        actual[ZIG_V12_ARCHIVE.path])
    validate_actual_zig_matching(
        strict_json(raw[ZIG_V3_MATCH_RECEIPT.path],
                    "real corrected Zig V3 original P0 matching"),
        actual[ZIG_V3_MATCH_ARCHIVE.path])
    toolchain = [read_toolchain(item) for item in TOOLCHAIN]
    bridge = load_frozen_module("_rebar_v13_frozen_bridge_v1",
                                BRIDGE_REPAIR[0], raw[BRIDGE_REPAIR[0].path])
    bridge_contract = strict_json(raw[BRIDGE_REPAIR[2].path],
                                  "first-party bridge source contract")
    require(bridge.SCHEMA == "rebar-phase2-owned-rust-source-repair-v1"
            and bridge.ORIGINAL_PATH == BRIDGE_PATH
            and bridge.ORIGINAL_SHA256 == RUST_OWNERS[2].sha256
            and bridge.ORIGINAL_BYTES == RUST_OWNERS[2].size
            and bridge.DERIVED_SHA256 == BRIDGE_DERIVED_SHA256
            and bridge.DERIVED_BYTES == BRIDGE_DERIVED_BYTES
            and bridge_contract == bridge.contract_document(
                BRIDGE_REPAIR[0].sha256, BRIDGE_REPAIR[1].sha256),
            "authenticate only first-party Rust bridge source")
    bridge_bytes = bridge.repaired_source(
        raw[BRIDGE_PATH], RUST_OWNERS[2].sha256, RUST_OWNERS[2].size)
    require(type(bridge_bytes) is bytes
            and len(bridge_bytes) == BRIDGE_DERIVED_BYTES
            and digest(bridge_bytes) == BRIDGE_DERIVED_SHA256,
            "derive the owned Rust bridge in memory only")
    public = load_frozen_module("_rebar_v13_frozen_public_v3",
                                PUBLIC_REPAIR_V3[0],
                                raw[PUBLIC_REPAIR_V3[0].path])
    repair = strict_json(raw[PUBLIC_REPAIR_V3[2].path],
                         "evidence-backed V3 pattern repair")
    require(public.SCHEMA
            == "rebar-phase2-owned-rust-public-contract-source-repair-v3"
            and public.ORIGINAL_SHA256 == RUST_OWNERS[-1].sha256
            and public.ORIGINAL_BYTES == RUST_OWNERS[-1].size
            and public.V2_DERIVED_SHA256 == HISTORICAL_PUBLIC_DERIVED_SHA256
            and public.DERIVED_SHA256 == PUBLIC_DERIVED_SHA256
            and public.DERIVED_BYTES == PUBLIC_DERIVED_BYTES
            and public.ACTUAL_CASE == ACTUAL_FIRST_MISMATCH
            and public.CASE_RECORD_SHA256 == ACTUAL_FIRST_MISMATCH_SHA256
            and repair == public.contract_document(
                PUBLIC_REPAIR_V3[0].sha256, PUBLIC_REPAIR_V3[1].sha256),
            "bind only the actual first-mismatch corrected V3 source")
    witness, public_bytes = public.verify_context(
        PUBLIC_REPAIR_V3[0].sha256, PUBLIC_REPAIR_V3[1].sha256,
        PUBLIC_REPAIR_V3[2].sha256)
    require(type(witness) is dict
            and witness.get("schema")
            == "rebar-phase2-owned-rust-public-contract-source-repair-v3-read-only-frozen-context"
            and witness.get("status") == "PASS"
            and witness.get("derived_source_sha256") == PUBLIC_DERIVED_SHA256
            and witness.get("derived_source_bytes") == PUBLIC_DERIVED_BYTES
            and witness.get("actual_first_failure_case") == ACTUAL_FIRST_MISMATCH
            and witness.get("actual_first_failure_record_sha256")
            == ACTUAL_FIRST_MISMATCH_SHA256
            and witness.get("actual_failure_corrected_in_synthetic_source") is True
            and witness.get("actual_stdlib_standalone_flag_vector_count") == 5128
            and witness.get("authenticated_repository_evidence_owner_lower_bound")
            == CURRENT_EVIDENCE_OWNERS
            and witness.get("authenticated_reference_lower_bound")
            == CURRENT_HISTORY_REFERENCES
            and witness.get("candidate_workers_started") == 0
            and witness.get("compiler_processes_started") == 0
            and witness.get("native_libraries_loaded") == 0
            and witness.get("rust_matching_archive_uncompressed_bytes_read") == 0
            and witness.get("clock_samples") == 0
            and witness.get("final_holdout_opened") is False
            and witness.get("winner_selected") is False
            and type(public_bytes) is bytes
            and len(public_bytes) == PUBLIC_DERIVED_BYTES
            and digest(public_bytes) == PUBLIC_DERIVED_SHA256,
            "prove all 5,128 flags and exact real V3 source without building")
    v9 = load_frozen_module("_rebar_v13_frozen_low_level_v9",
                            V9_KERNEL[0], raw[V9_KERNEL[0].path])
    original = {item.path: (item.sha256, item.size) for item in RUST_OWNERS}
    require(v9.SCHEMA == "rebar-phase2-owned-native-source-build-v9"
            and v9.FAMILY == FAMILY and tuple(v9.PHASES) == PHASES
            and tuple(v9.PROCESS_NAMES) == PROCESS_NAMES
            and v9.WORK_PREFIX + FAMILY + "-" == ROOT_PREFIX
            and v9.RUST_OWNERS == original
            and tuple(v9.V7_OWNERS["source"])
            == (V7_KERNEL[0].path, V7_KERNEL[0].sha256, V7_KERNEL[0].size)
            and v9.PINNED_RUSTC == TOOLCHAIN[0].path
            and v9.PINNED_CARGO == TOOLCHAIN[1].path
            and v9.PINNED_GCC == TOOLCHAIN[2].path
            and v9.PINNED_READELF == TOOLCHAIN[3].path
            and v9.ENGINE_NAME == ENGINE_NAME
            and v9.BRIDGE_NAME == BRIDGE_NAME,
            "use only exact owned V9/V7 offline native-build primitives")
    cargo = raw[RUST_OWNERS[1].path].decode("utf-8", "strict")
    lock = raw[RUST_OWNERS[0].path].decode("utf-8", "strict")
    require("[dependencies" not in cargo and "[dev-dependencies" not in cargo
            and "[build-dependencies" not in cargo
            and lock.count("[[package]]") == 1
            and 'name = "rebar-rust-continuation"' in lock,
            "reject every external or delegated regular-expression package")
    for owner in RUST_OWNERS:
        _, unchanged = read_owner(owner)
        require(unchanged == actual[owner.path],
                "preserve every canonical first-party source owner")
    verify_runtime()
    outcome = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "version": VERSION, "status": "PASS", "read_only": True,
        "family": FAMILY, "source_sha256": source_pin,
        "protocol_sha256": protocol_pin, "contract_sha256": contract_pin,
        "authenticated_source_owner_count": len(actual),
        "authenticated_toolchain_owner_count": len(toolchain),
        "streamed_toolchain_bytes": sum(item.size for item in TOOLCHAIN),
        "toolchain": toolchain,
        "historical_v33_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "historical_v33_reference_count": CURRENT_HISTORY_REFERENCES,
        "historical_v34_evidence_owner_count":
            HISTORICAL_V34_EVIDENCE_OWNERS,
        "historical_v34_reference_count":
            HISTORICAL_V34_HISTORY_REFERENCES,
        "historical_v34_supplementary_signature_reference_status":
            "NOT RUN",
        "historical_v34_supplementary_signature_reference_cases_executed":
            0,
        "repository_evidence_owner_lower_bound": ACTUAL_EVIDENCE_OWNERS,
        "authenticated_reference_lower_bound": ACTUAL_HISTORY_REFERENCES,
        "later_append_only_evidence_allowed": True,
        "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVERS,
        "actual_rust_semantic_mismatch_count": 1036,
        "actual_rust_verified_passing_case_count": 8965,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "historical_v33_zig_semantic_mismatch_count":
            HISTORICAL_V33_ZIG_MISMATCHES,
        "historical_v33_zig_verified_passing_case_count":
            HISTORICAL_V33_ZIG_VERIFIED_PASSES,
        "last_tested_zig_semantic_mismatch_count": ACTUAL_ZIG_V3_MISMATCHES,
        "last_tested_zig_verified_passing_case_count":
            ACTUAL_ZIG_V3_VERIFIED_PASSES,
        "actual_zig_v3_matching_status": "FAIL",
        "actual_zig_v3_semantic_mismatch_count": ACTUAL_ZIG_V3_MISMATCHES,
        "actual_zig_v3_verified_passing_case_count":
            ACTUAL_ZIG_V3_VERIFIED_PASSES,
        "actual_zig_v3_candidate_worker_count": SUITE_COUNT,
        "actual_zig_v3_completed_suite_count": SUITE_COUNT,
        "actual_zig_v3_infrastructure_failure_count": 0,
        "actual_zig_v12_build_process_count": 26,
        "actual_zig_v12_source_apply_count": 2,
        "actual_zig_v12_matching": "FAIL",
        "actual_zig_v12_matching_campaign_version": 3,
        "supplementary_signature_case_count": SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_status": "PASS",
        "supplementary_signature_reference_cases_executed":
            SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_process_count":
            SUPPLEMENT_REFERENCE_PROCESS_COUNT,
        "supplementary_signature_reference_process_ids": [81, 82],
        "supplementary_signature_reference_failure_count": 0,
        "supplementary_signature_candidate_status": "NOT RUN",
        "supplementary_signature_candidate_cases_executed": 0,
        "supplementary_signature_cases_included_in_original_denominator":
            False,
        "supplementary_signature_reference_receipt_sha256":
            SUPPLEMENT_REFERENCE_RECEIPT.sha256,
        "supplementary_signature_reference_receipt_bytes_read":
            SUPPLEMENT_REFERENCE_RECEIPT.size,
        "supplementary_signature_reference_archive_sha256":
            SUPPLEMENT_REFERENCE_ARCHIVE.sha256,
        "supplementary_signature_reference_archive_compressed_bytes_read":
            SUPPLEMENT_REFERENCE_ARCHIVE.size,
        "supplementary_signature_reference_archive_decompressed": False,
        "actual_previous_v12_process_count": 28,
        "actual_previous_v12_archive_compressed_bytes_read":
            PREVIOUS_BUILD_ARCHIVE.size,
        "actual_previous_v12_archive_decompressed": False,
        "actual_v4_rust_matching_archive_compressed_bytes_read":
            RUST_MATCH_ARCHIVE.size,
        "actual_v4_rust_matching_archive_decompressed": False,
        "actual_zig_v12_archive_compressed_bytes_read": ZIG_V12_ARCHIVE.size,
        "actual_zig_v12_archive_decompressed": False,
        "actual_zig_v3_matching_archive_sha256": ZIG_V3_MATCH_ARCHIVE.sha256,
        "actual_zig_v3_matching_archive_compressed_bytes_read":
            ZIG_V3_MATCH_ARCHIVE.size,
        "actual_zig_v3_matching_archive_decompressed": False,
        "actual_zig_v3_matching_receipt_sha256": ZIG_V3_MATCH_RECEIPT.sha256,
        "actual_zig_v3_matching_receipt_bytes_read":
            ZIG_V3_MATCH_RECEIPT.size,
        "actual_first_failure_case": ACTUAL_FIRST_MISMATCH,
        "actual_first_failure_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
        "historical_public_derived_sha256": HISTORICAL_PUBLIC_DERIVED_SHA256,
        "bridge_derived_source_sha256": BRIDGE_DERIVED_SHA256,
        "bridge_derived_source_bytes": BRIDGE_DERIVED_BYTES,
        "corrected_public_derived_source_sha256": PUBLIC_DERIVED_SHA256,
        "corrected_public_derived_source_bytes": PUBLIC_DERIVED_BYTES,
        "preserved_standalone_flag_vector_count": 5128,
        "derived_sources_materialized": False,
        "cargo_package_count": 1, "external_dependency_count": 0,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "future_phase_count": 2, "future_complete_sources_per_phase": 9,
        "future_unchanged_sources_per_phase": 7,
        "future_bridge_overlays_per_phase": 1,
        "future_corrected_public_overlays_per_phase": 1,
        "future_compiler_process_count": 2 * len(PROCESS_NAMES),
        "maximum_complete_uncompressed_build_report_bytes": MAX_REPORT_BYTES,
        "v9_high_level_context_called": False,
        "v10_high_level_context_called": False,
        "v11_build_called": False,
        "v12_high_level_build_called": False,
        **boundary(),
    }
    return outcome, {"v9": v9, "bridge": bridge, "public": public,
                     "bridge_bytes": bridge_bytes, "public_bytes": public_bytes,
                     "originals": {item.path: raw[item.path]
                                   for item in RUST_OWNERS}}


_ACTIVE: dict[str, Any] | None = None
_APPLIED: set[tuple[str, str]] = set()


def checked_workdir(value: str) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require an explicitly owned private Rust root")
    path = PurePosixPath(value)
    require(path.is_absolute() and str(path) == value
            and len(path.parts) == 3 and path.parts[1] == "tmp"
            and path.parts[2].startswith(ROOT_PREFIX)
            and len(path.parts[2]) > len(ROOT_PREFIX)
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in path.parts[2]),
            "reject an escaped or bridge-incompatible V9 private Rust root")
    return value


def copy_dual_snapshot(workdir: str, family: str, phase: str,
                       sources: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    require(_ACTIVE is not None, "require an explicitly pinned V13 actual build")
    state = _ACTIVE
    v9 = state["v9"]
    kernel = state["kernel"]
    checked_workdir(workdir)
    expected = {item.path for item in RUST_OWNERS}
    require(family == FAMILY and phase in PHASES and type(sources) is dict
            and set(sources) == expected and (workdir, phase) not in _APPLIED,
            "require a fresh V13 phase with exactly nine original source owners")
    paths = v9.phase_paths(workdir, family, phase)
    for peer in PHASES:
        peer_paths = v9.phase_paths(workdir, family, peer)
        for directory in (peer_paths["base"], peer_paths["source"],
                          peer_paths["source"] / "candidates",
                          peer_paths["source"] / "candidates/rust"):
            observed = os.lstat(directory)
            require(stat.S_ISDIR(observed.st_mode)
                    and stat.S_IMODE(observed.st_mode) == 0o700
                    and observed.st_uid == os.geteuid(),
                    "precreate both owner-only independent Rust phase trees")
    for item in RUST_OWNERS:
        require(type(sources[item.path]) is bytes
                and len(sources[item.path]) == item.size
                and digest(sources[item.path]) == item.sha256,
                "reject substituted canonical first-party Rust source")
    copies: dict[str, dict[str, Any]] = {}
    for item in sorted(RUST_OWNERS, key=lambda entry: entry.path):
        if item.path in (BRIDGE_PATH, PUBLIC_PATH):
            continue
        target = paths["source"] / item.path
        kernel.mkdir_private(target.parent)
        observed = kernel.write_fresh(target, sources[item.path],
                                      synchronize=False)
        observed["path"] = v9.sanitized(observed["path"], workdir, family)
        copies[item.path] = observed
    require(len(copies) == 7, "leave exactly both overlay destinations absent")
    bridge_result = state["bridge"].apply_private(
        str(paths["source"]), state["bridge_bytes"])
    public_result = state["public"].apply_private(
        str(paths["source"]), state["public_bytes"],
        PUBLIC_REPAIR_V3[0].sha256, PUBLIC_REPAIR_V3[1].sha256,
        PUBLIC_REPAIR_V3[2].sha256)
    require(type(bridge_result) is dict
            and bridge_result.get("status") == "PASS"
            and bridge_result.get("phase") == phase
            and bridge_result.get("source_apply_count") == 1
            and bridge_result.get("derived_sha256") == BRIDGE_DERIVED_SHA256
            and bridge_result.get("derived_bytes") == BRIDGE_DERIVED_BYTES
            and bridge_result.get("candidate_original_modified") is False,
            "apply the exact first-party bridge once to this private phase")
    require(type(public_result) is dict
            and public_result.get("status") == "PASS"
            and public_result.get("phase") == phase
            and public_result.get("source_apply_count") == 1
            and public_result.get("derived_source_sha256")
            == PUBLIC_DERIVED_SHA256
            and public_result.get("derived_source_bytes")
            == PUBLIC_DERIVED_BYTES
            and public_result.get("canonical_candidate_modified") is False,
            "apply the corrected V2 public adapter exactly once to this phase")
    for path, expected_sha, expected_size, expected_raw, overlay in (
        (BRIDGE_PATH, BRIDGE_DERIVED_SHA256, BRIDGE_DERIVED_BYTES,
         state["bridge_bytes"], bridge_result),
        (PUBLIC_PATH, PUBLIC_DERIVED_SHA256, PUBLIC_DERIVED_BYTES,
         state["public_bytes"], public_result),
    ):
        observed, actual = kernel.authenticate_file(
            paths["source"] / path, expected=expected_sha,
            maximum=MAX_SOURCE_BYTES, exact_size=expected_size, capture=True)
        require(type(actual) is bytes and actual == expected_raw
                and stat.S_IMODE(os.lstat(paths["source"] / path).st_mode)
                == 0o600,
                "reauthenticate the exact complete exclusive private overlay")
        copies[path] = {
            "path": v9.sanitized(observed["path"], workdir, family),
            "sha256": observed["sha256"], "bytes": observed["size_bytes"],
            "device": observed["device"], "inode": observed["inode"],
            "exclusive_creation": True, "same_inode_readback_verified": True,
            "file_fsync_completed": True, "source_overlay": overlay,
        }
    require(set(copies) == expected,
            "close the exact seven-original, two-overlay first-party snapshot")
    for item in RUST_OWNERS:
        read_owner(item)
    _APPLIED.add((workdir, phase))
    return copies


def verify_reproduced_phases(v9: types.ModuleType, v7: types.ModuleType,
                             workdir: str, phases: list[dict[str, Any]],
                             steps: list[dict[str, Any]]) -> dict[str, Any]:
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases] == list(PHASES)
            and type(steps) is list and len(steps) == 2 * len(PROCESS_NAMES),
            "require two actually completed ordered first-party Rust phases")
    identities: set[tuple[int, int]] = set()
    expected_paths = {item.path for item in RUST_OWNERS}
    for phase_index, phase in enumerate(phases):
        owners = phase.get("fresh_source_owners")
        require(type(owners) is dict and set(owners) == expected_paths,
                "require all nine independently identified phase source owners")
        for item in RUST_OWNERS:
            expected_sha, expected_bytes = expected_source_owner(item.path)
            observed = owners.get(item.path)
            require(type(observed) is dict
                    and observed.get("sha256") == expected_sha
                    and observed.get("bytes") == expected_bytes
                    and type(observed.get("device")) is int
                    and type(observed.get("inode")) is int
                    and (observed["device"], observed["inode"])
                    not in identities,
                    "reject omitted, stale, linked, or reused phase source")
            identities.add((observed["device"], observed["inode"]))
        for path in (BRIDGE_PATH, PUBLIC_PATH):
            applied = owners[path].get("source_overlay")
            require(type(applied) is dict and applied.get("status") == "PASS"
                    and applied.get("phase") == PHASES[phase_index]
                    and applied.get("source_apply_count") == 1,
                    "require exactly one genuine overlay per private phase")
            observed_digest = (applied.get("derived_sha256")
                               if path == BRIDGE_PATH
                               else applied.get("derived_source_sha256"))
            require(observed_digest == expected_source_owner(path)[0],
                    "reject the historical V1 adapter or substituted bridge")
    pids: set[int] = set()
    for index, process in enumerate(steps):
        require(type(process) is dict
                and process.get("name")
                == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in pids
                and process.get("exit_status") == 0,
                "require 28 distinct actually successful ordered processes")
        pids.add(process["pid"])
    outputs: dict[str, Any] = {}
    comparisons: dict[str, Any] = {}
    for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
        left = phases[0].get("native_outputs", {}).get(role)
        right = phases[1].get("native_outputs", {}).get(role)
        require(type(left) is dict and type(right) is dict
                and left.get("file_name") == right.get("file_name") == filename
                and left.get("sha256") == right.get("sha256")
                and left.get("size_bytes") == right.get("size_bytes")
                and left.get("path") != right.get("path")
                and (left.get("device"), left.get("inode"))
                != (right.get("device"), right.get("inode"))
                and left.get("audit") == right.get("audit"),
                "reject an irreproducible or borrowed native Rust output")
        first = v9._RAW_PHASE_ELF.get((workdir, PHASES[0], role))
        second = v9._RAW_PHASE_ELF.get((workdir, PHASES[1], role))
        require(type(first) is bytes and type(second) is bytes
                and digest(first) == left["sha256"]
                and digest(second) == right["sha256"] and first == second,
                "compare complete actual bytes from both independent phases")
        compared = v7.compare_owned_elf64(first, second)
        require(type(compared) is dict
                and compared.get("byte_identical") is True,
                "prove that both independently owned ELF outputs reproduce")
        comparisons[role] = compared
        outputs[role] = {"file_name": filename, "sha256": left["sha256"],
                         "size_bytes": left["size_bytes"],
                         "fresh_independent_inode_count": 2,
                         "audit": left["audit"]}
    for item in RUST_OWNERS:
        read_owner(item)
    return {"status": "PASS", "independent_fresh_phase_count": 2,
            "source_owners_per_phase": 9,
            "unchanged_source_owners_per_phase": 7,
            "bridge_overlay_count": 2, "corrected_public_overlay_count": 2,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "byte_identical": True, "unique_process_count": len(pids),
            "native_role_count": 2, "raw_elf_comparisons": comparisons,
            "native_outputs": outputs, "prebuilt_artifact_count": 0,
            "native_libraries_loaded": 0, "original_sources_modified": False}


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in value),
            "require one exact safe independently authorized V13 evidence label")
    return value


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(type(failed) is bool, "require a real, explicit build outcome")
    base = "native-source-build-v13-rust-" + checked_label(label)
    if failed:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def publish_report(kernel: types.ModuleType,
                   report: dict[str, Any]) -> dict[str, Any]:
    require(type(report) is dict and report.get("status") in ("PASS", "FAIL"),
            "publish only a genuinely executed and separately authorized build")
    label = checked_label(report.get("label"))
    archive_name, receipt_name = evidence_names(label,
                                                 report["status"] == "FAIL")
    directory = ROOT / EVIDENCE_PATH
    plain = canonical(report)
    require(0 < len(plain) <= MAX_REPORT_BYTES,
            "bound the actual complete corrected Rust build report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_REPORT_BYTES,
            "bound the deterministic single-member V13 evidence archive")
    published = kernel.write_fresh(directory / archive_name, archive,
                                   synchronize=True)
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "build_status": report["status"],
        "family": FAMILY, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": published["sha256"],
        "archive_bytes": published["bytes"],
        "archive_publication": published,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "historical_v33_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "historical_v33_reference_count": CURRENT_HISTORY_REFERENCES,
        "prepublication_repository_evidence_owner_lower_bound":
            ACTUAL_EVIDENCE_OWNERS,
        "prepublication_authenticated_reference_lower_bound":
            ACTUAL_HISTORY_REFERENCES,
        "later_append_only_evidence_allowed": True,
        "new_actual_evidence_owner_count": 2,
        "repository_evidence_owner_lower_bound_after_publication":
            ACTUAL_EVIDENCE_OWNERS + 2,
        "authenticated_reference_lower_bound_after_publication":
            ACTUAL_HISTORY_REFERENCES + 2,
        "repository_evidence_owner_count_after_publication": "NOT MEASURED",
        "authenticated_history_reference_count_after_publication":
            "NOT MEASURED",
        "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
        "public_derived_sha256": PUBLIC_DERIVED_SHA256,
        "bridge_overlay_apply_count": report.get("bridge_overlay_apply_count", 0),
        "corrected_public_overlay_apply_count":
            report.get("corrected_public_overlay_apply_count", 0),
        "expected_actual_compiler_process_count": 2 * len(PROCESS_NAMES),
        "actual_compiler_process_count":
            report.get("actual_compiler_process_count", 0),
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt_raw = canonical(receipt)
    require(len(receipt_raw) <= MAX_SOURCE_BYTES,
            "bound the independently durable actual V13 build receipt")
    recorded = kernel.write_fresh(directory / receipt_name, receipt_raw,
                                  synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    return {"schema": SCHEMA + "-published-build",
            "status": report["status"], "family": FAMILY, "label": label,
            "archive_relative": EVIDENCE_PATH + "/" + archive_name,
            "archive_sha256": published["sha256"],
            "receipt_relative": EVIDENCE_PATH + "/" + receipt_name,
            "receipt_sha256": recorded["sha256"],
            "receipt_directory_fsync": receipt_sync,
            "failure_preserved": report["status"] == "FAIL",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False, "performance": "NOT MEASURED",
            "memory": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False}


def run_build(arguments: argparse.Namespace) -> dict[str, Any]:
    global _ACTIVE
    context, state = verify_context(arguments.source_sha256,
                                    arguments.protocol_sha256,
                                    arguments.contract_sha256)
    expected_pins = {item.path + "=" + item.sha256 for item in RUST_OWNERS}
    require(type(arguments.owned_source_sha256) is list
            and len(arguments.owned_source_sha256) == len(RUST_OWNERS)
            and set(arguments.owned_source_sha256) == expected_pins,
            "independently and explicitly pin all nine original Rust sources")
    require(arguments.bridge_derived_sha256 == BRIDGE_DERIVED_SHA256
            and arguments.bridge_derived_bytes == BRIDGE_DERIVED_BYTES
            and arguments.public_derived_sha256 == PUBLIC_DERIVED_SHA256
            and arguments.public_derived_bytes == PUBLIC_DERIVED_BYTES,
            "explicitly pin both exact independent corrected private overlays")
    label = checked_label(arguments.label)
    v9 = state["v9"]
    v7 = v9.load_frozen_module("_rebar_v13_frozen_actual_low_level_v7",
                               v9.V7_OWNERS["source"])
    require(v7.SCHEMA == "rebar-phase2-owned-native-source-build-v7",
            "load only the exactly pinned first-party V7 low-level kernel")
    kernel = v7.load_frozen_v4()
    require(_ACTIVE is None and not _APPLIED,
            "reject a reused, nested, or cross-family corrected V13 build")
    state["kernel"] = kernel
    _ACTIVE = state
    v9.install_v9_build_kernel(v7, kernel)
    kernel.copy_snapshot = copy_dual_snapshot
    for failed in (False, True):
        for name in evidence_names(label, failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE_PATH / name)
    workdir = tempfile.mkdtemp(prefix=ROOT_PREFIX, dir="/tmp")
    checked_workdir(workdir)
    steps: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []

    def make_report(status: str, *, reproduction: Any = None,
                    error: Exception | None = None) -> dict[str, Any]:
        report: dict[str, Any] = {
            "schema": SCHEMA + "-actual-corrected-dual-overlay-build",
            "version": VERSION, "status": status, "family": FAMILY,
            "label": label, "source_sha256": arguments.source_sha256,
            "protocol_sha256": arguments.protocol_sha256,
            "contract_sha256": arguments.contract_sha256,
            "frozen_context": context, "root_prefix": ROOT_PREFIX,
            "historical_v33_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
            "historical_v33_reference_count": CURRENT_HISTORY_REFERENCES,
            "prepublication_repository_evidence_owner_lower_bound":
                ACTUAL_EVIDENCE_OWNERS,
            "prepublication_authenticated_reference_lower_bound":
                ACTUAL_HISTORY_REFERENCES,
            "later_append_only_evidence_allowed": True,
            "bridge_derived_sha256": BRIDGE_DERIVED_SHA256,
            "public_derived_sha256": PUBLIC_DERIVED_SHA256,
            "historical_public_derived_sha256":
                HISTORICAL_PUBLIC_DERIVED_SHA256,
            "bridge_overlay_apply_count": len(_APPLIED),
            "corrected_public_overlay_apply_count": len(_APPLIED),
            "expected_actual_compiler_process_count": 2 * len(PROCESS_NAMES),
            "actual_compiler_process_count": len(steps),
            "phase_count": len(completed), "phases": completed,
            "compiler_processes": steps,
            "reproducibility": reproduction,
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False, "candidate_processes_started": 0,
            "candidate_imports": 0, "native_libraries_loaded": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "performance": "NOT MEASURED",
            "memory": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        if error is not None:
            report["error_type"] = type(error).__name__
            report["error_message"] = str(error)[:8192]
        return report

    try:
        v9.prepare_private_phases(kernel, workdir)
        for phase in PHASES:
            result = kernel.exact_build_phase(workdir, FAMILY, phase,
                                              state["originals"], steps)
            result["native_forensics"] = v9.record_native_forensics(
                v7, kernel, workdir, phase, result, steps)
            completed.append(result)
        reproduction = verify_reproduced_phases(v9, v7, workdir,
                                                 completed, steps)
        require(len(steps) == 2 * len(PROCESS_NAMES) and len(_APPLIED) == 2
                and reproduction.get("status") == "PASS"
                and reproduction.get("unique_process_count") == 28
                and reproduction.get("bridge_overlay_count") == 2
                and reproduction.get("corrected_public_overlay_count") == 2,
                "require two real corrected phases and 28 actual unique processes")
        return publish_report(kernel, make_report("PASS",
                                                   reproduction=reproduction))
    except Exception as error:
        for item in RUST_OWNERS:
            read_owner(item)
        return publish_report(kernel, make_report("FAIL", error=error))


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    option_names = [item for item in values if item.startswith("--")
                    and item != "--owned-source-sha256"]
    require(len(option_names) == len(set(option_names)),
            "reject repeated or ambiguous V13 source-build authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", "--render-contract",
                       dest="emit_contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    parser.add_argument("--owned-source-sha256", action="append")
    parser.add_argument("--bridge-derived-sha256")
    parser.add_argument("--bridge-derived-bytes", type=int)
    parser.add_argument("--public-derived-sha256")
    parser.add_argument("--public-derived-bytes", type=int)
    options = parser.parse_args(values)
    checked_sha256(options.source_sha256, "V13 source")
    checked_sha256(options.protocol_sha256, "V13 protocol")
    build_values = (options.label, options.owned_source_sha256,
                    options.bridge_derived_sha256,
                    options.bridge_derived_bytes,
                    options.public_derived_sha256,
                    options.public_derived_bytes)
    if options.emit_contract:
        require(options.contract_sha256 is None
                and all(value is None for value in build_values),
                "contract emission never authorizes a snapshot, build, or run")
    else:
        checked_sha256(options.contract_sha256, "V13 canonical contract")
        if options.build:
            checked_label(options.label)
            checked_sha256(options.bridge_derived_sha256,
                           "independent bridge-derived source")
            checked_sha256(options.public_derived_sha256,
                           "independent corrected public-derived source")
            require(type(options.owned_source_sha256) is list
                    and len(options.owned_source_sha256) == len(RUST_OWNERS)
                    and type(options.bridge_derived_bytes) is int
                    and type(options.public_derived_bytes) is int,
                    "require all independently pinned original and derived owners")
        else:
            require(all(value is None for value in build_values),
                    "source-only gates can never authorize a build or snapshot")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.emit_contract:
            with SourceOnlyWall() as wall:
                result = contract_document(options.source_sha256,
                                           options.protocol_sha256)
                require(all(count == 0 for count in wall.blocked.values()),
                        "contract emission attempted a real source-only effect")
        elif options.self_test:
            result = self_test(options.source_sha256,
                               options.protocol_sha256,
                               options.contract_sha256)
        elif options.verify_frozen_context:
            result, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256,
                                       options.contract_sha256)
        else:
            result = run_build(options)
        output = canonical(result)
        require(len(output) <= MAX_REPORT_BYTES,
                "reject an unbounded corrected Rust source-build result")
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()
        return 0 if result.get("status", "PASS") == "PASS" else 1
    except (GateError, OSError, ValueError, TypeError, UnicodeError,
            RecursionError, SyntaxError, OverflowError, KeyError,
            AttributeError) as error:
        sys.stderr.write("owned Rust flag source build v13 rejected: "
                         + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
