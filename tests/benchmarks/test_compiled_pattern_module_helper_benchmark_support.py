from __future__ import annotations

import re
from types import SimpleNamespace

import pytest

from tests.benchmarks.benchmark_test_support import synthetic_workload
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _compiled_pattern_module_helper_route,
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
    _run_cpython_compiled_pattern_module_helper_workload,
)


def _manifest_id_for_operation(operation: str) -> str:
    if operation in {"module.search", "module.match", "module.fullmatch"}:
        return "module-boundary"
    return "collection-replacement-boundary"


def _fake_workload(
    *,
    workload_id: str,
    operation: str,
    text_model: str = "str",
    haystack_text_model: str | None = None,
    use_compiled_pattern: bool = False,
    expected_exception: dict[str, str] | None = None,
    kwargs: dict[str, object] | None = None,
) -> object:
    return SimpleNamespace(
        workload_id=workload_id,
        operation=operation,
        flags=0,
        text_model=text_model,
        haystack_text_model=haystack_text_model,
        use_compiled_pattern=use_compiled_pattern,
        expected_exception=expected_exception,
        kwargs={} if kwargs is None else kwargs,
    )


@pytest.mark.parametrize(
    ("workload", "callback_flags", "expected_result", "expected_call", "expected_cpython_args", "materialize"),
    (
        (
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.search"),
                workload_id="module-search-success",
                operation="module.search",
                pattern="abc",
                haystack="zzabczz",
                flags=re.IGNORECASE,
                use_compiled_pattern=True,
            ),
            re.IGNORECASE,
            "module-result",
            ("module.search", "zzabczz", 0, {}),
            ("zzabczz", re.IGNORECASE),
            False,
        ),
        (
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.subn"),
                workload_id="module-subn-success",
                operation="module.subn",
                pattern="abc",
                haystack="abcabc",
                replacement="x",
                count=1,
                flags=re.IGNORECASE,
                use_compiled_pattern=True,
            ),
            re.IGNORECASE,
            ("module-result", 0),
            ("module.subn", "x", "abcabc", 1, re.IGNORECASE, {}),
            ("x", "abcabc", 1),
            False,
        ),
        (
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.finditer"),
                workload_id="module-finditer-wrong-text-model",
                operation="module.finditer",
                pattern="abc",
                haystack="abcabc",
                text_model="bytes",
                haystack_text_model="str",
                use_compiled_pattern=True,
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
            synthetic_workload(
                manifest_id=_manifest_id_for_operation("module.split"),
                workload_id="module-split-success",
                operation="module.split",
                pattern="abc",
                haystack="abcabc",
                maxsplit=2,
                flags=re.MULTILINE,
                use_compiled_pattern=True,
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
    callback_result, callback_call, cpython_call_args, materialize_cpython_result = route

    assert callback_result == expected_result
    assert callback_call == expected_call
    assert cpython_call_args == expected_cpython_args
    assert materialize_cpython_result is materialize


def test_run_cpython_compiled_pattern_module_helper_workload_materializes_finditer() -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.finditer"),
        workload_id="module-finditer-runtime",
        operation="module.finditer",
        pattern="abc",
        haystack="abcabc",
        use_compiled_pattern=True,
    )

    result = _run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
    )

    assert isinstance(result, list)
    assert [match.group(0) for match in result] == ["abc", "abc"]


def test_run_cpython_compiled_pattern_module_helper_workload_preserves_scalar_result() -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.subn"),
        workload_id="module-subn-runtime",
        operation="module.subn",
        pattern="abc",
        haystack="abcabc",
        replacement="x",
        count=1,
        use_compiled_pattern=True,
    )

    result = _run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
    )

    assert result == ("xabc", 1)


def test_compiled_pattern_module_helper_wrong_text_model_selector_accepts_bounded_trio() -> None:
    workload = synthetic_workload(
        manifest_id=_manifest_id_for_operation("module.search"),
        workload_id="module.search-wrong-text-model",
        operation="module.search",
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )

    assert _is_module_workflow_compiled_pattern_wrong_text_model_workload(workload)


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

    assert not _is_module_workflow_compiled_pattern_wrong_text_model_workload(
        wrong_pattern_argument
    )
    assert not _is_module_workflow_compiled_pattern_wrong_text_model_workload(
        missing_haystack_text_model
    )
    assert not _is_module_workflow_compiled_pattern_wrong_text_model_workload(
        wrong_exception_type
    )
