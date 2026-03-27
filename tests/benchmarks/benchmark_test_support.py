from __future__ import annotations

import pathlib
import sys
import textwrap
from functools import cache

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    load_manifest,
)

benchmark_test_support = sys.modules[__name__]


@cache
def manifest_workloads(
    manifest_path: pathlib.Path | str,
) -> tuple[benchmarks.Workload, ...]:
    resolved_manifest_path = (
        manifest_path
        if isinstance(manifest_path, pathlib.Path)
        else benchmarks.BENCHMARK_WORKLOADS_ROOT / manifest_path
    )
    return tuple(load_manifest(resolved_manifest_path).workloads)


def live_manifest_workload(
    manifest_path: pathlib.Path | str,
    workload_id: str,
) -> benchmarks.Workload:
    return next(
        workload
        for workload in manifest_workloads(manifest_path)
        if workload.workload_id == workload_id
    )


def live_manifest_workloads(
    manifest_path: pathlib.Path | str,
    workload_ids: tuple[str, ...],
) -> tuple[benchmarks.Workload, ...]:
    workloads_by_id = {
        workload.workload_id: workload
        for workload in manifest_workloads(manifest_path)
    }
    return tuple(workloads_by_id[workload_id] for workload_id in workload_ids)


def _clear_anchor_support_caches() -> None:
    for function in vars(benchmark_test_support).values():
        cache_clear = getattr(function, "cache_clear", None)
        if callable(cache_clear):
            cache_clear()
    combined_suite = sys.modules.get(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    if combined_suite is not None:
        for function in vars(combined_suite).values():
            cache_clear = getattr(function, "cache_clear", None)
            if callable(cache_clear):
                cache_clear()

def _write_test_manifest(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path
