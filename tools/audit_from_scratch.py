#!/usr/bin/env python3
"""Fail-closed, bounded provenance audit for the owned regex candidates.

This is an integrity audit, not a correctness or performance benchmark.  The
only repository inputs are the explicitly enumerated production files below.
Candidate imports occur only in a fresh, guarded Python subprocess.  ELF
inspection is implemented here with the standard library and is restricted to
the five explicitly authorized VM, Rust, and Zig binaries.  Each isolated
worker verifies the actual owned mappings in its own ``/proc/self/maps``.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import struct
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


MAX_ELF_BYTES = 64 * 1024 * 1024
MAX_PYTHON_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PYTHON_AST_NODES = 200000
MAX_NATIVE_SOURCE_BYTES = 16 * 1024 * 1024
MAX_ELF_SECTIONS = 4096
MAX_ELF_STRING_TABLE_BYTES = 16 * 1024 * 1024
MAX_ELF_STRING_BYTES = 4096
MAX_ELF_DYNAMIC_ENTRIES = 8192
MAX_ELF_DYNAMIC_SYMBOLS = 131072
MAX_PROC_MAP_BYTES = 4 * 1024 * 1024
MAX_PROC_MAP_ROWS = 16384
MAX_PROC_MAP_LINE_BYTES = 16384
MAX_WORKER_RESPONSE_BYTES = 256 * 1024
HASH_CHUNK_BYTES = 1024 * 1024
EXPECTED_SELF_TEST_CHECKS = 73
EXPECTED_SELF_TEST_NAMES = frozenset({
    "direct_stdlib_re",
    "direct_cpython_sre",
    "third_party_regex",
    "aliased_regex",
    "cross_candidate",
    "cross_candidate_dotted",
    "dynamic_import",
    "chr_obfuscated_import",
    "join_obfuscated_import",
    "importlib_indirection",
    "builtins_subscript",
    "getattr_indirection",
    "foreign_ctypes",
    "unowned_zig_library",
    "zig_owned_path_reassignment",
    "environment_dispatch",
    "environment_mapping",
    "external_process",
    "dynamic_eval",
    "dynamic_exec",
    "benchmark_clock",
    "holdout_path",
    "benchmark_file",
    "unowned_vm_configuration",
    "native_posix_regex",
    "native_pcre",
    "native_cpython_import",
    "native_dynamic_loader",
    "native_hidden_header",
    "native_hidden_extern",
    "rust_external_crate",
    "rust_environment",
    "rust_hidden_extern",
    "zig_external_package",
    "zig_hidden_extern",
    "zig_c_import",
    "native_benchmark_clock",
    "ignore_native_comments_and_display_literals",
    "preserve_rust_lifetimes_and_owned_pipeline",
    "parse_in_memory_owned_elf",
    "reject_excessive_elf_section_count",
    "reject_excessive_elf_symbol_string",
    "reject_in_memory_external_elf_dependency",
    "reject_bridge_without_owned_elf_link",
    "reject_disguised_third_party_elf_dependency",
    "accept_five_owned_synthetic_elf_binaries_and_python_api_symbols",
    "reject_vm_disguised_external_engine",
    "reject_vm_external_regex_symbol",
    "reject_vm_cross_candidate_engine_symbol",
    "reject_vm_untrusted_runpath",
    "reject_vm_wrong_module_initializer",
    "reject_zig_engine_disguised_external_dependency",
    "reject_zig_bridge_disguised_external_dependency",
    "reject_zig_bridge_wrong_linked_rust_engine",
    "reject_zig_bridge_wrong_engine_cross_candidate",
    "reject_zig_bridge_compiler_bypass",
    "reject_zig_bridge_executor_bypass",
    "reject_zig_bridge_unresolved_owned_symbols",
    "reject_zig_engine_untrusted_runpath",
    "reject_zig_bridge_untrusted_runpath",
    "reject_zig_rust_cross_candidate_symbol",
    "reject_rust_zig_cross_candidate_symbol",
    "reject_rust_bridge_untrusted_runpath",
    "accept_exact_ast_owned_memory_mappings",
    "accept_exact_vm_owned_memory_mappings",
    "accept_exact_rust_owned_memory_mappings",
    "accept_exact_zig_owned_memory_mappings",
    "reject_cross_candidate_actual_memory_mapping",
    "reject_external_regex_actual_memory_mapping",
    "reject_unapproved_candidate_actual_memory_mapping",
    "reject_deleted_owned_native_memory_mapping",
    "reject_invalid_elf",
    "reject_renamed_and_transitive_cargo_dependency",
})


ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
PYTHON_SOURCES = {
    "ast": ROOT / "candidates" / "ast_candidate.py",
    "vm": ROOT / "candidates" / "vm_candidate.py",
    "rust": ROOT / "candidates" / "rust_candidate.py",
    "zig": ROOT / "candidates" / "zig_candidate.py",
}
NATIVE_SOURCES = {
    "vm": (ROOT / "candidates" / "_vm_native.c",),
    "rust": (
        ROOT / "candidates" / "rust" / "py_bridge.c",
        ROOT / "candidates" / "rust" / "src" / "lib.rs",
        ROOT / "candidates" / "rust" / "src" / "search.rs",
        ROOT / "candidates" / "rust" / "src" / "newline.rs",
        ROOT / "candidates" / "rust" / "src" / "stack.rs",
        ROOT / "candidates" / "rust" / "src" / "unicode_tables.rs",
    ),
    "zig": (
        ROOT / "candidates" / "zig" / "py_bridge.c",
        ROOT / "candidates" / "zig" / "mini_regex.zig",
    ),
}
MANIFESTS = {
    "project": ROOT / "pyproject.toml",
    "rust": ROOT / "candidates" / "rust" / "Cargo.toml",
    "rust_lock": ROOT / "candidates" / "rust" / "Cargo.lock",
}
NATIVE_BINARIES = {
    "vm": {
        "native": ROOT / "candidates" / "_vm_native.cpython-314-x86_64-linux-gnu.so",
    },
    "rust": {
        "engine": ROOT / "candidates" / "_rust_engine.so",
        "bridge": ROOT / "candidates" / "_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    },
    "zig": {
        "engine": ROOT / "candidates" / "_zig_probe.so",
        "bridge": ROOT / "candidates" / "_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    },
}
RUST_BINARIES = NATIVE_BINARIES["rust"]
OWNED_BRIDGES = {
    "ast": None,
    "vm": "_vm_native",
    "rust": "_rust_bridge",
    "zig": "_zig_bridge",
}
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "re", "_sre", "sre", "sre_compile", "sre_parse", "sre_constants",
    "regex", "regex_lite", "regex_automata", "regex_syntax",
    "fancy_regex", "re2", "pcre", "pcre2", "onig", "oniguruma",
    "onigurumacffi", "_onigurumacffi", "hyperscan", "aho_corasick",
    "rebar",
})
FORBIDDEN_IMPORT_ROOTS = frozenset({
    "builtins", "cffi", "importlib", "marshal", "multiprocessing",
    "pathlib", "pickle", "runpy", "socket", "subprocess", "sys",
    "time", "timeit", "urllib",
})
BENCHMARK_MARKER = re.compile(
    r"(?:^|[/\\_.-])(?:benchmark|benchmarks|holdout|holdouts|"
    r"perf_counter|frozen[-_]performance|timeit)(?:$|[/\\_.-])",
    re.IGNORECASE,
)
NATIVE_RULES = (
    ("external_regex_call", re.compile(
        r"\b(?:regcomp|regexec|regerror|regfree|pcre(?:2)?_[A-Za-z_0-9]+|"
        r"onig_[A-Za-z_0-9]+|hs_(?:compile|scan)|re2_[A-Za-z_0-9]+)\s*\("
    )),
    ("external_regex_crate", re.compile(
        r"\b(?:regex|regex_lite|regex_automata|regex_syntax|fancy_regex|"
        r"pcre|pcre2|onig|onig_sys|re2|hyperscan|aho_corasick)::"
    )),
    ("cpython_regex_delegation", re.compile(
        r"\b(?:_sre|sre_compile|sre_parse|sre_constants|PyInit__sre)\b"
    )),
    ("dynamic_native_loader", re.compile(
        r"\b(?:dlopen|dlsym|dlmopen|LoadLibrary(?:A|W)?|GetProcAddress)\s*\("
    )),
    ("dynamic_code_or_process", re.compile(
        r"\b(?:PyRun_(?:String|SimpleString|File)|PyEval_EvalCode|"
        r"system|popen|fork|vfork|execve|execvp|posix_spawn)\s*\("
    )),
    ("external_native_package_loader", re.compile(
        r"@(?:cImport|extern|embedFile)\s*\(|#\s*\[\s*link\b"
    )),
    ("environment_configuration", re.compile(
        r"\b(?:getenv|secure_getenv|putenv|setenv)\s*\(|"
        r"\bstd\s*::\s*(?:env|process|time)\s*::|"
        r"\b(?:env|option_env|include|include_str|include_bytes)\s*!\s*\("
    )),
    ("benchmark_or_holdout_detection", re.compile(
        r"\b(?:benchmark|benchmarks|holdout|holdouts|perf_counter|"
        r"clock_gettime|gettimeofday|timeit)\b", re.IGNORECASE
    )),
)
RUST_REQUIRED_EXPORTS = frozenset({
    "rebar_compile", "rebar_match", "rebar_match_ascii",
    "rebar_match_wide", "rebar_collect_ascii", "rebar_collect_wide",
})
ZIG_REQUIRED_EXPORTS = frozenset({
    "rebar_zig_compile", "rebar_zig_free", "rebar_zig_groups",
    "rebar_zig_flags", "rebar_zig_name_count", "rebar_zig_name_length",
    "rebar_zig_name_group", "rebar_zig_name_copy",
    "rebar_zig_match_wide", "rebar_zig_match_captures_wide",
    "rebar_zig_collect_records_wide",
})
ALLOWED_SYSTEM_NATIVE_LIBRARIES = frozenset({
    "ld-linux-x86-64.so.2", "libc.so.6", "libdl.so.2",
    "libgcc_s.so.1", "libm.so.6", "libpthread.so.0",
})
ALLOWED_C_HEADERS = frozenset({
    "Python.h", "stddef.h", "stdint.h", "stdlib.h", "string.h",
})
ALLOWED_ZIG_UNICODE_EXTERNS = frozenset({
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDecimalDigit",
    "_PyUnicode_IsDigit", "_PyUnicode_IsNumeric",
    "_PyUnicode_IsWhitespace", "_PyUnicode_ToLowercase",
    "_PyUnicode_ToUppercase",
})
FAIL_CLOSED_AUDIT_HISTORY = (
    {
        "attempt": "initial_live_audit",
        "result": "FAIL",
        "exit_code": 1,
        "manifest_passed": True,
        "rust_native_elf_passed": True,
        "verified_core_family_count": 2,
        "rust_findings": [
            "missing_owned_rust_component: owned parser",
            "missing_owned_rust_component: owned executor",
        ],
        "root_cause": "the native lexical scanner initially treated Rust lifetime apostrophes as character literals",
        "resolution": "correctly tokenize Rust lifetimes and retain both owned-component requirements",
        "regression_self_test": "preserve_rust_lifetimes_and_owned_pipeline",
        "findings_suppressed": 0,
    },
    {
        "attempt": "initial_five_elf_live_audit",
        "result": "FAIL",
        "exit_code": 137,
        "verified_before_interruption": "all five authorized native ELF files were read and parsed; bounded AST and mapping stages were isolated",
        "root_cause": "running all 73 malicious controls and the complete production-source audit in the same process caused cumulative SIGKILL; independent source, five-ELF, and actual-mapping gates all passed",
        "resolution": "execute and strictly validate every pinned malicious control in a fresh isolated subprocess; retain all fail-closed source, ELF, maps, hash, and worker-output bounds",
        "findings_suppressed": 0,
    },
)


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def finding(path: str, code: str, detail: str, line: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"file": path, "code": code, "detail": detail}
    if line is not None:
        result["line"] = line
    return result


def constant_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = constant_string(node.left), constant_string(node.right)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for item in node.values:
            if isinstance(item, ast.FormattedValue):
                if not isinstance(item.value, ast.Constant):
                    return None
                parts.append(str(item.value.value))
            else:
                value = constant_string(item)
                if value is None:
                    return None
                parts.append(value)
        return "".join(parts)
    if isinstance(node, ast.Call):
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "chr"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, int)
        ):
            try:
                return chr(node.args[0].value)
            except (OverflowError, ValueError):
                return None
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "join"
            and len(node.args) == 1
            and isinstance(node.args[0], (ast.Tuple, ast.List))
        ):
            separator = constant_string(node.func.value)
            values = [constant_string(item) for item in node.args[0].elts]
            if separator is not None and all(value is not None for value in values):
                return separator.join(value for value in values if value is not None)
    return None


class AuditLimitError(ValueError):
    """A bounded audit input exceeds an explicitly enforced resource cap."""


class PythonSourceAudit(ast.NodeVisitor):
    def __init__(self, family: str, path: str) -> None:
        self.family = family
        self.path = path
        self.issues: list[dict[str, Any]] = []
        self.imports: set[str] = set()
        self.aliases: dict[str, str] = {}
        self.native_loads: list[dict[str, Any]] = []
        self.visited_nodes = 0

    def visit(self, node: ast.AST) -> Any:
        self.visited_nodes += 1
        if self.visited_nodes > MAX_PYTHON_AST_NODES:
            raise AuditLimitError(f"AST exceeds {MAX_PYTHON_AST_NODES} nodes")
        return super().visit(node)

    def add(self, node: ast.AST, code: str, detail: str) -> None:
        self.issues.append(finding(self.path, code, detail, getattr(node, "lineno", None)))

    def expression_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return self.aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            parent = self.expression_name(node.value)
            return f"{parent}.{node.attr}" if parent else None
        if isinstance(node, ast.Call):
            call = self.expression_name(node.func)
            if call == "getattr" and len(node.args) >= 2:
                base = self.expression_name(node.args[0])
                attribute = constant_string(node.args[1])
                return f"{base}.{attribute}" if base and attribute else None
        if isinstance(node, ast.Subscript):
            base = self.expression_name(node.value)
            attribute = constant_string(node.slice)
            return f"{base}.{attribute}" if base and attribute else None
        return None

    def inspect_import(self, node: ast.AST, module: str) -> None:
        self.imports.add(module)
        root = module.partition(".")[0]
        if root in FORBIDDEN_ENGINE_ROOTS:
            self.add(node, "forbidden_regex_import", module)
        elif root in FORBIDDEN_IMPORT_ROOTS:
            self.add(node, "forbidden_indirection_import", module)
        elif root == "ctypes" and self.family != "zig":
            self.add(node, "unowned_native_loader", module)
        elif root == "candidates":
            expected = OWNED_BRIDGES[self.family]
            allowed = f"candidates.{expected}" if expected else None
            if module != allowed:
                self.add(node, "cross_candidate_delegation", module)

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            self.inspect_import(node, item.name)
            alias = item.asname or item.name.partition(".")[0]
            self.aliases[alias] = item.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if node.level:
            self.add(node, "relative_candidate_import", "relative imports are not independently auditable")
        if module == "candidates":
            for item in node.names:
                target = f"candidates.{item.name}"
                self.inspect_import(node, target)
                self.aliases[item.asname or item.name] = target
        else:
            self.inspect_import(node, module)
            for item in node.names:
                self.aliases[item.asname or item.name] = f"{module}.{item.name}"
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        name = self.expression_name(node.value)
        if name:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.aliases[target.id] = name
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        name = self.expression_name(node)
        if name == "os.environ" or name == "sys.modules":
            self.add(node, "environment_or_module_registry", name)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        base = self.expression_name(node.value)
        key = constant_string(node.slice)
        if base in {"builtins", "__builtins__"} and key in {"__import__", "eval", "exec", "open"}:
            self.add(node, "indirect_builtin_execution", f"{base}[{key!r}]")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and BENCHMARK_MARKER.search(node.value):
            self.add(node, "benchmark_or_holdout_reference", node.value)

    def visit_Call(self, node: ast.Call) -> None:
        name = self.expression_name(node.func)
        if name in {
            "__import__", "builtins.__import__", "__builtins__.__import__",
            "importlib.import_module", "importlib.__import__",
        }:
            target = constant_string(node.args[0]) if node.args else None
            self.add(node, "dynamic_import", target if target is not None else "nonconstant target")
        elif name in {"eval", "exec", "builtins.eval", "builtins.exec", "open", "builtins.open"}:
            self.add(node, "dynamic_code_or_file_access", name)
        elif name and (
            name.startswith("subprocess.")
            or name.startswith("os.exec")
            or name.startswith("os.spawn")
            or name in {"os.system", "os.popen", "os.getenv", "os.putenv"}
        ):
            self.add(node, "external_process_or_configuration", name)
        elif name in {"ctypes.CDLL", "ctypes.PyDLL", "ctypes.WinDLL", "ctypes.OleDLL"}:
            self.check_native_load(node, name)
        elif name == "getattr" and len(node.args) >= 2:
            target = self.expression_name(node.args[0])
            attribute = constant_string(node.args[1])
            if attribute in {"__import__", "import_module", "eval", "exec", "CDLL", "PyDLL", "dlopen"}:
                self.add(node, "indirect_dynamic_loader", f"{target or '?'}:{attribute}")
            elif target and target.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS:
                self.add(node, "indirect_regex_delegation", f"{target}:{attribute or '?'}")
        elif name == "candidates._vm_native.configure":
            actual = [self.expression_name(item) for item in node.args]
            if self.family != "vm" or actual != ["_template", "_template_parts"]:
                self.add(node, "unowned_native_configuration", repr(actual))
        self.generic_visit(node)

    def check_native_load(self, node: ast.Call, name: str) -> None:
        if self.family != "zig" or name != "ctypes.CDLL" or len(node.args) != 1:
            self.add(node, "unowned_native_loader", name)
            return
        argument = node.args[0]
        if not isinstance(argument, ast.Name) or argument.id != "path":
            self.add(node, "unproven_native_loader_path", ast.unparse(argument))
            return
        self.native_loads.append({"line": node.lineno, "loader": name, "expected_basename": "_zig_probe.so"})


def analyze_python(source: str, family: str, path: str) -> dict[str, Any]:
    if len(source.encode("utf-8")) > MAX_PYTHON_SOURCE_BYTES:
        return {
            "passed": False,
            "imports": [],
            "issues": [finding(path, "python_source_size_limit_exceeded", f"source exceeds {MAX_PYTHON_SOURCE_BYTES} bytes")],
            "native_loads": [],
        }
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as error:
        return {
            "passed": False,
            "imports": [],
            "issues": [finding(path, "python_syntax_error", str(error), error.lineno)],
            "native_loads": [],
        }
    audit = PythonSourceAudit(family, path)
    try:
        audit.visit(tree)
    except (AuditLimitError, RecursionError) as error:
        return {
            "passed": False,
            "imports": sorted(audit.imports),
            "issues": [finding(path, "python_ast_node_limit_exceeded", str(error))],
            "native_loads": audit.native_loads,
        }
    if family == "zig":
        approved_path = False
        initializer: ast.FunctionDef | None = None
        for item in tree.body:
            if isinstance(item, ast.ClassDef) and item.name == "_Native":
                initializer = next(
                    (method for method in item.body if isinstance(method, ast.FunctionDef) and method.name == "__init__"),
                    None,
                )
                break
        store_count = 0
        owned_load_lines: set[int] = set()
        if initializer is not None:
            for node in ast.walk(initializer):
                if isinstance(node, ast.Name) and node.id == "path" and isinstance(node.ctx, ast.Store):
                    store_count += 1
                if isinstance(node, ast.Call) and audit.expression_name(node.func) == "ctypes.CDLL":
                    owned_load_lines.add(node.lineno)
                if not isinstance(node, ast.Assign):
                    continue
                if not any(isinstance(item, ast.Name) and item.id == "path" for item in node.targets):
                    continue
                value = node.value
                if (
                    isinstance(value, ast.Call)
                    and audit.expression_name(value.func) == "os.path.join"
                    and len(value.args) == 2
                    and constant_string(value.args[1]) == "_zig_probe.so"
                    and isinstance(value.args[0], ast.Call)
                    and audit.expression_name(value.args[0].func) == "os.path.dirname"
                    and len(value.args[0].args) == 1
                    and isinstance(value.args[0].args[0], ast.Name)
                    and value.args[0].args[0].id == "__file__"
                ):
                    approved_path = True
        recorded_lines = {item["line"] for item in audit.native_loads}
        if (
            not approved_path
            or store_count != 1
            or len(audit.native_loads) != 1
            or owned_load_lines != recorded_lines
        ):
            audit.issues.append(finding(
                path, "unproven_zig_native_path",
                "_Native.__init__ must assign the owned _zig_probe.so path exactly once and use it for its only ctypes.CDLL call",
            ))
    return {
        "passed": not audit.issues,
        "imports": sorted(audit.imports),
        "issues": audit.issues,
        "native_loads": audit.native_loads,
        "tree": tree,
    }


def strip_native(source: str, *, preserve_strings: bool = False) -> str:
    """Remove comments and, by default, literals while retaining line numbers."""
    output: list[str] = []
    at = 0
    state = "code"
    quote = ""
    while at < len(source):
        char = source[at]
        pair = source[at:at + 2]
        if state == "code":
            if pair == "//":
                output.extend("  ")
                at += 2
                state = "line"
                continue
            if pair == "/*":
                output.extend("  ")
                at += 2
                state = "block"
                continue
            is_character_literal = (
                char == "'"
                and at + 1 < len(source)
                and (
                    source[at + 1] == "\\"
                    or (at + 2 < len(source) and source[at + 2] == "'")
                )
            )
            if char == "\"" or is_character_literal:
                quote = char
                state = "string"
                output.append(char if preserve_strings else " ")
            else:
                output.append(char)
        elif state == "line":
            output.append("\n" if char == "\n" else " ")
            if char == "\n":
                state = "code"
        elif state == "block":
            if pair == "*/":
                output.extend("  ")
                at += 2
                state = "code"
                continue
            output.append("\n" if char == "\n" else " ")
        else:
            if char == "\\" and at + 1 < len(source):
                following = source[at + 1]
                if preserve_strings:
                    output.extend((char, following))
                else:
                    output.extend((" ", "\n" if following == "\n" else " "))
                at += 2
                continue
            output.append(char if preserve_strings or char == "\n" else " ")
            if char == quote:
                state = "code"
        at += 1
    return "".join(output)


def analyze_native(source: str, path: str, family: str) -> dict[str, Any]:
    if len(source.encode("utf-8")) > MAX_NATIVE_SOURCE_BYTES:
        return {
            "passed": False,
            "issues": [finding(path, "native_source_size_limit_exceeded", f"source exceeds {MAX_NATIVE_SOURCE_BYTES} bytes")],
            "allowed_native_python_imports": [],
            "family": family,
        }
    issues: list[dict[str, Any]] = []
    code = strip_native(source)
    with_strings = strip_native(source, preserve_strings=True)
    for rule, expression in NATIVE_RULES:
        for match in expression.finditer(code):
            issues.append(finding(path, rule, match.group(0), code.count("\n", 0, match.start()) + 1))
    if path.endswith(".c"):
        for match in re.finditer(
            r'(?m)^[ \t]*#[ \t]*include[ \t]*([<"])([^>"\n]+)[>"]',
            with_strings,
        ):
            opener, header = match.group(1), match.group(2)
            if opener != "<" or header not in ALLOWED_C_HEADERS:
                issues.append(finding(
                    path, "unapproved_native_header", header,
                    with_strings.count("\n", 0, match.start()) + 1,
                ))
        for match in re.finditer(
            r"(?m)^[ \t]*extern[ \t]+[^;\n{]*?\b([A-Za-z_][A-Za-z_0-9]*)[ \t]*\(",
            code,
        ):
            target = match.group(1)
            prefix = "rebar_zig_" if family == "zig" else "rebar_" if family == "rust" else None
            if prefix is None or not target.startswith(prefix):
                issues.append(finding(
                    path, "unowned_native_extern", target,
                    code.count("\n", 0, match.start()) + 1,
                ))
    allowed_python_imports = {"functools", "inspect"} if path == "candidates/rust/py_bridge.c" else set()
    native_python_imports: list[str] = []
    call_pattern = re.compile(r"\bPyImport_(?:ImportModule(?:NoBlock)?|Import)\s*\(")
    for match in call_pattern.finditer(with_strings):
        remainder = with_strings[match.end():]
        target_match = re.match(r'\s*"([^"\\]*(?:\\.[^"\\]*)*)"', remainder)
        target = target_match.group(1) if target_match else None
        if target is None or target not in allowed_python_imports:
            issues.append(finding(
                path, "native_dynamic_python_import", target or "nonliteral target",
                with_strings.count("\n", 0, match.start()) + 1,
            ))
        else:
            native_python_imports.append(target)
    if path.endswith(".zig"):
        imports = re.findall(r'@import\s*\(\s*"([^"\\]+)"\s*\)', with_strings)
        for target in imports:
            if target != "std":
                issues.append(finding(path, "external_zig_package", target))
        for match in re.finditer(
            r"(?m)^[ \t]*extern[ \t]+fn[ \t]+([A-Za-z_][A-Za-z_0-9]*)",
            code,
        ):
            target = match.group(1)
            if target not in ALLOWED_ZIG_UNICODE_EXTERNS:
                issues.append(finding(
                    path, "unowned_zig_extern", target,
                    code.count("\n", 0, match.start()) + 1,
                ))
    if path.endswith(".rs"):
        allowed_roots = {"std", "core", "alloc", "crate", "self", "super", "stack", "newline", "search", "unicode_tables"}
        for match in re.finditer(r"(?m)^\s*(?:pub\s+)?use\s+([A-Za-z_][A-Za-z_0-9]*)", code):
            target = match.group(1)
            if target not in allowed_roots:
                issues.append(finding(path, "external_rust_use", target, code.count("\n", 0, match.start()) + 1))
        for match in re.finditer(r"\bextern\s+crate\s+([A-Za-z_][A-Za-z_0-9]*)", code):
            target = match.group(1)
            if target not in {"std", "core", "alloc"}:
                issues.append(finding(path, "external_rust_crate", target, code.count("\n", 0, match.start()) + 1))
        for block in re.finditer(r'\b(?:unsafe\s+)?extern\s+"C"\s*\{([^}]*)\}', with_strings, re.DOTALL):
            for declaration in re.finditer(r"\bfn\s+([A-Za-z_][A-Za-z_0-9]*)\s*\(", block.group(1)):
                target = declaration.group(1)
                if target not in {"memchr", "Py_GetRecursionLimit"}:
                    offset = block.start(1) + declaration.start()
                    issues.append(finding(
                        path, "unowned_rust_extern", target,
                        with_strings.count("\n", 0, offset) + 1,
                    ))
    return {
        "passed": not issues,
        "issues": issues,
        "allowed_native_python_imports": sorted(native_python_imports),
        "family": family,
    }


def function_names(tree: ast.Module) -> set[str]:
    return {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def class_names(tree: ast.Module) -> set[str]:
    return {node.name for node in tree.body if isinstance(node, ast.ClassDef)}


def function_references(tree: ast.Module, name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}
    return set()


def verify_pipeline(family: str, tree: ast.Module, native: dict[str, str]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    path = relative(PYTHON_SOURCES[family])
    refs = function_references(tree, "compile")
    if "compile" not in function_names(tree):
        issues.append(finding(path, "missing_public_compiler", "module must define its own compile function"))
    evidence: dict[str, Any]
    if family == "ast":
        required = {"_Parser", "_Engine", "Pattern"}
        missing = sorted(required - class_names(tree))
        if missing:
            issues.append(finding(path, "missing_owned_ast_pipeline", ", ".join(missing)))
        if not {"_Parser", "Pattern"}.issubset(refs):
            issues.append(finding(path, "unwired_ast_compiler", "compile must construct its own parser and Pattern"))
        evidence = {"parser": "_Parser", "compiler": "owned AST construction", "executor": "_Engine.run"}
    elif family == "vm":
        required = {"_BytecodeParser", "_BytecodeCompiler", "Pattern"}
        missing = sorted(required - class_names(tree))
        if missing:
            issues.append(finding(path, "missing_owned_vm_pipeline", ", ".join(missing)))
        if not {"_BytecodeParser", "_BytecodeCompiler", "Pattern"}.issubset(refs):
            issues.append(finding(path, "unwired_vm_compiler", "compile must construct its own parser, compiler and Pattern"))
        code = strip_native(native["candidates/_vm_native.c"])
        required_markers = {
            "owned opcodes": r"\bOP_(?:CHAR|SPLIT|JUMP|MATCH)\b",
            "owned executor": r"\bexecute\s*\(",
            "owned native builder": r"\bnative_build\s*\(",
            "owned module initializer": r"\bPyInit__vm_native\s*\(",
        }
        for label, expression in required_markers.items():
            if not re.search(expression, code):
                issues.append(finding("candidates/_vm_native.c", "missing_owned_vm_component", label))
        evidence = {"parser": "_BytecodeParser", "compiler": "_BytecodeCompiler", "executor": "candidates/_vm_native.c:execute"}
    elif family == "rust":
        if "Pattern" not in class_names(tree) or "_NATIVE" not in refs:
            issues.append(finding(path, "unwired_rust_bridge", "compile must use the owned _NATIVE bridge and Pattern"))
        code = strip_native(native["candidates/rust/src/lib.rs"])
        required_markers = {
            "owned parser": r"\bstruct\s+Parser\b",
            "owned compiler": r"\bstruct\s+Compiler\b",
            "owned program": r"\bstruct\s+Program\b",
            "owned instruction set": r"\benum\s+Op\b",
            "owned executor": r"\bfn\s+run_program\s*\(",
            "owned compile boundary": r"\bfn\s+rebar_compile\s*\(",
        }
        for label, expression in required_markers.items():
            if not re.search(expression, code):
                issues.append(finding("candidates/rust/src/lib.rs", "missing_owned_rust_component", label))
        declared = set(re.findall(r"(?m)^\s*mod\s+([A-Za-z_][A-Za-z_0-9]*)\s*;", code))
        expected = {"newline", "search", "stack", "unicode_tables"}
        if declared != expected:
            issues.append(finding("candidates/rust/src/lib.rs", "unverified_rust_module_graph", f"expected {sorted(expected)!r}; found {sorted(declared)!r}"))
        evidence = {"parser": "rust::Parser", "compiler": "rust::Compiler", "executor": "rust::run_program"}
    else:
        if "Pattern" not in class_names(tree) or "_NATIVE" not in refs:
            issues.append(finding(path, "unwired_zig_bridge", "compile must use the owned _NATIVE bridge and Pattern"))
        code = strip_native(native["candidates/zig/mini_regex.zig"])
        required_markers = {
            "owned parser": r"\bconst\s+Parser\s*=\s*struct\b",
            "owned compiler": r"\bconst\s+Compiler\s*=\s*struct\b",
            "owned instruction set": r"\bconst\s+Op\s*=\s*enum\b",
            "owned bytecode executor": r"\bfn\s+runBytecode\s*\(",
            "owned capture executor": r"\bfn\s+runCapturedAt\s*\(",
            "owned compile boundary": r"\bfn\s+rebar_zig_compile\s*\(",
        }
        for label, expression in required_markers.items():
            if not re.search(expression, code):
                issues.append(finding("candidates/zig/mini_regex.zig", "missing_owned_zig_component", label))
        bridge = strip_native(native["candidates/zig/py_bridge.c"])
        if re.search(r"\brebar_zig_match_tree\s*\(", bridge):
            issues.append(finding("candidates/zig/py_bridge.c", "legacy_tree_executor_in_public_bridge", "public bridge must not dispatch to the diagnostic tree evaluator"))
        evidence = {"parser": "zig::Parser", "compiler": "zig::Compiler", "executor": "zig::runBytecode/runCapturedAt"}
    evidence["passed"] = not issues
    evidence["issues"] = issues
    return evidence


def analyze_manifests(contents: dict[str, str]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    parsed: dict[str, dict[str, Any]] = {}
    for key, content in contents.items():
        path = relative(MANIFESTS[key])
        try:
            parsed[key] = tomllib.loads(content)
        except tomllib.TOMLDecodeError as error:
            issues.append(finding(path, "invalid_toml", str(error)))
    project = parsed.get("project", {})
    project_dependencies = project.get("project", {}).get("dependencies", [])
    if not isinstance(project_dependencies, list) or project_dependencies:
        issues.append(finding("pyproject.toml", "project_has_dependencies", repr(project_dependencies)))
    optional = project.get("project", {}).get("optional-dependencies", {})
    if optional:
        issues.append(finding("pyproject.toml", "project_has_optional_dependencies", repr(optional)))
    dependency_groups = project.get("dependency-groups", {})
    if dependency_groups:
        issues.append(finding("pyproject.toml", "project_has_dependency_groups", repr(dependency_groups)))
    build_requires = project.get("build-system", {}).get("requires", [])
    if build_requires:
        issues.append(finding("pyproject.toml", "project_has_build_dependencies", repr(build_requires)))

    cargo = parsed.get("rust", {})
    def walk(value: Any, location: str) -> None:
        if not isinstance(value, dict):
            return
        for key, child in value.items():
            nested = f"{location}.{key}" if location else str(key)
            if key in {"dependencies", "build-dependencies", "dev-dependencies"}:
                if not isinstance(child, dict):
                    issues.append(finding("candidates/rust/Cargo.toml", "invalid_cargo_dependencies", nested))
                elif child:
                    issues.append(finding("candidates/rust/Cargo.toml", "external_cargo_dependencies", f"{nested}: {sorted(child)!r}"))
            elif key in {"patch", "replace"} and child:
                issues.append(finding("candidates/rust/Cargo.toml", "cargo_dependency_override", nested))
            if isinstance(child, dict):
                walk(child, nested)
    walk(cargo, "")
    package = cargo.get("package", {})
    if package.get("name") != "rebar-rust-continuation":
        issues.append(finding("candidates/rust/Cargo.toml", "unexpected_rust_package", repr(package.get("name"))))
    if package.get("build") not in {None, False}:
        issues.append(finding("candidates/rust/Cargo.toml", "explicit_rust_build_script", repr(package.get("build"))))

    lock = parsed.get("rust_lock", {})
    entries = lock.get("package")
    if not isinstance(entries, list) or len(entries) != 1:
        issues.append(finding("candidates/rust/Cargo.lock", "transitive_rust_dependencies", "lockfile must contain exactly the owned root package"))
        names = [item.get("name") for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []
    else:
        entry = entries[0]
        names = [entry.get("name")] if isinstance(entry, dict) else []
        if not isinstance(entry, dict) or entry.get("name") != "rebar-rust-continuation":
            issues.append(finding("candidates/rust/Cargo.lock", "unexpected_rust_lock_package", repr(names)))
        elif entry.get("dependencies"):
            issues.append(finding("candidates/rust/Cargo.lock", "transitive_rust_dependencies", repr(entry["dependencies"])))
        elif entry.get("source"):
            issues.append(finding("candidates/rust/Cargo.lock", "external_rust_package_source", repr(entry["source"])))
    return {
        "passed": not issues,
        "python_dependencies": project_dependencies,
        "rust_lock_packages": names,
        "rust_third_party_dependency_count": max(len(names) - 1, 0),
        "issues": issues,
    }


class ElfError(ValueError):
    """A native file could not be independently parsed as ELF."""


def read_c_string(table: bytes, offset: int) -> str:
    if offset < 0 or offset >= len(table):
        raise ElfError(f"invalid ELF string-table offset {offset}")
    end = table.find(b"\0", offset, min(len(table), offset + MAX_ELF_STRING_BYTES + 1))
    if end < 0:
        raise ElfError("unterminated ELF string-table entry")
    try:
        return table[offset:end].decode("utf-8")
    except UnicodeDecodeError as error:
        raise ElfError("non-UTF-8 ELF symbol") from error


def parse_elf(data: bytes) -> dict[str, Any]:
    if len(data) > MAX_ELF_BYTES:
        raise ElfError("ELF binary exceeds the 64 MiB fail-closed audit limit")
    if len(data) < 16 or data[:4] != b"\x7fELF":
        raise ElfError("not an ELF binary")
    elf_class, byte_order = data[4], data[5]
    if elf_class not in {1, 2} or byte_order not in {1, 2}:
        raise ElfError("unsupported ELF class or byte order")
    prefix = "<" if byte_order == 1 else ">"
    is_64 = elf_class == 2
    header_format = prefix + ("16sHHIQQQIHHHHHH" if is_64 else "16sHHIIIIIHHHHHH")
    if len(data) < struct.calcsize(header_format):
        raise ElfError("truncated ELF header")
    header = struct.unpack_from(header_format, data)
    section_offset = header[6]
    section_size = header[11]
    section_count = header[12]
    section_format = prefix + ("IIQQQQIIQQ" if is_64 else "IIIIIIIIII")
    minimum_section_size = struct.calcsize(section_format)
    if not section_count or section_size < minimum_section_size:
        raise ElfError("missing or invalid ELF section table")
    if section_count > MAX_ELF_SECTIONS:
        raise ElfError("ELF section count exceeds the fail-closed audit limit")
    if section_offset + section_size * section_count > len(data):
        raise ElfError("ELF section table exceeds file size")
    sections: list[tuple[Any, ...]] = []
    for index in range(section_count):
        section = struct.unpack_from(section_format, data, section_offset + index * section_size)
        offset, size = section[4], section[5]
        if section[1] != 8 and offset + size > len(data):
            raise ElfError(f"ELF section {index} exceeds file size")
        sections.append(section)

    needed: list[str] = []
    runpaths: list[str] = []
    undefined: set[str] = set()
    exported: set[str] = set()
    for section in sections:
        section_type, offset, size, link, entry_size = section[1], section[4], section[5], section[6], section[9]
        if section_type not in {6, 11}:
            continue
        if link >= len(sections):
            raise ElfError("ELF dynamic section has an invalid string-table link")
        string_section = sections[link]
        if string_section[5] > MAX_ELF_STRING_TABLE_BYTES:
            raise ElfError("ELF dynamic string table exceeds the fail-closed audit limit")
        table = data[string_section[4]:string_section[4] + string_section[5]]
        if section_type == 6:
            item_format = prefix + ("qQ" if is_64 else "iI")
            minimum = struct.calcsize(item_format)
            step = entry_size or minimum
            if step < minimum or size % step:
                raise ElfError("malformed ELF dynamic table")
            if size // step > MAX_ELF_DYNAMIC_ENTRIES:
                raise ElfError("ELF dynamic-entry count exceeds the fail-closed audit limit")
            for position in range(offset, offset + size, step):
                tag, value = struct.unpack_from(item_format, data, position)
                if tag == 0:
                    break
                if tag == 1:
                    needed.append(read_c_string(table, value))
                elif tag in {15, 29}:
                    runpaths.append(read_c_string(table, value))
        else:
            symbol_format = prefix + ("IBBHQQ" if is_64 else "IIIBBH")
            minimum = struct.calcsize(symbol_format)
            step = entry_size or minimum
            if step < minimum or size % step:
                raise ElfError("malformed ELF dynamic symbol table")
            if size // step > MAX_ELF_DYNAMIC_SYMBOLS:
                raise ElfError("ELF dynamic-symbol count exceeds the fail-closed audit limit")
            for position in range(offset, offset + size, step):
                entry = struct.unpack_from(symbol_format, data, position)
                name_offset = entry[0]
                section_index = entry[3] if is_64 else entry[5]
                if not name_offset:
                    continue
                name = read_c_string(table, name_offset).partition("@")[0]
                (undefined if section_index == 0 else exported).add(name)
    return {
        "class": 64 if is_64 else 32,
        "byte_order": "little" if byte_order == 1 else "big",
        "needed": sorted(set(needed)),
        "runpaths": sorted(set(runpaths)),
        "undefined": sorted(undefined),
        "exported": sorted(exported),
    }


def forbidden_native_name(name: str) -> bool:
    lower = name.casefold().replace("-", "_")
    return (
        lower in {"regcomp", "regexec", "regerror", "regfree", "pyinit__sre"}
        or lower.startswith(("pcre_", "pcre2_", "onig_", "oniguruma_", "hyperscan_", "hs_compile", "hs_scan", "re2_", "sre_"))
        or lower.startswith(("libpcre", "libonig", "libhyperscan", "libre2", "libregex", "libhs."))
        or lower.startswith(("pyinit__regex", "pyinit__re2", "pyinit__pcre", "pyinit__onig"))
    )


def cross_candidate_native_name(family: str, name: str) -> bool:
    base = name.rsplit("/", 1)[-1]
    if base.startswith("rebar_zig_"):
        return family != "zig"
    if base.startswith("rebar_"):
        return family != "rust"
    if base == "_rust_engine.so" or base == "PyInit__rust_bridge":
        return family != "rust"
    if base == "_zig_probe.so" or base == "PyInit__zig_bridge":
        return family != "zig"
    if base == "PyInit__vm_native" or base == "_vm_native.cpython-314-x86_64-linux-gnu.so":
        return family != "vm"
    return False


def elf_file_evidence(path: str, data: bytes, elf: dict[str, Any], bad: list[str], cross: list[str]) -> dict[str, Any]:
    python_undefined = sorted(
        name for name in elf["undefined"]
        if name.startswith(("Py", "_Py"))
    )
    return {
        "file": path,
        "sha256": hashlib.sha256(data).hexdigest(),
        "elf_class": elf["class"],
        "needed": elf["needed"],
        "runpaths": elf["runpaths"],
        "undefined_symbol_count": len(elf["undefined"]),
        "python_api_undefined_count": len(python_undefined),
        "python_api_undefined_symbols": python_undefined,
        "owned_exports": sorted(
            symbol for symbol in elf["exported"]
            if symbol.startswith("rebar_") or symbol.startswith("PyInit_")
        ),
        "owned_undefined": sorted(
            symbol for symbol in elf["undefined"] if symbol.startswith("rebar_")
        ),
        "forbidden_regex_symbols": bad,
        "cross_candidate_symbols": cross,
    }


def analyze_rust_binaries(binary_data: dict[str, bytes]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    result: dict[str, Any] = {"passed": False, "files": {}, "issues": issues}
    parsed: dict[str, dict[str, Any]] = {}
    for name, data in binary_data.items():
        path = relative(RUST_BINARIES[name])
        try:
            elf = parse_elf(data)
        except (ElfError, struct.error, OverflowError) as error:
            issues.append(finding(path, "invalid_or_unverifiable_elf", str(error)))
            continue
        parsed[name] = elf
        all_names = elf["needed"] + elf["undefined"] + elf["exported"]
        bad = sorted({symbol for symbol in all_names if forbidden_native_name(symbol)})
        if bad:
            issues.append(finding(path, "external_regex_native_dependency", ", ".join(bad)))
        cross = sorted({symbol for symbol in all_names if cross_candidate_native_name("rust", symbol)})
        if cross:
            issues.append(finding(path, "cross_candidate_native_dependency", ", ".join(cross)))
        approved_needed = set(ALLOWED_SYSTEM_NATIVE_LIBRARIES)
        if name == "bridge":
            approved_needed.add("_rust_engine.so")
        unapproved = sorted(set(elf["needed"]) - approved_needed)
        if unapproved:
            issues.append(finding(path, "unapproved_native_dependency", ", ".join(unapproved)))
        for entry in elf["runpaths"]:
            if entry not in {"$ORIGIN", "${ORIGIN}"}:
                issues.append(finding(path, "untrusted_native_runpath", entry))
        result["files"][name] = elf_file_evidence(path, data, elf, bad, cross)
    if "engine" in parsed:
        missing = sorted(RUST_REQUIRED_EXPORTS - set(parsed["engine"]["exported"]))
        if missing:
            issues.append(finding(relative(RUST_BINARIES["engine"]), "missing_owned_rust_exports", ", ".join(missing)))
    if "bridge" in parsed:
        bridge = parsed["bridge"]
        if "PyInit__rust_bridge" not in bridge["exported"]:
            issues.append(finding(relative(RUST_BINARIES["bridge"]), "missing_rust_bridge_initializer", "PyInit__rust_bridge"))
        if "_rust_engine.so" not in bridge["needed"]:
            issues.append(finding(relative(RUST_BINARIES["bridge"]), "bridge_not_linked_to_owned_engine", repr(bridge["needed"])))
        if "rebar_compile" not in bridge["undefined"]:
            issues.append(finding(relative(RUST_BINARIES["bridge"]), "bridge_bypasses_owned_compiler", "rebar_compile is not an imported engine symbol"))
        execution = {"rebar_match", "rebar_match_ascii", "rebar_match_wide"}
        if not execution.intersection(bridge["undefined"]):
            issues.append(finding(relative(RUST_BINARIES["bridge"]), "bridge_bypasses_owned_executor", "no owned rebar_match symbol is imported"))
        if "engine" in parsed:
            missing = sorted(
                symbol for symbol in bridge["undefined"]
                if symbol.startswith("rebar_") and symbol not in parsed["engine"]["exported"]
            )
            if missing:
                issues.append(finding(relative(RUST_BINARIES["bridge"]), "unresolved_owned_engine_symbols", ", ".join(missing)))
    result["passed"] = not issues and set(parsed) == {"engine", "bridge"}
    return result


def analyze_vm_binaries(binary_data: dict[str, bytes]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    result: dict[str, Any] = {"passed": False, "files": {}, "issues": issues}
    expected = NATIVE_BINARIES["vm"]
    if set(binary_data) != {"native"}:
        for role in sorted({"native"} - set(binary_data)):
            issues.append(finding(relative(expected[role]), "required_native_binary_unreadable", "owned VM ELF binary is missing"))
        for role in sorted(set(binary_data) - {"native"}):
            issues.append(finding("candidates/_vm_native.cpython-314-x86_64-linux-gnu.so", "unexpected_native_binary_role", role))
    data = binary_data.get("native")
    if data is None:
        return result
    path = relative(expected["native"])
    try:
        elf = parse_elf(data)
    except (ElfError, struct.error, OverflowError) as error:
        issues.append(finding(path, "invalid_or_unverifiable_elf", str(error)))
        return result
    all_names = elf["needed"] + elf["undefined"] + elf["exported"]
    bad = sorted({name for name in all_names if forbidden_native_name(name)})
    if bad:
        issues.append(finding(path, "external_regex_native_dependency", ", ".join(bad)))
    cross = sorted({name for name in all_names if cross_candidate_native_name("vm", name)})
    if cross:
        issues.append(finding(path, "cross_candidate_native_dependency", ", ".join(cross)))
    unapproved = sorted(set(elf["needed"]) - set(ALLOWED_SYSTEM_NATIVE_LIBRARIES))
    if unapproved:
        issues.append(finding(path, "unapproved_native_dependency", ", ".join(unapproved)))
    for entry in elf["runpaths"]:
        if entry not in {"$ORIGIN", "${ORIGIN}"}:
            issues.append(finding(path, "untrusted_native_runpath", entry))
    if "PyInit__vm_native" not in elf["exported"]:
        issues.append(finding(path, "missing_vm_native_initializer", "PyInit__vm_native"))
    result["files"]["native"] = elf_file_evidence(path, data, elf, bad, cross)
    result["passed"] = not issues and set(binary_data) == {"native"}
    return result


def analyze_zig_binaries(binary_data: dict[str, bytes]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    result: dict[str, Any] = {"passed": False, "files": {}, "issues": issues}
    expected = NATIVE_BINARIES["zig"]
    parsed: dict[str, dict[str, Any]] = {}
    for role in sorted({"engine", "bridge"} - set(binary_data)):
        issues.append(finding(relative(expected[role]), "required_native_binary_unreadable", "owned Zig ELF binary is missing"))
    for role in sorted(set(binary_data) - {"engine", "bridge"}):
        issues.append(finding("candidates/_zig_probe.so", "unexpected_native_binary_role", role))
    for role in ("engine", "bridge"):
        data = binary_data.get(role)
        if data is None:
            continue
        path = relative(expected[role])
        try:
            elf = parse_elf(data)
        except (ElfError, struct.error, OverflowError) as error:
            issues.append(finding(path, "invalid_or_unverifiable_elf", str(error)))
            continue
        parsed[role] = elf
        all_names = elf["needed"] + elf["undefined"] + elf["exported"]
        bad = sorted({name for name in all_names if forbidden_native_name(name)})
        if bad:
            issues.append(finding(path, "external_regex_native_dependency", ", ".join(bad)))
        cross = sorted({name for name in all_names if cross_candidate_native_name("zig", name)})
        if cross:
            issues.append(finding(path, "cross_candidate_native_dependency", ", ".join(cross)))
        approved_needed = set(ALLOWED_SYSTEM_NATIVE_LIBRARIES)
        if role == "bridge":
            approved_needed.add("_zig_probe.so")
        unapproved = sorted(set(elf["needed"]) - approved_needed)
        if unapproved:
            issues.append(finding(path, "unapproved_native_dependency", ", ".join(unapproved)))
        for entry in elf["runpaths"]:
            if entry not in {"$ORIGIN", "${ORIGIN}"}:
                issues.append(finding(path, "untrusted_native_runpath", entry))
        result["files"][role] = elf_file_evidence(path, data, elf, bad, cross)
    if "engine" in parsed:
        missing = sorted(ZIG_REQUIRED_EXPORTS - set(parsed["engine"]["exported"]))
        if missing:
            issues.append(finding(relative(expected["engine"]), "missing_owned_zig_exports", ", ".join(missing)))
    if "bridge" in parsed:
        bridge = parsed["bridge"]
        bridge_path = relative(expected["bridge"])
        if "PyInit__zig_bridge" not in bridge["exported"]:
            issues.append(finding(bridge_path, "missing_zig_bridge_initializer", "PyInit__zig_bridge"))
        if "_zig_probe.so" not in bridge["needed"]:
            issues.append(finding(bridge_path, "zig_bridge_not_linked_to_owned_engine", repr(bridge["needed"])))
        if "rebar_zig_compile" not in bridge["undefined"]:
            issues.append(finding(bridge_path, "zig_bridge_bypasses_owned_compiler", "rebar_zig_compile is not an imported engine symbol"))
        executions = {"rebar_zig_match_wide", "rebar_zig_match_captures_wide"}
        if not executions.intersection(bridge["undefined"]):
            issues.append(finding(bridge_path, "zig_bridge_bypasses_owned_executor", "no owned Zig match symbol is imported"))
        if "engine" in parsed:
            missing = sorted(
                symbol for symbol in bridge["undefined"]
                if symbol.startswith("rebar_zig_") and symbol not in parsed["engine"]["exported"]
            )
            if missing:
                issues.append(finding(bridge_path, "unresolved_owned_zig_engine_symbols", ", ".join(missing)))
    result["passed"] = not issues and set(parsed) == {"engine", "bridge"}
    return result


def analyze_all_native_binaries(binary_data: dict[str, dict[str, bytes]]) -> dict[str, Any]:
    families: dict[str, dict[str, Any]] = {}
    for family, analyzer in (
        ("vm", analyze_vm_binaries),
        ("rust", analyze_rust_binaries),
        ("zig", analyze_zig_binaries),
    ):
        families[family] = analyzer(binary_data.get(family, {}))
    issues = [issue for family in families.values() for issue in family["issues"]]
    return {
        "passed": all(item["passed"] for item in families.values()),
        "audited_binary_count": sum(len(item["files"]) for item in families.values()),
        "expected_binary_count": 5,
        "families": families,
        "issues": issues,
    }


def classify_mapping_snapshot(maps_text: str, family: str) -> dict[str, Any]:
    expected = {str(path): role for role, path in NATIVE_BINARIES.get(family, {}).items()}
    all_owned = {
        str(path): (owner, role)
        for owner, paths in NATIVE_BINARIES.items()
        for role, path in paths.items()
    }
    candidate_root = str(ROOT / "candidates") + "/"
    observed: dict[str, int] = {}
    issues: list[dict[str, Any]] = []
    for line in maps_text.splitlines():
        fields = line.split(None, 5)
        if len(fields) != 6:
            continue
        raw = fields[5].strip()
        if not raw.startswith("/"):
            continue
        deleted = raw.endswith(" (deleted)")
        path = raw[:-10] if deleted else raw
        path = str(Path(path))
        basename = path.rsplit("/", 1)[-1]
        if forbidden_native_name(basename):
            issues.append(finding(path, "forbidden_mapped_regex_engine", basename))
        if path in all_owned:
            owner, _role = all_owned[path]
            if owner != family:
                issues.append(finding(path, "cross_candidate_native_mapping", f"{owner} binary mapped in {family} worker"))
            elif deleted:
                issues.append(finding(path, "deleted_owned_native_mapping", "mapped owned binary has been deleted"))
            else:
                observed[path] = observed.get(path, 0) + 1
        elif path.startswith(candidate_root) and (basename.endswith(".so") or ".so." in basename):
            issues.append(finding(path, "unapproved_candidate_native_mapping", "candidate native mapping is outside the five exact authorized binaries"))
    missing = sorted(set(expected) - set(observed))
    for path in missing:
        issues.append(finding(path, "required_owned_native_mapping_missing", "owned binary was not mapped after the candidate smoke checks"))
    return {
        "passed": not issues,
        "observed_mapping_counts": {path: observed[path] for path in sorted(observed)},
        "expected_owned_paths": sorted(expected),
        "issues": issues,
    }


ISOLATED_PROBE = r'''
import builtins
import ctypes
import enum
import functools
import hashlib
import importlib
import json
import operator
import os
import sys
import types
import unicodedata
import warnings

MAX_MAP_BYTES = 4 * 1024 * 1024
MAX_MAP_ROWS = 16384
MAX_MAP_LINE_BYTES = 16384
HASH_CHUNK_BYTES = 1024 * 1024

root, family, bridge, expected_hashes_text = sys.argv[1:5]
module_name = "candidates." + family + "_candidate"
owned = {module_name}
if bridge:
    owned.add("candidates." + bridge)
blocked_roots = {
    "re", "_sre", "sre", "sre_compile", "sre_parse", "sre_constants",
    "regex", "regex_lite", "regex_automata", "regex_syntax", "fancy_regex",
    "re2", "pcre", "pcre2", "onig", "oniguruma", "onigurumacffi",
    "_onigurumacffi", "hyperscan", "aho_corasick", "rebar",
}
blocked_events = []
native_loads = []
expected_zig = os.path.normpath(os.path.join(root, "candidates", "_zig_probe.so"))
native_paths = {
    "vm": {
        "native": os.path.normpath(os.path.join(root, "candidates", "_vm_native.cpython-314-x86_64-linux-gnu.so")),
    },
    "rust": {
        "engine": os.path.normpath(os.path.join(root, "candidates", "_rust_engine.so")),
        "bridge": os.path.normpath(os.path.join(root, "candidates", "_rust_bridge.cpython-314-x86_64-linux-gnu.so")),
    },
    "zig": {
        "engine": expected_zig,
        "bridge": os.path.normpath(os.path.join(root, "candidates", "_zig_bridge.cpython-314-x86_64-linux-gnu.so")),
    },
}
all_native_paths = {
    path: (owner, role)
    for owner, roles in native_paths.items()
    for role, path in roles.items()
}
expected_hashes = json.loads(expected_hashes_text)

def prohibited(name):
    name = str(name)
    base = name.partition(".")[0]
    if base in blocked_roots:
        return True
    if name.startswith("candidates.") and name not in owned:
        return True
    return False

for key in tuple(sys.modules):
    if key.partition(".")[0] in blocked_roots:
        sys.modules.pop(key, None)

def deny(kind, target):
    blocked_events.append({"kind": kind, "target": str(target)})
    raise ImportError("from-scratch audit rejected " + kind + ": " + str(target))

def hook(event, args):
    if event == "import" and args and prohibited(args[0]):
        deny("audit_import", args[0])
    elif event == "ctypes.dlopen":
        target = args[0] if args else None
        if family != "zig" or target is None or os.path.normpath(os.fspath(target)) != expected_zig:
            deny("native_load", target)
        native_loads.append(os.path.normpath(os.fspath(target)))
    elif event == "ctypes.dlsym":
        symbol = args[1] if len(args) > 1 else ""
        library = args[0] if args else None
        library_path = getattr(library, "_name", None)
        if (
            family != "zig"
            or not str(symbol).startswith("rebar_zig_")
            or library_path is None
            or os.path.normpath(os.fspath(library_path)) != expected_zig
        ):
            deny("native_symbol", symbol)
    elif event == "subprocess.Popen" or event == "os.system" or event.startswith("os.exec") or event.startswith("os.spawn") or event in {"os.fork", "os.posix_spawn"}:
        deny("external_process", event)
    elif event == "open" and args:
        raw_target = args[0]
        target = str(raw_target).casefold()
        if "holdout" in target or "benchmark" in target or "frozen-performance" in target:
            deny("benchmark_or_holdout_access", args[0])
        if isinstance(raw_target, (str, bytes, os.PathLike)):
            normalized = os.path.normpath(os.fsdecode(raw_target))
            candidate_root = os.path.normpath(os.path.join(root, "candidates")) + os.sep
            basename = os.path.basename(normalized)
            if (
                normalized.startswith(candidate_root)
                and (basename.endswith(".so") or ".so." in basename)
                and normalized not in all_native_paths
            ):
                deny("unapproved_candidate_native_file", normalized)

sys.path.insert(0, root)
sys.addaudithook(hook)
original_import = builtins.__import__
original_import_module = importlib.import_module

def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if prohibited(name):
        deny("python_import", name)
    if name == "candidates":
        for item in fromlist or ():
            if isinstance(item, str) and item != "*" and prohibited("candidates." + item):
                deny("cross_candidate_import", "candidates." + item)
    return original_import(name, globals, locals, fromlist, level)

def guarded_import_module(name, package=None):
    if prohibited(name):
        deny("import_module", name)
    return original_import_module(name, package)

builtins.__import__ = guarded_import
importlib.import_module = guarded_import_module

def forbidden_mapped_name(value):
    lower = os.path.basename(value).casefold().replace("-", "_")
    return (
        lower in {"regcomp", "regexec", "regerror", "regfree", "pyinit__sre"}
        or lower.startswith(("pcre_", "pcre2_", "onig_", "oniguruma_", "hyperscan_", "hs_compile", "hs_scan", "re2_", "sre_"))
        or lower.startswith(("libpcre", "libonig", "libhyperscan", "libre2", "libregex", "libhs."))
        or lower.startswith(("pyinit__regex", "pyinit__re2", "pyinit__pcre", "pyinit__onig"))
    )

def verify_actual_native_mappings():
    expected_paths = native_paths.get(family, {})
    issues = []
    observed = {}
    if set(expected_hashes) != set(expected_paths):
        issues.append({
            "code": "unexpected_static_hash_roles",
            "detail": {"expected": sorted(expected_paths), "actual": sorted(expected_hashes)},
        })
    with open("/proc/self/maps", "r", encoding="utf-8") as stream:
        maps_data = stream.read(MAX_MAP_BYTES + 1)
    if len(maps_data) > MAX_MAP_BYTES:
        issues.append({"code": "proc_maps_size_limit_exceeded", "maximum_bytes": MAX_MAP_BYTES})
        maps_rows = ()
    else:
        maps_rows = maps_data.splitlines()
        if len(maps_rows) > MAX_MAP_ROWS:
            issues.append({"code": "proc_maps_row_limit_exceeded", "maximum_rows": MAX_MAP_ROWS})
            maps_rows = ()
    for line in maps_rows:
            if len(line) > MAX_MAP_LINE_BYTES:
                issues.append({"code": "proc_maps_line_limit_exceeded", "maximum_bytes": MAX_MAP_LINE_BYTES})
                continue
            fields = line.split(None, 5)
            if len(fields) != 6:
                continue
            raw = fields[5].strip()
            if not raw.startswith("/"):
                continue
            deleted = raw.endswith(" (deleted)")
            path = raw[:-10] if deleted else raw
            path = os.path.normpath(path)
            basename = os.path.basename(path)
            if forbidden_mapped_name(basename):
                issues.append({"code": "forbidden_mapped_regex_engine", "file": path})
            if path in all_native_paths:
                owner, role = all_native_paths[path]
                if owner != family:
                    issues.append({
                        "code": "cross_candidate_native_mapping",
                        "file": path,
                        "owner": owner,
                        "worker_family": family,
                    })
                elif deleted:
                    issues.append({"code": "deleted_owned_native_mapping", "file": path})
                else:
                    observed[path] = observed.get(path, 0) + 1
            elif path.startswith(os.path.normpath(os.path.join(root, "candidates")) + os.sep) and (basename.endswith(".so") or ".so." in basename):
                issues.append({"code": "unapproved_candidate_native_mapping", "file": path})
    evidence = []
    for role, path in sorted(expected_paths.items()):
        expected = expected_hashes.get(role)
        if not isinstance(expected, dict) or expected.get("file") != path:
            issues.append({"code": "static_native_path_mismatch", "role": role, "file": path})
            continue
        count = observed.get(path, 0)
        if not count:
            issues.append({"code": "required_owned_native_mapping_missing", "role": role, "file": path})
            continue
        digest = hashlib.sha256()
        with open(path, "rb") as stream:
            while True:
                block = stream.read(HASH_CHUNK_BYTES)
                if not block:
                    break
                digest.update(block)
        actual = digest.hexdigest()
        matches = actual == expected.get("sha256")
        if not matches:
            issues.append({
                "code": "mapped_binary_hash_mismatch",
                "role": role,
                "file": path,
                "expected_sha256": expected.get("sha256"),
                "actual_sha256": actual,
            })
        evidence.append({
            "role": role,
            "file": os.path.relpath(path, root),
            "mapping_count": count,
            "sha256": actual,
            "matches_static_elf": matches,
        })
    return {
        "passed": not issues,
        "source": "/proc/self/maps",
        "expected_owned_mapping_count": len(expected_paths),
        "observed_owned_mapping_count": len(evidence),
        "observed_owned_mappings": evidence,
        "issues": issues,
        "unrelated_system_libraries_ignored": True,
    }

try:
    candidate = importlib.import_module(module_name)
    matched = candidate.search("a", "a")
    if matched is None or matched.group(0) != "a":
        raise AssertionError("owned text search did not match")
    full = candidate.fullmatch(b"a", b"a")
    if full is None or full.group(0) != b"a":
        raise AssertionError("owned bytes fullmatch did not match")
    if candidate.sub("a", "b", "a") != "b":
        raise AssertionError("owned replacement did not match")
    mapping_provenance = verify_actual_native_mappings()
    attempted_by_candidate = list(blocked_events)
    loaded_forbidden = sorted(name for name in sys.modules if name.partition(".")[0] in blocked_roots)
    loaded_candidates = sorted(name for name in sys.modules if name.startswith("candidates."))
    unexpected_candidates = sorted(set(loaded_candidates) - owned)
    probes = {}
    for label, operation in (
        ("stdlib_re", lambda: builtins.__import__("re")),
        ("cpython_sre", lambda: importlib.import_module("_sre")),
        ("third_party_regex", lambda: importlib.import_module("regex")),
        ("other_candidate", lambda: importlib.import_module("candidates." + ("vm_candidate" if family != "vm" else "ast_candidate"))),
        ("foreign_native_loader", lambda: ctypes.CDLL(None)),
    ):
        before = len(blocked_events)
        try:
            operation()
        except ImportError:
            probes[label] = len(blocked_events) > before
        else:
            probes[label] = False
    result = {
        "passed": not attempted_by_candidate and not loaded_forbidden and not unexpected_candidates and all(probes.values()) and mapping_provenance["passed"] and (family != "zig" or native_loads == [expected_zig]),
        "module": module_name,
        "loaded_candidate_modules": loaded_candidates,
        "forbidden_candidate_import_attempts": attempted_by_candidate,
        "forbidden_loaded_modules": loaded_forbidden,
        "unexpected_candidate_modules": unexpected_candidates,
        "owned_native_loads": native_loads,
        "native_mapping_provenance": mapping_provenance,
        "prohibited_import_and_loader_probes": probes,
        "fixed_smoke_checks": 3,
    }
    print(json.dumps(result, sort_keys=True))
except BaseException as error:
    print(json.dumps({
        "passed": False,
        "module": module_name,
        "error_type": type(error).__name__,
        "error": str(error),
        "forbidden_candidate_import_attempts": blocked_events,
        "owned_native_loads": native_loads,
    }, sort_keys=True))
    sys.exit(1)
'''


def isolated_probe(family: str, static_binary_evidence: dict[str, Any]) -> dict[str, Any]:
    bridge = OWNED_BRIDGES[family] or ""
    expected = {
        role: {
            "file": str(NATIVE_BINARIES[family][role]),
            "sha256": evidence["sha256"],
        }
        for role, evidence in static_binary_evidence.items()
    }
    command = [
        sys.executable, "-I", "-B", "-c", ISOLATED_PROBE,
        str(ROOT), family, bridge, json.dumps(expected, sort_keys=True),
    ]
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    except (OSError, subprocess.SubprocessError) as error:
        return {"passed": False, "module": f"candidates.{family}_candidate", "error": str(error)}
    if len(process.stdout.encode("utf-8")) > MAX_WORKER_RESPONSE_BYTES:
        return {
            "passed": False,
            "module": f"candidates.{family}_candidate",
            "error": "isolated worker stdout exceeds the bounded audit response limit",
            "maximum_response_bytes": MAX_WORKER_RESPONSE_BYTES,
        }
    if len(process.stderr.encode("utf-8")) > MAX_WORKER_RESPONSE_BYTES:
        return {
            "passed": False,
            "module": f"candidates.{family}_candidate",
            "error": "isolated worker stderr exceeds the bounded audit response limit",
            "maximum_response_bytes": MAX_WORKER_RESPONSE_BYTES,
        }
    lines = process.stdout.splitlines()
    if not lines:
        return {
            "passed": False,
            "module": f"candidates.{family}_candidate",
            "error": "isolated probe produced no JSON result",
            "exit_code": process.returncode,
            "stderr": process.stderr[-2000:],
        }
    try:
        result = json.loads(lines[-1])
    except (TypeError, json.JSONDecodeError) as error:
        return {
            "passed": False,
            "module": f"candidates.{family}_candidate",
            "error": f"invalid isolated audit result: {error}",
            "exit_code": process.returncode,
            "stderr": process.stderr[-2000:],
        }
    if process.returncode:
        result["passed"] = False
        result["exit_code"] = process.returncode
        if process.stderr:
            result["stderr"] = process.stderr[-2000:]
    return result


def synthetic_elf(
    *,
    undefined: tuple[str, ...] = (),
    exported: tuple[str, ...] = (),
    needed: tuple[str, ...] = (),
    runpaths: tuple[str, ...] = (),
) -> bytes:
    """Construct a small ELF64 entirely in memory for parser self-tests."""
    names = b"\0.shstrtab\0.dynstr\0.dynsym\0.dynamic\0"
    strings = bytearray(b"\0")
    offsets: dict[str, int] = {}
    for value in (*undefined, *exported, *needed, *runpaths):
        if value not in offsets:
            offsets[value] = len(strings)
            strings.extend(value.encode("utf-8") + b"\0")
    dynsym = bytearray(struct.pack("<IBBHQQ", 0, 0, 0, 0, 0, 0))
    for value in undefined:
        dynsym.extend(struct.pack("<IBBHQQ", offsets[value], 0x12, 0, 0, 0, 0))
    for value in exported:
        dynsym.extend(struct.pack("<IBBHQQ", offsets[value], 0x12, 0, 1, 0, 0))
    dynamic = bytearray()
    for value in needed:
        dynamic.extend(struct.pack("<qQ", 1, offsets[value]))
    for value in runpaths:
        dynamic.extend(struct.pack("<qQ", 29, offsets[value]))
    dynamic.extend(struct.pack("<qQ", 0, 0))
    data = bytearray(b"\0" * 64)

    def append(payload: bytes | bytearray, alignment: int = 1) -> tuple[int, int]:
        padding = (-len(data)) % alignment
        if padding:
            data.extend(b"\0" * padding)
        start = len(data)
        data.extend(payload)
        return start, len(payload)

    shstr_offset, shstr_size = append(names)
    string_offset, string_size = append(strings)
    symbol_offset, symbol_size = append(dynsym, 8)
    dynamic_offset, dynamic_size = append(dynamic, 8)
    section_offset, _ = append(b"", 8)
    sections = [
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (names.index(b".shstrtab"), 3, 0, 0, shstr_offset, shstr_size, 0, 0, 1, 0),
        (names.index(b".dynstr"), 3, 0, 0, string_offset, string_size, 0, 0, 1, 0),
        (names.index(b".dynsym"), 11, 0, 0, symbol_offset, symbol_size, 2, 1, 8, 24),
        (names.index(b".dynamic"), 6, 0, 0, dynamic_offset, dynamic_size, 2, 0, 8, 16),
    ]
    for section in sections:
        data.extend(struct.pack("<IIQQQQIIQQ", *section))
    ident = b"\x7fELF" + bytes((2, 1, 1, 0)) + b"\0" * 8
    struct.pack_into("<16sHHIQQQIHHHHHH", data, 0, ident, 3, 62, 1, 0, 0, section_offset, 0, 64, 0, 0, 64, len(sections), 1)
    return bytes(data)


def self_test() -> dict[str, Any]:
    fixtures: tuple[tuple[str, str, str], ...] = (
        ("direct_stdlib_re", "ast", "import re\n"),
        ("direct_cpython_sre", "vm", "import _sre\n"),
        ("third_party_regex", "rust", "from regex import compile\n"),
        ("aliased_regex", "ast", "import re as innocent\ninnocent.search('a', 'a')\n"),
        ("cross_candidate", "rust", "from candidates import vm_candidate\n"),
        ("cross_candidate_dotted", "zig", "import candidates.rust_candidate as engine\n"),
        ("dynamic_import", "ast", "__import__('r' + 'e')\n"),
        ("chr_obfuscated_import", "vm", "__import__(chr(114) + chr(101))\n"),
        ("join_obfuscated_import", "rust", "__import__(''.join(('r', 'e')))\n"),
        ("importlib_indirection", "ast", "import importlib\nimportlib.import_module('re')\n"),
        ("builtins_subscript", "vm", "__builtins__['__im' + 'port__']('re')\n"),
        ("getattr_indirection", "rust", "getattr(__builtins__, '__im' + 'port__')('re')\n"),
        ("foreign_ctypes", "rust", "import ctypes\nctypes.CDLL('libpcre2-8.so')\n"),
        ("unowned_zig_library", "zig", "import ctypes\nctypes.CDLL('libpcre2-8.so')\n"),
        (
            "zig_owned_path_reassignment",
            "zig",
            "import ctypes\nimport os\nclass _Native:\n"
            "    def __init__(self):\n"
            "        path = os.path.join(os.path.dirname(__file__), '_zig_probe.so')\n"
            "        path = '/tmp/foreign-engine.so'\n"
            "        ctypes.CDLL(path)\n",
        ),
        ("environment_dispatch", "ast", "import os\nos.getenv('REGEX_ENGINE')\n"),
        ("environment_mapping", "vm", "import os\nos.environ['REGEX_ENGINE']\n"),
        ("external_process", "rust", "import subprocess\nsubprocess.run(['regex'])\n"),
        ("dynamic_eval", "ast", "eval('re.search')\n"),
        ("dynamic_exec", "vm", "exec('import re')\n"),
        ("benchmark_clock", "rust", "import time\ntime.perf_counter()\n"),
        ("holdout_path", "zig", "target = 'sealed/holdout/cases.json'\n"),
        ("benchmark_file", "ast", "open('benchmarks/cases.json')\n"),
        ("unowned_vm_configuration", "vm", "from candidates import _vm_native\n_vm_native.configure(search, compile)\n"),
    )
    checks: list[dict[str, Any]] = []
    for label, family, source in fixtures:
        result = analyze_python(source, family, f"<synthetic:{label}>")
        checks.append({"name": label, "passed": not result["passed"]})

    native_fixtures = (
        ("native_posix_regex", "regexec(pattern, text, 0, 0, 0);", "candidates/_vm_native.c", "vm"),
        ("native_pcre", "pcre2_match(pattern, text, 0, 0, 0, 0, 0, 0);", "candidates/rust/py_bridge.c", "rust"),
        ("native_cpython_import", 'PyImport_ImportModule("re");', "candidates/rust/py_bridge.c", "rust"),
        ("native_dynamic_loader", 'dlopen("libpcre.so", 1);', "candidates/_vm_native.c", "vm"),
        ("native_hidden_header", '#include "innocent_engine.h"\n', "candidates/rust/py_bridge.c", "rust"),
        ("native_hidden_extern", "extern int innocent_engine_match(const char *);\n", "candidates/rust/py_bridge.c", "rust"),
        ("rust_external_crate", "use regex::Regex;", "candidates/rust/src/lib.rs", "rust"),
        ("rust_environment", 'std::env::var("ENGINE");', "candidates/rust/src/lib.rs", "rust"),
        ("rust_hidden_extern", 'unsafe extern "C" { fn innocent_engine_match(); }', "candidates/rust/src/lib.rs", "rust"),
        ("zig_external_package", 'const r = @import("regex");', "candidates/zig/mini_regex.zig", "zig"),
        ("zig_hidden_extern", "extern fn innocent_engine_match() c_int;", "candidates/zig/mini_regex.zig", "zig"),
        ("zig_c_import", 'const c = @cImport({ @cInclude("hidden.h"); });', "candidates/zig/mini_regex.zig", "zig"),
        ("native_benchmark_clock", "clock_gettime(1, &value);", "candidates/zig/py_bridge.c", "zig"),
    )
    for label, source, path, family in native_fixtures:
        result = analyze_native(source, path, family)
        checks.append({"name": label, "passed": not result["passed"]})

    benign = analyze_native('/* pcre2_match(fake) */\nconst char *s = "regexec(fake)";\n', "<synthetic:comments>", "vm")
    checks.append({"name": "ignore_native_comments_and_display_literals", "passed": benign["passed"]})

    lifetime_code = strip_native(
        "struct Parser<'source> { source: &'source str }\n"
        "fn run_program<'context>(source: &'context str) {}\n"
    )
    checks.append({
        "name": "preserve_rust_lifetimes_and_owned_pipeline",
        "passed": bool(
            re.search(r"\bstruct\s+Parser\b", lifetime_code)
            and re.search(r"\bfn\s+run_program\s*<", lifetime_code)
        ),
    })

    clean_elf = parse_elf(synthetic_elf(undefined=("memchr",), exported=("rebar_compile",), needed=("libc.so.6",)))
    checks.append({
        "name": "parse_in_memory_owned_elf",
        "passed": clean_elf["undefined"] == ["memchr"] and clean_elf["exported"] == ["rebar_compile"] and clean_elf["needed"] == ["libc.so.6"],
    })
    excessive_sections = bytearray(synthetic_elf(exported=("rebar_compile",)))
    struct.pack_into("<H", excessive_sections, 60, MAX_ELF_SECTIONS + 1)
    try:
        parse_elf(bytes(excessive_sections))
    except (ElfError, struct.error, OverflowError):
        bounded_sections = True
    else:
        bounded_sections = False
    checks.append({"name": "reject_excessive_elf_section_count", "passed": bounded_sections})
    try:
        parse_elf(synthetic_elf(needed=("x" * (MAX_ELF_STRING_BYTES + 1),)))
    except (ElfError, struct.error, OverflowError):
        bounded_strings = True
    else:
        bounded_strings = False
    checks.append({"name": "reject_excessive_elf_symbol_string", "passed": bounded_strings})
    malicious_engine = synthetic_elf(undefined=("pcre2_match",), exported=tuple(sorted(RUST_REQUIRED_EXPORTS)), needed=("libpcre2-8.so.0",))
    malicious_bridge = synthetic_elf(undefined=("rebar_compile", "rebar_match"), exported=("PyInit__rust_bridge",), needed=("_rust_engine.so",))
    malicious = analyze_rust_binaries({"engine": malicious_engine, "bridge": malicious_bridge})
    checks.append({
        "name": "reject_in_memory_external_elf_dependency",
        "passed": not malicious["passed"] and any(item["code"] == "external_regex_native_dependency" for item in malicious["issues"]),
    })
    missing_link = analyze_rust_binaries({
        "engine": synthetic_elf(exported=tuple(sorted(RUST_REQUIRED_EXPORTS))),
        "bridge": synthetic_elf(undefined=("rebar_compile", "rebar_match"), exported=("PyInit__rust_bridge",), needed=("libc.so.6",)),
    })
    checks.append({
        "name": "reject_bridge_without_owned_elf_link",
        "passed": not missing_link["passed"] and any(item["code"] == "bridge_not_linked_to_owned_engine" for item in missing_link["issues"]),
    })
    hidden_dependency = analyze_rust_binaries({
        "engine": synthetic_elf(exported=tuple(sorted(RUST_REQUIRED_EXPORTS))),
        "bridge": synthetic_elf(
            undefined=("rebar_compile", "rebar_match"),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so", "libinnocent_engine.so"),
        ),
    })
    checks.append({
        "name": "reject_disguised_third_party_elf_dependency",
        "passed": not hidden_dependency["passed"] and any(
            item["code"] == "unapproved_native_dependency"
            for item in hidden_dependency["issues"]
        ),
    })

    clean_vm_data = {
        "native": synthetic_elf(
            undefined=("PyUnicode_FromString",),
            exported=("PyInit__vm_native",),
            needed=("libc.so.6",),
        ),
    }
    clean_rust_data = {
        "engine": synthetic_elf(
            undefined=("Py_GetRecursionLimit",),
            exported=tuple(sorted(RUST_REQUIRED_EXPORTS)),
            needed=("libc.so.6",),
        ),
        "bridge": synthetic_elf(
            undefined=("PyUnicode_FromString", "rebar_compile", "rebar_match"),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so", "libc.so.6"),
            runpaths=("$ORIGIN",),
        ),
    }
    clean_zig_data = {
        "engine": synthetic_elf(
            undefined=("_PyUnicode_IsAlpha",),
            exported=tuple(sorted(ZIG_REQUIRED_EXPORTS)),
            needed=("libc.so.6",),
        ),
        "bridge": synthetic_elf(
            undefined=(
                "PyUnicode_FromString", "rebar_zig_compile",
                "rebar_zig_match_wide", "rebar_zig_match_captures_wide",
            ),
            exported=("PyInit__zig_bridge",),
            needed=("_zig_probe.so", "libc.so.6"),
            runpaths=("$ORIGIN",),
        ),
    }
    clean_all = analyze_all_native_binaries({
        "vm": clean_vm_data,
        "rust": clean_rust_data,
        "zig": clean_zig_data,
    })
    checks.append({
        "name": "accept_five_owned_synthetic_elf_binaries_and_python_api_symbols",
        "passed": clean_all["passed"] and clean_all["audited_binary_count"] == 5,
    })

    def rejects_elf(label: str, result: dict[str, Any], code: str) -> None:
        checks.append({
            "name": label,
            "passed": not result["passed"] and any(item["code"] == code for item in result["issues"]),
        })

    rejects_elf(
        "reject_vm_disguised_external_engine",
        analyze_vm_binaries({"native": synthetic_elf(
            exported=("PyInit__vm_native",),
            needed=("libc.so.6", "libinnocent_engine.so"),
        )}),
        "unapproved_native_dependency",
    )
    rejects_elf(
        "reject_vm_external_regex_symbol",
        analyze_vm_binaries({"native": synthetic_elf(
            undefined=("pcre2_match",),
            exported=("PyInit__vm_native",),
            needed=("libc.so.6",),
        )}),
        "external_regex_native_dependency",
    )
    rejects_elf(
        "reject_vm_cross_candidate_engine_symbol",
        analyze_vm_binaries({"native": synthetic_elf(
            undefined=("rebar_compile",),
            exported=("PyInit__vm_native",),
            needed=("libc.so.6",),
        )}),
        "cross_candidate_native_dependency",
    )
    rejects_elf(
        "reject_vm_untrusted_runpath",
        analyze_vm_binaries({"native": synthetic_elf(
            exported=("PyInit__vm_native",),
            needed=("libc.so.6",),
            runpaths=("/tmp/foreign-engine",),
        )}),
        "untrusted_native_runpath",
    )
    rejects_elf(
        "reject_vm_wrong_module_initializer",
        analyze_vm_binaries({"native": synthetic_elf(
            exported=("PyInit__foreign_engine",),
            needed=("libc.so.6",),
        )}),
        "missing_vm_native_initializer",
    )
    rejects_elf(
        "reject_zig_engine_disguised_external_dependency",
        analyze_zig_binaries({
            **clean_zig_data,
            "engine": synthetic_elf(
                exported=tuple(sorted(ZIG_REQUIRED_EXPORTS)),
                needed=("libc.so.6", "libinnocent_engine.so"),
            ),
        }),
        "unapproved_native_dependency",
    )
    rejects_elf(
        "reject_zig_bridge_disguised_external_dependency",
        analyze_zig_binaries({
            **clean_zig_data,
            "bridge": synthetic_elf(
                undefined=("rebar_zig_compile", "rebar_zig_match_wide"),
                exported=("PyInit__zig_bridge",),
                needed=("_zig_probe.so", "libinnocent_engine.so"),
            ),
        }),
        "unapproved_native_dependency",
    )
    rejects_elf(
        "reject_zig_bridge_wrong_linked_rust_engine",
        analyze_zig_binaries({
            **clean_zig_data,
            "bridge": synthetic_elf(
                undefined=("rebar_zig_compile", "rebar_zig_match_wide"),
                exported=("PyInit__zig_bridge",),
                needed=("_rust_engine.so",),
            ),
        }),
        "zig_bridge_not_linked_to_owned_engine",
    )
    rejects_elf(
        "reject_zig_bridge_wrong_engine_cross_candidate",
        analyze_zig_binaries({
            **clean_zig_data,
            "bridge": synthetic_elf(
                undefined=("rebar_zig_compile", "rebar_zig_match_wide"),
                exported=("PyInit__zig_bridge",),
                needed=("_rust_engine.so",),
            ),
        }),
        "cross_candidate_native_dependency",
    )
    rejects_elf(
        "reject_zig_bridge_compiler_bypass",
        analyze_zig_binaries({
            **clean_zig_data,
            "bridge": synthetic_elf(
                undefined=("rebar_zig_match_wide",),
                exported=("PyInit__zig_bridge",),
                needed=("_zig_probe.so",),
            ),
        }),
        "zig_bridge_bypasses_owned_compiler",
    )
    rejects_elf(
        "reject_zig_bridge_executor_bypass",
        analyze_zig_binaries({
            **clean_zig_data,
            "bridge": synthetic_elf(
                undefined=("rebar_zig_compile",),
                exported=("PyInit__zig_bridge",),
                needed=("_zig_probe.so",),
            ),
        }),
        "zig_bridge_bypasses_owned_executor",
    )
    rejects_elf(
        "reject_zig_bridge_unresolved_owned_symbols",
        analyze_zig_binaries({
            **clean_zig_data,
            "engine": synthetic_elf(
                exported=tuple(sorted(ZIG_REQUIRED_EXPORTS - {"rebar_zig_match_wide"})),
                needed=("libc.so.6",),
            ),
        }),
        "unresolved_owned_zig_engine_symbols",
    )
    rejects_elf(
        "reject_zig_engine_untrusted_runpath",
        analyze_zig_binaries({
            **clean_zig_data,
            "engine": synthetic_elf(
                exported=tuple(sorted(ZIG_REQUIRED_EXPORTS)),
                needed=("libc.so.6",),
                runpaths=("/tmp/foreign-engine",),
            ),
        }),
        "untrusted_native_runpath",
    )
    rejects_elf(
        "reject_zig_bridge_untrusted_runpath",
        analyze_zig_binaries({
            **clean_zig_data,
            "bridge": synthetic_elf(
                undefined=("rebar_zig_compile", "rebar_zig_match_wide"),
                exported=("PyInit__zig_bridge",),
                needed=("_zig_probe.so",),
                runpaths=("/tmp/foreign-engine",),
            ),
        }),
        "untrusted_native_runpath",
    )
    rejects_elf(
        "reject_zig_rust_cross_candidate_symbol",
        analyze_zig_binaries({
            **clean_zig_data,
            "bridge": synthetic_elf(
                undefined=("rebar_zig_compile", "rebar_zig_match_wide", "rebar_match"),
                exported=("PyInit__zig_bridge",),
                needed=("_zig_probe.so",),
            ),
        }),
        "cross_candidate_native_dependency",
    )
    rejects_elf(
        "reject_rust_zig_cross_candidate_symbol",
        analyze_rust_binaries({
            **clean_rust_data,
            "bridge": synthetic_elf(
                undefined=("rebar_compile", "rebar_match", "rebar_zig_match_wide"),
                exported=("PyInit__rust_bridge",),
                needed=("_rust_engine.so",),
            ),
        }),
        "cross_candidate_native_dependency",
    )
    rejects_elf(
        "reject_rust_bridge_untrusted_runpath",
        analyze_rust_binaries({
            **clean_rust_data,
            "bridge": synthetic_elf(
                undefined=("rebar_compile", "rebar_match"),
                exported=("PyInit__rust_bridge",),
                needed=("_rust_engine.so",),
                runpaths=("/tmp/foreign-engine",),
            ),
        }),
        "untrusted_native_runpath",
    )

    def synthetic_map(path: Path | str, *, deleted: bool = False) -> str:
        suffix = " (deleted)" if deleted else ""
        return f"00400000-00401000 r-xp 00000000 00:00 0 {path}{suffix}\n"

    for family in ("ast", "vm", "rust", "zig"):
        lines = "".join(
            synthetic_map(path)
            for path in NATIVE_BINARIES.get(family, {}).values()
        ) + synthetic_map("/usr/lib/libc.so.6")
        snapshot = classify_mapping_snapshot(lines, family)
        checks.append({
            "name": f"accept_exact_{family}_owned_memory_mappings",
            "passed": snapshot["passed"] and len(snapshot["observed_mapping_counts"]) == len(NATIVE_BINARIES.get(family, {})),
        })
    wrong_map = classify_mapping_snapshot(
        synthetic_map(NATIVE_BINARIES["zig"]["engine"])
        + synthetic_map(NATIVE_BINARIES["rust"]["engine"])
        + synthetic_map(NATIVE_BINARIES["zig"]["bridge"]),
        "zig",
    )
    checks.append({
        "name": "reject_cross_candidate_actual_memory_mapping",
        "passed": not wrong_map["passed"] and any(
            item["code"] == "cross_candidate_native_mapping"
            for item in wrong_map["issues"]
        ),
    })
    foreign_map = classify_mapping_snapshot(
        synthetic_map("/usr/lib/libpcre2-8.so.0"),
        "ast",
    )
    checks.append({
        "name": "reject_external_regex_actual_memory_mapping",
        "passed": not foreign_map["passed"] and any(
            item["code"] == "forbidden_mapped_regex_engine"
            for item in foreign_map["issues"]
        ),
    })
    unowned_map = classify_mapping_snapshot(
        synthetic_map(ROOT / "candidates" / "_hidden_engine.so"),
        "ast",
    )
    checks.append({
        "name": "reject_unapproved_candidate_actual_memory_mapping",
        "passed": not unowned_map["passed"] and any(
            item["code"] == "unapproved_candidate_native_mapping"
            for item in unowned_map["issues"]
        ),
    })
    deleted_map = classify_mapping_snapshot(
        synthetic_map(NATIVE_BINARIES["vm"]["native"], deleted=True),
        "vm",
    )
    checks.append({
        "name": "reject_deleted_owned_native_memory_mapping",
        "passed": not deleted_map["passed"] and any(
            item["code"] == "deleted_owned_native_mapping"
            for item in deleted_map["issues"]
        ),
    })
    try:
        parse_elf(b"not an ELF")
    except (ElfError, struct.error):
        rejected = True
    else:
        rejected = False
    checks.append({"name": "reject_invalid_elf", "passed": rejected})

    bad_cargo = analyze_manifests({
        "project": '[project]\nname="x"\ndependencies=[]\n',
        "rust": '[package]\nname="rebar-rust-continuation"\n[dependencies]\ninnocent={package="regex",version="1"}\n',
        "rust_lock": 'version=4\n[[package]]\nname="rebar-rust-continuation"\ndependencies=["regex"]\n[[package]]\nname="regex"\nversion="1.0.0"\n',
    })
    checks.append({
        "name": "reject_renamed_and_transitive_cargo_dependency",
        "passed": not bad_cargo["passed"] and {"external_cargo_dependencies", "transitive_rust_dependencies"}.issubset({item["code"] for item in bad_cargo["issues"]}),
    })
    failed = [item["name"] for item in checks if not item["passed"]]
    return {"passed": not failed, "checks": checks, "check_count": len(checks), "failed": failed, "fixture_storage": "in-memory only"}


def isolated_self_test() -> dict[str, Any]:
    """Execute and strictly validate every malicious control in a fresh process."""

    def rejected(reason: str, returncode: int | None = None) -> dict[str, Any]:
        execution: dict[str, Any] = {
            "isolated_subprocess": True,
            "interpreter": sys.executable,
            "expected_check_count": EXPECTED_SELF_TEST_CHECKS,
            "maximum_response_bytes": MAX_WORKER_RESPONSE_BYTES,
            "validated": False,
        }
        if returncode is not None:
            execution["exit_code"] = returncode
        return {
            "passed": False,
            "checks": [],
            "check_count": 0,
            "failed": [reason],
            "fixture_storage": "in-memory only",
            "execution": execution,
        }

    if len(EXPECTED_SELF_TEST_NAMES) != EXPECTED_SELF_TEST_CHECKS:
        return rejected("the independently pinned self-test control manifest is inconsistent")

    command = [
        sys.executable,
        "-I",
        "-B",
        str(Path(__file__).resolve()),
        "--self-test",
    ]
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return rejected(f"isolated malicious-control subprocess failed: {error}")

    stdout_bytes = len(process.stdout.encode("utf-8"))
    stderr_bytes = len(process.stderr.encode("utf-8"))
    if stdout_bytes > MAX_WORKER_RESPONSE_BYTES:
        return rejected("isolated malicious-control stdout exceeds the response bound", process.returncode)
    if stderr_bytes > MAX_WORKER_RESPONSE_BYTES:
        return rejected("isolated malicious-control stderr exceeds the response bound", process.returncode)
    if process.returncode != 0:
        return rejected("isolated malicious-control subprocess exited unsuccessfully", process.returncode)
    if process.stderr:
        return rejected("isolated malicious-control subprocess emitted unexpected stderr", process.returncode)

    lines = process.stdout.splitlines()
    if len(lines) != 1:
        return rejected("isolated malicious controls must produce exactly one JSON line", process.returncode)
    try:
        result = json.loads(lines[0])
    except (TypeError, json.JSONDecodeError) as error:
        return rejected(f"invalid isolated malicious-control JSON: {error}", process.returncode)

    required_keys = {"passed", "checks", "check_count", "failed", "fixture_storage"}
    if not isinstance(result, dict) or set(result) != required_keys:
        return rejected("isolated malicious-control JSON does not match the exact required schema", process.returncode)
    if result["passed"] is not True or result["failed"] != []:
        return rejected("one or more isolated malicious controls failed", process.returncode)
    if result["fixture_storage"] != "in-memory only":
        return rejected("malicious-control fixtures were not certified in-memory-only", process.returncode)
    checks = result["checks"]
    if (
        not isinstance(checks, list)
        or result["check_count"] != EXPECTED_SELF_TEST_CHECKS
        or len(checks) != EXPECTED_SELF_TEST_CHECKS
    ):
        return rejected("the complete set of 73 malicious controls did not execute", process.returncode)

    names: set[str] = set()
    for item in checks:
        if (
            not isinstance(item, dict)
            or set(item) != {"name", "passed"}
            or not isinstance(item["name"], str)
            or item["passed"] is not True
            or item["name"] in names
        ):
            return rejected("an isolated malicious control is invalid, duplicated, or failing", process.returncode)
        names.add(item["name"])
    if names != EXPECTED_SELF_TEST_NAMES:
        missing = sorted(EXPECTED_SELF_TEST_NAMES - names)
        unexpected = sorted(names - EXPECTED_SELF_TEST_NAMES)
        return rejected(
            f"the malicious-control manifest changed: missing={missing!r}, unexpected={unexpected!r}",
            process.returncode,
        )

    result["execution"] = {
        "isolated_subprocess": True,
        "interpreter": sys.executable,
        "expected_check_count": EXPECTED_SELF_TEST_CHECKS,
        "validated_check_count": len(names),
        "maximum_response_bytes": MAX_WORKER_RESPONSE_BYTES,
        "response_bytes": stdout_bytes,
        "exit_code": process.returncode,
        "validated": True,
    }
    return result


def read_authorized_inputs() -> tuple[
    dict[str, str],
    dict[str, str],
    dict[str, str],
    dict[str, dict[str, bytes]],
    list[dict[str, Any]],
]:
    python: dict[str, str] = {}
    native: dict[str, str] = {}
    manifests: dict[str, str] = {}
    binaries: dict[str, dict[str, bytes]] = {
        "vm": {},
        "rust": {},
        "zig": {},
    }
    issues: list[dict[str, Any]] = []
    for family, path in PYTHON_SOURCES.items():
        try:
            python[family] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            issues.append(finding(relative(path), "required_source_unreadable", str(error)))
    for family_paths in NATIVE_SOURCES.values():
        for path in family_paths:
            try:
                native[relative(path)] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                issues.append(finding(relative(path), "required_native_source_unreadable", str(error)))
    for key, path in MANIFESTS.items():
        try:
            manifests[key] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            issues.append(finding(relative(path), "required_manifest_unreadable", str(error)))
    for family, paths in NATIVE_BINARIES.items():
        for role, path in paths.items():
            try:
                with path.open("rb") as stream:
                    data = stream.read(MAX_ELF_BYTES + 1)
                if len(data) > MAX_ELF_BYTES:
                    issues.append(finding(
                        relative(path), "native_binary_size_limit_exceeded",
                        f"owned native binary exceeds {MAX_ELF_BYTES} bytes",
                    ))
                    continue
                binaries[family][role] = data
            except OSError as error:
                issues.append(finding(relative(path), "required_native_binary_unreadable", str(error)))
    return python, native, manifests, binaries, issues


def run_audit() -> dict[str, Any]:
    tests = isolated_self_test()
    python, native, manifests, binaries, read_issues = read_authorized_inputs()
    manifest_result = analyze_manifests(manifests) if len(manifests) == len(MANIFESTS) else {"passed": False, "issues": []}
    binary_result = analyze_all_native_binaries(binaries)
    static_binary_evidence = {
        family: result["files"]
        for family, result in binary_result["families"].items()
    }
    del binaries
    families: dict[str, Any] = {}
    fingerprints: set[tuple[str, str, str]] = set()
    for family in ("ast", "vm", "rust", "zig"):
        if family not in python:
            families[family] = {"passed": False, "issues": [finding(relative(PYTHON_SOURCES[family]), "required_source_unreadable", "candidate source could not be audited")]}
            continue
        path = relative(PYTHON_SOURCES[family])
        source_result = analyze_python(python[family], family, path)
        tree = source_result.pop("tree", None)
        native_results: list[dict[str, Any]] = []
        for native_path in NATIVE_SOURCES.get(family, ()):
            key = relative(native_path)
            if key in native:
                checked = analyze_native(native[key], key, family)
                checked["file"] = key
                checked["sha256"] = hashlib.sha256(native[key].encode("utf-8")).hexdigest()
                native_results.append(checked)
            else:
                native_results.append({"file": key, "passed": False, "issues": [finding(key, "required_native_source_unreadable", "native source could not be audited")]})
        if tree is not None and all(relative(item) in native for item in NATIVE_SOURCES.get(family, ())):
            pipeline = verify_pipeline(family, tree, native)
        else:
            pipeline = {"passed": False, "issues": [finding(path, "pipeline_unverifiable", "one or more required source inputs could not be parsed")]}
        family_binary_result = (
            {"passed": True, "files": {}, "issues": []}
            if family == "ast"
            else binary_result["families"][family]
        )
        static_passed = (
            source_result["passed"]
            and pipeline["passed"]
            and all(item["passed"] for item in native_results)
            and family_binary_result["passed"]
        )
        runtime = (
            isolated_probe(family, static_binary_evidence.get(family, {}))
            if static_passed
            else {"passed": False, "skipped": "static source or owned native ELF provenance failed"}
        )
        components = (str(pipeline.get("parser", "")), str(pipeline.get("compiler", "")), str(pipeline.get("executor", "")))
        if pipeline["passed"]:
            fingerprints.add(components)
        families[family] = {
            "passed": static_passed and runtime["passed"],
            "python_source": {"file": path, "sha256": hashlib.sha256(python[family].encode("utf-8")).hexdigest(), **source_result},
            "native_sources": native_results,
            "owned_pipeline": pipeline,
            "isolated_runtime": runtime,
            "native_binary_provenance": (
                "not_applicable_pure_python; no candidate native mapping observed"
                if family == "ast" and runtime.get("passed")
                else "not_applicable_pure_python; mapping audit failed"
                if family == "ast"
                else "verified_exact_owned_elf_and_actual_hashed_memory_mappings"
                if family_binary_result["passed"] and runtime.get("passed")
                else "failed_exact_owned_elf_or_actual_memory_mapping_provenance"
            ),
        }
    core_families = ("ast", "vm", "rust")
    verified_core_count = sum(families[item].get("passed", False) for item in core_families)
    all_family_passed = len(families) == 4 and all(item.get("passed", False) for item in families.values())
    mapping_results = {
        name: item.get("isolated_runtime", {}).get("native_mapping_provenance", {})
        for name, item in families.items()
    }
    mapping_provenance = {
        "passed": len(mapping_results) == 4 and all(item.get("passed", False) for item in mapping_results.values()),
        "source": "/proc/self/maps in each isolated candidate worker",
        "families": {
            name: {
                "passed": item.get("passed", False),
                "expected_owned_mapping_count": item.get("expected_owned_mapping_count", 0),
                "observed_owned_mapping_count": item.get("observed_owned_mapping_count", 0),
            }
            for name, item in mapping_results.items()
        },
    }
    passed = (
        tests["passed"]
        and not read_issues
        and manifest_result["passed"]
        and binary_result["passed"]
        and mapping_provenance["passed"]
        and all_family_passed
        and verified_core_count >= 3
        and len(fingerprints) >= 3
    )
    return {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "audit_history": list(FAIL_CLOSED_AUDIT_HISTORY),
        "passed": passed,
        "result": "PASS" if passed else "FAIL",
        "minimum_required_independent_families": 3,
        "verified_core_family_count": verified_core_count,
        "verified_distinct_pipeline_count": len(fingerprints),
        "core_families": list(core_families),
        "all_public_source_families": ["ast", "vm", "rust", "zig"],
        "manifest_provenance": manifest_result,
        "native_elf_provenance": binary_result,
        "vm_native_elf_provenance": binary_result["families"]["vm"],
        "rust_native_elf_provenance": binary_result["families"]["rust"],
        "zig_native_elf_provenance": binary_result["families"]["zig"],
        "runtime_native_mapping_provenance": mapping_provenance,
        "families": families,
        "self_test": tests,
        "input_issues": read_issues,
        "scope": {
            "explicit_source_paths_only": True,
            "repository_enumeration": False,
            "candidate_imports": "isolated subprocess only, with prohibited import and native-loader probes",
            "native_elf_paths": [
                relative(path)
                for roles in NATIVE_BINARIES.values()
                for path in roles.values()
            ],
            "runtime_native_mapping_source": "/proc/self/maps inside isolated candidate workers only",
            "mapped_binaries_hashed_against_static_elf": True,
            "resource_limits": {
                "maximum_python_source_bytes": MAX_PYTHON_SOURCE_BYTES,
                "maximum_python_ast_nodes": MAX_PYTHON_AST_NODES,
                "maximum_native_source_bytes": MAX_NATIVE_SOURCE_BYTES,
                "maximum_elf_bytes": MAX_ELF_BYTES,
                "maximum_elf_sections": MAX_ELF_SECTIONS,
                "maximum_elf_string_table_bytes": MAX_ELF_STRING_TABLE_BYTES,
                "maximum_elf_string_bytes": MAX_ELF_STRING_BYTES,
                "maximum_elf_dynamic_entries": MAX_ELF_DYNAMIC_ENTRIES,
                "maximum_elf_dynamic_symbols": MAX_ELF_DYNAMIC_SYMBOLS,
                "maximum_proc_maps_bytes": MAX_PROC_MAP_BYTES,
                "maximum_proc_maps_rows": MAX_PROC_MAP_ROWS,
                "maximum_proc_maps_line_bytes": MAX_PROC_MAP_LINE_BYTES,
                "maximum_worker_response_bytes": MAX_WORKER_RESPONSE_BYTES,
                "hash_chunk_bytes": HASH_CHUNK_BYTES,
            },
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "synthetic_malicious_fixtures": "in-memory only",
            "malicious_self_tests": "all 73 exact named controls validated in a fresh pinned isolated subprocess",
        },
        "limitations": [
            "Static and guarded-runtime auditing is evidence about the enumerated source graph and exercised entry points; it is not a mathematical proof of all future execution paths.",
            "Native provenance covers exactly the five authorized VM, Rust, and Zig ELF files and their actual per-worker mapped-file hashes; it does not attest to later file changes or unexercised future code paths.",
            "No implicit Cargo build script, unlisted repository source, holdout, benchmark, external package registry, or build environment was inspected.",
            "The Zig source retains an owned tree-evaluator diagnostic export; the audited public C bridge does not call that export.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run in-memory malicious-fixture tests only")
    parser.add_argument("--output", type=Path, default=REPORT, help="the single authorized JSON report path")
    args = parser.parse_args(argv)
    if args.self_test:
        report = self_test()
        print(json.dumps(report, sort_keys=True))
        return 0 if report["passed"] else 1
    if args.output.resolve() != REPORT.resolve():
        parser.error("only candidates/audits/FROM-SCRATCH-AUDIT.json is an authorized output")
    report = run_audit()
    summary = {
        "passed": report["passed"],
        "result": report["result"],
        "verified_core_family_count": report["verified_core_family_count"],
        "verified_distinct_pipeline_count": report["verified_distinct_pipeline_count"],
        "self_test_checks": report["self_test"]["check_count"],
        "family_results": {name: item.get("passed", False) for name, item in report["families"].items()},
        "manifest_passed": report["manifest_provenance"]["passed"],
        "native_elf_passed": report["native_elf_provenance"]["passed"],
        "native_elf_binary_count": report["native_elf_provenance"]["audited_binary_count"],
        "native_mapping_passed": report["runtime_native_mapping_provenance"]["passed"],
        "vm_native_elf_passed": report["vm_native_elf_provenance"]["passed"],
        "rust_native_elf_passed": report["rust_native_elf_provenance"]["passed"],
        "zig_native_elf_passed": report["zig_native_elf_provenance"]["passed"],
        "report": relative(REPORT),
    }
    if report["input_issues"]:
        summary["input_issues"] = report["input_issues"]
    if not report["self_test"]["passed"]:
        summary["self_test_failures"] = report["self_test"]["failed"]
    if report["passed"]:
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        REPORT.write_text(payload, encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    # Keep direct execution, pinned -I workers, and imported use on one
    # canonical module identity; the complete audit is proven under that path.
    project_root = str(ROOT)
    if not sys.path or sys.path[0] != project_root:
        sys.path.insert(0, project_root)
    from tools.audit_from_scratch import main as canonical_main

    raise SystemExit(canonical_main())
