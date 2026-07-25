#!/usr/bin/env python3
"""Fail-closed, independently reproducible Rust-engine ownership audit.

``--self-test`` uses only synthetic, in-memory controls. In particular it does
not inspect, import, execute, or make a claim about an actual candidate.
``--candidate`` is the separate, explicit actual-candidate observation.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import copyreg
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
import subprocess
import sys
import tomllib
import types


ORACLE_NAME = "rust-from-scratch-audit-v1"
PYTHON_VERSION = (3, 14, 6)
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
READELF = "/usr/bin/readelf"

ADAPTER = "candidates/rust_candidate.py"
BRIDGE_SOURCE = "candidates/rust/py_bridge.c"
MANIFEST = "candidates/rust/Cargo.toml"
LOCKFILE = "candidates/rust/Cargo.lock"
RUST_SOURCES = (
    "candidates/rust/src/lib.rs",
    "candidates/rust/src/newline.rs",
    "candidates/rust/src/search.rs",
    "candidates/rust/src/stack.rs",
    "candidates/rust/src/unicode_tables.rs",
)
ENGINE_BINARY = "candidates/_rust_engine.so"
BRIDGE_BINARY = "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
SOURCE_CLOSURE = (ADAPTER, BRIDGE_SOURCE, MANIFEST, LOCKFILE, *RUST_SOURCES)
BINARY_CLOSURE = (ENGINE_BINARY, BRIDGE_BINARY)
OWNED_CANDIDATE_MODULES = frozenset(
    {"candidates", "candidates.rust_candidate", "candidates._rust_bridge"}
)
ALLOWED_ADAPTER_IMPORTS = frozenset(
    {"enum", "operator", "os", "types", "unicodedata", "warnings"}
)
ALLOWED_BRIDGE_IMPORTS = frozenset({"copyreg", "functools", "inspect"})
ALLOWED_C_INCLUDES = frozenset({"Python.h", "stddef.h", "stdint.h", "string.h"})
OWNED_ENGINE_EXPORTS = frozenset(
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
ALLOWED_ENGINE_UNDEFINED = frozenset(
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
ALLOWED_BRIDGE_SYSTEM_UNDEFINED = frozenset(
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
FORBIDDEN_MODULE_ROOTS = frozenset(
    {
        "_regex",
        "_sre",
        "cffi",
        "ctypes",
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
    """A concrete ownership, dependency, or runtime-guard violation."""


def fail(message: str) -> None:
    raise AuditFailure(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def forbidden_module(name: str) -> bool:
    if not isinstance(name, str) or not name:
        return True
    root = name.partition(".")[0]
    if root in FORBIDDEN_MODULE_ROOTS or root.endswith("_candidate"):
        return name != "candidates.rust_candidate"
    if root == "candidates":
        return name not in OWNED_CANDIDATE_MODULES
    return False


def native_symbol_forbidden(name: str) -> bool:
    base = name.partition("@")[0]
    if base == "PyImport_ImportModule":
        return False
    return base in FORBIDDEN_NATIVE_IDENTIFIERS or base.startswith(
        FORBIDDEN_NATIVE_PREFIXES
    )


def adapter_imports(source: str) -> tuple[str, ...]:
    try:
        tree = ast.parse(source, filename=ADAPTER)
    except (SyntaxError, ValueError, TypeError) as error:
        fail(f"adapter is not valid Python source: {error}")

    imports: list[str] = []
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                require(
                    name in ALLOWED_ADAPTER_IMPORTS,
                    f"adapter imports an unowned or forbidden module: {name}",
                )
                imports.append(name)
                aliases[alias.asname or name] = name
        elif isinstance(node, ast.ImportFrom):
            require(
                node.level == 0
                and node.module == "candidates"
                and len(node.names) == 1
                and node.names[0].name == "_rust_bridge"
                and node.names[0].asname is None,
                "adapter uses an unowned, relative, or dynamic candidate import",
            )
            imports.append("candidates._rust_bridge")
            aliases["_rust_bridge"] = "candidates._rust_bridge"
        elif isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                require(
                    function.id not in {"__import__", "eval", "exec", "breakpoint"},
                    f"adapter uses a dynamic execution or import escape: {function.id}",
                )
            elif isinstance(function, ast.Attribute):
                path = attribute_path(function)
                if path:
                    root = aliases.get(path[0], path[0])
                    dotted = ".".join((root, *path[1:]))
                    require(
                        not forbidden_dynamic_call(dotted),
                        f"adapter uses a dynamic import or process escape: {dotted}",
                    )
            if (
                isinstance(function, ast.Name)
                and function.id == "getattr"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value
                in {"__import__", "eval", "exec", "system", "popen", "dlopen"}
            ):
                fail("adapter resolves a dynamic execution escape through getattr")

    expected = ALLOWED_ADAPTER_IMPORTS | {"candidates._rust_bridge"}
    require(
        len(imports) == len(expected) and frozenset(imports) == expected,
        "adapter does not have exactly the approved, independently owned import closure",
    )
    return tuple(sorted(imports))


def attribute_path(node: ast.AST) -> tuple[str, ...] | None:
    pieces: list[str] = []
    while isinstance(node, ast.Attribute):
        pieces.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    return (node.id, *reversed(pieces))


def forbidden_dynamic_call(dotted: str) -> bool:
    pieces = dotted.split(".")
    if forbidden_module(pieces[0]):
        return True
    if pieces[0] == "os":
        return any(
            piece in {"system", "popen", "fork", "posix_spawn", "execv", "execve"}
            for piece in pieces[1:]
        )
    if pieces[0] == "builtins":
        return any(piece in {"__import__", "eval", "exec"} for piece in pieces[1:])
    return False


def lexical_tokens(source: str) -> tuple[tuple[str, str], ...]:
    """Tokenize C/Rust identifiers and literals without trusting comments."""
    result: list[tuple[str, str]] = []
    at = 0
    length = len(source)
    while at < length:
        char = source[at]
        if char.isspace():
            at += 1
        elif source.startswith("//", at):
            newline = source.find("\n", at + 2)
            at = length if newline < 0 else newline + 1
        elif source.startswith("/*", at):
            depth = 1
            at += 2
            while at < length and depth:
                if source.startswith("/*", at):
                    depth += 1
                    at += 2
                elif source.startswith("*/", at):
                    depth -= 1
                    at += 2
                else:
                    at += 1
            require(depth == 0, "native source contains an unterminated block comment")
        elif char == 'r' and at + 1 < length and source[at + 1] in {'"', '#'}:
            marker = at + 1
            while marker < length and source[marker] == '#':
                marker += 1
            if marker >= length or source[marker] != '"':
                result.append(("identifier", "r"))
                at += 1
                continue
            ending = '"' + source[at + 1 : marker]
            close = source.find(ending, marker + 1)
            require(close >= 0, "native source contains an unterminated raw string")
            result.append(("string", source[marker + 1 : close]))
            at = close + len(ending)
        elif char == "'" and not rust_or_c_character_literal(source, at):
            # Rust lifetimes and loop labels are not quoted characters.
            result.append(("punctuation", char))
            at += 1
        elif char in {'"', "'"}:
            quote = char
            end = at + 1
            while end < length:
                if source[end] == "\\":
                    end += 2
                elif source[end] == quote:
                    break
                else:
                    end += 1
            require(end < length, "native source contains an unterminated literal")
            literal = source[at : end + 1]
            try:
                value = ast.literal_eval(literal)
            except (SyntaxError, ValueError, TypeError):
                value = source[at + 1 : end]
            result.append(("string" if quote == '"' else "character", str(value)))
            at = end + 1
        elif char.isalpha() or char == "_":
            end = at + 1
            while end < length and (
                source[end].isalnum() or source[end] == "_"
            ):
                end += 1
            result.append(("identifier", source[at:end]))
            at = end
        else:
            result.append(("punctuation", char))
            at += 1
    return tuple(result)


def rust_or_c_character_literal(source: str, at: int) -> bool:
    """Distinguish genuine character literals from Rust lifetimes/labels."""
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


def owned_public_re_metadata(
    tokens: tuple[tuple[str, str], ...], index: int
) -> bool:
    """Permit the compatible match attribute and owned public-type check only."""
    if index and tokens[index - 1] == ("punctuation", "{"):
        return True
    if index >= 4 and tokens[index - 4 : index] == (
        ("identifier", "PyUnicode_CompareWithASCIIString"),
        ("punctuation", "("),
        ("identifier", "pattern_module"),
        ("punctuation", ","),
    ):
        return True
    return False


def inspect_bridge(source: str) -> dict[str, object]:
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
            and argument[0] == "<"
            and argument[-1] == ">",
            "C bridge uses a non-system, computed, or external source include",
        )
        header = argument[1:-1]
        require(header in ALLOWED_C_INCLUDES, f"C bridge includes {header!r}")
        includes.append(header)
    require(
        len(includes) == len(ALLOWED_C_INCLUDES)
        and frozenset(includes) == ALLOWED_C_INCLUDES,
        "C bridge does not have exactly the approved CPython/C-system headers",
    )

    tokens = lexical_tokens(source)
    fixed_imports: list[str] = []
    owned_scanner_names = 0
    for index, (kind, value) in enumerate(tokens):
        if kind == "identifier" and native_symbol_forbidden(value):
            fail(f"C bridge references a forbidden native execution symbol: {value}")
        if kind == "identifier" and value == "PyImport_ImportModule":
            following = tokens[index + 1 : index + 4]
            require(
                len(following) == 3
                and following[0] == ("punctuation", "(")
                and following[1][0] == "string"
                and following[1][1] in ALLOWED_BRIDGE_IMPORTS
                and following[2] == ("punctuation", ")"),
                "C bridge dynamically imports an unapproved Python module",
            )
            fixed_imports.append(following[1][1])
        if kind == "string" and value == "_sre.SRE_Scanner":
            require(
                index >= 3
                and tokens[index - 3 : index]
                == (
                    ("punctuation", "."),
                    ("identifier", "tp_name"),
                    ("punctuation", "="),
                ),
                "C bridge uses the CPython scanner name outside owned type metadata",
            )
            owned_scanner_names += 1
        if (
            kind == "string"
            and value in FORBIDDEN_MODULE_ROOTS
            and not (value == "re" and owned_public_re_metadata(tokens, index))
        ):
            fail(f"C bridge embeds a forbidden external-engine module name: {value}")
    require(
        len(fixed_imports) == len(ALLOWED_BRIDGE_IMPORTS)
        and frozenset(fixed_imports) == ALLOWED_BRIDGE_IMPORTS,
        "C bridge does not have exactly its approved non-regex compatibility imports",
    )
    require(
        owned_scanner_names == 1,
        "C bridge does not declare exactly one independently owned compatible scanner type",
    )
    return {
        "includes": sorted(includes),
        "compatibility_imports": sorted(fixed_imports),
        "owned_compatible_scanner_names": owned_scanner_names,
    }


def inspect_rust_sources(sources: dict[str, str]) -> dict[str, object]:
    require(
        frozenset(sources) == frozenset(RUST_SOURCES),
        "Rust source closure is missing an owned file or contains an extra file",
    )
    approved_roots = {"std", "core", "crate", "self", "super", "stack"}
    declarations: list[str] = []
    for path, source in sources.items():
        tokens = lexical_tokens(source)
        for index, (kind, value) in enumerate(tokens):
            if kind != "identifier":
                continue
            if native_symbol_forbidden(value):
                fail(f"{path} references a forbidden native symbol: {value}")
            if value == "extern" and tokens[index + 1 : index + 2] == (
                ("identifier", "crate"),
            ):
                fail(f"{path} imports an external Rust crate")
            if value in {"include", "include_bytes", "include_str"} and tokens[
                index + 1 : index + 2
            ] == (("punctuation", "!"),):
                fail(f"{path} includes source or data outside the frozen source closure")
            if value == "use":
                next_token = tokens[index + 1 : index + 2]
                require(
                    bool(next_token)
                    and next_token[0][0] == "identifier"
                    and next_token[0][1] in approved_roots,
                    f"{path} imports an external or unowned Rust namespace",
                )
            if path == RUST_SOURCES[0] and value == "mod":
                next_pair = tokens[index + 1 : index + 3]
                if (
                    len(next_pair) == 2
                    and next_pair[0][0] == "identifier"
                    and next_pair[1] == ("punctuation", ";")
                ):
                    declarations.append(next_pair[0][1])
            if value in {"path", "link"} and index and tokens[index - 1] == (
                "punctuation",
                "[",
            ):
                fail(f"{path} redirects source ownership or links an external library")
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
    except (tomllib.TOMLDecodeError, ValueError, TypeError) as error:
        fail(f"Cargo source is not valid TOML: {error}")
    require(isinstance(manifest, dict), "Cargo manifest is not a TOML table")
    require(
        frozenset(manifest).issubset({"package", "lib", "profile"}),
        "Cargo manifest declares dependencies, a build script, a workspace, or external targets",
    )
    package = manifest.get("package")
    require(isinstance(package, dict), "Cargo manifest does not declare an owned package")
    require(
        frozenset(package)
        == {"name", "version", "edition", "rust-version", "publish"},
        "Cargo package contains a build script, link override, or unfrozen metadata",
    )
    require(
        package["name"] == "rebar-rust-continuation"
        and package["version"] == "0.1.0"
        and package["edition"] == "2024"
        and package["rust-version"] == "1.85"
        and package["publish"] is False,
        "Cargo manifest does not describe the exact unpublished, independently owned Rust package",
    )
    library = manifest.get("lib")
    require(
        isinstance(library, dict)
        and frozenset(library) == {"crate-type"}
        and library["crate-type"] == ["cdylib"],
        "Cargo library redirects its source, uses a procedural macro, or is not the owned cdylib",
    )
    require(isinstance(lock, dict), "Cargo lockfile is not a TOML table")
    require(
        frozenset(lock) == {"version", "package"} and lock["version"] == 4,
        "Cargo lockfile has external metadata, a source registry, or an unsupported version",
    )
    packages = lock["package"]
    require(
        isinstance(packages, list)
        and len(packages) == 1
        and isinstance(packages[0], dict)
        and frozenset(packages[0]) == {"name", "version"}
        and packages[0]["name"] == package["name"]
        and packages[0]["version"] == package["version"],
        "Cargo lockfile contains an external package, source, checksum, or dependency",
    )
    return {
        "package": package["name"],
        "package_count": 1,
        "external_package_count": 0,
        "build_script_count": 0,
    }


def parse_dynamic_section(output: str, binary: str) -> dict[str, object]:
    needed: list[str] = []
    runpaths: list[str] = []
    for line in output.splitlines():
        if "(NEEDED)" in line:
            prefix, separator, suffix = line.partition("[")
            require(bool(separator) and suffix.endswith("]"), "malformed ELF dependency")
            needed.append(suffix[:-1])
        elif "(RUNPATH)" in line or "(RPATH)" in line:
            _, separator, suffix = line.partition("[")
            require(bool(separator) and suffix.endswith("]"), "malformed ELF runpath")
            runpaths.append(suffix[:-1])
    expected = (
        {"libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2"}
        if binary == ENGINE_BINARY
        else {"_rust_engine.so", "libc.so.6"}
    )
    require(
        len(needed) == len(expected) and frozenset(needed) == expected,
        f"{binary} links an unexpected, missing, duplicated, or external shared library",
    )
    expected_runpaths = [] if binary == ENGINE_BINARY else ["$ORIGIN"]
    require(
        runpaths == expected_runpaths,
        f"{binary} has an unowned or externally redirected library search path",
    )
    return {"needed": sorted(needed), "runpaths": runpaths}


def parse_dynamic_symbols(output: str, binary: str) -> dict[str, object]:
    undefined: set[str] = set()
    exported: set[str] = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 8 or not fields[0].rstrip(":").isdigit():
            continue
        bind, section, name = fields[4], fields[6], fields[7].partition("@")[0]
        require(
            not native_symbol_forbidden(name),
            f"{binary} references a forbidden external engine or dynamic-execution symbol: {name}",
        )
        if section == "UND":
            undefined.add(name)
        elif bind in {"GLOBAL", "WEAK"}:
            exported.add(name)
    require(bool(undefined), f"{binary} has no verifiable dynamic symbol table")
    if binary == ENGINE_BINARY:
        unexpected = undefined - ALLOWED_ENGINE_UNDEFINED
        require(
            not unexpected,
            "Rust engine resolves an unapproved native symbol: "
            + ", ".join(sorted(unexpected)),
        )
        require(
            exported == OWNED_ENGINE_EXPORTS,
            "Rust engine does not export exactly its independently owned regular-expression ABI",
        )
        require(
            "Py_GetRecursionLimit" in undefined,
            "Rust engine is missing its approved CPython recursion-limit dependency",
        )
    else:
        unexpected = {
            name
            for name in undefined
            if name not in OWNED_ENGINE_EXPORTS
            and name not in ALLOWED_BRIDGE_SYSTEM_UNDEFINED
            and not name.startswith(("Py", "_Py"))
        }
        require(
            not unexpected,
            "CPython bridge resolves an unapproved or foreign native symbol: "
            + ", ".join(sorted(unexpected)),
        )
        require(
            exported == {"PyInit__rust_bridge"},
            "CPython bridge exports unowned native entry points",
        )
        referenced_engine = undefined & OWNED_ENGINE_EXPORTS
        require(
            {"rebar_compile", "rebar_compile_scanner", "rebar_match", "rebar_free"}
            <= referenced_engine,
            "CPython bridge is not linked to its independently owned Rust matching engine",
        )
        require(
            "PyImport_ImportModule" in undefined,
            "CPython bridge import sites cannot be matched to their approved literal audit",
        )
    return {
        "defined_exports": sorted(exported),
        "undefined_symbol_count": len(undefined),
        "owned_engine_references": sorted(undefined & OWNED_ENGINE_EXPORTS),
    }


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def approved_bytes(root: Path, relative: str) -> bytes:
    require(
        relative in SOURCE_CLOSURE or relative in BINARY_CLOSURE,
        f"refusing to inspect a path outside the explicit ownership closure: {relative}",
    )
    path = root / relative
    require(not path.is_symlink(), f"owned artifact is a symlink: {relative}")
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        fail(f"owned artifact is missing or cannot be resolved: {relative}: {error}")
    require(
        resolved == path.absolute() and resolved.is_file(),
        f"owned artifact escapes its frozen project path: {relative}",
    )
    try:
        return path.read_bytes()
    except OSError as error:
        fail(f"cannot read exact owned artifact {relative}: {error}")


def readelf(root: Path, option: str, binary: str) -> str:
    require(option in {"--dynamic", "--dyn-syms"}, "unapproved native inspection mode")
    require(binary in BINARY_CLOSURE, "unapproved native inspection path")
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
        fail(f"cannot inspect {binary} with pinned system readelf: {error}")
    require(
        result.returncode == 0 and not result.stderr,
        f"readelf failed for {binary}: {result.stderr.strip()}",
    )
    return result.stdout


def inspect_actual_sources(root: Path) -> dict[str, object]:
    contents = {relative: approved_bytes(root, relative) for relative in SOURCE_CLOSURE}
    binary_contents = {
        relative: approved_bytes(root, relative) for relative in BINARY_CLOSURE
    }
    try:
        texts = {path: value.decode("utf-8") for path, value in contents.items()}
    except UnicodeDecodeError as error:
        fail(f"an owned source file is not valid UTF-8: {error}")
    imports = adapter_imports(texts[ADAPTER])
    cargo = inspect_cargo(texts[MANIFEST], texts[LOCKFILE])
    bridge = inspect_bridge(texts[BRIDGE_SOURCE])
    rust = inspect_rust_sources({path: texts[path] for path in RUST_SOURCES})
    native: dict[str, object] = {}
    for binary in BINARY_CLOSURE:
        native[binary] = {
            **parse_dynamic_section(readelf(root, "--dynamic", binary), binary),
            **parse_dynamic_symbols(readelf(root, "--dyn-syms", binary), binary),
        }
    return {
        "source_sha256": {
            path: hashlib.sha256(value).hexdigest()
            for path, value in contents.items()
        },
        "native_sha256": {
            path: hashlib.sha256(value).hexdigest()
            for path, value in binary_contents.items()
        },
        "adapter_imports": list(imports),
        "cargo": cargo,
        "bridge": bridge,
        "rust": rust,
        "native": native,
    }


class ImportBlocker(importlib.abc.MetaPathFinder):
    def __init__(self, violations: list[str]) -> None:
        self.violations = violations

    def find_spec(self, fullname: str, path: object = None, target: object = None):
        if forbidden_module(fullname):
            self.violations.append(f"meta-path:{fullname}")
            fail(f"candidate attempted forbidden module import: {fullname}")
        return None


def worker_run(root: Path, expected: dict[str, object]) -> dict[str, object]:
    require(
        isinstance(expected, dict)
        and frozenset(expected) == {"source_sha256", "native_sha256"},
        "runtime worker received an incomplete or unapproved ownership manifest",
    )
    for label, paths in (("source_sha256", SOURCE_CLOSURE), ("native_sha256", BINARY_CLOSURE)):
        values = expected[label]
        require(
            isinstance(values, dict) and frozenset(values) == frozenset(paths),
            f"runtime worker has an incomplete {label} closure",
        )
        for path in paths:
            actual = hashlib.sha256(approved_bytes(root, path)).hexdigest()
            require(actual == values[path], f"owned artifact changed before guarded execution: {path}")

    old_re = sys.modules.get("re")
    old_sre = sys.modules.get("_sre")
    forbidden_identities = tuple(
        value
        for value in (
            old_re,
            old_sre,
            getattr(old_re, "Pattern", None),
            getattr(old_re, "Match", None),
        )
        if value is not None
    )
    removed = tuple(name for name in tuple(sys.modules) if forbidden_module(name))
    for name in removed:
        sys.modules.pop(name, None)

    violations: list[str] = []
    guarded_import_count = 0
    original_import = builtins.__import__
    original_import_module = importlib.import_module
    blocker = ImportBlocker(violations)

    def check_name(name: str, mechanism: str) -> None:
        if forbidden_module(name):
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
                require(isinstance(item, str), "candidate uses an invalid candidate from-list")
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
        elif event in {
            "ctypes.dlopen",
            "ctypes.dlsym",
            "os.system",
            "os.fork",
            "os.posix_spawn",
            "subprocess.Popen",
        } or event.startswith("os.exec"):
            violations.append(f"audit-event:{event}")
            fail(f"candidate attempted forbidden dynamic execution: {event}")

    sys.addaudithook(audit_hook)
    sys.meta_path.insert(0, blocker)
    builtins.__import__ = guarded_import
    importlib.import_module = guarded_import_module

    package = types.ModuleType("candidates")
    package.__package__ = "candidates"
    package.__path__ = [str(root / "candidates")]
    sys.modules["candidates"] = package

    bridge_path = root / BRIDGE_BINARY
    bridge_spec = importlib.util.spec_from_file_location(
        "candidates._rust_bridge", str(bridge_path)
    )
    require(
        bridge_spec is not None
        and isinstance(bridge_spec.loader, importlib.machinery.ExtensionFileLoader)
        and bridge_spec.origin == str(bridge_path),
        "guarded worker cannot resolve the exact owned native CPython bridge",
    )
    bridge = importlib.util.module_from_spec(bridge_spec)
    sys.modules["candidates._rust_bridge"] = bridge
    package._rust_bridge = bridge
    bridge_spec.loader.exec_module(bridge)

    adapter_path = root / ADAPTER
    candidate_spec = importlib.util.spec_from_file_location(
        "candidates.rust_candidate", str(adapter_path)
    )
    require(
        candidate_spec is not None
        and isinstance(candidate_spec.loader, importlib.machinery.SourceFileLoader)
        and candidate_spec.origin == str(adapter_path),
        "guarded worker cannot resolve the exact owned Rust Python adapter",
    )
    candidate = importlib.util.module_from_spec(candidate_spec)
    sys.modules["candidates.rust_candidate"] = candidate
    package.rust_candidate = candidate
    candidate_spec.loader.exec_module(candidate)

    require(candidate.Match is bridge.Match, "public match type is not the owned native bridge type")
    require(
        all(candidate.Pattern is not item and candidate.Match is not item for item in forbidden_identities),
        "public Rust objects reuse a captured standard-library regular-expression identity",
    )
    require(
        candidate.Pattern.__module__ == "re" and candidate.Match.__module__ == "re",
        "owned native public types do not preserve Python-compatible public names",
    )

    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        require(condition, message)
        checks += 1

    pattern = candidate.compile(r"(?P<word>[A-Za-z]+)-(\d+)")
    check(type(pattern) is candidate.Pattern, "compiled pattern is not independently owned")
    match = pattern.search("xx alpha-42 yy")
    check(type(match) is bridge.Match, "search returned an unowned native match")
    check(match.group(0, "word", 2) == ("alpha-42", "alpha", "42"), "owned named/counted capture failed")
    check(match.span("word") == (3, 8), "owned named capture span failed")
    check(match.expand(r"\g<word>:\2") == "alpha:42", "owned native replacement expansion failed")
    check(candidate.fullmatch(r"\w+", "hello_42") is not None, "owned fullmatch failed")
    check(candidate.match(r"a+", "aaab").span() == (0, 3), "owned anchored match failed")
    check(candidate.search(rb"a+", memoryview(b"--aaa--")).span() == (2, 5), "owned bytes-buffer match failed")
    check(candidate.findall(r"\d+", "a12b345") == ["12", "345"], "owned findall failed")
    check(
        [item.span() for item in candidate.finditer(r"\d+", "a12b345")]
        == [(1, 3), (4, 7)],
        "owned lazy iteration failed",
    )
    check(candidate.split(r"\s+", "a  b\tc") == ["a", "b", "c"], "owned split failed")
    callback_matches: list[object] = []

    def replacement(item):
        callback_matches.append(item)
        return item.group(0).upper()

    check(
        candidate.sub(r"[a-z]+", replacement, "ab 12 cd") == "AB 12 CD",
        "owned substitution or legitimate caller replacement callback failed",
    )
    check(
        len(callback_matches) == 2
        and all(type(item) is bridge.Match for item in callback_matches),
        "replacement callback was not given independently owned native matches",
    )
    check(
        candidate.subn(r"\d+", "#", "a12b345") == ("a#b#", 2),
        "owned counted substitution failed",
    )
    scanner = candidate.compile(r"\w+").scanner("aa bb")
    check(
        type(scanner).__module__ == "_sre"
        and type(scanner).__name__ == "SRE_Scanner",
        "independently owned scanner does not preserve the compatible scanner name",
    )
    first_scanner_match = scanner.search()
    second_scanner_match = scanner.search()
    check(
        type(first_scanner_match) is bridge.Match
        and type(second_scanner_match) is bridge.Match
        and first_scanner_match.group() == "aa"
        and second_scanner_match.group() == "bb",
        "independently owned scanner does not return Rust-native matching results",
    )
    check("_sre" not in sys.modules, "compatible owned scanner imported the real CPython engine")
    check(
        frozenset(name for name in sys.modules if name.startswith("candidates."))
        == {"candidates._rust_bridge", "candidates.rust_candidate"},
        "guarded execution imported another candidate or an unowned candidate module",
    )
    check(
        not any(forbidden_module(name) for name in sys.modules),
        "guarded execution loaded a forbidden regular-expression or foreign engine module",
    )
    check(not violations, "guarded execution recorded a forbidden import or process escape")

    return {
        "status": "PASS",
        "runtime_checks": checks,
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
    }


def run_candidate() -> dict[str, object]:
    require(
        sys.implementation.name == "cpython"
        and sys.version_info[:3] == PYTHON_VERSION
        and os.path.realpath(sys.executable) == os.path.realpath(PINNED_PYTHON),
        "actual ownership audit must run using the exact pinned CPython 3.14.6 interpreter",
    )
    root = project_root()
    before = inspect_actual_sources(root)
    worker_input = {
        "source_sha256": before["source_sha256"],
        "native_sha256": before["native_sha256"],
    }
    try:
        result = subprocess.run(
            [PINNED_PYTHON, "-I", "-B", str(root / "tools/rust_from_scratch_audit_v1.py"), "--_candidate-worker"],
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
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        fail(f"independent guarded runtime worker failed: {error}")
    require(
        result.returncode == 0 and not result.stderr,
        f"independent guarded runtime worker rejected the candidate: {result.stdout.strip()} {result.stderr.strip()}",
    )
    try:
        runtime = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        fail(f"independent guarded runtime worker produced invalid evidence: {error}")
    require(
        isinstance(runtime, dict)
        and runtime.get("status") == "PASS"
        and runtime.get("runtime_checks", 0) >= 20
        and runtime.get("forbidden_import_or_execution_count") == 0,
        "independent guarded runtime worker did not establish complete ownership checks",
    )
    after = inspect_actual_sources(root)
    require(before == after, "owned source, native symbols, dependencies, or binary changed during audit")
    return {
        "oracle": ORACLE_NAME,
        "status": "PASS",
        "python": {
            "implementation": "cpython",
            "version": list(PYTHON_VERSION),
            "executable": PINNED_PYTHON,
        },
        "candidate": "rust",
        "ownership": before,
        "runtime": runtime,
        "unchanged_before_after": True,
        "final_holdout_opened": False,
        "hidden_cases_read": False,
        "performance_measured": False,
        "winner_selected": False,
    }


def self_test() -> dict[str, object]:
    """Exercise only synthetic in-memory fixtures; never read candidate files."""
    positives = 0
    rejections = 0

    def accept(condition: bool, message: str) -> None:
        nonlocal positives
        require(condition, f"synthetic positive failed: {message}")
        positives += 1

    def reject(function, message: str) -> None:
        nonlocal rejections
        try:
            function()
        except AuditFailure:
            rejections += 1
            return
        fail(f"synthetic poison was not rejected: {message}")

    good_adapter = (
        "import enum\nimport operator\nimport os\nimport types\n"
        "import unicodedata\nimport warnings\n"
        "from candidates import _rust_bridge\n"
        "def replacement_callback(callback, match):\n"
        "    return callback(match)\n"
    )
    accept(
        len(adapter_imports(good_adapter)) == 7,
        "exact approved Python adapter and ordinary caller callback",
    )
    good_manifest = (
        '[package]\nname = "rebar-rust-continuation"\nversion = "0.1.0"\n'
        'edition = "2024"\nrust-version = "1.85"\npublish = false\n'
        '[lib]\ncrate-type = ["cdylib"]\n'
    )
    good_lock = (
        'version = 4\n[[package]]\nname = "rebar-rust-continuation"\n'
        'version = "0.1.0"\n'
    )
    accept(
        inspect_cargo(good_manifest, good_lock)["external_package_count"] == 0,
        "single owned Cargo package and no external packages",
    )
    good_bridge = (
        "#include <Python.h>\n#include <stddef.h>\n"
        "#include <stdint.h>\n#include <string.h>\n"
        'PyImport_ImportModule("copyreg");\n'
        'PyImport_ImportModule("functools");\n'
        'PyImport_ImportModule("inspect");\n'
        'RustScannerType = { .tp_name = "_sre.SRE_Scanner" };\n'
        'RustMatchType = { .tp_name = "re.Match" };\n'
        'owned_match_attribute = { "re", owned_pattern_descriptor };\n'
        'PyUnicode_CompareWithASCIIString(pattern_module, "re");\n'
        "PyObject_CallOneArg(user_replacement_callback, owned_match);\n"
    )
    bridge_result = inspect_bridge(good_bridge)
    accept(
        bridge_result["owned_compatible_scanner_names"] == 1,
        "independently owned scanner may retain its compatible _sre public name",
    )
    accept(
        bridge_result["compatibility_imports"]
        == ["copyreg", "functools", "inspect"],
        "non-regex compatibility imports remain allowed",
    )
    accept(
        len(lexical_tokens("struct Borrowed<'a> { value: &'a [u8] }")) > 8,
        "Rust borrowed lifetimes are not mistaken for unterminated characters",
    )
    accept(
        len(lexical_tokens("'execute: loop { break 'execute; }")) > 7,
        "Rust loop labels are not mistaken for unterminated characters",
    )
    escaped_character_tokens = lexical_tokens(
        "let ordinary = 'a'; let escaped = '\\\\'; use std::slice;"
    )
    accept(
        ("identifier", "use") in escaped_character_tokens,
        "escaped native character literals do not swallow subsequent executable source",
    )
    accept(
        len(lexical_tokens('// dlopen("libpcre.so")\n/* regex::Regex */\nvalue;'))
        == 2,
        "comment text does not masquerade as an actual native dependency",
    )
    good_rust = {
        RUST_SOURCES[0]: (
            "use std::slice;\nmod newline;\nmod search;\n"
            "mod stack;\nmod unicode_tables;\nuse stack::InlineStack;\n"
        ),
        RUST_SOURCES[1]: "use std::ffi::c_void;\n",
        RUST_SOURCES[2]: "use std::arch::x86_64::*;\n",
        RUST_SOURCES[3]: "use std::mem::MaybeUninit;\n",
        RUST_SOURCES[4]: "const TABLE: &[u32] = &[1, 2];\n",
    }
    accept(
        inspect_rust_sources(good_rust)["owned_modules"]
        == ["newline", "search", "stack", "unicode_tables"],
        "exact five-source Rust closure",
    )

    for name in (
        "re",
        "re._compiler",
        "re._parser",
        "_sre",
        "regex",
        "regex._regex",
        "_regex",
        "re2",
        "google_re2",
        "pcre",
        "pcre2",
        "onig",
        "oniguruma",
        "hyperscan",
        "vectorscan",
        "sre_compile",
        "sre_parse",
        "sre_constants",
        "rust_regex",
        "fancy_regex",
        "ctypes",
        "cffi",
        "subprocess",
        "runpy",
        "rebar",
        "zig",
        "python_candidate",
        "zig_candidate",
        "candidates.zig_candidate",
        "candidates.python_candidate",
        "candidates._zig_bridge",
        "candidates.rust_other",
    ):
        accept(forbidden_module(name), f"forbidden module classification: {name}")

    for name in (
        "readline",
        "resource",
        "reprlib",
        "enum",
        "operator",
        "os",
        "types",
        "unicodedata",
        "warnings",
        "copyreg",
        "functools",
        "inspect",
        "candidates",
        "candidates._rust_bridge",
        "candidates.rust_candidate",
    ):
        accept(not forbidden_module(name), f"safe module classification: {name}")

    poisoned_imports = (
        "import re\n",
        "import re as owned\n",
        "from re import compile\n",
        "import _sre\n",
        "import regex\n",
        "import re2\n",
        "import pcre2\n",
        "import ctypes\n",
        "import cffi\n",
        "import subprocess\n",
        "import importlib\n",
        "from candidates import zig_candidate\n",
        "from candidates import rust_candidate\n",
        "from . import _rust_bridge\n",
        "from candidates import _rust_bridge as borrowed\n",
        '__import__("re")\n',
        'eval("__import__(\\"re\\")")\n',
        'exec("import re")\n',
        'getattr(os, "system")("true")\n',
        'os.system("true")\n',
        'os.popen("true")\n',
        "os.fork()\n",
    )
    for poison in poisoned_imports:
        reject(
            lambda poison=poison: adapter_imports(good_adapter + poison),
            f"Python import or execution escape: {poison.strip()}",
        )

    for poison in (
        '\n[dependencies]\nregex = "1"\n',
        '\n[dev-dependencies]\nregex = "1"\n',
        '\n[build-dependencies]\nregex = "1"\n',
        '\n[target.x86_64-unknown-linux-gnu.dependencies]\nregex = "1"\n',
        '\n[workspace]\nmembers = ["borrowed-engine"]\n',
    ):
        reject(
            lambda poison=poison: inspect_cargo(good_manifest + poison, good_lock),
            "external Cargo dependency or workspace",
        )
    for bad_manifest in (
        good_manifest.replace('publish = false', 'publish = false\nbuild = "build.rs"'),
        good_manifest.replace('publish = false', 'publish = false\nlinks = "pcre2"'),
        good_manifest.replace('crate-type = ["cdylib"]', 'crate-type = ["cdylib"]\npath = "foreign.rs"'),
        good_manifest.replace('crate-type = ["cdylib"]', 'crate-type = ["proc-macro"]'),
        good_manifest.replace('name = "rebar-rust-continuation"', 'name = "borrowed-engine"'),
    ):
        reject(
            lambda bad_manifest=bad_manifest: inspect_cargo(bad_manifest, good_lock),
            "redirected Cargo build, linking, package, or source",
        )
    for bad_lock in (
        good_lock + '\n[[package]]\nname = "regex"\nversion = "1.0.0"\n',
        good_lock + '\nsource = "registry+https://example.invalid"\n',
        good_lock.replace('version = "0.1.0"', 'version = "9.9.9"'),
        good_lock.replace("version = 4", "version = 3"),
        good_lock.replace('version = "0.1.0"', 'version = "0.1.0"\ndependencies = ["regex"]'),
    ):
        reject(
            lambda bad_lock=bad_lock: inspect_cargo(good_manifest, bad_lock),
            "external or mismatched Cargo lockfile package",
        )

    for poison in (
        '#include <pcre2.h>\n',
        '#include "borrowed_engine.h"\n',
        'PyImport_ImportModule("re");\n',
        'PyImport_ImportModule("_sre");\n',
        'PyImport_ImportModule("regex");\n',
        'PyImport_ImportModule(dynamic_name);\n',
        'dlopen("libpcre2-8.so", 1);\n',
        'dlsym(handle, "pcre2_match");\n',
        'regcomp(pattern, value, 0);\n',
        'pcre2_match(pattern, value);\n',
        'onig_search(pattern, value);\n',
        'hs_scan(pattern, value);\n',
        'system("true");\n',
        'popen("true", "r");\n',
        'PyRun_SimpleString("import re");\n',
        'PyImport_Import("regex");\n',
        'const char *borrowed = "_sre.SRE_Scanner";\n',
        'const char *borrowed = "re";\n',
    ):
        reject(
            lambda poison=poison: inspect_bridge(good_bridge + poison),
            f"native C bridge delegation or dynamic loading: {poison.strip()}",
        )

    for poison in (
        "use regex::Regex;\n",
        "use pcre2::bytes::Regex;\n",
        "extern crate regex;\n",
        'include!("../../borrowed.rs");\n',
        'include_str!("../../borrowed.rs");\n',
        'include_bytes!("../../borrowed.so");\n',
        '#[link(name = "pcre2-8")]\n',
        '#[path = "../../borrowed.rs"]\n',
        'dlopen("libpcre.so");\n',
        "pcre2_match();\n",
        "onig_search();\n",
        "regexec();\n",
    ):
        def poisoned_rust(poison=poison):
            changed = dict(good_rust)
            changed[RUST_SOURCES[0]] += poison
            return inspect_rust_sources(changed)

        reject(poisoned_rust, f"Rust external-engine escape: {poison.strip()}")

    engine_dynamic = (
        "0x1 (NEEDED) Shared library: [libgcc_s.so.1]\n"
        "0x1 (NEEDED) Shared library: [libc.so.6]\n"
        "0x1 (NEEDED) Shared library: [ld-linux-x86-64.so.2]\n"
    )
    bridge_dynamic = (
        "0x1 (NEEDED) Shared library: [_rust_engine.so]\n"
        "0x1 (NEEDED) Shared library: [libc.so.6]\n"
        "0x1 (RUNPATH) Library runpath: [$ORIGIN]\n"
    )
    accept(
        len(parse_dynamic_section(engine_dynamic, ENGINE_BINARY)["needed"]) == 3,
        "owned Rust ELF system-library closure",
    )
    accept(
        parse_dynamic_section(bridge_dynamic, BRIDGE_BINARY)["runpaths"] == ["$ORIGIN"],
        "owned local native-bridge runpath",
    )
    for binary, dynamic, poison in (
        (ENGINE_BINARY, engine_dynamic, "0x1 (NEEDED) Shared library: [libpcre2-8.so]\n"),
        (ENGINE_BINARY, engine_dynamic, "0x1 (NEEDED) Shared library: [libre2.so]\n"),
        (ENGINE_BINARY, engine_dynamic, "0x1 (NEEDED) Shared library: [libonig.so]\n"),
        (ENGINE_BINARY, engine_dynamic, "0x1 (NEEDED) Shared library: [libhs.so]\n"),
        (ENGINE_BINARY, engine_dynamic, "0x1 (RUNPATH) Library runpath: [/foreign]\n"),
        (BRIDGE_BINARY, bridge_dynamic, "0x1 (NEEDED) Shared library: [libpcre.so]\n"),
        (BRIDGE_BINARY, bridge_dynamic, "0x1 (NEEDED) Shared library: [_zig_engine.so]\n"),
        (BRIDGE_BINARY, bridge_dynamic, "0x1 (RUNPATH) Library runpath: [/foreign]\n"),
    ):
        reject(
            lambda binary=binary, dynamic=dynamic, poison=poison: parse_dynamic_section(
                dynamic + poison, binary
            ),
            "external ELF dependency or library runpath",
        )

    engine_rows = [
        f"{number}: 0000000000000001 1 FUNC GLOBAL DEFAULT 15 {name}"
        for number, name in enumerate(sorted(OWNED_ENGINE_EXPORTS), start=1)
    ]
    engine_rows.append("99: 0000000000000000 0 NOTYPE GLOBAL DEFAULT UND Py_GetRecursionLimit")
    engine_symbols = "\n".join(engine_rows)
    bridge_rows = [
        "1: 0000000000000001 1 FUNC GLOBAL DEFAULT 14 PyInit__rust_bridge",
        "2: 0000000000000000 0 NOTYPE GLOBAL DEFAULT UND PyImport_ImportModule",
        "3: 0000000000000000 0 FUNC GLOBAL DEFAULT UND rebar_compile",
        "4: 0000000000000000 0 FUNC GLOBAL DEFAULT UND rebar_compile_scanner",
        "5: 0000000000000000 0 FUNC GLOBAL DEFAULT UND rebar_match",
        "6: 0000000000000000 0 FUNC GLOBAL DEFAULT UND rebar_free",
        "7: 0000000000000000 0 NOTYPE GLOBAL DEFAULT UND PyObject_CallOneArg",
    ]
    bridge_symbols = "\n".join(bridge_rows)
    accept(
        len(parse_dynamic_symbols(engine_symbols, ENGINE_BINARY)["defined_exports"])
        == len(OWNED_ENGINE_EXPORTS),
        "exact independently implemented Rust matcher ABI",
    )
    accept(
        len(parse_dynamic_symbols(bridge_symbols, BRIDGE_BINARY)["owned_engine_references"])
        == 4,
        "native bridge resolves owned matching ABI and allows caller callbacks",
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
        "zig_candidate_match",
    ):
        poison = f"199: 0000000000000000 0 FUNC GLOBAL DEFAULT UND {symbol}"
        reject(
            lambda poison=poison: parse_dynamic_symbols(
                engine_symbols + "\n" + poison, ENGINE_BINARY
            ),
            f"external ELF matching or execution symbol: {symbol}",
        )
    reject(
        lambda: parse_dynamic_symbols(
            bridge_symbols + "\n99: 0000000000000001 1 FUNC GLOBAL DEFAULT 14 PyInit__zig_bridge",
            BRIDGE_BINARY,
        ),
        "bridge exports another candidate's entry point",
    )

    require(rejections >= 70, "synthetic delegation-poison control count is incomplete")
    require(positives >= 50, "synthetic safe ownership control count is incomplete")
    return {
        "oracle": ORACLE_NAME,
        "status": "PASS",
        "self_test_only": True,
        "synthetic_positive_controls": positives,
        "synthetic_rejection_controls": rejections,
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
    group.add_argument("--candidate", action="store_true")
    group.add_argument("--_candidate-worker", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    try:
        if arguments.self_test:
            result = self_test()
        elif arguments.candidate:
            result = run_candidate()
        else:
            try:
                expected = json.load(sys.stdin)
            except (json.JSONDecodeError, ValueError, TypeError) as error:
                fail(f"runtime worker received invalid ownership evidence: {error}")
            result = worker_run(project_root(), expected)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except (AuditFailure, OSError, ValueError, TypeError) as error:
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
