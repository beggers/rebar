#!/usr/bin/env python3
"""Freeze and explicitly run the actual dual-overlay Rust against original P0.

Verification is source-only.  An explicitly requested future run preserves all
four original source and native inodes, all original CPython observations and
all actual failures.  No benchmark or hidden case is ever accessed.
"""
from __future__ import annotations

import argparse
import ast
import base64
import builtins
import copy
import ctypes
import gzip
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
import traceback
import types
from typing import Any, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_repaired_rust_original_campaign_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V2.md"
CONTRACT_RELATIVE = "oracle/phase2/repaired-rust-original-campaign-v2.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v2"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
JOURNAL_SCHEMA = SCHEMA + "-four-owner-recovery-journal"
INTENTION_SCHEMA = SCHEMA + "-individual-owner-intention"
ACTIVATION_SCHEMA = SCHEMA + "-four-owner-activation"
ACTIVATION_RECEIPT_SCHEMA = ACTIVATION_SCHEMA + "-durable-receipt"
RESTORATION_SCHEMA = SCHEMA + "-exact-four-inode-restoration"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
FAMILY = "rust"
LABEL = "phase2-v11-rust-dual-overlay-original-p0"
BUILD_LABEL = "phase2-v11-rust-dual-overlay"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
PRIVATE_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v2-"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_STDOUT_BYTES = 256 * 1024 * 1024
MAX_STDERR_BYTES = 16 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 8 * 3600
SUITE_COUNT = 13
CASE_COUNT = 31_237
PRIVATE_WAIVER_COUNT = 13

GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
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
    "source": ("tools/reproduce_owned_native_source_build_v11.py", "3fb0ca1b6914617eb8a6f491072fcb40b15a364afacbaec2d4caac1e9b6f5d10", 80171),
    "protocol": ("oracle/phase2/NATIVE-SOURCE-BUILD-V11.md", "bd6bce6b14bebe55691900e4a48bb8acf89197660e1d5ebd4c8c38e979c05fe6", 3868),
    "contract": ("oracle/phase2/native-source-build-v11.json", "7b1f8941444e942a85eb9f9df9dc23244112763ca92381fe22f76fd87c95a87a", 7676),
    "archive": ("oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz", "282927f91fd885701dff6c431474f586afbc09460c6a20417ffa20be5a2e891c", 107639),
    "receipt": ("oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay-publication-receipt.json", "4c75468663af0de60b37cdbabfca384c4e7f75e25a6155c2ff1c33f654d3f1d7", 1902),
}
RUST_BRIDGE_REPAIR = {
    "source": ("tools/apply_owned_rust_source_repair_v1.py", "1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851", 59388),
    "protocol": ("oracle/phase2/RUST-SOURCE-REPAIR-V1.md", "df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b", 5496),
    "contract": ("oracle/phase2/rust-source-repair-v1.json", "1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b", 8306),
}
RUST_PUBLIC_REPAIR = {
    "source": ("tools/apply_owned_rust_public_contract_source_repair_v1.py", "ac98ad24c6a4962fb38535cbaa470ae5cd4983643e7e8962e9fc9a1b6a0e12a0", 91232),
    "protocol": ("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V1.md", "a297cbccfe4d4a2a321e7f8fe518662f451fd84f90e17bf86c62cf579875955f", 4027),
    "contract": ("oracle/phase2/rust-public-contract-source-repair-v1.json", "a3b4670c3e321cefd6a1ec65ba80b9aa1a06534a73e30ba56654cc75f6f11431", 13450),
}
V26 = {
    "renderer": ("tools/render_candidate_current_overview_v26.py", "55c36e916f0da8b9ef7b6992724d1d1f98161e834f4d2d21729663d9671a3982", 80805),
    "inputs": ("docs/evidence/candidate-current-overview-v26.inputs.json", "c29e8df08d9b5a03eaad283b625465ba6638f19f69d7d3ab4ea5512e83c37685", 36434),
    "summary": ("docs/evidence/candidate-current-overview-v26.json", "8ebf2ccb74ae2cf62196a1507f94bd39ff4b103122c450865121306accf71f48", 186394),
    "svg": ("docs/evidence/candidate-current-overview-v26.svg", "52b42c7ceccf45f80777d94820a812c7f8e0f790fba03a57aef28c11573dd9cc", 12936),
}
V27 = {
    "renderer": ("tools/render_candidate_current_overview_v27.py", "0df3ed1efbbacd862597e7aac1652eb37ee84c12adf8b79b836a298418925eba", 78380),
    "inputs": ("docs/evidence/candidate-current-overview-v27.inputs.json", "c48ff1d86d6b9b40ff6f8651ae5cbedf1b17889e5420c27ca77ee03168b80897", 43722),
    "summary": ("docs/evidence/candidate-current-overview-v27.json", "e9a3adfa76acc8b551228708865a756b9ec8fc3ba5447280ac655fe78f8f5ab4", 208790),
    "svg": ("docs/evidence/candidate-current-overview-v27.svg", "f50791d54c0aaf743b03054b330957941d077874fa676ca1388b8314266870c3", 13270),
}
ZIG_FAILURE = {
    "source": ("tools/preserve_owned_zig_campaign_preflight_failure_v1.py", "4a401ea42b4446535d51d1c7c65c688196185a0bb9fa2e15aebdb3bfebb85498", 58558),
    "protocol": ("oracle/phase2/ZIG-CAMPAIGN-PREFLIGHT-FAILURE-V1.md", "a3c005c95c61a68a5683125f7805564f4749ea9e82350f2d883da9e29b2817c5", 4413),
    "contract": ("oracle/phase2/zig-campaign-preflight-failure-v1.json", "534a3cde3084c12a4124f5dea057ddb80b53fa4c591c8c72e26931bc277735f0", 16494),
    "archive": ("oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz", "1cb38eb48a2d3305ea98d5103a27ce6ae758137168f68df07a408dec3d055a37", 3711),
    "receipt": ("oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23", 1992),
}
ZIG_CORRECTED_CAMPAIGN = {
    "archive": ("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz", "583d63c92240cec78c861893407003466a5f754b099719aabfc8eaf4f14fbbf8", 5870948),
    "receipt": ("oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json", "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba", 4534),
}

REPAIRED_SOURCE_OWNERS: tuple[tuple[str, str, int], ...] = (
    ("candidates/rust_candidate.py", "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c", 31464),
    ("candidates/rust/py_bridge.c", "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257", 176118),
    ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    ("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
)
ORIGINAL_RUST_SOURCE_OWNERS: tuple[tuple[str, str, int], ...] = (
    ("candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
    ("candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
    *REPAIRED_SOURCE_OWNERS[2:],
)
ENGINE_SHA256 = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_BYTES = 658344
BRIDGE_SHA256 = "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54"
BRIDGE_BYTES = 148656

ROLE_ORDER = ("bridge_source", "adapter", "engine", "bridge")
RESTORATION_ORDER = tuple(reversed(ROLE_ORDER))
ROLES: dict[str, dict[str, Any]] = {
    "bridge_source": {
        "relative": "candidates/rust/py_bridge.c",
        "sha256": REPAIRED_SOURCE_OWNERS[1][1], "bytes": 176118,
        "original": {"relative": "candidates/rust/py_bridge.c", "sha256": "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", "bytes": 175676, "device": 2064, "inode": 419054, "mode": 0o600, "uid": 1000, "nlink": 1},
    },
    "adapter": {
        "relative": "candidates/rust_candidate.py",
        "sha256": REPAIRED_SOURCE_OWNERS[0][1], "bytes": 31464,
        "original": {"relative": "candidates/rust_candidate.py", "sha256": "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", "bytes": 31151, "device": 2064, "inode": 428100, "mode": 0o600, "uid": 1000, "nlink": 1},
    },
    "engine": {
        "relative": "candidates/_rust_engine.so",
        "sha256": ENGINE_SHA256, "bytes": ENGINE_BYTES,
        "original": {"relative": "candidates/_rust_engine.so", "sha256": "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4", "bytes": 660440, "device": 2064, "inode": 430563, "mode": 0o755, "uid": 1000, "nlink": 1},
    },
    "bridge": {
        "relative": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": BRIDGE_SHA256, "bytes": BRIDGE_BYTES,
        "original": {"relative": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "sha256": "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15", "bytes": 144992, "device": 2064, "inode": 430629, "mode": 0o755, "uid": 1000, "nlink": 1},
    },
}
SUITES: tuple[tuple[str, int], ...] = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
    ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)
COMPILER_ROLES = {
    "cargo_version", "rustc_version", "gcc_version", "readelf_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "bridge_dynamic", "engine_symbols", "bridge_symbols", "engine_sections",
    "bridge_sections", "engine_notes", "bridge_notes",
}


class CampaignError(Exception):
    """A source, actual Rust observation, restoration, or publication failed."""


class SourceOnlyViolation(CampaignError):
    """A synthetic-only control attempted an actual external effect."""


def require(valid: Any, message: str) -> None:
    if valid is not True:
        raise CampaignError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and not value.startswith("/")
            and "\\" not in value and "\x00" not in value
            and all(x not in ("", ".", "..") for x in value.split("/")),
            "reject an escaped, empty, or ambiguous owner path")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 96
            and all(x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
                    for x in value),
            "require an exact bounded Rust campaign label")
    return value


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only authentic byte strings")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, allow_nan=False, ensure_ascii=True,
                           sort_keys=True, separators=(",", ":"))
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, OverflowError, RecursionError,
            UnicodeError) as error:
        raise CampaignError("reject noncanonical or nonfinite evidence") from error


def unique_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    found: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in found,
                "reject duplicate JSON evidence fields")
        found[key] = value
    return found


def strict_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "reject missing or unbounded frozen evidence: " + label)
    try:
        value = json.loads(raw.decode("utf-8", "strict"),
                           object_pairs_hook=unique_pairs,
                           parse_constant=lambda x: (_ for _ in ()).throw(
                               ValueError("nonfinite JSON: " + x)))
    except (UnicodeError, ValueError, RecursionError) as error:
        raise CampaignError("reject invalid authentic evidence: " + label) from error
    require(type(value) is dict, "require exactly one evidence object: " + label)
    return value


def owner_record(item: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": checked_relative(item[0]),
            "sha256": checked_digest(item[1], item[0]), "bytes": item[2]}


def mapped_owners(group: dict[str, tuple[str, str, int]]) -> dict[str, Any]:
    return {key: owner_record(item) for key, item in sorted(group.items())}


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode
            and os.path.abspath(sys.executable) == PYTHON,
            "use only isolated, exact stable CPython 3.14.6 with -I -B")


def _read_owned(root: str, relative: str, digest: str, *,
                exact_size: int | None = None,
                maximum: int = MAX_SOURCE_BYTES,
                allow_canonical_target: bool = False,
                private: bool = False) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    checked_digest(digest, relative)
    require(type(root) is str and root.startswith("/")
            and root == root.rstrip("/") and "\x00" not in root,
            "open only one absolute, exact descriptor-owned root")
    if root == str(ROOT):
        require(allow_canonical_target
                or relative not in {entry["relative"] for entry in ROLES.values()},
                "source-only verification never opens a canonical Rust target")
    require(type(maximum) is int and 0 < maximum <= MAX_ARCHIVE_BYTES,
            "require a strict typed owner bound")
    require(exact_size is None or
            (type(exact_size) is int and 0 < exact_size <= maximum),
            "require the exact positive bounded frozen owner size")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    dirs = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        parent = os.open(root, dirs)
        opened.append(parent)
        root_stat = os.fstat(parent)
        require(stat.S_ISDIR(root_stat.st_mode)
                and (not private or
                     (stat.S_IMODE(root_stat.st_mode) == 0o700
                      and root_stat.st_uid == os.geteuid())),
                "reject an unsafe or substituted owner root")
        parts = relative.split("/")
        for part in parts[:-1]:
            parent = os.open(part, dirs, dir_fd=parent)
            opened.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a redirected no-follow owner parent")
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode)
                and first.st_nlink == 1
                and first.st_uid == os.geteuid()
                and 0 < first.st_size <= maximum
                and (exact_size is None or first.st_size == exact_size)
                and (first.st_dev, first.st_ino, first.st_size)
                == (named.st_dev, named.st_ino, named.st_size),
                "reject linked, symlinked, foreign or substituted owner")
        remaining = first.st_size
        chunks: list[bytes] = []
        calculated = hashlib.sha256()
        while remaining:
            part = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(part) is bytes and bool(part),
                    "reject a truncated complete original owner")
            remaining -= len(part)
            calculated.update(part)
            chunks.append(part)
        require(os.read(descriptor, 1) == b"",
                "reject an unrecorded suffix on a frozen owner")
        last = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns,
                 first.st_nlink, first.st_uid)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns,
                    last.st_nlink, last.st_uid)
                and (last.st_dev, last.st_ino, last.st_size,
                     last.st_nlink, last.st_uid)
                == (visible.st_dev, visible.st_ino, visible.st_size,
                    visible.st_nlink, visible.st_uid)
                and calculated.hexdigest() == digest,
                "reject a changed inode, metadata, complete hash, or TOCTOU")
        raw = b"".join(chunks)
        return raw, {
            "relative": relative, "path": root + "/" + relative,
            "sha256": digest, "size_bytes": first.st_size,
            "bytes": first.st_size, "device": first.st_dev,
            "inode": first.st_ino, "mode": stat.S_IMODE(first.st_mode),
            "nlink": first.st_nlink, "uid": first.st_uid,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_owner(item: tuple[str, str, int]) -> tuple[bytes, dict[str, Any]]:
    return _read_owned(str(ROOT), item[0], item[1],
                       exact_size=item[2],
                       maximum=max(MAX_SOURCE_BYTES, item[2]))


def load_frozen(item: tuple[str, str, int],
                purpose: str) -> types.ModuleType:
    raw, first = read_owner(item)
    name = "_rebar_owned_rust_original_campaign_v2_" + purpose + "_" + item[1][:20]
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
    _, last = read_owner(item)
    require(type(module) is types.ModuleType
            and module.__name__ == name
            and os.path.realpath(str(module.__file__)) == str(ROOT / item[0])
            and (first["device"], first["inode"])
            == (last["device"], last["inode"]),
            "reject a changed or redirected frozen helper: " + purpose)
    return module


def source_effects() -> dict[str, Any]:
    return {
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "canonical_target_links": 0, "canonical_target_replacements": 0,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_reference_workers": 0, "actual_native_activations": 0,
        "actual_native_recoveries": 0, "actual_native_libraries_loaded": 0,
        "actual_source_promotions": 0, "actual_source_builds": 0,
        "actual_subprocesses_started": 0, "actual_threads_started": 0,
        "actual_network_requests": 0, "workspace_mutations": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "winner_selected": False,
    }


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "Rust campaign source")
    checked_digest(protocol_pin, "Rust campaign protocol")
    originals = []
    for role in ROLE_ORDER:
        item = ROLES[role]
        old = dict(item["original"])
        old["mode"] = format(old["mode"], "04o")
        originals.append({
            "role": role, "original": old,
            "repaired_sha256": item["sha256"],
            "repaired_bytes": item["bytes"],
        })
    return {
        "schema": CONTRACT_SCHEMA, "version": 2,
        "status": "SOURCE FROZEN; RUST CANDIDATE NOT RUN",
        "phase": "CANDIDATES", "family": FAMILY,
        "campaign_label": LABEL,
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "pinned_cpython": {"path": PYTHON, "sha256": PYTHON_SHA256,
                           "version": "3.14.6"},
        "goal": owner_record(GOAL),
        "phase_one": owner_record(PHASE_ONE),
        "original_v3_producer": mapped_owners(PRODUCER),
        "lossless_v2_publication": {
            "owners": mapped_owners(PUBLICATION),
            "matching_runner_invoked": False,
            "used_only_for": ["exact-single-member-zero-mtime-gzip",
                              "four-gibibyte-bounded-complete-stream",
                              "exclusive-owner-only-fsync-readback"],
        },
        "published_v26_history": {
            "owners": mapped_owners(V26),
            "evidence_owner_count": 141,
            "authenticated_reference_count": 146,
            "qualified_candidate_count": 0,
            "actual_c_candidate_workers": 13,
            "actual_c_verified_passing_case_count": 7325,
            "actual_c_semantic_mismatch_count": 1262,
            "historical_rust_semantic_mismatch_count": 2042,
            "historical_zig_semantic_mismatch_count": 1764,
        },
        "published_v27_history": {
            "owners": mapped_owners(V27),
            "evidence_owner_count": 143,
            "authenticated_reference_count": 148,
            "qualified_candidate_count": 0,
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "actual_c_candidate_workers": 13,
            "actual_c_verified_passing_case_count": 7325,
            "actual_c_semantic_mismatch_count": 1262,
            "actual_repaired_zig_candidate_workers": 13,
            "actual_repaired_zig_completed_suite_count": 13,
            "actual_repaired_zig_semantic_mismatch_count": 2172,
            "actual_repaired_zig_verified_passing_case_count": 2847,
            "actual_repaired_zig_infrastructure_failure_count": 0,
            "actual_repaired_zig_archive_inflated": False,
            "preserved_v26_evidence_owner_count": 141,
            "preserved_v26_authenticated_reference_count": 146,
            "historical_rust_semantic_mismatch_count": 2042,
            "repaired_rust_matching_test_status": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        },
        "preserved_actual_zig_preflight_failure": {
            "owners": mapped_owners(ZIG_FAILURE),
            "actual_controller_exit_status": 1,
            "actual_controller_process_id": "NOT RECORDED",
            "actual_candidate_workers": 0,
            "actual_native_activations": 0,
            "candidate_correctness": "NOT MEASURED",
            "new_actual_evidence_owner_count": 2,
            "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        },
        "preserved_actual_zig_corrected_original_campaign": {
            "owners": mapped_owners(ZIG_CORRECTED_CAMPAIGN),
            "candidate_status": "FAIL",
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "case_execution_denominator": 31237,
            "semantic_mismatch_count": 2172,
            "verified_passing_case_count": 2847,
            "infrastructure_failure_count": 0,
            "all_original_suite_streams_retained": True,
            "original_native_restored": True,
            "restoration_verified_before_publication": True,
            "uncompressed_sha256":
                "c6bb2272f13595fc65a4d83feed12f10412706819962b0c18ba96c2ee01d68ce",
            "uncompressed_bytes": 198178404,
            "source_verification_inflates_archive": False,
            "first_preflight_failure_is_separately_preserved": True,
            "candidate_qualified": False,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
        },
        "actual_rust_v11_source_build": {
            "owners": mapped_owners(RUST_BUILD),
            "bridge_source_repair": mapped_owners(RUST_BRIDGE_REPAIR),
            "public_source_repair": mapped_owners(RUST_PUBLIC_REPAIR),
            "label": BUILD_LABEL,
            "actual_compiler_process_count": 28,
            "independent_phase_count": 2,
            "bridge_overlay_application_count": 2,
            "public_overlay_application_count": 2,
            "historical_evidence_owner_count_at_build": 137,
            "historical_reference_count_at_build": 142,
            "cargo_external_dependency_count": 0,
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "repaired_source_owners": [
                owner_record(x) for x in REPAIRED_SOURCE_OWNERS],
            "native_roles": [
                {"role": "engine", "sha256": ENGINE_SHA256,
                 "bytes": ENGINE_BYTES},
                {"role": "bridge", "sha256": BRIDGE_SHA256,
                 "bytes": BRIDGE_BYTES},
            ],
        },
        "original_oracle": {
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES],
            "unchanged_original_observers": [
                "observe_original_upstream", "observe_direct_suite",
                "observe_subinterpreters"],
            "original_producer_source_modified": False,
            "v3_legacy_activation_dispatch_invoked": False,
            "upstream_public_record_count": 152,
            "upstream_runnable_public_case_count": 151,
            "upstream_debug_skip_count": 1,
            "nested_case_count": 128,
            "nested_interpreter_events": 394,
            "nested_interpreters_created": 11,
            "nested_interpreters_destroyed": 11,
            "nested_fresh_temporary_interpreters": 8,
            "rust_only_candidate_source_rebinding": True,
            "rebind_all_fresh_nested_interpreters": True,
        },
        "four_original_target_owners": originals,
        "worker_policy": {
            "actual_worker_count": 13,
            "actual_distinct_worker_processes": 13,
            "one_isolated_process_per_original_suite": True,
            "continue_after_mismatch_timeout_or_crash": True,
            "preserve_every_worker_stdout_and_stderr": True,
            "preserve_every_complete_original_record": True,
            "candidate_matching_delegated": False,
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "cross_family_matching": "FORBIDDEN",
            "supplemental_cases_added": False,
        },
        "recovery_policy": {
            "target_count": 4,
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "original_inode_backup":
                "ADJACENT SAME-DIRECTORY NO-FOLLOW HARDLINK",
            "preserve_all_original_device_inode_mode_uid_nlink_and_bytes": True,
            "journal_fsync_before_any_mutation": True,
            "individual_intention_fsync_before_hardlink_or_promotion": True,
            "every_replacement_individually_atomic": True,
            "group_atomic": False,
            "recover_on_activation_failure": True,
            "recover_on_worker_failure": True,
            "recover_on_controller_failure": True,
            "restore_all_four_originals_before_publication": True,
            "touch_other_family": False,
        },
        "publication_policy": {
            "directory": EVIDENCE_RELATIVE,
            "stem": "repaired-rust-original-campaign-v2-rust-" + LABEL,
            "exclusive_owner_only_archive": True,
            "exclusive_owner_only_receipt": True,
            "complete_archive_readback_required": True,
            "single_member_gzip_mtime": 0,
            "publish_only_after_all_four_original_inodes_restored": True,
            "retain_all_thirteen_real_suite_streams": True,
            "file_and_directory_fsync": True,
            "overwrite_existing_evidence": False,
        },
        "source_only_effects": source_effects(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict
            and canonical(value) == canonical(
                protocol_document(source_pin, protocol_pin)),
            "reject a weakened Rust source, history, owner, oracle, or recovery")
    return value


class SourceWall:
    """Ensure synthetic controls cannot access native files or run a process."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "filesystem": 0, "process": 0, "clock": 0,
            "network": 0, "thread": 0, "native": 0, "import": 0,
        }

    def install(self, owner: Any, attribute: str, kind: str) -> None:
        if not hasattr(owner, attribute):
            return
        original = getattr(owner, attribute)

        def deny(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise SourceOnlyViolation("source-only gate forbids " + kind)

        self.previous.append((owner, attribute, original))
        setattr(owner, attribute, deny)

    def __enter__(self) -> "SourceWall":
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (os, "read"), (os, "write"), (os, "stat"), (os, "lstat"),
            (os, "fstat"), (os, "link"), (os, "replace"), (os, "rename"),
            (os, "unlink"), (os, "remove"), (os, "mkdir"), (os, "makedirs"),
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
        return self

    def __exit__(self, *_args: Any) -> None:
        for owner, attribute, original in reversed(self.previous):
            setattr(owner, attribute, original)


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(contract_pin, "independently caller-pinned contract")
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceWall() as wall:
        document = protocol_document(source_pin, protocol_pin)

        def accept(name: str, value: Any) -> None:
            require(value is True, "positive synthetic control failed: " + name)
            accepted.append(name)

        def reject(name: str, action: Any) -> None:
            try:
                action()
            except (CampaignError, SourceOnlyViolation, OSError, ValueError,
                    TypeError, UnicodeError, OverflowError, RecursionError):
                rejected.append(name)
                return
            raise CampaignError("unsafe hostile control passed: " + name)

        oracle = document["original_oracle"]
        historical = document["published_v26_history"]
        history = document["published_v27_history"]
        repair = document["actual_rust_v11_source_build"]
        recovery = document["recovery_policy"]
        failure = document["preserved_actual_zig_preflight_failure"]
        corrected_zig = document[
            "preserved_actual_zig_corrected_original_campaign"]
        accept("all-thirteen-unchanged-original-groups", len(SUITES) == 13)
        accept("all-31237-original-case-executions",
               sum(count for _, count in SUITES) == CASE_COUNT)
        accept("all-thirteen-named-private-waivers",
               oracle["named_private_waiver_count"] == 13)
        accept("exact-152-upstream-records-and-one-real-debug-skip",
               oracle["upstream_public_record_count"] == 152
               and oracle["upstream_debug_skip_count"] == 1)
        accept("genuine-128-case-394-event-11-interpreter-lifecycle",
               oracle["nested_case_count"] == 128
               and oracle["nested_interpreter_events"] == 394
               and oracle["nested_interpreters_created"] == 11)
        accept("rebind-exact-rust-only-nine-source-closure-in-every-interpreter",
               oracle["rust_only_candidate_source_rebinding"] is True
               and oracle["rebind_all_fresh_nested_interpreters"] is True
               and len(REPAIRED_SOURCE_OWNERS) == 9)
        accept("authenticate-both-actual-private-source-overlays",
               REPAIRED_SOURCE_OWNERS[0][1] != ORIGINAL_RUST_SOURCE_OWNERS[0][1]
               and REPAIRED_SOURCE_OWNERS[1][1] != ORIGINAL_RUST_SOURCE_OWNERS[1][1]
               and repair["bridge_overlay_application_count"] == 2
               and repair["public_overlay_application_count"] == 2)
        accept("authenticate-genuine-28-process-dual-phase-rust-build",
               repair["actual_compiler_process_count"] == 28
               and repair["independent_phase_count"] == 2)
        accept("preserve-historical-141-owner-146-reference-v26-graph",
               historical["evidence_owner_count"] == 141
               and historical["authenticated_reference_count"] == 146)
        accept("authenticate-current-143-owner-148-reference-v27-graph",
               history["evidence_owner_count"] == 143
               and history["authenticated_reference_count"] == 148)
        accept("current-graph-retains-the-complete-actual-zig-failure",
               history["actual_repaired_zig_candidate_workers"] == 13
               and history["actual_repaired_zig_completed_suite_count"] == 13
               and history["actual_repaired_zig_semantic_mismatch_count"] == 2172
               and history["actual_repaired_zig_verified_passing_case_count"]
               == 2847
               and history["actual_repaired_zig_infrastructure_failure_count"]
               == 0)
        accept("preserve-real-zig-preflight-failure-not-matching",
               failure["actual_controller_exit_status"] == 1
               and failure["actual_controller_process_id"] == "NOT RECORDED"
               and failure["actual_candidate_workers"] == 0
               and failure["candidate_correctness"] == "NOT MEASURED")
        accept("preserve-genuine-complete-repaired-zig-original-failure",
               corrected_zig["candidate_status"] == "FAIL"
               and corrected_zig["actual_candidate_workers"] == 13
               and corrected_zig["completed_suite_count"] == 13
               and corrected_zig["case_execution_denominator"] == 31237
               and corrected_zig["semantic_mismatch_count"] == 2172
               and corrected_zig["verified_passing_case_count"] == 2847
               and corrected_zig["infrastructure_failure_count"] == 0
               and corrected_zig["all_original_suite_streams_retained"]
               and corrected_zig["candidate_qualified"] is False)
        accept("authenticate-zig-compressed-evidence-without-inflation",
               corrected_zig["uncompressed_bytes"] == 198178404
               and corrected_zig["source_verification_inflates_archive"]
               is False)
        accept("preserve-four-authentic-existing-original-owners",
               len(document["four_original_target_owners"]) == 4
               and {ROLES[x]["original"]["inode"] for x in ROLE_ORDER}
               == {419054, 428100, 430563, 430629})
        accept("same-device-original-hardlinks-not-byte-copy",
               recovery["original_inode_backup"]
               == "ADJACENT SAME-DIRECTORY NO-FOLLOW HARDLINK")
        accept("exact-reverse-four-inode-restoration",
               recovery["restoration_order"] == list(RESTORATION_ORDER))
        accept("every-individual-file-operation-not-group-atomic",
               recovery["every_replacement_individually_atomic"] is True
               and recovery["group_atomic"] is False)
        accept("publish-only-after-verifying-all-four-original-inodes",
               recovery["restore_all_four_originals_before_publication"] is True
               and document["publication_policy"][
                   "publish_only_after_all_four_original_inodes_restored"])
        accept("do-not-dispatch-obsolete-original-activation",
               oracle["v3_legacy_activation_dispatch_invoked"] is False)
        accept("reuse-lossless-publication-without-go-or-cpp-matching",
               document["lossless_v2_publication"]["matching_runner_invoked"]
               is False)
        accept("continue-all-thirteen-workers-after-real-failures",
               document["worker_policy"][
                   "continue_after_mismatch_timeout_or_crash"] is True)
        accept("retain-existing-c-losses",
               history["actual_c_semantic_mismatch_count"] == 1262)
        accept("preserve-real-historical-rust-matching-losses",
               history["historical_rust_semantic_mismatch_count"] == 2042)
        accept("source-freeze-does-not-run-or-activate",
               document["source_only_effects"] == source_effects())

        for value in ("", "a" * 63, "a" * 65, "A" * 64,
                      "g" * 64, None, 1, True):
            reject("reject-invalid-digest-" + repr(value),
                   lambda item=value: checked_digest(item, "hostile"))
        for value in ("", "/", "/tmp", "../escape", "a/../b",
                      "a//b", "a\\b", "a\x00b", None, 1):
            reject("reject-invalid-relative-" + repr(value),
                   lambda item=value: checked_relative(item))
        changes = (
            ("weaken-full-original-denominator",
             lambda x: x["original_oracle"].update(
                 {"case_execution_denominator": 151})),
            ("remove-a-real-original-suite",
             lambda x: x["original_oracle"]["source_ordered_suites"].pop()),
            ("replace-historical-141-146-history",
             lambda x: x["published_v26_history"].update(
                 {"evidence_owner_count": 139})),
            ("replace-current-143-148-overview-history",
             lambda x: x["published_v27_history"].update(
                 {"evidence_owner_count": 141})),
            ("hide-corrected-zig-loss-from-current-overview",
             lambda x: x["published_v27_history"].update(
                 {"actual_repaired_zig_semantic_mismatch_count": 0})),
            ("hide-real-zig-preflight",
             lambda x: x["preserved_actual_zig_preflight_failure"].update(
                 {"actual_controller_exit_status": 0})),
            ("invent-failed-zig-worker",
             lambda x: x["preserved_actual_zig_preflight_failure"].update(
                 {"actual_candidate_workers": 1})),
            ("erase-corrected-zig-original-matching-failure",
             lambda x: x["preserved_actual_zig_corrected_original_campaign"]
             .update({"semantic_mismatch_count": 0})),
            ("falsely-qualify-corrected-zig",
             lambda x: x["preserved_actual_zig_corrected_original_campaign"]
             .update({"candidate_qualified": True})),
            ("inflate-corrected-zig-archive-in-source-verification",
             lambda x: x["preserved_actual_zig_corrected_original_campaign"]
             .update({"source_verification_inflates_archive": True})),
            ("omit-repaired-rust-public-adapter",
             lambda x: x["actual_rust_v11_source_build"][
                 "repaired_source_owners"].pop(0)),
            ("omit-repaired-rust-bridge-source",
             lambda x: x["actual_rust_v11_source_build"][
                 "repaired_source_owners"].pop(1)),
            ("use-only-one-native-role",
             lambda x: x["actual_rust_v11_source_build"]["native_roles"].pop()),
            ("omit-a-real-original-target",
             lambda x: x["four_original_target_owners"].pop()),
            ("replace-hardlink-with-copied-bytes",
             lambda x: x["recovery_policy"].update(
                 {"original_inode_backup": "BYTE COPY"})),
            ("falsely-claim-four-file-group-atomicity",
             lambda x: x["recovery_policy"].update({"group_atomic": True})),
            ("skip-nested-rust-source-rebinding",
             lambda x: x["original_oracle"].update(
                 {"rebind_all_fresh_nested_interpreters": False})),
            ("dispatch-obsolete-v3-activation",
             lambda x: x["original_oracle"].update(
                 {"v3_legacy_activation_dispatch_invoked": True})),
            ("run-v2-go-or-cpp-matching",
             lambda x: x["lossless_v2_publication"].update(
                 {"matching_runner_invoked": True})),
            ("publish-before-restoring-four-original-inodes",
             lambda x: x["publication_policy"].update(
                 {"publish_only_after_all_four_original_inodes_restored": False})),
            ("invent-candidate-pass",
             lambda x: x["source_only_effects"].update(
                 {"candidate_correctness": "PASS", "candidate_qualified": True})),
            ("open-the-sealed-final-holdout",
             lambda x: x["source_only_effects"].update({"holdout": "OPENED"})),
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
            ("native", lambda: ctypes.CDLL("foreign.so")),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("import", lambda: importlib.import_module(
                "candidates.rust_candidate")),
        )
        for name, action in controls:
            reject("block-real-" + name, action)
        blocked = dict(wall.blocked)
    require(len(accepted) >= 19 and all(value > 0 for value in blocked.values()),
            "require every positive and independently blocked effect control")
    return {
        "schema": SCHEMA + "-synthetic-self-test", "status": "PASS",
        "version": 2, "family": FAMILY, "mode": "SYNTHETIC SOURCE ONLY",
        "accepted_control_count": len(accepted), "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_effects_by_kind": blocked,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "published_v26_evidence_owner_count": 141,
        "published_v26_authenticated_reference_count": 146,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "actual_rust_build_process_count": 28,
        "actual_rust_source_owner_count": 9,
        "actual_rust_source_overlay_count": 4,
        "original_canonical_target_count": 4,
        "restoration_order": list(RESTORATION_ORDER),
        "actual_zig_preflight_exit_status": 1,
        "actual_zig_preflight_candidate_workers": 0,
        "actual_zig_corrected_candidate_status": "FAIL",
        "actual_zig_corrected_candidate_workers": 13,
        "actual_zig_corrected_completed_suite_count": 13,
        "actual_zig_corrected_semantic_mismatch_count": 2172,
        "actual_zig_corrected_verified_passing_case_count": 2847,
        "actual_zig_corrected_infrastructure_failure_count": 0,
        "actual_zig_corrected_archive_inflated": False,
        **source_effects(),
    }


def validate_rust_build(owners: dict[str, bytes]) -> dict[str, Any]:
    compressed = owners[RUST_BUILD["archive"][0]]
    receipt = strict_document(owners[RUST_BUILD["receipt"][0]],
                              "actual Rust V11 durable receipt")
    require(sha256(compressed) == RUST_BUILD["archive"][1]
            and len(compressed) == RUST_BUILD["archive"][2],
            "require the actual independently published Rust archive")
    try:
        expanded = gzip.decompress(compressed)
    except (OSError, EOFError, ValueError) as error:
        raise CampaignError("reject the invalid actual Rust archive") from error
    report = strict_document(expanded, "actual dual-overlay Rust build")
    require(report.get("schema")
            == "rebar-phase2-owned-native-source-build-v11-actual-dual-overlay-build"
            and report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("label") == BUILD_LABEL
            and report.get("source_sha256") == RUST_BUILD["source"][1]
            and report.get("protocol_sha256") == RUST_BUILD["protocol"][1]
            and report.get("contract_sha256") == RUST_BUILD["contract"][1]
            and report.get("historical_evidence_owner_count") == 137
            and report.get("historical_authenticated_reference_count") == 142
            and report.get("phase_count") == 2
            and report.get("actual_compiler_process_count") == 28
            and report.get("bridge_overlay_apply_count") == 2
            and report.get("public_overlay_apply_count") == 2,
            "preserve the authentic Rust V11 dual-overlay build and history")
    require(receipt.get("schema")
            == "rebar-phase2-owned-native-source-build-v11-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("archive_sha256") == sha256(compressed)
            and receipt.get("archive_bytes") == len(compressed)
            and receipt.get("uncompressed_sha256") == sha256(expanded)
            and receipt.get("uncompressed_bytes") == len(expanded)
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("source_sha256") == RUST_BUILD["source"][1]
            and receipt.get("protocol_sha256") == RUST_BUILD["protocol"][1]
            and receipt.get("contract_sha256") == RUST_BUILD["contract"][1],
            "require the separate authentic durable Rust build receipt")
    processes = report.get("compiler_processes")
    require(type(processes) is list and len(processes) == 28
            and {item.get("name") for item in processes} == COMPILER_ROLES
            and len({item.get("pid") for item in processes}) == 28
            and all(type(item.get("pid")) is int and item["pid"] > 0
                    and item.get("exit_status") == 0
                    and item.get("shell") is False
                    for item in processes),
            "preserve all actual twenty-eight distinct Rust build processes")
    phases = report.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "require both genuinely independently produced Rust phases")
    selected: dict[str, Any] | None = None
    for expected_name, phase in zip(("reference-a", "reference-b"),
                                    phases, strict=True):
        require(type(phase) is dict and phase.get("name") == expected_name,
                "reject a renamed or missing independent Rust phase")
        sources = phase.get("fresh_source_owners")
        require(type(sources) is dict
                and set(sources) == {item[0] for item in REPAIRED_SOURCE_OWNERS},
                "require all nine actual repaired Rust source owners")
        for relative, digest, size in REPAIRED_SOURCE_OWNERS:
            owner = sources[relative]
            require(type(owner) is dict
                    and owner.get("sha256") == digest
                    and owner.get("bytes") == size,
                    "reject a changed Rust phase source: " + relative)
        for role, expected_hash, expected_size in (
            ("engine", ENGINE_SHA256, ENGINE_BYTES),
            ("bridge", BRIDGE_SHA256, BRIDGE_BYTES),
        ):
            item = phase.get("native_outputs", {}).get(role)
            require(type(item) is dict and item.get("role") == role
                    and item.get("family") == FAMILY
                    and item.get("sha256") == expected_hash
                    and item.get("size_bytes") == expected_size
                    and item.get("candidate_imported") is False
                    and item.get("prebuilt_artifact_read") is False,
                    "require the authentic V11 phase native role: " + role)
            audit = item.get("audit")
            require(type(audit) is dict
                    and audit.get("external_regex_dependency_count") == 0
                    and audit.get("cross_family_dependency_count") == 0
                    and (role != "bridge" or
                         (audit.get("runpath") == ["$ORIGIN"]
                          and "_rust_engine.so" in audit.get("needed", []))),
                    "reject an external, substituted, or delegated Rust matcher")
        public = sources["candidates/rust_candidate.py"]
        bridge = sources["candidates/rust/py_bridge.c"]
        require(public.get("source_overlay", {}).get("status") == "PASS"
                and public["source_overlay"].get("source_apply_count") == 1
                and public["source_overlay"].get("derived_source_sha256")
                == REPAIRED_SOURCE_OWNERS[0][1]
                and bridge.get("source_overlay", {}).get("status") == "PASS"
                and bridge["source_overlay"].get("source_apply_count") == 1
                and bridge["source_overlay"].get("derived_sha256")
                == REPAIRED_SOURCE_OWNERS[1][1],
                "preserve each real first-party Rust source repair application")
        if selected is None:
            selected = phase
    reproducible = report.get("reproducibility")
    require(type(reproducible) is dict
            and reproducible.get("status") == "PASS"
            and reproducible.get("byte_identical") is True
            and reproducible.get("independent_fresh_phase_count") == 2
            and reproducible.get("source_owners_per_phase") == 9
            and reproducible.get("prebuilt_artifact_count") == 0
            and reproducible.get("original_sources_modified") is False,
            "reject an unproven or prebuilt Rust dual-overlay artifact")
    require(selected is not None, "select an authentic Rust source phase")
    return {"report": report, "receipt": receipt, "phase": selected}


def validate_zig_failure(owners: dict[str, bytes]) -> dict[str, Any]:
    compressed = owners[ZIG_FAILURE["archive"][0]]
    receipt = strict_document(owners[ZIG_FAILURE["receipt"][0]],
                              "preserved Zig preflight durable receipt")
    try:
        plain = gzip.decompress(compressed)
    except (OSError, EOFError, ValueError) as error:
        raise CampaignError("reject the real archived Zig failure") from error
    failure = strict_document(plain, "genuine preserved Zig preflight")
    require(failure.get("schema")
            == "rebar-owned-zig-campaign-preflight-failure-v1-actual-preserved-infrastructure-failure"
            and failure.get("status") == "FAIL"
            and failure.get("failure_class")
            == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
            and failure.get("actual_candidate_workers") == 0
            and failure.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("schema")
            == "rebar-owned-zig-campaign-preflight-failure-v1-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("actual_observed_controller_exit_status") == 1
            and receipt.get("actual_observed_controller_process_id")
            == "NOT RECORDED"
            and receipt.get("actual_candidate_workers") == 0
            and receipt.get("actual_native_activations") == 0
            and receipt.get("uncompressed_sha256") == sha256(plain)
            and receipt.get("uncompressed_bytes") == len(plain),
            "never erase, rewrite, or qualify the actual Zig preflight failure")
    return {"report": failure, "receipt": receipt}


def validate_zig_corrected_campaign(
        owners: dict[str, bytes]) -> dict[str, Any]:
    """Check the exact real Zig receipt without inflating its 198 MiB stream."""
    compressed = owners[ZIG_CORRECTED_CAMPAIGN["archive"][0]]
    require(type(compressed) is bytes
            and len(compressed) == ZIG_CORRECTED_CAMPAIGN["archive"][2]
            and sha256(compressed) == ZIG_CORRECTED_CAMPAIGN["archive"][1],
            "authenticate all genuine corrected Zig compressed failure bytes")
    receipt = strict_document(
        owners[ZIG_CORRECTED_CAMPAIGN["receipt"][0]],
        "actual separately durable corrected Zig original failure receipt")
    archive = receipt.get("archive")
    require(type(archive) is dict
            and archive.get("sha256")
            == ZIG_CORRECTED_CAMPAIGN["archive"][1]
            and archive.get("size_bytes")
            == ZIG_CORRECTED_CAMPAIGN["archive"][2]
            and archive.get("relative")
            == ZIG_CORRECTED_CAMPAIGN["archive"][0].rsplit("/", 1)[1]
            and archive.get("device") == 2064
            and archive.get("inode") == 524614
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("streaming_readback_verified") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True,
            "reject substituted or nondurable corrected Zig loss evidence")
    first_archive = receipt.get("actual_first_v1_failure_archive")
    first_receipt = receipt.get("actual_first_v1_failure_receipt")
    require(type(first_archive) is dict and type(first_receipt) is dict
            and first_archive.get("path") == ZIG_FAILURE["archive"][0]
            and first_archive.get("sha256") == ZIG_FAILURE["archive"][1]
            and first_archive.get("bytes") == ZIG_FAILURE["archive"][2]
            and first_receipt.get("path") == ZIG_FAILURE["receipt"][0]
            and first_receipt.get("sha256") == ZIG_FAILURE["receipt"][1]
            and first_receipt.get("bytes") == ZIG_FAILURE["receipt"][2],
            "preserve the genuine separate zero-worker Zig preflight failure")
    require(receipt.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("family") == "zig"
            and receipt.get("label") == "phase2-v11-zig-scanner-original-p0"
            and receipt.get("actual_candidate_workers") == 13
            and receipt.get("completed_suite_count") == 13
            and receipt.get("suite_count") == 13
            and receipt.get("case_execution_denominator") == 31237
            and receipt.get("named_private_waiver_count") == 13
            and receipt.get("semantic_mismatch_count") == 2172
            and receipt.get("verified_passing_case_count") == 2847
            and receipt.get("infrastructure_failure_count") == 0
            and receipt.get("all_original_suite_streams_retained") is True
            and receipt.get("original_native_restored") is True
            and receipt.get("restoration_verified_before_publication")
            is True
            and receipt.get("candidate_qualified") is False
            and receipt.get("uncompressed_bytes") == 198178404
            and receipt.get("uncompressed_sha256")
            == "c6bb2272f13595fc65a4d83feed12f10412706819962b0c18ba96c2ee01d68ce"
            and receipt.get("actual_first_v1_attempt_status") == "FAIL"
            and receipt.get("actual_first_v1_candidate_workers") == 0
            and receipt.get("actual_first_v1_matching_case_execution_count")
            == 0
            and receipt.get("published_v26_evidence_owner_count") == 141
            and receipt.get("published_v26_authenticated_reference_count")
            == 146
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("benchmark_files_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("winner_selected") is False,
            "retain every real corrected Zig mismatch without qualification")
    return {"receipt": receipt,
            "compressed_sha256": sha256(compressed),
            "compressed_bytes": len(compressed),
            "archive_inflated": False}


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None,
                   *, retain: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    checked_digest(source_pin, "Rust campaign source")
    checked_digest(protocol_pin, "Rust campaign protocol")
    _, source = _read_owned(str(ROOT), SOURCE_RELATIVE, source_pin)
    _, protocol = _read_owned(str(ROOT), PROTOCOL_RELATIVE, protocol_pin)
    stored: dict[str, bytes] = {}
    support_owners: dict[str, dict[str, Any]] = {}
    groups = (PRODUCER, PUBLICATION, RUST_BUILD, RUST_BRIDGE_REPAIR,
              RUST_PUBLIC_REPAIR, V26, V27, ZIG_FAILURE,
              ZIG_CORRECTED_CAMPAIGN)
    for group in groups:
        for item in group.values():
            if item[0] in stored:
                continue
            raw, owner = read_owner(item)
            stored[item[0]] = raw
            support_owners[item[0]] = owner
    for item in (GOAL, PHASE_ONE):
        raw, owner = read_owner(item)
        stored[item[0]] = raw
        support_owners[item[0]] = owner
    historical_graph = strict_document(
        stored[V26["summary"][0]],
        "separately preserved historical V26 overview")
    historical_inputs = strict_document(
        stored[V26["inputs"][0]],
        "separately preserved historical V26 overview inputs")
    require(historical_graph.get("schema")
            == "rebar-candidate-current-overview-v26-summary"
            and historical_graph.get("status") == "PASS"
            and historical_graph.get("repository_evidence_owner_count") == 141
            and historical_graph.get("authenticated_digest_addressed_history_paths")
            == 146
            and historical_graph.get("full_case_denominator") == 31237
            and historical_graph.get("suite_count") == 13
            and historical_graph.get("private_waiver_count") == 13
            and historical_graph.get("qualified_candidate_count") == 0
            and historical_graph.get("rust_historical_semantic_mismatch_count")
            == 2042
            and historical_graph.get("rust_dual_overlay_repaired_build_process_count")
            == 28
            and historical_graph.get("rust_dual_overlay_repaired_matching_test_status")
            == "NOT MEASURED"
            and historical_graph.get("c_repaired_semantic_mismatch_count")
            == 1262
            and historical_graph.get("c_repaired_verified_passing_case_count")
            == 7325
            and historical_graph.get("final_holdout_opened") is False
            and historical_graph.get("performance") == "NOT MEASURED",
            "preserve the genuine historical V26 overview without revision")
    require(historical_inputs.get("repository_evidence_owner_count") == 141
            and historical_inputs.get("all_digest_addressed_history_path_count")
            == 146
            and historical_inputs.get("full_case_denominator") == 31237
            and historical_inputs.get("private_waiver_count") == 13
            and historical_inputs.get("candidate_qualified_count") == 0,
            "preserve the separately authenticated 141/146 V26 history")
    graph = strict_document(stored[V27["summary"][0]],
                            "current independently published V27 overview")
    graph_inputs = strict_document(stored[V27["inputs"][0]],
                                   "current independently published V27 inputs")
    require(graph.get("schema")
            == "rebar-candidate-current-overview-v27-summary"
            and graph.get("status") == "PASS"
            and graph.get("repository_evidence_owner_count") == 143
            and graph.get("authenticated_digest_addressed_history_paths") == 148
            and graph.get("full_case_denominator") == 31237
            and graph.get("suite_count") == 13
            and graph.get("private_waiver_count") == 13
            and graph.get("qualified_candidate_count") == 0
            and graph.get("rust_historical_semantic_mismatch_count") == 2042
            and graph.get("rust_dual_overlay_repaired_build_process_count") == 28
            and graph.get("rust_dual_overlay_repaired_matching_test_status")
            == "NOT MEASURED"
            and graph.get("c_repaired_semantic_mismatch_count") == 1262
            and graph.get("c_repaired_verified_passing_case_count") == 7325
            and graph.get("preserved_v26_repository_evidence_owner_count")
            == 141
            and graph.get("preserved_v26_authenticated_reference_path_count")
            == 146
            and graph.get("new_zig_original_campaign_repository_evidence_owner_count")
            == 2
            and graph.get("zig_original_campaign_status") == "FAIL"
            and graph.get("zig_original_campaign_receipt_status") == "PASS"
            and graph.get("zig_original_campaign_receipt_pass_means")
            == "DURABLE FAILURE PUBLICATION ONLY"
            and graph.get("zig_original_campaign_candidate_worker_count")
            == 13
            and graph.get("zig_original_campaign_completed_suite_count")
            == 13
            and graph.get("zig_original_campaign_case_execution_denominator")
            == 31237
            and graph.get("zig_original_campaign_semantic_mismatch_count")
            == 2172
            and graph.get("zig_original_campaign_verified_passing_case_count")
            == 2847
            and graph.get("zig_original_campaign_infrastructure_failure_count")
            == 0
            and graph.get("zig_original_campaign_original_targets_restored")
            is True
            and graph.get("uncompressed_zig_archive_opened_by_graph") is False
            and graph.get("uncompressed_zig_archive_bytes_read_by_graph") == 0
            and graph.get("final_holdout_opened") is False
            and graph.get("performance") == "NOT MEASURED",
            "reject a stale V27 overview, concealed loss or invented Rust result")
    require(graph_inputs.get("repository_evidence_owner_count") == 143
            and graph_inputs.get("all_digest_addressed_history_path_count") == 148
            and graph_inputs.get("full_case_denominator") == 31237
            and graph_inputs.get("private_waiver_count") == 13
            and graph_inputs.get("candidate_qualified_count") == 0
            and graph_inputs.get("preserved_v26_repository_evidence_owner_count")
            == 141
            and graph_inputs.get("new_zig_original_campaign_repository_evidence_owner_count")
            == 2
            and graph_inputs.get("actual_zig_candidate_workers") == 13
            and graph_inputs.get("actual_zig_completed_suite_count") == 13
            and graph_inputs.get("actual_zig_semantic_mismatch_count") == 2172
            and graph_inputs.get("actual_zig_verified_passing_case_count")
            == 2847
            and graph_inputs.get("actual_zig_infrastructure_failure_count")
            == 0
            and graph_inputs.get("uncompressed_zig_archive_opened_by_graph")
            is False
            and graph_inputs.get("uncompressed_zig_archive_bytes_read_by_graph")
            == 0,
            "authenticate the actual current 143/148 V27 input graph")
    producer_contract = strict_document(
        stored[PRODUCER["contract"][0]],
        "unchanged original V3 six-family producer")
    require(producer_contract.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and producer_contract.get("version") == 3
            and producer_contract.get("suite_count") == SUITE_COUNT
            and producer_contract.get("case_execution_denominator") == CASE_COUNT,
            "preserve the exact complete original V3 producer")
    recorded_rust = next(
        (item for item in producer_contract.get("families", [])
         if type(item) is dict and item.get("family") == FAMILY), None)
    require(type(recorded_rust) is dict
            and recorded_rust.get("combined_native_engine_and_bridge") is False
            and recorded_rust.get("owned_ctypes_allowed") is False
            and len(recorded_rust.get("sources", [])) == 9
            and tuple((x["relative"], x["sha256"], x["size_bytes"])
                      for x in recorded_rust["sources"])
            == ORIGINAL_RUST_SOURCE_OWNERS,
            "preserve all nine immutable original Rust semantic owners")
    source_order = producer_contract.get("suites", [])
    require(type(source_order) is list
            and [(x.get("id"), x.get("case_execution_count"))
                 for x in source_order] == list(SUITES),
            "preserve every original suite, denominator and order")
    suite_owners = {}
    for item in source_order:
        relative = checked_relative(item.get("source_relative"))
        expected = checked_digest(item.get("source_sha256"), relative)
        raw, owner = _read_owned(str(ROOT), relative, expected)
        require(type(raw) is bytes, "require the actual immutable suite source")
        suite_owners[relative] = owner
    phase_one = strict_document(stored[PHASE_ONE[0]], "unchanged P0")
    require(phase_one.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and len(source_order) == 13,
            "keep the original frozen correctness oracle")
    build = validate_rust_build(stored)
    failure = validate_zig_failure(stored)
    corrected_zig = validate_zig_corrected_campaign(stored)
    publication_contract = strict_document(
        stored[PUBLICATION["contract"][0]],
        "unchanged lossless original-campaign publication")
    require(publication_contract.get("version") == 2,
            "authenticate only the genuine V2 lossless writer")
    producer = load_frozen(PRODUCER["source"], "original_v3_producer")
    publication = load_frozen(PUBLICATION["source"], "v2_lossless_writer")
    require(tuple((item.name, item.case_count)
                  for item in producer.SUITES) == SUITES
            and producer.OWNED_SOURCES["rust"] == ORIGINAL_RUST_SOURCE_OWNERS
            and all(callable(getattr(producer, name, None))
                    for name in ("observe_original_upstream",
                                 "observe_direct_suite",
                                 "observe_subinterpreters",
                                 "interpreter_bootstrap_source",
                                 "family_spec"))
            and all(callable(getattr(publication, name, None))
                    for name in ("open_evidence_directory",
                                 "write_streamed_archive",
                                 "stream_canonical_gzip")),
            "reuse exact original observers and V2 streaming publication only")
    frozen_owner = None
    if contract_pin is not None:
        checked_digest(contract_pin, "Rust campaign machine contract")
        raw, frozen_owner = _read_owned(str(ROOT), CONTRACT_RELATIVE,
                                        contract_pin)
        validate_contract(strict_document(raw, "canonical Rust campaign"),
                          source_pin, protocol_pin)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "source verification may not import a native candidate")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": 2, "family": FAMILY,
        "mode": "READ-ONLY ACTUAL DUAL-OVERLAY RUST SOURCE FREEZE",
        "source": source, "protocol": protocol, "contract": frozen_owner,
        "authenticated_support_owner_count": len(support_owners),
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "unchanged_original_suite_source_owner_count": len(suite_owners),
        "published_v26_evidence_owner_count": 141,
        "published_v26_authenticated_reference_count": 146,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "actual_rust_build_process_count": 28,
        "actual_rust_build_phase_count": 2,
        "actual_rust_bridge_source_repair_count": 2,
        "actual_rust_public_source_repair_count": 2,
        "actual_rust_source_owner_count": 9,
        "original_canonical_target_count": 4,
        "original_target_inodes": [
            ROLES[role]["original"]["inode"] for role in ROLE_ORDER],
        "restoration_order": list(RESTORATION_ORDER),
        "v3_legacy_activation_dispatch_invoked": False,
        "v2_candidate_matching_invoked": False,
        "rust_only_nested_source_rebinding": True,
        "nested_case_count": 128, "nested_interpreter_event_count": 394,
        "nested_interpreters_created": 11,
        "actual_zig_preflight_exit_status": 1,
        "actual_zig_preflight_candidate_workers": 0,
        "actual_zig_corrected_candidate_status": "FAIL",
        "actual_zig_corrected_candidate_workers": 13,
        "actual_zig_corrected_completed_suite_count": 13,
        "actual_zig_corrected_semantic_mismatch_count": 2172,
        "actual_zig_corrected_verified_passing_case_count": 2847,
        "actual_zig_corrected_infrastructure_failure_count": 0,
        "actual_zig_corrected_archive_inflated": False,
        "actual_c_candidate_workers": 13,
        "actual_c_semantic_mismatch_count": 1262,
        "historical_rust_semantic_mismatch_count": 2042,
        "group_atomic": False,
        **source_effects(),
    }
    kept = {
        "producer": producer, "publication": publication,
        "phase_one": phase_one, "build": build,
        "zig_failure": failure, "zig_corrected_campaign": corrected_zig,
        "support": support_owners,
    } if retain else {}
    return result, kept


def checked_private_root(value: Any) -> str:
    require(type(value) is str
            and value.startswith("/tmp/" + PRIVATE_PREFIX)
            and len(value.split("/")) == 3
            and value == value.rstrip("/")
            and "\x00" not in value and "\\" not in value,
            "accept only one exact owner-only Rust campaign root")
    return value


def private_directory(root: str) -> int:
    checked_private_root(root)
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_DIRECTORY", 0))
    descriptor = os.open(root, flags)
    actual = os.fstat(descriptor)
    require(stat.S_ISDIR(actual.st_mode)
            and stat.S_IMODE(actual.st_mode) == 0o700
            and actual.st_uid == os.geteuid(),
            "open only the genuinely owner-only Rust journal directory")
    return descriptor


def write_private(root: str, name: str,
                  document: dict[str, Any]) -> dict[str, Any]:
    checked_private_root(root)
    require(type(name) is str and "/" not in name and bool(name),
            "write only a fixed private journal basename")
    raw = canonical(document)
    directory = private_directory(root)
    descriptor: int | None = None
    try:
        descriptor = os.open(
            name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600, dir_fd=directory)
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1
                and first.st_uid == os.geteuid()
                and stat.S_IMODE(first.st_mode) == 0o600,
                "create only exclusive owner-only private evidence")
        offset = 0
        while offset < len(raw):
            amount = os.write(descriptor, raw[offset:])
            require(type(amount) is int and amount > 0,
                    "reject incomplete durable private control")
            offset += amount
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        require((first.st_dev, first.st_ino) == (final.st_dev, final.st_ino)
                and final.st_size == len(raw)
                and final.st_nlink == 1,
                "reject a swapped or partial private control inode")
        os.close(descriptor)
        descriptor = None
        os.fsync(directory)
        recorded, owner = _read_owned(
            root, name, sha256(raw), exact_size=len(raw),
            maximum=MAX_ARCHIVE_BYTES, private=True)
        require(recorded == raw,
                "require complete same-inode durable private readback")
        owner.update({
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
        })
        return owner
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def open_target_parent(relative: str) -> tuple[int, int, str]:
    checked_relative(relative)
    require(relative in {item["relative"] for item in ROLES.values()},
            "never open another candidate's source or native file")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_DIRECTORY", 0))
    base = os.open(str(ROOT), flags)
    parent = os.dup(base)
    try:
        for part in relative.split("/")[:-1]:
            next_parent = os.open(part, flags, dir_fd=parent)
            os.close(parent)
            parent = next_parent
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a redirected Rust canonical parent")
        return base, parent, relative.rsplit("/", 1)[-1]
    except BaseException:
        os.close(parent)
        os.close(base)
        raise


def same_original(owner: dict[str, Any],
                  expected: dict[str, Any]) -> bool:
    return (type(owner) is dict
            and owner.get("relative") == expected["relative"]
            and owner.get("sha256") == expected["sha256"]
            and owner.get("size_bytes") == expected["bytes"]
            and owner.get("device") == expected["device"]
            and owner.get("inode") == expected["inode"]
            and owner.get("mode") == expected["mode"]
            and owner.get("uid") == expected["uid"]
            and owner.get("nlink") == expected["nlink"])


def current_original(role: str) -> dict[str, Any]:
    require(role in ROLES, "select one authentic Rust original")
    target = ROLES[role]["original"]
    _, owner = _read_owned(
        str(ROOT), target["relative"], target["sha256"],
        exact_size=target["bytes"], maximum=MAX_BINARY_BYTES,
        allow_canonical_target=True)
    require(same_original(owner, target),
            "refuse a replaced, linked, modified, or foreign original: " + role)
    return owner


def exact_originals() -> dict[str, dict[str, Any]]:
    return {role: current_original(role) for role in ROLE_ORDER}


def read_recorded_phase(phase: dict[str, Any],
                        role: str) -> bytes:
    require(role in ROLE_ORDER and phase.get("name") == "reference-a",
            "read only the exact actual first independently built Rust phase")
    if role in ("adapter", "bridge_source"):
        relative = ROLES[role]["relative"]
        recorded = phase["fresh_source_owners"][relative]
        overlay = recorded.get("source_overlay", {})
        root = overlay.get("snapshot_root")
        require(type(root) is str
                and root.startswith(
                    "/tmp/rebar-phase2-native-build-v9-rust-")
                and root.endswith("/reference-a/source"),
                "reject a substituted Rust private source phase")
        phase_relative = relative
    else:
        recorded = phase["native_outputs"][role]
        public = phase["fresh_source_owners"][
            "candidates/rust_candidate.py"]["source_overlay"]
        source_root = public.get("snapshot_root")
        require(type(source_root) is str
                and source_root.startswith(
                    "/tmp/rebar-phase2-native-build-v9-rust-")
                and source_root.endswith("/reference-a/source"),
                "reject an unproven actual Rust phase root")
        root = source_root.removesuffix("/source") + "/native"
        phase_relative = ROLES[role]["relative"].rsplit("/", 1)[-1]
    require(recorded.get("sha256") == ROLES[role]["sha256"]
            and recorded.get("bytes", recorded.get("size_bytes"))
            == ROLES[role]["bytes"],
            "pin the exact authenticated actual Rust build phase")
    raw, owner = _read_owned(
        root, phase_relative, ROLES[role]["sha256"],
        exact_size=ROLES[role]["bytes"],
        maximum=MAX_BINARY_BYTES)
    require(owner["device"] == recorded.get("device")
            and owner["inode"] == recorded.get("inode"),
            "reject a changed actual Rust source-phase inode: " + role)
    return raw


def role_target_names(token: str, role: str) -> tuple[str, str]:
    require(type(token) is str and len(token) == 32
            and all(x in "0123456789abcdef" for x in token)
            and role in ROLE_ORDER,
            "require one unpredictable genuine four-role journal token")
    base = ROLES[role]["relative"].rsplit("/", 1)[-1]
    return (
        ".rebar-rust-v2-original-" + token + "-" + base,
        ".rebar-rust-v2-stage-" + token + "-" + base,
    )


def ensure_absent(directory: int, name: str) -> None:
    require(type(name) is str and "/" not in name and bool(name),
            "check only one exact adjacent Rust basename")
    try:
        os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise CampaignError("never overwrite existing user-owned staging: " + name)


def sync_directory(directory: int, expected: os.stat_result) -> None:
    os.fsync(directory)
    actual = os.fstat(directory)
    require(stat.S_ISDIR(actual.st_mode)
            and (actual.st_dev, actual.st_ino)
            == (expected.st_dev, expected.st_ino),
            "reject an exchanged canonical Rust directory")


def write_stage(directory: int, name: str,
                payload: bytes, mode: int) -> dict[str, Any]:
    ensure_absent(directory, name)
    descriptor = os.open(
        name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        0o600, dir_fd=directory)
    try:
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1
                and first.st_uid == os.geteuid()
                and stat.S_IMODE(first.st_mode) == 0o600,
                "create one exclusive no-follow Rust source or native stage")
        offset = 0
        while offset < len(payload):
            count = os.write(descriptor, payload[offset:])
            require(type(count) is int and count > 0,
                    "reject a truncated source or native stage")
            offset += count
        if mode != 0o600:
            os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        require((first.st_dev, first.st_ino)
                == (final.st_dev, final.st_ino)
                and final.st_size == len(payload)
                and final.st_nlink == 1
                and stat.S_IMODE(final.st_mode) == mode,
                "reject changed, linked or incorrectly moded stage")
        return {"sha256": sha256(payload), "size_bytes": len(payload),
                "device": final.st_dev, "inode": final.st_ino,
                "mode": mode, "uid": final.st_uid, "nlink": 1,
                "filename": name}
    finally:
        os.close(descriptor)


def read_private(root: str, name: str,
                 expected: str | None = None) -> tuple[dict[str, Any],
                                                        dict[str, Any]]:
    checked_private_root(root)
    require(type(name) is str and "/" not in name,
            "read only a literal Rust private control")
    if expected is None:
        descriptor = private_directory(root)
        try:
            found = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            require(stat.S_ISREG(found.st_mode)
                    and stat.S_IMODE(found.st_mode) == 0o600
                    and found.st_uid == os.geteuid()
                    and found.st_nlink == 1,
                    "authenticate a genuine private control owner")
            handle = os.open(name, os.O_RDONLY
                             | getattr(os, "O_NOFOLLOW", 0)
                             | getattr(os, "O_CLOEXEC", 0),
                             dir_fd=descriptor)
            try:
                first = os.fstat(handle)
                pieces: list[bytes] = []
                remain = first.st_size
                while remain:
                    piece = os.read(handle, min(remain, 1024 * 1024))
                    require(bool(piece), "reject a truncated private control")
                    pieces.append(piece)
                    remain -= len(piece)
                raw = b"".join(pieces)
                last = os.fstat(handle)
                require((first.st_dev, first.st_ino, first.st_size,
                         first.st_mtime_ns, first.st_ctime_ns)
                        == (last.st_dev, last.st_ino, last.st_size,
                            last.st_mtime_ns, last.st_ctime_ns),
                        "reject a changed private control")
            finally:
                os.close(handle)
        finally:
            os.close(descriptor)
        expected = sha256(raw)
    raw, owner = _read_owned(root, name, expected,
                             maximum=MAX_ARCHIVE_BYTES, private=True)
    return strict_document(raw, name), owner


def stage_four_roles(kept: dict[str, Any],
                     source_pin: str, protocol_pin: str,
                     contract_pin: str) -> dict[str, Any]:
    originals = exact_originals()
    payloads = {
        role: read_recorded_phase(kept["build"]["phase"], role)
        for role in ROLE_ORDER
    }
    root = tempfile.mkdtemp(prefix=PRIVATE_PREFIX, dir="/tmp")
    checked_private_root(root)
    private_fd = private_directory(root)
    os.close(private_fd)
    token = os.urandom(16).hex()
    entries = {}
    for role in ROLE_ORDER:
        backup, stage = role_target_names(token, role)
        entries[role] = {
            "role": role, "relative": ROLES[role]["relative"],
            "original": dict(ROLES[role]["original"]),
            "backup_filename": backup, "stage_filename": stage,
            "repaired_sha256": ROLES[role]["sha256"],
            "repaired_bytes": ROLES[role]["bytes"],
        }
    journal = {
        "schema": JOURNAL_SCHEMA, "status": "PREPARED",
        "version": 2, "family": FAMILY, "label": LABEL,
        "activation_root": root,
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "build_archive_sha256": RUST_BUILD["archive"][1],
        "build_receipt_sha256": RUST_BUILD["receipt"][1],
        "roles": entries, "role_order": list(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "group_atomic": False,
        "exact_original_inode_backup": "ADJACENT SAME-DIRECTORY HARDLINK",
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
    }
    journal_owner = write_private(root, "recovery-journal.json", journal)
    try:
        for role in ROLE_ORDER:
            original = current_original(role)
            require(same_original(original, ROLES[role]["original"]),
                    "refuse an original target changed after journaling")
            entry = entries[role]
            base, directory, filename = open_target_parent(entry["relative"])
            try:
                before = os.fstat(directory)
                ensure_absent(directory, entry["backup_filename"])
                ensure_absent(directory, entry["stage_filename"])
                link_intent = {
                    "schema": INTENTION_SCHEMA, "status": "PREPARED",
                    "operation": "HARDLINK_BACKUP", "family": FAMILY,
                    "role": role, "target": entry["relative"],
                    "activation_root": root,
                    "journal_sha256": journal_owner["sha256"],
                    "original": entry["original"],
                    "backup_filename": entry["backup_filename"],
                    "group_atomic": False,
                }
                write_private(root, "link-intent-" + role + ".json",
                              link_intent)
                os.link(filename, entry["backup_filename"],
                        src_dir_fd=directory, dst_dir_fd=directory,
                        follow_symlinks=False)
                actual = os.stat(filename, dir_fd=directory,
                                 follow_symlinks=False)
                backup = os.stat(entry["backup_filename"],
                                 dir_fd=directory, follow_symlinks=False)
                expected = ROLES[role]["original"]
                require((actual.st_dev, actual.st_ino)
                        == (backup.st_dev, backup.st_ino)
                        == (expected["device"], expected["inode"])
                        and actual.st_nlink == 2 and backup.st_nlink == 2
                        and actual.st_uid == expected["uid"]
                        and stat.S_IMODE(actual.st_mode) == expected["mode"],
                        "preserve the genuine same-inode Rust hardlink")
                sync_directory(directory, before)
                intent = {
                    "schema": INTENTION_SCHEMA, "status": "PREPARED",
                    "operation": "PROMOTE", "family": FAMILY,
                    "role": role, "target": entry["relative"],
                    "activation_root": root,
                    "journal_sha256": journal_owner["sha256"],
                    "original": entry["original"],
                    "backup_filename": entry["backup_filename"],
                    "stage_filename": entry["stage_filename"],
                    "repaired_sha256": entry["repaired_sha256"],
                    "repaired_bytes": entry["repaired_bytes"],
                    "group_atomic": False,
                }
                write_private(root, "promotion-intent-" + role + ".json",
                              intent)
                stage = write_stage(
                    directory, entry["stage_filename"],
                    payloads[role], expected["mode"])
                require(stage["sha256"] == entry["repaired_sha256"]
                        and stage["size_bytes"] == entry["repaired_bytes"],
                        "never promote a changed actual Rust build output")
                sync_directory(directory, before)
                os.replace(entry["stage_filename"], filename,
                           src_dir_fd=directory, dst_dir_fd=directory)
                sync_directory(directory, before)
                _, promoted = _read_owned(
                    str(ROOT), entry["relative"],
                    entry["repaired_sha256"],
                    exact_size=entry["repaired_bytes"],
                    maximum=MAX_BINARY_BYTES,
                    allow_canonical_target=True)
                require(promoted["device"] == stage["device"]
                        and promoted["inode"] == stage["inode"]
                        and promoted["mode"] == expected["mode"]
                        and promoted["nlink"] == 1,
                        "prove each actual promoted Rust stage inode")
            finally:
                os.close(directory)
                os.close(base)
        targets = {}
        for role in ROLE_ORDER:
            _, targets[role] = _read_owned(
                str(ROOT), ROLES[role]["relative"],
                ROLES[role]["sha256"], exact_size=ROLES[role]["bytes"],
                maximum=MAX_BINARY_BYTES, allow_canonical_target=True)
        activation = {
            "schema": ACTIVATION_SCHEMA, "status": "PASS", "version": 2,
            "family": FAMILY, "label": LABEL, "activation_root": root,
            "journal": journal_owner, "targets": targets,
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "build_archive_sha256": RUST_BUILD["archive"][1],
            "build_receipt_sha256": RUST_BUILD["receipt"][1],
            "all_four_original_inodes_retained": True,
            "group_atomic": False,
        }
        activation_owner = write_private(
            root, "activation-report.json", activation)
        receipt = {
            "schema": ACTIVATION_RECEIPT_SCHEMA,
            "status": "PASS", "activation_status": "PASS",
            "family": FAMILY, "activation_root": root,
            "activation": activation_owner, "journal": journal_owner,
            "group_atomic": False,
        }
        receipt_owner = write_private(
            root, "activation-receipt.json", receipt)
        return {
            "root": root, "journal": journal,
            "journal_owner": journal_owner,
            "activation": activation, "activation_owner": activation_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "originals": originals,
        }
    except BaseException:
        restore_four_roles(root, journal, journal_owner["sha256"])
        raise


def restore_four_roles(root: str, journal: dict[str, Any],
                       journal_sha256: str) -> dict[str, Any]:
    checked_private_root(root)
    checked_digest(journal_sha256, "complete four-owner journal")
    require(journal.get("schema") == JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("family") == FAMILY
            and journal.get("activation_root") == root
            and journal.get("role_order") == list(ROLE_ORDER)
            and journal.get("restoration_order") == list(RESTORATION_ORDER)
            and journal.get("group_atomic") is False
            and set(journal.get("roles", {})) == set(ROLE_ORDER),
            "recover only the genuine durable four-role Rust journal")
    recorded, actual_journal = read_private(
        root, "recovery-journal.json", journal_sha256)
    require(canonical(recorded) == canonical(journal)
            and actual_journal["sha256"] == journal_sha256,
            "reauthenticate the complete original Rust recovery journal")
    restored: dict[str, dict[str, Any]] = {}
    for role in RESTORATION_ORDER:
        definition = ROLES[role]
        entry = journal["roles"][role]
        require(entry.get("role") == role
                and entry.get("relative") == definition["relative"]
                and entry.get("original") == definition["original"]
                and entry.get("repaired_sha256") == definition["sha256"]
                and entry.get("repaired_bytes") == definition["bytes"],
                "reject a substituted Rust recovery role")
        repository, directory, filename = open_target_parent(
            definition["relative"])
        try:
            before_dir = os.fstat(directory)
            try:
                current = os.stat(filename, dir_fd=directory,
                                  follow_symlinks=False)
            except FileNotFoundError as error:
                raise CampaignError(
                    "refuse a removed original Rust target: " + role
                ) from error
            require(stat.S_ISREG(current.st_mode)
                    and current.st_uid == os.geteuid(),
                    "reject a foreign or symlinked canonical Rust file")
            expected = definition["original"]
            if ((current.st_dev, current.st_ino)
                    == (expected["device"], expected["inode"])
                    and current.st_nlink == 1):
                try:
                    os.stat(entry["backup_filename"], dir_fd=directory,
                            follow_symlinks=False)
                except FileNotFoundError:
                    restored[role] = current_original(role)
                    continue
                raise CampaignError("reject an unexplained original backup")
            if ((current.st_dev, current.st_ino)
                    == (expected["device"], expected["inode"])
                    and current.st_nlink == 2):
                intent, _ = read_private(
                    root, "link-intent-" + role + ".json")
                require(intent.get("schema") == INTENTION_SCHEMA
                        and intent.get("operation") == "HARDLINK_BACKUP"
                        and intent.get("journal_sha256") == journal_sha256
                        and intent.get("role") == role
                        and intent.get("backup_filename")
                        == entry["backup_filename"],
                        "reject an unauthenticated original hardlink")
                backup = os.stat(entry["backup_filename"], dir_fd=directory,
                                 follow_symlinks=False)
                require((backup.st_dev, backup.st_ino)
                        == (expected["device"], expected["inode"])
                        and backup.st_nlink == 2,
                        "refuse an unrelated original hardlink")
                os.unlink(entry["backup_filename"], dir_fd=directory)
                sync_directory(directory, before_dir)
                restored[role] = current_original(role)
                continue
            intent, _ = read_private(
                root, "promotion-intent-" + role + ".json")
            require(intent.get("schema") == INTENTION_SCHEMA
                    and intent.get("operation") == "PROMOTE"
                    and intent.get("journal_sha256") == journal_sha256
                    and intent.get("role") == role
                    and intent.get("repaired_sha256")
                    == definition["sha256"]
                    and current.st_size == definition["bytes"]
                    and stat.S_IMODE(current.st_mode) == expected["mode"]
                    and current.st_nlink == 1,
                    "refuse changed or unjournaled Rust promoted bytes")
            _, promoted = _read_owned(
                str(ROOT), definition["relative"],
                definition["sha256"], exact_size=definition["bytes"],
                maximum=MAX_BINARY_BYTES, allow_canonical_target=True)
            require(promoted["device"] == current.st_dev
                    and promoted["inode"] == current.st_ino,
                    "never overwrite substituted user-owned Rust content")
            backup = os.stat(entry["backup_filename"], dir_fd=directory,
                             follow_symlinks=False)
            require(stat.S_ISREG(backup.st_mode)
                    and (backup.st_dev, backup.st_ino)
                    == (expected["device"], expected["inode"])
                    and backup.st_nlink == 1
                    and backup.st_uid == expected["uid"]
                    and backup.st_size == expected["bytes"]
                    and stat.S_IMODE(backup.st_mode) == expected["mode"],
                    "reject a copied, stale or modified Rust original inode")
            restoration_intention = {
                "schema": INTENTION_SCHEMA, "status": "PREPARED",
                "operation": "RESTORE", "family": FAMILY, "role": role,
                "journal_sha256": journal_sha256,
                "target": definition["relative"],
                "backup_filename": entry["backup_filename"],
                "group_atomic": False,
            }
            try:
                write_private(root, "restore-intent-" + role + ".json",
                              restoration_intention)
            except FileExistsError:
                prior_intention, _ = read_private(
                    root, "restore-intent-" + role + ".json")
                require(canonical(prior_intention)
                        == canonical(restoration_intention),
                        "retry only the exact durable Rust recovery intention")
            os.replace(entry["backup_filename"], filename,
                       src_dir_fd=directory, dst_dir_fd=directory)
            sync_directory(directory, before_dir)
            restored[role] = current_original(role)
        finally:
            os.close(directory)
            os.close(repository)
    require(set(restored) == set(ROLE_ORDER)
            and all(same_original(restored[role], ROLES[role]["original"])
                    for role in ROLE_ORDER),
            "prove exact restoration of all four original Rust inodes")
    record = {
        "schema": RESTORATION_SCHEMA, "status": "PASS",
        "version": 2, "family": FAMILY, "activation_root": root,
        "journal_sha256": journal_sha256,
        "restored_targets": restored,
        "restoration_order": list(RESTORATION_ORDER),
        "original_inodes_preserved": True,
        "group_atomic": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }
    try:
        owner = write_private(root, "restoration-receipt.json", record)
    except FileExistsError:
        prior, owner = read_private(root, "restoration-receipt.json")
        require(canonical(prior) == canonical(record),
                "reject a substituted original Rust restoration record")
    return {"report": record, "owner": owner}


def rust_family_spec(producer: types.ModuleType) -> Any:
    old = producer.family_spec(FAMILY)
    require(old.source_owners == ORIGINAL_RUST_SOURCE_OWNERS
            and producer.OWNED_SOURCES[FAMILY] == ORIGINAL_RUST_SOURCE_OWNERS,
            "reauthenticate the exact immutable original Rust policy")
    adjusted = producer.FamilySpec(
        old.name, old.module, old.adapter_relative, old.bridge_module,
        old.engine_relative, old.bridge_relative,
        REPAIRED_SOURCE_OWNERS, old.combined_native, old.owned_ctypes)
    producer.OWNED_SOURCES[FAMILY] = REPAIRED_SOURCE_OWNERS
    producer.FAMILIES[FAMILY] = adjusted
    require(producer.family_spec(FAMILY) is adjusted,
            "rebind only the exact actual repaired Rust source closure")
    original_bootstrap = producer.interpreter_bootstrap_source

    def repaired_bootstrap(spec: Any, pins: Any, source_pins: Any,
                           *, owner: str, producer_sha256: str) -> str:
        code = original_bootstrap(
            spec, pins, source_pins, owner=owner,
            producer_sha256=producer_sha256)
        marker = "_six_producer.install_owned_interpreter_guard("
        require(code.count(marker) == 1,
                "preserve the unique original interpreter guard call")
        prefix = (
            "_six_original = _six_producer.FAMILIES['rust']\n"
            "assert _six_original.name == 'rust'\n"
            "assert tuple(_six_producer.OWNED_SOURCES['rust']) == "
            + repr(ORIGINAL_RUST_SOURCE_OWNERS) + "\n"
            "_six_repaired_sources = "
            + repr(REPAIRED_SOURCE_OWNERS) + "\n"
            "_six_producer.OWNED_SOURCES['rust'] = _six_repaired_sources\n"
            "_six_producer.FAMILIES['rust'] = _six_producer.FamilySpec(\n"
            "    _six_original.name, _six_original.module,\n"
            "    _six_original.adapter_relative, _six_original.bridge_module,\n"
            "    _six_original.engine_relative, _six_original.bridge_relative,\n"
            "    _six_repaired_sources, _six_original.combined_native,\n"
            "    _six_original.owned_ctypes)\n"
            "assert _six_producer.family_spec('rust').source_owners "
            "== _six_repaired_sources\n"
        )
        final = code.replace(marker, prefix + marker, 1)
        try:
            ast.parse(final, filename="<actual-rust-original-interpreter-bootstrap>")
        except (SyntaxError, ValueError, RecursionError) as error:
            raise CampaignError(
                "reject altered original Rust interpreter bootstrap") from error
        return final

    producer.interpreter_bootstrap_source = repaired_bootstrap
    return adjusted


def same_private_owner(expected: Any, actual: dict[str, Any]) -> bool:
    return (type(expected) is dict
            and expected.get("sha256") == actual.get("sha256")
            and expected.get("device") == actual.get("device")
            and expected.get("inode") == actual.get("inode")
            and expected.get("size_bytes") == actual.get("size_bytes"))


def active_worker_approval(options: argparse.Namespace) -> dict[str, Any]:
    root = checked_private_root(options.activation_root)
    report, report_owner = read_private(
        root, "activation-report.json", options.activation_report_sha256)
    receipt, receipt_owner = read_private(
        root, "activation-receipt.json", options.activation_receipt_sha256)
    journal, journal_owner = read_private(
        root, "recovery-journal.json", options.recovery_journal_sha256)
    require(report.get("schema") == ACTIVATION_SCHEMA
            and report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("activation_root") == root
            and report.get("group_atomic") is False
            and same_private_owner(report.get("journal"), journal_owner)
            and receipt.get("schema") == ACTIVATION_RECEIPT_SCHEMA
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and same_private_owner(receipt.get("activation"), report_owner)
            and same_private_owner(receipt.get("journal"), journal_owner)
            and journal.get("schema") == JOURNAL_SCHEMA
            and journal.get("role_order") == list(ROLE_ORDER)
            and journal.get("restoration_order") == list(RESTORATION_ORDER)
            and journal.get("group_atomic") is False,
            "authenticate the actual durable four-role Rust activation")
    for role in ROLE_ORDER:
        expected = ROLES[role]
        row = journal.get("roles", {}).get(role)
        actual = report.get("targets", {}).get(role)
        require(type(row) is dict and row.get("original") == expected["original"]
                and row.get("repaired_sha256") == expected["sha256"]
                and type(actual) is dict
                and actual.get("relative") == expected["relative"]
                and actual.get("sha256") == expected["sha256"]
                and actual.get("size_bytes") == expected["bytes"],
                "prove all four real original and active Rust owners")
    return {"root": root, "report": report, "report_owner": report_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "journal": journal, "journal_owner": journal_owner}


def run_worker(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    context, retained = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "require the complete frozen Rust worker context")
    active = active_worker_approval(options)
    producer = retained["producer"]
    spec = rust_family_spec(producer)
    suite = producer.suite_spec(options.suite)
    source_pins = {path: digest for path, digest, _ in
                   REPAIRED_SOURCE_OWNERS}
    pins = {
        "source": REPAIRED_SOURCE_OWNERS[0][1],
        "native_engine": ENGINE_SHA256,
        "native_bridge": BRIDGE_SHA256,
    }
    provenance = producer.exact_native_owners(spec, pins, source_pins)
    require(provenance["source"]["sha256"] == pins["source"]
            and provenance["native_engine"]["sha256"] == ENGINE_SHA256
            and provenance["native_bridge"]["sha256"] == BRIDGE_SHA256,
            "run only the actual full nine-owner repaired Rust family")
    if suite.name == "original_bounded_v5":
        observed = producer.observe_original_upstream(
            suite, spec, pins, source_pins)
    elif suite.name == "subinterpreter_v2":
        observed = producer.observe_subinterpreters(
            suite, spec, pins, source_pins,
            producer_sha256=PRODUCER["source"][1])
    else:
        observed = producer.observe_direct_suite(
            suite, spec, pins, source_pins, retained["phase_one"])
    require(type(observed) is dict
            and observed.get("schema")
            == producer.SCHEMA + "-actual-original-suite"
            and observed.get("status") in ("PASS", "FAIL")
            and observed.get("suite") == suite.name
            and observed.get("candidate_family") == FAMILY
            and observed.get("case_execution_denominator") == suite.case_count
            and observed.get("actual_candidate_case_count") == suite.case_count
            and type(observed.get("mismatch_count")) is int
            and observed["mismatch_count"] >= 0
            and type(observed.get("all_mismatches")) is list
            and len(observed["all_mismatches"]) == observed["mismatch_count"]
            and observed.get("actual_candidate_workers") == 1
            and observed.get("clock_samples") == 0
            and observed.get("holdout") == "NOT OPENED",
            "preserve every complete original Rust matching observation")
    if suite.name == "original_bounded_v5":
        require(observed.get("actual_public_record_count") == 152
                and observed.get("actual_debug_skip_count") == 1
                and observed.get("named_private_waiver_count") == 13,
                "never suppress genuine upstream public methods")
    if suite.name == "subinterpreter_v2" and observed["status"] == "PASS":
        require(observed.get("actual_case_interpreter_exec_calls") == 394
                and observed.get("actual_interpreters_created") == 11
                and observed.get("actual_interpreters_destroyed") == 11
                and observed.get("all_real_pipes_read_to_eof") is True
                and observed.get("all_real_pipe_descriptors_closed") is True
                and observed.get("interpreter_live_set_restored") is True,
                "preserve all genuine original Rust interpreter lifecycles")
    return {
        "schema": WORKER_SCHEMA, "status": observed["status"],
        "candidate_family": FAMILY, "label": LABEL, "suite": suite.name,
        "case_execution_denominator": suite.case_count,
        "mismatch_count": observed["mismatch_count"],
        "failure_class":
            "PASS" if observed["status"] == "PASS" else "SEMANTIC MISMATCH",
        "original_observer_source_sha256": PRODUCER["source"][1],
        "original_observer_unchanged": True,
        "v3_legacy_activation_dispatch_invoked": False,
        "actual_v11_build_archive_sha256": RUST_BUILD["archive"][1],
        "actual_v11_build_receipt_sha256": RUST_BUILD["receipt"][1],
        "activation_report_sha256": active["report_owner"]["sha256"],
        "activation_receipt_sha256": active["receipt_owner"]["sha256"],
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "repaired_source_owner_count": 9,
        "repaired_public_source_sha256": REPAIRED_SOURCE_OWNERS[0][1],
        "repaired_bridge_source_sha256": REPAIRED_SOURCE_OWNERS[1][1],
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "complete_original_observation": observed,
        "all_original_records_and_mismatches_preserved": True,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_qualified": False,
    }


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes, "record the exact genuine worker byte stream")
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "sha256": sha256(raw), "size_bytes": len(raw)}


def worker_arguments(options: argparse.Namespace, name: str,
                     active: dict[str, Any]) -> list[str]:
    return [
        PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE), "--worker",
        "--source-sha256", options.source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--contract-sha256", options.contract_sha256,
        "--family", FAMILY, "--label", LABEL, "--suite", name,
        "--activation-root", active["root"],
        "--activation-report-sha256", active["activation_owner"]["sha256"],
        "--activation-receipt-sha256", active["receipt_owner"]["sha256"],
        "--recovery-journal-sha256", active["journal_owner"]["sha256"],
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


def execute_one_worker(options: argparse.Namespace, name: str, count: int,
                       active: dict[str, Any]) -> dict[str, Any]:
    argv = worker_arguments(options, name, active)
    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = child.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        stdout, stderr = child.communicate()
    except BaseException:
        if child.poll() is None:
            child.kill()
        child.communicate()
        raise
    require(type(stdout) is bytes and type(stderr) is bytes
            and len(stdout) <= MAX_STDOUT_BYTES
            and len(stderr) <= MAX_STDERR_BYTES,
            "retain every complete bounded original Rust worker stream")
    process = {
        "argv": argv, "pid": child.pid,
        "returncode": child.returncode, "timed_out": timed_out,
        "stdout": encode_stream(stdout), "stderr": encode_stream(stderr),
        "actual_worker_processes": 1,
    }
    observed = None
    decode_failure = None
    try:
        observed = strict_document(stdout, "actual original Rust suite")
    except Exception as error:
        decode_failure = {
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:4096],
        }
    complete = (
        type(observed) is dict and observed.get("schema") == WORKER_SCHEMA
        and observed.get("candidate_family") == FAMILY
        and observed.get("label") == LABEL
        and observed.get("suite") == name
        and observed.get("case_execution_denominator") == count
        and observed.get("original_observer_source_sha256")
        == PRODUCER["source"][1]
        and observed.get("actual_v11_build_archive_sha256")
        == RUST_BUILD["archive"][1]
        and observed.get("native_engine_sha256") == ENGINE_SHA256
        and observed.get("native_bridge_sha256") == BRIDGE_SHA256
        and observed.get("repaired_source_owner_count") == 9
        and observed.get("all_original_records_and_mismatches_preserved")
        is True
        and observed.get("actual_candidate_workers") == 1
        and observed.get("holdout") == "NOT OPENED"
        and observed.get("status") in ("PASS", "FAIL")
        and type(observed.get("mismatch_count")) is int
        and observed["mismatch_count"] >= 0
        and not timed_out
        and child.returncode == (0 if observed["status"] == "PASS" else 1)
    )
    if complete:
        return {
            "suite": name, "status": observed["status"],
            "case_execution_denominator": count,
            "failure_class": observed["failure_class"],
            "mismatch_count": observed["mismatch_count"],
            "actual_worker_started": True, "actual_worker_processes": 1,
            "all_original_records_and_mismatches_preserved": True,
            "original_observer": observed, "process": process,
        }
    return {
        "suite": name, "status": "FAIL",
        "case_execution_denominator": count,
        "failure_class": "INFRASTRUCTURE FAILURE",
        "mismatch_count": "NOT MEASURED",
        "actual_worker_started": True, "actual_worker_processes": 1,
        "all_original_records_and_mismatches_preserved": False,
        "worker_decoding_failure": decode_failure,
        "actual_worker_output": observed,
        "process": process,
    }


def failed_worker(name: str, count: int,
                  error: BaseException) -> dict[str, Any]:
    return {
        "suite": name, "status": "FAIL",
        "case_execution_denominator": count,
        "failure_class": "INFRASTRUCTURE FAILURE",
        "mismatch_count": "NOT MEASURED",
        "actual_worker_started": False, "actual_worker_processes": 0,
        "all_original_records_and_mismatches_preserved": False,
        "error_type": type(error).__qualname__,
        "error_message": str(error)[:4096],
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__),
        "process": None,
    }


def evidence_names(failure: bool) -> tuple[str, str]:
    stem = "repaired-rust-original-campaign-v2-rust-" + LABEL
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_fresh_evidence(publication: types.ModuleType) -> None:
    directory = publication.open_evidence_directory()
    try:
        for failed in (False, True):
            for name in evidence_names(failed):
                try:
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise CampaignError(
                    "never overwrite an existing Rust campaign result: " + name)
    finally:
        os.close(directory)


def write_evidence_receipt(name: str,
                           document: dict[str, Any]) -> dict[str, Any]:
    require("/" not in name and bool(name),
            "publish only one exact owner-only receipt basename")
    relative = EVIDENCE_RELATIVE + "/" + name
    raw = canonical(document)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    root = os.open(str(ROOT / EVIDENCE_RELATIVE), flags)
    descriptor: int | None = None
    try:
        descriptor = os.open(
            name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600, dir_fd=root)
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and stat.S_IMODE(initial.st_mode) == 0o600
                and initial.st_uid == os.geteuid()
                and initial.st_nlink == 1,
                "publish a single exclusive genuine failure or success receipt")
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(type(count) is int and count > 0,
                    "reject a partial Rust publication receipt")
            offset += count
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        require((initial.st_dev, initial.st_ino)
                == (final.st_dev, final.st_ino)
                and final.st_size == len(raw),
                "reject an exchanged or truncated Rust publication receipt")
        os.close(descriptor)
        descriptor = None
        os.fsync(root)
        reread, owner = _read_owned(
            str(ROOT), relative, sha256(raw), exact_size=len(raw),
            maximum=MAX_ARCHIVE_BYTES)
        require(reread == raw, "reread every durable receipt byte")
        owner.update({
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
        })
        return owner
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(root)


def preserve_campaign(report: dict[str, Any],
                      retained: dict[str, Any]) -> dict[str, Any]:
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
            and [(item.get("suite"), item.get("case_execution_denominator"))
                 for item in report["suite_results"]] == list(SUITES)
            and report.get("all_original_targets_restored") is True
            and report.get("restoration_verified_before_publication") is True
            and report.get("holdout") == "NOT OPENED"
            and report.get("clock_samples") == 0,
            "never publish incomplete observations or unrestored Rust files")
    current = exact_originals()
    require(report.get("restored_original_targets") == current,
            "authenticate all four original inodes immediately before publication")
    archive_name, receipt_name = evidence_names(report["status"] == "FAIL")
    publication = retained["publication"]
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
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("streaming_readback_verified") is True
            and stream.get("gzip_mtime") == 0
            and stream.get("gzip_single_member") is True,
            "require complete genuine lossless single-member V2 publication")
    receipt_document = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "candidate_status": report["status"],
        "family": FAMILY, "label": LABEL, "archive": archive,
        "campaign_source_sha256": report["campaign_source_sha256"],
        "campaign_protocol_sha256": report["campaign_protocol_sha256"],
        "campaign_contract_sha256": report["campaign_contract_sha256"],
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
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "restoration_verified_before_publication": True,
        "preserved_zig_preflight_failure_archive_sha256":
            ZIG_FAILURE["archive"][1],
        "preserved_zig_preflight_failure_receipt_sha256":
            ZIG_FAILURE["receipt"][1],
        "preserved_zig_corrected_campaign_archive_sha256":
            ZIG_CORRECTED_CAMPAIGN["archive"][1],
        "preserved_zig_corrected_campaign_receipt_sha256":
            ZIG_CORRECTED_CAMPAIGN["receipt"][1],
        "actual_zig_corrected_semantic_mismatch_count": 2172,
        "actual_zig_corrected_verified_passing_case_count": 2847,
        "actual_zig_corrected_candidate_workers": 13,
        "published_v26_evidence_owner_count": 141,
        "published_v26_authenticated_reference_count": 146,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "group_atomic": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt = write_evidence_receipt(receipt_name, receipt_document)
    require((archive["device"], archive["inode"])
            != (receipt["device"], receipt["inode"])
            and exact_originals() == current,
            "prove separate durable evidence and unchanged restored Rust owners")
    return {
        "schema": SCHEMA + "-published-complete-original-campaign",
        "status": report["status"], "family": FAMILY, "label": LABEL,
        "archive": archive, "receipt": receipt,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "group_atomic": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
    }


def authenticate_failure_publication() -> types.ModuleType:
    """Pin the original writer before a future controller's first preflight.

    This function is reachable only from an explicitly authorized actual run.
    It accesses no canonical Rust source or native target.  Authenticating the
    writer first lets a genuine subsequent preactivation failure be recorded
    without importing a candidate or substituting a matching implementation.
    """
    for key in ("source", "protocol", "contract"):
        read_owner(PUBLICATION[key])
    raw, _ = read_owner(PUBLICATION["contract"])
    document = strict_document(raw, "exact original V2 lossless publisher")
    require(document.get("version") == 2,
            "authenticate the exact original V2 failure publisher")
    publication = load_frozen(PUBLICATION["source"], "v2_lossless_writer")
    require(all(callable(getattr(publication, name, None)) for name in
                ("open_evidence_directory", "write_streamed_archive",
                 "stream_canonical_gzip")),
            "reject an unavailable lossless original failure publisher")
    return publication


def run_campaign(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    publication = authenticate_failure_publication()
    ensure_fresh_evidence(publication)
    retained: dict[str, Any] = {"publication": publication}
    active: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    failure: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    baseline: dict[str, dict[str, Any]] | None = None
    try:
        context, retained = verify_context(
            options.source_sha256, options.protocol_sha256,
            options.contract_sha256, retain=True)
        require(context.get("status") == "PASS",
                "authenticate the released Rust context before activation")
        baseline = exact_originals()
        active = stage_four_roles(
            retained, options.source_sha256,
            options.protocol_sha256, options.contract_sha256)
        for name, count in SUITES:
            try:
                row = execute_one_worker(options, name, count, active)
            except Exception as error:
                row = failed_worker(name, count, error)
            rows.append(row)
    except Exception as error:
        failure = {
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:4096],
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
        }
        observed = {item.get("suite") for item in rows}
        for name, count in SUITES:
            if name not in observed:
                rows.append(failed_worker(name, count, error))
        rows.sort(key=lambda item: dict(
            (name, number) for number, (name, _) in enumerate(SUITES)
        )[item["suite"]])
    finally:
        if active is not None:
            restoration = restore_four_roles(
                active["root"], active["journal"],
                active["journal_owner"]["sha256"])
        originals = exact_originals()
        if baseline is not None:
            require(originals == baseline,
                    "restore all four exact original Rust inodes in finally")
    require(len(rows) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in rows] == list(SUITES),
            "preserve all original suite slots after every real failure")
    pids = [
        row["process"]["pid"] for row in rows
        if row.get("actual_worker_started") is True
        and type(row.get("process")) is dict
    ]
    require(len(pids) == len(set(pids)),
            "never count duplicate process IDs as independent Rust workers")
    passed = sum(
        count for (name, count), row in zip(SUITES, rows, strict=True)
        if row.get("suite") == name
        and row.get("failure_class") == "PASS"
        and row.get("mismatch_count") == 0
        and row.get("all_original_records_and_mismatches_preserved") is True)
    differences = sum(
        row["mismatch_count"] for row in rows
        if row.get("failure_class") == "SEMANTIC MISMATCH"
        and type(row.get("mismatch_count")) is int)
    infrastructure = sum(
        row.get("failure_class") == "INFRASTRUCTURE FAILURE"
        for row in rows) + int(failure is not None)
    complete = sum(row.get("actual_worker_started") is True
                   for row in rows)
    qualified = (
        len(pids) == 13 and complete == 13 and passed == CASE_COUNT
        and differences == 0 and infrastructure == 0
        and all(row.get("actual_worker_processes") == 1
                and row.get("all_original_records_and_mismatches_preserved")
                is True for row in rows)
        and restoration is not None
    )
    report = {
        "schema": CAMPAIGN_SCHEMA,
        "status": "PASS" if qualified else "FAIL",
        "family": FAMILY, "label": LABEL,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "original_v3_producer_source_sha256": PRODUCER["source"][1],
        "original_v3_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v3_producer_contract_sha256": PRODUCER["contract"][1],
        "actual_v11_build_archive_sha256": RUST_BUILD["archive"][1],
        "actual_v11_build_receipt_sha256": RUST_BUILD["receipt"][1],
        "actual_rust_compiler_process_count": 28,
        "actual_bridge_source_repair_count": 2,
        "actual_public_source_repair_count": 2,
        "repaired_rust_source_owner_count": 9,
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
        "semantic_mismatch_count": (
            differences if complete else "NOT MEASURED"),
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": qualified,
        "v3_legacy_activation_dispatch_invoked": False,
        "v2_candidate_matching_invoked": False,
        "actual_zig_preflight_failure_archive_sha256":
            ZIG_FAILURE["archive"][1],
        "actual_zig_preflight_failure_receipt_sha256":
            ZIG_FAILURE["receipt"][1],
        "actual_zig_corrected_campaign_archive_sha256":
            ZIG_CORRECTED_CAMPAIGN["archive"][1],
        "actual_zig_corrected_campaign_receipt_sha256":
            ZIG_CORRECTED_CAMPAIGN["receipt"][1],
        "actual_zig_corrected_semantic_mismatch_count": 2172,
        "actual_zig_corrected_verified_passing_case_count": 2847,
        "actual_zig_corrected_candidate_workers": 13,
        "published_v26_evidence_owner_count": 141,
        "published_v26_authenticated_reference_count": 146,
        "published_v27_evidence_owner_count": 143,
        "published_v27_authenticated_reference_count": 148,
        "all_original_targets_restored": True,
        "restored_original_targets": originals,
        "restoration": restoration,
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "controller_failure": failure,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return preserve_campaign(report, retained)


def assert_actual_authorization(options: argparse.Namespace) -> None:
    require(options.family == FAMILY
            and checked_label(options.label) == LABEL
            and options.producer_source_sha256 == PRODUCER["source"][1]
            and options.producer_protocol_sha256 == PRODUCER["protocol"][1]
            and options.producer_contract_sha256 == PRODUCER["contract"][1]
            and options.publication_source_sha256 == PUBLICATION["source"][1]
            and options.publication_protocol_sha256 == PUBLICATION["protocol"][1]
            and options.publication_contract_sha256 == PUBLICATION["contract"][1]
            and options.build_archive_sha256 == RUST_BUILD["archive"][1]
            and options.build_receipt_sha256 == RUST_BUILD["receipt"][1]
            and options.native_engine_sha256 == ENGINE_SHA256
            and options.native_bridge_sha256 == BRIDGE_SHA256
            and options.native_engine_bytes == ENGINE_BYTES
            and options.native_bridge_bytes == BRIDGE_BYTES,
            "independently caller-pin all genuine original Rust owners")


def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    require(all(type(value) is str for value in values),
            "require a complete literal Rust source-freeze invocation")
    names = [value for value in values if value.startswith("--")]
    require(len(names) == len(set(names)),
            "reject duplicate or ambiguous explicit authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--worker", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--suite", choices=tuple(x for x, _ in SUITES))
    parser.add_argument("--activation-root")
    for name in (
        "activation-report", "activation-receipt", "recovery-journal",
        "producer-source", "producer-protocol", "producer-contract",
        "publication-source", "publication-protocol", "publication-contract",
        "build-archive", "build-receipt", "native-engine", "native-bridge",
    ):
        parser.add_argument("--" + name + "-sha256")
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "Rust campaign source")
    checked_digest(options.protocol_sha256, "Rust campaign protocol")
    for name in (
        "contract_sha256", "activation_report_sha256",
        "activation_receipt_sha256", "recovery_journal_sha256",
        "producer_source_sha256", "producer_protocol_sha256",
        "producer_contract_sha256", "publication_source_sha256",
        "publication_protocol_sha256", "publication_contract_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
    ):
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    actual = (
        "family", "label", "suite", "activation_root",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256", "producer_source_sha256",
        "producer_protocol_sha256", "producer_contract_sha256",
        "publication_source_sha256", "publication_protocol_sha256",
        "publication_contract_sha256", "build_archive_sha256",
        "build_receipt_sha256", "native_engine_sha256",
        "native_bridge_sha256", "native_engine_bytes", "native_bridge_bytes",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, name) is None for name in actual),
                "contract rendering must not authorize a candidate")
        return options
    require(options.contract_sha256 is not None,
            "independently caller-pin the complete frozen Rust contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in actual),
                "source-only verification cannot authorize an actual run")
        return options
    required = (
        "family", "label", "producer_source_sha256",
        "producer_protocol_sha256", "producer_contract_sha256",
        "publication_source_sha256", "publication_protocol_sha256",
        "publication_contract_sha256", "build_archive_sha256",
        "build_receipt_sha256", "native_engine_sha256",
        "native_bridge_sha256", "native_engine_bytes", "native_bridge_bytes",
    )
    require(all(getattr(options, name) is not None for name in required),
            "independently pin every original reference and actual Rust role")
    if options.worker:
        require(options.suite is not None
                and options.activation_root is not None
                and options.activation_report_sha256 is not None
                and options.activation_receipt_sha256 is not None
                and options.recovery_journal_sha256 is not None,
                "authorize only one journal-bound actual Rust suite worker")
    else:
        require(options.suite is None and options.activation_root is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None
                and options.recovery_journal_sha256 is None,
                "a Rust campaign must create its own four-owner journal")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        result = self_test(
            options.source_sha256, options.protocol_sha256,
            options.contract_sha256)
        code = 0
    elif options.verify_frozen_context:
        result, _ = verify_context(
            options.source_sha256, options.protocol_sha256,
            options.contract_sha256)
        code = 0
    elif options.render_contract:
        result = protocol_document(
            options.source_sha256, options.protocol_sha256)
        code = 0
    elif options.worker:
        try:
            result = run_worker(options)
            code = 0 if result["status"] == "PASS" else 1
        except Exception as error:
            result = {
                "schema": WORKER_SCHEMA, "status": "FAIL",
                "candidate_family": FAMILY,
                "label": LABEL, "suite": options.suite,
                "case_execution_denominator": dict(SUITES).get(
                    options.suite),
                "failure_class": "INFRASTRUCTURE FAILURE",
                "mismatch_count": "NOT MEASURED",
                "error_type": type(error).__qualname__,
                "error_message": str(error)[:4096],
                "traceback": traceback.format_exception(
                    type(error), error, error.__traceback__),
                "actual_candidate_workers": 1,
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
                "candidate_qualified": False,
            }
            code = 1
    else:
        try:
            result = run_campaign(options)
            code = 0 if result["status"] == "PASS" else 1
        except Exception as error:
            result = {
                "schema": SCHEMA + "-actual-controller-infrastructure-failure",
                "status": "FAIL",
                "failure_class": "CONTROLLER INFRASTRUCTURE FAILURE",
                "family": FAMILY,
                "label": LABEL,
                "error_type": type(error).__qualname__,
                "error_message": str(error)[:4096],
                "traceback": traceback.format_exception(
                    type(error), error, error.__traceback__),
                "durable_failure_publication": "NOT VERIFIED",
                "all_four_original_targets_restored": "NOT VERIFIED",
                "suite_count": SUITE_COUNT,
                "case_execution_denominator": CASE_COUNT,
                "candidate_correctness": "NOT MEASURED",
                "candidate_qualified": False,
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
                "memory": "NOT MEASURED",
            }
            code = 1
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
