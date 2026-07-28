#!/usr/bin/env python3
"""Freeze a recoverable, genuinely original Rust V12 correctness campaign.

Source verification is read-only.  Matching, native replacement, recovery,
threads, subprocesses, and evidence publication are explicit, separate modes.
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
import io
import json
import locale
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
from typing import Any, Iterator, Mapping, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SOURCE_RELATIVE = "tools/run_owned_repaired_rust_original_campaign_v4.py"
PROTOCOL_RELATIVE = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V4.md"
CONTRACT_RELATIVE = "oracle/phase2/repaired-rust-original-campaign-v4.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v4"
CONTRACT_SCHEMA = SCHEMA + "-recoverable-source-freeze"
WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
RECOVERY_SCHEMA = SCHEMA + "-public-exact-inode-recovery"
RESTORATION_SCHEMA = SCHEMA + "-exact-original-inode-restoration"
SIGNAL_SCHEMA = SCHEMA + "-graceful-controller-signal"
FAMILY = "rust"
LABEL = "phase2-v12-rust-flag-original-p0"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
PUBLIC_RECOVERY_ROOT = (
    "/tmp/rebar-phase2-repaired-rust-original-campaign-v2-"
    "safe-v4-phase2-v12-rust-flag-original-p0"
)
LOCK_NAME = "recoverable-controller-v4.lock"
PHASE_NAMES = ("reference-a", "reference-b")
ROLE_ORDER = ("bridge_source", "adapter", "engine", "bridge")
RESTORATION_ORDER = tuple(reversed(ROLE_ORDER))
SIGNAL_NAMES = ("SIGINT", "SIGTERM", "SIGHUP")
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BUILD_ARCHIVE_BYTES = 2 * 1024 * 1024
MAX_BUILD_PLAIN_BYTES = 2 * 1024 * 1024
MAX_RECEIPT_BYTES = 64 * 1024
MAX_GRAPH_BYTES = 2 * 1024 * 1024
MAX_NATIVE_BYTES = 2 * 1024 * 1024
MAX_WORKER_STDOUT_BYTES = 32 * 1024 * 1024
MAX_WORKER_STDERR_BYTES = 4 * 1024 * 1024
MAX_SUITE_COMPRESSED_BYTES = 16 * 1024 * 1024
MAX_SUITE_PLAIN_BYTES = 512 * 1024 * 1024
MAX_PUBLIC_REPORT_BYTES = 32 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 8 * 3600
SUITE_COUNT = 13
CASE_COUNT = 31_237
PRIVATE_WAIVER_COUNT = 13
PREVIOUS_EVIDENCE_OWNER_COUNT = 149
PREVIOUS_AUTHENTICATED_REFERENCE_COUNT = 154
ACTUAL_EVIDENCE_OWNER_COUNT = 151
ACTUAL_AUTHENTICATED_REFERENCE_COUNT = 156

# Every entry is an already published, immutable source or evidence owner.
PRODUCER = {
    "source": ("tools/run_owned_six_family_original_p0_producer_v3.py",
               "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
                 "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76", 5522),
    "contract": ("oracle/phase2/six-family-p0-producer-v3.json",
                 "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1", 26909),
}
PUBLICATION = {
    "source": ("tools/run_owned_six_family_original_p0_campaign_v2.py",
               "6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1", 101836),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md",
                 "e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e", 4995),
    "contract": ("oracle/phase2/six-family-p0-campaign-v2.json",
                 "e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7", 21314),
}
V2 = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v2.py",
               "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3", 143441),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V2.md",
                 "9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0", 9342),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v2.json",
                 "bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547", 15927),
}
V3 = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v3.py",
               "23819da6e6bb1ce8b27144a5d974b4bb0ecac845c844cb6fadae2ba01b2ef3d2", 89825),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V3.md",
                 "c29edb7751045da17cce2052e028b92530d8eab5ba6b8adafc21135a746f7883", 5766),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v3.json",
                 "ab4b424570254201865394330e025850b4626dfe2eaacd4ec82f41d2e99b0980", 10992),
}
V30 = {
    "source": ("tools/render_candidate_current_overview_v30.py",
               "a8c2bb2e0ccfab0b76b5387437fe48279e01ca1034739a67967f543f1930c507", 60771),
    "inputs": ("docs/evidence/candidate-current-overview-v30.inputs.json",
               "ea2ea381a22a9a23344ff40505d975aba8d25704d2ad90e03b58018fda44ca0f", 65902),
    "summary": ("docs/evidence/candidate-current-overview-v30.json",
                "b04db4e93dc74bb9200c13133c0a33bd33961b5f35e5810e74de65b29fcab534", 293980),
    "svg": ("docs/evidence/candidate-current-overview-v30.svg",
            "a3dbbb69c5140d15588463e0e3579d5bea5d95587f1abf444b6679cd3361d4c6", 12987),
}
BUILD = {
    "source": ("tools/reproduce_owned_rust_flag_source_build_v12.py",
               "1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6", 86933),
    "protocol": ("oracle/phase2/RUST-FLAG-SOURCE-BUILD-V12.md",
                 "822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950", 5567),
    "contract": ("oracle/phase2/rust-flag-source-build-v12.json",
                 "c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592", 13038),
    "archive": (
        "oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz",
        "840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d", 108325,
    ),
    "receipt": (
        "oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-publication-receipt.json",
        "1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f", 2109,
    ),
}
PUBLIC_REPAIR = {
    "source": ("tools/apply_owned_rust_public_contract_source_repair_v2.py",
               "d0f90145195e9978482a7797956ef916adb1d0612118c2fc6343c4f38b823fa8", 74140),
    "protocol": ("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V2.md",
                 "3f469ca7298b08cc1d50d18aff5029ae17a3f4f318c4fc7a2d8f8f45cc16e239", 5505),
    "contract": ("oracle/phase2/rust-public-contract-source-repair-v2.json",
                 "b87c876e16041b0e08619aec0a86a069598b54478a1fa55cc9baa220c2c1f53b", 13826),
}
HISTORICAL_RUST_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-"
    "phase2-v11-rust-dual-overlay-original-p0-failures-publication-receipt.json",
    "97f0b8c47823b20cd04740e3fe2883189cc648d49769015800c0998e6698c281", 4447,
)
HISTORICAL_RUST_ARCHIVE_SHA256 = (
    "3ac7736c127d13d3fad579c4ab9974c6a83612b4253f7921ed3e44269f3a82ad"
)
HISTORICAL_RUST_JOURNAL = (
    "b28862fc1433af8c2897299cf6d64fb672f452f011c68fe887714dc09b60ea65"
)
CORRECTED_PUBLIC_SHA256 = (
    "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
)
CORRECTED_PUBLIC_BYTES = 31464
HISTORICAL_DERIVED_PUBLIC_SHA256 = (
    "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
)
BRIDGE_SOURCE_SHA256 = (
    "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
)
BRIDGE_SOURCE_BYTES = 176118
ENGINE_SHA256 = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_BYTES = 658344
BRIDGE_SHA256 = "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54"
BRIDGE_BYTES = 148656
V12_PLAIN_SHA256 = "a69fe5a873891c3aee51cf8e711877125b06c079057b04daeb86720bbd2dc75f"
V12_PLAIN_BYTES = 757826

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
CORRECTED_SOURCE_OWNERS: tuple[tuple[str, str, int], ...] = (
    ("candidates/rust_candidate.py", CORRECTED_PUBLIC_SHA256, CORRECTED_PUBLIC_BYTES),
    ("candidates/rust/py_bridge.c", BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
    ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    ("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
)
ORIGINAL_SOURCE_OWNERS: tuple[tuple[str, str, int], ...] = (
    ("candidates/rust_candidate.py", ORIGINALS["adapter"]["sha256"], ORIGINALS["adapter"]["bytes"]),
    ("candidates/rust/py_bridge.c", ORIGINALS["bridge_source"]["sha256"], ORIGINALS["bridge_source"]["bytes"]),
    *CORRECTED_SOURCE_OWNERS[2:],
)
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
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols",
    "engine_sections", "engine_notes", "bridge_sections", "bridge_notes",
)
RUST_EXPORTS = (
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group", "rebar_name_len",
)


class CampaignError(Exception):
    """A frozen original case, actual owner, or recovery proof was rejected."""


class SourceOnlyViolation(CampaignError):
    """A synthetic source check attempted an actual external operation."""


class GracefulControllerSignal(CampaignError):
    """An actually installed controller handler received a recoverable signal."""

    def __init__(self, signum: int) -> None:
        self.signum = signum
        self.signal_name = signal.Signals(signum).name
        super().__init__("restore all original Rust inodes after " + self.signal_name)


def require(valid: Any, reason: str) -> None:
    if valid is not True:
        raise CampaignError(reason)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(part in "0123456789abcdef" for part in value),
            "require an exact independent SHA-256 for " + label)
    return value


def digest(raw: Any) -> str:
    require(type(raw) is bytes, "hash only complete actual bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                           separators=(",", ":"), allow_nan=False)
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise CampaignError("reject a noncanonical complete observation") from error


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CampaignError("reject duplicated JSON owner: " + str(key))
        result[key] = value
    return result


def strict_document(raw: Any, label: str, *, exact: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw),
            "require the complete immutable document " + label)
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                CampaignError("reject a non-finite JSON number: " + token)),
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CampaignError("reject malformed original document " + label) from error
    require(type(value) is dict, "require an exact object for " + label)
    if exact:
        require(canonical(value) == raw,
                "reject noncanonical or concealed owner bytes: " + label)
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and not value.startswith("/")
            and "\\" not in value and "\x00" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "reject an absolute, escaped, empty, or ambiguous owner")
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and sys.version_info[:3] == (3, 14, 6)
            and os.path.abspath(sys.executable) == PYTHON
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "require independently pinned isolated CPython 3.14.6 with -I -B")


def read_absolute(path: str, expected: str, *, maximum: int,
                  exact_size: int | None = None,
                  private: bool = False,
                  device: int | None = None,
                  inode: int | None = None) -> tuple[bytes, dict[str, Any]]:
    checked_digest(expected, "descriptor-bound exact owner")
    require(type(path) is str and os.path.isabs(path) and "\x00" not in path
            and type(maximum) is int and maximum > 0,
            "read only one exact bounded absolute owner")
    if exact_size is not None:
        require(type(exact_size) is int and 0 <= exact_size <= maximum,
                "reject an invalid exact owner byte count")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    handle = os.open(path, flags)
    try:
        first = os.fstat(handle)
        require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1
                and 0 <= first.st_size <= maximum
                and (exact_size is None or first.st_size == exact_size)
                and (not private or (first.st_uid == os.geteuid()
                                     and stat.S_IMODE(first.st_mode) == 0o600))
                and (device is None or first.st_dev == device)
                and (inode is None or first.st_ino == inode),
                "reject a foreign, linked, substituted, oversized, or truncated owner")
        remaining = first.st_size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            require(type(piece) is bytes and bool(piece),
                    "reject a truncated bounded owner")
            pieces.append(piece)
            remaining -= len(piece)
        require(os.read(handle, 1) == b"", "reject concealed trailing owner bytes")
        raw = b"".join(pieces)
        last = os.fstat(handle)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns)
                and digest(raw) == expected,
                "reject owner bytes or inode exchanged during authentication")
        return raw, {
            "path": path, "sha256": expected, "bytes": len(raw),
            "size_bytes": len(raw), "device": last.st_dev,
            "inode": last.st_ino, "mode": stat.S_IMODE(last.st_mode),
            "uid": last.st_uid, "nlink": last.st_nlink,
        }
    finally:
        os.close(handle)


def read_owned(item: tuple[str, str, int], *, maximum: int = MAX_SOURCE_BYTES,
               private: bool = False) -> tuple[bytes, dict[str, Any]]:
    relative, expected, count = item
    checked_relative(relative)
    raw, owner = read_absolute(str(ROOT / relative), expected,
                               maximum=maximum, exact_size=count,
                               private=private)
    owner["relative"] = relative
    return raw, owner


def owner_document(item: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": item[0], "sha256": item[1], "bytes": item[2]}


def grouped_owners(items: Mapping[str, tuple[str, str, int]]) -> dict[str, Any]:
    return {name: owner_document(item)
            for name, item in sorted(items.items())}


def zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_library_loads": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "canonical_target_replacements": 0,
        "recovery_roots_created": 0,
        "recovery_locks_acquired": 0,
        "recovery_journals_created": 0,
        "signal_handlers_installed": 0,
        "signal_masks_installed": 0,
        "threads_started": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_mutations": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "V4 campaign source")
    checked_digest(protocol_pin, "V4 campaign explanation")
    return {
        "schema": CONTRACT_SCHEMA,
        "status": "SOURCE FROZEN; CORRECTED RUST V12 CANDIDATE NOT RUN",
        "version": 4,
        "family": FAMILY,
        "campaign_label": LABEL,
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "pinned_cpython": {"path": PYTHON, "sha256": PYTHON_SHA256,
                            "version": "3.14.6", "isolated": True},
        "original_oracle": {
            "producer": grouped_owners(PRODUCER),
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "upstream_public_records": 152,
            "upstream_real_debug_skip_count": 1,
            "nested_case_count": 128,
            "nested_interpreter_events": 394,
            "nested_interpreters_created": 11,
            "nested_interpreters_destroyed": 11,
            "actual_locale_cases": 64,
            "actual_locale_transitions": 192,
            "actual_shared_pattern_thread_cases": 512,
            "actual_python_buffer_exporter_cases": 264,
            "canonical_public_module": "candidates.rust_candidate",
            "cross_family_matching_allowed": False,
            "external_regex_dependency_allowed": False,
            "stdlib_re_fallback_allowed": False,
            "candidate_wrapper_allowed": False,
            "reference_worker_started": False,
        },
        "actual_corrected_v12_build": {
            "owners": grouped_owners(BUILD),
            "build_status": "PASS",
            "build_version": 12,
            "build_label": LABEL,
            "phase_count": 2,
            "compiler_process_count": 28,
            "process_names_per_phase": list(PROCESS_NAMES),
            "compressed_archive_byte_limit": MAX_BUILD_ARCHIVE_BYTES,
            "uncompressed_archive_byte_limit": MAX_BUILD_PLAIN_BYTES,
            "uncompressed_sha256": V12_PLAIN_SHA256,
            "uncompressed_bytes": V12_PLAIN_BYTES,
            "native_role_count": 2,
            "engine": {"sha256": ENGINE_SHA256, "bytes": ENGINE_BYTES},
            "bridge": {"sha256": BRIDGE_SHA256, "bytes": BRIDGE_BYTES},
            "corrected_public_adapter": {
                "relative": "candidates/rust_candidate.py",
                "sha256": CORRECTED_PUBLIC_SHA256,
                "bytes": CORRECTED_PUBLIC_BYTES,
                "independent_fresh_phase_count": 2,
            },
            "corrected_bridge_source": {
                "relative": "candidates/rust/py_bridge.c",
                "sha256": BRIDGE_SOURCE_SHA256,
                "bytes": BRIDGE_SOURCE_BYTES,
                "independent_fresh_phase_count": 2,
            },
            "corrected_public_overlay_apply_count": 2,
            "bridge_overlay_apply_count": 2,
            "source_owner_count_per_phase": 9,
            "unchanged_source_owner_count_per_phase": 7,
            "complete_corrected_source_owners": [
                {"relative": relative, "sha256": fingerprint,
                 "bytes": count}
                for relative, fingerprint, count in CORRECTED_SOURCE_OWNERS
            ],
            "corrected_public_source_repair": grouped_owners(PUBLIC_REPAIR),
            "native_bytes_may_equal_an_earlier_reproducible_build": True,
            "actual_v12_build_provenance_cannot_be_replaced_with_v11": True,
            "candidate_matching": "NOT MEASURED",
            "candidate_qualified": False,
        },
        "preserved_v30_history": {
            "owners": grouped_owners(V30),
            "repository_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
            "authenticated_reference_count": PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
            "actual_rust_status": "FAIL",
            "actual_rust_semantic_mismatch_count": 1087,
            "actual_rust_verified_passing_case_count": 7438,
            "actual_rust_original_receipt": owner_document(HISTORICAL_RUST_RECEIPT),
            "actual_rust_original_archive_sha256": HISTORICAL_RUST_ARCHIVE_SHA256,
            "actual_rust_original_uncompressed_bytes": 192335385,
            "actual_rust_original_archive_decompressed": False,
            "actual_rust_original_journal_sha256": HISTORICAL_RUST_JOURNAL,
            "actual_c_status": "FAIL",
            "actual_c_semantic_mismatch_count": 1230,
            "actual_c_verified_passing_case_count": 7325,
            "actual_zig_status": "FAIL",
            "actual_zig_semantic_mismatch_count": 2172,
            "actual_zig_verified_passing_case_count": 2847,
            "qualified_candidate_count": 0,
        },
        "current_historical_accounting": {
            "previous_actual_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
            "previous_actual_authenticated_reference_count":
            PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
            "new_actual_v12_source_build_evidence_owner_count": 2,
            "new_actual_v12_digest_addressed_reference_count": 2,
            "actual_evidence_owner_count_before_new_campaign":
            ACTUAL_EVIDENCE_OWNER_COUNT,
            "actual_authenticated_reference_count_before_new_campaign":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "future_campaign_evidence_owners_created": 0,
            "qualified_candidate_count": 0,
        },
        "historical_frozen_campaigns": {
            "rust_v2_worker_only": grouped_owners(V2),
            "rust_v3_recoverable_controller": grouped_owners(V3),
            "streaming_publication_v2": grouped_owners(PUBLICATION),
            "v2_unsafe_controller_allowed": False,
            "v2_unsafe_activation_allowed": False,
            "c_only_v9_runner_allowed": False,
            "zig_only_v7_activation_allowed": False,
        },
        "four_original_target_owners": [
            {"role": role, "original": copy.deepcopy(ORIGINALS[role])}
            for role in ROLE_ORDER
        ],
        "public_recovery": {
            "root": PUBLIC_RECOVERY_ROOT,
            "root_owner_mode": "0700",
            "lock_filename": LOCK_NAME,
            "lock_owner_mode": "0600",
            "exclusive_nonblocking_controller_lock": True,
            "fixed_public_journal_filename": "recovery-journal.json",
            "journal_fsync_before_first_target_mutation": True,
            "journal_location_announced_before_first_target_mutation": True,
            "individual_intention_fsync_before_hardlink_or_replace": True,
            "original_inode_backup": "ADJACENT SAME-DIRECTORY NO-FOLLOW HARDLINK",
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "restore_device_inode_mode_uid_nlink_and_hash": True,
            "registered_graceful_signals": list(SIGNAL_NAMES),
            "block_graceful_signals_during_individual_mutations": True,
            "keyboard_interrupt_and_system_exit_swallowed": False,
            "sigkill_automatically_recovered": False,
            "power_failure_automatically_recovered": False,
            "sigkill_or_power_failure_requires_public_recover": True,
            "recovery_command_mode": "--recover",
            "caller_pins_exact_journal_sha256": True,
            "caller_pins_exact_root": True,
            "unknown_or_foreign_owner_is_overwritten": False,
            "recovery_idempotent": True,
            "group_atomic": False,
        },
        "future_lossless_publication": {
            "publication_only_after_all_four_original_inodes_restored": True,
            "actual_original_suite_worker_count": SUITE_COUNT,
            "maximum_complete_worker_stdout_bytes": MAX_WORKER_STDOUT_BYTES,
            "maximum_worker_compressed_observation_bytes":
            MAX_SUITE_COMPRESSED_BYTES,
            "maximum_streamed_public_report_bytes": MAX_PUBLIC_REPORT_BYTES,
            "deterministic_single_member_zero_time_gzip": True,
            "archive_and_receipt_distinct_fresh_owner_inodes": True,
            "archive_owner_mode": "0600",
            "receipt_owner_mode": "0600",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "all_original_case_records_preserved": True,
            "all_actual_mismatches_preserved": True,
            "reference_oracle_rerun_allowed": False,
        },
        "source_only_effects": zero_effects(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict
            and canonical(value) == canonical(protocol_document(
                checked_digest(source_pin, "V4 source"),
                checked_digest(protocol_pin, "V4 protocol"))),
            "reject a substituted Rust V12 build, original suite, owner, or recovery policy")
    return value


def bounded_build_gzip(raw: bytes, *, expected_sha256: str,
                       expected_size: int) -> bytes:
    require(type(raw) is bytes and 18 <= len(raw) <= MAX_BUILD_ARCHIVE_BYTES
            and raw[:3] == b"\x1f\x8b\x08"
            and raw[4:8] == b"\x00\x00\x00\x00",
            "require exactly one deterministic, bounded V12 gzip member")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        plain = decoder.decompress(raw, MAX_BUILD_PLAIN_BYTES + 1)
        require(len(plain) <= MAX_BUILD_PLAIN_BYTES
                and not decoder.unconsumed_tail
                and decoder.eof and not decoder.unused_data,
                "reject an oversized, truncated, trailing, or multiple-member V12 archive")
        remainder = decoder.flush()
        require(len(plain) + len(remainder) <= MAX_BUILD_PLAIN_BYTES,
                "reject concealed V12 decompression bytes")
        plain += remainder
    except (zlib.error, EOFError, OSError) as error:
        raise CampaignError("reject an invalid original V12 gzip archive") from error
    require(len(plain) == expected_size and digest(plain) == expected_sha256,
            "authenticate every real V12 build document byte")
    return plain


def decode_process_stream(record: Mapping[str, Any], channel: str) -> bytes:
    encoded = record.get(channel + "_base64")
    expected_size = record.get(channel + "_bytes")
    expected_hash = record.get(channel + "_sha256")
    require(type(encoded) is str and type(expected_size) is int
            and 0 <= expected_size <= MAX_BUILD_PLAIN_BYTES,
            "preserve each complete real V12 compiler " + channel)
    checked_digest(expected_hash, "actual V12 compiler " + channel)
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as error:
        raise CampaignError("reject forged V12 compiler " + channel) from error
    require(len(raw) == expected_size and digest(raw) == expected_hash,
            "reject substituted V12 compiler " + channel)
    return raw


def require_actual_native_audit(output: Mapping[str, Any], role: str) -> None:
    require(type(output) is dict and output.get("family") == FAMILY
            and output.get("role") == role
            and output.get("candidate_imported") is False
            and output.get("prebuilt_artifact_read") is False,
            "reject a borrowed, imported, or prebuilt Rust native " + role)
    expected_hash, expected_size = (
        (ENGINE_SHA256, ENGINE_BYTES) if role == "engine"
        else (BRIDGE_SHA256, BRIDGE_BYTES)
    )
    expected_name = (
        "_rust_engine.so" if role == "engine"
        else "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
    )
    require(output.get("sha256") == expected_hash
            and output.get("size_bytes") == expected_size
            and output.get("file_name") == expected_name
            and type(output.get("device")) is int
            and type(output.get("inode")) is int
            and output["device"] >= 0 and output["inode"] > 0,
            "reject unproven complete V12 Rust native output " + role)
    audit = output.get("audit")
    require(type(audit) is dict and audit.get("role") == role
            and audit.get("cross_family_dependency_count") == 0
            and audit.get("external_regex_dependency_count") == 0,
            "reject sibling or external regex delegation in " + role)
    if role == "engine":
        require(tuple(audit.get("required_exports", ())) == RUST_EXPORTS
                and tuple(audit.get("exports", ())) == RUST_EXPORTS
                and tuple(audit.get("needed", ()))
                == ("ld-linux-x86-64.so.2", "libc.so.6", "libgcc_s.so.1")
                and audit.get("runpath") == [],
                "verify all eighteen genuine independently owned Rust exports")
    else:
        require(audit.get("exports") == ["PyInit__rust_bridge"]
                and audit.get("required_exports") == ["PyInit__rust_bridge"]
                and audit.get("needed") == ["_rust_engine.so", "libc.so.6"]
                and audit.get("runpath") == ["$ORIGIN"],
                "require the exact own-engine-only $ORIGIN CPython bridge")


def validate_phase(phase: Any, index: int, *, inspect_private: bool
                   ) -> dict[str, Any]:
    require(type(phase) is dict and 0 <= index < len(PHASE_NAMES)
            and phase.get("name") == PHASE_NAMES[index]
            and phase.get("candidate_imports") == 0
            and phase.get("candidate_processes_started") == 0
            and phase.get("hidden_cases_read") == 0
            and phase.get("timing_trials_run") == 0
            and phase.get("native_libraries_loaded") == 0,
            "require the exact fresh no-matching V12 build phase")
    sources = phase.get("fresh_source_owners")
    outputs = phase.get("native_outputs")
    forensics = phase.get("native_forensics")
    require(type(sources) is dict and type(outputs) is dict
            and type(forensics) is dict
            and set(sources) == {entry[0] for entry in CORRECTED_SOURCE_OWNERS}
            and set(outputs) == {"engine", "bridge"}
            and set(forensics) == {"engine", "bridge"},
            "require all nine original Rust owners and both native roles")
    actual_inodes: set[tuple[int, int]] = set()
    snapshot_root: str | None = None
    live: dict[str, dict[str, Any]] = {}
    for relative, fingerprint, count in CORRECTED_SOURCE_OWNERS:
        row = sources[relative]
        require(type(row) is dict and row.get("sha256") == fingerprint
                and row.get("bytes") == count
                and type(row.get("device")) is int
                and type(row.get("inode")) is int and row["inode"] > 0
                and row.get("exclusive_creation") is True
                and row.get("same_inode_readback_verified") is True
                and row.get("path")
                == "<FRESH_PRIVATE_TMP>/" + PHASE_NAMES[index]
                + "/source/" + relative,
                "reject an omitted, crossed, stale, or renamed V12 source: "
                + relative)
        identity = (row["device"], row["inode"])
        require(identity not in actual_inodes,
                "require nine genuinely distinct private V12 source inodes")
        actual_inodes.add(identity)
        if relative in {"candidates/rust_candidate.py",
                        "candidates/rust/py_bridge.c"}:
            overlay = row.get("source_overlay")
            require(type(overlay) is dict and overlay.get("status") == "PASS"
                    and overlay.get("phase") == PHASE_NAMES[index]
                    and overlay.get("source_apply_count") == 1
                    and overlay.get("candidate_imports", 0) == 0,
                    "require one real phase-owned first-party source overlay")
            root = overlay.get("snapshot_root")
            require(type(root) is str
                    and root.startswith("/tmp/rebar-phase2-native-build-v9-rust-")
                    and root.endswith("/" + PHASE_NAMES[index] + "/source")
                    and ".." not in Path(root).parts,
                    "reject a substituted actual V12 private phase root")
            if snapshot_root is None:
                snapshot_root = root
            require(snapshot_root == root,
                    "bind both corrected overlays to the same real phase root")
            if relative == "candidates/rust_candidate.py":
                require(overlay.get("schema")
                        == "rebar-phase2-owned-rust-public-contract-source-repair-v2-private-snapshot-application"
                        and overlay.get("source_sha256") == PUBLIC_REPAIR["source"][1]
                        and overlay.get("protocol_sha256") == PUBLIC_REPAIR["protocol"][1]
                        and overlay.get("contract_sha256") == PUBLIC_REPAIR["contract"][1]
                        and overlay.get("derived_source_sha256")
                        == CORRECTED_PUBLIC_SHA256
                        and overlay.get("derived_source_bytes")
                        == CORRECTED_PUBLIC_BYTES
                        and overlay.get("canonical_candidate_modified") is False,
                        "reject the old 81089 V11 public adapter or a wrapper")
            else:
                require(overlay.get("derived_sha256") == BRIDGE_SOURCE_SHA256
                        and overlay.get("derived_bytes") == BRIDGE_SOURCE_BYTES
                        and overlay.get("candidate_original_modified") is False,
                        "authenticate the genuinely corrected private Rust bridge")
    require(type(snapshot_root) is str,
            "retain the authentic complete V12 source snapshot root")
    for role in ("engine", "bridge"):
        output = outputs[role]
        require_actual_native_audit(output, role)
        expected_name = ("_rust_engine.so" if role == "engine"
                         else "_rust_bridge.cpython-314-x86_64-linux-gnu.so")
        require(output.get("path")
                == "<FRESH_PRIVATE_TMP>/" + PHASE_NAMES[index]
                + "/native/" + expected_name,
                "reject a redirected native build phase")
        forensic = forensics[role]
        require(type(forensic) is dict
                and set(forensic) == {"sections", "notes", "raw_elf64"}
                and all(type(forensic[name]) is dict
                        for name in ("sections", "notes", "raw_elf64")),
                "preserve complete actual independently owned ELF forensics")
    if inspect_private:
        for relative, fingerprint, count in CORRECTED_SOURCE_OWNERS:
            row = sources[relative]
            _, actual = read_absolute(
                snapshot_root + "/" + relative, fingerprint,
                maximum=MAX_NATIVE_BYTES, exact_size=count,
                device=row["device"], inode=row["inode"],
            )
            live[relative] = actual
        native_root = snapshot_root.removesuffix("/source") + "/native"
        for role in ("engine", "bridge"):
            row = outputs[role]
            name = row["file_name"]
            _, actual = read_absolute(
                native_root + "/" + name, row["sha256"],
                maximum=MAX_NATIVE_BYTES,
                exact_size=row["size_bytes"],
                device=row["device"], inode=row["inode"],
            )
            live[role] = actual
    return {"phase": phase, "snapshot_root": snapshot_root,
            "live_owners": live, "source_owner_count": len(sources)}


def validate_v12_report(report: Any, receipt: Any,
                        archive_owner: Mapping[str, Any],
                        *, inspect_private: bool) -> dict[str, Any]:
    require(type(report) is dict and type(receipt) is dict
            and type(archive_owner) is dict,
            "require three independent actual V12 build owners")
    require(report.get("schema")
            == "rebar-phase2-owned-rust-flag-source-build-v12-actual-corrected-dual-overlay-build"
            and report.get("status") == "PASS"
            and report.get("version") == 12
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("source_sha256") == BUILD["source"][1]
            and report.get("protocol_sha256") == BUILD["protocol"][1]
            and report.get("contract_sha256") == BUILD["contract"][1]
            and report.get("phase_count") == 2
            and report.get("expected_actual_compiler_process_count") == 28
            and report.get("actual_compiler_process_count") == 28
            and report.get("public_derived_sha256") == CORRECTED_PUBLIC_SHA256
            and report.get("historical_public_derived_sha256")
            == HISTORICAL_DERIVED_PUBLIC_SHA256
            and report.get("corrected_public_overlay_apply_count") == 2
            and report.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA256
            and report.get("bridge_overlay_apply_count") == 2
            and report.get("candidate_correctness") == "NOT MEASURED"
            and report.get("candidate_qualified") is False
            and report.get("candidate_processes_started") == 0
            and report.get("candidate_imports") == 0
            and report.get("native_libraries_loaded") == 0
            and report.get("hidden_cases_read") == 0
            and report.get("clock_samples") == 0
            and report.get("timing_trials_run") == 0
            and report.get("performance") == "NOT MEASURED"
            and report.get("memory") == "NOT MEASURED"
            and report.get("holdout") == "NOT OPENED"
            and report.get("winner_selected") is False,
            "reject a V11, nonreproducible, unowned, or candidate-running V12 build")
    require(receipt.get("schema")
            == "rebar-phase2-owned-rust-flag-source-build-v12-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == LABEL
            and receipt.get("source_sha256") == BUILD["source"][1]
            and receipt.get("protocol_sha256") == BUILD["protocol"][1]
            and receipt.get("contract_sha256") == BUILD["contract"][1]
            and receipt.get("archive_relative") == BUILD["archive"][0]
            and receipt.get("archive_sha256") == BUILD["archive"][1]
            and receipt.get("archive_bytes") == BUILD["archive"][2]
            and receipt.get("uncompressed_sha256") == V12_PLAIN_SHA256
            and receipt.get("uncompressed_bytes") == V12_PLAIN_BYTES
            and receipt.get("public_derived_sha256") == CORRECTED_PUBLIC_SHA256
            and receipt.get("corrected_public_overlay_apply_count") == 2
            and receipt.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA256
            and receipt.get("bridge_overlay_apply_count") == 2
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("candidate_imports") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED",
            "never confuse V12 publication, source build, or matching status")
    publication = receipt.get("archive_publication")
    require(type(publication) is dict
            and publication.get("path") == str(ROOT / BUILD["archive"][0])
            and publication.get("sha256") == archive_owner.get("sha256")
            and publication.get("bytes") == archive_owner.get("bytes")
            and publication.get("device") == archive_owner.get("device")
            and publication.get("inode") == archive_owner.get("inode")
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True
            and type(publication.get("write_calls")) is int
            and publication["write_calls"] > 0
            and type(receipt.get("archive_directory_fsync")) is dict
            and receipt["archive_directory_fsync"].get("completed") is True,
            "bind the V12 receipt to the exact durable archive inode")
    old = report.get("frozen_context")
    require(type(old) is dict and old.get("status") == "PASS"
            and old.get("version") == 12 and old.get("family") == FAMILY
            and old.get("repository_evidence_owner_count")
            == PREVIOUS_EVIDENCE_OWNER_COUNT
            and old.get("authenticated_digest_addressed_history_paths")
            == PREVIOUS_AUTHENTICATED_REFERENCE_COUNT
            and old.get("case_execution_denominator") == CASE_COUNT
            and old.get("suite_count") == SUITE_COUNT
            and old.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and old.get("actual_rust_semantic_mismatch_count") == 1087
            and old.get("actual_rust_verified_passing_case_count") == 7438
            and old.get("actual_c_semantic_mismatch_count") == 1230
            and old.get("actual_c_verified_passing_case_count") == 7325
            and old.get("actual_zig_semantic_mismatch_count") == 2172
            and old.get("actual_zig_verified_passing_case_count") == 2847
            and old.get("qualified_candidate_count") == 0
            and old.get("corrected_public_derived_source_sha256")
            == CORRECTED_PUBLIC_SHA256
            and old.get("corrected_public_derived_source_bytes")
            == CORRECTED_PUBLIC_BYTES
            and old.get("bridge_derived_source_sha256") == BRIDGE_SOURCE_SHA256
            and old.get("bridge_derived_source_bytes") == BRIDGE_SOURCE_BYTES
            and old.get("candidate_imports") == 0
            and old.get("canonical_native_target_reads") == 0
            and old.get("canonical_native_target_stats") == 0
            and old.get("native_activations") == 0
            and old.get("hidden_cases_read") == 0
            and old.get("benchmark_files_read") == 0
            and old.get("holdout") == "NOT OPENED",
            "preserve all 149 real evidence owners and 154 original references")
    processes = report.get("compiler_processes")
    require(type(processes) is list and len(processes) == 28
            and [item.get("name") for item in processes]
            == [*PROCESS_NAMES, *PROCESS_NAMES],
            "require both complete genuine fourteen-process source-build phases")
    pids: set[int] = set()
    for process in processes:
        require(type(process) is dict
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in pids
                and process.get("exit_status") == 0
                and process.get("shell") is False
                and type(process.get("argv")) is list
                and bool(process["argv"])
                and all(type(item) is str for item in process["argv"]),
                "reject invented, failed, repeated, shell, or missing real compiler processes")
        pids.add(process["pid"])
        decode_process_stream(process, "stdout")
        decode_process_stream(process, "stderr")
    phases = report.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "require both exact independent Rust V12 build phases")
    inspected = [validate_phase(phase, index, inspect_private=inspect_private)
                 for index, phase in enumerate(phases)]
    for relative, _, _ in CORRECTED_SOURCE_OWNERS:
        first = phases[0]["fresh_source_owners"][relative]
        second = phases[1]["fresh_source_owners"][relative]
        require((first["device"], first["inode"])
                != (second["device"], second["inode"]),
                "reject reused cross-phase source inode: " + relative)
    for role in ("engine", "bridge"):
        first = phases[0]["native_outputs"][role]
        second = phases[1]["native_outputs"][role]
        require((first["device"], first["inode"])
                != (second["device"], second["inode"])
                and first["sha256"] == second["sha256"]
                and first["size_bytes"] == second["size_bytes"],
                "prove both genuinely independently reproduced native " + role)
    reproduction = report.get("reproducibility")
    require(type(reproduction) is dict
            and reproduction.get("status") == "PASS"
            and reproduction.get("byte_identical") is True
            and reproduction.get("independent_fresh_phase_count") == 2
            and reproduction.get("unique_process_count") == 28
            and reproduction.get("native_role_count") == 2
            and reproduction.get("source_owners_per_phase") == 9
            and reproduction.get("unchanged_source_owners_per_phase") == 7
            and reproduction.get("corrected_public_overlay_count") == 2
            and reproduction.get("bridge_overlay_count") == 2
            and reproduction.get("public_derived_sha256")
            == CORRECTED_PUBLIC_SHA256
            and reproduction.get("bridge_derived_sha256")
            == BRIDGE_SOURCE_SHA256
            and reproduction.get("native_libraries_loaded") == 0
            and reproduction.get("original_sources_modified") is False
            and reproduction.get("prebuilt_artifact_count") == 0,
            "reject a falsely reproducible, applied, or source-modifying V12 build")
    native = reproduction.get("native_outputs")
    require(type(native) is dict and set(native) == {"engine", "bridge"},
            "retain exactly both V12 reproduced native outputs")
    for role, expected_hash, expected_size in (
        ("engine", ENGINE_SHA256, ENGINE_BYTES),
        ("bridge", BRIDGE_SHA256, BRIDGE_BYTES),
    ):
        row = native[role]
        require(type(row) is dict and row.get("sha256") == expected_hash
                and row.get("size_bytes") == expected_size
                and row.get("fresh_independent_inode_count") == 2,
                "authenticate exact reproducible V12 native " + role)
    comparisons = reproduction.get("raw_elf_comparisons")
    require(type(comparisons) is dict
            and set(comparisons) == {"engine", "bridge"},
            "require the two complete actual native ELF comparisons")
    actual_pairs: set[tuple[str, int]] = set()
    for role, expected_hash, expected_size in (
        ("engine", ENGINE_SHA256, ENGINE_BYTES),
        ("bridge", BRIDGE_SHA256, BRIDGE_BYTES),
    ):
        row = comparisons[role]
        require(type(row) is dict
                and row.get("schema")
                == "rebar-phase2-owned-native-source-build-v7-complete-raw-elf-difference"
                and row.get("byte_identical") is True
                and row.get("phase_a_sha256") == expected_hash
                and row.get("phase_a_bytes") == expected_size
                and row.get("phase_a_sha256") == row.get("phase_b_sha256")
                and row.get("phase_a_bytes") == row.get("phase_b_bytes")
                and row.get("changed_section_count") == 0
                and row.get("changed_sections") == []
                and row.get("total_difference_span_count") == 0
                and row.get("total_differing_byte_count") == 0
                and row.get("difference_spans") == []
                and row.get("reported_span_count") == 0
                and row.get("omitted_span_count") == 0
                and row.get("report_truncated") is False,
                "reject incomplete actual Rust raw-byte reproducibility")
        actual_pairs.add((row["phase_a_sha256"], row["phase_a_bytes"]))
    require(actual_pairs == {(ENGINE_SHA256, ENGINE_BYTES),
                             (BRIDGE_SHA256, BRIDGE_BYTES)},
            "bind the raw-byte comparison to both real native V12 roles")
    return {"report": report, "receipt": receipt,
            "archive_owner": dict(archive_owner), "phases": inspected,
            "actual_process_count": len(pids), "native_roles": native}


def authenticate_v30(summary: Any, inputs: Any,
                     rust_receipt: Any) -> dict[str, Any]:
    require(type(summary) is dict and type(inputs) is dict
            and type(rust_receipt) is dict,
            "require three independently frozen previous matching documents")
    require(summary.get("schema") == "rebar-candidate-current-overview-v30-summary"
            and summary.get("status") == "PASS"
            and summary.get("full_case_denominator") == CASE_COUNT
            and summary.get("suite_count") == SUITE_COUNT
            and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and summary.get("repository_evidence_owner_count")
            == PREVIOUS_EVIDENCE_OWNER_COUNT
            and summary.get("authenticated_digest_addressed_history_paths")
            == PREVIOUS_AUTHENTICATED_REFERENCE_COUNT
            and summary.get("qualified_candidate_count") == 0
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_receipt_status") == "PASS"
            and summary.get("rust_original_campaign_receipt_pass_means")
            == "DURABLE FAILURE PUBLICATION ONLY"
            and summary.get("rust_original_campaign_case_execution_denominator")
            == CASE_COUNT
            and summary.get("rust_original_campaign_candidate_worker_count") == 13
            and summary.get("rust_original_campaign_completed_suite_count") == 13
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087
            and summary.get("rust_original_campaign_verified_passing_case_count") == 7438
            and summary.get("rust_original_campaign_infrastructure_failure_count") == 0
            and summary.get("rust_original_campaign_recovery_journal_sha256")
            == HISTORICAL_RUST_JOURNAL
            and summary.get("rust_original_campaign_all_four_original_targets_restored")
            is True
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
            and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
            and summary.get("uncompressed_rust_archive_opened_by_graph") is False
            and summary.get("uncompressed_rust_archive_bytes_read_by_graph") == 0
            and summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("final_holdout_opened") is False
            and summary.get("winner_selected") is False,
            "preserve real V30 C/Rust/Zig losses and every 149/154 owner")
    require(inputs.get("schema") == "rebar-candidate-current-overview-v30-inputs"
            and inputs.get("version") == 30
            and inputs.get("full_case_denominator") == CASE_COUNT
            and inputs.get("suite_count") == SUITE_COUNT
            and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and inputs.get("repository_evidence_owner_count")
            == PREVIOUS_EVIDENCE_OWNER_COUNT
            and inputs.get("all_digest_addressed_history_path_count")
            == PREVIOUS_AUTHENTICATED_REFERENCE_COUNT
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("actual_rust_candidate_workers") == 13
            and inputs.get("actual_rust_semantic_mismatch_count") == 1087
            and inputs.get("actual_rust_verified_passing_case_count") == 7438
            and inputs.get("actual_rust_infrastructure_failure_count") == 0
            and inputs.get("uncompressed_rust_archive_opened_by_graph") is False
            and inputs.get("uncompressed_rust_archive_bytes_read_by_graph") == 0,
            "bind the original full Rust failure to independently frozen V30 inputs")
    require(rust_receipt.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v3-durable-publication-receipt"
            and rust_receipt.get("status") == "PASS"
            and rust_receipt.get("candidate_status") == "FAIL"
            and rust_receipt.get("family") == FAMILY
            and rust_receipt.get("label")
            == "phase2-v11-rust-dual-overlay-original-p0"
            and rust_receipt.get("suite_count") == SUITE_COUNT
            and rust_receipt.get("completed_suite_count") == SUITE_COUNT
            and rust_receipt.get("case_execution_denominator") == CASE_COUNT
            and rust_receipt.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and rust_receipt.get("actual_candidate_workers") == SUITE_COUNT
            and rust_receipt.get("verified_passing_case_count") == 7438
            and rust_receipt.get("semantic_mismatch_count") == 1087
            and rust_receipt.get("infrastructure_failure_count") == 0
            and rust_receipt.get("candidate_qualified") is False
            and rust_receipt.get("recovery_journal_sha256")
            == HISTORICAL_RUST_JOURNAL
            and rust_receipt.get("all_four_original_targets_restored") is True
            and rust_receipt.get("restoration_verified_before_publication") is True
            and rust_receipt.get("uncompressed_bytes") == 192335385
            and rust_receipt.get("group_atomic") is False
            and rust_receipt.get("hidden_cases_read") == 0
            and rust_receipt.get("benchmark_files_read") == 0
            and rust_receipt.get("holdout") == "NOT OPENED"
            and rust_receipt.get("performance") == "NOT MEASURED",
            "never mistake durable prior Rust failure publication for compatibility")
    archive = rust_receipt.get("archive")
    require(type(archive) is dict
            and archive.get("sha256") == HISTORICAL_RUST_ARCHIVE_SHA256
            and archive.get("size_bytes") == 5710284
            and archive.get("device") == 2064
            and archive.get("inode") == 524624
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("streaming_readback_verified") is True,
            "authenticate historical archive from its tiny receipt without opening it")
    restored = rust_receipt.get("restored_original_targets")
    require(type(restored) is dict and set(restored) == set(ROLE_ORDER),
            "preserve all four independently proved genuine original Rust targets")
    for role in ROLE_ORDER:
        expected = ORIGINALS[role]
        item = restored[role]
        require(type(item) is dict
                and item.get("relative") == expected["relative"]
                and item.get("sha256") == expected["sha256"]
                and item.get("size_bytes") == expected["bytes"]
                and item.get("device") == expected["device"]
                and item.get("inode") == expected["inode"]
                and item.get("mode") == expected["mode"]
                and item.get("uid") == expected["uid"]
                and item.get("nlink") == expected["nlink"],
                "reject a stale copied original Rust owner: " + role)
    included = inputs.get("actual_complete_rust_campaign")
    require(type(included) is dict and included.get("status") == "FAIL"
            and included.get("semantic_mismatch_count") == 1087
            and included.get("verified_passing_case_count") == 7438
            and included.get("publication_receipt") == rust_receipt,
            "authenticate the exact prior independent Rust receipt twice")
    return {
        "historical_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
        PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
        "rust_semantic_mismatch_count": 1087,
        "rust_verified_passing_case_count": 7438,
        "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_semantic_mismatch_count": 2172,
        "zig_verified_passing_case_count": 2847,
        "historical_rust_matching_archive_opened": False,
        "historical_rust_matching_archive_bytes_read": 0,
        "qualified_candidate_count": 0,
    }


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None,
                   *, retain: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    source_raw, source_owner = read_owned(
        (SOURCE_RELATIVE, checked_digest(source_pin, "V4 campaign source"),
         _exact_source_size(source_pin)), maximum=MAX_SOURCE_BYTES)
    del source_raw
    protocol_raw, protocol_owner = read_owned(
        (PROTOCOL_RELATIVE, checked_digest(protocol_pin, "V4 campaign protocol"),
         _exact_protocol_size(protocol_pin)), maximum=MAX_SOURCE_BYTES)
    del protocol_raw
    frozen_owner: dict[str, Any] | None = None
    if contract_pin is not None:
        raw, frozen_owner = read_owned(
            (CONTRACT_RELATIVE, checked_digest(contract_pin, "V4 campaign contract"),
             _exact_contract_size(contract_pin)), maximum=MAX_SOURCE_BYTES)
        validate_contract(strict_document(raw, "frozen Rust V4 machine contract"),
                          source_pin, protocol_pin)
    authenticated: dict[str, dict[str, Any]] = {}
    content: dict[str, bytes] = {}
    for group in (PRODUCER, PUBLICATION, V2, V3, V30, BUILD, PUBLIC_REPAIR):
        for item in group.values():
            if item[0] in authenticated or item[0] == BUILD["archive"][0]:
                continue
            maximum = (MAX_RECEIPT_BYTES if item == BUILD["receipt"]
                       else MAX_GRAPH_BYTES if item in V30.values()
                       else MAX_SOURCE_BYTES)
            private = item == BUILD["receipt"]
            raw, owner = read_owned(item, maximum=maximum, private=private)
            authenticated[item[0]] = owner
            content[item[0]] = raw
    previous_raw, previous_owner = read_owned(
        HISTORICAL_RUST_RECEIPT, maximum=MAX_RECEIPT_BYTES, private=True)
    authenticated[HISTORICAL_RUST_RECEIPT[0]] = previous_owner
    previous = strict_document(previous_raw, "exact historical Rust V3 failure receipt")
    summary = strict_document(content[V30["summary"][0]], "actual V30 summary")
    graph_inputs = strict_document(content[V30["inputs"][0]], "actual V30 inputs")
    history = authenticate_v30(summary, graph_inputs, previous)
    build_receipt = strict_document(
        content[BUILD["receipt"][0]], "actual durable V12 build receipt")
    compressed, archive_owner = read_owned(
        BUILD["archive"], maximum=MAX_BUILD_ARCHIVE_BYTES, private=True)
    require((archive_owner["device"], archive_owner["inode"])
            != (authenticated[BUILD["receipt"][0]]["device"],
                authenticated[BUILD["receipt"][0]]["inode"]),
            "require separately created genuine V12 archive and receipt inodes")
    plain = bounded_build_gzip(
        compressed, expected_sha256=V12_PLAIN_SHA256,
        expected_size=V12_PLAIN_BYTES)
    report = strict_document(plain, "complete bounded actual V12 build")
    build = validate_v12_report(report, build_receipt, archive_owner,
                                inspect_private=True)
    old_contract = strict_document(content[V3["contract"][0]],
                                   "unchanged historical Rust V3 source freeze")
    require(old_contract.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v3-recoverable-source-freeze"
            and old_contract.get("version") == 3
            and old_contract.get("family") == FAMILY
            and old_contract.get("source", {}).get("sha256") == V3["source"][1]
            and old_contract.get("protocol", {}).get("sha256")
            == V3["protocol"][1]
            and old_contract.get("original_oracle", {}).get("suite_count")
            == SUITE_COUNT
            and old_contract["original_oracle"].get("case_execution_denominator")
            == CASE_COUNT
            and old_contract["original_oracle"].get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and old_contract["original_oracle"].get("nested_interpreter_events")
            == 394,
            "preserve the actual committed original Rust recovery freeze")
    producer_contract = strict_document(content[PRODUCER["contract"][0]],
                                        "immutable original P0 producer")
    require(producer_contract.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and producer_contract.get("family_count") == 6
            and producer_contract.get("suite_count") == SUITE_COUNT
            and producer_contract.get("case_execution_denominator") == CASE_COUNT,
            "require the unchanged actual complete upstream case producer")
    repair_contract = strict_document(content[PUBLIC_REPAIR["contract"][0]],
                                      "exact corrected private public repair")
    require(repair_contract.get("schema")
            == "rebar-phase2-owned-rust-public-contract-source-repair-v2-source-freeze"
            and type(repair_contract.get("repair")) is dict
            and type(repair_contract["repair"].get("derived")) is dict
            and repair_contract["repair"]["derived"].get("sha256")
            == CORRECTED_PUBLIC_SHA256
            and repair_contract["repair"]["derived"].get("bytes")
            == CORRECTED_PUBLIC_BYTES
            and repair_contract["repair"]["derived"].get("materialized")
            is False
            and repair_contract["repair"]["derived"].get("path")
            == "candidates/rust_candidate.py",
            "bind actual matching to the corrected V2 f8afb public adapter")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "read-only verification may never import a candidate")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": 4, "family": FAMILY,
        "mode": "READ-ONLY CORRECTED V12 ORIGINAL RUST SOURCE FREEZE",
        "source": source_owner, "protocol": protocol_owner,
        "contract": frozen_owner,
        "authenticated_support_owner_count": len(authenticated) + 1,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_ordered_suites": [
            {"id": name, "case_execution_count": count}
            for name, count in SUITES
        ],
        "original_producer_source_sha256": PRODUCER["source"][1],
        "original_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_producer_contract_sha256": PRODUCER["contract"][1],
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "actual_v12_build_archive_bytes": BUILD["archive"][2],
        "actual_v12_build_uncompressed_bytes": V12_PLAIN_BYTES,
        "actual_v12_build_phase_count": 2,
        "actual_v12_compiler_process_count": build["actual_process_count"],
        "actual_v12_corrected_public_overlay_count": 2,
        "actual_v12_bridge_overlay_count": 2,
        "actual_v12_source_owner_count_per_phase": 9,
        "actual_v12_independent_native_roles": 2,
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "native_engine_bytes": ENGINE_BYTES,
        "native_bridge_bytes": BRIDGE_BYTES,
        "actual_evidence_owner_count_before_new_campaign":
        ACTUAL_EVIDENCE_OWNER_COUNT,
        "actual_authenticated_reference_count_before_new_campaign":
        ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "new_v12_build_evidence_owner_count": 2,
        "new_campaign_evidence_owner_count": 0,
        "published_v30_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
        "published_v30_authenticated_reference_count":
        PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_history": history,
        "historical_rust_failure_receipt_sha256":
        HISTORICAL_RUST_RECEIPT[1],
        "historical_rust_failure_archive_sha256":
        HISTORICAL_RUST_ARCHIVE_SHA256,
        "historical_rust_failure_archive_decompressed": False,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "original_target_count": len(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "nested_case_count": 128,
        "nested_interpreter_event_count": 394,
        "nested_interpreters_created": 11,
        "group_atomic": False,
        **zero_effects(),
    }
    kept = {"build": build, "summary": summary,
            "historical_receipt": previous,
            "owners": authenticated} if retain else {}
    return result, kept


def _exact_source_size(fingerprint: str) -> int:
    del fingerprint
    return os.path.getsize(str(ROOT / SOURCE_RELATIVE))


def _exact_protocol_size(fingerprint: str) -> int:
    del fingerprint
    return os.path.getsize(str(ROOT / PROTOCOL_RELATIVE))


def _exact_contract_size(fingerprint: str) -> int:
    del fingerprint
    return os.path.getsize(str(ROOT / CONTRACT_RELATIVE))


class SourceWall:
    """Physically deny every effect while testing hostile synthetic objects."""

    def __init__(self) -> None:
        self.blocked: dict[str, int] = {}
        self.originals: list[tuple[Any, str, Any]] = []

    def install(self, owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def blocked(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            self.blocked[counter] = self.blocked.get(counter, 0) + 1
            raise SourceOnlyViolation("source-only V4 blocks actual " + counter)

        self.originals.append((owner, name, previous))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceWall:
        for owner, name in ((builtins, "open"), (io, "open"),
                            (os, "open"), (os, "stat"), (os, "lstat")):
            self.install(owner, name, "filesystem_reads")
        for name in ("write", "unlink", "remove", "replace", "link",
                     "mkdir", "rmdir", "fsync", "fchmod", "urandom"):
            self.install(os, name, "filesystem_mutations")
        for owner, name, counter in (
            (subprocess, "run", "processes"),
            (subprocess, "Popen", "processes"),
            (importlib, "import_module", "candidate_imports"),
            (ctypes, "CDLL", "native_library_loads"),
            (tempfile, "mkdtemp", "recovery_roots"),
            (socket, "socket", "network_requests"),
            (threading.Thread, "start", "threads"),
            (locale, "setlocale", "locale_transitions"),
            (signal, "signal", "signal_handlers"),
            (signal, "pthread_sigmask", "signal_masks"),
            (fcntl, "flock", "recovery_locks"),
        ):
            self.install(owner, name, counter)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            self.install(time, name, "clocks")
        return self

    def __exit__(self, kind: Any, value: Any, detail: Any) -> bool:
        del kind, value, detail
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        return False


def _expect_rejected(name: str, operation: Any,
                     rejected: list[str]) -> None:
    try:
        operation()
    except (CampaignError, ValueError, TypeError, OverflowError,
            UnicodeError, RecursionError):
        rejected.append(name)
        return
    raise CampaignError("accepted hostile source-only case: " + name)


def _synthetic_stream(name: str, channel: str) -> dict[str, Any]:
    raw = ("synthetic-v12-" + name + "-" + channel).encode("ascii")
    return {channel + "_base64": base64.b64encode(raw).decode("ascii"),
            channel + "_bytes": len(raw),
            channel + "_sha256": digest(raw)}


def synthetic_v12_fixture() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    phases = []
    process_records = []
    root = "/tmp/rebar-phase2-native-build-v9-rust-synthetic-v4"
    for phase_index, phase_name in enumerate(PHASE_NAMES):
        sources: dict[str, Any] = {}
        for index, (relative, fingerprint, count) in enumerate(
                CORRECTED_SOURCE_OWNERS):
            row: dict[str, Any] = {
                "path": "<FRESH_PRIVATE_TMP>/" + phase_name
                + "/source/" + relative,
                "sha256": fingerprint, "bytes": count,
                "device": 2049, "inode": 100000 + phase_index * 100 + index,
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "file_fsync_completed": relative in {
                    "candidates/rust_candidate.py", "candidates/rust/py_bridge.c"},
            }
            if relative == "candidates/rust_candidate.py":
                row["source_overlay"] = {
                    "schema": "rebar-phase2-owned-rust-public-contract-source-repair-v2-private-snapshot-application",
                    "status": "PASS", "phase": phase_name,
                    "source_apply_count": 1,
                    "snapshot_root": root + "/" + phase_name + "/source",
                    "source_sha256": PUBLIC_REPAIR["source"][1],
                    "protocol_sha256": PUBLIC_REPAIR["protocol"][1],
                    "contract_sha256": PUBLIC_REPAIR["contract"][1],
                    "derived_source_sha256": CORRECTED_PUBLIC_SHA256,
                    "derived_source_bytes": CORRECTED_PUBLIC_BYTES,
                    "candidate_imports": 0,
                    "canonical_candidate_modified": False,
                }
            elif relative == "candidates/rust/py_bridge.c":
                row["source_overlay"] = {
                    "status": "PASS", "phase": phase_name,
                    "source_apply_count": 1,
                    "snapshot_root": root + "/" + phase_name + "/source",
                    "derived_sha256": BRIDGE_SOURCE_SHA256,
                    "derived_bytes": BRIDGE_SOURCE_BYTES,
                    "candidate_imports": 0,
                    "candidate_original_modified": False,
                }
            sources[relative] = row
        outputs: dict[str, Any] = {}
        for offset, (role, fingerprint, count, filename) in enumerate((
            ("engine", ENGINE_SHA256, ENGINE_BYTES, "_rust_engine.so"),
            ("bridge", BRIDGE_SHA256, BRIDGE_BYTES,
             "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
        )):
            audit = {
                "role": role,
                "cross_family_dependency_count": 0,
                "external_regex_dependency_count": 0,
                "exports": (list(RUST_EXPORTS) if role == "engine"
                            else ["PyInit__rust_bridge"]),
                "required_exports": (list(RUST_EXPORTS) if role == "engine"
                                     else ["PyInit__rust_bridge"]),
                "needed": (["ld-linux-x86-64.so.2", "libc.so.6",
                            "libgcc_s.so.1"] if role == "engine"
                           else ["_rust_engine.so", "libc.so.6"]),
                "runpath": ([] if role == "engine" else ["$ORIGIN"]),
            }
            outputs[role] = {
                "family": FAMILY, "role": role, "sha256": fingerprint,
                "size_bytes": count, "device": 2049,
                "inode": 200000 + phase_index * 100 + offset,
                "file_name": filename,
                "path": "<FRESH_PRIVATE_TMP>/" + phase_name
                + "/native/" + filename,
                "candidate_imported": False,
                "prebuilt_artifact_read": False,
                "audit": audit,
            }
        phases.append({
            "name": phase_name,
            "fresh_source_owners": sources,
            "native_outputs": outputs,
            "native_forensics": {
                role: {"sections": {}, "notes": {}, "raw_elf64": {}}
                for role in ("engine", "bridge")
            },
            "candidate_imports": 0, "candidate_processes_started": 0,
            "hidden_cases_read": 0, "timing_trials_run": 0,
            "native_libraries_loaded": 0,
        })
        for offset, name in enumerate(PROCESS_NAMES):
            record = {
                "name": name, "pid": 300000 + phase_index * 100 + offset,
                "exit_status": 0, "shell": False,
                "argv": ["/independently-pinned-synthetic/" + name],
                **_synthetic_stream(name, "stdout"),
                **_synthetic_stream(name, "stderr"),
            }
            process_records.append(record)
    previous = {
        "status": "PASS", "version": 12, "family": FAMILY,
        "repository_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
        "authenticated_digest_addressed_history_paths":
        PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "suite_count": SUITE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "actual_rust_semantic_mismatch_count": 1087,
        "actual_rust_verified_passing_case_count": 7438,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "actual_zig_semantic_mismatch_count": 2172,
        "actual_zig_verified_passing_case_count": 2847,
        "qualified_candidate_count": 0,
        "corrected_public_derived_source_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_public_derived_source_bytes": CORRECTED_PUBLIC_BYTES,
        "bridge_derived_source_sha256": BRIDGE_SOURCE_SHA256,
        "bridge_derived_source_bytes": BRIDGE_SOURCE_BYTES,
        "candidate_imports": 0,
        "canonical_native_target_reads": 0,
        "canonical_native_target_stats": 0,
        "native_activations": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "holdout": "NOT OPENED",
    }
    reproduction = {
        "status": "PASS", "byte_identical": True,
        "independent_fresh_phase_count": 2,
        "unique_process_count": 28,
        "native_role_count": 2,
        "source_owners_per_phase": 9,
        "unchanged_source_owners_per_phase": 7,
        "corrected_public_overlay_count": 2,
        "bridge_overlay_count": 2,
        "public_derived_sha256": CORRECTED_PUBLIC_SHA256,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA256,
        "native_libraries_loaded": 0,
        "original_sources_modified": False,
        "prebuilt_artifact_count": 0,
        "native_outputs": {
            "engine": {"sha256": ENGINE_SHA256, "size_bytes": ENGINE_BYTES,
                       "fresh_independent_inode_count": 2},
            "bridge": {"sha256": BRIDGE_SHA256, "size_bytes": BRIDGE_BYTES,
                       "fresh_independent_inode_count": 2},
        },
        "raw_elf_comparisons": {
            role: {
             "schema": "rebar-phase2-owned-native-source-build-v7-complete-raw-elf-difference",
             "byte_identical": True,
             "phase_a_sha256": fingerprint, "phase_b_sha256": fingerprint,
             "phase_a_bytes": size, "phase_b_bytes": size,
             "changed_section_count": 0, "changed_sections": [],
             "total_difference_span_count": 0,
             "total_differing_byte_count": 0, "difference_spans": [],
             "reported_span_count": 0, "omitted_span_count": 0,
             "report_truncated": False}
            for role, fingerprint, size in (
                ("bridge", BRIDGE_SHA256, BRIDGE_BYTES),
                ("engine", ENGINE_SHA256, ENGINE_BYTES),
            )
        },
    }
    archive_owner = {
        "path": str(ROOT / BUILD["archive"][0]),
        "relative": BUILD["archive"][0],
        "sha256": BUILD["archive"][1], "bytes": BUILD["archive"][2],
        "size_bytes": BUILD["archive"][2], "device": 2064,
        "inode": 524643, "mode": 0o600, "uid": 1000, "nlink": 1,
    }
    report = {
        "schema": "rebar-phase2-owned-rust-flag-source-build-v12-actual-corrected-dual-overlay-build",
        "status": "PASS", "version": 12, "family": FAMILY,
        "label": LABEL, "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "phase_count": 2,
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28,
        "public_derived_sha256": CORRECTED_PUBLIC_SHA256,
        "historical_public_derived_sha256": HISTORICAL_DERIVED_PUBLIC_SHA256,
        "corrected_public_overlay_apply_count": 2,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA256,
        "bridge_overlay_apply_count": 2,
        "frozen_context": previous,
        "compiler_processes": process_records,
        "phases": phases, "reproducibility": reproduction,
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt = {
        "schema": "rebar-phase2-owned-rust-flag-source-build-v12-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS", "family": FAMILY,
        "label": LABEL, "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "archive_relative": BUILD["archive"][0],
        "archive_sha256": BUILD["archive"][1],
        "archive_bytes": BUILD["archive"][2],
        "archive_publication": {
            "path": archive_owner["path"],
            "sha256": archive_owner["sha256"],
            "bytes": archive_owner["bytes"],
            "device": archive_owner["device"],
            "inode": archive_owner["inode"],
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "write_calls": 1,
        },
        "archive_directory_fsync": {"completed": True},
        "uncompressed_sha256": V12_PLAIN_SHA256,
        "uncompressed_bytes": V12_PLAIN_BYTES,
        "public_derived_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_public_overlay_apply_count": 2,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA256,
        "bridge_overlay_apply_count": 2,
        "actual_compiler_process_count": 28,
        "expected_actual_compiler_process_count": 28,
        "candidate_correctness": "NOT MEASURED",
        "candidate_processes_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }
    return report, receipt, archive_owner


def source_self_test(source_pin: str, protocol_pin: str,
                     contract_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "synthetic V4 source")
    checked_digest(protocol_pin, "synthetic V4 protocol")
    checked_digest(contract_pin, "synthetic V4 machine contract")
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceWall() as wall:
        contract = protocol_document(source_pin, protocol_pin)
        require(validate_contract(copy.deepcopy(contract), source_pin,
                                  protocol_pin) == contract,
                "accept the one exact pure corrected Rust V4 source freeze")
        accepted.append("accept-exact-corrected-rust-v12-source-freeze")
        require(sum(count for _, count in SUITES) == CASE_COUNT
                and len(SUITES) == SUITE_COUNT,
                "retain all thirteen unchanged original suite denominators")
        accepted.append("accept-all-thirteen-original-suites-and-31237-cases")
        report, receipt, archive = synthetic_v12_fixture()
        observed = validate_v12_report(report, receipt, archive,
                                       inspect_private=False)
        require(observed["actual_process_count"] == 28
                and len(observed["phases"]) == 2,
                "accept both complete synthetic independent source-build phases")
        accepted.append("accept-two-exact-corrected-nine-owner-build-phases")
        accepted.append("accept-twenty-eight-distinct-source-build-processes")
        accepted.append("accept-reproduced-v11-identical-native-bytes-only-with-v12-proof")
        accepted.append("accept-corrected-private-f8afb-public-adapter")
        accepted.append("accept-both-real-own-engine-elf-export-profiles")
        accepted.append("accept-149-plus-two-real-evidence-owners")
        accepted.append("accept-154-plus-two-real-authenticated-references")
        accepted.append("accept-four-exact-original-inode-identities")
        accepted.append("accept-authentic-394-call-original-interpreter-policy")
        accepted.append("accept-publication-pass-only-as-durable-publication")
        bad_contract_fields: tuple[tuple[str, Any], ...] = (
            ("schema", SCHEMA),
            ("status", "PASS"), ("version", 3), ("family", "c"),
            ("campaign_label", "phase2-v11-rust-dual-overlay-original-p0"),
        )
        for field, value in bad_contract_fields:
            hostile = copy.deepcopy(contract)
            hostile[field] = value
            _expect_rejected("reject-contract-" + field,
                             lambda item=hostile: validate_contract(
                                 item, source_pin, protocol_pin), rejected)
        for index, (name, count) in enumerate(SUITES):
            for changed_name, changed_count, label in (
                (name + "-forged", count, "identity"),
                (name, count + 1, "denominator"),
            ):
                hostile = copy.deepcopy(contract)
                hostile["original_oracle"]["source_ordered_suites"][index] = {
                    "id": changed_name, "case_execution_count": changed_count}
                _expect_rejected(
                    "reject-original-" + name + "-" + label,
                    lambda item=hostile: validate_contract(
                        item, source_pin, protocol_pin), rejected)
        for section, field, value, name in (
            ("original_oracle", "case_execution_denominator", 31236,
             "omit-original-case"),
            ("original_oracle", "suite_count", 12, "omit-original-suite"),
            ("original_oracle", "named_private_waiver_count", 12,
             "add-private-waiver"),
            ("original_oracle", "nested_interpreter_events", 385,
             "accept-old-failed-nested-lifecycle"),
            ("original_oracle", "canonical_public_module",
             "candidates.repaired_rust_candidate", "accept-wrapper-module"),
            ("original_oracle", "stdlib_re_fallback_allowed", True,
             "accept-standard-library-fallback"),
            ("original_oracle", "external_regex_dependency_allowed", True,
             "accept-external-regex-engine"),
            ("original_oracle", "cross_family_matching_allowed", True,
             "accept-borrowed-candidate-engine"),
            ("current_historical_accounting",
             "actual_evidence_owner_count_before_new_campaign", 150,
             "miscount-actual-owner"),
            ("current_historical_accounting",
             "actual_authenticated_reference_count_before_new_campaign", 155,
             "miscount-actual-reference"),
            ("preserved_v30_history", "actual_rust_semantic_mismatch_count",
             1086, "hide-original-rust-loss"),
            ("preserved_v30_history", "actual_c_semantic_mismatch_count", 0,
             "hide-original-c-loss"),
            ("preserved_v30_history", "actual_zig_semantic_mismatch_count", 0,
             "hide-original-zig-loss"),
            ("public_recovery", "group_atomic", True,
             "falsely-claim-group-atomic-replacement"),
            ("public_recovery", "sigkill_automatically_recovered", True,
             "claim-automatic-sigkill-recovery"),
            ("public_recovery", "power_failure_automatically_recovered", True,
             "claim-automatic-power-loss-recovery"),
            ("future_lossless_publication", "publication_pass_means",
             "CANDIDATE PASSED", "equate-publication-and-correctness"),
        ):
            hostile = copy.deepcopy(contract)
            hostile[section][field] = value
            _expect_rejected("reject-" + name,
                             lambda item=hostile: validate_contract(
                                 item, source_pin, protocol_pin), rejected)
        for role in ROLE_ORDER:
            for field, value in (("inode", 999999), ("device", 999999),
                                 ("mode", 0o777), ("nlink", 2),
                                 ("sha256", "0" * 64)):
                hostile = copy.deepcopy(contract)
                record = next(item for item in
                              hostile["four_original_target_owners"]
                              if item["role"] == role)
                record["original"][field] = value
                _expect_rejected("reject-" + role + "-original-" + field,
                                 lambda item=hostile: validate_contract(
                                     item, source_pin, protocol_pin), rejected)
        for field, value, tag in (
            ("schema", "rebar-phase2-owned-native-source-build-v11", "v11-schema"),
            ("status", "FAIL", "failed-build"),
            ("family", "c", "foreign-family"),
            ("label", "phase2-v11-rust-dual-overlay", "stale-build-label"),
            ("source_sha256", V3["source"][1], "stale-source"),
            ("phase_count", 1, "missing-phase"),
            ("actual_compiler_process_count", 27, "missing-real-process"),
            ("public_derived_sha256", HISTORICAL_DERIVED_PUBLIC_SHA256,
             "old-81089-public-adapter"),
            ("corrected_public_overlay_apply_count", 1,
             "missing-corrected-private-apply"),
            ("bridge_overlay_apply_count", 1, "missing-bridge-apply"),
            ("candidate_qualified", True, "build-as-qualified-candidate"),
            ("candidate_imports", 1, "source-build-imported-candidate"),
            ("hidden_cases_read", 1, "source-build-opened-holdout"),
            ("clock_samples", 1, "source-build-timed-matching"),
        ):
            hostile = copy.deepcopy(report)
            hostile[field] = value
            _expect_rejected("reject-real-v12-" + tag,
                             lambda item=hostile: validate_v12_report(
                                 item, receipt, archive,
                                 inspect_private=False), rejected)
        for phase_index, phase_name in enumerate(PHASE_NAMES):
            for relative, _, _ in CORRECTED_SOURCE_OWNERS:
                hostile = copy.deepcopy(report)
                hostile["phases"][phase_index]["fresh_source_owners"][relative]["sha256"] = "0" * 64
                _expect_rejected(
                    "reject-" + phase_name + "-source-"
                    + relative.replace("/", "-"),
                    lambda item=hostile: validate_v12_report(
                        item, receipt, archive,
                        inspect_private=False), rejected)
            for role in ("engine", "bridge"):
                for field, value in (("sha256", "0" * 64),
                                     ("size_bytes", 1),
                                     ("inode", 0),
                                     ("candidate_imported", True),
                                     ("prebuilt_artifact_read", True)):
                    hostile = copy.deepcopy(report)
                    hostile["phases"][phase_index]["native_outputs"][role][field] = value
                    _expect_rejected(
                        "reject-" + phase_name + "-" + role + "-" + field,
                        lambda item=hostile: validate_v12_report(
                            item, receipt, archive,
                            inspect_private=False), rejected)
                for field, value in (("cross_family_dependency_count", 1),
                                     ("external_regex_dependency_count", 1)):
                    hostile = copy.deepcopy(report)
                    hostile["phases"][phase_index]["native_outputs"][role]["audit"][field] = value
                    _expect_rejected(
                        "reject-" + phase_name + "-" + role + "-" + field,
                        lambda item=hostile: validate_v12_report(
                            item, receipt, archive,
                            inspect_private=False), rejected)
        for field, value in (("status", "FAIL"), ("build_status", "FAIL"),
                             ("family", "zig"),
                             ("archive_sha256", "0" * 64),
                             ("uncompressed_bytes", V12_PLAIN_BYTES - 1),
                             ("public_derived_sha256",
                              HISTORICAL_DERIVED_PUBLIC_SHA256),
                             ("candidate_processes_started", 1),
                             ("hidden_cases_read", 1)):
            hostile = copy.deepcopy(receipt)
            hostile[field] = value
            _expect_rejected("reject-v12-build-receipt-" + field,
                             lambda item=hostile: validate_v12_report(
                                 report, item, archive,
                                 inspect_private=False), rejected)
        for index in (0, 1, 13, 14, 27):
            hostile = copy.deepcopy(report)
            hostile["compiler_processes"][index]["exit_status"] = 1
            _expect_rejected("reject-failed-real-v12-process-" + str(index),
                             lambda item=hostile: validate_v12_report(
                                 item, receipt, archive,
                                 inspect_private=False), rejected)
        duplicate = copy.deepcopy(report)
        duplicate["compiler_processes"][1]["pid"] = (
            duplicate["compiler_processes"][0]["pid"])
        _expect_rejected("reject-duplicate-real-v12-process-identity",
                         lambda: validate_v12_report(
                             duplicate, receipt, archive,
                             inspect_private=False), rejected)
        for raw, tag in ((b'{"same":1,"same":2}\n', "duplicate-json"),
                         (b'{"number":NaN}\n', "json-nan"),
                         (b'{"number":Infinity}\n', "json-infinity"),
                         (b'{ "same": 1 }\n', "noncanonical-json")):
            _expect_rejected("reject-" + tag,
                             lambda value=raw: strict_document(
                                 value, "synthetic hostile"), rejected)
        hostile_raw = gzip.compress(b"synthetic\n", mtime=0)
        for raw, tag in ((hostile_raw + hostile_raw, "two-gzip-members"),
                         (hostile_raw[:-3], "truncated-gzip"),
                         (hostile_raw + b"trailing", "trailing-gzip")):
            _expect_rejected("reject-" + tag,
                             lambda value=raw: bounded_build_gzip(
                                 value, expected_sha256=digest(b"synthetic\n"),
                                 expected_size=len(b"synthetic\n")), rejected)
        actions = (
            ("file-open", lambda: builtins.open("forbidden-v4")),
            ("os-open", lambda: os.open("forbidden-v4", os.O_RDONLY)),
            ("candidate-import", lambda: importlib.import_module(
                "candidates.rust_candidate")),
            ("native-load", lambda: ctypes.CDLL("forbidden-v4.so")),
            ("process", lambda: subprocess.run(("forbidden-v4",))),
            ("worker", lambda: subprocess.Popen(("forbidden-v4",))),
            ("recovery-root", lambda: tempfile.mkdtemp()),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("locale", lambda: locale.setlocale(locale.LC_CTYPE)),
            ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)),
            ("signal-mask", lambda: signal.pthread_sigmask(
                signal.SIG_BLOCK, {signal.SIGINT})),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("replace", lambda: os.replace("forbidden-a", "forbidden-b")),
            ("hardlink", lambda: os.link("forbidden-a", "forbidden-b")),
            ("journal-fsync", lambda: os.fsync(0)),
            ("random-root", lambda: os.urandom(16)),
            ("clock", lambda: time.perf_counter()),
        )
        for tag, action in actions:
            _expect_rejected("block-actual-" + tag, action, rejected)
        require(len(rejected) >= 100,
                "run substantial hostile V12, owner, original-case and effect controls")
        blocked = dict(wall.blocked)
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "version": 4, "synthetic": True,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_source_only_effects": blocked,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "actual_v12_source_build_process_count": 28,
        "actual_evidence_owner_count_before_new_campaign":
        ACTUAL_EVIDENCE_OWNER_COUNT,
        "actual_authenticated_reference_count_before_new_campaign":
        ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "historical_rust_semantic_mismatch_count": 1087,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_zig_semantic_mismatch_count": 2172,
        "group_atomic": False,
        **zero_effects(),
    }


def load_frozen_module(item: tuple[str, str, int], name: str) -> types.ModuleType:
    raw, _ = read_owned(item)
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
    return module


def patched_v2_helpers() -> types.ModuleType:
    v2 = load_frozen_module(V2["source"],
                            "_rebar_frozen_rust_v2_helpers_for_actual_v4")
    require(v2.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v2"
            and tuple(v2.ROLE_ORDER) == ROLE_ORDER
            and tuple(v2.RESTORATION_ORDER) == RESTORATION_ORDER
            and tuple(v2.ORIGINAL_RUST_SOURCE_OWNERS)
            == ORIGINAL_SOURCE_OWNERS
            and v2.REPAIRED_SOURCE_OWNERS[0][1]
            == HISTORICAL_DERIVED_PUBLIC_SHA256
            and all(v2.ROLES[role]["original"] == ORIGINALS[role]
                    for role in ROLE_ORDER),
            "authenticate immutable historical helpers without running V2")
    roles = copy.deepcopy(v2.ROLES)
    corrected = {
        "bridge_source": (BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
        "adapter": (CORRECTED_PUBLIC_SHA256, CORRECTED_PUBLIC_BYTES),
        "engine": (ENGINE_SHA256, ENGINE_BYTES),
        "bridge": (BRIDGE_SHA256, BRIDGE_BYTES),
    }
    for role, (fingerprint, count) in corrected.items():
        roles[role]["sha256"] = fingerprint
        roles[role]["bytes"] = count
    v2.ROLES = roles
    v2.REPAIRED_SOURCE_OWNERS = CORRECTED_SOURCE_OWNERS
    v2.LABEL = LABEL
    return v2


def corrected_rust_family(producer: types.ModuleType) -> Any:
    original = producer.family_spec(FAMILY)
    require(tuple(original.source_owners) == ORIGINAL_SOURCE_OWNERS
            and tuple(producer.OWNED_SOURCES[FAMILY])
            == ORIGINAL_SOURCE_OWNERS
            and original.module == "candidates.rust_candidate"
            and original.adapter_relative == "candidates/rust_candidate.py"
            and original.bridge_module == "candidates._rust_bridge"
            and original.combined_native is False
            and original.owned_ctypes is False,
            "authenticate the exact original Rust module, no wrapper, and own bridge")
    corrected = producer.FamilySpec(
        original.name, original.module, original.adapter_relative,
        original.bridge_module, original.engine_relative,
        original.bridge_relative, CORRECTED_SOURCE_OWNERS,
        original.combined_native, original.owned_ctypes,
    )
    producer.OWNED_SOURCES[FAMILY] = CORRECTED_SOURCE_OWNERS
    producer.FAMILIES[FAMILY] = corrected
    require(producer.family_spec(FAMILY) is corrected,
            "rebind only genuine corrected same-family original source owners")
    original_bootstrap = producer.interpreter_bootstrap_source

    def corrected_bootstrap(spec: Any, pins: Any, source_pins: Any,
                            *, owner: str, producer_sha256: str) -> str:
        program = original_bootstrap(spec, pins, source_pins,
                                    owner=owner,
                                    producer_sha256=producer_sha256)
        marker = "_six_producer.install_owned_interpreter_guard("
        require(program.count(marker) == 1,
                "preserve the unique frozen upstream interpreter guard")
        prefix = (
            "_six_original = _six_producer.FAMILIES['rust']\n"
            "assert _six_original.name == 'rust'\n"
            "assert tuple(_six_producer.OWNED_SOURCES['rust']) == "
            + repr(ORIGINAL_SOURCE_OWNERS) + "\n"
            "_six_repaired_sources = " + repr(CORRECTED_SOURCE_OWNERS) + "\n"
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
        final = program.replace(marker, prefix + marker, 1)
        try:
            ast.parse(final, filename="<genuine-v12-rust-original-interpreter>")
        except (SyntaxError, ValueError, RecursionError) as error:
            raise CampaignError("reject a changed original Rust interpreter bootstrap") from error
        return final

    producer.interpreter_bootstrap_source = corrected_bootstrap
    return corrected


@contextlib.contextmanager
def installed_signal_handlers() -> Iterator[None]:
    require(threading.current_thread() is threading.main_thread(),
            "install actual controller signal handlers only in the main thread")
    previous: list[tuple[int, Any]] = []

    def handler(signum: int, frame: Any) -> None:
        del frame
        raise GracefulControllerSignal(signum)

    try:
        for name in SIGNAL_NAMES:
            number = getattr(signal, name)
            previous.append((number, signal.getsignal(number)))
            signal.signal(number, handler)
        yield
    finally:
        for number, old in reversed(previous):
            signal.signal(number, old)


@contextlib.contextmanager
def blocked_controller_signals() -> Iterator[None]:
    require(callable(getattr(signal, "pthread_sigmask", None)),
            "require genuine signal masking for each durable target mutation")
    selected = {getattr(signal, name) for name in SIGNAL_NAMES}
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, selected)
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


def checked_root(value: Any) -> str:
    require(type(value) is str and value == PUBLIC_RECOVERY_ROOT
            and value.startswith("/tmp/")
            and len(value.split("/")) == 3,
            "require the exact versioned caller-pinned V4 private recovery root")
    return value


def open_recovery_lock(v2: types.ModuleType, root: str,
                       *, create: bool) -> tuple[int, int]:
    checked_root(root)
    if create:
        os.mkdir(root, mode=0o700)
        temporary = os.open(
            "/tmp", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
        try:
            os.fsync(temporary)
        finally:
            os.close(temporary)
    directory = v2.private_directory(root)
    descriptor: int | None = None
    try:
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if create:
            flags |= os.O_CREAT | os.O_EXCL
        descriptor = os.open(LOCK_NAME, flags, 0o600, dir_fd=directory)
        actual = os.fstat(descriptor)
        visible = os.stat(LOCK_NAME, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(actual.st_mode)
                and actual.st_uid == os.geteuid()
                and actual.st_nlink == 1
                and stat.S_IMODE(actual.st_mode) == 0o600
                and (actual.st_dev, actual.st_ino)
                == (visible.st_dev, visible.st_ino),
                "reject a substituted, shared, or foreign V4 recovery lock")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.fsync(descriptor)
        os.fsync(directory)
        return directory, descriptor
    except BaseException:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)
        raise


def announce_recovery(root: str, journal_digest: str) -> None:
    record = {
        "schema": SCHEMA + "-preactivation-public-recovery-announcement",
        "status": "PASS", "family": FAMILY,
        "activation_root": checked_root(root),
        "journal_relative": "recovery-journal.json",
        "recovery_journal_sha256": checked_digest(
            journal_digest, "actual V4 pre-mutation recovery journal"),
        "canonical_target_replacements_so_far": 0,
        "group_atomic": False, "holdout": "NOT OPENED",
    }
    sys.stderr.buffer.write(canonical(record))
    sys.stderr.buffer.flush()


def restore_corrected_four_roles(
        v2: types.ModuleType, root: str, journal: dict[str, Any],
        journal_sha256: str) -> dict[str, Any]:
    checked_root(root)
    checked_digest(journal_sha256, "actual V4 four-owner recovery journal")
    require(type(journal) is dict
            and journal.get("schema") == v2.JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("activation_root") == root
            and journal.get("source_sha256") == V2["source"][1]
            and journal.get("protocol_sha256") == V2["protocol"][1]
            and journal.get("contract_sha256") == V2["contract"][1]
            and journal.get("build_archive_sha256") == BUILD["archive"][1]
            and journal.get("build_receipt_sha256") == BUILD["receipt"][1]
            and journal.get("corrected_public_adapter_sha256")
            == CORRECTED_PUBLIC_SHA256
            and journal.get("recoverable_v4_public_root")
            == PUBLIC_RECOVERY_ROOT
            and journal.get("recoverable_v4_public_lock_filename")
            == LOCK_NAME
            and journal.get("role_order") == list(ROLE_ORDER)
            and journal.get("restoration_order") == list(RESTORATION_ORDER)
            and journal.get("group_atomic") is False
            and type(journal.get("roles")) is dict
            and set(journal["roles"]) == set(ROLE_ORDER),
            "recover only the independently corrected exact V12 V4 journal")
    recorded, journal_owner = v2.read_private(
        root, "recovery-journal.json", journal_sha256)
    require(canonical(recorded) == canonical(journal)
            and journal_owner["sha256"] == journal_sha256,
            "reauthenticate every actual corrected V4 journal byte")
    restored: dict[str, dict[str, Any]] = {}
    for role in RESTORATION_ORDER:
        definition = v2.ROLES[role]
        entry = journal["roles"][role]
        expected = definition["original"]
        require(type(entry) is dict
                and entry.get("role") == role
                and entry.get("relative") == definition["relative"]
                and entry.get("original") == ORIGINALS[role]
                and expected == ORIGINALS[role]
                and entry.get("repaired_sha256") == definition["sha256"]
                and entry.get("repaired_bytes") == definition["bytes"],
                "refuse a stale V11 or substituted V12 recovery role: " + role)
        repository, directory, filename = v2.open_target_parent(
            definition["relative"])
        try:
            before = os.fstat(directory)
            try:
                current = os.stat(filename, dir_fd=directory,
                                  follow_symlinks=False)
            except FileNotFoundError as error:
                raise CampaignError(
                    "refuse a removed genuine original Rust target: " + role
                ) from error
            require(stat.S_ISREG(current.st_mode)
                    and current.st_uid == os.geteuid(),
                    "refuse a foreign or symlinked actual V4 recovery target")
            identity = (current.st_dev, current.st_ino)
            original_identity = (expected["device"], expected["inode"])
            if identity == original_identity and current.st_nlink == 1:
                try:
                    os.stat(entry["backup_filename"], dir_fd=directory,
                            follow_symlinks=False)
                except FileNotFoundError:
                    restored[role] = v2.current_original(role)
                    continue
                raise CampaignError(
                    "refuse an unexplained actual V4 original backup")
            if identity == original_identity and current.st_nlink == 2:
                intent, _ = v2.read_private(
                    root, "link-intent-" + role + ".json")
                require(intent.get("schema") == v2.INTENTION_SCHEMA
                        and intent.get("operation") == "HARDLINK_BACKUP"
                        and intent.get("family") == FAMILY
                        and intent.get("journal_sha256") == journal_sha256
                        and intent.get("role") == role
                        and intent.get("backup_filename")
                        == entry["backup_filename"],
                        "refuse an unauthenticated V4 original hardlink")
                backup = os.stat(entry["backup_filename"],
                                 dir_fd=directory, follow_symlinks=False)
                require((backup.st_dev, backup.st_ino) == original_identity
                        and backup.st_nlink == 2
                        and backup.st_uid == expected["uid"],
                        "refuse a substituted V4 original hardlink")
                os.unlink(entry["backup_filename"], dir_fd=directory)
                v2.sync_directory(directory, before)
                restored[role] = v2.current_original(role)
                continue
            intent, _ = v2.read_private(
                root, "promotion-intent-" + role + ".json")
            require(intent.get("schema") == v2.INTENTION_SCHEMA
                    and intent.get("operation") == "PROMOTE"
                    and intent.get("family") == FAMILY
                    and intent.get("journal_sha256") == journal_sha256
                    and intent.get("role") == role
                    and intent.get("repaired_sha256")
                    == definition["sha256"]
                    and intent.get("repaired_bytes") == definition["bytes"]
                    and current.st_size == definition["bytes"]
                    and stat.S_IMODE(current.st_mode) == expected["mode"]
                    and current.st_nlink == 1,
                    "never overwrite changed or stale actual V12 Rust bytes")
            _, promoted = v2._read_owned(
                str(ROOT), definition["relative"], definition["sha256"],
                exact_size=definition["bytes"], maximum=v2.MAX_BINARY_BYTES,
                allow_canonical_target=True)
            require((promoted["device"], promoted["inode"]) == identity,
                    "never replace a substituted user-owned Rust inode")
            backup = os.stat(entry["backup_filename"], dir_fd=directory,
                             follow_symlinks=False)
            require(stat.S_ISREG(backup.st_mode)
                    and (backup.st_dev, backup.st_ino) == original_identity
                    and backup.st_nlink == 1
                    and backup.st_uid == expected["uid"]
                    and backup.st_size == expected["bytes"]
                    and stat.S_IMODE(backup.st_mode) == expected["mode"],
                    "restore only the exact retained genuine original inode")
            intention = {
                "schema": v2.INTENTION_SCHEMA, "status": "PREPARED",
                "operation": "RESTORE", "family": FAMILY, "role": role,
                "journal_sha256": journal_sha256,
                "target": definition["relative"],
                "backup_filename": entry["backup_filename"],
                "group_atomic": False,
            }
            try:
                v2.write_private(root, "restore-intent-" + role + ".json",
                                 intention)
            except FileExistsError:
                previous, _ = v2.read_private(
                    root, "restore-intent-" + role + ".json")
                require(canonical(previous) == canonical(intention),
                        "retry only the exact durable V4 restoration intent")
            os.replace(entry["backup_filename"], filename,
                       src_dir_fd=directory, dst_dir_fd=directory)
            v2.sync_directory(directory, before)
            restored[role] = v2.current_original(role)
        finally:
            os.close(directory)
            os.close(repository)
    require(set(restored) == set(ROLE_ORDER)
            and all(v2.same_original(restored[role], ORIGINALS[role])
                    for role in ROLE_ORDER),
            "prove independent V4 recovery of every exact original inode")
    record = {
        "schema": RESTORATION_SCHEMA, "status": "PASS", "version": 4,
        "family": FAMILY, "label": LABEL, "activation_root": root,
        "journal_sha256": journal_sha256,
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "restored_targets": restored,
        "restoration_order": list(RESTORATION_ORDER),
        "original_inodes_preserved": True,
        "unchanged_v2_restoration_invoked": False,
        "group_atomic": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }
    try:
        owner = v2.write_private(root, "restoration-receipt.json", record)
    except FileExistsError:
        previous, owner = v2.read_private(root, "restoration-receipt.json")
        require(canonical(previous) == canonical(record),
                "refuse a substituted corrected V4 restoration record")
    return {"report": record, "owner": owner}


def activate_four_roles(v2: types.ModuleType,
                        retained: Mapping[str, Any],
                        options: argparse.Namespace) -> dict[str, Any]:
    root = checked_root(options.activation_root)
    originals = v2.exact_originals()
    require(all(v2.same_original(originals[role], ORIGINALS[role])
                for role in ROLE_ORDER),
            "authenticate all four genuine original inodes before activation")
    phase = retained["build"]["phases"][0]["phase"]
    payloads = {role: v2.read_recorded_phase(phase, role)
                for role in ROLE_ORDER}
    token = os.urandom(16).hex()
    entries: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        backup, stage = v2.role_target_names(token, role)
        expected = v2.ROLES[role]
        entries[role] = {
            "role": role, "relative": expected["relative"],
            "original": dict(expected["original"]),
            "backup_filename": backup, "stage_filename": stage,
            "repaired_sha256": expected["sha256"],
            "repaired_bytes": expected["bytes"],
        }
    journal = {
        "schema": v2.JOURNAL_SCHEMA, "status": "PREPARED", "version": 2,
        "family": FAMILY, "label": LABEL, "activation_root": root,
        "source_sha256": V2["source"][1],
        "protocol_sha256": V2["protocol"][1],
        "contract_sha256": V2["contract"][1],
        "build_archive_sha256": BUILD["archive"][1],
        "build_receipt_sha256": BUILD["receipt"][1],
        "roles": entries, "role_order": list(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "group_atomic": False,
        "exact_original_inode_backup": "ADJACENT SAME-DIRECTORY HARDLINK",
        "recoverable_v4_controller_source_sha256": options.source_sha256,
        "recoverable_v4_controller_protocol_sha256": options.protocol_sha256,
        "recoverable_v4_controller_contract_sha256": options.contract_sha256,
        "recoverable_v4_public_root": PUBLIC_RECOVERY_ROOT,
        "recoverable_v4_public_lock_filename": LOCK_NAME,
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
    }
    with blocked_controller_signals():
        journal_owner = v2.write_private(root, "recovery-journal.json", journal)
        announce_recovery(root, journal_owner["sha256"])
    try:
        for role in ROLE_ORDER:
            with blocked_controller_signals():
                entry = entries[role]
                owned = v2.ROLES[role]
                original = v2.current_original(role)
                require(v2.same_original(original, owned["original"]),
                        "refuse an original changed after journal publication")
                repository, directory, filename = v2.open_target_parent(
                    entry["relative"])
                try:
                    before = os.fstat(directory)
                    v2.ensure_absent(directory, entry["backup_filename"])
                    v2.ensure_absent(directory, entry["stage_filename"])
                    intention = {
                        "schema": v2.INTENTION_SCHEMA, "status": "PREPARED",
                        "operation": "HARDLINK_BACKUP", "family": FAMILY,
                        "role": role, "target": entry["relative"],
                        "activation_root": root,
                        "journal_sha256": journal_owner["sha256"],
                        "original": entry["original"],
                        "backup_filename": entry["backup_filename"],
                        "group_atomic": False,
                    }
                    v2.write_private(root, "link-intent-" + role + ".json",
                                     intention)
                    os.link(filename, entry["backup_filename"],
                            src_dir_fd=directory, dst_dir_fd=directory,
                            follow_symlinks=False)
                    current = os.stat(filename, dir_fd=directory,
                                      follow_symlinks=False)
                    backup = os.stat(entry["backup_filename"],
                                     dir_fd=directory,
                                     follow_symlinks=False)
                    expected = owned["original"]
                    require((current.st_dev, current.st_ino)
                            == (backup.st_dev, backup.st_ino)
                            == (expected["device"], expected["inode"])
                            and current.st_nlink == 2
                            and backup.st_nlink == 2
                            and current.st_uid == expected["uid"]
                            and stat.S_IMODE(current.st_mode)
                            == expected["mode"],
                            "preserve the real identical hardlinked original inode")
                    v2.sync_directory(directory, before)
                    promotion = {
                        "schema": v2.INTENTION_SCHEMA, "status": "PREPARED",
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
                    v2.write_private(root,
                                     "promotion-intent-" + role + ".json",
                                     promotion)
                    staged = v2.write_stage(
                        directory, entry["stage_filename"],
                        payloads[role], expected["mode"])
                    require(staged.get("sha256") == owned["sha256"]
                            and staged.get("size_bytes") == owned["bytes"],
                            "never promote unverified V12 private source or native bytes")
                    v2.sync_directory(directory, before)
                    os.replace(entry["stage_filename"], filename,
                               src_dir_fd=directory, dst_dir_fd=directory)
                    v2.sync_directory(directory, before)
                    _, promoted = v2._read_owned(
                        str(ROOT), entry["relative"], owned["sha256"],
                        exact_size=owned["bytes"],
                        maximum=v2.MAX_BINARY_BYTES,
                        allow_canonical_target=True)
                    require(promoted["device"] == staged["device"]
                            and promoted["inode"] == staged["inode"]
                            and promoted["mode"] == expected["mode"]
                            and promoted["nlink"] == 1,
                            "authenticate every one individually promoted source inode")
                finally:
                    os.close(directory)
                    os.close(repository)
        targets: dict[str, Any] = {}
        with blocked_controller_signals():
            for role in ROLE_ORDER:
                owned = v2.ROLES[role]
                _, targets[role] = v2._read_owned(
                    str(ROOT), owned["relative"], owned["sha256"],
                    exact_size=owned["bytes"], maximum=v2.MAX_BINARY_BYTES,
                    allow_canonical_target=True)
            report = {
                "schema": v2.ACTIVATION_SCHEMA, "status": "PASS",
                "version": 2, "family": FAMILY, "label": LABEL,
                "activation_root": root, "journal": journal_owner,
                "targets": targets, "role_order": list(ROLE_ORDER),
                "restoration_order": list(RESTORATION_ORDER),
                "build_archive_sha256": BUILD["archive"][1],
                "build_receipt_sha256": BUILD["receipt"][1],
                "all_four_original_inodes_retained": True,
                "recoverable_v4_controller_source_sha256": options.source_sha256,
                "group_atomic": False,
            }
            report_owner = v2.write_private(root, "activation-report.json", report)
            receipt = {
                "schema": v2.ACTIVATION_RECEIPT_SCHEMA,
                "status": "PASS", "activation_status": "PASS",
                "family": FAMILY, "activation_root": root,
                "activation": report_owner, "journal": journal_owner,
                "group_atomic": False,
            }
            receipt_owner = v2.write_private(
                root, "activation-receipt.json", receipt)
        return {
            "root": root, "journal": journal,
            "journal_owner": journal_owner,
            "activation": report, "activation_owner": report_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "originals": originals,
        }
    except BaseException:
        with blocked_controller_signals():
            restore_corrected_four_roles(
                v2, root, journal, journal_owner["sha256"])
        raise


def stream_observation(value: Any) -> dict[str, Any]:
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True,
                               separators=(",", ":"), allow_nan=False)
    plain_hash = hashlib.sha256()
    plain_size = 0
    destination = io.BytesIO()
    with gzip.GzipFile(fileobj=destination, mode="wb", compresslevel=9,
                       mtime=0) as stream:
        for piece in encoder.iterencode(value):
            raw = piece.encode("ascii")
            plain_size += len(raw)
            require(plain_size <= MAX_SUITE_PLAIN_BYTES,
                    "bound the complete actual original suite observation")
            plain_hash.update(raw)
            stream.write(raw)
            require(destination.tell() <= MAX_SUITE_COMPRESSED_BYTES,
                    "bound complete compressed original suite output")
        plain_size += 1
        require(plain_size <= MAX_SUITE_PLAIN_BYTES,
                "bound the exact original observation newline")
        plain_hash.update(b"\n")
        stream.write(b"\n")
    compressed = destination.getvalue()
    require(0 < len(compressed) <= MAX_SUITE_COMPRESSED_BYTES,
            "retain one complete bounded original observation gzip")
    return {
        "encoding": "deterministic-single-member-gzip-base64",
        "gzip_mtime": 0,
        "compressed_sha256": digest(compressed),
        "compressed_bytes": len(compressed),
        "compressed_base64": base64.b64encode(compressed).decode("ascii"),
        "uncompressed_sha256": plain_hash.hexdigest(),
        "uncompressed_bytes": plain_size,
    }


def validate_streamed_observation(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("encoding")
            == "deterministic-single-member-gzip-base64"
            and value.get("gzip_mtime") == 0
            and type(value.get("compressed_bytes")) is int
            and 0 < value["compressed_bytes"] <= MAX_SUITE_COMPRESSED_BYTES
            and type(value.get("uncompressed_bytes")) is int
            and 0 < value["uncompressed_bytes"] <= MAX_SUITE_PLAIN_BYTES
            and type(value.get("compressed_base64")) is str,
            "preserve a complete bounded original worker gzip")
    checked_digest(value.get("compressed_sha256"), "complete original worker gzip")
    checked_digest(value.get("uncompressed_sha256"), "complete original records")
    try:
        compressed = base64.b64decode(value["compressed_base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise CampaignError("reject concealed actual original worker gzip") from error
    require(len(compressed) == value["compressed_bytes"]
            and digest(compressed) == value["compressed_sha256"]
            and compressed[:3] == b"\x1f\x8b\x08"
            and compressed[4:8] == b"\x00\x00\x00\x00",
            "authenticate all genuinely compressed original records")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    actual_hash = hashlib.sha256()
    total = 0
    cursor = 0
    try:
        while cursor < len(compressed):
            part = compressed[cursor:cursor + 64 * 1024]
            cursor += len(part)
            pending = part
            while pending:
                block = decoder.decompress(pending, 1024 * 1024)
                total += len(block)
                require(total <= MAX_SUITE_PLAIN_BYTES,
                        "reject an oversized complete original observation")
                actual_hash.update(block)
                pending = decoder.unconsumed_tail
                if decoder.unused_data:
                    raise CampaignError("reject multiple original observation members")
        remainder = decoder.flush()
        total += len(remainder)
        require(total <= MAX_SUITE_PLAIN_BYTES and decoder.eof,
                "reject truncated actual candidate records")
        actual_hash.update(remainder)
    except (zlib.error, EOFError, OSError) as error:
        raise CampaignError("reject corrupt complete original case records") from error
    require(total == value["uncompressed_bytes"]
            and actual_hash.hexdigest() == value["uncompressed_sha256"],
            "reauthenticate every original mismatch without materializing the archive")
    return value


def same_owner(expected: Any, actual: Mapping[str, Any]) -> bool:
    return (type(expected) is dict
            and expected.get("sha256") == actual.get("sha256")
            and expected.get("device") == actual.get("device")
            and expected.get("inode") == actual.get("inode")
            and expected.get("size_bytes") == actual.get("size_bytes"))


def active_worker_approval(v2: types.ModuleType,
                           options: argparse.Namespace) -> dict[str, Any]:
    root = checked_root(options.activation_root)
    report, report_owner = v2.read_private(
        root, "activation-report.json", options.activation_report_sha256)
    receipt, receipt_owner = v2.read_private(
        root, "activation-receipt.json", options.activation_receipt_sha256)
    journal, journal_owner = v2.read_private(
        root, "recovery-journal.json", options.recovery_journal_sha256)
    require(report.get("schema") == v2.ACTIVATION_SCHEMA
            and report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("activation_root") == root
            and report.get("build_archive_sha256") == BUILD["archive"][1]
            and report.get("build_receipt_sha256") == BUILD["receipt"][1]
            and report.get("group_atomic") is False
            and same_owner(report.get("journal"), journal_owner)
            and receipt.get("schema") == v2.ACTIVATION_RECEIPT_SCHEMA
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and receipt.get("family") == FAMILY
            and same_owner(receipt.get("activation"), report_owner)
            and same_owner(receipt.get("journal"), journal_owner)
            and journal.get("schema") == v2.JOURNAL_SCHEMA
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("build_archive_sha256") == BUILD["archive"][1]
            and journal.get("build_receipt_sha256") == BUILD["receipt"][1]
            and journal.get("corrected_public_adapter_sha256")
            == CORRECTED_PUBLIC_SHA256
            and journal.get("role_order") == list(ROLE_ORDER)
            and journal.get("restoration_order") == list(RESTORATION_ORDER)
            and journal.get("group_atomic") is False,
            "authenticate only the live corrected four-owner Rust V12 journal")
    for role in ROLE_ORDER:
        expected = v2.ROLES[role]
        row = journal.get("roles", {}).get(role)
        current = report.get("targets", {}).get(role)
        require(type(row) is dict and row.get("original") == expected["original"]
                and row.get("repaired_sha256") == expected["sha256"]
                and row.get("repaired_bytes") == expected["bytes"]
                and type(current) is dict
                and current.get("relative") == expected["relative"]
                and current.get("sha256") == expected["sha256"]
                and current.get("size_bytes") == expected["bytes"],
                "reject a changed actual corrected activation role: " + role)
    return {"root": root, "report": report, "report_owner": report_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "journal": journal, "journal_owner": journal_owner}


def run_worker(options: argparse.Namespace) -> dict[str, Any]:
    context, _ = verify_context(options.source_sha256,
                                options.protocol_sha256,
                                options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "authenticate the complete frozen V4 context before one worker")
    v2 = patched_v2_helpers()
    active = active_worker_approval(v2, options)
    producer = load_frozen_module(
        PRODUCER["source"], "_rebar_exact_original_six_family_v3_for_v12_rust")
    require(producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v3"
            and producer.SUITE_COUNT == SUITE_COUNT
            and producer.CASE_DENOMINATOR == CASE_COUNT
            and producer.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
            and [(item.name, item.case_count) for item in producer.SUITES]
            == list(SUITES),
            "run only the complete unchanged original CPython P0 producer")
    spec = corrected_rust_family(producer)
    suite = producer.suite_spec(options.suite)
    source_pins = {path: fingerprint
                   for path, fingerprint, _ in CORRECTED_SOURCE_OWNERS}
    pins = {"source": CORRECTED_PUBLIC_SHA256,
            "native_engine": ENGINE_SHA256,
            "native_bridge": BRIDGE_SHA256}
    actual = producer.exact_native_owners(spec, pins, source_pins)
    require(actual["source"]["sha256"] == CORRECTED_PUBLIC_SHA256
            and actual["native_engine"]["sha256"] == ENGINE_SHA256
            and actual["native_bridge"]["sha256"] == BRIDGE_SHA256,
            "match only through the corrected actual first-party Rust owner")
    if suite.name == "original_bounded_v5":
        observation = producer.observe_original_upstream(
            suite, spec, pins, source_pins)
    elif suite.name == "subinterpreter_v2":
        observation = producer.observe_subinterpreters(
            suite, spec, pins, source_pins,
            producer_sha256=PRODUCER["source"][1])
    else:
        manifest_item = (
            "oracle/phase1/p0-completeness-v1.json",
            "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
            45632,
        )
        raw, _ = read_owned(manifest_item, maximum=MAX_SOURCE_BYTES)
        phase_one = strict_document(raw, "unchanged original complete phase-one oracle")
        observation = producer.observe_direct_suite(
            suite, spec, pins, source_pins, phase_one)
    require(type(observation) is dict
            and observation.get("schema")
            == producer.SCHEMA + "-actual-original-suite"
            and observation.get("status") in ("PASS", "FAIL")
            and observation.get("suite") == suite.name
            and observation.get("candidate_family") == FAMILY
            and observation.get("case_execution_denominator") == suite.case_count
            and observation.get("actual_candidate_case_count") == suite.case_count
            and type(observation.get("mismatch_count")) is int
            and observation["mismatch_count"] >= 0
            and type(observation.get("all_mismatches")) is list
            and len(observation["all_mismatches"])
            == observation["mismatch_count"]
            and observation.get("actual_candidate_workers") == 1
            and observation.get("clock_samples") == 0
            and observation.get("holdout") == "NOT OPENED",
            "retain every literal original upstream record and true mismatch")
    if suite.name == "original_bounded_v5":
        require(observation.get("actual_public_record_count") == 152
                and observation.get("actual_debug_skip_count") == 1
                and observation.get("named_private_waiver_count") == 13,
                "never suppress an upstream case or unnamed private failure")
    if suite.name == "subinterpreter_v2" and observation["status"] == "PASS":
        require(observation.get("actual_case_interpreter_exec_calls") == 394
                and observation.get("actual_interpreters_created") == 11
                and observation.get("actual_interpreters_destroyed") == 11
                and observation.get("all_real_pipes_read_to_eof") is True
                and observation.get("all_real_pipe_descriptors_closed") is True
                and observation.get("interpreter_live_set_restored") is True,
                "preserve all actual original 128/394/11 interpreter events")
    encoded = stream_observation(observation)
    return {
        "schema": WORKER_SCHEMA, "status": observation["status"],
        "candidate_family": FAMILY, "label": LABEL,
        "suite": suite.name,
        "case_execution_denominator": suite.case_count,
        "actual_candidate_case_count": suite.case_count,
        "mismatch_count": observation["mismatch_count"],
        "failure_class": ("PASS" if observation["status"] == "PASS"
                          else "SEMANTIC MISMATCH"),
        "original_observer_source_sha256": PRODUCER["source"][1],
        "original_observer_unchanged": True,
        "v9_c_only_runner_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "activation_report_sha256": active["report_owner"]["sha256"],
        "activation_receipt_sha256": active["receipt_owner"]["sha256"],
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "repaired_source_owner_count": 9,
        "corrected_public_source_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "complete_original_observation": encoded,
        "all_original_records_and_mismatches_preserved": True,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_qualified": False, "winner_selected": False,
    }


def worker_arguments(options: argparse.Namespace, name: str,
                     active: Mapping[str, Any]) -> list[str]:
    return [
        PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE), "--worker",
        "--source-sha256", options.source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--contract-sha256", options.contract_sha256,
        "--family", FAMILY, "--label", LABEL,
        "--suite", name,
        "--activation-root", active["root"],
        "--activation-report-sha256", active["activation_owner"]["sha256"],
        "--activation-receipt-sha256", active["receipt_owner"]["sha256"],
        "--recovery-journal-sha256", active["journal_owner"]["sha256"],
        "--producer-source-sha256", PRODUCER["source"][1],
        "--producer-protocol-sha256", PRODUCER["protocol"][1],
        "--producer-contract-sha256", PRODUCER["contract"][1],
        "--build-source-sha256", BUILD["source"][1],
        "--build-protocol-sha256", BUILD["protocol"][1],
        "--build-contract-sha256", BUILD["contract"][1],
        "--build-archive-sha256", BUILD["archive"][1],
        "--build-receipt-sha256", BUILD["receipt"][1],
        "--native-engine-sha256", ENGINE_SHA256,
        "--native-bridge-sha256", BRIDGE_SHA256,
        "--native-engine-bytes", str(ENGINE_BYTES),
        "--native-bridge-bytes", str(BRIDGE_BYTES),
    ]


def encode_stream(raw: bytes, limit: int, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= limit,
            "preserve one complete bounded " + label)
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "sha256": digest(raw), "size_bytes": len(raw)}


def execute_one_worker(options: argparse.Namespace, name: str,
                       count: int, active: Mapping[str, Any]) -> dict[str, Any]:
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
            and len(stdout) <= MAX_WORKER_STDOUT_BYTES
            and len(stderr) <= MAX_WORKER_STDERR_BYTES,
            "retain all actual corrected V12 Rust worker stdout and stderr")
    process = {
        "argv": argv, "pid": child.pid,
        "returncode": child.returncode, "timed_out": timed_out,
        "stdout": encode_stream(stdout, MAX_WORKER_STDOUT_BYTES,
                                "original suite stdout"),
        "stderr": encode_stream(stderr, MAX_WORKER_STDERR_BYTES,
                                "original suite stderr"),
        "actual_worker_processes": 1,
    }
    observed: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    try:
        observed = strict_document(stdout, "actual corrected Rust V4 worker")
        require(observed.get("schema") == WORKER_SCHEMA
                and observed.get("candidate_family") == FAMILY
                and observed.get("label") == LABEL
                and observed.get("suite") == name
                and observed.get("case_execution_denominator") == count
                and observed.get("actual_candidate_case_count") == count
                and observed.get("original_observer_source_sha256")
                == PRODUCER["source"][1]
                and observed.get("actual_v12_build_archive_sha256")
                == BUILD["archive"][1]
                and observed.get("actual_v12_build_receipt_sha256")
                == BUILD["receipt"][1]
                and observed.get("corrected_public_source_sha256")
                == CORRECTED_PUBLIC_SHA256
                and observed.get("corrected_bridge_source_sha256")
                == BRIDGE_SOURCE_SHA256
                and observed.get("native_engine_sha256") == ENGINE_SHA256
                and observed.get("native_bridge_sha256") == BRIDGE_SHA256
                and observed.get("repaired_source_owner_count") == 9
                and observed.get("all_original_records_and_mismatches_preserved")
                is True
                and observed.get("actual_candidate_workers") == 1
                and observed.get("status") in ("PASS", "FAIL")
                and type(observed.get("mismatch_count")) is int
                and observed["mismatch_count"] >= 0
                and not timed_out
                and child.returncode
                == (0 if observed["status"] == "PASS" else 1)
                and observed.get("clock_samples") == 0
                and observed.get("holdout") == "NOT OPENED",
                "reject a missing, stale, forged, timed-out, or C-family worker")
        validate_streamed_observation(observed.get("complete_original_observation"))
    except (CampaignError, ValueError, TypeError, zlib.error) as error:
        failure = {"error_type": type(error).__qualname__,
                   "error_message": str(error)[:4096]}
    if failure is None and observed is not None:
        return {
            "suite": name, "status": observed["status"],
            "case_execution_denominator": count,
            "failure_class": observed["failure_class"],
            "mismatch_count": observed["mismatch_count"],
            "actual_worker_started": True,
            "actual_worker_processes": 1,
            "all_original_records_and_mismatches_preserved": True,
            "original_observer": observed,
            "process": process,
        }
    return {
        "suite": name, "status": "FAIL",
        "case_execution_denominator": count,
        "failure_class": "INFRASTRUCTURE FAILURE",
        "mismatch_count": "NOT MEASURED",
        "actual_worker_started": True,
        "actual_worker_processes": 1,
        "all_original_records_and_mismatches_preserved": False,
        "worker_decoding_failure": failure,
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
        "actual_worker_started": False,
        "actual_worker_processes": 0,
        "all_original_records_and_mismatches_preserved": False,
        "error_type": type(error).__qualname__,
        "error_message": str(error)[:4096],
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__),
        "process": None,
    }


def evidence_names(failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "choose one exact exclusive campaign outcome")
    stem = "repaired-rust-original-campaign-v4-rust-" + LABEL
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_fresh_evidence(publication: types.ModuleType) -> None:
    directory = publication.open_evidence_directory()
    try:
        for failure in (False, True):
            for name in evidence_names(failure):
                try:
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise CampaignError("never overwrite a previous original Rust result: "
                                    + name)
    finally:
        os.close(directory)


def bounded_public_report(report: Mapping[str, Any]) -> int:
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True,
                               separators=(",", ":"), allow_nan=False)
    count = 1
    for piece in encoder.iterencode(report):
        count += len(piece.encode("ascii"))
        require(count <= MAX_PUBLIC_REPORT_BYTES,
                "bound complete streamed original V4 campaign report to 32 MiB")
    return count


def preserve_campaign(report: dict[str, Any], retained: Mapping[str, Any],
                      v2: types.ModuleType) -> dict[str, Any]:
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
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in report["suite_results"]] == list(SUITES)
            and report.get("all_four_original_targets_restored") is True
            and report.get("restoration_verified_before_publication") is True
            and report.get("historical_evidence_owner_count_before_publication")
            == ACTUAL_EVIDENCE_OWNER_COUNT
            and report.get("historical_authenticated_reference_count_before_publication")
            == ACTUAL_AUTHENTICATED_REFERENCE_COUNT
            and report.get("holdout") == "NOT OPENED",
            "never publish invented original cases or unrestored Rust target inodes")
    size = bounded_public_report(report)
    current = v2.exact_originals()
    require(report.get("restored_original_targets") == current,
            "prove all exact original target inodes immediately before publication")
    publication = retained["publication"]
    archive_name, receipt_name = evidence_names(report["status"] == "FAIL")
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
            and archive.get("streaming_readback_verified") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and stream.get("gzip_mtime") == 0
            and stream.get("gzip_single_member") is True
            and stream.get("uncompressed_bytes") == size,
            "create one complete owner-only deterministic streamed V4 result")
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": report["status"],
        "family": FAMILY, "label": LABEL, "archive": archive,
        "campaign_source_sha256": report["campaign_source_sha256"],
        "campaign_protocol_sha256": report["campaign_protocol_sha256"],
        "campaign_contract_sha256": report["campaign_contract_sha256"],
        "original_v3_producer_source_sha256": PRODUCER["source"][1],
        "original_v3_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v3_producer_contract_sha256": PRODUCER["contract"][1],
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
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
        "historical_evidence_owner_count_before_publication":
        ACTUAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count_before_publication":
        ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count":
        ACTUAL_EVIDENCE_OWNER_COUNT + 2,
        "resulting_authenticated_reference_count":
        ACTUAL_AUTHENTICATED_REFERENCE_COUNT + 2,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "restoration_verified_before_publication": True,
        "v9_c_only_runner_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt_owner = v2.write_evidence_receipt(receipt_name, receipt)
    require((archive["device"], archive["inode"])
            != (receipt_owner["device"], receipt_owner["inode"])
            and v2.exact_originals() == current,
            "publish two distinct durable owners only after exact restoration")
    return {
        "schema": SCHEMA + "-published-complete-original-campaign",
        "status": report["status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": FAMILY, "label": LABEL,
        "archive": archive, "receipt": receipt_owner,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "historical_evidence_owner_count_before_publication":
        ACTUAL_EVIDENCE_OWNER_COUNT,
        "resulting_repository_evidence_owner_count":
        ACTUAL_EVIDENCE_OWNER_COUNT + 2,
        "historical_authenticated_reference_count_before_publication":
        ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "resulting_authenticated_reference_count":
        ACTUAL_AUTHENTICATED_REFERENCE_COUNT + 2,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "group_atomic": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def record_failure(error: BaseException) -> dict[str, Any]:
    return {"error_type": type(error).__qualname__,
            "error_message": str(error)[:4096],
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__)}


def run_campaign(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    context, retained = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "authenticate V12, old failures, and V30 before target mutations")
    v2 = patched_v2_helpers()
    publication = load_frozen_module(
        PUBLICATION["source"], "_rebar_exact_v2_streaming_publication_for_rust_v4")
    require(publication.SCHEMA == "rebar-owned-six-family-original-p0-campaign-v2"
            and callable(publication.write_streamed_archive),
            "reuse only the exact original first-party streaming publisher")
    retained["publication"] = publication
    ensure_fresh_evidence(publication)
    baseline: dict[str, Any] | None = None
    active: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    controller_failure: dict[str, Any] | None = None
    graceful: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    directory: int | None = None
    lock: int | None = None
    with installed_signal_handlers():
        try:
            with blocked_controller_signals():
                directory, lock = open_recovery_lock(
                    v2, options.activation_root, create=True)
            baseline = v2.exact_originals()
            active = activate_four_roles(v2, retained, options)
            for name, count in SUITES:
                try:
                    row = execute_one_worker(options, name, count, active)
                except GracefulControllerSignal:
                    raise
                except Exception as error:
                    row = failed_worker(name, count, error)
                rows.append(row)
        except GracefulControllerSignal as error:
            controller_failure = record_failure(error)
            graceful = {
                "schema": SIGNAL_SCHEMA, "status": "FAIL",
                "signal_name": error.signal_name,
                "signal_number": error.signum,
                "candidate_matching_result": "NOT MEASURED",
                "group_atomic": False,
            }
            seen = {row.get("suite") for row in rows}
            for name, count in SUITES:
                if name not in seen:
                    rows.append(failed_worker(name, count, error))
        except Exception as error:
            controller_failure = record_failure(error)
            seen = {row.get("suite") for row in rows}
            for name, count in SUITES:
                if name not in seen:
                    rows.append(failed_worker(name, count, error))
        finally:
            try:
                if active is not None:
                    with blocked_controller_signals():
                        restoration = restore_corrected_four_roles(
                            v2, active["root"], active["journal"],
                            active["journal_owner"]["sha256"])
                if baseline is not None:
                    with blocked_controller_signals():
                        require(v2.exact_originals() == baseline,
                                "restore every exact original Rust owner inode")
            finally:
                if lock is not None:
                    os.close(lock)
                if directory is not None:
                    os.close(directory)
    suite_positions = {name: position
                       for position, (name, _) in enumerate(SUITES)}
    rows.sort(key=lambda row: suite_positions[row["suite"]])
    require(len(rows) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in rows] == list(SUITES),
            "preserve all original groups even when a genuine worker fails")
    require(baseline is not None and active is not None
            and restoration is not None,
            "never publish a campaign without actual exact original recovery")
    originals = v2.exact_originals()
    require(originals == baseline,
            "reauthenticate original inodes before any public evidence")
    pids = [row["process"]["pid"] for row in rows
            if row.get("actual_worker_started") is True
            and type(row.get("process")) is dict]
    require(len(pids) == len(set(pids)),
            "never count one actual original Rust process twice")
    complete = sum(row.get("actual_worker_started") is True for row in rows)
    passed = sum(count for (name, count), row in
                 zip(SUITES, rows, strict=True)
                 if row.get("suite") == name
                 and row.get("failure_class") == "PASS"
                 and row.get("mismatch_count") == 0
                 and row.get("all_original_records_and_mismatches_preserved")
                 is True)
    mismatches = sum(row["mismatch_count"] for row in rows
                     if row.get("failure_class") == "SEMANTIC MISMATCH"
                     and type(row.get("mismatch_count")) is int)
    infrastructure = sum(row.get("failure_class") == "INFRASTRUCTURE FAILURE"
                         for row in rows) + int(controller_failure is not None)
    qualified = (len(pids) == SUITE_COUNT and complete == SUITE_COUNT
                 and passed == CASE_COUNT and mismatches == 0
                 and infrastructure == 0 and graceful is None
                 and all(row.get("actual_worker_processes") == 1
                         and row.get("all_original_records_and_mismatches_preserved")
                         is True for row in rows))
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
        "actual_v12_build_source_sha256": BUILD["source"][1],
        "actual_v12_build_protocol_sha256": BUILD["protocol"][1],
        "actual_v12_build_contract_sha256": BUILD["contract"][1],
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "actual_v12_compiler_process_count": 28,
        "actual_corrected_rust_source_owner_count": 9,
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
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
        "semantic_mismatch_count": mismatches if complete else "NOT MEASURED",
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": qualified,
        "historical_evidence_owner_count_before_publication":
        ACTUAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count_before_publication":
        ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_previous_rust_semantic_mismatch_count": 1087,
        "preserved_previous_rust_verified_passing_case_count": 7438,
        "preserved_c_semantic_mismatch_count": 1230,
        "preserved_zig_semantic_mismatch_count": 2172,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "graceful_signal": graceful,
        "all_four_original_targets_restored": True,
        "restored_original_targets": originals,
        "restoration": restoration,
        "restoration_verified_before_publication": True,
        "v9_c_only_runner_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
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
    return preserve_campaign(report, retained, v2)


def recover_originals(options: argparse.Namespace) -> dict[str, Any]:
    require(options.recovery_journal_sha256 is not None,
            "independently pin the actual V4 journal before public recovery")
    context, _ = verify_context(options.source_sha256,
                                options.protocol_sha256,
                                options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "authenticate the complete immutable V4 context before recovery")
    v2 = patched_v2_helpers()
    root = checked_root(options.activation_root)
    directory: int | None = None
    lock: int | None = None
    restoration: dict[str, Any] | None = None
    try:
        with blocked_controller_signals():
            directory, lock = open_recovery_lock(v2, root, create=False)
            journal, owner = v2.read_private(
                root, "recovery-journal.json",
                options.recovery_journal_sha256)
            require(owner["sha256"] == options.recovery_journal_sha256
                    and journal.get("recoverable_v4_controller_source_sha256")
                    == options.source_sha256
                    and journal.get("recoverable_v4_controller_protocol_sha256")
                    == options.protocol_sha256
                    and journal.get("recoverable_v4_controller_contract_sha256")
                    == options.contract_sha256
                    and journal.get("corrected_public_adapter_sha256")
                    == CORRECTED_PUBLIC_SHA256
                    and journal.get("build_archive_sha256") == BUILD["archive"][1]
                    and journal.get("build_receipt_sha256") == BUILD["receipt"][1]
                    and journal.get("activation_root") == root
                    and journal.get("role_order") == list(ROLE_ORDER)
                    and journal.get("restoration_order")
                    == list(RESTORATION_ORDER)
                    and journal.get("group_atomic") is False,
                    "recover only the caller-pinned genuine exact V4 journal")
            restoration = restore_corrected_four_roles(
                v2, root, journal, options.recovery_journal_sha256)
            originals = v2.exact_originals()
            require(all(v2.same_original(originals[role], ORIGINALS[role])
                        for role in ROLE_ORDER)
                    and restoration.get("report", {}).get("status") == "PASS"
                    and restoration["report"].get("original_inodes_preserved")
                    is True,
                    "prove exact reverse recovery of all four original Rust inodes")
    finally:
        if lock is not None:
            os.close(lock)
        if directory is not None:
            os.close(directory)
    return {
        "schema": RECOVERY_SCHEMA, "status": "PASS", "version": 4,
        "family": FAMILY, "activation_root": root,
        "recovery_journal_sha256": options.recovery_journal_sha256,
        "restoration_order": list(RESTORATION_ORDER),
        "restoration": restoration,
        "restored_original_targets": originals,
        "all_four_original_targets_restored": True,
        "actual_candidate_workers": 0,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def assert_actual_authorization(options: argparse.Namespace) -> None:
    require(options.family == FAMILY and options.label == LABEL
            and options.activation_root == PUBLIC_RECOVERY_ROOT
            and options.producer_source_sha256 == PRODUCER["source"][1]
            and options.producer_protocol_sha256 == PRODUCER["protocol"][1]
            and options.producer_contract_sha256 == PRODUCER["contract"][1]
            and options.build_source_sha256 == BUILD["source"][1]
            and options.build_protocol_sha256 == BUILD["protocol"][1]
            and options.build_contract_sha256 == BUILD["contract"][1]
            and options.build_archive_sha256 == BUILD["archive"][1]
            and options.build_receipt_sha256 == BUILD["receipt"][1]
            and options.native_engine_sha256 == ENGINE_SHA256
            and options.native_bridge_sha256 == BRIDGE_SHA256
            and options.native_engine_bytes == ENGINE_BYTES
            and options.native_bridge_bytes == BRIDGE_BYTES,
            "independently caller-pin the exact actual V12 and original producer")


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
    checked_digest(options.source_sha256, "V4 controller source")
    checked_digest(options.protocol_sha256, "V4 controller protocol")
    if options.contract_sha256 is not None:
        checked_digest(options.contract_sha256, "V4 controller contract")
    actual_names = (
        "family", "label", "suite", "activation_root",
        "native_engine_bytes", "native_bridge_bytes",
        "producer_source_sha256", "producer_protocol_sha256",
        "producer_contract_sha256", "build_source_sha256",
        "build_protocol_sha256", "build_contract_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, name) is None for name in actual_names),
                "machine rendering may never select, activate, or run Rust")
        return options
    require(options.contract_sha256 is not None,
            "independently pin the immutable Rust V4 machine contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in actual_names),
                "source-only V4 may never run or recover a candidate")
        return options
    if options.recover:
        require(options.family == FAMILY
                and options.activation_root == PUBLIC_RECOVERY_ROOT
                and options.recovery_journal_sha256 is not None
                and options.label is None and options.suite is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None,
                "authorize only exact caller-pinned public recovery")
        checked_digest(options.recovery_journal_sha256,
                       "actual durable V4 recovery journal")
        return options
    assert_actual_authorization(options)
    if options.worker:
        require(options.suite is not None
                and options.activation_report_sha256 is not None
                and options.activation_receipt_sha256 is not None
                and options.recovery_journal_sha256 is not None,
                "bind each original worker to all three real live activation owners")
        for name in ("activation_report_sha256", "activation_receipt_sha256",
                     "recovery_journal_sha256"):
            checked_digest(getattr(options, name), name)
    else:
        require(options.suite is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None
                and options.recovery_journal_sha256 is None,
                "run all thirteen original suites only through fresh V4 activation")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    options: argparse.Namespace | None = None
    try:
        options = parse_arguments(arguments)
        verify_runtime()
        if options.self_test:
            result = source_self_test(options.source_sha256,
                                      options.protocol_sha256,
                                      options.contract_sha256)
        elif options.verify_frozen_context:
            result, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256,
                                       options.contract_sha256)
        elif options.render_contract:
            result = protocol_document(options.source_sha256,
                                       options.protocol_sha256)
        elif options.worker:
            result = run_worker(options)
        elif options.recover:
            result = recover_originals(options)
        else:
            result = run_campaign(options)
        raw = canonical(result)
        require(len(raw) <= MAX_WORKER_STDOUT_BYTES,
                "never truncate the complete caller-visible V4 result")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in ("PASS", "SOURCE FROZEN; CORRECTED RUST V12 CANDIDATE NOT RUN") else 1
    except BaseException as error:
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        result = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:4096],
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
            "family": FAMILY, "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "actual_evidence_owner_count_before_new_campaign":
            ACTUAL_EVIDENCE_OWNER_COUNT,
            "actual_authenticated_reference_count_before_new_campaign":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "group_atomic": False,
            **zero_effects(),
        }
        raw = canonical(result)
        sys.stdout.buffer.write(raw[:MAX_WORKER_STDOUT_BYTES])
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
