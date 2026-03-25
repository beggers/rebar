from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
import re
from typing import Any

from rebar_harness import benchmarks
from tests.benchmarks import benchmark_test_support
from tests.benchmarks.benchmark_test_support import (
    COLLECTION_REPLACEMENT_MANIFEST_PATH,
    MODULE_BOUNDARY_MANIFEST_PATH,
    StandardBenchmarkAnchorContractDefinition,
    _SourceTreeContractBuilderSpec,
    _contract_source_workloads,
    _definition_anchor_expectations,
    _is_module_workflow_keyword_error_workload,
    _workload_case_pair_anchor_expectations,
    _workload_case_pairs_case_ids,
    _workload_case_pairs_workload_ids,
    freeze_signature_value,
)
from tests.python.fixture_parity_support import (
    callable_match_group_signature,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)

_COLLECTION_REPLACEMENT_SPLIT_OPERATIONS = frozenset(
    {"module.split", "pattern.split"}
)
_COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS = frozenset(
    {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
)

def _collection_replacement_pattern_collection_workload_args(
    workload: Any,
    *,
    requires_window_bounds: bool,
) -> tuple[Any, ...]:
    if requires_window_bounds:
        args: list[object] = [workload.haystack_payload()]
        if workload.pos is not None or workload.endpos is not None:
            args.append(0 if workload.pos is None else workload.pos)
        if workload.endpos is not None:
            args.append(workload.endpos)
        return tuple(args)

    args = [workload.haystack_payload()]
    if workload.maxsplit is not None and not (
        type(workload.maxsplit) is int and workload.maxsplit == 0
    ):
        args.append(workload.maxsplit_argument())
    return tuple(args)


@dataclass(frozen=True, slots=True)
class _CollectionReplacementLiteralReplacementRoute:
    workload_case_pairs: tuple[tuple[str, str], ...]
    expected_operation: str
    operation_prefix: str
    operations: tuple[str, ...]
    text_models: tuple[str, ...]
    args_offset: int
    allowed_counts: tuple[int, ...] | None = None

    def workload_ids(self) -> tuple[str, ...]:
        return _workload_case_pairs_workload_ids(self.workload_case_pairs)

    def case_ids(self) -> tuple[str, ...]:
        return _workload_case_pairs_case_ids(self.workload_case_pairs)

    def anchor_expectations(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return _workload_case_pair_anchor_expectations(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            self.workload_case_pairs,
        )


@dataclass(frozen=True, slots=True)
class _CollectionReplacementPatternCollectionRoute:
    workload_case_pairs: tuple[tuple[str, str], ...]
    operation: str
    requires_window_bounds: bool

    @property
    def helper(self) -> str:
        return self.operation.removeprefix("pattern.")

    def workload_ids(self) -> tuple[str, ...]:
        return _workload_case_pairs_workload_ids(self.workload_case_pairs)

    def case_ids(self) -> tuple[str, ...]:
        return _workload_case_pairs_case_ids(self.workload_case_pairs)

    def anchor_expectations(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return _workload_case_pair_anchor_expectations(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            self.workload_case_pairs,
        )

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        if case.case_id not in self.case_ids():
            return None
        if case.operation != "pattern_call" or case.kwargs or case.helper != self.helper:
            return None
        return (
            self.operation,
            case_pattern(case),
            freeze_signature_value(list(case.args)),
            (),
            case.flags or 0,
            case.text_model or "str",
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        if not self.includes_workload(workload):
            raise AssertionError(
                "unexpected collection/replacement bounded "
                f"{self.operation} workload {workload.workload_id!r}"
            )
        return (
            self.operation,
            workload.pattern_payload(),
            freeze_signature_value(
                list(
                    _collection_replacement_pattern_collection_workload_args(
                        workload,
                        requires_window_bounds=self.requires_window_bounds,
                    )
                )
            ),
            (),
            workload.flags,
            workload.text_model,
        )

    def includes_workload(self, workload: Any) -> bool:
        return (
            workload.workload_id in self.workload_ids()
            and workload.operation == self.operation
            and workload.pattern == "abc"
            and workload.expected_exception is None
            and not workload.use_compiled_pattern
            and workload.text_model in {"str", "bytes"}
            and not workload.kwargs
            and (workload.pos is not None) is self.requires_window_bounds
            and (workload.endpos is not None) is self.requires_window_bounds
        )


_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES = {
    "findall": _CollectionReplacementPatternCollectionRoute(
        workload_case_pairs=(
            ("pattern-findall-bounded-warm-str", "pattern-findall-str-bounded"),
            (
                "pattern-findall-bounded-no-match-warm-str",
                "pattern-findall-str-bounded-no-match",
            ),
            ("pattern-findall-bounded-purged-bytes", "pattern-findall-bytes-bounded"),
        ),
        operation="pattern.findall",
        requires_window_bounds=True,
    ),
    "finditer": _CollectionReplacementPatternCollectionRoute(
        workload_case_pairs=(
            ("pattern-finditer-bounded-warm-str", "pattern-finditer-str-bounded"),
            (
                "pattern-finditer-bounded-no-match-warm-str",
                "pattern-finditer-str-bounded-no-match",
            ),
            (
                "pattern-finditer-bounded-purged-bytes",
                "pattern-finditer-bytes-bounded",
            ),
        ),
        operation="pattern.finditer",
        requires_window_bounds=True,
    ),
    "split": _CollectionReplacementPatternCollectionRoute(
        workload_case_pairs=(
            ("pattern-split-no-match-warm-str", "pattern-split-str-no-match"),
            ("pattern-split-repeated-warm-str", "pattern-split-str-repeated"),
            ("pattern-split-maxsplit-purged-bytes", "pattern-split-bytes-maxsplit"),
        ),
        operation="pattern.split",
        requires_window_bounds=False,
    ),
}

_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES = {
    "pattern": _CollectionReplacementLiteralReplacementRoute(
        workload_case_pairs=(
            ("pattern-sub-no-match-warm-str", "pattern-sub-str-no-match"),
            ("pattern-sub-single-match-warm-str", "pattern-sub-str-single-match"),
            ("pattern-sub-repeated-warm-str", "pattern-sub-str-repeated"),
            ("pattern-sub-count-one-warm-str", "pattern-sub-str-count-one"),
            ("pattern-sub-negative-count-warm-str", "pattern-sub-str-negative-count"),
            ("pattern-sub-bytes-no-match-purged-bytes", "pattern-sub-bytes-no-match"),
            (
                "pattern-sub-bytes-single-match-purged-bytes",
                "pattern-sub-bytes-single-match",
            ),
            (
                "pattern-sub-bytes-repeated-purged-bytes",
                "pattern-sub-bytes-repeated",
            ),
            (
                "pattern-sub-bytes-count-one-purged-bytes",
                "pattern-sub-bytes-count-one",
            ),
            (
                "pattern-sub-bytes-negative-count-purged-bytes",
                "pattern-sub-bytes-negative-count",
            ),
            ("pattern-subn-count-warm-str", "pattern-subn-str-count"),
            ("pattern-subn-single-match-warm-str", "pattern-subn-str-single-match"),
            ("pattern-subn-repeated-warm-str", "pattern-subn-str-repeated"),
            ("pattern-subn-negative-count-warm-str", "pattern-subn-str-negative-count"),
            ("pattern-subn-no-match-warm-str", "pattern-subn-str-no-match"),
            ("pattern-subn-bytes-count-purged-bytes", "pattern-subn-bytes-count"),
            (
                "pattern-subn-bytes-single-match-purged-bytes",
                "pattern-subn-bytes-single-match",
            ),
            (
                "pattern-subn-bytes-repeated-purged-bytes",
                "pattern-subn-bytes-repeated",
            ),
            (
                "pattern-subn-bytes-negative-count-purged-bytes",
                "pattern-subn-bytes-negative-count",
            ),
            (
                "pattern-subn-bytes-no-match-purged-bytes",
                "pattern-subn-bytes-no-match",
            ),
        ),
        expected_operation="pattern_call",
        operation_prefix="pattern",
        operations=("pattern.sub", "pattern.subn"),
        text_models=("str", "bytes"),
        args_offset=0,
    ),
    "module": _CollectionReplacementLiteralReplacementRoute(
        workload_case_pairs=(
            ("module-sub-str-no-match-purged-str", "module-sub-str-no-match"),
            ("module-sub-str-single-match-purged-str", "module-sub-str-single-match"),
            ("module-sub-str-repeated-purged-str", "module-sub-str-repeated"),
            ("module-sub-str-count-one-purged-str", "module-sub-str-count-one"),
            ("module-sub-str-negative-count-purged-str", "module-sub-str-negative-count"),
            ("module-subn-str-count-purged-str", "module-subn-str-count"),
            (
                "module-subn-str-single-match-purged-str",
                "module-subn-str-single-match",
            ),
            ("module-subn-str-repeated-purged-str", "module-subn-str-repeated"),
            (
                "module-subn-str-negative-count-purged-str",
                "module-subn-str-negative-count",
            ),
            ("module-subn-str-no-match-purged-str", "module-subn-str-no-match"),
            ("module-sub-bytes-no-match-purged-bytes", "module-sub-bytes-no-match"),
            (
                "module-sub-bytes-single-match-purged-bytes",
                "module-sub-bytes-single-match",
            ),
            ("module-sub-bytes-repeated-purged-bytes", "module-sub-bytes-repeated"),
            ("module-sub-bytes-count-one-purged-bytes", "module-sub-bytes-count-one"),
            ("module-subn-bytes-count-purged-bytes", "module-subn-bytes-count"),
            (
                "module-subn-bytes-single-match-purged-bytes",
                "module-subn-bytes-single-match",
            ),
            ("module-subn-bytes-repeated-purged-bytes", "module-subn-bytes-repeated"),
            ("module-subn-bytes-no-match-purged-bytes", "module-subn-bytes-no-match"),
        ),
        expected_operation="module_call",
        operation_prefix="module",
        operations=("module.sub", "module.subn"),
        text_models=("str", "bytes"),
        args_offset=1,
        allowed_counts=(-1, 0, 1),
    ),
}


def _collection_replacement_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-module-positional-indexlike",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-maxsplit-indexlike-positional-purged-bytes": (
                        "workflow-module-split-maxsplit-indexlike-positional-bytes",
                    ),
                    "module-sub-count-indexlike-positional-warm-str": (
                        "workflow-module-sub-count-indexlike-positional-str",
                    ),
                    "module-subn-count-indexlike-positional-purged-bytes": (
                        "workflow-module-subn-count-indexlike-positional-bytes",
                    ),
                    "pattern-split-maxsplit-indexlike-positional-warm-str": (
                        "workflow-pattern-split-str-maxsplit-indexlike-positional",
                    ),
                    "pattern-sub-count-indexlike-positional-purged-bytes": (
                        "workflow-pattern-sub-count-indexlike-positional-bytes",
                    ),
                    "pattern-subn-count-indexlike-positional-warm-str": (
                        "workflow-pattern-subn-count-indexlike-positional-str",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_positional_indexlike_workload,
            correctness_case_signature=(
                _module_workflow_positional_indexlike_correctness_case_signature
            ),
            workload_signature=_collection_replacement_positional_indexlike_workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-keyword",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-maxsplit-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-keyword-bytes",
                    ),
                    "module-split-maxsplit-bool-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-bool-false-bytes",
                    ),
                    "module-split-maxsplit-indexlike-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-indexlike-bytes",
                    ),
                    "module-split-maxsplit-keyword-purged-str-compiled-pattern": (
                        "workflow-module-split-maxsplit-keyword-str-compiled-pattern",
                    ),
                    "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern",
                    ),
                    "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern",
                    ),
                    "module-split-duplicate-maxsplit-keyword-purged-str": (
                        "workflow-module-split-duplicate-maxsplit-keyword",
                    ),
                    "module-split-unexpected-keyword-purged-str": (
                        "workflow-module-split-unexpected-keyword",
                    ),
                    "module-split-unexpected-keyword-purged-bytes": (
                        "workflow-module-split-unexpected-keyword-bytes",
                    ),
                    "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern": (
                        "workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
                    ),
                    "module-split-unexpected-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-unexpected-keyword-bytes-compiled-pattern",
                    ),
                    "module-sub-count-keyword-warm-str": (
                        "workflow-module-sub-count-keyword-str",
                    ),
                    "module-sub-count-bool-keyword-warm-str": (
                        "workflow-module-sub-count-bool-true-str",
                    ),
                    "module-sub-count-bool-false-keyword-warm-str": (
                        "workflow-module-sub-count-bool-false-str",
                    ),
                    "module-sub-count-indexlike-keyword-warm-str": (
                        "workflow-module-sub-count-indexlike-str",
                    ),
                    "module-sub-count-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-keyword-str-compiled-pattern",
                    ),
                    "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern": (
                        "workflow-module-sub-count-indexlike-bytes-compiled-pattern",
                    ),
                    "module-sub-count-bool-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-bool-true-str-compiled-pattern",
                    ),
                    "module-sub-count-bool-false-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-bool-false-str-compiled-pattern",
                    ),
                    "module-sub-duplicate-count-keyword-warm-str": (
                        "workflow-module-sub-duplicate-count-keyword",
                    ),
                    "module-sub-unexpected-keyword-purged-str": (
                        "workflow-module-sub-unexpected-keyword",
                    ),
                    "module-sub-unexpected-keyword-after-positional-count-purged-str": (
                        "workflow-module-sub-unexpected-keyword-after-positional-count",
                    ),
                    "module-sub-count-alias-keyword-purged-str": (
                        "workflow-module-sub-count-alias-keyword",
                    ),
                    "module-sub-duplicate-count-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-duplicate-count-keyword-str-compiled-pattern",
                    ),
                    "module-sub-unexpected-keyword-purged-str-compiled-pattern": (
                        "workflow-module-sub-unexpected-keyword-str-compiled-pattern",
                    ),
                    "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern": (
                        "workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern",
                    ),
                    "module-sub-count-alias-keyword-purged-str-compiled-pattern": (
                        "workflow-module-sub-count-alias-keyword-str-compiled-pattern",
                    ),
                    "module-subn-count-keyword-purged-bytes": (
                        "workflow-module-subn-count-keyword-bytes",
                    ),
                    "module-subn-count-bool-keyword-purged-bytes": (
                        "workflow-module-subn-count-bool-false-bytes",
                    ),
                    "module-subn-count-bool-true-keyword-purged-bytes": (
                        "workflow-module-subn-count-bool-true-bytes",
                    ),
                    "module-subn-count-indexlike-keyword-purged-bytes": (
                        "workflow-module-subn-count-indexlike-bytes",
                    ),
                    "module-subn-duplicate-count-keyword-warm-bytes": (
                        "workflow-module-subn-duplicate-count-keyword-bytes",
                    ),
                    "module-subn-unexpected-keyword-purged-bytes": (
                        "workflow-module-subn-unexpected-keyword-bytes",
                    ),
                    "module-subn-unexpected-keyword-after-positional-count-purged-bytes": (
                        "workflow-module-subn-unexpected-keyword-after-positional-count-bytes",
                    ),
                    "module-subn-count-alias-keyword-purged-bytes": (
                        "workflow-module-subn-count-alias-keyword-bytes",
                    ),
                    "module-subn-count-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-count-indexlike-keyword-purged-str-compiled-pattern": (
                        "workflow-module-subn-count-indexlike-str-compiled-pattern",
                    ),
                    "module-subn-count-bool-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-bool-false-bytes-compiled-pattern",
                    ),
                    "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-bool-true-bytes-compiled-pattern",
                    ),
                    "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern": (
                        "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-unexpected-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern",
                    ),
                    "module-subn-count-alias-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-alias-keyword-bytes-compiled-pattern",
                    ),
                    "pattern-split-maxsplit-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-keyword",
                    ),
                    "pattern-split-maxsplit-bool-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-bool-true",
                    ),
                    "pattern-split-maxsplit-indexlike-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-indexlike",
                    ),
                    "pattern-split-duplicate-maxsplit-keyword-warm-str": (
                        "workflow-pattern-split-duplicate-maxsplit-keyword-str",
                    ),
                    "pattern-split-unexpected-keyword-warm-bytes": (
                        "workflow-pattern-split-unexpected-keyword-bytes",
                    ),
                    "pattern-sub-count-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-keyword-bytes",
                    ),
                    "pattern-sub-count-bool-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-bool-false-bytes",
                    ),
                    "pattern-sub-count-bool-true-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-bool-true-bytes",
                    ),
                    "pattern-sub-count-indexlike-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-indexlike-bytes",
                    ),
                    "pattern-sub-duplicate-count-keyword-warm-str": (
                        "workflow-pattern-sub-duplicate-count-keyword-str",
                    ),
                    "pattern-sub-unexpected-keyword-warm-str": (
                        "workflow-pattern-sub-unexpected-keyword-str",
                    ),
                    "pattern-sub-unexpected-keyword-after-positional-count-warm-str": (
                        "workflow-pattern-sub-unexpected-keyword-after-positional-count-str",
                    ),
                    "pattern-sub-count-alias-keyword-warm-str": (
                        "workflow-pattern-sub-count-alias-keyword-str",
                    ),
                    "pattern-subn-count-keyword-warm-str": (
                        "workflow-pattern-subn-count-keyword-str",
                    ),
                    "pattern-subn-count-bool-keyword-warm-str": (
                        "workflow-pattern-subn-count-bool-true-str",
                    ),
                    "pattern-subn-count-bool-false-keyword-warm-str": (
                        "workflow-pattern-subn-count-bool-false-str",
                    ),
                    "pattern-subn-count-indexlike-keyword-warm-str": (
                        "workflow-pattern-subn-count-indexlike-str",
                    ),
                    "pattern-subn-duplicate-count-keyword-warm-bytes": (
                        "workflow-pattern-subn-duplicate-count-keyword-bytes",
                    ),
                    "pattern-subn-unexpected-keyword-warm-bytes": (
                        "workflow-pattern-subn-unexpected-keyword-bytes",
                    ),
                    "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes": (
                        "workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes",
                    ),
                    "pattern-subn-count-alias-keyword-warm-bytes": (
                        "workflow-pattern-subn-count-alias-keyword-bytes",
                    ),
                },
            ),
            include_workload=benchmark_test_support._is_collection_replacement_keyword_workload,
            correctness_case_signature=(
                _collection_replacement_keyword_correctness_case_signature
            ),
            workload_signature=_collection_replacement_keyword_workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-compiled-pattern-literal-success",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-literal-warm-str-compiled-pattern": (
                        "workflow-module-split-str-compiled-pattern",
                    ),
                    "module-findall-literal-purged-bytes-compiled-pattern": (
                        "workflow-module-findall-bytes-compiled-pattern",
                    ),
                    "module-finditer-literal-warm-str-compiled-pattern": (
                        "workflow-module-finditer-str-compiled-pattern",
                    ),
                    "module-sub-literal-warm-str-compiled-pattern": (
                        "workflow-module-sub-str-compiled-pattern",
                    ),
                    "module-subn-literal-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-bytes-compiled-pattern",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_compiled_pattern_success_workload,
            correctness_case_signature=(
                _collection_replacement_compiled_pattern_success_correctness_case_signature
            ),
            workload_signature=(
                _collection_replacement_compiled_pattern_success_workload_signature
            ),
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-compiled-pattern-wrong-text-model",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-on-bytes-string-purged-str-compiled-pattern": (
                        "workflow-module-split-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-findall-on-str-string-purged-bytes-compiled-pattern": (
                        "workflow-module-findall-bytes-compiled-pattern-on-str-string",
                    ),
                    "module-finditer-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-finditer-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-sub-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-sub-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-subn-on-str-string-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-bytes-compiled-pattern-on-str-string",
                    ),
                },
            ),
            include_workload=benchmark_test_support._is_collection_replacement_wrong_text_model_workload,
            correctness_case_signature=(
                _collection_replacement_wrong_text_model_correctness_case_signature
            ),
            workload_signature=_collection_replacement_wrong_text_model_workload_signature,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="pattern-helper-collection-replacement-wrong-text-model",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "pattern-split-on-bytes-string-warm-str": (
                        "workflow-pattern-split-str-pattern-on-bytes-string",
                    ),
                    "pattern-sub-on-bytes-string-warm-str": (
                        "workflow-pattern-sub-str-pattern-on-bytes-string",
                    ),
                    "pattern-subn-on-str-string-purged-bytes": (
                        "workflow-pattern-subn-bytes-pattern-on-str-string",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
            correctness_case_signature=(
                _collection_replacement_pattern_wrong_text_model_correctness_case_signature
            ),
            workload_signature=(
                _collection_replacement_pattern_wrong_text_model_workload_signature
            ),
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-findall-bounded",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "findall"
            ].anchor_expectations(),
            include_workload=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "findall"
            ].includes_workload,
            correctness_case_signature=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "findall"
            ].correctness_case_signature,
            workload_signature=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "findall"
            ].workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-finditer-bounded",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "finditer"
            ].anchor_expectations(),
            include_workload=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "finditer"
            ].includes_workload,
            correctness_case_signature=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "finditer"
            ].correctness_case_signature,
            workload_signature=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "finditer"
            ].workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-split",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "split"
            ].anchor_expectations(),
            include_workload=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "split"
            ].includes_workload,
            correctness_case_signature=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "split"
            ].correctness_case_signature,
            workload_signature=_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "split"
            ].workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-module-literal-replacement",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
                "module"
            ].anchor_expectations(),
            include_workload=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR,
            correctness_case_signature=partial(
                _collection_replacement_literal_replacement_correctness_case_signature,
                route=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["module"],
            ),
            workload_signature=partial(
                _collection_replacement_literal_replacement_workload_signature,
                include_workload=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR,
                workload_kind="module",
            ),
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-literal-replacement",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
                "pattern"
            ].anchor_expectations(),
            include_workload=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR,
            correctness_case_signature=partial(
                _collection_replacement_literal_replacement_correctness_case_signature,
                route=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["pattern"],
            ),
            workload_signature=partial(
                _collection_replacement_literal_replacement_workload_signature,
                include_workload=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR,
                workload_kind="direct Pattern",
            ),
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-grouped-callable-replacement",
            manifest_paths=(COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=_workload_case_pair_anchor_expectations(
                COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=_is_collection_replacement_grouped_callable_workload,
            correctness_case_signature=(
                _collection_replacement_grouped_callable_correctness_case_signature
            ),
            workload_signature=_collection_replacement_grouped_callable_workload_signature,
            run_callback_result_parity=True,
        ),
    )


def _collection_replacement_literal_replacement_correctness_case_signature(
    case: Any,
    *,
    route: _CollectionReplacementLiteralReplacementRoute | None = None,
    case_ids: tuple[str, ...] | None = None,
    expected_operation: str | None = None,
    operation_prefix: str | None = None,
    args_offset: int | None = None,
) -> tuple[Any, ...] | None:
    if route is not None:
        case_ids = route.case_ids()
        expected_operation = route.expected_operation
        operation_prefix = route.operation_prefix
        args_offset = route.args_offset

    if expected_operation is None or operation_prefix is None or args_offset is None:
        raise AssertionError(
            "literal replacement correctness signatures require either a route "
            "or explicit operation metadata"
        )
    if case.manifest_id != "collection-replacement-workflows":
        return None
    if case_ids is not None and case.case_id not in case_ids:
        return None
    if case.operation != expected_operation or case.kwargs:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.use_compiled_pattern:
        return None
    pattern = case_pattern(case)
    if pattern not in {"abc", b"abc"}:
        return None
    if len(case.args) <= args_offset:
        return None
    if case.args[args_offset] not in {"x", b"x"}:
        return None
    trailing_args = case.args[args_offset:]
    if len(trailing_args) not in {2, 3}:
        return None
    if len(trailing_args) == 3 and type(trailing_args[2]) is not int:
        return None
    return (
        f"{operation_prefix}.{case.helper}",
        pattern,
        freeze_signature_value(list(trailing_args)),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_literal_replacement_workload_signature(
    workload: Any,
    *,
    include_workload: Callable[[Any], bool],
    workload_kind: str,
) -> tuple[Any, ...]:
    if not include_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement "
            f"{workload_kind} literal replacement workload {workload.workload_id!r}"
        )
    args = [
        workload.replacement_payload(),
        workload.haystack_payload(),
    ]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(args),
        (),
        workload.flags,
        workload.text_model,
    )
def _collection_replacement_has_expected_unexpected_keyword_error(
    workload: Any,
) -> bool:
    keyword_names = tuple(workload.kwargs)
    if len(keyword_names) != 1:
        return False
    keyword_name = keyword_names[0]
    expected_keyword_parameter = (
        benchmark_test_support._collection_replacement_keyword_parameter_name(
            workload
        )
    )
    if keyword_name == expected_keyword_parameter:
        return False
    expected_exception = workload.expected_exception
    if expected_exception is None or expected_exception.get("type") != "TypeError":
        return False
    message_substring = expected_exception.get("message_substring")
    if not isinstance(message_substring, str):
        return False
    if f"unexpected keyword argument '{keyword_name}'" in message_substring:
        return True
    if workload.operation.startswith("pattern."):
        helper_name = workload.operation.removeprefix("pattern.")
        return (
            message_substring
            == f"'{keyword_name}' is an invalid keyword argument for {helper_name}()"
        )
    return False


def _module_workflow_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.helper not in {"split", "sub", "subn"} or case.kwargs:
        return None
    if case.operation == "module_call":
        if case.use_compiled_pattern or not case.include_pattern_arg:
            return None
    elif case.operation != "pattern_call":
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        case_pattern(case),
        module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _collection_replacement_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation in {"module.split", "pattern.split"}:
        return (
            workload.haystack_payload(),
            workload.maxsplit,
        )
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count,
        )
    raise AssertionError(
        "unexpected collection/replacement positional-indexlike workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("module.").removeprefix("pattern."),
        workload.pattern_payload(),
        module_workflow_positional_args_signature(
            _collection_replacement_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_collection_replacement_positional_indexlike_workload(workload: Any) -> bool:
    keyword_parameter = (
        benchmark_test_support._collection_replacement_keyword_parameter_name(
            workload
        )
    )
    if keyword_parameter == "maxsplit":
        parameter_payload = workload.maxsplit
    elif keyword_parameter == "count":
        parameter_payload = workload.count
    else:
        parameter_payload = None
    return (
        not workload.kwargs
        and workload.expected_exception is None
        and benchmark_test_support._is_encoded_indexlike_payload(parameter_payload)
    )

def _collection_replacement_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if not case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    use_compiled_pattern = False
    if case.operation == "module_call":
        use_compiled_pattern = case.use_compiled_pattern
    elif case.operation != "pattern_call":
        return None
    return (
        f"{'module' if case.operation == 'module_call' else 'pattern'}.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        use_compiled_pattern,
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_keyword_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    positional_keyword_field = (
        benchmark_test_support._collection_replacement_positional_keyword_field(
            workload
        )
    )
    if workload.operation in {"module.split", "pattern.split"}:
        args: list[object] = [workload.haystack_payload()]
        if positional_keyword_field == "maxsplit":
            args.append(workload.maxsplit)
        return tuple(args)
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        args: list[object] = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if positional_keyword_field == "count":
            args.append(workload.count)
        return tuple(args)
    raise AssertionError(
        "unexpected collection/replacement keyword workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not benchmark_test_support._is_collection_replacement_keyword_workload(
        workload
    ):
        raise AssertionError(
            "unexpected collection/replacement keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_collection_replacement_keyword_workload_args(workload))
        ),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _collection_replacement_compiled_pattern_success_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, str):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, bytes):
        return None
    return (
        operation,
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_compiled_pattern_success_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "module.split":
        return (
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"module.findall", "module.finditer"}:
        return (workload.haystack_payload(),)
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected collection/replacement compiled-pattern success workload "
        f"operation {workload.operation!r}"
    )


def _collection_replacement_compiled_pattern_success_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_compiled_pattern_success_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement compiled-pattern success workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_collection_replacement_compiled_pattern_success_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_compiled_pattern_success_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is None
        and not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in {
            "module.split",
            "module.findall",
            "module.finditer",
            "module.sub",
            "module.subn",
        }
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )
def _pattern_helper_collection_replacement_keyword_error_workload(
    *,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
) -> benchmarks.Workload:
    return benchmarks.workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-error-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": "warm",
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "pattern-split-duplicate-maxsplit-keyword-warm-str",
    "pattern-split-unexpected-keyword-warm-bytes",
    "pattern-sub-duplicate-count-keyword-warm-str",
    "pattern-sub-unexpected-keyword-warm-str",
    "pattern-sub-unexpected-keyword-after-positional-count-warm-str",
    "pattern-sub-count-alias-keyword-warm-str",
    "pattern-subn-duplicate-count-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes",
    "pattern-subn-count-alias-keyword-warm-bytes",
)


def _is_collection_replacement_pattern_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        benchmark_test_support._is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = _contract_source_workloads(
    manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_pattern_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "pattern helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)


_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-search-duplicate-flags-keyword-warm-str",
    "module-fullmatch-unexpected-keyword-purged-str",
)

_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-split-duplicate-maxsplit-keyword-purged-str",
    "module-split-unexpected-keyword-purged-str",
    "module-split-unexpected-keyword-purged-bytes",
    "module-sub-duplicate-count-keyword-warm-str",
    "module-sub-unexpected-keyword-purged-str",
    "module-sub-unexpected-keyword-after-positional-count-purged-str",
    "module-sub-count-alias-keyword-purged-str",
    "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
    "module-subn-count-alias-keyword-purged-bytes",
)


def _is_collection_replacement_module_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        benchmark_test_support._is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = _contract_source_workloads(
    manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
    include_workload_selectors=(_is_module_workflow_keyword_error_workload,),
    expected_source_workload_ids=_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS,
    drift_message=(
        "module helper keyword-error surface drifted from the live source "
        "workload surface"
    ),
) + _contract_source_workloads(
    manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_module_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "module helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)


def _assert_keyword_error_workload_probe_measured(
    source_workload: Any,
    *,
    import_name: str,
    adapter_name: str,
) -> None:
    payload = benchmarks.workload_to_payload(source_workload)
    round_tripped = benchmarks.workload_from_payload(payload)

    assert payload["workload_id"] == source_workload.workload_id
    assert round_tripped.workload_id == source_workload.workload_id
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert payload["kwargs"] == source_workload.kwargs
    assert round_tripped.kwargs == source_workload.kwargs

    probe = benchmarks.run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "smoke",
    }
)
_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "pattern-split-on-bytes-string-warm-str",
    "pattern-sub-on-bytes-string-warm-str",
    "pattern-subn-on-str-string-purged-bytes",
)
_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC = (
    _SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS,
        timing_scope="pattern-helper-call",
    )
)


def _collection_replacement_wrong_text_model_source_workloads() -> tuple[Any, ...]:
    return _contract_source_workloads(
        manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_pattern_wrong_text_model_workload,
        ),
        expected_source_workload_ids=(
            _COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        ),
        drift_message=(
            "direct Pattern collection/replacement wrong-text-model surface "
            "drifted from the live source workload surface"
        ),
    )


def _collection_replacement_wrong_text_model_expected_callback_call(
    source_workload: Any,
) -> tuple[object, ...]:
    if source_workload.operation == "pattern.split":
        return (
            "pattern.split",
            source_workload.haystack_payload(),
            (source_workload.maxsplit_argument(),),
            {},
        )
    if source_workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            source_workload.operation,
            source_workload.replacement_payload(),
            source_workload.haystack_payload(),
            (source_workload.count_argument(),),
            {},
        )
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {source_workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_expected_callback_result(
    source_workload: Any,
) -> object:
    if source_workload.operation == "pattern.subn":
        return ("pattern-result", 0)
    if source_workload.operation in {"pattern.split", "pattern.sub"}:
        return "pattern-result"
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {source_workload.operation!r}"
    )


def _run_cpython_collection_replacement_wrong_text_model_workload(
    workload: Any,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    helper_name = workload.operation.removeprefix("pattern.")
    if workload.operation == "pattern.split":
        return getattr(compiled_pattern, helper_name)(
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return getattr(compiled_pattern, helper_name)(
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_haystack_index(operation: str) -> int:
    if operation in {"module.split", "module.findall", "module.finditer"}:
        return 0
    if operation in {"module.sub", "module.subn"}:
        return 1
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{operation!r}"
    )


def _collection_replacement_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "module.split":
        return (
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"module.findall", "module.finditer"}:
        return (workload.haystack_payload(),)
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not benchmark_test_support._is_collection_replacement_wrong_text_model_workload(
        workload
    ):
        raise AssertionError(
            "unexpected collection/replacement wrong-text-model workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_collection_replacement_wrong_text_model_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )
def _pattern_collection_replacement_wrong_text_model_haystack_index(
    operation: str,
) -> int:
    if operation == "pattern.split":
        return 0
    if operation in {"pattern.sub", "pattern.subn"}:
        return 1
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    operation = f"pattern.{case.helper}"
    haystack_index = _pattern_collection_replacement_wrong_text_model_haystack_index(
        operation
    )
    case_args = list(case.args)
    if len(case_args) <= haystack_index:
        return None
    haystack = case_args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        freeze_signature_value(case_args),
        (),
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_pattern_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "pattern.split":
        args: list[object] = [workload.haystack_payload()]
        if workload.maxsplit:
            args.append(workload.maxsplit_argument())
        return tuple(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if workload.count:
            args.append(workload.count_argument())
        return tuple(args)
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_pattern_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected direct Pattern collection/replacement wrong-text-model "
            f"workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(
                _collection_replacement_pattern_wrong_text_model_workload_args(
                    workload
                )
            )
        ),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.kwargs
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _is_collection_replacement_literal_replacement_workload(
    workload: Any,
    *,
    route: _CollectionReplacementLiteralReplacementRoute,
    workload_ids: tuple[str, ...] | None = None,
) -> bool:
    return (
        (workload_ids is None or workload.workload_id in workload_ids)
        and workload.operation in route.operations
        and workload.pattern == "abc"
        and workload.replacement == "x"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in route.text_models
        and (route.allowed_counts is None or workload.count in route.allowed_counts)
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR = partial(
    _is_collection_replacement_literal_replacement_workload,
    route=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["module"],
    workload_ids=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
        "module"
    ].workload_ids(),
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR = partial(
    _is_collection_replacement_literal_replacement_workload,
    route=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["pattern"],
    workload_ids=_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
        "pattern"
    ].workload_ids(),
)

_COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS = (
    ("module-sub-callable-grouped-warm-str", "module-sub-callable-grouped-str"),
    ("module-sub-callable-grouped-warm-bytes", "module-sub-callable-grouped-bytes"),
    (
        "pattern-subn-callable-named-grouped-warm-str",
        "pattern-subn-callable-named-grouped-str",
    ),
    (
        "pattern-subn-callable-named-grouped-purged-bytes",
        "pattern-subn-callable-named-grouped-bytes",
    ),
)


def _is_collection_replacement_grouped_callable_workload(workload: Any) -> bool:
    return (
        workload.workload_id
        in _workload_case_pairs_workload_ids(
            _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
        )
        and workload.operation in {"module.sub", "pattern.subn"}
        and workload.pattern in {
            "(abc)",
            b"(abc)",
            "(?P<word>abc)",
            b"(?P<word>abc)",
        }
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


def _collection_replacement_grouped_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.case_id not in _workload_case_pairs_case_ids(
        _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
    ):
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    args = [case_text_argument(case)]
    if case.helper == "subn":
        count = case.args[-1]
        if type(count) is not int:
            return None
        args.append(count)
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        freeze_signature_value(args),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_grouped_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_grouped_callable_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement grouped callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for grouped callable workload "
            f"{workload.workload_id!r}"
        )
    args = [workload.haystack_payload()]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        freeze_signature_value(args),
        (),
        workload.flags,
        workload.text_model,
    )


def _workload_ids_for_text_model(
    workload_stems: tuple[str, ...],
    *,
    text_model: str,
) -> tuple[str, ...]:
    suffix = "-bytes" if text_model == "bytes" else "-str"
    return tuple(f"{stem}{suffix}" for stem in workload_stems)


CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-bytes",
    "module-sub-callable-named-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-bytes",
    "pattern-sub-callable-named-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-purged-bytes",
    "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged",
    "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm",
    "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged",
    "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm",
    "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged",
    "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS,
    text_model="str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS,
    text_model="bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap",
    "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[8:]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[8:]
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS = (
    "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
    "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
    "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
    "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
    "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
    "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
    "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS = (
    "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
    + CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[8:]
)


CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-str",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-str",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-str",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-str",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-str",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
)
_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS = (
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged",
)
CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
    text_model="str",
)
CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
    text_model="bytes",
)


def _conditional_group_exists_quantified_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.manifest_id != "conditional-group-exists-callable-replacement-workflows":
        return None
    if "quantified" not in case.categories:
        return None
    if any(category in case.categories for category in ("alternation", "nested")):
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    count_index = 3 if case.operation == "module_call" else 2
    args = [case_text_argument(case)]
    if len(case.args) > count_index:
        count = case.args[count_index]
        if count is None:
            pass
        elif type(count) is int:
            args.append(count)
        else:
            return None
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        freeze_signature_value(args),
        "exception" in case.categories,
        "no-match" in case.categories,
        case.flags or 0,
        case.text_model or "str",
    )


def _conditional_group_exists_nested_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.manifest_id != "conditional-group-exists-callable-replacement-workflows":
        return None
    if "nested" not in case.categories:
        return None
    if any(category in case.categories for category in ("quantified", "alternation")):
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    count_index = 3 if case.operation == "module_call" else 2
    args = [case_text_argument(case)]
    if len(case.args) > count_index:
        args.append(case.args[count_index])
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        freeze_signature_value(args),
        "exception" in case.categories,
        "no-match" in case.categories,
        case.flags or 0,
        case.text_model or "str",
    )


def _conditional_group_exists_nested_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    expected_workload_ids = (
        CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
        + CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    if workload.workload_id not in expected_workload_ids:
        raise AssertionError(
            "unexpected conditional nested callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for nested "
            f"conditional workload {workload.workload_id!r}"
        )
    args: list[object] = [workload.haystack_payload()]
    if workload.count != 0:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        freeze_signature_value(args),
        workload.expected_exception is not None,
        "no-match" in workload.categories,
        workload.flags,
        workload.text_model,
    )


def _conditional_group_exists_quantified_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    expected_workload_ids = (
        CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        + CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    if workload.workload_id not in expected_workload_ids:
        raise AssertionError(
            "unexpected conditional quantified callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for quantified "
            f"conditional workload {workload.workload_id!r}"
        )
    args = [workload.haystack_payload()]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        freeze_signature_value(args),
        workload.expected_exception is not None,
        "no-match" in workload.categories,
        workload.flags,
        workload.text_model,
    )


COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS = (
    _collection_replacement_standard_benchmark_definitions()
)
