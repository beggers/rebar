from __future__ import annotations

from dataclasses import dataclass
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


SCENARIOS = (
    Scenario(
        id="broader-range-conditional-numbered",
        pattern=r"a((bc|de){1,4})?(?(1)d|e)",
        max_group=2,
        search_matches=(
            "zzaezz",
            "zzabcdzz",
            "zzadedzz",
            "zzabcdedededzz",
        ),
        search_misses=(
            "zzadzz",
            "zzabcbcbcbcbcdzz",
        ),
        fullmatch_matches=(
            "ae",
            "abcded",
            "abcbcded",
            "abcdededed",
        ),
        fullmatch_misses=(
            "ad",
            "abcdede",
            "abcbcbcbcbcd",
        ),
    ),
    Scenario(
        id="broader-range-conditional-named",
        pattern=r"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        max_group=2,
        group_names=("outer",),
        search_matches=(
            "zzaezz",
            "zzabcdzz",
            "zzadedzz",
            "zzabcdedededzz",
        ),
        search_misses=(
            "zzadzz",
            "zzabcbcbcbcbcdzz",
        ),
        fullmatch_matches=(
            "ae",
            "abcded",
            "abcbcded",
            "abcdededed",
        ),
        fullmatch_misses=(
            "ad",
            "abcdede",
            "abcbcbcbcbcd",
        ),
    ),
)


def _encode_values(values: tuple[str, ...]) -> tuple[bytes, ...]:
    return tuple(value.encode("ascii") for value in values)


def _parity_case(
    scenario: Scenario,
    *,
    text_model: str,
) -> ParityCase:
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
        )
    raise AssertionError(f"unsupported text_model {text_model!r}")


CASES = tuple(
    _parity_case(scenario, text_model=text_model)
    for scenario in SCENARIOS
    for text_model in ("str", "bytes")
)


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
    for group_index in range(1, max_group + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groupdict() == expected.groupdict()
    assert observed.span() == expected.span()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup

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
