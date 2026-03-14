from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import re

import pytest

import rebar


@dataclass(frozen=True)
class Scenario:
    id: str
    pattern: str
    max_group: int
    group_names: tuple[str, ...] = ()
    search_misses: tuple[str, ...] = ()
    fullmatch_misses: tuple[str, ...] = ()


@dataclass(frozen=True)
class BacktrackingTraceCase:
    id: str
    pattern: str
    max_group: int
    group_names: tuple[str, ...] = ()
    search_text: str = ""
    fullmatch_text: str = ""


_MISSING_GROUP_DEFAULT = object()
_BACKTRACKING_BRANCH_TEXT = {
    "short": "b",
    "long": "bc",
}


SCENARIOS = (
    Scenario(
        id="quantified-alternation-backtracking-heavy-numbered",
        pattern=r"a(b|bc){1,2}d",
        max_group=1,
        search_misses=("zzadzz", "zzabccdzz"),
        fullmatch_misses=("ad", "abccd"),
    ),
    Scenario(
        id="quantified-alternation-backtracking-heavy-named",
        pattern=r"a(?P<word>b|bc){1,2}d",
        max_group=1,
        group_names=("word",),
        search_misses=("zzadzz", "zzabccdzz"),
        fullmatch_misses=("ad", "abccd"),
    ),
)


def _build_backtracking_trace_cases() -> tuple[BacktrackingTraceCase, ...]:
    cases: list[BacktrackingTraceCase] = []
    for scenario in SCENARIOS:
        for repetition_count in range(1, 3):
            for branch_order in product(("short", "long"), repeat=repetition_count):
                body = "".join(_BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    BacktrackingTraceCase(
                        id=f"{scenario.id}-{branch_id}",
                        pattern=scenario.pattern,
                        max_group=scenario.max_group,
                        group_names=scenario.group_names,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


TRACE_CASES = _build_backtracking_trace_cases()


def _assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str],
    *,
    max_group: int,
    group_names: tuple[str, ...],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    group_indexes = tuple(range(max_group + 1))

    assert observed.group(0) == expected.group(0)
    assert observed.group(*group_indexes) == expected.group(*group_indexes)

    for group_index in range(1, max_group + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groups(_MISSING_GROUP_DEFAULT) == expected.groups(_MISSING_GROUP_DEFAULT)
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(_MISSING_GROUP_DEFAULT) == expected.groupdict(
        _MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.span() == expected.span()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    assert observed.re.pattern == expected.re.pattern
    assert observed.re.flags == expected.re.flags
    assert observed.re.groups == expected.re.groups
    assert observed.re.groupindex == expected.re.groupindex

    for group_name in group_names:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


@pytest.mark.parametrize("case", SCENARIOS, ids=lambda case: case.id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: Scenario,
) -> None:
    _, backend = regex_backend

    observed = backend.compile(case.pattern)
    expected = re.compile(case.pattern)

    assert observed is backend.compile(case.pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


@pytest.mark.parametrize("case", TRACE_CASES, ids=lambda case: case.id)
def test_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(
        backend_name,
        observed,
        expected,
        max_group=case.max_group,
        group_names=case.group_names,
    )


@pytest.mark.parametrize("case", SCENARIOS, ids=lambda case: case.id)
def test_module_search_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: Scenario,
) -> None:
    _, backend = regex_backend

    for text in case.search_misses:
        assert backend.search(case.pattern, text) is None
        assert re.search(case.pattern, text) is None


@pytest.mark.parametrize("case", TRACE_CASES, ids=lambda case: case.id)
def test_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    observed = observed_pattern.fullmatch(case.fullmatch_text)
    expected = expected_pattern.fullmatch(case.fullmatch_text)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(
        backend_name,
        observed,
        expected,
        max_group=case.max_group,
        group_names=case.group_names,
    )


@pytest.mark.parametrize("case", SCENARIOS, ids=lambda case: case.id)
def test_pattern_fullmatch_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: Scenario,
) -> None:
    _, backend = regex_backend
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    for text in case.fullmatch_misses:
        assert observed_pattern.fullmatch(text) is None
        assert expected_pattern.fullmatch(text) is None
