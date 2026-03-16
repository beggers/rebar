from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import (
    FixtureCase,
    SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    manifest_case_ids,
    published_fixture_paths_from_bundles,
    str_case_pattern,
)

PUBLISHED_SIMPLE_BACKREFERENCE_FIXTURE_PATHS = select_correctness_fixture_paths(
    SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR
)
TARGET_FIXTURE_CASE_IDS = (
    "named-backreference-compile-metadata-str",
    "named-backreference-module-search-str",
    "named-backreference-pattern-search-str",
    "numbered-backreference-compile-metadata-str",
    "numbered-backreference-module-search-str",
    "numbered-backreference-pattern-search-str",
)
KNOWN_UNSUPPORTED_CASE_IDS = (
    "numbered-backreference-segment-module-search-str",
    "numbered-backreference-prefix-pattern-search-str",
)
MATCH_CASE_ID_BUCKET = frozenset(
    {
        "named-backreference-module-search-str",
        "named-backreference-pattern-search-str",
        "numbered-backreference-module-search-str",
        "numbered-backreference-pattern-search-str",
    }
)

@dataclass(frozen=True)
class SupplementalMissCase:
    id: str
    module_case_id: str
    pattern_case_id: str
    misses: tuple[str, ...]

FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "named_backreference_workflows.py",
        expected_manifest_id="named-backreference-workflows",
        selected_case_ids=TARGET_FIXTURE_CASE_IDS[:3],
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
    FixtureBundleSpec(
        "numbered_backreference_workflows.py",
        expected_manifest_id="numbered-backreference-workflows",
        selected_case_ids=TARGET_FIXTURE_CASE_IDS[3:],
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
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
PUBLISHED_CASE_IDS = tuple(
    case_id
    for bundle in FIXTURE_BUNDLES
    for case_id in manifest_case_ids(bundle)
)
SELECTED_CASES = fixture_cases_from_bundles(FIXTURE_BUNDLES)
COMPILE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
MATCH_CASES = tuple(
    case for case in SELECTED_CASES if case.operation in {"module_call", "pattern_call"}
)
CASES_BY_ID = {case.case_id: case for case in SELECTED_CASES}
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
    assert PUBLISHED_SIMPLE_BACKREFERENCE_FIXTURE_PATHS == published_fixture_paths_from_bundles(
        FIXTURE_BUNDLES
    )
    assert len(set(PUBLISHED_CASE_IDS)) == len(PUBLISHED_CASE_IDS)


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


def test_simple_backreference_parity_suite_tracks_published_case_frontier() -> None:
    selected_case_ids = frozenset(TARGET_FIXTURE_CASE_IDS)
    uncovered_case_ids = tuple(
        case_id for case_id in PUBLISHED_CASE_IDS if case_id not in selected_case_ids
    )

    assert uncovered_case_ids == KNOWN_UNSUPPORTED_CASE_IDS
    assert frozenset(PUBLISHED_CASE_IDS) == (
        selected_case_ids | frozenset(KNOWN_UNSUPPORTED_CASE_IDS)
    )


def test_simple_backreference_direct_match_and_miss_parametrizations_stay_supported_only() -> None:
    direct_match_case_ids = frozenset(case.case_id for case in MATCH_CASES)
    supplemental_case_ids = frozenset(
        case_id
        for miss_case in SUPPLEMENTAL_MISS_CASES
        for case_id in (miss_case.module_case_id, miss_case.pattern_case_id)
    )

    assert direct_match_case_ids == MATCH_CASE_ID_BUCKET
    assert supplemental_case_ids == MATCH_CASE_ID_BUCKET
    assert not (frozenset(KNOWN_UNSUPPORTED_CASE_IDS) & direct_match_case_ids)
    assert not (frozenset(KNOWN_UNSUPPORTED_CASE_IDS) & supplemental_case_ids)


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
