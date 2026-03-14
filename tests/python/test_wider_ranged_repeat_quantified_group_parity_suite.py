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
    search_matches: tuple[str, ...] = ()
    search_misses: tuple[str, ...] = ()
    fullmatch_matches: tuple[str, ...] = ()
    fullmatch_misses: tuple[str, ...] = ()
    text_models: tuple[str, ...] = ("str",)
    bytes_unsupported_backends: tuple[str, ...] = ()
    bytes_unsupported_backend_reason: str | None = None


@dataclass(frozen=True)
class ParityCase:
    id: str
    pattern: str | bytes
    max_group: int
    group_names: tuple[str, ...] = ()
    search_matches: tuple[str | bytes, ...] = ()
    search_misses: tuple[str | bytes, ...] = ()
    fullmatch_matches: tuple[str | bytes, ...] = ()
    fullmatch_misses: tuple[str | bytes, ...] = ()
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


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
    "short": "bc",
    "long": "bcc",
}


SCENARIOS = (
    Scenario(
        id="wider-ranged-repeat-numbered",
        pattern=r"a(bc){1,3}d",
        max_group=1,
        search_matches=("zzabcdzz",),
        fullmatch_matches=("abcbcbcd",),
    ),
    Scenario(
        id="wider-ranged-repeat-named",
        pattern=r"a(?P<word>bc){1,3}d",
        max_group=1,
        group_names=("word",),
        search_matches=("zzabcbcbcdzz",),
        fullmatch_matches=("abcd",),
    ),
    Scenario(
        id="wider-ranged-repeat-conditional-numbered",
        pattern=r"a((bc|de){1,3})?(?(1)d|e)",
        max_group=2,
        search_matches=("zzaezz", "zzabcdzz", "zzadedzz"),
        fullmatch_matches=("abcded",),
        fullmatch_misses=("abcde",),
    ),
    Scenario(
        id="wider-ranged-repeat-conditional-named",
        pattern=r"a(?P<outer>(bc|de){1,3})?(?(outer)d|e)",
        max_group=2,
        group_names=("outer",),
        search_matches=("zzaezz", "zzadedzz", "zzabcbcdedzz"),
        fullmatch_matches=("abcded",),
        fullmatch_misses=("ad",),
    ),
    Scenario(
        id="wider-ranged-repeat-backtracking-numbered",
        pattern=r"a((bc|b)c){1,3}d",
        max_group=2,
        search_matches=("zzabcdzz",),
        fullmatch_matches=("abccd", "abcbcd", "abcbccd"),
        fullmatch_misses=("abcccd",),
    ),
    Scenario(
        id="wider-ranged-repeat-backtracking-named",
        pattern=r"a(?P<word>(bc|b)c){1,3}d",
        max_group=2,
        group_names=("word",),
        search_matches=("zzabccdzz", "zzabcbccbccdzz"),
        search_misses=("zzabcccezz",),
        fullmatch_matches=("abccbcd", "abcbcbccd"),
    ),
    Scenario(
        id="broader-range-wider-ranged-repeat-numbered",
        pattern=r"a(bc|de){1,4}d",
        max_group=1,
        search_matches=("zzabcdzz", "zzadedzz"),
        fullmatch_matches=("abcbcded",),
        fullmatch_misses=("ad",),
    ),
    Scenario(
        id="broader-range-wider-ranged-repeat-named",
        pattern=r"a(?P<word>bc|de){1,4}d",
        max_group=1,
        group_names=("word",),
        search_matches=("zzabcbcdedzz", "zzadededededzz"),
        fullmatch_matches=("abcbcdeded",),
        fullmatch_misses=("abcbcbcbcbcd",),
    ),
    Scenario(
        id="broader-range-wider-ranged-repeat-backtracking-numbered",
        pattern=r"a((bc|b)c){1,4}d",
        max_group=2,
        search_matches=("zzabcdzz", "zzabccdzz", "zzabcbccdzz"),
        search_misses=("zzabccbdzz",),
        fullmatch_matches=("abcbccd", "abccbcd", "abcbccbccbcd"),
        fullmatch_misses=("abccbd", "abcbcbcbcbcd"),
    ),
    Scenario(
        id="broader-range-wider-ranged-repeat-backtracking-named",
        pattern=r"a(?P<word>(bc|b)c){1,4}d",
        max_group=2,
        group_names=("word",),
        search_matches=("zzabccdzz", "zzabcbccdzz", "zzabcbccbccbcdzz"),
        search_misses=("zzabccbdzz", "zzabcbcbcbcbcdzz"),
        fullmatch_matches=("abccbcd",),
        fullmatch_misses=("abccbd", "abcbcbcbcbcd"),
    ),
    Scenario(
        id="broader-range-wider-ranged-repeat-conditional-numbered",
        pattern=r"a((bc|de){1,4})?(?(1)d|e)",
        max_group=2,
        search_matches=("zzaezz", "zzabcdzz", "zzadedzz", "zzabcdedededzz"),
        search_misses=("zzadzz", "zzabcbcbcbcbcdzz"),
        fullmatch_matches=("ae", "abcded", "abcbcded", "abcdededed"),
        fullmatch_misses=("ad", "abcdede", "abcbcbcbcbcd"),
        text_models=("str", "bytes"),
        bytes_unsupported_backends=("rebar",),
        bytes_unsupported_backend_reason=(
            "rebar does not yet support broader-range wider-ranged-repeat "
            "grouped-conditional bytes parity"
        ),
    ),
    Scenario(
        id="broader-range-wider-ranged-repeat-conditional-named",
        pattern=r"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        max_group=2,
        group_names=("outer",),
        search_matches=("zzaezz", "zzabcdzz", "zzadedzz", "zzabcdedededzz"),
        search_misses=("zzadzz", "zzabcbcbcbcbcdzz"),
        fullmatch_matches=("ae", "abcded", "abcbcded", "abcdededed"),
        fullmatch_misses=("ad", "abcdede", "abcbcbcbcbcd"),
        text_models=("str", "bytes"),
        bytes_unsupported_backends=("rebar",),
        bytes_unsupported_backend_reason=(
            "rebar does not yet support broader-range wider-ranged-repeat "
            "grouped-conditional bytes parity"
        ),
    ),
)


def _encode_values(values: tuple[str, ...]) -> tuple[bytes, ...]:
    return tuple(value.encode("ascii") for value in values)


def _parity_case(scenario: Scenario, *, text_model: str) -> ParityCase:
    if text_model == "str":
        return ParityCase(
            id=f"{scenario.id}-str",
            pattern=scenario.pattern,
            max_group=scenario.max_group,
            group_names=scenario.group_names,
            search_matches=scenario.search_matches,
            search_misses=scenario.search_misses,
            fullmatch_matches=scenario.fullmatch_matches,
            fullmatch_misses=scenario.fullmatch_misses,
        )
    if text_model == "bytes":
        return ParityCase(
            id=f"{scenario.id}-bytes",
            pattern=scenario.pattern.encode("ascii"),
            max_group=scenario.max_group,
            group_names=scenario.group_names,
            search_matches=_encode_values(scenario.search_matches),
            search_misses=_encode_values(scenario.search_misses),
            fullmatch_matches=_encode_values(scenario.fullmatch_matches),
            fullmatch_misses=_encode_values(scenario.fullmatch_misses),
            unsupported_backends=scenario.bytes_unsupported_backends,
            unsupported_backend_reason=scenario.bytes_unsupported_backend_reason,
        )
    raise AssertionError(f"unsupported text_model {text_model!r}")


CASES = tuple(
    _parity_case(scenario, text_model=text_model)
    for scenario in SCENARIOS
    for text_model in scenario.text_models
)


def _build_broader_range_backtracking_trace_cases() -> tuple[BacktrackingTraceCase, ...]:
    cases: list[BacktrackingTraceCase] = []
    for variant, pattern, group_names in (
        (
            "numbered",
            r"a((bc|b)c){1,4}d",
            (),
        ),
        (
            "named",
            r"a(?P<word>(bc|b)c){1,4}d",
            ("word",),
        ),
    ):
        for repetition_count in range(1, 5):
            for branch_order in product(("short", "long"), repeat=repetition_count):
                body = "".join(_BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    BacktrackingTraceCase(
                        id=(
                            "broader-range-wider-ranged-repeat-backtracking-"
                            f"{variant}-{branch_id}"
                        ),
                        pattern=pattern,
                        max_group=2,
                        group_names=group_names,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


BROADER_RANGE_BACKTRACKING_TRACE_CASES = _build_broader_range_backtracking_trace_cases()


def _assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
    *,
    max_group: int,
    group_names: tuple[str, ...],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    assert observed.group(0) == expected.group(0)
    assert observed.group(*tuple(range(max_group + 1))) == expected.group(
        *tuple(range(max_group + 1))
    )
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


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    _, backend = regex_backend

    observed = backend.compile(case.pattern)
    expected = re.compile(case.pattern)

    assert observed is backend.compile(case.pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    backend_name, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_parity(
            backend_name,
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )

    for text in case.search_misses:
        assert backend.search(case.pattern, text) is None
        assert re.search(case.pattern, text) is None


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        _assert_match_parity(
            backend_name,
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )

    for text in case.fullmatch_misses:
        assert observed_pattern.fullmatch(text) is None
        assert expected_pattern.fullmatch(text) is None


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_BACKTRACKING_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_module_search_branch_traces_match_cpython(
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


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_BACKTRACKING_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_pattern_fullmatch_branch_traces_match_cpython(
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
