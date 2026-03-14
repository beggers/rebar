from __future__ import annotations

from collections import Counter
import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest


OPTIONAL_GROUP_FIXTURE_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "optional_group_workflows.py"
)
NESTED_EMPTY_ELSE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_else_nested_workflows.py"
)

EXPECTED_SYSTEMATIC_CASE_IDS_BY_MANIFEST = {
    "optional-group-workflows": (
        "systematic-optional-group-numbered-compile-metadata-str",
        "systematic-optional-group-numbered-module-search-present-str",
        "systematic-optional-group-numbered-module-search-absent-str",
        "systematic-optional-group-numbered-pattern-fullmatch-present-str",
        "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
        "systematic-optional-group-named-compile-metadata-str",
        "systematic-optional-group-named-module-search-present-str",
        "systematic-optional-group-named-module-search-absent-str",
        "systematic-optional-group-named-pattern-fullmatch-present-str",
        "systematic-optional-group-named-pattern-fullmatch-absent-str",
    ),
    "conditional-group-exists-empty-else-nested-workflows": (
        "systematic-conditional-group-exists-empty-else-nested-numbered-compile-metadata-str",
        "systematic-conditional-group-exists-empty-else-nested-numbered-module-search-present-str",
        "systematic-conditional-group-exists-empty-else-nested-numbered-module-fullmatch-missing-suffix-str",
        "systematic-conditional-group-exists-empty-else-nested-numbered-pattern-fullmatch-absent-str",
        "systematic-conditional-group-exists-empty-else-nested-named-compile-metadata-str",
        "systematic-conditional-group-exists-empty-else-nested-named-module-search-present-str",
        "systematic-conditional-group-exists-empty-else-nested-named-module-fullmatch-missing-suffix-str",
        "systematic-conditional-group-exists-empty-else-nested-named-pattern-fullmatch-absent-str",
    ),
}
EXPECTED_OPERATION_COUNTS = Counter({"module_call": 8, "pattern_call": 6, "compile": 4})
MISSING_GROUP_DEFAULT = object()


def _load_systematic_cases() -> dict[str, tuple[FixtureCase, ...]]:
    manifest_cases: dict[str, tuple[FixtureCase, ...]] = {}
    for path in (OPTIONAL_GROUP_FIXTURE_PATH, NESTED_EMPTY_ELSE_FIXTURE_PATH):
        manifest, cases = load_fixture_manifest(path)
        manifest_cases[manifest.manifest_id] = tuple(
            case for case in cases if "systematic" in case.categories
        )
    return manifest_cases


SYSTEMATIC_CASES_BY_MANIFEST = _load_systematic_cases()
SYSTEMATIC_COMPILE_CASES = tuple(
    case
    for manifest_id in sorted(SYSTEMATIC_CASES_BY_MANIFEST)
    for case in SYSTEMATIC_CASES_BY_MANIFEST[manifest_id]
    if case.operation == "compile"
)
SYSTEMATIC_MATCH_CASES = tuple(
    case
    for manifest_id in sorted(SYSTEMATIC_CASES_BY_MANIFEST)
    for case in SYSTEMATIC_CASES_BY_MANIFEST[manifest_id]
    if case.operation != "compile"
)


def _assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str] | re.Pattern[bytes],
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
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    group_indexes = tuple(range(expected.re.groups + 1))

    assert observed.group(0) == expected.group(0)
    assert observed.group(*group_indexes) == expected.group(*group_indexes)

    for group_index in range(1, expected.re.groups + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groups(MISSING_GROUP_DEFAULT) == expected.groups(MISSING_GROUP_DEFAULT)
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(MISSING_GROUP_DEFAULT) == expected.groupdict(
        MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.span() == expected.span()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    assert observed.re.pattern == expected.re.pattern
    assert observed.re.flags == expected.re.flags
    assert observed.re.groups == expected.re.groups
    assert observed.re.groupindex == expected.re.groupindex

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def test_folded_systematic_capture_corpus_stays_embedded_in_standard_manifests() -> None:
    assert set(SYSTEMATIC_CASES_BY_MANIFEST) == set(EXPECTED_SYSTEMATIC_CASE_IDS_BY_MANIFEST)

    actual_case_ids_by_manifest = {
        manifest_id: tuple(case.case_id for case in cases)
        for manifest_id, cases in SYSTEMATIC_CASES_BY_MANIFEST.items()
    }
    assert actual_case_ids_by_manifest == EXPECTED_SYSTEMATIC_CASE_IDS_BY_MANIFEST
    assert sum(len(case_ids) for case_ids in actual_case_ids_by_manifest.values()) == 18
    assert Counter(case.operation for case in SYSTEMATIC_COMPILE_CASES + SYSTEMATIC_MATCH_CASES) == (
        EXPECTED_OPERATION_COUNTS
    )

    for cases in SYSTEMATIC_CASES_BY_MANIFEST.values():
        for case in cases:
            assert case.layer == "match_behavior"
            assert case.text_model == "str"
            assert "systematic" in case.categories
            assert "landed-slice" in case.categories


@pytest.mark.parametrize("case", SYSTEMATIC_COMPILE_CASES, ids=lambda case: case.case_id)
def test_systematic_capture_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.compile(case.pattern_payload(), case.flags or 0)
    expected = re.compile(case.pattern_payload(), case.flags or 0)

    _assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", SYSTEMATIC_MATCH_CASES, ids=lambda case: case.case_id)
def test_systematic_capture_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    if case.operation == "module_call":
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)
    else:
        observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
        expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    if expected is None:
        assert observed is None
        return

    assert observed is not None
    _assert_match_parity(backend_name, observed, expected)
