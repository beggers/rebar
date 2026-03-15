from __future__ import annotations

from dataclasses import dataclass
import re

import pytest

import rebar


@dataclass(frozen=True)
class ParityCase:
    id: str
    pattern: str
    max_group: int
    module_helper: str
    pattern_helper: str
    group_names: tuple[str, ...] = ()
    module_matches: tuple[str, ...] = ()
    module_misses: tuple[str, ...] = ()
    pattern_matches: tuple[str, ...] = ()
    pattern_misses: tuple[str, ...] = ()


CASES = (
    ParityCase(
        id="numbered-two-capture-fullmatch",
        pattern=r"(ab)(c)",
        max_group=2,
        module_helper="fullmatch",
        pattern_helper="fullmatch",
        module_matches=("abc",),
        module_misses=("ab", "abcz"),
        pattern_matches=("abc",),
        pattern_misses=("ab", "abcz"),
    ),
    ParityCase(
        id="named-single-capture-search",
        pattern=r"(?P<word>abc)",
        max_group=1,
        module_helper="search",
        pattern_helper="search",
        group_names=("word",),
        module_matches=("zzabczz",),
        module_misses=("zzz",),
        pattern_matches=("zzabczz",),
        pattern_misses=("zzz",),
    ),
    ParityCase(
        id="numbered-optional-group-search-and-fullmatch",
        pattern=r"a(b)?d",
        max_group=1,
        module_helper="search",
        pattern_helper="fullmatch",
        module_matches=("zzabdzz",),
        module_misses=("zzz",),
        pattern_matches=("ad",),
        pattern_misses=("abdd",),
    ),
    ParityCase(
        id="named-optional-group-search-and-fullmatch",
        pattern=r"a(?P<word>b)?d",
        max_group=1,
        module_helper="search",
        pattern_helper="fullmatch",
        group_names=("word",),
        module_matches=("zzadzz",),
        module_misses=("zzz",),
        pattern_matches=("abd",),
        pattern_misses=("abdd",),
    ),
    ParityCase(
        id="numbered-nested-group-search-and-fullmatch",
        pattern=r"a((b))d",
        max_group=2,
        module_helper="search",
        pattern_helper="fullmatch",
        module_matches=("zzabdzz",),
        module_misses=("zzz",),
        pattern_matches=("abd",),
        pattern_misses=("abdd",),
    ),
    ParityCase(
        id="named-nested-group-search-and-fullmatch",
        pattern=r"a(?P<outer>(?P<inner>b))d",
        max_group=2,
        module_helper="search",
        pattern_helper="fullmatch",
        group_names=("outer", "inner"),
        module_matches=("zzabdzz",),
        module_misses=("zzz",),
        pattern_matches=("abd",),
        pattern_misses=("abdd",),
    ),
)


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

    assert observed.group(0) == expected.group(0)
    assert observed.group(*range(max_group + 1)) == expected.group(*range(max_group + 1))
    for group_index in range(1, max_group + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groupdict() == expected.groupdict()
    assert observed.span() == expected.span()
    assert observed.start() == expected.start()
    assert observed.end() == expected.end()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup

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

    templates = [r"<\g<0>>"]
    if max_group >= 1:
        templates.append(r"<\1>")
    if max_group >= 2:
        templates.append(r"<\2:\1>")
    for group_name in group_names:
        templates.append(fr"<\g<{group_name}>>")

    for template in templates:
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
def test_module_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    backend_name, backend = regex_backend

    module_helper = getattr(backend, case.module_helper)
    cpython_helper = getattr(re, case.module_helper)
    for text in case.module_matches:
        observed = module_helper(case.pattern, text)
        expected = cpython_helper(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_parity(
            backend_name,
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_module_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    _, backend = regex_backend

    module_helper = getattr(backend, case.module_helper)
    cpython_helper = getattr(re, case.module_helper)
    for text in case.module_misses:
        assert module_helper(case.pattern, text) is None
        assert cpython_helper(case.pattern, text) is None


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_pattern_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    backend_name, backend = regex_backend

    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)
    pattern_helper = getattr(observed_pattern, case.pattern_helper)
    cpython_helper = getattr(expected_pattern, case.pattern_helper)

    for text in case.pattern_matches:
        observed = pattern_helper(text)
        expected = cpython_helper(text)

        assert observed is not None
        assert expected is not None
        _assert_match_parity(
            backend_name,
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_module_helper_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    _, backend = regex_backend

    module_helper = getattr(backend, case.module_helper)
    cpython_helper = getattr(re, case.module_helper)
    for text in case.module_matches:
        observed = module_helper(case.pattern, text)
        expected = cpython_helper(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_convenience_api_parity(
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_pattern_helper_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    _, backend = regex_backend

    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)
    pattern_helper = getattr(observed_pattern, case.pattern_helper)
    cpython_helper = getattr(expected_pattern, case.pattern_helper)

    for text in case.pattern_matches:
        observed = pattern_helper(text)
        expected = cpython_helper(text)

        assert observed is not None
        assert expected is not None
        _assert_match_convenience_api_parity(
            observed,
            expected,
            max_group=case.max_group,
            group_names=case.group_names,
        )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_pattern_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: ParityCase,
) -> None:
    _, backend = regex_backend

    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)
    pattern_helper = getattr(observed_pattern, case.pattern_helper)
    cpython_helper = getattr(expected_pattern, case.pattern_helper)

    for text in case.pattern_misses:
        assert pattern_helper(text) is None
        assert cpython_helper(text) is None
