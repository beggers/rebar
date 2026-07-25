#!/usr/bin/env python3
"""Run unchanged CPython tests against an identity-quarantined native matcher."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import contextlib
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import traceback
import types
import unittest
from typing import Any, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/rust_original_cpython_suite_v2.py"
HARNESS_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
HARNESS_MODULE = "tools.rust_original_cpython_suite_v1"
HARNESS_SHA256 = (
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
)
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
)
SCHEMA = "rebar-original-cpython-re-full-methods-v2"
MATRIX_SHA256 = (
    "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
)
BASELINE_SHA256 = (
    "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
)
ORIGINAL_METHOD_COUNT = 165
PUBLIC_METHOD_COUNT = 152
PRIVATE_WAIVER_COUNT = 13
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


class OriginalSuiteError(Exception):
    """A real, complete original-suite observation failed closed."""


class ForbiddenOriginalMatcher(OriginalSuiteError):
    """A genuine original matcher was identified by actual object ownership."""


class BlockedMatcher(types.ModuleType):
    def __getattr__(self, name: str) -> Any:
        raise ForbiddenOriginalMatcher(
            "a quarantined actual original CPython matcher was accessed: "
            + name,
        )


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OriginalSuiteError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return type(value) is str and len(value) == 64 and len(set(value)) > 1 \
        and all(character in "0123456789abcdef" for character in value)


def verify_runtime(*, candidate: bool = False) -> None:
    expected = str(ROOT / SOURCE_RELATIVE)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.realpath(str(ROOT)) == str(ROOT)
            and os.path.abspath(__file__) == expected
            and os.path.realpath(__file__) == expected
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
            "use the pinned real CPython 3.14.6 and exact V2 source")
    if not candidate:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "the original-only V2 controller imported a candidate")


def read_frozen_source(path: Path, expected: str) -> bytes:
    require(isinstance(path, Path) and path.is_absolute()
            and os.path.realpath(str(path)) == str(path)
            and valid_digest(expected),
            "an exact no-symlink frozen original source is required")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode)
                and 0 < info.st_size <= MAX_SOURCE_BYTES,
                "a frozen V1 or V2 original source is not a regular file")
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            item = os.read(descriptor, min(remaining, 1_048_576))
            require(type(item) is bytes and bool(item),
                    "a frozen V1 or V2 original source was truncated")
            chunks.append(item)
            remaining -= len(item)
        require(os.read(descriptor, 1) == b"",
                "a frozen V1 or V2 original source grew during observation")
        final = os.fstat(descriptor)
        require(final.st_dev == info.st_dev and final.st_ino == info.st_ino
                and final.st_size == info.st_size,
                "a frozen original-source identity changed during observation")
    finally:
        os.close(descriptor)
    raw = b"".join(chunks)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "a frozen original V1 test harness or V2 source was substituted")
    return raw


def current_source_sha256() -> str:
    path = ROOT / SOURCE_RELATIVE
    require(os.path.realpath(str(path)) == str(path),
            "the exact V2 original controller source was substituted")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode)
                and 0 < info.st_size <= MAX_SOURCE_BYTES,
                "the actual V2 original controller is not a regular file")
        hasher = hashlib.sha256()
        remaining = info.st_size
        while remaining:
            item = os.read(descriptor, min(remaining, 1_048_576))
            require(type(item) is bytes and bool(item),
                    "the V2 original controller source was truncated")
            hasher.update(item)
            remaining -= len(item)
        require(os.read(descriptor, 1) == b"",
                "the V2 original controller source grew during observation")
        final = os.fstat(descriptor)
        require(final.st_dev == info.st_dev and final.st_ino == info.st_ino
                and final.st_size == info.st_size,
                "the V2 original controller inode changed during observation")
        return hasher.hexdigest()
    finally:
        os.close(descriptor)


def load_original_test_harness() -> Any:
    verify_runtime()
    read_frozen_source(ROOT / HARNESS_RELATIVE, HARNESS_SHA256)
    harness = importlib.import_module(HARNESS_MODULE)
    require(isinstance(harness, types.ModuleType)
            and harness.__name__ == HARNESS_MODULE
            and os.path.abspath(harness.__file__)
            == str(ROOT / HARNESS_RELATIVE)
            and os.path.realpath(harness.__file__)
            == str(ROOT / HARNESS_RELATIVE)
            and harness.current_source_sha256() == HARNESS_SHA256
            and harness.METHOD_MATRIX_SHA256 == MATRIX_SHA256
            and harness.BASELINE_RECORDS_SHA256 == BASELINE_SHA256
            and harness.ORIGINAL_METHOD_COUNT == ORIGINAL_METHOD_COUNT
            and harness.PUBLIC_METHOD_COUNT == PUBLIC_METHOD_COUNT
            and harness.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT,
            "authenticate the immutable V1 original-test harness before use")
    return harness


def capture_original_identities(baseline: Any) -> dict[str, Any]:
    require(type(baseline) is types.ModuleType
            and sys.modules.get("re") is baseline
            and os.path.realpath(baseline.__file__) == str(PINNED_STDLIB_RE),
            "capture actual original module identities before native import")
    blocked = ("_sre", "sre_compile", "sre_parse", "sre_constants")
    modules = {
        name: value for name, value in tuple(sys.modules.items())
        if (name.startswith("re.") or name in blocked)
        and isinstance(value, types.ModuleType)
    }
    require(all(name in modules for name in (
        "re._compiler", "re._parser", "re._casefix", "re._constants", "_sre",
    )), "capture all real original compiler, parser, constants and _sre modules")
    source_modules = (baseline, *modules.values())
    classes: list[type[Any]] = []
    for module in source_modules:
        for item in tuple(vars(module).values()):
            if isinstance(item, type) \
                    and getattr(item, "__module__", None) == module.__name__ \
                    and not any(item is known for known in classes):
                classes.append(item)
    require(isinstance(baseline.Pattern, type)
            and isinstance(baseline.Match, type)
            and any(baseline.Pattern is item for item in classes)
            and any(baseline.Match is item for item in classes),
            "capture the genuine CPython Pattern and Match type identities")
    genuine_scanner = baseline.compile("original-owner-identity").scanner("")
    scanner_type = type(genuine_scanner)
    if not any(scanner_type is item for item in classes):
        classes.append(scanner_type)
    return {
        "baseline": baseline,
        "blocked_names": blocked,
        "descendants": modules,
        "modules": source_modules,
        "namespaces": tuple(vars(module) for module in source_modules),
        "classes": tuple(classes),
        "pattern_type": baseline.Pattern,
        "match_type": baseline.Match,
        "scanner_type": scanner_type,
        "scanner_probe": genuine_scanner,
    }


def is_original_matcher_value(value: Any, ownership: Mapping[str, Any]) -> bool:
    modules = ownership["modules"]
    classes = ownership["classes"]
    if any(value is original for original in modules) \
            or any(value is original for original in classes):
        return True
    if isinstance(value, types.FunctionType):
        if any(value.__globals__ is original
               for original in ownership["namespaces"]):
            return True
    objclass = getattr(value, "__objclass__", None)
    if any(objclass is original for original in classes):
        return True
    bound = getattr(value, "__self__", None)
    if bound is not None and (
        any(bound is original for original in modules)
        or any(bound is original for original in classes)
        or any(type(bound) is original for original in classes)
    ):
        return True
    if any(type(value) is original for original in classes):
        return True
    wrapped = getattr(value, "__wrapped__", None)
    if wrapped is not None and wrapped is not value:
        return is_original_matcher_value(wrapped, ownership)
    return False


def forbid_captured_original_matchers(
    value: Any, ownership: Mapping[str, Any], label: str,
    *, visited: set[int] | None = None, depth: int = 0,
) -> None:
    require(depth <= 12, "the native-owner graph exceeded its audited depth")
    if visited is None:
        visited = set()
    identity = id(value)
    if identity in visited:
        return
    visited.add(identity)
    require(len(visited) <= 20_000,
            "the native-owner graph exceeded its audited object count")
    if is_original_matcher_value(value, ownership):
        raise ForbiddenOriginalMatcher(
            "a genuinely captured original CPython matcher escaped into "
            + label,
        )
    if isinstance(value, types.ModuleType):
        if value.__name__ == "candidates.rust_candidate" \
                or value.__name__.startswith("candidates.rust_candidate."):
            for name, item in tuple(vars(value).items()):
                if name not in ("__builtins__", "__loader__", "__spec__"):
                    forbid_captured_original_matchers(
                        item, ownership, label + "." + name,
                        visited=visited, depth=depth + 1,
                    )
        return
    if isinstance(value, types.FunctionType):
        for name, items in (
            ("defaults", value.__defaults__ or ()),
            ("keyword_defaults", tuple((value.__kwdefaults__ or {}).values())),
            ("closure", tuple(
                cell.cell_contents for cell in value.__closure__ or ()
            )),
        ):
            for index, item in enumerate(items):
                forbid_captured_original_matchers(
                    item, ownership,
                    label + "." + name + "[" + str(index) + "]",
                    visited=visited, depth=depth + 1,
                )
        return
    if isinstance(value, dict):
        for index, (key, item) in enumerate(tuple(value.items())):
            require(index < 20_000,
                    "a native-owner dictionary exceeded its audited bound")
            forbid_captured_original_matchers(
                key, ownership, label + ".key[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )
            forbid_captured_original_matchers(
                item, ownership, label + "[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )
        return
    if isinstance(value, (tuple, list, set, frozenset)):
        for index, item in enumerate(tuple(value)):
            forbid_captured_original_matchers(
                item, ownership, label + "[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )


@contextlib.contextmanager
def original_regex_guard(
    baseline: Any, pins: Mapping[str, str], *, candidate_loader: Any = None,
) -> Iterator[dict[str, Any]]:
    require(type(pins) is dict,
            "all actual quarantined native-owner pins are required")
    ownership = capture_original_identities(baseline)
    descendants = ownership["descendants"]
    blocked_names = ownership["blocked_names"]
    maxgroups = getattr(descendants["re._constants"], "MAXGROUPS", None)
    require(type(maxgroups) is int,
            "capture the exact genuine original MAXGROUPS integer")
    case_module = sys.modules.get("unittest.case")
    require(isinstance(case_module, types.ModuleType)
            and getattr(case_module, "re", None) is baseline
            and getattr(case_module, "TestCase", None) is unittest.TestCase,
            "capture genuine unittest assertions before native import")
    real_assert = unittest.TestCase.assertRegex
    real_assert_not = unittest.TestCase.assertNotRegex
    sentinel = BlockedMatcher("blocked_actual_original_cpython_matcher")
    shim = types.ModuleType("re._constants")
    shim.MAXGROUPS = maxgroups
    shim.__package__ = "re"
    shim.__loader__ = None
    shim.__spec__ = importlib.machinery.ModuleSpec("re._constants", None)
    holders: list[tuple[types.ModuleType, str, Any]] = []
    for module in tuple(sys.modules.values()):
        if not isinstance(module, types.ModuleType) \
                or any(module is item for item in ownership["modules"]):
            continue
        try:
            pairs = tuple(vars(module).items())
        except (TypeError, ValueError):
            continue
        for name, value in pairs:
            if any(value is item for item in ownership["modules"]) \
                    or callable(value) \
                    and is_original_matcher_value(value, ownership):
                holders.append((module, name, value))
    previous_import = builtins.__import__
    previous_import_module = importlib.import_module
    candidate: types.ModuleType | None = None
    native_provenance: dict[str, Any] | None = None

    def forbidden(name: str) -> None:
        raise ForbiddenOriginalMatcher(
            "the actual original CPython matcher is quarantined before and "
            "after native authentication: " + name,
        )

    def resolve_name(name: str, package: Any, level: int = 0) -> str:
        require(type(name) is str and type(level) is int and level >= 0,
                "a concealed relative original-matcher import was attempted")
        if level == 0 and not name.startswith("."):
            return name
        require(type(package) is str and bool(package),
                "a relative matcher import lacks its genuine package")
        return importlib.util.resolve_name(
            "." * level + name if level else name, package,
        )

    def guarded_import(
        name: str, globals: Any = None, locals: Any = None,
        fromlist: Any = (), level: int = 0,
    ) -> Any:
        package = None
        if level:
            require(type(globals) is dict,
                    "a relative matcher import concealed its namespace")
            package = globals.get("__package__")
            if not package:
                package = globals.get("__name__")
                if "__path__" not in globals and type(package) is str:
                    package = package.rpartition(".")[0]
        resolved = resolve_name(name, package, level)
        if resolved == "re":
            if candidate is None:
                forbidden(resolved)
            return candidate
        if resolved == "re._constants":
            if level == 0 and type(fromlist) is tuple \
                    and fromlist == ("MAXGROUPS",):
                return shim
            forbidden(resolved)
        if resolved.startswith("re.") or resolved in blocked_names:
            forbidden(resolved)
        return previous_import(name, globals, locals, fromlist, level)

    def guarded_import_module(name: str, package: str | None = None) -> Any:
        resolved = resolve_name(name, package)
        if resolved == "re":
            if candidate is None:
                forbidden(resolved)
            return candidate
        if resolved.startswith("re.") or resolved in blocked_names:
            forbidden(resolved)
        return previous_import_module(name, package)

    def verify_guard() -> None:
        expected_root = sentinel if candidate is None else candidate
        require(builtins.__import__ is guarded_import
                and importlib.import_module is guarded_import_module
                and sys.modules.get("re") is expected_root
                and sys.modules.get("re._constants") is shim
                and shim.MAXGROUPS == maxgroups
                and set(vars(shim)) == {
                    "__name__", "__doc__", "__package__", "__loader__",
                    "__spec__", "MAXGROUPS",
                }, "the continuous identity-based native quarantine escaped")
        for name, value in tuple(sys.modules.items()):
            if name == "re._constants":
                require(value is shim,
                        "the genuine MAXGROUPS-only constant shim was replaced")
            elif name.startswith("re.") or name in blocked_names:
                require(value is sentinel,
                        "a cached genuine original matcher escaped: " + name)
        for holder, name, original in holders:
            expected = candidate if original is baseline \
                and candidate is not None else sentinel
            require(vars(holder).get(name) is expected,
                    "a real original module or callable escaped: "
                    + holder.__name__ + "." + name)
        require(unittest.TestCase.assertRegex is real_assert
                and unittest.TestCase.assertNotRegex is real_assert_not
                and sys.modules.get("unittest.case") is case_module
                and case_module.TestCase is unittest.TestCase
                and case_module.re is expected_root,
                "genuine unittest assertions or matcher ownership changed")

    try:
        for holder, name, _ in holders:
            setattr(holder, name, sentinel)
        sys.modules["re"] = sentinel
        for name in descendants:
            sys.modules[name] = shim if name == "re._constants" else sentinel
        builtins.__import__ = guarded_import
        importlib.import_module = guarded_import_module
        verify_guard()
        loader = candidate_loader
        if loader is None:
            loader = lambda: load_original_test_harness().authenticate_candidate(
                pins,
            )
        require(callable(loader),
                "the pre-quarantined native adapter loader is mandatory")
        forbid_captured_original_matchers(loader, ownership, "native loader")
        loaded = loader()
        require(type(loaded) is tuple and len(loaded) == 2
                and type(loaded[0]) is types.ModuleType
                and type(loaded[1]) is dict,
                "the quarantined actual native adapter was not authenticated")
        loaded_candidate, loaded_provenance = loaded
        if candidate_loader is None:
            bridge = sys.modules.get("candidates._rust_bridge")
            require(type(bridge) is types.ModuleType
                    and bridge.__name__ == "candidates._rust_bridge"
                    and getattr(loaded_candidate, "Match", None)
                    is getattr(bridge, "Match", None)
                    and isinstance(loaded_candidate.Match, type)
                    and isinstance(getattr(loaded_candidate, "Pattern", None), type)
                    and loaded_candidate.Match is not ownership["match_type"]
                    and loaded_candidate.Pattern is not ownership["pattern_type"],
                    "authenticate actual owned native Match and Pattern identities")
            for name in (
                "search", "match", "fullmatch", "findall", "finditer",
                "split", "sub", "subn", "scanner",
            ):
                descriptor = vars(loaded_candidate.Pattern).get(name)
                require(descriptor is not None
                        and getattr(descriptor, "__objclass__", None)
                        is loaded_candidate.Pattern,
                        "an owned native Pattern descriptor was substituted: "
                        + name)
        forbid_captured_original_matchers(
            loaded_candidate, ownership, "authenticated native adapter",
        )
        candidate = loaded_candidate
        native_provenance = loaded_provenance
        sys.modules["re"] = candidate
        for holder, name, original in holders:
            if original is baseline:
                setattr(holder, name, candidate)
        verify_guard()
        report = {
            "cached_original_matcher_descendant_count": len(descendants),
            "cached_original_holder_count": len(holders),
            "original_matchers_blocked": True,
            "adapter_import_quarantined": True,
            "native_sre_blocked": True,
            "builtins_import_guarded": True,
            "importlib_import_guarded": True,
            "actual_object_identity_guarded": True,
            "public_type_names_used_for_ownership": False,
            "actual_method_guard_checks": 0,
            "verify": verify_guard,
            "candidate": candidate,
            "native_provenance": native_provenance,
        }
        yield report
        verify_guard()
    finally:
        builtins.__import__ = previous_import
        importlib.import_module = previous_import_module
        sys.modules["re"] = baseline
        for name, value in descendants.items():
            sys.modules[name] = value
        for holder, name, previous in reversed(holders):
            setattr(holder, name, previous)


def execute_original_worker(
    role: str, engine: str, source_pin: str, pins: Mapping[str, str] | None,
) -> dict[str, Any]:
    verify_runtime()
    require(valid_digest(source_pin)
            and source_pin == current_source_sha256()
            and role in ("reference_a", "reference_b", "candidate_reference", "rust")
            and engine in ("stdlib", "rust"),
            "an actual V2-pinned isolated original worker is required")
    harness = load_original_test_harness()
    previous = harness.original_regex_guard
    harness.original_regex_guard = original_regex_guard
    try:
        observed = harness.execute_original_worker(
            role, engine, HARNESS_SHA256, pins,
        )
    finally:
        harness.original_regex_guard = previous
    require(type(observed) is dict
            and observed.get("controller_source_sha256") == HARNESS_SHA256
            and observed.get("matrix_sha256") == MATRIX_SHA256
            and observed.get("all_original_method_count") == ORIGINAL_METHOD_COUNT
            and observed.get("actual_public_method_count") == PUBLIC_METHOD_COUNT
            and observed.get("private_waiver_count") == PRIVATE_WAIVER_COUNT,
            "the literal unchanged original V1 method harness was substituted")
    observed["schema"] = SCHEMA + "-isolated-original-worker"
    observed["controller_source_sha256"] = source_pin
    observed["test_harness_relative"] = HARNESS_RELATIVE
    observed["test_harness_sha256"] = HARNESS_SHA256
    return observed


def unique_json(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        require(type(name) is str and name not in result,
                "duplicate genuine original V2 evidence is forbidden")
        result[name] = value
    return result


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete genuine V2 original process output is mandatory: " + label)
    try:
        document = json.loads(
            raw, object_pairs_hook=unique_json,
            parse_constant=lambda _: (_ for _ in ()).throw(
                OriginalSuiteError("nonfinite original evidence is forbidden"),
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise OriginalSuiteError(
            "the complete V2 original process stdout was invalid: " + label,
        ) from error
    require(type(document) is dict and canonical(document) == raw,
            "genuine complete V2 original process output was truncated")
    return document


def validate_worker_document(
    document: Any, role: str, engine: str, source_pin: str, pid: int,
) -> dict[str, Any]:
    require(type(document) is dict and valid_digest(source_pin),
            "the exact source-pinned genuine V2 original worker is required")
    harness = load_original_test_harness()
    checks = {
        "schema": SCHEMA + "-isolated-original-worker",
        "python": "3.14.6", "role": role, "engine": engine, "pid": pid,
        "controller_source_sha256": source_pin,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "original_source_sha256": harness.TEST_SOURCE_SHA256,
        "original_support_sha256": harness.SUPPORT_SHA256,
        "original_warnings_helper_sha256": harness.WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": harness.CORPUS_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(harness.PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "multiprocessing_start_method": "fork",
        "original_bigmem_dry_run": True,
        "original_bigmem_maximum_size": 5_147,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }
    for name, value in checks.items():
        require(document.get(name) == value,
                "an exact genuine V2 original observation changed: " + name)
    matrix = harness.build_matrix()
    require(harness.validate_matrix(matrix) == MATRIX_SHA256,
            "the unchanged original 165-method AST matrix was substituted")
    requirements = [row for row in matrix if row["classification"] == "public"]
    records = document.get("records")
    require(type(records) is list and len(records) == PUBLIC_METHOD_COUNT
            and document.get("records_sha256") == digest(records),
            "an actual full V2 original method or traceback was omitted")
    for requirement, observed in zip(requirements, records, strict=True):
        require(type(observed) is dict
                and observed.get("test") == requirement["test"]
                and observed.get("source_ast_sha256")
                == requirement["source_ast_sha256"]
                and observed.get("tests_run") == 1
                and observed.get("status") in ("PASS", "FAIL", "SKIP")
                and type(observed.get("failure_tracebacks")) is list
                and type(observed.get("error_tracebacks")) is list
                and type(observed.get("skip_reasons")) is list,
                "a full original V2 method identity or traceback was forged")
    require(document.get("pass_count")
            == sum(row["status"] == "PASS" for row in records)
            and document.get("failure_count")
            == sum(row["status"] == "FAIL" for row in records)
            and document.get("skip_count")
            == sum(row["status"] == "SKIP" for row in records)
            and document.get("status") == (
                "PASS" if document.get("pass_count") == 151
                and document.get("skip_count") == 1
                and document.get("failure_count") == 0 else "FAIL"
            ), "an actual V2 original failure or skip was concealed")
    locales = document.get("actual_private_locales")
    require(type(locales) is dict
            and locales.get("actual_localedef_executable") == "/usr/bin/localedef"
            and locales.get("private_temporary_directories_created") == 1
            and locales.get("private_locale_outputs_created") == 2
            and locales.get("actual_localedef_workers") == 2
            and locales.get("iso_8859_1_verified") is True
            and locales.get("utf_8_verified") is True
            and locales.get("temporary_directory_removed") is True
            and locales.get("system_locales_installed") is False
            and locales.get("workspace_files_written") == 0,
            "genuine original V2 private locale resources were substituted")
    if engine == "stdlib":
        require(document.get("actual_candidate_workers") == 0
                and document.get("native_provenance") is None
                and document.get("matcher_guard") is None,
                "a genuine V2 standard reference imported a native candidate")
    else:
        guard = document.get("matcher_guard")
        require(document.get("actual_candidate_workers") == 1
                and type(document.get("native_provenance")) is dict
                and type(guard) is dict
                and guard.get("actual_method_guard_checks")
                == 2 * PUBLIC_METHOD_COUNT
                and guard.get("original_matchers_blocked") is True
                and guard.get("actual_object_identity_guarded") is True
                and guard.get("public_type_names_used_for_ownership") is False,
                "a genuine V2 original method lost its native identity guard")
    if document["status"] == "PASS":
        skips = [row for row in records if row["status"] == "SKIP"]
        require(len(skips) == 1
                and skips[0]["test"] == "ReTests.test_memory_leaks"
                and skips[0]["skip_reasons"] == ["requires debug build"],
                "the sole actual original debug-build skip was substituted")
    return dict(document)


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve every complete V2 original worker stream")
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def run_isolated_worker(
    role: str, engine: str, source_pin: str,
    pins: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--engine", engine, "--role", role,
        "--oracle-source-sha256", source_pin,
    ]
    if engine == "rust":
        require(type(pins) is dict,
                "all actual frozen native candidate pins are mandatory")
        for option, key in (
            ("--candidate-source-sha256", "source"),
            ("--native-engine-sha256", "native_engine"),
            ("--native-bridge-sha256", "native_bridge"),
        ):
            arguments.extend((option, pins[key]))
    else:
        require(pins is None,
                "a real original reference cannot receive native owners")
    process = subprocess.Popen(
        arguments, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(ROOT), shell=False,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
             "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
    )
    stdout, stderr = process.communicate()
    if stderr or process.returncode not in (0, 1):
        raise OriginalSuiteError(canonical({
            "schema": SCHEMA + "-complete-isolated-worker-failure",
            "role": role, "pid": process.pid,
            "returncode": process.returncode,
            "stdout": encode_stream(stdout), "stderr": encode_stream(stderr),
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED",
        }).decode("ascii"))
    result = validate_worker_document(
        decode_document(stdout, role), role, engine, source_pin, process.pid,
    )
    require(process.returncode == (0 if result["status"] == "PASS" else 1),
            "a genuine V2 original worker return code was misclassified")
    return result


def source_only_quarantine_controls() -> dict[str, Any]:
    baseline = importlib.import_module("re")
    native = importlib.import_module("_sre")
    require(type(baseline) is types.ModuleType
            and os.path.realpath(baseline.__file__) == str(PINNED_STDLIB_RE)
            and type(native) is types.ModuleType
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "source controls must not import or execute a native candidate")
    original_builtin = builtins.__import__
    original_import_module = importlib.import_module
    original_case = sys.modules["unittest.case"]
    original_assert = unittest.TestCase.assertRegex
    original_assert_not = unittest.TestCase.assertNotRegex
    original_modules = {
        name: value for name, value in tuple(sys.modules.items())
        if name == "re" or name.startswith("re.")
        or name in ("_sre", "sre_compile", "sre_parse", "sre_constants")
    }
    original_pattern = baseline.compile("source-only-v2-identity-poison")
    original_scanner = original_pattern.scanner("")
    poisoned_adapter = types.ModuleType("candidates.rust_candidate")
    poisoned_adapter.captured_original_compile = baseline.compile
    poisons: tuple[tuple[str, Any], ...] = (
        ("preimport_builtin_re", lambda: builtins.__import__("re")),
        ("preimport_builtin_native_sre", lambda: builtins.__import__("_sre")),
        ("preimport_builtin_re_compiler",
         lambda: builtins.__import__("re._compiler")),
        ("preimport_importlib_re", lambda: importlib.import_module("re")),
        ("preimport_importlib_native_sre",
         lambda: importlib.import_module("_sre")),
        ("preimport_importlib_re_compiler",
         lambda: importlib.import_module("re._compiler")),
        ("preimport_importlib_re_parser",
         lambda: importlib.import_module("re._parser")),
        ("preimport_importlib_legacy_sre_compile",
         lambda: importlib.import_module("sre_compile")),
        ("preimport_sys_modules_native_sre",
         lambda: getattr(sys.modules["_sre"], "compile")),
        ("preimport_sys_modules_re_compiler",
         lambda: getattr(sys.modules["re._compiler"], "compile")),
        ("preimport_sys_modules_root_re",
         lambda: getattr(sys.modules["re"], "compile")),
        ("constant_shim_importlib_bypass",
         lambda: importlib.import_module("re._constants")),
        ("constant_shim_multiple_names",
         lambda: builtins.__import__(
             "re._constants", fromlist=("MAXGROUPS", "SRE_FLAG_IGNORECASE"),
         )),
        ("constant_shim_mutable_fromlist",
         lambda: builtins.__import__(
             "re._constants", fromlist=["MAXGROUPS"],
         )),
        ("captured_original_compile",
         lambda matcher=baseline.compile: matcher("forbidden")),
        ("captured_original_search",
         lambda matcher=baseline.search: matcher("forbidden", "forbidden")),
        ("captured_native_sre_compile",
         lambda matcher=native.compile: matcher()),
        ("captured_original_pattern_bound_search",
         lambda matcher=original_pattern.search: matcher("forbidden")),
        ("captured_original_adapter_graph",
         lambda adapter=poisoned_adapter: (adapter, {})),
        ("captured_genuine_original_match_type",
         lambda original=baseline.Match: (original, {})),
        ("captured_genuine_original_pattern_type",
         lambda original=baseline.Pattern: (original, {})),
        ("captured_genuine_original_pattern_descriptor",
         lambda original=baseline.Pattern.search: (original, {})),
        ("captured_genuine_original_scanner_type",
         lambda original=type(original_scanner): (original, {})),
        ("captured_genuine_original_scanner_bound_method",
         lambda original=original_scanner.search: (original, {})),
    )
    rejected: list[str] = []
    for name, poison in poisons:
        try:
            with original_regex_guard(baseline, {}, candidate_loader=poison):
                raise OriginalSuiteError(
                    "a genuine captured matcher poison executed: " + name,
                )
        except ForbiddenOriginalMatcher:
            rejected.append(name)
        else:
            raise OriginalSuiteError(
                "a genuine original matcher poison escaped: " + name,
            )
        require(builtins.__import__ is original_builtin
                and importlib.import_module is original_import_module
                and sys.modules.get("unittest.case") is original_case
                and original_case.re is baseline
                and unittest.TestCase.assertRegex is original_assert
                and unittest.TestCase.assertNotRegex is original_assert_not
                and all(sys.modules.get(key) is value
                        for key, value in original_modules.items())
                and not any(key == "candidates" or key.startswith("candidates.")
                            for key in sys.modules),
                "a genuine V2 matcher poison failed to restore: " + name)

    synthetic = types.ModuleType("rebar_v2_source_only_owned_matcher")
    synthetic.Match = type("Match", (), {"__module__": "re"})
    synthetic.Pattern = type("Pattern", (), {"__module__": "re"})
    synthetic.ScannerType = type(
        "SRE_Scanner", (), {"__module__": "_sre"},
    )

    def clean_source_loader() -> tuple[types.ModuleType, dict[str, bool]]:
        return synthetic, {"source_only_control": True}

    ownership = capture_original_identities(baseline)
    require(all(not is_original_matcher_value(value, ownership) for value in (
        synthetic.Match, synthetic.Pattern, synthetic.ScannerType,
    )), "same-named independently owned native types were falsely rejected")
    with original_regex_guard(
        baseline, {}, candidate_loader=clean_source_loader,
    ) as active:
        require(active["candidate"] is synthetic
                and active["actual_object_identity_guarded"] is True
                and active["public_type_names_used_for_ownership"] is False
                and active["adapter_import_quarantined"] is True
                and active["native_sre_blocked"] is True
                and builtins.__import__("re") is synthetic
                and importlib.import_module("re") is synthetic
                and original_case.re is synthetic,
                "genuine source-only same-named owned types were rejected")
        constant = builtins.__import__(
            "re._constants", fromlist=("MAXGROUPS",),
        )
        require(constant is sys.modules["re._constants"]
                and type(constant.MAXGROUPS) is int
                and set(vars(constant)) == {
                    "__name__", "__doc__", "__package__", "__loader__",
                    "__spec__", "MAXGROUPS",
                }, "the identity-quarantined MAXGROUPS shim was expanded")
        active["verify"]()
    require(builtins.__import__ is original_builtin
            and importlib.import_module is original_import_module
            and sys.modules.get("unittest.case") is original_case
            and original_case.re is baseline
            and unittest.TestCase.assertRegex is original_assert
            and unittest.TestCase.assertNotRegex is original_assert_not
            and all(sys.modules.get(key) is value
                    for key, value in original_modules.items())
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "the identity-quarantined positive control was not fully restored")
    return {
        "rejected_count": len(rejected), "rejected_names": rejected,
        "source_only_positive_controls": 1,
        "source_only_owned_public_type_positive_count": 3,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "original_matchers_restored": True,
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    source_pin = current_source_sha256()
    harness = load_original_test_harness()
    matrix = harness.build_matrix()
    require(harness.validate_matrix(matrix) == MATRIX_SHA256,
            "authenticate all 165 actual source-ordered original methods")
    first = run_isolated_worker("reference_a", "stdlib", source_pin)
    second = run_isolated_worker("reference_b", "stdlib", source_pin)
    require(first["pid"] != second["pid"]
            and first["status"] == second["status"] == "PASS"
            and first["records"] == second["records"]
            and first["records_sha256"] == second["records_sha256"]
            == BASELINE_SHA256,
            "two genuine independent V2 original CPython references disagree")
    rejected = 0
    for index in range(30):
        omitted = list(matrix)
        omitted.pop(index)
        try:
            harness.validate_matrix(omitted)
        except harness.OriginalSuiteError:
            rejected += 1
        else:
            raise OriginalSuiteError("a genuine original method was omitted")
    for index in range(15):
        changed = list(matrix)
        substituted = dict(changed[index])
        substituted["test"] = "ForgedOriginal.test_substituted"
        changed[index] = substituted
        try:
            harness.validate_matrix(changed)
        except harness.OriginalSuiteError:
            rejected += 1
        else:
            raise OriginalSuiteError("a forged original method was accepted")
    for invalid in (None, "", "0" * 64, "A" * 64, "g" * 64):
        require(not valid_digest(invalid),
                "a forged V2 original source fingerprint was accepted")
        rejected += 1
    controls = source_only_quarantine_controls()
    require(controls["rejected_count"] >= 24
            and controls["source_only_owned_public_type_positive_count"] == 3
            and controls["actual_candidate_workers"] == 0
            and controls["actual_candidate_imports"] == 0
            and controls["original_matchers_restored"] is True,
            "actual V2 identity-quarantine source controls did not pass")
    rejected += controls["rejected_count"]
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "controller_source_sha256": source_pin,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "original_source_sha256": harness.TEST_SOURCE_SHA256,
        "original_support_sha256": harness.SUPPORT_SHA256,
        "original_warnings_helper_sha256": harness.WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": harness.CORPUS_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "actual_pass_count_per_worker": 151,
        "authentic_debug_skip_count_per_worker": 1,
        "authentic_debug_skip": "ReTests.test_memory_leaks",
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(harness.PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_localedef_workers": 4,
        "actual_private_temporary_directories_created": 2,
        "actual_private_locale_outputs_created": 4,
        "all_private_temporary_directories_removed": True,
        "original_multiprocessing_start_method": "fork",
        "original_bigmem_dry_run": True,
        "rejected_control_count": rejected,
        "source_only_quarantine_poison_count": controls["rejected_count"],
        "source_only_quarantine_poison_names": controls["rejected_names"],
        "source_only_quarantine_positive_controls": (
            controls["source_only_positive_controls"]
        ),
        "source_only_owned_public_type_positive_count": (
            controls["source_only_owned_public_type_positive_count"]
        ),
        "original_matchers_restored": controls["original_matchers_restored"],
        "public_type_names_used_for_ownership": False,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def run_candidate(
    source_pin: str, matrix_pin: str, pins: dict[str, str],
) -> dict[str, Any]:
    verify_runtime()
    require(valid_digest(source_pin)
            and source_pin == current_source_sha256()
            and matrix_pin == MATRIX_SHA256
            and set(pins) == {"source", "native_engine", "native_bridge"}
            and all(valid_digest(value) for value in pins.values()),
            "all exact frozen V2 oracle, original matrix and native pins are required")
    harness = load_original_test_harness()
    matrix = harness.build_matrix()
    require(harness.validate_matrix(matrix) == MATRIX_SHA256,
            "the frozen 165-method original V2 matrix was substituted")
    baseline = run_isolated_worker(
        "candidate_reference", "stdlib", source_pin,
    )
    require(baseline["status"] == "PASS"
            and baseline["records_sha256"] == BASELINE_SHA256,
            "the actual frozen V2 original standard reference failed")
    candidate = run_isolated_worker("rust", "rust", source_pin, pins)
    require(baseline["pid"] != candidate["pid"],
            "the genuine original standard and Rust workers were not isolated")
    mismatches: list[dict[str, Any]] = []
    for expected, observed in zip(
        baseline["records"], candidate["records"], strict=True,
    ):
        require(expected["test"] == observed["test"]
                and expected["source_ast_sha256"]
                == observed["source_ast_sha256"],
                "a source-ordered original V2 method was substituted")
        if expected != observed:
            mismatches.append({
                "test": expected["test"],
                "baseline": expected, "candidate": observed,
            })
    return {
        "schema": SCHEMA + "-actual-original-candidate-result",
        "status": "PASS" if not mismatches else "FAIL",
        "python": "3.14.6",
        "controller_source_sha256": source_pin,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "original_source_sha256": harness.TEST_SOURCE_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(harness.PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "baseline_records_sha256": baseline["records_sha256"],
        "candidate_records_sha256": candidate["records_sha256"],
        "baseline_records": baseline["records"],
        "candidate_records": candidate["records"],
        "mismatch_count": len(mismatches),
        "all_mismatches": mismatches,
        "baseline_pid": baseline["pid"],
        "candidate_pid": candidate["pid"],
        "native_provenance": candidate["native_provenance"],
        "matcher_guard": candidate["matcher_guard"],
        "actual_candidate_workers": 1,
        "actual_localedef_workers": 4,
        "actual_private_temporary_directories_created": 2,
        "actual_private_locale_outputs_created": 4,
        "all_private_temporary_directories_removed": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "benchmark_files_read": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run unchanged original CPython tests with owned matcher identities",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", action="store_true")
    modes.add_argument("--internal-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--engine", choices=("stdlib", "rust"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--role", help=argparse.SUPPRESS)
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def option_pins(options: argparse.Namespace) -> dict[str, str]:
    pins = {
        "source": options.candidate_source_sha256,
        "native_engine": options.native_engine_sha256,
        "native_bridge": options.native_bridge_sha256,
    }
    require(all(valid_digest(value) for value in pins.values()),
            "pin all three exact independently owned native components")
    return pins


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "engine", "role", "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "a genuine V2 source self-test must not pin or import a candidate")
        result = source_self_test()
    elif options.candidate:
        require(options.engine is None and options.role is None
                and valid_digest(options.oracle_source_sha256)
                and options.matrix_sha256 == MATRIX_SHA256,
                "a native candidate requires exact frozen V2 source and matrix pins")
        result = run_candidate(
            options.oracle_source_sha256, options.matrix_sha256,
            option_pins(options),
        )
    else:
        require(options.engine in ("stdlib", "rust")
                and type(options.role) is str and bool(options.role)
                and valid_digest(options.oracle_source_sha256),
                "an actual source-pinned V2 isolated original worker is mandatory")
        pins = option_pins(options) if options.engine == "rust" else None
        result = execute_original_worker(
            options.role, options.engine, options.oracle_source_sha256, pins,
        )
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        sys.stderr.buffer.write(canonical({
            "schema": SCHEMA + "-complete-original-worker-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "complete_traceback": traceback.format_exc(),
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED",
        }))
        sys.stderr.buffer.flush()
        raise SystemExit(1) from error
