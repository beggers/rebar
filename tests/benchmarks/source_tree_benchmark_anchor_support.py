from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
import pathlib
import re
from typing import Any

import pytest

from rebar_harness.benchmarks import build_callable
from rebar_harness.correctness import published_fixture_manifests
from tests.benchmarks.benchmark_test_support import (
    StandardBenchmarkAnchorContractDefinition,
    _definition_anchor_expectations,
    _workload_case_pair_anchor_expectations,
    _workload_case_pairs_case_ids,
    _workload_case_pairs_workload_ids,
    freeze_signature_value,
    selected_manifest_workloads,
)
from tests.conftest import REPO_ROOT, records_by_string_id
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    assert_match_result_parity,
    assert_pattern_parity,
    case_pattern,
    module_workflow_keyword_kwargs_signature,
)


@dataclass(frozen=True, slots=True)
class AnchoredWorkloadCasePair:
    manifest_name: str
    workload_id: str
    case_id: str
    workload: Any
    case: Any


def _module_workflow_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.kwargs:
        return None
    if case.use_compiled_pattern or case.helper not in {"search", "match", "fullmatch"}:
        return None
    return (
        f"module.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _module_workflow_keyword_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    args: list[object] = [workload.haystack_payload()]
    if (
        workload.operation == "module.search"
        and workload.expected_exception is not None
        and "flags" in workload.kwargs
    ):
        args.append(workload.flags)
    return tuple(args)


def _module_workflow_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(list(_module_workflow_keyword_workload_args(workload))),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_keyword_flags_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    return (
        workload.operation in {"module.search", "module.match", "module.fullmatch"}
        and bool(workload.kwargs)
        and len(keyword_names) == 1
        and keyword_names[0] == "flags"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
    )


def _is_module_workflow_keyword_error_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    expected_exception = workload.expected_exception
    if (
        workload.operation
        not in {"module.search", "module.match", "module.fullmatch"}
        or not workload.kwargs
        or len(keyword_names) != 1
        or expected_exception is None
        or expected_exception.get("type") != "TypeError"
        or workload.use_compiled_pattern
    ):
        return False
    message = expected_exception.get("message_substring", "")
    if keyword_names[0] == "flags":
        return "multiple values for argument" in message
    if keyword_names[0] == "missing":
        return "unexpected keyword argument" in message
    return False


MODULE_BOUNDARY_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.py"
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
)
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

_OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)


@cache
def _module_workflow_keyword_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
        StandardBenchmarkAnchorContractDefinition(
            name="module-workflow-keyword-flags",
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                MODULE_BOUNDARY_MANIFEST_PATH,
                {
                    "module-search-flags-keyword-warm-str": (
                        "workflow-module-search-flags-keyword-str",
                    ),
                    "module-match-flags-keyword-purged-bytes": (
                        "workflow-module-match-flags-keyword-bytes",
                    ),
                    "module-fullmatch-flags-keyword-warm-str": (
                        "workflow-module-fullmatch-flags-keyword-str",
                    ),
                },
            ),
            include_workload=_is_module_workflow_keyword_flags_workload,
            correctness_case_signature=_module_workflow_keyword_correctness_case_signature,
            workload_signature=_module_workflow_keyword_workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="module-workflow-keyword-errors",
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                MODULE_BOUNDARY_MANIFEST_PATH,
                {
                    "module-search-duplicate-flags-keyword-warm-str": (
                        "workflow-module-search-duplicate-flags-keyword",
                    ),
                    "module-fullmatch-unexpected-keyword-purged-str": (
                        "workflow-module-fullmatch-unexpected-keyword",
                    ),
                },
            ),
            include_workload=_is_module_workflow_keyword_error_workload,
            correctness_case_signature=_module_workflow_keyword_correctness_case_signature,
            workload_signature=_module_workflow_keyword_workload_signature,
        ),
    )


@cache
def _source_tree_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
        StandardBenchmarkAnchorContractDefinition(
            name="optional-group-conditional",
            manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                OPTIONAL_GROUP_MANIFEST_PATH,
                {
                    _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID: (
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
            include_workload=lambda _: True,
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
            include_workload=lambda _: True,
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
            include_workload=lambda _: True,
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
            include_workload=lambda _: True,
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
            include_workload=lambda _: True,
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


def __getattr__(name: str) -> object:
    if name == "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS":
        return _module_workflow_keyword_standard_benchmark_definitions()
    if name == "SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS":
        return _source_tree_standard_benchmark_definitions()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _compile_search_fullmatch_case_signature(
    case: Any,
    *,
    pattern: Callable[[], Any],
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", pattern(), (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            pattern(),
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _compile_search_fullmatch_workload_signature(
    workload: Any,
    *,
    pattern: Callable[[], Any],
    module_search_args: Callable[[], tuple[Any, ...]],
    pattern_fullmatch_args: Callable[[], tuple[Any, ...]],
    error_label: str,
) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            pattern(),
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            module_search_args(),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            pattern(),
            pattern_fullmatch_args(),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected {error_label} workload operation {workload.operation!r}"
    )


def _optional_group_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.helper != "search":
        return None

    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"
    return (
        "module.search",
        None,
        freeze_signature_value(case.serialized_args()),
        kwargs_signature,
        flags,
        text_model,
    )


def _optional_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation != "module.search":
        raise AssertionError(
            "unexpected optional-group benchmark workload operation "
            f"{workload.operation!r}"
        )

    return (
        "module.search",
        None,
        freeze_signature_value([workload.pattern, workload.haystack]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_optional_group_conditional_workload(workload: Any) -> bool:
    return workload.workload_id == _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID


def _nested_group_correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
    return _compile_search_fullmatch_case_signature(
        case,
        pattern=lambda: case.pattern,
    )


def _nested_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    return _compile_search_fullmatch_workload_signature(
        workload,
        pattern=lambda: workload.pattern,
        module_search_args=lambda: (workload.pattern, workload.haystack),
        pattern_fullmatch_args=lambda: (workload.haystack,),
        error_label="nested-group benchmark",
    )


def _counted_repeat_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _compile_search_fullmatch_case_signature(
        case,
        pattern=lambda: case.pattern_payload(),
    )


def _counted_repeat_workload_signature(workload: Any) -> tuple[Any, ...]:
    return _compile_search_fullmatch_workload_signature(
        workload,
        pattern=lambda: workload.pattern_payload(),
        module_search_args=lambda: freeze_signature_value(
            [
                workload.pattern_payload(),
                workload.haystack_payload(),
            ]
        ),
        pattern_fullmatch_args=lambda: freeze_signature_value(
            [workload.haystack_payload()]
        ),
        error_label="counted-repeat benchmark",
    )


def _is_non_alternation_counted_repeat_workload(workload: Any) -> bool:
    return workload.operation in {
        "module.compile",
        "module.search",
        "pattern.fullmatch",
    } and "|" not in workload.pattern


def _grouped_alternation_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper in {"search", "sub", "subn"}:
        return (
            f"module.{case.helper}",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"fullmatch", "sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ()
    if workload.operation == "module.search":
        return freeze_signature_value([workload.pattern, workload.haystack])
    if workload.operation == "pattern.fullmatch":
        return freeze_signature_value([workload.haystack])
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"module.search", "module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.fullmatch", "pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_replacement_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "module_call" and case.helper in {"sub", "subn"}:
        return (
            f"module.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


@cache
def published_case_ids_by_signature(
    case_signature: Callable[[Any], tuple[Any, ...] | None],
) -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for case in published_cases_by_id().values():
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
    return records_by_string_id(
        (
            case
            for manifest in published_fixture_manifests()
            for case in manifest.cases
        ),
        id_attr="case_id",
        duplicate_error=lambda duplicate_ids: AssertionError(
            f"duplicate published correctness case id {duplicate_ids[0]!r}"
        ),
    )


def anchored_workload_case_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return {
        (manifest_path.name, workload.workload_id): anchor_case_ids.get(
            workload_signature(workload),
            (),
        )
        for workload in workloads
    }


def unanchored_workload_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[str, ...]:
    workloads = selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload_signature(workload) not in anchor_case_ids
    )


def expected_anchored_workload_case_pairs(
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[AnchoredWorkloadCasePair, ...]:
    manifest_name = manifest_path.name
    workloads_by_id = records_by_string_id(
        selected_manifest_workloads(
            manifest_path,
            include_workload=include_workload,
        ),
        id_attr="workload_id",
    )
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
        try:
            expected = run_correctness_case_with_cpython(anchored_pair.case)
        except Exception as expected_exc:
            with pytest.raises(type(expected_exc)) as observed_exc:
                run_benchmark_workload_with_cpython(anchored_pair.workload)
            assert str(observed_exc.value) == str(expected_exc)
            continue
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
        compiled_pattern = None
        if case.use_compiled_pattern:
            compiled_pattern = re.compile(case.pattern_payload(), case.flags or 0)
        if not case.use_compiled_pattern and not case.include_pattern_arg:
            if case.pattern is None:
                return getattr(re, case.helper)(
                    *case.args,
                    **case.kwargs,
                )
            return getattr(re, case.helper)(
                case.pattern_payload(),
                *case.args,
                **case.kwargs,
            )
        return getattr(re, case.helper)(
            *case.module_call_args(compiled_pattern),
            **case.kwargs,
        )

    if case.operation == "pattern_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        compiled = re.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise AssertionError(f"unexpected correctness operation {case.operation!r}")
