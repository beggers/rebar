#!/usr/bin/env python3
"""Freeze the independent, first-party Zig original-P0 worker without running it.

This worker cannot authorize matching until its coordinator publishes the exact
V45 current history, publication-safe Rust V7, and a separately verified live
Zig activation. Source verification never opens an archive, imports a candidate,
starts a process, builds, loads native code, or inspects a performance holdout.
"""

from __future__ import annotations

import _ctypes
import _imp
import _io
import _posixsubprocess
import _socket
import _thread
import argparse
import ast
import base64
import builtins
import contextlib
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
import zlib
from typing import Any, Iterator, Mapping, NamedTuple, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_zig_original_p0_candidate_worker_v1.py"
RUNNER_RELATIVE = "tools/run_frozen_zig_original_p0_candidate_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/ZIG-ORIGINAL-P0-CANDIDATE-PROTOCOL-V1.md"
DOCUMENT_RELATIVE = "oracle/phase2/zig-original-p0-candidate-protocol-v1.json"
SCHEMA = "rebar-frozen-zig-original-p0-candidate-worker-v1"
RUNNER_SCHEMA = "rebar-frozen-zig-original-p0-candidate-v1"
CONTRACT_SCHEMA = "rebar-frozen-zig-original-p0-candidate-protocol-v1"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
FAMILY = "zig"
FAMILY_NAMES = ("rust", "c", "zig", "cpp", "go", "fortran")
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
SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
PRIVATE_WAIVER_COUNT = 13
SOURCE_FAMILY_COUNT = 6
SOURCE_OWNER_COUNT = 25
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PUBLIC_REPORT_BYTES = 32 * 1024 * 1024
MAX_CHILD_STDOUT_BYTES = 1024 * 1024
MAX_CHILD_STDERR_BYTES = 2 * 1024 * 1024
MAX_ERROR_BYTES = 64 * 1024
WORKER_TIMEOUT_SECONDS = 3_600


class Owner(NamedTuple):
    path: str
    sha256: str
    size_bytes: int


GOAL = Owner(
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
PHASE_ONE = Owner(
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45_632,
)
ORIGINAL_PRODUCER = {
    "source": Owner(
        "tools/run_owned_six_family_original_p0_producer_v4.py",
        "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        230_782,
    ),
    "protocol": Owner(
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md",
        "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
        5_981,
    ),
    "document": Owner(
        "oracle/phase2/six-family-p0-producer-v4.json",
        "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
        30_867,
    ),
}
CORRECTED_REFERENCE = {
    "source": Owner(
        "tools/verify_owned_public_type_reference_context_v1.py",
        "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc",
        102_474,
    ),
    "protocol": Owner(
        "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md",
        "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018",
        10_691,
    ),
    "document": Owner(
        "oracle/phase1/p0-public-type-reference-context-v1.json",
        "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b",
        13_965,
    ),
    "receipt": Owner(
        "oracle/phase1/evidence/"
        "public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-"
        "publication-receipt.json",
        "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966",
        2_509,
    ),
    "falsification": Owner(
        "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json",
        "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670",
        3_892,
    ),
}
ZIG_SOURCES = {
    "adapter": Owner(
        "candidates/zig_candidate.py",
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        68_422,
    ),
    "engine": Owner(
        "candidates/zig/mini_regex.zig",
        "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
        186_915,
    ),
    "bridge": Owner(
        "candidates/zig/py_bridge.c",
        "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
        173_026,
    ),
}
OFFICIAL_ZIG_LOCK = Owner(
    "toolchains/zig-0.16.0.lock.json",
    "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
    628,
)
HISTORICAL_V12_BUILD = {
    "source": Owner(
        "tools/reproduce_owned_zig_scanner_source_build_v12.py",
        "5192fa35dd0b13cb3bdddfc8f24c37d7e797d0b8463d000c4692c8131f33d1b6",
        124_781,
    ),
    "protocol": Owner(
        "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V12.md",
        "f80743d8109402e5876792b6713237b1ab770e3286874dd5ae47fb56381131b1",
        6_531,
    ),
    "document": Owner(
        "oracle/phase2/zig-scanner-source-build-v12.json",
        "5abb6f60c7a9672e32d6f2980a109ccb15b7ef56e5cc3a81abda458109552c1a",
        23_611,
    ),
    "receipt": Owner(
        "oracle/phase2/evidence/"
        "native-source-build-v12-zig-phase2-v12-zig-scanner-v2-"
        "publication-receipt.json",
        "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b",
        2_029,
    ),
}
HISTORICAL_ZIG_CAMPAIGN = {
    "source": Owner(
        "tools/run_owned_repaired_zig_original_campaign_v3.py",
        "e4efad7dfbe921bec9f7160cd33dbbed0376b1373037a78de8bcaabdcd2ece98",
        178_576,
    ),
    "protocol": Owner(
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V3.md",
        "0463e23aaed9de6e1b50db7f106a1f175b504eefdbf868fa1f03ed5b313776d1",
        8_448,
    ),
    "document": Owner(
        "oracle/phase2/repaired-zig-original-campaign-v3.json",
        "4d20518685e2db7b80c9a1936f4ae480cff85c2a3b672562f6d4fded20b8328d",
        16_316,
    ),
    "receipt": Owner(
        "oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-"
        "original-p0-failures-publication-receipt.json",
        "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96",
        4_111,
    ),
}
SCANNER_REPAIR = {
    "source": Owner(
        "tools/apply_owned_zig_scanner_phrase_source_repair_v3.py",
        "9b5cf55b9d66729b84b91470f8ba5906208ccee09312b43c329acaab2ff34010",
        84_556,
    ),
    "protocol": Owner(
        "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V3.md",
        "78fccd7fffd33e5ecd9a9033d8225c294d82ee07f391eb46ccd621a08e0d38e1",
        6_205,
    ),
    "document": Owner(
        "oracle/phase2/zig-scanner-phrase-source-repair-v3.json",
        "4eee672b4fe6f25f7481c34a34928f00d34a45a9e0675e024238a8ee5576fade",
        11_117,
    ),
}
V41_OWNERS = {
    "source": Owner(
        "tools/render_candidate_current_overview_v41.py",
        "c0ab9b19acd895a122a171ca1d9df9010de0ec732b81b0f52f29b96cbc88f87a",
        50_242,
    ),
    "inputs": Owner(
        "docs/evidence/candidate-current-overview-v41.inputs.json",
        "3abaa207a8d25f03c59bd9f7443dcd0bfb5fd6934c7f1fa388e2abf636893fc4",
        235_674,
    ),
    "summary": Owner(
        "docs/evidence/candidate-current-overview-v41.json",
        "e2835917d55d654a6d4c167298737c51f5f3b299ab7e2bc2c2eba60f9bff4f9f",
        675_118,
    ),
    "svg": Owner(
        "docs/evidence/candidate-current-overview-v41.svg",
        "882e8ddb4e233a1c569c0330bbbf618f65f54bcf3d0bb59dc1c99542677dd2b7",
        12_401,
    ),
}

# The coordinator released these exact owners only after V42 was committed and
# pushed at 2a85610e32681bf43820e0aabd2590a2385df9b5. Rust V6 is source-only.
V42_PINS_RELEASED = True
V42_OWNERS: dict[str, Owner] = {
    "source": Owner(
        "tools/render_candidate_current_overview_v42.py",
        "8e4783f7c61340ce8f291f84e2dfa802189a66353edd7a89026934d9863d1ce2",
        51_652,
    ),
    "inputs": Owner(
        "docs/evidence/candidate-current-overview-v42.inputs.json",
        "ca11b1d4d7e7cd483a8ebf81fe12f36037a22608cf8ab459ce9d97d16f86dda2",
        271_354,
    ),
    "summary": Owner(
        "docs/evidence/candidate-current-overview-v42.json",
        "30b7ba546209796f950ea6720a19acb16972bf8d984841f74d45c00d4c639838",
        787_504,
    ),
    "svg": Owner(
        "docs/evidence/candidate-current-overview-v42.svg",
        "3d1f05706861d662f3113dc7340ceb09731c66b137df99637819a3e8b4cbd781",
        12_837,
    ),
}
RUST_V6_PINS_RELEASED = True
RUST_V6_OWNERS: dict[str, Owner] = {
    "source": Owner(
        "tools/run_owned_repaired_rust_original_campaign_v6.py",
        "c25cbdf3674fc3e054c388e53de3ed38d4b1dab0a820808c42848e1803909f5e",
        374_429,
    ),
    "protocol": Owner(
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V6.md",
        "ddc5c212d3e188bc1d1cdde992bf872a38962e64d3b07d6ec7c275ba4f55f13c",
        8_551,
    ),
    "document": Owner(
        "oracle/phase2/repaired-rust-original-campaign-v6.json",
        "ce044f18be388ab0608d0bd3bb68751e6970973f8e6ef758971e75e6d6b584a5",
        33_386,
    ),
}
V43_OWNERS: dict[str, Owner] = {
    "source": Owner(
        "tools/render_candidate_current_overview_v43.py",
        "3b3647a2090fd98e89ea421b2d2a3018983e1014adecf9f0b30731b54ca51e8b",
        67_805,
    ),
    "inputs": Owner(
        "docs/evidence/candidate-current-overview-v43.inputs.json",
        "394fb27e12b9a48fbd8bdd353930084891c09118e0cfa49fc90f596124e15017",
        281_096,
    ),
    "summary": Owner(
        "docs/evidence/candidate-current-overview-v43.json",
        "1c5ea146e6d40f0e81f2fe274f2a1a50fe01efdd074ca7ea5b36cca420d16bf0",
        817_337,
    ),
    "svg": Owner(
        "docs/evidence/candidate-current-overview-v43.svg",
        "bee43e78aa59a806927a50e1e807181c62a3f6497d75add1834de2c75fdc546b",
        13_359,
    ),
}
V45_PINS_RELEASED = True
V45_OWNERS: dict[str, Owner] = {
    "source": Owner(
        "tools/render_candidate_current_overview_v45.py",
        "07a7e1b6c96434e66e852e0eb784326816d340edb338d2e89de4f1d6918bb586",
        68_616,
    ),
    "inputs": Owner(
        "docs/evidence/candidate-current-overview-v45.inputs.json",
        "cbc1b861fe59067e64adf396493630360f6bf616fe1f51598220aabafadea4a5",
        352_881,
    ),
    "summary": Owner(
        "docs/evidence/candidate-current-overview-v45.json",
        "1086a7bd72116b590d00f5216835534ec745265a0f249d3cd5eb05a3701ff840",
        1_013_003,
    ),
    "svg": Owner(
        "docs/evidence/candidate-current-overview-v45.svg",
        "1c9d56fd4b8480bab9cedc2e95b6449a414cb68a02ee447963454db5b4242b2b",
        15_948,
    ),
}
RUST_V7_PINS_RELEASED = True
RUST_V7_OWNERS: dict[str, Owner] = {
    "source": Owner(
        "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        505_616,
    ),
    "protocol": Owner(
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md",
        "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840",
        8_433,
    ),
    "document": Owner(
        "oracle/phase2/repaired-rust-original-campaign-v7.json",
        "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5",
        46_385,
    ),
}
PUBLIC_ENTRYPOINT_OWNERS: dict[str, Owner] = {
    "source": Owner(
        "tools/verify_public_entrypoint_import_v1.py",
        "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4",
        83_957,
    ),
    "protocol": Owner(
        "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md",
        "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0",
        7_991,
    ),
    "document": Owner(
        "oracle/phase1/p0-public-entrypoint-import-v1.json",
        "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47",
        9_823,
    ),
}
PUBLIC_ENTRYPOINT_SURFACE = {
    "entrypoint": Owner(
        "rebar.py",
        "289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f",
        212,
    ),
    "project": Owner(
        "pyproject.toml",
        "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
        224,
    ),
}
ACTUAL_RUST_V6_FAILURE = {
    "failure": Owner(
        "oracle/phase2/evidence/"
        "repaired-rust-original-campaign-v6-rust-phase2-v13-rust-pattern-repr-"
        "original-p0-entry-failure.json",
        "88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7",
        3_175,
    ),
    "observation": Owner(
        "oracle/phase2/evidence/"
        "repaired-rust-original-campaign-v6-rust-phase2-v13-rust-pattern-repr-"
        "original-p0-entry-failure-observation.json",
        "51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6",
        3_061,
    ),
}
# A past source build and a past restored target are not a live activation.
VERIFIED_ZIG_ACTIVATION_RELEASED = False
VERIFIED_ZIG_ACTIVATION_OWNERS: dict[str, Owner] = {}

CORRECTED_PUBLIC_RECORDS_SHA256 = (
    "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
)
HISTORICAL_PUBLIC_RECORDS_SHA256 = (
    "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
)
CORRECTED_PUBLIC_COHORT_RECORDS_SHA256 = (
    "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
)
CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256 = (
    "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
)
CORRECTED_PUBLIC_MATRIX_SHA256 = (
    "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
)
CORRECTED_PUBLIC_REFERENCE_PIDS = (81, 82)
CORRECTED_PUBLIC_CASES_PER_REFERENCE = 6_912
CORRECTED_PUBLIC_COHORT_CASE_COUNT = 96
ZIG_COMPILER_SHA256 = (
    "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
)
ZIG_COMPILER_ABSOLUTE_PATH = "/tmp/zig-x86_64-linux-0.16.0/zig"
ZIG_COMPILER_BYTES = 172_641_672
PUBLIC_ENTRYPOINT_MATRIX_SHA256 = (
    "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
)
ZIG_V12_BUILD_ARCHIVE_SHA256 = (
    "3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d"
)
HISTORICAL_ZIG_CAMPAIGN_ARCHIVE_SHA256 = (
    "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b"
)
HISTORICAL_ZIG_V3_PRODUCER_SOURCE_SHA256 = (
    "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c"
)
HISTORICAL_ZIG_V3_PRODUCER_PROTOCOL_SHA256 = (
    "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76"
)
HISTORICAL_ZIG_V3_PRODUCER_CONTRACT_SHA256 = (
    "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1"
)
DERIVED_SCANNER_ADAPTER_SHA256 = (
    "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b"
)
ORIGINAL_SCANNER_BLOCK = (
    b"        if not branches:\n"
    b'            raise RuntimeError("invalid SRE code")\n'
    b"        group_count = len(branches)\n"
)
CORRECTED_SCANNER_BLOCK = (
    b"        group_count = len(branches)\n"
    b"        if not group_count or any(\n"
    b"            local_groups > group_count\n"
    b"            for _body, local_groups in branches\n"
    b"        ):\n"
    b'            raise RuntimeError("invalid SRE code")\n'
)


class CandidateGateError(Exception):
    """Reject substituted evidence, incomplete cases, and premature matching."""


class SourceOnlyEffect(CandidateGateError):
    """A source-only operation attempted a physically prohibited effect."""


def require(value: Any, message: str) -> None:
    if value is not True:
        raise CandidateGateError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash only exact original bytes")
    return hashlib.sha256(value).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require a complete lowercase SHA-256 for " + label,
    )
    return value


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise CandidateGateError("reject invalid or noncanonical evidence") from error


def bounded_error(error: BaseException) -> str:
    raw = str(error).encode("utf-8", "backslashreplace")
    if len(raw) > MAX_ERROR_BYTES:
        raw = raw[:MAX_ERROR_BYTES] + b" [error summary truncated]"
    return raw.decode("utf-8", "replace")


def bounded_public_report(value: Any, maximum: int = MAX_PUBLIC_REPORT_BYTES) -> bytes:
    require(type(maximum) is int and maximum > 0, "require a positive report bound")
    raw = canonical(value)
    require(len(raw) <= maximum, "never truncate an oversized public report")
    return raw


def exact_json(
    raw: bytes, label: str, *, canonical_required: bool = True
) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        answer: dict[str, Any] = {}
        for key, value in items:
            require(type(key) is str and key not in answer, "reject duplicate JSON keys in " + label)
            answer[key] = value
        return answer

    def nonfinite(value: str) -> Any:
        raise CandidateGateError("reject nonfinite JSON in " + label)

    try:
        document = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise CandidateGateError("reject malformed JSON in " + label) from error
    require(type(document) is dict, "require a complete JSON object in " + label)
    require(
        canonical_required is False or canonical(document) == raw,
        "require complete canonical JSON in " + label,
    )
    return document


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and "\\" not in value and "\x00" not in value,
            "require a safe owner-relative path")
    parts = value.split("/")
    require(all(part not in ("", ".", "..") for part in parts),
            "reject absolute, traversing, or ambiguous owner paths")
    lowered = value.casefold()
    require(
        not lowered.endswith((".gz", ".xz", ".bz2", ".zip", ".tar", ".so"))
        and "holdout" not in lowered
        and not lowered.startswith(("performance/", "benchmarks/", "benchmark/")),
        "source-only Zig verification never opens archives, native outputs, holdouts, or benchmarks",
    )
    return value


def owner_record(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size_bytes}


def relative_owner_record(owner: Owner) -> dict[str, Any]:
    return {"relative": owner.path, "sha256": owner.sha256, "size_bytes": owner.size_bytes}


def read_owner(owner: Owner, *, maximum: int = MAX_SOURCE_BYTES, private: bool = False) -> tuple[bytes, dict[str, Any]]:
    require(type(owner) is Owner, "require an exact independently frozen owner")
    relative = checked_relative(owner.path)
    checked_digest(owner.sha256, relative)
    require(type(owner.size_bytes) is int and 0 < owner.size_bytes <= maximum,
            "require an exact bounded source owner size")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    descriptors: list[int] = []
    try:
        directory = os.open(str(ROOT), directory_flags)
        descriptors.append(directory)
        pieces = relative.split("/")
        for piece in pieces[:-1]:
            directory = os.open(piece, directory_flags, dir_fd=directory)
            descriptors.append(directory)
        descriptor = os.open(pieces[-1], flags, dir_fd=directory)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(pieces[-1], dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and (before.st_dev, before.st_ino, before.st_size)
            == (visible.st_dev, visible.st_ino, visible.st_size)
            and before.st_size == owner.size_bytes,
            "reject a missing, linked, substituted, or resized source owner: " + relative,
        )
        if private:
            require(stat.S_IMODE(before.st_mode) == 0o600,
                    "require an actually owner-private publication receipt: " + relative)
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(part) is bytes and bool(part), "reject truncated source owner: " + relative)
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "reject concealed trailing owner bytes: " + relative)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and digest(raw) == owner.sha256,
            "reject source owner changes during verification: " + relative,
        )
        return raw, owner_record(owner)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def authenticate_official_zig_compiler() -> dict[str, Any]:
    """Stream-authenticate the exact compiler; never execute or load it."""
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(ZIG_COMPILER_ABSOLUTE_PATH, flags)
        before = os.fstat(descriptor)
        visible = os.stat(ZIG_COMPILER_ABSOLUTE_PATH, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and (before.st_dev, before.st_ino, before.st_size)
            == (visible.st_dev, visible.st_ino, visible.st_size)
            and before.st_size == ZIG_COMPILER_BYTES,
            "reject a missing, linked, substituted, or resized official Zig compiler",
        )
        hashed = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk),
                    "reject a truncated pinned official Zig compiler")
            hashed.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject concealed bytes in the official Zig compiler")
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and hashed.hexdigest() == ZIG_COMPILER_SHA256,
            "reject a changed exact official stable Zig compiler",
        )
        return {
            "path": ZIG_COMPILER_ABSOLUTE_PATH,
            "sha256": ZIG_COMPILER_SHA256,
            "bytes": ZIG_COMPILER_BYTES,
            "compiler_executed": False,
            "native_library_loaded": False,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)


def runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "run only the exact worker under isolated pinned CPython 3.14.6",
    )


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    names = (
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "source_builds", "native_activations",
        "native_promotions", "native_libraries_loaded", "interpreter_creations",
        "threads_started", "network_requests", "clock_samples",
        "hidden_cases_read", "benchmark_files_read", "blocked_reads",
        "blocked_writes", "blocked_processes", "blocked_imports",
        "blocked_low_level_imports", "blocked_native_loads",
        "blocked_decompression", "blocked_threads", "blocked_network",
        "blocked_clocks", "blocked_signals", "blocked_locks",
    )
    effects = dict.fromkeys(names, 0)
    originals: list[tuple[Any, str, Any]] = []

    def block(owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def forbidden(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyEffect("the first-party Zig source boundary forbids " + name)

        originals.append((owner, name, original))
        setattr(owner, name, forbidden)

    try:
        for owner, name in (
            (builtins, "open"), (_io, "open"), (io, "open"),
            (os, "open"), (os, "read"), (os, "stat"), (os, "lstat"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
        ):
            block(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "mkdir"), (os, "makedirs"), (os, "replace"),
            (os, "rename"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"), (Path, "touch"),
            (Path, "unlink"), (Path, "mkdir"),
            (tempfile, "mkstemp"), (tempfile, "mkdtemp"),
        ):
            block(owner, name, "blocked_writes")
        block(importlib, "import_module", "blocked_imports")
        for name in ("create_dynamic", "exec_dynamic", "create_builtin"):
            block(_imp, name, "blocked_low_level_imports")
        for owner, name in (
            (_ctypes, "dlopen"), (ctypes, "CDLL"), (ctypes, "PyDLL"),
        ):
            block(owner, name, "blocked_native_loads")
        for owner, name in (
            (gzip, "GzipFile"), (gzip, "decompress"),
            (zlib, "decompress"), (zlib, "decompressobj"),
        ):
            block(owner, name, "blocked_decompression")
        for owner, name in (
            (subprocess, "Popen"), (subprocess, "run"),
            (_posixsubprocess, "fork_exec"), (os, "fork"), (os, "system"),
            (os, "execv"), (os, "execve"), (os, "posix_spawn"),
        ):
            block(owner, name, "blocked_processes")
        block(_thread, "start_new_thread", "blocked_threads")
        block(threading.Thread, "start", "blocked_threads")
        for owner, name in (
            (socket, "create_connection"), (socket.socket, "connect"),
            (_socket, "socket"),
        ):
            block(owner, name, "blocked_network")
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns", "thread_time", "thread_time_ns", "sleep",
        ):
            block(time, name, "blocked_clocks")
        yield effects
    finally:
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)


def require_coordination_release() -> None:
    require(
        V42_PINS_RELEASED is True
        and type(V42_OWNERS) is dict
        and set(V42_OWNERS) == {"source", "inputs", "summary", "svg"}
        and all(type(owner) is Owner for owner in V42_OWNERS.values()),
        "WAITING FOR COORDINATOR-RELEASED PUSHED V42 EXACT GRAPH OWNERS; FAIL CLOSED",
    )
    require(
        RUST_V6_PINS_RELEASED is True
        and type(RUST_V6_OWNERS) is dict
        and set(RUST_V6_OWNERS) == {"source", "protocol", "document"}
        and all(type(owner) is Owner for owner in RUST_V6_OWNERS.values()),
        "WAITING FOR COORDINATOR-RELEASED PUSHED RUST V6 EXACT OWNERS; FAIL CLOSED",
    )
    require(
        V45_PINS_RELEASED is True
        and type(V45_OWNERS) is dict
        and set(V45_OWNERS) == {"source", "inputs", "summary", "svg"}
        and all(type(owner) is Owner for owner in V45_OWNERS.values()),
        "WAITING FOR THE COORDINATOR-RELEASED PUSHED CURRENT V45 GRAPH; FAIL CLOSED",
    )
    require(
        RUST_V7_PINS_RELEASED is True
        and type(RUST_V7_OWNERS) is dict
        and set(RUST_V7_OWNERS) == {"source", "protocol", "document"}
        and all(type(owner) is Owner for owner in RUST_V7_OWNERS.values()),
        "WAITING FOR THE PUBLICATION-SAFE COORDINATOR-RELEASED RUST V7; FAIL CLOSED",
    )
    require(
        set(V43_OWNERS) == {"source", "inputs", "summary", "svg"}
        and set(PUBLIC_ENTRYPOINT_OWNERS) == {"source", "protocol", "document"}
        and set(PUBLIC_ENTRYPOINT_SURFACE) == {"entrypoint", "project"}
        and set(ACTUAL_RUST_V6_FAILURE) == {"failure", "observation"},
        "require current public-oracle and actual historical-failure owner completeness",
    )
    for name, owner in (
        *V42_OWNERS.items(), *RUST_V6_OWNERS.items(),
        *V43_OWNERS.items(), *V45_OWNERS.items(), *RUST_V7_OWNERS.items(),
        *PUBLIC_ENTRYPOINT_OWNERS.items(), *PUBLIC_ENTRYPOINT_SURFACE.items(),
        *ACTUAL_RUST_V6_FAILURE.items(),
    ):
        require(type(owner) is Owner,
                "reject guessed or substituted coordinator-released source owners")
        checked_relative(owner.path)
        checked_digest(owner.sha256, "coordinator-released " + name)
        require(type(owner.size_bytes) is int and 0 < owner.size_bytes <= MAX_SOURCE_BYTES,
                "reject absent, guessed, or unbounded coordinator-released owner bytes")


def require_verified_zig_activation() -> None:
    require_coordination_release()
    require(
        VERIFIED_ZIG_ACTIVATION_RELEASED is True
        and type(VERIFIED_ZIG_ACTIVATION_OWNERS) is dict
        and set(VERIFIED_ZIG_ACTIVATION_OWNERS)
        == {"source", "protocol", "document", "receipt"}
        and all(type(owner) is Owner for owner in VERIFIED_ZIG_ACTIVATION_OWNERS.values()),
        "NO INDEPENDENTLY FROZEN AND VERIFIED LIVE ZIG ACTIVATION; "
        "HISTORICAL V12 BUILD IS NOT ACTIVATION; FAIL CLOSED",
    )


def validate_candidate_source_audit(adapter: bytes, engine: bytes, bridge: bytes) -> dict[str, Any]:
    try:
        tree = ast.parse(adapter.decode("utf-8", "strict"), filename=ZIG_SOURCES["adapter"].path)
        engine_text = engine.decode("utf-8", "strict")
        bridge_text = bridge.decode("utf-8", "strict")
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise CandidateGateError("reject malformed actual first-party Zig source") from error
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported.append(module)
            if module == "candidates":
                imported.extend("candidates." + item.name for item in node.names)
    forbidden_roots = {"re", "_sre", "sre_compile", "sre_parse", "regex", "pcre", "re2"}
    require(
        all(name.split(".", 1)[0] not in forbidden_roots for name in imported)
        and not any(
            name == other or name.startswith(other + ".")
            for name in imported
            for other in (
                "candidates.rust_candidate", "candidates.vm_candidate",
                "candidates.cpp_candidate", "candidates.go_candidate",
                "candidates.fortran_candidate", "candidates._rust_bridge",
                "candidates._vm_native", "candidates._cpp_bridge",
                "candidates._go_bridge", "candidates._fortran_bridge",
            )
        )
        and "candidates._zig_bridge" in imported,
        "reject stdlib regex, an external package, another candidate, or a missing owned Zig bridge",
    )
    required_engine = (
        'const std = @import("std");',
        "Parser", "Compiler", "runBytecode", "runCapturedAt", "compileOwned",
        "pub export fn rebar_zig_compile",
        "pub export fn rebar_zig_match_wide",
        "pub export fn rebar_zig_match_captures_wide",
    )
    require(all(token in engine_text for token in required_engine),
            "require the actually owned Zig parser, compiler, executor, and C ABI")
    forbidden_native = (
        "PyImport_Import", "dlopen(", "dlsym(", "pcre2_", "onig_",
        "hs_compile", "hs_scan", 'std.process', 'std.DynLib',
        '@import("regex")', '@import("re2")',
        "rebar_rust_", "rebar_cpp_", "rebar_go_", "rebar_fortran_",
    )
    require(not any(token in engine_text or token in bridge_text for token in forbidden_native),
            "reject external, CPython, dynamically delegated, or cross-family native matching")
    require(
        '#include <Python.h>' in bridge_text
        and "extern void *rebar_zig_compile(" in bridge_text
        and "rebar_zig_match_captures_wide" in bridge_text
        and '"_sre.SRE_Scanner"' in bridge_text,
        "preserve the actual owned bridge and Python-compatible scanner display metadata",
    )
    return {
        "family": FAMILY,
        "adapter_imports": sorted(set(imported)),
        "owned_python_bridge_module": "candidates._zig_bridge",
        "owned_native_engine_relative": "candidates/_zig_probe.so",
        "owned_native_bridge_relative":
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "display_metadata_is_not_an_import": True,
        "external_regex_source_dependency_count": 0,
        "stdlib_regex_engine_source_dependency_count": 0,
        "cross_family_source_dependency_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
    }


def validate_corrected_reference(receipt: Any, v4_reference: Any) -> dict[str, Any]:
    require(type(receipt) is dict and type(v4_reference) is dict,
            "require both the actual published reference receipt and corrected V4 reference")
    require(
        receipt.get("schema")
        == "rebar-phase1-owned-public-type-reference-context-v1-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and receipt.get("reference_status") == "PASS"
        and receipt.get("source_sha256") == CORRECTED_REFERENCE["source"].sha256
        and receipt.get("protocol_sha256") == CORRECTED_REFERENCE["protocol"].sha256
        and receipt.get("contract_sha256") == CORRECTED_REFERENCE["document"].sha256
        and receipt.get("actual_distinct_reference_process_ids")
        == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and receipt.get("actual_reference_worker_count") == 2
        and receipt.get("actual_started_reference_worker_count") == 2
        and receipt.get("completed_reference_worker_count") == 2
        and receipt.get("validated_reference_worker_count") == 2
        and receipt.get("public_case_count_per_reference")
        == CORRECTED_PUBLIC_CASES_PER_REFERENCE
        and receipt.get("original_case_execution_denominator") == CASE_DENOMINATOR
        and receipt.get("full_reference_records_sha256") == CORRECTED_PUBLIC_RECORDS_SHA256
        and receipt.get("cache_records_sha256") == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and receipt.get("matrix_sha256") == CORRECTED_PUBLIC_MATRIX_SHA256
        and receipt.get("candidate_imports") == 0
        and receipt.get("candidate_workers_started") == 0
        and receipt.get("holdout") == "NOT OPENED",
        "reject stale-context, missing-worker, misattributed, or incomplete public reference evidence",
    )
    require(
        v4_reference.get("candidate_facing_reference") is True
        and v4_reference.get("records_sha256") == CORRECTED_PUBLIC_RECORDS_SHA256
        and v4_reference.get("historical_reference_records_sha256")
        == HISTORICAL_PUBLIC_RECORDS_SHA256
        and v4_reference.get("reference_pids") == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and v4_reference.get("case_count") == CORRECTED_PUBLIC_CASES_PER_REFERENCE
        and v4_reference.get("actual_reference_worker_count") == 2
        and v4_reference.get("completed_reference_worker_count") == 2
        and v4_reference.get("validated_reference_worker_count") == 2
        and v4_reference.get("cache_case_count") == CORRECTED_PUBLIC_COHORT_CASE_COUNT
        and v4_reference.get("cache_records_sha256")
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and v4_reference.get("cache_case_ids_sha256")
        == CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256
        and v4_reference.get("matrix_sha256") == CORRECTED_PUBLIC_MATRIX_SHA256
        and v4_reference.get("candidate_run_uses_both_complete_reference_vectors") is True
        and v4_reference.get("candidate_run_starts_reference_processes") is False
        and v4_reference.get("source_context_reads_reference_archive") is False
        and v4_reference.get("source_context_inflates_reference_archive") is False
        and v4_reference.get("c_pattern_equality_failure_waived") is False,
        "reject a false candidate-facing vector, invented reference PID, opened archive, or private waiver",
    )
    owners = v4_reference.get("owners")
    require(type(owners) is dict, "require separately identified V4 reference owners")
    for key in ("source", "protocol", "contract", "receipt", "falsification"):
        mapped = "document" if key == "contract" else key
        require(owners.get(key) == relative_owner_record(CORRECTED_REFERENCE[mapped]),
                "reject a changed corrected V4 reference owner: " + key)
    archive = owners.get("archive")
    require(
        type(archive) is dict
        and archive.get("relative", "").endswith(".json.gz")
        and archive.get("sha256")
        == "c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05"
        and archive.get("size_bytes") == 1_374_913,
        "record corrected public archive metadata without opening or inflating the archive",
    )
    return {
        "candidate_facing_reference": True,
        "reference_status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "reference_process_ids": list(CORRECTED_PUBLIC_REFERENCE_PIDS),
        "reference_worker_count": 2,
        "case_count_per_reference": CORRECTED_PUBLIC_CASES_PER_REFERENCE,
        "total_actual_reference_case_observations": 13_824,
        "full_reference_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "historical_script_context_records_sha256": HISTORICAL_PUBLIC_RECORDS_SHA256,
        "cache_case_count_per_reference": CORRECTED_PUBLIC_COHORT_CASE_COUNT,
        "cache_records_sha256": CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "cache_case_ids_sha256": CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256,
        "reference_receipt": owner_record(CORRECTED_REFERENCE["receipt"]),
        "archive_metadata_only": copy.deepcopy(archive),
        "archive_opened_by_source_freeze": False,
        "archive_inflated_by_source_freeze": False,
        "new_reference_processes_started_by_source_freeze": 0,
    }


def validate_v4_producer(document: Any) -> dict[str, Any]:
    require(
        type(document) is dict
        and document.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
        and document.get("status")
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and document.get("goal_sha256") == GOAL.sha256
        and document.get("family_count") == SOURCE_FAMILY_COUNT
        and document.get("source_owner_count") == SOURCE_OWNER_COUNT
        and document.get("suite_count") == SUITE_COUNT
        and document.get("case_execution_denominator") == CASE_DENOMINATOR,
        "reject a stale V3, C-only worker, changed denominator, or substituted V4 producer",
    )
    suites = document.get("suites")
    require(type(suites) is list and len(suites) == SUITE_COUNT,
            "preserve every frozen original V4 suite")
    require(
        tuple((row.get("id"), row.get("case_execution_count")) for row in suites)
        == SUITES,
        "reject hidden, duplicated, reordered, invented, or omitted original cases",
    )
    require(sum(count for _, count in SUITES) == CASE_DENOMINATOR,
            "preserve the exact 31,237-case phase-one denominator")
    phase = document.get("phase_one")
    require(
        type(phase) is dict
        and phase.get("inventory_relative") == PHASE_ONE.path
        and phase.get("inventory_sha256") == PHASE_ONE.sha256
        and phase.get("suite_count") == SUITE_COUNT
        and phase.get("case_execution_denominator") == CASE_DENOMINATOR
        and phase.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and phase.get("supplemental_cases_added") is False,
        "reject a changed original phase-one oracle or unnamed additional waiver",
    )
    families = document.get("families")
    require(type(families) is list and len(families) == SOURCE_FAMILY_COUNT,
            "retain all six independent source families as inventory only")
    zig = [row for row in families if type(row) is dict and row.get("family") == FAMILY]
    require(len(zig) == 1, "require exactly one independently owned Zig family")
    family = zig[0]
    require(
        family.get("module") == "candidates.zig_candidate"
        and family.get("bridge_module") == "candidates._zig_bridge"
        and family.get("adapter_relative") == ZIG_SOURCES["adapter"].path
        and family.get("engine_relative") == "candidates/_zig_probe.so"
        and family.get("bridge_relative")
        == "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"
        and family.get("combined_native_engine_and_bridge") is False
        and family.get("owned_ctypes_allowed") is True
        and family.get("owned_source_count") == len(ZIG_SOURCES)
        and family.get("sources") == [
            relative_owner_record(ZIG_SOURCES["adapter"]),
            relative_owner_record(ZIG_SOURCES["engine"]),
            relative_owner_record(ZIG_SOURCES["bridge"]),
        ],
        "reject wrapping another engine, rejecting the owned Zig FFI, or substituting source owners",
    )
    independence = document.get("independence_policy")
    require(
        type(independence) is dict
        and independence.get("candidate_regex_stdlib_allowed") is False
        and independence.get("candidate_sre_allowed") is False
        and independence.get("third_party_regex_allowed") is False
        and independence.get("cross_family_native_engine_allowed") is False
        and independence.get("fallback_allowed") is False
        and independence.get("new_public_reference_processes_allowed") is False,
        "require first-party matching without fallback, packages, CPython regex, or cross-family engines",
    )
    return family


def validate_historical_build(receipt: Any, lock: Any) -> dict[str, Any]:
    require(
        type(lock) is dict
        and lock.get("schema") == "rebar-official-language-toolchain-v1"
        and lock.get("language") == "Zig"
        and lock.get("version") == "0.16.0"
        and lock.get("release_channel") == "stable"
        and lock.get("compiler_sha256") == ZIG_COMPILER_SHA256,
        "require the actually pinned official stable Zig compiler lock")
    require(
        type(receipt) is dict
        and receipt.get("schema")
        == "rebar-phase2-owned-zig-scanner-source-build-v12-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == FAMILY
        and receipt.get("label") == "phase2-v12-zig-scanner-v2"
        and receipt.get("source_sha256") == HISTORICAL_V12_BUILD["source"].sha256
        and receipt.get("protocol_sha256") == HISTORICAL_V12_BUILD["protocol"].sha256
        and receipt.get("contract_sha256") == HISTORICAL_V12_BUILD["document"].sha256
        and receipt.get("actual_compiler_process_count") == 26
        and receipt.get("expected_compiler_process_count_only_after_success") == 26
        and receipt.get("actual_source_apply_count") == 2
        and receipt.get("corrected_bridge_sha256") == ZIG_SOURCES["bridge"].sha256
        and receipt.get("corrected_bridge_bytes") == ZIG_SOURCES["bridge"].size_bytes
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("candidate_imports") == 0
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("holdout") == "NOT OPENED",
        "distinguish an authentic historical 26-process source build from native activation or matching",
    )
    archive = receipt.get("archive")
    require(
        type(archive) is dict
        and archive.get("path", "").endswith(".json.gz")
        and archive.get("sha256") == ZIG_V12_BUILD_ARCHIVE_SHA256
        and archive.get("bytes") == 48_371,
        "retain actual historical build archive metadata without opening the archive",
    )
    return {
        "historical_build_status": "PASS",
        "build_publication_status": "PASS",
        "build_receipt_pass_means": "DURABLE PUBLICATION ONLY",
        "compiler_process_count": 26,
        "source_apply_count": 2,
        "archive_metadata_only": {
            "path": archive["path"], "sha256": archive["sha256"],
            "bytes": archive["bytes"],
        },
        "archive_opened_by_source_freeze": False,
        "native_libraries_loaded_by_historical_build": 0,
        "historical_build_establishes_live_activation": False,
        "historical_build_establishes_candidate_correctness": False,
        "candidate_correctness": "NOT MEASURED",
        "official_zig_lock": owner_record(OFFICIAL_ZIG_LOCK),
        "compiler_sha256": ZIG_COMPILER_SHA256,
        "compiler_executed_by_source_freeze": False,
    }


def validate_historical_campaign(receipt: Any) -> dict[str, Any]:
    require(
        type(receipt) is dict
        and receipt.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_qualified") is False
        and receipt.get("family") == FAMILY
        and receipt.get("campaign_source_sha256") == HISTORICAL_ZIG_CAMPAIGN["source"].sha256
        and receipt.get("campaign_protocol_sha256") == HISTORICAL_ZIG_CAMPAIGN["protocol"].sha256
        and receipt.get("campaign_contract_sha256") == HISTORICAL_ZIG_CAMPAIGN["document"].sha256
        and receipt.get("original_v3_producer_source_sha256")
        == HISTORICAL_ZIG_V3_PRODUCER_SOURCE_SHA256
        and receipt.get("original_v3_producer_protocol_sha256")
        == HISTORICAL_ZIG_V3_PRODUCER_PROTOCOL_SHA256
        and receipt.get("original_v3_producer_contract_sha256")
        == HISTORICAL_ZIG_V3_PRODUCER_CONTRACT_SHA256
        and receipt.get("case_execution_denominator") == CASE_DENOMINATOR
        and receipt.get("suite_count") == SUITE_COUNT
        and receipt.get("completed_suite_count") == SUITE_COUNT
        and receipt.get("actual_candidate_workers") == SUITE_COUNT
        and receipt.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and receipt.get("semantic_mismatch_count") == 1_764
        and receipt.get("verified_passing_case_count") == 3_711
        and receipt.get("infrastructure_failure_count") == 0
        and receipt.get("all_original_native_targets_restored") is True
        and receipt.get("holdout") == "NOT OPENED",
        "preserve the real historical stale-V3 Zig failure; publication PASS is not matching PASS",
    )
    archive = receipt.get("archive")
    require(
        type(archive) is dict
        and archive.get("sha256") == HISTORICAL_ZIG_CAMPAIGN_ARCHIVE_SHA256
        and archive.get("size_bytes") == 3_722_337,
        "preserve historical Zig failure archive metadata without opening its archive",
    )
    return {
        "historical_matching_status": "FAIL",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "historical_producer_version": 3,
        "historical_result_is_corrected_v4_campaign": False,
        "historical_candidate_workers": SUITE_COUNT,
        "historical_completed_suite_count": SUITE_COUNT,
        "historical_case_execution_denominator": CASE_DENOMINATOR,
        "historical_semantic_mismatch_count": 1_764,
        "historical_verified_passing_case_count": 3_711,
        "historical_infrastructure_failure_count": 0,
        "historical_failure_receipt": owner_record(HISTORICAL_ZIG_CAMPAIGN["receipt"]),
        "historical_archive_metadata_only": {
            "sha256": archive["sha256"], "bytes": archive["size_bytes"],
        },
        "archive_opened_by_source_freeze": False,
        "individual_suite_mismatches": "NOT ESTABLISHED BY SMALL RECEIPT",
    }


def validate_scanner_repair(document: Any, adapter: bytes) -> dict[str, Any]:
    require(
        type(document) is dict
        and document.get("schema") == "rebar-owned-zig-scanner-phrase-source-repair-v3"
        and document.get("status") == "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN",
        "preserve the actual source-only, unapplied Zig scanner correction",
    )
    repair = document.get("construction_repair")
    require(type(repair) is dict, "require the complete frozen scanner correction")
    matrix = repair.get("complete_original_scanner_matrix")
    derived = repair.get("corrected_private_adapter")
    original = repair.get("original_adapter")
    require(
        type(matrix) is dict
        and matrix.get("matrix_case_count") == 1_024
        and matrix.get("overflow_case_count") == 64
        and matrix.get("preserved_nonoverflow_case_count") == 960
        and matrix.get("overflow_family_case_counts")
        == {"named-captures": 16, "nested-captures": 32, "numbered-captures": 16}
        and matrix.get("candidate_imports") == 0
        and matrix.get("candidate_workers_started") == 0
        and matrix.get("native_activations") == 0
        and type(original) is dict
        and original.get("path") == ZIG_SOURCES["adapter"].path
        and original.get("sha256") == ZIG_SOURCES["adapter"].sha256
        and original.get("bytes") == ZIG_SOURCES["adapter"].size_bytes
        and original.get("modified") is False
        and type(derived) is dict
        and derived.get("sha256") == DERIVED_SCANNER_ADAPTER_SHA256
        and derived.get("bytes") == 68_530
        and derived.get("materialized") is False
        and derived.get("outside_block_unchanged") is True
        and repair.get("candidate_qualified") is False
        and repair.get("corrected_candidate_matching") == "NOT RUN"
        and repair.get("verbose_scanner_620_mismatches")
        == "NOT REPAIRED; CORRECTED CANDIDATE NOT RUN"
        and repair.get("original_bridge_modified") is False
        and repair.get("original_engine_modified") is False,
        "never misrepresent a source-only 64-case correction as applied or as repairing 620 verbose losses",
    )
    require(
        adapter.count(ORIGINAL_SCANNER_BLOCK) == 1
        and adapter.count(CORRECTED_SCANNER_BLOCK) == 0,
        "require the actual original Zig adapter to remain unmodified",
    )
    projected = adapter.replace(ORIGINAL_SCANNER_BLOCK, CORRECTED_SCANNER_BLOCK, 1)
    require(
        len(projected) == 68_530 and digest(projected) == DERIVED_SCANNER_ADAPTER_SHA256,
        "reproduce the unmaterialized corrected adapter from the exact original block in memory only",
    )
    return {
        "source_repair_status": "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN",
        "matrix_case_count": 1_024,
        "preserved_nonoverflow_case_count": 960,
        "capture_overflow_case_count": 64,
        "capture_overflow_family_counts": copy.deepcopy(matrix["overflow_family_case_counts"]),
        "original_adapter": owner_record(ZIG_SOURCES["adapter"]),
        "projected_corrected_adapter_sha256": DERIVED_SCANNER_ADAPTER_SHA256,
        "projected_corrected_adapter_bytes": 68_530,
        "projected_corrected_adapter_materialized": False,
        "correction_applied": False,
        "corrected_candidate_matching": "NOT RUN",
        "verbose_scanner_620_mismatches": "NOT REPAIRED; CORRECTED CANDIDATE NOT RUN",
        "mismatch_reduction": "NOT MEASURED",
        "speedup": "NOT MEASURED",
    }


def validate_v41_history(summary: Any) -> dict[str, Any]:
    require(
        type(summary) is dict
        and summary.get("schema") == "rebar-candidate-current-overview-v41-summary"
        and summary.get("status") == "PASS"
        and summary.get("all_candidate_matching_blocked") is True
        and summary.get("candidate_case_producer_status")
        == "V4 SOURCE FROZEN; C-ONLY V8/V10 RUNNER FROZEN; C MATCHING NOT RUN"
        and summary.get("pending_corrected_candidate_families")
        == ["rust", "zig", "cpp", "go", "fortran"]
        and summary.get("required_corrected_candidate_runner_versions") == ["RUST V6"]
        and summary.get("repository_evidence_owner_count") == 164
        and summary.get("authenticated_digest_addressed_history_paths") == 169
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and summary.get("qualified_candidate_count") == 0
        and summary.get("zig_original_campaign_status") == "FAIL"
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 1_764
        and summary.get("zig_original_campaign_verified_passing_case_count") == 3_711
        and summary.get("zig_original_campaign_infrastructure_failure_count") == 0
        and summary.get("zig_scanner_phrase_matrix_case_count") == 1_024
        and summary.get("zig_scanner_phrase_preserved_nonoverflow_case_count") == 960
        and summary.get("zig_scanner_phrase_correction_applied") is False
        and summary.get("zig_scanner_phrase_corrected_matching_status") == "NOT RUN"
        and summary.get("zig_scanner_phrase_measured_mismatch_reduction") == "NOT MEASURED"
        and summary.get("zig_scanner_phrase_measured_speedup") == "NOT MEASURED"
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("memory") == "NOT MEASURED"
        and summary.get("undefined_behavior") == "NOT MEASURED"
        and summary.get("timing_trials_run") == 0
        and summary.get("winner_selected") is False,
        "reject rewriting historical V41 C-only blocking, real Zig losses, or unmeasured performance",
    )
    return {
        "overview": "V41",
        "summary": owner_record(V41_OWNERS["summary"]),
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "v41_runner_is_c_only": True,
        "v41_rust_v6_was_not_published": True,
        "v41_zig_runner_was_not_frozen": True,
        "historical_zig_corrected_v4_matching_status": "NOT RUN",
        "whole_repository_census_claimed": False,
    }


def validate_v42_history(summary: Any) -> dict[str, Any]:
    require_coordination_release()
    require(
        type(summary) is dict
        and summary.get("schema") == "rebar-candidate-current-overview-v42-summary"
        and summary.get("status") == "PASS"
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and summary.get("candidate_case_producer_source_sha256")
        == ORIGINAL_PRODUCER["source"].sha256
        and summary.get("candidate_case_producer_protocol_sha256")
        == ORIGINAL_PRODUCER["protocol"].sha256
        and summary.get("candidate_case_producer_contract_sha256")
        == ORIGINAL_PRODUCER["document"].sha256
        and summary.get("candidate_case_producer_status")
        == "V4 SOURCE FROZEN; SEPARATE C-ONLY V8/V10 AND "
        "RUST-ONLY V6 RUNNERS FROZEN; BOTH MATCHING NOT RUN"
        and summary.get("all_candidate_matching_blocked") is True
        and summary.get("pending_corrected_candidate_families")
        == ["zig", "cpp", "go", "fortran"]
        and summary.get("required_corrected_candidate_runner_versions") == []
        and summary.get("dedicated_corrected_runnable_families") == ["c", "rust"]
        and summary.get("dedicated_corrected_runnable_family_count") == 2
        and summary.get("corrected_rust_only_runner_family") == "rust"
        and summary.get("corrected_rust_only_runner_source_sha256")
        == RUST_V6_OWNERS["source"].sha256
        and summary.get("corrected_rust_only_runner_protocol_sha256")
        == RUST_V6_OWNERS["protocol"].sha256
        and summary.get("corrected_rust_only_runner_contract_sha256")
        == RUST_V6_OWNERS["document"].sha256
        and summary.get("corrected_rust_only_runner_status")
        == "RUST-ONLY RUNNER SOURCE FROZEN; CORRECTED RUST MATCHING NOT RUN"
        and summary.get("rust_v6_runner_status")
        == "SOURCE FROZEN; CORRECTED RUST MATCHING NOT RUN"
        and summary.get("actual_candidate_workers_started_by_graph") == 0
        and summary.get("actual_reference_workers_started_by_graph") == 0
        and summary.get("actual_compiler_processes_started_by_graph") == 0
        and summary.get("zig_original_campaign_status") == "FAIL"
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 1_764
        and summary.get("zig_original_campaign_verified_passing_case_count") == 3_711
        and summary.get("zig_scanner_phrase_matrix_case_count") == 1_024
        and summary.get("zig_scanner_phrase_preserved_nonoverflow_case_count") == 960
        and summary.get("zig_scanner_phrase_prospective_case_count") == 64
        and summary.get("zig_scanner_phrase_correction_applied") is False
        and summary.get("zig_scanner_phrase_corrected_matching_status") == "NOT RUN"
        and summary.get("zig_scanner_phrase_measured_mismatch_reduction") == "NOT MEASURED"
        and summary.get("zig_scanner_phrase_measured_speedup") == "NOT MEASURED"
        and summary.get("repository_evidence_owner_count") == 164
        and summary.get("authenticated_digest_addressed_history_paths") == 169
        and summary.get("final_holdout_opened") is False
        and summary.get("qualified_candidate_count") == 0
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("memory") == "NOT MEASURED"
        and summary.get("undefined_behavior") == "NOT MEASURED"
        and summary.get("timing_trials_run") == 0
        and summary.get("winner_selected") is False,
        "reject guessed, stale, incomplete, measured, or premature coordinator-released V42 history",
    )
    return {
        "overview": "V42",
        "owners": {key: owner_record(owner) for key, owner in V42_OWNERS.items()},
        "rust_v6_owners": {
            key: owner_record(owner) for key, owner in RUST_V6_OWNERS.items()
        },
        "v42_dedicated_source_only_families": ["c", "rust"],
        "v42_pending_source_only_families": ["zig", "cpp", "go", "fortran"],
        "v42_rust_candidate_matching": "NOT RUN",
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "zig_candidate_matching": "NOT RUN",
        "zig_live_activation": "NOT FROZEN; FAIL CLOSED",
    }


def validate_rust_v6_source_freeze(document: Any) -> dict[str, Any]:
    require(
        type(document) is dict
        and document.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v6-recoverable-source-freeze"
        and document.get("version") == 6
        and document.get("family") == "rust"
        and document.get("status")
        == "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        "authenticate the actual Rust V6 source freeze without mistaking it for a Zig runner",
    )
    source = document.get("source")
    protocol = document.get("protocol")
    require(
        type(source) is dict
        and source.get("path") == RUST_V6_OWNERS["source"].path
        and source.get("sha256") == RUST_V6_OWNERS["source"].sha256
        and type(protocol) is dict
        and protocol.get("path") == RUST_V6_OWNERS["protocol"].path
        and protocol.get("sha256") == RUST_V6_OWNERS["protocol"].sha256,
        "bind the published Rust-only source freeze to its exact independently released owners",
    )
    oracle = document.get("original_oracle")
    reference = document.get("actual_corrected_candidate_context_reference")
    effects = document.get("source_only_effects")
    require(
        type(oracle) is dict
        and oracle.get("suite_count") == SUITE_COUNT
        and oracle.get("case_execution_denominator") == CASE_DENOMINATOR
        and oracle.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and type(oracle.get("producer")) is dict
        and oracle["producer"].get("source") == owner_record(ORIGINAL_PRODUCER["source"])
        and oracle["producer"].get("protocol") == owner_record(ORIGINAL_PRODUCER["protocol"])
        and oracle["producer"].get("contract") == owner_record(ORIGINAL_PRODUCER["document"])
        and type(reference) is dict
        and reference.get("actual_distinct_reference_process_ids")
        == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and reference.get("actual_distinct_reference_process_count") == 2
        and reference.get("case_count_per_reference")
        == CORRECTED_PUBLIC_CASES_PER_REFERENCE
        and reference.get("total_observed_reference_case_count") == 13_824
        and reference.get("full_reference_records_sha256")
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and reference.get("cache_case_count_per_reference")
        == CORRECTED_PUBLIC_COHORT_CASE_COUNT
        and reference.get("cache_records_sha256")
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and reference.get("candidate_matching") == "NOT RUN"
        and reference.get("candidate_qualified") is False
        and reference.get("source_context_opens_reference_archive") is False
        and reference.get("source_context_inflates_reference_archive") is False
        and type(effects) is dict
        and effects.get("actual_candidate_workers") == 0
        and effects.get("actual_reference_workers") == 0
        and effects.get("actual_source_builds") == 0
        and effects.get("actual_native_activations") == 0
        and effects.get("actual_native_library_loads") == 0
        and effects.get("holdout") == "NOT OPENED"
        and effects.get("performance") == "NOT MEASURED"
        and effects.get("memory") == "NOT MEASURED"
        and effects.get("undefined_behavior") == "NOT MEASURED",
        "reject a changed Rust-only V4 source, reference, phase-one denominator, or zero-effect status",
    )
    return {
        "family": "rust",
        "source_freeze_status": "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        "owners": {
            key: owner_record(owner) for key, owner in RUST_V6_OWNERS.items()
        },
        "rust_candidate_matching": "NOT RUN",
        "rust_candidate_workers_started_by_source_freeze": 0,
        "rust_runner_is_a_zig_runner": False,
    }


def validate_actual_rust_v6_failure(
    failure: Any, observation: Any
) -> dict[str, Any]:
    require(
        type(failure) is dict
        and failure.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v6-entry-failure"
        and failure.get("status") == "FAIL"
        and failure.get("family") == "rust"
        and failure.get("campaign_source_sha256") == RUST_V6_OWNERS["source"].sha256
        and failure.get("campaign_protocol_sha256") == RUST_V6_OWNERS["protocol"].sha256
        and failure.get("campaign_contract_sha256") == RUST_V6_OWNERS["document"].sha256
        and failure.get("case_execution_denominator") == CASE_DENOMINATOR
        and failure.get("suite_count") == SUITE_COUNT
        and failure.get("attempted_suite_count") == 0
        and failure.get("started_suite_count") == 0
        and failure.get("fully_observed_suite_count") == 0
        and failure.get("actual_candidate_workers") == 0
        and failure.get("actual_reference_workers") == 0
        and failure.get("actual_native_activations") == 0
        and failure.get("semantic_mismatch_count") == "NOT MEASURED"
        and failure.get("candidate_qualified") is False
        and failure.get("source_only_zero_effects_claimed") is False
        and failure.get("holdout") == "NOT OPENED"
        and failure.get("performance") == "NOT MEASURED",
        "preserve the actually failed Rust V6 preflight without inventing matching or zero actual effects",
    )
    require(
        type(observation) is dict
        and observation.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v6-entry-failure-independent-observation-v1"
        and observation.get("observation_status")
        == "PASS; FAILURE AND OMITTED SOURCE-BUILD EFFECT PRESERVED",
        "require the authentic independent observation of the historical failed run",
    )
    effects = observation.get("source_build_archive_effect")
    candidate = observation.get("actual_candidate_effects")
    require(
        type(effects) is dict
        and effects.get("archive_read_count") == 1
        and effects.get("gzip_inflation_count") == 1
        and effects.get("controller_failure_ledger_records_effect") is False
        and effects.get("matching_archive_read_count") == 0
        and effects.get("nested_matching_archive_read_count") == 0
        and effects.get("reference_archive_read_count") == 0
        and type(candidate) is dict
        and candidate.get("candidate_workers") == 0
        and candidate.get("reference_workers") == 0
        and candidate.get("native_activations") == 0
        and candidate.get("attempted_suite_count") == 0
        and candidate.get("started_suite_count") == 0
        and candidate.get("fully_observed_suite_count") == 0
        and candidate.get("case_execution_denominator") == CASE_DENOMINATOR
        and candidate.get("suite_count") == SUITE_COUNT
        and candidate.get("semantic_mismatch_count") == "NOT MEASURED"
        and candidate.get("candidate_qualified") is False
        and candidate.get("holdout") == "NOT OPENED",
        "preserve one genuine prior build-archive inflation and zero matching/reference workers",
    )
    return {
        "family": "rust",
        "actual_preflight_status": "FAIL",
        "failure": owner_record(ACTUAL_RUST_V6_FAILURE["failure"]),
        "independent_observation": owner_record(
            ACTUAL_RUST_V6_FAILURE["observation"]
        ),
        "historical_source_build_archive_read_count": 1,
        "historical_source_build_archive_gzip_inflation_count": 1,
        "historical_source_build_archive_compressed_bytes": 108_985,
        "historical_source_build_archive_effect_was_omitted_by_failed_controller": True,
        "historical_matching_archive_read_count": 0,
        "historical_reference_archive_read_count": 0,
        "historical_candidate_workers": 0,
        "historical_reference_workers": 0,
        "historical_native_activations": 0,
        "historical_semantic_mismatch_count": "NOT MEASURED",
        "failure_archive_read_or_inflated_by_zig_source_freeze": False,
    }


def validate_v43_history(summary: Any) -> dict[str, Any]:
    require(
        type(summary) is dict
        and summary.get("schema") == "rebar-candidate-current-overview-v43-summary"
        and summary.get("version") == 43
        and summary.get("status") == "PASS"
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and summary.get("candidate_case_producer_source_sha256")
        == ORIGINAL_PRODUCER["source"].sha256
        and summary.get("candidate_case_producer_protocol_sha256")
        == ORIGINAL_PRODUCER["protocol"].sha256
        and summary.get("candidate_case_producer_contract_sha256")
        == ORIGINAL_PRODUCER["document"].sha256
        and summary.get("candidate_case_producer_status")
        == "V4 SOURCE FROZEN; RUST PREFLIGHT FAIL; ZERO RUNNABLE CANDIDATES"
        and summary.get("all_candidate_matching_blocked") is True
        and summary.get("actually_runnable_candidate_families") == []
        and summary.get("actually_runnable_candidate_family_count") == 0
        and summary.get("authenticated_evidence_owner_lower_bound") == 166
        and summary.get("authenticated_history_reference_lower_bound") == 171
        and summary.get("actual_rust_source_build_archive_read_count") == 1
        and summary.get("actual_rust_source_build_archive_gzip_inflation_count") == 1
        and summary.get("actual_rust_source_build_archive_compressed_bytes") == 108_985
        and summary.get("actual_rust_failure_evidence_sha256")
        == ACTUAL_RUST_V6_FAILURE["failure"].sha256
        and summary.get("actual_rust_candidate_workers") == 0
        and summary.get("actual_rust_attempted_suite_count") == 0
        and summary.get("actual_rust_matching_archive_read_count") == 0
        and summary.get("actual_rust_reference_archive_read_count") == 0
        and summary.get("actual_candidate_workers_started_by_graph") == 0
        and summary.get("actual_reference_workers_started_by_graph") == 0
        and summary.get("actual_compiler_processes_started_by_graph") == 0
        and summary.get("final_holdout_opened") is False
        and summary.get("qualified_candidate_count") == 0
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("memory") == "NOT MEASURED"
        and summary.get("undefined_behavior") == "NOT MEASURED"
        and summary.get("timing_trials_run") == 0
        and summary.get("winner_selected") is False,
        "preserve the published V43 failed-preflight graph and genuine 166/171 evidence bounds",
    )
    return {
        "overview": "V43",
        "owners": {key: owner_record(owner) for key, owner in V43_OWNERS.items()},
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "historical_rust_failure_status": "FAIL",
        "historical_rust_build_archive_read_count": 1,
        "historical_rust_build_archive_gzip_inflation_count": 1,
        "historical_rust_candidate_workers": 0,
        "historical_rust_reference_workers": 0,
        "actually_runnable_candidate_families": [],
        "archive_opened_by_zig_source_freeze": False,
    }


def validate_rust_v7_source_freeze(document: Any) -> dict[str, Any]:
    require(
        type(document) is dict
        and document.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v7-recoverable-source-freeze"
        and document.get("version") == 7
        and document.get("family") == "rust"
        and document.get("status")
        == "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        "require the actual publication-safe, first-party, source-only Rust V7 freeze",
    )
    source = document.get("source")
    protocol = document.get("protocol")
    accounting = document.get("current_historical_accounting")
    oracle = document.get("original_oracle")
    reference = document.get("actual_corrected_candidate_context_reference")
    preserved = document.get("preserved_actual_v6_preflight_failure")
    effects = document.get("source_only_effects")
    require(
        type(source) is dict
        and source.get("path") == RUST_V7_OWNERS["source"].path
        and source.get("sha256") == RUST_V7_OWNERS["source"].sha256
        and type(protocol) is dict
        and protocol.get("path") == RUST_V7_OWNERS["protocol"].path
        and protocol.get("sha256") == RUST_V7_OWNERS["protocol"].sha256
        and type(accounting) is dict
        and accounting.get("actual_evidence_owner_count_before_new_campaign") == 166
        and accounting.get("actual_authenticated_reference_count_before_new_campaign") == 171
        and accounting.get("actual_v6_failure_evidence_owners_created") == 2
        and accounting.get("future_campaign_evidence_owners_created") == 0
        and accounting.get("qualified_candidate_count") == 0
        and type(oracle) is dict
        and oracle.get("suite_count") == SUITE_COUNT
        and oracle.get("case_execution_denominator") == CASE_DENOMINATOR
        and oracle.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and type(oracle.get("producer")) is dict
        and oracle["producer"].get("source")
        == owner_record(ORIGINAL_PRODUCER["source"])
        and oracle["producer"].get("protocol")
        == owner_record(ORIGINAL_PRODUCER["protocol"])
        and oracle["producer"].get("contract")
        == owner_record(ORIGINAL_PRODUCER["document"])
        and type(reference) is dict
        and reference.get("actual_distinct_reference_process_ids")
        == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and reference.get("actual_distinct_reference_process_count") == 2
        and reference.get("case_count_per_reference")
        == CORRECTED_PUBLIC_CASES_PER_REFERENCE
        and reference.get("total_observed_reference_case_count") == 13_824
        and reference.get("full_reference_records_sha256")
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and reference.get("cache_case_count_per_reference")
        == CORRECTED_PUBLIC_COHORT_CASE_COUNT
        and reference.get("cache_records_sha256")
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and reference.get("candidate_matching") == "NOT RUN"
        and reference.get("candidate_qualified") is False,
        "reject a stale Rust runner, altered V4 route, incorrect corrected reference, or false bounds",
    )
    owners = preserved.get("owners") if type(preserved) is dict else None
    require(
        type(preserved) is dict
        and preserved.get("status") == "FAIL"
        and preserved.get("actual_source_build_archive_read_count") == 1
        and preserved.get("actual_source_build_archive_gzip_inflation_count") == 1
        and preserved.get("actual_source_build_archive_compressed_bytes") == 108_985
        and preserved.get("actual_candidate_workers") == 0
        and preserved.get("matching_archive_read_count") == 0
        and preserved.get("reference_archive_read_count") == 0
        and preserved.get("semantic_mismatch_count") == "NOT MEASURED"
        and type(owners) is dict
        and owners.get("failure")
        == owner_record(ACTUAL_RUST_V6_FAILURE["failure"])
        and owners.get("observation")
        == owner_record(ACTUAL_RUST_V6_FAILURE["observation"])
        and type(effects) is dict
        and effects.get("actual_candidate_workers") == 0
        and effects.get("actual_reference_workers") == 0
        and effects.get("actual_source_builds") == 0
        and effects.get("actual_native_activations") == 0
        and effects.get("actual_native_library_loads") == 0
        and effects.get("v13_source_build_archive_read_count") == 0
        and effects.get("v13_source_build_archive_gzip_inflation_count") == 0
        and effects.get("matching_archive_bytes_read") == 0
        and effects.get("candidate_correctness") == "NOT MEASURED"
        and effects.get("candidate_qualified") is False
        and effects.get("performance") == "NOT MEASURED"
        and effects.get("memory") == "NOT MEASURED"
        and effects.get("undefined_behavior") == "NOT MEASURED"
        and effects.get("holdout") == "NOT OPENED",
        "distinguish the genuinely preserved V6 archive effect from zero-effect V7 source verification",
    )
    return {
        "family": "rust",
        "source_freeze_status": "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        "owners": {key: owner_record(owner) for key, owner in RUST_V7_OWNERS.items()},
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "preserved_actual_v6_build_archive_read_count": 1,
        "preserved_actual_v6_build_archive_gzip_inflation_count": 1,
        "rust_candidate_matching": "NOT RUN",
        "rust_candidate_workers_started_by_source_freeze": 0,
        "rust_runner_is_a_zig_runner": False,
    }


def validate_public_entrypoint_oracle(
    document: Any, entrypoint_source: bytes
) -> dict[str, Any]:
    require(
        type(document) is dict
        and document.get("schema")
        == "rebar-python-re-public-entrypoint-import-v1-source-freeze"
        and document.get("version") == 1
        and document.get("goal_sha256") == GOAL.sha256
        and document.get("case_matrix_sha256") == PUBLIC_ENTRYPOINT_MATRIX_SHA256,
        "require the actual independent, frozen 32-case Python public-entrypoint oracle",
    )
    matrix = document.get("case_matrix")
    require(type(matrix) is list and len(matrix) == 32,
            "preserve all 32 original expanded public-entrypoint source checks")
    require(digest(canonical(matrix)[:-1]) == PUBLIC_ENTRYPOINT_MATRIX_SHA256,
            "reject omitted, reordered, relabeled, or changed public-entrypoint cases")
    counts = {"PASS": 0, "FAIL": 0, "NOT MEASURED": 0,
              "NOT ESTABLISHED": 0, "NOT OPENED": 0}
    identifiers: set[str] = set()
    for item in matrix:
        require(type(item) is dict and type(item.get("id")) is str
                and item["id"] not in identifiers
                and item.get("observed_status") in counts,
                "reject duplicated, ambiguous, or unclassified public-entrypoint evidence")
        identifiers.add(item["id"])
        counts[item["observed_status"]] += 1
    require(
        counts == {
            "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
            "NOT ESTABLISHED": 1, "NOT OPENED": 1,
        },
        "preserve 17 real passing checks, seven failures, and all unmeasured public obligations",
    )
    correctness = document.get("original_correctness")
    boundaries = document.get("boundaries")
    owners = document.get("owners")
    policy = document.get("future_public_winner_policy")
    require(
        type(correctness) is dict
        and correctness.get("case_count") == CASE_DENOMINATOR
        and correctness.get("suite_count") == SUITE_COUNT
        and correctness.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and correctness.get("additional_signature_case_count") == 50
        and correctness.get("additional_signature_cases_in_original_denominator") is False
        and type(boundaries) is dict
        and boundaries.get("observed_public_entrypoint_status") == "FAIL"
        and boundaries.get("observed_public_entrypoint_classification")
        == "UNQUALIFIED_ZIG_PROTOTYPE"
        and boundaries.get("qualified_candidate_count") == 0
        and boundaries.get("public_entrypoint_qualified") is False
        and boundaries.get("actual_public_entrypoint_imports") == 0
        and boundaries.get("actual_candidate_imports") == 0
        and boundaries.get("actual_native_libraries_loaded") == 0
        and boundaries.get("actual_archives_opened") == 0
        and boundaries.get("actual_archives_decompressed") == 0
        and boundaries.get("actual_holdout_cases_read") == 0
        and boundaries.get("final_holdout_status") == "NOT OPENED"
        and boundaries.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and boundaries.get("performance") == "NOT MEASURED"
        and boundaries.get("winner_selected") is False
        and type(policy) is dict
        and policy.get("allows_external_regex_engine") is False
        and policy.get("allows_cross_family_fallback") is False
        and policy.get("allows_stdlib_regex_fallback") is False
        and policy.get("allows_premature_winner") is False
        and policy.get("fixes_public_entrypoint_in_this_chunk") is False
        and type(owners) is dict
        and owners.get("historical_zig_adapter")
        == owner_record(ZIG_SOURCES["adapter"])
        and owners.get("public_entrypoint")
        == owner_record(PUBLIC_ENTRYPOINT_SURFACE["entrypoint"])
        and owners.get("project_configuration")
        == owner_record(PUBLIC_ENTRYPOINT_SURFACE["project"])
        and owners.get("repaired_rust_v7_source")
        == owner_record(RUST_V7_OWNERS["source"])
        and owners.get("repaired_rust_v7_protocol")
        == owner_record(RUST_V7_OWNERS["protocol"])
        and owners.get("repaired_rust_v7_contract")
        == owner_record(RUST_V7_OWNERS["document"]),
        "preserve actual failing public import, exact source owners, and zero candidate/native execution",
    )
    try:
        tree = ast.parse(entrypoint_source.decode("utf-8", "strict"),
                         filename=PUBLIC_ENTRYPOINT_SURFACE["entrypoint"].path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise CandidateGateError("reject invalid actually frozen public-entrypoint source") from error
    imports = [
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    ]
    require(bool(imports) and set(imports) == {"candidates.zig_candidate"},
            "preserve the actual premature Zig entrypoint without importing it or treating it as a winner")
    return {
        "oracle_owners": {
            key: owner_record(owner) for key, owner in PUBLIC_ENTRYPOINT_OWNERS.items()
        },
        "actual_public_source": owner_record(
            PUBLIC_ENTRYPOINT_SURFACE["entrypoint"]
        ),
        "actual_project_configuration": owner_record(
            PUBLIC_ENTRYPOINT_SURFACE["project"]
        ),
        "source_ast_only": True,
        "actual_public_imports_by_zig_source_freeze": 0,
        "public_entrypoint_status": "FAIL",
        "public_entrypoint_classification": "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER",
        "selected_family_is_historically_failed_zig": True,
        "matrix_case_count": 32,
        "matrix_sha256": PUBLIC_ENTRYPOINT_MATRIX_SHA256,
        "case_status_counts": counts,
        "additional_signature_case_count": 50,
        "additional_cases_added_to_original_denominator": False,
        "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_v45_history(summary: Any) -> dict[str, Any]:
    require(
        type(summary) is dict
        and summary.get("schema") == "rebar-candidate-current-overview-v45-summary"
        and summary.get("version") == 45
        and summary.get("status") == "PASS"
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and summary.get("candidate_case_producer_source_sha256")
        == ORIGINAL_PRODUCER["source"].sha256
        and summary.get("candidate_case_producer_protocol_sha256")
        == ORIGINAL_PRODUCER["protocol"].sha256
        and summary.get("candidate_case_producer_contract_sha256")
        == ORIGINAL_PRODUCER["document"].sha256
        and summary.get("all_candidate_matching_blocked") is True
        and summary.get("actually_runnable_candidate_families") == []
        and summary.get("actually_runnable_candidate_family_count") == 0
        and summary.get("dedicated_corrected_runnable_families") == []
        and summary.get("dedicated_corrected_runnable_family_count") == 0
        and summary.get("authenticated_evidence_owner_lower_bound") == 166
        and summary.get("authenticated_history_reference_lower_bound") == 171
        and summary.get("actual_rust_source_build_archive_read_count") == 1
        and summary.get("actual_rust_source_build_archive_gzip_inflation_count") == 1
        and summary.get("actual_rust_source_build_archive_compressed_bytes") == 108_985
        and summary.get("actual_rust_candidate_workers") == 0
        and summary.get("actual_rust_attempted_suite_count") == 0
        and summary.get("actual_candidate_workers_started_by_graph") == 0
        and summary.get("actual_reference_workers_started_by_graph") == 0
        and summary.get("actual_compiler_processes_started_by_graph") == 0
        and summary.get("corrected_reference_process_ids")
        == list(CORRECTED_PUBLIC_REFERENCE_PIDS)
        and summary.get("corrected_reference_actual_worker_count") == 2
        and summary.get("corrected_reference_case_count_per_worker")
        == CORRECTED_PUBLIC_CASES_PER_REFERENCE
        and summary.get("corrected_reference_full_records_sha256")
        == CORRECTED_PUBLIC_RECORDS_SHA256
        and summary.get("corrected_reference_cache_records_sha256")
        == CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
        and summary.get("corrected_rust_v7_source_sha256")
        == RUST_V7_OWNERS["source"].sha256
        and summary.get("corrected_rust_v7_protocol_sha256")
        == RUST_V7_OWNERS["protocol"].sha256
        and summary.get("corrected_rust_v7_contract_sha256")
        == RUST_V7_OWNERS["document"].sha256
        and summary.get("corrected_rust_v7_source_self_test_control_count") == 517
        and summary.get("corrected_rust_v7_candidate_matching_status") == "NOT RUN"
        and summary.get("corrected_rust_v7_actual_candidate_workers") == 0
        and summary.get("corrected_rust_v7_actual_native_activations") == 0
        and summary.get("corrected_rust_v7_candidate_qualified") is False
        and summary.get("public_entrypoint_oracle_source_sha256")
        == PUBLIC_ENTRYPOINT_OWNERS["source"].sha256
        and summary.get("public_entrypoint_oracle_protocol_sha256")
        == PUBLIC_ENTRYPOINT_OWNERS["protocol"].sha256
        and summary.get("public_entrypoint_oracle_contract_sha256")
        == PUBLIC_ENTRYPOINT_OWNERS["document"].sha256
        and summary.get("public_entrypoint_case_matrix_count") == 32
        and summary.get("public_entrypoint_case_matrix_sha256")
        == PUBLIC_ENTRYPOINT_MATRIX_SHA256
        and summary.get("public_entrypoint_pass_count") == 17
        and summary.get("public_entrypoint_fail_count") == 7
        and summary.get("public_entrypoint_not_measured_count") == 6
        and summary.get("public_entrypoint_not_established_count") == 1
        and summary.get("public_entrypoint_not_opened_count") == 1
        and summary.get("public_entrypoint_actual_observed_status") == "FAIL"
        and summary.get("public_entrypoint_status")
        == "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER"
        and summary.get("public_entrypoint_selected_family") == FAMILY
        and summary.get("public_entrypoint_qualified") is False
        and summary.get("public_entrypoint_winner_selected") is False
        and summary.get("public_entrypoint_cases_in_original_denominator") is False
        and summary.get("public_entrypoint_cases_in_signature_denominator") is False
        and summary.get("public_entrypoint_actual_imports_by_graph") == 0
        and summary.get("public_entrypoint_actual_native_loads_by_graph") == 0
        and summary.get("zig_original_campaign_status") == "FAIL"
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 1_764
        and summary.get("zig_original_campaign_verified_passing_case_count") == 3_711
        and summary.get("zig_original_campaign_infrastructure_failure_count") == 0
        and summary.get("zig_scanner_phrase_matrix_case_count") == 1_024
        and summary.get("zig_scanner_phrase_preserved_nonoverflow_case_count") == 960
        and summary.get("zig_scanner_phrase_prospective_case_count") == 64
        and summary.get("zig_scanner_phrase_correction_applied") is False
        and summary.get("zig_scanner_phrase_corrected_matching_status") == "NOT RUN"
        and summary.get("qualified_candidate_count") == 0
        and summary.get("final_holdout_opened") is False
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("memory") == "NOT MEASURED"
        and summary.get("undefined_behavior") == "NOT MEASURED"
        and summary.get("timing_trials_run") == 0
        and summary.get("winner_selected") is False,
        "reject stale history, false runtime eligibility, omitted Rust archive effects, or hidden public losses",
    )
    return {
        "overview": "V45",
        "owners": {key: owner_record(owner) for key, owner in V45_OWNERS.items()},
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "actually_runnable_candidate_families": [],
        "actually_runnable_candidate_family_count": 0,
        "actual_rust_v6_build_archive_read_count": 1,
        "actual_rust_v6_build_archive_gzip_inflation_count": 1,
        "actual_rust_v6_candidate_workers": 0,
        "publication_safe_rust_v7_source_frozen_only": True,
        "zig_public_entrypoint_status": "FAIL",
        "public_entrypoint_matrix_case_count": 32,
        "public_entrypoint_case_status_counts": {
            "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
            "NOT ESTABLISHED": 1, "NOT OPENED": 1,
        },
        "zig_candidate_matching": "NOT RUN",
        "zig_live_activation": "NOT FROZEN; FAIL CLOSED",
        "holdout": "NOT OPENED",
    }


def source_zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_compiler_processes": 0,
        "actual_native_activations": 0,
        "actual_native_promotions": 0,
        "actual_native_libraries_loaded": 0,
        "actual_threads_started": 0,
        "actual_network_requests": 0,
        "archives_opened": 0,
        "archives_inflated": 0,
        "compressed_archive_bytes_read": 0,
        "uncompressed_archive_bytes_read": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def synthetic_contract() -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA + "-synthetic-source-control",
        "family": FAMILY,
        "suite_count": SUITE_COUNT,
        "suites": [{"id": name, "case_execution_count": count} for name, count in SUITES],
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": SOURCE_FAMILY_COUNT,
        "source_owner_count": SOURCE_OWNER_COUNT,
        "current_overview_version": 45,
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "runnable_candidate_families": [],
        "runnable_candidate_family_count": 0,
        "future_exclusively_runnable_candidate_family": FAMILY,
        "zig_source_owners": {
            key: owner_record(owner) for key, owner in ZIG_SOURCES.items()
        },
        "original_producer": {
            key: owner_record(owner) for key, owner in ORIGINAL_PRODUCER.items()
        },
        "corrected_reference_full_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256,
        "historical_script_context_records_sha256": HISTORICAL_PUBLIC_RECORDS_SHA256,
        "corrected_reference_process_ids": list(CORRECTED_PUBLIC_REFERENCE_PIDS),
        "corrected_reference_case_count_per_worker": CORRECTED_PUBLIC_CASES_PER_REFERENCE,
        "corrected_reference_case_observation_count": 13_824,
        "corrected_reference_cache_case_count_per_worker": CORRECTED_PUBLIC_COHORT_CASE_COUNT,
        "corrected_reference_cache_records_sha256": CORRECTED_PUBLIC_COHORT_RECORDS_SHA256,
        "corrected_reference_cache_case_ids_sha256": CORRECTED_PUBLIC_COHORT_CASE_IDS_SHA256,
        "historical_zig_mismatch_count": 1_764,
        "historical_zig_verified_passing_case_count": 3_711,
        "historical_zig_matching_status": "FAIL",
        "historical_zig_producer_version": 3,
        "historical_zig_build_compiler_process_count": 26,
        "historical_zig_build_is_live_activation": False,
        "historical_rust_v6_preflight_status": "FAIL",
        "historical_rust_v6_build_archive_read_count": 1,
        "historical_rust_v6_build_archive_gzip_inflation_count": 1,
        "historical_rust_v6_candidate_workers": 0,
        "publication_safe_rust_v7_candidate_matching": "NOT RUN",
        "public_entrypoint_status": "FAIL",
        "public_entrypoint_matrix_case_count": 32,
        "public_entrypoint_matrix_sha256": PUBLIC_ENTRYPOINT_MATRIX_SHA256,
        "public_entrypoint_case_status_counts": {
            "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
            "NOT ESTABLISHED": 1, "NOT OPENED": 1,
        },
        "official_zig_compiler_path": ZIG_COMPILER_ABSOLUTE_PATH,
        "official_zig_compiler_sha256": ZIG_COMPILER_SHA256,
        "official_zig_compiler_bytes": ZIG_COMPILER_BYTES,
        "official_zig_compiler_executed": False,
        "scanner_matrix_case_count": 1_024,
        "scanner_preserved_nonoverflow_case_count": 960,
        "scanner_overflow_case_count": 64,
        "scanner_correction_applied": False,
        "scanner_verbose_620_repaired": False,
        "corrected_candidate_matching": "NOT RUN",
        "verified_live_zig_activation": "NOT FROZEN; FAIL CLOSED",
        "qualified_candidate_count": 0,
        "source_only_effects": source_zero_effects(),
        "candidate_correctness": "NOT MEASURED",
        "from_scratch_policy": {
            "external_regex_package": "FORBIDDEN",
            "stdlib_matching_engine": "FORBIDDEN",
            "another_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "winner_selected": False,
    }


def validate_synthetic(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(synthetic_contract()),
            "reject any changed owner, reference, suite, denominator, loss, repair, or fail-closed control")
    suites = value["suites"]
    require(len(suites) == SUITE_COUNT
            and sum(item["case_execution_count"] for item in suites) == CASE_DENOMINATOR,
            "require exactly 13 complete original suites and 31,237 cases")
    return value


def expect_rejection(function: Any, *arguments: Any) -> None:
    try:
        function(*arguments)
    except (CandidateGateError, SourceOnlyEffect, ValueError, TypeError, KeyError, OSError):
        return
    raise CandidateGateError("accepted an adversarial first-party Zig source-only control")


def synthetic_source_fault_controls() -> dict[str, int]:
    accepted = 0
    rejected = 0
    original = validate_synthetic(synthetic_contract())
    accepted += 1
    mutations: list[tuple[str, Any]] = [
        ("schema", RUNNER_SCHEMA),
        ("family", "c"),
        ("suite_count", 12),
        ("case_execution_denominator", 31_236),
        ("named_private_waiver_count", 12),
        ("source_family_count", 5),
        ("source_owner_count", 24),
        ("current_overview_version", 44),
        ("authenticated_evidence_owner_lower_bound", 164),
        ("authenticated_history_reference_lower_bound", 169),
        ("runnable_candidate_families", [FAMILY]),
        ("runnable_candidate_family_count", 1),
        ("future_exclusively_runnable_candidate_family", "c"),
        ("corrected_reference_full_records_sha256", HISTORICAL_PUBLIC_RECORDS_SHA256),
        ("corrected_reference_process_ids", [82, 83]),
        ("corrected_reference_process_ids", [81, 81]),
        ("corrected_reference_case_count_per_worker", 6_911),
        ("corrected_reference_case_observation_count", 6_912),
        ("corrected_reference_cache_case_count_per_worker", 95),
        ("corrected_reference_cache_records_sha256", "0" * 64),
        ("historical_zig_mismatch_count", 0),
        ("historical_zig_verified_passing_case_count", 31_237),
        ("historical_zig_matching_status", "PASS"),
        ("historical_zig_producer_version", 4),
        ("historical_zig_build_compiler_process_count", 25),
        ("historical_zig_build_is_live_activation", True),
        ("historical_rust_v6_preflight_status", "PASS"),
        ("historical_rust_v6_build_archive_read_count", 0),
        ("historical_rust_v6_build_archive_gzip_inflation_count", 0),
        ("historical_rust_v6_candidate_workers", 1),
        ("publication_safe_rust_v7_candidate_matching", "PASS"),
        ("public_entrypoint_status", "PASS"),
        ("public_entrypoint_matrix_case_count", 31),
        ("public_entrypoint_matrix_sha256", "0" * 64),
        ("official_zig_compiler_path", "/tmp/zig"),
        ("official_zig_compiler_sha256", "0" * 64),
        ("official_zig_compiler_bytes", ZIG_COMPILER_BYTES - 1),
        ("official_zig_compiler_executed", True),
        ("scanner_matrix_case_count", 1_023),
        ("scanner_preserved_nonoverflow_case_count", 959),
        ("scanner_overflow_case_count", 63),
        ("scanner_correction_applied", True),
        ("scanner_verbose_620_repaired", True),
        ("corrected_candidate_matching", "PASS"),
        ("verified_live_zig_activation", "PASS"),
        ("qualified_candidate_count", 1),
        ("candidate_correctness", "PASS"),
        ("winner_selected", True),
    ]
    for key, changed in mutations:
        altered = copy.deepcopy(original)
        altered[key] = changed
        expect_rejection(validate_synthetic, altered)
        rejected += 1
    for index in range(len(SUITES)):
        altered = copy.deepcopy(original)
        altered["suites"][index]["case_execution_count"] -= 1
        expect_rejection(validate_synthetic, altered)
        rejected += 1
    for changed in (
        "oracle/phase1/evidence/reference.json.gz",
        "oracle/phase2/evidence/build.tar.xz",
        "candidates/_zig_probe.so",
        "performance/final-holdout.json",
        "oracle/phase3/holdout-cases.json",
        "../GOAL.md",
        "/tmp/reference.json",
        "oracle//phase1.json",
    ):
        expect_rejection(checked_relative, changed)
        rejected += 1
    for raw in (
        b'{"x":1,"x":2}\n',
        b'{"x":NaN}\n',
        b'{"x":Infinity}\n',
        b'{"x":1}',
        b'{"x": 1}\n',
    ):
        expect_rejection(exact_json, raw, "adversarial synthetic document")
        rejected += 1
    expect_rejection(require_verified_zig_activation)
    rejected += 1
    return {"accepted": accepted, "rejected": rejected}


def synthetic_boundary_controls(effects: dict[str, int]) -> dict[str, int]:
    probes: tuple[tuple[str, Any, tuple[Any, ...]], ...] = (
        ("blocked_reads", builtins.open, ("never-open-source-only",)),
        ("blocked_reads", io.open, ("never-open-source-only",)),
        ("blocked_reads", _io.open, ("never-open-source-only",)),
        ("blocked_reads", os.open, ("never-open-source-only", os.O_RDONLY)),
        ("blocked_reads", os.read, (-1, 1)),
        ("blocked_writes", os.write, (-1, b"x")),
        ("blocked_writes", os.unlink, ("never-remove-source-only",)),
        ("blocked_processes", subprocess.Popen, (["never-start-source-only"],)),
        ("blocked_processes", subprocess.run, (["never-start-source-only"],)),
        ("blocked_native_loads", ctypes.CDLL, ("never-load-native-source-only",)),
        ("blocked_native_loads", _ctypes.dlopen, ("never-load-native-source-only",)),
        ("blocked_decompression", gzip.decompress, (b"never-inflate",)),
        ("blocked_decompression", zlib.decompress, (b"never-inflate",)),
        ("blocked_imports", importlib.import_module, ("candidates.zig_candidate",)),
        ("blocked_low_level_imports", _imp.create_dynamic, (None,)),
        ("blocked_threads", _thread.start_new_thread, (lambda: None, ())),
        ("blocked_network", socket.create_connection, (("127.0.0.1", 1),)),
        ("blocked_clocks", time.perf_counter, ()),
        ("blocked_clocks", time.sleep, (0,)),
    )
    rejected = 0
    for counter, function, arguments in probes:
        before = effects[counter]
        expect_rejection(function, *arguments)
        require(effects[counter] == before + 1,
                "physically prove each prohibited Zig source-only effect is blocked")
        rejected += 1
    return {"accepted": 0, "rejected": rejected}


def source_self_test() -> dict[str, Any]:
    with source_only_boundary() as effects:
        controls = synthetic_source_fault_controls()
        boundaries = synthetic_boundary_controls(effects)
        require(
            all(effects[name] == 0 for name in (
                "file_reads", "file_writes", "candidate_imports",
                "candidate_workers", "reference_workers", "source_builds",
                "native_activations", "native_promotions", "native_libraries_loaded",
                "interpreter_creations", "threads_started", "network_requests",
                "clock_samples", "hidden_cases_read", "benchmark_files_read",
            )),
            "never confuse a blocked adversarial probe with an actual external effect",
        )
        measured = copy.deepcopy(effects)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "family": FAMILY,
        "source_only": True,
        "synthetic_controls_accepted": controls["accepted"] + boundaries["accepted"],
        "synthetic_controls_rejected": controls["rejected"] + boundaries["rejected"],
        "source_only_effects": measured,
        "coordination_release_required": True,
        "live_activation_required": True,
        "live_activation_verified": False,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "archives_opened": 0,
        "archives_inflated": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def authenticate_owner_groups() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    raws: dict[str, bytes] = {}
    owners: dict[str, dict[str, Any]] = {}
    groups = (
        {"goal": GOAL, "phase_one": PHASE_ONE},
        ORIGINAL_PRODUCER,
        CORRECTED_REFERENCE,
        ZIG_SOURCES,
        {"official_zig_lock": OFFICIAL_ZIG_LOCK},
        HISTORICAL_V12_BUILD,
        HISTORICAL_ZIG_CAMPAIGN,
        SCANNER_REPAIR,
        V41_OWNERS,
        V42_OWNERS,
        RUST_V6_OWNERS,
        V43_OWNERS,
        V45_OWNERS,
        RUST_V7_OWNERS,
        PUBLIC_ENTRYPOINT_OWNERS,
        PUBLIC_ENTRYPOINT_SURFACE,
        ACTUAL_RUST_V6_FAILURE,
    )
    for group in groups:
        for owner in group.values():
            if owner.path in owners:
                require(owners[owner.path] == owner_record(owner),
                        "reject inconsistent repeated frozen source owners")
                continue
            raw, observed = read_owner(
                owner,
                private=owner in (
                    CORRECTED_REFERENCE["receipt"],
                    HISTORICAL_V12_BUILD["receipt"],
                    HISTORICAL_ZIG_CAMPAIGN["receipt"],
                ),
            )
            raws[owner.path] = raw
            owners[owner.path] = observed
    return raws, owners


def expected_protocol_document(options: argparse.Namespace, context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA + "-source-freeze",
        "version": 1,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; FIRST-PARTY ZIG CANDIDATE NOT RUN",
        "family": FAMILY,
        "goal": owner_record(GOAL),
        "python": {
            "version": "3.14.6",
            "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
            "isolated": True,
        },
        "source": {
            "worker": {
                "path": SOURCE_RELATIVE,
                "sha256": checked_digest(options.source_sha256, "Zig V1 worker"),
            },
            "runner": {
                "path": RUNNER_RELATIVE,
                "sha256": checked_digest(options.runner_source_sha256, "Zig V1 runner"),
            },
            "protocol": {
                "path": PROTOCOL_RELATIVE,
                "sha256": checked_digest(options.protocol_sha256, "Zig V1 protocol"),
            },
        },
        "phase_one": {
            "owner": owner_record(PHASE_ONE),
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "supplemental_cases_added": False,
        },
        "corrected_v4_original_producer": {
            "owners": {
                key: owner_record(owner) for key, owner in ORIGINAL_PRODUCER.items()
            },
            "family_count": SOURCE_FAMILY_COUNT,
            "source_owner_count": SOURCE_OWNER_COUNT,
            "source_inventory_is_not_candidate_execution": True,
        },
        "first_party_zig_family": {
            "source_owners": {
                key: owner_record(owner) for key, owner in ZIG_SOURCES.items()
            },
            "family_spec": copy.deepcopy(context["zig_family"]),
            "source_audit": copy.deepcopy(context["source_audit"]),
            "exact_official_zig_compiler": copy.deepcopy(
                context["official_zig_compiler"]
            ),
            "candidate_imported_by_source_freeze": False,
            "native_library_loaded_by_source_freeze": False,
        },
        "corrected_public_reference": copy.deepcopy(context["corrected_reference"]),
        "historical_zig_v12_build": copy.deepcopy(context["historical_build"]),
        "historical_zig_original_campaign": copy.deepcopy(context["historical_campaign"]),
        "scanner_capture_overflow_source_repair": copy.deepcopy(context["scanner_repair"]),
        "preserved_v41_history": copy.deepcopy(context["v41_history"]),
        "preserved_v42_history": copy.deepcopy(context["v42_history"]),
        "separately_frozen_rust_v6_history": copy.deepcopy(context["rust_v6_history"]),
        "preserved_actual_rust_v6_failure": copy.deepcopy(
            context["actual_rust_v6_failure"]
        ),
        "preserved_v43_failure_history": copy.deepcopy(context["v43_history"]),
        "separately_frozen_publication_safe_rust_v7": copy.deepcopy(
            context["rust_v7_history"]
        ),
        "expanded_public_entrypoint_oracle": copy.deepcopy(
            context["public_entrypoint"]
        ),
        "coordinator_released_current_v45_history": copy.deepcopy(
            context["v45_history"]
        ),
        "candidate_run_policy": {
            "candidate_matching_status": "NOT RUN",
            "candidate_qualified": False,
            "runnable_candidate_family_count": 0,
            "runnable_candidate_families": [],
            "future_exclusively_runnable_candidate_family": FAMILY,
            "verified_live_zig_activation": "NOT FROZEN; FAIL CLOSED",
            "historical_build_does_not_activate_native": True,
            "runner_builds_or_activates_native": False,
            "future_process_count_only_after_real_success": SUITE_COUNT,
            "future_one_distinct_real_worker_per_original_suite": True,
            "future_preserve_every_case_and_mismatch": True,
            "future_preserve_full_stdout_stderr_hashes": True,
            "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
            "maximum_retained_worker_stdout_bytes": MAX_CHILD_STDOUT_BYTES,
            "maximum_retained_worker_stderr_bytes": MAX_CHILD_STDERR_BYTES,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "matching_pass_requires_all_31237_original_cases": True,
            "missing_or_uncounted_case_fails_closed": True,
        },
        "from_scratch_policy": {
            "external_regex_package": "FORBIDDEN",
            "stdlib_matching_engine": "FORBIDDEN",
            "another_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "source_only_effects": source_zero_effects(),
        "candidate_correctness": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def verify_frozen_context(options: argparse.Namespace, *, include_document: bool = True) -> dict[str, Any]:
    require_coordination_release()
    raws, owners = authenticate_owner_groups()
    source_owner = Owner(SOURCE_RELATIVE, options.source_sha256, options.source_size_bytes)
    runner_owner = Owner(RUNNER_RELATIVE, options.runner_source_sha256, options.runner_source_size_bytes)
    protocol_owner = Owner(PROTOCOL_RELATIVE, options.protocol_sha256, options.protocol_size_bytes)
    for owner in (source_owner, runner_owner, protocol_owner):
        raw, observed = read_owner(owner)
        raws[owner.path] = raw
        owners[owner.path] = observed
    for owner in (
        source_owner, runner_owner, ORIGINAL_PRODUCER["source"],
        CORRECTED_REFERENCE["source"], HISTORICAL_V12_BUILD["source"],
        HISTORICAL_ZIG_CAMPAIGN["source"], SCANNER_REPAIR["source"],
        V41_OWNERS["source"], V42_OWNERS["source"], RUST_V6_OWNERS["source"],
        V43_OWNERS["source"], V45_OWNERS["source"],
        RUST_V7_OWNERS["source"], PUBLIC_ENTRYPOINT_OWNERS["source"],
        PUBLIC_ENTRYPOINT_SURFACE["entrypoint"],
    ):
        try:
            ast.parse(raws[owner.path].decode("utf-8", "strict"), filename=owner.path)
        except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
            raise CandidateGateError("reject invalid independently frozen source: " + owner.path) from error
    producer = exact_json(raws[ORIGINAL_PRODUCER["document"].path], "complete corrected V4 producer")
    zig_family = validate_v4_producer(producer)
    reference_receipt = exact_json(
        raws[CORRECTED_REFERENCE["receipt"].path], "actual corrected public reference receipt"
    )
    build_receipt = exact_json(
        raws[HISTORICAL_V12_BUILD["receipt"].path], "actual historical Zig V12 build receipt"
    )
    campaign_receipt = exact_json(
        raws[HISTORICAL_ZIG_CAMPAIGN["receipt"].path], "actual historical failed Zig receipt"
    )
    lock = exact_json(
        raws[OFFICIAL_ZIG_LOCK.path], "official stable Zig lock",
        canonical_required=False,
    )
    repair_document = exact_json(
        raws[SCANNER_REPAIR["document"].path], "actual unapplied scanner source repair"
    )
    v41_summary = exact_json(raws[V41_OWNERS["summary"].path], "preserved complete V41 graph")
    v42_summary = exact_json(raws[V42_OWNERS["summary"].path], "coordinator-released complete V42 graph")
    v43_summary = exact_json(
        raws[V43_OWNERS["summary"].path],
        "published complete V43 actual Rust preflight failure history",
    )
    v45_summary = exact_json(
        raws[V45_OWNERS["summary"].path],
        "coordinator-released current complete V45 public-entrypoint graph",
    )
    rust_v6_document = exact_json(
        raws[RUST_V6_OWNERS["document"].path],
        "coordinator-released complete Rust V6 source freeze",
    )
    rust_v7_document = exact_json(
        raws[RUST_V7_OWNERS["document"].path],
        "publication-safe complete Rust V7 source freeze",
    )
    rust_v6_failure = exact_json(
        raws[ACTUAL_RUST_V6_FAILURE["failure"].path],
        "actual small preserved Rust V6 preflight failure",
    )
    rust_v6_observation = exact_json(
        raws[ACTUAL_RUST_V6_FAILURE["observation"].path],
        "actual small independent Rust V6 archive-effect observation",
        canonical_required=False,
    )
    public_entrypoint_document = exact_json(
        raws[PUBLIC_ENTRYPOINT_OWNERS["document"].path],
        "complete frozen 32-case public-entrypoint source oracle",
        canonical_required=False,
    )
    context = {
        "zig_family": zig_family,
        "source_audit": validate_candidate_source_audit(
            raws[ZIG_SOURCES["adapter"].path],
            raws[ZIG_SOURCES["engine"].path],
            raws[ZIG_SOURCES["bridge"].path],
        ),
        "corrected_reference": validate_corrected_reference(
            reference_receipt,
            producer.get("corrected_candidate_context_public_type_reference"),
        ),
        "historical_build": validate_historical_build(build_receipt, lock),
        "historical_campaign": validate_historical_campaign(campaign_receipt),
        "scanner_repair": validate_scanner_repair(
            repair_document, raws[ZIG_SOURCES["adapter"].path]
        ),
        "v41_history": validate_v41_history(v41_summary),
        "v42_history": validate_v42_history(v42_summary),
        "rust_v6_history": validate_rust_v6_source_freeze(rust_v6_document),
        "actual_rust_v6_failure": validate_actual_rust_v6_failure(
            rust_v6_failure, rust_v6_observation
        ),
        "v43_history": validate_v43_history(v43_summary),
        "rust_v7_history": validate_rust_v7_source_freeze(rust_v7_document),
        "public_entrypoint": validate_public_entrypoint_oracle(
            public_entrypoint_document,
            raws[PUBLIC_ENTRYPOINT_SURFACE["entrypoint"].path],
        ),
        "v45_history": validate_v45_history(v45_summary),
        "official_zig_compiler": authenticate_official_zig_compiler(),
    }
    expected = expected_protocol_document(options, context)
    if include_document:
        document_owner = Owner(
            DOCUMENT_RELATIVE, options.document_sha256, options.document_size_bytes
        )
        document_raw, document_record = read_owner(document_owner)
        document = exact_json(document_raw, "complete first-party Zig V1 candidate contract")
        require(canonical(document) == canonical(expected),
                "reject changed Zig family, coordinator history, cases, reference, repair, or fail-closed policy")
        owners[document_owner.path] = document_record
    return {
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS",
        "family": FAMILY,
        "case_execution_denominator": CASE_DENOMINATOR,
        "suite_count": SUITE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "authenticated_source_owner_count": len(owners),
        "authenticated_source_owners": [owners[key] for key in sorted(owners)],
        "corrected_reference": context["corrected_reference"],
        "historical_zig_build": context["historical_build"],
        "historical_zig_campaign": context["historical_campaign"],
        "scanner_repair": context["scanner_repair"],
        "v41_history": context["v41_history"],
        "v42_history": context["v42_history"],
        "rust_v6_history": context["rust_v6_history"],
        "actual_rust_v6_failure": context["actual_rust_v6_failure"],
        "v43_history": context["v43_history"],
        "rust_v7_history": context["rust_v7_history"],
        "public_entrypoint": context["public_entrypoint"],
        "v45_history": context["v45_history"],
        "official_zig_compiler": context["official_zig_compiler"],
        "expected_protocol_document": expected,
        "candidate_matching_status": "NOT RUN",
        "live_activation_status": "NOT FROZEN; FAIL CLOSED",
        "source_only_effects": source_zero_effects(),
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def render_frozen_contract(options: argparse.Namespace) -> dict[str, Any]:
    require_coordination_release()
    return verify_frozen_context(options, include_document=False)["expected_protocol_document"]


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    if arguments is None:
        arguments = sys.argv[1:]
    require(isinstance(arguments, (list, tuple)) and all(type(item) is str for item in arguments),
            "require one unambiguous Zig V1 worker command")
    flags = [item for item in arguments if item.startswith("--")]
    require(len(flags) == len(set(flags)), "reject duplicate or ambiguous Zig worker authorizations")
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=(FAMILY,))
    parser.add_argument("--suite", choices=tuple(name for name, _ in SUITES))
    parser.add_argument("--label")
    for name in ("source", "runner-source", "protocol", "document"):
        parser.add_argument("--" + name + "-sha256")
        parser.add_argument("--" + name + "-size-bytes", type=int)
    for name in ("producer-source", "producer-protocol", "producer-document"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(list(arguments))
    hash_names = (
        "source_sha256", "runner_source_sha256", "protocol_sha256",
        "document_sha256", "producer_source_sha256",
        "producer_protocol_sha256", "producer_document_sha256",
    )
    size_names = (
        "source_size_bytes", "runner_source_size_bytes",
        "protocol_size_bytes", "document_size_bytes",
    )
    actual_names = ("candidate", "suite", "label")
    if options.self_test:
        require(all(getattr(options, name) is None for name in (*hash_names, *size_names, *actual_names)),
                "source-only self-tests never authorize an owner, candidate, worker, or activation")
        return options
    for name in (
        "source_sha256", "runner_source_sha256", "protocol_sha256",
        "producer_source_sha256", "producer_protocol_sha256", "producer_document_sha256",
    ):
        checked_digest(getattr(options, name), name)
    for name in ("source_size_bytes", "runner_source_size_bytes", "protocol_size_bytes"):
        value = getattr(options, name)
        require(type(value) is int and 0 < value <= MAX_SOURCE_BYTES,
                "independently pin complete owner bytes for " + name)
    require(
        options.producer_source_sha256 == ORIGINAL_PRODUCER["source"].sha256
        and options.producer_protocol_sha256 == ORIGINAL_PRODUCER["protocol"].sha256
        and options.producer_document_sha256 == ORIGINAL_PRODUCER["document"].sha256,
        "require all three actual corrected V4 producer pins; reject stale V3 and C-only workers",
    )
    if options.render_contract:
        require(options.document_sha256 is None and options.document_size_bytes is None
                and all(getattr(options, name) is None for name in actual_names),
                "contract generation cannot import, build, activate, or run a Zig candidate")
        return options
    checked_digest(options.document_sha256, "document_sha256")
    require(type(options.document_size_bytes) is int
            and 0 < options.document_size_bytes <= MAX_SOURCE_BYTES,
            "independently pin complete canonical Zig V1 contract bytes")
    if options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in actual_names),
                "source verification cannot select, activate, or run a candidate")
        return options
    require(options.candidate == FAMILY and options.suite is not None
            and type(options.label) is str and bool(options.label),
            "require an explicit first-party Zig family, original suite, and safe run label")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    options: argparse.Namespace | None = None
    try:
        runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = source_self_test()
        elif options.render_contract:
            result = render_frozen_contract(options)
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            # The live activation is a separate, presently absent prerequisite.
            # Never touch a native target, candidate module, archive, or process.
            require_verified_zig_activation()
            raise CandidateGateError(
                "ACTUAL ZIG V1 MATCHING IS NOT AUTHORIZED; VERIFIED ORIGINAL V4 "
                "SUITE OBSERVATION HAS NOT BEEN FROZEN"
            )
        sys.stdout.buffer.write(bounded_public_report(result))
        sys.stdout.buffer.flush()
        return 0 if options.render_contract or result.get("status") == "PASS" else 1
    except BaseException as error:
        result = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "family": FAMILY,
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "actual_native_libraries_loaded": 0,
            "archives_opened": 0,
            "archives_inflated": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_matching_status": "NOT RUN",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        try:
            sys.stdout.buffer.write(bounded_public_report(result))
            sys.stdout.buffer.flush()
        except BaseException:
            return 1
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
