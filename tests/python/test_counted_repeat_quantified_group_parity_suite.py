from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import (
    COUNTED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_match_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    published_fixture_paths_from_bundles,
)

PUBLISHED_COUNTED_REPEAT_FIXTURE_PATHS = select_correctness_fixture_paths(
    COUNTED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR
)

FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "exact_repeat_quantified_group_workflows.py",
        expected_manifest_id="exact-repeat-quantified-group-workflows",
        expected_case_ids=frozenset(
            {
                "exact-repeat-numbered-group-compile-metadata-str",
                "exact-repeat-numbered-group-module-search-str",
                "exact-repeat-numbered-group-pattern-fullmatch-str",
                "exact-repeat-named-group-compile-metadata-str",
                "exact-repeat-named-group-module-search-str",
                "exact-repeat-named-group-pattern-fullmatch-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(bc){2}d",
                r"a(?P<word>bc){2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    FixtureBundleSpec(
        "ranged_repeat_quantified_group_workflows.py",
        expected_manifest_id="ranged-repeat-quantified-group-workflows",
        expected_case_ids=frozenset(
            {
                "ranged-repeat-numbered-group-compile-metadata-str",
                "ranged-repeat-numbered-group-module-search-lower-bound-str",
                "ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
                "ranged-repeat-named-group-compile-metadata-str",
                "ranged-repeat-named-group-module-search-upper-bound-str",
                "ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(bc){1,2}d",
                r"a(?P<word>bc){1,2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
PUBLISHED_CASES = fixture_cases_from_bundles(FIXTURE_BUNDLES)
COMPILE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
MODULE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "module_call")
PATTERN_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "pattern_call")


def test_counted_repeat_quantified_group_suite_uses_expected_published_fixtures() -> None:
    assert PUBLISHED_COUNTED_REPEAT_FIXTURE_PATHS == published_fixture_paths_from_bundles(
        FIXTURE_BUNDLES
    )
    assert len({case.case_id for case in PUBLISHED_CASES}) == len(PUBLISHED_CASES)


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
        pattern_extractor=case_pattern,
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case_pattern(case), case.flags or 0)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_parity(backend_name, observed, expected)


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
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_parity(backend_name, observed, expected)
