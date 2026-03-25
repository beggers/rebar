from __future__ import annotations

import json
import importlib
import pathlib
from types import SimpleNamespace

import pytest

from rebar_harness.benchmarks import (
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    RecordingBenchmarkModule,
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
    _write_test_manifest,
    assert_benchmark_workload_matches_expected_result,
    run_benchmark_workload_with_cpython,
    selected_manifest_workloads,
    top_level_module_definition_and_assignment_names,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _is_collection_replacement_compiled_pattern_success_workload,
)
from tests.benchmarks.compiled_pattern_module_success_benchmark_support import (
    CompiledPatternModuleSuccessOwnerSpec,
    _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS,
    _COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
    _assert_compiled_pattern_module_success_payload_round_trip,
    _assert_compiled_pattern_success_rows_measured_in_combined_manifest,
    include_live_compiled_pattern_module_success_workload,
    live_compiled_pattern_module_success_surface_ids,
)


def test_compiled_pattern_module_success_suite_imports_owner_surface_from_support() -> None:
    import sys

    local_definition_names, _ = (
        top_level_module_definition_and_assignment_names(sys.modules[__name__])
    )
    support_module = importlib.import_module(
        "tests.benchmarks.compiled_pattern_module_success_benchmark_support"
    )
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support_module)
    )

    assert not {
        "CompiledPatternModuleSuccessOwnerSpec",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
    } & local_definition_names
    assert {
        "CompiledPatternModuleSuccessOwnerSpec",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
        "include_live_compiled_pattern_module_success_workload",
        "live_compiled_pattern_module_success_surface_ids",
    }.issubset(support_definition_names | support_assignment_names)
    assert CompiledPatternModuleSuccessOwnerSpec.contract_builder_spec.__name__ == (
        "contract_builder_spec"
    )
    assert CompiledPatternModuleSuccessOwnerSpec.source_workloads.__name__ == (
        "source_workloads"
    )
    assert CompiledPatternModuleSuccessOwnerSpec.expected_build_calls.__name__ == (
        "expected_build_calls"
    )
    assert CompiledPatternModuleSuccessOwnerSpec.expected_callback_result.__name__ == (
        "expected_callback_result"
    )
    assert CompiledPatternModuleSuccessOwnerSpec.expected_callback_call.__name__ == (
        "expected_callback_call"
    )


def test_compiled_pattern_module_success_owner_specs_match_live_nonkeyword_noncompile_success_surface_without_overlap(
) -> None:
    owner_surface_ids = tuple(
        source_workload.workload_id
        for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        for source_workload in owner_spec.source_workloads()
    )
    expected_live_surface_ids = tuple(
        workload.workload_id
        for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        for workload in selected_manifest_workloads(
            owner_spec.manifest_path,
            include_workload=include_live_compiled_pattern_module_success_workload,
        )
    )

    assert tuple(sorted(owner_surface_ids)) == tuple(sorted(expected_live_surface_ids))
    assert expected_live_surface_ids == live_compiled_pattern_module_success_surface_ids()
    assert len(owner_surface_ids) == len(set(owner_surface_ids))


def _compiled_pattern_module_success_selector_candidate(
    **overrides,
) -> SimpleNamespace:
    payload = {
        "operation": "module.search",
        "use_compiled_pattern": False,
        "expected_exception": None,
        "haystack_text_model": None,
        "kwargs": {},
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


@pytest.mark.parametrize(
    ("workload", "expected"),
    (
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                use_compiled_pattern=True,
            ),
            True,
            id="module-boundary-direct-success",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.sub",
                use_compiled_pattern=True,
            ),
            True,
            id="collection-replacement-direct-success",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(),
            False,
            id="rejects-non-compiled-pattern-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                expected_exception={
                    "type": "TypeError",
                    "message_substring": "synthetic selector rejection",
                },
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-exception-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.fullmatch",
                use_compiled_pattern=True,
                haystack_text_model="bytes",
            ),
            False,
            id="rejects-wrong-text-model-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.split",
                kwargs={"maxsplit": 1},
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-keyword-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.compile",
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-compile-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="pattern.search",
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-non-module-operation",
        ),
    ),
)
def test_include_live_compiled_pattern_module_success_workload_accepts_only_direct_success_rows(
    workload,
    expected: bool,
) -> None:
    assert include_live_compiled_pattern_module_success_workload(workload) is expected


@pytest.mark.parametrize(
    "owner_spec",
    _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS,
    ids=lambda owner_spec: owner_spec.case_id,
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
) -> None:
    source_workloads = owner_spec.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=owner_spec.contract_builder_spec(),
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        owner_spec.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        owner_spec.expected_source_workload_ids
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_success_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
            owner_spec=owner_spec,
        )
        assert_benchmark_workload_matches_expected_result(
            round_tripped,
            run_benchmark_workload_with_cpython(round_tripped),
        )


def test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured(
) -> None:
    _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
        include_workload=_is_collection_replacement_compiled_pattern_success_workload,
    )


def test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured(
) -> None:
    _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
        include_workload=_is_module_workflow_compiled_pattern_literal_success_workload,
    )


def test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured(
) -> None:
    _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
        include_workload=(
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload
        ),
    )


def test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured(
) -> None:
    _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
        include_workload=_is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
    )


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    _COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads(
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
    source_workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=owner_spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    _assert_compiled_pattern_module_success_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
        owner_spec=owner_spec,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    _COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing(
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
    source_workload,
) -> None:
    expected_build_calls = owner_spec.expected_build_calls(source_workload)
    expected_callback_call = owner_spec.expected_callback_call(source_workload)
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=owner_spec.contract_builder_spec(),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == owner_spec.expected_callback_result(source_workload)

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]
