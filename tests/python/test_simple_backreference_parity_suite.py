from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest

from rebar_harness.correctness import (
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)
from tests.python.fixture_parity_support import (
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    select_published_fixture_paths,
    str_case_pattern,
)


FIXTURES_DIR = pathlib.Path(__file__).resolve().parents[1] / "conformance" / "fixtures"
EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "named_backreference_workflows.py",
    "numbered_backreference_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_SIMPLE_BACKREFERENCE_FIXTURE_PATHS = select_published_fixture_paths(
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
class SupplementalMissCase:
    id: str
    module_case_id: str
    pattern_case_id: str
    misses: tuple[str, ...]


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
        "named_backreference_workflows.py",
        expected_manifest_id="named-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "named-backreference-compile-metadata-str",
                "named-backreference-module-search-str",
                "named-backreference-pattern-search-str",
            }
        ),
        expected_patterns=frozenset({r"(?P<word>ab)(?P=word)"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
    _fixture_bundle(
        "numbered_backreference_workflows.py",
        expected_manifest_id="numbered-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "numbered-backreference-compile-metadata-str",
                "numbered-backreference-module-search-str",
                "numbered-backreference-pattern-search-str",
            }
        ),
        expected_patterns=frozenset({r"(ab)\1"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
)

PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
MATCH_CASES = tuple(
    case for case in PUBLISHED_CASES if case.operation in {"module_call", "pattern_call"}
)
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}
SUPPLEMENTAL_MISS_CASES = (
    SupplementalMissCase(
        id="named-backreference-search-misses",
        module_case_id="named-backreference-module-search-str",
        pattern_case_id="named-backreference-pattern-search-str",
        misses=("zzabzz", "zzz"),
    ),
    SupplementalMissCase(
        id="numbered-backreference-search-misses",
        module_case_id="numbered-backreference-module-search-str",
        pattern_case_id="numbered-backreference-pattern-search-str",
        misses=("zzabzz", "zzz"),
    ),
)


def _module_call_with_text(regex_api: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "module_call"
    assert case.helper is not None

    return getattr(regex_api, case.helper)(
        str_case_pattern(case),
        text,
        *case.args[2:],
        **case.kwargs,
    )


def _pattern_call_with_text(compiled_pattern: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "pattern_call"
    assert case.helper is not None

    return getattr(compiled_pattern, case.helper)(text, *case.args[1:], **case.kwargs)


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


def test_simple_backreference_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_SIMPLE_BACKREFERENCE_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
    assert len({case.case_id for case in PUBLISHED_CASES}) == len(PUBLISHED_CASES)


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
    assert {str_case_pattern(case) for case in bundle.cases} == bundle.expected_patterns
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
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


@pytest.mark.parametrize("case", MATCH_CASES, ids=lambda case: case.case_id)
def test_search_results_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_search_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    backend_name, backend = regex_backend
    module_case = CASES_BY_ID[case.module_case_id]
    pattern_case = CASES_BY_ID[case.pattern_case_id]

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern_case.pattern_payload(),
        pattern_case.flags or 0,
    )

    for text in case.misses:
        assert _module_call_with_text(backend, module_case, text) is None
        assert _module_call_with_text(re, module_case, text) is None
        assert _pattern_call_with_text(observed_pattern, pattern_case, text) is None
        assert _pattern_call_with_text(expected_pattern, pattern_case, text) is None
