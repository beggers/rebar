from __future__ import annotations

from dataclasses import dataclass
import pathlib

import pytest

from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.fixture_parity_support import (
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    str_case_pattern,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern: str
    helper: str
    string: str
    bounds: tuple[int, ...]


def _fixture_cases(fixture_name: str) -> dict[str, FixtureCase]:
    _, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return {case.case_id: case for case in cases}


GROUPED_SEGMENT_CASES = _fixture_cases("grouped_segment_workflows.py")
OPTIONAL_GROUP_CASES = _fixture_cases("optional_group_workflows.py")

GROUPED_SEGMENT_PATTERN = str_case_pattern(
    GROUPED_SEGMENT_CASES["grouped-segment-compile-metadata-str"]
)
OPTIONAL_NAMED_GROUP_PATTERN = str_case_pattern(
    OPTIONAL_GROUP_CASES["named-optional-group-compile-metadata-str"]
)

MATCH_CASES = (
    BoundedPatternCase(
        id="grouped-segment-search-normalizes-negative-and-oversized-bounds",
        pattern=GROUPED_SEGMENT_PATTERN,
        helper="search",
        string="zzabczz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="grouped-segment-match-honors-narrowed-offset-window",
        pattern=GROUPED_SEGMENT_PATTERN,
        helper="match",
        string="zzabczz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-optional-fullmatch-preserves-absent-group-metadata-in-window",
        pattern=OPTIONAL_NAMED_GROUP_PATTERN,
        helper="fullmatch",
        string="zzadzz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="named-optional-fullmatch-preserves-present-group-metadata-in-window",
        pattern=OPTIONAL_NAMED_GROUP_PATTERN,
        helper="fullmatch",
        string="zzabdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-optional-search-normalizes-negative-and-oversized-bounds",
        pattern=OPTIONAL_NAMED_GROUP_PATTERN,
        helper="search",
        string="zzabdzz",
        bounds=(-100, 999),
    ),
)

NO_MATCH_CASES = (
    BoundedPatternCase(
        id="named-optional-search-skips-match-before-pos",
        pattern=OPTIONAL_NAMED_GROUP_PATTERN,
        helper="search",
        string="zzabdzz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="grouped-segment-match-fails-when-endpos-truncates-the-subject",
        pattern=GROUPED_SEGMENT_PATTERN,
        helper="match",
        string="zzabczz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="named-optional-fullmatch-does-not-expand-to-the-whole-string",
        pattern=OPTIONAL_NAMED_GROUP_PATTERN,
        helper="fullmatch",
        string="zzabdzz",
        bounds=(-100, 999),
    ),
)


def _invoke_bound_helper(pattern: object, case: BoundedPatternCase) -> object:
    return getattr(pattern, case.helper)(case.string, *case.bounds)


def test_pattern_bounds_suite_stays_anchored_to_published_patterns() -> None:
    assert GROUPED_SEGMENT_PATTERN == r"a(b)c"
    assert OPTIONAL_NAMED_GROUP_PATTERN == r"a(?P<word>b)?d"


@pytest.mark.parametrize("case", MATCH_CASES, ids=lambda case: case.id)
def test_compiled_pattern_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = _invoke_bound_helper(observed_pattern, case)
    expected = _invoke_bound_helper(expected_pattern, case)

    assert observed is not None
    assert expected is not None

    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", NO_MATCH_CASES, ids=lambda case: case.id)
def test_compiled_pattern_bounds_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = _invoke_bound_helper(observed_pattern, case)
    expected = _invoke_bound_helper(expected_pattern, case)

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)
