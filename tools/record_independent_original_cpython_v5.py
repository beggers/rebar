#!/usr/bin/env python3
"""Durably preserve one independently owned, frozen V5 CPython regex test.

Only explicit ``--record`` starts one genuine V5 original-test controller.
The exact candidate adapter and native artifacts must be supplied by the
caller, so future genuinely fixed C implementations cannot inherit stale pins.
The synthetic ``--self-test`` never reads candidates, starts a worker, takes a
clock sample, opens a final holdout, or creates evidence.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass
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
SOURCE_RELATIVE = "tools/record_independent_original_cpython_v5.py"
SCHEMA = "rebar-independent-original-cpython-recorder-v5"
ORIGINAL_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
ORIGINAL_MODULE = "tools.independent_original_cpython_suite_v5"
# Replaced with the independently reviewed final V5 digest before publication.
ORIGINAL_SHA256 = "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
ORIGINAL_SCHEMA = "rebar-independent-original-cpython-re-full-methods-v5"
PREVIOUS_ORACLE_RELATIVE = "tools/independent_original_cpython_suite_v4.py"
PREVIOUS_ORACLE_SHA256 = "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3"
PREVIOUS_RECORDER_RELATIVE = "tools/record_independent_original_cpython_v4.py"
PREVIOUS_RECORDER_SHA256 = "eecafcae7dc27f4be7ac6b1886b51dfe54d5d83843541dca68e018d1caf1683b"
HARNESS_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
HARNESS_SHA256 = "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
IDENTITY_GUARD_RELATIVE = "tools/rust_original_cpython_suite_v2.py"
IDENTITY_GUARD_SHA256 = "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267"
WARNING_GUARD_RELATIVE = "tools/rust_original_cpython_suite_v3.py"
WARNING_GUARD_SHA256 = "55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2"
MATRIX_SHA256 = "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
BASELINE_SHA256 = "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
ORIGINAL_TEST_SHA256 = "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
ORIGINAL_SUPPORT_SHA256 = "519f9d36eccf2fda59f78c3480bb4b6e35b2ecb51551f11e0ac03ecbfa503159"
ORIGINAL_WARNINGS_HELPER_SHA256 = "fc02de4d91bae3988079e3fb3fec3da96ae467fd548295745c2846af179f3870"
ORIGINAL_CORPUS_SHA256 = "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_CTYPES = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/ctypes/__init__.py"
)
PINNED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
TOTAL_METHODS = 165
PUBLIC_METHODS = 152
PRIVATE_WAIVER_COUNT = 13
GUARD_CHECKS = 304
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 192 * 1024 * 1024
PRIVATE_METHODS = (
    "DebugTests.test_debug_flag", "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one", "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable", "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness", "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules", "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc", "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
RECORD_FIELDS = frozenset({
    "test", "source_ast_sha256", "status", "tests_run", "failure_count",
    "error_count", "skip_count", "failure_tracebacks", "error_tracebacks",
    "skip_reasons",
})
GUARD_TRUE_FIELDS = (
    "original_matchers_blocked", "adapter_import_quarantined", "native_sre_blocked",
    "builtins_import_guarded", "importlib_import_guarded",
    "actual_object_identity_guarded", "warning_registry_introspection_safe",
    "warning_registry_exactly_absent", "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
GUARD_COUNTER_FIELDS = (
    "cached_original_matcher_descendant_count", "cached_original_holder_count",
    "owned_ctypes_load_count", "owned_ctypes_symbol_count",
)
TRUSTED_CTYPES_GUARD_FIELDS = (
    "trusted_stdlib_ctypes_preloaded",
    "trusted_stdlib_ctypes_builtin_verified",
    "trusted_stdlib_ctypes_pythonapi_initialized",
    "trusted_stdlib_ctypes_source_sha256",
)
V4_RESULT_FIELDS = frozenset({
    "schema", "status", "python", "candidate_family", "controller_source_sha256",
    "test_harness_relative", "test_harness_sha256", "identity_guard_relative",
    "identity_guard_sha256", "warning_guard_relative", "warning_guard_sha256",
    "matrix_sha256", "original_source_sha256", "original_support_sha256",
    "original_warnings_helper_sha256", "original_corpus_sha256",
    "all_original_method_count", "actual_public_method_count", "private_waiver_count",
    "private_waivers", "public_waivers", "all_original_methods_executed",
    "all_original_methods_qualified", "baseline_records_sha256",
    "candidate_records_sha256", "baseline_records", "candidate_records",
    "mismatch_count", "all_mismatches", "baseline_pid", "candidate_pid",
    "native_provenance", "matcher_guard", "actual_candidate_workers",
    "actual_localedef_workers", "actual_private_temporary_directories_created",
    "actual_private_locale_outputs_created",
    "all_private_temporary_directories_removed", "clock_samples",
    "timing_trials_run", "workspace_files_written", "benchmark_files_read",
    "hidden_cases_read", "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})
RESULT_FIELDS = V4_RESULT_FIELDS | frozenset({
    "previous_oracle_relative", "previous_oracle_sha256",
    "isolated_process_evidence",
})
WORKER_RESULT_FIELDS = frozenset({
    "schema", "status", "python", "role", "engine", "pid",
    "candidate_family", "controller_source_sha256",
    "previous_oracle_relative", "previous_oracle_sha256",
    "test_harness_relative", "test_harness_sha256",
    "identity_guard_relative", "identity_guard_sha256",
    "warning_guard_relative", "warning_guard_sha256",
    "original_source_sha256", "original_support_sha256",
    "original_warnings_helper_sha256", "original_corpus_sha256",
    "matrix_sha256", "all_original_method_count",
    "actual_public_method_count", "private_waiver_count",
    "private_waivers", "public_waivers", "all_original_methods_executed",
    "all_original_methods_qualified", "records_sha256", "records",
    "pass_count", "skip_count", "failure_count", "native_provenance",
    "matcher_guard", "multiprocessing_start_method",
    "original_bigmem_dry_run", "original_bigmem_maximum_size",
    "actual_private_locales", "captured_original_stdout",
    "captured_original_stderr", "actual_candidate_workers",
    "legacy_original_worker_role", "legacy_original_worker_engine",
    "clock_samples", "timing_trials_run", "workspace_files_written",
    "benchmark_files_read", "hidden_cases_read", "performance",
    "final_winner_selected",
})
PRIVATE_LOCALE_FIELDS = frozenset({
    "actual_localedef_executable", "private_temporary_directories_created",
    "private_locale_outputs_created", "actual_localedef_workers",
    "iso_8859_1_verified", "utf_8_verified", "system_locales_installed",
    "workspace_files_written", "temporary_directory_removed",
})


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    adapter_module: str
    adapter_relative: str
    engine_relative: str
    bridge_module: str
    bridge_relative: str
    owned_ctypes: bool


FAMILIES = {
    "rust": FamilySpec(
        "rust", "candidates.rust_candidate", "candidates/rust_candidate.py",
        "candidates/_rust_engine.so", "candidates._rust_bridge",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX, False,
    ),
    "c": FamilySpec(
        "c", "candidates.vm_candidate", "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates._vm_native", "candidates/_vm_native" + EXTENSION_SUFFIX,
        False,
    ),
    "zig": FamilySpec(
        "zig", "candidates.zig_candidate", "candidates/zig_candidate.py",
        "candidates/_zig_probe.so", "candidates._zig_bridge",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX, True,
    ),
}


@dataclass(frozen=True, slots=True)
class OwnerPins:
    family: str
    original: str
    matrix: str
    baseline: str
    candidate: str
    native_engine: str
    native_bridge: str


class RecorderError(Exception):
    """An original method, candidate owner, or atomic result is unauthenticated."""


class SourceOnlyError(RecorderError):
    """A synthetic source control attempted a real effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise RecorderError("evidence is not exact complete canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64 and len(set(value)) > 1
            and all(c in "0123456789abcdef" for c in value),
            "an independently pinned lowercase SHA-256 is required: " + label)
    return value


def verify_runtime() -> None:
    expected = str(ROOT / SOURCE_RELATIVE)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.realpath(str(ROOT)) == str(ROOT)
            and os.path.abspath(__file__) == expected
            and os.path.realpath(__file__) == expected
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
            "use only isolated, no-bytecode, frozen CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the original recorder cannot import a candidate or matching engine")


def family_spec(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independently owned Rust, C, or Zig family")
    spec = FAMILIES[value]
    require(isinstance(spec, FamilySpec) and spec.name == value
            and spec.owned_ctypes is (value == "zig")
            and (spec.engine_relative == spec.bridge_relative) is (value == "c"),
            "an exact independently owned candidate family was substituted")
    return spec


def validate_pins(pins: OwnerPins) -> FamilySpec:
    require(isinstance(pins, OwnerPins), "all candidate source pins must be explicit")
    spec = family_spec(pins.family)
    for field in ("original", "matrix", "baseline", "candidate",
                  "native_engine", "native_bridge"):
        validate_digest(getattr(pins, field), field)
    require(pins.original == ORIGINAL_SHA256 and pins.matrix == MATRIX_SHA256
            and pins.baseline == BASELINE_SHA256,
            "pin the independently approved V5 original source, matrix, and baseline")
    require((pins.native_engine == pins.native_bridge) is (spec.name == "c"),
            "only C may use the same independently owned bridge and native engine")
    return spec


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in value)
            and "--" not in value,
            "an exact bounded lowercase nonescaping original-run label is required")
    return value


def approved_paths(family: Any, label: Any) -> tuple[str, str]:
    spec = family_spec(family)
    basename = spec.name + "-original-v5-" + validate_label(label)
    return (APPROVED_DIRECTORY + "/" + basename + ".json",
            APPROVED_DIRECTORY + "/" + basename + "-publication-receipt.json")


def safe_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "an exact owned no-follow relative path is required")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative,
            "an original source or publication path escaped the repository")
    return parts


def directory_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) \
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def read_owned_regular(relative: str, expected: str, maximum: int) -> dict[str, Any]:
    parts = safe_parts(relative)
    expected = validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "an exact bounded original source or native binary is required")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid source root")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an original source parent became a symlink")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino) == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum,
                "the exact frozen source or native binary was substituted")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part), "an exact source was truncated")
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "a frozen source has a hidden suffix")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "an exact frozen source changed during authentication")
        raw = b"".join(chunks)
        require(hashlib.sha256(raw).hexdigest() == expected,
                "an independently frozen source or native binary changed: " + relative)
        return {"relative": relative, "sha256": expected, "bytes": len(raw),
                "device": before.st_dev, "inode": before.st_ino}
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def valid_owner(value: Any, relative: str, expected: str) -> bool:
    return (type(value) is dict
            and set(value) == {"relative", "sha256", "bytes", "device", "inode"}
            and value.get("relative") == relative
            and value.get("sha256") == expected
            and type(value.get("bytes")) is int and value["bytes"] > 0
            and type(value.get("device")) is int and value["device"] >= 0
            and type(value.get("inode")) is int and value["inode"] > 0)


def authenticate_candidate(pins: OwnerPins) -> dict[str, dict[str, Any]]:
    spec = validate_pins(pins)
    source = read_owned_regular(spec.adapter_relative, pins.candidate, MAX_SOURCE_BYTES)
    engine = read_owned_regular(spec.engine_relative, pins.native_engine, MAX_BINARY_BYTES)
    bridge = engine if spec.name == "c" else read_owned_regular(
        spec.bridge_relative, pins.native_bridge, MAX_BINARY_BYTES,
    )
    result = {"source": source, "native_engine": engine, "native_bridge": bridge}
    validate_native(result, spec, pins)
    return result


def validate_native(value: Any, spec: FamilySpec, pins: OwnerPins) -> None:
    require(type(value) is dict
            and set(value) == {"source", "native_engine", "native_bridge"},
            "all exact independently owned native components are mandatory")
    for key, path, expected in (
        ("source", spec.adapter_relative, pins.candidate),
        ("native_engine", spec.engine_relative, pins.native_engine),
        ("native_bridge", spec.bridge_relative, pins.native_bridge),
    ):
        require(valid_owner(value.get(key), path, expected),
                "an exact independently owned original component changed: " + key)
    require((value["native_engine"] == value["native_bridge"]) is (spec.name == "c"),
            "native bridge identity cannot be borrowed between candidate families")


def authenticate_frozen_sources(pins: OwnerPins) -> None:
    validate_pins(pins)
    for relative, source_hash in (
        (ORIGINAL_RELATIVE, ORIGINAL_SHA256),
        (PREVIOUS_ORACLE_RELATIVE, PREVIOUS_ORACLE_SHA256),
        (PREVIOUS_RECORDER_RELATIVE, PREVIOUS_RECORDER_SHA256),
        (HARNESS_RELATIVE, HARNESS_SHA256),
        (IDENTITY_GUARD_RELATIVE, IDENTITY_GUARD_SHA256),
        (WARNING_GUARD_RELATIVE, WARNING_GUARD_SHA256),
    ):
        read_owned_regular(relative, source_hash, MAX_SOURCE_BYTES)


def load_frozen_context(pins: OwnerPins) -> list[dict[str, Any]]:
    verify_runtime()
    authenticate_frozen_sources(pins)
    suite = importlib.import_module(ORIGINAL_MODULE)
    loader_spec = getattr(suite, "__spec__", None)
    expected = str(ROOT / ORIGINAL_RELATIVE)
    require(getattr(suite, "__name__", None) == ORIGINAL_MODULE
            and os.path.abspath(getattr(suite, "__file__", "")) == expected
            and os.path.realpath(getattr(suite, "__file__", "")) == expected
            and getattr(loader_spec, "origin", None) == expected
            and isinstance(getattr(loader_spec, "loader", None),
                           importlib.machinery.SourceFileLoader)
            and getattr(suite, "SCHEMA", None) == ORIGINAL_SCHEMA
            and getattr(suite, "MATRIX_SHA256", None) == MATRIX_SHA256
            and getattr(suite, "BASELINE_SHA256", None) == BASELINE_SHA256
            and getattr(suite, "ORIGINAL_METHOD_COUNT", None) == TOTAL_METHODS
            and getattr(suite, "PUBLIC_METHOD_COUNT", None) == PUBLIC_METHODS
            and getattr(suite, "PRIVATE_WAIVER_COUNT", None) == PRIVATE_WAIVER_COUNT,
            "the exact independently approved V5 original controller was substituted")
    ours = family_spec(pins.family)
    native = suite.family_spec(ours.name)
    require(native.name == ours.name and native.adapter_module == ours.adapter_module
            and native.adapter_relative == ours.adapter_relative
            and native.engine_relative == ours.engine_relative
            and native.bridge_module == ours.bridge_module
            and native.bridge_relative == ours.bridge_relative
            and native.owned_ctypes is ours.owned_ctypes,
            "the V5 original suite selected an unowned candidate family")
    _, _, harness, matrix = suite.load_frozen_oracles()
    require(getattr(harness, "METHOD_MATRIX_SHA256", None) == MATRIX_SHA256
            and getattr(harness, "BASELINE_RECORDS_SHA256", None) == BASELINE_SHA256
            and getattr(harness, "TEST_SOURCE_SHA256", None) == ORIGINAL_TEST_SHA256
            and getattr(harness, "SUPPORT_SHA256", None) == ORIGINAL_SUPPORT_SHA256
            and getattr(harness, "WARNINGS_HELPER_SHA256", None)
            == ORIGINAL_WARNINGS_HELPER_SHA256
            and getattr(harness, "CORPUS_SHA256", None) == ORIGINAL_CORPUS_SHA256
            and tuple(getattr(harness, "PRIVATE_METHODS", ())) == PRIVATE_METHODS
            and type(matrix) is list and len(matrix) == TOTAL_METHODS
            and digest(matrix) == MATRIX_SHA256,
            "the exact unchanged original 165-method Python matrix was substituted")
    verify_runtime()
    return matrix


def require_directory_identity(retained: tuple[int, int],
                               expected: tuple[int, int],
                               literal: tuple[int, int]) -> None:
    require(type(retained) is tuple and type(expected) is tuple
            and type(literal) is tuple
            and len(retained) == len(expected) == len(literal) == 2
            and all(type(value) is int and value >= 0
                    for identity in (retained, expected, literal) for value in identity)
            and retained == expected == literal,
            "the literal original evidence path no longer names its owned directory")


def verify_retained_directory(preflight: Mapping[str, Any]) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain the exact no-follow original evidence directory")
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode), "the retained directory was replaced")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid literal evidence root")
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a literal original evidence parent became a symlink")
        actual = os.fstat(current)
        require_directory_identity(
            (retained.st_dev, retained.st_ino),
            (preflight.get("directory_device"), preflight.get("directory_inode")),
            (actual.st_dev, actual.st_ino),
        )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)
    return preflight["directory_descriptor"]


@contextlib.contextmanager
def preflight_fresh_outputs(family: str, label: str) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(family, label)
    report_parts, receipt_parts = safe_parts(report), safe_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "preflight exactly two distinct owned original V5 evidence paths")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid evidence root")
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an original evidence parent follows a symlink")
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError("refusing to overwrite original evidence: " + basename)
        actual = os.fstat(current)
        result = {
            "report_relative": report, "receipt_relative": receipt,
            "report_basename": report_parts[-1], "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": actual.st_dev, "directory_inode": actual.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
        }
        verify_retained_directory(result)
        yield result
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def readback(preflight: Mapping[str, Any], basename: str, expected: bytes) -> None:
    directory = verify_retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        actual = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(actual.st_mode) and stat.S_ISREG(named.st_mode)
                and (actual.st_dev, actual.st_ino) == (named.st_dev, named.st_ino)
                and actual.st_size == len(expected),
                "the durable original report or receipt was substituted")
        remaining = len(expected)
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the genuine complete original publication was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "original evidence has a hidden suffix")
        require(b"".join(chunks) == expected,
                "genuine complete original vectors or tracebacks were altered")
    finally:
        os.close(descriptor)
    verify_retained_directory(preflight)


def publish_atomic(preflight: Mapping[str, Any], document: Mapping[str, Any],
                   kind: str) -> dict[str, Any]:
    require(kind in ("report", "receipt"), "publish only exact original report/receipt")
    directory = verify_retained_directory(preflight)
    raw = canonical(dict(document))
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "the complete original-suite publication exceeds its safe bound")
    basename = preflight[kind + "_basename"]
    temporary = ".rebar-original-v5-" + basename + "-" + str(os.getpid()) \
        + "-" + hashlib.sha256(raw).hexdigest()[:20]
    safe_parts(temporary)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL \
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    verify_retained_directory(preflight)
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    identity: tuple[int, int] | None = None
    linked = False
    write_calls = 0
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode), "the atomic original temporary is not regular")
        identity = (initial.st_dev, initial.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the owned original temporary was replaced")
        position = 0
        while position < len(raw):
            count = os.write(descriptor, raw[position:])
            require(type(count) is int and count > 0,
                    "the complete original-suite publication was truncated")
            position += count
            write_calls += 1
        os.fsync(descriptor)
        require(os.fstat(descriptor).st_size == len(raw),
                "the complete original publication lost bytes")
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the original evidence temporary changed before atomic publication")
        os.link(temporary, basename, src_dir_fd=directory,
                dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.fsync(directory)
        verify_retained_directory(preflight)
        destination = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((destination.st_dev, destination.st_ino) == identity,
                "the exact no-overwrite original result was substituted")
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "refusing to unlink an unowned original temporary")
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
    result = {
        "path": preflight[kind + "_relative"], "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(), "actual_write_calls": write_calls,
        "file_fsync_completed": True, "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True, "owned_temporary_removed": True,
    }
    readback(preflight, basename, raw)
    return result


def capture_stream(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve the complete genuine original process stream: " + label)
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "complete": True}


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "duplicate fields cannot hide an original test failure")
        result[key] = value
    return result


def decode_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "a complete bounded original process document is required: " + label)
    try:
        result = json.loads(raw, object_pairs_hook=unique_object,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                RecorderError("nonfinite original evidence is forbidden")
                            ))
    except (UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise RecorderError("invalid complete original process JSON: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "the complete original process JSON was clipped or substituted: " + label)
    return result


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"base64", "bytes", "sha256", "complete"}
            and value.get("complete") is True
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and type(value.get("base64")) is str,
            "a complete isolated original process stream was omitted: " + label)
    validate_digest(value.get("sha256"), label)
    try:
        result = base64.b64decode(value["base64"], validate=True)
    except (TypeError, ValueError) as error:
        raise RecorderError("invalid complete isolated original stream: " + label) from error
    require(len(result) == value["bytes"]
            and hashlib.sha256(result).hexdigest() == value["sha256"]
            and base64.b64encode(result).decode("ascii") == value["base64"],
            "the genuine complete isolated original stream was truncated: " + label)
    return result


def validate_original_record(requirement: Mapping[str, Any], actual: Any) -> dict[str, Any]:
    require(type(actual) is dict and set(actual) == RECORD_FIELDS
            and actual.get("test") == requirement.get("test")
            and actual.get("source_ast_sha256") == requirement.get("source_ast_sha256")
            and actual.get("status") in ("PASS", "FAIL", "SKIP")
            and actual.get("tests_run") == 1,
            "an original Python method or complete case outcome was omitted")
    for count, records in (
        ("failure_count", "failure_tracebacks"),
        ("error_count", "error_tracebacks"),
        ("skip_count", "skip_reasons"),
    ):
        tracebacks = actual.get(records)
        require(type(tracebacks) is list and all(type(item) is str for item in tracebacks)
                and type(actual.get(count)) is int
                and actual[count] == len(tracebacks),
                "a genuine original traceback or named skip was hidden")
    expected = ("FAIL" if actual["failure_count"] or actual["error_count"]
                else "SKIP" if actual["skip_count"] else "PASS")
    require(actual["status"] == expected
            and not (actual["skip_count"]
                     and (actual["failure_count"] or actual["error_count"])),
            "an original failure or genuine debug skip was misclassified")
    return actual


def validate_guard(actual: Any, spec: FamilySpec) -> None:
    fields = frozenset((*GUARD_TRUE_FIELDS, *GUARD_COUNTER_FIELDS,
        *TRUSTED_CTYPES_GUARD_FIELDS,
        "actual_method_guard_checks", "actual_warning_registry_guard_checks",
        "public_type_names_used_for_ownership", "owned_native_ffi_allowed"))
    require(type(actual) is dict and set(actual) == fields,
            "the exact continuous warning-safe matcher guard was omitted")
    for name in GUARD_TRUE_FIELDS:
        require(actual[name] is True, "a genuine ownership guard was lost: " + name)
    require(actual["public_type_names_used_for_ownership"] is False
            and type(actual["actual_method_guard_checks"]) is int
            and actual["actual_method_guard_checks"] == GUARD_CHECKS
            and type(actual["actual_warning_registry_guard_checks"]) is int
            and actual["actual_warning_registry_guard_checks"] == GUARD_CHECKS
            and actual["owned_native_ffi_allowed"] is spec.owned_ctypes,
            "all 304 matcher checks and 304 warnings checks are mandatory")
    for name in GUARD_COUNTER_FIELDS:
        require(type(actual[name]) is int and actual[name] >= 0,
                "a genuine warning or native FFI guard counter was omitted")
    require(
        actual["trusted_stdlib_ctypes_preloaded"] is spec.owned_ctypes
        and actual["trusted_stdlib_ctypes_builtin_verified"]
        is spec.owned_ctypes
        and actual["trusted_stdlib_ctypes_pythonapi_initialized"]
        is spec.owned_ctypes
        and actual["trusted_stdlib_ctypes_source_sha256"]
        == (PINNED_CTYPES_SHA256 if spec.owned_ctypes else None),
        "the authenticated pre-guard standard ctypes policy was changed",
    )
    require((actual["owned_ctypes_load_count"] > 0) is spec.owned_ctypes
            and (actual["owned_ctypes_symbol_count"] > 0) is spec.owned_ctypes,
            "only independently owned Zig may dynamically load its exact own engine")


def trusted_ctypes_guard(actual: Mapping[str, Any]) -> dict[str, Any]:
    return {name: actual[name] for name in TRUSTED_CTYPES_GUARD_FIELDS}


def validate_result(
    value: Any, matrix: list[dict[str, Any]], pins: OwnerPins,
    owners: Mapping[str, Any], *, digestor: Callable[[Any], str] = digest,
) -> dict[str, Any]:
    spec = validate_pins(pins)
    require(type(value) is dict and set(value) == RESULT_FIELDS,
            "all exact V5 original-suite fields must be retained")
    expected = {
        "schema": ORIGINAL_SCHEMA + "-actual-original-candidate-result",
        "python": "3.14.6", "candidate_family": spec.name,
        "controller_source_sha256": pins.original,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "original_source_sha256": ORIGINAL_TEST_SHA256,
        "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
        "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS), "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "baseline_records_sha256": BASELINE_SHA256,
        "actual_candidate_workers": 1,
        "actual_localedef_workers": 4,
        "actual_private_temporary_directories_created": 2,
        "actual_private_locale_outputs_created": 4,
        "all_private_temporary_directories_removed": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for name, expected_value in expected.items():
        require(value.get(name) == expected_value,
                "a frozen full-method original observation changed: " + name)
    require(type(matrix) is list and len(matrix) == TOTAL_METHODS
            and digestor(matrix) == MATRIX_SHA256,
            "the independently frozen 165-method original matrix changed")
    public = [record for record in matrix if record.get("classification") == "public"]
    private = [record for record in matrix
               if record.get("classification") == "named-private-waiver"]
    require(len(public) == PUBLIC_METHODS and len(private) == PRIVATE_WAIVER_COUNT
            and tuple(item["test"] for item in private) == PRIVATE_METHODS,
            "an original public method or named private waiver was concealed")
    baseline, candidate = value["baseline_records"], value["candidate_records"]
    require(type(baseline) is list and type(candidate) is list
            and len(baseline) == len(candidate) == PUBLIC_METHODS
            and digestor(baseline) == BASELINE_SHA256
            and digestor(candidate) == value["candidate_records_sha256"],
            "the complete original baseline or candidate vector was changed")
    mismatches: list[dict[str, Any]] = []
    for case, original, observed in zip(public, baseline, candidate, strict=True):
        original = validate_original_record(case, original)
        observed = validate_original_record(case, observed)
        if original != observed:
            mismatches.append({"test": case["test"],
                               "baseline": original, "candidate": observed})
    require(sum(item["status"] == "PASS" for item in baseline) == 151
            and sum(item["status"] == "SKIP" for item in baseline) == 1
            and sum(item["status"] == "FAIL" for item in baseline) == 0,
            "the exact genuine original Python baseline was substituted")
    skip = [item for item in baseline if item["status"] == "SKIP"]
    require(skip[0]["test"] == "ReTests.test_memory_leaks"
            and skip[0]["skip_reasons"] == ["requires debug build"],
            "the single original debug-build-only skip was changed")
    require(type(value["mismatch_count"]) is int
            and value["mismatch_count"] == len(mismatches)
            and value["all_mismatches"] == mismatches
            and value["status"] == ("FAIL" if mismatches else "PASS"),
            "a genuine original test failure or traceback was omitted")
    require(type(value["baseline_pid"]) is int and value["baseline_pid"] > 0
            and type(value["candidate_pid"]) is int and value["candidate_pid"] > 0
            and value["baseline_pid"] != value["candidate_pid"],
            "the genuine original baseline and native candidate were not isolated")
    validate_native(owners, spec, pins)
    validate_native(value["native_provenance"], spec, pins)
    require(value["native_provenance"] == dict(owners),
            "the selected candidate source or owned native engine was replaced")
    validate_guard(value["matcher_guard"], spec)
    validate_isolated_processes(value["isolated_process_evidence"], value,
                                matrix, pins, digestor)
    return value


def validate_worker_result(
    worker: Any, result: Mapping[str, Any], matrix: list[dict[str, Any]],
    pins: OwnerPins, *, role: str, family: str | None, pid: int,
    records: list[dict[str, Any]], record_hash: str,
    digestor: Callable[[Any], str],
) -> dict[str, Any]:
    spec = validate_pins(pins)
    require(type(worker) is dict and set(worker) == WORKER_RESULT_FIELDS,
            "all 51 exact frozen V5 isolated original worker fields are mandatory")
    baseline = family is None
    expected = {
        "schema": ORIGINAL_SCHEMA + "-isolated-original-worker",
        "python": "3.14.6", "role": role,
        "engine": "stdlib" if baseline else spec.name,
        "candidate_family": family, "pid": pid,
        "controller_source_sha256": pins.original,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "original_source_sha256": ORIGINAL_TEST_SHA256,
        "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
        "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS), "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "records_sha256": record_hash,
        "multiprocessing_start_method": "fork",
        "original_bigmem_dry_run": True,
        "original_bigmem_maximum_size": 5_147,
        "actual_candidate_workers": 0 if baseline else 1,
        "legacy_original_worker_role": role if baseline else "rust",
        "legacy_original_worker_engine": "stdlib" if baseline else "rust",
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }
    for name, expected_value in expected.items():
        actual = worker.get(name)
        require(
            (actual is expected_value if type(expected_value) is bool
             else type(actual) is int and actual == expected_value
             if type(expected_value) is int
             else actual == expected_value),
            "a frozen original worker observation was changed: " + name,
        )
    actual_records = worker["records"]
    require(type(actual_records) is list
            and len(actual_records) == PUBLIC_METHODS
            and actual_records == records
            and digestor(actual_records) == record_hash,
            "a complete source-ordered original worker vector was substituted")
    public = [item for item in matrix if item.get("classification") == "public"]
    require(len(public) == PUBLIC_METHODS,
            "every original public worker method is mandatory")
    for requirement, actual in zip(public, actual_records, strict=True):
        validate_original_record(requirement, actual)
    counts = {
        "pass_count": sum(item["status"] == "PASS" for item in actual_records),
        "skip_count": sum(item["status"] == "SKIP" for item in actual_records),
        "failure_count": sum(item["status"] == "FAIL" for item in actual_records),
    }
    for name, count in counts.items():
        require(type(worker[name]) is int and worker[name] == count,
                "a genuine original worker result count was concealed: " + name)
    status = "PASS" if counts == {
        "pass_count": 151, "skip_count": 1, "failure_count": 0,
    } else "FAIL"
    require(worker["status"] == status,
            "a genuine original worker pass or semantic failure was misclassified")
    if baseline:
        require(status == "PASS" and record_hash == BASELINE_SHA256
                and worker["native_provenance"] is None
                and worker["matcher_guard"] is None,
                "the isolated standard reference borrowed a native candidate")
    else:
        require(worker["native_provenance"] == result["native_provenance"]
                and worker["matcher_guard"] == result["matcher_guard"],
                "the original candidate worker substituted native ownership")
        validate_native(worker["native_provenance"], spec, pins)
        validate_guard(worker["matcher_guard"], spec)
    locales = worker["actual_private_locales"]
    require(type(locales) is dict and set(locales) == PRIVATE_LOCALE_FIELDS,
            "a complete exact original worker private locale was omitted")
    for name, expected_value in {
        "actual_localedef_executable": "/usr/bin/localedef",
        "private_temporary_directories_created": 1,
        "private_locale_outputs_created": 2,
        "actual_localedef_workers": 2,
        "iso_8859_1_verified": True,
        "utf_8_verified": True,
        "system_locales_installed": False,
        "workspace_files_written": 0,
        "temporary_directory_removed": True,
    }.items():
        actual = locales[name]
        require(
            (actual is expected_value if type(expected_value) is bool
             else type(actual) is int and actual == expected_value
             if type(expected_value) is int
             else actual == expected_value),
            "a genuine original worker private locale changed: " + name,
        )
    decode_stream(worker["captured_original_stdout"], role + " original stdout")
    decode_stream(worker["captured_original_stderr"], role + " original stderr")
    return worker


def validate_isolated_processes(
    value: Any, result: Mapping[str, Any], matrix: list[dict[str, Any]],
    pins: OwnerPins, digestor: Callable[[Any], str],
) -> None:
    spec = validate_pins(pins)
    require(type(value) is list and len(value) == 2,
            "preserve one genuine standard reference and one candidate worker")
    roles = (
        ("candidate_reference", None, result["baseline_pid"],
         result["baseline_records"], result["baseline_records_sha256"], 0),
        ("candidate-" + spec.name, spec.name, result["candidate_pid"],
         result["candidate_records"], result["candidate_records_sha256"],
         0 if result["status"] == "PASS" else 1),
    )
    for evidence, (role, family, expected_pid, records, expected_hash,
                   expected_exit) in zip(
        value, roles, strict=True,
    ):
        require(type(evidence) is dict
                and set(evidence) == {"role", "candidate_family", "pid",
                                      "returncode", "stdout", "stderr",
                                      "records_sha256", "record_count"}
                and evidence["role"] == role
                and evidence["candidate_family"] == family
                and type(evidence["pid"]) is int
                and evidence["pid"] == expected_pid
                and type(evidence["returncode"]) is int
                and evidence["returncode"] == expected_exit
                and evidence["records_sha256"] == expected_hash
                and type(evidence["record_count"]) is int
                and evidence["record_count"] == PUBLIC_METHODS,
                "a genuine original worker role, PID, or exit was forged")
        stdout = decode_stream(evidence["stdout"], role + " stdout")
        stderr = decode_stream(evidence["stderr"], role + " stderr")
        require(stderr == b"", "a complete original test worker concealed stderr")
        worker = decode_document(stdout, role + " complete worker")
        observed = validate_worker_result(
            worker, result, matrix, pins, role=role, family=family,
            pid=expected_pid, records=records, record_hash=expected_hash,
            digestor=digestor,
        )
        require(expected_exit == (0 if observed["status"] == "PASS" else 1),
                "the genuine complete original worker exit was misclassified")


def decode_controller_worker_failure(
    raw_stderr: bytes, spec: FamilySpec,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    require(type(raw_stderr) is bytes,
            "preserve the complete original controller diagnostic bytes")
    if not raw_stderr.startswith(b"{"):
        return None, None
    outer = decode_document(raw_stderr, "complete original controller failure")
    require(set(outer) == {
        "schema", "status", "error_type", "error", "complete_traceback",
        "clock_samples", "timing_trials_run", "hidden_cases_read",
        "performance",
    } and outer.get("schema")
    == ORIGINAL_SCHEMA + "-complete-original-worker-failure"
    and outer.get("status") == "FAIL"
    and type(outer.get("error_type")) is str and bool(outer["error_type"])
    and type(outer.get("error")) is str
    and type(outer.get("complete_traceback")) is str
    and bool(outer["complete_traceback"])
    and outer["error_type"] in outer["complete_traceback"]
    and outer["error"] in outer["complete_traceback"]
    and type(outer.get("clock_samples")) is int
    and outer["clock_samples"] == 0
    and type(outer.get("timing_trials_run")) is int
    and outer["timing_trials_run"] == 0
    and type(outer.get("hidden_cases_read")) is int
    and outer["hidden_cases_read"] == 0
    and outer.get("performance") == "NOT MEASURED",
    "the complete canonical original controller crash was substituted")
    if not outer["error"].startswith("{"):
        return outer, None
    require(outer["error_type"] == "OriginalSuiteError",
            "a genuine nested original failure changed its outer exception type")
    try:
        nested_raw = outer["error"].encode("ascii")
    except UnicodeError as error:
        raise RecorderError(
            "an isolated original worker failure was not canonical ASCII",
        ) from error
    failure = decode_document(nested_raw, "complete isolated original worker failure")
    shared = {
        "schema", "status", "pid", "returncode", "stdout", "stderr",
        "clock_samples", "timing_trials_run", "hidden_cases_read",
        "performance",
    }
    schema = failure.get("schema")
    if schema == ORIGINAL_SCHEMA + "-complete-isolated-reference-failure":
        require(set(failure) == shared | {"role"}
                and failure.get("role") == "candidate_reference",
                "a genuine failed original standard reference was substituted")
    elif schema == ORIGINAL_SCHEMA + "-complete-isolated-worker-failure":
        require(set(failure) == shared | {"candidate_family"}
                and failure.get("candidate_family") == spec.name,
                "a genuine failed original candidate worker was substituted")
    else:
        raise RecorderError("the exact isolated original crash schema was substituted")
    require(failure.get("status") == "FAIL"
            and type(failure.get("pid")) is int and failure["pid"] > 0
            and type(failure.get("returncode")) is int
            and type(failure.get("clock_samples")) is int
            and failure["clock_samples"] == 0
            and type(failure.get("timing_trials_run")) is int
            and failure["timing_trials_run"] == 0
            and type(failure.get("hidden_cases_read")) is int
            and failure["hidden_cases_read"] == 0
            and failure.get("performance") == "NOT MEASURED",
            "a complete isolated original crash or side effect was concealed")
    stdout = decode_stream(failure["stdout"], "failed original worker stdout")
    stderr = decode_stream(failure["stderr"], "failed original worker stderr")
    require(
        (bool(stderr) or failure["returncode"] != 0)
        if schema == ORIGINAL_SCHEMA + "-complete-isolated-reference-failure"
        else (bool(stderr) or failure["returncode"] not in (0, 1)),
        "a genuine complete original worker crash was misclassified",
    )
    require(type(stdout) is bytes,
            "the genuine complete failed original worker stdout was lost")
    return outer, failure


def run_one_controller(pins: OwnerPins) -> dict[str, Any]:
    spec = validate_pins(pins)
    args = [str(PINNED_PYTHON), "-I", "-B", str(ROOT / ORIGINAL_RELATIVE),
            "--candidate", spec.name,
            "--oracle-source-sha256", pins.original,
            "--matrix-sha256", pins.matrix,
            "--candidate-source-sha256", pins.candidate,
            "--native-engine-sha256", pins.native_engine,
            "--native-bridge-sha256", pins.native_bridge]
    try:
        process = subprocess.Popen(
            args, cwd=str(ROOT), shell=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"started": False, "pid": None, "returncode": None,
                "signal": None, "timed_out": False,
                "spawn_error": str(error), "stdout": b"", "stderr": b""}
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and type(process.returncode) is int,
            "the actual original controller lost complete raw process streams")
    return {"started": True, "pid": process.pid,
            "returncode": process.returncode,
            "signal": -process.returncode if process.returncode < 0 else None,
            "timed_out": timed_out, "spawn_error": None,
            "stdout": stdout, "stderr": stderr}


def build_complete_report(
    pins: OwnerPins, label: str, process: Mapping[str, Any],
    matrix: list[dict[str, Any]], before: Mapping[str, Any],
    after: Mapping[str, Any] | None, *, post_run_error: str | None = None,
    digestor: Callable[[Any], str] = digest,
) -> dict[str, Any]:
    spec = validate_pins(pins)
    failures: list[str] = []
    raw_stdout, raw_stderr = process.get("stdout"), process.get("stderr")
    stdout = capture_stream(raw_stdout, "actual V5 original controller stdout")
    stderr = capture_stream(raw_stderr, "actual V5 original controller stderr")
    result: dict[str, Any] | None = None
    controller_failure: dict[str, Any] | None = None
    isolated_worker_failure: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append("the exact original controller could not start: "
                        + str(process.get("spawn_error")))
    if process.get("timed_out") is True:
        failures.append("the exact original controller exceeded its safe timeout")
    if raw_stdout:
        try:
            result = validate_result(
                decode_document(raw_stdout, "V5 complete original controller"),
                matrix, pins, before, digestor=digestor,
            )
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append("invalid original-suite process result: " + str(error))
    if result is None:
        failures.append("the actual original baseline and candidate outcomes are unknown")
    elif result["status"] == "FAIL":
        failures.append("the original Python suite exposed "
                        + str(result["mismatch_count"]) + " genuine mismatches")
    if raw_stderr:
        try:
            controller_failure, isolated_worker_failure = decode_controller_worker_failure(
                raw_stderr, spec,
            )
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append(
                "invalid complete isolated original worker failure: " + str(error),
            )
        failures.append("the real V5 controller emitted diagnostic stderr")
    expected_exit = 0 if result is not None and result["status"] == "PASS" \
        and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append("the original controller crashed, timed out, or returned a wrong exit")
    if post_run_error is not None:
        failures.append("the post-run native owner authentication failed: " + post_run_error)
    if before != after:
        failures.append("the independently frozen native owner changed during the run")
    return {
        "schema": SCHEMA + "-complete-first-run-report",
        "status": "FAIL" if failures else "PASS",
        "candidate_family": spec.name,
        "label": validate_label(label),
        "python": "3.14.6",
        "controller_relative": ORIGINAL_RELATIVE,
        "controller_source_sha256": ORIGINAL_SHA256,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "frozen_baseline_records_sha256": BASELINE_SHA256,
        "original_source_sha256": ORIGINAL_TEST_SHA256,
        "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
        "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS),
        "public_waivers": [],
        "candidate_provenance_before": dict(before),
        "candidate_provenance_after": dict(after) if after is not None else None,
        "candidate_provenance_unchanged": before == after,
        "complete_original_process_stdout": stdout,
        "complete_original_process_stderr": stderr,
        "complete_original_structured_failure": controller_failure,
        "complete_original_suite_result": result,
        "isolated_worker_failure": isolated_worker_failure,
        "validated_baseline_record_count": (
            len(result["baseline_records"]) if result is not None else None
        ),
        "validated_candidate_record_count": (
            len(result["candidate_records"]) if result is not None else None
        ),
        "baseline_records_sha256": (
            result["baseline_records_sha256"] if result is not None else None
        ),
        "candidate_records_sha256": (
            result["candidate_records_sha256"] if result is not None else None
        ),
        "baseline_records": result["baseline_records"] if result is not None else None,
        "candidate_records": result["candidate_records"] if result is not None else None,
        "mismatch_count": result["mismatch_count"] if result is not None else None,
        "all_mismatches": result["all_mismatches"] if result is not None else None,
        "all_mismatches_preserved": True if result is not None else None,
        "baseline_pid": result["baseline_pid"] if result is not None else None,
        "candidate_pid": result["candidate_pid"] if result is not None else None,
        "actual_method_guard_checks": (
            result["matcher_guard"]["actual_method_guard_checks"]
            if result is not None else None
        ),
        "actual_warning_registry_guard_checks": (
            result["matcher_guard"]["actual_warning_registry_guard_checks"]
            if result is not None else None
        ),
        "trusted_stdlib_ctypes_guard": (
            trusted_ctypes_guard(result["matcher_guard"])
            if result is not None else None
        ),
        "isolated_process_evidence": (
            result["isolated_process_evidence"] if result is not None else None
        ),
        "actual_candidate_workers": (
            result["actual_candidate_workers"] if result is not None else None
        ),
        "actual_reference_workers": 1 if result is not None else None,
        "actual_localedef_workers": (
            result["actual_localedef_workers"] if result is not None else None
        ),
        "actual_private_temporary_directories_created": (
            result["actual_private_temporary_directories_created"]
            if result is not None else None
        ),
        "actual_private_locale_outputs_created": (
            result["actual_private_locale_outputs_created"]
            if result is not None else None
        ),
        "all_private_temporary_directories_removed": (
            result["all_private_temporary_directories_removed"]
            if result is not None else None
        ),
        "actual_original_suite_invocations": int(process.get("started") is True),
        "actual_original_controller_pid": process.get("pid"),
        "actual_original_process_returncode": process.get("returncode"),
        "actual_original_process_signal": process.get("signal"),
        "actual_original_process_timed_out": process.get("timed_out") is True,
        "actual_original_process_spawn_error": process.get("spawn_error"),
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def record_original(pins: OwnerPins, label: str) -> dict[str, Any]:
    verify_runtime()
    spec = validate_pins(pins)
    validate_label(label)
    authenticate_frozen_sources(pins)
    before = authenticate_candidate(pins)
    matrix = load_frozen_context(pins)
    require(authenticate_candidate(pins) == before,
            "the candidate owner changed during original matrix authentication")
    with preflight_fresh_outputs(spec.name, label) as preflight:
        verify_retained_directory(preflight)
        process = run_one_controller(pins)
        verify_retained_directory(preflight)
        after: dict[str, Any] | None = None
        post_run_error: str | None = None
        try:
            authenticate_frozen_sources(pins)
            after = authenticate_candidate(pins)
        except (OSError, RecorderError) as error:
            post_run_error = str(error)
        report = build_complete_report(
            pins, label, process, matrix, before, after,
            post_run_error=post_run_error,
        )
        publication = publish_atomic(preflight, report, "report")
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS", "candidate_family": spec.name,
            "original_result_status": report["status"],
            "label": label,
            "controller_relative": ORIGINAL_RELATIVE,
            "controller_source_sha256": ORIGINAL_SHA256,
            "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
            "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
            "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
            "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "frozen_baseline_records_sha256": BASELINE_SHA256,
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVER_COUNT,
            "public_waivers": [],
            "candidate_source_sha256": pins.candidate,
            "native_engine_sha256": pins.native_engine,
            "native_bridge_sha256": pins.native_bridge,
            "validated_baseline_record_count": report["validated_baseline_record_count"],
            "validated_candidate_record_count": report["validated_candidate_record_count"],
            "baseline_records_sha256": report["baseline_records_sha256"],
            "candidate_records_sha256": report["candidate_records_sha256"],
            "mismatch_count": report["mismatch_count"],
            "all_mismatches_preserved": report["all_mismatches_preserved"],
            "actual_method_guard_checks": report["actual_method_guard_checks"],
            "actual_warning_registry_guard_checks": report["actual_warning_registry_guard_checks"],
            "trusted_stdlib_ctypes_guard": report["trusted_stdlib_ctypes_guard"],
            "complete_original_structured_failure": report[
                "complete_original_structured_failure"
            ],
            "isolated_worker_failure": report["isolated_worker_failure"],
            "actual_candidate_workers": report["actual_candidate_workers"],
            "actual_reference_workers": report["actual_reference_workers"],
            "actual_original_suite_invocations": report["actual_original_suite_invocations"],
            "candidate_provenance_before": report["candidate_provenance_before"],
            "candidate_provenance_after": report["candidate_provenance_after"],
            "candidate_provenance_unchanged": report["candidate_provenance_unchanged"],
            "report_relative": publication["path"],
            "report_sha256": publication["sha256"],
            "report_bytes": publication["bytes"],
            "report_actual_write_calls": publication["actual_write_calls"],
            "report_file_fsync_completed": publication["file_fsync_completed"],
            "report_directory_fsync_completed": publication["directory_fsync_completed"],
            "report_atomic_no_overwrite_link": publication["atomic_no_overwrite_link"],
            "report_complete_readback_verified": True,
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
        "candidate_family": spec.name, "label": label,
        "validated_baseline_record_count": report["validated_baseline_record_count"],
        "validated_candidate_record_count": report["validated_candidate_record_count"],
        "mismatch_count": report["mismatch_count"],
        "report_publication": publication,
        "receipt_publication": receipt_publication,
        "actual_original_suite_invocations": report["actual_original_suite_invocations"],
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
    effects = {key: 0 for key in (
        "blocked_reads", "blocked_writes", "blocked_imports", "blocked_workers",
        "blocked_threads", "blocked_clocks", "blocked_gc_collections",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def deny(key: str, message: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[key] += 1
            raise SourceOnlyError(message)
        return blocked

    def install(owner: Any, name: str, value: Any) -> None:
        original = getattr(owner, name, None)
        if original is not None:
            installed.append((owner, name, original))
            setattr(owner, name, value)

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, deny("blocked_reads",
                    "a synthetic original control cannot read files"))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (os, "link"), (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, deny("blocked_writes",
                    "a synthetic original control cannot write files"))
        install(builtins, "__import__", deny("blocked_imports",
                "a synthetic original control cannot directly import a candidate"))
        install(importlib, "import_module", deny("blocked_imports",
                "a synthetic original control cannot import a candidate"))
        install(subprocess, "Popen", deny("blocked_workers",
                "a synthetic original control cannot start workers"))
        install(subprocess, "run", deny("blocked_workers",
                "a synthetic original control cannot start workers"))
        for name in ("call", "check_call", "check_output"):
            install(subprocess, name, deny("blocked_workers",
                    "a synthetic original control cannot start workers"))
        install(threading.Thread, "start", deny("blocked_threads",
                "a synthetic original control cannot start threads"))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns"):
            install(time, name, deny("blocked_clocks",
                    "a synthetic original control cannot sample clocks"))
        install(gc, "collect", deny("blocked_gc_collections",
                "a synthetic original control cannot collect garbage"))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_owner(relative: str, value: str,
                    inode: int = 29) -> dict[str, Any]:
    return {"relative": relative, "sha256": value,
            "bytes": 71, "device": 7, "inode": inode}


def synthetic_private_locales() -> dict[str, Any]:
    return {
        "actual_localedef_executable": "/usr/bin/localedef",
        "private_temporary_directories_created": 1,
        "private_locale_outputs_created": 2,
        "actual_localedef_workers": 2,
        "iso_8859_1_verified": True,
        "utf_8_verified": True,
        "system_locales_installed": False,
        "workspace_files_written": 0,
        "temporary_directory_removed": True,
    }


def synthetic_isolated_evidence(result: Mapping[str, Any],
                                spec: FamilySpec) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for role, family, pid, records, record_hash in (
        ("candidate_reference", None, result["baseline_pid"],
         result["baseline_records"], result["baseline_records_sha256"]),
        ("candidate-" + spec.name, spec.name, result["candidate_pid"],
         result["candidate_records"], result["candidate_records_sha256"]),
    ):
        baseline = family is None
        pass_count = sum(row["status"] == "PASS" for row in records)
        skip_count = sum(row["status"] == "SKIP" for row in records)
        failure_count = sum(row["status"] == "FAIL" for row in records)
        status = "PASS" if (pass_count, skip_count, failure_count) == (
            151, 1, 0,
        ) else "FAIL"
        worker = {
            "schema": ORIGINAL_SCHEMA + "-isolated-original-worker",
            "status": status, "python": "3.14.6", "role": role,
            "engine": "stdlib" if baseline else spec.name,
            "candidate_family": family, "pid": pid,
            "controller_source_sha256": ORIGINAL_SHA256,
            "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
            "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
            "test_harness_relative": HARNESS_RELATIVE,
            "test_harness_sha256": HARNESS_SHA256,
            "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
            "identity_guard_sha256": IDENTITY_GUARD_SHA256,
            "warning_guard_relative": WARNING_GUARD_RELATIVE,
            "warning_guard_sha256": WARNING_GUARD_SHA256,
            "original_source_sha256": ORIGINAL_TEST_SHA256,
            "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
            "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
            "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVER_COUNT,
            "private_waivers": list(PRIVATE_METHODS), "public_waivers": [],
            "all_original_methods_executed": False,
            "all_original_methods_qualified": False,
            "records": copy.deepcopy(records), "records_sha256": record_hash,
            "pass_count": pass_count, "skip_count": skip_count,
            "failure_count": failure_count,
            "native_provenance": copy.deepcopy(result["native_provenance"])
            if not baseline else None,
            "matcher_guard": copy.deepcopy(result["matcher_guard"])
            if not baseline else None,
            "multiprocessing_start_method": "fork",
            "original_bigmem_dry_run": True,
            "original_bigmem_maximum_size": 5_147,
            "actual_private_locales": synthetic_private_locales(),
            "captured_original_stdout": capture_stream(
                b"", role + " synthetic captured original stdout",
            ),
            "captured_original_stderr": capture_stream(
                b"", role + " synthetic captured original stderr",
            ),
            "actual_candidate_workers": 0 if baseline else 1,
            "legacy_original_worker_role": role if baseline else "rust",
            "legacy_original_worker_engine": "stdlib" if baseline else "rust",
            "clock_samples": 0, "timing_trials_run": 0,
            "workspace_files_written": 0, "benchmark_files_read": 0,
            "hidden_cases_read": 0, "performance": "NOT MEASURED",
            "final_winner_selected": False,
        }
        documents.append({
            "role": role, "candidate_family": family, "pid": pid,
            "returncode": 0 if status == "PASS" else 1,
            "stdout": capture_stream(canonical(worker), role + " synthetic stdout"),
            "stderr": capture_stream(b"", role + " synthetic stderr"),
            "records_sha256": record_hash, "record_count": PUBLIC_METHODS,
        })
    return documents


def poison_synthetic_worker(
    result: dict[str, Any], index: int,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    require(type(index) is int and index in (0, 1),
            "poison exactly one original baseline or independent worker")
    evidence = result["isolated_process_evidence"][index]
    role = evidence["role"]
    worker = decode_document(
        decode_stream(evidence["stdout"], role + " synthetic poison stdout"),
        role + " synthetic poison worker",
    )
    mutate(worker)
    evidence["stdout"] = capture_stream(
        canonical(worker), role + " poisoned synthetic stdout",
    )


def synthetic_controller_failure(
    spec: FamilySpec, *, reference: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    inner: dict[str, Any] = {
        "schema": ORIGINAL_SCHEMA + (
            "-complete-isolated-reference-failure" if reference
            else "-complete-isolated-worker-failure"
        ),
        "status": "FAIL", "pid": 801 if reference else 802,
        "returncode": 1 if reference else -11,
        "stdout": capture_stream(
            b"synthetic complete native worker stdout\n",
            "synthetic failed original worker stdout",
        ),
        "stderr": capture_stream(
            b"" if reference else b"synthetic complete native worker diagnostic\n",
            "synthetic failed original worker stderr",
        ),
        "clock_samples": 0, "timing_trials_run": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
    }
    if reference:
        inner["role"] = "candidate_reference"
    else:
        inner["candidate_family"] = spec.name
    outer = {
        "schema": ORIGINAL_SCHEMA + "-complete-original-worker-failure",
        "status": "FAIL", "error_type": "OriginalSuiteError",
        "error": canonical(inner).decode("ascii"),
        "complete_traceback": (
            "Traceback (most recent call last):\n"
            "OriginalSuiteError: " + canonical(inner).decode("ascii")
        ),
        "clock_samples": 0, "timing_trials_run": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
    }
    return outer, inner


def poison_synthetic_controller_failure(
    outer: dict[str, Any], mutate: Callable[[dict[str, Any]], None],
) -> None:
    inner = decode_document(
        outer["error"].encode("ascii"), "synthetic complete nested failure",
    )
    mutate(inner)
    outer["error"] = canonical(inner).decode("ascii")
    outer["complete_traceback"] = (
        "Traceback (most recent call last):\n"
        "OriginalSuiteError: " + outer["error"]
    )


def synthetic_documents(spec: FamilySpec) -> tuple[
    OwnerPins, dict[str, Any], list[dict[str, Any]], dict[str, Any],
    Callable[[Any], str],
]:
    pins = OwnerPins(
        spec.name, ORIGINAL_SHA256, MATRIX_SHA256, BASELINE_SHA256,
        hashlib.sha256((spec.name + "-owned-adapter").encode()).hexdigest(),
        hashlib.sha256((spec.name + "-owned-engine").encode()).hexdigest(),
        hashlib.sha256((spec.name + "-owned-engine").encode()).hexdigest()
        if spec.name == "c" else
        hashlib.sha256((spec.name + "-owned-bridge").encode()).hexdigest(),
    )
    owners = {
        "source": synthetic_owner(spec.adapter_relative, pins.candidate, 41),
        "native_engine": synthetic_owner(spec.engine_relative, pins.native_engine, 43),
        "native_bridge": synthetic_owner(spec.bridge_relative, pins.native_bridge,
                                            43 if spec.name == "c" else 47),
    }
    matrix: list[dict[str, Any]] = []
    baseline: list[dict[str, Any]] = []
    for index in range(PUBLIC_METHODS):
        name = ("ReTests.test_memory_leaks" if index == PUBLIC_METHODS - 1
                else "ReTests.test_synthetic_" + format(index, "03d"))
        source_hash = hashlib.sha256(name.encode("ascii")).hexdigest()
        matrix.append({"index": index, "test": name, "class": "ReTests",
                       "method": name.split(".", 1)[1],
                       "source_ast_sha256": source_hash,
                       "classification": "public", "waiver_reason": None})
        skipped = index == PUBLIC_METHODS - 1
        baseline.append({
            "test": name, "source_ast_sha256": source_hash,
            "status": "SKIP" if skipped else "PASS", "tests_run": 1,
            "failure_count": 0, "error_count": 0,
            "skip_count": 1 if skipped else 0,
            "failure_tracebacks": [], "error_tracebacks": [],
            "skip_reasons": ["requires debug build"] if skipped else [],
        })
    for name in PRIVATE_METHODS:
        cls, method = name.split(".", 1)
        matrix.append({"index": len(matrix), "test": name, "class": cls,
                       "method": method,
                       "source_ast_sha256": hashlib.sha256(name.encode()).hexdigest(),
                       "classification": "named-private-waiver",
                       "waiver_reason": "frozen original private implementation"})
    matrix_bytes, baseline_bytes = canonical(matrix), canonical(baseline)

    def synthetic_digest(value: Any) -> str:
        raw = canonical(value)
        if raw == matrix_bytes:
            return MATRIX_SHA256
        if raw == baseline_bytes:
            return BASELINE_SHA256
        return hashlib.sha256(raw).hexdigest()

    guard = {name: True for name in GUARD_TRUE_FIELDS}
    guard.update({
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": GUARD_CHECKS,
        "actual_warning_registry_guard_checks": GUARD_CHECKS,
        "owned_native_ffi_allowed": spec.owned_ctypes,
        "trusted_stdlib_ctypes_preloaded": spec.owned_ctypes,
        "trusted_stdlib_ctypes_builtin_verified": spec.owned_ctypes,
        "trusted_stdlib_ctypes_pythonapi_initialized": spec.owned_ctypes,
        "trusted_stdlib_ctypes_source_sha256": (
            PINNED_CTYPES_SHA256 if spec.owned_ctypes else None
        ),
        "cached_original_matcher_descendant_count": 1,
        "cached_original_holder_count": 1,
        "owned_ctypes_load_count": 1 if spec.owned_ctypes else 0,
        "owned_ctypes_symbol_count": 9 if spec.owned_ctypes else 0,
    })
    result = {
        "schema": ORIGINAL_SCHEMA + "-actual-original-candidate-result",
        "status": "PASS", "python": "3.14.6", "candidate_family": spec.name,
        "controller_source_sha256": ORIGINAL_SHA256,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "original_source_sha256": ORIGINAL_TEST_SHA256,
        "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
        "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS), "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "baseline_records_sha256": BASELINE_SHA256,
        "candidate_records_sha256": BASELINE_SHA256,
        "baseline_records": baseline,
        "candidate_records": copy.deepcopy(baseline),
        "mismatch_count": 0, "all_mismatches": [],
        "baseline_pid": 101, "candidate_pid": 102,
        "native_provenance": owners,
        "matcher_guard": guard,
        "actual_candidate_workers": 1,
        "actual_localedef_workers": 4,
        "actual_private_temporary_directories_created": 2,
        "actual_private_locale_outputs_created": 4,
        "all_private_temporary_directories_removed": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    result["isolated_process_evidence"] = synthetic_isolated_evidence(result, spec)
    return pins, owners, matrix, result, synthetic_digest


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []
    with source_only_boundary() as effects:

        def accept(name: str, condition: Any) -> None:
            require(condition, "a synthetic original recorder control failed: " + name)
            accepted.append(name)

        def reject(name: str, operation: Callable[[], Any]) -> None:
            try:
                operation()
            except (RecorderError, OSError, ValueError, TypeError, KeyError, IndexError):
                rejected.append(name)
                return
            raise RecorderError("a synthetic original poison was accepted: " + name)

        for name, spec in FAMILIES.items():
            pins, owners, matrix, result, synthetic_digest = synthetic_documents(spec)
            accept(name + "-complete-paired-original-vectors",
                   validate_result(result, matrix, pins, owners,
                                   digestor=synthetic_digest) is result)
            accept(name + "-all-165-original-methods-and-13-waivers",
                   len(matrix) == TOTAL_METHODS
                   and len(result["baseline_records"])
                   == len(result["candidate_records"]) == PUBLIC_METHODS
                   and result["private_waivers"] == list(PRIVATE_METHODS))
            accept(name + "-all-304-identity-and-warning-guards",
                   result["matcher_guard"]["actual_method_guard_checks"]
                   == result["matcher_guard"]["actual_warning_registry_guard_checks"]
                   == GUARD_CHECKS)
            accept(name + "-actual-owned-zig-preload-policy",
                   result["matcher_guard"]["trusted_stdlib_ctypes_preloaded"]
                   is spec.owned_ctypes
                   and result["matcher_guard"]["trusted_stdlib_ctypes_builtin_verified"]
                   is spec.owned_ctypes
                   and result["matcher_guard"]
                   ["trusted_stdlib_ctypes_pythonapi_initialized"]
                   is spec.owned_ctypes
                   and result["matcher_guard"]["trusted_stdlib_ctypes_source_sha256"]
                   == (PINNED_CTYPES_SHA256 if spec.owned_ctypes else None))
            report_path, receipt_path = approved_paths(name, "synthetic-proof")
            accept(name + "-fresh-v5-report-and-receipt-paths",
                   report_path != receipt_path
                   and ("/" + name + "-original-v5-") in report_path
                   and ("/" + name + "-original-v5-") in receipt_path)

            process = {"started": True, "pid": 701, "returncode": 0,
                       "signal": None, "timed_out": False,
                       "spawn_error": None, "stdout": canonical(result),
                       "stderr": b""}
            observed = build_complete_report(
                pins, "synthetic-proof", process, matrix, owners, owners,
                digestor=synthetic_digest,
            )
            accept(name + "-preserve-complete-passing-original-result",
                   observed["status"] == "PASS"
                   and observed["validated_baseline_record_count"] == PUBLIC_METHODS
                   and observed["validated_candidate_record_count"] == PUBLIC_METHODS
                   and observed["actual_method_guard_checks"] == GUARD_CHECKS
                   and observed["actual_warning_registry_guard_checks"] == GUARD_CHECKS
                   and observed["actual_candidate_workers"] == 1
                   and observed["actual_reference_workers"] == 1
                   and observed["trusted_stdlib_ctypes_guard"]
                   == trusted_ctypes_guard(result["matcher_guard"])
                   and observed["complete_original_structured_failure"] is None
                   and observed["isolated_worker_failure"] is None
                   and observed["isolated_process_evidence"]
                   == result["isolated_process_evidence"])

            failure = copy.deepcopy(result)
            failed_record = failure["candidate_records"][0]
            failed_record["status"] = "FAIL"
            failed_record["failure_count"] = 1
            failed_record["failure_tracebacks"] = ["synthetic complete original failure"]
            failure["candidate_records_sha256"] = digest(failure["candidate_records"])
            mismatch = {"test": matrix[0]["test"],
                        "baseline": failure["baseline_records"][0],
                        "candidate": failed_record}
            failure["mismatch_count"] = 1
            failure["all_mismatches"] = [mismatch]
            failure["status"] = "FAIL"
            failure["isolated_process_evidence"] = synthetic_isolated_evidence(failure, spec)
            failed_process = {**process, "stdout": canonical(failure), "returncode": 1}
            failed = build_complete_report(
                pins, "synthetic-proof", failed_process, matrix, owners, owners,
                digestor=synthetic_digest,
            )
            accept(name + "-preserve-complete-genuine-original-failure",
                   failed["status"] == "FAIL"
                   and failed["validated_baseline_record_count"] == PUBLIC_METHODS
                   and failed["validated_candidate_record_count"] == PUBLIC_METHODS
                   and failed["mismatch_count"] == 1
                   and failed["all_mismatches"] == [mismatch]
                   and failed["all_mismatches_preserved"] is True
                   and failed["actual_candidate_workers"] == 1
                   and failed["actual_reference_workers"] == 1
                   and failed["isolated_process_evidence"][0]["role"]
                   == "candidate_reference"
                   and failed["isolated_process_evidence"][0]["returncode"] == 0
                   and failed["isolated_process_evidence"][1]["role"]
                   == "candidate-" + name
                   and failed["isolated_process_evidence"][1]["returncode"] == 1
                   and failed["isolated_worker_failure"] is None)
            reject(
                name + "-reject-genuine-mismatch-forged-as-zero-candidate-exit",
                lambda: validate_result(
                    {
                        **failure,
                        "isolated_process_evidence": [
                            failure["isolated_process_evidence"][0],
                            {
                                **failure["isolated_process_evidence"][1],
                                "returncode": 0,
                            },
                        ],
                    }, matrix, pins, owners, digestor=synthetic_digest,
                ),
            )

            crashed = {**process, "returncode": -11, "signal": 11,
                       "stdout": b"synthetic native crash\n",
                       "stderr": b"synthetic complete native diagnostic\n"}
            unknown = build_complete_report(
                pins, "synthetic-proof", crashed, matrix, owners, owners,
                digestor=synthetic_digest,
            )
            accept(name + "-preserve-unknown-native-crash",
                   unknown["status"] == "FAIL"
                   and unknown["actual_original_process_signal"] == 11
                   and all(unknown[key] is None for key in (
                       "validated_baseline_record_count",
                       "validated_candidate_record_count",
                       "baseline_records_sha256", "candidate_records_sha256",
                       "baseline_records", "candidate_records",
                       "mismatch_count", "all_mismatches", "all_mismatches_preserved",
                       "baseline_pid", "candidate_pid",
                       "actual_method_guard_checks", "actual_warning_registry_guard_checks",
                       "trusted_stdlib_ctypes_guard", "isolated_process_evidence",
                       "complete_original_structured_failure",
                       "isolated_worker_failure", "actual_candidate_workers",
                       "actual_reference_workers", "actual_localedef_workers",
                       "actual_private_temporary_directories_created",
                       "actual_private_locale_outputs_created",
                       "all_private_temporary_directories_removed",
                   )))
            timed_process = {**crashed, "returncode": -9, "signal": 9,
                             "timed_out": True}
            timed = build_complete_report(
                pins, "synthetic-proof", timed_process, matrix, owners, owners,
                digestor=synthetic_digest,
            )
            accept(name + "-preserve-unknown-original-timeout",
                   timed["status"] == "FAIL"
                   and timed["actual_original_process_timed_out"] is True
                   and timed["validated_baseline_record_count"] is None
                   and timed["validated_candidate_record_count"] is None
                   and timed["actual_reference_workers"] is None)
            unstarted_process = {"started": False, "pid": None, "returncode": None,
                                 "signal": None, "timed_out": False,
                                 "spawn_error": "synthetic original spawn failure",
                                 "stdout": b"", "stderr": b""}
            unstarted = build_complete_report(
                pins, "synthetic-proof", unstarted_process, matrix, owners, owners,
                digestor=synthetic_digest,
            )
            accept(name + "-preserve-unknown-original-spawn",
                   unstarted["status"] == "FAIL"
                   and unstarted["actual_original_suite_invocations"] == 0
                   and unstarted["validated_baseline_record_count"] is None
                   and unstarted["validated_candidate_record_count"] is None
                   and unstarted["actual_reference_workers"] is None)

            for reference in (True, False):
                kind = "reference" if reference else "candidate"
                outer_failure, inner_failure = synthetic_controller_failure(
                    spec, reference=reference,
                )
                decoded_outer, decoded_inner = decode_controller_worker_failure(
                    canonical(outer_failure), spec,
                )
                accept(
                    name + "-preserve-canonical-nested-" + kind + "-crash",
                    decoded_outer == outer_failure
                    and decoded_inner == inner_failure
                    and (
                        inner_failure["returncode"] == 1
                        and decode_stream(
                            inner_failure["stderr"],
                            kind + " empty synthetic reference stderr",
                        ) == b""
                        if reference else
                        inner_failure["returncode"] == -11
                        and bool(decode_stream(
                            inner_failure["stderr"],
                            kind + " complete synthetic candidate stderr",
                        ))
                    ),
                )
                structured_process = {
                    **process, "returncode": 1, "signal": None,
                    "stdout": b"", "stderr": canonical(outer_failure),
                }
                structured_report = build_complete_report(
                    pins, "synthetic-proof", structured_process,
                    matrix, owners, owners, digestor=synthetic_digest,
                )
                accept(
                    name + "-publish-complete-nested-" + kind + "-crash",
                    structured_report["status"] == "FAIL"
                    and structured_report["complete_original_structured_failure"]
                    == outer_failure
                    and structured_report["isolated_worker_failure"]
                    == inner_failure
                    and decode_stream(
                        structured_report["complete_original_process_stderr"],
                        kind + " complete synthetic outer diagnostic",
                    ) == canonical(outer_failure)
                    and all(structured_report[key] is None for key in (
                        "validated_baseline_record_count",
                        "validated_candidate_record_count",
                        "baseline_records_sha256", "candidate_records_sha256",
                        "baseline_records", "candidate_records",
                        "mismatch_count", "all_mismatches",
                        "all_mismatches_preserved", "baseline_pid",
                        "candidate_pid", "actual_method_guard_checks",
                        "actual_warning_registry_guard_checks",
                        "trusted_stdlib_ctypes_guard",
                        "isolated_process_evidence",
                        "actual_candidate_workers", "actual_reference_workers",
                    )),
                )
                outer_attacks = [
                    ("extra-field", lambda item: item.__setitem__("foreign", True)),
                    ("wrong-schema", lambda item: item.__setitem__("schema", "foreign")),
                    ("wrong-status", lambda item: item.__setitem__("status", "PASS")),
                    ("wrong-error-type", lambda item:
                     item.__setitem__("error_type", "ValueError")),
                    ("missing-traceback", lambda item:
                     item.__setitem__("complete_traceback", "")),
                    ("foreign-traceback", lambda item:
                     item.__setitem__("complete_traceback", "foreign traceback")),
                    ("hidden-clock", lambda item: item.__setitem__("clock_samples", 1)),
                    ("hidden-timing", lambda item:
                     item.__setitem__("timing_trials_run", 1)),
                    ("hidden-case", lambda item:
                     item.__setitem__("hidden_cases_read", 1)),
                ]
                for field in tuple(outer_failure):
                    outer_attacks.append((
                        "missing-" + field,
                        lambda item, field=field: item.pop(field),
                    ))
                for title, mutate in outer_attacks:
                    poisoned_outer = copy.deepcopy(outer_failure)
                    mutate(poisoned_outer)
                    reject(
                        name + "-reject-" + kind + "-outer-" + title,
                        lambda poisoned_outer=poisoned_outer:
                        decode_controller_worker_failure(
                            canonical(poisoned_outer), spec,
                        ),
                    )
                inner_attacks = [
                    ("extra-field", lambda item: item.__setitem__("foreign", True)),
                    ("wrong-schema", lambda item: item.__setitem__("schema", "foreign")),
                    ("wrong-status", lambda item: item.__setitem__("status", "PASS")),
                    ("wrong-pid", lambda item: item.__setitem__("pid", 0)),
                    ("wrong-returncode", lambda item:
                     item.__setitem__("returncode", "foreign")),
                    ("truncated-stdout", lambda item:
                     item["stdout"].__setitem__("bytes", 1)),
                    ("forged-stdout-hash", lambda item:
                     item["stdout"].__setitem__(
                         "sha256", PREVIOUS_ORACLE_SHA256)),
                    ("forged-stdout-base64", lambda item:
                     item["stdout"].__setitem__("base64", "e30=")),
                    ("truncated-stderr", lambda item:
                     item["stderr"].__setitem__("bytes", 1)),
                    ("forged-stderr-hash", lambda item:
                     item["stderr"].__setitem__(
                         "sha256", PREVIOUS_ORACLE_SHA256)),
                    ("hidden-clock", lambda item: item.__setitem__("clock_samples", 1)),
                    ("hidden-timing", lambda item:
                     item.__setitem__("timing_trials_run", 1)),
                    ("hidden-case", lambda item:
                     item.__setitem__("hidden_cases_read", 1)),
                ]
                if reference:
                    inner_attacks.extend([
                        ("wrong-reference-role", lambda item:
                         item.__setitem__("role", "reference")),
                        ("zero-exit-forged-as-reference-crash", lambda item:
                         item.__setitem__("returncode", 0)),
                    ])
                else:
                    inner_attacks.extend([
                        ("wrong-candidate-family", lambda item:
                         item.__setitem__("candidate_family", "foreign")),
                        ("semantic-exit-forged-as-crash", lambda item: (
                            item.__setitem__("returncode", 1),
                            item.__setitem__("stderr", capture_stream(
                                b"", "synthetic genuine semantic failure stderr",
                            )),
                        )),
                    ])
                for field in tuple(inner_failure):
                    inner_attacks.append((
                        "missing-" + field,
                        lambda item, field=field: item.pop(field),
                    ))
                for title, mutate in inner_attacks:
                    poisoned_outer = copy.deepcopy(outer_failure)
                    poison_synthetic_controller_failure(poisoned_outer, mutate)
                    reject(
                        name + "-reject-" + kind + "-nested-" + title,
                        lambda poisoned_outer=poisoned_outer:
                        decode_controller_worker_failure(
                            canonical(poisoned_outer), spec,
                        ),
                    )
                encoded_outer = canonical(outer_failure)
                reject(
                    name + "-reject-" + kind + "-clipped-outer-stream",
                    lambda encoded_outer=encoded_outer:
                    decode_controller_worker_failure(encoded_outer[:-1], spec),
                )
                reject(
                    name + "-reject-" + kind + "-duplicate-outer-json-field",
                    lambda encoded_outer=encoded_outer:
                    decode_controller_worker_failure(
                        encoded_outer[:-2] + b',"status":"PASS"}\n', spec,
                    ),
                )

            attacks: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
                ("missing-original-schema", lambda value: value.pop("schema")),
                ("foreign-original-schema", lambda value: value.__setitem__("schema", "foreign")),
                ("borrowed-family", lambda value: value.__setitem__("candidate_family", "foreign")),
                ("foreign-controller", lambda value: value.__setitem__("controller_source_sha256", PREVIOUS_ORACLE_SHA256)),
                ("omit-previous-v4-oracle", lambda value: value.pop("previous_oracle_sha256")),
                ("foreign-matrix", lambda value: value.__setitem__("matrix_sha256", PREVIOUS_ORACLE_SHA256)),
                ("foreign-baseline", lambda value: value.__setitem__("baseline_records_sha256", PREVIOUS_ORACLE_SHA256)),
                ("hidden-public-method", lambda value: value["baseline_records"].pop()),
                ("hidden-candidate-method", lambda value: value["candidate_records"].pop()),
                ("reordered-candidate-methods", lambda value: value["candidate_records"].reverse()),
                ("forged-candidate-digest", lambda value: value.__setitem__("candidate_records_sha256", PREVIOUS_ORACLE_SHA256)),
                ("public-waiver", lambda value: value.__setitem__("public_waivers", ["ReTests.test_synthetic_000"])),
                ("hidden-private-waiver", lambda value: value["private_waivers"].pop()),
                ("wrong-private-count", lambda value: value.__setitem__("private_waiver_count", 12)),
                ("false-baseline-pid", lambda value: value.__setitem__("baseline_pid", 0)),
                ("shared-worker-pid", lambda value: value.__setitem__("candidate_pid", value["baseline_pid"])),
                ("hidden-original-mismatch", lambda value: value.__setitem__("mismatch_count", 1)),
                ("false-pass", lambda value: value.__setitem__("status", "FAIL")),
                ("missing-native-provenance", lambda value: value.__setitem__("native_provenance", {})),
                ("borrowed-native-engine", lambda value: value["native_provenance"]["native_engine"].__setitem__("sha256", PREVIOUS_ORACLE_SHA256)),
                ("missing-continuous-guard", lambda value: value.__setitem__("matcher_guard", {})),
                ("missing-method-guard", lambda value: value["matcher_guard"].__setitem__("actual_method_guard_checks", GUARD_CHECKS - 1)),
                ("missing-warning-guard", lambda value: value["matcher_guard"].__setitem__("actual_warning_registry_guard_checks", GUARD_CHECKS - 1)),
                ("borrowed-stdlib-engine", lambda value: value["matcher_guard"].__setitem__("original_matchers_blocked", False)),
                ("wrong-owned-ffi-policy", lambda value: value["matcher_guard"].__setitem__("owned_native_ffi_allowed", not spec.owned_ctypes)),
                ("missing-isolated-worker", lambda value: value["isolated_process_evidence"].pop()),
                ("reordered-isolated-workers", lambda value: value["isolated_process_evidence"].reverse()),
                ("forged-isolated-worker-role", lambda value: value["isolated_process_evidence"][0].__setitem__("role", "candidate-foreign")),
                ("forged-isolated-worker-pid", lambda value: value["isolated_process_evidence"][0].__setitem__("pid", 9001)),
                ("forged-isolated-worker-exit", lambda value: value["isolated_process_evidence"][0].__setitem__("returncode", 1)),
                ("truncated-isolated-worker-stdout", lambda value: value["isolated_process_evidence"][0]["stdout"].__setitem__("bytes", 1)),
                ("forged-isolated-worker-hash", lambda value: value["isolated_process_evidence"][0]["stdout"].__setitem__("sha256", PREVIOUS_ORACLE_SHA256)),
                ("forged-isolated-worker-base64", lambda value: value["isolated_process_evidence"][0]["stdout"].__setitem__("base64", "e30=")),
                ("false-original-clock", lambda value: value.__setitem__("clock_samples", 1)),
                ("hidden-performance", lambda value: value.__setitem__("timing_trials_run", 1)),
                ("hidden-final-case", lambda value: value.__setitem__("hidden_cases_read", 1)),
                ("premature-winner", lambda value: value.__setitem__("final_winner_selected", True)),
            ]
            for field in sorted(RESULT_FIELDS):
                attacks.append((
                    "omit-result-" + field,
                    lambda value, field=field: value.pop(field),
                ))
            for index, role_name in ((0, "baseline"), (1, "candidate")):
                for field in sorted(WORKER_RESULT_FIELDS):
                    attacks.append((
                        "omit-" + role_name + "-worker-" + field,
                        lambda value, index=index, field=field:
                        poison_synthetic_worker(
                            value, index,
                            lambda worker, field=field: worker.pop(field),
                        ),
                    ))
                for field in (
                    "role", "candidate_family", "pid", "returncode",
                    "stdout", "stderr", "records_sha256", "record_count",
                ):
                    attacks.append((
                        "omit-" + role_name + "-process-" + field,
                        lambda value, index=index, field=field:
                        value["isolated_process_evidence"][index].pop(field),
                    ))
                attacks.extend([
                    (
                        "extra-" + role_name + "-worker-field",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__("foreign", True),
                        ),
                    ),
                    (
                        "extra-" + role_name + "-process-field",
                        lambda value, index=index:
                        value["isolated_process_evidence"][index].__setitem__(
                            "foreign", True,
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-worker-schema",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__("schema", "foreign"),
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-worker-engine",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__("engine", "foreign"),
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-worker-controller",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__(
                                "controller_source_sha256", PREVIOUS_ORACLE_SHA256,
                            ),
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-worker-predecessor",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__(
                                "previous_oracle_sha256", HARNESS_SHA256,
                            ),
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-worker-native-ownership",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__(
                                "native_provenance", {"foreign": True},
                            ),
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-worker-locale",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker["actual_private_locales"].__setitem__(
                                "actual_localedef_workers", 0,
                            ),
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-captured-original-stdout",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker["captured_original_stdout"].__setitem__(
                                "bytes", 1,
                            ),
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-captured-original-stderr",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker["captured_original_stderr"].__setitem__(
                                "sha256", PREVIOUS_ORACLE_SHA256,
                            ),
                        ),
                    ),
                    (
                        "hidden-" + role_name + "-worker-clock",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__("clock_samples", 1),
                        ),
                    ),
                    (
                        "hidden-" + role_name + "-worker-final-case",
                        lambda value, index=index: poison_synthetic_worker(
                            value, index,
                            lambda worker: worker.__setitem__("hidden_cases_read", 1),
                        ),
                    ),
                    (
                        "false-" + role_name + "-worker-record-count",
                        lambda value, index=index:
                        value["isolated_process_evidence"][index].__setitem__(
                            "record_count", PUBLIC_METHODS - 1,
                        ),
                    ),
                    (
                        "foreign-" + role_name + "-worker-record-hash",
                        lambda value, index=index:
                        value["isolated_process_evidence"][index].__setitem__(
                            "records_sha256", PREVIOUS_ORACLE_SHA256,
                        ),
                    ),
                ])
            if spec.owned_ctypes:
                attacks.extend([
                    ("missing-preloaded-ctypes", lambda value:
                     value["matcher_guard"].pop("trusted_stdlib_ctypes_preloaded")),
                    ("late-ctypes-preload", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_preloaded", False)),
                    ("foreign-built-in-ctypes", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_builtin_verified", False)),
                    ("foreign-pythonapi", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_pythonapi_initialized", False)),
                    ("foreign-ctypes-source", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_source_sha256", PREVIOUS_ORACLE_SHA256)),
                    ("missing-owned-native-load", lambda value: value["matcher_guard"].__setitem__("owned_ctypes_load_count", 0)),
                ])
            else:
                attacks.extend([
                    ("foreign-ctypes-preload", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_preloaded", True)),
                    ("foreign-ctypes-builtin", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_builtin_verified", True)),
                    ("foreign-pythonapi", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_pythonapi_initialized", True)),
                    ("foreign-ctypes-source", lambda value:
                     value["matcher_guard"].__setitem__(
                         "trusted_stdlib_ctypes_source_sha256", PINNED_CTYPES_SHA256)),
                ])
            for title, mutate in attacks:
                poisoned = copy.deepcopy(result)
                mutate(poisoned)
                reject(name + "-" + title,
                       lambda poisoned=poisoned: validate_result(
                           poisoned, matrix, pins, owners,
                           digestor=synthetic_digest,
                       ))
            for other, foreign in FAMILIES.items():
                if other != name:
                    foreign_pins, _, _, _, _ = synthetic_documents(foreign)
                    reject(name + "-reject-" + other + "-owner",
                           lambda foreign_pins=foreign_pins: validate_result(
                               result, matrix, foreign_pins, owners,
                               digestor=synthetic_digest,
                           ))

        accept("literal-original-directory-identity",
               require_directory_identity((17, 31), (17, 31), (17, 31)) is None)
        for title, retained, expected, literal in (
            ("renamed-original-evidence-directory", (17, 31), (17, 31), (17, 32)),
            ("replaced-original-evidence-device", (17, 31), (17, 31), (18, 31)),
            ("forged-original-retained-inode", (17, 32), (17, 31), (17, 32)),
            ("boolean-original-literal-inode", (17, 31), (17, 31), (True, 31)),
            ("negative-original-literal-inode", (17, 31), (17, 31), (-1, 31)),
        ):
            reject(title, lambda retained=retained, expected=expected, literal=literal:
                   require_directory_identity(retained, expected, literal))
        for label in ("", "..", "../escape", "/absolute", "a/b", "a--b",
                      "-bad", "bad-", "CAPS", "bad_name", "a" * 65):
            reject("unsafe-label-" + repr(label),
                   lambda label=label: approved_paths("rust", label))
        for name in ("", "all", "re", "_sre", "../zig", "external"):
            reject("foreign-family-" + repr(name),
                   lambda name=name: family_spec(name))
        for name, operation in (
            ("read", lambda: builtins.open("synthetic-read")),
            ("metadata-read", lambda: os.stat("synthetic-read")),
            ("symlink-metadata-read", lambda: os.lstat("synthetic-read")),
            ("write", lambda: os.write(1, b"synthetic")),
            ("import", lambda: importlib.import_module("candidates.vm_candidate")),
            ("direct-import", lambda: builtins.__import__("candidates.vm_candidate")),
            ("worker", lambda: subprocess.Popen(["synthetic"])),
            ("worker-run", lambda: subprocess.run(["synthetic"])),
            ("worker-call", lambda: subprocess.call(["synthetic"])),
            ("worker-check-call", lambda: subprocess.check_call(["synthetic"])),
            ("worker-check-output", lambda: subprocess.check_output(["synthetic"])),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("gc", lambda: gc.collect()),
        ):
            reject("block-actual-" + name, operation)
        accept("all-seven-real-side-effects-blocked",
               all(count > 0 for count in effects.values()))
        accept("exactly-three-independent-original-families",
               set(FAMILIES) == {"rust", "c", "zig"})
        accept("zero-candidate-imports",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "python": "3.14.6",
        "original_source_relative": ORIGINAL_RELATIVE,
        "original_source_sha256": ORIGINAL_SHA256,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "families": ["rust", "c", "zig"],
        "accepted_control_count": len(accepted), "accepted_controls": accepted,
        "rejected_control_count": len(rejected), "rejected_controls": rejected,
        "blocked_effects": effects,
        "actual_candidate_workers": 0, "actual_reference_workers": 0,
        "actual_original_suite_invocations": 0,
        "real_candidate_files_read": 0, "real_native_binary_files_read": 0,
        "real_candidate_imported": False,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
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
        require(all(getattr(options, field) in (None, False) for field in (
            "record", "candidate", "label", "oracle_source_sha256",
            "matrix_sha256", "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "a synthetic source self-test cannot execute or pin a real candidate")
        result = source_self_test()
    else:
        require(options.record is True,
                "require explicit actual V5 original-suite recording")
        spec = family_spec(options.candidate)
        label = validate_label(options.label)
        pins = OwnerPins(
            family=spec.name,
            original=validate_digest(options.oracle_source_sha256,
                                     "frozen V5 original-suite controller"),
            matrix=validate_digest(options.matrix_sha256,
                                   "frozen 165-method Python matrix"),
            baseline=BASELINE_SHA256,
            candidate=validate_digest(options.candidate_source_sha256,
                                      "caller-pinned candidate adapter"),
            native_engine=validate_digest(options.native_engine_sha256,
                                          "caller-pinned owned native engine"),
            native_bridge=validate_digest(options.native_bridge_sha256,
                                          "caller-pinned owned native bridge"),
        )
        result = record_original(pins, label)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RecorderError, OSError, subprocess.SubprocessError) as error:
        print("frozen V5 original CPython recording failed closed: "
              + str(error), file=sys.stderr)
        raise SystemExit(1) from error
