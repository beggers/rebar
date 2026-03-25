from __future__ import annotations

import json
import pathlib
import re

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
    compiled_pattern_module_compile_benchmark_support as support,
)
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkModule,
)
from tests.benchmarks.benchmark_test_support import (
    assert_benchmark_workload_contract,
    assert_zero_gap_manifest_workloads_measured,
    _expected_exception_instance,
    _record_numeric_materialization_fields,
    selected_manifest_workloads,
    _write_test_manifest,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    anchored_workload_case_ids,
    assert_benchmark_workload_matches_expected_result,
    expected_anchored_workload_case_pairs,
    run_benchmark_workload_with_cpython,
    unanchored_workload_ids,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)

def test_compiled_pattern_module_compile_success_payload_round_trip_on_live_workload() -> None:
    contract_case = next(
        case
        for case in support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "success"
    )
    source_workload = contract_case.source_workloads()[0]
    workload = _source_tree_contract_workload(
        source_workload,
        spec=contract_case.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_case.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert round_tripped.pattern_payload() == source_workload.pattern_payload()


def test_compiled_pattern_module_compile_keyword_payload_round_trip_preserves_keyword_type() -> None:
    contract_case = next(
        case
        for case in support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "bool-false"
    )
    source_workload = contract_case.source_workloads()[0]
    workload = _source_tree_contract_workload(
        source_workload,
        spec=contract_case.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_case.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert (
        support._compiled_pattern_module_compile_keyword_kwargs_signature(
            source_workload.kwargs
        )
        == contract_case.keyword_signature
    )
    assert type(payload["kwargs"]["flags"]) is bool
    assert type(round_tripped.kwargs["flags"]) is bool


def test_compiled_pattern_module_compile_cpython_dispatch_covers_success_and_keyword_lanes() -> None:
    success_case = next(
        case
        for case in support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "success"
    )
    success_source_workload = success_case.source_workloads()[0]
    success_workload = _source_tree_contract_workload(
        success_source_workload,
        spec=success_case.contract_builder_spec(),
    )

    keyword_case = next(
        case
        for case in support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "bool-false"
    )
    keyword_source_workload = keyword_case.source_workloads()[0]
    keyword_workload = _source_tree_contract_workload(
        keyword_source_workload,
        spec=keyword_case.contract_builder_spec(),
    )

    success_result = success_case.run_cpython_workload(success_workload)
    keyword_result = keyword_case.run_cpython_workload(keyword_workload)

    assert success_result.pattern == success_workload.pattern_payload()
    assert success_case.callback_flags(success_source_workload) == success_source_workload.flags
    assert keyword_result.pattern == keyword_workload.pattern_payload()
    assert keyword_case.callback_flags(keyword_source_workload) is False


def test_compiled_pattern_module_compile_anchor_and_case_metadata_stay_pinned_to_live_rows() -> None:
    contract_cases = support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
    anchor_lanes = support._COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES

    success_case = next(case for case in contract_cases if case.case_id == "success")
    bool_false_case = next(case for case in contract_cases if case.case_id == "bool-false")
    success_anchor_lane = next(
        lane for lane in anchor_lanes if lane.case_id == success_case.case_id
    )
    bool_false_anchor_lane = next(
        lane for lane in anchor_lanes if lane.case_id == bool_false_case.case_id
    )

    assert success_case.expected_source_workload_ids() == (
        "module-compile-literal-warm-str-compiled-pattern",
        "module-compile-literal-purged-bytes-compiled-pattern",
        "module-compile-named-group-warm-str-compiled-pattern",
        "module-compile-named-group-purged-bytes-compiled-pattern",
    )
    assert success_anchor_lane.expected_anchor_pairs == (
        (
            "module-compile-literal-warm-str-compiled-pattern-contract",
            "workflow-module-compile-str-compiled-pattern",
        ),
        (
            "module-compile-literal-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-bytes-compiled-pattern",
        ),
        (
            "module-compile-named-group-warm-str-compiled-pattern-contract",
            "workflow-module-compile-str-compiled-pattern-named-group",
        ),
        (
            "module-compile-named-group-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-bytes-compiled-pattern-named-group",
        ),
    )
    assert tuple(
        workload.workload_id for workload in bool_false_anchor_lane.source_workloads
    ) == (
        "module-compile-flags-bool-false-warm-str-compiled-pattern",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
    )
    assert bool_false_anchor_lane.expected_anchor_pairs == (
        (
            "module-compile-flags-bool-false-warm-str-compiled-pattern-contract",
            "workflow-module-compile-flags-bool-false-str-compiled-pattern",
        ),
        (
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
        ),
    )


def test_module_boundary_manifest_keeps_compiled_pattern_module_compile_literal_rows_measured() -> None:
    owner_spec = support._COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS[0]
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            support.MODULE_BOUNDARY_MANIFEST_PATH,
            include_workload=owner_spec.includes_workload,
        )
    )
    manifest_workload_count = len(
        selected_manifest_workloads(support.MODULE_BOUNDARY_MANIFEST_PATH)
    )

    assert expected_measured_workload_ids == owner_spec.expected_anchor_workload_ids()
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=support.MODULE_BOUNDARY_MANIFEST_PATH,
        manifest_id="module-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_module_boundary_manifest_keeps_compiled_pattern_module_compile_named_group_rows_measured() -> None:
    owner_spec = support._COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS[1]
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            support.MODULE_BOUNDARY_MANIFEST_PATH,
            include_workload=owner_spec.includes_workload,
        )
    )
    manifest_workload_count = len(
        selected_manifest_workloads(support.MODULE_BOUNDARY_MANIFEST_PATH)
    )

    assert expected_measured_workload_ids == owner_spec.expected_anchor_workload_ids()
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=support.MODULE_BOUNDARY_MANIFEST_PATH,
        manifest_id="module-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured() -> None:
    manifest_workload_count = len(
        selected_manifest_workloads(support.MODULE_BOUNDARY_MANIFEST_PATH)
    )

    for owner_spec in support._COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS:
        expected_measured_workload_ids = tuple(
            workload.workload_id
            for workload in selected_manifest_workloads(
                support.MODULE_BOUNDARY_MANIFEST_PATH,
                include_workload=owner_spec.includes_workload,
            )
        )

        assert expected_measured_workload_ids == owner_spec.expected_anchor_workload_ids()
        assert_zero_gap_manifest_workloads_measured(
            manifest_path=support.MODULE_BOUNDARY_MANIFEST_PATH,
            manifest_id="module-boundary",
            expected_measured_workload_ids=expected_measured_workload_ids,
            expected_measured_workload_count=manifest_workload_count,
            expected_total_workload_count=manifest_workload_count,
        )


def test_compiled_pattern_module_compile_standard_definition_export_is_lazy_cached_and_owner_built(
) -> None:
    expected_definitions = tuple(
        owner_spec.anchor_definition()
        for owner_spec in (
            *support._COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
            *support._COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
        )
    )

    assert (
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
        not in vars(support)
    )

    first_export = getattr(
        support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )
    second_export = getattr(
        support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )

    assert first_export is second_export
    assert first_export is support._build_compiled_pattern_module_compile_standard_benchmark_definitions()
    assert first_export == expected_definitions
    assert first_export is not expected_definitions
    assert tuple(definition.name for definition in first_export) == (
        "module-workflow-compiled-pattern-module-compile-literal-success",
        "module-workflow-compiled-pattern-module-compile-named-group-success",
        "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword",
        "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword-named-group",
        "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword",
        "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword-named-group",
        "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection",
        "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
    )
    assert (
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
        not in vars(support)
    )


def test_compiled_pattern_module_compile_source_avoids_local_constructor_wrapper() -> None:
    import inspect

    support_source = inspect.getsource(support)

    assert "def _standard_benchmark_anchor_contract_definition" not in support_source
    assert "StandardBenchmarkAnchorContractDefinition(" in support_source


@pytest.mark.parametrize(
    "contract_case",
    support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
    ids=lambda contract_case: contract_case.case_id,
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
    contract_case: support.CompiledPatternModuleCompileContractCase,
) -> None:
    source_workloads = contract_case.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=contract_case.contract_builder_spec(),
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        contract_case.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == tuple(
        contract_case.expected_source_workload_ids()
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        workload_id for workload_id, _case_id in contract_case.expected_anchor_pairs
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        contract_case.assert_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        if source_workload.expected_exception is None:
            assert_benchmark_workload_matches_expected_result(
                round_tripped,
                contract_case.run_cpython_workload(workload),
            )
            continue

        expected_exception = _expected_exception_instance(
            source_workload.expected_exception
        )
        with pytest.raises(
            type(expected_exception),
            match=source_workload.expected_exception["message_substring"],
        ) as expected_error:
            contract_case.run_cpython_workload(workload)
        with pytest.raises(type(expected_error.value)) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)
        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "anchor_lane",
    support._COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES,
    ids=lambda anchor_lane: anchor_lane.case_id,
)
def test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases(
    tmp_path: pathlib.Path,
    anchor_lane: support._CompiledPatternModuleContractAnchorLane,
) -> None:
    manifest = _source_tree_contract_manifest(
        anchor_lane.source_workloads,
        spec=anchor_lane.contract_builder_spec(),
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        anchor_lane.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    expected_anchor_case_ids = anchor_lane.expected_anchor_case_ids(manifest_path)
    anchor_case_ids = anchor_lane.anchor_case_ids

    assert anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=anchor_lane.workload_signature,
        include_workload=anchor_lane.include_workload,
    ) == expected_anchor_case_ids
    assert unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=anchor_lane.workload_signature,
        include_workload=anchor_lane.include_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in expected_anchored_workload_case_pairs(
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
            include_workload=anchor_lane.include_workload,
        )
    ) == anchor_lane.expected_anchor_pairs


@pytest.mark.parametrize(
    ("case_group", "source_workload"),
    tuple(
        pytest.param(case_group, source_workload, id=source_workload.workload_id)
        for case_group in (
            owner_spec.contract_case()
            for owner_spec in support._COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS
        )
        for source_workload in case_group.source_workloads()
    ),
)
def test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time(
    monkeypatch: pytest.MonkeyPatch,
    case_group: support.CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=case_group.contract_builder_spec(),
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        if source_workload.expected_exception is None:
            observed_result = callback()
            assert observed_result.pattern == workload.pattern_payload()
        else:
            expected_exception = _expected_exception_instance(
                source_workload.expected_exception
            )
            with pytest.raises(
                type(expected_exception),
                match=source_workload.expected_exception["message_substring"],
            ):
                callback()

        assert observed_field_names == ["kwargs.flags"]
    finally:
        re.purge()


@pytest.mark.parametrize(
    ("contract_case", "source_workload"),
    support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads(
    contract_case: support.CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=contract_case.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_case.assert_payload_round_trip(
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
    ("contract_case", "source_workload"),
    support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing(
    contract_case: support.CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> None:
    expected_build_calls = contract_case.expected_build_calls(source_workload)
    compile_exception = (
        None
        if source_workload.expected_exception is None
        else _expected_exception_instance(source_workload.expected_exception)
    )
    module = RecordingBenchmarkModule(compile_exception=compile_exception)
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=contract_case.contract_builder_spec(),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1

    compiled_pattern = module.compiled_patterns[0]
    if source_workload.expected_exception is None:
        assert callback() is compiled_pattern
    else:
        with pytest.raises(
            type(compile_exception),
            match=source_workload.expected_exception["message_substring"],
        ):
            callback()

    last_call = module.calls[-1]
    assert last_call[0] == "compile"
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == (contract_case.callback_flags(source_workload),)
