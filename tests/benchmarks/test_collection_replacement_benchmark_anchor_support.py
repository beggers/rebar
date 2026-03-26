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
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import benchmark_test_support
from tests.benchmarks import collection_replacement_benchmark_anchor_support as support
from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support
from tests.conftest import records_by_string_id
from tests.python.fixture_parity_support import IndexLike


def _default_collection_replacement_wrong_text_model_manifest_timed_samples() -> int:
    default = (
        support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC.manifest_timed_samples
    )
    assert isinstance(default, int)
    return default


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


def _workload_ids_for_declared_slice(
    workloads: tuple[Workload, ...],
    *,
    text_model: str | None = None,
    include_categories: tuple[str, ...] = (),
    exclude_categories: tuple[str, ...] = (),
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in workloads
        if (text_model is None or workload.text_model == text_model)
        and all(category in workload.categories for category in include_categories)
        and all(category not in workload.categories for category in exclude_categories)
    )


def _collection_routed_owner_assignment_names() -> tuple[str, ...]:
    _, assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )
    return tuple(
        sorted(
            name
            for name in assignment_names
            if name.startswith("CONDITIONAL_GROUP_EXISTS_")
            and name.endswith("_WORKLOAD_IDS")
        )
    )


def test_collection_replacement_pattern_wrong_text_model_support_surface_is_owner_module_owned_without_local_duplicates(
) -> None:
    import sys

    benchmark_test_support.assert_owner_surface_module_owned_without_local_duplicates(
        sys.modules[__name__],
        support,
        definition_names=(
            "_collection_replacement_wrong_text_model_source_workloads",
            "_collection_replacement_wrong_text_model_expected_callback_call",
            "_collection_replacement_wrong_text_model_expected_callback_result",
            "_run_cpython_collection_replacement_wrong_text_model_workload",
            "_pattern_collection_replacement_wrong_text_model_haystack_index",
            "_collection_replacement_pattern_wrong_text_model_correctness_case_signature",
            "_collection_replacement_pattern_wrong_text_model_workload_args",
            "_collection_replacement_pattern_wrong_text_model_workload_signature",
            "_is_collection_replacement_pattern_wrong_text_model_workload",
        ),
        assignment_names=(
            "_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
            "_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC",
        ),
    )


def test_collection_replacement_pattern_wrong_text_model_contract_spec_uses_owner_metadata(
) -> None:
    spec = support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC

    assert spec == SimpleNamespace(
        manifest_id="collection-replacement-boundary",
        excluded_fields=(
            support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS
        ),
        manifest_timed_samples=(
            _default_collection_replacement_wrong_text_model_manifest_timed_samples()
        ),
        timing_scope="pattern-helper-call",
        notes=(),
    )
    assert (
        spec.manifest_timed_samples
        == _default_collection_replacement_wrong_text_model_manifest_timed_samples()
    )


def test_positional_indexlike_workloads_stay_in_scope_and_keep_expected_signature() -> None:
    split_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-indexlike",
        operation="module.split",
        haystack="zabcabc",
        maxsplit={"type": "indexlike", "value": 2},
    )
    sub_workload = benchmark_test_support.synthetic_workload(
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
    keyword_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-keyword",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": {"type": "indexlike", "value": 1}},
    )
    plain_int_workload = benchmark_test_support.synthetic_workload(
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
    expected_keyword_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-keyword-indexlike",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": {"type": "indexlike", "value": 1}},
    )
    duplicate_keyword_workload = benchmark_test_support.synthetic_workload(
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
    unexpected_keyword_workload = benchmark_test_support.synthetic_workload(
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

    assert benchmark_test_support._is_collection_replacement_keyword_workload(
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

    assert benchmark_test_support._is_collection_replacement_keyword_workload(
        duplicate_keyword_workload
    )
    assert (
        benchmark_test_support._collection_replacement_positional_keyword_field(
            duplicate_keyword_workload
        )
        == "count"
    )
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

    assert benchmark_test_support._is_collection_replacement_keyword_workload(
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
    multiple_keyword_workload = benchmark_test_support.synthetic_workload(
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
    search_keyword_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-search-keyword",
        operation="module.search",
        haystack="abcabc",
        kwargs={"flags": 1},
    )

    assert not benchmark_test_support._is_collection_replacement_keyword_workload(
        multiple_keyword_workload
    )
    assert not benchmark_test_support._is_collection_replacement_keyword_workload(
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
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=lambda workload: (
                benchmark_test_support._is_collection_replacement_keyword_workload(
                    workload
                )
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
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=lambda workload: (
                benchmark_test_support._is_collection_replacement_keyword_workload(
                    workload
                )
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
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
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
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


@pytest.mark.parametrize(
    ("label", "workload_case_pairs"),
    (
        (
            "pattern-findall",
            support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "findall"
            ].workload_case_pairs,
        ),
        (
            "pattern-finditer",
            support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "finditer"
            ].workload_case_pairs,
        ),
        (
            "pattern-split",
            support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
                "split"
            ].workload_case_pairs,
        ),
        (
            "pattern-literal-replacement",
            support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS,
        ),
        (
            "module-literal-replacement",
            support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS,
        ),
    ),
    ids=lambda item: item if isinstance(item, str) else None,
)
def test_collection_replacement_routes_preserve_declared_workload_case_pair_order_and_anchor_expectations(
    label: str,
    workload_case_pairs: tuple[tuple[str, str], ...],
) -> None:
    del label

    anchor_expectations = benchmark_test_support._workload_case_pair_anchor_expectations(
        benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        workload_case_pairs,
    )

    assert all(
        isinstance(workload_id, str) and isinstance(case_id, str)
        for workload_id, case_id in workload_case_pairs
    )
    assert tuple(manifest_path for manifest_path, _ in anchor_expectations) == (
        benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH.name,
    ) * len(workload_case_pairs)
    assert tuple(workload_id for _, workload_id in anchor_expectations) == tuple(
        workload_id for workload_id, _ in workload_case_pairs
    )
    assert tuple(anchor_expectations.values()) == tuple(
        (case_id,) for _, case_id in workload_case_pairs
    )


def test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    route = support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES["findall"]
    expected_measured_workload_ids = tuple(
        workload_id for workload_id, _ in route.workload_case_pairs
    )
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=route.includes_workload,
        )
    )

    assert len(expected_measured_workload_ids) == 3
    assert selected_measured_workload_ids == expected_measured_workload_ids
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    route = support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES["finditer"]
    expected_measured_workload_ids = tuple(
        workload_id for workload_id, _ in route.workload_case_pairs
    )
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=route.includes_workload,
        )
    )

    assert len(expected_measured_workload_ids) == 3
    assert selected_measured_workload_ids == expected_measured_workload_ids
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_pattern_split_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    route = support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES["split"]
    expected_measured_workload_ids = tuple(
        workload_id for workload_id, _ in route.workload_case_pairs
    )
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=route.includes_workload,
        )
    )

    assert len(expected_measured_workload_ids) == 3
    assert selected_measured_workload_ids == expected_measured_workload_ids
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    selected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR,
        )
    )

    assert selected_measured_workload_ids == tuple(
        workload_id
        for workload_id, _ in (
            support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
        )
    )
    assert len(selected_measured_workload_ids) == 20
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=selected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR,
        )
    )

    assert expected_measured_workload_ids == tuple(
        workload_id
        for workload_id, _ in (
            support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
        )
    )
    assert len(expected_measured_workload_ids) == 18
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
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
        for workload in benchmark_test_support.manifest_workloads(
            "collection_replacement_boundary.py"
        )
        if include_workload(workload)
    }
    unbenchmarked_case_ids = tuple(
        case.case_id
        for case in benchmark_test_support.published_cases_by_id().values()
        if (
            signature := (
                support._collection_replacement_literal_replacement_correctness_case_signature(
                    case,
                    case_ids=(
                        support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_CASE_IDS
                    ),
                    expected_operation=(
                        support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_EXPECTED_OPERATION
                    ),
                    operation_prefix=(
                        support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATION_PREFIX
                    ),
                    args_offset=(
                        support._COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ARGS_OFFSET
                    ),
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
        for workload in benchmark_test_support.manifest_workloads(
            "collection_replacement_boundary.py"
        )
        if include_workload(workload)
    }
    unbenchmarked_case_ids = tuple(
        case.case_id
        for case in benchmark_test_support.published_cases_by_id().values()
        if (
            signature := (
                support._collection_replacement_literal_replacement_correctness_case_signature(
                    case,
                    case_ids=(
                        support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_CASE_IDS
                    ),
                    expected_operation=(
                        support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_EXPECTED_OPERATION
                    ),
                    operation_prefix=(
                        support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATION_PREFIX
                    ),
                    args_offset=(
                        support._COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_ARGS_OFFSET
                    ),
                )
            )
        )
        is not None
        and signature not in workload_signatures
    )

    assert unbenchmarked_case_ids == ()


def test_collection_replacement_manifest_keeps_grouped_callable_rows_measured() -> None:
    manifest_path = "collection_replacement_boundary.py"
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(manifest_path)
    )
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            manifest_path,
            include_workload=support._is_collection_replacement_grouped_callable_workload,
        )
    )

    assert expected_measured_workload_ids == tuple(
        workload_id
        for workload_id, _ in support._COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
    )
    assert len(expected_measured_workload_ids) == 4
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
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
        for definition in benchmark_test_support.STANDARD_BENCHMARK_DEFINITIONS
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
    owner_definition_names = tuple(
        definition.name for definition in owner_definitions
    )
    standard_definitions_by_name = {
        definition.name: definition
        for definition in benchmark_test_support.STANDARD_BENCHMARK_DEFINITIONS
        if definition.name in owner_definition_names
    }

    assert tuple(standard_definitions_by_name) == owner_definition_names
    assert tuple(
        standard_definitions_by_name[definition_name]
        for definition_name in owner_definition_names
    ) == owner_definitions
    assert all(
        standard_definitions_by_name[definition.name] is definition
        for definition in owner_definitions
    )


def test_grouped_callable_correctness_case_signature_keeps_live_pair_shapes() -> None:
    cases = benchmark_test_support.published_cases_by_id()

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
    case = benchmark_test_support.published_cases_by_id()[
        "module-sub-callable-grouped-str"
    ]
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
    workloads = benchmark_test_support.live_manifest_workloads(
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
    workload = benchmark_test_support.live_manifest_workloads(
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
            benchmark_test_support.synthetic_workload(
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
            benchmark_test_support.synthetic_workload(
                manifest_id="collection-replacement-boundary",
                workload_id="module-sub-callable-grouped-warm-str",
                operation="module.sub",
                pattern="(abc)",
                haystack="abcabc",
                replacement="x",
            )
        )


def test_moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import(
) -> None:
    source_tree_support._assert_source_tree_combined_routes_owner_names_through_module_alias(
        alias_name="collection_replacement_support",
        owner_module=support,
        owner_names=_collection_routed_owner_assignment_names(),
    )


def test_conditional_collection_replacement_slice_expectations_stay_in_sync_with_owner_workload_ids(
) -> None:
    callable_expectations = {
        expectation.slice_id: expectation.expected_workload_ids
        for expectation in support._conditional_group_exists_callable_replacement_expectations()
    }
    minimal_callable_workload_ids = (
        callable_expectations["minimal-callable-replacement-rows"]
        + callable_expectations["minimal-callable-replacement-exception-rows"]
    )
    minimal_callable_workloads = benchmark_test_support.live_manifest_workloads(
        "conditional_group_exists_boundary.py",
        minimal_callable_workload_ids,
    )
    callable_none_count_candidate_workloads = benchmark_test_support.live_manifest_workloads(
        "conditional_group_exists_boundary.py",
        callable_expectations["minimal-callable-replacement-none-count-exception-rows"]
        + callable_expectations["alternation-heavy-callable-replacement-rows"],
    )
    alternation_workloads = benchmark_test_support.live_manifest_workloads(
        "conditional_group_exists_boundary.py",
        callable_expectations["alternation-heavy-callable-replacement-rows"],
    )
    template_workload_ids = (
        support._conditional_group_exists_template_replacement_expectation().expected_workload_ids
    )
    template_workloads = benchmark_test_support.live_manifest_workloads(
        "conditional_group_exists_boundary.py",
        template_workload_ids,
    )
    callable_none_count_str_ids = _workload_ids_for_declared_slice(
        callable_none_count_candidate_workloads,
        text_model="str",
        include_categories=("none-count",),
    )
    callable_none_count_bytes_ids = _workload_ids_for_declared_slice(
        callable_none_count_candidate_workloads,
        text_model="bytes",
        include_categories=("none-count",),
    )

    observed_workload_ids_by_label = {
        "callable-bytes": _workload_ids_for_declared_slice(
            minimal_callable_workloads,
            text_model="bytes",
            exclude_categories=("negative-count",),
        ),
        "callable-negative-count-str": _workload_ids_for_declared_slice(
            minimal_callable_workloads,
            text_model="str",
            include_categories=("negative-count",),
        ),
        "callable-negative-count-bytes": _workload_ids_for_declared_slice(
            minimal_callable_workloads,
            text_model="bytes",
            include_categories=("negative-count",),
        ),
        "callable-none-count-all": (
            callable_none_count_str_ids + callable_none_count_bytes_ids
        ),
        "callable-none-count-str": callable_none_count_str_ids,
        "callable-none-count-bytes": callable_none_count_bytes_ids,
        "callable-alternation-all": _workload_ids_for_declared_slice(
            alternation_workloads,
            include_categories=("alternation-heavy",),
        ),
        "callable-alternation-str": _workload_ids_for_declared_slice(
            alternation_workloads,
            text_model="str",
            include_categories=("alternation-heavy",),
        ),
        "callable-alternation-bytes": _workload_ids_for_declared_slice(
            alternation_workloads,
            text_model="bytes",
            include_categories=("alternation-heavy",),
        ),
        "template-round-trip": tuple(
            workload.workload_id
            for workload in template_workloads
            if workload.text_model == "bytes" or "negative-count" in workload.categories
        ),
        "template-bytes": _workload_ids_for_declared_slice(
            template_workloads,
            text_model="bytes",
        ),
        "template-negative-count-str": _workload_ids_for_declared_slice(
            template_workloads,
            text_model="str",
            include_categories=("negative-count",),
        ),
        "nested-callable-str": (
            support._conditional_group_exists_nested_callable_replacement_expectation().expected_workload_ids
        ),
        "nested-callable-bytes": (
            support._conditional_group_exists_nested_callable_bytes_replacement_expectation().expected_workload_ids
        ),
        "quantified-callable-str": (
            support._conditional_group_exists_quantified_callable_replacement_expectation().expected_workload_ids
        ),
        "quantified-callable-bytes": (
            support._conditional_group_exists_quantified_callable_bytes_replacement_expectation().expected_workload_ids
        ),
    }
    expected_workload_ids_by_label = {
        "callable-bytes": support.CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS,
        "callable-negative-count-str": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
        ),
        "callable-negative-count-bytes": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS
        ),
        "callable-none-count-all": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
        ),
        "callable-none-count-str": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
        ),
        "callable-none-count-bytes": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
        ),
        "callable-alternation-all": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS
        ),
        "callable-alternation-str": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS
        ),
        "callable-alternation-bytes": (
            support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS
        ),
        "template-round-trip": (
            support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS
        ),
        "template-bytes": support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS,
        "template-negative-count-str": (
            support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
        ),
        "nested-callable-str": (
            support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
        ),
        "nested-callable-bytes": (
            support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
        ),
        "quantified-callable-str": (
            support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        ),
        "quantified-callable-bytes": (
            support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
        ),
    }

    for label, expected_workload_ids in expected_workload_ids_by_label.items():
        assert observed_workload_ids_by_label[label] == expected_workload_ids, label


def test_quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids(
) -> None:
    combined_suite = source_tree_support._assert_source_tree_combined_routes_owner_names_through_module_alias(
        alias_name="collection_replacement_support",
        owner_module=support,
        owner_names=(
            "COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS",
        ),
    )
    expectations_by_slice_id = {
        expectation.slice_id: expectation
        for expectation in (
            combined_suite.collection_replacement_support.COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
        )
    }

    assert (
        expectations_by_slice_id[
            "quantified-callable-replacement-str-rows"
        ].expected_workload_ids
        == support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
    )
    assert (
        expectations_by_slice_id[
            "quantified-callable-replacement-bytes-rows"
        ].expected_workload_ids
        == support.CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
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
    cases = benchmark_test_support.published_cases_by_id()

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
    workloads = benchmark_test_support.live_manifest_workloads(
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
            benchmark_test_support.synthetic_workload(
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
            benchmark_test_support.synthetic_workload(
                manifest_id="conditional-group-exists-boundary",
                workload_id="module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
                operation="module.sub",
                pattern="a(b)?c(?(1)(?(1)d|e)|f)",
                haystack="zzabcdzz",
                replacement="x",
            )
        )


def test_quantified_conditional_callable_correctness_case_signature_keeps_tuple_shapes_and_category_bits() -> None:
    cases = benchmark_test_support.published_cases_by_id()

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
    workloads = benchmark_test_support.live_manifest_workloads(
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
            benchmark_test_support.synthetic_workload(
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
            benchmark_test_support.synthetic_workload(
                manifest_id="conditional-group-exists-boundary",
                workload_id="module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-str",
                operation="module.sub",
                pattern="a(b)?c(?(1)d|e){2}",
                haystack="zzabcddzz",
                replacement="x",
            )
        )


def test_compiled_pattern_wrong_text_model_workloads_keep_scope_and_split_sub_signatures() -> None:
    split_workload = benchmark_test_support.synthetic_workload(
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
    subn_workload = benchmark_test_support.synthetic_workload(
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
    direct_pattern_workload = benchmark_test_support.synthetic_workload(
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

    assert benchmark_test_support._is_collection_replacement_wrong_text_model_workload(
        split_workload
    )
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

    assert benchmark_test_support._is_collection_replacement_wrong_text_model_workload(
        subn_workload
    )
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

    assert not benchmark_test_support._is_collection_replacement_wrong_text_model_workload(
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
    split_workload = benchmark_test_support.synthetic_workload(
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
    sub_workload = benchmark_test_support.synthetic_workload(
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
    compiled_pattern_workload = benchmark_test_support.synthetic_workload(
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
    owner_support = support.benchmark_test_support
    split_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-literal-compiled-pattern",
        operation="module.split",
        haystack="zabcabc",
        maxsplit=2,
        use_compiled_pattern=True,
    )
    subn_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-subn-literal-compiled-pattern-bytes",
        operation="module.subn",
        haystack="abcabc",
        replacement="x",
        count=1,
        text_model="bytes",
        use_compiled_pattern=True,
    )

    assert owner_support._is_collection_replacement_compiled_pattern_success_workload(
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

    assert owner_support._is_collection_replacement_compiled_pattern_success_workload(
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


def test_compiled_pattern_success_selector_routes_through_shared_support_without_local_definition(
) -> None:
    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            support
        )
    )
    owner_support = support.benchmark_test_support

    assert owner_support is benchmark_test_support
    assert (
        owner_support._is_collection_replacement_compiled_pattern_success_workload
        is benchmark_test_support._is_collection_replacement_compiled_pattern_success_workload
    )
    assert not hasattr(support, "_is_collection_replacement_compiled_pattern_success_workload")
    assert (
        "_is_collection_replacement_compiled_pattern_success_workload"
        not in local_definition_names
    )
    assert (
        "_is_collection_replacement_compiled_pattern_success_workload"
        not in local_assignment_names
    )


def test_compiled_pattern_success_workload_filter_rejects_non_matching_rows() -> None:
    owner_support = support.benchmark_test_support
    keyword_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-split-compiled-pattern-keyword",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": 1},
        use_compiled_pattern=True,
    )
    wrong_pattern_workload = benchmark_test_support.synthetic_workload(
        manifest_id="collection-replacement-boundary",
        workload_id="module-findall-bounded-wildcard-compiled-pattern",
        operation="module.findall",
        pattern="a.c",
        haystack="abcabc",
        use_compiled_pattern=True,
    )

    assert not owner_support._is_collection_replacement_compiled_pattern_success_workload(
        keyword_workload
    )
    assert not owner_support._is_collection_replacement_compiled_pattern_success_workload(
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
    assert benchmark_test_support.compiled_pattern_contract_expected_build_calls(
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
    manifest = source_tree_support._source_tree_contract_manifest(
        source_workloads,
        spec=support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_collection_replacement_wrong_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = tuple(
        benchmarks.load_manifest(manifest_path).workloads
    )
    assert manifest["defaults"] == {
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": (
            _default_collection_replacement_wrong_text_model_manifest_timed_samples()
        ),
    }

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

        benchmark_test_support.assert_pattern_helper_wrong_text_model_payload_round_trip(
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
            benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)

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
    workload = source_tree_support._source_tree_contract_workload(
        source_workload,
        spec=support._COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    benchmark_test_support.assert_pattern_helper_wrong_text_model_payload_round_trip(
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
    expected_build_calls = benchmark_test_support.compiled_pattern_contract_expected_build_calls(
        source_workload,
        label="direct Pattern collection/replacement wrong-text-model",
    )
    expected_callback_call = (
        support._collection_replacement_wrong_text_model_expected_callback_call(
            source_workload
        )
    )
    module = benchmark_test_support.RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        source_tree_support._source_tree_contract_workload(
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


def test_collection_replacement_keyword_contract_surface_routes_owner_names_through_support_alias_without_local_duplicates(
) -> None:
    import sys

    local_definition_names, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            sys.modules[__name__]
        )
    )
    owner_support = support.benchmark_test_support

    assert owner_support is benchmark_test_support
    for name in (
        "COLLECTION_REPLACEMENT_MANIFEST_PATH",
        "MODULE_BOUNDARY_MANIFEST_PATH",
    ):
        assert hasattr(owner_support, name)
        assert not hasattr(support, name)

    for name in (
        "_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES",
        "_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_assert_keyword_error_workload_probe_measured",
        "_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_is_collection_replacement_module_helper_keyword_error_workload",
        "_is_collection_replacement_pattern_helper_keyword_error_workload",
        "_pattern_helper_collection_replacement_keyword_error_workload",
    ):
        assert hasattr(support, name)
    assert {
        "_assert_keyword_error_workload_probe_measured",
        "_pattern_helper_collection_replacement_keyword_error_workload",
        "_is_collection_replacement_pattern_helper_keyword_error_workload",
        "_is_collection_replacement_module_helper_keyword_error_workload",
    }.isdisjoint(local_definition_names)
    assert {
        "COLLECTION_REPLACEMENT_MANIFEST_PATH",
        "MODULE_BOUNDARY_MANIFEST_PATH",
        "_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES",
        "_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS",
        "_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS",
        "_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS",
        "_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
    }.isdisjoint(local_assignment_names)


def test_pattern_helper_collection_replacement_keyword_error_workload_builder_shape() -> None:
    workload = support._pattern_helper_collection_replacement_keyword_error_workload(
        operation="pattern.subn",
        haystack="abc",
        kwargs_payload={"count_alias": 1},
        replacement="x",
        count=0,
        maxsplit=0,
        expected_exception={
            "type": "TypeError",
            "message_substring": "'count_alias' is an invalid keyword argument for subn()",
        },
        text_model="bytes",
    )
    payload = workload_to_payload(workload)

    assert payload["manifest_id"] == (
        "python-benchmark-pattern-collection-replacement-keyword-contract"
    )
    assert payload["timing_scope"] == "pattern-helper-call"
    assert payload["expected_exception"] == {
        "type": "TypeError",
        "message_substring": "'count_alias' is an invalid keyword argument for subn()",
    }
    assert payload["kwargs"] == {"count_alias": 1}
    assert payload["text_model"] == "bytes"


def test_pattern_helper_keyword_error_selector_stays_in_scope() -> None:
    workload = next(
        workload
        for workload in support._PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        if workload.workload_id == "pattern-sub-unexpected-keyword-warm-str"
    )

    assert support._is_collection_replacement_pattern_helper_keyword_error_workload(
        workload
    )


def test_module_helper_collection_replacement_keyword_error_selector_stays_in_scope() -> None:
    workload = next(
        workload
        for workload in support._MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        if workload.workload_id == "module-sub-count-alias-keyword-purged-str"
    )

    assert support._is_collection_replacement_module_helper_keyword_error_workload(
        workload
    )


def test_keyword_error_workload_probe_helper_measures_real_source_workload() -> None:
    support._assert_keyword_error_workload_probe_measured(
        next(iter(support._PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS)),
        import_name="re",
        adapter_name="cpython.re",
    )


def test_standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "pattern-split-maxsplit-keyword-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "zabczabc",
                "kwargs": {"maxsplit": 1},
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [],
            },
            {
                "id": "pattern-sub-count-bool-keyword-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {"count": False},
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [],
            },
            {
                "id": "pattern-sub-unexpected-keyword-after-positional-count-contract-str",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "count": 1,
                "kwargs": {"missing": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "sub() takes at most 3 arguments (4 given)",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [],
            },
            {
                "id": "pattern-subn-count-keyword-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {"count": 1},
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [],
            },
            {
                "id": "pattern-subn-count-alias-keyword-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {"count_alias": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'count_alias' is an invalid keyword argument for subn()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [],
            },
        ],
    }
    """

    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_collection_replacement_keyword_contract.py",
        manifest_source,
    )
    workloads_by_id = records_by_string_id(
        load_manifest(manifest_path).workloads,
        id_attr="workload_id",
    )

    split_workload = workloads_by_id["pattern-split-maxsplit-keyword-contract-str"]
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.kwargs == {"maxsplit": 1}
    assert round_tripped_split.keyword_arguments() == {"maxsplit": 1}
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_split
    ) == ["z", "zabc"]

    sub_bool_workload = workloads_by_id["pattern-sub-count-bool-keyword-contract-bytes"]
    round_tripped_sub_bool = workload_from_payload(
        workload_to_payload(sub_bool_workload)
    )
    assert round_tripped_sub_bool.kwargs == {"count": False}
    assert round_tripped_sub_bool.keyword_arguments() == {"count": False}
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_sub_bool
    ) == b"xx"

    sub_missing_after_positional_count_workload = workloads_by_id[
        "pattern-sub-unexpected-keyword-after-positional-count-contract-str"
    ]
    round_tripped_sub_missing_after_positional_count = workload_from_payload(
        workload_to_payload(sub_missing_after_positional_count_workload)
    )
    assert round_tripped_sub_missing_after_positional_count.count == 1
    assert (
        round_tripped_sub_missing_after_positional_count.keyword_arguments()
        == {"missing": 1}
    )
    with pytest.raises(
        TypeError,
        match=re.escape("sub() takes at most 3 arguments (4 given)"),
    ):
        benchmark_test_support.run_benchmark_workload_with_cpython(
            round_tripped_sub_missing_after_positional_count
        )

    subn_workload = workloads_by_id["pattern-subn-count-keyword-contract-str"]
    round_tripped_subn = workload_from_payload(workload_to_payload(subn_workload))
    assert round_tripped_subn.kwargs == {"count": 1}
    assert round_tripped_subn.keyword_arguments() == {"count": 1}
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_subn
    ) == ("xabc", 1)

    subn_count_alias_workload = workloads_by_id[
        "pattern-subn-count-alias-keyword-contract-bytes"
    ]
    round_tripped_subn_count_alias = workload_from_payload(
        workload_to_payload(subn_count_alias_workload)
    )
    assert round_tripped_subn_count_alias.kwargs == {"count_alias": 1}
    assert round_tripped_subn_count_alias.keyword_arguments() == {"count_alias": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'count_alias' is an invalid keyword argument for subn()"),
    ):
        benchmark_test_support.run_benchmark_workload_with_cpython(
            round_tripped_subn_count_alias
        )


def test_standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-module-collection-replacement-keyword-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "module-split-maxsplit-keyword-contract-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabczabc",
                "text_model": "bytes",
                "kwargs": {"maxsplit": 1},
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [],
            },
            {
                "id": "module-sub-count-indexlike-keyword-warm-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "kwargs": {"count": {"type": "indexlike", "value": 2}},
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [],
            },
            {
                "id": "module-subn-duplicate-count-keyword-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "count": 1,
                "text_model": "bytes",
                "kwargs": {"count": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "multiple values for argument 'count'",
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [],
            },
            {
                "id": "module-split-unexpected-keyword-contract-str",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "abc",
                "kwargs": {"missing": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [],
            },
            {
                "id": "module-sub-count-alias-keyword-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {"count_alias": 1},
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'count_alias'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [],
            },
        ],
    }
    """

    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_module_collection_replacement_keyword_contract.py",
        manifest_source,
    )
    workloads_by_id = records_by_string_id(
        load_manifest(manifest_path).workloads,
        id_attr="workload_id",
    )

    split_workload = workloads_by_id["module-split-maxsplit-keyword-contract-bytes"]
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.kwargs == {"maxsplit": 1}
    assert round_tripped_split.keyword_arguments() == {"maxsplit": 1}
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_split
    ) == [b"z", b"zabc"]

    sub_indexlike_workload = workloads_by_id["module-sub-count-indexlike-keyword-warm-str"]
    round_tripped_sub_indexlike = workload_from_payload(
        workload_to_payload(sub_indexlike_workload)
    )
    assert round_tripped_sub_indexlike.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    assert round_tripped_sub_indexlike.keyword_arguments()["count"].__index__() == 2
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_sub_indexlike
    ) == "xxabc"

    subn_duplicate_workload = workloads_by_id[
        "module-subn-duplicate-count-keyword-contract-bytes"
    ]
    round_tripped_subn_duplicate = workload_from_payload(
        workload_to_payload(subn_duplicate_workload)
    )
    assert round_tripped_subn_duplicate.count == 1
    assert round_tripped_subn_duplicate.keyword_arguments() == {"count": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("subn() got multiple values for argument 'count'"),
    ):
        benchmark_test_support.run_benchmark_workload_with_cpython(
            round_tripped_subn_duplicate
        )

    split_missing_workload = workloads_by_id["module-split-unexpected-keyword-contract-str"]
    round_tripped_split_missing = workload_from_payload(
        workload_to_payload(split_missing_workload)
    )
    assert round_tripped_split_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("split() got an unexpected keyword argument 'missing'"),
    ):
        benchmark_test_support.run_benchmark_workload_with_cpython(
            round_tripped_split_missing
        )

    sub_count_alias_workload = workloads_by_id[
        "module-sub-count-alias-keyword-contract-str"
    ]
    round_tripped_sub_count_alias = workload_from_payload(
        workload_to_payload(sub_count_alias_workload)
    )
    assert round_tripped_sub_count_alias.keyword_arguments() == {"count_alias": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("sub() got an unexpected keyword argument 'count_alias'"),
    ):
        benchmark_test_support.run_benchmark_workload_with_cpython(
            round_tripped_sub_count_alias
        )


def test_standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-indexlike-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "module-split-indexlike-contract-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabcabcabc",
                "maxsplit": {"type": "indexlike", "value": 2},
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [],
            },
            {
                "id": "pattern-sub-indexlike-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {"type": "indexlike", "value": 2},
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [],
            },
            {
                "id": "pattern-subn-indexlike-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {"type": "indexlike", "value": 2},
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [],
            },
        ],
    }
    """

    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_indexlike_contract.py",
        manifest_source,
    )
    workloads_by_id = records_by_string_id(
        load_manifest(manifest_path).workloads,
        id_attr="workload_id",
    )

    split_workload = workloads_by_id["module-split-indexlike-contract-bytes"]
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.maxsplit_argument().__index__() == 2
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_split
    ) == [b"z", b"", b"abc"]

    pattern_sub_workload = workloads_by_id["pattern-sub-indexlike-contract-bytes"]
    round_tripped_pattern_sub = workload_from_payload(
        workload_to_payload(pattern_sub_workload)
    )
    assert round_tripped_pattern_sub.count_argument().__index__() == 2
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_pattern_sub
    ) == b"xxabc"

    pattern_subn_workload = workloads_by_id["pattern-subn-indexlike-contract-str"]
    round_tripped_pattern_subn = workload_from_payload(
        workload_to_payload(pattern_subn_workload)
    )
    assert round_tripped_pattern_subn.count_argument().__index__() == 2
    assert benchmark_test_support.run_benchmark_workload_with_cpython(
        round_tripped_pattern_subn
    ) == (
        "xxabc",
        2,
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "text_model",
        "expected_result",
        "expected_field_names",
    ),
    (
        pytest.param(
            "pattern.split",
            "zabcabc",
            {"maxsplit": {"type": "indexlike", "value": 1}},
            None,
            "str",
            ["z", "abc"],
            ["kwargs.maxsplit"],
            id="split-maxsplit-indexlike",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count": {"type": "indexlike", "value": 1}},
            "x",
            "bytes",
            b"xabc",
            ["kwargs.count"],
            id="sub-count-indexlike",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count": {"type": "indexlike", "value": 1}},
            "x",
            "str",
            ("xabc", 1),
            ["kwargs.count"],
            id="subn-count-indexlike",
        ),
        pytest.param(
            "pattern.split",
            "zabcabc",
            {"maxsplit": True},
            None,
            "str",
            ["z", "abc"],
            ["kwargs.maxsplit"],
            id="split-maxsplit-bool",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count": False},
            "x",
            "bytes",
            b"xx",
            ["kwargs.count"],
            id="sub-count-bool",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count": True},
            "x",
            "str",
            ("xabc", 1),
            ["kwargs.count"],
            id="subn-count-bool",
        ),
    ),
)
def test_pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    text_model: str,
    expected_result: object,
    expected_field_names: list[str],
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
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
    benchmark_test_support._assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=expected_result,
        expected_field_names=expected_field_names,
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_exception",
        "expected_field_names",
    ),
    (
        pytest.param(
            "pattern.split",
            "abcabc",
            {"maxsplit": 1},
            None,
            0,
            1,
            "str",
            {
                "type": "TypeError",
                "message_substring": "split() takes at most 2 arguments (3 given)",
            },
            ["maxsplit", "kwargs.maxsplit"],
            id="pattern-split-duplicate-maxsplit-keyword",
        ),
        pytest.param(
            "pattern.split",
            "abcabc",
            {"missing": 1},
            None,
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for split()",
            },
            ["kwargs.missing"],
            id="pattern-split-unexpected-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abc",
            {"count": 1},
            "x",
            1,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "sub() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.count"],
            id="pattern-sub-duplicate-count-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count_alias": 1},
            "x",
            0,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "'count_alias' is an invalid keyword argument for sub()",
            },
            ["kwargs.count_alias"],
            id="pattern-sub-count-alias-keyword",
        ),
        pytest.param(
            "pattern.subn",
            "abc",
            {"missing": 1},
            "x",
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for subn()",
            },
            ["kwargs.missing"],
            id="pattern-subn-unexpected-keyword",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count_alias": 1},
            "x",
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'count_alias' is an invalid keyword argument for subn()",
            },
            ["kwargs.count_alias"],
            id="pattern-subn-count-alias-keyword",
        ),
    ),
)
def test_pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    text_model: str,
    expected_exception: dict[str, str],
    expected_field_names: list[str],
) -> None:
    workload = support._pattern_helper_collection_replacement_keyword_error_workload(
        operation=operation,
        haystack=haystack,
        kwargs_payload=kwargs_payload,
        replacement=replacement,
        count=count,
        maxsplit=maxsplit,
        expected_exception=expected_exception,
        text_model=text_model,
    )
    observed_field_names = benchmark_test_support._record_numeric_materialization_fields(
        monkeypatch
    )
    callback_field_names: list[str] = []
    helper_name = workload.operation.removeprefix("pattern.")
    positional_keyword_field = (
        benchmark_test_support._collection_replacement_positional_keyword_field(
            workload
        )
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        for _ in range(2):
            with pytest.raises(TypeError) as expected_error:
                compiled_pattern = re.compile(
                    workload.pattern_payload(),
                    workload.flags,
                )
                kwargs = dict(workload.kwargs)
                if workload.operation == "pattern.split":
                    args: list[object] = [workload.haystack_payload()]
                    if positional_keyword_field == "maxsplit":
                        args.append(workload.maxsplit_argument())
                    getattr(compiled_pattern, helper_name)(*args, **kwargs)
                elif workload.operation in {"pattern.sub", "pattern.subn"}:
                    args = [
                        workload.replacement_payload(),
                        workload.haystack_payload(),
                    ]
                    if positional_keyword_field == "count":
                        args.append(workload.count_argument())
                    getattr(compiled_pattern, helper_name)(*args, **kwargs)
                else:
                    raise AssertionError(
                        "unexpected pattern helper keyword-error workload "
                        f"operation {workload.operation!r}"
                    )
            observed_field_names.clear()
            with pytest.raises(TypeError) as observed_error:
                callback()
            callback_field_names.extend(observed_field_names)

            assert str(observed_error.value) == str(expected_error.value)

        assert callback_field_names == expected_field_names * 2
    finally:
        re.purge()


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    support._assert_keyword_error_workload_probe_measured(
        source_workload,
        import_name=import_name,
        adapter_name=adapter_name,
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_result",
        "expected_exception_message",
        "expected_field_names",
    ),
    (
        pytest.param(
            "module.split",
            "zabczabc",
            {"maxsplit": 1},
            None,
            0,
            0,
            "bytes",
            [b"z", b"zabc"],
            None,
            ["kwargs.maxsplit"],
            id="module-split-maxsplit-int",
        ),
        pytest.param(
            "module.sub",
            "abcabc",
            {"count": 1},
            "x",
            0,
            0,
            "str",
            "xabc",
            None,
            ["kwargs.count"],
            id="module-sub-count-int",
        ),
        pytest.param(
            "module.subn",
            "abcabc",
            {"count": True},
            "x",
            0,
            0,
            "bytes",
            (b"xabc", 1),
            None,
            ["kwargs.count"],
            id="module-subn-count-bool",
        ),
        pytest.param(
            "module.split",
            "abc",
            {"missing": 1},
            None,
            0,
            0,
            "str",
            None,
            "split() got an unexpected keyword argument 'missing'",
            ["kwargs.missing"],
            id="module-split-unexpected-keyword",
        ),
        pytest.param(
            "module.sub",
            "abcabc",
            {"count_alias": 1},
            "x",
            0,
            0,
            "str",
            None,
            "sub() got an unexpected keyword argument 'count_alias'",
            ["kwargs.count_alias"],
            id="module-sub-count-alias-keyword",
        ),
        pytest.param(
            "module.subn",
            "abc",
            {"missing": 1},
            "x",
            1,
            0,
            "bytes",
            None,
            "subn() got an unexpected keyword argument 'missing'",
            ["count", "kwargs.missing"],
            id="module-subn-unexpected-keyword-after-positional-count",
        ),
    ),
)
def test_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: int,
    maxsplit: int,
    text_model: str,
    expected_result: object | None,
    expected_exception_message: str | None,
    expected_field_names: list[str],
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-materialization-contract",
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "expected_exception": (
                None
                if expected_exception_message is None
                else {
                    "type": "TypeError",
                    "message_substring": expected_exception_message,
                }
            ),
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    benchmark_test_support._assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=expected_result,
        expected_exception_message=expected_exception_message,
        expected_field_names=expected_field_names,
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    ),
)
def test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    source_workload: Workload,
) -> None:
    observed_field_names = benchmark_test_support._record_numeric_materialization_fields(
        monkeypatch
    )

    re.purge()
    try:
        callback = build_callable(re, "re", source_workload)
        assert observed_field_names == []

        with pytest.raises(TypeError) as expected_error:
            benchmark_test_support.run_benchmark_workload_with_cpython(
                source_workload
            )
        observed_field_names.clear()
        with pytest.raises(TypeError) as observed_error:
            callback()

        expected_field_names = [f"kwargs.{name}" for name in source_workload.kwargs]
        if not benchmark_test_support._is_module_workflow_keyword_error_workload(
            source_workload
        ):
            positional_keyword_field = (
                benchmark_test_support._collection_replacement_positional_keyword_field(
                    source_workload
                )
            )
            if positional_keyword_field is not None:
                expected_field_names.insert(0, positional_keyword_field)

        assert observed_field_names == expected_field_names
        assert str(observed_error.value) == str(expected_error.value)
    finally:
        re.purge()


@pytest.mark.parametrize(
    (
        "workload_id",
        "bucket",
        "operation",
        "haystack",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_result",
        "expected_field_name",
    ),
    (
        pytest.param(
            "module-split-indexlike-contract-bytes",
            "module-split",
            "module.split",
            "zabcabcabc",
            None,
            0,
            {"type": "indexlike", "value": 2},
            "bytes",
            [b"z", b"", b"abc"],
            "maxsplit",
            id="module-split",
        ),
        pytest.param(
            "module-sub-indexlike-contract-str",
            "module-sub",
            "module.sub",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "str",
            "xxabc",
            "count",
            id="module-sub",
        ),
        pytest.param(
            "module-subn-indexlike-contract-bytes",
            "module-subn",
            "module.subn",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "bytes",
            (b"xxabc", 2),
            "count",
            id="module-subn",
        ),
        pytest.param(
            "pattern-split-indexlike-contract-str",
            "pattern-split",
            "pattern.split",
            "zabcabcabc",
            None,
            0,
            {"type": "indexlike", "value": 2},
            "str",
            ["z", "", "abc"],
            "maxsplit",
            id="pattern-split",
        ),
        pytest.param(
            "pattern-sub-indexlike-contract-bytes",
            "pattern-sub",
            "pattern.sub",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "bytes",
            b"xxabc",
            "count",
            id="pattern-sub",
        ),
        pytest.param(
            "pattern-subn-indexlike-contract-str",
            "pattern-subn",
            "pattern.subn",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "str",
            ("xxabc", 2),
            "count",
            id="pattern-subn",
        ),
    ),
)
def test_collection_replacement_indexlike_descriptors_materialize_on_each_helper_call(
    monkeypatch,
    workload_id: str,
    bucket: str,
    operation: str,
    haystack: str,
    replacement: str | None,
    count: object,
    maxsplit: object,
    text_model: str,
    expected_result: object,
    expected_field_name: str,
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-indexlike-contract",
            "workload_id": workload_id,
            "bucket": bucket,
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": (
                "module-helper-call"
                if operation.startswith("module.")
                else "pattern-helper-call"
            ),
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    observed_field_names = benchmark_test_support._record_numeric_materialization_fields(
        monkeypatch
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []
        assert callback() == expected_result
        assert callback() == expected_result
    finally:
        re.purge()

    assert observed_field_names == [expected_field_name, expected_field_name]


def test_pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor(
) -> None:
    manifest = load_manifest(
        support.benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH
    )
    workload = next(
        candidate
        for candidate in manifest.workloads
        if candidate.workload_id == "pattern-split-no-match-warm-str"
    )

    assert workload.maxsplit == 0
    assert (
        support._COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES[
            "split"
        ].workload_signature(workload)
        == (
        "pattern.split",
        "abc",
        ("zzz",),
        (),
        0,
        "str",
        )
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    support._assert_keyword_error_workload_probe_measured(
        source_workload,
        import_name=import_name,
        adapter_name=adapter_name,
    )
