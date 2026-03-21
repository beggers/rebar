from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT, FixtureCase
from tests.python.fixture_parity_support import (
    BoundedPatternCase,
    FixtureBundle,
    SupplementalCase,
    assert_direct_bytes_follow_on_bundle_routing,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_bounded_pattern_case_match_parity,
    assert_bounded_pattern_case_no_match_parity,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_module_search_case_parity,
    assert_pattern_fullmatch_case_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_published_fixture_bundles,
    partition_direct_bytes_follow_on_case_buckets,
    published_bytes_texts_by_pattern,
    published_fixture_bundle_by_manifest_id,
)
BACKTRACKING_BRANCH_TEXT = {
    "short": "bc",
    "long": "bcc",
}


@dataclass(frozen=True)
class DirectBytesFollowOnSpec:
    id: str
    bundle: FixtureBundle
    cases: tuple[SupplementalCase, ...]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_module_search_texts_by_pattern: dict[bytes, frozenset[bytes]]
    expected_pattern_fullmatch_texts_by_pattern: dict[bytes, frozenset[bytes]]


@dataclass(frozen=True)
class BacktrackingTraceCase:
    id: str
    pattern: str
    search_text: str
    fullmatch_text: str

WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_NAMES = (
    "exact_repeat_quantified_group_workflows.py",
    "ranged_repeat_quantified_group_workflows.py",
    "wider_ranged_repeat_quantified_group_workflows.py",
    "broader_range_wider_ranged_repeat_quantified_group_workflows.py",
    "wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
    "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
    "broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
    "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
    "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
)
FIXTURE_BUNDLES = load_published_fixture_bundles(
    tuple(
        CORRECTNESS_FIXTURES_ROOT / fixture_name
        for fixture_name in WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_NAMES
    ),
    pattern_extractor=case_pattern,
)
NESTED_BROADER_RANGE_ALTERNATION_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows",
)
NESTED_BROADER_RANGE_CONDITIONAL_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
)
BROADER_RANGE_CONDITIONAL_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
)
BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
)
NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
)
BACKTRACKING_TRACE_BUNDLES = (
    BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE,
    NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE,
)
BROADER_RANGE_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-wider-ranged-repeat-conditional-numbered-bytes",
        pattern=rb"a((bc|de){1,4})?(?(1)d|e)",
        search_matches=(b"zzaezz", b"zzabcdzz", b"zzadedzz", b"zzabcdedededzz"),
        search_misses=(b"zzadzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"ae", b"abcded", b"abcbcded", b"abcdededed"),
        fullmatch_misses=(b"ad", b"abcdede", b"abcbcbcbcbcd"),
    ),
    SupplementalCase(
        id="broader-range-wider-ranged-repeat-conditional-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        search_matches=(b"zzaezz", b"zzabcdzz", b"zzadedzz", b"zzabcdedededzz"),
        search_misses=(b"zzadzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"ae", b"abcded", b"abcbcded", b"abcdededed"),
        fullmatch_misses=(b"ad", b"abcdede", b"abcbcbcbcbcd"),
    ),
)
BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-wider-ranged-repeat-backtracking-heavy-numbered-bytes",
        pattern=rb"a((bc|b)c){1,4}d",
        search_matches=(b"zzabcdzz", b"zzabccdzz"),
        search_misses=(b"zzabccbdzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"abcbccd", b"abccbcd", b"abcbccbccbcd"),
        fullmatch_misses=(b"abccbd", b"abcbcbcbcbcd"),
    ),
    SupplementalCase(
        id="broader-range-wider-ranged-repeat-backtracking-heavy-named-bytes",
        pattern=rb"a(?P<word>(bc|b)c){1,4}d",
        search_matches=(b"zzabccdzz", b"zzabcbccdzz", b"zzabcbccbccbcdzz"),
        search_misses=(b"zzabccbdzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"abccbcd",),
        fullmatch_misses=(b"abccbd", b"abcbcbcbcbcd"),
    ),
)
NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES = (
    SupplementalCase(
        id="nested-broader-range-wider-ranged-repeat-grouped-alternation-numbered-bytes",
        pattern=rb"a((bc|de){1,4})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adedededed"),
        fullmatch_misses=(b"ae", b"abcbcdede"),
    ),
    SupplementalCase(
        id="nested-broader-range-wider-ranged-repeat-grouped-alternation-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,4})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adedededed"),
        fullmatch_misses=(b"ae", b"abcbcbcbcbcd"),
    ),
)
NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="nested-broader-range-wider-ranged-repeat-grouped-conditional-numbered-bytes",
        pattern=rb"a(((bc|de){1,4})d)?(?(1)e|f)",
        search_matches=(b"zzafzz", b"zzabcdezz", b"zzadedezz"),
        fullmatch_matches=(b"abcbcdede",),
        fullmatch_misses=(b"abcbcded", b"ae"),
    ),
    SupplementalCase(
        id="nested-broader-range-wider-ranged-repeat-grouped-conditional-named-bytes",
        pattern=rb"a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
        search_matches=(b"zzafzz", b"zzadedezz", b"zzadededededezz"),
        fullmatch_matches=(b"abcbcdede",),
        fullmatch_misses=(b"ae", b"abcbcbcbcbcde"),
    ),
)
NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES = (
    SupplementalCase(
        id="nested-broader-range-wider-ranged-repeat-backtracking-heavy-numbered-bytes",
        pattern=rb"a(((bc|b)c){1,4})d",
        search_matches=(b"zzabcdzz", b"zzabccdzz"),
        search_misses=(b"zzabccbdzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"abcbccd", b"abccbcd", b"abcbccbccbcd"),
        fullmatch_misses=(b"abccbd",),
    ),
    SupplementalCase(
        id="nested-broader-range-wider-ranged-repeat-backtracking-heavy-named-bytes",
        pattern=rb"a(?P<outer>((bc|b)c){1,4})d",
        search_matches=(b"zzabccdzz", b"zzabcbccdzz", b"zzabcbccbccbcdzz"),
        search_misses=(b"zzabccbdzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"abccbcd",),
        fullmatch_misses=(b"abccbd", b"abcbcbcbcbcd"),
    ),
)
DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES = (
    DirectBytesFollowOnSpec(
        id="broader-range-conditional",
        bundle=BROADER_RANGE_CONDITIONAL_BUNDLE,
        cases=BROADER_RANGE_CONDITIONAL_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            BROADER_RANGE_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"zzaezz", b"zzabcdzz", b"zzadedzz"}
            ),
            BROADER_RANGE_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"zzaezz", b"zzadedzz", b"zzabcdedededzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            BROADER_RANGE_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"abcbcded", b"abcdede", b"ad"}
            ),
            BROADER_RANGE_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"abcbcded", b"abcbcbcbcbcd", b"ad"}
            ),
        },
    ),
    DirectBytesFollowOnSpec(
        id="broader-range-backtracking-heavy",
        bundle=BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE,
        cases=BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 5,
                ("pattern_call", "fullmatch"): 7,
            }
        ),
        expected_module_search_texts_by_pattern={
            BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"zzabcdzz", b"zzabccdzz"}
            ),
            BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {b"zzabccdzz", b"zzabcbccdzz", b"zzabcbccbccbcdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"abcbccd", b"abccbcd", b"abcbccbccbcd", b"abccbd"}
            ),
            BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {b"abccbcd", b"abccbd", b"abcbcbcbcbcd"}
            ),
        },
    ),
    DirectBytesFollowOnSpec(
        id="nested-broader-range-alternation",
        bundle=NESTED_BROADER_RANGE_ALTERNATION_BUNDLE,
        cases=NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
        expected_module_search_texts_by_pattern={
            NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"zzabcdzz", b"zzadedzz"}
            ),
            NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"zzabcdzz", b"zzadedzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"abcbcded", b"adedededed", b"ae", b"abcbcdede"}
            ),
            NESTED_BROADER_RANGE_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"abcbcded", b"adedededed", b"ae", b"abcbcbcbcbcd"}
            ),
        },
    ),
    DirectBytesFollowOnSpec(
        id="nested-broader-range-conditional",
        bundle=NESTED_BROADER_RANGE_CONDITIONAL_BUNDLE,
        cases=NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"zzafzz", b"zzabcdezz", b"zzadedezz"}
            ),
            NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"zzafzz", b"zzadedezz", b"zzadededededezz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"abcbcdede", b"abcbcded", b"ae"}
            ),
            NESTED_BROADER_RANGE_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"abcbcdede", b"ae", b"abcbcbcbcbcde"}
            ),
        },
    ),
    DirectBytesFollowOnSpec(
        id="nested-broader-range-backtracking-heavy",
        bundle=NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE,
        cases=NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 5,
                ("pattern_call", "fullmatch"): 7,
            }
        ),
        expected_module_search_texts_by_pattern={
            NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"zzabcdzz", b"zzabccdzz"}
            ),
            NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {b"zzabccdzz", b"zzabcbccdzz", b"zzabcbccbccbcdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"abcbccd", b"abccbcd", b"abcbccbccbcd", b"abccbd"}
            ),
            NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {b"abccbcd", b"abccbd", b"abcbcbcbcbcd"}
            ),
        },
    ),
)


def _flatten_direct_bytes_follow_on_surfaces() -> tuple[SupplementalCase, ...]:
    return tuple(
        case for spec in DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES for case in spec.cases
    )


# Keep the shared manifest contract honest, but route the published bytes slices
# through explicit supplemental parity anchors so the direct bytes contracts
# stay covered without duplicating the shared manifest rows in this suite.
COMPILE_CASES, MODULE_CASES, PATTERN_CASES = partition_direct_bytes_follow_on_case_buckets(
    FIXTURE_BUNDLES,
    tuple(spec.bundle for spec in DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES),
)
WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS = tuple(
    case.case_id for bundle in FIXTURE_BUNDLES for case in bundle.cases
)


def _wider_ranged_repeat_quantified_group_direct_test_case_id_buckets(
) -> dict[str, frozenset[str]]:
    return {
        "shared-compile": frozenset(case.case_id for case in COMPILE_CASES),
        "shared-module-search": frozenset(case.case_id for case in MODULE_CASES),
        "shared-pattern-fullmatch": frozenset(case.case_id for case in PATTERN_CASES),
        **{
            f"{spec.id}-bytes-follow-on": frozenset(
                case.case_id for case in spec.bundle.cases if case.text_model == "bytes"
            )
            for spec in DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
        },
    }


def _build_backtracking_trace_cases(
    *,
    prefix: str,
    numbered_pattern: str,
    named_pattern: str,
) -> tuple[BacktrackingTraceCase, ...]:
    cases: list[BacktrackingTraceCase] = []
    for variant, pattern in (
        ("numbered", numbered_pattern),
        ("named", named_pattern),
    ):
        for repetition_count in range(1, 5):
            for branch_order in product(("short", "long"), repeat=repetition_count):
                body = "".join(BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    BacktrackingTraceCase(
                        id=f"{prefix}-{variant}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


BACKTRACKING_TRACE_CASES = (
    *_build_backtracking_trace_cases(
        prefix="broader-range-wider-ranged-repeat-backtracking",
        numbered_pattern=r"a((bc|b)c){1,4}d",
        named_pattern=r"a(?P<word>(bc|b)c){1,4}d",
    ),
    *_build_backtracking_trace_cases(
        prefix="nested-broader-range-wider-ranged-repeat-backtracking",
        numbered_pattern=r"a(((bc|b)c){1,4})d",
        named_pattern=r"a(?P<outer>((bc|b)c){1,4})d",
    ),
)
EXPECTED_BACKTRACKING_FULLMATCH_TEXTS = frozenset(
    f"a{''.join(BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)}d"
    for repetition_count in range(1, 5)
    for branch_order in product(("short", "long"), repeat=repetition_count)
)
PATTERN_BOUNDS_MATCH_CASES = (
    BoundedPatternCase(
        id="broader-range-conditional-search-normalizes-negative-and-oversized-bounds",
        pattern=r"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        helper="search",
        string="xxaezz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="broader-range-backtracking-heavy-match-honors-narrowed-window",
        pattern=r"a((bc|b)c){1,4}d",
        helper="match",
        string="yyabccbcdzz",
        bounds=(2, 9),
    ),
    BoundedPatternCase(
        id=(
            "nested-broader-range-backtracking-heavy-fullmatch-preserves-"
            "visible-outer-capture-window"
        ),
        pattern=r"a(?P<outer>((bc|b)c){1,4})d",
        helper="fullmatch",
        string="yyabcbccbccbcdzz",
        bounds=(2, 14),
    ),
    BoundedPatternCase(
        id="broader-range-conditional-bytes-search-normalizes-negative-and-oversized-bounds",
        pattern=rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        helper="search",
        string=b"xxaezz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="broader-range-backtracking-heavy-bytes-match-honors-narrowed-window",
        pattern=rb"a((bc|b)c){1,4}d",
        helper="match",
        string=b"yyabccbcdzz",
        bounds=(2, 9),
    ),
    BoundedPatternCase(
        id=(
            "nested-broader-range-backtracking-heavy-bytes-fullmatch-preserves-"
            "visible-outer-capture-window"
        ),
        pattern=rb"a(?P<outer>((bc|b)c){1,4})d",
        helper="fullmatch",
        string=b"yyabcbccbccbcdzz",
        bounds=(2, 14),
    ),
)
PATTERN_BOUNDS_NO_MATCH_CASES = (
    BoundedPatternCase(
        id="broader-range-conditional-match-fails-when-endpos-truncates-the-yes-arm",
        pattern=r"a((bc|de){1,4})?(?(1)d|e)",
        helper="match",
        string="xxabcdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="broader-range-backtracking-heavy-search-skips-match-before-pos",
        pattern=r"a(?P<word>(bc|b)c){1,4}d",
        helper="search",
        string="yyabcbccdzz",
        bounds=(3, 11),
    ),
    BoundedPatternCase(
        id="nested-broader-range-backtracking-heavy-fullmatch-does-not-expand-to-whole-string",
        pattern=r"a(((bc|b)c){1,4})d",
        helper="fullmatch",
        string="yyabccbcdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="broader-range-conditional-bytes-match-fails-when-endpos-truncates-the-yes-arm",
        pattern=rb"a((bc|de){1,4})?(?(1)d|e)",
        helper="match",
        string=b"xxabcdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="broader-range-backtracking-heavy-bytes-search-skips-match-before-pos",
        pattern=rb"a(?P<word>(bc|b)c){1,4}d",
        helper="search",
        string=b"yyabcbccdzz",
        bounds=(3, 11),
    ),
    BoundedPatternCase(
        id=(
            "nested-broader-range-backtracking-heavy-bytes-fullmatch-does-"
            "not-expand-to-whole-string"
        ),
        pattern=rb"a(((bc|b)c){1,4})d",
        helper="fullmatch",
        string=b"yyabccbcdzz",
        bounds=(-50, 999),
    ),
)

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
        pattern_extractor=case_pattern,
    )


def test_published_fixture_bundle_loading_preserves_mixed_text_model_contract() -> None:
    bundle = BROADER_RANGE_CONDITIONAL_BUNDLE

    assert bundle.manifest.manifest_id == (
        "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
    )
    assert bundle.expected_case_ids is None
    assert bundle.expected_text_models == frozenset({"bytes", "str"})
    assert bundle.expected_patterns == frozenset(
        {
            r"a((bc|de){1,4})?(?(1)d|e)",
            r"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
            rb"a((bc|de){1,4})?(?(1)d|e)",
            rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        }
    )
    assert Counter((case.operation, case.helper) for case in bundle.cases) == Counter(
        {
            ("compile", None): 4,
            ("module_call", "search"): 12,
            ("pattern_call", "fullmatch"): 12,
        }
    )
    assert {
        isinstance(case_pattern(case), str)
        for case in bundle.cases
        if case.text_model == "str"
    } == {True}
    assert {
        isinstance(case_pattern(case), bytes)
        for case in bundle.cases
        if case.text_model == "bytes"
    } == {True}

    str_case_ids = frozenset(
        case.case_id for case in bundle.cases if case.text_model == "str"
    )
    bytes_case_ids = frozenset(
        case.case_id for case in bundle.cases if case.text_model == "bytes"
    )

    assert len(str_case_ids) == len(bytes_case_ids) == 14
    assert bytes_case_ids == {
        f"{case_id.removesuffix('-str')}-bytes" for case_id in str_case_ids
    }
    assert bundle.manifest.path.name == (
        "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=bundle.manifest.path,
        expected_ordered_case_ids=tuple(
            case.case_id for case in bundle.manifest.cases
        ),
    )


def test_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets_cover_selected_frontier(
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        _wider_ranged_repeat_quantified_group_direct_test_case_id_buckets(),
        selected_case_ids=WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS,
        coverage_label=(
            "wider-ranged-repeat quantified group direct-test case-id buckets"
        ),
    )


@pytest.mark.parametrize(
    "spec",
    DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES,
    ids=lambda spec: spec.id,
)
def test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets(
    spec: DirectBytesFollowOnSpec,
) -> None:
    _, bundle_bytes_cases = assert_direct_bytes_follow_on_bundle_routing(
        spec.bundle,
        compile_cases=COMPILE_CASES,
        module_cases=MODULE_CASES,
        pattern_cases=PATTERN_CASES,
    )

    assert bundle_bytes_cases
    assert {case.pattern for case in spec.cases} == frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation((spec.bundle,), "compile")
        if case.text_model == "bytes"
    )


@pytest.mark.parametrize(
    "spec",
    DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES,
    ids=lambda spec: spec.id,
)
def test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor(
    spec: DirectBytesFollowOnSpec,
) -> None:
    bundle_str_cases, bundle_bytes_cases = assert_direct_bytes_follow_on_bundle_routing(
        spec.bundle,
        compile_cases=COMPILE_CASES,
        module_cases=MODULE_CASES,
        pattern_cases=PATTERN_CASES,
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation((spec.bundle,), "compile")
        if case.text_model == "bytes"
    )

    assert len(spec.cases) == 2
    assert {case.pattern for case in spec.cases} == expected_compile_patterns
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == sum(
        spec.expected_operation_helper_counts.values()
    )
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == (
        spec.expected_operation_helper_counts
    )

    for case in spec.cases:
        assert case.unsupported_backends == ()
        assert case.unsupported_backend_reason is None
        assert set(case.search_matches).isdisjoint(case.search_misses)
        assert set(case.fullmatch_matches).isdisjoint(case.fullmatch_misses)
        assert all(
            isinstance(text, bytes)
            for text in (
                *case.search_matches,
                *case.search_misses,
                *case.fullmatch_matches,
                *case.fullmatch_misses,
            )
        )

    (
        published_module_texts_by_pattern,
        published_fullmatch_texts_by_pattern,
    ) = published_bytes_texts_by_pattern(bundle_bytes_cases)
    assert (
        published_module_texts_by_pattern
        == spec.expected_module_search_texts_by_pattern
    )
    assert (
        published_fullmatch_texts_by_pattern
        == spec.expected_pattern_fullmatch_texts_by_pattern
    )


def test_backtracking_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for bundle in BACKTRACKING_TRACE_BUNDLES
        for case in fixture_cases_for_operation((bundle,), "compile")
        if case.text_model == "str"
    )

    assert len(EXPECTED_BACKTRACKING_FULLMATCH_TEXTS) == 30
    assert len(BACKTRACKING_TRACE_CASES) == (
        len(expected_patterns) * len(EXPECTED_BACKTRACKING_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in BACKTRACKING_TRACE_CASES}) == len(
        BACKTRACKING_TRACE_CASES
    )
    assert {case.pattern for case in BACKTRACKING_TRACE_CASES} == expected_patterns

    for pattern in expected_patterns:
        matching_cases = tuple(
            case for case in BACKTRACKING_TRACE_CASES if case.pattern == pattern
        )
        assert len(matching_cases) == len(EXPECTED_BACKTRACKING_FULLMATCH_TEXTS)
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_BACKTRACKING_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            f"zz{text}zz" for text in EXPECTED_BACKTRACKING_FULLMATCH_TEXTS
        }


@pytest.mark.parametrize(
    "case",
    PATTERN_BOUNDS_MATCH_CASES,
    ids=lambda case: case.id,
)
def test_pattern_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    assert_bounded_pattern_case_match_parity(
        regex_backend,
        case,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


@pytest.mark.parametrize(
    "case",
    PATTERN_BOUNDS_NO_MATCH_CASES,
    ids=lambda case: case.id,
)
def test_pattern_bounds_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    assert_bounded_pattern_case_no_match_parity(
        regex_backend,
        case,
        check_regs=True,
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case_pattern(case), case.flags or 0)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_module_search_case_parity(regex_backend, case, check_regs=True)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_module_search_case_parity(
        regex_backend,
        case,
        check_convenience_api=True,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_module_search_case_parity(
        regex_backend,
        case,
        check_group_access=True,
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_pattern_fullmatch_case_parity(regex_backend, case, check_regs=True)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_pattern_fullmatch_case_parity(
        regex_backend,
        case,
        check_convenience_api=True,
    )


@pytest.mark.parametrize(
    "case", PATTERN_CASES, ids=lambda case: case.case_id
)
def test_pattern_fullmatch_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_pattern_fullmatch_case_parity(
        regex_backend,
        case,
        check_group_access=True,
    )


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_match_parity(backend_name, observed, expected, check_regs=True)

    for text in case.search_misses:
        assert backend.search(case.pattern, text) is None
        assert re.search(case.pattern, text) is None


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_module_search_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        assert_match_parity(backend_name, observed, expected, check_regs=True)

    for text in case.fullmatch_misses:
        assert observed_pattern.fullmatch(text) is None
        assert expected_pattern.fullmatch(text) is None


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_pattern_fullmatch_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = observed_pattern.fullmatch(case.fullmatch_text)
    expected = expected_pattern.fullmatch(case.fullmatch_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)
