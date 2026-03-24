from __future__ import annotations

import json
import pathlib

import pytest

from rebar_harness.benchmarks import (
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import (
    compiled_pattern_module_success_benchmark_support as support,
)
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkModule,
)
from tests.benchmarks.benchmark_test_support import _write_test_manifest
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    assert_benchmark_workload_matches_expected_result,
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)


@pytest.mark.parametrize(
    "owner_spec",
    support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS,
    ids=lambda owner_spec: owner_spec.case_id,
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
    owner_spec: support.CompiledPatternModuleSuccessOwnerSpec,
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

        support._assert_compiled_pattern_module_success_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
            owner_spec=owner_spec,
        )
        assert_benchmark_workload_matches_expected_result(
            round_tripped,
            run_benchmark_workload_with_cpython(round_tripped),
        )


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    support._COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads(
    owner_spec: support.CompiledPatternModuleSuccessOwnerSpec,
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

    support._assert_compiled_pattern_module_success_payload_round_trip(
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
    support._COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing(
    owner_spec: support.CompiledPatternModuleSuccessOwnerSpec,
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
