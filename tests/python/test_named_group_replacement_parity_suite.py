from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    case_replacement_argument,
    case_text_argument,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_fixture_bundles,
    str_case_pattern,
)


NAMED_GROUP_REPLACEMENT_CASE_IDS = (
    "module-sub-template-named-group-str",
    "module-subn-template-named-group-str",
    "pattern-sub-template-named-group-str",
    "pattern-subn-template-named-group-str",
)
NO_MATCH_TEXT = "xyzxyz"

(NAMED_GROUP_REPLACEMENT_BUNDLE,) = load_fixture_bundles(
    (
        FixtureBundleSpec(
            fixture_name="named_group_replacement_workflows.py",
            expected_manifest_id="named-group-replacement-workflows",
            selected_case_ids=NAMED_GROUP_REPLACEMENT_CASE_IDS,
            expected_case_ids=frozenset(NAMED_GROUP_REPLACEMENT_CASE_IDS),
            expected_patterns=frozenset({r"(?P<word>abc)"}),
            expected_operation_helper_counts=Counter(
                {
                    ("module_call", "sub"): 1,
                    ("module_call", "subn"): 1,
                    ("pattern_call", "sub"): 1,
                    ("pattern_call", "subn"): 1,
                }
            ),
            expected_text_models=frozenset({"str"}),
        ),
    )
)
PUBLISHED_CASES = NAMED_GROUP_REPLACEMENT_BUNDLE.cases
MODULE_CASES = fixture_cases_for_operation((NAMED_GROUP_REPLACEMENT_BUNDLE,), "module_call")
PATTERN_CASES = fixture_cases_for_operation((NAMED_GROUP_REPLACEMENT_BUNDLE,), "pattern_call")
DIRECT_TEST_CASE_ID_BUCKETS = {
    "module-replacement": frozenset(case.case_id for case in MODULE_CASES),
    "pattern-replacement": frozenset(case.case_id for case in PATTERN_CASES),
}


def _replacement_args(
    case: FixtureCase,
    *,
    text: str | None = None,
) -> tuple[object, ...]:
    args = list(case.args)
    if text is None:
        return tuple(args)

    text_index = 2 if case.operation == "module_call" else 1
    args[text_index] = text
    return tuple(args)


def _run_replacement_case(
    backend_name: str,
    backend: object,
    case: FixtureCase,
    *,
    text: str | None = None,
) -> object:
    if case.helper is None:
        raise ValueError(f"case {case.case_id!r} requires a helper name")

    if case.operation == "module_call":
        return getattr(backend, case.helper)(
            *_replacement_args(case, text=text),
            **case.kwargs,
        )

    if case.operation == "pattern_call":
        observed_pattern, _ = compile_with_cpython_parity(
            backend_name,
            backend,
            str_case_pattern(case),
            case.flags or 0,
        )
        return getattr(observed_pattern, case.helper)(
            *_replacement_args(case, text=text),
            **case.kwargs,
        )

    raise ValueError(f"unsupported replacement parity operation {case.operation!r}")


def _run_cpython_replacement_case(
    case: FixtureCase,
    *,
    text: str | None = None,
) -> object:
    if case.helper is None:
        raise ValueError(f"case {case.case_id!r} requires a helper name")

    if case.operation == "module_call":
        return getattr(re, case.helper)(
            *_replacement_args(case, text=text),
            **case.kwargs,
        )

    if case.operation == "pattern_call":
        expected_pattern = re.compile(str_case_pattern(case), case.flags or 0)
        return getattr(expected_pattern, case.helper)(
            *_replacement_args(case, text=text),
            **case.kwargs,
        )

    raise ValueError(f"unsupported replacement parity operation {case.operation!r}")


def _search_match_for_case(
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str]]:
    pattern = str_case_pattern(case)
    string = case_text_argument(case)
    assert isinstance(string, str)

    if case.operation == "module_call":
        observed = backend.search(pattern, string, case.flags or 0)
        expected = re.search(pattern, string, case.flags or 0)
    elif case.operation == "pattern_call":
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
            case.flags or 0,
        )
        observed = observed_pattern.search(string)
        expected = expected_pattern.search(string)
    else:
        raise ValueError(f"unsupported replacement parity operation {case.operation!r}")

    assert expected is not None
    assert observed is not None
    return observed, expected


@pytest.mark.parametrize(
    "bundle",
    (NAMED_GROUP_REPLACEMENT_BUNDLE,),
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_named_group_replacement_suite_tracks_published_case_frontier() -> None:
    assert_fixture_bundle_tracks_published_case_frontier(
        NAMED_GROUP_REPLACEMENT_BUNDLE,
        selected_case_ids=NAMED_GROUP_REPLACEMENT_CASE_IDS,
    )


def test_named_group_replacement_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        DIRECT_TEST_CASE_ID_BUCKETS,
        selected_case_ids=NAMED_GROUP_REPLACEMENT_CASE_IDS,
        coverage_label="named-group replacement direct-test case-id buckets",
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed = _run_replacement_case(backend_name, backend, case)
    expected = _run_cpython_replacement_case(case)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed = _run_replacement_case(backend_name, backend, case)
    expected = _run_cpython_replacement_case(case)

    assert observed == expected


@pytest.mark.parametrize("case", PUBLISHED_CASES, ids=lambda case: case.case_id)
def test_replacement_match_capture_and_expand_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    template = case_replacement_argument(case)
    assert isinstance(template, str)

    observed_match, expected_match = _search_match_for_case(
        backend_name,
        backend,
        case,
    )

    assert_match_parity(backend_name, observed_match, expected_match, check_regs=True)
    assert_match_convenience_api_parity(observed_match, expected_match)
    assert_valid_match_group_access_parity(observed_match, expected_match)
    assert_invalid_match_group_access_parity(observed_match, expected_match)

    observed = observed_match.expand(template)
    expected = expected_match.expand(template)

    assert type(observed) is type(expected)
    assert observed == expected


@pytest.mark.parametrize("case", PUBLISHED_CASES, ids=lambda case: case.case_id)
def test_replacement_no_match_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert re.search(str_case_pattern(case), NO_MATCH_TEXT, case.flags or 0) is None

    observed = _run_replacement_case(
        backend_name,
        backend,
        case,
        text=NO_MATCH_TEXT,
    )
    expected = _run_cpython_replacement_case(case, text=NO_MATCH_TEXT)

    expected_result: str | tuple[str, int]
    if case.helper == "sub":
        expected_result = NO_MATCH_TEXT
    else:
        expected_result = (NO_MATCH_TEXT, 0)

    assert observed == expected == expected_result
