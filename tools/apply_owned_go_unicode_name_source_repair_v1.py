#!/usr/bin/env python3
"""Freeze the observed Go UTF-8 group-name repair without running a candidate."""

from __future__ import annotations

import argparse
import ast
import builtins
import ctypes
from dataclasses import dataclass
import fcntl
import gzip
import hashlib
import importlib
import io
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
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-go-unicode-name-source-repair-v1"
SOURCE_RELATIVE = "tools/apply_owned_go_unicode_name_source_repair_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/GO-UNICODE-NAME-SOURCE-REPAIR-V1.md"
CONTRACT_RELATIVE = "oracle/phase2/go-unicode-name-source-repair-v1.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
MAX_OWNER_BYTES = 8 * 1024 * 1024
SUITE_COUNT = 13
CASE_DENOMINATOR = 31237
PRIVATE_WAIVER_COUNT = 13
V31_EVIDENCE_OWNERS = 151
V31_HISTORY_REFERENCES = 156
CURRENT_EVIDENCE_OWNERS = 153
CURRENT_HISTORY_REFERENCES = 158
SIGNATURE_CASE_COUNT = 50
GO_ORIGINAL_SHA256 = "6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192"
GO_ORIGINAL_BYTES = 53782
GO_DERIVED_SHA256 = "095fd5a69ab8c3667ba92dc1934bf91b650260f6e55f1ac876fd267f0d8bcf1a"
GO_DERIVED_BYTES = 53803
UPSTREAM_METHOD_SHA256 = "877192ec0ba4b1f74a044ec8c3d7fd475ad28529dc55ba3ff0a7f1ed0b9cb025"
UPSTREAM_METHOD_AST_SHA256 = "ef698b58e26a4876de31dce525d24e7bd88f874de85f76b623549cda414e6712"
GO_ARCHIVE_SHA256 = "af971b3387382862ebf084b1d48ff0a21f37084cb234fd9e776d721b3ca5aae0"
GO_ARCHIVE_BYTES = 9139062
GO_REPORT_PREFIX_SHA256 = "226fe9ccf85def9cd41457c0320f1a0670871df946a013d3f44ba6c1c652bede"
GO_REPORT_PREFIX_BYTES = 1048576
GO_REPORT_PREFIX_COMPRESSED_BYTES_READ = 77824
RUST_V4_ARCHIVE_SHA256 = "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f"
RUST_V4_ARCHIVE_BYTES = 3663299
PRIVATE_ROOT_PREFIX = "rebar-phase2-native-build-"
PHASE_NAMES = ("reference-a", "reference-b")


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int


GOAL = Owner(
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
)
PHASE_ONE = Owner(
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
COMMITTED_UPSTREAM = Owner(
    "oracle/cpython-3.14.6/test_re.py",
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
    150895,
)
EXTERNAL_UPSTREAM = Owner(
    "/tmp/rebar-cpython/cpython-3.14.6-upstream-source/Python-3.14.6/Lib/test/test_re.py",
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
    150895,
)
GO_OWNERS = (
    Owner("candidates/go/engine.go", GO_ORIGINAL_SHA256, GO_ORIGINAL_BYTES),
    Owner(
        "candidates/go/go.mod",
        "9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b",
        44,
    ),
    Owner(
        "candidates/go/py_bridge.c",
        "52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a",
        39373,
    ),
    Owner(
        "candidates/go_candidate.py",
        "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20",
        31049,
    ),
)
V31 = (
    Owner(
        "tools/render_candidate_current_overview_v31.py",
        "daea5423d47bc84ec0ff503c14bae17ecdff392a60db14c5c66c575e978de588",
        75072,
    ),
    Owner(
        "docs/evidence/candidate-current-overview-v31.inputs.json",
        "25f1ef2cdf7f3443f5924b9c9814c4f0864148ebdf243c92a1df12d1c5754900",
        80376,
    ),
    Owner(
        "docs/evidence/candidate-current-overview-v31.json",
        "6d6f8fa23022b9198255cd0836961d4f78cd2d4c5d4041734a82a1d9f9d2ec90",
        314023,
    ),
    Owner(
        "docs/evidence/candidate-current-overview-v31.svg",
        "23f89b7983d5154d9275dcfa029bfe2a5599ad339c80675efb7c5eabda587d1a",
        12509,
    ),
)
RUST_V4 = (
    Owner(
        "tools/run_owned_repaired_rust_original_campaign_v4.py",
        "7d63b397deddd5c23af075754fcb50f7b3bdfb44390269383aae7903d46b4dd0",
        176358,
    ),
    Owner(
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V4.md",
        "5296b7ed7c3ba37ce4e299924e9e9edae849bebcd0e92e828977ae9ac6c9e26b",
        7725,
    ),
    Owner(
        "oracle/phase2/repaired-rust-original-campaign-v4.json",
        "26e86429e1e437fc791401197fb8c6dd9cf399bb025bd027af5f9c2554d6f60b",
        14361,
    ),
)
RUST_V4_RECEIPT = Owner(
    "oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json",
    "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3",
    4674,
)
GO_CAMPAIGN_RECEIPT = Owner(
    "oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures-publication-receipt.json",
    "a7352b7028348941cf0655ddc0e973ae43c6498be91139d47eb4d3555f90b3da",
    4615,
)
GO_BUILD_RECEIPT = Owner(
    "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6-publication-receipt.json",
    "f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca",
    3262,
)
C_RECEIPT = Owner(
    "oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json",
    "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9",
    3482,
)
ZIG_RECEIPT = Owner(
    "oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json",
    "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba",
    4534,
)
ZIG_PREFLIGHT_RECEIPT = Owner(
    "oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json",
    "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23",
    1992,
)
GO_WORKER_CLASSIFIER = Owner(
    "tools/render_candidate_current_overview_v19.py",
    "8144272f7c91e3821306a4d3963c8e201c68b275cecacf80d5000dd98c502494",
    38801,
)
CALLABLE_OWNERS = (
    Owner(
        "tools/verify_python_re_callable_introspection_v1.py",
        "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653",
        75608,
    ),
    Owner(
        "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
        "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
        8952,
    ),
    Owner(
        "oracle/phase1/p0-callable-introspection-v1.json",
        "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
        14749,
    ),
)

SUITES = (
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
GO_SEMANTIC_SUITES = {
    "buffer_v3": 197,
    "managed_v1": 668,
    "original_bounded_v5": 38,
    "pep688_v4": 120,
    "public_surface_v19": 324,
    "public_v3": 153,
    "scanner_v3": 960,
    "substitution_v2": 2058,
}
GO_INFRASTRUCTURE_SUITES = (
    "scanner_verbose_v1",
    "public_types_v1",
    "shape_v2",
    "threaded_pattern_v1",
)

GO_IMPORT_BLOCK = b'''import (
\t"fmt"
\t"runtime/cgo"
\t"strconv"
\t"sync"
\t"sync/atomic"
\t"unsafe"
)
'''
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
    b"\t\tfor offset := 0; offset < len(name); offset++ {\n",
    1,
)
ORIGINAL_BLOCK_SHA256 = "acae2de40ef8cdb23d07d68b6226015420809df6ba8b6eaee96ffa3baa5004d5"
CORRECTED_BLOCK_SHA256 = "07908b618132c14c8815feaf4e860274c7bedeefeddc45185533f18a8abb49ec"
UTF8_VECTORS = (
    "ascii",
    "a1",
    "µ",
    "𝔘𝔫𝔦𝔠𝔬𝔡𝔢",
    "é",
    "变量",
    "a\u0301",
    "κόσμε",
    "𐐷name",
    "_µ",
)
REQUIRED_ENGINE_MARKERS = (
    b"package main\n",
    b'import "C"\n',
    GO_IMPORT_BLOCK,
    b"func (p *parser) parse(",
    b"func (c *compiler) translate(",
    b"func compileProgram(",
    b"func (value *program) executeAt(",
    b"func installUnicodeTables(",
    b"//export rebar_go_compile\n",
    b"//export rebar_go_release\n",
    b"//export rebar_go_group_count\n",
    b"//export rebar_go_flags\n",
    b"//export rebar_go_name_count\n",
    b"//export rebar_go_name_group\n",
    b"//export rebar_go_name_length\n",
    b"//export rebar_go_copy_name\n",
    b"//export rebar_go_execute\n",
)
FORBIDDEN_GO_TOKENS = (
    b'"regexp"',
    b'"regexp/',
    b'"github.com/',
    b'"gitlab.com/',
    b'"golang.org/',
    b"#cgo",
    b"go:linkname",
    b"dlopen(",
    b"dlsym(",
    b"pcre",
    b"oniguruma",
    b"hyperscan",
    b"_sre",
    b"rust_candidate",
    b"zig_candidate",
    b"cpp_candidate",
    b"fortran_candidate",
)


class RepairError(Exception):
    """The evidence, first-party source, or phase boundary was not genuine."""


class ForbiddenEffect(RepairError):
    """A synthetic source-only self-test physically blocked a real effect."""


def need(condition: object, explanation: str) -> None:
    if condition is not True:
        raise RepairError(explanation)


def digest(data: bytes) -> str:
    need(type(data) is bytes, "hash only complete immutable bytes")
    return hashlib.sha256(data).hexdigest()


def checked_sha256(value: object, label: str) -> str:
    need(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require an exact lower-case independently pinned SHA-256: " + label,
    )
    return value


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise RepairError("reject ambiguous or nonfinite frozen evidence") from error


def strict_json(data: bytes, label: str) -> dict[str, Any]:
    need(
        type(data) is bytes and 0 < len(data) <= MAX_OWNER_BYTES,
        "reject empty, oversized, or substituted JSON: " + label,
    )

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            need(type(key) is str and key not in result, "reject duplicate JSON keys: " + label)
            result[key] = value
        return result

    def nonfinite(value: str) -> Any:
        raise RepairError("reject nonfinite JSON value: " + value)

    try:
        result = json.loads(
            data.decode("utf-8", "strict"),
            object_pairs_hook=pairs,
            parse_constant=nonfinite,
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise RepairError("reject malformed frozen JSON: " + label) from error
    need(type(result) is dict and canonical(result) == data, "reject noncanonical JSON: " + label)
    return result


def checked_relative(value: object) -> tuple[str, ...]:
    need(
        type(value) is str
        and 0 < len(value) <= 512
        and "\\" not in value
        and "\x00" not in value,
        "reject an escaped source-owner path",
    )
    parsed = PurePosixPath(value)
    need(
        not parsed.is_absolute()
        and str(parsed) == value
        and 0 < len(parsed.parts) <= 12
        and all(part not in ("", ".", "..") for part in parsed.parts),
        "reject an absolute, noncanonical, or broad owner path",
    )
    return parsed.parts


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "require the exact isolated, bytecode-free CPython 3.14.6 source tool",
    )
    need(
        not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
        "never import a matching candidate in a Go source-only process",
    )


def owner_document(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size}


def read_owner(owner: Owner, *, external: bool = False) -> tuple[bytes, dict[str, Any]]:
    checked_sha256(owner.sha256, owner.path)
    need(
        type(owner.size) is int and 0 < owner.size <= MAX_OWNER_BYTES,
        "refuse an unbounded, absent, or oversized evidence owner",
    )
    need(not owner.path.endswith(".gz"), "never open any compressed matching archive")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    folders: list[int] = []
    handle: int | None = None
    try:
        if external:
            need(owner == EXTERNAL_UPSTREAM, "refuse every substituted external source")
            handle = os.open(owner.path, flags)
            visible = os.stat(owner.path, follow_symlinks=False)
        else:
            parts = checked_relative(owner.path)
            if parts[0] == "candidates":
                need(owner.path in {item.path for item in GO_OWNERS}, "never inspect another engine or a native target")
            folder = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
            folders.append(folder)
            for part in parts[:-1]:
                folder = os.open(part, flags | getattr(os, "O_DIRECTORY", 0), dir_fd=folder)
                folders.append(folder)
            handle = os.open(parts[-1], flags, dir_fd=folder)
            visible = os.stat(parts[-1], dir_fd=folder, follow_symlinks=False)
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and before.st_size == owner.size
            and not (stat.S_IMODE(before.st_mode) & 0o022)
            and (before.st_dev, before.st_ino, before.st_size, before.st_uid, before.st_nlink)
            == (visible.st_dev, visible.st_ino, visible.st_size, visible.st_uid, visible.st_nlink),
            "reject a symlinked, linked, exchanged, foreign, or writable owner: " + owner.path,
        )
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(handle, min(remaining, 1024 * 1024))
            need(type(chunk) is bytes and bool(chunk), "reject truncated descriptor-bound evidence")
            pieces.append(chunk)
            remaining -= len(chunk)
        need(os.read(handle, 1) == b"", "reject appended source evidence")
        data = b"".join(pieces)
        after = os.fstat(handle)
        need(
            (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_uid,
                before.st_nlink,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_uid,
                after.st_nlink,
                after.st_mtime_ns,
                after.st_ctime_ns,
            )
            and digest(data) == owner.sha256,
            "reject evidence changed during descriptor-bound authentication: " + owner.path,
        )
        return data, {
            "path": owner.path,
            "sha256": owner.sha256,
            "bytes": owner.size,
            "device": after.st_dev,
            "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
            "uid": after.st_uid,
            "nlink": after.st_nlink,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for folder in reversed(folders):
            os.close(folder)


def source_boundary() -> dict[str, Any]:
    return {
        "candidate_correctness": "NOT MEASURED",
        "corrected_go_matching": "NOT MEASURED",
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_processes_started": 0,
        "upstream_test_methods_executed": 0,
        "source_builds_started": 0,
        "compiler_processes_started": 0,
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "canonical_native_target_reads": 0,
        "canonical_native_target_stats": 0,
        "source_apply_count": 0,
        "workspace_mutations": 0,
        "matching_archive_bytes_read": 0,
        "matching_archive_uncompressed_bytes_read": 0,
        "matching_archives_opened": 0,
        "rust_v4_archive_bytes_read": 0,
        "go_archive_bytes_read": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "network_requests": 0,
        "threads_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "memory": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "final_holdout_opened": False,
        "final_comparison_cases_generated": False,
        "winner_selected": False,
    }


def baseline() -> dict[str, Any]:
    return {
        "full_case_denominator": CASE_DENOMINATOR,
        "suite_count": SUITE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "v31_repository_evidence_owner_count": V31_EVIDENCE_OWNERS,
        "v31_authenticated_reference_count": V31_HISTORY_REFERENCES,
        "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "authenticated_reference_count": CURRENT_HISTORY_REFERENCES,
        "qualified_candidate_count": 0,
        "historical_rust_status": "FAIL",
        "historical_rust_mismatch_count": 1087,
        "historical_rust_verified_passing_case_count": 7438,
        "current_rust_status": "FAIL",
        "current_rust_mismatch_count": 1036,
        "current_rust_verified_passing_case_count": 8965,
        "current_rust_worker_count": 13,
        "current_rust_infrastructure_failure_count": 0,
        "c_status": "FAIL",
        "c_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_status": "FAIL",
        "zig_mismatch_count": 2172,
        "zig_verified_passing_case_count": 2847,
        "zig_historical_preflight_worker_count": 0,
        "go_status": "FAIL",
        "go_mismatch_count": 4518,
        "go_verified_passing_case_count": 128,
        "go_worker_failure_count": 4,
        "go_worker_failure_suites": list(GO_INFRASTRUCTURE_SUITES),
        "go_output_limit_suite": "shape_v2",
        "go_output_limit_bytes": 64 * 1024 * 1024,
        "go_crash_count": 0,
        "go_timeout_count": 0,
        "go_native_crash_proven": False,
        "go_external_regex_dependency_count": 0,
        "go_cross_family_dependency_count": 0,
        "signature_case_count": SIGNATURE_CASE_COUNT,
        "signature_reference": "NOT RUN",
        "signature_candidate_matching": "NOT MEASURED",
        "signature_cases_included_in_original_denominator": False,
        "final_comparison_planned_case_count": 4194304,
        **source_boundary(),
    }


def validate_baseline(value: object) -> None:
    need(
        type(value) is dict and value == baseline(),
        "reject substituted 153/158 evidence, old Rust as current, hidden Go worker failures, changed tests, timing, archive reads, or an opened holdout",
    )


def validate_first_party_engine(data: bytes) -> None:
    need(type(data) is bytes and 0 < len(data) <= MAX_OWNER_BYTES, "require exact first-party Go source bytes")
    for marker in REQUIRED_ENGINE_MARKERS:
        need(data.count(marker) == 1, "require one original independent Go parser, compiler, executor, or export")
    lowered = data.lower()
    for token in FORBIDDEN_GO_TOKENS:
        need(token not in lowered, "reject an outside regular-expression engine, foreign package, or candidate: " + token.decode("ascii"))


def repaired_source(data: bytes, *, frozen: bool) -> bytes:
    validate_first_party_engine(data)
    need(
        len(ORIGINAL_COPY_BLOCK) == 571
        and digest(ORIGINAL_COPY_BLOCK) == ORIGINAL_BLOCK_SHA256
        and len(CORRECTED_COPY_BLOCK) == 592
        and digest(CORRECTED_COPY_BLOCK) == CORRECTED_BLOCK_SHA256,
        "reject the exact full first-party Go UTF-8 export anchors",
    )
    if frozen:
        need(
            len(data) == GO_ORIGINAL_BYTES and digest(data) == GO_ORIGINAL_SHA256,
            "reject a modified or substituted original Go engine",
        )
    need(
        data.count(ORIGINAL_COPY_BLOCK) == 1
        and data.count(CORRECTED_COPY_BLOCK) == 0
        and data.count(b"\t\tfor offset := range name {\n") == 1,
        "require exactly one complete, unmodified original UTF-8 name export",
    )
    offset = data.index(ORIGINAL_COPY_BLOCK)
    prefix = data[:offset]
    suffix = data[offset + len(ORIGINAL_COPY_BLOCK) :]
    result = prefix + CORRECTED_COPY_BLOCK + suffix
    need(
        result.startswith(prefix)
        and result.endswith(suffix)
        and result.count(ORIGINAL_COPY_BLOCK) == 0
        and result.count(CORRECTED_COPY_BLOCK) == 1
        and result.count(b"\t\tfor offset := 0; offset < len(name); offset++ {\n") == 1,
        "never alter the parser, ABI, compiler, executor, bridge, or any unrelated source byte",
    )
    validate_first_party_engine(result)
    if frozen:
        need(
            len(result) == GO_DERIVED_BYTES and digest(result) == GO_DERIVED_SHA256,
            "derive only the independently pinned first-party Go repair",
        )
    return result


def verify_utf8_vectors() -> dict[str, Any]:
    need(len(UTF8_VECTORS) == 10, "never silently change the source-only UTF-8 vector denominator")
    historically_broken: list[str] = []
    corrected_names: list[str] = []
    byte_positions = 0
    for name in UTF8_VECTORS:
        need(type(name) is str and name.isidentifier(), "require a genuine Python identifier")
        expected = name.encode("utf-8", "strict")
        historical = bytearray(len(expected))
        offset = 0
        for character in name:
            historical[offset] = expected[offset]
            offset += len(character.encode("utf-8", "strict"))
        need(offset == len(expected), "preserve exact original rune-start offsets")
        corrected = bytearray(len(expected))
        for index in range(len(expected)):
            corrected[index] = expected[index]
            byte_positions += 1
        need(
            bytes(corrected) == expected
            and bytes(corrected).decode("utf-8", "strict") == name,
            "reject a missing continuation byte in the repaired Go export",
        )
        corrected_names.append(name)
        if bytes(historical) != expected:
            historically_broken.append(name)
    need(
        len(historically_broken) == 8
        and "µ" in historically_broken
        and "𝔘𝔫𝔦𝔠𝔬𝔡𝔢" in historically_broken
        and corrected_names == list(UTF8_VECTORS),
        "reproduce the archived non-ASCII defect without running Go or substituting the oracle",
    )
    historical_mu = bytearray(len("µ".encode("utf-8")))
    historical_mu[0] = "µ".encode("utf-8")[0]
    try:
        bytes(historical_mu).decode("utf-8", "strict")
    except UnicodeDecodeError as error:
        need(
            error.start == 0 and error.object[0] == 0xC2,
            "reproduce the actual archived leading-byte decoding failure",
        )
    else:
        raise RepairError("failed to reproduce the real invalid UTF-8 group name")
    return {
        "vector_count": len(UTF8_VECTORS),
        "historically_broken_vector_count": len(historically_broken),
        "historically_broken_vectors": historically_broken,
        "corrected_vectors": corrected_names,
        "verified_utf8_byte_positions": byte_positions,
        "actual_micro_sign_failure_reproduced": True,
        "actual_astral_identifier_preserved": True,
        "source_only": True,
        "candidate_run": False,
    }


def validate_upstream_test(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8", "strict")
        tree = ast.parse(text, filename=COMMITTED_UPSTREAM.path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise RepairError("reject the genuine frozen CPython test source") from error
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ReTests"]
    need(len(classes) == 1, "require the one actual upstream ReTests class")
    methods = [
        node
        for node in classes[0].body
        if isinstance(node, ast.FunctionDef) and node.name == "test_symbolic_groups"
    ]
    need(len(methods) == 1, "require the actual upstream Unicode symbolic-group method")
    method = methods[0]
    source = ast.get_source_segment(text, method)
    need(
        type(source) is str
        and method.lineno == 282
        and method.end_lineno == 293
        and digest(source.encode("utf-8")) == UPSTREAM_METHOD_SHA256
        and digest(ast.dump(method, include_attributes=False).encode("utf-8"))
        == UPSTREAM_METHOD_AST_SHA256,
        "reject a reconstructed, reordered, or substituted upstream Python method",
    )
    calls: list[tuple[int, str]] = []
    for node in ast.walk(method):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "re"
            and node.func.attr == "compile"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            calls.append((node.lineno, node.args[0].value))
    need(
        (288, "(?P<µ>x)(?P=µ)(?(µ)y)") in calls
        and (289, "(?P<𝔘𝔫𝔦𝔠𝔬𝔡𝔢>x)(?P=𝔘𝔫𝔦𝔠𝔬𝔡𝔢)(?(𝔘𝔫𝔦𝔠𝔬𝔡𝔢)y)") in calls,
        "derive both real non-ASCII identifiers from the original upstream source AST",
    )
    return {
        "test": "ReTests.test_symbolic_groups",
        "method_start_line": method.lineno,
        "method_end_line": method.end_lineno,
        "observed_failure_line": 288,
        "method_source_sha256": UPSTREAM_METHOD_SHA256,
        "method_ast_sha256": UPSTREAM_METHOD_AST_SHA256,
        "micro_sign_pattern": "(?P<µ>x)(?P=µ)(?(µ)y)",
        "astral_pattern": "(?P<𝔘𝔫𝔦𝔠𝔬𝔡𝔢>x)(?P=𝔘𝔫𝔦𝔠𝔬𝔡𝔢)(?(𝔘𝔫𝔦𝔠𝔬𝔡𝔢)y)",
        "upstream_test_executed": False,
    }


def observed_failure() -> dict[str, Any]:
    return {
        "suite": "original_bounded_v5",
        "suite_case_denominator": 151,
        "suite_mismatch_count": 38,
        "first_archived_original_mismatch": "ReTests.test_keep_buffer",
        "first_archived_original_mismatch_fixed_by_this_chunk": False,
        "targeted_archived_mismatch": "ReTests.test_symbolic_groups",
        "upstream_method_start_line": 282,
        "upstream_method_end_line": 293,
        "actual_failure_line": 288,
        "actual_candidate_adapter_line": 667,
        "actual_error_class": "UnicodeDecodeError",
        "actual_error_leading_byte": "0xc2",
        "actual_error_byte_position": 0,
        "actual_group_name": "µ",
        "actual_pattern": "(?P<µ>x)(?P=µ)(?(µ)y)",
        "separate_original_astral_pattern": "(?P<𝔘𝔫𝔦𝔠𝔬𝔡𝔢>x)(?P=𝔘𝔫𝔦𝔠𝔬𝔡𝔢)(?(𝔘𝔫𝔦𝔠𝔬𝔡𝔢)y)",
        "archive_sha256": GO_ARCHIVE_SHA256,
        "archive_compressed_bytes": GO_ARCHIVE_BYTES,
        "previously_read_uncompressed_prefix_bytes": GO_REPORT_PREFIX_BYTES,
        "previously_read_compressed_bytes": GO_REPORT_PREFIX_COMPRESSED_BYTES_READ,
        "previously_read_prefix_sha256": GO_REPORT_PREFIX_SHA256,
        "matching_archive_read_or_opened_during_source_freeze": False,
        "full_matching_archive_decompressed": False,
        "other_go_failure_root_causes": "NOT MEASURED",
        "corrected_go_matching": "NOT MEASURED",
    }


def repair_block_document() -> dict[str, Any]:
    return {
        "name": "owned-go-utf8-named-group-copy",
        "original_sha256": ORIGINAL_BLOCK_SHA256,
        "original_bytes": 571,
        "corrected_sha256": CORRECTED_BLOCK_SHA256,
        "corrected_bytes": 592,
        "original_occurrence_count": 1,
        "corrected_occurrence_count": 1,
        "original_line": 2125,
        "original_statement": "for offset := range name {",
        "corrected_statement": "for offset := 0; offset < len(name); offset++ {",
        "reason": "Go ranges strings by Unicode-rune start; the Python bridge requires every UTF-8 byte",
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_sha256(source_pin, "Go Unicode repair source")
    checked_sha256(protocol_pin, "Go Unicode repair explanation")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "phase": "SOURCE FREEZE; NO APPLICATION, BUILD, OR CANDIDATE RUN",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "goal": owner_document(GOAL),
        "runtime": {
            "implementation": "cpython",
            "version": "3.14.6",
            "python": PYTHON,
            "python_sha256": PYTHON_SHA256,
            "isolated": True,
            "bytecode_writes": False,
        },
        "phase_one": owner_document(PHASE_ONE),
        "upstream_oracle": {
            "committed_source": owner_document(COMMITTED_UPSTREAM),
            "separately_located_original_source": owner_document(EXTERNAL_UPSTREAM),
            "test": "ReTests.test_symbolic_groups",
            "method_start_line": 282,
            "method_end_line": 293,
            "failure_line": 288,
            "method_source_sha256": UPSTREAM_METHOD_SHA256,
            "method_ast_sha256": UPSTREAM_METHOD_AST_SHA256,
            "upstream_test_executed": False,
        },
        "observed_actual_go_failure": observed_failure(),
        "go_source": {
            "family": "go",
            "owner_count": len(GO_OWNERS),
            "owners": [owner_document(item) for item in GO_OWNERS],
            "source_build_receipt": owner_document(GO_BUILD_RECEIPT),
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "stdlib_re_delegation_allowed": False,
            "go_regexp_delegation_allowed": False,
            "go_module_dependency_count": 0,
            "original_native_parser_compiler_executor_preserved": True,
            "original_cgo_export_count": 9,
            "original_python_bridge_preserved": True,
            "original_python_adapter_preserved": True,
        },
        "repair": {
            "original": {
                "path": GO_OWNERS[0].path,
                "sha256": GO_ORIGINAL_SHA256,
                "bytes": GO_ORIGINAL_BYTES,
                "modified": False,
            },
            "derived": {
                "path": GO_OWNERS[0].path,
                "sha256": GO_DERIVED_SHA256,
                "bytes": GO_DERIVED_BYTES,
                "materialized": False,
            },
            "anchored_block_count": 1,
            "block": repair_block_document(),
            "source_only_utf8_vector_count": len(UTF8_VECTORS),
            "historically_broken_utf8_vector_count": 8,
            "preserve_ascii": True,
            "preserve_all_non_ascii_utf8_bytes": True,
            "preserve_astral_group_names": True,
            "preserve_combining_identifiers": True,
            "preserve_original_cgo_abi": True,
            "preserve_original_go_parser": True,
            "preserve_original_go_compiler": True,
            "preserve_original_go_executor": True,
            "preserve_original_python_bridge": True,
            "preserve_original_python_adapter": True,
            "change_buffer_lifetime": False,
            "external_regex_package_added": False,
            "stdlib_regex_engine_added": False,
            "cross_family_source_added": False,
            "candidate_matching_proven": False,
        },
        "published_history": {
            "v31": [owner_document(item) for item in V31],
            "v31_evidence_owner_count": V31_EVIDENCE_OWNERS,
            "v31_authenticated_reference_count": V31_HISTORY_REFERENCES,
            "corrected_rust_v4_source": [owner_document(item) for item in RUST_V4],
            "corrected_rust_v4_receipt": owner_document(RUST_V4_RECEIPT),
            "corrected_rust_v4_archive_verified_by_receipt_only": {
                "sha256": RUST_V4_ARCHIVE_SHA256,
                "bytes": RUST_V4_ARCHIVE_BYTES,
                "archive_opened": False,
                "archive_bytes_read": 0,
            },
            "actual_go_failure_receipt": owner_document(GO_CAMPAIGN_RECEIPT),
            "actual_go_worker_classifier": owner_document(GO_WORKER_CLASSIFIER),
            "actual_c_failure_receipt": owner_document(C_RECEIPT),
            "actual_zig_failure_receipt": owner_document(ZIG_RECEIPT),
            "historical_zig_preflight_receipt": owner_document(ZIG_PREFLIGHT_RECEIPT),
            "frozen_signature_source": [owner_document(item) for item in CALLABLE_OWNERS],
            "current": baseline(),
        },
        "apply_policy": {
            "explicit_apply_required": True,
            "independent_derived_sha256_required": True,
            "independent_derived_bytes_required": True,
            "snapshot_root_required": True,
            "private_parent": "/tmp",
            "private_root_prefix": PRIVATE_ROOT_PREFIX,
            "private_root_family_component": "-go-",
            "phase_names": list(PHASE_NAMES),
            "two_distinct_phase_directories_required": True,
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "destination_phase_relative": "go-engine-package/engine.go",
            "authenticated_private_go_module_required": True,
            "creation_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "existing_destination": "FORBIDDEN",
            "canonical_worktree_destination": "FORBIDDEN",
            "other_family_destination": "FORBIDDEN",
            "candidate_activation": "FORBIDDEN",
            "source_build": "FORBIDDEN",
        },
        "phase_boundary": source_boundary(),
    }


class SourceWall:
    """Make the synthetic test unable to perform its claimed forbidden effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {
            category: 0
            for category in (
                "filesystem",
                "write",
                "process",
                "import",
                "network",
                "thread",
                "clock",
                "native",
                "lock",
                "signal",
                "decompression",
            )
        }

    def deny(self, owner: Any, name: str, category: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise ForbiddenEffect("physically blocked " + category + ": " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceWall:
        for owner, names, category in (
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "resolve"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename", "replace", "fsync"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename", "replace"), "write"),
            (tempfile, ("mkdtemp", "mkstemp"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output"), "process"),
            (importlib, ("import_module",), "import"),
            (builtins, ("__import__",), "import"),
            (socket, ("socket", "create_connection"), "network"),
            (threading.Thread, ("start",), "thread"),
            (
                time,
                (
                    "time",
                    "time_ns",
                    "monotonic",
                    "monotonic_ns",
                    "perf_counter",
                    "perf_counter_ns",
                    "process_time",
                    "process_time_ns",
                    "sleep",
                ),
                "clock",
            ),
            (ctypes, ("CDLL", "PyDLL"), "native"),
            (fcntl, ("flock",), "lock"),
            (signal, ("signal", "pthread_sigmask"), "signal"),
            (gzip, ("open", "decompress", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        ):
            for name in names:
                self.deny(owner, name, category)
        return self

    def __exit__(self, *_args: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def synthetic_go_source() -> bytes:
    return (
        b'package main\n\nimport "C"\n\n'
        + GO_IMPORT_BLOCK
        + b"\nfunc (p *parser) parse() {}\n"
        + b"func (c *compiler) translate() {}\n"
        + b"func compileProgram() {}\n"
        + b"func (value *program) executeAt() {}\n"
        + b"func installUnicodeTables() {}\n"
        + b"//export rebar_go_compile\nfunc rebar_go_compile() {}\n"
        + b"//export rebar_go_release\nfunc rebar_go_release() {}\n"
        + b"//export rebar_go_group_count\nfunc rebar_go_group_count() {}\n"
        + b"//export rebar_go_flags\nfunc rebar_go_flags() {}\n"
        + b"//export rebar_go_name_count\nfunc rebar_go_name_count() {}\n"
        + b"//export rebar_go_name_group\nfunc rebar_go_name_group() {}\n"
        + b"//export rebar_go_name_length\nfunc rebar_go_name_length() {}\n"
        + ORIGINAL_COPY_BLOCK
        + b"//export rebar_go_execute\nfunc rebar_go_execute() {}\n"
    )


def validate_python_adapter(data: bytes) -> None:
    try:
        tree = ast.parse(data.decode("utf-8", "strict"), filename=GO_OWNERS[3].path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise RepairError("reject an invalid or delegated original Go adapter") from error
    own_bridge = 0
    banned_roots = {"re", "regex", "_sre", "regexp", "ctypes", "cffi", "subprocess"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                need(item.name.split(".", 1)[0] not in banned_roots, "reject an outside Go matching adapter")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            need(module.split(".", 1)[0] not in banned_roots, "reject a Python regex fallback")
            if module == "candidates":
                names = tuple(item.name for item in node.names)
                need(names == ("_go_bridge",), "never borrow another candidate engine")
                own_bridge += 1
    need(own_bridge == 1, "require exactly one original owned Go Python bridge import")


def self_test(source_pin: str, protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    expected = contract_document(source_pin, protocol_pin)
    need(
        digest(canonical(expected)) == checked_sha256(contract_pin, "canonical Go source contract"),
        "reject an independently substituted Go freeze contract",
    )
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: bool) -> None:
        need(condition, "reject a required positive source-only control: " + name)
        accepted.append(name)

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except (
            RepairError,
            OSError,
            ValueError,
            TypeError,
            SyntaxError,
            UnicodeError,
            RecursionError,
            OverflowError,
            KeyError,
        ):
            rejected.append(name)
            return
        raise RepairError("accepted hostile source-only Go evidence: " + name)

    with SourceWall() as wall:
        original = synthetic_go_source()
        corrected = repaired_source(original, frozen=False)
        vectors = verify_utf8_vectors()
        accept("preserve all 13 original suites", len(SUITES) == SUITE_COUNT)
        accept("preserve the complete 31,237-case denominator", sum(count for _, count in SUITES) == CASE_DENOMINATOR)
        accept("preserve the 13 named private waivers", baseline()["private_waiver_count"] == 13)
        accept("preserve the immutable 151/156 V31 history", baseline()["v31_repository_evidence_owner_count"] == 151 and baseline()["v31_authenticated_reference_count"] == 156)
        accept("preserve the actual current 153/158 evidence", baseline()["repository_evidence_owner_count"] == 153 and baseline()["authenticated_reference_count"] == 158)
        accept("preserve corrected Rust as failed", baseline()["current_rust_mismatch_count"] == 1036 and baseline()["current_rust_verified_passing_case_count"] == 8965)
        accept("preserve historical Rust separately", baseline()["historical_rust_mismatch_count"] == 1087)
        accept("preserve C and Zig as failed", baseline()["c_mismatch_count"] == 1230 and baseline()["zig_mismatch_count"] == 2172)
        accept("preserve all actual Go differences", baseline()["go_mismatch_count"] == 4518)
        accept("preserve all actual Go worker failures", baseline()["go_worker_failure_count"] == 4)
        accept("distinguish the intentional shape output kill", baseline()["go_output_limit_suite"] == "shape_v2" and baseline()["go_crash_count"] == 0)
        accept("preserve 50 unrun signatures", baseline()["signature_case_count"] == 50 and baseline()["signature_reference"] == "NOT RUN")
        accept("preserve exactly one complete historical Go name function", original.count(ORIGINAL_COPY_BLOCK) == 1)
        accept("correct exactly one complete historical Go name function", corrected.count(CORRECTED_COPY_BLOCK) == 1)
        accept("preserve every parser, compiler, executor, and native export", all(corrected.count(marker) == 1 for marker in REQUIRED_ENGINE_MARKERS))
        accept("reproduce the real invalid micro-sign UTF-8", vectors["actual_micro_sign_failure_reproduced"] is True)
        accept("preserve the real upstream astral identifier", vectors["actual_astral_identifier_preserved"] is True)
        accept("verify all ten source-only UTF-8 identifiers", vectors["vector_count"] == 10)
        accept("reproduce eight historical incomplete copies", vectors["historically_broken_vector_count"] == 8)
        accept("retain every original source byte outside the function", corrected.replace(CORRECTED_COPY_BLOCK, ORIGINAL_COPY_BLOCK, 1) == original)
        accept("never qualify untested Go", baseline()["corrected_go_matching"] == "NOT MEASURED")
        accept("never time a candidate", baseline()["performance"] == "NOT MEASURED")
        accept("keep the final holdout closed", baseline()["holdout"] == "NOT OPENED")
        validate_baseline(baseline())

        for label, hostile in (
            ("missing original exporter", original.replace(ORIGINAL_COPY_BLOCK, b"// removed\n")),
            ("duplicated original exporter", original.replace(ORIGINAL_COPY_BLOCK, ORIGINAL_COPY_BLOCK * 2)),
            ("already corrected exporter", corrected),
            ("changed rune increment", original.replace(b"for offset := range name {", b"for offset := range []rune(name) {")),
            ("off-by-one byte loop", original.replace(b"for offset := range name {", b"for offset := 0; offset <= len(name); offset++ {")),
            ("escaped destination policy", original.replace(b"target[offset] = C.uint8_t(name[offset])", b"target[offset] = C.uint8_t(name[0])")),
            ("synthetic source claimed as genuine owner", original),
        ):
            reject(
                "reject " + label,
                lambda data=hostile, genuine=label == "synthetic source claimed as genuine owner": repaired_source(data, frozen=genuine),
            )
        for index, marker in enumerate(REQUIRED_ENGINE_MARKERS):
            altered = original.replace(marker, b"/* missing first-party source anchor */\n", 1)
            reject("reject missing original Go semantic marker " + str(index), lambda data=altered: repaired_source(data, frozen=False))
        for index, token in enumerate(FORBIDDEN_GO_TOKENS):
            altered = original + b"\n" + token + b"\n"
            reject("reject external Go regex token " + str(index), lambda data=altered: repaired_source(data, frozen=False))
        for value in ("", "0" * 63, "0" * 65, "A" * 64, "g" * 64, None, 0, True):
            reject("reject unpinned independent SHA-256", lambda item=value: checked_sha256(item, "synthetic hostile digest"))
        for value in ("", "/tmp/escape", "../escape", "a/../b", "a//b", "a/./b", "./a", "a/", "a\\b", "x" * 513):
            reject("reject escaped source owner", lambda item=value: checked_relative(item))
        for data in (
            b'{"x":1,"x":2}\n',
            b'{"x":NaN}\n',
            b'{"x":Infinity}\n',
            b"[]\n",
            b'{"x":1}',
            b"",
            b"null\n",
        ):
            reject("reject hostile canonical JSON", lambda item=data: strict_json(item, "synthetic hostile JSON"))
        hostile_baseline = (
            ("full_case_denominator", 31236),
            ("suite_count", 12),
            ("private_waiver_count", 12),
            ("v31_repository_evidence_owner_count", 149),
            ("v31_authenticated_reference_count", 154),
            ("repository_evidence_owner_count", 151),
            ("authenticated_reference_count", 156),
            ("qualified_candidate_count", 1),
            ("historical_rust_mismatch_count", 1036),
            ("current_rust_mismatch_count", 1087),
            ("current_rust_verified_passing_case_count", 7438),
            ("current_rust_worker_count", 12),
            ("current_rust_infrastructure_failure_count", 1),
            ("c_mismatch_count", 1262),
            ("zig_mismatch_count", 0),
            ("go_status", "PASS"),
            ("go_mismatch_count", 4517),
            ("go_verified_passing_case_count", 129),
            ("go_worker_failure_count", 3),
            ("go_worker_failure_suites", []),
            ("go_output_limit_suite", "scanner_verbose_v1"),
            ("go_output_limit_bytes", 128 * 1024 * 1024),
            ("go_crash_count", 1),
            ("go_timeout_count", 1),
            ("go_native_crash_proven", True),
            ("go_external_regex_dependency_count", 1),
            ("go_cross_family_dependency_count", 1),
            ("signature_case_count", 51),
            ("signature_reference", "PASS"),
            ("signature_cases_included_in_original_denominator", True),
            ("candidate_correctness", "PASS"),
            ("corrected_go_matching", "PASS"),
            ("candidate_qualified", True),
            ("candidate_imports", 1),
            ("candidate_workers_started", 1),
            ("reference_processes_started", 1),
            ("source_builds_started", 1),
            ("compiler_processes_started", 1),
            ("native_activations", 1),
            ("native_libraries_loaded", 1),
            ("canonical_native_target_reads", 1),
            ("canonical_native_target_stats", 1),
            ("source_apply_count", 1),
            ("workspace_mutations", 1),
            ("matching_archive_bytes_read", 1),
            ("matching_archive_uncompressed_bytes_read", 1),
            ("matching_archives_opened", 1),
            ("rust_v4_archive_bytes_read", 1),
            ("go_archive_bytes_read", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("network_requests", 1),
            ("threads_started", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("performance", "FASTER"),
            ("memory", "ZERO"),
            ("undefined_behavior", "PASS"),
            ("holdout", "OPENED"),
            ("final_holdout_opened", True),
            ("final_comparison_cases_generated", True),
            ("winner_selected", True),
        )
        for key, value in hostile_baseline:
            altered = baseline()
            altered[key] = value
            reject("reject altered actual history or boundary: " + key, lambda item=altered: validate_baseline(item))

        probes = (
            ("filesystem", lambda: builtins.open("/tmp/rebar-go-unicode-forbidden", "rb")),
            ("filesystem", lambda: io.open("/tmp/rebar-go-unicode-forbidden", "rb")),
            ("filesystem", lambda: os.open("/tmp/rebar-go-unicode-forbidden", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("/tmp/rebar-go-unicode-forbidden")),
            ("filesystem", lambda: Path("/tmp/rebar-go-unicode-forbidden").read_bytes()),
            ("write", lambda: os.write(-1, b"forbidden")),
            ("write", lambda: tempfile.mkdtemp()),
            ("process", lambda: subprocess.run(("rebar-go-unicode-forbidden",))),
            ("import", lambda: importlib.import_module("candidates.go_candidate")),
            ("import", lambda: builtins.__import__("regexp")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("native", lambda: ctypes.CDLL("rebar-go-unicode-forbidden")),
            ("lock", lambda: fcntl.flock(-1, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden")),
            ("decompression", lambda: zlib.decompress(b"forbidden")),
        )
        for category, action in probes:
            before = wall.blocked[category]
            reject("physically block " + category, action)
            need(wall.blocked[category] == before + 1, "prove each claimed forbidden effect was physically blocked")
        blocked = dict(wall.blocked)
    need(
        len(accepted) >= 20
        and len(rejected) >= 100
        and all(amount > 0 for amount in blocked.values()),
        "require exhaustive real hostile controls and all physical source-only walls",
    )
    need(
        not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
        "never retain or import a matching candidate",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "version": 1,
        "mode": "SYNTHETIC SOURCE ONLY",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "blocked_effects_by_kind": blocked,
        "source_only_utf8_vector_count": vectors["vector_count"],
        "historically_broken_utf8_vector_count": vectors["historically_broken_vector_count"],
        "verified_utf8_byte_positions": vectors["verified_utf8_byte_positions"],
        "actual_micro_sign_failure_reproduced": True,
        "actual_astral_identifier_preserved": True,
        "original_engine_sha256": GO_ORIGINAL_SHA256,
        "derived_engine_sha256": GO_DERIVED_SHA256,
        "derived_engine_bytes": GO_DERIVED_BYTES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "authenticated_digest_addressed_history_paths": CURRENT_HISTORY_REFERENCES,
        "actual_rust_semantic_mismatch_count": 1036,
        "actual_rust_verified_passing_case_count": 8965,
        "actual_go_semantic_mismatch_count": 4518,
        "actual_go_verified_passing_case_count": 128,
        "actual_go_infrastructure_failure_count": 4,
        **source_boundary(),
    }


def read_contract_owners(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    result: list[dict[str, Any]] = []
    for relative, fingerprint in (
        (SOURCE_RELATIVE, source_pin),
        (PROTOCOL_RELATIVE, protocol_pin),
        (CONTRACT_RELATIVE, contract_pin),
    ):
        checked_relative(relative)
        checked_sha256(fingerprint, relative)
        visible = os.stat(str(ROOT / relative), follow_symlinks=False)
        owner = Owner(relative, fingerprint, visible.st_size)
        data, observed = read_owner(owner)
        result.append(observed)
        if relative == CONTRACT_RELATIVE:
            actual = strict_json(data, "caller-pinned Go Unicode freeze contract")
    expected = contract_document(source_pin, protocol_pin)
    need(
        actual == expected and digest(canonical(expected)) == contract_pin,
        "reject a changed, omitted, or substituted independently pinned source contract",
    )
    return expected, result


def validate_original_matrix(data: bytes) -> None:
    value = strict_json(data, "original CPython 3.14.6 P0 matrix")
    denominator = value.get("denominator")
    need(
        value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and isinstance(denominator, dict)
        and denominator.get("final_required_case_execution_denominator") == CASE_DENOMINATOR
        and denominator.get("frozen_planned_case_execution_denominator") == CASE_DENOMINATOR
        and denominator.get("private_upstream_methods_outside_public_denominator") == PRIVATE_WAIVER_COUNT
        and denominator.get("counted_suite_ids") == [name for name, _ in SUITES],
        "preserve all 31,237 real original cases, all 13 suites, and all 13 named waivers",
    )


def validate_signature_freeze(data: bytes) -> None:
    value = strict_json(data, "50 separately frozen callable signature obligations")
    obligation = value.get("additional_obligation")
    boundary = value.get("phase_boundary")
    future_reference = value.get("future_reference_policy")
    future_candidate = value.get("future_candidate_policy")
    need(
        value.get("schema") == "rebar-python-re-callable-introspection-v1-source-freeze"
        and value.get("version") == 1
        and value.get("status") == "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN"
        and isinstance(obligation, dict)
        and obligation.get("case_count") == SIGNATURE_CASE_COUNT
        and obligation.get("status") == "FROZEN; TWO INDEPENDENT REFERENCES NOT RUN"
        and obligation.get("included_in_original_31237_denominator") is False
        and isinstance(future_reference, dict)
        and future_reference.get("executed_in_source_freeze") is False
        and isinstance(future_candidate, dict)
        and future_candidate.get("executed_in_source_freeze") is False
        and isinstance(boundary, dict)
        and boundary.get("introspection_reference") == "NOT RUN"
        and boundary.get("candidate_introspection") == "NOT MEASURED"
        and boundary.get("actual_reference_roles_started") == 0
        and boundary.get("actual_candidate_workers_started") == 0
        and boundary.get("holdout") == "NOT OPENED"
        and boundary.get("performance") == "NOT MEASURED",
        "never count or claim an unrun 50-case callable reference or candidate",
    )


def validate_go_sources(raw: dict[str, bytes]) -> bytes:
    original = raw[GO_OWNERS[0].path]
    corrected = repaired_source(original, frozen=True)
    module = raw[GO_OWNERS[1].path]
    need(
        module == b"module rebar.local/candidates/go\n\ngo 1.26.0\n",
        "require exactly the original dependency-free first-party Go module",
    )
    bridge = raw[GO_OWNERS[2].path]
    for marker in (
        b"#include <Python.h>",
        b"extern uint64_t rebar_go_compile(",
        b"extern size_t rebar_go_copy_name(",
        b"PyUnicode_DecodeUTF8(",
        b"Py_MOD_PER_INTERPRETER_GIL_SUPPORTED",
        b"Py_MOD_GIL_USED",
    ):
        need(marker in bridge, "preserve the complete original interpreter-local Go C bridge")
    for token in (
        b'PyImport_ImportModule("re")',
        b'PyImport_ImportModule("_sre")',
        b'"regexp"',
        b"pcre",
        b"oniguruma",
        b"hyperscan",
    ):
        need(token.lower() not in bridge.lower(), "reject matching delegated from the Go bridge")
    validate_python_adapter(raw[GO_OWNERS[3].path])
    return corrected


def validate_v31_history(summary: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    need(
        summary.get("schema") == "rebar-candidate-current-overview-v31-summary"
        and summary.get("status") == "PASS"
        and summary.get("version") == 31
        and summary.get("full_case_denominator") == CASE_DENOMINATOR
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and summary.get("repository_evidence_owner_count") == V31_EVIDENCE_OWNERS
        and summary.get("authenticated_digest_addressed_history_paths") == V31_HISTORY_REFERENCES
        and summary.get("qualified_candidate_count") == 0
        and summary.get("rust_original_campaign_status") == "FAIL"
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087
        and summary.get("rust_original_campaign_verified_passing_case_count") == 7438
        and summary.get("c_original_campaign_status") == "FAIL"
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_status") == "FAIL"
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
        and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
        and summary.get("final_comparison_planned_case_count") == 4194304
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
        "preserve the exact immutable published 151/156 V31 history",
    )
    need(
        inputs.get("schema") == "rebar-candidate-current-overview-v31-inputs"
        and inputs.get("version") == 31
        and inputs.get("full_case_denominator") == CASE_DENOMINATOR
        and inputs.get("suite_count") == SUITE_COUNT
        and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and inputs.get("repository_evidence_owner_count") == V31_EVIDENCE_OWNERS
        and inputs.get("all_digest_addressed_history_path_count") == V31_HISTORY_REFERENCES
        and inputs.get("candidate_qualified_count") == 0
        and inputs.get("actual_rust_semantic_mismatch_count") == 1087
        and inputs.get("actual_rust_verified_passing_case_count") == 7438
        and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
        and inputs.get("c_original_campaign_verified_passing_case_count") == 7325
        and inputs.get("actual_zig_semantic_mismatch_count") == 2172
        and inputs.get("final_holdout_opened") is False
        and inputs.get("performance") == "NOT MEASURED",
        "preserve the actual separately authenticated published V31 inputs",
    )
    families = summary.get("families")
    need(isinstance(families, list), "require the published original candidate-family graph")
    go = [item for item in families if isinstance(item, dict) and item.get("family") == "go"]
    need(len(go) == 1, "require exactly one independently owned historical Go family")
    family = go[0]
    build = family.get("build_evidence")
    campaign = family.get("complete_v2_original_campaign")
    expected_owners = [
        {"path": owner.path, "sha256": owner.sha256}
        for owner in GO_OWNERS
    ]
    need(
        family.get("build_status") == "PASS"
        and family.get("matching_test_status") == "FAIL"
        and family.get("qualified") is False
        and family.get("performance") == "NOT MEASURED"
        and family.get("owned_sources") == expected_owners
        and isinstance(build, dict)
        and build.get("external_regex_dependency_count") == 0
        and build.get("cross_family_dependency_count") == 0
        and isinstance(campaign, dict)
        and campaign.get("status") == "FAIL"
        and campaign.get("completed_suite_count") == SUITE_COUNT
        and campaign.get("verified_passing_case_count") == 128
        and campaign.get("semantic_mismatch_count") == 4518
        and campaign.get("semantic_failure_suites") == GO_SEMANTIC_SUITES
        and campaign.get("infrastructure_failure_count") == 4
        and campaign.get("infrastructure_failure_suites") == list(GO_INFRASTRUCTURE_SUITES)
        and campaign.get("intentional_output_overflow_suite") == "shape_v2"
        and campaign.get("native_crash_proven") is False
        and campaign.get("crash_count") == 0
        and campaign.get("timeout_count") == 0
        and campaign.get("candidate_qualified") is False,
        "preserve all genuine Go mismatches and four worker failures without inventing a crash",
    )
    return campaign


def validate_receipts(
    rust: dict[str, Any],
    go: dict[str, Any],
    go_build: dict[str, Any],
    c: dict[str, Any],
    zig: dict[str, Any],
    zig_preflight: dict[str, Any],
) -> None:
    rust_archive = rust.get("archive")
    need(
        rust.get("schema") == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
        and rust.get("status") == "PASS"
        and rust.get("publication_status") == "PASS"
        and rust.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and rust.get("family") == "rust"
        and rust.get("candidate_status") == "FAIL"
        and rust.get("candidate_qualified") is False
        and rust.get("suite_count") == SUITE_COUNT
        and rust.get("completed_suite_count") == SUITE_COUNT
        and rust.get("case_execution_denominator") == CASE_DENOMINATOR
        and rust.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and rust.get("actual_candidate_workers") == SUITE_COUNT
        and rust.get("semantic_mismatch_count") == 1036
        and rust.get("verified_passing_case_count") == 8965
        and rust.get("infrastructure_failure_count") == 0
        and rust.get("historical_evidence_owner_count_before_publication") == V31_EVIDENCE_OWNERS
        and rust.get("historical_authenticated_reference_count_before_publication") == V31_HISTORY_REFERENCES
        and rust.get("new_repository_evidence_owner_count") == 2
        and rust.get("resulting_repository_evidence_owner_count") == CURRENT_EVIDENCE_OWNERS
        and rust.get("resulting_authenticated_reference_count") == CURRENT_HISTORY_REFERENCES
        and rust.get("campaign_source_sha256") == RUST_V4[0].sha256
        and rust.get("campaign_protocol_sha256") == RUST_V4[1].sha256
        and rust.get("campaign_contract_sha256") == RUST_V4[2].sha256
        and isinstance(rust_archive, dict)
        and rust_archive.get("sha256") == RUST_V4_ARCHIVE_SHA256
        and rust_archive.get("size_bytes") == RUST_V4_ARCHIVE_BYTES
        and rust_archive.get("mode") == 0o600
        and rust_archive.get("exclusive_creation") is True
        and rust_archive.get("same_inode_readback_verified") is True
        and rust_archive.get("streaming_readback_verified") is True
        and rust_archive.get("file_fsync_completed") is True
        and rust_archive.get("directory_fsync_completed") is True
        and rust.get("all_four_original_targets_restored") is True
        and rust.get("restoration_verified_before_publication") is True
        and rust.get("holdout") == "NOT OPENED"
        and rust.get("performance") == "NOT MEASURED"
        and rust.get("hidden_cases_read") == 0
        and rust.get("clock_samples") == 0
        and rust.get("timing_trials_run") == 0
        and rust.get("winner_selected") is False,
        "authenticate the genuine newer 1,036-mismatch Rust V4 and 153/158 history through its small receipt only",
    )
    go_archive = go.get("archive")
    need(
        go.get("schema") == "rebar-owned-six-family-original-p0-campaign-v2-durable-publication-receipt"
        and go.get("status") == "PASS"
        and go.get("candidate_status") == "FAIL"
        and go.get("candidate_family") == "go"
        and go.get("suite_count") == SUITE_COUNT
        and go.get("completed_suite_count") == SUITE_COUNT
        and go.get("case_execution_denominator") == CASE_DENOMINATOR
        and go.get("verified_passing_case_count") == 128
        and go.get("all_mismatches_crashes_and_timeouts_preserved") is True
        and isinstance(go_archive, dict)
        and go_archive.get("sha256") == GO_ARCHIVE_SHA256
        and go_archive.get("size_bytes") == GO_ARCHIVE_BYTES
        and go_archive.get("mode") == 0o600
        and go_archive.get("exclusive_creation") is True
        and go_archive.get("same_inode_readback_verified") is True
        and go_archive.get("streaming_readback_verified") is True
        and go_archive.get("file_fsync_completed") is True
        and go_archive.get("directory_fsync_completed") is True
        and go.get("holdout") == "NOT OPENED"
        and go.get("performance") == "NOT MEASURED"
        and go.get("hidden_cases_read") == 0
        and go.get("clock_samples") == 0
        and go.get("timing_trials_run") == 0
        and go.get("winner_selected") is False,
        "preserve the actual failing Go campaign without opening its matching archive",
    )
    expected_go_sources = {owner.path: owner.sha256 for owner in GO_OWNERS}
    need(
        go_build.get("schema") == "rebar-phase2-owned-native-source-build-v6-durable-publication-receipt"
        and go_build.get("status") == "PASS"
        and go_build.get("family") == "go"
        and go_build.get("build_status") == "PASS"
        and go_build.get("actual_v6_compiler_process_count") == 26
        and go_build.get("expected_v6_compiler_process_count") == 26
        and go_build.get("owned_source_sha256") == expected_go_sources
        and go_build.get("candidate_correctness") == "NOT MEASURED"
        and go_build.get("holdout") == "NOT OPENED"
        and go_build.get("performance") == "NOT MEASURED"
        and go_build.get("hidden_cases_read") == 0
        and go_build.get("clock_samples") == 0,
        "preserve the real dependency-free original Go build without calling it a passing regex",
    )
    need(
        c.get("schema") == "rebar-owned-repaired-c-original-campaign-v4-durable-publication-receipt"
        and c.get("status") == "PASS"
        and c.get("candidate_status") == "FAIL"
        and c.get("actual_candidate_workers") == SUITE_COUNT
        and c.get("completed_suite_count") == SUITE_COUNT
        and c.get("case_execution_denominator") == CASE_DENOMINATOR
        and c.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and c.get("semantic_mismatch_count") == 1230
        and c.get("verified_passing_case_count") == 7325
        and c.get("infrastructure_failure_count") == 0
        and c.get("candidate_qualified") is False
        and c.get("holdout") == "NOT OPENED",
        "preserve the latest separately tested 1,230-mismatch C engine",
    )
    need(
        zig.get("schema") == "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt"
        and zig.get("status") == "PASS"
        and zig.get("candidate_status") == "FAIL"
        and zig.get("actual_candidate_workers") == SUITE_COUNT
        and zig.get("completed_suite_count") == SUITE_COUNT
        and zig.get("case_execution_denominator") == CASE_DENOMINATOR
        and zig.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and zig.get("semantic_mismatch_count") == 2172
        and zig.get("verified_passing_case_count") == 2847
        and zig.get("infrastructure_failure_count") == 0
        and zig.get("candidate_qualified") is False
        and zig.get("holdout") == "NOT OPENED",
        "preserve the independently failed 2,172-mismatch Zig candidate",
    )
    need(
        zig_preflight.get("schema") == "rebar-owned-zig-campaign-preflight-failure-v1-durable-publication-receipt"
        and zig_preflight.get("status") == "PASS"
        and zig_preflight.get("preserved_failure_status") == "FAIL"
        and zig_preflight.get("actual_candidate_workers") == 0
        and zig_preflight.get("actual_matching_case_execution_count") == 0
        and zig_preflight.get("semantic_mismatch_count") == "NOT MEASURED"
        and zig_preflight.get("holdout") == "NOT OPENED",
        "preserve the distinct zero-worker historical Zig failure",
    )


def verify_frozen_context(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> tuple[dict[str, Any], bytes]:
    expected, frozen_owners = read_contract_owners(source_pin, protocol_pin, contract_pin)
    authenticated: list[dict[str, Any]] = []
    raw: dict[str, bytes] = {}
    support = (
        GOAL,
        PHASE_ONE,
        COMMITTED_UPSTREAM,
        *GO_OWNERS,
        *V31,
        *RUST_V4,
        RUST_V4_RECEIPT,
        GO_CAMPAIGN_RECEIPT,
        GO_BUILD_RECEIPT,
        C_RECEIPT,
        ZIG_RECEIPT,
        ZIG_PREFLIGHT_RECEIPT,
        GO_WORKER_CLASSIFIER,
        *CALLABLE_OWNERS,
    )
    need(len({owner.path for owner in support}) == len(support), "reject duplicated frozen support evidence")
    for owner in support:
        data, actual = read_owner(owner)
        raw[owner.path] = data
        authenticated.append(actual)
    external, external_owner = read_owner(EXTERNAL_UPSTREAM, external=True)
    need(external == raw[COMMITTED_UPSTREAM.path], "authenticate the exact byte-identical original upstream checkout")
    validate_original_matrix(raw[PHASE_ONE.path])
    witness = validate_upstream_test(external)
    vectors = verify_utf8_vectors()
    derived = validate_go_sources(raw)
    summary = strict_json(raw[V31[2].path], "genuine V31 summary")
    inputs = strict_json(raw[V31[1].path], "genuine V31 graph inputs")
    campaign = validate_v31_history(summary, inputs)
    rust = strict_json(raw[RUST_V4_RECEIPT.path], "corrected Rust V4 durable receipt")
    go = strict_json(raw[GO_CAMPAIGN_RECEIPT.path], "original failing Go durable receipt")
    go_build = strict_json(raw[GO_BUILD_RECEIPT.path], "original first-party Go build receipt")
    c = strict_json(raw[C_RECEIPT.path], "latest first-party C failure receipt")
    zig = strict_json(raw[ZIG_RECEIPT.path], "complete Zig failure receipt")
    preflight = strict_json(raw[ZIG_PREFLIGHT_RECEIPT.path], "historical zero-worker Zig receipt")
    validate_receipts(rust, go, go_build, c, zig, preflight)
    validate_signature_freeze(raw[CALLABLE_OWNERS[2].path])
    worker_classifier = raw[GO_WORKER_CLASSIFIER.path]
    need(
        b"process.get('returncode') in (0,1)" in worker_classifier
        and b"process.get('returncode')==-9" in worker_classifier
        and b"'OUTPUT-OVERFLOW INFRASTRUCTURE'" in worker_classifier
        and b"'unproven worker crash or misclassified bounded harness kill'" in worker_classifier,
        "preserve the separately proven Go harness-kill and non-crash classification",
    )
    validate_baseline(baseline())
    need(
        expected == contract_document(source_pin, protocol_pin)
        and not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
        "retain the caller-pinned source freeze without importing a candidate",
    )
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "version": 1,
        "mode": "READ-ONLY FIRST-PARTY SOURCE FREEZE",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "frozen_owner_count": len(frozen_owners),
        "authenticated_support_owner_count": len(authenticated),
        "authenticated_external_upstream_owner_count": 1,
        "authenticated_external_upstream": external_owner,
        "original_engine_sha256": GO_ORIGINAL_SHA256,
        "original_engine_bytes": GO_ORIGINAL_BYTES,
        "derived_engine_sha256": GO_DERIVED_SHA256,
        "derived_engine_bytes": GO_DERIVED_BYTES,
        "anchored_repair_block_count": 1,
        "original_full_export_sha256": ORIGINAL_BLOCK_SHA256,
        "corrected_full_export_sha256": CORRECTED_BLOCK_SHA256,
        "actual_observed_failure": witness,
        "source_only_utf8_vector_count": vectors["vector_count"],
        "historically_broken_utf8_vector_count": vectors["historically_broken_vector_count"],
        "verified_utf8_byte_positions": vectors["verified_utf8_byte_positions"],
        "actual_micro_sign_failure_reproduced": True,
        "actual_astral_identifier_preserved": True,
        "v31_repository_evidence_owner_count": V31_EVIDENCE_OWNERS,
        "v31_authenticated_reference_count": V31_HISTORY_REFERENCES,
        "repository_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "authenticated_digest_addressed_history_paths": CURRENT_HISTORY_REFERENCES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "actual_rust_semantic_mismatch_count": 1036,
        "actual_rust_verified_passing_case_count": 8965,
        "historical_rust_semantic_mismatch_count": 1087,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_zig_semantic_mismatch_count": 2172,
        "actual_go_semantic_mismatch_count": campaign["semantic_mismatch_count"],
        "actual_go_verified_passing_case_count": campaign["verified_passing_case_count"],
        "actual_go_infrastructure_failure_count": campaign["infrastructure_failure_count"],
        "actual_go_infrastructure_failure_suites": campaign["infrastructure_failure_suites"],
        "actual_go_output_overflow_suite": campaign["intentional_output_overflow_suite"],
        "go_native_crash_proven": False,
        "separately_frozen_signature_case_count": SIGNATURE_CASE_COUNT,
        "separately_frozen_signature_reference": "NOT RUN",
        "go_external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "rust_v4_archive_authenticated_by_small_receipt_only": True,
        "go_archive_authenticated_by_small_receipt_only": True,
        **source_boundary(),
    }
    return result, derived


def open_private_directory(parent: int, name: str) -> int:
    need(
        type(name) is str
        and bool(name)
        and name not in (".", "..")
        and "/" not in name
        and "\\" not in name,
        "reject an escaped or broad private Go phase directory",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    handle = os.open(name, flags, dir_fd=parent)
    try:
        current = os.fstat(handle)
        visible = os.stat(name, dir_fd=parent, follow_symlinks=False)
        need(
            stat.S_ISDIR(current.st_mode)
            and current.st_uid == os.geteuid()
            and stat.S_IMODE(current.st_mode) == 0o700
            and (current.st_dev, current.st_ino) == (visible.st_dev, visible.st_ino),
            "require an unchanged owner-only no-follow private Go phase",
        )
        return handle
    except BaseException:
        os.close(handle)
        raise


def private_module(package: int) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open("go.mod", flags, dir_fd=package)
    try:
        before = os.fstat(handle)
        visible = os.stat("go.mod", dir_fd=package, follow_symlinks=False)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and stat.S_IMODE(before.st_mode) == 0o600
            and before.st_nlink == 1
            and before.st_size == GO_OWNERS[1].size
            and (before.st_dev, before.st_ino) == (visible.st_dev, visible.st_ino),
            "require one fresh owner-only authenticated first-party Go module",
        )
        data = os.read(handle, GO_OWNERS[1].size)
        need(
            len(data) == GO_OWNERS[1].size
            and os.read(handle, 1) == b""
            and digest(data) == GO_OWNERS[1].sha256,
            "reject an external, modified, or truncated private Go module",
        )
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            "reject a private Go module changed during authentication",
        )
        return {
            "path": "go-engine-package/go.mod",
            "sha256": GO_OWNERS[1].sha256,
            "bytes": GO_OWNERS[1].size,
            "device": after.st_dev,
            "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        os.close(handle)


def apply_private(
    root: str,
    derived: bytes,
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> dict[str, Any]:
    need(type(root) is str and 0 < len(root) <= 512, "require an explicit independently pinned private Go package root")
    parsed = PurePosixPath(root)
    pieces = parsed.parts
    need(
        parsed.is_absolute()
        and str(parsed) == root
        and len(pieces) == 5
        and pieces[0] == "/"
        and pieces[1] == "tmp"
        and pieces[2].startswith(PRIVATE_ROOT_PREFIX)
        and "-go-" in pieces[2]
        and all(character.isascii() and (character.isalnum() or character in "-_") for character in pieces[2])
        and pieces[3] in PHASE_NAMES
        and pieces[4] == "go-engine-package",
        "never create a source outside a fresh owner-only Go native-build package phase",
    )
    need(
        type(derived) is bytes and len(derived) == GO_DERIVED_BYTES and digest(derived) == GO_DERIVED_SHA256,
        "require exactly the separately pinned corrected first-party Go source",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    temp = os.open("/tmp", flags)
    top: int | None = None
    phase: int | None = None
    sibling: int | None = None
    package: int | None = None
    sibling_package: int | None = None
    destination: int | None = None
    verifier: int | None = None
    try:
        top = open_private_directory(temp, pieces[2])
        phase = open_private_directory(top, pieces[3])
        sibling_name = "reference-b" if pieces[3] == "reference-a" else "reference-a"
        sibling = open_private_directory(top, sibling_name)
        first, second = os.fstat(phase), os.fstat(sibling)
        need(
            (first.st_dev, first.st_ino) != (second.st_dev, second.st_ino),
            "never alias the two independently owned Go source phases",
        )
        package = open_private_directory(phase, "go-engine-package")
        sibling_package = open_private_directory(sibling, "go-engine-package")
        first_package, second_package = os.fstat(package), os.fstat(sibling_package)
        need(
            (first_package.st_dev, first_package.st_ino)
            != (second_package.st_dev, second_package.st_ino),
            "never alias independent private Go package directories",
        )
        module = private_module(package)
        original, canonical_original = read_owner(GO_OWNERS[0])
        need(repaired_source(original, frozen=True) == derived, "refuse private application after canonical source substitution")
        destination = os.open(
            "engine.go",
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=package,
        )
        position = 0
        while position < len(derived):
            count = os.write(destination, derived[position:])
            need(type(count) is int and count > 0, "reject a partial private Go source write")
            position += count
        os.fsync(destination)
        written = os.fstat(destination)
        need(
            stat.S_ISREG(written.st_mode)
            and written.st_uid == os.geteuid()
            and stat.S_IMODE(written.st_mode) == 0o600
            and written.st_nlink == 1
            and written.st_size == GO_DERIVED_BYTES
            and (written.st_dev, written.st_ino)
            != (canonical_original["device"], canonical_original["inode"]),
            "require a new distinct 0600 no-follow private Go source inode",
        )
        verifier = os.open(
            "engine.go",
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=package,
        )
        observed = os.fstat(verifier)
        need(
            (observed.st_dev, observed.st_ino, observed.st_size)
            == (written.st_dev, written.st_ino, written.st_size),
            "reject a swapped private Go repair destination",
        )
        chunks: list[bytes] = []
        remaining = GO_DERIVED_BYTES
        while remaining:
            chunk = os.read(verifier, min(remaining, 1024 * 1024))
            need(type(chunk) is bytes and bool(chunk), "reject a truncated corrected Go private source")
            chunks.append(chunk)
            remaining -= len(chunk)
        need(
            os.read(verifier, 1) == b""
            and b"".join(chunks) == derived
            and digest(b"".join(chunks)) == GO_DERIVED_SHA256,
            "verify every byte of the exact corrected private Go engine",
        )
        os.fsync(package)
        unchanged, _ = read_owner(GO_OWNERS[0])
        need(unchanged == original, "never alter the canonical first-party Go engine")
        return {
            "schema": SCHEMA + "-private-source-application",
            "status": "PASS",
            "version": 1,
            "source_sha256": source_pin,
            "protocol_sha256": protocol_pin,
            "contract_sha256": contract_pin,
            "snapshot_root": root,
            "phase": pieces[3],
            "distinct_phase_count": 2,
            "private_module": module,
            "destination": {
                "relative": pieces[3] + "/go-engine-package/engine.go",
                "sha256": GO_DERIVED_SHA256,
                "bytes": GO_DERIVED_BYTES,
                "device": observed.st_dev,
                "inode": observed.st_ino,
                "mode": stat.S_IMODE(observed.st_mode),
                "uid": observed.st_uid,
                "nlink": observed.st_nlink,
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "file_fsync_completed": True,
                "directory_fsync_completed": True,
            },
            "canonical_source_unchanged": True,
            "source_apply_count": 1,
            "candidate_correctness": "NOT MEASURED",
            "corrected_go_matching": "NOT MEASURED",
            "source_builds_started": 0,
            "compiler_processes_started": 0,
            "candidate_workers_started": 0,
            "candidate_imports": 0,
            "native_activations": 0,
            "matching_archives_opened": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
    finally:
        for handle in (verifier, destination, sibling_package, package, sibling, phase, top, temp):
            if handle is not None:
                os.close(handle)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--emit-contract", "--render-contract", dest="emit_contract", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    parser.add_argument("--derived-source-sha256")
    parser.add_argument("--derived-source-bytes", type=int)
    options = parser.parse_args(arguments)
    checked_sha256(options.source_sha256, "Go Unicode repair source")
    checked_sha256(options.protocol_sha256, "Go Unicode repair protocol")
    if options.emit_contract:
        need(
            options.contract_sha256 is None
            and options.snapshot_root is None
            and options.derived_source_sha256 is None
            and options.derived_source_bytes is None,
            "contract rendering never authorizes a source application",
        )
    else:
        checked_sha256(options.contract_sha256, "Go Unicode canonical source contract")
        if options.apply:
            need(
                options.snapshot_root is not None
                and checked_sha256(options.derived_source_sha256, "independently pinned corrected Go engine")
                == GO_DERIVED_SHA256
                and options.derived_source_bytes == GO_DERIVED_BYTES,
                "require an explicit private Go root, independently pinned corrected digest, and complete byte count",
            )
        else:
            need(
                options.snapshot_root is None
                and options.derived_source_sha256 is None
                and options.derived_source_bytes is None,
                "never authorize a private source application from a read-only verification mode",
            )
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        runtime()
        options = parse_arguments(arguments)
        if options.emit_contract:
            output = contract_document(options.source_sha256, options.protocol_sha256)
        elif options.self_test:
            output = self_test(options.source_sha256, options.protocol_sha256, options.contract_sha256)
        elif options.verify_frozen_context:
            output, _ = verify_frozen_context(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
        else:
            _, derived = verify_frozen_context(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
            output = apply_private(
                options.snapshot_root,
                derived,
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
        sys.stdout.buffer.write(canonical(output))
        return 0
    except (
        RepairError,
        OSError,
        ValueError,
        TypeError,
        UnicodeError,
        SyntaxError,
        OverflowError,
        RecursionError,
        KeyError,
        AttributeError,
    ) as error:
        sys.stderr.write("owned Go Unicode-name source repair v1 rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
