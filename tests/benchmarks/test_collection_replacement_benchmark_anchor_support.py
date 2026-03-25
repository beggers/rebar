from __future__ import annotations

import json
import pathlib
import re
from types import SimpleNamespace

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    Workload,
    build_callable,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import synthetic_workload
from tests.benchmarks.benchmark_test_support import (
    STANDARD_BENCHMARK_DEFINITIONS,
    compiled_pattern_contract_expected_build_calls,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
    assert_zero_gap_manifest_workloads_measured,
    _write_test_manifest,
    assert_pattern_helper_wrong_text_model_payload_round_trip as _assert_wrong_text_model_payload_round_trip,
    live_manifest_workloads,
    manifest_workloads,
    published_cases_by_id,
    selected_manifest_workloads,
)
from tests.benchmarks import collection_replacement_benchmark_anchor_support as support
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkModule,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    run_benchmark_workload_with_cpython,
)
from tests.python.fixture_parity_support import IndexLike

_COLLECTION_REPLACEMENT_STANDARD_DEFINITION_NAMES = (
    "collection-replacement-module-positional-indexlike",
    "collection-replacement-keyword",
    "collection-replacement-compiled-pattern-literal-success",
    "collection-replacement-compiled-pattern-wrong-text-model",
    "pattern-helper-collection-replacement-wrong-text-model",
    "collection-replacement-pattern-findall-bounded",
    "collection-replacement-pattern-finditer-bounded",
    "collection-replacement-pattern-split",
    "collection-replacement-module-literal-replacement",
    "collection-replacement-pattern-literal-replacement",
    "collection-replacement-grouped-callable-replacement",
)


def _collection_replacement_case(
    *,
    helper: str,
    operation: str,
    args: tuple[object, ...],
    kwargs: dict[str, object] | None = None,
    pattern: str = "abc",
    text_model: str | None = "str",
    flags: int = 0,
    use_compiled_pattern: bool = False,
    include_pattern_arg: bool = True,
    case_id: str = "synthetic-case",
) -> object:
    pattern_value = pattern.encode() if text_model == "bytes" else pattern
    return SimpleNamespace(
        case_id=case_id,
        helper=helper,
        operation=operation,
        args=args,
        kwargs={} if kwargs is None else kwargs,
        pattern=pattern,
        flags=flags,
        text_model=text_model,
        use_compiled_pattern=use_compiled_pattern,
        include_pattern_arg=include_pattern_arg,
        pattern_payload=lambda: pattern_value,
    )


def _group_callable_replacement(
    *,
    group_reference: object,
    prefix: object = "<",
    suffix: object = ">",
) -> object:
    def replacement(
        _match: object,
        *,
        _group_reference: object = group_reference,
        _prefix: object = prefix,
        _suffix: object = suffix,
    ) -> str:
        return ""

    return replacement


def test_collection_replacement_pattern_wrong_text_model_support_surface_is_owner_module_owned_without_local_duplicates(
) -> None:
    import sys

    from tests.benchmarks.benchmark_test_support import (
        top_level_module_definition_and_assignment_names,
    )

    local_definition_names, local_assignment_names = (
        top_level_module_definition_and_assignment_names(sys.modules[__name__])
    )

    expected_definition_names = {
        "_collection_replacement_wrong_text_model_source_workloads",
        "_collection_replacement_wrong_text_model_expected_callback_call",
        "_collection_replacement_wrong_text_model_expected_callback_result",
        "_run_cpython_collection_replacement_wrong_text_model_workload",
        "_pattern_collection_replacement_wrong_text_model_haystack_index",
        "_collection_replacement_pattern_wrong_text_model_correctness_case_signature",
        "_collection_replacement_pattern_wrong_text_model_workload_args",
        "_collection_replacement_pattern_wrong_text_model_workload_signature",
        "_is_collection_replacement_pattern_wrong_text_model_workload",
    }
    expected_assignment_names = {
        "_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC",
    }

    for name in expected_definition_names | expected_assignment_names:
        assert hasattr(support, name)

    assert expected_definition_names.isdisjoint(local_definition_names)
    assert expected_assignment_names.isdisjoint(local_assignment_names)


def test_positional_indexlike_workloads_stay_in_scope_and_keep_expected_signature() -> None:
    split_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-indexlike",
        operation="module.split",
        haystack="zabcabc",
        maxsplit={"type": "indexlike", "value": 2},
    )
    sub_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="pattern-sub-indexlike-bytes",
        operation="pattern.sub",
        haystack="abcabc",
        replacement="x",
        count={"type": "indexlike", "value": 1},
        text_model="bytes",
    )

    assert support._is_collection_replacement_positional_indexlike_workload(
        split_workload
    )
    assert support._collection_replacement_positional_indexlike_workload_signature(
        split_workload
    ) == (
        "split",
        "abc",
        (("str", "zabcabc"), ("indexlike", 2)),
        "str",
    )

    assert support._is_collection_replacement_positional_indexlike_workload(
        sub_workload
    )
    assert support._collection_replacement_positional_indexlike_workload_signature(
        sub_workload
    ) == (
        "sub",
        b"abc",
        (("bytes", b"x"), ("bytes", b"abcabc"), ("indexlike", 1)),
        "bytes",
    )


def test_positional_indexlike_workload_filter_rejects_keyword_and_non_indexlike_rows() -> None:
    keyword_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-keyword",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": {"type": "indexlike", "value": 1}},
    )
    plain_int_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-sub-plain-int",
        operation="module.sub",
        haystack="abcabc",
        replacement="x",
        count=1,
    )

    assert not support._is_collection_replacement_positional_indexlike_workload(
        keyword_workload
    )
    assert not support._is_collection_replacement_positional_indexlike_workload(
        plain_int_workload
    )


def test_positional_indexlike_correctness_case_signature_requires_collection_call_shape() -> None:
    matching_case = _collection_replacement_case(
        helper="split",
        operation="module_call",
        args=("zabcabc", IndexLike(2)),
    )
    compiled_pattern_case = _collection_replacement_case(
        helper="split",
        operation="module_call",
        args=("zabcabc", IndexLike(2)),
        use_compiled_pattern=True,
    )
    unsupported_helper_case = _collection_replacement_case(
        helper="search",
        operation="pattern_call",
        args=("zabcabc", 2),
    )

    assert support._module_workflow_positional_indexlike_correctness_case_signature(
        matching_case
    ) == (
        "split",
        "abc",
        (("str", "zabcabc"), ("indexlike", 2)),
        "str",
    )
    assert (
        support._module_workflow_positional_indexlike_correctness_case_signature(
            compiled_pattern_case
        )
        is None
    )
    assert (
        support._module_workflow_positional_indexlike_correctness_case_signature(
            unsupported_helper_case
        )
        is None
    )


def test_keyword_workloads_cover_expected_keyword_duplicate_and_unexpected_keyword_rows() -> None:
    expected_keyword_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-keyword-indexlike",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": {"type": "indexlike", "value": 1}},
    )
    duplicate_keyword_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="pattern-sub-duplicate-count",
        operation="pattern.sub",
        haystack="abc",
        replacement="x",
        count=1,
        kwargs={"missing": 1},
        expected_exception={
            "type": "TypeError",
            "message_substring": "sub() takes at most 3 arguments (4 given)",
        },
    )
    unexpected_keyword_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-subn-unexpected-keyword",
        operation="module.subn",
        haystack="abc",
        replacement="x",
        text_model="bytes",
        kwargs={"missing": 1},
        expected_exception={
            "type": "TypeError",
            "message_substring": "subn() got an unexpected keyword argument 'missing'",
        },
    )

    assert support._is_collection_replacement_keyword_workload(
        expected_keyword_workload
    )
    assert support._collection_replacement_keyword_workload_signature(
        expected_keyword_workload
    ) == (
        "module.split",
        "abc",
        ("zabcabc",),
        (("maxsplit", "indexlike", 1),),
        False,
        0,
        "str",
    )

    assert support._is_collection_replacement_keyword_workload(
        duplicate_keyword_workload
    )
    assert support._collection_replacement_positional_keyword_field(
        duplicate_keyword_workload
    ) == "count"
    assert support._collection_replacement_keyword_workload_signature(
        duplicate_keyword_workload
    ) == (
        "pattern.sub",
        "abc",
        ("x", "abc", 1),
        (("missing", "int", 1),),
        False,
        0,
        "str",
    )

    assert support._is_collection_replacement_keyword_workload(
        unexpected_keyword_workload
    )
    assert support._collection_replacement_has_expected_unexpected_keyword_error(
        unexpected_keyword_workload
    )
    assert support._collection_replacement_keyword_workload_signature(
        unexpected_keyword_workload
    ) == (
        "module.subn",
        b"abc",
        (b"x", b"abc"),
        (("missing", "int", 1),),
        False,
        0,
        "bytes",
    )


def test_keyword_workload_filter_rejects_non_collection_keyword_shapes() -> None:
    multiple_keyword_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-sub-multiple-keywords",
        operation="module.sub",
        haystack="abcabc",
        replacement="x",
        kwargs={"count": 1, "missing": 2},
        expected_exception={
            "type": "TypeError",
            "message_substring": "sub() got an unexpected keyword argument 'missing'",
        },
    )
    search_keyword_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-search-keyword",
        operation="module.search",
        haystack="abcabc",
        kwargs={"flags": 1},
    )

    assert not support._is_collection_replacement_keyword_workload(
        multiple_keyword_workload
    )
    assert not support._is_collection_replacement_keyword_workload(
        search_keyword_workload
    )


def test_keyword_correctness_case_signature_preserves_call_shape_and_compiled_pattern_flag() -> None:
    module_case = _collection_replacement_case(
        helper="subn",
        operation="module_call",
        args=("x", "abcabc"),
        kwargs={"count": IndexLike(2)},
        text_model="bytes",
        use_compiled_pattern=True,
    )
    pattern_case = _collection_replacement_case(
        helper="split",
        operation="pattern_call",
        args=("abcabc",),
        kwargs={"maxsplit": 1},
    )

    assert support._collection_replacement_keyword_correctness_case_signature(
        module_case
    ) == (
        "module.subn",
        b"abc",
        ("x", "abcabc"),
        (("count", "indexlike", 2),),
        True,
        0,
        "bytes",
    )
    assert support._collection_replacement_keyword_correctness_case_signature(
        pattern_case
    ) == (
        "pattern.split",
        "abc",
        ("abcabc",),
        (("maxsplit", "int", 1),),
        False,
        0,
        "str",
    )


def test_collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=lambda workload: (
                support._is_collection_replacement_keyword_workload(workload)
                and workload.operation.startswith("pattern.")
            ),
        )
    )

    assert expected_measured_workload_ids == (
        "pattern-split-maxsplit-keyword-warm-str",
        "pattern-split-maxsplit-bool-keyword-warm-str",
        "pattern-split-maxsplit-indexlike-keyword-warm-str",
        "pattern-split-duplicate-maxsplit-keyword-warm-str",
        "pattern-split-unexpected-keyword-warm-bytes",
        "pattern-sub-count-keyword-purged-bytes",
        "pattern-sub-count-bool-keyword-purged-bytes",
        "pattern-sub-count-bool-true-keyword-purged-bytes",
        "pattern-sub-count-indexlike-keyword-purged-bytes",
        "pattern-sub-duplicate-count-keyword-warm-str",
        "pattern-sub-unexpected-keyword-warm-str",
        "pattern-sub-unexpected-keyword-after-positional-count-warm-str",
        "pattern-sub-count-alias-keyword-warm-str",
        "pattern-subn-count-keyword-warm-str",
        "pattern-subn-count-bool-keyword-warm-str",
        "pattern-subn-count-bool-false-keyword-warm-str",
        "pattern-subn-count-indexlike-keyword-warm-str",
        "pattern-subn-duplicate-count-keyword-warm-bytes",
        "pattern-subn-unexpected-keyword-warm-bytes",
        "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes",
        "pattern-subn-count-alias-keyword-warm-bytes",
    )
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=lambda workload: (
                support._is_collection_replacement_keyword_workload(workload)
                and workload.operation.startswith("module.")
            ),
        )
    )

    assert expected_measured_workload_ids == (
        "module-split-maxsplit-keyword-purged-bytes",
        "module-split-maxsplit-bool-keyword-purged-bytes",
        "module-split-maxsplit-indexlike-keyword-purged-bytes",
        "module-split-maxsplit-keyword-purged-str-compiled-pattern",
        "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
        "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
        "module-split-duplicate-maxsplit-keyword-purged-str",
        "module-split-unexpected-keyword-purged-str",
        "module-split-unexpected-keyword-purged-bytes",
        "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
        "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
        "module-sub-count-keyword-warm-str",
        "module-sub-count-bool-keyword-warm-str",
        "module-sub-count-bool-false-keyword-warm-str",
        "module-sub-count-indexlike-keyword-warm-str",
        "module-sub-count-keyword-warm-str-compiled-pattern",
        "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
        "module-sub-count-bool-keyword-warm-str-compiled-pattern",
        "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
        "module-sub-duplicate-count-keyword-warm-str",
        "module-sub-unexpected-keyword-purged-str",
        "module-sub-unexpected-keyword-after-positional-count-purged-str",
        "module-sub-count-alias-keyword-purged-str",
        "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
        "module-sub-unexpected-keyword-purged-str-compiled-pattern",
        "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
        "module-sub-count-alias-keyword-purged-str-compiled-pattern",
        "module-subn-count-keyword-purged-bytes",
        "module-subn-count-bool-keyword-purged-bytes",
        "module-subn-count-bool-true-keyword-purged-bytes",
        "module-subn-count-indexlike-keyword-purged-bytes",
        "module-subn-duplicate-count-keyword-warm-bytes",
        "module-subn-unexpected-keyword-purged-bytes",
        "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
        "module-subn-count-alias-keyword-purged-bytes",
        "module-subn-count-keyword-purged-bytes-compiled-pattern",
        "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
        "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
        "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
        "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
        "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
        "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
        "module-subn-count-alias-keyword-purged-bytes-compiled-pattern",
    )
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=support._is_collection_replacement_positional_indexlike_workload,
        )
    )

    assert expected_measured_workload_ids == (
        "module-split-maxsplit-indexlike-positional-purged-bytes",
        "module-sub-count-indexlike-positional-warm-str",
        "module-subn-count-indexlike-positional-purged-bytes",
        "pattern-split-maxsplit-indexlike-positional-warm-str",
        "pattern-sub-count-indexlike-positional-purged-bytes",
        "pattern-subn-count-indexlike-positional-warm-str",
    )
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
        "findall"
    ].workload_ids()
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "findall"
            ].includes_workload,
        )
    )

    assert len(expected_measured_workload_ids) == 3
    assert selected_measured_workload_ids == expected_measured_workload_ids
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
        "finditer"
    ].workload_ids()
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "finditer"
            ].includes_workload,
        )
    )

    assert len(expected_measured_workload_ids) == 3
    assert selected_measured_workload_ids == expected_measured_workload_ids
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_pattern_split_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
        "split"
    ].workload_ids()
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "split"
            ].includes_workload,
        )
    )

    assert len(expected_measured_workload_ids) == 3
    assert selected_measured_workload_ids == expected_measured_workload_ids
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR,
        )
    )

    assert selected_measured_workload_ids == support._COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
        "pattern"
    ].workload_ids()
    assert len(selected_measured_workload_ids) == 20
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR,
        )
    )

    assert expected_measured_workload_ids == support._COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
        "module"
    ].workload_ids()
    assert len(expected_measured_workload_ids) == 18
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit() -> None:
    include_workload = support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR
    workload_signatures = {
        support._collection_replacement_literal_replacement_workload_signature(
            workload,
            include_workload=include_workload,
            workload_kind="module",
        )
        for workload in manifest_workloads("collection_replacement_boundary.py")
        if include_workload(workload)
    }
    unbenchmarked_case_ids = tuple(
        case.case_id
        for case in published_cases_by_id().values()
        if (
            signature := (
                support._collection_replacement_literal_replacement_correctness_case_signature(
                    case,
                    route=support._COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
                        "module"
                    ],
                )
            )
        )
        is not None
        and signature not in workload_signatures
    )

    assert unbenchmarked_case_ids == ()


def test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit() -> None:
    include_workload = support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR
    workload_signatures = {
        support._collection_replacement_literal_replacement_workload_signature(
            workload,
            include_workload=include_workload,
            workload_kind="direct Pattern",
        )
        for workload in manifest_workloads("collection_replacement_boundary.py")
        if include_workload(workload)
    }
    unbenchmarked_case_ids = tuple(
        case.case_id
        for case in published_cases_by_id().values()
        if (
            signature := (
                support._collection_replacement_literal_replacement_correctness_case_signature(
                    case,
                    route=support._COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES[
                        "pattern"
                    ],
                )
            )
        )
        is not None
        and signature not in workload_signatures
    )

    assert unbenchmarked_case_ids == ()


def test_collection_replacement_manifest_keeps_grouped_callable_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(selected_manifest_workloads(manifest_path))
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=support._is_collection_replacement_grouped_callable_workload,
        )
    )

    assert expected_measured_workload_ids == tuple(
        workload_id
        for workload_id, _ in support._COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
    )
    assert len(expected_measured_workload_ids) == 4
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_grouped_callable_anchor_contract_in_combined_suite_uses_owner_helpers() -> None:
    import importlib
    import inspect

    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definitions = [
        definition
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if definition.name == "collection-replacement-grouped-callable-replacement"
    ]

    assert len(definitions) == 1
    definition = definitions[0]
    assert definition.correctness_case_signature is (
        support._collection_replacement_grouped_callable_correctness_case_signature
    )
    assert definition.workload_signature is (
        support._collection_replacement_grouped_callable_workload_signature
    )
    combined_source = inspect.getsource(combined_suite)
    assert "def _collection_replacement_grouped_callable_correctness_case_signature(" not in combined_source
    assert "def _collection_replacement_grouped_callable_workload_signature(" not in combined_source


def test_collection_replacement_standard_definitions_are_reused_by_standard_inventory(
) -> None:
    owner_definitions = support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS
    standard_definitions = tuple(
        definition
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if definition.name in _COLLECTION_REPLACEMENT_STANDARD_DEFINITION_NAMES
    )

    assert isinstance(owner_definitions, tuple)
    assert tuple(definition.name for definition in owner_definitions) == (
        _COLLECTION_REPLACEMENT_STANDARD_DEFINITION_NAMES
    )
    assert tuple(definition.name for definition in standard_definitions) == (
        _COLLECTION_REPLACEMENT_STANDARD_DEFINITION_NAMES
    )
    assert standard_definitions == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_definitions, owner_definitions
        )
    )


def test_grouped_callable_correctness_case_signature_keeps_live_pair_shapes() -> None:
    cases = published_cases_by_id()

    assert {
        case_id: support._collection_replacement_grouped_callable_correctness_case_signature(
            cases[case_id]
        )
        for _, case_id in support._COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
    } == {
        "module-sub-callable-grouped-str": (
            "module.sub",
            "(abc)",
            ("callable_match_group", 1, "<", ">"),
            ("abcabc",),
            (),
            0,
            "str",
        ),
        "module-sub-callable-grouped-bytes": (
            "module.sub",
            b"(abc)",
            ("callable_match_group", 1, b"<", b">"),
            (b"abcabc",),
            (),
            0,
            "bytes",
        ),
        "pattern-subn-callable-named-grouped-str": (
            "pattern.subn",
            "(?P<word>abc)",
            ("callable_match_group", "word", "<", ">"),
            ("abcabc", 1),
            (),
            0,
            "str",
        ),
        "pattern-subn-callable-named-grouped-bytes": (
            "pattern.subn",
            b"(?P<word>abc)",
            ("callable_match_group", "word", b"<", b">"),
            (b"abcabc", 1),
            (),
            0,
            "bytes",
        ),
    }

    assert (
        support._collection_replacement_grouped_callable_correctness_case_signature(
            _collection_replacement_case(
                case_id="not-a-paired-case",
                helper="sub",
                operation="module_call",
                args=(
                    "(abc)",
                    _group_callable_replacement(group_reference=1),
                    "abcabc",
                ),
                pattern="(abc)",
            )
        )
        is None
    )


def test_grouped_callable_correctness_case_signature_rejects_non_callable_and_wrong_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = published_cases_by_id()["module-sub-callable-grouped-str"]
    observed_replacements: list[object] = []

    def fake_callable_match_group_signature(
        replacement: object,
    ) -> tuple[object, ...] | None:
        observed_replacements.append(replacement)
        return ("sentinel", 1, "<", ">")

    monkeypatch.setattr(
        support,
        "callable_match_group_signature",
        fake_callable_match_group_signature,
    )

    assert support._collection_replacement_grouped_callable_correctness_case_signature(
        case
    ) == (
        "module.sub",
        "(abc)",
        ("sentinel", 1, "<", ">"),
        ("abcabc",),
        (),
        0,
        "str",
    )
    assert observed_replacements == [case.args[1]]
    monkeypatch.undo()

    assert (
        support._collection_replacement_grouped_callable_correctness_case_signature(
            _collection_replacement_case(
                case_id="module-sub-callable-grouped-str",
                helper="split",
                operation="module_call",
                args=(
                    "(abc)",
                    _group_callable_replacement(group_reference=1),
                    "abcabc",
                ),
                pattern="(abc)",
            )
        )
        is None
    )
    assert (
        support._collection_replacement_grouped_callable_correctness_case_signature(
            _collection_replacement_case(
                case_id="module-sub-callable-grouped-str",
                helper="sub",
                operation="module_call",
                args=("(abc)", "x", "abcabc"),
                pattern="(abc)",
            )
        )
        is None
    )


def test_grouped_callable_workload_signature_keeps_live_pair_shapes() -> None:
    workloads = live_manifest_workloads(
        "collection_replacement_boundary.py",
        tuple(
            workload_id
            for workload_id, _ in support._COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
        ),
    )

    assert {
        workload.workload_id: support._collection_replacement_grouped_callable_workload_signature(
            workload
        )
        for workload in workloads
    } == {
        "module-sub-callable-grouped-warm-str": (
            "module.sub",
            "(abc)",
            ("callable_match_group", 1, "<", ">"),
            ("abcabc",),
            (),
            0,
            "str",
        ),
        "module-sub-callable-grouped-warm-bytes": (
            "module.sub",
            b"(abc)",
            ("callable_match_group", 1, b"<", b">"),
            (b"abcabc",),
            (),
            0,
            "bytes",
        ),
        "pattern-subn-callable-named-grouped-warm-str": (
            "pattern.subn",
            "(?P<word>abc)",
            ("callable_match_group", "word", "<", ">"),
            ("abcabc", 1),
            (),
            0,
            "str",
        ),
        "pattern-subn-callable-named-grouped-purged-bytes": (
            "pattern.subn",
            b"(?P<word>abc)",
            ("callable_match_group", "word", b"<", b">"),
            (b"abcabc", 1),
            (),
            0,
            "bytes",
        ),
    }


def test_grouped_callable_workload_signature_rejects_non_pair_and_non_callable_replacements(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workload = live_manifest_workloads(
        "collection_replacement_boundary.py",
        ("module-sub-callable-grouped-warm-str",),
    )[0]
    observed_replacements: list[object] = []

    def fake_callable_match_group_signature(
        replacement: object,
    ) -> tuple[object, ...] | None:
        observed_replacements.append(replacement)
        return ("sentinel", 1, "<", ">")

    monkeypatch.setattr(
        support,
        "callable_match_group_signature",
        fake_callable_match_group_signature,
    )

    assert support._collection_replacement_grouped_callable_workload_signature(
        workload
    ) == (
        "module.sub",
        "(abc)",
        ("sentinel", 1, "<", ">"),
        ("abcabc",),
        (),
        0,
        "str",
    )
    assert len(observed_replacements) == 1
    monkeypatch.undo()

    with pytest.raises(
        AssertionError,
        match="unexpected collection/replacement grouped callable workload",
    ):
        support._collection_replacement_grouped_callable_workload_signature(
            synthetic_workload(
                manifest_id="collection-replacement-boundary",
                workload_id="not-a-paired-workload",
                operation="module.sub",
                pattern="(abc)",
                haystack="abcabc",
                replacement={
                    "type": "callable_match_group",
                    "group": 1,
                    "prefix": "<",
                    "suffix": ">",
                },
            )
        )

    with pytest.raises(
        AssertionError,
        match="expected callable_match_group replacement for grouped callable workload",
    ):
        support._collection_replacement_grouped_callable_workload_signature(
            synthetic_workload(
                manifest_id="collection-replacement-boundary",
                workload_id="module-sub-callable-grouped-warm-str",
                operation="module.sub",
                pattern="(abc)",
                haystack="abcabc",
                replacement="x",
            )
        )


def test_conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers() -> None:
    import importlib
    import inspect

    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    combined_source = inspect.getsource(combined_suite)

    assert (
        combined_suite._conditional_group_exists_nested_callable_correctness_case_signature
        is support._conditional_group_exists_nested_callable_correctness_case_signature
    )
    assert (
        combined_suite._conditional_group_exists_nested_callable_workload_signature
        is support._conditional_group_exists_nested_callable_workload_signature
    )
    assert (
        combined_suite._conditional_group_exists_quantified_callable_correctness_case_signature
        is support._conditional_group_exists_quantified_callable_correctness_case_signature
    )
    assert (
        combined_suite._conditional_group_exists_quantified_callable_workload_signature
        is support._conditional_group_exists_quantified_callable_workload_signature
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    assert (
        combined_suite._workload_ids_for_text_model
        is support._workload_ids_for_text_model
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS
    )
    assert (
        "def _conditional_group_exists_nested_callable_correctness_case_signature("
        not in combined_source
    )
    assert (
        "def _conditional_group_exists_nested_callable_workload_signature("
        not in combined_source
    )
    assert (
        "def _conditional_group_exists_quantified_callable_correctness_case_signature("
        not in combined_source
    )
    assert (
        "def _conditional_group_exists_quantified_callable_workload_signature("
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS ="
        not in combined_source
    )
    assert "def _workload_ids_for_text_model(" not in combined_source
    assert "CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS =" not in combined_source
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS ="
        not in combined_source
    )


def test_quantified_conditional_callable_combined_slice_expectations_use_owner_workload_ids() -> None:
    import importlib

    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    expectations_by_slice_id = {
        expectation.slice_id: expectation
        for expectation in combined_suite.SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    }

    assert (
        expectations_by_slice_id[
            "quantified-callable-replacement-str-rows"
        ].expected_workload_ids
        is support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
    )
    assert (
        expectations_by_slice_id[
            "quantified-callable-replacement-bytes-rows"
        ].expected_workload_ids
        is support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
    )


def test_conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers() -> None:
    import importlib
    import inspect

    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    combined_source = inspect.getsource(combined_suite)

    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
    )
    assert (
        combined_suite.CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS
        is support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS =" not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS ="
        not in combined_source
    )
    assert (
        "CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS ="
        not in combined_source
    )


def test_conditional_callable_none_count_workload_id_expansion_preserves_stem_order() -> None:
    stems = (
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

    assert support._workload_ids_for_text_model(stems, text_model="str") == (
        support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
    )
    assert support._workload_ids_for_text_model(stems, text_model="bytes") == (
        support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
    )


def test_conditional_callable_alternation_round_trip_workload_ids_keep_interleaved_order() -> None:
    assert support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS == (
        support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[:8]
        + support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[:8]
        + support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[8:]
        + support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[8:]
    )


def test_conditional_template_round_trip_workload_ids_keep_bytes_leading_shape() -> None:
    assert support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS == (
        support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[:8]
        + support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
        + support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[8:]
    )


def test_nested_conditional_callable_correctness_case_signature_keeps_live_tuple_shapes() -> None:
    cases = published_cases_by_id()

    assert {
        case_id: support._conditional_group_exists_nested_callable_correctness_case_signature(
            cases[case_id]
        )
        for case_id in (
            "module-sub-callable-conditional-group-exists-nested-present-str",
            "module-subn-callable-conditional-group-exists-nested-absent-str",
            "pattern-sub-callable-conditional-group-exists-nested-present-str",
            "pattern-subn-callable-conditional-group-exists-nested-absent-str",
            "module-sub-callable-conditional-group-exists-nested-present-bytes",
            "module-subn-callable-conditional-group-exists-nested-absent-bytes",
            "pattern-sub-callable-conditional-group-exists-nested-present-bytes",
            "pattern-subn-callable-conditional-group-exists-nested-absent-bytes",
            "module-sub-callable-named-conditional-group-exists-nested-present-str",
            "module-subn-callable-named-conditional-group-exists-nested-absent-str",
            "pattern-sub-callable-named-conditional-group-exists-nested-present-str",
            "pattern-subn-callable-named-conditional-group-exists-nested-absent-str",
            "module-sub-callable-named-conditional-group-exists-nested-present-bytes",
            "module-subn-callable-named-conditional-group-exists-nested-absent-bytes",
            "pattern-sub-callable-named-conditional-group-exists-nested-present-bytes",
            "pattern-subn-callable-named-conditional-group-exists-nested-absent-bytes",
        )
    } == {
        "module-sub-callable-conditional-group-exists-nested-present-str": (
            "module.sub",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-conditional-group-exists-nested-absent-str": (
            "module.subn",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-conditional-group-exists-nested-present-str": (
            "pattern.sub",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-conditional-group-exists-nested-absent-str": (
            "pattern.subn",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-conditional-group-exists-nested-present-bytes": (
            "module.sub",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-conditional-group-exists-nested-absent-bytes": (
            "module.subn",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-conditional-group-exists-nested-present-bytes": (
            "pattern.sub",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-conditional-group-exists-nested-absent-bytes": (
            "pattern.subn",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "module-sub-callable-named-conditional-group-exists-nested-present-str": (
            "module.sub",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-named-conditional-group-exists-nested-absent-str": (
            "module.subn",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-named-conditional-group-exists-nested-present-str": (
            "pattern.sub",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-named-conditional-group-exists-nested-absent-str": (
            "pattern.subn",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-named-conditional-group-exists-nested-present-bytes": (
            "module.sub",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-named-conditional-group-exists-nested-absent-bytes": (
            "module.subn",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-named-conditional-group-exists-nested-present-bytes": (
            "pattern.sub",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-named-conditional-group-exists-nested-absent-bytes": (
            "pattern.subn",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
    }


def test_nested_conditional_callable_workload_signature_keeps_live_tuple_shapes() -> None:
    workload_ids = (
        "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
        "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-str",
        "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-str",
        "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-str",
        "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
        "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
        "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
        "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
        "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-str",
        "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-str",
        "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-str",
        "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-str",
        "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
        "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
        "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
        "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
    )
    workloads = live_manifest_workloads(
        "conditional_group_exists_boundary.py",
        workload_ids,
    )

    assert {
        workload.workload_id: support._conditional_group_exists_nested_callable_workload_signature(
            workload
        )
        for workload in workloads
    } == {
        "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str": (
            "module.sub",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-str": (
            "module.subn",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-str": (
            "pattern.sub",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-str": (
            "pattern.subn",
            "a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes": (
            "module.sub",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes": (
            "module.subn",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes": (
            "pattern.sub",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes": (
            "pattern.subn",
            b"a(b)?c(?(1)(?(1)d|e)|f)",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-str": (
            "module.sub",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-str": (
            "module.subn",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-str": (
            "pattern.sub",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzabcdzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-str": (
            "pattern.subn",
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", "", "x"),
            ("zzacfzz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes": (
            "module.sub",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes": (
            "module.subn",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes": (
            "pattern.sub",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcdzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes": (
            "pattern.subn",
            b"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzacfzz", 1),
            True,
            False,
            0,
            "bytes",
        ),
    }


def test_nested_conditional_callable_workload_signature_rejects_non_owned_rows_and_non_callable_replacements() -> None:
    with pytest.raises(
        AssertionError,
        match="unexpected conditional nested callable workload",
    ):
        support._conditional_group_exists_nested_callable_workload_signature(
            synthetic_workload(
                manifest_id="conditional-group-exists-boundary",
                workload_id="not-an-owned-nested-callable-row",
                operation="module.sub",
                pattern="a(b)?c(?(1)(?(1)d|e)|f)",
                haystack="zzabcdzz",
                replacement={
                    "type": "callable_match_group",
                    "group": 1,
                    "prefix": "<",
                    "suffix": ">",
                },
            )
        )

    with pytest.raises(
        AssertionError,
        match="expected callable_match_group replacement for nested conditional workload",
    ):
        support._conditional_group_exists_nested_callable_workload_signature(
            synthetic_workload(
                manifest_id="conditional-group-exists-boundary",
                workload_id="module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
                operation="module.sub",
                pattern="a(b)?c(?(1)(?(1)d|e)|f)",
                haystack="zzabcdzz",
                replacement="x",
            )
        )


def test_quantified_conditional_callable_correctness_case_signature_keeps_tuple_shapes_and_category_bits() -> None:
    cases = published_cases_by_id()

    assert {
        case_id: support._conditional_group_exists_quantified_callable_correctness_case_signature(
            cases[case_id]
        )
        for case_id in (
            "module-sub-callable-conditional-group-exists-quantified-present-str",
            "module-subn-callable-conditional-group-exists-quantified-absent-str",
            "pattern-sub-callable-conditional-group-exists-quantified-present-str",
            "pattern-subn-callable-conditional-group-exists-quantified-absent-str",
            "module-sub-callable-conditional-group-exists-quantified-none-count-present-str",
            "module-sub-callable-conditional-group-exists-quantified-near-miss-present-str",
            "module-sub-callable-conditional-group-exists-quantified-negative-count-present-str",
            "module-sub-callable-conditional-group-exists-quantified-present-bytes",
            "module-subn-callable-conditional-group-exists-quantified-absent-bytes",
            "pattern-sub-callable-conditional-group-exists-quantified-present-bytes",
            "pattern-subn-callable-conditional-group-exists-quantified-absent-bytes",
            "module-sub-callable-named-conditional-group-exists-quantified-present-str",
            "module-subn-callable-named-conditional-group-exists-quantified-absent-str",
            "pattern-sub-callable-named-conditional-group-exists-quantified-present-str",
            "pattern-subn-callable-named-conditional-group-exists-quantified-absent-str",
            "module-sub-callable-named-conditional-group-exists-quantified-present-bytes",
            "module-subn-callable-named-conditional-group-exists-quantified-absent-bytes",
            "pattern-sub-callable-named-conditional-group-exists-quantified-present-bytes",
            "pattern-subn-callable-named-conditional-group-exists-quantified-absent-bytes",
        )
    } == {
        "module-sub-callable-conditional-group-exists-quantified-present-str": (
            "module.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-conditional-group-exists-quantified-absent-str": (
            "module.subn",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-conditional-group-exists-quantified-present-str": (
            "pattern.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-conditional-group-exists-quantified-absent-str": (
            "pattern.subn",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-conditional-group-exists-quantified-none-count-present-str": (
            "module.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz",),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-conditional-group-exists-quantified-near-miss-present-str": (
            "module.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcdezz",),
            False,
            True,
            0,
            "str",
        ),
        "module-sub-callable-conditional-group-exists-quantified-negative-count-present-str": (
            "module.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz", -1),
            False,
            False,
            0,
            "str",
        ),
        "module-sub-callable-conditional-group-exists-quantified-present-bytes": (
            "module.sub",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-conditional-group-exists-quantified-absent-bytes": (
            "module.subn",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-conditional-group-exists-quantified-present-bytes": (
            "pattern.sub",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-conditional-group-exists-quantified-absent-bytes": (
            "pattern.subn",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "module-sub-callable-named-conditional-group-exists-quantified-present-str": (
            "module.sub",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-named-conditional-group-exists-quantified-absent-str": (
            "module.subn",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-named-conditional-group-exists-quantified-present-str": (
            "pattern.sub",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-named-conditional-group-exists-quantified-absent-str": (
            "pattern.subn",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-named-conditional-group-exists-quantified-present-bytes": (
            "module.sub",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-named-conditional-group-exists-quantified-absent-bytes": (
            "module.subn",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-named-conditional-group-exists-quantified-present-bytes": (
            "pattern.sub",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-named-conditional-group-exists-quantified-absent-bytes": (
            "pattern.subn",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
    }


def test_quantified_conditional_callable_workload_signature_keeps_count_and_category_bits() -> None:
    workloads = live_manifest_workloads(
        "conditional_group_exists_boundary.py",
        (
            "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm-str",
            "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged-str",
            "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-str",
            "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-str",
            "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
        ),
    )

    assert {
        workload.workload_id: support._conditional_group_exists_quantified_callable_workload_signature(
            workload
        )
        for workload in workloads
    } == {
        "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-str": (
            "module.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-str": (
            "module.subn",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-str": (
            "pattern.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-str": (
            "pattern.subn",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm-str": (
            "module.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz",),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged-str": (
            "pattern.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcddzz",),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-str": (
            "module.sub",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzabcdezz", -1),
            False,
            True,
            0,
            "str",
        ),
        "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-str": (
            "pattern.subn",
            "a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, "", "x"),
            ("zzacedzz", -1),
            False,
            True,
            0,
            "str",
        ),
        "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-bytes": (
            "module.sub",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes": (
            "module.subn",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-bytes": (
            "pattern.sub",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes": (
            "pattern.subn",
            b"a(b)?c(?(1)d|e){2}",
            ("callable_match_group", 1, b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-str": (
            "module.sub",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-str": (
            "module.subn",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-str": (
            "pattern.sub",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzabcddzz",),
            False,
            False,
            0,
            "str",
        ),
        "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-str": (
            "pattern.subn",
            "a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", "", "x"),
            ("zzaceezz", 1),
            True,
            False,
            0,
            "str",
        ),
        "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-bytes": (
            "module.sub",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes": (
            "module.subn",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
        "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-bytes": (
            "pattern.sub",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzabcddzz",),
            False,
            False,
            0,
            "bytes",
        ),
        "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes": (
            "pattern.subn",
            b"a(?P<word>b)?c(?(word)d|e){2}",
            ("callable_match_group", "word", b"", b"x"),
            (b"zzaceezz", 1),
            True,
            False,
            0,
            "bytes",
        ),
    }


def test_quantified_conditional_callable_workload_signature_rejects_non_owned_rows_and_non_callable_replacements() -> None:
    with pytest.raises(
        AssertionError,
        match="unexpected conditional quantified callable workload",
    ):
        support._conditional_group_exists_quantified_callable_workload_signature(
            synthetic_workload(
                manifest_id="conditional-group-exists-boundary",
                workload_id="not-an-owned-quantified-callable-row",
                operation="module.sub",
                pattern="a(b)?c(?(1)d|e){2}",
                haystack="zzabcddzz",
                replacement={
                    "type": "callable_match_group",
                    "group": 1,
                    "prefix": "<",
                    "suffix": ">",
                },
            )
        )

    with pytest.raises(
        AssertionError,
        match="expected callable_match_group replacement for quantified conditional workload",
    ):
        support._conditional_group_exists_quantified_callable_workload_signature(
            synthetic_workload(
                manifest_id="conditional-group-exists-boundary",
                workload_id="module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-str",
                operation="module.sub",
                pattern="a(b)?c(?(1)d|e){2}",
                haystack="zzabcddzz",
                replacement="x",
            )
        )


def test_compiled_pattern_wrong_text_model_workloads_keep_scope_and_split_sub_signatures() -> None:
    split_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-wrong-text-model",
        operation="module.split",
        haystack="abcabc",
        maxsplit=2,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    subn_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-subn-wrong-text-model",
        operation="module.subn",
        haystack="abcabc",
        replacement="x",
        count=1,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    direct_pattern_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="pattern-sub-wrong-text-model",
        operation="pattern.sub",
        haystack="abcabc",
        replacement="x",
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )

    assert support._is_collection_replacement_wrong_text_model_workload(split_workload)
    assert support._collection_replacement_wrong_text_model_workload_signature(
        split_workload
    ) == (
        "module.split",
        "abc",
        (b"abcabc", 2),
        True,
        0,
        "str",
    )

    assert support._is_collection_replacement_wrong_text_model_workload(subn_workload)
    assert support._collection_replacement_wrong_text_model_workload_signature(
        subn_workload
    ) == (
        "module.subn",
        "abc",
        ("x", b"abcabc", 1),
        True,
        0,
        "str",
    )

    assert not support._is_collection_replacement_wrong_text_model_workload(
        direct_pattern_workload
    )


def test_wrong_text_model_correctness_case_signatures_keep_haystack_positions_for_compiled_pattern_and_pattern_routes() -> None:
    compiled_split_case = _collection_replacement_case(
        helper="split",
        operation="module_call",
        args=(b"abcabc", 2),
        use_compiled_pattern=True,
    )
    compiled_sub_case = _collection_replacement_case(
        helper="sub",
        operation="module_call",
        args=("x", b"abcabc", 1),
        use_compiled_pattern=True,
    )
    pattern_split_case = _collection_replacement_case(
        helper="split",
        operation="pattern_call",
        args=(b"abcabc", 2),
    )
    pattern_subn_case = _collection_replacement_case(
        helper="subn",
        operation="pattern_call",
        args=("x", b"abcabc", 1),
    )

    assert support._collection_replacement_wrong_text_model_correctness_case_signature(
        compiled_split_case
    ) == (
        "module.split",
        "abc",
        (b"abcabc", 2),
        True,
        0,
        "str",
    )
    assert support._collection_replacement_wrong_text_model_correctness_case_signature(
        compiled_sub_case
    ) == (
        "module.sub",
        "abc",
        ("x", b"abcabc", 1),
        True,
        0,
        "str",
    )
    assert (
        support._collection_replacement_wrong_text_model_correctness_case_signature(
            _collection_replacement_case(
                helper="sub",
                operation="module_call",
                args=(b"abcabc", "x", 1),
                use_compiled_pattern=True,
            )
        )
        is None
    )

    assert (
        support._collection_replacement_pattern_wrong_text_model_correctness_case_signature(
            pattern_split_case
        )
        == (
            "pattern.split",
            "abc",
            (b"abcabc", 2),
            (),
            0,
            "str",
        )
    )
    assert (
        support._collection_replacement_pattern_wrong_text_model_correctness_case_signature(
            pattern_subn_case
        )
        == (
            "pattern.subn",
            "abc",
            ("x", b"abcabc", 1),
            (),
            0,
            "str",
        )
    )


def test_pattern_wrong_text_model_workloads_keep_scope_and_signature_shapes() -> None:
    split_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="pattern-split-wrong-text-model",
        operation="pattern.split",
        haystack="abcabc",
        maxsplit=2,
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    sub_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="pattern-sub-wrong-text-model",
        operation="pattern.sub",
        haystack="abcabc",
        replacement="x",
        count=1,
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    compiled_pattern_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-sub-wrong-text-model",
        operation="module.sub",
        haystack="abcabc",
        replacement="x",
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )

    assert support._is_collection_replacement_pattern_wrong_text_model_workload(
        split_workload
    )
    assert support._collection_replacement_pattern_wrong_text_model_workload_signature(
        split_workload
    ) == (
        "pattern.split",
        "abc",
        (b"abcabc", 2),
        (),
        0,
        "str",
    )

    assert support._is_collection_replacement_pattern_wrong_text_model_workload(
        sub_workload
    )
    assert support._collection_replacement_pattern_wrong_text_model_workload_signature(
        sub_workload
    ) == (
        "pattern.sub",
        "abc",
        ("x", b"abcabc", 1),
        (),
        0,
        "str",
    )

    assert not support._is_collection_replacement_pattern_wrong_text_model_workload(
        compiled_pattern_workload
    )


def test_compiled_pattern_success_workloads_stay_in_scope_and_keep_expected_signature() -> None:
    split_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-literal-compiled-pattern",
        operation="module.split",
        haystack="zabcabc",
        maxsplit=2,
        use_compiled_pattern=True,
    )
    subn_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-subn-literal-compiled-pattern-bytes",
        operation="module.subn",
        haystack="abcabc",
        replacement="x",
        count=1,
        text_model="bytes",
        use_compiled_pattern=True,
    )

    assert support._is_collection_replacement_compiled_pattern_success_workload(
        split_workload
    )
    assert support._collection_replacement_compiled_pattern_success_workload_signature(
        split_workload
    ) == (
        "module.split",
        "abc",
        ("zabcabc", 2),
        True,
        0,
        "str",
    )

    assert support._is_collection_replacement_compiled_pattern_success_workload(
        subn_workload
    )
    assert support._collection_replacement_compiled_pattern_success_workload_signature(
        subn_workload
    ) == (
        "module.subn",
        b"abc",
        (b"x", b"abcabc", 1),
        True,
        0,
        "bytes",
    )


def test_compiled_pattern_success_workload_filter_rejects_non_matching_rows() -> None:
    keyword_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-compiled-pattern-keyword",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": 1},
        use_compiled_pattern=True,
    )
    wrong_pattern_workload = synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-findall-bounded-wildcard-compiled-pattern",
        operation="module.findall",
        pattern="a.c",
        haystack="abcabc",
        use_compiled_pattern=True,
    )

    assert not support._is_collection_replacement_compiled_pattern_success_workload(
        keyword_workload
    )
    assert not support._is_collection_replacement_compiled_pattern_success_workload(
        wrong_pattern_workload
    )


def test_compiled_pattern_success_correctness_case_signature_requires_collection_call_shape() -> None:
    matching_case = _collection_replacement_case(
        helper="finditer",
        operation="module_call",
        args=("zabcabc",),
        use_compiled_pattern=True,
    )
    wrong_haystack_case = _collection_replacement_case(
        helper="sub",
        operation="module_call",
        args=("x", b"abcabc", 1),
        use_compiled_pattern=True,
    )
    unsupported_helper_case = _collection_replacement_case(
        helper="search",
        operation="module_call",
        args=("zabcabc",),
        use_compiled_pattern=True,
    )

    assert support._collection_replacement_compiled_pattern_success_correctness_case_signature(
        matching_case
    ) == (
        "module.finditer",
        "abc",
        ("zabcabc",),
        True,
        0,
        "str",
    )
    assert (
        support._collection_replacement_compiled_pattern_success_correctness_case_signature(
            wrong_haystack_case
        )
        is None
    )
    assert (
        support._collection_replacement_compiled_pattern_success_correctness_case_signature(
            unsupported_helper_case
        )
        is None
    )


def test_collection_replacement_pattern_wrong_text_model_source_workloads_stay_exact_and_in_order() -> None:
    workloads = support._collection_replacement_wrong_text_model_source_workloads()

    assert tuple(workload.workload_id for workload in workloads) == (
        support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._collection_replacement_wrong_text_model_source_workloads()
    ),
)
def test_collection_replacement_pattern_wrong_text_model_helpers_preserve_callback_and_runtime_contract(
    workload: Workload,
) -> None:
    assert compiled_pattern_contract_expected_build_calls(
        workload,
        label="direct Pattern collection/replacement wrong-text-model",
    ) == (
        [("compile", workload.pattern_payload(), workload.flags)]
        if workload.cache_mode == "warm"
        else [("compile", workload.pattern_payload(), workload.flags), ("purge",)]
    )
    assert support._collection_replacement_wrong_text_model_expected_callback_call(
        workload
    ) == (
        ("pattern.split", workload.haystack_payload(), (workload.maxsplit_argument(),), {})
        if workload.operation == "pattern.split"
        else (
            workload.operation,
            workload.replacement_payload(),
            workload.haystack_payload(),
            (workload.count_argument(),),
            {},
        )
    )
    assert support._collection_replacement_wrong_text_model_expected_callback_result(
        workload
    ) == (
        ("pattern-result", 0)
        if workload.operation == "pattern.subn"
        else "pattern-result"
    )

    with pytest.raises(TypeError) as observed_error:
        support._run_cpython_collection_replacement_wrong_text_model_workload(workload)

    assert str(observed_error.value) == str(
        workload.expected_exception["message_substring"]
    )


def test_standard_benchmark_manifest_preserves_collection_replacement_pattern_wrong_text_model_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = support._collection_replacement_wrong_text_model_source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_collection_replacement_wrong_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = tuple(
        benchmarks.load_manifest(manifest_path).workloads
    )

    assert tuple(workload.workload_id for workload in source_workloads) == (
        support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract"
        for workload_id in support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [False] * len(
        source_workloads
    )
    assert [workload.timing_scope for workload in workloads] == [
        "pattern-helper-call"
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
            expect_replacement_payload=source_workload.replacement is not None,
        )

        with pytest.raises(TypeError) as expected_error:
            support._run_cpython_collection_replacement_wrong_text_model_workload(
                workload
            )
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._collection_replacement_wrong_text_model_source_workloads()
    ),
)
def test_run_internal_workload_probe_measures_collection_replacement_pattern_wrong_text_model_contract_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
        expect_replacement_payload=source_workload.replacement is not None,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._collection_replacement_wrong_text_model_source_workloads()
    ),
)
def test_collection_replacement_pattern_wrong_text_model_callbacks_preserve_precompile_contract(
    source_workload: Workload,
) -> None:
    expected_build_calls = compiled_pattern_contract_expected_build_calls(
        source_workload,
        label="direct Pattern collection/replacement wrong-text-model",
    )
    expected_callback_call = (
        support._collection_replacement_wrong_text_model_expected_callback_call(
            source_workload
        )
    )
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == (
        support._collection_replacement_wrong_text_model_expected_callback_result(
            source_workload
        )
    )
    assert module.calls[-1] == expected_callback_call


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._collection_replacement_wrong_text_model_source_workloads()
    ),
)
def test_pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time(
    monkeypatch: pytest.MonkeyPatch,
    workload: Workload,
) -> None:
    observed_workload_ids: list[str] = []
    original_haystack_payload = benchmarks.Workload.haystack_payload

    def record_haystack_payload(self: Workload) -> object:
        observed_workload_ids.append(self.workload_id)
        return original_haystack_payload(self)

    monkeypatch.setattr(
        benchmarks.Workload,
        "haystack_payload",
        record_haystack_payload,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_workload_ids == []

        with pytest.raises(
            TypeError,
            match=re.escape(str(workload.expected_exception["message_substring"])),
        ):
            callback()

        assert observed_workload_ids == [workload.workload_id]
    finally:
        re.purge()
