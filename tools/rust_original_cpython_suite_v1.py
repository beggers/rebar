#!/usr/bin/env python3
"""Run the literal frozen CPython 3.14.6 original regular-expression tests."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import contextlib
import hashlib
import importlib
from importlib.machinery import EXTENSION_SUFFIXES, ExtensionFileLoader
import importlib.util
import io
import json
import locale
import multiprocessing
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from typing import Any, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
)
UPSTREAM_LIB = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-upstream-source/"
    "Python-3.14.6/Lib",
)
TEST_SOURCE = UPSTREAM_LIB / "test/test_re.py"
TEST_SOURCE_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
TEST_PACKAGE_SOURCE = UPSTREAM_LIB / "test/__init__.py"
TEST_PACKAGE_SHA256 = (
    "836cdb388117cf81e78d9fa2a141cca1b14b0179733322e710067749a1b16fe9"
)
SUPPORT_SOURCE = UPSTREAM_LIB / "test/support/__init__.py"
SUPPORT_SHA256 = (
    "519f9d36eccf2fda59f78c3480bb4b6e35b2ecb51551f11e0ac03ecbfa503159"
)
WARNINGS_HELPER_SOURCE = UPSTREAM_LIB / "test/support/warnings_helper.py"
WARNINGS_HELPER_SHA256 = (
    "fc02de4d91bae3988079e3fb3fec3da96ae467fd548295745c2846af179f3870"
)
CORPUS_SOURCE = UPSTREAM_LIB / "test/re_tests.py"
CORPUS_SHA256 = (
    "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab"
)
SCHEMA = "rebar-original-cpython-re-full-methods-v1"
METHOD_MATRIX_SHA256 = (
    "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
)
BASELINE_RECORDS_SHA256 = (
    "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
)
ORIGINAL_METHOD_COUNT = 165
PUBLIC_METHOD_COUNT = 152
PRIVATE_WAIVER_COUNT = 13
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_WORKER_BYTES = 64 * 1024 * 1024
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
PRIVATE_CLASS_REASONS = {
    "DebugTests": (
        "CPython-only textual disassembly of private matching opcodes"
    ),
    "ImplementationTest": (
        "private CPython regex compiler, _sre, type internals, "
        "and deprecated private implementation modules"
    ),
}
EXPECTED_CLASS_COUNTS = {
    "ReTests": 139,
    "DebugTests": 4,
    "PatternReprTests": 11,
    "ImplementationTest": 9,
    "ExternalTests": 2,
}

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


class OriginalSuiteError(Exception):
    """Preserve a genuine original-source, worker, or native-owner failure."""


class OriginalWorkerFailure(OriginalSuiteError):
    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


class ForbiddenOriginalMatcher(OriginalSuiteError):
    """An original CPython regex engine escaped into the Rust-only worker."""


class BlockedMatcher(types.ModuleType):
    def __getattr__(self, name: str) -> Any:
        raise ForbiddenOriginalMatcher(
            "a cached original CPython matcher was used: " + name,
        )


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OriginalSuiteError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return type(value) is str and len(value) == 64 \
        and len(set(value)) > 1 \
        and all(letter in "0123456789abcdef" for letter in value)


def verify_runtime(*, candidate: bool = False) -> None:
    expected_source = str(ROOT / SOURCE_RELATIVE)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.realpath(str(ROOT)) == str(ROOT)
            and os.path.abspath(__file__) == expected_source
            and os.path.realpath(__file__) == expected_source
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
            "use only the actual frozen root, original suite, and CPython 3.14.6")
    if not candidate:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "a Rust candidate entered the original-only suite controller")


def read_exact(path: Path, expected: str, *, maximum: int) -> bytes:
    require(isinstance(path, Path) and path.is_absolute()
            and valid_digest(expected)
            and type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES
            and os.path.realpath(str(path)) == str(path),
            "an exact no-symlink frozen original source is mandatory")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= maximum,
                "an authentic frozen original source is not a regular file")
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            item = os.read(descriptor, min(remaining, 1_048_576))
            require(type(item) is bytes and bool(item),
                    "a frozen original suite prerequisite was truncated")
            chunks.append(item)
            remaining -= len(item)
        require(os.read(descriptor, 1) == b"",
                "a frozen original prerequisite changed while being read")
        latest = os.fstat(descriptor)
        require(latest.st_dev == info.st_dev and latest.st_ino == info.st_ino
                and latest.st_size == info.st_size,
                "a frozen original source inode changed during authentication")
    finally:
        os.close(descriptor)
    raw = b"".join(chunks)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "the literal original CPython source changed: " + str(path))
    return raw


def authenticate_original_sources() -> bytes:
    verify_runtime()
    original = read_exact(TEST_SOURCE, TEST_SOURCE_SHA256,
                          maximum=MAX_SOURCE_BYTES)
    for path, expected in (
        (TEST_PACKAGE_SOURCE, TEST_PACKAGE_SHA256),
        (SUPPORT_SOURCE, SUPPORT_SHA256),
        (WARNINGS_HELPER_SOURCE, WARNINGS_HELPER_SHA256),
        (CORPUS_SOURCE, CORPUS_SHA256),
    ):
        read_exact(path, expected, maximum=MAX_SOURCE_BYTES)
    return original


def build_matrix() -> list[dict[str, Any]]:
    raw = authenticate_original_sources()
    try:
        source = raw.decode("utf-8")
        original = ast.parse(source, filename=str(TEST_SOURCE))
    except (UnicodeError, SyntaxError) as error:
        raise OriginalSuiteError(
            "the exact frozen original CPython test source cannot be parsed",
        ) from error
    records: list[dict[str, Any]] = []
    for item in original.body:
        if not isinstance(item, ast.ClassDef):
            continue
        for method in item.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    or not method.name.startswith("test_"):
                continue
            identity = item.name + "." + method.name
            waived = identity in PRIVATE_METHODS
            records.append({
                "index": len(records),
                "test": identity,
                "class": item.name,
                "method": method.name,
                "source_ast_sha256": hashlib.sha256(
                    ast.dump(method, include_attributes=False).encode("utf-8"),
                ).hexdigest(),
                "classification": "named-private-waiver" if waived else "public",
                "waiver_reason": (
                    PRIVATE_CLASS_REASONS[item.name] if waived else None
                ),
            })
    return records


def validate_matrix(records: Any) -> str:
    require(type(records) is list and len(records) == ORIGINAL_METHOD_COUNT
            and len({row["test"] for row in records}) == ORIGINAL_METHOD_COUNT
            and digest(records) == METHOD_MATRIX_SHA256
            and records == build_matrix(),
            "all 165 source-ordered literal original methods are mandatory")
    counts: dict[str, int] = {}
    public = 0
    private: list[str] = []
    for index, row in enumerate(records):
        require(type(row) is dict and row.get("index") == index
                and valid_digest(row.get("source_ast_sha256")),
                "an original method identity or source AST was substituted")
        counts[row["class"]] = counts.get(row["class"], 0) + 1
        if row["classification"] == "public":
            public += 1
            require(row["waiver_reason"] is None,
                    "a real original public method was silently waived")
        else:
            require(row["classification"] == "named-private-waiver"
                    and row["test"] in PRIVATE_METHODS
                    and row["class"] in PRIVATE_CLASS_REASONS
                    and row["waiver_reason"]
                    == PRIVATE_CLASS_REASONS[row["class"]],
                    "an unnamed original private waiver was injected")
            private.append(row["test"])
    require(counts == EXPECTED_CLASS_COUNTS
            and public == PUBLIC_METHOD_COUNT
            and tuple(private) == PRIVATE_METHODS
            and len(private) == PRIVATE_WAIVER_COUNT,
            "the authentic 152 public / 13 exact private original methods changed")
    return METHOD_MATRIX_SHA256


def capture_stream(text: str) -> dict[str, Any]:
    require(type(text) is str,
            "an authentic complete original stdout or stderr is required")
    raw = text.encode("utf-8", "surrogatepass")
    require(len(raw) <= MAX_WORKER_BYTES,
            "the complete original-method process output exceeded its bound")
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


@contextlib.contextmanager
def authentic_private_locales() -> Iterator[dict[str, Any]]:
    localedef = shutil.which("localedef")
    require(localedef == "/usr/bin/localedef"
            and os.path.realpath(localedef) == localedef,
            "the authentic original private-locale compiler is unavailable")
    previous_locale = locale.setlocale(locale.LC_CTYPE)
    previous_path = os.environ.get("LOCPATH")
    evidence: dict[str, Any] = {
        "actual_localedef_executable": localedef,
        "private_temporary_directories_created": 1,
        "private_locale_outputs_created": 2,
        "actual_localedef_workers": 2,
        "iso_8859_1_verified": False,
        "utf_8_verified": False,
        "system_locales_installed": False,
        "workspace_files_written": 0,
        "temporary_directory_removed": False,
    }
    temporary_path: str | None = None
    try:
        with tempfile.TemporaryDirectory(
            prefix="rebar-rust-original-cpython-v1-locales-", dir="/tmp",
        ) as temporary:
            temporary_path = temporary
            for encoding, name, key in (
                ("ISO-8859-1", "en_US.iso88591", "iso_8859_1_verified"),
                ("UTF-8", "en_US.utf8", "utf_8_verified"),
            ):
                result = subprocess.run(
                    [localedef, "--no-archive", "-i", "en_US", "-f", encoding,
                     str(Path(temporary) / name)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    check=False,
                )
                if result.returncode != 0:
                    raise OriginalWorkerFailure(
                        "the actual required original locale could not be compiled",
                        {
                            "locale": name,
                            "encoding": encoding,
                            "returncode": result.returncode,
                            "stdout": capture_stream(
                                result.stdout.decode("utf-8", "replace"),
                            ),
                            "stderr": capture_stream(
                                result.stderr.decode("utf-8", "replace"),
                            ),
                            "temporary_artifacts": dict(evidence),
                        },
                    )
            os.environ["LOCPATH"] = temporary
            for name, key in (
                ("en_US.iso88591", "iso_8859_1_verified"),
                ("en_US.utf8", "utf_8_verified"),
            ):
                try:
                    locale.setlocale(locale.LC_CTYPE, name)
                except locale.Error as error:
                    raise OriginalWorkerFailure(
                        "a genuinely compiled original locale was not usable",
                        {"locale": name, "error": str(error),
                         "temporary_artifacts": dict(evidence)},
                    ) from error
                evidence[key] = True
            locale.setlocale(locale.LC_CTYPE, previous_locale)
            yield evidence
    finally:
        locale.setlocale(locale.LC_CTYPE, previous_locale)
        if previous_path is None:
            os.environ.pop("LOCPATH", None)
        else:
            os.environ["LOCPATH"] = previous_path
        if temporary_path is not None:
            evidence["temporary_directory_removed"] = not os.path.exists(
                temporary_path,
            )


def normalize_test_result(
    requirement: Mapping[str, Any], result: unittest.TestResult,
) -> dict[str, Any]:
    failures = list(result.failures)
    errors = list(result.errors)
    skipped = list(result.skipped)
    unexpected = list(getattr(result, "unexpectedSuccesses", ()))
    expected_failures = list(getattr(result, "expectedFailures", ()))
    require(result.testsRun == 1 and not unexpected and not expected_failures,
            "an original test method was silently omitted or reclassified")
    if failures or errors:
        status = "FAIL"
    elif skipped:
        status = "SKIP"
    else:
        status = "PASS"
    return {
        "test": requirement["test"],
        "source_ast_sha256": requirement["source_ast_sha256"],
        "status": status,
        "tests_run": result.testsRun,
        "failure_count": len(failures),
        "error_count": len(errors),
        "skip_count": len(skipped),
        "failure_tracebacks": [trace for _, trace in failures],
        "error_tracebacks": [trace for _, trace in errors],
        "skip_reasons": [reason for _, reason in skipped],
    }


def _read_owned_binary(path: Path, expected: str) -> dict[str, Any]:
    raw = read_exact(path, expected, maximum=MAX_BINARY_BYTES)
    info = os.stat(path, follow_symlinks=False)
    require(stat.S_ISREG(info.st_mode),
            "the exact native Rust original-method owner was substituted")
    return {
        "relative": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "device": info.st_dev,
        "inode": info.st_ino,
    }


def authenticate_candidate(pins: Mapping[str, str]) -> tuple[Any, dict[str, Any]]:
    require(type(pins) is dict
            and set(pins) == {"source", "native_engine", "native_bridge"}
            and all(valid_digest(item) for item in pins.values()),
            "all three externally frozen native Rust owner pins are mandatory")
    source = ROOT / "candidates/rust_candidate.py"
    source_bytes = read_exact(source, pins["source"], maximum=MAX_SOURCE_BYTES)
    engine = _read_owned_binary(
        ROOT / "candidates/_rust_engine.so", pins["native_engine"],
    )
    adapter = importlib.import_module("candidates.rust_candidate")
    require(adapter.__name__ == "candidates.rust_candidate"
            and type(adapter.__file__) is str
            and os.path.abspath(adapter.__file__) == str(source)
            and os.path.realpath(adapter.__file__) == str(source),
            "the exact owned original-suite Rust adapter was substituted")
    bridge = sys.modules.get("candidates._rust_bridge")
    require(isinstance(bridge, types.ModuleType)
            and bridge.__name__ == "candidates._rust_bridge",
            "the exact native CPython bridge did not load")
    bridge_file = getattr(bridge, "__file__", None)
    require(type(bridge_file) is str
            and os.path.realpath(bridge_file) == bridge_file
            and os.path.commonpath((str(ROOT / "candidates"), bridge_file))
            == str(ROOT / "candidates")
            and any(bridge_file.endswith(item) for item in EXTENSION_SUFFIXES),
            "the genuine owned native bridge path was forged")
    native_bridge = _read_owned_binary(Path(bridge_file), pins["native_bridge"])
    specification = getattr(bridge, "__spec__", None)
    loader = getattr(specification, "loader", None)
    require(specification is not None
            and getattr(specification, "name", None) == "candidates._rust_bridge"
            and getattr(specification, "origin", None) == bridge_file
            and isinstance(loader, ExtensionFileLoader)
            and getattr(loader, "name", None) == "candidates._rust_bridge"
            and getattr(loader, "path", None) == bridge_file,
            "the exact loaded native Rust bridge owner was substituted")
    return adapter, {
        "source": {
            "relative": "candidates/rust_candidate.py",
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "bytes": len(source_bytes),
        },
        "native_engine": engine,
        "native_bridge": native_bridge,
    }


def is_original_matcher_value(value: Any, originals: tuple[Any, ...]) -> bool:
    if any(value is item for item in originals):
        return True
    owner = getattr(value, "__module__", None)
    if type(owner) is str and (
        owner == "re" or owner.startswith("re.") or owner == "_sre"
        or owner in ("sre_compile", "sre_parse", "sre_constants")
    ):
        return True
    bound = getattr(value, "__self__", None)
    if bound is not None:
        bound_owner = getattr(type(bound), "__module__", None)
        if type(bound_owner) is str and (
            bound_owner == "re" or bound_owner.startswith("re.")
            or bound_owner == "_sre"
        ):
            return True
    value_owner = getattr(type(value), "__module__", None)
    return type(value_owner) is str and (
        value_owner == "re" or value_owner.startswith("re.")
        or value_owner == "_sre"
    )


def forbid_captured_original_matchers(
    value: Any, originals: tuple[Any, ...], label: str,
    *, visited: set[int] | None = None, depth: int = 0,
) -> None:
    require(depth <= 12,
            "the owned Rust matcher graph exceeded its authenticated depth")
    if visited is None:
        visited = set()
    identity = id(value)
    if identity in visited:
        return
    visited.add(identity)
    require(len(visited) <= 20_000,
            "the owned Rust matcher graph exceeded its authenticated bound")
    if is_original_matcher_value(value, originals):
        raise ForbiddenOriginalMatcher(
            "a captured original CPython matcher escaped into " + label,
        )
    if isinstance(value, types.ModuleType):
        if value.__name__ == "candidates.rust_candidate" \
                or value.__name__.startswith("candidates.rust_candidate."):
            for name, item in tuple(vars(value).items()):
                if name in ("__builtins__", "__loader__", "__spec__"):
                    continue
                forbid_captured_original_matchers(
                    item, originals, label + "." + name,
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
                    item, originals, label + "." + name + "[" + str(index) + "]",
                    visited=visited, depth=depth + 1,
                )
        return
    if isinstance(value, dict):
        for index, (key, item) in enumerate(tuple(value.items())):
            require(index < 20_000,
                    "the owned Rust matcher dictionary exceeds its audit bound")
            forbid_captured_original_matchers(
                key, originals, label + ".key[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )
            forbid_captured_original_matchers(
                item, originals, label + "[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )
        return
    if isinstance(value, (tuple, list, set, frozenset)):
        for index, item in enumerate(tuple(value)):
            forbid_captured_original_matchers(
                item, originals, label + "[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )


@contextlib.contextmanager
def original_regex_guard(
    baseline: Any, pins: Mapping[str, str], *, candidate_loader: Any = None,
) -> Iterator[dict[str, Any]]:
    require(type(baseline) is types.ModuleType
            and sys.modules.get("re") is baseline
            and type(pins) is dict,
            "capture the actual original matcher before native authentication")
    blocked_names = ("_sre", "sre_compile", "sre_parse", "sre_constants")
    descendants = {
        name: value for name, value in tuple(sys.modules.items())
        if (name.startswith("re.") or name in blocked_names)
        and isinstance(value, types.ModuleType)
    }
    require(all(name in descendants for name in (
        "re._compiler", "re._parser", "re._casefix", "re._constants", "_sre",
    )), "authenticate every actual original regex and native _sre module")
    maxgroups = getattr(descendants["re._constants"], "MAXGROUPS", None)
    require(type(maxgroups) is int,
            "the literal original MAXGROUPS constant was substituted")
    case_module = sys.modules.get("unittest.case")
    require(isinstance(case_module, types.ModuleType)
            and getattr(case_module, "re", None) is baseline
            and getattr(case_module, "TestCase", None) is unittest.TestCase,
            "capture genuine unittest assertions before native authentication")
    real_assert_regex = unittest.TestCase.assertRegex
    real_assert_not_regex = unittest.TestCase.assertNotRegex
    sentinel = BlockedMatcher("blocked_original_cpython_regex")
    shim = types.ModuleType("re._constants")
    shim.MAXGROUPS = maxgroups
    shim.__package__ = "re"
    shim.__loader__ = None
    shim.__spec__ = importlib.machinery.ModuleSpec("re._constants", None)
    originals = (baseline, *descendants.values())
    holders: list[tuple[types.ModuleType, str, Any]] = []
    for module in tuple(sys.modules.values()):
        if not isinstance(module, types.ModuleType) \
                or any(module is original for original in originals):
            continue
        try:
            values = tuple(vars(module).items())
        except (TypeError, ValueError):
            continue
        for name, value in values:
            if any(value is original for original in originals) \
                    or callable(value) \
                    and is_original_matcher_value(value, originals):
                holders.append((module, name, value))
    previous_import = builtins.__import__
    previous_import_module = importlib.import_module
    candidate: types.ModuleType | None = None
    native_provenance: dict[str, Any] | None = None

    def forbidden(name: str) -> None:
        raise ForbiddenOriginalMatcher(
            "the original CPython matcher is forbidden before and after "
            "native authentication: " + name,
        )

    def resolve_name(name: str, package: Any, level: int = 0) -> str:
        require(type(name) is str and type(level) is int and level >= 0,
                "an invalid guarded regex import was attempted")
        if not level and not name.startswith("."):
            return name
        require(type(package) is str and bool(package),
                "a relative matcher import lacks its authentic package")
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
                    "a relative matcher import concealed its package")
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
        require(builtins.__import__ is guarded_import
                and importlib.import_module is guarded_import_module
                and sys.modules.get("re") is (
                    sentinel if candidate is None else candidate
                ) and sys.modules.get("re._constants") is shim,
                "the continuous pre-import original matcher quarantine escaped")
        for name, value in tuple(sys.modules.items()):
            if name == "re._constants":
                require(value is shim,
                        "the exact MAXGROUPS-only constant shim was replaced")
            elif name.startswith("re.") or name in blocked_names:
                require(value is sentinel,
                        "a cached original regex or native engine escaped: " + name)
        for holder, name, original in holders:
            expected = candidate if original is baseline \
                and candidate is not None else sentinel
            require(vars(holder).get(name) is expected,
                    "a cached original matcher module or callable escaped: "
                    + holder.__name__ + "." + name)
        require(unittest.TestCase.assertRegex is real_assert_regex
                and unittest.TestCase.assertNotRegex is real_assert_not_regex
                and sys.modules.get("unittest.case") is case_module
                and case_module.TestCase is unittest.TestCase
                and case_module.re is (
                    sentinel if candidate is None else candidate
                ), "an actual original unittest assertion or candidate was altered")

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
            loader = lambda: authenticate_candidate(pins)
        require(callable(loader),
                "an authenticated pre-quarantine native adapter loader is required")
        forbid_captured_original_matchers(loader, originals, "native adapter loader")
        loaded = loader()
        require(type(loaded) is tuple and len(loaded) == 2
                and type(loaded[0]) is types.ModuleType
                and type(loaded[1]) is dict,
                "the quarantined native adapter did not authenticate exactly")
        loaded_candidate, loaded_native_provenance = loaded
        forbid_captured_original_matchers(
            loaded_candidate, originals, "authenticated native adapter",
        )
        candidate = loaded_candidate
        native_provenance = loaded_native_provenance
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
    require(role in ("reference_a", "reference_b", "candidate_reference", "rust")
            and engine in ("stdlib", "rust") and valid_digest(source_pin),
            "only an independently isolated frozen original role is permitted")
    controller_bytes = read_exact(
        ROOT / SOURCE_RELATIVE, source_pin, maximum=MAX_SOURCE_BYTES,
    )
    require(hashlib.sha256(controller_bytes).hexdigest() == source_pin,
            "the frozen original-method controller source changed")
    matrix = build_matrix()
    validate_matrix(matrix)
    public_matrix = [row for row in matrix if row["classification"] == "public"]
    methods = multiprocessing.get_all_start_methods()
    require("fork" in methods,
            "the literal original GH94675 regression requires genuine fork")
    multiprocessing.set_start_method("fork", force=True)
    require(multiprocessing.get_start_method() == "fork",
            "the genuine original multiprocessing fork was not selected")
    previous_path = list(sys.path)
    previous_test = sys.modules.get("test.test_re")
    output = io.StringIO()
    errors = io.StringIO()
    records: list[dict[str, Any]] = []
    native_provenance: dict[str, Any] | None = None
    guard_summary: dict[str, Any] | None = None
    locale_evidence: dict[str, Any]
    try:
        sys.path.insert(1, str(UPSTREAM_LIB))
        support = importlib.import_module("test.support")
        helper = importlib.import_module("test.support.warnings_helper")
        corpus = importlib.import_module("test.re_tests")
        require(os.path.realpath(support.__file__) == str(SUPPORT_SOURCE)
                and os.path.realpath(helper.__file__)
                == str(WARNINGS_HELPER_SOURCE)
                and os.path.realpath(corpus.__file__) == str(CORPUS_SOURCE)
                and support.use_resources is None
                and support.real_max_memuse == 0
                and support.is_resource_enabled("cpu")
                and len(corpus.tests) == 403 and len(corpus.benchmarks) == 11,
                "the authentic upstream original support or 403/11 corpus changed")
        baseline = importlib.import_module("re")
        require(baseline.__name__ == "re"
                and os.path.realpath(baseline.__file__) == str(PINNED_STDLIB_RE),
                "the exact original pinned CPython matcher was substituted")
        if engine == "rust":
            require(pins is not None,
                    "all actual frozen candidate owner pins are required")
            guard: Any = original_regex_guard(baseline, pins)
        else:
            require(pins is None and not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ), "an original-only reference imported Rust")
            guard = contextlib.nullcontext(None)

        with authentic_private_locales() as locale_evidence:
            with guard as active_guard:
                if active_guard is not None:
                    native_provenance = active_guard["native_provenance"]
                specification = importlib.util.spec_from_file_location(
                    "test.test_re", str(TEST_SOURCE),
                )
                require(specification is not None
                        and specification.loader is not None,
                        "the literal unchanged original test source cannot load")
                module = importlib.util.module_from_spec(specification)
                sys.modules["test.test_re"] = module
                with contextlib.redirect_stdout(output):
                    with contextlib.redirect_stderr(errors):
                        specification.loader.exec_module(module)
                        require(os.path.realpath(module.__file__) == str(TEST_SOURCE),
                                "the actual original test source was substituted")
                        for requirement in public_matrix:
                            if active_guard is not None:
                                active_guard["verify"]()
                                active_guard["actual_method_guard_checks"] += 1
                            cls = getattr(module, requirement["class"])
                            actual_case = cls(requirement["method"])
                            actual_result = unittest.TestResult()
                            actual_case.run(actual_result)
                            records.append(normalize_test_result(
                                requirement, actual_result,
                            ))
                            if active_guard is not None:
                                active_guard["verify"]()
                                active_guard["actual_method_guard_checks"] += 1
                if active_guard is not None:
                    require(active_guard["actual_method_guard_checks"]
                            == 2 * PUBLIC_METHOD_COUNT,
                            "an actual original method lost its native owner guard")
                    guard_summary = {
                        key: value for key, value in active_guard.items()
                        if key not in ("verify", "candidate", "native_provenance")
                    }
        require(locale_evidence.get("temporary_directory_removed") is True
                and locale_evidence.get("iso_8859_1_verified") is True
                and locale_evidence.get("utf_8_verified") is True,
                "actual original private locales were not restored and removed")
    finally:
        sys.path[:] = previous_path
        if previous_test is None:
            sys.modules.pop("test.test_re", None)
        else:
            sys.modules["test.test_re"] = previous_test

    require(len(records) == PUBLIC_METHOD_COUNT,
            "a genuine original public method was omitted")
    counts = {
        "pass": sum(row["status"] == "PASS" for row in records),
        "skip": sum(row["status"] == "SKIP" for row in records),
        "failure": sum(row["status"] == "FAIL" for row in records),
    }
    return {
        "schema": SCHEMA + "-isolated-original-worker",
        "status": "PASS" if counts == {
            "pass": 151, "skip": 1, "failure": 0,
        } else "FAIL",
        "python": "3.14.6",
        "role": role,
        "engine": engine,
        "pid": os.getpid(),
        "controller_source_sha256": source_pin,
        "original_source_sha256": TEST_SOURCE_SHA256,
        "original_support_sha256": SUPPORT_SHA256,
        "original_warnings_helper_sha256": WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": CORPUS_SHA256,
        "matrix_sha256": METHOD_MATRIX_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "records_sha256": digest(records),
        "records": records,
        "pass_count": counts["pass"],
        "skip_count": counts["skip"],
        "failure_count": counts["failure"],
        "native_provenance": native_provenance,
        "matcher_guard": guard_summary,
        "multiprocessing_start_method": multiprocessing.get_start_method(),
        "original_bigmem_dry_run": True,
        "original_bigmem_maximum_size": 5_147,
        "actual_private_locales": locale_evidence,
        "captured_original_stdout": capture_stream(output.getvalue()),
        "captured_original_stderr": capture_stream(errors.getvalue()),
        "actual_candidate_workers": 0 if engine == "stdlib" else 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def unique_json(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        require(type(name) is str and name not in result,
                "duplicate original worker evidence is forbidden")
        result[name] = value
    return result


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_WORKER_BYTES,
            "complete actual original process stdout is mandatory: " + label)
    try:
        document = json.loads(
            raw, object_pairs_hook=unique_json,
            parse_constant=lambda value: (_ for _ in ()).throw(
                OriginalSuiteError("nonfinite original evidence is forbidden"),
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise OriginalSuiteError(
            "the actual complete original worker stdout is invalid: " + label,
        ) from error
    require(type(document) is dict and canonical(document) == raw,
            "the actual original worker output was truncated or forged")
    return document


def current_source_sha256() -> str:
    path = ROOT / SOURCE_RELATIVE
    require(os.path.realpath(path) == str(path),
            "the frozen original-suite controller path was substituted")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= MAX_SOURCE_BYTES,
                "the frozen original-suite controller is not a regular file")
        hasher = hashlib.sha256()
        remaining = info.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the frozen original-suite source was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "the frozen original-suite source grew during authentication")
        return hasher.hexdigest()
    finally:
        os.close(descriptor)


def validate_worker_document(
    document: Any, role: str, engine: str, source_pin: str,
    process_pid: int,
) -> dict[str, Any]:
    require(type(document) is dict and valid_digest(source_pin),
            "the complete genuine source-pinned original worker is mandatory")
    checks: dict[str, Any] = {
        "schema": SCHEMA + "-isolated-original-worker",
        "python": "3.14.6",
        "role": role,
        "engine": engine,
        "pid": process_pid,
        "controller_source_sha256": source_pin,
        "original_source_sha256": TEST_SOURCE_SHA256,
        "original_support_sha256": SUPPORT_SHA256,
        "original_warnings_helper_sha256": WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": CORPUS_SHA256,
        "matrix_sha256": METHOD_MATRIX_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "multiprocessing_start_method": "fork",
        "original_bigmem_dry_run": True,
        "original_bigmem_maximum_size": 5_147,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }
    for name, value in checks.items():
        require(document.get(name) == value,
                "a full original-worker observation changed: " + name)
    records = document.get("records")
    public = [row for row in build_matrix()
              if row["classification"] == "public"]
    require(type(records) is list and len(records) == PUBLIC_METHOD_COUNT
            and document.get("records_sha256") == digest(records),
            "a genuine original public method or complete vector was omitted")
    for requirement, observed in zip(public, records, strict=True):
        require(type(observed) is dict
                and observed.get("test") == requirement["test"]
                and observed.get("source_ast_sha256")
                == requirement["source_ast_sha256"]
                and observed.get("tests_run") == 1
                and observed.get("status") in ("PASS", "FAIL", "SKIP")
                and type(observed.get("failure_tracebacks")) is list
                and type(observed.get("error_tracebacks")) is list
                and type(observed.get("skip_reasons")) is list,
                "an actual complete original method or traceback was forged")
    require(document.get("pass_count")
            == sum(item["status"] == "PASS" for item in records)
            and document.get("failure_count")
            == sum(item["status"] == "FAIL" for item in records)
            and document.get("skip_count")
            == sum(item["status"] == "SKIP" for item in records)
            and document.get("status") == (
                "PASS" if document.get("pass_count") == 151
                and document.get("skip_count") == 1
                and document.get("failure_count") == 0 else "FAIL"
            ), "an actual original PASS, failure, or debug skip was concealed")
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
            "the two genuine worker-only locale resources were not authenticated")
    if engine == "stdlib":
        require(document.get("actual_candidate_workers") == 0
                and document.get("native_provenance") is None
                and document.get("matcher_guard") is None,
                "an original-only reference imported a native Rust candidate")
    else:
        guard = document.get("matcher_guard")
        require(document.get("actual_candidate_workers") == 1
                and type(document.get("native_provenance")) is dict
                and type(guard) is dict
                and guard.get("actual_method_guard_checks")
                == 2 * PUBLIC_METHOD_COUNT
                and guard.get("original_matchers_blocked") is True,
                "an original method lost its actually owned native matcher")
    if document["status"] == "PASS":
        skips = [row for row in records if row["status"] == "SKIP"]
        require(len(skips) == 1
                and skips[0]["test"] == "ReTests.test_memory_leaks"
                and skips[0]["skip_reasons"] == ["requires debug build"],
                "the sole genuine original debug-only skip was substituted")
    return dict(document)


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
                "an explicit native worker requires all frozen actual owner pins")
        for option, key in (
            ("--candidate-source-sha256", "source"),
            ("--native-engine-sha256", "native_engine"),
            ("--native-bridge-sha256", "native_bridge"),
        ):
            arguments.extend((option, pins[key]))
    else:
        require(pins is None,
                "an original-only method worker cannot accept native owners")
    process = subprocess.Popen(
        arguments, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(ROOT), shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0", "LC_ALL": "C",
            "PATH": "/usr/bin:/bin",
        },
    )
    # Do not sample a monotonic timeout: the original suite is not a benchmark.
    stdout, stderr = process.communicate()
    if stderr or process.returncode not in (0, 1):
        raise OriginalWorkerFailure(
            "the genuine isolated original test process did not complete",
            {
                "role": role, "pid": process.pid,
                "returncode": process.returncode,
                "stdout": {
                    "base64": base64.b64encode(stdout).decode("ascii"),
                    "bytes": len(stdout),
                    "sha256": hashlib.sha256(stdout).hexdigest(),
                    "complete": True,
                },
                "stderr": {
                    "base64": base64.b64encode(stderr).decode("ascii"),
                    "bytes": len(stderr),
                    "sha256": hashlib.sha256(stderr).hexdigest(),
                    "complete": True,
                },
            },
        )
    document = validate_worker_document(
        decode_document(stdout, role), role, engine, source_pin, process.pid,
    )
    require(process.returncode == (0 if document["status"] == "PASS" else 1),
            "an actual original worker failure exit was misclassified")
    return document


def source_only_quarantine_controls() -> dict[str, Any]:
    baseline = importlib.import_module("re")
    native = importlib.import_module("_sre")
    require(type(baseline) is types.ModuleType
            and os.path.realpath(baseline.__file__) == str(PINNED_STDLIB_RE)
            and type(native) is types.ModuleType
            and native.__name__ == "_sre"
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "quarantine controls must use actual stdlib and zero Rust candidates")
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
    original_pattern = baseline.compile("source-only-quarantine-poison")
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
         lambda adapter=poisoned_adapter: (adapter, {"source_only": True})),
    )
    rejected: list[str] = []
    for name, poison in poisons:
        try:
            with original_regex_guard(baseline, {}, candidate_loader=poison):
                raise OriginalSuiteError(
                    "a pre-authentication original matcher poison executed: "
                    + name,
                )
        except ForbiddenOriginalMatcher:
            rejected.append(name)
        else:
            raise OriginalSuiteError(
                "an original matcher quarantine poison escaped: " + name,
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
                "an original source-only quarantine poison was not restored: "
                + name)

    synthetic = types.ModuleType("rebar_original_guard_source_control")

    def clean_source_loader() -> tuple[types.ModuleType, dict[str, bool]]:
        return synthetic, {"source_only_control": True}

    with original_regex_guard(
        baseline, {}, candidate_loader=clean_source_loader,
    ) as active:
        require(active["candidate"] is synthetic
                and active["adapter_import_quarantined"] is True
                and active["native_sre_blocked"] is True
                and active["builtins_import_guarded"] is True
                and active["importlib_import_guarded"] is True
                and builtins.__import__("re") is synthetic
                and importlib.import_module("re") is synthetic
                and original_case.re is synthetic,
                "the candidate-free source-only guarded binding did not work")
        constant = builtins.__import__(
            "re._constants", fromlist=("MAXGROUPS",),
        )
        require(constant is sys.modules["re._constants"]
                and type(constant.MAXGROUPS) is int
                and set(vars(constant)) == {
                    "__name__", "__doc__", "__package__", "__loader__",
                    "__spec__", "MAXGROUPS",
                }, "the exact original MAXGROUPS-only shim was expanded")
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
            "the source-only clean quarantine did not restore exact originals")
    return {
        "rejected_count": len(rejected),
        "rejected_names": rejected,
        "source_only_positive_controls": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "original_matchers_restored": True,
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    source_pin = current_source_sha256()
    matrix = build_matrix()
    validate_matrix(matrix)
    first = run_isolated_worker("reference_a", "stdlib", source_pin)
    second = run_isolated_worker("reference_b", "stdlib", source_pin)
    require(first["pid"] != second["pid"]
            and first["status"] == second["status"] == "PASS"
            and first["records"] == second["records"]
            and first["records_sha256"] == second["records_sha256"]
            == BASELINE_RECORDS_SHA256,
            "the two complete original 152-method references genuinely disagree")
    rejected = 0
    for index in range(30):
        omitted = list(matrix)
        omitted.pop(index)
        try:
            validate_matrix(omitted)
        except OriginalSuiteError:
            rejected += 1
        else:
            raise OriginalSuiteError("an authentic original method was omitted")
    for index in range(15):
        replaced = list(matrix)
        changed = dict(replaced[index])
        changed["test"] = "ForgedOriginal.test_substituted"
        replaced[index] = changed
        try:
            validate_matrix(replaced)
        except OriginalSuiteError:
            rejected += 1
        else:
            raise OriginalSuiteError("a forged original method was accepted")
    for invalid in (None, "", "0" * 64, "A" * 64, "g" * 64):
        require(not valid_digest(invalid),
                "a forged original source fingerprint was accepted")
        rejected += 1
    quarantine = source_only_quarantine_controls()
    require(quarantine["rejected_count"] >= 18
            and quarantine["actual_candidate_workers"] == 0
            and quarantine["actual_candidate_imports"] == 0
            and quarantine["original_matchers_restored"] is True,
            "actual pre-import source-only matcher poisons were not rejected")
    rejected += quarantine["rejected_count"]
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "controller_source_sha256": source_pin,
        "original_source_sha256": TEST_SOURCE_SHA256,
        "original_support_sha256": SUPPORT_SHA256,
        "original_warnings_helper_sha256": WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": CORPUS_SHA256,
        "matrix_sha256": METHOD_MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "actual_pass_count_per_worker": 151,
        "authentic_debug_skip_count_per_worker": 1,
        "authentic_debug_skip": "ReTests.test_memory_leaks",
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_localedef_workers": 4,
        "actual_private_temporary_directories_created": 2,
        "actual_private_locale_outputs_created": 4,
        "all_private_temporary_directories_removed": True,
        "original_multiprocessing_start_method": "fork",
        "original_bigmem_dry_run": True,
        "rejected_control_count": rejected,
        "source_only_quarantine_poison_count": quarantine["rejected_count"],
        "source_only_quarantine_poison_names": quarantine["rejected_names"],
        "source_only_quarantine_positive_controls": (
            quarantine["source_only_positive_controls"]
        ),
        "actual_candidate_imports": quarantine["actual_candidate_imports"],
        "original_matchers_restored": quarantine["original_matchers_restored"],
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def run_candidate(source_pin: str, matrix_pin: str, pins: dict[str, str]) -> dict[str, Any]:
    verify_runtime()
    require(valid_digest(source_pin)
            and source_pin == current_source_sha256()
            and matrix_pin == METHOD_MATRIX_SHA256
            and all(valid_digest(value) for value in pins.values()),
            "an explicit candidate requires all actual frozen oracle/native pins")
    matrix = build_matrix()
    validate_matrix(matrix)
    baseline = run_isolated_worker(
        "candidate_reference", "stdlib", source_pin,
    )
    require(baseline["status"] == "PASS"
            and baseline["records_sha256"] == BASELINE_RECORDS_SHA256,
            "the genuine original stdlib method reference no longer passes")
    candidate = run_isolated_worker("rust", "rust", source_pin, pins)
    require(baseline["pid"] != candidate["pid"],
            "the actual original standard and Rust roles were not independent")
    mismatches: list[dict[str, Any]] = []
    for original, observed in zip(
        baseline["records"], candidate["records"], strict=True,
    ):
        require(original["test"] == observed["test"]
                and original["source_ast_sha256"]
                == observed["source_ast_sha256"],
                "an actual original public method was replaced")
        if original != observed:
            mismatches.append({
                "test": original["test"],
                "baseline": original,
                "candidate": observed,
            })
    return {
        "schema": SCHEMA + "-actual-original-candidate-result",
        "status": "PASS" if not mismatches else "FAIL",
        "python": "3.14.6",
        "controller_source_sha256": source_pin,
        "matrix_sha256": METHOD_MATRIX_SHA256,
        "original_source_sha256": TEST_SOURCE_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(PRIVATE_METHODS),
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
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run literal, source-ordered original CPython regex methods",
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
            "pin all three exact actual original-suite Rust owner components")
    return pins


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "engine", "role", "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "an original source-only test cannot run or pin a Rust candidate")
        document = source_self_test()
    elif options.candidate:
        require(options.engine is None and options.role is None
                and valid_digest(options.oracle_source_sha256)
                and options.matrix_sha256 == METHOD_MATRIX_SHA256,
                "an actual candidate needs exact frozen original-suite pins")
        document = run_candidate(
            options.oracle_source_sha256, options.matrix_sha256,
            option_pins(options),
        )
    else:
        require(options.engine in ("stdlib", "rust")
                and type(options.role) is str and bool(options.role)
                and valid_digest(options.oracle_source_sha256),
                "a complete genuine isolated original role is mandatory")
        pins = option_pins(options) if options.engine == "rust" else None
        document = execute_original_worker(
            options.role, options.engine, options.oracle_source_sha256, pins,
        )
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OriginalWorkerFailure as error:
        sys.stderr.buffer.write(canonical({
            "schema": SCHEMA + "-complete-original-worker-failure",
            "status": "FAIL",
            "error": str(error),
            "details": error.details,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
        }))
        sys.stderr.buffer.flush()
        raise SystemExit(1) from error
    except OriginalSuiteError as error:
        print("literal original CPython suite failed closed: " + str(error),
              file=sys.stderr)
        raise SystemExit(1) from error
