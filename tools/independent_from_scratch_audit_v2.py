#!/usr/bin/env python3
"""Fail-closed, separately guarded ownership audits for three native engines.

``--self-test`` uses synthetic, in-memory controls only.  It never reads a
candidate, imports a candidate, starts a worker, measures performance, or
creates evidence.  ``--candidate {rust,c,zig}`` is the separately explicit
actual-candidate observation and must not be run before this source is frozen.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import copyreg
import ctypes
import functools
import hashlib
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tomllib
import types


ORACLE_NAME = "independent-from-scratch-audit-v2"
PYTHON_VERSION = (3, 14, 6)
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
READELF = "/usr/bin/readelf"
PREDECESSOR = "tools/rust_from_scratch_audit_v1.py"

# Every source and binary is independently pinned before an actual worker can
# be started.  The original Rust closure, including its lockfile, is preserved.
ARTIFACT_SHA256 = types.MappingProxyType(
    {
        PREDECESSOR: "536dea67430257ea38e968c98e9da50462d37fb8188a973e33775d14d7545ce0",
        "candidates/rust_candidate.py": "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        "candidates/rust/Cargo.toml": "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
        "candidates/rust/Cargo.lock": "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
        "candidates/rust/src/lib.rs": "4ac8f3e9b96e37f5670cb610c6b031315eeedf92fd645399ac693f2f3d27ba72",
        "candidates/rust/src/newline.rs": "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
        "candidates/rust/src/search.rs": "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
        "candidates/rust/src/stack.rs": "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
        "candidates/rust/src/unicode_tables.rs": "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
        "candidates/rust/py_bridge.c": "6f4401a8e9205e3e7b9797dd655f1a0b3d51190b8bd5239f77c5ad1534707f2d",
        "candidates/_rust_engine.so": "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so": "a7ef601a91527d7dcefcacb4c602afb972e4adbbed7d112239e7896530416c02",
        "candidates/vm_candidate.py": "2bd8cd6d3844d6cd8c94f338803b41671d6aa1e999897e21a81cbe91182eb2fb",
        "candidates/_vm_native.c": "a516ae8f2409af054b456068e403df63d8fea029a516ce1adb22ee5f836a819c",
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so": "9308563f7541f7b9f56afc7965a47ae4d4d00b1a94db8857891e493a82ae5148",
        "candidates/zig_candidate.py": "07e9fa19af8fe9938dc8ed5170e30a478ff56f0d04cd2488a0bd1869e28201cc",
        "candidates/zig/mini_regex.zig": "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346",
        "candidates/zig/py_bridge.c": "f4900d04734a7c02bd766aee81c1d64114803dbefcf6f4591bfb667262658fea",
        "candidates/_zig_probe.so": "96b899f8c5f25e4c94fe029d6218c0408cd20f7a86d661bcc4ce891648f17cb6",
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so": "ad1a7ea024721e329857753d288abd834fcfc029055a6274195daf00754bf65a",
    }
)

RUST_SOURCE_FILES = (
    "candidates/rust/src/lib.rs",
    "candidates/rust/src/newline.rs",
    "candidates/rust/src/search.rs",
    "candidates/rust/src/stack.rs",
    "candidates/rust/src/unicode_tables.rs",
)
RUST_ENGINE_EXPORTS = frozenset(
    {
        "rebar_collect_ascii",
        "rebar_collect_wide",
        "rebar_compile",
        "rebar_compile_scanner",
        "rebar_error_copy",
        "rebar_error_include",
        "rebar_error_len",
        "rebar_error_pos",
        "rebar_flags",
        "rebar_free",
        "rebar_groups",
        "rebar_match",
        "rebar_match_ascii",
        "rebar_match_wide",
        "rebar_name_copy",
        "rebar_name_count",
        "rebar_name_group",
        "rebar_name_len",
    }
)
RUST_ENGINE_UNDEFINED = frozenset(
    {
        "Py_GetRecursionLimit",
        "_ITM_deregisterTMCloneTable",
        "_ITM_registerTMCloneTable",
        "_Unwind_Backtrace",
        "_Unwind_GetDataRelBase",
        "_Unwind_GetIP",
        "_Unwind_GetIPInfo",
        "_Unwind_GetLanguageSpecificData",
        "_Unwind_GetRegionStart",
        "_Unwind_GetTextRelBase",
        "_Unwind_Resume",
        "_Unwind_SetGR",
        "_Unwind_SetIP",
        "__cxa_finalize",
        "__cxa_thread_atexit_impl",
        "__errno_location",
        "__gmon_start__",
        "__tls_get_addr",
        "abort",
        "bcmp",
        "calloc",
        "close",
        "dl_iterate_phdr",
        "free",
        "fstat64",
        "getcwd",
        "getenv",
        "gettid",
        "isalnum",
        "lseek64",
        "malloc",
        "memchr",
        "memcmp",
        "memcpy",
        "memmem",
        "memmove",
        "memrchr",
        "memset",
        "mmap64",
        "munmap",
        "open64",
        "posix_memalign",
        "pthread_key_create",
        "pthread_key_delete",
        "pthread_setspecific",
        "read",
        "readlink",
        "realloc",
        "realpath",
        "stat64",
        "statx",
        "strcmp",
        "strlen",
        "strncmp",
        "syscall",
        "tolower",
        "write",
        "writev",
    }
)
ZIG_ENGINE_EXPORTS = frozenset(
    {
        "rebar_zig_batch",
        "rebar_zig_collect_captures",
        "rebar_zig_collect_records",
        "rebar_zig_collect_records_wide",
        "rebar_zig_compile",
        "rebar_zig_compile_guarded",
        "rebar_zig_flags",
        "rebar_zig_free",
        "rebar_zig_groups",
        "rebar_zig_match",
        "rebar_zig_match_captures",
        "rebar_zig_match_captures_wide",
        "rebar_zig_match_inverted_wide",
        "rebar_zig_match_nonempty_wide",
        "rebar_zig_match_tree",
        "rebar_zig_match_wide",
        "rebar_zig_name_copy",
        "rebar_zig_name_count",
        "rebar_zig_name_group",
        "rebar_zig_name_length",
        "rebar_zig_program_memory",
        "rebar_zig_program_size",
    }
)
ZIG_ENGINE_UNDEFINED = frozenset(
    {
        "_PyUnicode_IsAlpha",
        "_PyUnicode_IsDecimalDigit",
        "_PyUnicode_IsDigit",
        "_PyUnicode_IsNumeric",
        "_PyUnicode_IsWhitespace",
        "_PyUnicode_ToLowercase",
        "_PyUnicode_ToUppercase",
        "__gmon_start__",
        "free",
        "isalnum",
        "malloc",
        "malloc_usable_size",
        "memcpy",
        "memset",
        "posix_memalign",
        "realloc",
        "tolower",
    }
)
ZIG_BRIDGE_REFERENCES = frozenset(
    {
        "rebar_zig_collect_records_wide",
        "rebar_zig_compile",
        "rebar_zig_compile_guarded",
        "rebar_zig_flags",
        "rebar_zig_free",
        "rebar_zig_groups",
        "rebar_zig_match_captures_wide",
        "rebar_zig_match_inverted_wide",
        "rebar_zig_match_nonempty_wide",
        "rebar_zig_match_wide",
        "rebar_zig_name_copy",
        "rebar_zig_name_count",
        "rebar_zig_name_group",
        "rebar_zig_name_length",
    }
)
ZIG_CTYPES_SYMBOLS = frozenset(
    {
        "rebar_zig_compile",
        "rebar_zig_free",
        "rebar_zig_groups",
        "rebar_zig_flags",
        "rebar_zig_program_memory",
        "rebar_zig_name_count",
        "rebar_zig_name_length",
        "rebar_zig_name_group",
        "rebar_zig_name_copy",
    }
)
RUST_BRIDGE_SYSTEM_UNDEFINED = frozenset(
    {
        "_ITM_deregisterTMCloneTable",
        "_ITM_registerTMCloneTable",
        "__assert_fail",
        "__cxa_finalize",
        "__gmon_start__",
        "__stack_chk_fail",
        "calloc",
        "free",
        "malloc",
        "memchr",
        "memcmp",
        "memcpy",
        "memmem",
        "memmove",
        "memset",
        "realloc",
        "strlen",
    }
)
SYSTEM_NATIVE_UNDEFINED = frozenset(
    {
        "_ITM_deregisterTMCloneTable",
        "_ITM_registerTMCloneTable",
        "__assert_fail",
        "__ctype_b_loc",
        "__ctype_tolower_loc",
        "__cxa_finalize",
        "__gmon_start__",
        "__memcpy_chk",
        "__stack_chk_fail",
        "bcmp",
        "calloc",
        "free",
        "malloc",
        "memchr",
        "memcmp",
        "memcpy",
        "memmem",
        "memmove",
        "memset",
        "realloc",
        "strlen",
    }
)

FAMILY_SPECS = types.MappingProxyType(
    {
        "rust": types.MappingProxyType(
            {
                "module": "candidates.rust_candidate",
                "adapter": "candidates/rust_candidate.py",
                "bridge_module": "candidates._rust_bridge",
                "bridge_source": "candidates/rust/py_bridge.c",
                "engine": "candidates/_rust_engine.so",
                "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                "sources": (
                    "candidates/rust_candidate.py",
                    "candidates/rust/py_bridge.c",
                    "candidates/rust/Cargo.toml",
                    "candidates/rust/Cargo.lock",
                    *RUST_SOURCE_FILES,
                ),
                "binaries": (
                    "candidates/_rust_engine.so",
                    "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                ),
                "imports": frozenset(
                    {"enum", "operator", "os", "types", "unicodedata", "warnings"}
                ),
                "from_imports": frozenset(
                    {("candidates", "_rust_bridge", None)}
                ),
                "headers": frozenset(
                    {"Python.h", "stddef.h", "stdint.h", "string.h"}
                ),
                "exports": RUST_ENGINE_EXPORTS,
            }
        ),
        "c": types.MappingProxyType(
            {
                "module": "candidates.vm_candidate",
                "adapter": "candidates/vm_candidate.py",
                "bridge_module": "candidates._vm_native",
                "bridge_source": "candidates/_vm_native.c",
                "engine": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
                "bridge": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
                "sources": (
                    "candidates/vm_candidate.py",
                    "candidates/_vm_native.c",
                ),
                "binaries": (
                    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
                ),
                "imports": frozenset(
                    {"enum", "os", "types", "unicodedata", "warnings"}
                ),
                "from_imports": frozenset(
                    {
                        ("copyreg", "_reconstructor", "_copy_reconstructor"),
                        ("struct", "calcsize", "_native_calcsize"),
                        ("candidates", "_vm_native", None),
                    }
                ),
                "headers": frozenset(
                    {
                        "Python.h",
                        "ctype.h",
                        "stddef.h",
                        "stdint.h",
                        "stdlib.h",
                        "string.h",
                    }
                ),
                "exports": frozenset(),
            }
        ),
        "zig": types.MappingProxyType(
            {
                "module": "candidates.zig_candidate",
                "adapter": "candidates/zig_candidate.py",
                "bridge_module": "candidates._zig_bridge",
                "bridge_source": "candidates/zig/py_bridge.c",
                "engine": "candidates/_zig_probe.so",
                "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                "sources": (
                    "candidates/zig_candidate.py",
                    "candidates/zig/mini_regex.zig",
                    "candidates/zig/py_bridge.c",
                ),
                "binaries": (
                    "candidates/_zig_probe.so",
                    "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                ),
                "imports": frozenset(
                    {"ctypes", "enum", "os", "types", "unicodedata", "warnings"}
                ),
                "from_imports": frozenset(
                    {("candidates", "_zig_bridge", None)}
                ),
                "headers": frozenset({"Python.h", "stddef.h", "stdint.h"}),
                "exports": ZIG_ENGINE_EXPORTS,
            }
        ),
    }
)

FORBIDDEN_MODULE_ROOTS = frozenset(
    {
        "_regex",
        "_sre",
        "cffi",
        "fancy_regex",
        "google_re2",
        "hyperscan",
        "onig",
        "oniguruma",
        "pcre",
        "pcre2",
        "re",
        "re2",
        "regex",
        "rebar",
        "runpy",
        "rust_regex",
        "sre_compile",
        "sre_constants",
        "sre_parse",
        "subprocess",
        "vectorscan",
        "zig",
    }
)
FORBIDDEN_NATIVE_IDENTIFIERS = frozenset(
    {
        "LoadLibrary",
        "LoadLibraryA",
        "LoadLibraryW",
        "GetProcAddress",
        "PyRun_AnyFile",
        "PyRun_SimpleString",
        "PyRun_String",
        "Py_CompileString",
        "PyEval_EvalCode",
        "dlmopen",
        "dlopen",
        "dlsym",
        "dlvsym",
        "execv",
        "execve",
        "fork",
        "popen",
        "posix_spawn",
        "regcomp",
        "regexec",
        "regfree",
        "system",
    }
)
FORBIDDEN_NATIVE_PREFIXES = (
    "_PyImport_",
    "_PyRun_",
    "PyInit__sre",
    "PyImport_ExecCode",
    "PyImport_Import",
    "PyRun_",
    "Py_CompileString",
    "PyEval_Eval",
    "hs_",
    "onig_",
    "pcre2_",
    "pcre_",
    "re2_",
    "regex_",
    "sre_",
)


class AuditFailure(Exception):
    """A concrete ownership, dependency, or guarded-runtime violation."""


def fail(message: str) -> None:
    raise AuditFailure(message)


def require(condition: object, message: str) -> None:
    if not condition:
        fail(message)


def family_spec(family: str):
    require(family in FAMILY_SPECS, f"unknown independently owned family: {family!r}")
    return FAMILY_SPECS[family]


def forbidden_module(name: object, family: str) -> bool:
    if not isinstance(name, str) or not name:
        return True
    spec = family_spec(family)
    root = name.partition(".")[0]
    if root == "candidates":
        return name not in {"candidates", spec["module"], spec["bridge_module"]}
    if root == "ctypes":
        return family != "zig" or name not in {"ctypes", "ctypes._endian"}
    if root in FORBIDDEN_MODULE_ROOTS or root.endswith("_candidate"):
        return True
    return False


def native_symbol_forbidden(name: str) -> bool:
    base = name.partition("@")[0]
    if base == "PyImport_ImportModule":
        return False
    return base in FORBIDDEN_NATIVE_IDENTIFIERS or base.startswith(
        FORBIDDEN_NATIVE_PREFIXES
    )


def attribute_path(node: ast.AST) -> tuple[str, ...] | None:
    pieces: list[str] = []
    while isinstance(node, ast.Attribute):
        pieces.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    return (node.id, *reversed(pieces))


def forbidden_dynamic_call(dotted: str, family: str) -> bool:
    pieces = dotted.split(".")
    if forbidden_module(pieces[0], family):
        return True
    if pieces[0] == "os":
        return any(
            part
            in {"system", "popen", "fork", "posix_spawn", "execv", "execve"}
            for part in pieces[1:]
        )
    if pieces[0] == "builtins":
        return any(part in {"__import__", "eval", "exec"} for part in pieces[1:])
    if pieces[0] == "ctypes":
        return family != "zig" or any(
            part
            in {
                "PyDLL",
                "WinDLL",
                "OleDLL",
                "LibraryLoader",
                "pythonapi",
                "pydll",
                "cdll",
                "windll",
                "oledll",
                "util",
                "_dlopen",
            }
            for part in pieces[1:]
        )
    return False


def inspect_zig_ctypes_loader(tree: ast.AST) -> dict[str, object]:
    classes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == "_Native"
    ]
    require(len(classes) == 1, "Zig adapter lacks its one owned native loader")
    initializers = [
        node
        for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "__init__"
    ]
    require(
        len(initializers) == 1 and isinstance(initializers[0], ast.FunctionDef),
        "Zig adapter lacks its one synchronous owned native initializer",
    )
    body = initializers[0].body
    require(len(body) >= 3, "Zig owned native loader has an incomplete path chain")
    first, second, third = body[:3]
    require(
        isinstance(first, ast.Assign)
        and len(first.targets) == 1
        and isinstance(first.targets[0], ast.Name)
        and first.targets[0].id == "path"
        and isinstance(first.value, ast.Call)
        and attribute_path(first.value.func) == ("os", "path", "join")
        and len(first.value.args) == 2
        and not first.value.keywords
        and isinstance(first.value.args[0], ast.Call)
        and attribute_path(first.value.args[0].func)
        == ("os", "path", "dirname")
        and len(first.value.args[0].args) == 1
        and not first.value.args[0].keywords
        and isinstance(first.value.args[0].args[0], ast.Name)
        and first.value.args[0].args[0].id == "__file__"
        and isinstance(first.value.args[1], ast.Constant)
        and first.value.args[1].value == "_zig_probe.so",
        "Zig ctypes path is not derived from the exact owned adjacent engine",
    )
    require(
        isinstance(second, ast.Assign)
        and len(second.targets) == 1
        and isinstance(second.targets[0], ast.Attribute)
        and attribute_path(second.targets[0]) == ("self", "library")
        and isinstance(second.value, ast.Call)
        and attribute_path(second.value.func) == ("ctypes", "CDLL")
        and len(second.value.args) == 1
        and not second.value.keywords
        and isinstance(second.value.args[0], ast.Name)
        and second.value.args[0].id == "path",
        "Zig ctypes does not load exactly the owned, validated engine path",
    )
    require(
        isinstance(third, ast.Assign)
        and len(third.targets) == 1
        and isinstance(third.targets[0], ast.Name)
        and third.targets[0].id == "lib"
        and isinstance(third.value, ast.Attribute)
        and attribute_path(third.value) == ("self", "library"),
        "Zig ctypes symbols are not bound to the one exact owned library",
    )
    configured: list[str] = []
    for node in ast.walk(initializers[0]):
        if isinstance(node, ast.Attribute):
            path = attribute_path(node)
            if path and len(path) >= 2 and path[0] == "lib":
                require(
                    path[1] in ZIG_CTYPES_SYMBOLS,
                    f"Zig ctypes references an unowned native symbol: {path[1]}",
                )
                configured.append(path[1])
    require(
        frozenset(configured) == ZIG_CTYPES_SYMBOLS,
        "Zig ctypes does not configure exactly its nine owned native symbols",
    )
    return {
        "owned_library": "candidates/_zig_probe.so",
        "configured_symbols": sorted(ZIG_CTYPES_SYMBOLS),
    }


def adapter_imports(source: str, family: str) -> dict[str, object]:
    spec = family_spec(family)
    try:
        tree = ast.parse(source, filename=spec["adapter"])
    except (SyntaxError, TypeError, ValueError) as error:
        fail(f"{family} adapter is not valid Python: {error}")
    modules: list[str] = []
    from_imports: list[tuple[str, str, str | None]] = []
    aliases: dict[str, str] = {}
    owned_ctypes_calls = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                require(
                    alias.name in spec["imports"] and alias.asname is None,
                    f"{family} adapter imports an unowned or aliased module: {alias.name}",
                )
                modules.append(alias.name)
                aliases[alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            require(
                node.level == 0 and node.module is not None and len(node.names) == 1,
                f"{family} adapter uses a relative, wildcard, or multiple import",
            )
            alias = node.names[0]
            value = (node.module, alias.name, alias.asname)
            require(
                value in spec["from_imports"],
                f"{family} adapter imports an unowned module or candidate: {value!r}",
            )
            from_imports.append(value)
            aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        elif isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                require(
                    function.id not in {"__import__", "eval", "exec", "breakpoint"},
                    f"{family} adapter uses dynamic execution: {function.id}",
                )
            elif isinstance(function, ast.Attribute):
                path = attribute_path(function)
                if path:
                    root = aliases.get(path[0], path[0])
                    dotted = ".".join((root, *path[1:]))
                    require(
                        not forbidden_dynamic_call(dotted, family),
                        f"{family} adapter uses a dynamic import or process escape: {dotted}",
                    )
                    if path == ("ctypes", "CDLL"):
                        require(
                            family == "zig"
                            and len(node.args) == 1
                            and not node.keywords
                            and isinstance(node.args[0], ast.Name)
                            and node.args[0].id == "path",
                            "ctypes may load only the exact owned Zig engine path",
                        )
                        owned_ctypes_calls += 1
            if isinstance(function, ast.Name) and function.id == "getattr":
                if node.args and isinstance(node.args[0], ast.Name):
                    require(
                        node.args[0].id not in {"ctypes", "lib"},
                        "adapter computes a ctypes loader or symbol dynamically",
                    )
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    require(
                        node.args[1].value
                        not in {
                            "__import__",
                            "eval",
                            "exec",
                            "system",
                            "popen",
                            "dlopen",
                            "dlsym",
                            "CDLL",
                            "PyDLL",
                            "find_library",
                            "import_module",
                            "load_module",
                            "spec_from_file_location",
                        },
                        f"{family} adapter resolves a dynamic execution escape",
                    )
            if (
                isinstance(function, ast.Name)
                and function.id in {"setattr", "delattr"}
                and node.args
            ):
                target = node.args[0]
                direct_name = target.id if isinstance(target, ast.Name) else None
                target_path = attribute_path(target)
                require(
                    direct_name not in {"ctypes", "lib"}
                    and target_path != ("self", "library"),
                    f"{family} adapter mutates a trusted native loader with {function.id}",
                )
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = (
                node.targets
                if isinstance(node, ast.Assign)
                else (node.target,)
            )
            for target in targets:
                for item in ast.walk(target):
                    if isinstance(item, ast.Name):
                        require(
                            item.id not in {"ctypes", "__file__"},
                            f"{family} adapter rebinds a native ownership primitive",
                        )
                    elif isinstance(item, ast.Attribute):
                        path = attribute_path(item)
                        require(
                            not (path and path[0] == "ctypes"),
                            f"{family} adapter mutates its trusted ctypes loader",
                        )
        elif isinstance(node, ast.Attribute):
            path = attribute_path(node)
            if path and path[0] == "ctypes":
                require(
                    not forbidden_dynamic_call(".".join(path), family),
                    f"{family} adapter resolves an ambient ctypes loader or process",
                )
            require(
                path
                not in {
                    ("lib", "_handle"),
                    ("lib", "__class__"),
                    ("self", "library", "_handle"),
                    ("self", "library", "__class__"),
                },
                f"{family} adapter alters a frozen native library handle",
            )
    require(
        len(modules) == len(spec["imports"])
        and frozenset(modules) == spec["imports"],
        f"{family} adapter does not have exactly its approved module imports",
    )
    require(
        len(from_imports) == len(spec["from_imports"])
        and frozenset(from_imports) == spec["from_imports"],
        f"{family} adapter does not have exactly its approved direct imports",
    )
    result: dict[str, object] = {
        "modules": sorted(modules),
        "from_imports": [list(value) for value in sorted(
            from_imports, key=lambda item: (item[0], item[1], item[2] or "")
        )],
    }
    if family == "zig":
        require(owned_ctypes_calls == 1, "Zig uses more than one native ctypes load")
        result["owned_ctypes"] = inspect_zig_ctypes_loader(tree)
    else:
        require(owned_ctypes_calls == 0, f"{family} uses a native ctypes loader")
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
    result: list[tuple[str, str]] = []
    at = 0
    while at < len(source):
        char = source[at]
        if char.isspace():
            at += 1
        elif source.startswith("//", at):
            newline = source.find("\n", at + 2)
            at = len(source) if newline < 0 else newline + 1
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
            require(depth == 0, "native source has an unterminated block comment")
        elif char == "r" and at + 1 < len(source) and source[at + 1] in {'"', "#"}:
            marker = at + 1
            while marker < len(source) and source[marker] == "#":
                marker += 1
            if marker >= len(source) or source[marker] != '"':
                result.append(("identifier", "r"))
                at += 1
                continue
            ending = '"' + source[at + 1 : marker]
            close = source.find(ending, marker + 1)
            require(close >= 0, "native source has an unterminated raw string")
            result.append(("string", source[marker + 1 : close]))
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
            require(end < len(source), "native source has an unterminated literal")
            try:
                value = ast.literal_eval(source[at : end + 1])
            except (SyntaxError, TypeError, ValueError):
                value = source[at + 1 : end]
            result.append(("string" if quote == '"' else "character", str(value)))
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
    tokens: tuple[tuple[str, str], ...], index: int, family: str
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
    if index >= 4:
        prior = tokens[index - 4 : index]
        return (
            prior[0] == ("identifier", "PyUnicode_CompareWithASCIIString")
            and prior[1] == ("punctuation", "(")
            and prior[2][0] == "identifier"
            and prior[2][1] in names
            and prior[3] == ("punctuation", ",")
        )
    return False


def inspect_bridge(source: str, family: str) -> dict[str, object]:
    spec = family_spec(family)
    includes: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        directive = stripped[1:].lstrip()
        if not directive.startswith("include"):
            continue
        argument = directive[len("include") :].strip()
        require(
            len(argument) >= 3
            and argument.startswith("<")
            and argument.endswith(">"),
            f"{family} native source uses a computed or external include",
        )
        header = argument[1:-1]
        require(header in spec["headers"], f"{family} includes unowned {header!r}")
        includes.append(header)
    require(
        len(includes) == len(spec["headers"])
        and frozenset(includes) == spec["headers"],
        f"{family} native source lacks its exact approved system-header closure",
    )
    tokens = lexical_tokens(source)
    fixed_imports: list[str] = []
    owned_scanners = 0
    for index, (kind, value) in enumerate(tokens):
        if kind == "identifier":
            require(
                not native_symbol_forbidden(value),
                f"{family} native source uses forbidden native symbol {value}",
            )
            if value.startswith("rebar_"):
                require(
                    value in spec["exports"],
                    f"{family} native source borrows another matching engine: {value}",
                )
            if value == "PyImport_ImportModule":
                following = tokens[index + 1 : index + 4]
                require(
                    family == "rust"
                    and len(following) == 3
                    and following[0] == ("punctuation", "(")
                    and following[1][0] == "string"
                    and following[1][1] in {"copyreg", "functools", "inspect"}
                    and following[2] == ("punctuation", ")"),
                    f"{family} native source imports an unapproved Python module",
                )
                fixed_imports.append(following[1][1])
        elif kind == "string":
            if value == "_sre.SRE_Scanner":
                require(
                    index >= 3
                    and tokens[index - 3] == ("punctuation", ".")
                    and tokens[index - 2]
                    in {("identifier", "tp_name"), ("identifier", "name")}
                    and tokens[index - 1] == ("punctuation", "="),
                    f"{family} uses the scanner name outside owned type metadata",
                )
                owned_scanners += 1
            elif value.startswith("candidates."):
                require(
                    value == spec["module"],
                    f"{family} native source references a foreign candidate: {value}",
                )
            elif value in FORBIDDEN_MODULE_ROOTS:
                require(
                    value == "re" and public_re_metadata(tokens, index, family),
                    f"{family} native source embeds a foreign engine name: {value}",
                )
    require(
        owned_scanners == 1,
        f"{family} must declare exactly one independently owned scanner type",
    )
    approved_fixed = {"copyreg", "functools", "inspect"} if family == "rust" else set()
    require(
        len(fixed_imports) == len(approved_fixed)
        and frozenset(fixed_imports) == approved_fixed,
        f"{family} native source has unexpected dynamic Python imports",
    )
    return {
        "includes": sorted(includes),
        "compatibility_imports": sorted(fixed_imports),
        "owned_compatible_scanner_names": owned_scanners,
    }


def inspect_rust_sources(sources: dict[str, str]) -> dict[str, object]:
    require(
        frozenset(sources) == frozenset(RUST_SOURCE_FILES),
        "Rust source closure has a missing, extra, or substituted engine file",
    )
    declarations: list[str] = []
    approved_roots = {"std", "core", "crate", "self", "super", "stack"}
    for path, source in sources.items():
        tokens = lexical_tokens(source)
        for index, (kind, value) in enumerate(tokens):
            if kind != "identifier":
                continue
            require(
                not native_symbol_forbidden(value),
                f"{path} references forbidden native symbol {value}",
            )
            if value.startswith("rebar_"):
                require(value in RUST_ENGINE_EXPORTS, f"{path} borrows {value}")
            if value == "extern" and tokens[index + 1 : index + 2] == (
                ("identifier", "crate"),
            ):
                fail(f"{path} imports an external Rust crate")
            if value in {"include", "include_bytes", "include_str"} and tokens[
                index + 1 : index + 2
            ] == (("punctuation", "!"),):
                fail(f"{path} includes source outside the owned closure")
            if value == "use":
                following = tokens[index + 1 : index + 2]
                require(
                    following
                    and following[0][0] == "identifier"
                    and following[0][1] in approved_roots,
                    f"{path} imports an external Rust namespace",
                )
            if path == RUST_SOURCE_FILES[0] and value == "mod":
                following = tokens[index + 1 : index + 3]
                if (
                    len(following) == 2
                    and following[0][0] == "identifier"
                    and following[1] == ("punctuation", ";")
                ):
                    declarations.append(following[0][1])
            if value in {"path", "link"} and index and tokens[index - 1] == (
                "punctuation",
                "[",
            ):
                fail(f"{path} redirects source ownership or external linking")
    require(
        len(declarations) == 4
        and frozenset(declarations)
        == {"newline", "search", "stack", "unicode_tables"},
        "Rust root does not declare exactly its four independently owned modules",
    )
    return {"source_count": len(sources), "owned_modules": sorted(declarations)}


def inspect_cargo(manifest_source: str, lock_source: str) -> dict[str, object]:
    try:
        manifest = tomllib.loads(manifest_source)
        lock = tomllib.loads(lock_source)
    except (tomllib.TOMLDecodeError, TypeError, ValueError) as error:
        fail(f"owned Rust Cargo sources are not valid TOML: {error}")
    require(
        isinstance(manifest, dict)
        and frozenset(manifest).issubset({"package", "lib", "profile"}),
        "Cargo declares dependencies, a workspace, a build script, or extra targets",
    )
    package = manifest.get("package")
    require(
        isinstance(package, dict)
        and frozenset(package)
        == {"name", "version", "edition", "rust-version", "publish"}
        and package["name"] == "rebar-rust-continuation"
        and package["version"] == "0.1.0"
        and package["edition"] == "2024"
        and package["rust-version"] == "1.85"
        and package["publish"] is False,
        "Cargo package is not the exact unpublished, independently owned engine",
    )
    library = manifest.get("lib")
    require(
        isinstance(library, dict)
        and frozenset(library) == {"crate-type"}
        and library["crate-type"] == ["cdylib"],
        "Cargo library redirects source, adds procedural macros, or is not a cdylib",
    )
    require(
        isinstance(lock, dict)
        and frozenset(lock) == {"version", "package"}
        and lock["version"] == 4,
        "Cargo lockfile adds an external registry, source, or metadata",
    )
    packages = lock["package"]
    require(
        isinstance(packages, list)
        and len(packages) == 1
        and isinstance(packages[0], dict)
        and frozenset(packages[0]) == {"name", "version"}
        and packages[0]["name"] == package["name"]
        and packages[0]["version"] == package["version"],
        "Cargo lockfile contains an external package, dependency, or checksum",
    )
    return {
        "package": package["name"],
        "package_count": 1,
        "external_package_count": 0,
        "build_script_count": 0,
    }


def inspect_zig_source(source: str) -> dict[str, object]:
    tokens = lexical_tokens(source)
    standard_imports = 0
    external_declarations: list[str] = []
    approved_external = frozenset(
        {
            "_PyUnicode_IsAlpha",
            "_PyUnicode_IsDecimalDigit",
            "_PyUnicode_IsDigit",
            "_PyUnicode_IsNumeric",
            "_PyUnicode_IsWhitespace",
            "_PyUnicode_ToLowercase",
            "_PyUnicode_ToUppercase",
            "tolower",
            "isalnum",
        }
    )
    for index, (kind, value) in enumerate(tokens):
        if kind != "identifier":
            continue
        require(
            not native_symbol_forbidden(value),
            f"owned Zig source references a forbidden native symbol: {value}",
        )
        if value.startswith("rebar_"):
            require(value in ZIG_ENGINE_EXPORTS, f"Zig borrows another engine: {value}")
        if index and tokens[index - 1] == ("punctuation", "@"):
            if value == "import":
                require(
                    tokens[index + 1 : index + 4]
                    == (
                        ("punctuation", "("),
                        ("string", "std"),
                        ("punctuation", ")"),
                    ),
                    "Zig imports an external package or another candidate",
                )
                standard_imports += 1
            elif value in {"cImport", "cInclude", "embedFile", "extern"}:
                fail(f"Zig imports external source or a dynamic library: @{value}")
        if value == "extern":
            at = index + 1
            if at < len(tokens) and tokens[at] == ("string", "c"):
                at += 1
            if at < len(tokens) and tokens[at] == ("identifier", "fn"):
                at += 1
                require(
                    at < len(tokens)
                    and tokens[at][0] == "identifier"
                    and tokens[at][1] in approved_external,
                    "Zig links an unowned external matcher or callback",
                )
                external_declarations.append(tokens[at][1])
    require(standard_imports == 1, "Zig source must import exactly its standard library")
    require(
        len(external_declarations) == len(approved_external)
        and frozenset(external_declarations) == approved_external,
        "Zig source does not have exactly its approved Unicode and libc helpers",
    )
    return {
        "standard_library_imports": standard_imports,
        "approved_unicode_and_system_helpers": sorted(external_declarations),
        "external_regex_package_count": 0,
    }


def expected_dynamic(family: str, binary: str) -> tuple[frozenset[str], tuple[str, ...]]:
    spec = family_spec(family)
    require(binary in spec["binaries"], "native inspection path is outside its family")
    if family == "rust" and binary == spec["engine"]:
        return frozenset({"libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2"}), ()
    if family == "rust":
        return frozenset({"_rust_engine.so", "libc.so.6"}), ("$ORIGIN",)
    if family == "c":
        return frozenset({"libc.so.6"}), ()
    if binary == spec["engine"]:
        return frozenset({"libc.so.6"}), ()
    return frozenset({"_zig_probe.so", "libc.so.6"}), ("$ORIGIN",)


def parse_dynamic_section(output: str, family: str, binary: str) -> dict[str, object]:
    expected_needed, expected_paths = expected_dynamic(family, binary)
    needed: list[str] = []
    paths: list[str] = []
    for line in output.splitlines():
        if "(NEEDED)" in line:
            _, separator, suffix = line.partition("[")
            require(separator and suffix.endswith("]"), "malformed ELF dependency")
            needed.append(suffix[:-1])
        elif "(RPATH)" in line:
            fail(f"{binary} uses an externally redirectable legacy RPATH")
        elif "(RUNPATH)" in line:
            _, separator, suffix = line.partition("[")
            require(separator and suffix.endswith("]"), "malformed ELF runpath")
            paths.append(suffix[:-1])
    require(
        len(needed) == len(expected_needed)
        and len(needed) == len(frozenset(needed))
        and frozenset(needed) == expected_needed,
        f"{binary} links a missing, duplicated, foreign, or cross-family library",
    )
    require(
        tuple(paths) == expected_paths,
        f"{binary} has a duplicated, foreign, or externally redirected runpath",
    )
    return {"needed": sorted(needed), "runpaths": list(paths)}


def parse_dynamic_symbols(output: str, family: str, binary: str) -> dict[str, object]:
    spec = family_spec(family)
    require(binary in spec["binaries"], "symbol table is outside its owned family")
    undefined: set[str] = set()
    exported: set[str] = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 8 or not fields[0].rstrip(":").isdigit():
            continue
        bind = fields[4]
        section = fields[6]
        name = fields[7].partition("@")[0]
        require(
            not native_symbol_forbidden(name),
            f"{binary} resolves a forbidden external matcher or execution symbol: {name}",
        )
        if section == "UND":
            require(name not in undefined, f"{binary} duplicates undefined symbol {name}")
            undefined.add(name)
        elif bind in {"GLOBAL", "WEAK"}:
            require(name not in exported, f"{binary} duplicates public symbol {name}")
            exported.add(name)
    require(undefined, f"{binary} has no verifiable undefined dynamic symbols")
    if family == "rust" and binary == spec["engine"]:
        require(
            not (undefined - RUST_ENGINE_UNDEFINED),
            f"{binary} resolves an unapproved Rust native dependency",
        )
        require(exported == RUST_ENGINE_EXPORTS, "Rust engine exports an unowned ABI")
        require(
            "Py_GetRecursionLimit" in undefined,
            "Rust engine lacks its audited CPython recursion-limit helper",
        )
    elif family == "rust":
        unexpected = {
            name
            for name in undefined
            if name not in RUST_ENGINE_EXPORTS
            and name not in RUST_BRIDGE_SYSTEM_UNDEFINED
            and not name.startswith(("Py", "_Py"))
        }
        require(not unexpected, f"Rust bridge resolves foreign symbols: {sorted(unexpected)}")
        require(exported == {"PyInit__rust_bridge"}, "Rust bridge exports a foreign entry")
        require(
            {"rebar_compile", "rebar_compile_scanner", "rebar_match", "rebar_free"}
            <= undefined,
            "Rust bridge does not resolve its own complete matching engine",
        )
        require(
            "PyImport_ImportModule" in undefined,
            "Rust compatibility imports cannot be matched to their literal source",
        )
    elif family == "c":
        unexpected = {
            name
            for name in undefined
            if name not in SYSTEM_NATIVE_UNDEFINED
            and not name.startswith(("Py", "_Py"))
        }
        require(not unexpected, f"C engine resolves foreign symbols: {sorted(unexpected)}")
        require(
            "PyImport_ImportModule" not in undefined,
            "C matching engine imports an unapproved Python module",
        )
        require(exported == {"PyInit__vm_native"}, "C engine exports a foreign entry")
    elif binary == spec["engine"]:
        require(
            undefined == ZIG_ENGINE_UNDEFINED,
            "Zig engine does not have exactly its audited Unicode and libc symbols",
        )
        require(exported == ZIG_ENGINE_EXPORTS, "Zig engine exports an unowned ABI")
    else:
        unexpected = {
            name
            for name in undefined
            if name not in ZIG_ENGINE_EXPORTS
            and name not in SYSTEM_NATIVE_UNDEFINED
            and not name.startswith(("Py", "_Py"))
        }
        require(not unexpected, f"Zig bridge resolves foreign symbols: {sorted(unexpected)}")
        require(exported == {"PyInit__zig_bridge"}, "Zig bridge exports a foreign entry")
        require(
            undefined & ZIG_ENGINE_EXPORTS == ZIG_BRIDGE_REFERENCES,
            "Zig bridge does not reference exactly its own matching engine",
        )
        require(
            "PyImport_ImportModule" not in undefined,
            "Zig matching bridge imports an unapproved Python module",
        )
    return {
        "defined_exports": sorted(exported),
        "undefined_symbol_count": len(undefined),
        "owned_engine_references": sorted(undefined & spec["exports"]),
    }


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def approved_bytes(root: Path, relative: str, family: str) -> bytes:
    spec = family_spec(family)
    approved = frozenset((*spec["sources"], *spec["binaries"], PREDECESSOR))
    require(relative in approved, f"refusing unapproved artifact path: {relative}")
    require(relative in ARTIFACT_SHA256, f"artifact has no prospectively frozen hash: {relative}")
    path = root / relative
    require(not path.is_symlink(), f"frozen artifact is a symlink: {relative}")
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        fail(f"frozen artifact is missing or cannot be resolved: {relative}: {error}")
    require(
        resolved == path.absolute() and resolved.is_file(),
        f"frozen artifact escapes its exact project path: {relative}",
    )
    try:
        value = path.read_bytes()
    except OSError as error:
        fail(f"cannot read the exact frozen artifact {relative}: {error}")
    digest = hashlib.sha256(value).hexdigest()
    require(
        digest == ARTIFACT_SHA256[relative],
        f"frozen source or native binary differs from its recorded hash: {relative}",
    )
    return value


def readelf(root: Path, option: str, binary: str, family: str) -> str:
    spec = family_spec(family)
    require(option in {"--dynamic", "--dyn-syms"}, "unapproved ELF inspection")
    require(binary in spec["binaries"], "ELF inspection escapes its frozen family")
    try:
        result = subprocess.run(
            [READELF, "--wide", option, str(root / binary)],
            cwd=str(root),
            env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        fail(f"cannot inspect frozen native artifact {binary}: {error}")
    require(
        result.returncode == 0 and not result.stderr,
        f"pinned readelf rejected {binary}: {result.stderr.strip()}",
    )
    return result.stdout


def inspect_actual_sources(root: Path, family: str) -> dict[str, object]:
    spec = family_spec(family)
    predecessor = approved_bytes(root, PREDECESSOR, family)
    source_bytes = {
        path: approved_bytes(root, path, family) for path in spec["sources"]
    }
    binary_bytes = {
        path: approved_bytes(root, path, family) for path in spec["binaries"]
    }
    try:
        sources = {path: value.decode("utf-8") for path, value in source_bytes.items()}
    except UnicodeDecodeError as error:
        fail(f"frozen {family} source is not valid UTF-8: {error}")
    adapter = adapter_imports(sources[spec["adapter"]], family)
    bridge = inspect_bridge(sources[spec["bridge_source"]], family)
    implementation: dict[str, object]
    if family == "rust":
        implementation = {
            "cargo": inspect_cargo(
                sources["candidates/rust/Cargo.toml"],
                sources["candidates/rust/Cargo.lock"],
            ),
            "engine": inspect_rust_sources(
                {path: sources[path] for path in RUST_SOURCE_FILES}
            ),
        }
    elif family == "zig":
        implementation = {
            "engine": inspect_zig_source(sources["candidates/zig/mini_regex.zig"])
        }
    else:
        implementation = {"engine": "independently owned Python compiler and native C VM"}
    native: dict[str, object] = {}
    for binary in spec["binaries"]:
        native[binary] = {
            **parse_dynamic_section(
                readelf(root, "--dynamic", binary, family), family, binary
            ),
            **parse_dynamic_symbols(
                readelf(root, "--dyn-syms", binary, family), family, binary
            ),
        }
    return {
        "family": family,
        "source_sha256": {
            path: hashlib.sha256(value).hexdigest()
            for path, value in source_bytes.items()
        },
        "native_sha256": {
            path: hashlib.sha256(value).hexdigest()
            for path, value in binary_bytes.items()
        },
        "predecessor_source_sha256": hashlib.sha256(predecessor).hexdigest(),
        "adapter": adapter,
        "bridge": bridge,
        "implementation": implementation,
        "native": native,
        "external_regex_package_count": 0,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
    }


def validate_ctypes_dlopen(family: str, value: object, expected: str) -> None:
    require(
        family == "zig"
        and isinstance(value, str)
        and os.path.isabs(value)
        and value == expected
        and os.path.normpath(value) == expected,
        "ctypes may load only the exact hash-pinned adjacent Zig engine",
    )


def validate_ctypes_dlsym(
    family: str, library_name: object, symbol: object, expected: str
) -> None:
    require(
        family == "zig"
        and isinstance(library_name, str)
        and library_name == expected
        and isinstance(symbol, str)
        and symbol in ZIG_CTYPES_SYMBOLS,
        "ctypes may resolve only a frozen symbol from the exact owned Zig engine",
    )


def forbid_captured_original_matchers(
    candidate: types.ModuleType,
    bridge: types.ModuleType,
    originals: tuple[object, ...],
    family: str,
) -> int:
    spec = family_spec(family)
    owned_modules = {spec["module"], spec["bridge_module"]}
    seen: set[int] = set()
    checks = 0

    def visit(value: object, depth: int) -> None:
        nonlocal checks
        require(depth <= 24, "owned candidate contains an excessive reference chain")
        identifier = id(value)
        if identifier in seen:
            return
        seen.add(identifier)
        checks += 1
        require(checks <= 40_000, "owned candidate contains an excessive object graph")
        require(
            all(value is not original for original in originals),
            "candidate captured an original Python regular-expression engine or type",
        )
        original_types = tuple(item for item in originals if isinstance(item, type))
        if original_types and not isinstance(value, type):
            require(
                not isinstance(value, original_types),
                "candidate retained a compiled original Python regular expression",
            )
        if isinstance(value, types.ModuleType):
            if value.__name__ not in owned_modules:
                return
            for key, nested in vars(value).items():
                if key not in {"__builtins__", "__loader__", "__spec__"}:
                    visit(nested, depth + 1)
        elif isinstance(value, dict):
            for key, nested in value.items():
                visit(key, depth + 1)
                visit(nested, depth + 1)
        elif isinstance(value, (tuple, list, set, frozenset)):
            for nested in value:
                visit(nested, depth + 1)
        elif isinstance(value, types.FunctionType):
            if value.__module__ in owned_modules:
                visit(value.__defaults__, depth + 1)
                visit(value.__kwdefaults__, depth + 1)
                if value.__closure__:
                    for cell in value.__closure__:
                        try:
                            visit(cell.cell_contents, depth + 1)
                        except ValueError:
                            continue
        elif isinstance(value, type):
            if value.__module__ in owned_modules | {"re"}:
                for key, nested in vars(value).items():
                    if key not in {"__dict__", "__weakref__", "__doc__"}:
                        visit(nested, depth + 1)

    visit(candidate, 0)
    visit(bridge, 0)
    return checks


class ImportBlocker(importlib.abc.MetaPathFinder):
    def __init__(self, family: str, violations: list[str]) -> None:
        self.family = family
        self.violations = violations

    def find_spec(self, fullname: str, path: object = None, target: object = None):
        if forbidden_module(fullname, self.family):
            self.violations.append(f"meta-path:{fullname}")
            fail(f"candidate attempted a forbidden module import: {fullname}")
        return None


def worker_run(root: Path, family: str, expected: dict[str, object]) -> dict[str, object]:
    spec = family_spec(family)
    require(
        isinstance(expected, dict)
        and frozenset(expected)
        == {"family", "source_sha256", "native_sha256", "predecessor_source_sha256"}
        and expected["family"] == family,
        "worker received an incomplete, substituted, or cross-family ownership manifest",
    )
    for label, paths in (
        ("source_sha256", spec["sources"]),
        ("native_sha256", spec["binaries"]),
    ):
        values = expected[label]
        require(
            isinstance(values, dict) and frozenset(values) == frozenset(paths),
            f"worker received an incomplete or substituted {family} {label}",
        )
        for path in paths:
            actual = hashlib.sha256(approved_bytes(root, path, family)).hexdigest()
            require(actual == values[path], f"frozen artifact changed before execution: {path}")
    predecessor_digest = hashlib.sha256(
        approved_bytes(root, PREDECESSOR, family)
    ).hexdigest()
    require(
        predecessor_digest == expected["predecessor_source_sha256"],
        "the frozen original Rust ownership policy changed before execution",
    )

    old_re = sys.modules.get("re")
    old_sre = sys.modules.get("_sre")
    forbidden_identities = tuple(
        item
        for item in (
            old_re,
            old_sre,
            getattr(old_re, "Pattern", None),
            getattr(old_re, "Match", None),
        )
        if item is not None
    )
    removed = tuple(
        name for name in tuple(sys.modules) if forbidden_module(name, family)
    )
    for name in removed:
        sys.modules.pop(name, None)

    violations: list[str] = []
    guarded_import_count = 0
    opened_zig_paths: list[str] = []
    resolved_zig_symbols: list[str] = []
    owned_zig_handles: list[ctypes.CDLL] = []
    exact_zig_engine = str(root / FAMILY_SPECS["zig"]["engine"])
    original_import = builtins.__import__
    original_import_module = importlib.import_module
    blocker = ImportBlocker(family, violations)

    def check_name(name: object, mechanism: str) -> None:
        if forbidden_module(name, family):
            violations.append(f"{mechanism}:{name}")
            fail(f"candidate attempted forbidden {mechanism}: {name}")

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        nonlocal guarded_import_count
        guarded_import_count += 1
        if level:
            package = globals.get("__package__") if isinstance(globals, dict) else None
            require(isinstance(package, str), "candidate uses an unresolvable relative import")
            try:
                resolved = importlib.util.resolve_name("." * level + name, package)
            except (ImportError, ValueError) as error:
                fail(f"candidate uses an invalid relative import: {error}")
        else:
            resolved = name
        check_name(resolved, "builtins-import")
        if resolved == "candidates":
            for item in fromlist or ():
                require(isinstance(item, str), "candidate has an invalid candidate import")
                check_name(f"candidates.{item}", "candidate-from-import")
        return original_import(name, globals, locals, fromlist, level)

    def guarded_import_module(name: str, package: str | None = None):
        resolved = (
            importlib.util.resolve_name(name, package)
            if name.startswith(".") and package
            else name
        )
        check_name(resolved, "importlib-import")
        return original_import_module(name, package)

    def audit_hook(event: str, arguments: tuple[object, ...]) -> None:
        if event == "import" and arguments and isinstance(arguments[0], str):
            check_name(arguments[0], "audit-import")
        elif event == "ctypes.dlopen":
            require(len(arguments) >= 1, "ctypes load has no auditable library")
            try:
                validate_ctypes_dlopen(family, arguments[0], exact_zig_engine)
            except AuditFailure:
                violations.append("audit-event:ctypes.dlopen")
                raise
            opened_zig_paths.append(arguments[0])
            require(len(opened_zig_paths) == 1, "Zig loads more than one native library")
        elif event == "ctypes.dlsym":
            require(len(arguments) >= 2, "ctypes resolution has no library or symbol")
            library = arguments[0]
            try:
                require(
                    type(library) is ctypes.CDLL
                    and library is not ctypes.pythonapi
                    and getattr(library, "_handle", None)
                    not in {None, getattr(ctypes.pythonapi, "_handle", None)},
                    "ctypes uses a foreign, process, or forged native-library handle",
                )
                validate_ctypes_dlsym(
                    family, getattr(library, "_name", None), arguments[1], exact_zig_engine
                )
                require(
                    opened_zig_paths == [exact_zig_engine],
                    "ctypes resolves a Zig symbol before its exact owned load",
                )
                if owned_zig_handles:
                    require(
                        library is owned_zig_handles[0],
                        "ctypes resolves a symbol from a second native library handle",
                    )
                else:
                    owned_zig_handles.append(library)
                require(
                    arguments[1] not in resolved_zig_symbols,
                    "ctypes resolves the same owned Zig symbol more than once",
                )
            except AuditFailure:
                violations.append("audit-event:ctypes.dlsym")
                raise
            resolved_zig_symbols.append(arguments[1])
        elif event in {
            "os.system",
            "os.fork",
            "os.posix_spawn",
            "subprocess.Popen",
        } or event.startswith("os.exec"):
            violations.append(f"audit-event:{event}")
            fail(f"candidate attempted a forbidden process escape: {event}")

    sys.addaudithook(audit_hook)
    sys.meta_path.insert(0, blocker)
    builtins.__import__ = guarded_import
    importlib.import_module = guarded_import_module

    package = types.ModuleType("candidates")
    package.__package__ = "candidates"
    package.__path__ = [str(root / "candidates")]
    sys.modules["candidates"] = package

    bridge_path = root / spec["bridge"]
    bridge_spec = importlib.util.spec_from_file_location(
        spec["bridge_module"], str(bridge_path)
    )
    require(
        bridge_spec is not None
        and isinstance(bridge_spec.loader, importlib.machinery.ExtensionFileLoader)
        and bridge_spec.origin == str(bridge_path)
        and bridge_spec.name == spec["bridge_module"],
        f"guarded worker cannot resolve the exact frozen {family} native extension",
    )
    bridge = importlib.util.module_from_spec(bridge_spec)
    sys.modules[spec["bridge_module"]] = bridge
    setattr(package, spec["bridge_module"].rsplit(".", 1)[1], bridge)
    bridge_spec.loader.exec_module(bridge)

    adapter_path = root / spec["adapter"]
    candidate_spec = importlib.util.spec_from_file_location(
        spec["module"], str(adapter_path)
    )
    require(
        candidate_spec is not None
        and isinstance(candidate_spec.loader, importlib.machinery.SourceFileLoader)
        and candidate_spec.origin == str(adapter_path)
        and candidate_spec.name == spec["module"],
        f"guarded worker cannot resolve the exact frozen {family} Python adapter",
    )
    candidate = importlib.util.module_from_spec(candidate_spec)
    sys.modules[spec["module"]] = candidate
    setattr(package, spec["module"].rsplit(".", 1)[1], candidate)
    candidate_spec.loader.exec_module(candidate)

    require(candidate.Match is bridge.Match, f"{family} match type is not its own extension")
    require(
        all(
            candidate.Pattern is not item and candidate.Match is not item
            for item in forbidden_identities
        ),
        f"{family} public types reuse an original standard-library matcher",
    )
    require(
        candidate.Pattern.__module__ == "re" and candidate.Match.__module__ == "re",
        f"{family} owned native types lack their compatible public names",
    )
    if family == "zig":
        require(
            opened_zig_paths == [exact_zig_engine]
            and frozenset(resolved_zig_symbols) == ZIG_CTYPES_SYMBOLS
            and len(resolved_zig_symbols) == len(ZIG_CTYPES_SYMBOLS)
            and len(owned_zig_handles) == 1
            and candidate._NATIVE.library is owned_zig_handles[0],
            "Zig did not use exactly its frozen engine and nine owned FFI symbols",
        )
    else:
        require(
            not opened_zig_paths and not resolved_zig_symbols and not owned_zig_handles,
            f"{family} performed an unapproved dynamic native load",
        )

    checks = 0

    def check(condition: object, message: str) -> None:
        nonlocal checks
        require(condition, message)
        checks += 1

    pattern = candidate.compile(r"(?P<word>[A-Za-z]+)-(\d+)")
    check(type(pattern) is candidate.Pattern, f"{family} compiled pattern is unowned")
    match = pattern.search("xx alpha-42 yy")
    check(type(match) is bridge.Match, f"{family} search returned an unowned match")
    check(
        match.group(0, "word", 2) == ("alpha-42", "alpha", "42"),
        f"{family} named or numbered matching was not independently performed",
    )
    check(match.span("word") == (3, 8), f"{family} native named span is incorrect")
    check(match.expand(r"\g<word>:\2") == "alpha:42", f"{family} expansion is unowned")
    check(candidate.fullmatch(r"\w+", "hello_42") is not None, f"{family} fullmatch failed")
    check(candidate.match(r"a+", "aaab").span() == (0, 3), f"{family} match failed")
    check(
        candidate.search(rb"a+", memoryview(b"--aaa--")).span() == (2, 5),
        f"{family} bytes-buffer matching failed",
    )
    check(candidate.findall(r"\d+", "a12b345") == ["12", "345"], f"{family} findall failed")
    check(
        [item.span() for item in candidate.finditer(r"\d+", "a12b345")]
        == [(1, 3), (4, 7)],
        f"{family} native iteration failed",
    )
    check(candidate.split(r"\s+", "a  b\tc") == ["a", "b", "c"], f"{family} split failed")
    callback_matches: list[object] = []

    def replacement(item):
        callback_matches.append(item)
        return item.group(0).upper()

    check(
        candidate.sub(r"[a-z]+", replacement, "ab 12 cd") == "AB 12 CD",
        f"{family} legitimate caller replacement callback failed",
    )
    check(
        len(callback_matches) == 2
        and all(type(item) is bridge.Match for item in callback_matches),
        f"{family} replacement callback received foreign matches",
    )
    check(
        candidate.subn(r"\d+", "#", "a12b345") == ("a#b#", 2),
        f"{family} counted substitution failed",
    )
    scanner = candidate.compile(r"\w+").scanner("aa bb")
    check(
        type(scanner).__module__ == "_sre"
        and type(scanner).__name__ == "SRE_Scanner",
        f"{family} scanner lacks its independently owned compatibility name",
    )
    first = scanner.search()
    second = scanner.search()
    check(
        type(first) is bridge.Match
        and type(second) is bridge.Match
        and first.group() == "aa"
        and second.group() == "bb",
        f"{family} scanner returned borrowed or incorrect matches",
    )
    graph_checks = forbid_captured_original_matchers(
        candidate, bridge, forbidden_identities, family
    )
    check(graph_checks > 0, f"{family} ownership graph was not independently inspected")
    check("_sre" not in sys.modules, f"{family} loaded the original CPython engine")
    check(
        frozenset(name for name in sys.modules if name.startswith("candidates."))
        == {spec["bridge_module"], spec["module"]},
        f"{family} imported a foreign candidate or native bridge",
    )
    check(
        not any(forbidden_module(name, family) for name in sys.modules),
        f"{family} loaded a forbidden matcher or external execution module",
    )
    check(not violations, f"{family} recorded a forbidden import or process escape")
    return {
        "status": "PASS",
        "family": family,
        "runtime_checks": checks,
        "owned_graph_checks": graph_checks,
        "guarded_import_calls": guarded_import_count,
        "forbidden_import_or_execution_count": len(violations),
        "removed_preexisting_forbidden_module_count": len(removed),
        "caller_replacement_callback_supported": True,
        "owned_public_re_names_supported": True,
        "owned_public_sre_scanner_name_supported": True,
        "actual_standard_library_engine_loaded": False,
        "candidate_modules": sorted(
            name for name in sys.modules if name.startswith("candidates.")
        ),
        "owned_ctypes_library_load_count": len(opened_zig_paths),
        "owned_ctypes_symbols": sorted(resolved_zig_symbols),
    }


def require_pinned_python() -> None:
    require(
        sys.implementation.name == "cpython"
        and sys.version_info[:3] == PYTHON_VERSION
        and os.path.realpath(sys.executable) == os.path.realpath(PINNED_PYTHON),
        "actual ownership audit requires the exact frozen CPython 3.14.6 interpreter",
    )
    expected_ctypes = os.path.join(
        os.path.dirname(os.path.dirname(PINNED_PYTHON)),
        "lib",
        "python3.14",
        "ctypes",
        "__init__.py",
    )
    require(
        isinstance(getattr(ctypes, "__file__", None), str)
        and os.path.realpath(ctypes.__file__) == os.path.realpath(expected_ctypes)
        and ctypes.CDLL.__module__ == "ctypes"
        and type(ctypes.pythonapi).__module__ == "ctypes",
        "native FFI was not preloaded from the exact frozen CPython standard library",
    )


def run_candidate(family: str) -> dict[str, object]:
    require_pinned_python()
    spec = family_spec(family)
    root = project_root()
    before = inspect_actual_sources(root, family)
    worker_input = {
        "family": family,
        "source_sha256": before["source_sha256"],
        "native_sha256": before["native_sha256"],
        "predecessor_source_sha256": before["predecessor_source_sha256"],
    }
    try:
        result = subprocess.run(
            [
                PINNED_PYTHON,
                "-I",
                "-B",
                str(root / "tools/independent_from_scratch_audit_v2.py"),
                "--_candidate-worker",
                family,
            ],
            cwd=str(root),
            env={
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
            input=json.dumps(worker_input, sort_keys=True),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        fail(f"independent {family} runtime worker failed: {error}")
    require(
        result.returncode == 0 and not result.stderr,
        f"guarded {family} worker rejected the candidate: "
        f"{result.stdout.strip()} {result.stderr.strip()}",
    )
    try:
        runtime = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        fail(f"guarded {family} worker produced invalid evidence: {error}")
    require(
        isinstance(runtime, dict)
        and runtime.get("status") == "PASS"
        and runtime.get("family") == family
        and runtime.get("runtime_checks", 0) >= 20
        and runtime.get("forbidden_import_or_execution_count") == 0,
        f"guarded {family} worker did not establish complete ownership checks",
    )
    after = inspect_actual_sources(root, family)
    require(before == after, f"{family} frozen ownership changed during its guarded audit")
    return {
        "oracle": ORACLE_NAME,
        "status": "PASS",
        "python": {
            "implementation": "cpython",
            "version": list(PYTHON_VERSION),
            "executable": PINNED_PYTHON,
        },
        "candidate": family,
        "candidate_module": spec["module"],
        "ownership": before,
        "runtime": runtime,
        "unchanged_before_after": True,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "final_holdout_opened": False,
        "hidden_cases_read": False,
        "performance_measured": False,
        "winner_selected": False,
    }


def synthetic_dynamic(family: str, binary: str) -> str:
    needed, runpaths = expected_dynamic(family, binary)
    return "\n".join(
        [f"0x1 (NEEDED) Shared library: [{name}]" for name in sorted(needed)]
        + [f"0x1 (RUNPATH) Library runpath: [{path}]" for path in runpaths]
    )


def synthetic_symbols(family: str, binary: str) -> str:
    spec = family_spec(family)
    if family == "rust" and binary == spec["engine"]:
        exports = RUST_ENGINE_EXPORTS
        undefined = {"Py_GetRecursionLimit"}
    elif family == "rust":
        exports = {"PyInit__rust_bridge"}
        undefined = {
            "PyImport_ImportModule",
            "PyObject_CallOneArg",
            "rebar_compile",
            "rebar_compile_scanner",
            "rebar_match",
            "rebar_free",
        }
    elif family == "c":
        exports = {"PyInit__vm_native"}
        undefined = {"PyObject_CallOneArg", "memcpy", "__ctype_b_loc"}
    elif binary == spec["engine"]:
        exports = ZIG_ENGINE_EXPORTS
        undefined = ZIG_ENGINE_UNDEFINED
    else:
        exports = {"PyInit__zig_bridge"}
        undefined = ZIG_BRIDGE_REFERENCES | {"PyObject_CallOneArg", "memcpy"}
    rows = []
    for number, name in enumerate(sorted(exports), start=1):
        rows.append(f"{number}: 0000000000000001 1 FUNC GLOBAL DEFAULT 14 {name}")
    for number, name in enumerate(sorted(undefined), start=len(rows) + 1):
        rows.append(f"{number}: 0000000000000000 0 FUNC GLOBAL DEFAULT UND {name}")
    return "\n".join(rows)


def synthetic_adapter(family: str) -> str:
    spec = family_spec(family)
    lines = [f"import {name}" for name in sorted(spec["imports"])]
    for module, name, alias in sorted(
        spec["from_imports"], key=lambda value: (value[0], value[1], value[2] or "")
    ):
        suffix = f" as {alias}" if alias else ""
        lines.append(f"from {module} import {name}{suffix}")
    if family == "zig":
        lines.extend(
            [
                "class _Native:",
                "    def __init__(self):",
                '        path = os.path.join(os.path.dirname(__file__), "_zig_probe.so")',
                "        self.library = ctypes.CDLL(path)",
                "        lib = self.library",
                *[
                    f"        lib.{symbol}.restype = ctypes.c_void_p"
                    for symbol in sorted(ZIG_CTYPES_SYMBOLS)
                ],
            ]
        )
    else:
        lines.append("def replacement_callback(callback, match):")
        lines.append("    return callback(match)")
    return "\n".join(lines) + "\n"


def synthetic_bridge(family: str) -> str:
    spec = family_spec(family)
    lines = [f"#include <{name}>" for name in sorted(spec["headers"])]
    if family == "rust":
        lines.extend(
            f'PyImport_ImportModule("{name}");'
            for name in ("copyreg", "functools", "inspect")
        )
    scanner_field = "name" if family == "zig" else "tp_name"
    lines.extend(
        [
            f'OwnedScanner = {{ .{scanner_field} = "_sre.SRE_Scanner" }};',
            'OwnedMatch = { .tp_name = "re.Match" };',
            'owned_match_attribute = { "re", owned_descriptor };',
            "PyObject_CallOneArg(user_replacement_callback, owned_match);",
        ]
    )
    return "\n".join(lines) + "\n"


def self_test() -> dict[str, object]:
    """Exercise synthetic objects and strings; never touch actual candidates."""
    positives = 0
    rejections = 0

    def accept(value: object, message: str) -> None:
        nonlocal positives
        require(value, f"synthetic positive failed: {message}")
        positives += 1

    def reject(function, message: str) -> None:
        nonlocal rejections
        try:
            function()
        except AuditFailure:
            rejections += 1
            return
        fail(f"synthetic poison was not rejected: {message}")

    accept(frozenset(FAMILY_SPECS) == {"rust", "c", "zig"}, "three distinct families")
    accept(len(RUST_ENGINE_EXPORTS) == 18, "exact owned Rust engine exports")
    accept(len(ZIG_ENGINE_EXPORTS) == 22, "exact owned Zig engine exports")
    accept(len(ZIG_CTYPES_SYMBOLS) == 9, "exact owned Zig FFI surface")
    accept(len(ZIG_BRIDGE_REFERENCES) == 14, "exact native Zig bridge references")
    accept(
        FAMILY_SPECS["c"]["engine"] == FAMILY_SPECS["c"]["bridge"],
        "C engine and bridge are the same owned native artifact",
    )
    accept(
        all(
            path in ARTIFACT_SHA256
            and len(ARTIFACT_SHA256[path]) == 64
            and all(char in "0123456789abcdef" for char in ARTIFACT_SHA256[path])
            for spec in FAMILY_SPECS.values()
            for path in (*spec["sources"], *spec["binaries"], PREDECESSOR)
        ),
        "all three exact source, binary, and predecessor pins",
    )

    for family in FAMILY_SPECS:
        spec = family_spec(family)
        good_adapter = synthetic_adapter(family)
        inspected_adapter = adapter_imports(good_adapter, family)
        accept(
            len(inspected_adapter["modules"]) == len(spec["imports"]),
            f"{family} exact safe standard-library adapter imports",
        )
        accept(
            len(inspected_adapter["from_imports"]) == len(spec["from_imports"]),
            f"{family} exact owned native candidate import",
        )
        accept(
            not forbidden_module(spec["module"], family)
            and not forbidden_module(spec["bridge_module"], family),
            f"{family} owns its exact adapter and native extension",
        )
        for foreign in (
            "re",
            "re._compiler",
            "_sre",
            "regex",
            "_regex",
            "pcre2",
            "onig",
            "google_re2",
            "hyperscan",
            "subprocess",
            "runpy",
            "candidates.rust_candidate",
            "candidates._rust_bridge",
            "candidates.vm_candidate",
            "candidates._vm_native",
            "candidates.zig_candidate",
            "candidates._zig_bridge",
        ):
            if foreign not in {spec["module"], spec["bridge_module"]}:
                accept(forbidden_module(foreign, family), f"{family} blocks {foreign}")
        for poison in (
            "import re\n",
            "import _sre\n",
            "import regex\n",
            "import pcre2\n",
            "import onig\n",
            "import subprocess\n",
            "import importlib\n",
            "from candidates import another_candidate\n",
            "__import__('re')\n",
            "eval('1')\n",
            "exec('import re')\n",
            "os.system('external-engine')\n",
            "os.popen('external-engine')\n",
            "getattr(os, 'system')('external-engine')\n",
        ):
            reject(
                lambda poison=poison: adapter_imports(good_adapter + poison, family),
                f"{family} dynamic adapter escape: {poison.strip()}",
            )

        good_bridge = synthetic_bridge(family)
        bridge_result = inspect_bridge(good_bridge, family)
        accept(
            bridge_result["owned_compatible_scanner_names"] == 1,
            f"{family} compatible scanner name without importing _sre",
        )
        accept(
            len(bridge_result["includes"]) == len(spec["headers"]),
            f"{family} exact approved CPython and C headers",
        )
        accept(
            isinstance(bridge_result["compatibility_imports"], list),
            f"{family} legitimate native callbacks and compatibility imports",
        )
        for poison in (
            '#include "external_regex.h"\n',
            "#include <pcre2.h>\n",
            "dlopen();\n",
            "dlsym();\n",
            "regcomp();\n",
            "regexec();\n",
            "pcre2_match();\n",
            "onig_search();\n",
            "hs_scan();\n",
            "re2_match();\n",
            "PyRun_SimpleString();\n",
            "PyEval_EvalCode();\n",
            'foreign = "candidates.foreign_candidate";\n',
            'external_scanner = "_sre.SRE_Scanner";\n',
        ):
            reject(
                lambda poison=poison: inspect_bridge(good_bridge + poison, family),
                f"{family} native external-engine escape: {poison.strip()}",
            )

        for binary in spec["binaries"]:
            good_dynamic = synthetic_dynamic(family, binary)
            dynamic_result = parse_dynamic_section(good_dynamic, family, binary)
            expected_needed, expected_paths = expected_dynamic(family, binary)
            accept(
                frozenset(dynamic_result["needed"]) == expected_needed,
                f"{family} owned ELF dependency closure for {binary}",
            )
            accept(
                tuple(dynamic_result["runpaths"]) == expected_paths,
                f"{family} exact nonredirectable owned ELF runpath for {binary}",
            )
            for poison in (
                "0x1 (NEEDED) Shared library: [libpcre2-8.so]\n",
                "0x1 (NEEDED) Shared library: [libre2.so]\n",
                "0x1 (NEEDED) Shared library: [libonig.so]\n",
                "0x1 (NEEDED) Shared library: [_foreign_candidate.so]\n",
                "0x1 (NEEDED) Shared library: [libc.so.6]\n",
                "0x1 (RUNPATH) Library runpath: [/foreign]\n",
                "0x1 (RPATH) Library rpath: [$ORIGIN]\n",
            ):
                reject(
                    lambda poison=poison: parse_dynamic_section(
                        good_dynamic + "\n" + poison.rstrip("\n"), family, binary
                    ),
                    f"{family} external or duplicated ELF dependency",
                )
            good_symbols = synthetic_symbols(family, binary)
            symbol_result = parse_dynamic_symbols(good_symbols, family, binary)
            accept(
                bool(symbol_result["defined_exports"]),
                f"{family} exact owned public ABI for {binary}",
            )
            for symbol in (
                "dlopen",
                "dlsym",
                "regcomp",
                "regexec",
                "pcre2_match",
                "onig_search",
                "hs_scan",
                "re2_match",
                "PyRun_SimpleString",
                "PyEval_EvalCode",
                "PyInit__sre",
                "borrowed_matching_engine",
            ):
                row = f"999: 0000000000000000 0 FUNC GLOBAL DEFAULT UND {symbol}"
                reject(
                    lambda row=row: parse_dynamic_symbols(
                        good_symbols + "\n" + row, family, binary
                    ),
                    f"{family} foreign native matching symbol {symbol}",
                )
            for entry in ("PyInit__rust_bridge", "PyInit__vm_native", "PyInit__zig_bridge"):
                current_exports = set(symbol_result["defined_exports"])
                if entry not in current_exports:
                    row = f"998: 0000000000000001 1 FUNC GLOBAL DEFAULT 14 {entry}"
                    reject(
                        lambda row=row: parse_dynamic_symbols(
                            good_symbols + "\n" + row, family, binary
                        ),
                        f"{family} cross-family native extension entry {entry}",
                    )
            if family == "rust" and binary == spec["bridge"]:
                for symbol in (
                    "__ctype_b_loc",
                    "__ctype_tolower_loc",
                    "__memcpy_chk",
                    "bcmp",
                ):
                    row = (
                        "997: 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
                        + symbol
                    )
                    reject(
                        lambda row=row: parse_dynamic_symbols(
                            good_symbols + "\n" + row, family, binary
                        ),
                        f"preserved original Rust bridge rejects unapproved {symbol}",
                    )
            missing = "\n".join(good_symbols.splitlines()[1:])
            reject(
                lambda missing=missing: parse_dynamic_symbols(missing, family, binary),
                f"{family} missing or substituted owned export",
            )

    good_rust = {path: "" for path in RUST_SOURCE_FILES}
    good_rust[RUST_SOURCE_FILES[0]] = (
        "use std::slice;\nmod newline;\nmod search;\n"
        "mod stack;\nmod unicode_tables;\nuse stack::InlineStack;\n"
    )
    accept(
        inspect_rust_sources(good_rust)["source_count"] == 5,
        "preserved original complete five-file Rust semantic source closure",
    )
    for poison in (
        "extern crate regex;\n",
        "use regex::Regex;\n",
        'include!("foreign.rs");\n',
        'include_bytes!("foreign.so");\n',
        "dlopen();\n",
        "pcre2_match();\n",
        "regexec();\n",
        "rebar_zig_compile();\n",
    ):
        def poisoned_rust(poison=poison):
            changed = dict(good_rust)
            changed[RUST_SOURCE_FILES[0]] += poison
            return inspect_rust_sources(changed)

        reject(poisoned_rust, f"Rust external semantic implementation: {poison.strip()}")
    reject(
        lambda: inspect_rust_sources({RUST_SOURCE_FILES[0]: good_rust[RUST_SOURCE_FILES[0]]}),
        "missing independently owned Rust source module",
    )

    manifest = (
        '[package]\nname = "rebar-rust-continuation"\nversion = "0.1.0"\n'
        'edition = "2024"\nrust-version = "1.85"\npublish = false\n'
        '[lib]\ncrate-type = ["cdylib"]\n'
    )
    lock = (
        'version = 4\n[[package]]\nname = "rebar-rust-continuation"\n'
        'version = "0.1.0"\n'
    )
    accept(
        inspect_cargo(manifest, lock)["external_package_count"] == 0,
        "preserved original one-package dependency-free Rust lockfile",
    )
    for poison in (
        '\n[dependencies]\nregex = "1"\n',
        '\n[build-dependencies]\ncc = "1"\n',
        '\n[workspace]\nmembers = ["foreign"]\n',
    ):
        reject(
            lambda poison=poison: inspect_cargo(manifest + poison, lock),
            "Rust manifest external package, build script, or workspace",
        )
    reject(
        lambda: inspect_cargo(
            manifest,
            lock + '\n[[package]]\nname = "regex"\nversion = "1.0.0"\n',
        ),
        "external regular-expression package in the Rust lockfile",
    )

    approved_external = (
        "_PyUnicode_IsAlpha",
        "_PyUnicode_IsDecimalDigit",
        "_PyUnicode_IsDigit",
        "_PyUnicode_IsNumeric",
        "_PyUnicode_IsWhitespace",
        "_PyUnicode_ToLowercase",
        "_PyUnicode_ToUppercase",
        "tolower",
        "isalnum",
    )
    good_zig = 'const std = @import("std");\n' + "".join(
        f"extern fn {name}(u32) c_int;\n" for name in approved_external
    )
    accept(
        inspect_zig_source(good_zig)["external_regex_package_count"] == 0,
        "independent Zig parser imports only its standard library and Unicode helpers",
    )
    for poison in (
        '@import("regex");\n',
        '@import("pcre");\n',
        '@cImport("pcre.h");\n',
        '@embedFile("foreign.so");\n',
        "extern fn regexec(u32) c_int;\n",
        "extern fn foreign_match(u32) c_int;\n",
        "rebar_compile();\n",
    ):
        reject(
            lambda poison=poison: inspect_zig_source(good_zig + poison),
            f"Zig external matcher or source escape: {poison.strip()}",
        )

    exact_engine = "/owned/candidates/_zig_probe.so"
    for symbol in sorted(ZIG_CTYPES_SYMBOLS):
        validate_ctypes_dlsym("zig", exact_engine, symbol, exact_engine)
        accept(True, f"exact owned Zig ctypes symbol {symbol}")
    validate_ctypes_dlopen("zig", exact_engine, exact_engine)
    accept(True, "exact hash-pinned adjacent Zig ctypes engine path")
    for family in ("rust", "c"):
        reject(
            lambda family=family: validate_ctypes_dlopen(family, exact_engine, exact_engine),
            f"{family} must not perform any ctypes native loading",
        )
        reject(
            lambda family=family: validate_ctypes_dlsym(
                family, exact_engine, "rebar_zig_compile", exact_engine
            ),
            f"{family} must not resolve any Zig native symbols",
        )
    for foreign_path in (
        None,
        "_zig_probe.so",
        "/owned/candidates/../candidates/_zig_probe.so",
        "/owned/candidates/libc.so.6",
        "/owned/candidates/libpcre2-8.so",
        "/owned/candidates/_rust_engine.so",
        "/owned/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    ):
        reject(
            lambda foreign_path=foreign_path: validate_ctypes_dlopen(
                "zig", foreign_path, exact_engine
            ),
            "Zig ctypes foreign, relative, traversal, or ambient library",
        )
    for foreign_symbol in (
        "rebar_compile",
        "regexec",
        "pcre2_match",
        "onig_search",
        "PyRun_SimpleString",
        "system",
        "rebar_zig_match",
        None,
    ):
        reject(
            lambda foreign_symbol=foreign_symbol: validate_ctypes_dlsym(
                "zig", exact_engine, foreign_symbol, exact_engine
            ),
            "Zig ctypes unapproved external or cross-family symbol",
        )
    reject(
        lambda: validate_ctypes_dlsym(
            "zig", "/foreign/libpcre.so", "rebar_zig_compile", exact_engine
        ),
        "Zig ctypes resolves an owned-looking symbol from a foreign library",
    )
    good_zig_adapter = synthetic_adapter("zig")
    for poisoned in (
        good_zig_adapter.replace('"_zig_probe.so"', '"libpcre2-8.so"'),
        good_zig_adapter.replace("ctypes.CDLL(path)", "ctypes.CDLL(None)"),
        good_zig_adapter.replace("ctypes.CDLL(path)", "ctypes.CDLL('foreign.so')"),
        good_zig_adapter.replace("ctypes.CDLL(path)", "ctypes.PyDLL(path)"),
        good_zig_adapter + "ctypes.CDLL(path)\n",
        good_zig_adapter + "getattr(ctypes, 'CDLL')('foreign.so')\n",
        good_zig_adapter + "getattr(lib, 'foreign_match')\n",
        good_zig_adapter + "ctypes.pythonapi\n",
        good_zig_adapter + "ctypes.util\n",
        good_zig_adapter + "lib._handle\n",
        good_zig_adapter + "lib.__class__\n",
        good_zig_adapter + "setattr(ctypes, 'CDLL', replacement)\n",
        good_zig_adapter + "setattr(ctypes, 'pythonapi', replacement)\n",
        good_zig_adapter + "delattr(ctypes, 'CDLL')\n",
        good_zig_adapter + "setattr(lib, '_handle', replacement)\n",
        good_zig_adapter + "delattr(lib, '_handle')\n",
        good_zig_adapter + "ctypes.CDLL = replacement\n",
        good_zig_adapter + "ctypes = replacement\n",
    ):
        reject(lambda poisoned=poisoned: adapter_imports(poisoned, "zig"), "foreign Zig FFI")

    for family in FAMILY_SPECS:
        spec = family_spec(family)
        original_re = types.ModuleType("re")
        original_sre = types.ModuleType("_sre")
        original_pattern = type("OriginalPattern", (), {})
        original_match = type("OriginalMatch", (), {})
        original_re.Pattern = original_pattern
        original_re.Match = original_match
        originals = (original_re, original_sre, original_pattern, original_match)
        clean_candidate = types.ModuleType(spec["module"])
        clean_bridge = types.ModuleType(spec["bridge_module"])
        clean_candidate.safe = ("independent", 1, None)
        accept(
            forbid_captured_original_matchers(
                clean_candidate, clean_bridge, originals, family
            )
            > 0,
            f"{family} safe owned candidate module graph",
        )
        for captured in (
            original_re,
            original_sre,
            original_pattern,
            original_match,
            original_pattern(),
            original_match(),
            {"hidden": original_re},
            ("hidden", original_pattern),
        ):
            def poisoned_capture(captured=captured):
                candidate = types.ModuleType(spec["module"])
                candidate.hidden = captured
                bridge = types.ModuleType(spec["bridge_module"])
                return forbid_captured_original_matchers(
                    candidate, bridge, originals, family
                )

            reject(poisoned_capture, f"{family} captured original engine or matcher")

    require(positives >= 80, "synthetic safe ownership-control count is incomplete")
    require(rejections >= 200, "synthetic external-engine rejection count is incomplete")
    return {
        "oracle": ORACLE_NAME,
        "status": "PASS",
        "self_test_only": True,
        "families": ["rust", "c", "zig"],
        "synthetic_positive_controls": positives,
        "synthetic_rejection_controls": rejections,
        "actual_candidate_ownership_established": False,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "real_candidate_imported": False,
        "real_candidate_executed": False,
        "real_candidate_files_read": False,
        "real_native_binary_read": False,
        "external_process_started": False,
        "evidence_files_created": False,
        "final_holdout_opened": False,
        "hidden_cases_read": False,
        "performance_measured": False,
        "winner_selected": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--candidate", choices=tuple(FAMILY_SPECS))
    group.add_argument(
        "--_candidate-worker", choices=tuple(FAMILY_SPECS), help=argparse.SUPPRESS
    )
    arguments = parser.parse_args()
    try:
        if arguments.self_test:
            result = self_test()
        elif arguments.candidate:
            result = run_candidate(arguments.candidate)
        else:
            require_pinned_python()
            try:
                expected = json.load(sys.stdin)
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                fail(f"guarded worker received invalid frozen ownership evidence: {error}")
            result = worker_run(project_root(), arguments._candidate_worker, expected)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except (AuditFailure, OSError, TypeError, ValueError) as error:
        print(
            json.dumps(
                {"oracle": ORACLE_NAME, "status": "FAIL", "error": str(error)},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
