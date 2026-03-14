from __future__ import annotations

from dataclasses import dataclass
import re

import pytest

import rebar


_MISSING_GROUP_DEFAULT = object()


@dataclass(frozen=True)
class ParityCase:
    id: str
    pattern: str
    max_group: int
    group_names: tuple[str, ...] = ()
    search_matches: tuple[str, ...] = ()
    search_misses: tuple[str, ...] = ()
    fullmatch_matches: tuple[str, ...] = ()
    fullmatch_misses: tuple[str, ...] = ()


CASES = (
    ParityCase(
        id="open-ended-alternation-numbered",
        pattern=r"a(bc|de){1,}d",
        max_group=1,
        search_matches=("zzabcdzz", "zzadedzz"),
        fullmatch_matches=("abcbcd", "abcbcded"),
        fullmatch_misses=("ad", "abed"),
    ),
    ParityCase(
        id="open-ended-alternation-named",
        pattern=r"a(?P<word>bc|de){1,}d",
        max_group=1,
        group_names=("word",),
        search_matches=("zzabcdzz", "zzadedzz"),
        fullmatch_matches=("abcded", "abcbcded", "adededed"),
        fullmatch_misses=("ad", "abed"),
    ),
    ParityCase(
        id="open-ended-conditional-numbered",
        pattern=r"a((bc|de){1,})?(?(1)d|e)",
        max_group=2,
        search_matches=("zzaezz", "zzabcdzz", "zzadedzz"),
        fullmatch_matches=("abcded", "abcbcded"),
        fullmatch_misses=("abcde",),
    ),
    ParityCase(
        id="open-ended-conditional-named",
        pattern=r"a(?P<outer>(bc|de){1,})?(?(outer)d|e)",
        max_group=2,
        group_names=("outer",),
        search_matches=("zzaezz", "zzadedzz", "zzadedededzz"),
        fullmatch_matches=("abcbcded",),
        fullmatch_misses=("ad",),
    ),
    ParityCase(
        id="open-ended-backtracking-numbered",
        pattern=r"a((bc|b)c){1,}d",
        max_group=2,
        search_matches=("zzabcdzz",),
        fullmatch_matches=("abccd", "abcbcd", "abcbccd"),
        fullmatch_misses=("abcccd",),
    ),
    ParityCase(
        id="open-ended-backtracking-named",
        pattern=r"a(?P<word>(bc|b)c){1,}d",
        max_group=2,
        group_names=("word",),
        search_matches=("zzabccdzz", "zzabcbccbcdzz", "zzabccbcdzz"),
        search_misses=("zzabccbdzz",),
        fullmatch_matches=("abcbcbcbcd",),
    ),
    ParityCase(
        id="broader-range-open-ended-alternation-numbered",
        pattern=r"a(bc|de){2,}d",
        max_group=1,
        search_matches=("zzabcbcdzz", "zzadededzz"),
        fullmatch_matches=("abcded", "abcbcded", "adededed"),
        fullmatch_misses=("abcd", "ad"),
    ),
    ParityCase(
        id="broader-range-open-ended-alternation-named",
        pattern=r"a(?P<word>bc|de){2,}d",
        max_group=1,
        group_names=("word",),
        search_matches=("zzabcbcdzz", "zzadededzz"),
        fullmatch_matches=("abcded", "abcbcded", "adededed"),
        fullmatch_misses=("abcd", "ad"),
    ),
    ParityCase(
        id="broader-range-open-ended-conditional-numbered",
        pattern=r"a((bc|de){2,})?(?(1)d|e)",
        max_group=2,
        search_matches=("zzaezz", "zzabcbcdzz", "zzadededzz"),
        fullmatch_matches=("abcded", "abcbcded"),
        fullmatch_misses=("abcdede", "abcd"),
    ),
    ParityCase(
        id="broader-range-open-ended-conditional-named",
        pattern=r"a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
        max_group=2,
        group_names=("outer",),
        search_matches=("zzaezz", "zzadededzz", "zzadedededzz"),
        fullmatch_matches=("abcbcded",),
        fullmatch_misses=("ad",),
    ),
    ParityCase(
        id="broader-range-open-ended-backtracking-numbered",
        pattern=r"a((bc|b)c){2,}d",
        max_group=2,
        search_matches=("zzabcbcdzz", "zzabcbccdzz"),
        fullmatch_matches=("abccbcd", "abcbcbcbcd"),
        fullmatch_misses=("abcd", "abccbd"),
    ),
    ParityCase(
        id="broader-range-open-ended-backtracking-named",
        pattern=r"a(?P<word>(bc|b)c){2,}d",
        max_group=2,
        group_names=("word",),
        search_matches=("zzabccbcdzz", "zzabcbcbcbcdzz"),
        search_misses=("zzabccbdzz",),
        fullmatch_matches=("abcbccd",),
        fullmatch_misses=("abcd",),
    ),
    ParityCase(
        id="nested-open-ended-alternation-numbered",
        pattern=r"a((bc|de){1,})d",
        max_group=2,
        search_matches=("zzabcdzz", "zzadedzz"),
        fullmatch_matches=("abcbcded", "adededed"),
        fullmatch_misses=("ae", "abcbcdede"),
    ),
    ParityCase(
        id="nested-open-ended-alternation-named",
        pattern=r"a(?P<outer>(bc|de){1,})d",
        max_group=2,
        group_names=("outer",),
        search_matches=("zzabcdzz", "zzadedzz"),
        fullmatch_matches=("abcbcded", "adededed"),
        fullmatch_misses=("ae", "abcbcdede"),
    ),
)


def _match_api_templates(
    *,
    max_group: int,
    group_names: tuple[str, ...],
) -> tuple[str, ...]:
    templates = [r"<\g<0>>"]
    if max_group >= 1:
        templates.append(
            "<" + "|".join(f"\\{group_index}" for group_index in range(1, max_group + 1)) + ">"
        )
        templates.append(
            "<"
            + "|".join(f"\\g<{group_index}>" for group_index in range(max_group + 1))
            + ">"
        )
    for group_name in group_names:
        templates.append(fr"<\g<{group_name}>>")
    return tuple(templates)


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
    assert observed.start() == expected.start()
    assert observed.end() == expected.end()
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


def _assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str],
    *,
    max_group: int,
    group_names: tuple[str, ...],
) -> None:
    for group_index in range(max_group + 1):
        assert observed[group_index] == expected[group_index]

    for group_name in group_names:
        assert observed[group_name] == expected[group_name]

    for template in _match_api_templates(
        max_group=max_group,
        group_names=group_names,
    ):
        assert observed.expand(template) == expected.expand(template)


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
def test_module_search_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_convenience_api_parity(
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )


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


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_pattern_fullmatch_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    _, backend = regex_backend
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        _assert_match_convenience_api_parity(
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )
