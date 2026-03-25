from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
import pathlib
import re
from typing import Any, Protocol

import pytest

from tests.benchmarks.benchmark_test_support import (
    compile_proxy_correctness_case_signature,
    compile_proxy_workload_signature,
    is_compile_proxy_workload,
    manifest_workloads,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    _definition_anchor_expectations,
    _workload_case_pair_anchor_expectations,
    _workload_case_pairs_case_ids,
    _workload_case_pairs_workload_ids,
    anchored_workload_case_ids,
    expected_anchored_workload_case_pairs,
    published_case_ids_by_signature,
    unanchored_workload_ids,
)
from tests.conftest import REPO_ROOT, records_by_string_id


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


COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
)
MODULE_BOUNDARY_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.py"
PATTERN_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "pattern_boundary.py"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)
NESTED_GROUP_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py"
)
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
)


def _include_all_workloads(_: Any) -> bool:
    return True


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
    from tests.benchmarks.compiled_pattern_module_compile_benchmark_support import (
        _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
        _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
    )
    from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
        COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
    )
    from tests.benchmarks.pattern_boundary_benchmark_anchor_support import (
        PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
    )
    from tests.benchmarks.source_tree_benchmark_anchor_support import (
        MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
        _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID as OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
        _counted_repeat_correctness_case_signature,
        _counted_repeat_workload_signature,
        _grouped_alternation_correctness_case_signature,
        _grouped_alternation_replacement_correctness_case_signature,
        _grouped_alternation_workload_signature,
        _is_non_alternation_counted_repeat_workload,
        _is_optional_group_conditional_workload,
        _nested_group_correctness_case_signature,
        _nested_group_workload_signature,
        _optional_group_correctness_case_signature,
        _optional_group_workload_signature,
    )
    from tests.python.fixture_parity_support import (
        BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
        BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
        BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
        OPEN_ENDED_ALTERNATION_BYTES_CASES,
        OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
        OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    )

    return (
    StandardBenchmarkAnchorContractDefinition(
        name="compile-proxy",
        manifest_paths=(
            COMPILE_MATRIX_MANIFEST_PATH,
            REGRESSION_MATRIX_MANIFEST_PATH,
        ),
        expected_anchor_case_ids=(
            _definition_anchor_expectations(
                COMPILE_MATRIX_MANIFEST_PATH,
                {
                    "compile-inline-locale-bytes-warm": (
                        "bytes-inline-locale-flag-success",
                    ),
                    "compile-lookbehind-cold": (
                        "str-fixed-width-lookbehind-success",
                    ),
                    "compile-character-class-ignorecase-warm": (
                        "str-character-class-ignorecase-success",
                    ),
                    "compile-possessive-quantifier-cold": (
                        "str-possessive-quantifier-success",
                    ),
                    "compile-atomic-group-purged": (
                        "str-atomic-group-success",
                    ),
                    "compile-parser-stress-cold": (
                        "str-parser-stress-compile-proxy-success",
                    ),
                },
            )
            | _definition_anchor_expectations(
                REGRESSION_MATRIX_MANIFEST_PATH,
                {
                    "regression-parser-atomic-lookbehind-cold": (
                        "str-parser-stress-compile-proxy-success",
                    ),
                    "regression-parser-bytes-backreference-purged": (
                        "bytes-named-backreference-compile-proxy-success",
                    ),
                    "regression-module-compile-verbose-purged": (
                        "workflow-compile-str-verbose-regression",
                    ),
                    "regression-module-compile-multiline-purged": (
                        "workflow-compile-str-multiline-regression",
                    ),
                    "regression-module-compile-multiline-purged-bytes": (
                        "workflow-compile-bytes-multiline-regression",
                    ),
                    "regression-module-compile-verbose-purged-bytes": (
                        "workflow-compile-bytes-verbose-regression",
                    ),
                },
            )
        ),
        include_workload=is_compile_proxy_workload,
        correctness_case_signature=compile_proxy_correctness_case_signature,
        workload_signature=compile_proxy_workload_signature,
    ),
    *COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
    *MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
    *(
        owner_spec.anchor_definition()
        for owner_spec in _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS
    ),
    *(
        owner_spec.anchor_definition()
        for owner_spec in _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS
    ),
    *COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
    *PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
    StandardBenchmarkAnchorContractDefinition(
        name="optional-group-conditional",
        manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            OPTIONAL_GROUP_MANIFEST_PATH,
            {
                OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID: (
                    "optional-group-conditional-module-search-present-str",
                ),
            },
        ),
        include_workload=_is_optional_group_conditional_workload,
        correctness_case_signature=_optional_group_correctness_case_signature,
        workload_signature=_optional_group_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group",
        manifest_paths=(NESTED_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            NESTED_GROUP_MANIFEST_PATH,
            {
                "module-compile-nested-group-cold-str": (
                    "nested-group-compile-metadata-str",
                ),
                "module-search-nested-group-warm-str": (
                    "nested-group-module-search-str",
                ),
                "pattern-fullmatch-nested-group-purged-str": (
                    "nested-group-pattern-fullmatch-str",
                ),
                "module-compile-named-nested-group-warm-str": (
                    "named-nested-group-compile-metadata-str",
                ),
                "module-search-named-nested-group-warm-str": (
                    "named-nested-group-module-search-str",
                ),
                "pattern-fullmatch-named-nested-group-purged-str": (
                    "named-nested-group-pattern-fullmatch-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=_nested_group_correctness_case_signature,
        workload_signature=_nested_group_workload_signature,
        run_callback_result_parity=True,
        expected_excluded_workload_ids=frozenset(
            {
                "module-search-triple-nested-group-cold-gap",
                "pattern-fullmatch-named-quantified-nested-group-purged-gap",
            }
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="exact-repeat",
        manifest_paths=(EXACT_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            EXACT_REPEAT_MANIFEST_PATH,
            {
                "module-compile-numbered-exact-repeat-group-cold-str": (
                    "exact-repeat-numbered-group-compile-metadata-str",
                ),
                "module-search-numbered-exact-repeat-group-warm-str": (
                    "exact-repeat-numbered-group-module-search-str",
                ),
                "pattern-fullmatch-numbered-exact-repeat-group-purged-str": (
                    "exact-repeat-numbered-group-pattern-fullmatch-str",
                ),
                "module-compile-named-exact-repeat-group-warm-str": (
                    "exact-repeat-named-group-compile-metadata-str",
                ),
                "module-search-named-exact-repeat-group-warm-str": (
                    "exact-repeat-named-group-module-search-str",
                ),
                "pattern-fullmatch-named-exact-repeat-group-purged-str": (
                    "exact-repeat-named-group-pattern-fullmatch-str",
                ),
                "module-search-numbered-broader-ranged-repeat-group-cold-gap": (
                    "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                ),
            },
        ),
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="ranged-repeat",
        manifest_paths=(RANGED_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            RANGED_REPEAT_MANIFEST_PATH,
            {
                "module-compile-numbered-ranged-repeat-group-cold-str": (
                    "ranged-repeat-numbered-group-compile-metadata-str",
                ),
                "module-search-numbered-ranged-repeat-group-lower-bound-warm-str": (
                    "ranged-repeat-numbered-group-module-search-lower-bound-str",
                ),
                "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str": (
                    "ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
                ),
                "module-compile-named-ranged-repeat-group-warm-str": (
                    "ranged-repeat-named-group-compile-metadata-str",
                ),
                "module-search-named-ranged-repeat-group-upper-bound-warm-str": (
                    "ranged-repeat-named-group-module-search-upper-bound-str",
                ),
                "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str": (
                    "ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
                ),
                "module-search-numbered-ranged-repeat-group-wider-range-cold-gap": (
                    "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                ),
            },
        ),
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation",
        manifest_paths=(GROUPED_ALTERNATION_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            GROUPED_ALTERNATION_MANIFEST_PATH,
            {
                "module-compile-grouped-alternation-cold-str": (
                    "grouped-alternation-compile-metadata-str",
                ),
                "module-search-grouped-alternation-warm-str": (
                    "grouped-alternation-module-search-str",
                ),
                "pattern-fullmatch-grouped-alternation-purged-str": (
                    "grouped-alternation-pattern-fullmatch-str",
                ),
                "module-compile-named-grouped-alternation-warm-str": (
                    "named-grouped-alternation-compile-metadata-str",
                ),
                "module-search-named-grouped-alternation-warm-str": (
                    "named-grouped-alternation-module-search-str",
                ),
                "pattern-fullmatch-named-grouped-alternation-purged-str": (
                    "named-grouped-alternation-pattern-fullmatch-str",
                ),
                "module-sub-template-nested-grouped-alternation-warm-gap": (
                    "module-sub-template-nested-group-alternation-numbered-wrapper-str",
                ),
                "pattern-subn-template-named-nested-grouped-alternation-purged-gap": (
                    "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=_grouped_alternation_correctness_case_signature,
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=frozenset(
            {
                "module-sub-template-nested-grouped-alternation-warm-gap",
                "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
            }
        ),
        callback_anchor_workload_ids=frozenset(
            {
                "module-sub-template-nested-grouped-alternation-warm-gap",
                "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
            }
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation-replacement",
        manifest_paths=(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
            {
                "module-sub-template-grouped-alternation-warm-str": (
                    "module-sub-template-grouped-alternation-str",
                ),
                "module-subn-template-grouped-alternation-warm-str": (
                    "module-subn-template-grouped-alternation-str",
                ),
                "pattern-sub-template-grouped-alternation-purged-str": (
                    "pattern-sub-template-grouped-alternation-str",
                ),
                "pattern-subn-template-grouped-alternation-purged-str": (
                    "pattern-subn-template-grouped-alternation-str",
                ),
                "module-sub-template-named-grouped-alternation-warm-str": (
                    "module-sub-template-named-grouped-alternation-str",
                ),
                "module-subn-template-named-grouped-alternation-warm-str": (
                    "module-subn-template-named-grouped-alternation-str",
                ),
                "pattern-sub-template-named-grouped-alternation-purged-str": (
                    "pattern-sub-template-named-grouped-alternation-str",
                ),
                "pattern-subn-template-named-grouped-alternation-purged-str": (
                    "pattern-subn-template-named-grouped-alternation-str",
                ),
                "module-sub-template-nested-grouped-alternation-cold-gap": (
                    "module-sub-template-nested-group-alternation-numbered-outer-str",
                ),
                "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap": (
                    "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=frozenset(
            {
                "module-sub-template-nested-grouped-alternation-cold-gap",
                "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
            }
        ),
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group-replacement",
        manifest_paths=(NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
            {
                "module-sub-template-nested-group-numbered-warm-str": (
                    "module-sub-template-nested-group-numbered-str",
                ),
                "module-subn-template-nested-group-numbered-warm-str": (
                    "module-subn-template-nested-group-numbered-str",
                ),
                "pattern-sub-template-nested-group-numbered-purged-str": (
                    "pattern-sub-template-nested-group-numbered-str",
                ),
                "pattern-subn-template-nested-group-numbered-purged-str": (
                    "pattern-subn-template-nested-group-numbered-str",
                ),
                "module-sub-template-nested-group-named-warm-str": (
                    "module-sub-template-nested-group-named-str",
                ),
                "module-subn-template-nested-group-named-warm-str": (
                    "module-subn-template-nested-group-named-str",
                ),
                "pattern-sub-template-nested-group-named-purged-str": (
                    "pattern-sub-template-nested-group-named-str",
                ),
                "pattern-subn-template-nested-group-named-purged-str": (
                    "pattern-subn-template-nested-group-named-str",
                ),
                "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str": (
                    "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
                ),
                "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str": (
                    "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
                ),
                "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str": (
                    "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
                ),
                "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap": (
                    "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
                ),
                "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                    "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str": (
                    "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
                ),
                "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                ),
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                    "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str": (
                    "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                ),
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                ),
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str": (
                    "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str": (
                    "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                ),
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                ),
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str": (
                    "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                ),
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str": (
                    "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                ),
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str": (
                    "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
                ),
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str": (
                    "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        run_special_unanchored_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="open-ended-grouped-alternation",
        manifest_paths=(OPEN_ENDED_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            OPEN_ENDED_MANIFEST_PATH,
            {
                "module-compile-numbered-open-ended-group-alternation-cold-str": (
                    "open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str": (
                    "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-str": (
                    "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                ),
                "module-compile-named-open-ended-group-alternation-warm-str": (
                    "open-ended-quantified-group-alternation-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-alternation-lower-bound-de-warm-str": (
                    "open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                ),
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str": (
                    "open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                ),
                "module-compile-numbered-open-ended-group-alternation-cold-bytes": (
                    "open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-alternation-warm-bytes": (
                    "open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-conditional-cold-str": (
                    "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-cold-str": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-broader-range-cold-gap": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                ),
                "module-compile-named-open-ended-group-broader-range-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                ),
                "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-cold-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-broader-range-warm-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-named-open-ended-group-broader-range-conditional-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                ),
                "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
                ),
                "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
                ),
                "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes": (
                    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                ),
                "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                    "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-named-open-ended-group-conditional-warm-str": (
                    "open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str": (
                    "open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                ),
                "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                    "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                ),
                "module-compile-numbered-open-ended-group-conditional-cold-bytes": (
                    "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-conditional-warm-bytes": (
                    "open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                ),
                "module-compile-numbered-open-ended-group-backtracking-heavy-cold-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                ),
                "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                ),
                "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
                ),
                "module-compile-named-open-ended-group-backtracking-heavy-warm-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                ),
                "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-str": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
                ),
                "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",
                ),
                "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                ),
                "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes": (
                    "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                ),
            },
        ),
        include_workload=_include_all_workloads,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
            "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            "module-search-numbered-open-ended-group-conditional-warm-gap",
            "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
        ),
        direct_parity_supplemental_cases=(
            *OPEN_ENDED_ALTERNATION_BYTES_CASES,
            *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
            *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
        ),
        run_special_unanchored_result_parity=True,
    ),
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
