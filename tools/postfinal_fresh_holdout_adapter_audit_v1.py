#!/usr/bin/env python3
"""Independently audit the unopened, four-channel fresh-holdout adapter.

The adversarial self-test is exclusively in memory.  While it is running,
filesystem access, subprocess creation, clocks, production entropy, and guard
operations are actively blocked.  A production audit is a separate, affirmative
operation; it never opens the fresh holdout or starts a candidate worker.
"""

from __future__ import annotations

import ast
import builtins
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCHEMA = "rebar-postfinal-fresh-holdout-adapter-audit-v2"
ADAPTER_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-v1"
ADAPTER_DECLARED_AUDIT_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-audit-v1"
REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V2.json"
)
PRIOR_ADAPTER_AUDIT_REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V1.json"
)
PRIOR_ADAPTER_SMOKE_REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FRESH-HOLDOUT-ADAPTER-SMOKE-V1.json"
)
AUDIT_SOURCE = ROOT / "tools" / "postfinal_fresh_holdout_adapter_audit_v1.py"
ADAPTER_SOURCE = ROOT / "tools" / "postfinal_fresh_holdout_adapter_v1.py"
BOOTSTRAP_SOURCE = ROOT / "tools" / "postfinal_fresh_holdout_bootstrap_v1.c"
GUARD_SOURCE = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
BASE_AUDIT_SOURCE = ROOT / "tools" / "audit_from_scratch.py"
BASE_AUDIT_REPORT = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
STRICT_AUDIT_REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)

PINNED_GUARD_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)
PINNED_BASE_AUDIT_SOURCE_SHA256 = (
    "4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024"
)
PINNED_BASE_AUDIT_REPORT_SHA256 = (
    "c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb"
)
PINNED_STRICT_AUDIT_REPORT_SHA256 = (
    "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b"
)
PINNED_BASE_WORKER_SHA256 = (
    "527c5a5b1c3a717d9786ae04fb8ad738987b10c3a92319d542df574360b84656"
)
PINNED_DERIVED_WORKER_SHA256 = (
    "8bf0774b8f98d89545fd4d5b336c65bdd570812ee84f10da6ae9bc40c9c02590"
)
PINNED_WORKER_EXTENSION_SHA256 = (
    "1c629b89f61d5dc4c73cfb0da4034c5b1081c3d5207a42ae253a0d20a43535e3"
)
PINNED_ADAPTER_SOURCE_SHA256 = (
    "cc29f089344e2ccfb85765689d36938f01ee2e26289c525bafd7aec629cbdba0"
)
PINNED_BOOTSTRAP_SOURCE_SHA256 = (
    "d9950b54c140e4739e3edae09c07a68e588a4bbc5f3680ceb7576941d75fe0a8"
)
PINNED_PRIOR_ADAPTER_AUDIT_REPORT_SHA256 = (
    "d21f61740501a32d6f2b9782c0886e9b47cc28b2452ecdf871de2d42861a5b97"
)
PINNED_PRIOR_ADAPTER_SMOKE_REPORT_SHA256 = (
    "60a2a2666627a412b71381166decbfc97bbffadc704900413f5d8b66cbf6aee1"
)

MODE_ANCHOR = 'if mode not in {"smoke", "persistent"}:'
MODE_REPLACEMENT = (
    'if mode not in {"smoke", "persistent", "fresh_holdout_v1"}:'
)
PREPARE_ANCHOR = "prepared = None\n\n\ndef prepare_case"
DISPATCH_ANCHOR = '            elif operation == "quit":'
CHANNELS = (
    "compiled-pattern-metadata",
    "return-values-match-spans-and-buffer-representation",
    "exception-class-arguments-and-public-pattern-error-fields",
    "documented-converter-callback-warning-and-scanner-traces",
)
LANE_DOMAIN = b"rebar/fresh-holdout/v1/observable-lane\x00"
FRESH_OPERATIONS = (
    "fresh_prepare",
    "fresh_snapshot",
    "fresh_observe",
    "fresh_reveal",
)
NATIVE_FINGERPRINT_KEYS = frozenset(
    {
        "candidates.vm_candidate:native-engine",
        "candidates.rust_candidate:native-engine",
        "candidates.rust_candidate:native-bridge",
        "candidates.zig_candidate:native-engine",
        "candidates.zig_candidate:native-bridge",
    }
)
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_REPORT_BYTES = 16 * 1024 * 1024
MAX_NATIVE_BYTES = 64 * 1024 * 1024
HASH_CHUNK_BYTES = 64 * 1024
EXPECTED_SELF_TEST_CHECKS = 63
OWNED_SOURCE_PATHS = frozenset(
    {
        "candidates/_vm_native.c",
        "candidates/ast_candidate.py",
        "candidates/rust/Cargo.lock",
        "candidates/rust/Cargo.toml",
        "candidates/rust/py_bridge.c",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/newline.rs",
        "candidates/rust/src/search.rs",
        "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
        "candidates/rust_candidate.py",
        "candidates/vm_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
        "candidates/zig_candidate.py",
        "pyproject.toml",
    }
)
OWNED_NATIVE_ARTIFACTS = {
    "candidates.vm_candidate:native-engine": (
        "vm",
        "native",
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    ),
    "candidates.rust_candidate:native-engine": (
        "rust",
        "engine",
        "candidates/_rust_engine.so",
    ),
    "candidates.rust_candidate:native-bridge": (
        "rust",
        "bridge",
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    ),
    "candidates.zig_candidate:native-engine": (
        "zig",
        "engine",
        "candidates/_zig_probe.so",
    ),
    "candidates.zig_candidate:native-bridge": (
        "zig",
        "bridge",
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    ),
}
ALLOWED_C_HEADERS = frozenset(
    {
        "float.h",
        "limits.h",
        "math.h",
        "stdbool.h",
        "stddef.h",
        "stdint.h",
        "stdio.h",
        "stdlib.h",
        "string.h",
    }
)
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "_sre",
        "re",
        "regex",
        "regex_lite",
        "regex_automata",
        "regex_syntax",
        "fancy_regex",
        "re2",
        "pcre",
        "pcre2",
        "onig",
        "oniguruma",
        "onigurumacffi",
        "_onigurumacffi",
        "hyperscan",
        "aho_corasick",
        "sre",
        "sre_compile",
        "sre_parse",
        "sre_constants",
    }
)
FORBIDDEN_C_IDENTIFIERS = frozenset(
    {
        "regcomp",
        "regexec",
        "regerror",
        "regfree",
        "pcre_compile",
        "pcre_exec",
        "pcre2_compile",
        "pcre2_match",
        "onig_new",
        "onig_search",
        "hs_compile",
        "hs_scan",
        "dlopen",
        "dlsym",
        "dlmopen",
        "LoadLibrary",
        "LoadLibraryA",
        "LoadLibraryW",
        "GetProcAddress",
        "PyImport_ImportModule",
        "PyImport_GetModuleDict",
        "PyRun_String",
        "system",
        "popen",
        "fork",
        "vfork",
        "execve",
        "execv",
        "execl",
        "posix_spawn",
        "fopen",
        "freopen",
        "open",
        "openat",
        "creat",
        "socket",
        "connect",
        "mmap",
        "getenv",
        "setenv",
        "putenv",
        "getrandom",
        "getentropy",
        "clock",
        "clock_gettime",
        "gettimeofday",
        "time",
        "production_key",
        "key_hex",
        "token_bytes",
    }
)
GUARD_MARKERS = (
    "sys.addaudithook(guard_hook)",
    "builtins.__import__ = guarded_import",
    "importlib.import_module = guarded_import_module",
    "def verify_registry():",
    "def verify_native_mappings(force_hash=False):",
    'with open("/proc/self/maps", "r", encoding="utf-8") as stream:',
    "def native_stat_identity(value):",
    "blocked_regex_roots = {",
    "def forbidden_native_name(value):",
)


class AdapterAuditError(RuntimeError):
    """An independently checked fresh adapter invariant was not established."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AdapterAuditError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(',', ':'),
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def ensure_candidate_free() -> None:
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
    require(not loaded, f"the independent adapter auditor imported a candidate: {loaded!r}")


def parse_source(source: str, label: str) -> ast.Module:
    require(isinstance(source, str), f"{label} is not source text")
    try:
        encoded = source.encode("utf-8")
    except UnicodeError as error:
        raise AdapterAuditError(f"{label} is not strict UTF-8 source") from error
    require(0 < len(encoded) <= MAX_SOURCE_BYTES, f"{label} exceeds its source bound")
    try:
        return ast.parse(source, filename=label)
    except (SyntaxError, ValueError, RecursionError) as error:
        raise AdapterAuditError(f"{label} is not valid bounded Python source") from error


def literal_assignment(tree: ast.Module, name: str) -> Any:
    matches: list[ast.expr] = []
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in statement.targets):
                matches.append(statement.value)
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.target.id == name
            and statement.value is not None
        ):
            matches.append(statement.value)
    require(len(matches) == 1, f"the immutable literal {name} is missing or duplicated")
    try:
        return ast.literal_eval(matches[0])
    except (TypeError, ValueError, RecursionError) as error:
        raise AdapterAuditError(f"the immutable {name} is not a literal") from error


def function_map(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    result: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for statement in getattr(tree, "body", ()):
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            require(statement.name not in result, f"a public function was duplicated: {statement.name}")
            result[statement.name] = statement
    return result


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return None if parent is None else parent + "." + node.attr
    return None


class PythonPolicy(ast.NodeVisitor):
    """Reject capabilities, not comments or innocent user-visible strings."""

    def __init__(self, *, self_test: bool = False) -> None:
        self.self_test = self_test
        self.issues: list[str] = []

    def reject(self, node: ast.AST, code: str) -> None:
        self.issues.append(f"{code}:{getattr(node, 'lineno', 0)}")

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            root = item.name.partition(".")[0]
            if root in FORBIDDEN_IMPORT_ROOTS or root == "candidates":
                self.reject(node, "forbidden-regex-or-candidate-import")
            if root in {"secrets", "random"}:
                self.reject(node, "production-entropy-import")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").partition(".")[0]
        if root in FORBIDDEN_IMPORT_ROOTS or root == "candidates":
            self.reject(node, "forbidden-regex-or-candidate-import")
        if root in {"secrets", "random"}:
            self.reject(node, "production-entropy-import")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = dotted_name(node.func)
        if name in {
            "__import__",
            "builtins.__import__",
            "importlib.import_module",
            "importlib.__import__",
            "eval",
            "exec",
        }:
            self.reject(node, "dynamic-engine-or-code-loading")
        if name in {
            "secrets.token_bytes",
            "secrets.token_hex",
            "secrets.token_urlsafe",
            "os.urandom",
            "os.getrandom",
            "random.SystemRandom",
            "os.getenv",
            "os.putenv",
            "os.setenv",
        }:
            self.reject(node, "production-key-or-environment-access")
        if name in {"subprocess.Popen", "subprocess.run"}:
            if any(keyword.arg == "env" for keyword in node.keywords):
                self.reject(node, "worker-environment-substitution")
            if self.self_test:
                self.reject(node, "self-test-starts-process")
        if self.self_test and name in {
            "open",
            "builtins.open",
            "os.open",
            "os.pread",
            "os.read",
            "os.write",
            "os.fsync",
            "time.time",
            "time.monotonic",
            "time.perf_counter",
            "time.perf_counter_ns",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
            "subprocess.run",
            "subprocess.Popen",
        }:
            self.reject(node, "self-test-accesses-file-process-or-clock")
        if name in {"open", "builtins.open", "os.open"} and node.args:
            target = node.args[0]
            if isinstance(target, ast.Constant) and isinstance(target.value, str):
                lowered = target.value.casefold().replace("\\", "/")
                if (
                    "/performance/v9/" in lowered
                    or "one-use.guard" in lowered
                    or "private-production-key" in lowered
                    or "freeze-manifest" in lowered
                ):
                    self.reject(node, "restricted-holdout-or-secret-file")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        owner = dotted_name(node.value)
        key = node.slice
        if (
            owner in {"sys.modules", "os.environ"}
            and isinstance(key, ast.Constant)
            and isinstance(key.value, str)
        ):
            root = key.value.partition(".")[0]
            if owner == "os.environ" or root in FORBIDDEN_IMPORT_ROOTS or root == "candidates":
                self.reject(node, "reflective-engine-or-secret-environment")
        self.generic_visit(node)


def policy_issues(source: str, label: str, *, self_test: bool = False) -> list[str]:
    tree = parse_source(source, label)
    visitor = PythonPolicy(self_test=self_test)
    visitor.visit(tree)
    return sorted(set(visitor.issues))


def strip_c_comments(source: str) -> str:
    """Preserve literals and line numbers; reject unterminated C comments."""

    result: list[str] = []
    index = 0
    state = "code"
    while index < len(source):
        current = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if current == "/" and following == "/":
                result.extend((" ", " "))
                index += 2
                state = "line"
                continue
            if current == "/" and following == "*":
                result.extend((" ", " "))
                index += 2
                state = "block"
                continue
            if current in {'"', "'"}:
                state = current
            result.append(current)
        elif state == "line":
            result.append("\n" if current == "\n" else " ")
            if current == "\n":
                state = "code"
        elif state == "block":
            if current == "*" and following == "/":
                result.extend((" ", " "))
                index += 2
                state = "code"
                continue
            result.append("\n" if current == "\n" else " ")
        else:
            result.append(current)
            if current == "\\" and following:
                result.append(following)
                index += 2
                continue
            if current == state:
                state = "code"
        index += 1
    require(state not in {"block", '"', "'"}, "native helper has an unterminated token")
    return "".join(result)


def c_identifiers(source: str) -> set[str]:
    identifiers: set[str] = set()
    index = 0
    while index < len(source):
        mark = source[index]
        if mark in {'"', "'"}:
            quote = mark
            index += 1
            while index < len(source):
                if source[index] == "\\":
                    index += 2
                elif source[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
            continue
        if mark == "_" or mark.isalpha():
            end = index + 1
            while end < len(source) and (source[end] == "_" or source[end].isalnum()):
                end += 1
            identifiers.add(source[index:end])
            index = end
        else:
            index += 1
    return identifiers


def native_policy_issues(source: str) -> list[str]:
    try:
        encoded = source.encode("utf-8")
    except UnicodeError as error:
        raise AdapterAuditError("native helper is not strict UTF-8") from error
    require(0 < len(encoded) <= MAX_SOURCE_BYTES, "native helper exceeds its source bound")
    stripped = strip_c_comments(source)
    issues: set[str] = set()
    for number, line in enumerate(stripped.splitlines(), 1):
        directive = line.strip()
        if not directive.startswith("#"):
            continue
        value = directive[1:].lstrip()
        if value.startswith("include"):
            rest = value[len("include"):].strip()
            if (
                not rest.startswith("<")
                or not rest.endswith(">")
                or rest[1:-1] not in ALLOWED_C_HEADERS
            ):
                issues.add(f"unapproved-native-header:{number}")
    for token in sorted(c_identifiers(stripped) & FORBIDDEN_C_IDENTIFIERS):
        issues.add("forbidden-native-capability:" + token)
    return sorted(issues)


def independently_derive_worker(
    base_source: str,
    adapter_tree: ast.Module,
) -> tuple[str, dict[str, Any]]:
    """Rebuild the complete worker from three audited literal insertions."""

    adapter_mode = literal_assignment(adapter_tree, "MODE_ANCHOR")
    replacement = literal_assignment(adapter_tree, "MODE_REPLACEMENT")
    preparation = literal_assignment(adapter_tree, "PREPARE_ANCHOR")
    dispatch_anchor = literal_assignment(adapter_tree, "DISPATCH_ANCHOR")
    extension = literal_assignment(adapter_tree, "WORKER_EXTENSION")
    dispatch = literal_assignment(adapter_tree, "DISPATCH_EXTENSION")
    require(adapter_mode == MODE_ANCHOR, "the immutable worker mode anchor changed")
    require(replacement == MODE_REPLACEMENT, "the approved fresh worker mode changed")
    require(preparation == PREPARE_ANCHOR, "the immutable preparation anchor changed")
    require(dispatch_anchor == DISPATCH_ANCHOR, "the immutable dispatch anchor changed")
    require(isinstance(extension, str) and extension, "fresh worker extension is not a literal")
    require(isinstance(dispatch, str) and dispatch, "fresh worker dispatch is not a literal")
    anchors = {
        "frozen-worker-mode": base_source.count(MODE_ANCHOR),
        "guarded-fresh-functions": base_source.count(PREPARE_ANCHOR),
        "guarded-fresh-dispatch": base_source.count(DISPATCH_ANCHOR),
    }
    require(all(count == 1 for count in anchors.values()), "a frozen worker insertion anchor is absent or duplicated")
    require("fresh_holdout_v1" not in base_source, "the original worker was already modified")
    require(not policy_issues(extension, "<fresh-worker-extension>"), "fresh worker extension contains a forbidden capability")
    require("base64" not in c_identifiers(extension), "the isolated worker exposes a base64 loader")
    require(
        all(name not in c_identifiers(extension) for name in ("production_key", "key_hex", "expected_sha256", "expected_digest", "result_sha256")),
        "the isolated worker exposes production entropy or a baseline answer",
    )
    extension_tree = parse_source(extension, "<fresh-worker-extension>")
    extension_functions = function_map(extension_tree)
    require(
        {"fresh_prepare", "fresh_snapshot", "fresh_observe", "fresh_channel_snapshots", "fresh_channel_digests", "fresh_error", "fresh_traces", "fresh_wire"}
        <= set(extension_functions),
        "fresh worker omitted an independently reconstructed correctness surface",
    )
    require(literal_assignment(extension_tree, "FRESH_CHANNELS") == CHANNELS, "the worker changed the four public channel names")
    require(literal_assignment(extension_tree, "FRESH_LANE_DOMAIN") == LANE_DOMAIN, "the worker changed its independent lane domain")
    for name in FRESH_OPERATIONS:
        require(dispatch.count('operation == "' + name + '"') == 1, f"fresh dispatch omitted or duplicated {name}")
    require(dispatch.count("fresh_snapshot(candidate, request, reveal=True)") == 1, "fresh reveal does not independently expose exact original channels")
    derived = base_source.replace(MODE_ANCHOR, MODE_REPLACEMENT, 1)
    derived = derived.replace(
        PREPARE_ANCHOR,
        "prepared = None\n" + extension + "\n\ndef prepare_case",
        1,
    )
    derived = derived.replace(DISPATCH_ANCHOR, dispatch + DISPATCH_ANCHOR, 1)
    parse_source(derived, "<independently-derived-fresh-worker>")
    restored = derived.replace(dispatch + DISPATCH_ANCHOR, DISPATCH_ANCHOR, 1)
    restored = restored.replace(
        "prepared = None\n" + extension + "\n\ndef prepare_case",
        PREPARE_ANCHOR,
        1,
    )
    restored = restored.replace(MODE_REPLACEMENT, MODE_ANCHOR, 1)
    require(restored == base_source, "fresh insertion altered immutable original guard bytes")
    for marker in GUARD_MARKERS:
        require(
            base_source.count(marker) == 1 and derived.count(marker) == 1,
            "an immutable import, registry, audit, or native-mapping guard changed",
        )
    return derived, {
        "base_worker_source_sha256": sha256_bytes(base_source.encode("utf-8")),
        "derived_worker_source_sha256": sha256_bytes(derived.encode("utf-8")),
        "worker_extension_sha256": sha256_bytes(extension.encode("utf-8")),
        "worker_dispatch_sha256": sha256_bytes(dispatch.encode("utf-8")),
        "worker_anchor_counts": anchors,
        "unchanged_original_guard_restores_exactly": True,
        "original_guard_marker_count": len(GUARD_MARKERS),
        "private_wire_format": "canonical-ascii-json-utf8",
        "descriptor_wire": "bounded-text-or-hex; no key or reference answer",
    }


def independent_lane_digests(channels: Mapping[str, Any]) -> dict[str, str]:
    require(isinstance(channels, Mapping), "observable channels are not a mapping")
    require(set(channels) == set(CHANNELS), "observable correctness requires exactly four distinct channels")
    return {
        name: sha256_bytes(
            LANE_DOMAIN + name.encode("ascii") + b"\x00" + canonical(channels[name])
        )
        for name in CHANNELS
    }


class BlockSelfTestEffects:
    """Fail closed on I/O, worker launch, clock sampling, or entropy."""

    def __init__(self) -> None:
        self.counts = {"files": 0, "processes": 0, "clocks": 0, "entropy": 0}
        self.originals: list[tuple[Any, str, Any]] = []

    def _block(self, owner: Any, attribute: str, kind: str) -> None:
        if not hasattr(owner, attribute):
            return
        original = getattr(owner, attribute)

        def denied(*_args: Any, **_kwargs: Any) -> Any:
            self.counts[kind] += 1
            raise AdapterAuditError("synthetic adapter audit attempted forbidden " + kind)

        setattr(owner, attribute, denied)
        self.originals.append((owner, attribute, original))

    def __enter__(self) -> BlockSelfTestEffects:
        for owner, name, kind in (
            (builtins, "open", "files"),
            (os, "open", "files"),
            (os, "pread", "files"),
            (os, "read", "files"),
            (os, "write", "files"),
            (os, "fsync", "files"),
            (Path, "open", "files"),
            (Path, "read_text", "files"),
            (Path, "read_bytes", "files"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (subprocess, "call", "processes"),
            (subprocess, "check_call", "processes"),
            (subprocess, "check_output", "processes"),
            (time, "time", "clocks"),
            (time, "monotonic", "clocks"),
            (time, "perf_counter", "clocks"),
            (time, "perf_counter_ns", "clocks"),
            (secrets, "token_bytes", "entropy"),
            (secrets, "token_hex", "entropy"),
            (os, "urandom", "entropy"),
        ):
            self._block(owner, name, kind)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        while self.originals:
            owner, attribute, original = self.originals.pop()
            setattr(owner, attribute, original)


def self_test() -> dict[str, Any]:
    """Exercise named source and lane poisons without touching the disk."""

    ensure_candidate_free()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (AdapterAuditError, TypeError, ValueError, UnicodeError, RecursionError):
            check(name, True)
        else:
            check(name, False)

    effects = BlockSelfTestEffects()
    with effects:
        check("four-distinct-public-channel-names", len(CHANNELS) == 4 and len(set(CHANNELS)) == 4)
        check("exact-65536-prospective-cases", 16 * 16 * 256 == 65_536)
        check("exact-4980736-raw-observations", 65_536 * 19 * 4 == 4_980_736)
        check("exact-14942208-independent-gates", 65_536 * 19 * 3 * 4 == 14_942_208)
        check("exact-196611-paired-intervals", 65_536 * 3 + 3 == 196_611)
        check("exactly-five-independent-native-fingerprint-roles", len(NATIVE_FINGERPRINT_KEYS) == 5)
        canonical_fixture = {"emoji": "\U0001f9ea", "high": "\ud800", "low": "\udfff", "newline": "a\nb"}
        encoded = canonical(canonical_fixture)
        check("surrogate-safe-ascii-wire", encoded.isascii() and json.loads(encoded) == canonical_fixture)
        check("canonical-sorted-wire", canonical({"b": 2, "a": 1}) == b'{"a":1,"b":2}')
        for name, value in (("nan", float("nan")), ("positive-infinity", float("inf")), ("negative-infinity", -float("inf"))):
            rejected("reject-nonfinite-wire:" + name, lambda item=value: canonical({"value": item}))
        lanes = {
            CHANNELS[0]: {"pattern": "(?P<a>a)", "flags": 32, "groups": 1},
            CHANNELS[1]: {"span": [0, 1], "captures": ["a"], "buffer": {"kind": "bytes", "hex": "61"}},
            CHANNELS[2]: {"class": "ValueError", "args": ["sentinel"], "cause": {"class": "TypeError", "args": ["nested"]}},
            CHANNELS[3]: {"converter": ["__index__"], "callback": ["a", "b"], "warnings": ["FutureWarning"], "scanner": ["match", None]},
        }
        original_digests = independent_lane_digests(lanes)
        check("four-distinct-labeled-lane-digests", len(set(original_digests.values())) == 4)
        check("deterministic-lane-digests", independent_lane_digests(lanes) == original_digests)
        for index, lane in enumerate(CHANNELS):
            altered = dict(lanes)
            altered[lane] = {"changed": index, "original": lanes[lane]}
            difference = independent_lane_digests(altered)
            check(
                "single-independent-lane-mutation:" + lane,
                difference[lane] != original_digests[lane]
                and all(difference[name] == original_digests[name] for name in CHANNELS if name != lane),
            )
        rejected("reject-missing-correctness-lane", lambda: independent_lane_digests(dict(list(lanes.items())[:-1])))
        rejected("reject-foreign-correctness-lane", lambda: independent_lane_digests({**lanes, "foreign": {}}))
        rejected("reject-nonmapping-correctness-lanes", lambda: independent_lane_digests(list(lanes.items())))
        swapped = dict(lanes)
        swapped[CHANNELS[0]], swapped[CHANNELS[1]] = swapped[CHANNELS[1]], swapped[CHANNELS[0]]
        changed = independent_lane_digests(swapped)
        check("reject-interchanged-channel-labels", changed[CHANNELS[0]] != original_digests[CHANNELS[0]] and changed[CHANNELS[1]] != original_digests[CHANNELS[1]])
        for name, fixture in (
            ("stdlib-regex-import", "import re\n"),
            ("cpython-sre-import", "import _sre\n"),
            ("foreign-regex-import", "from regex import compile\n"),
            ("cross-candidate-import", "from candidates import vm_candidate\n"),
            ("computed-import", "__import__('re')\n"),
            ("importlib-engine-loading", "import importlib\nimportlib.import_module('re')\n"),
            ("reflective-regex-registry", "import sys\nsys.modules['re']\n"),
            ("production-entropy-import", "import secrets\n"),
            ("production-key-draw", "import os\nos.urandom(32)\n"),
            ("secret-environment-read", "import os\nos.environ['PRODUCTION_KEY']\n"),
            ("worker-environment-injection", "import subprocess\nsubprocess.Popen(['x'], env={})\n"),
            ("guard-file-access", "open('.FRESH-HOLDOUT-V1.one-use.guard')\n"),
            ("historical-holdout-access", "open('/performance/v9/hidden.json')\n"),
            ("private-key-file-access", "open('private-production-key')\n"),
            ("dynamic-eval-fallback", "eval('candidate.search(pattern, subject)')\n"),
            ("dynamic-exec-fallback", "exec('import re')\n"),
        ):
            check("reject:" + name, bool(policy_issues(fixture, "<synthetic:" + name + ">")))
        for name, fixture in (
            ("clock", "import time\ntime.perf_counter_ns()\n"),
            ("subprocess", "import subprocess\nsubprocess.Popen(['x'])\n"),
            ("file-read", "open('public.txt')\n"),
            ("guard-pread", "import os\nos.pread(3, 32, 0)\n"),
        ):
            check("reject-self-test:" + name, bool(policy_issues(fixture, "<synthetic-self-test>", self_test=True)))
        benign = "import hashlib\nimport json\nvalue = hashlib.sha256(json.dumps({'a': 1}).encode()).hexdigest()\n"
        check("allow-independent-hash-and-json", not policy_issues(benign, "<benign>"))
        c_fixture = "#include <stdint.h>\n#include <stdio.h>\nint main(void) { return 0; }\n"
        check("allow-bounded-native-standard-headers", not native_policy_issues(c_fixture))
        for name, source in (
            ("foreign-regex-header", "#include <regex.h>\n"),
            ("dynamic-loader-header", "#include <dlfcn.h>\n"),
            ("computed-native-header", "#include FOREIGN_ENGINE\n"),
            ("native-regex-delegation", "int f(void) { return regexec(0,0,0,0,0); }\n"),
            ("native-dynamic-library", "void f(void) { dlopen(0, 0); }\n"),
            ("native-process", "void f(void) { system(0); }\n"),
            ("native-filesystem", "void f(void) { fopen(0, 0); }\n"),
            ("native-clock", "void f(void) { clock_gettime(0, 0); }\n"),
            ("native-production-entropy", "void f(void) { getrandom(0, 0, 0); }\n"),
            ("native-environment", "void f(void) { getenv(0); }\n"),
        ):
            check("reject:" + name, bool(native_policy_issues(source)))
        check(
            "ignore-commented-native-poison",
            not native_policy_issues(c_fixture + "/* dlopen(); regexec(); */\n// fopen()\n"),
        )
        rejected("reject-unterminated-native-comment", lambda: native_policy_issues("int x; /*"))
        duplicate = "VALUE = 1\nVALUE = 2\n"
        rejected("reject-duplicate-frozen-literal", lambda: literal_assignment(parse_source(duplicate, "<duplicate>"), "VALUE"))
        rejected("reject-computed-frozen-literal", lambda: literal_assignment(parse_source("VALUE = 'a' + 'b'\n", "<computed>"), "VALUE"))
        rejected("reject-missing-frozen-literal", lambda: literal_assignment(parse_source("OTHER = 1\n", "<missing>"), "VALUE"))
        ensure_candidate_free()
        check("candidate-free-throughout-synthetic-controls", True)

    check("zero-synthetic-file-access", effects.counts["files"] == 0)
    check("zero-synthetic-subprocesses", effects.counts["processes"] == 0)
    check("zero-synthetic-clock-samples", effects.counts["clocks"] == 0)
    check("zero-synthetic-production-entropy", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(checks) != EXPECTED_SELF_TEST_CHECKS:
        failed.append("synthetic-control-count-changed")
    if len(names) != len(set(names)):
        failed.append("duplicate-synthetic-control-name")
    ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "fixture_storage": "in-memory only",
        "candidate_imported": False,
        "candidate_imports": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "file_reads": effects.counts["files"],
        "file_writes": 0,
        "production_entropy_drawn": False,
        "guard_created": False,
        "guard_read": False,
        "production_cases_materialized": 0,
        "holdout_or_case_fixture_access": False,
        "historical_holdout_accessed": False,
        "benchmark_or_timing_executed": False,
    }


def read_authorized_source(
    path: Path,
    *,
    expected_sha256: str | None,
    label: str,
) -> str:
    require(not path.is_symlink(), f"{label} cannot be a symbolic link")
    require(path.parent.resolve() == (ROOT / "tools").resolve(), f"{label} escaped the owned tools directory")
    try:
        with path.open("rb") as stream:
            value = stream.read(MAX_SOURCE_BYTES + 1)
    except OSError as error:
        raise AdapterAuditError(f"{label} could not be independently read") from error
    require(0 < len(value) <= MAX_SOURCE_BYTES, f"{label} exceeds its source bound")
    if expected_sha256 is not None:
        require(
            sha256_bytes(value) == expected_sha256,
            f"{label} does not match its frozen exact SHA-256",
        )
    try:
        return value.decode("utf-8")
    except UnicodeError as error:
        raise AdapterAuditError(f"{label} is not strict UTF-8") from error


def stream_owned_file(
    path: Path,
    *,
    maximum: int,
    label: str,
    capture: bool = False,
) -> tuple[str, int, bytes]:
    """Hash one explicitly selected owned regular file in 64 KiB chunks."""

    require(isinstance(path, Path), f"{label} is not an explicitly selected path")
    require(not path.is_symlink(), f"{label} cannot be a symbolic link")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(ROOT.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as error:
        raise AdapterAuditError(f"{label} escaped the owned public repository") from error
    digest = hashlib.sha256()
    length = 0
    prefix = bytearray()
    retained = bytearray() if capture else None
    try:
        with resolved.open("rb") as stream:
            before = os.fstat(stream.fileno())
            require(stat.S_ISREG(before.st_mode), f"{label} is not a regular file")
            identity = (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            while True:
                block = stream.read(HASH_CHUNK_BYTES)
                if not block:
                    break
                length += len(block)
                require(length <= maximum, f"{label} exceeds its finite byte bound")
                digest.update(block)
                if len(prefix) < 16:
                    prefix.extend(block[: 16 - len(prefix)])
                if retained is not None:
                    retained.extend(block)
            after = os.fstat(stream.fileno())
            require(
                identity
                == (
                    after.st_dev,
                    after.st_ino,
                    after.st_size,
                    after.st_mtime_ns,
                    after.st_ctime_ns,
                ),
                f"{label} changed during bounded verification",
            )
        final = os.stat(resolved, follow_symlinks=False)
    except OSError as error:
        raise AdapterAuditError(f"{label} cannot be independently streamed") from error
    require(
        identity
        == (
            final.st_dev,
            final.st_ino,
            final.st_size,
            final.st_mtime_ns,
            final.st_ctime_ns,
        )
        and length == before.st_size
        and length > 0,
        f"{label} changed after bounded verification",
    )
    return digest.hexdigest(), length, bytes(retained if retained is not None else prefix)


def load_public_audit(
    path: Path,
    *,
    expected_sha256: str,
    label: str,
) -> dict[str, Any]:
    digest, _length, payload = stream_owned_file(
        path,
        maximum=256 * 1024,
        label=label,
        capture=True,
    )
    require(digest == expected_sha256, f"{label} does not match its frozen public SHA-256")
    try:
        value = json.loads(payload)
    except (TypeError, UnicodeError, ValueError) as error:
        raise AdapterAuditError(f"{label} is not a valid bounded JSON proof") from error
    require(isinstance(value, dict), f"{label} is not a JSON object")
    return value


def verify_public_controls(
    value: Any,
    *,
    count: int,
    label: str,
) -> None:
    require(isinstance(value, dict), f"{label} omitted its synthetic controls")
    checks = value.get("checks")
    require(
        value.get("passed") is True
        and value.get("check_count") == count
        and value.get("failed") == []
        and isinstance(checks, list)
        and len(checks) == count
        and all(
            isinstance(check, dict)
            and isinstance(check.get("name"), str)
            and check.get("passed") is True
            for check in checks
        )
        and len({check["name"] for check in checks}) == count,
        f"{label} did not pass every separately named control",
    )


def verify_original_families(
    base: Mapping[str, Any],
    strict: Mapping[str, Any],
    source_hashes: Mapping[str, str],
) -> None:
    original_families = base.get("families")
    strict_families = strict.get("families")
    require(
        isinstance(original_families, dict)
        and isinstance(strict_families, dict)
        and set(original_families) == {"ast", "rust", "vm", "zig"}
        and set(strict_families) == set(original_families),
        "the independent public audits omitted an owned engine family",
    )
    graph: set[str] = set()
    for name in sorted(original_families):
        family = original_families[name]
        strict_family = strict_families[name]
        require(
            isinstance(family, dict)
            and family.get("passed") is True
            and isinstance(strict_family, dict)
            and strict_family.get("passed") is True,
            f"an original or strict owned family did not pass: {name}",
        )
        pipeline = family.get("owned_pipeline")
        require(
            isinstance(pipeline, dict)
            and pipeline.get("passed") is True
            and pipeline.get("issues") == [],
            f"the original public audit omitted an independent {name} pipeline",
        )
        python = family.get("python_source")
        require(
            isinstance(python, dict)
            and python.get("passed") is True
            and isinstance(python.get("file"), str)
            and python.get("sha256") == source_hashes.get(python["file"])
            and python.get("issues") == [],
            f"the original public {name} Python source changed",
        )
        graph.add(python["file"])
        records = family.get("native_sources")
        require(isinstance(records, list), f"the original {name} native sources are not explicit")
        for record in records:
            require(
                isinstance(record, dict)
                and record.get("passed") is True
                and isinstance(record.get("file"), str)
                and record.get("sha256") == source_hashes.get(record["file"])
                and record.get("issues") == [],
                f"the original public {name} native source changed",
            )
            graph.add(record["file"])
    require(
        graph
        == OWNED_SOURCE_PATHS
        - {"candidates/rust/Cargo.lock", "candidates/rust/Cargo.toml", "pyproject.toml"},
        "the independently owned source graph is incomplete",
    )


def native_fingerprints() -> tuple[dict[str, str], dict[str, Any]]:
    """Directly rehash two frozen proofs, 16 sources, and five owned ELFs."""

    ensure_candidate_free()
    base = load_public_audit(
        BASE_AUDIT_REPORT,
        expected_sha256=PINNED_BASE_AUDIT_REPORT_SHA256,
        label="original 76-control public audit",
    )
    strict = load_public_audit(
        STRICT_AUDIT_REPORT,
        expected_sha256=PINNED_STRICT_AUDIT_REPORT_SHA256,
        label="strict 32-control public no-delegation audit",
    )
    require(
        base.get("schema_version") == 1
        and base.get("audit") == "bounded-from-scratch-engine-provenance"
        and base.get("result") == "PASS"
        and base.get("passed") is True
        and base.get("verified_core_family_count") == 3
        and base.get("verified_distinct_pipeline_count") == 4,
        "the original public from-scratch engine audit is not an exact PASS",
    )
    verify_public_controls(base.get("self_test"), count=76, label="original public audit")
    require(
        strict.get("schema") == "rebar-postfinal-no-delegation-audit-v1"
        and strict.get("result") == "PASS"
        and strict.get("passed") is True
        and strict.get("audit_source_path")
        == "tools/postfinal_no_delegation_audit_v1.py"
        and strict.get("audit_source_sha256") == PINNED_GUARD_SOURCE_SHA256
        and strict.get("base_audit_report_path")
        == "candidates/audits/FROM-SCRATCH-AUDIT.json"
        and strict.get("base_audit_report_sha256")
        == PINNED_BASE_AUDIT_REPORT_SHA256
        and strict.get("base_audit_source_path") == "tools/audit_from_scratch.py"
        and strict.get("base_audit_source_sha256")
        == PINNED_BASE_AUDIT_SOURCE_SHA256
        and strict.get("inherited_control_count") == 76,
        "the strict public no-delegation proof lost its original source bindings",
    )
    verify_public_controls(strict.get("self_test"), count=32, label="strict public audit")
    verify_public_controls(
        strict.get("inherited_self_test"),
        count=76,
        label="strict audit inherited original controls",
    )
    require(
        strict.get("inherited_self_test") == base.get("self_test"),
        "the strict audit changed the exact original 76 poison controls",
    )
    for proof, label in ((base, "original"), (strict, "strict")):
        scope = proof.get("scope")
        require(
            isinstance(scope, dict)
            and scope.get("explicit_source_paths_only") is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            f"the {label} public proof weakened its candidate or holdout scope",
        )
    require(
        strict["scope"].get("closed_owned_source_graph") is True
        and strict["scope"].get("persistent_measurement_worker_available") is True,
        "the strict public audit omitted its closed, independently guarded source graph",
    )
    base_source_digest, _base_source_length, _base_source_prefix = stream_owned_file(
        BASE_AUDIT_SOURCE,
        maximum=MAX_SOURCE_BYTES,
        label="original 76-control audit source",
    )
    strict_source_digest, _strict_source_length, _strict_source_prefix = stream_owned_file(
        GUARD_SOURCE,
        maximum=MAX_SOURCE_BYTES,
        label="strict 32-control guard audit source",
    )
    require(
        base_source_digest == PINNED_BASE_AUDIT_SOURCE_SHA256
        and strict_source_digest == PINNED_GUARD_SOURCE_SHA256,
        "an independently source-bound public audit changed",
    )
    source_hashes = strict.get("source_fingerprints")
    require(
        isinstance(source_hashes, dict)
        and set(source_hashes) == OWNED_SOURCE_PATHS,
        "the strict public audit changed its exact 16-file closed source graph",
    )
    for relative in sorted(OWNED_SOURCE_PATHS):
        expected = source_hashes[relative]
        require(
            isinstance(expected, str)
            and len(expected) == 64
            and all(mark in "0123456789abcdef" for mark in expected),
            f"an owned public source has an invalid digest: {relative}",
        )
        actual, _length, _prefix = stream_owned_file(
            ROOT / relative,
            maximum=MAX_SOURCE_BYTES,
            label="explicit owned public source " + relative,
        )
        require(actual == expected, f"an independently owned public source changed: {relative}")
    verify_original_families(base, strict, source_hashes)
    original_native = base.get("native_elf_provenance")
    strict_native = strict.get("native_elf_provenance")
    require(
        isinstance(original_native, dict)
        and original_native == strict_native
        and original_native.get("passed") is True
        and original_native.get("audited_binary_count") == 5
        and original_native.get("expected_binary_count") == 5
        and original_native.get("issues") == [],
        "the original and strict public proofs disagree about five owned native ELFs",
    )
    families = original_native.get("families")
    require(
        isinstance(families, dict) and set(families) == {"rust", "vm", "zig"},
        "public ELF provenance omitted an independent native owner",
    )
    native = strict.get("native_elf_fingerprints")
    require(
        isinstance(native, dict)
        and set(native) == NATIVE_FINGERPRINT_KEYS
        and set(OWNED_NATIVE_ARTIFACTS) == NATIVE_FINGERPRINT_KEYS,
        "the strict proof changed its exact five owned native roles",
    )
    for key, (family, role, relative) in sorted(OWNED_NATIVE_ARTIFACTS.items()):
        expected = native[key]
        require(
            isinstance(expected, str)
            and len(expected) == 64
            and all(mark in "0123456789abcdef" for mark in expected),
            f"the frozen native SHA-256 is invalid: {key}",
        )
        owner = families.get(family)
        require(
            isinstance(owner, dict)
            and owner.get("passed") is True
            and owner.get("issues") == []
            and isinstance(owner.get("files"), dict),
            f"the independently guarded native family is invalid: {family}",
        )
        record = owner["files"].get(role)
        require(
            isinstance(record, dict)
            and record.get("file") == relative
            and record.get("sha256") == expected
            and record.get("elf_class") == 64
            and record.get("forbidden_regex_symbols") == []
            and record.get("cross_candidate_symbols") == [],
            f"the independently guarded native role was substituted: {key}",
        )
        actual, _native_length, magic = stream_owned_file(
            ROOT / relative,
            maximum=MAX_NATIVE_BYTES,
            label="actual independently owned native ELF " + relative,
        )
        require(
            actual == expected and len(magic) >= 6 and magic[:5] == b"\x7fELF\x02",
            f"an actual independently owned 64-bit native ELF changed: {relative}",
        )
    mapping = base.get("runtime_native_mapping_provenance")
    require(
        isinstance(mapping, dict) and mapping.get("passed") is True,
        "the original proof omitted its isolated actual native mapping evidence",
    )
    ensure_candidate_free()
    return dict(native), {
        "passed": True,
        "audited_binary_count": 5,
        "expected_binary_count": 5,
        "verification": "current independently verified 76-control and 32-control public audits",
        "base_audit_report_sha256": PINNED_BASE_AUDIT_REPORT_SHA256,
        "postfinal_no_delegation_audit_path": str(STRICT_AUDIT_REPORT.resolve()),
        "postfinal_no_delegation_audit_sha256": PINNED_STRICT_AUDIT_REPORT_SHA256,
        "postfinal_no_delegation_audit_source_sha256": PINNED_GUARD_SOURCE_SHA256,
        "postfinal_no_delegation_control_count": 32,
        "inherited_control_count": 76,
        "closed_owned_source_count": len(OWNED_SOURCE_PATHS),
        "actual_native_elf_count": len(OWNED_NATIVE_ARTIFACTS),
        "hash_chunk_bytes": HASH_CHUNK_BYTES,
        "public_benchmark_runner_imported": False,
    }


def audit() -> dict[str, Any]:
    """Audit only exact public sources; never open or execute the holdout."""

    ensure_candidate_free()
    controls = self_test()
    require(controls["passed"] is True, "an independent synthetic adapter poison control failed")
    guard_source = read_authorized_source(
        GUARD_SOURCE,
        expected_sha256=PINNED_GUARD_SOURCE_SHA256,
        label="original 32-control guarded-worker audit",
    )
    adapter_source = read_authorized_source(
        ADAPTER_SOURCE,
        expected_sha256=PINNED_ADAPTER_SOURCE_SHA256,
        label="fresh four-channel adapter",
    )
    bootstrap_source = read_authorized_source(
        BOOTSTRAP_SOURCE,
        expected_sha256=PINNED_BOOTSTRAP_SOURCE_SHA256,
        label="dependency-free native paired-bootstrap helper",
    )
    guard_tree = parse_source(guard_source, "tools/postfinal_no_delegation_audit_v1.py")
    adapter_tree = parse_source(adapter_source, "tools/postfinal_fresh_holdout_adapter_v1.py")
    require(not policy_issues(adapter_source, "<fresh-adapter>"), "fresh adapter contains a forbidden regex, key, or environment capability")
    bootstrap_issues = native_policy_issues(bootstrap_source)
    require(not bootstrap_issues, f"native bootstrap exposes a forbidden capability: {bootstrap_issues!r}")
    require(literal_assignment(adapter_tree, "ADAPTER_SCHEMA") == ADAPTER_SCHEMA, "the fresh adapter schema changed")
    require(
        literal_assignment(adapter_tree, "AUDIT_SCHEMA")
        == ADAPTER_DECLARED_AUDIT_SCHEMA,
        "the immutable fresh adapter changed its original declared audit schema",
    )
    require(literal_assignment(adapter_tree, "WORKER_MODE") == "fresh_holdout_v1", "the isolated fresh worker mode changed")
    require(literal_assignment(adapter_tree, "CHANNELS") == CHANNELS, "the adapter changed its four independent public channel names")
    require(literal_assignment(adapter_tree, "LANE_DOMAIN") == LANE_DOMAIN, "the adapter changed its four-lane hash domain")
    require(literal_assignment(adapter_tree, "GUARDED_AUDIT_SOURCE_SHA256") == PINNED_GUARD_SOURCE_SHA256, "adapter does not pin the independent original guard source")
    base_source = literal_assignment(guard_tree, "GUARDED_WORKER_SOURCE")
    require(isinstance(base_source, str), "the exact original guarded worker is not a literal")
    require(sha256_bytes(base_source.encode("utf-8")) == PINNED_BASE_WORKER_SHA256, "the immutable original guarded worker source was substituted")
    derived, worker = independently_derive_worker(base_source, adapter_tree)
    require(worker["derived_worker_source_sha256"] == PINNED_DERIVED_WORKER_SHA256, "the independently reconstructed four-channel worker changed")
    require(worker["worker_extension_sha256"] == PINNED_WORKER_EXTENSION_SHA256, "the audited four-channel worker extension changed")
    require(sha256_bytes(derived.encode("utf-8")) == PINNED_DERIVED_WORKER_SHA256, "the complete derived worker SHA-256 is inconsistent")
    adapter_functions = function_map(adapter_tree)
    require(
        {"canonical", "normalize", "lane_digests", "derive_guarded_worker_source", "guarded_holdout_worker_command", "candidate_free_self_test", "main"}
        <= set(adapter_functions),
        "the four-channel adapter omitted a required bounded public operation",
    )
    classes = {
        statement.name
        for statement in adapter_tree.body
        if isinstance(statement, ast.ClassDef)
    }
    require(
        {"HoldoutAdapterError", "PersistentFreshHoldoutWorker", "CaseTrialBuffer", "BootstrapStream"}
        <= classes,
        "the adapter omitted isolated-worker or bounded paired-bootstrap ownership",
    )
    native, provenance = native_fingerprints()
    prior_audit_sha256, _prior_audit_bytes, _prior_audit_prefix = stream_owned_file(
        PRIOR_ADAPTER_AUDIT_REPORT,
        maximum=MAX_REPORT_BYTES,
        label="immutable original V1 adapter audit evidence",
    )
    prior_smoke_sha256, _prior_smoke_bytes, _prior_smoke_prefix = stream_owned_file(
        PRIOR_ADAPTER_SMOKE_REPORT,
        maximum=MAX_REPORT_BYTES,
        label="immutable original V1 adapter smoke evidence",
    )
    require(
        prior_audit_sha256 == PINNED_PRIOR_ADAPTER_AUDIT_REPORT_SHA256
        and prior_smoke_sha256 == PINNED_PRIOR_ADAPTER_SMOKE_REPORT_SHA256,
        "the additive V2 audit cannot supersede altered original V1 evidence",
    )
    audit_source = read_authorized_source(
        AUDIT_SOURCE,
        expected_sha256=None,
        label="independent fresh adapter audit",
    )
    audit_digest = sha256_bytes(audit_source.encode("utf-8"))
    ensure_candidate_free()
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": "tools/postfinal_fresh_holdout_adapter_audit_v1.py",
        "audit_source_sha256": audit_digest,
        "adapter_source_path": "tools/postfinal_fresh_holdout_adapter_v1.py",
        "adapter_source_sha256": PINNED_ADAPTER_SOURCE_SHA256,
        "adapter_declared_audit_schema": ADAPTER_DECLARED_AUDIT_SCHEMA,
        "bootstrap_source_path": "tools/postfinal_fresh_holdout_bootstrap_v1.c",
        "bootstrap_source_sha256": PINNED_BOOTSTRAP_SOURCE_SHA256,
        "guard_source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "guard_source_sha256": PINNED_GUARD_SOURCE_SHA256,
        **worker,
        "channel_names": list(CHANNELS),
        "correctness_channel_count": len(CHANNELS),
        "candidate_families": ["rust", "vm", "zig"],
        "isolated_families": ["re", "rust", "vm", "zig"],
        "case_count": 65_536,
        "paired_trials": 19,
        "raw_observations": 4_980_736,
        "correctness_gates": 14_942_208,
        "confidence_intervals": 196_611,
        "bootstrap_samples_per_interval": 2_000,
        "native_elf_fingerprints": native,
        "native_elf_provenance": provenance,
        "inherited_control_count": 76,
        "original_no_delegation_control_count": 32,
        "self_test": controls,
        "supersedes": {
            "adapter_audit_report_path": (
                "candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V1.json"
            ),
            "adapter_audit_report_sha256": prior_audit_sha256,
            "adapter_smoke_report_path": (
                "candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-SMOKE-V1.json"
            ),
            "adapter_smoke_report_sha256": prior_smoke_sha256,
            "original_reports_preserved": True,
        },
        "scope": {
            "explicit_source_paths_only": True,
            "independent_ast_literal_worker_derivation": True,
            "original_guard_restores_byte_for_byte": True,
            "exactly_four_separately_labeled_public_channels": True,
            "candidate_imported": False,
            "candidate_workers_started": 0,
            "native_bootstrap_started": False,
            "production_entropy_drawn": False,
            "guard_created": False,
            "guard_read": False,
            "production_cases_materialized": 0,
            "holdout_or_case_fixture_access": False,
            "historical_holdout_accessed": False,
            "benchmark_or_timing_executed": False,
        },
        "candidate_imported": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "historical_holdout_accessed": False,
        "production_cases_materialized": 0,
    }


def write_report(report: Mapping[str, Any], target: Path) -> None:
    require(target.name == REPORT.name, "the adapter audit report filename was substituted")
    require(target.parent.resolve() == REPORT.parent.resolve(), "the adapter audit report escaped its exact authorized directory")
    require(not target.is_symlink(), "the adapter audit report cannot be a symbolic link")
    payload = canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the adapter audit report exceeds its bounded size")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(target, flags, 0o644)
    except OSError as error:
        raise AdapterAuditError("refusing to replace an existing independent adapter audit report") from error
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            require(written > 0, "independent adapter audit report write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main(arguments: list[str] | None = None) -> int:
    selected = list(sys.argv[1:] if arguments is None else arguments)
    try:
        if selected in (["-h"], ["--help"]):
            sys.stdout.write(
                "usage: postfinal_fresh_holdout_adapter_audit_v1.py "
                "--self-test | --validate | --audit [--output AUTHORIZED_REPORT]\n"
            )
            return 0
        if selected == ["--self-test"]:
            report = self_test()
            sys.stdout.buffer.write(canonical(report) + b"\n")
            return 0 if report["passed"] else 1
        if selected == ["--validate"]:
            report = audit()
            sys.stdout.buffer.write(
                canonical(
                    {
                        "schema": SCHEMA + "-validation",
                        "status": "PASS",
                        "result": "PASS",
                        "passed": True,
                        "validation_only": True,
                        "report_written": False,
                        "audit_source_sha256": report["audit_source_sha256"],
                        "adapter_source_sha256": report["adapter_source_sha256"],
                        "adapter_declared_audit_schema": report[
                            "adapter_declared_audit_schema"
                        ],
                        "bootstrap_source_sha256": report["bootstrap_source_sha256"],
                        "derived_worker_source_sha256": report["derived_worker_source_sha256"],
                        "self_test_checks": report["self_test"]["check_count"],
                        "verified_native_library_count": len(report["native_elf_fingerprints"]),
                        "verified_owned_source_count": report["native_elf_provenance"]["closed_owned_source_count"],
                        "public_benchmark_runner_imported": False,
                        "candidate_imported": False,
                        "candidate_workers_started": 0,
                        "benchmark_or_timing_executed": False,
                        "holdout_or_case_fixture_access": False,
                        "production_cases_materialized": 0,
                    }
                )
                + b"\n"
            )
            return 0
        require(
            selected == ["--audit"]
            or (len(selected) == 3 and selected[:2] == ["--audit", "--output"]),
            "select exactly --self-test or --audit [--output AUTHORIZED_REPORT]",
        )
        output = REPORT if len(selected) == 1 else Path(selected[2])
        report = audit()
        write_report(report, output)
        sys.stdout.buffer.write(
            canonical(
                {
                    "schema": SCHEMA,
                    "status": "PASS",
                    "result": "PASS",
                    "passed": True,
                    "report": (
                        "candidates/audits/"
                        "POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V2.json"
                    ),
                    "audit_source_sha256": report["audit_source_sha256"],
                    "adapter_source_sha256": report["adapter_source_sha256"],
                    "adapter_declared_audit_schema": report[
                        "adapter_declared_audit_schema"
                    ],
                    "bootstrap_source_sha256": report["bootstrap_source_sha256"],
                    "derived_worker_source_sha256": report["derived_worker_source_sha256"],
                    "self_test_checks": report["self_test"]["check_count"],
                    "verified_native_library_count": len(report["native_elf_fingerprints"]),
                    "correctness_channel_count": report["correctness_channel_count"],
                    "benchmark_or_timing_executed": False,
                    "holdout_or_case_fixture_access": False,
                    "production_cases_materialized": 0,
                }
            )
            + b"\n"
        )
        return 0
    except (
        AdapterAuditError,
        OSError,
        TypeError,
        ValueError,
        UnicodeError,
        subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(
            canonical(
                {
                    "schema": SCHEMA,
                    "status": "FAIL",
                    "result": "FAIL",
                    "passed": False,
                    "error": str(error),
                    "candidate_imported": False,
                    "historical_holdout_accessed": False,
                    "benchmark_or_timing_executed": False,
                }
            )
            + b"\n"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
