from __future__ import annotations

import pathlib
import re

import pytest

from rebar_harness.benchmarks import (
    Workload,
    build_callable,
    load_manifest,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    _record_numeric_materialization_fields,
    _write_test_manifest,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _collection_replacement_pattern_split_workload_signature,
    _collection_replacement_positional_keyword_field,
)
from tests.benchmarks.module_pattern_keyword_benchmark_anchor_support import (
    _is_module_workflow_keyword_error_workload,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks import (
    collection_replacement_keyword_contract_benchmark_support as support,
)
from tests.conftest import records_by_string_id


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


def test_standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "pattern-split-maxsplit-keyword-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "zabczabc",
                "kwargs": {
                    "maxsplit": 1,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split maxsplit= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-split-maxsplit-bool-keyword-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "maxsplit": True,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split maxsplit= bool keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-split-duplicate-maxsplit-keyword-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "abcabc",
                "maxsplit": 1,
                "kwargs": {
                    "maxsplit": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "split() takes at most 2 arguments (3 given)",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split duplicate maxsplit= carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-split-unexpected-keyword-contract-bytes",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'missing' is an invalid keyword argument for split()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-count-keyword-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-count-bool-keyword-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": False,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub count= bool keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-unexpected-keyword-contract-str",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'missing' is an invalid keyword argument for sub()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-unexpected-keyword-after-positional-count-contract-str",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "count": 1,
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "sub() takes at most 3 arguments (4 given)",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub positional count plus unexpected keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-count-alias-keyword-contract-str",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count_alias": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'count_alias' is an invalid keyword argument for sub()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub count_alias keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-count-keyword-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-count-bool-keyword-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": True,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn count= bool keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-unexpected-keyword-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "text_model": "bytes",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'missing' is an invalid keyword argument for subn()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-unexpected-keyword-after-positional-count-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "text_model": "bytes",
                "count": 1,
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "subn() takes at most 3 arguments (4 given)",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn positional count plus unexpected keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-count-alias-keyword-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count_alias": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "'count_alias' is an invalid keyword argument for subn()",
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn count_alias keyword carriers unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_collection_replacement_keyword_contract.py",
        manifest_source,
    )
    workloads_by_id = records_by_string_id(
        load_manifest(manifest_path).workloads,
        id_attr="workload_id",
    )
    split_workload = workloads_by_id["pattern-split-maxsplit-keyword-contract-str"]
    split_bool_workload = workloads_by_id[
        "pattern-split-maxsplit-bool-keyword-contract-str"
    ]
    split_duplicate_workload = workloads_by_id[
        "pattern-split-duplicate-maxsplit-keyword-contract-str"
    ]
    split_missing_workload = workloads_by_id[
        "pattern-split-unexpected-keyword-contract-bytes"
    ]
    sub_workload = workloads_by_id["pattern-sub-count-keyword-contract-bytes"]
    sub_bool_workload = workloads_by_id["pattern-sub-count-bool-keyword-contract-bytes"]
    sub_missing_workload = workloads_by_id["pattern-sub-unexpected-keyword-contract-str"]
    sub_missing_after_positional_count_workload = workloads_by_id[
        "pattern-sub-unexpected-keyword-after-positional-count-contract-str"
    ]
    sub_count_alias_workload = workloads_by_id[
        "pattern-sub-count-alias-keyword-contract-str"
    ]
    subn_workload = workloads_by_id["pattern-subn-count-keyword-contract-str"]
    subn_bool_workload = workloads_by_id["pattern-subn-count-bool-keyword-contract-str"]
    subn_missing_workload = workloads_by_id[
        "pattern-subn-unexpected-keyword-contract-bytes"
    ]
    subn_missing_after_positional_count_workload = workloads_by_id[
        "pattern-subn-unexpected-keyword-after-positional-count-contract-bytes"
    ]
    subn_count_alias_workload = workloads_by_id[
        "pattern-subn-count-alias-keyword-contract-bytes"
    ]

    assert split_workload.kwargs == {"maxsplit": 1}
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.kwargs == {"maxsplit": 1}
    assert round_tripped_split.keyword_arguments() == {"maxsplit": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_split) == ["z", "zabc"]

    assert split_bool_workload.kwargs == {"maxsplit": True}
    assert type(split_bool_workload.kwargs["maxsplit"]) is bool
    round_tripped_split_bool = workload_from_payload(
        workload_to_payload(split_bool_workload)
    )
    assert round_tripped_split_bool.kwargs == {"maxsplit": True}
    assert type(round_tripped_split_bool.kwargs["maxsplit"]) is bool
    materialized_split_bool_kwargs = round_tripped_split_bool.keyword_arguments()
    assert materialized_split_bool_kwargs == {"maxsplit": True}
    assert materialized_split_bool_kwargs["maxsplit"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_split_bool) == [
        "z",
        "abc",
    ]

    assert split_duplicate_workload.maxsplit == 1
    assert split_duplicate_workload.kwargs == {"maxsplit": 1}
    round_tripped_split_duplicate = workload_from_payload(
        workload_to_payload(split_duplicate_workload)
    )
    assert round_tripped_split_duplicate.maxsplit == 1
    assert round_tripped_split_duplicate.kwargs == {"maxsplit": 1}
    assert round_tripped_split_duplicate.keyword_arguments() == {"maxsplit": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("split() takes at most 2 arguments (3 given)"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_split_duplicate)

    assert split_missing_workload.kwargs == {"missing": 1}
    round_tripped_split_missing = workload_from_payload(
        workload_to_payload(split_missing_workload)
    )
    assert round_tripped_split_missing.kwargs == {"missing": 1}
    assert round_tripped_split_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'missing' is an invalid keyword argument for split()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_split_missing)

    assert sub_workload.kwargs == {"count": 1}
    round_tripped_sub = workload_from_payload(workload_to_payload(sub_workload))
    assert round_tripped_sub.kwargs == {"count": 1}
    assert round_tripped_sub.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_sub) == b"xabc"

    assert sub_bool_workload.kwargs == {"count": False}
    assert type(sub_bool_workload.kwargs["count"]) is bool
    round_tripped_sub_bool = workload_from_payload(
        workload_to_payload(sub_bool_workload)
    )
    assert round_tripped_sub_bool.kwargs == {"count": False}
    assert type(round_tripped_sub_bool.kwargs["count"]) is bool
    materialized_sub_bool_kwargs = round_tripped_sub_bool.keyword_arguments()
    assert materialized_sub_bool_kwargs == {"count": False}
    assert materialized_sub_bool_kwargs["count"] is False
    assert run_benchmark_workload_with_cpython(round_tripped_sub_bool) == b"xx"

    assert sub_missing_workload.kwargs == {"missing": 1}
    round_tripped_sub_missing = workload_from_payload(
        workload_to_payload(sub_missing_workload)
    )
    assert round_tripped_sub_missing.kwargs == {"missing": 1}
    assert round_tripped_sub_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'missing' is an invalid keyword argument for sub()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_sub_missing)

    assert sub_missing_after_positional_count_workload.count == 1
    assert sub_missing_after_positional_count_workload.kwargs == {"missing": 1}
    round_tripped_sub_missing_after_positional_count = workload_from_payload(
        workload_to_payload(sub_missing_after_positional_count_workload)
    )
    assert round_tripped_sub_missing_after_positional_count.count == 1
    assert round_tripped_sub_missing_after_positional_count.kwargs == {"missing": 1}
    assert (
        round_tripped_sub_missing_after_positional_count.keyword_arguments()
        == {"missing": 1}
    )
    with pytest.raises(
        TypeError,
        match=re.escape("sub() takes at most 3 arguments (4 given)"),
    ):
        run_benchmark_workload_with_cpython(
            round_tripped_sub_missing_after_positional_count
        )

    assert sub_count_alias_workload.kwargs == {"count_alias": 1}
    round_tripped_sub_count_alias = workload_from_payload(
        workload_to_payload(sub_count_alias_workload)
    )
    assert round_tripped_sub_count_alias.kwargs == {"count_alias": 1}
    assert round_tripped_sub_count_alias.keyword_arguments() == {"count_alias": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'count_alias' is an invalid keyword argument for sub()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_sub_count_alias)

    assert subn_workload.kwargs == {"count": 1}
    round_tripped_subn = workload_from_payload(workload_to_payload(subn_workload))
    assert round_tripped_subn.kwargs == {"count": 1}
    assert round_tripped_subn.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_subn) == ("xabc", 1)

    assert subn_bool_workload.kwargs == {"count": True}
    assert type(subn_bool_workload.kwargs["count"]) is bool
    round_tripped_subn_bool = workload_from_payload(
        workload_to_payload(subn_bool_workload)
    )
    assert round_tripped_subn_bool.kwargs == {"count": True}
    assert type(round_tripped_subn_bool.kwargs["count"]) is bool
    materialized_subn_bool_kwargs = round_tripped_subn_bool.keyword_arguments()
    assert materialized_subn_bool_kwargs == {"count": True}
    assert materialized_subn_bool_kwargs["count"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_subn_bool) == (
        "xabc",
        1,
    )

    assert subn_missing_workload.kwargs == {"missing": 1}
    round_tripped_subn_missing = workload_from_payload(
        workload_to_payload(subn_missing_workload)
    )
    assert round_tripped_subn_missing.kwargs == {"missing": 1}
    assert round_tripped_subn_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'missing' is an invalid keyword argument for subn()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_subn_missing)

    assert subn_missing_after_positional_count_workload.count == 1
    assert subn_missing_after_positional_count_workload.kwargs == {"missing": 1}
    round_tripped_subn_missing_after_positional_count = workload_from_payload(
        workload_to_payload(subn_missing_after_positional_count_workload)
    )
    assert round_tripped_subn_missing_after_positional_count.count == 1
    assert round_tripped_subn_missing_after_positional_count.kwargs == {"missing": 1}
    assert (
        round_tripped_subn_missing_after_positional_count.keyword_arguments()
        == {"missing": 1}
    )
    with pytest.raises(
        TypeError,
        match=re.escape("subn() takes at most 3 arguments (4 given)"),
    ):
        run_benchmark_workload_with_cpython(
            round_tripped_subn_missing_after_positional_count
        )

    assert subn_count_alias_workload.kwargs == {"count_alias": 1}
    round_tripped_subn_count_alias = workload_from_payload(
        workload_to_payload(subn_count_alias_workload)
    )
    assert round_tripped_subn_count_alias.kwargs == {"count_alias": 1}
    assert round_tripped_subn_count_alias.keyword_arguments() == {"count_alias": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("'count_alias' is an invalid keyword argument for subn()"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_subn_count_alias)


def test_standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-module-collection-replacement-keyword-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "module-split-maxsplit-keyword-contract-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabczabc",
                "text_model": "bytes",
                "kwargs": {
                    "maxsplit": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split maxsplit= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-count-keyword-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-count-keyword-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-split-maxsplit-bool-keyword-contract-str",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "maxsplit": True,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split bool maxsplit= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-count-bool-keyword-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": False,
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub bool count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-count-bool-keyword-contract-str",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "kwargs": {
                    "count": True,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn bool count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-split-maxsplit-indexlike-keyword-purged-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabcabcabc",
                "text_model": "bytes",
                "kwargs": {
                    "maxsplit": {"type": "indexlike", "value": 2},
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split keyword __index__ carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-count-indexlike-keyword-warm-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "kwargs": {
                    "count": {"type": "indexlike", "value": 2},
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub keyword __index__ carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-count-indexlike-keyword-purged-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "text_model": "bytes",
                "kwargs": {
                    "count": {"type": "indexlike", "value": 2},
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn keyword __index__ carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-duplicate-count-keyword-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "count": 1,
                "text_model": "bytes",
                "kwargs": {
                    "count": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "multiple values for argument 'count'",
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn duplicate count= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-split-unexpected-keyword-contract-str",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "abc",
                "flags": 0,
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-split-unexpected-keyword-contract-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "abc",
                "flags": 0,
                "text_model": "bytes",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep bytes module.split unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-unexpected-keyword-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "text_model": "bytes",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-count-alias-keyword-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "flags": 0,
                "kwargs": {
                    "count_alias": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'count_alias'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub count_alias keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-sub-unexpected-keyword-after-positional-count-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "count": 1,
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub positional-count-plus-unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-count-alias-keyword-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabc",
                "flags": 0,
                "text_model": "bytes",
                "kwargs": {
                    "count_alias": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'count_alias'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn count_alias keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "module-subn-unexpected-keyword-after-positional-count-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "flags": 0,
                "count": 1,
                "text_model": "bytes",
                "kwargs": {
                    "missing": 1,
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "unexpected keyword argument 'missing'",
                },
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn positional-count-plus-unexpected-keyword carriers unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_module_collection_replacement_keyword_contract.py",
        manifest_source,
    )
    (
        split_workload,
        sub_workload,
        subn_workload,
        split_bool_workload,
        sub_bool_workload,
        subn_bool_workload,
        split_indexlike_workload,
        sub_indexlike_workload,
        subn_indexlike_workload,
        subn_duplicate_workload,
        split_missing_str_workload,
        split_missing_bytes_workload,
        subn_missing_workload,
        sub_count_alias_workload,
        sub_missing_after_positional_count_workload,
        subn_count_alias_workload,
        subn_missing_after_positional_count_workload,
    ) = load_manifest(manifest_path).workloads

    assert split_workload.kwargs == {"maxsplit": 1}
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.kwargs == {"maxsplit": 1}
    assert round_tripped_split.keyword_arguments() == {"maxsplit": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_split) == [
        b"z",
        b"zabc",
    ]

    assert sub_workload.kwargs == {"count": 1}
    round_tripped_sub = workload_from_payload(workload_to_payload(sub_workload))
    assert round_tripped_sub.kwargs == {"count": 1}
    assert round_tripped_sub.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_sub) == "xabc"

    assert subn_workload.kwargs == {"count": 1}
    round_tripped_subn = workload_from_payload(workload_to_payload(subn_workload))
    assert round_tripped_subn.kwargs == {"count": 1}
    assert round_tripped_subn.keyword_arguments() == {"count": 1}
    assert run_benchmark_workload_with_cpython(round_tripped_subn) == (
        b"xabc",
        1,
    )

    assert split_bool_workload.kwargs == {"maxsplit": True}
    assert type(split_bool_workload.kwargs["maxsplit"]) is bool
    round_tripped_split_bool = workload_from_payload(
        workload_to_payload(split_bool_workload)
    )
    assert round_tripped_split_bool.kwargs == {"maxsplit": True}
    assert type(round_tripped_split_bool.kwargs["maxsplit"]) is bool
    materialized_split_bool_kwargs = round_tripped_split_bool.keyword_arguments()
    assert materialized_split_bool_kwargs == {"maxsplit": True}
    assert materialized_split_bool_kwargs["maxsplit"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_split_bool) == [
        "z",
        "abc",
    ]

    assert sub_bool_workload.kwargs == {"count": False}
    assert type(sub_bool_workload.kwargs["count"]) is bool
    round_tripped_sub_bool = workload_from_payload(
        workload_to_payload(sub_bool_workload)
    )
    assert round_tripped_sub_bool.kwargs == {"count": False}
    assert type(round_tripped_sub_bool.kwargs["count"]) is bool
    materialized_sub_bool_kwargs = round_tripped_sub_bool.keyword_arguments()
    assert materialized_sub_bool_kwargs == {"count": False}
    assert materialized_sub_bool_kwargs["count"] is False
    assert run_benchmark_workload_with_cpython(round_tripped_sub_bool) == b"xx"

    assert subn_bool_workload.kwargs == {"count": True}
    assert type(subn_bool_workload.kwargs["count"]) is bool
    round_tripped_subn_bool = workload_from_payload(
        workload_to_payload(subn_bool_workload)
    )
    assert round_tripped_subn_bool.kwargs == {"count": True}
    assert type(round_tripped_subn_bool.kwargs["count"]) is bool
    materialized_subn_bool_kwargs = round_tripped_subn_bool.keyword_arguments()
    assert materialized_subn_bool_kwargs == {"count": True}
    assert materialized_subn_bool_kwargs["count"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_subn_bool) == (
        "xabc",
        1,
    )

    assert split_indexlike_workload.kwargs == {
        "maxsplit": {"type": "indexlike", "value": 2}
    }
    round_tripped_split_indexlike = workload_from_payload(
        workload_to_payload(split_indexlike_workload)
    )
    assert round_tripped_split_indexlike.kwargs == {
        "maxsplit": {"type": "indexlike", "value": 2}
    }
    materialized_split_indexlike_kwargs = (
        round_tripped_split_indexlike.keyword_arguments()
    )
    assert materialized_split_indexlike_kwargs["maxsplit"].__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_split_indexlike) == [
        b"z",
        b"",
        b"abc",
    ]

    assert sub_indexlike_workload.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    round_tripped_sub_indexlike = workload_from_payload(
        workload_to_payload(sub_indexlike_workload)
    )
    assert round_tripped_sub_indexlike.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    materialized_sub_indexlike_kwargs = round_tripped_sub_indexlike.keyword_arguments()
    assert materialized_sub_indexlike_kwargs["count"].__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_sub_indexlike) == "xxabc"

    assert subn_indexlike_workload.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    round_tripped_subn_indexlike = workload_from_payload(
        workload_to_payload(subn_indexlike_workload)
    )
    assert round_tripped_subn_indexlike.kwargs == {
        "count": {"type": "indexlike", "value": 2}
    }
    materialized_subn_indexlike_kwargs = (
        round_tripped_subn_indexlike.keyword_arguments()
    )
    assert materialized_subn_indexlike_kwargs["count"].__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_subn_indexlike) == (
        b"xxabc",
        2,
    )

    assert subn_duplicate_workload.count == 1
    assert subn_duplicate_workload.kwargs == {"count": 1}
    round_tripped_subn_duplicate = workload_from_payload(
        workload_to_payload(subn_duplicate_workload)
    )
    assert round_tripped_subn_duplicate.count == 1
    assert round_tripped_subn_duplicate.kwargs == {"count": 1}
    assert round_tripped_subn_duplicate.keyword_arguments() == {"count": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("subn() got multiple values for argument 'count'"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_subn_duplicate)

    assert split_missing_str_workload.kwargs == {"missing": 1}
    round_tripped_split_missing_str = workload_from_payload(
        workload_to_payload(split_missing_str_workload)
    )
    assert round_tripped_split_missing_str.kwargs == {"missing": 1}
    assert round_tripped_split_missing_str.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("split() got an unexpected keyword argument 'missing'"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_split_missing_str)

    assert split_missing_bytes_workload.kwargs == {"missing": 1}
    round_tripped_split_missing_bytes = workload_from_payload(
        workload_to_payload(split_missing_bytes_workload)
    )
    assert round_tripped_split_missing_bytes.kwargs == {"missing": 1}
    assert round_tripped_split_missing_bytes.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("split() got an unexpected keyword argument 'missing'"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_split_missing_bytes)

    assert subn_missing_workload.kwargs == {"missing": 1}
    round_tripped_subn_missing = workload_from_payload(
        workload_to_payload(subn_missing_workload)
    )
    assert round_tripped_subn_missing.kwargs == {"missing": 1}
    assert round_tripped_subn_missing.keyword_arguments() == {"missing": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("subn() got an unexpected keyword argument 'missing'"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_subn_missing)

    assert sub_count_alias_workload.kwargs == {"count_alias": 1}
    round_tripped_sub_count_alias = workload_from_payload(
        workload_to_payload(sub_count_alias_workload)
    )
    assert round_tripped_sub_count_alias.kwargs == {"count_alias": 1}
    assert round_tripped_sub_count_alias.keyword_arguments() == {"count_alias": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("sub() got an unexpected keyword argument 'count_alias'"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_sub_count_alias)

    assert sub_missing_after_positional_count_workload.count == 1
    assert sub_missing_after_positional_count_workload.kwargs == {"missing": 1}
    round_tripped_sub_missing_after_positional_count = workload_from_payload(
        workload_to_payload(sub_missing_after_positional_count_workload)
    )
    assert round_tripped_sub_missing_after_positional_count.count == 1
    assert round_tripped_sub_missing_after_positional_count.kwargs == {"missing": 1}
    assert (
        round_tripped_sub_missing_after_positional_count.keyword_arguments()
        == {"missing": 1}
    )
    with pytest.raises(
        TypeError,
        match=re.escape("sub() got an unexpected keyword argument 'missing'"),
    ):
        run_benchmark_workload_with_cpython(
            round_tripped_sub_missing_after_positional_count
        )

    assert subn_count_alias_workload.kwargs == {"count_alias": 1}
    round_tripped_subn_count_alias = workload_from_payload(
        workload_to_payload(subn_count_alias_workload)
    )
    assert round_tripped_subn_count_alias.kwargs == {"count_alias": 1}
    assert round_tripped_subn_count_alias.keyword_arguments() == {"count_alias": 1}
    with pytest.raises(
        TypeError,
        match=re.escape("subn() got an unexpected keyword argument 'count_alias'"),
    ):
        run_benchmark_workload_with_cpython(round_tripped_subn_count_alias)

    assert subn_missing_after_positional_count_workload.count == 1
    assert subn_missing_after_positional_count_workload.kwargs == {"missing": 1}
    round_tripped_subn_missing_after_positional_count = workload_from_payload(
        workload_to_payload(subn_missing_after_positional_count_workload)
    )
    assert round_tripped_subn_missing_after_positional_count.count == 1
    assert round_tripped_subn_missing_after_positional_count.kwargs == {"missing": 1}
    assert (
        round_tripped_subn_missing_after_positional_count.keyword_arguments()
        == {"missing": 1}
    )
    with pytest.raises(
        TypeError,
        match=re.escape("subn() got an unexpected keyword argument 'missing'"),
    ):
        run_benchmark_workload_with_cpython(
            round_tripped_subn_missing_after_positional_count
        )


def test_standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-indexlike-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "module-split-indexlike-contract-bytes",
                "bucket": "module-split",
                "family": "module",
                "operation": "module.split",
                "pattern": "abc",
                "haystack": "zabcabcabc",
                "maxsplit": {
                    "type": "indexlike",
                    "value": 2,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.split positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "module-sub-indexlike-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.sub positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "module-subn-indexlike-contract-bytes",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "module-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep module.subn positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "pattern-split-indexlike-contract-str",
                "bucket": "pattern-split",
                "family": "module",
                "operation": "pattern.split",
                "pattern": "abc",
                "haystack": "zabcabcabc",
                "maxsplit": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.split positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "pattern-sub-indexlike-contract-bytes",
                "bucket": "pattern-sub",
                "family": "module",
                "operation": "pattern.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.sub positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
            {
                "id": "pattern-subn-indexlike-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abcabcabc",
                "count": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.subn positional indexlike descriptors JSON-safe until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_indexlike_contract.py",
        manifest_source,
    )
    (
        split_workload,
        sub_workload,
        subn_workload,
        pattern_split_workload,
        pattern_sub_workload,
        pattern_subn_workload,
    ) = load_manifest(manifest_path).workloads

    assert split_workload.maxsplit == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_split = workload_from_payload(workload_to_payload(split_workload))
    assert round_tripped_split.maxsplit_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_split) == [b"z", b"", b"abc"]

    assert sub_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_sub = workload_from_payload(workload_to_payload(sub_workload))
    assert round_tripped_sub.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_sub) == "xxabc"

    assert subn_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_subn = workload_from_payload(workload_to_payload(subn_workload))
    assert round_tripped_subn.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_subn) == (b"xxabc", 2)

    assert pattern_split_workload.maxsplit == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_pattern_split = workload_from_payload(
        workload_to_payload(pattern_split_workload)
    )
    assert round_tripped_pattern_split.maxsplit_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_pattern_split) == [
        "z",
        "",
        "abc",
    ]

    assert pattern_sub_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_pattern_sub = workload_from_payload(
        workload_to_payload(pattern_sub_workload)
    )
    assert round_tripped_pattern_sub.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_pattern_sub) == b"xxabc"

    assert pattern_subn_workload.count == {
        "type": "indexlike",
        "value": 2,
    }
    round_tripped_pattern_subn = workload_from_payload(
        workload_to_payload(pattern_subn_workload)
    )
    assert round_tripped_pattern_subn.count_argument().__index__() == 2
    assert run_benchmark_workload_with_cpython(round_tripped_pattern_subn) == (
        "xxabc",
        2,
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "text_model",
        "expected_result",
        "expected_field_names",
    ),
    (
        pytest.param(
            "pattern.split",
            "zabcabc",
            {"maxsplit": {"type": "indexlike", "value": 1}},
            None,
            "str",
            ["z", "abc"],
            ["kwargs.maxsplit"],
            id="split-maxsplit-indexlike",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count": {"type": "indexlike", "value": 1}},
            "x",
            "bytes",
            b"xabc",
            ["kwargs.count"],
            id="sub-count-indexlike",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count": {"type": "indexlike", "value": 1}},
            "x",
            "str",
            ("xabc", 1),
            ["kwargs.count"],
            id="subn-count-indexlike",
        ),
        pytest.param(
            "pattern.split",
            "zabcabc",
            {"maxsplit": True},
            None,
            "str",
            ["z", "abc"],
            ["kwargs.maxsplit"],
            id="split-maxsplit-bool",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count": False},
            "x",
            "bytes",
            b"xx",
            ["kwargs.count"],
            id="sub-count-bool",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count": True},
            "x",
            "str",
            ("xabc", 1),
            ["kwargs.count"],
            id="subn-count-bool",
        ),
    ),
)
def test_pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    text_model: str,
    expected_result: object,
    expected_field_names: list[str],
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": "warm",
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    support._assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=expected_result,
        expected_field_names=expected_field_names,
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_exception",
        "expected_field_names",
    ),
    (
        pytest.param(
            "pattern.split",
            "abcabc",
            {"maxsplit": 1},
            None,
            0,
            1,
            "str",
            {
                "type": "TypeError",
                "message_substring": "split() takes at most 2 arguments (3 given)",
            },
            ["maxsplit", "kwargs.maxsplit"],
            id="pattern-split-duplicate-maxsplit-keyword",
        ),
        pytest.param(
            "pattern.split",
            "abcabc",
            {"missing": 1},
            None,
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for split()",
            },
            ["kwargs.missing"],
            id="pattern-split-unexpected-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abc",
            {"count": 1},
            "x",
            1,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "sub() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.count"],
            id="pattern-sub-duplicate-count-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abc",
            {"missing": 1},
            "x",
            0,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for sub()",
            },
            ["kwargs.missing"],
            id="pattern-sub-unexpected-keyword",
        ),
        pytest.param(
            "pattern.sub",
            "abc",
            {"missing": 1},
            "x",
            1,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "sub() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.missing"],
            id="pattern-sub-unexpected-keyword-after-positional-count",
        ),
        pytest.param(
            "pattern.sub",
            "abcabc",
            {"count_alias": 1},
            "x",
            0,
            0,
            "str",
            {
                "type": "TypeError",
                "message_substring": "'count_alias' is an invalid keyword argument for sub()",
            },
            ["kwargs.count_alias"],
            id="pattern-sub-count-alias-keyword",
        ),
        pytest.param(
            "pattern.subn",
            "abc",
            {"count": 1},
            "x",
            1,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "subn() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.count"],
            id="pattern-subn-duplicate-count-keyword",
        ),
        pytest.param(
            "pattern.subn",
            "abc",
            {"missing": 1},
            "x",
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'missing' is an invalid keyword argument for subn()",
            },
            ["kwargs.missing"],
            id="pattern-subn-unexpected-keyword",
        ),
        pytest.param(
            "pattern.subn",
            "abc",
            {"missing": 1},
            "x",
            1,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "subn() takes at most 3 arguments (4 given)",
            },
            ["count", "kwargs.missing"],
            id="pattern-subn-unexpected-keyword-after-positional-count",
        ),
        pytest.param(
            "pattern.subn",
            "abcabc",
            {"count_alias": 1},
            "x",
            0,
            0,
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "'count_alias' is an invalid keyword argument for subn()",
            },
            ["kwargs.count_alias"],
            id="pattern-subn-count-alias-keyword",
        ),
    ),
)
def test_pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    text_model: str,
    expected_exception: dict[str, str],
    expected_field_names: list[str],
) -> None:
    workload = support._pattern_helper_collection_replacement_keyword_error_workload(
        operation=operation,
        haystack=haystack,
        kwargs_payload=kwargs_payload,
        replacement=replacement,
        count=count,
        maxsplit=maxsplit,
        expected_exception=expected_exception,
        text_model=text_model,
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)
    callback_field_names: list[str] = []
    helper_name = workload.operation.removeprefix("pattern.")
    positional_keyword_field = _collection_replacement_positional_keyword_field(
        workload
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        for _ in range(2):
            with pytest.raises(TypeError) as expected_error:
                compiled_pattern = re.compile(
                    workload.pattern_payload(),
                    workload.flags,
                )
                kwargs = dict(workload.kwargs)
                if workload.operation == "pattern.split":
                    args: list[object] = [workload.haystack_payload()]
                    if positional_keyword_field == "maxsplit":
                        args.append(workload.maxsplit_argument())
                    getattr(compiled_pattern, helper_name)(*args, **kwargs)
                elif workload.operation in {"pattern.sub", "pattern.subn"}:
                    args = [
                        workload.replacement_payload(),
                        workload.haystack_payload(),
                    ]
                    if positional_keyword_field == "count":
                        args.append(workload.count_argument())
                    getattr(compiled_pattern, helper_name)(*args, **kwargs)
                else:
                    raise AssertionError(
                        "unexpected pattern helper keyword-error workload "
                        f"operation {workload.operation!r}"
                    )
            observed_field_names.clear()
            with pytest.raises(TypeError) as observed_error:
                callback()
            callback_field_names.extend(observed_field_names)

            assert str(observed_error.value) == str(expected_error.value)

        assert callback_field_names == expected_field_names * 2
    finally:
        re.purge()


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    support._assert_keyword_error_workload_probe_measured(
        source_workload,
        import_name=import_name,
        adapter_name=adapter_name,
    )


@pytest.mark.parametrize(
    (
        "operation",
        "haystack",
        "kwargs_payload",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_result",
        "expected_exception_message",
        "expected_field_names",
    ),
    (
        pytest.param(
            "module.split",
            "zabczabc",
            {"maxsplit": 1},
            None,
            0,
            0,
            "bytes",
            [b"z", b"zabc"],
            None,
            ["kwargs.maxsplit"],
            id="module-split-maxsplit-int",
        ),
        pytest.param(
            "module.sub",
            "abcabc",
            {"count": 1},
            "x",
            0,
            0,
            "str",
            "xabc",
            None,
            ["kwargs.count"],
            id="module-sub-count-int",
        ),
        pytest.param(
            "module.subn",
            "abcabc",
            {"count": 1},
            "x",
            0,
            0,
            "bytes",
            (b"xabc", 1),
            None,
            ["kwargs.count"],
            id="module-subn-count-int",
        ),
        pytest.param(
            "module.split",
            "zabcabcabc",
            {"maxsplit": {"type": "indexlike", "value": 2}},
            None,
            0,
            0,
            "bytes",
            [b"z", b"", b"abc"],
            None,
            ["kwargs.maxsplit"],
            id="module-split-maxsplit-indexlike",
        ),
        pytest.param(
            "module.sub",
            "abcabcabc",
            {"count": {"type": "indexlike", "value": 2}},
            "x",
            0,
            0,
            "str",
            "xxabc",
            None,
            ["kwargs.count"],
            id="module-sub-count-indexlike",
        ),
        pytest.param(
            "module.subn",
            "abcabcabc",
            {"count": {"type": "indexlike", "value": 2}},
            "x",
            0,
            0,
            "bytes",
            (b"xxabc", 2),
            None,
            ["kwargs.count"],
            id="module-subn-count-indexlike",
        ),
        pytest.param(
            "module.split",
            "zabcabc",
            {"maxsplit": True},
            None,
            0,
            0,
            "str",
            ["z", "abc"],
            None,
            ["kwargs.maxsplit"],
            id="module-split-maxsplit-bool",
        ),
        pytest.param(
            "module.sub",
            "abcabc",
            {"count": False},
            "x",
            0,
            0,
            "bytes",
            b"xx",
            None,
            ["kwargs.count"],
            id="module-sub-count-bool",
        ),
        pytest.param(
            "module.subn",
            "abcabc",
            {"count": True},
            "x",
            0,
            0,
            "str",
            ("xabc", 1),
            None,
            ["kwargs.count"],
            id="module-subn-count-bool",
        ),
        pytest.param(
            "module.subn",
            "abc",
            {"count": 1},
            "x",
            1,
            0,
            "bytes",
            None,
            "subn() got multiple values for argument 'count'",
            ["count", "kwargs.count"],
            id="module-subn-duplicate-count-keyword-bytes",
        ),
        pytest.param(
            "module.split",
            "abc",
            {"missing": 1},
            None,
            0,
            0,
            "str",
            None,
            "split() got an unexpected keyword argument 'missing'",
            ["kwargs.missing"],
            id="module-split-unexpected-keyword-str",
        ),
        pytest.param(
            "module.split",
            "abc",
            {"missing": 1},
            None,
            0,
            0,
            "bytes",
            None,
            "split() got an unexpected keyword argument 'missing'",
            ["kwargs.missing"],
            id="module-split-unexpected-keyword-bytes",
        ),
        pytest.param(
            "module.subn",
            "abc",
            {"missing": 1},
            "x",
            0,
            0,
            "bytes",
            None,
            "subn() got an unexpected keyword argument 'missing'",
            ["kwargs.missing"],
            id="module-subn-unexpected-keyword-bytes",
        ),
        pytest.param(
            "module.sub",
            "abcabc",
            {"count_alias": 1},
            "x",
            0,
            0,
            "str",
            None,
            "sub() got an unexpected keyword argument 'count_alias'",
            ["kwargs.count_alias"],
            id="module-sub-count-alias-keyword",
        ),
        pytest.param(
            "module.sub",
            "abc",
            {"missing": 1},
            "x",
            1,
            0,
            "str",
            None,
            "sub() got an unexpected keyword argument 'missing'",
            ["count", "kwargs.missing"],
            id="module-sub-unexpected-keyword-after-positional-count",
        ),
        pytest.param(
            "module.subn",
            "abcabc",
            {"count_alias": 1},
            "x",
            0,
            0,
            "bytes",
            None,
            "subn() got an unexpected keyword argument 'count_alias'",
            ["kwargs.count_alias"],
            id="module-subn-count-alias-keyword-bytes",
        ),
        pytest.param(
            "module.subn",
            "abc",
            {"missing": 1},
            "x",
            1,
            0,
            "bytes",
            None,
            "subn() got an unexpected keyword argument 'missing'",
            ["count", "kwargs.missing"],
            id="module-helper-subn-unexpected-keyword-after-positional-count-bytes",
        ),
    ),
)
def test_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: int,
    maxsplit: int,
    text_model: str,
    expected_result: object | None,
    expected_exception_message: str | None,
    expected_field_names: list[str],
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-materialization-contract",
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "expected_exception": (
                None
                if expected_exception_message is None
                else {
                    "type": "TypeError",
                    "message_substring": expected_exception_message,
                }
            ),
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    support._assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=expected_result,
        expected_exception_message=expected_exception_message,
        expected_field_names=expected_field_names,
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    ),
)
def test_module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    source_workload: Workload,
) -> None:
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = build_callable(re, "re", source_workload)
        assert observed_field_names == []

        with pytest.raises(TypeError) as expected_error:
            run_benchmark_workload_with_cpython(source_workload)
        observed_field_names.clear()
        with pytest.raises(TypeError) as observed_error:
            callback()

        expected_field_names = [f"kwargs.{name}" for name in source_workload.kwargs]
        if not _is_module_workflow_keyword_error_workload(source_workload):
            positional_keyword_field = _collection_replacement_positional_keyword_field(
                source_workload
            )
            if positional_keyword_field is not None:
                expected_field_names.insert(0, positional_keyword_field)

        assert observed_field_names == expected_field_names
        assert str(observed_error.value) == str(expected_error.value)
    finally:
        re.purge()


@pytest.mark.parametrize(
    (
        "workload_id",
        "bucket",
        "operation",
        "haystack",
        "replacement",
        "count",
        "maxsplit",
        "text_model",
        "expected_result",
        "expected_field_name",
    ),
    (
        pytest.param(
            "module-split-indexlike-contract-bytes",
            "module-split",
            "module.split",
            "zabcabcabc",
            None,
            0,
            {"type": "indexlike", "value": 2},
            "bytes",
            [b"z", b"", b"abc"],
            "maxsplit",
            id="module-split",
        ),
        pytest.param(
            "module-sub-indexlike-contract-str",
            "module-sub",
            "module.sub",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "str",
            "xxabc",
            "count",
            id="module-sub",
        ),
        pytest.param(
            "module-subn-indexlike-contract-bytes",
            "module-subn",
            "module.subn",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "bytes",
            (b"xxabc", 2),
            "count",
            id="module-subn",
        ),
        pytest.param(
            "pattern-split-indexlike-contract-str",
            "pattern-split",
            "pattern.split",
            "zabcabcabc",
            None,
            0,
            {"type": "indexlike", "value": 2},
            "str",
            ["z", "", "abc"],
            "maxsplit",
            id="pattern-split",
        ),
        pytest.param(
            "pattern-sub-indexlike-contract-bytes",
            "pattern-sub",
            "pattern.sub",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "bytes",
            b"xxabc",
            "count",
            id="pattern-sub",
        ),
        pytest.param(
            "pattern-subn-indexlike-contract-str",
            "pattern-subn",
            "pattern.subn",
            "abcabcabc",
            "x",
            {"type": "indexlike", "value": 2},
            0,
            "str",
            ("xxabc", 2),
            "count",
            id="pattern-subn",
        ),
    ),
)
def test_collection_replacement_indexlike_descriptors_materialize_on_each_helper_call(
    monkeypatch,
    workload_id: str,
    bucket: str,
    operation: str,
    haystack: str,
    replacement: str | None,
    count: object,
    maxsplit: object,
    text_model: str,
    expected_result: object,
    expected_field_name: str,
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-indexlike-contract",
            "workload_id": workload_id,
            "bucket": bucket,
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": (
                "module-helper-call"
                if operation.startswith("module.")
                else "pattern-helper-call"
            ),
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []
        assert callback() == expected_result
        assert callback() == expected_result
    finally:
        re.purge()

    assert observed_field_names == [expected_field_name, expected_field_name]


def test_pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor(
) -> None:
    manifest = load_manifest(support.COLLECTION_REPLACEMENT_MANIFEST_PATH)
    workload = next(
        candidate
        for candidate in manifest.workloads
        if candidate.workload_id == "pattern-split-no-match-warm-str"
    )

    assert workload.maxsplit == 0
    assert _collection_replacement_pattern_split_workload_signature(workload) == (
        "pattern.split",
        "abc",
        ("zzz",),
        (),
        0,
        "str",
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in support._MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_module_helper_keyword_error_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    support._assert_keyword_error_workload_probe_measured(
        source_workload,
        import_name=import_name,
        adapter_name=adapter_name,
    )
