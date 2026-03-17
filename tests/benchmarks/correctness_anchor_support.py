from __future__ import annotations

from collections.abc import Callable
from functools import cache
import pathlib
import re
from typing import Any

from rebar_harness.benchmarks import build_callable, load_manifest
from rebar_harness.correctness import (
    DEFAULT_FIXTURE_PATHS,
    FixtureManifest,
    load_fixture_manifests,
)


def freeze_signature_value(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(
            (str(key), freeze_signature_value(nested_value))
            for key, nested_value in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(freeze_signature_value(item) for item in value)
    return value


@cache
def _published_fixture_inventory() -> tuple[FixtureManifest, ...]:
    return tuple(load_fixture_manifests(DEFAULT_FIXTURE_PATHS))


@cache
def published_case_ids_by_signature(
    case_signature: Callable[[Any], tuple[Any, ...] | None],
) -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for manifest in _published_fixture_inventory():
        for case in manifest.cases:
            signature = case_signature(case)
            if signature is None:
                continue
            case_ids_by_signature.setdefault(signature, []).append(case.case_id)

    return {
        signature: tuple(sorted(case_ids))
        for signature, case_ids in case_ids_by_signature.items()
    }


@cache
def published_cases_by_id() -> dict[str, Any]:
    cases_by_id: dict[str, Any] = {}

    for manifest in _published_fixture_inventory():
        for case in manifest.cases:
            if case.case_id in cases_by_id:
                raise AssertionError(
                    f"duplicate published correctness case id {case.case_id!r}"
                )
            cases_by_id[case.case_id] = case

    return cases_by_id


def anchored_workload_case_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = load_manifest(manifest_path).workloads

    return {
        (manifest_path.name, workload.workload_id): anchor_case_ids.get(
            workload_signature(workload),
            (),
        )
        for workload in workloads
        if include_workload is None or include_workload(workload)
    }


def unanchored_workload_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[str, ...]:
    workloads = load_manifest(manifest_path).workloads

    return tuple(
        workload.workload_id
        for workload in workloads
        if (include_workload is None or include_workload(workload))
        and workload_signature(workload) not in anchor_case_ids
    )


def run_benchmark_workload_with_cpython(workload: Any) -> object:
    re.purge()
    callback = build_callable(re, "re", workload)
    result = callback()
    re.purge()
    return result


def run_correctness_case_with_cpython(case: Any) -> object:
    if case.operation == "compile":
        return re.compile(case.pattern_payload(), case.flags or 0)

    if case.operation == "module_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        return getattr(re, case.helper)(*case.args, **case.kwargs)

    if case.operation == "pattern_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        compiled = re.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise AssertionError(f"unexpected correctness operation {case.operation!r}")
