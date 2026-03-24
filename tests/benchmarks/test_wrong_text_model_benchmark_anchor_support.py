from __future__ import annotations

from collections.abc import Callable
from types import SimpleNamespace
import unittest

import pytest
from rebar_harness.benchmarks import BENCHMARK_WORKLOADS_ROOT, load_manifest

from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _is_collection_replacement_pattern_wrong_text_model_workload,
    _is_collection_replacement_wrong_text_model_workload,
)
from tests.benchmarks.benchmark_test_support import (
    assert_benchmark_workload_contract,
    find_workload_document,
    find_workload_record,
    manifest_workload_ids_matching,
    synthetic_workload,
)
from tests.benchmarks import wrong_text_model_benchmark_anchor_support as support
from tests.conftest import run_harness_scorecard

_SOURCE_TREE_MANIFEST_PATHS = {
    "collection-replacement-boundary": (
        BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
    ),
    "module-boundary": BENCHMARK_WORKLOADS_ROOT / "module_boundary.py",
    "pattern-boundary": BENCHMARK_WORKLOADS_ROOT / "pattern_boundary.py",
}


def _manifest_id_for_operation(operation: str) -> str:
    if operation.startswith("module."):
        return "module-boundary"
    if operation.startswith("pattern."):
        return "pattern-boundary"
    return "wrong-text-model-support"


def _fake_workload(
    *,
    workload_id: str,
    operation: str,
    text_model: str = "str",
    haystack_text_model: str | None = None,
    use_compiled_pattern: bool = False,
    expected_exception: dict[str, str] | None = None,
    kwargs: dict[str, object] | None = None,
    pos: object = None,
    endpos: object = None,
) -> object:
    pattern_value = b"abc" if text_model == "bytes" else "abc"
    haystack_value: object = b"abc" if haystack_text_model == "bytes" else "abc"
    return SimpleNamespace(
        workload_id=workload_id,
        operation=operation,
        flags=0,
        text_model=text_model,
        haystack_text_model=haystack_text_model,
        use_compiled_pattern=use_compiled_pattern,
        expected_exception=expected_exception,
        kwargs={} if kwargs is None else kwargs,
        pos=pos,
        endpos=endpos,
        pattern_payload=lambda: pattern_value,
        haystack_payload=lambda: haystack_value,
    )


def _pattern_case(
    *,
    helper: str,
    haystack: object,
    text_model: str | None,
    kwargs: dict[str, object] | None = None,
    flags: int = 0,
    pattern: str = "abc",
) -> object:
    pattern_value = pattern.encode() if text_model == "bytes" else pattern
    return SimpleNamespace(
        helper=helper,
        operation="pattern_call",
        args=(haystack,),
        kwargs={} if kwargs is None else kwargs,
        pattern=pattern,
        flags=flags,
        text_model=text_model,
        pattern_payload=lambda: pattern_value,
    )


def _assert_zero_gap_source_tree_manifest_rows_measured(
    *,
    manifest_id: str,
    include_workload: Callable[[object], bool],
    expected_selected_workload_ids: tuple[str, ...],
) -> None:
    manifest = load_manifest(_SOURCE_TREE_MANIFEST_PATHS[manifest_id])
    workload_count = len(manifest.workloads)
    expected_measured_workload_ids = manifest_workload_ids_matching(
        manifest,
        include_workload,
    )

    assert expected_measured_workload_ids == expected_selected_workload_ids

    _, scorecard = run_harness_scorecard(
        "rebar_harness.benchmarks",
        ["--manifest", str(manifest.path)],
        report_name="benchmarks.json",
    )
    manifest_summary = scorecard["manifests"][manifest_id]

    assert manifest_summary["known_gap_count"] == 0
    assert manifest_summary["measured_workloads"] == workload_count
    assert manifest_summary["workload_count"] == workload_count

    testcase = unittest.TestCase()
    for workload_id in expected_measured_workload_ids:
        assert_benchmark_workload_contract(
            testcase,
            find_workload_record(scorecard, workload_id),
            manifest_id=manifest_id,
            workload_document=find_workload_document(
                manifest,
                workload_id,
            ),
            expected_status="measured",
        )


@pytest.mark.parametrize(
    ("operation", "haystack_text_model", "message_substring"),
    (
        (
            "module.search",
            "bytes",
            "cannot use a string pattern on a bytes-like object",
        ),
        (
            "module.match",
            "str",
            "cannot use a bytes pattern on a string-like object",
        ),
        (
            "module.fullmatch",
            "bytes",
            "cannot use a string pattern on a bytes-like object",
        ),
    ),
)
def test_compiled_pattern_module_helper_wrong_text_model_selector_accepts_bounded_trio(
    operation: str,
    haystack_text_model: str,
    message_substring: str,
) -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation(operation),
        workload_id=f"{operation}-wrong-text-model",
        operation=operation,
        text_model="str" if haystack_text_model == "bytes" else "bytes",
        haystack_text_model=haystack_text_model,
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": message_substring,
        },
    )

    assert support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
        workload
    )


def test_compiled_pattern_module_helper_wrong_text_model_selector_rejects_missing_guard_fields() -> None:
    wrong_pattern_argument = _fake_workload(
        workload_id="module-search-direct-pattern",
        operation="module.search",
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    missing_haystack_text_model = _fake_workload(
        workload_id="module-search-no-haystack-model",
        operation="module.search",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )
    wrong_exception_type = _fake_workload(
        workload_id="module-search-value-error",
        operation="module.search",
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "ValueError",
            "message_substring": "wrong exception type",
        },
    )

    assert not support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
        wrong_pattern_argument
    )
    assert not support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
        missing_haystack_text_model
    )
    assert not support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
        wrong_exception_type
    )


@pytest.mark.parametrize(
    ("operation", "text_model", "haystack_text_model", "expected_haystack"),
    (
        ("pattern.search", "str", "bytes", b"abc"),
        ("pattern.match", "bytes", "str", "abc"),
        ("pattern.fullmatch", "str", "bytes", b"abc"),
    ),
)
def test_pattern_boundary_wrong_text_model_selector_accepts_exact_trio_and_signature_shape(
    operation: str,
    text_model: str,
    haystack_text_model: str,
    expected_haystack: object,
) -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation(operation),
        workload_id=f"{operation}-wrong-text-model",
        operation=operation,
        text_model=text_model,
        haystack_text_model=haystack_text_model,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
    )

    assert support._is_pattern_boundary_wrong_text_model_workload(workload)
    assert support._pattern_boundary_wrong_text_model_workload_signature(
        workload
    ) == (
        operation,
        b"abc" if text_model == "bytes" else "abc",
        (expected_haystack,),
        (),
        0,
        text_model,
    )


def test_pattern_boundary_wrong_text_model_selector_rejects_compiled_pattern_window_and_keyword_rows() -> None:
    compiled_pattern_workload = _fake_workload(
        workload_id="pattern-search-compiled-pattern",
        operation="pattern.search",
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
    )
    keyword_workload = _fake_workload(
        workload_id="pattern-search-keyword",
        operation="pattern.search",
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        kwargs={"pos": 1},
    )
    windowed_workload = _fake_workload(
        workload_id="pattern-search-window",
        operation="pattern.search",
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        pos=0,
    )

    assert not support._is_pattern_boundary_wrong_text_model_workload(
        compiled_pattern_workload
    )
    assert not support._is_pattern_boundary_wrong_text_model_workload(keyword_workload)
    assert not support._is_pattern_boundary_wrong_text_model_workload(windowed_workload)


def test_pattern_boundary_wrong_text_model_correctness_case_signatures_cover_str_and_bytes_rows() -> None:
    str_case = _pattern_case(helper="search", haystack=b"abc", text_model="str")
    bytes_case = _pattern_case(helper="match", haystack="abc", text_model="bytes")
    wrong_haystack_type = _pattern_case(
        helper="fullmatch",
        haystack="abc",
        text_model="str",
    )

    assert support._pattern_boundary_wrong_text_model_correctness_case_signature(
        str_case
    ) == (
        "pattern.search",
        "abc",
        (b"abc",),
        (),
        0,
        "str",
    )
    assert support._pattern_boundary_wrong_text_model_correctness_case_signature(
        bytes_case
    ) == (
        "pattern.match",
        b"abc",
        ("abc",),
        (),
        0,
        "bytes",
    )
    assert (
        support._pattern_boundary_wrong_text_model_correctness_case_signature(
            wrong_haystack_type
        )
        is None
    )


def test_collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured() -> None:
    _assert_zero_gap_source_tree_manifest_rows_measured(
        manifest_id="collection-replacement-boundary",
        include_workload=_is_collection_replacement_wrong_text_model_workload,
        expected_selected_workload_ids=(
            "module-split-on-bytes-string-purged-str-compiled-pattern",
            "module-findall-on-str-string-purged-bytes-compiled-pattern",
            "module-finditer-on-bytes-string-warm-str-compiled-pattern",
            "module-sub-on-bytes-string-warm-str-compiled-pattern",
            "module-subn-on-str-string-purged-bytes-compiled-pattern",
        ),
    )


def test_collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured() -> None:
    _assert_zero_gap_source_tree_manifest_rows_measured(
        manifest_id="collection-replacement-boundary",
        include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
        expected_selected_workload_ids=(
            "pattern-split-on-bytes-string-warm-str",
            "pattern-sub-on-bytes-string-warm-str",
            "pattern-subn-on-str-string-purged-bytes",
        ),
    )


def test_module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured() -> None:
    _assert_zero_gap_source_tree_manifest_rows_measured(
        manifest_id="module-boundary",
        include_workload=(
            support._is_module_workflow_compiled_pattern_wrong_text_model_workload
        ),
        expected_selected_workload_ids=(
            "module-search-on-bytes-string-warm-str-compiled-pattern",
            "module-match-on-str-string-purged-bytes-compiled-pattern",
            "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
        ),
    )
