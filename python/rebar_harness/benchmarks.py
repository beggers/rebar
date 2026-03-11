"""Phase 0 benchmark harness for compile-oriented smoke workloads."""

from __future__ import annotations

import argparse
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
DEFAULT_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_smoke.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


@dataclass(frozen=True)
class Workload:
    """Single benchmark workload definition."""

    workload_id: str
    family: str
    operation: str
    pattern: str
    flags: int
    text_model: str
    cache_mode: str
    warmup_iterations: int
    sample_iterations: int
    timed_samples: int
    notes: list[str]
    categories: list[str]

    @classmethod
    def from_dict(cls, raw_workload: dict[str, Any], defaults: dict[str, Any]) -> "Workload":
        return cls(
            workload_id=str(raw_workload["id"]),
            family=str(raw_workload.get("family", "parser")),
            operation=str(raw_workload["operation"]),
            pattern=str(raw_workload["pattern"]),
            flags=int(raw_workload.get("flags", 0)),
            text_model=str(raw_workload.get("text_model", "str")),
            cache_mode=str(raw_workload.get("cache_mode", "cold")),
            warmup_iterations=int(
                raw_workload.get("warmup_iterations", defaults.get("warmup_iterations", 2))
            ),
            sample_iterations=int(
                raw_workload.get("sample_iterations", defaults.get("sample_iterations", 1))
            ),
            timed_samples=int(raw_workload.get("timed_samples", defaults.get("timed_samples", 5))),
            notes=[str(note) for note in raw_workload.get("notes", [])],
            categories=[str(category) for category in raw_workload.get("categories", [])],
        )

    def pattern_payload(self) -> str | bytes:
        if self.text_model == "str":
            return self.pattern
        if self.text_model == "bytes":
            return self.pattern.encode("utf-8")
        raise ValueError(f"unsupported text model {self.text_model!r}")


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

    workloads = [
        Workload.from_dict(raw_workload, defaults) for raw_workload in raw_manifest.get("workloads", [])
    ]
    return raw_manifest, workloads


class BenchmarkAdapter:
    """Adapter boundary for benchmarkable compile workloads."""

    adapter_name: str

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        raise NotImplementedError


def compile_callable(module: Any, workload: Workload) -> Any:
    pattern = workload.pattern_payload()

    if workload.operation != "compile":
        raise ValueError(f"unsupported benchmark operation {workload.operation!r}")

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

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        callback = compile_callable(cpython_re, workload)
        timing = measure_callable(workload, callback)
        return {"adapter": self.adapter_name, **timing}


class RebarBenchmarkAdapter(BenchmarkAdapter):
    adapter_name = "rebar"

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        try:
            callback = compile_callable(rebar, workload)
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


def calculate_speedup(baseline_timing: dict[str, Any], implementation_timing: dict[str, Any]) -> float | None:
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
        notes.append(
            "Implementation timing is unavailable until the rebar compile surface exists."
        )

    return {
        "id": workload.workload_id,
        "family": workload.family,
        "operation": workload.operation,
        "cache_mode": workload.cache_mode,
        "text_model": workload.text_model,
        "pattern": workload.pattern,
        "flags": workload.flags,
        "categories": workload.categories,
        "status": status,
        "baseline_ns": baseline_timing.get("median_ns"),
        "implementation_ns": implementation_timing.get("median_ns"),
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
    readiness = "measured" if known_gap_count == 0 and family_workloads else "scaffold-only"

    return {
        "workload_count": len(family_workloads),
        "known_gap_count": known_gap_count,
        "readiness": readiness,
        "median_baseline_ns": _median(baseline_samples),
        "median_implementation_ns": _median(implementation_samples),
        "median_speedup_vs_cpython": _median_float(speedups),
        "notes": (
            ["Phase 0 scaffold currently covers compile-path proxy workloads only."]
            if family == "parser"
            else ["Phase 0 scaffold defers module-boundary timings."]
        ),
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
    known_gap_count = sum(1 for workload in workloads if workload["status"] != "measured")
    return {
        "total_workloads": len(workloads),
        "parser_workloads": sum(1 for workload in workloads if workload["family"] == "parser"),
        "module_workloads": sum(1 for workload in workloads if workload["family"] == "module"),
        "measured_workloads": len(all_speedups),
        "known_gap_count": known_gap_count,
        "median_speedup_vs_baseline": _median_float(all_speedups),
        "geomean_speedup_vs_baseline": _geomean(all_speedups),
        "parser_median_speedup_vs_cpython": _median_float(parser_speedups),
        "module_median_speedup_vs_cpython": _median_float(module_speedups),
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


def build_scorecard(
    *,
    manifest_path: pathlib.Path,
    raw_manifest: dict[str, Any],
    workloads: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = build_summary(workloads)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "suite": "benchmarks",
        "phase": "phase0-runner-skeleton",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "python -m rebar_harness.benchmarks",
        "baseline": build_cpython_baseline(version_family=TARGET_CPYTHON_SERIES),
        "implementation": {
            "module_name": "rebar",
            "adapter": "rebar.compile",
            "build_mode": "source-tree-shim",
            "native_module_loaded": rebar.native_module_loaded(),
            "git_commit": git_commit(),
        },
        "environment": {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "cpu_model": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "runner": "perf_counter_ns",
            "runner_version": "phase0",
        },
        "summary": summary,
        "families": {
            "parser": build_family_summary(workloads, "parser"),
            "module": build_family_summary(workloads, "module"),
        },
        "workloads": workloads,
        "deferred": [
            {
                "area": "module-boundary",
                "reason": "Phase 0 benchmark scaffold measures compile-path proxy workloads only.",
                "follow_up": "RBR-0015",
            },
            {
                "area": "regex-execution-throughput",
                "reason": "Execution benchmarks stay deferred until parser and module-boundary harnesses exist.",
                "follow_up": "future milestone",
            },
        ],
        "artifacts": {
            "manifest": str(manifest_path.relative_to(REPO_ROOT)),
            "manifest_id": raw_manifest["manifest_id"],
            "raw_samples": None,
        },
    }


def write_scorecard(scorecard: dict[str, Any], report_path: pathlib.Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_benchmarks(
    manifest_path: pathlib.Path = DEFAULT_MANIFEST_PATH,
    report_path: pathlib.Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    report_path = report_path.resolve()
    raw_manifest, manifest_workloads = load_manifest(manifest_path)
    baseline_adapter = CpythonReBenchmarkAdapter()
    implementation_adapter = RebarBenchmarkAdapter()
    workloads = [
        evaluate_workload(workload, baseline_adapter, implementation_adapter)
        for workload in manifest_workloads
    ]
    scorecard = build_scorecard(
        manifest_path=manifest_path,
        raw_manifest=raw_manifest,
        workloads=workloads,
    )
    write_scorecard(scorecard, report_path)
    return scorecard


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Path to the benchmark workload manifest.",
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
    scorecard = run_benchmarks(manifest_path=args.manifest, report_path=args.report)
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
