#!/usr/bin/env python3
"""Freeze the observed first-party C++ public optional-argument correction."""

from __future__ import annotations

import argparse
import ast
import builtins
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import inspect
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re as isolated_reference_re
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Sequence
import warnings
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-phase2-owned-cpp-public-argument-source-repair-v1"
SOURCE_RELATIVE = "tools/apply_owned_cpp_public_argument_source_repair_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/CPP-PUBLIC-ARGUMENT-SOURCE-REPAIR-V1.md"
CONTRACT_RELATIVE = "oracle/phase2/cpp-public-argument-source-repair-v1.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
LIMIT = 8 * 1024 * 1024
SUITE_COUNT = 13
CASE_DENOMINATOR = 31237
PRIVATE_WAIVER_COUNT = 13
ADDITIVE_INTROSPECTION_CASE_COUNT = 50
V31_EVIDENCE_OWNERS = 151
V31_HISTORY_REFERENCES = 156
CURRENT_EVIDENCE_OWNERS = 153
CURRENT_HISTORY_REFERENCES = 158
ORIGINAL_SHA256 = "8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5"
ORIGINAL_BYTES = 27488
DERIVED_SHA256 = "aa4256725c75635d4e4e932b173d6d74ccd059bd867461ad6b0f5939306891c1"
DERIVED_BYTES = 28109
PRIVATE_ROOT_PREFIX = "rebar-phase2-cpp-public-argument-source-build-v1-"
PHASE_NAMES = ("reference-a", "reference-b")
OBSERVED_TEST = "ReTests.test_qualified_re_sub"
UPSTREAM_METHOD_LINE = 240
UPSTREAM_METHOD_END_LINE = 256
UPSTREAM_FAILURE_LINE = 253
UPSTREAM_METHOD_SHA256 = "16c182d4d8a4ea9e346f38d11aa3fc7db4a89415528b009b5f3b134fa5efabad"
UPSTREAM_METHOD_AST_SHA256 = "1f4bf7975be9aeb8b05a4a9cbc0ee0f45cde4b900cfd428eca510a452ce1d7bf"
OBSERVED_ACTUAL = "sub() takes at most 5 arguments"
OBSERVED_EXPECTED = "sub() takes from 3 to 5 positional arguments but 6 were given"
CPP_FAILURE_ARCHIVE_SHA256 = "0462adbd6ee7bafb274578462117513669de9b849473a2e1ada441407bc814a2"
CPP_FAILURE_ARCHIVE_BYTES = 3244833
CPP_FAILURE_ARCHIVE_UNCOMPRESSED_BYTES = 97639407
PREVIOUS_PREFIX_BYTES = 1048576
PREVIOUS_PREFIX_SHA256 = "66cb4ec2f314213676486261e170e8109190b3029553509de637beaa6038bb53"
CPP_INFRASTRUCTURE_SUITES = (
    "scanner_verbose_v1",
    "public_types_v1",
    "substitution_v2",
    "shape_v2",
    "threaded_pattern_v1",
)
CPP_SEMANTIC_SUITE_COUNTS = {
    "buffer_v3": 181,
    "managed_v1": 600,
    "original_bounded_v5": 43,
    "pep688_v4": 116,
    "public_surface_v19": 336,
    "public_v3": 40,
    "scanner_v3": 992,
}
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
EXPECTED_TEXT_SIGNATURES = {
    "split": "(pattern, string, maxsplit=0, flags=0)",
    "sub": "(pattern, repl, string, count=0, flags=0)",
    "subn": "(pattern, repl, string, count=0, flags=0)",
}


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
UPSTREAM_TEST = Owner(
    "oracle/cpython-3.14.6/test_re.py",
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
    150895,
)
SEPARATE_UPSTREAM_TEST = Owner(
    "/tmp/rebar-cpython/cpython-3.14.6-upstream-source/"
    "Python-3.14.6/Lib/test/test_re.py",
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
    150895,
)
INSTALLED_RE = Owner(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
    "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    17876,
)
CPP_OWNERS = (
    Owner("candidates/cpp_candidate.py", ORIGINAL_SHA256, ORIGINAL_BYTES),
    Owner(
        "candidates/cpp/engine.hpp",
        "66998fed1839f5e5f7f09382830ed9fda1a62b80bd545305c4eee95ed9a13df9",
        4089,
    ),
    Owner(
        "candidates/cpp/engine.cpp",
        "a9ceb37cfde77447a01a36a8882f7713faf5f201d7a15a193dd17e7b91d118f5",
        62813,
    ),
    Owner(
        "candidates/cpp/py_bridge.cpp",
        "1d930b63b2f9493dd4759b7521f75d8846daf2580a5699337fcf82540484ab6d",
        25068,
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
INDEPENDENCE = (
    Owner(
        "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md",
        "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b",
        6194,
    ),
    Owner(
        "oracle/phase2/candidate-independence-v2.json",
        "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659",
        8798,
    ),
)
CPP_CAMPAIGN = (
    Owner(
        "oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V1.md",
        "01d5908b9c1c3c356059a21cd0b418a7278559843d465e9062155b68f6497422",
        4249,
    ),
    Owner(
        "oracle/phase2/six-family-p0-campaign-v1.json",
        "c619e63dd18b8242bfc1af9e01030eff60e8d17128a83de216992b5cdc619801",
        19273,
    ),
    Owner(
        "tools/run_owned_six_family_original_p0_campaign_v1.py",
        "50ac9f549739bb6b540f1762177f25b46c1fa345dce717ea7163e15d98ae7e88",
        93832,
    ),
)
CPP_RECEIPT = Owner(
    "oracle/phase2/evidence/"
    "owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-"
    "failures-publication-receipt.json",
    "7b1156c07441acd579149ca9b3aedcb9308eb75a130ce7f7df98aa6a89d776f6",
    3936,
)
RUST_V4_ARCHIVE = Owner(
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-"
    "original-p0-failures.json.gz",
    "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f",
    3663299,
)
RUST_V4_RECEIPT = Owner(
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-"
    "original-p0-failures-publication-receipt.json",
    "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3",
    4674,
)
ADDITIVE_INTROSPECTION = (
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

OLD_OPTIONAL_BLOCK = b'''def split(pattern, string, *args, maxsplit=_MISSING, flags=_MISSING):
    if len(args) > 2:
        raise TypeError("split() takes at most 4 arguments")
    _deprecated_positional("maxsplit", args)
    if args:
        if maxsplit is not _MISSING:
            raise TypeError("split() got multiple values for argument 'maxsplit'")
        maxsplit = args[0]
    if len(args) == 2:
        if flags is not _MISSING:
            raise TypeError("split() got multiple values for argument 'flags'")
        flags = args[1]
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).split(string, 0 if maxsplit is _MISSING else maxsplit)


def sub(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    if len(args) > 2:
        raise TypeError("sub() takes at most 5 arguments")
    _deprecated_positional("count", args)
    if args:
        if count is not _MISSING:
            raise TypeError("sub() got multiple values for argument 'count'")
        count = args[0]
    if len(args) == 2:
        if flags is not _MISSING:
            raise TypeError("sub() got multiple values for argument 'flags'")
        flags = args[1]
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).sub(repl, string, 0 if count is _MISSING else count)


def subn(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    if len(args) > 2:
        raise TypeError("subn() takes at most 5 arguments")
    _deprecated_positional("count", args)
    if args:
        if count is not _MISSING:
            raise TypeError("subn() got multiple values for argument 'count'")
        count = args[0]
    if len(args) == 2:
        if flags is not _MISSING:
            raise TypeError("subn() got multiple values for argument 'flags'")
        flags = args[1]
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).subn(repl, string, 0 if count is _MISSING else count)
'''

CORRECTED_OPTIONAL_BLOCK = b'''def split(pattern, string, *args, maxsplit=_MISSING, flags=_MISSING):
    if args:
        if maxsplit is not _MISSING:
            raise TypeError("split() got multiple values for argument 'maxsplit'")
        maxsplit, *args = args
        if args:
            if flags is not _MISSING:
                raise TypeError("split() got multiple values for argument 'flags'")
            flags, *args = args
            if args:
                raise TypeError(
                    "split() takes from 2 to 4 positional arguments but "
                    f"{4 + len(args)} were given"
                )
        _deprecated_positional("maxsplit", (maxsplit,))
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).split(string, 0 if maxsplit is _MISSING else maxsplit)


split.__text_signature__ = "(pattern, string, maxsplit=0, flags=0)"


def sub(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    if args:
        if count is not _MISSING:
            raise TypeError("sub() got multiple values for argument 'count'")
        count, *args = args
        if args:
            if flags is not _MISSING:
                raise TypeError("sub() got multiple values for argument 'flags'")
            flags, *args = args
            if args:
                raise TypeError(
                    "sub() takes from 3 to 5 positional arguments but "
                    f"{5 + len(args)} were given"
                )
        _deprecated_positional("count", (count,))
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).sub(repl, string, 0 if count is _MISSING else count)


sub.__text_signature__ = "(pattern, repl, string, count=0, flags=0)"


def subn(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    if args:
        if count is not _MISSING:
            raise TypeError("subn() got multiple values for argument 'count'")
        count, *args = args
        if args:
            if flags is not _MISSING:
                raise TypeError("subn() got multiple values for argument 'flags'")
            flags, *args = args
            if args:
                raise TypeError(
                    "subn() takes from 3 to 5 positional arguments but "
                    f"{5 + len(args)} were given"
                )
        _deprecated_positional("count", (count,))
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).subn(repl, string, 0 if count is _MISSING else count)


subn.__text_signature__ = "(pattern, repl, string, count=0, flags=0)"
'''


class RepairError(Exception):
    """A frozen source owner, actual witness, or phase boundary failed."""


class ForbiddenEffect(RepairError):
    """A real external effect was physically blocked by the source wall."""


def need(value: object, message: str) -> None:
    if value is not True:
        raise RepairError(message)


def sha256(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only exact immutable bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_sha256(value: object, label: str) -> str:
    need(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "reject a substituted or noncanonical SHA-256: " + label,
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
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject ambiguous canonical evidence") from exc


def strict_json(
    raw: bytes,
    label: str,
    *,
    require_canonical: bool = True,
) -> dict[str, Any]:
    need(type(raw) is bytes and 0 < len(raw) <= LIMIT, "reject invalid evidence: " + label)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            need(type(key) is str and key not in result, "reject duplicate keys: " + label)
            result[key] = value
        return result

    def reject_nonfinite(value: str) -> Any:
        raise RepairError("reject nonfinite evidence: " + value)

    try:
        result = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=pairs,
            parse_constant=reject_nonfinite,
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise RepairError("reject malformed evidence: " + label) from exc
    need(type(result) is dict, "reject non-object evidence: " + label)
    if require_canonical:
        need(canonical(result) == raw, "reject noncanonical evidence: " + label)
    return result


def owner_document(owner: Owner) -> dict[str, Any]:
    return {"path": owner.path, "sha256": owner.sha256, "bytes": owner.size}


def checked_relative(path: object) -> tuple[str, ...]:
    need(
        type(path) is str
        and 0 < len(path) <= 512
        and "\\" not in path
        and "\x00" not in path,
        "reject an escaped source owner",
    )
    parsed = PurePosixPath(path)
    need(
        not parsed.is_absolute()
        and str(parsed) == path
        and 0 < len(parsed.parts) <= 12
        and all(item not in ("", ".", "..") for item in parsed.parts),
        "reject an absolute, ambiguous, or escaped source owner",
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
        "require the exact isolated, bytecode-free stable CPython 3.14.6",
    )
    need(
        os.path.abspath(isolated_reference_re.__file__) == INSTALLED_RE.path,
        "require the authenticated pinned CPython reference only",
    )
    need(
        not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
        "never import a candidate or native engine in a source-only oracle",
    )


def read_owner(owner: Owner, *, external: bool = False) -> tuple[bytes, dict[str, Any]]:
    checked_sha256(owner.sha256, owner.path)
    need(type(owner.size) is int and 0 < owner.size <= LIMIT, "reject an unbounded owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    handle: int | None = None
    try:
        if external:
            need(
                owner.path in {INSTALLED_RE.path, SEPARATE_UPSTREAM_TEST.path},
                "reject an unauthorized host or upstream source",
            )
            handle = os.open(owner.path, flags)
            visible = os.stat(owner.path, follow_symlinks=False)
        else:
            parts = checked_relative(owner.path)
            if parts[0] == "candidates":
                need(owner in CPP_OWNERS, "never inspect a native target or another candidate")
            if owner.path.endswith(".gz"):
                need(owner == RUST_V4_ARCHIVE, "never reopen a matching-failure archive")
            directory = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
            descriptors.append(directory)
            for part in parts[:-1]:
                directory = os.open(
                    part,
                    flags | getattr(os, "O_DIRECTORY", 0),
                    dir_fd=directory,
                )
                descriptors.append(directory)
            handle = os.open(parts[-1], flags, dir_fd=directory)
            visible = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and before.st_size == owner.size
            and (before.st_dev, before.st_ino, before.st_uid, before.st_nlink, before.st_size)
            == (visible.st_dev, visible.st_ino, visible.st_uid, visible.st_nlink, visible.st_size),
            "reject a linked, exchanged, truncated, or foreign owner: " + owner.path,
        )
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(handle, min(remaining, 1024 * 1024))
            need(type(chunk) is bytes and bool(chunk), "reject a truncated immutable owner")
            chunks.append(chunk)
            remaining -= len(chunk)
        need(os.read(handle, 1) == b"", "reject appended source evidence")
        raw = b"".join(chunks)
        after = os.fstat(handle)
        need(
            (
                before.st_dev,
                before.st_ino,
                before.st_uid,
                before.st_nlink,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_uid,
                after.st_nlink,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
            )
            and sha256(raw) == owner.sha256,
            "reject an owner changed during descriptor-bound verification: " + owner.path,
        )
        return raw, {
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
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def boundary() -> dict[str, Any]:
    return {
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "candidate_matching_operations": 0,
        "reference_processes_started": 0,
        "upstream_unittest_methods_executed": 0,
        "source_builds_started": 0,
        "compiler_processes_started": 0,
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "source_apply_count": 0,
        "workspace_mutations": 0,
        "canonical_native_target_reads": 0,
        "canonical_native_target_stats": 0,
        "cpp_matching_archive_opened": False,
        "cpp_matching_archive_uncompressed_bytes_read": 0,
        "rust_matching_archive_decompressed": False,
        "rust_matching_archive_uncompressed_bytes_read": 0,
        "c_matching_archive_uncompressed_bytes_read": 0,
        "zig_matching_archive_uncompressed_bytes_read": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "network_requests": 0,
        "threads_started": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
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
        "historical_v31_evidence_owner_count": V31_EVIDENCE_OWNERS,
        "historical_v31_authenticated_reference_count": V31_HISTORY_REFERENCES,
        "current_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "current_authenticated_reference_count": CURRENT_HISTORY_REFERENCES,
        "qualified_candidate_count": 0,
        "cpp_status": "FAIL",
        "cpp_passing_suite_count": 1,
        "cpp_failing_suite_count": 12,
        "cpp_verified_passing_case_count": 128,
        "cpp_semantic_mismatch_count": 2308,
        "cpp_semantic_failure_suite_count": 7,
        "cpp_infrastructure_failure_suite_count": 5,
        "cpp_crash_count": 0,
        "cpp_timeout_count": 0,
        "cpp_semantic_failure_suite_counts": dict(CPP_SEMANTIC_SUITE_COUNTS),
        "cpp_infrastructure_failure_suites": list(CPP_INFRASTRUCTURE_SUITES),
        "c_status": "FAIL",
        "c_semantic_mismatch_count": 1230,
        "zig_status": "FAIL",
        "zig_semantic_mismatch_count": 2172,
        "v31_historical_rust_semantic_mismatch_count": 1087,
        "current_rust_status": "FAIL",
        "current_rust_semantic_mismatch_count": 1036,
        "current_rust_verified_passing_case_count": 8965,
        "current_rust_candidate_workers": 13,
        "current_rust_infrastructure_failure_count": 0,
        "additive_introspection_case_count": ADDITIVE_INTROSPECTION_CASE_COUNT,
        "additive_introspection_reference": "NOT RUN",
        "additive_introspection_candidate": "NOT RUN",
        "final_comparison_planned_case_count": 4194304,
        **boundary(),
    }


def validate_baseline(value: object) -> None:
    need(
        type(value) is dict and value == baseline(),
        "reject stale history, altered C++ failures, an opened holdout, "
        "candidate execution, benchmark timing, or a false qualification",
    )


def repaired_source(raw: bytes, *, frozen: bool) -> bytes:
    need(type(raw) is bytes and 0 < len(raw) <= LIMIT, "require complete C++ public source")
    if frozen:
        need(
            len(raw) == ORIGINAL_BYTES and sha256(raw) == ORIGINAL_SHA256,
            "reject a substituted canonical C++ public adapter",
        )
    need(
        raw.count(OLD_OPTIONAL_BLOCK) == 1
        and raw.count(CORRECTED_OPTIONAL_BLOCK) == 0,
        "require exactly one unchanged observed optional-argument source block",
    )
    offset = raw.index(OLD_OPTIONAL_BLOCK)
    prefix = raw[:offset]
    suffix = raw[offset + len(OLD_OPTIONAL_BLOCK) :]
    derived = prefix + CORRECTED_OPTIONAL_BLOCK + suffix
    need(
        derived.startswith(prefix)
        and derived.endswith(suffix)
        and derived.count(OLD_OPTIONAL_BLOCK) == 0
        and derived.count(CORRECTED_OPTIONAL_BLOCK) == 1,
        "change only the uniquely anchored three public optional-argument functions",
    )
    forbidden = (
        b"import re\n",
        b"from re import",
        b"import _sre",
        b"from _sre",
        b"std::regex",
        b"boost::regex",
        b"pcre",
        b"oniguruma",
        b"candidates.rust_candidate",
        b"candidates.zig_candidate",
        b"candidates.vm_candidate",
        b"candidates.go_candidate",
        b"candidates.fortran_candidate",
        b"subprocess",
        b"ctypes",
    )
    for marker in forbidden:
        need(
            marker not in raw and marker not in derived,
            "reject a delegated regex engine, package, fallback, or another family",
        )
    try:
        tree = ast.parse(derived.decode("utf-8", "strict"), filename="private/cpp_candidate.py")
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise RepairError("reject invalid corrected C++ public source") from exc
    functions = {
        item.name: item
        for item in tree.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    need(
        all(name in functions for name in ("_deprecated_positional", "split", "sub", "subn")),
        "preserve all four independent public argument and warning functions",
    )
    assignments = signature_assignments(tree)
    need(assignments == EXPECTED_TEXT_SIGNATURES, "freeze all three real CPython text signatures")
    if frozen:
        need(
            len(derived) == DERIVED_BYTES and sha256(derived) == DERIVED_SHA256,
            "reject substituted derived C++ public source",
        )
        for marker in (
            b"from candidates import _cpp_bridge\n",
            b"class RegexFlag(enum.IntFlag):\n",
            b"class PatternError(Exception):\n",
            b"class Match:\n",
            b"class Pattern:\n",
            b"class Scanner:\n",
            b"def compile(pattern, flags=0):\n",
            b"def purge():\n",
            b"__all__ = [\n",
        ):
            need(raw.count(marker) == 1 and derived.count(marker) == 1, "preserve C++ engine ownership and public source: " + repr(marker))
    return derived


def signature_assignments(tree: ast.Module) -> dict[str, str]:
    actual: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if (
            isinstance(target, ast.Attribute)
            and target.attr == "__text_signature__"
            and isinstance(target.value, ast.Name)
            and target.value.id in EXPECTED_TEXT_SIGNATURES
        ):
            need(target.value.id not in actual, "reject a duplicate public text signature")
            need(isinstance(node.value, ast.Constant) and type(node.value.value) is str, "reject a computed public text signature")
            actual[target.value.id] = node.value.value
    return actual


def observed_failure() -> dict[str, Any]:
    return {
        "family": "cpp",
        "suite": "original_bounded_v5",
        "test": OBSERVED_TEST,
        "test_source": owner_document(UPSTREAM_TEST),
        "method_start_line": UPSTREAM_METHOD_LINE,
        "method_end_line": UPSTREAM_METHOD_END_LINE,
        "failure_line": UPSTREAM_FAILURE_LINE,
        "method_source_sha256": UPSTREAM_METHOD_SHA256,
        "method_ast_sha256": UPSTREAM_METHOD_AST_SHA256,
        "failure_class": "SEMANTIC MISMATCH",
        "actual_exception_type": "TypeError",
        "actual": OBSERVED_ACTUAL,
        "expected": OBSERVED_EXPECTED,
        "failure_archive_sha256": CPP_FAILURE_ARCHIVE_SHA256,
        "failure_archive_compressed_bytes": CPP_FAILURE_ARCHIVE_BYTES,
        "failure_archive_uncompressed_bytes": CPP_FAILURE_ARCHIVE_UNCOMPRESSED_BYTES,
        "previously_observed_prefix_bytes": PREVIOUS_PREFIX_BYTES,
        "previously_observed_prefix_sha256": PREVIOUS_PREFIX_SHA256,
        "previously_observed_prefix_inspection_count": 1,
        "failure_archive_reopened_by_source_freeze": False,
        "failure_archive_decompressed_by_source_freeze": False,
        "corrected_candidate_matching": "NOT MEASURED",
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_sha256(source_pin, "C++ repair source")
    checked_sha256(protocol_pin, "C++ repair protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "phase": "SOURCE FREEZE; NO APPLICATION, BUILD, OR CANDIDATE RUN",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "goal": owner_document(GOAL),
        "phase_one": owner_document(PHASE_ONE),
        "runtime": {
            "implementation": "cpython",
            "version": "3.14.6",
            "python": PYTHON,
            "python_sha256": PYTHON_SHA256,
            "isolated": True,
            "bytecode_writes": False,
            "stdlib_reference_scope": "THIS PINNED ISOLATED SOURCE-ONLY ORACLE PROCESS",
            "candidate_stdlib_regex_delegation": "FORBIDDEN",
        },
        "upstream_oracle": {
            "committed_test": owner_document(UPSTREAM_TEST),
            "separately_located_upstream_test": owner_document(SEPARATE_UPSTREAM_TEST),
            "separately_installed_re": owner_document(INSTALLED_RE),
            "observed_test": OBSERVED_TEST,
            "source_text_signatures": dict(EXPECTED_TEXT_SIGNATURES),
            "upstream_test_method_execution": "NOT RUN",
        },
        "observed_actual_cpp_failure": observed_failure(),
        "cpp_source": {
            "family": "cpp",
            "source_owner_count": len(CPP_OWNERS),
            "owners": [owner_document(owner) for owner in CPP_OWNERS],
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "stdlib_regex_engine_delegation_allowed": False,
            "native_parser_compiler_executor_modified": False,
            "native_bridge_modified": False,
        },
        "repair": {
            "original": {
                "path": CPP_OWNERS[0].path,
                "sha256": ORIGINAL_SHA256,
                "bytes": ORIGINAL_BYTES,
                "modified": False,
            },
            "derived": {
                "path": CPP_OWNERS[0].path,
                "sha256": DERIVED_SHA256,
                "bytes": DERIVED_BYTES,
                "materialized": False,
            },
            "anchored_block_count": 1,
            "block": {
                "name": "observed-cpython-public-optional-argument-order-errors-and-signatures",
                "original_sha256": sha256(OLD_OPTIONAL_BLOCK),
                "original_bytes": len(OLD_OPTIONAL_BLOCK),
                "derived_sha256": sha256(CORRECTED_OPTIONAL_BLOCK),
                "derived_bytes": len(CORRECTED_OPTIONAL_BLOCK),
                "original_occurrence_count": 1,
                "derived_occurrence_count": 1,
            },
            "affected_public_functions": ["split", "sub", "subn"],
            "duplicate_validation_precedes_warnings": True,
            "exact_variable_positional_count_errors": True,
            "preserve_deprecation_warning_filename": True,
            "exact_text_signatures": dict(EXPECTED_TEXT_SIGNATURES),
            "native_cpp_sources_modified": False,
            "native_cpp_bridge_modified": False,
            "external_regex_package_added": False,
            "stdlib_regex_engine_added": False,
            "cross_family_source_added": False,
            "corrected_candidate_matching": "NOT MEASURED",
        },
        "additional_callable_introspection": {
            "owners": [owner_document(owner) for owner in ADDITIVE_INTROSPECTION],
            "separate_case_count": ADDITIVE_INTROSPECTION_CASE_COUNT,
            "original_case_execution_denominator": CASE_DENOMINATOR,
            "reference_execution": "NOT RUN",
            "candidate_execution": "NOT RUN",
            "counted_in_original_denominator": False,
        },
        "published_history": {
            "historical_v31": [owner_document(owner) for owner in V31],
            "cpp_actual_failure_receipt": owner_document(CPP_RECEIPT),
            "cpp_failure_archive_opened": False,
            "cpp_failure_archive_decompressed": False,
            "candidate_independence": [owner_document(owner) for owner in INDEPENDENCE],
            "cpp_original_campaign": [owner_document(owner) for owner in CPP_CAMPAIGN],
            "actual_current_rust_failure_raw_compressed_archive": owner_document(RUST_V4_ARCHIVE),
            "actual_current_rust_failure_receipt": owner_document(RUST_V4_RECEIPT),
            "rust_matching_archive_decompressed": False,
            "historical_v31_evidence_owner_count": V31_EVIDENCE_OWNERS,
            "historical_v31_authenticated_reference_count": V31_HISTORY_REFERENCES,
            "current_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
            "current_authenticated_reference_count": CURRENT_HISTORY_REFERENCES,
            "current": baseline(),
        },
        "apply_policy": {
            "explicit_apply_required": True,
            "independent_derived_sha256_required": True,
            "independent_derived_bytes_required": True,
            "snapshot_root_required": True,
            "private_parent": "/tmp",
            "private_root_prefix": PRIVATE_ROOT_PREFIX,
            "phase_names": list(PHASE_NAMES),
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "destination_relative": "source/candidates/cpp_candidate.py",
            "creation_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "two_distinct_phase_directories_required": True,
            "existing_destination": "FORBIDDEN",
            "canonical_worktree_destination": "FORBIDDEN",
            "other_family_destination": "FORBIDDEN",
            "candidate_activation": "FORBIDDEN",
            "source_build": "FORBIDDEN",
        },
        "phase_boundary": boundary(),
    }


class SourceWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {
            key: 0
            for key in (
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
        targets = (
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "resolve"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename", "replace", "fsync"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename", "replace"), "write"),
            (tempfile, ("mkdtemp", "mkstemp"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output"), "process"),
            (importlib, ("import_module",), "import"),
            (socket, ("socket", "create_connection"), "network"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "process_time", "process_time_ns", "sleep"), "clock"),
            (ctypes, ("CDLL", "PyDLL"), "native"),
            (fcntl, ("flock",), "lock"),
            (signal, ("signal", "pthread_sigmask"), "signal"),
            (gzip, ("open", "decompress"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        )
        for owner, names, category in targets:
            for name in names:
                self.deny(owner, name, category)
        return self

    def __exit__(self, *_args: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


class LiteralPattern:
    def __init__(self, pattern: str | bytes) -> None:
        self.pattern = pattern

    def split(self, subject: str | bytes, maximum: int) -> list[str] | list[bytes]:
        if maximum < 0:
            return [subject]
        if maximum == 0:
            return subject.split(self.pattern)
        return subject.split(self.pattern, maximum)

    def sub(self, replacement: str | bytes, subject: str | bytes, count: int) -> str | bytes:
        if count < 0:
            return subject
        if count == 0:
            return subject.replace(self.pattern, replacement)
        return subject.replace(self.pattern, replacement, count)

    def subn(
        self,
        replacement: str | bytes,
        subject: str | bytes,
        count: int,
    ) -> tuple[str | bytes, int]:
        if count < 0:
            return subject, 0
        available = subject.count(self.pattern)
        total = available if count == 0 else min(available, count)
        return self.sub(replacement, subject, count), total


class LiteralCompiler:
    def __init__(self) -> None:
        self.calls: list[tuple[str | bytes, int]] = []

    def __call__(self, pattern: str | bytes, flags: int) -> LiteralPattern:
        need(type(pattern) in (str, bytes), "require a first-party literal witness")
        need(type(flags) is int, "require exactly normalized witness flags")
        self.calls.append((pattern, flags))
        return LiteralPattern(pattern)


def synthetic_functions(raw: bytes) -> tuple[dict[str, Any], LiteralCompiler]:
    try:
        tree = ast.parse(raw.decode("utf-8", "strict"), filename="<owned-cpp-argument-source>")
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise RepairError("reject an invalid in-memory C++ source witness") from exc
    requested = {"_deprecated_positional", "split", "sub", "subn"}
    nodes: list[ast.stmt] = []
    found: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in requested:
            need(node.name not in found, "reject a duplicate synthetic public function")
            found.add(node.name)
            nodes.append(node)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id in EXPECTED_TEXT_SIGNATURES
                and target.attr == "__text_signature__"
            ):
                nodes.append(node)
    need(found == requested, "extract only the four exact first-party public witness functions")
    module = ast.Module(body=nodes, type_ignores=[])
    compiler = LiteralCompiler()
    namespace: dict[str, Any] = {
        "__name__": SCHEMA + "_synthetic",
        "warnings": warnings,
        "_MISSING": object(),
        "compile": compiler,
    }
    exec(
        builtins.compile(
            ast.fix_missing_locations(module),
            "<owned-cpp-argument-source>",
            "exec",
            dont_inherit=True,
        ),
        namespace,
    )
    return {name: namespace[name] for name in ("split", "sub", "subn")}, compiler


def observe(
    function: Any,
    arguments: tuple[Any, ...],
    keywords: dict[str, Any],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        try:
            result["result"] = function(*arguments, **keywords)
        except (TypeError, ValueError, OverflowError) as exc:
            result["exception_type"] = type(exc).__name__
            result["exception_message"] = str(exc)
        result["warnings"] = [
            {
                "category": type(item.message).__name__,
                "message": str(item.message),
                "filename": item.filename,
            }
            for item in recorded
        ]
    return result


def verify_argument_vectors(functions: dict[str, Any], compiler: LiteralCompiler) -> dict[str, Any]:
    total = 0
    successful = 0
    warning_cases = 0
    failure_cases = 0
    for name in ("split", "sub", "subn"):
        expected_function = getattr(isolated_reference_re, name)
        candidate = functions[name]
        need(
            getattr(candidate, "__text_signature__", None)
            == EXPECTED_TEXT_SIGNATURES[name]
            == getattr(expected_function, "__text_signature__", None),
            "reject a non-CPython public text signature: " + name,
        )
        need(
            str(inspect.signature(candidate))
            == str(inspect.signature(expected_function))
            == EXPECTED_TEXT_SIGNATURES[name],
            "reject a non-CPython inspect.signature result: " + name,
        )
        for binary in (False, True):
            if name == "split":
                base = (b":", b":a:b") if binary else (":", ":a:b")
                primary = "maxsplit"
            else:
                base = (b"a", b"b", b"aaaaa") if binary else ("a", "b", "aaaaa")
                primary = "count"
            options = (
                {},
                {primary: 0},
                {primary: 1},
                {primary: -1},
                {"flags": 0},
                {"flags": 2},
                {primary: 0, "flags": 0},
                {primary: 1, "flags": 2},
            )
            extras = (1, 0, 0, 3, 4, 5)
            for extra_count in range(len(extras) + 1):
                arguments = base + extras[:extra_count]
                for keywords in options:
                    before = len(compiler.calls)
                    expected = observe(expected_function, arguments, dict(keywords))
                    actual = observe(candidate, arguments, dict(keywords))
                    need(
                        actual == expected,
                        "reject real CPython public argument, error, warning, or result parity: "
                        + name
                        + "/"
                        + ("bytes" if binary else "text")
                        + "/"
                        + str(extra_count)
                        + "/"
                        + repr(keywords),
                    )
                    delta = len(compiler.calls) - before
                    if "exception_type" in actual:
                        need(delta == 0, "never invoke a candidate matcher for invalid arguments")
                        failure_cases += 1
                    else:
                        need(delta == 1, "use only the owned literal source-only synthetic witness")
                        successful += 1
                    if actual["warnings"]:
                        need(
                            len(actual["warnings"]) == 1
                            and actual["warnings"][0]["category"] == "DeprecationWarning",
                            "emit exactly one real-CPython deprecation warning",
                        )
                        warning_cases += 1
                    total += 1
    need(total == 336, "never silently alter the deterministic public-argument denominator")
    return {
        "isolated_stdlib_reference_case_count": total,
        "owned_literal_synthetic_case_count": total,
        "successful_argument_case_count": successful,
        "rejected_argument_case_count": failure_cases,
        "one_deprecation_warning_case_count": warning_cases,
        "verified_public_text_signature_count": 3,
        "candidate_engine_or_native_matcher_used": False,
    }


def sample_source() -> bytes:
    return (
        b"def _deprecated_positional(argument, supplied):\n"
        b"    if supplied:\n"
        b"        warnings.warn(\n"
        b"            f\"'{argument}' is passed as positional argument\",\n"
        b"            DeprecationWarning,\n"
        b"            stacklevel=3,\n"
        b"        )\n\n\n"
        + OLD_OPTIONAL_BLOCK
    )


def validate_upstream(committed: bytes, separate: bytes, installed: bytes) -> dict[str, Any]:
    need(committed == separate, "require byte-identical committed and separate genuine CPython tests")
    try:
        text = committed.decode("utf-8", "strict")
        tree = ast.parse(text, filename=UPSTREAM_TEST.path)
        installed_tree = ast.parse(installed.decode("utf-8", "strict"), filename=INSTALLED_RE.path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise RepairError("reject altered genuine CPython upstream source") from exc
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ReTests"]
    need(len(classes) == 1, "require the genuine original upstream ReTests class")
    methods = [
        node
        for node in classes[0].body
        if isinstance(node, ast.FunctionDef) and node.name == "test_qualified_re_sub"
    ]
    need(len(methods) == 1, "require the actual observed upstream optional-argument test")
    method = methods[0]
    segment = ast.get_source_segment(text, method)
    need(
        type(segment) is str
        and method.lineno == UPSTREAM_METHOD_LINE
        and method.end_lineno == UPSTREAM_METHOD_END_LINE
        and sha256(segment.encode("utf-8")) == UPSTREAM_METHOD_SHA256
        and sha256(ast.dump(method, include_attributes=False).encode("utf-8"))
        == UPSTREAM_METHOD_AST_SHA256,
        "reject a substituted genuine upstream observed test method",
    )
    need(
        'r"sub\\(\\) takes from 3 to 5 positional arguments but 6 "' in segment
        and 'r"were given"' in segment,
        "derive the observed expected positional-argument error from the real upstream test",
    )
    installed_functions = {
        node.name
        for node in installed_tree.body
        if isinstance(node, ast.FunctionDef) and node.name in EXPECTED_TEXT_SIGNATURES
    }
    need(installed_functions == set(EXPECTED_TEXT_SIGNATURES), "authenticate all three pinned standard-library argument functions")
    need(
        signature_assignments(installed_tree) == EXPECTED_TEXT_SIGNATURES,
        "derive all three exact signatures from authenticated stable CPython source",
    )
    for name, signature in EXPECTED_TEXT_SIGNATURES.items():
        reference = getattr(isolated_reference_re, name)
        need(
            getattr(reference, "__text_signature__", None) == signature
            and str(inspect.signature(reference)) == signature,
            "authenticate the pinned live CPython signature: " + name,
        )
    return {
        "test": OBSERVED_TEST,
        "source_path": UPSTREAM_TEST.path,
        "source_sha256": UPSTREAM_TEST.sha256,
        "method_start_line": UPSTREAM_METHOD_LINE,
        "method_end_line": UPSTREAM_METHOD_END_LINE,
        "method_source_sha256": UPSTREAM_METHOD_SHA256,
        "method_ast_sha256": UPSTREAM_METHOD_AST_SHA256,
        "failure_line": UPSTREAM_FAILURE_LINE,
        "source_text_signature_count": 3,
        "upstream_unittest_method_executed": False,
    }


def validate_history(
    overview: dict[str, Any],
    inputs: dict[str, Any],
    phase_one: dict[str, Any],
    independence: dict[str, Any],
    campaign: dict[str, Any],
    cpp_receipt: dict[str, Any],
    rust_receipt: dict[str, Any],
    additive: dict[str, Any],
) -> None:
    need(
        overview.get("schema") == "rebar-candidate-current-overview-v31-summary"
        and overview.get("version") == 31
        and overview.get("status") == "PASS"
        and overview.get("full_case_denominator") == CASE_DENOMINATOR
        and overview.get("suite_count") == SUITE_COUNT
        and overview.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and overview.get("repository_evidence_owner_count") == V31_EVIDENCE_OWNERS
        and overview.get("authenticated_digest_addressed_history_paths")
        == V31_HISTORY_REFERENCES
        and overview.get("qualified_candidate_count") == 0
        and overview.get("c_original_campaign_status") == "FAIL"
        and overview.get("c_original_campaign_semantic_mismatch_count") == 1230
        and overview.get("rust_original_campaign_status") == "FAIL"
        and overview.get("rust_original_campaign_semantic_mismatch_count") == 1087
        and overview.get("zig_original_campaign_status") == "FAIL"
        and overview.get("zig_original_campaign_semantic_mismatch_count") == 2172
        and overview.get("performance") == "NOT MEASURED"
        and overview.get("memory") == "NOT MEASURED"
        and overview.get("hidden_cases_read") == 0
        and overview.get("clock_samples") == 0
        and overview.get("timing_trials_run") == 0
        and overview.get("final_holdout_opened") is False
        and overview.get("final_comparison_cases_generated") is False
        and overview.get("winner_selected") is False,
        "reject the historical 151/156 V31 overview, changed original results, or opened holdout",
    )
    need(
        inputs.get("version") == 31
        and inputs.get("repository_evidence_owner_count") == V31_EVIDENCE_OWNERS
        and inputs.get("all_digest_addressed_history_path_count") == V31_HISTORY_REFERENCES
        and inputs.get("full_case_denominator") == CASE_DENOMINATOR
        and inputs.get("suite_count") == SUITE_COUNT
        and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and inputs.get("final_holdout_opened") is False
        and inputs.get("final_comparison_cases_generated") is False,
        "reject substituted historical V31 inputs or stale history references",
    )
    families = overview.get("families")
    need(isinstance(families, list), "require the authenticated V31 candidate families")
    selected = [item for item in families if isinstance(item, dict) and item.get("family") == "cpp"]
    need(len(selected) == 1, "require the one genuinely owned C++ family")
    cpp = selected[0]
    result = cpp.get("complete_campaign")
    need(
        cpp.get("build_status") == "PASS"
        and cpp.get("matching_test_status") == "FAIL"
        and cpp.get("correctness") == "FAILED; NOT QUALIFIED"
        and cpp.get("qualified") is False
        and isinstance(result, dict)
        and result.get("status") == "FAIL"
        and result.get("candidate_qualified") is False
        and result.get("completed_suite_count") == SUITE_COUNT
        and result.get("passing_suite_count") == 1
        and result.get("verified_passing_case_count") == 128
        and result.get("semantic_mismatch_count") == 2308
        and result.get("semantic_failure_suite_counts") == CPP_SEMANTIC_SUITE_COUNTS
        and result.get("infrastructure_failure_suites") == list(CPP_INFRASTRUCTURE_SUITES)
        and result.get("crash_count") == 0
        and result.get("timeout_count") == 0
        and result.get("restoration_status") == "PASS"
        and result.get("restored_original_state") == "originally absent",
        "preserve the actual 2,308 C++ differences, five infrastructure suites, and 128 passing cases",
    )
    need(
        1 + len(CPP_INFRASTRUCTURE_SUITES) + len(CPP_SEMANTIC_SUITE_COUNTS)
        == SUITE_COUNT
        and sum(CPP_SEMANTIC_SUITE_COUNTS.values()) == 2308,
        "never mislabel twelve failing suites as twelve worker crashes",
    )
    denominator = phase_one.get("denominator")
    need(
        phase_one.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and isinstance(denominator, dict)
        and denominator.get("final_required_case_execution_denominator") == CASE_DENOMINATOR
        and denominator.get("private_upstream_methods_outside_public_denominator") == PRIVATE_WAIVER_COUNT
        and denominator.get("counted_suite_ids") == [name for name, _ in SUITES]
        and sum(amount for _, amount in SUITES) == CASE_DENOMINATOR,
        "never change an original test, suite, named waiver, or 31,237-case denominator",
    )
    entries = independence.get("families")
    need(isinstance(entries, list), "require frozen first-party family independence")
    cpp_entries = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == "cpp"]
    need(len(cpp_entries) == 1, "reject an absent or duplicate first-party C++ family")
    cpp_owners = cpp_entries[0].get("owners")
    need(
        isinstance(cpp_owners, list)
        and len(cpp_owners) == len(CPP_OWNERS)
        and {
            (item.get("path"), item.get("sha256"))
            for item in cpp_owners
            if isinstance(item, dict)
        }
        == {(owner.path, owner.sha256) for owner in CPP_OWNERS}
        and cpp_entries[0].get("bridge") == "_cpp_bridge",
        "reject a delegated, shared, wrapped, or substituted C++ engine",
    )
    need(
        campaign.get("schema") == "rebar-owned-six-family-original-p0-campaign-v1-source-freeze"
        and campaign.get("case_execution_denominator") == CASE_DENOMINATOR
        and campaign.get("suite_count") == SUITE_COUNT
        and campaign.get("supported_actual_campaign_families") == ["cpp", "go"]
        and campaign.get("independence_policy", {}).get("python_re_matching_allowed") is False
        and campaign.get("independence_policy", {}).get("sre_matching_allowed") is False
        and campaign.get("independence_policy", {}).get("third_party_regex_allowed") is False
        and campaign.get("independence_policy", {}).get("cross_family_engine_allowed") is False,
        "preserve the frozen no-delegation original C++ campaign",
    )
    archive = cpp_receipt.get("archive")
    need(
        cpp_receipt.get("schema") == "rebar-owned-six-family-original-p0-campaign-v1-durable-publication-receipt"
        and cpp_receipt.get("status") == "PASS"
        and cpp_receipt.get("candidate_family") == "cpp"
        and cpp_receipt.get("candidate_status") == "FAIL"
        and cpp_receipt.get("case_execution_denominator") == CASE_DENOMINATOR
        and cpp_receipt.get("suite_count") == SUITE_COUNT
        and cpp_receipt.get("completed_suite_count") == SUITE_COUNT
        and cpp_receipt.get("all_mismatches_crashes_and_timeouts_preserved") is True
        and isinstance(archive, dict)
        and archive.get("sha256") == CPP_FAILURE_ARCHIVE_SHA256
        and archive.get("size_bytes") == CPP_FAILURE_ARCHIVE_BYTES
        and cpp_receipt.get("uncompressed_bytes") == CPP_FAILURE_ARCHIVE_UNCOMPRESSED_BYTES
        and cpp_receipt.get("hidden_cases_read") == 0
        and cpp_receipt.get("holdout") == "NOT OPENED"
        and cpp_receipt.get("performance") == "NOT MEASURED"
        and cpp_receipt.get("timing_trials_run") == 0,
        "preserve the actual failed C++ receipt without reopening its failure archive",
    )
    rust_archive = rust_receipt.get("archive")
    need(
        rust_receipt.get("schema") == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
        and rust_receipt.get("status") == "PASS"
        and rust_receipt.get("publication_status") == "PASS"
        and rust_receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and rust_receipt.get("family") == "rust"
        and rust_receipt.get("candidate_status") == "FAIL"
        and rust_receipt.get("candidate_qualified") is False
        and rust_receipt.get("case_execution_denominator") == CASE_DENOMINATOR
        and rust_receipt.get("suite_count") == SUITE_COUNT
        and rust_receipt.get("completed_suite_count") == SUITE_COUNT
        and rust_receipt.get("actual_candidate_workers") == SUITE_COUNT
        and rust_receipt.get("semantic_mismatch_count") == 1036
        and rust_receipt.get("verified_passing_case_count") == 8965
        and rust_receipt.get("infrastructure_failure_count") == 0
        and rust_receipt.get("historical_evidence_owner_count_before_publication") == V31_EVIDENCE_OWNERS
        and rust_receipt.get("historical_authenticated_reference_count_before_publication") == V31_HISTORY_REFERENCES
        and rust_receipt.get("new_repository_evidence_owner_count") == 2
        and rust_receipt.get("resulting_repository_evidence_owner_count") == CURRENT_EVIDENCE_OWNERS
        and rust_receipt.get("resulting_authenticated_reference_count") == CURRENT_HISTORY_REFERENCES
        and isinstance(rust_archive, dict)
        and rust_archive.get("sha256") == RUST_V4_ARCHIVE.sha256
        and rust_archive.get("size_bytes") == RUST_V4_ARCHIVE.size
        and rust_receipt.get("hidden_cases_read") == 0
        and rust_receipt.get("holdout") == "NOT OPENED"
        and rust_receipt.get("performance") == "NOT MEASURED"
        and rust_receipt.get("timing_trials_run") == 0
        and rust_receipt.get("all_four_original_targets_restored") is True,
        "reject stale 151/156 current history or the actual newly failed 1,036-difference Rust run",
    )
    addition = additive.get("additional_obligation")
    original = additive.get("original_correctness")
    need(
        additive.get("schema") == "rebar-python-re-callable-introspection-v1-source-freeze"
        and additive.get("status") == "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN"
        and additive.get("phase") == "ADDITIVE CORRECTNESS ORACLE; NO BENCHMARK"
        and isinstance(addition, dict)
        and addition.get("case_count") == ADDITIVE_INTROSPECTION_CASE_COUNT
        and isinstance(original, dict)
        and original.get("case_execution_denominator") == CASE_DENOMINATOR
        and original.get("suite_count") == SUITE_COUNT,
        "never claim the separately frozen 50-case reference or candidate was executed",
    )


def self_test(source_pin: str, protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    expected_contract = contract_document(source_pin, protocol_pin)
    need(
        sha256(canonical(expected_contract)) == checked_sha256(contract_pin, "canonical C++ repair contract"),
        "reject a substituted caller-pinned C++ source contract",
    )
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: bool) -> None:
        need(value, "reject a required positive control: " + name)
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
        ):
            rejected.append(name)
            return
        raise RepairError("accept hostile C++ source evidence: " + name)

    with SourceWall() as wall:
        original = sample_source()
        fixed = repaired_source(original, frozen=False)
        old_functions, old_compiler = synthetic_functions(original)
        functions, compiler = synthetic_functions(fixed)
        wrong = observe(old_functions["sub"], ("a", "b", "aaaaa", 1, 0, 0), {})
        expected = observe(isolated_reference_re.sub, ("a", "b", "aaaaa", 1, 0, 0), {})
        accept("reproduce the actual upstream archived C++ TypeError", wrong.get("exception_message") == OBSERVED_ACTUAL)
        accept("derive the exact pinned CPython observed TypeError", expected.get("exception_message") == OBSERVED_EXPECTED)
        accept("reject the historical C++ public behavior", wrong != expected and not old_compiler.calls)
        vectors = verify_argument_vectors(functions, compiler)
        accept("compare all 336 real isolated CPython argument vectors", vectors["isolated_stdlib_reference_case_count"] == 336)
        accept("freeze three real CPython public text signatures", vectors["verified_public_text_signature_count"] == 3)
        accept("never use a C++ native or external matcher", vectors["candidate_engine_or_native_matcher_used"] is False)
        accept("preserve one uniquely anchored first-party repair", fixed.count(CORRECTED_OPTIONAL_BLOCK) == 1)
        accept("preserve the exact original 31,237 cases", sum(count for _, count in SUITES) == CASE_DENOMINATOR)
        accept("preserve all thirteen original suite owners", len(SUITES) == SUITE_COUNT)
        accept("keep 50 additional introspection cases separate", baseline()["additive_introspection_case_count"] == 50)
        accept("leave the introspection baseline genuinely not run", baseline()["additive_introspection_reference"] == "NOT RUN")
        accept("preserve historical V31 151/156", baseline()["historical_v31_evidence_owner_count"] == 151 and baseline()["historical_v31_authenticated_reference_count"] == 156)
        accept("preserve current Rust-publication 153/158", baseline()["current_evidence_owner_count"] == 153 and baseline()["current_authenticated_reference_count"] == 158)
        accept("preserve 2,308 true C++ semantic mismatches", baseline()["cpp_semantic_mismatch_count"] == 2308)
        accept("distinguish five failed infrastructure suites", baseline()["cpp_infrastructure_failure_suite_count"] == 5)
        accept("preserve 128 passing C++ observations", baseline()["cpp_verified_passing_case_count"] == 128)
        accept("preserve the actual 1,036-mismatch Rust run", baseline()["current_rust_semantic_mismatch_count"] == 1036)
        accept("leave all holdout and performance claims unmeasured", baseline()["holdout"] == "NOT OPENED" and baseline()["performance"] == "NOT MEASURED")
        validate_baseline(baseline())
        for label, hostile in (
            ("missing anchored optional block", original.replace(OLD_OPTIONAL_BLOCK, b"# missing public API\n")),
            ("duplicate anchored optional block", original + OLD_OPTIONAL_BLOCK),
            ("already repaired anchored block", original.replace(OLD_OPTIONAL_BLOCK, CORRECTED_OPTIONAL_BLOCK)),
            ("stdlib re wrapper", original + b"\nimport re\n"),
            ("CPython private regex wrapper", original + b"\nimport _sre\n"),
            ("another Rust candidate", original + b"\ncandidates.rust_candidate\n"),
            ("another Zig candidate", original + b"\ncandidates.zig_candidate\n"),
            ("another virtual-machine candidate", original + b"\ncandidates.vm_candidate\n"),
            ("foreign package", original + b"\npcre\n"),
            ("native loader", original + b"\nctypes\n"),
            ("external process", original + b"\nsubprocess\n"),
        ):
            reject(label, lambda data=hostile: repaired_source(data, frozen=False))
        for digest in ("", "0" * 63, "0" * 65, "A" * 64, "z" * 64, None, 0, True):
            reject("invalid independent digest", lambda value=digest: checked_sha256(value, "hostile"))
        for path in ("", "/tmp/escape", "../escape", "a/../b", "a//b", "./a", "a/", "a\\b", "x" * 513):
            reject("unsafe immutable owner path", lambda value=path: checked_relative(value))
        for raw in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n', b"[]\n", b'{"x":1}', b"", b"null\n"):
            reject("ambiguous canonical evidence", lambda data=raw: strict_json(data, "hostile"))
        changes = (
            ("full_case_denominator", 31287),
            ("suite_count", 12),
            ("private_waiver_count", 12),
            ("historical_v31_evidence_owner_count", 153),
            ("historical_v31_authenticated_reference_count", 158),
            ("current_evidence_owner_count", 151),
            ("current_authenticated_reference_count", 156),
            ("qualified_candidate_count", 1),
            ("cpp_status", "PASS"),
            ("cpp_passing_suite_count", 13),
            ("cpp_failing_suite_count", 0),
            ("cpp_verified_passing_case_count", 31237),
            ("cpp_semantic_mismatch_count", 0),
            ("cpp_semantic_failure_suite_count", 12),
            ("cpp_infrastructure_failure_suite_count", 12),
            ("cpp_crash_count", 12),
            ("cpp_timeout_count", 1),
            ("c_semantic_mismatch_count", 0),
            ("zig_semantic_mismatch_count", 0),
            ("v31_historical_rust_semantic_mismatch_count", 1036),
            ("current_rust_status", "PASS"),
            ("current_rust_semantic_mismatch_count", 1087),
            ("current_rust_verified_passing_case_count", 7438),
            ("current_rust_candidate_workers", 0),
            ("current_rust_infrastructure_failure_count", 1),
            ("additive_introspection_case_count", 0),
            ("additive_introspection_reference", "PASS"),
            ("additive_introspection_candidate", "PASS"),
            ("final_comparison_planned_case_count", 4194303),
            ("candidate_correctness", "PASS"),
            ("candidate_qualified", True),
            ("candidate_imports", 1),
            ("candidate_workers_started", 1),
            ("candidate_matching_operations", 1),
            ("reference_processes_started", 1),
            ("source_builds_started", 1),
            ("compiler_processes_started", 1),
            ("native_activations", 1),
            ("native_libraries_loaded", 1),
            ("source_apply_count", 1),
            ("workspace_mutations", 1),
            ("cpp_matching_archive_opened", True),
            ("cpp_matching_archive_uncompressed_bytes_read", 1),
            ("rust_matching_archive_decompressed", True),
            ("rust_matching_archive_uncompressed_bytes_read", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("performance", "FASTER"),
            ("memory", "ZERO"),
            ("confidence_intervals", "MEASURED"),
            ("undefined_behavior", "PASS"),
            ("holdout", "OPENED"),
            ("final_holdout_opened", True),
            ("final_comparison_cases_generated", True),
            ("winner_selected", True),
        )
        for key, bad in changes:
            hostile = baseline()
            hostile[key] = bad
            reject("altered truthful published history: " + key, lambda value=hostile: validate_baseline(value))
        probes = (
            ("filesystem", lambda: builtins.open("/tmp/rebar-cpp-argument-forbidden", "rb")),
            ("filesystem", lambda: os.open("/tmp/rebar-cpp-argument-forbidden", os.O_RDONLY)),
            ("write", lambda: tempfile.mkdtemp()),
            ("process", lambda: subprocess.run(("rebar-cpp-argument-forbidden",))),
            ("import", lambda: importlib.import_module("candidates.cpp_candidate")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("native", lambda: ctypes.CDLL("rebar-cpp-argument-forbidden")),
            ("lock", lambda: fcntl.flock(-1, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL)),
            ("decompression", lambda: gzip.decompress(b"forbidden")),
            ("decompression", lambda: zlib.decompress(b"forbidden")),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            reject("physically blocked source-only " + kind, action)
            need(wall.blocked[kind] == before + 1, "prove each forbidden external effect was actually intercepted")
        blocked = dict(wall.blocked)
    need(len(rejected) >= 80 and all(value > 0 for value in blocked.values()), "require exhaustive hostile controls and every blocked effect")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "version": 1,
        "mode": "SYNTHETIC SOURCE ONLY; PINNED STDLIB REFERENCE",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "blocked_effects_by_kind": blocked,
        "actual_observed_failure_reproduced": True,
        "actual_observed_failure_corrected_in_synthetic_source": True,
        "historical_v31_evidence_owner_count": V31_EVIDENCE_OWNERS,
        "historical_v31_authenticated_reference_count": V31_HISTORY_REFERENCES,
        "current_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "current_authenticated_reference_count": CURRENT_HISTORY_REFERENCES,
        "cpp_semantic_mismatch_count": 2308,
        "cpp_infrastructure_failure_suite_count": 5,
        "cpp_failing_suite_count": 12,
        "cpp_verified_passing_case_count": 128,
        "current_rust_semantic_mismatch_count": 1036,
        "current_rust_verified_passing_case_count": 8965,
        "original_case_execution_denominator": CASE_DENOMINATOR,
        "separate_additive_introspection_case_count": ADDITIVE_INTROSPECTION_CASE_COUNT,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        **vectors,
        **boundary(),
    }


def read_contract_owners(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    descriptors = (
        Owner(SOURCE_RELATIVE, checked_sha256(source_pin, "source"), os.stat(str(ROOT / SOURCE_RELATIVE), follow_symlinks=False).st_size),
        Owner(PROTOCOL_RELATIVE, checked_sha256(protocol_pin, "protocol"), os.stat(str(ROOT / PROTOCOL_RELATIVE), follow_symlinks=False).st_size),
        Owner(CONTRACT_RELATIVE, checked_sha256(contract_pin, "contract"), os.stat(str(ROOT / CONTRACT_RELATIVE), follow_symlinks=False).st_size),
    )
    raw: list[bytes] = []
    actual: list[dict[str, Any]] = []
    for owner in descriptors:
        content, authenticated = read_owner(owner)
        raw.append(content)
        actual.append(authenticated)
    expected = contract_document(source_pin, protocol_pin)
    need(
        strict_json(raw[2], "C++ canonical repair contract") == expected
        and sha256(canonical(expected)) == contract_pin,
        "reject a substituted canonical C++ source contract",
    )
    return expected, actual


def verify_context(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> tuple[dict[str, Any], bytes]:
    _, contract_owners = read_contract_owners(source_pin, protocol_pin, contract_pin)
    support = (
        GOAL,
        PHASE_ONE,
        UPSTREAM_TEST,
        *CPP_OWNERS,
        *V31,
        *INDEPENDENCE,
        *CPP_CAMPAIGN,
        CPP_RECEIPT,
        RUST_V4_ARCHIVE,
        RUST_V4_RECEIPT,
        *ADDITIVE_INTROSPECTION,
    )
    raw: dict[str, bytes] = {}
    authenticated: list[dict[str, Any]] = []
    for owner in support:
        value, actual = read_owner(owner)
        need(owner.path not in raw, "reject a duplicated source evidence owner")
        raw[owner.path] = value
        authenticated.append(actual)
    separate, separate_owner = read_owner(SEPARATE_UPSTREAM_TEST, external=True)
    installed, installed_owner = read_owner(INSTALLED_RE, external=True)
    upstream = validate_upstream(raw[UPSTREAM_TEST.path], separate, installed)
    validate_history(
        strict_json(raw[V31[2].path], "historical V31 summary"),
        strict_json(raw[V31[1].path], "historical V31 inputs"),
        strict_json(raw[PHASE_ONE.path], "immutable original correctness matrix"),
        strict_json(
            raw[INDEPENDENCE[1].path],
            "frozen first-party independence",
            require_canonical=False,
        ),
        strict_json(raw[CPP_CAMPAIGN[1].path], "frozen original C++ campaign"),
        strict_json(raw[CPP_RECEIPT.path], "actual failed C++ publication"),
        strict_json(raw[RUST_V4_RECEIPT.path], "actual newer failed Rust publication"),
        strict_json(raw[ADDITIVE_INTROSPECTION[2].path], "separate unexecuted introspection amendment"),
    )
    original = raw[CPP_OWNERS[0].path]
    derived = repaired_source(original, frozen=True)
    wrong_functions, wrong_compiler = synthetic_functions(original)
    corrected_functions, compiler = synthetic_functions(derived)
    wrong = observe(wrong_functions["sub"], ("a", "b", "aaaaa", 1, 0, 0), {})
    reference = observe(isolated_reference_re.sub, ("a", "b", "aaaaa", 1, 0, 0), {})
    correct = observe(corrected_functions["sub"], ("a", "b", "aaaaa", 1, 0, 0), {})
    need(
        wrong.get("exception_message") == OBSERVED_ACTUAL
        and reference.get("exception_message") == OBSERVED_EXPECTED
        and correct == reference
        and not wrong_compiler.calls,
        "reproduce and correct the actual archived original CPython C++ public failure",
    )
    vectors = verify_argument_vectors(corrected_functions, compiler)
    need(
        not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
        "never import, activate, or run a candidate during context verification",
    )
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "version": 1,
        "mode": "READ-ONLY SOURCE FREEZE; PINNED STDLIB REFERENCE",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "authenticated_frozen_owner_count": len(contract_owners),
        "authenticated_support_owner_count": len(authenticated),
        "authenticated_external_oracle_owner_count": 2,
        "original_adapter_sha256": ORIGINAL_SHA256,
        "original_adapter_bytes": ORIGINAL_BYTES,
        "derived_source_sha256": DERIVED_SHA256,
        "derived_source_bytes": DERIVED_BYTES,
        "anchored_repair_block_count": 1,
        "observed_actual_failure": observed_failure(),
        "authenticated_upstream_method": upstream,
        "historical_v31_evidence_owner_count": V31_EVIDENCE_OWNERS,
        "historical_v31_authenticated_reference_count": V31_HISTORY_REFERENCES,
        "current_evidence_owner_count": CURRENT_EVIDENCE_OWNERS,
        "current_authenticated_reference_count": CURRENT_HISTORY_REFERENCES,
        "cpp_semantic_mismatch_count": 2308,
        "cpp_infrastructure_failure_suite_count": 5,
        "cpp_semantic_failure_suite_count": 7,
        "cpp_failing_suite_count": 12,
        "cpp_verified_passing_case_count": 128,
        "current_rust_semantic_mismatch_count": 1036,
        "current_rust_verified_passing_case_count": 8965,
        "original_case_execution_denominator": CASE_DENOMINATOR,
        "separate_additive_introspection_case_count": ADDITIVE_INTROSPECTION_CASE_COUNT,
        "additive_introspection_reference_execution": "NOT RUN",
        "additive_introspection_candidate_execution": "NOT RUN",
        "rust_archive_compressed_bytes_authenticated": RUST_V4_ARCHIVE.size,
        "rust_archive_sha256": RUST_V4_ARCHIVE.sha256,
        "rust_archive_decompressed": False,
        "cpp_failure_archive_reopened": False,
        "external_oracle_owners": [separate_owner, installed_owner],
        **vectors,
        **boundary(),
    }, derived


def open_private_directory(parent: int, name: str) -> int:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    descriptor = os.open(name, flags, dir_fd=parent)
    info = os.fstat(descriptor)
    if not (
        stat.S_ISDIR(info.st_mode)
        and info.st_uid == os.geteuid()
        and stat.S_IMODE(info.st_mode) == 0o700
    ):
        os.close(descriptor)
        raise RepairError("reject a non-private, linked, or foreign C++ source directory")
    return descriptor


def validate_private_root(root: object) -> tuple[str, ...]:
    need(type(root) is str and 0 < len(root) <= 512, "require one exact independent private snapshot root")
    parsed = PurePosixPath(root)
    pieces = parsed.parts
    need(
        parsed.is_absolute()
        and str(parsed) == root
        and len(pieces) == 5
        and pieces[0] == "/"
        and pieces[1] == "tmp"
        and pieces[2].startswith(PRIVATE_ROOT_PREFIX)
        and len(pieces[2]) > len(PRIVATE_ROOT_PREFIX)
        and all(char.isascii() and (char.isalnum() or char in "-_") for char in pieces[2])
        and pieces[3] in PHASE_NAMES
        and pieces[4] == "source",
        "never write outside a fresh, exclusively owned C++ /tmp reference phase",
    )
    return pieces


def apply_private(
    root: str,
    derived: bytes,
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> dict[str, Any]:
    pieces = validate_private_root(root)
    need(
        type(derived) is bytes
        and len(derived) == DERIVED_BYTES
        and sha256(derived) == DERIVED_SHA256,
        "reject unpinned derived C++ source bytes",
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
    source: int | None = None
    candidates: int | None = None
    destination: int | None = None
    try:
        top = open_private_directory(temp, pieces[2])
        phase = open_private_directory(top, pieces[3])
        other = "reference-b" if pieces[3] == "reference-a" else "reference-a"
        sibling = open_private_directory(top, other)
        first, second = os.fstat(phase), os.fstat(sibling)
        need((first.st_dev, first.st_ino) != (second.st_dev, second.st_ino), "never alias independent private C++ source phases")
        source = open_private_directory(phase, "source")
        candidates = open_private_directory(source, "candidates")
        original_before, owner_before = read_owner(CPP_OWNERS[0])
        need(repaired_source(original_before, frozen=True) == derived, "reject changed canonical C++ source before private application")
        destination = os.open(
            "cpp_candidate.py",
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=candidates,
        )
        before = os.fstat(destination)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "create only one fresh exclusive owner-only private source snapshot",
        )
        cursor = 0
        while cursor < len(derived):
            amount = os.write(destination, derived[cursor:])
            need(type(amount) is int and amount > 0, "reject an incomplete private C++ snapshot")
            cursor += amount
        os.fsync(destination)
        after = os.fstat(destination)
        need(
            (before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
            and after.st_size == DERIVED_BYTES,
            "reject a swapped private C++ snapshot inode",
        )
        os.close(destination)
        destination = None
        verifier = os.open(
            "cpp_candidate.py",
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=candidates,
        )
        try:
            actual = os.fstat(verifier)
            need(
                (actual.st_dev, actual.st_ino, actual.st_uid, actual.st_nlink, actual.st_size)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink, after.st_size),
                "reject substituted private snapshot readback",
            )
            chunks: list[bytes] = []
            remaining = actual.st_size
            while remaining:
                chunk = os.read(verifier, min(remaining, 1024 * 1024))
                need(type(chunk) is bytes and bool(chunk), "reject truncated private source readback")
                chunks.append(chunk)
                remaining -= len(chunk)
            recovered = b"".join(chunks)
            need(
                os.read(verifier, 1) == b""
                and recovered == derived
                and sha256(recovered) == DERIVED_SHA256,
                "reauthenticate all exact independently frozen private source bytes",
            )
        finally:
            os.close(verifier)
        os.fsync(candidates)
        original_after, owner_after = read_owner(CPP_OWNERS[0])
        need(original_before == original_after and owner_before == owner_after, "never modify the canonical C++ candidate")
        return {
            "schema": SCHEMA + "-private-snapshot-application",
            "status": "PASS",
            "version": 1,
            "source_sha256": source_pin,
            "protocol_sha256": protocol_pin,
            "contract_sha256": contract_pin,
            "snapshot_root": root,
            "phase": pieces[3],
            "derived_source_sha256": DERIVED_SHA256,
            "derived_source_bytes": DERIVED_BYTES,
            "source_apply_count": 1,
            "canonical_candidate_modified": False,
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "source_builds_started": 0,
            "native_activations": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
    finally:
        if destination is not None:
            os.close(destination)
        for descriptor in (candidates, source, sibling, phase, top, temp):
            if descriptor is not None:
                os.close(descriptor)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    options_seen = [value for value in values if value.startswith("--")]
    need(len(options_seen) == len(set(options_seen)), "reject repeated or ambiguous caller authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", "--render-contract", dest="emit_contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    parser.add_argument("--derived-source-sha256")
    parser.add_argument("--derived-source-bytes", type=int)
    options = parser.parse_args(values)
    checked_sha256(options.source_sha256, "C++ source")
    checked_sha256(options.protocol_sha256, "C++ protocol")
    if options.emit_contract:
        need(
            options.contract_sha256 is None
            and options.snapshot_root is None
            and options.derived_source_sha256 is None
            and options.derived_source_bytes is None,
            "contract emission never authorizes a candidate or snapshot",
        )
    else:
        checked_sha256(options.contract_sha256, "C++ canonical contract")
        if options.apply:
            need(
                options.snapshot_root is not None
                and checked_sha256(options.derived_source_sha256, "private derived source")
                == DERIVED_SHA256
                and options.derived_source_bytes == DERIVED_BYTES,
                "require an explicitly caller-pinned private root, derived hash, and byte count",
            )
            validate_private_root(options.snapshot_root)
        else:
            need(
                options.snapshot_root is None
                and options.derived_source_sha256 is None
                and options.derived_source_bytes is None,
                "source-only gates never authorize private application",
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
            output, _ = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256)
        else:
            _, derived = verify_context(options.source_sha256, options.protocol_sha256, options.contract_sha256)
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
        RecursionError,
        SyntaxError,
        OverflowError,
        KeyError,
        AttributeError,
    ) as exc:
        sys.stderr.write("owned C++ public argument source repair v1 rejected: " + str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
