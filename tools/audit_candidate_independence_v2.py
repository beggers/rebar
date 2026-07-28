#!/usr/bin/env python3
"""Fail-closed, source-only independence audit for six owned regex engines."""

from __future__ import annotations

import argparse
import ast
import builtins
import ctypes
import hashlib
import io
import json
import os
import socket
import stat
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


SCHEMA = "rebar-phase2-six-candidate-independence-static-audit-v2"
SELF_TEST_SCHEMA = "rebar-phase2-six-candidate-independence-source-self-test-v2"
PINNED_PYTHON = (3, 14, 6)
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MAX_SOURCE_BYTES = 32 * 1024 * 1024
HEX_DIGITS = frozenset("0123456789abcdef")
FIXED_CONTEXT = {
    "GOAL.md": GOAL_SHA256,
    "pyproject.toml":
        "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
    "uv.lock":
        "1f8402bb3fdda2c1ba57b5cfdcb1f8b835a4528784d553fe1219ca157f0750f2",
    "tools/audit_candidate_independence_v1.py":
        "f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5",
    "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md":
        "a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292",
    "oracle/phase1/p0-completeness-v1.json":
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    "oracle/phase1/P0-COMPLETENESS-V1.md":
        "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
    "tools/verify_p0_completeness_v1.py":
        "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
    "docs/evidence/candidate-current-overview-v7.inputs.json":
        "744f86e241e3489cf07c5fccccf291eb68c44a50605d79723dd1ae1092d8511f",
    "docs/evidence/candidate-current-overview-v7.json":
        "50aafe8c56c21dc95fca2f7ddaead623ef5cf7151db9f28e6c47de7630764f3b",
    "tools/render_candidate_current_overview_v7.py":
        "1f5a5baa82ecb0fd5de53094f1c97ae33c5ac2b71d91c920849c92f5e92217cf",
    "oracle/phase2/p0-candidate-protocol-v5.json":
        "f0ae8a783a3091cb2f59fdb7f82cb012fe34eceffbead347ff3ee2e11ec1724b",
    "oracle/phase2/P0-CANDIDATE-PROTOCOL-V5.md":
        "a943eb9d8d9dbc8ca13562c274b9a96b340ddc531423d6669a00d2aeba65ead8",
    "tools/run_frozen_p0_candidate_v5.py":
        "5dfdd52069379f4410a9620f95914717e0a9d278fdfc9f1d7416f3aa36ec6326",
    "tools/run_frozen_p0_candidate_worker_v3.py":
        "3364ee6d2168803751a2a8c06533828fe9762bb5ad323e8f798bc346a4a2f475",
}


class AuditError(Exception):
    """An owner, provenance, dependency, or side-effect check failed."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise AuditError(message)


@dataclass(frozen=True)
class Owner:
    path: str
    kind: str
    role: str


@dataclass(frozen=True)
class Family:
    name: str
    graph_name: str
    bridge: str
    owners: tuple[Owner, ...]


FAMILIES = (
    Family("c_vm", "c", "_vm_native", (
        Owner("candidates/vm_candidate.py", "python", "owned parser and compiler"),
        Owner("candidates/_vm_native.c", "c", "owned virtual machine and bridge"),
    )),
    Family("rust", "rust", "_rust_bridge", (
        Owner("candidates/rust_candidate.py", "python", "owned public adapter"),
        Owner("candidates/rust/py_bridge.c", "c", "owned Python C bridge"),
        Owner("candidates/rust/src/lib.rs", "rust", "owned parser, compiler and executor"),
        Owner("candidates/rust/src/newline.rs", "rust", "owned newline operations"),
        Owner("candidates/rust/src/search.rs", "rust", "owned search operations"),
        Owner("candidates/rust/src/stack.rs", "rust", "owned executor stack"),
        Owner("candidates/rust/src/unicode_tables.rs", "rust", "owned Unicode data"),
        Owner("candidates/rust/Cargo.toml", "cargo_manifest", "first-party dependency manifest"),
        Owner("candidates/rust/Cargo.lock", "cargo_lock", "first-party dependency lock"),
    )),
    Family("zig", "zig", "_zig_bridge", (
        Owner("candidates/zig_candidate.py", "python", "owned public adapter and anchored native loader"),
        Owner("candidates/zig/mini_regex.zig", "zig", "owned parser, compiler and executor"),
        Owner("candidates/zig/py_bridge.c", "c", "owned Python C bridge"),
    )),
    Family("cpp", "cpp", "_cpp_bridge", (
        Owner("candidates/cpp_candidate.py", "python", "owned public adapter"),
        Owner("candidates/cpp/engine.hpp", "cpp", "owned engine declarations"),
        Owner("candidates/cpp/engine.cpp", "cpp", "owned parser, compiler and executor"),
        Owner("candidates/cpp/py_bridge.cpp", "cpp", "owned Python C bridge"),
    )),
    Family("go", "go", "_go_bridge", (
        Owner("candidates/go_candidate.py", "python", "owned public adapter"),
        Owner("candidates/go/engine.go", "go", "owned parser, compiler and executor"),
        Owner("candidates/go/py_bridge.c", "c", "owned Python C bridge"),
        Owner("candidates/go/go.mod", "go_mod", "first-party Go module"),
    )),
    Family("fortran", "fortran", "_fortran_bridge", (
        Owner("candidates/fortran_candidate.py", "python", "owned public adapter"),
        Owner("candidates/fortran/engine.f90", "fortran", "owned parser, compiler and executor"),
        Owner("candidates/fortran/py_bridge.c", "c", "owned Python C bridge"),
    )),
)
FAMILY_BY_NAME = {family.name: family for family in FAMILIES}
FORBIDDEN_ROOTS = frozenset({
    "_sre", "ahocorasick", "hyperscan", "onig", "oniguruma", "pcre",
    "pcre2", "pyre2", "re", "re2", "regex", "regex_automata",
    "regex_lite", "regex_syntax", "regexp", "rure", "sre_compile",
    "sre_constants", "sre_parse",
})
ALLOWED_PYTHON_ROOTS = frozenset({
    "__future__", "copyreg", "ctypes", "enum", "operator", "os",
    "struct", "sys", "types", "unicodedata", "warnings",
})
FORBIDDEN_ATTRIBUTES = frozenset({
    "__builtins__", "__code__", "__getattribute__", "__globals__",
    "__loader__", "__spec__", "__subclasses__", "cr_frame", "f_builtins",
    "f_globals", "func_globals", "gi_frame", "tb_frame",
})
FORBIDDEN_CALLS = frozenset({
    "__import__", "eval", "exec", "globals", "locals", "vars",
    "import_module", "module_from_spec", "spec_from_file_location",
    "SourceFileLoader", "dlopen", "dlsym", "PyDLL", "WinDLL", "OleDLL",
    "LoadLibrary", "CFUNCTYPE", "Popen", "system", "popen", "posix_spawn",
})
FORBIDDEN_NATIVE = frozenset({
    "GetProcAddress", "LoadLibrary", "LoadLibraryA", "LoadLibraryW",
    "PyImport_AddModule", "PyImport_ExecCodeModule", "PyImport_GetModule",
    "PyImport_GetModuleDict", "PyImport_Import", "PyImport_ImportModuleLevel",
    "PyImport_ImportModuleLevelObject", "PyRun_AnyFile", "PyRun_SimpleString",
    "PyRun_String", "PyRun_StringFlags", "PyEval_EvalCode", "Py_CompileString",
    "Py_CompileStringExFlags", "dlmopen", "dlopen", "dlsym", "execve",
    "onig_new", "onig_search", "pcre2_compile", "pcre2_match", "pcre_compile",
    "pcre_exec", "popen", "regcomp", "regexec", "system",
})
ALLOWED_HEADERS = frozenset({
    "Python.h", "algorithm", "array", "cctype", "cstddef", "cstdint",
    "ctype.h", "exception", "limits", "limits.h", "memory", "new",
    "optional", "stdexcept", "stddef.h", "stdint.h", "stdlib.h", "string",
    "string.h", "string_view", "unordered_map", "utility", "vector",
})
ALLOWED_GO_IMPORTS = frozenset({
    "C", "fmt", "runtime/cgo", "strconv", "sync", "sync/atomic", "unsafe",
})
ALLOWED_GO_EXPORTS = frozenset({
    "rebar_go_compile", "rebar_go_release", "rebar_go_group_count",
    "rebar_go_flags", "rebar_go_name_count", "rebar_go_name_group",
    "rebar_go_name_length", "rebar_go_copy_name", "rebar_go_execute",
})
ALLOWED_FORTRAN_BINDINGS = frozenset({
    "rebar_fortran_unicode_case_key", "rebar_fortran_locale_case_key",
    "rebar_fortran_locale_is_word", "rebar_fortran_compile",
    "rebar_fortran_destroy", "rebar_fortran_group_count",
    "rebar_fortran_effective_flags", "rebar_fortran_name_count",
    "rebar_fortran_name_length", "rebar_fortran_name_group",
    "rebar_fortran_copy_name", "rebar_fortran_execute",
})
FORBIDDEN_NATIVE_PREFIXES = (
    "pcre", "onig", "re2_", "hs_", "hyperscan", "rure_", "tre_",
)
ALLOWED_RUST_SUPPORT = frozenset({"copyreg", "functools", "inspect"})


def valid_sha256(value: object, label: str) -> str:
    require(isinstance(value, str) and len(value) == 64 and
            all(character in HEX_DIGITS for character in value),
            f"{label}: expected an exact lowercase SHA-256")
    return value


def checked_relative(value: object, *, allow_evidence: bool = False) -> tuple[str, ...]:
    require(isinstance(value, str) and bool(value), "owner path is missing")
    require("\x00" not in value and "\\" not in value, "unsafe path encoding")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value, "noncanonical owner path")
    require(all(item not in {"", ".", "..", ".git"} for item in path.parts),
            "owner traversal or Git metadata")
    for item in path.parts:
        folded = item.casefold()
        require("holdout" not in folded and "benchmark" not in folded and
                "performance" not in folded and folded != "perf",
                "hidden, benchmark, or performance path")
        if not allow_evidence:
            require(folded != "evidence" or value.startswith("docs/evidence/"),
                    "unapproved evidence path")
    return path.parts


def _signature(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns


def read_owned_file(root: Path, relative: str, *, evidence: bool = False) -> tuple[bytes, str]:
    parts = checked_relative(relative, allow_evidence=evidence)
    descriptors: list[int] = []
    try:
        directory = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
        descriptors.append(os.open(os.fspath(root), directory))
        for part in parts[:-1]:
            descriptors.append(os.open(part, directory, dir_fd=descriptors[-1]))
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=descriptors[-1])
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= MAX_SOURCE_BYTES,
                f"{relative}: unsafe source size or type")
        result = bytearray()
        remaining = before.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(piece), f"{relative}: source changed during read")
            result.extend(piece)
            remaining -= len(piece)
        require(not os.read(descriptor, 1), f"{relative}: source grew during read")
        require(_signature(before) == _signature(os.fstat(descriptor)),
                f"{relative}: source changed during read")
        data = bytes(result)
        return data, hashlib.sha256(data).hexdigest()
    except (OSError, ValueError) as error:
        raise AuditError(f"{relative}: safe source read failed: {error}") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def decode_source(data: bytes, path: str) -> str:
    require(b"\x00" not in data, f"{path}: NUL in source")
    try:
        return data.decode("utf-8", "strict")
    except UnicodeError as error:
        raise AuditError(f"{path}: source is not strict UTF-8") from error


def constant_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        first, second = constant_string(node.left), constant_string(node.right)
        return first + second if first is not None and second is not None else None
    if isinstance(node, ast.JoinedStr):
        parts = [constant_string(value) for value in node.values]
        return "".join(parts) if all(value is not None for value in parts) else None
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and
            node.func.id == "chr" and len(node.args) == 1 and not node.keywords and
            isinstance(node.args[0], ast.Constant) and
            isinstance(node.args[0].value, int) and 0 <= node.args[0].value <= 0x10FFFF):
        return chr(node.args[0].value)
    return None


def attribute_chain(node: ast.AST) -> tuple[str, ...] | None:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        parent = attribute_chain(node.value)
        return (*parent, node.attr) if parent is not None else None
    return None


class PythonOwnershipVisitor(ast.NodeVisitor):
    def __init__(self, family: Family, path: str) -> None:
        self.family = family
        self.path = path
        self.imports: set[str] = set()
        self.aliases: dict[str, str] = {}
        self.owned_bridges: set[str] = set()
        self.zig_loaders = 0
        self.zig_anchor = False
        self.top_level_names: set[str] = set()

    def reject(self, node: ast.AST, reason: str) -> None:
        raise AuditError(f"{self.path}:{getattr(node, 'lineno', '?')}: {reason}")

    def chain(self, node: ast.AST) -> tuple[str, ...] | None:
        value = attribute_chain(node)
        if value is None:
            return None
        root = self.aliases.get(value[0], value[0])
        return (*root.split("."), *value[1:])

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            root = item.name.split(".", 1)[0]
            if root in FORBIDDEN_ROOTS or root not in ALLOWED_PYTHON_ROOTS:
                self.reject(node, f"unowned or dynamic Python import {item.name!r}")
            if root == "ctypes" and self.family.name != "zig":
                self.reject(node, "native loader outside the owned Zig adapter")
            if root == "ctypes" and item.asname is not None:
                self.reject(node, "aliased native loader")
            local = item.asname or root
            if local in self.aliases and self.aliases[local] != item.name:
                self.reject(node, "shadowed sensitive import")
            self.aliases[local] = item.name
            self.imports.add(item.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            self.reject(node, "relative or ambiguous candidate import")
        module = node.module or ""
        root = module.split(".", 1)[0]
        if module == "candidates":
            for item in node.names:
                if item.name != self.family.bridge or item.asname is not None:
                    self.reject(node, f"cross-family or aliased bridge {item.name!r}")
                self.owned_bridges.add(item.name)
                self.aliases[item.name] = f"candidates.{item.name}"
            return
        if root in FORBIDDEN_ROOTS or root not in ALLOWED_PYTHON_ROOTS:
            self.reject(node, f"unowned or dynamic Python import {module!r}")
        if root in {"ctypes", "os", "sys", "unicodedata"}:
            self.reject(node, f"computed or direct sensitive import from {module!r}")
        for item in node.names:
            if item.name == "*":
                self.reject(node, "unbounded star import")
            self.aliases[item.asname or item.name] = f"{module}.{item.name}"
        self.imports.add(module)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name.casefold() in {"fallback", "benchmark", "holdout", "pytest"}:
            self.reject(node, "fallback or benchmark-specific execution")
        self.top_level_names.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.reject(node, "asynchronous candidate dispatch")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        chain = self.chain(node)
        if node.attr in FORBIDDEN_ATTRIBUTES:
            self.reject(node, f"computed module escape {node.attr!r}")
        if chain and chain[0] == "sys" and chain != ("sys", "maxsize"):
            self.reject(node, f"unapproved Python system access {'.'.join(chain)!r}")
        if chain and chain[0] == "os":
            allowed = {("os", "path"), ("os", "path", "join"),
                       ("os", "path", "dirname")}
            if chain not in allowed:
                self.reject(node, f"environment or process dispatch {'.'.join(chain)!r}")
        if chain and chain[0] == "ctypes":
            approved = {"CDLL", "c_bool", "c_char", "c_char_p", "c_int",
                        "c_int32", "c_int64", "c_size_t", "c_ssize_t",
                        "c_uint", "c_uint32", "c_uint64", "c_void_p"}
            if self.family.name != "zig" or len(chain) != 2 or chain[1] not in approved:
                self.reject(node, f"unowned native loader {'.'.join(chain)!r}")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        chain = self.chain(node.value)
        key = constant_string(node.slice)
        if (chain and (chain[0] in {"sys", "os"} or
                       chain[-1] in {"__dict__", "__builtins__", "modules"})):
            self.reject(node, "environment, module-table, or dictionary escape")
        if key in FORBIDDEN_ATTRIBUTES or key in {"__import__", "eval", "exec"}:
            self.reject(node, f"dynamic lookup {key!r}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        chain = self.chain(node.func)
        if chain and chain[-1] in FORBIDDEN_CALLS:
            self.reject(node, f"dynamic import, process, or native call {'.'.join(chain)!r}")
        if chain == ("getattr",) and len(node.args) >= 2:
            target = constant_string(node.args[1])
            receiver = self.chain(node.args[0])
            if (target is None or target in FORBIDDEN_ATTRIBUTES or
                    target in FORBIDDEN_CALLS or
                    (receiver and receiver[0] in {"sys", "os", "ctypes"})):
                self.reject(node, "computed sensitive attribute dispatch")
        if chain == ("ctypes", "CDLL"):
            if (self.family.name != "zig" or len(node.args) != 1 or node.keywords or
                    not isinstance(node.args[0], ast.Name) or node.args[0].id != "path"):
                self.reject(node, "native loader is not the owned file-anchored Zig engine")
            self.zig_loaders += 1
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if any(isinstance(target, ast.Name) and target.id == "path"
               for target in node.targets):
            call = node.value
            if (isinstance(call, ast.Call) and self.chain(call.func) == ("os", "path", "join")
                    and len(call.args) == 2 and not call.keywords
                    and isinstance(call.args[0], ast.Call)
                    and self.chain(call.args[0].func) == ("os", "path", "dirname")
                    and len(call.args[0].args) == 1
                    and isinstance(call.args[0].args[0], ast.Name)
                    and call.args[0].args[0].id == "__file__"
                    and constant_string(call.args[1]) == "_zig_probe.so"):
                if self.zig_anchor:
                    self.reject(node, "reassigned Zig library path")
                self.zig_anchor = True
        self.generic_visit(node)


def inspect_python(source: str, family: Family, path: str) -> dict[str, object]:
    try:
        tree = ast.parse(source, filename=path)
    except (SyntaxError, TypeError, ValueError, RecursionError) as error:
        raise AuditError(f"{path}: invalid Python syntax: {error}") from error
    visitor = PythonOwnershipVisitor(family, path)
    visitor.visit(tree)
    require(visitor.owned_bridges == {family.bridge},
            f"{path}: required exact owned bridge {family.bridge!r}")
    if family.name == "zig":
        require(visitor.zig_loaders == 1 and visitor.zig_anchor,
                f"{path}: exactly one file-anchored Zig loader is required")
    else:
        require(visitor.zig_loaders == 0, f"{path}: unowned native loader")
    return {"python_imports": sorted(visitor.imports),
            "owned_bridge": family.bridge,
            "owned_anchored_native_loaders": visitor.zig_loaders,
            "parsed_not_imported": True}


@dataclass(frozen=True)
class NativeToken:
    kind: str
    value: str
    line: int


def native_tokens(source: str, path: str, language: str) -> list[NativeToken]:
    tokens: list[NativeToken] = []
    offset, line, size = 0, 1, len(source)
    while offset < size:
        value = source[offset]
        if value.isspace():
            line += value == "\n"
            offset += 1
            continue
        if language == "fortran" and value == "!":
            end = source.find("\n", offset + 1)
            offset = size if end < 0 else end
            continue
        if language != "fortran" and source.startswith("//", offset):
            end = source.find("\n", offset + 2)
            offset = size if end < 0 else end
            continue
        if language != "fortran" and source.startswith("/*", offset):
            start_line, depth = line, 1
            offset += 2
            while offset < size and depth:
                if source.startswith("/*", offset):
                    depth += 1
                    offset += 2
                elif source.startswith("*/", offset):
                    depth -= 1
                    offset += 2
                else:
                    line += source[offset] == "\n"
                    offset += 1
            require(depth == 0, f"{path}:{start_line}: unterminated native comment")
            continue
        if language == "go" and value == "`":
            end = source.find("`", offset + 1)
            require(end >= 0, f"{path}:{line}: unterminated Go raw string")
            content = source[offset + 1:end]
            tokens.append(NativeToken("string", content, line))
            line += content.count("\n")
            offset = end + 1
            continue
        if language == "cpp" and source.startswith('R"', offset):
            opening = source.find("(", offset + 2)
            require(opening >= 0, f"{path}:{line}: invalid C++ raw string")
            marker = source[offset + 2:opening]
            require(len(marker) <= 16 and all(ch not in " ()\\\t\n" for ch in marker),
                    f"{path}:{line}: invalid C++ raw string delimiter")
            terminator = ")" + marker + '"'
            end = source.find(terminator, opening + 1)
            require(end >= 0, f"{path}:{line}: unterminated C++ raw string")
            content = source[opening + 1:end]
            tokens.append(NativeToken("string", content, line))
            line += content.count("\n")
            offset = end + len(terminator)
            continue
        raw: tuple[int, int] | None = None
        if language == "rust":
            for prefix in ("br", "rb", "r"):
                if source.startswith(prefix, offset):
                    marker = offset + len(prefix)
                    while marker < size and source[marker] == "#":
                        marker += 1
                    if marker < size and source[marker] == '"':
                        raw = marker, marker - offset - len(prefix)
                        break
        if raw is not None:
            opening, count = raw
            terminator = '"' + "#" * count
            end = source.find(terminator, opening + 1)
            require(end >= 0, f"{path}:{line}: unterminated Rust raw string")
            content = source[opening + 1:end]
            tokens.append(NativeToken("string", content, line))
            line += content.count("\n")
            offset = end + len(terminator)
            continue
        if value in {'"', "'"}:
            if (language == "rust" and value == "'" and offset + 1 < size and
                    (source[offset + 1].isalpha() or source[offset + 1] == "_") and
                    (offset + 2 >= size or source[offset + 2] != "'")):
                tokens.append(NativeToken("punctuation", value, line))
                offset += 1
                continue
            opening, start_line, quote = offset, line, value
            offset += 1
            while offset < size:
                current = source[offset]
                if language == "fortran" and current == quote and source.startswith(quote * 2, offset):
                    offset += 2
                elif current == "\\" and language != "fortran":
                    require(offset + 1 < size, f"{path}:{start_line}: unterminated escape")
                    line += source[offset + 1] == "\n"
                    offset += 2
                elif current == quote:
                    offset += 1
                    break
                else:
                    require(current != "\n", f"{path}:{start_line}: unterminated native string")
                    offset += 1
            else:
                raise AuditError(f"{path}:{start_line}: unterminated native string")
            spelling = source[opening:offset]
            if language == "fortran":
                decoded = spelling[1:-1].replace(quote * 2, quote)
            else:
                try:
                    decoded = ast.literal_eval(spelling)
                except (SyntaxError, TypeError, ValueError) as error:
                    raise AuditError(f"{path}:{start_line}: invalid native string") from error
            require(isinstance(decoded, str), f"{path}:{start_line}: non-text native string")
            tokens.append(NativeToken("string", decoded, start_line))
            continue
        if value.isalpha() or value == "_":
            end = offset + 1
            while end < size and (source[end].isalnum() or source[end] == "_"):
                end += 1
            tokens.append(NativeToken("identifier", source[offset:end], line))
            offset = end
            continue
        tokens.append(NativeToken("punctuation", value, line))
        offset += 1
    return tokens


def inspect_go_preamble(source: str, path: str) -> dict[str, object]:
    offset, size = 0, len(source)
    preambles = 0
    exports: set[str] = set()
    required_headers = ("#include <stddef.h>", "#include <stdint.h>",
                        "#include <stdlib.h>")
    while offset < size:
        if source.startswith("//", offset):
            end = source.find("\n", offset + 2)
            end = size if end < 0 else end
            comment = source[offset + 2:end].strip()
            require(not comment.startswith("go:") and "#cgo" not in comment,
                    f"{path}: unowned active Go directive or cgo linker configuration")
            if comment.startswith("export"):
                parts = comment.split()
                require(len(parts) == 2 and parts[0] == "export" and
                        parts[1] in ALLOWED_GO_EXPORTS and parts[1] not in exports,
                        f"{path}: foreign or duplicated cgo export")
                exports.add(parts[1])
            offset = end
            continue
        if source.startswith("/*", offset):
            end = source.find("*/", offset + 2)
            require(end >= 0, f"{path}: unterminated Go cgo preamble")
            following = source[end + 2:].lstrip()
            if (following.startswith("import") and
                    len(following) > 6 and following[6].isspace() and
                    following[6:].lstrip().startswith('"C"')):
                content = source[offset + 2:end]
                lines = tuple(line.strip() for line in content.splitlines()
                              if line.strip())
                require(lines == required_headers,
                        f"{path}: cgo preamble contains foreign headers, linker flags, or C code")
                preambles += 1
            offset = end + 2
            continue
        if source[offset] == "`":
            end = source.find("`", offset + 1)
            require(end >= 0, f"{path}: unterminated Go raw string")
            offset = end + 1
            continue
        if source[offset] in {'"', "'"}:
            quote = source[offset]
            offset += 1
            while offset < size and source[offset] != quote:
                require(source[offset] != "\n", f"{path}: unterminated Go literal")
                if source[offset] == "\\":
                    offset += 1
                    require(offset < size, f"{path}: unterminated Go escape")
                offset += 1
            require(offset < size, f"{path}: unterminated Go literal")
            offset += 1
            continue
        offset += 1
    require(preambles == 1, f"{path}: exactly one owned, header-only cgo preamble is required")
    if path == "candidates/go/engine.go":
        require(exports == ALLOWED_GO_EXPORTS,
                f"{path}: Go native exports are missing, foreign, or incomplete")
    return {"owned_cgo_preamble_count": 1,
            "owned_cgo_preamble_headers": list(required_headers),
            "owned_cgo_exports": sorted(exports),
            "external_cgo_linker_directive_count": 0}


def inspect_native(source: str, family: Family, path: str, kind: str) -> dict[str, object]:
    tokens = native_tokens(source, path, kind)
    identifiers = {item.value for item in tokens if item.kind == "identifier"}
    blocked = sorted((identifiers & FORBIDDEN_NATIVE) | {
        value for value in identifiers
        if value == "RE2" or value.casefold().startswith(FORBIDDEN_NATIVE_PREFIXES)
    })
    require(not blocked, f"{path}: forbidden native engine or dispatch {blocked!r}")
    imports: list[str] = []
    headers: list[str] = []
    zig_imports: list[str] = []
    go_imports: list[str] = []
    fortran_bindings: list[str] = []
    prefixes = {"zig": "rebar_zig_", "cpp": "rebar_cpp_", "go": "rebar_go_",
                "fortran": "rebar_fortran_"}
    for other, prefix in prefixes.items():
        if family.name != other:
            conflict = sorted(value for value in identifiers if value.startswith(prefix))
            require(not conflict, f"{path}: cross-family native symbols {conflict!r}")
    if family.name not in {"rust", "c_vm"}:
        require(not ({"rebar_compile", "rebar_match", "rebar_collect"} & identifiers),
                f"{path}: cross-family Rust engine symbols")
    for index, token in enumerate(tokens):
        if token.kind != "identifier":
            continue
        if (token.value in {"regex", "basic_regex", "wregex", "cmatch", "smatch"}
                and index >= 3 and tokens[index - 1].value == ":" and
                tokens[index - 2].value == ":" and
                tokens[index - 3].value in {"std", "boost", "experimental"}):
            raise AuditError(f"{path}:{token.line}: foreign C++ regular-expression engine")
        if token.value == "PyImport_ImportModule":
            require(index + 2 < len(tokens) and tokens[index + 1].value == "(" and
                    tokens[index + 2].kind == "string",
                    f"{path}:{token.line}: computed Python C import")
            cursor, pieces = index + 2, []
            while cursor < len(tokens) and tokens[cursor].kind == "string":
                pieces.append(tokens[cursor].value)
                cursor += 1
            require(cursor < len(tokens) and tokens[cursor].value == ")",
                    f"{path}:{token.line}: indirect Python C import")
            module = "".join(pieces)
            if family.name == "rust":
                require(path == "candidates/rust/py_bridge.c" and module in ALLOWED_RUST_SUPPORT,
                        f"{path}:{token.line}: unowned Rust support module {module!r}")
            elif family.name in {"cpp", "go"}:
                require(path == f"candidates/{family.name}/py_bridge." +
                        ("cpp" if family.name == "cpp" else "c") and module == "unicodedata",
                        f"{path}:{token.line}: unowned Unicode support module {module!r}")
            else:
                raise AuditError(f"{path}:{token.line}: unowned Python C import {module!r}")
            imports.append(module)
        if token.value == "include" and index and tokens[index - 1].value == "#":
            require(index + 1 < len(tokens), f"{path}:{token.line}: missing include")
            cursor = index + 1
            if tokens[cursor].kind == "string":
                header = tokens[cursor].value
                require(family.name == "cpp" and header == "engine.hpp",
                        f"{path}:{token.line}: unowned quoted source include {header!r}")
            else:
                require(tokens[cursor].value == "<", f"{path}:{token.line}: computed source include")
                cursor += 1
                parts: list[str] = []
                while cursor < len(tokens) and tokens[cursor].value != ">":
                    parts.append(tokens[cursor].value)
                    cursor += 1
                require(cursor < len(tokens), f"{path}:{token.line}: unterminated system header")
                header = "".join(parts)
                require(header in ALLOWED_HEADERS,
                        f"{path}:{token.line}: external native header {header!r}")
            headers.append(header)
        if token.value == "import" and index and tokens[index - 1].value == "@":
            require(kind == "zig" and index + 3 < len(tokens) and
                    tokens[index + 1].value == "(" and tokens[index + 2].kind == "string" and
                    tokens[index + 3].value == ")", f"{path}:{token.line}: computed Zig package")
            require(tokens[index + 2].value == "std",
                    f"{path}:{token.line}: external Zig dependency")
            zig_imports.append("std")
        if token.value in {"cImport", "cInclude", "DynLib", "embedFile"}:
            raise AuditError(f"{path}:{token.line}: external native source or loader")
        if kind == "go" and token.value == "import":
            require(index + 1 < len(tokens), f"{path}:{token.line}: missing Go import")
            cursor = index + 1
            if tokens[cursor].kind == "string":
                values = [tokens[cursor].value]
            else:
                require(tokens[cursor].value == "(", f"{path}:{token.line}: computed Go import")
                cursor += 1
                values = []
                while cursor < len(tokens) and tokens[cursor].value != ")":
                    require(tokens[cursor].kind == "string",
                            f"{path}:{token.line}: aliased or dynamic Go dependency")
                    values.append(tokens[cursor].value)
                    cursor += 1
                require(cursor < len(tokens), f"{path}:{token.line}: unterminated Go imports")
            for module in values:
                require(module in ALLOWED_GO_IMPORTS, f"{path}: external Go import {module!r}")
            go_imports.extend(values)
        if kind == "fortran" and token.value.casefold() == "use":
            cursor = index + 1
            while cursor < len(tokens) and tokens[cursor].value in {",", "intrinsic", ":"}:
                cursor += 1
            require(cursor < len(tokens) and tokens[cursor].value.casefold() == "iso_c_binding",
                    f"{path}:{token.line}: external Fortran module")
        if kind == "fortran" and token.value.casefold() == "include":
            raise AuditError(f"{path}:{token.line}: external Fortran source include")
        if kind == "fortran" and token.value.casefold() == "bind":
            require(index + 7 < len(tokens) and tokens[index + 1].value == "(" and
                    tokens[index + 2].value.casefold() == "c" and
                    tokens[index + 3].value == "," and
                    tokens[index + 4].value.casefold() == "name" and
                    tokens[index + 5].value == "=" and
                    tokens[index + 6].kind == "string" and
                    tokens[index + 7].value == ")" and
                    tokens[index + 6].value in ALLOWED_FORTRAN_BINDINGS,
                    f"{path}:{token.line}: foreign, computed, or unowned Fortran C binding")
            fortran_bindings.append(tokens[index + 6].value)
    if kind == "zig":
        require(zig_imports == ["std"], f"{path}: exact Zig standard library is required")
    if kind == "go":
        require(set(go_imports) == ALLOWED_GO_IMPORTS and
                len(go_imports) == len(ALLOWED_GO_IMPORTS),
                f"{path}: missing or extra owned Go standard imports")
    if kind == "fortran" and path == "candidates/fortran/engine.f90":
        require(set(fortran_bindings) == ALLOWED_FORTRAN_BINDINGS and
                len(fortran_bindings) == len(ALLOWED_FORTRAN_BINDINGS),
                f"{path}: Fortran native imports or owned exports were substituted")
    result = {"identifiers": identifiers, "system_headers": sorted(set(headers)),
            "literal_native_support_imports": sorted(set(imports)),
            "zig_standard_imports": zig_imports,
            "go_standard_imports": sorted(set(go_imports)),
            "fortran_owned_c_bindings": sorted(fortran_bindings),
            "compatibility_display_names": sorted({item.value for item in tokens
                                                    if item.kind == "string" and
                                                    item.value == "_sre.SRE_Scanner"})}
    if kind == "go":
        result.update(inspect_go_preamble(source, path))
    return result


def reject_dependency_sections(value: object, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            require(isinstance(key, str), f"{label}: invalid metadata key")
            folded = key.casefold()
            require(not folded.endswith("dependencies") and
                    folded not in {"patch", "replace", "workspace"},
                    f"{label}: external dependency section {key!r}")
            reject_dependency_sections(item, label)
    elif isinstance(value, list):
        for item in value:
            reject_dependency_sections(item, label)


def inspect_cargo(manifest: str, lock: str) -> dict[str, object]:
    try:
        package, locked = tomllib.loads(manifest), tomllib.loads(lock)
    except (tomllib.TOMLDecodeError, ValueError, RecursionError) as error:
        raise AuditError(f"Rust metadata is not valid TOML: {error}") from error
    reject_dependency_sections(package, "candidates/rust/Cargo.toml")
    info = package.get("package")
    require(isinstance(info, dict) and info.get("name") == "rebar-rust-continuation"
            and info.get("version") == "0.1.0" and info.get("publish") is False,
            "Rust manifest must name one unpublished first-party engine")
    require(isinstance(package.get("lib"), dict) and
            package["lib"].get("crate-type") == ["cdylib"],
            "Rust manifest must own its native engine")
    packages = locked.get("package")
    require(locked.get("version") == 4 and set(locked) == {"version", "package"}
            and isinstance(packages, list) and len(packages) == 1,
            "Rust lock must contain exactly one first-party package")
    require(packages[0] == {"name": "rebar-rust-continuation", "version": "0.1.0"},
            "Rust lock contains a registry or external package")
    return {"package": "rebar-rust-continuation", "package_count": 1,
            "external_dependency_count": 0}


def inspect_project(manifest: str, lock: str) -> dict[str, object]:
    try:
        project_file, locked = tomllib.loads(manifest), tomllib.loads(lock)
    except (tomllib.TOMLDecodeError, ValueError, RecursionError) as error:
        raise AuditError(f"Python project metadata is not valid TOML: {error}") from error
    require(set(project_file) == {"project", "tool"},
            "Python project contains an external workspace or unowned configuration")
    project = project_file.get("project")
    require(isinstance(project, dict) and
            set(project) == {"name", "version", "description", "requires-python",
                             "dependencies"} and
            project.get("name") == "rebar-experiment" and
            project.get("version") == "0.0.0" and
            project.get("requires-python") == ">=3.14,<3.15" and
            project.get("dependencies") == [],
            "Python project must contain exactly one first-party package and no dependencies")
    tools = project_file.get("tool")
    require(isinstance(tools, dict) and set(tools) == {"uv"} and
            tools.get("uv") == {"package": False},
            "Python project contains external tool, workspace, source, or dependency metadata")
    packages = locked.get("package")
    require(set(locked) == {"version", "revision", "requires-python", "package"} and
            locked.get("version") == 1 and locked.get("revision") == 3 and
            locked.get("requires-python") == "==3.14.*" and
            isinstance(packages, list) and len(packages) == 1 and
            packages[0] == {"name": "rebar-experiment", "version": "0.0.0",
                            "source": {"virtual": "."}},
            "Python dependency lock must contain exactly the first-party local project")
    return {"package": "rebar-experiment", "package_count": 1,
            "external_dependency_count": 0, "third_party_regex_packages": 0,
            "optional_dependency_count": 0, "workspace_dependency_count": 0,
            "support_owner_count": 2}


def inspect_go_mod(source: str) -> dict[str, object]:
    values = [line.strip() for line in source.splitlines()
              if line.strip() and not line.lstrip().startswith("//")]
    require(values == ["module rebar.local/candidates/go", "go 1.26.0"],
            "Go module must contain exactly the first-party module and language version")
    return {"module": "rebar.local/candidates/go", "language_version": "1.26.0",
            "external_dependency_count": 0,
            "generated_header": "NOT GENERATED; NOT BUILT",
            "generated_header_committed_owner": None}


ARCHITECTURE_MARKERS = {
    "c_vm": {"_BytecodeParser", "_BytecodeCompiler", "PyInit__vm_native"},
    "rust": {"Parser", "Compiler", "run_program", "rebar_compile", "rebar_match"},
    "zig": {"Parser", "Compiler", "runBytecode", "rebar_zig_compile"},
    "cpp": {"Lexer", "Parser", "Compiler", "execute", "compile", "PyInit__cpp_bridge"},
    "go": {"parser", "compiler", "compileProgram", "executeAt", "rebar_go_compile",
           "rebar_go_execute"},
    "fortran": {"parse_alternation", "compile_node", "execute_once",
                "rebar_fortran_compile", "rebar_fortran_execute"},
}


def exact_json(data: bytes, path: str) -> dict[str, object]:
    try:
        record = json.loads(decode_source(data, path))
    except (json.JSONDecodeError, TypeError, ValueError, RecursionError) as error:
        raise AuditError(f"{path}: invalid frozen JSON") from error
    require(isinstance(record, dict), f"{path}: JSON must contain an object")
    return record


def check_graph_summary(summary: dict[str, object]) -> None:
    require(summary.get("schema") == "rebar-candidate-current-overview-v7-summary" and
            summary.get("status") == "PASS" and
            summary.get("source") == {
                "path": "tools/render_candidate_current_overview_v7.py",
                "sha256": FIXED_CONTEXT["tools/render_candidate_current_overview_v7.py"]} and
            summary.get("inputs") == {
                "path": "docs/evidence/candidate-current-overview-v7.inputs.json",
                "sha256": FIXED_CONTEXT[
                    "docs/evidence/candidate-current-overview-v7.inputs.json"]} and
            summary.get("python") == "3.14.6" and
            summary.get("suite_count") == 13 and
            summary.get("full_case_denominator") == 31237 and
            summary.get("actual_candidate_imports") == 0 and
            summary.get("actual_candidate_processes_started") == 0 and
            summary.get("clock_samples") == 0 and
            summary.get("hidden_cases_read") == 0 and
            summary.get("performance_files_read") == 0 and
            summary.get("final_holdout_opened") is False and
            summary.get("winner_selected") is False and
            summary.get("performance") == "NOT MEASURED",
            "published graph V7 summary, source linkage, or measurement boundary changed")


def check_graph_owners(graph: dict[str, object]) -> dict[str, dict[str, str]]:
    require(graph.get("schema") == "rebar-candidate-current-overview-v7-inputs"
            and graph.get("version") == 7 and graph.get("suite_count") == 13
            and graph.get("full_case_denominator") == 31237,
            "pushed graph V7 source-owner provenance has changed")
    records = graph.get("families")
    require(isinstance(records, list), "graph V7 family records are missing")
    by_name: dict[str, dict[str, str]] = {}
    for record in records:
        require(isinstance(record, dict) and isinstance(record.get("family"), str),
                "invalid graph V7 family record")
        name = record["family"]
        require(name not in by_name, "duplicate graph V7 family")
        source_list = record.get("owned_sources")
        require(isinstance(source_list, list), f"{name}: graph source owners are missing")
        owners: dict[str, str] = {}
        for owner in source_list:
            require(isinstance(owner, dict) and set(owner) == {"path", "sha256"},
                    f"{name}: invalid graph source owner")
            path = owner["path"]
            checked_relative(path)
            require(path not in owners, f"{name}: duplicate graph source owner")
            owners[path] = valid_sha256(owner["sha256"], f"{path} graph owner")
        by_name[name] = owners
    require(set(by_name) == {"python", "rust", "c", "zig", "cpp", "go", "fortran"},
            "graph V7 does not contain Python and exactly six candidate families")
    require(not by_name["python"], "Python baseline must not count as a native source family")
    all_paths: set[str] = set()
    for family in FAMILIES:
        required = {owner.path for owner in family.owners}
        actual = by_name[family.graph_name]
        require(set(actual) == required,
                f"{family.name}: missing, foreign, or silently substituted graph V7 owner")
        require(not (all_paths & required), f"{family.name}: cross-family owner overlap")
        all_paths.update(required)
    require(len(all_paths) == 25, "graph V7 must prove exactly 25 disjoint semantic owners")
    return by_name


def preserved_receipts(graph: dict[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}

    def add(value: object) -> None:
        if not isinstance(value, dict):
            return
        path, digest = value.get("path"), value.get("sha256")
        if (isinstance(path, str) and
                (path.endswith("-publication-receipt.json") or
                 path.endswith("-restoration-receipt.json"))):
            checked_relative(path, allow_evidence=True)
            digest = valid_sha256(digest, f"{path} receipt")
            require(path not in result or result[path] == digest,
                    f"{path}: conflicting historical receipt pins")
            result[path] = digest

    records = graph.get("families")
    require(isinstance(records, list), "historical graph families are missing")
    for family in records:
        require(isinstance(family, dict), "invalid historical graph family")
        for key in ("build_evidence", "historical_build_evidence", "correctness_evidence",
                    "historical_correctness_evidence", "historical_worker_failure_evidence"):
            item = family.get(key)
            if isinstance(item, dict):
                add(item.get("receipt"))
                add(item.get("worker_receipt"))
        children = family.get("subordinate_evidence")
        if isinstance(children, list):
            for child in children:
                add(child)
    frozen = graph.get("frozen_inputs")
    require(isinstance(frozen, dict), "graph V7 frozen-input provenance is missing")
    add(frozen.get("v5_c_restoration_receipt"))
    add(frozen.get("v5_rust_restoration_receipt"))
    require(len(result) == 24, "graph V7 historical build/failure receipts were omitted")
    return result


def current_v5_evidence(graph: dict[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}

    def add(value: object, *, archive: bool) -> None:
        require(isinstance(value, dict) and set(value) == {"path", "sha256"},
                "current C/Rust V5 evidence must contain an exact path and SHA-256")
        path = value["path"]
        checked_relative(path, allow_evidence=True)
        require(path.startswith("oracle/phase2/evidence/") or
                path.startswith("experiments/rust_public_practice_v1/"),
                f"{path}: evidence is outside the published C/Rust V5 owners")
        require(path.endswith(".json.gz") if archive else
                path.endswith("-publication-receipt.json") or
                path.endswith("-restoration-receipt.json"),
                f"{path}: current V5 evidence has the wrong archive or receipt type")
        require(path not in result, f"{path}: current V5 evidence owner is duplicated")
        result[path] = valid_sha256(value["sha256"], f"{path} current V5 evidence")

    records = graph.get("families")
    require(isinstance(records, list), "current C/Rust V5 graph families are missing")
    selected = [record for record in records if isinstance(record, dict) and
                record.get("family") in {"c", "rust"}]
    require(len(selected) == 2 and
            {record["family"] for record in selected} == {"c", "rust"},
            "current V5 failure lineage must contain exactly C and Rust")
    expected_passes = {"c": 7197, "rust": 7461}
    expected_suites = {"c": 7, "rust": 8}
    for family in selected:
        name = family["family"]
        evidence = family.get("correctness_evidence")
        require(isinstance(evidence, dict) and
                evidence.get("expected_gate_status") == "FAIL" and
                evidence.get("qualified_case_executions") == 0 and
                evidence.get("verified_passing_case_executions") ==
                expected_passes[name] and
                evidence.get("passed_suite_count") == expected_suites[name] and
                evidence.get("interpreter_failure_classification") ==
                "TEST INFRASTRUCTURE; MATCHING CASE EXECUTION NOT ESTABLISHED",
                f"{name}: historical current V5 failure was omitted or presented as a pass")
        add(evidence.get("archive"), archive=True)
        add(evidence.get("receipt"), archive=False)
        add(evidence.get("worker_archive"), archive=True)
        add(evidence.get("worker_receipt"), archive=False)
        children = family.get("subordinate_evidence")
        require(isinstance(children, list) and len(children) == 12,
                f"{name}: current V5 specialist evidence was omitted")
        for child in children:
            require(isinstance(child, dict) and isinstance(child.get("path"), str),
                    f"{name}: specialist evidence is invalid")
            add(child, archive=child["path"].endswith(".json.gz"))
    frozen = graph.get("frozen_inputs")
    require(isinstance(frozen, dict), "current V5 restoration provenance is missing")
    add(frozen.get("v5_c_restoration_receipt"), archive=False)
    add(frozen.get("v5_rust_restoration_receipt"), archive=False)
    archive_count = sum(path.endswith(".json.gz") for path in result)
    require(len(result) == 34 and archive_count == 16 and
            len(result) - archive_count == 18,
            "current C/Rust V5 must preserve exactly 16 compressed reports and 18 receipts")
    return result


def inspect_architecture(family: Family, records: dict[str, dict[str, object]],
                         parsed_python: dict[str, object]) -> dict[str, object]:
    names: set[str] = set()
    for record in records.values():
        identifiers = record.get("identifiers")
        if isinstance(identifiers, set):
            names.update(identifiers)
    names.update(parsed_python.get("python_names", set()))
    missing = sorted(ARCHITECTURE_MARKERS[family.name] - names)
    require(not missing, f"{family.name}: missing independently owned execution {missing!r}")
    return {"parser_compiler_executor_owned": True,
            "required_production_markers": sorted(ARCHITECTURE_MARKERS[family.name]),
            "shared_semantic_owner_count": 0}


def _self_test_checks() -> tuple[int, int]:
    positives = 0
    hostile = 0

    def accept(function: object, *args: object) -> None:
        nonlocal positives
        function(*args)
        positives += 1

    def reject(function: object, *args: object) -> None:
        nonlocal hostile
        try:
            function(*args)
        except (AuditError, TypeError, ValueError, UnicodeError, RecursionError):
            hostile += 1
            return
        raise AuditError(f"hostile source control accepted by {function.__name__}: {args!r}")

    basic = {
        family.name: f"from candidates import {family.bridge}\n"
        for family in FAMILIES
    }
    basic["cpp"] += "import sys\nvalue = sys.maxsize\n"
    basic["fortran"] += "import sys\nvalue = -sys.maxsize - 1\n"
    basic["go"] += "import copyreg\n"
    basic["zig"] = (
        "import ctypes\nimport os\nfrom candidates import _zig_bridge\n"
        "class Native:\n"
        "    def __init__(self):\n"
        '        path = os.path.join(os.path.dirname(__file__), "_zig_probe.so")\n'
        "        self.library = ctypes.CDLL(path)\n"
    )
    attacks = (
        "import re\n", "import re as engine\n", "from re import compile\n",
        "from re._compiler import compile\n", "import _sre\n", "import regex\n",
        "import regexp\n", "import re2\n", "import pcre2\n", "import importlib\n",
        "from importlib import import_module\n", "import builtins\n",
        "import subprocess\n", "import multiprocessing\n", "import runpy\n",
        "import cffi\n", "__import__('r' + 'e')\n", "eval('re')\n",
        "exec('import re')\n", "globals()['__builtins__']\n",
        "locals()['__import__']\n", "getattr(object(), '__glo' + 'bals__')\n",
        "getattr(object(), chr(95) + '_import__')\n", "object().__globals__\n",
        "import os as outside\noutside.system('x')\n",
        "from os import system as dispatch\ndispatch('x')\n",
        "import os\nos.environ['PYTEST_CURRENT_TEST']\n",
        "import os\nos.getenv('REBAR_BENCHMARK')\n",
        "import sys as system\nsystem.modules['re']\n",
        "import sys\nsys.meta_path\n", "import sys\nsys.path\n",
        "def fallback():\n    return 1\n", "def benchmark():\n    return 1\n",
    )
    for family in FAMILIES:
        accept(inspect_python, basic[family.name], family, "fixture.py")
        for attack in attacks:
            reject(inspect_python, basic[family.name] + attack, family, "fixture.py")
        for other in FAMILIES:
            if other.name != family.name:
                reject(inspect_python,
                       basic[family.name] + f"from candidates import {other.bridge}\n",
                       family, "fixture.py")
    zig = FAMILY_BY_NAME["zig"]
    for payload in (
        "import ctypes as c\nc.CDLL('foreign.so')\n",
        "from ctypes import CDLL\nCDLL('foreign.so')\n",
        "ctypes.CDLL('foreign.so')\n",
        "ctypes.PyDLL(path)\n",
        "ctypes.CDLL(path)\n",
        "getattr(ctypes, 'CD' + 'LL')(path)\n",
    ):
        reject(inspect_python, basic["zig"] + payload, zig, "fixture.py")
    reject(inspect_python, basic["zig"].replace("_zig_probe.so", "_rust_engine.so"),
           zig, "fixture.py")

    safe_c = '#include <Python.h>\nconst char *name="_sre.SRE_Scanner";\n'
    accept(inspect_native, safe_c, FAMILY_BY_NAME["c_vm"], "fixture.c", "c")
    accept(inspect_native, '#include "engine.hpp"\nclass Parser {};\n',
           FAMILY_BY_NAME["cpp"], "candidates/cpp/engine.cpp", "cpp")
    for module in ("copyreg", "functools", "inspect"):
        accept(inspect_native, f'PyImport_ImportModule("{module}");\n',
               FAMILY_BY_NAME["rust"], "candidates/rust/py_bridge.c", "c")
    for family_name, path, kind in (
        ("cpp", "candidates/cpp/py_bridge.cpp", "cpp"),
        ("go", "candidates/go/py_bridge.c", "c"),
    ):
        accept(inspect_native, 'PyImport_ImportModule("unicodedata");\n',
               FAMILY_BY_NAME[family_name], path, kind)
    zig_native = 'const std = @import("std");\n'
    accept(inspect_native, zig_native, zig, "fixture.zig", "zig")
    for payload in (
        'PyImport_ImportModule("re");\n',
        'PyImport_ImportModule("r" "e");\n',
        'PyImport_ImportModule("\\x72\\x65");\n',
        'PyImport_ImportModule("_sre");\n',
        'PyImport_ImportModule("regex");\n',
        "PyImport_ImportModule(module_name);\n",
        "#define DISPATCH PyImport_ImportModule\n",
        'PyRun_SimpleString("import re");\n',
        'PyEval_EvalCode(code, globals, locals);\n',
        'dlopen("libpcre2.so", 1);\n', 'dlsym(handle, "pcre2_match");\n',
        "regcomp(pattern, flags);\n", "pcre2_compile(pattern);\n",
        "pcre2_compile_8(pattern);\n", "pcre2_match_8(pattern);\n",
        "pcre2_match_16(pattern);\n", "onig_search_gpos(pattern);\n",
        "re2_match(pattern);\n", "RE2 engine;\n", "hs_compile(pattern);\n",
        "hs_scan(pattern);\n", "hyperscan_match(pattern);\n",
        "rure_compile(pattern);\n", "tre_regcomp(pattern);\n",
        "onig_search(pattern);\n", "system(command);\n",
        '#include <pcre2.h>\n', '#include "foreign.hpp"\n',
        "#include FOREIGN\n", "/* unterminated", '"unterminated',
    ):
        reject(inspect_native, safe_c + payload, FAMILY_BY_NAME["rust"],
               "candidates/rust/py_bridge.c", "c")
    for payload in (
        '@import("regex")', '@import("pcre2")', "@import(package)",
        '@cImport({ @cInclude("pcre2.h"); })', "std.DynLib.open(path)",
        "rebar_go_compile()", "rebar_fortran_compile()",
    ):
        reject(inspect_native, zig_native + payload, zig, "fixture.zig", "zig")
    accept(inspect_native,
           'module rebar_fortran_engine\nuse, intrinsic :: iso_c_binding\n'
           '! dlopen("pcre2") and PyImport_ImportModule("re") are comments\n'
           'end module rebar_fortran_engine\n',
           FAMILY_BY_NAME["fortran"], "fixture.f90", "fortran")
    reject(inspect_native, "module x\nuse external_regex\nend module\n",
           FAMILY_BY_NAME["fortran"], "fixture.f90", "fortran")
    for payload in (
        'include "foreign-engine.f90"\n',
        "include 'foreign-engine.f90'\n",
        'function hidden() bind(C, name="pcre2_match_8")\nend function\n',
        'function hidden() bind(C, name="rebar_go_execute")\nend function\n',
        'function hidden() bind(C, name=foreign)\nend function\n',
    ):
        reject(inspect_native, payload, FAMILY_BY_NAME["fortran"],
               "fixture.f90", "fortran")
    accept(inspect_native,
           '#include "engine.hpp"\nconst char *x=R"tag(dlopen pcre2)tag";\n',
           FAMILY_BY_NAME["cpp"], "candidates/cpp/engine.cpp", "cpp")
    reject(inspect_native, '#include "engine.hpp"\nconst char*x=R"x(oops)',
           FAMILY_BY_NAME["cpp"], "candidates/cpp/engine.cpp", "cpp")
    for payload in ("std::regex pattern;\n", "std::basic_regex<char> pattern;\n",
                    "boost::regex pattern;\n", "boost::basic_regex<char> pattern;\n",
                    "std::experimental::regex pattern;\n"):
        reject(inspect_native, '#include "engine.hpp"\n' + payload,
               FAMILY_BY_NAME["cpp"], "candidates/cpp/engine.cpp", "cpp")
    for family in FAMILIES:
        for other in FAMILIES:
            prefix = {"zig": "rebar_zig_", "cpp": "rebar_cpp_",
                      "go": "rebar_go_", "fortran": "rebar_fortran_"}.get(other.name)
            if prefix is not None and family.name != other.name:
                reject(inspect_native, safe_c + f"void {prefix}compile(void);\n",
                       family, "fixture.c", "c")

    clean_manifest = ('[package]\nname="rebar-rust-continuation"\n'
                      'version="0.1.0"\npublish=false\n[lib]\ncrate-type=["cdylib"]\n')
    clean_lock = ('version=4\n[[package]]\nname="rebar-rust-continuation"\n'
                  'version="0.1.0"\n')
    accept(inspect_cargo, clean_manifest, clean_lock)
    for addition in ('[dependencies]\nregex="1"\n', '[dev-dependencies]\nregex="1"\n',
                     '[build-dependencies]\nregex="1"\n',
                     '[target."cfg(unix)".dependencies]\nregex="1"\n',
                     '[workspace.dependencies]\nregex="1"\n',
                     '[patch.crates-io]\nregex={path="../regex"}\n',
                     '[replace]\n"regex:1"={path="../regex"}\n'):
        reject(inspect_cargo, clean_manifest + addition, clean_lock)
    for addition in ('\n[[package]]\nname="regex"\nversion="1"\n',
                     'source="registry+https://example.invalid"\n',
                     'dependencies=["regex"]\n'):
        reject(inspect_cargo, clean_manifest, clean_lock + addition)
    clean_go = "module rebar.local/candidates/go\n\ngo 1.26.0\n"
    accept(inspect_go_mod, clean_go)
    for extra in ('require example.invalid/regexp v1.0.0\n',
                  'replace local => ../rust\n', 'exclude regex v1\n',
                  'toolchain go1.26.3\n', 'go 1.25.0\n'):
        reject(inspect_go_mod, clean_go + extra)
    clean_project = (
        '[project]\nname = "rebar-experiment"\nversion = "0.0.0"\n'
        'description = "First-party experiment"\n'
        'requires-python = ">=3.14,<3.15"\ndependencies = []\n'
        '\n[tool.uv]\npackage = false\n'
    )
    clean_project_lock = (
        'version = 1\nrevision = 3\nrequires-python = "==3.14.*"\n'
        '\n[[package]]\nname = "rebar-experiment"\nversion = "0.0.0"\n'
        'source = { virtual = "." }\n'
    )
    accept(inspect_project, clean_project, clean_project_lock)
    for changed in (
        clean_project.replace("dependencies = []", 'dependencies = ["regex"]'),
        clean_project.replace("dependencies = []", 'dependencies = ["re2"]'),
        clean_project + '\n[project.optional-dependencies]\nfast = ["regex"]\n',
        clean_project + '\n[dependency-groups]\nfast = ["regex"]\n',
        clean_project + '\n[tool.uv.sources]\nregex = { path = "../regex" }\n',
        clean_project + '\n[tool.uv.workspace]\nmembers = ["../regex"]\n',
        clean_project.replace("package = false", "package = true"),
        clean_project.replace("rebar-experiment", "external-regex"),
        clean_project.replace(">=3.14,<3.15", ">=3.13"),
    ):
        reject(inspect_project, changed, clean_project_lock)
    for changed in (
        clean_project_lock + '\n[[package]]\nname = "regex"\nversion = "1"\n',
        clean_project_lock.replace('{ virtual = "." }',
                                   '{ registry = "https://example.invalid" }'),
        clean_project_lock + '\ndependencies = [{ name = "regex" }]\n',
        clean_project_lock.replace("revision = 3", "revision = 2"),
        clean_project_lock.replace('==3.14.*', '==3.13.*'),
    ):
        reject(inspect_project, clean_project, changed)

    clean_go_source = (
        'package main\n/*\n#include <stddef.h>\n#include <stdint.h>\n'
        '#include <stdlib.h>\n*/\nimport "C"\n'
        'import ("fmt" "runtime/cgo" "strconv" "sync" "sync/atomic" "unsafe")\n'
        'var documentation = `dlopen("pcre2") and PyImport_ImportModule("re")`\n'
    )
    go_family = FAMILY_BY_NAME["go"]
    accept(inspect_native, clean_go_source, go_family,
           "fixture.go", "go")
    for changed in (
        clean_go_source + '\nimport "regexp"\n',
        clean_go_source + '\nimport "github.com/example/regex"\n',
        clean_go_source + '\nimport (external "regexp")\n',
        clean_go_source + '\nimport "C"\n',
        clean_go_source.replace('"sync/atomic" ', ''),
        clean_go_source + '\nvar hidden = `unterminated\n',
        clean_go_source.replace('#include <stdlib.h>\n',
                                '#include <stdlib.h>\n#cgo LDFLAGS: -lpcre2-8\n'),
        clean_go_source.replace('#include <stdlib.h>\n',
                                '#include <stdlib.h>\n#include <pcre2.h>\n'),
        clean_go_source.replace('#include <stdlib.h>\n',
                                '#include <stdlib.h>\n'
                                'static int hidden(void) { return pcre2_match_8(); }\n'),
        clean_go_source + '\n//go:linkname hidden pcre2_match_8\n',
        clean_go_source + '\n//go:embed external-engine.so\n',
        clean_go_source + '\n//export pcre2_match_8\n',
    ):
        reject(inspect_native, changed, go_family,
               "fixture.go", "go")

    clean_summary = {
        "schema": "rebar-candidate-current-overview-v7-summary",
        "status": "PASS", "source": {
            "path": "tools/render_candidate_current_overview_v7.py",
            "sha256": FIXED_CONTEXT["tools/render_candidate_current_overview_v7.py"]},
        "inputs": {
            "path": "docs/evidence/candidate-current-overview-v7.inputs.json",
            "sha256": FIXED_CONTEXT[
                "docs/evidence/candidate-current-overview-v7.inputs.json"]},
        "python": "3.14.6", "suite_count": 13,
        "full_case_denominator": 31237, "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0, "clock_samples": 0,
        "hidden_cases_read": 0, "performance_files_read": 0,
        "final_holdout_opened": False, "winner_selected": False,
        "performance": "NOT MEASURED",
    }
    accept(check_graph_summary, clean_summary)
    for key, value in (
        ("status", "FAIL"), ("python", "3.14.7"),
        ("suite_count", 12), ("full_case_denominator", 31236),
        ("actual_candidate_imports", 1), ("actual_candidate_processes_started", 1),
        ("clock_samples", 1), ("hidden_cases_read", 1),
        ("performance_files_read", 1), ("final_holdout_opened", True),
        ("winner_selected", True), ("performance", "MEASURED"),
        ("source", {"path": "tools/foreign.py", "sha256": "a" * 64}),
        ("inputs", {"path": "docs/evidence/foreign.json", "sha256": "a" * 64}),
    ):
        changed_summary = dict(clean_summary)
        changed_summary[key] = value
        reject(check_graph_summary, changed_summary)

    def reference(path: str) -> dict[str, str]:
        return {"path": path, "sha256": "a" * 64}

    synthetic_families: list[dict[str, object]] = []
    for name, passes, suite_count in (("c", 7197, 7), ("rust", 7461, 8)):
        prefix = f"oracle/phase2/evidence/synthetic-v5-{name}"
        children: list[dict[str, str]] = []
        for index in range(6):
            feature = f"experiments/rust_public_practice_v1/{name}-synthetic-{index}"
            children.append(reference(feature + ".json.gz"))
            children.append(reference(feature + "-publication-receipt.json"))
        synthetic_families.append({
            "family": name,
            "correctness_evidence": {
                "expected_gate_status": "FAIL", "qualified_case_executions": 0,
                "verified_passing_case_executions": passes,
                "passed_suite_count": suite_count,
                "interpreter_failure_classification":
                    "TEST INFRASTRUCTURE; MATCHING CASE EXECUTION NOT ESTABLISHED",
                "archive": reference(prefix + "-failures.json.gz"),
                "receipt": reference(prefix + "-failures-publication-receipt.json"),
                "worker_archive": reference(prefix + "-worker-failures.json.gz"),
                "worker_receipt": reference(
                    prefix + "-worker-failures-publication-receipt.json"),
            },
            "subordinate_evidence": children,
        })
    synthetic_graph = {
        "families": synthetic_families,
        "frozen_inputs": {
            "v5_c_restoration_receipt": reference(
                "oracle/phase2/evidence/synthetic-v5-c-restoration-receipt.json"),
            "v5_rust_restoration_receipt": reference(
                "oracle/phase2/evidence/synthetic-v5-rust-restoration-receipt.json"),
        },
    }
    accept(current_v5_evidence, synthetic_graph)
    for attack in range(9):
        changed_graph = json.loads(json.dumps(synthetic_graph))
        family_evidence = changed_graph["families"][0]["correctness_evidence"]
        if attack == 0:
            family_evidence.pop("archive")
        elif attack == 1:
            family_evidence["archive"]["sha256"] = "b"
        elif attack == 2:
            family_evidence["expected_gate_status"] = "PASS"
        elif attack == 3:
            family_evidence["qualified_case_executions"] = 1
        elif attack == 4:
            family_evidence["verified_passing_case_executions"] = 7198
        elif attack == 5:
            changed_graph["families"][0]["subordinate_evidence"].pop()
        elif attack == 6:
            changed_graph["families"][0]["subordinate_evidence"][0]["path"] = (
                "../foreign-failures.json.gz")
        elif attack == 7:
            changed_graph["frozen_inputs"].pop("v5_c_restoration_receipt")
        else:
            changed_graph["families"].pop()
        reject(current_v5_evidence, changed_graph)

    for value in ("", "/etc/passwd", "../candidate.py", "candidates/../secret",
                  "candidates//x", "./candidates/x", "candidates\\x", "candidates/\x00x",
                  ".git/config", "hidden-holdout/x", "benchmarks/input.json",
                  "performance/results.json", "tools/perf/x"):
        reject(checked_relative, value)
    for value in ("GOAL.md", "candidates/go/engine.go",
                  "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md",
                  "docs/evidence/candidate-current-overview-v7.inputs.json"):
        accept(checked_relative, value)
    require(len({owner.path for family in FAMILIES for owner in family.owners}) == 25,
            "synthetic family closure does not contain exactly 25 disjoint owners")
    positives += 1
    require(positives >= 18 and hostile >= 225,
            "insufficient positive or adversarial source-only independence controls")
    return positives, hostile


def run_self_test() -> dict[str, object]:
    effects = {"candidate_imports": 0, "candidate_processes_started": 0,
               "reference_processes_started": 0, "file_reads": 0,
               "file_writes": 0, "clock_samples": 0, "network_requests": 0,
               "native_libraries_loaded": 0, "hidden_cases_read": 0,
               "performance_files_read": 0}
    before = frozenset(name for name in sys.modules
                       if name == "candidates" or name.startswith("candidates."))
    patches: list[tuple[object, str, object]] = []

    def blocked(category: str):
        def reject(*_args: object, **_kwargs: object) -> object:
            effects[category] += 1
            raise AuditError(f"source self-test attempted external effect: {category}")
        return reject

    def guard(owner: object, name: str, category: str) -> None:
        if hasattr(owner, name):
            patches.append((owner, name, getattr(owner, name)))
            setattr(owner, name, blocked(category))

    for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                        (os, "stat"), (os, "lstat"), (os, "scandir")):
        guard(owner, name, "file_reads")
    for owner, name in ((os, "system"), (os, "popen"), (os, "fork"),
                        (os, "posix_spawn"), (subprocess, "Popen"),
                        (subprocess, "run"), (subprocess, "call")):
        guard(owner, name, "candidate_processes_started")
    for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                 "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                 "thread_time_ns", "clock_gettime", "clock_gettime_ns"):
        guard(time, name, "clock_samples")
    for name in ("CDLL", "PyDLL"):
        guard(ctypes, name, "native_libraries_loaded")
    for name in ("socket", "create_connection"):
        guard(socket, name, "network_requests")
    try:
        positive, hostile = _self_test_checks()
        after = frozenset(name for name in sys.modules
                          if name == "candidates" or name.startswith("candidates."))
        effects["candidate_imports"] = len(after - before)
        require(not any(effects.values()),
                f"source-only audit produced an external side effect: {effects!r}")
    finally:
        for owner, name, original in reversed(patches):
            setattr(owner, name, original)
    return {"schema": SELF_TEST_SCHEMA, "status": "PASS",
            "python": ".".join(map(str, sys.version_info[:3])),
            "family_count": 6, "source_owner_count": 25,
            "positive_controls": positive, "rejected_attack_controls": hostile,
            "candidate_correctness": "NOT MEASURED", "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED", **effects}


def run_verify(arguments: argparse.Namespace) -> dict[str, object]:
    require(tuple(sys.version_info[:3]) == PINNED_PYTHON,
            "use the pinned CPython 3.14.6")
    root = Path(__file__).resolve(strict=True).parent.parent
    cache: dict[str, tuple[bytes, str]] = {}
    allowed = set(FIXED_CONTEXT)
    allowed.update({"tools/audit_candidate_independence_v2.py",
                    "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md",
                    "oracle/phase2/candidate-independence-v2.json"})
    allowed.update(owner.path for family in FAMILIES for owner in family.owners)

    def owned(path: str, *, evidence: bool = False) -> tuple[bytes, str]:
        require(path in allowed, f"read outside the frozen source-only closure: {path}")
        if path not in cache:
            cache[path] = read_owned_file(root, path, evidence=evidence)
        return cache[path]

    for path, expected in FIXED_CONTEXT.items():
        _, digest = owned(path)
        require(digest == expected, f"{path}: frozen predecessor or graph V7 changed")
    goal, _ = owned("GOAL.md")
    require(goal.startswith(b"/goal "), "immutable goal prefix changed")
    source, source_hash = owned("tools/audit_candidate_independence_v2.py")
    explanation, explanation_hash = owned("oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md")
    inventory_bytes, inventory_hash = owned("oracle/phase2/candidate-independence-v2.json")
    if arguments.source_sha256:
        require(source_hash == valid_sha256(arguments.source_sha256, "V2 audit source"),
                "V2 audit source pin does not match")
    if arguments.protocol_sha256:
        require(explanation_hash == valid_sha256(arguments.protocol_sha256, "V2 audit protocol"),
                "V2 audit protocol pin does not match")
    if arguments.inventory_sha256:
        require(inventory_hash == valid_sha256(arguments.inventory_sha256, "V2 audit inventory"),
                "V2 audit inventory pin does not match")
    require(bool(source) and bool(explanation), "V2 source or explanation is empty")
    inventory = exact_json(inventory_bytes, "oracle/phase2/candidate-independence-v2.json")
    require(inventory.get("schema") == SCHEMA and inventory.get("version") == 2,
            "V2 inventory schema or version is wrong")
    require(inventory.get("goal_sha256") == GOAL_SHA256,
            "V2 inventory objective does not match")
    require(inventory.get("family_count") == 6 and inventory.get("source_owner_count") == 25,
            "V2 inventory candidate family denominator changed")
    support = inventory.get("python_project_support_owners")
    require(isinstance(support, dict) and support.get("count") == 2 and
            support.get("external_dependency_count") == 0 and
            support.get("owners") == [
                {"path": "pyproject.toml", "sha256": FIXED_CONTEXT["pyproject.toml"]},
                {"path": "uv.lock", "sha256": FIXED_CONTEXT["uv.lock"]}],
            "V2 inventory omitted or substituted the Python project dependency closure")
    project = inspect_project(
        decode_source(owned("pyproject.toml")[0], "pyproject.toml"),
        decode_source(owned("uv.lock")[0], "uv.lock"))
    graph_inventory = inventory.get("pushed_graph_v7")
    require(isinstance(graph_inventory, dict) and
            graph_inventory.get("inputs") == {
                "path": "docs/evidence/candidate-current-overview-v7.inputs.json",
                "sha256": FIXED_CONTEXT[
                    "docs/evidence/candidate-current-overview-v7.inputs.json"]} and
            graph_inventory.get("summary") == {
                "path": "docs/evidence/candidate-current-overview-v7.json",
                "sha256": FIXED_CONTEXT[
                    "docs/evidence/candidate-current-overview-v7.json"]} and
            graph_inventory.get("renderer") == {
                "path": "tools/render_candidate_current_overview_v7.py",
                "sha256": FIXED_CONTEXT[
                    "tools/render_candidate_current_overview_v7.py"]} and
            graph_inventory.get("is_a_p0_candidate_protocol") is False,
            "V2 inventory changed the published graph V7 source, inputs, or summary")
    check_graph_summary(exact_json(
        owned("docs/evidence/candidate-current-overview-v7.json")[0],
        "docs/evidence/candidate-current-overview-v7.json"))
    graph = exact_json(owned("docs/evidence/candidate-current-overview-v7.inputs.json")[0],
                       "docs/evidence/candidate-current-overview-v7.inputs.json")
    graph_owners = check_graph_owners(graph)
    graph_receipts = preserved_receipts(graph)
    graph_current_evidence = current_v5_evidence(graph)
    history = inventory.get("historical_receipts")
    require(isinstance(history, dict) and history.get("count") == len(graph_receipts)
            and history.get("source") ==
            "docs/evidence/candidate-current-overview-v7.inputs.json" and
            history.get("current_v5_archive_payloads") ==
            "RAW SHA-256 VERIFIED; NOT DECOMPRESSED" and
            history.get("receipt_publication_does_not_qualify_a_candidate") is True,
            "V2 preserved historical receipt denominator changed")
    current_history = inventory.get("historical_c_rust_v5_evidence_owners")
    require(isinstance(current_history, dict) and
            current_history.get("source") ==
            "docs/evidence/candidate-current-overview-v7.inputs.json" and
            current_history.get("count") == len(graph_current_evidence) and
            current_history.get("compressed_report_archive_count") == 16 and
            current_history.get("durable_receipt_count") == 18 and
            current_history.get("compressed_report_bytes_sha256_verified") is True and
            current_history.get("report_archives_are_not_decompressed") is True and
            current_history.get("failure_results_are_preserved") is True,
            "V2 omitted or misstated the 34 current C/Rust V5 failure evidence owners")
    published = graph.get("frozen_inputs")
    require(isinstance(published, dict), "graph V7 frozen provenance is absent")
    for key, path in (("goal", "GOAL.md"),
                      ("independence_audit", "tools/audit_candidate_independence_v1.py"),
                      ("independence_protocol", "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md"),
                      ("phase1_inventory", "oracle/phase1/p0-completeness-v1.json"),
                      ("phase1_verifier", "tools/verify_p0_completeness_v1.py"),
                      ("phase2_v5_inventory", "oracle/phase2/p0-candidate-protocol-v5.json"),
                      ("phase2_v5_protocol", "oracle/phase2/P0-CANDIDATE-PROTOCOL-V5.md"),
                      ("phase2_v5_runner", "tools/run_frozen_p0_candidate_v5.py"),
                      ("phase2_v5_worker", "tools/run_frozen_p0_candidate_worker_v3.py")):
        value = published.get(key)
        require(isinstance(value, dict) and value.get("path") == path and
                value.get("sha256") == FIXED_CONTEXT[path],
                f"graph V7 does not bind the actual frozen {key}")
    phase1 = exact_json(owned("oracle/phase1/p0-completeness-v1.json")[0],
                        "oracle/phase1/p0-completeness-v1.json")
    suites = phase1.get("suites")
    upstream = phase1.get("original_upstream")
    phase_gate = phase1.get("phase_gate")
    require(phase1.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and isinstance(suites, list) and len(suites) == 13 and
            sum(item.get("case_execution_count", -1) for item in suites
                if isinstance(item, dict)) == 31237 and
            isinstance(upstream, dict) and upstream.get("private_waiver_count") == 13 and
            isinstance(upstream.get("private_waivers"), list) and
            len(upstream["private_waivers"]) == 13 and
            isinstance(phase_gate, dict) and phase_gate.get("status") == "PASS",
            "the immutable 13-suite, 31,237-case Python standard changed")
    entries = inventory.get("families")
    require(isinstance(entries, list) and len(entries) == 6,
            "V2 inventory does not list exactly six real families")
    by_name: dict[str, dict[str, object]] = {}
    for entry in entries:
        require(isinstance(entry, dict) and isinstance(entry.get("name"), str),
                "V2 contains an invalid family entry")
        require(entry["name"] not in by_name, "V2 contains a duplicate family")
        by_name[entry["name"]] = entry
    require(set(by_name) == set(FAMILY_BY_NAME), "V2 omitted or invented a candidate family")

    results: list[dict[str, object]] = []
    for family in FAMILIES:
        entry = by_name[family.name]
        require(entry.get("graph_family") == family.graph_name and
                entry.get("bridge") == family.bridge,
                f"{family.name}: inventory substitutes a native family")
        expected_owners = entry.get("owners")
        require(isinstance(expected_owners, list) and len(expected_owners) == len(family.owners),
                f"{family.name}: incomplete transitive source closure")
        expected_by_path: dict[str, str] = {}
        for value in expected_owners:
            require(isinstance(value, dict) and set(value) == {"path", "kind", "role", "sha256"},
                    f"{family.name}: malformed source owner")
            path = value["path"]
            checked_relative(path)
            require(path not in expected_by_path, f"{family.name}: duplicate source owner")
            expected_by_path[path] = valid_sha256(value["sha256"], f"{path} owner")
        require(expected_by_path == graph_owners[family.graph_name],
                f"{family.name}: source owners do not match pushed graph V7")
        native_records: dict[str, dict[str, object]] = {}
        python_names: set[str] = set()
        owner_records: list[dict[str, object]] = []
        cargo_manifest: str | None = None
        cargo_lock: str | None = None
        go_metadata: dict[str, object] | None = None
        for owner in family.owners:
            content, digest = owned(owner.path)
            require(digest == expected_by_path[owner.path],
                    f"{owner.path}: current source differs from graph V7")
            expected_entry = next(item for item in expected_owners
                                  if isinstance(item, dict) and item.get("path") == owner.path)
            require(expected_entry.get("kind") == owner.kind and
                    expected_entry.get("role") == owner.role,
                    f"{owner.path}: semantic source role changed")
            text = decode_source(content, owner.path)
            record: dict[str, object] = {"path": owner.path, "kind": owner.kind,
                                        "role": owner.role, "sha256": digest,
                                        "bytes": len(content)}
            if owner.kind == "python":
                inspected = inspect_python(text, family, owner.path)
                tree = ast.parse(text, filename=owner.path)
                python_names.update(node.name for node in ast.walk(tree)
                                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)))
                record.update(inspected)
            elif owner.kind in {"c", "cpp", "rust", "zig", "go", "fortran"}:
                inspected = inspect_native(text, family, owner.path, owner.kind)
                native_records[owner.path] = inspected
                record.update({key: value for key, value in inspected.items()
                               if key != "identifiers"})
            elif owner.kind == "cargo_manifest":
                cargo_manifest = text
            elif owner.kind == "cargo_lock":
                cargo_lock = text
            elif owner.kind == "go_mod":
                go_metadata = inspect_go_mod(text)
            owner_records.append(record)
        architecture = inspect_architecture(family, native_records,
                                            {"python_names": python_names})
        item: dict[str, object] = {"name": family.name, "graph_family": family.graph_name,
                                   "static_independence": "PASS", "architecture": architecture,
                                   "owners": owner_records,
                                   "source_to_binary_provenance": "NOT ESTABLISHED",
                                   "runtime_no_delegation": "NOT ESTABLISHED",
                                   "candidate_correctness": "NOT MEASURED",
                                   "performance": "NOT MEASURED"}
        if family.name == "rust":
            require(cargo_manifest is not None and cargo_lock is not None,
                    "Rust manifest or lock was omitted")
            item["dependency_metadata"] = inspect_cargo(cargo_manifest, cargo_lock)
            item["support_import_caveat"] = (
                "The literal inspect support import can transitively import Python re; "
                "runtime non-delegation is NOT ESTABLISHED by static analysis."
            )
        if family.name == "go":
            require(go_metadata is not None, "Go module owner was omitted")
            item["dependency_metadata"] = go_metadata
        if family.name == "fortran":
            item["build"] = "NOT BUILT"
        results.append(item)

    verified_current_evidence: list[dict[str, object]] = []
    allowed.update(graph_current_evidence)
    allowed.update(graph_receipts)
    for path, expected in sorted(graph_current_evidence.items()):
        _, digest = owned(path, evidence=True)
        require(digest == expected, f"{path}: current C/Rust V5 evidence bytes changed")
        archive = path.endswith(".json.gz")
        verified_current_evidence.append({
            "path": path, "sha256": digest,
            "kind": "compressed-report-raw-bytes" if archive else "durable-receipt",
            "raw_bytes_sha256_verified": True,
            "decompressed": False,
        })
    require(len(verified_current_evidence) == 34 and
            sum(item["kind"] == "compressed-report-raw-bytes"
                for item in verified_current_evidence) == 16,
            "current C/Rust V5 reports and receipts were not fully authenticated")
    verified_receipts: list[dict[str, object]] = []
    for path, expected in sorted(graph_receipts.items()):
        data, digest = owned(path, evidence=True)
        require(digest == expected, f"{path}: preserved receipt changed")
        record = exact_json(data, path)
        require(record.get("status") == "PASS" and
                isinstance(record.get("schema"), str),
                f"{path}: historical publication or restoration was not complete")
        require(record.get("hidden_cases_read", 0) == 0 and
                record.get("clock_samples", 0) == 0 and
                record.get("performance", "NOT MEASURED") == "NOT MEASURED",
                f"{path}: historical receipt changes hidden or measurement boundaries")
        verified_receipts.append({"path": path, "sha256": digest,
                                  "receipt_status": "PASS",
                                  "historical_candidate_status":
                                  record.get("candidate_status", record.get("build_status",
                                      record.get("candidate_result_status", "NOT APPLICABLE")))})
    return {"schema": SCHEMA, "status": "PASS", "static_independence": "PASS",
            "python": ".".join(map(str, sys.version_info[:3])),
            "goal_sha256": GOAL_SHA256, "source_sha256": source_hash,
            "protocol_sha256": explanation_hash, "inventory_sha256": inventory_hash,
            "family_count": 6, "source_owner_count": 25,
            "pairwise_semantic_owner_overlap_count": 0,
            "phase1_suite_count": 13, "phase1_case_execution_count": 31237,
            "phase1_private_waiver_count": 13,
            "pushed_graph_v7_input_sha256": FIXED_CONTEXT[
                "docs/evidence/candidate-current-overview-v7.inputs.json"],
            "pushed_graph_v7_summary_sha256": FIXED_CONTEXT[
                "docs/evidence/candidate-current-overview-v7.json"],
            "python_project_support_owner_count": 2,
            "project_dependency_lock": project,
            "historical_c_rust_v5_evidence_owner_count": len(verified_current_evidence),
            "historical_c_rust_v5_compressed_report_count": 16,
            "historical_c_rust_v5_durable_receipt_count": 18,
            "historical_c_rust_v5_evidence_owners": verified_current_evidence,
            "historical_report_archives_decompressed": False,
            "historical_receipt_count": len(verified_receipts),
            "historical_receipts": verified_receipts,
            "families": results, "candidate_correctness_qualified_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "source_to_binary_provenance": "NOT ESTABLISHED",
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            "candidate_code_executed": False, "native_libraries_loaded": False,
            "candidate_processes_started": 0, "reference_processes_started": 0,
            "clock_samples": 0, "hidden_cases_read": 0,
            "performance_files_read": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit six source-owned regex engines without running them.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--inventory-sha256")
    arguments = parser.parse_args(argv)
    try:
        if arguments.self_test:
            require(not arguments.source_sha256 and not arguments.protocol_sha256 and
                    not arguments.inventory_sha256,
                    "source self-test never accepts source or owner reads")
            result = run_self_test()
        else:
            result = run_verify(arguments)
    except (AuditError, OSError, ValueError, TypeError, RecursionError) as error:
        print(json.dumps({"schema": SELF_TEST_SCHEMA if arguments.self_test else SCHEMA,
                          "status": "FAIL", "error": str(error),
                          "candidate_correctness": "NOT MEASURED",
                          "performance": "NOT MEASURED", "holdout": "NOT ACCESSED"},
                         sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
