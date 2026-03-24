from __future__ import annotations

import pathlib
from types import SimpleNamespace
from typing import Any

import pytest

from tests.benchmarks import source_tree_benchmark_anchor_support as anchor_support


@pytest.fixture
def anchor_support_cache_guard() -> None:
    for cached_function in (
        anchor_support._manifest_workloads,
        anchor_support.published_case_ids_by_signature,
        anchor_support.published_cases_by_id,
    ):
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()
    yield
    for cached_function in (
        anchor_support._manifest_workloads,
        anchor_support.published_case_ids_by_signature,
        anchor_support.published_cases_by_id,
    ):
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()


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


def _single_manifest_tuple(manifest: Any) -> tuple[Any, ...]:
    return (manifest,)


def _synthetic_workload_signature(workload: Any) -> tuple[Any, ...]:
    return workload.signature


def _synthetic_case_signature(case: Any) -> tuple[Any, ...] | None:
    return case.signature


def _synthetic_workload_is_included(workload: Any) -> bool:
    return workload.include
