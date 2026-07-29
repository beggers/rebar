#!/usr/bin/env python3
"""Freeze, and separately authorize, the original first-party Rust V16 run.

Source and frozen-context modes never open a build archive, private build
directory, candidate, native library, clock, subprocess, or final holdout.
An actual run is a separately authorized operation with caller-pinned source,
build receipt, private root, native artifacts, and four-inode recovery.
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
import gzip
import hashlib
import importlib
import importlib.machinery
import io
import json
import locale
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
import traceback
import types
from typing import Any, Callable, Iterator, Mapping, NamedTuple, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SOURCE_PATH = "tools/run_owned_repaired_rust_original_campaign_v9.py"
PROTOCOL_PATH = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V9.md"
CONTRACT_PATH = "oracle/phase2/repaired-rust-original-campaign-v9.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v9"
CONTRACT_SCHEMA = SCHEMA + "-recoverable-source-freeze"
WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
FAMILY = "rust"
LABEL = "phase2-v16-rust-buffer-shape-pickle-original-p0-v9"
BUILD_LABEL = "phase2-v16-rust-buffer-shape-pickle"
EVIDENCE_PATH = "oracle/phase2/evidence"
PUBLIC_RECOVERY_ROOT = (
    "/tmp/rebar-phase2-repaired-rust-original-campaign-v9-"
    "phase2-v16-rust-buffer-shape-pickle-original-p0"
)
BUILD_ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
LOCK_NAME = "recoverable-controller-v9.lock"
ROLE_ORDER = ("bridge_source", "adapter", "engine", "bridge")
RESTORATION_ORDER = tuple(reversed(ROLE_ORDER))
PHASE_NAMES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols",
    "engine_sections", "engine_notes", "bridge_sections", "bridge_notes",
)
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_GRAPH_BYTES = 2 * 1024 * 1024
MAX_BUILD_ARCHIVE_BYTES = 2 * 1024 * 1024
MAX_BUILD_PLAIN_BYTES = 2 * 1024 * 1024
MAX_NATIVE_BYTES = 8 * 1024 * 1024
MAX_WORKER_STDOUT_BYTES = 32 * 1024 * 1024
MAX_WORKER_STDERR_BYTES = 4 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 8 * 3600
SUITE_COUNT = 13
CASE_COUNT = 31_237
PRIVATE_WAIVER_COUNT = 13
CURRENT_GRAPH_VERSION = 54
CURRENT_GRAPH_EVIDENCE_OWNER_LOWER_BOUND = 186
CURRENT_GRAPH_HISTORY_REFERENCE_LOWER_BOUND = 191
CURRENT_EVIDENCE_OWNER_LOWER_BOUND = 189
CURRENT_HISTORY_REFERENCE_LOWER_BOUND = 194
REFERENCE_RECORDS_SHA256 = (
    "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
)
REFERENCE_CACHE_RECORDS_SHA256 = (
    "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
)
REFERENCE_PIDS = (81, 82)
COMBINED_BRIDGE_SHA256 = (
    "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335"
)
COMBINED_BRIDGE_BYTES = 181_004
CORRECTED_ADAPTER_SHA256 = (
    "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
)
CORRECTED_ADAPTER_BYTES = 31_934
ENGINE_NAME = "_rust_engine.so"
BRIDGE_NAME = "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
VERIFIED_BUILD_PRIVATE_ROOT = "/tmp/rebar-phase2-native-build-v9-rust-4l03jkq2"
VERIFIED_BUILD_PRIVATE_ROOT_DEVICE = 2049
VERIFIED_BUILD_PRIVATE_ROOT_INODE = 11673028
VERIFIED_NATIVE_ENGINE_SHA256 = (
    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
)
VERIFIED_NATIVE_ENGINE_BYTES = 658344
VERIFIED_NATIVE_BRIDGE_SHA256 = (
    "324b811bfb3567d7f530d0a316a337897f84529defe83544e31ae34407b83e04"
)
VERIFIED_NATIVE_BRIDGE_BYTES = 148832


class Owner(NamedTuple):
    path: str
    sha256: str
    size: int
    device: int | None = None
    inode: int | None = None


GOAL = Owner("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = Owner("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
PRODUCER = (
    Owner("tools/run_owned_six_family_original_p0_producer_v4.py", "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782),
    Owner("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md", "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981),
    Owner("oracle/phase2/six-family-p0-producer-v4.json", "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867),
)
HISTORICAL_HELPER = (
    Owner("tools/run_owned_repaired_rust_original_campaign_v2.py", "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3", 143441),
    Owner("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V2.md", "9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0", 9342),
    Owner("oracle/phase2/repaired-rust-original-campaign-v2.json", "bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547", 15927),
)
HISTORICAL_CAMPAIGN = (
    Owner("tools/run_owned_repaired_rust_original_campaign_v7.py", "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104", 505616),
    Owner("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md", "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840", 8433),
    Owner("oracle/phase2/repaired-rust-original-campaign-v7.json", "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5", 46385),
)
HISTORICAL_RECEIPT = Owner(
    "oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures-publication-receipt.json",
    "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943", 8450,
)
CORRECTED_REFERENCE_RECEIPT = Owner(
    "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json",
    "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966", 2509,
)
BUFFER_FEATURE = (
    Owner("tools/apply_owned_rust_buffer_shape_source_repair_v1.py", "9c2a3642f2cda9fc85fd391baf4e0d57b25117f444d3a831592e8b62de3a627b", 64345),
    Owner("oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-REPAIR-V1.md", "67ba62acc8e51a6868404ea3faeb1aaaacb1d053cc1c915bef0c397edf5ac408", 5033),
    Owner("oracle/phase2/rust-buffer-shape-source-repair-v1.json", "ffa76d1724396fae5816cf96e0ae2104bcce8fc5eb246b8306d4441db0fe4a1b", 11454),
)
PICKLE_FEATURE = (
    Owner("tools/apply_owned_rust_match_pickle_source_repair_v1.py", "85383f4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517", 81784),
    Owner("oracle/phase2/RUST-MATCH-PICKLE-SOURCE-REPAIR-V1.md", "fad29fdcd3956ae99f9db40afae33b51eb99fb743baf89540a4ee7aafb7ac1af", 5105),
    Owner("oracle/phase2/rust-match-pickle-source-repair-v1.json", "5456535223cb029d41e8739696bde30b2b7127995fd0ef30286ff0488b1ed133", 15276),
)
BUILD = (
    Owner("tools/reproduce_owned_rust_buffer_shape_source_build_v16.py", "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a", 134640),
    Owner("oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md", "315f0a24e64b50804565f86c6ca4187024c4a1db5a23ab2f57c8805ed37f51f5", 6497),
    Owner("oracle/phase2/rust-buffer-shape-source-build-v16.json", "4f82f88da3329c6bacac2092af19d915d379f90101dcd9840366274355cc92b7", 18260),
)
BUILD_RECEIPT = Owner(
    "oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle-publication-receipt.json",
    "c893812a1796cce056de5e2feff2289df34ff816158685730205996549e338cb",
    3459, 2064, 524994,
)
BUILD_ARCHIVE = Owner(
    "oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle.json.gz",
    "c24c0e1544003b231bac3e45601faabfd1c1e5c181d89fce7d660a2df4a29270",
    109671, 2064, 524993,
)
BUILD_PLAIN_SHA256 = "c89af182cdb8e98dc05a4538e620c1db8404fbd7a11a3d43fea54f9da609f9c5"
BUILD_PLAIN_BYTES = 765382
V8_FAILURE = Owner(
    "oracle/phase2/evidence/repaired-rust-original-campaign-v8-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-entry-failure.json",
    "6a955d8ce361650395d1d7a4090a9bb1a6348b135143e2d65e63c8f5e196f9d0",
    4348, 2064, 525012,
)
V8_OBSERVATION = Owner(
    "oracle/phase2/evidence/repaired-rust-original-campaign-v8-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-entry-failure-observation.json",
    "76e476bd4d61dd0dc456c796953f024f98d6c581910ce9d30b6379f6ec8cac23",
    5739, 2064, 525013,
)

GRAPH = (
    Owner("tools/render_candidate_current_overview_v54.py", "d8fb850038ece0494cf6c85e324a8437b190dbcf606262ad640a25e4a94064ca", 73705),
    Owner("docs/evidence/candidate-current-overview-v54.inputs.json", "d64ea510aabf46d6fe904977ef170ea73bd9d3470226a4cad83876e2bb8af478", 627777),
    Owner("docs/evidence/candidate-current-overview-v54.json", "146ae2ed7fe6ba91f4c30e027e02d2ca8b9589c6d57e4bccc59da64fcd76a625", 1732575),
    Owner("docs/evidence/candidate-current-overview-v54.svg", "56aef3b0bbfc4602c65b6a968f778273e7e46f185e4090010c883ce2ba500728", 14034),
)
ORIGINALS: dict[str, dict[str, Any]] = {
    "bridge_source": {
        "relative": "candidates/rust/py_bridge.c",
        "sha256": "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        "bytes": 175676, "device": 2064, "inode": 419054,
        "mode": 0o600, "uid": 1000, "nlink": 1,
    },
    "adapter": {
        "relative": "candidates/rust_candidate.py",
        "sha256": "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        "bytes": 31151, "device": 2064, "inode": 428100,
        "mode": 0o600, "uid": 1000, "nlink": 1,
    },
    "engine": {
        "relative": "candidates/_rust_engine.so",
        "sha256": "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
        "bytes": 660440, "device": 2064, "inode": 430563,
        "mode": 0o755, "uid": 1000, "nlink": 1,
    },
    "bridge": {
        "relative": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
        "bytes": 144992, "device": 2064, "inode": 430629,
        "mode": 0o755, "uid": 1000, "nlink": 1,
    },
}
SOURCE_OWNERS = (
    ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    ("candidates/rust/py_bridge.c", COMBINED_BRIDGE_SHA256, COMBINED_BRIDGE_BYTES),
    ("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    ("candidates/rust_candidate.py", CORRECTED_ADAPTER_SHA256, CORRECTED_ADAPTER_BYTES),
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)


class CampaignError(Exception):
    """Reject a substituted owner, frozen route, or incomplete real run."""


class SourceOnlyViolation(CampaignError):
    """Reject a physically blocked effect in a source-only gate."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise CampaignError(message)


def checked_sha256(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(letter in "0123456789abcdef" for letter in value),
            "require one complete lowercase caller-pinned SHA-256: " + label)
    return value


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete bytes only")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False)
            + "\n").encode("ascii")


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw),
            "require complete frozen JSON bytes: " + label)

    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result,
                    "reject a repeated JSON owner key: " + label)
            result[key] = value
        return result

    def nonfinite(value: str) -> Any:
        raise CampaignError("reject a nonfinite JSON number: " + value)

    try:
        result = json.loads(raw, object_pairs_hook=unique,
                            parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise CampaignError("reject malformed frozen JSON: " + label) from error
    require(type(result) is dict, "require an exact JSON object: " + label)
    return result


def checked_relative(value: str) -> str:
    require(type(value) is str and 0 < len(value) <= 512
            and "\x00" not in value, "require a bounded relative owner")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value
            and all(part not in ("", ".", "..") for part in path.parts),
            "reject an escaped or noncanonical owner: " + value)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode
            and os.path.abspath(sys.executable) == PYTHON,
            "use only the exact isolated CPython 3.14.6 -I -B oracle")


def read_owner(owner: Owner, *, allow_archive: bool = False,
               private_root: str | None = None,
               maximum: int = MAX_SOURCE_BYTES) -> tuple[bytes, dict[str, Any]]:
    require(type(owner) is Owner,
            "read only a separately named, caller-authenticated owner")
    relative = checked_relative(owner.path)
    checked_sha256(owner.sha256, relative)
    require(type(owner.size) is int and 0 < owner.size <= maximum,
            "require exact bounded complete owner bytes: " + relative)
    if relative.endswith(".gz"):
        require(allow_archive and owner == BUILD_ARCHIVE,
                "source-only verification never opens a compressed archive")
    require(not relative.startswith("candidates/") or private_root is not None,
            "source-only verification never reads a canonical candidate")
    require("holdout" not in relative.lower()
            and "benchmark" not in relative.lower(),
            "never authenticate a final holdout or benchmark file")
    root = str(ROOT) if private_root is None else private_root
    require(type(root) is str and root.startswith("/")
            and root == root.rstrip("/") and "\x00" not in root,
            "require an exact absolute independently pinned owner root")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    dirs = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        parent = os.open(root, dirs)
        opened.append(parent)
        first_root = os.fstat(parent)
        require(stat.S_ISDIR(first_root.st_mode),
                "reject a redirected no-follow owner root")
        if private_root is not None:
            require(first_root.st_uid == os.geteuid()
                    and stat.S_IMODE(first_root.st_mode) == 0o700,
                    "reject a foreign or non-private build phase root")
        components = relative.split("/")
        for part in components[:-1]:
            parent = os.open(part, dirs, dir_fd=parent)
            opened.append(parent)
            observed = os.fstat(parent)
            require(stat.S_ISDIR(observed.st_mode),
                    "reject a substituted no-follow owner parent")
            if private_root is not None:
                require(observed.st_uid == os.geteuid()
                        and stat.S_IMODE(observed.st_mode) == 0o700,
                        "reject an exposed or foreign private phase parent")
        descriptor = os.open(components[-1], flags, dir_fd=parent)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        visible = os.stat(components[-1], dir_fd=parent,
                          follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode)
                and first.st_uid == os.geteuid()
                and first.st_nlink == 1 and first.st_size == owner.size
                and (first.st_dev, first.st_ino, first.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size),
                "reject a linked, foreign, truncated, or substituted owner: "
                + relative)
        if owner.device is not None:
            require(first.st_dev == owner.device,
                    "reject an exchanged durable owner device: " + relative)
        if owner.inode is not None:
            require(first.st_ino == owner.inode,
                    "reject an exchanged durable owner inode: " + relative)
        remaining = first.st_size
        chunks: list[bytes] = []
        checksum = hashlib.sha256()
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk),
                    "reject incomplete bounded owner bytes: " + relative)
            remaining -= len(chunk)
            checksum.update(chunk)
            chunks.append(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject appended bounded owner bytes: " + relative)
        last = os.fstat(descriptor)
        visible = os.stat(components[-1], dir_fd=parent,
                          follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns,
                 first.st_uid, first.st_nlink)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns,
                    last.st_uid, last.st_nlink)
                and (last.st_dev, last.st_ino, last.st_size,
                     last.st_nlink, last.st_uid)
                == (visible.st_dev, visible.st_ino, visible.st_size,
                    visible.st_nlink, visible.st_uid)
                and checksum.hexdigest() == owner.sha256,
                "reject owner replacement, TOCTOU, or digest: " + relative)
        raw = b"".join(chunks)
        return raw, {
            "path": root + "/" + relative, "relative": relative,
            "sha256": owner.sha256, "size_bytes": first.st_size,
            "device": first.st_dev, "inode": first.st_ino,
            "mode": stat.S_IMODE(first.st_mode),
            "uid": first.st_uid, "nlink": first.st_nlink,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def owner_document(owner: Owner) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": owner.path, "sha256": owner.sha256,
        "size_bytes": owner.size,
    }
    if owner.device is not None:
        result["device"] = owner.device
    if owner.inode is not None:
        result["inode"] = owner.inode
    return result


def source_zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_compiler_processes": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_library_loads": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "canonical_target_replacements": 0,
        "private_build_root_reads": 0,
        "private_build_root_enumerations": 0,
        "recovery_roots_created": 0,
        "recovery_locks_acquired": 0,
        "recovery_journals_created": 0,
        "v16_build_archive_reads": 0,
        "v16_build_archive_gzip_inflations": 0,
        "historical_build_archive_reads": 0,
        "historical_matching_archive_reads": 0,
        "reference_archive_reads": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "network_requests": 0,
        "threads_started": 0,
        "workspace_mutations": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    source_pin = checked_sha256(source_pin, "V9 source")
    protocol_pin = checked_sha256(protocol_pin, "V9 protocol")
    return {
        "schema": CONTRACT_SCHEMA,
        "status": "SOURCE FROZEN; CORRECTED RUST V16 CANDIDATE NOT RUN",
        "version": 9,
        "phase": "CANDIDATES",
        "family": FAMILY,
        "label": LABEL,
        "source": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "pinned_cpython": {
            "path": PYTHON, "sha256": PYTHON_SHA256,
            "version": "3.14.6", "isolated": True,
            "bytecode_writes": False,
        },
        "original_oracle": {
            "producer": [owner_document(item) for item in PRODUCER],
            "producer_version": 4, "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "additional_waivers": 0,
            "supplementary_cases_added_to_original_denominator": 0,
        },
        "corrected_python_reference": {
            "small_plaintext_receipt":
                owner_document(CORRECTED_REFERENCE_RECEIPT),
            "reference_process_ids": list(REFERENCE_PIDS),
            "public_type_cases_per_reference": 6912,
            "subclass_cache_cases_per_reference": 96,
            "full_reference_records_sha256": REFERENCE_RECORDS_SHA256,
            "cache_records_sha256": REFERENCE_CACHE_RECORDS_SHA256,
            "reference_archive_opened_by_source_gate": False,
        },
        "current_v54_graph": {
            "version": CURRENT_GRAPH_VERSION,
            "owners": [owner_document(item) for item in GRAPH],
            "authenticated_evidence_owner_lower_bound":
                CURRENT_GRAPH_EVIDENCE_OWNER_LOWER_BOUND,
            "authenticated_history_reference_lower_bound":
                CURRENT_GRAPH_HISTORY_REFERENCE_LOWER_BOUND,
            "global_owner_census": "NOT MEASURED",
        },
        "historical_actual_v8_pre_matching_failure": {
            "failure_owner": owner_document(V8_FAILURE),
            "independent_observation_owner": owner_document(V8_OBSERVATION),
            "controller_status": "FAIL",
            "failure_stage": "BUILD-PROCESS PREFLIGHT; NO MATCHING",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_workers": 0,
            "started_suite_count": 0,
            "completed_suite_count": 0,
            "native_activations": 0,
            "recovery_journals_created": 0,
            "target_replacements": 0,
            "historical_archive_reads_by_authorized_v8_controller": 1,
            "historical_archive_inflations_by_authorized_v8_controller": 1,
            "archive_reads_by_v9_source_gate": 0,
            "archive_inflations_by_v9_source_gate": 0,
            "root_cause": "V8 required an operation phase the authentic V16 build does not emit",
            "v9_fix": "derive each operation phase from its authenticated ordered index",
            "invented_phase_values": 0,
            "withdrawn_original_cases": 0,
            "additional_private_waivers": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        },
        "historical_rust_v7": {
            "owners": [owner_document(item) for item in HISTORICAL_CAMPAIGN],
            "small_plaintext_receipt": owner_document(HISTORICAL_RECEIPT),
            "candidate_status": "FAIL",
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "semantic_mismatch_count": 928,
            "explicitly_verified_passing_case_count": 8965,
            "passing_cases_derived_by_subtraction": False,
            "distinct_worker_process_count": 13,
            "infrastructure_failure_count": 0,
            "all_four_original_targets_restored": True,
            "individual_suite_histogram_present_in_small_receipt": False,
            "archive_opened_by_source_gate": False,
        },
        "first_party_combined_repairs": {
            "same_existing_rust_family": True,
            "new_candidate_family_count": 0,
            "buffer_feature_owners":
                [owner_document(item) for item in BUFFER_FEATURE],
            "pickle_feature_owners":
                [owner_document(item) for item in PICKLE_FEATURE],
            "combined_bridge_source_sha256": COMBINED_BRIDGE_SHA256,
            "combined_bridge_source_bytes": COMBINED_BRIDGE_BYTES,
            "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "corrected_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "canonical_candidate_source_read_by_source_gate": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_matching": "NOT RUN",
        },
        "actual_v16_reproducible_build": {
            "frozen_build_owners": [owner_document(item) for item in BUILD],
            "small_plaintext_receipt": owner_document(BUILD_RECEIPT),
            "archive_attested_by_receipt_only":
                owner_document(BUILD_ARCHIVE),
            "archive_uncompressed_sha256_attested_by_receipt":
                BUILD_PLAIN_SHA256,
            "archive_uncompressed_bytes_attested_by_receipt":
                BUILD_PLAIN_BYTES,
            "build_label": BUILD_LABEL,
            "build_status": "PASS",
            "build_publication_pass_means": "DURABLE PUBLICATION ONLY",
            "actual_compiler_process_count_attested_by_receipt": 28,
            "full_process_pid_vector_present_in_small_receipt": False,
            "full_phase_vector_present_in_small_receipt": False,
            "native_binary_digests_present_in_small_receipt": False,
            "combined_bridge_overlay_apply_count": 2,
            "corrected_adapter_overlay_apply_count": 2,
            "receipt_prepublication_graph_version": 50,
            "receipt_historical_evidence_owner_floor": 176,
            "receipt_historical_reference_floor": 181,
            "receipt_historical_resulting_evidence_floor": 178,
            "receipt_historical_resulting_reference_floor": 183,
            "actual_current_v54_evidence_floor":
                CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
            "actual_current_v54_reference_floor":
                CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
            "source_gate_reads_build_archive": False,
            "source_gate_reads_private_root": False,
            "build_publication_qualifies_candidate": False,
        },
        "future_authorized_run": {
            "explicit_run_required": True,
            "unique_campaign_label": LABEL,
            "caller_pins_build_private_root": True,
            "caller_pins_private_root_device_and_inode": True,
            "caller_pins_both_native_sha256_and_bytes": True,
            "independently_verified_build_private_root":
                VERIFIED_BUILD_PRIVATE_ROOT,
            "independently_verified_build_private_root_device":
                VERIFIED_BUILD_PRIVATE_ROOT_DEVICE,
            "independently_verified_build_private_root_inode":
                VERIFIED_BUILD_PRIVATE_ROOT_INODE,
            "independently_verified_native_engine_sha256":
                VERIFIED_NATIVE_ENGINE_SHA256,
            "independently_verified_native_engine_bytes":
                VERIFIED_NATIVE_ENGINE_BYTES,
            "independently_verified_native_bridge_sha256":
                VERIFIED_NATIVE_BRIDGE_SHA256,
            "independently_verified_native_bridge_bytes":
                VERIFIED_NATIVE_BRIDGE_BYTES,
            "private_root_and_native_hashes_present_in_small_receipt": False,
            "private_root_and_native_provenance":
                "INDEPENDENT FULL-REPORT AND ACTUAL PHASE-INODE PREFLIGHT",
            "phase_directory_device_or_inode_present_in_full_report": False,
            "infer_private_root_from_mtime": False,
            "enumerate_or_select_tmp_directories": False,
            "invent_snapshot_root": False,
            "authenticate_complete_v16_build_archive_exactly_once": True,
            "archive_effect_ledger_initialized_before_read": True,
            "source_gate_reads_build_archive": False,
            "worker_reads_build_archive": False,
            "public_recovery_reads_build_archive": False,
            "phase_names": list(PHASE_NAMES),
            "expected_compiler_processes_per_phase": len(PROCESS_NAMES),
            "expected_distinct_compiler_processes": 2 * len(PROCESS_NAMES),
            "ordered_process_names_per_phase": list(PROCESS_NAMES),
            "private_source_owners_per_phase": len(SOURCE_OWNERS),
            "private_native_roles_per_phase": 2,
            "fresh_distinct_phase_inodes_required": True,
            "full_elf_bytes_compared_before_activation": True,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "distinct_actual_candidate_worker_processes": SUITE_COUNT,
        },
        "public_exact_inode_recovery": {
            "root": PUBLIC_RECOVERY_ROOT,
            "lock_filename": LOCK_NAME,
            "lock_mode": "0600",
            "exclusive_nonblocking_lock": True,
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "original_owner_identities": copy.deepcopy(ORIGINALS),
            "caller_pins_exact_recovery_journal_sha256": True,
            "same_directory_nofollow_original_inode_hardlinks": True,
            "journal_announced_and_fsynced_before_first_mutation": True,
            "individual_intention_fsync_before_mutation": True,
            "blocked_graceful_signals_during_mutations": True,
            "restore_all_four_original_inodes_before_publication": True,
            "group_atomic": False,
            "sigkill_automatically_recovered": False,
            "power_failure_automatically_recovered": False,
        },
        "publication": {
            "fresh_evidence_prefix":
                "repaired-rust-original-campaign-v9-rust-" + LABEL,
            "previous_evidence_owner_lower_bound":
                CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
            "previous_history_reference_lower_bound":
                CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
            "new_evidence_owner_count_after_genuine_publication": 2,
            "resulting_evidence_owner_lower_bound":
                CURRENT_EVIDENCE_OWNER_LOWER_BOUND + 2,
            "resulting_history_reference_lower_bound":
                CURRENT_HISTORY_REFERENCE_LOWER_BOUND + 2,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "publication_before_restoration": "FORBIDDEN",
            "global_evidence_owner_census": "NOT MEASURED",
        },
        "source_only_effects": source_zero_effects(),
    }


def validate_contract(document: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(document) is dict,
            "require the exact V9 complete frozen machine contract")
    expected = protocol_document(source_pin, protocol_pin)
    require(canonical(document) == canonical(expected),
            "reject a missing, reordered-policy, or forged V9 source freeze")
    return document


def validate_historical_receipt(document: Mapping[str, Any]) -> None:
    expected: dict[str, Any] = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v7-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL", "family": FAMILY,
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "campaign_source_sha256": HISTORICAL_CAMPAIGN[0].sha256,
        "campaign_protocol_sha256": HISTORICAL_CAMPAIGN[1].sha256,
        "campaign_contract_sha256": HISTORICAL_CAMPAIGN[2].sha256,
        "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "attempted_suite_count": SUITE_COUNT,
        "started_suite_count": SUITE_COUNT,
        "completed_suite_count": SUITE_COUNT,
        "actual_candidate_workers": SUITE_COUNT,
        "distinct_worker_process_id_count": SUITE_COUNT,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "semantic_mismatch_count": 928,
        "verified_passing_case_count": 8965,
        "infrastructure_failure_count": 0,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "corrected_reference_records_sha256": REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_process_ids": list(REFERENCE_PIDS),
        "candidate_qualified": False,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "winner_selected": False,
    }
    for name, value in expected.items():
        require(type(document.get(name)) is type(value)
                and document[name] == value,
                "reject a changed historical Rust V7 receipt: " + name)
    workers = document.get("actual_worker_process_ids")
    require(type(workers) is list and len(workers) == SUITE_COUNT
            and len(set(workers)) == SUITE_COUNT
            and all(type(pid) is int and pid > 0 for pid in workers),
            "require thirteen genuine distinct historical Rust workers")
    require(document["verified_passing_case_count"]
            != CASE_COUNT - document["semantic_mismatch_count"],
            "never invent verified passes by subtracting mismatches")


def validate_build_receipt(document: Mapping[str, Any]) -> None:
    expected: dict[str, Any] = {
        "schema": "rebar-phase2-owned-rust-buffer-shape-source-build-v16-durable-publication-receipt",
        "status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": "PASS", "family": FAMILY, "label": BUILD_LABEL,
        "source_sha256": BUILD[0].sha256,
        "protocol_sha256": BUILD[1].sha256,
        "contract_sha256": BUILD[2].sha256,
        "archive_relative": BUILD_ARCHIVE.path,
        "archive_sha256": BUILD_ARCHIVE.sha256,
        "archive_bytes": BUILD_ARCHIVE.size,
        "uncompressed_sha256": BUILD_PLAIN_SHA256,
        "uncompressed_bytes": BUILD_PLAIN_BYTES,
        "current_graph_version": 50,
        "prepublication_evidence_owner_lower_bound": 176,
        "prepublication_history_reference_lower_bound": 181,
        "later_append_only_evidence_allowed": True,
        "new_actual_evidence_owner_count": 2,
        "evidence_owner_lower_bound_after_publication": 178,
        "history_reference_lower_bound_after_publication": 183,
        "historical_actual_rust_matching_status": "FAIL",
        "historical_actual_rust_mismatch_count": 928,
        "historical_actual_rust_verified_passing_case_count": 8965,
        "historical_actual_rust_candidate_workers": SUITE_COUNT,
        "buffer_feature_source_sha256": BUFFER_FEATURE[0].sha256,
        "buffer_feature_protocol_sha256": BUFFER_FEATURE[1].sha256,
        "buffer_feature_contract_sha256": BUFFER_FEATURE[2].sha256,
        "pickle_feature_source_sha256": PICKLE_FEATURE[0].sha256,
        "pickle_feature_protocol_sha256": PICKLE_FEATURE[1].sha256,
        "pickle_feature_contract_sha256": PICKLE_FEATURE[2].sha256,
        "combined_bridge_sha256": COMBINED_BRIDGE_SHA256,
        "combined_bridge_bytes": COMBINED_BRIDGE_BYTES,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "combined_bridge_overlay_apply_count": 2,
        "corrected_public_adapter_overlay_apply_count": 2,
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN", "candidate_qualified": False,
        "candidate_processes_started": 0,
        "candidate_workers_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    require(type(document) is dict,
            "require the independently durable small V16 build receipt")
    for name, value in expected.items():
        require(type(document.get(name)) is type(value)
                and document[name] == value,
                "reject a false or crossed V16 build receipt: " + name)
    archive = document.get("archive_publication")
    require(type(archive) is dict
            and archive.get("path") == str(ROOT / BUILD_ARCHIVE.path)
            and archive.get("sha256") == BUILD_ARCHIVE.sha256
            and archive.get("bytes") == BUILD_ARCHIVE.size
            and archive.get("device") == BUILD_ARCHIVE.device
            and archive.get("inode") == BUILD_ARCHIVE.inode
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("file_fsync_completed") is True,
            "authenticate V16 archive metadata without opening the archive")
    directory = document.get("archive_directory_fsync")
    require(type(directory) is dict and directory.get("completed") is True,
            "require the actual independently durable V16 archive")


def validate_v8_pre_matching_failure(
        failure: Mapping[str, Any], observation: Mapping[str, Any],
) -> None:
    expected_failure = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v8-entry-failure",
        "status": "FAIL", "family": FAMILY, "error_type": "CampaignError",
        "error_message": "reject a missing, invented, crossed, or duplicate build PID",
        "case_execution_denominator": CASE_COUNT,
        "suite_count": SUITE_COUNT, "candidate_qualified": False,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "winner_selected": False,
    }
    for key, value in expected_failure.items():
        require(failure.get(key) == value,
                "reject a forged actual V8 pre-matching failure: " + key)
    effects = failure.get("actual_effects")
    require(type(effects) is dict, "require the authenticated V8 effect ledger")
    expected_effects = {
        "actual_candidate_workers": 0, "actual_native_activations": 0,
        "actual_reference_workers": 0, "started_suite_count": 0,
        "fully_observed_suite_count": 0, "recovery_journals_created": 0,
        "canonical_target_replacements": 0,
        "v16_build_archive_read_count": 1,
        "v16_build_archive_gzip_inflation_count": 1,
        "v16_build_archive_compressed_bytes_read": BUILD_ARCHIVE.size,
        "v16_build_archive_uncompressed_bytes_read": BUILD_PLAIN_BYTES,
        "v16_build_archive_uncompressed_sha256": BUILD_PLAIN_SHA256,
    }
    for key, value in expected_effects.items():
        require(effects.get(key) == value,
                "reject a fabricated actual V8 effect: " + key)
    require(observation.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v8-entry-failure-observation-v1"
            and observation.get("status") == "PASS"
            and observation.get("version") == 1,
            "require the independent durable observation of the actual V8 failure")
    observed = observation.get("observed_failure")
    require(type(observed) is dict,
            "require the independently observed actual V8 failure")
    observed_expected = {
        "schema": expected_failure["schema"], "status": "FAIL",
        "error_type": "CampaignError",
        "error_message": expected_failure["error_message"],
        "failure_category":
            "AUTHENTIC BUILD-PROCESS SHAPE REJECTED BEFORE CANDIDATE ACTIVATION",
        "candidate_matching": "NOT RUN",
        "full_original_case_denominator": CASE_COUNT,
        "original_suite_count": SUITE_COUNT, "started_suite_count": 0,
        "completed_suite_count": 0, "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "candidate_qualified": False,
    }
    for key, value in observed_expected.items():
        require(observed.get(key) == value,
                "reject a fabricated V8 failure observation: " + key)
    archive = observation.get("actual_build_archive_effects")
    require(type(archive) is dict,
            "require the independently observed historical V8 archive effects")
    archive_expected = {
        "compressed_build_archive_sha256": BUILD_ARCHIVE.sha256,
        "actual_archive_read_count": 1,
        "actual_archive_inflation_count": 1,
        "compressed_bytes_read": BUILD_ARCHIVE.size,
        "uncompressed_bytes_read": BUILD_PLAIN_BYTES,
        "uncompressed_sha256": BUILD_PLAIN_SHA256,
    }
    for key, value in archive_expected.items():
        require(archive.get(key) == value,
                "reject a fabricated V8 historical archive effect: " + key)
    targets = observation.get("actual_target_effects")
    require(type(targets) is dict
            and targets.get("canonical_target_replacements") == 0
            and targets.get("recovery_roots_created") == 0
            and targets.get("recovery_journals_created") == 0
            and targets.get("activated_target_roles") == []
            and targets.get("restored_target_roles") == []
            and targets.get("all_four_original_targets_unchanged_without_recovery") is True
            and targets.get("all_four_original_targets_restored_by_a_recovery") is False,
            "require all actual original targets unchanged with zero V8 recovery")
    require(observation.get("actual_reference_workers") == 0
            and observation.get("new_actual_observation_owner_count") == 2
            and observation.get("actual_clock_samples") == 0
            and observation.get("actual_timing_trials") == 0
            and observation.get("hidden_cases_read") == 0
            and observation.get("holdout") == "NOT OPENED"
            and observation.get("performance") == "NOT MEASURED"
            and observation.get("memory") == "NOT MEASURED"
            and observation.get("confidence_intervals") == "NOT MEASURED"
            and observation.get("winner_selected") is False,
            "reject invented historical V8 candidate work or measurements")


def validate_graph(document: Mapping[str, Any]) -> None:
    expected: dict[str, Any] = {
        "schema": "rebar-candidate-current-overview-v54-summary",
        "version": CURRENT_GRAPH_VERSION, "status": "PASS",
        "suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "full_case_denominator": CASE_COUNT,
        "case_denominator_changed": False,
        "authenticated_evidence_owner_lower_bound":
            CURRENT_GRAPH_EVIDENCE_OWNER_LOWER_BOUND,
        "authenticated_history_reference_lower_bound":
            CURRENT_GRAPH_HISTORY_REFERENCE_LOWER_BOUND,
        "qualified_candidate_count": 0,
        "actually_runnable_candidate_family_count": 0,
        "actual_rust_semantic_mismatch_count": 928,
        "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
        "actual_rust_v16_build_family": FAMILY,
        "actual_rust_v16_build_status": "PASS",
        "actual_rust_v16_publication_status": "PASS",
        "actual_rust_v16_publication_pass_means":
            "DURABLE PUBLICATION ONLY",
        "actual_rust_v16_receipt_sha256": BUILD_RECEIPT.sha256,
        "actual_rust_v16_receipt_bytes": BUILD_RECEIPT.size,
        "actual_rust_v16_receipt_inode": BUILD_RECEIPT.inode,
        "actual_rust_v16_archive_sha256_attested_by_receipt":
            BUILD_ARCHIVE.sha256,
        "actual_rust_v16_archive_bytes": BUILD_ARCHIVE.size,
        "actual_rust_v16_archive_inode": BUILD_ARCHIVE.inode,
        "actual_rust_v16_archive_opened_by_graph": False,
        "actual_rust_v16_archive_inflated_by_graph": False,
        "actual_rust_v16_compiler_process_count": 28,
        "actual_rust_v16_expected_compiler_process_count": 28,
        "actual_rust_v16_compiler_pid_vector_present_in_receipt": False,
        "actual_rust_v16_phase_vector_present_in_receipt": False,
        "actual_rust_v16_native_artifact_digests_present_in_receipt": False,
        "actual_rust_v16_combined_bridge_source_sha256":
            COMBINED_BRIDGE_SHA256,
        "actual_rust_v16_combined_bridge_source_bytes":
            COMBINED_BRIDGE_BYTES,
        "actual_rust_v16_corrected_public_adapter_sha256":
            CORRECTED_ADAPTER_SHA256,
        "actual_rust_v16_corrected_public_adapter_bytes":
            CORRECTED_ADAPTER_BYTES,
        "actual_rust_v16_combined_bridge_overlay_apply_count": 2,
        "actual_rust_v16_corrected_public_adapter_overlay_apply_count": 2,
        "actual_rust_v16_current_prepublication_evidence_lower_bound": 179,
        "actual_rust_v16_current_prepublication_history_lower_bound": 184,
        "actual_rust_v16_historical_receipt_prepublication_evidence_lower_bound": 176,
        "actual_rust_v16_historical_receipt_prepublication_history_lower_bound": 181,
        "actual_rust_v16_historical_receipt_resulting_evidence_lower_bound": 178,
        "actual_rust_v16_historical_receipt_resulting_history_lower_bound": 183,
        "actual_rust_v16_candidate_matching_status": "NOT RUN",
        "actual_rust_v16_candidate_workers_started": 0,
        "actual_rust_v16_candidate_qualified": False,
        "actual_rust_v8_controller_status": "FAIL",
        "actual_rust_v8_controller_failure_stage":
            "BUILD-PROCESS PREFLIGHT; NO MATCHING",
        "actual_rust_v8_controller_error":
            "reject a missing, invented, crossed, or duplicate build PID",
        "actual_rust_v8_failure_sha256": V8_FAILURE.sha256,
        "actual_rust_v8_observation_sha256": V8_OBSERVATION.sha256,
        "actual_rust_v8_observation_status": "PASS",
        "actual_rust_v8_candidate_workers": 0,
        "actual_rust_v8_started_suite_count": 0,
        "actual_rust_v8_completed_suite_count": 0,
        "actual_rust_v8_native_activations": 0,
        "actual_rust_v8_recovery_journals_created": 0,
        "actual_rust_v8_target_replacements": 0,
        "actual_rust_v8_build_archive_reads_by_controller": 1,
        "actual_rust_v8_build_archive_inflations_by_controller": 1,
        "actual_rust_v8_build_archive_compressed_bytes_read":
            BUILD_ARCHIVE.size,
        "actual_rust_v8_build_archive_uncompressed_bytes_read":
            BUILD_PLAIN_BYTES,
        "actual_rust_v8_all_original_targets_unchanged": True,
        "actual_rust_v8_new_plaintext_outcome_owner_count": 2,
        "actual_rust_v8_matching_status": "NOT RUN",
        "actual_rust_v8_candidate_correctness": "NOT MEASURED",
        "actual_rust_v8_candidate_qualified": False,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
    }
    require(type(document) is dict, "require the actual immutable V54 summary")
    for name, value in expected.items():
        require(type(document.get(name)) is type(value)
                and document[name] == value,
                "reject stale or invented current V54 evidence: " + name)


def validate_original_producer(document: Mapping[str, Any]) -> None:
    require(type(document) is dict
            and document.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
            and document.get("version") == 4
            and document.get("family_count") == 6
            and document.get("pairwise_shared_semantic_source_count") == 0
            and document.get("suite_count") == SUITE_COUNT
            and document.get("case_execution_denominator") == CASE_COUNT
            and type(document.get("suites")) is list
            and [(row.get("id"), row.get("case_execution_count"))
                 for row in document["suites"]] == list(SUITES)
            and sum(count for _, count in SUITES) == CASE_COUNT,
            "preserve all 13 original producer V4 suites and all 31,237 cases")


def validate_feature_contract(document: Mapping[str, Any],
                              *, pickle: bool) -> None:
    expected_schema = (
        "rebar-phase2-owned-rust-match-pickle-source-repair-v1-source-freeze"
        if pickle else
        "rebar-phase2-owned-rust-buffer-shape-source-repair-v1-source-freeze"
    )
    require(type(document) is dict and document.get("schema") == expected_schema
            and document.get("version") == 1 and document.get("family") == FAMILY,
            "reject a substituted or crossed first-party Rust repair")
    failure = document.get("actual_v7_failure")
    require(type(failure) is dict
            and failure.get("candidate_status") == "FAIL"
            and failure.get("suite_count") == SUITE_COUNT
            and failure.get("case_execution_denominator") == CASE_COUNT
            and failure.get("semantic_mismatch_count") == 928
            and failure.get("verified_passing_case_count") == 8965
            and failure.get("verified_passing_cases_derived_by_subtraction")
            is False,
            "preserve only the genuinely measured previous Rust failure")
    variant = document.get("candidate_variant")
    if pickle:
        require(type(variant) is dict
                and variant.get("sha256") == COMBINED_BRIDGE_SHA256
                and variant.get("bytes") == COMBINED_BRIDGE_BYTES
                and variant.get("includes_frozen_buffer_shape_repair") is True
                and variant.get("includes_owned_match_pickle_repair") is True
                and variant.get("adds_candidate_family") is False,
                "bind the exact same-family dual-overlay Rust bridge")


def validate_build_freeze(document: Mapping[str, Any]) -> None:
    require(type(document) is dict
            and document.get("schema")
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v16-source-freeze"
            and document.get("version") == 16
            and document.get("family") == FAMILY
            and document.get("source", {}).get("sha256") == BUILD[0].sha256
            and document.get("protocol", {}).get("sha256") == BUILD[1].sha256,
            "require the actually frozen first-party Rust V16 build source")
    future = document.get("future_offline_native_build")
    require(type(future) is dict
            and future.get("phase_count") == 2
            and future.get("processes_per_phase") == 14
            and future.get("ordered_process_names_per_phase")
            == list(PROCESS_NAMES)
            and future.get("cargo_net_offline") is True
            and future.get("passing_build_qualifies_candidate") is False,
            "preserve the exact frozen, offline two-phase build policy")
    family = document.get("first_party_source_family")
    require(type(family) is dict and family.get("family") == FAMILY
            and family.get("canonical_rust_source_owner_count") == 9
            and family.get("external_cargo_dependency_count") == 0
            and family.get("external_regular_expression_engine") == "FORBIDDEN"
            and family.get("stdlib_regular_expression_engine") == "FORBIDDEN"
            and family.get("cpython_sre_engine") == "FORBIDDEN"
            and family.get("another_candidate_engine") == "FORBIDDEN"
            and family.get("production_matching_fallback") == "FORBIDDEN",
            "reject a wrapped package, stdlib engine, or foreign candidate")


def verify_frozen_context(source_pin: str, protocol_pin: str,
                          contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    source_pin = checked_sha256(source_pin, "V9 source")
    protocol_pin = checked_sha256(protocol_pin, "V9 protocol")
    contract_pin = checked_sha256(contract_pin, "V9 canonical contract")
    source = Owner(SOURCE_PATH, source_pin,
                   os.path.getsize(str(ROOT / SOURCE_PATH)))
    protocol = Owner(PROTOCOL_PATH, protocol_pin,
                     os.path.getsize(str(ROOT / PROTOCOL_PATH)))
    contract = Owner(CONTRACT_PATH, contract_pin,
                     os.path.getsize(str(ROOT / CONTRACT_PATH)))
    authenticated: dict[str, dict[str, Any]] = {}
    content: dict[str, bytes] = {}
    groups = (
        (source, protocol, contract, GOAL, PHASE_ONE),
        PRODUCER, HISTORICAL_HELPER, HISTORICAL_CAMPAIGN,
        BUFFER_FEATURE, PICKLE_FEATURE, BUILD, GRAPH,
        (HISTORICAL_RECEIPT, CORRECTED_REFERENCE_RECEIPT, BUILD_RECEIPT,
         V8_FAILURE, V8_OBSERVATION),
    )
    for group in groups:
        for item in group:
            require(not item.path.endswith(".gz"),
                    "a source gate may never enumerate or read an archive")
            require(not item.path.startswith("candidates/"),
                    "a source gate may never read a user candidate")
            if item.path in authenticated:
                continue
            maximum = MAX_GRAPH_BYTES if item in GRAPH else MAX_SOURCE_BYTES
            raw, recorded = read_owner(item, maximum=maximum)
            authenticated[item.path] = recorded
            content[item.path] = raw
    validate_contract(strict_json(content[CONTRACT_PATH], "V9 source contract"),
                      source_pin, protocol_pin)
    producer = strict_json(content[PRODUCER[2].path], "original V4 producer")
    validate_original_producer(producer)
    historical = strict_json(content[HISTORICAL_RECEIPT.path],
                             "historical V7 small receipt")
    validate_historical_receipt(historical)
    v8_failure = strict_json(content[V8_FAILURE.path],
                             "actual V8 pre-matching failure")
    v8_observation = strict_json(content[V8_OBSERVATION.path],
                                 "independent actual V8 failure observation")
    validate_v8_pre_matching_failure(v8_failure, v8_observation)
    build_receipt = strict_json(content[BUILD_RECEIPT.path],
                                "actual V16 small receipt")
    validate_build_receipt(build_receipt)
    build_freeze = strict_json(content[BUILD[2].path], "V16 source freeze")
    validate_build_freeze(build_freeze)
    validate_feature_contract(
        strict_json(content[BUFFER_FEATURE[2].path], "V49 buffer feature"),
        pickle=False,
    )
    validate_feature_contract(
        strict_json(content[PICKLE_FEATURE[2].path], "V50 pickle feature"),
        pickle=True,
    )
    graph = strict_json(content[GRAPH[2].path], "actual current V54 summary")
    validate_graph(graph)
    reference = strict_json(content[CORRECTED_REFERENCE_RECEIPT.path],
                            "corrected reference small receipt")
    require(reference.get("status") == "PASS",
            "retain the genuinely corrected two-process Python reference")
    require(len({item.path for group in groups for item in group})
            == len(authenticated), "reject duplicated frozen source owners")
    return {
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS", "family": FAMILY,
        "version": 9, "label": LABEL,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "authenticated_owner_count": len(authenticated),
        "source_only_authenticated_owners": authenticated,
        "original_producer_version": 4,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "actual_previous_rust_mismatch_count": 928,
        "actual_previous_rust_verified_passing_case_count": 8965,
        "actual_current_graph_version": CURRENT_GRAPH_VERSION,
        "actual_current_evidence_owner_lower_bound":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "actual_current_history_reference_lower_bound":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "actual_v16_build_status": "PASS",
        "actual_v16_build_receipt_sha256": BUILD_RECEIPT.sha256,
        "actual_v16_build_archive_sha256_attested_only":
            BUILD_ARCHIVE.sha256,
        "native_artifact_digests_present_in_receipt": False,
        "private_root_present_in_receipt": False,
        "individual_compiler_pids_present_in_receipt": False,
        "receipt_historical_evidence_owner_floor": 176,
        "receipt_historical_reference_floor": 181,
        "receipt_historical_resulting_evidence_floor": 178,
        "receipt_historical_resulting_reference_floor": 183,
        "actual_current_evidence_owner_floor":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "actual_current_reference_owner_floor":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "build_receipt": build_receipt,
        **source_zero_effects(),
    }


class SourceWall:
    """Physically prevent archive, candidate, native, process, and clock use."""

    def __init__(self) -> None:
        self.blocked: dict[str, int] = {}
        self.originals: list[tuple[Any, str, Any]] = []

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def forbidden(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            self.blocked[category] = self.blocked.get(category, 0) + 1
            raise SourceOnlyViolation(
                "source-only V9 physically blocks " + category + ": " + name
            )

        self.originals.append((owner, name, original))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceWall:
        actions = (
            (builtins, ("open",), "filesystem_reads"),
            (io, ("open",), "filesystem_reads"),
            (os, ("open", "read", "stat", "lstat", "listdir", "scandir"),
             "filesystem_reads"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat"),
             "filesystem_reads"),
            (os, ("write", "unlink", "remove", "rename", "replace", "link",
                  "symlink", "mkdir", "makedirs", "rmdir", "fsync"),
             "filesystem_mutations"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename",
                    "replace", "touch"), "filesystem_mutations"),
            (builtins, ("__import__",), "candidate_imports"),
            (importlib, ("import_module",), "candidate_imports"),
            (importlib.machinery.ExtensionFileLoader,
             ("create_module", "exec_module", "load_module"),
             "native_library_loads"),
            (ctypes, ("CDLL", "PyDLL", "_dlopen"),
             "native_library_loads"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output"), "processes"),
            (os, ("fork", "system", "posix_spawn", "posix_spawnp",
                  "execv", "execve", "spawnv", "spawnve"), "processes"),
            (gzip, ("open", "decompress"), "archive_operations"),
            (tempfile, ("mkdtemp", "mkstemp", "TemporaryFile"),
             "private_root_creation"),
            (socket, ("socket", "create_connection", "getaddrinfo"),
             "network_requests"),
            (threading.Thread, ("start",), "threads"),
            (locale, ("setlocale",), "locale_transitions"),
            (signal, ("signal", "pthread_sigmask", "raise_signal"),
             "signal_operations"),
            (fcntl, ("flock", "lockf"), "recovery_locks"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "sleep"), "clocks"),
        )
        for owner, names, category in actions:
            for name in names:
                self.install(owner, name, category)
        previous = gzip.GzipFile

        def memory_only(*args: Any, **kwargs: Any) -> Any:
            filename = kwargs.get("filename", args[0] if args else None)
            fileobj = kwargs.get("fileobj")
            if filename is None and type(fileobj) is io.BytesIO:
                return previous(*args, **kwargs)
            category = "archive_operations"
            self.blocked[category] = self.blocked.get(category, 0) + 1
            raise SourceOnlyViolation("source-only V9 blocks archive GzipFile")

        self.originals.append((gzip, "GzipFile", previous))
        gzip.GzipFile = memory_only
        return self

    def __exit__(self, kind: Any, value: Any, detail: Any) -> bool:
        del kind, value, detail
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        return False


def synthetic_build_report() -> dict[str, Any]:
    phases: list[dict[str, Any]] = []
    for phase_number, name in enumerate(PHASE_NAMES):
        rows: dict[str, dict[str, Any]] = {}
        for number, (relative, fingerprint, count) in enumerate(SOURCE_OWNERS):
            item: dict[str, Any] = {
                "path": "<FRESH_PRIVATE_TMP>/" + name + "/source/" + relative,
                "sha256": fingerprint, "bytes": count,
                "device": 70016, "inode": 100000 + 100 * phase_number + number,
            }
            if relative in ("candidates/rust/py_bridge.c",
                            "candidates/rust_candidate.py"):
                item["source_overlay"] = {
                    "status": "PASS", "phase": name,
                    "role": ("combined-buffer-shape-and-pickle-bridge"
                             if relative == "candidates/rust/py_bridge.c"
                             else "historically-corrected-public-adapter"),
                    "source_apply_count": 1,
                    "derived_sha256": fingerprint,
                    "derived_source_sha256": fingerprint,
                    "derived_bytes": count,
                    "derived_source_bytes": count,
                    "candidate_original_modified": False,
                    "canonical_candidate_modified": False,
                }
            rows[relative] = item
        outputs: dict[str, dict[str, Any]] = {}
        for offset, (role, filename) in enumerate(
                (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME))):
            fingerprint = digest(("synthetic-v16-owned-" + role).encode("ascii"))
            count = 8192 if role == "engine" else 16384
            outputs[role] = {
                "path": ("<FRESH_PRIVATE_TMP>/" + name
                         + "/native/" + filename),
                "file_name": filename, "sha256": fingerprint,
                "size_bytes": count, "device": 70016,
                "inode": 120000 + 10 * phase_number + offset,
                "audit": {"status": "PASS", "role": role},
            }
        phases.append({"name": name, "fresh_source_owners": rows,
                       "native_outputs": outputs})
    processes = [{"name": name,
                  "pid": 180000 + index, "exit_status": 0}
                 for index, name in enumerate(PROCESS_NAMES * 2)]
    return {
        "schema": "rebar-phase2-owned-rust-buffer-shape-source-build-v16-actual-combined-dual-source-build",
        "version": 16, "status": "PASS", "family": FAMILY,
        "label": BUILD_LABEL, "source_sha256": BUILD[0].sha256,
        "protocol_sha256": BUILD[1].sha256,
        "contract_sha256": BUILD[2].sha256,
        "root_prefix": BUILD_ROOT_PREFIX, "graph_version": 50,
        "prepublication_evidence_owner_lower_bound": 176,
        "prepublication_history_reference_lower_bound": 181,
        "historical_rust_matching_status": "FAIL",
        "historical_rust_mismatch_count": 928,
        "historical_rust_verified_passing_case_count": 8965,
        "buffer_feature_source_sha256": BUFFER_FEATURE[0].sha256,
        "buffer_variant_sha256":
            "29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3",
        "pickle_feature_source_sha256": PICKLE_FEATURE[0].sha256,
        "combined_bridge_sha256": COMBINED_BRIDGE_SHA256,
        "combined_bridge_bytes": COMBINED_BRIDGE_BYTES,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "combined_bridge_overlay_apply_count": 2,
        "corrected_public_adapter_overlay_apply_count": 2,
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28,
        "phase_count": 2, "phases": phases,
        "compiler_processes": processes,
        "reproducibility": {
            "status": "PASS", "family": FAMILY,
            "independent_fresh_phase_count": 2,
            "source_owners_per_phase": 9,
            "unchanged_source_owners_per_phase": 7,
            "combined_bridge_overlay_count": 2,
            "corrected_public_adapter_overlay_count": 2,
            "combined_bridge_sha256": COMBINED_BRIDGE_SHA256,
            "combined_bridge_bytes": COMBINED_BRIDGE_BYTES,
            "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "byte_identical": True, "unique_process_count": 28,
            "native_role_count": 2,
            "native_outputs": {
                role: {
                    "file_name": filename,
                    "sha256": phases[0]["native_outputs"][role]["sha256"],
                    "size_bytes": phases[0]["native_outputs"][role]["size_bytes"],
                    "fresh_independent_inode_count": 2,
                    "reproduced_in_two_fresh_directories": True,
                    "audit": phases[0]["native_outputs"][role]["audit"],
                }
                for role, filename in (("engine", ENGINE_NAME),
                                       ("bridge", BRIDGE_NAME))
            },
        },
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN", "candidate_qualified": False,
        "candidate_processes_started": 0, "candidate_workers_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_build_report(report: Mapping[str, Any],
                          receipt: Mapping[str, Any]) -> dict[str, Any]:
    validate_build_receipt(receipt)
    expected: dict[str, Any] = {
        "schema": "rebar-phase2-owned-rust-buffer-shape-source-build-v16-actual-combined-dual-source-build",
        "version": 16, "status": "PASS", "family": FAMILY,
        "label": BUILD_LABEL, "source_sha256": BUILD[0].sha256,
        "protocol_sha256": BUILD[1].sha256,
        "contract_sha256": BUILD[2].sha256,
        "root_prefix": BUILD_ROOT_PREFIX, "graph_version": 50,
        "prepublication_evidence_owner_lower_bound": 176,
        "prepublication_history_reference_lower_bound": 181,
        "historical_rust_matching_status": "FAIL",
        "historical_rust_mismatch_count": 928,
        "historical_rust_verified_passing_case_count": 8965,
        "buffer_feature_source_sha256": BUFFER_FEATURE[0].sha256,
        "pickle_feature_source_sha256": PICKLE_FEATURE[0].sha256,
        "combined_bridge_sha256": COMBINED_BRIDGE_SHA256,
        "combined_bridge_bytes": COMBINED_BRIDGE_BYTES,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "combined_bridge_overlay_apply_count": 2,
        "corrected_public_adapter_overlay_apply_count": 2,
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28, "phase_count": 2,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN", "candidate_qualified": False,
        "candidate_processes_started": 0, "candidate_workers_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    require(type(report) is dict, "require a complete actual V16 build report")
    for name, value in expected.items():
        require(type(report.get(name)) is type(value)
                and report[name] == value,
                "reject a false complete V16 build report: " + name)
    phases = report.get("phases")
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases] == list(PHASE_NAMES),
            "require both genuinely ordered independent V16 build phases")
    source_identities: set[tuple[int, int]] = set()
    native_identities: set[tuple[int, int]] = set()
    expected_paths = {relative for relative, _, _ in SOURCE_OWNERS}
    expected_native: dict[str, tuple[str, int]] = {}
    for phase in phases:
        name = phase["name"]
        rows = phase.get("fresh_source_owners")
        require(type(rows) is dict and set(rows) == expected_paths,
                "reject an omitted, added, or crossed private Rust source")
        for relative, fingerprint, size in SOURCE_OWNERS:
            row = rows[relative]
            require(type(row) is dict and row.get("sha256") == fingerprint
                    and row.get("bytes") == size
                    and row.get("path")
                    == "<FRESH_PRIVATE_TMP>/" + name + "/source/" + relative
                    and type(row.get("device")) is int
                    and type(row.get("inode")) is int
                    and (row["device"], row["inode"])
                    not in source_identities,
                    "reject an unowned private Rust source: " + relative)
            source_identities.add((row["device"], row["inode"]))
            if relative in ("candidates/rust/py_bridge.c",
                            "candidates/rust_candidate.py"):
                overlay = row.get("source_overlay")
                require(type(overlay) is dict
                        and overlay.get("status") == "PASS"
                        and overlay.get("phase") == name
                        and overlay.get("source_apply_count") == 1
                        and overlay.get("derived_sha256") == fingerprint
                        and overlay.get("derived_source_sha256") == fingerprint
                        and overlay.get("derived_bytes") == size
                        and overlay.get("derived_source_bytes") == size
                        and overlay.get("candidate_original_modified") is False
                        and overlay.get("canonical_candidate_modified") is False
                        and "snapshot_root" not in overlay,
                        "reject a forged or synthetic V16 source overlay")
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                "require both independent actual Rust native roles")
        for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
            item = outputs[role]
            require(type(item) is dict
                    and item.get("file_name") == filename
                    and item.get("path")
                    == "<FRESH_PRIVATE_TMP>/" + name + "/native/" + filename
                    and type(item.get("size_bytes")) is int
                    and 0 < item["size_bytes"] <= MAX_NATIVE_BYTES
                    and checked_sha256(item.get("sha256"),
                                      "complete actual " + role)
                    and type(item.get("device")) is int
                    and type(item.get("inode")) is int
                    and (item["device"], item["inode"])
                    not in native_identities,
                    "reject a reused, incomplete, or foreign V16 ELF: " + role)
            native_identities.add((item["device"], item["inode"]))
            current = (item["sha256"], item["size_bytes"])
            if role in expected_native:
                require(expected_native[role] == current,
                        "require byte-identical independent V16 native roles")
            else:
                expected_native[role] = current
    operations = report.get("compiler_processes")
    require(type(operations) is list and len(operations) == 28,
            "retain all twenty-eight genuine ordered build processes")
    pids: set[int] = set()
    for index, operation in enumerate(operations):
        require(type(operation) is dict
                and operation.get("name")
                == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and ("phase" not in operation
                     or operation.get("phase")
                     == PHASE_NAMES[index // len(PROCESS_NAMES)])
                and type(operation.get("pid")) is int
                and operation["pid"] > 0
                and operation["pid"] not in pids
                and operation.get("exit_status") == 0,
                "reject a missing, invented, crossed, or duplicate build PID")
        pids.add(operation["pid"])
    reproduction = report.get("reproducibility")
    require(type(reproduction) is dict
            and reproduction.get("status") == "PASS"
            and reproduction.get("family") == FAMILY
            and reproduction.get("independent_fresh_phase_count") == 2
            and reproduction.get("source_owners_per_phase") == 9
            and reproduction.get("unchanged_source_owners_per_phase") == 7
            and reproduction.get("combined_bridge_overlay_count") == 2
            and reproduction.get("corrected_public_adapter_overlay_count") == 2
            and reproduction.get("combined_bridge_sha256")
            == COMBINED_BRIDGE_SHA256
            and reproduction.get("corrected_public_adapter_sha256")
            == CORRECTED_ADAPTER_SHA256
            and reproduction.get("byte_identical") is True
            and reproduction.get("unique_process_count") == 28
            and reproduction.get("native_role_count") == 2,
            "require the actual complete dual native reproducibility proof")
    reproduced = reproduction.get("native_outputs")
    require(type(reproduced) is dict
            and set(reproduced) == {"engine", "bridge"},
            "preserve both actual independently reproduced ELF outputs")
    for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
        item = reproduced[role]
        require(type(item) is dict and item.get("file_name") == filename
                and (item.get("sha256"), item.get("size_bytes"))
                == expected_native[role]
                and item.get("fresh_independent_inode_count") == 2
                and item.get("reproduced_in_two_fresh_directories") is True,
                "never derive native ELF identity from Rust C source")
    return {
        "status": "PASS", "source_identity_count": len(source_identities),
        "native_identity_count": len(native_identities),
        "distinct_compiler_process_count": len(pids),
        "native_outputs": {
            role: {"sha256": fingerprint, "size_bytes": size}
            for role, (fingerprint, size) in expected_native.items()
        },
    }


def synthetic_restoration() -> dict[str, Any]:
    restored = {
        role: {
            "relative": expected["relative"],
            "sha256": expected["sha256"],
            "size_bytes": expected["bytes"],
            "device": expected["device"],
            "inode": expected["inode"],
            "mode": expected["mode"],
            "uid": expected["uid"],
            "nlink": expected["nlink"],
        }
        for role, expected in ORIGINALS.items()
    }
    return {
        "report": {
            "status": "PASS", "family": FAMILY, "label": LABEL,
            "restored_targets": restored,
            "restoration_order": list(RESTORATION_ORDER),
            "original_inodes_preserved": True,
            "group_atomic": False,
        },
    }


def validated_restoration_targets(
        restoration: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    require(type(restoration) is dict,
            "require the reviewed actual four-owner restoration receipt")
    report = restoration.get("report")
    require(type(report) is dict and report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("restoration_order") == list(RESTORATION_ORDER)
            and report.get("original_inodes_preserved") is True
            and report.get("group_atomic") is False,
            "preserve the actual same-family reverse-order restoration")
    targets = report.get("restored_targets")
    require(type(targets) is dict and set(targets) == set(ROLE_ORDER),
            "use the real reviewed helper restored_targets field")
    for role in ROLE_ORDER:
        actual = targets[role]
        expected = ORIGINALS[role]
        require(type(actual) is dict
                and actual.get("relative") == expected["relative"]
                and actual.get("sha256") == expected["sha256"]
                and actual.get("size_bytes") == expected["bytes"]
                and actual.get("device") == expected["device"]
                and actual.get("inode") == expected["inode"]
                and actual.get("mode") == expected["mode"]
                and actual.get("uid") == expected["uid"]
                and actual.get("nlink") == expected["nlink"],
                "reject a substituted actual restored original: " + role)
    return targets


def synthetic_campaign_report(source_pin: str, protocol_pin: str,
                              contract_pin: str) -> dict[str, Any]:
    rows = []
    pids = []
    for index, (name, count) in enumerate(SUITES):
        pid = 280000 + index
        pids.append(pid)
        rows.append({
            "suite": name, "case_execution_denominator": count,
            "worker_attempted": True, "actual_worker_started": True,
            "fully_observed": True, "failure_class": "PASS",
            "mismatch_count": 0, "verified_passing_case_count": count,
            "process": {"pid": pid, "actual_worker_processes": 1},
        })
    targets = validated_restoration_targets(synthetic_restoration())
    return {
        "schema": CAMPAIGN_SCHEMA, "status": "PASS",
        "family": FAMILY, "label": LABEL,
        "campaign_source_sha256": source_pin,
        "campaign_protocol_sha256": protocol_pin,
        "campaign_contract_sha256": contract_pin,
        "original_v4_producer_source_sha256": PRODUCER[0].sha256,
        "original_v4_producer_protocol_sha256": PRODUCER[1].sha256,
        "original_v4_producer_contract_sha256": PRODUCER[2].sha256,
        "original_v4_producer_version": 4,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE_RECEIPT.sha256,
        "corrected_reference_records_sha256": REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count": 6912,
        "corrected_reference_process_ids": list(REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "published_current_v54_source_sha256": GRAPH[0].sha256,
        "published_current_v54_inputs_sha256": GRAPH[1].sha256,
        "published_current_v54_summary_sha256": GRAPH[2].sha256,
        "published_current_v54_svg_sha256": GRAPH[3].sha256,
        "current_overview_version": CURRENT_GRAPH_VERSION,
        "actual_v16_build_source_sha256": BUILD[0].sha256,
        "actual_v16_build_protocol_sha256": BUILD[1].sha256,
        "actual_v16_build_contract_sha256": BUILD[2].sha256,
        "actual_v16_build_archive_sha256": BUILD_ARCHIVE.sha256,
        "actual_v16_build_receipt_sha256": BUILD_RECEIPT.sha256,
        "actual_v16_compiler_process_count": 28,
        "actual_v16_build_archive_read_count": 1,
        "actual_v16_build_archive_gzip_inflation_count": 1,
        "actual_v16_build_private_root": VERIFIED_BUILD_PRIVATE_ROOT,
        "actual_v16_build_private_root_device":
            VERIFIED_BUILD_PRIVATE_ROOT_DEVICE,
        "actual_v16_build_private_root_inode":
            VERIFIED_BUILD_PRIVATE_ROOT_INODE,
        "actual_v16_private_source_inode_count": 18,
        "actual_v16_private_native_inode_count": 4,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_bridge_source_sha256": COMBINED_BRIDGE_SHA256,
        "native_engine_sha256": VERIFIED_NATIVE_ENGINE_SHA256,
        "native_engine_bytes": VERIFIED_NATIVE_ENGINE_BYTES,
        "native_bridge_sha256": VERIFIED_NATIVE_BRIDGE_SHA256,
        "native_bridge_bytes": VERIFIED_NATIVE_BRIDGE_BYTES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "suite_results": rows,
        "attempted_suite_count": SUITE_COUNT,
        "started_suite_count": SUITE_COUNT,
        "completed_suite_count": SUITE_COUNT,
        "actual_candidate_workers": SUITE_COUNT,
        "actual_worker_process_ids": pids,
        "distinct_worker_process_id_count": SUITE_COUNT,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "all_original_observation_vectors_complete": True,
        "verified_passing_case_count": CASE_COUNT,
        "semantic_mismatch_count": 0,
        "observed_partial_semantic_mismatch_count": 0,
        "infrastructure_failure_count": 0,
        "candidate_qualified": True,
        "historical_evidence_owner_count_before_publication":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "historical_authenticated_reference_count_before_publication":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "preserved_previous_rust_semantic_mismatch_count": 928,
        "preserved_previous_rust_verified_passing_case_count": 8965,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": "1" * 64,
        "all_four_original_targets_restored": True,
        "restored_original_targets": targets,
        "restoration": synthetic_restoration(),
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "controller_failure": None,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_v9_publication_report(
        report: Mapping[str, Any], source_pin: str,
        protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    require(type(report) is dict,
            "require the complete actual V9 publication report")
    expected: dict[str, Any] = {
        "schema": CAMPAIGN_SCHEMA, "family": FAMILY, "label": LABEL,
        "campaign_source_sha256": source_pin,
        "campaign_protocol_sha256": protocol_pin,
        "campaign_contract_sha256": contract_pin,
        "original_v4_producer_source_sha256": PRODUCER[0].sha256,
        "original_v4_producer_protocol_sha256": PRODUCER[1].sha256,
        "original_v4_producer_contract_sha256": PRODUCER[2].sha256,
        "original_v4_producer_version": 4,
        "corrected_reference_records_sha256": REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_process_ids": list(REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "published_current_v54_source_sha256": GRAPH[0].sha256,
        "published_current_v54_inputs_sha256": GRAPH[1].sha256,
        "published_current_v54_summary_sha256": GRAPH[2].sha256,
        "published_current_v54_svg_sha256": GRAPH[3].sha256,
        "current_overview_version": CURRENT_GRAPH_VERSION,
        "actual_v16_build_source_sha256": BUILD[0].sha256,
        "actual_v16_build_protocol_sha256": BUILD[1].sha256,
        "actual_v16_build_contract_sha256": BUILD[2].sha256,
        "actual_v16_build_archive_sha256": BUILD_ARCHIVE.sha256,
        "actual_v16_build_receipt_sha256": BUILD_RECEIPT.sha256,
        "actual_v16_compiler_process_count": 28,
        "actual_v16_build_archive_read_count": 1,
        "actual_v16_build_archive_gzip_inflation_count": 1,
        "actual_v16_build_private_root": VERIFIED_BUILD_PRIVATE_ROOT,
        "actual_v16_build_private_root_device":
            VERIFIED_BUILD_PRIVATE_ROOT_DEVICE,
        "actual_v16_build_private_root_inode":
            VERIFIED_BUILD_PRIVATE_ROOT_INODE,
        "actual_v16_private_source_inode_count": 18,
        "actual_v16_private_native_inode_count": 4,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_bridge_source_sha256": COMBINED_BRIDGE_SHA256,
        "native_engine_sha256": VERIFIED_NATIVE_ENGINE_SHA256,
        "native_engine_bytes": VERIFIED_NATIVE_ENGINE_BYTES,
        "native_bridge_sha256": VERIFIED_NATIVE_BRIDGE_SHA256,
        "native_bridge_bytes": VERIFIED_NATIVE_BRIDGE_BYTES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "historical_evidence_owner_count_before_publication":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "historical_authenticated_reference_count_before_publication":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "preserved_previous_rust_semantic_mismatch_count": 928,
        "preserved_previous_rust_verified_passing_case_count": 8965,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    for name, value in expected.items():
        require(type(report.get(name)) is type(value)
                and report[name] == value,
                "reject stale or inherited actual V9 publication metadata: "
                + name)
    require(report.get("status") in ("PASS", "FAIL")
            and report.get("candidate_qualified")
            is (report["status"] == "PASS"),
            "never call durable publication candidate correctness")
    require(not any(key.startswith("published_current_v43_")
                    or key.startswith("actual_v13_")
                    for key in report),
            "reject inherited V43 graph or V13 build publication metadata")
    rows = report.get("suite_results")
    require(type(rows) is list and len(rows) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in rows] == list(SUITES),
            "publish only all thirteen exact original V4 suite vectors")
    targets = validated_restoration_targets(report.get("restoration", {}))
    require(report.get("restored_original_targets") == targets,
            "bind V9 publication to the actual helper restored_targets field")
    checked_sha256(report.get("recovery_journal_sha256"),
                   "actual V9 prepared recovery journal")
    return dict(report)


def expect_rejection(operation: Callable[[], Any], name: str,
                     rejected: list[str]) -> None:
    try:
        operation()
    except (CampaignError, KeyError, IndexError, TypeError,
            ValueError, OverflowError, RecursionError):
        rejected.append(name)
        return
    raise CampaignError("accepted a hostile V9 source control: " + name)


def alter(document: Any, path: Sequence[str | int], value: Any) -> Any:
    changed = copy.deepcopy(document)
    current = changed
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = value
    return changed


def source_self_test(source_pin: str, protocol_pin: str,
                     contract_pin: str) -> dict[str, Any]:
    context = verify_frozen_context(source_pin, protocol_pin, contract_pin)
    receipt = context["build_receipt"]
    source_owner = Owner(SOURCE_PATH, source_pin,
                         os.path.getsize(str(ROOT / SOURCE_PATH)))
    source_raw, _ = read_owner(source_owner)
    helper_raw, _ = read_owner(HISTORICAL_HELPER[0])
    build_raw, _ = read_owner(BUILD[0])
    own_ast = ast.parse(source_raw, filename=SOURCE_PATH)
    helper_ast = ast.parse(helper_raw, filename=HISTORICAL_HELPER[0].path)
    build_ast = ast.parse(build_raw, filename=BUILD[0].path)
    # ast.walk imports collections lazily; finish trusted source parsing
    # before physically forbidding every subsequent import.
    own_nodes = tuple(ast.walk(own_ast))
    helper_nodes = tuple(ast.walk(helper_ast))
    build_nodes = tuple(ast.walk(build_ast))
    accepted: list[str] = []
    rejected: list[str] = []
    # Warm standard-library internals before the import wall is installed.
    canonical({"warm": 1})
    digest(b"source-only-v9")
    with SourceWall() as wall:
        frozen = protocol_document(source_pin, protocol_pin)
        validate_contract(copy.deepcopy(frozen), source_pin, protocol_pin)
        accepted.append("accept-exact-v9-canonical-source-freeze")
        require(sum(count for _, count in SUITES) == CASE_COUNT
                and len(SUITES) == SUITE_COUNT
                and len(set(name for name, _ in SUITES)) == SUITE_COUNT,
                "require all exact original CPython case groups")
        accepted.append("accept-exact-thirteen-original-31237-case-groups")
        validate_build_receipt(copy.deepcopy(receipt))
        accepted.append("accept-only-real-small-v16-build-receipt")
        plan = synthetic_build_report()
        summary = validate_build_report(plan, receipt)
        require(summary["source_identity_count"] == 18
                and summary["native_identity_count"] == 4
                and summary["distinct_compiler_process_count"] == 28,
                "exercise the complete real-route-shaped in-memory V16 proof")
        accepted.append("accept-memory-only-two-phase-28-pid-v16-proof")
        restored = synthetic_restoration()
        actual_targets = validated_restoration_targets(restored)
        require(set(actual_targets) == set(ROLE_ORDER),
                "exercise the reviewed actual restored_targets field")
        accepted.append("accept-memory-only-real-restored-targets-key")
        publication_plan = synthetic_campaign_report(
            source_pin, protocol_pin, contract_pin,
        )
        validate_v9_publication_report(
            publication_plan, source_pin, protocol_pin, contract_pin,
        )
        accepted.append("accept-memory-only-own-v54-v16-stream-publication")
        imports = {
            alias.name.split(".", 1)[0]
            for node in own_nodes
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module.split(".", 1)[0]
            for node in own_nodes
            if isinstance(node, ast.ImportFrom) and node.module
        }
        require(not imports.intersection(
            {"re", "_sre", "sre_compile", "sre_parse", "regex",
             "pcre", "pcre2", "re2", "hyperscan"}),
            "reject any stdlib or external production regex delegation")
        accepted.append("accept-zero-import-first-party-production-engine")
        require(any(isinstance(node, ast.FunctionDef)
                    and node.name == "read_recorded_phase"
                    for node in helper_nodes)
                and any(isinstance(node, ast.FunctionDef)
                        and node.name == "verify_reproduced_phases"
                        for node in build_nodes),
                "authenticate frozen first-party recovery and V16 routes")
        accepted.append("accept-historical-helper-and-v16-source-ast-only")

        contract_paths: list[tuple[str, tuple[str, ...], Any]] = [
            ("version", ("version",), 7),
            ("family", ("family",), "zig"),
            ("label", ("label",), BUILD_LABEL),
            ("schema", ("schema",), "rebar-false-v9"),
            ("status", ("status",), "PASS"),
            ("oracle-version", ("original_oracle", "producer_version"), 3),
            ("suite-denominator", ("original_oracle", "case_execution_denominator"), CASE_COUNT - 1),
            ("suite-count", ("original_oracle", "suite_count"), 12),
            ("waiver-count", ("original_oracle", "named_private_waiver_count"), 14),
            ("new-waiver", ("original_oracle", "additional_waivers"), 1),
            ("current-graph", ("current_v54_graph", "version"), 50),
            ("current-evidence", ("current_v54_graph", "authenticated_evidence_owner_lower_bound"), 178),
            ("current-reference", ("current_v54_graph", "authenticated_history_reference_lower_bound"), 183),
            ("historical-mismatch", ("historical_rust_v7", "semantic_mismatch_count"), 1087),
            ("historical-passing", ("historical_rust_v7", "explicitly_verified_passing_case_count"), CASE_COUNT - 928),
            ("false-receipt-pids", ("actual_v16_reproducible_build", "full_process_pid_vector_present_in_small_receipt"), True),
            ("false-receipt-phases", ("actual_v16_reproducible_build", "full_phase_vector_present_in_small_receipt"), True),
            ("false-receipt-native", ("actual_v16_reproducible_build", "native_binary_digests_present_in_small_receipt"), True),
            ("false-snapshot-root", ("future_authorized_run", "invent_snapshot_root"), True),
            ("false-root-enumeration", ("future_authorized_run", "enumerate_or_select_tmp_directories"), True),
            ("false-source-archive", ("future_authorized_run", "source_gate_reads_build_archive"), True),
            ("false-worker-archive", ("future_authorized_run", "worker_reads_build_archive"), True),
            ("false-recovery-archive", ("future_authorized_run", "public_recovery_reads_build_archive"), True),
            ("false-runtime-audit", ("source_only_effects", "runtime_non_delegation"), "PASS"),
            ("false-matching", ("source_only_effects", "candidate_matching"), "PASS"),
            ("false-qualification", ("source_only_effects", "candidate_qualified"), True),
            ("open-holdout", ("source_only_effects", "holdout"), "OPENED"),
            ("invent-speed", ("source_only_effects", "performance"), "PASS"),
            ("invent-memory", ("source_only_effects", "memory"), "PASS"),
            ("group-atomic", ("public_exact_inode_recovery", "group_atomic"), True),
            ("power-loss", ("public_exact_inode_recovery", "power_failure_automatically_recovered"), True),
            ("early-publication", ("publication", "publication_before_restoration"), "ALLOWED"),
        ]
        for name, path, value in contract_paths:
            candidate = alter(frozen, path, value)
            expect_rejection(
                lambda item=candidate: validate_contract(item, source_pin,
                                                          protocol_pin),
                "reject-" + name, rejected,
            )
        receipt_paths: list[tuple[str, Any]] = [
            ("status", "FAIL"), ("build_status", "FAIL"),
            ("label", LABEL), ("source_sha256", HISTORICAL_CAMPAIGN[0].sha256),
            ("archive_sha256", HISTORICAL_RECEIPT.sha256),
            ("archive_bytes", BUILD_ARCHIVE.size + 1),
            ("uncompressed_sha256", COMBINED_BRIDGE_SHA256),
            ("uncompressed_bytes", BUILD_PLAIN_BYTES + 1),
            ("historical_actual_rust_mismatch_count", 1087),
            ("historical_actual_rust_verified_passing_case_count", CASE_COUNT - 928),
            ("combined_bridge_sha256", CORRECTED_ADAPTER_SHA256),
            ("combined_bridge_bytes", COMBINED_BRIDGE_BYTES + 1),
            ("corrected_public_adapter_sha256", COMBINED_BRIDGE_SHA256),
            ("corrected_public_adapter_bytes", CORRECTED_ADAPTER_BYTES + 1),
            ("combined_bridge_overlay_apply_count", 1),
            ("corrected_public_adapter_overlay_apply_count", 1),
            ("actual_compiler_process_count", 27),
            ("candidate_workers_started", 1),
            ("candidate_qualified", True), ("holdout", "OPENED"),
        ]
        for name, value in receipt_paths:
            candidate = copy.deepcopy(receipt)
            candidate[name] = value
            expect_rejection(lambda item=candidate: validate_build_receipt(item),
                             "reject-build-receipt-" + name, rejected)
        genuine_optional = copy.deepcopy(plan)
        genuine_optional["compiler_processes"][0]["phase"] = PHASE_NAMES[0]
        validate_build_report(genuine_optional, receipt)
        accepted.append("accept-correct-optional-authenticated-index-phase")
        for operation_index in range(28):
            candidate = copy.deepcopy(plan)
            correct_phase = PHASE_NAMES[operation_index // len(PROCESS_NAMES)]
            wrong_phase = PHASE_NAMES[1] if correct_phase == PHASE_NAMES[0] else PHASE_NAMES[0]
            candidate["compiler_processes"][operation_index]["phase"] = wrong_phase
            expect_rejection(
                lambda item=candidate: validate_build_report(item, receipt),
                "reject-wrong-optional-index-phase-" + str(operation_index),
                rejected,
            )
        for index in range(28):
            for field, value in (("pid", 0), ("exit_status", 1)):
                candidate = copy.deepcopy(plan)
                candidate["compiler_processes"][index][field] = value
                expect_rejection(
                    lambda item=candidate: validate_build_report(item, receipt),
                    "reject-real-process-" + str(index) + "-" + field,
                    rejected,
                )
        for index in range(1, 28):
            candidate = copy.deepcopy(plan)
            candidate["compiler_processes"][index]["pid"] = (
                candidate["compiler_processes"][0]["pid"]
            )
            expect_rejection(
                lambda item=candidate: validate_build_report(item, receipt),
                "reject-duplicate-real-process-" + str(index), rejected,
            )
        for phase_index, phase_name in enumerate(PHASE_NAMES):
            for relative, _, _ in SOURCE_OWNERS:
                candidate = copy.deepcopy(plan)
                candidate["phases"][phase_index]["fresh_source_owners"][
                    relative
                ]["sha256"] = "0" * 64
                expect_rejection(
                    lambda item=candidate: validate_build_report(item, receipt),
                    "reject-" + phase_name + "-source-" + relative,
                    rejected,
                )
            for role in ("engine", "bridge"):
                candidate = copy.deepcopy(plan)
                candidate["phases"][phase_index]["native_outputs"][role][
                    "sha256"
                ] = "0" * 64
                expect_rejection(
                    lambda item=candidate: validate_build_report(item, receipt),
                    "reject-" + phase_name + "-native-" + role, rejected,
                )
        publication_mutations: list[tuple[str, tuple[str, ...], Any]] = [
            ("stale-v43-current", ("current_overview_version",), 43),
            ("stale-v43-summary", ("published_current_v54_summary_sha256",),
             HISTORICAL_CAMPAIGN[0].sha256),
            ("false-v16-archive", ("actual_v16_build_archive_sha256",),
             HISTORICAL_RECEIPT.sha256),
            ("false-v16-receipt", ("actual_v16_build_receipt_sha256",),
             HISTORICAL_RECEIPT.sha256),
            ("false-v16-archive-count", ("actual_v16_build_archive_read_count",), 0),
            ("false-v16-inflation-count",
             ("actual_v16_build_archive_gzip_inflation_count",), 0),
            ("false-v16-engine", ("native_engine_sha256",),
             COMBINED_BRIDGE_SHA256),
            ("false-v16-bridge", ("native_bridge_sha256",),
             COMBINED_BRIDGE_SHA256),
            ("false-current-evidence",
             ("historical_evidence_owner_count_before_publication",), 178),
            ("false-current-reference",
             ("historical_authenticated_reference_count_before_publication",), 183),
            ("false-historical-mismatches",
             ("preserved_previous_rust_semantic_mismatch_count",), 1087),
            ("false-restoration", ("all_four_original_targets_restored",), False),
            ("false-candidate-qualification", ("candidate_qualified",), False),
        ]
        for name, path, value in publication_mutations:
            candidate = alter(publication_plan, path, value)
            expect_rejection(
                lambda item=candidate: validate_v9_publication_report(
                    item, source_pin, protocol_pin, contract_pin,
                ),
                "reject-v9-publication-" + name, rejected,
            )
        for stale in ("published_current_v43_source_sha256",
                      "published_current_v43_summary_sha256",
                      "actual_v13_build_archive_sha256",
                      "actual_v13_build_receipt_sha256"):
            candidate = copy.deepcopy(publication_plan)
            candidate[stale] = "0" * 64
            expect_rejection(
                lambda item=candidate: validate_v9_publication_report(
                    item, source_pin, protocol_pin, contract_pin,
                ),
                "reject-inherited-v7-receipt-" + stale, rejected,
            )
        wrong_restoration = copy.deepcopy(restored)
        wrong_restoration["report"]["restored_original_targets"] = (
            wrong_restoration["report"].pop("restored_targets")
        )
        expect_rejection(
            lambda: validated_restoration_targets(wrong_restoration),
            "reject-invented-restored-original-targets-field", rejected,
        )
        blockers: list[tuple[str, Callable[[], Any]]] = [
            ("actual-build-archive", lambda: builtins.open(BUILD_ARCHIVE.path, "rb")),
            ("candidate-owner", lambda: os.open("candidates/rust/py_bridge.c", os.O_RDONLY)),
            ("private-build-root", lambda: os.scandir("/tmp")),
            ("native-load", lambda: ctypes.CDLL("_rust_engine.so")),
            ("worker-process", lambda: subprocess.Popen(["false"])),
            ("archive-gzip", lambda: gzip.open(BUILD_ARCHIVE.path, "rb")),
            ("clock", lambda: time.perf_counter()),
            ("network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("recovery-root", lambda: tempfile.mkdtemp()),
        ]
        for name, operation in blockers:
            expect_rejection(operation, "physically-block-" + name, rejected)
        require(len(rejected) >= 160,
                "exercise complete hostile real-route and source-only controls")
        blocked = dict(wall.blocked)
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "family": FAMILY, "version": 9, "label": LABEL,
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "physically_blocked_effect_attempts": blocked,
        "actual_current_graph_version": CURRENT_GRAPH_VERSION,
        "actual_current_evidence_owner_lower_bound":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "actual_current_history_reference_lower_bound":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "actual_v16_build_status": "PASS",
        "actual_v16_small_receipt_sha256": BUILD_RECEIPT.sha256,
        "simulated_only_compiler_process_count": 28,
        "simulated_only_phase_count": 2,
        "simulation_was_real_candidate_execution": False,
        **source_zero_effects(),
    }


def checked_private_root(value: Any, *, device: int | None = None,
                         inode: int | None = None) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "independently caller-pin the actual V16 private build root")
    path = PurePosixPath(value)
    require(path.is_absolute() and str(path) == value
            and len(path.parts) == 3 and path.parts[1] == "tmp"
            and path.parts[2].startswith(BUILD_ROOT_PREFIX)
            and len(path.parts[2]) > len(BUILD_ROOT_PREFIX)
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in path.parts[2]),
            "reject an inferred, escaped, stale, or cross-family build root")
    if device is not None:
        require(type(device) is int and device > 0,
                "caller-pin the actual private root device")
    if inode is not None:
        require(type(inode) is int and inode > 0,
                "caller-pin the actual private root inode")
    require(value == VERIFIED_BUILD_PRIVATE_ROOT,
            "reject a guessed, different, or stale V16 private build root")
    if device is not None:
        require(device == VERIFIED_BUILD_PRIVATE_ROOT_DEVICE,
                "reject the actual independently observed V16 root device")
    if inode is not None:
        require(inode == VERIFIED_BUILD_PRIVATE_ROOT_INODE,
                "reject the actual independently observed V16 root inode")
    return value


def new_actual_ledger(options: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-authorized-real-run-effect-ledger",
        "campaign_mode": "AUTHORIZED RUN",
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "v16_build_archive_read_attempted": False,
        "v16_build_archive_read_count": 0,
        "v16_build_archive_compressed_bytes_read": 0,
        "v16_build_archive_gzip_inflation_attempted": False,
        "v16_build_archive_gzip_inflation_count": 0,
        "v16_build_archive_uncompressed_bytes_read": 0,
        "v16_build_archive_uncompressed_sha256": "NOT READ",
        "historical_v2_helper_preflight_attempted": False,
        "historical_v2_helper_source_preflight_status": "NOT ATTEMPTED",
        "historical_v2_helper_module_preflight_status": "NOT ATTEMPTED",
        "attempted_suite_count": 0,
        "started_suite_count": 0,
        "fully_observed_suite_count": 0,
        "actual_candidate_workers": 0,
        "actual_worker_process_ids": [],
        "worker_attempts": [],
        "retained_suite_results": [],
        "actual_native_activations": 0,
        "activated_target_roles": [],
        "canonical_target_replacements": 0,
        "canonical_target_reads": "NOT MEASURED",
        "canonical_target_stats": "NOT MEASURED",
        "canonical_target_read_lower_bound": 0,
        "recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_root_creation_attempted": False,
        "recovery_roots_created": 0,
        "recovery_lock_attempted": False,
        "recovery_locks_acquired": 0,
        "recovery_journal_creation_attempted": False,
        "recovery_journals_created": 0,
        "recovery_journal_sha256": None,
        "recovery_journal_announced": False,
        "restoration_attempted": False,
        "restored_target_roles": [],
        "all_four_original_targets_restored": False,
        "restoration_verified": False,
        "publication_attempted": False,
        "archive_publication_attempted": False,
        "archive_publication_status": "NOT ATTEMPTED",
        "archive_owner": None,
        "receipt_publication_attempted": False,
        "receipt_publication_status": "NOT ATTEMPTED",
        "receipt_owner": None,
        "publication_status": "NOT ATTEMPTED",
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_qualified": False,
        "winner_selected": False,
    }


def load_frozen_module(owner: Owner, name: str) -> types.ModuleType:
    require(type(name) is str and name.startswith("_rebar_v9_frozen_"),
            "load only an explicitly authorized first-party frozen helper")
    raw, _ = read_owner(owner)
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
    return module


def read_actual_build_report(receipt: Mapping[str, Any],
                             ledger: dict[str, Any]) -> dict[str, Any]:
    validate_build_receipt(receipt)
    require(type(ledger) is dict
            and ledger.get("v16_build_archive_read_count") == 0
            and ledger.get("v16_build_archive_gzip_inflation_count") == 0,
            "initialize a unique actual effect ledger before build archive access")
    ledger["v16_build_archive_read_attempted"] = True
    compressed, archive_owner = read_owner(
        BUILD_ARCHIVE, allow_archive=True, maximum=MAX_BUILD_ARCHIVE_BYTES,
    )
    ledger["v16_build_archive_read_count"] = 1
    ledger["v16_build_archive_compressed_bytes_read"] = len(compressed)
    require(archive_owner["device"] == BUILD_ARCHIVE.device
            and archive_owner["inode"] == BUILD_ARCHIVE.inode
            and (archive_owner["device"], archive_owner["inode"])
            != (BUILD_RECEIPT.device, BUILD_RECEIPT.inode),
            "bind distinct no-follow V16 archive and small receipt inodes")
    ledger["v16_build_archive_gzip_inflation_attempted"] = True
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = decompressor.decompress(compressed, MAX_BUILD_PLAIN_BYTES + 1)
        plain += decompressor.flush()
    except zlib.error as error:
        raise CampaignError("reject the authenticated V16 gzip member") from error
    ledger["v16_build_archive_gzip_inflation_count"] = 1
    ledger["v16_build_archive_uncompressed_bytes_read"] = len(plain)
    ledger["v16_build_archive_uncompressed_sha256"] = digest(plain)
    require(decompressor.eof and not decompressor.unused_data
            and not decompressor.unconsumed_tail
            and len(plain) == BUILD_PLAIN_BYTES
            and digest(plain) == BUILD_PLAIN_SHA256
            and receipt.get("uncompressed_sha256") == digest(plain)
            and receipt.get("uncompressed_bytes") == len(plain),
            "read exactly one complete receipt-authenticated V16 gzip member")
    report = strict_json(plain, "complete actual two-phase V16 build report")
    validate_build_report(report, receipt)
    return report


def authenticate_private_build(report: Mapping[str, Any],
                               options: argparse.Namespace) -> dict[str, Any]:
    root = checked_private_root(options.build_private_root,
                                device=options.build_private_root_device,
                                inode=options.build_private_root_inode)
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_DIRECTORY", 0))
    descriptor = os.open(root, flags)
    try:
        actual_root = os.fstat(descriptor)
        require(stat.S_ISDIR(actual_root.st_mode)
                and actual_root.st_uid == os.geteuid()
                and stat.S_IMODE(actual_root.st_mode) == 0o700
                and actual_root.st_dev == options.build_private_root_device
                and actual_root.st_ino == options.build_private_root_inode,
                "prove the exact caller-pinned private build root inode")
    finally:
        os.close(descriptor)
    raw_natives: dict[str, bytes] = {}
    identities: set[tuple[int, int]] = set()
    phase_rows: dict[str, dict[str, bytes]] = {}
    for phase in report["phases"]:
        name = phase["name"]
        phase_rows[name] = {}
        for relative, fingerprint, count in SOURCE_OWNERS:
            owner = Owner(name + "/source/" + relative, fingerprint, count)
            raw, actual = read_owner(owner, private_root=root)
            row = phase["fresh_source_owners"][relative]
            require((actual["device"], actual["inode"])
                    == (row["device"], row["inode"])
                    and actual["mode"] == 0o600
                    and (actual["device"], actual["inode"])
                    not in identities,
                    "reject an exchanged actual V16 private source inode")
            identities.add((actual["device"], actual["inode"]))
            phase_rows[name][relative] = raw
        for role, filename in (("engine", ENGINE_NAME),
                               ("bridge", BRIDGE_NAME)):
            row = phase["native_outputs"][role]
            owner = Owner(name + "/native/" + filename,
                          row["sha256"], row["size_bytes"])
            raw, actual = read_owner(owner, private_root=root,
                                     maximum=MAX_NATIVE_BYTES)
            require((actual["device"], actual["inode"])
                    == (row["device"], row["inode"])
                    and (actual["device"], actual["inode"])
                    not in identities,
                    "reject an exchanged actual V16 private native inode")
            identities.add((actual["device"], actual["inode"]))
            if role in raw_natives:
                require(raw_natives[role] == raw,
                        "compare complete independently built V16 ELF bytes")
            else:
                raw_natives[role] = raw
    first = report["phases"][0]["native_outputs"]
    require(first["engine"]["sha256"] == options.native_engine_sha256
            and first["engine"]["size_bytes"] == options.native_engine_bytes
            and first["bridge"]["sha256"] == options.native_bridge_sha256
            and first["bridge"]["size_bytes"] == options.native_bridge_bytes,
            "independently caller-pin both actual V16 native ELF artifacts")
    return {
        "root": root, "root_device": actual_root.st_dev,
        "root_inode": actual_root.st_ino,
        "source_inode_count": len(SOURCE_OWNERS) * len(PHASE_NAMES),
        "native_inode_count": 4,
        "all_phase_source_rows": phase_rows,
        "native_bytes": raw_natives,
        "first_phase": report["phases"][0],
        "native_engine_sha256": first["engine"]["sha256"],
        "native_engine_bytes": first["engine"]["size_bytes"],
        "native_bridge_sha256": first["bridge"]["sha256"],
        "native_bridge_bytes": first["bridge"]["size_bytes"],
    }


def corrected_source_tuples() -> tuple[tuple[str, str, int], ...]:
    lookup = {path: (fingerprint, size)
              for path, fingerprint, size in SOURCE_OWNERS}
    ordered = (
        "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
        "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
        "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
        "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
    )
    return tuple((path, *lookup[path]) for path in ordered)


def configure_historical_helpers(
        options: argparse.Namespace,
        *, ledger: dict[str, Any] | None = None,
        private: Mapping[str, Any] | None = None,
        ) -> tuple[types.ModuleType, types.ModuleType]:
    v7 = load_frozen_module(HISTORICAL_CAMPAIGN[0],
                            "_rebar_v9_frozen_reviewed_rust_v7")
    require(v7.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v7"
            and tuple(v7.ROLE_ORDER) == ROLE_ORDER
            and tuple(v7.RESTORATION_ORDER) == RESTORATION_ORDER
            and tuple(v7.SUITES) == SUITES
            and v7.PRODUCER["source"][1] == PRODUCER[0].sha256,
            "load only the exact reviewed same-family V7 recovery helpers")
    if ledger is not None:
        ledger["historical_v2_helper_preflight_attempted"] = True
    v2 = v7.patched_v2_helpers()
    require(v2.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v2"
            and tuple(v2.ROLE_ORDER) == ROLE_ORDER
            and tuple(v2.RESTORATION_ORDER) == RESTORATION_ORDER
            and all(v2.ROLES[role]["original"] == ORIGINALS[role]
                    for role in ROLE_ORDER),
            "authenticate exact first-party V2 helper before V16 activation")
    if ledger is not None:
        ledger["historical_v2_helper_source_preflight_status"] = "PASS"
        ledger["historical_v2_helper_module_preflight_status"] = "PASS"
    corrected = {
        "bridge_source": (COMBINED_BRIDGE_SHA256, COMBINED_BRIDGE_BYTES),
        "adapter": (CORRECTED_ADAPTER_SHA256, CORRECTED_ADAPTER_BYTES),
        "engine": (options.native_engine_sha256, options.native_engine_bytes),
        "bridge": (options.native_bridge_sha256, options.native_bridge_bytes),
    }
    roles = copy.deepcopy(v2.ROLES)
    for role, (fingerprint, count) in corrected.items():
        roles[role]["sha256"] = checked_sha256(fingerprint, "V16 " + role)
        require(type(count) is int and 0 < count <= MAX_NATIVE_BYTES,
                "require an exact caller-pinned actual V16 role size")
        roles[role]["bytes"] = count
    v2.ROLES = roles
    v2.REPAIRED_SOURCE_OWNERS = corrected_source_tuples()
    v2.LABEL = LABEL
    v7.SCHEMA = SCHEMA
    v7.WORKER_SCHEMA = WORKER_SCHEMA
    v7.CAMPAIGN_SCHEMA = CAMPAIGN_SCHEMA
    v7.RECEIPT_SCHEMA = RECEIPT_SCHEMA
    v7.SOURCE_RELATIVE = SOURCE_PATH
    v7.PROTOCOL_RELATIVE = PROTOCOL_PATH
    v7.CONTRACT_RELATIVE = CONTRACT_PATH
    v7.LABEL = LABEL
    v7.PUBLIC_RECOVERY_ROOT = PUBLIC_RECOVERY_ROOT
    v7.LOCK_NAME = LOCK_NAME
    v7.BRIDGE_SOURCE_SHA256 = COMBINED_BRIDGE_SHA256
    v7.BRIDGE_SOURCE_BYTES = COMBINED_BRIDGE_BYTES
    v7.CORRECTED_PUBLIC_SHA256 = CORRECTED_ADAPTER_SHA256
    v7.CORRECTED_PUBLIC_BYTES = CORRECTED_ADAPTER_BYTES
    v7.ENGINE_SHA256 = options.native_engine_sha256
    v7.ENGINE_BYTES = options.native_engine_bytes
    v7.BRIDGE_SHA256 = options.native_bridge_sha256
    v7.BRIDGE_BYTES = options.native_bridge_bytes
    v7.CORRECTED_SOURCE_OWNERS = corrected_source_tuples()
    v7.CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND = (
        CURRENT_EVIDENCE_OWNER_LOWER_BOUND
    )
    v7.CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND = (
        CURRENT_HISTORY_REFERENCE_LOWER_BOUND
    )
    v7.BUILD = {
        "source": (BUILD[0].path, BUILD[0].sha256, BUILD[0].size),
        "protocol": (BUILD[1].path, BUILD[1].sha256, BUILD[1].size),
        "contract": (BUILD[2].path, BUILD[2].sha256, BUILD[2].size),
        "archive": (BUILD_ARCHIVE.path, BUILD_ARCHIVE.sha256,
                    BUILD_ARCHIVE.size),
        "receipt": (BUILD_RECEIPT.path, BUILD_RECEIPT.sha256,
                    BUILD_RECEIPT.size),
    }

    if private is not None:
        def actual_v16_phase(phase: dict[str, Any], role: str) -> bytes:
            require(role in ROLE_ORDER and phase.get("name") == "reference-a",
                    "select only the caller-authenticated first actual V16 phase")
            if role == "bridge_source":
                return private["all_phase_source_rows"]["reference-a"][
                    "candidates/rust/py_bridge.c"
                ]
            if role == "adapter":
                return private["all_phase_source_rows"]["reference-a"][
                    "candidates/rust_candidate.py"
                ]
            return private["native_bytes"][role]

        v2.read_recorded_phase = actual_v16_phase
    return v7, v2


def run_original_worker(options: argparse.Namespace) -> dict[str, Any]:
    context = verify_frozen_context(options.source_sha256,
                                    options.protocol_sha256,
                                    options.contract_sha256)
    require(context.get("status") == "PASS",
            "authenticate all original frozen owners before a real worker")
    v7, v2 = configure_historical_helpers(options)
    active = v7.active_worker_approval(v2, options)
    producer = load_frozen_module(PRODUCER[0],
                                  "_rebar_v9_frozen_original_six_family_v4")
    require(producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v4"
            and producer.SUITE_COUNT == SUITE_COUNT
            and producer.CASE_DENOMINATOR == CASE_COUNT
            and producer.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
            and producer.CORRECTED_PUBLIC_RECORDS_SHA256
            == REFERENCE_RECORDS_SHA256
            and producer.CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
            == REFERENCE_CACHE_RECORDS_SHA256
            and tuple(producer.CORRECTED_PUBLIC_REFERENCE_PIDS)
            == REFERENCE_PIDS
            and [(row.name, row.case_count) for row in producer.SUITES]
            == list(SUITES),
            "run only the complete original independently frozen V4 producer")
    spec = v7.corrected_rust_family(producer)
    suite = producer.suite_spec(options.suite)
    source_pins = {path: fingerprint
                   for path, fingerprint, _ in corrected_source_tuples()}
    pins = {"source": CORRECTED_ADAPTER_SHA256,
            "native_engine": options.native_engine_sha256,
            "native_bridge": options.native_bridge_sha256}
    actual = producer.exact_native_owners(spec, pins, source_pins)
    require(actual["source"]["sha256"] == CORRECTED_ADAPTER_SHA256
            and actual["native_engine"]["sha256"]
            == options.native_engine_sha256
            and actual["native_bridge"]["sha256"]
            == options.native_bridge_sha256,
            "match only through exact genuine first-party Rust native roles")
    if suite.name == "original_bounded_v5":
        observation = producer.observe_original_upstream(
            suite, spec, pins, source_pins)
    elif suite.name == "subinterpreter_v2":
        observation = producer.observe_subinterpreters(
            suite, spec, pins, source_pins,
            producer_sha256=PRODUCER[0].sha256,
        )
    else:
        raw, _ = read_owner(PHASE_ONE)
        manifest = strict_json(raw, "immutable phase-one original oracle")
        observation = producer.observe_direct_suite(
            suite, spec, pins, source_pins, manifest,
        )
    require(type(observation) is dict
            and observation.get("schema")
            == producer.SCHEMA + "-actual-original-suite"
            and observation.get("status") in ("PASS", "FAIL")
            and observation.get("suite") == suite.name
            and observation.get("candidate_family") == FAMILY
            and observation.get("case_execution_denominator")
            == suite.case_count
            and observation.get("actual_candidate_case_count")
            == suite.case_count
            and observation.get("reference_records_sha256")
            == suite.reference_sha256
            and type(observation.get("mismatch_count")) is int
            and observation["mismatch_count"] >= 0
            and type(observation.get("all_mismatches")) is list
            and len(observation["all_mismatches"])
            == observation["mismatch_count"]
            and observation.get("actual_candidate_workers") == 1
            and observation.get("clock_samples") == 0
            and observation.get("holdout") == "NOT OPENED",
            "retain every literal unchanged original candidate observation")
    if suite.name == "public_types_v1":
        baseline = observation.get("baseline_evidence")
        require(type(baseline) is dict
                and baseline.get("status") == "PASS"
                and baseline.get("reference_status") == "PASS"
                and baseline.get("actual_independent_reference_count") == 2
                and baseline.get("reference_records_sha256")
                == REFERENCE_RECORDS_SHA256
                and baseline.get("baseline_reference_pids")
                == list(REFERENCE_PIDS)
                and baseline.get("cache_case_count") == 96
                and baseline.get("cache_records_sha256")
                == REFERENCE_CACHE_RECORDS_SHA256
                and baseline.get("new_reference_workers_started") == 0
                and baseline.get("candidate_imports_by_reference_decoder") == 0
                and baseline.get("c_pattern_equality_failure_waived") is False,
                "bind all 6,912 cases to both complete real Python references")
    if suite.name == "original_bounded_v5":
        require(observation.get("actual_public_record_count") == 152
                and observation.get("actual_debug_skip_count") == 1
                and observation.get("named_private_waiver_count") == 13,
                "preserve all upstream tests and exactly 13 named exclusions")
    if suite.name == "subinterpreter_v2" and observation["status"] == "PASS":
        require(observation.get("actual_case_interpreter_exec_calls") == 394
                and observation.get("actual_interpreters_created") == 11
                and observation.get("actual_interpreters_destroyed") == 11
                and observation.get("all_real_pipes_read_to_eof") is True
                and observation.get("all_real_pipe_descriptors_closed") is True
                and observation.get("interpreter_live_set_restored") is True,
                "retain all 128/394/11 authentic interpreter observations")
    return {
        "schema": WORKER_SCHEMA, "status": observation["status"],
        "candidate_family": FAMILY, "label": LABEL,
        "suite": suite.name,
        "case_execution_denominator": suite.case_count,
        "actual_candidate_case_count": suite.case_count,
        "mismatch_count": observation["mismatch_count"],
        "failure_class": ("PASS" if observation["status"] == "PASS"
                          else "SEMANTIC MISMATCH"),
        "original_observer_source_sha256": PRODUCER[0].sha256,
        "original_observer_version": 4,
        "original_observer_unchanged": True,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE_RECEIPT.sha256,
        "corrected_reference_records_sha256": REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count": 6912,
        "corrected_reference_process_ids": list(REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "actual_v16_build_archive_sha256": BUILD_ARCHIVE.sha256,
        "actual_v16_build_receipt_sha256": BUILD_RECEIPT.sha256,
        "activation_report_sha256": active["report_owner"]["sha256"],
        "activation_receipt_sha256": active["receipt_owner"]["sha256"],
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "repaired_source_owner_count": 9,
        "corrected_public_source_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_bridge_source_sha256": COMBINED_BRIDGE_SHA256,
        "native_engine_sha256": options.native_engine_sha256,
        "native_bridge_sha256": options.native_bridge_sha256,
        "complete_original_observation": v7.stream_observation(observation),
        "all_original_records_and_mismatches_preserved": True,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_qualified": False, "winner_selected": False,
    }


def worker_arguments(options: argparse.Namespace, suite: str,
                     active: Mapping[str, Any]) -> list[str]:
    return [
        PYTHON, "-I", "-B", str(ROOT / SOURCE_PATH), "--worker",
        "--source-sha256", options.source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--contract-sha256", options.contract_sha256,
        "--family", FAMILY, "--label", LABEL, "--suite", suite,
        "--activation-root", active["root"],
        "--activation-report-sha256", active["activation_owner"]["sha256"],
        "--activation-receipt-sha256", active["receipt_owner"]["sha256"],
        "--recovery-journal-sha256", active["journal_owner"]["sha256"],
        "--producer-source-sha256", PRODUCER[0].sha256,
        "--producer-protocol-sha256", PRODUCER[1].sha256,
        "--producer-contract-sha256", PRODUCER[2].sha256,
        "--build-source-sha256", BUILD[0].sha256,
        "--build-protocol-sha256", BUILD[1].sha256,
        "--build-contract-sha256", BUILD[2].sha256,
        "--build-archive-sha256", BUILD_ARCHIVE.sha256,
        "--build-receipt-sha256", BUILD_RECEIPT.sha256,
        "--native-engine-sha256", options.native_engine_sha256,
        "--native-engine-bytes", str(options.native_engine_bytes),
        "--native-bridge-sha256", options.native_bridge_sha256,
        "--native-bridge-bytes", str(options.native_bridge_bytes),
    ]


def stream_record(raw: bytes, maximum: int) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= maximum,
            "retain complete bounded original worker output")
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "sha256": digest(raw), "size_bytes": len(raw),
            "complete": True, "limit_bytes": maximum}


def failed_worker(suite: str, count: int, message: str,
                  *, pid: int | None = None,
                  started: bool = False) -> dict[str, Any]:
    return {
        "suite": suite, "case_execution_denominator": count,
        "worker_attempted": True, "actual_worker_started": started,
        "fully_observed": False,
        "failure_class": "INFRASTRUCTURE FAILURE",
        "mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": 0,
        "process": ({"pid": pid, "actual_worker_processes": 1}
                    if started else None),
        "error_message": message[:8192],
    }


def execute_one_worker(options: argparse.Namespace,
                       suite: str, count: int,
                       active: Mapping[str, Any],
                       ledger: dict[str, Any],
                       v7: types.ModuleType) -> dict[str, Any]:
    ledger["attempted_suite_count"] += 1
    attempt: dict[str, Any] = {
        "suite": suite, "case_execution_denominator": count,
        "worker_attempted": True, "actual_worker_started": False,
        "pid": None,
    }
    ledger["worker_attempts"].append(attempt)
    child: Any = None
    try:
        argv = worker_arguments(options, suite, active)
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        pid = child.pid
        attempt["actual_worker_started"] = True
        attempt["pid"] = pid
        ledger["started_suite_count"] += 1
        ledger["actual_candidate_workers"] += 1
        if type(pid) is int and pid > 0:
            ledger["actual_worker_process_ids"].append(pid)
        stdout, stderr = child.communicate(timeout=WORKER_TIMEOUT_SECONDS)
        require(type(pid) is int and pid > 0
                and type(stdout) is bytes and type(stderr) is bytes
                and len(stdout) <= MAX_WORKER_STDOUT_BYTES
                and len(stderr) <= MAX_WORKER_STDERR_BYTES,
                "preserve the complete started genuine suite worker")
        observed = strict_json(stdout, "complete actual V9 original worker")
        require(observed.get("schema") == WORKER_SCHEMA
                and observed.get("candidate_family") == FAMILY
                and observed.get("label") == LABEL
                and observed.get("suite") == suite
                and observed.get("case_execution_denominator") == count
                and observed.get("actual_candidate_case_count") == count
                and observed.get("original_observer_source_sha256")
                == PRODUCER[0].sha256
                and observed.get("original_observer_version") == 4
                and observed.get("corrected_reference_records_sha256")
                == REFERENCE_RECORDS_SHA256
                and observed.get("corrected_reference_cache_records_sha256")
                == REFERENCE_CACHE_RECORDS_SHA256
                and observed.get("corrected_reference_process_ids")
                == list(REFERENCE_PIDS)
                and observed.get("actual_v16_build_archive_sha256")
                == BUILD_ARCHIVE.sha256
                and observed.get("actual_v16_build_receipt_sha256")
                == BUILD_RECEIPT.sha256
                and observed.get("corrected_public_source_sha256")
                == CORRECTED_ADAPTER_SHA256
                and observed.get("corrected_bridge_source_sha256")
                == COMBINED_BRIDGE_SHA256
                and observed.get("native_engine_sha256")
                == options.native_engine_sha256
                and observed.get("native_bridge_sha256")
                == options.native_bridge_sha256
                and observed.get("actual_candidate_workers") == 1
                and observed.get("all_original_records_and_mismatches_preserved")
                is True
                and observed.get("status") in ("PASS", "FAIL")
                and type(observed.get("mismatch_count")) is int
                and observed["mismatch_count"] >= 0
                and observed.get("failure_class")
                == ("PASS" if observed["status"] == "PASS"
                    else "SEMANTIC MISMATCH")
                and child.returncode
                == (0 if observed["status"] == "PASS" else 1),
                "reject an incomplete, borrowed, or falsified V9 worker")
        v7.validate_streamed_observation(
            observed.get("complete_original_observation")
        )
        ledger["fully_observed_suite_count"] += 1
        return {
            "suite": suite, "case_execution_denominator": count,
            "worker_attempted": True, "actual_worker_started": True,
            "fully_observed": True,
            "failure_class": observed["failure_class"],
            "mismatch_count": observed["mismatch_count"],
            "verified_passing_case_count":
                count if observed["status"] == "PASS" else 0,
            "process": {
                "pid": pid, "returncode": child.returncode,
                "actual_worker_processes": 1,
                "stdout": stream_record(stdout, MAX_WORKER_STDOUT_BYTES),
                "stderr": stream_record(stderr, MAX_WORKER_STDERR_BYTES),
            },
            "original_observer": observed,
        }
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as error:
        if child is not None:
            try:
                if child.poll() is None:
                    child.kill()
                    child.communicate()
            except Exception:
                pass
        return failed_worker(
            suite, count, type(error).__name__ + ": " + str(error),
            pid=attempt.get("pid"),
            started=attempt["actual_worker_started"],
        )


def aggregate_rows(rows: Sequence[dict[str, Any]],
                   controller_failure: Mapping[str, Any] | None
                   ) -> dict[str, Any]:
    require(len(rows) == SUITE_COUNT
            and [(item.get("suite"), item.get("case_execution_denominator"))
                 for item in rows] == list(SUITES),
            "retain all thirteen genuine original worker results")
    pids: list[int] = []
    unique: set[int] = set()
    duplicate = 0
    missing = 0
    started = 0
    complete = 0
    passing = 0
    observed_mismatch = 0
    for row in rows:
        if row.get("actual_worker_started") is True:
            started += 1
            process = row.get("process")
            pid = process.get("pid") if type(process) is dict else None
            if type(pid) is not int or pid <= 0:
                missing += 1
            elif pid in unique:
                duplicate += 1
            else:
                unique.add(pid)
                pids.append(pid)
        if row.get("fully_observed") is True:
            complete += 1
            require(type(row.get("mismatch_count")) is int
                    and row["mismatch_count"] >= 0,
                    "retain every actual original semantic mismatch")
            observed_mismatch += row["mismatch_count"]
            if row.get("failure_class") == "PASS":
                passing += row["case_execution_denominator"]
        else:
            require(row.get("failure_class") == "INFRASTRUCTURE FAILURE",
                    "classify an incomplete worker as infrastructure failure")
    infrastructure = sum(row.get("failure_class") == "INFRASTRUCTURE FAILURE"
                         for row in rows) + int(controller_failure is not None)
    full = (complete == SUITE_COUNT and started == SUITE_COUNT
            and len(unique) == SUITE_COUNT and not duplicate and not missing)
    mismatches: int | str = observed_mismatch if full else "NOT MEASURED"
    qualified = (full and passing == CASE_COUNT and mismatches == 0
                 and infrastructure == 0)
    return {
        "suite_results": list(rows),
        "attempted_suite_count": SUITE_COUNT,
        "started_suite_count": started,
        "completed_suite_count": complete,
        "actual_candidate_workers": started,
        "actual_worker_process_ids": pids,
        "distinct_worker_process_id_count": len(unique),
        "duplicate_worker_process_id_count": duplicate,
        "missing_worker_process_id_count": missing,
        "all_original_observation_vectors_complete": full,
        "verified_passing_case_count": passing,
        "semantic_mismatch_count": mismatches,
        "observed_partial_semantic_mismatch_count": observed_mismatch,
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": qualified,
    }


def fresh_evidence_names(failed: bool) -> tuple[str, str]:
    require(type(failed) is bool, "choose an exact original campaign outcome")
    prefix = "repaired-rust-original-campaign-v9-rust-" + LABEL
    if failed:
        prefix += "-failures"
    return prefix + ".json.gz", prefix + "-publication-receipt.json"


def configure_publication(v7: types.ModuleType) -> types.ModuleType:
    owner = Owner(v7.PUBLICATION["source"][0],
                  v7.PUBLICATION["source"][1],
                  v7.PUBLICATION["source"][2])
    publication = load_frozen_module(owner,
                                     "_rebar_v9_frozen_first_party_publisher")
    require(publication.SCHEMA
            == "rebar-owned-six-family-original-p0-campaign-v2"
            and callable(publication.write_streamed_archive),
            "use only the original independently reviewed streaming publisher")
    v7.evidence_names = fresh_evidence_names
    return publication


def preserve_actual_campaign(
        report: dict[str, Any], v7: types.ModuleType,
        v2: types.ModuleType, publication: types.ModuleType,
        ledger: dict[str, Any]) -> dict[str, Any]:
    ledger["publication_attempted"] = True
    ledger["publication_status"] = "ATTEMPTED; NOT COMPLETE"
    report = validate_v9_publication_report(
        report, report["campaign_source_sha256"],
        report["campaign_protocol_sha256"],
        report["campaign_contract_sha256"],
    )
    actual = v2.exact_originals()
    require(report["restored_original_targets"] == actual,
            "verify every exact restored inode before V9 publication")
    publication_counts = {
        "historical_evidence_owner_count_before_publication":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "historical_authenticated_reference_count_before_publication":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND + 2,
        "resulting_authenticated_reference_count":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND + 2,
    }
    ledger["bounded_report_attempted"] = True
    plain_size = v7.bounded_public_report(report)
    ledger["bounded_report_status"] = "PASS"
    archive_name, receipt_name = fresh_evidence_names(
        report["status"] == "FAIL",
    )
    ledger["archive_publication_attempted"] = True
    ledger["archive_publication_status"] = "ATTEMPTED; OUTCOME UNKNOWN"
    directory = publication.open_evidence_directory()
    try:
        archive, stream = publication.write_streamed_archive(
            report, archive_name, directory,
        )
    finally:
        os.close(directory)
    ledger["archive_owner"] = copy.deepcopy(archive)
    require(type(archive) is dict and type(stream) is dict
            and archive.get("relative") == archive_name
            and archive.get("path") == str(ROOT / EVIDENCE_PATH / archive_name)
            and archive.get("sha256") == stream.get("archive_sha256")
            and archive.get("size_bytes") == stream.get("archive_bytes")
            and type(archive.get("write_calls")) is int
            and archive["write_calls"] > 0
            and archive["write_calls"] == stream.get("archive_write_calls")
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("streaming_readback_verified") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and stream.get("gzip_mtime") == 0
            and stream.get("gzip_single_member") is True
            and stream.get("canonical_terminal_newline_count") == 1
            and stream.get("uncompressed_bytes") == plain_size,
            "publish one complete first-party deterministic V9 result archive")
    ledger["archive_publication_status"] = "PASS"
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA, "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": report["status"],
        "family": FAMILY, "label": LABEL,
        "archive": archive,
        "campaign_source_sha256": report["campaign_source_sha256"],
        "campaign_protocol_sha256": report["campaign_protocol_sha256"],
        "campaign_contract_sha256": report["campaign_contract_sha256"],
        "original_v4_producer_source_sha256": PRODUCER[0].sha256,
        "original_v4_producer_protocol_sha256": PRODUCER[1].sha256,
        "original_v4_producer_contract_sha256": PRODUCER[2].sha256,
        "original_v4_producer_version": 4,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE_RECEIPT.sha256,
        "corrected_reference_records_sha256": REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count": 6912,
        "corrected_reference_process_ids": list(REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "published_current_v54_source_sha256": GRAPH[0].sha256,
        "published_current_v54_inputs_sha256": GRAPH[1].sha256,
        "published_current_v54_summary_sha256": GRAPH[2].sha256,
        "published_current_v54_svg_sha256": GRAPH[3].sha256,
        "current_overview_version": CURRENT_GRAPH_VERSION,
        "actual_v16_build_source_sha256": BUILD[0].sha256,
        "actual_v16_build_protocol_sha256": BUILD[1].sha256,
        "actual_v16_build_contract_sha256": BUILD[2].sha256,
        "actual_v16_build_archive_sha256": BUILD_ARCHIVE.sha256,
        "actual_v16_build_receipt_sha256": BUILD_RECEIPT.sha256,
        "actual_v16_compiler_process_count": 28,
        "actual_v16_build_archive_read_count":
            ledger["v16_build_archive_read_count"],
        "actual_v16_build_archive_gzip_inflation_count":
            ledger["v16_build_archive_gzip_inflation_count"],
        "actual_v16_build_private_root": VERIFIED_BUILD_PRIVATE_ROOT,
        "actual_v16_build_private_root_device":
            VERIFIED_BUILD_PRIVATE_ROOT_DEVICE,
        "actual_v16_build_private_root_inode":
            VERIFIED_BUILD_PRIVATE_ROOT_INODE,
        "combined_bridge_source_sha256": COMBINED_BRIDGE_SHA256,
        "combined_bridge_source_bytes": COMBINED_BRIDGE_BYTES,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "native_engine_sha256": VERIFIED_NATIVE_ENGINE_SHA256,
        "native_engine_bytes": VERIFIED_NATIVE_ENGINE_BYTES,
        "native_bridge_sha256": VERIFIED_NATIVE_BRIDGE_SHA256,
        "native_bridge_bytes": VERIFIED_NATIVE_BRIDGE_BYTES,
        "uncompressed_sha256": stream["uncompressed_sha256"],
        "uncompressed_bytes": stream["uncompressed_bytes"],
        "uncompressed_chunk_count": stream["uncompressed_chunk_count"],
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "attempted_suite_count": report["attempted_suite_count"],
        "started_suite_count": report["started_suite_count"],
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_worker_process_ids": report["actual_worker_process_ids"],
        "distinct_worker_process_id_count":
            report["distinct_worker_process_id_count"],
        "duplicate_worker_process_id_count":
            report["duplicate_worker_process_id_count"],
        "missing_worker_process_id_count":
            report["missing_worker_process_id_count"],
        "all_original_observation_vectors_complete":
            report["all_original_observation_vectors_complete"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        **publication_counts,
        "preserved_previous_rust_semantic_mismatch_count": 928,
        "preserved_previous_rust_verified_passing_case_count": 8965,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": actual,
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    require(not any(name.startswith("published_current_v43_")
                    or name.startswith("actual_v13_")
                    for name in receipt),
            "never inherit stale V43 or V13 metadata in the V9 receipt")
    ledger["receipt_publication_attempted"] = True
    ledger["receipt_publication_status"] = "ATTEMPTED; OUTCOME UNKNOWN"
    receipt_owner = v2.write_evidence_receipt(receipt_name, receipt)
    complete = v7.canonical(receipt)
    require(type(receipt_owner) is dict
            and receipt_owner.get("relative")
            == EVIDENCE_PATH + "/" + receipt_name
            and receipt_owner.get("path")
            == str(ROOT / EVIDENCE_PATH / receipt_name)
            and receipt_owner.get("sha256") == digest(complete)
            and receipt_owner.get("bytes") == len(complete)
            and receipt_owner.get("size_bytes") == len(complete)
            and receipt_owner.get("mode") == 0o600
            and receipt_owner.get("uid") == ORIGINALS["adapter"]["uid"]
            and receipt_owner.get("nlink") == 1
            and receipt_owner.get("exclusive_creation") is True
            and receipt_owner.get("same_inode_readback_verified") is True
            and receipt_owner.get("file_fsync_completed") is True
            and receipt_owner.get("directory_fsync_completed") is True
            and (archive["device"], archive["inode"])
            != (receipt_owner["device"], receipt_owner["inode"])
            and v2.exact_originals() == actual,
            "publish a separate owner-only V54/V16 V9 receipt after restoration")
    ledger["receipt_owner"] = copy.deepcopy(receipt_owner)
    ledger["receipt_publication_status"] = "PASS"
    ledger["publication_status"] = "PASS"
    return {
        "schema": SCHEMA + "-published-complete-original-campaign",
        "status": report["status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": FAMILY, "label": LABEL,
        "archive": archive, "receipt": receipt_owner,
        "current_overview_version": CURRENT_GRAPH_VERSION,
        "actual_v16_build_archive_sha256": BUILD_ARCHIVE.sha256,
        "actual_v16_build_receipt_sha256": BUILD_RECEIPT.sha256,
        "actual_v16_build_archive_read_count":
            ledger["v16_build_archive_read_count"],
        "actual_v16_build_archive_gzip_inflation_count":
            ledger["v16_build_archive_gzip_inflation_count"],
        "native_engine_sha256": VERIFIED_NATIVE_ENGINE_SHA256,
        "native_bridge_sha256": VERIFIED_NATIVE_BRIDGE_SHA256,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "attempted_suite_count": report["attempted_suite_count"],
        "started_suite_count": report["started_suite_count"],
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_worker_process_ids": report["actual_worker_process_ids"],
        "distinct_worker_process_id_count":
            report["distinct_worker_process_id_count"],
        "duplicate_worker_process_id_count":
            report["duplicate_worker_process_id_count"],
        "missing_worker_process_id_count":
            report["missing_worker_process_id_count"],
        "all_original_observation_vectors_complete":
            report["all_original_observation_vectors_complete"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        **publication_counts,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": actual,
        "group_atomic": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def run_campaign(options: argparse.Namespace,
                 ledger: dict[str, Any]) -> dict[str, Any]:
    context = verify_frozen_context(options.source_sha256,
                                    options.protocol_sha256,
                                    options.contract_sha256)
    require(context.get("status") == "PASS",
            "verify all exact frozen sources before any archive or activation")
    validate_build_receipt(context["build_receipt"])
    report = read_actual_build_report(context["build_receipt"], ledger)
    private = authenticate_private_build(report, options)
    v7, v2 = configure_historical_helpers(options, ledger=ledger,
                                           private=private)
    publication = configure_publication(v7)
    v7.ensure_fresh_evidence(publication)
    baseline: dict[str, Any] | None = None
    active: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    controller_failure: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    directory: int | None = None
    lock: int | None = None
    with v7.installed_signal_handlers():
        try:
            with v7.blocked_controller_signals():
                directory, lock = v7.open_recovery_lock(
                    v2, options.activation_root, create=True, ledger=ledger,
                )
            baseline = v2.exact_originals()
            ledger["canonical_target_read_lower_bound"] += len(ROLE_ORDER)
            active = v7.activate_four_roles(
                v2, {"build": {"phases": report["phases"]}},
                options, ledger,
            )
            for name, count in SUITES:
                row = execute_one_worker(options, name, count,
                                         active, ledger, v7)
                rows.append(row)
                ledger["retained_suite_results"].append(row)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as error:
            controller_failure = {
                "error_type": type(error).__name__,
                "error_message": str(error)[:8192],
                "traceback": traceback.format_exc(),
            }
            finished = {row.get("suite") for row in rows}
            for name, count in SUITES:
                if name not in finished:
                    row = failed_worker(name, count,
                                        controller_failure["error_message"])
                    rows.append(row)
                    ledger["retained_suite_results"].append(row)
        finally:
            try:
                if active is not None:
                    with v7.blocked_controller_signals():
                        restoration = v7.restore_corrected_four_roles(
                            v2, active["root"], active["journal"],
                            active["journal_owner"]["sha256"], ledger,
                        )
                if baseline is not None:
                    with v7.blocked_controller_signals():
                        require(v2.exact_originals() == baseline,
                                "restore all four exact original Rust inodes")
            finally:
                if lock is not None:
                    os.close(lock)
                if directory is not None:
                    os.close(directory)
    require(baseline is not None and active is not None
            and restoration is not None,
            "never publish without a prepared and fully restored journal")
    positions = {name: index for index, (name, _) in enumerate(SUITES)}
    rows.sort(key=lambda item: positions[item["suite"]])
    aggregate = aggregate_rows(rows, controller_failure)
    restored = validated_restoration_targets(restoration)
    require(v2.exact_originals() == restored and restored == baseline,
            "prove exact original inodes before any campaign publication")
    qualified = aggregate["candidate_qualified"]
    result: dict[str, Any] = {
        "schema": CAMPAIGN_SCHEMA,
        "status": "PASS" if qualified else "FAIL",
        "family": FAMILY, "label": LABEL,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "original_v4_producer_source_sha256": PRODUCER[0].sha256,
        "original_v4_producer_protocol_sha256": PRODUCER[1].sha256,
        "original_v4_producer_contract_sha256": PRODUCER[2].sha256,
        "original_v4_producer_version": 4,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE_RECEIPT.sha256,
        "corrected_reference_records_sha256": REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count": 6912,
        "corrected_reference_process_ids": list(REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "published_current_v54_source_sha256": GRAPH[0].sha256,
        "published_current_v54_inputs_sha256": GRAPH[1].sha256,
        "published_current_v54_summary_sha256": GRAPH[2].sha256,
        "published_current_v54_svg_sha256": GRAPH[3].sha256,
        "current_overview_version": CURRENT_GRAPH_VERSION,
        "actual_v16_build_source_sha256": BUILD[0].sha256,
        "actual_v16_build_protocol_sha256": BUILD[1].sha256,
        "actual_v16_build_contract_sha256": BUILD[2].sha256,
        "actual_v16_build_archive_sha256": BUILD_ARCHIVE.sha256,
        "actual_v16_build_receipt_sha256": BUILD_RECEIPT.sha256,
        "actual_v16_compiler_process_count": 28,
        "actual_v16_build_archive_read_count":
            ledger["v16_build_archive_read_count"],
        "actual_v16_build_archive_gzip_inflation_count":
            ledger["v16_build_archive_gzip_inflation_count"],
        "actual_v16_build_private_root": private["root"],
        "actual_v16_build_private_root_device": private["root_device"],
        "actual_v16_build_private_root_inode": private["root_inode"],
        "actual_v16_private_source_inode_count":
            private["source_inode_count"],
        "actual_v16_private_native_inode_count":
            private["native_inode_count"],
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_bridge_source_sha256": COMBINED_BRIDGE_SHA256,
        "native_engine_sha256": options.native_engine_sha256,
        "native_engine_bytes": options.native_engine_bytes,
        "native_bridge_sha256": options.native_bridge_sha256,
        "native_bridge_bytes": options.native_bridge_bytes,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        **aggregate,
        "historical_evidence_owner_count_before_publication":
            CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "historical_authenticated_reference_count_before_publication":
            CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "preserved_previous_rust_semantic_mismatch_count": 928,
        "preserved_previous_rust_verified_passing_case_count": 8965,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": restored,
        "restoration": restoration,
        "restoration_verified_before_publication": True,
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
    return preserve_actual_campaign(result, v7, v2, publication, ledger)


def recover_originals(options: argparse.Namespace) -> dict[str, Any]:
    context = verify_frozen_context(options.source_sha256,
                                    options.protocol_sha256,
                                    options.contract_sha256)
    require(context["status"] == "PASS",
            "authenticate all source before exact-inode recovery")
    v7, v2 = configure_historical_helpers(options)
    directory, descriptor = v7.open_recovery_lock(
        v2, options.activation_root, create=False,
    )
    try:
        journal, owner = v2.read_private(
            PUBLIC_RECOVERY_ROOT, "recovery-journal.json",
            options.recovery_journal_sha256,
        )
        restoration = v7.restore_corrected_four_roles(
            v2, PUBLIC_RECOVERY_ROOT, journal, owner["sha256"],
        )
        targets = validated_restoration_targets(restoration)
        require(v2.exact_originals() == targets,
                "independently confirm every actual restored_targets inode")
        return {
            "schema": SCHEMA + "-public-exact-inode-recovery",
            "status": "PASS", "family": FAMILY,
            "label": LABEL, "activation_root": PUBLIC_RECOVERY_ROOT,
            "recovery_journal_sha256": owner["sha256"],
            "restoration": restoration,
            "build_archive_read_count": 0,
            "candidate_workers_started": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False,
        }
    finally:
        os.close(descriptor)
        os.close(directory)


def assert_actual_authority(options: argparse.Namespace,
                            *, worker: bool = False,
                            recover: bool = False) -> None:
    require(options.family == FAMILY and options.activation_root
            == PUBLIC_RECOVERY_ROOT,
            "independently authorize the exact V9 family and recovery root")
    require(options.native_engine_sha256 is not None
            and options.native_bridge_sha256 is not None
            and checked_sha256(options.native_engine_sha256, "V16 engine")
            and checked_sha256(options.native_bridge_sha256, "V16 bridge")
            and type(options.native_engine_bytes) is int
            and 0 < options.native_engine_bytes <= MAX_NATIVE_BYTES
            and type(options.native_bridge_bytes) is int
            and 0 < options.native_bridge_bytes <= MAX_NATIVE_BYTES,
            "caller-pin both actual reproducible V16 ELF roles")
    require(options.native_engine_sha256 == VERIFIED_NATIVE_ENGINE_SHA256
            and options.native_engine_bytes == VERIFIED_NATIVE_ENGINE_BYTES
            and options.native_bridge_sha256 == VERIFIED_NATIVE_BRIDGE_SHA256
            and options.native_bridge_bytes == VERIFIED_NATIVE_BRIDGE_BYTES,
            "reject an unproven native hash or source-derived false ELF role")
    if recover:
        require(options.recovery_journal_sha256 is not None
                and options.label is None and options.suite is None,
                "caller-pin only one exact durable V9 recovery journal")
        checked_sha256(options.recovery_journal_sha256, "V9 recovery journal")
        return
    require(options.label == LABEL
            and options.producer_source_sha256 == PRODUCER[0].sha256
            and options.producer_protocol_sha256 == PRODUCER[1].sha256
            and options.producer_contract_sha256 == PRODUCER[2].sha256
            and options.build_source_sha256 == BUILD[0].sha256
            and options.build_protocol_sha256 == BUILD[1].sha256
            and options.build_contract_sha256 == BUILD[2].sha256
            and options.build_archive_sha256 == BUILD_ARCHIVE.sha256
            and options.build_receipt_sha256 == BUILD_RECEIPT.sha256,
            "caller-pin all exact original producer and actual V16 build owners")
    if worker:
        require(options.suite in {name for name, _ in SUITES}
                and options.activation_report_sha256 is not None
                and options.activation_receipt_sha256 is not None
                and options.recovery_journal_sha256 is not None
                and options.build_private_root is None
                and options.build_private_root_device is None
                and options.build_private_root_inode is None,
                "bind one worker to activation without reopening V16 root")
        for name in ("activation_report_sha256", "activation_receipt_sha256",
                     "recovery_journal_sha256"):
            checked_sha256(getattr(options, name), name)
    else:
        checked_private_root(options.build_private_root,
                             device=options.build_private_root_device,
                             inode=options.build_private_root_inode)
        require(type(options.build_private_root_device) is int
                and type(options.build_private_root_inode) is int
                and options.suite is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None
                and options.recovery_journal_sha256 is None,
                "authorize exactly one full original V9 campaign and root")


def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--worker", action="store_true")
    modes.add_argument("--recover", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--suite", choices=tuple(name for name, _ in SUITES))
    parser.add_argument("--activation-root")
    parser.add_argument("--build-private-root")
    parser.add_argument("--build-private-root-device", type=int)
    parser.add_argument("--build-private-root-inode", type=int)
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    for name in (
        "producer-source", "producer-protocol", "producer-contract",
        "build-source", "build-protocol", "build-contract", "build-archive",
        "build-receipt", "native-engine", "native-bridge",
        "activation-report", "activation-receipt", "recovery-journal",
    ):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    checked_sha256(options.source_sha256, "V9 source")
    checked_sha256(options.protocol_sha256, "V9 protocol")
    authority = (
        "family", "label", "suite", "activation_root",
        "build_private_root", "build_private_root_device",
        "build_private_root_inode", "native_engine_sha256",
        "native_bridge_sha256", "native_engine_bytes", "native_bridge_bytes",
        "producer_source_sha256", "producer_protocol_sha256",
        "producer_contract_sha256", "build_source_sha256",
        "build_protocol_sha256", "build_contract_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, name) is None for name in authority),
                "canonical source rendering never authorizes a build or run")
        return options
    checked_sha256(options.contract_sha256, "V9 canonical machine contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in authority),
                "source-only verification cannot authorize any real effect")
    elif options.worker:
        assert_actual_authority(options, worker=True)
    elif options.recover:
        assert_actual_authority(options, recover=True)
    else:
        assert_actual_authority(options)
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    options: argparse.Namespace | None = None
    ledger: dict[str, Any] | None = None
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.render_contract:
            with SourceWall() as wall:
                result = protocol_document(options.source_sha256,
                                           options.protocol_sha256)
                require(not wall.blocked,
                        "source contract rendering attempted an actual effect")
        elif options.self_test:
            result = source_self_test(options.source_sha256,
                                      options.protocol_sha256,
                                      options.contract_sha256)
        elif options.verify_frozen_context:
            result = verify_frozen_context(options.source_sha256,
                                           options.protocol_sha256,
                                           options.contract_sha256)
        elif options.worker:
            result = run_original_worker(options)
        elif options.recover:
            result = recover_originals(options)
        else:
            ledger = new_actual_ledger(options)
            result = run_campaign(options, ledger)
        raw = canonical(result)
        require(len(raw) <= MAX_WORKER_STDOUT_BYTES,
                "bound complete authentic V9 public output")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; CORRECTED RUST V16 CANDIDATE NOT RUN",
        ) else 1
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as error:
        result: dict[str, Any] = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            "traceback": traceback.format_exc(),
            "family": FAMILY, "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "candidate_qualified": False,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }
        if ledger is not None:
            result["actual_operation_mode"] = "AUTHORIZED RUN"
            result["actual_effects"] = ledger
            result["source_only_zero_effects_claimed"] = False
        else:
            result.update(source_zero_effects())
        raw = canonical(result)
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
