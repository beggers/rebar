from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_match_result_parity,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_fixture_bundles,
    str_case_pattern,
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 2,
        ("module_call", "fullmatch"): 2,
        ("pattern_call", "fullmatch"): 2,
    }
)
SYSTEMATIC_EMPTY_ELSE_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 4,
        ("module_call", "search"): 4,
        ("module_call", "fullmatch"): 4,
        ("pattern_call", "fullmatch"): 4,
    }
)


FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "conditional_group_exists_nested_workflows.py",
        expected_manifest_id="conditional-group-exists-nested-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-nested-compile-metadata-str",
                "conditional-group-exists-nested-module-search-present-str",
                "conditional-group-exists-nested-module-fullmatch-absent-str",
                "conditional-group-exists-nested-pattern-fullmatch-unreachable-inner-else-str",
                "named-conditional-group-exists-nested-compile-metadata-str",
                "named-conditional-group-exists-nested-module-search-present-str",
                "named-conditional-group-exists-nested-module-fullmatch-absent-str",
                "named-conditional-group-exists-nested-pattern-fullmatch-unreachable-inner-else-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(?(1)d|e)|f)",
                r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_no_else_nested_workflows.py",
        expected_manifest_id="conditional-group-exists-no-else-nested-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-no-else-nested-compile-metadata-str",
                "conditional-group-exists-no-else-nested-module-search-present-str",
                "conditional-group-exists-no-else-nested-module-fullmatch-missing-suffix-str",
                "conditional-group-exists-no-else-nested-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-no-else-nested-compile-metadata-str",
                "named-conditional-group-exists-no-else-nested-module-search-present-str",
                "named-conditional-group-exists-no-else-nested-module-fullmatch-missing-suffix-str",
                "named-conditional-group-exists-no-else-nested-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(?(1)d))",
                r"a(?P<word>b)?c(?(word)(?(word)d))",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_empty_else_nested_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-else-nested-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-else-nested-compile-metadata-str",
                "conditional-group-exists-empty-else-nested-module-search-present-str",
                "conditional-group-exists-empty-else-nested-module-fullmatch-missing-suffix-str",
                "conditional-group-exists-empty-else-nested-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-empty-else-nested-compile-metadata-str",
                "named-conditional-group-exists-empty-else-nested-module-search-present-str",
                "named-conditional-group-exists-empty-else-nested-module-fullmatch-missing-suffix-str",
                "named-conditional-group-exists-empty-else-nested-pattern-fullmatch-absent-str",
                "systematic-conditional-group-exists-empty-else-nested-numbered-compile-metadata-str",
                "systematic-conditional-group-exists-empty-else-nested-numbered-module-search-present-str",
                "systematic-conditional-group-exists-empty-else-nested-numbered-module-fullmatch-missing-suffix-str",
                "systematic-conditional-group-exists-empty-else-nested-numbered-pattern-fullmatch-absent-str",
                "systematic-conditional-group-exists-empty-else-nested-named-compile-metadata-str",
                "systematic-conditional-group-exists-empty-else-nested-named-module-search-present-str",
                "systematic-conditional-group-exists-empty-else-nested-named-module-fullmatch-missing-suffix-str",
                "systematic-conditional-group-exists-empty-else-nested-named-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(?(1)d)|)",
                r"a(?P<word>b)?c(?(word)(?(word)d)|)",
            }
        ),
        expected_operation_helper_counts=SYSTEMATIC_EMPTY_ELSE_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_empty_yes_else_nested_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-yes-else-nested-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-yes-else-nested-compile-metadata-str",
                "conditional-group-exists-empty-yes-else-nested-module-search-present-str",
                "conditional-group-exists-empty-yes-else-nested-module-fullmatch-absent-str",
                "conditional-group-exists-empty-yes-else-nested-pattern-fullmatch-absent-failure-str",
                "named-conditional-group-exists-empty-yes-else-nested-compile-metadata-str",
                "named-conditional-group-exists-empty-yes-else-nested-module-search-present-str",
                "named-conditional-group-exists-empty-yes-else-nested-module-fullmatch-absent-str",
                "named-conditional-group-exists-empty-yes-else-nested-pattern-fullmatch-absent-failure-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|(?(1)e|f))",
                r"a(?P<word>b)?c(?(word)|(?(word)e|f))",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "conditional_group_exists_fully_empty_nested_workflows.py",
        expected_manifest_id="conditional-group-exists-fully-empty-nested-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-fully-empty-nested-compile-metadata-str",
                "conditional-group-exists-fully-empty-nested-module-search-present-str",
                "conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
                "conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
                "named-conditional-group-exists-fully-empty-nested-compile-metadata-str",
                "named-conditional-group-exists-fully-empty-nested-module-search-present-str",
                "named-conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
                "named-conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|(?(1)|))",
                r"a(?P<word>b)?c(?(word)|(?(word)|))",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
COMPILE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
MODULE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "module_call")
PATTERN_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "pattern_call")


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(bundle) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


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
def test_module_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

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
