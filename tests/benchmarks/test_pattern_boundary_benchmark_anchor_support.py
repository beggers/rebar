from __future__ import annotations

from types import SimpleNamespace

from tests.benchmarks.benchmark_test_support import synthetic_workload
from tests.benchmarks import pattern_boundary_benchmark_anchor_support as support


def _pattern_case(
    *,
    case_id: str,
    helper: str,
    args: tuple[object, ...],
    pattern: str,
    flags: int,
    text_model: str = "str",
    kwargs: dict[str, object] | None = None,
) -> object:
    return SimpleNamespace(
        case_id=case_id,
        helper=helper,
        operation="pattern_call",
        args=args,
        kwargs={} if kwargs is None else kwargs,
        pattern=pattern,
        flags=flags,
        text_model=text_model,
        pattern_payload=lambda: pattern.encode() if text_model == "bytes" else pattern,
        serialized_args=lambda: list(args),
    )


def test_pattern_bounded_wildcard_selector_and_signature_stay_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id=support._PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS[0],
        operation="pattern.search",
        flags=2,
        pattern="a.c",
        haystack="zabc",
        timing_scope="pattern-helper-call",
        pos=1,
        endpos=4,
    )

    assert support._is_pattern_bounded_wildcard_workload(workload)
    assert support._pattern_bounded_wildcard_workload_signature(workload) == (
        "pattern.search",
        "a.c",
        ("zabc", 1, 4),
        (),
        2,
        "str",
    )


def test_pattern_bounded_wildcard_selector_rejects_nonmatching_pattern() -> None:
    workload = synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id=support._PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS[1],
        operation="pattern.match",
        pattern="abc",
        haystack="zabc",
        timing_scope="pattern-helper-call",
        pos=0,
        endpos=3,
    )

    assert not support._is_pattern_bounded_wildcard_workload(workload)


def test_pattern_verbose_regression_selector_and_signature_stay_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id=support._PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS[0],
        operation="pattern.search",
        pattern=(
            "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"
        ),
        haystack="KEY = 42",
        flags=72,
        timing_scope="pattern-helper-call",
    )

    assert support._is_pattern_verbose_regression_workload(workload)
    assert support._pattern_verbose_regression_workload_signature(workload) == (
        "pattern.search",
        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        ("KEY = 42",),
        (),
        72,
        "str",
    )


def test_pattern_verbose_regression_correctness_case_signature_stays_pinned() -> None:
    case = _pattern_case(
        case_id=support._PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS[0],
        helper="fullmatch",
        args=("KEY = ABC",),
        pattern="^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        flags=72,
    )

    assert support._pattern_verbose_regression_correctness_case_signature(case) == (
        "pattern.fullmatch",
        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        ("KEY = ABC",),
        (),
        72,
        "str",
    )


def test_pattern_boundary_wrong_text_model_selector_accepts_exact_trio_and_signature_shape() -> None:
    workload = synthetic_workload(
        manifest_id="pattern-boundary",
        workload_id="pattern.search-wrong-text-model",
        operation="pattern.search",
        text_model="str",
        haystack_text_model="bytes",
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
    )

    assert support._is_pattern_boundary_wrong_text_model_workload(workload)
    assert support._pattern_boundary_wrong_text_model_workload_signature(
        workload
    ) == (
        "pattern.search",
        "abc",
        (b"abc",),
        (),
        0,
        "str",
    )


def test_pattern_boundary_wrong_text_model_selector_rejects_compiled_pattern_window_and_keyword_rows() -> None:
    compiled_pattern_workload = SimpleNamespace(
        workload_id="pattern-search-compiled-pattern",
        operation="pattern.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        kwargs={},
        pos=None,
        endpos=None,
    )
    keyword_workload = SimpleNamespace(
        workload_id="pattern-search-keyword",
        operation="pattern.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=False,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        kwargs={"pos": 1},
        pos=None,
        endpos=None,
    )
    windowed_workload = SimpleNamespace(
        workload_id="pattern-search-window",
        operation="pattern.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=False,
        expected_exception={
            "type": "TypeError",
            "message_substring": "wrong text model",
        },
        kwargs={},
        pos=0,
        endpos=None,
    )

    assert not support._is_pattern_boundary_wrong_text_model_workload(
        compiled_pattern_workload
    )
    assert not support._is_pattern_boundary_wrong_text_model_workload(keyword_workload)
    assert not support._is_pattern_boundary_wrong_text_model_workload(windowed_workload)


def test_pattern_boundary_wrong_text_model_correctness_case_signatures_cover_str_and_bytes_rows() -> None:
    str_case = _pattern_case(
        case_id="workflow-pattern-search-str-wrong-text-model",
        helper="search",
        args=(b"abc",),
        pattern="abc",
        flags=0,
        text_model="str",
    )
    bytes_case = _pattern_case(
        case_id="workflow-pattern-match-bytes-wrong-text-model",
        helper="match",
        args=("abc",),
        pattern="abc",
        flags=0,
        text_model="bytes",
    )
    wrong_haystack_type = _pattern_case(
        case_id="workflow-pattern-fullmatch-str-not-wrong-text-model",
        helper="fullmatch",
        args=("abc",),
        pattern="abc",
        flags=0,
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
