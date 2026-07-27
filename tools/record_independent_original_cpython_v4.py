#!/usr/bin/env python3
"""Durably record one source-pinned, independent original CPython test run.

Only ``--record --candidate {rust,c,zig}`` starts the immutable V4 controller.
That controller starts exactly one genuine standard-library reference and one
independent candidate. Complete success, mismatch, crash, and process streams
are recorded without overwriting evidence. ``--self-test`` is synthetic and
cannot read files, start workers, import candidates, measure time, or publish.
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
SOURCE_RELATIVE = "tools/record_independent_original_cpython_v4.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SCHEMA = "rebar-independent-original-cpython-recorder-v4"
ORIGINAL_RELATIVE = "tools/independent_original_cpython_suite_v4.py"
ORIGINAL_MODULE = "tools.independent_original_cpython_suite_v4"
ORIGINAL_SHA256 = (
    "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3"
)
ORIGINAL_SCHEMA = "rebar-independent-original-cpython-re-full-methods-v4"
HARNESS_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
HARNESS_SHA256 = (
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
)
IDENTITY_GUARD_RELATIVE = "tools/rust_original_cpython_suite_v2.py"
IDENTITY_GUARD_SHA256 = (
    "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267"
)
WARNING_GUARD_RELATIVE = "tools/rust_original_cpython_suite_v3.py"
WARNING_GUARD_SHA256 = (
    "55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2"
)
MATRIX_SHA256 = (
    "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
)
BASELINE_SHA256 = (
    "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
)
ORIGINAL_TEST_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
ORIGINAL_SUPPORT_SHA256 = (
    "519f9d36eccf2fda59f78c3480bb4b6e35b2ecb51551f11e0ac03ecbfa503159"
)
ORIGINAL_WARNINGS_HELPER_SHA256 = (
    "fc02de4d91bae3988079e3fb3fec3da96ae467fd548295745c2846af179f3870"
)
ORIGINAL_CORPUS_SHA256 = (
    "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab"
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
TOTAL_METHODS = 165
PUBLIC_METHODS = 152
PRIVATE_WAIVER_COUNT = 13
GUARD_CHECKS = 2 * PUBLIC_METHODS
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 128 * 1024 * 1024
PRIVATE_METHODS = (
    "DebugTests.test_debug_flag",
    "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one",
    "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable",
    "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
RESULT_FIELDS = frozenset({
    "schema", "status", "python", "candidate_family",
    "controller_source_sha256", "test_harness_relative",
    "test_harness_sha256", "identity_guard_relative",
    "identity_guard_sha256", "warning_guard_relative",
    "warning_guard_sha256", "matrix_sha256", "original_source_sha256",
    "original_support_sha256", "original_warnings_helper_sha256",
    "original_corpus_sha256", "all_original_method_count",
    "actual_public_method_count", "private_waiver_count", "private_waivers",
    "public_waivers", "all_original_methods_executed",
    "all_original_methods_qualified", "baseline_records_sha256",
    "candidate_records_sha256", "baseline_records", "candidate_records",
    "mismatch_count", "all_mismatches", "baseline_pid", "candidate_pid",
    "native_provenance", "matcher_guard", "actual_candidate_workers",
    "actual_localedef_workers", "actual_private_temporary_directories_created",
    "actual_private_locale_outputs_created",
    "all_private_temporary_directories_removed", "clock_samples",
    "timing_trials_run", "workspace_files_written", "benchmark_files_read",
    "hidden_cases_read", "performance",
    "candidate_qualified_for_hidden_benchmark", "final_winner_selected",
})
RECORD_FIELDS = frozenset({
    "test", "source_ast_sha256", "status", "tests_run", "failure_count",
    "error_count", "skip_count", "failure_tracebacks", "error_tracebacks",
    "skip_reasons",
})


class RecorderError(Exception):
    """Reject substituted original tests, native ownership, or publication."""


class SourceOnlyError(RecorderError):
    """A synthetic control attempted an actual external effect."""


@dataclass(frozen=True)
class FamilySpec:
    name: str
    adapter_module: str
    adapter_relative: str
    engine_relative: str
    bridge_module: str
    bridge_relative: str
    owned_ctypes: bool = False


FAMILIES = {
    "rust": FamilySpec(
        "rust", "candidates.rust_candidate", "candidates/rust_candidate.py",
        "candidates/_rust_engine.so", "candidates._rust_bridge",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
    ),
    "c": FamilySpec(
        "c", "candidates.vm_candidate", "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates._vm_native", "candidates/_vm_native" + EXTENSION_SUFFIX,
    ),
    "zig": FamilySpec(
        "zig", "candidates.zig_candidate", "candidates/zig_candidate.py",
        "candidates/_zig_probe.so", "candidates._zig_bridge",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX, owned_ctypes=True,
    ),
}


@dataclass(frozen=True)
class OwnerPins:
    family: str
    original: str
    matrix: str
    baseline: str
    candidate: str
    native_engine: str
    native_bridge: str


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64 and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value),
        "an independently pinned lowercase SHA-256 is required: " + label,
    )
    return value


def verify_runtime() -> None:
    expected = str(ROOT / SOURCE_RELATIVE)
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path) and sys.path[0] == str(ROOT)
        and os.path.abspath(__file__) == expected
        and os.path.realpath(__file__) == expected
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
        "use only isolated, no-bytecode, pinned CPython 3.14.6",
    )
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "the durable original recorder must never import a candidate",
    )


def family_spec(name: Any) -> FamilySpec:
    require(type(name) is str and name in FAMILIES,
            "select exactly one independent Rust, C, or Zig family")
    spec = FAMILIES[name]
    require(
        isinstance(spec, FamilySpec) and spec.name == name
        and spec.adapter_relative.startswith("candidates/")
        and spec.engine_relative.startswith("candidates/")
        and spec.bridge_relative.startswith("candidates/")
        and spec.adapter_module.startswith("candidates.")
        and spec.bridge_module.startswith("candidates.")
        and spec.adapter_module != spec.bridge_module
        and spec.bridge_relative.endswith(EXTENSION_SUFFIX)
        and (spec.engine_relative == spec.bridge_relative) == (name == "c")
        and spec.owned_ctypes == (name == "zig"),
        "the immutable independent-family ownership policy was substituted",
    )
    return spec


def validate_owner_pins(pins: OwnerPins) -> FamilySpec:
    require(isinstance(pins, OwnerPins),
            "the complete independent native pins are mandatory")
    spec = family_spec(pins.family)
    for key in ("original", "matrix", "baseline", "candidate",
                "native_engine", "native_bridge"):
        validate_digest(getattr(pins, key), key)
    require((pins.native_engine == pins.native_bridge) == (spec.name == "c"),
            "only the genuine C engine and native bridge may share a hash")
    return spec


def validate_label(value: Any) -> str:
    require(
        type(value) is str and 1 <= len(value) <= 64
        and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-"
                for letter in value)
        and "--" not in value,
        "require a bounded, lowercase, nonescaping original-run label",
    )
    return value


def approved_paths(family: Any, label: Any) -> tuple[str, str]:
    spec = family_spec(family)
    slug = validate_label(label)
    basename = spec.name + "-original-v4-" + slug
    return (
        APPROVED_DIRECTORY + "/" + basename + ".json",
        APPROVED_DIRECTORY + "/" + basename + "-publication-receipt.json",
    )


def relative_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "an exact owned, no-follow relative path is mandatory")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative,
            "an independent original recorder path escaped its root")
    return parts


def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0))


def read_owned_regular(
    relative: str, expected: str, *, maximum: int,
) -> tuple[bytes, dict[str, Any]]:
    parts = relative_parts(relative)
    validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "an exact bounded, owned source or native artifact is mandatory")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the literal recorder root is not an owned directory")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an owned source parent is not a real directory")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino)
                == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum,
                "an owned source was substituted, linked, or unbounded")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "a complete authenticated artifact was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "an authenticated artifact gained a concealed suffix")
        after = os.fstat(descriptor)
        require((after.st_dev, after.st_ino, after.st_size)
                == (before.st_dev, before.st_ino, before.st_size),
                "an authenticated artifact changed while being read")
        raw = b"".join(chunks)
        require(hashlib.sha256(raw).hexdigest() == expected,
                "an independently pinned artifact changed: " + relative)
        return raw, {
            "relative": relative, "sha256": expected, "bytes": len(raw),
            "device": before.st_dev, "inode": before.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def authenticate_sources(pins: OwnerPins) -> tuple[Any, list[dict[str, Any]]]:
    verify_runtime()
    spec = validate_owner_pins(pins)
    require(pins.original == ORIGINAL_SHA256
            and pins.matrix == MATRIX_SHA256
            and pins.baseline == BASELINE_SHA256,
            "pin the exact immutable V4 controller, matrix, and baseline")
    for relative, expected in (
        (ORIGINAL_RELATIVE, ORIGINAL_SHA256),
        (HARNESS_RELATIVE, HARNESS_SHA256),
        (IDENTITY_GUARD_RELATIVE, IDENTITY_GUARD_SHA256),
        (WARNING_GUARD_RELATIVE, WARNING_GUARD_SHA256),
    ):
        read_owned_regular(relative, expected, maximum=MAX_SOURCE_BYTES)
    suite = importlib.import_module(ORIGINAL_MODULE)
    require(
        suite.__name__ == ORIGINAL_MODULE
        and os.path.abspath(suite.__file__) == str(ROOT / ORIGINAL_RELATIVE)
        and os.path.realpath(suite.__file__) == str(ROOT / ORIGINAL_RELATIVE)
        and suite.current_source_sha256() == ORIGINAL_SHA256
        and suite.SCHEMA == ORIGINAL_SCHEMA
        and suite.MATRIX_SHA256 == MATRIX_SHA256
        and suite.BASELINE_SHA256 == BASELINE_SHA256
        and suite.ORIGINAL_METHOD_COUNT == TOTAL_METHODS
        and suite.PUBLIC_METHOD_COUNT == PUBLIC_METHODS
        and suite.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT,
        "the frozen independent V4 original controller was substituted",
    )
    source_spec = suite.family_spec(spec.name)
    require(
        source_spec.name == spec.name
        and source_spec.adapter_module == spec.adapter_module
        and source_spec.adapter_relative == spec.adapter_relative
        and source_spec.engine_relative == spec.engine_relative
        and source_spec.bridge_module == spec.bridge_module
        and source_spec.bridge_relative == spec.bridge_relative
        and source_spec.owned_ctypes is spec.owned_ctypes,
        "the source-pinned independent engine or legitimate Zig FFI changed",
    )
    _, _, harness, matrix = suite.load_frozen_oracles()
    require(
        harness.current_source_sha256() == HARNESS_SHA256
        and harness.METHOD_MATRIX_SHA256 == MATRIX_SHA256
        and harness.BASELINE_RECORDS_SHA256 == BASELINE_SHA256
        and harness.TEST_SOURCE_SHA256 == ORIGINAL_TEST_SHA256
        and harness.SUPPORT_SHA256 == ORIGINAL_SUPPORT_SHA256
        and harness.WARNINGS_HELPER_SHA256 == ORIGINAL_WARNINGS_HELPER_SHA256
        and harness.CORPUS_SHA256 == ORIGINAL_CORPUS_SHA256
        and tuple(harness.PRIVATE_METHODS) == PRIVATE_METHODS
        and type(matrix) is list and len(matrix) == TOTAL_METHODS
        and digest(matrix) == MATRIX_SHA256,
        "the complete unchanged original 165-method CPython matrix changed",
    )
    verify_runtime()
    return suite, matrix


def valid_provenance(
    actual: Any, spec: FamilySpec, pins: OwnerPins,
) -> bool:
    if type(actual) is not dict or set(actual) != {
        "source", "native_engine", "native_bridge",
    }:
        return False
    expected = (
        ("source", spec.adapter_relative, pins.candidate),
        ("native_engine", spec.engine_relative, pins.native_engine),
        ("native_bridge", spec.bridge_relative, pins.native_bridge),
    )
    for key, relative, expected_sha in expected:
        owner = actual.get(key)
        if not (
            type(owner) is dict
            and set(owner) == {"relative", "sha256", "bytes", "device", "inode"}
            and owner.get("relative") == relative
            and owner.get("sha256") == expected_sha
            and type(owner.get("bytes")) is int and owner["bytes"] > 0
            and type(owner.get("device")) is int and owner["device"] >= 0
            and type(owner.get("inode")) is int and owner["inode"] > 0
        ):
            return False
    return (actual["native_engine"] == actual["native_bridge"]) \
        == (spec.name == "c")


def authenticate_candidate_owners(pins: OwnerPins) -> dict[str, Any]:
    spec = validate_owner_pins(pins)
    owners: dict[str, Any] = {}
    for key, relative, expected, maximum in (
        ("source", spec.adapter_relative, pins.candidate, MAX_SOURCE_BYTES),
        ("native_engine", spec.engine_relative, pins.native_engine,
         MAX_BINARY_BYTES),
        ("native_bridge", spec.bridge_relative, pins.native_bridge,
         MAX_BINARY_BYTES),
    ):
        if key == "native_bridge" and spec.name == "c":
            owners[key] = dict(owners["native_engine"])
        else:
            _, owners[key] = read_owned_regular(
                relative, expected, maximum=maximum,
            )
    require(valid_provenance(owners, spec, pins),
            "the selected adapter, native engine, or native bridge changed")
    return owners


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "duplicate evidence keys cannot conceal an original failure")
        result[key] = value
    return result


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "the complete canonical V4 process output is mandatory: " + label)
    try:
        document = json.loads(
            raw, object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                RecorderError("nonfinite original evidence is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise RecorderError(
            "invalid complete V4 process JSON: " + label,
        ) from error
    require(type(document) is dict and canonical(document) == raw,
            "the canonical V4 process output was clipped or substituted")
    return document


def validate_original_record(
    requirement: Mapping[str, Any], observed: Any,
) -> dict[str, Any]:
    require(
        type(observed) is dict and set(observed) == RECORD_FIELDS
        and observed.get("test") == requirement["test"]
        and observed.get("source_ast_sha256")
        == requirement["source_ast_sha256"]
        and observed.get("status") in ("PASS", "FAIL", "SKIP")
        and observed.get("tests_run") == 1,
        "an exact source-ordered original method or result was substituted",
    )
    for count, vector in (
        ("failure_count", "failure_tracebacks"),
        ("error_count", "error_tracebacks"),
        ("skip_count", "skip_reasons"),
    ):
        values = observed.get(vector)
        require(type(values) is list
                and all(type(value) is str for value in values)
                and type(observed.get(count)) is int
                and observed[count] == len(values),
                "a complete original failure, traceback, or skip was hidden")
    expected_status = (
        "FAIL" if observed["failure_count"] or observed["error_count"]
        else "SKIP" if observed["skip_count"] else "PASS"
    )
    require(observed["status"] == expected_status
            and not (observed["skip_count"]
                     and (observed["failure_count"] or observed["error_count"])),
            "a genuine original failure or skip was misclassified")
    return observed


def validate_guard(value: Any, spec: FamilySpec) -> None:
    fields = {
        "cached_original_matcher_descendant_count",
        "cached_original_holder_count", "original_matchers_blocked",
        "adapter_import_quarantined", "native_sre_blocked",
        "builtins_import_guarded", "importlib_import_guarded",
        "actual_object_identity_guarded", "public_type_names_used_for_ownership",
        "actual_method_guard_checks", "warning_registry_introspection_safe",
        "warning_registry_exactly_absent",
        "actual_warning_registry_guard_checks", "cross_family_imports_blocked",
        "external_regex_imports_blocked", "owned_native_ffi_allowed",
        "owned_ctypes_load_count", "owned_ctypes_symbol_count",
    }
    require(type(value) is dict and set(value) == fields,
            "the complete original native and warning guards are mandatory")
    for name in (
        "original_matchers_blocked", "adapter_import_quarantined",
        "native_sre_blocked", "builtins_import_guarded",
        "importlib_import_guarded", "actual_object_identity_guarded",
        "warning_registry_introspection_safe",
        "warning_registry_exactly_absent", "cross_family_imports_blocked",
        "external_regex_imports_blocked",
    ):
        require(value.get(name) is True,
                "an actual continuous original ownership guard failed: " + name)
    require(value.get("public_type_names_used_for_ownership") is False
            and value.get("actual_method_guard_checks") == GUARD_CHECKS
            and value.get("actual_warning_registry_guard_checks") == GUARD_CHECKS
            and value.get("owned_native_ffi_allowed") is spec.owned_ctypes,
            "all 304 identity checks and 304 warning checks are mandatory")
    for name in (
        "cached_original_matcher_descendant_count",
        "cached_original_holder_count", "owned_ctypes_load_count",
        "owned_ctypes_symbol_count",
    ):
        actual = value.get(name)
        require(type(actual) is int and actual >= 0,
                "an actual owned-native guard count was hidden: " + name)
    if not spec.owned_ctypes:
        require(value["owned_ctypes_load_count"] == 0
                and value["owned_ctypes_symbol_count"] == 0,
                "unowned dynamic FFI escaped the Rust or C native boundary")
    else:
        require(value["owned_ctypes_load_count"] >= 1
                and value["owned_ctypes_symbol_count"] >= 1,
                "the owned, independently pinned Zig native FFI was omitted")


def validate_suite_result(
    result: Any, matrix: list[dict[str, Any]], pins: OwnerPins,
    owners: Mapping[str, Any],
) -> dict[str, Any]:
    spec = validate_owner_pins(pins)
    require(type(result) is dict and set(result) == RESULT_FIELDS,
            "every exact V4 candidate result field must be preserved")
    require(type(matrix) is list and len(matrix) == TOTAL_METHODS
            and digest(matrix) == pins.matrix,
            "the complete source-ordered 165-method matrix was substituted")
    expected = {
        "schema": ORIGINAL_SCHEMA + "-actual-original-candidate-result",
        "python": "3.14.6", "candidate_family": spec.name,
        "controller_source_sha256": pins.original,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "matrix_sha256": pins.matrix,
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
        "baseline_records_sha256": pins.baseline,
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
    for name, value in expected.items():
        require(result.get(name) == value,
                "an exact original V4 observation changed: " + name)
    public = [row for row in matrix if row.get("classification") == "public"]
    private = [row for row in matrix
               if row.get("classification") == "named-private-waiver"]
    require(len(public) == PUBLIC_METHODS
            and len(private) == PRIVATE_WAIVER_COUNT
            and tuple(row["test"] for row in private) == PRIVATE_METHODS,
            "an original public method or named private waiver was substituted")
    baseline = result.get("baseline_records")
    candidate = result.get("candidate_records")
    require(type(baseline) is list and type(candidate) is list
            and len(baseline) == len(candidate) == PUBLIC_METHODS
            and digest(baseline) == pins.baseline
            and result.get("candidate_records_sha256") == digest(candidate),
            "both complete genuine 152-method vectors are mandatory")
    mismatches: list[dict[str, Any]] = []
    for requirement, original, observed in zip(
        public, baseline, candidate, strict=True,
    ):
        original = validate_original_record(requirement, original)
        observed = validate_original_record(requirement, observed)
        if original != observed:
            mismatches.append({
                "test": requirement["test"],
                "baseline": original, "candidate": observed,
            })
    require(sum(row["status"] == "PASS" for row in baseline) == 151
            and sum(row["status"] == "SKIP" for row in baseline) == 1
            and sum(row["status"] == "FAIL" for row in baseline) == 0,
            "the authentic CPython baseline needs 151 passes and one skip")
    skips = [row for row in baseline if row["status"] == "SKIP"]
    require(skips[0]["test"] == "ReTests.test_memory_leaks"
            and skips[0]["skip_reasons"] == ["requires debug build"],
            "the one genuine debug-build-only original skip was substituted")
    require(type(result.get("all_mismatches")) is list
            and result["all_mismatches"] == mismatches
            and type(result.get("mismatch_count")) is int
            and result["mismatch_count"] == len(mismatches)
            and result.get("status") == ("FAIL" if mismatches else "PASS"),
            "a complete original mismatch or failure traceback was hidden")
    baseline_pid = result.get("baseline_pid")
    candidate_pid = result.get("candidate_pid")
    require(type(baseline_pid) is int and baseline_pid > 0
            and type(candidate_pid) is int and candidate_pid > 0
            and baseline_pid != candidate_pid,
            "the genuine standard reference and candidate are not isolated")
    require(valid_provenance(owners, spec, pins)
            and valid_provenance(result.get("native_provenance"), spec, pins)
            and result["native_provenance"] == dict(owners),
            "the independently pinned source, engine, or bridge was replaced")
    validate_guard(result.get("matcher_guard"), spec)
    return result


def capture_stream(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "the complete bounded original process stream is mandatory: " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def build_complete_report(
    *, label: str, stdout: bytes, stderr: bytes, returncode: int,
    process_pid: int, matrix: list[dict[str, Any]], pins: OwnerPins,
    owners_before: Mapping[str, Any], owners_after: Mapping[str, Any] | None,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    spec = validate_owner_pins(pins)
    slug = validate_label(label)
    require(type(process_pid) is int and process_pid > 0
            and type(returncode) is int
            and valid_provenance(owners_before, spec, pins),
            "the actual V4 controller process and owned pre-run engine are required")
    full_stdout = capture_stream(stdout, "V4 controller stdout")
    full_stderr = capture_stream(stderr, "V4 controller stderr")
    failure = post_run_error
    result: dict[str, Any] | None = None
    if (owners_after is None
            or not valid_provenance(owners_after, spec, pins)
            or dict(owners_after) != dict(owners_before)):
        failure = (failure + "; " if failure else "") \
            + "the actual independently owned native artifacts changed"
    try:
        parsed = decode_canonical(stdout, "complete V4 controller stdout")
        result = validate_suite_result(parsed, matrix, pins, owners_before)
        require(returncode == (0 if result["status"] == "PASS" else 1),
                "the genuine complete V4 process exit was misclassified")
        require(not stderr,
                "the V4 process emitted a complete infrastructure failure")
        require(process_pid not in (
            result["baseline_pid"], result["candidate_pid"],
        ), "the outer V4 controller was confused with an isolated worker")
    except (RecorderError, ValueError, TypeError, KeyError) as error:
        failure = (failure + "; " if failure else "") + str(error)
    status = "PASS" if result is not None \
        and result["status"] == "PASS" and failure is None else "FAIL"
    baseline = result["baseline_records"] if result is not None else []
    candidate = result["candidate_records"] if result is not None else []
    mismatches = result["all_mismatches"] if result is not None else []
    return {
        "schema": SCHEMA + "-complete-first-run-report",
        "status": status, "label": slug, "python": "3.14.6",
        "candidate_family": spec.name,
        "original_suite_relative": ORIGINAL_RELATIVE,
        "original_suite_sha256": pins.original,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "original_test_source_sha256": ORIGINAL_TEST_SHA256,
        "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
        "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
        "matrix_sha256": pins.matrix,
        "expected_baseline_records_sha256": pins.baseline,
        "baseline_records_sha256": (
            result["baseline_records_sha256"] if result is not None else None
        ),
        "candidate_records_sha256": (
            result["candidate_records_sha256"] if result is not None else None
        ),
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS), "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "validated_baseline_record_count": len(baseline),
        "validated_candidate_record_count": len(candidate),
        "baseline_records": baseline,
        "candidate_records": candidate,
        "mismatch_count": len(mismatches) if result is not None else None,
        "all_mismatches": mismatches if result is not None else None,
        "all_mismatches_preserved": result is not None,
        "complete_original_suite_result": result,
        "complete_original_process_stdout": full_stdout,
        "complete_original_process_stderr": full_stderr,
        "original_process_pid": process_pid,
        "original_process_returncode": returncode,
        "actual_original_suite_invocations": 1,
        "actual_reference_workers": 1 if result is not None else None,
        "actual_candidate_workers": 1 if result is not None else None,
        "baseline_pid": result["baseline_pid"] if result is not None else None,
        "candidate_pid": result["candidate_pid"] if result is not None else None,
        "candidate_source_relative": spec.adapter_relative,
        "candidate_source_sha256": pins.candidate,
        "native_engine_relative": spec.engine_relative,
        "native_engine_sha256": pins.native_engine,
        "native_bridge_relative": spec.bridge_relative,
        "native_bridge_sha256": pins.native_bridge,
        "candidate_provenance_before": dict(owners_before),
        "candidate_provenance_after": (
            dict(owners_after) if owners_after is not None else None
        ),
        "candidate_provenance_unchanged": (
            owners_after is not None
            and valid_provenance(owners_after, spec, pins)
            and dict(owners_after) == dict(owners_before)
        ),
        "matcher_guard": result["matcher_guard"] if result is not None else None,
        "actual_method_guard_checks": (
            result["matcher_guard"]["actual_method_guard_checks"]
            if result is not None else None
        ),
        "actual_warning_registry_guard_checks": (
            result["matcher_guard"]["actual_warning_registry_guard_checks"]
            if result is not None else None
        ),
        "owned_native_ffi_allowed": (
            result["matcher_guard"]["owned_native_ffi_allowed"]
            if result is not None else None
        ),
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
        "validation_error": failure,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "native_elf_or_external_engine_audit": "NOT ESTABLISHED BY THIS ORACLE",
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written_by_original_suite": (
            result["workspace_files_written"] if result is not None else None
        ),
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


@contextlib.contextmanager
def preflight_fresh_outputs(
    family: str, label: str,
) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(family, label)
    report_parts = relative_parts(report)
    receipt_parts = relative_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "preflight two distinct, exact, family-specific evidence paths")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact evidence root is not a real owned directory")
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the evidence parent is absent or follows a symlink")
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError(
                "refusing to overwrite existing original evidence: " + basename,
            )
        identity = os.fstat(current)
        preflight = {
            "report_relative": report, "receipt_relative": receipt,
            "report_basename": report_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": identity.st_dev,
            "directory_inode": identity.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
        }
        verify_retained_directory(preflight)
        yield preflight
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def verify_retained_directory(preflight: Mapping[str, Any]) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain the exact preflight-approved evidence directory")
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode)
            and retained.st_dev == preflight.get("directory_device")
            and retained.st_ino == preflight.get("directory_inode"),
            "the preflight-approved evidence directory descriptor changed")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an exact current evidence parent became a symlink")
        current_identity = os.fstat(current)
        require((current_identity.st_dev, current_identity.st_ino)
                == (retained.st_dev, retained.st_ino),
                "the declared evidence pathname no longer names its retained directory")
    finally:
        for opened_descriptor in reversed(opened):
            os.close(opened_descriptor)
    return descriptor


def read_published(
    preflight: Mapping[str, Any], document: Mapping[str, Any],
    publication: Mapping[str, Any], *, kind: str,
) -> bytes:
    require(kind in ("report", "receipt"),
            "read back only the genuine report or publication receipt")
    directory = verify_retained_directory(preflight)
    expected = canonical(dict(document))
    require(type(publication) is dict
            and publication.get("path") == preflight[kind + "_relative"]
            and publication.get("bytes") == len(expected)
            and publication.get("sha256")
            == hashlib.sha256(expected).hexdigest()
            and type(publication.get("actual_write_calls")) is int
            and publication["actual_write_calls"] >= 1
            and publication.get("file_fsync_completed") is True
            and publication.get("directory_fsync_completed") is True
            and publication.get("atomic_no_overwrite_link") is True,
            "the durable atomic original publication was substituted")
    basename = preflight[kind + "_basename"]
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        actual_stat = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(actual_stat.st_mode)
                and stat.S_ISREG(named.st_mode)
                and (actual_stat.st_dev, actual_stat.st_ino)
                == (named.st_dev, named.st_ino)
                and actual_stat.st_size == len(expected),
                "the atomic evidence inode or complete size was substituted")
        remaining = len(expected)
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the complete atomic evidence readback was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "atomic evidence gained a concealed suffix")
    finally:
        os.close(descriptor)
    actual = b"".join(chunks)
    require(actual == expected
            and hashlib.sha256(actual).hexdigest() == publication["sha256"],
            "the complete original vectors, tracebacks, or streams were lost")
    verify_retained_directory(preflight)
    return actual


def publish_fresh(
    preflight: Mapping[str, Any], document: Mapping[str, Any], *, kind: str,
) -> tuple[dict[str, Any], bytes]:
    require(kind in ("report", "receipt"),
            "atomically publish only the approved original report or receipt")
    directory = verify_retained_directory(preflight)
    raw = canonical(dict(document))
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "the complete original publication exceeds its exact bound")
    basename = preflight[kind + "_basename"]
    temp_name = (
        ".rebar-original-v4-" + basename + "-"
        + str(os.getpid()) + "-" + hashlib.sha256(raw).hexdigest()[:16]
    )
    relative_parts(temp_name)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(temp_name, flags, 0o644, dir_fd=directory)
    temp_identity: tuple[int, int] | None = None
    linked = False
    actual_write_calls = 0
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode),
                "the exclusive atomic evidence temporary is not a real file")
        temp_identity = (identity.st_dev, identity.st_ino)
        named = os.stat(temp_name, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == temp_identity,
                "the owned atomic evidence temporary was substituted")
        position = 0
        while position < len(raw):
            count = os.write(descriptor, raw[position:])
            actual_write_calls += 1
            require(type(count) is int and count > 0,
                    "the complete atomic evidence write was truncated")
            position += count
        os.fsync(descriptor)
        require(os.fstat(descriptor).st_size == len(raw),
                "the complete atomic evidence temporary lost bytes")
        verify_retained_directory(preflight)
        named = os.stat(temp_name, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == temp_identity,
                "the owned atomic evidence temporary changed before linking")
        os.link(temp_name, basename, src_dir_fd=directory,
                dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.fsync(directory)
        verify_retained_directory(preflight)
        destination = os.stat(basename, dir_fd=directory,
                              follow_symlinks=False)
        require((destination.st_dev, destination.st_ino) == temp_identity,
                "the completed, no-overwrite atomic evidence was substituted")
        temporary = os.stat(temp_name, dir_fd=directory,
                            follow_symlinks=False)
        require((temporary.st_dev, temporary.st_ino) == temp_identity,
                "refusing to unlink a substituted atomic evidence temporary")
        os.unlink(temp_name, dir_fd=directory)
        os.fsync(directory)
    except BaseException:
        if not linked and temp_identity is not None:
            try:
                temporary = os.stat(temp_name, dir_fd=directory,
                                    follow_symlinks=False)
                if (temporary.st_dev, temporary.st_ino) == temp_identity:
                    os.unlink(temp_name, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, RecorderError):
                pass
        raise
    finally:
        os.close(descriptor)
    publication = {
        "path": preflight[kind + "_relative"],
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "actual_write_calls": actual_write_calls,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "owned_temporary_removed": True,
    }
    return publication, read_published(
        preflight, document, publication, kind=kind,
    )


def run_exactly_one_original(
    pins: OwnerPins,
) -> tuple[bytes, bytes, int, int]:
    spec = validate_owner_pins(pins)
    verify_runtime()
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / ORIGINAL_RELATIVE),
        "--candidate", spec.name,
        "--oracle-source-sha256", pins.original,
        "--matrix-sha256", pins.matrix,
        "--candidate-source-sha256", pins.candidate,
        "--native-engine-sha256", pins.native_engine,
        "--native-bridge-sha256", pins.native_bridge,
    ]
    process = subprocess.Popen(
        arguments, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(ROOT), shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "LC_ALL": "C", "PATH": "/usr/bin:/bin",
        },
    )
    stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and type(process.returncode) is int
            and type(process.pid) is int and process.pid > 0,
            "the one complete independent V4 process was not collected")
    return stdout, stderr, process.returncode, process.pid


def record_original(label: str, pins: OwnerPins) -> dict[str, Any]:
    slug = validate_label(label)
    spec = validate_owner_pins(pins)
    _, matrix = authenticate_sources(pins)
    owners_before = authenticate_candidate_owners(pins)
    with preflight_fresh_outputs(spec.name, slug) as preflight:
        verify_retained_directory(preflight)
        before_launch = authenticate_candidate_owners(pins)
        require(before_launch == owners_before,
                "an exact frozen native owner changed before its first run")
        stdout, stderr, returncode, process_pid = run_exactly_one_original(pins)
        owners_after: dict[str, Any] | None = None
        post_run_error: str | None = None
        try:
            owners_after = authenticate_candidate_owners(pins)
        except (RecorderError, OSError, ValueError, TypeError) as error:
            post_run_error = "post-run native owner verification failed: " + str(error)
        report = build_complete_report(
            label=slug, stdout=stdout, stderr=stderr,
            returncode=returncode, process_pid=process_pid,
            matrix=matrix, pins=pins, owners_before=owners_before,
            owners_after=owners_after, post_run_error=post_run_error,
        )
        verify_runtime()
        report_publication, raw_report = publish_fresh(
            preflight, report, kind="report",
        )
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS", "correctness_status": report["status"],
            "label": slug, "python": "3.14.6",
            "candidate_family": spec.name,
            "original_suite_relative": ORIGINAL_RELATIVE,
            "original_suite_sha256": pins.original,
            "test_harness_relative": HARNESS_RELATIVE,
            "test_harness_sha256": HARNESS_SHA256,
            "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
            "identity_guard_sha256": IDENTITY_GUARD_SHA256,
            "warning_guard_relative": WARNING_GUARD_RELATIVE,
            "warning_guard_sha256": WARNING_GUARD_SHA256,
            "original_test_source_sha256": ORIGINAL_TEST_SHA256,
            "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
            "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
            "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
            "matrix_sha256": pins.matrix,
            "expected_baseline_records_sha256": pins.baseline,
            "baseline_records_sha256": report["baseline_records_sha256"],
            "candidate_records_sha256": report["candidate_records_sha256"],
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVER_COUNT,
            "private_waivers": list(PRIVATE_METHODS), "public_waivers": [],
            "validated_baseline_record_count": report[
                "validated_baseline_record_count"
            ],
            "validated_candidate_record_count": report[
                "validated_candidate_record_count"
            ],
            "mismatch_count": report["mismatch_count"],
            "all_mismatches_preserved": report["all_mismatches_preserved"],
            "actual_method_guard_checks": report["actual_method_guard_checks"],
            "actual_warning_registry_guard_checks": report[
                "actual_warning_registry_guard_checks"
            ],
            "owned_native_ffi_allowed": report["owned_native_ffi_allowed"],
            "candidate_source_relative": spec.adapter_relative,
            "candidate_source_sha256": pins.candidate,
            "native_engine_relative": spec.engine_relative,
            "native_engine_sha256": pins.native_engine,
            "native_bridge_relative": spec.bridge_relative,
            "native_bridge_sha256": pins.native_bridge,
            "candidate_provenance_before": dict(owners_before),
            "candidate_provenance_after": (
                dict(owners_after) if owners_after is not None else None
            ),
            "candidate_provenance_unchanged": report[
                "candidate_provenance_unchanged"
            ],
            "original_process_pid": process_pid,
            "original_process_returncode": returncode,
            "original_process_stdout_sha256": report[
                "complete_original_process_stdout"
            ]["sha256"],
            "original_process_stdout_bytes": report[
                "complete_original_process_stdout"
            ]["bytes"],
            "original_process_stderr_sha256": report[
                "complete_original_process_stderr"
            ]["sha256"],
            "original_process_stderr_bytes": report[
                "complete_original_process_stderr"
            ]["bytes"],
            "actual_original_suite_invocations": 1,
            "actual_reference_workers": report["actual_reference_workers"],
            "actual_candidate_workers": report["actual_candidate_workers"],
            "report_relative": preflight["report_relative"],
            "report_sha256": hashlib.sha256(raw_report).hexdigest(),
            "report_bytes": len(raw_report),
            "report_actual_write_calls": report_publication[
                "actual_write_calls"
            ],
            "report_file_fsync_completed": True,
            "report_directory_fsync_completed": True,
            "report_atomic_no_overwrite_link": True,
            "report_complete_readback_verified": True,
            "receipt_complete_readback_required": True,
            "receipt_complete_readback_verified": True,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
            "native_elf_or_external_engine_audit":
            "NOT ESTABLISHED BY THIS ORACLE",
            "clock_samples": 0, "timing_trials_run": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        receipt_publication, raw_receipt = publish_fresh(
            preflight, receipt, kind="receipt",
        )
        verify_runtime()
        return {
            "schema": SCHEMA + "-compact-result",
            "status": report["status"], "label": slug,
            "python": "3.14.6", "candidate_family": spec.name,
            "original_suite_sha256": pins.original,
            "matrix_sha256": pins.matrix,
            "baseline_records_sha256": report["baseline_records_sha256"],
            "candidate_records_sha256": report["candidate_records_sha256"],
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVER_COUNT,
            "public_waivers": [],
            "validated_baseline_record_count": report[
                "validated_baseline_record_count"
            ],
            "validated_candidate_record_count": report[
                "validated_candidate_record_count"
            ],
            "mismatch_count": report["mismatch_count"],
            "all_mismatches_preserved": report["all_mismatches_preserved"],
            "actual_method_guard_checks": report["actual_method_guard_checks"],
            "actual_warning_registry_guard_checks": report[
                "actual_warning_registry_guard_checks"
            ],
            "candidate_source_sha256": pins.candidate,
            "native_engine_sha256": pins.native_engine,
            "native_bridge_sha256": pins.native_bridge,
            "original_process_returncode": returncode,
            "actual_original_suite_invocations": 1,
            "actual_reference_workers": report["actual_reference_workers"],
            "actual_candidate_workers": report["actual_candidate_workers"],
            "report_publication": report_publication,
            "receipt_publication": receipt_publication,
            "receipt_complete_readback_verified": True,
            "receipt_verified_bytes": len(raw_receipt),
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
            "clock_samples": 0, "timing_trials_run": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0, "file_writes": 0,
        "candidate_imports": 0, "reference_imports": 0,
        "workers_started": 0, "threads_started": 0,
        "clock_samples": 0, "gc_collections": 0,
        "hidden_cases_read": 0, "performance_files_read": 0,
        "blocked_reads": 0, "blocked_writes": 0,
        "blocked_imports": 0, "blocked_workers": 0,
        "blocked_threads": 0, "blocked_clocks": 0,
        "blocked_gc_collections": 0,
    }
    installed: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def deny(counter: str, message: str) -> Callable[..., Any]:
        def blocked(*args: Any, **keywords: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyError(message)
        return blocked

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, deny(
                "blocked_reads", "a synthetic V4 control cannot read files",
            ))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "rename"), (os, "replace"), (os, "link"),
            (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, deny(
                "blocked_writes", "a synthetic V4 control cannot publish files",
            ))
        install(importlib, "import_module", deny(
            "blocked_imports", "a synthetic V4 control cannot import engines",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "a synthetic V4 control cannot import modules",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny(
                "blocked_workers", "a synthetic V4 control cannot start workers",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "a synthetic V4 control cannot start threads",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns",
        ):
            install(time, name, deny(
                "blocked_clocks", "a synthetic V4 control cannot sample clocks",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections",
            "a synthetic V4 control cannot collect garbage",
        ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_documents(
    family: str,
) -> tuple[list[dict[str, Any]], OwnerPins, dict[str, Any],
           dict[str, Any], dict[str, Any]]:
    spec = family_spec(family)
    matrix: list[dict[str, Any]] = []
    baseline: list[dict[str, Any]] = []
    for index in range(PUBLIC_METHODS):
        name = (
            "ReTests.test_memory_leaks" if index == PUBLIC_METHODS - 1
            else "ReTests.test_synthetic_" + format(index, "03d")
        )
        ast_sha = hashlib.sha256(name.encode("ascii")).hexdigest()
        matrix.append({
            "index": index, "test": name, "class": "ReTests",
            "method": name.split(".", 1)[1],
            "source_ast_sha256": ast_sha,
            "classification": "public", "waiver_reason": None,
        })
        skipped = index == PUBLIC_METHODS - 1
        baseline.append({
            "test": name, "source_ast_sha256": ast_sha,
            "status": "SKIP" if skipped else "PASS", "tests_run": 1,
            "failure_count": 0, "error_count": 0,
            "skip_count": 1 if skipped else 0,
            "failure_tracebacks": [], "error_tracebacks": [],
            "skip_reasons": ["requires debug build"] if skipped else [],
        })
    for identity in PRIVATE_METHODS:
        cls, method = identity.split(".", 1)
        matrix.append({
            "index": len(matrix), "test": identity, "class": cls,
            "method": method,
            "source_ast_sha256": hashlib.sha256(
                identity.encode("ascii"),
            ).hexdigest(),
            "classification": "named-private-waiver",
            "waiver_reason": "synthetic named private-only control",
        })
    candidate_pin = {"rust": "12", "c": "34", "zig": "56"}[family] * 32
    engine_pin = {"rust": "78", "c": "9a", "zig": "bc"}[family] * 32
    bridge_pin = engine_pin if family == "c" else {
        "rust": "de" * 32, "zig": "ef" * 32,
    }[family]
    pins = OwnerPins(
        family=family, original=ORIGINAL_SHA256, matrix=digest(matrix),
        baseline=digest(baseline), candidate=candidate_pin,
        native_engine=engine_pin, native_bridge=bridge_pin,
    )
    owners = {
        "source": {
            "relative": spec.adapter_relative, "sha256": pins.candidate,
            "bytes": 113, "device": 17, "inode": 101,
        },
        "native_engine": {
            "relative": spec.engine_relative, "sha256": pins.native_engine,
            "bytes": 227, "device": 17, "inode": 102,
        },
    }
    owners["native_bridge"] = (
        dict(owners["native_engine"]) if family == "c" else {
            "relative": spec.bridge_relative,
            "sha256": pins.native_bridge,
            "bytes": 331, "device": 17, "inode": 103,
        }
    )
    guard = {
        "cached_original_matcher_descendant_count": 5,
        "cached_original_holder_count": 7,
        "original_matchers_blocked": True,
        "adapter_import_quarantined": True, "native_sre_blocked": True,
        "builtins_import_guarded": True, "importlib_import_guarded": True,
        "actual_object_identity_guarded": True,
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": GUARD_CHECKS,
        "warning_registry_introspection_safe": True,
        "warning_registry_exactly_absent": True,
        "actual_warning_registry_guard_checks": GUARD_CHECKS,
        "cross_family_imports_blocked": True,
        "external_regex_imports_blocked": True,
        "owned_native_ffi_allowed": spec.owned_ctypes,
        "owned_ctypes_load_count": 1 if spec.owned_ctypes else 0,
        "owned_ctypes_symbol_count": 9 if spec.owned_ctypes else 0,
    }

    def make(candidate: list[dict[str, Any]]) -> dict[str, Any]:
        mismatches = [
            {"test": original["test"], "baseline": original,
             "candidate": observed}
            for original, observed in zip(baseline, candidate, strict=True)
            if original != observed
        ]
        return {
            "schema": ORIGINAL_SCHEMA + "-actual-original-candidate-result",
            "status": "FAIL" if mismatches else "PASS",
            "python": "3.14.6", "candidate_family": spec.name,
            "controller_source_sha256": pins.original,
            "test_harness_relative": HARNESS_RELATIVE,
            "test_harness_sha256": HARNESS_SHA256,
            "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
            "identity_guard_sha256": IDENTITY_GUARD_SHA256,
            "warning_guard_relative": WARNING_GUARD_RELATIVE,
            "warning_guard_sha256": WARNING_GUARD_SHA256,
            "matrix_sha256": pins.matrix,
            "original_source_sha256": ORIGINAL_TEST_SHA256,
            "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
            "original_warnings_helper_sha256":
            ORIGINAL_WARNINGS_HELPER_SHA256,
            "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
            "all_original_method_count": TOTAL_METHODS,
            "actual_public_method_count": PUBLIC_METHODS,
            "private_waiver_count": PRIVATE_WAIVER_COUNT,
            "private_waivers": list(PRIVATE_METHODS), "public_waivers": [],
            "all_original_methods_executed": False,
            "all_original_methods_qualified": False,
            "baseline_records_sha256": pins.baseline,
            "candidate_records_sha256": digest(candidate),
            "baseline_records": baseline, "candidate_records": candidate,
            "mismatch_count": len(mismatches), "all_mismatches": mismatches,
            "baseline_pid": 1011, "candidate_pid": 1012,
            "native_provenance": copy.deepcopy(owners),
            "matcher_guard": copy.deepcopy(guard),
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

    passed = make(copy.deepcopy(baseline))
    failing_candidate = copy.deepcopy(baseline)
    failing_candidate[3].update({
        "status": "FAIL", "failure_count": 1,
        "failure_tracebacks": [
            "Traceback (most recent call last):\n"
            "  File synthetic, line 3\n"
            "AssertionError: genuine synthetic original failure\n",
        ],
    })
    return matrix, pins, owners, passed, make(failing_candidate)


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a genuine synthetic V4 recorder control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "an independent synthetic forgery control was duplicated")
        try:
            action()
        except (RecorderError, OSError, ValueError, TypeError, KeyError):
            rejected.append(name)
            return
        raise RecorderError("a forged V4 original result was accepted: " + name)

    with source_only_boundary() as effects:
        for family in ("rust", "c", "zig"):
            spec = family_spec(family)
            matrix, pins, owners, passed, failed = synthetic_documents(family)
            require(validate_suite_result(passed, matrix, pins, owners) is passed
                    and validate_suite_result(failed, matrix, pins, owners)
                    is failed,
                    "a complete independent family PASS or FAIL was lost")
            passing_report = build_complete_report(
                label="synthetic-" + family + "-pass",
                stdout=canonical(passed), stderr=b"", returncode=0,
                process_pid=501, matrix=matrix, pins=pins,
                owners_before=owners, owners_after=copy.deepcopy(owners),
            )
            failing_report = build_complete_report(
                label="synthetic-" + family + "-fail",
                stdout=canonical(failed), stderr=b"", returncode=1,
                process_pid=502, matrix=matrix, pins=pins,
                owners_before=owners, owners_after=copy.deepcopy(owners),
            )
            broken_report = build_complete_report(
                label="synthetic-" + family + "-crash",
                stdout=b"synthetic malformed V4 worker stdout\n",
                stderr=b"synthetic complete V4 traceback\n",
                returncode=-11, process_pid=503, matrix=matrix, pins=pins,
                owners_before=owners, owners_after=copy.deepcopy(owners),
            )
            accept("preserve-complete-independent-original-pass-" + family,
                   passing_report["status"] == "PASS"
                   and passing_report["validated_baseline_record_count"]
                   == passing_report["validated_candidate_record_count"]
                   == PUBLIC_METHODS)
            accept("preserve-genuine-exit-one-full-mismatch-" + family,
                   failing_report["status"] == "FAIL"
                   and failing_report["original_process_returncode"] == 1
                   and failing_report["mismatch_count"] == 1
                   and failing_report["all_mismatches"][0]["candidate"]
                   ["failure_tracebacks"]
                   == failed["candidate_records"][3]["failure_tracebacks"])
            accept("preserve-full-malformed-worker-and-signal-" + family,
                   broken_report["status"] == "FAIL"
                   and broken_report["original_process_returncode"] == -11
                   and broken_report["complete_original_suite_result"] is None
                   and broken_report["validated_baseline_record_count"] == 0
                   and broken_report["validated_candidate_record_count"] == 0
                   and broken_report["complete_original_process_stdout"]
                   ["complete"] is True
                   and broken_report["complete_original_process_stderr"]
                   ["complete"] is True)
            accept("do-not-invent-crashed-inner-worker-counts-" + family,
                   broken_report["actual_reference_workers"] is None
                   and broken_report["actual_candidate_workers"] is None
                   and broken_report["mismatch_count"] is None
                   and broken_report["all_mismatches"] is None
                   and broken_report["all_mismatches_preserved"] is False
                   and broken_report["actual_method_guard_checks"] is None
                   and broken_report["actual_warning_registry_guard_checks"]
                   is None
                   and broken_report["actual_localedef_workers"] is None
                   and broken_report[
                       "actual_private_temporary_directories_created"
                   ] is None
                   and broken_report[
                       "actual_private_locale_outputs_created"
                   ] is None
                   and broken_report[
                       "all_private_temporary_directories_removed"
                   ] is None
                   and broken_report[
                       "workspace_files_written_by_original_suite"
                   ] is None)
            accept("require-both-complete-304-original-guards-" + family,
                   passing_report["actual_method_guard_checks"] == GUARD_CHECKS
                   and passing_report["actual_warning_registry_guard_checks"]
                   == GUARD_CHECKS)
            accept("preserve-one-real-reference-and-candidate-" + family,
                   passing_report["actual_reference_workers"] == 1
                   and passing_report["actual_candidate_workers"] == 1
                   and passing_report["baseline_pid"]
                   != passing_report["candidate_pid"])
            accept("authenticate-distinct-owned-native-family-" + family,
                   valid_provenance(owners, spec, pins)
                   and passing_report["candidate_provenance_unchanged"] is True
                   and passing_report["owned_native_ffi_allowed"]
                   is spec.owned_ctypes)
            accept("predeclare-exact-safe-independent-paths-" + family,
                   approved_paths(family, "synthetic-pass") == (
                       APPROVED_DIRECTORY + "/" + family
                       + "-original-v4-synthetic-pass.json",
                       APPROVED_DIRECTORY + "/" + family
                       + "-original-v4-synthetic-pass-publication-receipt.json",
                   ))
            accept("do-not-claim-hidden-speed-or-build-proof-" + family,
                   passing_report["clock_samples"] == 0
                   and passing_report["timing_trials_run"] == 0
                   and passing_report["hidden_cases_read"] == 0
                   and passing_report["performance"] == "NOT MEASURED"
                   and passing_report["source_to_binary_reproducibility"]
                   == "NOT ESTABLISHED"
                   and passing_report["candidate_qualified_for_hidden_benchmark"]
                   is False
                   and passing_report["final_winner_selected"] is False)

            for index, field in enumerate(sorted(RESULT_FIELDS)):
                forged = dict(passed)
                forged.pop(field)
                reject(
                    "reject-missing-" + family + "-result-"
                    + format(index, "02d"),
                    lambda forged=forged: validate_suite_result(
                        forged, matrix, pins, owners,
                    ),
                )
            for index, key, value in (
                (0, "candidate_family", "foreign"),
                (1, "all_original_method_count", 164),
                (2, "actual_public_method_count", 151),
                (3, "private_waiver_count", 12),
                (4, "public_waivers", ["ReTests.test_synthetic_001"]),
                (5, "all_original_methods_executed", True),
                (6, "all_original_methods_qualified", True),
                (7, "matrix_sha256", "ab" * 32),
                (8, "controller_source_sha256", "cd" * 32),
                (9, "baseline_records_sha256", "ef" * 32),
                (10, "actual_candidate_workers", 0),
                (11, "actual_localedef_workers", 3),
                (12, "actual_private_temporary_directories_created", 1),
                (13, "actual_private_locale_outputs_created", 3),
                (14, "all_private_temporary_directories_removed", False),
                (15, "clock_samples", 1),
                (16, "timing_trials_run", 1),
                (17, "benchmark_files_read", 1),
                (18, "hidden_cases_read", 1),
                (19, "performance", "FASTER"),
                (20, "final_winner_selected", True),
                (21, "candidate_qualified_for_hidden_benchmark", True),
                (22, "status", "FAIL"),
                (23, "baseline_pid", passed["candidate_pid"]),
                (24, "original_support_sha256", "01" * 32),
                (25, "original_warnings_helper_sha256", "23" * 32),
                (26, "original_corpus_sha256", "45" * 32),
            ):
                forged = dict(passed)
                forged[key] = value
                reject(
                    "reject-false-" + family + "-observation-"
                    + format(index, "02d"),
                    lambda forged=forged: validate_suite_result(
                        forged, matrix, pins, owners,
                    ),
                )
            for index, key, transform in (
                (0, "baseline_records", lambda rows: rows[:-1]),
                (1, "candidate_records", lambda rows: rows[:-1]),
                (2, "baseline_records", lambda rows: list(reversed(rows))),
                (3, "candidate_records", lambda rows: list(reversed(rows))),
                (4, "all_mismatches", lambda _: []),
                (5, "mismatch_count", lambda _: 0),
                (6, "candidate_records_sha256", lambda _: "ab" * 32),
                (7, "private_waivers", lambda rows: rows[:-1]),
            ):
                template = failed if key in ("all_mismatches", "mismatch_count") \
                    else passed
                forged = dict(template)
                forged[key] = transform(template[key])
                reject(
                    "reject-hidden-" + family + "-vector-"
                    + format(index, "02d"),
                    lambda forged=forged: validate_suite_result(
                        forged, matrix, pins, owners,
                    ),
                )
            for index, key, value in (
                (0, "actual_method_guard_checks", GUARD_CHECKS - 1),
                (1, "original_matchers_blocked", False),
                (2, "adapter_import_quarantined", False),
                (3, "native_sre_blocked", False),
                (4, "builtins_import_guarded", False),
                (5, "importlib_import_guarded", False),
                (6, "actual_object_identity_guarded", False),
                (7, "public_type_names_used_for_ownership", True),
                (8, "warning_registry_introspection_safe", False),
                (9, "warning_registry_exactly_absent", False),
                (10, "actual_warning_registry_guard_checks", GUARD_CHECKS - 1),
                (11, "cross_family_imports_blocked", False),
                (12, "external_regex_imports_blocked", False),
                (13, "owned_native_ffi_allowed", not spec.owned_ctypes),
                (14, "owned_ctypes_load_count", -1),
                (15, "owned_ctypes_symbol_count", -1),
            ):
                forged = dict(passed)
                forged_guard = dict(passed["matcher_guard"])
                forged_guard[key] = value
                forged["matcher_guard"] = forged_guard
                reject(
                    "reject-unguarded-" + family + "-matcher-"
                    + format(index, "02d"),
                    lambda forged=forged: validate_suite_result(
                        forged, matrix, pins, owners,
                    ),
                )
            for index, key, attribute, value in (
                (0, "source", "relative", "candidates/foreign.py"),
                (1, "source", "sha256", "78" * 32),
                (2, "native_engine", "relative", "candidates/foreign.so"),
                (3, "native_engine", "sha256", "01" * 32),
                (4, "native_bridge", "relative", "candidates/foreign-bridge.so"),
                (5, "native_bridge", "sha256", "bc" * 32),
                (6, "source", "inode", 0),
                (7, "native_engine", "device", -1),
                (8, "native_bridge", "bytes", 0),
            ):
                forged_owners = copy.deepcopy(owners)
                forged_owners[key][attribute] = value
                reject(
                    "reject-foreign-" + family + "-native-owner-"
                    + format(index, "02d"),
                    lambda forged_owners=forged_owners: require(
                        valid_provenance(forged_owners, spec, pins),
                        "the forged independent native owner was rejected",
                    ),
                )

        for index, label in enumerate((
            "", ".", "..", "../escape", "/tmp/escape", "UPPER",
            "a space", "has_underscore", "two--hyphens", "-leading",
            "trailing-", "line\nbreak", "slash/component",
            "back\\slash", "\x00", "a" * 65,
        )):
            reject("reject-escaping-evidence-label-" + format(index, "02d"),
                   lambda label=label: validate_label(label))
        for index, invalid in enumerate((
            None, 0, True, "", "0" * 64, "A" * 64, "g" * 64,
            "ab" * 31, "ab" * 33, ORIGINAL_SHA256.upper(),
            ORIGINAL_SHA256 + "0",
        )):
            reject("reject-forged-sha256-" + format(index, "02d"),
                   lambda invalid=invalid: validate_digest(
                       invalid, "synthetic V4 poison",
                   ))
        reject("reject-duplicate-canonical-result-keys",
               lambda: decode_canonical(b'{"status":1,"status":2}\n',
                                       "synthetic duplicate"))
        for name, action in (
            ("block-real-V4-source-read",
             lambda: builtins.open(ORIGINAL_RELATIVE, "rb")),
            ("block-real-candidate-source-read",
             lambda: io.open("candidates/rust_candidate.py", "rb")),
            ("block-real-approved-evidence-read",
             lambda: os.open(approved_paths("rust", "synthetic-pass")[0],
                             os.O_RDONLY)),
            ("block-real-original-evidence-write",
             lambda: os.write(1, b"forbidden")),
            ("block-real-atomic-evidence-link",
             lambda: os.link("synthetic-temp", "synthetic-report")),
            ("block-real-rust-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("block-real-c-candidate-import",
             lambda: importlib.import_module("candidates.vm_candidate")),
            ("block-real-zig-candidate-import",
             lambda: importlib.import_module("candidates.zig_candidate")),
            ("block-real-original-suite-import",
             lambda: importlib.import_module(ORIGINAL_MODULE)),
            ("block-real-original-candidate-worker",
             lambda: subprocess.Popen([str(PINNED_PYTHON)])),
            ("block-real-background-worker",
             lambda: threading.Thread(target=lambda: None).start()),
            ("block-real-original-timing-clock", lambda: time.perf_counter()),
            ("block-real-original-wall-clock", lambda: time.time()),
            ("block-real-original-garbage-collection", lambda: gc.collect()),
        ):
            reject(name, action)
        accept("preserve-all-165-methods-and-13-named-private-waivers",
               len(matrix) == TOTAL_METHODS
               and sum(row["classification"] == "public" for row in matrix)
               == PUBLIC_METHODS
               and sum(row["classification"] == "named-private-waiver"
                       for row in matrix) == PRIVATE_WAIVER_COUNT)
        accept("cover-three-independent-native-families",
               all(any(name.endswith("-" + family) for name in accepted)
                   for family in ("rust", "c", "zig")))
        accept("reject-at-least-200-distinct-original-forgeries",
               len(rejected) >= 200 and len(rejected) == len(set(rejected)))
        accept("prove-ten-real-recorder-side-effects-remain-zero",
               all(effects[key] == 0 for key in (
                   "file_reads", "file_writes", "candidate_imports",
                   "reference_imports", "workers_started", "threads_started",
                   "clock_samples", "gc_collections", "hidden_cases_read",
                   "performance_files_read",
               )))
        accept("prove-seven-real-side-effect-categories-are-blocked",
               all(effects[key] > 0 for key in (
                   "blocked_reads", "blocked_writes", "blocked_imports",
                   "blocked_workers", "blocked_threads", "blocked_clocks",
                   "blocked_gc_collections",
               )))
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "original_suite_relative": ORIGINAL_RELATIVE,
        "original_suite_sha256": ORIGINAL_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "frozen_actual_matrix_sha256": MATRIX_SHA256,
        "frozen_actual_baseline_records_sha256": BASELINE_SHA256,
        "all_original_method_count": TOTAL_METHODS,
        "actual_public_method_count": PUBLIC_METHODS,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "synthetic_families": ["rust", "c", "zig"],
        "synthetic_baseline_pass_count": 151,
        "synthetic_baseline_skip_count": 1,
        "complete_synthetic_baseline_record_count": PUBLIC_METHODS,
        "complete_synthetic_candidate_record_count": PUBLIC_METHODS,
        "synthetic_original_method_guard_checks": GUARD_CHECKS,
        "synthetic_warning_registry_guard_checks": GUARD_CHECKS,
        "synthetic_failures_preserved": 3,
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted, "rejected_controls": rejected,
        "effects": effects,
        "actual_original_suite_invocations": 0,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "actual_clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "files_written": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False, "synthetic": True,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Durably preserve one independent original CPython V4 run",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record", action="store_true")
    parser.add_argument("--candidate", choices=("rust", "c", "zig"))
    parser.add_argument("--label")
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "candidate", "label", "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "a synthetic self-test must not select, pin, or execute a candidate")
        document = source_self_test()
    else:
        spec = family_spec(options.candidate)
        require(type(options.label) is str,
                "actual recording requires one explicit fresh evidence label")
        source = validate_digest(options.oracle_source_sha256,
                                 "frozen independent V4 controller")
        matrix = validate_digest(options.matrix_sha256,
                                 "frozen 165-method original matrix")
        require(source == ORIGINAL_SHA256 and matrix == MATRIX_SHA256,
                "pin the exact already frozen independent V4 source and matrix")
        pins = OwnerPins(
            family=spec.name, original=source, matrix=matrix,
            baseline=BASELINE_SHA256,
            candidate=validate_digest(options.candidate_source_sha256,
                                      "independent native Python adapter"),
            native_engine=validate_digest(options.native_engine_sha256,
                                          "independently owned native engine"),
            native_bridge=validate_digest(options.native_bridge_sha256,
                                          "independently owned native bridge"),
        )
        document = record_original(options.label, pins)
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecorderError as error:
        print("independent original V4 recording failed closed: " + str(error),
              file=sys.stderr)
        raise SystemExit(1) from error
