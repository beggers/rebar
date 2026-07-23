#!/usr/bin/env python3
"""Fail-fast, reproducible correctness and safety gate for the Rust candidate."""

from __future__ import annotations

import argparse
import ast
import dataclasses
import hashlib
import json
import math
import os
import platform
import re
import resource
import subprocess
import sys
import time
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
V7_EXPECTED_SHA256 = "2e6c098bd3a4757620461363106a9795f8defa98fe8bc9c13c0ebbf7ed58b598"
PINNED_CPYTHON = (3, 14, 6)
RUST_MODULE = "candidates.rust_candidate"
SEALED_EXCLUDED_STEP_NAMES = (
    "frozen-performance-correctness-v6",
    "frozen-performance-v7-integrity",
    "frozen-performance-correctness-v7",
)
SEALED_REQUIRED_STEP_NAMES = frozenset({
    "rust-source-no-delegation",
    "rust-bridge-no-delegation",
    "rust-native-boundary-integrity",
    "rust-native-boundary-self-oracle",
    "rust-native-boundary-compatibility",
    "frozen-correctness-v2",
    "frozen-correctness-v3",
    "official-cpython-tests",
    "upstream-public-surface",
    "rust-public-surface",
    "unicode-group-name-errors",
    "replacement-and-callback-adversarial",
    "deep-replacement-and-callback-adversarial",
    "extended-cpython-paths",
    "isolated-crash-and-resource-safety",
    "isolated-depth-and-overflow-safety",
    "full-unicode-plane",
})


@dataclasses.dataclass(frozen=True)
class Step:
    name: str
    script: str
    arguments: tuple[str, ...]
    expected_checks: int | None
    timeout_seconds: int
    artifact: str | None = None


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def goal_state():
    goal = ROOT / "GOAL.md"
    if not goal.is_file():
        return {"passed": False, "error": "GOAL.md is missing"}
    actual = sha256(goal)
    return {
        "passed": actual == GOAL_SHA256,
        "expected_sha256": GOAL_SHA256,
        "actual_sha256": actual,
    }


def strip_comments(source):
    source = re.sub(r"/\*.*?\*/", " ", source, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", source)


def static_audit():
    python_path = ROOT / "candidates" / "rust_candidate.py"
    bridge_path = ROOT / "candidates" / "rust" / "py_bridge.c"
    cargo_path = ROOT / "candidates" / "rust" / "Cargo.toml"
    cargo_lock_path = ROOT / "candidates" / "rust" / "Cargo.lock"
    rust_root = ROOT / "candidates" / "rust" / "src"
    issues = []
    inspected = []

    for path in (python_path, bridge_path, cargo_path, cargo_lock_path):
        if not path.is_file():
            issues.append({"file": str(path.relative_to(ROOT)), "reason": "required production file missing"})

    if python_path.is_file():
        inspected.append(str(python_path.relative_to(ROOT)))
        source = python_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(python_path))
        except SyntaxError as error:
            issues.append({"file": str(python_path.relative_to(ROOT)), "reason": f"invalid Python source: {error}"})
        else:
            blocked = {"re", "_sre", "sre_parse", "sre_compile", "regex", "re2", "pcre", "pcre2", "onig", "hyperscan", "ctypes", "cffi"}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name.partition(".")[0] in blocked:
                            issues.append({"file": str(python_path.relative_to(ROOT)), "line": node.lineno,
                                           "reason": "production import is forbidden", "import": name.name})
                elif isinstance(node, ast.ImportFrom):
                    base = (node.module or "").partition(".")[0]
                    if base in blocked:
                        issues.append({"file": str(python_path.relative_to(ROOT)), "line": node.lineno,
                                       "reason": "production import is forbidden", "import": node.module})
                elif isinstance(node, ast.Call):
                    function = node.func
                    if isinstance(function, ast.Attribute) and function.attr in {"CDLL", "PyDLL", "WinDLL", "dlopen"}:
                        issues.append({"file": str(python_path.relative_to(ROOT)), "line": node.lineno,
                                       "reason": "ctypes or dynamic regex-engine loading is forbidden", "call": function.attr})
                    dynamic_import = (
                        isinstance(function, ast.Name) and function.id == "__import__"
                        or isinstance(function, ast.Attribute) and function.attr == "import_module"
                    )
                    if dynamic_import and node.args:
                        target = node.args[0]
                        if isinstance(target, ast.Constant) and isinstance(target.value, str):
                            if target.value.partition(".")[0] in blocked:
                                issues.append({"file": str(python_path.relative_to(ROOT)), "line": node.lineno,
                                               "reason": "dynamic production import is forbidden", "import": target.value})

    prohibited = (
        (re.compile(r"\b(?:regcomp|regexec|pcre2?_compile|onig_new|onig_search)\s*\("), "external regex executor"),
        (re.compile(r"\b(?:sre_compile|sre_parse|_sre)\b"), "CPython regex delegation"),
        (re.compile(r"\b(?:regex|regex_lite|regex_syntax|fancy_regex|regex_automata|pcre|pcre2|onig|onig_sys|re2|hyperscan|aho_corasick)::"), "external Rust regex or search crate"),
        (re.compile(r"\bfn\s+(?:eval|run_match_legacy|eval_counted)\s*\("), "retained legacy AST evaluator"),
        (re.compile(r"\brun_match_legacy\s*\("), "runtime legacy-regex fallback"),
    )
    if rust_root.is_dir():
        for path in sorted(rust_root.rglob("*.rs")):
            inspected.append(str(path.relative_to(ROOT)))
            source = strip_comments(path.read_text(encoding="utf-8"))
            for expression, reason in prohibited:
                match = expression.search(source)
                if match:
                    issues.append({"file": str(path.relative_to(ROOT)),
                                   "line": source.count("\n", 0, match.start()) + 1,
                                   "reason": reason, "match": match.group(0)})
    else:
        issues.append({"file": str(rust_root.relative_to(ROOT)), "reason": "Rust source directory missing"})

    if bridge_path.is_file():
        inspected.append(str(bridge_path.relative_to(ROOT)))
        source = strip_comments(bridge_path.read_text(encoding="utf-8"))
        for expression, reason in prohibited[:2]:
            match = expression.search(source)
            if match:
                issues.append({"file": str(bridge_path.relative_to(ROOT)),
                               "line": source.count("\n", 0, match.start()) + 1,
                               "reason": reason, "match": match.group(0)})
        imported = re.search(r"PyImport_ImportModule\s*\(\s*[\"'](?:re|_sre|regex)[\"']", source)
        if imported:
            issues.append({"file": str(bridge_path.relative_to(ROOT)), "reason": "bridge imports a forbidden regex engine",
                           "line": source.count("\n", 0, imported.start()) + 1})

    if cargo_path.is_file():
        inspected.append(str(cargo_path.relative_to(ROOT)))
        blocked_packages = {
            "regex", "regex-lite", "regex-automata", "regex-syntax", "fancy-regex",
            "pcre", "pcre2", "onig", "onig-sys", "re2", "hyperscan",
            "aho-corasick", "memchr",
        }
        try:
            cargo = tomllib.loads(cargo_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            issues.append({"file": str(cargo_path.relative_to(ROOT)), "reason": str(error)})
        else:
            sections = ("dependencies", "build-dependencies", "dev-dependencies")
            scopes = [("package", cargo)]
            workspace = cargo.get("workspace")
            if isinstance(workspace, dict):
                scopes.append(("workspace", workspace))
            for target, scope in cargo.get("target", {}).items():
                if isinstance(scope, dict):
                    scopes.append((f"target.{target}", scope))
            for scope_name, scope in scopes:
                for section in sections:
                    dependencies = scope.get(section, {})
                    if not isinstance(dependencies, dict):
                        issues.append({"file": str(cargo_path.relative_to(ROOT)),
                                       "reason": "invalid Cargo dependency declaration",
                                       "section": f"{scope_name}.{section}"})
                        continue
                    for name, specification in dependencies.items():
                        actual = specification.get("package", name) if isinstance(specification, dict) else name
                        if str(actual).replace("_", "-") in blocked_packages:
                            issues.append({"file": str(cargo_path.relative_to(ROOT)),
                                           "reason": "external regex or search package",
                                           "section": f"{scope_name}.{section}", "dependency": name,
                                           "package": actual})

    if cargo_lock_path.is_file():
        inspected.append(str(cargo_lock_path.relative_to(ROOT)))
        try:
            lock = tomllib.loads(cargo_lock_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            issues.append({"file": str(cargo_lock_path.relative_to(ROOT)), "reason": str(error)})
        else:
            packages = lock.get("package")
            if not isinstance(packages, list):
                issues.append({"file": str(cargo_lock_path.relative_to(ROOT)),
                               "reason": "invalid Cargo lockfile package list"})
            else:
                for package in packages:
                    if not isinstance(package, dict):
                        issues.append({"file": str(cargo_lock_path.relative_to(ROOT)),
                                       "reason": "invalid Cargo lockfile package entry"})
                        continue
                    name = package.get("name")
                    if not isinstance(name, str):
                        issues.append({"file": str(cargo_lock_path.relative_to(ROOT)),
                                       "reason": "Cargo lockfile package has no name"})
                    elif name.replace("_", "-") in {
                        "regex", "regex-lite", "regex-automata", "regex-syntax", "fancy-regex",
                        "pcre", "pcre2", "onig", "onig-sys", "re2", "hyperscan",
                        "aho-corasick", "memchr",
                    }:
                        issues.append({"file": str(cargo_lock_path.relative_to(ROOT)),
                                       "reason": "transitive external regex or search package", "dependency": name})

    return {"name": "from-scratch-static-audit", "passed": not issues,
            "inspected_files": inspected, "issues": issues}


def all_metric_values(value):
    output = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"correctness_checks", "checks", "cases", "case_count", "cases_per_module", "total_checks", "passed", "runnable"} and isinstance(child, int):
                output.append({"key": key, "value": child})
            output.extend(all_metric_values(child))
    elif isinstance(value, list):
        for child in value:
            output.extend(all_metric_values(child))
    return output


def failure_values(value):
    output = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"failed", "mismatches", "crashes", "timeouts", "oracle_failures", "self_oracle_failures", "unexplained_failures"}:
                if isinstance(child, int) and child:
                    output.append({"key": key, "value": child})
                elif isinstance(child, list) and child:
                    output.append({"key": key, "value": len(child)})
            output.extend(failure_values(child))
    elif isinstance(value, list):
        for child in value:
            output.extend(failure_values(child))
    return output


def performance_suite_step(step):
    script = Path(step.script)
    return (
        step.name.startswith("frozen-performance-")
        or script.name.startswith("perf_")
        or "performance" in script.parts
        or any(
            "performance/" in argument
            or "performance.v" in argument
            or "tools/perf_" in argument
            for argument in step.arguments
        )
    )


def suite_steps(artifact_dir, sealed_practice_only=False):
    def output(name):
        return str(artifact_dir / (name + ".json"))

    v3_manifest = ROOT / "oracle" / "v3" / "manifest.json"
    try:
        frozen_v3 = json.loads(v3_manifest.read_text(encoding="utf-8"))
        v3_cases = frozen_v3.get("cases")
        if not isinstance(v3_cases, int) or v3_cases <= 0:
            v3_cases = None
    except (OSError, UnicodeError, json.JSONDecodeError):
        v3_cases = None

    steps = (
        Step("rust-source-no-delegation", "tools/audit_candidate.py",
             ("candidates/rust_candidate.py", RUST_MODULE, "candidates/rust/src/lib.rs"), None, 120),
        Step("rust-bridge-no-delegation", "tools/audit_candidate.py",
             ("candidates/rust_candidate.py", RUST_MODULE, "candidates/rust/py_bridge.c"), None, 120),
        Step("rust-native-boundary-integrity", "tools/rust_ffi_lab.py",
             ("self-test", "--output", output("ffi-integrity")), None, 120, output("ffi-integrity")),
        Step("rust-native-boundary-self-oracle", "tools/rust_ffi_lab.py",
             ("oracle-self", "--output", output("ffi-oracle-self")), 546, 300, output("ffi-oracle-self")),
        Step("rust-native-boundary-compatibility", "tools/rust_ffi_lab.py",
             ("verify", "--module", RUST_MODULE, "--output", output("ffi-production")),
             738, 300, output("ffi-production")),
        Step("frozen-correctness-v2", "tools/oracle_v2.py",
             ("verify", "--module", RUST_MODULE, "--output", output("v2")), 8244, 900, output("v2")),
        Step("frozen-correctness-v3", "tools/oracle_v3.py",
             ("verify", "--module", RUST_MODULE, "--cohort", "all", "--output", output("v3")), v3_cases, 1800, output("v3")),
        Step("official-cpython-tests", "tools/cpython_re_oracle.py",
             ("verify", "--module", RUST_MODULE, "--output", output("cpython")), 144, 1800, output("cpython")),
        Step("frozen-performance-correctness-v6", "tools/perf_v6.py",
             ("verify", "--module", RUST_MODULE, "--output", output("v6")), 12432, 1200, output("v6")),
        Step("frozen-performance-v7-integrity", "tools/perf_v7.py",
             ("self-test",), None, 300),
        Step("frozen-performance-correctness-v7", "tools/perf_v7.py",
             ("verify", "--module", RUST_MODULE, "--output", output("v7")), 20624, 1800, output("v7")),
        Step("upstream-public-surface", "tools/zig_public_surface_probe.py",
             ("--module", RUST_MODULE, "--output", output("official-surface")), 190, 300, output("official-surface")),
        Step("rust-public-surface", "tools/rust_surface_probe.py",
             ("--module", RUST_MODULE, "--output", output("rust-surface")), 1198, 300, output("rust-surface")),
        Step("unicode-group-name-errors", "tools/rust_group_name_adversarial.py",
             ("--module", RUST_MODULE, "--output", output("group-name-errors")),
             420, 300, output("group-name-errors")),
        Step("replacement-and-callback-adversarial", "tools/rust_replacement_adversarial.py",
             ("--module", RUST_MODULE, "--output", output("replacement-adversarial")), 8862, 600, output("replacement-adversarial")),
        Step("deep-replacement-and-callback-adversarial", "tools/rust_replacement_adversarial.py",
             ("--module", RUST_MODULE, "--deep", "--output", output("replacement-adversarial-deep")),
             11266, 1200, output("replacement-adversarial-deep")),
        Step("extended-cpython-paths", "tools/rust_v6_paths_probe.py",
             ("--module", RUST_MODULE, "--seeded-cases", "512", "--output", output("extended-paths")),
             72248, 2400, output("extended-paths")),
        Step("isolated-crash-and-resource-safety", "tools/rust_safety_probe.py",
             ("--module", RUST_MODULE, "--output", output("safety")), 254, 1800, output("safety")),
        Step("isolated-depth-and-overflow-safety", "tools/rust_depth_probe.py",
             ("--module", RUST_MODULE, "--output", output("depth-safety")), 348, 2400, output("depth-safety")),
        Step("full-unicode-plane", "tools/rust_unicode_probe.py",
             ("--module", RUST_MODULE, "--membership-stride", "1", "--seeded-cases", "1024", "--output", output("unicode")),
             4494555, 3600, output("unicode")),
    )
    if not sealed_practice_only:
        return steps

    performance = tuple(step for step in steps if performance_suite_step(step))
    if tuple(step.name for step in performance) != SEALED_EXCLUDED_STEP_NAMES:
        raise RuntimeError(
            "sealed campaign discovered an unclassified performance or hidden-workload step"
        )
    retained = tuple(step for step in steps if not performance_suite_step(step))
    if len(retained) != len(SEALED_REQUIRED_STEP_NAMES):
        raise RuntimeError("sealed campaign changed its mandatory correctness denominator")
    if {step.name for step in retained} != SEALED_REQUIRED_STEP_NAMES:
        raise RuntimeError("sealed campaign dropped or replaced a required correctness or safety gate")
    if any(performance_suite_step(step) for step in retained):
        raise RuntimeError("a performance or hidden-workload suite entered the sealed campaign")
    return retained


def execute_selected_step(step, memory_mib, sealed_practice_only=False):
    if sealed_practice_only and (
        performance_suite_step(step)
        or step.name not in SEALED_REQUIRED_STEP_NAMES
    ):
        raise RuntimeError(
            f"sealed campaign refused to execute a performance or unclassified step: {step.name}"
        )
    return execute(step, memory_mib)


def restrict_process(memory_mib, cpu_seconds):
    def apply():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        limit = memory_mib * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))

    return apply


def execute(step, memory_mib):
    script = ROOT / step.script
    command = [sys.executable, str(script), *step.arguments]
    result = {"name": step.name, "command": command,
              "expected_checks": step.expected_checks,
              "timeout_seconds": step.timeout_seconds,
              "memory_limit_mib": memory_mib, "core_dumps": "disabled"}
    if not script.is_file():
        return {**result, "passed": False, "status": "missing-required-oracle"}

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    try:
        child = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="backslashreplace",
            timeout=step.timeout_seconds,
            check=False,
            preexec_fn=restrict_process(memory_mib, step.timeout_seconds + 5),
        )
    except subprocess.TimeoutExpired as error:
        return {**result, "passed": False, "status": "timeout",
                "elapsed_seconds": time.monotonic() - started,
                "stdout": (error.stdout or b"")[-16384:].decode("utf-8", "backslashreplace")
                if isinstance(error.stdout, bytes) else (error.stdout or "")[-16384:],
                "stderr": (error.stderr or b"")[-16384:].decode("utf-8", "backslashreplace")
                if isinstance(error.stderr, bytes) else (error.stderr or "")[-16384:]}

    result.update({"elapsed_seconds": time.monotonic() - started,
                   "returncode": child.returncode,
                   "stdout": child.stdout[-32768:],
                   "stderr": child.stderr[-32768:]})
    if child.returncode:
        result["passed"] = False
        result["status"] = "signal" if child.returncode < 0 else "failed"
        if child.returncode < 0:
            result["signal"] = -child.returncode
        return result

    if step.artifact is not None:
        artifact = Path(step.artifact)
        if not artifact.is_file():
            return {**result, "passed": False, "status": "missing-required-evidence"}
        result["artifact"] = str(artifact)
        result["artifact_sha256"] = sha256(artifact)
        try:
            report = json.loads(artifact.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            return {**result, "passed": False, "status": "invalid-evidence", "error": str(error)}
        values = all_metric_values(report)
        result["observed_metrics"] = values
        problems = failure_values(report)
        if problems:
            return {**result, "passed": False, "status": "reported-failures", "failure_metrics": problems}
        if step.expected_checks is not None and not any(value["value"] == step.expected_checks for value in values):
            return {**result, "passed": False, "status": "incorrect-or-unverified-denominator"}
        if step.name.startswith("rust-native-boundary-"):
            expected_kinds = {
                "rust-native-boundary-integrity": "self-test",
                "rust-native-boundary-self-oracle": "stdlib-vs-stdlib-boundary-oracle",
                "rust-native-boundary-compatibility": "semantic-verification",
            }
            if (
                report.get("schema") != "rebar-rust-ffi-lab-v1"
                or report.get("kind") != expected_kinds[step.name]
                or report.get("holdout_accessed") is not False
                or report.get("semantic_cases") != 354
                or report.get("timing_cases") != 192
            ):
                return {**result, "passed": False, "status": "invalid-native-boundary-evidence"}
            if step.name == "rust-native-boundary-integrity" and (
                report.get("result") != "PASS"
                or report.get("timing_families") != 24
                or report.get("rejected_corrupt_observations") != 5
            ):
                return {**result, "passed": False, "status": "failed-native-boundary-integrity-controls"}
            if (
                step.name == "rust-native-boundary-compatibility"
                and report.get("module") != RUST_MODULE
            ):
                return {**result, "passed": False, "status": "incorrect-native-boundary-candidate"}
        if step.name == "unicode-group-name-errors" and (
            report.get("schema") != "rebar-rust-unicode-group-name-adversarial-v1"
            or report.get("module") != RUST_MODULE
            or report.get("formatter") != "production"
            or report.get("self_oracle_passes") != 2
        ):
            return {**result, "passed": False, "status": "invalid-unicode-group-name-evidence"}
        if step.name == "official-cpython-tests":
            result["official_counts"] = {
                "methods": report.get("methods"),
                "passed": report.get("passed"),
                "skipped": report.get("skipped"),
            }
            if report.get("methods") != 146 or report.get("passed") != 144 or report.get("skipped") != 2:
                return {**result, "passed": False, "status": "incorrect-official-cpython-denominator"}
        if step.name == "frozen-correctness-v3":
            manifest = ROOT / "oracle" / "v3" / "manifest.json"
            if step.expected_checks is None or not manifest.is_file():
                return {**result, "passed": False, "status": "missing-frozen-v3-denominator"}
            frozen = json.loads(manifest.read_text(encoding="utf-8"))
            wanted = frozen.get("expected_sha256")
            observed = report.get("expected_sha256")
            result["fixture_sha256"] = {"expected": wanted, "actual": observed}
            if not wanted or wanted != observed:
                return {**result, "passed": False, "status": "v3-fixture-hash-mismatch"}
            obligations = frozen.get("obligations")
            result["mapped_obligations"] = report.get("mapped_obligations")
            if isinstance(obligations, int) and report.get("mapped_obligations") != obligations:
                return {**result, "passed": False, "status": "unmapped-frozen-v3-obligation"}
        if step.name == "frozen-performance-correctness-v7":
            manifest = ROOT / "performance" / "v7" / "manifest.json"
            if not manifest.is_file():
                return {**result, "passed": False, "status": "missing-frozen-v7-manifest"}
            frozen = json.loads(manifest.read_text(encoding="utf-8"))
            wanted = frozen.get("expected_sha256")
            observed = report.get("expected_sha256")
            result["fixture_sha256"] = {
                "pinned": V7_EXPECTED_SHA256,
                "manifest": wanted,
                "actual": observed,
            }
            if wanted != V7_EXPECTED_SHA256 or observed != V7_EXPECTED_SHA256:
                return {**result, "passed": False, "status": "v7-fixture-hash-mismatch"}

    return {**result, "passed": True, "status": "passed"}


def sealed_practice_self_test():
    """Poison mixed-suite execution, imports, and file access without running a gate."""
    import builtins
    from unittest import mock

    original_import = builtins.__import__
    original_open = Path.open
    forbidden_directory = (ROOT / "performance").resolve()
    tools_directory = (ROOT / "tools").resolve()
    poisoned_imports = []
    poisoned_opens = []

    def guarded_import(name, *args, **kwargs):
        if (
            name == "performance"
            or name.startswith("performance.")
            or name.startswith("tools.perf_")
        ):
            poisoned_imports.append(name)
            raise AssertionError(f"sealed campaign tried to import a performance suite: {name}")
        return original_import(name, *args, **kwargs)

    def guarded_open(path, *args, **kwargs):
        resolved = path.resolve()
        if (
            resolved.is_relative_to(forbidden_directory)
            or (
                resolved.is_relative_to(tools_directory)
                and resolved.name.startswith("perf_")
            )
        ):
            poisoned_opens.append(str(resolved))
            raise AssertionError(f"sealed campaign tried to open performance evidence: {resolved}")
        return original_open(path, *args, **kwargs)

    directory = Path("/tmp/rebar-rust-sealed-campaign-poison-controls")
    with (
        mock.patch.object(builtins, "__import__", guarded_import),
        mock.patch.object(Path, "open", guarded_open),
        mock.patch.object(
            subprocess,
            "run",
            side_effect=AssertionError("sealed campaign self-test must not execute a child"),
        ) as child,
    ):
        complete = suite_steps(directory)
        retained = suite_steps(directory, sealed_practice_only=True)
        excluded = tuple(step for step in complete if performance_suite_step(step))
        if tuple(step.name for step in excluded) != SEALED_EXCLUDED_STEP_NAMES:
            raise RuntimeError("sealed self-test changed the excluded performance suites")
        if tuple(step for step in complete if not performance_suite_step(step)) != retained:
            raise RuntimeError("sealed self-test changed default campaign ordering")
        if {step.name for step in retained} != SEALED_REQUIRED_STEP_NAMES:
            raise RuntimeError("sealed self-test lost a required correctness or safety step")

        rejected = 0
        poisoned = (*excluded, Step(
            "unclassified-hidden-performance-step",
            "tools/perf_v8.py",
            ("verify",),
            None,
            1,
        ))
        for step in poisoned:
            try:
                execute_selected_step(step, 256, sealed_practice_only=True)
            except RuntimeError:
                rejected += 1
            else:
                raise RuntimeError("sealed campaign accepted a poisoned performance step")
        if rejected != len(poisoned):
            raise RuntimeError("sealed campaign did not reject every poisoned performance step")
        if child.call_count or poisoned_opens or poisoned_imports:
            raise RuntimeError("a sealed performance step was executed, opened, or imported")

    return {
        "schema": "rebar-rust-campaign-gate-sealed-practice-self-test-v1",
        "mode": "sealed-practice-only",
        "default_step_count": len(complete),
        "retained_step_count": len(retained),
        "retained_step_names": [step.name for step in retained],
        "excluded_step_names": [step.name for step in excluded],
        "excluded_step_count": len(excluded),
        "rejected_poisoned_steps": rejected,
        "performance_processes_started": child.call_count,
        "performance_files_opened": len(poisoned_opens),
        "performance_modules_imported": len(poisoned_imports),
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
        "failed": 0,
    }


def persist(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--memory-mib", type=int, default=2048)
    parser.add_argument("--continue-on-failure", action="store_true")
    parser.add_argument(
        "--sealed-practice-only",
        action="store_true",
        help="exclude every performance suite and preserve all compatibility and safety gates",
    )
    parser.add_argument(
        "--sealed-practice-self-test",
        action="store_true",
        help="prove excluded performance steps cannot be executed, imported, or opened",
    )
    args = parser.parse_args()
    if args.memory_mib < 256:
        parser.error("--memory-mib must be at least 256")
    if args.sealed_practice_self_test:
        if args.output is not None or args.artifact_dir is not None:
            parser.error("the sealed-practice self-test never creates output or artifacts")
        print(json.dumps(sealed_practice_self_test(), sort_keys=True))
        return
    if args.output is None:
        parser.error("the following arguments are required: --output")
    destination = Path(args.output).resolve()
    directory = Path(args.artifact_dir).resolve() if args.artifact_dir else destination.parent / (destination.stem + "-steps")
    selected_steps = (
        suite_steps(directory, sealed_practice_only=True)
        if args.sealed_practice_only
        else None
    )
    directory.mkdir(parents=True, exist_ok=True)

    report = {
        "schema": "rebar-rust-campaign-gate-v1",
        "candidate": RUST_MODULE,
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "pinned_cpython": ".".join(map(str, PINNED_CPYTHON)),
        "artifact_directory": str(directory),
        "fail_fast": not args.continue_on_failure,
        "memory_limit_mib": args.memory_mib,
        "goal": goal_state(),
        "steps": [],
        "passed": False,
    }
    if args.sealed_practice_only:
        complete = suite_steps(directory)
        excluded = [
            {"name": step.name, "script": step.script, "reason": "performance fixture or held-out workload"}
            for step in complete
            if performance_suite_step(step)
        ]
        report.update({
            "mode": "sealed-practice-only",
            "holdout_accessed": False,
            "performance": "NOT MEASURED",
            "timing_performed": False,
            "excluded_steps": excluded,
            "required_correctness_step_count": len(selected_steps),
        })

    if tuple(sys.version_info[:3]) != PINNED_CPYTHON:
        report["failure"] = "campaign must run under pinned CPython 3.14.6"
        persist(destination, report)
        print(json.dumps({"schema": report["schema"], "passed": False, "failure": report["failure"]}, sort_keys=True))
        raise SystemExit(1)
    if not report["goal"]["passed"]:
        report["failure"] = "immutable objective hash does not match"
        persist(destination, report)
        print(json.dumps({"schema": report["schema"], "passed": False, "failure": report["failure"]}, sort_keys=True))
        raise SystemExit(1)

    audit = static_audit()
    report["steps"].append(audit)
    persist(destination, report)
    print(json.dumps({"step": audit["name"], "passed": audit["passed"]}, sort_keys=True), flush=True)
    if not audit["passed"] and not args.continue_on_failure:
        raise SystemExit(1)

    for step in (
        selected_steps if selected_steps is not None else suite_steps(directory)
    ):
        print(json.dumps({"starting": step.name, "expected_checks": step.expected_checks}, sort_keys=True), flush=True)
        outcome = execute_selected_step(step, args.memory_mib, args.sealed_practice_only)
        after = goal_state()
        if not after["passed"]:
            outcome["passed"] = False
            outcome["status"] = "immutable-objective-changed"
            outcome["goal"] = after
        report["steps"].append(outcome)
        persist(destination, report)
        print(json.dumps({"step": step.name, "passed": outcome["passed"], "status": outcome["status"]}, sort_keys=True), flush=True)
        if not outcome["passed"] and not args.continue_on_failure:
            raise SystemExit(1)

    report["goal"] = goal_state()
    report["passed"] = report["goal"]["passed"] and all(step.get("passed") for step in report["steps"])
    persist(destination, report)
    result = {
        "schema": report["schema"],
        "passed": report["passed"],
        "steps": len(report["steps"]),
        "goal_sha256": report["goal"].get("actual_sha256"),
        "output": str(destination),
    }
    if args.sealed_practice_only:
        result.update({
            "mode": "sealed-practice-only",
            "holdout_accessed": False,
            "performance": "NOT MEASURED",
            "excluded_step_names": [step["name"] for step in report["excluded_steps"]],
        })
    print(json.dumps(result, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
