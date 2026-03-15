from __future__ import annotations

import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
REPLACEMENT_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "collection_replacement_workflows.py"
)
MATCH_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "grouped_match_workflows.py"
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest


REPLACEMENT_FIXTURE_MANIFEST, REPLACEMENT_FIXTURE_CASES = load_fixture_manifest(
    REPLACEMENT_FIXTURE_PATH
)
MATCH_FIXTURE_MANIFEST, MATCH_FIXTURE_CASES = load_fixture_manifest(MATCH_FIXTURE_PATH)
EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS = (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
)
REPLACEMENT_VARIANTS = (
    pytest.param(False, "sub", 1, 0, id="module-sub-single-match"),
    pytest.param(False, "sub", 2, 0, id="module-sub-repeated"),
    pytest.param(False, "subn", 2, 1, id="module-subn-first-match-only"),
    pytest.param(True, "sub", 1, 0, id="pattern-sub-single-match"),
    pytest.param(True, "sub", 2, 0, id="pattern-sub-repeated"),
    pytest.param(True, "subn", 2, 1, id="pattern-subn-first-match-only"),
)
MISSING_GROUP_DEFAULT = object()


def _replacement_case() -> FixtureCase:
    cases = [
        case
        for case in REPLACEMENT_FIXTURE_CASES
        if case.case_id == "module-sub-grouping-template"
    ]
    assert len(cases) == 1
    return cases[0]


def _match_case_by_id(case_id: str) -> FixtureCase:
    cases = [case for case in MATCH_FIXTURE_CASES if case.case_id == case_id]
    assert len(cases) == 1
    return cases[0]


GROUPED_TEMPLATE_CASE = _replacement_case()
GROUPED_SINGLE_CAPTURE_CASES = tuple(
    _match_case_by_id(case_id) for case_id in EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS
)


def _pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


def _replacement(case: FixtureCase) -> str:
    replacement_index = 1 if case.operation == "module_call" else 0
    replacement = case.args[replacement_index]
    assert isinstance(replacement, str)
    return replacement


def _single_match_string(case: FixtureCase) -> str:
    string_index = 2 if case.operation == "module_call" else 1
    string = case.args[string_index]
    assert isinstance(string, str)
    return string


def _assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str],
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
    expected: re.Match[str],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    assert observed.group() == expected.group()
    assert observed.group(0) == expected.group(0)
    assert observed.group(1) == expected.group(1)
    assert observed.group(0, 1) == expected.group(0, 1)
    assert observed[0] == expected[0]
    assert observed[1] == expected[1]
    assert observed.groups() == expected.groups()
    assert observed.groups(MISSING_GROUP_DEFAULT) == expected.groups(
        MISSING_GROUP_DEFAULT
    )
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(MISSING_GROUP_DEFAULT) == expected.groupdict(
        MISSING_GROUP_DEFAULT
    )
    assert observed.span() == expected.span()
    assert observed.span(1) == expected.span(1)
    assert observed.start() == expected.start()
    assert observed.start(1) == expected.start(1)
    assert observed.end() == expected.end()
    assert observed.end(1) == expected.end(1)
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    assert observed.expand(r"<\g<0>>") == expected.expand(r"<\g<0>>")
    assert observed.expand(r"<\1>") == expected.expand(r"<\1>")
    assert observed.expand(r"<\g<0>:\1>") == expected.expand(r"<\g<0>:\1>")
    assert hasattr(observed, "regs") == hasattr(expected, "regs")
    if hasattr(expected, "regs"):
        assert tuple(observed.regs) == tuple(expected.regs)

    _assert_pattern_parity(backend_name, observed.re, expected.re)


def test_grouped_literal_template_suite_stays_aligned_with_published_fixtures() -> None:
    assert REPLACEMENT_FIXTURE_MANIFEST.manifest_id == "collection-replacement-workflows"
    assert MATCH_FIXTURE_MANIFEST.manifest_id == "grouped-match-workflows"
    assert GROUPED_TEMPLATE_CASE.operation == "module_call"
    assert GROUPED_TEMPLATE_CASE.helper == "sub"
    assert _pattern(GROUPED_TEMPLATE_CASE) == "(abc)"
    assert _replacement(GROUPED_TEMPLATE_CASE) == r"\1x"
    assert _single_match_string(GROUPED_TEMPLATE_CASE) == "abc"
    assert "replacement-template" in GROUPED_TEMPLATE_CASE.categories
    assert "grouping-dependent" in GROUPED_TEMPLATE_CASE.categories

    assert tuple(case.case_id for case in GROUPED_SINGLE_CAPTURE_CASES) == (
        EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS
    )
    for case in GROUPED_SINGLE_CAPTURE_CASES:
        assert _pattern(case) == "(abc)"
        assert "grouped" in case.categories
        assert "capture" in case.categories
        assert "gap" not in case.categories


def test_grouped_literal_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
) -> None:
    backend_name, backend = regex_backend

    observed = backend.compile(_pattern(GROUPED_TEMPLATE_CASE))
    expected = re.compile(_pattern(GROUPED_TEMPLATE_CASE))

    assert observed is backend.compile(_pattern(GROUPED_TEMPLATE_CASE))
    _assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    ("use_compiled_pattern", "helper", "string_repetitions", "count"),
    REPLACEMENT_VARIANTS,
)
def test_grouped_literal_template_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
    helper: str,
    string_repetitions: int,
    count: int,
) -> None:
    backend_name, backend = regex_backend
    pattern = _pattern(GROUPED_TEMPLATE_CASE)
    replacement = _replacement(GROUPED_TEMPLATE_CASE)
    string = _single_match_string(GROUPED_TEMPLATE_CASE) * string_repetitions

    if use_compiled_pattern:
        observed_pattern = backend.compile(pattern)
        expected_pattern = re.compile(pattern)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, helper)(replacement, string, count=count)
        expected = getattr(expected_pattern, helper)(replacement, string, count=count)
    else:
        observed = getattr(backend, helper)(pattern, replacement, string, count=count)
        expected = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected


@pytest.mark.parametrize(
    "case",
    GROUPED_SINGLE_CAPTURE_CASES,
    ids=lambda case: case.case_id,
)
def test_grouped_single_capture_workflows_match_cpython(
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
