from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_match_convenience_api_parity,
    assert_match_parity,
    compile_with_cpython_parity,
    str_case_pattern,
)


REPLACEMENT_FIXTURE_PATH = FIXTURES_DIR / "collection_replacement_workflows.py"
ALTERNATION_REPLACEMENT_FIXTURE_PATH = (
    FIXTURES_DIR / "grouped_alternation_replacement_workflows.py"
)
NESTED_REPLACEMENT_FIXTURE_PATH = FIXTURES_DIR / "nested_group_replacement_workflows.py"
QUANTIFIED_NESTED_REPLACEMENT_FIXTURE_PATH = (
    FIXTURES_DIR / "quantified_nested_group_replacement_workflows.py"
)
MATCH_FIXTURE_PATH = FIXTURES_DIR / "grouped_match_workflows.py"

REPLACEMENT_FIXTURE_MANIFEST, REPLACEMENT_FIXTURE_CASES = load_fixture_manifest(
    REPLACEMENT_FIXTURE_PATH
)
ALTERNATION_REPLACEMENT_FIXTURE_MANIFEST, ALTERNATION_REPLACEMENT_FIXTURE_CASES = (
    load_fixture_manifest(ALTERNATION_REPLACEMENT_FIXTURE_PATH)
)
NESTED_REPLACEMENT_FIXTURE_MANIFEST, NESTED_REPLACEMENT_FIXTURE_CASES = (
    load_fixture_manifest(NESTED_REPLACEMENT_FIXTURE_PATH)
)
(
    QUANTIFIED_NESTED_REPLACEMENT_FIXTURE_MANIFEST,
    QUANTIFIED_NESTED_REPLACEMENT_FIXTURE_CASES,
) = load_fixture_manifest(QUANTIFIED_NESTED_REPLACEMENT_FIXTURE_PATH)
MATCH_FIXTURE_MANIFEST, MATCH_FIXTURE_CASES = load_fixture_manifest(MATCH_FIXTURE_PATH)

EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS = (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
)
EXPECTED_GROUPED_ALTERNATION_COMPILE_PATTERNS = {
    "a(b|c)d",
    "a(?P<word>b|c)d",
}
EXPECTED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS = {
    r"a((b))d",
    r"a(?P<outer>(?P<inner>b))d",
}
EXPECTED_QUANTIFIED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS = {
    r"a((bc)+)d",
    r"a(?P<outer>(?P<inner>bc)+)d",
}
EXPECTED_FIXTURE_REPLACEMENT_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
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


@dataclass(frozen=True)
class ReplacementFixtureBundle:
    manifest_id: str
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_compile_patterns: frozenset[str]


def _fixture_case_by_id(
    cases: tuple[FixtureCase, ...] | list[FixtureCase],
    case_id: str,
) -> FixtureCase:
    cases = [case for case in cases if case.case_id == case_id]
    assert len(cases) == 1
    return cases[0]


GROUPED_TEMPLATE_CASE = _fixture_case_by_id(
    REPLACEMENT_FIXTURE_CASES,
    "module-sub-grouping-template",
)
GROUPED_SINGLE_CAPTURE_CASES = tuple(
    _fixture_case_by_id(MATCH_FIXTURE_CASES, case_id)
    for case_id in EXPECTED_SINGLE_CAPTURE_MATCH_CASE_IDS
)
GROUPED_ALTERNATION_REPLACEMENT_CASES = tuple(ALTERNATION_REPLACEMENT_FIXTURE_CASES)
NESTED_GROUP_REPLACEMENT_CASES = tuple(NESTED_REPLACEMENT_FIXTURE_CASES)
QUANTIFIED_NESTED_GROUP_REPLACEMENT_CASES = tuple(
    QUANTIFIED_NESTED_REPLACEMENT_FIXTURE_CASES
)
BUNDLED_GROUPED_REPLACEMENT_FIXTURES = (
    ReplacementFixtureBundle(
        manifest_id=ALTERNATION_REPLACEMENT_FIXTURE_MANIFEST.manifest_id,
        cases=GROUPED_ALTERNATION_REPLACEMENT_CASES,
        expected_manifest_id="grouped-alternation-replacement-workflows",
        expected_compile_patterns=frozenset(
            EXPECTED_GROUPED_ALTERNATION_COMPILE_PATTERNS
        ),
    ),
    ReplacementFixtureBundle(
        manifest_id=NESTED_REPLACEMENT_FIXTURE_MANIFEST.manifest_id,
        cases=NESTED_GROUP_REPLACEMENT_CASES,
        expected_manifest_id="nested-group-replacement-workflows",
        expected_compile_patterns=frozenset(
            EXPECTED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS
        ),
    ),
    ReplacementFixtureBundle(
        manifest_id=QUANTIFIED_NESTED_REPLACEMENT_FIXTURE_MANIFEST.manifest_id,
        cases=QUANTIFIED_NESTED_GROUP_REPLACEMENT_CASES,
        expected_manifest_id="quantified-nested-group-replacement-workflows",
        expected_compile_patterns=frozenset(
            EXPECTED_QUANTIFIED_NESTED_GROUP_REPLACEMENT_COMPILE_PATTERNS
        ),
    ),
)
FIXTURE_BACKED_GROUPED_REPLACEMENT_CASES = (
    GROUPED_ALTERNATION_REPLACEMENT_CASES
    + NESTED_GROUP_REPLACEMENT_CASES
    + QUANTIFIED_NESTED_GROUP_REPLACEMENT_CASES
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


def _replacement(case: FixtureCase) -> str:
    replacement_index = 1 if case.operation == "module_call" else 0
    replacement = case.args[replacement_index]
    assert isinstance(replacement, str)
    return replacement


def _single_match_string(case: FixtureCase) -> str:
    string_index = 2 if case.operation == "module_call" else 1
    string = case.args[string_index]
    assert isinstance(string, str)
    return string


def _compiled_pattern(case: FixtureCase) -> re.Pattern[str]:
    return re.compile(str_case_pattern(case), case.flags or 0)


def _group_kind(case: FixtureCase) -> str:
    return "named" if _compiled_pattern(case).groupindex else "numbered"


def _expected_replacement(case: FixtureCase) -> str:
    compiled = _compiled_pattern(case)
    target_group_index = 1 if case.helper == "sub" else compiled.groups
    if compiled.groupindex:
        group_names_by_index = {
            index: group_name for group_name, index in compiled.groupindex.items()
        }
        return rf"\g<{group_names_by_index[target_group_index]}>x"
    return rf"\{target_group_index}x"


def _assert_replacement_fixture_bundle_contract(bundle: ReplacementFixtureBundle) -> None:
    assert bundle.manifest_id == bundle.expected_manifest_id
    assert len(bundle.cases) == 8
    assert len({case.case_id for case in bundle.cases}) == len(bundle.cases)
    assert {str_case_pattern(case) for case in bundle.cases} == (
        bundle.expected_compile_patterns
    )
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        EXPECTED_FIXTURE_REPLACEMENT_OPERATION_HELPER_COUNTS
    )
    assert Counter(
        (case.operation, case.helper, _group_kind(case)) for case in bundle.cases
    ) == Counter(
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

        assert _replacement(case) == _expected_replacement(case)
        if case.helper == "sub":
            assert len(case.args) == count_index
        else:
            assert len(case.args) == count_index + 1
            assert case.args[count_index] == 1


def test_grouped_literal_template_suite_stays_aligned_with_published_fixtures() -> None:
    assert REPLACEMENT_FIXTURE_MANIFEST.manifest_id == "collection-replacement-workflows"
    assert MATCH_FIXTURE_MANIFEST.manifest_id == "grouped-match-workflows"
    assert GROUPED_TEMPLATE_CASE.operation == "module_call"
    assert GROUPED_TEMPLATE_CASE.helper == "sub"
    assert str_case_pattern(GROUPED_TEMPLATE_CASE) == "(abc)"
    assert _replacement(GROUPED_TEMPLATE_CASE) == r"\1x"
    assert _single_match_string(GROUPED_TEMPLATE_CASE) == "abc"
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
    BUNDLED_GROUPED_REPLACEMENT_FIXTURES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_grouped_template_fixture_bundles_stay_aligned_with_published_fixtures(
    bundle: ReplacementFixtureBundle,
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
    replacement = _replacement(GROUPED_TEMPLATE_CASE)
    string = _single_match_string(GROUPED_TEMPLATE_CASE) * string_repetitions

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
