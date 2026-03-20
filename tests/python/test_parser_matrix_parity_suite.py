from __future__ import annotations

from collections import Counter
import re
from unittest import mock
import warnings

import pytest

import rebar
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT, FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_pattern_parity,
    build_fixture_bundle,
    case_pattern,
    compile_with_cpython_parity,
    load_published_fixture_bundles,
    published_fixture_bundle_by_manifest_id,
)


PARSER_MATRIX_FIXTURE_PATH = CORRECTNESS_FIXTURES_ROOT / "parser_matrix.py"
EXPECTED_CASE_IDS = (
    "str-character-class-ignorecase-success",
    "str-possessive-quantifier-success",
    "str-atomic-group-success",
    "str-fixed-width-lookbehind-success",
    "str-parser-stress-compile-proxy-success",
    "str-variable-width-lookbehind-error",
    "str-nested-set-warning",
    "str-invalid-repeat-error",
    "str-invalid-inline-flag-position-error",
    "str-inline-unicode-flag-success",
    "str-inline-locale-flag-error",
    "bytes-named-backreference-compile-proxy-success",
    "bytes-inline-unicode-flag-error",
    "bytes-inline-locale-flag-success",
    "bytes-unicode-escape-error",
)
# Keep the parser-focused direct parity suite on parser-specific rows; the literal
# baseline compile rows are exercised elsewhere and stay intentionally out of scope here.
KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS = (
    "str-literal-success",
    "bytes-literal-success",
)
CONDITIONAL_ASSERTION_DIAGNOSTIC_FIXTURE_PATH = (
    CORRECTNESS_FIXTURES_ROOT / "conditional_group_exists_assertion_diagnostics.py"
)
EXPECTED_CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS = (
    "conditional-group-exists-assertion-positive-lookahead-error-str",
    "conditional-group-exists-assertion-negative-lookahead-error-str",
)


def _ordered_cases_from_owner_bundle(
    owner_bundle: FixtureBundle,
    ordered_case_ids: tuple[str, ...],
    *,
    error_label: str,
) -> tuple[FixtureCase, ...]:
    duplicate_requested_case_ids = tuple(
        case_id
        for case_id, count in Counter(ordered_case_ids).items()
        if count > 1
    )
    if duplicate_requested_case_ids:
        raise AssertionError(
            f"{error_label} contain duplicate requested case ids: "
            f"{duplicate_requested_case_ids}"
        )

    published_cases = tuple(owner_bundle.manifest.cases)
    duplicate_published_case_ids = tuple(
        case_id
        for case_id, count in Counter(case.case_id for case in published_cases).items()
        if count > 1
    )
    if duplicate_published_case_ids:
        raise AssertionError(
            f"{error_label} owner manifest contains duplicate case ids: "
            f"{duplicate_published_case_ids}"
        )

    case_by_id = {case.case_id: case for case in published_cases}
    missing_case_ids = tuple(
        case_id for case_id in ordered_case_ids if case_id not in case_by_id
    )
    if missing_case_ids:
        raise AssertionError(
            f"{error_label} are missing published fixture rows: {missing_case_ids}"
        )

    return tuple(case_by_id[case_id] for case_id in ordered_case_ids)


OWNER_FIXTURE_BUNDLES = load_published_fixture_bundles(
    (
        PARSER_MATRIX_FIXTURE_PATH,
        CONDITIONAL_ASSERTION_DIAGNOSTIC_FIXTURE_PATH,
    )
)
PARSER_MATRIX_OWNER_BUNDLE = published_fixture_bundle_by_manifest_id(
    OWNER_FIXTURE_BUNDLES,
    "parser-matrix",
)
CONDITIONAL_ASSERTION_DIAGNOSTIC_OWNER_BUNDLE = (
    published_fixture_bundle_by_manifest_id(
        OWNER_FIXTURE_BUNDLES,
        "conditional-group-exists-assertion-diagnostics",
    )
)
TARGET_CASES = _ordered_cases_from_owner_bundle(
    PARSER_MATRIX_OWNER_BUNDLE,
    EXPECTED_CASE_IDS,
    error_label="parser matrix selected case ids",
)
CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES = _ordered_cases_from_owner_bundle(
    CONDITIONAL_ASSERTION_DIAGNOSTIC_OWNER_BUNDLE,
    EXPECTED_CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS,
    error_label="conditional assertion diagnostic selected case ids",
)
PARSER_MATRIX_FIXTURE_BUNDLE = build_fixture_bundle(
    PARSER_MATRIX_OWNER_BUNDLE.manifest,
    TARGET_CASES,
    pattern_extractor=case_pattern,
    expected_case_ids=frozenset(case.case_id for case in TARGET_CASES),
    expected_text_models=frozenset(case.text_model or "str" for case in TARGET_CASES),
)
CONDITIONAL_ASSERTION_DIAGNOSTIC_FIXTURE_BUNDLE = build_fixture_bundle(
    CONDITIONAL_ASSERTION_DIAGNOSTIC_OWNER_BUNDLE.manifest,
    CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES,
    pattern_extractor=case_pattern,
    expected_case_ids=frozenset(
        case.case_id for case in CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES
    ),
    expected_text_models=frozenset(
        case.text_model or "str"
        for case in CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES
    ),
)
PARSER_MATRIX_CASES_BY_ID = {
    case.case_id: case for case in PARSER_MATRIX_FIXTURE_BUNDLE.cases
}


def _case_ids(cases: tuple[FixtureCase, ...]) -> frozenset[str]:
    return frozenset(case.case_id for case in cases)


COMPILE_METADATA_CASES = tuple(
    PARSER_MATRIX_CASES_BY_ID[case_id]
    for case_id in (
        "str-character-class-ignorecase-success",
        "str-possessive-quantifier-success",
        "str-atomic-group-success",
        "str-fixed-width-lookbehind-success",
        "str-parser-stress-compile-proxy-success",
        "str-inline-unicode-flag-success",
        "bytes-named-backreference-compile-proxy-success",
        "bytes-inline-locale-flag-success",
    )
)
PLACEHOLDER_SEARCH_CASES = tuple(
    PARSER_MATRIX_CASES_BY_ID[case_id]
    for case_id in (
        "str-character-class-ignorecase-success",
        "str-possessive-quantifier-success",
        "str-atomic-group-success",
        "str-fixed-width-lookbehind-success",
        "str-parser-stress-compile-proxy-success",
        "str-inline-unicode-flag-success",
        "bytes-named-backreference-compile-proxy-success",
        "bytes-inline-locale-flag-success",
        "str-nested-set-warning",
    )
)
REPEATED_COMPILE_CACHE_CASES = tuple(
    PARSER_MATRIX_CASES_BY_ID[case_id]
    for case_id in (
        "str-possessive-quantifier-success",
        "str-atomic-group-success",
        "str-fixed-width-lookbehind-success",
        "str-parser-stress-compile-proxy-success",
        "str-inline-unicode-flag-success",
        "bytes-named-backreference-compile-proxy-success",
        "bytes-inline-locale-flag-success",
    )
)
DIAGNOSTIC_CASES = tuple(
    PARSER_MATRIX_CASES_BY_ID[case_id]
    for case_id in (
        "str-variable-width-lookbehind-error",
        "str-invalid-repeat-error",
        "str-invalid-inline-flag-position-error",
        "str-inline-locale-flag-error",
        "bytes-inline-unicode-flag-error",
        "bytes-unicode-escape-error",
    )
)
NO_STDLIB_DELEGATION_CASES = tuple(
    PARSER_MATRIX_CASES_BY_ID[case_id]
    for case_id in (
        "str-character-class-ignorecase-success",
        "str-possessive-quantifier-success",
        "str-atomic-group-success",
        "str-fixed-width-lookbehind-success",
        "str-parser-stress-compile-proxy-success",
        "str-variable-width-lookbehind-error",
        "str-inline-unicode-flag-success",
        "bytes-named-backreference-compile-proxy-success",
        "bytes-inline-locale-flag-success",
    )
)
NESTED_SET_WARNING_CASE = PARSER_MATRIX_CASES_BY_ID["str-nested-set-warning"]
CHARACTER_CLASS_CASE = PARSER_MATRIX_CASES_BY_ID[
    "str-character-class-ignorecase-success"
]
PLACEHOLDER_SEARCH_SUBJECTS = {
    "str-character-class-ignorecase-success": "Token_123",
    "str-possessive-quantifier-success": "aaaa",
    "str-atomic-group-success": "ab",
    "str-fixed-width-lookbehind-success": "abc",
    "str-parser-stress-compile-proxy-success": "lemma_12barlemma",
    "str-inline-unicode-flag-success": "a",
    "bytes-named-backreference-compile-proxy-success": b"AA-AA",
    "bytes-inline-locale-flag-success": b"a",
    "str-nested-set-warning": "[[a]",
}


def _parser_matrix_direct_test_case_id_buckets() -> dict[str, frozenset[str]]:
    # Keep the frontier coverage buckets disjoint even though several parser rows
    # are exercised by additional focused tests in this module.
    return {
        "warning-cache": frozenset({NESTED_SET_WARNING_CASE.case_id}),
        "ignorecase-cache-normalization": frozenset(
            {CHARACTER_CLASS_CASE.case_id}
        ),
        "compile-cache": _case_ids(REPEATED_COMPILE_CACHE_CASES),
        "compile-diagnostics": _case_ids(DIAGNOSTIC_CASES),
    }


@pytest.fixture
def rebar_backend(regex_backend: tuple[str, object]) -> object:
    backend_name, backend = regex_backend
    if backend_name != "rebar":
        pytest.skip("rebar-specific parser parity observation")
    return backend


def _compile_case(backend: object, case: FixtureCase) -> object:
    return backend.compile(case_pattern(case), case.flags or 0)


def _warning_summary(
    records: list[warnings.WarningMessage],
) -> list[tuple[type[Warning], str]]:
    return [(record.category, str(record.message)) for record in records]


def _compile_case_with_warnings(
    backend: object,
    case: FixtureCase,
) -> tuple[object, list[tuple[type[Warning], str]]]:
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        compiled = _compile_case(backend, case)
    return compiled, _warning_summary(caught_warnings)


def _assert_compile_error_parity(backend: object, case: FixtureCase) -> BaseException:
    pattern = case_pattern(case)
    flags = case.flags or 0

    with pytest.raises(re.error) as expected:
        re.compile(pattern, flags)
    with pytest.raises(backend.error) as actual:
        backend.compile(pattern, flags)

    expected_error = expected.value
    actual_error = actual.value

    assert type(actual_error) is type(expected_error)
    assert str(actual_error) == str(expected_error)
    assert actual_error.pos == expected_error.pos
    assert actual_error.lineno == expected_error.lineno
    assert actual_error.colno == expected_error.colno
    return actual_error


def test_parser_matrix_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert_fixture_bundle_contract(
        PARSER_MATRIX_FIXTURE_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=PARSER_MATRIX_FIXTURE_PATH,
        expected_ordered_case_ids=EXPECTED_CASE_IDS,
    )


def test_parser_matrix_parity_suite_tracks_published_case_frontier() -> None:
    assert_fixture_bundle_tracks_published_case_frontier(
        PARSER_MATRIX_FIXTURE_BUNDLE,
        selected_case_ids=EXPECTED_CASE_IDS,
        expected_uncovered_case_ids=KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS,
    )


def test_parser_matrix_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        _parser_matrix_direct_test_case_id_buckets(),
        selected_case_ids=EXPECTED_CASE_IDS,
        coverage_label="parser matrix direct-test case-id buckets",
    )


def test_conditional_assertion_diagnostic_fixture_stays_aligned_with_published_correctness_fixture() -> None:
    assert_fixture_bundle_contract(
        CONDITIONAL_ASSERTION_DIAGNOSTIC_FIXTURE_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=CONDITIONAL_ASSERTION_DIAGNOSTIC_FIXTURE_PATH,
        expected_ordered_case_ids=EXPECTED_CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS,
    )


@pytest.mark.parametrize("case", COMPILE_METADATA_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )


def test_nested_set_warning_matches_cpython_and_re_emits_after_purge(
    rebar_backend: object,
) -> None:
    pattern = case_pattern(NESTED_SET_WARNING_CASE)
    flags = NESTED_SET_WARNING_CASE.flags or 0

    with warnings.catch_warnings(record=True) as expected_warnings:
        warnings.simplefilter("always")
        expected = re.compile(pattern, flags)

    first, first_warnings = _compile_case_with_warnings(
        rebar_backend,
        NESTED_SET_WARNING_CASE,
    )
    second, second_warnings = _compile_case_with_warnings(
        rebar_backend,
        NESTED_SET_WARNING_CASE,
    )

    assert first_warnings == _warning_summary(expected_warnings)
    assert second_warnings == []
    assert first is second
    assert_pattern_parity("rebar", first, expected)

    rebar_backend.purge()

    refreshed, refreshed_warnings = _compile_case_with_warnings(
        rebar_backend,
        NESTED_SET_WARNING_CASE,
    )

    assert refreshed is not first
    assert refreshed_warnings == first_warnings


@pytest.mark.parametrize(
    "case",
    PLACEHOLDER_SEARCH_CASES,
    ids=lambda case: case.case_id,
)
def test_compile_only_rows_keep_rebar_search_placeholder(
    rebar_backend: object,
    case: FixtureCase,
) -> None:
    if case.case_id == NESTED_SET_WARNING_CASE.case_id:
        compiled, _ = _compile_case_with_warnings(rebar_backend, case)
    else:
        compiled, _ = compile_with_cpython_parity(
            "rebar",
            rebar_backend,
            case_pattern(case),
            case.flags or 0,
        )

    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.Pattern\.search\(\) is a scaffold placeholder",
    ):
        compiled.search(PLACEHOLDER_SEARCH_SUBJECTS[case.case_id])


def test_character_class_cache_normalizes_ignorecase_and_unicode_flags(
    rebar_backend: object,
) -> None:
    pattern = case_pattern(CHARACTER_CLASS_CASE)
    ignorecase_flags = CHARACTER_CLASS_CASE.flags or 0

    first = rebar_backend.compile(pattern, ignorecase_flags)
    second = rebar_backend.compile(pattern, ignorecase_flags | rebar_backend.UNICODE)

    assert first is second

    rebar_backend.purge()

    refreshed = rebar_backend.compile(pattern, ignorecase_flags)
    assert refreshed is not first


@pytest.mark.parametrize(
    "case",
    REPEATED_COMPILE_CACHE_CASES,
    ids=lambda case: case.case_id,
)
def test_compile_cache_identity_and_purge_for_supported_parser_rows(
    rebar_backend: object,
    case: FixtureCase,
) -> None:
    first = _compile_case(rebar_backend, case)
    second = _compile_case(rebar_backend, case)

    assert first is second

    rebar_backend.purge()

    refreshed = _compile_case(rebar_backend, case)
    assert refreshed is not first


@pytest.mark.parametrize("case", DIAGNOSTIC_CASES, ids=lambda case: case.case_id)
def test_compile_diagnostics_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    actual_error = _assert_compile_error_parity(backend, case)

    if case.case_id == "str-variable-width-lookbehind-error":
        assert str(actual_error) == "look-behind requires fixed-width pattern"
        assert actual_error.pos is None
        assert actual_error.lineno is None
        assert actual_error.colno is None


@pytest.mark.parametrize(
    "case",
    CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES,
    ids=lambda case: case.case_id,
)
def test_conditional_assertion_compile_diagnostics_match_cpython(
    rebar_backend: object,
    case: FixtureCase,
) -> None:
    _assert_compile_error_parity(rebar_backend, case)


@pytest.mark.parametrize(
    "case",
    NO_STDLIB_DELEGATION_CASES,
    ids=lambda case: case.case_id,
)
def test_rebar_compile_does_not_delegate_to_stdlib_for_selected_parser_rows(
    rebar_backend: object,
    case: FixtureCase,
) -> None:
    pattern = case_pattern(case)
    flags = case.flags or 0

    if case.case_id == "str-variable-width-lookbehind-error":
        with pytest.raises(re.error) as expected:
            re.compile(pattern, flags)

        with mock.patch.object(
            rebar._stdlib_re,
            "compile",
            side_effect=AssertionError("stdlib re.compile() should not be used"),
        ):
            with pytest.raises(rebar_backend.error) as actual:
                rebar_backend.compile(pattern, flags)

        expected_error = expected.value
        actual_error = actual.value
        assert type(actual_error) is type(expected_error)
        assert str(actual_error) == str(expected_error)
        assert actual_error.pos == expected_error.pos
        assert actual_error.lineno == expected_error.lineno
        assert actual_error.colno == expected_error.colno
        assert str(actual_error) == "look-behind requires fixed-width pattern"
        return

    expected = re.compile(pattern, flags)

    with mock.patch.object(
        rebar._stdlib_re,
        "compile",
        side_effect=AssertionError("stdlib re.compile() should not be used"),
    ):
        observed = rebar_backend.compile(pattern, flags)
        assert observed is rebar_backend.compile(pattern, flags)

    assert_pattern_parity("rebar", observed, expected)
