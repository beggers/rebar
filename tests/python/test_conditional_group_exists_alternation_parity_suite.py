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


FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "conditional_group_exists_alternation_workflows.py",
        expected_manifest_id="conditional-group-exists-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-alternation-compile-metadata-str",
                "conditional-group-exists-alternation-module-search-present-first-arm-str",
                "conditional-group-exists-alternation-pattern-fullmatch-present-second-arm-str",
                "conditional-group-exists-alternation-module-search-absent-first-arm-str",
                "conditional-group-exists-alternation-pattern-fullmatch-absent-second-arm-str",
                "named-conditional-group-exists-alternation-compile-metadata-str",
                "named-conditional-group-exists-alternation-module-search-present-first-arm-str",
                "named-conditional-group-exists-alternation-pattern-fullmatch-present-second-arm-str",
                "named-conditional-group-exists-alternation-module-search-absent-first-arm-str",
                "named-conditional-group-exists-alternation-pattern-fullmatch-absent-second-arm-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(de|df)|(eg|eh))",
                r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
    ),
    FixtureBundleSpec(
        "conditional_group_exists_no_else_alternation_workflows.py",
        expected_manifest_id="conditional-group-exists-no-else-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-no-else-alternation-compile-metadata-str",
                "conditional-group-exists-no-else-alternation-module-search-first-arm-str",
                "conditional-group-exists-no-else-alternation-module-search-second-arm-str",
                "conditional-group-exists-no-else-alternation-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-no-else-alternation-compile-metadata-str",
                "named-conditional-group-exists-no-else-alternation-module-search-first-arm-str",
                "named-conditional-group-exists-no-else-alternation-module-search-second-arm-str",
                "named-conditional-group-exists-no-else-alternation-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(de|df))",
                r"a(?P<word>b)?c(?(word)(de|df))",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    FixtureBundleSpec(
        "conditional_group_exists_empty_else_alternation_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-else-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-else-alternation-compile-metadata-str",
                "conditional-group-exists-empty-else-alternation-module-search-first-arm-str",
                "conditional-group-exists-empty-else-alternation-module-search-second-arm-str",
                "conditional-group-exists-empty-else-alternation-pattern-fullmatch-absent-str",
                "named-conditional-group-exists-empty-else-alternation-compile-metadata-str",
                "named-conditional-group-exists-empty-else-alternation-module-search-first-arm-str",
                "named-conditional-group-exists-empty-else-alternation-module-search-second-arm-str",
                "named-conditional-group-exists-empty-else-alternation-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(de|df)|)",
                r"a(?P<word>b)?c(?(word)(de|df)|)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    FixtureBundleSpec(
        "conditional_group_exists_empty_yes_else_alternation_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-yes-else-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-yes-else-alternation-compile-metadata-str",
                "conditional-group-exists-empty-yes-else-alternation-module-search-present-str",
                "conditional-group-exists-empty-yes-else-alternation-module-search-absent-first-arm-str",
                "conditional-group-exists-empty-yes-else-alternation-pattern-fullmatch-absent-second-arm-str",
                "named-conditional-group-exists-empty-yes-else-alternation-compile-metadata-str",
                "named-conditional-group-exists-empty-yes-else-alternation-module-search-present-str",
                "named-conditional-group-exists-empty-yes-else-alternation-module-search-absent-first-arm-str",
                "named-conditional-group-exists-empty-yes-else-alternation-pattern-fullmatch-absent-second-arm-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|(e|f))",
                r"a(?P<word>b)?c(?(word)|(e|f))",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    FixtureBundleSpec(
        "conditional_group_exists_fully_empty_alternation_workflows.py",
        expected_manifest_id="conditional-group-exists-fully-empty-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-fully-empty-alternation-compile-metadata-str",
                "conditional-group-exists-fully-empty-alternation-module-search-present-str",
                "conditional-group-exists-fully-empty-alternation-module-fullmatch-absent-str",
                "conditional-group-exists-fully-empty-alternation-pattern-fullmatch-extra-suffix-failure-str",
                "named-conditional-group-exists-fully-empty-alternation-compile-metadata-str",
                "named-conditional-group-exists-fully-empty-alternation-module-search-present-str",
                "named-conditional-group-exists-fully-empty-alternation-module-fullmatch-absent-str",
                "named-conditional-group-exists-fully-empty-alternation-pattern-fullmatch-extra-suffix-failure-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|(?:|))",
                r"a(?P<word>b)?c(?(word)|(?:|))",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("module_call", "fullmatch"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
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
