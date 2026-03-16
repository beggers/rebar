from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_match_convenience_api_parity,
    assert_match_parity,
    case_replacement_argument,
    case_text_argument,
    compile_with_cpython_parity,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    str_case_pattern,
)


EXPECTED_GROUPED_TEMPLATE_CASE_ID = "module-sub-grouping-template"
EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS = (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
)
EXPECTED_GROUPED_TEMPLATE_OPERATION_HELPER_COUNTS = Counter({("module_call", "sub"): 1})
EXPECTED_SINGLE_CAPTURE_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "search"): 1,
        ("module_call", "fullmatch"): 1,
        ("pattern_call", "search"): 1,
        ("pattern_call", "match"): 1,
    }
)
EXPECTED_GROUPED_ALTERNATION_COMPILE_PATTERNS = {
    "a(b|c)d",
    "a(?P<word>b|c)d",
}
EXPECTED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS = {
    r"a((b))d",
    r"a(?P<outer>(?P<inner>b))d",
}
EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_COMPILE_PATTERNS = {
    r"a((b|c))d",
    r"a(?P<outer>(b|c))d",
}
EXPECTED_QUANTIFIED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS = {
    r"a((bc)+)d",
    r"a(?P<outer>(?P<inner>bc)+)d",
}
EXPECTED_SHARED_REPLACEMENT_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 1,
        ("pattern_call", "subn"): 1,
    }
)
EXPECTED_SHARED_REPLACEMENT_GROUP_KIND_COUNTS = Counter(
    {
        ("module_call", "sub", "numbered"): 1,
        ("module_call", "sub", "named"): 1,
        ("module_call", "subn", "numbered"): 1,
        ("module_call", "subn", "named"): 1,
        ("pattern_call", "sub", "numbered"): 1,
        ("pattern_call", "sub", "named"): 1,
        ("pattern_call", "subn", "numbered"): 1,
        ("pattern_call", "subn", "named"): 1,
    }
)
EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_GROUP_KIND_COUNTS = Counter(
    {
        ("module_call", "sub", "numbered"): 1,
        ("pattern_call", "subn", "named"): 1,
    }
)
SELECTED_CASE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "collection_replacement_workflows.py",
        expected_manifest_id="collection-replacement-workflows",
        selected_case_ids=(EXPECTED_GROUPED_TEMPLATE_CASE_ID,),
        expected_patterns=frozenset({"(abc)"}),
        expected_operation_helper_counts=EXPECTED_GROUPED_TEMPLATE_OPERATION_HELPER_COUNTS,
        expected_text_models=frozenset({"str"}),
    ),
    FixtureBundleSpec(
        "grouped_match_workflows.py",
        expected_manifest_id="grouped-match-workflows",
        selected_case_ids=EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS,
        expected_patterns=frozenset({"(abc)"}),
        expected_operation_helper_counts=EXPECTED_SINGLE_CAPTURE_OPERATION_HELPER_COUNTS,
        expected_text_models=frozenset({"str"}),
    ),
)
GROUPED_TEMPLATE_BUNDLE, GROUPED_SINGLE_CAPTURE_BUNDLE = load_fixture_bundles(
    SELECTED_CASE_BUNDLE_SPECS
)
GROUPED_TEMPLATE_CASE = GROUPED_TEMPLATE_BUNDLE.cases[0]
GROUPED_SINGLE_CAPTURE_CASES = GROUPED_SINGLE_CAPTURE_BUNDLE.cases
FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "grouped_alternation_replacement_workflows.py",
        expected_manifest_id="grouped-alternation-replacement-workflows",
        expected_patterns=frozenset(EXPECTED_GROUPED_ALTERNATION_COMPILE_PATTERNS),
        expected_operation_helper_counts=EXPECTED_SHARED_REPLACEMENT_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "nested_group_replacement_workflows.py",
        expected_manifest_id="nested-group-replacement-workflows",
        expected_patterns=frozenset(
            EXPECTED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS
        ),
        expected_operation_helper_counts=EXPECTED_SHARED_REPLACEMENT_OPERATION_HELPER_COUNTS,
    ),
    FixtureBundleSpec(
        "nested_group_alternation_replacement_workflows.py",
        expected_manifest_id="nested-group-alternation-replacement-workflows",
        expected_patterns=frozenset(
            EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_COMPILE_PATTERNS
        ),
        expected_operation_helper_counts=(
            EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_OPERATION_HELPER_COUNTS
        ),
    ),
    FixtureBundleSpec(
        "nested_group_alternation_wrapper_replacement_workflows.py",
        expected_manifest_id="nested-group-alternation-wrapper-replacement-workflows",
        expected_patterns=frozenset(
            EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_COMPILE_PATTERNS
        ),
        expected_operation_helper_counts=(
            EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_OPERATION_HELPER_COUNTS
        ),
    ),
    FixtureBundleSpec(
        "quantified_nested_group_replacement_workflows.py",
        expected_manifest_id="quantified-nested-group-replacement-workflows",
        expected_patterns=frozenset(
            EXPECTED_QUANTIFIED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS
        ),
        expected_operation_helper_counts=EXPECTED_SHARED_REPLACEMENT_OPERATION_HELPER_COUNTS,
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
FIXTURE_BACKED_GROUPED_REPLACEMENT_CASES = fixture_cases_from_bundles(FIXTURE_BUNDLES)
MATCH_EXPAND_CASES = (
    GROUPED_TEMPLATE_CASE,
    *tuple(
        case
        for case in FIXTURE_BACKED_GROUPED_REPLACEMENT_CASES
        if case.manifest_id != "quantified-nested-group-replacement-workflows"
    ),
)
COMPILE_PATTERNS = (
    str_case_pattern(GROUPED_TEMPLATE_CASE),
    *tuple(
        sorted(
            {
                str_case_pattern(case)
                for case in FIXTURE_BACKED_GROUPED_REPLACEMENT_CASES
            }
        )
    ),
)
REPLACEMENT_VARIANTS = (
    pytest.param(False, "sub", 1, 0, id="module-sub-single-match"),
    pytest.param(False, "sub", 2, 0, id="module-sub-repeated"),
    pytest.param(False, "subn", 2, 1, id="module-subn-first-match-only"),
    pytest.param(True, "sub", 1, 0, id="pattern-sub-single-match"),
    pytest.param(True, "sub", 2, 0, id="pattern-sub-repeated"),
    pytest.param(True, "subn", 2, 1, id="pattern-subn-first-match-only"),
)
NESTED_GROUP_NO_MATCH_CASES = (
    pytest.param(
        False,
        "sub",
        r"a((b))d",
        r"\1x",
        "zzadzz",
        0,
        id="module-numbered-sub-no-match",
    ),
    pytest.param(
        False,
        "subn",
        r"a((b))d",
        r"\2x",
        "zzadzz",
        1,
        id="module-numbered-subn-no-match",
    ),
    pytest.param(
        True,
        "sub",
        r"a((b))d",
        r"\1x",
        "zzadzz",
        0,
        id="pattern-numbered-sub-no-match",
    ),
    pytest.param(
        True,
        "subn",
        r"a((b))d",
        r"\2x",
        "zzadzz",
        1,
        id="pattern-numbered-subn-no-match",
    ),
    pytest.param(
        False,
        "sub",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<outer>x",
        "zzadzz",
        0,
        id="module-named-sub-no-match",
    ),
    pytest.param(
        False,
        "subn",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<inner>x",
        "zzadzz",
        1,
        id="module-named-subn-no-match",
    ),
    pytest.param(
        True,
        "sub",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<outer>x",
        "zzadzz",
        0,
        id="pattern-named-sub-no-match",
    ),
    pytest.param(
        True,
        "subn",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<inner>x",
        "zzadzz",
        1,
        id="pattern-named-subn-no-match",
    ),
)

def _compiled_pattern(case: FixtureCase) -> re.Pattern[str]:
    return re.compile(str_case_pattern(case), case.flags or 0)


def _group_kind(case: FixtureCase) -> str:
    return "named" if _compiled_pattern(case).groupindex else "numbered"


def _expected_replacement(case: FixtureCase) -> str:
    compiled = _compiled_pattern(case)
    target_group_index = (
        1
        if case.helper == "sub" or "outer-capture" in case.categories
        else compiled.groups
    )
    if compiled.groupindex:
        group_names_by_index = {
            index: group_name for group_name, index in compiled.groupindex.items()
        }
        replacement = rf"\g<{group_names_by_index[target_group_index]}>"
    else:
        replacement = rf"\{target_group_index}"
    if "wrapper-template" in case.categories:
        return f"<{replacement}>"
    return f"{replacement}x"


def _assert_replacement_fixture_bundle_contract(bundle: FixtureBundle) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)
    expected_group_kind_counts = (
        EXPECTED_NESTED_GROUP_ALTERNATION_REPLACEMENT_GROUP_KIND_COUNTS
        if bundle.expected_manifest_id
        in {
            "nested-group-alternation-replacement-workflows",
            "nested-group-alternation-wrapper-replacement-workflows",
        }
        else EXPECTED_SHARED_REPLACEMENT_GROUP_KIND_COUNTS
    )
    assert Counter(
        (case.operation, case.helper, _group_kind(case)) for case in bundle.cases
    ) == expected_group_kind_counts

    for case in bundle.cases:
        compiled = _compiled_pattern(case)
        count_index = 3 if case.operation == "module_call" else 2

        assert case.kwargs == {}
        assert "replacement-template" in case.categories
        assert "str" in case.categories
        assert case.helper in {"sub", "subn"}
        assert case.helper in case.categories
        if case.operation == "module_call":
            assert "module" in case.categories
        else:
            assert "pattern" in case.categories

        if compiled.groupindex:
            assert "named-group" in case.categories

        assert case_replacement_argument(case) == _expected_replacement(case)
        if case.helper == "sub":
            assert len(case.args) == count_index
        else:
            assert len(case.args) == count_index + 1
            assert case.args[count_index] == 1


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
        raise ValueError(f"unsupported grouped template operation {case.operation!r}")

    assert observed is not None
    assert expected is not None
    return observed, expected


def test_grouped_literal_template_suite_stays_aligned_with_published_fixtures() -> None:
    assert_fixture_bundle_contract(
        GROUPED_TEMPLATE_BUNDLE,
        pattern_extractor=str_case_pattern,
    )
    assert_fixture_bundle_contract(
        GROUPED_SINGLE_CAPTURE_BUNDLE,
        pattern_extractor=str_case_pattern,
    )
    assert GROUPED_TEMPLATE_BUNDLE.manifest.manifest_id == "collection-replacement-workflows"
    assert GROUPED_SINGLE_CAPTURE_BUNDLE.manifest.manifest_id == "grouped-match-workflows"
    assert GROUPED_TEMPLATE_CASE.case_id == EXPECTED_GROUPED_TEMPLATE_CASE_ID
    assert GROUPED_TEMPLATE_CASE.operation == "module_call"
    assert GROUPED_TEMPLATE_CASE.helper == "sub"
    assert str_case_pattern(GROUPED_TEMPLATE_CASE) == "(abc)"
    assert case_replacement_argument(GROUPED_TEMPLATE_CASE) == r"\1x"
    assert case_text_argument(GROUPED_TEMPLATE_CASE) == "abc"
    assert "replacement-template" in GROUPED_TEMPLATE_CASE.categories
    assert "grouping-dependent" in GROUPED_TEMPLATE_CASE.categories

    assert tuple(case.case_id for case in GROUPED_SINGLE_CAPTURE_CASES) == (
        EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS
    )
    for case in GROUPED_SINGLE_CAPTURE_CASES:
        assert str_case_pattern(case) == "(abc)"
        assert "grouped" in case.categories
        assert "capture" in case.categories
        assert "gap" not in case.categories


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_grouped_template_fixture_bundles_stay_aligned_with_published_fixtures(
    bundle: FixtureBundle,
) -> None:
    _assert_replacement_fixture_bundle_contract(bundle)


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_grouped_replacement_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, pattern)


@pytest.mark.parametrize(
    ("use_compiled_pattern", "helper", "string_repetitions", "count"),
    REPLACEMENT_VARIANTS,
)
def test_grouped_literal_template_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
    helper: str,
    string_repetitions: int,
    count: int,
) -> None:
    backend_name, backend = regex_backend
    pattern = str_case_pattern(GROUPED_TEMPLATE_CASE)
    replacement = case_replacement_argument(GROUPED_TEMPLATE_CASE)
    string = case_text_argument(GROUPED_TEMPLATE_CASE) * string_repetitions

    assert isinstance(replacement, str)
    assert isinstance(string, str)

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed = getattr(observed_pattern, helper)(replacement, string, count=count)
        expected = getattr(expected_pattern, helper)(replacement, string, count=count)
    else:
        observed = getattr(backend, helper)(pattern, replacement, string, count=count)
        expected = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected


@pytest.mark.parametrize(
    "case",
    FIXTURE_BACKED_GROUPED_REPLACEMENT_CASES,
    ids=lambda case: case.case_id,
)
def test_fixture_backed_grouped_template_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
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

    assert observed == expected


@pytest.mark.parametrize(
    "case",
    MATCH_EXPAND_CASES,
    ids=lambda case: case.case_id,
)
def test_grouped_template_match_expand_matches_cpython(
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

    assert_match_parity(
        backend_name,
        observed_match,
        expected_match,
        check_regs=True,
    )
    assert_match_convenience_api_parity(observed_match, expected_match)

    observed = observed_match.expand(template)
    expected = expected_match.expand(template)

    assert type(observed) is type(expected)
    assert observed == expected


@pytest.mark.parametrize(
    ("use_compiled_pattern", "helper", "pattern", "replacement", "string", "count"),
    NESTED_GROUP_NO_MATCH_CASES,
)
def test_nested_group_no_match_template_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
    helper: str,
    pattern: str,
    replacement: str,
    string: str,
    count: int,
) -> None:
    backend_name, backend = regex_backend

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed = getattr(observed_pattern, helper)(replacement, string, count=count)
        expected = getattr(expected_pattern, helper)(replacement, string, count=count)
    else:
        observed = getattr(backend, helper)(pattern, replacement, string, count=count)
        expected = getattr(re, helper)(pattern, replacement, string, count=count)

    expected_result: str | tuple[str, int]
    if helper == "sub":
        expected_result = string
    else:
        expected_result = (string, 0)

    assert observed == expected == expected_result


@pytest.mark.parametrize(
    "case",
    GROUPED_SINGLE_CAPTURE_CASES,
    ids=lambda case: case.case_id,
)
def test_grouped_single_capture_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
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
    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
