from __future__ import annotations

from collections import Counter
import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_group_alternation_workflows.py"
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest


FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(FIXTURE_PATH)
EXPECTED_CASE_IDS = {
    "nested-group-alternation-compile-metadata-str",
    "nested-group-alternation-module-search-str",
    "nested-group-alternation-pattern-fullmatch-str",
    "named-nested-group-alternation-compile-metadata-str",
    "named-nested-group-alternation-module-search-str",
    "named-nested-group-alternation-pattern-fullmatch-str",
}
EXPECTED_COMPILE_PATTERNS = {
    r"a((b|c))d",
    r"a(?P<outer>(?P<inner>b|c))d",
}
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 2,
        ("pattern_call", "fullmatch"): 2,
    }
)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
WORKFLOW_CASES = tuple(case for case in PUBLISHED_CASES if case.operation != "compile")
NEGATIVE_CASES = (
    pytest.param(
        "module",
        r"a((b|c))d",
        "search",
        "zzadzz",
        id="module-numbered-search-miss-too-short",
    ),
    pytest.param(
        "module",
        r"a((b|c))d",
        "search",
        "zzabbdzz",
        id="module-numbered-search-miss-extra-branch",
    ),
    pytest.param(
        "pattern",
        r"a((b|c))d",
        "fullmatch",
        "ad",
        id="pattern-numbered-fullmatch-miss-too-short",
    ),
    pytest.param(
        "pattern",
        r"a((b|c))d",
        "fullmatch",
        "abbd",
        id="pattern-numbered-fullmatch-miss-extra-branch",
    ),
    pytest.param(
        "module",
        r"a(?P<outer>(?P<inner>b|c))d",
        "search",
        "zzadzz",
        id="module-named-search-miss-too-short",
    ),
    pytest.param(
        "module",
        r"a(?P<outer>(?P<inner>b|c))d",
        "search",
        "zzaccddzz",
        id="module-named-search-miss-extra-branch",
    ),
    pytest.param(
        "pattern",
        r"a(?P<outer>(?P<inner>b|c))d",
        "fullmatch",
        "ad",
        id="pattern-named-fullmatch-miss-too-short",
    ),
    pytest.param(
        "pattern",
        r"a(?P<outer>(?P<inner>b|c))d",
        "fullmatch",
        "accd",
        id="pattern-named-fullmatch-miss-extra-branch",
    ),
)
MISSING_GROUP_DEFAULT = object()


def _case_pattern(case: FixtureCase) -> str | bytes:
    if case.pattern is not None:
        return case.pattern_payload()
    return case.args[0]


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


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert FIXTURE_MANIFEST.manifest_id == "nested-group-alternation-workflows"
    assert len(PUBLISHED_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in PUBLISHED_CASES} == EXPECTED_CASE_IDS
    assert {_case_pattern(case) for case in PUBLISHED_CASES} == EXPECTED_COMPILE_PATTERNS
    assert Counter((case.operation, case.helper) for case in PUBLISHED_CASES) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.compile(case.pattern_payload(), case.flags or 0)
    expected = re.compile(case.pattern_payload(), case.flags or 0)

    assert observed is backend.compile(case.pattern_payload(), case.flags or 0)
    _assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", WORKFLOW_CASES, ids=lambda case: case.case_id)
def test_published_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    if case.operation == "module_call":
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)
    else:
        observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
        expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(("target", "pattern", "helper", "text"), NEGATIVE_CASES)
def test_negative_paths_match_cpython(
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
