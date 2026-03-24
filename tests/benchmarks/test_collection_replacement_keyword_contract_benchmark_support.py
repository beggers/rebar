from __future__ import annotations

from rebar_harness.benchmarks import workload_to_payload
from tests.benchmarks import (
    collection_replacement_keyword_contract_benchmark_support as support,
)


def test_pattern_helper_collection_replacement_keyword_error_workload_builder_shape() -> None:
    workload = support._pattern_helper_collection_replacement_keyword_error_workload(
        operation="pattern.subn",
        haystack="abc",
        kwargs_payload={"count_alias": 1},
        replacement="x",
        count=0,
        maxsplit=0,
        expected_exception={
            "type": "TypeError",
            "message_substring": "'count_alias' is an invalid keyword argument for subn()",
        },
        text_model="bytes",
    )
    payload = workload_to_payload(workload)

    assert payload["manifest_id"] == (
        "python-benchmark-pattern-collection-replacement-keyword-contract"
    )
    assert payload["timing_scope"] == "pattern-helper-call"
    assert payload["expected_exception"] == {
        "type": "TypeError",
        "message_substring": "'count_alias' is an invalid keyword argument for subn()",
    }
    assert payload["kwargs"] == {"count_alias": 1}
    assert payload["text_model"] == "bytes"


def test_pattern_helper_keyword_error_selector_stays_in_scope() -> None:
    workload = next(
        workload
        for workload in support._PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        if workload.workload_id == "pattern-sub-unexpected-keyword-warm-str"
    )

    assert support._is_collection_replacement_pattern_helper_keyword_error_workload(
        workload
    )


def test_module_helper_collection_replacement_keyword_error_selector_stays_in_scope() -> None:
    workload = next(
        workload
        for workload in support._MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        if workload.workload_id == "module-sub-count-alias-keyword-purged-str"
    )

    assert support._is_collection_replacement_module_helper_keyword_error_workload(
        workload
    )


def test_keyword_error_workload_probe_helper_measures_real_source_workload() -> None:
    support._assert_keyword_error_workload_probe_measured(
        next(iter(support._PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS)),
        import_name="re",
        adapter_name="cpython.re",
    )
