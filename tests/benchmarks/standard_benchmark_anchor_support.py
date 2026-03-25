from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import cache
import pathlib
import re
from typing import Any

import pytest

from tests.benchmarks.benchmark_test_support import (
    _definition_anchor_expectations,
    _workload_case_pair_anchor_expectations,
    _workload_case_pairs_case_ids,
    _workload_case_pairs_workload_ids,
    manifest_workloads,
    published_case_ids_by_signature,
    StandardBenchmarkAnchorContract,
    StandardBenchmarkAnchorContractDefinition,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    anchored_workload_case_ids,
    expected_anchored_workload_case_pairs,
    unanchored_workload_ids,
)
from tests.conftest import records_by_string_id


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


def _definition_workloads_by_id(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[str, Any]:
    workloads_by_id: dict[str, Any] = {}
    for manifest_path in definition.manifest_paths:
        workloads_by_id.update(
                records_by_string_id(
                manifest_workloads(manifest_path),
                id_attr="workload_id",
            )
        )
    return workloads_by_id


@cache
def _direct_parity_case_ids_by_signature(
    supplemental_cases: tuple[Any, ...],
) -> dict[tuple[str, bytes, bytes], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[str, bytes, bytes], list[str]] = {}

    for case in supplemental_cases:
        for haystack in case.search_matches + case.search_misses:
            case_ids_by_signature.setdefault(
                ("module.search", case.pattern, haystack),
                [],
            ).append(case.id)
        for haystack in case.fullmatch_matches + case.fullmatch_misses:
            case_ids_by_signature.setdefault(
                ("pattern.fullmatch", case.pattern, haystack),
                [],
            ).append(case.id)

    return {
        signature: tuple(case_ids)
        for signature, case_ids in case_ids_by_signature.items()
    }


def _manual_expected_result(workload: Any) -> object:
    pattern = workload.pattern_payload()
    re.purge()
    try:
        if workload.operation == "module.compile":
            pattern_argument = (
                re.compile(pattern, workload.flags)
                if workload.use_compiled_pattern
                else pattern
            )
            return re.compile(pattern_argument, workload.flags)
        if workload.operation == "module.search":
            return re.search(pattern, workload.haystack_payload(), workload.flags)
        if workload.operation == "pattern.search":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.search(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.search(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.search(workload.haystack_payload())
        if workload.operation == "pattern.fullmatch":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.fullmatch(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.fullmatch(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.fullmatch(workload.haystack_payload())
        if workload.operation == "pattern.findall":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.findall(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.findall(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.findall(workload.haystack_payload())
        if workload.operation == "pattern.finditer":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return list(
                    compiled.finditer(
                        workload.haystack_payload(),
                        workload.pos_argument(),
                        workload.endpos_argument(),
                    )
                )
            if workload.pos is not None:
                return list(
                    compiled.finditer(
                        workload.haystack_payload(),
                        workload.pos_argument(),
                    )
                )
            return list(compiled.finditer(workload.haystack_payload()))
        if workload.operation == "module.sub":
            return re.sub(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "module.subn":
            return re.subn(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "pattern.sub":
            compiled = re.compile(pattern, workload.flags)
            return compiled.sub(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
        if workload.operation == "pattern.subn":
            compiled = re.compile(pattern, workload.flags)
            return compiled.subn(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
    finally:
        re.purge()

    raise AssertionError(
        f"unexpected special-unanchored benchmark workload operation {workload.operation!r}"
    )


@cache
def _build_standard_benchmark_definitions() -> tuple[StandardBenchmarkAnchorContractDefinition, ...]:
    from functools import partial

    from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
        COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
        _conditional_group_exists_nested_callable_correctness_case_signature,
        _conditional_group_exists_nested_callable_workload_signature,
        _conditional_group_exists_quantified_callable_correctness_case_signature,
        _conditional_group_exists_quantified_callable_workload_signature,
    )
    from tests.benchmarks.benchmark_test_support import (
        COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
    )
    from tests.benchmarks.compiled_pattern_module_compile_benchmark_support import (
        COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
    )
    from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
        COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
    )
    from tests.benchmarks.pattern_boundary_benchmark_anchor_support import (
        PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
    )
    from tests.benchmarks.source_tree_benchmark_anchor_support import (
        MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
        SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
    )

    return (
        *COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
        *COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
        *MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
        *COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
        *COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
        *PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
        *SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
    )

STANDARD_BENCHMARK_DEFINITIONS = _build_standard_benchmark_definitions()


def _has_standard_benchmark_legacy_workloads(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(definition.expected_legacy_workload_ids)


def _runs_standard_benchmark_callback_result_parity(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return definition.run_callback_result_parity


def _has_standard_benchmark_special_unanchored_workloads(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(definition.expected_special_unanchored_workload_ids)


def _has_standard_benchmark_special_unanchored_direct_parity_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(
        definition.expected_special_unanchored_workload_ids
        and definition.direct_parity_supplemental_cases
    )


def _standard_benchmark_manifest_params() -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            manifest_path,
            id=f"{definition.name}:{manifest_path.name}",
        )
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        for manifest_path in definition.manifest_paths
    )


def _standard_benchmark_definition_params(
    *,
    include_definition: Callable[[StandardBenchmarkAnchorContractDefinition], bool],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(definition, id=definition.name)
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if include_definition(definition)
    )


def _standard_benchmark_definition_id(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> str:
    return definition.name


def _standard_benchmark_special_unanchored_result_parity_params() -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            workload_id,
            id=f"{definition.name}:{workload_id}",
        )
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if definition.run_special_unanchored_result_parity
        for workload_id in definition.expected_special_unanchored_workload_ids
    )
