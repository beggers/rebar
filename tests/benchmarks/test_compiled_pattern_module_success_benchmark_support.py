from __future__ import annotations

from collections.abc import Callable
import json
import pathlib
import unittest

import pytest

from rebar_harness.benchmarks import (
    Workload,
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _is_collection_replacement_compiled_pattern_success_workload,
)
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
)
from tests.benchmarks.compiled_pattern_module_success_benchmark_support import (
    CompiledPatternModuleSuccessOwnerSpec,
    _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS,
)
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkModule,
)
from tests.benchmarks.benchmark_test_support import _write_test_manifest
from tests.benchmarks.benchmark_test_support import (
    assert_benchmark_workload_contract,
    find_workload_document,
    find_workload_record,
    manifest_workload_ids_matching,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    assert_benchmark_workload_matches_expected_result,
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)
from tests.conftest import run_harness_scorecard


def _assert_compiled_pattern_module_success_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
    *,
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_text_type)
    for field_name in owner_spec.preserved_payload_fields:
        assert payload[field_name] == getattr(source_workload, field_name)
        assert getattr(round_tripped, field_name) == getattr(
            source_workload,
            field_name,
        )
    if (
        owner_spec.preserve_replacement_payload_typing
        and source_workload.replacement is not None
    ):
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def test_compiled_pattern_module_success_owner_specs_are_support_owned_without_local_duplicates(
) -> None:
    import ast
    import inspect
    import sys

    from tests.benchmarks import (
        compiled_pattern_module_success_benchmark_support as support,
    )

    test_source = inspect.getsource(sys.modules[__name__])
    module_tree = ast.parse(test_source)
    local_definition_names = {
        node.name
        for node in module_tree.body
        if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef))
    }
    local_assignment_names = {
        node.target.id
        for node in module_tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    local_assignment_names.update(
        target.id
        for node in module_tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    )

    assert (
        CompiledPatternModuleSuccessOwnerSpec
        is support.CompiledPatternModuleSuccessOwnerSpec
    )
    assert (
        _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC
        is support._COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC
    )
    assert (
        _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC
        is support._COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC
    )
    assert (
        _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        is support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
    )
    assert {
        "CompiledPatternModuleSuccessOwnerSpec",
        "contract_builder_spec",
        "source_workloads",
        "expected_build_calls",
        "expected_callback_result",
        "expected_callback_call",
    }.isdisjoint(local_definition_names)
    assert {
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
    }.isdisjoint(local_assignment_names)


_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        owner_spec,
        source_workload,
        id=f"{owner_spec.case_id}-{source_workload.workload_id}",
    )
    for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
    for source_workload in owner_spec.source_workloads()
)


def _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
    *,
    include_workload: Callable[[Any], bool],
) -> None:
    testcase = unittest.TestCase()
    manifest = load_manifest(owner_spec.manifest_path)
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in owner_spec.source_workloads()
        if include_workload(workload)
    )
    selected_measured_workload_ids = manifest_workload_ids_matching(
        manifest,
        include_workload,
    )

    assert selected_measured_workload_ids == expected_measured_workload_ids

    _, scorecard = run_harness_scorecard(
        "rebar_harness.benchmarks",
        ["--manifest", str(owner_spec.manifest_path)],
        report_name="benchmarks.json",
    )
    manifest_summary = scorecard["manifests"][owner_spec.contract_manifest_id]
    expected_workload_count = len(manifest.workloads)

    assert manifest_summary["known_gap_count"] == 0
    assert manifest_summary["measured_workloads"] == expected_workload_count
    assert manifest_summary["workload_count"] == expected_workload_count

    for workload_id in expected_measured_workload_ids:
        assert_benchmark_workload_contract(
            testcase,
            find_workload_record(scorecard, workload_id),
            manifest_id=owner_spec.contract_manifest_id,
            workload_document=find_workload_document(
                manifest,
                workload_id,
            ),
            expected_status="measured",
        )


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
