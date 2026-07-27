#!/usr/bin/env python3
"""Durably record exactly one independent regex family and public category.

Only ``--record --candidate FAMILY --category CATEGORY`` starts the frozen
category controller. A report retains both original CPython reference vectors,
one owned candidate vector, every mismatch, and complete genuine process
streams. Native crashes, timeouts, and unknown results remain unknown. The
synthetic ``--self-test`` cannot read a source, run a worker, open a final
holdout, measure time, or write evidence.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass, replace
import gc
import hashlib
import importlib
import importlib.machinery
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/record_independent_public_contract_v2.py"
SCHEMA = "rebar-independent-public-contract-v2-recorder"
CONTRACT_RELATIVE = "tools/independent_public_contract_v2.py"
CONTRACT_MODULE = "tools.independent_public_contract_v2"
CONTRACT_SHA256 = "a0ae9621e06b760477a167705cc6e521cc7e9df4d44d126e39c614df89bd3e68"
CONTRACT_SCHEMA = "rebar-independent-public-contract-v2"
V4_RELATIVE = "tools/independent_original_cpython_suite_v4.py"
V4_SHA256 = "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3"
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
AUDIT_SHA256 = "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
ORIGINAL_RECORDER_RELATIVE = "tools/record_independent_original_cpython_v4.py"
ORIGINAL_RECORDER_SHA256 = "eecafcae7dc27f4be7ac6b1886b51dfe54d5d83843541dca68e018d1caf1683b"
AUDIT_RECORDER_RELATIVE = "tools/record_independent_from_scratch_audit_v2.py"
AUDIT_RECORDER_SHA256 = "dabd1ef53d8a40e672f8faba1690f86283ea05f6c0207cf83bf1054c8edd1e41"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 192 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class CategorySpec:
    name: str
    source_relative: str
    source_sha256: str
    matrix_sha256: str
    baseline_sha256: str
    published_seed: int
    case_count: int
    group_count: int
    cases_per_group: int


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    module: str
    bridge_module: str
    adapter: str
    adapter_sha256: str
    engine: str
    engine_sha256: str
    bridge: str
    bridge_sha256: str
    owned_ctypes: bool
    closure: tuple[tuple[str, str], ...]


CATEGORIES = {
    "public": CategorySpec(
        "public", "tools/rust_public_practice_benchmark_v1.py",
        "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
        "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
        "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
        0x5245_4241_525F_5031, 864, 36, 24,
    ),
    "scanner": CategorySpec(
        "scanner", "tools/rust_scanner_differential_v1.py",
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
        "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
        "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
        0x5343_414E_4E45_5231, 1024, 32, 32,
    ),
    "buffer": CategorySpec(
        "buffer", "tools/rust_memoryview_expand_differential_v1.py",
        "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
        "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
        "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
        0x4D45_5850_414E_4431, 768, 24, 32,
    ),
}

RUST_CLOSURE = (
    ("candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"),
    ("candidates/rust/py_bridge.c", "6f4401a8e9205e3e7b9797dd655f1a0b3d51190b8bd5239f77c5ad1534707f2d"),
    ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966"),
    ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63"),
    ("candidates/rust/src/lib.rs", "4ac8f3e9b96e37f5670cb610c6b031315eeedf92fd645399ac693f2f3d27ba72"),
    ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b"),
    ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe"),
    ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e"),
    ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af"),
    ("candidates/_rust_engine.so", "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4"),
    ("candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "a7ef601a91527d7dcefcacb4c602afb972e4adbbed7d112239e7896530416c02"),
)
C_CLOSURE = (
    ("candidates/vm_candidate.py", "2bd8cd6d3844d6cd8c94f338803b41671d6aa1e999897e21a81cbe91182eb2fb"),
    ("candidates/_vm_native.c", "a516ae8f2409af054b456068e403df63d8fea029a516ce1adb22ee5f836a819c"),
    ("candidates/_vm_native.cpython-314-x86_64-linux-gnu.so", "9308563f7541f7b9f56afc7965a47ae4d4d00b1a94db8857891e493a82ae5148"),
)
ZIG_CLOSURE = (
    ("candidates/zig_candidate.py", "07e9fa19af8fe9938dc8ed5170e30a478ff56f0d04cd2488a0bd1869e28201cc"),
    ("candidates/zig/mini_regex.zig", "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346"),
    ("candidates/zig/py_bridge.c", "f4900d04734a7c02bd766aee81c1d64114803dbefcf6f4591bfb667262658fea"),
    ("candidates/_zig_probe.so", "96b899f8c5f25e4c94fe029d6218c0408cd20f7a86d661bcc4ce891648f17cb6"),
    ("candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so", "ad1a7ea024721e329857753d288abd834fcfc029055a6274195daf00754bf65a"),
)
FAMILIES = {
    "rust": FamilySpec(
        "rust", "candidates.rust_candidate", "candidates._rust_bridge",
        "candidates/rust_candidate.py", RUST_CLOSURE[0][1],
        "candidates/_rust_engine.so", RUST_CLOSURE[-2][1],
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        RUST_CLOSURE[-1][1], False, RUST_CLOSURE,
    ),
    "c": FamilySpec(
        "c", "candidates.vm_candidate", "candidates._vm_native",
        "candidates/vm_candidate.py", C_CLOSURE[0][1],
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so", C_CLOSURE[-1][1],
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so", C_CLOSURE[-1][1],
        False, C_CLOSURE,
    ),
    "zig": FamilySpec(
        "zig", "candidates.zig_candidate", "candidates._zig_bridge",
        "candidates/zig_candidate.py", ZIG_CLOSURE[0][1],
        "candidates/_zig_probe.so", ZIG_CLOSURE[-2][1],
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        ZIG_CLOSURE[-1][1], True, ZIG_CLOSURE,
    ),
}

GUARD_TRUE_FIELDS = (
    "original_matchers_blocked", "adapter_import_quarantined",
    "native_sre_blocked", "builtins_import_guarded", "importlib_import_guarded",
    "actual_object_identity_guarded", "warning_registry_introspection_safe",
    "warning_registry_exactly_absent", "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
GUARD_COUNTER_FIELDS = (
    "cached_original_matcher_descendant_count", "cached_original_holder_count",
    "owned_ctypes_load_count", "owned_ctypes_symbol_count",
)
ACTUAL_RESULT_FIELDS = frozenset({
    "schema", "status", "python", "candidate_family", "category",
    "controller_source_sha256", "category_source_relative",
    "category_source_sha256", "original_v4_relative", "original_v4_sha256",
    "ownership_audit_relative", "ownership_audit_sha256", "published_seed",
    "matrix_sha256", "case_denominator", "group_count", "cases_per_group",
    "baseline_reference_count", "baseline_reference_pids",
    "baseline_records_sha256", "second_reference_records_sha256",
    "candidate_records_sha256", "actual_baseline_cases",
    "actual_second_reference_cases", "actual_candidate_cases",
    "baseline_records", "second_reference_records", "candidate_records",
    "mismatch_count", "mismatches_by_group", "all_mismatches",
    "first_mismatch", "candidate_pid", "isolated_process_evidence",
    "source_provenance",
    "native_provenance", "audit_source_closure", "audit_closure_unchanged",
    "matcher_guard", "actual_reference_workers", "actual_candidate_workers",
    "clock_samples", "timing_trials_run", "workspace_files_written",
    "evidence_files_created", "benchmark_files_read", "hidden_cases_read",
    "performance", "source_to_binary_reproducibility",
    "candidate_qualified_for_hidden_benchmark", "final_winner_selected",
})
WORKER_RESULT_FIELDS = frozenset({
    "schema", "status", "python", "role", "category", "candidate_family",
    "controller_source_sha256", "category_source_relative",
    "category_source_sha256", "original_v4_relative", "original_v4_sha256",
    "ownership_audit_relative", "ownership_audit_sha256", "published_seed",
    "matrix_sha256", "frozen_baseline_records_sha256", "case_count",
    "records_sha256", "records", "source_provenance", "native_provenance",
    "audit_source_closure", "matcher_guard", "pid", "candidate_import_count",
    "actual_candidate_workers", "clock_samples", "timing_trials_run",
    "workspace_files_written", "evidence_files_created", "benchmark_files_read",
    "hidden_cases_read", "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})


class RecorderError(Exception):
    """Frozen case evidence or its safe publication was substituted."""


class SourceOnlyError(RecorderError):
    """A synthetic source control attempted an external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise RecorderError("category evidence is not exact canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64 and len(set(value)) > 1
            and all(c in "0123456789abcdef" for c in value),
            "an exact independently pinned lowercase SHA-256 is required: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON),
            "use the exact isolated, no-bytecode, frozen CPython 3.14.6")
    require(not any(n == "candidates" or n.startswith("candidates.")
                    for n in sys.modules),
            "the category recorder must never import a candidate or native engine")


def category_spec(value: Any) -> CategorySpec:
    require(type(value) is str and value in CATEGORIES,
            "select exactly one independently frozen public, scanner, or buffer category")
    spec = CATEGORIES[value]
    require(isinstance(spec, CategorySpec) and spec.name == value
            and spec.case_count == spec.group_count * spec.cases_per_group
            and (spec.name, spec.case_count) in {
                ("public", 864), ("scanner", 1024), ("buffer", 768),
            } and spec.published_seed > 0,
            "an immutable single-category denominator was replaced")
    return spec


def family_spec(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independently owned Rust, C, or Zig family")
    spec = FAMILIES[value]
    require(isinstance(spec, FamilySpec) and spec.name == value
            and spec.owned_ctypes is (value == "zig")
            and (spec.engine == spec.bridge) is (value == "c")
            and dict(spec.closure).get(spec.adapter) == spec.adapter_sha256
            and dict(spec.closure).get(spec.engine) == spec.engine_sha256
            and dict(spec.closure).get(spec.bridge) == spec.bridge_sha256,
            "an immutable independently owned native family was substituted")
    return spec


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in value)
            and "--" not in value,
            "an exact bounded lowercase nonescaping category-run label is required")
    return value


def approved_paths(family: Any, category: Any, label: Any) -> tuple[str, str]:
    owner = family_spec(family)
    selected = category_spec(category)
    slug = (owner.name + "-" + selected.name + "-contract-v2-"
            + validate_label(label))
    return (APPROVED_DIRECTORY + "/" + slug + ".json",
            APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json")


def safe_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "an exact owned no-follow relative path is mandatory")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative,
            "a category path escapes its frozen source or evidence root")
    return parts


def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def read_owned_regular(relative: str, expected: str, maximum: int) -> dict[str, Any]:
    parts = safe_parts(relative)
    expected = validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "a bounded frozen source or native artifact is mandatory")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid category project root")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a category source component follows a symlink")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode) and stat.S_ISREG(named.st_mode)
                and (first.st_dev, first.st_ino) == (named.st_dev, named.st_ino)
                and 0 < first.st_size <= maximum,
                "an exact source or owned binary was substituted")
        remaining = first.st_size
        parts_read: list[bytes] = []
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part), "a frozen source was truncated")
            parts_read.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "a frozen source has a hidden suffix")
        after = os.fstat(descriptor)
        require((first.st_dev, first.st_ino, first.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "a frozen source or native binary changed during authentication")
        value = b"".join(parts_read)
        require(hashlib.sha256(value).hexdigest() == expected,
                "a prospectively frozen category artifact changed: " + relative)
        return {"relative": relative, "sha256": expected, "bytes": len(value),
                "device": first.st_dev, "inode": first.st_ino}
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def authenticate_artifacts(category: CategorySpec, family: FamilySpec) -> dict[str, Any]:
    verify_runtime()
    sources = {
        "controller": read_owned_regular(CONTRACT_RELATIVE, CONTRACT_SHA256, MAX_SOURCE_BYTES),
        "original_v4": read_owned_regular(V4_RELATIVE, V4_SHA256, MAX_SOURCE_BYTES),
        "ownership_audit": read_owned_regular(AUDIT_RELATIVE, AUDIT_SHA256, MAX_SOURCE_BYTES),
        "category": read_owned_regular(category.source_relative, category.source_sha256,
                                        MAX_SOURCE_BYTES),
        "original_recorder": read_owned_regular(ORIGINAL_RECORDER_RELATIVE,
                                                  ORIGINAL_RECORDER_SHA256,
                                                  MAX_SOURCE_BYTES),
        "ownership_recorder": read_owned_regular(AUDIT_RECORDER_RELATIVE,
                                                   AUDIT_RECORDER_SHA256,
                                                   MAX_SOURCE_BYTES),
    }
    closure = {
        path: read_owned_regular(
            path, expected,
            MAX_BINARY_BYTES if path.endswith(".so") else MAX_SOURCE_BYTES,
        ) for path, expected in family.closure
    }
    return {
        "category": category.name, "family": family.name,
        "source_provenance": sources, "audit_source_closure": closure,
    }


def require_directory_identity(
    retained: tuple[int, int], expected: tuple[int, int], literal: tuple[int, int],
) -> None:
    require(type(retained) is tuple and type(expected) is tuple
            and type(literal) is tuple
            and len(retained) == len(expected) == len(literal) == 2
            and all(type(value) is int and value >= 0
                    for identity in (retained, expected, literal) for value in identity)
            and retained == expected == literal,
            "the literal category evidence path no longer names its owned directory")


def verify_retained_directory(preflight: Mapping[str, Any]) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain the exact category evidence directory descriptor")
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode), "the category evidence descriptor changed")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid literal evidence root")
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the literal category evidence parent became a symlink")
        literal = os.fstat(current)
        require_directory_identity(
            (retained.st_dev, retained.st_ino),
            (preflight.get("directory_device"), preflight.get("directory_inode")),
            (literal.st_dev, literal.st_ino),
        )
    finally:
        for current in reversed(opened):
            os.close(current)
    return descriptor


@contextlib.contextmanager
def preflight_fresh_outputs(
    family: str, category: str, label: str,
) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(family, category, label)
    report_parts, receipt_parts = safe_parts(report), safe_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "preflight exactly two distinct family-and-category-specific outputs")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid category evidence root")
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a category evidence parent is absent or follows a symlink")
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError("refusing to overwrite category evidence: " + basename)
        info = os.fstat(current)
        preflight = {
            "report_relative": report, "receipt_relative": receipt,
            "report_basename": report_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": info.st_dev, "directory_inode": info.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
        }
        verify_retained_directory(preflight)
        yield preflight
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def readback(preflight: Mapping[str, Any], basename: str, expected: bytes) -> None:
    directory = verify_retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        info = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(info.st_mode) and stat.S_ISREG(named.st_mode)
                and (info.st_dev, info.st_ino) == (named.st_dev, named.st_ino)
                and info.st_size == len(expected),
                "the durable category result changed inode, type, or complete size")
        remaining = len(expected)
        chunks: list[bytes] = []
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part), "category evidence was truncated")
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "category evidence has a hidden suffix")
        require(b"".join(chunks) == expected,
                "the complete category report or receipt was altered")
    finally:
        os.close(descriptor)
    verify_retained_directory(preflight)


def publish_atomic(
    preflight: Mapping[str, Any], document: Mapping[str, Any], kind: str,
) -> dict[str, Any]:
    require(kind in ("report", "receipt"), "publish only two frozen category outputs")
    directory = verify_retained_directory(preflight)
    basename = preflight[kind + "_basename"]
    raw = canonical(dict(document))
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "the complete category evidence exceeds its frozen bound")
    temporary = (".rebar-contract-v2-" + basename + "-" + str(os.getpid())
                 + "-" + hashlib.sha256(raw).hexdigest()[:20])
    safe_parts(temporary)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    verify_retained_directory(preflight)
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    identity: tuple[int, int] | None = None
    linked = False
    calls = 0
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode), "the owned category temporary is not regular")
        identity = (initial.st_dev, initial.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the owned category temporary was replaced")
        position = 0
        while position < len(raw):
            written = os.write(descriptor, raw[position:])
            require(type(written) is int and written > 0,
                    "the complete category result write was truncated")
            calls += 1
            position += written
        os.fsync(descriptor)
        require(os.fstat(descriptor).st_size == len(raw),
                "the complete category result temporary lost bytes")
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the category temporary changed before atomic linking")
        os.link(temporary, basename, src_dir_fd=directory, dst_dir_fd=directory,
                follow_symlinks=False)
        linked = True
        os.fsync(directory)
        verify_retained_directory(preflight)
        final = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((final.st_dev, final.st_ino) == identity,
                "the no-overwrite category publication was replaced")
        original = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((original.st_dev, original.st_ino) == identity,
                "refusing to unlink a replaced category temporary")
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
        verify_retained_directory(preflight)
    except BaseException:
        if not linked and identity is not None:
            try:
                named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
                if (named.st_dev, named.st_ino) == identity:
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, RecorderError):
                pass
        raise
    finally:
        os.close(descriptor)
    publication = {
        "path": preflight[kind + "_relative"], "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(), "actual_write_calls": calls,
        "file_fsync_completed": True, "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True, "owned_temporary_removed": True,
    }
    readback(preflight, basename, raw)
    return publication


def capture_stream(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve the complete bounded actual category stream: " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in document,
                "duplicate JSON keys cannot hide category mismatches")
        document[key] = value
    return document


def decode_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete canonical category process bytes are mandatory: " + label)
    try:
        document = json.loads(
            raw, object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                RecorderError("nonfinite category outcome evidence is forbidden")
            ),
        )
    except (json.JSONDecodeError, ValueError, TypeError, UnicodeError) as error:
        raise RecorderError("invalid complete category process JSON: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "the complete category process JSON is not canonical: " + label)
    return document


def valid_owner(value: Any, relative: str, expected: str) -> bool:
    return (type(value) is dict
            and set(value) == {"relative", "sha256", "bytes", "device", "inode"}
            and value.get("relative") == relative
            and value.get("sha256") == expected
            and type(value.get("bytes")) is int and value["bytes"] > 0
            and type(value.get("device")) is int and value["device"] >= 0
            and type(value.get("inode")) is int and value["inode"] > 0)


def validate_outcome(category: CategorySpec, outcome: Any) -> None:
    require(type(outcome) is dict and outcome.get("status") in ("return", "raise"),
            "a complete category return or genuine exception was hidden")
    value = "value" if outcome["status"] == "return" else "exception"
    if category.name == "public":
        expected = {"status", "callbacks", "warnings", value}
        require(type(outcome.get("callbacks")) is list,
                "a genuine public callback observation was hidden")
    elif category.name == "scanner":
        expected = {"status", "callbacks", "warnings", "combined_pattern",
                    "lexicon", value}
        require(type(outcome.get("callbacks")) is list,
                "a genuine scanner callback observation was hidden")
    else:
        expected = {"status", "stage", "match_before", "source_after",
                    "mutation", "warnings", value}
        require(type(outcome.get("stage")) is str,
                "a genuine buffer lifetime or exporter stage was hidden")
    require(set(outcome) == expected and type(outcome.get("warnings")) is list,
            "a complete source-ordered outcome or warning was omitted")
    if value == "exception":
        require(type(outcome.get("exception")) is dict,
                "a genuine category exception or traceback was omitted")


def validate_records(
    category: CategorySpec, matrix: list[dict[str, Any]], records: Any,
    expected_sha256: str, digestor: Callable[[Any], str] = digest,
) -> list[dict[str, Any]]:
    validate_digest(expected_sha256, category.name + " exact outcome vector")
    require(type(records) is list and len(records) == category.case_count
            and digestor(records) == expected_sha256,
            "a complete frozen category outcome vector was replaced")
    for case, record in zip(matrix, records, strict=True):
        fields = {"case", "outcome"} if category.name == "public" else {
            "case", "family", "outcome",
        }
        require(type(record) is dict and set(record) == fields
                and record.get("case") == case.get("case"),
                "a source-ordered category case or outcome was omitted")
        if category.name != "public":
            require(record["family"] == case.get("family"),
                    "a source-ordered category group was substituted")
        validate_outcome(category, record["outcome"])
    return records


def validate_guard(
    guard: Any, category: CategorySpec, family: FamilySpec,
) -> dict[str, Any]:
    expected_fields = frozenset((*GUARD_TRUE_FIELDS, *GUARD_COUNTER_FIELDS,
        "public_type_names_used_for_ownership", "actual_method_guard_checks",
        "actual_warning_registry_guard_checks", "owned_native_ffi_allowed"))
    require(type(guard) is dict and set(guard) == expected_fields,
            "the exact continuous warning-safe matcher guard was omitted")
    for name in GUARD_TRUE_FIELDS:
        require(guard[name] is True, "an actual matcher ownership guard was lost: " + name)
    require(guard["public_type_names_used_for_ownership"] is False
            and guard["actual_method_guard_checks"] == 2 * category.case_count
            and type(guard["actual_method_guard_checks"]) is int
            and guard["actual_warning_registry_guard_checks"] == 2 * category.case_count
            and type(guard["actual_warning_registry_guard_checks"]) is int
            and guard["owned_native_ffi_allowed"] is family.owned_ctypes,
            "the exact 2N per-category ownership or warning checks were hidden")
    for name in GUARD_COUNTER_FIELDS:
        require(type(guard[name]) is int and guard[name] >= 0,
                "an independently owned native guard counter was omitted")
    require((guard["owned_ctypes_load_count"] > 0) is family.owned_ctypes
            and (guard["owned_ctypes_symbol_count"] > 0) is family.owned_ctypes,
            "only the genuine Zig-owned native FFI may be used")
    return guard


def validate_source_provenance(value: Any, category: CategorySpec) -> None:
    require(type(value) is dict
            and set(value) == {"original_v4", "ownership_audit", "category"},
            "an original, ownership, or exact category source was omitted")
    for key, path, expected in (
        ("original_v4", V4_RELATIVE, V4_SHA256),
        ("ownership_audit", AUDIT_RELATIVE, AUDIT_SHA256),
        ("category", category.source_relative, category.source_sha256),
    ):
        require(valid_owner(value.get(key), path, expected),
                "an exact frozen category source owner changed: " + key)


def validate_native_provenance(value: Any, family: FamilySpec) -> None:
    require(type(value) is dict
            and set(value) == {"source", "native_engine", "native_bridge"},
            "all independently owned native components must be preserved")
    for key, path, expected in (
        ("source", family.adapter, family.adapter_sha256),
        ("native_engine", family.engine, family.engine_sha256),
        ("native_bridge", family.bridge, family.bridge_sha256),
    ):
        require(valid_owner(value.get(key), path, expected),
                "an exact family-owned candidate component changed: " + key)


def validate_closure(value: Any, family: FamilySpec) -> None:
    require(type(value) is dict and set(value) == set(dict(family.closure)),
            "a frozen owned source or binary closure was omitted")
    for path, expected in family.closure:
        require(valid_owner(value.get(path), path, expected),
                "an independently owned family artifact changed: " + path)


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"base64", "bytes", "sha256", "complete"}
            and value.get("complete") is True
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and type(value.get("base64")) is str,
            "a complete isolated process stream was omitted: " + label)
    validate_digest(value.get("sha256"), label + " complete stream")
    try:
        decoded = base64.b64decode(value["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise RecorderError("invalid complete encoded process stream: " + label) from error
    require(len(decoded) == value["bytes"]
            and hashlib.sha256(decoded).hexdigest() == value["sha256"]
            and base64.b64encode(decoded).decode("ascii") == value["base64"],
            "the complete isolated process stream was truncated: " + label)
    return decoded


def validate_isolated_processes(
    value: Any, result: Mapping[str, Any],
    category: CategorySpec, family: FamilySpec,
    matrix: list[dict[str, Any]],
    digestor: Callable[[Any], str],
) -> list[dict[str, Any]]:
    require(type(value) is list and len(value) == 3,
            "preserve exactly two genuine references and one genuine candidate process")
    roles = (
        ("reference_a", None, result["baseline_reference_pids"][0],
         result["baseline_records"], category.baseline_sha256),
        ("reference_b", None, result["baseline_reference_pids"][1],
         result["second_reference_records"], category.baseline_sha256),
        ("candidate-" + family.name, family.name, result["candidate_pid"],
         result["candidate_records"], result["candidate_records_sha256"]),
    )
    for evidence, (role, owner, expected_pid, records, record_sha) in zip(
        value, roles, strict=True,
    ):
        require(type(evidence) is dict
                and set(evidence) == {
                    "role", "category", "candidate_family", "pid",
                    "returncode", "stdout", "stderr",
                }
                and evidence["role"] == role
                and evidence["category"] == category.name
                and evidence["candidate_family"] == owner
                and type(evidence["pid"]) is int
                and evidence["pid"] == expected_pid
                and type(evidence["returncode"]) is int
                and evidence["returncode"] == 0,
                "an actual isolated worker role, family, PID, or exit was forged")
        stdout = decode_stream(evidence["stdout"], role + " stdout")
        stderr = decode_stream(evidence["stderr"], role + " stderr")
        require(stderr == b"", "a successful isolated worker concealed stderr")
        worker = decode_document(stdout, role + " complete worker document")
        require(set(worker) == WORKER_RESULT_FIELDS,
                "a complete isolated worker document field was hidden")
        expected = {
            "schema": CONTRACT_SCHEMA + "-isolated-category-worker",
            "status": "OBSERVED", "python": "3.14.6",
            "role": role, "category": category.name,
            "candidate_family": owner,
            "controller_source_sha256": CONTRACT_SHA256,
            "category_source_relative": category.source_relative,
            "category_source_sha256": category.source_sha256,
            "original_v4_relative": V4_RELATIVE,
            "original_v4_sha256": V4_SHA256,
            "ownership_audit_relative": AUDIT_RELATIVE,
            "ownership_audit_sha256": AUDIT_SHA256,
            "published_seed": category.published_seed,
            "matrix_sha256": category.matrix_sha256,
            "frozen_baseline_records_sha256": category.baseline_sha256,
            "case_count": category.case_count,
            "records_sha256": record_sha,
            "pid": expected_pid,
            "actual_candidate_workers": int(owner is not None),
            "clock_samples": 0, "timing_trials_run": 0,
            "workspace_files_written": 0, "evidence_files_created": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        for name, expected_value in expected.items():
            require(worker.get(name) == expected_value,
                    "a complete genuine isolated worker was changed: " + name)
        require(worker["records"] == records,
                "an encoded isolated process concealed or substituted case outcomes")
        validate_records(category, matrix, worker["records"], record_sha, digestor)
        require(worker["source_provenance"] == result["source_provenance"],
                "an encoded worker substituted its original source owner")
        if owner is None:
            require(worker["candidate_import_count"] == 0
                    and worker["native_provenance"] is None
                    and worker["audit_source_closure"] is None
                    and worker["matcher_guard"] is None,
                    "a frozen standard-library reference imported a candidate")
        else:
            require(type(worker["candidate_import_count"]) is int
                    and worker["candidate_import_count"] >= 3
                    and worker["native_provenance"] == result["native_provenance"]
                    and worker["audit_source_closure"] == result["audit_source_closure"]
                    and worker["matcher_guard"] == result["matcher_guard"],
                    "the genuine isolated native worker substituted its owned engine")
    return value


def validate_result(
    value: Any, category: CategorySpec, family: FamilySpec,
    matrix: list[dict[str, Any]], groups: tuple[str, ...],
    digestor: Callable[[Any], str] = digest,
) -> dict[str, Any]:
    require(type(value) is dict and set(value) == ACTUAL_RESULT_FIELDS,
            "the complete, exact, single-category controller result is mandatory")
    expected = {
        "schema": CONTRACT_SCHEMA + "-actual-category-result",
        "python": "3.14.6", "candidate_family": family.name,
        "category": category.name, "controller_source_sha256": CONTRACT_SHA256,
        "category_source_relative": category.source_relative,
        "category_source_sha256": category.source_sha256,
        "original_v4_relative": V4_RELATIVE, "original_v4_sha256": V4_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "published_seed": category.published_seed,
        "matrix_sha256": category.matrix_sha256,
        "case_denominator": category.case_count,
        "group_count": category.group_count,
        "cases_per_group": category.cases_per_group,
        "baseline_reference_count": 2,
        "baseline_records_sha256": category.baseline_sha256,
        "second_reference_records_sha256": category.baseline_sha256,
        "actual_baseline_cases": category.case_count,
        "actual_second_reference_cases": category.case_count,
        "actual_candidate_cases": category.case_count,
        "audit_closure_unchanged": True,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for name, expected_value in expected.items():
        require(value.get(name) == expected_value,
                "a frozen single-category observation was changed: " + name)
    require(type(matrix) is list and len(matrix) == category.case_count
            and digestor(matrix) == category.matrix_sha256
            and type(groups) is tuple and len(groups) == category.group_count
            and len(set(groups)) == len(groups),
            "an exact single-category case matrix or group denominator changed")
    pids = value["baseline_reference_pids"]
    candidate_pid = value["candidate_pid"]
    require(type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1]
            and type(candidate_pid) is int and candidate_pid > 0
            and candidate_pid not in pids,
            "the two independent Python references and candidate were not isolated")
    baseline = validate_records(category, matrix, value["baseline_records"],
                                category.baseline_sha256, digestor)
    second = validate_records(category, matrix, value["second_reference_records"],
                              category.baseline_sha256, digestor)
    candidate = validate_records(category, matrix, value["candidate_records"],
                                 value["candidate_records_sha256"], digestor)
    require(second == baseline,
            "the two actual complete Python reference vectors did not agree")
    by_group = {group: 0 for group in groups}
    mismatches: list[dict[str, Any]] = []
    for case, original, observed in zip(matrix, baseline, candidate, strict=True):
        if original["outcome"] != observed["outcome"]:
            group = case["operation"] if category.name == "public" else case["family"]
            require(group in by_group,
                    "a genuine mismatch was assigned to a foreign case group")
            by_group[group] += 1
            mismatches.append({
                "case": case["case"], "group": group, "input": case,
                "baseline_outcome": original["outcome"],
                "candidate_outcome": observed["outcome"],
            })
    require(value["all_mismatches"] == mismatches
            and type(value["mismatch_count"]) is int
            and value["mismatch_count"] == len(mismatches)
            and value["mismatches_by_group"] == by_group
            and value["first_mismatch"]
            == (mismatches[0] if mismatches else None)
            and value["status"] == ("FAIL" if mismatches else "PASS"),
            "a genuine source-ordered mismatch, group, or failure was omitted")
    validate_source_provenance(value["source_provenance"], category)
    validate_native_provenance(value["native_provenance"], family)
    validate_closure(value["audit_source_closure"], family)
    validate_guard(value["matcher_guard"], category, family)
    validate_isolated_processes(value["isolated_process_evidence"], value,
                                category, family, matrix, digestor)
    return value


def load_frozen_context(
    category: CategorySpec, family: FamilySpec,
) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
    verify_runtime()
    controller = importlib.import_module(CONTRACT_MODULE)
    specification = getattr(controller, "__spec__", None)
    loader = getattr(specification, "loader", None)
    require(getattr(controller, "__name__", None) == CONTRACT_MODULE
            and os.path.abspath(getattr(controller, "__file__", ""))
            == str(ROOT / CONTRACT_RELATIVE)
            and getattr(specification, "origin", None) == str(ROOT / CONTRACT_RELATIVE)
            and isinstance(loader, importlib.machinery.SourceFileLoader)
            and getattr(controller, "SCHEMA", None) == CONTRACT_SCHEMA,
            "the authenticated frozen category controller or loader was substituted")
    selected = controller.category_spec(category.name)
    owned = controller.family_spec(family.name)
    require(selected.name == category.name
            and selected.source_relative == category.source_relative
            and selected.source_sha256 == category.source_sha256
            and selected.matrix_sha256 == category.matrix_sha256
            and selected.baseline_sha256 == category.baseline_sha256
            and selected.published_seed == category.published_seed
            and selected.case_count == category.case_count
            and selected.group_count == category.group_count
            and selected.cases_per_group == category.cases_per_group,
            "the controller substituted an independently frozen category")
    require(owned.name == family.name and owned.adapter_module == family.module
            and owned.adapter_relative == family.adapter
            and owned.adapter_sha256 == family.adapter_sha256
            and owned.engine_relative == family.engine
            and owned.engine_sha256 == family.engine_sha256
            and owned.bridge_module == family.bridge_module
            and owned.bridge_relative == family.bridge
            and owned.bridge_sha256 == family.bridge_sha256
            and owned.owned_ctypes is family.owned_ctypes,
            "the controller substituted an independently owned native family")
    _, _, _, matrix, groups, _ = controller.load_prerequisites(selected)
    require(type(matrix) is list and len(matrix) == category.case_count
            and digest(matrix) == category.matrix_sha256
            and type(groups) is tuple and len(groups) == category.group_count,
            "the frozen category matrix was not generated exactly once")
    verify_runtime()
    return matrix, groups


def run_one_controller(category: CategorySpec, family: FamilySpec) -> dict[str, Any]:
    command = [str(PINNED_PYTHON), "-I", "-B", str(ROOT / CONTRACT_RELATIVE),
               "--candidate", family.name, "--category", category.name,
               "--oracle-source-sha256", CONTRACT_SHA256]
    try:
        process = subprocess.Popen(
            command, cwd=str(ROOT), shell=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"started": False, "pid": None, "returncode": None,
                "signal": None, "timed_out": False, "spawn_error": str(error),
                "stdout": b"", "stderr": b""}
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and type(process.returncode) is int,
            "the genuine controller lost its complete process streams or exit")
    return {"started": True, "pid": process.pid, "returncode": process.returncode,
            "signal": -process.returncode if process.returncode < 0 else None,
            "timed_out": timed_out, "spawn_error": None,
            "stdout": stdout, "stderr": stderr}


def decode_controller_failure(raw: bytes, category: CategorySpec,
                              family: FamilySpec) -> dict[str, Any]:
    result = decode_document(raw, "complete category failure stderr")
    required = {
        "schema", "status", "error_type", "error", "complete_traceback",
        "clock_samples", "timing_trials_run", "workspace_files_written",
        "evidence_files_created", "benchmark_files_read", "hidden_cases_read",
        "performance", "candidate_qualified_for_hidden_benchmark",
        "final_winner_selected",
    }
    require(type(result) is dict and required.issubset(result)
            and set(result).issubset(required | {"complete_worker_failure"})
            and result.get("schema") == CONTRACT_SCHEMA + "-complete-category-process-failure"
            and result.get("status") == "FAIL"
            and type(result.get("error_type")) is str
            and type(result.get("error")) is str
            and type(result.get("complete_traceback")) is str
            and result.get("clock_samples") == 0
            and result.get("timing_trials_run") == 0
            and result.get("workspace_files_written") == 0
            and result.get("evidence_files_created") == 0
            and result.get("benchmark_files_read") == 0
            and result.get("hidden_cases_read") == 0
            and result.get("performance") == "NOT MEASURED"
            and result.get("candidate_qualified_for_hidden_benchmark") is False
            and result.get("final_winner_selected") is False,
            "the complete genuine controller failure or traceback was forged")
    worker = result.get("complete_worker_failure")
    if worker is not None:
        require(type(worker) is dict
                and worker.get("category") == category.name
                and worker.get("role") in {
                    "reference_a", "reference_b", "candidate-" + family.name,
                }, "a genuine failed worker category or family was substituted")
        spawned = {"role", "category", "candidate_family", "pid",
                   "returncode", "stdout", "stderr"}
        unstarted = {"role", "category", "error_type", "error"}
        if set(worker) == unstarted:
            require(type(worker["error_type"]) is str
                    and bool(worker["error_type"])
                    and type(worker["error"]) is str and bool(worker["error"]),
                    "the failed worker spawn fabricated a PID or complete process stream")
        else:
            require(set(worker) in (spawned, spawned | {"validation_error"}),
                    "a failed isolated worker omitted its genuine complete process streams")
            expected_family = (family.name
                               if worker["role"] == "candidate-" + family.name
                               else None)
            require(worker["candidate_family"] == expected_family
                    and type(worker["pid"]) is int and worker["pid"] > 0
                    and type(worker["returncode"]) is int,
                    "a genuine failing worker PID, exit, or owned family was substituted")
            stdout = decode_stream(worker["stdout"], worker["role"] + " failed stdout")
            stderr = decode_stream(worker["stderr"], worker["role"] + " failed stderr")
            validation = worker.get("validation_error")
            if validation is not None:
                require(type(validation) is dict
                        and set(validation) == {"type", "message"}
                        and type(validation["type"]) is str and bool(validation["type"])
                        and type(validation["message"]) is str,
                        "the complete isolated worker validation failure was forged")
            require(worker["returncode"] != 0 or bool(stderr)
                    or validation is not None,
                    "a successful isolated worker was falsely reported as failed")
            require(type(stdout) is bytes and type(stderr) is bytes,
                    "a failing worker omitted genuine complete binary diagnostics")
    return result


def build_complete_report(
    category: CategorySpec, family: FamilySpec, label: str,
    process: Mapping[str, Any], before: Mapping[str, Any],
    after: Mapping[str, Any] | None,
    matrix: list[dict[str, Any]], groups: tuple[str, ...],
    *, post_run_error: str | None = None,
    digestor: Callable[[Any], str] = digest,
) -> dict[str, Any]:
    failures: list[str] = []
    stdout_raw, stderr_raw = process.get("stdout"), process.get("stderr")
    stdout = capture_stream(stdout_raw, "single category controller stdout")
    stderr = capture_stream(stderr_raw, "single category controller stderr")
    result: dict[str, Any] | None = None
    controller_failure: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append("the exact category controller could not start: "
                        + str(process.get("spawn_error")))
    if process.get("timed_out") is True:
        failures.append("the exact category controller exceeded its frozen timeout")
    if stdout_raw:
        try:
            result = validate_result(
                decode_document(stdout_raw, "complete category result stdout"),
                category, family, matrix, groups, digestor,
            )
        except (RecorderError, ValueError, TypeError, KeyError) as error:
            failures.append("invalid or incomplete complete category result: " + str(error))
    if stderr_raw:
        try:
            controller_failure = decode_controller_failure(stderr_raw, category, family)
        except (RecorderError, ValueError, TypeError, KeyError) as error:
            failures.append("invalid or incomplete controller failure stderr: " + str(error))
    if result is None:
        failures.append("the complete isolated candidate case outcome is unknown")
    elif result["status"] == "FAIL":
        failures.append("the frozen category exposed "
                        + str(result["mismatch_count"]) + " genuine mismatches")
    expected_returncode = (0 if result is not None and result["status"] == "PASS"
                           and controller_failure is None else 1)
    if process.get("returncode") != expected_returncode:
        failures.append("the genuine category process returned a crash, timeout, or incorrect exit")
    if controller_failure is not None:
        failures.append("the frozen controller preserved a genuine category worker failure")
    if post_run_error is not None:
        failures.append("post-run frozen category authentication failed: " + post_run_error)
    if before != after:
        failures.append("the frozen category sources or native family changed during the run")
    return {
        "schema": SCHEMA + "-complete-report",
        "status": "FAIL" if failures else "PASS",
        "label": validate_label(label),
        "category": category.name,
        "candidate_family": family.name,
        "python": {"implementation": "cpython", "version": [3, 14, 6],
                   "executable": str(PINNED_PYTHON)},
        "controller_relative": CONTRACT_RELATIVE,
        "controller_sha256": CONTRACT_SHA256,
        "original_v4_relative": V4_RELATIVE, "original_v4_sha256": V4_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_recorder_relative": ORIGINAL_RECORDER_RELATIVE,
        "original_recorder_sha256": ORIGINAL_RECORDER_SHA256,
        "ownership_recorder_relative": AUDIT_RECORDER_RELATIVE,
        "ownership_recorder_sha256": AUDIT_RECORDER_SHA256,
        "category_source_relative": category.source_relative,
        "category_source_sha256": category.source_sha256,
        "published_seed": category.published_seed,
        "matrix_sha256": category.matrix_sha256,
        "frozen_baseline_sha256": category.baseline_sha256,
        "case_denominator": category.case_count,
        "group_count": category.group_count,
        "cases_per_group": category.cases_per_group,
        "complete_artifacts_before": dict(before),
        "complete_artifacts_after": dict(after) if after is not None else None,
        "unchanged_before_after": before == after,
        "complete_controller_stdout": stdout,
        "complete_controller_stderr": stderr,
        "complete_controller_result": result,
        "complete_controller_process_failure": controller_failure,
        "observed_baseline_reference_count": (
            result["baseline_reference_count"] if result is not None else None
        ),
        "observed_baseline_cases": (
            result["actual_baseline_cases"] if result is not None else None
        ),
        "observed_second_reference_cases": (
            result["actual_second_reference_cases"] if result is not None else None
        ),
        "observed_candidate_cases": (
            result["actual_candidate_cases"] if result is not None else None
        ),
        "observed_mismatch_count": (
            result["mismatch_count"] if result is not None else None
        ),
        "observed_method_guard_checks": (
            result["matcher_guard"]["actual_method_guard_checks"]
            if result is not None else None
        ),
        "observed_warning_guard_checks": (
            result["matcher_guard"]["actual_warning_registry_guard_checks"]
            if result is not None else None
        ),
        "actual_controller_process_started": process.get("started") is True,
        "actual_controller_process_count": int(process.get("started") is True),
        "actual_controller_process_pid": process.get("pid"),
        "actual_controller_process_returncode": process.get("returncode"),
        "actual_controller_process_signal": process.get("signal"),
        "actual_controller_process_timed_out": process.get("timed_out") is True,
        "actual_controller_process_spawn_error": process.get("spawn_error"),
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def record_category(category: CategorySpec, family: FamilySpec,
                    label: str) -> dict[str, Any]:
    verify_runtime()
    before = authenticate_artifacts(category, family)
    matrix, groups = load_frozen_context(category, family)
    require(authenticate_artifacts(category, family) == before,
            "the frozen case matrix or native family changed during preparation")
    with preflight_fresh_outputs(family.name, category.name, label) as preflight:
        verify_retained_directory(preflight)
        process = run_one_controller(category, family)
        verify_retained_directory(preflight)
        after: dict[str, Any] | None = None
        post_run_error: str | None = None
        try:
            after = authenticate_artifacts(category, family)
        except (OSError, RecorderError) as error:
            post_run_error = str(error)
        report = build_complete_report(
            category, family, label, process, before, after, matrix, groups,
            post_run_error=post_run_error,
        )
        report_publication = publish_atomic(preflight, report, "report")
        receipt = {
            "schema": SCHEMA + "-publication-receipt",
            "publication_status": "PASS",
            "category_result_status": report["status"],
            "category": category.name, "candidate_family": family.name,
            "label": label,
            "controller_relative": CONTRACT_RELATIVE,
            "controller_sha256": CONTRACT_SHA256,
            "category_source_sha256": category.source_sha256,
            "published_seed": category.published_seed,
            "matrix_sha256": category.matrix_sha256,
            "frozen_baseline_sha256": category.baseline_sha256,
            "case_denominator": category.case_count,
            "group_count": category.group_count,
            "cases_per_group": category.cases_per_group,
            "adapter_sha256": family.adapter_sha256,
            "native_engine_sha256": family.engine_sha256,
            "native_bridge_sha256": family.bridge_sha256,
            "report_publication": report_publication,
            "receipt_relative": preflight["receipt_relative"],
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
            "clock_samples": 0, "timing_trials_run": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        receipt_publication = publish_atomic(preflight, receipt, "receipt")
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded",
        "status": report["status"], "publication_status": "PASS",
        "category": category.name, "candidate_family": family.name,
        "label": label, "case_denominator": category.case_count,
        "observed_baseline_cases": report["observed_baseline_cases"],
        "observed_second_reference_cases": report["observed_second_reference_cases"],
        "observed_candidate_cases": report["observed_candidate_cases"],
        "observed_mismatch_count": report["observed_mismatch_count"],
        "report_publication": report_publication,
        "receipt_publication": receipt_publication,
        "actual_controller_process_count": report["actual_controller_process_count"],
        "all_failure_reasons": report["all_failure_reasons"],
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {name: 0 for name in (
        "blocked_reads", "blocked_writes", "blocked_imports", "blocked_workers",
        "blocked_threads", "blocked_clocks", "blocked_gc_collections",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def deny(key: str, message: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[key] += 1
            raise SourceOnlyError(message)
        return blocked

    def install(owner: Any, name: str, replacement: Any) -> None:
        actual = getattr(owner, name, None)
        if actual is not None:
            installed.append((owner, name, actual))
            setattr(owner, name, replacement)

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name,
                    deny("blocked_reads", "a synthetic category control cannot read files"))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (os, "link"), (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name,
                    deny("blocked_writes", "a synthetic category control cannot write files"))
        install(importlib, "import_module", deny(
            "blocked_imports", "a synthetic category control cannot import candidates",
        ))
        install(subprocess, "Popen", deny(
            "blocked_workers", "a synthetic category control cannot start workers",
        ))
        install(subprocess, "run", deny(
            "blocked_workers", "a synthetic category control cannot start workers",
        ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "a synthetic category control cannot start threads",
        ))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns"):
            install(time, name, deny(
                "blocked_clocks", "a synthetic category control cannot sample clocks",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections", "a synthetic category control cannot collect garbage",
        ))
        yield effects
    finally:
        for owner, name, actual in reversed(installed):
            setattr(owner, name, actual)


def synthetic_owner(relative: str, source_hash: str,
                    inode: int = 17) -> dict[str, Any]:
    return {"relative": relative, "sha256": source_hash,
            "bytes": 23, "device": 7, "inode": inode}


def synthetic_isolated_evidence(
    category: CategorySpec, family: FamilySpec, result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    roles = (
        ("reference_a", None, result["baseline_reference_pids"][0],
         result["baseline_records"], category.baseline_sha256),
        ("reference_b", None, result["baseline_reference_pids"][1],
         result["second_reference_records"], category.baseline_sha256),
        ("candidate-" + family.name, family.name, result["candidate_pid"],
         result["candidate_records"], result["candidate_records_sha256"]),
    )
    for role, owner, pid, records, record_sha in roles:
        worker = {
            "schema": CONTRACT_SCHEMA + "-isolated-category-worker",
            "status": "OBSERVED", "python": "3.14.6", "role": role,
            "category": category.name, "candidate_family": owner,
            "controller_source_sha256": CONTRACT_SHA256,
            "category_source_relative": category.source_relative,
            "category_source_sha256": category.source_sha256,
            "original_v4_relative": V4_RELATIVE, "original_v4_sha256": V4_SHA256,
            "ownership_audit_relative": AUDIT_RELATIVE,
            "ownership_audit_sha256": AUDIT_SHA256,
            "published_seed": category.published_seed,
            "matrix_sha256": category.matrix_sha256,
            "frozen_baseline_records_sha256": category.baseline_sha256,
            "case_count": category.case_count, "records_sha256": record_sha,
            "records": records,
            "source_provenance": copy.deepcopy(result["source_provenance"]),
            "native_provenance": copy.deepcopy(result["native_provenance"])
            if owner is not None else None,
            "audit_source_closure": copy.deepcopy(result["audit_source_closure"])
            if owner is not None else None,
            "matcher_guard": copy.deepcopy(result["matcher_guard"])
            if owner is not None else None,
            "pid": pid, "candidate_import_count": 3 if owner is not None else 0,
            "actual_candidate_workers": int(owner is not None),
            "clock_samples": 0, "timing_trials_run": 0,
            "workspace_files_written": 0, "evidence_files_created": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        evidence.append({
            "role": role, "category": category.name,
            "candidate_family": owner, "pid": pid, "returncode": 0,
            "stdout": capture_stream(canonical(worker), role + " synthetic stdout"),
            "stderr": capture_stream(b"", role + " synthetic stderr"),
        })
    return evidence


def synthetic_category(
    category: CategorySpec, family: FamilySpec,
) -> tuple[list[dict[str, Any]], tuple[str, ...], list[dict[str, Any]],
           Callable[[Any], str], dict[str, Any]]:
    groups = tuple("synthetic-group-" + format(index, "02d")
                   for index in range(category.group_count))
    matrix: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for group_index, group in enumerate(groups):
        for offset in range(category.cases_per_group):
            index = group_index * category.cases_per_group + offset
            case = {"case": category.name + "-synthetic-" + format(index, "04d")}
            if category.name == "public":
                case["operation"] = group
                case["domain"] = "text" if index % 2 == 0 else "bytes"
                outcome = {"status": "return", "callbacks": [],
                           "warnings": [], "value": index}
                record = {"case": case["case"], "outcome": outcome}
            elif category.name == "scanner":
                case["family"] = group
                outcome = {"status": "return", "callbacks": [], "warnings": [],
                           "combined_pattern": "synthetic",
                           "lexicon": [], "value": index}
                record = {"case": case["case"], "family": group, "outcome": outcome}
            else:
                case["family"] = group
                outcome = {"status": "return", "stage": "synthetic",
                           "match_before": None, "source_after": None,
                           "mutation": None, "warnings": [], "value": index}
                record = {"case": case["case"], "family": group, "outcome": outcome}
            matrix.append(case)
            records.append(record)
    matrix_bytes, records_bytes = canonical(matrix), canonical(records)

    def synthetic_digest(value: Any) -> str:
        raw = canonical(value)
        if raw == matrix_bytes:
            return category.matrix_sha256
        if raw == records_bytes:
            return category.baseline_sha256
        return hashlib.sha256(raw).hexdigest()

    closure = {path: synthetic_owner(path, source_hash, index + 31)
               for index, (path, source_hash) in enumerate(family.closure)}
    guard = {name: True for name in GUARD_TRUE_FIELDS}
    guard.update({
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": 2 * category.case_count,
        "actual_warning_registry_guard_checks": 2 * category.case_count,
        "owned_native_ffi_allowed": family.owned_ctypes,
        "cached_original_matcher_descendant_count": 0,
        "cached_original_holder_count": 0,
        "owned_ctypes_load_count": 1 if family.owned_ctypes else 0,
        "owned_ctypes_symbol_count": 9 if family.owned_ctypes else 0,
    })
    sources = {
        "original_v4": synthetic_owner(V4_RELATIVE, V4_SHA256),
        "ownership_audit": synthetic_owner(AUDIT_RELATIVE, AUDIT_SHA256),
        "category": synthetic_owner(category.source_relative, category.source_sha256),
    }
    provenance = {
        "source": synthetic_owner(family.adapter, family.adapter_sha256),
        "native_engine": synthetic_owner(family.engine, family.engine_sha256),
        "native_bridge": synthetic_owner(family.bridge, family.bridge_sha256),
    }
    result = {
        "schema": CONTRACT_SCHEMA + "-actual-category-result",
        "status": "PASS", "python": "3.14.6", "candidate_family": family.name,
        "category": category.name, "controller_source_sha256": CONTRACT_SHA256,
        "category_source_relative": category.source_relative,
        "category_source_sha256": category.source_sha256,
        "original_v4_relative": V4_RELATIVE, "original_v4_sha256": V4_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "published_seed": category.published_seed,
        "matrix_sha256": category.matrix_sha256,
        "case_denominator": category.case_count,
        "group_count": category.group_count,
        "cases_per_group": category.cases_per_group,
        "baseline_reference_count": 2,
        "baseline_reference_pids": [101, 102],
        "baseline_records_sha256": category.baseline_sha256,
        "second_reference_records_sha256": category.baseline_sha256,
        "candidate_records_sha256": category.baseline_sha256,
        "actual_baseline_cases": category.case_count,
        "actual_second_reference_cases": category.case_count,
        "actual_candidate_cases": category.case_count,
        "baseline_records": records,
        "second_reference_records": copy.deepcopy(records),
        "candidate_records": copy.deepcopy(records),
        "mismatch_count": 0,
        "mismatches_by_group": {group: 0 for group in groups},
        "all_mismatches": [], "first_mismatch": None,
        "candidate_pid": 103,
        "source_provenance": sources,
        "native_provenance": provenance,
        "audit_source_closure": closure,
        "audit_closure_unchanged": True,
        "matcher_guard": guard,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 1,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    result["isolated_process_evidence"] = synthetic_isolated_evidence(
        category, family, result,
    )
    return matrix, groups, records, synthetic_digest, result


def synthetic_controller_error(category: CategorySpec,
                               family: FamilySpec) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA + "-complete-category-process-failure",
        "status": "FAIL", "error_type": "WorkerFailure",
        "error": "synthetic independently guarded category worker failed",
        "complete_traceback": "synthetic complete frozen traceback\n",
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "complete_worker_failure": {
            "role": "candidate-" + family.name,
            "category": category.name,
            "candidate_family": family.name,
            "pid": 103, "returncode": -11,
            "stdout": capture_stream(b"synthetic native crash\n", "synthetic worker"),
            "stderr": capture_stream(b"synthetic complete native traceback\n",
                                      "synthetic worker"),
        },
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []
    with source_only_boundary() as effects:

        def accept(label: str, condition: Any) -> None:
            require(condition, "synthetic public recorder control failed: " + label)
            accepted.append(label)

        def reject(label: str, operation: Callable[[], Any]) -> None:
            try:
                operation()
            except (RecorderError, OSError, ValueError, TypeError, KeyError, IndexError):
                rejected.append(label)
                return
            raise RecorderError("a synthetic public recorder poison was accepted: " + label)

        for category_name, category in CATEGORIES.items():
            for family_name, family in FAMILIES.items():
                matrix, groups, records, fake_digest, result = synthetic_category(category, family)
                accept(category_name + "-" + family_name + "-complete-single-category",
                       validate_result(result, category, family, matrix, groups,
                                       fake_digest) is result)
                accept(category_name + "-" + family_name + "-exact-denominator",
                       len(matrix) == len(records) == category.case_count
                       and len(groups) == category.group_count)
                accept(category_name + "-" + family_name + "-exact-two-n-guards",
                       result["matcher_guard"]["actual_method_guard_checks"]
                       == result["matcher_guard"]["actual_warning_registry_guard_checks"]
                       == 2 * category.case_count)
                report_path, receipt_path = approved_paths(
                    family_name, category_name, "synthetic-proof",
                )
                accept(category_name + "-" + family_name + "-exact-two-output-paths",
                       report_path != receipt_path
                       and ("/" + family_name + "-" + category_name + "-contract-v2-")
                       in report_path
                       and ("/" + family_name + "-" + category_name + "-contract-v2-")
                       in receipt_path)

                before = {"family": family_name, "category": category_name,
                          "synthetic": True}
                raw = canonical(result)
                passing = {"started": True, "pid": 701, "returncode": 0,
                           "signal": None, "timed_out": False,
                           "spawn_error": None, "stdout": raw, "stderr": b""}
                report = build_complete_report(
                    category, family, "synthetic-proof", passing, before, before,
                    matrix, groups, digestor=fake_digest,
                )
                accept(category_name + "-" + family_name + "-complete-pass-report",
                       report["status"] == "PASS"
                       and report["observed_baseline_reference_count"] == 2
                       and report["observed_baseline_cases"] == category.case_count
                       and report["observed_second_reference_cases"] == category.case_count
                       and report["observed_candidate_cases"] == category.case_count
                       and report["observed_method_guard_checks"] == 2 * category.case_count
                       and report["observed_warning_guard_checks"] == 2 * category.case_count
                       and report["complete_controller_result"] == result)

                failed_result = copy.deepcopy(result)
                failed_result["candidate_records"][0]["outcome"]["value"] = -1
                failed_result["candidate_records_sha256"] = digest(
                    failed_result["candidate_records"],
                )
                bad_case = matrix[0]
                group = (bad_case["operation"] if category_name == "public"
                         else bad_case["family"])
                mismatch = {
                    "case": bad_case["case"], "group": group,
                    "input": bad_case,
                    "baseline_outcome": failed_result["baseline_records"][0]["outcome"],
                    "candidate_outcome": failed_result["candidate_records"][0]["outcome"],
                }
                failed_result["status"] = "FAIL"
                failed_result["mismatch_count"] = 1
                failed_result["all_mismatches"] = [mismatch]
                failed_result["first_mismatch"] = mismatch
                failed_result["mismatches_by_group"][group] = 1
                failed_result["isolated_process_evidence"] = synthetic_isolated_evidence(
                    category, family, failed_result,
                )
                failed_raw = canonical(failed_result)
                failed_process = {**passing, "returncode": 1, "stdout": failed_raw}
                failed = build_complete_report(
                    category, family, "synthetic-proof", failed_process, before,
                    before, matrix, groups, digestor=fake_digest,
                )
                accept(category_name + "-" + family_name + "-preserve-genuine-mismatch",
                       failed["status"] == "FAIL"
                       and failed["observed_mismatch_count"] == 1
                       and failed["observed_candidate_cases"] == category.case_count
                       and failed["complete_controller_result"] == failed_result
                       and failed["actual_controller_process_returncode"] == 1)

                error = synthetic_controller_error(category, family)
                error_raw = canonical(error)
                process_error = {**passing, "returncode": 1,
                                 "stdout": b"", "stderr": error_raw}
                unknown = build_complete_report(
                    category, family, "synthetic-proof", process_error,
                    before, before, matrix, groups, digestor=fake_digest,
                )
                accept(category_name + "-" + family_name + "-preserve-stderr-worker-failure",
                       unknown["status"] == "FAIL"
                       and unknown["complete_controller_process_failure"] == error
                       and unknown["complete_controller_result"] is None
                       and unknown["observed_baseline_cases"] is None
                       and unknown["observed_second_reference_cases"] is None
                       and unknown["observed_candidate_cases"] is None
                       and unknown["observed_mismatch_count"] is None
                       and unknown["observed_method_guard_checks"] is None
                       and unknown["observed_warning_guard_checks"] is None
                       and unknown["complete_controller_stderr"]["sha256"]
                       == hashlib.sha256(error_raw).hexdigest())

                accept(category_name + "-" + family_name + "-authenticate-complete-failed-worker",
                       decode_controller_failure(error_raw, category, family) == error)
                for field in ("role", "category", "candidate_family", "pid",
                              "returncode", "stdout", "stderr"):
                    broken_failure = copy.deepcopy(error)
                    del broken_failure["complete_worker_failure"][field]
                    reject(category_name + "-" + family_name + "-missing-failed-worker-" + field,
                           lambda broken_failure=broken_failure:
                           decode_controller_failure(canonical(broken_failure),
                                                     category, family))
                worker_attacks: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
                    ("wrong-failed-worker-role", lambda value: value["complete_worker_failure"].__setitem__("role", "candidate-foreign")),
                    ("wrong-failed-worker-category", lambda value: value["complete_worker_failure"].__setitem__("category", "foreign")),
                    ("wrong-failed-worker-family", lambda value: value["complete_worker_failure"].__setitem__("candidate_family", "foreign")),
                    ("missing-failed-worker-pid", lambda value: value["complete_worker_failure"].__setitem__("pid", 0)),
                    ("fabricated-failed-worker-exit", lambda value: value["complete_worker_failure"].__setitem__("returncode", "signal")),
                    ("truncated-failed-worker-stdout", lambda value: value["complete_worker_failure"]["stdout"].__setitem__("bytes", 1)),
                    ("forged-failed-worker-stdout-hash", lambda value: value["complete_worker_failure"]["stdout"].__setitem__("sha256", AUDIT_SHA256)),
                    ("forged-failed-worker-stdout-base64", lambda value: value["complete_worker_failure"]["stdout"].__setitem__("base64", "e30=")),
                    ("truncated-failed-worker-stderr", lambda value: value["complete_worker_failure"]["stderr"].__setitem__("bytes", 1)),
                    ("forged-failed-worker-stderr-hash", lambda value: value["complete_worker_failure"]["stderr"].__setitem__("sha256", AUDIT_SHA256)),
                    ("forged-failed-worker-stderr-base64", lambda value: value["complete_worker_failure"]["stderr"].__setitem__("base64", "e30=")),
                    ("extra-failed-worker-field", lambda value: value["complete_worker_failure"].__setitem__("forged", True)),
                ]
                for title, mutate in worker_attacks:
                    broken_failure = copy.deepcopy(error)
                    mutate(broken_failure)
                    reject(category_name + "-" + family_name + "-" + title,
                           lambda broken_failure=broken_failure:
                           decode_controller_failure(canonical(broken_failure),
                                                     category, family))
                failed_reference = copy.deepcopy(error)
                failed_reference["complete_worker_failure"]["role"] = "reference_a"
                failed_reference["complete_worker_failure"]["candidate_family"] = None
                accept(category_name + "-" + family_name + "-preserve-failed-reference",
                       decode_controller_failure(canonical(failed_reference),
                                                 category, family) == failed_reference)
                failed_spawn = copy.deepcopy(error)
                failed_spawn["complete_worker_failure"] = {
                    "role": "candidate-" + family_name,
                    "category": category_name,
                    "error_type": "OSError",
                    "error": "synthetic isolated worker could not start",
                }
                accept(category_name + "-" + family_name + "-preserve-unknown-worker-spawn",
                       decode_controller_failure(canonical(failed_spawn),
                                                 category, family) == failed_spawn)
                for invented, invented_value in (
                    ("pid", 103),
                    ("returncode", -11),
                    ("stdout", capture_stream(b"invented stdout", "synthetic poison")),
                    ("stderr", capture_stream(b"invented stderr", "synthetic poison")),
                    ("candidate_family", family_name),
                ):
                    forged_spawn = copy.deepcopy(failed_spawn)
                    forged_spawn["complete_worker_failure"][invented] = invented_value
                    reject(category_name + "-" + family_name
                           + "-invented-spawn-" + invented,
                           lambda forged_spawn=forged_spawn:
                           decode_controller_failure(canonical(forged_spawn),
                                                     category, family))

                crashed = {**passing, "returncode": -11, "signal": 11,
                           "stdout": b"synthetic native crash\n",
                           "stderr": b"synthetic complete signal traceback\n"}
                crash = build_complete_report(
                    category, family, "synthetic-proof", crashed,
                    before, before, matrix, groups, digestor=fake_digest,
                )
                accept(category_name + "-" + family_name + "-preserve-unknown-native-crash",
                       crash["status"] == "FAIL"
                       and crash["actual_controller_process_signal"] == 11
                       and crash["observed_baseline_reference_count"] is None
                       and crash["observed_baseline_cases"] is None
                       and crash["observed_second_reference_cases"] is None
                       and crash["observed_candidate_cases"] is None
                       and crash["observed_mismatch_count"] is None
                       and crash["observed_method_guard_checks"] is None
                       and crash["observed_warning_guard_checks"] is None
                       and crash["complete_controller_result"] is None)

                timed = {**crashed, "returncode": -9, "signal": 9,
                         "timed_out": True}
                timeout = build_complete_report(
                    category, family, "synthetic-proof", timed,
                    before, before, matrix, groups, digestor=fake_digest,
                )
                accept(category_name + "-" + family_name + "-preserve-unknown-timeout",
                       timeout["status"] == "FAIL"
                       and timeout["actual_controller_process_timed_out"] is True
                       and timeout["observed_baseline_cases"] is None
                       and timeout["observed_second_reference_cases"] is None
                       and timeout["observed_candidate_cases"] is None)

                unstarted = {"started": False, "pid": None, "returncode": None,
                             "signal": None, "timed_out": False,
                             "spawn_error": "synthetic controller start failure",
                             "stdout": b"", "stderr": b""}
                start_failure = build_complete_report(
                    category, family, "synthetic-proof", unstarted,
                    before, before, matrix, groups, digestor=fake_digest,
                )
                accept(category_name + "-" + family_name + "-preserve-unknown-spawn",
                       start_failure["status"] == "FAIL"
                       and start_failure["actual_controller_process_count"] == 0
                       and start_failure["observed_candidate_cases"] is None)

                poisons: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
                    ("missing-controller-schema", lambda value: value.pop("schema")),
                    ("foreign-controller-schema", lambda value: value.__setitem__("schema", "borrowed")),
                    ("foreign-category", lambda value: value.__setitem__("category", "foreign")),
                    ("foreign-family", lambda value: value.__setitem__("candidate_family", "external")),
                    ("foreign-source", lambda value: value.__setitem__("controller_source_sha256", AUDIT_SHA256)),
                    ("foreign-category-source", lambda value: value.__setitem__("category_source_sha256", AUDIT_SHA256)),
                    ("foreign-matrix", lambda value: value.__setitem__("matrix_sha256", AUDIT_SHA256)),
                    ("foreign-baseline", lambda value: value.__setitem__("baseline_records_sha256", AUDIT_SHA256)),
                    ("foreign-seed", lambda value: value.__setitem__("published_seed", 1)),
                    ("combined-category-denominator", lambda value: value.__setitem__("case_denominator", 864 + 1024 + 768)),
                    ("missing-case", lambda value: value["candidate_records"].pop()),
                    ("reordered-cases", lambda value: value["candidate_records"].reverse()),
                    ("hidden-baseline-case", lambda value: value["baseline_records"].pop()),
                    ("hidden-second-baseline-case", lambda value: value["second_reference_records"].pop()),
                    ("foreign-record-digest", lambda value: value.__setitem__("candidate_records_sha256", AUDIT_SHA256)),
                    ("missing-reference-worker", lambda value: value.__setitem__("actual_reference_workers", 1)),
                    ("borrowed-reference-process", lambda value: value.__setitem__("baseline_reference_pids", [101, 101])),
                    ("borrowed-candidate-process", lambda value: value.__setitem__("candidate_pid", 101)),
                    ("missing-candidate-worker", lambda value: value.__setitem__("actual_candidate_workers", 0)),
                    ("missing-isolated-process", lambda value: value["isolated_process_evidence"].pop()),
                    ("reordered-isolated-processes", lambda value: value["isolated_process_evidence"].reverse()),
                    ("foreign-isolated-role", lambda value: value["isolated_process_evidence"][0].__setitem__("role", "candidate-foreign")),
                    ("foreign-isolated-category", lambda value: value["isolated_process_evidence"][0].__setitem__("category", "foreign")),
                    ("foreign-isolated-family", lambda value: value["isolated_process_evidence"][2].__setitem__("candidate_family", "foreign")),
                    ("foreign-isolated-pid", lambda value: value["isolated_process_evidence"][0].__setitem__("pid", 100001)),
                    ("failing-isolated-exit", lambda value: value["isolated_process_evidence"][0].__setitem__("returncode", 1)),
                    ("truncated-isolated-stdout", lambda value: value["isolated_process_evidence"][0]["stdout"].__setitem__("bytes", 1)),
                    ("foreign-isolated-stdout-hash", lambda value: value["isolated_process_evidence"][0]["stdout"].__setitem__("sha256", AUDIT_SHA256)),
                    ("foreign-isolated-stdout-bytes", lambda value: value["isolated_process_evidence"][0]["stdout"].__setitem__("base64", "e30=")),
                    ("foreign-isolated-stderr", lambda value: value["isolated_process_evidence"][0].__setitem__("stderr", capture_stream(b"foreign diagnostics", "synthetic poison"))),
                    ("hidden-mismatch", lambda value: value.__setitem__("mismatch_count", 1)),
                    ("hidden-group", lambda value: value["mismatches_by_group"].pop(groups[0])),
                    ("false-status", lambda value: value.__setitem__("status", "FAIL")),
                    ("missing-native-proof", lambda value: value.__setitem__("native_provenance", {})),
                    ("foreign-native", lambda value: value["native_provenance"]["native_engine"].__setitem__("sha256", AUDIT_SHA256)),
                    ("missing-source-closure", lambda value: value["audit_source_closure"].pop(family.adapter)),
                    ("foreign-source-closure", lambda value: value["audit_source_closure"][family.adapter].__setitem__("sha256", AUDIT_SHA256)),
                    ("missing-guard", lambda value: value.__setitem__("matcher_guard", {})),
                    ("missing-method-guards", lambda value: value["matcher_guard"].__setitem__("actual_method_guard_checks", 2 * category.case_count - 1)),
                    ("missing-warning-guards", lambda value: value["matcher_guard"].__setitem__("actual_warning_registry_guard_checks", 2 * category.case_count - 1)),
                    ("borrowed-standard-matcher", lambda value: value["matcher_guard"].__setitem__("original_matchers_blocked", False)),
                    ("foreign-native-ffi", lambda value: value["matcher_guard"].__setitem__("owned_native_ffi_allowed", not family.owned_ctypes)),
                    ("clock-sample", lambda value: value.__setitem__("clock_samples", 1)),
                    ("timing-trial", lambda value: value.__setitem__("timing_trials_run", 1)),
                    ("evidence-write", lambda value: value.__setitem__("evidence_files_created", 1)),
                    ("hidden-case", lambda value: value.__setitem__("hidden_cases_read", 1)),
                    ("premature-winner", lambda value: value.__setitem__("final_winner_selected", True)),
                    ("false-reproducibility", lambda value: value.__setitem__("source_to_binary_reproducibility", "ESTABLISHED")),
                ]
                for title, mutate in poisons:
                    broken = copy.deepcopy(result)
                    mutate(broken)
                    reject(category_name + "-" + family_name + "-" + title,
                           lambda broken=broken: validate_result(
                               broken, category, family, matrix, groups, fake_digest,
                           ))
                for other_name, other in CATEGORIES.items():
                    if other_name != category_name:
                        reject(category_name + "-" + family_name + "-reject-category-" + other_name,
                               lambda other=other: validate_result(
                                   result, other, family, matrix, groups, fake_digest,
                               ))
                for other_name, other in FAMILIES.items():
                    if other_name != family_name:
                        reject(category_name + "-" + family_name + "-reject-family-" + other_name,
                               lambda other=other: validate_result(
                                   result, category, other, matrix, groups, fake_digest,
                               ))

        accept("literal-evidence-directory-identity",
               require_directory_identity((17, 31), (17, 31), (17, 31)) is None)
        for name, retained, expected, literal in (
            ("renamed-evidence-directory", (17, 31), (17, 31), (17, 32)),
            ("replaced-evidence-device", (17, 31), (17, 31), (18, 31)),
            ("replaced-retained-inode", (17, 32), (17, 31), (17, 32)),
            ("truncated-directory-identity", (17, 31), (17, 31), (17,)),
            ("boolean-directory-identity", (17, 31), (17, 31), (True, 31)),
            ("negative-directory-identity", (17, 31), (17, 31), (-1, 31)),
        ):
            reject(name, lambda retained=retained, expected=expected, literal=literal:
                   require_directory_identity(retained, expected, literal))
        for label in ("", "..", "../escape", "/absolute", "a/b", "a--b", "-bad",
                      "bad-", "bad_name", "CAPS", "a" * 65):
            reject("unsafe-label-" + repr(label),
                   lambda label=label: approved_paths("rust", "public", label))
        for name in ("", "all", "combined", "public,scanner", "../public"):
            reject("combined-or-foreign-category-" + repr(name),
                   lambda name=name: category_spec(name))
        for name in ("", "all", "re", "_sre", "../zig", "external"):
            reject("combined-or-foreign-family-" + repr(name),
                   lambda name=name: family_spec(name))
        for title, operation in (
            ("read", lambda: builtins.open("synthetic-read")),
            ("write", lambda: os.write(1, b"synthetic")),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("worker", lambda: subprocess.Popen(["synthetic"])),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("garbage-collection", lambda: gc.collect()),
        ):
            reject("block-actual-" + title, operation)
        accept("all-seven-actual-side-effects-blocked",
               all(count > 0 for count in effects.values()))
        accept("exactly-three-independent-categories",
               set(CATEGORIES) == {"public", "scanner", "buffer"})
        accept("exactly-three-independent-candidate-families",
               set(FAMILIES) == {"rust", "c", "zig"})
        accept("no-real-candidate-imported",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "controller_relative": CONTRACT_RELATIVE,
        "controller_sha256": CONTRACT_SHA256,
        "original_v4_sha256": V4_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_recorder_sha256": ORIGINAL_RECORDER_SHA256,
        "ownership_recorder_sha256": AUDIT_RECORDER_SHA256,
        "families": ["rust", "c", "zig"],
        "categories": ["public", "scanner", "buffer"],
        "category_case_counts": {
            "public": 864, "scanner": 1024, "buffer": 768,
        },
        "category_guard_counts": {
            "public": 1728, "scanner": 2048, "buffer": 1536,
        },
        "accepted_control_count": len(accepted), "accepted_controls": accepted,
        "rejected_control_count": len(rejected), "rejected_controls": rejected,
        "blocked_effects": effects,
        "actual_candidate_workers": 0, "actual_reference_workers": 0,
        "actual_controller_processes": 0,
        "real_candidate_files_read": 0, "real_native_binary_files_read": 0,
        "real_candidate_imported": False,
        "evidence_files_created": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record", action="store_true")
    parser.add_argument("--candidate", choices=tuple(FAMILIES))
    parser.add_argument("--category", choices=tuple(CATEGORIES))
    parser.add_argument("--label")
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    verify_runtime()
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) in (None, False) for name in (
            "record", "candidate", "category", "label",
            "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "a synthetic control cannot select or execute an actual family or category")
        result = source_self_test()
    else:
        require(options.record is True,
                "actual evidence requires the explicit single-category record mode")
        category = category_spec(options.category)
        family = family_spec(options.candidate)
        label = validate_label(options.label)
        require(validate_digest(options.oracle_source_sha256, "frozen category controller")
                == CONTRACT_SHA256,
                "pin the exact independently approved category controller")
        require(validate_digest(options.matrix_sha256, category.name + " case matrix")
                == category.matrix_sha256,
                "pin the exact one-category source-ordered case matrix")
        require(validate_digest(options.candidate_source_sha256, "owned family adapter")
                == family.adapter_sha256,
                "pin the exact independently owned family adapter")
        require(validate_digest(options.native_engine_sha256, "owned family engine")
                == family.engine_sha256,
                "pin the exact independently owned family engine")
        require(validate_digest(options.native_bridge_sha256, "owned family bridge")
                == family.bridge_sha256,
                "pin the exact independently owned family bridge")
        result = record_category(category, family, label)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RecorderError, OSError, subprocess.SubprocessError) as error:
        print("frozen single-category correctness recording failed closed: "
              + str(error), file=sys.stderr)
        raise SystemExit(1) from error
