#!/usr/bin/env python3
"""Additive, bounded provenance and no-delegation audit for owned engines.

The self-test never imports a production candidate or writes a report.  A
production audit imports each candidate only in its own guarded subprocess.
Source, ELF, and mapped-file identity are attested; a reproducible, hermetic
source-to-binary build is deliberately not claimed.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import audit_from_scratch as original


SCHEMA = "rebar-postfinal-no-delegation-audit-v1"
REPORT = ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
AUDITED_FAMILIES = ("ast", "vm", "rust", "zig")
MEASURED_FAMILIES = ("vm", "rust", "zig")
WORKER_FAMILIES = frozenset((*AUDITED_FAMILIES, "re"))
EXPECTED_SELF_TEST_CHECKS = 32
EXPECTED_SELF_TEST_NAMES = frozenset(
    {
        "direct_stdlib_re",
        "direct_cpython_sre",
        "third_party_regex",
        "cross_family_import",
        "dynamic_import",
        "enum_sys_modules",
        "aliased_registry",
        "from_import_sys_alias",
        "registry_assignment_alias",
        "getattr_registry",
        "joined_registry_key",
        "vars_module_registry",
        "dunder_module_registry",
        "cached_json_decoder_regex",
        "conditional_registry_delegation",
        "cross_family_registry",
        "function_globals_reflection",
        "os_sys_registry",
        "warnings_sys_registry",
        "c_python_module_registry",
        "c_python_module_loader",
        "c_computed_loader",
        "rust_external_crate",
        "rust_link_name_and_include",
        "rust_inline_assembly",
        "zig_external_package",
        "zig_dynamic_loader_and_external",
        "allow_owned_callback_calls",
        "allow_owned_generic_attributes",
        "allow_owned_rust_helper_imports",
        "allow_owned_zig_unicode_extern",
        "preserve_original_76_control_manifest",
    }
)

NATIVE_FINGERPRINT_KEYS = {
    ("vm", "native"): "candidates.vm_candidate:native-engine",
    ("rust", "engine"): "candidates.rust_candidate:native-engine",
    ("rust", "bridge"): "candidates.rust_candidate:native-bridge",
    ("zig", "engine"): "candidates.zig_candidate:native-engine",
    ("zig", "bridge"): "candidates.zig_candidate:native-bridge",
}


class AuditFailure(RuntimeError):
    """A required provenance or no-delegation invariant was not established."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditFailure(message)


def require_candidate_free() -> None:
    loaded = sorted(
        name
        for name in sys.modules
        if name.startswith("candidates.")
        and (
            name.endswith("_candidate")
            or name.rsplit(".", 1)[-1]
            in {"_vm_native", "_rust_bridge", "_zig_bridge"}
        )
    )
    require(not loaded, f"the audit parent imported a production candidate: {loaded!r}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(original.HASH_CHUNK_BYTES):
            digest.update(block)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    require(
        resolved.is_relative_to(ROOT),
        f"an authorized production input escaped the repository: {path}",
    )
    return str(resolved.relative_to(ROOT))


class NoDelegationPythonAudit(original.PythonSourceAudit):
    """Extend the original bounded visitor with module-capability tracking.

    Ordinary match ``.re``, ``getattr``, templates, user callbacks, and native
    bridge calls remain valid.  Only module registries, module reflection, and
    candidate-controlled access to another regex implementation are rejected.
    """

    _REFLECTIVE_ATTRIBUTES = frozenset(
        {"__globals__", "__builtins__", "__subclasses__", "__mro__", "__bases__"}
    )

    def __init__(self, family: str, path: str) -> None:
        super().__init__(family, path)
        self.module_aliases: set[str] = set()

    def expression_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Call):
            name = super().expression_name(node.func)
            if name == "vars" and len(node.args) == 1:
                parent = self.expression_name(node.args[0])
                return f"{parent}.__dict__" if parent else None
        return super().expression_name(node)

    @staticmethod
    def is_registry(name: str | None) -> bool:
        if not name:
            return False
        return name == "sys.modules" or ".sys.modules" in name

    def is_module_expression(self, node: ast.AST) -> bool:
        name = self.expression_name(node)
        if not name:
            return False
        root = name.partition(".")[0]
        return root in self.module_aliases or root in self.aliases

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            self.module_aliases.add(item.asname or item.name.partition(".")[0])
        super().visit_Import(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for item in node.names:
            if item.name != "*":
                self.module_aliases.add(item.asname or item.name)
        super().visit_ImportFrom(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        name = self.expression_name(node)
        if self.is_registry(name):
            self.add(node, "module_registry_delegation", name or "sys.modules")
        elif node.attr in self._REFLECTIVE_ATTRIBUTES:
            self.add(node, "reflective_engine_capability", name or node.attr)
        elif (
            node.attr == "__dict__"
            and self.is_module_expression(node.value)
        ):
            self.add(node, "reflective_module_dictionary", name or "module.__dict__")
        elif node.attr in original.FORBIDDEN_ENGINE_ROOTS and self.is_module_expression(
            node.value
        ):
            self.add(node, "cached_regex_module_capability", name or node.attr)
        super().visit_Attribute(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        parent = self.expression_name(node.value)
        key = original.constant_string(node.slice)
        if self.is_registry(parent):
            self.add(
                node,
                "indirect_module_registry_delegation",
                f"{parent}[{key!r}]",
            )
        elif (
            key in {"sys", "modules", "re", "regex", "_sre", "__globals__", "__builtins__"}
            and (
                self.is_module_expression(node.value)
                or (parent is not None and ".__dict__" in parent)
            )
        ):
            self.add(
                node,
                "reflective_module_dictionary_capability",
                f"{parent or '?'}[{key!r}]",
            )
        super().visit_Subscript(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = self.expression_name(node.func)
        if name == "getattr" and len(node.args) >= 2:
            target = self.expression_name(node.args[0])
            attribute = original.constant_string(node.args[1])
            if self.is_registry(target):
                self.add(
                    node,
                    "reflective_module_registry_delegation",
                    f"{target}:{attribute or '?'}",
                )
            elif self.is_module_expression(node.args[0]) and (
                attribute is None
                or attribute
                in {"sys", "modules", "re", "regex", "_sre", "__dict__", "__globals__"}
            ):
                self.add(
                    node,
                    "reflective_module_capability",
                    f"{target or '?'}:{attribute or '?'}",
                )
        elif name == "vars" and node.args and self.is_module_expression(node.args[0]):
            self.add(
                node,
                "reflective_module_dictionary",
                self.expression_name(node.args[0]) or "module",
            )
        super().visit_Call(node)


def analyze_python_no_delegation(
    source: str, family: str, path: str
) -> dict[str, Any]:
    checked = original.analyze_python(source, family, path)
    tree = checked.pop("tree", None)
    if tree is None:
        return checked
    extra = NoDelegationPythonAudit(family, path)
    try:
        extra.visit(tree)
    except (original.AuditLimitError, RecursionError) as error:
        checked["issues"].append(
            original.finding(path, "no_delegation_ast_limit_exceeded", str(error))
        )
    else:
        seen = {
            (item.get("file"), item.get("code"), item.get("detail"), item.get("line"))
            for item in checked["issues"]
        }
        for issue in extra.issues:
            identity = (
                issue.get("file"),
                issue.get("code"),
                issue.get("detail"),
                issue.get("line"),
            )
            if identity not in seen:
                checked["issues"].append(issue)
                seen.add(identity)
    checked["passed"] = not checked["issues"]
    checked["registry_capability_checked"] = True
    return checked


_NATIVE_INDIRECTION_RULES = (
    (
        "native_python_module_registry",
        re.compile(
            r"\b(?:PyImport_GetModuleDict|PyImport_AddModule(?:Object|Ref)?|"
            r"PyImport_ExecCodeModule(?:Object|Ex)?|PyEval_GetBuiltins|"
            r"PyEval_GetGlobals|PyEval_GetLocals|PySys_GetObject)\b"
        ),
    ),
    (
        "native_reflective_regex_registry",
        re.compile(
            r"\b(?:PyObject_GetAttrString|PyDict_GetItemString)\s*\("
            r"[^;]*?,\s*[\"'](?:modules|__globals__|__builtins__|"
            r"__import__|re|regex|_sre|candidates\.[^\"']+)[\"']",
            re.DOTALL,
        ),
    ),
    (
        "native_computed_loader",
        re.compile(
            r"(?:\b(?:PyImport_|PyEval_|dlopen|dlsym|regexec|pcre|onig|re2)\s*##|"
            r"##\s*(?:GetModuleDict|AddModule|ImportModule|dlopen|dlsym|regexec)|"
            r"\bPyImport_\s*,\s*(?:GetModuleDict|AddModule|ImportModule)\b)"
        ),
    ),
)


def analyze_native_no_delegation(
    source: str, path: str, family: str
) -> dict[str, Any]:
    checked = original.analyze_native(source, path, family)
    code = original.strip_native(source)
    with_strings = original.strip_native(source, preserve_strings=True)
    for rule, expression in _NATIVE_INDIRECTION_RULES:
        inspected = with_strings if rule == "native_reflective_regex_registry" else code
        for match in expression.finditer(inspected):
            checked["issues"].append(
                original.finding(
                    path,
                    rule,
                    match.group(0),
                    inspected.count("\n", 0, match.start()) + 1,
                )
            )

    if path.endswith(".rs"):
        patterns = (
            ("unowned_rust_module_path", r"#\s*\[\s*path\s*="),
            ("unowned_rust_link_alias", r"#\s*\[\s*(?:unsafe\s*\()?link(?:_name)?\b"),
            (
                "unowned_rust_source_inclusion",
                r"\b(?:include|include_str|include_bytes)\s*!\s*\(",
            ),
            ("unowned_rust_inline_assembly", r"\b(?:asm|global_asm)\s*!\s*\("),
        )
        for rule, pattern in patterns:
            for match in re.finditer(pattern, code):
                checked["issues"].append(
                    original.finding(
                        path,
                        rule,
                        match.group(0),
                        code.count("\n", 0, match.start()) + 1,
                    )
                )
    elif path.endswith(".zig"):
        for match in re.finditer(r"@import\s*\(([^)]*)\)", with_strings):
            if not re.fullmatch(r'\s*"std"\s*', match.group(1)):
                checked["issues"].append(
                    original.finding(
                        path,
                        "unowned_or_computed_zig_import",
                        match.group(0),
                        with_strings.count("\n", 0, match.start()) + 1,
                    )
                )
        expressions = (
            ("unowned_zig_external_source", r"@(?:extern|embedFile|cImport|cInclude)\s*\("),
            (
                "unowned_zig_dynamic_loader",
                r"\bDynLib\b|@field\s*\([^)]*(?:Dyn|Lib|dlopen|dlsym|load)",
            ),
        )
        for rule, expression in expressions:
            for match in re.finditer(expression, with_strings, re.IGNORECASE):
                checked["issues"].append(
                    original.finding(
                        path,
                        rule,
                        match.group(0),
                        with_strings.count("\n", 0, match.start()) + 1,
                    )
                )

    checked["passed"] = not checked["issues"]
    checked["callback_calls_permitted"] = True
    checked["registry_and_loader_indirection_checked"] = True
    return checked


def self_test() -> dict[str, Any]:
    """Run only bounded in-memory controls; never import a candidate."""

    require_candidate_free()
    require(
        len(EXPECTED_SELF_TEST_NAMES) == EXPECTED_SELF_TEST_CHECKS,
        "the independently pinned no-delegation control manifest is inconsistent",
    )
    python_fixtures = (
        ("direct_stdlib_re", "import re\n"),
        ("direct_cpython_sre", "import _sre\n"),
        ("third_party_regex", "from regex import compile\n"),
        ("cross_family_import", "from candidates import vm_candidate\n"),
        ("dynamic_import", "__import__('r' + 'e')\n"),
        ("enum_sys_modules", "import enum\nenum.sys.modules['re'].search('a', 'a')\n"),
        ("aliased_registry", "import enum as flags\nflags.sys.modules['re']\n"),
        ("from_import_sys_alias", "from enum import sys as system\nsystem.modules['re']\n"),
        (
            "registry_assignment_alias",
            "import enum\nregistry = enum.sys.modules\nregistry['re'].compile('a')\n",
        ),
        (
            "getattr_registry",
            "import enum\ngetattr(enum, 's' + 'ys').modules['re']\n",
        ),
        (
            "joined_registry_key",
            "import enum\nenum.sys.modules[''.join(('r', 'e'))]\n",
        ),
        (
            "vars_module_registry",
            "import enum\nvars(enum)['sys'].modules['re']\n",
        ),
        (
            "dunder_module_registry",
            "import enum\nenum.__dict__['sys'].modules['re']\n",
        ),
        (
            "cached_json_decoder_regex",
            "import enum\nenum.sys.modules['json.decoder'].re.search('a', 'a')\n",
        ),
        (
            "conditional_registry_delegation",
            "import enum\nif len(pattern) > 1:\n"
            "    engine = enum.sys.modules['re']\n"
            "    engine.compile(pattern)\n",
        ),
        (
            "cross_family_registry",
            "import enum\nenum.sys.modules['candidates.vm_candidate'].compile('a')\n",
        ),
        (
            "function_globals_reflection",
            "function = lambda: None\nfunction.__globals__['__builtins__']\n",
        ),
        ("os_sys_registry", "import os\nos.sys.modules['re']\n"),
        (
            "warnings_sys_registry",
            "import warnings\nwarnings.sys.modules['re']\n",
        ),
    )
    native_fixtures = (
        (
            "c_python_module_registry",
            "PyImport_GetModuleDict();",
            "candidates/rust/py_bridge.c",
            "rust",
        ),
        (
            "c_python_module_loader",
            'PyObject_GetAttrString(owner, "modules");',
            "candidates/zig/py_bridge.c",
            "zig",
        ),
        (
            "c_computed_loader",
            "#define JOIN(a,b) a##b\nJOIN(PyImport_, GetModuleDict)();",
            "candidates/_vm_native.c",
            "vm",
        ),
        (
            "rust_external_crate",
            "use regex::Regex;",
            "candidates/rust/src/lib.rs",
            "rust",
        ),
        (
            "rust_link_name_and_include",
            '#[link_name = "regexec"]\n'
            'unsafe extern "C" { fn memchr(); }\ninclude!("foreign.rs");\n',
            "candidates/rust/src/lib.rs",
            "rust",
        ),
        (
            "rust_inline_assembly",
            'unsafe { core::arch::asm!("call foreign_engine"); }',
            "candidates/rust/src/lib.rs",
            "rust",
        ),
        (
            "zig_external_package",
            'const engine = @import("regex");',
            "candidates/zig/mini_regex.zig",
            "zig",
        ),
        (
            "zig_dynamic_loader_and_external",
            'const x = @field(std, "Dyn" ++ "Lib");\n'
            '@extern(*anyopaque, .{ .name = "foreign_engine" });\n',
            "candidates/zig/mini_regex.zig",
            "zig",
        ),
    )

    checks: list[dict[str, Any]] = []
    for name, source in python_fixtures:
        result = analyze_python_no_delegation(source, "rust", f"<synthetic:{name}>")
        checks.append({"name": name, "passed": not result["passed"]})
    for name, source, path, family in native_fixtures:
        result = analyze_native_no_delegation(source, path, family)
        checks.append({"name": name, "passed": not result["passed"]})

    benign = (
        (
            "allow_owned_callback_calls",
            "PyObject_CallOneArg(replacement, match);\n"
            "PyObject_Vectorcall(callback, arguments, 1, NULL);\n",
            "candidates/rust/py_bridge.c",
            "rust",
        ),
        (
            "allow_owned_generic_attributes",
            'PyObject_GetAttrString(pattern, "groupindex");\n'
            'PyObject_GetAttrString(pattern, "_templates");\n',
            "candidates/rust/py_bridge.c",
            "rust",
        ),
        (
            "allow_owned_rust_helper_imports",
            'PyImport_ImportModule("copyreg");\n'
            'PyImport_ImportModule("functools");\n'
            'PyImport_ImportModule("inspect");\n',
            "candidates/rust/py_bridge.c",
            "rust",
        ),
        (
            "allow_owned_zig_unicode_extern",
            "extern fn _PyUnicode_IsAlpha(u32) c_int;\n"
            'const std = @import("std");\n',
            "candidates/zig/mini_regex.zig",
            "zig",
        ),
    )
    for name, source, path, family in benign:
        result = analyze_native_no_delegation(source, path, family)
        checks.append({"name": name, "passed": result["passed"]})
    checks.append(
        {
            "name": "preserve_original_76_control_manifest",
            "passed": (
                original.EXPECTED_SELF_TEST_CHECKS == 76
                and len(original.EXPECTED_SELF_TEST_NAMES) == 76
            ),
        }
    )
    names = {item["name"] for item in checks}
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(checks) != EXPECTED_SELF_TEST_CHECKS or names != EXPECTED_SELF_TEST_NAMES:
        failed.append("no_delegation_control_manifest_mismatch")
    require_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "passed": not failed,
        "result": "PASS" if not failed else "FAIL",
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "fixture_storage": "in-memory only",
        "candidate_imported": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


GUARDED_WORKER_SOURCE = r'''
import builtins
import ctypes
import enum
import functools
import gc
import hashlib
import importlib
import json
import os
import sys
import time
import tracemalloc
import types
import warnings

MAX_MAP_BYTES = 4 * 1024 * 1024
MAX_MAP_ROWS = 16384
MAX_MAP_LINE_BYTES = 16384
MAX_RESPONSE_BYTES = 256 * 1024
HASH_CHUNK_BYTES = 1024 * 1024

root, family, bridge, expected_text, mode = sys.argv[1:6]
if family not in {"re", "ast", "vm", "rust", "zig"}:
    raise RuntimeError("invalid guarded worker family")
if mode not in {"smoke", "persistent"}:
    raise RuntimeError("invalid guarded worker mode")
sys.path.insert(0, root)
pilot = None
if mode == "persistent":
    from tools import rust_v7_calibration_pilot as pilot
expected_hashes = json.loads(expected_text)
native_paths = {
    "vm": {
        "native": os.path.normpath(os.path.join(root, "candidates", "_vm_native.cpython-314-x86_64-linux-gnu.so")),
    },
    "rust": {
        "engine": os.path.normpath(os.path.join(root, "candidates", "_rust_engine.so")),
        "bridge": os.path.normpath(os.path.join(root, "candidates", "_rust_bridge.cpython-314-x86_64-linux-gnu.so")),
    },
    "zig": {
        "engine": os.path.normpath(os.path.join(root, "candidates", "_zig_probe.so")),
        "bridge": os.path.normpath(os.path.join(root, "candidates", "_zig_bridge.cpython-314-x86_64-linux-gnu.so")),
    },
}
all_native_paths = {
    path: (owner, role)
    for owner, roles in native_paths.items()
    for role, path in roles.items()
}
owned = set()
if family != "re":
    owned.add("candidates." + family + "_candidate")
    if bridge:
        owned.add("candidates." + bridge)
blocked_regex_roots = {
    "regex", "regex_lite", "regex_automata", "regex_syntax",
    "fancy_regex", "re2", "pcre", "pcre2", "onig", "oniguruma",
    "onigurumacffi", "_onigurumacffi", "hyperscan", "aho_corasick",
    "rebar", "sre", "sre_compile", "sre_parse", "sre_constants",
}
if family != "re":
    blocked_regex_roots.update({"re", "_sre"})
blocked_events = []
native_loads = []
verified_native_digest_cache = {}


def prohibited(name):
    name = str(name)
    base = name.partition(".")[0]
    if base in blocked_regex_roots:
        return True
    if name.startswith("candidates.") and name not in owned:
        return True
    return False


def scrub_preloaded_capabilities():
    forbidden = []
    for key, module in tuple(sys.modules.items()):
        if prohibited(key):
            forbidden.append(module)
            sys.modules.pop(key, None)
    forbidden_ids = {id(item) for item in forbidden if isinstance(item, types.ModuleType)}
    for module in tuple(sys.modules.values()):
        if not isinstance(module, types.ModuleType):
            continue
        namespace = getattr(module, "__dict__", None)
        if not isinstance(namespace, dict):
            continue
        for key, value in tuple(namespace.items()):
            if isinstance(value, types.ModuleType) and (
                id(value) in forbidden_ids or prohibited(value.__name__)
            ):
                namespace.pop(key, None)


def deny(kind, target):
    blocked_events.append({"kind": kind, "target": str(target)})
    raise ImportError("guarded candidate rejected " + kind + ": " + str(target))


def guard_hook(event, args):
    if event == "import" and args and prohibited(args[0]):
        deny("audit_import", args[0])
    elif event == "ctypes.dlopen":
        target = args[0] if args else None
        expected = native_paths.get("zig", {}).get("engine")
        if (
            family != "zig"
            or target is None
            or os.path.normpath(os.fspath(target)) != expected
        ):
            deny("native_load", target)
        native_loads.append(expected)
    elif event == "ctypes.dlsym":
        symbol = args[1] if len(args) > 1 else ""
        library = args[0] if args else None
        path = getattr(library, "_name", None)
        if (
            family != "zig"
            or not str(symbol).startswith("rebar_zig_")
            or path is None
            or os.path.normpath(os.fspath(path))
            != native_paths["zig"]["engine"]
        ):
            deny("native_symbol", symbol)
    elif (
        event == "subprocess.Popen"
        or event == "os.system"
        or event.startswith("os.exec")
        or event.startswith("os.spawn")
        or event in {"os.fork", "os.posix_spawn"}
    ):
        deny("external_process", event)
    elif event == "open" and args:
        raw = args[0]
        if not isinstance(raw, (str, bytes, os.PathLike)):
            return
        target = os.path.normpath(os.fsdecode(raw))
        lowered = target.casefold()
        if (
            "holdout" in lowered
            or "benchmark" in lowered
            or "frozen-performance" in lowered
            or "/performance/v9/" in lowered.replace("\\", "/")
        ):
            deny("restricted_evidence_access", target)
        candidate_root = os.path.normpath(os.path.join(root, "candidates")) + os.sep
        basename = os.path.basename(target)
        if (
            target.startswith(candidate_root)
            and (basename.endswith(".so") or ".so." in basename)
            and target not in all_native_paths
        ):
            deny("unapproved_candidate_native_file", target)


scrub_preloaded_capabilities()
sys.addaudithook(guard_hook)
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


def forbidden_native_name(value):
    lower = os.path.basename(value).casefold().replace("-", "_")
    return (
        lower in {"regcomp", "regexec", "regerror", "regfree", "pyinit__sre"}
        or lower.startswith(("pcre_", "pcre2_", "onig_", "oniguruma_", "hyperscan_", "hs_compile", "hs_scan", "re2_", "sre_"))
        or lower.startswith(("libpcre", "libonig", "libhyperscan", "libre2", "libregex", "libhs."))
        or lower.startswith(("pyinit__regex", "pyinit__re2", "pyinit__pcre", "pyinit__onig"))
    )


def verify_registry():
    forbidden = sorted(key for key in sys.modules if prohibited(key))
    unexpected = sorted(
        key
        for key in sys.modules
        if key.startswith("candidates.") and key not in owned
    )
    retained = []
    for module_name in ("enum", "os", "warnings", "json", "json.decoder"):
        module = sys.modules.get(module_name)
        if not isinstance(module, types.ModuleType):
            continue
        for key, value in tuple(module.__dict__.items()):
            if isinstance(value, types.ModuleType) and prohibited(value.__name__):
                retained.append(module_name + "." + key)
    if forbidden or unexpected or retained:
        raise RuntimeError(
            "forbidden loaded or retained engine: "
            + repr({"modules": forbidden, "cross_family": unexpected, "retained": retained})
        )
    return {
        "passed": True,
        "forbidden_loaded_modules": forbidden,
        "unexpected_candidate_modules": unexpected,
        "retained_forbidden_module_references": retained,
    }


def native_stat_identity(value):
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def verify_native_mappings(force_hash=False):
    if not isinstance(force_hash, bool):
        raise RuntimeError("the guarded native force-hash policy is invalid")
    expected_paths = native_paths.get(family, {})
    if set(expected_hashes) != set(expected_paths):
        raise RuntimeError("guarded worker native roles do not match its family")
    with open("/proc/self/maps", "r", encoding="utf-8") as stream:
        content = stream.read(MAX_MAP_BYTES + 1)
    if len(content) > MAX_MAP_BYTES:
        raise RuntimeError("actual native mapping snapshot exceeds its bounded limit")
    lines = content.splitlines()
    if len(lines) > MAX_MAP_ROWS:
        raise RuntimeError("actual native mapping row count exceeds its bounded limit")
    observed = {}
    for line in lines:
        if len(line) > MAX_MAP_LINE_BYTES:
            raise RuntimeError("actual native mapping line exceeds its bounded limit")
        fields = line.split(None, 5)
        if len(fields) != 6:
            continue
        raw = fields[5].strip()
        if not raw.startswith("/"):
            continue
        deleted = raw.endswith(" (deleted)")
        path = os.path.normpath(raw[:-10] if deleted else raw)
        if forbidden_native_name(path):
            raise RuntimeError("forbidden external regex library is actually mapped: " + path)
        if path in all_native_paths:
            owner, _role = all_native_paths[path]
            if owner != family:
                raise RuntimeError("another candidate's native engine is actually mapped: " + path)
            if deleted:
                raise RuntimeError("an owned native mapping was deleted: " + path)
            observed[path] = observed.get(path, 0) + 1
        elif (
            path.startswith(os.path.normpath(os.path.join(root, "candidates")) + os.sep)
            and (os.path.basename(path).endswith(".so") or ".so." in os.path.basename(path))
        ):
            raise RuntimeError("an unapproved candidate native engine is actually mapped: " + path)
    evidence = []
    for role, path in sorted(expected_paths.items()):
        expected = expected_hashes.get(role)
        if not isinstance(expected, dict) or expected.get("file") != path:
            raise RuntimeError("a frozen native path was substituted: " + role)
        count = observed.get(path, 0)
        if not count:
            raise RuntimeError("an owned native engine was not actually mapped: " + path)
        if os.path.islink(path):
            raise RuntimeError("an owned mapped native engine became a symlink: " + path)
        before = native_stat_identity(os.stat(path, follow_symlinks=False))
        cached = verified_native_digest_cache.get(role)
        recomputed = (
            force_hash
            or cached is None
            or cached.get("file") != path
            or cached.get("identity") != before
        )
        if recomputed:
            digest = hashlib.sha256()
            with open(path, "rb") as stream:
                if native_stat_identity(os.fstat(stream.fileno())) != before:
                    raise RuntimeError("an owned native engine changed before hashing: " + path)
                while True:
                    block = stream.read(HASH_CHUNK_BYTES)
                    if not block:
                        break
                    digest.update(block)
                if native_stat_identity(os.fstat(stream.fileno())) != before:
                    raise RuntimeError("an owned native engine changed during hashing: " + path)
            if native_stat_identity(os.stat(path, follow_symlinks=False)) != before:
                raise RuntimeError("an owned native engine changed after hashing: " + path)
            actual = digest.hexdigest()
            verified_native_digest_cache[role] = {
                "file": path,
                "identity": before,
                "sha256": actual,
            }
        else:
            actual = cached["sha256"]
        if actual != expected.get("sha256"):
            raise RuntimeError("an actual mapped native engine changed: " + path)
        evidence.append(
            {
                "role": role,
                "file": os.path.relpath(path, root),
                "sha256": actual,
                "mapping_count": count,
                "matches_static_elf": True,
                "content_sha256_recomputed": recomputed,
            }
        )
    return {
        "passed": True,
        "source": "/proc/self/maps",
        "expected_owned_mapping_count": len(expected_paths),
        "observed_owned_mapping_count": len(evidence),
        "observed_owned_mappings": evidence,
        "force_hash": force_hash,
        "digest_cache_key": "device,inode,size,mtime_ns,ctime_ns",
    }


def verify_runtime(force_hash=False):
    return {
        "passed": True,
        "registry_provenance": verify_registry(),
        "native_mapping_provenance": verify_native_mappings(force_hash),
    }


def run_smoke(candidate):
    checks = []

    def check(name, value):
        if not value:
            raise AssertionError("owned engine operation failed: " + name)
        checks.append(name)
        verify_registry()

    match = candidate.search("a", "za")
    check("text_search", match is not None and match.group(0) == "a")
    match = candidate.fullmatch(b"ab", b"ab")
    check("bytes_fullmatch", match is not None and match.group(0) == b"ab")
    check("search_miss", candidate.search("a", "z") is None)
    capture = candidate.search(r"(?P<first>a)(b)", "zab")
    check(
        "named_capture",
        capture is not None
        and capture.group("first") == "a"
        and capture.groups() == ("a", "b"),
    )
    check("case_fold", candidate.search("a", "A", candidate.I) is not None)
    check("unicode_subject", candidate.search("é", "xé").group(0) == "é")
    check("lookahead", candidate.search(r"a(?=b)", "zab").span() == (1, 2))
    window = candidate.compile("ab").search("xxabyy", 2, 4)
    check("bounded_window", window is not None and window.span() == (2, 4))
    check("bytes_buffer", candidate.search(b"ab", bytearray(b"zab")).span() == (1, 3))
    check("memoryview_buffer", candidate.search(b"ab", memoryview(b"zab")).span() == (1, 3))
    check("findall", candidate.findall(r"(a)(b)", "zabxab") == [("a", "b"), ("a", "b")])
    check("finditer", [item.span() for item in candidate.finditer("a", "aba")] == [(0, 1), (2, 3)])
    check("split", candidate.split(",", "a,b,c") == ["a", "b", "c"])
    check("bounded_split", candidate.compile(",").split("a,b,c", 1) == ["a", "b,c"])
    callback_values = []

    def callback(item):
        callback_values.append(item.group(0))
        return item.group(0).upper()

    check(
        "owned_callable_replacement",
        candidate.sub("a", callback, "a-a") == "A-A"
        and callback_values == ["a", "a"],
    )
    callback_values.clear()
    check(
        "owned_callable_replacement_count",
        candidate.subn("a", callback, "a-a", count=1) == ("A-a", 1)
        and callback_values == ["a"],
    )
    scanner = candidate.compile("a").scanner("ba")
    first = scanner.search()
    check(
        "owned_scanner",
        first is not None and first.span() == (1, 2) and scanner.search() is None,
    )
    check("literal_escape", candidate.escape("a+b") == r"a\+b")
    runtime = verify_runtime(force_hash=True)
    return {
        "passed": True,
        "family": family,
        "fixed_smoke_checks": len(checks),
        "operation_checks": checks,
        "forbidden_candidate_import_attempts": list(blocked_events),
        "owned_native_loads": list(native_loads),
        "registry_provenance": runtime["registry_provenance"],
        "native_mapping_provenance": runtime["native_mapping_provenance"],
        "callbacks_permitted": True,
        "guard_persistent": True,
    }


def emit(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > MAX_RESPONSE_BYTES:
        raise RuntimeError("guarded worker response exceeds its bounded limit")
    sys.stdout.write(encoded + "\n")
    sys.stdout.flush()


prepared = None


def prepare_case(candidate, request):
    global prepared
    if pilot is None:
        raise RuntimeError("case preparation requires a persistent guarded worker")
    before = verify_runtime()
    case = pilot.unpack_calibration_value(request["case"])
    expected = pilot.unpack_calibration_value(request["expected"])
    if not isinstance(case, dict) or not isinstance(expected, dict):
        raise RuntimeError("invalid packed guarded case")
    if case.get("cohort") != "calibration" or expected.get("cohort") != "calibration":
        raise RuntimeError("a nonpublic case reached the guarded practice worker")
    if case.get("id") != expected.get("id"):
        raise RuntimeError("guarded practice case and expected answer disagree")
    expected_digest = expected.get("result_sha256")
    if (
        not isinstance(expected_digest, str)
        or len(expected_digest) != 64
        or any(mark not in "0123456789abcdef" for mark in expected_digest)
    ):
        raise RuntimeError("guarded practice expected answer has no frozen SHA-256")
    action = pilot.operation(candidate, case)
    if not callable(action):
        raise RuntimeError("guarded practice operation is not callable")
    prepared = (case, expected, action)
    return {
        "op": "prepare",
        "passed": True,
        "family": family,
        "module": module_name,
        "case": case["id"],
        "expected_sha256": expected_digest,
        "guard_persistent": True,
        "registry_provenance": before["registry_provenance"],
        "native_mapping_provenance": before["native_mapping_provenance"],
    }


def observe_case(candidate, request):
    if prepared is None or pilot is None:
        raise RuntimeError("no case has been prepared in this guarded worker")
    case, expected, action = prepared
    operations = request.get("operations")
    warmups = request.get("warmups")
    trial = request.get("trial")
    if (
        not isinstance(operations, int)
        or isinstance(operations, bool)
        or not 1 <= operations <= 16
        or not isinstance(warmups, int)
        or isinstance(warmups, bool)
        or not 0 <= warmups <= 64
        or not isinstance(trial, int)
        or isinstance(trial, bool)
        or trial < 0
    ):
        raise RuntimeError("invalid bounded guarded observation")
    verify_registry()
    expected_digest = pilot.correctness_gate(candidate, case, expected)
    for _ in range(warmups):
        action()
    tracemalloc.start()
    try:
        sampled = action()
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    pilot.exact_snapshot(sampled, expected, expected_digest, "guarded allocation sample")
    before_memory = pilot.proc_memory()
    previously_enabled = gc.isenabled()
    if previously_enabled:
        gc.disable()
    try:
        start = time.perf_counter_ns()
        result = None
        for _ in range(operations):
            result = action()
        elapsed = time.perf_counter_ns() - start
    finally:
        if previously_enabled:
            gc.enable()
    after_memory = pilot.proc_memory()
    pilot.exact_snapshot(result, expected, expected_digest, "guarded post-observation")
    if elapsed <= 0:
        raise RuntimeError("guarded observation produced a nonpositive interval")
    registry = verify_registry()
    return {
        "op": "observe",
        "passed": True,
        "family": family,
        "module": module_name,
        "case": case["id"],
        "trial": trial,
        "operations": operations,
        "warmups": warmups,
        "elapsed_ns": elapsed,
        "ns_per_op": elapsed / operations,
        "peak_traced_bytes": peak,
        "rss_before_kb": before_memory["rss_kb"],
        "rss_after_kb": after_memory["rss_kb"],
        "hwm_kb": after_memory["hwm_kb"],
        "expected_sha256": expected_digest,
        "correctness_checks": 3,
        "guard_persistent": True,
        "registry_provenance": registry,
    }


try:
    verify_registry()
    module_name = "re" if family == "re" else "candidates." + family + "_candidate"
    candidate = importlib.import_module(module_name)
    ready = verify_runtime(force_hash=True)
    if mode == "smoke":
        emit(run_smoke(candidate))
    else:
        emit(
            {
                "op": "ready",
                "passed": True,
                "family": family,
                "module": module_name,
                "guard_persistent": True,
                "registry_provenance": ready["registry_provenance"],
                "native_mapping_provenance": ready["native_mapping_provenance"],
            }
        )
        for raw in sys.stdin:
            if len(raw.encode("utf-8")) > MAX_RESPONSE_BYTES:
                raise RuntimeError("guarded worker request exceeds its bounded limit")
            request = json.loads(raw)
            if not isinstance(request, dict):
                raise RuntimeError("guarded worker request is not an object")
            operation = request.get("op")
            if operation == "verify":
                force_hash = request.get("force_hash", False)
                if not isinstance(force_hash, bool):
                    raise RuntimeError("invalid guarded worker force-hash request")
                result = {
                    "op": "verify",
                    "family": family,
                    **verify_runtime(force_hash=force_hash),
                }
            elif operation == "smoke":
                result = {"op": "smoke", **run_smoke(candidate)}
            elif operation == "prepare":
                result = prepare_case(candidate, request)
            elif operation == "observe":
                result = observe_case(candidate, request)
            elif operation == "quit":
                emit({"op": "quit", "passed": True, "family": family})
                break
            else:
                raise RuntimeError("unknown guarded worker operation: " + repr(operation))
            emit(result)
except BaseException as error:
    emit(
        {
            "passed": False,
            "family": family,
            "op": "error",
            "error_type": type(error).__name__,
            "error": str(error),
            "forbidden_candidate_import_attempts": blocked_events,
        }
    )
    sys.exit(1)
'''


def _expected_worker_hashes(
    family: str, native_elf_fingerprints: Mapping[str, str]
) -> dict[str, dict[str, str]]:
    require(family in WORKER_FAMILIES, f"unknown guarded worker family: {family!r}")
    if family in {"re", "ast"}:
        return {}
    roles = original.NATIVE_BINARIES[family]
    result: dict[str, dict[str, str]] = {}
    for role, path in sorted(roles.items()):
        key = NATIVE_FINGERPRINT_KEYS[(family, role)]
        digest = native_elf_fingerprints.get(key)
        require(
            isinstance(digest, str)
            and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            f"missing or invalid frozen native fingerprint: {key}",
        )
        result[role] = {"file": str(path), "sha256": digest}
    return result


def guarded_worker_command(
    family: str,
    native_elf_fingerprints: Mapping[str, str],
    *,
    persistent: bool = False,
) -> list[str]:
    """Return one reusable isolated-worker command; never launch a worker."""

    expected = _expected_worker_hashes(family, native_elf_fingerprints)
    bridge = "" if family == "re" else original.OWNED_BRIDGES[family] or ""
    return [
        sys.executable,
        "-I",
        "-B",
        "-c",
        GUARDED_WORKER_SOURCE,
        str(ROOT),
        family,
        bridge,
        json.dumps(expected, sort_keys=True, separators=(",", ":")),
        "persistent" if persistent else "smoke",
    ]


def validate_guarded_worker_response(
    family: str,
    response: Mapping[str, Any],
    native_elf_fingerprints: Mapping[str, str],
) -> dict[str, Any]:
    """Fail closed on worker identity, native mappings, and frozen hashes."""

    require(isinstance(response, Mapping), "guarded worker response is not an object")
    require(response.get("passed") is True, f"guarded worker failed: {dict(response)!r}")
    require(response.get("family") == family, "guarded worker substituted its family")
    mapping = response.get("native_mapping_provenance")
    if mapping is not None:
        require(isinstance(mapping, dict), "guarded worker mapping provenance is invalid")
        require(mapping.get("passed") is True, "guarded worker native mapping failed")
        expected = _expected_worker_hashes(family, native_elf_fingerprints)
        records = mapping.get("observed_owned_mappings")
        require(isinstance(records, list), "guarded worker native mappings are missing")
        actual: dict[str, dict[str, Any]] = {}
        for record in records:
            require(isinstance(record, dict), "invalid guarded worker native mapping")
            role = record.get("role")
            require(isinstance(role, str) and role not in actual, "duplicate native mapping role")
            actual[role] = record
        require(set(actual) == set(expected), "guarded worker native mapping roles changed")
        for role, pinned in expected.items():
            record = actual[role]
            require(
                record.get("file") == repo_relative(Path(pinned["file"]))
                and record.get("sha256") == pinned["sha256"]
                and record.get("matches_static_elf") is True
                and isinstance(record.get("mapping_count"), int)
                and record["mapping_count"] > 0,
                f"guarded worker native identity changed: {family}/{role}",
            )
    registry = response.get("registry_provenance")
    if registry is not None:
        require(
            isinstance(registry, dict)
            and registry.get("passed") is True
            and registry.get("forbidden_loaded_modules") == []
            and registry.get("unexpected_candidate_modules") == []
            and registry.get("retained_forbidden_module_references") == [],
            "guarded worker retained an external or cross-family engine",
        )
    return dict(response)


def isolated_no_delegation_probe(
    family: str, native_elf_fingerprints: Mapping[str, str]
) -> dict[str, Any]:
    require_candidate_free()
    command = guarded_worker_command(family, native_elf_fingerprints)
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=45,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise AuditFailure(f"guarded {family} worker could not be verified: {error}") from error
    stdout_bytes = len(process.stdout.encode("utf-8"))
    stderr_bytes = len(process.stderr.encode("utf-8"))
    require(
        stdout_bytes <= original.MAX_WORKER_RESPONSE_BYTES
        and stderr_bytes <= original.MAX_WORKER_RESPONSE_BYTES,
        f"guarded {family} worker exceeded its bounded response",
    )
    lines = process.stdout.splitlines()
    require(len(lines) == 1, f"guarded {family} worker emitted more than one result")
    try:
        response = json.loads(lines[0])
    except (TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise AuditFailure(f"guarded {family} worker emitted invalid JSON") from error
    require(process.returncode == 0, f"guarded {family} worker exited unsuccessfully: {response!r}")
    result = validate_guarded_worker_response(family, response, native_elf_fingerprints)
    require(result.get("fixed_smoke_checks", 0) >= 18, f"guarded {family} checks were omitted")
    require(result.get("callbacks_permitted") is True, "owned user callback was not exercised")
    require(result.get("guard_persistent") is True, "candidate guard did not remain installed")
    require(result.get("forbidden_candidate_import_attempts") == [], "candidate attempted a forbidden import")
    require_candidate_free()
    return result


def _load_original_report() -> tuple[dict[str, Any], str]:
    try:
        data = original.REPORT.read_bytes()
        report = json.loads(data)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AuditFailure("the original 76-control provenance report cannot be read") from error
    require(isinstance(report, dict), "the original provenance report is not an object")
    require(
        report.get("schema_version") == 1
        and report.get("audit") == "bounded-from-scratch-engine-provenance"
        and report.get("passed") is True
        and report.get("result") == "PASS",
        "the original from-scratch provenance report is not a verified PASS",
    )
    tests = report.get("self_test")
    require(isinstance(tests, dict), "the original pinned control evidence is missing")
    checks = tests.get("checks")
    require(
        tests.get("passed") is True
        and tests.get("check_count") == original.EXPECTED_SELF_TEST_CHECKS == 76
        and isinstance(checks, list)
        and len(checks) == 76
        and all(
            isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and item.get("passed") is True
            for item in checks
        )
        and {item["name"] for item in checks} == original.EXPECTED_SELF_TEST_NAMES,
        "the original exact 76 malicious controls were omitted or changed",
    )
    require(
        report.get("native_elf_provenance", {}).get("passed") is True
        and report.get("native_elf_provenance", {}).get("audited_binary_count") == 5
        and report.get("runtime_native_mapping_provenance", {}).get("passed") is True,
        "the original five-ELF and mapping provenance is not a verified PASS",
    )
    families = report.get("families")
    require(
        isinstance(families, dict)
        and set(families) == set(AUDITED_FAMILIES)
        and all(isinstance(families[name], dict) and families[name].get("passed") is True for name in AUDITED_FAMILIES),
        "the original provenance does not verify all four owned families",
    )
    return report, sha256_bytes(data)


def _verify_source_graph() -> dict[str, Any]:
    rust_root = ROOT / "candidates" / "rust"
    rust_src = rust_root / "src"
    expected_rust = {
        path.resolve()
        for path in original.NATIVE_SOURCES["rust"]
        if path.suffix == ".rs"
    }
    actual_rust = {path.resolve() for path in rust_src.glob("*.rs")}
    require(actual_rust == expected_rust, "the declared owned Rust source graph is not closed")
    build_script = rust_root / "build.rs"
    require(not build_script.exists(), "an implicit Rust build script was not audited")
    zig_root = ROOT / "candidates" / "zig"
    expected_zig = {
        path.resolve()
        for path in original.NATIVE_SOURCES["zig"]
        if path.suffix == ".zig"
    }
    actual_zig = {path.resolve() for path in zig_root.glob("*.zig")}
    require(actual_zig == expected_zig, "the declared owned Zig source graph is not closed")
    zig_build = zig_root / "build.zig"
    zig_package = zig_root / "build.zig.zon"
    require(
        not zig_build.exists() and not zig_package.exists(),
        "an unaudited Zig build manifest or package graph was introduced",
    )
    for paths in (
        tuple(original.PYTHON_SOURCES.values()),
        *(tuple(value) for value in original.NATIVE_SOURCES.values()),
        tuple(original.MANIFESTS.values()),
        *(tuple(value.values()) for value in original.NATIVE_BINARIES.values()),
    ):
        for path in paths:
            require(not path.is_symlink(), f"an authorized production input is a symlink: {path}")
            repo_relative(path)
    return {
        "passed": True,
        "rust_module_graph": sorted(repo_relative(path) for path in actual_rust),
        "implicit_rust_build_script_present": False,
        "zig_module_graph": sorted(repo_relative(path) for path in actual_zig),
        "zig_build_manifest_present": False,
        "source_to_binary_reproducibility_attested": False,
        "compiler_sysroot_or_linker_invocation_attested": False,
    }


def _original_source_hashes(report: Mapping[str, Any]) -> dict[str, str]:
    fingerprints: dict[str, str] = {}
    families = report["families"]
    for family in AUDITED_FAMILIES:
        current = families[family]
        python = current.get("python_source")
        require(isinstance(python, dict), f"missing original {family} Python provenance")
        fingerprints[python["file"]] = python["sha256"]
        native = current.get("native_sources")
        require(isinstance(native, list), f"missing original {family} native provenance")
        for item in native:
            require(isinstance(item, dict), "invalid original native-source record")
            require(item.get("passed") is True, "the original native-source audit did not pass")
            fingerprints[item["file"]] = item["sha256"]
    return fingerprints


def run_audit() -> dict[str, Any]:
    """Verify production provenance using isolated guarded candidates only."""

    require_candidate_free()
    controls = self_test()
    require(controls["passed"], f"no-delegation malicious controls failed: {controls['failed']!r}")
    inherited = original.isolated_self_test()
    require(
        inherited.get("passed") is True
        and inherited.get("check_count") == 76
        and {item["name"] for item in inherited.get("checks", ())}
        == original.EXPECTED_SELF_TEST_NAMES,
        "the original pinned 76 controls no longer pass in isolation",
    )
    original_report, original_report_hash = _load_original_report()
    graph = _verify_source_graph()
    python, native, manifests, binaries, read_issues = original.read_authorized_inputs()
    require(not read_issues, f"an exact owned production input cannot be verified: {read_issues!r}")
    require(
        set(python) == set(AUDITED_FAMILIES)
        and set(manifests) == set(original.MANIFESTS),
        "the closed production source or build manifest graph changed",
    )
    manifest_provenance = original.analyze_manifests(manifests)
    require(manifest_provenance.get("passed") is True, "an external Python or Rust build dependency was detected")
    native_evidence = original.analyze_all_native_binaries(binaries)
    require(
        native_evidence.get("passed") is True
        and native_evidence.get("audited_binary_count") == 5
        and native_evidence.get("expected_binary_count") == 5,
        "the five independently parsed and linked native ELFs do not verify",
    )

    source_fingerprints: dict[str, str] = {}
    qualified_source_fingerprints: dict[str, str] = {}
    build_input_fingerprints: dict[str, str] = {}
    families: dict[str, Any] = {}
    pinned_sources = _original_source_hashes(original_report)
    for family in AUDITED_FAMILIES:
        path = original.PYTHON_SOURCES[family]
        relative_path = repo_relative(path)
        digest = sha256_bytes(python[family].encode("utf-8"))
        require(pinned_sources.get(relative_path) == digest, f"original audited Python source changed: {relative_path}")
        source_fingerprints[relative_path] = digest
        if family in MEASURED_FAMILIES:
            qualified_source_fingerprints[relative_path] = digest
        checked_python = analyze_python_no_delegation(python[family], family, relative_path)
        require(checked_python["passed"], f"Python engine delegation or capability detected: {checked_python['issues']!r}")
        native_results = []
        for source_path in original.NATIVE_SOURCES.get(family, ()):
            key = repo_relative(source_path)
            require(key in native, f"an owned native source was omitted: {key}")
            source = native[key]
            source_digest = sha256_bytes(source.encode("utf-8"))
            require(pinned_sources.get(key) == source_digest, f"original audited native source changed: {key}")
            source_fingerprints[key] = source_digest
            qualified_source_fingerprints[key] = source_digest
            result = analyze_native_no_delegation(source, key, family)
            require(result["passed"], f"native engine delegation detected in {key}: {result['issues']!r}")
            native_results.append({"file": key, "sha256": source_digest, **result})
        source_result = original.analyze_python(python[family], family, relative_path)
        tree = source_result.pop("tree", None)
        require(tree is not None, f"the owned {family} source graph is not independently parsable")
        pipeline = original.verify_pipeline(family, tree, native)
        require(pipeline.get("passed") is True, f"the {family} parser/compiler/executor is not owned")
        families[family] = {
            "passed": False,
            "python_source": {"file": relative_path, "sha256": digest, **checked_python},
            "native_sources": native_results,
            "owned_pipeline": pipeline,
        }

    for key, content in sorted(manifests.items()):
        path = original.MANIFESTS[key]
        relative_path = repo_relative(path)
        digest = sha256_bytes(content.encode("utf-8"))
        build_input_fingerprints[relative_path] = digest
        source_fingerprints[relative_path] = digest

    native_fingerprints: dict[str, str] = {}
    original_native = original_report["native_elf_provenance"]["families"]
    for (family, role), key in sorted(NATIVE_FINGERPRINT_KEYS.items()):
        current = native_evidence["families"][family]["files"].get(role)
        previous = original_native.get(family, {}).get("files", {}).get(role)
        require(isinstance(current, dict) and isinstance(previous, dict), f"an owned ELF role is missing: {family}/{role}")
        require(
            current.get("sha256") == previous.get("sha256")
            and current.get("file") == previous.get("file"),
            f"the original-audited owned native ELF changed: {family}/{role}",
        )
        native_fingerprints[key] = current["sha256"]
    require(
        set(native_fingerprints) == set(NATIVE_FINGERPRINT_KEYS.values()),
        "the five exact native artifact identities changed",
    )

    for family in AUDITED_FAMILIES:
        runtime = isolated_no_delegation_probe(family, native_fingerprints)
        families[family]["isolated_runtime"] = runtime
        families[family]["native_mapping_provenance"] = runtime["native_mapping_provenance"]
        families[family]["passed"] = True

    require_candidate_free()
    result = {
        "schema": SCHEMA,
        "result": "PASS",
        "passed": True,
        "audit_source_path": repo_relative(Path(__file__)),
        "audit_source_sha256": sha256_file(Path(__file__)),
        "base_audit_source_path": repo_relative(Path(original.__file__)),
        "base_audit_source_sha256": sha256_file(Path(original.__file__)),
        "base_audit_report_path": repo_relative(original.REPORT),
        "base_audit_report_sha256": original_report_hash,
        "inherited_control_count": 76,
        "self_test": controls,
        "inherited_self_test": inherited,
        "source_graph_provenance": graph,
        "manifest_provenance": manifest_provenance,
        "source_fingerprints": dict(sorted(source_fingerprints.items())),
        "qualified_source_fingerprints": dict(sorted(qualified_source_fingerprints.items())),
        "build_input_fingerprints": dict(sorted(build_input_fingerprints.items())),
        "native_elf_fingerprints": dict(sorted(native_fingerprints.items())),
        "native_elf_provenance": native_evidence,
        "families": families,
        "scope": {
            "explicit_source_paths_only": True,
            "closed_owned_source_graph": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "runtime_native_mapping_source": "/proc/self/maps inside continuously guarded isolated candidate workers",
            "mapped_binaries_hashed_against_static_elf": True,
            "persistent_measurement_worker_available": True,
            "legitimate_user_callbacks_permitted": True,
            "hermetic_reproducible_source_to_binary_attested": False,
            "compiler_sysroot_or_linker_invocation_attested": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "self_test_candidate_imported": False,
        },
        "limitations": [
            "The audit verifies the exact enumerated owned production source graph, zero declared project and Cargo dependencies, and five exact parsed and actually mapped native ELF artifacts.",
            "A matching source hash and binary hash establish identity, not that the binary was reproducibly or hermetically built from that source.",
            "Compiler, linker, system-header, sysroot, environment, and Zig build invocation provenance is not independently attested.",
            "Guarded operation coverage and module-capability analysis are fail-closed bounded evidence, not a mathematical proof of all unexecuted future paths.",
            "Between explicitly forced content hashes, persistent workers reuse a verified SHA-256 only while device, inode, size, mtime_ns, and ctime_ns are unchanged; adversarial metadata-preserving file mutation is not independently excluded.",
            "The optional persistent worker performs measurements only when explicitly commanded by a separately frozen public benchmark; the audit and self-test perform no timing.",
        ],
    }
    return result


def write_report(report: Mapping[str, Any], output: Path) -> None:
    require(output.resolve() == REPORT.resolve(), "only the additive no-delegation evidence path is authorized")
    require(report.get("passed") is True, "refusing to write a failing no-delegation report")
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if REPORT.exists():
        require(REPORT.read_bytes() == payload, "refusing to overwrite existing no-delegation evidence")
        return
    try:
        with REPORT.open("xb") as stream:
            stream.write(payload)
    except OSError as error:
        raise AuditFailure("cannot exclusively create the additive no-delegation report") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--self-test", action="store_true", help="run only the 32 in-memory candidate-free malicious controls")
    group.add_argument("--audit", action="store_true", help="verify each owned engine in its own permanently guarded subprocess")
    parser.add_argument("--output", type=Path, default=REPORT, help="the one authorized additive JSON evidence path")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            report = self_test()
            print(json.dumps(report, sort_keys=True, separators=(",", ":")))
            return 0 if report["passed"] else 1
        report = run_audit()
        write_report(report, args.output)
        summary = {
            "schema": SCHEMA,
            "result": report["result"],
            "passed": report["passed"],
            "report": repo_relative(REPORT),
            "audit_source_sha256": report["audit_source_sha256"],
            "self_test_checks": report["self_test"]["check_count"],
            "inherited_self_test_checks": report["inherited_control_count"],
            "verified_family_count": len(report["families"]),
            "verified_native_library_count": len(report["native_elf_fingerprints"]),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
        return 0
    except (AuditFailure, OSError, ValueError, TypeError, KeyError) as error:
        print(
            json.dumps(
                {"schema": SCHEMA, "passed": False, "result": "FAIL", "error": str(error)},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
