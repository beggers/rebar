from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import pathlib
import re

import pytest

import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_backtracking_heavy_workflows.py"
)

FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(FIXTURE_PATH)
EXPECTED_CASE_IDS = frozenset(
    {
        "quantified-alternation-backtracking-heavy-numbered-compile-metadata-str",
        "quantified-alternation-backtracking-heavy-numbered-module-search-lower-bound-b-branch-str",
        "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-bc-branch-str",
        "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-b-then-bc-str",
        "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-b-str",
        "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-bc-str",
        "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-str",
        "quantified-alternation-backtracking-heavy-named-compile-metadata-str",
        "quantified-alternation-backtracking-heavy-named-module-search-lower-bound-bc-branch-str",
        "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-b-then-b-str",
        "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-bc-then-b-str",
        "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-str",
    }
)
EXPECTED_PATTERNS = frozenset(
    {
        r"a(b|bc){1,2}d",
        r"a(?P<word>b|bc){1,2}d",
    }
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 2,
        ("pattern_call", "fullmatch"): 8,
    }
)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
WORKFLOW_CASES = tuple(case for case in PUBLISHED_CASES if case.operation != "compile")

MISSING_GROUP_DEFAULT = object()
BACKTRACKING_BRANCH_TEXT = {
    "short": "b",
    "long": "bc",
}
ZERO_REPETITION_NO_MATCH_TEXT = "ad"
OVERLAP_TAIL_NO_MATCH_TEXT = "abccd"


@dataclass(frozen=True)
class BacktrackingTraceCase:
    id: str
    pattern: str
    search_text: str
    fullmatch_text: str


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


def _compile_case_prefix(case: FixtureCase) -> str:
    suffix = "-compile-metadata-str"
    assert case.case_id.endswith(suffix)
    return case.case_id.removesuffix(suffix)


def _build_backtracking_trace_cases() -> tuple[BacktrackingTraceCase, ...]:
    cases: list[BacktrackingTraceCase] = []
    for case in COMPILE_CASES:
        pattern = _case_pattern(case)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(1, 3):
            for branch_order in product(("short", "long"), repeat=repetition_count):
                body = "".join(BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    BacktrackingTraceCase(
                        id=f"{prefix}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


def _build_extra_no_match_cases() -> tuple[object, ...]:
    cases: list[object] = []
    for case in COMPILE_CASES:
        pattern = _case_pattern(case)
        prefix = _compile_case_prefix(case)
        cases.extend(
            [
                pytest.param(
                    "module",
                    pattern,
                    "search",
                    f"zz{ZERO_REPETITION_NO_MATCH_TEXT}zz",
                    id=f"{prefix}-module-search-miss-zero-repetition",
                ),
                pytest.param(
                    "module",
                    pattern,
                    "search",
                    f"zz{OVERLAP_TAIL_NO_MATCH_TEXT}zz",
                    id=f"{prefix}-module-search-miss-overlap-tail",
                ),
                pytest.param(
                    "pattern",
                    pattern,
                    "fullmatch",
                    ZERO_REPETITION_NO_MATCH_TEXT,
                    id=f"{prefix}-pattern-fullmatch-miss-zero-repetition",
                ),
            ]
        )
    return tuple(cases)


TRACE_CASES = _build_backtracking_trace_cases()
EXTRA_NO_MATCH_CASES = _build_extra_no_match_cases()


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

    _assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert FIXTURE_MANIFEST.manifest_id == "quantified-alternation-backtracking-heavy-workflows"
    assert len(PUBLISHED_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in PUBLISHED_CASES} == EXPECTED_CASE_IDS
    assert {_case_pattern(case) for case in PUBLISHED_CASES} == EXPECTED_PATTERNS
    assert Counter((case.operation, case.helper) for case in PUBLISHED_CASES) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case.pattern_payload()
    assert isinstance(pattern, str)

    observed = backend.compile(pattern, case.flags or 0)
    expected = re.compile(pattern, case.flags or 0)

    assert observed is backend.compile(pattern, case.flags or 0)
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
        pattern = case.pattern_payload()
        assert isinstance(pattern, str)
        observed_pattern = backend.compile(pattern, case.flags or 0)
        expected_pattern = re.compile(pattern, case.flags or 0)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    _assert_match_parity(backend_name, observed, expected)


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
    _assert_match_parity(backend_name, observed, expected)


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
    _assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(("target", "pattern", "helper", "text"), EXTRA_NO_MATCH_CASES)
def test_extra_no_match_paths_match_cpython(
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
