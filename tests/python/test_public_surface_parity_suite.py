from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import (
    FixtureCase,
    normalize_exported_symbol_metadata,
    normalize_exported_symbol_value,
    normalize_pattern_object_metadata,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_fixture_bundles,
    published_fixture_bundle_by_manifest_id,
)


PUBLIC_API_CASE_IDS = (
    "helper-compile-present",
    "helper-search-present",
    "helper-purge-present",
    "purge-noop-success",
    "compile-pattern-scaffold-success",
    "search-literal-success",
    "escape-success",
)
EXPORTED_SYMBOL_CASE_IDS = (
    "regexflag-type-metadata",
    "error-type-metadata",
    "pattern-type-metadata",
    "match-type-metadata",
    "ascii-constant-value",
    "ignorecase-constant-value",
    "noflag-constant-value",
    "debug-constant-value",
    "pattern-constructor-guard",
    "match-constructor-guard",
)
PATTERN_OBJECT_CASE_IDS = (
    "pattern-object-str-metadata",
    "pattern-object-str-ignorecase-metadata",
    "pattern-object-bytes-ignorecase-metadata",
    "pattern-search-literal-success",
    "pattern-match-literal-success",
    "pattern-fullmatch-literal-success",
)

# These manifests include helper-presence and exported-attribute rows that do not
# have a regex pattern payload, so the contract check anchors on stable case ids.
FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        fixture_name="public_api_surface.py",
        expected_manifest_id="public-api-surface",
        selected_case_ids=PUBLIC_API_CASE_IDS,
        expected_patterns=frozenset(PUBLIC_API_CASE_IDS),
        expected_operation_helper_counts=Counter(
            {
                ("module_has_attr", "compile"): 1,
                ("module_has_attr", "search"): 1,
                ("module_has_attr", "purge"): 1,
                ("module_call", "purge"): 1,
                ("module_call", "compile"): 1,
                ("module_call", "search"): 1,
                ("module_call", "escape"): 1,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="exported_symbol_surface.py",
        expected_manifest_id="exported-symbol-surface",
        selected_case_ids=EXPORTED_SYMBOL_CASE_IDS,
        expected_patterns=frozenset(EXPORTED_SYMBOL_CASE_IDS),
        expected_operation_helper_counts=Counter(
            {
                ("module_attr_metadata", "RegexFlag"): 1,
                ("module_attr_metadata", "error"): 1,
                ("module_attr_metadata", "Pattern"): 1,
                ("module_attr_metadata", "Match"): 1,
                ("module_attr_value", "ASCII"): 1,
                ("module_attr_value", "IGNORECASE"): 1,
                ("module_attr_value", "NOFLAG"): 1,
                ("module_attr_value", "DEBUG"): 1,
                ("module_call", "Pattern"): 1,
                ("module_call", "Match"): 1,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="pattern_object_surface.py",
        expected_manifest_id="pattern-object-surface",
        selected_case_ids=PATTERN_OBJECT_CASE_IDS,
        expected_patterns=frozenset(PATTERN_OBJECT_CASE_IDS),
        expected_operation_helper_counts=Counter(
            {
                ("pattern_metadata", None): 3,
                ("pattern_call", "search"): 1,
                ("pattern_call", "match"): 1,
                ("pattern_call", "fullmatch"): 1,
            }
        ),
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
PUBLIC_API_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "public-api-surface",
)
EXPORTED_SYMBOL_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "exported-symbol-surface",
)
PATTERN_OBJECT_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "pattern-object-surface",
)

PUBLIC_HELPER_CASES = fixture_cases_for_operation((PUBLIC_API_BUNDLE,), "module_has_attr")
PUBLIC_MODULE_CALL_CASES = fixture_cases_for_operation((PUBLIC_API_BUNDLE,), "module_call")
EXPORTED_METADATA_CASES = fixture_cases_for_operation(
    (EXPORTED_SYMBOL_BUNDLE,),
    "module_attr_metadata",
)
EXPORTED_VALUE_CASES = fixture_cases_for_operation(
    (EXPORTED_SYMBOL_BUNDLE,),
    "module_attr_value",
)
EXPORTED_CONSTRUCTOR_GUARD_CASES = fixture_cases_for_operation(
    (EXPORTED_SYMBOL_BUNDLE,),
    "module_call",
)
PATTERN_METADATA_CASES = fixture_cases_for_operation(
    (PATTERN_OBJECT_BUNDLE,),
    "pattern_metadata",
)
PATTERN_CALL_CASES = fixture_cases_for_operation((PATTERN_OBJECT_BUNDLE,), "pattern_call")

DIRECT_TEST_CASE_ID_BUCKETS = {
    "public-helper-presence": frozenset(case.case_id for case in PUBLIC_HELPER_CASES),
    "public-module-call": frozenset(case.case_id for case in PUBLIC_MODULE_CALL_CASES),
    "exported-symbol-metadata": frozenset(case.case_id for case in EXPORTED_METADATA_CASES),
    "exported-symbol-value": frozenset(case.case_id for case in EXPORTED_VALUE_CASES),
    "exported-constructor-guard": frozenset(
        case.case_id for case in EXPORTED_CONSTRUCTOR_GUARD_CASES
    ),
    "pattern-object-metadata": frozenset(case.case_id for case in PATTERN_METADATA_CASES),
    "pattern-object-call": frozenset(case.case_id for case in PATTERN_CALL_CASES),
}
SELECTED_CASE_IDS_BY_MANIFEST = {
    PUBLIC_API_BUNDLE.expected_manifest_id: PUBLIC_API_CASE_IDS,
    EXPORTED_SYMBOL_BUNDLE.expected_manifest_id: EXPORTED_SYMBOL_CASE_IDS,
    PATTERN_OBJECT_BUNDLE.expected_manifest_id: PATTERN_OBJECT_CASE_IDS,
}
PUBLIC_SURFACE_SELECTED_CASE_IDS = (
    *PUBLIC_API_CASE_IDS,
    *EXPORTED_SYMBOL_CASE_IDS,
    *PATTERN_OBJECT_CASE_IDS,
)


def _case_contract_token(case: FixtureCase) -> str:
    return case.case_id


def _capture_error(callback) -> BaseException:
    try:
        callback()
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError("expected call to raise")


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_public_surface_parity_suite_stays_aligned_with_published_fixtures(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=_case_contract_token,
    )


def test_public_surface_parity_suite_tracks_published_case_frontier() -> None:
    for bundle in FIXTURE_BUNDLES:
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=SELECTED_CASE_IDS_BY_MANIFEST[bundle.expected_manifest_id],
        )


def test_public_surface_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        DIRECT_TEST_CASE_ID_BUCKETS,
        selected_case_ids=PUBLIC_SURFACE_SELECTED_CASE_IDS,
        coverage_label="public surface direct-test case-id buckets",
    )


@pytest.mark.parametrize("case", PUBLIC_HELPER_CASES, ids=lambda case: case.case_id)
def test_public_helper_presence_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper, None)
    expected = getattr(re, case.helper, None)

    assert observed is not None
    assert expected is not None
    assert callable(observed) == callable(expected)
    assert case.helper in backend.__all__
    assert case.helper in re.__all__


@pytest.mark.parametrize("case", PUBLIC_MODULE_CALL_CASES, ids=lambda case: case.case_id)
def test_public_module_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    if case.helper == "compile":
        pattern = case.args[0]
        assert isinstance(pattern, (str, bytes))
        compile_with_cpython_parity(backend_name, backend, pattern)
        return

    if case.helper == "purge":
        assert getattr(backend, case.helper)(*case.args, **case.kwargs) is None
        assert re.purge() is None
        return

    if case.helper == "escape":
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)

        assert type(observed) is type(expected)
        assert observed == expected
        return

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", EXPORTED_METADATA_CASES, ids=lambda case: case.case_id)
def test_exported_symbol_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper, None)
    expected = getattr(re, case.helper, None)

    assert normalize_exported_symbol_metadata(observed) == (
        normalize_exported_symbol_metadata(expected)
    )
    if case.helper == "error":
        assert observed is expected is re.error


@pytest.mark.parametrize("case", EXPORTED_VALUE_CASES, ids=lambda case: case.case_id)
def test_exported_symbol_values_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper, None)
    expected = getattr(re, case.helper, None)

    assert normalize_exported_symbol_value(observed) == normalize_exported_symbol_value(
        expected
    )
    assert int(observed) == int(expected)
    assert type(observed).__name__ == type(expected).__name__


@pytest.mark.parametrize(
    "case",
    EXPORTED_CONSTRUCTOR_GUARD_CASES,
    ids=lambda case: case.case_id,
)
def test_exported_type_constructor_guards_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed_error = _capture_error(
        lambda: getattr(backend, case.helper)(*case.args, **case.kwargs)
    )
    expected_error = _capture_error(
        lambda: getattr(re, case.helper)(*case.args, **case.kwargs)
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize("case", PATTERN_METADATA_CASES, ids=lambda case: case.case_id)
def test_pattern_object_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )

    assert normalize_pattern_object_metadata(observed_pattern) == (
        normalize_pattern_object_metadata(expected_pattern)
    )


@pytest.mark.parametrize("case", PATTERN_CALL_CASES, ids=lambda case: case.case_id)
def test_pattern_object_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
