from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import pathlib
from typing import Any, Protocol

from tests.benchmarks.source_tree_benchmark_anchor_support import (
    anchored_workload_case_ids,
    expected_anchored_workload_case_pairs,
    published_case_ids_by_signature,
    unanchored_workload_ids,
)


class StandardBenchmarkAnchorContract(Protocol):
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    callback_anchor_workload_ids: frozenset[str]
    expected_legacy_workload_ids: frozenset[str]

    def includes_workload(self, workload: Any) -> bool: ...


@dataclass(frozen=True, slots=True)
class StandardBenchmarkAnchorContractDefinition:
    name: str
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    include_workload: Callable[[Any], bool]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    run_callback_result_parity: bool = False
    expected_excluded_workload_ids: frozenset[str] = frozenset()
    expected_legacy_workload_ids: frozenset[str] = frozenset()
    callback_anchor_workload_ids: frozenset[str] = frozenset()
    expected_special_unanchored_workload_ids: tuple[str, ...] = ()
    direct_parity_supplemental_cases: tuple[Any, ...] = ()
    run_special_unanchored_result_parity: bool = False

    def includes_workload(self, workload: Any) -> bool:
        return (
            workload.workload_id not in self.expected_excluded_workload_ids
            and workload.workload_id
            not in self.expected_special_unanchored_workload_ids
            and self.include_workload(workload)
        )


def _definition_anchor_expectations(
    manifest_path: pathlib.Path,
    anchor_expectations: dict[str, tuple[str, ...]],
) -> dict[tuple[str, str], tuple[str, ...]]:
    return {
        (manifest_path.name, workload_id): case_ids
        for workload_id, case_ids in anchor_expectations.items()
    }


def _workload_case_pairs_workload_ids(
    workload_case_pairs: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    return tuple(workload_id for workload_id, _ in workload_case_pairs)


def _workload_case_pairs_case_ids(
    workload_case_pairs: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    return tuple(case_id for _, case_id in workload_case_pairs)


def _workload_case_pair_anchor_expectations(
    manifest_path: pathlib.Path,
    workload_case_pairs: tuple[tuple[str, str], ...],
) -> dict[tuple[str, str], tuple[str, ...]]:
    return _definition_anchor_expectations(
        manifest_path,
        {
            workload_id: (case_id,)
            for workload_id, case_id in workload_case_pairs
        },
    )


def _anchor_case_subset(
    anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
    workload_ids: Iterable[str],
) -> dict[tuple[str, str], tuple[str, ...]]:
    selected_workload_ids = frozenset(workload_ids)
    return {
        key: case_ids
        for key, case_ids in anchor_case_ids.items()
        if key[1] in selected_workload_ids
    }


def _expected_workload_ids(
    definition: StandardBenchmarkAnchorContract,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return tuple(
        workload_id
        for (manifest_name, workload_id), _ in definition.expected_anchor_case_ids.items()
        if manifest_name == manifest_path.name
    )


def _expected_anchor_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContract,
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchor_case_ids = (
        definition.expected_anchor_case_ids
        if expected_anchor_case_ids is None
        else expected_anchor_case_ids
    )
    return {
        (manifest_name, workload_id): case_ids
        for (manifest_name, workload_id), case_ids in anchor_case_ids.items()
        if manifest_name == manifest_path.name
    }


def _anchored_case_ids(
    definition: StandardBenchmarkAnchorContract,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchored_case_ids: dict[tuple[str, str], tuple[str, ...]] = {}
    for manifest_path in definition.manifest_paths:
        anchored_case_ids.update(
            anchored_workload_case_ids(
                manifest_path,
                anchor_case_ids=published_case_ids_by_signature(
                    definition.correctness_case_signature
                ),
                workload_signature=definition.workload_signature,
                include_workload=definition.includes_workload,
            )
        )
    return anchored_case_ids


def _unanchored_case_ids(
    definition: StandardBenchmarkAnchorContract,
    manifest_path: pathlib.Path,
    *,
    include_special_unanchored: bool = False,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=(
            None if include_special_unanchored else definition.includes_workload
        ),
    )


def _expected_callback_anchor_case_ids(
    definition: StandardBenchmarkAnchorContract,
) -> dict[tuple[str, str], tuple[str, ...]]:
    if definition.callback_anchor_workload_ids:
        return _anchor_case_subset(
            definition.expected_anchor_case_ids,
            definition.callback_anchor_workload_ids,
        )
    return definition.expected_anchor_case_ids


def _expected_legacy_anchor_case_ids(
    definition: StandardBenchmarkAnchorContract,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return _anchor_case_subset(
        definition.expected_anchor_case_ids,
        definition.expected_legacy_workload_ids,
    )


def _expected_anchored_pairs(
    definition: StandardBenchmarkAnchorContract,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> tuple[Any, ...]:
    anchored_pairs = []
    for manifest_path in definition.manifest_paths:
        manifest_anchor_case_ids = _expected_anchor_case_ids_for_manifest(
            definition,
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
        )
        if not manifest_anchor_case_ids:
            continue
        anchored_pairs.extend(
            expected_anchored_workload_case_pairs(
                manifest_path,
                expected_anchor_case_ids=manifest_anchor_case_ids,
                include_workload=definition.includes_workload,
            )
        )
    return tuple(anchored_pairs)
