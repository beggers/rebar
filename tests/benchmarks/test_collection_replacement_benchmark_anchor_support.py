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
    _write_test_manifest,
    selected_manifest_workloads,
)
from tests.benchmarks import collection_replacement_benchmark_anchor_support as support
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkModule,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _SourceTreeContractBuilderSpec,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)
from tests.python.fixture_parity_support import IndexLike


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
_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC = _SourceTreeContractBuilderSpec(
    manifest_id="collection-replacement-boundary",
    excluded_fields=_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS,
    timing_scope="pattern-helper-call",
)


def _collection_replacement_wrong_text_model_source_workloads() -> tuple[Workload, ...]:
    return selected_manifest_workloads(
        "collection_replacement_boundary.py",
        include_workload=support._is_collection_replacement_pattern_wrong_text_model_workload,
    )


def _assert_wrong_text_model_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes
    expected_haystack_type = (
        str if source_workload.haystack_text_model == "str" else bytes
    )

    assert payload.get("use_compiled_pattern") is None
    assert round_tripped.use_compiled_pattern is False
    assert payload["timing_scope"] == "pattern-helper-call"
    assert round_tripped.timing_scope == "pattern-helper-call"
    assert payload["haystack_text_model"] == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if source_workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _collection_replacement_wrong_text_model_expected_build_calls(
    source_workload: Workload,
) -> list[tuple[object, ...]]:
    compile_call = (
        "compile",
        source_workload.pattern_payload(),
        source_workload.flags,
    )
    if source_workload.cache_mode == "warm":
        return [compile_call]
    if source_workload.cache_mode == "purged":
        return [compile_call, ("purge",)]
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"cache mode {source_workload.cache_mode!r}"
    )


def _collection_replacement_wrong_text_model_expected_callback_call(
    source_workload: Workload,
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
    source_workload: Workload,
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
    workload: Workload,
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


def test_collection_replacement_pattern_wrong_text_model_source_workloads_stay_exact_and_in_order() -> None:
    workloads = _collection_replacement_wrong_text_model_source_workloads()

    assert tuple(workload.workload_id for workload in workloads) == (
        _COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _collection_replacement_wrong_text_model_source_workloads()
    ),
)
def test_collection_replacement_pattern_wrong_text_model_helpers_preserve_callback_and_runtime_contract(
    workload: Workload,
) -> None:
    assert _collection_replacement_wrong_text_model_expected_build_calls(workload) == (
        [("compile", workload.pattern_payload(), workload.flags)]
        if workload.cache_mode == "warm"
        else [("compile", workload.pattern_payload(), workload.flags), ("purge",)]
    )
    assert _collection_replacement_wrong_text_model_expected_callback_call(
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
    assert _collection_replacement_wrong_text_model_expected_callback_result(
        workload
    ) == (
        ("pattern-result", 0)
        if workload.operation == "pattern.subn"
        else "pattern-result"
    )

    with pytest.raises(TypeError) as observed_error:
        _run_cpython_collection_replacement_wrong_text_model_workload(workload)

    assert str(observed_error.value) == str(
        workload.expected_exception["message_substring"]
    )


def test_standard_benchmark_manifest_preserves_collection_replacement_pattern_wrong_text_model_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = _collection_replacement_wrong_text_model_source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
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
        _COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract"
        for workload_id in _COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
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
        )

        with pytest.raises(TypeError) as expected_error:
            _run_cpython_collection_replacement_wrong_text_model_workload(workload)
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
        for workload in _collection_replacement_wrong_text_model_source_workloads()
    ),
)
def test_run_internal_workload_probe_measures_collection_replacement_pattern_wrong_text_model_contract_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
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
        for workload in _collection_replacement_wrong_text_model_source_workloads()
    ),
)
def test_collection_replacement_pattern_wrong_text_model_callbacks_preserve_precompile_contract(
    source_workload: Workload,
) -> None:
    expected_build_calls = _collection_replacement_wrong_text_model_expected_build_calls(
        source_workload
    )
    expected_callback_call = (
        _collection_replacement_wrong_text_model_expected_callback_call(source_workload)
    )
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC,
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == (
        _collection_replacement_wrong_text_model_expected_callback_result(
            source_workload
        )
    )
    assert module.calls[-1] == expected_callback_call


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _collection_replacement_wrong_text_model_source_workloads()
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
