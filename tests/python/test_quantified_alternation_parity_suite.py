from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest

import rebar
from rebar_harness.correctness import (
    DEFAULT_FIXTURE_PATHS,
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"
EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "quantified_alternation_workflows.py",
    "quantified_alternation_broader_range_workflows.py",
    "quantified_alternation_conditional_workflows.py",
    "quantified_alternation_open_ended_workflows.py",
    "quantified_alternation_nested_branch_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES
)
PUBLISHED_QUANTIFIED_ALTERNATION_FIXTURE_PATHS = tuple(
    path for path in DEFAULT_FIXTURE_PATHS if path in EXPECTED_PUBLISHED_FIXTURE_PATHS
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=expected_case_ids,
        expected_patterns=expected_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "quantified_alternation_workflows.py",
        expected_manifest_id="quantified-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-numbered-compile-metadata-str",
                "quantified-alternation-numbered-module-search-lower-bound-str",
                "quantified-alternation-numbered-pattern-fullmatch-second-repetition-str",
                "quantified-alternation-named-compile-metadata-str",
                "quantified-alternation-named-module-search-second-repetition-str",
                "quantified-alternation-named-pattern-fullmatch-lower-bound-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,2}d",
                r"a(?P<word>b|c){1,2}d",
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
    _fixture_bundle(
        "quantified_alternation_broader_range_workflows.py",
        expected_manifest_id="quantified-alternation-broader-range-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-broader-range-numbered-compile-metadata-str",
                "quantified-alternation-broader-range-numbered-module-search-lower-bound-b-str",
                "quantified-alternation-broader-range-numbered-module-search-lower-bound-c-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bbb-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcb-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-overflow-str",
                "quantified-alternation-broader-range-named-compile-metadata-str",
                "quantified-alternation-broader-range-named-module-search-lower-bound-b-str",
                "quantified-alternation-broader-range-named-module-search-lower-bound-c-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bbb-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcb-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-overflow-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,3}d",
                r"a(?P<word>b|c){1,3}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_conditional_workflows.py",
        expected_manifest_id="quantified-alternation-conditional-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-conditional-numbered-compile-metadata-str",
                "quantified-alternation-conditional-numbered-module-search-absent-workflow-str",
                "quantified-alternation-conditional-numbered-module-search-lower-bound-b-workflow-str",
                "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-b-workflow-str",
                "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str",
                "quantified-alternation-conditional-numbered-pattern-fullmatch-no-match-workflow-str",
                "quantified-alternation-conditional-named-compile-metadata-str",
                "quantified-alternation-conditional-named-module-search-absent-workflow-str",
                "quantified-alternation-conditional-named-module-search-lower-bound-c-workflow-str",
                "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-c-workflow-str",
                "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-mixed-workflow-str",
                "quantified-alternation-conditional-named-pattern-fullmatch-no-match-workflow-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){1,2})?(?(1)d|e)",
                r"a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_open_ended_workflows.py",
        expected_manifest_id="quantified-alternation-open-ended-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-open-ended-numbered-compile-metadata-str",
                "quantified-alternation-open-ended-numbered-module-search-lower-bound-b-str",
                "quantified-alternation-open-ended-numbered-module-search-lower-bound-c-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-second-repetition-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-fourth-repetition-bcbc-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-invalid-branch-str",
                "quantified-alternation-open-ended-named-compile-metadata-str",
                "quantified-alternation-open-ended-named-module-search-lower-bound-b-str",
                "quantified-alternation-open-ended-named-module-search-lower-bound-c-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-second-repetition-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-fourth-repetition-bcbc-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-invalid-branch-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,}d",
                r"a(?P<word>b|c){1,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_nested_branch_workflows.py",
        expected_manifest_id="quantified-alternation-nested-branch-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-nested-branch-numbered-compile-metadata-str",
                "quantified-alternation-nested-branch-numbered-module-search-lower-bound-inner-branch-str",
                "quantified-alternation-nested-branch-numbered-pattern-fullmatch-lower-bound-literal-branch-str",
                "quantified-alternation-nested-branch-numbered-pattern-fullmatch-second-repetition-mixed-branches-str",
                "quantified-alternation-nested-branch-numbered-pattern-fullmatch-no-match-str",
                "quantified-alternation-nested-branch-named-compile-metadata-str",
                "quantified-alternation-nested-branch-named-module-search-lower-bound-literal-branch-str",
                "quantified-alternation-nested-branch-named-pattern-fullmatch-lower-bound-inner-branch-str",
                "quantified-alternation-nested-branch-named-pattern-fullmatch-second-repetition-mixed-branches-str",
                "quantified-alternation-nested-branch-named-pattern-fullmatch-no-match-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)|de){1,2}d",
                r"a(?P<word>(b|c)|de){1,2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
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


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


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

    assert observed.group(0) == expected.group(0)
    for group_index in range(1, expected.re.groups + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groupdict() == expected.groupdict()
    assert observed.span() == expected.span()
    assert observed.start() == expected.start()
    assert observed.end() == expected.end()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def test_quantified_alternation_suite_uses_expected_published_fixtures() -> None:
    assert set(PUBLISHED_QUANTIFIED_ALTERNATION_FIXTURE_PATHS) == set(
        EXPECTED_PUBLISHED_FIXTURE_PATHS
    )


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert bundle.manifest.manifest_id == bundle.expected_manifest_id
    assert len(bundle.cases) == len(bundle.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    assert {_case_pattern(case) for case in bundle.cases} == bundle.expected_patterns
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
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
    _assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
    expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    if expected is None:
        assert observed is None
        return

    assert observed is not None
    _assert_match_parity(backend_name, observed, expected)
