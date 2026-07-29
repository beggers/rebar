#!/usr/bin/env python3
"""Freeze two reproducible offline builds of the combined first-party Rust bridge."""

from __future__ import annotations

import argparse
import ast
import builtins
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
import tomllib
import types
import zlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
VERSION = 16
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py"
PROTOCOL_PATH = "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md"
CONTRACT_PATH = "oracle/phase2/rust-buffer-shape-source-build-v16.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_TOOLCHAIN_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 2 * 1024 * 1024
MAX_AST_NODES = 200_000
PHASES = ("reference-a", "reference-b")
BUFFER_GRAPH_VERSION = 49
FINAL_GRAPH_VERSION = 50
CURRENT_EVIDENCE_OWNER_LOWER_BOUND = 176
CURRENT_HISTORY_REFERENCE_LOWER_BOUND = 181
BRIDGE_PATH = "candidates/rust/py_bridge.c"
PUBLIC_PATH = "candidates/rust_candidate.py"
ACTUAL_BRIDGE_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
ACTUAL_BRIDGE_BYTES = 176_118
CORRECTED_ADAPTER_SHA256 = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
CORRECTED_ADAPTER_BYTES = 31_934
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


GOAL = Owner("GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)

PHASE_ONE = Owner("oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)

RUST_OWNERS = (
    Owner("candidates/rust/Cargo.lock",
        "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    Owner("candidates/rust/Cargo.toml",
        "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    Owner("candidates/rust/py_bridge.c",
        "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
    Owner("candidates/rust/src/lib.rs",
        "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    Owner("candidates/rust/src/newline.rs",
        "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    Owner("candidates/rust/src/search.rs",
        "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    Owner("candidates/rust/src/stack.rs",
        "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    Owner("candidates/rust/src/unicode_tables.rs",
        "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    Owner("candidates/rust_candidate.py",
        "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
)

REFERENCE_SOURCE = (
    Owner("tools/verify_owned_public_type_reference_context_v1.py",
        "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc", 102474),
    Owner("oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md",
        "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018", 10691),
    Owner("oracle/phase1/p0-public-type-reference-context-v1.json",
        "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b", 13965),
)

REFERENCE_RECEIPT = Owner("oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json",
    "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966", 2509)

HISTORICAL_BRIDGE_REPAIR = (
    Owner("tools/apply_owned_rust_source_repair_v1.py",
        "1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851", 59388),
    Owner("oracle/phase2/RUST-SOURCE-REPAIR-V1.md",
        "df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b", 5496),
    Owner("oracle/phase2/rust-source-repair-v1.json",
        "1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b", 8306),
)

HISTORICAL_ADAPTER_REPAIR = (
    Owner("tools/apply_owned_rust_public_contract_source_repair_v3.py",
        "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060),
    Owner("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md",
        "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405),
    Owner("oracle/phase2/rust-public-contract-source-repair-v3.json",
        "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817),
)

LOW_LEVEL_V9 = (
    Owner("tools/reproduce_owned_native_source_build_v9.py",
        "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f", 81124),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V9.md",
        "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc", 4960),
    Owner("oracle/phase2/native-source-build-v9.json",
        "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da", 9134),
)

LOW_LEVEL_V7 = (
    Owner("tools/reproduce_owned_native_source_build_v7.py",
        "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7", 300624),
    Owner("oracle/phase2/NATIVE-SOURCE-BUILD-V7.md",
        "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313", 8063),
    Owner("oracle/phase2/native-source-build-v7.json",
        "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819", 28924),
)

HISTORICAL_V13_BUILD = (
    Owner("tools/reproduce_owned_rust_pattern_repr_source_build_v13.py",
        "2ec050c9902cbb3a239ed3a2dce3258344300b40546e37aea374cf18a9c8b797", 133023),
    Owner("oracle/phase2/RUST-PATTERN-REPR-SOURCE-BUILD-V13.md",
        "3c486fdb63041b4f6060a6147186dd93c8339cbdff5f8060f597ab156ff05701", 5894),
    Owner("oracle/phase2/rust-pattern-repr-source-build-v13.json",
        "15023a0a484715f2d97ae5ea9649bb16fe3d30781d601635bda40c246c5906aa", 20519),
)

HISTORICAL_V13_BUILD_RECEIPT = Owner("oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0-publication-receipt.json",
    "4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805", 2437)

HISTORICAL_RUST_CAMPAIGN = (
    Owner("tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104", 505616),
    Owner("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md",
        "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840", 8433),
    Owner("oracle/phase2/repaired-rust-original-campaign-v7.json",
        "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5", 46385),
)

HISTORICAL_RUST_RECEIPT = Owner("oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures-publication-receipt.json",
    "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943", 8450)

HISTORICAL_V48_GRAPH = (
    Owner("tools/render_candidate_current_overview_v48.py",
        "29604bd560dcba08f95ca8bcc792bf277c43a4680d94a82990fd341a1b0f6394", 89718),
    Owner("docs/evidence/candidate-current-overview-v48.inputs.json",
        "d1bc5998012a8f174788a4c28fad7fa1116078a3cbb859b0f952eb65777e33da", 523944),
    Owner("docs/evidence/candidate-current-overview-v48.json",
        "bfd591aebf6aea805c8f6a4b5665d87ceca6b2574513bb5cdfb8331b36176305", 1428930),
    Owner("docs/evidence/candidate-current-overview-v48.svg",
        "cf8955199d714854faeea4d5c0cabf4431010949a7b7d5ed81d5b65f14b74903", 20331),
)

BUFFER_FEATURE = (
    Owner("tools/apply_owned_rust_buffer_shape_source_repair_v1.py",
        "9c2a3642f2cda9fc85fd391baf4e0d57b25117f444d3a831592e8b62de3a627b", 64345),
    Owner("oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-REPAIR-V1.md",
        "67ba62acc8e51a6868404ea3faeb1aaaacb1d053cc1c915bef0c397edf5ac408", 5033),
    Owner("oracle/phase2/rust-buffer-shape-source-repair-v1.json",
        "ffa76d1724396fae5816cf96e0ae2104bcce8fc5eb246b8306d4441db0fe4a1b", 11454),
)

BUFFER_VARIANT = Owner("candidates/rust/variants/buffer_shape_v1/py_bridge.c",
    "29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3", 180436)

BUFFER_GRAPH = (
    Owner("tools/render_candidate_current_overview_v49.py",
        "03ae29acb80817de9cfbd512e919702cea1a761f2bfa69c638b4644f179304b0", 74565),
    Owner("docs/evidence/candidate-current-overview-v49.inputs.json",
        "0d78d45480bfd701024b733d33c43651a6ae29c760ac8f88c9404ee061d5bc76", 540049),
    Owner("docs/evidence/candidate-current-overview-v49.json",
        "1b5dad9574883e45b6bad5b2c9ec69f59a77e2ab079d7ed23a226280a4a4f4a4", 1475826),
    Owner("docs/evidence/candidate-current-overview-v49.svg",
        "761d1303e617827b79f0dd3ee24ab062d1282ea5cf568c4ca89c65a8ae19b75c", 13490),
)

PICKLE_FEATURE = (
    Owner("tools/apply_owned_rust_match_pickle_source_repair_v1.py",
        "85383f4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517", 81784),
    Owner("oracle/phase2/RUST-MATCH-PICKLE-SOURCE-REPAIR-V1.md",
        "fad29fdcd3956ae99f9db40afae33b51eb99fb743baf89540a4ee7aafb7ac1af", 5105),
    Owner("oracle/phase2/rust-match-pickle-source-repair-v1.json",
        "5456535223cb029d41e8739696bde30b2b7127995fd0ef30286ff0488b1ed133", 15276),
)

COMBINED_VARIANT = Owner("candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c",
    "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335", 181004)

FINAL_GRAPH = (
    Owner("tools/render_candidate_current_overview_v50.py",
        "4077fbf6703e98325c4b4eacea95d27608a3bb21a93143024094154385787f45", 60235),
    Owner("docs/evidence/candidate-current-overview-v50.inputs.json",
        "8506587243c98fa75a14dfc74cfc918772a74eadebc3f2728772d1d0d94bd726", 560297),
    Owner("docs/evidence/candidate-current-overview-v50.json",
        "60f0648be19016e5d8ebfa01f93c2c50c32aa4fb981fc0d518902b8b9985005e", 1535160),
    Owner("docs/evidence/candidate-current-overview-v50.svg",
        "a114a7b813c4c1fc470950639adc50ffb7118dd91a31d9f63dee6ba46e04f8b9", 14209),
)

TOOLCHAIN = (
    ToolOwner("/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/rustc", "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6", 644784, 2064, 31359570, 0o755, 1000),
    ToolOwner("/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/cargo", "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66", 42185192, 2064, 31359488, 0o755, 1000),
    ToolOwner("/usr/bin/x86_64-linux-gnu-gcc-13", "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26", 1023032, 1048708, 10445975, 0o755, 65534),
    ToolOwner("/usr/bin/x86_64-linux-gnu-readelf", "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0", 789280, 1048708, 10446013, 0o755, 65534),
)


class GateError(Exception):
    """Reject changed source, evidence, or an unauthorized build."""


class ForbiddenEffect(GateError):
    """Reject a genuine external action attempted by a source-only check."""


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
    base = parsed.parts[-1].lower()
    require(not value.endswith(".gz")
            and base not in ("readme.md", "experiment-log.md", "reproducing.md"),
            "source-only context never reads archives or mutable project documents")
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



def load_frozen_module(name: str, owner: Owner,
                       raw: bytes) -> types.ModuleType:
    require(type(name) is str and name.startswith("_rebar_v16_frozen_")
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



def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in value),
            "require one exact safe independently authorized V16 evidence label")
    return value



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



def replace_once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    require(type(raw) is bytes and type(old) is bytes and type(new) is bytes,
            "source repair accepts bytes only")
    require(old != new and raw.count(old) == 1,
            "source repair requires one authentic anchor: " + label)
    return raw.replace(old, new, 1)



def byte_assignments(raw: bytes, path: str,
                     required: tuple[str, ...]) -> dict[str, bytes]:
    try:
        tree = ast.parse(raw, filename=path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise GateError("historical source cannot be parsed as bounded AST") from error
    pending: list[ast.AST] = [tree]
    seen = 0
    while pending:
        node = pending.pop()
        seen += 1
        require(seen <= 50000, "historical source exceeded its AST allowance")
        pending.extend(ast.iter_child_nodes(node))
    found: dict[str, bytes] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in required:
                require(target.id not in found and
                        isinstance(node.value, ast.Constant) and
                        type(node.value.value) is bytes,
                        "historical repair must expose one literal byte anchor")
                found[target.id] = node.value.value
    require(set(found) == set(required),
            "historical repair byte-literal anchors are incomplete")
    return found



def corrected_bridge(source: bytes, repair_source: bytes) -> bytes:
    names = byte_assignments(
        repair_source, "tools/apply_owned_rust_source_repair_v1.py",
        ("OLD_BLOCK", "NEW_BLOCK"),
    )
    fixed = replace_once(source, names["OLD_BLOCK"], names["NEW_BLOCK"],
                         "actual-v13-historical-first-party-bridge")
    require(len(fixed) == ACTUAL_BRIDGE_BYTES and
            digest(fixed) == ACTUAL_BRIDGE_SHA256,
            "the actual V13 corrected Rust bridge did not reproduce")
    return fixed



def corrected_adapter(source: bytes, repair_source: bytes) -> bytes:
    names = byte_assignments(
        repair_source, "tools/apply_owned_rust_public_contract_source_repair_v3.py",
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "OLD_ERROR_BLOCK",
         "V2_ERROR_BLOCK", "OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK",
         "V3_PATTERN_BLOCK"),
    )
    fixed = source
    for old, new, label in (
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "first-party-V2-flags"),
        ("OLD_ERROR_BLOCK", "V2_ERROR_BLOCK", "first-party-V2-pattern-error"),
        ("OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK", "first-party-V2-pattern-value"),
        ("V2_PATTERN_BLOCK", "V3_PATTERN_BLOCK", "actual-V13-first-party-adapter"),
    ):
        fixed = replace_once(fixed, names[old], names[new], label)
    require(len(fixed) == CORRECTED_ADAPTER_BYTES and
            digest(fixed) == CORRECTED_ADAPTER_SHA256,
            "the actual V13 corrected Rust public adapter did not reproduce")
    return fixed



def derive_buffer_variant(actual: bytes, verifier_source: bytes) -> bytes:
    blocks = byte_assignments(
        verifier_source,
        BUFFER_FEATURE[0].path,
        (
            "HELPER_ANCHOR",
            "HELPER",
            "OLD_CACHE_DECLARATION",
            "NEW_CACHE_DECLARATION",
            "OLD_BUFFER_MATERIALIZATION",
            "NEW_BUFFER_MATERIALIZATION",
            "OLD_HASH",
            "NEW_HASH",
            "OLD_TEMPLATE_FAILURE",
            "NEW_TEMPLATE_FAILURE",
            "OLD_EXPANSION_FAILURE",
            "NEW_EXPANSION_FAILURE",
            "OLD_CAPTURE",
            "NEW_CAPTURE",
            "SUBSTITUTION_START",
            "SUBSTITUTION_END",
            "SNAPSHOT_ANCHOR",
            "SNAPSHOT_INSERTION",
            "UNSAFE_CONTIGUOUS_COPY",
            "SAFE_CONTIGUOUS_COPY",
            "OLD_SUBJECT_ORDER",
            "SAFE_SUBJECT_ORDER",
        ),
    )
    require(len(actual) == ACTUAL_BRIDGE_BYTES and
            digest(actual) == ACTUAL_BRIDGE_SHA256,
            "buffer repair must start from the actually tested V13 bridge")
    fixed = replace_once(actual, blocks["HELPER_ANCHOR"],
                         blocks["HELPER"] + blocks["HELPER_ANCHOR"], "owned original-error restoration")
    for old, new, label in (
        (blocks["OLD_CACHE_DECLARATION"], blocks["NEW_CACHE_DECLARATION"], "single observed original hash"),
        (blocks["OLD_BUFFER_MATERIALIZATION"], blocks["NEW_BUFFER_MATERIALIZATION"],
         "observable buffer acquisition and hash order"),
        (blocks["OLD_HASH"], blocks["NEW_HASH"], "do not repeat original replacement hashing"),
        (blocks["OLD_TEMPLATE_FAILURE"], blocks["NEW_TEMPLATE_FAILURE"],
         "restore replacement error from original exporter"),
        (blocks["OLD_EXPANSION_FAILURE"], blocks["NEW_EXPANSION_FAILURE"],
         "restore original match-expansion template error"),
        (blocks["OLD_CAPTURE"], blocks["NEW_CAPTURE"], "check fresh capture buffer bounds"),
    ):
        fixed = replace_once(fixed, old, new, label)
    start = fixed.find(blocks["SUBSTITUTION_START"])
    require(start >= 0 and fixed.count(blocks["SUBSTITUTION_START"]) == 1,
            "the first-party substitution implementation must be unique")
    stop = fixed.find(blocks["SUBSTITUTION_END"], start + len(blocks["SUBSTITUTION_START"]))
    require(stop > start and fixed.count(blocks["SUBSTITUTION_END"]) == 1,
            "the first-party substitution boundary must be unique")
    function = fixed[start:stop]
    old_local = b"    PyObject *raw = NULL;\n    PyObject *tokens = NULL;\n"
    new_local = old_local + b"    PyObject *subject_snapshot = NULL;\n"
    function = replace_once(function, old_local, new_local,
                            "one owned substitution subject snapshot")
    lines: list[bytes] = []
    released = 0
    for line in function.splitlines(keepends=True):
        body = line.lstrip(b" \t")
        if body == b"rust_subject_release(&subject);\n":
            prefix = line[:len(line) - len(body)]
            lines.append(line)
            lines.append(prefix + b"Py_XDECREF(subject_snapshot);\n")
            released += 1
        else:
            lines.append(line)
    require(released == 6, "all six existing subject cleanups must remain balanced")
    function = b"".join(lines)
    function = replace_once(function, blocks["SNAPSHOT_ANCHOR"],
                            blocks["SNAPSHOT_INSERTION"] + blocks["SNAPSHOT_ANCHOR"],
                            "snapshot a live, owned noncallback subject")
    fixed = fixed[:start] + function + fixed[stop:]
    fixed = replace_once(fixed, blocks["UNSAFE_CONTIGUOUS_COPY"], blocks["SAFE_CONTIGUOUS_COPY"],
                         "copy possibly strided FULL_RO buffers safely")
    fixed = replace_once(fixed, blocks["OLD_SUBJECT_ORDER"], blocks["SAFE_SUBJECT_ORDER"],
                         "acquire and snapshot the subject before hashing replacement")
    require(len(fixed) == BUFFER_VARIANT.size and digest(fixed) == BUFFER_VARIANT.sha256,
            "the complete reviewed buffer-shape source variant did not reproduce")
    require(fixed.count(b"rust_restore_original_template_error(") == 3 and
            fixed.count(b"PyBuffer_ToContiguous(") >= 1 and
            fixed.count(b"PyBUF_FULL_RO") >= 1,
            "general original-error and strided-buffer protections are missing")
    for marker in (b"__reduce__", b"__reduce_ex__"):
        require(fixed.count(marker) == actual.count(marker),
                "the separate match-pickling source feature must remain untouched")
    for forbidden in (
        b"import re\n", b"from re import", b"import _sre", b"from _sre",
        b"regex.compile", b"pcre", b"oniguruma", b"candidates.vm_candidate",
        b"candidates.zig_candidate", b"candidates.cpp_candidate",
        b"candidates.go_candidate", b"candidates.fortran_candidate",
    ):
        require(fixed.count(forbidden) == actual.count(forbidden),
                "a delegated or cross-family regex engine was introduced")
    return fixed



def derive_combined_variant(buffer: bytes, verifier_source: bytes) -> bytes:
    blocks = byte_assignments(
        verifier_source,
        PICKLE_FEATURE[0].path,
        (
            "PICKLE_OLD_MATCH",
            "PICKLE_NEW_MATCH",
            "PICKLE_OLD_SCANNER",
            "PICKLE_NEW_SCANNER",
            "PICKLE_OLD_METHODS",
            "PICKLE_NEW_METHODS",
        ),
    )
    require(type(buffer) is bytes and
            len(buffer) == BUFFER_VARIANT.size and
            digest(buffer) == BUFFER_VARIANT.sha256,
            "match-pickle repair must start from the exact frozen V49 buffer variant")
    fixed = replace_once(buffer, blocks["PICKLE_OLD_MATCH"], blocks["PICKLE_NEW_MATCH"],
                         "owned match reconstruction and signed C-int protocol")
    fixed = replace_once(fixed, blocks["PICKLE_OLD_SCANNER"], blocks["PICKLE_NEW_SCANNER"],
                         "preserve scanner through the shared owned reconstructor")
    fixed = replace_once(fixed, blocks["PICKLE_OLD_METHODS"], blocks["PICKLE_NEW_METHODS"],
                         "register the distinct native protocol-aware match reducer")
    require(len(fixed) == COMBINED_VARIANT.size and digest(fixed) == COMBINED_VARIANT.sha256,
            "the complete combined buffer-shape and match-pickle variant changed")
    require(fixed.count(b"rust_owned_pickle_reconstruction(") == 4,
            "the owned match and scanner must share exactly one reconstructor")
    require(fixed.count(b"PyLong_AsInt(protocol)") == 1 and
            fixed.count(b"if (protocol_number < 2)") == 1,
            "match reduction must preserve signed C-int pickle protocols")
    require(fixed.count(b'{Py_tp_new, (void *)rust_match_new}') == 1,
            "the native Match constructor and public adapter must remain unchanged")
    for marker in (b"PyBuffer_ToContiguous(", b"PyBUF_FULL_RO",
                   b"rust_restore_original_template_error(",
                   b"Py_XDECREF(subject_snapshot);",
                   b"if (!callback && subject.view.obj != NULL)",
                   b"rust_match_copy(", b"rust_match_deepcopy("):
        require(fixed.count(marker) == buffer.count(marker),
                "the frozen first-party buffer or immutable-copy behavior changed")
    require(fixed.count(b'PyImport_ImportModule("copyreg")') ==
            buffer.count(b'PyImport_ImportModule("copyreg")') == 1,
            "serialization must reuse the existing scanner copyreg import")
    for forbidden in (b"import re\\n", b"from re import", b"import _sre",
                      b"from _sre", b"regex.compile", b"pcre", b"oniguruma",
                      b"candidates.vm_candidate", b"candidates.zig_candidate",
                      b"candidates.cpp_candidate", b"candidates.go_candidate",
                      b"candidates.fortran_candidate"):
        require(fixed.count(forbidden) == buffer.count(forbidden),
                "match reconstruction introduced a delegated regex engine")
    return fixed




def phase_boundary() -> dict[str, Any]:
    return {
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_benchmark_files_read": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_clock_samples": 0,
        "actual_compiler_processes_started": 0,
        "actual_hidden_cases_read": 0,
        "actual_holdout_cases_read": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "actual_network_requests": 0,
        "actual_reference_workers_started": 0,
        "actual_source_builds_started": 0,
        "actual_workspace_mutations": 0,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "confidence_intervals": "NOT MEASURED",
        "final_holdout_opened": False,
        "final_holdout_planned_case_count": 4_194_304,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "mutable_document_owners_read": 0,
        "performance": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def current_history() -> dict[str, Any]:
    return {
        "current_graph_version": FINAL_GRAPH_VERSION,
        "preserved_actual_matching_graph_version": 48,
        "authenticated_evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "authenticated_history_reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "source_inventory_family_count": 6,
        "rust_family_count": 1,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31_237,
        "original_named_private_waiver_count": 13,
        "actual_rust_candidate_status": "FAIL",
        "actual_rust_semantic_mismatch_count": 928,
        "actual_rust_verified_passing_case_count": 8_965,
        "passing_cases_derived_by_subtraction": False,
        "actual_rust_candidate_worker_count": 13,
        "actual_rust_infrastructure_failure_count": 0,
        "all_four_original_rust_targets_restored": True,
        "corrected_reference_status": "PASS",
        "corrected_reference_worker_process_ids": [81, 82],
        "corrected_reference_public_cases_per_worker": 6_912,
        "corrected_reference_cache_cases_per_worker": 96,
        "corrected_reference_full_records_sha256":
            "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "corrected_reference_cache_records_sha256":
            "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "additional_callable_reference_case_count": 50,
        "additional_callable_cases_added_to_original_denominator": False,
        "v49_buffer_variant_correctness": "NOT MEASURED",
        "v50_combined_variant_correctness": "NOT MEASURED",
        "actual_v16_build_status": "NOT RUN",
        "actual_v16_candidate_matching": "NOT RUN",
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "winner_selected": False,
    }


def expected_source_owner(path: str) -> tuple[str, int]:
    found = [owner for owner in RUST_OWNERS if owner.path == path]
    require(len(found) == 1, "require a unique original first-party Rust owner")
    original = found[0]
    if path == BRIDGE_PATH:
        return COMBINED_VARIANT.sha256, COMBINED_VARIANT.size
    if path == PUBLIC_PATH:
        return CORRECTED_ADAPTER_SHA256, CORRECTED_ADAPTER_BYTES
    return original.sha256, original.size


def synthetic_plan() -> dict[str, Any]:
    phases: list[dict[str, Any]] = []
    for index, name in enumerate(PHASES):
        rows: dict[str, dict[str, Any]] = {}
        for number, source in enumerate(RUST_OWNERS):
            expected_hash, expected_size = expected_source_owner(source.path)
            rows[source.path] = {
                "sha256": expected_hash,
                "bytes": expected_size,
                "mode": 0o600,
                "nlink": 1,
                "device": 70_016,
                "inode": 100_000 + index * 100 + number,
                "overlay_count": int(source.path in (BRIDGE_PATH, PUBLIC_PATH)),
            }
        phases.append({
            "name": name,
            "directory_mode": 0o700,
            "directory_device": 70_016,
            "directory_inode": 110_000 + index,
            "fresh_source_owners": rows,
            "native_outputs": {
                role: {
                    "file_name": filename,
                    "sha256": digest(("v16-first-party-rust-" + role).encode("ascii")),
                    "size_bytes": 8_192 if role == "engine" else 16_384,
                    "device": 70_016,
                    "inode": 120_000 + index * 10 + offset,
                }
                for offset, (role, filename) in enumerate(
                    (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME))
                )
            },
        })
    return {
        "schema": SCHEMA + "-synthetic-offline-two-phase-plan",
        "family": FAMILY,
        "root_prefix": ROOT_PREFIX,
        "graph_version": FINAL_GRAPH_VERSION,
        "historical_rust_candidate_status": "FAIL",
        "historical_rust_semantic_mismatch_count": 928,
        "historical_rust_verified_passing_case_count": 8_965,
        "corrected_reference_process_ids": [81, 82],
        "original_suite_count": 13,
        "original_case_execution_denominator": 31_237,
        "original_named_private_waiver_count": 13,
        "evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "buffer_feature_sha256": BUFFER_FEATURE[0].sha256,
        "buffer_variant_sha256": BUFFER_VARIANT.sha256,
        "pickle_feature_sha256": PICKLE_FEATURE[0].sha256,
        "combined_variant_sha256": COMBINED_VARIANT.sha256,
        "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "cargo_external_dependency_count": 0,
        "candidate_workers_started": 0,
        "clock_samples": 0,
        "matching_archive_reads": 0,
        "mutable_document_reads": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
        "phases": phases,
        "processes": [
            {
                "name": name,
                "phase": PHASES[index // len(PROCESS_NAMES)],
                "pid": 160_000 + index,
                "exit_status": 0,
            }
            for index, name in enumerate(PROCESS_NAMES * 2)
        ],
    }


def validate_synthetic_plan(plan: Any) -> dict[str, Any]:
    require(type(plan) is dict, "require a complete synthetic V16 build plan")
    required = {
        "schema": SCHEMA + "-synthetic-offline-two-phase-plan",
        "family": FAMILY,
        "root_prefix": ROOT_PREFIX,
        "graph_version": FINAL_GRAPH_VERSION,
        "historical_rust_candidate_status": "FAIL",
        "historical_rust_semantic_mismatch_count": 928,
        "historical_rust_verified_passing_case_count": 8_965,
        "corrected_reference_process_ids": [81, 82],
        "original_suite_count": 13,
        "original_case_execution_denominator": 31_237,
        "original_named_private_waiver_count": 13,
        "evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "buffer_feature_sha256": BUFFER_FEATURE[0].sha256,
        "buffer_variant_sha256": BUFFER_VARIANT.sha256,
        "pickle_feature_sha256": PICKLE_FEATURE[0].sha256,
        "combined_variant_sha256": COMBINED_VARIANT.sha256,
        "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "cargo_external_dependency_count": 0,
        "candidate_workers_started": 0,
        "clock_samples": 0,
        "matching_archive_reads": 0,
        "mutable_document_reads": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }
    for name, expected in required.items():
        require(type(plan.get(name)) is type(expected)
                and plan[name] == expected,
                "reject a substituted synthetic build invariant: " + name)
    phases = plan.get("phases")
    require(type(phases) is list and len(phases) == len(PHASES)
            and [phase.get("name") for phase in phases] == list(PHASES),
            "require exactly two genuinely distinct ordered source phases")
    all_directory_identities: set[tuple[int, int]] = set()
    all_source_identities: set[tuple[int, int]] = set()
    all_output_identities: set[tuple[int, int]] = set()
    expected_paths = {owner.path for owner in RUST_OWNERS}
    for phase in phases:
        require(type(phase) is dict
                and phase.get("directory_mode") == 0o700
                and type(phase.get("directory_device")) is int
                and phase["directory_device"] > 0
                and type(phase.get("directory_inode")) is int
                and phase["directory_inode"] > 0,
                "require genuine private owner-only phase roots")
        phase_identity = (phase["directory_device"], phase["directory_inode"])
        require(phase_identity not in all_directory_identities,
                "reject an aliased independent phase root")
        all_directory_identities.add(phase_identity)
        owners = phase.get("fresh_source_owners")
        require(type(owners) is dict and set(owners) == expected_paths,
                "require all seven original and two reviewed overlay sources")
        for original in RUST_OWNERS:
            entry = owners.get(original.path)
            actual_digest, actual_bytes = expected_source_owner(original.path)
            require(type(entry) is dict
                    and entry.get("sha256") == actual_digest
                    and entry.get("bytes") == actual_bytes
                    and entry.get("mode") == 0o600
                    and entry.get("nlink") == 1
                    and entry.get("overlay_count")
                    == int(original.path in (BRIDGE_PATH, PUBLIC_PATH))
                    and type(entry.get("device")) is int
                    and entry["device"] > 0
                    and type(entry.get("inode")) is int
                    and entry["inode"] > 0,
                    "reject an altered or non-private phase owner: " + original.path)
            identity = (entry["device"], entry["inode"])
            require(identity not in all_source_identities,
                    "reject linked, borrowed, or duplicated phase source inodes")
            all_source_identities.add(identity)
        native = phase.get("native_outputs")
        require(type(native) is dict and set(native) == {"engine", "bridge"},
                "require the two genuine first-party Rust native output roles")
        for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
            value = native[role]
            expected_digest = digest(("v16-first-party-rust-" + role).encode("ascii"))
            require(type(value) is dict and value.get("file_name") == filename
                    and value.get("sha256") == expected_digest
                    and type(value.get("size_bytes")) is int
                    and value["size_bytes"] > 0
                    and type(value.get("device")) is int
                    and value["device"] > 0
                    and type(value.get("inode")) is int
                    and value["inode"] > 0,
                    "reject an omitted, substituted, or non-native synthetic output")
            identity = (value["device"], value["inode"])
            require(identity not in all_output_identities,
                    "reject a borrowed native phase output inode")
            all_output_identities.add(identity)
    for role in ("engine", "bridge"):
        first = phases[0]["native_outputs"][role]
        second = phases[1]["native_outputs"][role]
        require(first["sha256"] == second["sha256"]
                and first["size_bytes"] == second["size_bytes"],
                "require independent reproducible first-party native outputs")
    operations = plan.get("processes")
    require(type(operations) is list
            and len(operations) == 2 * len(PROCESS_NAMES),
            "require exactly 28 complete pinned offline process roles")
    process_ids: set[int] = set()
    for index, item in enumerate(operations):
        require(type(item) is dict
                and item.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and item.get("phase") == PHASES[index // len(PROCESS_NAMES)]
                and type(item.get("pid")) is int and item["pid"] > 0
                and item["pid"] not in process_ids
                and item.get("exit_status") == 0,
                "reject missing, forged, failed, or reordered compiler processes")
        process_ids.add(item["pid"])
    return {
        "status": "PASS",
        "independent_phase_count": 2,
        "source_owners_per_phase": 9,
        "distinct_source_inode_count": 18,
        "native_output_roles_per_phase": 2,
        "distinct_native_output_inode_count": 4,
        "process_count": 28,
        "distinct_process_count": 28,
        "candidate_workers_started": 0,
        "mutable_document_reads": 0,
        "archive_reads": 0,
        "holdout": "NOT OPENED",
    }



def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    source_pin = checked_sha256(source_pin, "V16 source")
    protocol_pin = checked_sha256(protocol_pin, "V16 protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "status": (
            "SOURCE FROZEN; COMBINED FIRST-PARTY RUST BRIDGE "
            "NOT BUILT OR MATCHING-TESTED"
        ),
        "version": VERSION,
        "phase": "CANDIDATES",
        "family": FAMILY,
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "immutable_goal": owner_document(GOAL),
        "original_oracle": {
            "implementation": "CPython",
            "version": "3.14.6",
            "python": {"path": PYTHON, "sha256": PYTHON_SHA256},
            "matrix": owner_document(PHASE_ONE),
            "suite_count": 13,
            "case_execution_denominator": 31_237,
            "named_private_waiver_count": 13,
            "additional_callable_reference_case_count": 50,
            "additional_cases_included_in_original_denominator": False,
        },
        "preserved_corrected_python_reference": {
            "source_owners": [owner_document(item) for item in REFERENCE_SOURCE],
            "small_plaintext_publication_receipt":
                owner_document(REFERENCE_RECEIPT),
            "status": "PASS",
            "distinct_reference_process_ids": [81, 82],
            "original_public_type_case_count_per_worker": 6_912,
            "subclass_cache_case_count_per_worker": 96,
            "full_reference_records_sha256":
                "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
            "cache_records_sha256":
                "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
            "compressed_reference_archive_opened": False,
        },
        "preserved_actual_rust_matching": {
            "source_owners": [owner_document(item)
                               for item in HISTORICAL_RUST_CAMPAIGN],
            "small_plaintext_publication_receipt":
                owner_document(HISTORICAL_RUST_RECEIPT),
            "durable_publication_status": "PASS",
            "candidate_matching_status": "FAIL",
            "semantic_mismatch_count": 928,
            "actually_verified_passing_case_count": 8_965,
            "passing_cases_derived_by_subtraction": False,
            "completed_original_suite_count": 13,
            "distinct_candidate_worker_count": 13,
            "infrastructure_failure_count": 0,
            "all_four_original_targets_restored": True,
            "actual_matching_archive_opened": False,
            "actual_matching_archive_inflated": False,
            "later_corrected_bridge_matching_status": "NOT RUN",
        },
        "historical_v13_owned_rust_build": {
            "source_owners": [owner_document(item)
                               for item in HISTORICAL_V13_BUILD],
            "small_plaintext_publication_receipt":
                owner_document(HISTORICAL_V13_BUILD_RECEIPT),
            "actual_build_status": "PASS",
            "actual_historical_compiler_process_count": 28,
            "historical_bridge_sha256": ACTUAL_BRIDGE_SHA256,
            "historical_bridge_bytes": ACTUAL_BRIDGE_BYTES,
            "historical_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "historical_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "build_archive_opened": False,
            "build_archive_inflated": False,
            "historical_build_reexecuted": False,
        },
        "historical_v48_actual_result_graph": [
            owner_document(item) for item in HISTORICAL_V48_GRAPH
        ],
        "current_pushed_graph": {
            "version": FINAL_GRAPH_VERSION,
            "owners": [owner_document(item) for item in FINAL_GRAPH],
            "authenticated_evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
            "authenticated_history_reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
            "preserves_actual_rust_mismatch_count": 928,
            "preserves_actual_rust_verified_passing_count": 8_965,
            "mutable_document_pin_count": 0,
            "mutable_document_read_count": 0,
        },
        "first_party_source_family": {
            "family": FAMILY,
            "source_inventory_family_count": 6,
            "candidate_family_added": False,
            "canonical_rust_source_owner_count": len(RUST_OWNERS),
            "canonical_rust_source_owners":
                [owner_document(item) for item in RUST_OWNERS],
            "original_sources_modified": False,
            "rust_cargo_package_count": 1,
            "external_cargo_dependency_count": 0,
            "stdlib_regular_expression_engine": "FORBIDDEN",
            "cpython_sre_engine": "FORBIDDEN",
            "external_regular_expression_engine": "FORBIDDEN",
            "another_candidate_engine": "FORBIDDEN",
            "production_matching_fallback": "FORBIDDEN",
        },
        "v49_buffer_shape_source_feature": {
            "owners": [owner_document(item) for item in BUFFER_FEATURE],
            "reviewed_append_only_variant": owner_document(BUFFER_VARIANT),
            "historical_input_bridge_sha256": ACTUAL_BRIDGE_SHA256,
            "candidate_family_added": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
        },
        "v50_combined_buffer_shape_and_pickle_source_feature": {
            "owners": [owner_document(item) for item in PICKLE_FEATURE],
            "reviewed_append_only_variant": owner_document(COMBINED_VARIANT),
            "input_buffer_variant_sha256": BUFFER_VARIANT.sha256,
            "historical_input_bridge_sha256": ACTUAL_BRIDGE_SHA256,
            "candidate_family_added": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
        },
        "historical_first_party_source_derivation": {
            "bridge_repair_owners":
                [owner_document(item) for item in HISTORICAL_BRIDGE_REPAIR],
            "adapter_repair_owners":
                [owner_document(item) for item in HISTORICAL_ADAPTER_REPAIR],
            "historical_bridge_sha256": ACTUAL_BRIDGE_SHA256,
            "historical_bridge_bytes": ACTUAL_BRIDGE_BYTES,
            "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "method": "BOUNDED AST LITERALS; NO MODULE EXECUTION OR ARCHIVE READ",
            "canonical_original_modified": False,
        },
        "authenticated_low_level_first_party_kernels": {
            "v9": [owner_document(item) for item in LOW_LEVEL_V9],
            "v7": [owner_document(item) for item in LOW_LEVEL_V7],
            "loaded_by_source_only_gate": False,
            "historical_high_level_context_invoked": False,
            "historical_high_level_build_invoked": False,
            "loaded_only_during_explicit_v16_build": True,
        },
        "future_private_snapshot": {
            "explicit_build_required": True,
            "root_parent": "/tmp",
            "root_prefix": ROOT_PREFIX,
            "phase_names": list(PHASES),
            "peer_phases_precreated_before_source_overlay": True,
            "directory_mode": "0700",
            "source_mode": "0600",
            "source_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "original_source_owner_count_per_phase": 7,
            "combined_bridge_overlay_count_per_phase": 1,
            "historical_corrected_public_adapter_overlay_count_per_phase": 1,
            "total_source_owner_count_per_phase": 9,
            "cross_phase_source_inode_reuse": "FORBIDDEN",
            "canonical_target_mutation": "FORBIDDEN",
            "prebuilt_artifacts": "FORBIDDEN",
        },
        "future_offline_native_build": {
            "explicit_build_required": True,
            "build_status": "NOT RUN",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "toolchain": [tool_document(item) for item in TOOLCHAIN],
            "phase_count": 2,
            "processes_per_phase": len(PROCESS_NAMES),
            "total_successful_process_count": 2 * len(PROCESS_NAMES),
            "ordered_process_names_per_phase": list(PROCESS_NAMES),
            "unique_successful_process_ids_required": True,
            "offline_cargo_flags": [
                "--release", "--locked", "--offline", "--frozen", "--target-dir",
            ],
            "cargo_net_offline": True,
            "private_phase_cargo_home": True,
            "private_phase_target_directory": True,
            "network_requests_allowed": 0,
            "engine_name": ENGINE_NAME,
            "bridge_name": BRIDGE_NAME,
            "complete_raw_elf_comparison_required": True,
            "native_library_loading": "FORBIDDEN",
            "candidate_execution": "FORBIDDEN",
            "passing_build_qualifies_candidate": False,
        },
        "future_durable_evidence": {
            "explicit_build_required": True,
            "directory": EVIDENCE_PATH,
            "archive_prefix": "native-source-build-v16-rust-",
            "archive_suffix": ".json.gz",
            "failure_suffix": "-failures",
            "receipt_suffix": "-publication-receipt.json",
            "exclusive_creation": True,
            "no_follow": True,
            "mode": "0600",
            "canonical_json": True,
            "single_member_gzip_mtime": 0,
            "archive_file_fsync": True,
            "archive_directory_fsync": True,
            "independent_receipt_file_fsync": True,
            "independent_receipt_directory_fsync": True,
            "maximum_complete_report_bytes": MAX_REPORT_BYTES,
            "maximum_complete_compressed_bytes": MAX_REPORT_BYTES,
            "previous_evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
            "previous_reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
            "new_owner_count_only_after_genuine_publication": 2,
            "exact_global_evidence_census": "NOT MEASURED",
            "successful_publication_qualifies_candidate": False,
        },
        "current_history": current_history(),
        "phase_boundary": phase_boundary(),
    }



def checked_source_tree(raw: bytes, path: str) -> ast.Module:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "bound every frozen first-party Python source")
    try:
        source = raw.decode("utf-8", "strict")
        tree = ast.parse(source, filename=path, mode="exec")
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise GateError("reject malformed frozen Python source: " + path) from error
    count = 0
    pending: list[ast.AST] = [tree]
    while pending:
        node = pending.pop()
        count += 1
        require(count <= MAX_AST_NODES,
                "reject an oversized or recursive frozen source tree")
        pending.extend(ast.iter_child_nodes(node))
    return tree


def validate_owner_ast(raw: bytes, owner: Owner,
                       required_functions: tuple[str, ...]) -> None:
    tree = checked_source_tree(raw, owner.path)
    declared = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    require(set(required_functions) <= declared,
            "the independently pinned low-level owner lost required functions: "
            + owner.path)


def validate_rust_package(originals: dict[str, bytes]) -> dict[str, Any]:
    manifest_owner = next(
        item for item in RUST_OWNERS if item.path == "candidates/rust/Cargo.toml"
    )
    lock_owner = next(
        item for item in RUST_OWNERS if item.path == "candidates/rust/Cargo.lock"
    )
    try:
        manifest = tomllib.loads(
            originals[manifest_owner.path].decode("utf-8", "strict")
        )
        lock = tomllib.loads(
            originals[lock_owner.path].decode("utf-8", "strict")
        )
    except (UnicodeError, tomllib.TOMLDecodeError, ValueError) as error:
        raise GateError("reject an invalid or unowned Rust package") from error
    package = manifest.get("package")
    library = manifest.get("lib")
    release = manifest.get("profile", {}).get("release")
    packages = lock.get("package")
    require(
        type(package) is dict
        and package.get("name") == "rebar-rust-continuation"
        and package.get("version") == "0.1.0"
        and package.get("edition") == "2024"
        and package.get("rust-version") == "1.85"
        and package.get("publish") is False
        and type(library) is dict
        and library.get("crate-type") == ["cdylib"]
        and type(release) is dict
        and release.get("opt-level") == 3
        and release.get("lto") is True
        and release.get("codegen-units") == 1
        and release.get("panic") == "abort"
        and all(
            item not in manifest
            for item in (
                "dependencies", "dev-dependencies", "build-dependencies",
                "workspace", "patch", "replace",
            )
        )
        and lock.get("version") == 4
        and type(packages) is list
        and len(packages) == 1
        and type(packages[0]) is dict
        and packages[0].get("name") == "rebar-rust-continuation"
        and packages[0].get("version") == "0.1.0"
        and "dependencies" not in packages[0],
        "require one independently owned offline Rust package and no dependency",
    )
    return {
        "status": "PASS",
        "package_count": 1,
        "external_dependency_count": 0,
        "external_regex_dependency_count": 0,
        "manifest_sha256": manifest_owner.sha256,
        "lock_sha256": lock_owner.sha256,
        "network_requests": 0,
    }


def authenticate_corrected_reference(receipt: Any) -> dict[str, Any]:
    require(type(receipt) is dict,
            "require the independently durable plaintext Python reference")
    expected = {
        "schema": (
            "rebar-phase1-owned-public-type-reference-context-v1-"
            "durable-publication-receipt"
        ),
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "reference_status": "PASS",
        "source_sha256": REFERENCE_SOURCE[0].sha256,
        "protocol_sha256": REFERENCE_SOURCE[1].sha256,
        "contract_sha256": REFERENCE_SOURCE[2].sha256,
        "original_case_execution_denominator": 31_237,
        "public_case_count_per_reference": 6_912,
        "attempted_reference_worker_count": 2,
        "actual_started_reference_worker_count": 2,
        "actual_reference_worker_count": 2,
        "validated_reference_worker_count": 2,
        "completed_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": [81, 82],
        "full_reference_records_sha256":
            "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "cache_records_sha256":
            "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }
    for name, expected_value in expected.items():
        require(type(receipt.get(name)) is type(expected_value)
                and receipt[name] == expected_value,
                "reject a stale, partial, or falsified corrected reference: " + name)
    archive = receipt.get("archive")
    require(type(archive) is dict
            and archive.get("path") == (
                "oracle/phase1/evidence/"
                "public-type-reference-context-v1-cpython-3-14-6-"
                "candidate-context-p0.json.gz"
            )
            and archive.get("sha256")
            == "c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05"
            and archive.get("bytes") == 1_374_913
            and archive.get("mode") == 0o600
            and archive.get("nlink") == 1
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True,
            "verify the reference archive as receipt-only metadata; never open it")
    return {
        "status": "PASS",
        "reference_worker_process_ids": [81, 82],
        "public_cases_per_reference": 6_912,
        "subclass_cache_cases_per_reference": 96,
        "records_sha256": expected["full_reference_records_sha256"],
        "cache_records_sha256": expected["cache_records_sha256"],
        "archives_opened": 0,
        "archives_decompressed": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
    }


def authenticate_historical_rust_matching(receipt: Any) -> dict[str, Any]:
    require(type(receipt) is dict,
            "require the genuine small historical Rust publication receipt")
    expected = {
        "schema": (
            "rebar-owned-repaired-rust-original-campaign-v7-"
            "durable-publication-receipt"
        ),
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL",
        "family": "rust",
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "campaign_source_sha256": HISTORICAL_RUST_CAMPAIGN[0].sha256,
        "campaign_protocol_sha256": HISTORICAL_RUST_CAMPAIGN[1].sha256,
        "campaign_contract_sha256": HISTORICAL_RUST_CAMPAIGN[2].sha256,
        "suite_count": 13,
        "case_execution_denominator": 31_237,
        "named_private_waiver_count": 13,
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "completed_suite_count": 13,
        "actual_candidate_workers": 13,
        "infrastructure_failure_count": 0,
        "semantic_mismatch_count": 928,
        "verified_passing_case_count": 8_965,
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "historical_evidence_owner_count_before_publication": 166,
        "historical_authenticated_reference_count_before_publication": 171,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": 168,
        "resulting_authenticated_reference_count": 173,
        "corrected_reference_receipt_sha256": REFERENCE_RECEIPT.sha256,
        "corrected_reference_records_sha256":
            "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "corrected_reference_cache_records_sha256":
            "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "corrected_reference_process_ids": [81, 82],
        "corrected_reference_case_count": 6_912,
        "candidate_run_uses_both_complete_reference_vectors": True,
        "all_original_observation_vectors_complete": True,
        "corrected_bridge_source_sha256": ACTUAL_BRIDGE_SHA256,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "actual_v13_build_receipt_sha256": HISTORICAL_V13_BUILD_RECEIPT.sha256,
        "candidate_qualified": False,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "winner_selected": False,
    }
    for name, expected_value in expected.items():
        require(type(receipt.get(name)) is type(expected_value)
                and receipt[name] == expected_value,
                "reject substituted or invented historical Rust evidence: " + name)
    workers = receipt.get("actual_worker_process_ids")
    require(type(workers) is list and len(workers) == 13
            and len(set(workers)) == 13
            and all(type(value) is int and value > 0 for value in workers),
            "authenticate all 13 genuinely distinct historical Rust worker processes")
    require(
        receipt["verified_passing_case_count"]
        != receipt["case_execution_denominator"] - receipt["semantic_mismatch_count"],
        "never replace measured passing observations with subtraction",
    )
    return {
        "status": "PASS",
        "publication_status": "PASS",
        "candidate_matching_status": "FAIL",
        "semantic_mismatch_count": 928,
        "explicitly_verified_passing_case_count": 8_965,
        "passing_cases_derived_by_subtraction": False,
        "distinct_worker_process_count": 13,
        "infrastructure_failure_count": 0,
        "all_four_original_targets_restored": True,
        "authenticated_evidence_owner_lower_bound": 168,
        "authenticated_history_reference_lower_bound": 173,
        "archive_reads": 0,
        "archive_decompressions": 0,
    }


def authenticate_historical_v13_build(receipt: Any) -> dict[str, Any]:
    require(type(receipt) is dict,
            "require a complete genuine plaintext V13 Rust build receipt")
    expected = {
        "schema": (
            "rebar-phase2-owned-rust-pattern-repr-source-build-v13-"
            "durable-publication-receipt"
        ),
        "status": "PASS",
        "build_status": "PASS",
        "family": "rust",
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "source_sha256": HISTORICAL_V13_BUILD[0].sha256,
        "protocol_sha256": HISTORICAL_V13_BUILD[1].sha256,
        "contract_sha256": HISTORICAL_V13_BUILD[2].sha256,
        "archive_relative": (
            "oracle/phase2/evidence/"
            "native-source-build-v13-rust-"
            "phase2-v13-rust-pattern-repr-original-p0.json.gz"
        ),
        "archive_sha256":
            "c201c014f55a51454baab77d2148dc39d6024bae3273242d6eb1f1b43f419f6a",
        "archive_bytes": 108_985,
        "uncompressed_bytes": 760_477,
        "uncompressed_sha256":
            "7bf86cbaec1df17548a0989d03db896036a86b0671d32e82f12ce4c3fae630db",
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28,
        "bridge_derived_sha256": ACTUAL_BRIDGE_SHA256,
        "public_derived_sha256": CORRECTED_ADAPTER_SHA256,
        "bridge_overlay_apply_count": 2,
        "corrected_public_overlay_apply_count": 2,
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    for name, expected_value in expected.items():
        require(type(receipt.get(name)) is type(expected_value)
                and receipt[name] == expected_value,
                "reject a stale or forged historical V13 build: " + name)
    return {
        "status": "PASS",
        "historical_build_status": "PASS",
        "historical_unique_compiler_process_count": 28,
        "archive_reads": 0,
        "archive_decompressions": 0,
        "candidate_correctness": "NOT MEASURED",
    }



def authenticate_pickle_contract(document: Any) -> None:
    require(type(document) is dict
            and document.get("schema") == (
                "rebar-phase2-owned-rust-match-pickle-source-repair-v1-"
                "source-freeze"
            )
            and document.get("version") == 1
            and document.get("phase") == "CANDIDATES"
            and document.get("family") == FAMILY
            and document.get("source") == {
                "path": PICKLE_FEATURE[0].path,
                "sha256": PICKLE_FEATURE[0].sha256,
            }
            and document.get("protocol") == {
                "path": PICKLE_FEATURE[1].path,
                "sha256": PICKLE_FEATURE[1].sha256,
            },
            "bind the exact independently reviewed combined pickle source freeze")
    actual = document.get("candidate_variant")
    require(type(actual) is dict
            and actual.get("path") == COMBINED_VARIANT.path
            and actual.get("sha256") == COMBINED_VARIANT.sha256
            and actual.get("bytes") == COMBINED_VARIANT.size
            and actual.get("actual_corrected_bridge_sha256")
            == ACTUAL_BRIDGE_SHA256
            and actual.get("buffer_shape_origin_sha256")
            == BUFFER_VARIANT.sha256
            and actual.get("buffer_shape_origin_bytes")
            == BUFFER_VARIANT.size
            and actual.get("same_existing_rust_family") is True
            and actual.get("adds_candidate_family") is False
            and actual.get("includes_frozen_buffer_shape_repair") is True
            and actual.get("includes_owned_match_pickle_repair") is True
            and actual.get("custom_match_constructor_preserved") is True
            and actual.get("scanner_reconstructor_shared") is True
            and actual.get("signed_c_int_protocol_parser") == "PyLong_AsInt"
            and actual.get("new_serialization_regex_engine_count") == 0
            and actual.get("materialized") is True
            and actual.get("built") is False
            and actual.get("candidate_matching") == "NOT RUN"
            and actual.get("correctness") == "NOT MEASURED"
            and actual.get("runtime_no_delegation") == "NOT ESTABLISHED",
            "reject false matching, a substituted bridge, or a foreign regex engine")
    previous = document.get("previous_frozen_buffer_source_repair")
    require(type(previous) is dict
            and previous.get("source") == owner_document(BUFFER_FEATURE[0])
            and previous.get("protocol") == owner_document(BUFFER_FEATURE[1])
            and previous.get("contract") == owner_document(BUFFER_FEATURE[2])
            and previous.get("variant") == owner_document(BUFFER_VARIANT)
            and previous.get("same_existing_rust_family") is True
            and previous.get("candidate_matching") == "NOT RUN"
            and previous.get("repair_effect") == "NOT MEASURED",
            "authenticate the exact distinct historical four-owner buffer feature")
    v49 = document.get("current_v49_overview")
    require(type(v49) is dict
            and v49.get("version") == 49
            and v49.get("authenticated_evidence_owner_lower_bound") == 172
            and v49.get("authenticated_history_reference_lower_bound") == 177
            and v49.get("actual_rust_status") == "FAIL"
            and v49.get("actual_rust_semantic_mismatch_count") == 928
            and v49.get("actual_rust_verified_passing_case_count") == 8_965
            and v49.get("first_party_source_inventory_family_count") == 6
            and v49.get("qualified_candidate_count") == 0,
            "preserve the actual independently pushed V49 graph and failed Rust")
    failure = document.get("actual_v7_failure")
    require(type(failure) is dict
            and failure.get("candidate_status") == "FAIL"
            and failure.get("case_execution_denominator") == 31_237
            and failure.get("suite_count") == 13
            and failure.get("semantic_mismatch_count") == 928
            and failure.get("verified_passing_case_count") == 8_965
            and failure.get("distinct_worker_process_id_count") == 13
            and failure.get("infrastructure_failure_count") == 0
            and failure.get("verified_passing_cases_derived_by_subtraction")
            is False,
            "preserve the genuine full campaign without invented pickle results")
    pickle = document.get("owned_match_pickle_protocol")
    require(type(pickle) is dict
            and pickle.get("protocol_parser") == "PyLong_AsInt"
            and pickle.get("low_protocol_condition") == "signed C int below 2"
            and pickle.get("high_protocol_result") == "TypeError"
            and pickle.get("existing_scanner_reconstructor_reused") is True
            and pickle.get("native_custom_constructor_preserved") is True
            and pickle.get("copy_identity_preserved") is True
            and pickle.get("deepcopy_identity_preserved") is True
            and pickle.get("additional_regex_engine_imports") == 0
            and pickle.get("serialization_import_on_matching_hot_path") is False
            and pickle.get("candidate_matching") == "NOT RUN"
            and pickle.get("repair_effect") == "NOT MEASURED",
            "reject altered protocol behavior, added regex import, or invented pass")
    wall = document.get("phase_boundary")
    require(type(wall) is dict
            and wall.get("actual_archives_opened") == 0
            and wall.get("actual_archives_decompressed") == 0
            and wall.get("actual_candidate_workers_started") == 0
            and wall.get("actual_subprocesses_started") == 0
            and wall.get("actual_clock_samples") == 0
            and wall.get("actual_hidden_cases_read") == 0
            and wall.get("holdout") == "NOT OPENED"
            and wall.get("qualified_candidate_count") == 0
            and wall.get("source_variant_built") is False
            and wall.get("source_variant_candidate_matching") == "NOT RUN",
            "reject any V50 source feature that ran matching or crossed its wall")



def validate_public_graph(
    document: Any, *, version: int, label: str,
    expected_evidence_owner_lower_bound: int,
    expected_history_reference_lower_bound: int,
) -> None:
    require(type(document) is dict,
            "require a canonical immutable " + label + " graph")
    require(document.get("version") == version,
            "reject a stale or borrowed " + label + " overview")
    require(document.get("suite_count") == 13
            and document.get("private_waiver_count") == 13
            and document.get("original_cases_removed") == 0
            and document.get("additional_private_waivers") == 0
            and document.get("qualified_candidate_count") == 0,
            "preserve the exact complete frozen P0 obligations")
    require(document.get("authenticated_evidence_owner_lower_bound")
            == expected_evidence_owner_lower_bound
            and document.get("authenticated_history_reference_lower_bound")
            == expected_history_reference_lower_bound,
            "preserve genuine current lower bounds; never borrow stale 164/169")
    require(document.get("actual_rust_semantic_mismatch_count") == 928
            and document.get("actual_rust_verified_passing_case_count") == 8_965
            and document.get("actual_rust_infrastructure_failure_count") == 0
            and document.get("actual_rust_candidate_workers") == 13
            and document.get("actual_rust_candidate_qualified") is False,
            "preserve the genuine complete failed original Rust campaign")
    require(document.get("corrected_reference_status") == "PASS"
            and document.get("corrected_reference_actual_worker_count") == 2
            and document.get("corrected_reference_case_count_per_worker") == 6_912
            and document.get("corrected_reference_cache_cases_per_worker") == 96
            and document.get("corrected_reference_process_ids") == [81, 82]
            and document.get("corrected_reference_full_records_sha256")
            == "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
            and document.get("corrected_reference_cache_records_sha256")
            == "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
            "reject a stale, falsified, or incomplete two-process CPython oracle")
    require(document.get("actual_candidate_workers_started_by_graph") == 0
            and document.get("actual_compiler_processes_started_by_graph") == 0
            and document.get("actual_clock_samples_by_graph") == 0
            and document.get("hidden_cases_read") == 0
            and document.get("final_holdout_opened") is False
            and document.get("performance") == "NOT MEASURED"
            and document.get("memory") == "NOT MEASURED"
            and document.get("winner_selected") is False,
            "reject a graph that ran a candidate, hid losses, or opened the holdout")


def authenticate_buffer_contract(document: Any) -> None:
    require(type(document) is dict
            and document.get("schema") == (
                "rebar-phase2-owned-rust-buffer-shape-source-repair-v1-"
                "source-freeze"
            )
            and document.get("version") == 1
            and document.get("family") == FAMILY
            and document.get("phase") == "CANDIDATES"
            and document.get("source") == {
                "path": BUFFER_FEATURE[0].path,
                "sha256": BUFFER_FEATURE[0].sha256,
            }
            and document.get("protocol") == {
                "path": BUFFER_FEATURE[1].path,
                "sha256": BUFFER_FEATURE[1].sha256,
            },
            "bind only the actual independently frozen V49 buffer source")
    actual = document.get("candidate_variant")
    require(type(actual) is dict
            and actual.get("path") == BUFFER_VARIANT.path
            and actual.get("sha256") == BUFFER_VARIANT.sha256
            and actual.get("bytes") == BUFFER_VARIANT.size
            and actual.get("actual_corrected_bridge_sha256")
            == ACTUAL_BRIDGE_SHA256
            and actual.get("same_existing_rust_family") is True
            and actual.get("adds_candidate_family") is False
            and actual.get("materialized") is True
            and actual.get("built") is False
            and actual.get("candidate_matching") == "NOT RUN"
            and actual.get("correctness") == "NOT MEASURED",
            "reject a substituted or falsely tested first-party buffer variant")
    failure = document.get("actual_v7_failure")
    require(type(failure) is dict
            and failure.get("candidate_status") == "FAIL"
            and failure.get("case_execution_denominator") == 31_237
            and failure.get("suite_count") == 13
            and failure.get("semantic_mismatch_count") == 928
            and failure.get("verified_passing_case_count") == 8_965
            and failure.get("distinct_worker_process_id_count") == 13
            and failure.get("infrastructure_failure_count") == 0
            and failure.get("verified_passing_cases_derived_by_subtraction")
            is False,
            "reject invented historical Rust passes or stale feature evidence")
    wall = document.get("phase_boundary")
    require(type(wall) is dict
            and wall.get("actual_archives_opened") == 0
            and wall.get("actual_archives_decompressed") == 0
            and wall.get("actual_candidate_workers_started") == 0
            and wall.get("actual_subprocesses_started") == 0
            and wall.get("actual_clock_samples") == 0
            and wall.get("actual_hidden_cases_read") == 0
            and wall.get("holdout") == "NOT OPENED"
            and wall.get("qualified_candidate_count") == 0
            and wall.get("source_variant_built") is False
            and wall.get("source_variant_candidate_matching") == "NOT RUN",
            "reject a V49 feature that violated its frozen source-only boundary")


def authenticate_phase_one(matrix: Any) -> None:
    require(type(matrix) is dict
            and matrix.get("schema") == "rebar-cpython-re-p0-completeness-v1",
            "authenticate the original complete P0 correctness matrix")
    denominator = matrix.get("denominator")
    require(type(denominator) is dict
            and denominator.get("final_required_case_execution_denominator")
            == 31_237
            and denominator.get("frozen_planned_case_execution_denominator")
            == 31_237
            and denominator.get("private_upstream_methods_outside_public_denominator")
            == 13
            and type(denominator.get("counted_suite_ids")) is list
            and len(denominator["counted_suite_ids"]) == 13,
            "preserve all 31,237 original cases and exactly 13 private waivers")


def verify_frozen_context(
    source_pin: str, protocol_pin: str, contract_pin: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    source_pin = checked_sha256(source_pin, "V16 source")
    protocol_pin = checked_sha256(protocol_pin, "V16 protocol")
    contract_pin = checked_sha256(contract_pin, "V16 machine contract")
    source_size = os.stat(
        ROOT / SOURCE_PATH, follow_symlinks=False,
    ).st_size
    protocol_size = os.stat(
        ROOT / PROTOCOL_PATH, follow_symlinks=False,
    ).st_size
    require(0 < source_size <= MAX_SOURCE_BYTES
            and 0 < protocol_size <= MAX_SOURCE_BYTES,
            "bound the independently caller-pinned V16 source and protocol")
    expected = canonical(contract_document(source_pin, protocol_pin))
    require(digest(expected) == contract_pin,
            "independently pin the canonical complete V16 machine contract")
    own = (
        Owner(SOURCE_PATH, source_pin, source_size),
        Owner(PROTOCOL_PATH, protocol_pin, protocol_size),
        Owner(CONTRACT_PATH, contract_pin, len(expected)),
    )
    groups = (
        own,
        (GOAL, PHASE_ONE),
        tuple(RUST_OWNERS),
        tuple(REFERENCE_SOURCE),
        (REFERENCE_RECEIPT,),
        tuple(HISTORICAL_BRIDGE_REPAIR),
        tuple(HISTORICAL_ADAPTER_REPAIR),
        tuple(LOW_LEVEL_V7),
        tuple(LOW_LEVEL_V9),
        tuple(HISTORICAL_V13_BUILD),
        (HISTORICAL_V13_BUILD_RECEIPT,),
        tuple(HISTORICAL_RUST_CAMPAIGN),
        (HISTORICAL_RUST_RECEIPT,),
        tuple(HISTORICAL_V48_GRAPH),
        tuple(BUFFER_FEATURE),
        (BUFFER_VARIANT,),
        tuple(PICKLE_FEATURE),
        (COMBINED_VARIANT,),
        tuple(BUFFER_GRAPH),
        tuple(FINAL_GRAPH),
    )
    content: dict[str, bytes] = {}
    evidence: dict[str, dict[str, Any]] = {}
    for group in groups:
        for item in group:
            previous = content.get(item.path)
            raw, observed = read_owner(item)
            if previous is not None:
                require(previous == raw,
                        "reject inconsistent repeated frozen owner identity")
            content[item.path] = raw
            evidence[item.path] = observed
    require(content[CONTRACT_PATH] == expected
            and strict_json(content[CONTRACT_PATH], "V16 frozen contract")
            == contract_document(source_pin, protocol_pin),
            "authenticate the exact independently generated V16 contract")
    validate_owner_ast(content[SOURCE_PATH], own[0], (
        "contract_document", "source_self_test", "verify_frozen_context",
        "run_build", "copy_combined_snapshot",
    ))
    authenticate_phase_one(
        strict_json(content[PHASE_ONE.path], "original P0 completeness matrix")
    )
    reference_contract = strict_json(
        content[REFERENCE_SOURCE[2].path],
        "corrected original two-reference source freeze",
    )
    require(reference_contract.get("source", {}).get("sha256")
            == REFERENCE_SOURCE[0].sha256
            and reference_contract.get("protocol", {}).get("sha256")
            == REFERENCE_SOURCE[1].sha256,
            "preserve both independent corrected reference source owners")
    reference = authenticate_corrected_reference(strict_json(
        content[REFERENCE_RECEIPT.path],
        "corrected independently durable Python reference receipt",
    ))
    historical_rust = authenticate_historical_rust_matching(strict_json(
        content[HISTORICAL_RUST_RECEIPT.path],
        "complete historical Rust matching receipt",
    ))
    previous_build = authenticate_historical_v13_build(strict_json(
        content[HISTORICAL_V13_BUILD_RECEIPT.path],
        "genuine previous V13 Rust dual-build receipt",
    ))
    validate_owner_ast(content[LOW_LEVEL_V9[0].path], LOW_LEVEL_V9[0], (
        "phase_paths", "prepare_private_phases", "install_v9_build_kernel",
        "record_native_forensics",
    ))
    validate_owner_ast(content[LOW_LEVEL_V7[0].path], LOW_LEVEL_V7[0], (
        "load_frozen_v4", "install_v7_build_kernel",
        "parse_owned_elf64", "compare_owned_elf64",
    ))
    validate_owner_ast(content[BUFFER_FEATURE[0].path], BUFFER_FEATURE[0], (
        "byte_assignments", "corrected_bridge", "corrected_adapter",
        "derive_variant",
    ))
    validate_owner_ast(content[PICKLE_FEATURE[0].path], PICKLE_FEATURE[0], (
        "derive_variant",
    ))
    for graph, version, owner_lower_bound, reference_lower_bound, name in (
        (HISTORICAL_V48_GRAPH, 48, 168, 173,
         "historical actual Rust V48"),
        (BUFFER_GRAPH, BUFFER_GRAPH_VERSION, 172, 177,
         "pushed buffer-feature graph"),
        (FINAL_GRAPH, FINAL_GRAPH_VERSION,
         CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
         CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
         "pushed combined-feature graph"),
    ):
        summary = strict_json(
            content[graph[2].path],
            name + " canonical public summary",
        )
        inputs = strict_json(
            content[graph[1].path],
            name + " canonical public graph inputs",
        )
        validate_public_graph(
            summary, version=version, label=name,
            expected_evidence_owner_lower_bound=owner_lower_bound,
            expected_history_reference_lower_bound=reference_lower_bound,
        )
        require(type(inputs) is dict
                and inputs.get("version") == version
                and inputs.get("suite_count") == 13
                and inputs.get("actual_rust_semantic_mismatch_count") == 928
                and inputs.get("actual_rust_verified_passing_case_count") == 8_965
                and inputs.get("qualified_candidate_count") == 0
                and inputs.get("authenticated_evidence_owner_lower_bound")
                == owner_lower_bound
                and inputs.get("authenticated_history_reference_lower_bound")
                == reference_lower_bound,
                "reject missing or changed " + name + " overview inputs")
    buffer_contract = strict_json(
        content[BUFFER_FEATURE[2].path],
        "pushed V49 first-party buffer feature contract",
    )
    pickle_contract = strict_json(
        content[PICKLE_FEATURE[2].path],
        "pushed V50 combined first-party feature contract",
    )
    authenticate_buffer_contract(buffer_contract)
    authenticate_pickle_contract(pickle_contract)

    originals = {
        item.path: content[item.path]
        for item in RUST_OWNERS
    }
    rust_package = validate_rust_package(originals)
    actual_bridge = corrected_bridge(
        originals[BRIDGE_PATH],
        content[HISTORICAL_BRIDGE_REPAIR[0].path],
    )
    adapter = corrected_adapter(
        originals[PUBLIC_PATH],
        content[HISTORICAL_ADAPTER_REPAIR[0].path],
    )
    require(digest(actual_bridge) == ACTUAL_BRIDGE_SHA256
            and len(actual_bridge) == ACTUAL_BRIDGE_BYTES
            and digest(adapter) == CORRECTED_ADAPTER_SHA256
            and len(adapter) == CORRECTED_ADAPTER_BYTES,
            "derive both exact historical corrected Rust sources by bounded AST")
    buffer = derive_buffer_variant(
        actual_bridge,
        content[BUFFER_FEATURE[0].path],
    )
    require(buffer == content[BUFFER_VARIANT.path]
            and len(buffer) == BUFFER_VARIANT.size
            and digest(buffer) == BUFFER_VARIANT.sha256,
            "reproduce every reviewed V49 buffer-variant byte")
    combined = derive_combined_variant(
        buffer,
        content[PICKLE_FEATURE[0].path],
    )
    require(combined == content[COMBINED_VARIANT.path]
            and len(combined) == COMBINED_VARIANT.size
            and digest(combined) == COMBINED_VARIANT.sha256,
            "reproduce every reviewed final V50 combined-variant byte")
    for forbidden in (
        b"import re\n",
        b"from re import",
        b"import _sre",
        b"from _sre",
        b"regex.compile",
        b"pcre",
        b"oniguruma",
        b"candidates.vm_candidate",
        b"candidates.zig_candidate",
        b"candidates.cpp_candidate",
        b"candidates.go_candidate",
        b"candidates.fortran_candidate",
    ):
        require(combined.count(forbidden) == actual_bridge.count(forbidden)
                and adapter.count(forbidden) == originals[PUBLIC_PATH].count(forbidden),
                "reject an external, delegated, or cross-family regex source")
    tools = [read_toolchain(item) for item in TOOLCHAIN]
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "version": VERSION,
        "source": evidence[SOURCE_PATH],
        "protocol": evidence[PROTOCOL_PATH],
        "contract": evidence[CONTRACT_PATH],
        "read_only": True,
        "family": FAMILY,
        "frozen_correctness": {
            "status": "PASS",
            "suite_count": 13,
            "case_execution_denominator": 31_237,
            "named_private_waiver_count": 13,
            "matrix_sha256": PHASE_ONE.sha256,
        },
        "history": current_history(),
        "corrected_python_reference": reference,
        "last_actual_rust_matching": historical_rust,
        "historical_v13_rust_build": previous_build,
        "source_family_count": 6,
        "rust_family_count": 1,
        "source_owner_count": 25,
        "rust_source_owner_count": 9,
        "rust_package": rust_package,
        "source_feature_count": 2,
        "source_features": {
            "buffer": {
                "source": evidence[BUFFER_FEATURE[0].path],
                "protocol": evidence[BUFFER_FEATURE[1].path],
                "contract": evidence[BUFFER_FEATURE[2].path],
                "variant": evidence[BUFFER_VARIANT.path],
            },
            "combined_buffer_and_pickle": {
                "source": evidence[PICKLE_FEATURE[0].path],
                "protocol": evidence[PICKLE_FEATURE[1].path],
                "contract": evidence[PICKLE_FEATURE[2].path],
                "variant": evidence[COMBINED_VARIANT.path],
            },
        },
        "preserved_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "preserved_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "historical_bridge_sha256": ACTUAL_BRIDGE_SHA256,
        "historical_bridge_bytes": ACTUAL_BRIDGE_BYTES,
        "buffer_variant_sha256": BUFFER_VARIANT.sha256,
        "buffer_variant_bytes": BUFFER_VARIANT.size,
        "combined_variant_sha256": COMBINED_VARIANT.sha256,
        "combined_variant_bytes": COMBINED_VARIANT.size,
        "toolchain": tools,
        "expected_future_phase_count": 2,
        "expected_future_process_count": 28,
        "historical_v48_graph_verified": True,
        "buffer_graph_version": BUFFER_GRAPH_VERSION,
        "current_graph_version": FINAL_GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "authenticated_history_reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "candidate_variant_built": False,
        **phase_boundary(),
    }
    state = {
        "originals": originals,
        "combined_bridge": combined,
        "corrected_adapter": adapter,
        "low_level_v9_source": content[LOW_LEVEL_V9[0].path],
    }
    return result, state



def source_self_test(source_pin: str, protocol_pin: str,
                     contract_pin: str) -> dict[str, Any]:
    frozen = contract_document(source_pin, protocol_pin)
    require(digest(canonical(frozen))
            == checked_sha256(contract_pin, "V16 canonical source contract"),
            "reject an altered independently pinned source-freeze contract")
    plan = synthetic_plan()
    rejected: list[str] = []
    accepted: list[str] = []

    def reject(label: str, action: Any) -> None:
        try:
            action()
        except (GateError, ForbiddenEffect):
            rejected.append(label)
            return
        except (TypeError, ValueError, KeyError, IndexError, OSError):
            rejected.append(label)
            return
        raise GateError("accepted a hostile V16 synthetic source control: " + label)

    def changed(label: str, update: Any) -> None:
        def check() -> None:
            variant = copy.deepcopy(plan)
            update(variant)
            validate_synthetic_plan(variant)
        reject(label, check)

    with SourceOnlyWall() as wall:
        result = validate_synthetic_plan(plan)
        require(result.get("status") == "PASS"
                and result.get("independent_phase_count") == 2
                and result.get("distinct_source_inode_count") == 18
                and result.get("distinct_native_output_inode_count") == 4
                and result.get("distinct_process_count") == 28,
                "close the complete synthetic first-party Rust build denominator")
        accepted.append("complete-independent-two-phase-nine-owner-plan")
        for field, hostile in (
            ("schema", "rebar-phase2-owned-stale-build"),
            ("family", "zig"),
            ("root_prefix", "rebar-phase2-native-build-v16-rust-"),
            ("graph_version", 48),
            ("historical_rust_candidate_status", "PASS"),
            ("historical_rust_semantic_mismatch_count", 0),
            ("historical_rust_verified_passing_case_count", 31_237 - 928),
            ("corrected_reference_process_ids", [81, 81]),
            ("original_suite_count", 12),
            ("original_case_execution_denominator", 31_236),
            ("original_named_private_waiver_count", 14),
            ("evidence_owner_lower_bound", 164),
            ("reference_lower_bound", 169),
            ("buffer_feature_sha256", "0" * 64),
            ("buffer_variant_sha256", "0" * 64),
            ("pickle_feature_sha256", "0" * 64),
            ("combined_variant_sha256", "0" * 64),
            ("corrected_adapter_sha256", "0" * 64),
            ("cargo_external_dependency_count", 1),
            ("candidate_workers_started", 1),
            ("clock_samples", 1),
            ("matching_archive_reads", 1),
            ("mutable_document_reads", 1),
            ("native_libraries_loaded", 1),
            ("network_requests", 1),
            ("holdout", "OPENED"),
            ("candidate_qualified", True),
            ("winner_selected", True),
        ):
            changed("reject-" + field,
                    lambda candidate, name=field, value=hostile:
                    candidate.__setitem__(name, value))
        for index in range(2):
            changed("reject-phase-name-" + str(index),
                    lambda candidate, at=index:
                    candidate["phases"][at].__setitem__("name", "borrowed"))
            changed("reject-phase-mode-" + str(index),
                    lambda candidate, at=index:
                    candidate["phases"][at].__setitem__("directory_mode", 0o755))
            for original in RUST_OWNERS:
                for field, hostile in (
                    ("sha256", "0" * 64),
                    ("bytes", 0),
                    ("mode", 0o644),
                    ("nlink", 2),
                    ("overlay_count", 2),
                ):
                    changed(
                        "reject-phase-" + str(index) + "-"
                        + original.path + "-" + field,
                        lambda candidate, at=index, path=original.path,
                               key=field, value=hostile:
                        candidate["phases"][at]["fresh_source_owners"][path]
                        .__setitem__(key, value),
                    )
            for role in ("engine", "bridge"):
                for field, hostile in (
                    ("file_name", "foreign_regex.so"),
                    ("sha256", "0" * 64),
                    ("size_bytes", 0),
                    ("inode", 0),
                ):
                    changed(
                        "reject-native-" + str(index) + "-" + role + "-" + field,
                        lambda candidate, at=index, kind=role,
                               key=field, value=hostile:
                        candidate["phases"][at]["native_outputs"][kind]
                        .__setitem__(key, value),
                    )
        changed(
            "reject-reused-phase-directory-inode",
            lambda candidate:
            candidate["phases"][1].__setitem__(
                "directory_inode",
                candidate["phases"][0]["directory_inode"],
            ),
        )
        changed(
            "reject-reused-source-inode",
            lambda candidate:
            candidate["phases"][1]["fresh_source_owners"][RUST_OWNERS[0].path]
            .__setitem__(
                "inode",
                candidate["phases"][0]["fresh_source_owners"][RUST_OWNERS[0].path]
                ["inode"],
            ),
        )
        changed(
            "reject-reused-native-inode",
            lambda candidate:
            candidate["phases"][1]["native_outputs"]["engine"].__setitem__(
                "inode",
                candidate["phases"][0]["native_outputs"]["engine"]["inode"],
            ),
        )
        for index in range(2 * len(PROCESS_NAMES)):
            for field, hostile in (
                ("name", "build_external_regex"),
                ("phase", "reference-c"),
                ("exit_status", 1),
                ("pid", 0),
            ):
                changed(
                    "reject-process-" + str(index) + "-" + field,
                    lambda candidate, at=index, key=field, value=hostile:
                    candidate["processes"][at].__setitem__(key, value),
                )
        changed(
            "reject-reused-process-id",
            lambda candidate:
            candidate["processes"][1].__setitem__(
                "pid", candidate["processes"][0]["pid"],
            ),
        )
        probes: tuple[tuple[str, Any], ...] = (
            ("filesystem", lambda: os.stat(str(ROOT))),
            ("write", lambda: os.mkdir("forbidden-v16-source-freeze")),
            ("process", lambda: subprocess.run(("forbidden-v16-build",))),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("native", lambda: ctypes.CDLL("forbidden-v16-native.so")),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)),
            ("gzip", lambda: gzip.decompress(b"forbidden")),
            ("zlib", lambda: zlib.decompress(b"forbidden")),
        )
        for name, operation in probes:
            reject("physically-block-" + name, operation)
        require(sum(wall.blocked.values()) == len(probes),
                "physically block every attempted source-only effect")
        require(all(wall.blocked[name] >= 1 for name in (
            "filesystem", "write", "process", "import", "network",
            "thread", "clock", "native", "lock", "signal", "decompression",
        )), "exercise every filesystem, native, archive, clock, and process wall")
        require(len(rejected) >= 245,
                "exercise the complete hostile owner, history, process, and effect matrix")
        result = {
            "schema": SCHEMA + "-source-only-self-test",
            "status": "PASS",
            "version": VERSION,
            "source_sha256": source_pin,
            "protocol_sha256": protocol_pin,
            "contract_sha256": contract_pin,
            "accepted_positive_controls": accepted,
            "rejected_hostile_controls": len(rejected),
            "blocked_effect_attempts": dict(wall.blocked),
            "synthetic_evidence": result,
            "current_history": current_history(),
            **phase_boundary(),
            "read_only": True,
        }
    return result



_ACTIVE: dict[str, Any] | None = None
_APPLIED_PHASES: set[tuple[str, str]] = set()


def copy_combined_snapshot(workdir: str, family: str, phase: str,
                           originals: dict[str, bytes]
                           ) -> dict[str, dict[str, Any]]:
    require(_ACTIVE is not None,
            "require an explicitly pinned and authorized V16 native build")
    state = _ACTIVE
    kernel = state["kernel"]
    v9 = state["v9"]
    checked_workdir(workdir)
    expected_paths = {item.path for item in RUST_OWNERS}
    require(family == FAMILY and phase in PHASES
            and type(originals) is dict and set(originals) == expected_paths
            and (workdir, phase) not in _APPLIED_PHASES,
            "require a unique phase containing all nine original Rust source owners")
    paths = v9.phase_paths(workdir, family, phase)
    for peer in PHASES:
        peer_paths = v9.phase_paths(workdir, family, peer)
        for folder in (
            peer_paths["base"],
            peer_paths["source"],
            peer_paths["source"] / "candidates",
            peer_paths["source"] / "candidates/rust",
        ):
            observed = os.lstat(folder)
            require(stat.S_ISDIR(observed.st_mode)
                    and stat.S_IMODE(observed.st_mode) == 0o700
                    and observed.st_uid == os.geteuid(),
                    "precreate both genuinely owner-only independent Rust phases")
    for item in RUST_OWNERS:
        value = originals.get(item.path)
        require(type(value) is bytes
                and len(value) == item.size and digest(value) == item.sha256,
                "reject an altered canonical Rust source: " + item.path)

    rows: dict[str, dict[str, Any]] = {}
    for item in sorted(RUST_OWNERS, key=lambda owner: owner.path):
        if item.path in (BRIDGE_PATH, PUBLIC_PATH):
            continue
        destination = paths["source"] / item.path
        kernel.mkdir_private(destination.parent)
        recorded = kernel.write_fresh(destination, originals[item.path],
                                      synchronize=False)
        recorded["path"] = v9.sanitized(recorded["path"], workdir, family)
        rows[item.path] = recorded
    require(len(rows) == 7,
            "preserve all seven unchanged original non-overlay Rust owners")

    for path, payload, expected_hash, expected_size, source_role in (
        (
            BRIDGE_PATH,
            state["combined_bridge"],
            COMBINED_VARIANT.sha256,
            COMBINED_VARIANT.size,
            "combined-buffer-shape-and-pickle-bridge",
        ),
        (
            PUBLIC_PATH,
            state["corrected_adapter"],
            CORRECTED_ADAPTER_SHA256,
            CORRECTED_ADAPTER_BYTES,
            "historically-corrected-public-adapter",
        ),
    ):
        require(type(payload) is bytes
                and len(payload) == expected_size
                and digest(payload) == expected_hash,
                "require the complete reviewed first-party private overlay")
        destination = paths["source"] / path
        kernel.mkdir_private(destination.parent)
        published = kernel.write_fresh(destination, payload, synchronize=True)
        observed, checked = kernel.authenticate_file(
            destination,
            expected=expected_hash,
            maximum=MAX_SOURCE_BYTES,
            exact_size=expected_size,
            capture=True,
        )
        require(type(checked) is bytes and checked == payload
                and published["sha256"] == expected_hash
                and published["bytes"] == expected_size
                and published["device"] == observed["device"]
                and published["inode"] == observed["inode"]
                and stat.S_IMODE(os.lstat(destination).st_mode) == 0o600,
                "authenticate an exclusive no-follow private overlay inode")
        rows[path] = {
            "path": v9.sanitized(observed["path"], workdir, family),
            "sha256": observed["sha256"],
            "bytes": observed["size_bytes"],
            "device": observed["device"],
            "inode": observed["inode"],
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "source_overlay": {
                "status": "PASS",
                "phase": phase,
                "role": source_role,
                "source_apply_count": 1,
                "derived_sha256": expected_hash,
                "derived_source_sha256": expected_hash,
                "derived_bytes": expected_size,
                "derived_source_bytes": expected_size,
                "candidate_original_modified": False,
                "canonical_candidate_modified": False,
            },
        }
    require(set(rows) == expected_paths,
            "close the exact seven-original, two-overlay first-party phase")
    for item in RUST_OWNERS:
        read_owner(item)
    _APPLIED_PHASES.add((workdir, phase))
    return rows


def verify_reproduced_phases(v9: types.ModuleType, v7: types.ModuleType,
                             workdir: str, phases: list[dict[str, Any]],
                             steps: list[dict[str, Any]]) -> dict[str, Any]:
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases] == list(PHASES)
            and type(steps) is list
            and len(steps) == 2 * len(PROCESS_NAMES),
            "require two actually completed ordered 14-process Rust phases")
    identities: set[tuple[int, int]] = set()
    expected_paths = {item.path for item in RUST_OWNERS}
    for index, phase in enumerate(phases):
        rows = phase.get("fresh_source_owners")
        require(type(rows) is dict and set(rows) == expected_paths,
                "require all nine independently owned private Rust sources")
        for item in RUST_OWNERS:
            expected_hash, expected_size = expected_source_owner(item.path)
            actual = rows.get(item.path)
            require(type(actual) is dict
                    and actual.get("sha256") == expected_hash
                    and actual.get("bytes") == expected_size
                    and type(actual.get("device")) is int
                    and type(actual.get("inode")) is int
                    and (actual["device"], actual["inode"]) not in identities,
                    "reject missing, shared, or altered private Rust source")
            identities.add((actual["device"], actual["inode"]))
        for path in (BRIDGE_PATH, PUBLIC_PATH):
            overlay = rows[path].get("source_overlay")
            expected_hash, expected_size = expected_source_owner(path)
            require(type(overlay) is dict and overlay.get("status") == "PASS"
                    and overlay.get("phase") == PHASES[index]
                    and overlay.get("source_apply_count") == 1
                    and overlay.get("derived_sha256") == expected_hash
                    and overlay.get("derived_bytes") == expected_size,
                    "require both genuinely applied reviewed private overlays")
    process_ids: set[int] = set()
    for index, operation in enumerate(steps):
        require(type(operation) is dict
                and operation.get("name")
                == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and type(operation.get("pid")) is int
                and operation["pid"] > 0
                and operation["pid"] not in process_ids
                and operation.get("exit_status") == 0,
                "require 28 distinct genuine successful compiler/ELF processes")
        process_ids.add(operation["pid"])
    results: dict[str, dict[str, Any]] = {}
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
                "reject a borrowed or nonreproducible native output")
        first = v9._RAW_PHASE_ELF.get((workdir, PHASES[0], role))
        second = v9._RAW_PHASE_ELF.get((workdir, PHASES[1], role))
        require(type(first) is bytes and type(second) is bytes
                and digest(first) == left["sha256"]
                and digest(second) == right["sha256"] and first == second,
                "compare both complete independent authenticated Rust ELF files")
        report = v7.compare_owned_elf64(first, second)
        require(type(report) is dict and report.get("byte_identical") is True,
                "prove complete independently reproduced native ELF bytes")
        comparisons[role] = report
        results[role] = {
            "file_name": filename,
            "sha256": left["sha256"],
            "size_bytes": left["size_bytes"],
            "fresh_independent_inode_count": 2,
            "reproduced_in_two_fresh_directories": True,
            "audit": left["audit"],
        }
    for item in RUST_OWNERS:
        read_owner(item)
    return {
        "status": "PASS",
        "family": FAMILY,
        "independent_fresh_phase_count": 2,
        "source_owners_per_phase": 9,
        "unchanged_source_owners_per_phase": 7,
        "combined_bridge_overlay_count": 2,
        "corrected_public_adapter_overlay_count": 2,
        "buffer_feature_source_sha256": BUFFER_FEATURE[0].sha256,
        "pickle_feature_source_sha256": PICKLE_FEATURE[0].sha256,
        "combined_bridge_sha256": COMBINED_VARIANT.sha256,
        "combined_bridge_bytes": COMBINED_VARIANT.size,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "byte_identical": True,
        "unique_process_count": len(process_ids),
        "native_role_count": 2,
        "raw_elf_comparisons": comparisons,
        "native_outputs": results,
        "prebuilt_artifact_count": 0,
        "native_libraries_loaded": 0,
        "original_sources_modified": False,
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(type(failed) is bool,
            "select an actual, independently preserved V16 build outcome")
    base = "native-source-build-v16-rust-" + checked_label(label)
    if failed:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def publish_build_report(kernel: types.ModuleType,
                         report: dict[str, Any]) -> dict[str, Any]:
    require(type(report) is dict and report.get("status") in ("PASS", "FAIL"),
            "publish only an actual authorized successful or failed V16 build")
    label = checked_label(report.get("label"))
    archive_name, receipt_name = evidence_names(
        label, report["status"] == "FAIL",
    )
    directory = ROOT / EVIDENCE_PATH
    plain = canonical(report)
    require(0 < len(plain) <= MAX_REPORT_BYTES,
            "bound every complete actual combined first-party build report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_REPORT_BYTES,
            "bound one deterministic combined-build archive")
    saved = kernel.write_fresh(directory / archive_name, archive,
                               synchronize=True)
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": report["status"],
        "family": FAMILY,
        "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": saved["sha256"],
        "archive_bytes": saved["bytes"],
        "archive_publication": saved,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "current_graph_version": FINAL_GRAPH_VERSION,
        "prepublication_evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "prepublication_history_reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "later_append_only_evidence_allowed": True,
        "new_actual_evidence_owner_count": 2,
        "evidence_owner_lower_bound_after_publication": CURRENT_EVIDENCE_OWNER_LOWER_BOUND + 2,
        "history_reference_lower_bound_after_publication": CURRENT_HISTORY_REFERENCE_LOWER_BOUND + 2,
        "global_evidence_owner_census": "NOT MEASURED",
        "global_history_reference_census": "NOT MEASURED",
        "historical_actual_rust_matching_status": "FAIL",
        "historical_actual_rust_mismatch_count": 928,
        "historical_actual_rust_verified_passing_case_count": 8_965,
        "historical_actual_rust_candidate_workers": 13,
        "buffer_feature_source_sha256": BUFFER_FEATURE[0].sha256,
        "buffer_feature_protocol_sha256": BUFFER_FEATURE[1].sha256,
        "buffer_feature_contract_sha256": BUFFER_FEATURE[2].sha256,
        "buffer_variant_sha256": BUFFER_VARIANT.sha256,
        "pickle_feature_source_sha256": PICKLE_FEATURE[0].sha256,
        "pickle_feature_protocol_sha256": PICKLE_FEATURE[1].sha256,
        "pickle_feature_contract_sha256": PICKLE_FEATURE[2].sha256,
        "combined_bridge_sha256": COMBINED_VARIANT.sha256,
        "combined_bridge_bytes": COMBINED_VARIANT.size,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "combined_bridge_overlay_apply_count":
            report.get("combined_bridge_overlay_apply_count", 0),
        "corrected_public_adapter_overlay_apply_count":
            report.get("corrected_public_adapter_overlay_apply_count", 0),
        "expected_actual_compiler_process_count": 2 * len(PROCESS_NAMES),
        "actual_compiler_process_count":
            report.get("actual_compiler_process_count", 0),
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_processes_started": 0,
        "candidate_workers_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    payload = canonical(receipt)
    require(0 < len(payload) <= MAX_SOURCE_BYTES,
            "bound the complete separately durable actual V16 receipt")
    recorded = kernel.write_fresh(directory / receipt_name, payload,
                                  synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    return {
        "schema": SCHEMA + "-published-build",
        "status": report["status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": report["status"],
        "family": FAMILY,
        "label": label,
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": saved["sha256"],
        "receipt_relative": EVIDENCE_PATH + "/" + receipt_name,
        "receipt_sha256": recorded["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": report["status"] == "FAIL",
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def run_build(options: argparse.Namespace) -> dict[str, Any]:
    global _ACTIVE
    context, state = verify_frozen_context(
        options.source_sha256, options.protocol_sha256, options.contract_sha256,
    )
    original_pins = {item.path + "=" + item.sha256 for item in RUST_OWNERS}
    require(type(options.owned_source_sha256) is list
            and len(options.owned_source_sha256) == len(RUST_OWNERS)
            and set(options.owned_source_sha256) == original_pins,
            "independently caller-pin all nine original first-party Rust sources")
    require(options.combined_bridge_sha256 == COMBINED_VARIANT.sha256
            and options.combined_bridge_bytes == COMBINED_VARIANT.size
            and options.corrected_adapter_sha256 == CORRECTED_ADAPTER_SHA256
            and options.corrected_adapter_bytes == CORRECTED_ADAPTER_BYTES,
            "independently caller-pin both complete first-party private overlays")
    label = checked_label(options.label)
    require(_ACTIVE is None and not _APPLIED_PHASES,
            "reject a nested, reused, or cross-family actual V16 native build")

    v9 = load_frozen_module(
        "_rebar_v16_frozen_actual_low_level_v9",
        LOW_LEVEL_V9[0],
        state["low_level_v9_source"],
    )
    require(v9.SCHEMA == "rebar-phase2-owned-native-source-build-v9"
            and v9.FAMILY == FAMILY
            and v9.PHASES == PHASES
            and v9.PROCESS_NAMES == PROCESS_NAMES,
            "load only the exact first-party frozen Rust V9 low-level recorder")
    v7 = v9.load_frozen_module(
        "_rebar_v16_frozen_actual_low_level_v7", v9.V7_OWNERS["source"],
    )
    require(v7.SCHEMA == "rebar-phase2-owned-native-source-build-v7",
            "load only the exact first-party frozen V7 native build kernel")
    kernel = v7.load_frozen_v4()
    state["v9"] = v9
    state["v7"] = v7
    state["kernel"] = kernel
    _ACTIVE = state
    v9.install_v9_build_kernel(v7, kernel)
    kernel.copy_snapshot = copy_combined_snapshot
    for outcome in (False, True):
        for relative in evidence_names(label, outcome):
            kernel.require_fresh_absent(ROOT / EVIDENCE_PATH / relative)

    workdir = tempfile.mkdtemp(prefix=ROOT_PREFIX, dir="/tmp")
    checked_workdir(workdir)
    operations: list[dict[str, Any]] = []
    phases: list[dict[str, Any]] = []

    def make_report(status: str, *, reproduction: Any = None,
                    error: Exception | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema": SCHEMA + "-actual-combined-dual-source-build",
            "version": VERSION,
            "status": status,
            "family": FAMILY,
            "label": label,
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "contract_sha256": options.contract_sha256,
            "frozen_context": context,
            "root_prefix": ROOT_PREFIX,
            "graph_version": FINAL_GRAPH_VERSION,
            "prepublication_evidence_owner_lower_bound": CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
            "prepublication_history_reference_lower_bound": CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
            "historical_rust_matching_status": "FAIL",
            "historical_rust_mismatch_count": 928,
            "historical_rust_verified_passing_case_count": 8_965,
            "buffer_feature_source_sha256": BUFFER_FEATURE[0].sha256,
            "buffer_variant_sha256": BUFFER_VARIANT.sha256,
            "pickle_feature_source_sha256": PICKLE_FEATURE[0].sha256,
            "combined_bridge_sha256": COMBINED_VARIANT.sha256,
            "combined_bridge_bytes": COMBINED_VARIANT.size,
            "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "combined_bridge_overlay_apply_count": len(_APPLIED_PHASES),
            "corrected_public_adapter_overlay_apply_count": len(_APPLIED_PHASES),
            "expected_actual_compiler_process_count": 2 * len(PROCESS_NAMES),
            "actual_compiler_process_count": len(operations),
            "phase_count": len(phases),
            "phases": phases,
            "compiler_processes": operations,
            "reproducibility": reproduction,
            "candidate_correctness": "NOT MEASURED",
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
            "candidate_processes_started": 0,
            "candidate_workers_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        if error is not None:
            result["error_type"] = type(error).__name__
            result["error_message"] = str(error)[:8_192]
        return result

    try:
        v9.prepare_private_phases(kernel, workdir)
        for phase in PHASES:
            completed = kernel.exact_build_phase(
                workdir, FAMILY, phase, state["originals"], operations,
            )
            completed["native_forensics"] = v9.record_native_forensics(
                v7, kernel, workdir, phase, completed, operations,
            )
            phases.append(completed)
        comparison = verify_reproduced_phases(
            v9, v7, workdir, phases, operations,
        )
        require(comparison.get("status") == "PASS"
                and comparison.get("unique_process_count") == 28
                and comparison.get("combined_bridge_overlay_count") == 2
                and comparison.get("corrected_public_adapter_overlay_count") == 2
                and len(_APPLIED_PHASES) == 2,
                "require the complete real first-party reproducibility proof")
        return publish_build_report(kernel, make_report(
            "PASS", reproduction=comparison,
        ))
    except Exception as error:
        for original in RUST_OWNERS:
            read_owner(original)
        return publish_build_report(kernel, make_report("FAIL", error=error))



def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    repeated = [
        value for value in values
        if value.startswith("--") and value != "--owned-source-sha256"
    ]
    require(len(repeated) == len(set(repeated)),
            "reject repeated or ambiguous V16 source-build authority")
    parser = argparse.ArgumentParser(
        description=__doc__, allow_abbrev=False,
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument(
        "--render-contract", "--emit-contract",
        dest="render_contract", action="store_true",
    )
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    parser.add_argument("--owned-source-sha256", action="append")
    parser.add_argument("--combined-bridge-sha256")
    parser.add_argument("--combined-bridge-bytes", type=int)
    parser.add_argument("--corrected-adapter-sha256")
    parser.add_argument("--corrected-adapter-bytes", type=int)
    options = parser.parse_args(values)
    checked_sha256(options.source_sha256, "V16 frozen source")
    checked_sha256(options.protocol_sha256, "V16 frozen protocol")
    authority = (
        options.label,
        options.owned_source_sha256,
        options.combined_bridge_sha256,
        options.combined_bridge_bytes,
        options.corrected_adapter_sha256,
        options.corrected_adapter_bytes,
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(value is None for value in authority),
                "canonical rendering can never authorize a build or candidate")
    else:
        checked_sha256(options.contract_sha256, "V16 canonical contract")
        if options.build:
            checked_label(options.label)
            checked_sha256(options.combined_bridge_sha256,
                           "final combined first-party C bridge")
            checked_sha256(options.corrected_adapter_sha256,
                           "historically corrected first-party Python adapter")
            require(type(options.combined_bridge_bytes) is int
                    and type(options.corrected_adapter_bytes) is int
                    and type(options.owned_source_sha256) is list
                    and len(options.owned_source_sha256) == len(RUST_OWNERS),
                    "explicitly pin both overlays and all nine original sources")
        else:
            require(all(value is None for value in authority),
                    "source-only gates can never activate a build, source, or run")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.render_contract:
            with SourceOnlyWall() as wall:
                result = contract_document(
                    options.source_sha256, options.protocol_sha256,
                )
                require(all(value == 0 for value in wall.blocked.values()),
                        "contract rendering attempted a forbidden source effect")
        elif options.self_test:
            result = source_self_test(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
        elif options.verify_frozen_context:
            result, _state = verify_frozen_context(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
        else:
            result = run_build(options)
        encoded = canonical(result)
        require(0 < len(encoded) <= MAX_REPORT_BYTES,
                "bound each complete authentic V16 gate result")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0 if options.render_contract or result.get("status", "PASS") == "PASS" else 1
    except (
        GateError, OSError, ValueError, UnicodeError, TypeError, KeyError,
        AttributeError, SyntaxError, RecursionError, subprocess.SubprocessError,
    ) as error:
        failure = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error)[:8_192],
            "actual_candidate_workers_started": 0,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "timing_trials_run": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(failure))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
