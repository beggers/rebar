from __future__ import annotations

from types import SimpleNamespace

from rebar_harness.benchmarks import workload_from_payload
from tests.benchmarks import (
    module_pattern_keyword_benchmark_anchor_support as support,
)
from tests.python.fixture_parity_support import IndexLike


def _module_pattern_workload(
    *,
    workload_id: str,
    operation: str,
    pattern: str = "abc",
    haystack: str = "zabc",
    kwargs: dict[str, object] | None = None,
    expected_exception: dict[str, str] | None = None,
    flags: int = 0,
    use_compiled_pattern: bool = False,
    text_model: str = "str",
    categories: list[str] | None = None,
    pos: object | None = None,
    endpos: object | None = None,
) -> object:
    return workload_from_payload(
        {
            "manifest_id": "module-pattern-boundary",
            "workload_id": workload_id,
            "bucket": operation.replace(".", "-"),
            "family": "module",
            "operation": operation,
            "pattern": pattern,
            "haystack": haystack,
            "replacement": None,
            "expected_exception": expected_exception,
            "flags": flags,
            "use_compiled_pattern": use_compiled_pattern,
            "count": 0,
            "maxsplit": 0,
            "kwargs": {} if kwargs is None else kwargs,
            "text_model": text_model,
            "haystack_text_model": None,
            "pos": pos,
            "endpos": endpos,
            "cache_mode": "warm",
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [] if categories is None else categories,
            "syntax_features": [],
            "smoke": False,
        }
    )


def _module_pattern_case(
    *,
    helper: str,
    operation: str,
    args: tuple[object, ...],
    kwargs: dict[str, object] | None = None,
    pattern: str = "abc",
    flags: int = 0,
    text_model: str | None = "str",
    use_compiled_pattern: bool = False,
) -> object:
    pattern_value = pattern.encode() if text_model == "bytes" else pattern
    return SimpleNamespace(
        helper=helper,
        operation=operation,
        args=args,
        kwargs={} if kwargs is None else kwargs,
        pattern=pattern,
        flags=flags,
        text_model=text_model,
        use_compiled_pattern=use_compiled_pattern,
        pattern_payload=lambda: pattern_value,
    )


def test_module_keyword_success_workload_and_case_signatures_stay_pinned() -> None:
    workload = _module_pattern_workload(
        workload_id="module-search-flags-keyword",
        operation="module.search",
        kwargs={"flags": {"type": "indexlike", "value": 2}},
        flags=2,
    )
    case = _module_pattern_case(
        helper="search",
        operation="module_call",
        args=("zabc",),
        kwargs={"flags": IndexLike(2)},
        flags=2,
    )

    assert support._is_module_workflow_keyword_flags_workload(workload)
    assert support._module_workflow_keyword_workload_args(workload) == ("zabc",)
    assert support._module_workflow_keyword_workload_signature(workload) == (
        "module.search",
        "abc",
        ("zabc",),
        (("flags", "indexlike", 2),),
        2,
        "str",
    )
    assert support._module_workflow_keyword_correctness_case_signature(case) == (
        "module.search",
        "abc",
        ("zabc",),
        (("flags", "indexlike", 2),),
        2,
        "str",
    )


def test_module_keyword_error_workload_stays_pinned() -> None:
    workload = _module_pattern_workload(
        workload_id="module-search-duplicate-flags-keyword",
        operation="module.search",
        kwargs={"flags": {"type": "indexlike", "value": 4}},
        expected_exception={
            "type": "TypeError",
            "message_substring": "multiple values for argument 'flags'",
        },
        flags=4,
    )

    assert support._is_module_workflow_keyword_error_workload(workload)
    assert support._module_workflow_keyword_workload_args(workload) == ("zabc", 4)
    assert support._module_workflow_keyword_workload_signature(workload) == (
        "module.search",
        "abc",
        ("zabc", 4),
        (("flags", "indexlike", 4),),
        4,
        "str",
    )


def test_pattern_window_positional_indexlike_workload_and_case_signatures_stay_pinned() -> None:
    workload = _module_pattern_workload(
        workload_id="pattern-finditer-window-indexlike",
        operation="pattern.finditer",
        haystack="zabcabc",
        categories=["positional-window", "indexlike"],
        pos={"type": "indexlike", "value": 1},
        endpos={"type": "indexlike", "value": 6},
    )
    case = _module_pattern_case(
        helper="finditer",
        operation="pattern_call",
        args=("zabcabc", IndexLike(1), IndexLike(6)),
    )

    assert support._is_pattern_window_positional_indexlike_workload(workload)
    assert support._pattern_window_positional_indexlike_workload_args(workload) == (
        "zabcabc",
        {"type": "indexlike", "value": 1},
        {"type": "indexlike", "value": 6},
    )
    assert support._pattern_window_positional_indexlike_workload_signature(
        workload
    ) == (
        "finditer",
        "abc",
        (("str", "zabcabc"), ("indexlike", 1), ("indexlike", 6)),
        "str",
    )
    assert support._pattern_window_positional_indexlike_correctness_case_signature(
        case
    ) == (
        "finditer",
        "abc",
        (("str", "zabcabc"), ("indexlike", 1), ("indexlike", 6)),
        "str",
    )


def test_pattern_keyword_window_workload_and_case_signatures_stay_pinned() -> None:
    workload = _module_pattern_workload(
        workload_id="pattern-findall-bool-window-keyword",
        operation="pattern.findall",
        haystack="zabcabc",
        kwargs={"endpos": True},
        categories=["keyword"],
    )
    case = _module_pattern_case(
        helper="findall",
        operation="pattern_call",
        args=("zabcabc",),
        kwargs={"endpos": True},
    )

    assert support._is_pattern_keyword_window_workload(workload)
    assert support._pattern_keyword_window_workload_signature(workload) == (
        "pattern.findall",
        "abc",
        ("zabcabc",),
        (("endpos", "bool", True),),
        0,
        "str",
    )
    assert support._pattern_keyword_window_correctness_case_signature(case) == (
        "pattern.findall",
        "abc",
        ("zabcabc",),
        (("endpos", "bool", True),),
        0,
        "str",
    )
