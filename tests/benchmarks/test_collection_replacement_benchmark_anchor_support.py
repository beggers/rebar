from __future__ import annotations

from types import SimpleNamespace

import pytest

from rebar_harness.benchmarks import workload_from_payload
from tests.benchmarks import collection_replacement_benchmark_anchor_support as support
from tests.python.fixture_parity_support import IndexLike


def _collection_replacement_workload(
    *,
    manifest_id: str = "collection-replacement-boundary",
    workload_id: str,
    operation: str,
    haystack: str,
    pattern: str = "abc",
    replacement: str | None = None,
    count: object = 0,
    maxsplit: object = 0,
    kwargs: dict[str, object] | None = None,
    expected_exception: dict[str, str] | None = None,
    text_model: str = "str",
    haystack_text_model: str | None = None,
    use_compiled_pattern: bool = False,
) -> object:
    return workload_from_payload(
        {
            "manifest_id": manifest_id,
            "workload_id": workload_id,
            "bucket": operation.replace(".", "-"),
            "family": "module",
            "operation": operation,
            "pattern": pattern,
            "haystack": haystack,
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "use_compiled_pattern": use_compiled_pattern,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": {} if kwargs is None else kwargs,
            "text_model": text_model,
            "haystack_text_model": haystack_text_model,
            "cache_mode": "warm",
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
) -> object:
    pattern_value = pattern.encode() if text_model == "bytes" else pattern
    return SimpleNamespace(
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


def test_positional_indexlike_workloads_stay_in_scope_and_keep_expected_signature() -> None:
    split_workload = _collection_replacement_workload(
        workload_id="module-split-indexlike",
        operation="module.split",
        haystack="zabcabc",
        maxsplit={"type": "indexlike", "value": 2},
    )
    sub_workload = _collection_replacement_workload(
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
    keyword_workload = _collection_replacement_workload(
        workload_id="module-split-keyword",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": {"type": "indexlike", "value": 1}},
    )
    plain_int_workload = _collection_replacement_workload(
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
    expected_keyword_workload = _collection_replacement_workload(
        workload_id="module-split-keyword-indexlike",
        operation="module.split",
        haystack="zabcabc",
        kwargs={"maxsplit": {"type": "indexlike", "value": 1}},
    )
    duplicate_keyword_workload = _collection_replacement_workload(
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
    unexpected_keyword_workload = _collection_replacement_workload(
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
    multiple_keyword_workload = _collection_replacement_workload(
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
    search_keyword_workload = _collection_replacement_workload(
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


def test_compiled_pattern_wrong_text_model_workloads_keep_scope_and_split_sub_signatures() -> None:
    split_workload = _collection_replacement_workload(
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
    subn_workload = _collection_replacement_workload(
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
    direct_pattern_workload = _collection_replacement_workload(
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
    split_workload = _collection_replacement_workload(
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
    sub_workload = _collection_replacement_workload(
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
    compiled_pattern_workload = _collection_replacement_workload(
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
