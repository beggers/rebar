from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_fixture_bundles,
    published_fixture_bundle_by_manifest_id,
)


OPEN_ENDED_BRANCH_TEXT = {
    "bc": "bc",
    "de": "de",
}
OPEN_ENDED_BACKTRACKING_BRANCH_TEXT = {
    "short": "bc",
    "long": "bcc",
}


@dataclass(frozen=True)
class SupplementalCase:
    id: str
    pattern: bytes
    search_matches: tuple[bytes, ...] = ()
    search_misses: tuple[bytes, ...] = ()
    fullmatch_matches: tuple[bytes, ...] = ()
    fullmatch_misses: tuple[bytes, ...] = ()
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


@dataclass(frozen=True)
class OpenEndedTraceCase:
    id: str
    pattern: str
    search_text: str
    fullmatch_text: str


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern: str | bytes
    helper: str
    string: str | bytes
    bounds: tuple[int, int]


FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a(bc|de){1,}d",
                r"a(?P<word>bc|de){1,}d",
                rb"a(bc|de){1,}d",
                rb"a(?P<word>bc|de){1,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 8,
                ("pattern_call", "fullmatch"): 20,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "open_ended_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id="open-ended-quantified-group-alternation-conditional-workflows",
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,})?(?(1)d|e)",
                r"a(?P<outer>(bc|de){1,})?(?(outer)d|e)",
                rb"a((bc|de){1,})?(?(1)d|e)",
                rb"a(?P<outer>(bc|de){1,})?(?(outer)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 12,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id="open-ended-quantified-group-alternation-backtracking-heavy-workflows",
        expected_patterns=frozenset(
            {
                r"a((bc|b)c){1,}d",
                r"a(?P<word>(bc|b)c){1,}d",
                rb"a((bc|b)c){1,}d",
                rb"a(?P<word>(bc|b)c){1,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 10,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "broader_range_open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="broader-range-open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a(bc|de){2,}d",
                r"a(?P<word>bc|de){2,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
    ),
    FixtureBundleSpec(
        "broader_range_open_ended_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id=(
            "broader-range-open-ended-quantified-group-alternation-conditional-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|de){2,})?(?(1)d|e)",
                r"a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
                rb"a((bc|de){2,})?(?(1)d|e)",
                rb"a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 12,
                ("pattern_call", "fullmatch"): 12,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id=(
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|b)c){2,}d",
                r"a(?P<word>(bc|b)c){2,}d",
                rb"a((bc|b)c){2,}d",
                rb"a(?P<word>(bc|b)c){2,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 12,
                ("pattern_call", "fullmatch"): 12,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "nested_open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="nested-open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,})d",
                r"a(?P<outer>(bc|de){1,})d",
                rb"a((bc|de){1,})d",
                rb"a(?P<outer>(bc|de){1,})d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 8,
                ("pattern_call", "fullmatch"): 16,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
OPEN_ENDED_ALTERNATION_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "open-ended-quantified-group-alternation-workflows",
)
OPEN_ENDED_CONDITIONAL_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "open-ended-quantified-group-alternation-conditional-workflows",
)
BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
)
BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
)
OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
)
NESTED_OPEN_ENDED_ALTERNATION_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "nested-open-ended-quantified-group-alternation-workflows",
)
OPEN_ENDED_TRACE_BUNDLES = (
    OPEN_ENDED_ALTERNATION_BUNDLE,
    NESTED_OPEN_ENDED_ALTERNATION_BUNDLE,
)
OPEN_ENDED_ALTERNATION_BYTES_UNSUPPORTED_REASON = (
    "rebar backend does not yet implement the open-ended grouped alternation bytes pair "
    "(pending RBR-0550)"
)
OPEN_ENDED_ALTERNATION_BYTES_CASES = (
    SupplementalCase(
        id="open-ended-grouped-alternation-numbered-bytes",
        pattern=rb"a(bc|de){1,}d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcd", b"abcded", b"abcbcded"),
        fullmatch_misses=(b"ad", b"abed"),
        unsupported_backends=("rebar",),
        unsupported_backend_reason=OPEN_ENDED_ALTERNATION_BYTES_UNSUPPORTED_REASON,
    ),
    SupplementalCase(
        id="open-ended-grouped-alternation-named-bytes",
        pattern=rb"a(?P<word>bc|de){1,}d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcded", b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ad", b"abed"),
        unsupported_backends=("rebar",),
        unsupported_backend_reason=OPEN_ENDED_ALTERNATION_BYTES_UNSUPPORTED_REASON,
    ),
)
NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES = (
    SupplementalCase(
        id="nested-open-ended-grouped-alternation-numbered-bytes",
        pattern=rb"a((bc|de){1,})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ae", b"abcbcdede"),
    ),
    SupplementalCase(
        id="nested-open-ended-grouped-alternation-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ae", b"abcbcdede"),
    ),
)
OPEN_ENDED_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="open-ended-grouped-conditional-numbered-bytes",
        pattern=rb"a((bc|de){1,})?(?(1)d|e)",
        search_matches=(b"zzaezz", b"zzabcdzz", b"zzabcbcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcded", b"abcbcded"),
        fullmatch_misses=(b"abcde",),
    ),
    SupplementalCase(
        id="open-ended-grouped-conditional-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,})?(?(outer)d|e)",
        search_matches=(b"zzaezz", b"zzadedzz", b"zzadedededzz"),
        fullmatch_matches=(b"abcbcded",),
        fullmatch_misses=(b"ad",),
    ),
)
OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES = (
    SupplementalCase(
        id="open-ended-grouped-backtracking-heavy-numbered-bytes",
        pattern=rb"a((bc|b)c){1,}d",
        fullmatch_matches=(b"abccd", b"abcbcd", b"abcbccd"),
        fullmatch_misses=(b"abcccd",),
        search_matches=(b"zzabcdzz",),
    ),
    SupplementalCase(
        id="open-ended-grouped-backtracking-heavy-named-bytes",
        pattern=rb"a(?P<word>(bc|b)c){1,}d",
        search_matches=(b"zzabccdzz", b"zzabccbcdzz", b"zzabcbccbcdzz"),
        search_misses=(b"zzabccbdzz",),
        fullmatch_matches=(b"abcbcbcbcd",),
    ),
)
BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-open-ended-grouped-conditional-numbered-bytes",
        pattern=rb"a((bc|de){2,})?(?(1)d|e)",
        search_matches=(b"zzaezz", b"zzabcbcdzz", b"zzadededzz"),
        fullmatch_matches=(b"abcded", b"abcbcded"),
        fullmatch_misses=(b"abcdede", b"abcd"),
    ),
    SupplementalCase(
        id="broader-range-open-ended-grouped-conditional-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
        search_matches=(b"zzaezz", b"zzadededzz", b"zzadedededzz"),
        fullmatch_matches=(b"abcbcded",),
        fullmatch_misses=(b"ad",),
    ),
)
BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-open-ended-grouped-backtracking-heavy-numbered-bytes",
        pattern=rb"a((bc|b)c){2,}d",
        search_matches=(b"zzabcbcdzz", b"zzabcbccdzz"),
        fullmatch_matches=(b"abccbcd", b"abcbcbcbcd"),
        fullmatch_misses=(b"abcd", b"abccbd"),
    ),
    SupplementalCase(
        id="broader-range-open-ended-grouped-backtracking-heavy-named-bytes",
        pattern=rb"a(?P<word>(bc|b)c){2,}d",
        search_matches=(b"zzabcbccdzz", b"zzabccbcdzz", b"zzabcbcbcbcdzz"),
        search_misses=(b"zzabccbdzz",),
        fullmatch_matches=(b"abcbccd", b"abcbcbcbcd"),
        fullmatch_misses=(b"abcd",),
    ),
)
DIRECT_BYTES_FOLLOW_ON_MANIFEST_IDS = frozenset(
    {
        "open-ended-quantified-group-alternation-workflows",
        "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
        "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
    }
)


def _uses_direct_bytes_follow_on(case: FixtureCase) -> bool:
    return case.manifest_id in DIRECT_BYTES_FOLLOW_ON_MANIFEST_IDS and case.text_model == "bytes"


COMPILE_CASES = tuple(
    case
    for case in fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
    if not _uses_direct_bytes_follow_on(case)
)
MODULE_CASES = tuple(
    case
    for case in fixture_cases_for_operation(FIXTURE_BUNDLES, "module_call")
    if not _uses_direct_bytes_follow_on(case)
)
PATTERN_CASES = tuple(
    case
    for case in fixture_cases_for_operation(FIXTURE_BUNDLES, "pattern_call")
    if not _uses_direct_bytes_follow_on(case)
)


def _assert_match_group_access_apis_match_cpython(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


def _compile_case_prefix(case: FixtureCase) -> str:
    suffix = "-compile-metadata-str"
    assert case.case_id.endswith(suffix)
    return case.case_id.removesuffix(suffix)


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


def _invoke_bounded_pattern_case(compiled_pattern: object, case: BoundedPatternCase) -> object:
    return getattr(compiled_pattern, case.helper)(case.string, *case.bounds)


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


def test_open_ended_alternation_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor(
) -> None:
    bundle_str_cases = tuple(
        case for case in OPEN_ENDED_ALTERNATION_BUNDLE.cases if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case
        for case in OPEN_ENDED_ALTERNATION_BUNDLE.cases
        if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (OPEN_ENDED_ALTERNATION_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(OPEN_ENDED_ALTERNATION_BYTES_CASES) == 2
    assert {case.id for case in OPEN_ENDED_ALTERNATION_BYTES_CASES} == {
        "open-ended-grouped-alternation-numbered-bytes",
        "open-ended-grouped-alternation-named-bytes",
    }
    assert {case.pattern for case in OPEN_ENDED_ALTERNATION_BYTES_CASES} == (
        expected_compile_patterns
    )
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 16
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 4,
            ("pattern_call", "fullmatch"): 10,
        }
    )

    for case in OPEN_ENDED_ALTERNATION_BYTES_CASES:
        assert case.unsupported_backends == ("rebar",)
        assert case.unsupported_backend_reason == (
            OPEN_ENDED_ALTERNATION_BYTES_UNSUPPORTED_REASON
        )
        assert case.search_misses == ()
        assert len(case.search_matches) == 2
        assert len(case.fullmatch_matches) == 3
        assert len(case.fullmatch_misses) == 2
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

    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}
    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

    numbered_case, named_case = OPEN_ENDED_ALTERNATION_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzabcdzz", b"zzadedzz"},
        named_case.pattern: {b"zzabcdzz", b"zzadedzz"},
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abcbcd", b"abcded", b"abcbcded", b"ad", b"abed"},
        named_case.pattern: {b"abcded", b"abcbcded", b"adededed", b"ad", b"abed"},
    }


def test_open_ended_alternation_bytes_fixture_rows_route_through_direct_follow_on_anchor(
) -> None:
    bundle_manifest_id = OPEN_ENDED_ALTERNATION_BUNDLE.manifest.manifest_id

    assert {
        case.case_id
        for case in COMPILE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in MODULE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in PATTERN_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()


def test_open_ended_conditional_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor(
) -> None:
    bundle_str_cases = tuple(
        case
        for case in OPEN_ENDED_CONDITIONAL_BUNDLE.cases
        if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case
        for case in OPEN_ENDED_CONDITIONAL_BUNDLE.cases
        if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (OPEN_ENDED_CONDITIONAL_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(OPEN_ENDED_CONDITIONAL_BYTES_CASES) == 2
    assert {case.id for case in OPEN_ENDED_CONDITIONAL_BYTES_CASES} == {
        "open-ended-grouped-conditional-numbered-bytes",
        "open-ended-grouped-conditional-named-bytes",
    }
    assert {case.pattern for case in OPEN_ENDED_CONDITIONAL_BYTES_CASES} == (
        expected_compile_patterns
    )
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 13
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 6,
            ("pattern_call", "fullmatch"): 5,
        }
    )

    for case in OPEN_ENDED_CONDITIONAL_BYTES_CASES:
        assert case.unsupported_backends == ()
        assert case.unsupported_backend_reason is None
        assert case.search_misses == ()
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

    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}
    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

    numbered_case, named_case = OPEN_ENDED_CONDITIONAL_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzaezz", b"zzabcdzz", b"zzadedzz"},
        named_case.pattern: {b"zzaezz", b"zzadedzz", b"zzadedededzz"},
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abcded", b"abcbcded", b"abcde"},
        named_case.pattern: {b"abcbcded", b"ad"},
    }


def test_open_ended_conditional_bytes_fixture_rows_run_through_generic_case_buckets(
) -> None:
    bundle_manifest_id = OPEN_ENDED_CONDITIONAL_BUNDLE.manifest.manifest_id
    bundle_bytes_cases = tuple(
        case
        for case in OPEN_ENDED_CONDITIONAL_BUNDLE.cases
        if case.text_model == "bytes"
    )

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


def test_open_ended_backtracking_heavy_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor(
) -> None:
    bundle_str_cases = tuple(
        case
        for case in OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE.cases
        if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case
        for case in OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE.cases
        if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES) == 2
    assert {case.id for case in OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES} == {
        "open-ended-grouped-backtracking-heavy-numbered-bytes",
        "open-ended-grouped-backtracking-heavy-named-bytes",
    }
    assert {case.pattern for case in OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES} == (
        expected_compile_patterns
    )
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 12
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 5,
            ("pattern_call", "fullmatch"): 5,
        }
    )

    for case in OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES:
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

    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}
    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

    numbered_case, named_case = OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzabcdzz"},
        named_case.pattern: {
            b"zzabccdzz",
            b"zzabccbcdzz",
            b"zzabcbccbcdzz",
            b"zzabccbdzz",
        },
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abccd", b"abcbcd", b"abcbccd", b"abcccd"},
        named_case.pattern: {b"abcbcbcbcd"},
    }


def test_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor(
) -> None:
    bundle_manifest_id = OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE.manifest.manifest_id

    assert {
        case.case_id
        for case in COMPILE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in MODULE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in PATTERN_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()


def test_broader_range_open_ended_conditional_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor(
) -> None:
    bundle_str_cases = tuple(
        case
        for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE.cases
        if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case
        for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE.cases
        if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES) == 2
    assert {case.id for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES} == {
        "broader-range-open-ended-grouped-conditional-numbered-bytes",
        "broader-range-open-ended-grouped-conditional-named-bytes",
    }
    assert {
        case.pattern for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES
    } == expected_compile_patterns
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 14
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 6,
            ("pattern_call", "fullmatch"): 6,
        }
    )

    for case in BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES:
        assert case.unsupported_backends == ()
        assert case.unsupported_backend_reason is None
        assert case.search_misses == ()
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

    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}
    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

    numbered_case, named_case = BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzaezz", b"zzabcbcdzz", b"zzadededzz"},
        named_case.pattern: {b"zzaezz", b"zzadededzz", b"zzadedededzz"},
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abcded", b"abcbcded", b"abcdede", b"abcd"},
        named_case.pattern: {b"abcbcded", b"ad"},
    }


def test_broader_range_open_ended_conditional_bytes_fixture_rows_route_through_direct_follow_on_anchor(
) -> None:
    bundle_manifest_id = BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE.manifest.manifest_id

    assert {
        case.case_id
        for case in COMPILE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in MODULE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in PATTERN_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()


def test_broader_range_open_ended_backtracking_heavy_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor(
) -> None:
    bundle_str_cases = tuple(
        case
        for case in BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE.cases
        if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case
        for case in BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE.cases
        if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES) == 2
    assert {
        case.id for case in BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    } == {
        "broader-range-open-ended-grouped-backtracking-heavy-numbered-bytes",
        "broader-range-open-ended-grouped-backtracking-heavy-named-bytes",
    }
    assert {
        case.pattern for case in BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    } == expected_compile_patterns
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 14
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 6,
            ("pattern_call", "fullmatch"): 6,
        }
    )

    for case in BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES:
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

    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}
    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

    numbered_case, named_case = BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzabcbcdzz", b"zzabcbccdzz"},
        named_case.pattern: {
            b"zzabcbccdzz",
            b"zzabccbcdzz",
            b"zzabcbcbcbcdzz",
            b"zzabccbdzz",
        },
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abccbcd", b"abcbcbcbcd", b"abcd", b"abccbd"},
        named_case.pattern: {b"abcbccd", b"abcd"},
    }


def test_broader_range_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor(
) -> None:
    bundle_manifest_id = BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE.manifest.manifest_id

    assert {
        case.case_id
        for case in COMPILE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in MODULE_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()
    assert {
        case.case_id
        for case in PATTERN_CASES
        if case.manifest_id == bundle_manifest_id and case.text_model == "bytes"
    } == set()


def test_nested_open_ended_alternation_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor(
) -> None:
    bundle_str_cases = tuple(
        case
        for case in NESTED_OPEN_ENDED_ALTERNATION_BUNDLE.cases
        if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case
        for case in NESTED_OPEN_ENDED_ALTERNATION_BUNDLE.cases
        if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (NESTED_OPEN_ENDED_ALTERNATION_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES) == 2
    assert {case.id for case in NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES} == {
        "nested-open-ended-grouped-alternation-numbered-bytes",
        "nested-open-ended-grouped-alternation-named-bytes",
    }
    assert {case.pattern for case in NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES} == (
        expected_compile_patterns
    )
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 14
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 4,
            ("pattern_call", "fullmatch"): 8,
        }
    )

    for case in NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES:
        assert case.search_misses == ()
        assert len(case.search_matches) == 2
        assert len(case.fullmatch_matches) == 2
        assert len(case.fullmatch_misses) == 2
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

    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}
    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

    numbered_case, named_case = NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzabcdzz", b"zzadedzz"},
        named_case.pattern: {b"zzabcdzz", b"zzadedzz"},
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abcbcded", b"adededed", b"ae", b"abcbcdede"},
        named_case.pattern: {b"abcbcded", b"adededed", b"ae", b"abcbcdede"},
    }


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


@pytest.mark.parametrize(
    "case",
    PATTERN_BOUNDS_MATCH_CASES,
    ids=lambda case: case.id,
)
def test_pattern_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = _invoke_bounded_pattern_case(observed_pattern, case)
    expected = _invoke_bounded_pattern_case(expected_pattern, case)

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )
    assert_match_convenience_api_parity(observed, expected)
    _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    PATTERN_BOUNDS_NO_MATCH_CASES,
    ids=lambda case: case.id,
)
def test_pattern_bounds_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = _invoke_bounded_pattern_case(observed_pattern, case)
    expected = _invoke_bounded_pattern_case(expected_pattern, case)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_alternation_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_alternation_bytes_module_search_matches_cpython(
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
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_alternation_bytes_module_search_convenience_api_matches_cpython(
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
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_alternation_bytes_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_alternation_bytes_pattern_fullmatch_matches_cpython(
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
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_alternation_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_alternation_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_conditional_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_conditional_bytes_module_search_matches_cpython(
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
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_conditional_bytes_module_search_convenience_api_matches_cpython(
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
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_conditional_bytes_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_conditional_bytes_pattern_fullmatch_matches_cpython(
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
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_conditional_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_conditional_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_heavy_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_heavy_bytes_module_search_matches_cpython(
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
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_heavy_bytes_module_search_convenience_api_matches_cpython(
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
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_heavy_bytes_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_heavy_bytes_pattern_fullmatch_matches_cpython(
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
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_heavy_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_open_ended_backtracking_heavy_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_module_search_matches_cpython(
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
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_module_search_convenience_api_matches_cpython(
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
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_pattern_fullmatch_matches_cpython(
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
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_module_search_matches_cpython(
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


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_module_search_convenience_api_matches_cpython(
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
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_pattern_fullmatch_matches_cpython(
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
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_conditional_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_backtracking_heavy_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_backtracking_heavy_bytes_module_search_matches_cpython(
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
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_backtracking_heavy_bytes_module_search_convenience_api_matches_cpython(
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
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_backtracking_heavy_bytes_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_backtracking_heavy_bytes_pattern_fullmatch_matches_cpython(
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
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_backtracking_heavy_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_open_ended_backtracking_heavy_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
        _assert_match_group_access_apis_match_cpython(observed, expected)


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
    backend_name, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_parity(backend_name, observed, expected)


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


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    _assert_match_group_access_apis_match_cpython(observed, expected)
