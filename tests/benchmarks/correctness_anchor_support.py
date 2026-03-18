from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
import pathlib
import re
from typing import Any

from rebar_harness.benchmarks import build_callable, load_manifest
from rebar_harness.correctness import published_fixture_manifests
from tests.python.fixture_parity_support import (
    assert_match_result_parity,
    assert_pattern_parity,
)


@dataclass(frozen=True, slots=True)
class AnchoredWorkloadCasePair:
    manifest_name: str
    workload_id: str
    case_id: str
    workload: Any
    case: Any


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
def published_case_ids_by_signature(
    case_signature: Callable[[Any], tuple[Any, ...] | None],
) -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for manifest in published_fixture_manifests():
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

    for manifest in published_fixture_manifests():
        for case in manifest.cases:
            if case.case_id in cases_by_id:
                raise AssertionError(
                    f"duplicate published correctness case id {case.case_id!r}"
                )
            cases_by_id[case.case_id] = case

    return cases_by_id


@cache
def _manifest_workloads(manifest_path: pathlib.Path) -> tuple[Any, ...]:
    return tuple(load_manifest(manifest_path).workloads)


def anchored_workload_case_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = _manifest_workloads(manifest_path)

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
    workloads = _manifest_workloads(manifest_path)

    return tuple(
        workload.workload_id
        for workload in workloads
        if (include_workload is None or include_workload(workload))
        and workload_signature(workload) not in anchor_case_ids
    )


def expected_anchored_workload_case_pairs(
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[AnchoredWorkloadCasePair, ...]:
    manifest_name = manifest_path.name
    workloads_by_id = {
        workload.workload_id: workload
        for workload in _manifest_workloads(manifest_path)
        if include_workload is None or include_workload(workload)
    }
    published_cases = published_cases_by_id()
    anchored_pairs: list[AnchoredWorkloadCasePair] = []

    for (expected_manifest_name, workload_id), case_ids in expected_anchor_case_ids.items():
        if expected_manifest_name != manifest_name:
            raise AssertionError(
                f"expected anchored manifest {expected_manifest_name!r} "
                f"does not match {manifest_name!r}"
            )
        if len(case_ids) != 1:
            raise AssertionError(
                "expected exactly one published correctness case for "
                f"{(expected_manifest_name, workload_id)!r}, got {case_ids!r}"
            )

        case_id = case_ids[0]
        if workload_id not in workloads_by_id:
            raise AssertionError(
                f"expected anchored workload {workload_id!r} to be in scope for "
                f"{manifest_name!r}"
            )
        if case_id not in published_cases:
            raise AssertionError(
                f"expected anchored correctness case {case_id!r} to be published"
            )

        anchored_pairs.append(
            AnchoredWorkloadCasePair(
                manifest_name=manifest_name,
                workload_id=workload_id,
                case_id=case_id,
                workload=workloads_by_id[workload_id],
                case=published_cases[case_id],
            )
        )

    return tuple(anchored_pairs)


def assert_anchored_workload_case_result_parity(
    anchored_pairs: Iterable[AnchoredWorkloadCasePair],
) -> None:
    for anchored_pair in anchored_pairs:
        expected = run_correctness_case_with_cpython(anchored_pair.case)
        assert_benchmark_workload_matches_expected_result(
            anchored_pair.workload,
            expected,
        )


def assert_benchmark_workload_matches_expected_result(
    workload: Any,
    expected: object,
) -> None:
    observed = run_benchmark_workload_with_cpython(workload)

    if workload.operation == "module.compile":
        assert_pattern_parity("stdlib", observed, expected)
        return

    if workload.operation in {"module.search", "pattern.fullmatch"}:
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )
        return

    if workload.operation in {
        "module.sub",
        "module.subn",
        "pattern.sub",
        "pattern.subn",
    }:
        assert observed == expected
        return

    raise AssertionError(
        "unexpected anchored benchmark workload operation "
        f"{workload.operation!r}"
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
