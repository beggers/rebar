from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundleSpec,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    load_fixture_bundles,
    ordered_manifest_cases_from_bundles,
    published_fixture_bundle_by_manifest_id,
    str_case_pattern,
)
GROUPED_MATCH_TRACKED_CASE_IDS = (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
    "grouped-module-fullmatch-two-capture-gap-str",
    "grouped-pattern-fullmatch-two-capture-gap-str",
)
GROUPED_MATCH_BUNDLE_CASE_IDS = GROUPED_MATCH_TRACKED_CASE_IDS
GROUPED_MATCH_UNCOVERED_CASE_IDS = ()
NAMED_GROUP_CASE_IDS = (
    "named-group-compile-metadata-str",
    "named-group-module-search-metadata-str",
    "named-group-pattern-search-metadata-str",
)
GROUPED_SEGMENT_LEADING_CAPTURE_PATTERN = r"(ab)c"
GROUPED_SEGMENT_CASE_IDS = (
    "grouped-segment-compile-metadata-str",
    "grouped-segment-module-search-str",
    "grouped-segment-leading-capture-module-search-str",
    "grouped-segment-pattern-fullmatch-str",
    "grouped-segment-leading-capture-pattern-search-str",
    "named-grouped-segment-compile-metadata-str",
    "named-grouped-segment-module-search-str",
    "named-grouped-segment-pattern-fullmatch-str",
)
GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER = (
    "grouped-segment-leading-capture-module-search-str",
    "grouped-segment-leading-capture-pattern-search-str",
)
GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS = frozenset(
    GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER
)
GROUPED_ALTERNATION_CASE_IDS = (
    "grouped-alternation-compile-metadata-str",
    "grouped-alternation-module-search-str",
    "grouped-alternation-pattern-fullmatch-str",
    "named-grouped-alternation-compile-metadata-str",
    "named-grouped-alternation-module-search-str",
    "named-grouped-alternation-pattern-fullmatch-str",
)
OPTIONAL_GROUP_CASE_IDS = (
    "optional-group-compile-metadata-str",
    "optional-group-module-search-present-str",
    "optional-group-pattern-fullmatch-absent-str",
    "named-optional-group-compile-metadata-str",
    "named-optional-group-module-search-absent-str",
    "named-optional-group-pattern-fullmatch-present-str",
    "systematic-optional-group-numbered-compile-metadata-str",
    "systematic-optional-group-numbered-module-search-present-str",
    "systematic-optional-group-numbered-module-search-absent-str",
    "systematic-optional-group-numbered-pattern-fullmatch-present-str",
    "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
    "systematic-optional-group-named-compile-metadata-str",
    "systematic-optional-group-named-module-search-present-str",
    "systematic-optional-group-named-module-search-absent-str",
    "systematic-optional-group-named-pattern-fullmatch-present-str",
    "systematic-optional-group-named-pattern-fullmatch-absent-str",
)
OPTIONAL_GROUP_ALTERNATION_CASE_IDS = (
    "optional-group-alternation-compile-metadata-str",
    "optional-group-alternation-module-search-present-str",
    "optional-group-alternation-pattern-fullmatch-absent-str",
    "named-optional-group-alternation-compile-metadata-str",
    "named-optional-group-alternation-module-search-present-str",
    "named-optional-group-alternation-pattern-fullmatch-absent-str",
)
NESTED_GROUP_CASE_IDS = (
    "nested-group-compile-metadata-str",
    "nested-group-module-search-str",
    "nested-group-pattern-fullmatch-str",
    "named-nested-group-compile-metadata-str",
    "named-nested-group-module-search-str",
    "named-nested-group-pattern-fullmatch-str",
)
NESTED_GROUP_ALTERNATION_CASE_IDS = (
    "nested-group-alternation-compile-metadata-str",
    "nested-group-alternation-module-search-str",
    "nested-group-alternation-pattern-fullmatch-str",
    "named-nested-group-alternation-compile-metadata-str",
    "named-nested-group-alternation-module-search-str",
    "named-nested-group-alternation-pattern-fullmatch-str",
)
GROUPED_CAPTURE_TRACKED_CASE_IDS = (
    *GROUPED_MATCH_TRACKED_CASE_IDS,
    *NAMED_GROUP_CASE_IDS,
    *GROUPED_SEGMENT_CASE_IDS,
    *GROUPED_ALTERNATION_CASE_IDS,
    *OPTIONAL_GROUP_CASE_IDS,
    *OPTIONAL_GROUP_ALTERNATION_CASE_IDS,
    *NESTED_GROUP_CASE_IDS,
    *NESTED_GROUP_ALTERNATION_CASE_IDS,
)
GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS = {
    "grouped-match": frozenset(GROUPED_MATCH_TRACKED_CASE_IDS),
    "named-group": frozenset(NAMED_GROUP_CASE_IDS),
    "grouped-segment": frozenset(GROUPED_SEGMENT_CASE_IDS),
    "grouped-alternation": frozenset(GROUPED_ALTERNATION_CASE_IDS),
    "optional-group": frozenset(OPTIONAL_GROUP_CASE_IDS),
    "optional-group-alternation": frozenset(OPTIONAL_GROUP_ALTERNATION_CASE_IDS),
    "nested-group": frozenset(NESTED_GROUP_CASE_IDS),
    "nested-group-alternation": frozenset(NESTED_GROUP_ALTERNATION_CASE_IDS),
}


@dataclass(frozen=True)
class CompileCase:
    id: str
    pattern: str
    flags: int = 0


@dataclass(frozen=True)
class SupplementalMissCase:
    id: str
    module_case_id: str
    module_misses: tuple[str, ...]
    pattern_case_id: str
    pattern_misses: tuple[str, ...]


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern_case_id: str
    helper: str
    string: str
    bounds: tuple[int, ...]


SELECTED_CASE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        fixture_name="grouped_match_workflows.py",
        expected_manifest_id="grouped-match-workflows",
        selected_case_ids=GROUPED_MATCH_BUNDLE_CASE_IDS,
        expected_patterns=frozenset({r"(abc)", r"(ab)(c)"}),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "search"): 1,
                ("module_call", "fullmatch"): 2,
                ("pattern_call", "search"): 1,
                ("pattern_call", "match"): 1,
                ("pattern_call", "fullmatch"): 1,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="named_group_workflows.py",
        expected_manifest_id="named-group-workflows",
        selected_case_ids=NAMED_GROUP_CASE_IDS,
        expected_patterns=frozenset({r"(?P<word>abc)"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="grouped_segment_workflows.py",
        expected_manifest_id="grouped-segment-workflows",
        selected_case_ids=GROUPED_SEGMENT_CASE_IDS,
        expected_patterns=frozenset(
            {
                r"a(b)c",
                GROUPED_SEGMENT_LEADING_CAPTURE_PATTERN,
                r"a(?P<word>b)c",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 3,
                ("pattern_call", "fullmatch"): 2,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="grouped_alternation_workflows.py",
        expected_manifest_id="grouped-alternation-workflows",
        selected_case_ids=GROUPED_ALTERNATION_CASE_IDS,
        expected_patterns=frozenset(
            {
                r"a(b|c)d",
                r"a(?P<word>b|c)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="optional_group_workflows.py",
        expected_manifest_id="optional-group-workflows",
        selected_case_ids=OPTIONAL_GROUP_CASE_IDS,
        expected_patterns=frozenset(
            {
                r"a(b)?d",
                r"a(?P<word>b)?d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="optional_group_alternation_workflows.py",
        expected_manifest_id="optional-group-alternation-workflows",
        selected_case_ids=OPTIONAL_GROUP_ALTERNATION_CASE_IDS,
        expected_patterns=frozenset(
            {
                r"a(b|c)?d",
                r"a(?P<word>b|c)?d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="nested_group_workflows.py",
        expected_manifest_id="nested-group-workflows",
        selected_case_ids=NESTED_GROUP_CASE_IDS,
        expected_patterns=frozenset(
            {
                r"a((b))d",
                r"a(?P<outer>(?P<inner>b))d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    FixtureBundleSpec(
        fixture_name="nested_group_alternation_workflows.py",
        expected_manifest_id="nested-group-alternation-workflows",
        selected_case_ids=NESTED_GROUP_ALTERNATION_CASE_IDS,
        expected_patterns=frozenset(
            {
                r"a((b|c))d",
                r"a(?P<outer>(?P<inner>b|c))d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(SELECTED_CASE_BUNDLE_SPECS)
GROUPED_SEGMENT_FIXTURE_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "grouped-segment-workflows",
)


def _compile_cases(cases: tuple[FixtureCase, ...]) -> tuple[CompileCase, ...]:
    grouped_cases: dict[tuple[str, int], list[FixtureCase]] = {}
    for case in cases:
        key = (str_case_pattern(case), case.flags or 0)
        grouped_cases.setdefault(key, []).append(case)

    compile_cases: list[CompileCase] = []
    for (pattern, flags), cases_for_pattern in grouped_cases.items():
        source_case = next((case for case in cases_for_pattern if case.operation == "compile"), None)
        if source_case is None:
            source_case = cases_for_pattern[0]
            case_id = f"{source_case.case_id}-compile-metadata"
        else:
            case_id = source_case.case_id
        compile_cases.append(CompileCase(id=case_id, pattern=pattern, flags=flags))
    return tuple(compile_cases)


PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
DIRECT_PARITY_CASES = PUBLISHED_CASES
COMPILE_CASES = _compile_cases(DIRECT_PARITY_CASES)
MODULE_CASES = tuple(
    case for case in DIRECT_PARITY_CASES if case.operation == "module_call"
)
PATTERN_CASES = tuple(
    case for case in DIRECT_PARITY_CASES if case.operation == "pattern_call"
)
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}
assert len(CASES_BY_ID) == len(PUBLISHED_CASES)
SUPPLEMENTAL_MISS_CASES = (
    SupplementalMissCase(
        id="numbered-two-capture-fullmatch",
        module_case_id="grouped-module-fullmatch-two-capture-gap-str",
        module_misses=("ab", "abcz"),
        pattern_case_id="grouped-pattern-fullmatch-two-capture-gap-str",
        pattern_misses=("ab", "abcz"),
    ),
    SupplementalMissCase(
        id="numbered-grouped-segment-search-and-fullmatch",
        module_case_id="grouped-segment-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="grouped-segment-pattern-fullmatch-str",
        pattern_misses=("abcz",),
    ),
    SupplementalMissCase(
        id="named-grouped-segment-search-and-fullmatch",
        module_case_id="named-grouped-segment-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="named-grouped-segment-pattern-fullmatch-str",
        pattern_misses=("abcz",),
    ),
    SupplementalMissCase(
        id="numbered-grouped-alternation-search-and-fullmatch",
        module_case_id="grouped-alternation-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="grouped-alternation-pattern-fullmatch-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="named-grouped-alternation-search-and-fullmatch",
        module_case_id="named-grouped-alternation-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="named-grouped-alternation-pattern-fullmatch-str",
        pattern_misses=("acdd",),
    ),
    SupplementalMissCase(
        id="named-single-capture-search",
        module_case_id="named-group-module-search-metadata-str",
        module_misses=("zzz",),
        pattern_case_id="named-group-pattern-search-metadata-str",
        pattern_misses=("zzz",),
    ),
    SupplementalMissCase(
        id="numbered-optional-group-search-and-fullmatch",
        module_case_id="optional-group-module-search-present-str",
        module_misses=("zzz",),
        pattern_case_id="optional-group-pattern-fullmatch-absent-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="named-optional-group-search-and-fullmatch",
        module_case_id="named-optional-group-module-search-absent-str",
        module_misses=("zzz",),
        pattern_case_id="named-optional-group-pattern-fullmatch-present-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="numbered-optional-group-alternation-search-and-fullmatch",
        module_case_id="optional-group-alternation-module-search-present-str",
        module_misses=("zzaedzz",),
        pattern_case_id="optional-group-alternation-pattern-fullmatch-absent-str",
        pattern_misses=("ae",),
    ),
    SupplementalMissCase(
        id="named-optional-group-alternation-search-and-fullmatch",
        module_case_id="named-optional-group-alternation-module-search-present-str",
        module_misses=("zzaedzz",),
        pattern_case_id="named-optional-group-alternation-pattern-fullmatch-absent-str",
        pattern_misses=("ae",),
    ),
    SupplementalMissCase(
        id="numbered-nested-group-search-and-fullmatch",
        module_case_id="nested-group-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="nested-group-pattern-fullmatch-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="named-nested-group-search-and-fullmatch",
        module_case_id="named-nested-group-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="named-nested-group-pattern-fullmatch-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="numbered-nested-group-alternation-search-and-fullmatch",
        module_case_id="nested-group-alternation-module-search-str",
        module_misses=("zzadzz", "zzabbdzz"),
        pattern_case_id="nested-group-alternation-pattern-fullmatch-str",
        pattern_misses=("ad", "abbd"),
    ),
    SupplementalMissCase(
        id="named-nested-group-alternation-search-and-fullmatch",
        module_case_id="named-nested-group-alternation-module-search-str",
        module_misses=("zzadzz", "zzaccddzz"),
        pattern_case_id="named-nested-group-alternation-pattern-fullmatch-str",
        pattern_misses=("ad", "accd"),
    ),
)
MATCH_GROUP_ACCESS_CASE_IDS = (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
    "grouped-segment-module-search-str",
    "grouped-segment-leading-capture-module-search-str",
    "grouped-segment-pattern-fullmatch-str",
    "grouped-segment-leading-capture-pattern-search-str",
    "grouped-alternation-module-search-str",
    "grouped-alternation-pattern-fullmatch-str",
    "named-group-module-search-metadata-str",
    "named-group-pattern-search-metadata-str",
    "named-grouped-segment-module-search-str",
    "named-grouped-segment-pattern-fullmatch-str",
    "named-grouped-alternation-module-search-str",
    "named-grouped-alternation-pattern-fullmatch-str",
    "systematic-optional-group-numbered-module-search-absent-str",
    "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
    "systematic-optional-group-named-module-search-absent-str",
    "systematic-optional-group-named-pattern-fullmatch-absent-str",
    "optional-group-alternation-module-search-present-str",
    "optional-group-alternation-pattern-fullmatch-absent-str",
    "named-optional-group-alternation-module-search-present-str",
    "named-optional-group-alternation-pattern-fullmatch-absent-str",
    "nested-group-module-search-str",
    "nested-group-pattern-fullmatch-str",
    "named-nested-group-module-search-str",
    "named-nested-group-pattern-fullmatch-str",
    "nested-group-alternation-module-search-str",
    "nested-group-alternation-pattern-fullmatch-str",
    "named-nested-group-alternation-module-search-str",
    "named-nested-group-alternation-pattern-fullmatch-str",
)
REGS_PARITY_CASE_IDS = frozenset(
    {
        "grouped-module-search-single-capture-str",
        "grouped-module-fullmatch-single-capture-str",
        "grouped-pattern-search-single-capture-str",
        "grouped-pattern-match-single-capture-str",
        "optional-group-alternation-module-search-present-str",
        "optional-group-alternation-pattern-fullmatch-absent-str",
        "named-optional-group-alternation-module-search-present-str",
        "named-optional-group-alternation-pattern-fullmatch-absent-str",
        "nested-group-alternation-module-search-str",
        "nested-group-alternation-pattern-fullmatch-str",
        "named-nested-group-alternation-module-search-str",
        "named-nested-group-alternation-pattern-fullmatch-str",
    }
)
GROUPED_SEGMENT_COMPILE_CASE_ID = "grouped-segment-compile-metadata-str"
NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID = "named-optional-group-compile-metadata-str"
PATTERN_BOUNDS_MATCH_CASES = (
    BoundedPatternCase(
        id="grouped-segment-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id=GROUPED_SEGMENT_COMPILE_CASE_ID,
        helper="search",
        string="zzabczz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="grouped-segment-match-honors-narrowed-offset-window",
        pattern_case_id=GROUPED_SEGMENT_COMPILE_CASE_ID,
        helper="match",
        string="zzabczz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-optional-fullmatch-preserves-absent-group-metadata-in-window",
        pattern_case_id=NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID,
        helper="fullmatch",
        string="zzadzz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="named-optional-fullmatch-preserves-present-group-metadata-in-window",
        pattern_case_id=NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID,
        helper="fullmatch",
        string="zzabdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-optional-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id=NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID,
        helper="search",
        string="zzabdzz",
        bounds=(-100, 999),
    ),
)
PATTERN_BOUNDS_NO_MATCH_CASES = (
    BoundedPatternCase(
        id="named-optional-search-skips-match-before-pos",
        pattern_case_id=NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID,
        helper="search",
        string="zzabdzz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="grouped-segment-match-fails-when-endpos-truncates-the-subject",
        pattern_case_id=GROUPED_SEGMENT_COMPILE_CASE_ID,
        helper="match",
        string="zzabczz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="named-optional-fullmatch-does-not-expand-to-the-whole-string",
        pattern_case_id=NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID,
        helper="fullmatch",
        string="zzabdzz",
        bounds=(-100, 999),
    ),
)

MATCH_GROUP_ACCESS_CASES = ordered_manifest_cases_from_bundles(
    FIXTURE_BUNDLES,
    MATCH_GROUP_ACCESS_CASE_IDS,
    error_label="grouped capture match-group-access rows",
)
GROUPED_SEGMENT_LEADING_CAPTURE_CASES = ordered_manifest_cases_from_bundles(
    FIXTURE_BUNDLES,
    GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER,
    error_label="grouped-segment leading-capture rows",
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


def _bounded_pattern(case: BoundedPatternCase) -> str:
    return str_case_pattern(CASES_BY_ID[case.pattern_case_id])


def _invoke_bound_helper(pattern: object, case: BoundedPatternCase) -> object:
    return getattr(pattern, case.helper)(case.string, *case.bounds)


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


def test_grouped_segment_leading_capture_rows_stay_on_direct_parity_frontier() -> None:
    assert tuple(case.case_id for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases) == (
        GROUPED_SEGMENT_CASE_IDS
    )
    assert GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS <= frozenset(
        case.case_id for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
    )
    assert GROUPED_SEGMENT_LEADING_CAPTURE_PATTERN in {
        case.pattern for case in COMPILE_CASES
    }
    assert "grouped-segment-leading-capture-module-search-str" in {
        case.case_id for case in MODULE_CASES
    }
    assert "grouped-segment-leading-capture-pattern-search-str" in {
        case.case_id for case in PATTERN_CASES
    }
    assert GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS <= set(MATCH_GROUP_ACCESS_CASE_IDS)
    assert GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS.isdisjoint(
        {case.module_case_id for case in SUPPLEMENTAL_MISS_CASES}
    )
    assert GROUPED_SEGMENT_LEADING_CAPTURE_CASE_IDS.isdisjoint(
        {case.pattern_case_id for case in SUPPLEMENTAL_MISS_CASES}
    )
    assert tuple(case.case_id for case in GROUPED_SEGMENT_LEADING_CAPTURE_CASES) == (
        GROUPED_SEGMENT_LEADING_CAPTURE_CASE_ID_ORDER
    )


def test_pattern_bounds_cases_stay_anchored_to_grouped_capture_patterns() -> None:
    assert str_case_pattern(CASES_BY_ID[GROUPED_SEGMENT_COMPILE_CASE_ID]) == r"a(b)c"
    assert str_case_pattern(CASES_BY_ID[NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID]) == r"a(?P<word>b)?d"


def test_match_group_access_rows_remain_on_grouped_capture_fixture_paths() -> None:
    assert tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES) == MATCH_GROUP_ACCESS_CASE_IDS
    assert {case.text_model for case in MATCH_GROUP_ACCESS_CASES} == {"str"}


@pytest.mark.parametrize(
    "case",
    GROUPED_SEGMENT_LEADING_CAPTURE_CASES,
    ids=lambda case: case.case_id,
)
def test_grouped_segment_leading_capture_groups_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert observed.span() == expected.span() == (1, 4)
    assert observed.group(0) == expected.group(0) == "abc"
    assert observed.group(1) == expected.group(1) == "ab"
    assert observed.groups() == expected.groups() == ("ab",)


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(bundle) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)
    assert {case.text_model for case in bundle.cases} == {"str"}


def test_grouped_capture_parity_suite_tracks_published_case_frontier() -> None:
    for bundle in FIXTURE_BUNDLES:
        manifest_id = bundle.expected_manifest_id
        if manifest_id == "grouped-match-workflows":
            selected_case_ids = GROUPED_MATCH_TRACKED_CASE_IDS
            expected_uncovered_case_ids = GROUPED_MATCH_UNCOVERED_CASE_IDS
        else:
            selected_case_ids = tuple(case.case_id for case in bundle.cases)
            expected_uncovered_case_ids = ()
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=selected_case_ids,
            expected_uncovered_case_ids=expected_uncovered_case_ids,
        )


def test_grouped_capture_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS,
        selected_case_ids=GROUPED_CAPTURE_TRACKED_CASE_IDS,
        coverage_label="grouped capture direct-test case-id buckets",
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: CompileCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern, case.flags)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_module_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    _, backend = regex_backend
    module_case = CASES_BY_ID[case.module_case_id]

    for text in case.module_misses:
        assert _module_call_with_text(backend, module_case, text) is None
        assert _module_call_with_text(re, module_case, text) is None


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

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
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


@pytest.mark.parametrize("case", PATTERN_BOUNDS_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_helper_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        _bounded_pattern(case),
    )

    observed = _invoke_bound_helper(observed_pattern, case)
    expected = _invoke_bound_helper(expected_pattern, case)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=lambda case: case.case_id)
def test_match_group_accessors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)
    assert_valid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=lambda case: case.case_id)
def test_invalid_match_group_access_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_helper_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_helper_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

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
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_pattern_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    backend_name, backend = regex_backend
    pattern_case = CASES_BY_ID[case.pattern_case_id]
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern_case.pattern_payload(),
        pattern_case.flags or 0,
    )

    for text in case.pattern_misses:
        assert _pattern_call_with_text(observed_pattern, pattern_case, text) is None
        assert _pattern_call_with_text(expected_pattern, pattern_case, text) is None


@pytest.mark.parametrize("case", PATTERN_BOUNDS_NO_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_helper_bounds_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        _bounded_pattern(case),
    )

    observed = _invoke_bound_helper(observed_pattern, case)
    expected = _invoke_bound_helper(expected_pattern, case)

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)
