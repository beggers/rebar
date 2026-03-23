from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import (
    GROUPED_CAPTURE_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    CaseIdBoundedPatternCase as BoundedPatternCase,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    invoke_bounded_pattern_case,
    load_published_fixture_bundles,
    str_case_pattern,
    workflow_result_with_cpython_parity,
)
from tests.conftest import duplicate_string_ids
GROUPED_SEGMENT_LEADING_CAPTURE_PATTERN = r"(ab)c"


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
class OptionalGroupExpandCase:
    id: str
    case_id: str
    template: str
    expected_expansion: str


FIXTURE_BUNDLES, FIXTURE_BUNDLES_BY_MANIFEST_ID = load_published_fixture_bundles(
    GROUPED_CAPTURE_FIXTURE_SELECTOR,
    pattern_extractor=str_case_pattern,
)
GROUPED_MATCH_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID["grouped-match-workflows"]
NAMED_GROUP_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID["named-group-workflows"]
GROUPED_SEGMENT_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "grouped-segment-workflows"
]
NESTED_GROUP_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID["nested-group-workflows"]
NESTED_GROUP_ALTERNATION_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "nested-group-alternation-workflows"
]
GROUPED_ALTERNATION_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "grouped-alternation-workflows"
]
OPTIONAL_GROUP_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "optional-group-workflows"
]
OPTIONAL_GROUP_ALTERNATION_FIXTURE_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "optional-group-alternation-workflows"
]


def _iter_fixture_cases() -> Iterator[FixtureCase]:
    for bundle in FIXTURE_BUNDLES:
        yield from bundle.cases


def _compile_cases(cases: Iterable[FixtureCase]) -> tuple[CompileCase, ...]:
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


COMPILE_CASES = _compile_cases(_iter_fixture_cases())
MODULE_CASES = tuple(
    case for case in _iter_fixture_cases() if case.operation == "module_call"
)
PATTERN_CASES = tuple(
    case for case in _iter_fixture_cases() if case.operation == "pattern_call"
)
CASES_BY_ID = {case.case_id: case for case in _iter_fixture_cases()}
assert len(CASES_BY_ID) == sum(len(bundle.cases) for bundle in FIXTURE_BUNDLES)


def _grouped_segment_leading_capture_cases() -> tuple[FixtureCase, ...]:
    return tuple(
        case
        for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
        if "leading-capture" in case.case_id
    )


def _match_group_access_cases() -> tuple[FixtureCase, ...]:
    return (
        tuple(GROUPED_MATCH_FIXTURE_BUNDLE.cases[:4])
        + tuple(
            case
            for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("grouped-segment-") and case.operation != "compile"
        )
        + tuple(
            case
            for case in GROUPED_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("grouped-alternation-")
            and case.operation != "compile"
        )
        + tuple(
            case
            for case in NAMED_GROUP_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
        + tuple(
            case
            for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("named-grouped-segment-")
            and case.operation != "compile"
        )
        + tuple(
            case
            for case in GROUPED_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("named-grouped-alternation-")
            and case.operation != "compile"
        )
        + tuple(
            case
            for case in OPTIONAL_GROUP_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("systematic-optional-group-")
            and "-absent-" in case.case_id
        )
        + tuple(
            case
            for case in OPTIONAL_GROUP_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
        + tuple(
            case
            for case in NESTED_GROUP_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
        + tuple(
            case
            for case in NESTED_GROUP_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
    )


OPTIONAL_GROUP_ABSENT_EXPAND_CASES = (
    OptionalGroupExpandCase(
        id="numbered-module-search-absent",
        case_id="systematic-optional-group-numbered-module-search-absent-str",
        template=r"<\g<0>|\1>",
        expected_expansion="<ad|>",
    ),
    OptionalGroupExpandCase(
        id="numbered-pattern-fullmatch-absent",
        case_id="systematic-optional-group-numbered-pattern-fullmatch-absent-str",
        template=r"<\g<0>|\1>",
        expected_expansion="<ad|>",
    ),
    OptionalGroupExpandCase(
        id="named-module-search-absent",
        case_id="systematic-optional-group-named-module-search-absent-str",
        template=r"<\g<0>|\g<word>>",
        expected_expansion="<ad|>",
    ),
    OptionalGroupExpandCase(
        id="named-pattern-fullmatch-absent",
        case_id="systematic-optional-group-named-pattern-fullmatch-absent-str",
        template=r"<\g<0>|\g<word>>",
        expected_expansion="<ad|>",
    ),
)
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

GROUPED_SEGMENT_LEADING_CAPTURE_CASES = _grouped_segment_leading_capture_cases()
MATCH_GROUP_ACCESS_CASES = _match_group_access_cases()
assert not duplicate_string_ids(
    tuple(case.case_id for case in GROUPED_SEGMENT_LEADING_CAPTURE_CASES)
)
assert not duplicate_string_ids(tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES))


def _fixture_case_id(case: FixtureCase) -> str:
    return case.case_id


def _bundle_expected_manifest_id(bundle) -> str:
    return bundle.expected_manifest_id


def _case_id(case: CompileCase | SupplementalMissCase | OptionalGroupExpandCase | BoundedPatternCase) -> str:
    return case.id


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


def _grouped_match_frontier_contract_case_ids() -> tuple[tuple[str, ...], tuple[str, ...]]:
    grouped_match_case_ids = tuple(
        case.case_id for case in GROUPED_MATCH_FIXTURE_BUNDLE.cases
    )
    selected_case_ids = grouped_match_case_ids[-2:]
    uncovered_case_ids = grouped_match_case_ids[:-2]

    assert GROUPED_MATCH_FIXTURE_BUNDLE.published_case_ids == (
        *uncovered_case_ids,
        *selected_case_ids,
    )
    return selected_case_ids, uncovered_case_ids


def test_grouped_segment_leading_capture_rows_stay_on_direct_parity_frontier() -> None:
    grouped_segment_leading_capture_case_ids = tuple(
        case.case_id for case in GROUPED_SEGMENT_LEADING_CAPTURE_CASES
    )
    grouped_segment_leading_capture_case_id_set = set(
        grouped_segment_leading_capture_case_ids
    )
    grouped_segment_case_ids = frozenset(
        case.case_id for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
    )
    direct_test_case_id_buckets = {
        bundle.manifest.manifest_id.removesuffix("-workflows"): frozenset(
            case.case_id for case in bundle.cases
        )
        for bundle in FIXTURE_BUNDLES
    }
    assert direct_test_case_id_buckets["grouped-segment"] == (
        grouped_segment_case_ids
    )
    assert grouped_segment_leading_capture_case_id_set <= grouped_segment_case_ids
    assert GROUPED_SEGMENT_LEADING_CAPTURE_PATTERN in {
        case.pattern for case in COMPILE_CASES
    }
    assert "grouped-segment-leading-capture-module-search-str" in {
        case.case_id for case in MODULE_CASES
    }
    assert "grouped-segment-leading-capture-pattern-search-str" in {
        case.case_id for case in PATTERN_CASES
    }
    assert grouped_segment_leading_capture_case_id_set <= set(
        case.case_id for case in MATCH_GROUP_ACCESS_CASES
    )
    assert grouped_segment_leading_capture_case_id_set.isdisjoint(
        {case.module_case_id for case in SUPPLEMENTAL_MISS_CASES}
    )
    assert grouped_segment_leading_capture_case_id_set.isdisjoint(
        {case.pattern_case_id for case in SUPPLEMENTAL_MISS_CASES}
    )
    assert grouped_segment_leading_capture_case_ids == (
        "grouped-segment-leading-capture-module-search-str",
        "grouped-segment-leading-capture-pattern-search-str",
    )


def test_pattern_bounds_cases_stay_anchored_to_grouped_capture_patterns() -> None:
    assert str_case_pattern(CASES_BY_ID[GROUPED_SEGMENT_COMPILE_CASE_ID]) == r"a(b)c"
    assert str_case_pattern(CASES_BY_ID[NAMED_OPTIONAL_GROUP_COMPILE_CASE_ID]) == r"a(?P<word>b)?d"


def test_match_group_access_rows_remain_on_grouped_capture_fixture_paths() -> None:
    assert tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES) == (
        tuple(case.case_id for case in GROUPED_MATCH_FIXTURE_BUNDLE.cases[:4])
        + tuple(
            case.case_id
            for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("grouped-segment-") and case.operation != "compile"
        )
        + tuple(
            case.case_id
            for case in GROUPED_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("grouped-alternation-")
            and case.operation != "compile"
        )
        + tuple(
            case.case_id
            for case in NAMED_GROUP_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
        + tuple(
            case.case_id
            for case in GROUPED_SEGMENT_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("named-grouped-segment-")
            and case.operation != "compile"
        )
        + tuple(
            case.case_id
            for case in GROUPED_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("named-grouped-alternation-")
            and case.operation != "compile"
        )
        + tuple(
            case.case_id
            for case in OPTIONAL_GROUP_FIXTURE_BUNDLE.cases
            if case.case_id.startswith("systematic-optional-group-")
            and "-absent-" in case.case_id
        )
        + tuple(
            case.case_id
            for case in OPTIONAL_GROUP_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
        + tuple(
            case.case_id
            for case in NESTED_GROUP_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
        + tuple(
            case.case_id
            for case in NESTED_GROUP_ALTERNATION_FIXTURE_BUNDLE.cases
            if case.operation != "compile"
        )
    )
    assert {case.text_model for case in MATCH_GROUP_ACCESS_CASES} == {"str"}


@pytest.mark.parametrize(
    "case",
    GROUPED_SEGMENT_LEADING_CAPTURE_CASES,
    ids=_fixture_case_id,
)
def test_grouped_segment_leading_capture_groups_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is not None
    assert expected is not None
    assert observed.span() == expected.span() == (1, 4)
    assert observed.group(0) == expected.group(0) == "abc"
    assert observed.group(1) == expected.group(1) == "ab"
    assert observed.groups() == expected.groups() == ("ab",)


def test_fixture_bundles_load_expected_published_owner_order() -> None:
    assert tuple(bundle.manifest.path for bundle in FIXTURE_BUNDLES) == (
        select_correctness_fixture_paths(GROUPED_CAPTURE_FIXTURE_SELECTOR)
    )
    assert tuple(bundle.manifest.manifest_id for bundle in FIXTURE_BUNDLES) == (
        "grouped-match-workflows",
        "named-group-workflows",
        "grouped-segment-workflows",
        "nested-group-workflows",
        "nested-group-alternation-workflows",
        "grouped-alternation-workflows",
        "optional-group-workflows",
        "optional-group-alternation-workflows",
    )


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=_bundle_expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(bundle) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert bundle.expected_text_models == frozenset({"str"})
    assert {case.text_model for case in bundle.cases} == {"str"}


def test_grouped_capture_parity_suite_tracks_published_case_frontier() -> None:
    for bundle in FIXTURE_BUNDLES:
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=tuple(case.case_id for case in bundle.cases),
        )


def test_published_case_frontier_helper_preserves_ordered_uncovered_case_ids() -> None:
    selected_case_ids, uncovered_case_ids = _grouped_match_frontier_contract_case_ids()

    assert_fixture_bundle_tracks_published_case_frontier(
        GROUPED_MATCH_FIXTURE_BUNDLE,
        selected_case_ids=selected_case_ids,
        expected_uncovered_case_ids=uncovered_case_ids,
    )


def test_published_case_frontier_helper_rejects_duplicate_selected_case_ids() -> None:
    selected_case_ids, uncovered_case_ids = _grouped_match_frontier_contract_case_ids()
    duplicated_selected_case_ids = (*selected_case_ids, selected_case_ids[0])

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows selected_case_ids contain duplicate ids: "
            f"{(selected_case_ids[0],)}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            GROUPED_MATCH_FIXTURE_BUNDLE,
            selected_case_ids=duplicated_selected_case_ids,
            expected_uncovered_case_ids=uncovered_case_ids,
        )


def test_published_case_frontier_helper_rejects_duplicate_uncovered_case_ids() -> None:
    selected_case_ids, uncovered_case_ids = _grouped_match_frontier_contract_case_ids()
    assert uncovered_case_ids
    duplicated_uncovered_case_ids = (*uncovered_case_ids, uncovered_case_ids[0])

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows expected_uncovered_case_ids contain duplicate "
            f"ids: {(uncovered_case_ids[0],)}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            GROUPED_MATCH_FIXTURE_BUNDLE,
            selected_case_ids=selected_case_ids,
            expected_uncovered_case_ids=duplicated_uncovered_case_ids,
        )


def test_published_case_frontier_helper_rejects_selected_and_uncovered_overlap() -> None:
    selected_case_ids, _ = _grouped_match_frontier_contract_case_ids()
    overlapping_case_ids = (selected_case_ids[0],)

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows selected and uncovered case ids overlap: "
            f"{overlapping_case_ids}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            GROUPED_MATCH_FIXTURE_BUNDLE,
            selected_case_ids=selected_case_ids,
            expected_uncovered_case_ids=overlapping_case_ids,
        )


def test_published_case_frontier_helper_reports_missing_and_unexpected_case_ids() -> None:
    selected_case_ids, uncovered_case_ids = _grouped_match_frontier_contract_case_ids()

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows published frontier drifted; "
            "missing published case ids: ('missing-case-id',); "
            f"unexpected published case ids: {uncovered_case_ids}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            GROUPED_MATCH_FIXTURE_BUNDLE,
            selected_case_ids=selected_case_ids,
            expected_uncovered_case_ids=("missing-case-id",),
        )


def test_published_case_frontier_helper_reports_uncovered_order_drift() -> None:
    selected_case_ids, uncovered_case_ids = _grouped_match_frontier_contract_case_ids()
    reordered_uncovered_case_ids = tuple(reversed(uncovered_case_ids))

    assert reordered_uncovered_case_ids != uncovered_case_ids

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows uncovered published case ids changed; "
            f"expected {reordered_uncovered_case_ids}, got {uncovered_case_ids}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            GROUPED_MATCH_FIXTURE_BUNDLE,
            selected_case_ids=selected_case_ids,
            expected_uncovered_case_ids=reordered_uncovered_case_ids,
        )


def test_grouped_capture_direct_test_buckets_cover_selected_frontier() -> None:
    direct_test_case_id_buckets = {
        bundle.manifest.manifest_id.removesuffix("-workflows"): frozenset(
            case.case_id for case in bundle.cases
        )
        for bundle in FIXTURE_BUNDLES
    }

    assert tuple(direct_test_case_id_buckets) == tuple(
        bundle.manifest.manifest_id.removesuffix("-workflows")
        for bundle in FIXTURE_BUNDLES
    )

    assert_direct_test_case_id_buckets_cover_selected_frontier(
        direct_test_case_id_buckets,
        selected_case_ids=tuple(
            case.case_id
            for bundle in FIXTURE_BUNDLES
            for case in bundle.cases
        ),
        coverage_label="grouped capture direct-test case-id buckets",
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=_case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: CompileCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern, case.flags)


@pytest.mark.parametrize("case", MODULE_CASES, ids=_fixture_case_id)
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


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=_case_id)
def test_module_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    _, backend = regex_backend
    module_case = CASES_BY_ID[case.module_case_id]

    for text in case.module_misses:
        assert _module_call_with_text(backend, module_case, text) is None
        assert _module_call_with_text(re, module_case, text) is None


@pytest.mark.parametrize("case", PATTERN_CASES, ids=_fixture_case_id)
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


@pytest.mark.parametrize("case", PATTERN_BOUNDS_MATCH_CASES, ids=_case_id)
def test_pattern_helper_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(CASES_BY_ID[case.pattern_case_id]),
    )

    observed = invoke_bounded_pattern_case(observed_pattern, case)
    expected = invoke_bounded_pattern_case(expected_pattern, case)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=_fixture_case_id)
def test_match_group_accessors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)
    assert_valid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=_fixture_case_id)
def test_invalid_match_group_access_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=_fixture_case_id)
def test_match_metadata_apis_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is not None
    assert expected is not None

    default = object()

    assert observed.groups() == expected.groups()
    assert observed.groups(default) == expected.groups(default)
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(default) == expected.groupdict(default)
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup


@pytest.mark.parametrize(
    "case",
    OPTIONAL_GROUP_ABSENT_EXPAND_CASES,
    ids=_case_id,
)
def test_optional_group_absent_match_expand_preserves_whole_match_and_clears_group_reference(
    regex_backend: tuple[str, object],
    case: OptionalGroupExpandCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        CASES_BY_ID[case.case_id],
    )

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)

    observed_expansion = observed.expand(case.template)
    expected_expansion = expected.expand(case.template)

    assert type(observed_expansion) is type(expected_expansion)
    assert observed_expansion == expected_expansion == case.expected_expansion


@pytest.mark.parametrize("case", MODULE_CASES, ids=_fixture_case_id)
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


@pytest.mark.parametrize("case", PATTERN_CASES, ids=_fixture_case_id)
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


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=_case_id)
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


@pytest.mark.parametrize("case", PATTERN_BOUNDS_NO_MATCH_CASES, ids=_case_id)
def test_pattern_helper_bounds_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(CASES_BY_ID[case.pattern_case_id]),
    )

    observed = invoke_bounded_pattern_case(observed_pattern, case)
    expected = invoke_bounded_pattern_case(expected_pattern, case)

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)
