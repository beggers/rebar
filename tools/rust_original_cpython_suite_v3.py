#!/usr/bin/env python3
"""Run original CPython regex tests with safe matcher and warning identities."""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import traceback
import types
import unittest
import warnings
from typing import Any, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/rust_original_cpython_suite_v3.py"
IDENTITY_GUARD_RELATIVE = "tools/rust_original_cpython_suite_v2.py"
IDENTITY_GUARD_MODULE = "tools.rust_original_cpython_suite_v2"
IDENTITY_GUARD_SHA256 = (
    "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267"
)
HARNESS_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
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
SCHEMA = "rebar-original-cpython-re-full-methods-v3"
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
    """An authenticated original observation was missing or substituted."""


_identity_guard: types.ModuleType | None = None


class WarningSafeBlockedMatcher(types.ModuleType):
    """Deny matcher access while leaving absent warning metadata truly absent."""

    def __getattr__(self, name: str) -> Any:
        if name == "__warningregistry__":
            raise AttributeError(name)
        guard = _identity_guard
        if guard is None:
            raise OriginalSuiteError(
                "the warning-safe original matcher guard was not authenticated",
            )
        raise guard.ForbiddenOriginalMatcher(
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
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.realpath(str(ROOT)) == str(ROOT)
            and os.path.abspath(__file__) == expected
            and os.path.realpath(__file__) == expected
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
            "use only the exact pinned CPython and original V3 controller")
    if not candidate:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "an original-only V3 source controller imported a candidate")


def read_frozen_source(path: Path, expected: str) -> bytes:
    require(isinstance(path, Path) and path.is_absolute()
            and os.path.realpath(str(path)) == str(path)
            and valid_digest(expected),
            "authenticate every exact immutable original-test source")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and 0 < initial.st_size <= MAX_SOURCE_BYTES,
                "a frozen original-test source is not a regular file")
        remaining = initial.st_size
        chunks: list[bytes] = []
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "a frozen original-test source was truncated")
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "a frozen original-test source grew during observation")
        final = os.fstat(descriptor)
        require(final.st_dev == initial.st_dev
                and final.st_ino == initial.st_ino
                and final.st_size == initial.st_size,
                "a frozen original-test source inode was substituted")
    finally:
        os.close(descriptor)
    raw = b"".join(chunks)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "a frozen V1 original harness or V2 identity guard changed")
    return raw


def current_source_sha256() -> str:
    path = ROOT / SOURCE_RELATIVE
    require(os.path.realpath(str(path)) == str(path),
            "the exact frozen V3 original controller path was substituted")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and 0 < initial.st_size <= MAX_SOURCE_BYTES,
                "the real V3 original controller is not a regular file")
        remaining = initial.st_size
        hasher = hashlib.sha256()
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "the actual V3 controller was truncated")
            hasher.update(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "the actual V3 controller grew during observation")
        final = os.fstat(descriptor)
        require(final.st_dev == initial.st_dev
                and final.st_ino == initial.st_ino
                and final.st_size == initial.st_size,
                "the exact V3 original controller inode changed")
        return hasher.hexdigest()
    finally:
        os.close(descriptor)


def load_identity_guard() -> types.ModuleType:
    global _identity_guard
    verify_runtime()
    read_frozen_source(ROOT / IDENTITY_GUARD_RELATIVE, IDENTITY_GUARD_SHA256)
    read_frozen_source(ROOT / HARNESS_RELATIVE, HARNESS_SHA256)
    guard = importlib.import_module(IDENTITY_GUARD_MODULE)
    require(isinstance(guard, types.ModuleType)
            and guard.__name__ == IDENTITY_GUARD_MODULE
            and os.path.abspath(guard.__file__)
            == str(ROOT / IDENTITY_GUARD_RELATIVE)
            and os.path.realpath(guard.__file__)
            == str(ROOT / IDENTITY_GUARD_RELATIVE)
            and guard.current_source_sha256() == IDENTITY_GUARD_SHA256
            and guard.HARNESS_RELATIVE == HARNESS_RELATIVE
            and guard.HARNESS_SHA256 == HARNESS_SHA256
            and guard.MATRIX_SHA256 == MATRIX_SHA256
            and guard.BASELINE_SHA256 == BASELINE_SHA256
            and guard.ORIGINAL_METHOD_COUNT == ORIGINAL_METHOD_COUNT
            and guard.PUBLIC_METHOD_COUNT == PUBLIC_METHOD_COUNT
            and guard.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT,
            "authenticate both immutable original V2 guard and V1 harness")
    if _identity_guard is not None:
        require(_identity_guard is guard,
                "the exact loaded V2 identity guard was substituted")
    _identity_guard = guard
    return guard


@contextlib.contextmanager
def installed_warning_safe_guard(guard: types.ModuleType) -> Iterator[None]:
    require(guard is _identity_guard
            and guard.current_source_sha256() == IDENTITY_GUARD_SHA256,
            "install only the actual immutable V2 matcher-identity guard")
    previous_sentinel = guard.BlockedMatcher
    previous_guard = guard.original_regex_guard

    @contextlib.contextmanager
    def warning_safe_original_regex_guard(
        baseline: Any, pins: Mapping[str, str], *, candidate_loader: Any = None,
    ) -> Iterator[dict[str, Any]]:
        with previous_guard(
            baseline, pins, candidate_loader=candidate_loader,
        ) as active:
            sentinel = sys.modules.get("_sre")
            require(type(sentinel) is WarningSafeBlockedMatcher
                    and "__warningregistry__" not in vars(sentinel)
                    and getattr(sentinel, "__warningregistry__", None) is None,
                    "the exact absent warning registry was substituted")
            previous_verify = active["verify"]
            active["warning_registry_introspection_safe"] = True
            active["warning_registry_exactly_absent"] = True
            active["actual_warning_registry_guard_checks"] = 0

            def verify_warning_safe_guard() -> None:
                previous_verify()
                require(sys.modules.get("_sre") is sentinel
                        and "__warningregistry__" not in vars(sentinel)
                        and getattr(sentinel, "__warningregistry__", None)
                        is None,
                        "an original warning registry or matcher guard escaped")
                active["actual_warning_registry_guard_checks"] += 1

            active["verify"] = verify_warning_safe_guard
            yield active

    guard.BlockedMatcher = WarningSafeBlockedMatcher
    guard.original_regex_guard = warning_safe_original_regex_guard
    try:
        require(guard.BlockedMatcher is WarningSafeBlockedMatcher
                and guard.original_regex_guard is warning_safe_original_regex_guard,
                "the warning-safe original matcher guard was substituted")
        yield
    finally:
        guard.original_regex_guard = previous_guard
        guard.BlockedMatcher = previous_sentinel


def execute_original_worker(
    role: str, engine: str, source_pin: str, pins: Mapping[str, str] | None,
) -> dict[str, Any]:
    verify_runtime()
    require(valid_digest(source_pin)
            and source_pin == current_source_sha256()
            and role in ("reference_a", "reference_b", "candidate_reference", "rust")
            and engine in ("stdlib", "rust"),
            "require an exact genuine V3-pinned original worker")
    guard = load_identity_guard()
    with installed_warning_safe_guard(guard):
        observed = guard.execute_original_worker(
            role, engine, IDENTITY_GUARD_SHA256, pins,
        )
    require(type(observed) is dict
            and observed.get("schema")
            == guard.SCHEMA + "-isolated-original-worker"
            and observed.get("controller_source_sha256")
            == IDENTITY_GUARD_SHA256
            and observed.get("test_harness_relative") == HARNESS_RELATIVE
            and observed.get("test_harness_sha256") == HARNESS_SHA256
            and observed.get("matrix_sha256") == MATRIX_SHA256,
            "authenticate exact frozen V2 guard and V1 literal test results")
    if engine == "rust":
        report = observed.get("matcher_guard")
        require(type(report) is dict
                and report.get("warning_registry_introspection_safe") is True
                and report.get("warning_registry_exactly_absent") is True
                and report.get("actual_method_guard_checks")
                == 2 * PUBLIC_METHOD_COUNT
                and report.get("actual_warning_registry_guard_checks")
                == 2 * PUBLIC_METHOD_COUNT,
                "every genuine upstream method needs both exact identity guards")
    observed["schema"] = SCHEMA + "-isolated-original-worker"
    observed["controller_source_sha256"] = source_pin
    observed["identity_guard_relative"] = IDENTITY_GUARD_RELATIVE
    observed["identity_guard_sha256"] = IDENTITY_GUARD_SHA256
    return observed


def unique_json(items: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in output,
                "duplicate original V3 observations are forbidden")
        output[key] = value
    return output


def decode_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete genuine original V3 worker bytes are mandatory: " + label)
    try:
        result = json.loads(
            raw, object_pairs_hook=unique_json,
            parse_constant=lambda _: (_ for _ in ()).throw(
                OriginalSuiteError("nonfinite original evidence is forbidden"),
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise OriginalSuiteError(
            "the complete genuine V3 original worker output was invalid",
        ) from error
    require(type(result) is dict and canonical(result) == raw,
            "the complete genuine V3 original worker output was truncated")
    return result


def validate_worker_document(
    result: Any, role: str, engine: str, source_pin: str, pid: int,
) -> dict[str, Any]:
    require(type(result) is dict and valid_digest(source_pin)
            and result.get("schema") == SCHEMA + "-isolated-original-worker"
            and result.get("controller_source_sha256") == source_pin
            and result.get("identity_guard_relative") == IDENTITY_GUARD_RELATIVE
            and result.get("identity_guard_sha256") == IDENTITY_GUARD_SHA256
            and result.get("test_harness_relative") == HARNESS_RELATIVE
            and result.get("test_harness_sha256") == HARNESS_SHA256,
            "require all three exact frozen original-source provenances")
    guard = load_identity_guard()
    previous = dict(result)
    previous.pop("identity_guard_relative")
    previous.pop("identity_guard_sha256")
    previous["schema"] = guard.SCHEMA + "-isolated-original-worker"
    previous["controller_source_sha256"] = IDENTITY_GUARD_SHA256
    with installed_warning_safe_guard(guard):
        guard.validate_worker_document(
            previous, role, engine, IDENTITY_GUARD_SHA256, pid,
        )
    if engine == "rust":
        matcher = result.get("matcher_guard")
        require(type(matcher) is dict
                and matcher.get("warning_registry_introspection_safe") is True
                and matcher.get("warning_registry_exactly_absent") is True
                and matcher.get("actual_method_guard_checks")
                == 2 * PUBLIC_METHOD_COUNT
                and matcher.get("actual_warning_registry_guard_checks")
                == 2 * PUBLIC_METHOD_COUNT,
                "actual V3 matcher and original warning checks were omitted")
    return dict(result)


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve complete authentic original V3 process streams")
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
                "pin all genuine owned native candidate components")
        for option, key in (
            ("--candidate-source-sha256", "source"),
            ("--native-engine-sha256", "native_engine"),
            ("--native-bridge-sha256", "native_bridge"),
        ):
            arguments.extend((option, pins[key]))
    else:
        require(pins is None,
                "a genuine original reference cannot receive native pins")
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
            "a genuine original V3 worker exit code was misclassified")
    return result


def warning_registry_controls(guard: types.ModuleType) -> dict[str, Any]:
    baseline = importlib.import_module("re")
    require(type(baseline) is types.ModuleType
            and os.path.realpath(baseline.__file__) == str(PINNED_STDLIB_RE)
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "warning controls must contain zero actual native candidates")
    original_builtin = builtins.__import__
    original_import_module = importlib.import_module
    original_case = sys.modules["unittest.case"]
    original_assert = unittest.TestCase.assertRegex
    original_assert_not = unittest.TestCase.assertNotRegex
    synthetic = types.ModuleType("rebar_v3_source_only_owned_matcher")
    synthetic.Match = type("Match", (), {"__module__": "re"})
    synthetic.Pattern = type("Pattern", (), {"__module__": "re"})
    synthetic.ScannerType = type(
        "SRE_Scanner", (), {"__module__": "_sre"},
    )

    def source_loader() -> tuple[types.ModuleType, dict[str, bool]]:
        return synthetic, {"source_only_warning_control": True}

    with guard.original_regex_guard(
        baseline, {}, candidate_loader=source_loader,
    ) as active:
        require(active["candidate"] is synthetic
                and active.get("warning_registry_introspection_safe") is True
                and active.get("warning_registry_exactly_absent") is True
                and active.get("actual_object_identity_guarded") is True
                and active.get("public_type_names_used_for_ownership") is False,
                "genuine warning-safe matcher identities were substituted")
        sentinel = sys.modules["_sre"]
        require(type(sentinel) is WarningSafeBlockedMatcher
                and "__warningregistry__" not in vars(sentinel)
                and getattr(sentinel, "__warningregistry__", None) is None,
                "the absent original warning registry was silently expanded")
        try:
            getattr(sentinel, "__warningregistry__")
        except AttributeError:
            registry_absent = True
        else:
            raise OriginalSuiteError(
                "quarantined warning metadata did not behave as genuinely absent",
            )
        case = unittest.TestCase()
        with case.assertWarns(DeprecationWarning) as captured:
            warnings.warn(
                "genuine V3 original assertWarns registry control",
                DeprecationWarning, stacklevel=1,
            )
        require(registry_absent
                and isinstance(captured.warning, DeprecationWarning)
                and os.path.realpath(captured.filename)
                == str(ROOT / SOURCE_RELATIVE)
                and "__warningregistry__" not in vars(sentinel),
                "the actual original unittest.assertWarns control failed")
        rejected: list[str] = []
        for name, poison in (
            ("warning_safe_block_native_compile",
             lambda: getattr(sys.modules["_sre"], "compile")),
            ("warning_safe_block_native_search",
             lambda: getattr(sys.modules["_sre"], "search")),
            ("warning_safe_block_native_import",
             lambda: builtins.__import__("_sre")),
            ("warning_safe_block_native_importlib",
             lambda: importlib.import_module("_sre")),
            ("warning_safe_block_cached_compiler",
             lambda: getattr(sys.modules["re._compiler"], "compile")),
            ("warning_safe_block_constant_importlib",
             lambda: importlib.import_module("re._constants")),
        ):
            try:
                poison()
            except guard.ForbiddenOriginalMatcher:
                rejected.append(name)
            else:
                raise OriginalSuiteError(
                    "a warning-safe original matcher operation escaped: " + name,
                )
        active["verify"]()
    require(builtins.__import__ is original_builtin
            and importlib.import_module is original_import_module
            and sys.modules.get("unittest.case") is original_case
            and original_case.re is baseline
            and unittest.TestCase.assertRegex is original_assert
            and unittest.TestCase.assertNotRegex is original_assert_not
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "the actual assertWarns matcher control did not restore exact originals")
    return {
        "source_only_warning_positive_controls": 1,
        "source_only_warning_filename_verified": True,
        "warning_registry_exactly_absent": True,
        "warning_safe_rejected_count": len(rejected),
        "warning_safe_rejected_names": rejected,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    source_pin = current_source_sha256()
    guard = load_identity_guard()
    harness = guard.load_original_test_harness()
    matrix = harness.build_matrix()
    require(harness.validate_matrix(matrix) == MATRIX_SHA256,
            "authenticate the complete unchanged 165-method original matrix")
    first = run_isolated_worker("reference_a", "stdlib", source_pin)
    second = run_isolated_worker("reference_b", "stdlib", source_pin)
    require(first["pid"] != second["pid"]
            and first["status"] == second["status"] == "PASS"
            and first["records"] == second["records"]
            and first["records_sha256"] == second["records_sha256"]
            == BASELINE_SHA256,
            "genuine independent V3 original CPython workers disagree")
    rejected = 0
    for index in range(30):
        changed = list(matrix)
        changed.pop(index)
        try:
            harness.validate_matrix(changed)
        except harness.OriginalSuiteError:
            rejected += 1
        else:
            raise OriginalSuiteError("a genuine V3 original method was omitted")
    for index in range(15):
        changed = list(matrix)
        row = dict(changed[index])
        row["test"] = "ForgedOriginal.test_substituted"
        changed[index] = row
        try:
            harness.validate_matrix(changed)
        except harness.OriginalSuiteError:
            rejected += 1
        else:
            raise OriginalSuiteError("a forged V3 original method was accepted")
    for invalid in (None, "", "0" * 64, "A" * 64, "g" * 64):
        require(not valid_digest(invalid),
                "a forged V3 original source fingerprint was accepted")
        rejected += 1
    with installed_warning_safe_guard(guard):
        controls = guard.source_only_quarantine_controls()
        registry = warning_registry_controls(guard)
    require(controls["rejected_count"] >= 24
            and controls["source_only_owned_public_type_positive_count"] == 3
            and controls["actual_candidate_workers"] == 0
            and controls["actual_candidate_imports"] == 0
            and controls["original_matchers_restored"] is True
            and registry["source_only_warning_positive_controls"] == 1
            and registry["warning_safe_rejected_count"] >= 6
            and registry["warning_registry_exactly_absent"] is True
            and registry["source_only_warning_filename_verified"] is True
            and registry["actual_candidate_workers"] == 0
            and registry["actual_candidate_imports"] == 0,
            "real matcher, owned-name and assertWarns controls failed")
    rejected += controls["rejected_count"] + registry["warning_safe_rejected_count"]
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "controller_source_sha256": source_pin,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
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
        "source_only_owned_public_type_positive_count": (
            controls["source_only_owned_public_type_positive_count"]
        ),
        "source_only_warning_positive_controls": (
            registry["source_only_warning_positive_controls"]
        ),
        "source_only_warning_filename_verified": (
            registry["source_only_warning_filename_verified"]
        ),
        "warning_registry_exactly_absent": (
            registry["warning_registry_exactly_absent"]
        ),
        "warning_safe_rejected_count": registry["warning_safe_rejected_count"],
        "warning_safe_rejected_names": registry["warning_safe_rejected_names"],
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
            "pin exact original V3, frozen matrix and all native owners")
    guard = load_identity_guard()
    harness = guard.load_original_test_harness()
    require(harness.validate_matrix(harness.build_matrix()) == MATRIX_SHA256,
            "the source-ordered original V3 matrix was substituted")
    baseline = run_isolated_worker(
        "candidate_reference", "stdlib", source_pin,
    )
    require(baseline["status"] == "PASS"
            and baseline["records_sha256"] == BASELINE_SHA256,
            "the genuine original V3 standard reference failed")
    candidate = run_isolated_worker("rust", "rust", source_pin, pins)
    require(baseline["pid"] != candidate["pid"],
            "genuine V3 original standard and native workers were not isolated")
    mismatches: list[dict[str, Any]] = []
    for expected, observed in zip(
        baseline["records"], candidate["records"], strict=True,
    ):
        require(expected["test"] == observed["test"]
                and expected["source_ast_sha256"]
                == observed["source_ast_sha256"],
                "a real source-ordered V3 method was substituted")
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
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
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
        "mismatch_count": len(mismatches), "all_mismatches": mismatches,
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
        description="Run unchanged original regex tests and genuine warning assertions",
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
            "authenticate all three exact independently owned native components")
    return pins


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "engine", "role", "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "a real V3 source self-test must contain zero native candidates")
        result = source_self_test()
    elif options.candidate:
        require(options.engine is None and options.role is None
                and valid_digest(options.oracle_source_sha256)
                and options.matrix_sha256 == MATRIX_SHA256,
                "an actual candidate requires frozen V3 source and matrix pins")
        result = run_candidate(
            options.oracle_source_sha256, options.matrix_sha256,
            option_pins(options),
        )
    else:
        require(options.engine in ("stdlib", "rust")
                and type(options.role) is str and bool(options.role)
                and valid_digest(options.oracle_source_sha256),
                "require a genuine isolated source-pinned V3 original worker")
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
            "status": "FAIL", "error_type": type(error).__name__,
            "error": str(error), "complete_traceback": traceback.format_exc(),
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED",
        }))
        sys.stderr.buffer.flush()
        raise SystemExit(1) from error
