from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_match_convenience_api_parity,
    assert_match_parity,
    compile_with_cpython_parity,
    str_case_pattern,
)


REPLACEMENT_FIXTURE_PATH = FIXTURES_DIR / "collection_replacement_workflows.py"
ALTERNATION_REPLACEMENT_FIXTURE_PATH = (
    FIXTURES_DIR / "grouped_alternation_replacement_workflows.py"
)
MATCH_FIXTURE_PATH = FIXTURES_DIR / "grouped_match_workflows.py"

REPLACEMENT_FIXTURE_MANIFEST, REPLACEMENT_FIXTURE_CASES = load_fixture_manifest(
    REPLACEMENT_FIXTURE_PATH
)
ALTERNATION_REPLACEMENT_FIXTURE_MANIFEST, ALTERNATION_REPLACEMENT_FIXTURE_CASES = (
    load_fixture_manifest(ALTERNATION_REPLACEMENT_FIXTURE_PATH)
)
MATCH_FIXTURE_MANIFEST, MATCH_FIXTURE_CASES = load_fixture_manifest(MATCH_FIXTURE_PATH)

EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS = (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
)
EXPECTED_GROUPED_ALTERNATION_CASE_IDS = (
    "module-sub-template-grouped-alternation-str",
    "module-subn-template-grouped-alternation-str",
    "pattern-sub-template-grouped-alternation-str",
    "pattern-subn-template-grouped-alternation-str",
    "module-sub-template-named-grouped-alternation-str",
    "module-subn-template-named-grouped-alternation-str",
    "pattern-sub-template-named-grouped-alternation-str",
    "pattern-subn-template-named-grouped-alternation-str",
)
EXPECTED_GROUPED_ALTERNATION_COMPILE_PATTERNS = {
    "a(b|c)d",
    "a(?P<word>b|c)d",
}
EXPECTED_GROUPED_ALTERNATION_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
REPLACEMENT_VARIANTS = (
    pytest.param(False, "sub", 1, 0, id="module-sub-single-match"),
    pytest.param(False, "sub", 2, 0, id="module-sub-repeated"),
    pytest.param(False, "subn", 2, 1, id="module-subn-first-match-only"),
    pytest.param(True, "sub", 1, 0, id="pattern-sub-single-match"),
    pytest.param(True, "sub", 2, 0, id="pattern-sub-repeated"),
    pytest.param(True, "subn", 2, 1, id="pattern-subn-first-match-only"),
)


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
GROUPED_ALTERNATION_REPLACEMENT_CASES = tuple(ALTERNATION_REPLACEMENT_FIXTURE_CASES)
GROUPED_ALTERNATION_MODULE_CASES = tuple(
    case
    for case in GROUPED_ALTERNATION_REPLACEMENT_CASES
    if case.operation == "module_call"
)
GROUPED_ALTERNATION_PATTERN_CASES = tuple(
    case
    for case in GROUPED_ALTERNATION_REPLACEMENT_CASES
    if case.operation == "pattern_call"
)
COMPILE_PATTERNS = (
    str_case_pattern(GROUPED_TEMPLATE_CASE),
    *tuple(sorted({str_case_pattern(case) for case in GROUPED_ALTERNATION_REPLACEMENT_CASES})),
)


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


def test_grouped_literal_template_suite_stays_aligned_with_published_fixtures() -> None:
    assert REPLACEMENT_FIXTURE_MANIFEST.manifest_id == "collection-replacement-workflows"
    assert MATCH_FIXTURE_MANIFEST.manifest_id == "grouped-match-workflows"
    assert GROUPED_TEMPLATE_CASE.operation == "module_call"
    assert GROUPED_TEMPLATE_CASE.helper == "sub"
    assert str_case_pattern(GROUPED_TEMPLATE_CASE) == "(abc)"
    assert _replacement(GROUPED_TEMPLATE_CASE) == r"\1x"
    assert _single_match_string(GROUPED_TEMPLATE_CASE) == "abc"
    assert "replacement-template" in GROUPED_TEMPLATE_CASE.categories
    assert "grouping-dependent" in GROUPED_TEMPLATE_CASE.categories

    assert tuple(case.case_id for case in GROUPED_SINGLE_CAPTURE_CASES) == (
        EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS
    )
    for case in GROUPED_SINGLE_CAPTURE_CASES:
        assert str_case_pattern(case) == "(abc)"
        assert "grouped" in case.categories
        assert "capture" in case.categories
        assert "gap" not in case.categories


def test_grouped_alternation_template_suite_stays_aligned_with_published_fixtures() -> None:
    assert (
        ALTERNATION_REPLACEMENT_FIXTURE_MANIFEST.manifest_id
        == "grouped-alternation-replacement-workflows"
    )
    assert tuple(case.case_id for case in GROUPED_ALTERNATION_REPLACEMENT_CASES) == (
        EXPECTED_GROUPED_ALTERNATION_CASE_IDS
    )
    assert {
        str_case_pattern(case) for case in GROUPED_ALTERNATION_REPLACEMENT_CASES
    } == EXPECTED_GROUPED_ALTERNATION_COMPILE_PATTERNS
    assert Counter(
        (case.operation, case.helper) for case in GROUPED_ALTERNATION_REPLACEMENT_CASES
    ) == EXPECTED_GROUPED_ALTERNATION_OPERATION_HELPER_COUNTS


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_grouped_replacement_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, pattern)


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
    pattern = str_case_pattern(GROUPED_TEMPLATE_CASE)
    replacement = _replacement(GROUPED_TEMPLATE_CASE)
    string = _single_match_string(GROUPED_TEMPLATE_CASE) * string_repetitions

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed = getattr(observed_pattern, helper)(replacement, string, count=count)
        expected = getattr(expected_pattern, helper)(replacement, string, count=count)
    else:
        observed = getattr(backend, helper)(pattern, replacement, string, count=count)
        expected = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected


@pytest.mark.parametrize(
    "case",
    GROUPED_ALTERNATION_MODULE_CASES,
    ids=lambda case: case.case_id,
)
def test_grouped_alternation_module_template_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize(
    "case",
    GROUPED_ALTERNATION_PATTERN_CASES,
    ids=lambda case: case.case_id,
)
def test_grouped_alternation_pattern_template_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

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
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern_payload(),
            case.flags or 0,
        )
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
