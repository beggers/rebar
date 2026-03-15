"""Benchmark harness for compile-path and Python-surface workload suites."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import math
import os
import pathlib
import platform
import re as cpython_re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.descriptor_values import materialize_descriptor_value
from rebar_harness.metadata import build_cpython_baseline
from rebar_harness.scorecard_io import (
    load_scorecard_report,
    remove_scorecard_sidecar,
    validate_scorecard_report_path,
    write_scorecard_report,
)


TARGET_CPYTHON_SERIES = "3.12.x"
REPORT_SCHEMA_VERSION = "1.0"
REPORT_ATTRIBUTE = "REPORT"
MANIFEST_SCHEMA_VERSION = 1
PUBLISHED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"
LEGACY_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"
LEGACY_REPORT_PATH_ERROR = (
    "reports/benchmarks/latest.json is a retired legacy published scorecard path; "
    "use reports/benchmarks/latest.py for the tracked published scorecard or a "
    "non-tracked temporary .json path for scratch output."
)
DEFAULT_MANIFEST_PATHS = (
    REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py",
    REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "pattern_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "literal_flag_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_named_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "numbered_backreference_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_segment_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "literal_alternation_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_callable_replacement_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_alternation_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_callable_replacement_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "branch_local_backreference_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "wider_ranged_repeat_quantified_group_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "quantified_alternation_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_alternation_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_no_else_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_empty_else_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_empty_yes_else_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_fully_empty_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py",
)
DEFAULT_REPORT_PATH = PUBLISHED_REPORT_PATH
DEFAULT_NATIVE_SMOKE_MANIFEST_PATHS = (
    REPO_ROOT / "benchmarks" / "workloads" / "pattern_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.py",
    REPO_ROOT / "benchmarks" / "workloads" / "literal_flag_boundary.py",
)
SOURCE_TREE_SHIM_MODE = "source-tree-shim"
BUILT_NATIVE_MODE = "built-native"
NATIVE_MODULE_NAME = "rebar._rebar"


@dataclass(frozen=True)
class Workload:
    """Single benchmark workload definition."""

    manifest_id: str
    workload_id: str
    bucket: str
    family: str
    operation: str
    pattern: str
    haystack: str | None
    replacement: Any | None
    flags: int
    count: int
    maxsplit: int
    text_model: str
    cache_mode: str
    timing_scope: str
    warmup_iterations: int
    sample_iterations: int
    timed_samples: int
    notes: list[str]
    categories: list[str]
    syntax_features: list[str]
    smoke: bool

    @classmethod
    def from_dict(
        cls,
        *,
        manifest_id: str,
        raw_workload: dict[str, Any],
        defaults: dict[str, Any],
    ) -> "Workload":
        categories = [str(category) for category in raw_workload.get("categories", [])]
        return cls(
            manifest_id=manifest_id,
            workload_id=str(raw_workload["id"]),
            bucket=str(raw_workload.get("bucket", "unbucketed")),
            family=str(raw_workload.get("family", "parser")),
            operation=str(raw_workload["operation"]),
            pattern=str(raw_workload.get("pattern", "")),
            haystack=(
                None
                if raw_workload.get("haystack") is None
                else str(raw_workload.get("haystack"))
            ),
            replacement=normalize_workload_value(raw_workload.get("replacement")),
            flags=int(raw_workload.get("flags", 0)),
            count=int(raw_workload.get("count", 0)),
            maxsplit=int(raw_workload.get("maxsplit", 0)),
            text_model=str(raw_workload.get("text_model", "str")),
            cache_mode=str(raw_workload.get("cache_mode", "cold")),
            timing_scope=str(raw_workload.get("timing_scope", "compile-path-proxy")),
            warmup_iterations=int(
                raw_workload.get("warmup_iterations", defaults.get("warmup_iterations", 2))
            ),
            sample_iterations=int(
                raw_workload.get("sample_iterations", defaults.get("sample_iterations", 1))
            ),
            timed_samples=int(raw_workload.get("timed_samples", defaults.get("timed_samples", 5))),
            notes=[str(note) for note in raw_workload.get("notes", [])],
            categories=categories,
            syntax_features=[
                str(feature)
                for feature in raw_workload.get("syntax_features", raw_workload.get("categories", []))
            ],
            smoke=bool(raw_workload.get("smoke", False) or "smoke" in categories),
        )

    def _encode_text(self, value: str) -> str | bytes:
        if self.text_model == "str":
            return value
        if self.text_model == "bytes":
            return value.encode("utf-8")
        raise ValueError(f"unsupported text model {self.text_model!r}")

    def pattern_payload(self) -> str | bytes:
        return self._encode_text(self.pattern)

    def haystack_payload(self) -> str | bytes:
        if self.haystack is None:
            raise ValueError(f"workload {self.workload_id!r} requires a haystack payload")
        return self._encode_text(self.haystack)

    def replacement_payload(self) -> Any:
        if self.replacement is None:
            raise ValueError(f"workload {self.workload_id!r} requires a replacement payload")
        return materialize_descriptor_value(
            self.replacement,
            text_model=self.text_model,
            callback_module_name="rebar_harness.benchmarks",
        )


def normalize_workload_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [normalize_workload_value(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalize_workload_value(item_value)
            for key, item_value in value.items()
        }
    raise ValueError(f"unsupported workload value {value!r}")


@dataclass
class BenchmarkRunContext:
    """Resolved benchmark execution mode plus adapter/runtime metadata."""

    requested_mode: str
    resolved_mode: str
    baseline_adapter: "BenchmarkAdapter"
    implementation_adapter: "BenchmarkAdapter"
    implementation_metadata: dict[str, Any]
    execution_model: str
    cleanup: Callable[[], None]


class NativeBenchmarkProvisionError(RuntimeError):
    """Raised when a strict built-native benchmark run cannot provision a native wheel."""


def workload_to_payload(workload: Workload) -> dict[str, Any]:
    return {
        "manifest_id": workload.manifest_id,
        "workload_id": workload.workload_id,
        "bucket": workload.bucket,
        "family": workload.family,
        "operation": workload.operation,
        "pattern": workload.pattern,
        "haystack": workload.haystack,
        "replacement": workload.replacement,
        "flags": workload.flags,
        "count": workload.count,
        "maxsplit": workload.maxsplit,
        "text_model": workload.text_model,
        "cache_mode": workload.cache_mode,
        "timing_scope": workload.timing_scope,
        "warmup_iterations": workload.warmup_iterations,
        "sample_iterations": workload.sample_iterations,
        "timed_samples": workload.timed_samples,
        "notes": list(workload.notes),
        "categories": list(workload.categories),
        "syntax_features": list(workload.syntax_features),
        "smoke": workload.smoke,
    }


def workload_from_payload(payload: dict[str, Any]) -> Workload:
    return Workload(
        manifest_id=str(payload["manifest_id"]),
        workload_id=str(payload["workload_id"]),
        bucket=str(payload["bucket"]),
        family=str(payload["family"]),
        operation=str(payload["operation"]),
        pattern=str(payload.get("pattern", "")),
        haystack=None if payload.get("haystack") is None else str(payload["haystack"]),
        replacement=normalize_workload_value(payload.get("replacement")),
        flags=int(payload.get("flags", 0)),
        count=int(payload.get("count", 0)),
        maxsplit=int(payload.get("maxsplit", 0)),
        text_model=str(payload["text_model"]),
        cache_mode=str(payload["cache_mode"]),
        timing_scope=str(payload["timing_scope"]),
        warmup_iterations=int(payload["warmup_iterations"]),
        sample_iterations=int(payload["sample_iterations"]),
        timed_samples=int(payload["timed_samples"]),
        notes=[str(note) for note in payload.get("notes", [])],
        categories=[str(category) for category in payload.get("categories", [])],
        syntax_features=[str(feature) for feature in payload.get("syntax_features", [])],
        smoke=bool(payload.get("smoke", False)),
    )


def _load_python_manifest(path: pathlib.Path) -> dict[str, Any]:
    module_name = f"_rebar_benchmark_manifest_{path.stem}".replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load Python benchmark manifest from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "MANIFEST"):
        raise ValueError(f"Python benchmark manifest module {path} is missing a MANIFEST value")
    raw_manifest = getattr(module, "MANIFEST")
    if not isinstance(raw_manifest, dict):
        raise ValueError(f"benchmark manifest in {path} must be a dict")
    return raw_manifest


def _load_raw_manifest(path: pathlib.Path) -> dict[str, Any]:
    if path.suffix != ".py":
        raise ValueError(
            f"unsupported benchmark manifest extension {path.suffix!r} for {path}"
        )
    raw_manifest = _load_python_manifest(path)

    if not isinstance(raw_manifest, dict):
        raise ValueError(f"benchmark manifest in {path} must be an object")
    return raw_manifest


def load_manifest(path: pathlib.Path) -> tuple[dict[str, Any], list[Workload]]:
    raw_manifest = _load_raw_manifest(path)
    schema_version = raw_manifest.get("schema_version")
    if schema_version != MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported benchmark manifest schema version {schema_version!r}; "
            f"expected {MANIFEST_SCHEMA_VERSION}"
        )

    defaults = raw_manifest.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("benchmark manifest defaults must be an object")

    manifest_id = str(raw_manifest["manifest_id"])
    workloads = [
        Workload.from_dict(
            manifest_id=manifest_id,
            raw_workload=raw_workload,
            defaults=defaults,
        )
        for raw_workload in raw_manifest.get("workloads", [])
    ]
    return raw_manifest, workloads


def load_manifests(paths: list[pathlib.Path]) -> tuple[list[dict[str, Any]], list[Workload]]:
    raw_manifests: list[dict[str, Any]] = []
    workloads: list[Workload] = []
    manifest_ids: set[str] = set()
    workload_ids: set[str] = set()

    for path in paths:
        raw_manifest, manifest_workloads = load_manifest(path)
        manifest_id = str(raw_manifest["manifest_id"])
        if manifest_id in manifest_ids:
            raise ValueError(f"duplicate benchmark manifest id {manifest_id!r}")
        manifest_ids.add(manifest_id)

        for workload in manifest_workloads:
            if workload.workload_id in workload_ids:
                raise ValueError(f"duplicate benchmark workload id {workload.workload_id!r}")
            workload_ids.add(workload.workload_id)

        raw_manifests.append(raw_manifest)
        workloads.extend(manifest_workloads)

    return raw_manifests, workloads


def select_workloads(workloads: list[Workload], *, smoke_only: bool) -> list[Workload]:
    if not smoke_only:
        return workloads

    selected_workloads = [workload for workload in workloads if workload.smoke]
    if not selected_workloads:
        raise ValueError("no smoke-tagged workloads matched the selected benchmark manifests")
    return selected_workloads


class BenchmarkAdapter:
    """Adapter boundary for benchmarkable workloads."""

    adapter_name: str
    import_name: str
    module: Any

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        raise NotImplementedError


def load_module(module_name: str) -> Any:
    return importlib.import_module(module_name)


def load_rebar_module() -> Any:
    return load_module("rebar")


def _clear_module(module_name: str) -> None:
    module_prefix = f"{module_name}."
    loaded_names = [
        name for name in sys.modules if name == module_name or name.startswith(module_prefix)
    ]
    for name in loaded_names:
        sys.modules.pop(name, None)
    importlib.invalidate_caches()


def import_callable(module_name: str, workload: Workload) -> Any:
    if workload.operation != "import":
        raise ValueError(f"unsupported import workload operation {workload.operation!r}")

    if workload.cache_mode in {"cold", "purged"}:

        def run_once() -> object:
            _clear_module(module_name)
            return importlib.import_module(module_name)

        return run_once

    if workload.cache_mode == "warm":
        importlib.import_module(module_name)

        def run_once() -> object:
            return importlib.import_module(module_name)

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def compile_callable(module: Any, workload: Workload) -> Any:
    pattern = workload.pattern_payload()

    if workload.operation not in {"compile", "module.compile"}:
        raise ValueError(f"unsupported compile workload operation {workload.operation!r}")

    if workload.cache_mode == "cold":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            return module.compile(pattern, workload.flags)

        return run_once

    if workload.cache_mode == "warm":
        module.compile(pattern, workload.flags)

        def run_once() -> object:
            return module.compile(pattern, workload.flags)

        return run_once

    if workload.cache_mode == "purged":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            result = module.compile(pattern, workload.flags)
            if hasattr(module, "purge"):
                module.purge()
            return result

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def module_helper_invoke(module: Any, workload: Workload) -> object:
    pattern = workload.pattern_payload()
    haystack = workload.haystack_payload()

    if workload.operation == "module.search":
        return module.search(pattern, haystack, workload.flags)
    if workload.operation == "module.match":
        return module.match(pattern, haystack, workload.flags)
    if workload.operation == "module.fullmatch":
        return module.fullmatch(pattern, haystack, workload.flags)
    if workload.operation == "module.split":
        return module.split(pattern, haystack, workload.maxsplit, workload.flags)
    if workload.operation == "module.findall":
        return module.findall(pattern, haystack, workload.flags)
    if workload.operation == "module.sub":
        return module.sub(
            pattern,
            workload.replacement_payload(),
            haystack,
            workload.count,
            workload.flags,
        )
    if workload.operation == "module.subn":
        return module.subn(
            pattern,
            workload.replacement_payload(),
            haystack,
            workload.count,
            workload.flags,
        )
    raise ValueError(f"unsupported module helper operation {workload.operation!r}")


def helper_callable(module: Any, workload: Workload) -> Any:
    def invoke() -> object:
        return module_helper_invoke(module, workload)

    if workload.cache_mode == "cold":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            return invoke()

        return run_once

    if workload.cache_mode == "warm":
        invoke()

        def run_once() -> object:
            return invoke()

        return run_once

    if workload.cache_mode == "purged":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            result = invoke()
            if hasattr(module, "purge"):
                module.purge()
            return result

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def pattern_helper_invoke(compiled: Any, workload: Workload) -> object:
    haystack = workload.haystack_payload()

    if workload.operation == "pattern.search":
        return compiled.search(haystack)
    if workload.operation == "pattern.match":
        return compiled.match(haystack)
    if workload.operation == "pattern.fullmatch":
        return compiled.fullmatch(haystack)
    if workload.operation == "pattern.finditer":
        return list(compiled.finditer(haystack))
    if workload.operation == "pattern.sub":
        return compiled.sub(workload.replacement_payload(), haystack, count=workload.count)
    if workload.operation == "pattern.subn":
        return compiled.subn(workload.replacement_payload(), haystack, count=workload.count)
    raise ValueError(f"unsupported pattern helper operation {workload.operation!r}")


def pattern_helper_callable(module: Any, workload: Workload) -> Any:
    pattern = workload.pattern_payload()

    def compile_pattern() -> Any:
        return module.compile(pattern, workload.flags)

    if workload.cache_mode == "cold":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            compiled = compile_pattern()
            return pattern_helper_invoke(compiled, workload)

        return run_once

    if workload.cache_mode == "warm":
        compiled = compile_pattern()

        def run_once() -> object:
            return pattern_helper_invoke(compiled, workload)

        return run_once

    if workload.cache_mode == "purged":
        compiled = compile_pattern()
        if hasattr(module, "purge"):
            module.purge()

        def run_once() -> object:
            return pattern_helper_invoke(compiled, workload)

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def build_callable(module: Any, import_name: str, workload: Workload) -> Any:
    if workload.operation == "import":
        return import_callable(import_name, workload)
    if workload.operation in {"compile", "module.compile"}:
        return compile_callable(module, workload)
    if workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
        "module.split",
        "module.findall",
        "module.sub",
        "module.subn",
    }:
        return helper_callable(module, workload)
    if workload.operation in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
        "pattern.finditer",
        "pattern.sub",
        "pattern.subn",
    }:
        return pattern_helper_callable(module, workload)
    raise ValueError(f"unsupported benchmark operation {workload.operation!r}")


def measure_callable(workload: Workload, callback: Any) -> dict[str, Any]:
    for _ in range(workload.warmup_iterations):
        for _ in range(workload.sample_iterations):
            callback()

    sample_ns: list[int] = []
    for _ in range(workload.timed_samples):
        start = time.perf_counter_ns()
        for _ in range(workload.sample_iterations):
            callback()
        elapsed_ns = time.perf_counter_ns() - start
        sample_ns.append(max(1, round(elapsed_ns / workload.sample_iterations)))

    median_ns = int(statistics.median(sample_ns))
    mean_ns = int(round(statistics.fmean(sample_ns)))
    return {
        "status": "measured",
        "median_ns": median_ns,
        "mean_ns": mean_ns,
        "min_ns": min(sample_ns),
        "max_ns": max(sample_ns),
        "sample_count": len(sample_ns),
        "warmup_iterations": workload.warmup_iterations,
        "sample_iterations": workload.sample_iterations,
        "samples_ns": sample_ns,
    }


class CpythonReBenchmarkAdapter(BenchmarkAdapter):
    adapter_name = "cpython.re"
    import_name = "re"
    module = cpython_re

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        callback = build_callable(self.module, self.import_name, workload)
        timing = measure_callable(workload, callback)
        return {"adapter": self.adapter_name, **timing}


class RebarBenchmarkAdapter(BenchmarkAdapter):
    adapter_name = "rebar"
    import_name = "rebar"

    def __init__(self, module: Any) -> None:
        self.module = module

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        try:
            callback = build_callable(self.module, self.import_name, workload)
            timing = measure_callable(workload, callback)
        except NotImplementedError as exc:
            return {
                "adapter": self.adapter_name,
                "status": "unimplemented",
                "reason": str(exc),
            }
        except Exception as exc:
            return {
                "adapter": self.adapter_name,
                "status": "unavailable",
                "reason": f"{type(exc).__name__}: {exc}",
            }
        return {"adapter": self.adapter_name, **timing}


class SubprocessBenchmarkAdapter(BenchmarkAdapter):
    """Runs one workload probe in a fresh subprocess environment."""

    def __init__(
        self,
        *,
        adapter_name: str,
        import_name: str,
        python_executable: pathlib.Path,
        pythonpath_entries: list[pathlib.Path],
    ) -> None:
        self.adapter_name = adapter_name
        self.import_name = import_name
        self.python_executable = python_executable
        self.pythonpath_entries = list(pythonpath_entries)

    def _environment(self) -> dict[str, str]:
        env = os.environ.copy()
        pythonpath = os.pathsep.join(str(path) for path in self.pythonpath_entries)
        existing_pythonpath = env.get("PYTHONPATH")
        if existing_pythonpath:
            pythonpath = os.pathsep.join((pythonpath, existing_pythonpath))
        env["PYTHONPATH"] = pythonpath
        return env

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        result = subprocess.run(
            [
                str(self.python_executable),
                "-m",
                "rebar_harness.benchmarks",
                "--internal-run-workload",
                json.dumps(workload_to_payload(workload), sort_keys=True),
                "--internal-import-name",
                self.import_name,
                "--internal-adapter-name",
                self.adapter_name,
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=self._environment(),
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown subprocess failure"
            return {
                "adapter": self.adapter_name,
                "status": "unavailable",
                "reason": f"subprocess benchmark probe failed: {detail}",
            }
        return json.loads(result.stdout)


def calculate_speedup(
    baseline_timing: dict[str, Any], implementation_timing: dict[str, Any]
) -> float | None:
    baseline_ns = baseline_timing.get("median_ns")
    implementation_ns = implementation_timing.get("median_ns")
    if not isinstance(baseline_ns, int) or not isinstance(implementation_ns, int):
        return None
    if baseline_ns <= 0 or implementation_ns <= 0:
        return None
    return round(baseline_ns / implementation_ns, 4)


def build_variance_summary(timing: dict[str, Any]) -> dict[str, Any] | None:
    samples = timing.get("samples_ns")
    if not isinstance(samples, list) or not samples:
        return None
    return {
        "min_ns": timing["min_ns"],
        "max_ns": timing["max_ns"],
        "mean_ns": timing["mean_ns"],
        "sample_count": timing["sample_count"],
    }


def ns_to_ops_per_second(value: int | None) -> float | None:
    if not isinstance(value, int) or value <= 0:
        return None
    return round(1_000_000_000 / value, 2)


def gap_note_for_workload(workload: Workload) -> str:
    if workload.family == "parser":
        return (
            "Implementation timing is unavailable for parser cases outside the current "
            "rebar compile surface."
        )
    if workload.operation == "import":
        return "Implementation import timing is unavailable until the rebar package can be imported in the benchmark environment."
    if workload.operation.startswith("pattern."):
        return "Implementation timing is unavailable until the rebar compiled-pattern helper surface performs real work."
    return "Implementation timing is unavailable until the rebar module helper surface performs real work."


def evaluate_workload(
    workload: Workload,
    baseline_adapter: BenchmarkAdapter,
    implementation_adapter: BenchmarkAdapter,
) -> dict[str, Any]:
    baseline_timing = baseline_adapter.run_workload(workload)
    implementation_timing = implementation_adapter.run_workload(workload)
    speedup = calculate_speedup(baseline_timing, implementation_timing)

    status = "measured" if speedup is not None else implementation_timing["status"]
    notes = list(workload.notes)
    if implementation_timing["status"] != "measured":
        notes.append(gap_note_for_workload(workload))

    baseline_ns = baseline_timing.get("median_ns")
    implementation_ns = implementation_timing.get("median_ns")
    return {
        "id": workload.workload_id,
        "manifest_id": workload.manifest_id,
        "bucket": workload.bucket,
        "family": workload.family,
        "operation": workload.operation,
        "cache_mode": workload.cache_mode,
        "timing_scope": workload.timing_scope,
        "text_model": workload.text_model,
        "pattern": workload.pattern,
        "haystack": workload.haystack,
        "replacement": workload.replacement,
        "flags": workload.flags,
        "count": workload.count,
        "maxsplit": workload.maxsplit,
        "categories": workload.categories,
        "syntax_features": workload.syntax_features,
        "status": status,
        "baseline_ns": baseline_ns,
        "baseline_ops_per_second": ns_to_ops_per_second(baseline_ns),
        "implementation_ns": implementation_ns,
        "implementation_ops_per_second": ns_to_ops_per_second(implementation_ns),
        "speedup_vs_cpython": speedup,
        "notes": notes,
        "baseline_timing": baseline_timing,
        "implementation_timing": implementation_timing,
        "variance": {
            "baseline": build_variance_summary(baseline_timing),
            "implementation": build_variance_summary(implementation_timing),
        },
    }


def _median(values: list[int]) -> int | None:
    if not values:
        return None
    return int(statistics.median(values))


def _median_float(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(statistics.median(values)), 4)


def _geomean(values: list[float]) -> float | None:
    if not values:
        return None
    if any(value <= 0 for value in values):
        return None
    return round(math.exp(statistics.fmean(math.log(value) for value in values)), 4)


def build_cache_mode_summary(workloads: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for cache_mode in ("cold", "warm", "purged"):
        cache_workloads = [workload for workload in workloads if workload["cache_mode"] == cache_mode]
        baseline_samples = [
            workload["baseline_ns"]
            for workload in cache_workloads
            if isinstance(workload.get("baseline_ns"), int)
        ]
        implementation_samples = [
            workload["implementation_ns"]
            for workload in cache_workloads
            if isinstance(workload.get("implementation_ns"), int)
        ]
        speedups = [
            workload["speedup_vs_cpython"]
            for workload in cache_workloads
            if isinstance(workload.get("speedup_vs_cpython"), float)
        ]
        summary[cache_mode] = {
            "workload_count": len(cache_workloads),
            "known_gap_count": sum(1 for workload in cache_workloads if workload["status"] != "measured"),
            "median_baseline_ns": _median(baseline_samples),
            "median_implementation_ns": _median(implementation_samples),
            "median_speedup_vs_cpython": _median_float(speedups),
        }
    return summary


def family_readiness(family_workloads: list[dict[str, Any]], known_gap_count: int) -> str:
    if not family_workloads:
        return "absent"
    if known_gap_count == 0:
        return "measured"
    if known_gap_count < len(family_workloads):
        return "partial"
    return "scaffold-only"


def family_notes(family: str, family_workloads: list[dict[str, Any]]) -> list[str]:
    if family == "parser":
        return [
            "Phase 1 compile-path suite uses compile() as a parser proxy until a narrower benchmark hook exists."
        ]
    if family_workloads:
        return [
            "Phase 2 module-boundary timings use tiny import and helper-call workloads so the scorecard stays focused on public API overhead."
        ]
    return ["Module-boundary timings remain deferred to RBR-0015."]


def manifest_notes(raw_manifest: dict[str, Any], selected_workloads: list[dict[str, Any]]) -> list[str]:
    configured_notes = [str(note) for note in raw_manifest.get("notes", [])]
    if configured_notes:
        return configured_notes

    manifest_id = str(raw_manifest.get("manifest_id", ""))
    if manifest_id == "compile-matrix":
        return [
            "Compile-path workloads remain the parser proxy portion of the suite until a narrower parser hook exists."
        ]
    if manifest_id == "module-boundary":
        return [
            "Module-boundary workloads keep haystacks intentionally small so the timings emphasize public helper overhead."
        ]
    if manifest_id == "pattern-boundary":
        return [
            "Pattern-boundary workloads precompile tiny literal patterns ahead of the timed call so the scorecard isolates bound-method overhead from module helper and compile costs."
        ]
    if selected_workloads:
        return [
            "Regression/stability workloads track small, curated performance-cliff probes instead of broad engine-throughput claims."
        ]
    return []


def build_family_summary(workloads: list[dict[str, Any]], family: str) -> dict[str, Any]:
    family_workloads = [workload for workload in workloads if workload["family"] == family]
    baseline_samples = [
        workload["baseline_ns"]
        for workload in family_workloads
        if isinstance(workload.get("baseline_ns"), int)
    ]
    implementation_samples = [
        workload["implementation_ns"]
        for workload in family_workloads
        if isinstance(workload.get("implementation_ns"), int)
    ]
    speedups = [
        workload["speedup_vs_cpython"]
        for workload in family_workloads
        if isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    known_gap_count = sum(1 for workload in family_workloads if workload["status"] != "measured")

    return {
        "workload_count": len(family_workloads),
        "known_gap_count": known_gap_count,
        "readiness": family_readiness(family_workloads, known_gap_count),
        "median_baseline_ns": _median(baseline_samples),
        "median_implementation_ns": _median(implementation_samples),
        "median_speedup_vs_cpython": _median_float(speedups),
        "cache_modes": build_cache_mode_summary(family_workloads),
        "notes": family_notes(family, family_workloads),
    }


def _manifest_record_by_id(raw_manifests: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(raw_manifest["manifest_id"]): raw_manifest for raw_manifest in raw_manifests}


def build_manifest_summaries(
    *,
    raw_manifests: list[dict[str, Any]],
    workloads: list[dict[str, Any]],
    selection_mode: str,
) -> dict[str, dict[str, Any]]:
    raw_manifest_map = _manifest_record_by_id(raw_manifests)
    summaries: dict[str, dict[str, Any]] = {}

    for manifest_id, raw_manifest in raw_manifest_map.items():
        manifest_workloads = [
            workload for workload in workloads if workload["manifest_id"] == manifest_id
        ]
        speedups = [
            workload["speedup_vs_cpython"]
            for workload in manifest_workloads
            if isinstance(workload.get("speedup_vs_cpython"), float)
        ]
        known_gap_count = sum(1 for workload in manifest_workloads if workload["status"] != "measured")
        smoke_workload_ids = [
            str(workload["id"])
            for workload in raw_manifest.get("workloads", [])
            if bool(workload.get("smoke", False) or "smoke" in workload.get("categories", []))
        ]

        summaries[manifest_id] = {
            "workload_count": len(raw_manifest.get("workloads", [])),
            "selected_workload_count": len(manifest_workloads),
            "measured_workloads": len(speedups),
            "known_gap_count": known_gap_count,
            "readiness": family_readiness(manifest_workloads, known_gap_count),
            "median_speedup_vs_cpython": _median_float(speedups),
            "families": sorted({str(workload["family"]) for workload in manifest_workloads}),
            "operations": sorted({str(workload["operation"]) for workload in manifest_workloads}),
            "selection_mode": selection_mode,
            "smoke_workload_ids": smoke_workload_ids,
            "available_smoke_workload_count": len(smoke_workload_ids),
            "spec_refs": [str(ref) for ref in raw_manifest.get("spec_refs", [])],
            "notes": manifest_notes(raw_manifest, manifest_workloads),
        }

    return summaries


def build_summary(workloads: list[dict[str, Any]]) -> dict[str, Any]:
    parser_speedups = [
        workload["speedup_vs_cpython"]
        for workload in workloads
        if workload["family"] == "parser" and isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    module_speedups = [
        workload["speedup_vs_cpython"]
        for workload in workloads
        if workload["family"] == "module" and isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    all_speedups = [
        workload["speedup_vs_cpython"]
        for workload in workloads
        if isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    baseline_samples = [
        workload["baseline_ns"] for workload in workloads if isinstance(workload.get("baseline_ns"), int)
    ]
    implementation_samples = [
        workload["implementation_ns"]
        for workload in workloads
        if isinstance(workload.get("implementation_ns"), int)
    ]
    known_gap_count = sum(1 for workload in workloads if workload["status"] != "measured")
    baseline_median_ns = _median(baseline_samples)
    implementation_median_ns = _median(implementation_samples)
    return {
        "total_workloads": len(workloads),
        "parser_workloads": sum(1 for workload in workloads if workload["family"] == "parser"),
        "module_workloads": sum(1 for workload in workloads if workload["family"] == "module"),
        "regression_workloads": sum(
            1 for workload in workloads if workload["manifest_id"] == "regression-matrix"
        ),
        "measured_workloads": len(all_speedups),
        "known_gap_count": known_gap_count,
        "baseline_median_ns": baseline_median_ns,
        "baseline_median_ops_per_second": ns_to_ops_per_second(baseline_median_ns),
        "implementation_median_ns": implementation_median_ns,
        "implementation_median_ops_per_second": ns_to_ops_per_second(implementation_median_ns),
        "median_speedup_vs_baseline": _median_float(all_speedups),
        "geomean_speedup_vs_baseline": _geomean(all_speedups),
        "parser_median_speedup_vs_cpython": _median_float(parser_speedups),
        "module_median_speedup_vs_cpython": _median_float(module_speedups),
        "workloads_by_cache_mode": {
            cache_mode: sum(1 for workload in workloads if workload["cache_mode"] == cache_mode)
            for cache_mode in ("cold", "warm", "purged")
        },
    }


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def cpu_model() -> str:
    cpuinfo_path = pathlib.Path("/proc/cpuinfo")
    if cpuinfo_path.is_file():
        for line in cpuinfo_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name"):
                _, _, value = line.partition(":")
                return value.strip()
    return platform.processor() or "unknown"


def determine_phase(workloads: list[dict[str, Any]]) -> str:
    if any(workload["manifest_id"] == "regression-matrix" for workload in workloads):
        return "phase3-regression-stability-suite"
    if any(workload["family"] == "module" for workload in workloads):
        return "phase2-module-boundary-suite"
    return "phase1-compile-path-suite"


def determine_runner_version(workloads: list[dict[str, Any]]) -> str:
    if any(workload["manifest_id"] == "regression-matrix" for workload in workloads):
        return "phase3"
    if any(workload["family"] == "module" for workload in workloads):
        return "phase2"
    return "phase1"


def probe_loaded_rebar_metadata(module: Any) -> dict[str, Any]:
    native_loaded = bool(module.native_module_loaded())
    native_module_name = getattr(module, "NATIVE_MODULE_NAME", NATIVE_MODULE_NAME)
    native_scaffold_status = module.native_scaffold_status()
    native_target_cpython_series = module.native_target_cpython_series()
    return {
        "native_module_loaded": native_loaded,
        "native_module_name": native_module_name,
        "native_scaffold_status": native_scaffold_status,
        "native_target_cpython_series": native_target_cpython_series,
    }


def workload_family(workload: dict[str, Any] | Workload) -> str:
    if isinstance(workload, Workload):
        return workload.family
    return str(workload["family"])


def source_tree_metadata(
    *,
    workloads: list[dict[str, Any]] | list[Workload],
    requested_mode: str,
    native_unavailable_reason: str | None,
) -> dict[str, Any]:
    module = load_rebar_module()
    probed = probe_loaded_rebar_metadata(module)
    includes_module_boundary = any(workload_family(workload) == "module" for workload in workloads)
    return {
        "module_name": "rebar",
        "adapter": "rebar.module-surface" if includes_module_boundary else "rebar.compile",
        "adapter_mode_requested": requested_mode,
        "adapter_mode_resolved": SOURCE_TREE_SHIM_MODE,
        "build_mode": SOURCE_TREE_SHIM_MODE,
        "timing_path": SOURCE_TREE_SHIM_MODE,
        "native_unavailable_reason": native_unavailable_reason,
        "native_build_tool": None,
        "native_wheel": None,
        "git_commit": git_commit(),
        **probed,
    }


def _clean_failure_message(label: str, result: subprocess.CompletedProcess[str]) -> str:
    detail = result.stderr.strip() or result.stdout.strip() or f"{label} failed"
    return f"{label} failed: {detail}"


def _pythonpath_env(entries: list[pathlib.Path]) -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = os.pathsep.join(str(entry) for entry in entries)
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath = os.pathsep.join((pythonpath, existing_pythonpath))
    env["PYTHONPATH"] = pythonpath
    return env


def _native_runtime_failure(
    temp_dir: tempfile.TemporaryDirectory,
    reason: str,
) -> tuple[None, None, str]:
    temp_dir.cleanup()
    return None, None, reason


def provision_built_native_runtime() -> tuple[dict[str, Any] | None, tempfile.TemporaryDirectory | None, str | None]:
    maturin = shutil.which("maturin")
    if maturin is None:
        return None, None, "built-native mode unavailable because no `maturin` executable was found on PATH"

    temp_dir = tempfile.TemporaryDirectory(prefix="rebar-bench-native-")
    temp_root = pathlib.Path(temp_dir.name)
    wheelhouse = temp_root / "wheelhouse"
    install_root = temp_root / "site-packages"
    wheelhouse.mkdir(parents=True, exist_ok=True)
    install_root.mkdir(parents=True, exist_ok=True)

    build_result = subprocess.run(
        [
            maturin,
            "build",
            "--manifest-path",
            "crates/rebar-cpython/Cargo.toml",
            "--interpreter",
            sys.executable,
            "--out",
            str(wheelhouse),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if build_result.returncode != 0:
        return _native_runtime_failure(
            temp_dir,
            _clean_failure_message("maturin build", build_result),
        )

    wheels = sorted(wheelhouse.glob("rebar-*.whl"))
    if len(wheels) != 1:
        return _native_runtime_failure(
            temp_dir,
            f"built-native mode unavailable because wheel build produced {len(wheels)} rebar wheels",
        )

    install_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(install_root),
            str(wheels[0]),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if install_result.returncode != 0:
        return _native_runtime_failure(
            temp_dir,
            _clean_failure_message("pip install --target", install_result),
        )

    probe_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rebar_harness.benchmarks",
            "--internal-probe-rebar-metadata",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=_pythonpath_env([install_root, PYTHON_SOURCE]),
    )
    if probe_result.returncode != 0:
        return _native_runtime_failure(
            temp_dir,
            _clean_failure_message("native metadata probe", probe_result),
        )

    probed = json.loads(probe_result.stdout)
    if not probed.get("native_module_loaded", False):
        return _native_runtime_failure(
            temp_dir,
            "built-native mode unavailable because the installed wheel did not load `rebar._rebar`",
        )

    return {
        "install_root": install_root,
        "maturin_path": pathlib.Path(maturin),
        "wheel_name": wheels[0].name,
        "probe": probed,
    }, temp_dir, None


def prepare_benchmark_run(
    *,
    workloads: list[Workload],
    adapter_mode: str,
    allow_fallback: bool = True,
) -> BenchmarkRunContext:
    requested_mode = adapter_mode
    if adapter_mode == BUILT_NATIVE_MODE:
        provisioned, temp_dir, native_error = provision_built_native_runtime()
        if provisioned is not None and temp_dir is not None:
            includes_module_boundary = any(workload.family == "module" for workload in workloads)
            probe = provisioned["probe"]
            return BenchmarkRunContext(
                requested_mode=BUILT_NATIVE_MODE,
                resolved_mode=BUILT_NATIVE_MODE,
                baseline_adapter=SubprocessBenchmarkAdapter(
                    adapter_name="cpython.re",
                    import_name="re",
                    python_executable=pathlib.Path(sys.executable),
                    pythonpath_entries=[PYTHON_SOURCE],
                ),
                implementation_adapter=SubprocessBenchmarkAdapter(
                    adapter_name="rebar",
                    import_name="rebar",
                    python_executable=pathlib.Path(sys.executable),
                    pythonpath_entries=[provisioned["install_root"], PYTHON_SOURCE],
                ),
                implementation_metadata={
                    "module_name": "rebar",
                    "adapter": "rebar.module-surface" if includes_module_boundary else "rebar.compile",
                    "adapter_mode_requested": BUILT_NATIVE_MODE,
                    "adapter_mode_resolved": BUILT_NATIVE_MODE,
                    "build_mode": BUILT_NATIVE_MODE,
                    "timing_path": BUILT_NATIVE_MODE,
                    "native_unavailable_reason": None,
                    "native_build_tool": "maturin",
                    "native_wheel": provisioned["wheel_name"],
                    "git_commit": git_commit(),
                    **probe,
                },
                execution_model="single-interpreter subprocess workload probes against a built native wheel",
                cleanup=temp_dir.cleanup,
            )
        if not allow_fallback:
            raise NativeBenchmarkProvisionError(
                native_error or "built-native mode unavailable for the requested benchmark run"
            )
        native_unavailable_reason = native_error
    else:
        native_unavailable_reason = (
            "built-native timing path not requested; using the default source-tree shim"
        )

    return BenchmarkRunContext(
        requested_mode=requested_mode,
        resolved_mode=SOURCE_TREE_SHIM_MODE,
        baseline_adapter=CpythonReBenchmarkAdapter(),
        implementation_adapter=RebarBenchmarkAdapter(load_rebar_module()),
        implementation_metadata=source_tree_metadata(
            workloads=workloads,
            requested_mode=requested_mode,
            native_unavailable_reason=native_unavailable_reason,
        ),
        execution_model="single-process in-process adapter comparison",
        cleanup=lambda: None,
    )


def build_deferred_sections(workloads: list[dict[str, Any]]) -> list[dict[str, str]]:
    deferred: list[dict[str, str]] = []
    if not any(workload["family"] == "module" for workload in workloads):
        deferred.append(
            {
                "area": "module-boundary",
                "reason": "Phase 1 benchmark suite measures compile-path workloads only.",
                "follow_up": "RBR-0015",
            }
        )
    deferred.append(
        {
            "area": "regex-execution-throughput",
            "reason": "Execution benchmarks stay deferred until parser and module-boundary harnesses exist.",
            "follow_up": "future milestone",
        }
    )
    return deferred


def build_artifacts(
    *,
    manifest_paths: list[pathlib.Path],
    raw_manifests: list[dict[str, Any]],
    selection_mode: str,
) -> dict[str, Any]:
    manifest_records = [
        {
            "manifest": str(path.relative_to(REPO_ROOT)),
            "manifest_id": raw_manifest["manifest_id"],
            "manifest_schema_version": raw_manifest["schema_version"],
            "workload_count": len(raw_manifest.get("workloads", [])),
            "smoke_workload_ids": [
                str(workload["id"])
                for workload in raw_manifest.get("workloads", [])
                if bool(workload.get("smoke", False) or "smoke" in workload.get("categories", []))
            ],
            "spec_refs": [str(ref) for ref in raw_manifest.get("spec_refs", [])],
        }
        for path, raw_manifest in zip(manifest_paths, raw_manifests, strict=True)
    ]
    if len(manifest_records) == 1:
        return {
            **manifest_records[0],
            "manifests": manifest_records,
            "raw_samples": None,
            "selection_mode": selection_mode,
        }
    return {
        "manifest": None,
        "manifest_id": "combined-benchmark-suite",
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "manifests": manifest_records,
        "raw_samples": None,
        "selection_mode": selection_mode,
    }


def run_internal_workload_probe(
    *,
    workload_payload: str,
    import_name: str,
    adapter_name: str,
) -> dict[str, Any]:
    workload = workload_from_payload(json.loads(workload_payload))
    try:
        module = cpython_re if import_name == "re" else load_module(import_name)
        callback = build_callable(module, import_name, workload)
        timing = measure_callable(workload, callback)
    except NotImplementedError as exc:
        return {
            "adapter": adapter_name,
            "status": "unimplemented",
            "reason": str(exc),
        }
    except Exception as exc:
        return {
            "adapter": adapter_name,
            "status": "unavailable",
            "reason": f"{type(exc).__name__}: {exc}",
        }
    return {"adapter": adapter_name, **timing}


def run_internal_rebar_metadata_probe() -> dict[str, Any]:
    module = load_rebar_module()
    return {
        "module_name": "rebar",
        **probe_loaded_rebar_metadata(module),
    }


def build_scorecard(
    *,
    manifest_paths: list[pathlib.Path],
    raw_manifests: list[dict[str, Any]],
    workloads: list[dict[str, Any]],
    selection_mode: str,
    implementation_metadata: dict[str, Any],
    execution_model: str,
) -> dict[str, Any]:
    summary = build_summary(workloads)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "suite": "benchmarks",
        "phase": determine_phase(workloads),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "python -m rebar_harness.benchmarks",
        "baseline": build_cpython_baseline(version_family=TARGET_CPYTHON_SERIES),
        "implementation": implementation_metadata,
        "environment": {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "cpu_model": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "runner": "perf_counter_ns",
            "runner_version": determine_runner_version(workloads),
            "execution_model": execution_model,
        },
        "summary": summary,
        "manifests": build_manifest_summaries(
            raw_manifests=raw_manifests,
            workloads=workloads,
            selection_mode=selection_mode,
        ),
        "families": {
            "parser": build_family_summary(workloads, "parser"),
            "module": build_family_summary(workloads, "module"),
        },
        "cache_modes": build_cache_mode_summary(workloads),
        "workloads": workloads,
        "deferred": build_deferred_sections(workloads),
        "artifacts": build_artifacts(
            manifest_paths=manifest_paths,
            raw_manifests=raw_manifests,
            selection_mode=selection_mode,
        ),
    }


def validate_report_path(report_path: pathlib.Path) -> pathlib.Path:
    return validate_scorecard_report_path(
        report_path,
        legacy_path=LEGACY_REPORT_PATH,
        legacy_path_error=LEGACY_REPORT_PATH_ERROR,
    )


def load_scorecard(report_path: pathlib.Path) -> dict[str, Any]:
    return load_scorecard_report(
        report_path,
        module_name_prefix="_rebar_benchmark_scorecard",
        report_attribute=REPORT_ATTRIBUTE,
        scorecard_kind="benchmark",
    )


def write_scorecard(scorecard: dict[str, Any], report_path: pathlib.Path) -> None:
    report_path = validate_report_path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    write_scorecard_report(
        scorecard,
        report_path,
        report_attribute=REPORT_ATTRIBUTE,
        scorecard_kind="benchmark",
    )


def remove_legacy_report_sidecar() -> bool:
    return remove_scorecard_sidecar(LEGACY_REPORT_PATH)


def run_benchmarks(
    manifest_paths: list[pathlib.Path] | None = None,
    report_path: pathlib.Path | None = DEFAULT_REPORT_PATH,
    *,
    smoke_only: bool = False,
    adapter_mode: str = SOURCE_TREE_SHIM_MODE,
    allow_fallback: bool = True,
) -> dict[str, Any]:
    resolved_manifest_paths = [
        path.resolve() for path in (manifest_paths or list(DEFAULT_MANIFEST_PATHS))
    ]
    resolved_report_path = (
        validate_report_path(report_path) if report_path is not None else None
    )
    raw_manifests, manifest_workloads = load_manifests(resolved_manifest_paths)
    selected_manifest_workloads = select_workloads(manifest_workloads, smoke_only=smoke_only)
    run_context = prepare_benchmark_run(
        workloads=selected_manifest_workloads,
        adapter_mode=adapter_mode,
        allow_fallback=allow_fallback,
    )
    try:
        workloads = [
            evaluate_workload(
                workload,
                run_context.baseline_adapter,
                run_context.implementation_adapter,
            )
            for workload in selected_manifest_workloads
        ]
        scorecard = build_scorecard(
            manifest_paths=resolved_manifest_paths,
            raw_manifests=raw_manifests,
            workloads=workloads,
            selection_mode="smoke" if smoke_only else "full",
            implementation_metadata=run_context.implementation_metadata,
            execution_model=run_context.execution_model,
        )
        if resolved_report_path is not None:
            write_scorecard(scorecard, resolved_report_path)
            if resolved_report_path == DEFAULT_REPORT_PATH:
                remove_legacy_report_sidecar()
        return scorecard
    finally:
        run_context.cleanup()


def run_built_native_smoke_benchmarks(
    report_path: pathlib.Path | None = None,
) -> dict[str, Any]:
    return run_benchmarks(
        manifest_paths=list(DEFAULT_NATIVE_SMOKE_MANIFEST_PATHS),
        report_path=report_path,
        smoke_only=True,
        adapter_mode=BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def run_built_native_full_benchmarks(
    report_path: pathlib.Path | None = None,
) -> dict[str, Any]:
    return run_benchmarks(
        manifest_paths=list(DEFAULT_MANIFEST_PATHS),
        report_path=report_path,
        smoke_only=False,
        adapter_mode=BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        action="append",
        default=None,
        help="Path to a benchmark workload manifest. Repeat to combine multiple manifests.",
    )
    parser.add_argument(
        "--report",
        type=pathlib.Path,
        default=None,
        help=(
            "Path to the output scorecard. Ordinary runs default to "
            "`reports/benchmarks/latest.py`; explicit `.py` and temporary `.json` outputs "
            "remain supported, and strict built-native modes only write a report when you pass "
            "this flag explicitly."
        ),
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run only workloads tagged as smoke within the selected manifests.",
    )
    parser.add_argument(
        "--adapter-mode",
        choices=(SOURCE_TREE_SHIM_MODE, BUILT_NATIVE_MODE),
        default=SOURCE_TREE_SHIM_MODE,
        help=(
            "Benchmark the source-tree shim or provision a built native wheel when possible. "
            "The default keeps the existing source-tree shim path."
        ),
    )
    parser.add_argument(
        "--native-smoke",
        action="store_true",
        help=(
            "Run the dedicated built-native smoke slice against the tracked smoke manifests. "
            "This mode requires a real built native wheel and returns an in-memory scorecard "
            "unless you pass --report."
        ),
    )
    parser.add_argument(
        "--native-full",
        action="store_true",
        help=(
            "Run the full combined benchmark suite against a real built native wheel. "
            "This mode requires a real built native wheel and returns an in-memory scorecard "
            "unless you pass --report."
        ),
    )
    parser.add_argument(
        "--internal-run-workload",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--internal-import-name",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--internal-adapter-name",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--internal-probe-rebar-metadata",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.internal_probe_rebar_metadata:
        print(json.dumps(run_internal_rebar_metadata_probe(), sort_keys=True))
        return 0
    if args.internal_run_workload is not None:
        if args.internal_import_name is None or args.internal_adapter_name is None:
            raise SystemExit(
                "--internal-run-workload requires --internal-import-name and --internal-adapter-name"
            )
        print(
            json.dumps(
                run_internal_workload_probe(
                    workload_payload=args.internal_run_workload,
                    import_name=args.internal_import_name,
                    adapter_name=args.internal_adapter_name,
                ),
                sort_keys=True,
            )
        )
        return 0
    if args.native_smoke and args.native_full:
        raise SystemExit("--native-smoke and --native-full are mutually exclusive")
    try:
        if args.native_smoke:
            if args.manifest is not None:
                raise SystemExit("--native-smoke cannot be combined with --manifest")
            if args.smoke:
                raise SystemExit("--native-smoke already implies smoke-only selection")
            if args.adapter_mode != SOURCE_TREE_SHIM_MODE:
                raise SystemExit("--native-smoke manages adapter selection itself")
            scorecard = run_built_native_smoke_benchmarks(report_path=args.report)
        elif args.native_full:
            if args.manifest is not None:
                raise SystemExit("--native-full cannot be combined with --manifest")
            if args.smoke:
                raise SystemExit("--native-full runs the full suite and cannot be combined with --smoke")
            if args.adapter_mode != SOURCE_TREE_SHIM_MODE:
                raise SystemExit("--native-full manages adapter selection itself")
            scorecard = run_built_native_full_benchmarks(report_path=args.report)
        else:
            scorecard = run_benchmarks(
                manifest_paths=args.manifest,
                report_path=args.report or DEFAULT_REPORT_PATH,
                smoke_only=args.smoke,
                adapter_mode=args.adapter_mode,
            )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    smoke_summary = {
        "total_workloads": scorecard["summary"]["total_workloads"],
        "parser_workloads": scorecard["summary"]["parser_workloads"],
        "module_workloads": scorecard["summary"]["module_workloads"],
        "regression_workloads": scorecard["summary"]["regression_workloads"],
        "measured_workloads": scorecard["summary"]["measured_workloads"],
        "known_gap_count": scorecard["summary"]["known_gap_count"],
    }
    print(json.dumps(smoke_summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
