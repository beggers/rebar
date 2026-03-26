from __future__ import annotations

import json
import pathlib
from types import SimpleNamespace

import pytest

from rebar_harness.benchmarks import (
    Workload,
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_replacement_support,
)
from tests.benchmarks import benchmark_test_support as support
from tests.benchmarks import (
    pattern_boundary_benchmark_anchor_support as pattern_boundary_support,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support
from tests.python.fixture_parity_support import IndexLike


def _explicit_standard_benchmark_definitions(
) -> tuple[support.StandardBenchmarkAnchorContractDefinition, ...]:
    return (
        *support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_replacement_support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
        *support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
        *support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
        *support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
        *pattern_boundary_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
        *source_tree_support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
    )


def test_pattern_boundary_wrong_text_model_support_surface_is_owner_module_owned_without_local_duplicates(
) -> None:
    import sys

    support.assert_owner_surface_module_owned_without_local_duplicates(
        sys.modules[__name__],
        pattern_boundary_support,
        definition_names=(
            "_pattern_boundary_wrong_text_model_source_workloads",
            "_pattern_boundary_wrong_text_model_expected_callback_call",
            "_run_cpython_pattern_boundary_wrong_text_model_workload",
            "_pattern_boundary_wrong_text_model_correctness_case_signature",
            "_pattern_boundary_wrong_text_model_workload_signature",
            "_is_pattern_boundary_wrong_text_model_workload",
        ),
        assignment_names=(
            "_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        ),
        extra_owner_name="_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC",
        extra_owner_module=pattern_boundary_support,
    )


def test_pattern_boundary_standard_definitions_are_owner_owned_in_exact_order() -> None:
    definitions = pattern_boundary_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS
    definition_names = tuple(definition.name for definition in definitions)

    assert isinstance(definitions, tuple)
    assert definition_names == (
        "pattern-window-positional-indexlike",
        "pattern-window-keyword",
        "pattern-boundary-bounded-wildcard",
        "pattern-boundary-verbose-regression",
        "pattern-boundary-wrong-text-model",
    )


def test_pattern_boundary_standard_definitions_are_reused_by_standard_inventory() -> None:
    owner_definitions = pattern_boundary_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS
    owner_definition_names = tuple(definition.name for definition in owner_definitions)
    standard_definitions_by_name = {
        definition.name: definition
        for definition in _explicit_standard_benchmark_definitions()
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


def test_pattern_bounded_wildcard_selector_and_signature_stay_pinned() -> None:
    workload = support.synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id=support._PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS[0],
        operation="pattern.search",
        flags=2,
        pattern="a.c",
        haystack="zabc",
        timing_scope="pattern-helper-call",
        pos=1,
        endpos=4,
    )

    assert support._is_pattern_bounded_wildcard_workload(workload)
    assert support._pattern_bounded_wildcard_workload_signature(workload) == (
        "pattern.search",
        "a.c",
        ("zabc", 1, 4),
        (),
        2,
        "str",
    )


def test_pattern_window_positional_indexlike_workload_and_case_signatures_stay_pinned() -> None:
    workload = support.synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="pattern-finditer-window-indexlike",
        operation="pattern.finditer",
        haystack="zabcabc",
        categories=["positional-window", "indexlike"],
        pos={"type": "indexlike", "value": 1},
        endpos={"type": "indexlike", "value": 6},
    )
    case = support._module_pattern_case(
        case_id="workflow-pattern-finditer-str-window-indexlike-positional",
        helper="finditer",
        operation="pattern_call",
        args=("zabcabc", IndexLike(1), IndexLike(6)),
        pattern="abc",
        flags=0,
    )

    assert support._is_pattern_window_positional_indexlike_workload(workload)
    assert support._pattern_window_positional_indexlike_workload_args(workload) == (
        "zabcabc",
        {"type": "indexlike", "value": 1},
        {"type": "indexlike", "value": 6},
    )
    assert support._pattern_window_positional_indexlike_workload_signature(
        workload
    ) == (
        "finditer",
        "abc",
        (("str", "zabcabc"), ("indexlike", 1), ("indexlike", 6)),
        "str",
    )
    assert support._pattern_window_positional_indexlike_correctness_case_signature(
        case
    ) == (
        "finditer",
        "abc",
        (("str", "zabcabc"), ("indexlike", 1), ("indexlike", 6)),
        "str",
    )


def test_pattern_keyword_window_workload_and_case_signatures_stay_pinned() -> None:
    workload = support.synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="pattern-findall-bool-window-keyword",
        operation="pattern.findall",
        haystack="zabcabc",
        kwargs={"endpos": True},
        categories=["keyword"],
    )
    case = support._module_pattern_case(
        case_id="workflow-pattern-findall-str-bool-window-keyword",
        helper="findall",
        operation="pattern_call",
        args=("zabcabc",),
        pattern="abc",
        flags=0,
        kwargs={"endpos": True},
    )

    assert support._is_pattern_keyword_window_workload(workload)
    assert support._pattern_keyword_window_workload_signature(workload) == (
        "pattern.findall",
        "abc",
        ("zabcabc",),
        (("endpos", "bool", True),),
        0,
        "str",
    )
    assert support._pattern_keyword_window_correctness_case_signature(case) == (
        "pattern.findall",
        "abc",
        ("zabcabc",),
        (("endpos", "bool", True),),
        0,
        "str",
    )


def test_pattern_bounded_wildcard_selector_rejects_nonmatching_pattern() -> None:
    workload = support.synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id=support._PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS[1],
        operation="pattern.match",
        pattern="abc",
        haystack="zabc",
        timing_scope="pattern-helper-call",
        pos=0,
        endpos=3,
    )

    assert not support._is_pattern_bounded_wildcard_workload(workload)


def test_pattern_verbose_regression_selector_and_signature_stay_pinned() -> None:
    workload = support.synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id=support._PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS[0],
        operation="pattern.search",
        pattern=(
            "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"
        ),
        haystack="KEY = 42",
        flags=72,
        timing_scope="pattern-helper-call",
    )

    assert support._is_pattern_verbose_regression_workload(workload)
    assert support._pattern_verbose_regression_workload_signature(workload) == (
        "pattern.search",
        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        ("KEY = 42",),
        (),
        72,
        "str",
    )


def test_pattern_verbose_regression_correctness_case_signature_stays_pinned() -> None:
    case = support._module_pattern_case(
        case_id=support._PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS[0],
        helper="fullmatch",
        operation="pattern_call",
        args=("KEY = ABC",),
        pattern="^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        flags=72,
    )

    assert support._pattern_verbose_regression_correctness_case_signature(case) == (
        "pattern.fullmatch",
        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        ("KEY = ABC",),
        (),
        72,
        "str",
    )


def test_pattern_boundary_wrong_text_model_selector_accepts_exact_trio_and_signature_shape() -> None:
    workload = support.synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id="pattern.search-wrong-text-model",
        operation="pattern.search",
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
    )

    assert pattern_boundary_support._is_pattern_boundary_wrong_text_model_workload(
        workload
    )
    assert pattern_boundary_support._pattern_boundary_wrong_text_model_workload_signature(
        workload
    ) == (
        "pattern.search",
        "abc",
        (b"abc",),
        (),
        0,
        "str",
    )


def test_pattern_boundary_wrong_text_model_selector_rejects_compiled_pattern_window_and_keyword_rows() -> None:
    compiled_pattern_workload = SimpleNamespace(
        workload_id="pattern-search-compiled-pattern",
        operation="pattern.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        kwargs={},
        pos=None,
        endpos=None,
    )
    keyword_workload = SimpleNamespace(
        workload_id="pattern-search-keyword",
        operation="pattern.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=False,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        kwargs={"pos": 1},
        pos=None,
        endpos=None,
    )
    windowed_workload = SimpleNamespace(
        workload_id="pattern-search-window",
        operation="pattern.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=False,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        kwargs={},
        pos=0,
        endpos=None,
    )

    assert not pattern_boundary_support._is_pattern_boundary_wrong_text_model_workload(
        compiled_pattern_workload
    )
    assert not pattern_boundary_support._is_pattern_boundary_wrong_text_model_workload(
        keyword_workload
    )
    assert not pattern_boundary_support._is_pattern_boundary_wrong_text_model_workload(
        windowed_workload
    )


def test_pattern_boundary_wrong_text_model_correctness_case_signatures_cover_str_and_bytes_rows() -> None:
    str_case = support._module_pattern_case(
        case_id="workflow-pattern-search-str-wrong-text-model",
        helper="search",
        operation="pattern_call",
        args=(b"abc",),
        pattern="abc",
        flags=0,
        text_model="str",
    )
    bytes_case = support._module_pattern_case(
        case_id="workflow-pattern-match-bytes-wrong-text-model",
        helper="match",
        operation="pattern_call",
        args=("abc",),
        pattern="abc",
        flags=0,
        text_model="bytes",
    )
    wrong_haystack_type = support._module_pattern_case(
        case_id="workflow-pattern-fullmatch-str-not-wrong-text-model",
        helper="fullmatch",
        operation="pattern_call",
        args=("abc",),
        pattern="abc",
        flags=0,
        text_model="str",
    )

    assert pattern_boundary_support._pattern_boundary_wrong_text_model_correctness_case_signature(
        str_case
    ) == (
        "pattern.search",
        "abc",
        (b"abc",),
        (),
        0,
        "str",
    )
    assert pattern_boundary_support._pattern_boundary_wrong_text_model_correctness_case_signature(
        bytes_case
    ) == (
        "pattern.match",
        b"abc",
        ("abc",),
        (),
        0,
        "bytes",
    )
    assert (
        pattern_boundary_support._pattern_boundary_wrong_text_model_correctness_case_signature(
            wrong_haystack_type
        )
        is None
    )


def test_pattern_boundary_wrong_text_model_source_workloads_stay_exact_and_in_order() -> None:
    workloads = pattern_boundary_support._pattern_boundary_wrong_text_model_source_workloads()

    assert tuple(workload.workload_id for workload in workloads) == (
        pattern_boundary_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )


def test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured() -> None:
    all_workloads = support.selected_manifest_workloads("pattern_boundary.py")
    wrong_text_model_workload_ids = tuple(
        workload.workload_id
        for workload in pattern_boundary_support._pattern_boundary_wrong_text_model_source_workloads()
    )
    bounded_wildcard_workload_ids = tuple(
        workload.workload_id
        for workload in support.selected_manifest_workloads(
            "pattern_boundary.py",
            include_workload=support._is_pattern_bounded_wildcard_workload,
        )
    )
    verbose_regression_workload_ids = tuple(
        workload.workload_id
        for workload in support.selected_manifest_workloads(
            "pattern_boundary.py",
            include_workload=support._is_pattern_verbose_regression_workload,
        )
    )
    fullmatch_verbose_regression_workload_ids = tuple(
        workload.workload_id
        for workload in support.selected_manifest_workloads(
            "pattern_boundary.py",
            include_workload=lambda workload: (
                support._is_pattern_verbose_regression_workload(workload)
                and workload.operation == "pattern.fullmatch"
            ),
        )
    )
    keyword_workload_ids = tuple(
        workload.workload_id
        for workload in support.selected_manifest_workloads(
            "pattern_boundary.py",
            include_workload=support._is_pattern_keyword_window_workload,
        )
    )
    positional_workload_ids = tuple(
        workload.workload_id
        for workload in support.selected_manifest_workloads(
            "pattern_boundary.py",
            include_workload=support._is_pattern_window_positional_indexlike_workload,
        )
    )

    assert len(all_workloads) == 49
    assert wrong_text_model_workload_ids == (
        "pattern-search-on-bytes-string-warm-str",
        "pattern-match-on-str-string-purged-bytes",
        "pattern-fullmatch-on-bytes-string-warm-str",
    )
    assert (
        bounded_wildcard_workload_ids
        == support._PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS
    )
    assert (
        verbose_regression_workload_ids
        == support._PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS
    )
    assert (
        fullmatch_verbose_regression_workload_ids
        == support._PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS
    )
    assert keyword_workload_ids == (
        "pattern-search-pos-keyword-warm-str",
        "pattern-search-bool-endpos-keyword-warm-str",
        "pattern-search-endpos-keyword-purged-bytes",
        "pattern-search-pos-indexlike-keyword-warm-str",
        "pattern-search-endpos-indexlike-keyword-purged-bytes",
        "pattern-match-pos-keyword-purged-str",
        "pattern-match-bool-pos-keyword-purged-str",
        "pattern-match-window-indexlike-purged-bytes",
        "pattern-fullmatch-window-keyword-purged-bytes",
        "pattern-fullmatch-window-indexlike-keyword-purged-bytes",
        "pattern-findall-window-keyword-warm-str",
        "pattern-findall-window-indexlike-keyword-warm-str",
        "pattern-findall-bool-window-keyword-warm-str",
        "pattern-finditer-window-keyword-purged-bytes",
        "pattern-finditer-window-indexlike-purged-bytes",
        "pattern-finditer-bool-window-keyword-purged-bytes",
    )
    assert positional_workload_ids == (
        "pattern-search-pos-indexlike-positional-warm-str",
        "pattern-search-endpos-indexlike-positional-purged-bytes",
        "pattern-match-window-indexlike-positional-purged-bytes",
        "pattern-fullmatch-window-indexlike-positional-purged-bytes",
        "pattern-findall-window-indexlike-positional-warm-str",
        "pattern-finditer-window-indexlike-positional-purged-bytes",
    )

    support.assert_zero_gap_manifest_workloads_measured(
        manifest_path="pattern_boundary.py",
        manifest_id="pattern-boundary",
        expected_measured_workload_ids=(
            wrong_text_model_workload_ids
            + bounded_wildcard_workload_ids
            + verbose_regression_workload_ids
            + keyword_workload_ids
            + positional_workload_ids
        ),
        expected_measured_workload_count=49,
        expected_total_workload_count=49,
    )


@pytest.mark.parametrize(
    "workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in pattern_boundary_support._pattern_boundary_wrong_text_model_source_workloads()
    ),
)
def test_pattern_boundary_wrong_text_model_helpers_preserve_callback_and_runtime_contract(
    workload: Workload,
) -> None:
    assert support.compiled_pattern_contract_expected_build_calls(
        workload,
        label="direct Pattern pattern-boundary wrong-text-model",
    ) == (
        [("compile", workload.pattern_payload(), workload.flags)]
        if workload.cache_mode == "warm"
        else [("compile", workload.pattern_payload(), workload.flags), ("purge",)]
    )
    assert pattern_boundary_support._pattern_boundary_wrong_text_model_expected_callback_call(
        workload
    ) == (
        workload.operation,
        workload.haystack_payload(),
        (),
        {},
    )

    with pytest.raises(TypeError) as observed_error:
        pattern_boundary_support._run_cpython_pattern_boundary_wrong_text_model_workload(
            workload
        )

    assert str(observed_error.value) == str(
        workload.expected_exception["message_substring"]
    )


def test_standard_benchmark_manifest_preserves_pattern_boundary_wrong_text_model_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = pattern_boundary_support._pattern_boundary_wrong_text_model_source_workloads()
    manifest = source_tree_support._source_tree_contract_manifest(
        source_workloads,
        spec=pattern_boundary_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    manifest_path = support._write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_boundary_wrong_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = tuple(load_manifest(manifest_path).workloads)

    assert tuple(workload.workload_id for workload in source_workloads) == (
        pattern_boundary_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract"
        for workload_id in pattern_boundary_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
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

        support.assert_pattern_helper_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        with pytest.raises(TypeError) as expected_error:
            pattern_boundary_support._run_cpython_pattern_boundary_wrong_text_model_workload(
                workload
            )
        with pytest.raises(TypeError) as observed_error:
            support.run_benchmark_workload_with_cpython(round_tripped)

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
        for workload in pattern_boundary_support._pattern_boundary_wrong_text_model_source_workloads()
    ),
)
def test_run_internal_workload_probe_measures_pattern_boundary_wrong_text_model_contract_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = source_tree_support._source_tree_contract_workload(
        source_workload,
        spec=pattern_boundary_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    support.assert_pattern_helper_wrong_text_model_payload_round_trip(
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
        for workload in pattern_boundary_support._pattern_boundary_wrong_text_model_source_workloads()
    ),
)
def test_pattern_boundary_wrong_text_model_callbacks_preserve_precompile_contract(
    source_workload: Workload,
) -> None:
    expected_build_calls = support.compiled_pattern_contract_expected_build_calls(
        source_workload,
        label="direct Pattern pattern-boundary wrong-text-model",
    )
    expected_callback_call = (
        pattern_boundary_support._pattern_boundary_wrong_text_model_expected_callback_call(
            source_workload
        )
    )
    module = support.RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        source_tree_support._source_tree_contract_workload(
            source_workload,
            spec=pattern_boundary_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC,
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == "pattern-result"
    assert module.calls[-1] == expected_callback_call
