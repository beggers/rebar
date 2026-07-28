#!/usr/bin/env python3
"""Fail-closed, read-only ownership audit for the four phase-two engines."""

from __future__ import annotations

import argparse
import ast
import builtins
import hashlib
import io
import json
import os
import stat
import struct
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


SCHEMA = "rebar-phase2-candidate-independence-static-audit-v1"
SELF_TEST_SCHEMA = "rebar-phase2-candidate-independence-source-self-test-v1"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PINNED_PYTHON = (3, 14, 6)
MAX_SOURCE_BYTES = 32 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
HEX_DIGITS = frozenset("0123456789abcdef")


class AuditError(Exception):
    """A failed ownership, input, dependency, or native-artifact check."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise AuditError(message)


@dataclass(frozen=True)
class Owner:
    path: str
    kind: str


@dataclass(frozen=True)
class Artifact:
    path: str
    required_exports: tuple[str, ...]
    required_undefined: tuple[str, ...]
    needed: tuple[str, ...]
    runpath: str | None = None
    soname: str | None = None


@dataclass(frozen=True)
class Family:
    name: str
    architecture: str
    owners: tuple[Owner, ...]
    artifacts: tuple[Artifact, ...]
    allowed_bridge: str | None


FAMILIES = (
    Family(
        "python_ast",
        "independently owned Python parser and tree interpreter",
        (Owner("candidates/ast_candidate.py", "python"),),
        (),
        None,
    ),
    Family(
        "c_vm",
        "independently owned Python bytecode compiler and C virtual machine",
        (
            Owner("candidates/vm_candidate.py", "python"),
            Owner("candidates/_vm_native.c", "c"),
        ),
        (
            Artifact(
                "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
                ("PyInit__vm_native",),
                (),
                ("libc.so.6",),
            ),
        ),
        "_vm_native",
    ),
    Family(
        "rust",
        "independently owned Rust parser, compiler and executor",
        (
            Owner("candidates/rust_candidate.py", "python"),
            Owner("candidates/rust/py_bridge.c", "c"),
            Owner("candidates/rust/src/lib.rs", "rust"),
            Owner("candidates/rust/src/newline.rs", "rust"),
            Owner("candidates/rust/src/search.rs", "rust"),
            Owner("candidates/rust/src/stack.rs", "rust"),
            Owner("candidates/rust/src/unicode_tables.rs", "rust"),
            Owner("candidates/rust/Cargo.toml", "cargo_manifest"),
            Owner("candidates/rust/Cargo.lock", "cargo_lock"),
        ),
        (
            Artifact(
                "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                ("PyInit__rust_bridge",),
                ("rebar_compile", "rebar_match"),
                ("_rust_engine.so", "libc.so.6"),
                "$ORIGIN",
            ),
            Artifact(
                "candidates/_rust_engine.so",
                (
                    "rebar_compile",
                    "rebar_match",
                    "rebar_match_ascii",
                    "rebar_match_wide",
                    "rebar_collect_ascii",
                    "rebar_collect_wide",
                ),
                (),
                ("ld-linux-x86-64.so.2", "libc.so.6", "libgcc_s.so.1"),
            ),
        ),
        "_rust_bridge",
    ),
    Family(
        "zig",
        "independently owned Zig parser, bytecode compiler and executor",
        (
            Owner("candidates/zig_candidate.py", "python"),
            Owner("candidates/zig/mini_regex.zig", "zig"),
            Owner("candidates/zig/py_bridge.c", "c"),
        ),
        (
            Artifact(
                "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                ("PyInit__zig_bridge",),
                ("rebar_zig_compile_guarded", "rebar_zig_match_wide"),
                ("_zig_probe.so", "libc.so.6"),
                "$ORIGIN",
            ),
            Artifact(
                "candidates/_zig_probe.so",
                (
                    "rebar_zig_compile",
                    "rebar_zig_compile_guarded",
                    "rebar_zig_match_wide",
                ),
                (),
                ("libc.so.6",),
                None,
                "_zig_probe.so",
            ),
        ),
        "_zig_bridge",
    ),
)
FAMILY_BY_NAME = {family.name: family for family in FAMILIES}

RUSTC_PIN = {
    "path": "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/rustc",
    "sha256": "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6",
    "release": "1.95.0",
    "commit": "59807616e1fa2540724bfbac14d7976d7e4a3860",
}
CARGO_PIN = {
    "path": "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/cargo",
    "sha256": "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66",
    "release": "1.95.0",
    "commit": "f2d3ce0bd7f24a49f8f72d9000448f8838c4e850",
}
ZIG_PIN = {
    "path": "/tmp/zig-x86_64-linux-0.16.0/zig",
    "sha256": "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
    "release": "0.16.0",
}

FORBIDDEN_MODULE_ROOTS = frozenset(
    {
        "_sre",
        "ahocorasick",
        "hyperscan",
        "onig",
        "oniguruma",
        "pcre",
        "pcre2",
        "pyre2",
        "re",
        "re2",
        "regex",
        "regex_automata",
        "regex_lite",
        "regex_syntax",
        "rure",
        "sre_compile",
        "sre_constants",
        "sre_parse",
    }
)
FORBIDDEN_DYNAMIC_MODULES = frozenset(
    {
        "builtins",
        "cffi",
        "importlib",
        "marshal",
        "multiprocessing",
        "pkgutil",
        "runpy",
        "subprocess",
        "sys",
        "zipimport",
    }
)
FORBIDDEN_INTROSPECTION = frozenset(
    {
        "__builtins__",
        "__code__",
        "__getattribute__",
        "__globals__",
        "__loader__",
        "__spec__",
        "__subclasses__",
        "cr_frame",
        "f_builtins",
        "f_globals",
        "func_globals",
        "gi_frame",
        "tb_frame",
    }
)
FORBIDDEN_NATIVE_IDENTIFIERS = frozenset(
    {
        "GetProcAddress",
        "LoadLibrary",
        "LoadLibraryA",
        "LoadLibraryW",
        "PyImport_AddModule",
        "PyImport_ExecCodeModule",
        "PyImport_GetModule",
        "PyImport_GetModuleDict",
        "PyImport_Import",
        "PyImport_ImportModuleLevel",
        "PyImport_ImportModuleLevelObject",
        "PyRun_AnyFile",
        "PyRun_SimpleString",
        "PyRun_String",
        "PyRun_StringFlags",
        "PyEval_EvalCode",
        "Py_CompileString",
        "Py_CompileStringExFlags",
        "benchmark",
        "dlmopen",
        "dlopen",
        "dlsym",
        "execve",
        "holdout",
        "onig_new",
        "onig_search",
        "oracle",
        "pcre2_compile",
        "pcre2_match",
        "pcre_compile",
        "pcre_exec",
        "popen",
        "pytest",
        "regcomp",
        "regexec",
        "system",
    }
)
ALLOWED_C_HEADERS = frozenset(
    {"Python.h", "ctype.h", "stddef.h", "stdint.h", "stdlib.h", "string.h"}
)
ALLOWED_RUST_SUPPORT_IMPORTS = frozenset({"copyreg", "functools", "inspect"})
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
ELF_PROGRAM = struct.Struct("<IIQQQQQQ")
ELF_SECTION = struct.Struct("<IIQQQQIIQQ")
ELF_SYMBOL = struct.Struct("<IBBHQQ")
ELF_DYNAMIC = struct.Struct("<qQ")


def valid_sha256(value: str, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX_DIGITS for character in value),
        f"{label} must be an exact lowercase SHA-256",
    )
    return value


def checked_relative(value: str) -> tuple[str, ...]:
    require(isinstance(value, str) and value, "an owner path must not be empty")
    require("\x00" not in value and "\\" not in value, "unsafe owner path encoding")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute(), "absolute owner path rejected")
    require(str(parsed) == value, "noncanonical owner path rejected")
    require(
        all(part not in {"", ".", "..", ".git"} for part in parsed.parts),
        "owner traversal or repository metadata rejected",
    )
    require(
        all(
            "holdout" not in part.casefold()
            and "benchmark" not in part.casefold()
            and part.casefold() not in {"evidence", "performance", "perf"}
            for part in parsed.parts
        ),
        "hidden, evidence, or performance path rejected",
    )
    return parsed.parts


def _stable_signature(details: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        details.st_dev,
        details.st_ino,
        details.st_size,
        details.st_mtime_ns,
        details.st_ctime_ns,
    )


def read_owned_file(root: Path, relative: str, maximum: int) -> tuple[bytes, str]:
    parts = checked_relative(relative)
    descriptors: list[int] = []
    try:
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
        descriptors.append(os.open(os.fspath(root), directory_flags))
        for part in parts[:-1]:
            descriptors.append(os.open(part, directory_flags, dir_fd=descriptors[-1]))
        file_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
        descriptors.append(os.open(parts[-1], file_flags, dir_fd=descriptors[-1]))
        before = os.fstat(descriptors[-1])
        require(stat.S_ISREG(before.st_mode), f"{relative}: owner is not a regular file")
        require(0 <= before.st_size <= maximum, f"{relative}: owner size is unsafe")
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            piece = os.read(descriptors[-1], min(remaining, 1024 * 1024))
            require(bool(piece), f"{relative}: owner changed during audit")
            pieces.append(piece)
            remaining -= len(piece)
        require(not os.read(descriptors[-1], 1), f"{relative}: owner grew during audit")
        after = os.fstat(descriptors[-1])
        require(
            _stable_signature(before) == _stable_signature(after),
            f"{relative}: owner changed during audit",
        )
        content = b"".join(pieces)
        return content, hashlib.sha256(content).hexdigest()
    except (OSError, ValueError) as error:
        raise AuditError(f"{relative}: safe owner read failed: {error}") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def hash_pinned_tool(pin: dict[str, str]) -> dict[str, object]:
    path = pin["path"]
    require(path.startswith("/"), "toolchain pin must be absolute")
    descriptor: int | None = None
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and 0 < before.st_size <= MAX_BINARY_BYTES,
            f"{path}: unsafe toolchain executable",
        )
        digest = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(piece), f"{path}: compiler changed during audit")
            digest.update(piece)
            remaining -= len(piece)
        require(not os.read(descriptor, 1), f"{path}: compiler grew during audit")
        require(
            _stable_signature(before) == _stable_signature(os.fstat(descriptor)),
            f"{path}: compiler changed during audit",
        )
        actual = digest.hexdigest()
        require(actual == pin["sha256"], f"{path}: pinned compiler SHA-256 mismatch")
        return {
            "path": path,
            "sha256": actual,
            "size_bytes": before.st_size,
            "release": pin["release"],
            **({"commit": pin["commit"]} if "commit" in pin else {}),
            "compiler_executed": False,
        }
    except (OSError, ValueError) as error:
        raise AuditError(f"{path}: pinned toolchain read failed: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def constant_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = constant_string(node.left), constant_string(node.right)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.JoinedStr):
        parts = [constant_string(part) for part in node.values]
        return "".join(parts) if all(part is not None for part in parts) else None
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "chr"
        and len(node.args) == 1
        and not node.keywords
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, int)
        and 0 <= node.args[0].value <= 0x10FFFF
    ):
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
        self.bridge_imports: set[str] = set()
        self.zig_loaders = 0
        self.zig_anchor = False
        self.class_methods: dict[str, set[str]] = {}
        self.top_level_functions: set[str] = set()

    def reject(self, node: ast.AST, reason: str) -> None:
        raise AuditError(f"{self.path}:{getattr(node, 'lineno', '?')}: {reason}")

    def module(self, node: ast.AST, value: str) -> None:
        root = value.split(".", 1)[0]
        if root in FORBIDDEN_MODULE_ROOTS:
            self.reject(node, f"external or Python regex import {value!r}")
        if root in FORBIDDEN_DYNAMIC_MODULES:
            self.reject(node, f"dynamic import or execution module {value!r}")
        if root == "ctypes" and self.family.name != "zig":
            self.reject(node, "foreign native-library loader")
        if root == "candidates":
            if value == "candidates":
                return
            allowed = f"candidates.{self.family.allowed_bridge}"
            if self.family.allowed_bridge is None or value != allowed:
                self.reject(node, f"cross-candidate source or bridge import {value!r}")
            self.bridge_imports.add(self.family.allowed_bridge)
        self.imports.add(value)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.module(node, alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            self.reject(node, "relative candidate imports are not auditable")
        module = node.module or ""
        self.module(node, module)
        if module == "candidates":
            for alias in node.names:
                if (
                    alias.name == "*"
                    or self.family.allowed_bridge is None
                    or alias.name != self.family.allowed_bridge
                ):
                    self.reject(node, f"cross-candidate bridge import {alias.name!r}")
                self.bridge_imports.add(alias.name)
        elif module.split(".", 1)[0] == "candidates":
            self.reject(node, f"nested candidate import {module!r}")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_methods[node.name] = {
            item.name
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.top_level_functions.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.top_level_functions.add(node.name)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        chain = attribute_chain(node)
        if node.attr in FORBIDDEN_INTROSPECTION:
            self.reject(node, f"computed module escape {node.attr!r}")
        if chain is not None and chain[0] == "os":
            if len(chain) > 1 and (
                chain[1] in {"environ", "getenv", "popen", "system"}
                or chain[1].startswith(("exec", "spawn"))
            ):
                self.reject(node, f"environment or process dispatch {'.'.join(chain)!r}")
        if chain is not None and chain[0] == "ctypes":
            allowed_scalars = {
                "c_bool",
                "c_char",
                "c_char_p",
                "c_int",
                "c_int32",
                "c_int64",
                "c_size_t",
                "c_ssize_t",
                "c_uint",
                "c_uint32",
                "c_uint64",
                "c_void_p",
                "CDLL",
            }
            if self.family.name != "zig" or len(chain) != 2 or chain[1] not in allowed_scalars:
                self.reject(node, f"unowned ctypes dispatch {'.'.join(chain)!r}")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        chain = attribute_chain(node.value)
        key = constant_string(node.slice)
        if chain is not None and (
            chain == ("sys", "modules")
            or chain[-1] in {"__dict__", "__builtins__", "modules"}
        ):
            self.reject(node, f"computed module-table lookup {'.'.join(chain)!r}")
        if key in FORBIDDEN_INTROSPECTION:
            self.reject(node, f"computed introspection key {key!r}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        chain = attribute_chain(node.func)
        if chain is not None and chain[-1] in {
            "__import__",
            "eval",
            "exec",
            "globals",
            "locals",
            "vars",
            "import_module",
            "module_from_spec",
            "spec_from_file_location",
            "SourceFileLoader",
            "dlopen",
            "PyDLL",
            "WinDLL",
            "OleDLL",
            "LoadLibrary",
            "CFUNCTYPE",
        }:
            self.reject(node, f"dynamic import or execution {'.'.join(chain)!r}")
        if chain == ("getattr",) and len(node.args) >= 2:
            name = constant_string(node.args[1])
            if name in FORBIDDEN_INTROSPECTION or name in {
                "__import__",
                "eval",
                "exec",
                "import_module",
                "CDLL",
                "PyDLL",
                "LoadLibrary",
            }:
                self.reject(node, f"computed dynamic loader {name!r}")
        if chain == ("ctypes", "CDLL"):
            if (
                self.family.name != "zig"
                or len(node.args) != 1
                or node.keywords
                or not isinstance(node.args[0], ast.Name)
                or node.args[0].id != "path"
            ):
                self.reject(node, "native loader is not the owned Zig library")
            self.zig_loaders += 1
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if any(isinstance(target, ast.Name) and target.id == "path" for target in node.targets):
            call = node.value
            if (
                isinstance(call, ast.Call)
                and attribute_chain(call.func) == ("os", "path", "join")
                and len(call.args) == 2
                and not call.keywords
                and isinstance(call.args[0], ast.Call)
                and attribute_chain(call.args[0].func) == ("os", "path", "dirname")
                and len(call.args[0].args) == 1
                and isinstance(call.args[0].args[0], ast.Name)
                and call.args[0].args[0].id == "__file__"
                and constant_string(call.args[1]) == "_zig_probe.so"
            ):
                self.zig_anchor = True
        self.generic_visit(node)


def inspect_python(source: str, family: Family, path: str) -> PythonOwnershipVisitor:
    try:
        parsed = ast.parse(source, filename=path)
    except (SyntaxError, ValueError, TypeError, RecursionError) as error:
        raise AuditError(f"{path}: Python source is not safely parseable: {error}") from error
    visitor = PythonOwnershipVisitor(family, path)
    visitor.visit(parsed)
    expected = set() if family.allowed_bridge is None else {family.allowed_bridge}
    require(visitor.bridge_imports == expected, f"{path}: exact owned native bridge not found")
    if family.name == "zig":
        require(
            visitor.zig_loaders == 1 and visitor.zig_anchor,
            f"{path}: Zig must load exactly its own file-anchored probe",
        )
    else:
        require(visitor.zig_loaders == 0, f"{path}: unexpected native library loader")
    return visitor


@dataclass(frozen=True)
class NativeToken:
    kind: str
    value: str
    line: int


def native_tokens(source: str, path: str) -> list[NativeToken]:
    tokens: list[NativeToken] = []
    index = 0
    line = 1
    length = len(source)
    while index < length:
        character = source[index]
        if character.isspace():
            line += character == "\n"
            index += 1
            continue
        if source.startswith("//", index):
            finish = source.find("\n", index + 2)
            index = length if finish < 0 else finish
            continue
        if source.startswith("/*", index):
            depth = 1
            start_line = line
            index += 2
            while index < length and depth:
                if source.startswith("/*", index):
                    depth += 1
                    index += 2
                elif source.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    line += source[index] == "\n"
                    index += 1
            require(depth == 0, f"{path}:{start_line}: unterminated native comment")
            continue
        raw_prefix = None
        for prefix in ("br", "rb", "r"):
            if source.startswith(prefix, index):
                marker = index + len(prefix)
                while marker < length and source[marker] == "#":
                    marker += 1
                if marker < length and source[marker] == '"':
                    raw_prefix = (marker, marker - index - len(prefix))
                    break
        if raw_prefix is not None:
            quote_at, hashes = raw_prefix
            terminator = '"' + "#" * hashes
            finish = source.find(terminator, quote_at + 1)
            require(finish >= 0, f"{path}:{line}: unterminated raw native string")
            value = source[quote_at + 1 : finish]
            tokens.append(NativeToken("string", value, line))
            line += value.count("\n")
            index = finish + len(terminator)
            continue
        if character in {'"', "'"}:
            if (
                character == "'"
                and index + 1 < length
                and (source[index + 1].isalpha() or source[index + 1] == "_")
                and (index + 2 >= length or source[index + 2] != "'")
            ):
                tokens.append(NativeToken("punctuation", character, line))
                index += 1
                continue
            start, start_line, quote = index, line, character
            index += 1
            while index < length:
                current = source[index]
                if current == "\\":
                    require(index + 1 < length, f"{path}:{start_line}: unterminated escape")
                    line += source[index + 1] == "\n"
                    index += 2
                elif current == quote:
                    index += 1
                    break
                else:
                    require(current != "\n", f"{path}:{start_line}: unterminated native string")
                    index += 1
            else:
                raise AuditError(f"{path}:{start_line}: unterminated native string")
            spelling = source[start:index]
            try:
                value = ast.literal_eval(spelling)
            except (SyntaxError, ValueError, TypeError) as error:
                raise AuditError(f"{path}:{start_line}: invalid native string") from error
            require(isinstance(value, str), f"{path}:{start_line}: non-text native string")
            tokens.append(NativeToken("string", value, start_line))
            continue
        if character.isalpha() or character == "_":
            finish = index + 1
            while finish < length and (
                source[finish].isalnum() or source[finish] == "_"
            ):
                finish += 1
            tokens.append(NativeToken("identifier", source[index:finish], line))
            index = finish
            continue
        tokens.append(NativeToken("punctuation", character, line))
        index += 1
    return tokens


def inspect_native(source: str, family: Family, path: str, kind: str) -> dict[str, object]:
    tokens = native_tokens(source, path)
    identifiers = {token.value for token in tokens if token.kind == "identifier"}
    forbidden = sorted(identifiers & FORBIDDEN_NATIVE_IDENTIFIERS)
    require(not forbidden, f"{path}: forbidden native dispatch {forbidden!r}")
    support_imports: list[str] = []
    headers: list[str] = []
    zig_imports: list[str] = []
    for position, token in enumerate(tokens):
        if token.kind != "identifier":
            continue
        if token.value == "PyImport_ImportModule":
            require(
                family.name == "rust" and path == "candidates/rust/py_bridge.c",
                f"{path}:{token.line}: unowned native Python-module import",
            )
            require(
                position + 2 < len(tokens)
                and tokens[position + 1].value == "("
                and tokens[position + 2].kind == "string",
                f"{path}:{token.line}: computed native module import",
            )
            cursor = position + 2
            pieces: list[str] = []
            while cursor < len(tokens) and tokens[cursor].kind == "string":
                pieces.append(tokens[cursor].value)
                cursor += 1
            require(
                cursor < len(tokens) and tokens[cursor].value == ")",
                f"{path}:{token.line}: indirect native module import",
            )
            module = "".join(pieces)
            require(
                module in ALLOWED_RUST_SUPPORT_IMPORTS,
                f"{path}:{token.line}: forbidden native module {module!r}",
            )
            support_imports.append(module)
        if token.value == "include" and position and tokens[position - 1].value == "#":
            require(position + 1 < len(tokens), f"{path}:{token.line}: missing C header")
            cursor = position + 1
            if tokens[cursor].kind == "string":
                header = tokens[cursor].value
            else:
                require(tokens[cursor].value == "<", f"{path}:{token.line}: computed C header")
                cursor += 1
                pieces = []
                while cursor < len(tokens) and tokens[cursor].value != ">":
                    pieces.append(tokens[cursor].value)
                    cursor += 1
                require(cursor < len(tokens), f"{path}:{token.line}: unterminated C header")
                header = "".join(pieces)
            require(header in ALLOWED_C_HEADERS, f"{path}:{token.line}: foreign C header {header!r}")
            headers.append(header)
        if token.value == "import" and position and tokens[position - 1].value == "@":
            require(
                kind == "zig"
                and position + 3 < len(tokens)
                and tokens[position + 1].value == "("
                and tokens[position + 2].kind == "string"
                and tokens[position + 3].value == ")",
                f"{path}:{token.line}: computed Zig dependency",
            )
            value = tokens[position + 2].value
            require(value == "std", f"{path}:{token.line}: foreign Zig package {value!r}")
            zig_imports.append(value)
        if token.value in {"cImport", "cInclude", "DynLib"}:
            raise AuditError(f"{path}:{token.line}: unowned native loader {token.value!r}")
    if kind == "zig":
        require(zig_imports == ["std"], f"{path}: Zig must use exactly its standard library")
    if family.name != "rust":
        require(not support_imports, f"{path}: unexpected native support imports")
    incompatible_prefixes = {
        "c_vm": ("rebar_zig_", "rebar_compile", "rebar_match"),
        "rust": ("rebar_zig_", "_vm_native"),
        "zig": ("_rust_bridge", "_rust_engine", "_vm_native"),
    }
    bad_owners = sorted(
        name
        for name in identifiers
        if any(
            name.startswith(prefix)
            for prefix in incompatible_prefixes.get(family.name, ())
        )
        or (
            family.name == "zig"
            and name.startswith("rebar_")
            and not name.startswith("rebar_zig_")
        )
    )
    require(not bad_owners, f"{path}: cross-family native symbols {bad_owners!r}")
    return {
        "identifiers": identifiers,
        "native_support_imports": sorted(set(support_imports)),
        "c_headers": sorted(set(headers)),
        "zig_standard_library_imports": zig_imports,
        "compatibility_display_names": sorted(
            {
                token.value
                for token in tokens
                if token.kind == "string" and token.value == "_sre.SRE_Scanner"
            }
        ),
    }


def _cstring(data: bytes, offset: int, context: str) -> str:
    require(0 <= offset < len(data), f"{context}: string offset outside string table")
    finish = data.find(b"\x00", offset)
    require(finish >= 0, f"{context}: unterminated dynamic string")
    try:
        return data[offset:finish].decode("utf-8", "strict")
    except UnicodeDecodeError as error:
        raise AuditError(f"{context}: invalid dynamic string") from error


def _within(offset: int, size: int, maximum: int, context: str) -> None:
    require(
        0 <= offset <= maximum and 0 <= size <= maximum - offset,
        f"{context}: offset or size outside the native file",
    )


def inspect_elf(data: bytes, context: str) -> dict[str, object]:
    require(len(data) >= ELF_HEADER.size, f"{context}: truncated ELF header")
    header = ELF_HEADER.unpack_from(data)
    ident = header[0]
    require(ident[:4] == b"\x7fELF", f"{context}: not an ELF file")
    require(ident[4] == 2, f"{context}: native library must be 64-bit")
    require(ident[5] == 1, f"{context}: native library must be little-endian")
    require(ident[6] == 1, f"{context}: invalid ELF identification version")
    (
        _,
        file_type,
        machine,
        version,
        _entry,
        program_offset,
        section_offset,
        _flags,
        header_size,
        program_entry_size,
        program_count,
        section_entry_size,
        section_count,
        names_index,
    ) = header
    require(file_type == 3, f"{context}: native artifact is not a shared object")
    require(machine == 62 and version == 1, f"{context}: unexpected native machine")
    require(header_size == ELF_HEADER.size, f"{context}: invalid ELF header size")
    require(
        0 < section_count <= 4096
        and section_entry_size == ELF_SECTION.size
        and names_index < section_count,
        f"{context}: invalid ELF section table",
    )
    _within(
        section_offset,
        section_count * ELF_SECTION.size,
        len(data),
        f"{context}: section table",
    )
    programs: list[tuple[int, ...]] = []
    if program_count:
        require(
            program_count <= 4096 and program_entry_size == ELF_PROGRAM.size,
            f"{context}: invalid ELF program table",
        )
        _within(
            program_offset,
            program_count * ELF_PROGRAM.size,
            len(data),
            f"{context}: program table",
        )
        for index in range(program_count):
            entry = ELF_PROGRAM.unpack_from(data, program_offset + index * ELF_PROGRAM.size)
            if entry[0] in {1, 2}:
                _within(entry[2], entry[5], len(data), f"{context}: program segment")
                if entry[0] == 1:
                    require(entry[5] <= entry[6], f"{context}: invalid load segment")
            programs.append(entry)
    sections = [
        ELF_SECTION.unpack_from(data, section_offset + index * ELF_SECTION.size)
        for index in range(section_count)
    ]
    for index, section in enumerate(sections):
        if section[1] != 8:
            _within(section[4], section[5], len(data), f"{context}: section {index}")
    names = sections[names_index]
    require(names[1] == 3, f"{context}: invalid section-name table")
    name_table = data[names[4] : names[4] + names[5]]
    by_name: dict[str, tuple[int, ...]] = {}
    for index, section in enumerate(sections):
        if index == 0:
            continue
        name = _cstring(name_table, section[0], f"{context}: section name")
        require(name not in by_name, f"{context}: duplicate ELF section {name!r}")
        by_name[name] = section
    require(
        all(name in by_name for name in (".dynstr", ".dynsym", ".dynamic")),
        f"{context}: incomplete native dynamic information",
    )
    strings_section = by_name[".dynstr"]
    symbols_section = by_name[".dynsym"]
    dynamic_section = by_name[".dynamic"]
    string_index = sections.index(strings_section)
    require(strings_section[1] == 3, f"{context}: invalid dynamic string section")
    require(
        symbols_section[1] == 11
        and symbols_section[6] == string_index
        and symbols_section[9] == ELF_SYMBOL.size
        and symbols_section[5] % ELF_SYMBOL.size == 0,
        f"{context}: invalid dynamic symbol table",
    )
    require(
        dynamic_section[1] == 6
        and dynamic_section[6] == string_index
        and dynamic_section[9] == ELF_DYNAMIC.size
        and dynamic_section[5] % ELF_DYNAMIC.size == 0,
        f"{context}: invalid dynamic dependency table",
    )
    if programs:
        require(
            any(
                entry[0] == 2
                and entry[2] <= dynamic_section[4]
                and dynamic_section[4] + dynamic_section[5] <= entry[2] + entry[5]
                for entry in programs
            ),
            f"{context}: dynamic section is outside its program segment",
        )
    strings = data[strings_section[4] : strings_section[4] + strings_section[5]]
    exports: set[str] = set()
    undefined: set[str] = set()
    for index in range(symbols_section[5] // ELF_SYMBOL.size):
        entry = ELF_SYMBOL.unpack_from(
            data, symbols_section[4] + index * ELF_SYMBOL.size
        )
        name_offset, information, _visibility, section_index, _value, _size = entry
        if name_offset == 0:
            continue
        name = _cstring(strings, name_offset, f"{context}: native symbol")
        binding = information >> 4
        if section_index == 0:
            undefined.add(name)
        elif binding in {1, 2}:
            exports.add(name)
    needed: list[str] = []
    runpaths: list[str] = []
    rpaths: list[str] = []
    sonames: list[str] = []
    null_found = False
    for index in range(dynamic_section[5] // ELF_DYNAMIC.size):
        tag, value = ELF_DYNAMIC.unpack_from(
            data, dynamic_section[4] + index * ELF_DYNAMIC.size
        )
        if tag == 0:
            null_found = True
            continue
        require(not null_found, f"{context}: dynamic entry occurs after terminator")
        if tag in {1, 14, 15, 29}:
            name = _cstring(strings, value, f"{context}: dynamic dependency")
            target = {1: needed, 14: sonames, 15: rpaths, 29: runpaths}[tag]
            target.append(name)
    require(null_found, f"{context}: missing dynamic table terminator")
    require(
        len(needed) == len(set(needed)),
        f"{context}: duplicate dynamic library dependency",
    )
    require(
        len(runpaths) <= 1 and len(rpaths) <= 1 and len(sonames) <= 1,
        f"{context}: duplicate native search path or library name",
    )
    require(not rpaths, f"{context}: legacy or external native search path")
    return {
        "exports": exports,
        "undefined": undefined,
        "needed": tuple(sorted(needed)),
        "runpath": runpaths[0] if runpaths else None,
        "soname": sonames[0] if sonames else None,
    }


def inspect_artifact(data: bytes, specification: Artifact) -> dict[str, object]:
    record = inspect_elf(data, specification.path)
    require(
        record["needed"] == tuple(sorted(specification.needed)),
        f"{specification.path}: unowned or missing native dependency",
    )
    require(
        record["runpath"] == specification.runpath,
        f"{specification.path}: native search path is not the exact owner",
    )
    require(
        record["soname"] == specification.soname,
        f"{specification.path}: unexpected native library identity",
    )
    missing_exports = sorted(set(specification.required_exports) - record["exports"])
    require(not missing_exports, f"{specification.path}: missing native exports {missing_exports!r}")
    missing_imports = sorted(set(specification.required_undefined) - record["undefined"])
    require(not missing_imports, f"{specification.path}: missing owned native calls {missing_imports!r}")
    forbidden_symbols = sorted(
        symbol
        for symbol in record["undefined"]
        if symbol in FORBIDDEN_NATIVE_IDENTIFIERS
        or symbol.split("@", 1)[0] in FORBIDDEN_NATIVE_IDENTIFIERS
        or symbol.casefold().startswith(
            ("pcre", "onig_", "oniguruma", "hs_scan", "hs_compile", "re2_", "_sre")
        )
    )
    require(not forbidden_symbols, f"{specification.path}: forbidden native calls {forbidden_symbols!r}")
    if specification.path.endswith("_rust_engine.so"):
        require(
            not any(name.startswith("rebar_zig_") for name in record["exports"]),
            f"{specification.path}: cross-family Zig executor",
        )
    if specification.path.endswith("_zig_probe.so"):
        require(
            not any(
                name.startswith("rebar_") and not name.startswith("rebar_zig_")
                for name in record["exports"]
            ),
            f"{specification.path}: cross-family Rust executor",
        )
    return {
        "path": specification.path,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "required_exports": list(specification.required_exports),
        "verified_owned_imports": list(specification.required_undefined),
        "needed": list(record["needed"]),
        "runpath": record["runpath"],
        "soname": record["soname"],
        "native_code_loaded": False,
        "source_to_binary_provenance": "NOT ESTABLISHED",
        "tracked_or_reproducibly_built": "NOT ESTABLISHED",
    }


def _reject_dependency_sections(value: object, context: str, chain: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(isinstance(key, str), f"{context}: invalid manifest key")
            folded = key.casefold()
            require(
                not folded.endswith("dependencies")
                and folded not in {"patch", "replace", "workspace"},
                f"{context}: external dependency section {'.'.join((*chain, key))!r}",
            )
            _reject_dependency_sections(child, context, (*chain, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_dependency_sections(child, context, (*chain, str(index)))


def inspect_cargo(manifest_text: str, lock_text: str) -> dict[str, object]:
    try:
        manifest = tomllib.loads(manifest_text)
        lock = tomllib.loads(lock_text)
    except (tomllib.TOMLDecodeError, ValueError, RecursionError) as error:
        raise AuditError(f"Rust dependency metadata is invalid: {error}") from error
    _reject_dependency_sections(manifest, "candidates/rust/Cargo.toml")
    require(
        isinstance(manifest.get("package"), dict)
        and manifest["package"].get("name") == "rebar-rust-continuation"
        and manifest["package"].get("version") == "0.1.0"
        and manifest["package"].get("publish") is False,
        "Rust manifest does not describe the single owned unpublished engine",
    )
    require(
        isinstance(manifest.get("lib"), dict)
        and manifest["lib"].get("crate-type") == ["cdylib"],
        "Rust engine must build its own native shared library",
    )
    packages = lock.get("package")
    require(
        lock.get("version") == 4
        and isinstance(packages, list)
        and len(packages) == 1,
        "Rust lock must contain exactly one first-party package",
    )
    package = packages[0]
    require(
        isinstance(package, dict)
        and package.get("name") == "rebar-rust-continuation"
        and package.get("version") == "0.1.0"
        and set(package) == {"name", "version"},
        "Rust lock contains a registry, replacement, or external dependency",
    )
    require(set(lock) == {"version", "package"}, "Rust lock contains unowned metadata")
    return {
        "package": "rebar-rust-continuation",
        "package_count": 1,
        "external_dependency_count": 0,
        "third_party_regex_packages": 0,
    }


def inspect_project(manifest_text: str, lock_text: str) -> dict[str, object]:
    try:
        manifest = tomllib.loads(manifest_text)
        lock = tomllib.loads(lock_text)
    except (tomllib.TOMLDecodeError, ValueError, RecursionError) as error:
        raise AuditError(f"Python dependency metadata is invalid: {error}") from error
    project = manifest.get("project")
    require(
        isinstance(project, dict)
        and project.get("name") == "rebar-experiment"
        and project.get("dependencies") == [],
        "Python project must have zero external production dependencies",
    )
    require(
        "optional-dependencies" not in project,
        "Python project has unowned optional production dependencies",
    )
    packages = lock.get("package")
    require(
        isinstance(packages, list)
        and len(packages) == 1
        and isinstance(packages[0], dict)
        and packages[0].get("name") == "rebar-experiment"
        and packages[0].get("source") == {"virtual": "."}
        and "dependencies" not in packages[0],
        "Python lock must contain only the first-party local project",
    )
    return {
        "package": "rebar-experiment",
        "package_count": 1,
        "external_dependency_count": 0,
        "third_party_regex_packages": 0,
        "shared_semantic_engine": False,
    }


def inspect_architecture(
    family: Family,
    python_records: dict[str, PythonOwnershipVisitor],
    native_records: dict[str, dict[str, object]],
) -> dict[str, str]:
    if family.name == "python_ast":
        visitor = python_records["candidates/ast_candidate.py"]
        require(
            {"parse"} <= visitor.class_methods.get("_Parser", set())
            and {"run"} <= visitor.class_methods.get("_Engine", set())
            and "compile" in visitor.top_level_functions,
            "Python tree candidate lacks its own parser, compiler entry and executor",
        )
        return {
            "parser": "candidates/ast_candidate.py:_Parser.parse",
            "compiler": "candidates/ast_candidate.py:compile",
            "executor": "candidates/ast_candidate.py:_Engine.run",
        }
    if family.name == "c_vm":
        visitor = python_records["candidates/vm_candidate.py"]
        identifiers = native_records["candidates/_vm_native.c"]["identifiers"]
        require(
            {"parse"} <= visitor.class_methods.get("_BytecodeParser", set())
            and {"build", "emit"} <= visitor.class_methods.get("_BytecodeCompiler", set())
            and {"execute", "native_build", "native_match"} <= identifiers,
            "C virtual machine lacks its own parser, compiler or C executor",
        )
        return {
            "parser": "candidates/vm_candidate.py:_BytecodeParser.parse",
            "compiler": "candidates/vm_candidate.py:_BytecodeCompiler.build",
            "executor": "candidates/_vm_native.c:execute",
        }
    if family.name == "rust":
        identifiers = native_records["candidates/rust/src/lib.rs"]["identifiers"]
        require(
            {
                "Parser",
                "Compiler",
                "parse",
                "run_program",
                "rebar_compile",
                "rebar_match",
            }
            <= identifiers,
            "Rust candidate lacks its own parser, compiler or Rust executor",
        )
        return {
            "parser": "candidates/rust/src/lib.rs:Parser.parse",
            "compiler": "candidates/rust/src/lib.rs:Compiler",
            "executor": "candidates/rust/src/lib.rs:run_program",
        }
    identifiers = native_records["candidates/zig/mini_regex.zig"]["identifiers"]
    require(
        {
            "Parser",
            "Compiler",
            "compileOwned",
            "runBytecode",
            "rebar_zig_compile",
            "rebar_zig_match_wide",
        }
        <= identifiers,
        "Zig candidate lacks its own parser, compiler or Zig executor",
    )
    return {
        "parser": "candidates/zig/mini_regex.zig:Parser",
        "compiler": "candidates/zig/mini_regex.zig:Compiler",
        "executor": "candidates/zig/mini_regex.zig:runBytecode",
    }


def fixture_elf(
    *,
    needed: tuple[str, ...] = ("libc.so.6",),
    exports: tuple[str, ...] = ("PyInit__vm_native",),
    undefined: tuple[str, ...] = (),
    runpath: str | None = None,
    soname: str | None = None,
) -> bytes:
    dynamic_strings = bytearray(b"\x00")

    def add_string(value: str) -> int:
        offset = len(dynamic_strings)
        dynamic_strings.extend(value.encode("utf-8"))
        dynamic_strings.append(0)
        return offset

    symbol_records = [ELF_SYMBOL.pack(0, 0, 0, 0, 0, 0)]
    for value in exports:
        symbol_records.append(ELF_SYMBOL.pack(add_string(value), 0x12, 0, 1, 0, 0))
    for value in undefined:
        symbol_records.append(ELF_SYMBOL.pack(add_string(value), 0x12, 0, 0, 0, 0))
    entries = [(1, add_string(value)) for value in needed]
    if soname is not None:
        entries.append((14, add_string(soname)))
    if runpath is not None:
        entries.append((29, add_string(runpath)))
    entries.append((0, 0))
    dynamic = b"".join(ELF_DYNAMIC.pack(tag, value) for tag, value in entries)
    names = b"\x00.shstrtab\x00.dynstr\x00.dynsym\x00.dynamic\x00"

    def name_offset(value: bytes) -> int:
        offset = names.find(value + b"\x00")
        require(offset >= 0, "invalid synthetic section name")
        return offset

    blob = bytearray(ELF_HEADER.size + ELF_PROGRAM.size)

    def append(value: bytes, alignment: int = 8) -> tuple[int, int]:
        padding = (-len(blob)) % alignment
        blob.extend(b"\x00" * padding)
        offset = len(blob)
        blob.extend(value)
        return offset, len(value)

    name_at, name_size = append(names, 1)
    string_at, string_size = append(bytes(dynamic_strings), 1)
    symbols_at, symbols_size = append(b"".join(symbol_records))
    dynamic_at, dynamic_size = append(dynamic)
    section_at = (len(blob) + 7) & ~7
    blob.extend(b"\x00" * (section_at - len(blob)))
    sections = (
        ELF_SECTION.pack(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ELF_SECTION.pack(
            name_offset(b".shstrtab"), 3, 0, 0, name_at, name_size, 0, 0, 1, 0
        ),
        ELF_SECTION.pack(
            name_offset(b".dynstr"), 3, 0, 0, string_at, string_size, 0, 0, 1, 0
        ),
        ELF_SECTION.pack(
            name_offset(b".dynsym"),
            11,
            0,
            0,
            symbols_at,
            symbols_size,
            2,
            1,
            8,
            ELF_SYMBOL.size,
        ),
        ELF_SECTION.pack(
            name_offset(b".dynamic"),
            6,
            0,
            0,
            dynamic_at,
            dynamic_size,
            2,
            0,
            8,
            ELF_DYNAMIC.size,
        ),
    )
    blob.extend(b"".join(sections))
    ident = b"\x7fELF" + bytes((2, 1, 1, 0)) + b"\x00" * 8
    ELF_HEADER.pack_into(
        blob,
        0,
        ident,
        3,
        62,
        1,
        0,
        ELF_HEADER.size,
        section_at,
        0,
        ELF_HEADER.size,
        ELF_PROGRAM.size,
        1,
        ELF_SECTION.size,
        len(sections),
        1,
    )
    ELF_PROGRAM.pack_into(
        blob,
        ELF_HEADER.size,
        2,
        4,
        dynamic_at,
        0,
        0,
        dynamic_size,
        dynamic_size,
        8,
    )
    return bytes(blob)


def _self_test_checks() -> tuple[int, int]:
    positives = 0
    attacks = 0

    def accept(function: object, *args: object) -> None:
        nonlocal positives
        function(*args)
        positives += 1

    def reject(function: object, *args: object) -> None:
        nonlocal attacks
        try:
            function(*args)
        except (AuditError, ValueError, TypeError, UnicodeError, struct.error):
            attacks += 1
            return
        raise AuditError(
            f"hostile self-test was accepted: {function.__name__}: {args!r}"
        )

    python_ast = FAMILY_BY_NAME["python_ast"]
    c_vm = FAMILY_BY_NAME["c_vm"]
    rust = FAMILY_BY_NAME["rust"]
    zig = FAMILY_BY_NAME["zig"]
    clean_ast = 'import enum\nvalue = "re.NOFLAG"\ndisplay = "_sre.SRE_Scanner"\n'
    clean_c_python = "from candidates import _vm_native\n"
    clean_rust_python = "from candidates import _rust_bridge\n"
    clean_zig_python = (
        "import ctypes\nimport os\nfrom candidates import _zig_bridge\n"
        "class _Native:\n"
        "    def __init__(self):\n"
        '        path = os.path.join(os.path.dirname(__file__), "_zig_probe.so")\n'
        "        self.library = ctypes.CDLL(path)\n"
    )
    accept(inspect_python, clean_ast, python_ast, "fixture.py")
    accept(inspect_python, clean_c_python, c_vm, "fixture.py")
    accept(inspect_python, clean_rust_python, rust, "fixture.py")
    accept(inspect_python, clean_zig_python, zig, "fixture.py")
    for family, base in (
        (python_ast, clean_ast),
        (c_vm, clean_c_python),
        (rust, clean_rust_python),
        (zig, clean_zig_python),
    ):
        for payload in (
            "import re\n",
            "import re as trusted\n",
            "from re import compile\n",
            "from re._compiler import compile\n",
            "import _sre\n",
            "import regex\n",
            "import re2\n",
            "import pcre2\n",
            "import importlib\n",
            "from importlib import import_module\n",
            "import sys\n",
            "import builtins\n",
            "import subprocess\n",
            "import multiprocessing\n",
            "import runpy\n",
            "import cffi\n",
            "__import__('r' + 'e')\n",
            "eval('import re')\n",
            "exec('import re')\n",
            "globals()['__builtins__']\n",
            "locals()['__import__']\n",
            "getattr(object(), '__im' + 'port__')\n",
            "getattr(object(), '__glo' + 'bals__')\n",
            "object().__globals__\n",
            "os.environ['PYTEST_CURRENT_TEST']\n",
            "os.getenv('REBAR_BENCHMARK')\n",
            "os.system('candidate')\n",
        ):
            reject(inspect_python, base + payload, family, "fixture.py")
    reject(inspect_python, "from candidates import _rust_bridge\n", c_vm, "fixture.py")
    reject(inspect_python, "from candidates import _zig_bridge\n", rust, "fixture.py")
    reject(inspect_python, "from candidates import _vm_native\n", python_ast, "fixture.py")
    reject(inspect_python, "from candidates import *\n", rust, "fixture.py")
    reject(inspect_python, "from candidates.ast_candidate import compile\n", rust, "fixture.py")
    reject(
        inspect_python,
        clean_zig_python.replace("_zig_probe.so", "_rust_engine.so"),
        zig,
        "fixture.py",
    )
    reject(
        inspect_python,
        clean_zig_python.replace("ctypes.CDLL(path)", 'ctypes.CDLL("libpcre2.so")'),
        zig,
        "fixture.py",
    )
    reject(
        inspect_python,
        clean_zig_python + "ctypes.PyDLL(path)\n",
        zig,
        "fixture.py",
    )
    reject(inspect_python, "import ctypes\n", python_ast, "fixture.py")
    safe_native = (
        '#include <Python.h>\n'
        '// PyImport_ImportModule("re") is a comment, not executable code.\n'
        'const char *display = "_sre.SRE_Scanner";\n'
        'const char *representation = "re.NOFLAG";\n'
    )
    accept(inspect_native, safe_native, c_vm, "fixture.c", "c")
    accept(
        inspect_native,
        'const std = @import("std");\n',
        zig,
        "fixture.zig",
        "zig",
    )
    accept(
        inspect_native,
        'PyImport_ImportModule("copyreg");\n'
        'PyImport_ImportModule("functools");\n'
        'PyImport_ImportModule("inspect");\n',
        rust,
        "candidates/rust/py_bridge.c",
        "c",
    )
    for payload in (
        'PyImport_ImportModule("re");\n',
        'PyImport_ImportModule("r" "e");\n',
        'PyImport_ImportModule("\\x72\\x65");\n',
        'PyImport_ImportModule("_sre");\n',
        'PyImport_ImportModule("regex");\n',
        'PyImport_ImportModule(module_name);\n',
        "#define FOREIGN PyImport_ImportModule\n",
        'PyImport_Import("re");\n',
        'PyRun_SimpleString("import re");\n',
        'PyEval_EvalCode(code, globals, locals);\n',
        'dlopen("libpcre2.so", 1);\n',
        'dlsym(handle, "pcre2_match");\n',
        "regcomp(pattern, flags);\n",
        "pcre2_compile(pattern);\n",
        "onig_search(pattern);\n",
        "system(command);\n",
        "popen(command, mode);\n",
        '#include <pcre2.h>\n',
        "#include FOREIGN_HEADER\n",
        "/* never finished",
        '"never finished',
    ):
        reject(
            inspect_native,
            safe_native + payload,
            rust,
            "candidates/rust/py_bridge.c",
            "c",
        )
    for payload in (
        'const external = @import("regex");\n',
        'const external = @import("pcre2");\n',
        "const external = @import(package);\n",
        'const external = @cImport({ @cInclude("pcre2.h"); });\n',
        "const external = std.DynLib.open(path);\n",
        "fn wrapper() void { rebar_match(); }\n",
    ):
        reject(
            inspect_native,
            'const std = @import("std");\n' + payload,
            zig,
            "fixture.zig",
            "zig",
        )
    for path in (
        "",
        "/etc/passwd",
        "../candidate.py",
        "candidates/../secret",
        "candidates//secret",
        "./candidates/ast_candidate.py",
        "candidates\\secret.py",
        "candidates/\x00secret.py",
        ".git/config",
        "candidates/evidence/result.json",
        "oracle/hidden-holdout/cases.json",
        "benchmarks/input.json",
        "performance/results.json",
    ):
        reject(checked_relative, path)
    for path in (
        "GOAL.md",
        "pyproject.toml",
        "uv.lock",
        "candidates/ast_candidate.py",
        "candidates/rust/src/lib.rs",
        "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md",
    ):
        accept(checked_relative, path)
    clean_manifest = (
        '[package]\nname = "rebar-rust-continuation"\n'
        'version = "0.1.0"\npublish = false\n'
        '[lib]\ncrate-type = ["cdylib"]\n'
    )
    clean_lock = (
        "version = 4\n[[package]]\n"
        'name = "rebar-rust-continuation"\nversion = "0.1.0"\n'
    )
    accept(inspect_cargo, clean_manifest, clean_lock)
    for addition in (
        '[dependencies]\nregex = "1"\n',
        "[dependencies]\n",
        '[dev-dependencies]\nregex = "1"\n',
        '[build-dependencies]\nregex = "1"\n',
        '[target."cfg(unix)".dependencies]\nregex = "1"\n',
        '[workspace.dependencies]\nregex = "1"\n',
        '[patch.crates-io]\nregex = { path = "../regex" }\n',
        '[replace]\n"regex:1.0.0" = { path = "../regex" }\n',
    ):
        reject(inspect_cargo, clean_manifest + addition, clean_lock)
    for changed_lock in (
        clean_lock + '\n[[package]]\nname = "regex"\nversion = "1.0.0"\n',
        clean_lock + 'source = "registry+https://example.invalid"\n',
        clean_lock + 'dependencies = ["regex"]\n',
        clean_lock.replace("version = 4", "version = 3", 1),
    ):
        reject(inspect_cargo, clean_manifest, changed_lock)
    project_manifest = (
        '[project]\nname = "rebar-experiment"\n'
        'version = "0.0.0"\ndependencies = []\n'
    )
    project_lock = (
        "version = 1\n[[package]]\n"
        'name = "rebar-experiment"\nversion = "0.0.0"\n'
        'source = { virtual = "." }\n'
    )
    accept(inspect_project, project_manifest, project_lock)
    reject(
        inspect_project,
        project_manifest.replace("dependencies = []", 'dependencies = ["regex"]'),
        project_lock,
    )
    reject(
        inspect_project,
        project_manifest,
        project_lock + '\n[[package]]\nname = "regex"\nversion = "1"\n',
    )
    c_artifact = c_vm.artifacts[0]
    clean_elf = fixture_elf()
    accept(inspect_artifact, clean_elf, c_artifact)
    rust_bridge = fixture_elf(
        needed=("_rust_engine.so", "libc.so.6"),
        exports=("PyInit__rust_bridge",),
        undefined=("rebar_compile", "rebar_match"),
        runpath="$ORIGIN",
    )
    accept(inspect_artifact, rust_bridge, rust.artifacts[0])
    rust_engine = fixture_elf(
        needed=("libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2"),
        exports=rust.artifacts[1].required_exports,
    )
    accept(inspect_artifact, rust_engine, rust.artifacts[1])
    zig_bridge = fixture_elf(
        needed=("_zig_probe.so", "libc.so.6"),
        exports=("PyInit__zig_bridge",),
        undefined=("rebar_zig_compile_guarded", "rebar_zig_match_wide"),
        runpath="$ORIGIN",
    )
    accept(inspect_artifact, zig_bridge, zig.artifacts[0])
    zig_engine = fixture_elf(
        needed=("libc.so.6",),
        exports=zig.artifacts[1].required_exports,
        soname="_zig_probe.so",
    )
    accept(inspect_artifact, zig_engine, zig.artifacts[1])
    for dangerous in (
        b"",
        b"not ELF",
        clean_elf[: ELF_HEADER.size - 1],
        clean_elf[: ELF_HEADER.size + 7],
        clean_elf[: len(clean_elf) // 2],
    ):
        reject(inspect_artifact, dangerous, c_artifact)
    for offset, value in (
        (0, 0),
        (4, 1),
        (5, 2),
        (6, 0),
        (16, 2),
        (18, 3),
    ):
        changed = bytearray(clean_elf)
        changed[offset] = value
        reject(inspect_artifact, bytes(changed), c_artifact)
    for changed in (
        fixture_elf(needed=("libc.so.6", "libpcre2-8.so.0")),
        fixture_elf(needed=("libc.so.6", "libc.so.6")),
        fixture_elf(needed=("_rust_engine.so",)),
        fixture_elf(needed=("_zig_probe.so",)),
        fixture_elf(exports=("PyInit__rust_bridge",)),
        fixture_elf(undefined=("regcomp",)),
        fixture_elf(undefined=("pcre2_match",)),
        fixture_elf(runpath="/tmp/unowned"),
        fixture_elf(runpath="$ORIGIN/../foreign"),
        fixture_elf(soname="foreign.so"),
    ):
        reject(inspect_artifact, changed, c_artifact)
    for changed in (
        fixture_elf(
            needed=("_zig_probe.so", "libc.so.6"),
            exports=("PyInit__rust_bridge",),
            undefined=("rebar_compile", "rebar_match"),
            runpath="$ORIGIN",
        ),
        fixture_elf(
            needed=("_rust_engine.so", "libc.so.6"),
            exports=("PyInit__rust_bridge",),
            undefined=("rebar_compile", "rebar_match"),
            runpath="/tmp",
        ),
        fixture_elf(
            needed=("_rust_engine.so", "libc.so.6"),
            exports=("PyInit__rust_bridge",),
            undefined=("rebar_compile",),
            runpath="$ORIGIN",
        ),
    ):
        reject(inspect_artifact, changed, rust.artifacts[0])
    for changed in (
        fixture_elf(
            needed=("libc.so.6",),
            exports=zig.artifacts[1].required_exports,
            soname="_rust_engine.so",
        ),
        fixture_elf(
            needed=("libc.so.6",),
            exports=(*zig.artifacts[1].required_exports, "rebar_match"),
            soname="_zig_probe.so",
        ),
    ):
        reject(inspect_artifact, changed, zig.artifacts[1])
    owners: dict[str, str] = {}
    for family in FAMILIES:
        for owner in family.owners:
            require(owner.path not in owners, "candidate semantic source is shared")
            owners[owner.path] = family.name
    positives += 1
    require(positives >= 20 and attacks >= 145, "insufficient hostile ownership controls")
    return positives, attacks


def run_self_test() -> dict[str, object]:
    effects = {
        "candidate_imports": 0,
        "candidate_workers": 0,
        "clock_samples": 0,
        "file_reads": 0,
        "file_writes": 0,
        "hidden_cases_read": 0,
        "native_libraries_loaded": 0,
        "performance_files_read": 0,
        "reference_workers": 0,
    }
    before_candidates = frozenset(
        name for name in sys.modules if name == "candidates" or name.startswith("candidates.")
    )
    replacements: list[tuple[object, str, object]] = []

    def forbid(category: str):
        def blocked(*_args: object, **_kwargs: object) -> object:
            effects[category] += 1
            raise AuditError(f"self-test attempted external effect: {category}")

        return blocked

    def replace(owner: object, name: str, category: str) -> None:
        if hasattr(owner, name):
            replacements.append((owner, name, getattr(owner, name)))
            setattr(owner, name, forbid(category))

    for owner, name in (
        (builtins, "open"),
        (io, "open"),
        (os, "open"),
        (os, "stat"),
        (os, "lstat"),
        (os, "scandir"),
    ):
        replace(owner, name, "file_reads")
    for owner, name in ((os, "system"), (os, "popen"), (os, "fork")):
        replace(owner, name, "candidate_workers")
    for name in (
        "time",
        "time_ns",
        "monotonic",
        "monotonic_ns",
        "perf_counter",
        "perf_counter_ns",
        "process_time",
        "process_time_ns",
        "thread_time",
        "thread_time_ns",
    ):
        replace(time, name, "clock_samples")
    try:
        positives, attacks = _self_test_checks()
        after_candidates = frozenset(
            name for name in sys.modules if name == "candidates" or name.startswith("candidates.")
        )
        effects["candidate_imports"] = len(after_candidates - before_candidates)
        require(
            not any(effects.values()),
            f"source-only ownership self-test caused external effects: {effects!r}",
        )
    finally:
        for owner, name, original in reversed(replacements):
            setattr(owner, name, original)
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "python": ".".join(str(value) for value in sys.version_info[:3]),
        "positive_controls": positives,
        "rejected_attack_controls": attacks,
        "family_count": len(FAMILIES),
        "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        **effects,
    }


def parse_owner_pins(values: list[str], allowed_paths: set[str]) -> dict[str, str]:
    pins: dict[str, str] = {}
    for entry in values:
        require(entry.count("=") == 1, "owner pin must have exactly PATH=SHA256 form")
        path, digest = entry.split("=", 1)
        checked_relative(path)
        require(path in allowed_paths, f"owner pin is outside the selected frozen closure: {path}")
        require(path not in pins, f"duplicate owner pin: {path}")
        pins[path] = valid_sha256(digest, f"{path} owner pin")
    return pins


def _decode_source(data: bytes, path: str) -> str:
    require(b"\x00" not in data, f"{path}: source contains a NUL byte")
    try:
        return data.decode("utf-8", "strict")
    except UnicodeDecodeError as error:
        raise AuditError(f"{path}: source is not valid UTF-8") from error


def run_verify(arguments: argparse.Namespace) -> dict[str, object]:
    require(
        tuple(sys.version_info[:3]) == PINNED_PYTHON,
        "run the audit with the pinned CPython 3.14.6 interpreter",
    )
    selected = (
        (FAMILY_BY_NAME[arguments.family],)
        if arguments.family is not None
        else FAMILIES
    )
    owner_set: set[str] = set()
    for family in FAMILIES:
        for owner in family.owners:
            require(owner.path not in owner_set, f"shared semantic owner: {owner.path}")
            owner_set.add(owner.path)
    allowed_paths = {
        "GOAL.md",
        "pyproject.toml",
        "uv.lock",
        "tools/audit_candidate_independence_v1.py",
        "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md",
    }
    for family in selected:
        allowed_paths.update(owner.path for owner in family.owners)
        allowed_paths.update(artifact.path for artifact in family.artifacts)
    expected = parse_owner_pins(arguments.expect_owner_sha256, allowed_paths)
    root = Path(__file__).resolve(strict=True).parent.parent
    source_cache: dict[str, tuple[bytes, str]] = {}

    def owned(path: str, maximum: int = MAX_SOURCE_BYTES) -> tuple[bytes, str]:
        require(path in allowed_paths, f"read outside the fixed static-audit closure: {path}")
        if path not in source_cache:
            source_cache[path] = read_owned_file(root, path, maximum)
        content, digest = source_cache[path]
        if path in expected:
            require(digest == expected[path], f"{path}: externally pinned owner changed")
        return content, digest

    goal, goal_digest = owned("GOAL.md")
    require(goal_digest == GOAL_SHA256, "immutable objective SHA-256 mismatch")
    require(goal.startswith(b"/goal "), "immutable objective prefix mismatch")
    source, source_digest = owned("tools/audit_candidate_independence_v1.py")
    protocol, protocol_digest = owned("oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md")
    if arguments.source_sha256 is not None:
        require(
            source_digest == valid_sha256(arguments.source_sha256, "audit-source pin"),
            "frozen independence audit source SHA-256 mismatch",
        )
    if arguments.protocol_sha256 is not None:
        require(
            protocol_digest == valid_sha256(arguments.protocol_sha256, "audit-protocol pin"),
            "frozen independence audit protocol SHA-256 mismatch",
        )
    require(bool(source) and bool(protocol), "frozen audit source or protocol is empty")
    project_manifest, _ = owned("pyproject.toml")
    project_lock, _ = owned("uv.lock")
    project_record = inspect_project(
        _decode_source(project_manifest, "pyproject.toml"),
        _decode_source(project_lock, "uv.lock"),
    )
    family_results: list[dict[str, object]] = []
    compiler_results: dict[str, dict[str, object]] = {}
    for family in selected:
        python_records: dict[str, PythonOwnershipVisitor] = {}
        native_records: dict[str, dict[str, object]] = {}
        owner_records: list[dict[str, object]] = []
        cargo_manifest: str | None = None
        cargo_lock: str | None = None
        for owner in family.owners:
            content, digest = owned(owner.path)
            text = _decode_source(content, owner.path)
            record: dict[str, object] = {
                "path": owner.path,
                "kind": owner.kind,
                "size_bytes": len(content),
                "sha256": digest,
                "externally_pinned": owner.path in expected,
            }
            if owner.kind == "python":
                visitor = inspect_python(text, family, owner.path)
                python_records[owner.path] = visitor
                record["direct_python_imports"] = sorted(visitor.imports)
                record["owned_bridge_imports"] = sorted(visitor.bridge_imports)
                if family.name == "zig":
                    record["owned_file_anchored_zig_loader_count"] = visitor.zig_loaders
            elif owner.kind in {"c", "rust", "zig"}:
                inspected = inspect_native(text, family, owner.path, owner.kind)
                native_records[owner.path] = inspected
                record["native_support_imports"] = inspected["native_support_imports"]
                record["c_headers"] = inspected["c_headers"]
                record["zig_standard_library_imports"] = inspected[
                    "zig_standard_library_imports"
                ]
                record["compatibility_display_names"] = inspected[
                    "compatibility_display_names"
                ]
            elif owner.kind == "cargo_manifest":
                cargo_manifest = text
            elif owner.kind == "cargo_lock":
                cargo_lock = text
            owner_records.append(record)
        architecture = inspect_architecture(family, python_records, native_records)
        cargo_record: dict[str, object] | None = None
        if family.name == "rust":
            require(
                cargo_manifest is not None and cargo_lock is not None,
                "Rust first-party dependency closure is incomplete",
            )
            cargo_record = inspect_cargo(cargo_manifest, cargo_lock)
            for label, pin in (("rustc", RUSTC_PIN), ("cargo", CARGO_PIN)):
                if label not in compiler_results:
                    compiler_results[label] = hash_pinned_tool(pin)
        if family.name == "zig" and "zig" not in compiler_results:
            compiler_results["zig"] = hash_pinned_tool(ZIG_PIN)
        artifact_records = []
        for artifact in family.artifacts:
            data, digest = owned(artifact.path, MAX_BINARY_BYTES)
            inspected = inspect_artifact(data, artifact)
            require(inspected["sha256"] == digest, f"{artifact.path}: inconsistent native SHA-256")
            inspected["externally_pinned"] = artifact.path in expected
            artifact_records.append(inspected)
        support_imports = sorted(
            {
                module
                for record in native_records.values()
                for module in record["native_support_imports"]
            }
        )
        family_record: dict[str, object] = {
            "name": family.name,
            "architecture": family.architecture,
            "static_independence": "PASS",
            "semantic_owners": architecture,
            "source_owners": owner_records,
            "local_untracked_native_artifacts": artifact_records,
            "direct_native_support_imports": support_imports,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "source_to_binary_provenance": "NOT ESTABLISHED",
            "reproducible_clean_clone_build": "NOT ESTABLISHED",
            "candidate_correctness": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "performance": "NOT MEASURED",
        }
        if "inspect" in support_imports:
            family_record["transitive_stdlib_re_import"] = (
                "POSSIBLE: inspect can import re; no production matching call "
                "is established or excluded by this static audit"
            )
        if cargo_record is not None:
            family_record["rust_dependency_lock"] = cargo_record
        family_results.append(family_record)
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "static_independence": "PASS",
        "python": ".".join(str(value) for value in sys.version_info[:3]),
        "goal_sha256": goal_digest,
        "audit_source_sha256": source_digest,
        "audit_protocol_sha256": protocol_digest,
        "family_count": len(family_results),
        "candidate_correctness_qualified_count": 0,
        "pairwise_semantic_owner_overlap_count": 0,
        "project_dependency_lock": project_record,
        "pinned_compilers": compiler_results,
        "families": family_results,
        "externally_pinned_owner_count": len(expected),
        "runtime_no_delegation": "NOT ESTABLISHED",
        "source_to_binary_provenance": "NOT ESTABLISHED",
        "reproducible_clean_clone_build": "NOT ESTABLISHED",
        "candidate_correctness": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "candidate_code_executed": False,
        "native_libraries_loaded": False,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "performance_files_read": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Statically audit independent, from-scratch Python re candidates."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--family", choices=tuple(FAMILY_BY_NAME))
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--expect-owner-sha256", action="append", default=[])
    arguments = parser.parse_args(argv)
    try:
        if arguments.self_test:
            require(
                arguments.family is None
                and arguments.source_sha256 is None
                and arguments.protocol_sha256 is None
                and not arguments.expect_owner_sha256,
                "source-only self-test does not accept owner or source reads",
            )
            result = run_self_test()
        else:
            result = run_verify(arguments)
    except (AuditError, OSError, ValueError, RecursionError, struct.error) as error:
        result = {
            "schema": SELF_TEST_SCHEMA if arguments.self_test else SCHEMA,
            "status": "FAIL",
            "error": str(error),
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
        print(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
