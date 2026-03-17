from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    str_case_pattern,
)


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern_case_id: str
    helper: str
    string: str
    bounds: tuple[int, int]


EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 2,
        ("pattern_call", "fullmatch"): 2,
    }
)

FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "optional_group_conditional_workflows.py",
        expected_manifest_id="optional-group-conditional-workflows",
        expected_case_ids=frozenset(
            {
                "optional-group-conditional-compile-metadata-str",
                "optional-group-conditional-module-search-present-str",
                "optional-group-conditional-pattern-fullmatch-absent-str",
                "named-optional-group-conditional-compile-metadata-str",
                "named-optional-group-conditional-module-search-present-str",
                "named-optional-group-conditional-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?(?(1)c|d)e",
                r"a(?P<word>b)?(?(word)c|d)e",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_workflows.py",
        expected_manifest_id="conditional-group-exists-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-compile-metadata-str",
                "conditional-group-exists-module-search-present-str",
                "conditional-group-exists-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-compile-metadata-str",
                "named-conditional-group-exists-module-search-present-str",
                "named-conditional-group-exists-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e)",
                r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_no_else_workflows.py",
        expected_manifest_id="conditional-group-exists-no-else-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-no-else-compile-metadata-str",
                "conditional-group-exists-no-else-module-search-present-str",
                "conditional-group-exists-no-else-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-no-else-compile-metadata-str",
                "named-conditional-group-exists-no-else-module-search-present-str",
                "named-conditional-group-exists-no-else-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d)",
                r"a(?P<word>b)?c(?(word)d)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_empty_else_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-else-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-else-compile-metadata-str",
                "conditional-group-exists-empty-else-module-search-present-str",
                "conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-empty-else-compile-metadata-str",
                "named-conditional-group-exists-empty-else-module-search-present-str",
                "named-conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|)",
                r"a(?P<word>b)?c(?(word)d|)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_empty_yes_else_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-yes-else-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-yes-else-compile-metadata-str",
                "conditional-group-exists-empty-yes-else-module-search-present-str",
                "conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-empty-yes-else-compile-metadata-str",
                "named-conditional-group-exists-empty-yes-else-module-search-present-str",
                "named-conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|e)",
                r"a(?P<word>b)?c(?(word)|e)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_fully_empty_workflows.py",
        expected_manifest_id="conditional-group-exists-fully-empty-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-fully-empty-compile-metadata-str",
                "conditional-group-exists-fully-empty-module-search-present-str",
                "conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-fully-empty-compile-metadata-str",
                "named-conditional-group-exists-fully-empty-module-search-present-str",
                "named-conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|)",
                r"a(?P<word>b)?c(?(word)|)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
PUBLISHED_CASES = fixture_cases_from_bundles(FIXTURE_BUNDLES)
COMPILE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
MODULE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "module_call")
PATTERN_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "pattern_call")
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}

PATTERN_BOUNDS_MATCH_CASES = (
    BoundedPatternCase(
        id="optional-group-conditional-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="optional-group-conditional-compile-metadata-str",
        helper="search",
        string="zzabcezz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="named-optional-group-conditional-fullmatch-preserves-absent-group-metadata-in-window",
        pattern_case_id="named-optional-group-conditional-compile-metadata-str",
        helper="fullmatch",
        string="zzadezz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="conditional-group-exists-compile-metadata-str",
        helper="search",
        string="zzabcdzz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-no-else-fullmatch-preserves-absent-group-metadata-in-window",
        pattern_case_id="named-conditional-group-exists-no-else-compile-metadata-str",
        helper="fullmatch",
        string="zzaczz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-empty-else-match-honors-narrowed-window",
        pattern_case_id="conditional-group-exists-empty-else-compile-metadata-str",
        helper="match",
        string="zzabcdzz",
        bounds=(2, 6),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-empty-yes-else-fullmatch-preserves-absent-group-metadata-in-window",
        pattern_case_id="named-conditional-group-exists-empty-yes-else-compile-metadata-str",
        helper="fullmatch",
        string="zzacezz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-fully-empty-fullmatch-preserves-present-group-metadata-in-window",
        pattern_case_id="named-conditional-group-exists-fully-empty-compile-metadata-str",
        helper="fullmatch",
        string="zzabczz",
        bounds=(2, 5),
    ),
)

PATTERN_BOUNDS_NO_MATCH_CASES = (
    BoundedPatternCase(
        id="named-optional-group-conditional-search-skips-match-before-pos",
        pattern_case_id="named-optional-group-conditional-compile-metadata-str",
        helper="search",
        string="zzadezz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="optional-group-conditional-match-fails-when-endpos-truncates-suffix",
        pattern_case_id="optional-group-conditional-compile-metadata-str",
        helper="match",
        string="zzabcezz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-search-skips-match-before-pos",
        pattern_case_id="named-conditional-group-exists-compile-metadata-str",
        helper="search",
        string="zzacezz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-no-else-match-fails-when-endpos-truncates-yes-branch",
        pattern_case_id="conditional-group-exists-no-else-compile-metadata-str",
        helper="match",
        string="zzabcdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-empty-else-fullmatch-does-not-expand-to-whole-string",
        pattern_case_id="named-conditional-group-exists-empty-else-compile-metadata-str",
        helper="fullmatch",
        string="zzaczz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-empty-yes-else-search-skips-match-before-pos",
        pattern_case_id="conditional-group-exists-empty-yes-else-compile-metadata-str",
        helper="search",
        string="zzabczz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-fully-empty-fullmatch-fails-when-endpos-includes-extra-suffix",
        pattern_case_id="named-conditional-group-exists-fully-empty-compile-metadata-str",
        helper="fullmatch",
        string="zzaczz",
        bounds=(2, 5),
    ),
)


def _bounded_pattern(case: BoundedPatternCase) -> str:
    return str_case_pattern(CASES_BY_ID[case.pattern_case_id])


def _invoke_bound_helper(pattern: object, case: BoundedPatternCase) -> object:
    return getattr(pattern, case.helper)(case.string, *case.bounds)


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
    )


def test_pattern_bounds_cases_stay_anchored_to_published_conditional_patterns() -> None:
    assert str_case_pattern(
        CASES_BY_ID["optional-group-conditional-compile-metadata-str"]
    ) == r"a(b)?(?(1)c|d)e"
    assert str_case_pattern(
        CASES_BY_ID["named-optional-group-conditional-compile-metadata-str"]
    ) == r"a(?P<word>b)?(?(word)c|d)e"
    assert str_case_pattern(CASES_BY_ID["conditional-group-exists-compile-metadata-str"]) == (
        r"a(b)?c(?(1)d|e)"
    )
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-no-else-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)d)"
    assert str_case_pattern(
        CASES_BY_ID["conditional-group-exists-empty-else-compile-metadata-str"]
    ) == r"a(b)?c(?(1)d|)"
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-empty-else-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)d|)"
    assert str_case_pattern(
        CASES_BY_ID["conditional-group-exists-empty-yes-else-compile-metadata-str"]
    ) == r"a(b)?c(?(1)|e)"
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-empty-yes-else-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)|e)"
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-fully-empty-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)|)"


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

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", PATTERN_BOUNDS_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_helper_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        _bounded_pattern(case),
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


@pytest.mark.parametrize("case", PATTERN_BOUNDS_NO_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_helper_bounds_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        _bounded_pattern(case),
    )

    observed = _invoke_bound_helper(observed_pattern, case)
    expected = _invoke_bound_helper(expected_pattern, case)

    assert observed is None
    assert expected is None
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

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)
