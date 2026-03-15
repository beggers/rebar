from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import (
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_fixture_bundle_contract,
    compile_with_cpython_parity,
    load_fixture_bundle,
    published_fixture_paths_from_bundles,
    str_case_pattern,
)
PUBLISHED_CONDITIONAL_REPLACEMENT_FIXTURE_PATHS = select_correctness_fixture_paths(
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
NO_MATCH_TEXT_CANDIDATES = (
    "zzz",
    "",
    "----",
    "no-match",
    "999",
    "ffff",
    "ac",
    "ae",
    "ad",
)


FIXTURE_BUNDLES = (
    load_fixture_bundle(
        "conditional_group_exists_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-replacement-present-str",
                "module-subn-conditional-group-exists-replacement-absent-str",
                "pattern-sub-conditional-group-exists-replacement-present-str",
                "pattern-subn-conditional-group-exists-replacement-absent-str",
                "module-sub-named-conditional-group-exists-replacement-present-str",
                "module-subn-named-conditional-group-exists-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e)",
                r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    load_fixture_bundle(
        "conditional_group_exists_no_else_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-no-else-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-no-else-replacement-present-str",
                "module-subn-conditional-group-exists-no-else-replacement-absent-str",
                "pattern-sub-conditional-group-exists-no-else-replacement-present-str",
                "pattern-subn-conditional-group-exists-no-else-replacement-absent-str",
                "module-sub-named-conditional-group-exists-no-else-replacement-present-str",
                "module-subn-named-conditional-group-exists-no-else-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-no-else-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-no-else-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d)",
                r"a(?P<word>b)?c(?(word)d)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    load_fixture_bundle(
        "conditional_group_exists_empty_else_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-else-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-empty-else-replacement-present-str",
                "module-subn-conditional-group-exists-empty-else-replacement-absent-str",
                "pattern-sub-conditional-group-exists-empty-else-replacement-present-str",
                "pattern-subn-conditional-group-exists-empty-else-replacement-absent-str",
                "module-sub-named-conditional-group-exists-empty-else-replacement-present-str",
                "module-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-empty-else-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|)",
                r"a(?P<word>b)?c(?(word)d|)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    load_fixture_bundle(
        "conditional_group_exists_empty_yes_else_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-yes-else-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
                "module-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
                "pattern-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
                "pattern-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
                "module-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
                "module-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|e)",
                r"a(?P<word>b)?c(?(word)|e)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    load_fixture_bundle(
        "conditional_group_exists_fully_empty_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-fully-empty-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-fully-empty-replacement-present-str",
                "module-subn-conditional-group-exists-fully-empty-replacement-absent-str",
                "pattern-sub-conditional-group-exists-fully-empty-replacement-present-str",
                "pattern-subn-conditional-group-exists-fully-empty-replacement-absent-str",
                "module-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
                "module-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|)",
                r"a(?P<word>b)?c(?(word)|)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    load_fixture_bundle(
        "conditional_group_exists_alternation_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-alternation-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-alternation-replacement-present-first-arm-str",
                "module-subn-conditional-group-exists-alternation-replacement-present-second-arm-str",
                "pattern-sub-conditional-group-exists-alternation-replacement-absent-first-arm-str",
                "pattern-subn-conditional-group-exists-alternation-replacement-absent-second-arm-str",
                "module-sub-named-conditional-group-exists-alternation-replacement-present-first-arm-str",
                "module-subn-named-conditional-group-exists-alternation-replacement-present-second-arm-str",
                "pattern-sub-named-conditional-group-exists-alternation-replacement-absent-first-arm-str",
                "pattern-subn-named-conditional-group-exists-alternation-replacement-absent-second-arm-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(de|df)|(eg|eh))",
                r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    load_fixture_bundle(
        "conditional_group_exists_nested_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-nested-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-nested-replacement-present-str",
                "module-subn-conditional-group-exists-nested-replacement-absent-str",
                "pattern-sub-conditional-group-exists-nested-replacement-present-str",
                "pattern-subn-conditional-group-exists-nested-replacement-absent-str",
                "module-sub-named-conditional-group-exists-nested-replacement-present-str",
                "module-subn-named-conditional-group-exists-nested-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-nested-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-nested-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(?(1)d|e)|f)",
                r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    load_fixture_bundle(
        "conditional_group_exists_quantified_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-quantified-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-quantified-replacement-present-str",
                "module-subn-conditional-group-exists-quantified-replacement-absent-str",
                "pattern-sub-conditional-group-exists-quantified-replacement-present-str",
                "pattern-subn-conditional-group-exists-quantified-replacement-absent-str",
                "module-sub-named-conditional-group-exists-quantified-replacement-present-str",
                "module-subn-named-conditional-group-exists-quantified-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-quantified-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-quantified-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e){2}",
                r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
    ),
)

REPLACEMENT_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)


def _case_string(case: FixtureCase) -> str:
    text_index = 2 if case.operation == "module_call" else 1
    string = case.args[text_index]
    assert isinstance(string, str)
    return string


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


def _no_match_text(case: FixtureCase) -> str:
    compiled = re.compile(str_case_pattern(case), case.flags or 0)
    for text in NO_MATCH_TEXT_CANDIDATES:
        if compiled.search(text) is None:
            return text

    raise AssertionError(f"could not find a shared no-match text for {case.case_id!r}")


def _search_match_for_case(
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str]]:
    pattern = str_case_pattern(case)
    string = _case_string(case)

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

    assert observed is not None
    assert expected is not None
    return observed, expected


def _run_replacement_case(
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
        compiled = backend.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(
            *_replacement_args(case, text=text),
            **case.kwargs,
        )

    raise ValueError(f"unsupported replacement parity operation {case.operation!r}")


def test_replacement_parity_suite_discovers_all_published_correctness_fixtures() -> None:
    assert PUBLISHED_CONDITIONAL_REPLACEMENT_FIXTURE_PATHS
    assert PUBLISHED_CONDITIONAL_REPLACEMENT_FIXTURE_PATHS == published_fixture_paths_from_bundles(
        FIXTURE_BUNDLES
    )


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(bundle) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


@pytest.mark.parametrize("case", REPLACEMENT_CASES, ids=lambda case: case.case_id)
def test_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    observed = _run_replacement_case(backend, case)
    expected = _run_replacement_case(re, case)
    assert observed == expected


@pytest.mark.parametrize("case", REPLACEMENT_CASES, ids=lambda case: case.case_id)
def test_replacement_match_capture_and_expand_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed_match, expected_match = _search_match_for_case(
        backend_name,
        backend,
        case,
    )

    assert_match_parity(
        backend_name,
        observed_match,
        expected_match,
        check_regs=True,
    )
    assert_match_convenience_api_parity(observed_match, expected_match)


@pytest.mark.parametrize("case", REPLACEMENT_CASES, ids=lambda case: case.case_id)
def test_replacement_no_match_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    text = _no_match_text(case)
    observed = _run_replacement_case(backend, case, text=text)
    expected = _run_replacement_case(re, case, text=text)
    expected_result: str | tuple[str, int]
    if case.helper == "sub":
        expected_result = text
    else:
        expected_result = (text, 0)

    assert observed == expected == expected_result
