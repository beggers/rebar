from __future__ import annotations

import re
from unittest import mock
import warnings

import pytest

import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_pattern_parity,
    case_pattern,
    compile_with_cpython_parity,
)


PARSER_MATRIX_FIXTURE_PATH = FIXTURES_DIR / "parser_matrix.py"
PARSER_MATRIX_MANIFEST, PARSER_MATRIX_FIXTURE_CASES = load_fixture_manifest(
    PARSER_MATRIX_FIXTURE_PATH
)
PARSER_MATRIX_CASES_BY_ID = {
    case.case_id: case for case in PARSER_MATRIX_FIXTURE_CASES
}

EXPECTED_CASE_IDS = (
    "str-character-class-ignorecase-success",
    "str-possessive-quantifier-success",
    "str-atomic-group-success",
    "str-fixed-width-lookbehind-success",
    "str-variable-width-lookbehind-error",
    "str-nested-set-warning",
    "str-invalid-repeat-error",
    "str-invalid-inline-flag-position-error",
    "str-inline-unicode-flag-success",
    "str-inline-locale-flag-error",
    "bytes-inline-unicode-flag-error",
    "bytes-inline-locale-flag-success",
    "bytes-unicode-escape-error",
)
TARGET_CASES = tuple(PARSER_MATRIX_CASES_BY_ID[case_id] for case_id in EXPECTED_CASE_IDS)

COMPILE_METADATA_CASES = tuple(
    PARSER_MATRIX_CASES_BY_ID[case_id]
    for case_id in (
        "str-character-class-ignorecase-success",
        "str-possessive-quantifier-success",
        "str-atomic-group-success",
        "str-fixed-width-lookbehind-success",
        "str-inline-unicode-flag-success",
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
        "str-inline-unicode-flag-success",
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
        "str-inline-unicode-flag-success",
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
        "str-variable-width-lookbehind-error",
        "str-inline-unicode-flag-success",
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
    "str-inline-unicode-flag-success": "a",
    "bytes-inline-locale-flag-success": b"a",
    "str-nested-set-warning": "[[a]",
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
    assert PARSER_MATRIX_MANIFEST.path == PARSER_MATRIX_FIXTURE_PATH
    assert PARSER_MATRIX_MANIFEST.manifest_id == "parser-matrix"
    assert len(TARGET_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in TARGET_CASES} == set(EXPECTED_CASE_IDS)
    assert {case.operation for case in TARGET_CASES} == {"compile"}
    assert {case.helper for case in TARGET_CASES} == {None}


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
