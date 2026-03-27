from __future__ import annotations

import pathlib
import re
import sys
import textwrap
from functools import cache
from typing import Any

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    load_manifest,
    published_benchmark_manifests,
)
from tests.python.fixture_parity_support import (
    assert_match_result_parity,
    assert_pattern_parity,
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


@cache
def _live_manifest_workloads_by_id(
    manifest_path: pathlib.Path | str,
) -> dict[str, benchmarks.Workload]:
    return {
        workload.workload_id: workload
        for workload in manifest_workloads(manifest_path)
    }


def live_manifest_workload(
    manifest_path: pathlib.Path | str,
    workload_id: str,
) -> benchmarks.Workload:
    return _live_manifest_workloads_by_id(manifest_path)[workload_id]


def live_manifest_workloads(
    manifest_path: pathlib.Path | str,
    workload_ids: tuple[str, ...],
) -> tuple[benchmarks.Workload, ...]:
    workloads_by_id = _live_manifest_workloads_by_id(manifest_path)
    return tuple(workloads_by_id[workload_id] for workload_id in workload_ids)


def _clear_anchor_support_caches() -> None:
    for functions in (
        (
            manifest_workloads,
            _live_manifest_workloads_by_id,
        ),
        vars(benchmark_test_support).values(),
    ):
        for function in functions:
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

def run_benchmark_workload_with_cpython(workload: Any) -> object:
    re.purge()
    callback = benchmarks.build_callable(re, "re", workload)
    result = callback()
    re.purge()
    return result


def assert_benchmark_workload_matches_expected_result(
    workload: Any,
    expected: object,
) -> None:
    observed = run_benchmark_workload_with_cpython(workload)

    if workload.operation == "module.compile":
        assert_pattern_parity("stdlib", observed, expected)
        return

    if workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
    }:
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )
        return

    if workload.operation in {
        "module.split",
        "module.findall",
        "pattern.findall",
        "module.sub",
        "module.subn",
        "pattern.split",
        "pattern.sub",
        "pattern.subn",
    }:
        assert observed == expected
        return

    if workload.operation in {"module.finditer", "pattern.finditer"}:
        assert isinstance(observed, list)
        expected_matches = list(expected)
        assert len(observed) == len(expected_matches)
        for observed_match, expected_match in zip(
            observed,
            expected_matches,
            strict=True,
        ):
            assert_match_result_parity(
                "stdlib",
                observed_match,
                expected_match,
                check_regs=True,
            )
        return

    raise AssertionError(
        "unexpected anchored benchmark workload operation "
        f"{workload.operation!r}"
    )

def _write_test_manifest(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path
