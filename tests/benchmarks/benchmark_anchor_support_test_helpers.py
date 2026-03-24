from __future__ import annotations

import pathlib
from types import SimpleNamespace
from typing import Any

import pytest

from tests.benchmarks import benchmark_test_support
from tests.benchmarks import source_tree_benchmark_anchor_support as anchor_support


_ANCHOR_SUPPORT_CACHED_FUNCTIONS = (
    benchmark_test_support.manifest_workloads,
    benchmark_test_support._live_manifest_workloads_by_id,
    anchor_support.published_case_ids_by_signature,
    anchor_support.published_cases_by_id,
)


def _clear_anchor_support_caches() -> None:
    for cached_function in _ANCHOR_SUPPORT_CACHED_FUNCTIONS:
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()


@pytest.fixture
def anchor_support_cache_guard() -> None:
    _clear_anchor_support_caches()
    yield
    _clear_anchor_support_caches()


def _synthetic_manifest(
    *,
    cases: tuple[object, ...] = (),
    workloads: tuple[object, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(cases=list(cases), workloads=list(workloads))


def _synthetic_case(
    case_id: str,
    signature: tuple[Any, ...] | None,
) -> SimpleNamespace:
    return SimpleNamespace(case_id=case_id, signature=signature)


def _synthetic_workload(
    workload_id: str,
    signature: tuple[Any, ...],
    *,
    include: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(workload_id=workload_id, signature=signature, include=include)


def _synthetic_manifest_loader(
    _: pathlib.Path,
    *,
    workloads: tuple[Any, ...],
) -> SimpleNamespace:
    return _synthetic_manifest(workloads=workloads)


def _synthetic_workload_signature(workload: Any) -> tuple[Any, ...]:
    return workload.signature


def _synthetic_workload_is_included(workload: Any) -> bool:
    return workload.include
