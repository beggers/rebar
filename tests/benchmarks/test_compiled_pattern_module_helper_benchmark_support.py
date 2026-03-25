from __future__ import annotations

import json
import pathlib
import re
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
from tests.benchmarks.benchmark_test_support import synthetic_workload
from tests.benchmarks.benchmark_test_support import (
    RecordingBenchmarkModule,
    STANDARD_BENCHMARK_DEFINITIONS,
    _write_test_manifest,
)
from tests.benchmarks import (
    compiled_pattern_module_helper_benchmark_support as compiled_pattern_module_helper_support,
)
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS,
    _COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS,
    _assert_wrong_text_model_payload_round_trip,
    _compiled_pattern_wrong_text_model_contract_spec,
    _compiled_pattern_wrong_text_model_source_workloads,
    _compiled_pattern_wrong_text_model_specs,
    _compiled_pattern_module_helper_route,
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
    _module_workflow_compiled_pattern_correctness_case_signature,
    _module_workflow_compiled_pattern_workload_signature,
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
    _run_cpython_compiled_pattern_module_helper_workload,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks.benchmark_test_support import (
    compiled_pattern_contract_expected_build_calls,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)


def _manifest_id_for_operation(operation: str) -> str:
    if operation in {"module.search", "module.match", "module.fullmatch"}:
        return "module-boundary"
    return "collection-replacement-boundary"


def _fake_workload(
    *,
    workload_id: str,
    operation: str,
    text_model: str = "str",
    haystack_text_model: str | None = None,
    use_compiled_pattern: bool = False,
    expected_exception: dict[str, str] | None = None,
    kwargs: dict[str, object] | None = None,
) -> object:
    return SimpleNamespace(
        workload_id=workload_id,
        operation=operation,
        flags=0,
        text_model=text_model,
        haystack_text_model=haystack_text_model,
        use_compiled_pattern=use_compiled_pattern,
        expected_exception=expected_exception,
        kwargs={} if kwargs is None else kwargs,
    )


def test_compiled_pattern_wrong_text_model_support_surface_is_owner_module_owned_without_local_duplicates(
) -> None:
    import sys

    from tests.benchmarks import (
        compiled_pattern_module_helper_benchmark_support as support,
    )
    from tests.benchmarks.benchmark_test_support import (
        top_level_module_definition_and_assignment_names,
    )

    local_definition_names, local_assignment_names = (
        top_level_module_definition_and_assignment_names(sys.modules[__name__])
    )

    assert (
        _COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        is support._COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert (
        _COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        is support._COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert (
        _compiled_pattern_wrong_text_model_specs
        is support._compiled_pattern_wrong_text_model_specs
    )
    assert (
        _compiled_pattern_wrong_text_model_source_workloads
        is support._compiled_pattern_wrong_text_model_source_workloads
    )
    assert (
        _compiled_pattern_wrong_text_model_contract_spec
        is support._compiled_pattern_wrong_text_model_contract_spec
    )
    assert (
        _assert_wrong_text_model_payload_round_trip
        is support._assert_wrong_text_model_payload_round_trip
    )
    assert (
        _is_module_workflow_compiled_pattern_wrong_text_model_workload
        is support._is_module_workflow_compiled_pattern_wrong_text_model_workload
    )
    assert {
        "_compiled_pattern_wrong_text_model_specs",
        "_compiled_pattern_wrong_text_model_source_workloads",
        "_compiled_pattern_wrong_text_model_contract_spec",
        "_assert_wrong_text_model_payload_round_trip",
        "_is_module_workflow_compiled_pattern_wrong_text_model_workload",
    }.isdisjoint(local_definition_names)
    assert {
        "_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
    }.isdisjoint(local_assignment_names)


def test_standard_inventory_reuses_owner_owned_compiled_pattern_module_helper_definitions(
) -> None:
    owner_definitions = (
        compiled_pattern_module_helper_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS
    )
    definition_names = {
        "module-workflow-compiled-pattern-literal-success",
        "module-workflow-compiled-pattern-bounded-wildcard-success",
        "module-workflow-compiled-pattern-verbose-bytes-success",
        "module-workflow-compiled-pattern-wrong-text-model",
    }

    standard_definitions = tuple(
        definition
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if definition.name in definition_names
    )

    assert tuple(definition.name for definition in owner_definitions) == (
        "module-workflow-compiled-pattern-literal-success",
        "module-workflow-compiled-pattern-bounded-wildcard-success",
        "module-workflow-compiled-pattern-verbose-bytes-success",
        "module-workflow-compiled-pattern-wrong-text-model",
    )
    assert standard_definitions == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_definitions,
            owner_definitions,
            strict=True,
        )
    )


@pytest.mark.parametrize(
    ("workload", "callback_flags", "expected_result", "expected_call", "expected_cpython_args", "materialize"),
    (
        (
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.search"),
                workload_id="module-search-success",
                operation="module.search",
                pattern="abc",
                haystack="zzabczz",
                flags=re.IGNORECASE,
                use_compiled_pattern=True,
            ),
            re.IGNORECASE,
            "module-result",
            ("module.search", "zzabczz", 0, {}),
            ("zzabczz", re.IGNORECASE),
            False,
        ),
        (
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.subn"),
                workload_id="module-subn-success",
                operation="module.subn",
                pattern="abc",
                haystack="abcabc",
                replacement="x",
                count=1,
                flags=re.IGNORECASE,
                use_compiled_pattern=True,
            ),
            re.IGNORECASE,
            ("module-result", 0),
            ("module.subn", "x", "abcabc", 1, re.IGNORECASE, {}),
            ("x", "abcabc", 1),
            False,
        ),
        (
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.finditer"),
                workload_id="module-finditer-wrong-text-model",
                operation="module.finditer",
                pattern="abc",
                haystack="abcabc",
                text_model="bytes",
                haystack_text_model="str",
                use_compiled_pattern=True,
                expected_exception={
                    "type": "TypeError",
                    "message_substring": "cannot use a bytes pattern on a string-like object",
                },
            ),
            0,
            ["module-finditer-result"],
            ("module.finditer", "abcabc", 0),
            ("abcabc", 0),
            True,
        ),
        (
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.split"),
                workload_id="module-split-success",
                operation="module.split",
                pattern="abc",
                haystack="abcabc",
                maxsplit=2,
                flags=re.MULTILINE,
                use_compiled_pattern=True,
            ),
            re.MULTILINE,
            "module-result",
            ("module.split", "abcabc", 2, re.MULTILINE, {}),
            ("abcabc", 2),
            False,
        ),
    ),
    ids=(
        "module-boundary-search",
        "collection-replacement-subn",
        "wrong-text-model-finditer",
        "collection-replacement-split",
    ),
)
def test_compiled_pattern_module_helper_route_preserves_expected_shapes(
    workload: object,
    callback_flags: int,
    expected_result: object,
    expected_call: tuple[object, ...],
    expected_cpython_args: tuple[object, ...],
    materialize: bool,
) -> None:
    route = _compiled_pattern_module_helper_route(
        workload,
        collection_replacement_callback_flags=callback_flags,
    )
    callback_result, callback_call, cpython_call_args, materialize_cpython_result = route

    assert callback_result == expected_result
    assert callback_call == expected_call
    assert cpython_call_args == expected_cpython_args
    assert materialize_cpython_result is materialize


def test_run_cpython_compiled_pattern_module_helper_workload_materializes_finditer() -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.finditer"),
        workload_id="module-finditer-runtime",
        operation="module.finditer",
        pattern="abc",
        haystack="abcabc",
        use_compiled_pattern=True,
    )

    result = _run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
    )

    assert isinstance(result, list)
    assert [match.group(0) for match in result] == ["abc", "abc"]


def test_run_cpython_compiled_pattern_module_helper_workload_preserves_scalar_result() -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.subn"),
        workload_id="module-subn-runtime",
        operation="module.subn",
        pattern="abc",
        haystack="abcabc",
        replacement="x",
        count=1,
        use_compiled_pattern=True,
    )

    result = _run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
    )

    assert result == ("xabc", 1)


def test_compiled_pattern_module_helper_wrong_text_model_selector_accepts_bounded_trio() -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.search"),
        workload_id="module.search-wrong-text-model",
        operation="module.search",
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )

    assert _is_module_workflow_compiled_pattern_wrong_text_model_workload(workload)


def test_compiled_pattern_module_helper_wrong_text_model_selector_rejects_missing_guard_fields() -> None:
    wrong_pattern_argument = _fake_workload(
        workload_id="module-search-direct-pattern",
        operation="module.search",
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    missing_haystack_text_model = _fake_workload(
        workload_id="module-search-no-haystack-model",
        operation="module.search",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    wrong_exception_type = _fake_workload(
        workload_id="module-search-value-error",
        operation="module.search",
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "ValueError",
            "message_substring": "wrong exception type",
        },
    )

    assert not _is_module_workflow_compiled_pattern_wrong_text_model_workload(
        wrong_pattern_argument
    )
    assert not _is_module_workflow_compiled_pattern_wrong_text_model_workload(
        missing_haystack_text_model
    )
    assert not _is_module_workflow_compiled_pattern_wrong_text_model_workload(
        wrong_exception_type
    )


def test_module_workflow_compiled_pattern_success_selectors_accept_bounded_workloads() -> None:
    literal_workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.search"),
        workload_id="module-search-literal-compiled-pattern",
        operation="module.search",
        pattern="abc",
        haystack="zzabczz",
        use_compiled_pattern=True,
    )
    wildcard_workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.fullmatch"),
        workload_id="module-fullmatch-bounded-wildcard-compiled-pattern",
        operation="module.fullmatch",
        pattern="a.c",
        haystack="abc",
        text_model="bytes",
        use_compiled_pattern=True,
    )
    verbose_workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.search"),
        workload_id="module-search-verbose-bytes-compiled-pattern",
        operation="module.search",
        pattern=r"^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $",
        haystack="FOO = 123",
        text_model="bytes",
        flags=re.VERBOSE | re.MULTILINE,
        use_compiled_pattern=True,
    )

    assert _is_module_workflow_compiled_pattern_literal_success_workload(literal_workload)
    assert (
        _module_workflow_compiled_pattern_workload_signature(literal_workload)
        == ("module.search", "abc", ("zzabczz",), True, 0, "str")
    )

    assert _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
        wildcard_workload
    )
    assert (
        _module_workflow_compiled_pattern_workload_signature(wildcard_workload)
        == ("module.fullmatch", b"a.c", (b"abc",), True, 0, "bytes")
    )

    assert _is_module_workflow_compiled_pattern_verbose_bytes_success_workload(
        verbose_workload
    )
    assert (
        _module_workflow_compiled_pattern_workload_signature(verbose_workload)
        == (
            "module.search",
            b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
            (b"FOO = 123",),
            True,
            re.VERBOSE | re.MULTILINE,
            "bytes",
        )
    )


def test_module_workflow_compiled_pattern_success_selectors_reject_non_matching_rows() -> None:
    direct_pattern_workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.search"),
        workload_id="module-search-direct-pattern",
        operation="module.search",
        pattern="abc",
        haystack="zzabczz",
    )
    wrong_haystack_model = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.match"),
        workload_id="module-match-wrong-text-model",
        operation="module.match",
        pattern="abc",
        haystack="zzabczz",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={"type": "TypeError", "message_substring": "wrong type"},
    )

    assert not _is_module_workflow_compiled_pattern_literal_success_workload(
        direct_pattern_workload
    )
    assert not _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
        wrong_haystack_model
    )


def test_module_workflow_compiled_pattern_correctness_case_signature_requires_compiled_module_call_shape() -> None:
    matching_case = _fake_workload(
        workload_id="unused",
        operation="module_call",
        use_compiled_pattern=True,
    )
    matching_case.helper = "search"
    matching_case.args = ("zzabczz",)
    matching_case.pattern = "abc"
    matching_case.pattern_payload = lambda: "abc"
    matching_case.text_model = "str"
    matching_case.flags = 0

    missing_args_case = _fake_workload(
        workload_id="unused-missing-args",
        operation="module_call",
        use_compiled_pattern=True,
    )
    missing_args_case.helper = "search"
    missing_args_case.args = ()
    missing_args_case.pattern = "abc"
    missing_args_case.pattern_payload = lambda: "abc"
    missing_args_case.text_model = "str"
    missing_args_case.flags = 0

    unsupported_helper_case = _fake_workload(
        workload_id="unused-split",
        operation="module_call",
        use_compiled_pattern=True,
    )
    unsupported_helper_case.helper = "split"
    unsupported_helper_case.args = ("zzabczz",)
    unsupported_helper_case.pattern = "abc"
    unsupported_helper_case.pattern_payload = lambda: "abc"
    unsupported_helper_case.text_model = "str"
    unsupported_helper_case.flags = 0

    assert _module_workflow_compiled_pattern_correctness_case_signature(
        matching_case
    ) == ("module.search", "abc", ("zzabczz",), True, 0, "str")
    assert _module_workflow_compiled_pattern_correctness_case_signature(
        missing_args_case
    ) is None
    assert _module_workflow_compiled_pattern_correctness_case_signature(
        unsupported_helper_case
    ) is None


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in _compiled_pattern_wrong_text_model_specs()
    ),
)
def test_compiled_pattern_wrong_text_model_source_workloads_stay_exact_and_in_order(
    spec: dict[str, object],
) -> None:
    workloads = _compiled_pattern_wrong_text_model_source_workloads(spec)

    assert tuple(workload.workload_id for workload in workloads) == tuple(
        spec["expected_source_workload_ids"]
    )


@pytest.mark.parametrize(
    ("spec", "workload"),
    tuple(
        pytest.param(spec, workload, id=f"{spec['case_id']}-{workload.workload_id}")
        for spec in _compiled_pattern_wrong_text_model_specs()
        for workload in _compiled_pattern_wrong_text_model_source_workloads(spec)
    ),
)
def test_compiled_pattern_wrong_text_model_helpers_preserve_callback_and_runtime_contract(
    spec: dict[str, object],
    workload: Workload,
) -> None:
    expected_callback_result, expected_callback_call, _, _ = (
        _compiled_pattern_module_helper_route(
            workload,
            collection_replacement_callback_flags=0,
        )
    )

    assert compiled_pattern_contract_expected_build_calls(
        workload,
        label="wrong-text-model",
    ) == (
        [("compile", workload.pattern_payload(), workload.flags)]
        if workload.cache_mode == "warm"
        else [("compile", workload.pattern_payload(), workload.flags), ("purge",)]
    )
    assert expected_callback_call == _compiled_pattern_module_helper_route(
        workload,
        collection_replacement_callback_flags=0,
    )[1]
    assert expected_callback_result == _compiled_pattern_module_helper_route(
        workload,
        collection_replacement_callback_flags=0,
    )[0]

    with pytest.raises(TypeError) as observed_error:
        _run_cpython_compiled_pattern_module_helper_workload(
            workload,
            collection_replacement_callback_flags=0,
        )

    assert str(observed_error.value) == str(
        workload.expected_exception["message_substring"]
    )


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in _compiled_pattern_wrong_text_model_specs()
    ),
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_wrong_text_model_rows_until_helper_invocation(
    spec: dict[str, object],
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = _compiled_pattern_wrong_text_model_source_workloads(spec)
    contract_spec = _compiled_pattern_wrong_text_model_contract_spec(spec)
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=contract_spec,
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        str(spec["contract_filename"]),
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = tuple(load_manifest(manifest_path).workloads)

    assert tuple(workload.workload_id for workload in source_workloads) == tuple(
        spec["expected_source_workload_ids"]
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract" for workload_id in spec["expected_source_workload_ids"]
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [True] * len(
        source_workloads
    )
    assert [workload.timing_scope for workload in workloads] == [
        "module-helper-call"
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
            _run_cpython_compiled_pattern_module_helper_workload(
                workload,
                collection_replacement_callback_flags=0,
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
    ("spec", "source_workload"),
    tuple(
        pytest.param(spec, workload, id=f"{spec['case_id']}-{workload.workload_id}")
        for spec in _compiled_pattern_wrong_text_model_specs()
        for workload in _compiled_pattern_wrong_text_model_source_workloads(spec)
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads(
    spec: dict[str, object],
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=_compiled_pattern_wrong_text_model_contract_spec(spec),
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
    ("spec", "source_workload"),
    tuple(
        pytest.param(spec, workload, id=f"{spec['case_id']}-{workload.workload_id}")
        for spec in _compiled_pattern_wrong_text_model_specs()
        for workload in _compiled_pattern_wrong_text_model_source_workloads(spec)
    ),
)
def test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract(
    spec: dict[str, object],
    source_workload: Workload,
) -> None:
    expected_build_calls = compiled_pattern_contract_expected_build_calls(
        source_workload,
        label="wrong-text-model",
    )
    expected_callback_result, expected_callback_call, _, _ = (
        _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=0,
        )
    )
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=_compiled_pattern_wrong_text_model_contract_spec(spec),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == expected_callback_result

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]
