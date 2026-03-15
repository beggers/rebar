from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    assert_fixture_bundle_contract,
    assert_match_parity,
    compile_with_cpython_parity,
    load_fixture_bundle,
    str_case_pattern,
)

EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 2,
        ("pattern_call", "fullmatch"): 2,
    }
)

FIXTURE_BUNDLES = (
    load_fixture_bundle(
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
    load_fixture_bundle(
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
    load_fixture_bundle(
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
    load_fixture_bundle(
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
    load_fixture_bundle(
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
COMPILE_CASES = tuple(
    case
    for bundle in FIXTURE_BUNDLES
    for case in bundle.cases
    if case.operation == "compile"
)
MODULE_CASES = tuple(
    case
    for bundle in FIXTURE_BUNDLES
    for case in bundle.cases
    if case.operation == "module_call"
)
PATTERN_CASES = tuple(
    case
    for bundle in FIXTURE_BUNDLES
    for case in bundle.cases
    if case.operation == "pattern_call"
)


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
