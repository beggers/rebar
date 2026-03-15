from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_match_result_parity,
    compile_with_cpython_parity,
    str_case_pattern,
)


FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(
    FIXTURES_DIR / "exact_repeat_quantified_group_alternation_workflows.py"
)
EXPECTED_CASE_IDS = frozenset(
    {
        "exact-repeat-quantified-group-alternation-numbered-compile-metadata-str",
        "exact-repeat-quantified-group-alternation-numbered-module-search-bc-bc-str",
        "exact-repeat-quantified-group-alternation-numbered-module-search-bc-de-str",
        "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-de-de-str",
        "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
        "exact-repeat-quantified-group-alternation-named-compile-metadata-str",
        "exact-repeat-quantified-group-alternation-named-module-search-bc-bc-str",
        "exact-repeat-quantified-group-alternation-named-module-search-bc-de-str",
        "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-de-de-str",
        "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-extra-repetition-str",
    }
)
EXPECTED_PATTERNS = frozenset(
    {
        r"a(bc|de){2}d",
        r"a(?P<word>bc|de){2}d",
    }
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 4,
        ("pattern_call", "fullmatch"): 4,
    }
)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert FIXTURE_MANIFEST.manifest_id == "exact-repeat-quantified-group-alternation-workflows"
    assert len(PUBLISHED_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in PUBLISHED_CASES} == EXPECTED_CASE_IDS
    assert {str_case_pattern(case) for case in PUBLISHED_CASES} == EXPECTED_PATTERNS
    assert {case.text_model for case in PUBLISHED_CASES} == {"str"}
    assert Counter((case.operation, case.helper) for case in PUBLISHED_CASES) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(case),
        case.flags or 0,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(case),
        case.flags or 0,
    )

    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected)
