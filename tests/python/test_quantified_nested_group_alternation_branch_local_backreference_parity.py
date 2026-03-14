from __future__ import annotations

import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


NUMBERED_PATTERN = r"a((b|c)+)\2d"
NAMED_PATTERN = r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"
COMPILE_CASES = (
    pytest.param(NUMBERED_PATTERN, id="numbered-compile"),
    pytest.param(NAMED_PATTERN, id="named-compile"),
)
WORKFLOW_CASES = (
    pytest.param(
        "module",
        NUMBERED_PATTERN,
        "search",
        "zzabbdzz",
        id="module-numbered-search-lower-bound-b-branch",
    ),
    pytest.param(
        "pattern",
        NUMBERED_PATTERN,
        "fullmatch",
        "abbbd",
        id="pattern-numbered-fullmatch-repeated-b-branch",
    ),
    pytest.param(
        "pattern",
        NUMBERED_PATTERN,
        "fullmatch",
        "abccd",
        id="pattern-numbered-fullmatch-repeated-mixed-branch",
    ),
    pytest.param(
        "module",
        NAMED_PATTERN,
        "search",
        "zzaccdzz",
        id="module-named-search-lower-bound-c-branch",
    ),
    pytest.param(
        "pattern",
        NAMED_PATTERN,
        "fullmatch",
        "abbbd",
        id="pattern-named-fullmatch-repeated-b-branch",
    ),
    pytest.param(
        "pattern",
        NAMED_PATTERN,
        "fullmatch",
        "acbbd",
        id="pattern-named-fullmatch-repeated-mixed-branch",
    ),
)
NEGATIVE_CASES = (
    pytest.param(
        "module",
        NUMBERED_PATTERN,
        "search",
        "zzabcdzz",
        id="module-numbered-search-miss-mismatched-replay",
    ),
    pytest.param(
        "pattern",
        NUMBERED_PATTERN,
        "fullmatch",
        "acbd",
        id="pattern-numbered-fullmatch-miss-short-replay",
    ),
    pytest.param(
        "module",
        NAMED_PATTERN,
        "search",
        "zzacbdzz",
        id="module-named-search-miss-short-replay",
    ),
    pytest.param(
        "pattern",
        NAMED_PATTERN,
        "fullmatch",
        "abcd",
        id="pattern-named-fullmatch-miss-mismatched-replay",
    ),
)
MISSING_GROUP_DEFAULT = object()


def _assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str] | re.Pattern[bytes],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Pattern
    else:
        assert type(observed) is type(expected)

    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


def _assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    group_indexes = tuple(range(expected.re.groups + 1))

    assert observed.group(0) == expected.group(0)
    assert observed.group(*group_indexes) == expected.group(*group_indexes)

    for group_index in range(1, expected.re.groups + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groups(MISSING_GROUP_DEFAULT) == expected.groups(MISSING_GROUP_DEFAULT)
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(MISSING_GROUP_DEFAULT) == expected.groupdict(
        MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.span() == expected.span()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    assert hasattr(observed, "regs") == hasattr(expected, "regs")
    if hasattr(expected, "regs"):
        assert tuple(observed.regs) == tuple(expected.regs)

    _assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def _assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    for group_index in range(expected.re.groups + 1):
        assert observed[group_index] == expected[group_index]

    ordered_group_names = tuple(expected.re.groupindex)
    for group_name in ordered_group_names:
        assert observed[group_name] == expected[group_name]

    templates = [r"<\g<0>>"]
    if expected.re.groups >= 1:
        templates.append(r"<\1>")
    if expected.re.groups >= 2:
        templates.append(r"<\1:\2>")
    if ordered_group_names:
        templates.append(
            "<" + ":".join(fr"\g<{group_name}>" for group_name in ordered_group_names) + ">"
        )

    for template in templates:
        assert observed.expand(template) == expected.expand(template)


@pytest.mark.parametrize("pattern", COMPILE_CASES)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.compile(pattern)
    expected = re.compile(pattern)

    assert observed is backend.compile(pattern)
    _assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize(("target", "pattern", "helper", "text"), WORKFLOW_CASES)
def test_supported_success_paths_match_cpython(
    regex_backend: tuple[str, object],
    target: str,
    pattern: str,
    helper: str,
    text: str,
) -> None:
    backend_name, backend = regex_backend

    if target == "module":
        observed = getattr(backend, helper)(pattern, text)
        expected = getattr(re, helper)(pattern, text)
    else:
        observed_pattern = backend.compile(pattern)
        expected_pattern = re.compile(pattern)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, helper)(text)
        expected = getattr(expected_pattern, helper)(text)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(backend_name, observed, expected)
    _assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(("target", "pattern", "helper", "text"), NEGATIVE_CASES)
def test_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    target: str,
    pattern: str,
    helper: str,
    text: str,
) -> None:
    backend_name, backend = regex_backend

    if target == "module":
        observed = getattr(backend, helper)(pattern, text)
        expected = getattr(re, helper)(pattern, text)
    else:
        observed_pattern = backend.compile(pattern)
        expected_pattern = re.compile(pattern)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, helper)(text)
        expected = getattr(expected_pattern, helper)(text)

    assert observed is None
    assert expected is None
