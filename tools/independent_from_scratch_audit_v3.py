#!/usr/bin/env python3
"""Audit caller-pinned, genuinely independent Rust, C, and Zig regex engines.

The immutable V2 and original CPython V5 ownership policies remain mandatory;
no old candidate source or binary hash is reused.  An actual ``--audit`` must
explicitly pin every exact source and every distinct native artifact for its
single chosen family, as well as the adapter, engine, bridge, and this source.
It verifies Python ASTs, native lexical source, Rust and Zig dependencies, ELF
imports and exports, object identities, and one continuously guarded isolated
worker.  ``--self-test`` is in-memory only: it cannot read a source or binary,
import or run a candidate, spawn a process or thread, or sample a clock.
This file has no correctness, benchmark, holdout, or winner-selection mode.
"""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import copyreg
import ctypes
import functools
import gc
import hashlib
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import json
import os
import stat
import struct
import subprocess
import sys
import threading
import time
import tomllib
import types
from collections.abc import Callable, Mapping
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
ORACLE_NAME = "independent-from-scratch-audit-v3"
SCHEMA = "rebar-independent-from-scratch-audit-v3"
PYTHON_VERSION = (3, 14, 6)
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_CTYPES = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/ctypes/__init__.py"
)
PINNED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
READELF = "/usr/bin/readelf"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
IMMUTABLE_POLICY_SHA256 = types.MappingProxyType({
    "tools/independent_from_scratch_audit_v2.py": (
        "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
    ),
    "tools/independent_original_cpython_suite_v5.py": (
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
    ),
})
RUST_SOURCE_FILES = (
    "candidates/rust/src/lib.rs",
    "candidates/rust/src/newline.rs",
    "candidates/rust/src/search.rs",
    "candidates/rust/src/stack.rs",
    "candidates/rust/src/unicode_tables.rs",
)
RUST_ENGINE_EXPORTS = frozenset({
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group",
    "rebar_name_len",
})
RUST_ENGINE_UNDEFINED = frozenset({
    "Py_GetRecursionLimit", "_ITM_deregisterTMCloneTable",
    "_ITM_registerTMCloneTable", "_Unwind_Backtrace",
    "_Unwind_GetDataRelBase", "_Unwind_GetIP", "_Unwind_GetIPInfo",
    "_Unwind_GetLanguageSpecificData", "_Unwind_GetRegionStart",
    "_Unwind_GetTextRelBase", "_Unwind_Resume", "_Unwind_SetGR",
    "_Unwind_SetIP", "__cxa_finalize", "__cxa_thread_atexit_impl",
    "__errno_location", "__gmon_start__", "__tls_get_addr", "abort",
    "bcmp", "calloc", "close", "dl_iterate_phdr", "free", "fstat64",
    "getcwd", "getenv", "gettid", "isalnum", "lseek64", "malloc",
    "memchr", "memcmp", "memcpy", "memmem", "memmove", "memrchr",
    "memset", "mmap64", "munmap", "open64", "posix_memalign",
    "pthread_key_create", "pthread_key_delete", "pthread_setspecific",
    "read", "readlink", "realloc", "realpath", "stat64", "statx",
    "strcmp", "strlen", "strncmp", "syscall", "tolower", "write", "writev",
})
ZIG_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
})
ZIG_ENGINE_UNDEFINED = frozenset({
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDecimalDigit", "_PyUnicode_IsDigit",
    "_PyUnicode_IsNumeric", "_PyUnicode_IsWhitespace",
    "_PyUnicode_ToLowercase", "_PyUnicode_ToUppercase", "__gmon_start__",
    "free", "isalnum", "malloc", "malloc_usable_size", "memcpy", "memset",
    "posix_memalign", "realloc", "tolower",
})
ZIG_BRIDGE_REFERENCES = frozenset({
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
})
ZIG_CTYPES_SYMBOLS = frozenset({
    "rebar_zig_compile", "rebar_zig_free", "rebar_zig_groups",
    "rebar_zig_flags", "rebar_zig_program_memory", "rebar_zig_name_count",
    "rebar_zig_name_length", "rebar_zig_name_group", "rebar_zig_name_copy",
})
RUST_BRIDGE_SYSTEM_UNDEFINED = frozenset({
    "_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable",
    "__assert_fail", "__cxa_finalize", "__gmon_start__",
    "__stack_chk_fail", "calloc", "free", "malloc", "memchr", "memcmp",
    "memcpy", "memmem", "memmove", "memset", "realloc", "strlen",
})
SYSTEM_NATIVE_UNDEFINED = frozenset({
    "_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable",
    "__assert_fail", "__ctype_b_loc", "__ctype_tolower_loc",
    "__cxa_finalize", "__gmon_start__", "__memcpy_chk",
    "__stack_chk_fail", "bcmp", "calloc", "free", "malloc", "memchr",
    "memcmp", "memcpy", "memmem", "memmove", "memset", "realloc",
    "strlen",
})
FAMILY_SPECS = types.MappingProxyType({
    "rust": types.MappingProxyType({
        "module": "candidates.rust_candidate",
        "adapter": "candidates/rust_candidate.py",
        "bridge_module": "candidates._rust_bridge",
        "bridge_source": "candidates/rust/py_bridge.c",
        "engine": "candidates/_rust_engine.so",
        "bridge": "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        "sources": (
            "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
            *RUST_SOURCE_FILES,
        ),
        "binaries": (
            "candidates/_rust_engine.so",
            "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        ),
        "imports": frozenset({
            "enum", "operator", "os", "types", "unicodedata", "warnings",
        }),
        "from_imports": frozenset({("candidates", "_rust_bridge", None)}),
        "headers": frozenset({
            "Python.h", "stddef.h", "stdint.h", "string.h",
        }),
        "exports": RUST_ENGINE_EXPORTS,
    }),
    "c": types.MappingProxyType({
        "module": "candidates.vm_candidate",
        "adapter": "candidates/vm_candidate.py",
        "bridge_module": "candidates._vm_native",
        "bridge_source": "candidates/_vm_native.c",
        "engine": "candidates/_vm_native" + EXTENSION_SUFFIX,
        "bridge": "candidates/_vm_native" + EXTENSION_SUFFIX,
        "sources": (
            "candidates/vm_candidate.py", "candidates/_vm_native.c",
        ),
        "binaries": ("candidates/_vm_native" + EXTENSION_SUFFIX,),
        "imports": frozenset({
            "enum", "os", "types", "unicodedata", "warnings",
        }),
        "from_imports": frozenset({
            ("copyreg", "_reconstructor", "_copy_reconstructor"),
            ("struct", "calcsize", "_native_calcsize"),
            ("candidates", "_vm_native", None),
        }),
        "headers": frozenset({
            "Python.h", "ctype.h", "stddef.h", "stdint.h", "stdlib.h",
            "string.h",
        }),
        "exports": frozenset(),
    }),
    "zig": types.MappingProxyType({
        "module": "candidates.zig_candidate",
        "adapter": "candidates/zig_candidate.py",
        "bridge_module": "candidates._zig_bridge",
        "bridge_source": "candidates/zig/py_bridge.c",
        "engine": "candidates/_zig_probe.so",
        "bridge": "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        "sources": (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        "binaries": (
            "candidates/_zig_probe.so",
            "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        ),
        "imports": frozenset({
            "ctypes", "enum", "os", "types", "unicodedata", "warnings",
        }),
        "from_imports": frozenset({("candidates", "_zig_bridge", None)}),
        "headers": frozenset({"Python.h", "stddef.h", "stdint.h"}),
        "exports": ZIG_ENGINE_EXPORTS,
    }),
})
FORBIDDEN_MODULE_ROOTS = frozenset({
    "_regex", "_sre", "cffi", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re", "re2", "regex",
    "rebar", "runpy", "rust_regex", "sre_compile", "sre_constants",
    "sre_parse", "subprocess", "vectorscan", "zig",
})
FORBIDDEN_NATIVE_IDENTIFIERS = frozenset({
    "LoadLibrary", "LoadLibraryA", "LoadLibraryW", "GetProcAddress",
    "PyRun_AnyFile", "PyRun_SimpleString", "PyRun_String",
    "Py_CompileString", "PyEval_EvalCode", "dlmopen", "dlopen", "dlsym",
    "dlvsym", "execv", "execve", "fork", "popen", "posix_spawn",
    "regcomp", "regexec", "regfree", "system",
})
FORBIDDEN_NATIVE_PREFIXES = (
    "_PyImport_", "_PyRun_", "PyInit__sre", "PyImport_ExecCode",
    "PyImport_Import", "PyRun_", "Py_CompileString", "PyEval_Eval",
    "hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "sre_",
)


class AuditFailure(Exception):
    """A candidate family, pinned owner, native ABI, or audit was forged."""


class SourceOnlyError(AuditFailure):
    """A synthetic self-test attempted a real file or execution effect."""


class WorkerFailure(AuditFailure):
    """Preserve the complete stdout and stderr of a rejected real worker."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditFailure(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise AuditFailure("complete ownership evidence is not canonical JSON") from error


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value)
    )


def checked_digest(value: Any, label: str) -> str:
    require(valid_digest(value), "an explicit exact SHA-256 is required: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "complete native ownership JSON contains a duplicate field")
        result[key] = value
    return result


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "a complete bounded ownership worker is mandatory: " + label)

    def reject_constant(_: str) -> Any:
        raise AuditFailure("nonfinite native ownership JSON is forbidden")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (AuditFailure, TypeError, ValueError, UnicodeError,
            json.JSONDecodeError) as error:
        raise AuditFailure(
            "an isolated ownership worker emitted invalid JSON: " + label
        ) from error
    require(type(value) is dict and canonical(value) == raw,
            "a complete ownership worker was truncated or substituted: " + label)
    return value


def family_spec(family: Any) -> Mapping[str, Any]:
    require(type(family) is str and family in FAMILY_SPECS,
            "select exactly one genuine Rust, C, or Zig native family")
    spec = FAMILY_SPECS[family]
    require(isinstance(spec, Mapping)
            and spec["module"].startswith("candidates.")
            and spec["bridge_module"].startswith("candidates.")
            and spec["module"] != spec["bridge_module"]
            and spec["adapter"] in spec["sources"]
            and spec["bridge_source"] in spec["sources"]
            and spec["engine"] in spec["binaries"]
            and spec["bridge"] in spec["binaries"]
            and (spec["engine"] == spec["bridge"]) == (family == "c")
            and (len(spec["binaries"]) == 1) == (family == "c")
            and len(set(spec["sources"])) == len(spec["sources"])
            and len(set(spec["binaries"])) == len(spec["binaries"]),
            "the independent native family closure was substituted")
    return spec


def owned_relative(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "an exact bounded native-owner relative path is mandatory")
    parts = tuple(relative.split("/"))
    require(all(part not in {"", ".", ".."} for part in parts)
            and "/".join(parts) == relative,
            "a caller-pinned path escaped its canonical project root")
    return parts


def parse_pin_entries(values: Any, label: str) -> dict[str, str]:
    require(type(values) is list and bool(values),
            "explicitly pin every exact " + label)
    result: dict[str, str] = {}
    for item in values:
        require(type(item) is str, "an exact path=SHA-256 pin is mandatory")
        path, separator, value = item.partition("=")
        require(separator == "=" and "=" not in value,
                "a complete canonical path=SHA-256 pin is mandatory")
        owned_relative(path)
        checked_digest(value, label + " " + path)
        require(path not in result,
                "a caller repeated or concealed a pinned owner: " + path)
        result[path] = value
    return result


def validate_family_pins(
    family: Any,
    adapter_pin: Any,
    engine_pin: Any,
    bridge_pin: Any,
    source_entries: Any,
    native_entries: Any,
) -> dict[str, Any]:
    spec = family_spec(family)
    checked_digest(adapter_pin, "independently owned Python adapter")
    checked_digest(engine_pin, "independently owned native regex engine")
    checked_digest(bridge_pin, "independently owned native Python bridge")
    sources = parse_pin_entries(source_entries, family + " source")
    binaries = parse_pin_entries(native_entries, family + " native artifact")
    require(set(sources) == set(spec["sources"]),
            "pin the complete exact " + family + " source and lockfile closure")
    require(set(binaries) == set(spec["binaries"]),
            "pin every exact distinct " + family + " native artifact")
    require(sources[spec["adapter"]] == adapter_pin,
            "pin the exact family-owned Python adapter")
    require(binaries[spec["engine"]] == engine_pin,
            "pin the exact family-owned native matching engine")
    require(binaries[spec["bridge"]] == bridge_pin,
            "pin the exact family-owned Python native bridge")
    require((engine_pin == bridge_pin) == (family == "c"),
            "only the genuine combined C engine and bridge may alias")
    require(len(set(sources.values())) == len(sources),
            "two distinct candidate source files were silently substituted")
    require(len(set(binaries.values())) == len(binaries),
            "two distinct native candidate artifacts were silently substituted")
    return {
        "family": family,
        "candidate_source_sha256": adapter_pin,
        "native_engine_sha256": engine_pin,
        "native_bridge_sha256": bridge_pin,
        "source_sha256": dict(sorted(sources.items())),
        "native_sha256": dict(sorted(binaries.items())),
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_SHA256),
    }


def validate_manifest(value: Any, family: str) -> dict[str, Any]:
    require(type(value) is dict and set(value) == {
        "family", "candidate_source_sha256", "native_engine_sha256",
        "native_bridge_sha256", "source_sha256", "native_sha256",
        "immutable_policy_sha256",
    }, "a complete dynamically pinned ownership manifest is mandatory")
    source_map = value.get("source_sha256")
    native_map = value.get("native_sha256")
    require(type(source_map) is dict and type(native_map) is dict,
            "complete canonical source and native ownership maps are mandatory")
    expected = validate_family_pins(
        value.get("family"),
        value.get("candidate_source_sha256"),
        value.get("native_engine_sha256"),
        value.get("native_bridge_sha256"),
        [path + "=" + source_hash for path, source_hash in source_map.items()],
        [path + "=" + native_hash for path, native_hash in native_map.items()],
    )
    require(value == expected and value["family"] == family,
            "a complete family manifest or immutable V2/V5 policy was forged")
    return value


def forbidden_module(name: Any, family: str) -> bool:
    if type(name) is not str or not name:
        return True
    spec = family_spec(family)
    root = name.partition(".")[0]
    if root == "candidates":
        return name not in {"candidates", spec["module"], spec["bridge_module"]}
    if root == "ctypes":
        return family != "zig" or name not in {"ctypes", "ctypes._endian"}
    return root in FORBIDDEN_MODULE_ROOTS or root.endswith("_candidate")


def native_symbol_forbidden(name: str) -> bool:
    base = name.partition("@")[0]
    if base == "PyImport_ImportModule":
        return False
    return base in FORBIDDEN_NATIVE_IDENTIFIERS or base.startswith(
        FORBIDDEN_NATIVE_PREFIXES
    )


def walk_ast(node: ast.AST) -> Any:
    """Traverse the whole syntax tree without ast.walk's lazy import."""
    require(isinstance(node, ast.AST),
            "a complete native adapter syntax tree is mandatory")
    pending = [node]
    while pending:
        current = pending.pop()
        yield current
        pending.extend(reversed(tuple(ast.iter_child_nodes(current))))


def attribute_path(node: ast.AST) -> tuple[str, ...] | None:
    pieces: list[str] = []
    while isinstance(node, ast.Attribute):
        pieces.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    return (node.id, *reversed(pieces))


def forbidden_dynamic_call(dotted: str, family: str) -> bool:
    parts = dotted.split(".")
    if forbidden_module(parts[0], family):
        return True
    if parts[0] == "os":
        return any(part in {
            "system", "popen", "fork", "posix_spawn", "execv", "execve",
        } for part in parts[1:])
    if parts[0] == "builtins":
        return any(part in {"__import__", "eval", "exec"}
                   for part in parts[1:])
    if parts[0] == "ctypes":
        return family != "zig" or any(part in {
            "PyDLL", "WinDLL", "OleDLL", "LibraryLoader", "pythonapi",
            "pydll", "cdll", "windll", "oledll", "util", "_dlopen",
        } for part in parts[1:])
    return False


def inspect_zig_ctypes_loader(tree: ast.AST) -> dict[str, Any]:
    classes = [
        node for node in walk_ast(tree)
        if isinstance(node, ast.ClassDef) and node.name == "_Native"
    ]
    require(len(classes) == 1, "Zig has no unique family-owned native loader")
    functions = [
        node for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "__init__"
    ]
    require(len(functions) == 1 and isinstance(functions[0], ast.FunctionDef),
            "Zig has no unique synchronous native loader")
    body = functions[0].body
    require(len(body) >= 3, "the owned Zig engine load path is incomplete")
    first, second, third = body[:3]
    require(isinstance(first, ast.Assign) and len(first.targets) == 1
            and isinstance(first.targets[0], ast.Name)
            and first.targets[0].id == "path"
            and isinstance(first.value, ast.Call)
            and attribute_path(first.value.func) == ("os", "path", "join")
            and len(first.value.args) == 2 and not first.value.keywords
            and isinstance(first.value.args[0], ast.Call)
            and attribute_path(first.value.args[0].func)
            == ("os", "path", "dirname")
            and len(first.value.args[0].args) == 1
            and not first.value.args[0].keywords
            and isinstance(first.value.args[0].args[0], ast.Name)
            and first.value.args[0].args[0].id == "__file__"
            and isinstance(first.value.args[1], ast.Constant)
            and first.value.args[1].value == "_zig_probe.so",
            "Zig ctypes does not derive its exact adjacent pinned engine")
    require(isinstance(second, ast.Assign) and len(second.targets) == 1
            and attribute_path(second.targets[0]) == ("self", "library")
            and isinstance(second.value, ast.Call)
            and attribute_path(second.value.func) == ("ctypes", "CDLL")
            and len(second.value.args) == 1 and not second.value.keywords
            and isinstance(second.value.args[0], ast.Name)
            and second.value.args[0].id == "path",
            "Zig ctypes opens a process, foreign library, or ambient handle")
    require(isinstance(third, ast.Assign) and len(third.targets) == 1
            and isinstance(third.targets[0], ast.Name)
            and third.targets[0].id == "lib"
            and attribute_path(third.value) == ("self", "library"),
            "Zig symbols are not bound to their single owned engine")
    configured: list[str] = []
    for node in walk_ast(functions[0]):
        if isinstance(node, ast.Attribute):
            path = attribute_path(node)
            if path and len(path) >= 2 and path[0] == "lib":
                require(path[1] in ZIG_CTYPES_SYMBOLS,
                        "Zig references an unowned native FFI symbol: " + path[1])
                configured.append(path[1])
    require(frozenset(configured) == ZIG_CTYPES_SYMBOLS,
            "Zig must configure all nine and only nine owned FFI symbols")
    return {
        "owned_library": "candidates/_zig_probe.so",
        "configured_symbols": sorted(ZIG_CTYPES_SYMBOLS),
    }


def adapter_imports(source: str, family: str) -> dict[str, Any]:
    spec = family_spec(family)
    try:
        tree = ast.parse(source, filename=spec["adapter"])
    except (SyntaxError, TypeError, ValueError) as error:
        raise AuditFailure(
            "the owned " + family + " adapter is invalid Python: " + str(error)
        ) from error
    modules: list[str] = []
    from_imports: list[tuple[str, str, str | None]] = []
    aliases: dict[str, str] = {}
    ctypes_loads = 0
    for node in walk_ast(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                require(alias.name in spec["imports"] and alias.asname is None,
                        family + " imports an unowned or aliased module: "
                        + alias.name)
                modules.append(alias.name)
                aliases[alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            require(node.level == 0 and node.module is not None
                    and len(node.names) == 1,
                    family + " uses relative, wildcard, or concealed imports")
            alias = node.names[0]
            item = (node.module, alias.name, alias.asname)
            require(item in spec["from_imports"],
                    family + " imports a sibling, external, or borrowed engine")
            from_imports.append(item)
            aliases[alias.asname or alias.name] = (
                node.module + "." + alias.name
            )
        elif isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                require(function.id not in {
                    "__import__", "eval", "exec", "breakpoint",
                }, family + " performs dynamic Python execution")
            elif isinstance(function, ast.Attribute):
                path = attribute_path(function)
                if path:
                    root = aliases.get(path[0], path[0])
                    dotted = ".".join((root, *path[1:]))
                    require(not forbidden_dynamic_call(dotted, family),
                            family + " escapes through " + dotted)
                    if path == ("ctypes", "CDLL"):
                        require(family == "zig" and len(node.args) == 1
                                and not node.keywords
                                and isinstance(node.args[0], ast.Name)
                                and node.args[0].id == "path",
                                "load only the exact caller-pinned Zig engine")
                        ctypes_loads += 1
            if isinstance(function, ast.Name) and function.id == "getattr":
                if node.args and isinstance(node.args[0], ast.Name):
                    require(node.args[0].id not in {"ctypes", "lib"},
                            "a dynamic FFI loader or symbol was concealed")
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    require(node.args[1].value not in {
                        "__import__", "eval", "exec", "system", "popen",
                        "dlopen", "dlsym", "CDLL", "PyDLL", "find_library",
                        "import_module", "load_module",
                        "spec_from_file_location",
                    }, family + " resolves a dynamic import or process escape")
            if (isinstance(function, ast.Name)
                    and function.id in {"setattr", "delattr"}
                    and node.args):
                target = node.args[0]
                direct = target.id if isinstance(target, ast.Name) else None
                require(direct not in {"ctypes", "lib"}
                        and attribute_path(target) != ("self", "library"),
                        family + " mutates an authenticated FFI loader")
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
            for target in targets:
                for item in walk_ast(target):
                    if isinstance(item, ast.Name):
                        require(item.id not in {"ctypes", "__file__"},
                                family + " rebinds a trusted ownership primitive")
                    elif isinstance(item, ast.Attribute):
                        path = attribute_path(item)
                        require(not (path and path[0] == "ctypes"),
                                family + " mutates its trusted native loader")
        elif isinstance(node, ast.Attribute):
            path = attribute_path(node)
            if path and path[0] == "ctypes":
                require(not forbidden_dynamic_call(".".join(path), family),
                        family + " accesses an ambient native library")
            require(path not in {
                ("lib", "_handle"), ("lib", "__class__"),
                ("self", "library", "_handle"),
                ("self", "library", "__class__"),
            }, family + " mutates its pinned native library handle")
    require(len(modules) == len(spec["imports"])
            and frozenset(modules) == spec["imports"],
            family + " lacks its exact approved standard-library imports")
    require(len(from_imports) == len(spec["from_imports"])
            and frozenset(from_imports) == spec["from_imports"],
            family + " lacks its one exact native-family import closure")
    result: dict[str, Any] = {
        "modules": sorted(modules),
        "from_imports": [
            list(value) for value in sorted(
                from_imports,
                key=lambda item: (item[0], item[1], item[2] or ""),
            )
        ],
    }
    if family == "zig":
        require(ctypes_loads == 1,
                "Zig must perform exactly one owned native FFI load")
        result["owned_ctypes"] = inspect_zig_ctypes_loader(tree)
    else:
        require(ctypes_loads == 0,
                family + " must not use an independent dynamic loader")
    return result


def rust_or_c_character_literal(source: str, at: int) -> bool:
    if at + 2 >= len(source):
        return False
    if source[at + 1] != "\\":
        return source[at + 2] == "'"
    end = at + 1
    while end < len(source) and source[end] != "\n":
        if source[end] == "\\":
            end += 2
        elif source[end] == "'":
            return True
        else:
            end += 1
    return False


def lexical_tokens(source: str) -> tuple[tuple[str, str], ...]:
    require(type(source) is str,
            "a complete decoded native lexical source is mandatory")
    result: list[tuple[str, str]] = []
    at = 0
    while at < len(source):
        char = source[at]
        if char.isspace():
            at += 1
        elif source.startswith("//", at):
            end = source.find("\n", at + 2)
            at = len(source) if end < 0 else end + 1
        elif source.startswith("/*", at):
            depth = 1
            at += 2
            while at < len(source) and depth:
                if source.startswith("/*", at):
                    depth += 1
                    at += 2
                elif source.startswith("*/", at):
                    depth -= 1
                    at += 2
                else:
                    at += 1
            require(depth == 0,
                    "an owned native source has an unterminated block comment")
        elif char == "r" and at + 1 < len(source) \
                and source[at + 1] in {'"', "#"}:
            marker = at + 1
            while marker < len(source) and source[marker] == "#":
                marker += 1
            if marker >= len(source) or source[marker] != '"':
                result.append(("identifier", "r"))
                at += 1
                continue
            ending = '"' + source[at + 1:marker]
            close = source.find(ending, marker + 1)
            require(close >= 0, "an owned native raw string is unterminated")
            result.append(("string", source[marker + 1:close]))
            at = close + len(ending)
        elif char == "'" and not rust_or_c_character_literal(source, at):
            result.append(("punctuation", char))
            at += 1
        elif char in {'"', "'"}:
            quote = char
            end = at + 1
            while end < len(source):
                if source[end] == "\\":
                    end += 2
                elif source[end] == quote:
                    break
                else:
                    end += 1
            require(end < len(source), "an owned native literal is unterminated")
            try:
                actual = ast.literal_eval(source[at:end + 1])
            except (SyntaxError, TypeError, ValueError):
                actual = source[at + 1:end]
            result.append((
                "string" if quote == '"' else "character", str(actual)
            ))
            at = end + 1
        elif char.isalpha() or char == "_":
            end = at + 1
            while end < len(source) and (
                source[end].isalnum() or source[end] == "_"
            ):
                end += 1
            result.append(("identifier", source[at:end]))
            at = end
        else:
            result.append(("punctuation", char))
            at += 1
    return tuple(result)


def public_re_metadata(
    tokens: tuple[tuple[str, str], ...], index: int, family: str,
) -> bool:
    if index and tokens[index - 1] == ("punctuation", "{"):
        return True
    names = (
        {"pattern_module"}
        if family == "rust"
        else {"module", "public_pattern_module", "public_match_module"}
        if family == "c"
        else set()
    )
    if index < 4:
        return False
    previous = tokens[index - 4:index]
    return (
        previous[0] == ("identifier", "PyUnicode_CompareWithASCIIString")
        and previous[1] == ("punctuation", "(")
        and previous[2][0] == "identifier" and previous[2][1] in names
        and previous[3] == ("punctuation", ",")
    )


def inspect_bridge(source: str, family: str) -> dict[str, Any]:
    spec = family_spec(family)
    includes: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        directive = stripped[1:].lstrip()
        if not directive.startswith("include"):
            continue
        argument = directive[len("include"):].strip()
        require(len(argument) >= 3 and argument.startswith("<")
                and argument.endswith(">"),
                family + " computes or imports an external native header")
        header = argument[1:-1]
        require(header in spec["headers"],
                family + " includes an unowned native header: " + header)
        includes.append(header)
    require(len(includes) == len(spec["headers"])
            and frozenset(includes) == spec["headers"],
            family + " lacks its complete exact approved C header closure")
    tokens = lexical_tokens(source)
    fixed_imports: list[str] = []
    owned_scanners = 0
    for index, (kind, value) in enumerate(tokens):
        if kind == "identifier":
            require(not native_symbol_forbidden(value),
                    family + " calls a forbidden native matcher: " + value)
            if value.startswith("rebar_"):
                require(value in spec["exports"],
                        family + " borrows another native regex engine: " + value)
            if value == "PyImport_ImportModule":
                after = tokens[index + 1:index + 4]
                require(family == "rust" and len(after) == 3
                        and after[0] == ("punctuation", "(")
                        and after[1][0] == "string"
                        and after[1][1] in {"copyreg", "functools", "inspect"}
                        and after[2] == ("punctuation", ")"),
                        family + " dynamically imports an external matcher")
                fixed_imports.append(after[1][1])
        elif kind == "string":
            if value == "_sre.SRE_Scanner":
                require(index >= 3
                        and tokens[index - 3] == ("punctuation", ".")
                        and tokens[index - 2] in {
                            ("identifier", "tp_name"),
                            ("identifier", "name"),
                        }
                        and tokens[index - 1] == ("punctuation", "="),
                        family + " borrows a real CPython scanner engine")
                owned_scanners += 1
            elif value.startswith("candidates."):
                require(value == spec["module"],
                        family + " names another candidate in native code")
            elif value in FORBIDDEN_MODULE_ROOTS:
                require(value == "re" and public_re_metadata(
                    tokens, index, family
                ), family + " embeds or delegates to a forbidden regex engine")
    require(owned_scanners == 1,
            family + " must declare exactly one compatible owned scanner")
    approved_fixed = {
        "copyreg", "functools", "inspect",
    } if family == "rust" else set()
    require(len(fixed_imports) == len(approved_fixed)
            and frozenset(fixed_imports) == approved_fixed,
            family + " uses an unapproved native Python import")
    return {
        "includes": sorted(includes),
        "compatibility_imports": sorted(fixed_imports),
        "owned_compatible_scanner_names": owned_scanners,
    }


def inspect_rust_sources(sources: Mapping[str, str]) -> dict[str, Any]:
    require(isinstance(sources, Mapping)
            and frozenset(sources) == frozenset(RUST_SOURCE_FILES),
            "all five exact independently owned Rust sources are mandatory")
    declarations: list[str] = []
    approved_roots = {"std", "core", "crate", "self", "super", "stack"}
    for path, source in sources.items():
        tokens = lexical_tokens(source)
        for index, (kind, value) in enumerate(tokens):
            if kind != "identifier":
                continue
            require(not native_symbol_forbidden(value),
                    path + " references a forbidden external matching symbol")
            if value.startswith("rebar_"):
                require(value in RUST_ENGINE_EXPORTS,
                        path + " borrows another native matching engine")
            if value == "extern" and tokens[index + 1:index + 2] == (
                ("identifier", "crate"),
            ):
                raise AuditFailure(path + " imports an external Rust crate")
            if value in {"include", "include_bytes", "include_str"} \
                    and tokens[index + 1:index + 2] == (
                        ("punctuation", "!"),
                    ):
                raise AuditFailure(path + " embeds unowned external source")
            if value == "use":
                following = tokens[index + 1:index + 2]
                require(bool(following) and following[0][0] == "identifier"
                        and following[0][1] in approved_roots,
                        path + " imports an external Rust regex namespace")
            if path == RUST_SOURCE_FILES[0] and value == "mod":
                following = tokens[index + 1:index + 3]
                if len(following) == 2 \
                        and following[0][0] == "identifier" \
                        and following[1] == ("punctuation", ";"):
                    declarations.append(following[0][1])
            if value in {"path", "link"} and index \
                    and tokens[index - 1] == ("punctuation", "["):
                raise AuditFailure(path + " redirects native ownership")
    require(len(declarations) == 4
            and frozenset(declarations) == {
                "newline", "search", "stack", "unicode_tables",
            }, "Rust lacks exactly its four independently owned modules")
    return {"source_count": 5, "owned_modules": sorted(declarations)}


def inspect_cargo(manifest: str, lock_source: str) -> dict[str, Any]:
    try:
        package_file = tomllib.loads(manifest)
        lock = tomllib.loads(lock_source)
    except (tomllib.TOMLDecodeError, TypeError, ValueError) as error:
        raise AuditFailure("owned Cargo sources are invalid TOML") from error
    require(type(package_file) is dict
            and set(package_file).issubset({"package", "lib", "profile"}),
            "Cargo uses external dependencies, a workspace, or a build script")
    package = package_file.get("package")
    require(type(package) is dict and set(package) == {
        "name", "version", "edition", "rust-version", "publish",
    } and package["name"] == "rebar-rust-continuation"
      and package["version"] == "0.1.0"
      and package["edition"] == "2024"
      and package["rust-version"] == "1.85"
      and package["publish"] is False,
      "Cargo is not the exact unpublished independent Rust engine")
    library = package_file.get("lib")
    require(type(library) is dict and set(library) == {"crate-type"}
            and library["crate-type"] == ["cdylib"],
            "Cargo redirects or replaces its owned native source")
    require(type(lock) is dict and set(lock) == {"version", "package"}
            and lock["version"] == 4,
            "Cargo lockfile uses an external registry, source, or metadata")
    packages = lock["package"]
    require(type(packages) is list and len(packages) == 1
            and type(packages[0]) is dict
            and set(packages[0]) == {"name", "version"}
            and packages[0]["name"] == package["name"]
            and packages[0]["version"] == package["version"],
            "Cargo lockfile contains an external package or regex")
    return {
        "package": package["name"],
        "package_count": 1,
        "external_package_count": 0,
        "build_script_count": 0,
    }


def inspect_zig_source(source: str) -> dict[str, Any]:
    tokens = lexical_tokens(source)
    standard_imports = 0
    declarations: list[str] = []
    approved = frozenset({
        "_PyUnicode_IsAlpha", "_PyUnicode_IsDecimalDigit",
        "_PyUnicode_IsDigit", "_PyUnicode_IsNumeric",
        "_PyUnicode_IsWhitespace", "_PyUnicode_ToLowercase",
        "_PyUnicode_ToUppercase", "tolower", "isalnum",
    })
    for index, (kind, value) in enumerate(tokens):
        if kind != "identifier":
            continue
        require(not native_symbol_forbidden(value),
                "owned Zig source references a foreign regex or loader")
        if value.startswith("rebar_"):
            require(value in ZIG_ENGINE_EXPORTS,
                    "Zig borrows another native matching engine")
        if index and tokens[index - 1] == ("punctuation", "@"):
            if value == "import":
                require(tokens[index + 1:index + 4] == (
                    ("punctuation", "("), ("string", "std"),
                    ("punctuation", ")"),
                ), "Zig imports an external package or sibling engine")
                standard_imports += 1
            elif value in {"cImport", "cInclude", "embedFile", "extern"}:
                raise AuditFailure("Zig loads external native source: @" + value)
        if value == "extern":
            at = index + 1
            if at < len(tokens) and tokens[at] == ("string", "c"):
                at += 1
            if at < len(tokens) and tokens[at] == ("identifier", "fn"):
                at += 1
                require(at < len(tokens) and tokens[at][0] == "identifier"
                        and tokens[at][1] in approved,
                        "Zig links a foreign regex matcher or callback")
                declarations.append(tokens[at][1])
    require(standard_imports == 1,
            "Zig must import exactly one genuine standard library")
    require(len(declarations) == len(approved)
            and frozenset(declarations) == approved,
            "Zig hides an external or omitted native Unicode helper")
    return {
        "standard_library_imports": 1,
        "approved_unicode_and_system_helpers": sorted(declarations),
        "external_regex_package_count": 0,
    }


def expected_dynamic(
    family: str, binary: str,
) -> tuple[frozenset[str], tuple[str, ...]]:
    spec = family_spec(family)
    require(binary in spec["binaries"],
            "ELF inspection escaped the selected exact native family")
    if family == "rust" and binary == spec["engine"]:
        return frozenset({
            "libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2",
        }), ()
    if family == "rust":
        return frozenset({"_rust_engine.so", "libc.so.6"}), ("$ORIGIN",)
    if family == "c":
        return frozenset({"libc.so.6"}), ()
    if binary == spec["engine"]:
        return frozenset({"libc.so.6"}), ()
    return frozenset({"_zig_probe.so", "libc.so.6"}), ("$ORIGIN",)


def parse_dynamic_section(
    output: str, family: str, binary: str,
) -> dict[str, Any]:
    require(type(output) is str,
            "a complete actual ELF dynamic section is mandatory")
    approved, runpaths = expected_dynamic(family, binary)
    needed: list[str] = []
    paths: list[str] = []
    for line in output.splitlines():
        if "(NEEDED)" in line:
            _, separator, suffix = line.partition("[")
            require(bool(separator) and suffix.endswith("]"),
                    "the exact native ELF dependency is malformed")
            needed.append(suffix[:-1])
        elif "(RPATH)" in line:
            raise AuditFailure(binary + " uses an externally redirected RPATH")
        elif "(RUNPATH)" in line:
            _, separator, suffix = line.partition("[")
            require(bool(separator) and suffix.endswith("]"),
                    "the exact native ELF runpath is malformed")
            paths.append(suffix[:-1])
    require(len(needed) == len(approved)
            and len(set(needed)) == len(needed)
            and frozenset(needed) == approved,
            binary + " links a missing, duplicated, or external regex library")
    require(tuple(paths) == runpaths,
            binary + " uses a foreign, duplicated, or redirected runpath")
    return {"needed": sorted(needed), "runpaths": list(paths)}


def parse_dynamic_symbols(
    output: str, family: str, binary: str,
) -> dict[str, Any]:
    require(type(output) is str,
            "a complete actual native ELF symbol table is mandatory")
    spec = family_spec(family)
    require(binary in spec["binaries"],
            "a dynamic symbol table escaped its exact native family")
    undefined: set[str] = set()
    exported: set[str] = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 8 or not fields[0].rstrip(":").isdigit():
            continue
        bind = fields[4]
        section = fields[6]
        name = fields[7].partition("@")[0]
        require(not native_symbol_forbidden(name),
                binary + " resolves a forbidden matcher or native loader: " + name)
        if section == "UND":
            require(name not in undefined,
                    binary + " repeats an undefined native symbol: " + name)
            undefined.add(name)
        elif bind in {"GLOBAL", "WEAK"}:
            require(name not in exported,
                    binary + " repeats a public native symbol: " + name)
            exported.add(name)
    require(bool(undefined),
            binary + " has no independently auditable dynamic symbols")
    if family == "rust" and binary == spec["engine"]:
        require(not (undefined - RUST_ENGINE_UNDEFINED),
                binary + " links an unapproved Rust-native dependency")
        require(exported == RUST_ENGINE_EXPORTS,
                "the Rust engine exports a foreign or incomplete matching ABI")
        require("Py_GetRecursionLimit" in undefined,
                "the Rust engine lost its guarded CPython recursion helper")
    elif family == "rust":
        unexpected = {
            name for name in undefined
            if name not in RUST_ENGINE_EXPORTS
            and name not in RUST_BRIDGE_SYSTEM_UNDEFINED
            and not name.startswith(("Py", "_Py"))
        }
        require(not unexpected,
                "the Rust bridge resolves foreign symbols: "
                + str(sorted(unexpected)))
        require(exported == {"PyInit__rust_bridge"},
                "the Rust bridge exports a sibling or external entry point")
        require({
            "rebar_compile", "rebar_compile_scanner", "rebar_match",
            "rebar_free",
        } <= undefined, "the Rust bridge does not use its own native engine")
        require("PyImport_ImportModule" in undefined,
                "Rust compatibility imports are absent from native evidence")
    elif family == "c":
        unexpected = {
            name for name in undefined
            if name not in SYSTEM_NATIVE_UNDEFINED
            and not name.startswith(("Py", "_Py"))
        }
        require(not unexpected,
                "the C engine resolves foreign symbols: " + str(sorted(unexpected)))
        require("PyImport_ImportModule" not in undefined,
                "the C engine imports an unapproved Python matcher")
        require(exported == {"PyInit__vm_native"},
                "the C engine exports a sibling or external entry point")
    elif binary == spec["engine"]:
        require(undefined == ZIG_ENGINE_UNDEFINED,
                "Zig has foreign or missing Unicode and libc dependencies")
        require(exported == ZIG_ENGINE_EXPORTS,
                "Zig exports a foreign or incomplete matching ABI")
    else:
        unexpected = {
            name for name in undefined
            if name not in ZIG_ENGINE_EXPORTS
            and name not in SYSTEM_NATIVE_UNDEFINED
            and not name.startswith(("Py", "_Py"))
        }
        require(not unexpected,
                "the Zig bridge resolves foreign symbols: "
                + str(sorted(unexpected)))
        require(exported == {"PyInit__zig_bridge"},
                "the Zig bridge exports a sibling or external entry point")
        require(undefined & ZIG_ENGINE_EXPORTS == ZIG_BRIDGE_REFERENCES,
                "Zig does not reference all and only its own native matcher")
        require("PyImport_ImportModule" not in undefined,
                "Zig dynamically imports an unapproved Python matcher")
    return {
        "defined_exports": sorted(exported),
        "undefined_symbol_count": len(undefined),
        "owned_engine_references": sorted(undefined & spec["exports"]),
    }


def verify_runtime(*, synthetic: bool = False) -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == PYTHON_VERSION
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == SOURCE_ABSOLUTE,
            "run the exact isolated pinned CPython and exact V3 audit source")
    if not synthetic:
        require(os.path.realpath(ROOT) == ROOT
                and os.path.realpath(sys.executable) == PINNED_PYTHON
                and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
                "the exact audit root, interpreter, or source is a symlink")


def read_owned(
    relative: str, expected: str, *, maximum: int,
) -> tuple[bytes, dict[str, Any]]:
    parts = owned_relative(relative)
    checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "an exact bounded caller-pinned source or binary is mandatory")
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
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact ownership root is not a real directory")
        for component in parts[:-1]:
            current = os.open(component, directory_flags, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an owned source parent was replaced with a symlink")
        descriptor = os.open(parts[-1], regular_flags, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino)
                == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum,
                "a caller-pinned source or binary is not its exact owned file")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "an independently owned artifact was truncated")
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "an independently owned artifact has a hidden suffix")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "a caller-pinned native artifact changed during authentication")
        raw = b"".join(chunks)
        require(hashlib.sha256(raw).hexdigest() == expected,
                "an exact caller-pinned owner changed: " + relative)
        return raw, {
            "relative": relative,
            "sha256": expected,
            "bytes": len(raw),
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_external(
    absolute: str, expected: str, *, maximum: int,
) -> dict[str, Any]:
    checked_digest(expected, absolute)
    require(type(absolute) is str and os.path.isabs(absolute)
            and os.path.abspath(absolute) == absolute
            and os.path.realpath(absolute) == absolute
            and 0 < maximum <= MAX_BINARY_BYTES,
            "an exact pinned CPython external owner is mandatory")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= maximum,
                "a pinned standard CPython owner is not a bounded regular file")
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "a pinned standard CPython owner was truncated")
            hasher.update(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "a pinned standard CPython owner has a concealed suffix")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size)
                and hasher.hexdigest() == expected,
                "the pinned standard CPython owner was substituted")
        return {
            "path": absolute,
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        os.close(descriptor)


def inspect_readelf(relative: str, option: str, family: str) -> str:
    spec = family_spec(family)
    require(relative in spec["binaries"]
            and option in {"--dynamic", "--dyn-syms"},
            "an ELF command escaped its exact pinned native family")
    absolute = ROOT + "/" + relative
    try:
        process = subprocess.run(
            [READELF, "--wide", option, absolute],
            cwd=ROOT,
            env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise AuditFailure(
            "pinned readelf could not inspect " + relative
        ) from error
    require(process.returncode == 0 and not process.stderr,
            "pinned readelf rejected the exact native artifact: " + relative)
    require(type(process.stdout) is str
            and len(process.stdout.encode("utf-8")) <= MAX_PROCESS_BYTES,
            "a complete bounded actual ELF observation is mandatory")
    return process.stdout


def authenticate_closure(
    family: str, manifest: Mapping[str, Any], source_pin: str,
) -> dict[str, Any]:
    verify_runtime()
    manifest = validate_manifest(dict(manifest), family)
    checked_digest(source_pin, "exact independent V3 audit controller")
    source_bytes: dict[str, bytes] = {}
    source_owners: dict[str, dict[str, Any]] = {}
    for relative, pinned in manifest["source_sha256"].items():
        raw, owner = read_owned(relative, pinned, maximum=MAX_SOURCE_BYTES)
        source_bytes[relative] = raw
        source_owners[relative] = owner
    native_owners: dict[str, dict[str, Any]] = {}
    for relative, pinned in manifest["native_sha256"].items():
        _, owner = read_owned(relative, pinned, maximum=MAX_BINARY_BYTES)
        native_owners[relative] = owner
    policies: dict[str, dict[str, Any]] = {}
    for relative, pinned in IMMUTABLE_POLICY_SHA256.items():
        _, policies[relative] = read_owned(
            relative, pinned, maximum=MAX_SOURCE_BYTES
        )
    _, oracle = read_owned(
        SOURCE_RELATIVE, source_pin, maximum=MAX_SOURCE_BYTES
    )
    python = read_external(
        PINNED_PYTHON, PINNED_PYTHON_SHA256, maximum=MAX_BINARY_BYTES
    )
    return {
        "family": family,
        "manifest": dict(manifest),
        "source_bytes": source_bytes,
        "source_owners": source_owners,
        "native_owners": native_owners,
        "policy_owners": policies,
        "oracle_owner": oracle,
        "python_owner": python,
    }


def serializable_owners(closure: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "family": closure["family"],
        "manifest": closure["manifest"],
        "source_owners": closure["source_owners"],
        "native_owners": closure["native_owners"],
        "policy_owners": closure["policy_owners"],
        "oracle_owner": closure["oracle_owner"],
        "python_owner": closure["python_owner"],
    }


def validate_owner(value: Any, relative: str, source_hash: str) -> None:
    require(type(value) is dict and set(value) == {
        "relative", "sha256", "bytes", "device", "inode",
    } and value.get("relative") == relative
      and value.get("sha256") == source_hash
      and type(value.get("bytes")) is int and value["bytes"] > 0
      and type(value.get("device")) is int and value["device"] >= 0
      and type(value.get("inode")) is int and value["inode"] > 0,
      "an actual complete pinned file owner was forged: " + relative)


def validate_external_owner(value: Any, absolute: str, source_hash: str) -> None:
    require(type(value) is dict and set(value) == {
        "path", "sha256", "bytes", "device", "inode",
    } and value.get("path") == absolute
      and value.get("sha256") == source_hash
      and type(value.get("bytes")) is int and value["bytes"] > 0
      and type(value.get("device")) is int and value["device"] >= 0
      and type(value.get("inode")) is int and value["inode"] > 0,
      "a genuine pinned standard CPython file owner was forged")


def validate_serializable_owners(
    value: Any, family: str, manifest: Mapping[str, Any], source_pin: str,
) -> dict[str, Any]:
    require(type(value) is dict and set(value) == {
        "family", "manifest", "source_owners", "native_owners",
        "policy_owners", "oracle_owner", "python_owner",
    } and value.get("family") == family,
      "a complete candidate and policy ownership closure is mandatory")
    validate_manifest(value["manifest"], family)
    require(value["manifest"] == manifest,
            "the caller-pinned native manifest was substituted")
    sources = value["source_owners"]
    binaries = value["native_owners"]
    policies = value["policy_owners"]
    require(type(sources) is dict
            and set(sources) == set(manifest["source_sha256"]),
            "a pinned family source owner was omitted")
    require(type(binaries) is dict
            and set(binaries) == set(manifest["native_sha256"]),
            "a pinned native binary owner was omitted")
    require(type(policies) is dict
            and set(policies) == set(IMMUTABLE_POLICY_SHA256),
            "an immutable V2 or V5 ownership policy was omitted")
    for relative, pinned in manifest["source_sha256"].items():
        validate_owner(sources.get(relative), relative, pinned)
    for relative, pinned in manifest["native_sha256"].items():
        validate_owner(binaries.get(relative), relative, pinned)
    for relative, pinned in IMMUTABLE_POLICY_SHA256.items():
        validate_owner(policies.get(relative), relative, pinned)
    validate_owner(value["oracle_owner"], SOURCE_RELATIVE, source_pin)
    validate_external_owner(
        value["python_owner"], PINNED_PYTHON, PINNED_PYTHON_SHA256
    )
    return value


def inspect_actual_sources(
    family: str, manifest: Mapping[str, Any], source_pin: str,
) -> dict[str, Any]:
    spec = family_spec(family)
    closure = authenticate_closure(family, manifest, source_pin)
    source_bytes = closure["source_bytes"]
    try:
        sources = {
            name: raw.decode("utf-8") for name, raw in source_bytes.items()
        }
    except UnicodeDecodeError as error:
        raise AuditFailure(
            family + " has an invalid UTF-8 native source closure"
        ) from error
    adapter = adapter_imports(sources[spec["adapter"]], family)
    bridge = inspect_bridge(sources[spec["bridge_source"]], family)
    implementation: dict[str, Any]
    if family == "rust":
        implementation = {
            "cargo": inspect_cargo(
                sources["candidates/rust/Cargo.toml"],
                sources["candidates/rust/Cargo.lock"],
            ),
            "engine": inspect_rust_sources({
                path: sources[path] for path in RUST_SOURCE_FILES
            }),
        }
    elif family == "zig":
        implementation = {
            "engine": inspect_zig_source(
                sources["candidates/zig/mini_regex.zig"]
            ),
        }
    else:
        implementation = {
            "engine": "independently owned Python compiler and native C VM",
        }
    native: dict[str, Any] = {}
    for relative in spec["binaries"]:
        native[relative] = {
            **parse_dynamic_section(
                inspect_readelf(relative, "--dynamic", family),
                family, relative,
            ),
            **parse_dynamic_symbols(
                inspect_readelf(relative, "--dyn-syms", family),
                family, relative,
            ),
        }
    result = {
        "family": family,
        "owners": serializable_owners(closure),
        "adapter": adapter,
        "bridge": bridge,
        "implementation": implementation,
        "native": native,
        "external_regex_package_count": 0,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
    }
    validate_serializable_owners(
        result["owners"], family, manifest, source_pin
    )
    return result


def validate_ctypes_dlopen(
    family: str, value: Any, expected: str,
) -> None:
    require(family == "zig" and type(value) is str
            and os.path.isabs(value) and value == expected
            and os.path.normpath(value) == expected,
            "load only the exact caller-pinned adjacent Zig engine")


def validate_ctypes_dlsym(
    family: str, library_name: Any, symbol: Any, expected: str,
) -> None:
    require(family == "zig" and type(library_name) is str
            and library_name == expected and type(symbol) is str
            and symbol in ZIG_CTYPES_SYMBOLS,
            "resolve only exact family-owned Zig FFI symbols")


def validate_trusted_ctypes() -> dict[str, Any]:
    native = sys.modules.get("_ctypes")
    require(type(native) is types.ModuleType
            and native.__name__ == "_ctypes"
            and getattr(native, "__file__", None) is None,
            "the genuine built-in CPython FFI module was substituted")
    native_spec = getattr(native, "__spec__", None)
    require(native_spec is not None
            and native_spec.name == "_ctypes"
            and native_spec.origin == "built-in"
            and native_spec.loader is importlib.machinery.BuiltinImporter,
            "the genuine built-in CPython FFI loader was substituted")
    require(isinstance(native.dlopen, types.BuiltinFunctionType)
            and native.dlopen.__module__ == "_ctypes"
            and native.dlopen.__name__ == "dlopen"
            and isinstance(native.CFuncPtr, type),
            "the genuine built-in FFI entry points were substituted")
    require(type(ctypes) is types.ModuleType
            and sys.modules.get("ctypes") is ctypes
            and ctypes.__name__ == "ctypes"
            and getattr(ctypes, "__file__", None) == PINNED_CTYPES,
            "the pinned standard CPython ctypes source was substituted")
    specification = getattr(ctypes, "__spec__", None)
    loader = getattr(specification, "loader", None)
    require(specification is not None and specification.name == "ctypes"
            and specification.origin == PINNED_CTYPES
            and isinstance(loader, importlib.machinery.SourceFileLoader)
            and loader.name == "ctypes" and loader.path == PINNED_CTYPES,
            "the genuine standard ctypes source loader was substituted")
    values = vars(ctypes)
    cdll = values.get("CDLL")
    pydll = values.get("PyDLL")
    require(isinstance(cdll, type) and isinstance(pydll, type)
            and cdll.__module__ == "ctypes"
            and pydll.__module__ == "ctypes"
            and pydll.__bases__ == (cdll,)
            and getattr(cdll.__init__, "__globals__", None) is values
            and cdll.__init__.__code__.co_filename == PINNED_CTYPES
            and values.get("_dlopen") is native.dlopen
            and values.get("_CFuncPtr") is native.CFuncPtr,
            "the genuine standard ctypes API or dlopen entry was substituted")
    for method in ("__init__", "__getattr__", "__getitem__", "_load_library"):
        actual = vars(cdll).get(method)
        require(isinstance(actual, types.FunctionType)
                and actual.__globals__ is values
                and actual.__code__.co_filename == PINNED_CTYPES,
                "a genuine standard ctypes loading method was substituted: "
                + method)
    loader_type = values.get("LibraryLoader")
    require(isinstance(loader_type, type)
            and loader_type.__module__ == "ctypes",
            "the genuine standard FFI library loader was substituted")
    for name, expected in (("cdll", cdll), ("pydll", pydll)):
        instance = values.get(name)
        require(type(instance) is loader_type
                and set(vars(instance)) == {"_dlltype"}
                and vars(instance)["_dlltype"] is expected,
                "a cached ambient ctypes loader was substituted: " + name)
    pythonapi = values.get("pythonapi")
    require(type(pythonapi) is pydll,
            "the genuine standard Python FFI handle was substituted")
    items = tuple(vars(pythonapi).items())
    require(all(type(name) is str for name, _ in items),
            "the genuine Python FFI handle contains a forged attribute")
    attributes = dict(items)
    require(set(attributes) == {"_name", "_handle", "_FuncPtr"}
            and isinstance(attributes.get("_FuncPtr"), type)
            and issubclass(attributes["_FuncPtr"], native.CFuncPtr)
            and attributes["_FuncPtr"].__module__ == "ctypes"
            and attributes.get("_name") is None
            and type(attributes.get("_handle")) is int
            and attributes["_handle"] > 0,
            "an ambient or forged standard Python FFI handle was supplied")
    return {
        "source": PINNED_CTYPES,
        "source_sha256": PINNED_CTYPES_SHA256,
        "native_module": "_ctypes",
        "native_origin": "built-in",
        "pythonapi_initialized": True,
        "foreign_loads_permitted": False,
    }


def forbid_captured_original_matchers(
    candidate: types.ModuleType,
    bridge: types.ModuleType,
    originals: tuple[Any, ...],
    family: str,
) -> int:
    spec = family_spec(family)
    owned_names = {spec["module"], spec["bridge_module"]}
    original_types = tuple(item for item in originals if isinstance(item, type))
    owned_class_ids: set[int] = set()
    for module in (candidate, bridge):
        for item in tuple(vars(module).values()):
            if isinstance(item, type):
                owned_class_ids.add(id(item))
                for parent in item.__mro__[1:]:
                    if getattr(parent, "__module__", None) in (
                        *owned_names, "re", "_sre",
                    ):
                        owned_class_ids.add(id(parent))
    visited: set[int] = set()

    def visit(value: Any, depth: int) -> None:
        require(depth <= 24,
                "a candidate matcher escaped in an excessive reference chain")
        identity = id(value)
        if identity in visited:
            return
        visited.add(identity)
        require(len(visited) <= 40_000,
                "the independently owned object graph exceeded its bound")
        require(all(value is not original for original in originals),
                "the candidate captured a genuine CPython regex engine")
        if original_types and not isinstance(value, type):
            require(not isinstance(value, original_types),
                    "the candidate captured a compiled standard regex")
        if isinstance(value, types.ModuleType):
            require(not forbidden_module(value.__name__, family),
                    "the candidate retained a sibling or foreign regex module")
            if value.__name__ not in owned_names:
                return
            for name, item in tuple(vars(value).items()):
                if name not in {"__builtins__", "__loader__", "__spec__"}:
                    visit(item, depth + 1)
        elif isinstance(value, types.FunctionType):
            if value.__module__ in owned_names:
                for item in value.__defaults__ or ():
                    visit(item, depth + 1)
                for item in (value.__kwdefaults__ or {}).values():
                    visit(item, depth + 1)
                for cell in value.__closure__ or ():
                    try:
                        visit(cell.cell_contents, depth + 1)
                    except ValueError:
                        continue
        elif isinstance(value, types.MethodType):
            visit(value.__func__, depth + 1)
            visit(value.__self__, depth + 1)
        elif isinstance(value, (staticmethod, classmethod)):
            visit(value.__func__, depth + 1)
        elif isinstance(value, property):
            for item in (value.fget, value.fset, value.fdel):
                if item is not None:
                    visit(item, depth + 1)
        elif isinstance(value, type):
            if id(value) not in owned_class_ids:
                return
            for name, item in tuple(vars(value).items()):
                if name not in {"__dict__", "__weakref__", "__doc__"}:
                    visit(item, depth + 1)
            for parent in value.__mro__[1:]:
                if id(parent) in owned_class_ids:
                    visit(parent, depth + 1)
        elif isinstance(value, (dict, types.MappingProxyType)):
            for index, (key, item) in enumerate(tuple(value.items())):
                require(index < 20_000,
                        "an independently owned object mapping is unbounded")
                visit(key, depth + 1)
                visit(item, depth + 1)
        elif isinstance(value, (tuple, list, set, frozenset)):
            for index, item in enumerate(tuple(value)):
                require(index < 20_000,
                        "an independently owned object collection is unbounded")
                visit(item, depth + 1)
        elif id(type(value)) in owned_class_ids:
            try:
                attributes = vars(value)
            except TypeError:
                return
            visit(attributes, depth + 1)

    visit(candidate, 0)
    visit(bridge, 0)
    return len(visited)


class ImportBlocker(importlib.abc.MetaPathFinder):
    def __init__(self, family: str, violations: list[str]) -> None:
        self.family = family
        self.violations = violations

    def find_spec(
        self, fullname: str, path: Any = None, target: Any = None,
    ) -> None:
        del path, target
        if forbidden_module(fullname, self.family):
            self.violations.append("meta-path:" + fullname)
            raise AuditFailure(
                "the candidate attempted a foreign matcher import: " + fullname
            )
        return None


def worker_run(
    family: str, manifest: Mapping[str, Any], source_pin: str,
) -> dict[str, Any]:
    spec = family_spec(family)
    closure = authenticate_closure(family, manifest, source_pin)
    owners = serializable_owners(closure)
    validate_serializable_owners(owners, family, manifest, source_pin)
    ffi = validate_trusted_ctypes() if family == "zig" else None
    if family == "zig":
        ctypes_owner = read_external(
            PINNED_CTYPES, PINNED_CTYPES_SHA256,
            maximum=MAX_SOURCE_BYTES,
        )
    else:
        ctypes_owner = None

    old_re = sys.modules.get("re")
    old_sre = sys.modules.get("_sre")
    originals = tuple(item for item in (
        old_re, old_sre,
        getattr(old_re, "Pattern", None),
        getattr(old_re, "Match", None),
    ) if item is not None)
    removed = tuple(
        name for name in tuple(sys.modules) if forbidden_module(name, family)
    )
    for name in removed:
        sys.modules.pop(name, None)

    violations: list[str] = []
    import_checks = 0
    opened_paths: list[str] = []
    resolved_symbols: list[str] = []
    owned_handles: list[Any] = []
    exact_engine = ROOT + "/" + spec["engine"]
    original_import = builtins.__import__
    original_import_module = importlib.import_module
    blocker = ImportBlocker(family, violations)

    def check_name(name: Any, mechanism: str) -> None:
        if forbidden_module(name, family):
            violations.append(mechanism + ":" + str(name))
            raise AuditFailure(
                "a native family attempted forbidden "
                + mechanism + ": " + str(name)
            )

    def guarded_import(
        name: str, globals: Any = None, locals: Any = None,
        fromlist: Any = (), level: int = 0,
    ) -> Any:
        nonlocal import_checks
        import_checks += 1
        if level:
            package = globals.get("__package__") \
                if isinstance(globals, dict) else None
            require(type(package) is str,
                    "a relative candidate import lacks a genuine owner")
            try:
                resolved = importlib.util.resolve_name(
                    "." * level + name, package
                )
            except (ImportError, ValueError) as error:
                raise AuditFailure(
                    "an independent native adapter escaped a relative import"
                ) from error
        else:
            resolved = name
        check_name(resolved, "builtins-import")
        if resolved == "candidates":
            for item in fromlist or ():
                require(type(item) is str,
                        "a candidate contains a forged native from-import")
                check_name("candidates." + item, "candidate-from-import")
        return original_import(name, globals, locals, fromlist, level)

    def guarded_import_module(
        name: str, package: str | None = None,
    ) -> Any:
        resolved = (
            importlib.util.resolve_name(name, package)
            if name.startswith(".") and package else name
        )
        check_name(resolved, "importlib-import")
        return original_import_module(name, package)

    def audit_hook(event: str, arguments: tuple[Any, ...]) -> None:
        if event == "import" and arguments and type(arguments[0]) is str:
            check_name(arguments[0], "audit-import")
        elif event == "ctypes.dlopen":
            actual = arguments[0] if arguments else None
            try:
                validate_ctypes_dlopen(family, actual, exact_engine)
                require(not opened_paths,
                        "Zig loaded more than one owned native engine")
            except AuditFailure:
                violations.append("audit-event:ctypes.dlopen")
                raise
            opened_paths.append(actual)
        elif event in {"ctypes.dlsym", "ctypes.dlsym/handle"}:
            library = arguments[0] if arguments else None
            symbol = arguments[1] if len(arguments) > 1 else None
            try:
                require(type(library) is ctypes.CDLL
                        and library is not ctypes.pythonapi
                        and getattr(library, "_handle", None)
                        not in {None, getattr(ctypes.pythonapi, "_handle", None)},
                        "a candidate resolved an ambient process FFI handle")
                validate_ctypes_dlsym(
                    family, getattr(library, "_name", None),
                    symbol, exact_engine,
                )
                require(opened_paths == [exact_engine],
                        "Zig resolved an FFI symbol before its owned engine")
                if owned_handles:
                    require(library is owned_handles[0],
                            "Zig resolved FFI symbols from a second handle")
                else:
                    owned_handles.append(library)
                require(symbol not in resolved_symbols,
                        "Zig resolved an owned native symbol more than once")
            except AuditFailure:
                violations.append("audit-event:ctypes.dlsym")
                raise
            resolved_symbols.append(symbol)
        elif event in {
            "os.system", "os.fork", "os.posix_spawn", "subprocess.Popen",
        } or event.startswith("os.exec"):
            violations.append("audit-event:" + event)
            raise AuditFailure(
                "a candidate attempted native process delegation: " + event
            )

    sys.addaudithook(audit_hook)
    sys.meta_path.insert(0, blocker)
    builtins.__import__ = guarded_import
    importlib.import_module = guarded_import_module

    package = types.ModuleType("candidates")
    package.__package__ = "candidates"
    package.__path__ = [ROOT + "/candidates"]
    sys.modules["candidates"] = package
    bridge_path = ROOT + "/" + spec["bridge"]
    bridge_spec = importlib.util.spec_from_file_location(
        spec["bridge_module"], bridge_path
    )
    require(bridge_spec is not None
            and isinstance(bridge_spec.loader,
                           importlib.machinery.ExtensionFileLoader)
            and bridge_spec.origin == bridge_path
            and bridge_spec.name == spec["bridge_module"],
            "the exact caller-pinned native extension loader was substituted")
    bridge = importlib.util.module_from_spec(bridge_spec)
    sys.modules[spec["bridge_module"]] = bridge
    setattr(package, spec["bridge_module"].rsplit(".", 1)[1], bridge)
    bridge_spec.loader.exec_module(bridge)

    adapter_path = ROOT + "/" + spec["adapter"]
    adapter_spec = importlib.util.spec_from_file_location(
        spec["module"], adapter_path
    )
    require(adapter_spec is not None
            and isinstance(adapter_spec.loader,
                           importlib.machinery.SourceFileLoader)
            and adapter_spec.origin == adapter_path
            and adapter_spec.name == spec["module"],
            "the exact caller-pinned Python adapter loader was substituted")
    candidate = importlib.util.module_from_spec(adapter_spec)
    sys.modules[spec["module"]] = candidate
    setattr(package, spec["module"].rsplit(".", 1)[1], candidate)
    adapter_spec.loader.exec_module(candidate)

    require(candidate.Match is bridge.Match,
            family + " does not own its actual native Match")
    require(all(candidate.Pattern is not item and candidate.Match is not item
                for item in originals),
            family + " captured original standard-library matching types")
    require(candidate.Pattern.__module__ == "re"
            and candidate.Match.__module__ == "re",
            family + " does not preserve its own public-compatible type names")
    if family == "zig":
        require(opened_paths == [exact_engine]
                and frozenset(resolved_symbols) == ZIG_CTYPES_SYMBOLS
                and len(resolved_symbols) == len(ZIG_CTYPES_SYMBOLS)
                and len(owned_handles) == 1
                and candidate._NATIVE.library is owned_handles[0],
                "Zig delegated, loaded an ambient handle, or omitted FFI symbols")
    else:
        require(not opened_paths and not resolved_symbols and not owned_handles,
                family + " performed a forbidden native dynamic load")

    checks = 0

    def check(condition: Any, message: str) -> None:
        nonlocal checks
        require(condition, message)
        checks += 1

    pattern = candidate.compile(r"(?P<word>[A-Za-z]+)-(\d+)")
    check(type(pattern) is candidate.Pattern,
          family + " returned a foreign compiled pattern")
    match = pattern.search("xx alpha-42 yy")
    check(type(match) is bridge.Match,
          family + " returned a foreign search Match")
    check(match.group(0, "word", 2) == ("alpha-42", "alpha", "42"),
          family + " delegated or corrupted numbered and named captures")
    check(match.span("word") == (3, 8),
          family + " corrupted its independently matched capture span")
    check(match.expand(r"\g<word>:\2") == "alpha:42",
          family + " delegated its replacement expansion")
    check(candidate.fullmatch(r"\w+", "hello_42") is not None,
          family + " did not perform a native fullmatch")
    check(candidate.match(r"a+", "aaab").span() == (0, 3),
          family + " did not perform a native match")
    check(candidate.search(rb"a+", memoryview(b"--aaa--")).span() == (2, 5),
          family + " did not perform genuine bytes-buffer matching")
    check(candidate.findall(r"\d+", "a12b345") == ["12", "345"],
          family + " did not perform native findall")
    check([item.span() for item in candidate.finditer(r"\d+", "a12b345")]
          == [(1, 3), (4, 7)],
          family + " did not perform independent native iteration")
    check(candidate.split(r"\s+", "a  b\tc") == ["a", "b", "c"],
          family + " did not perform independent splitting")
    callback_matches: list[Any] = []

    def replacement(item: Any) -> str:
        callback_matches.append(item)
        return item.group(0).upper()

    check(candidate.sub(r"[a-z]+", replacement, "ab 12 cd") == "AB 12 CD",
          family + " does not support genuine user replacement callbacks")
    check(len(callback_matches) == 2
          and all(type(item) is bridge.Match for item in callback_matches),
          family + " sent a foreign Match to a user callback")
    check(candidate.subn(r"\d+", "#", "a12b345") == ("a#b#", 2),
          family + " did not perform independent counted replacement")
    scanner = candidate.compile(r"\w+").scanner("aa bb")
    check(type(scanner).__module__ == "_sre"
          and type(scanner).__name__ == "SRE_Scanner",
          family + " has no compatible independently owned native scanner")
    first = scanner.search()
    second = scanner.search()
    check(type(first) is bridge.Match and type(second) is bridge.Match
          and first.group() == "aa" and second.group() == "bb",
          family + " returned a foreign or incorrect native scanner Match")
    graph_checks = forbid_captured_original_matchers(
        candidate, bridge, originals, family
    )
    check(graph_checks > 0,
          family + " did not inspect its actual native object graph")
    check("_sre" not in sys.modules,
          family + " dynamically loaded the original standard engine")
    check(frozenset(
        name for name in sys.modules if name.startswith("candidates.")
    ) == {spec["bridge_module"], spec["module"]},
          family + " borrowed a sibling candidate or native bridge")
    check(not any(forbidden_module(name, family) for name in sys.modules),
          family + " retained an external regex or native process module")
    check(not violations,
          family + " attempted forbidden runtime imports or process delegation")

    result = {
        "schema": SCHEMA + "-isolated-worker",
        "status": "PASS",
        "family": family,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "manifest": dict(manifest),
        "owners": owners,
        "runtime_checks": checks,
        "owned_graph_checks": graph_checks,
        "guarded_import_calls": import_checks,
        "forbidden_import_or_execution_count": len(violations),
        "removed_preexisting_forbidden_module_count": len(removed),
        "caller_replacement_callback_supported": True,
        "owned_public_re_names_supported": True,
        "owned_public_sre_scanner_name_supported": True,
        "actual_standard_library_engine_loaded": False,
        "candidate_modules": sorted(
            name for name in sys.modules if name.startswith("candidates.")
        ),
        "owned_ctypes_library_load_count": len(opened_paths),
        "owned_ctypes_symbols": sorted(resolved_symbols),
        "trusted_ctypes": ffi,
        "trusted_ctypes_owner": ctypes_owner,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return validate_worker(
        result, family, manifest, source_pin, expected_pid=result["pid"]
    )


def validate_worker(
    value: Any,
    family: str,
    manifest: Mapping[str, Any],
    source_pin: str,
    *,
    expected_pid: int,
) -> dict[str, Any]:
    spec = family_spec(family)
    require(type(expected_pid) is int and expected_pid > 0,
            "an actual independently isolated candidate PID is mandatory")
    expected = {
        "schema": SCHEMA + "-isolated-worker",
        "status": "PASS",
        "family": family,
        "pid": expected_pid,
        "oracle_source_sha256": source_pin,
        "manifest": dict(manifest),
        "forbidden_import_or_execution_count": 0,
        "caller_replacement_callback_supported": True,
        "owned_public_re_names_supported": True,
        "owned_public_sre_scanner_name_supported": True,
        "actual_standard_library_engine_loaded": False,
        "candidate_modules": sorted([spec["bridge_module"], spec["module"]]),
        "owned_ctypes_library_load_count": 1 if family == "zig" else 0,
        "owned_ctypes_symbols": sorted(ZIG_CTYPES_SYMBOLS)
        if family == "zig" else [],
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(type(value) is dict and set(value) == set(expected) | {
        "owners", "runtime_checks", "owned_graph_checks",
        "guarded_import_calls", "removed_preexisting_forbidden_module_count",
        "trusted_ctypes", "trusted_ctypes_owner",
    }, "the complete isolated native audit worker was forged")
    for name, original in expected.items():
        require(value.get(name) == original,
                "a genuine isolated native worker changed: " + name)
    validate_serializable_owners(
        value["owners"], family, manifest, source_pin
    )
    for field, minimum in (
        ("runtime_checks", 20),
        ("owned_graph_checks", 1),
        ("guarded_import_calls", 1),
        ("removed_preexisting_forbidden_module_count", 0),
    ):
        number = value[field]
        require(type(number) is int and number >= minimum,
                "an actual continuous native ownership check was hidden: "
                + field)
    if family == "zig":
        trusted = value["trusted_ctypes"]
        require(type(trusted) is dict and trusted == {
            "source": PINNED_CTYPES,
            "source_sha256": PINNED_CTYPES_SHA256,
            "native_module": "_ctypes",
            "native_origin": "built-in",
            "pythonapi_initialized": True,
            "foreign_loads_permitted": False,
        }, "the trusted genuine Zig ctypes standard FFI was substituted")
        validate_external_owner(
            value["trusted_ctypes_owner"],
            PINNED_CTYPES, PINNED_CTYPES_SHA256,
        )
    else:
        require(value["trusted_ctypes"] is None
                and value["trusted_ctypes_owner"] is None,
                family + " attempted a borrowed FFI dynamic engine")
    return value


def encode_stream(value: bytes) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
            "an exact bounded native worker stream is mandatory")
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict and set(value) == {
        "base64", "bytes", "sha256", "complete",
    } and type(value.get("base64")) is str
      and type(value.get("bytes")) is int
      and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
      and valid_digest(value.get("sha256"))
      and value.get("complete") is True,
      "a complete genuine native worker stream was hidden: " + label)
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise AuditFailure(
            "an exact native worker stream is not valid base64: " + label
        ) from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == value["sha256"]
            and base64.b64encode(raw).decode("ascii") == value["base64"],
            "a complete native worker stream was substituted: " + label)
    return raw


def validate_process_evidence(
    evidence: Any, worker: Mapping[str, Any], family: str,
) -> dict[str, Any]:
    require(type(evidence) is dict and set(evidence) == {
        "family", "pid", "returncode", "stdout", "stderr",
    } and evidence.get("family") == family
      and type(evidence.get("pid")) is int and evidence["pid"] > 0
      and evidence["pid"] == worker.get("pid")
      and evidence.get("returncode") == 0,
      "a genuine independently isolated native worker was forged")
    stdout = decode_stream(evidence["stdout"], family + " stdout")
    stderr = decode_stream(evidence["stderr"], family + " stderr")
    require(stderr == b"" and stdout == canonical(dict(worker)),
            "complete native process evidence differs from its worker")
    return evidence


def manifest_arguments(manifest: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for path, source_hash in manifest["source_sha256"].items():
        values.extend(("--source-pin", path + "=" + source_hash))
    for path, native_hash in manifest["native_sha256"].items():
        values.extend(("--native-pin", path + "=" + native_hash))
    return values


def run_isolated_worker(
    family: str, manifest: Mapping[str, Any], source_pin: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    arguments = [
        PINNED_PYTHON, "-I", "-B", SOURCE_ABSOLUTE,
        "--internal-audit-worker",
        "--family", family,
        "--oracle-source-sha256", source_pin,
        "--candidate-source-sha256", manifest["candidate_source_sha256"],
        "--native-engine-sha256", manifest["native_engine_sha256"],
        "--native-bridge-sha256", manifest["native_bridge_sha256"],
        *manifest_arguments(manifest),
    ]
    try:
        process = subprocess.Popen(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            cwd=ROOT,
            env={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            },
        )
        stdout, stderr = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        raise WorkerFailure(
            "an isolated pinned native candidate worker could not start",
            {
                "family": family,
                "error_type": type(error).__qualname__,
                "error": str(error),
            },
        ) from error
    evidence = {
        "family": family,
        "pid": process.pid,
        "returncode": process.returncode,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    if process.returncode != 0 or stderr:
        raise WorkerFailure(
            "an independently owned candidate rejected its runtime audit",
            evidence,
        )
    try:
        worker = validate_worker(
            decode_canonical(stdout, family + " runtime"),
            family, manifest, source_pin,
            expected_pid=process.pid,
        )
        validate_process_evidence(evidence, worker, family)
    except (AuditFailure, TypeError, ValueError, KeyError) as error:
        evidence["validation_error"] = {
            "type": type(error).__qualname__, "message": str(error),
        }
        raise WorkerFailure(
            "the complete independent runtime audit evidence was rejected",
            evidence,
        ) from error
    return worker, evidence


def run_audit(
    family: str, manifest: Mapping[str, Any], source_pin: str,
) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "exact dynamically caller-pinned V3 audit")
    manifest = validate_manifest(dict(manifest), family)
    before = inspect_actual_sources(family, manifest, source_pin)
    worker, process = run_isolated_worker(family, manifest, source_pin)
    after = inspect_actual_sources(family, manifest, source_pin)
    require(before == after,
            "the exact family-owned closure changed during its live audit")
    validate_process_evidence(process, worker, family)
    require(worker["owners"] == before["owners"],
            "the isolated worker did not use the exact inspected native closure")
    return {
        "schema": SCHEMA + "-actual-audit",
        "oracle": ORACLE_NAME,
        "status": "PASS",
        "python": {
            "implementation": "cpython",
            "version": list(PYTHON_VERSION),
            "executable": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
        },
        "oracle_source_sha256": source_pin,
        "family": family,
        "candidate_module": family_spec(family)["module"],
        "manifest": dict(manifest),
        "ownership": before,
        "runtime": worker,
        "process": process,
        "unchanged_before_after": True,
        "actual_candidate_workers": 1,
        "external_regex_package_count": 0,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


class SourceOnlyBoundary:
    """Fail closed on genuine file, import, process, clock, or thread effects."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "file_reads": 0,
            "file_writes": 0,
            "processes": 0,
            "candidate_imports": 0,
            "dynamic_imports": 0,
            "threads": 0,
            "clock_samples": 0,
            "garbage_collections": 0,
            "randomness": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)
        self.originals.append((owner, name, previous))

        def denied(*args: Any, **kwargs: Any) -> Any:
            chosen = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(x in mode for x in "wax+"):
                    chosen = "file_writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT
                    | os.O_TRUNC | os.O_APPEND
                ):
                    chosen = "file_writes"
            elif category == "dynamic_imports" and args:
                requested = args[0]
                if type(requested) is str and (
                    requested == "candidates"
                    or requested.startswith("candidates.")
                    or requested.partition(".")[0]
                    in FORBIDDEN_MODULE_ROOTS
                ):
                    chosen = "candidate_imports"
            self.blocked[chosen] += 1
            raise SourceOnlyError(
                "synthetic ownership controls cannot perform " + chosen
            )

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        guards = (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "readlink", "file_reads"),
            (os, "replace", "file_writes"),
            (os, "rename", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (os, "fork", "processes"),
            (os, "system", "processes"),
            (os, "posix_spawn", "processes"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clock_samples"),
            (time, "time_ns", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "monotonic_ns", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
            (time, "perf_counter_ns", "clock_samples"),
            (gc, "collect", "garbage_collections"),
            (os, "urandom", "randomness"),
            (importlib, "import_module", "dynamic_imports"),
            (builtins, "__import__", "dynamic_imports"),
        )
        for owner, name, category in guards:
            self.install(owner, name, category)
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, previous in reversed(self.originals):
            setattr(owner, name, previous)
        self.originals.clear()
        return False


def synthetic_dynamic(family: str, binary: str) -> str:
    needed, paths = expected_dynamic(family, binary)
    return "\n".join(
        ["0x1 (NEEDED) Shared library: [" + name + "]"
         for name in sorted(needed)]
        + ["0x1 (RUNPATH) Library runpath: [" + path + "]"
           for path in paths]
    )


def synthetic_symbols(family: str, binary: str) -> str:
    spec = family_spec(family)
    if family == "rust" and binary == spec["engine"]:
        exports = RUST_ENGINE_EXPORTS
        undefined = {"Py_GetRecursionLimit"}
    elif family == "rust":
        exports = {"PyInit__rust_bridge"}
        undefined = {
            "PyImport_ImportModule", "PyObject_CallOneArg", "rebar_compile",
            "rebar_compile_scanner", "rebar_match", "rebar_free",
        }
    elif family == "c":
        exports = {"PyInit__vm_native"}
        undefined = {"PyObject_CallOneArg", "memcpy", "__ctype_b_loc"}
    elif binary == spec["engine"]:
        exports = ZIG_ENGINE_EXPORTS
        undefined = ZIG_ENGINE_UNDEFINED
    else:
        exports = {"PyInit__zig_bridge"}
        undefined = ZIG_BRIDGE_REFERENCES | {
            "PyObject_CallOneArg", "memcpy",
        }
    lines: list[str] = []
    for number, name in enumerate(sorted(exports), start=1):
        lines.append(
            str(number) + ": 0000000000000001 1 FUNC GLOBAL DEFAULT 14 "
            + name
        )
    for number, name in enumerate(sorted(undefined), start=len(lines) + 1):
        lines.append(
            str(number) + ": 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
            + name
        )
    return "\n".join(lines)


def synthetic_adapter(family: str) -> str:
    spec = family_spec(family)
    lines = ["import " + name for name in sorted(spec["imports"])]
    for module, name, alias in sorted(
        spec["from_imports"], key=lambda item: (
            item[0], item[1], item[2] or ""
        )
    ):
        suffix = " as " + alias if alias else ""
        lines.append("from " + module + " import " + name + suffix)
    if family == "zig":
        lines.extend([
            "class _Native:",
            "    def __init__(self):",
            '        path = os.path.join(os.path.dirname(__file__), "_zig_probe.so")',
            "        self.library = ctypes.CDLL(path)",
            "        lib = self.library",
            *[
                "        lib." + symbol + ".restype = ctypes.c_void_p"
                for symbol in sorted(ZIG_CTYPES_SYMBOLS)
            ],
        ])
    else:
        lines.extend([
            "def replacement_callback(callback, match):",
            "    return callback(match)",
        ])
    return "\n".join(lines) + "\n"


def synthetic_bridge(family: str) -> str:
    spec = family_spec(family)
    lines = ["#include <" + name + ">" for name in sorted(spec["headers"])]
    if family == "rust":
        lines.extend(
            'PyImport_ImportModule("' + name + '");'
            for name in ("copyreg", "functools", "inspect")
        )
    scanner = "name" if family == "zig" else "tp_name"
    lines.extend([
        'OwnedScanner = { .' + scanner + ' = "_sre.SRE_Scanner" };',
        'OwnedMatch = { .tp_name = "re.Match" };',
        'owned_match_attribute = { "re", owned_descriptor };',
        "PyObject_CallOneArg(user_replacement_callback, owned_match);",
    ])
    return "\n".join(lines) + "\n"


def synthetic_pin(family: str, relative: str) -> str:
    return hashlib.sha256(
        ("independent-v3-synthetic:" + family + ":" + relative).encode("utf-8")
    ).hexdigest()


def synthetic_manifest(family: str) -> dict[str, Any]:
    spec = family_spec(family)
    source_entries = [
        path + "=" + synthetic_pin(family, path)
        for path in spec["sources"]
    ]
    native_entries = [
        path + "=" + synthetic_pin(family, path)
        for path in spec["binaries"]
    ]
    return validate_family_pins(
        family,
        synthetic_pin(family, spec["adapter"]),
        synthetic_pin(family, spec["engine"]),
        synthetic_pin(family, spec["bridge"]),
        source_entries,
        native_entries,
    )


def synthetic_owner(relative: str, source_hash: str, index: int) -> dict[str, Any]:
    return {
        "relative": relative,
        "sha256": source_hash,
        "bytes": 4096 + index,
        "device": 11,
        "inode": 2000 + index,
    }


def synthetic_owners(
    family: str, manifest: Mapping[str, Any], source_pin: str,
) -> dict[str, Any]:
    counter = 0
    sources: dict[str, dict[str, Any]] = {}
    for path, pinned in manifest["source_sha256"].items():
        counter += 1
        sources[path] = synthetic_owner(path, pinned, counter)
    binaries: dict[str, dict[str, Any]] = {}
    for path, pinned in manifest["native_sha256"].items():
        counter += 1
        binaries[path] = synthetic_owner(path, pinned, counter)
    policies: dict[str, dict[str, Any]] = {}
    for path, pinned in IMMUTABLE_POLICY_SHA256.items():
        counter += 1
        policies[path] = synthetic_owner(path, pinned, counter)
    counter += 1
    return {
        "family": family,
        "manifest": dict(manifest),
        "source_owners": sources,
        "native_owners": binaries,
        "policy_owners": policies,
        "oracle_owner": synthetic_owner(SOURCE_RELATIVE, source_pin, counter),
        "python_owner": {
            "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
            "bytes": 8192,
            "device": 11,
            "inode": 7001,
        },
    }


def synthetic_worker(
    family: str, manifest: Mapping[str, Any], source_pin: str, pid: int,
) -> dict[str, Any]:
    spec = family_spec(family)
    zig = family == "zig"
    ffi = {
        "source": PINNED_CTYPES,
        "source_sha256": PINNED_CTYPES_SHA256,
        "native_module": "_ctypes",
        "native_origin": "built-in",
        "pythonapi_initialized": True,
        "foreign_loads_permitted": False,
    } if zig else None
    ffi_owner = {
        "path": PINNED_CTYPES,
        "sha256": PINNED_CTYPES_SHA256,
        "bytes": 8192,
        "device": 11,
        "inode": 7002,
    } if zig else None
    return {
        "schema": SCHEMA + "-isolated-worker",
        "status": "PASS",
        "family": family,
        "pid": pid,
        "oracle_source_sha256": source_pin,
        "manifest": dict(manifest),
        "owners": synthetic_owners(family, manifest, source_pin),
        "runtime_checks": 20,
        "owned_graph_checks": 11,
        "guarded_import_calls": 3,
        "forbidden_import_or_execution_count": 0,
        "removed_preexisting_forbidden_module_count": 2,
        "caller_replacement_callback_supported": True,
        "owned_public_re_names_supported": True,
        "owned_public_sre_scanner_name_supported": True,
        "actual_standard_library_engine_loaded": False,
        "candidate_modules": sorted([spec["bridge_module"], spec["module"]]),
        "owned_ctypes_library_load_count": 1 if zig else 0,
        "owned_ctypes_symbols": sorted(ZIG_CTYPES_SYMBOLS) if zig else [],
        "trusted_ctypes": ffi,
        "trusted_ctypes_owner": ffi_owner,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def synthetic_process(worker: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "family": worker["family"],
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": encode_stream(canonical(dict(worker))),
        "stderr": encode_stream(b""),
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime(synthetic=True)
    require(not any(
        name == "candidates" or name.startswith("candidates.")
        for name in sys.modules
    ), "a candidate was loaded before the in-memory V3 ownership self-test")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a synthetic V3 ownership positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a synthetic V3 ownership rejection was duplicated")
        try:
            action()
        except (AuditFailure, TypeError, ValueError, KeyError,
                OSError, OverflowError):
            rejected.append(name)
            return
        raise AuditFailure(
            "a forged synthetic native ownership control passed: " + name
        )

    with SourceOnlyBoundary() as boundary:
        accept("preserve-all-three-genuinely-independent-native-families",
               frozenset(FAMILY_SPECS) == {"rust", "c", "zig"})
        accept("preserve-all-eighteen-owned-rust-engine-exports",
               len(RUST_ENGINE_EXPORTS) == 18)
        accept("preserve-all-twenty-two-owned-zig-engine-exports",
               len(ZIG_ENGINE_EXPORTS) == 22)
        accept("preserve-all-fourteen-owned-zig-bridge-engine-references",
               len(ZIG_BRIDGE_REFERENCES) == 14)
        accept("preserve-all-nine-owned-zig-ffi-symbols",
               len(ZIG_CTYPES_SYMBOLS) == 9)
        accept("freeze-the-original-v2-and-v5-policy-not-obsolete-candidates",
               len(IMMUTABLE_POLICY_SHA256) == 2
               and all(valid_digest(value)
                       for value in IMMUTABLE_POLICY_SHA256.values()))
        accept("freeze-the-genuine-pinned-cpython-interpreter",
               valid_digest(PINNED_PYTHON_SHA256))
        accept("freeze-the-genuine-standard-zig-ctypes-source",
               valid_digest(PINNED_CTYPES_SHA256))
        accept("allow-only-the-genuine-combined-c-engine-and-bridge",
               FAMILY_SPECS["c"]["engine"]
               == FAMILY_SPECS["c"]["bridge"])
        source_pin = "12" * 32

        for family_index, family in enumerate(("rust", "c", "zig")):
            spec = family_spec(family)
            manifest = synthetic_manifest(family)
            accept("accept-a-complete-dynamically-pinned-" + family + "-closure",
                   validate_manifest(manifest, family) == manifest)
            accept("require-all-exact-" + family + "-source-paths",
                   set(manifest["source_sha256"]) == set(spec["sources"]))
            accept("require-all-distinct-" + family + "-native-paths",
                   set(manifest["native_sha256"]) == set(spec["binaries"]))
            accept("preserve-the-frozen-v2-and-v5-" + family + "-policies",
                   manifest["immutable_policy_sha256"]
                   == dict(IMMUTABLE_POLICY_SHA256))
            accept("preserve-exact-" + family + "-adapter-and-native-core-pins",
                   manifest["candidate_source_sha256"]
                   == manifest["source_sha256"][spec["adapter"]]
                   and manifest["native_engine_sha256"]
                   == manifest["native_sha256"][spec["engine"]]
                   and manifest["native_bridge_sha256"]
                   == manifest["native_sha256"][spec["bridge"]])
            updated_sources = {
                path: hashlib.sha256(
                    ("independent-v3-updated:" + family + ":" + path).encode()
                ).hexdigest()
                for path in spec["sources"]
            }
            updated_binaries = {
                path: hashlib.sha256(
                    ("independent-v3-updated:" + family + ":" + path).encode()
                ).hexdigest()
                for path in spec["binaries"]
            }
            updated = validate_family_pins(
                family,
                updated_sources[spec["adapter"]],
                updated_binaries[spec["engine"]],
                updated_binaries[spec["bridge"]],
                [path + "=" + value
                 for path, value in updated_sources.items()],
                [path + "=" + value
                 for path, value in updated_binaries.items()],
            )
            accept("accept-new-explicitly-repinned-" + family + "-artifacts",
                   validate_manifest(updated, family) == updated
                   and updated != manifest)

            adapter = synthetic_adapter(family)
            parsed_adapter = adapter_imports(adapter, family)
            accept("preserve-exact-approved-" + family + "-adapter-imports",
                   len(parsed_adapter["modules"]) == len(spec["imports"]))
            accept("preserve-exact-owned-" + family + "-bridge-imports",
                   len(parsed_adapter["from_imports"])
                   == len(spec["from_imports"]))
            accept("approve-only-owned-" + family + "-runtime-modules",
                   not forbidden_module(spec["module"], family)
                   and not forbidden_module(spec["bridge_module"], family))
            for foreign in (
                "re", "re._compiler", "_sre", "regex", "_regex", "pcre2",
                "onig", "google_re2", "hyperscan", "subprocess", "runpy",
                "candidates.rust_candidate", "candidates._rust_bridge",
                "candidates.vm_candidate", "candidates._vm_native",
                "candidates.zig_candidate", "candidates._zig_bridge",
            ):
                if foreign not in {spec["module"], spec["bridge_module"]}:
                    accept("block-" + family + "-foreign-module-" + foreign,
                           forbidden_module(foreign, family))
            for poison in (
                "import re\n", "import _sre\n", "import regex\n",
                "import pcre2\n", "import onig\n", "import subprocess\n",
                "import importlib\n",
                "from candidates import another_candidate\n",
                "__import__('re')\n", "eval('1')\n",
                "exec('import re')\n", "os.system('foreign')\n",
                "os.popen('foreign')\n",
                "getattr(os, 'system')('foreign')\n",
            ):
                reject("reject-" + family + "-dynamic-adapter-"
                       + hashlib.sha256(poison.encode()).hexdigest()[:12],
                       lambda poison=poison: adapter_imports(
                           adapter + poison, family
                       ))

            bridge = synthetic_bridge(family)
            bridge_result = inspect_bridge(bridge, family)
            accept("preserve-one-owned-" + family + "-public-scanner-name",
                   bridge_result["owned_compatible_scanner_names"] == 1)
            accept("preserve-exact-approved-" + family + "-native-headers",
                   len(bridge_result["includes"]) == len(spec["headers"]))
            accept("preserve-owned-" + family + "-safe-compatibility-imports",
                   type(bridge_result["compatibility_imports"]) is list)
            for poison in (
                '#include "external_regex.h"\n',
                "#include <pcre2.h>\n", "dlopen();\n", "dlsym();\n",
                "regcomp();\n", "regexec();\n", "pcre2_match();\n",
                "onig_search();\n", "hs_scan();\n", "re2_match();\n",
                "PyRun_SimpleString();\n", "PyEval_EvalCode();\n",
                'foreign = "candidates.foreign_candidate";\n',
                'external_scanner = "_sre.SRE_Scanner";\n',
            ):
                reject("reject-" + family + "-foreign-native-"
                       + hashlib.sha256(poison.encode()).hexdigest()[:12],
                       lambda poison=poison: inspect_bridge(
                           bridge + poison, family
                       ))

            for binary in spec["binaries"]:
                dynamic = synthetic_dynamic(family, binary)
                inspected = parse_dynamic_section(dynamic, family, binary)
                dependencies, paths = expected_dynamic(family, binary)
                suffix = binary.rsplit("/", 1)[1]
                accept("preserve-" + family + "-owned-elf-dependencies-" + suffix,
                       frozenset(inspected["needed"]) == dependencies)
                accept("preserve-" + family + "-owned-runpath-" + suffix,
                       tuple(inspected["runpaths"]) == paths)
                for poison in (
                    "0x1 (NEEDED) Shared library: [libpcre2-8.so]\n",
                    "0x1 (NEEDED) Shared library: [libre2.so]\n",
                    "0x1 (NEEDED) Shared library: [libonig.so]\n",
                    "0x1 (NEEDED) Shared library: [_foreign_candidate.so]\n",
                    "0x1 (NEEDED) Shared library: [libc.so.6]\n",
                    "0x1 (RUNPATH) Library runpath: [/foreign]\n",
                    "0x1 (RPATH) Library rpath: [$ORIGIN]\n",
                ):
                    reject("reject-" + family + "-foreign-elf-" + suffix + "-"
                           + hashlib.sha256(poison.encode()).hexdigest()[:10],
                           lambda poison=poison: parse_dynamic_section(
                               dynamic + "\n" + poison.rstrip("\n"),
                               family, binary,
                           ))
                symbols = synthetic_symbols(family, binary)
                inspected_symbols = parse_dynamic_symbols(
                    symbols, family, binary
                )
                accept("preserve-" + family + "-owned-elf-exports-" + suffix,
                       bool(inspected_symbols["defined_exports"]))
                for symbol in (
                    "dlopen", "dlsym", "regcomp", "regexec", "pcre2_match",
                    "onig_search", "hs_scan", "re2_match",
                    "PyRun_SimpleString", "PyEval_EvalCode", "PyInit__sre",
                    "borrowed_matching_engine",
                ):
                    row = (
                        "999: 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
                        + symbol
                    )
                    reject("reject-" + family + "-foreign-symbol-" + suffix
                           + "-" + symbol,
                           lambda row=row: parse_dynamic_symbols(
                               symbols + "\n" + row, family, binary
                           ))
                for entry in (
                    "PyInit__rust_bridge", "PyInit__vm_native",
                    "PyInit__zig_bridge",
                ):
                    if entry not in inspected_symbols["defined_exports"]:
                        row = (
                            "998: 0000000000000001 1 FUNC GLOBAL DEFAULT 14 "
                            + entry
                        )
                        reject("reject-" + family + "-sibling-export-"
                               + suffix + "-" + entry,
                               lambda row=row: parse_dynamic_symbols(
                                   symbols + "\n" + row, family, binary
                               ))
                reject("reject-missing-" + family + "-owned-symbol-" + suffix,
                       lambda: parse_dynamic_symbols(
                           "\n".join(symbols.splitlines()[1:]),
                           family, binary,
                       ))
                if family == "rust" and binary == spec["bridge"]:
                    for symbol in (
                        "__ctype_b_loc", "__ctype_tolower_loc",
                        "__memcpy_chk", "bcmp",
                    ):
                        row = (
                            "997: 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
                            + symbol
                        )
                        reject("reject-rust-bridge-external-symbol-" + symbol,
                               lambda row=row: parse_dynamic_symbols(
                                   symbols + "\n" + row, family, binary
                               ))

            for field, changed in (
                ("family", "foreign"),
                ("candidate_source_sha256", "98" * 32),
                ("native_engine_sha256", "98" * 32),
                ("native_bridge_sha256", "98" * 32),
                ("immutable_policy_sha256", {}),
            ):
                poisoned = dict(manifest)
                poisoned[field] = changed
                reject("reject-" + family + "-forged-manifest-" + field,
                       lambda poisoned=poisoned: validate_manifest(
                           poisoned, family
                       ))
            for label in ("source_sha256", "native_sha256"):
                items = manifest[label]
                first_path = next(iter(items))
                for change_index, change in enumerate((
                    {},
                    {path: value for path, value in items.items()
                     if path != first_path},
                    {**items, "candidates/foreign_engine.so": "98" * 32},
                )):
                    poisoned = dict(manifest)
                    poisoned[label] = change
                    reject("reject-" + family + "-incomplete-" + label + "-"
                           + str(change_index) + "-"
                           + hashlib.sha256(canonical(change)).hexdigest()[:10],
                           lambda poisoned=poisoned: validate_manifest(
                               poisoned, family
                           ))
                core_path = (
                    spec["adapter"] if label == "source_sha256"
                    else spec["engine"]
                )
                inconsistent = dict(manifest)
                inconsistent[label] = {
                    **items, core_path: "98" * 32,
                }
                reject("reject-" + family + "-inconsistent-core-" + label,
                       lambda inconsistent=inconsistent: validate_manifest(
                           inconsistent, family
                       ))

            owners = synthetic_owners(family, manifest, source_pin)
            accept("authenticate-all-synthetic-" + family + "-source-owners",
                   validate_serializable_owners(
                       owners, family, manifest, source_pin
                   ) == owners)
            worker = synthetic_worker(
                family, manifest, source_pin, 42000 + family_index
            )
            accept("accept-complete-synthetic-" + family + "-guarded-worker",
                   validate_worker(
                       worker, family, manifest, source_pin,
                       expected_pid=42000 + family_index,
                   ) == worker)
            process = synthetic_process(worker)
            accept("preserve-complete-synthetic-" + family + "-process-streams",
                   validate_process_evidence(process, worker, family) == process)
            for field, changed in (
                ("status", "FAIL"),
                ("family", "foreign"),
                ("pid", 1),
                ("oracle_source_sha256", "98" * 32),
                ("runtime_checks", 19),
                ("owned_graph_checks", 0),
                ("guarded_import_calls", 0),
                ("forbidden_import_or_execution_count", 1),
                ("caller_replacement_callback_supported", False),
                ("owned_public_re_names_supported", False),
                ("owned_public_sre_scanner_name_supported", False),
                ("actual_standard_library_engine_loaded", True),
                ("candidate_modules", []),
                ("owned_ctypes_library_load_count", 2),
                ("owned_ctypes_symbols", [] if family == "zig"
                 else ["rebar_zig_compile"]),
                ("actual_candidate_workers", 0),
                ("clock_samples", 1),
                ("timing_trials_run", 1),
                ("workspace_files_written", 1),
                ("evidence_files_created", 1),
                ("benchmark_files_read", 1),
                ("hidden_cases_read", 1),
                ("performance", "MEASURED"),
                ("candidate_qualified_for_hidden_benchmark", True),
                ("final_winner_selected", True),
            ):
                poisoned_worker = dict(worker)
                poisoned_worker[field] = changed
                reject("reject-" + family + "-forged-worker-" + field,
                       lambda poisoned_worker=poisoned_worker:
                       validate_worker(
                           poisoned_worker, family, manifest, source_pin,
                           expected_pid=42000 + family_index,
                       ))
            for field, changed in (
                ("family", "foreign"),
                ("pid", 1),
                ("returncode", 1),
                ("stdout", encode_stream(b"{}\n")),
                ("stderr", encode_stream(b"poison\n")),
            ):
                poisoned_process = dict(process)
                poisoned_process[field] = changed
                reject("reject-" + family + "-forged-process-" + field,
                       lambda poisoned_process=poisoned_process:
                       validate_process_evidence(
                           poisoned_process, worker, family
                       ))

            original_re = types.ModuleType("re")
            original_sre = types.ModuleType("_sre")
            original_pattern = type("OriginalPattern", (), {})
            original_match = type("OriginalMatch", (), {})
            original_re.Pattern = original_pattern
            original_re.Match = original_match
            originals = (original_re, original_sre,
                         original_pattern, original_match)
            safe_adapter = types.ModuleType(spec["module"])
            safe_bridge = types.ModuleType(spec["bridge_module"])
            safe_adapter.safe = ("independent", 1, None)
            accept("inspect-an-independent-" + family + "-object-graph",
                   forbid_captured_original_matchers(
                       safe_adapter, safe_bridge, originals, family
                   ) > 0)
            for index, captured in enumerate((
                original_re, original_sre, original_pattern, original_match,
                original_pattern(), original_match(),
                {"hidden": original_re}, ("hidden", original_pattern),
                types.MappingProxyType({"hidden": original_match}),
            )):
                def poisoned_capture(captured: Any = captured) -> int:
                    adapter_module = types.ModuleType(spec["module"])
                    adapter_module.hidden = captured
                    bridge_module = types.ModuleType(spec["bridge_module"])
                    return forbid_captured_original_matchers(
                        adapter_module, bridge_module, originals, family
                    )

                reject("reject-" + family + "-captured-original-"
                       + str(index), poisoned_capture)

        rust = {path: "" for path in RUST_SOURCE_FILES}
        rust[RUST_SOURCE_FILES[0]] = (
            "use std::slice;\nmod newline;\nmod search;\n"
            "mod stack;\nmod unicode_tables;\nuse stack::InlineStack;\n"
        )
        accept("preserve-five-owned-rust-native-semantic-source-files",
               inspect_rust_sources(rust)["source_count"] == 5)
        for poison in (
            "extern crate regex;\n", "use regex::Regex;\n",
            'include!("foreign.rs");\n',
            'include_bytes!("foreign.so");\n', "dlopen();\n",
            "pcre2_match();\n", "regexec();\n", "rebar_zig_compile();\n",
        ):
            def poisoned_rust(poison: str = poison) -> dict[str, Any]:
                changed = dict(rust)
                changed[RUST_SOURCE_FILES[0]] += poison
                return inspect_rust_sources(changed)

            reject("reject-external-rust-semantic-engine-"
                   + hashlib.sha256(poison.encode()).hexdigest()[:12],
                   poisoned_rust)
        reject("reject-a-missing-owned-rust-native-source",
               lambda: inspect_rust_sources({
                   RUST_SOURCE_FILES[0]: rust[RUST_SOURCE_FILES[0]],
               }))

        manifest_text = (
            '[package]\nname = "rebar-rust-continuation"\n'
            'version = "0.1.0"\nedition = "2024"\n'
            'rust-version = "1.85"\npublish = false\n'
            '[lib]\ncrate-type = ["cdylib"]\n'
        )
        lock_text = (
            'version = 4\n[[package]]\nname = "rebar-rust-continuation"\n'
            'version = "0.1.0"\n'
        )
        accept("preserve-a-dependency-free-owned-rust-lockfile",
               inspect_cargo(manifest_text, lock_text)
               ["external_package_count"] == 0)
        for poison in (
            '\n[dependencies]\nregex = "1"\n',
            '\n[build-dependencies]\ncc = "1"\n',
            '\n[workspace]\nmembers = ["foreign"]\n',
        ):
            reject("reject-external-rust-dependency-"
                   + hashlib.sha256(poison.encode()).hexdigest()[:12],
                   lambda poison=poison: inspect_cargo(
                       manifest_text + poison, lock_text
                   ))
        reject("reject-an-external-regex-inside-the-rust-lockfile",
               lambda: inspect_cargo(
                   manifest_text,
                   lock_text
                   + '\n[[package]]\nname = "regex"\nversion = "1.0.0"\n',
               ))

        approved_external = (
            "_PyUnicode_IsAlpha", "_PyUnicode_IsDecimalDigit",
            "_PyUnicode_IsDigit", "_PyUnicode_IsNumeric",
            "_PyUnicode_IsWhitespace", "_PyUnicode_ToLowercase",
            "_PyUnicode_ToUppercase", "tolower", "isalnum",
        )
        zig = 'const std = @import("std");\n' + "".join(
            "extern fn " + name + "(u32) c_int;\n"
            for name in approved_external
        )
        accept("preserve-the-owned-no-dependency-zig-source",
               inspect_zig_source(zig)["external_regex_package_count"] == 0)
        for poison in (
            '@import("regex");\n', '@import("pcre");\n',
            '@cImport("pcre.h");\n', '@embedFile("foreign.so");\n',
            "extern fn regexec(u32) c_int;\n",
            "extern fn foreign_match(u32) c_int;\n",
            "rebar_compile();\n",
        ):
            reject("reject-an-external-zig-engine-"
                   + hashlib.sha256(poison.encode()).hexdigest()[:12],
                   lambda poison=poison: inspect_zig_source(zig + poison))

        exact_engine = "/owned/candidates/_zig_probe.so"
        for symbol in sorted(ZIG_CTYPES_SYMBOLS):
            validate_ctypes_dlsym("zig", exact_engine, symbol, exact_engine)
            accept("preserve-exact-owned-zig-ffi-" + symbol, True)
        validate_ctypes_dlopen("zig", exact_engine, exact_engine)
        accept("preserve-only-the-adjacent-owned-zig-engine-path", True)
        for family in ("rust", "c"):
            reject("reject-" + family + "-ambient-ctypes-engine",
                   lambda family=family: validate_ctypes_dlopen(
                       family, exact_engine, exact_engine
                   ))
            reject("reject-" + family + "-sibling-zig-ffi-symbol",
                   lambda family=family: validate_ctypes_dlsym(
                       family, exact_engine, "rebar_zig_compile", exact_engine
                   ))
        for index, foreign_path in enumerate((
            None, "_zig_probe.so",
            "/owned/candidates/../candidates/_zig_probe.so",
            "/owned/candidates/libc.so.6",
            "/owned/candidates/libpcre2-8.so",
            "/owned/candidates/_rust_engine.so",
            "/owned/candidates/_vm_native" + EXTENSION_SUFFIX,
        )):
            reject("reject-foreign-zig-ffi-library-" + str(index),
                   lambda foreign_path=foreign_path: validate_ctypes_dlopen(
                       "zig", foreign_path, exact_engine
                   ))
        for index, symbol in enumerate((
            "rebar_compile", "regexec", "pcre2_match", "onig_search",
            "PyRun_SimpleString", "system", "rebar_zig_match", None,
        )):
            reject("reject-foreign-zig-ffi-symbol-" + str(index),
                   lambda symbol=symbol: validate_ctypes_dlsym(
                       "zig", exact_engine, symbol, exact_engine
                   ))

        good_zig = synthetic_adapter("zig")
        for index, poison in enumerate((
            good_zig.replace('"_zig_probe.so"', '"libpcre2-8.so"'),
            good_zig.replace("ctypes.CDLL(path)", "ctypes.CDLL(None)"),
            good_zig.replace(
                "ctypes.CDLL(path)", "ctypes.CDLL('foreign.so')"
            ),
            good_zig.replace("ctypes.CDLL(path)", "ctypes.PyDLL(path)"),
            good_zig + "ctypes.CDLL(path)\n",
            good_zig + "getattr(ctypes, 'CDLL')('foreign.so')\n",
            good_zig + "getattr(lib, 'foreign_match')\n",
            good_zig + "ctypes.pythonapi\n",
            good_zig + "ctypes.util\n",
            good_zig + "lib._handle\n",
            good_zig + "lib.__class__\n",
            good_zig + "setattr(ctypes, 'CDLL', replacement)\n",
            good_zig + "setattr(ctypes, 'pythonapi', replacement)\n",
            good_zig + "delattr(ctypes, 'CDLL')\n",
            good_zig + "setattr(lib, '_handle', replacement)\n",
            good_zig + "delattr(lib, '_handle')\n",
            good_zig + "ctypes.CDLL = replacement\n",
            good_zig + "ctypes = replacement\n",
        )):
            reject("reject-a-hidden-zig-ffi-loader-" + str(index),
                   lambda poison=poison: adapter_imports(poison, "zig"))

        for relative in (
            "", "/outside", "../outside", "candidates/../outside",
            "candidates//outside", "candidates/./outside",
            "candidates\\outside", "candidates/\x00outside",
        ):
            reject("reject-an-escaped-canonical-owner-path-"
                   + hashlib.sha256(relative.encode()).hexdigest()[:10],
                   lambda relative=relative: owned_relative(relative))
        for value in (
            "", "z" * 64, "a" * 64, "AB" * 32,
            "98" * 31, "98" * 32 + "00", None, True,
        ):
            reject("reject-an-unpinned-native-owner-"
                   + hashlib.sha256(repr(value).encode()).hexdigest()[:10],
                   lambda value=value: checked_digest(
                       value, "synthetic caller pin"
                   ))
        reject("reject-duplicate-canonical-ownership-json",
               lambda: decode_canonical(b'{"value":1,"value":2}\n',
                                        "duplicate synthetic owner"))
        reject("reject-noncanonical-ownership-whitespace",
               lambda: decode_canonical(b'{ "value":1}\n',
                                        "noncanonical synthetic owner"))
        reject("reject-nonfinite-ownership-json",
               lambda: decode_canonical(b'{"value":NaN}\n',
                                        "nonfinite synthetic owner"))

        reject("block-genuine-source-file-reads",
               lambda: builtins.open(SOURCE_ABSOLUTE, "rb"))
        reject("block-genuine-source-or-binary-writes",
               lambda: builtins.open(SOURCE_ABSOLUTE, "wb"))
        reject("block-genuine-source-filesystem-stat",
               lambda: os.stat(SOURCE_ABSOLUTE))
        reject("block-all-real-candidate-imports",
               lambda: importlib.import_module("candidates.zig_candidate"))
        reject("block-all-real-foreign-regex-imports",
               lambda: importlib.import_module("regex"))
        reject("block-all-dynamic-standard-imports",
               lambda: importlib.import_module("json"))
        reject("block-all-genuine-readelf-or-candidate-workers",
               lambda: subprocess.Popen([READELF, "--version"]))
        reject("block-all-background-candidate-threads",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-wall-clock-performance-measurement",
               lambda: time.time())
        reject("block-monotonic-performance-measurement",
               lambda: time.monotonic())
        reject("block-native-performance-counter-measurement",
               lambda: time.perf_counter())
        reject("block-operating-system-randomness",
               lambda: os.urandom(1))
        reject("block-garbage-collection-side-effects",
               lambda: gc.collect())
        blocked = dict(boundary.blocked)
        accept("exercise-every-effect-blocked-synthetic-ownership-guard",
               all(blocked[name] > 0 for name in blocked))
        accept("import-no-real-candidate-in-any-synthetic-control",
               not any(
                   name == "candidates" or name.startswith("candidates.")
                   for name in sys.modules
               ))
        require(len(accepted) >= 80,
                "the exact positive native ownership controls are incomplete")
        require(len(rejected) >= 250,
                "the exact external matcher rejection controls are incomplete")

    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "oracle": ORACLE_NAME,
        "status": "PASS",
        "self_test_only": True,
        "families": ["rust", "c", "zig"],
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_SHA256),
        "synthetic_positive_controls": len(accepted),
        "synthetic_rejection_controls": len(rejected),
        "positive_controls": accepted,
        "rejection_controls": rejected,
        "source_only_blocked_operations": blocked,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit only fully caller-pinned independent native engines",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run only effect-blocked in-memory ownership controls")
    modes.add_argument("--audit", action="store_true",
                       help="explicitly audit exactly one caller-pinned family")
    modes.add_argument("--internal-audit-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--family", choices=("rust", "c", "zig"))
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--source-pin", action="append")
    parser.add_argument("--native-pin", action="append")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(all(getattr(options, name) is None for name in (
                "family", "oracle_source_sha256", "candidate_source_sha256",
                "native_engine_sha256", "native_bridge_sha256",
                "source_pin", "native_pin",
            )), "synthetic ownership controls cannot select or pin a candidate")
            result = source_self_test()
            sys.stdout.buffer.write(canonical(result))
            return 0

        require(options.family in FAMILY_SPECS,
                "choose exactly one actual independently owned candidate")
        source_pin = checked_digest(
            options.oracle_source_sha256,
            "explicitly pinned independent V3 audit source",
        )
        manifest = validate_family_pins(
            options.family,
            options.candidate_source_sha256,
            options.native_engine_sha256,
            options.native_bridge_sha256,
            options.source_pin,
            options.native_pin,
        )
        if options.internal_audit_worker:
            result = worker_run(options.family, manifest, source_pin)
        else:
            require(options.audit,
                    "only explicit caller authorization can run a native audit")
            result = run_audit(options.family, manifest, source_pin)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except WorkerFailure as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "oracle": ORACLE_NAME,
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "complete_worker_failure": error.evidence,
            "actual_candidate_workers": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1
    except (AuditFailure, OSError, TypeError, ValueError) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "oracle": ORACLE_NAME,
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
