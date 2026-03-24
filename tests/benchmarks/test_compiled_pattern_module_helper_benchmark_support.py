from __future__ import annotations

import re

import pytest

from rebar_harness.benchmarks import workload_from_payload
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _compiled_pattern_module_helper_route,
    _run_cpython_compiled_pattern_module_helper_workload,
)


def _manifest_id_for_operation(operation: str) -> str:
    if operation in {"module.search", "module.match", "module.fullmatch"}:
        return "module-boundary"
    return "collection-replacement-boundary"


def _workload(
    *,
    workload_id: str,
    operation: str,
    pattern: str = "abc",
    haystack: str = "abc",
    replacement: str | None = None,
    flags: int = 0,
    text_model: str = "str",
    haystack_text_model: str | None = None,
    expected_exception: dict[str, str] | None = None,
    count: int = 0,
    maxsplit: int = 0,
) -> object:
    payload: dict[str, object] = {
        "manifest_id": _manifest_id_for_operation(operation),
        "workload_id": workload_id,
        "bucket": operation.replace(".", "-"),
        "family": "module",
        "operation": operation,
        "pattern": pattern,
        "haystack": haystack,
        "flags": flags,
        "use_compiled_pattern": True,
        "expected_exception": expected_exception,
        "text_model": text_model,
        "cache_mode": "warm",
        "timing_scope": "module-helper-call",
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": False,
    }
    if replacement is not None:
        payload["replacement"] = replacement
    if haystack_text_model is not None:
        payload["haystack_text_model"] = haystack_text_model
    if count:
        payload["count"] = count
    if maxsplit:
        payload["maxsplit"] = maxsplit
    return workload_from_payload(payload)


@pytest.mark.parametrize(
    ("workload", "callback_flags", "expected_result", "expected_call", "expected_cpython_args", "materialize"),
    (
        (
            _workload(
                workload_id="module-search-success",
                operation="module.search",
                pattern="abc",
                haystack="zzabczz",
                flags=re.IGNORECASE,
            ),
            re.IGNORECASE,
            "module-result",
            ("module.search", "zzabczz", 0, {}),
            ("zzabczz", re.IGNORECASE),
            False,
        ),
        (
            _workload(
                workload_id="module-subn-success",
                operation="module.subn",
                pattern="abc",
                haystack="abcabc",
                replacement="x",
                count=1,
                flags=re.IGNORECASE,
            ),
            re.IGNORECASE,
            ("module-result", 0),
            ("module.subn", "x", "abcabc", 1, re.IGNORECASE, {}),
            ("x", "abcabc", 1),
            False,
        ),
        (
            _workload(
                workload_id="module-finditer-wrong-text-model",
                operation="module.finditer",
                pattern="abc",
                haystack="abcabc",
                text_model="bytes",
                haystack_text_model="str",
                expected_exception={
                    "type": "TypeError",
                    "message_substring": "cannot use a bytes pattern on a string-like object",
                },
            ),
            0,
            ["module-finditer-result"],
            ("module.finditer", "abcabc", 0),
            ("abcabc", 0),
            True,
        ),
        (
            _workload(
                workload_id="module-split-success",
                operation="module.split",
                pattern="abc",
                haystack="abcabc",
                maxsplit=2,
                flags=re.MULTILINE,
            ),
            re.MULTILINE,
            "module-result",
            ("module.split", "abcabc", 2, re.MULTILINE, {}),
            ("abcabc", 2),
            False,
        ),
    ),
    ids=(
        "module-boundary-search",
        "collection-replacement-subn",
        "wrong-text-model-finditer",
        "collection-replacement-split",
    ),
)
def test_compiled_pattern_module_helper_route_preserves_expected_shapes(
    workload: object,
    callback_flags: int,
    expected_result: object,
    expected_call: tuple[object, ...],
    expected_cpython_args: tuple[object, ...],
    materialize: bool,
) -> None:
    route = _compiled_pattern_module_helper_route(
        workload,
        collection_replacement_callback_flags=callback_flags,
    )

    assert route.callback_result == expected_result
    assert route.callback_call == expected_call
    assert route.cpython_call_args == expected_cpython_args
    assert route.materialize_cpython_result is materialize


def test_run_cpython_compiled_pattern_module_helper_workload_materializes_finditer() -> None:
    workload = _workload(
        workload_id="module-finditer-runtime",
        operation="module.finditer",
        pattern="abc",
        haystack="abcabc",
    )

    result = _run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
    )

    assert isinstance(result, list)
    assert [match.group(0) for match in result] == ["abc", "abc"]


def test_run_cpython_compiled_pattern_module_helper_workload_preserves_scalar_result() -> None:
    workload = _workload(
        workload_id="module-subn-runtime",
        operation="module.subn",
        pattern="abc",
        haystack="abcabc",
        replacement="x",
        count=1,
    )

    result = _run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
    )

    assert result == ("xabc", 1)
