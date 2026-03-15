from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest
import rebar

from rebar_harness.correctness import FixtureCase, FixtureManifest, load_fixture_manifest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 2,
        ("pattern_call", "fullmatch"): 2,
    }
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_compile_patterns: frozenset[str],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=expected_case_ids,
        expected_compile_patterns=expected_compile_patterns,
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
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
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e)",
                r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
    ),
    _fixture_bundle(
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
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d)",
                r"a(?P<word>b)?c(?(word)d)",
            }
        ),
    ),
    _fixture_bundle(
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
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|)",
                r"a(?P<word>b)?c(?(word)d|)",
            }
        ),
    ),
    _fixture_bundle(
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
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)|e)",
                r"a(?P<word>b)?c(?(word)|e)",
            }
        ),
    ),
    _fixture_bundle(
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
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)|)",
                r"a(?P<word>b)?c(?(word)|)",
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
    assert observed.group(1) == expected.group(1)
    assert observed.groups() == expected.groups()
    assert observed.groupdict() == expected.groupdict()
    assert observed.span() == expected.span()
    assert observed.span(1) == expected.span(1)
    assert observed.start(1) == expected.start(1)
    assert observed.end(1) == expected.end(1)
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)


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
    assert {_case_pattern(case) for case in bundle.cases} == bundle.expected_compile_patterns
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

    assert observed is not None
    assert expected is not None
    _assert_match_parity(backend_name, observed, expected)
