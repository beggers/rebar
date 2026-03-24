from __future__ import annotations

import json
import re
from typing import Any

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    Workload,
    build_callable,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    _record_numeric_materialization_fields,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _collection_replacement_positional_keyword_field,
    _is_collection_replacement_keyword_workload,
)
from tests.benchmarks.module_pattern_keyword_benchmark_anchor_support import (
    _is_module_workflow_keyword_error_workload,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _contract_source_workloads,
)

COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
)
MODULE_BOUNDARY_MANIFEST_PATH = BENCHMARK_WORKLOADS_ROOT / "module_boundary.py"


def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
    monkeypatch,
    workload: Workload,
    *,
    expected_result: object | None,
    expected_exception_message: str | None = None,
    expected_field_names: list[str] | tuple[str, ...],
) -> None:
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        if expected_exception_message is None:
            assert callback() == expected_result
            assert callback() == expected_result
        else:
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()

        assert observed_field_names == list(expected_field_names) * 2
    finally:
        re.purge()


def _pattern_helper_collection_replacement_keyword_error_workload(
    *,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
) -> Workload:
    return workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-error-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
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


_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "pattern-split-duplicate-maxsplit-keyword-warm-str",
    "pattern-split-unexpected-keyword-warm-bytes",
    "pattern-sub-duplicate-count-keyword-warm-str",
    "pattern-sub-unexpected-keyword-warm-str",
    "pattern-sub-unexpected-keyword-after-positional-count-warm-str",
    "pattern-sub-count-alias-keyword-warm-str",
    "pattern-subn-duplicate-count-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes",
    "pattern-subn-count-alias-keyword-warm-bytes",
)


def _is_collection_replacement_pattern_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = _contract_source_workloads(
    manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_pattern_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "pattern helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)


def _assert_keyword_error_workload_probe_measured(
    source_workload: Workload,
    *,
    import_name: str,
    adapter_name: str,
) -> None:
    payload = workload_to_payload(source_workload)
    round_tripped = workload_from_payload(payload)

    assert payload["workload_id"] == source_workload.workload_id
    assert round_tripped.workload_id == source_workload.workload_id
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert payload["kwargs"] == source_workload.kwargs
    assert round_tripped.kwargs == source_workload.kwargs

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-search-duplicate-flags-keyword-warm-str",
    "module-fullmatch-unexpected-keyword-purged-str",
)

_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-split-duplicate-maxsplit-keyword-purged-str",
    "module-split-unexpected-keyword-purged-str",
    "module-split-unexpected-keyword-purged-bytes",
    "module-sub-duplicate-count-keyword-warm-str",
    "module-sub-unexpected-keyword-purged-str",
    "module-sub-unexpected-keyword-after-positional-count-purged-str",
    "module-sub-count-alias-keyword-purged-str",
    "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
    "module-subn-count-alias-keyword-purged-bytes",
)


def _is_collection_replacement_module_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = _contract_source_workloads(
    manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
    include_workload_selectors=(_is_module_workflow_keyword_error_workload,),
    expected_source_workload_ids=_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS,
    drift_message=(
        "module helper keyword-error surface drifted from the live source "
        "workload surface"
    ),
) + _contract_source_workloads(
    manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_module_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "module helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)
