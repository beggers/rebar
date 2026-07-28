#!/usr/bin/env python3
"""Freeze and explicitly run the complete corrected first-party Zig P0 campaign.

Verification is read-only.  Native activation, journal creation, workers,
recovery, publication, clocks and benchmarks are never implicit.
"""

from __future__ import annotations

import argparse
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
from typing import Any, Iterator, Mapping, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_repaired_zig_original_campaign_v3.py"
PROTOCOL_RELATIVE = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V3.md"
CONTRACT_RELATIVE = "oracle/phase2/repaired-zig-original-campaign-v3.json"
SCHEMA = "rebar-owned-repaired-zig-original-campaign-v3"
CONTRACT_SCHEMA = SCHEMA + "-recoverable-source-freeze"
WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
RESULT_SCHEMA = SCHEMA + "-published-complete-original-campaign"
RECOVERY_SCHEMA = SCHEMA + "-public-exact-inode-recovery"
SIGNAL_SCHEMA = SCHEMA + "-graceful-controller-signal"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
FAMILY = "zig"
LABEL = "phase2-v12-zig-scanner-v2-original-p0"
BUILD_LABEL = "phase2-v12-zig-scanner-v2"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
PUBLIC_RECOVERY_ROOT = (
    "/tmp/rebar-phase2-repaired-zig-original-campaign-v3-"
    "phase2-v12-zig-scanner-v2-original-p0"
)
RECOVERY_PRIVATE_PREFIX = "rebar-phase2-repaired-zig-original-campaign-v3-"
LOCK_NAME = "recoverable-zig-v3.lock"
PHASE_NAMES = ("reference-a", "reference-b")
ROLE_ORDER = ("engine", "bridge")
RESTORATION_ORDER = ("bridge", "engine")
SIGNAL_NAMES = ("SIGINT", "SIGTERM", "SIGHUP")
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BUILD_ARCHIVE_BYTES = 1024 * 1024
MAX_BUILD_PLAIN_BYTES = 1024 * 1024
MAX_NATIVE_BYTES = 2 * 1024 * 1024
MAX_WORKER_STDOUT_BYTES = 32 * 1024 * 1024
MAX_WORKER_STDERR_BYTES = 4 * 1024 * 1024
MAX_SUITE_COMPRESSED_BYTES = 16 * 1024 * 1024
MAX_SUITE_PLAIN_BYTES = 512 * 1024 * 1024
MAX_PUBLIC_REPORT_BYTES = 64 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 8 * 3600
SUITE_COUNT = 13
CASE_COUNT = 31_237
PRIVATE_WAIVER_COUNT = 13
ACTUAL_EVIDENCE_OWNER_COUNT = 155
ACTUAL_AUTHENTICATED_REFERENCE_COUNT = 160
HISTORICAL_V31_OWNER_COUNT = 151
HISTORICAL_V31_REFERENCE_COUNT = 156
BUILD_PLAIN_SHA256 = "7a912e1221412e969e21400703bb95d15746a07b5776ee4530493cc3c8512b32"
BUILD_PLAIN_BYTES = 299_800
ENGINE_SHA256 = "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
ENGINE_BYTES = 108_888
BRIDGE_SHA256 = "e5809566a166f469e7f95fc1a43e814a3beeeffa2a6e848c00a3a48215ee6726"
BRIDGE_BYTES = 133_656
BRIDGE_SOURCE_SHA256 = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
BRIDGE_SOURCE_BYTES = 173_026
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "zig_version",
    "build_zig_engine", "build_zig_bridge",
    "engine_dynamic", "engine_symbols", "engine_sections", "engine_notes",
    "bridge_dynamic", "bridge_symbols", "bridge_sections", "bridge_notes",
)
SUITES: tuple[tuple[str, int], ...] = (
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
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
PHASE_ONE = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45_632,
)
ZIG_V2 = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v2.py",
        "a9f62061f709583c60a4d0b72ba1150931132a66b80b6eed1081e017fd389795",
        141_031,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V2.md",
        "fe17a8fc4e5fb5638ff92caa6e1b6d625e93dfb27ced02ba7b1490b830356db3",
        6_075,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v2.json",
        "0112748e8dbca769625ea2643643fad81ced069e20ed87a458bebe0a922d2851",
        15_015,
    ),
}
ACTIVATION_V7 = {
    "source": (
        "tools/activate_verified_native_candidate_v7.py",
        "98002a0a283ffec24670bcb9f35546c5720d2a7a1d098257729d244918022f8e",
        61_930,
    ),
    "protocol": (
        "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V7.md",
        "f333b50f9810cf246ae659c6d07eb4c63b8e2114d07b485b50d570ab272f22f8",
        5_141,
    ),
    "contract": (
        "oracle/phase2/verified-native-activation-v7.json",
        "62375f7d013b7b02a160b9492e5aa249b7af556041f2c86f20e7bfd5ad6885b1",
        9_718,
    ),
}
ACTIVATION_V6 = {
    "source": (
        "tools/activate_verified_native_candidate_v6.py",
        "d3a9b08c1bf7e3408719a0e92b8c1965aa6160dd2e18ab1501bb8662aaf8e4a1",
        107_982,
    ),
    "protocol": (
        "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V6.md",
        "0e736d575835fa22388841a527e22b62eef1ddf39eac9415bd7c518ba985b1d0",
        6_688,
    ),
    "contract": (
        "oracle/phase2/verified-native-activation-v6.json",
        "e0d486cc6d621e963f8af5db1c4f7a47d590ad679837db1f53e11d05b670332e",
        12_902,
    ),
}
PRODUCER = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v3.py",
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
        195_555,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
        5_522,
    ),
    "contract": (
        "oracle/phase2/six-family-p0-producer-v3.json",
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
        26_909,
    ),
}
PUBLICATION = {
    "source": (
        "tools/run_owned_six_family_original_p0_campaign_v2.py",
        "6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1",
        101_836,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md",
        "e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e",
        4_995,
    ),
    "contract": (
        "oracle/phase2/six-family-p0-campaign-v2.json",
        "e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7",
        21_314,
    ),
}
BUILD = {
    "source": (
        "tools/reproduce_owned_zig_scanner_source_build_v12.py",
        "5192fa35dd0b13cb3bdddfc8f24c37d7e797d0b8463d000c4692c8131f33d1b6",
        124_781,
    ),
    "protocol": (
        "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V12.md",
        "f80743d8109402e5876792b6713237b1ab770e3286874dd5ae47fb56381131b1",
        6_531,
    ),
    "contract": (
        "oracle/phase2/zig-scanner-source-build-v12.json",
        "5abb6f60c7a9672e32d6f2980a109ccb15b7ef56e5cc3a81abda458109552c1a",
        23_611,
    ),
    "archive": (
        "oracle/phase2/evidence/"
        "native-source-build-v12-zig-phase2-v12-zig-scanner-v2.json.gz",
        "3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d",
        48_371,
    ),
    "receipt": (
        "oracle/phase2/evidence/native-source-build-v12-zig-"
        "phase2-v12-zig-scanner-v2-publication-receipt.json",
        "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b",
        2_029,
    ),
}
RAW_ELF = {
    "source": (
        "tools/reproduce_owned_native_source_build_v7.py",
        "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
        300_624,
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md",
        "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
        8_063,
    ),
    "contract": (
        "oracle/phase2/native-source-build-v7.json",
        "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
        28_924,
    ),
}
V31 = {
    "source": (
        "tools/render_candidate_current_overview_v31.py",
        "daea5423d47bc84ec0ff503c14bae17ecdff392a60db14c5c66c575e978de588",
        75_072,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v31.inputs.json",
        "25f1ef2cdf7f3443f5924b9c9814c4f0864148ebdf243c92a1df12d1c5754900",
        80_376,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v31.json",
        "6d6f8fa23022b9198255cd0836961d4f78cd2d4c5d4041734a82a1d9f9d2ec90",
        314_023,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v31.svg",
        "23f89b7983d5154d9275dcfa029bfe2a5599ad339c80675efb7c5eabda587d1a",
        12_509,
    ),
}
ADDITIVE = {
    "source": (
        "tools/verify_python_re_callable_introspection_v1.py",
        "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653",
        75_608,
    ),
    "protocol": (
        "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
        "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
        8_952,
    ),
    "contract": (
        "oracle/phase1/p0-callable-introspection-v1.json",
        "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
        14_749,
    ),
}
ACTUAL_RUST_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-"
    "phase2-v12-rust-flag-original-p0-failures-publication-receipt.json",
    "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3",
    4_674,
)
HISTORICAL_ZIG_RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-"
    "phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json",
    "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba",
    4_534,
)
SOURCE_OWNERS: tuple[tuple[str, str, int], ...] = (
    (
        "candidates/zig_candidate.py",
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        68_422,
    ),
    (
        "candidates/zig/mini_regex.zig",
        "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
        186_915,
    ),
    ("candidates/zig/py_bridge.c", BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
)
ORIGINAL_NATIVE: dict[str, dict[str, Any]] = {
    "engine": {
        "relative": "candidates/_zig_probe.so",
        "sha256": "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
        "bytes": 478_432,
        "device": 2_064,
        "inode": 431_260,
        "mode": 0o700,
        "uid": 1_000,
        "nlink": 1,
    },
    "bridge": {
        "relative": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b",
        "bytes": 134_112,
        "device": 2_064,
        "inode": 431_274,
        "mode": 0o700,
        "uid": 1_000,
        "nlink": 1,
    },
}
NATIVE_PINS = {
    "engine": {
        "filename": "_zig_probe.so",
        "relative": ORIGINAL_NATIVE["engine"]["relative"],
        "sha256": ENGINE_SHA256,
        "bytes": ENGINE_BYTES,
    },
    "bridge": {
        "filename": "_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "relative": ORIGINAL_NATIVE["bridge"]["relative"],
        "sha256": BRIDGE_SHA256,
        "bytes": BRIDGE_BYTES,
    },
}
ENGINE_EXPORTS = (
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide",
    "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
)
BRIDGE_IMPORTS = (
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group",
    "rebar_zig_name_length",
)


class CampaignError(Exception):
    """The exact corrected original Zig campaign cannot be authenticated."""


class SourceOnlyViolation(CampaignError):
    """A source-only test attempted a real external effect."""


class GracefulControllerSignal(CampaignError):
    """A recoverable controller was stopped by an actual graceful signal."""

    def __init__(self, signum: int) -> None:
        self.signum = signum
        self.signal_name = signal.Signals(signum).name
        super().__init__("received " + self.signal_name)


def require(valid: Any, reason: str) -> None:
    if valid is not True:
        raise CampaignError(reason)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(part in "0123456789abcdef" for part in value),
            "require one complete lowercase SHA-256 for " + label)
    return value


def digest(raw: Any) -> str:
    require(type(raw) is bytes, "hash only complete authenticated bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(
            value, ensure_ascii=True, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CampaignError("reject noncanonical original evidence") from error


def strict_document(raw: Any, label: str,
                    *, exact: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes, "require complete bytes for " + label)

    def unique(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in rows:
            require(type(key) is str and key not in result,
                    "reject repeated JSON keys in " + label)
            result[key] = value
        return result

    def nonfinite(_value: str) -> Any:
        raise CampaignError("reject nonfinite original evidence in " + label)

    try:
        result = json.loads(raw.decode("utf-8", "strict"),
                            object_pairs_hook=unique, parse_constant=nonfinite)
    except (UnicodeError, ValueError, TypeError, OverflowError,
            RecursionError) as error:
        raise CampaignError("reject incomplete JSON: " + label) from error
    require(type(result) is dict and (not exact or canonical(result) == raw),
            "require the exact canonical original document: " + label)
    return result


def checked_relative(value: Any, *, archive: bool = False) -> str:
    require(type(value) is str and 0 < len(value) <= 512
            and "\\" not in value and "\x00" not in value,
            "require one bounded relative source owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value
            and all(part not in ("", ".", "..") for part in parsed.parts)
            and "holdout" not in value.casefold()
            and (
                "benchmark" not in value.casefold()
                or value == "tools/rust_public_practice_benchmark_v1.py"
            )
            and not value.endswith((".so", ".dll", ".dylib")),
            "reject a native target, holdout or escaped source owner")
    require((not value.endswith(".gz") and not archive)
            or (archive and value == BUILD["archive"][0]),
            "allow inflation only for the exact bounded Zig V12 build archive")
    return value


def read_owned(item: tuple[str, str, int], *,
               archive: bool = False) -> tuple[bytes, dict[str, Any]]:
    relative, expected, expected_size = item
    checked_relative(relative, archive=archive)
    checked_digest(expected, relative)
    maximum = MAX_BUILD_ARCHIVE_BYTES if archive else MAX_SOURCE_BYTES
    require(type(expected_size) is int and 0 < expected_size <= maximum,
            "bound every exact independently frozen owner")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory_flags = flags | os.O_DIRECTORY
    opened: list[int] = []
    try:
        parent = os.open(str(ROOT), directory_flags)
        opened.append(parent)
        pieces = relative.split("/")
        for component in pieces[:-1]:
            parent = os.open(component, directory_flags, dir_fd=parent)
            opened.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a redirected immutable owner parent")
        descriptor = os.open(pieces[-1], flags, dir_fd=parent)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(pieces[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size,
                     before.st_nlink, before.st_uid)
                == (visible.st_dev, visible.st_ino, visible.st_size,
                    visible.st_nlink, visible.st_uid)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and before.st_size == expected_size,
                "reject a substituted, linked or incomplete owner: " + relative)
        chunks: list[bytes] = []
        remaining = expected_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(part) is bytes and bool(part),
                    "reject truncated immutable bytes: " + relative)
            remaining -= len(part)
            chunks.append(part)
        require(os.read(descriptor, 1) == b"",
                "reject hidden trailing source bytes: " + relative)
        raw = b"".join(chunks)
        final = os.fstat(descriptor)
        last = os.stat(pieces[-1], dir_fd=parent, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns,
                 before.st_nlink, before.st_uid)
                == (final.st_dev, final.st_ino, final.st_size,
                    final.st_mtime_ns, final.st_ctime_ns,
                    final.st_nlink, final.st_uid)
                and (final.st_dev, final.st_ino, final.st_size)
                == (last.st_dev, last.st_ino, last.st_size)
                and len(raw) == expected_size and digest(raw) == expected,
                "reject changed immutable bytes or owner: " + relative)
        owner = {
            "path": relative, "sha256": expected, "bytes": expected_size,
            "device": final.st_dev, "inode": final.st_ino,
            "mode": stat.S_IMODE(final.st_mode),
            "uid": final.st_uid, "nlink": final.st_nlink,
        }
        return raw, owner
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_private_snapshot(record: Mapping[str, Any],
                          expected: Mapping[str, Any], *,
                          root: str) -> bytes:
    path = record.get("path")
    require(type(path) is str and path.startswith(root + "/")
            and path == str(PurePosixPath(path))
            and path.startswith("/tmp/" + "rebar-phase2-zig-scanner-capture-source-build-v2-")
            and "\\" not in path and "\x00" not in path
            and "holdout" not in path.casefold()
            and "benchmark" not in path.casefold(),
            "read only a recorded original first-party V12 private snapshot")
    require(record.get("sha256") == expected["sha256"]
            and record.get("bytes") == expected["bytes"]
            and record.get("link_count") == 1
            and record.get("mode") in ("0600", "0700")
            and type(record.get("device")) is int
            and type(record.get("inode")) is int,
            "reject a substituted V12 private source or native owner")
    components = PurePosixPath(path).parts
    require(components[:2] == ("/", "tmp")
            and all(part not in ("", ".", "..") for part in components[2:]),
            "reject an escaped private build snapshot")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    opened: list[int] = []
    try:
        parent = os.open("/tmp", flags | os.O_DIRECTORY)
        opened.append(parent)
        for part in components[2:-1]:
            parent = os.open(part, flags | os.O_DIRECTORY, dir_fd=parent)
            opened.append(parent)
            seen = os.fstat(parent)
            require(stat.S_ISDIR(seen.st_mode)
                    and seen.st_uid == os.geteuid()
                    and stat.S_IMODE(seen.st_mode) == 0o700,
                    "reject a public, substituted or cross-family private parent")
        descriptor = os.open(components[-1], flags, dir_fd=parent)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        named = os.stat(components[-1], dir_fd=parent, follow_symlinks=False)
        expected_mode = int(record["mode"], 8)
        require(stat.S_ISREG(first.st_mode)
                and (first.st_dev, first.st_ino, first.st_size,
                     first.st_uid, first.st_nlink)
                == (named.st_dev, named.st_ino, named.st_size,
                    named.st_uid, named.st_nlink)
                and first.st_dev == record["device"]
                and first.st_ino == record["inode"]
                and first.st_size == expected["bytes"]
                and first.st_uid == os.geteuid()
                and first.st_nlink == 1
                and stat.S_IMODE(first.st_mode) == expected_mode,
                "reject a replaced, hardlinked or foreign V12 private snapshot")
        require(0 < first.st_size <= MAX_NATIVE_BYTES,
                "bound each exact private matching or source snapshot")
        chunks: list[bytes] = []
        remaining = first.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk),
                    "reject incomplete corrected private native bytes")
            remaining -= len(chunk)
            chunks.append(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject hidden corrected private bytes")
        raw = b"".join(chunks)
        last = os.fstat(descriptor)
        visible = os.stat(components[-1], dir_fd=parent, follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns,
                 first.st_uid, first.st_nlink)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns,
                    last.st_uid, last.st_nlink)
                and (last.st_dev, last.st_ino, last.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and digest(raw) == expected["sha256"],
                "reject a changed or incorrectly hashed V12 phase artifact")
        return raw
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def owner_document(item: tuple[str, str, int]) -> dict[str, Any]:
    checked_relative(item[0], archive=item[0] == BUILD["archive"][0])
    return {"path": item[0], "sha256": checked_digest(item[1], item[0]),
            "bytes": item[2]}


def grouped_owners(group: Mapping[str, tuple[str, str, int]]) -> dict[str, Any]:
    return {name: owner_document(item)
            for name, item in sorted(group.items())}


def zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_recoveries": 0,
        "actual_native_library_loads": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "canonical_target_links": 0,
        "canonical_target_replacements": 0,
        "source_freeze_original_targets_modified": 0,
        "recovery_roots_created": 0,
        "recovery_locks_acquired": 0,
        "recovery_journals_created": 0,
        "signal_handlers_installed": 0,
        "signal_masks_installed": 0,
        "threads_started": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "final_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "matching_failure_archives_opened": 0,
        "matching_failure_archives_inflated": 0,
        "actual_corrected_build_archive_files_opened": 1,
        "actual_corrected_build_archive_compressed_bytes_read": BUILD["archive"][2],
        "actual_corrected_build_archive_uncompressed_bytes_read": BUILD_PLAIN_BYTES,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "final_comparison_cases_generated": False,
        "final_comparison_planned_case_count": 4_194_304,
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "winner_selected": False,
        "workspace_mutations": 0,
    }


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only the exact isolated stable CPython 3.14.6 source owner")


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "Zig V3 campaign source")
    checked_digest(protocol_pin, "Zig V3 campaign explanation")
    return {
        "schema": CONTRACT_SCHEMA,
        "status": "SOURCE FROZEN; CORRECTED ZIG V12 MATCHING NOT RUN",
        "version": 3,
        "family": FAMILY,
        "campaign_label": LABEL,
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "pinned_cpython": {
            "path": PYTHON, "sha256": PYTHON_SHA256,
            "version": "3.14.6", "isolated": True, "bytecode_writes": False,
        },
        "original_oracle": {
            "goal": owner_document(GOAL),
            "phase_one": owner_document(PHASE_ONE),
            "unchanged_v3_producer": grouped_owners(PRODUCER),
            "immutable_v2_zig_campaign": grouped_owners(ZIG_V2),
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "family_count": 6,
            "source_owner_count": 25,
            "owned_zig_source_count": 3,
            "canonical_public_module": "candidates.zig_candidate",
            "canonical_bridge_module": "candidates._zig_bridge",
            "upstream_public_record_count": 152,
            "upstream_runnable_public_case_count": 151,
            "upstream_debug_build_skip_count": 1,
            "nested_case_count": 128,
            "nested_interpreter_events": 394,
            "nested_interpreters_created": 11,
            "nested_interpreters_destroyed": 11,
            "nested_fresh_temporary_interpreters": 8,
            "external_regex_dependency_allowed": False,
            "stdlib_re_fallback_allowed": False,
            "cross_family_matching_allowed": False,
            "candidate_wrapper_allowed": False,
            "reference_rerun_allowed": False,
            "owned_zig_ctypes_only": True,
        },
        "actual_corrected_v12_build": {
            "owners": grouped_owners(BUILD),
            "build_status": "PASS",
            "build_label": BUILD_LABEL,
            "compressed_archive_byte_limit": MAX_BUILD_ARCHIVE_BYTES,
            "uncompressed_archive_byte_limit": MAX_BUILD_PLAIN_BYTES,
            "uncompressed_sha256": BUILD_PLAIN_SHA256,
            "uncompressed_bytes": BUILD_PLAIN_BYTES,
            "actual_independent_phase_count": 2,
            "actual_compiler_process_count": 26,
            "actual_corrected_source_apply_count": 2,
            "process_names_per_phase": list(PROCESS_NAMES),
            "phase_names": list(PHASE_NAMES),
            "source_owners_per_phase": 3,
            "complete_first_party_source_owners": [
                owner_document(item) for item in SOURCE_OWNERS
            ],
            "corrected_bridge_source": {
                "relative": "candidates/zig/py_bridge.c",
                "sha256": BRIDGE_SOURCE_SHA256,
                "bytes": BRIDGE_SOURCE_BYTES,
                "identical_to_canonical_first_party_source": True,
                "v1_conditional_overlay_used": False,
            },
            "native_engine": {
                "sha256": ENGINE_SHA256, "bytes": ENGINE_BYTES,
                "first_party_export_count": len(ENGINE_EXPORTS),
            },
            "native_bridge": {
                "sha256": BRIDGE_SHA256, "bytes": BRIDGE_BYTES,
                "runpath": "$ORIGIN",
                "first_party_import_count": len(BRIDGE_IMPORTS),
            },
            "raw_elf_auditor": grouped_owners(RAW_ELF),
            "full_native_bytes_reauthenticated": True,
            "both_phase_native_roles_byte_identical": True,
            "external_matching_engine_count": 0,
            "stdlib_matching_engine_count": 0,
            "cross_family_engine_count": 0,
            "native_loader_symbol_count": 0,
            "candidate_matching": "NOT MEASURED",
            "candidate_qualified": False,
        },
        "preserved_v31_history": {
            "owners": grouped_owners(V31),
            "repository_evidence_owner_count": HISTORICAL_V31_OWNER_COUNT,
            "authenticated_reference_count": HISTORICAL_V31_REFERENCE_COUNT,
            "actual_historical_rust_status": "FAIL",
            "actual_historical_rust_semantic_mismatch_count": 1_087,
            "actual_historical_rust_verified_passing_case_count": 7_438,
            "actual_c_status": "FAIL",
            "actual_c_semantic_mismatch_count": 1_230,
            "actual_c_verified_passing_case_count": 7_325,
            "actual_zig_status": "FAIL",
            "actual_zig_semantic_mismatch_count": 2_172,
            "actual_zig_verified_passing_case_count": 2_847,
            "actual_zig_candidate_worker_count": 13,
            "actual_zig_completed_suite_count": 13,
            "historical_zero_worker_zig_attempt_preserved": True,
            "qualified_candidate_count": 0,
            "concurrent_v33_source_or_graph_not_required": True,
            "unpublished_source_owners_do_not_change_evidence_denominator": True,
        },
        "actual_corrected_rust_matching": {
            "receipt": owner_document(ACTUAL_RUST_RECEIPT),
            "receipt_status": "PASS",
            "receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1_036,
            "verified_passing_case_count": 8_965,
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "infrastructure_failure_count": 0,
            "all_four_original_targets_restored": True,
            "matching_archive_opened": False,
            "candidate_qualified": False,
        },
        "actual_previous_zig_matching": {
            "receipt": owner_document(HISTORICAL_ZIG_RECEIPT),
            "receipt_status": "PASS",
            "receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 2_172,
            "verified_passing_case_count": 2_847,
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "infrastructure_failure_count": 0,
            "matching_archive_opened": False,
            "candidate_qualified": False,
        },
        "current_evidence": {
            "historical_v31_evidence_owner_count": HISTORICAL_V31_OWNER_COUNT,
            "historical_v31_authenticated_reference_count": HISTORICAL_V31_REFERENCE_COUNT,
            "additional_corrected_rust_matching_evidence_owner_count": 2,
            "additional_corrected_zig_v12_build_evidence_owner_count": 2,
            "actual_evidence_owner_count_before_new_campaign": ACTUAL_EVIDENCE_OWNER_COUNT,
            "actual_authenticated_reference_count_before_new_campaign":
                ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "future_campaign_evidence_owners_created": 0,
            "qualified_candidate_count": 0,
        },
        "additive_callable_introspection": {
            "owners": grouped_owners(ADDITIVE),
            "additive_case_count": 50,
            "reference_status": "NOT RUN",
            "candidate_status": "NOT RUN",
            "included_in_original_denominator": False,
            "original_case_execution_denominator": CASE_COUNT,
        },
        "normalized_recovery": {
            "activation_v7": grouped_owners(ACTIVATION_V7),
            "activation_v6_journal_primitives": grouped_owners(ACTIVATION_V6),
            "immutable_v2_worker_source": grouped_owners(ZIG_V2),
            "public_recovery_root": PUBLIC_RECOVERY_ROOT,
            "public_root_mode": "0700",
            "lock_filename": LOCK_NAME,
            "lock_mode": "0600",
            "exclusive_nonblocking_recovery_lock": True,
            "journal_filename": "recovery-journal.json",
            "journal_fsynced_and_announced_before_first_replacement": True,
            "original_inode_backup": "ADJACENT SAME-DIRECTORY HARDLINK",
            "source_target_count": 0,
            "native_target_count": 2,
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "original_native_owners": [
                {"role": role, "original": copy.deepcopy(ORIGINAL_NATIVE[role])}
                for role in ROLE_ORDER
            ],
            "registered_graceful_signals": list(SIGNAL_NAMES),
            "block_signals_during_target_mutations": True,
            "public_recovery_mode": "--recover",
            "group_atomic": False,
            "sigkill_automatically_recovered": False,
            "power_failure_automatically_recovered": False,
            "sigkill_or_power_failure_requires_explicit_recovery": True,
            "recovery_idempotent": True,
            "unknown_target_overwritten": False,
        },
        "future_complete_campaign": {
            "status": "NOT RUN",
            "actual_candidate_workers": 0,
            "future_worker_count": SUITE_COUNT,
            "one_distinct_isolated_process_per_original_suite": True,
            "continue_after_semantic_or_worker_failure": True,
            "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
            "maximum_complete_worker_stdout_bytes": MAX_WORKER_STDOUT_BYTES,
            "maximum_complete_worker_stderr_bytes": MAX_WORKER_STDERR_BYTES,
            "maximum_compressed_suite_observation_bytes": MAX_SUITE_COMPRESSED_BYTES,
            "maximum_uncompressed_suite_observation_bytes": MAX_SUITE_PLAIN_BYTES,
            "maximum_public_report_bytes": MAX_PUBLIC_REPORT_BYTES,
            "all_original_mismatches_and_records_retained": True,
            "deterministic_single_member_zero_time_gzip": True,
            "publication_only_after_original_inode_restoration": True,
            "exclusive_archive_and_distinct_receipt_mode": "0600",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "qualification_requires_all_31237_cases_pass": True,
            "qualification_requires_all_13_real_workers": True,
            "qualification_requires_zero_infrastructure_failures": True,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
        },
        "lossless_publication_primitives": grouped_owners(PUBLICATION),
        "source_only_effects": zero_effects(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    expected = protocol_document(source_pin, protocol_pin)
    require(type(value) is dict and canonical(value) == canonical(expected),
            "reject an altered V12 build, owner, original suite or recovery policy")
    return value


def bounded_build_gzip(raw: bytes) -> bytes:
    require(type(raw) is bytes and len(raw) == BUILD["archive"][2]
            and len(raw) <= MAX_BUILD_ARCHIVE_BYTES
            and digest(raw) == BUILD["archive"][1]
            and raw[:3] == b"\x1f\x8b\x08",
            "inflate only the one exactly authenticated corrected Zig build")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    chunks: list[bytes] = []
    total = 0
    cursor = 0
    try:
        while cursor < len(raw):
            piece = raw[cursor:cursor + 65_536]
            cursor += len(piece)
            pending = piece
            while pending:
                block = decoder.decompress(pending, 65_536)
                total += len(block)
                require(total <= MAX_BUILD_PLAIN_BYTES,
                        "reject an expanded Zig build report beyond its strict bound")
                chunks.append(block)
                pending = decoder.unconsumed_tail
                require(not decoder.unused_data,
                        "reject concatenated or hidden Zig build gzip members")
        tail = decoder.flush()
        total += len(tail)
        require(total <= MAX_BUILD_PLAIN_BYTES and decoder.eof
                and not decoder.unused_data,
                "reject an incomplete corrected build gzip envelope")
        chunks.append(tail)
    except (zlib.error, EOFError, OSError) as error:
        raise CampaignError("reject a damaged corrected Zig build report") from error
    plain = b"".join(chunks)
    require(total == BUILD_PLAIN_BYTES and len(plain) == BUILD_PLAIN_BYTES
            and digest(plain) == BUILD_PLAIN_SHA256,
            "bind all 299800 actual source-build report bytes")
    return plain


def load_frozen(item: tuple[str, str, int], name: str) -> types.ModuleType:
    raw, first = read_owned(item)
    checked_relative(item[0])
    require(type(name) is str and name.startswith("_rebar_owned_zig_v3_")
            and name not in sys.modules,
            "load one exclusively named, digest-pinned first-party module")
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
    _, last = read_owned(item)
    require((first["device"], first["inode"], first["sha256"])
            == (last["device"], last["inode"], last["sha256"]),
            "reject immutable worker primitives changed during loading")
    return module


def decode_process_stream(row: Mapping[str, Any],
                          channel: str) -> None:
    record = row.get(channel)
    require(type(record) is dict and record.get("complete") is True
            and type(record.get("bytes")) is int
            and 0 <= record["bytes"] <= MAX_SOURCE_BYTES
            and type(record.get("base64")) is str,
            "retain a complete bounded actual source-build " + channel)
    checked_digest(record.get("sha256"), "actual compiler " + channel)
    try:
        raw = base64.b64decode(record["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise CampaignError("reject hidden source-build process bytes") from error
    require(len(raw) == record["bytes"]
            and digest(raw) == record["sha256"],
            "reject a fabricated actual compiler stream")


def validate_native_audit(audit: Any, role: str) -> None:
    require(type(audit) is dict and audit.get("role") == role
            and audit.get("external_regex_engine_count") == 0
            and audit.get("stdlib_regex_engine_count") == 0
            and audit.get("cross_family_engine_count") == 0
            and audit.get("native_loader_symbol_count") == 0
            and audit.get("network_symbol_count") == 0
            and audit.get("legacy_rpath_count") == 0,
            "reject a delegated, dynamically loaded or cross-family matching role")
    if role == "engine":
        require(audit.get("needed") == ["libc.so.6"]
                and audit.get("runpath") is None
                and audit.get("soname") == "_zig_probe.so"
                and tuple(audit.get("defined_first_party_symbols", ()))
                == ENGINE_EXPORTS
                and audit.get("imported_first_party_symbols") == [],
                "require all and only the genuine owned Zig engine exports")
    else:
        require(audit.get("needed") == ["_zig_probe.so", "libc.so.6"]
                and audit.get("runpath") == "$ORIGIN"
                and audit.get("defined_first_party_symbols") == []
                and tuple(audit.get("imported_first_party_symbols", ()))
                == BRIDGE_IMPORTS,
                "link the Python bridge exclusively to its adjacent owned engine")


def validate_build_phase(
    phase: Any, index: int, root: str, *,
    parser: types.ModuleType | None,
    inspect_private: bool,
) -> dict[str, Any]:
    name = PHASE_NAMES[index]
    require(type(phase) is dict and phase.get("name") == name
            and type(phase.get("source_snapshots")) is dict
            and set(phase["source_snapshots"])
            == {item[0] for item in SOURCE_OWNERS}
            and type(phase.get("native_outputs")) is dict
            and set(phase["native_outputs"]) == set(ROLE_ORDER),
            "reject an omitted or substituted corrected Zig build phase")
    phase_prefix = root + "/" + name
    sources: dict[str, Any] = {}
    for item in SOURCE_OWNERS:
        path, fingerprint, size = item
        row = phase["source_snapshots"][path]
        require(type(row) is dict
                and row.get("path") == phase_prefix + "/source/" + path
                and row.get("sha256") == fingerprint
                and row.get("bytes") == size
                and row.get("mode") == "0600"
                and row.get("link_count") == 1,
                "reject an omitted canonical V2-corrected phase source")
        if inspect_private:
            read_private_snapshot(row, {"sha256": fingerprint, "bytes": size},
                                  root=root)
        sources[path] = row
    overlay = phase.get("overlay_application")
    require(type(overlay) is dict
            and overlay.get("schema")
            == "rebar-phase2-owned-zig-scanner-capture-source-repair-v2"
            and overlay.get("status") == "PASS"
            and overlay.get("phase") == name
            and overlay.get("source_apply_count") == 1
            and overlay.get("candidate_original_modified") is False
            and overlay.get("byte_identical_to_original") is True
            and overlay.get("derived_source_sha256") == BRIDGE_SOURCE_SHA256
            and overlay.get("derived_source_bytes") == BRIDGE_SOURCE_BYTES
            and overlay.get("snapshot_root") == phase_prefix + "/source",
            "reject the stale V1 scanner overlay or changed canonical bridge")
    outputs: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        entry = phase["native_outputs"][role]
        pin = NATIVE_PINS[role]
        require(type(entry) is dict and type(entry.get("owner")) is dict,
                "require the complete actual corrected native " + role)
        owner = entry["owner"]
        require(owner.get("path")
                == phase_prefix + "/native/" + pin["filename"]
                and owner.get("sha256") == pin["sha256"]
                and owner.get("bytes") == pin["bytes"]
                and owner.get("mode") == "0700"
                and owner.get("link_count") == 1,
                "bind the exact actual corrected native owner: " + role)
        validate_native_audit(entry.get("independence_audit"), role)
        raw_elf = entry.get("raw_elf64")
        require(type(raw_elf) is dict
                and raw_elf.get("file_sha256") == pin["sha256"]
                and raw_elf.get("file_size") == pin["bytes"],
                "retain complete first-party raw ELF for " + role)
        raw: bytes | None = None
        if inspect_private:
            require(type(parser) is types.ModuleType
                    and callable(getattr(parser, "parse_owned_elf64", None)),
                    "require the independently pinned first-party ELF parser")
            raw = read_private_snapshot(owner, pin, root=root)
            parsed = parser.parse_owned_elf64(raw)
            require(type(parsed) is dict
                    and canonical(parsed) == canonical(raw_elf),
                    "reauthenticate every byte and ELF table of " + role)
        outputs[role] = {
            "owner": copy.deepcopy(owner),
            "raw_elf64": copy.deepcopy(raw_elf),
            "bytes": raw,
        }
    return {"name": name, "sources": sources, "native": outputs}


def validate_v12_report(
    report: Any, receipt: Any, archive_owner: Mapping[str, Any], *,
    parser: types.ModuleType | None,
    inspect_private: bool,
) -> dict[str, Any]:
    require(type(report) is dict and type(receipt) is dict
            and type(archive_owner) is dict,
            "require actual complete corrected build and separate receipt")
    require(report.get("schema") == "rebar-phase2-owned-zig-scanner-source-build-v12"
            and report.get("status") == "PASS"
            and report.get("version") == 12
            and report.get("family") == FAMILY
            and report.get("label") == BUILD_LABEL
            and report.get("source_sha256") == BUILD["source"][1]
            and report.get("protocol_sha256") == BUILD["protocol"][1]
            and report.get("contract_sha256") == BUILD["contract"][1]
            and report.get("frozen_case_execution_count") == CASE_COUNT
            and report.get("suite_count") == SUITE_COUNT
            and report.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and report.get("actual_build_process_count") == 26
            and report.get("actual_source_apply_count") == 2
            and report.get("corrected_bridge_sha256") == BRIDGE_SOURCE_SHA256
            and report.get("corrected_bridge_bytes") == BRIDGE_SOURCE_BYTES
            and report.get("v1_overlay_used") is False
            and report.get("actual_evidence_owner_count_before_publication") == 153
            and report.get("actual_authenticated_reference_count_before_publication") == 158
            and report.get("candidate_correctness") == "NOT MEASURED"
            and report.get("candidate_imports") == 0
            and report.get("candidate_processes_started") == 0
            and report.get("native_libraries_loaded") == 0
            and report.get("network_requests") == 0
            and report.get("clock_samples") == 0
            and report.get("holdout") == "NOT OPENED",
            "reject a stale build, changed oracle, invented match or V1 bridge")
    require(receipt.get("schema")
            == "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == BUILD_LABEL
            and receipt.get("source_sha256") == BUILD["source"][1]
            and receipt.get("protocol_sha256") == BUILD["protocol"][1]
            and receipt.get("contract_sha256") == BUILD["contract"][1]
            and receipt.get("uncompressed_sha256") == BUILD_PLAIN_SHA256
            and receipt.get("uncompressed_bytes") == BUILD_PLAIN_BYTES
            and receipt.get("actual_compiler_process_count") == 26
            and receipt.get("actual_source_apply_count") == 2
            and receipt.get("corrected_bridge_sha256") == BRIDGE_SOURCE_SHA256
            and receipt.get("corrected_bridge_bytes") == BRIDGE_SOURCE_BYTES
            and receipt.get("v1_overlay_used") is False
            and receipt.get("actual_evidence_owner_count_before_publication") == 153
            and receipt.get("actual_authenticated_reference_count_before_publication") == 158
            and receipt.get("repository_evidence_owner_count_after_publication") == 155
            and receipt.get("authenticated_history_reference_count_after_publication") == 160
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED",
            "reject an altered genuine corrected-build publication receipt")
    selected_archive = receipt.get("archive")
    require(type(selected_archive) is dict
            and selected_archive.get("path") == BUILD["archive"][0]
            and selected_archive.get("sha256") == BUILD["archive"][1]
            and selected_archive.get("bytes") == BUILD["archive"][2]
            and selected_archive.get("device") == archive_owner["device"]
            and selected_archive.get("inode") == archive_owner["inode"]
            and selected_archive.get("uid") == archive_owner["uid"]
            and selected_archive.get("nlink") == archive_owner["nlink"]
            and selected_archive.get("mode") == "0600"
            and selected_archive.get("exclusive_creation") is True
            and selected_archive.get("file_fsync_completed") is True
            and selected_archive.get("directory_fsync_completed") is True
            and selected_archive.get("same_inode_readback_verified") is True,
            "bind the independently fsynced receipt to its actual archive inode")
    root_record = report.get("private_root")
    require(type(root_record) is dict and type(root_record.get("path")) is str
            and root_record["path"].startswith(
                "/tmp/rebar-phase2-zig-scanner-capture-source-build-v2-")
            and len(PurePosixPath(root_record["path"]).parts) == 3
            and root_record.get("mode") == "0700",
            "require the exact exclusive corrected V2 private build root")
    root = root_record["path"]
    processes = report.get("processes")
    require(type(processes) is list and len(processes) == 26
            and [(row.get("phase"), row.get("name"))
                 for row in processes if type(row) is dict]
            == [(phase, name) for phase in PHASE_NAMES for name in PROCESS_NAMES],
            "require all twenty-six real ordered compiler and inspector roles")
    seen_pids: set[int] = set()
    for row in processes:
        require(type(row) is dict
                and type(row.get("pid")) is int and row["pid"] > 0
                and row["pid"] not in seen_pids
                and row.get("returncode") == 0
                and row.get("signal") is None
                and row.get("shell", False) is False
                and type(row.get("argv")) is list and bool(row["argv"])
                and all(type(part) is str for part in row["argv"])
                and row.get("working_directory") == root + "/" + row["phase"],
                "reject an invented, duplicate, failed or shell build process")
        decode_process_stream(row, "stdout")
        decode_process_stream(row, "stderr")
        seen_pids.add(row["pid"])
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2,
            "require both genuinely independent corrected source-build phases")
    selected = [
        validate_build_phase(
            phase, index, root, parser=parser, inspect_private=inspect_private,
        )
        for index, phase in enumerate(phases)
    ]
    for relative, _, _ in SOURCE_OWNERS:
        first = selected[0]["sources"][relative]
        second = selected[1]["sources"][relative]
        require((first["device"], first["inode"])
                != (second["device"], second["inode"]),
                "reject shared corrected phase source inode: " + relative)
    for role in ROLE_ORDER:
        first = selected[0]["native"][role]["owner"]
        second = selected[1]["native"][role]["owner"]
        require((first["device"], first["inode"])
                != (second["device"], second["inode"])
                and first["sha256"] == second["sha256"]
                and first["bytes"] == second["bytes"],
                "require two independently reproduced corrected " + role + "s")
    reproduction = report.get("reproducibility")
    require(type(reproduction) is dict
            and reproduction.get("status") == "PASS"
            and reproduction.get("independent_phase_count") == 2
            and reproduction.get("byte_identical_native_role_count") == 2
            and reproduction.get("compiler_process_count") == 26
            and reproduction.get("source_apply_count") == 2
            and type(reproduction.get("roles")) is dict
            and set(reproduction["roles"]) == set(ROLE_ORDER),
            "reject invented corrected source-build reproducibility")
    for role in ROLE_ORDER:
        entry = reproduction["roles"][role]
        require(type(entry) is dict
                and entry.get("sha256") == NATIVE_PINS[role]["sha256"]
                and entry.get("bytes") == NATIVE_PINS[role]["bytes"]
                and entry.get("phase_owner_count") == 2
                and entry.get("byte_identical") is True,
                "bind complete reproducibility to corrected first-party " + role)
    differences = report.get("raw_elf_differences")
    require(type(differences) is dict
            and differences.get("schema")
            == "rebar-phase2-owned-zig-scanner-source-build-v12-all-phase-raw-elf-differences"
            and differences.get("independent_phase_count") == 2
            and differences.get("native_role_count") == 2
            and differences.get("all_native_artifacts_byte_identical") is True
            and differences.get("additional_compiler_or_inspector_processes") == 0
            and differences.get("comparison_completed_before_reproducibility_classification")
            is True
            and type(differences.get("roles")) is dict
            and set(differences["roles"]) == set(ROLE_ORDER),
            "require complete first-party actual ELF reproducibility comparisons")
    for role in ROLE_ORDER:
        comparison = differences["roles"][role]
        pin = NATIVE_PINS[role]
        require(type(comparison) is dict
                and comparison.get("byte_identical") is True
                and comparison.get("phase_a_sha256") == pin["sha256"]
                and comparison.get("phase_b_sha256") == pin["sha256"]
                and comparison.get("phase_a_bytes") == pin["bytes"]
                and comparison.get("phase_b_bytes") == pin["bytes"]
                and comparison.get("changed_section_count") == 0
                and comparison.get("total_differing_byte_count") == 0
                and comparison.get("difference_spans") == []
                and comparison.get("report_truncated") is False,
                "reject a hidden raw-byte corrected-build difference: " + role)
        if inspect_private:
            require(parser is not None
                    and callable(getattr(parser, "compare_owned_elf64", None)),
                    "retain the complete exact owned V7 ELF comparator")
            calculated = parser.compare_owned_elf64(
                selected[0]["native"][role]["bytes"],
                selected[1]["native"][role]["bytes"],
                selected[0]["native"][role]["raw_elf64"],
                selected[1]["native"][role]["raw_elf64"],
            )
            require(canonical(calculated) == canonical(comparison),
                    "recompute the exact actual corrected ELF comparison")
    return {
        "report": report,
        "receipt": receipt,
        "archive_owner": dict(archive_owner),
        "phases": selected,
        "actual_process_count": len(seen_pids),
    }


def validate_history(summary: Any, inputs: Any,
                     rust: Any, old_zig: Any) -> None:
    require(type(summary) is dict and type(inputs) is dict
            and summary.get("schema") == "rebar-candidate-current-overview-v31-summary"
            and summary.get("version") == 31
            and summary.get("status") == "PASS"
            and inputs.get("schema") == "rebar-candidate-current-overview-v31-inputs"
            and inputs.get("version") == 31
            and summary.get("repository_evidence_owner_count")
            == inputs.get("repository_evidence_owner_count")
            == HISTORICAL_V31_OWNER_COUNT
            and summary.get("authenticated_digest_addressed_history_paths")
            == inputs.get("all_digest_addressed_history_path_count")
            == HISTORICAL_V31_REFERENCE_COUNT
            and summary.get("full_case_denominator")
            == inputs.get("full_case_denominator") == CASE_COUNT
            and summary.get("suite_count") == inputs.get("suite_count") == 13
            and summary.get("private_waiver_count")
            == inputs.get("private_waiver_count") == 13
            and summary.get("qualified_candidate_count")
            == inputs.get("candidate_qualified_count") == 0
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1_087
            and summary.get("rust_original_campaign_verified_passing_case_count") == 7_438
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1_230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7_325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 2_172
            and summary.get("zig_original_campaign_verified_passing_case_count") == 2_847
            and summary.get("zig_original_campaign_candidate_worker_count") == 13
            and summary.get("zig_original_campaign_completed_suite_count") == 13
            and summary.get("zig_original_campaign_infrastructure_failure_count") == 0
            and summary.get("final_comparison_planned_case_count") == 4_194_304
            and summary.get("final_holdout_opened") is False
            and summary.get("final_comparison_cases_generated") is False
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("winner_selected") is False,
            "preserve V31 as actual historical evidence, never as the current count")
    require(type(rust) is dict
            and rust.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
            and rust.get("status") == "PASS"
            and rust.get("candidate_status") == "FAIL"
            and rust.get("family") == "rust"
            and rust.get("label") == "phase2-v12-rust-flag-original-p0"
            and rust.get("suite_count") == SUITE_COUNT
            and rust.get("completed_suite_count") == SUITE_COUNT
            and rust.get("case_execution_denominator") == CASE_COUNT
            and rust.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and rust.get("actual_candidate_workers") == SUITE_COUNT
            and rust.get("semantic_mismatch_count") == 1_036
            and rust.get("verified_passing_case_count") == 8_965
            and rust.get("infrastructure_failure_count") == 0
            and rust.get("candidate_qualified") is False
            and rust.get("all_four_original_targets_restored") is True
            and rust.get("restoration_verified_before_publication") is True
            and rust.get("historical_evidence_owner_count_before_publication") == 151
            and rust.get("historical_authenticated_reference_count_before_publication") == 156
            and rust.get("new_repository_evidence_owner_count") == 2
            and rust.get("resulting_repository_evidence_owner_count") == 153
            and rust.get("resulting_authenticated_reference_count") == 158,
            "never hide or call the actual 1036-loss Rust matching failure a pass")
    rust_archive = rust.get("archive")
    require(type(rust_archive) is dict
            and rust_archive.get("sha256")
            == "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f"
            and rust_archive.get("size_bytes") == 3_663_299,
            "bind the actual Rust failure only by its independently pinned receipt")
    require(type(old_zig) is dict
            and old_zig.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt"
            and old_zig.get("status") == "PASS"
            and old_zig.get("candidate_status") == "FAIL"
            and old_zig.get("family") == FAMILY
            and old_zig.get("suite_count") == SUITE_COUNT
            and old_zig.get("completed_suite_count") == SUITE_COUNT
            and old_zig.get("case_execution_denominator") == CASE_COUNT
            and old_zig.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and old_zig.get("actual_candidate_workers") == SUITE_COUNT
            and old_zig.get("semantic_mismatch_count") == 2_172
            and old_zig.get("verified_passing_case_count") == 2_847
            and old_zig.get("infrastructure_failure_count") == 0
            and old_zig.get("candidate_qualified") is False
            and old_zig.get("original_native_restored") is True
            and old_zig.get("restoration_verified_before_publication") is True
            and old_zig.get("actual_first_v1_attempt_status") == "FAIL"
            and old_zig.get("actual_first_v1_candidate_workers") == 0
            and old_zig.get("actual_first_v1_matching_case_execution_count") == 0,
            "retain both the real 13-worker Zig loss and genuine zero-worker attempt")


def validate_original_oracle(manifest: Any, contract: Any,
                             previous: Any) -> list[dict[str, Any]]:
    require(type(manifest) is dict
            and manifest.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and type(manifest.get("denominator")) is dict
            and manifest["denominator"].get("final_required_case_execution_denominator")
            == CASE_COUNT
            and manifest["denominator"].get("frozen_planned_case_execution_denominator")
            == CASE_COUNT
            and manifest["denominator"].get("counted_suite_ids")
            == [name for name, _ in SUITES]
            and type(manifest.get("original_upstream")) is dict
            and manifest["original_upstream"].get("private_waiver_count") == 13
            and manifest["original_upstream"].get("public_method_count") == 152
            and manifest["original_upstream"].get("runnable_public_method_count") == 151
            and type(manifest["original_upstream"].get("private_waivers")) is list
            and len(manifest["original_upstream"]["private_waivers"]) == 13,
            "never change the immutable original phase-one denominator or waivers")
    require(type(contract) is dict
            and contract.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and contract.get("version") == 3
            and contract.get("family_count") == 6
            and contract.get("source_owner_count") == 25
            and contract.get("suite_count") == SUITE_COUNT
            and contract.get("case_execution_denominator") == CASE_COUNT
            and type(contract.get("suites")) is list
            and [(row.get("id"), row.get("case_execution_count"))
                 for row in contract["suites"] if type(row) is dict]
            == list(SUITES),
            "freeze all and only the thirteen actual unchanged original observers")
    lifecycle = contract.get("successful_nested_lifecycle")
    require(type(lifecycle) is dict
            and lifecycle.get("counted_case_count") == 128
            and lifecycle.get("actual_case_interpreter_exec_calls") == 394
            and lifecycle.get("actual_interpreters_created") == 11
            and lifecycle.get("actual_interpreters_destroyed") == 11
            and lifecycle.get("actual_fresh_temporary_interpreters") == 8,
            "retain the actual original 128/394/11 interpreter lifecycle")
    families = [
        row for row in contract.get("families", [])
        if type(row) is dict and row.get("family") == FAMILY
    ]
    require(len(families) == 1
            and families[0].get("module") == "candidates.zig_candidate"
            and families[0].get("bridge_module") == "candidates._zig_bridge"
            and families[0].get("engine_relative")
            == ORIGINAL_NATIVE["engine"]["relative"]
            and families[0].get("bridge_relative")
            == ORIGINAL_NATIVE["bridge"]["relative"]
            and families[0].get("owned_ctypes_allowed") is True
            and families[0].get("combined_native_engine_and_bridge") is False
            and families[0].get("owned_source_count") == 3
            and [(item.get("relative"), item.get("sha256"),
                  item.get("size_bytes"))
                 for item in families[0].get("sources", [])
                 if type(item) is dict]
            == list(SOURCE_OWNERS),
            "reject an external wrapper, delegated engine or incomplete Zig closure")
    require(type(previous) is dict
            and previous.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v2-source-freeze"
            and previous.get("version") == 2
            and previous.get("family") == FAMILY
            and type(previous.get("original_oracle")) is dict
            and previous["original_oracle"].get("suite_count") == SUITE_COUNT
            and previous["original_oracle"].get("case_execution_denominator") == CASE_COUNT
            and previous["original_oracle"].get("named_private_waiver_count") == 13
            and [(row.get("id"), row.get("case_execution_count"))
                 for row in previous["original_oracle"].get("source_ordered_suites", [])
                 if type(row) is dict]
            == list(SUITES),
            "retain the independently frozen V2 genuine thirteen-worker policy")
    manifest_suites = manifest.get("suites")
    require(type(manifest_suites) is list and len(manifest_suites) == SUITE_COUNT,
            "retain all original named case-source owners")
    owners: list[dict[str, Any]] = []
    for (name, count), original, frozen in zip(
            SUITES, manifest_suites, contract["suites"], strict=True):
        require(type(original) is dict and type(frozen) is dict
                and original.get("id") == frozen.get("id") == name
                and original.get("case_execution_count")
                == frozen.get("case_execution_count") == count
                and original.get("matrix_sha256") == frozen.get("matrix_sha256")
                and original.get("baseline_records_sha256")
                == frozen.get("reference_records_sha256")
                and type(original.get("source")) is dict
                and original["source"].get("path") == frozen.get("source_relative")
                and original["source"].get("sha256") == frozen.get("source_sha256"),
                "reject changed, reordered or weaker original group: " + name)
        relative = frozen["source_relative"]
        seen = os.stat(str(ROOT / relative), follow_symlinks=False)
        require(stat.S_ISREG(seen.st_mode)
                and 0 < seen.st_size <= MAX_SOURCE_BYTES,
                "bound a frozen original case-source owner")
        item = (relative, frozen["source_sha256"], seen.st_size)
        _, owner = read_owned(item)
        owners.append(owner)
    return owners


def verify_context(
    source_pin: str, protocol_pin: str, contract_pin: str | None,
    *, retain: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    checked_digest(source_pin, "V3 source")
    checked_digest(protocol_pin, "V3 protocol")
    source_stat = os.stat(str(ROOT / SOURCE_RELATIVE), follow_symlinks=False)
    protocol_stat = os.stat(str(ROOT / PROTOCOL_RELATIVE), follow_symlinks=False)
    _, own_source = read_owned((SOURCE_RELATIVE, source_pin, source_stat.st_size))
    _, own_protocol = read_owned(
        (PROTOCOL_RELATIVE, protocol_pin, protocol_stat.st_size))
    read_owned(GOAL)
    raw_phase, _ = read_owned(PHASE_ONE)
    manifest = strict_document(raw_phase, "unchanged complete original phase-one")
    protected: dict[str, bytes] = {}
    for group in (PRODUCER, ZIG_V2, ACTIVATION_V7, ACTIVATION_V6,
                  PUBLICATION, BUILD, RAW_ELF, V31, ADDITIVE):
        for name, item in sorted(group.items()):
            if group is BUILD and name == "archive":
                continue
            raw, _ = read_owned(item)
            protected[item[0]] = raw
    producer_contract = strict_document(
        protected[PRODUCER["contract"][0]], "original six-family V3 contract")
    previous_contract = strict_document(
        protected[ZIG_V2["contract"][0]], "immutable original Zig V2 contract")
    suite_owners = validate_original_oracle(
        manifest, producer_contract, previous_contract)
    for item in SOURCE_OWNERS:
        read_owned(item)
    summary = strict_document(protected[V31["summary"][0]],
                              "historical V31 summary")
    graph_inputs = strict_document(protected[V31["inputs"][0]],
                                   "historical V31 inputs")
    rust_raw, rust_owner = read_owned(ACTUAL_RUST_RECEIPT)
    zig_raw, previous_zig_owner = read_owned(HISTORICAL_ZIG_RECEIPT)
    rust_receipt = strict_document(rust_raw, "actual completed Rust failure receipt")
    previous_zig = strict_document(zig_raw, "actual completed Zig failure receipt")
    validate_history(summary, graph_inputs, rust_receipt, previous_zig)
    build_contract = strict_document(
        protected[BUILD["contract"][0]], "independently frozen V12 source build")
    require(build_contract.get("schema")
            == "rebar-phase2-owned-zig-scanner-source-build-v12-source-freeze"
            and build_contract.get("version") == 12
            and build_contract.get("source", {}).get("sha256") == BUILD["source"][1]
            and build_contract.get("protocol", {}).get("sha256") == BUILD["protocol"][1]
            and build_contract.get("published_history", {}).get("authoritative_evidence_owner_count") == 153
            and build_contract.get("published_history", {}).get("authenticated_reference_count") == 158
            and build_contract.get("corrected_v2_overlay", {}).get("derived_bridge_sha256")
            == BRIDGE_SOURCE_SHA256
            and build_contract.get("corrected_v2_overlay", {}).get("derived_bridge_bytes")
            == BRIDGE_SOURCE_BYTES,
            "require the exact independently frozen genuine corrected V12 build")
    archive_raw, archive_owner = read_owned(BUILD["archive"], archive=True)
    receipt = strict_document(
        protected[BUILD["receipt"][0]], "genuinely published V12 build receipt")
    report = strict_document(
        bounded_build_gzip(archive_raw), "complete bounded V12 build report")
    parser = load_frozen(
        RAW_ELF["source"], "_rebar_owned_zig_v3_exact_complete_elf_v7")
    require(parser.SCHEMA == "rebar-phase2-owned-native-source-build-v7"
            and callable(getattr(parser, "parse_owned_elf64", None))
            and callable(getattr(parser, "compare_owned_elf64", None)),
            "load only the exact first-party complete raw-ELF V7 auditor")
    build = validate_v12_report(
        report, receipt, archive_owner, parser=parser, inspect_private=True)
    normalized = load_frozen(
        ACTIVATION_V7["source"], "_rebar_owned_zig_v3_exact_activation_v7")
    require(normalized.SCHEMA == "rebar-phase2-verified-native-activation-v7"
            and normalized.FAMILY == FAMILY
            and all(callable(getattr(normalized, name, None))
                    for name in ("verify_context", "parse_arguments",
                                 "activate", "recover")),
            "retain only the authenticated V7 exact-inode normalizer")
    normalized_context, normalized_retained = normalized.verify_context(
        ACTIVATION_V7["source"][1], ACTIVATION_V7["protocol"][1],
        ACTIVATION_V7["contract"][1], retain=True)
    require(type(normalized_context) is dict
            and normalized_context.get("status") == "PASS"
            and normalized_context.get("version") == 7
            and normalized_context.get("canonical_target_reads") == 0
            and normalized_context.get("canonical_target_stats") == 0
            and normalized_context.get("canonical_target_replacements") == 0
            and normalized_context.get("owner_shape_defect_proven_without_target_access") is True
            and normalized_context.get("uid_and_nlink_fabricated") is False
            and type(normalized_retained) is dict
            and type(normalized_retained.get("v6")) is types.ModuleType
            and type(normalized_retained.get("inherited")) is dict
            and type(normalized_retained["inherited"].get("mature"))
            is types.ModuleType,
            "authenticate the original V7 no-touch descriptor normalization")
    additive = strict_document(
        protected[ADDITIVE["contract"][0]], "frozen additive introspection")
    require(type(additive) is dict,
            "retain the separately frozen and unrun 50-case addition")
    frozen_owner = None
    if contract_pin is not None:
        checked_digest(contract_pin, "exact campaign machine contract")
        seen = os.stat(str(ROOT / CONTRACT_RELATIVE), follow_symlinks=False)
        raw, frozen_owner = read_owned(
            (CONTRACT_RELATIVE, contract_pin, seen.st_size))
        validate_contract(
            strict_document(raw, "complete original Zig V3 machine contract"),
            source_pin, protocol_pin)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "source verification may never import any actual candidate")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "version": 3,
        "family": FAMILY,
        "campaign_label": LABEL,
        "source": own_source,
        "protocol": own_protocol,
        "contract": frozen_owner,
        "historical_v31_evidence_owner_count": HISTORICAL_V31_OWNER_COUNT,
        "historical_v31_authenticated_reference_count":
            HISTORICAL_V31_REFERENCE_COUNT,
        "actual_evidence_owner_count": ACTUAL_EVIDENCE_OWNER_COUNT,
        "actual_authenticated_reference_count":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "original_case_source_owner_count": len(suite_owners),
        "independent_family_count": 6,
        "independent_source_owner_count": 25,
        "owned_zig_source_owner_count": len(SOURCE_OWNERS),
        "actual_corrected_v12_build_status": "PASS",
        "actual_corrected_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_corrected_v12_build_receipt_sha256": BUILD["receipt"][1],
        "actual_corrected_v12_build_plain_sha256": BUILD_PLAIN_SHA256,
        "actual_corrected_v12_build_plain_bytes": BUILD_PLAIN_BYTES,
        "actual_corrected_v12_compiler_process_count": 26,
        "actual_corrected_v12_independent_build_phase_count": 2,
        "actual_corrected_v12_source_apply_count": 2,
        "actual_corrected_v12_engine_sha256": ENGINE_SHA256,
        "actual_corrected_v12_engine_bytes": ENGINE_BYTES,
        "actual_corrected_v12_bridge_sha256": BRIDGE_SHA256,
        "actual_corrected_v12_bridge_bytes": BRIDGE_BYTES,
        "canonical_corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "canonical_corrected_bridge_source_bytes": BRIDGE_SOURCE_BYTES,
        "all_four_actual_private_native_snapshots_verified": True,
        "all_six_actual_private_source_snapshots_verified": True,
        "complete_first_party_elf_comparisons_verified": True,
        "previous_rust_semantic_mismatch_count": 1_087,
        "actual_corrected_rust_semantic_mismatch_count": 1_036,
        "actual_corrected_rust_verified_passing_case_count": 8_965,
        "actual_corrected_rust_candidate_worker_count": 13,
        "actual_c_semantic_mismatch_count": 1_230,
        "actual_c_verified_passing_case_count": 7_325,
        "historical_zig_semantic_mismatch_count": 2_172,
        "historical_zig_verified_passing_case_count": 2_847,
        "historical_zig_candidate_worker_count": 13,
        "historical_zig_zero_worker_attempt_preserved": True,
        "additive_callable_introspection_case_count": 50,
        "additive_callable_reference_status": "NOT RUN",
        "additive_callable_candidate_status": "NOT RUN",
        "additive_cases_in_original_denominator": False,
        "normalized_activation_version": 7,
        "inherited_private_journal_version": 6,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "original_native_target_count": len(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "rust_matching_receipt_sha256": rust_owner["sha256"],
        "previous_zig_matching_receipt_sha256":
            previous_zig_owner["sha256"],
        **zero_effects(),
    }
    kept = {
        "build": build,
        "normalized_activation": normalized,
        "normalized_activation_context": normalized_context,
        "normalized_activation_retained": normalized_retained,
        "phase_one": manifest,
        "producer_contract": producer_contract,
        "historical_v31_summary": summary,
        "actual_rust_receipt": rust_receipt,
        "previous_zig_receipt": previous_zig,
    } if retain else {}
    return result, kept


class SourceWall:
    """Physically block every filesystem, activation, process or clock effect."""

    def __init__(self) -> None:
        self.blocked: dict[str, int] = {}
        self.originals: list[tuple[Any, str, Any]] = []

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def deny(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            self.blocked[category] = self.blocked.get(category, 0) + 1
            raise SourceOnlyViolation("source-only gate blocks " + category)

        self.originals.append((owner, name, previous))
        setattr(owner, name, deny)

    def __enter__(self) -> SourceWall:
        for owner, name in (
                (builtins, "open"), (io, "open"), (os, "open"),
                (os, "stat"), (os, "lstat"), (os, "scandir")):
            self.install(owner, name, "filesystem_access")
        for name in ("write", "replace", "link", "unlink", "remove",
                     "mkdir", "rmdir", "fsync", "fchmod", "chmod", "urandom"):
            self.install(os, name, "filesystem_mutations")
        for owner, name, category in (
                (subprocess, "Popen", "candidate_or_compiler_processes"),
                (subprocess, "run", "candidate_or_compiler_processes"),
                (importlib, "import_module", "candidate_imports"),
                (ctypes, "CDLL", "native_library_loads"),
                (tempfile, "mkdtemp", "recovery_roots"),
                (socket, "socket", "network_requests"),
                (threading.Thread, "start", "thread_starts"),
                (locale, "setlocale", "locale_transitions"),
                (signal, "signal", "signal_handlers"),
                (signal, "pthread_sigmask", "signal_masks"),
                (fcntl, "flock", "recovery_locks"),
                (gzip, "open", "archive_files")):
            self.install(owner, name, category)
        for name in (
                "time", "time_ns", "monotonic", "monotonic_ns",
                "perf_counter", "perf_counter_ns", "process_time",
                "process_time_ns", "thread_time", "thread_time_ns"):
            self.install(time, name, "clock_samples")
        return self

    def __exit__(self, kind: Any, value: Any, detail: Any) -> bool:
        del kind, value, detail
        for owner, name, previous in reversed(self.originals):
            setattr(owner, name, previous)
        return False


def expect_rejected(name: str, operation: Any,
                    rejected: list[str]) -> None:
    try:
        operation()
    except (CampaignError, ValueError, TypeError, OverflowError,
            UnicodeError, RecursionError, zlib.error):
        rejected.append(name)
        return
    raise CampaignError("accepted hostile source-only control: " + name)


def synthetic_stream(text: str) -> dict[str, Any]:
    raw = text.encode("ascii")
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": digest(raw),
        "complete": True,
    }


def synthetic_v12_fixture() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = "/tmp/rebar-phase2-zig-scanner-capture-source-build-v2-synthetic-v3"
    processes: list[dict[str, Any]] = []
    phases: list[dict[str, Any]] = []
    for index, name in enumerate(PHASE_NAMES):
        snapshots = {}
        for offset, item in enumerate(SOURCE_OWNERS):
            snapshots[item[0]] = {
                "path": root + "/" + name + "/source/" + item[0],
                "sha256": item[1], "bytes": item[2],
                "device": 2049, "inode": 100_000 + 100 * index + offset,
                "mode": "0600", "link_count": 1,
            }
        native = {}
        for offset, role in enumerate(ROLE_ORDER):
            pin = NATIVE_PINS[role]
            audit = {
                "role": role,
                "external_regex_engine_count": 0,
                "stdlib_regex_engine_count": 0,
                "cross_family_engine_count": 0,
                "native_loader_symbol_count": 0,
                "network_symbol_count": 0,
                "legacy_rpath_count": 0,
                "defined_first_party_symbols":
                    list(ENGINE_EXPORTS) if role == "engine" else [],
                "imported_first_party_symbols":
                    [] if role == "engine" else list(BRIDGE_IMPORTS),
                "needed":
                    ["libc.so.6"] if role == "engine"
                    else ["_zig_probe.so", "libc.so.6"],
                "runpath": None if role == "engine" else "$ORIGIN",
                "soname": "_zig_probe.so" if role == "engine" else None,
            }
            native[role] = {
                "owner": {
                    "path": root + "/" + name + "/native/" + pin["filename"],
                    "sha256": pin["sha256"], "bytes": pin["bytes"],
                    "device": 2049, "inode": 200_000 + 100 * index + offset,
                    "mode": "0700", "link_count": 1,
                },
                "independence_audit": audit,
                "raw_elf64": {
                    "schema": "rebar-phase2-owned-native-source-build-v7-owned-elf64",
                    "file_sha256": pin["sha256"], "file_size": pin["bytes"],
                },
            }
        phases.append({
            "name": name,
            "source_snapshots": snapshots,
            "native_outputs": native,
            "overlay_application": {
                "schema": "rebar-phase2-owned-zig-scanner-capture-source-repair-v2",
                "status": "PASS",
                "phase": name,
                "source_apply_count": 1,
                "candidate_original_modified": False,
                "byte_identical_to_original": True,
                "derived_source_sha256": BRIDGE_SOURCE_SHA256,
                "derived_source_bytes": BRIDGE_SOURCE_BYTES,
                "snapshot_root": root + "/" + name + "/source",
            },
        })
        for offset, role in enumerate(PROCESS_NAMES):
            processes.append({
                "name": role, "phase": name,
                "pid": 400_000 + index * len(PROCESS_NAMES) + offset,
                "returncode": 0, "signal": None,
                "argv": ["/usr/bin/synthetic-source-only-compiler", role],
                "working_directory": root + "/" + name,
                "stdout": synthetic_stream("synthetic-" + name + "-" + role),
                "stderr": synthetic_stream(""),
            })
    comparisons = {}
    roles = {}
    for role in ROLE_ORDER:
        pin = NATIVE_PINS[role]
        comparisons[role] = {
            "byte_identical": True,
            "phase_a_sha256": pin["sha256"],
            "phase_b_sha256": pin["sha256"],
            "phase_a_bytes": pin["bytes"],
            "phase_b_bytes": pin["bytes"],
            "changed_section_count": 0,
            "total_differing_byte_count": 0,
            "difference_spans": [],
            "report_truncated": False,
        }
        roles[role] = {
            "sha256": pin["sha256"], "bytes": pin["bytes"],
            "phase_owner_count": 2, "byte_identical": True,
        }
    report = {
        "schema": "rebar-phase2-owned-zig-scanner-source-build-v12",
        "status": "PASS", "version": 12, "family": FAMILY,
        "label": BUILD_LABEL,
        "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "frozen_case_execution_count": CASE_COUNT,
        "suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "actual_build_process_count": 26,
        "actual_source_apply_count": 2,
        "corrected_bridge_sha256": BRIDGE_SOURCE_SHA256,
        "corrected_bridge_bytes": BRIDGE_SOURCE_BYTES,
        "v1_overlay_used": False,
        "actual_evidence_owner_count_before_publication": 153,
        "actual_authenticated_reference_count_before_publication": 158,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "clock_samples": 0,
        "holdout": "NOT OPENED",
        "private_root": {
            "path": root, "device": 2049, "inode": 90_000, "mode": "0700",
        },
        "processes": processes,
        "build_phases": phases,
        "reproducibility": {
            "status": "PASS",
            "independent_phase_count": 2,
            "byte_identical_native_role_count": 2,
            "compiler_process_count": 26,
            "source_apply_count": 2,
            "roles": roles,
        },
        "raw_elf_differences": {
            "schema": "rebar-phase2-owned-zig-scanner-source-build-v12-all-phase-raw-elf-differences",
            "independent_phase_count": 2,
            "native_role_count": 2,
            "all_native_artifacts_byte_identical": True,
            "additional_compiler_or_inspector_processes": 0,
            "comparison_completed_before_reproducibility_classification": True,
            "roles": comparisons,
        },
    }
    archive_owner = {
        "path": BUILD["archive"][0],
        "sha256": BUILD["archive"][1],
        "bytes": BUILD["archive"][2],
        "device": 2064,
        "inode": 524_663,
        "mode": 0o600,
        "uid": 1000,
        "nlink": 1,
    }
    receipt = {
        "schema":
            "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS",
        "family": FAMILY, "label": BUILD_LABEL,
        "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "uncompressed_sha256": BUILD_PLAIN_SHA256,
        "uncompressed_bytes": BUILD_PLAIN_BYTES,
        "actual_compiler_process_count": 26,
        "actual_source_apply_count": 2,
        "corrected_bridge_sha256": BRIDGE_SOURCE_SHA256,
        "corrected_bridge_bytes": BRIDGE_SOURCE_BYTES,
        "v1_overlay_used": False,
        "actual_evidence_owner_count_before_publication": 153,
        "actual_authenticated_reference_count_before_publication": 158,
        "repository_evidence_owner_count_after_publication": 155,
        "authenticated_history_reference_count_after_publication": 160,
        "candidate_correctness": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "archive": {
            "path": BUILD["archive"][0], "sha256": BUILD["archive"][1],
            "bytes": BUILD["archive"][2],
            "device": archive_owner["device"],
            "inode": archive_owner["inode"],
            "uid": archive_owner["uid"],
            "nlink": archive_owner["nlink"],
            "mode": "0600",
            "exclusive_creation": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "same_inode_readback_verified": True,
        },
    }
    return report, receipt, archive_owner


def source_self_test(source_pin: str, protocol_pin: str,
                     contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "synthetic V3 source")
    checked_digest(protocol_pin, "synthetic V3 protocol")
    checked_digest(contract_pin, "synthetic V3 machine contract")
    source_size = os.stat(str(ROOT / SOURCE_RELATIVE),
                          follow_symlinks=False).st_size
    protocol_size = os.stat(str(ROOT / PROTOCOL_RELATIVE),
                            follow_symlinks=False).st_size
    contract_size = os.stat(str(ROOT / CONTRACT_RELATIVE),
                            follow_symlinks=False).st_size
    read_owned((SOURCE_RELATIVE, source_pin, source_size))
    read_owned((PROTOCOL_RELATIVE, protocol_pin, protocol_size))
    frozen_raw, _ = read_owned((CONTRACT_RELATIVE, contract_pin, contract_size))
    contract = strict_document(frozen_raw, "pinned wholly synthetic V3 contract")
    expected = protocol_document(source_pin, protocol_pin)
    require(canonical(contract) == canonical(expected),
            "authenticate the exact complete contract before the synthetic wall")
    fixture, receipt, archive_owner = synthetic_v12_fixture()
    accepted: list[str] = []
    rejected: list[str] = []
    sandbox = SourceWall()
    with sandbox:
        validate_contract(contract, source_pin, protocol_pin)
        accepted.append("accept-exact-triple-pinned-canonical-contract")
        validate_v12_report(
            fixture, receipt, archive_owner, parser=None, inspect_private=False)
        accepted.append("accept-synthetic-full-26-process-corrected-v12-build")
        accepted.append("accept-13-unchanged-original-suites")
        accepted.append("accept-31237-unchanged-original-case-executions")
        accepted.append("accept-13-named-private-waivers")
        accepted.append("accept-155-real-evidence-owners")
        accepted.append("accept-160-digest-addressed-references")
        accepted.append("accept-corrected-rust-1036-failure")
        accepted.append("accept-actual-previous-zig-2172-failure")
        accepted.append("accept-corrected-canonical-173026-byte-v2-bridge")
        accepted.append("accept-owned-bridge-origin-only-native-dependency")
        accepted.append("accept-v7-descriptor-normalized-journal-policy")
        accepted.append("accept-explicit-idempotent-two-role-inode-recovery")
        accepted.append("accept-additive-50-cases-as-unrun")
        accepted.append("accept-publication-pass-only-as-durable-publication")
        for key, value in (
                ("schema", SCHEMA),
                ("status", "PASS"),
                ("version", 2),
                ("family", "rust"),
                ("campaign_label", "phase2-v11-zig-scanner-original-p0")):
            hostile = copy.deepcopy(contract)
            hostile[key] = value
            expect_rejected(
                "reject-campaign-" + key,
                lambda value=hostile: validate_contract(
                    value, source_pin, protocol_pin), rejected)
        for index, (name, count) in enumerate(SUITES):
            for changed_name, changed_count, suffix in (
                    (name + "-forged", count, "identity"),
                    (name, count + 1, "denominator")):
                hostile = copy.deepcopy(contract)
                hostile["original_oracle"]["source_ordered_suites"][index] = {
                    "id": changed_name, "case_execution_count": changed_count,
                }
                expect_rejected(
                    "reject-original-" + name + "-" + suffix,
                    lambda value=hostile: validate_contract(
                        value, source_pin, protocol_pin), rejected)
        for section, field, value, label in (
                ("original_oracle", "case_execution_denominator", 31_236,
                 "omit-one-original-case"),
                ("original_oracle", "suite_count", 12, "omit-original-suite"),
                ("original_oracle", "named_private_waiver_count", 14,
                 "invent-private-waiver"),
                ("original_oracle", "nested_interpreter_events", 385,
                 "accept-old-failed-interpreter-count"),
                ("original_oracle", "canonical_public_module",
                 "candidates.repaired_zig_candidate", "accept-wrapper-module"),
                ("original_oracle", "external_regex_dependency_allowed",
                 True, "allow-external-regex-package"),
                ("original_oracle", "stdlib_re_fallback_allowed",
                 True, "allow-stdlib-matching-fallback"),
                ("original_oracle", "cross_family_matching_allowed",
                 True, "allow-borrowed-candidate-engine"),
                ("actual_corrected_v12_build", "actual_compiler_process_count",
                 25, "fabricate-build-process-denominator"),
                ("actual_corrected_v12_build", "actual_independent_phase_count",
                 1, "drop-independent-build-phase"),
                ("actual_corrected_v12_build", "actual_corrected_source_apply_count",
                 1, "drop-canonical-v2-bridge-application"),
                ("preserved_v31_history", "repository_evidence_owner_count",
                 155, "present-v31-historical-graph-as-current"),
                ("preserved_v31_history", "actual_c_semantic_mismatch_count",
                 0, "conceal-c-matching-failure"),
                ("preserved_v31_history", "actual_zig_semantic_mismatch_count",
                 0, "conceal-earlier-zig-matching-failure"),
                ("actual_corrected_rust_matching", "semantic_mismatch_count",
                 0, "conceal-real-corrected-rust-failure"),
                ("actual_corrected_rust_matching", "candidate_status",
                 "PASS", "equate-rust-receipt-with-candidate-pass"),
                ("actual_previous_zig_matching", "actual_candidate_workers",
                 0, "conceal-thirteen-real-earlier-zig-workers"),
                ("current_evidence", "actual_evidence_owner_count_before_new_campaign",
                 153, "omit-real-corrected-zig-build-owners"),
                ("current_evidence",
                 "actual_authenticated_reference_count_before_new_campaign",
                 158, "omit-real-corrected-zig-build-references"),
                ("additive_callable_introspection", "reference_status",
                 "PASS", "invent-additive-baseline"),
                ("additive_callable_introspection", "included_in_original_denominator",
                 True, "silently-change-original-denominator"),
                ("normalized_recovery", "group_atomic",
                 True, "falsely-claim-two-file-group-atomicity"),
                ("normalized_recovery", "sigkill_automatically_recovered",
                 True, "invent-automatic-sigkill-recovery"),
                ("normalized_recovery", "power_failure_automatically_recovered",
                 True, "invent-automatic-power-failure-recovery"),
                ("future_complete_campaign", "status", "PASS",
                 "invent-corrected-zig-matching-pass"),
                ("future_complete_campaign", "actual_candidate_workers", 13,
                 "invent-unrun-candidate-processes"),
                ("future_complete_campaign", "publication_pass_means",
                 "CANDIDATE PASSED", "equate-publication-with-correctness"),
        ):
            hostile = copy.deepcopy(contract)
            hostile[section][field] = value
            expect_rejected(
                "reject-" + label,
                lambda value=hostile: validate_contract(
                    value, source_pin, protocol_pin), rejected)
        for role in ROLE_ORDER:
            for field, wrong in (
                    ("inode", 999_999),
                    ("device", 999_999),
                    ("mode", 0o777),
                    ("nlink", 2),
                    ("uid", 0),
                    ("sha256", "0" * 64)):
                hostile = copy.deepcopy(contract)
                selected = next(
                    row for row in
                    hostile["normalized_recovery"]["original_native_owners"]
                    if row["role"] == role)
                selected["original"][field] = wrong
                expect_rejected(
                    "reject-" + role + "-original-" + field,
                    lambda value=hostile: validate_contract(
                        value, source_pin, protocol_pin), rejected)
        for key, wrong, label in (
                ("status", "FAIL", "failed-build"),
                ("label", "phase2-v11-zig-scanner", "old-v11-build-label"),
                ("actual_build_process_count", 25, "missing-actual-build-process"),
                ("actual_source_apply_count", 1, "missing-canonical-bridge-apply"),
                ("corrected_bridge_sha256",
                 "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148",
                 "obsolete-v1-conditional-bridge"),
                ("corrected_bridge_bytes", 173_082,
                 "obsolete-v1-conditional-bridge-size"),
                ("v1_overlay_used", True, "allow-v1-scanner-overlay"),
                ("candidate_correctness", "PASS",
                 "equate-successful-build-with-matching"),
                ("candidate_imports", 1, "allow-build-candidate-import"),
                ("holdout", "OPENED", "allow-final-holdout"),
                ("actual_evidence_owner_count_before_publication", 151,
                 "forge-corrected-build-prepublication-count")):
            hostile = copy.deepcopy(fixture)
            hostile[key] = wrong
            expect_rejected(
                "reject-" + label,
                lambda value=hostile: validate_v12_report(
                    value, receipt, archive_owner,
                    parser=None, inspect_private=False), rejected)
        for index, role in enumerate(PROCESS_NAMES):
            for field, wrong, tag in (
                    ("name", "borrowed-" + role, "name"),
                    ("returncode", 1, "failure"),
                    ("pid", 0, "fake-pid"),
                    ("phase", "reference-b", "cross-phase")):
                hostile = copy.deepcopy(fixture)
                hostile["processes"][index][field] = wrong
                expect_rejected(
                    "reject-process-" + role + "-" + tag,
                    lambda value=hostile: validate_v12_report(
                        value, receipt, archive_owner,
                        parser=None, inspect_private=False), rejected)
        for phase_index, phase_name in enumerate(PHASE_NAMES):
            for role in ROLE_ORDER:
                for field, wrong, tag in (
                        ("sha256", "0" * 64, "native-digest"),
                        ("mode", "0777", "native-mode"),
                        ("link_count", 2, "native-hardlink")):
                    hostile = copy.deepcopy(fixture)
                    hostile["build_phases"][phase_index]["native_outputs"][role][
                        "owner"][field] = wrong
                    expect_rejected(
                        "reject-" + phase_name + "-" + role + "-" + tag,
                        lambda value=hostile: validate_v12_report(
                            value, receipt, archive_owner,
                            parser=None, inspect_private=False), rejected)
            hostile = copy.deepcopy(fixture)
            hostile["build_phases"][phase_index]["overlay_application"][
                "derived_source_bytes"] = 173_082
            expect_rejected(
                "reject-" + phase_name + "-v1-overlay",
                lambda value=hostile: validate_v12_report(
                    value, receipt, archive_owner,
                    parser=None, inspect_private=False), rejected)
        for role in ROLE_ORDER:
            for field, wrong in (
                    ("external_regex_engine_count", 1),
                    ("stdlib_regex_engine_count", 1),
                    ("cross_family_engine_count", 1),
                    ("native_loader_symbol_count", 1),
                    ("network_symbol_count", 1)):
                hostile = copy.deepcopy(fixture)
                hostile["build_phases"][0]["native_outputs"][role][
                    "independence_audit"][field] = wrong
                expect_rejected(
                    "reject-" + role + "-" + field,
                    lambda value=hostile: validate_v12_report(
                        value, receipt, archive_owner,
                        parser=None, inspect_private=False), rejected)
        for field, wrong, label in (
                ("status", "FAIL", "failed-publication"),
                ("build_status", "FAIL", "failed-build-receipt"),
                ("uncompressed_sha256", "0" * 64, "fabricated-build-bytes"),
                ("uncompressed_bytes", BUILD_PLAIN_BYTES + 1,
                 "wrong-expanded-build-size"),
                ("repository_evidence_owner_count_after_publication", 153,
                 "conceal-real-build-owners"),
                ("authenticated_history_reference_count_after_publication", 158,
                 "conceal-real-build-references")):
            hostile = copy.deepcopy(receipt)
            hostile[field] = wrong
            expect_rejected(
                "reject-" + label,
                lambda value=hostile: validate_v12_report(
                    fixture, value, archive_owner,
                    parser=None, inspect_private=False), rejected)
        for owner, name, category in (
                (builtins, "open", "filesystem"),
                (os, "open", "filesystem-descriptor"),
                (os, "stat", "native-target-stat"),
                (os, "write", "native-target-write"),
                (os, "replace", "native-target-replacement"),
                (os, "link", "native-target-hardlink"),
                (os, "fsync", "durable-journal-creation"),
                (subprocess, "Popen", "candidate-worker"),
                (subprocess, "run", "compiler-process"),
                (importlib, "import_module", "candidate-import"),
                (ctypes, "CDLL", "native-library-load"),
                (tempfile, "mkdtemp", "private-recovery-root"),
                (socket, "socket", "network"),
                (threading.Thread, "start", "thread"),
                (locale, "setlocale", "locale"),
                (signal, "signal", "signal-handler"),
                (signal, "pthread_sigmask", "signal-mask"),
                (fcntl, "flock", "recovery-lock"),
                (gzip, "open", "matching-archive"),
                (time, "time", "wall-clock"),
                (time, "perf_counter", "benchmark-clock")):
            if hasattr(owner, name):
                expect_rejected(
                    "block-actual-" + category,
                    lambda target=owner, attribute=name:
                        getattr(target, attribute)(),
                    rejected)
    require(len(accepted) >= 15 and len(rejected) >= 120
            and len(set(rejected)) == len(rejected)
            and sandbox.blocked
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "require genuine hostile controls and physically blocked effects")
    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "status": "PASS", "version": 3,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "blocked_effect_category_count": len(sandbox.blocked),
        "blocked_effect_attempt_count": sum(sandbox.blocked.values()),
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "actual_evidence_owner_count": ACTUAL_EVIDENCE_OWNER_COUNT,
        "actual_authenticated_reference_count":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "actual_corrected_rust_semantic_mismatch_count": 1_036,
        "actual_c_semantic_mismatch_count": 1_230,
        "historical_zig_semantic_mismatch_count": 2_172,
        "actual_corrected_v12_compiler_process_count": 26,
        "canonical_corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "additive_callable_introspection_case_count": 50,
        "additive_callable_reference_status": "NOT RUN",
        "actual_corrected_build_archive_files_opened": 0,
        "actual_corrected_build_archive_compressed_bytes_read": 0,
        "actual_corrected_build_archive_uncompressed_bytes_read": 0,
        "matching_failure_archives_opened": 0,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actual_source_builds": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "canonical_target_replacements": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "workspace_mutations": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


@contextlib.contextmanager
def blocked_controller_signals() -> Iterator[None]:
    require(callable(getattr(signal, "pthread_sigmask", None)),
            "require exact actual POSIX signal masking")
    mask = {
        getattr(signal, name) for name in SIGNAL_NAMES
        if hasattr(signal, name)
    }
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, mask)
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


@contextlib.contextmanager
def installed_signal_handlers() -> Iterator[None]:
    previous: list[tuple[int, Any]] = []

    def handle(signum: int, _frame: Any) -> None:
        raise GracefulControllerSignal(signum)

    try:
        for name in SIGNAL_NAMES:
            if hasattr(signal, name):
                number = getattr(signal, name)
                previous.append((number, signal.getsignal(number)))
                signal.signal(number, handle)
        yield
    finally:
        for number, handler in reversed(previous):
            signal.signal(number, handler)


def checked_public_root(value: Any) -> str:
    require(type(value) is str and value == PUBLIC_RECOVERY_ROOT
            and value.startswith("/tmp/" + RECOVERY_PRIVATE_PREFIX)
            and len(PurePosixPath(value).parts) == 3
            and "\\" not in value and "\x00" not in value,
            "authorize only the exact public owner-only Zig V3 recovery root")
    return value


def open_recovery_lock(*, create: bool) -> tuple[int, int]:
    root = checked_public_root(PUBLIC_RECOVERY_ROOT)
    if create:
        try:
            os.mkdir(root, 0o700)
        except FileExistsError:
            pass
    directory = os.open(root, os.O_RDONLY | os.O_CLOEXEC
                        | os.O_DIRECTORY | os.O_NOFOLLOW)
    lock: int | None = None
    try:
        first = os.fstat(directory)
        require(stat.S_ISDIR(first.st_mode)
                and stat.S_IMODE(first.st_mode) == 0o700
                and first.st_uid == os.geteuid(),
                "reject a foreign or publicly writable exact recovery root")
        flags = os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW
        if create:
            flags |= os.O_CREAT
        lock = os.open(LOCK_NAME, flags, 0o600, dir_fd=directory)
        owner = os.fstat(lock)
        require(stat.S_ISREG(owner.st_mode)
                and stat.S_IMODE(owner.st_mode) == 0o600
                and owner.st_uid == os.geteuid() and owner.st_nlink == 1,
                "require one independently owned actual recovery lock")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise CampaignError("another exact Zig recovery controller owns the lock") from error
        return directory, lock
    except BaseException:
        if lock is not None:
            os.close(lock)
        os.close(directory)
        raise


def patched_activation(
    retained: Mapping[str, Any],
    *, announce: bool = False,
) -> tuple[types.ModuleType, types.ModuleType, types.ModuleType, dict[str, Any]]:
    normalized = retained["normalized_activation"]
    historic_context = retained["normalized_activation_context"]
    original = retained["normalized_activation_retained"]
    v6 = original["v6"]
    inherited = original["inherited"]
    mature = inherited["mature"]
    build = retained["build"]
    require(type(normalized) is types.ModuleType
            and type(v6) is types.ModuleType
            and type(mature) is types.ModuleType
            and normalized.SCHEMA == "rebar-phase2-verified-native-activation-v7"
            and v6.SCHEMA == "rebar-phase2-verified-native-activation-v6"
            and tuple(v6.ROLE_ORDER) == ROLE_ORDER
            and tuple(v6.RESTORATION_ORDER) == RESTORATION_ORDER
            and callable(mature.read_owned)
            and callable(mature.write_fresh)
            and callable(mature.synchronize_directory),
            "reuse only the immutable authenticated V7-normalized V6 journal")
    phase_roles = {
        phase["name"]: {
            role: copy.deepcopy(phase["native"][role]["owner"])
            for role in ROLE_ORDER
        }
        for phase in build["phases"]
    }
    cached = {
        "mature": mature,
        "zig": {
            "report": build["report"],
            "phase_roles": phase_roles,
        },
    }

    def exact_v6_context(
        source_pin: str, protocol_pin: str,
        contract_pin: str | None = None,
        *, retain: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        require(source_pin == ACTIVATION_V6["source"][1]
                and protocol_pin == ACTIVATION_V6["protocol"][1]
                and contract_pin == ACTIVATION_V6["contract"][1],
                "independently pin the immutable actual V6 journal source")
        historic = original["v6_context"]
        require(type(historic) is dict and historic.get("status") == "PASS",
                "retain previously authenticated immutable V6 source context")
        return historic, (cached if retain else {})

    def exact_v7_context(
        source_pin: str, protocol_pin: str,
        contract_pin: str | None = None,
        *, retain: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        require(source_pin == ACTIVATION_V7["source"][1]
                and protocol_pin == ACTIVATION_V7["protocol"][1]
                and contract_pin == ACTIVATION_V7["contract"][1],
                "independently pin the immutable actual V7 normalizer")
        require(historic_context.get("status") == "PASS",
                "reuse only the actually verified V7 context")
        return historic_context, (
            {"v6": v6, "v6_context": original["v6_context"],
             "inherited": cached}
            if retain else {}
        )

    v6.BUILD_LABEL = BUILD_LABEL
    v6.PRIVATE_PREFIX = RECOVERY_PRIVATE_PREFIX
    v6.V11_ARCHIVE = BUILD["archive"][0]
    v6.V11_RECEIPT = BUILD["receipt"][0]
    v6.SUPPORT_OWNERS = dict(v6.SUPPORT_OWNERS)
    v6.SUPPORT_OWNERS[BUILD["archive"][0]] = (
        BUILD["archive"][1], BUILD["archive"][2])
    v6.SUPPORT_OWNERS[BUILD["receipt"][0]] = (
        BUILD["receipt"][1], BUILD["receipt"][2])
    v6.DERIVED_BRIDGE_SHA256 = BRIDGE_SOURCE_SHA256
    v6.DERIVED_BRIDGE_BYTES = BRIDGE_SOURCE_BYTES
    v6.NATIVE_ROLES = copy.deepcopy(v6.NATIVE_ROLES)
    for role in ROLE_ORDER:
        v6.NATIVE_ROLES[role]["sha256"] = NATIVE_PINS[role]["sha256"]
        v6.NATIVE_ROLES[role]["bytes"] = NATIVE_PINS[role]["bytes"]
        require(v6.NATIVE_ROLES[role]["original"] == ORIGINAL_NATIVE[role],
                "never change the original genuine Zig target identity")
    v6.authenticate_context = exact_v6_context
    normalized.BUILD_LABEL = BUILD_LABEL
    normalized.BUILD_ARCHIVE = BUILD["archive"]
    normalized.BUILD_RECEIPT = BUILD["receipt"]
    normalized.ENGINE_SHA256 = ENGINE_SHA256
    normalized.ENGINE_BYTES = ENGINE_BYTES
    normalized.BRIDGE_SHA256 = BRIDGE_SHA256
    normalized.BRIDGE_BYTES = BRIDGE_BYTES
    normalized.verify_context = exact_v7_context
    announcement: dict[str, Any] = {}
    if announce:
        previous_control = v6.private_control

        def announce_control(
            selected_mature: types.ModuleType, root: str,
            filename: str, document: dict[str, Any],
        ) -> dict[str, Any]:
            owner = previous_control(selected_mature, root, filename, document)
            if filename == "recovery-journal.json":
                require(checked_public_root(root) == PUBLIC_RECOVERY_ROOT
                        and document.get("schema") == v6.JOURNAL_SCHEMA
                        and document.get("build_label") == BUILD_LABEL
                        and document.get("build_archive_sha256") == BUILD["archive"][1]
                        and document.get("build_receipt_sha256") == BUILD["receipt"][1]
                        and document.get("role_order") == list(ROLE_ORDER)
                        and document.get("restoration_order") == list(RESTORATION_ORDER),
                        "publish only the exact corrected pre-activation recovery journal")
                synchronized = mature.synchronize_directory(root)
                require(synchronized.get("completed") is True,
                        "fsync the exact public journal before target replacement")
                announcement.update({
                    "root": root,
                    "journal": copy.deepcopy(document),
                    "journal_owner": copy.deepcopy(owner),
                })
                sys.stderr.write(
                    "REPAIRED ZIG ORIGINAL CAMPAIGN V3 RECOVERY JOURNAL: "
                    + root + "/recovery-journal.json SHA256 "
                    + owner["sha256"] + "\n"
                )
                sys.stderr.flush()
            return owner

        v6.private_control = announce_control
    return normalized, v6, mature, announcement


def activation_arguments() -> list[str]:
    return [
        "--activate",
        "--source-sha256", ACTIVATION_V7["source"][1],
        "--protocol-sha256", ACTIVATION_V7["protocol"][1],
        "--contract-sha256", ACTIVATION_V7["contract"][1],
        "--predecessor-source-sha256", ACTIVATION_V6["source"][1],
        "--predecessor-protocol-sha256", ACTIVATION_V6["protocol"][1],
        "--predecessor-contract-sha256", ACTIVATION_V6["contract"][1],
        "--family", FAMILY,
        "--build-label", BUILD_LABEL,
        "--build-archive-sha256", BUILD["archive"][1],
        "--build-receipt-sha256", BUILD["receipt"][1],
        "--native-engine-sha256", ENGINE_SHA256,
        "--native-bridge-sha256", BRIDGE_SHA256,
        "--native-engine-bytes", str(ENGINE_BYTES),
        "--native-bridge-bytes", str(BRIDGE_BYTES),
    ]


def recovery_arguments(root: str, journal: str) -> list[str]:
    checked_public_root(root)
    checked_digest(journal, "exact actual Zig recovery journal")
    return [
        "--recover",
        "--source-sha256", ACTIVATION_V7["source"][1],
        "--protocol-sha256", ACTIVATION_V7["protocol"][1],
        "--contract-sha256", ACTIVATION_V7["contract"][1],
        "--predecessor-source-sha256", ACTIVATION_V6["source"][1],
        "--predecessor-protocol-sha256", ACTIVATION_V6["protocol"][1],
        "--predecessor-contract-sha256", ACTIVATION_V6["contract"][1],
        "--family", FAMILY,
        "--activation-root", root,
        "--recovery-journal-sha256", journal,
    ]


def exact_originals(
    v6: types.ModuleType, mature: types.ModuleType,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        _, actual = v6.exact_current_original(mature, role)
        expected = ORIGINAL_NATIVE[role]
        require(type(actual) is dict
                and actual.get("relative") == expected["relative"]
                and actual.get("sha256") == expected["sha256"]
                and actual.get("size_bytes") == expected["bytes"]
                and actual.get("device") == expected["device"]
                and actual.get("inode") == expected["inode"]
                and actual.get("mode") == expected["mode"]
                and actual.get("uid") == expected["uid"]
                and actual.get("nlink") == expected["nlink"],
                "restore the exact original Zig native inode: " + role)
        result[role] = actual
    return result


def activate_corrected(
    normalized: types.ModuleType,
    root: str,
) -> dict[str, Any]:
    checked_public_root(root)
    original_mkdtemp = tempfile.mkdtemp

    def fixed_public_root(*args: Any, **kwargs: Any) -> str:
        require(not args
                and kwargs.get("dir") == "/tmp"
                and kwargs.get("prefix") == RECOVERY_PRIVATE_PREFIX,
                "create only the previously locked public recovery root")
        directory = os.open(root, os.O_RDONLY | os.O_CLOEXEC
                            | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            observed = os.fstat(directory)
            require(stat.S_ISDIR(observed.st_mode)
                    and stat.S_IMODE(observed.st_mode) == 0o700
                    and observed.st_uid == os.geteuid(),
                    "retain the exact locked public recovery root")
        finally:
            os.close(directory)
        return root

    tempfile.mkdtemp = fixed_public_root
    try:
        active = normalized.activate(
            normalized.parse_arguments(activation_arguments()))
    finally:
        tempfile.mkdtemp = original_mkdtemp
    require(type(active) is dict
            and active.get("schema")
            == normalized.SCHEMA + "-normalized-activation-result"
            and active.get("status") == "PASS"
            and active.get("version") == 7
            and active.get("family") == FAMILY
            and active.get("activation_root") == root
            and active.get("immutable_v6_predecessor_source_sha256")
            == ACTIVATION_V6["source"][1]
            and active.get("group_atomic") is False
            and active.get("original_inodes_preserved_in_adjacent_backups")
            is True
            and type(active.get("roles")) is dict
            and set(active["roles"]) == set(ROLE_ORDER),
            "activate only the two actual V12 roles through verified V7")
    for role in ROLE_ORDER:
        entry = active["roles"][role]
        require(type(entry) is dict
                and entry.get("relative") == NATIVE_PINS[role]["relative"]
                and entry.get("sha256") == NATIVE_PINS[role]["sha256"]
                and entry.get("size_bytes") == NATIVE_PINS[role]["bytes"],
                "reject a crossed active corrected native " + role)
    return active


def same_owner(expected: Any, actual: Mapping[str, Any]) -> bool:
    return (type(expected) is dict
            and expected.get("sha256") == actual.get("sha256")
            and expected.get("device") == actual.get("device")
            and expected.get("inode") == actual.get("inode")
            and expected.get("size_bytes") == actual.get("size_bytes"))


def active_worker_approval(
    v6: types.ModuleType, mature: types.ModuleType,
    options: argparse.Namespace,
) -> dict[str, Any]:
    root = checked_public_root(options.activation_root)
    rows = {}
    for filename, pin, key in (
            ("activation-report.json", options.activation_report_sha256, "report"),
            ("activation-receipt.json", options.activation_receipt_sha256, "receipt"),
            ("recovery-journal.json", options.recovery_journal_sha256, "journal")):
        checked_digest(pin, "actual private " + filename)
        raw, owner = mature.read_owned(
            root, filename, pin, maximum=v6.MAX_REPORT_BYTES, private=True)
        rows[key] = v6.strict_json(raw, filename)
        rows[key + "_owner"] = owner
    report = rows["report"]
    receipt = rows["receipt"]
    journal = rows["journal"]
    require(report.get("schema") == v6.REPORT_SCHEMA
            and report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("activation_root") == root
            and report.get("build_label") == BUILD_LABEL
            and report.get("build_archive_sha256") == BUILD["archive"][1]
            and report.get("build_receipt_sha256") == BUILD["receipt"][1]
            and report.get("group_atomic") is False
            and report.get("exact_original_inode_backups_retained") is True
            and same_owner(report.get("recovery_journal"), rows["journal_owner"])
            and receipt.get("schema") == v6.RECEIPT_SCHEMA
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("activation_root") == root
            and same_owner(receipt.get("activation_report"), rows["report_owner"])
            and same_owner(receipt.get("recovery_journal"), rows["journal_owner"])
            and journal.get("schema") == v6.JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("family") == FAMILY
            and journal.get("activation_root") == root
            and journal.get("build_label") == BUILD_LABEL
            and journal.get("build_archive_sha256") == BUILD["archive"][1]
            and journal.get("build_receipt_sha256") == BUILD["receipt"][1]
            and journal.get("role_order") == list(ROLE_ORDER)
            and journal.get("restoration_order") == list(RESTORATION_ORDER)
            and journal.get("group_atomic") is False,
            "reject a stale or unannounced actual V12 two-role journal")
    for role in ROLE_ORDER:
        definition = v6.NATIVE_ROLES[role]
        entry = journal.get("roles", {}).get(role)
        selected = report.get("canonical_targets", {}).get(role)
        require(type(entry) is dict
                and entry.get("relative") == definition["relative"]
                and entry.get("original") == definition["original"]
                and entry.get("native_sha256") == definition["sha256"]
                and entry.get("native_bytes") == definition["bytes"]
                and type(selected) is dict
                and selected.get("relative") == definition["relative"]
                and selected.get("sha256") == definition["sha256"]
                and selected.get("size_bytes") == definition["bytes"],
                "authenticate the complete actual corrected role: " + role)
    return {"root": root, **rows}


def stream_observation(value: Any) -> dict[str, Any]:
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True,
                               separators=(",", ":"), allow_nan=False)
    destination = io.BytesIO()
    plain_hash = hashlib.sha256()
    plain_size = 0
    with gzip.GzipFile(fileobj=destination, mode="wb", compresslevel=9,
                       mtime=0) as stream:
        for text in encoder.iterencode(value):
            raw = text.encode("ascii")
            plain_size += len(raw)
            require(plain_size <= MAX_SUITE_PLAIN_BYTES,
                    "bound complete actual original Zig observations")
            plain_hash.update(raw)
            stream.write(raw)
            require(destination.tell() <= MAX_SUITE_COMPRESSED_BYTES,
                    "bound losslessly compressed original Zig observations")
        plain_hash.update(b"\n")
        plain_size += 1
        require(plain_size <= MAX_SUITE_PLAIN_BYTES,
                "retain the exact terminal observation newline")
        stream.write(b"\n")
    compressed = destination.getvalue()
    require(0 < len(compressed) <= MAX_SUITE_COMPRESSED_BYTES,
            "bound the complete actual original suite gzip")
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
            "preserve the complete bounded compressed original worker")
    checked_digest(value.get("compressed_sha256"), "actual suite gzip")
    checked_digest(value.get("uncompressed_sha256"), "actual suite records")
    try:
        compressed = base64.b64decode(value["compressed_base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise CampaignError("reject hidden compressed original matching records") from error
    require(len(compressed) == value["compressed_bytes"]
            and digest(compressed) == value["compressed_sha256"]
            and compressed[:3] == b"\x1f\x8b\x08"
            and compressed[4:8] == b"\x00\x00\x00\x00",
            "authenticate every actual zero-time compressed worker byte")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    hasher = hashlib.sha256()
    cursor = 0
    total = 0
    try:
        while cursor < len(compressed):
            piece = compressed[cursor:cursor + 65_536]
            cursor += len(piece)
            pending = piece
            while pending:
                block = decoder.decompress(pending, 1024 * 1024)
                total += len(block)
                require(total <= MAX_SUITE_PLAIN_BYTES,
                        "reject an oversized actual original suite observation")
                hasher.update(block)
                pending = decoder.unconsumed_tail
                require(not decoder.unused_data,
                        "reject multiple original suite gzip members")
        tail = decoder.flush()
        total += len(tail)
        require(total <= MAX_SUITE_PLAIN_BYTES and decoder.eof,
                "reject truncated actual original records")
        hasher.update(tail)
    except (zlib.error, EOFError, OSError) as error:
        raise CampaignError("reject damaged original Zig worker records") from error
    require(total == value["uncompressed_bytes"]
            and hasher.hexdigest() == value["uncompressed_sha256"],
            "reauthenticate every unchanged original matching record")
    return value


def assert_actual_authorization(options: argparse.Namespace) -> None:
    require(options.family == FAMILY and options.label == LABEL
            and options.producer_source_sha256 == PRODUCER["source"][1]
            and options.producer_protocol_sha256 == PRODUCER["protocol"][1]
            and options.producer_contract_sha256 == PRODUCER["contract"][1]
            and options.normalized_activation_source_sha256
            == ACTIVATION_V7["source"][1]
            and options.normalized_activation_protocol_sha256
            == ACTIVATION_V7["protocol"][1]
            and options.normalized_activation_contract_sha256
            == ACTIVATION_V7["contract"][1]
            and options.activation_source_sha256 == ACTIVATION_V6["source"][1]
            and options.activation_protocol_sha256 == ACTIVATION_V6["protocol"][1]
            and options.activation_contract_sha256 == ACTIVATION_V6["contract"][1]
            and options.publication_source_sha256 == PUBLICATION["source"][1]
            and options.publication_protocol_sha256 == PUBLICATION["protocol"][1]
            and options.publication_contract_sha256 == PUBLICATION["contract"][1]
            and options.build_source_sha256 == BUILD["source"][1]
            and options.build_protocol_sha256 == BUILD["protocol"][1]
            and options.build_contract_sha256 == BUILD["contract"][1]
            and options.build_archive_sha256 == BUILD["archive"][1]
            and options.build_receipt_sha256 == BUILD["receipt"][1]
            and options.native_engine_sha256 == ENGINE_SHA256
            and options.native_bridge_sha256 == BRIDGE_SHA256
            and options.native_engine_bytes == ENGINE_BYTES
            and options.native_bridge_bytes == BRIDGE_BYTES,
            "independently caller-pin each actual V12, original worker and V7 owner")


def run_worker(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    context, retained = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "authenticate all original suites before one actual worker")
    _, v6, mature, _ = patched_activation(retained)
    active = active_worker_approval(v6, mature, options)
    producer = load_frozen(
        PRODUCER["source"], "_rebar_owned_zig_v3_exact_original_producer")
    require(producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v3"
            and producer.SUITE_COUNT == SUITE_COUNT
            and producer.CASE_DENOMINATOR == CASE_COUNT
            and producer.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
            and [(row.name, row.case_count) for row in producer.SUITES]
            == list(SUITES),
            "reuse only the actual immutable complete original P0 observer")
    spec = producer.family_spec(FAMILY)
    require(spec.module == "candidates.zig_candidate"
            and spec.bridge_module == "candidates._zig_bridge"
            and tuple(spec.source_owners) == SOURCE_OWNERS
            and spec.owned_ctypes is True
            and spec.combined_native is False,
            "import only the genuine first-party original Zig public module")
    suite = producer.suite_spec(options.suite)
    sources = {path: fingerprint for path, fingerprint, _ in SOURCE_OWNERS}
    pins = {
        "source": SOURCE_OWNERS[0][1],
        "native_engine": ENGINE_SHA256,
        "native_bridge": BRIDGE_SHA256,
    }
    exact = producer.exact_native_owners(spec, pins, sources)
    require(exact["source"]["sha256"] == SOURCE_OWNERS[0][1]
            and exact["native_engine"]["sha256"] == ENGINE_SHA256
            and exact["native_bridge"]["sha256"] == BRIDGE_SHA256,
            "match only through the actual corrected built first-party Zig engine")
    if suite.name == "original_bounded_v5":
        observed = producer.observe_original_upstream(
            suite, spec, pins, sources)
    elif suite.name == "subinterpreter_v2":
        observed = producer.observe_subinterpreters(
            suite, spec, pins, sources,
            producer_sha256=PRODUCER["source"][1])
    else:
        observed = producer.observe_direct_suite(
            suite, spec, pins, sources, retained["phase_one"])
    require(type(observed) is dict
            and observed.get("schema") == producer.SCHEMA + "-actual-original-suite"
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
            "retain every genuine immutable original case and matching failure")
    if suite.name == "original_bounded_v5":
        require(observed.get("actual_public_record_count") == 152
                and observed.get("actual_debug_skip_count") == 1
                and observed.get("named_private_waiver_count") == 13
                and type(observed.get("named_private_waivers")) is list
                and len(observed["named_private_waivers"]) == 13,
                "never suppress a public method or invent a private waiver")
    if suite.name == "subinterpreter_v2" and observed["status"] == "PASS":
        require(observed.get("actual_case_interpreter_exec_calls") == 394
                and observed.get("actual_interpreters_created") == 11
                and observed.get("actual_interpreters_destroyed") == 11
                and observed.get("all_real_pipes_read_to_eof") is True
                and observed.get("all_real_pipe_descriptors_closed") is True
                and observed.get("interpreter_live_set_restored") is True,
                "retain every actual original subinterpreter lifecycle")
    encoded = stream_observation(observed)
    return {
        "schema": WORKER_SCHEMA, "status": observed["status"],
        "candidate_family": FAMILY, "label": LABEL,
        "suite": suite.name,
        "case_execution_denominator": suite.case_count,
        "actual_candidate_case_count": suite.case_count,
        "mismatch_count": observed["mismatch_count"],
        "failure_class":
            "PASS" if observed["status"] == "PASS" else "SEMANTIC MISMATCH",
        "original_observer_source_sha256": PRODUCER["source"][1],
        "original_observer_unchanged": True,
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "actual_v7_normalized_activation_source_sha256":
            ACTIVATION_V7["source"][1],
        "actual_v6_activation_source_sha256": ACTIVATION_V6["source"][1],
        "activation_report_sha256": active["report_owner"]["sha256"],
        "activation_receipt_sha256": active["receipt_owner"]["sha256"],
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "canonical_corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "owned_zig_source_count": len(SOURCE_OWNERS),
        "complete_original_observation": encoded,
        "all_original_records_and_mismatches_preserved": True,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def worker_arguments(options: argparse.Namespace, name: str,
                     active: Mapping[str, Any]) -> list[str]:
    return [
        PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE), "--worker",
        "--source-sha256", options.source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--contract-sha256", options.contract_sha256,
        "--family", FAMILY, "--label", LABEL, "--suite", name,
        "--activation-root", active["activation_root"],
        "--activation-report-sha256", active["report"]["sha256"],
        "--activation-receipt-sha256", active["receipt"]["sha256"],
        "--recovery-journal-sha256", active["recovery_journal"]["sha256"],
        "--normalized-activation-source-sha256", ACTIVATION_V7["source"][1],
        "--normalized-activation-protocol-sha256", ACTIVATION_V7["protocol"][1],
        "--normalized-activation-contract-sha256", ACTIVATION_V7["contract"][1],
        "--activation-source-sha256", ACTIVATION_V6["source"][1],
        "--activation-protocol-sha256", ACTIVATION_V6["protocol"][1],
        "--activation-contract-sha256", ACTIVATION_V6["contract"][1],
        "--producer-source-sha256", PRODUCER["source"][1],
        "--producer-protocol-sha256", PRODUCER["protocol"][1],
        "--producer-contract-sha256", PRODUCER["contract"][1],
        "--publication-source-sha256", PUBLICATION["source"][1],
        "--publication-protocol-sha256", PUBLICATION["protocol"][1],
        "--publication-contract-sha256", PUBLICATION["contract"][1],
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


def encoded_process(raw: bytes, limit: int, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= limit,
            "retain all actual original " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "sha256": digest(raw), "size_bytes": len(raw), "complete": True,
    }


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
            "preserve complete bounded actual corrected Zig worker output")
    process = {
        "argv": argv, "pid": child.pid,
        "returncode": child.returncode, "timed_out": timed_out,
        "stdout": encoded_process(
            stdout, MAX_WORKER_STDOUT_BYTES, "suite stdout"),
        "stderr": encoded_process(
            stderr, MAX_WORKER_STDERR_BYTES, "suite stderr"),
        "actual_worker_processes": 1,
    }
    observed: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    try:
        observed = strict_document(stdout, "actual original corrected Zig worker")
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
                and observed.get("actual_v7_normalized_activation_source_sha256")
                == ACTIVATION_V7["source"][1]
                and observed.get("canonical_corrected_bridge_source_sha256")
                == BRIDGE_SOURCE_SHA256
                and observed.get("native_engine_sha256") == ENGINE_SHA256
                and observed.get("native_bridge_sha256") == BRIDGE_SHA256
                and observed.get("owned_zig_source_count") == len(SOURCE_OWNERS)
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
                "reject a missing, stale, forged, timed-out or foreign worker")
        validate_streamed_observation(
            observed.get("complete_original_observation"))
    except (CampaignError, ValueError, TypeError, zlib.error) as error:
        failure = {
            "error_type": type(error).__qualname__,
            "error_message": str(error)[:4096],
        }
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


def evidence_names(failed: bool) -> tuple[str, str]:
    require(type(failed) is bool, "select one exact actual campaign outcome")
    base = "repaired-zig-original-campaign-v3-zig-" + LABEL
    if failed:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


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
                    "never overwrite an actual original Zig outcome: " + name)
    finally:
        os.close(directory)


def bounded_public_report(value: Mapping[str, Any]) -> int:
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True,
                               separators=(",", ":"), allow_nan=False)
    total = 1
    for part in encoder.iterencode(value):
        total += len(part.encode("ascii"))
        require(total <= MAX_PUBLIC_REPORT_BYTES,
                "bound all actual complete original campaign evidence")
    return total


def preserve_campaign(
    report: dict[str, Any], publication: types.ModuleType,
    v6: types.ModuleType, mature: types.ModuleType,
) -> dict[str, Any]:
    require(report.get("schema") == CAMPAIGN_SCHEMA
            and report.get("status") in ("PASS", "FAIL")
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("suite_count") == SUITE_COUNT
            and report.get("case_execution_denominator") == CASE_COUNT
            and report.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and type(report.get("suite_results")) is list
            and len(report["suite_results"]) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in report["suite_results"]]
            == list(SUITES)
            and report.get("historical_evidence_owner_count_before_publication")
            == ACTUAL_EVIDENCE_OWNER_COUNT
            and report.get("historical_authenticated_reference_count_before_publication")
            == ACTUAL_AUTHENTICATED_REFERENCE_COUNT
            and report.get("all_original_native_targets_restored") is True
            and report.get("restoration_verified_before_publication") is True
            and report.get("holdout") == "NOT OPENED"
            and report.get("clock_samples") == 0,
            "never publish invented cases or unrestored original native inodes")
    size = bounded_public_report(report)
    originals = exact_originals(v6, mature)
    require(report.get("restored_original_targets") == originals,
            "verify both exact user-owned original inodes before publication")
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
            "retain one complete exclusively published deterministic outcome")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": report["status"],
        "family": FAMILY,
        "label": LABEL,
        "archive": archive,
        "campaign_source_sha256": report["campaign_source_sha256"],
        "campaign_protocol_sha256": report["campaign_protocol_sha256"],
        "campaign_contract_sha256": report["campaign_contract_sha256"],
        "original_v3_producer_source_sha256": PRODUCER["source"][1],
        "original_v3_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v3_producer_contract_sha256": PRODUCER["contract"][1],
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "canonical_corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
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
        "actual_corrected_rust_semantic_mismatch_count": 1_036,
        "actual_c_semantic_mismatch_count": 1_230,
        "historical_zig_semantic_mismatch_count": 2_172,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_original_native_targets_restored": True,
        "restored_original_targets": originals,
        "restoration_verified_before_publication": True,
        "v7_normalized_activation_source_sha256": ACTIVATION_V7["source"][1],
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
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
    evidence_root = str(ROOT / EVIDENCE_RELATIVE)
    receipt_owner = mature.write_fresh(
        evidence_root, receipt_name, canonical(receipt))
    synced = mature.synchronize_directory(evidence_root)
    require(receipt_owner.get("relative") == receipt_name
            and receipt_owner.get("mode") == 0o600
            and receipt_owner.get("exclusive_creation") is True
            and receipt_owner.get("same_inode_readback_verified") is True
            and receipt_owner.get("file_fsync_completed") is True
            and synced.get("completed") is True
            and (archive["device"], archive["inode"])
            != (receipt_owner["device"], receipt_owner["inode"])
            and exact_originals(v6, mature) == originals,
            "publish exactly two distinct durable owners after exact recovery")
    return {
        "schema": RESULT_SCHEMA,
        "status": report["status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": FAMILY,
        "label": LABEL,
        "archive": archive,
        "receipt": receipt_owner,
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
        "resulting_repository_evidence_owner_count":
            ACTUAL_EVIDENCE_OWNER_COUNT + 2,
        "resulting_authenticated_reference_count":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT + 2,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_original_native_targets_restored": True,
        "restored_original_targets": originals,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def record_failure(error: BaseException) -> dict[str, Any]:
    return {
        "error_type": type(error).__qualname__,
        "error_message": str(error)[:4096],
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__),
    }


def run_campaign(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    context, retained = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "verify all real build and original evidence before any mutation")
    publication = load_frozen(
        PUBLICATION["source"], "_rebar_owned_zig_v3_lossless_publication")
    require(publication.SCHEMA == "rebar-owned-six-family-original-p0-campaign-v2"
            and callable(publication.open_evidence_directory)
            and callable(publication.write_streamed_archive),
            "reuse only exact unchanged first-party streaming publication")
    ensure_fresh_evidence(publication)
    normalized, v6, mature, announced = patched_activation(
        retained, announce=True)
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
                directory, lock = open_recovery_lock(create=True)
                baseline = exact_originals(v6, mature)
                for item in SOURCE_OWNERS:
                    read_owned(item)
                active = activate_corrected(
                    normalized, PUBLIC_RECOVERY_ROOT)
                require(announced.get("root") == PUBLIC_RECOVERY_ROOT
                        and type(announced.get("journal_owner")) is dict
                        and same_owner(active["recovery_journal"],
                                       announced["journal_owner"]),
                        "announce the durable recovery journal before activation")
            for name, count in SUITES:
                try:
                    rows.append(execute_one_worker(options, name, count, active))
                except GracefulControllerSignal:
                    raise
                except Exception as error:
                    rows.append(failed_worker(name, count, error))
        except GracefulControllerSignal as error:
            controller_failure = record_failure(error)
            graceful = {
                "schema": SIGNAL_SCHEMA,
                "status": "FAIL",
                "signal_name": error.signal_name,
                "signal_number": error.signum,
                "candidate_matching_result": "NOT MEASURED",
                "group_atomic": False,
            }
        except Exception as error:
            controller_failure = record_failure(error)
        finally:
            try:
                if announced.get("journal_owner") is not None:
                    journal_digest = announced["journal_owner"]["sha256"]
                    with blocked_controller_signals():
                        existing: dict[str, Any] | None = None
                        try:
                            raw, _ = mature.read_owned(
                                PUBLIC_RECOVERY_ROOT,
                                "restoration-receipt.json", None,
                                maximum=v6.MAX_REPORT_BYTES, private=True)
                            existing = v6.strict_json(
                                raw, "existing genuine exact Zig restoration")
                        except FileNotFoundError:
                            existing = None
                        if existing is None:
                            restored = normalized.recover(
                                normalized.parse_arguments(
                                    recovery_arguments(
                                        PUBLIC_RECOVERY_ROOT, journal_digest)))
                            require(type(restored) is dict
                                    and restored.get("schema")
                                    == normalized.SCHEMA
                                    + "-normalized-recovery-result"
                                    and restored.get("status") == "PASS"
                                    and restored.get("original_inode_preserved")
                                    is True
                                    and restored.get("group_atomic") is False,
                                    "restore both exact original Zig inodes")
                            restoration = restored
                        else:
                            require(existing.get("schema")
                                    == v6.RESTORATION_SCHEMA
                                    and existing.get("status") == "PASS"
                                    and existing.get("recovery_journal_sha256")
                                    == journal_digest
                                    and existing.get("restoration_order")
                                    == list(RESTORATION_ORDER)
                                    and existing.get("original_inode_preserved")
                                    is True,
                                    "reject forged prior exact-inode recovery")
                            restoration = existing
                if baseline is not None:
                    with blocked_controller_signals():
                        require(exact_originals(v6, mature) == baseline,
                                "restore both exact genuine Zig original inodes")
                        for item in SOURCE_OWNERS:
                            read_owned(item)
            finally:
                if lock is not None:
                    os.close(lock)
                if directory is not None:
                    os.close(directory)
    existing_names = {row.get("suite") for row in rows}
    if controller_failure is not None:
        error = CampaignError(controller_failure["error_message"])
        for name, count in SUITES:
            if name not in existing_names:
                rows.append(failed_worker(name, count, error))
    positions = {name: offset for offset, (name, _) in enumerate(SUITES)}
    rows.sort(key=lambda row: positions[row["suite"]])
    require(len(rows) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in rows] == list(SUITES),
            "preserve all original groups, failures and denominator")
    require(baseline is not None and active is not None
            and restoration is not None
            and type(announced.get("journal_owner")) is dict,
            "never publish a candidate campaign without actual journaled recovery")
    originals = exact_originals(v6, mature)
    require(originals == baseline,
            "verify exact actual original inodes immediately before publication")
    pids = [
        row["process"]["pid"] for row in rows
        if row.get("actual_worker_started") is True
        and type(row.get("process")) is dict
    ]
    require(len(pids) == len(set(pids)),
            "never count an original candidate worker process twice")
    completed = sum(row.get("actual_worker_started") is True for row in rows)
    passed = sum(
        count for (name, count), row in zip(SUITES, rows, strict=True)
        if row.get("suite") == name
        and row.get("failure_class") == "PASS"
        and row.get("mismatch_count") == 0
        and row.get("all_original_records_and_mismatches_preserved") is True
    )
    mismatches = sum(
        row["mismatch_count"] for row in rows
        if row.get("failure_class") == "SEMANTIC MISMATCH"
        and type(row.get("mismatch_count")) is int
    )
    infrastructure = sum(
        row.get("failure_class") == "INFRASTRUCTURE FAILURE"
        for row in rows
    ) + int(controller_failure is not None)
    qualified = (
        completed == SUITE_COUNT and len(pids) == SUITE_COUNT
        and passed == CASE_COUNT and mismatches == 0
        and infrastructure == 0 and graceful is None
        and all(row.get("actual_worker_processes") == 1
                and row.get("all_original_records_and_mismatches_preserved") is True
                for row in rows)
    )
    report = {
        "schema": CAMPAIGN_SCHEMA,
        "status": "PASS" if qualified else "FAIL",
        "family": FAMILY,
        "label": LABEL,
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
        "actual_v12_compiler_process_count": 26,
        "actual_v12_source_apply_count": 2,
        "canonical_corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "canonical_corrected_bridge_source_bytes": BRIDGE_SOURCE_BYTES,
        "native_engine_sha256": ENGINE_SHA256,
        "native_engine_bytes": ENGINE_BYTES,
        "native_bridge_sha256": BRIDGE_SHA256,
        "native_bridge_bytes": BRIDGE_BYTES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "completed_suite_count": completed,
        "suite_results": rows,
        "actual_candidate_workers": len(pids),
        "actual_worker_process_ids": pids,
        "verified_passing_case_count": passed,
        "semantic_mismatch_count":
            mismatches if completed == SUITE_COUNT else "NOT MEASURED",
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": qualified,
        "historical_evidence_owner_count_before_publication":
            ACTUAL_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count_before_publication":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "actual_corrected_rust_semantic_mismatch_count": 1_036,
        "actual_corrected_rust_verified_passing_case_count": 8_965,
        "historical_rust_semantic_mismatch_count": 1_087,
        "actual_c_semantic_mismatch_count": 1_230,
        "historical_zig_semantic_mismatch_count": 2_172,
        "historical_zig_verified_passing_case_count": 2_847,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": announced["journal_owner"]["sha256"],
        "recovery_journal_announced_before_replacement": True,
        "actual_v7_normalized_activation_source_sha256":
            ACTIVATION_V7["source"][1],
        "graceful_signal": graceful,
        "all_original_native_targets_restored": True,
        "restored_original_targets": originals,
        "restoration": restoration,
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "controller_failure": controller_failure,
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
    return preserve_campaign(report, publication, v6, mature)


def recover_originals(options: argparse.Namespace) -> dict[str, Any]:
    require(options.activation_root == PUBLIC_RECOVERY_ROOT
            and options.recovery_journal_sha256 is not None,
            "independently pin the exact public root and actual recovery journal")
    context, retained = verify_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256, retain=True)
    require(context.get("status") == "PASS",
            "reauthenticate the full immutable source freeze before recovery")
    normalized, v6, mature, _ = patched_activation(retained)
    directory: int | None = None
    lock: int | None = None
    try:
        with blocked_controller_signals():
            directory, lock = open_recovery_lock(create=False)
            recovered = normalized.recover(
                normalized.parse_arguments(recovery_arguments(
                    PUBLIC_RECOVERY_ROOT,
                    options.recovery_journal_sha256)))
            require(type(recovered) is dict
                    and recovered.get("schema")
                    == normalized.SCHEMA + "-normalized-recovery-result"
                    and recovered.get("status") == "PASS"
                    and recovered.get("activation_root") == PUBLIC_RECOVERY_ROOT
                    and recovered.get("recovery_journal_sha256")
                    == options.recovery_journal_sha256
                    and recovered.get("original_inode_preserved") is True
                    and recovered.get("group_atomic") is False,
                    "refuse unsafe, unjournaled or incomplete public recovery")
            originals = exact_originals(v6, mature)
            for item in SOURCE_OWNERS:
                read_owned(item)
    finally:
        if lock is not None:
            os.close(lock)
        if directory is not None:
            os.close(directory)
    return {
        "schema": RECOVERY_SCHEMA,
        "status": "PASS",
        "family": FAMILY,
        "label": LABEL,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": options.recovery_journal_sha256,
        "actual_v12_build_archive_sha256": BUILD["archive"][1],
        "actual_v12_build_receipt_sha256": BUILD["receipt"][1],
        "actual_v7_normalized_activation_source_sha256":
            ACTIVATION_V7["source"][1],
        "all_original_native_targets_restored": True,
        "restored_original_targets": originals,
        "restoration": recovered,
        "candidate_workers_started": 0,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }


def worker_failure(options: argparse.Namespace,
                   error: BaseException) -> dict[str, Any]:
    return {
        "schema": WORKER_SCHEMA,
        "status": "FAIL",
        "candidate_family": FAMILY,
        "label": LABEL,
        "suite": options.suite,
        "case_execution_denominator": dict(SUITES).get(options.suite),
        "actual_candidate_case_count": "NOT MEASURED",
        "failure_class": "INFRASTRUCTURE FAILURE",
        "mismatch_count": "NOT MEASURED",
        "error_type": type(error).__qualname__,
        "error_message": str(error)[:4096],
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__),
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def parse_arguments(
    arguments: Sequence[str] | None = None,
) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    require(all(type(row) is str for row in values),
            "require one exact bounded original Zig campaign command")
    names = [row for row in values if row.startswith("--")]
    require(len(names) == len(set(names)),
            "reject shadowed or repeated actual matching authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--worker", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--recover", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--suite", choices=tuple(name for name, _ in SUITES))
    parser.add_argument("--activation-root")
    for name in (
            "activation-report", "activation-receipt", "recovery-journal",
            "normalized-activation-source", "normalized-activation-protocol",
            "normalized-activation-contract",
            "activation-source", "activation-protocol", "activation-contract",
            "producer-source", "producer-protocol", "producer-contract",
            "publication-source", "publication-protocol", "publication-contract",
            "build-source", "build-protocol", "build-contract",
            "build-archive", "build-receipt", "native-engine", "native-bridge"):
        parser.add_argument("--" + name + "-sha256")
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "campaign source")
    checked_digest(options.protocol_sha256, "campaign protocol")
    for name in (
            "contract_sha256", "activation_report_sha256",
            "activation_receipt_sha256", "recovery_journal_sha256",
            "normalized_activation_source_sha256",
            "normalized_activation_protocol_sha256",
            "normalized_activation_contract_sha256",
            "activation_source_sha256", "activation_protocol_sha256",
            "activation_contract_sha256", "producer_source_sha256",
            "producer_protocol_sha256", "producer_contract_sha256",
            "publication_source_sha256", "publication_protocol_sha256",
            "publication_contract_sha256", "build_source_sha256",
            "build_protocol_sha256", "build_contract_sha256",
            "build_archive_sha256", "build_receipt_sha256",
            "native_engine_sha256", "native_bridge_sha256"):
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    actual = (
        "family", "label", "suite", "activation_root",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256",
        "normalized_activation_source_sha256",
        "normalized_activation_protocol_sha256",
        "normalized_activation_contract_sha256",
        "activation_source_sha256", "activation_protocol_sha256",
        "activation_contract_sha256",
        "producer_source_sha256", "producer_protocol_sha256",
        "producer_contract_sha256",
        "publication_source_sha256", "publication_protocol_sha256",
        "publication_contract_sha256",
        "build_source_sha256", "build_protocol_sha256",
        "build_contract_sha256", "build_archive_sha256",
        "build_receipt_sha256", "native_engine_sha256",
        "native_bridge_sha256", "native_engine_bytes", "native_bridge_bytes",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, name) is None for name in actual),
                "read-only contract rendering cannot authorize actual matching")
        return options
    require(options.contract_sha256 is not None,
            "independently pin all three exact campaign source owners")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in actual),
                "a source-only gate cannot activate, match or recover")
        return options
    if options.recover:
        require(options.family == FAMILY and options.label == LABEL
                and options.activation_root == PUBLIC_RECOVERY_ROOT
                and options.recovery_journal_sha256 is not None
                and options.suite is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None,
                "recover only the exact independently pinned public journal")
        return options
    assert_actual_authorization(options)
    if options.worker:
        require(options.suite is not None
                and options.activation_root == PUBLIC_RECOVERY_ROOT
                and all(getattr(options, name) is not None for name in (
                    "activation_report_sha256", "activation_receipt_sha256",
                    "recovery_journal_sha256")),
                "bind one genuine worker to the exact prepublished live journal")
    else:
        require(options.suite is None
                and options.activation_root is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None
                and options.recovery_journal_sha256 is None,
                "only the controller may create one locked recovery root")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = source_self_test(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256)
        elif options.verify_frozen_context:
            result, _ = verify_context(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256)
        elif options.render_contract:
            verify_context(options.source_sha256,
                           options.protocol_sha256, None)
            result = protocol_document(
                options.source_sha256, options.protocol_sha256)
        elif options.worker:
            try:
                result = run_worker(options)
            except Exception as error:
                result = worker_failure(options, error)
            sys.stdout.buffer.write(canonical(result))
            sys.stdout.buffer.flush()
            return 0 if result["status"] == "PASS" else 1
        elif options.recover:
            result = recover_originals(options)
        else:
            result = run_campaign(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        if options.run:
            return 0 if result["status"] == "PASS" else 1
        return 0
    except Exception as error:
        sys.stderr.write(
            "REPAIRED ORIGINAL ZIG CAMPAIGN V3: FAIL: "
            + type(error).__name__ + ": " + str(error) + "\n"
        )
        sys.stderr.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
