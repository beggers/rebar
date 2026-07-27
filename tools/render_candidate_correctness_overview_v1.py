#!/usr/bin/env python3
"""Render the hash-pinned, common-denominator native-candidate overview.

Only explicit ``--render`` reads the one fixed input manifest and its named,
frozen correctness reports. It publishes exactly two fixed generated files.
``--self-test`` is entirely synthetic: no files, candidates, workers, clocks,
threads, benchmarks, final holdout, or generated graphics are accessed.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
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
SOURCE_RELATIVE = "tools/render_candidate_correctness_overview_v1.py"
SCHEMA = "rebar-candidate-correctness-overview-v1"
MANIFEST_RELATIVE = "docs/evidence/candidate-correctness-overview-v1.inputs.json"
SVG_RELATIVE = "docs/evidence/candidate-correctness-overview-v1.svg"
SUMMARY_RELATIVE = "docs/evidence/candidate-correctness-overview-v1.json"
EVIDENCE_PARENT = ("experiments", "rust_public_practice_v1")
FAMILY_NAMES = ("rust", "c", "zig")
CATEGORY_NAMES = ("original", "public", "scanner", "buffer")
DENOMINATORS = {"original": 151, "public": 864, "scanner": 1024, "buffer": 768}
TOTAL_CASES = 2807
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_DOCUMENT_BYTES = 192 * 1024 * 1024
MAX_STREAM_BYTES = 64 * 1024 * 1024
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
ORIGINAL_V4_SHA = "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3"
ORIGINAL_V5_SHA = "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
ORIGINAL_MATRIX_SHA = "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
ORIGINAL_BASELINE_SHA = "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
CONTRACT_SHA = "a0ae9621e06b760477a167705cc6e521cc7e9df4d44d126e39c614df89bd3e68"
OWNERSHIP_SHA = "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
PINNED_CTYPES_SHA = "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
PRIVATE_METHODS = (
    "DebugTests.test_debug_flag", "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one", "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable", "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness", "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules", "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc", "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
CATEGORY_META = {
    "public": (864, "tools/rust_public_practice_benchmark_v1.py",
        "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
        "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
        "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
        0x5245_4241_525F_5031, 36, 24),
    "scanner": (1024, "tools/rust_scanner_differential_v1.py",
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
        "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
        "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
        0x5343_414E_4E45_5231, 32, 32),
    "buffer": (768, "tools/rust_memoryview_expand_differential_v1.py",
        "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
        "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
        "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
        0x4D45_5850_414E_4431, 24, 32),
}
ADAPTERS = {"rust": "candidates/rust_candidate.py",
            "c": "candidates/vm_candidate.py", "zig": "candidates/zig_candidate.py"}
NATIVE_COMPONENTS = {
    "rust": ("candidates/_rust_engine.so",
             "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
    "c": ("candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
          "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"),
    "zig": ("candidates/_zig_probe.so",
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"),
}
GUARD_TRUE = (
    "original_matchers_blocked", "adapter_import_quarantined", "native_sre_blocked",
    "builtins_import_guarded", "importlib_import_guarded",
    "actual_object_identity_guarded", "warning_registry_introspection_safe",
    "warning_registry_exactly_absent", "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
ORIGINAL_RECORD_FIELDS = frozenset({"test", "source_ast_sha256", "status", "tests_run",
    "failure_count", "error_count", "skip_count", "failure_tracebacks",
    "error_tracebacks", "skip_reasons"})


class OverviewError(Exception):
    """The frozen input, complete observation, or safe publication was forged."""


class SourceOnlyError(OverviewError):
    """A synthetic control attempted a real side effect."""


def require(value: Any, message: str) -> None:
    if not value:
        raise OverviewError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise OverviewError("require complete canonical overview JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_hash(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64 and len(set(value)) > 1
            and all(char in "0123456789abcdef" for char in value),
            "require an exact independent lowercase SHA-256: " + label)
    return value


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        require(type(name) is str and name not in result,
                "duplicate overview JSON fields cannot conceal results")
        result[name] = value
    return result


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_DOCUMENT_BYTES,
            "require a complete bounded canonical document: " + label)
    try:
        value = json.loads(raw, object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                OverviewError("nonfinite overview evidence is forbidden")))
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise OverviewError("invalid complete overview JSON: " + label) from error
    require(type(value) is dict and canonical(value) == raw,
            "a complete canonical overview document was clipped: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(__file__) == os.path.realpath(
                str(ROOT / SOURCE_RELATIVE))
            and os.path.realpath(sys.executable) == os.path.realpath(PINNED_PYTHON),
            "use only isolated, frozen CPython 3.14.6 and the approved renderer")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a correctness graph must never import or execute a candidate")


def path_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and relative and "\\" not in relative
            and "\x00" not in relative, "require an owned canonical relative path")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative, "a graph path escaped its frozen root")
    return parts


def evidence_pin(value: Any, seen: set[str]) -> tuple[str, str]:
    require(type(value) is dict and set(value) == {"relative", "sha256"},
            "every explicitly named correctness report needs its exact frozen hash")
    relative, source_hash = value["relative"], valid_hash(value["sha256"], "report")
    parts = path_parts(relative)
    require(parts[:-1] == EVIDENCE_PARENT and parts[-1].endswith(".json")
            and "publication-receipt" not in parts[-1]
            and relative not in seen,
            "a correctness report was duplicated, redirected, or silently substituted")
    seen.add(relative)
    return relative, source_hash


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    parts, expected = path_parts(relative), valid_hash(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_DOCUMENT_BYTES,
            "require a bounded exact graph source or correctness document")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directories = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directories)
        opened.append(current)
        for part in parts[:-1]:
            current = os.open(part, directories, dir_fd=current)
            opened.append(current)
        descriptor = os.open(parts[-1], flags, dir_fd=current)
        opened.append(descriptor)
        before, named = os.fstat(descriptor), os.stat(
            parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino) == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum,
                "an approved graph input was replaced, linked, or unbounded")
        remaining, chunks = before.st_size, []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk), "a graph input was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "a graph input has a concealed suffix")
        after, raw = os.fstat(descriptor), b"".join(chunks)
        require((after.st_dev, after.st_ino, after.st_size)
                == (before.st_dev, before.st_ino, before.st_size)
                and hashlib.sha256(raw).hexdigest() == expected,
                "a hash-pinned correctness input changed while being read")
        return raw
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict and set(value) == {"base64", "bytes", "sha256", "complete"}
            and value.get("complete") is True and type(value.get("base64")) is str
            and type(value.get("bytes")) is int and 0 <= value["bytes"] <= MAX_STREAM_BYTES,
            "a complete isolated correctness stream was omitted: " + label)
    expected = valid_hash(value.get("sha256"), label)
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (TypeError, ValueError) as error:
        raise OverviewError("invalid complete correctness stream: " + label) from error
    require(len(raw) == value["bytes"] and hashlib.sha256(raw).hexdigest() == expected
            and base64.b64encode(raw).decode("ascii") == value["base64"],
            "a genuine complete correctness stream was clipped: " + label)
    return raw


def owner(value: Any, relative: str, source_hash: str) -> None:
    require(type(value) is dict and set(value) ==
            {"relative", "sha256", "bytes", "device", "inode"}
            and value.get("relative") == relative and value.get("sha256") == source_hash
            and type(value.get("bytes")) is int and value["bytes"] > 0
            and type(value.get("device")) is int and value["device"] >= 0
            and type(value.get("inode")) is int and value["inode"] > 0,
            "the exact candidate source or owned native provenance was substituted")


def native_identity(value: Any, family: str,
                    source_hash: str | None) -> tuple[tuple[str, str], ...]:
    require(type(value) is dict and set(value) ==
            {"source", "native_engine", "native_bridge"},
            "the exact three-component independently owned engine closure was hidden")
    identities = []
    complete = []
    expected_paths = (ADAPTERS[family], *NATIVE_COMPONENTS[family])
    for role, expected_relative in zip(
            ("source", "native_engine", "native_bridge"), expected_paths,
            strict=True):
        item = value.get(role)
        require(type(item) is dict, "a genuine owned native component was omitted")
        relative = item.get("relative")
        parts = path_parts(relative)
        require(parts[0] == "candidates" and relative == expected_relative,
                "a genuine fixed family-owned native engine or bridge was substituted")
        component_hash = valid_hash(item.get("sha256"), family + " " + role)
        owner(item, relative, component_hash)
        if role == "source":
            require(relative == ADAPTERS[family]
                    and (source_hash is None or component_hash == source_hash),
                    "the current family adapter pin was silently substituted")
        identities.append((relative, component_hash))
        complete.append((relative, component_hash, item["device"], item["inode"]))
    if family == "c":
        require(complete[1] == complete[2],
                "C must authenticate its genuine one-file engine and bridge identity")
    else:
        require(identities[1] != identities[2],
                "independent Rust and Zig engines cannot alias their bridges")
    return tuple(identities)


def verify_guard(value: Any, family: str, count: int, *, original_v5: bool) -> None:
    require(type(value) is dict, "a continuous independent matcher guard was omitted")
    for name in GUARD_TRUE:
        require(value.get(name) is True, "an actual continuous matcher guard failed: " + name)
    require(value.get("public_type_names_used_for_ownership") is False
            and type(value.get("actual_method_guard_checks")) is int
            and value["actual_method_guard_checks"] == 2 * count
            and type(value.get("actual_warning_registry_guard_checks")) is int
            and value["actual_warning_registry_guard_checks"] == 2 * count
            and value.get("owned_native_ffi_allowed") is (family == "zig"),
            "the exact 2N ownership and warning checks were hidden")
    for name in ("cached_original_matcher_descendant_count", "cached_original_holder_count",
                 "owned_ctypes_load_count", "owned_ctypes_symbol_count"):
        require(type(value.get(name)) is int and value[name] >= 0,
                "an exact owned native graph or FFI counter was hidden")
    require((value["owned_ctypes_load_count"] > 0) is (family == "zig")
            and (value["owned_ctypes_symbol_count"] > 0) is (family == "zig"),
            "only Zig may load and call its independently owned native engine")
    if original_v5:
        for name in ("trusted_stdlib_ctypes_preloaded",
                     "trusted_stdlib_ctypes_builtin_verified",
                     "trusted_stdlib_ctypes_pythonapi_initialized"):
            require(value.get(name) is (family == "zig"),
                    "the authenticated pre-guard standard-library FFI was forged")
        require(value.get("trusted_stdlib_ctypes_source_sha256") ==
                (PINNED_CTYPES_SHA if family == "zig" else None),
                "the pinned standard-library FFI source was substituted")


def original_record(value: Any, reference: Mapping[str, Any]) -> None:
    require(type(value) is dict and set(value) == ORIGINAL_RECORD_FIELDS
            and value.get("test") == reference.get("test")
            and value.get("source_ast_sha256") == reference.get("source_ast_sha256")
            and value.get("status") in ("PASS", "FAIL", "SKIP")
            and type(value.get("tests_run")) is int and value["tests_run"] == 1,
            "an original Python method or its complete outcome was omitted")
    for number, vector in (("failure_count", "failure_tracebacks"),
                           ("error_count", "error_tracebacks"),
                           ("skip_count", "skip_reasons")):
        require(type(value.get(vector)) is list
                and all(type(item) is str for item in value[vector])
                and type(value.get(number)) is int
                and value[number] == len(value[vector]),
                "a genuine original test traceback or skip was concealed")
    expected = "FAIL" if value["failure_count"] or value["error_count"] else (
        "SKIP" if value["skip_count"] else "PASS")
    require(value["status"] == expected
            and not (value["skip_count"] and
                     (value["failure_count"] or value["error_count"])),
            "a genuine original failure or debug skip was misclassified")


def validate_original(document: Any, family: str, source_hash: str | None,
                      digestor: Callable[[Any], str]) -> dict[str, int]:
    require(type(document) is dict and document.get("candidate_family") == family,
            "a genuine original-test report was substituted across families")
    schema = document.get("schema")
    versions = {
        "rebar-independent-original-cpython-recorder-v4-complete-first-run-report":
            (4, ORIGINAL_V4_SHA),
        "rebar-independent-original-cpython-recorder-v5-complete-first-run-report":
            (5, ORIGINAL_V5_SHA),
    }
    require(schema in versions, "only frozen V4 or V5 original results may be shown")
    version, controller = versions[schema]
    expected_controller = (document.get("original_suite_sha256") if version == 4
                           else document.get("controller_source_sha256"))
    require(expected_controller == controller and document.get("python") == "3.14.6"
            and document.get("matrix_sha256") == ORIGINAL_MATRIX_SHA
            and document.get("all_original_method_count") == 165
            and document.get("actual_public_method_count") == 152
            and document.get("private_waiver_count") == 13
            and document.get("private_waivers") == list(PRIVATE_METHODS)
            and document.get("public_waivers") == []
            and document.get("validated_baseline_record_count") == 152
            and document.get("validated_candidate_record_count") == 152
            and document.get("actual_reference_workers") == 1
            and document.get("actual_candidate_workers") == 1
            and document.get("actual_method_guard_checks") == 304
            and document.get("actual_warning_registry_guard_checks") == 304
            and document.get("hidden_cases_read") == 0
            and document.get("benchmark_files_read") == 0
            and document.get("performance") == "NOT MEASURED",
            "the exact 165/152/13 original oracle, guards, or hidden boundary changed")
    before, after = document.get("candidate_provenance_before"), document.get(
        "candidate_provenance_after")
    require(type(before) is dict and before == after
            and document.get("candidate_provenance_unchanged") is True,
            "the original candidate changed during its independently guarded run")
    native_identity(before, family, source_hash)
    result = document.get("complete_original_suite_result")
    require(type(result) is dict and result.get("candidate_family") == family
            and result.get("controller_source_sha256") == controller
            and result.get("matrix_sha256") == ORIGINAL_MATRIX_SHA
            and result.get("all_original_method_count") == 165
            and result.get("actual_public_method_count") == 152
            and result.get("private_waiver_count") == 13
            and result.get("private_waivers") == list(PRIVATE_METHODS)
            and result.get("public_waivers") == []
            and result.get("baseline_records_sha256") == ORIGINAL_BASELINE_SHA
            and result.get("native_provenance") == before,
            "a complete frozen original result was hidden")
    baseline, candidate = result.get("baseline_records"), result.get("candidate_records")
    require(type(baseline) is list and type(candidate) is list
            and len(baseline) == len(candidate) == 152
            and digestor(baseline) == ORIGINAL_BASELINE_SHA
            and valid_hash(result.get("candidate_records_sha256"), "original vector")
            and digestor(candidate) == result["candidate_records_sha256"],
            "a genuine 152-case original baseline or candidate vector was replaced")
    mismatch: list[dict[str, Any]] = []
    for expected, observed in zip(baseline, candidate, strict=True):
        original_record(expected, expected)
        original_record(observed, expected)
        if expected != observed:
            mismatch.append({"test": expected["test"], "baseline": expected,
                             "candidate": observed})
    skips = [row for row in baseline if row["status"] == "SKIP"]
    require(len(skips) == 1 and skips[0]["test"] == "ReTests.test_memory_leaks"
            and skips[0]["skip_reasons"] == ["requires debug build"]
            and sum(row["status"] == "PASS" for row in baseline) == 151
            and all(row["status"] != "FAIL" for row in baseline)
            and candidate[baseline.index(skips[0])] == skips[0],
            "the genuine shared debug-build skip was concealed or counted as a pass")
    require(type(result.get("mismatch_count")) is int
            and result["mismatch_count"] == len(mismatch)
            and result.get("all_mismatches") == mismatch
            and document.get("mismatch_count") == len(mismatch)
            and document.get("all_mismatches") == mismatch
            and document.get("all_mismatches_preserved") is True
            and result.get("status") == ("FAIL" if mismatch else "PASS")
            and document.get("status") == result["status"],
            "a genuine original failure was concealed or miscounted")
    verify_guard(result.get("matcher_guard"), family, 152, original_v5=version == 5)
    require(decode_stream(document.get("complete_original_process_stdout"),
                         "original controller stdout") == canonical(result)
            and decode_stream(document.get("complete_original_process_stderr"),
                              "original controller stderr") == b"",
            "a complete original process stream was concealed")
    return {"passed": 151 - len(mismatch), "failed": len(mismatch), "not_run": 0}


def validate_outcome(value: Any, category: str) -> None:
    require(type(value) is dict and value.get("status") in ("return", "raise"),
            "a complete source-ordered category result was hidden")
    output = "value" if value["status"] == "return" else "exception"
    base = {"status", "callbacks", "warnings", output}
    expected = base if category == "public" else (
        base | {"combined_pattern", "lexicon"} if category == "scanner"
        else {"status", "stage", "match_before", "source_after", "mutation",
              "warnings", output})
    require(set(value) == expected and type(value.get("warnings")) is list,
            "a category callback, warning, mutation, or exception was concealed")
    if category != "buffer":
        require(type(value.get("callbacks")) is list, "a callback vector was omitted")
    if category == "buffer":
        require(type(value.get("stage")) is str, "a buffer lifetime stage was omitted")
    if output == "exception":
        require(type(value.get(output)) is dict, "a genuine exception was concealed")


def validate_category(document: Any, family: str, category: str,
                      source_hash: str | None,
                      digestor: Callable[[Any], str]) -> dict[str, int]:
    (count, source, category_sha, matrix_sha, baseline_sha, seed, groups,
     per) = CATEGORY_META[category]
    require(type(document) is dict and document.get("schema") ==
            "rebar-independent-public-contract-v2-recorder-complete-report"
            and document.get("candidate_family") == family
            and document.get("category") == category
            and document.get("controller_sha256") == CONTRACT_SHA
            and document.get("original_v4_sha256") == ORIGINAL_V4_SHA
            and document.get("ownership_audit_sha256") == OWNERSHIP_SHA
            and document.get("category_source_relative") == source
            and document.get("category_source_sha256") == category_sha
            and document.get("published_seed") == seed
            and document.get("matrix_sha256") == matrix_sha
            and document.get("frozen_baseline_sha256") == baseline_sha
            and document.get("case_denominator") == count
            and document.get("group_count") == groups
            and document.get("cases_per_group") == per
            and document.get("observed_baseline_reference_count") == 2
            and document.get("observed_baseline_cases") == count
            and document.get("observed_second_reference_cases") == count
            and document.get("observed_candidate_cases") == count
            and document.get("observed_method_guard_checks") == 2 * count
            and document.get("observed_warning_guard_checks") == 2 * count
            and document.get("actual_controller_process_started") is True
            and document.get("actual_controller_process_count") == 1
            and document.get("actual_controller_process_timed_out") is False
            and document.get("complete_controller_process_failure") is None
            and document.get("unchanged_before_after") is True
            and document.get("hidden_cases_read") == 0
            and document.get("benchmark_files_read") == 0
            and document.get("performance") == "NOT MEASURED",
            "an exact frozen V2 category, denominator, guard, or reference was forged")
    result = document.get("complete_controller_result")
    require(type(result) is dict and result.get("schema") ==
            "rebar-independent-public-contract-v2-actual-category-result"
            and result.get("python") == "3.14.6"
            and result.get("candidate_family") == family
            and result.get("category") == category
            and result.get("controller_source_sha256") == CONTRACT_SHA
            and result.get("category_source_relative") == source
            and result.get("category_source_sha256") == category_sha
            and result.get("original_v4_sha256") == ORIGINAL_V4_SHA
            and result.get("ownership_audit_sha256") == OWNERSHIP_SHA
            and result.get("published_seed") == seed
            and result.get("matrix_sha256") == matrix_sha
            and result.get("case_denominator") == count
            and result.get("group_count") == groups
            and result.get("cases_per_group") == per
            and result.get("baseline_reference_count") == 2
            and result.get("actual_baseline_cases") == count
            and result.get("actual_second_reference_cases") == count
            and result.get("actual_candidate_cases") == count
            and result.get("actual_reference_workers") == 2
            and result.get("actual_candidate_workers") == 1
            and result.get("hidden_cases_read") == 0
            and result.get("benchmark_files_read") == 0
            and result.get("performance") == "NOT MEASURED",
            "a complete independent category source or isolated worker was omitted")
    baseline, second, candidate = (result.get("baseline_records"),
        result.get("second_reference_records"), result.get("candidate_records"))
    require(all(type(rows) is list and len(rows) == count
                for rows in (baseline, second, candidate))
            and baseline == second and result.get("baseline_records_sha256") == baseline_sha
            and result.get("second_reference_records_sha256") == baseline_sha
            and digestor(baseline) == baseline_sha
            and valid_hash(result.get("candidate_records_sha256"), "category vector")
            and digestor(candidate) == result["candidate_records_sha256"],
            "complete agreeing Python references or candidate outcomes were hidden")
    mismatches = []
    for expected, observed in zip(baseline, candidate, strict=True):
        fields = ({"case", "outcome"} if category == "public"
                  else {"case", "family", "outcome"})
        require(type(expected) is dict and type(observed) is dict
                and set(expected) == set(observed) == fields
                and type(expected.get("case")) is str
                and expected["case"] == observed.get("case"),
                "a complete source-ordered category case was omitted")
        if category != "public":
            require(type(expected.get("family")) is str
                    and expected["family"] == observed.get("family"),
                    "a frozen category group was changed")
        validate_outcome(expected["outcome"], category)
        validate_outcome(observed["outcome"], category)
        if expected["outcome"] != observed["outcome"]:
            mismatches.append((expected, observed))
    listed = result.get("all_mismatches")
    require(type(listed) is list and type(result.get("mismatch_count")) is int
            and result["mismatch_count"] == len(mismatches) == len(listed)
            and document.get("observed_mismatch_count") == len(mismatches),
            "a genuine category mismatch was omitted or silently recounted")
    for (expected, observed), mismatch in zip(mismatches, listed, strict=True):
        require(type(mismatch) is dict and mismatch.get("case") == expected["case"]
                and mismatch.get("baseline_outcome") == expected["outcome"]
                and mismatch.get("candidate_outcome") == observed["outcome"],
                "a genuine category mismatch, callback, or exception was substituted")
    expected_status = "FAIL" if mismatches else "PASS"
    require(result.get("status") == expected_status
            and document.get("status") == expected_status
            and document.get("actual_controller_process_returncode") ==
                (1 if mismatches else 0),
            "a genuine category failure was falsely displayed as a pass")
    verify_guard(result.get("matcher_guard"), family, count, original_v5=False)
    native = result.get("native_provenance")
    native_identity(native, family, source_hash)
    artifacts = document.get("complete_artifacts_before")
    require(type(artifacts) is dict and artifacts == document.get("complete_artifacts_after")
            and artifacts.get("family") == family and artifacts.get("category") == category
            and type(artifacts.get("audit_source_closure")) is dict,
            "the independently frozen category source closure changed")
    closure = artifacts["audit_source_closure"]
    for role in ("source", "native_engine", "native_bridge"):
        component = native[role]
        require(closure.get(component["relative"]) == component,
                "the frozen category omitted or swapped an exact owned engine component")
    require(decode_stream(document.get("complete_controller_stdout"),
                         "category controller stdout") == canonical(result)
            and decode_stream(document.get("complete_controller_stderr"),
                              "category controller stderr") == b"",
            "a complete category-controller process stream was hidden")
    return {"passed": count - len(mismatches), "failed": len(mismatches), "not_run": 0}


def manifest_rows(manifest: Any, loader: Callable[[str, str], dict[str, Any]],
                  digestor: Callable[[Any], str] = digest) -> list[dict[str, Any]]:
    require(type(manifest) is dict and set(manifest) ==
            {"schema", "python", "common_case_denominator", "families"}
            and manifest.get("schema") == SCHEMA + "-inputs"
            and manifest.get("python") == "3.14.6"
            and type(manifest.get("common_case_denominator")) is int
            and manifest["common_case_denominator"] == TOTAL_CASES
            and sum(DENOMINATORS.values()) == TOTAL_CASES,
            "the exact common 2,807-case manifest was forged")
    rows, families, used = [], manifest.get("families"), set()
    require(type(families) is list and len(families) == len(FAMILY_NAMES),
            "all three independently owned native families are mandatory")
    for expected_family, item in zip(FAMILY_NAMES, families, strict=True):
        require(type(item) is dict and set(item) ==
                {"family", "candidate_source_sha256", "categories"}
                and item.get("family") == expected_family,
                "a native family was omitted, duplicated, reordered, or substituted")
        family_hash = valid_hash(item.get("candidate_source_sha256"), expected_family)
        categories = item.get("categories")
        require(type(categories) is list and len(categories) == len(CATEGORY_NAMES),
                "all four public correctness categories are mandatory")
        row = {"family": expected_family, "candidate_source_sha256": family_hash,
               "passed": 0, "failed": 0, "not_run": 0, "categories": []}
        selected_native_identity = None
        for expected_category, category in zip(CATEGORY_NAMES, categories, strict=True):
            require(type(category) is dict and set(category) ==
                    {"category", "state", "report", "superseded"}
                    and category.get("category") == expected_category
                    and category.get("state") in ("RUN", "NOT RUN")
                    and type(category.get("superseded")) is list,
                    "a category was omitted, reordered, duplicated, or misclassified")
            previous = []
            for old in category["superseded"]:
                old_path, old_hash = evidence_pin(old, used)
                old_doc = loader(old_path, old_hash)
                (validate_original(old_doc, expected_family, None, digestor)
                 if expected_category == "original" else
                 validate_category(old_doc, expected_family, expected_category,
                                   None, digestor))
                previous.append({"relative": old_path, "sha256": old_hash})
            if category["state"] == "NOT RUN":
                require(category["report"] is None,
                        "an unrun current revision cannot pretend history is a current result")
                counts = {"passed": 0, "failed": 0,
                          "not_run": DENOMINATORS[expected_category]}
                report_pin = None
            else:
                path, source = evidence_pin(category.get("report"), used)
                document = loader(path, source)
                counts = (validate_original(document, expected_family, family_hash, digestor)
                          if expected_category == "original" else
                          validate_category(document, expected_family,
                                            expected_category, family_hash, digestor))
                observed_native = (
                    document["complete_original_suite_result"]["native_provenance"]
                    if expected_category == "original"
                    else document["complete_controller_result"]["native_provenance"])
                observed_identity = native_identity(
                    observed_native, expected_family, family_hash)
                require(selected_native_identity is None
                        or selected_native_identity == observed_identity,
                        "selected categories silently mixed different owned engine revisions")
                selected_native_identity = observed_identity
                report_pin = {"relative": path, "sha256": source}
            require(sum(counts.values()) == DENOMINATORS[expected_category],
                    "a category changed its genuine frozen case denominator")
            for state in ("passed", "failed", "not_run"):
                row[state] += counts[state]
            row["categories"].append({"category": expected_category,
                "denominator": DENOMINATORS[expected_category], **counts,
                "state": category["state"], "report": report_pin,
                "superseded": previous})
        require(sum(row[state] for state in ("passed", "failed", "not_run"))
                == TOTAL_CASES, "a family silently changed the 2,807-case denominator")
        rows.append(row)
    return rows


def escape_xml(value: str) -> str:
    require(type(value) is str, "render only genuine frozen text")
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))


def make_svg(rows: list[dict[str, Any]], source_hash: str,
             manifest_hash: str) -> bytes:
    require(type(rows) is list and len(rows) == 3, "render all three independent families")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="590" '
        'viewBox="0 0 1120 590" role="img" aria-labelledby="overview-title overview-desc">',
        '<title id="overview-title">How well each independently built regex engine '
        'matches Python</title>',
        '<desc id="overview-desc">Each engine is judged against the same 2,807 '
        'frozen Python compatibility checks. Green means passed, red means failed, '
        'and gray means not yet tested. No speed or hidden benchmark is shown.</desc>',
        '<rect width="1120" height="590" rx="18" fill="#f8fafc"/>',
        '<text x="42" y="54" fill="#0f172a" font-family="system-ui,sans-serif" '
        'font-size="27" font-weight="700">Compatibility with Python’s re</text>',
        '<text x="42" y="83" fill="#475569" font-family="system-ui,sans-serif" '
        'font-size="15">Same 2,807 checks for every independently built engine '
        '· no speed claims</text>',
    ]
    colors = (("passed", "#15803d", "Passed"), ("failed", "#dc2626", "Failed"),
              ("not_run", "#94a3b8", "Not yet tested"))
    for index, (state, color, label) in enumerate(colors):
        x = 43 + index * 175
        parts.append(f'<rect x="{x}" y="105" width="14" height="14" rx="3" '
                     f'fill="{color}"/><text x="{x + 22}" y="117" '
                     'fill="#334155" font-family="system-ui,sans-serif" '
                     f'font-size="13">{label}</text>')
    captions = {"original": "Original Python tests", "public": "General behavior",
                "scanner": "Scanner behavior", "buffer": "Buffers and memory"}
    for index, row in enumerate(rows):
        top = 151 + 125 * index
        name = {"rust": "Rust", "c": "C", "zig": "Zig"}[row["family"]]
        parts.append(f'<text x="43" y="{top + 19}" fill="#0f172a" '
                     'font-family="system-ui,sans-serif" font-size="19" '
                     f'font-weight="700">{name}</text>')
        parts.append(f'<text x="1040" y="{top + 19}" fill="#334155" '
                     'text-anchor="end" font-family="system-ui,sans-serif" '
                     f'font-size="14">{row["passed"]:,} / {TOTAL_CASES:,} passed</text>')
        parts.append(f'<rect x="43" y="{top + 30}" width="996" height="24" '
                     'rx="6" fill="#e2e8f0"/>')
        cumulative = 0
        for state, color, label in colors:
            start = 43 + (cumulative * 996 // TOTAL_CASES)
            cumulative += row[state]
            end = 43 + (cumulative * 996 // TOTAL_CASES)
            if end > start:
                parts.append(f'<rect x="{start}" y="{top + 30}" '
                    f'width="{end - start}" height="24" fill="{color}">'
                    f'<title>{name}: {row[state]:,} {label.lower()} '
                    f'out of {TOTAL_CASES:,}</title></rect>')
        for offset, category in enumerate(row["categories"]):
            x = 43 + 250 * offset
            label = captions[category["category"]]
            status = ("NOT YET TESTED" if category["not_run"] else
                      f'{category["passed"]:,}/{category["denominator"]:,} passed')
            color = "#64748b" if category["not_run"] else (
                "#dc2626" if category["failed"] else "#15803d")
            parts.append(f'<text x="{x}" y="{top + 77}" fill="#475569" '
                f'font-family="system-ui,sans-serif" font-size="12">{label}</text>')
            parts.append(f'<text x="{x}" y="{top + 96}" fill="{color}" '
                f'font-family="system-ui,sans-serif" font-size="13" '
                f'font-weight="600">{status}</text>')
    footer = ("Frozen original: 151 runnable + one genuine debug-only skip; "
              "13 named private tests are excluded equally.")
    parts.extend([
        f'<text x="43" y="548" fill="#475569" font-family="system-ui,sans-serif" '
        f'font-size="12">{escape_xml(footer)}</text>',
        f'<text x="43" y="570" fill="#64748b" font-family="system-ui,sans-serif" '
        f'font-size="11">Manifest SHA-256: {manifest_hash} · '
        f'renderer SHA-256: {source_hash}</text>',
        "</svg>\n",
    ])
    return "\n".join(parts).encode("utf-8")


def build_documents(manifest: Mapping[str, Any], source_hash: str,
                    manifest_hash: str, loader: Callable[[str, str], dict[str, Any]],
                    digestor: Callable[[Any], str] = digest) -> tuple[bytes, bytes]:
    valid_hash(source_hash, "renderer")
    valid_hash(manifest_hash, "manifest")
    rows = manifest_rows(manifest, loader, digestor)
    svg = make_svg(rows, source_hash, manifest_hash)
    summary = {"schema": SCHEMA + "-summary", "python": "3.14.6",
        "source_relative": SOURCE_RELATIVE, "source_sha256": source_hash,
        "manifest_relative": MANIFEST_RELATIVE, "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE, "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "common_case_denominator": TOTAL_CASES, "families": rows,
        "hidden_cases_read": 0, "performance_files_read": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "final_holdout_opened": False, "winner_selected": False}
    return svg, canonical(summary)


def directory_identity(descriptor: int, expected: tuple[int, int]) -> None:
    actual = os.fstat(descriptor)
    require(stat.S_ISDIR(actual.st_mode)
            and (actual.st_dev, actual.st_ino) == expected,
            "the exact owned output directory was renamed or substituted")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), flags)
        opened.append(current)
        for part in ("docs", "evidence"):
            current = os.open(part, flags, dir_fd=current)
            opened.append(current)
        named = os.fstat(current)
        require((named.st_dev, named.st_ino) == expected,
                "the literal graph directory no longer names its retained inode")
    finally:
        for item in reversed(opened):
            os.close(item)


def read_existing_output(directory: int, basename: str,
                         maximum: int = MAX_SOURCE_BYTES) -> bytes | None:
    require(basename in (path_parts(SVG_RELATIVE)[-1],
                         path_parts(SUMMARY_RELATIVE)[-1]),
            "only the two exact generated graph files may be inspected")
    require(type(maximum) is int and 0 < maximum <= MAX_DOCUMENT_BYTES,
            "require a bounded existing generated graph")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(basename, flags, dir_fd=directory)
    except FileNotFoundError:
        return None
    try:
        info = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(info.st_mode)
                and stat.S_ISREG(named.st_mode)
                and (info.st_dev, info.st_ino) == (named.st_dev, named.st_ino)
                and 0 < info.st_size <= maximum,
                "refusing a symlink, replaced, unbounded, or nonregular generated graph")
        remaining, chunks = info.st_size, []
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part), "an existing graph was truncated")
            chunks.append(part)
            remaining -= len(part)
        after = os.fstat(descriptor)
        require(os.read(descriptor, 1) == b""
                and (after.st_dev, after.st_ino, after.st_size)
                    == (info.st_dev, info.st_ino, info.st_size),
                "an existing generated graph changed during its complete read")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def existing_output(directory: int, basename: str, expected: bytes) -> bool:
    actual = read_existing_output(directory, basename)
    if actual is None:
        return False
    require(actual == expected,
            "refusing to overwrite different generated graph bytes without explicit replacement")
    return True


def validate_previous_outputs(old_svg: Any, old_summary: Any) -> dict[str, Any]:
    require(type(old_svg) is bytes and type(old_summary) is bytes,
            "replacement requires both complete previously generated graph files")
    previous = decode_document(old_summary, "previous generated graph summary")
    require(set(previous) == {
        "schema", "python", "source_relative", "source_sha256", "manifest_relative",
        "manifest_sha256", "svg_relative", "svg_sha256", "common_case_denominator",
        "families", "hidden_cases_read", "performance_files_read", "timing_trials_run",
        "performance", "final_holdout_opened", "winner_selected"}
        and previous.get("schema") == SCHEMA + "-summary"
        and previous.get("python") == "3.14.6"
        and previous.get("source_relative") == SOURCE_RELATIVE
        and previous.get("manifest_relative") == MANIFEST_RELATIVE
        and previous.get("svg_relative") == SVG_RELATIVE
        and previous.get("common_case_denominator") == TOTAL_CASES
        and previous.get("hidden_cases_read") == 0
        and previous.get("performance_files_read") == 0
        and previous.get("timing_trials_run") == 0
        and previous.get("performance") == "NOT MEASURED"
        and previous.get("final_holdout_opened") is False
        and previous.get("winner_selected") is False,
        "replacement is limited to an authentic prior correctness-only generated summary")
    valid_hash(previous.get("source_sha256"), "previous renderer")
    valid_hash(previous.get("manifest_sha256"), "previous manifest")
    require(valid_hash(previous.get("svg_sha256"), "previous graph")
            == hashlib.sha256(old_svg).hexdigest(),
            "the previous generated summary does not authenticate the existing graph")
    rows, seen = previous.get("families"), set()
    require(type(rows) is list and len(rows) == len(FAMILY_NAMES),
            "the previous generated graph must account for all three families")
    for expected_family, row in zip(FAMILY_NAMES, rows, strict=True):
        require(type(row) is dict and set(row) == {
            "family", "candidate_source_sha256", "passed", "failed", "not_run", "categories"}
            and row.get("family") == expected_family,
            "a previous graph family was foreign, omitted, or reordered")
        valid_hash(row.get("candidate_source_sha256"), "previous candidate source")
        categories = row.get("categories")
        require(type(categories) is list and len(categories) == len(CATEGORY_NAMES),
                "a previous graph concealed an entire correctness category")
        actual = {key: 0 for key in ("passed", "failed", "not_run")}
        for expected_category, item in zip(CATEGORY_NAMES, categories, strict=True):
            require(type(item) is dict and set(item) == {
                "category", "denominator", "passed", "failed", "not_run", "state",
                "report", "superseded"}
                and item.get("category") == expected_category
                and item.get("denominator") == DENOMINATORS[expected_category]
                and item.get("state") in ("RUN", "NOT RUN")
                and type(item.get("superseded")) is list,
                "a previous graph category or exact frozen denominator was foreign")
            for key in actual:
                require(type(item.get(key)) is int and item[key] >= 0,
                        "a previous graph concealed negative or nonintegral outcomes")
                actual[key] += item[key]
            require(sum(item[key] for key in actual)
                    == DENOMINATORS[expected_category],
                    "a previous graph changed a shared category denominator")
            if item["state"] == "NOT RUN":
                require(item["report"] is None
                        and item["not_run"] == DENOMINATORS[expected_category]
                        and item["passed"] == item["failed"] == 0,
                        "a previous graph counted historical results as current work")
            else:
                evidence_pin(item.get("report"), seen)
                require(item["not_run"] == 0,
                        "a completed previous category concealed untested work")
            for old in item["superseded"]:
                evidence_pin(old, seen)
        require(all(type(row.get(key)) is int and row[key] == actual[key]
                    for key in actual) and sum(actual.values()) == TOTAL_CASES,
                "a previous graph changed its shared 2,807-case denominator")
    return previous


def approve_publication(old_svg: bytes | None, old_summary: bytes | None,
                        new_svg: bytes, new_summary: bytes,
                        replace_generated: bool) -> None:
    require(type(replace_generated) is bool,
            "generated-graph replacement requires an explicit Boolean choice")
    if not replace_generated:
        require((old_svg is None or old_svg == new_svg)
                and (old_summary is None or old_summary == new_summary),
                "different existing graphs require explicit --replace-generated")
        return
    validate_previous_outputs(old_svg, old_summary)


def atomic_output(directory: int, identity: tuple[int, int],
                  basename: str, value: bytes, previous: bytes | None = None,
                  replace_generated: bool = False) -> None:
    directory_identity(directory, identity)
    observed = read_existing_output(directory, basename)
    if observed == value:
        directory_identity(directory, identity)
        return
    if replace_generated:
        require(type(previous) is bytes and observed == previous,
                "refusing to replace a generated graph that changed after verification")
    else:
        require(observed is None,
                "refusing to overwrite a different generated graph")
    temporary = (".rebar-correctness-v1-" + basename + "-" + str(os.getpid())
                 + "-" + hashlib.sha256(value).hexdigest()[:20])
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    owned: tuple[int, int] | None = None
    linked = False
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode), "graph temporary is not regular")
        owned = (initial.st_dev, initial.st_ino)
        position = 0
        while position < len(value):
            written = os.write(descriptor, value[position:])
            require(type(written) is int and written > 0, "generated graph was truncated")
            position += written
        os.fsync(descriptor)
        directory_identity(directory, identity)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == owned,
                "the owned graph temporary was substituted")
        if replace_generated:
            require(read_existing_output(directory, basename) == previous,
                    "the authenticated previous graph was changed before replacement")
            os.replace(temporary, basename, src_dir_fd=directory,
                       dst_dir_fd=directory)
        else:
            os.link(temporary, basename, src_dir_fd=directory,
                    dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.fsync(directory)
        require(existing_output(directory, basename, value),
                "the complete generated chart failed its readback")
        if not replace_generated:
            named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
            require((named.st_dev, named.st_ino) == owned,
                    "refusing to remove an unowned graph temporary")
            os.unlink(temporary, dir_fd=directory)
            os.fsync(directory)
        directory_identity(directory, identity)
    except BaseException:
        if not linked and owned is not None:
            try:
                named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
                if (named.st_dev, named.st_ino) == owned:
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, OverviewError):
                pass
        raise
    finally:
        os.close(descriptor)


def render(source_hash: str, manifest_relative: str,
           manifest_hash: str, replace_generated: bool = False) -> dict[str, Any]:
    verify_runtime()
    source_hash, manifest_hash = valid_hash(source_hash, "renderer"), valid_hash(
        manifest_hash, "manifest")
    require(manifest_relative == MANIFEST_RELATIVE,
            "only the one explicitly frozen overview manifest is approved")
    read_frozen(SOURCE_RELATIVE, source_hash, MAX_SOURCE_BYTES)
    manifest = decode_document(read_frozen(MANIFEST_RELATIVE, manifest_hash,
                                          MAX_SOURCE_BYTES), "frozen overview manifest")

    def load_report(relative: str, expected: str) -> dict[str, Any]:
        return decode_document(read_frozen(relative, expected, MAX_DOCUMENT_BYTES), relative)

    svg, summary = build_documents(manifest, source_hash, manifest_hash, load_report)
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), flags)
        opened.append(current)
        for part in ("docs", "evidence"):
            current = os.open(part, flags, dir_fd=current)
            opened.append(current)
        info, identity = os.fstat(current), None
        require(stat.S_ISDIR(info.st_mode), "the chart parent is not an owned directory")
        identity = (info.st_dev, info.st_ino)
        directory_identity(current, identity)
        svg_name, summary_name = path_parts(SVG_RELATIVE)[-1], path_parts(
            SUMMARY_RELATIVE)[-1]
        require(path_parts(SVG_RELATIVE)[:-1] == ("docs", "evidence")
                and path_parts(SUMMARY_RELATIVE)[:-1] == ("docs", "evidence"),
                "generated chart escaped its two exact fixed paths")
        old_svg, old_summary = read_existing_output(current, svg_name), \
            read_existing_output(current, summary_name)
        approve_publication(old_svg, old_summary, svg, summary, replace_generated)
        for basename, raw, previous in ((svg_name, svg, old_svg),
                                         (summary_name, summary, old_summary)):
            atomic_output(current, identity, basename, raw, previous,
                          replace_generated)
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)
    verify_runtime()
    return {"schema": SCHEMA + "-rendered", "status": "PASS",
            "source_sha256": source_hash, "manifest_sha256": manifest_hash,
            "svg_relative": SVG_RELATIVE, "svg_sha256": hashlib.sha256(svg).hexdigest(),
            "summary_relative": SUMMARY_RELATIVE,
            "summary_sha256": hashlib.sha256(summary).hexdigest(),
            "common_case_denominator": TOTAL_CASES, "families": list(FAMILY_NAMES),
            "actual_candidate_workers": 0, "hidden_cases_read": 0,
            "performance_files_read": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "final_holdout_opened": False,
            "winner_selected": False}


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {key: 0 for key in ("reads", "writes", "imports", "workers",
                                 "threads", "clocks", "garbage_collection")}
    installed: list[tuple[Any, str, Any]] = []

    def deny(key: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[key] += 1
            raise SourceOnlyError("synthetic correctness controls cannot " + key)
        return blocked

    def install(module: Any, name: str, replacement: Any) -> None:
        actual = getattr(module, name, None)
        if actual is not None:
            installed.append((module, name, actual))
            setattr(module, name, replacement)

    try:
        for module, name in ((builtins, "open"), (io, "open"), (os, "open"),
                             (os, "read"), (os, "stat"), (os, "lstat"),
                             (Path, "open"), (Path, "read_bytes"), (Path, "read_text")):
            install(module, name, deny("reads"))
        for module, name in ((os, "write"), (os, "unlink"), (os, "remove"),
                             (os, "rename"), (os, "replace"), (os, "mkdir"),
                             (os, "rmdir"), (os, "fsync"), (os, "link"),
                             (Path, "write_bytes"), (Path, "write_text"),
                             (Path, "unlink"), (Path, "mkdir")):
            install(module, name, deny("writes"))
        install(builtins, "__import__", deny("imports"))
        install(importlib, "import_module", deny("imports"))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny("workers"))
        install(threading.Thread, "start", deny("threads"))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time", "process_time_ns"):
            install(time, name, deny("clocks"))
        install(gc, "collect", deny("garbage_collection"))
        yield effects
    finally:
        for module, name, original in reversed(installed):
            setattr(module, name, original)


def self_test() -> dict[str, Any]:
    """Exercise synthetic complete evidence without reading or writing a file."""
    verify_runtime()
    controls: list[str] = []
    with source_only_boundary() as effects:
        aliases: dict[bytes, str] = {}

        def synthetic_digest(value: Any) -> str:
            raw = canonical(value)
            return aliases.get(raw, hashlib.sha256(raw).hexdigest())

        def stream(raw: bytes) -> dict[str, Any]:
            return {"base64": base64.b64encode(raw).decode("ascii"),
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "complete": True}

        def artifact(relative: str, salt: str, inode: int) -> dict[str, Any]:
            return {"relative": relative,
                    "sha256": hashlib.sha256(salt.encode("ascii")).hexdigest(),
                    "bytes": len(salt), "device": 71, "inode": inode}

        def provenance(family: str, revision: str = "current") -> dict[str, Any]:
            source = artifact(ADAPTERS[family], family + ":source:" + revision,
                              1000 + FAMILY_NAMES.index(family))
            engine = artifact(NATIVE_COMPONENTS[family][0],
                              family + ":engine:" + revision,
                              2000 + FAMILY_NAMES.index(family))
            bridge = (copy.deepcopy(engine) if family == "c" else
                      artifact(NATIVE_COMPONENTS[family][1],
                               family + ":bridge:" + revision,
                               3000 + FAMILY_NAMES.index(family)))
            return {"source": source, "native_engine": engine,
                    "native_bridge": bridge}

        def guard(family: str, count: int, version: int) -> dict[str, Any]:
            value = {name: True for name in GUARD_TRUE}
            value.update({"public_type_names_used_for_ownership": False,
                "actual_method_guard_checks": 2 * count,
                "actual_warning_registry_guard_checks": 2 * count,
                "owned_native_ffi_allowed": family == "zig",
                "cached_original_matcher_descendant_count": 1,
                "cached_original_holder_count": 1,
                "owned_ctypes_load_count": 1 if family == "zig" else 0,
                "owned_ctypes_symbol_count": 9 if family == "zig" else 0})
            if version == 5:
                value.update({"trusted_stdlib_ctypes_preloaded": family == "zig",
                    "trusted_stdlib_ctypes_builtin_verified": family == "zig",
                    "trusted_stdlib_ctypes_pythonapi_initialized": family == "zig",
                    "trusted_stdlib_ctypes_source_sha256":
                        PINNED_CTYPES_SHA if family == "zig" else None})
            return value

        original_baseline = []
        for index in range(152):
            name = ("ReTests.test_memory_leaks" if index == 151 else
                    f"ReTests.test_synthetic_{index:03d}")
            skipped = index == 151
            original_baseline.append({"test": name,
                "source_ast_sha256": hashlib.sha256(name.encode("ascii")).hexdigest(),
                "status": "SKIP" if skipped else "PASS", "tests_run": 1,
                "failure_count": 0, "error_count": 0,
                "skip_count": 1 if skipped else 0,
                "failure_tracebacks": [], "error_tracebacks": [],
                "skip_reasons": ["requires debug build"] if skipped else []})
        aliases[canonical(original_baseline)] = ORIGINAL_BASELINE_SHA

        def original(family: str, version: int, failures: int = 0,
                     revision: str = "current") -> dict[str, Any]:
            native = provenance(family, revision)
            candidate = copy.deepcopy(original_baseline)
            for row in candidate[:failures]:
                row.update({"status": "FAIL", "failure_count": 1,
                            "failure_tracebacks": ["synthetic complete mismatch"]})
            mismatches = [{"test": expected["test"], "baseline": expected,
                           "candidate": actual}
                          for expected, actual in zip(original_baseline, candidate,
                                                      strict=True) if expected != actual]
            controller = ORIGINAL_V4_SHA if version == 4 else ORIGINAL_V5_SHA
            status = "FAIL" if mismatches else "PASS"
            result = {"schema": f"synthetic-original-v{version}-result",
                "status": status, "python": "3.14.6", "candidate_family": family,
                "controller_source_sha256": controller,
                "matrix_sha256": ORIGINAL_MATRIX_SHA,
                "all_original_method_count": 165, "actual_public_method_count": 152,
                "private_waiver_count": 13, "private_waivers": list(PRIVATE_METHODS),
                "public_waivers": [], "baseline_records": original_baseline,
                "baseline_records_sha256": ORIGINAL_BASELINE_SHA,
                "candidate_records": candidate,
                "candidate_records_sha256": synthetic_digest(candidate),
                "mismatch_count": len(mismatches), "all_mismatches": mismatches,
                "native_provenance": native,
                "matcher_guard": guard(family, 152, version)}
            document = {"schema":
                f"rebar-independent-original-cpython-recorder-v{version}-complete-first-run-report",
                "status": status, "python": "3.14.6", "candidate_family": family,
                "original_suite_sha256": controller,
                "controller_source_sha256": controller,
                "matrix_sha256": ORIGINAL_MATRIX_SHA,
                "all_original_method_count": 165, "actual_public_method_count": 152,
                "private_waiver_count": 13, "private_waivers": list(PRIVATE_METHODS),
                "public_waivers": [], "validated_baseline_record_count": 152,
                "validated_candidate_record_count": 152,
                "actual_reference_workers": 1, "actual_candidate_workers": 1,
                "actual_method_guard_checks": 304,
                "actual_warning_registry_guard_checks": 304,
                "hidden_cases_read": 0, "benchmark_files_read": 0,
                "performance": "NOT MEASURED",
                "candidate_provenance_before": native,
                "candidate_provenance_after": copy.deepcopy(native),
                "candidate_provenance_unchanged": True,
                "complete_original_suite_result": result,
                "complete_original_process_stdout": stream(canonical(result)),
                "complete_original_process_stderr": stream(b""),
                "mismatch_count": len(mismatches), "all_mismatches": mismatches,
                "all_mismatches_preserved": True}
            return document

        def category_report(family: str, category: str,
                            failures: int = 0,
                            revision: str = "current") -> dict[str, Any]:
            count, source, category_sha, matrix_sha, baseline_sha, seed, groups, per = \
                CATEGORY_META[category]
            native = provenance(family, revision)
            baseline = []
            for index in range(count):
                outcome = {"status": "return", "value": index, "warnings": []}
                if category == "buffer":
                    outcome.update({"stage": "complete", "match_before": None,
                                    "source_after": None, "mutation": None})
                else:
                    outcome["callbacks"] = []
                    if category == "scanner":
                        outcome.update({"combined_pattern": None, "lexicon": None})
                row = {"case": f"{category}.{index:04d}", "outcome": outcome}
                if category != "public":
                    row["family"] = f"synthetic-{index // per:03d}"
                baseline.append(row)
            aliases[canonical(baseline)] = baseline_sha
            candidate = copy.deepcopy(baseline)
            for index in range(failures):
                candidate[index]["outcome"]["value"] = -index - 1
            mismatches = [{"case": expected["case"],
                           "baseline_outcome": expected["outcome"],
                           "candidate_outcome": actual["outcome"]}
                          for expected, actual in zip(baseline, candidate, strict=True)
                          if expected["outcome"] != actual["outcome"]]
            status = "FAIL" if mismatches else "PASS"
            common = {"python": "3.14.6", "candidate_family": family,
                "category": category, "category_source_relative": source,
                "category_source_sha256": category_sha,
                "original_v4_sha256": ORIGINAL_V4_SHA,
                "ownership_audit_sha256": OWNERSHIP_SHA,
                "published_seed": seed, "matrix_sha256": matrix_sha,
                "case_denominator": count, "group_count": groups,
                "cases_per_group": per, "hidden_cases_read": 0,
                "benchmark_files_read": 0, "performance": "NOT MEASURED"}
            result = {**common,
                "schema": "rebar-independent-public-contract-v2-actual-category-result",
                "status": status, "controller_source_sha256": CONTRACT_SHA,
                "baseline_reference_count": 2, "actual_baseline_cases": count,
                "actual_second_reference_cases": count,
                "actual_candidate_cases": count, "actual_reference_workers": 2,
                "actual_candidate_workers": 1, "baseline_records": baseline,
                "second_reference_records": copy.deepcopy(baseline),
                "candidate_records": candidate,
                "baseline_records_sha256": baseline_sha,
                "second_reference_records_sha256": baseline_sha,
                "candidate_records_sha256": synthetic_digest(candidate),
                "mismatch_count": len(mismatches), "all_mismatches": mismatches,
                "matcher_guard": guard(family, count, 2),
                "native_provenance": native}
            closure = {part["relative"]: copy.deepcopy(part)
                       for part in native.values()}
            artifacts = {"family": family, "category": category,
                         "audit_source_closure": closure}
            return {**common,
                "schema": "rebar-independent-public-contract-v2-recorder-complete-report",
                "status": status, "controller_sha256": CONTRACT_SHA,
                "frozen_baseline_sha256": baseline_sha,
                "observed_baseline_reference_count": 2,
                "observed_baseline_cases": count,
                "observed_second_reference_cases": count,
                "observed_candidate_cases": count,
                "observed_method_guard_checks": 2 * count,
                "observed_warning_guard_checks": 2 * count,
                "actual_controller_process_started": True,
                "actual_controller_process_count": 1,
                "actual_controller_process_timed_out": False,
                "actual_controller_process_returncode": 1 if mismatches else 0,
                "complete_controller_process_failure": None,
                "unchanged_before_after": True,
                "observed_mismatch_count": len(mismatches),
                "complete_controller_result": result,
                "complete_controller_stdout": stream(canonical(result)),
                "complete_controller_stderr": stream(b""),
                "complete_artifacts_before": artifacts,
                "complete_artifacts_after": copy.deepcopy(artifacts)}

        documents: dict[str, bytes] = {}

        def pin(family: str, category: str, document: dict[str, Any],
                suffix: str = "current") -> dict[str, str]:
            relative = ("experiments/rust_public_practice_v1/" + family + "-"
                        + category + "-" + suffix + "-synthetic.json")
            raw = canonical(document)
            documents[relative] = raw
            return {"relative": relative,
                    "sha256": hashlib.sha256(raw).hexdigest()}

        configurations = {"rust": {"original": (4, 0), "public": 0,
                                   "scanner": 0},
                          "c": {"original": (5, 1), "public": 40,
                                "scanner": 992, "buffer": 21},
                          "zig": {"original": (5, 0)}}
        families = []
        for family in FAMILY_NAMES:
            current = provenance(family)
            categories = []
            for category in CATEGORY_NAMES:
                if category not in configurations[family]:
                    categories.append({"category": category, "state": "NOT RUN",
                                       "report": None, "superseded": []})
                    continue
                setting = configurations[family][category]
                report = (original(family, *setting) if category == "original"
                          else category_report(family, category, setting))
                superseded = []
                if family == "zig" and category == "original":
                    superseded.append(pin(family, category,
                        original(family, 5, 1, "historical"), "superseded"))
                categories.append({"category": category, "state": "RUN",
                    "report": pin(family, category, report),
                    "superseded": superseded})
            families.append({"family": family,
                "candidate_source_sha256": current["source"]["sha256"],
                "categories": categories})
        manifest = {"schema": SCHEMA + "-inputs", "python": "3.14.6",
                    "common_case_denominator": TOTAL_CASES, "families": families}

        def loader(relative: str, expected: str) -> dict[str, Any]:
            require(relative in documents, "synthetic evidence cannot discover files")
            raw = documents[relative]
            require(hashlib.sha256(raw).hexdigest() == expected,
                    "synthetic report pin was substituted")
            return decode_document(raw, relative)

        def accept(name: str, value: Any) -> None:
            require(bool(value), "synthetic positive control failed: " + name)
            controls.append("PASS " + name)

        def reject(name: str, operation: Callable[[], Any]) -> None:
            try:
                operation()
            except (OverviewError, OSError, TypeError, ValueError, KeyError):
                controls.append("PASS reject " + name)
                return
            raise OverviewError("synthetic poison control was accepted: " + name)

        rows = manifest_rows(manifest, loader, synthetic_digest)
        source_hash = hashlib.sha256(b"synthetic approved renderer").hexdigest()
        manifest_hash = hashlib.sha256(canonical(manifest)).hexdigest()
        svg, summary = build_documents(manifest, source_hash, manifest_hash,
                                       loader, synthetic_digest)
        decoded_summary = decode_document(summary, "synthetic generated summary")
        accept("exact three independently owned engine families",
               [row["family"] for row in rows] == list(FAMILY_NAMES))
        for row in rows:
            accept(row["family"] + " exact 2807-case shared denominator",
                   sum(row[key] for key in ("passed", "failed", "not_run")) == 2807)
            for item in row["categories"]:
                accept(row["family"] + " " + item["category"] + " honest denominator",
                       sum(item[key] for key in ("passed", "failed", "not_run"))
                       == DENOMINATORS[item["category"]])
        accept("Rust complete and missing results are never mixed",
               (rows[0]["passed"], rows[0]["failed"], rows[0]["not_run"])
               == (2039, 0, 768))
        accept("C reports preserve every actual mismatch",
               (rows[1]["passed"], rows[1]["failed"], rows[1]["not_run"])
               == (1753, 1054, 0))
        accept("Zig untested categories remain visible",
               (rows[2]["passed"], rows[2]["failed"], rows[2]["not_run"])
               == (151, 0, 2656))
        accept("historical failure is preserved without inflating current results",
               len(rows[2]["categories"][0]["superseded"]) == 1
               and rows[2]["categories"][0]["failed"] == 0)
        accept("graph is byte-for-byte deterministic",
               (svg, summary) == build_documents(manifest, source_hash, manifest_hash,
                                                  loader, synthetic_digest))
        accept("green red and gray remain separately labeled",
               all(token in svg for token in (b"#15803d", b"#dc2626", b"#94a3b8",
                                              b"Passed", b"Failed", b"Not yet tested")))
        accept("original debug skip is never counted in 151 runnable methods",
               rows[0]["categories"][0]["denominator"] == 151
               and b"genuine debug-only skip" in svg)
        accept("summary authenticates complete generated graph",
               decoded_summary["svg_sha256"] == hashlib.sha256(svg).hexdigest())
        accept("no speed measurement is invented",
               decoded_summary["performance"] == "NOT MEASURED"
               and decoded_summary["timing_trials_run"] == 0)
        accept("no holdout is opened and no winner is chosen",
               decoded_summary["final_holdout_opened"] is False
               and decoded_summary["winner_selected"] is False)
        accept("first publication is safe without replacement",
               approve_publication(None, None, svg, summary, False) is None)
        accept("identical generated files are safe and idempotent",
               approve_publication(svg, summary, svg, summary, False) is None)
        accept("verified graph refresh is explicitly permitted",
               approve_publication(svg, summary, svg + b"<!--refresh-->",
                                   summary, True) is None)
        historical_c_manifest = copy.deepcopy(manifest)
        for offset, category in enumerate(("public", "scanner", "buffer"), 1):
            failures = configurations["c"][category]
            historical = pin("c", category,
                category_report("c", category, failures, "historical"), "historical")
            historical_c_manifest["families"][1]["categories"][offset].update(
                {"state": "NOT RUN", "report": None, "superseded": [historical]})
        historical_c_rows = manifest_rows(historical_c_manifest, loader,
                                           synthetic_digest)
        accept("old C category results cannot enter the current C score",
               (historical_c_rows[1]["passed"], historical_c_rows[1]["failed"],
                historical_c_rows[1]["not_run"]) == (150, 1, 2656))
        accept("all three superseded C failure reports remain visible",
               all(len(item["superseded"]) == 1 and item["not_run"]
                       == item["denominator"]
                   for item in historical_c_rows[1]["categories"][1:]))

        def bad_manifest(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
            changed = copy.deepcopy(manifest)
            mutate(changed)
            reject(name, lambda: manifest_rows(changed, loader, synthetic_digest))

        bad_manifest("wrong manifest schema", lambda value: value.update(
            {"schema": SCHEMA + "-foreign"}))
        bad_manifest("wrong pinned Python", lambda value: value.update(
            {"python": "3.13.0"}))
        bad_manifest("silently smaller denominator", lambda value: value.update(
            {"common_case_denominator": 2806}))
        bad_manifest("extra manifest field", lambda value: value.update({"extra": True}))
        bad_manifest("missing independent family", lambda value: value["families"].pop())
        bad_manifest("cross-family substitution", lambda value: value["families"].reverse())
        bad_manifest("duplicated family", lambda value: value["families"][1].update(
            {"family": "rust"}))
        bad_manifest("missing category", lambda value: value["families"][0][
            "categories"].pop())
        bad_manifest("reordered categories", lambda value: value["families"][0][
            "categories"].reverse())
        bad_manifest("missing current candidate revision", lambda value:
            value["families"][0].update({"candidate_source_sha256": "0" * 64}))
        bad_manifest("mixed old and current adapter revisions", lambda value:
            value["families"][0].update({"candidate_source_sha256":
                provenance("rust", "old")["source"]["sha256"]}))
        bad_manifest("untested category disguised as run", lambda value:
            value["families"][2]["categories"][1].update({"state": "RUN"}))
        bad_manifest("real report disguised as untested", lambda value:
            value["families"][0]["categories"][0].update({"state": "NOT RUN"}))
        bad_manifest("cross-family history attached to missing observations", lambda value:
            value["families"][2]["categories"][1]["superseded"].append(
                value["families"][2]["categories"][0]["superseded"][0]))
        bad_manifest("duplicated report pin", lambda value:
            value["families"][1]["categories"][0].update({"report":
                value["families"][0]["categories"][0]["report"]}))
        for path in ("/foreign.json", "../foreign.json", "docs/evidence/foreign.json",
                     "experiments/rust_public_practice_v1/../foreign.json",
                     "experiments/rust_public_practice_v1/publication-receipt.json"):
            bad_manifest("unsafe report path " + path, lambda value, target=path:
                value["families"][0]["categories"][0]["report"].update(
                    {"relative": target}))

        def bad_report(name: str, family_index: int, category_index: int,
                       mutate: Callable[[dict[str, Any]], None]) -> None:
            changed_manifest = copy.deepcopy(manifest)
            changed_documents = dict(documents)
            entry = changed_manifest["families"][family_index]["categories"][
                category_index]["report"]
            require(type(entry) is dict, "synthetic poison requires a selected report")
            report = decode_document(changed_documents[entry["relative"]],
                                     "synthetic poison source")
            mutate(report)
            if "complete_original_suite_result" in report:
                report["complete_original_process_stdout"] = stream(
                    canonical(report["complete_original_suite_result"]))
            if "complete_controller_result" in report:
                report["complete_controller_stdout"] = stream(
                    canonical(report["complete_controller_result"]))
            raw = canonical(report)
            changed_documents[entry["relative"]] = raw
            entry["sha256"] = hashlib.sha256(raw).hexdigest()

            def changed_loader(relative: str, expected: str) -> dict[str, Any]:
                require(relative in changed_documents
                        and hashlib.sha256(changed_documents[relative]).hexdigest()
                            == expected, "synthetic poison report pin changed")
                return decode_document(changed_documents[relative], relative)

            reject(name, lambda: manifest_rows(changed_manifest, changed_loader,
                                                synthetic_digest))

        bad_report("original private-waiver substitution", 0, 0,
                   lambda value: value.update({"private_waivers": []}))
        bad_report("original public-waiver insertion", 0, 0,
                   lambda value: value.update({"public_waivers": ["ReTests.test_any"]}))
        bad_report("concealed original runnable case", 0, 0,
                   lambda value: value["complete_original_suite_result"][
                       "baseline_records"].pop())
        bad_report("fake debug-only original skip", 0, 0,
                   lambda value: value["complete_original_suite_result"][
                       "baseline_records"][-1].update({"skip_reasons": ["invented"]}))
        bad_report("concealed original mismatch", 1, 0,
                   lambda value: value["complete_original_suite_result"].update(
                       {"mismatch_count": 0, "all_mismatches": []}))
        bad_report("original ownership guard disabled", 0, 0,
                   lambda value: value["complete_original_suite_result"][
                       "matcher_guard"].update({"native_sre_blocked": False}))
        bad_report("original warning checks reduced", 0, 0,
                   lambda value: value["complete_original_suite_result"][
                       "matcher_guard"].update(
                           {"actual_warning_registry_guard_checks": 302}))
        bad_report("unauthenticated Zig FFI preload", 2, 0,
                   lambda value: value["complete_original_suite_result"][
                       "matcher_guard"].update(
                           {"trusted_stdlib_ctypes_source_sha256": None}))
        bad_report("different category candidate adapter", 0, 1,
                   lambda value: value["complete_controller_result"][
                       "native_provenance"]["source"].update(
                           {"sha256": provenance("rust", "old")["source"]["sha256"]}))
        bad_report("swapped independent Rust engine", 0, 1,
                   lambda value: value["complete_controller_result"][
                       "native_provenance"]["native_engine"].update(
                           {"sha256": provenance("rust", "old")[
                               "native_engine"]["sha256"]}))
        bad_report("swapped independent Rust bridge", 0, 1,
                   lambda value: value["complete_controller_result"][
                       "native_provenance"]["native_bridge"].update(
                           {"sha256": provenance("rust", "old")[
                               "native_bridge"]["sha256"]}))
        bad_report("false C engine-bridge identity", 1, 1,
                   lambda value: value["complete_controller_result"][
                       "native_provenance"].update({"native_bridge":
                           provenance("rust")["native_bridge"]}))
        bad_report("cross-family borrowed native adapter", 1, 1,
                   lambda value: value["complete_controller_result"][
                       "native_provenance"].update({"source":
                           provenance("rust")["source"]}))

        def swap_original_component(value: dict[str, Any], role: str,
                                    replacement: dict[str, Any]) -> None:
            for native in (value["candidate_provenance_before"],
                           value["candidate_provenance_after"],
                           value["complete_original_suite_result"]["native_provenance"]):
                native[role] = copy.deepcopy(replacement)

        for index, family in enumerate(FAMILY_NAMES):
            foreign_family = FAMILY_NAMES[(index + 1) % len(FAMILY_NAMES)]
            for role in ("native_engine", "native_bridge"):
                replacement = provenance(foreign_family)[role]
                bad_report(family + " borrowed " + foreign_family + " " + role,
                           index, 0,
                           lambda value, chosen=role, component=replacement:
                               swap_original_component(value, chosen, component))
                replacement = copy.deepcopy(provenance(family)[role])
                replacement["relative"] = (
                    "candidates/_foreign_" + family + "_" + role + ".so")
                bad_report(family + " unapproved same-hash " + role + " path",
                           index, 0,
                           lambda value, chosen=role, component=replacement:
                               swap_original_component(value, chosen, component))

        def swap_c_combined_native(value: dict[str, Any],
                                   replacement: dict[str, Any]) -> None:
            for native in (value["candidate_provenance_before"],
                           value["candidate_provenance_after"],
                           value["complete_original_suite_result"]["native_provenance"]):
                native["native_engine"] = copy.deepcopy(replacement)
                native["native_bridge"] = copy.deepcopy(replacement)

        bad_report("C borrowed foreign engine with preserved same-file bridge", 1, 0,
                   lambda value: swap_c_combined_native(
                       value, provenance("zig")["native_engine"]))
        foreign_c_alias = copy.deepcopy(provenance("c")["native_engine"])
        foreign_c_alias["relative"] = "candidates/_foreign_combined_c.so"
        bad_report("C unapproved same-hash same-file engine and bridge", 1, 0,
                   lambda value: swap_c_combined_native(value, foreign_c_alias))
        bad_report("clipped complete scanner vector", 1, 2,
                   lambda value: value["complete_controller_result"][
                       "candidate_records"].pop())
        bad_report("concealed full scanner mismatches", 1, 2,
                   lambda value: value["complete_controller_result"].update(
                       {"mismatch_count": 0, "all_mismatches": []}))
        bad_report("false candidate category pass", 1, 3,
                   lambda value: value.update({"status": "PASS"}))
        bad_report("reduced category warning guards", 0, 1,
                   lambda value: value.update({"observed_warning_guard_checks": 1}))
        bad_report("false second Python reference", 0, 1,
                   lambda value: value["complete_controller_result"][
                       "second_reference_records"].pop())
        bad_report("hidden-case access", 0, 1,
                   lambda value: value.update({"hidden_cases_read": 1}))
        bad_report("invented speed measurement", 0, 1,
                   lambda value: value.update({"performance": "FAST"}))
        bad_report("clipped isolated controller stream", 0, 1,
                   lambda value: value["complete_controller_stderr"].update(
                       {"complete": False}))

        reject("foreign existing graph without explicit replacement",
               lambda: approve_publication(b"foreign", None, svg, summary, False))
        reject("foreign existing summary without explicit replacement",
               lambda: approve_publication(None, b"foreign", svg, summary, False))
        reject("replacement with only an existing graph",
               lambda: approve_publication(svg, None, svg, summary, True))
        reject("replacement with only an existing summary",
               lambda: approve_publication(None, summary, svg, summary, True))
        reject("replacement with a foreign graph",
               lambda: approve_publication(b"foreign", summary, svg, summary, True))
        reject("replacement with a foreign summary",
               lambda: approve_publication(svg, canonical({"schema": "foreign"}),
                                            svg, summary, True))
        false_summary = copy.deepcopy(decoded_summary)
        false_summary["families"][0]["categories"][0]["passed"] = 150
        reject("replacement with silently changed prior denominator",
               lambda: approve_publication(svg, canonical(false_summary),
                                            svg, summary, True))
        false_summary = copy.deepcopy(decoded_summary)
        false_summary["performance"] = "MEASURED"
        reject("replacement with invented prior speed measurement",
               lambda: approve_publication(svg, canonical(false_summary),
                                            svg, summary, True))

        for label, operation in (
            ("ordinary file reads", lambda: builtins.open("synthetic-forbidden")),
            ("filesystem descriptor reads", lambda: os.open("synthetic", os.O_RDONLY)),
            ("filesystem stat", lambda: os.stat("synthetic")),
            ("symlink-sensitive filesystem stat", lambda: os.lstat("synthetic")),
            ("path evidence reads", lambda: Path("synthetic").read_bytes()),
            ("generated-graph writes", lambda: os.write(1, b"forbidden")),
            ("generated-graph replacement", lambda: os.replace("old", "new")),
            ("candidate imports", lambda: builtins.__import__("candidates")),
            ("dynamic candidate imports", lambda: importlib.import_module("candidates")),
            ("candidate or oracle workers", lambda: subprocess.run(["synthetic"])),
            ("background worker threads", lambda: threading.Thread.start(None)),
            ("performance clocks", lambda: time.perf_counter()),
            ("garbage-collection measurements", lambda: gc.collect()),
        ):
            reject(label, operation)
        accept("every real-world side-effect class is intercepted",
               all(number > 0 for number in effects.values()))
        accept("no candidate imported during purely synthetic controls",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
        require(len(controls) >= 40, "run every mandatory synthetic poison control")
        result = {"schema": SCHEMA + "-self-test", "status": "PASS",
            "python": "3.14.6", "control_count": len(controls),
            "controls": controls, "intercepted_side_effects": dict(effects),
            "common_case_denominator": TOTAL_CASES,
            "families": list(FAMILY_NAMES), "actual_candidate_workers": 0,
            "hidden_cases_read": 0, "performance_files_read": 0,
            "timing_trials_run": 0, "performance": "NOT MEASURED",
            "final_holdout_opened": False, "winner_selected": False,
            "actual_evidence_read": False, "actual_outputs_written": False,
            "synthetic_svg_sha256": hashlib.sha256(svg).hexdigest(),
            "synthetic_summary_sha256": hashlib.sha256(summary).hexdigest()}
    verify_runtime()
    return result


def main(arguments: list[str] | None = None) -> int:
    verify_runtime()
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--manifest")
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--replace-generated", action="store_true",
                        help="atomically refresh only a fully verified previous graph pair")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(not options.render and not options.replace_generated
                and all(getattr(options, name) is None for name in
                ("source_sha256", "manifest", "manifest_sha256")),
                "a synthetic self-test must never render, read, or pin actual inputs")
        result = self_test()
    else:
        require(options.render is True, "explicitly request the pinned overview render")
        result = render(options.source_sha256, options.manifest,
                        options.manifest_sha256, options.replace_generated)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OverviewError, OSError, subprocess.SubprocessError) as error:
        print("frozen correctness overview failed closed: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
