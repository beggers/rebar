from __future__ import annotations

from collections.abc import Callable, Iterable
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
