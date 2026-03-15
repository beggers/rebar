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


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


@dataclass(frozen=True)
class SupplementalModuleFullmatchCase:
    id: str
    pattern: str
    text: str


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_compile_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=expected_case_ids,
        expected_compile_patterns=expected_compile_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "conditional_group_exists_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-quantified-compile-metadata-str",
                "conditional-group-exists-quantified-module-search-present-str",
                "conditional-group-exists-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
                "named-conditional-group-exists-quantified-compile-metadata-str",
                "named-conditional-group-exists-quantified-module-search-present-str",
                "named-conditional-group-exists-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e){2}",
                r"a(?P<word>b)?c(?(word)d|e){2}",
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
    _fixture_bundle(
        "conditional_group_exists_no_else_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-no-else-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-no-else-quantified-compile-metadata-str",
                "conditional-group-exists-no-else-quantified-module-search-present-str",
                "conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
                "named-conditional-group-exists-no-else-quantified-compile-metadata-str",
                "named-conditional-group-exists-no-else-quantified-module-search-present-str",
                "named-conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d){2}",
                r"a(?P<word>b)?c(?(word)d){2}",
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
    _fixture_bundle(
        "conditional_group_exists_empty_else_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-else-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-else-quantified-compile-metadata-str",
                "conditional-group-exists-empty-else-quantified-module-search-present-str",
                "conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
                "named-conditional-group-exists-empty-else-quantified-compile-metadata-str",
                "named-conditional-group-exists-empty-else-quantified-module-search-present-str",
                "named-conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|){2}",
                r"a(?P<word>b)?c(?(word)d|){2}",
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
    _fixture_bundle(
        "conditional_group_exists_empty_yes_else_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-yes-else-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
                "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
                "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
                "named-conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
                "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
                "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"(?:a(b)?c(?(1)|e)){2}",
                r"(?:a(?P<word>b)?c(?(word)|e)){2}",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "fullmatch"): 4,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_fully_empty_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-fully-empty-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-fully-empty-quantified-compile-metadata-str",
                "conditional-group-exists-fully-empty-quantified-module-fullmatch-present-str",
                "conditional-group-exists-fully-empty-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-fully-empty-quantified-pattern-fullmatch-mixed-str",
                "conditional-group-exists-fully-empty-quantified-pattern-fullmatch-extra-suffix-failure-str",
                "named-conditional-group-exists-fully-empty-quantified-compile-metadata-str",
                "named-conditional-group-exists-fully-empty-quantified-module-fullmatch-present-str",
                "named-conditional-group-exists-fully-empty-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-fully-empty-quantified-pattern-fullmatch-mixed-str",
                "named-conditional-group-exists-fully-empty-quantified-pattern-fullmatch-extra-suffix-failure-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"(?:a(b)?c(?(1)|)){2}",
                r"(?:a(?P<word>b)?c(?(word)|)){2}",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "fullmatch"): 4,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")

# Preserve the extra module.fullmatch mixed-iteration checks that only lived in
# the superseded singleton files and were never promoted into scorecard fixtures.
SUPPLEMENTAL_MODULE_FULLMATCH_CASES = (
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-empty-yes-else-quantified-numbered-module-fullmatch-mixed-present-then-absent-failure",
        pattern=r"(?:a(b)?c(?(1)|e)){2}",
        text="abcace",
    ),
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-empty-yes-else-quantified-named-module-fullmatch-mixed-present-then-absent-failure",
        pattern=r"(?:a(?P<word>b)?c(?(word)|e)){2}",
        text="abcace",
    ),
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-fully-empty-quantified-numbered-module-fullmatch-mixed-present-then-absent",
        pattern=r"(?:a(b)?c(?(1)|)){2}",
        text="abcac",
    ),
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-fully-empty-quantified-named-module-fullmatch-mixed-present-then-absent",
        pattern=r"(?:a(?P<word>b)?c(?(word)|)){2}",
        text="abcac",
    ),
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


def _assert_match_result_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | None,
) -> None:
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    _assert_match_parity(backend_name, observed, expected)


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
def test_module_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    _assert_match_result_parity(backend_name, observed, expected)


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

    _assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    SUPPLEMENTAL_MODULE_FULLMATCH_CASES,
    ids=lambda case: case.id,
)
def test_supplemental_module_fullmatch_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalModuleFullmatchCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.fullmatch(case.pattern, case.text)
    expected = re.fullmatch(case.pattern, case.text)

    _assert_match_result_parity(backend_name, observed, expected)
