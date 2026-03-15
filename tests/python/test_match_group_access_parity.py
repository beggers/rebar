from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness.correctness import FixtureCase, FixtureManifest, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_match_result_parity,
    case_pattern,
    compile_with_cpython_parity,
    select_published_fixture_paths,
)


EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "grouped_match_workflows.py",
    "named_group_workflows.py",
    "optional_group_workflows.py",
    "nested_group_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_MATCH_GROUP_ACCESS_FIXTURE_PATHS = select_published_fixture_paths(
    EXPECTED_PUBLISHED_FIXTURE_PATHS
)
ACCESSOR_NAMES = ("group", "span", "start", "end", "getitem")


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str]]


def _fixture_bundle(
    fixture_name: str,
    *,
    selected_case_ids: tuple[str, ...],
    expected_manifest_id: str,
    expected_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    case_by_id = {case.case_id: case for case in cases}
    missing_case_ids = tuple(case_id for case_id in selected_case_ids if case_id not in case_by_id)
    if missing_case_ids:
        raise ValueError(
            f"{fixture_name} is missing expected match-group-access rows: {missing_case_ids}"
        )

    return FixtureBundle(
        manifest=manifest,
        cases=tuple(case_by_id[case_id] for case_id in selected_case_ids),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=frozenset(selected_case_ids),
        expected_patterns=expected_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "grouped_match_workflows.py",
        selected_case_ids=(
            "grouped-module-search-single-capture-str",
            "grouped-pattern-search-single-capture-str",
        ),
        expected_manifest_id="grouped-match-workflows",
        expected_patterns=frozenset({r"(abc)"}),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
    _fixture_bundle(
        "named_group_workflows.py",
        selected_case_ids=(
            "named-group-module-search-metadata-str",
            "named-group-pattern-search-metadata-str",
        ),
        expected_manifest_id="named-group-workflows",
        expected_patterns=frozenset({r"(?P<word>abc)"}),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
    _fixture_bundle(
        "optional_group_workflows.py",
        selected_case_ids=(
            "systematic-optional-group-numbered-module-search-absent-str",
            "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
            "systematic-optional-group-named-module-search-absent-str",
            "systematic-optional-group-named-pattern-fullmatch-absent-str",
        ),
        expected_manifest_id="optional-group-workflows",
        expected_patterns=frozenset(
            {
                r"a(b)?d",
                r"a(?P<word>b)?d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "nested_group_workflows.py",
        selected_case_ids=(
            "nested-group-module-search-str",
            "nested-group-pattern-fullmatch-str",
            "named-nested-group-module-search-str",
            "named-nested-group-pattern-fullmatch-str",
        ),
        expected_manifest_id="nested-group-workflows",
        expected_patterns=frozenset(
            {
                r"a((b))d",
                r"a(?P<outer>(?P<inner>b))d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)


def _match_for_case(
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str]]:
    assert case.helper is not None
    if case.operation == "module_call":
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)
    else:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern_payload(),
            case.flags or 0,
        )
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    return observed, expected


def _valid_group_references(expected: re.Match[str]) -> tuple[int | str, ...]:
    return (*range(expected.re.groups + 1), *expected.re.groupindex)


def _invalid_group_references(expected: re.Match[str]) -> tuple[int | str, ...]:
    missing_name = "missing"
    while missing_name in expected.re.groupindex:
        missing_name += "_group"
    return (-1, expected.re.groups + 1, missing_name)


def _apply_accessor(
    match: object,
    accessor_name: str,
    reference: int | str,
) -> object:
    if accessor_name == "group":
        return match.group(reference)
    if accessor_name == "span":
        return match.span(reference)
    if accessor_name == "start":
        return match.start(reference)
    if accessor_name == "end":
        return match.end(reference)
    if accessor_name == "getitem":
        return match[reference]
    raise AssertionError(f"unknown accessor {accessor_name!r}")


def _capture_accessor_error(
    match: object,
    accessor_name: str,
    reference: int | str,
) -> BaseException:
    try:
        _apply_accessor(match, accessor_name, reference)
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError(
        f"expected {accessor_name}({reference!r}) to raise for {match.re.pattern!r}"
    )


def test_match_group_access_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_MATCH_GROUP_ACCESS_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
    assert len({case.case_id for case in PUBLISHED_CASES}) == len(PUBLISHED_CASES)


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_match_group_access_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert bundle.manifest.manifest_id == bundle.expected_manifest_id
    assert len(bundle.cases) == len(bundle.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    assert {case_pattern(case) for case in bundle.cases} == bundle.expected_patterns
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


@pytest.mark.parametrize("case", PUBLISHED_CASES, ids=lambda case: case.case_id)
def test_match_getitem_matches_cpython_for_valid_group_references(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_result_parity(backend_name, observed, expected)
    for reference in _valid_group_references(expected):
        assert observed[reference] == expected[reference]


@pytest.mark.parametrize("case", PUBLISHED_CASES, ids=lambda case: case.case_id)
def test_invalid_match_group_access_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_result_parity(backend_name, observed, expected)
    for reference in _invalid_group_references(expected):
        for accessor_name in ACCESSOR_NAMES:
            expected_error = _capture_accessor_error(expected, accessor_name, reference)
            observed_error = _capture_accessor_error(observed, accessor_name, reference)

            assert type(observed_error) is type(expected_error)
            assert observed_error.args == expected_error.args
