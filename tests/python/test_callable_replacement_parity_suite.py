from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest

from rebar_harness.correctness import FixtureCase, FixtureManifest, load_fixture_manifest
from tests.python.callable_replacement_callback_support import (
    assert_callable_replacement_match_parity,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str]]


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_compile_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    assert manifest.manifest_id == expected_manifest_id
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_case_ids=expected_case_ids,
        expected_compile_patterns=expected_compile_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "nested_group_callable_replacement_workflows.py",
        expected_manifest_id="nested-group-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-group-numbered-str",
                "module-subn-callable-nested-group-numbered-str",
                "pattern-sub-callable-nested-group-numbered-str",
                "pattern-subn-callable-nested-group-numbered-str",
                "module-sub-callable-nested-group-named-str",
                "module-subn-callable-nested-group-named-str",
                "pattern-sub-callable-nested-group-named-str",
                "pattern-subn-callable-nested-group-named-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b))d",
                r"a(?P<outer>(?P<inner>b))d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "sub"): 2,
                ("module_call", "subn"): 2,
                ("pattern_call", "sub"): 2,
                ("pattern_call", "subn"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "grouped_alternation_callable_replacement_workflows.py",
        expected_manifest_id="grouped-alternation-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-grouped-alternation-str",
                "module-subn-callable-grouped-alternation-str",
                "pattern-sub-callable-grouped-alternation-str",
                "pattern-subn-callable-grouped-alternation-str",
                "module-sub-callable-named-grouped-alternation-str",
                "module-subn-callable-named-grouped-alternation-str",
                "pattern-sub-callable-named-grouped-alternation-str",
                "pattern-subn-callable-named-grouped-alternation-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b|c)d",
                r"a(?P<word>b|c)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "sub"): 2,
                ("module_call", "subn"): 2,
                ("pattern_call", "sub"): 2,
                ("pattern_call", "subn"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_nested_group_callable_replacement_workflows.py",
        expected_manifest_id="quantified-nested-group-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-quantified-nested-group-numbered-lower-bound-str",
                "module-subn-callable-quantified-nested-group-numbered-first-match-only-str",
                "pattern-sub-callable-quantified-nested-group-numbered-repeated-outer-capture-str",
                "pattern-subn-callable-quantified-nested-group-numbered-first-match-only-str",
                "module-sub-callable-quantified-nested-group-named-lower-bound-str",
                "module-subn-callable-quantified-nested-group-named-first-match-only-str",
                "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-str",
                "pattern-subn-callable-quantified-nested-group-named-first-match-only-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((bc)+)d",
                r"a(?P<outer>(?P<inner>bc)+)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "sub"): 2,
                ("module_call", "subn"): 2,
                ("pattern_call", "sub"): 2,
                ("pattern_call", "subn"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "nested_group_alternation_callable_replacement_workflows.py",
        expected_manifest_id="nested-group-alternation-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-group-alternation-numbered-b-branch-str",
                "module-subn-callable-nested-group-alternation-numbered-first-match-only-str",
                "pattern-sub-callable-nested-group-alternation-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-group-alternation-numbered-c-branch-first-match-only-str",
                "module-sub-callable-nested-group-alternation-named-c-branch-str",
                "module-subn-callable-nested-group-alternation-named-first-match-only-str",
                "pattern-sub-callable-nested-group-alternation-named-mixed-branches-str",
                "pattern-subn-callable-nested-group-alternation-named-b-branch-first-match-only-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c))d",
                r"a(?P<outer>(?P<inner>b|c))d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "sub"): 2,
                ("module_call", "subn"): 2,
                ("pattern_call", "sub"): 2,
                ("pattern_call", "subn"): 2,
            }
        ),
    ),
)

COMPILE_PATTERNS = tuple(
    sorted(
        {
            pattern
            for bundle in FIXTURE_BUNDLES
            for pattern in bundle.expected_compile_patterns
        }
    )
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


def _case_string(case: FixtureCase) -> str:
    string_index = 2 if case.operation == "module_call" else 1
    string = case.args[string_index]
    assert isinstance(string, str)
    return string


def _case_count(case: FixtureCase) -> int:
    if "count" in case.kwargs:
        return int(case.kwargs["count"])

    count_index = 3 if case.operation == "module_call" else 2
    if len(case.args) > count_index:
        return int(case.args[count_index])
    return 0


def _case_group_names(case: FixtureCase) -> tuple[str, ...]:
    return tuple(re.compile(_case_pattern(case), case.flags or 0).groupindex)


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.manifest.manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert len(bundle.cases) == len(bundle.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    assert {_case_pattern(case) for case in bundle.cases} == bundle.expected_compile_patterns
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    _, backend = regex_backend

    observed = backend.compile(pattern)
    expected = re.compile(pattern)

    assert observed is backend.compile(pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
    expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)

    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
        use_compiled_pattern=True,
    )
