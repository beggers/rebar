from __future__ import annotations

from types import SimpleNamespace

import pytest

from rebar_harness.benchmarks import workload_from_payload
from tests.benchmarks import wrong_text_model_benchmark_anchor_support as support


def _manifest_id_for_operation(operation: str) -> str:
    if operation.startswith("module."):
        return "module-boundary"
    if operation.startswith("pattern."):
        return "pattern-boundary"
    return "wrong-text-model-support"


def _workload(
    *,
    workload_id: str,
    operation: str,
    pattern: str = "abc",
    haystack: str = "abc",
    text_model: str = "str",
    haystack_text_model: str | None = None,
    use_compiled_pattern: bool = False,
    expected_exception: dict[str, str] | None = None,
    kwargs: dict[str, object] | None = None,
    pos: object = None,
    endpos: object = None,
) -> object:
    return workload_from_payload(
        {
            "manifest_id": _manifest_id_for_operation(operation),
            "workload_id": workload_id,
            "bucket": operation.replace(".", "-"),
            "family": "module",
            "operation": operation,
            "pattern": pattern,
            "haystack": haystack,
            "expected_exception": expected_exception,
            "flags": 0,
            "use_compiled_pattern": use_compiled_pattern,
            "kwargs": {} if kwargs is None else kwargs,
            "text_model": text_model,
            "haystack_text_model": haystack_text_model,
            "pos": pos,
            "endpos": endpos,
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
    )


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
    workload = _workload(
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
    workload = _workload(
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
