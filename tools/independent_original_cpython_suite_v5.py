#!/usr/bin/env python3
"""Judge independently owned regex engines against unchanged CPython tests.

``--self-test`` authenticates the unchanged upstream test matrix and runs two
independent standard-library references, but never imports or reads a candidate.
Only ``--candidate {rust,c,zig}`` runs a candidate.  Every candidate uses the
same frozen test source, baseline, object-identity quarantine, warning-safe
guard, genuine private locales, and complete source-ordered result vectors.
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
import importlib.abc
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
import traceback
import types
from typing import Any, Callable, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SCHEMA = "rebar-independent-original-cpython-re-full-methods-v5"
PREVIOUS_ORACLE_RELATIVE = "tools/independent_original_cpython_suite_v4.py"
PREVIOUS_ORACLE_SHA256 = (
    "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3"
)
PINNED_STDLIB_CTYPES = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/ctypes/__init__.py",
)
PINNED_STDLIB_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
HARNESS_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
HARNESS_MODULE = "tools.rust_original_cpython_suite_v1"
HARNESS_SHA256 = (
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
)
IDENTITY_GUARD_RELATIVE = "tools/rust_original_cpython_suite_v2.py"
IDENTITY_GUARD_MODULE = "tools.rust_original_cpython_suite_v2"
IDENTITY_GUARD_SHA256 = (
    "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267"
)
WARNING_GUARD_RELATIVE = "tools/rust_original_cpython_suite_v3.py"
WARNING_GUARD_MODULE = "tools.rust_original_cpython_suite_v3"
WARNING_GUARD_SHA256 = (
    "55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2"
)
MATRIX_SHA256 = (
    "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
)
BASELINE_SHA256 = (
    "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
)
ORIGINAL_SOURCE_SHA256 = (
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
ORIGINAL_METHOD_COUNT = 165
PUBLIC_METHOD_COUNT = 152
PRIVATE_WAIVER_COUNT = 13
GUARD_CHECKS = 2 * PUBLIC_METHOD_COUNT
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "fancy_regex", "google_re2", "hyperscan", "onig",
    "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})
ZIG_FFI_EXPORTS = frozenset({
    "rebar_zig_compile", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory",
})


class OriginalSuiteError(Exception):
    """An unchanged original test or independently owned engine was forged."""


class SourceOnlyError(OriginalSuiteError):
    """A synthetic source control attempted a real external effect."""


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
        "candidates._vm_native",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
    ),
    "zig": FamilySpec(
        "zig", "candidates.zig_candidate", "candidates/zig_candidate.py",
        "candidates/_zig_probe.so", "candidates._zig_bridge",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        owned_ctypes=True,
    ),
}


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


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
    return (
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value)
    )


def checked_digest(value: Any, label: str) -> str:
    require(valid_digest(value), "an exact lowercase SHA-256 is required: " + label)
    return value


def verify_runtime(*, candidate: bool = False) -> None:
    expected = str(ROOT / SOURCE_RELATIVE)
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == str(ROOT)
        and os.path.realpath(str(ROOT)) == str(ROOT)
        and os.path.abspath(__file__) == expected
        and os.path.realpath(__file__) == expected
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
        "use only the exact isolated pinned CPython and frozen V5 source",
    )
    if not candidate:
        require(
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
            "a candidate entered the original-only V5 source controller",
        )


def family_spec(name: Any) -> FamilySpec:
    require(type(name) is str and name in FAMILIES,
            "select exactly one independently owned Rust, C, or Zig family")
    spec = FAMILIES[name]
    require(
        isinstance(spec, FamilySpec)
        and spec.name == name
        and spec.adapter_relative.startswith("candidates/")
        and spec.bridge_relative.startswith("candidates/")
        and spec.engine_relative.startswith("candidates/")
        and spec.adapter_module.startswith("candidates.")
        and spec.bridge_module.startswith("candidates.")
        and spec.adapter_module != spec.bridge_module
        and spec.bridge_relative.endswith(EXTENSION_SUFFIX)
        and (spec.engine_relative == spec.bridge_relative) == (name == "c")
        and spec.owned_ctypes == (name == "zig"),
        "the immutable independent native family specification was substituted",
    )
    return spec


def owned_relative(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "require an exact bounded native-owner relative path")
    parts = tuple(relative.split("/"))
    require(parts and all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative,
            "a native owner path escaped its exact frozen root")
    return parts


def read_owned(
    relative: str, expected: str, *, maximum: int,
) -> tuple[bytes, dict[str, Any]]:
    parts = owned_relative(relative)
    checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "an exact independently owned source or native size is mandatory")
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    regular_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the immutable project root is not an owned directory")
        for component in parts[:-1]:
            current = os.open(component, directory_flags, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an owned native parent was replaced with a symlink")
        descriptor = os.open(parts[-1], regular_flags, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (before.st_dev, before.st_ino)
            == (named.st_dev, named.st_ino)
            and 0 < before.st_size <= maximum,
            "an exact independently owned source or engine was substituted",
        )
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "a complete owned source or native engine was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "an independently owned artifact has a concealed suffix")
        after = os.fstat(descriptor)
        require(
            (after.st_dev, after.st_ino, after.st_size)
            == (before.st_dev, before.st_ino, before.st_size),
            "an independently owned artifact changed during authentication",
        )
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


def current_source_sha256() -> str:
    path = ROOT / SOURCE_RELATIVE
    require(os.path.realpath(str(path)) == str(path),
            "the actual independent V5 source path was substituted")
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= MAX_SOURCE_BYTES,
                "the exact independent V5 source is not a regular file")
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the exact independent V5 source was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "the exact independent V5 source grew during authentication")
        after = os.fstat(descriptor)
        require((after.st_dev, after.st_ino, after.st_size)
                == (before.st_dev, before.st_ino, before.st_size),
                "the independent V5 source changed during authentication")
        return hasher.hexdigest()
    finally:
        os.close(descriptor)


def load_frozen_oracles() -> tuple[Any, Any, Any, list[dict[str, Any]]]:
    verify_runtime()
    for relative, expected in (
        (PREVIOUS_ORACLE_RELATIVE, PREVIOUS_ORACLE_SHA256),
        (HARNESS_RELATIVE, HARNESS_SHA256),
        (IDENTITY_GUARD_RELATIVE, IDENTITY_GUARD_SHA256),
        (WARNING_GUARD_RELATIVE, WARNING_GUARD_SHA256),
    ):
        read_owned(relative, expected, maximum=MAX_SOURCE_BYTES)
    warning = importlib.import_module(WARNING_GUARD_MODULE)
    require(
        isinstance(warning, types.ModuleType)
        and warning.__name__ == WARNING_GUARD_MODULE
        and os.path.abspath(warning.__file__)
        == str(ROOT / WARNING_GUARD_RELATIVE)
        and warning.current_source_sha256() == WARNING_GUARD_SHA256
        and warning.IDENTITY_GUARD_RELATIVE == IDENTITY_GUARD_RELATIVE
        and warning.IDENTITY_GUARD_SHA256 == IDENTITY_GUARD_SHA256
        and warning.HARNESS_RELATIVE == HARNESS_RELATIVE
        and warning.HARNESS_SHA256 == HARNESS_SHA256
        and warning.MATRIX_SHA256 == MATRIX_SHA256
        and warning.BASELINE_SHA256 == BASELINE_SHA256,
        "the immutable warning-safe original V3 controller was substituted",
    )
    guard = warning.load_identity_guard()
    require(
        isinstance(guard, types.ModuleType)
        and guard.__name__ == IDENTITY_GUARD_MODULE
        and guard.current_source_sha256() == IDENTITY_GUARD_SHA256
        and guard.HARNESS_RELATIVE == HARNESS_RELATIVE
        and guard.HARNESS_SHA256 == HARNESS_SHA256
        and guard.MATRIX_SHA256 == MATRIX_SHA256
        and guard.BASELINE_SHA256 == BASELINE_SHA256,
        "the immutable original V2 object-identity guard was substituted",
    )
    harness = guard.load_original_test_harness()
    require(
        isinstance(harness, types.ModuleType)
        and harness.__name__ == HARNESS_MODULE
        and harness.current_source_sha256() == HARNESS_SHA256
        and harness.METHOD_MATRIX_SHA256 == MATRIX_SHA256
        and harness.BASELINE_RECORDS_SHA256 == BASELINE_SHA256
        and harness.ORIGINAL_METHOD_COUNT == ORIGINAL_METHOD_COUNT
        and harness.PUBLIC_METHOD_COUNT == PUBLIC_METHOD_COUNT
        and harness.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
        and harness.TEST_SOURCE_SHA256 == ORIGINAL_SOURCE_SHA256
        and harness.SUPPORT_SHA256 == ORIGINAL_SUPPORT_SHA256
        and harness.WARNINGS_HELPER_SHA256
        == ORIGINAL_WARNINGS_HELPER_SHA256
        and harness.CORPUS_SHA256 == ORIGINAL_CORPUS_SHA256,
        "the unchanged literal upstream V1 test harness was substituted",
    )
    matrix = harness.build_matrix()
    require(harness.validate_matrix(matrix) == MATRIX_SHA256
            and digest(matrix) == MATRIX_SHA256
            and len(matrix) == ORIGINAL_METHOD_COUNT,
            "all 165 actual source-ordered original methods are mandatory")
    verify_runtime()
    return warning, guard, harness, matrix



def validate_trusted_builtin_ctypes(native: Any) -> types.ModuleType:
    require(
        type(native) is types.ModuleType
        and native.__name__ == "_ctypes"
        and sys.modules.get("_ctypes") is native
        and getattr(native, "__file__", None) is None,
        "the genuine built-in CPython FFI module was substituted",
    )
    native_spec = getattr(native, "__spec__", None)
    require(
        native_spec is not None
        and getattr(native_spec, "name", None) == "_ctypes"
        and getattr(native_spec, "origin", None) == "built-in"
        and getattr(native_spec, "loader", None)
        is importlib.machinery.BuiltinImporter,
        "the genuine built-in CPython FFI loader was substituted",
    )
    native_dlopen = getattr(native, "dlopen", None)
    require(
        isinstance(native_dlopen, types.BuiltinFunctionType)
        and native_dlopen.__module__ == "_ctypes"
        and native_dlopen.__name__ == "dlopen"
        and isinstance(getattr(native, "CFuncPtr", None), type),
        "the genuine built-in CPython FFI entry points were substituted",
    )
    return native


def validate_trusted_stdlib_ctypes(
    module: Any, native: Any,
) -> dict[str, Any]:
    native = validate_trusted_builtin_ctypes(native)
    expected = str(PINNED_STDLIB_CTYPES)
    require(
        type(module) is types.ModuleType
        and module.__name__ == "ctypes"
        and sys.modules.get("ctypes") is module
        and type(getattr(module, "__file__", None)) is str
        and module.__file__ == expected,
        "the actual pinned standard-library ctypes module was substituted",
    )
    specification = getattr(module, "__spec__", None)
    loader = getattr(specification, "loader", None)
    require(
        specification is not None
        and getattr(specification, "name", None) == "ctypes"
        and getattr(specification, "origin", None) == expected
        and isinstance(loader, importlib.machinery.SourceFileLoader)
        and getattr(loader, "name", None) == "ctypes"
        and getattr(loader, "path", None) == expected,
        "the actual pinned standard ctypes source loader was substituted",
    )
    values = vars(module)
    cdll = values.get("CDLL")
    pydll = values.get("PyDLL")
    native_dlopen = getattr(native, "dlopen", None)
    require(
        isinstance(cdll, type)
        and isinstance(pydll, type)
        and getattr(cdll, "__module__", None) == "ctypes"
        and getattr(pydll, "__module__", None) == "ctypes"
        and pydll.__bases__ == (cdll,)
        and getattr(getattr(cdll, "__init__", None), "__globals__", None)
        is values
        and getattr(getattr(cdll, "__init__", None), "__code__", None)
        is not None
        and cdll.__init__.__code__.co_filename == expected
        and isinstance(native_dlopen, types.BuiltinFunctionType)
        and native_dlopen.__module__ == "_ctypes"
        and native_dlopen.__name__ == "dlopen"
        and values.get("_dlopen") is native_dlopen
        and values.get("_CFuncPtr") is getattr(native, "CFuncPtr", None),
        "the genuine pinned standard ctypes API or native entry changed",
    )
    for method in ("__init__", "__getattr__", "__getitem__", "_load_library"):
        actual = vars(cdll).get(method)
        require(isinstance(actual, types.FunctionType)
                and actual.__globals__ is values
                and actual.__code__.co_filename == expected,
                "a genuine pinned ctypes loading method changed: " + method)
    library_loader = values.get("LibraryLoader")
    require(isinstance(library_loader, type)
            and library_loader.__module__ == "ctypes",
            "the genuine standard ctypes library loader was substituted")
    for key, expected_type in (("cdll", cdll), ("pydll", pydll)):
        loader_instance = values.get(key)
        require(type(loader_instance) is library_loader
                and set(vars(loader_instance)) == {"_dlltype"}
                and vars(loader_instance)["_dlltype"] is expected_type,
                "a cached standard ctypes library loader escaped: " + key)
    pythonapi = values.get("pythonapi")
    require(type(pythonapi) is pydll,
            "the actual standard Python FFI handle was not initialized")
    items = tuple(vars(pythonapi).items())
    require(all(type(key) is str for key, _ in items),
            "the genuine standard Python FFI handle contains a forged key")
    attributes = dict(items)
    require(
        set(attributes) == {"_name", "_handle", "_FuncPtr"}
        and isinstance(attributes.get("_FuncPtr"), type)
        and issubclass(attributes["_FuncPtr"], native.CFuncPtr)
        and getattr(attributes["_FuncPtr"], "__module__", None) == "ctypes"
        and attributes.get("_name") is None
        and type(attributes.get("_handle")) is int
        and attributes["_handle"] > 0,
        "the genuine standard PyDLL(None) process handle was substituted",
    )
    return {
        "module": "ctypes",
        "source_relative": expected,
        "source_sha256": PINNED_STDLIB_CTYPES_SHA256,
        "native_module": "_ctypes",
        "native_origin": "built-in",
        "native_loader": "BuiltinImporter",
        "pythonapi_initialized": True,
        "pythonapi_process_handle": True,
        "foreign_loads_permitted": False,
    }


def preload_trusted_stdlib_ctypes(
    spec: FamilySpec, warning: Any,
) -> dict[str, Any] | None:
    if not spec.owned_ctypes:
        return None
    require(
        warning.__name__ == WARNING_GUARD_MODULE
        and warning.current_source_sha256() == WARNING_GUARD_SHA256,
        "authenticate the exact frozen source reader before FFI preload",
    )
    warning.read_frozen_source(
        PINNED_STDLIB_CTYPES, PINNED_STDLIB_CTYPES_SHA256,
    )
    previous_native = sys.modules.get("_ctypes")
    if previous_native is not None:
        validate_trusted_builtin_ctypes(previous_native)
    native = importlib.import_module("_ctypes")
    validate_trusted_builtin_ctypes(native)
    existing = sys.modules.get("ctypes")
    if existing is not None:
        validate_trusted_stdlib_ctypes(existing, native)
    module = importlib.import_module("ctypes")
    require(sys.modules.get("_ctypes") is native,
            "the trusted built-in FFI module changed while importing ctypes")
    evidence = validate_trusted_stdlib_ctypes(module, native)
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "trusted standard-library FFI preloading imported a candidate",
    )
    return evidence


def forbidden_family_module(name: Any, spec: FamilySpec) -> bool:
    if type(name) is not str or not name:
        return True
    root = name.partition(".")[0]
    if root in FORBIDDEN_ENGINE_ROOTS:
        return True
    if name == "candidates":
        return False
    if root == "candidates":
        return name not in {spec.adapter_module, spec.bridge_module}
    if root.endswith("_candidate"):
        return True
    return False


class FamilyImportBlocker(importlib.abc.MetaPathFinder):
    def __init__(self, spec: FamilySpec, evidence: dict[str, Any]) -> None:
        self.spec = spec
        self.evidence = evidence

    def find_spec(
        self, fullname: str, path: Any = None, target: Any = None,
    ) -> None:
        if forbidden_family_module(fullname, self.spec):
            self.evidence["rejected_cross_family_or_external_imports"] += 1
            raise OriginalSuiteError(
                "the candidate imported an external or sibling regex engine: "
                + str(fullname),
            )
        return None


def validate_owners(
    actual: Any, spec: FamilySpec, pins: Mapping[str, str],
) -> bool:
    if type(actual) is not dict or set(actual) != {
        "source", "native_engine", "native_bridge",
    }:
        return False
    for key, relative in (
        ("source", spec.adapter_relative),
        ("native_engine", spec.engine_relative),
        ("native_bridge", spec.bridge_relative),
    ):
        owner = actual.get(key)
        if not (
            type(owner) is dict
            and set(owner) == {"relative", "sha256", "bytes", "device", "inode"}
            and owner.get("relative") == relative
            and owner.get("sha256") == pins.get(key)
            and type(owner.get("bytes")) is int and owner["bytes"] > 0
            and type(owner.get("device")) is int and owner["device"] >= 0
            and type(owner.get("inode")) is int and owner["inode"] > 0
        ):
            return False
    return (
        (actual["native_engine"] == actual["native_bridge"])
        == (spec.name == "c")
    )


def validate_pins(pins: Any, spec: FamilySpec) -> dict[str, str]:
    require(type(pins) is dict
            and set(pins) == {"source", "native_engine", "native_bridge"}
            and all(valid_digest(item) for item in pins.values()),
            "independently pin the adapter, engine, and native Python bridge")
    require((pins["native_engine"] == pins["native_bridge"])
            == (spec.name == "c"),
            "only the C family's genuine combined engine and bridge may alias")
    return dict(pins)


def owned_class_identities(
    modules: tuple[types.ModuleType, ...], spec: FamilySpec,
) -> frozenset[int]:
    found: set[int] = set()
    for module in modules:
        for value in tuple(vars(module).values()):
            if not isinstance(value, type):
                continue
            found.add(id(value))
            for parent in value.__mro__[1:]:
                if getattr(parent, "__module__", None) in {
                    spec.adapter_module, spec.bridge_module, "re", "_sre",
                }:
                    found.add(id(parent))
    return frozenset(found)


def forbid_owned_original_matchers(
    value: Any,
    ownership: Mapping[str, Any],
    spec: FamilySpec,
    guard: Any,
    owned_classes: frozenset[int],
    label: str,
    *,
    visited: set[int] | None = None,
    depth: int = 0,
) -> None:
    require(depth <= 20,
            "the independent candidate ownership graph exceeded its depth")
    if visited is None:
        visited = set()
    identity = id(value)
    if identity in visited:
        return
    visited.add(identity)
    require(len(visited) <= 30_000,
            "the independent candidate ownership graph exceeded its bound")
    ctypes_module = sys.modules.get("ctypes")
    if type(ctypes_module) is types.ModuleType:
        cdll = vars(ctypes_module).get("CDLL")
        if isinstance(cdll, type) and type(value) is cdll:
            items = tuple(vars(value).items())
            require(all(type(name) is str for name, _ in items),
                    "an owned native FFI attribute has a forged key")
            attributes = dict(items)
            require(
                spec.owned_ctypes
                and type(attributes.get("_name")) is str
                and attributes.get("_name") == str(ROOT / spec.engine_relative)
                and type(attributes.get("_handle")) is int
                and attributes["_handle"] > 0,
                "an FFI handle is not the exact authenticated owned Zig engine",
            )
            for name, item in items:
                if name not in ("_name", "_handle"):
                    forbid_owned_original_matchers(
                        item, ownership, spec, guard, owned_classes,
                        label + ".ffi[" + str(name) + "]",
                        visited=visited, depth=depth + 1,
                    )
            return
    if guard.is_original_matcher_value(value, ownership):
        raise guard.ForbiddenOriginalMatcher(
            "a genuine captured CPython matcher escaped into " + label,
        )
    if isinstance(value, types.ModuleType):
        if forbidden_family_module(value.__name__, spec):
            raise OriginalSuiteError(
                "an independently owned graph references a sibling or external "
                "regex engine: " + value.__name__,
            )
        if value.__name__ not in {spec.adapter_module, spec.bridge_module}:
            return
        for name, item in tuple(vars(value).items()):
            if name not in ("__builtins__", "__loader__", "__spec__"):
                forbid_owned_original_matchers(
                    item, ownership, spec, guard, owned_classes,
                    label + "." + name, visited=visited, depth=depth + 1,
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
                forbid_owned_original_matchers(
                    item, ownership, spec, guard, owned_classes,
                    label + "." + name + "[" + str(index) + "]",
                    visited=visited, depth=depth + 1,
                )
        return
    if isinstance(value, types.MethodType):
        for name, item in (("function", value.__func__),
                           ("instance", value.__self__)):
            forbid_owned_original_matchers(
                item, ownership, spec, guard, owned_classes,
                label + "." + name, visited=visited, depth=depth + 1,
            )
        return
    if isinstance(value, (staticmethod, classmethod)):
        forbid_owned_original_matchers(
            value.__func__, ownership, spec, guard, owned_classes,
            label + ".function", visited=visited, depth=depth + 1,
        )
        return
    if isinstance(value, property):
        for name, item in (("get", value.fget), ("set", value.fset),
                           ("delete", value.fdel)):
            if item is not None:
                forbid_owned_original_matchers(
                    item, ownership, spec, guard, owned_classes,
                    label + "." + name, visited=visited, depth=depth + 1,
                )
        return
    if isinstance(value, type):
        if id(value) not in owned_classes:
            return
        for name, item in tuple(vars(value).items()):
            if name not in ("__dict__", "__weakref__"):
                forbid_owned_original_matchers(
                    item, ownership, spec, guard, owned_classes,
                    label + "." + name, visited=visited, depth=depth + 1,
                )
        for parent in value.__mro__[1:]:
            if id(parent) in owned_classes:
                forbid_owned_original_matchers(
                    parent, ownership, spec, guard, owned_classes,
                    label + ".base", visited=visited, depth=depth + 1,
                )
        return
    if isinstance(value, (dict, types.MappingProxyType)):
        for index, (key, item) in enumerate(tuple(value.items())):
            require(index < 20_000,
                    "an independent ownership dictionary exceeded its bound")
            forbid_owned_original_matchers(
                key, ownership, spec, guard, owned_classes,
                label + ".key[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )
            forbid_owned_original_matchers(
                item, ownership, spec, guard, owned_classes,
                label + "[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )
        return
    if isinstance(value, (tuple, list, set, frozenset)):
        for index, item in enumerate(tuple(value)):
            require(index < 20_000,
                    "an independent ownership collection exceeded its bound")
            forbid_owned_original_matchers(
                item, ownership, spec, guard, owned_classes,
                label + "[" + str(index) + "]",
                visited=visited, depth=depth + 1,
            )
        return
    if id(type(value)) in owned_classes or (
        spec.owned_ctypes
        and getattr(type(value), "__module__", None) in ("ctypes", "_ctypes")
    ):
        try:
            attributes = vars(value)
        except TypeError:
            return
        forbid_owned_original_matchers(
            attributes, ownership, spec, guard, owned_classes,
            label + ".attributes", visited=visited, depth=depth + 1,
        )


def authenticate_family_candidate(
    spec: FamilySpec, pins: Mapping[str, str],
) -> tuple[types.ModuleType, dict[str, Any]]:
    approved = validate_pins(dict(pins), spec)
    _, source = read_owned(
        spec.adapter_relative, approved["source"], maximum=MAX_SOURCE_BYTES,
    )
    _, engine = read_owned(
        spec.engine_relative, approved["native_engine"],
        maximum=MAX_BINARY_BYTES,
    )
    if spec.engine_relative == spec.bridge_relative:
        require(approved["native_engine"] == approved["native_bridge"],
                "the genuine combined C native engine was substituted")
        bridge_owner = dict(engine)
    else:
        _, bridge_owner = read_owned(
            spec.bridge_relative, approved["native_bridge"],
            maximum=MAX_BINARY_BYTES,
        )
    adapter = importlib.import_module(spec.adapter_module)
    require(type(adapter) is types.ModuleType
            and adapter.__name__ == spec.adapter_module
            and os.path.abspath(adapter.__file__)
            == str(ROOT / spec.adapter_relative)
            and os.path.realpath(adapter.__file__)
            == str(ROOT / spec.adapter_relative),
            "the exact selected independently owned Python adapter changed")
    adapter_spec = getattr(adapter, "__spec__", None)
    require(adapter_spec is not None
            and getattr(adapter_spec, "name", None) == spec.adapter_module
            and getattr(adapter_spec, "origin", None)
            == str(ROOT / spec.adapter_relative)
            and isinstance(getattr(adapter_spec, "loader", None),
                           importlib.machinery.SourceFileLoader),
            "the selected independent Python source loader was substituted")
    bridge = sys.modules.get(spec.bridge_module)
    bridge_path = str(ROOT / spec.bridge_relative)
    require(type(bridge) is types.ModuleType
            and bridge.__name__ == spec.bridge_module
            and os.path.abspath(getattr(bridge, "__file__", "")) == bridge_path
            and os.path.realpath(getattr(bridge, "__file__", "")) == bridge_path,
            "the candidate did not load its exact owned native bridge")
    bridge_spec = getattr(bridge, "__spec__", None)
    bridge_loader = getattr(bridge_spec, "loader", None)
    require(bridge_spec is not None
            and getattr(bridge_spec, "name", None) == spec.bridge_module
            and getattr(bridge_spec, "origin", None) == bridge_path
            and isinstance(bridge_loader, importlib.machinery.ExtensionFileLoader)
            and getattr(bridge_loader, "name", None) == spec.bridge_module
            and getattr(bridge_loader, "path", None) == bridge_path,
            "the chosen independently owned native extension was substituted")
    require(isinstance(getattr(adapter, "Pattern", None), type)
            and isinstance(getattr(adapter, "Match", None), type)
            and getattr(adapter, "Match", None)
            is getattr(bridge, "Match", None),
            "the selected candidate did not own its native Match and Pattern")
    for name in (
        "search", "match", "fullmatch", "findall", "finditer", "split",
        "sub", "subn", "scanner",
    ):
        require(callable(getattr(adapter.Pattern, name, None)),
                "an owned original Pattern operation is missing: " + name)
    actual = {
        "source": source,
        "native_engine": engine,
        "native_bridge": bridge_owner,
    }
    require(validate_owners(actual, spec, approved),
            "the exact independently owned three-component closure changed")
    return adapter, actual


def frame_has_candidate(spec: FamilySpec) -> bool:
    try:
        frame = sys._getframe(1)
    except (AttributeError, ValueError):
        return False
    for _ in range(64):
        if frame is None:
            return False
        if frame.f_globals.get("__name__") == spec.adapter_module:
            return True
        frame = frame.f_back
    return False


@contextlib.contextmanager
def isolated_family_imports(spec: FamilySpec) -> Iterator[dict[str, Any]]:
    evidence: dict[str, Any] = {
        "rejected_cross_family_or_external_imports": 0,
        "rejected_foreign_dynamic_loads": 0,
        "rejected_process_delegations": 0,
        "owned_ctypes_load_paths": [],
        "owned_ctypes_symbol_names": [],
    }
    blocker = FamilyImportBlocker(spec, evidence)
    state = {"armed": True}
    owned_engine = str(ROOT / spec.engine_relative)

    def audit(event: str, arguments: tuple[Any, ...]) -> None:
        if not state["armed"]:
            return
        if event == "import" and arguments and isinstance(arguments[0], str):
            if forbidden_family_module(arguments[0], spec):
                evidence["rejected_cross_family_or_external_imports"] += 1
                raise OriginalSuiteError(
                    "the candidate attempted a foreign regex engine import: "
                    + arguments[0],
                )
        elif event == "ctypes.dlopen":
            actual = arguments[0] if arguments else None
            if not (
                spec.owned_ctypes
                and type(actual) is str
                and actual == owned_engine
                and os.path.abspath(actual) == owned_engine
                and os.path.realpath(actual) == owned_engine
            ):
                evidence["rejected_foreign_dynamic_loads"] += 1
                raise OriginalSuiteError(
                    "only the selected exact owned Zig FFI engine may load",
                )
            evidence["owned_ctypes_load_paths"].append(spec.engine_relative)
        elif event in ("ctypes.dlsym", "ctypes.dlsym/handle"):
            owner = arguments[0] if arguments else None
            symbol = arguments[1] if len(arguments) > 1 else None
            ctypes_module = sys.modules.get("ctypes")
            genuine_cdll = (
                vars(ctypes_module).get("CDLL")
                if type(ctypes_module) is types.ModuleType else None
            )
            owner_items = (
                tuple(vars(owner).items())
                if isinstance(genuine_cdll, type)
                and type(owner) is genuine_cdll else ()
            )
            safe_keys = all(type(key) is str for key, _ in owner_items)
            owner_attributes = dict(owner_items) if safe_keys else {}
            if not (
                spec.owned_ctypes
                and bool(owner_items)
                and safe_keys
                and type(owner_attributes.get("_name")) is str
                and owner_attributes["_name"] == owned_engine
                and os.path.abspath(owner_attributes["_name"]) == owned_engine
                and os.path.realpath(owner_attributes["_name"]) == owned_engine
                and type(owner_attributes.get("_handle")) is int
                and owner_attributes["_handle"] > 0
                and type(symbol) is str
                and symbol in ZIG_FFI_EXPORTS
            ):
                evidence["rejected_foreign_dynamic_loads"] += 1
                raise OriginalSuiteError(
                    "a foreign or unowned native FFI symbol was requested",
                )
            evidence["owned_ctypes_symbol_names"].append(symbol)
        elif (
            event in {"os.system", "os.fork", "os.posix_spawn", "subprocess.Popen"}
            or event.startswith("os.exec")
        ) and frame_has_candidate(spec):
            evidence["rejected_process_delegations"] += 1
            raise OriginalSuiteError(
                "the independent candidate attempted process delegation: "
                + event,
            )

    sys.meta_path.insert(0, blocker)
    sys.addaudithook(audit)
    try:
        yield evidence
    finally:
        state["armed"] = False
        try:
            sys.meta_path.remove(blocker)
        except ValueError as error:
            raise OriginalSuiteError(
                "the independent candidate removed its original import guard",
            ) from error


def verify_family_isolation(
    spec: FamilySpec, candidate: types.ModuleType, owners: Mapping[str, Any],
    pins: Mapping[str, str], original_ownership: Mapping[str, Any],
    evidence: Mapping[str, Any], blocker: FamilyImportBlocker,
) -> None:
    require(sys.meta_path and sys.meta_path[0] is blocker,
            "the continuous cross-family import guard was replaced")
    require(validate_owners(owners, spec, pins),
            "the selected candidate escaped its exact native ownership")
    require(sys.modules.get(spec.adapter_module) is candidate
            and type(sys.modules.get(spec.bridge_module)) is types.ModuleType,
            "the independently owned candidate or bridge identity changed")
    for name in tuple(sys.modules):
        require(not forbidden_family_module(name, spec),
                "an external or sibling regex engine escaped: " + name)
    require(candidate.Pattern is not original_ownership["pattern_type"]
            and candidate.Match is not original_ownership["match_type"]
            and candidate.Match is getattr(
                sys.modules[spec.bridge_module], "Match", None,
            ),
            "a captured standard-library matcher or foreign bridge escaped")
    require(evidence["rejected_cross_family_or_external_imports"] == 0
            and evidence["rejected_foreign_dynamic_loads"] == 0
            and evidence["rejected_process_delegations"] == 0,
            "an independent candidate attempted forbidden regex delegation")
    for path in evidence["owned_ctypes_load_paths"]:
        require(spec.owned_ctypes and path == spec.engine_relative,
                "a ctypes loader escaped its exact owned native engine")
    for symbol in evidence["owned_ctypes_symbol_names"]:
        require(spec.owned_ctypes and symbol in ZIG_FFI_EXPORTS,
                "an owned FFI loader resolved a foreign native symbol")


@contextlib.contextmanager
def chosen_original_guard(
    baseline: Any, pins: Mapping[str, str], spec: FamilySpec, guard: Any,
    warning: Any,
) -> Iterator[dict[str, Any]]:
    approved = validate_pins(dict(pins), spec)
    trusted_ctypes = preload_trusted_stdlib_ctypes(spec, warning)
    ownership = guard.capture_original_identities(baseline)
    with isolated_family_imports(spec) as isolation:
        blocker = sys.meta_path[0]
        require(isinstance(blocker, FamilyImportBlocker)
                and blocker.spec is spec,
                "install the exact independent candidate import guard")

        def candidate_loader() -> tuple[types.ModuleType, dict[str, Any]]:
            return authenticate_family_candidate(spec, approved)

        with guard.original_regex_guard(
            baseline, approved, candidate_loader=candidate_loader,
        ) as active:
            candidate = active["candidate"]
            owners = active["native_provenance"]
            require(type(candidate) is types.ModuleType,
                    "the exact independently owned adapter was not returned")
            bridge = sys.modules.get(spec.bridge_module)
            require(type(bridge) is types.ModuleType,
                    "the exact independently owned bridge was not returned")
            native_classes = owned_class_identities((candidate, bridge), spec)
            visited: set[int] = set()
            for module in (candidate, bridge):
                forbid_owned_original_matchers(
                    module, ownership, spec, guard, native_classes,
                    spec.name + " independent native owner",
                    visited=visited,
                )
            verify_family_isolation(
                spec, candidate, owners, approved, ownership, isolation,
                blocker,
            )
            warning_verify = active["verify"]

            def verify() -> None:
                warning_verify()
                verify_family_isolation(
                    spec, candidate, owners, approved, ownership, isolation,
                    blocker,
                )

            active["verify"] = verify
            active["cross_family_imports_blocked"] = True
            active["external_regex_imports_blocked"] = True
            active["owned_native_ffi_allowed"] = spec.owned_ctypes
            active["trusted_stdlib_ctypes_preloaded"] = spec.owned_ctypes
            active["trusted_stdlib_ctypes_source_sha256"] = (
                PINNED_STDLIB_CTYPES_SHA256 if spec.owned_ctypes else None
            )
            active["trusted_stdlib_ctypes_builtin_verified"] = spec.owned_ctypes
            active["trusted_stdlib_ctypes_pythonapi_initialized"] = (
                spec.owned_ctypes
            )
            require((trusted_ctypes is not None) is spec.owned_ctypes,
                    "the actual pinned standard FFI preload was substituted")
            active["owned_ctypes_load_count"] = len(
                isolation["owned_ctypes_load_paths"],
            )
            active["owned_ctypes_symbol_count"] = len(
                isolation["owned_ctypes_symbol_names"],
            )
            try:
                yield active
            finally:
                verify()


def validate_guard(value: Any, spec: FamilySpec) -> None:
    require(type(value) is dict,
            "the complete original matcher and warning guard is mandatory")
    for name in (
        "original_matchers_blocked", "adapter_import_quarantined",
        "native_sre_blocked", "builtins_import_guarded",
        "importlib_import_guarded", "actual_object_identity_guarded",
        "warning_registry_introspection_safe",
        "warning_registry_exactly_absent", "cross_family_imports_blocked",
        "external_regex_imports_blocked",
    ):
        require(value.get(name) is True,
                "a genuine continuous original identity guard was lost: " + name)
    require(value.get("public_type_names_used_for_ownership") is False,
            "owned Python-compatible public type names were misclassified")
    require(value.get("actual_method_guard_checks") == GUARD_CHECKS
            and value.get("actual_warning_registry_guard_checks")
            == GUARD_CHECKS,
            "all 304 original identity and 304 warning checks are mandatory")
    require(value.get("owned_native_ffi_allowed") is spec.owned_ctypes,
            "the exact chosen independent native FFI policy was changed")
    require(
        value.get("trusted_stdlib_ctypes_preloaded") is spec.owned_ctypes
        and value.get("trusted_stdlib_ctypes_builtin_verified")
        is spec.owned_ctypes
        and value.get("trusted_stdlib_ctypes_pythonapi_initialized")
        is spec.owned_ctypes
        and value.get("trusted_stdlib_ctypes_source_sha256")
        == (PINNED_STDLIB_CTYPES_SHA256 if spec.owned_ctypes else None),
        "the authenticated pre-guard standard ctypes preload was changed",
    )
    for name in ("owned_ctypes_load_count", "owned_ctypes_symbol_count",
                 "cached_original_matcher_descendant_count",
                 "cached_original_holder_count"):
        number = value.get(name)
        require(type(number) is int and number >= 0,
                "an exact continuous ownership guard count was hidden: " + name)
    if not spec.owned_ctypes:
        require(value["owned_ctypes_load_count"] == 0
                and value["owned_ctypes_symbol_count"] == 0,
                "an unowned foreign FFI library escaped the selected family")


def validate_original_record(
    requirement: Mapping[str, Any], observed: Any,
) -> dict[str, Any]:
    fields = {
        "test", "source_ast_sha256", "status", "tests_run", "failure_count",
        "error_count", "skip_count", "failure_tracebacks",
        "error_tracebacks", "skip_reasons",
    }
    require(type(observed) is dict and set(observed) == fields
            and observed.get("test") == requirement["test"]
            and observed.get("source_ast_sha256")
            == requirement["source_ast_sha256"]
            and observed.get("status") in ("PASS", "FAIL", "SKIP")
            and observed.get("tests_run") == 1,
            "an original source-ordered test or full result was substituted")
    for count, vector in (
        ("failure_count", "failure_tracebacks"),
        ("error_count", "error_tracebacks"),
        ("skip_count", "skip_reasons"),
    ):
        actual = observed.get(vector)
        require(type(actual) is list
                and all(type(item) is str for item in actual)
                and type(observed.get(count)) is int
                and observed[count] == len(actual),
                "a complete original failure traceback or skip was concealed")
    expected = (
        "FAIL" if observed["failure_count"] or observed["error_count"]
        else "SKIP" if observed["skip_count"] else "PASS"
    )
    require(observed["status"] == expected
            and not (observed["skip_count"]
                     and (observed["failure_count"] or observed["error_count"])),
            "a genuine original failure or skip was misclassified")
    return observed


def validate_family_worker(
    observed: Any, spec: FamilySpec, source_pin: str, pins: Mapping[str, str],
    matrix: list[dict[str, Any]], *, pid: int | None = None,
) -> dict[str, Any]:
    require(type(observed) is dict
            and type(matrix) is list and len(matrix) == ORIGINAL_METHOD_COUNT
            and digest(matrix) == MATRIX_SHA256,
            "the complete original 165-method independent result is mandatory")
    approved = validate_pins(dict(pins), spec)
    expected = {
        "schema": SCHEMA + "-isolated-original-worker",
        "python": "3.14.6",
        "role": "candidate-" + spec.name,
        "engine": spec.name,
        "candidate_family": spec.name,
        "controller_source_sha256": source_pin,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "original_source_sha256": ORIGINAL_SOURCE_SHA256,
        "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
        "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "multiprocessing_start_method": "fork",
        "original_bigmem_dry_run": True,
        "original_bigmem_maximum_size": 5_147,
        "actual_candidate_workers": 1,
        "legacy_original_worker_role": "rust",
        "legacy_original_worker_engine": "rust",
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }
    for name, value in expected.items():
        require(observed.get(name) == value,
                "a frozen independent original observation changed: " + name)
    if pid is not None:
        require(type(pid) is int and pid > 0 and observed.get("pid") == pid,
                "the exact isolated original candidate process was forged")
    require(type(observed.get("pid")) is int and observed["pid"] > 0,
            "the independently isolated candidate process was omitted")
    private = [row["test"] for row in matrix
               if row.get("classification") == "named-private-waiver"]
    public = [row for row in matrix if row.get("classification") == "public"]
    require(len(public) == PUBLIC_METHOD_COUNT
            and len(private) == PRIVATE_WAIVER_COUNT
            and observed.get("private_waivers") == private,
            "an original public method or named private waiver was changed")
    records = observed.get("records")
    require(type(records) is list and len(records) == PUBLIC_METHOD_COUNT
            and observed.get("records_sha256") == digest(records),
            "a complete original source-ordered result was omitted")
    for requirement, actual in zip(public, records, strict=True):
        validate_original_record(requirement, actual)
    counts = {
        "pass": sum(row["status"] == "PASS" for row in records),
        "skip": sum(row["status"] == "SKIP" for row in records),
        "failure": sum(row["status"] == "FAIL" for row in records),
    }
    require(observed.get("pass_count") == counts["pass"]
            and observed.get("skip_count") == counts["skip"]
            and observed.get("failure_count") == counts["failure"]
            and observed.get("status") == (
                "PASS" if counts == {"pass": 151, "skip": 1, "failure": 0}
                else "FAIL"
            ),
            "a genuine independent original failure was concealed")
    if observed["status"] == "PASS":
        skipped = [row for row in records if row["status"] == "SKIP"]
        require(len(skipped) == 1
                and skipped[0]["test"] == "ReTests.test_memory_leaks"
                and skipped[0]["skip_reasons"] == ["requires debug build"],
                "the genuine original debug-build skip was substituted")
    require(validate_owners(observed.get("native_provenance"), spec, approved),
            "the independently selected original engine ownership was forged")
    validate_guard(observed.get("matcher_guard"), spec)
    locales = observed.get("actual_private_locales")
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
            "a genuine upstream private locale was silently replaced")
    return observed


def execute_family_worker(
    family: str, source_pin: str, matrix_pin: str, pins: Mapping[str, str],
) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(family)
    require(checked_digest(source_pin, "independent V5 source")
            == current_source_sha256()
            and matrix_pin == MATRIX_SHA256,
            "freeze the exact independent original controller and matrix")
    approved = validate_pins(dict(pins), spec)
    warning, guard, harness, matrix = load_frozen_oracles()
    previous_guard = harness.original_regex_guard

    @contextlib.contextmanager
    def family_guard(
        baseline: Any, observed_pins: Mapping[str, str],
    ) -> Iterator[dict[str, Any]]:
        require(dict(observed_pins) == approved,
                "the frozen independent original native pins were changed")
        with chosen_original_guard(
            baseline, approved, spec, guard, warning,
        ) as active:
            yield active

    try:
        with warning.installed_warning_safe_guard(guard):
            harness.original_regex_guard = family_guard
            original = harness.execute_original_worker(
                "rust", "rust", HARNESS_SHA256, approved,
            )
    finally:
        harness.original_regex_guard = previous_guard
    require(type(original) is dict
            and original.get("schema")
            == harness.SCHEMA + "-isolated-original-worker"
            and original.get("role") == "rust"
            and original.get("engine") == "rust"
            and original.get("controller_source_sha256") == HARNESS_SHA256,
            "the unchanged original-harness candidate slot was substituted")
    original.update({
        "schema": SCHEMA + "-isolated-original-worker",
        "role": "candidate-" + spec.name,
        "engine": spec.name,
        "candidate_family": spec.name,
        "controller_source_sha256": source_pin,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "legacy_original_worker_role": "rust",
        "legacy_original_worker_engine": "rust",
    })
    return validate_family_worker(
        original, spec, source_pin, approved, matrix, pid=os.getpid(),
    )


def unique_json(items: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in output,
                "duplicate complete original worker results are forbidden")
        output[key] = value
    return output


def decode_worker(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete genuine original worker output is mandatory: " + label)
    try:
        document = json.loads(
            raw, object_pairs_hook=unique_json,
            parse_constant=lambda _: (_ for _ in ()).throw(
                OriginalSuiteError("nonfinite original evidence is forbidden"),
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise OriginalSuiteError(
            "a complete independently isolated original result was invalid",
        ) from error
    require(type(document) is dict and canonical(document) == raw,
            "a complete canonical original result was silently truncated")
    return document


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve the complete independent original process output")
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def validate_encoded_stream(actual: Any, *, label: str) -> bytes:
    require(type(actual) is dict
            and set(actual) == {"base64", "bytes", "sha256", "complete"}
            and type(actual.get("base64")) is str
            and type(actual.get("bytes")) is int
            and 0 <= actual["bytes"] <= MAX_PROCESS_BYTES
            and actual.get("complete") is True
            and valid_digest(actual.get("sha256")),
            "a complete authentic original process stream was forged: " + label)
    try:
        raw = base64.b64decode(actual["base64"].encode("ascii"), validate=True)
    except (ValueError, TypeError, UnicodeError) as error:
        raise OriginalSuiteError(
            "an authentic original process stream was truncated: " + label,
        ) from error
    require(len(raw) == actual["bytes"]
            and hashlib.sha256(raw).hexdigest() == actual["sha256"],
            "an original process stream changed its complete bytes: " + label)
    return raw


def validate_isolated_process_evidence(
    actual: Any, worker: Mapping[str, Any], *, role: str,
    family: str | None, pid: int, returncode: int,
) -> dict[str, Any]:
    require(type(actual) is dict and set(actual) == {
        "role", "candidate_family", "pid", "returncode",
        "stdout", "stderr", "records_sha256", "record_count",
    } and actual.get("role") == role
            and actual.get("candidate_family") == family
            and type(pid) is int and pid > 0 and actual.get("pid") == pid
            and type(returncode) is int
            and actual.get("returncode") == returncode
            and actual.get("records_sha256") == worker.get("records_sha256")
            and actual.get("record_count") == PUBLIC_METHOD_COUNT
            and type(worker.get("records")) is list
            and len(worker["records"]) == PUBLIC_METHOD_COUNT,
            "a complete isolated original worker stream was substituted")
    stdout = validate_encoded_stream(actual.get("stdout"), label=role + " stdout")
    stderr = validate_encoded_stream(actual.get("stderr"), label=role + " stderr")
    require(stderr == b"" and stdout == canonical(dict(worker)),
            "a complete original worker vector or process stream was concealed")
    return actual


def capture_isolated_process_evidence(
    worker: Mapping[str, Any], *, role: str, family: str | None,
    pid: int, returncode: int, stdout: bytes, stderr: bytes,
) -> dict[str, Any]:
    evidence = {
        "role": role,
        "candidate_family": family,
        "pid": pid,
        "returncode": returncode,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
        "records_sha256": worker.get("records_sha256"),
        "record_count": len(worker.get("records", ())),
    }
    return validate_isolated_process_evidence(
        evidence, worker, role=role, family=family,
        pid=pid, returncode=returncode,
    )


def validate_reference_worker(
    observed: Any, role: str, source_pin: str,
    matrix: list[dict[str, Any]], *, pid: int | None = None,
) -> dict[str, Any]:
    require(role in ("reference_a", "reference_b", "candidate_reference")
            and type(observed) is dict
            and type(matrix) is list
            and len(matrix) == ORIGINAL_METHOD_COUNT
            and digest(matrix) == MATRIX_SHA256,
            "the complete V4-source-pinned standard reference is mandatory")
    expected = {
        "schema": SCHEMA + "-isolated-original-worker",
        "status": "PASS",
        "python": "3.14.6",
        "role": role,
        "engine": "stdlib",
        "candidate_family": None,
        "controller_source_sha256": source_pin,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "original_source_sha256": ORIGINAL_SOURCE_SHA256,
        "original_support_sha256": ORIGINAL_SUPPORT_SHA256,
        "original_warnings_helper_sha256": ORIGINAL_WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": ORIGINAL_CORPUS_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "records_sha256": BASELINE_SHA256,
        "pass_count": 151,
        "skip_count": 1,
        "failure_count": 0,
        "native_provenance": None,
        "matcher_guard": None,
        "multiprocessing_start_method": "fork",
        "original_bigmem_dry_run": True,
        "original_bigmem_maximum_size": 5_147,
        "actual_candidate_workers": 0,
        "legacy_original_worker_role": role,
        "legacy_original_worker_engine": "stdlib",
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }
    for name, value in expected.items():
        require(observed.get(name) == value,
                "an actual independent V5 baseline changed: " + name)
    require(type(observed.get("pid")) is int and observed["pid"] > 0,
            "the actual V5 reference process was omitted")
    if pid is not None:
        require(type(pid) is int and pid > 0 and observed["pid"] == pid,
                "the genuine isolated V5 reference process was substituted")
    public = [row for row in matrix if row.get("classification") == "public"]
    private = [row["test"] for row in matrix
               if row.get("classification") == "named-private-waiver"]
    require(len(public) == PUBLIC_METHOD_COUNT
            and len(private) == PRIVATE_WAIVER_COUNT
            and observed.get("private_waivers") == private,
            "an original V5 standard method or private waiver was hidden")
    records = observed.get("records")
    require(type(records) is list and len(records) == PUBLIC_METHOD_COUNT
            and digest(records) == BASELINE_SHA256,
            "all genuine source-ordered V5 baseline results are mandatory")
    for requirement, actual in zip(public, records, strict=True):
        validate_original_record(requirement, actual)
    skipped = [row for row in records if row["status"] == "SKIP"]
    require(len(skipped) == 1
            and skipped[0]["test"] == "ReTests.test_memory_leaks"
            and skipped[0]["skip_reasons"] == ["requires debug build"],
            "the one real V5 original debug-build skip was replaced")
    locales = observed.get("actual_private_locales")
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
            "the genuine V5 original private baseline locales were replaced")
    return observed


def execute_reference_worker(
    role: str, source_pin: str, matrix_pin: str,
) -> dict[str, Any]:
    verify_runtime()
    require(role in ("reference_a", "reference_b", "candidate_reference")
            and checked_digest(source_pin, "independent V5 reference source")
            == current_source_sha256()
            and matrix_pin == MATRIX_SHA256,
            "run only a genuinely source-pinned V5 standard reference")
    _, _, harness, matrix = load_frozen_oracles()
    original = harness.execute_original_worker(
        role, "stdlib", HARNESS_SHA256, None,
    )
    require(type(original) is dict
            and original.get("schema")
            == harness.SCHEMA + "-isolated-original-worker"
            and original.get("role") == role
            and original.get("engine") == "stdlib"
            and original.get("controller_source_sha256") == HARNESS_SHA256,
            "the unchanged upstream standard reference was substituted")
    original.update({
        "schema": SCHEMA + "-isolated-original-worker",
        "candidate_family": None,
        "controller_source_sha256": source_pin,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "legacy_original_worker_role": role,
        "legacy_original_worker_engine": "stdlib",
    })
    return validate_reference_worker(
        original, role, source_pin, matrix, pid=os.getpid(),
    )


def run_reference_worker(
    role: str, source_pin: str, matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    require(role in ("reference_a", "reference_b", "candidate_reference"),
            "choose an exact independently isolated V5 reference role")
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--role", role,
        "--oracle-source-sha256", source_pin,
        "--matrix-sha256", MATRIX_SHA256,
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
    if stderr or process.returncode != 0:
        raise OriginalSuiteError(canonical({
            "schema": SCHEMA + "-complete-isolated-reference-failure",
            "status": "FAIL", "role": role,
            "pid": process.pid, "returncode": process.returncode,
            "stdout": encode_stream(stdout),
            "stderr": encode_stream(stderr),
            "clock_samples": 0, "timing_trials_run": 0,
            "hidden_cases_read": 0, "performance": "NOT MEASURED",
        }).decode("ascii"))
    result = validate_reference_worker(
        decode_worker(stdout, role), role, source_pin, matrix,
        pid=process.pid,
    )
    process_evidence = capture_isolated_process_evidence(
        result, role=role, family=None, pid=process.pid,
        returncode=process.returncode, stdout=stdout, stderr=stderr,
    )
    result["isolated_process_evidence"] = process_evidence
    return result


def run_family_worker(
    spec: FamilySpec, source_pin: str, pins: Mapping[str, str],
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    approved = validate_pins(dict(pins), spec)
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--family", spec.name,
        "--oracle-source-sha256", source_pin,
        "--matrix-sha256", MATRIX_SHA256,
        "--candidate-source-sha256", approved["source"],
        "--native-engine-sha256", approved["native_engine"],
        "--native-bridge-sha256", approved["native_bridge"],
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
    if stderr or process.returncode not in (0, 1):
        raise OriginalSuiteError(canonical({
            "schema": SCHEMA + "-complete-isolated-worker-failure",
            "status": "FAIL", "candidate_family": spec.name,
            "pid": process.pid, "returncode": process.returncode,
            "stdout": encode_stream(stdout),
            "stderr": encode_stream(stderr),
            "clock_samples": 0, "timing_trials_run": 0,
            "hidden_cases_read": 0, "performance": "NOT MEASURED",
        }).decode("ascii"))
    result = validate_family_worker(
        decode_worker(stdout, spec.name), spec, source_pin, approved, matrix,
        pid=process.pid,
    )
    require(process.returncode == (0 if result["status"] == "PASS" else 1),
            "the actual independent original worker exit was misclassified")
    process_evidence = capture_isolated_process_evidence(
        result, role="candidate-" + spec.name, family=spec.name,
        pid=process.pid, returncode=process.returncode,
        stdout=stdout, stderr=stderr,
    )
    result["isolated_process_evidence"] = process_evidence
    return result


def run_candidate(
    family: str, source_pin: str, matrix_pin: str, pins: Mapping[str, str],
) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(family)
    require(checked_digest(source_pin, "independent V5 source")
            == current_source_sha256()
            and matrix_pin == MATRIX_SHA256,
            "pin the exact common original test source and method matrix")
    approved = validate_pins(dict(pins), spec)
    _, _, harness, matrix = load_frozen_oracles()
    baseline = run_reference_worker("candidate_reference", source_pin, matrix)
    require(baseline["status"] == "PASS"
            and baseline["records_sha256"] == BASELINE_SHA256
            and baseline["pass_count"] == 151
            and baseline["skip_count"] == 1
            and baseline["failure_count"] == 0,
            "the actual pinned original standard-library reference failed")
    candidate = run_family_worker(spec, source_pin, approved, matrix)
    require(baseline["pid"] != candidate["pid"],
            "the actual original reference and candidate were not isolated")
    mismatch: list[dict[str, Any]] = []
    for original, observed in zip(
        baseline["records"], candidate["records"], strict=True,
    ):
        require(original["test"] == observed["test"]
                and original["source_ast_sha256"]
                == observed["source_ast_sha256"],
                "an original source-ordered method was silently substituted")
        if original != observed:
            mismatch.append({
                "test": original["test"],
                "baseline": original, "candidate": observed,
            })
    return {
        "schema": SCHEMA + "-actual-original-candidate-result",
        "status": "FAIL" if mismatch else "PASS",
        "python": "3.14.6",
        "candidate_family": spec.name,
        "controller_source_sha256": source_pin,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "original_source_sha256": harness.TEST_SOURCE_SHA256,
        "original_support_sha256": harness.SUPPORT_SHA256,
        "original_warnings_helper_sha256": harness.WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": harness.CORPUS_SHA256,
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
        "isolated_process_evidence": [
            baseline["isolated_process_evidence"],
            candidate["isolated_process_evidence"],
        ],
        "mismatch_count": len(mismatch),
        "all_mismatches": mismatch,
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
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0, "file_writes": 0, "candidate_imports": 0,
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

    def deny(counter: str, reason: str) -> Callable[..., Any]:
        def blocked(*args: Any, **keywords: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyError(reason)

        return blocked

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, deny(
                "blocked_reads", "a synthetic V5 control cannot read a file",
            ))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, deny(
                "blocked_writes", "a synthetic V5 control cannot write a file",
            ))
        install(importlib, "import_module", deny(
            "blocked_imports", "a synthetic V5 control cannot import a candidate",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "a synthetic V5 control cannot import a module",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny(
                "blocked_workers", "a synthetic V5 control cannot run a worker",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "a synthetic V5 control cannot run a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns",
        ):
            install(time, name, deny(
                "blocked_clocks", "a synthetic V5 control cannot read a clock",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections", "a synthetic V5 control cannot run GC",
        ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_pins(spec: FamilySpec) -> dict[str, str]:
    source = {"rust": "12", "c": "34", "zig": "56"}[spec.name] * 32
    engine = {"rust": "78", "c": "9a", "zig": "bc"}[spec.name] * 32
    bridge = engine if spec.name == "c" else {
        "rust": "de" * 32, "zig": "ef" * 32,
    }[spec.name]
    return {"source": source, "native_engine": engine,
            "native_bridge": bridge}


def synthetic_owners(
    spec: FamilySpec, pins: Mapping[str, str],
) -> dict[str, dict[str, Any]]:
    source = {
        "relative": spec.adapter_relative, "sha256": pins["source"],
        "bytes": 113, "device": 17, "inode": 101,
    }
    engine = {
        "relative": spec.engine_relative, "sha256": pins["native_engine"],
        "bytes": 227, "device": 17, "inode": 102,
    }
    bridge = dict(engine) if spec.name == "c" else {
        "relative": spec.bridge_relative, "sha256": pins["native_bridge"],
        "bytes": 331, "device": 17, "inode": 103,
    }
    return {"source": source, "native_engine": engine,
            "native_bridge": bridge}


def synthetic_guard(spec: FamilySpec) -> dict[str, Any]:
    return {
        "cached_original_matcher_descendant_count": 5,
        "cached_original_holder_count": 7,
        "original_matchers_blocked": True,
        "adapter_import_quarantined": True,
        "native_sre_blocked": True,
        "builtins_import_guarded": True,
        "importlib_import_guarded": True,
        "actual_object_identity_guarded": True,
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": GUARD_CHECKS,
        "warning_registry_introspection_safe": True,
        "warning_registry_exactly_absent": True,
        "actual_warning_registry_guard_checks": GUARD_CHECKS,
        "cross_family_imports_blocked": True,
        "external_regex_imports_blocked": True,
        "owned_native_ffi_allowed": spec.owned_ctypes,
        "trusted_stdlib_ctypes_preloaded": spec.owned_ctypes,
        "trusted_stdlib_ctypes_builtin_verified": spec.owned_ctypes,
        "trusted_stdlib_ctypes_pythonapi_initialized": spec.owned_ctypes,
        "trusted_stdlib_ctypes_source_sha256": (
            PINNED_STDLIB_CTYPES_SHA256 if spec.owned_ctypes else None
        ),
        "owned_ctypes_load_count": 1 if spec.owned_ctypes else 0,
        "owned_ctypes_symbol_count": len(ZIG_FFI_EXPORTS)
        if spec.owned_ctypes else 0,
    }


def synthetic_worker(
    spec: FamilySpec, reference: Mapping[str, Any], source_pin: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    pins = synthetic_pins(spec)
    owners = synthetic_owners(spec, pins)
    document = copy.deepcopy(dict(reference))
    document.update({
        "schema": SCHEMA + "-isolated-original-worker",
        "role": "candidate-" + spec.name,
        "engine": spec.name,
        "candidate_family": spec.name,
        "controller_source_sha256": source_pin,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "native_provenance": owners,
        "matcher_guard": synthetic_guard(spec),
        "actual_candidate_workers": 1,
        "legacy_original_worker_role": "rust",
        "legacy_original_worker_engine": "rust",
    })
    return document, pins


def synthetic_owned_modules(
    spec: FamilySpec, ownership: Mapping[str, Any], poison: str | None,
) -> tuple[types.ModuleType, types.ModuleType]:
    candidate = types.ModuleType(spec.adapter_module)
    bridge = types.ModuleType(spec.bridge_module)
    pattern = type("Pattern", (), {"__module__": "re"})
    match = type("Match", (), {"__module__": "re"})
    scanner = type("SRE_Scanner", (), {"__module__": "_sre"})
    candidate.Pattern = pattern
    candidate.Match = match
    candidate.Scanner = scanner
    bridge.Pattern = pattern
    bridge.Match = match
    captured = ownership["baseline"].compile
    if poison == "module":
        candidate.captured_original = captured
    elif poison == "bridge":
        bridge.captured_original = captured
    elif poison == "pattern-class":
        pattern.captured_original = ownership["pattern_type"].search
    elif poison == "helper-class":
        candidate.Helper = type(
            "OwnedHelper", (), {
                "__module__": spec.adapter_module,
                "captured_original": captured,
            },
        )
    elif poison == "helper-instance":
        helper = type(
            "OwnedHelper", (), {"__module__": spec.adapter_module},
        )
        candidate.Helper = helper
        candidate.helper = helper()
        candidate.helper.captured_original = captured
    elif poison == "closure":
        def captured_closure() -> Any:
            return captured

        candidate.captured_closure = captured_closure
    elif poison == "scanner":
        candidate.scanner_reference = ownership["scanner_probe"]
    else:
        require(poison is None,
                "an exact synthetic ownership poison was substituted")
    return candidate, bridge


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    source_pin = current_source_sha256()
    warning, guard, harness, matrix = load_frozen_oracles()
    first = run_reference_worker("reference_a", source_pin, matrix)
    second = run_reference_worker("reference_b", source_pin, matrix)
    require(
        first["pid"] != second["pid"]
        and first["status"] == second["status"] == "PASS"
        and first["records"] == second["records"]
        and first["records_sha256"] == second["records_sha256"]
        == BASELINE_SHA256
        and first["pass_count"] == second["pass_count"] == 151
        and first["skip_count"] == second["skip_count"] == 1
        and first["failure_count"] == second["failure_count"] == 0,
        "the two genuinely isolated original standard references disagree",
    )
    trusted_stdlib_ctypes = preload_trusted_stdlib_ctypes(
        family_spec("zig"), warning,
    )
    require(type(trusted_stdlib_ctypes) is dict,
            "genuinely initialize trusted standard ctypes before audit controls")
    with warning.installed_warning_safe_guard(guard):
        quarantine_controls = guard.source_only_quarantine_controls()
        warning_controls = warning.warning_registry_controls(guard)
    require(
        quarantine_controls["rejected_count"] >= 24
        and quarantine_controls["source_only_owned_public_type_positive_count"]
        == 3
        and quarantine_controls["actual_candidate_workers"] == 0
        and quarantine_controls["actual_candidate_imports"] == 0
        and quarantine_controls["original_matchers_restored"] is True
        and warning_controls["source_only_warning_positive_controls"] == 1
        and warning_controls["warning_safe_rejected_count"] >= 6
        and warning_controls["warning_registry_exactly_absent"] is True
        and warning_controls["source_only_warning_filename_verified"] is True
        and warning_controls["actual_candidate_workers"] == 0
        and warning_controls["actual_candidate_imports"] == 0,
        "the actual unchanged V2 identity or V3 warning guard controls failed",
    )
    genuine_baseline = importlib.import_module("re")
    original_ownership = guard.capture_original_identities(genuine_baseline)
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a source-only independent original control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a synthetic independent original poison was duplicated")
        try:
            action()
        except (
            OriginalSuiteError, guard.ForbiddenOriginalMatcher,
            ValueError, TypeError, KeyError, OSError,
        ):
            rejected.append(name)
            return
        raise OriginalSuiteError(
            "a synthetic independent original forgery was accepted: " + name,
        )

    with source_only_boundary() as effects:
        accept("preserve-all-165-actual-original-source-methods",
               len(matrix) == ORIGINAL_METHOD_COUNT
               and digest(matrix) == MATRIX_SHA256)
        accept("preserve-all-152-public-methods-and-13-named-private-waivers",
               sum(row["classification"] == "public" for row in matrix)
               == PUBLIC_METHOD_COUNT
               and sum(row["classification"] == "named-private-waiver"
                       for row in matrix) == PRIVATE_WAIVER_COUNT)
        accept("preserve-exact-151-standard-passes-and-real-debug-skip",
               first["pass_count"] == 151 and first["skip_count"] == 1
               and first["records_sha256"] == BASELINE_SHA256)
        fixtures: dict[str, tuple[dict[str, Any], dict[str, str]]] = {}
        for name in ("rust", "c", "zig"):
            spec = family_spec(name)
            worker, pins = synthetic_worker(spec, first, source_pin)
            fixtures[name] = (worker, pins)
            accept("accept-complete-owned-" + name + "-family",
                   validate_family_worker(
                       worker, spec, source_pin, pins, matrix,
                   ) is worker)
            accept("preserve-owned-python-compatible-type-identity-" + name,
                   worker["matcher_guard"]
                   ["public_type_names_used_for_ownership"] is False)
            accept("require-all-304-identity-and-warning-checks-" + name,
                   worker["matcher_guard"]["actual_method_guard_checks"]
                   == GUARD_CHECKS
                   and worker["matcher_guard"]
                   ["actual_warning_registry_guard_checks"] == GUARD_CHECKS)
            clean_candidate, clean_bridge = synthetic_owned_modules(
                spec, original_ownership, None,
            )
            clean_classes = owned_class_identities(
                (clean_candidate, clean_bridge), spec,
            )
            clean_visited: set[int] = set()
            for module in (clean_candidate, clean_bridge):
                forbid_owned_original_matchers(
                    module, original_ownership, spec, guard, clean_classes,
                    "synthetic owned " + name, visited=clean_visited,
                )
            accept("accept-genuine-same-name-owned-pattern-match-scanner-"
                   + name,
                   clean_candidate.Pattern.__module__ == "re"
                   and clean_candidate.Match.__module__ == "re"
                   and clean_candidate.Scanner.__module__ == "_sre")
            for poison in (
                "module", "bridge", "pattern-class", "helper-class",
                "helper-instance", "closure", "scanner",
            ):
                poisoned_candidate, poisoned_bridge = synthetic_owned_modules(
                    spec, original_ownership, poison,
                )
                poisoned_classes = owned_class_identities(
                    (poisoned_candidate, poisoned_bridge), spec,
                )

                def check_poison(
                    candidate: types.ModuleType = poisoned_candidate,
                    bridge: types.ModuleType = poisoned_bridge,
                    classes: frozenset[int] = poisoned_classes,
                    actual_spec: FamilySpec = spec,
                ) -> None:
                    seen: set[int] = set()
                    for item in (candidate, bridge):
                        forbid_owned_original_matchers(
                            item, original_ownership, actual_spec, guard,
                            classes, "synthetic captured original",
                            visited=seen,
                        )

                reject("reject-real-captured-" + poison + "-" + name,
                       check_poison)
            previous_ctypes = sys.modules.get("ctypes")
            synthetic_ctypes = types.ModuleType("ctypes")

            def unexpected_ffi_lookup(self: Any, attribute: str) -> Any:
                raise OriginalSuiteError(
                    "an owned FFI handle was unsafely introspected: "
                    + attribute,
                )

            fake_cdll = type(
                "CDLL", (), {
                    "__module__": "ctypes",
                    "__getattr__": unexpected_ffi_lookup,
                },
            )
            synthetic_ctypes.CDLL = fake_cdll
            sys.modules["ctypes"] = synthetic_ctypes
            try:
                owned_handle = fake_cdll()
                vars(owned_handle).update({
                    "_name": str(ROOT / spec.engine_relative),
                    "_handle": 7,
                    "safe_cached_metadata": {"owned": True},
                })

                def check_handle(item: Any = owned_handle) -> None:
                    forbid_owned_original_matchers(
                        item, original_ownership, spec, guard,
                        frozenset(), "synthetic exact native FFI",
                    )

                if spec.owned_ctypes:
                    check_handle()
                    accept("accept-exact-owned-zig-ffi-without-dynamic-lookups",
                           vars(owned_handle)["_handle"] == 7)
                    foreign_handle = fake_cdll()
                    vars(foreign_handle).update({
                        "_name": str(ROOT / "candidates/foreign_regex.so"),
                        "_handle": 7,
                    })
                    reject("reject-foreign-zig-native-ffi-handle",
                           lambda item=foreign_handle:
                           forbid_owned_original_matchers(
                               item, original_ownership, spec, guard,
                               frozenset(), "synthetic foreign native FFI",
                           ))
                    invalid_handle = fake_cdll()
                    vars(invalid_handle).update({
                        "_name": str(ROOT / spec.engine_relative),
                        "_handle": 0,
                    })
                    reject("reject-invalid-owned-zig-native-ffi-handle",
                           lambda item=invalid_handle:
                           forbid_owned_original_matchers(
                               item, original_ownership, spec, guard,
                               frozenset(), "synthetic invalid native FFI",
                           ))
                    captured_handle = fake_cdll()
                    vars(captured_handle).update({
                        "_name": str(ROOT / spec.engine_relative),
                        "_handle": 7,
                        "captured_original":
                        original_ownership["baseline"].compile,
                    })
                    reject("reject-captured-original-in-owned-zig-ffi-handle",
                           lambda item=captured_handle:
                           forbid_owned_original_matchers(
                               item, original_ownership, spec, guard,
                               frozenset(), "synthetic captured native FFI",
                           ))
                    nested_handle = fake_cdll()
                    vars(nested_handle).update({
                        "_name": str(ROOT / spec.engine_relative),
                        "_handle": 7,
                        "cached_symbols": {
                            "captured_original_scanner":
                            original_ownership["scanner_probe"],
                        },
                    })
                    reject("reject-captured-scanner-nested-in-zig-ffi-handle",
                           lambda item=nested_handle:
                           forbid_owned_original_matchers(
                               item, original_ownership, spec, guard,
                               frozenset(), "synthetic nested native FFI",
                           ))

                    class SpoofedFfiName:
                        def __init__(self) -> None:
                            self.captured_original = (
                                original_ownership["baseline"].compile
                            )

                        def __eq__(self, other: Any) -> bool:
                            return True

                    spoofed_handle = fake_cdll()
                    vars(spoofed_handle).update({
                        "_name": SpoofedFfiName(),
                        "_handle": 7,
                    })
                    reject("reject-spoofed-zig-ffi-engine-path-identity",
                           lambda item=spoofed_handle:
                           forbid_owned_original_matchers(
                               item, original_ownership, spec, guard,
                               frozenset(), "synthetic spoofed native FFI",
                           ))

                    class SpoofedFfiKey:
                        __hash__ = object.__hash__

                        def __eq__(self, other: Any) -> bool:
                            return True

                    keyed_handle = fake_cdll()
                    vars(keyed_handle).update({
                        "_name": str(ROOT / spec.engine_relative),
                        "_handle": 7,
                    })
                    vars(keyed_handle)[SpoofedFfiKey()] = (
                        original_ownership["baseline"].compile
                    )
                    reject("reject-spoofed-zig-ffi-attribute-key",
                           lambda item=keyed_handle:
                           forbid_owned_original_matchers(
                               item, original_ownership, spec, guard,
                               frozenset(), "synthetic spoofed FFI key",
                           ))
                else:
                    reject("reject-unowned-native-ffi-handle-" + name,
                           check_handle)
            finally:
                if previous_ctypes is None:
                    sys.modules.pop("ctypes", None)
                else:
                    sys.modules["ctypes"] = previous_ctypes
        accept("allow-the-genuine-shared-c-engine-and-python-bridge",
               fixtures["c"][0]["native_provenance"]["native_engine"]
               == fixtures["c"][0]["native_provenance"]["native_bridge"])
        accept("allow-only-the-independently-owned-zig-native-ffi",
               fixtures["zig"][0]["matcher_guard"]
               ["owned_native_ffi_allowed"] is True
               and fixtures["zig"][0]["matcher_guard"]
               ["owned_ctypes_load_count"] == 1)
        for family in ("rust", "c", "zig"):
            spec = family_spec(family)
            worker, pins = fixtures[family]
            for index, key, value in (
                (0, "candidate_family", "borrowed"),
                (1, "engine", "borrowed"),
                (2, "role", "candidate-borrowed"),
                (3, "matrix_sha256", "ab" * 32),
                (4, "controller_source_sha256", "cd" * 32),
                (5, "actual_public_method_count", 151),
                (6, "private_waiver_count", 12),
                (7, "public_waivers", ["ReTests.test_memory_leaks"]),
                (8, "hidden_cases_read", 1),
                (9, "clock_samples", 1),
                (10, "timing_trials_run", 1),
                (11, "final_winner_selected", True),
                (12, "original_source_sha256", "01" * 32),
                (13, "original_support_sha256", "23" * 32),
                (14, "original_warnings_helper_sha256", "45" * 32),
                (15, "original_corpus_sha256", "67" * 32),
                (16, "previous_oracle_relative", "tools/borrowed_oracle.py"),
                (17, "previous_oracle_sha256", "89" * 32),
            ):
                forged = dict(worker)
                forged[key] = value
                reject(
                    "reject-forged-" + family + "-worker-"
                    + format(index, "02d"),
                    lambda forged=forged, spec=spec, pins=pins:
                    validate_family_worker(
                        forged, spec, source_pin, pins, matrix,
                    ),
                )
            for index, key, value in (
                (0, "actual_method_guard_checks", GUARD_CHECKS - 1),
                (1, "actual_warning_registry_guard_checks", GUARD_CHECKS - 1),
                (2, "actual_object_identity_guarded", False),
                (3, "public_type_names_used_for_ownership", True),
                (4, "warning_registry_introspection_safe", False),
                (5, "warning_registry_exactly_absent", False),
                (6, "cross_family_imports_blocked", False),
                (7, "external_regex_imports_blocked", False),
                (8, "owned_native_ffi_allowed", not spec.owned_ctypes),
                (9, "trusted_stdlib_ctypes_preloaded", not spec.owned_ctypes),
                (10, "trusted_stdlib_ctypes_builtin_verified",
                 not spec.owned_ctypes),
                (11, "trusted_stdlib_ctypes_pythonapi_initialized",
                 not spec.owned_ctypes),
                (12, "trusted_stdlib_ctypes_source_sha256", "ab" * 32),
            ):
                forged = dict(worker)
                poisoned_guard = dict(worker["matcher_guard"])
                poisoned_guard[key] = value
                forged["matcher_guard"] = poisoned_guard
                reject(
                    "reject-unguarded-" + family + "-owner-"
                    + format(index, "02d"),
                    lambda forged=forged, spec=spec, pins=pins:
                    validate_family_worker(
                        forged, spec, source_pin, pins, matrix,
                    ),
                )
            for index, key, value in (
                (0, "relative", "candidates/borrowed_engine.so"),
                (1, "sha256", "fe" * 32),
                (2, "bytes", 0),
                (3, "inode", 0),
            ):
                forged = copy.deepcopy(worker)
                forged["native_provenance"]["native_engine"][key] = value
                reject(
                    "reject-forged-" + family + "-native-owner-"
                    + format(index, "02d"),
                    lambda forged=forged, spec=spec, pins=pins:
                    validate_family_worker(
                        forged, spec, source_pin, pins, matrix,
                    ),
                )
            forged = dict(worker)
            forged["records"] = worker["records"][:-1]
            reject("reject-omitted-original-method-" + family,
                   lambda forged=forged, spec=spec, pins=pins:
                   validate_family_worker(
                       forged, spec, source_pin, pins, matrix,
                   ))
            forged = dict(worker)
            forged["records"] = list(reversed(worker["records"]))
            forged["records_sha256"] = digest(forged["records"])
            reject("reject-reordered-original-methods-" + family,
                   lambda forged=forged, spec=spec, pins=pins:
                   validate_family_worker(
                       forged, spec, source_pin, pins, matrix,
                   ))
            for sibling in ("rust", "c", "zig"):
                if sibling == family:
                    continue
                sibling_spec = family_spec(sibling)
                accept("block-cross-family-" + family + "-to-" + sibling,
                       forbidden_family_module(
                           sibling_spec.adapter_module, spec,
                       )
                       and forbidden_family_module(
                           sibling_spec.bridge_module, spec,
                       ))
        for index, name in enumerate((
            "regex", "regex._regex", "_regex", "re2", "google_re2",
            "pcre", "pcre2", "onig", "oniguruma", "hyperscan",
            "vectorscan", "rust_regex", "fancy_regex", "sre_compile",
        )):
            accept("reject-external-regex-family-" + format(index, "02d"),
                   all(forbidden_family_module(name, family_spec(family))
                       for family in ("rust", "c", "zig")))
        for index, invalid in enumerate((
            None, 0, True, "", "0" * 64, "A" * 64, "g" * 64,
            "ab" * 31, "ab" * 33, MATRIX_SHA256.upper(),
        )):
            reject("reject-invalid-owner-fingerprint-" + format(index, "02d"),
                   lambda invalid=invalid: checked_digest(
                       invalid, "synthetic independent owner",
                   ))
        for index, invalid in enumerate((
            None, 0, True, "", "python", "vm", "RUST", "../zig",
        )):
            reject("reject-unowned-candidate-family-" + format(index, "02d"),
                   lambda invalid=invalid: family_spec(invalid))

        genuine_ctypes = sys.modules.get("ctypes")
        genuine_builtin = sys.modules.get("_ctypes")
        accept(
            "authenticate-genuine-prearmed-standard-ctypes-and-built-in",
            validate_trusted_stdlib_ctypes(
                genuine_ctypes, genuine_builtin,
            )["source_sha256"] == PINNED_STDLIB_CTYPES_SHA256,
        )
        spoofed_ctypes = types.ModuleType("ctypes")
        reject(
            "reject-preseeded-foreign-standard-ctypes-module",
            lambda: validate_trusted_stdlib_ctypes(
                spoofed_ctypes, genuine_builtin,
            ),
        )
        spoofed_builtin = types.ModuleType("_ctypes")
        reject(
            "reject-preseeded-foreign-builtin-ctypes-before-import",
            lambda: validate_trusted_builtin_ctypes(spoofed_builtin),
        )
        pythonapi = vars(genuine_ctypes)["pythonapi"]
        pythonapi_values = vars(pythonapi)
        require("PyImport_ImportModule" not in pythonapi_values,
                "a genuine standard process symbol was cached before control")
        pythonapi_values["PyImport_ImportModule"] = (
            original_ownership["baseline"].compile
        )
        try:
            reject(
                "reject-cached-original-matcher-on-standard-pythonapi",
                lambda: validate_trusted_stdlib_ctypes(
                    genuine_ctypes, genuine_builtin,
                ),
            )
        finally:
            pythonapi_values.pop("PyImport_ImportModule", None)
        accept(
            "restore-exact-fresh-standard-pythonapi-cache",
            validate_trusted_stdlib_ctypes(
                genuine_ctypes, genuine_builtin,
            )["pythonapi_initialized"] is True,
        )

        genuine_reference = dict(first)
        genuine_reference_evidence = genuine_reference.pop(
            "isolated_process_evidence",
        )
        accept(
            "preserve-complete-genuine-v5-reference-process-stream",
            validate_isolated_process_evidence(
                genuine_reference_evidence, genuine_reference,
                role="reference_a", family=None,
                pid=genuine_reference["pid"], returncode=0,
            ) is genuine_reference_evidence,
        )
        for index, key, value in (
            (0, "role", "reference"),
            (1, "candidate_family", "zig"),
            (2, "pid", 0),
            (3, "returncode", 1),
            (4, "records_sha256", "ab" * 32),
            (5, "record_count", PUBLIC_METHOD_COUNT - 1),
        ):
            forged_evidence = copy.deepcopy(genuine_reference_evidence)
            forged_evidence[key] = value
            reject(
                "reject-forged-complete-reference-process-"
                + format(index, "02d"),
                lambda actual=forged_evidence:
                validate_isolated_process_evidence(
                    actual, genuine_reference, role="reference_a",
                    family=None, pid=genuine_reference["pid"], returncode=0,
                ),
            )
        for index, key, value in (
            (0, "base64", "@@not-base64@@"),
            (1, "bytes", genuine_reference_evidence["stdout"]["bytes"] + 1),
            (2, "sha256", "cd" * 32),
            (3, "complete", False),
        ):
            forged_evidence = copy.deepcopy(genuine_reference_evidence)
            forged_evidence["stdout"][key] = value
            reject(
                "reject-clipped-genuine-reference-process-stream-"
                + format(index, "02d"),
                lambda actual=forged_evidence:
                validate_isolated_process_evidence(
                    actual, genuine_reference, role="reference_a",
                    family=None, pid=genuine_reference["pid"], returncode=0,
                ),
            )

        zig_spec = family_spec("zig")
        with isolated_family_imports(zig_spec) as actual_ffi_guard:
            actual_ctypes = genuine_ctypes
            actual_native = genuine_builtin
            expected_engine = str(ROOT / zig_spec.engine_relative)
            actual_realpath = os.path.realpath

            def synthetic_exact_realpath(value: Any) -> Any:
                if type(value) is str and value == expected_engine:
                    return expected_engine
                raise OriginalSuiteError(
                    "a synthetic path escaped exact owned FFI canonicalization",
                )

            os.path.realpath = synthetic_exact_realpath
            try:
                previous_allowed = len(
                    actual_ffi_guard["owned_ctypes_load_paths"],
                )
                sys.audit("ctypes.dlopen", expected_engine)
                accept(
                    "accept-only-simulated-exact-owned-zig-engine-load",
                    len(actual_ffi_guard["owned_ctypes_load_paths"])
                    == previous_allowed + 1
                    and actual_ffi_guard["owned_ctypes_load_paths"][-1]
                    == zig_spec.engine_relative,
                )

                def reject_live_dynamic(
                    name: str, action: Callable[[], Any],
                ) -> None:
                    before = actual_ffi_guard[
                        "rejected_foreign_dynamic_loads"
                    ]
                    reject(name, action)
                    require(
                        actual_ffi_guard["rejected_foreign_dynamic_loads"]
                        == before + 1,
                        "the actual armed native FFI audit was not exercised: "
                        + name,
                    )

                reject_live_dynamic(
                    "reject-real-postarm-cdll-process-handle",
                    lambda: actual_ctypes.CDLL(None),
                )
                reject_live_dynamic(
                    "reject-real-postarm-pydll-process-handle",
                    lambda: actual_ctypes.PyDLL(None),
                )
                reject_live_dynamic(
                    "reject-real-postarm-builtin-ctypes-process-load",
                    lambda: actual_native.dlopen(None),
                )
                reject_live_dynamic(
                    "reject-real-postarm-cdll-loader-process-handle",
                    lambda: actual_ctypes.cdll.LoadLibrary(None),
                )
                reject_live_dynamic(
                    "reject-real-postarm-pydll-loader-process-handle",
                    lambda: actual_ctypes.pydll.LoadLibrary(None),
                )
                reject_live_dynamic(
                    "reject-real-postarm-foreign-native-library",
                    lambda: actual_ctypes.CDLL(
                        "/tmp/rebar-forbidden-foreign-regex.so",
                    ),
                )
                reject_live_dynamic(
                    "reject-real-postarm-pythonapi-symbol-resolution",
                    lambda: getattr(
                        actual_ctypes.pythonapi, "PyImport_ImportModule",
                    ),
                )
                reject_live_dynamic(
                    "reject-real-postarm-pythonapi-audit-event",
                    lambda: sys.audit(
                        "ctypes.dlsym", actual_ctypes.pythonapi,
                        "PyImport_ImportModule",
                    ),
                )

                def synthetic_symlink_realpath(value: Any) -> str:
                    return "/tmp/rebar-forbidden-symlink-engine.so"

                os.path.realpath = synthetic_symlink_realpath
                reject_live_dynamic(
                    "reject-postarm-owned-path-swapped-for-foreign-symlink",
                    lambda: sys.audit("ctypes.dlopen", expected_engine),
                )
                os.path.realpath = synthetic_exact_realpath

                before_imports = actual_ffi_guard[
                    "rejected_cross_family_or_external_imports"
                ]
                reject(
                    "reject-real-postarm-external-regex-import-event",
                    lambda: sys.audit("import", "regex", None, None, None),
                )
                require(
                    actual_ffi_guard[
                        "rejected_cross_family_or_external_imports"
                    ] == before_imports + 1,
                    "the genuine post-arm external regex import was not blocked",
                )

                def process_probe() -> None:
                    sys.audit("subprocess.Popen", "synthetic", (), None, None)

                owned_process_probe = types.FunctionType(
                    process_probe.__code__, {
                        "__name__": zig_spec.adapter_module,
                        "__builtins__": builtins.__dict__,
                        "sys": sys,
                    },
                )
                before_process = actual_ffi_guard[
                    "rejected_process_delegations"
                ]
                reject(
                    "reject-real-postarm-candidate-process-delegation-event",
                    owned_process_probe,
                )
                require(
                    actual_ffi_guard["rejected_process_delegations"]
                    == before_process + 1,
                    "the genuine candidate process audit was not exercised",
                )
            finally:
                os.path.realpath = actual_realpath

        for name, action in (
            ("block-candidate-source-file-read",
             lambda: builtins.open("candidates/rust_candidate.py", "rb")),
            ("block-owned-native-binary-read",
             lambda: os.open("candidates/_zig_probe.so", os.O_RDONLY)),
            ("block-original-evidence-file-write",
             lambda: os.write(1, b"forbidden")),
            ("block-rust-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("block-c-family-candidate-import",
             lambda: importlib.import_module("candidates.vm_candidate")),
            ("block-zig-candidate-import",
             lambda: importlib.import_module("candidates.zig_candidate")),
            ("block-real-candidate-worker",
             lambda: subprocess.Popen([str(PINNED_PYTHON)])),
            ("block-background-candidate-worker",
             lambda: threading.Thread(target=lambda: None).start()),
            ("block-performance-clock", lambda: time.perf_counter()),
            ("block-wall-clock", lambda: time.time()),
            ("block-garbage-collection", lambda: gc.collect()),
        ):
            reject(name, action)
        accept("reject-at-least-40-distinct-genuine-independent-forgeries",
               len(rejected) >= 40 and len(rejected) == len(set(rejected)))
        accept("synthetic-controls-never-read-candidates-or-native-engines",
               all(effects[key] == 0 for key in (
                   "file_reads", "file_writes", "candidate_imports",
                   "workers_started", "threads_started", "clock_samples",
                   "gc_collections", "hidden_cases_read",
                   "performance_files_read",
               )))
        accept("seven-distinct-real-source-side-effects-are-blocked",
               all(effects[key] > 0 for key in (
                   "blocked_reads", "blocked_writes", "blocked_imports",
                   "blocked_workers", "blocked_threads", "blocked_clocks",
                   "blocked_gc_collections",
               )))
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "controller_source_sha256": source_pin,
        "previous_oracle_relative": PREVIOUS_ORACLE_RELATIVE,
        "previous_oracle_sha256": PREVIOUS_ORACLE_SHA256,
        "test_harness_relative": HARNESS_RELATIVE,
        "test_harness_sha256": HARNESS_SHA256,
        "identity_guard_relative": IDENTITY_GUARD_RELATIVE,
        "identity_guard_sha256": IDENTITY_GUARD_SHA256,
        "warning_guard_relative": WARNING_GUARD_RELATIVE,
        "warning_guard_sha256": WARNING_GUARD_SHA256,
        "original_source_sha256": harness.TEST_SOURCE_SHA256,
        "original_support_sha256": harness.SUPPORT_SHA256,
        "original_warnings_helper_sha256": harness.WARNINGS_HELPER_SHA256,
        "original_corpus_sha256": harness.CORPUS_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_SHA256,
        "all_original_method_count": ORIGINAL_METHOD_COUNT,
        "actual_public_method_count": PUBLIC_METHOD_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "private_waivers": list(harness.PRIVATE_METHODS),
        "public_waivers": [],
        "all_original_methods_executed": False,
        "all_original_methods_qualified": False,
        "actual_pass_count_per_worker": 151,
        "authentic_debug_skip_count_per_worker": 1,
        "authentic_debug_skip": "ReTests.test_memory_leaks",
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_native_files_read": 0,
        "actual_localedef_workers": 4,
        "actual_private_temporary_directories_created": 2,
        "actual_private_locale_outputs_created": 4,
        "all_private_temporary_directories_removed": True,
        "supported_independent_families": ["rust", "c", "zig"],
        "combined_c_native_engine_and_bridge_supported": True,
        "exact_owned_zig_ctypes_ffi_supported": True,
        "trusted_stdlib_ctypes_preloaded_before_guard": True,
        "trusted_stdlib_ctypes_provenance": trusted_stdlib_ctypes,
        "owned_public_re_type_names_supported": True,
        "required_original_method_guard_checks": GUARD_CHECKS,
        "required_warning_registry_guard_checks": GUARD_CHECKS,
        "actual_source_only_identity_poison_count":
        quarantine_controls["rejected_count"],
        "actual_source_only_identity_poison_names":
        quarantine_controls["rejected_names"],
        "actual_source_only_owned_type_positive_count":
        quarantine_controls["source_only_owned_public_type_positive_count"],
        "actual_source_only_warning_poison_count":
        warning_controls["warning_safe_rejected_count"],
        "actual_source_only_warning_poison_names":
        warning_controls["warning_safe_rejected_names"],
        "actual_warning_registry_exactly_absent":
        warning_controls["warning_registry_exactly_absent"],
        "actual_warning_filename_verified":
        warning_controls["source_only_warning_filename_verified"],
        "actual_original_matchers_restored":
        quarantine_controls["original_matchers_restored"],
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "synthetic_effects": effects,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the exact same original Python regex tests for independent native engines",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", choices=("rust", "c", "zig"))
    modes.add_argument("--internal-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--family", choices=("rust", "c", "zig"),
                        help=argparse.SUPPRESS)
    parser.add_argument(
        "--role", choices=("reference_a", "reference_b", "candidate_reference"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def option_pins(options: argparse.Namespace) -> dict[str, str]:
    return {
        "source": checked_digest(
            options.candidate_source_sha256, "independent Python adapter",
        ),
        "native_engine": checked_digest(
            options.native_engine_sha256, "independent native engine",
        ),
        "native_bridge": checked_digest(
            options.native_bridge_sha256, "independent native Python bridge",
        ),
    }


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "candidate", "family", "role", "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "an original source self-test cannot pin or import a candidate")
        result = source_self_test()
    elif options.candidate:
        require(options.family is None and options.role is None,
                "only one exact independent candidate family may be selected")
        result = run_candidate(
            options.candidate,
            checked_digest(options.oracle_source_sha256,
                           "independent original controller"),
            checked_digest(options.matrix_sha256,
                           "unchanged original method matrix"),
            option_pins(options),
        )
    else:
        source_pin = checked_digest(
            options.oracle_source_sha256, "independent original controller",
        )
        matrix_pin = checked_digest(
            options.matrix_sha256, "unchanged original method matrix",
        )
        if options.role is not None:
            require(options.family is None
                    and all(getattr(options, name) is None for name in (
                        "candidate_source_sha256", "native_engine_sha256",
                        "native_bridge_sha256",
                    )),
                    "a genuine standard reference cannot select a native family")
            result = execute_reference_worker(
                options.role, source_pin, matrix_pin,
            )
        else:
            require(options.family in FAMILIES,
                    "the isolated worker needs exactly one native family")
            result = execute_family_worker(
                options.family, source_pin, matrix_pin, option_pins(options),
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
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        sys.stderr.buffer.flush()
        raise SystemExit(1) from error
