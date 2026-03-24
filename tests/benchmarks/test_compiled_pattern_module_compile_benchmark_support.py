from __future__ import annotations

from functools import partial

from rebar_harness.benchmarks import (
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import (
    compiled_pattern_module_compile_benchmark_support as support,
)
from tests.benchmarks import (
    test_source_tree_combined_boundary_benchmarks as combined,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _source_tree_contract_workload,
)


def _contract_cases():
    return support.build_compiled_pattern_module_compile_contract_cases(
        manifest_path=combined.MODULE_BOUNDARY_MANIFEST_PATH,
        expected_build_calls_builder=partial(
            combined._compiled_pattern_contract_expected_build_calls,
            label="module.compile contract",
        ),
        success_owner_specs=combined._COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
        keyword_owner_specs=combined._COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    )


def _contract_case(case_id: str):
    return next(case for case in _contract_cases() if case.case_id == case_id)


def test_compiled_pattern_module_compile_success_payload_round_trip_on_live_workload() -> None:
    contract_case = _contract_case("success")
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
    contract_case = _contract_case("bool-false")
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
    success_case = _contract_case("success")
    success_source_workload = success_case.source_workloads()[0]
    success_workload = _source_tree_contract_workload(
        success_source_workload,
        spec=success_case.contract_builder_spec(),
    )

    keyword_case = _contract_case("bool-false")
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
    contract_cases = _contract_cases()
    anchor_lanes = support.build_compiled_pattern_module_contract_anchor_lanes(
        success_anchor_specs=combined._COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS,
        contract_cases=contract_cases,
        published_case_ids_by_signature=combined.published_case_ids_by_signature,
    )

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
