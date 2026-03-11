"""Benchmark harness for compile-path and module-boundary workload suites."""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import pathlib
import platform
import re as cpython_re
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

import rebar
from rebar_harness.metadata import build_cpython_baseline


TARGET_CPYTHON_SERIES = "3.12.x"
REPORT_SCHEMA_VERSION = "1.0"
MANIFEST_SCHEMA_VERSION = 1
DEFAULT_MANIFEST_PATHS = (
    REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.json",
    REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.json",
)
DEFAULT_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


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
    flags: int
    text_model: str
    cache_mode: str
    timing_scope: str
    warmup_iterations: int
    sample_iterations: int
    timed_samples: int
    notes: list[str]
    categories: list[str]
    syntax_features: list[str]

    @classmethod
    def from_dict(
        cls,
        *,
        manifest_id: str,
        raw_workload: dict[str, Any],
        defaults: dict[str, Any],
    ) -> "Workload":
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
            flags=int(raw_workload.get("flags", 0)),
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
            categories=[str(category) for category in raw_workload.get("categories", [])],
            syntax_features=[
                str(feature)
                for feature in raw_workload.get("syntax_features", raw_workload.get("categories", []))
            ],
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


def load_manifest(path: pathlib.Path) -> tuple[dict[str, Any], list[Workload]]:
    raw_manifest = json.loads(path.read_text(encoding="utf-8"))
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


class BenchmarkAdapter:
    """Adapter boundary for benchmarkable workloads."""

    adapter_name: str
    import_name: str
    module: Any

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        raise NotImplementedError


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


def helper_callable(module: Any, workload: Workload, helper_name: str) -> Any:
    pattern = workload.pattern_payload()
    haystack = workload.haystack_payload()
    helper = getattr(module, helper_name)

    def invoke() -> object:
        return helper(pattern, haystack, workload.flags)

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


def build_callable(module: Any, import_name: str, workload: Workload) -> Any:
    if workload.operation == "import":
        return import_callable(import_name, workload)
    if workload.operation in {"compile", "module.compile"}:
        return compile_callable(module, workload)
    if workload.operation == "module.search":
        return helper_callable(module, workload, "search")
    if workload.operation == "module.match":
        return helper_callable(module, workload, "match")
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
    module = rebar

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
        return "Implementation timing is unavailable until the rebar compile surface exists."
    if workload.operation == "import":
        return "Implementation import timing is unavailable until the rebar package can be imported in the benchmark environment."
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
        "flags": workload.flags,
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
    if any(workload["family"] == "module" for workload in workloads):
        return "phase2-module-boundary-suite"
    return "phase1-compile-path-suite"


def determine_runner_version(workloads: list[dict[str, Any]]) -> str:
    if any(workload["family"] == "module" for workload in workloads):
        return "phase2"
    return "phase1"


def build_implementation_metadata(workloads: list[dict[str, Any]]) -> dict[str, Any]:
    native_loaded = rebar.native_module_loaded()
    includes_module_boundary = any(workload["family"] == "module" for workload in workloads)
    return {
        "module_name": "rebar",
        "adapter": "rebar.module-surface" if includes_module_boundary else "rebar.compile",
        "build_mode": "native-extension" if native_loaded else "source-tree-shim",
        "timing_path": "native-extension" if native_loaded else "source-tree-shim",
        "native_module_loaded": native_loaded,
        "native_module_name": rebar.NATIVE_MODULE_NAME,
        "native_scaffold_status": rebar.native_scaffold_status(),
        "native_target_cpython_series": rebar.native_target_cpython_series(),
        "git_commit": git_commit(),
    }


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
) -> dict[str, Any]:
    manifest_records = [
        {
            "manifest": str(path.relative_to(REPO_ROOT)),
            "manifest_id": raw_manifest["manifest_id"],
            "manifest_schema_version": raw_manifest["schema_version"],
            "workload_count": len(raw_manifest.get("workloads", [])),
        }
        for path, raw_manifest in zip(manifest_paths, raw_manifests, strict=True)
    ]
    if len(manifest_records) == 1:
        return {
            **manifest_records[0],
            "manifests": manifest_records,
            "raw_samples": None,
        }
    return {
        "manifest": None,
        "manifest_id": "combined-benchmark-suite",
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "manifests": manifest_records,
        "raw_samples": None,
    }


def build_scorecard(
    *,
    manifest_paths: list[pathlib.Path],
    raw_manifests: list[dict[str, Any]],
    workloads: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = build_summary(workloads)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "suite": "benchmarks",
        "phase": determine_phase(workloads),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "python -m rebar_harness.benchmarks",
        "baseline": build_cpython_baseline(version_family=TARGET_CPYTHON_SERIES),
        "implementation": build_implementation_metadata(workloads),
        "environment": {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "cpu_model": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "runner": "perf_counter_ns",
            "runner_version": determine_runner_version(workloads),
            "execution_model": "single-process in-process adapter comparison",
        },
        "summary": summary,
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
        ),
    }


def write_scorecard(scorecard: dict[str, Any], report_path: pathlib.Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_benchmarks(
    manifest_paths: list[pathlib.Path] | None = None,
    report_path: pathlib.Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    resolved_manifest_paths = [
        path.resolve() for path in (manifest_paths or list(DEFAULT_MANIFEST_PATHS))
    ]
    report_path = report_path.resolve()
    raw_manifests, manifest_workloads = load_manifests(resolved_manifest_paths)
    baseline_adapter = CpythonReBenchmarkAdapter()
    implementation_adapter = RebarBenchmarkAdapter()
    workloads = [
        evaluate_workload(workload, baseline_adapter, implementation_adapter)
        for workload in manifest_workloads
    ]
    scorecard = build_scorecard(
        manifest_paths=resolved_manifest_paths,
        raw_manifests=raw_manifests,
        workloads=workloads,
    )
    write_scorecard(scorecard, report_path)
    return scorecard


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
        default=DEFAULT_REPORT_PATH,
        help="Path to the output JSON scorecard.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    scorecard = run_benchmarks(manifest_paths=args.manifest, report_path=args.report)
    smoke_summary = {
        "total_workloads": scorecard["summary"]["total_workloads"],
        "parser_workloads": scorecard["summary"]["parser_workloads"],
        "module_workloads": scorecard["summary"]["module_workloads"],
        "measured_workloads": scorecard["summary"]["measured_workloads"],
        "known_gap_count": scorecard["summary"]["known_gap_count"],
    }
    print(json.dumps(smoke_summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
