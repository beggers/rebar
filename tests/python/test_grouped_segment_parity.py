from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import (
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    select_published_fixture_paths,
)


EXPECTED_PUBLISHED_FIXTURE_NAMES = ("grouped_segment_workflows.py",)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_GROUPED_SEGMENT_FIXTURE_PATHS = select_published_fixture_paths(
    EXPECTED_PUBLISHED_FIXTURE_PATHS
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


@dataclass(frozen=True)
class TextCase:
    id: str
    case_id: str
    text: str


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


FIXTURE_BUNDLE = _fixture_bundle(
    "grouped_segment_workflows.py",
    expected_manifest_id="grouped-segment-workflows",
    expected_case_ids=frozenset(
        {
            "grouped-segment-compile-metadata-str",
            "grouped-segment-module-search-str",
            "grouped-segment-pattern-fullmatch-str",
            "named-grouped-segment-compile-metadata-str",
            "named-grouped-segment-module-search-str",
            "named-grouped-segment-pattern-fullmatch-str",
        }
    ),
    expected_patterns=frozenset(
        {
            r"a(b)c",
            r"a(?P<word>b)c",
        }
    ),
    expected_operation_helper_counts=Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 2,
            ("pattern_call", "fullmatch"): 2,
        }
    ),
)

PUBLISHED_CASES = FIXTURE_BUNDLE.cases
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")
MATCH_CASES = MODULE_CASES + PATTERN_CASES
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}
MODULE_MISS_CASES = (
    TextCase(
        id="numbered-module-search-no-match",
        case_id="grouped-segment-module-search-str",
        text="zzz",
    ),
    TextCase(
        id="named-module-search-no-match",
        case_id="named-grouped-segment-module-search-str",
        text="zzz",
    ),
)
PATTERN_MISS_CASES = (
    TextCase(
        id="numbered-pattern-fullmatch-no-match",
        case_id="grouped-segment-pattern-fullmatch-str",
        text="abcz",
    ),
    TextCase(
        id="named-pattern-fullmatch-no-match",
        case_id="named-grouped-segment-pattern-fullmatch-str",
        text="abcz",
    ),
)


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


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


def _module_call_with_text(regex_api: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "module_call"
    assert case.helper is not None

    return getattr(regex_api, case.helper)(
        _case_pattern(case),
        text,
        *case.args[2:],
        **case.kwargs,
    )


def _pattern_call_with_text(compiled_pattern: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "pattern_call"
    assert case.helper is not None

    return getattr(compiled_pattern, case.helper)(text, *case.args[1:], **case.kwargs)


def test_grouped_segment_parity_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_GROUPED_SEGMENT_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert FIXTURE_BUNDLE.manifest.manifest_id == FIXTURE_BUNDLE.expected_manifest_id
    assert len({case.case_id for case in FIXTURE_BUNDLE.cases}) == len(FIXTURE_BUNDLE.cases)
    assert {case.case_id for case in FIXTURE_BUNDLE.cases} == FIXTURE_BUNDLE.expected_case_ids
    assert {_case_pattern(case) for case in FIXTURE_BUNDLE.cases} == FIXTURE_BUNDLE.expected_patterns
    assert {case.text_model for case in FIXTURE_BUNDLE.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in FIXTURE_BUNDLE.cases) == (
        FIXTURE_BUNDLE.expected_operation_helper_counts
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
        case.pattern_payload(),
        case.flags or 0,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", MATCH_CASES, ids=lambda case: case.case_id)
def test_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_CASES, ids=lambda case: case.case_id)
def test_valid_match_group_accessors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)
    assert_valid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_CASES, ids=lambda case: case.case_id)
def test_invalid_match_group_access_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MODULE_MISS_CASES, ids=lambda case: case.id)
def test_module_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: TextCase,
) -> None:
    _, backend = regex_backend
    fixture_case = CASES_BY_ID[case.case_id]

    assert _module_call_with_text(backend, fixture_case, case.text) is None
    assert _module_call_with_text(re, fixture_case, case.text) is None


@pytest.mark.parametrize("case", PATTERN_MISS_CASES, ids=lambda case: case.id)
def test_pattern_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: TextCase,
) -> None:
    backend_name, backend = regex_backend
    fixture_case = CASES_BY_ID[case.case_id]

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        fixture_case.pattern_payload(),
        fixture_case.flags or 0,
    )

    assert _pattern_call_with_text(observed_pattern, fixture_case, case.text) is None
    assert _pattern_call_with_text(expected_pattern, fixture_case, case.text) is None
