from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    case_pattern,
    load_fixture_bundles,
    manifest_case_ids,
)


MATCH_BEHAVIOR_FIXTURE_PATH = FIXTURES_DIR / "match_behavior_smoke.py"
EXPECTED_CASE_IDS = (
    "search-str-success-literal",
    "search-str-no-match",
    "match-str-success-literal",
    "match-str-no-match",
    "fullmatch-str-success-literal",
    "fullmatch-bytes-success-literal",
)
EXPECTED_PATTERNS = frozenset({"abc", "ab", "123", b"123"})
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "search"): 2,
        ("module_call", "match"): 2,
        ("module_call", "fullmatch"): 2,
    }
)
MATCH_BEHAVIOR_BUNDLE, = load_fixture_bundles(
    (
        FixtureBundleSpec(
            fixture_name="match_behavior_smoke.py",
            expected_manifest_id="match-behavior-smoke",
            selected_case_ids=EXPECTED_CASE_IDS,
            expected_patterns=EXPECTED_PATTERNS,
            expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            expected_text_models=frozenset({"bytes", "str"}),
        ),
    )
)
MATCH_BEHAVIOR_CASES = tuple(MATCH_BEHAVIOR_BUNDLE.cases)
MATCH_BEHAVIOR_PUBLISHED_CASE_IDS = manifest_case_ids(MATCH_BEHAVIOR_BUNDLE)
DIRECT_TEST_CASE_IDS = frozenset(case.case_id for case in MATCH_BEHAVIOR_CASES)


@dataclass(frozen=True)
class SupplementalMatchBehaviorCase:
    case_id: str
    helper: str
    pattern: bytes
    string: bytes
    matches: bool


SUPPLEMENTAL_BYTES_CASES = (
    SupplementalMatchBehaviorCase(
        case_id="search-bytes-success-literal",
        helper="search",
        pattern=b"abc",
        string=b"zzabczz",
        matches=True,
    ),
    SupplementalMatchBehaviorCase(
        case_id="search-bytes-no-match",
        helper="search",
        pattern=b"abc",
        string=b"zzz",
        matches=False,
    ),
    SupplementalMatchBehaviorCase(
        case_id="match-bytes-success-literal",
        helper="match",
        pattern=b"ab",
        string=b"abbb",
        matches=True,
    ),
    SupplementalMatchBehaviorCase(
        case_id="match-bytes-no-match",
        helper="match",
        pattern=b"abc",
        string=b"zabc",
        matches=False,
    ),
    SupplementalMatchBehaviorCase(
        case_id="fullmatch-bytes-no-match",
        helper="fullmatch",
        pattern=b"123",
        string=b"1234",
        matches=False,
    ),
)


def _case_string(case: FixtureCase) -> str | bytes:
    string = case.args[1]
    assert isinstance(string, (str, bytes))
    return string


def test_match_behavior_parity_suite_stays_aligned_with_published_fixture() -> None:
    assert_fixture_bundle_contract(
        MATCH_BEHAVIOR_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=MATCH_BEHAVIOR_FIXTURE_PATH,
        expected_ordered_case_ids=EXPECTED_CASE_IDS,
    )


def test_match_behavior_parity_suite_tracks_published_case_frontier() -> None:
    selected_case_ids = frozenset(EXPECTED_CASE_IDS)
    uncovered_case_ids = tuple(
        case_id
        for case_id in MATCH_BEHAVIOR_PUBLISHED_CASE_IDS
        if case_id not in selected_case_ids
    )

    assert uncovered_case_ids == ()
    assert frozenset(MATCH_BEHAVIOR_PUBLISHED_CASE_IDS) == selected_case_ids


def test_match_behavior_direct_test_bucket_covers_selected_frontier() -> None:
    assert DIRECT_TEST_CASE_IDS == frozenset(EXPECTED_CASE_IDS)


def test_match_behavior_supplemental_bytes_cases_cover_missing_module_paths() -> None:
    assert {(case.helper, case.matches) for case in SUPPLEMENTAL_BYTES_CASES} == {
        ("search", True),
        ("search", False),
        ("match", True),
        ("match", False),
        ("fullmatch", False),
    }
    assert all(
        isinstance(payload, bytes)
        for case in SUPPLEMENTAL_BYTES_CASES
        for payload in (case.pattern, case.string)
    )


@pytest.mark.parametrize("case", MATCH_BEHAVIOR_CASES, ids=lambda case: case.case_id)
def test_match_behavior_module_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.operation == "module_call"
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    assert_match_convenience_api_parity(observed, expected)
    assert type(observed.group(0)) is type(expected.group(0))
    assert observed.re.pattern == expected.re.pattern == case_pattern(case)
    assert observed.string == expected.string == _case_string(case)


@pytest.mark.parametrize("case", SUPPLEMENTAL_BYTES_CASES, ids=lambda case: case.case_id)
def test_match_behavior_supplemental_bytes_module_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMatchBehaviorCase,
) -> None:
    backend_name, backend = regex_backend

    observed = getattr(backend, case.helper)(case.pattern, case.string)
    expected = getattr(re, case.helper)(case.pattern, case.string)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert (expected is not None) is case.matches
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    assert_match_convenience_api_parity(observed, expected)
    assert type(observed.group(0)) is type(expected.group(0)) is bytes
    assert observed.re.pattern == expected.re.pattern == case.pattern
    assert observed.string == expected.string == case.string
