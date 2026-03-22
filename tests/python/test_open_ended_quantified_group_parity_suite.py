from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import (
    FixtureCase,
    OPEN_ENDED_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    BoundedPatternCase,
    FixtureBundle,
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    PatternTraceCase as OpenEndedTraceCase,
    SupplementalCase,
    assert_direct_bytes_follow_on_bundle_routing,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_bounded_pattern_case_match_parity,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_module_search_case_parity,
    assert_pattern_fullmatch_case_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    build_selected_fixture_bundle,
    case_pattern,
    compile_with_cpython_parity,
    direct_test_case_id_buckets_for_follow_on_bundles,
    fixture_cases_for_operation,
    partition_direct_bytes_follow_on_case_buckets,
    published_bytes_texts_by_pattern,
    published_fixture_bundles_by_manifest_id,
)


OPEN_ENDED_BRANCH_TEXT = {
    "bc": "bc",
    "de": "de",
}
OPEN_ENDED_BRANCH_BYTES = {
    branch: text.encode("ascii") for branch, text in OPEN_ENDED_BRANCH_TEXT.items()
}
OPEN_ENDED_BACKTRACKING_BRANCH_TEXT = {
    "short": "bc",
    "long": "bcc",
}
OPEN_ENDED_BACKTRACKING_BRANCH_BYTES = {
    branch: text.encode("ascii")
    for branch, text in OPEN_ENDED_BACKTRACKING_BRANCH_TEXT.items()
}


FIXTURE_BUNDLES = tuple(
    build_selected_fixture_bundle(path, pattern_extractor=case_pattern)
    for path in select_correctness_fixture_paths(
        OPEN_ENDED_QUANTIFIED_GROUP_FIXTURE_SELECTOR
    )
)
FIXTURE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id(FIXTURE_BUNDLES)
OPEN_ENDED_ALTERNATION_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "open-ended-quantified-group-alternation-workflows"
]
OPEN_ENDED_CONDITIONAL_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "open-ended-quantified-group-alternation-conditional-workflows"
]
BROADER_RANGE_OPEN_ENDED_ALTERNATION_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "broader-range-open-ended-quantified-group-alternation-workflows"
]
BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "broader-range-open-ended-quantified-group-alternation-conditional-workflows"
]
BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows"
]
OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "open-ended-quantified-group-alternation-backtracking-heavy-workflows"
]
NESTED_OPEN_ENDED_ALTERNATION_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "nested-open-ended-quantified-group-alternation-workflows"
]
OPEN_ENDED_TRACE_BUNDLES = (
    OPEN_ENDED_ALTERNATION_BUNDLE,
    NESTED_OPEN_ENDED_ALTERNATION_BUNDLE,
)


@dataclass(frozen=True)
class BytesCaseSurfaceSpec:
    bundle: FixtureBundle
    cases: tuple[SupplementalCase, ...]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_module_search_texts_by_pattern: dict[bytes, frozenset[bytes]]
    expected_pattern_fullmatch_texts_by_pattern: dict[bytes, frozenset[bytes]]
    follow_on_id: str | None = None


OPEN_ENDED_BYTES_CASE_SURFACES = (
    BytesCaseSurfaceSpec(
        bundle=OPEN_ENDED_ALTERNATION_BUNDLE,
        cases=OPEN_ENDED_ALTERNATION_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_module_search_texts_by_pattern={
            OPEN_ENDED_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"zzabcdzz", b"zzadedzz"}
            ),
            OPEN_ENDED_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"zzabcdzz", b"zzadedzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            OPEN_ENDED_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"abcbcd", b"abcded", b"abcbcded", b"ad", b"abed"}
            ),
            OPEN_ENDED_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"abcded", b"abcbcded", b"adededed", b"ad", b"abed"}
            ),
        },
    ),
    BytesCaseSurfaceSpec(
        bundle=OPEN_ENDED_CONDITIONAL_BUNDLE,
        cases=OPEN_ENDED_CONDITIONAL_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 5,
            }
        ),
        expected_module_search_texts_by_pattern={
            OPEN_ENDED_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"zzaezz", b"zzabcdzz", b"zzadedzz"}
            ),
            OPEN_ENDED_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"zzaezz", b"zzadedzz", b"zzadedededzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            OPEN_ENDED_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"abcded", b"abcbcded", b"abcde"}
            ),
            OPEN_ENDED_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"abcbcded", b"ad"}
            ),
        },
    ),
    BytesCaseSurfaceSpec(
        bundle=BROADER_RANGE_OPEN_ENDED_ALTERNATION_BUNDLE,
        cases=BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_module_search_texts_by_pattern={
            BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"zzabcbcdzz", b"zzadededzz"}
            ),
            BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"zzabcbcdzz", b"zzadededzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"abcded", b"abcbcded", b"adededed", b"abcd", b"ad"}
            ),
            BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"abcded", b"abcbcded", b"adededed", b"abcd", b"ad"}
            ),
        },
        follow_on_id="broader-range-alternation",
    ),
    BytesCaseSurfaceSpec(
        bundle=OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,
        cases=OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 5,
                ("pattern_call", "fullmatch"): 5,
            }
        ),
        expected_module_search_texts_by_pattern={
            OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"zzabcdzz"}
            ),
            OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {
                    b"zzabccdzz",
                    b"zzabccbcdzz",
                    b"zzabcbccbcdzz",
                    b"zzabccbdzz",
                }
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"abccd", b"abcbcd", b"abcbccd", b"abcccd"}
            ),
            OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {b"abcbcbcbcd"}
            ),
        },
        follow_on_id="open-ended-backtracking-heavy",
    ),
    BytesCaseSurfaceSpec(
        bundle=BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE,
        cases=BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"zzaezz", b"zzabcbcdzz", b"zzadededzz"}
            ),
            BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"zzaezz", b"zzadededzz", b"zzadedededzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"abcded", b"abcbcded", b"abcdede", b"abcd"}
            ),
            BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"abcbcded", b"ad"}
            ),
        },
        follow_on_id="broader-range-conditional",
    ),
    BytesCaseSurfaceSpec(
        bundle=BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,
        cases=BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: (
                frozenset({b"zzabcbcdzz", b"zzabcbccdzz"})
            ),
            BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: (
                frozenset(
                    {
                        b"zzabcbccdzz",
                        b"zzabccbcdzz",
                        b"zzabcbcbcbcdzz",
                        b"zzabccbdzz",
                    }
                )
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: (
                frozenset({b"abccbcd", b"abcbcbcbcd", b"abcd", b"abccbd"})
            ),
            BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: (
                frozenset({b"abcbccd", b"abcd"})
            ),
        },
        follow_on_id="broader-range-backtracking-heavy",
    ),
    BytesCaseSurfaceSpec(
        bundle=NESTED_OPEN_ENDED_ALTERNATION_BUNDLE,
        cases=NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
        expected_module_search_texts_by_pattern={
            NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"zzabcdzz", b"zzadedzz"}
            ),
            NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"zzabcdzz", b"zzadedzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES[0].pattern: frozenset(
                {b"abcbcded", b"adededed", b"ae", b"abcbcdede"}
            ),
            NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES[1].pattern: frozenset(
                {b"abcbcded", b"adededed", b"ae", b"abcbcdede"}
            ),
        },
    ),
)
COMPILE_CASES, MODULE_CASES, PATTERN_CASES = partition_direct_bytes_follow_on_case_buckets(
    FIXTURE_BUNDLES,
    tuple(
        spec.bundle
        for spec in OPEN_ENDED_BYTES_CASE_SURFACES
        if spec.follow_on_id is not None
    ),
)


def _compile_case_prefix(case: FixtureCase) -> str:
    for suffix in ("-compile-metadata-str", "-compile-metadata-bytes"):
        if case.case_id.endswith(suffix):
            return case.case_id.removesuffix(suffix)
    raise AssertionError(f"unexpected compile case id {case.case_id!r}")


def _build_open_ended_trace_cases() -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for bundle in OPEN_ENDED_TRACE_BUNDLES:
        for case in fixture_cases_for_operation((bundle,), "compile"):
            if case.text_model != "str":
                continue
            pattern = case_pattern(case)
            assert isinstance(pattern, str)
            prefix = _compile_case_prefix(case)
            for repetition_count in range(1, 5):
                for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count):
                    body = "".join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)
                    branch_id = "-".join(branch_order)
                    fullmatch_text = f"a{body}d"
                    cases.append(
                        OpenEndedTraceCase(
                            id=f"{prefix}-{branch_id}",
                            pattern=pattern,
                            search_text=f"zz{fullmatch_text}zz",
                            fullmatch_text=fullmatch_text,
                        )
                    )
    return tuple(cases)


OPEN_ENDED_TRACE_CASES = _build_open_ended_trace_cases()
EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS = frozenset(
    f"a{''.join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)}d"
    for repetition_count in range(1, 5)
    for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count)
)


def _build_broader_range_open_ended_trace_cases() -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for case in fixture_cases_for_operation(
        (BROADER_RANGE_OPEN_ENDED_ALTERNATION_BUNDLE,),
        "compile",
    ):
        if case.text_model != "str":
            continue
        pattern = case_pattern(case)
        assert isinstance(pattern, str)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(2, 6):
            for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count):
                body = "".join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    OpenEndedTraceCase(
                        id=f"{prefix}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


BROADER_RANGE_OPEN_ENDED_TRACE_CASES = _build_broader_range_open_ended_trace_cases()
EXPECTED_BROADER_RANGE_OPEN_ENDED_FULLMATCH_TEXTS = frozenset(
    f"a{''.join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)}d"
    for repetition_count in range(2, 6)
    for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count)
)


def _build_broader_range_open_ended_conditional_trace_cases(
) -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for case in fixture_cases_for_operation(
        (BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE,),
        "compile",
    ):
        if case.text_model != "str":
            continue
        pattern = case_pattern(case)
        assert isinstance(pattern, str)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(2, 6):
            for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count):
                body = "".join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    OpenEndedTraceCase(
                        id=f"{prefix}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES = (
    _build_broader_range_open_ended_conditional_trace_cases()
)
EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_FULLMATCH_TEXTS = frozenset(
    f"a{''.join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)}d"
    for repetition_count in range(2, 6)
    for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count)
)


def _build_open_ended_bytes_trace_cases() -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for bundle in OPEN_ENDED_TRACE_BUNDLES:
        for case in fixture_cases_for_operation((bundle,), "compile"):
            if case.text_model != "bytes":
                continue
            pattern = case_pattern(case)
            assert isinstance(pattern, bytes)
            prefix = _compile_case_prefix(case)
            for repetition_count in range(1, 5):
                for branch_order in product(OPEN_ENDED_BRANCH_BYTES, repeat=repetition_count):
                    body = b"".join(
                        OPEN_ENDED_BRANCH_BYTES[branch] for branch in branch_order
                    )
                    branch_id = "-".join(branch_order)
                    fullmatch_text = b"a" + body + b"d"
                    cases.append(
                        OpenEndedTraceCase(
                            id=f"{prefix}-bytes-{branch_id}",
                            pattern=pattern,
                            search_text=b"zz" + fullmatch_text + b"zz",
                            fullmatch_text=fullmatch_text,
                        )
                    )
    return tuple(cases)


OPEN_ENDED_BYTES_TRACE_CASES = _build_open_ended_bytes_trace_cases()
EXPECTED_OPEN_ENDED_BYTES_FULLMATCH_TEXTS = frozenset(
    b"a" + b"".join(OPEN_ENDED_BRANCH_BYTES[branch] for branch in branch_order) + b"d"
    for repetition_count in range(1, 5)
    for branch_order in product(OPEN_ENDED_BRANCH_BYTES, repeat=repetition_count)
)


def _build_broader_range_open_ended_conditional_bytes_trace_cases(
) -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for case in fixture_cases_for_operation(
        (BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE,),
        "compile",
    ):
        if case.text_model != "bytes":
            continue
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(2, 6):
            for branch_order in product(OPEN_ENDED_BRANCH_BYTES, repeat=repetition_count):
                body = b"".join(
                    OPEN_ENDED_BRANCH_BYTES[branch] for branch in branch_order
                )
                branch_id = "-".join(branch_order)
                fullmatch_text = b"a" + body + b"d"
                cases.append(
                    OpenEndedTraceCase(
                        id=f"{prefix}-bytes-{branch_id}",
                        pattern=pattern,
                        search_text=b"zz" + fullmatch_text + b"zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES = (
    _build_broader_range_open_ended_conditional_bytes_trace_cases()
)
EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_FULLMATCH_TEXTS = frozenset(
    b"a" + b"".join(OPEN_ENDED_BRANCH_BYTES[branch] for branch in branch_order) + b"d"
    for repetition_count in range(2, 6)
    for branch_order in product(OPEN_ENDED_BRANCH_BYTES, repeat=repetition_count)
)


def _build_open_ended_backtracking_trace_cases() -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for case in fixture_cases_for_operation(
        (OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,),
        "compile",
    ):
        if case.text_model != "str":
            continue
        pattern = case_pattern(case)
        assert isinstance(pattern, str)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(1, 5):
            for branch_order in product(
                OPEN_ENDED_BACKTRACKING_BRANCH_TEXT,
                repeat=repetition_count,
            ):
                body = "".join(
                    OPEN_ENDED_BACKTRACKING_BRANCH_TEXT[branch]
                    for branch in branch_order
                )
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    OpenEndedTraceCase(
                        id=f"{prefix}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


OPEN_ENDED_BACKTRACKING_TRACE_CASES = _build_open_ended_backtracking_trace_cases()
EXPECTED_OPEN_ENDED_BACKTRACKING_FULLMATCH_TEXTS = frozenset(
    f"a{''.join(OPEN_ENDED_BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)}d"
    for repetition_count in range(1, 5)
    for branch_order in product(
        OPEN_ENDED_BACKTRACKING_BRANCH_TEXT,
        repeat=repetition_count,
    )
)


def _build_open_ended_backtracking_bytes_trace_cases() -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for case in fixture_cases_for_operation(
        (OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,),
        "compile",
    ):
        if case.text_model != "bytes":
            continue
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(1, 5):
            for branch_order in product(
                OPEN_ENDED_BACKTRACKING_BRANCH_BYTES,
                repeat=repetition_count,
            ):
                body = b"".join(
                    OPEN_ENDED_BACKTRACKING_BRANCH_BYTES[branch]
                    for branch in branch_order
                )
                branch_id = "-".join(branch_order)
                fullmatch_text = b"a" + body + b"d"
                cases.append(
                    OpenEndedTraceCase(
                        id=f"{prefix}-bytes-{branch_id}",
                        pattern=pattern,
                        search_text=b"zz" + fullmatch_text + b"zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES = (
    _build_open_ended_backtracking_bytes_trace_cases()
)
EXPECTED_OPEN_ENDED_BACKTRACKING_BYTES_FULLMATCH_TEXTS = frozenset(
    b"a"
    + b"".join(
        OPEN_ENDED_BACKTRACKING_BRANCH_BYTES[branch] for branch in branch_order
    )
    + b"d"
    for repetition_count in range(1, 5)
    for branch_order in product(
        OPEN_ENDED_BACKTRACKING_BRANCH_BYTES,
        repeat=repetition_count,
    )
)
PATTERN_BOUNDS_MATCH_CASES = (
    BoundedPatternCase(
        id=(
            "broader-range-open-ended-conditional-search-normalizes-negative-and-"
            "oversized-bounds-str"
        ),
        pattern=r"a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
        helper="search",
        string="xxaezz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="open-ended-backtracking-heavy-match-honors-narrowed-window-str",
        pattern=r"a((bc|b)c){1,}d",
        helper="match",
        string="yyabccbcdzz",
        bounds=(2, 9),
    ),
    BoundedPatternCase(
        id="nested-open-ended-fullmatch-preserves-visible-outer-capture-window-str",
        pattern=r"a(?P<outer>(bc|de){1,})d",
        helper="fullmatch",
        string="yyabcbcdzz",
        bounds=(2, 8),
    ),
    BoundedPatternCase(
        id="open-ended-conditional-bytes-search-normalizes-negative-and-oversized-bounds",
        pattern=rb"a(?P<outer>(bc|de){1,})?(?(outer)d|e)",
        helper="search",
        string=b"xxaezz",
        bounds=(-50, 999),
    ),
)
PATTERN_BOUNDS_NO_MATCH_CASES = (
    BoundedPatternCase(
        id=(
            "broader-range-open-ended-conditional-match-fails-below-lower-bound-"
            "within-window-str"
        ),
        pattern=r"a((bc|de){2,})?(?(1)d|e)",
        helper="match",
        string="xxabcdzz",
        bounds=(2, 6),
    ),
    BoundedPatternCase(
        id="open-ended-backtracking-heavy-search-skips-match-before-pos-str",
        pattern=r"a(?P<word>(bc|b)c){1,}d",
        helper="search",
        string="yyabcbccdzz",
        bounds=(3, 11),
    ),
    BoundedPatternCase(
        id="nested-open-ended-fullmatch-does-not-expand-to-whole-string-str",
        pattern=r"a((bc|de){1,})d",
        helper="fullmatch",
        string="yyabcbcdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="open-ended-conditional-bytes-match-fails-when-endpos-truncates-the-yes-arm",
        pattern=rb"a((bc|de){1,})?(?(1)d|e)",
        helper="match",
        string=b"xxabcdzz",
        bounds=(2, 5),
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


def test_open_ended_quantified_group_direct_test_case_id_buckets_cover_selected_frontier(
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        direct_test_case_id_buckets_for_follow_on_bundles(
            compile_cases=COMPILE_CASES,
            module_cases=MODULE_CASES,
            pattern_cases=PATTERN_CASES,
            module_bucket_label="shared-module-search",
            pattern_bucket_label="shared-pattern-fullmatch",
            follow_on_buckets=(
                (f"{spec.follow_on_id}-bytes-follow-on", spec.bundle)
                for spec in OPEN_ENDED_BYTES_CASE_SURFACES
                if spec.follow_on_id is not None
            ),
        ),
        selected_case_ids=tuple(
            case.case_id for bundle in FIXTURE_BUNDLES for case in bundle.cases
        ),
        coverage_label="open-ended quantified group direct-test case-id buckets",
    )


@pytest.mark.parametrize(
    "spec",
    OPEN_ENDED_BYTES_CASE_SURFACES,
    ids=lambda spec: spec.bundle.manifest.manifest_id,
)
def test_bytes_cases_stay_explicit_with_expected_bundle_coverage(
    spec: BytesCaseSurfaceSpec,
) -> None:
    bundle_str_cases = tuple(
        case for case in spec.bundle.cases if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case for case in spec.bundle.cases if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation((spec.bundle,), "compile")
        if case.text_model == "bytes"
    )
    direct_manifest_ids = frozenset(
        follow_on_spec.bundle.manifest.manifest_id
        for follow_on_spec in OPEN_ENDED_BYTES_CASE_SURFACES
        if follow_on_spec.follow_on_id is not None
    )

    assert (spec.follow_on_id is None) == (
        spec.bundle.manifest.manifest_id not in direct_manifest_ids
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


@pytest.mark.parametrize(
    "spec",
    tuple(spec for spec in OPEN_ENDED_BYTES_CASE_SURFACES if spec.follow_on_id is None),
    ids=lambda spec: spec.bundle.manifest.manifest_id,
)
def test_generic_bytes_fixture_rows_run_through_generic_case_buckets(
    spec: BytesCaseSurfaceSpec,
) -> None:
    bundle_manifest_id = spec.bundle.manifest.manifest_id
    bundle_bytes_cases = tuple(
        case for case in spec.bundle.cases if case.text_model == "bytes"
    )

    assert spec.follow_on_id is None
    assert {
        case.case_id
        for case in COMPILE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == {
        case.case_id for case in bundle_bytes_cases if case.operation == "compile"
    }
    assert {
        case.case_id
        for case in MODULE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == {
        case.case_id for case in bundle_bytes_cases if case.operation == "module_call"
    }
    assert {
        case.case_id
        for case in PATTERN_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == {
        case.case_id for case in bundle_bytes_cases if case.operation == "pattern_call"
    }


@pytest.mark.parametrize(
    "spec",
    tuple(
        spec for spec in OPEN_ENDED_BYTES_CASE_SURFACES if spec.follow_on_id is not None
    ),
    ids=lambda spec: spec.follow_on_id,
)
def test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets(
    spec: BytesCaseSurfaceSpec,
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
    ("supplemental_cases", "expected_case_ids"),
    (
        pytest.param(
            OPEN_ENDED_ALTERNATION_BYTES_CASES,
            (
                "open-ended-grouped-alternation-numbered-bytes",
                "open-ended-grouped-alternation-named-bytes",
            ),
            id="open-ended-alternation",
        ),
        pytest.param(
            NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
            (
                "nested-open-ended-grouped-alternation-numbered-bytes",
                "nested-open-ended-grouped-alternation-named-bytes",
            ),
            id="nested-open-ended-alternation",
        ),
        pytest.param(
            OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            (
                "open-ended-grouped-conditional-numbered-bytes",
                "open-ended-grouped-conditional-named-bytes",
            ),
            id="open-ended-conditional",
        ),
        pytest.param(
            OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            (
                "open-ended-grouped-backtracking-heavy-numbered-bytes",
                "open-ended-grouped-backtracking-heavy-named-bytes",
            ),
            id="open-ended-backtracking-heavy",
        ),
        pytest.param(
            BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
            (
                "broader-range-open-ended-grouped-alternation-numbered-bytes",
                "broader-range-open-ended-grouped-alternation-named-bytes",
            ),
            id="broader-range-open-ended-alternation",
        ),
        pytest.param(
            BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            (
                "broader-range-open-ended-grouped-conditional-numbered-bytes",
                "broader-range-open-ended-grouped-conditional-named-bytes",
            ),
            id="broader-range-open-ended-conditional",
        ),
        pytest.param(
            BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            (
                "broader-range-open-ended-grouped-backtracking-heavy-numbered-bytes",
                "broader-range-open-ended-grouped-backtracking-heavy-named-bytes",
            ),
            id="broader-range-open-ended-backtracking-heavy",
        ),
    ),
)
def test_open_ended_supplemental_bytes_case_tables_keep_case_ids_in_order(
    supplemental_cases: tuple[SupplementalCase, ...],
    expected_case_ids: tuple[str, ...],
) -> None:
    assert tuple(case.id for case in supplemental_cases) == expected_case_ids


def test_open_ended_direct_bytes_follow_on_case_surfaces_keep_expected_manifest_pairings(
) -> None:
    follow_on_specs = tuple(
        spec for spec in OPEN_ENDED_BYTES_CASE_SURFACES if spec.follow_on_id is not None
    )

    assert tuple(spec.follow_on_id for spec in follow_on_specs) == (
        "broader-range-alternation",
        "open-ended-backtracking-heavy",
        "broader-range-conditional",
        "broader-range-backtracking-heavy",
    )
    assert tuple(
        (spec.follow_on_id, spec.bundle.manifest.manifest_id) for spec in follow_on_specs
    ) == (
        (
            "broader-range-alternation",
            "broader-range-open-ended-quantified-group-alternation-workflows",
        ),
        (
            "open-ended-backtracking-heavy",
            "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
        ),
        (
            "broader-range-conditional",
            "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
        ),
        (
            "broader-range-backtracking-heavy",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
        ),
    )
    assert follow_on_specs[0].cases is BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES
    assert follow_on_specs[1].cases is OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    assert follow_on_specs[2].cases is BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES
    assert (
        follow_on_specs[3].cases
        is BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    )


def test_open_ended_direct_bytes_follow_on_case_surfaces_resolve_to_expected_published_mixed_fixtures(
) -> None:
    follow_on_specs = tuple(
        spec for spec in OPEN_ENDED_BYTES_CASE_SURFACES if spec.follow_on_id is not None
    )

    assert tuple(
        spec.bundle.manifest.path.name for spec in follow_on_specs
    ) == (
        "broader_range_open_ended_quantified_group_alternation_workflows.py",
        "open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
        "broader_range_open_ended_quantified_group_alternation_conditional_workflows.py",
        "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
    )
    assert all(
        {case.text_model for case in spec.bundle.cases} == {"bytes", "str"}
        for spec in follow_on_specs
    )
    assert all(
        {
            case.operation
            for case in spec.bundle.cases
            if case.text_model == "bytes"
        }
        == {"compile", "module_call", "pattern_call"}
        for spec in follow_on_specs
    )


def test_open_ended_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for bundle in OPEN_ENDED_TRACE_BUNDLES
        for case in fixture_cases_for_operation((bundle,), "compile")
        if case.text_model == "str"
    )

    assert len(EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS) == 30
    assert len(OPEN_ENDED_TRACE_CASES) == (
        len(expected_patterns) * len(EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in OPEN_ENDED_TRACE_CASES}) == len(
        OPEN_ENDED_TRACE_CASES
    )
    assert {case.pattern for case in OPEN_ENDED_TRACE_CASES} == expected_patterns

    for pattern in expected_patterns:
        matching_cases = tuple(
            case for case in OPEN_ENDED_TRACE_CASES if case.pattern == pattern
        )
        assert len(matching_cases) == len(EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS)
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            f"zz{text}zz" for text in EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS
        }


def test_broader_range_open_ended_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (BROADER_RANGE_OPEN_ENDED_ALTERNATION_BUNDLE,),
            "compile",
        )
        if case.text_model == "str"
    )

    assert len(EXPECTED_BROADER_RANGE_OPEN_ENDED_FULLMATCH_TEXTS) == 60
    assert len(BROADER_RANGE_OPEN_ENDED_TRACE_CASES) == (
        len(expected_patterns) * len(EXPECTED_BROADER_RANGE_OPEN_ENDED_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in BROADER_RANGE_OPEN_ENDED_TRACE_CASES}) == len(
        BROADER_RANGE_OPEN_ENDED_TRACE_CASES
    )
    assert {case.pattern for case in BROADER_RANGE_OPEN_ENDED_TRACE_CASES} == (
        expected_patterns
    )

    for pattern in expected_patterns:
        matching_cases = tuple(
            case
            for case in BROADER_RANGE_OPEN_ENDED_TRACE_CASES
            if case.pattern == pattern
        )
        assert len(matching_cases) == len(
            EXPECTED_BROADER_RANGE_OPEN_ENDED_FULLMATCH_TEXTS
        )
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_BROADER_RANGE_OPEN_ENDED_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            f"zz{text}zz" for text in EXPECTED_BROADER_RANGE_OPEN_ENDED_FULLMATCH_TEXTS
        }


def test_broader_range_open_ended_conditional_trace_cases_cover_all_declared_branch_orders(
) -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE,),
            "compile",
        )
        if case.text_model == "str"
    )

    assert len(EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_FULLMATCH_TEXTS) == 60
    assert len(BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES) == (
        len(expected_patterns)
        * len(EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_FULLMATCH_TEXTS)
    )
    assert len(
        {case.id for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES}
    ) == len(BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES)
    assert {case.pattern for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES} == (
        expected_patterns
    )

    for pattern in expected_patterns:
        matching_cases = tuple(
            case
            for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES
            if case.pattern == pattern
        )
        assert len(matching_cases) == len(
            EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_FULLMATCH_TEXTS
        )
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            f"zz{text}zz"
            for text in EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_FULLMATCH_TEXTS
        }


def test_open_ended_backtracking_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,),
            "compile",
        )
        if case.text_model == "str"
    )

    assert len(EXPECTED_OPEN_ENDED_BACKTRACKING_FULLMATCH_TEXTS) == 30
    assert len(OPEN_ENDED_BACKTRACKING_TRACE_CASES) == (
        len(expected_patterns) * len(EXPECTED_OPEN_ENDED_BACKTRACKING_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in OPEN_ENDED_BACKTRACKING_TRACE_CASES}) == len(
        OPEN_ENDED_BACKTRACKING_TRACE_CASES
    )
    assert {case.pattern for case in OPEN_ENDED_BACKTRACKING_TRACE_CASES} == (
        expected_patterns
    )

    for pattern in expected_patterns:
        matching_cases = tuple(
            case
            for case in OPEN_ENDED_BACKTRACKING_TRACE_CASES
            if case.pattern == pattern
        )
        assert len(matching_cases) == len(
            EXPECTED_OPEN_ENDED_BACKTRACKING_FULLMATCH_TEXTS
        )
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_OPEN_ENDED_BACKTRACKING_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            f"zz{text}zz" for text in EXPECTED_OPEN_ENDED_BACKTRACKING_FULLMATCH_TEXTS
        }


def test_open_ended_bytes_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for bundle in OPEN_ENDED_TRACE_BUNDLES
        for case in fixture_cases_for_operation((bundle,), "compile")
        if case.text_model == "bytes"
    )

    assert len(EXPECTED_OPEN_ENDED_BYTES_FULLMATCH_TEXTS) == 30
    assert len(OPEN_ENDED_BYTES_TRACE_CASES) == (
        len(expected_patterns) * len(EXPECTED_OPEN_ENDED_BYTES_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in OPEN_ENDED_BYTES_TRACE_CASES}) == len(
        OPEN_ENDED_BYTES_TRACE_CASES
    )
    assert {case.pattern for case in OPEN_ENDED_BYTES_TRACE_CASES} == expected_patterns

    for pattern in expected_patterns:
        matching_cases = tuple(
            case for case in OPEN_ENDED_BYTES_TRACE_CASES if case.pattern == pattern
        )
        assert len(matching_cases) == len(EXPECTED_OPEN_ENDED_BYTES_FULLMATCH_TEXTS)
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_OPEN_ENDED_BYTES_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            b"zz" + text + b"zz" for text in EXPECTED_OPEN_ENDED_BYTES_FULLMATCH_TEXTS
        }


def test_broader_range_open_ended_conditional_bytes_trace_cases_cover_all_declared_branch_orders(
) -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_FULLMATCH_TEXTS) == 60
    assert len(BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES) == (
        len(expected_patterns)
        * len(EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_FULLMATCH_TEXTS)
    )
    assert len(
        {case.id for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES}
    ) == len(BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES)
    assert {
        case.pattern for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES
    } == expected_patterns

    for pattern in expected_patterns:
        matching_cases = tuple(
            case
            for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES
            if case.pattern == pattern
        )
        assert len(matching_cases) == len(
            EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_FULLMATCH_TEXTS
        )
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            b"zz" + text + b"zz"
            for text in EXPECTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_FULLMATCH_TEXTS
        }


def test_open_ended_backtracking_bytes_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(EXPECTED_OPEN_ENDED_BACKTRACKING_BYTES_FULLMATCH_TEXTS) == 30
    assert len(OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES) == (
        len(expected_patterns)
        * len(EXPECTED_OPEN_ENDED_BACKTRACKING_BYTES_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES}) == len(
        OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES
    )
    assert {case.pattern for case in OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES} == (
        expected_patterns
    )

    for pattern in expected_patterns:
        matching_cases = tuple(
            case
            for case in OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES
            if case.pattern == pattern
        )
        assert len(matching_cases) == len(
            EXPECTED_OPEN_ENDED_BACKTRACKING_BYTES_FULLMATCH_TEXTS
        )
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_OPEN_ENDED_BACKTRACKING_BYTES_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            b"zz" + text + b"zz"
            for text in EXPECTED_OPEN_ENDED_BACKTRACKING_BYTES_FULLMATCH_TEXTS
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
    assert_bounded_pattern_case_match_parity(
        regex_backend,
        case,
        expect_match=False,
        check_regs=True,
    )


@pytest.mark.parametrize(
    "case",
    tuple(case for spec in OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases),
    ids=lambda case: case.id,
)
def test_supplemental_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    tuple(case for spec in OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases),
    ids=lambda case: case.id,
)
def test_supplemental_bytes_module_search_matches_cpython(
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
    tuple(case for spec in OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases),
    ids=lambda case: case.id,
)
def test_supplemental_bytes_module_search_convenience_api_matches_cpython(
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
    tuple(case for spec in OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases),
    ids=lambda case: case.id,
)
def test_supplemental_bytes_module_search_match_group_access_matches_cpython(
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
    tuple(case for spec in OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases),
    ids=lambda case: case.id,
)
def test_supplemental_bytes_pattern_fullmatch_matches_cpython(
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
    tuple(case for spec in OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases),
    ids=lambda case: case.id,
)
def test_supplemental_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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
    tuple(case for spec in OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases),
    ids=lambda case: case.id,
)
def test_supplemental_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
    assert_module_search_case_parity(regex_backend, case)


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
    assert_pattern_fullmatch_case_parity(regex_backend, case)


@pytest.mark.parametrize("case", OPEN_ENDED_TRACE_CASES, ids=lambda case: case.id)
def test_open_ended_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", OPEN_ENDED_TRACE_CASES, ids=lambda case: case.id)
def test_open_ended_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
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
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
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
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
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
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend
    assert isinstance(case.pattern, bytes)
    assert isinstance(case.search_text, bytes)

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend
    assert isinstance(case.pattern, bytes)
    assert isinstance(case.fullmatch_text, bytes)
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


@pytest.mark.parametrize("case", OPEN_ENDED_BYTES_TRACE_CASES, ids=lambda case: case.id)
def test_open_ended_bytes_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend
    assert isinstance(case.pattern, bytes)
    assert isinstance(case.search_text, bytes)

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize("case", OPEN_ENDED_BYTES_TRACE_CASES, ids=lambda case: case.id)
def test_open_ended_bytes_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend
    assert isinstance(case.pattern, bytes)
    assert isinstance(case.fullmatch_text, bytes)
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


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_BACKTRACKING_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_BACKTRACKING_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
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
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_bytes_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend
    assert isinstance(case.pattern, bytes)
    assert isinstance(case.search_text, bytes)

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_BACKTRACKING_BYTES_TRACE_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_bytes_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend
    assert isinstance(case.pattern, bytes)
    assert isinstance(case.fullmatch_text, bytes)
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


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_pattern_fullmatch_case_parity(
        regex_backend,
        case,
        check_group_access=True,
    )
