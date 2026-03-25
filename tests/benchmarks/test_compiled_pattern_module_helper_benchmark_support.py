from __future__ import annotations

import json
import pathlib

import pytest

from rebar_harness.benchmarks import (
    Workload,
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    RecordingBenchmarkModule,
    STANDARD_BENCHMARK_DEFINITIONS,
    _compiled_pattern_module_helper_route,
    _run_cpython_compiled_pattern_module_helper_workload,
    _write_test_manifest,
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks import (
    compiled_pattern_module_helper_benchmark_support as compiled_pattern_module_helper_support,
)
from tests.benchmarks.benchmark_test_support import (
    compiled_pattern_contract_expected_build_calls,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)


def test_compiled_pattern_wrong_text_model_owner_spec_surface_is_owner_module_owned_without_local_duplicates(
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
        compiled_pattern_module_helper_support._COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        is support._COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        is support._COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs
        is support._compiled_pattern_wrong_text_model_specs
    )
    assert (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads
        is support._compiled_pattern_wrong_text_model_source_workloads
    )
    assert (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec
        is support._compiled_pattern_wrong_text_model_contract_spec
    )
    assert (
        compiled_pattern_module_helper_support._assert_wrong_text_model_payload_round_trip
        is support._assert_wrong_text_model_payload_round_trip
    )
    assert {
        "_compiled_pattern_wrong_text_model_specs",
        "_compiled_pattern_wrong_text_model_source_workloads",
        "_compiled_pattern_wrong_text_model_contract_spec",
        "_assert_wrong_text_model_payload_round_trip",
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
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
    ),
)
def test_compiled_pattern_wrong_text_model_source_workloads_stay_exact_and_in_order(
    spec: dict[str, object],
) -> None:
    workloads = (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    )

    assert tuple(workload.workload_id for workload in workloads) == tuple(
        spec["expected_source_workload_ids"]
    )


@pytest.mark.parametrize(
    ("spec", "workload"),
    tuple(
        pytest.param(spec, workload, id=f"{spec['case_id']}-{workload.workload_id}")
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
        for workload in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
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
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
    ),
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_wrong_text_model_rows_until_helper_invocation(
    spec: dict[str, object],
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    )
    contract_spec = (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
            spec
        )
    )
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

        compiled_pattern_module_helper_support._assert_wrong_text_model_payload_round_trip(
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
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
        for workload in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
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
        spec=compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
            spec
        ),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    compiled_pattern_module_helper_support._assert_wrong_text_model_payload_round_trip(
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
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
        for workload in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
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
            spec=compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
                spec
            ),
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
