#!/usr/bin/env python3
"""Fail-closed, first-party source/link audit; never execute a regex candidate."""

from __future__ import annotations

import ast
import builtins
import hashlib
import importlib
import io
import json
import os
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
import tomllib


ROOT = "/home/dev-user/src/rebar"
SOURCE = "tools/audit_candidate_runtime_non_delegation_v4.py"
PROTOCOL = "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md"
CONTRACT = "oracle/phase2/runtime-non-delegation-v4.json"
SCHEMA = "rebar-phase2-first-party-runtime-non-delegation-v4"
V2_OWNERS = {
    "tools/audit_candidate_runtime_non_delegation_v2.py":
        "23862f929d7b875cbc16059cb8c1d5c60df7aaba7379e17b57fe943a7d77bf6f",
    "oracle/phase2/RUNTIME-NON-DELEGATION-V2.md":
        "bd8a393d8f385ea9ff55570b1a222a9baed347e9f238ec89534fc46a85127802",
    "oracle/phase2/runtime-non-delegation-v2.json":
        "456439d8b0467b17bd40ee78b5de0f00ace6e0f01e5d558590fabb592dd49729",
}
V2_FAILURE_RECEIPT_PATH = (
    "oracle/phase2/evidence/runtime-non-delegation-v2-actual-source-lexer-failure.json"
)
V2_FAILURE_RECEIPT_SHA256 = (
    "7f30581baf5b47adf7c2d21f0baf2218bc78e14a72aeba90355140519dbadf1a"
)
V2_FAILURE_RECEIPT_BYTES = 411
V2_FAILURE_RECEIPT_DEVICE = 2064
V2_FAILURE_RECEIPT_INODE = 525976
V2_FAILURE_RECEIPT_MODE = 0o600
V3_OWNERS = {
    "tools/audit_candidate_runtime_non_delegation_v3.py":
        "410fd1341eeab2256a1b5b5e8a0d16553f829ae943f655fc7b39f7fc7323f822",
    "oracle/phase2/RUNTIME-NON-DELEGATION-V3.md":
        "c88af5593f3aa3b4ca92ffe626a15490f2a39e500daa5a07e91fed083d7f0440",
    "oracle/phase2/runtime-non-delegation-v3.json":
        "d0d85e301a81ea0c00564f5060bf2ec25dbe2cf7ef7bec35485ff4c6bccf6dd3",
}
V3_FAILURE_RECEIPT_PATH = (
    "oracle/phase2/evidence/runtime-non-delegation-v3-actual-source-audit-failure.json"
)
V3_FAILURE_RECEIPT_SHA256 = (
    "8afe74eeaaa2cab4a1138366d6d2d088de16e31cee5c855827a4efdee97a10db"
)
V3_FAILURE_RECEIPT_BYTES = 20583
V3_FAILURE_RECEIPT_DEVICE = 2064
V3_FAILURE_RECEIPT_INODE = 526043
V3_FAILURE_RECEIPT_MODE = 0o600
PINNED_VERSION = (3, 14, 6)
PINNED_STDLIB = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/"
PINNED_STDLIB_OWNERS = {
    "inspect.py": "9e9793a663928e98cb7b5e300a6fd7a747bb977641eec94c22a6074009aa6c46",
    "tokenize.py": "65ba1bacdc42e768382208ff27f3001ee77d9d61aafba686c67652d22b84b330",
    "warnings.py": "142225786de63c593f1c9abdacf5b4fc0b05dd847f6bed0ebb4b4aa2d4d93b02",
    "_py_warnings.py": "7728580177727fa3b295478cef4777a9d2a364c5cbd809efcea352db31144f85",
    "linecache.py": "692daec68e2a419adf46bafc0eb2f8a2fb36c482183fa1ac47e00fec440f7d7e",
    "enum.py": "fd23a7598fa1104ef892abcd4154d3627283e6361eb7a91cd11dc4a7b6fb3a93",
}
FAMILIES = {
    "c_vm": {
        "bridge": "_vm_native",
        "sources": (
            ("candidates/vm_candidate.py", "python"),
            ("candidates/_vm_native.c", "c"),
        ),
        "binaries": (("candidates/_vm_native.cpython-314-x86_64-linux-gnu.so", "bridge"),),
    },
    "rust": {
        "bridge": "_rust_bridge",
        "sources": (
            ("candidates/rust_candidate.py", "python"),
            ("candidates/rust/py_bridge.c", "c"),
            ("candidates/rust/src/lib.rs", "rust"),
            ("candidates/rust/src/newline.rs", "rust"),
            ("candidates/rust/src/search.rs", "rust"),
            ("candidates/rust/src/stack.rs", "rust"),
            ("candidates/rust/src/unicode_tables.rs", "rust"),
            ("candidates/rust/Cargo.toml", "cargo_manifest"),
            ("candidates/rust/Cargo.lock", "cargo_lock"),
        ),
        "binaries": (
            ("candidates/_rust_engine.so", "engine"),
            ("candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "bridge"),
        ),
    },
    "zig": {
        "bridge": "_zig_bridge",
        "sources": (
            ("candidates/zig_candidate.py", "python"),
            ("candidates/zig/mini_regex.zig", "zig"),
            ("candidates/zig/py_bridge.c", "c"),
        ),
        "binaries": (
            ("candidates/_zig_probe.so", "engine"),
            ("candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so", "bridge"),
        ),
    },
    "cpp": {
        "bridge": "_cpp_bridge",
        "sources": (
            ("candidates/cpp_candidate.py", "python"),
            ("candidates/cpp/engine.hpp", "cpp"),
            ("candidates/cpp/engine.cpp", "cpp"),
            ("candidates/cpp/py_bridge.cpp", "cpp"),
        ),
        "binaries": (),
    },
    "go": {
        "bridge": "_go_bridge",
        "sources": (
            ("candidates/go_candidate.py", "python"),
            ("candidates/go/engine.go", "go"),
            ("candidates/go/py_bridge.c", "c"),
            ("candidates/go/go.mod", "go_mod"),
        ),
        "binaries": (),
    },
    "fortran": {
        "bridge": "_fortran_bridge",
        "sources": (
            ("candidates/fortran_candidate.py", "python"),
            ("candidates/fortran/engine.f90", "fortran"),
            ("candidates/fortran/py_bridge.c", "c"),
        ),
        "binaries": (),
    },
}
SAFE_PYTHON_ROOTS = frozenset({
    "__future__", "copyreg", "enum", "operator", "os", "struct", "sys",
    "types", "unicodedata", "warnings",
})
FORBIDDEN_ROOTS = frozenset({
    "_sre", "ahocorasick", "cffi", "ctypes", "hyperscan", "importlib",
    "onig", "oniguruma", "pcre", "pcre2", "pyre2", "re", "re2", "regex",
    "regex_automata", "regex_lite", "regex_syntax", "regexp", "rure",
    "sre_compile", "sre_constants", "sre_parse",
})
SAFE_NATIVE_IMPORTS = frozenset({"copyreg", "functools", "unicodedata"})
FORBIDDEN_NATIVE_SYMBOLS = frozenset({
    "PyImport_AddModule", "PyImport_ExecCodeModule", "PyImport_GetModule",
    "PyImport_GetModuleDict", "PyImport_Import", "PyImport_ImportModuleLevel",
    "PyImport_ImportModuleLevelObject", "PyRun_AnyFile", "PyRun_SimpleString",
    "PyRun_String", "PyRun_StringFlags", "PyEval_EvalCode", "Py_CompileString",
    "Py_CompileStringExFlags", "GetProcAddress", "LoadLibrary", "LoadLibraryA",
    "LoadLibraryW", "dlopen", "dlmopen", "dlsym", "dlvsym", "execve", "fork",
    "popen", "posix_spawn", "posix_spawnp", "regcomp", "regexec", "system",
})
FORBIDDEN_SYMBOL_PREFIXES = (
    "pcre", "onig", "re2_", "hs_", "hyperscan", "rure_", "tre_",
)
ALLOWED_HEADERS = frozenset({
    "Python.h", "algorithm", "array", "cctype", "cstddef", "cstdint",
    "ctype.h", "exception", "limits", "limits.h", "memory", "new",
    "optional", "stdexcept", "stddef.h", "stdint.h", "stdlib.h", "string",
    "string.h", "string_view", "unordered_map", "utility", "vector",
})
SAFE_SYSTEM_LIBRARIES = frozenset({
    "libc.so.6", "libgcc_s.so.1", "libm.so.6", "ld-linux-x86-64.so.2",
})
SAFE_GO_IMPORTS = frozenset({
    "C", "fmt", "runtime/cgo", "strconv", "sync", "sync/atomic", "unsafe",
})
SAFE_RUST_IMPORT_ROOTS = frozenset({
    "alloc", "core", "crate", "newline", "search", "self", "stack", "std",
    "super", "unicode_tables",
})
FAMILY_PREFIXES = {
    "c_vm": ("vm_", "PyInit__vm_native"),
    "rust": ("rebar_", "PyInit__rust_bridge"),
    "zig": ("rebar_zig_", "PyInit__zig_bridge"),
    "cpp": ("rebar_cpp_", "PyInit__cpp_bridge"),
    "go": ("rebar_go_", "PyInit__go_bridge"),
    "fortran": ("rebar_fortran_", "PyInit__fortran_bridge"),
}
SOURCE_ONLY_MODES = frozenset({"--self-test", "--verify-source"})
MAX_SOURCE_BYTES = 32 * 1024 * 1024
MAX_BINARY_BYTES = 64 * 1024 * 1024
READ_CHUNK = 65536
HEX = frozenset("0123456789abcdef")
_OPEN = os.open
_READ = os.read
_FSTAT = os.fstat
_CLOSE = os.close


class AuditError(Exception):
    """A source, dependency, link, provenance, or phase boundary failed."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def exact_sha(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64 and frozenset(value) <= HEX,
            name + ": expected exactly 64 lowercase SHA-256 digits")
    return value


def unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicate or invalid JSON object keys")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str) -> dict[str, object]:
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_json_object,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                AuditError("nonfinite JSON constant " + value)))
    except (ValueError, UnicodeError, TypeError) as error:
        raise AuditError(label + ": invalid strict JSON") from error
    require(type(result) is dict, label + ": expected a JSON object")
    return result


def empty_effects() -> dict[str, int]:
    return {key: 0 for key in (
        "approved_owner_reads", "candidate_source_reads", "candidate_binary_reads",
        "pinned_stdlib_reads", "historical_v2_owner_reads",
        "historical_v3_owner_reads", "public_failure_receipt_reads",
        "candidate_imports", "reference_imports",
        "imports_after_wall", "native_library_loads", "candidate_executions",
        "candidate_workers", "reference_workers", "compiler_processes",
        "subprocesses", "archive_reads", "archive_decompressions", "private_reads",
        "holdout_reads", "hidden_case_reads", "benchmark_reads", "network_requests",
        "threads_started", "clock_samples", "workspace_mutations", "git_reads",
        "blocked_reads", "blocked_writes", "blocked_imports", "blocked_processes",
        "blocked_native_loads", "blocked_threads", "blocked_network", "blocked_clocks",
        "blocked_audit_hooks",
    )}


class EffectWall:
    """Physically deny effects; saved primitives admit only enumerated owner reads."""

    def __init__(self) -> None:
        self.effects = empty_effects()
        self.originals: list[tuple[object, str, object]] = []

    def block(self, owner: object, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def denied(*args: object, **kwargs: object) -> object:
            self.effects[counter] += 1
            raise AuditError("the effect wall forbids " + name)

        self.originals.append((owner, name, previous))
        setattr(owner, name, denied)

    def __enter__(self) -> EffectWall:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (os, "fstat"), (os, "listdir"),
            (os, "scandir"), (os, "walk"),
        ):
            self.block(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "mkdir"),
            (os, "makedirs"), (os, "rename"), (os, "replace"), (os, "rmdir"),
            (os, "chmod"), (os, "chown"), (os, "link"), (os, "symlink"),
            (os, "truncate"), (os, "utime"), (os, "fsync"),
        ):
            self.block(owner, name, "blocked_writes")
        self.block(builtins, "__import__", "blocked_imports")
        self.block(importlib, "import_module", "blocked_imports")
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            self.block(subprocess, name, "blocked_processes")
        for name in ("system", "popen", "fork", "posix_spawn", "posix_spawnp"):
            self.block(os, name, "blocked_processes")
        self.block(threading.Thread, "start", "blocked_threads")
        self.block(socket, "create_connection", "blocked_network")
        self.block(socket.socket, "connect", "blocked_network")
        self.block(sys, "addaudithook", "blocked_audit_hooks")
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
            "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
            "thread_time_ns", "sleep",
        ):
            self.block(time, name, "blocked_clocks")
        for module_name in ("ctypes", "_ctypes"):
            module = sys.modules.get(module_name)
            if module is not None:
                for name in ("CDLL", "PyDLL", "WinDLL", "OleDLL", "dlopen", "_dlopen"):
                    self.block(module, name, "blocked_native_loads")
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        for owner, name, previous in reversed(self.originals):
            setattr(owner, name, previous)


def checked_relative(path: str, *, allow_public_failure_receipt: bool = False) -> tuple[str, ...]:
    require(type(path) is str and bool(path) and "\x00" not in path and "\\" not in path,
            "invalid owner path")
    parts = path.split("/")
    require(not path.startswith("/") and all(part not in {"", ".", ".."} for part in parts),
            "noncanonical owner path")
    for part in parts:
        lowered = part.casefold()
        require(part not in {".git", ".agents", ".codex", "__pycache__"},
                "metadata, agent, or cache owner is forbidden")
        require(not any(item in lowered for item in ("holdout", "hidden", "private", "benchmark")),
                "private, holdout, hidden, or benchmark owner is forbidden")
        require(lowered not in {"performance", "perf", "archives"},
                "archive and performance owners are forbidden")
        if lowered == "evidence":
            require(allow_public_failure_receipt
                    and path in {V2_FAILURE_RECEIPT_PATH, V3_FAILURE_RECEIPT_PATH},
                    "only the two exact pinned public V2/V3 failure receipts may enter evidence")
    return tuple(parts)


def read_file_at(base: str, relative: str, wall: EffectWall, *, category: str,
                 maximum: int = MAX_SOURCE_BYTES) -> tuple[bytes, dict[str, object]]:
    public_failure_receipt = category == "public_failure_receipt_reads"
    require(not public_failure_receipt or relative in {
        V2_FAILURE_RECEIPT_PATH, V3_FAILURE_RECEIPT_PATH,
    },
            "the public-receipt read capability is exact and non-transferable")
    parts = checked_relative(relative, allow_public_failure_receipt=public_failure_receipt)
    handles: list[int] = []
    try:
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
        handles.append(_OPEN(base, directory_flags))
        for part in parts[:-1]:
            handles.append(_OPEN(part, directory_flags, dir_fd=handles[-1]))
        file_descriptor = _OPEN(parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                                dir_fd=handles[-1])
        handles.append(file_descriptor)
        before = _FSTAT(file_descriptor)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
                relative + ": require one bounded regular owned file")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = _READ(file_descriptor, min(remaining, READ_CHUNK))
            require(bool(chunk), relative + ": source was truncated during reading")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(not _READ(file_descriptor, 1), relative + ": source grew during reading")
        after = _FSTAT(file_descriptor)
        signature = lambda item: (item.st_dev, item.st_ino, item.st_size,
                                   item.st_mtime_ns, item.st_ctime_ns)
        require(signature(before) == signature(after), relative + ": source changed while read")
        raw = b"".join(chunks)
        wall.effects["approved_owner_reads"] += 1
        if category != "approved_owner_reads":
            wall.effects[category] += 1
        return raw, {
            "path": relative, "sha256": digest(raw), "bytes": len(raw),
            "device": before.st_dev, "inode": before.st_ino,
            "mode": f"{stat.S_IMODE(before.st_mode):04o}",
        }
    finally:
        for handle in reversed(handles):
            _CLOSE(handle)


def finding(family: str, path: str, line: int, code: str, message: str,
            provenance: str = "CANDIDATE_OWNED", **extra: object) -> dict[str, object]:
    item: dict[str, object] = {
        "severity": "FAIL", "family": family, "path": path, "line": line,
        "code": code, "provenance": provenance, "message": message,
    }
    item.update(extra)
    return item


def folded_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and type(node.value) is str:
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        first, second = folded_string(node.left), folded_string(node.right)
        return first + second if first is not None and second is not None else None
    if isinstance(node, ast.JoinedStr):
        values = [folded_string(value) for value in node.values]
        return "".join(values) if all(value is not None for value in values) else None
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "chr" and len(node.args) == 1 and not node.keywords
            and isinstance(node.args[0], ast.Constant)
            and type(node.args[0].value) is int and 0 <= node.args[0].value <= 0x10FFFF):
        return chr(node.args[0].value)
    return None


def raw_chain(node: ast.AST) -> tuple[str, ...] | None:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        head = raw_chain(node.value)
        return head + (node.attr,) if head is not None else None
    return None


class PythonInspector(ast.NodeVisitor):
    def __init__(self, family: str, path: str, *, facade: bool = False) -> None:
        self.family, self.path, self.facade = family, path, facade
        self.aliases: dict[str, tuple[str, ...]] = {}
        self.findings: list[dict[str, object]] = []
        self.imports: set[str] = set()
        self.owned_bridges: set[str] = set()
        self.facade_targets: set[str] = set()
        self.scope: list[str] = []
        self.approved_ctypes_imports = 0
        self.owned_native_anchors = 0
        self.owned_native_loaders = 0
        self.loader_assignment_ids: set[int] = set()
        self.valid_native_anchor = False

    def add(self, node: ast.AST, code: str, message: str, **extra: object) -> None:
        self.findings.append(finding(self.family, self.path, getattr(node, "lineno", 0),
                                     code, message, **extra))

    def chain(self, node: ast.AST) -> tuple[str, ...] | None:
        chain = raw_chain(node)
        if chain is None:
            return None
        return self.aliases.get(chain[0], (chain[0],)) + chain[1:]

    def owned_loader_scope(self) -> bool:
        return (self.family == "zig" and self.path == "candidates/zig_candidate.py"
                and self.scope == ["_Native", "__init__"])

    def exact_native_anchor(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.Call) or self.chain(node.func) != ("os", "path", "join"):
            return False
        if len(node.args) != 2 or node.keywords:
            return False
        directory, filename = node.args
        if not (isinstance(filename, ast.Constant) and type(filename.value) is str
                and filename.value == "_zig_probe.so"):
            return False
        if not (isinstance(directory, ast.Call)
                and self.chain(directory.func) == ("os", "path", "dirname")
                and len(directory.args) == 1 and not directory.keywords):
            return False
        return isinstance(directory.args[0], ast.Name) and directory.args[0].id == "__file__"

    def exact_owned_loader(self, node: ast.Call) -> bool:
        return (
            self.owned_loader_scope() and self.approved_ctypes_imports == 1
            and self.valid_native_anchor and self.owned_native_anchors == 1
            and self.owned_native_loaders == 0 and id(node) in self.loader_assignment_ids
            and self.chain(node.func) == ("ctypes", "CDLL") and len(node.args) == 1
            and not node.keywords and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "path"
        )

    def classify_import(self, node: ast.AST, module: str) -> None:
        root = module.split(".", 1)[0]
        self.imports.add(module)
        if root == "ctypes":
            if not (self.family == "zig" and self.path == "candidates/zig_candidate.py"
                    and module == "ctypes"):
                self.add(node, "CANDIDATE_UNOWNED_CTYPES_IMPORT",
                         "ctypes is permitted only for the exact Zig-owned first-party binding")
        elif root in FORBIDDEN_ROOTS or root == "inspect":
            chain = ["inspect", "tokenize", "re", "re.compile"] if root == "inspect" else [module]
            self.add(node, "CANDIDATE_FORBIDDEN_IMPORT",
                     "candidate-owned production import reaches a foreign engine or loader",
                     import_chain=chain)
        elif root not in SAFE_PYTHON_ROOTS and root != "candidates":
            self.add(node, "CANDIDATE_UNKNOWN_IMPORT",
                     "candidate-owned import is outside the exact metadata allowlist")

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            self.classify_import(node, item.name)
            if item.name.startswith("candidates."):
                expected_candidate = "candidates." + (
                    "vm" if self.family == "c_vm" else self.family
                ) + "_candidate"
                if not self.facade or item.name != expected_candidate:
                    self.add(node, "CROSS_FAMILY_DIRECT_CANDIDATE_IMPORT",
                             "direct candidate imports may not borrow another engine",
                             imported_candidate=item.name)
                else:
                    self.facade_targets.add(item.name)
            if item.name == "ctypes":
                if (self.family == "zig" and self.path == "candidates/zig_candidate.py"
                        and item.asname is None):
                    self.approved_ctypes_imports += 1
                    if self.approved_ctypes_imports != 1:
                        self.add(node, "DUPLICATE_OWNED_CTYPES_IMPORT",
                                 "the owned Zig adapter must import ctypes exactly once")
                else:
                    self.add(node, "ALIASED_OR_UNOWNED_CTYPES_IMPORT",
                             "aliased or cross-family ctypes imports are forbidden")
            local = item.asname or item.name.split(".", 1)[0]
            self.aliases[local] = tuple(item.name.split("."))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if node.level:
            self.add(node, "CANDIDATE_RELATIVE_IMPORT", "relative candidate imports are ambiguous")
            return
        if self.facade and module.startswith("candidates."):
            self.facade_targets.add(module)
            expected = "candidates." + ("vm" if self.family == "c_vm" else self.family) + "_candidate"
            if module != expected:
                self.add(node, "PUBLIC_FACADE_FOREIGN_CANDIDATE",
                         "the public facade may expose only its own selected first-party candidate",
                         provenance="PUBLIC_FACADE", imported_candidate=module,
                         expected_candidate=expected)
        elif module.split(".", 1)[0] == "ctypes":
            self.add(node, "INDIRECT_OR_ALIASED_CTYPES_IMPORT",
                     "direct or aliased ctypes names bypass the exact owned-loader proof")
            self.classify_import(node, module)
        elif module == "candidates":
            expected = str(FAMILIES[self.family]["bridge"])
            for item in node.names:
                if item.name != expected or item.asname is not None:
                    self.add(node, "CROSS_FAMILY_CANDIDATE_IMPORT",
                             "candidate imports a foreign or aliased bridge",
                             imported_bridge=item.name)
                else:
                    self.owned_bridges.add(item.name)
                self.aliases[item.asname or item.name] = ("candidates", item.name)
            return
        else:
            self.classify_import(node, module)
        for item in node.names:
            if item.name == "*" and not self.facade:
                self.add(node, "CANDIDATE_STAR_IMPORT", "candidate uses an unbounded star import")
            self.aliases[item.asname or item.name] = tuple(module.split(".")) + (item.name,)

    def visit_Assign(self, node: ast.Assign) -> None:
        chain = self.chain(node.value)
        if chain is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.aliases[target.id] = chain
                    if chain == ("ctypes",):
                        self.add(node, "ALIASED_OWNED_NATIVE_LOADER",
                                 "the exact first-party ctypes loader cannot be rebound")
        if self.owned_loader_scope():
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "path":
                    if self.exact_native_anchor(node.value) and self.owned_native_anchors == 0:
                        self.owned_native_anchors += 1
                        self.valid_native_anchor = True
                    else:
                        self.valid_native_anchor = False
                        self.add(node, "MUTABLE_OR_UNOWNED_NATIVE_PATH",
                                 "the Zig loader path must be one immutable __file__/_zig_probe.so anchor")
                if (isinstance(target, ast.Attribute) and target.attr == "library"
                        and isinstance(target.value, ast.Name) and target.value.id == "self"
                        and isinstance(node.value, ast.Call)):
                    self.loader_assignment_ids.add(id(node.value))
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if (self.owned_loader_scope() and isinstance(node.target, ast.Name)
                and node.target.id == "path"):
            self.valid_native_anchor = False
            self.add(node, "MUTABLE_OWNED_NATIVE_PATH",
                     "the authenticated first-party native path cannot be mutated")
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        if self.owned_loader_scope() and any(
                isinstance(target, ast.Name) and target.id == "path"
                for target in node.targets):
            self.valid_native_anchor = False
            self.add(node, "DELETED_OWNED_NATIVE_PATH",
                     "the authenticated first-party native path cannot be replaced")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        chain = self.chain(node.func)
        if chain is not None:
            tail = chain[-1]
            if tail in {"__import__", "import_module", "module_from_spec",
                        "spec_from_file_location", "exec_module"}:
                name = folded_string(node.args[0]) if node.args else None
                self.add(node, "CANDIDATE_DYNAMIC_IMPORT",
                         "candidate-owned dynamic module resolution is forbidden",
                         dynamic_name=name if name is not None else "NOT STATICALLY DETERMINED")
            if tail in {"CDLL", "PyDLL", "WinDLL", "OleDLL", "LoadLibrary",
                        "dlopen", "dlsym", "CFUNCTYPE"}:
                if self.exact_owned_loader(node):
                    self.owned_native_loaders += 1
                else:
                    self.add(node, "UNOWNED_DYNAMIC_LIBRARY_LOAD",
                             "only the exact authenticated Zig-owned engine may be loaded",
                             loader=".".join(chain))
            if tail in {"eval", "exec", "system", "popen", "Popen", "posix_spawn"}:
                self.add(node, "CANDIDATE_DYNAMIC_EXECUTION",
                         "candidate-owned interpreter/process dispatch is forbidden",
                         dispatch=".".join(chain))
        if chain == ("getattr",) and len(node.args) >= 2:
            receiver = self.chain(node.args[0])
            attribute = folded_string(node.args[1])
            if receiver and (
                receiver[0] in {"__import__", "eval", "exec"}
                or ((receiver[0] in FORBIDDEN_ROOTS or receiver[0] in {"builtins", "sys"})
                    and (attribute is None or attribute in {
                        "__import__", "import_module", "CDLL", "PyDLL", "dlopen",
                        "modules", "__dict__", "__globals__",
                    }))
            ):
                self.add(node, "CANDIDATE_INDIRECT_DYNAMIC_DISPATCH",
                         "candidate computes a sensitive import or native-loader attribute")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        chain = self.chain(node.value)
        key = folded_string(node.slice)
        if chain and (chain == ("sys", "modules") or chain[-1] in {"__dict__", "__builtins__"}):
            if key is None or key.split(".", 1)[0] in FORBIDDEN_ROOTS or key == "inspect":
                self.add(node, "CANDIDATE_CACHED_MODULE_ACCESS",
                         "candidate accesses a forbidden cached engine or dynamic module")
        self.generic_visit(node)


def inspect_python(source: str, family: str, path: str, *, facade: bool = False) -> dict[str, object]:
    try:
        tree = ast.parse(source, filename=path)
    except (SyntaxError, ValueError, TypeError, RecursionError) as error:
        raise AuditError(path + ": cannot parse candidate Python source") from error
    visitor = PythonInspector(family, path, facade=facade)
    visitor.visit(tree)
    if not facade and visitor.owned_bridges != {str(FAMILIES[family]["bridge"])}:
        visitor.findings.append(finding(family, path, 0, "MISSING_OWNED_BRIDGE",
                                        "candidate must import exactly its own first-party bridge"))
    if visitor.approved_ctypes_imports and (
            visitor.approved_ctypes_imports != 1 or visitor.owned_native_anchors != 1
            or visitor.owned_native_loaders != 1 or not visitor.valid_native_anchor):
        visitor.findings.append(finding(
            family, path, 0, "UNPROVEN_OWNED_NATIVE_FFI",
            "first-party ctypes requires exactly one immutable owned path and one exact CDLL call",
        ))
    return {
        "family": family, "path": path, "imports": sorted(visitor.imports),
        "owned_bridges": sorted(visitor.owned_bridges),
        "facade_targets": sorted(visitor.facade_targets), "findings": visitor.findings,
        "owned_ctypes_imports": visitor.approved_ctypes_imports,
        "owned_first_party_native_anchors": visitor.owned_native_anchors,
        "owned_first_party_native_loaders": visitor.owned_native_loaders,
        "facade_counts_as_candidate_family": False,
        "source_parsed_not_imported": True,
    }


def rust_identifier_start(char: str) -> bool:
    return bool(char) and (char == "_" or char.isalpha())


def rust_identifier_part(char: str) -> bool:
    return bool(char) and (char == "_" or char.isalnum())


def rust_raw_string(source: str, at: int, path: str,
                    line: int) -> tuple[str, int, int] | None:
    prefix_length = 0
    for prefix in ("br", "cr", "r"):
        if source.startswith(prefix, at):
            prefix_length = len(prefix)
            break
    if not prefix_length:
        return None
    cursor = at + prefix_length
    while cursor < len(source) and source[cursor] == "#":
        cursor += 1
    hashes = cursor - at - prefix_length
    if cursor >= len(source) or source[cursor] != '"':
        return None
    require(hashes <= 255, f"{path}:{line}: Rust raw string delimiter exceeds 255 hashes")
    closing = '"' + "#" * hashes
    finish = source.find(closing, cursor + 1)
    require(finish >= 0, f"{path}:{line}: unterminated Rust raw string")
    end = finish + len(closing)
    require(end >= len(source) or source[end] != "#",
            f"{path}:{line}: Rust raw string has mismatched trailing delimiter hashes")
    content = source[cursor + 1:finish]
    return content, end, line + content.count("\n")


def rust_character_or_lifetime(source: str, at: int, path: str,
                               line: int, *, byte: bool = False) -> tuple[str, str, int]:
    quote = at + (1 if byte else 0)
    require(quote + 1 < len(source) and source[quote] == "'",
            f"{path}:{line}: incomplete Rust character or lifetime")
    first = quote + 1
    char = source[first]
    if char == "\\":
        cursor = first + 1
        require(cursor < len(source), f"{path}:{line}: truncated Rust character escape")
        marker = source[cursor]
        if marker == "x":
            digits = source[cursor + 1:cursor + 3]
            require(len(digits) == 2 and all(item in "0123456789abcdefABCDEF" for item in digits),
                    f"{path}:{line}: malformed Rust hexadecimal character escape")
            cursor += 3
        elif marker == "u":
            require(not byte and cursor + 1 < len(source) and source[cursor + 1] == "{",
                    f"{path}:{line}: malformed Rust Unicode character escape")
            finish = source.find("}", cursor + 2)
            digits = source[cursor + 2:finish] if finish >= 0 else ""
            require(1 <= len(digits.replace("_", "")) <= 6
                    and all(item in "0123456789abcdefABCDEF_" for item in digits),
                    f"{path}:{line}: malformed Rust Unicode character escape")
            cursor = finish + 1
        else:
            require(marker in {"n", "r", "t", "0", "\\", "'", '"'},
                    f"{path}:{line}: invalid Rust character escape")
            cursor += 1
        require(cursor < len(source) and source[cursor] == "'",
                f"{path}:{line}: unterminated Rust character literal")
        return "literal", source[at:cursor + 1], cursor + 1
    require(char not in {"\n", "\r", "'"},
            f"{path}:{line}: invalid empty or multiline Rust character/lifetime")
    if rust_identifier_start(char):
        cursor = first + 1
        while cursor < len(source) and rust_identifier_part(source[cursor]):
            cursor += 1
        if cursor < len(source) and source[cursor] == "'":
            require(cursor == first + 1,
                    f"{path}:{line}: Rust character literals contain exactly one character")
            require(not byte or ord(char) < 128,
                    f"{path}:{line}: Rust byte characters must be ASCII")
            return "literal", source[at:cursor + 1], cursor + 1
        require(not byte, f"{path}:{line}: byte literal cannot be a Rust lifetime")
        return "lifetime", source[first:cursor], cursor
    require(first + 1 < len(source) and source[first + 1] == "'",
            f"{path}:{line}: malformed Rust character literal")
    require(not byte or ord(char) < 128,
            f"{path}:{line}: Rust byte characters must be ASCII")
    return "literal", source[at:first + 2], first + 2


def native_tokens(source: str, path: str, kind: str) -> list[tuple[str, str, int]]:
    tokens: list[tuple[str, str, int]] = []
    at, line, size = 0, 1, len(source)
    while at < size:
        char = source[at]
        if char.isspace():
            line += char == "\n"
            at += 1
            continue
        if kind == "fortran" and char == "!":
            stop = source.find("\n", at)
            at = size if stop < 0 else stop
            continue
        if kind != "fortran" and source.startswith("//", at):
            stop = source.find("\n", at + 2)
            at = size if stop < 0 else stop
            continue
        if kind != "fortran" and source.startswith("/*", at):
            start, depth = line, 1
            at += 2
            while at < size and depth:
                if source.startswith("/*", at):
                    depth += 1
                    at += 2
                elif source.startswith("*/", at):
                    depth -= 1
                    at += 2
                else:
                    line += source[at] == "\n"
                    at += 1
            require(depth == 0, f"{path}:{start}: unterminated nested native block comment")
            continue
        if kind == "rust":
            raw = rust_raw_string(source, at, path, line)
            if raw is not None:
                value, at, next_line = raw
                tokens.append(("string", value, line))
                line = next_line
                continue
            if source.startswith("b'", at):
                token_kind, value, at = rust_character_or_lifetime(source, at, path, line, byte=True)
                tokens.append((token_kind, value, line))
                continue
            if char == "'":
                token_kind, value, at = rust_character_or_lifetime(source, at, path, line)
                tokens.append((token_kind, value, line))
                continue
        if source.startswith('R"', at):
            open_at = source.find("(", at + 2)
            require(open_at >= 0, f"{path}:{line}: invalid C++ raw string")
            delimiter = source[at + 2:open_at]
            close = ")" + delimiter + '"'
            end = source.find(close, open_at + 1)
            require(end >= 0, f"{path}:{line}: unterminated C++ raw string")
            value = source[open_at + 1:end]
            tokens.append(("string", value, line))
            line += value.count("\n")
            at = end + len(close)
            continue
        rust_prefixed = kind == "rust" and (
            source.startswith('b"', at) or source.startswith('c"', at)
        )
        if char in {"'", '"', "`"} or rust_prefixed:
            start_line = line
            start = at
            if rust_prefixed:
                at += 1
            quote = source[at]
            at += 1
            while at < size and source[at] != quote:
                if source[at] == "\n":
                    require(quote == "`" or kind == "rust",
                            f"{path}:{start_line}: unterminated native literal")
                    line += 1
                if source[at] == "\\" and quote != "`":
                    at += 1
                    require(at < size, f"{path}:{start_line}: invalid native escape")
                    if source[at] == "\n":
                        line += 1
                at += 1
            require(at < size, f"{path}:{start_line}: unterminated native literal")
            raw = source[start:at + 1]
            if quote == '"':
                if kind == "rust":
                    prefix = 1 if rust_prefixed else 0
                    value = raw[prefix + 1:-1]
                else:
                    try:
                        value = ast.literal_eval(raw)
                    except (ValueError, SyntaxError, TypeError) as error:
                        raise AuditError(f"{path}:{start_line}: invalid native string") from error
                    require(type(value) is str, f"{path}:{start_line}: invalid native string")
                tokens.append(("string", value, start_line))
            else:
                tokens.append(("literal", raw, start_line))
            at += 1
            continue
        if char.isalpha() or char == "_":
            if kind == "rust" and source.startswith("r#", at) and at + 2 < size \
                    and rust_identifier_start(source[at + 2]):
                at += 2
            end = at + 1
            while end < size and (source[end].isalnum() or source[end] == "_"):
                end += 1
            tokens.append(("identifier", source[at:end], line))
            at = end
            continue
        tokens.append(("punctuation", char, line))
        at += 1
    return tokens


def header_name(tokens: list[tuple[str, str, int]], cursor: int,
                path: str) -> tuple[str, int]:
    require(cursor < len(tokens), path + ": native include is missing a header")
    if tokens[cursor][0] == "string":
        return tokens[cursor][1], cursor + 1
    require(tokens[cursor][1] == "<", path + ": computed native header is forbidden")
    cursor += 1
    pieces: list[str] = []
    while cursor < len(tokens) and tokens[cursor][1] != ">":
        pieces.append(tokens[cursor][1])
        cursor += 1
    require(cursor < len(tokens), path + ": unterminated native include")
    return "".join(pieces), cursor + 1


def inspect_native(source: str, family: str, path: str, kind: str) -> dict[str, object]:
    tokens = native_tokens(source, path, kind)
    findings: list[dict[str, object]] = []
    imports: list[str] = []
    headers: list[str] = []
    if kind == "go":
        for line_number, raw_line in enumerate(source.splitlines(), 1):
            if raw_line.lstrip(" \t*").startswith("#cgo"):
                findings.append(finding(family, path, line_number, "EXTERNAL_CGO_LINK_DIRECTIVE",
                                        "cgo compiler/linker directives can hide an external engine"))
    for index, (token_kind, value, line) in enumerate(tokens):
        if token_kind != "identifier":
            continue
        lowered = value.casefold()
        if value in FORBIDDEN_NATIVE_SYMBOLS or lowered.startswith(FORBIDDEN_SYMBOL_PREFIXES):
            findings.append(finding(family, path, line, "FORBIDDEN_NATIVE_ENGINE_OR_DISPATCH",
                                    "native candidate exposes an external regex engine or dynamic dispatch",
                                    symbol=value))
        if value == "RE2" or (value in {"regex", "basic_regex", "wregex"}
                              and index >= 3 and tokens[index - 1][1] == ":"
                              and tokens[index - 2][1] == ":"):
            findings.append(finding(family, path, line, "FOREIGN_NATIVE_REGEX_ENGINE",
                                    "native source uses a non-owned regular-expression engine"))
        if value == "PyImport_ImportModule":
            if (index + 2 >= len(tokens) or tokens[index + 1][1] != "("
                    or tokens[index + 2][0] != "string"):
                findings.append(finding(family, path, line, "COMPUTED_NATIVE_PYTHON_IMPORT",
                                        "native bridge aliases or computes a Python import"))
                continue
            cursor, pieces = index + 2, []
            while cursor < len(tokens) and tokens[cursor][0] == "string":
                pieces.append(tokens[cursor][1])
                cursor += 1
            if cursor >= len(tokens) or tokens[cursor][1] != ")":
                findings.append(finding(family, path, line, "COMPUTED_NATIVE_PYTHON_IMPORT",
                                        "native bridge computes a Python import"))
                continue
            module = "".join(pieces)
            imports.append(module)
            if module == "inspect":
                findings.append(finding(
                    family, path, line, "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
                    "candidate-owned native import reaches inspect, tokenize, and standard-library re.compile",
                    import_chain=["candidate native bridge", "inspect", "tokenize", "re", "re.compile"],
                    reachability="PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN",
                ))
            elif module not in SAFE_NATIVE_IMPORTS:
                findings.append(finding(family, path, line, "FORBIDDEN_NATIVE_PYTHON_IMPORT",
                                        "native bridge imports an unapproved Python module",
                                        imported_module=module))
        if value == "include" and index and tokens[index - 1][1] == "#":
            header, _ = header_name(tokens, index + 1, path)
            headers.append(header)
            if header not in ALLOWED_HEADERS and not (family == "cpp" and header == "engine.hpp"):
                findings.append(finding(family, path, line, "EXTERNAL_NATIVE_HEADER",
                                        "native source includes a non-owned or non-system header",
                                        header=header))
        if value in {"cImport", "cInclude", "DynLib", "embedFile"}:
            findings.append(finding(family, path, line, "NATIVE_EXTERNAL_SOURCE_OR_LOADER",
                                    "native candidate reaches an external include or dynamic loader",
                                    symbol=value))
        if value in {"linkSystemLibrary", "linkLibC", "linkLibCpp", "linkFramework"}:
            findings.append(finding(family, path, line, "EXTERNAL_NATIVE_LINK_DIRECTIVE",
                                    "native source requests an unapproved dynamic link owner",
                                    symbol=value))
        if kind == "go" and value == "import":
            if index + 1 >= len(tokens):
                findings.append(finding(family, path, line, "COMPUTED_GO_IMPORT",
                                        "Go import is incomplete or computed"))
            elif tokens[index + 1][0] == "string":
                module = tokens[index + 1][1]
                if module not in SAFE_GO_IMPORTS:
                    findings.append(finding(family, path, line, "EXTERNAL_GO_PACKAGE",
                                            "Go imports an external matching package", imported_module=module))
            elif tokens[index + 1][1] == "(":
                cursor = index + 2
                while cursor < len(tokens) and tokens[cursor][1] != ")":
                    if tokens[cursor][0] != "string" or tokens[cursor][1] not in SAFE_GO_IMPORTS:
                        findings.append(finding(family, path, tokens[cursor][2], "EXTERNAL_GO_PACKAGE",
                                                "Go imports an aliased, computed, or external package"))
                    cursor += 1
                if cursor >= len(tokens):
                    findings.append(finding(family, path, line, "COMPUTED_GO_IMPORT",
                                            "Go import block is not terminated"))
            else:
                findings.append(finding(family, path, line, "COMPUTED_GO_IMPORT",
                                        "Go import is aliased or computed"))
        if kind == "rust" and value == "use":
            if index + 1 >= len(tokens) or tokens[index + 1][0] != "identifier":
                findings.append(finding(family, path, line, "COMPUTED_RUST_PACKAGE",
                                        "Rust package import is incomplete or computed"))
            elif tokens[index + 1][1] not in SAFE_RUST_IMPORT_ROOTS:
                findings.append(finding(family, path, line, "EXTERNAL_RUST_PACKAGE",
                                        "Rust imports a non-first-party package",
                                        imported_module=tokens[index + 1][1]))
        if kind == "rust" and value == "extern" and index + 2 < len(tokens) and (
                tokens[index + 1][1] == "crate"):
            findings.append(finding(family, path, line, "EXTERNAL_RUST_CRATE",
                                    "Rust imports a dynamically supplied external crate"))
        if kind == "rust" and value in {
            "concat", "concat_idents", "include", "include_bytes", "include_str",
            "macro_rules", "env", "option_env", "asm", "global_asm",
        } and index + 1 < len(tokens) and tokens[index + 1][1] == "!":
            findings.append(finding(family, path, line, "COMPUTED_RUST_MACRO_DISPATCH",
                                    "Rust macro can conceal an external source, symbol, or engine",
                                    macro=value))
        if kind == "rust" and value in {"link", "link_name", "link_ordinal"}:
            previous = [item[1] for item in tokens[max(0, index - 3):index]]
            if "[" in previous or "#" in previous:
                findings.append(finding(family, path, line, "EXTERNAL_RUST_LINK_ATTRIBUTE",
                                        "Rust native link attribute can hide an external engine",
                                        attribute=value))
        if kind == "rust" and value in {"Library", "Command"} and index >= 2:
            prefix = [item[1] for item in tokens[max(0, index - 6):index]]
            if "libloading" in prefix or "process" in prefix:
                findings.append(finding(family, path, line, "RUST_DYNAMIC_LOADER_OR_PROCESS",
                                        "Rust source reaches a dynamic loader or external process",
                                        symbol=value))
        if kind == "fortran" and value.casefold() == "use":
            cursor = index + 1
            while cursor < len(tokens) and tokens[cursor][1] in {",", ":", "intrinsic", "non_intrinsic"}:
                cursor += 1
            if cursor >= len(tokens) or tokens[cursor][1].casefold() != "iso_c_binding":
                findings.append(finding(family, path, line, "EXTERNAL_FORTRAN_MODULE",
                                        "Fortran imports a non-intrinsic external module"))
        if value == "import" and index and tokens[index - 1][1] == "@":
            if not (kind == "zig" and index + 3 < len(tokens)
                    and tokens[index + 1][1] == "("
                    and tokens[index + 2][0] == "string"
                    and tokens[index + 3][1] == ")"
                    and tokens[index + 2][1] == "std"):
                findings.append(finding(family, path, line, "EXTERNAL_ZIG_PACKAGE",
                                        "Zig imports a computed or non-standard external package"))
        for other, prefixes in FAMILY_PREFIXES.items():
            if other != family and other not in {"c_vm", "rust"} and any(
                    value.startswith(prefix) for prefix in prefixes):
                findings.append(finding(family, path, line, "CROSS_FAMILY_NATIVE_SYMBOL",
                                        "native candidate refers to another candidate's engine",
                                        symbol=value, foreign_family=other))
        if family != "rust" and (
                value in {"rebar_compile", "rebar_compile_scanner", "rebar_match",
                          "rebar_match_ascii", "rebar_match_wide", "rebar_free",
                          "rebar_groups", "rebar_flags"}
                or value.startswith(("rebar_collect_", "rebar_name_", "rebar_error_"))):
            findings.append(finding(family, path, line, "CROSS_FAMILY_NATIVE_SYMBOL",
                                    "native candidate refers to the Rust-owned engine",
                                    symbol=value, foreign_family="rust"))
    return {
        "family": family, "path": path, "kind": kind,
        "native_python_imports": imports, "native_headers": sorted(set(headers)),
        "findings": findings, "source_parsed_not_compiled": True,
    }


def inspect_rust_manifest(source: str) -> dict[str, object]:
    try:
        manifest = tomllib.loads(source)
    except (ValueError, TypeError, RecursionError) as error:
        raise AuditError("Rust Cargo.toml is invalid TOML") from error
    package = manifest.get("package")
    library = manifest.get("lib")
    require(type(package) is dict and package.get("name") == "rebar-rust-continuation"
            and package.get("publish") is False and type(library) is dict
            and library.get("crate-type") == ["cdylib"],
            "Rust manifest does not identify exactly one first-party cdylib")

    def no_dependencies(item: object, trail: tuple[str, ...]) -> None:
        if type(item) is dict:
            for key, value in item.items():
                normalized = key.casefold().replace("_", "-")
                require(not normalized.endswith("dependencies") and normalized not in {
                    "patch", "replace", "build", "build-script", "links", "git", "path",
                }, "Rust manifest contains an external/build dependency at " + ".".join(trail + (key,)))
                no_dependencies(value, trail + (key,))
        elif type(item) is list:
            for index, value in enumerate(item):
                no_dependencies(value, trail + (str(index),))

    no_dependencies(manifest, ())
    return {"package": package["name"], "crate_type": ["cdylib"],
            "production_dependencies": 0, "dev_dependencies": 0,
            "build_dependencies": 0, "workspace_dependencies": 0,
            "target_dependencies": 0, "external_regex_packages": 0}


def inspect_rust_lock(source: str) -> dict[str, object]:
    try:
        lock = tomllib.loads(source)
    except (ValueError, TypeError, RecursionError) as error:
        raise AuditError("Rust Cargo.lock is invalid TOML") from error
    packages = lock.get("package")
    require(lock.get("version") == 4 and type(packages) is list and len(packages) == 1,
            "Rust lock must contain exactly one first-party package")
    package = packages[0]
    require(type(package) is dict and package.get("name") == "rebar-rust-continuation"
            and package.get("version") == "0.1.0"
            and set(package) == {"name", "version"}
            and set(lock) == {"version", "package"},
            "Rust lock contains a dependency, source, checksum, or extra package")
    return {"package_count": 1, "first_party_package_count": 1,
            "external_package_count": 0, "external_regex_package_count": 0}


def inspect_project_manifest(source: str) -> dict[str, object]:
    try:
        manifest = tomllib.loads(source)
    except (ValueError, TypeError, RecursionError) as error:
        raise AuditError("pyproject.toml is invalid TOML") from error
    project = manifest.get("project")
    require(type(project) is dict and project.get("name") == "rebar-experiment"
            and project.get("dependencies") == []
            and "optional-dependencies" not in project,
            "Python project must contain zero external or optional production packages")
    return {"external_python_package_count": 0}


def inspect_project_lock(source: str) -> dict[str, object]:
    try:
        lock = tomllib.loads(source)
    except (ValueError, TypeError, RecursionError) as error:
        raise AuditError("uv.lock is invalid TOML") from error
    packages = lock.get("package")
    require(type(packages) is list and len(packages) == 1 and type(packages[0]) is dict
            and packages[0].get("name") == "rebar-experiment"
            and "dependencies" not in packages[0],
            "Python lock must contain exactly one first-party package and no dependencies")
    return {"package_count": 1, "external_python_package_count": 0}


def inspect_go_manifest(source: str) -> dict[str, object]:
    statements = [line.strip() for line in source.splitlines()
                  if line.strip() and not line.lstrip().startswith("//")]
    require(len(statements) == 2 and statements[0] == "module rebar.local/candidates/go"
            and statements[1].startswith("go ")
            and len(statements[1].split()) == 2,
            "Go module must contain exactly its first-party module and language version")
    return {"first_party_module_count": 1, "external_go_package_count": 0,
            "replace_directive_count": 0, "external_regex_package_count": 0}


def bounded_unpack(format_string: str, raw: bytes, offset: int,
                   limit: int, label: str) -> tuple[object, ...]:
    length = struct.calcsize(format_string)
    require(type(offset) is int and 0 <= offset <= limit and length <= limit - offset,
            label + ": ELF field exceeds its verified section bounds")
    return struct.unpack_from(format_string, raw, offset)


def elf_string(table: bytes, offset: int, label: str) -> str:
    require(type(offset) is int and 0 <= offset < len(table),
            label + ": ELF string offset lies outside the string table")
    end = table.find(b"\x00", offset)
    require(end >= offset, label + ": ELF string is not terminated")
    try:
        result = table[offset:end].decode("ascii")
    except UnicodeError as error:
        raise AuditError(label + ": non-ASCII dynamic name") from error
    require("\x00" not in result and len(result) <= 1024,
            label + ": invalid dynamic name")
    return result


def inspect_elf(raw: bytes, family: str, role: str, path: str) -> dict[str, object]:
    require(type(raw) is bytes and 64 <= len(raw) <= MAX_BINARY_BYTES,
            path + ": require one bounded ELF64 binary")
    require(raw[:8] == b"\x7fELF\x02\x01\x01\x00",
            path + ": require first-party 64-bit little-endian ELF")
    header = bounded_unpack("<16sHHIQQQIHHHHHH", raw, 0, len(raw), path)
    require(header[1] == 3 and header[2] == 62 and header[8] == 64
            and header[11] == 64 and 0 < header[12] <= 512 and header[13] < header[12],
            path + ": malformed ELF64 shared-library headers")
    section_offset, section_count = int(header[6]), int(header[12])
    require(section_offset <= len(raw) and section_count <= (len(raw) - section_offset) // 64,
            path + ": section headers exceed the file")
    sections = [bounded_unpack("<IIQQQQIIQQ", raw, section_offset + index * 64,
                               len(raw), path) for index in range(section_count)]
    names_section = sections[int(header[13])]
    names_start, names_size = int(names_section[4]), int(names_section[5])
    require(names_start <= len(raw) and names_size <= len(raw) - names_start,
            path + ": section-name table exceeds the file")
    section_names = raw[names_start:names_start + names_size]
    by_name: dict[str, tuple[object, ...]] = {}
    for section in sections:
        name = elf_string(section_names, int(section[0]), path)
        require(name not in by_name, path + ": duplicate ELF section name")
        offset, length = int(section[4]), int(section[5])
        require(offset <= len(raw) and (
            int(section[1]) == 8 or length <= len(raw) - offset
        ), path + ": ELF section lies outside the file")
        by_name[name] = section
    require(all(name in by_name for name in (".dynstr", ".dynsym", ".dynamic")),
            path + ": require dynamic string, symbol, and dependency sections")
    string_section = by_name[".dynstr"]
    dynstr = raw[int(string_section[4]):int(string_section[4]) + int(string_section[5])]
    require(bool(dynstr) and dynstr[0] == 0, path + ": malformed ELF dynamic string table")
    symbol_section, dynamic_section = by_name[".dynsym"], by_name[".dynamic"]
    require(int(symbol_section[1]) == 11 and int(symbol_section[9]) == 24
            and int(symbol_section[5]) % 24 == 0,
            path + ": malformed ELF dynamic symbol table")
    require(int(dynamic_section[1]) == 6 and int(dynamic_section[9]) == 16
            and int(dynamic_section[5]) % 16 == 0,
            path + ": malformed ELF dynamic dependency table")
    imported: set[str] = set()
    exported: set[str] = set()
    for cursor in range(int(symbol_section[4]),
                        int(symbol_section[4]) + int(symbol_section[5]), 24):
        symbol = bounded_unpack("<IBBHQQ", raw, cursor, len(raw), path)
        name = elf_string(dynstr, int(symbol[0]), path)
        if not name:
            continue
        (imported if int(symbol[3]) == 0 else exported).add(name.split("@", 1)[0])
    needed: list[str] = []
    runpaths: list[str] = []
    terminated = False
    for cursor in range(int(dynamic_section[4]),
                        int(dynamic_section[4]) + int(dynamic_section[5]), 16):
        tag, value = bounded_unpack("<qQ", raw, cursor, len(raw), path)
        if tag == 0:
            terminated = True
            break
        if tag == 1:
            needed.append(elf_string(dynstr, int(value), path))
        if tag in {15, 29}:
            runpaths.append(elf_string(dynstr, int(value), path))
    require(terminated, path + ": ELF dynamic table is not terminated")
    allowed_owned = {"_rust_engine.so"} if family == "rust" else (
        {"_zig_probe.so"} if family == "zig" else set())
    allowed_system = (SAFE_SYSTEM_LIBRARIES if family == "rust"
                      else frozenset({"libc.so.6", "ld-linux-x86-64.so.2"}))
    for library in needed:
        require(library in allowed_system or library in allowed_owned,
                path + ": unowned external dynamic dependency " + library)
    for runpath in runpaths:
        require(runpath in {"$ORIGIN", "$ORIGIN/"},
                path + ": dynamic library search path escapes its first-party owner")
    for symbol in imported | exported:
        lowered = symbol.casefold()
        require(symbol not in FORBIDDEN_NATIVE_SYMBOLS
                and not lowered.startswith(FORBIDDEN_SYMBOL_PREFIXES),
                path + ": forbidden external regex/loader symbol " + symbol)
        for other, prefixes in FAMILY_PREFIXES.items():
            if other != family and other not in {"c_vm", "rust"}:
                require(not any(symbol.startswith(prefix) for prefix in prefixes),
                        path + ": dynamic symbol belongs to another candidate: " + symbol)
    required = {
        ("c_vm", "bridge"): {"PyInit__vm_native"},
        ("rust", "engine"): {"rebar_compile", "rebar_match"},
        ("rust", "bridge"): {"PyInit__rust_bridge"},
        ("zig", "engine"): {"rebar_zig_compile", "rebar_zig_match_wide"},
        ("zig", "bridge"): {"PyInit__zig_bridge"},
    }.get((family, role), set())
    require(required <= exported,
            path + ": native binary is missing its required first-party owner symbols")
    return {
        "family": family, "role": role, "path": path,
        "needed_libraries": needed, "runpaths": runpaths,
        "imported_symbol_count": len(imported), "exported_symbol_count": len(exported),
        "python_c_import_capability": "PyImport_ImportModule" in imported,
        "required_owned_symbols": sorted(required),
        "external_regex_libraries": 0, "external_regex_symbols": 0,
        "binary_parsed_not_loaded": True,
    }


def ast_nodes(tree: ast.AST) -> object:
    """Traverse without ast.walk's per-call, wall-forbidden collections import."""
    pending = [tree]
    while pending:
        node = pending.pop()
        yield node
        pending.extend(ast.iter_child_nodes(node))


def exact_imports(tree: ast.AST, name: str) -> int:
    return sum(
        1 for node in ast_nodes(tree)
        if isinstance(node, ast.Import) and any(item.name == name for item in node.names)
        or isinstance(node, ast.ImportFrom) and node.module == name
    )


def pinned_stdlib_graph(raw_owners: dict[str, bytes]) -> dict[str, object]:
    parsed = {name: ast.parse(raw.decode("utf-8"), filename=name)
              for name, raw in raw_owners.items()}
    inspect_tree, tokenize_tree = parsed["inspect.py"], parsed["tokenize.py"]
    require(exact_imports(inspect_tree, "re") >= 1
            and exact_imports(inspect_tree, "tokenize") >= 1
            and exact_imports(tokenize_tree, "re") >= 1,
            "pinned inspect/tokenize transitive regex import graph changed")
    top_level_compiles = 0
    for item in getattr(tokenize_tree, "body", ()):
        if isinstance(item, (ast.Assign, ast.AnnAssign)):
            value = item.value
            if isinstance(value, ast.Call) and raw_chain(value.func) == ("re", "compile"):
                top_level_compiles += 1
    require(top_level_compiles == 2,
            "pinned tokenize must execute exactly two top-level re.compile calls")
    warning_entrypoint, warning_tree = parsed["warnings.py"], parsed["_py_warnings.py"]
    linecache_tree, enum_tree = parsed["linecache.py"], parsed["enum.py"]
    require(exact_imports(warning_entrypoint, "_py_warnings") >= 1
            and exact_imports(warning_tree, "linecache") >= 1
            and exact_imports(linecache_tree, "tokenize") >= 1,
            "caller-owned warning formatting transitive graph changed")
    enum_signature = [node for node in ast_nodes(enum_tree)
                      if isinstance(node, ast.FunctionDef) and node.name == "__signature__"]
    require(bool(enum_signature)
            and any(exact_imports(node, "inspect") >= 1 for node in enum_signature),
            "caller-owned EnumType.__signature__ transitive graph changed")
    return {
        "candidate_owned_forbidden": {
            "chain": ["candidate native bridge", "inspect", "tokenize", "re", "re.compile"],
            "tokenize_import_time_re_compile_count": top_level_compiles,
            "classification": "FORBIDDEN_CANDIDATE_NATIVE_CAPABILITY",
        },
        "caller_owned_warning_formatting": {
            "chain": ["warnings", "_py_warnings", "linecache", "tokenize", "re", "re.compile"],
            "classification": "HOST_STDLIB_PLUMBING; NOT CANDIDATE MATCHING DELEGATION",
        },
        "caller_owned_enum_introspection": {
            "chain": ["enum.EnumType.__signature__", "inspect", "tokenize", "re", "re.compile"],
            "classification": "HOST_STDLIB_INTROSPECTION; NOT CANDIDATE MATCHING DELEGATION",
        },
    }


def rust_reachability(adapter_source: str, bridge_source: str) -> dict[str, object]:
    tree = ast.parse(adapter_source, filename="candidates/rust_candidate.py")
    aliases = [node for node in ast_nodes(tree)
               if isinstance(node, ast.Name) and node.id == "_NATIVE_BIND"]
    calls = [node for node in ast_nodes(tree)
             if isinstance(node, ast.Call) and raw_chain(node.func) == ("_NATIVE_BIND",)]
    bridge_has_getter = "rust_bound_get_signature" in bridge_source
    bridge_exports_bind = '"bind",' in bridge_source and "bridge_bind(" in bridge_source
    public_uses_descriptors = ("PyDescr_NewMethod(" in bridge_source
                               and "_rust_bridge.pattern_descriptors(Pattern)" in adapter_source)
    return {
        "bridge_exports_private_bind": bridge_exports_bind,
        "bridge_has_legacy_signature_getter": bridge_has_getter,
        "adapter_native_bind_alias_count": len(aliases),
        "adapter_native_bind_call_count": len(calls),
        "public_pattern_methods_use_native_descriptors": public_uses_descriptors,
        "public_matching_delegation_proven": False,
        "classification": (
            "LATENT_PRIVATE_BRIDGE_ESCAPE_HATCH; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN"
            if bridge_exports_bind and bridge_has_getter and not calls and public_uses_descriptors
            else "SOURCE_CONFIGURATION_CHANGED; RE-EVALUATE_REACHABILITY"
        ),
    }


def verify_owned_zig_ffi(results: list[dict[str, object]],
                         facade: dict[str, object]) -> dict[str, object]:
    owned = {
        item["path"]: item for item in results
        if item.get("family") == "zig" and type(item.get("path")) is str
    }
    required_sources = {
        "candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
    }
    required_binaries = {
        "candidates/_zig_probe.so", "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    require(required_sources | required_binaries <= owned.keys(),
            "first-party Zig FFI must authenticate all owned source, bridge, and engine files")
    owner_devices: set[int] = set()
    owner_inodes: set[int] = set()
    owner_digests: set[str] = set()
    for path in required_sources | required_binaries:
        owner = owned[path].get("owner")
        require(type(owner) is dict and owner.get("path") == path
                and type(owner.get("bytes")) is int and owner["bytes"] > 0
                and type(owner.get("device")) is int and owner["device"] > 0
                and type(owner.get("inode")) is int and owner["inode"] > 0
                and owner.get("mode") == ("0700" if path in required_binaries else "0600"),
                "first-party Zig FFI owner changed path, device, inode, size, or mode: " + path)
        owner_digests.add(exact_sha(owner.get("sha256"), path))
        owner_devices.add(owner["device"])
        owner_inodes.add(owner["inode"])
    require(len(owner_devices) == 1 and len(owner_inodes) == 5 and len(owner_digests) == 5,
            "first-party Zig FFI owners must be independently identified, distinct, same-device files")
    adapter, engine, bridge = (
        owned["candidates/zig_candidate.py"],
        owned["candidates/_zig_probe.so"],
        owned["candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"],
    )
    ffi_used = adapter.get("owned_ctypes_imports", 0) != 0
    if ffi_used:
        require(adapter.get("owned_ctypes_imports") == 1
                and adapter.get("owned_first_party_native_anchors") == 1
                and adapter.get("owned_first_party_native_loaders") == 1,
                "first-party Zig FFI has no exact, immutable, same-family loader proof")
    require(engine.get("role") == "engine" and bridge.get("role") == "bridge"
            and engine.get("required_owned_symbols") ==
            ["rebar_zig_compile", "rebar_zig_match_wide"]
            and bridge.get("required_owned_symbols") == ["PyInit__zig_bridge"]
            and set(engine.get("needed_libraries", ())) <=
            {"libc.so.6", "ld-linux-x86-64.so.2"}
            and set(bridge.get("needed_libraries", ())) <=
            {"_zig_probe.so", "libc.so.6", "ld-linux-x86-64.so.2"}
            and "_zig_probe.so" in bridge.get("needed_libraries", ())
            and bridge.get("runpaths") == ["$ORIGIN"],
            "Zig first-party FFI does not bind to its independently verified engine/link owner")
    require(facade.get("family") == "zig"
            and facade.get("facade_targets") == ["candidates.zig_candidate"]
            and facade.get("facade_counts_as_candidate_family") is False,
            "public facade must select exactly the owned Zig family and is never another candidate")
    return {
        "status": "PASS", "ffi_used": ffi_used,
        "candidate_family": "zig", "candidate_family_count": len(FAMILIES),
        "public_facade_counts_as_candidate_family": False,
        "exact_native_filename": "_zig_probe.so",
        "native_path_anchor": "os.path.join(os.path.dirname(__file__), '_zig_probe.so')",
        "owned_source_paths": sorted(required_sources),
        "owned_engine": engine["owner"], "owned_bridge": bridge["owner"],
        "engine_exports": engine["required_owned_symbols"],
        "bridge_exports": bridge["required_owned_symbols"],
        "bridge_needed_libraries": bridge["needed_libraries"],
        "bridge_runpath": bridge["runpaths"],
        "external_regex_engine_count": 0,
        "source_to_binary_reproducible_build": "NOT ESTABLISHED BY THIS STATIC AUDIT",
    }


def validate_contract(contract: dict[str, object]) -> None:
    require(contract.get("schema") == SCHEMA and contract.get("version") == 4,
            "runtime non-delegation V4 contract schema/version changed")
    freeze = contract.get("source_freeze")
    require(type(freeze) is dict and freeze.get("source", {}).get("path") == SOURCE
            and freeze.get("protocol", {}).get("path") == PROTOCOL
            and freeze.get("contract_path") == CONTRACT,
            "contract no longer freezes exactly the three V4 sole-owned files")
    for role in ("source", "protocol"):
        exact_sha(freeze[role].get("sha256"), role)
    require(contract.get("families") == sorted(FAMILIES)
            and contract.get("family_count") == 6,
            "contract must enumerate exactly six first-party candidates")
    stdlib = contract.get("pinned_stdlib")
    require(type(stdlib) is dict and stdlib.get("version") == "3.14.6"
            and stdlib.get("root") == PINNED_STDLIB
            and stdlib.get("sha256") == PINNED_STDLIB_OWNERS,
            "contract changed the pinned stdlib transitive-graph source owners")
    boundaries = contract.get("boundaries")
    require(type(boundaries) is dict
            and boundaries.get("source_only_modes") == ["--self-test", "--verify-source"]
            and boundaries.get("static_audit") == "ROOT AGENT ONLY AFTER VERIFIED SOURCE PUSH"
            and boundaries.get("runtime_audit") == "NOT IMPLEMENTED; ROOT AGENT ONLY"
            and boundaries.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and boundaries.get("candidate_qualified") is False
            and boundaries.get("holdout") == "NOT OPENED",
            "contract weakens the frozen phase or future runtime boundary")
    snapshot = contract.get("current_source_findings")
    require(type(snapshot) is dict
            and snapshot.get("rust") == "FAIL: LATENT PRIVATE BRIDGE INSPECT ESCAPE HATCH"
            and snapshot.get("zig") == "PASS: AUTHENTICATED FIRST-PARTY FFI IS PERMITTED"
            and snapshot.get("public_rebar") ==
            "PASS: SAME-FAMILY FIRST-PARTY FACADE; NOT A SEVENTH CANDIDATE"
            and snapshot.get("rust_public_matching_delegation") == "NOT PROVEN",
            "contract suppresses the Rust finding or misclassifies permitted first-party ownership")
    policy = contract.get("first_party_policy")
    require(type(policy) is dict
            and policy.get("candidate_owned_re_sre_regex_packages") == "FORBIDDEN"
            and policy.get("candidate_owned_inspect_tokenize_transitive_re") == "FORBIDDEN"
            and policy.get("candidate_owned_ctypes_or_dynamic_library_loading") ==
            "ONLY EXACT AUTHENTICATED SAME-FAMILY FIRST-PARTY ENGINE FFI"
            and policy.get("public_first_party_facade") ==
            "ALLOWED FOR ONE SELECTED FAMILY; NEVER A SEPARATE CANDIDATE"
            and policy.get("candidate_cross_family_dispatch") == "FORBIDDEN"
            and policy.get("external_regex_packages") == 0,
            "V4 weakened external-engine quarantine or again rejected first-party FFI/facades")
    predecessor = contract.get("immutable_v2_predecessor")
    require(type(predecessor) is dict and predecessor.get("owners") == V2_OWNERS,
            "V3 must retain all exact immutable V2 source, protocol, and contract pins")
    failed = predecessor.get("actual_failure_receipt")
    require(type(failed) is dict
            and failed.get("path") == V2_FAILURE_RECEIPT_PATH
            and failed.get("sha256") == V2_FAILURE_RECEIPT_SHA256
            and failed.get("bytes") == V2_FAILURE_RECEIPT_BYTES
            and failed.get("device") == V2_FAILURE_RECEIPT_DEVICE
            and failed.get("inode") == V2_FAILURE_RECEIPT_INODE
            and failed.get("mode") == "0600"
            and failed.get("status") == "FAIL"
            and failed.get("message") ==
            "candidates/rust/src/lib.rs:252: unterminated native literal",
            "V3 must preserve the actual first root V2 lexer failure without reinterpretation")
    predecessor_v3 = contract.get("immutable_v3_predecessor")
    require(type(predecessor_v3) is dict and predecessor_v3.get("owners") == V3_OWNERS,
            "V4 must retain all exact immutable V3 source, protocol, and contract pins")
    actual = predecessor_v3.get("actual_failure_receipt")
    require(type(actual) is dict and actual.get("path") == V3_FAILURE_RECEIPT_PATH
            and actual.get("sha256") == V3_FAILURE_RECEIPT_SHA256
            and actual.get("bytes") == V3_FAILURE_RECEIPT_BYTES
            and actual.get("device") == V3_FAILURE_RECEIPT_DEVICE
            and actual.get("inode") == V3_FAILURE_RECEIPT_INODE
            and actual.get("mode") == "0600" and actual.get("status") == "FAIL"
            and actual.get("finding_count") == 7,
            "V4 must preserve the exact complete V3 seven-finding source audit")
    lexer = contract.get("rust_lexer")
    require(type(lexer) is dict and lexer.get("rust_lifetimes") is True
            and lexer.get("rust_loop_labels") is True and lexer.get("rust_raw_strings") is True
            and lexer.get("rust_byte_literals") is True
            and lexer.get("rust_nested_block_comments") is True
            and lexer.get("computed_or_obfuscated_engine_dispatch") == "FORBIDDEN",
            "V3 Rust lexical repair is incomplete or weakens the V2 no-delegation policy")


def verify_v2_lineage(wall: EffectWall) -> dict[str, object]:
    owners: dict[str, dict[str, object]] = {}
    contracts: dict[str, bytes] = {}
    for path, fingerprint in V2_OWNERS.items():
        raw, owner = read_file_at(ROOT, path, wall, category="historical_v2_owner_reads")
        require(owner["sha256"] == fingerprint,
                "immutable V2 predecessor owner changed: " + path)
        owners[path] = owner
        if path.endswith(".json"):
            contracts[path] = raw
    v2 = strict_json(contracts["oracle/phase2/runtime-non-delegation-v2.json"],
                     "immutable V2 contract")
    require(v2.get("schema") == "rebar-phase2-first-party-runtime-non-delegation-v2"
            and v2.get("version") == 2,
            "V2 immutable predecessor no longer has its published schema")
    frozen = v2.get("source_freeze")
    require(type(frozen) is dict
            and frozen.get("source", {}).get("sha256") ==
            V2_OWNERS["tools/audit_candidate_runtime_non_delegation_v2.py"]
            and frozen.get("protocol", {}).get("sha256") ==
            V2_OWNERS["oracle/phase2/RUNTIME-NON-DELEGATION-V2.md"],
            "V2 predecessor no longer internally binds its own authentic sources")
    raw, owner = read_file_at(ROOT, V2_FAILURE_RECEIPT_PATH, wall,
                              category="public_failure_receipt_reads", maximum=4096)
    require(owner["sha256"] == V2_FAILURE_RECEIPT_SHA256
            and owner["bytes"] == V2_FAILURE_RECEIPT_BYTES
            and owner["device"] == V2_FAILURE_RECEIPT_DEVICE
            and owner["inode"] == V2_FAILURE_RECEIPT_INODE
            and owner["mode"] == f"{V2_FAILURE_RECEIPT_MODE:04o}",
            "public V2 failure receipt digest, size, device, inode, or mode changed")
    receipt = strict_json(raw, V2_FAILURE_RECEIPT_PATH)
    require(receipt.get("schema") ==
            "rebar-phase2-first-party-runtime-non-delegation-v2-entry-failure"
            and receipt.get("status") == "FAIL"
            and receipt.get("error_type") == "AuditError"
            and receipt.get("message") ==
            "candidates/rust/src/lib.rs:252: unterminated native literal"
            and receipt.get("candidate_executions") == 0
            and receipt.get("candidate_workers") == 0
            and receipt.get("native_library_loads") == 0
            and receipt.get("candidate_qualified") is False
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("winner_selected") is False,
            "the actual V2 failure receipt was suppressed, mutated, or overstated")
    v2_result = {"owners": owners, "actual_failure_receipt": owner,
                 "actual_failure": receipt, "v2_candidate_executions": 0,
                 "v2_runtime_non_delegation": "NOT ESTABLISHED"}
    v3_owners: dict[str, dict[str, object]] = {}
    v3_contract_raw = b""
    for path, fingerprint in V3_OWNERS.items():
        raw, prior_owner = read_file_at(ROOT, path, wall,
                                        category="historical_v3_owner_reads")
        require(prior_owner["sha256"] == fingerprint,
                "immutable V3 predecessor owner changed: " + path)
        v3_owners[path] = prior_owner
        if path.endswith(".json"):
            v3_contract_raw = raw
    v3_contract = strict_json(v3_contract_raw, "immutable V3 contract")
    require(v3_contract.get("schema") ==
            "rebar-phase2-first-party-runtime-non-delegation-v3"
            and v3_contract.get("version") == 3,
            "V3 immutable predecessor no longer has its published schema")
    frozen_v3 = v3_contract.get("source_freeze")
    require(type(frozen_v3) is dict
            and frozen_v3.get("source", {}).get("sha256") ==
            V3_OWNERS["tools/audit_candidate_runtime_non_delegation_v3.py"]
            and frozen_v3.get("protocol", {}).get("sha256") ==
            V3_OWNERS["oracle/phase2/RUNTIME-NON-DELEGATION-V3.md"]
            and v3_contract.get("immutable_v2_predecessor", {}).get("owners") == V2_OWNERS,
            "V3 predecessor no longer authenticates its V2/V3 lineage")
    v3_raw, v3_owner = read_file_at(ROOT, V3_FAILURE_RECEIPT_PATH, wall,
                                    category="public_failure_receipt_reads", maximum=65536)
    require(v3_owner["sha256"] == V3_FAILURE_RECEIPT_SHA256
            and v3_owner["bytes"] == V3_FAILURE_RECEIPT_BYTES
            and v3_owner["device"] == V3_FAILURE_RECEIPT_DEVICE
            and v3_owner["inode"] == V3_FAILURE_RECEIPT_INODE
            and v3_owner["mode"] == f"{V3_FAILURE_RECEIPT_MODE:04o}",
            "public V3 complete source-audit receipt digest, owner, or mode changed")
    v3_receipt = strict_json(v3_raw, V3_FAILURE_RECEIPT_PATH)
    v3_effects = v3_receipt.get("effects")
    v3_findings = v3_receipt.get("findings")
    require(v3_receipt.get("schema") ==
            "rebar-phase2-first-party-runtime-non-delegation-v3-root-static-audit"
            and v3_receipt.get("status") == "FAIL"
            and v3_receipt.get("finding_count") == 7
            and type(v3_findings) is list and len(v3_findings) == 7
            and [item.get("code") for item in v3_findings] == [
                "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE", "CANDIDATE_CTYPES_IMPORT",
                "CANDIDATE_DYNAMIC_LIBRARY_LOAD", "PUBLIC_FACADE_CANDIDATE_WRAPPER",
                "PUBLIC_FACADE_CANDIDATE_WRAPPER", "PUBLIC_FACADE_CANDIDATE_WRAPPER",
                "PUBLIC_FACADE_TRANSITIVE_CTYPES",
            ]
            and type(v3_effects) is dict
            and all(v3_effects.get(key) == 0 for key in (
                "candidate_executions", "candidate_workers", "candidate_imports",
                "native_library_loads", "holdout_reads", "compiler_processes",
                "archive_reads", "archive_decompressions", "workspace_mutations",
            ))
            and v3_receipt.get("candidate_qualified") is False
            and v3_receipt.get("holdout") == "NOT OPENED"
            and v3_receipt.get("runtime_non_delegation") ==
            "NOT ESTABLISHED; CANDIDATES NEVER EXECUTED",
            "the complete V3 seven-finding audit was suppressed, mutated, or overstated")
    return {"immutable_v2": v2_result,
            "immutable_v3": {"owners": v3_owners,
                              "actual_failure_receipt": v3_owner,
                              "finding_count": 7,
                              "candidate_executions": 0,
                              "runtime_non_delegation": "NOT ESTABLISHED"}}


def verify_zero_effects(effects: dict[str, int], *, owner_reads: int = 0,
                        v2_owner_reads: int = 0,
                        v3_owner_reads: int = 0,
                        public_failure_receipt_reads: int = 0) -> None:
    require(effects["approved_owner_reads"] == owner_reads,
            "unexpected number of explicitly approved source-owner reads")
    require(effects["historical_v2_owner_reads"] == v2_owner_reads,
            "unexpected number of exact immutable V2 predecessor reads")
    require(effects["historical_v3_owner_reads"] == v3_owner_reads,
            "unexpected number of exact immutable V3 predecessor reads")
    require(effects["public_failure_receipt_reads"] == public_failure_receipt_reads,
            "unexpected number of exact public V2 failure-receipt reads")
    for key, value in effects.items():
        if key not in {"approved_owner_reads", "historical_v2_owner_reads",
                       "historical_v3_owner_reads", "public_failure_receipt_reads"}:
            require(value == 0, "source-only mode attempted forbidden effect: " + key)


def verify_source(options: dict[str, object]) -> dict[str, object]:
    require(tuple(sys.version_info[:3]) == PINNED_VERSION,
            "source verification requires pinned CPython 3.14.6")
    pins = {SOURCE: exact_sha(options.get("source_sha256"), "source"),
            PROTOCOL: exact_sha(options.get("protocol_sha256"), "protocol"),
            CONTRACT: exact_sha(options.get("contract_sha256"), "contract")}
    require(len(set(pins.values())) == 3, "pin all three distinct sole-owned source files")
    with EffectWall() as wall:
        raw: dict[str, bytes] = {}
        owners: dict[str, dict[str, object]] = {}
        for path in (SOURCE, PROTOCOL, CONTRACT):
            payload, owner = read_file_at(ROOT, path, wall, category="approved_owner_reads")
            require(owner["sha256"] == pins[path], path + ": published SHA-256 pin mismatch")
            raw[path], owners[path] = payload, owner
        contract = strict_json(raw[CONTRACT], CONTRACT)
        validate_contract(contract)
        freeze = contract["source_freeze"]
        require(freeze["source"]["sha256"] == pins[SOURCE]
                and freeze["protocol"]["sha256"] == pins[PROTOCOL],
                "contract does not bind the independently supplied source/protocol pins")
        predecessor = verify_v2_lineage(wall)
        effects = dict(wall.effects)
        verify_zero_effects(effects, owner_reads=11, v2_owner_reads=3,
                            v3_owner_reads=3, public_failure_receipt_reads=2)
    return {
        "schema": SCHEMA + "-source-verification", "status": "PASS",
        "phase": "FROZEN SOURCE ONLY; NO CANDIDATE OR STDLIB OWNERS OPENED",
        "owners": owners, "immutable_predecessors": predecessor, "effects": effects,
        "current_candidate_source_audit": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED", "candidate_qualified": False,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED", "winner_selected": False,
    }


def synthetic_elf(needed: tuple[str, ...], imported: tuple[str, ...],
                  exported: tuple[str, ...], *, runpath: str | None = None) -> bytes:
    strings = bytearray(b"\x00")

    def add(value: str) -> int:
        offset = len(strings)
        strings.extend(value.encode("ascii") + b"\x00")
        return offset

    needed_offsets = [add(value) for value in needed]
    imported_offsets = [add(value) for value in imported]
    exported_offsets = [add(value) for value in exported]
    runpath_offset = add(runpath) if runpath is not None else None
    shstr = b"\x00.shstrtab\x00.dynstr\x00.dynsym\x00.dynamic\x00"
    shstr_names = {name: shstr.index(name.encode("ascii"))
                   for name in (".shstrtab", ".dynstr", ".dynsym", ".dynamic")}
    symbols = bytearray(struct.pack("<IBBHQQ", 0, 0, 0, 0, 0, 0))
    for offset in imported_offsets:
        symbols.extend(struct.pack("<IBBHQQ", offset, 0x12, 0, 0, 0, 0))
    for offset in exported_offsets:
        symbols.extend(struct.pack("<IBBHQQ", offset, 0x12, 0, 1, 1, 1))
    dynamic = bytearray()
    for offset in needed_offsets:
        dynamic.extend(struct.pack("<qQ", 1, offset))
    if runpath_offset is not None:
        dynamic.extend(struct.pack("<qQ", 29, runpath_offset))
    dynamic.extend(struct.pack("<qQ", 0, 0))
    payload = bytearray(b"\x00" * 64)

    def put(data: bytes | bytearray) -> tuple[int, int]:
        while len(payload) % 8:
            payload.append(0)
        start = len(payload)
        payload.extend(data)
        return start, len(data)

    names_at, names_size = put(shstr)
    strings_at, strings_size = put(strings)
    symbols_at, symbols_size = put(symbols)
    dynamic_at, dynamic_size = put(dynamic)
    while len(payload) % 8:
        payload.append(0)
    sections_at = len(payload)
    records = [struct.pack("<IIQQQQIIQQ", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
    records.append(struct.pack("<IIQQQQIIQQ", shstr_names[".shstrtab"], 3, 0, 0,
                               names_at, names_size, 0, 0, 1, 0))
    records.append(struct.pack("<IIQQQQIIQQ", shstr_names[".dynstr"], 3, 0, 0,
                               strings_at, strings_size, 0, 0, 1, 0))
    records.append(struct.pack("<IIQQQQIIQQ", shstr_names[".dynsym"], 11, 0, 0,
                               symbols_at, symbols_size, 2, 1, 8, 24))
    records.append(struct.pack("<IIQQQQIIQQ", shstr_names[".dynamic"], 6, 0, 0,
                               dynamic_at, dynamic_size, 2, 0, 8, 16))
    payload.extend(b"".join(records))
    identifier = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8
    payload[:64] = struct.pack("<16sHHIQQQIHHHHHH", identifier, 3, 62, 1, 0, 0,
                              sections_at, 0, 64, 0, 0, 64, len(records), 1)
    return bytes(payload)


def source_self_test() -> dict[str, object]:
    require(tuple(sys.version_info[:3]) == PINNED_VERSION,
            "source self-test requires pinned CPython 3.14.6")
    positives = 0
    hostile = 0

    def accept(function: object, *arguments: object, **keywords: object) -> object:
        nonlocal positives
        result = function(*arguments, **keywords)
        if type(result) is dict and type(result.get("findings")) is list:
            require(not result["findings"], "clean fixture produced a false-positive finding")
        positives += 1
        return result

    def reject(function: object, *arguments: object, **keywords: object) -> None:
        nonlocal hostile
        try:
            result = function(*arguments, **keywords)
        except (AuditError, ValueError, TypeError, SyntaxError, UnicodeError, RecursionError):
            hostile += 1
            return
        if type(result) is dict and type(result.get("findings")) is list and result["findings"]:
            hostile += 1
            return
        raise AuditError("hostile synthetic source accepted by " + function.__name__
                         + ": " + repr(arguments)[:512])

    with EffectWall() as wall:
        for family, config in FAMILIES.items():
            clean = "import enum\nimport warnings\nfrom candidates import " + str(config["bridge"]) + "\n"
            accept(inspect_python, clean, family, "fixture.py")
            for attack in (
                "import re\n", "import re as engine\n", "from re import compile\n",
                "from re._compiler import compile\n", "import _sre\n", "import regex\n",
                "import re2\n", "import pcre2\n", "import inspect\n", "import ctypes\n",
                "import ctypes as native\nnative.CDLL('foreign.so')\n",
                "from ctypes import CDLL as load\nload('foreign.so')\n",
                "import importlib as loader\nloader.import_module('r' + 'e')\n",
                "from importlib import import_module as load\nload(chr(114) + 'e')\n",
                "__import__('r' + 'e')\n", "getattr(__import__, '__call__')('re')\n",
                "import sys\nsys.modules['r' + 'e']\n", "eval('import re')\n",
            ):
                reject(inspect_python, clean + attack, family, "fixture.py")
            for other, foreign in FAMILIES.items():
                if other != family:
                    reject(inspect_python,
                           clean + "from candidates import " + str(foreign["bridge"]) + "\n",
                           family, "fixture.py")
        for fixture in (
            "import enum\nimport warnings\nfrom candidates import _rust_bridge\n",
            "from copyreg import _reconstructor\nfrom struct import calcsize\n"
            "from candidates import _vm_native\n",
        ):
            accept(inspect_python, fixture, "rust" if "_rust_bridge" in fixture else "c_vm", "fixture.py")
        for facade in (
            "from candidates.zig_candidate import *\n",
            "from candidates.zig_candidate import DEBUG, Scanner\n",
            "from candidates.zig_candidate import __all__\n",
        ):
            accept(inspect_python, facade, "zig", "rebar.py", facade=True)
        selected_facade = accept(
            inspect_python,
            "from candidates.zig_candidate import *\n"
            "from candidates.zig_candidate import DEBUG, Scanner\n"
            "from candidates.zig_candidate import __all__\n",
            "zig", "rebar.py", facade=True,
        )
        for facade in (
            "from candidates.rust_candidate import compile as borrowed\n",
            "from candidates.vm_candidate import compile\n",
            "import candidates.rust_candidate as borrowed\n",
            "from re import compile\n",
            "import regex\n",
            "from candidates import _rust_bridge\n",
        ):
            reject(inspect_python, facade, "zig", "rebar.py", facade=True)

        owned_zig_ffi = (
            "import ctypes\nimport os\nfrom candidates import _zig_bridge\n"
            "class _Native:\n"
            "    def __init__(self):\n"
            "        path = os.path.join(os.path.dirname(__file__), \"_zig_probe.so\")\n"
            "        self.library = ctypes.CDLL(path)\n"
        )
        accepted_ffi = accept(inspect_python, owned_zig_ffi, "zig",
                              "candidates/zig_candidate.py")
        require(accepted_ffi["owned_ctypes_imports"] == 1
                and accepted_ffi["owned_first_party_native_anchors"] == 1
                and accepted_ffi["owned_first_party_native_loaders"] == 1,
                "exact same-family first-party FFI must remain permissible")
        hostile_ffi = (
            owned_zig_ffi.replace('"_zig_probe.so"', '"libpcre2.so"'),
            owned_zig_ffi.replace('"_zig_probe.so"', '"_rust_engine.so"'),
            owned_zig_ffi.replace('"_zig_probe.so"', '"../_zig_probe.so"'),
            owned_zig_ffi.replace('"_zig_probe.so"', '"/tmp/_zig_probe.so"'),
            owned_zig_ffi.replace('"_zig_probe.so"', '"_zig_" + "probe.so"'),
            owned_zig_ffi.replace('"_zig_probe.so"', 'os.getenv("FOREIGN_ENGINE")'),
            owned_zig_ffi.replace('os.path.dirname(__file__)',
                                  'os.path.realpath(os.path.dirname(__file__))'),
            owned_zig_ffi.replace('os.path.dirname(__file__), "_zig_probe.so"',
                                  'os.path.dirname(__file__), "..", "_zig_probe.so"'),
            owned_zig_ffi.replace('ctypes.CDLL(path)', 'ctypes.CDLL(path, mode=0)'),
            owned_zig_ffi.replace('ctypes.CDLL(path)', 'ctypes.CDLL(path, handle=0)'),
            owned_zig_ffi.replace('ctypes.CDLL(path)', 'ctypes.PyDLL(path)'),
            owned_zig_ffi.replace('ctypes.CDLL(path)', 'ctypes.CDLL("_zig_probe.so")'),
            owned_zig_ffi.replace('ctypes.CDLL(path)', 'ctypes.cdll.LoadLibrary(path)'),
            owned_zig_ffi.replace('ctypes.CDLL(path)', 'ctypes.CDLL(os.fspath(path))'),
            owned_zig_ffi.replace('ctypes.CDLL(path)',
                                  'ctypes.CDLL(os.path.join(os.path.dirname(__file__), "_zig_probe.so"))'),
            owned_zig_ffi.replace('self.library = ctypes.CDLL(path)',
                                  'path = "/tmp/libpcre2.so"\n        self.library = ctypes.CDLL(path)'),
            owned_zig_ffi.replace('self.library = ctypes.CDLL(path)',
                                  'path += ".bad"\n        self.library = ctypes.CDLL(path)'),
            owned_zig_ffi.replace('self.library = ctypes.CDLL(path)',
                                  'del path\n        self.library = ctypes.CDLL(path)'),
            owned_zig_ffi.replace('self.library = ctypes.CDLL(path)',
                                  'native = ctypes\n        self.library = native.CDLL(path)'),
            owned_zig_ffi.replace('self.library = ctypes.CDLL(path)',
                                  'self.library = getattr(ctypes, "CD" + "LL")(path)'),
            owned_zig_ffi.replace('self.library = ctypes.CDLL(path)',
                                  'self.library = ctypes.CDLL(path)\n        again = ctypes.CDLL(path)'),
            owned_zig_ffi.replace('import ctypes', 'import ctypes as native').replace('ctypes.CDLL', 'native.CDLL'),
            owned_zig_ffi.replace('import ctypes', 'from ctypes import CDLL').replace('ctypes.CDLL', 'CDLL'),
            owned_zig_ffi.replace('class _Native:', 'class Foreign:'),
            owned_zig_ffi.replace('def __init__(self):', 'def load(self):'),
            owned_zig_ffi + 'ctypes.CDLL("libpcre2.so")\n',
            owned_zig_ffi + 'import pip\n',
            owned_zig_ffi + 'import _ctypes\n_ctypes.dlopen("libpcre2.so")\n',
            owned_zig_ffi + 'import ensurepip\nensurepip.bootstrap()\n',
            owned_zig_ffi + 'import subprocess\nsubprocess.run(["pip", "install", "regex"])\n',
            owned_zig_ffi + 'import re\nre.compile("foreign")\n',
            owned_zig_ffi + 'from candidates import _rust_bridge\n',
            owned_zig_ffi + 'import importlib\nimportlib.import_module("regex")\n',
        )
        for fixture in hostile_ffi:
            reject(inspect_python, fixture, "zig", "candidates/zig_candidate.py")
        reject(inspect_python, owned_zig_ffi, "rust", "candidates/rust_candidate.py")
        reject(inspect_python, owned_zig_ffi, "zig", "fixture.py")

        clean_c = '#include <Python.h>\nPyImport_ImportModule("copyreg");\n'
        accept(inspect_native, clean_c, "rust", "fixture.c", "c")
        accept(inspect_native,
               '// PyImport_ImportModule("re") and dlopen("pcre") are comments\n'
               'const char *message = "pcre2_match dlopen re";\n',
               "rust", "fixture.c", "c")
        accept(inspect_native, 'const std = @import("std");\n',
               "zig", "fixture.zig", "zig")
        accept(inspect_native, '#include "engine.hpp"\n', "cpp", "fixture.cpp", "cpp")
        for module in ("copyreg", "functools", "unicodedata"):
            accept(inspect_native, 'PyImport_ImportModule("' + module + '");\n',
                   "rust", "fixture.c", "c")
        for attack in (
            'PyImport_ImportModule("inspect");\n',
            'PyImport_ImportModule("re");\n',
            'PyImport_ImportModule("r" "e");\n',
            'PyImport_ImportModule("\\x72\\x65");\n',
            'PyImport_ImportModule("_sre");\n',
            'PyImport_ImportModule(module_name);\n',
            '#define ALIAS PyImport_ImportModule\nALIAS("re");\n',
            'dlopen("libpcre2.so", 1);\n', 'dlsym(handle, "pcre2_match");\n',
            'regcomp(pattern, flags);\n', 'pcre2_match_8(pattern);\n',
            'onig_search_gpos(pattern);\n', 're2_match(pattern);\n',
            '#include <pcre2.h>\n', '#include "foreign.hpp"\n',
            'PyRun_SimpleString("import re");\n', '/* unterminated',
        ):
            reject(inspect_native, clean_c + attack, "rust", "fixture.c", "c")
        for attack in (
            '@import("regex")', '@import("pcre2")', '@import(computed)',
            '@cImport({ @cInclude("pcre2.h"); })', 'std.DynLib.open(path)',
            'rebar_go_compile()', 'rebar_fortran_compile()', 'rebar_compile()',
            'std.Build.Step.Compile.linkSystemLibrary("pcre2")',
        ):
            reject(inspect_native, 'const std = @import("std");\n' + attack,
                   "zig", "fixture.zig", "zig")
        accept(inspect_native, 'import "C"\nimport ("fmt" "sync")\n',
               "go", "fixture.go", "go")
        accept(inspect_native, 'use std::mem;\nuse stack::InlineStack;\n',
               "rust", "fixture.rs", "rust")
        accept(inspect_native, 'use, intrinsic :: iso_c_binding\n',
               "fortran", "fixture.f90", "fortran")
        for family, kind, attack in (
            ("go", "go", 'import "regexp"\n'),
            ("go", "go", 'import ("fmt" "github.com/foreign/re2")\n'),
            ("go", "go", '/*\n#cgo LDFLAGS: -lpcre2\n*/\nimport "C"\n'),
            ("rust", "rust", 'use regex::Regex;\n'),
            ("rust", "rust", 'extern crate regex;\n'),
            ("fortran", "fortran", 'use foreign_regex_engine\n'),
        ):
            reject(inspect_native, attack, family, "fixture." + kind, kind)

        rust_clean = (
            "struct BorrowedText<'a> { bytes: &'a [u8] }\n"
            "impl<'a> BorrowedText<'a> { fn bytes(&'a self) -> &'a [u8] { self.bytes } }\n",
            "let reference: &'static str = \"owned\";\n",
            "fn borrowed<'_, 'alpha>(value: &'alpha str) -> &'alpha str { value }\n",
            "'outer: loop { 'inner: loop { break 'outer; } }\n",
            "let character = 'a'; let quoted = '\\''; let escaped = '\\n';\n",
            "let byte = b'a'; let escaped_byte = b'\\x7f';\n",
            "let unicode = '🦀'; let escaped_unicode = '\\u{1F980}';\n",
            'let raw = r"use regex::Regex; pcre2_match();";\n',
            'let raw = r#"use regex::Regex; dlopen("pcre2")"#;\n',
            'let raw = r###"raw # " ## text use regex::Regex"###;\n',
            'let bytes = br##"pcre2_match(); use regex::Regex;"##;\n',
            'let c_text = cr#"use regex::Regex; dlopen("pcre")"#;\n',
            'let unicode = "\\u{1F980} use regex::Regex;";\n',
            '/// use regex::Regex; dlopen("pcre2")\n//! pcre2_match()\nlet owned = 1;\n',
            '/* outer use regex /* middle pcre2_match /* nested */ */ */\nuse std::slice;\n',
            'unsafe extern "C" { fn Py_GetRecursionLimit() -> i32; }\n',
            'fn r#match(value: usize) -> usize { value }\n',
        )
        for fixture in rust_clean:
            accept(inspect_native, fixture, "rust", "fixture.rs", "rust")
        rust_hostile = (
            "struct BorrowedText<'a> { bytes: &'a [u8] }\nuse regex::Regex;\n",
            "'outer: loop { break 'outer; }\nuse regex::Regex;\n",
            'let safe = r#"use std::slice;"#;\nuse regex::Regex;\n',
            'let safe = br###"pcre2_match"###;\npcre2_match(pattern);\n',
            '/* allowed /* nested */ */\nonig_search(pattern);\n',
            'unsafe extern "C" { fn pcre2_match_8(); }\n',
            'unsafe extern "C" { fn dlopen(); }\n',
            'extern crate regex;\n',
            'concat!("reg", "ex");\n',
            'concat_idents!(reg, ex);\n',
            'include!("foreign_regex.rs");\n',
            'include_bytes!("foreign_engine.so");\n',
            'include_str!("foreign_engine.rs");\n',
            'macro_rules! hidden { () => { use regex::Regex; } }\n',
            'env!("FOREIGN_REGEX_ENGINE");\n',
            'option_env!("FOREIGN_REGEX_ENGINE");\n',
            'asm!("call pcre2_match");\n',
            '#[link(name = "pcre2")] unsafe extern "C" {}\n',
            '#[link_name = "pcre2_match"] fn outside();\n',
            'let engine = libloading::Library::new("libpcre2.so");\n',
            'let process = std::process::Command::new("foreign-regex");\n',
            'let broken = r###"unterminated"##;\n',
            'let broken = br#"unterminated"##;\n',
            "let broken = 'ab';\n",
            "let broken = b'ab';\n",
            "let broken = b'🦀';\n",
            "let broken = '\\xq0';\n",
            "let broken = '\\u{}';\n",
            '/* outer /* inner */\n',
            "let broken = ' ;\n",
        )
        for fixture in rust_hostile:
            reject(inspect_native, fixture, "rust", "fixture.rs", "rust")

        manifest = (
            '[package]\nname="rebar-rust-continuation"\nversion="0.1.0"\n'
            'publish=false\n[lib]\ncrate-type=["cdylib"]\n'
        )
        lock = 'version=4\n[[package]]\nname="rebar-rust-continuation"\nversion="0.1.0"\n'
        project = '[project]\nname="rebar-experiment"\ndependencies=[]\n'
        project_lock = 'version=1\n[[package]]\nname="rebar-experiment"\n'
        go_manifest = 'module rebar.local/candidates/go\n\ngo 1.26.0\n'
        accept(inspect_rust_manifest, manifest)
        accept(inspect_rust_lock, lock)
        accept(inspect_project_manifest, project)
        accept(inspect_project_lock, project_lock)
        accept(inspect_go_manifest, go_manifest)
        for extension in (
            '[dependencies]\nregex="1"\n', '[dev-dependencies]\nregex="1"\n',
            '[build-dependencies]\nregex="1"\n',
            '[target."cfg(unix)".dependencies]\nregex="1"\n',
            '[workspace.dependencies]\nregex="1"\n',
            '[patch.crates-io]\nregex={git="https://foreign.invalid/regex"}\n',
        ):
            reject(inspect_rust_manifest, manifest + extension)
        for extension in (
            '\ndependencies=["regex"]\n',
            '\n[[package]]\nname="regex"\nversion="1.0"\n',
            '\nsource="registry+https://foreign.invalid"\n',
        ):
            reject(inspect_rust_lock, lock + extension)
        reject(inspect_project_manifest, project.replace("dependencies=[]", 'dependencies=["regex"]'))
        reject(inspect_project_manifest, project + '\n[project.optional-dependencies]\nfast=["re2"]\n')
        reject(inspect_project_lock, project_lock + '\ndependencies=[{name="pcre2"}]\n')
        for directive in (
            'require github.com/foreign/re2 v1.0.0\n',
            'replace rebar.local/candidates/go => /tmp/foreign\n',
            'tool github.com/foreign/regexp\n',
        ):
            reject(inspect_go_manifest, go_manifest + directive)

        clean_engine = synthetic_elf(("libc.so.6",), ("malloc",),
                                     ("rebar_zig_compile", "rebar_zig_match_wide"))
        clean_bridge = synthetic_elf(("libc.so.6", "_zig_probe.so"),
                                     ("PyImport_ImportModule", "rebar_zig_compile"),
                                     ("PyInit__zig_bridge",), runpath="$ORIGIN")
        engine_proof = accept(inspect_elf, clean_engine, "zig", "engine",
                              "candidates/_zig_probe.so")
        bridge_proof = accept(inspect_elf, clean_bridge, "zig", "bridge",
                              "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so")
        proof_paths = (
            "candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c", "candidates/_zig_probe.so",
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        )
        proof_rows: list[dict[str, object]] = [accepted_ffi]
        proof_rows.extend({"family": "zig", "path": value}
                          for value in proof_paths[1:3])
        proof_rows.extend((engine_proof, bridge_proof))
        for index, item in enumerate(proof_rows, 1):
            item["owner"] = {
                "path": item["path"], "bytes": index, "device": 1,
                "inode": index, "mode": "0700" if index > 3 else "0600",
                "sha256": format(index, "064x"),
            }
        accept(verify_owned_zig_ffi, proof_rows, selected_facade)
        for mutation in (
            (3, "path", "candidates/_rust_engine.so"),
            (3, "mode", "0600"),
            (3, "device", 2),
            (3, "inode", 1),
            (3, "sha256", "not-an-authenticated-sha256"),
        ):
            index, key, replacement = mutation
            previous = proof_rows[index]["owner"][key]
            proof_rows[index]["owner"][key] = replacement
            reject(verify_owned_zig_ffi, proof_rows, selected_facade)
            proof_rows[index]["owner"][key] = previous
        for fixture in (
            synthetic_elf(("libpcre2-8.so.0",), (),
                          ("rebar_zig_compile", "rebar_zig_match_wide")),
            synthetic_elf(("libgcc_s.so.1",), (),
                          ("rebar_zig_compile", "rebar_zig_match_wide")),
            synthetic_elf(("libc.so.6",), ("pcre2_match_8",),
                          ("rebar_zig_compile", "rebar_zig_match_wide")),
            synthetic_elf(("libc.so.6",), ("dlopen",),
                          ("rebar_zig_compile", "rebar_zig_match_wide")),
            synthetic_elf(("libc.so.6",), ("rebar_go_compile",),
                          ("rebar_zig_compile", "rebar_zig_match_wide")),
            synthetic_elf(("libc.so.6",), (), ("rebar_zig_compile",)),
            synthetic_elf(("libc.so.6",), (),
                          ("rebar_zig_compile", "rebar_zig_match_wide"), runpath="/tmp/foreign"),
            clean_engine[:63],
        ):
            reject(inspect_elf, fixture, "zig", "engine", "fixture.so")
        adapter = (
            "from candidates import _rust_bridge\n_NATIVE_BIND = _rust_bridge.bind\n"
            "_rust_bridge.pattern_descriptors(Pattern)\n"
        )
        bridge = ('rust_bound_get_signature() {}\nbridge_bind() {}\n'
                  'PyDescr_NewMethod(x);\n{"bind", fn};\n')
        reachability = accept(rust_reachability, adapter, bridge)
        require(reachability["classification"].startswith("LATENT_PRIVATE_BRIDGE")
                and reachability["public_matching_delegation_proven"] is False,
                "do not misclassify a dead private native getter as public matching")
        for attack in ("../private", ".git/config", "oracle/phase3/holdout.json",
                       "oracle/phase2/evidence/report.json.gz", "performance/bench.py",
                       "candidates/../rust_candidate.py", "/tmp/private-owner"):
            reject(checked_relative, attack)
        accept(checked_relative, SOURCE)
        accept(checked_relative, V2_FAILURE_RECEIPT_PATH, allow_public_failure_receipt=True)
        accept(checked_relative, V3_FAILURE_RECEIPT_PATH, allow_public_failure_receipt=True)
        for attack in (
            "oracle/phase2/evidence/runtime-non-delegation-v2-actual-source-lexer-failure.json.gz",
            "oracle/phase2/evidence/another-public-receipt.json",
            "oracle/phase2/evidence/../runtime-non-delegation-v2-actual-source-lexer-failure.json",
        ):
            reject(checked_relative, attack, allow_public_failure_receipt=True)
        require(positives >= 49 and hostile >= 270,
                f"synthetic adversarial coverage unexpectedly shrank: {positives} clean/{hostile} hostile")
        effects = dict(wall.effects)
        verify_zero_effects(effects)
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "positive_controls": positives, "hostile_controls": hostile,
        "candidate_native_inspect_is_rejected": True,
        "host_owned_warning_and_enum_metadata_is_allowed": True,
        "authenticated_same_family_zig_ffi_is_allowed": True,
        "arbitrary_external_or_borrowed_ctypes_loaders_are_rejected": True,
        "same_family_first_party_public_facade_is_allowed": True,
        "external_or_cross_family_public_facades_are_rejected": True,
        "rust_private_getter_is_not_misreported_as_public_matching": True,
        "fake_external_engine_libraries_and_symbols_are_rejected": True,
        "rust_lifetimes_labels_raw_strings_and_byte_literals_are_accepted": True,
        "rust_hidden_external_engines_and_macro_obfuscation_are_rejected": True,
        "immutable_v2_failure_receipt_path_is_exact": True,
        "immutable_v3_failure_receipt_path_is_exact": True,
        "effects": effects, "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False, "holdout": "NOT OPENED",
    }


def run_static_audit(options: dict[str, object]) -> dict[str, object]:
    require(options.get("root_authorized") is True,
            "static candidate audit is ROOT-AGENT-ONLY and requires --root-authorized")
    pushed = exact_sha(options.get("pushed_source_sha256"), "pushed source")
    require(tuple(sys.version_info[:3]) == PINNED_VERSION,
            "static candidate audit requires pinned CPython 3.14.6")
    with EffectWall() as wall:
        source_raw, source_owner = read_file_at(ROOT, SOURCE, wall,
                                                category="approved_owner_reads")
        require(source_owner["sha256"] == pushed,
                "root's externally verified pushed source SHA-256 differs from this source")
        contract_raw, _ = read_file_at(ROOT, CONTRACT, wall,
                                      category="approved_owner_reads")
        contract = strict_json(contract_raw, CONTRACT)
        validate_contract(contract)
        require(contract["source_freeze"]["source"]["sha256"] == pushed,
                "static root audit is not bound to the published source contract")
        predecessor = verify_v2_lineage(wall)
        del source_raw
        stdlib_raw: dict[str, bytes] = {}
        for name, fingerprint in PINNED_STDLIB_OWNERS.items():
            raw, owner = read_file_at(PINNED_STDLIB, name, wall,
                                     category="pinned_stdlib_reads")
            require(owner["sha256"] == fingerprint,
                    "pinned CPython transitive source changed: " + name)
            stdlib_raw[name] = raw
        stdlib_graph = pinned_stdlib_graph(stdlib_raw)
        project_results = {}
        for name, inspector in (("pyproject.toml", inspect_project_manifest),
                                ("uv.lock", inspect_project_lock)):
            raw, _ = read_file_at(ROOT, name, wall, category="candidate_source_reads")
            project_results[name] = inspector(raw.decode("utf-8"))
        results: list[dict[str, object]] = []
        failures: list[dict[str, object]] = []
        source_cache: dict[str, str] = {}
        for family, configuration in FAMILIES.items():
            for path, kind in configuration["sources"]:
                raw, owner = read_file_at(ROOT, path, wall, category="candidate_source_reads")
                source = raw.decode("utf-8")
                source_cache[path] = source
                if kind == "python":
                    item = inspect_python(source, family, path)
                elif kind in {"c", "cpp", "rust", "zig", "go", "fortran"}:
                    item = inspect_native(source, family, path, kind)
                elif kind == "cargo_manifest":
                    item = {"family": family, "path": path,
                            "result": inspect_rust_manifest(source), "findings": []}
                elif kind == "cargo_lock":
                    item = {"family": family, "path": path,
                            "result": inspect_rust_lock(source), "findings": []}
                elif kind == "go_mod":
                    item = {"family": family, "path": path,
                            "result": inspect_go_manifest(source), "findings": []}
                else:
                    item = {"family": family, "path": path,
                            "result": "FIRST-PARTY MODULE SOURCE; NO EXTERNAL LOCK", "findings": []}
                item["owner"] = owner
                results.append(item)
                failures.extend(item.get("findings", ()))
            for path, role in configuration["binaries"]:
                raw, owner = read_file_at(ROOT, path, wall,
                                         category="candidate_binary_reads", maximum=MAX_BINARY_BYTES)
                item = inspect_elf(raw, family, role, path)
                item["owner"] = owner
                results.append(item)
        facade_raw, facade_owner = read_file_at(ROOT, "rebar.py", wall,
                                               category="candidate_source_reads")
        facade = inspect_python(facade_raw.decode("utf-8"), "zig", "rebar.py", facade=True)
        facade["owner"] = facade_owner
        failures.extend(facade["findings"])
        owned_zig_ffi = verify_owned_zig_ffi(results, facade)
        reachability = rust_reachability(source_cache["candidates/rust_candidate.py"],
                                         source_cache["candidates/rust/py_bridge.c"])
        require(not reachability["public_matching_delegation_proven"],
                "static source analysis cannot establish candidate runtime matching")
        effects = dict(wall.effects)
        for key in (
            "candidate_imports", "reference_imports", "imports_after_wall",
            "native_library_loads", "candidate_executions", "candidate_workers",
            "reference_workers", "compiler_processes", "subprocesses", "archive_reads",
            "archive_decompressions", "private_reads", "holdout_reads", "hidden_case_reads",
            "benchmark_reads", "network_requests", "threads_started", "clock_samples",
            "workspace_mutations", "git_reads",
        ):
            require(effects[key] == 0, "read-only static audit escaped its boundary: " + key)
    return {
        "schema": SCHEMA + "-root-static-audit", "status": "FAIL" if failures else "PASS",
        "phase": "ROOT-AUTHORIZED READ-ONLY SOURCE AND ELF AUDIT",
        "root_authorized": True, "pushed_source_sha256": pushed,
        "immutable_predecessors": predecessor,
        "project_dependencies": project_results, "pinned_stdlib_graph": stdlib_graph,
        "rust_reachability": reachability, "public_facade": facade,
        "first_party_zig_ffi_and_facade_provenance": owned_zig_ffi,
        "candidate_family_count": len(FAMILIES),
        "owners_and_binary_results": results, "finding_count": len(failures),
        "findings": failures, "effects": effects,
        "runtime_non_delegation": "NOT ESTABLISHED; CANDIDATES NEVER EXECUTED",
        "candidate_qualified": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "winner_selected": False,
    }


def parse_arguments(arguments: list[str]) -> dict[str, object]:
    require(bool(arguments), "choose --self-test, --verify-source, --audit, or --run-runtime-audit")
    mode = arguments[0]
    require(mode in {"--self-test", "--verify-source", "--audit", "--run-runtime-audit"},
            "unknown or noncanonical audit mode")
    result: dict[str, object] = {"mode": mode}
    index = 1
    mapping = {
        "--source-sha256": "source_sha256", "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256", "--pushed-source-sha256": "pushed_source_sha256",
    }
    while index < len(arguments):
        name = arguments[index]
        if name == "--root-authorized":
            require(mode == "--audit" and "root_authorized" not in result,
                    "root authorization applies only once to the static root audit")
            result["root_authorized"] = True
            index += 1
            continue
        require(name in mapping and index + 1 < len(arguments), "invalid audit argument " + name)
        field = mapping[name]
        require(field not in result, "duplicate audit pin " + name)
        result[field] = arguments[index + 1]
        index += 2
    if mode == "--self-test" or mode == "--run-runtime-audit":
        require(set(result) == {"mode"}, mode + " cannot authorize file reads or runtime work")
    elif mode == "--verify-source":
        require(set(result) == {"mode", "source_sha256", "protocol_sha256", "contract_sha256"},
                "source verification requires exactly three independently supplied owner pins")
    else:
        require(set(result) == {"mode", "root_authorized", "pushed_source_sha256"},
                "static candidate inspection requires explicit root authorization and a pushed source pin")
    return result


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if options["mode"] == "--self-test":
            result = source_self_test()
        elif options["mode"] == "--verify-source":
            result = verify_source(options)
        elif options["mode"] == "--audit":
            result = run_static_audit(options)
        else:
            result = {
                "schema": SCHEMA + "-unimplemented-runtime-audit", "status": "FAIL",
                "reason": "NOT IMPLEMENTED; FUTURE RUNTIME AUDIT IS ROOT-AGENT-ONLY",
                "candidate_executions": 0, "candidate_workers": 0,
                "native_library_loads": 0, "runtime_non_delegation": "NOT ESTABLISHED",
                "holdout": "NOT OPENED", "candidate_qualified": False,
            }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except (Exception, KeyboardInterrupt) as error:
        result = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__name__, "message": str(error)[:2048],
            "candidate_executions": 0, "candidate_workers": 0,
            "native_library_loads": 0, "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False, "holdout": "NOT OPENED",
            "performance": "NOT MEASURED", "winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
