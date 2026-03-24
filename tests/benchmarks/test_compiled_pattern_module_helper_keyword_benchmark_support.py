from __future__ import annotations

import pytest

from rebar_harness.benchmarks import (
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import (
    compiled_pattern_module_helper_keyword_benchmark_support as support,
)
from tests.benchmarks import (
    test_source_tree_combined_boundary_benchmarks as combined,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _source_tree_contract_workload,
)


def _contract_surface(case_id: str):
    return next(
        surface
        for surface in support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        if surface.case_id == case_id
    )


def test_compiled_pattern_module_helper_keyword_source_workload_order_stays_pinned() -> None:
    success_surface = _contract_surface("success")
    keyword_error_surface = _contract_surface("keyword-error")

    assert tuple(
        workload.workload_id for workload in success_surface.source_workloads()
    ) == support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids
    assert tuple(
        workload.workload_id for workload in keyword_error_surface.source_workloads()
    ) == support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids


def test_compiled_pattern_module_helper_keyword_success_payload_round_trip_preserves_bool_type() -> None:
    success_surface = _contract_surface("success")
    source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-sub-count-bool-false-keyword-warm-str-compiled-pattern"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    success_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert type(payload["kwargs"]["count"]) is bool
    assert type(round_tripped.kwargs["count"]) is bool


def test_compiled_pattern_module_helper_keyword_error_payload_round_trip_preserves_expected_exception() -> None:
    keyword_error_surface = _contract_surface("keyword-error")
    source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    keyword_error_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception


def test_compiled_pattern_module_helper_keyword_expected_materialized_field_names_cover_split_and_sub() -> None:
    success_surface = _contract_surface("success")
    keyword_error_surface = _contract_surface("keyword-error")

    split_duplicate_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern"
    )
    sub_keyword_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-sub-count-keyword-warm-str-compiled-pattern"
    )

    assert keyword_error_surface.spec.expected_materialized_field_names(
        split_duplicate_workload
    ) == ("maxsplit", "kwargs.maxsplit")
    assert success_surface.spec.expected_materialized_field_names(
        sub_keyword_workload
    ) == ("kwargs.count",)


def test_compiled_pattern_module_helper_keyword_precompile_anchor_order_stays_pinned() -> None:
    assert tuple(
        workload.workload_id
        for workload in support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
    ) == support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids


def test_compiled_pattern_module_helper_keyword_cpython_outcomes_cover_success_and_error_lanes() -> None:
    success_surface = _contract_surface("success")
    success_source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-subn-count-keyword-purged-bytes-compiled-pattern"
    )
    success_workload = _source_tree_contract_workload(
        success_source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    success_payload = workload_to_payload(success_workload)
    success_round_tripped = workload_from_payload(success_payload)

    success_surface.assert_outcome(
        success_source_workload,
        success_workload,
        success_round_tripped,
    )
    assert success_surface.run_cpython_helper_workload(success_workload) == (
        b"xabc",
        1,
    )

    keyword_error_surface = _contract_surface("keyword-error")
    keyword_error_source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id == "module-subn-count-alias-keyword-purged-bytes-compiled-pattern"
    )
    keyword_error_workload = _source_tree_contract_workload(
        keyword_error_source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    keyword_error_payload = workload_to_payload(keyword_error_workload)
    keyword_error_round_tripped = workload_from_payload(keyword_error_payload)

    keyword_error_surface.assert_outcome(
        keyword_error_source_workload,
        keyword_error_workload,
        keyword_error_round_tripped,
    )
    with pytest.raises(TypeError):
        combined.run_benchmark_workload_with_cpython(keyword_error_round_tripped)
