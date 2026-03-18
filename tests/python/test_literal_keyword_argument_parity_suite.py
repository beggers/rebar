from __future__ import annotations

from dataclasses import dataclass
import re

import pytest

from tests.python.fixture_parity_support import (
    assert_finditer_parity,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    compile_with_cpython_parity,
)


@dataclass(frozen=True)
class ModuleKeywordCallCase:
    case_id: str
    helper: str
    args: tuple[object, ...]
    kwargs: dict[str, object]
    result_kind: str


@dataclass(frozen=True)
class PatternKeywordCallCase:
    case_id: str
    helper: str
    pattern: str | bytes
    args: tuple[object, ...]
    kwargs: dict[str, object]
    result_kind: str
    flags: int = 0


@dataclass(frozen=True)
class ModuleKeywordErrorCase:
    case_id: str
    helper: str
    args: tuple[object, ...]
    kwargs: dict[str, object]


MODULE_KEYWORD_CALL_CASES = (
    ModuleKeywordCallCase(
        case_id="module-search-flags-keyword-str",
        helper="search",
        args=("abc", "zAbc"),
        kwargs={"flags": int(re.IGNORECASE)},
        result_kind="match",
    ),
    ModuleKeywordCallCase(
        case_id="module-match-flags-keyword-bytes",
        helper="match",
        args=(b"abc", b"Abc"),
        kwargs={"flags": int(re.IGNORECASE)},
        result_kind="match",
    ),
    ModuleKeywordCallCase(
        case_id="module-fullmatch-flags-keyword-str",
        helper="fullmatch",
        args=("abc", "Abc"),
        kwargs={"flags": int(re.IGNORECASE)},
        result_kind="match",
    ),
    ModuleKeywordCallCase(
        case_id="module-split-maxsplit-keyword-bytes",
        helper="split",
        args=(b"abc", b"zabczabc"),
        kwargs={"maxsplit": 1},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-sub-count-keyword-str",
        helper="sub",
        args=("abc", "x", "abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-subn-count-keyword-bytes",
        helper="subn",
        args=(b"abc", b"x", b"abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
)

PATTERN_KEYWORD_CALL_CASES = (
    PatternKeywordCallCase(
        case_id="pattern-search-pos-keyword-str",
        helper="search",
        pattern="abc",
        args=("zabcabc",),
        kwargs={"pos": 2},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-search-bool-endpos-keyword-str",
        helper="search",
        pattern="z",
        args=("zabcabc",),
        kwargs={"endpos": True},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-search-endpos-keyword-bytes",
        helper="search",
        pattern=b"abc",
        args=(b"zabcabc",),
        kwargs={"endpos": 4},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-match-pos-keyword-str",
        helper="match",
        pattern="abc",
        args=("zabcabc",),
        kwargs={"pos": 1},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-match-bool-pos-keyword-str",
        helper="match",
        pattern="abc",
        args=("zabcabc",),
        kwargs={"pos": True},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-fullmatch-window-keyword-bytes",
        helper="fullmatch",
        pattern=b"abc",
        args=(b"zabc",),
        kwargs={"pos": 1, "endpos": 4},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-findall-window-keyword-str",
        helper="findall",
        pattern="abc",
        args=("zabcabcz",),
        kwargs={"pos": 1, "endpos": 7},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-findall-bool-window-keyword-str",
        helper="findall",
        pattern="abc",
        args=("zabcabcz",),
        kwargs={"pos": True, "endpos": 7},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-finditer-window-keyword-bytes",
        helper="finditer",
        pattern=b"abc",
        args=(b"zabcabcz",),
        kwargs={"pos": 1, "endpos": 7},
        result_kind="iter",
    ),
    PatternKeywordCallCase(
        case_id="pattern-finditer-bool-window-keyword-bytes",
        helper="finditer",
        pattern=b"abc",
        args=(b"zabcabcz",),
        kwargs={"pos": True, "endpos": 7},
        result_kind="iter",
    ),
    PatternKeywordCallCase(
        case_id="pattern-split-maxsplit-keyword-str",
        helper="split",
        pattern="abc",
        args=("zabczabc",),
        kwargs={"maxsplit": 1},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-sub-count-keyword-bytes",
        helper="sub",
        pattern=b"abc",
        args=(b"x", b"abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-subn-count-keyword-str",
        helper="subn",
        pattern="abc",
        args=("x", "abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
)

MODULE_KEYWORD_ERROR_CASES = (
    ModuleKeywordErrorCase(
        case_id="module-search-duplicate-flags-keyword",
        helper="search",
        args=("abc", "abc", 0),
        kwargs={"flags": 0},
    ),
    ModuleKeywordErrorCase(
        case_id="module-split-duplicate-maxsplit-keyword",
        helper="split",
        args=("abc", "abc", 1),
        kwargs={"maxsplit": 1},
    ),
    ModuleKeywordErrorCase(
        case_id="module-sub-duplicate-count-keyword",
        helper="sub",
        args=("abc", "x", "abc", 1),
        kwargs={"count": 1},
    ),
    ModuleKeywordErrorCase(
        case_id="module-fullmatch-unexpected-keyword",
        helper="fullmatch",
        args=("abc", "abc"),
        kwargs={"missing": 1},
    ),
    ModuleKeywordErrorCase(
        case_id="module-sub-unexpected-keyword",
        helper="sub",
        args=("abc", "x", "abc"),
        kwargs={"missing": 1},
    ),
)


def _call_module_case(regex_api: object, case: ModuleKeywordCallCase) -> object:
    return getattr(regex_api, case.helper)(*case.args, **case.kwargs)


def _call_pattern_case(pattern: object, case: PatternKeywordCallCase) -> object:
    return getattr(pattern, case.helper)(*case.args, **case.kwargs)


def _capture_error(callback) -> BaseException:
    try:
        callback()
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError("expected call to raise")


@pytest.mark.parametrize("case", MODULE_KEYWORD_CALL_CASES, ids=lambda case: case.case_id)
def test_module_keyword_argument_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: ModuleKeywordCallCase,
) -> None:
    backend_name, backend = regex_backend
    observed = _call_module_case(backend, case)
    expected = _call_module_case(re, case)

    if case.result_kind == "match":
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)
        return

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_KEYWORD_CALL_CASES, ids=lambda case: case.case_id)
def test_pattern_keyword_argument_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: PatternKeywordCallCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    observed = _call_pattern_case(observed_pattern, case)
    expected = _call_pattern_case(expected_pattern, case)

    if case.result_kind == "match":
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)
        return

    if case.result_kind == "iter":
        assert_finditer_parity(backend_name, observed, expected, check_regs=True)
        return

    assert observed == expected


@pytest.mark.parametrize("case", MODULE_KEYWORD_ERROR_CASES, ids=lambda case: case.case_id)
def test_module_keyword_argument_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: ModuleKeywordErrorCase,
) -> None:
    _, backend = regex_backend

    observed_error = _capture_error(
        lambda: getattr(backend, case.helper)(*case.args, **case.kwargs)
    )
    expected_error = _capture_error(
        lambda: getattr(re, case.helper)(*case.args, **case.kwargs)
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args
