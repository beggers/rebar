from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT, FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    SupplementalCase,
    assert_direct_bytes_follow_on_bundle_routing,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    invoke_bounded_pattern_case,
    load_published_fixture_bundles,
    partition_direct_bytes_follow_on_case_buckets,
    published_bytes_texts_by_pattern,
    published_fixture_bundle_by_manifest_id,
    record_generated_match_failure,
)
BACKTRACKING_BRANCH_TEXT = {
    "short": "b",
    "long": "bc",
}
ZERO_REPETITION_NO_MATCH_TEXT = "ad"
OVERLAP_TAIL_NO_MATCH_TEXT = "abccd"


@dataclass(frozen=True)
class BacktrackingTraceCase:
    id: str
    pattern: str
    search_text: str
    fullmatch_text: str


@dataclass(frozen=True)
class SupplementalNoMatchCase:
    id: str
    target: str
    pattern: str
    text: str


@dataclass(frozen=True)
class QuantifiedAlternationBytesCaseExpectation:
    search_matches: tuple[bytes, ...]
    fullmatch_matches: tuple[bytes, ...]
    fullmatch_misses: tuple[bytes, ...]


@dataclass(frozen=True)
class QuantifiedAlternationDirectBytesFollowOnSpec:
    follow_on_id: str
    bundle: FixtureBundle
    cases: tuple[SupplementalCase, ...]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_module_search_texts_by_pattern: dict[bytes, frozenset[bytes]]
    expected_pattern_fullmatch_texts_by_pattern: dict[bytes, frozenset[bytes]]
    expected_case_payloads: dict[str, QuantifiedAlternationBytesCaseExpectation]


@dataclass(frozen=True)
class GeneratedQuantifiedAlternationParitySpec:
    bundle: FixtureBundle
    fixture_name: str
    expected_compile_case_ids: tuple[str, ...]
    expected_patterns: frozenset[str | bytes]
    expected_text_models: frozenset[str]
    candidate_lengths: range
    expected_candidate_count: int
    failure_prefix: str


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern_case_id: str
    helper: str
    string: str | bytes
    bounds: tuple[int, int]
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


HELPERS = ("search", "match", "fullmatch")
BODY_ATOMS = ("b", "c", "e")
WRAPPER_PAIRS = (
    ("", ""),
    ("zz", ""),
    ("", "zz"),
    ("zz", "zz"),
)
FAILURE_PREVIEW_LIMIT = 20
STR_AND_BYTES_TEXT_MODELS = frozenset({"bytes", "str"})


QUANTIFIED_ALTERNATION_FIXTURE_NAMES = (
    "literal_alternation_workflows.py",
    "exact_repeat_quantified_group_alternation_workflows.py",
    "quantified_alternation_workflows.py",
    "quantified_nested_group_alternation_workflows.py",
    "quantified_alternation_backtracking_heavy_workflows.py",
    "quantified_alternation_broader_range_workflows.py",
    "quantified_alternation_conditional_workflows.py",
    "quantified_alternation_open_ended_workflows.py",
    "quantified_alternation_nested_branch_workflows.py",
)
FIXTURE_BUNDLES = load_published_fixture_bundles(
    tuple(
        CORRECTNESS_FIXTURES_ROOT / fixture_name
        for fixture_name in QUANTIFIED_ALTERNATION_FIXTURE_NAMES
    ),
    pattern_extractor=case_pattern,
)
QUANTIFIED_ALTERNATION_BOUNDED_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "quantified-alternation-workflows",
)
QUANTIFIED_ALTERNATION_BROADER_RANGE_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "quantified-alternation-broader-range-workflows",
)
QUANTIFIED_ALTERNATION_CONDITIONAL_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "quantified-alternation-conditional-workflows",
)
QUANTIFIED_ALTERNATION_OPEN_ENDED_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "quantified-alternation-open-ended-workflows",
)
QUANTIFIED_ALTERNATION_NESTED_BRANCH_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "quantified-alternation-nested-branch-workflows",
)
BACKTRACKING_HEAVY_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "quantified-alternation-backtracking-heavy-workflows",
)
GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS = (
    GeneratedQuantifiedAlternationParitySpec(
        bundle=QUANTIFIED_ALTERNATION_BOUNDED_BUNDLE,
        fixture_name="quantified_alternation_workflows.py",
        expected_compile_case_ids=(
            "quantified-alternation-numbered-compile-metadata-str",
            "quantified-alternation-named-compile-metadata-str",
            "quantified-alternation-numbered-compile-metadata-bytes",
            "quantified-alternation-named-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,2}d",
                r"a(?P<word>b|c){1,2}d",
                rb"a(b|c){1,2}d",
                rb"a(?P<word>b|c){1,2}d",
            }
        ),
        expected_text_models=STR_AND_BYTES_TEXT_MODELS,
        candidate_lengths=range(4),
        expected_candidate_count=160,
        failure_prefix="bounded quantified alternation generated parity drifted",
    ),
    GeneratedQuantifiedAlternationParitySpec(
        bundle=QUANTIFIED_ALTERNATION_BROADER_RANGE_BUNDLE,
        fixture_name="quantified_alternation_broader_range_workflows.py",
        expected_compile_case_ids=(
            "quantified-alternation-broader-range-numbered-compile-metadata-str",
            "quantified-alternation-broader-range-named-compile-metadata-str",
            "quantified-alternation-broader-range-numbered-compile-metadata-bytes",
            "quantified-alternation-broader-range-named-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,3}d",
                r"a(?P<word>b|c){1,3}d",
                rb"a(b|c){1,3}d",
                rb"a(?P<word>b|c){1,3}d",
            }
        ),
        expected_text_models=STR_AND_BYTES_TEXT_MODELS,
        candidate_lengths=range(5),
        expected_candidate_count=484,
        failure_prefix="broader-range quantified alternation generated parity drifted",
    ),
    GeneratedQuantifiedAlternationParitySpec(
        bundle=BACKTRACKING_HEAVY_BUNDLE,
        fixture_name="quantified_alternation_backtracking_heavy_workflows.py",
        expected_compile_case_ids=(
            "quantified-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "quantified-alternation-backtracking-heavy-named-compile-metadata-str",
            "quantified-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
            "quantified-alternation-backtracking-heavy-named-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a(b|bc){1,2}d",
                r"a(?P<word>b|bc){1,2}d",
                rb"a(b|bc){1,2}d",
                rb"a(?P<word>b|bc){1,2}d",
            }
        ),
        expected_text_models=STR_AND_BYTES_TEXT_MODELS,
        candidate_lengths=range(5),
        expected_candidate_count=484,
        failure_prefix=(
            "backtracking-heavy quantified alternation generated parity drifted"
        ),
    ),
)


def _build_generated_quantified_alternation_candidate_texts(
    candidate_lengths: range,
) -> tuple[str, ...]:
    return tuple(
        f"{prefix}a{''.join(body)}d{suffix}"
        for length in candidate_lengths
        for body in product(BODY_ATOMS, repeat=length)
        for prefix, suffix in WRAPPER_PAIRS
    )


GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPEC_BY_MANIFEST_ID = {
    spec.bundle.expected_manifest_id: spec
    for spec in GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS
}
GENERATED_STR_CANDIDATE_TEXTS_BY_MANIFEST_ID = {
    spec.bundle.expected_manifest_id: _build_generated_quantified_alternation_candidate_texts(
        spec.candidate_lengths
    )
    for spec in GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS
}
GENERATED_BYTES_CANDIDATE_TEXTS_BY_MANIFEST_ID = {
    manifest_id: tuple(text.encode("ascii") for text in texts)
    for manifest_id, texts in GENERATED_STR_CANDIDATE_TEXTS_BY_MANIFEST_ID.items()
}
GENERATED_QUANTIFIED_ALTERNATION_COMPILE_CASES = tuple(
    case
    for spec in GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS
    for case in fixture_cases_for_operation((spec.bundle,), "compile")
)


def _generated_candidate_texts(
    spec: GeneratedQuantifiedAlternationParitySpec,
    case: FixtureCase,
) -> tuple[str | bytes, ...]:
    if case.text_model == "bytes":
        return GENERATED_BYTES_CANDIDATE_TEXTS_BY_MANIFEST_ID[
            spec.bundle.expected_manifest_id
        ]
    return GENERATED_STR_CANDIDATE_TEXTS_BY_MANIFEST_ID[spec.bundle.expected_manifest_id]


QUANTIFIED_ALTERNATION_BOUNDED_BYTES_CASES = (
    SupplementalCase(
        id="quantified-alternation-numbered-bytes",
        pattern=rb"a(b|c){1,2}d",
        search_matches=(b"zzacdz",),
        fullmatch_matches=(b"abcd",),
        fullmatch_misses=(),
    ),
    SupplementalCase(
        id="quantified-alternation-named-bytes",
        pattern=rb"a(?P<word>b|c){1,2}d",
        search_matches=(b"zzacbdzz",),
        fullmatch_matches=(b"abd",),
        fullmatch_misses=(),
    ),
)
QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES = (
    SupplementalCase(
        id="quantified-alternation-broader-range-numbered-bytes",
        pattern=rb"a(b|c){1,3}d",
        search_matches=(b"zzabdzz", b"zzacdzz"),
        fullmatch_matches=(b"abbbd", b"abccd", b"abcbd"),
        fullmatch_misses=(b"ad", b"abbbcd"),
    ),
    SupplementalCase(
        id="quantified-alternation-broader-range-named-bytes",
        pattern=rb"a(?P<word>b|c){1,3}d",
        search_matches=(b"zzabdzz", b"zzacdzz"),
        fullmatch_matches=(b"abbbd", b"abccd", b"abcbd"),
        fullmatch_misses=(b"ad", b"abbbcd"),
    ),
)
QUANTIFIED_ALTERNATION_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="quantified-alternation-conditional-numbered-bytes",
        pattern=rb"a((b|c){1,2})?(?(1)d|e)",
        search_matches=(b"zzaezz", b"zzabdzz"),
        fullmatch_matches=(b"abbd", b"abcd"),
        fullmatch_misses=(b"abe",),
    ),
    SupplementalCase(
        id="quantified-alternation-conditional-named-bytes",
        pattern=rb"a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
        search_matches=(b"zzaezz", b"zzacdzz"),
        fullmatch_matches=(b"accd", b"abcd"),
        fullmatch_misses=(b"acce",),
    ),
)
QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES = (
    SupplementalCase(
        id="quantified-alternation-open-ended-numbered-bytes",
        pattern=rb"a(b|c){1,}d",
        search_matches=(b"zzabdzz", b"zzacdzz"),
        fullmatch_matches=(b"abcd", b"abccd", b"abcbcd"),
        fullmatch_misses=(b"ad", b"abed"),
    ),
    SupplementalCase(
        id="quantified-alternation-open-ended-named-bytes",
        pattern=rb"a(?P<word>b|c){1,}d",
        search_matches=(b"zzabdzz", b"zzacdzz"),
        fullmatch_matches=(b"abcd", b"abccd", b"abcbcd"),
        fullmatch_misses=(b"ad", b"abed"),
    ),
)
QUANTIFIED_ALTERNATION_NESTED_BRANCH_BYTES_CASES = (
    SupplementalCase(
        id="quantified-alternation-nested-branch-numbered-bytes",
        pattern=rb"a((b|c)|de){1,2}d",
        search_matches=(b"zzabdzz",),
        fullmatch_matches=(b"aded", b"abded"),
        fullmatch_misses=(b"abde",),
    ),
    SupplementalCase(
        id="quantified-alternation-nested-branch-named-bytes",
        pattern=rb"a(?P<word>(b|c)|de){1,2}d",
        search_matches=(b"zzadedzz",),
        fullmatch_matches=(b"acd", b"adebd"),
        fullmatch_misses=(b"adeb",),
    ),
)
QUANTIFIED_ALTERNATION_BACKTRACKING_HEAVY_BYTES_CASES = (
    SupplementalCase(
        id="quantified-alternation-backtracking-heavy-numbered-bytes",
        pattern=rb"a(b|bc){1,2}d",
        search_matches=(b"zzabdzz",),
        fullmatch_matches=(b"abcd", b"abbcd", b"abcbd", b"abcbcd"),
        fullmatch_misses=(b"abccd",),
    ),
    SupplementalCase(
        id="quantified-alternation-backtracking-heavy-named-bytes",
        pattern=rb"a(?P<word>b|bc){1,2}d",
        search_matches=(b"zzabcdzz",),
        fullmatch_matches=(b"abbd", b"abcbd"),
        fullmatch_misses=(b"abccd",),
    ),
)
DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES = (
    QuantifiedAlternationDirectBytesFollowOnSpec(
        follow_on_id="bounded",
        bundle=QUANTIFIED_ALTERNATION_BOUNDED_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_BOUNDED_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BOUNDED_BYTES_CASES[0].pattern: frozenset(
                {b"zzacdz"}
            ),
            QUANTIFIED_ALTERNATION_BOUNDED_BYTES_CASES[1].pattern: frozenset(
                {b"zzacbdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BOUNDED_BYTES_CASES[0].pattern: frozenset(
                {b"abcd"}
            ),
            QUANTIFIED_ALTERNATION_BOUNDED_BYTES_CASES[1].pattern: frozenset(
                {b"abd"}
            ),
        },
        expected_case_payloads={
            "quantified-alternation-numbered-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzacdz",),
                fullmatch_matches=(b"abcd",),
                fullmatch_misses=(),
            ),
            "quantified-alternation-named-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzacbdzz",),
                fullmatch_matches=(b"abd",),
                fullmatch_misses=(),
            ),
        },
    ),
    QuantifiedAlternationDirectBytesFollowOnSpec(
        follow_on_id="broader-range",
        bundle=QUANTIFIED_ALTERNATION_BROADER_RANGE_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES[0].pattern: frozenset(
                {b"zzabdzz", b"zzacdzz"}
            ),
            QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES[1].pattern: frozenset(
                {b"zzabdzz", b"zzacdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES[0].pattern: frozenset(
                {b"abbbd", b"abccd", b"abcbd", b"ad", b"abbbcd"}
            ),
            QUANTIFIED_ALTERNATION_BROADER_RANGE_BYTES_CASES[1].pattern: frozenset(
                {b"abbbd", b"abccd", b"abcbd", b"ad", b"abbbcd"}
            ),
        },
        expected_case_payloads={
            "quantified-alternation-broader-range-numbered-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzabdzz", b"zzacdzz"),
                fullmatch_matches=(b"abbbd", b"abccd", b"abcbd"),
                fullmatch_misses=(b"ad", b"abbbcd"),
            ),
            "quantified-alternation-broader-range-named-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzabdzz", b"zzacdzz"),
                fullmatch_matches=(b"abbbd", b"abccd", b"abcbd"),
                fullmatch_misses=(b"ad", b"abbbcd"),
            ),
        },
    ),
    QuantifiedAlternationDirectBytesFollowOnSpec(
        follow_on_id="conditional",
        bundle=QUANTIFIED_ALTERNATION_CONDITIONAL_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_CONDITIONAL_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_ALTERNATION_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"zzaezz", b"zzabdzz"}
            ),
            QUANTIFIED_ALTERNATION_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"zzaezz", b"zzacdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_ALTERNATION_CONDITIONAL_BYTES_CASES[0].pattern: frozenset(
                {b"abbd", b"abcd", b"abe"}
            ),
            QUANTIFIED_ALTERNATION_CONDITIONAL_BYTES_CASES[1].pattern: frozenset(
                {b"accd", b"abcd", b"acce"}
            ),
        },
        expected_case_payloads={
            "quantified-alternation-conditional-numbered-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzaezz", b"zzabdzz"),
                fullmatch_matches=(b"abbd", b"abcd"),
                fullmatch_misses=(b"abe",),
            ),
            "quantified-alternation-conditional-named-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzaezz", b"zzacdzz"),
                fullmatch_matches=(b"accd", b"abcd"),
                fullmatch_misses=(b"acce",),
            ),
        },
    ),
    QuantifiedAlternationDirectBytesFollowOnSpec(
        follow_on_id="open-ended",
        bundle=QUANTIFIED_ALTERNATION_OPEN_ENDED_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES[0].pattern: frozenset(
                {b"zzabdzz", b"zzacdzz"}
            ),
            QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES[1].pattern: frozenset(
                {b"zzabdzz", b"zzacdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES[0].pattern: frozenset(
                {b"abcd", b"abccd", b"abcbcd", b"ad", b"abed"}
            ),
            QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES[1].pattern: frozenset(
                {b"abcd", b"abccd", b"abcbcd", b"ad", b"abed"}
            ),
        },
        expected_case_payloads={
            "quantified-alternation-open-ended-numbered-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzabdzz", b"zzacdzz"),
                fullmatch_matches=(b"abcd", b"abccd", b"abcbcd"),
                fullmatch_misses=(b"ad", b"abed"),
            ),
            "quantified-alternation-open-ended-named-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzabdzz", b"zzacdzz"),
                fullmatch_matches=(b"abcd", b"abccd", b"abcbcd"),
                fullmatch_misses=(b"ad", b"abed"),
            ),
        },
    ),
    QuantifiedAlternationDirectBytesFollowOnSpec(
        follow_on_id="nested-branch",
        bundle=QUANTIFIED_ALTERNATION_NESTED_BRANCH_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_NESTED_BRANCH_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_ALTERNATION_NESTED_BRANCH_BYTES_CASES[0].pattern: frozenset(
                {b"zzabdzz"}
            ),
            QUANTIFIED_ALTERNATION_NESTED_BRANCH_BYTES_CASES[1].pattern: frozenset(
                {b"zzadedzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_ALTERNATION_NESTED_BRANCH_BYTES_CASES[0].pattern: frozenset(
                {b"aded", b"abded", b"abde"}
            ),
            QUANTIFIED_ALTERNATION_NESTED_BRANCH_BYTES_CASES[1].pattern: frozenset(
                {b"acd", b"adebd", b"adeb"}
            ),
        },
        expected_case_payloads={
            "quantified-alternation-nested-branch-numbered-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzabdzz",),
                fullmatch_matches=(b"aded", b"abded"),
                fullmatch_misses=(b"abde",),
            ),
            "quantified-alternation-nested-branch-named-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzadedzz",),
                fullmatch_matches=(b"acd", b"adebd"),
                fullmatch_misses=(b"adeb",),
            ),
        },
    ),
    QuantifiedAlternationDirectBytesFollowOnSpec(
        follow_on_id="backtracking-heavy",
        bundle=BACKTRACKING_HEAVY_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_BACKTRACKING_HEAVY_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"zzabdzz"}
            ),
            QUANTIFIED_ALTERNATION_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {b"zzabcdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BACKTRACKING_HEAVY_BYTES_CASES[0].pattern: frozenset(
                {b"abcd", b"abbcd", b"abcbd", b"abcbcd", b"abccd"}
            ),
            QUANTIFIED_ALTERNATION_BACKTRACKING_HEAVY_BYTES_CASES[1].pattern: frozenset(
                {b"abbd", b"abcbd", b"abccd"}
            ),
        },
        expected_case_payloads={
            "quantified-alternation-backtracking-heavy-numbered-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzabdzz",),
                fullmatch_matches=(b"abcd", b"abbcd", b"abcbd", b"abcbcd"),
                fullmatch_misses=(b"abccd",),
            ),
            "quantified-alternation-backtracking-heavy-named-bytes": QuantifiedAlternationBytesCaseExpectation(
                search_matches=(b"zzabcdzz",),
                fullmatch_matches=(b"abbd", b"abcbd"),
                fullmatch_misses=(b"abccd",),
            ),
        },
    ),
)


def _flatten_direct_bytes_follow_on_surfaces() -> tuple[SupplementalCase, ...]:
    return tuple(
        case for spec in DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES for case in spec.cases
    )


# Keep the shared manifest contract honest, but route the published bytes slice
# through one explicit follow-on anchor so the generic shared buckets stay
# focused on the currently supported `str` cases.
COMPILE_CASES, MODULE_CASES, PATTERN_CASES = partition_direct_bytes_follow_on_case_buckets(
    FIXTURE_BUNDLES,
    tuple(spec.bundle for spec in DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES),
)
QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS = tuple(
    case.case_id for bundle in FIXTURE_BUNDLES for case in bundle.cases
)


def _quantified_alternation_direct_test_case_id_buckets() -> dict[str, frozenset[str]]:
    return {
        "shared-compile": frozenset(case.case_id for case in COMPILE_CASES),
        "shared-module-search": frozenset(case.case_id for case in MODULE_CASES),
        "shared-pattern-fullmatch": frozenset(case.case_id for case in PATTERN_CASES),
        **{
            f"{spec.follow_on_id}-bytes-follow-on": frozenset(
                case.case_id for case in spec.bundle.cases if case.text_model == "bytes"
            )
            for spec in DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
        },
    }


MATCH_GROUP_ACCESS_CASES = tuple(
    case for case in (*MODULE_CASES, *PATTERN_CASES) if "no-match" not in case.case_id
)
COMPILE_CASES_BY_ID = {
    case.case_id: case
    for case in fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
}
REGS_PARITY_CASE_IDS = frozenset(
    {
        "quantified-nested-group-alternation-numbered-module-search-lower-bound-b-str",
        "quantified-nested-group-alternation-numbered-pattern-fullmatch-repeated-mixed-str",
        "quantified-nested-group-alternation-named-module-search-lower-bound-c-str",
        "quantified-nested-group-alternation-named-pattern-fullmatch-repeated-mixed-str",
    }
)
BACKTRACKING_HEAVY_COMPILE_CASES = tuple(
    case
    for case in fixture_cases_for_operation((BACKTRACKING_HEAVY_BUNDLE,), "compile")
    if case.text_model == "str"
)
PATTERN_BOUNDS_MATCH_CASES = (
    BoundedPatternCase(
        id="quantified-alternation-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="quantified-alternation-numbered-compile-metadata-str",
        helper="search",
        string="xxabcdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="quantified-alternation-broader-range-named-fullmatch-honors-narrowed-window",
        pattern_case_id="quantified-alternation-broader-range-named-compile-metadata-str",
        helper="fullmatch",
        string="yyabccdzz",
        bounds=(2, 7),
    ),
    BoundedPatternCase(
        id="quantified-alternation-conditional-match-honors-else-window",
        pattern_case_id="quantified-alternation-conditional-numbered-compile-metadata-str",
        helper="match",
        string="xxaezz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="quantified-alternation-nested-branch-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="quantified-alternation-nested-branch-named-compile-metadata-str",
        helper="search",
        string="xxabcdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="quantified-alternation-bytes-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="quantified-alternation-numbered-compile-metadata-bytes",
        helper="search",
        string=b"xxabcdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="quantified-alternation-broader-range-named-bytes-fullmatch-honors-narrowed-window",
        pattern_case_id="quantified-alternation-broader-range-named-compile-metadata-bytes",
        helper="fullmatch",
        string=b"yyabccdzz",
        bounds=(2, 7),
    ),
    BoundedPatternCase(
        id="quantified-alternation-open-ended-named-bytes-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="quantified-alternation-open-ended-named-compile-metadata-bytes",
        helper="search",
        string=b"xxabcbcdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="quantified-alternation-conditional-named-bytes-match-honors-else-window",
        pattern_case_id="quantified-alternation-conditional-named-compile-metadata-bytes",
        helper="match",
        string=b"xxaezz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="quantified-alternation-nested-branch-named-bytes-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="quantified-alternation-nested-branch-named-compile-metadata-bytes",
        helper="search",
        string=b"xxadebdzz",
        bounds=(-50, 999),
    ),
)
PATTERN_BOUNDS_NO_MATCH_CASES = (
    BoundedPatternCase(
        id="quantified-alternation-search-skips-match-before-pos",
        pattern_case_id="quantified-alternation-numbered-compile-metadata-str",
        helper="search",
        string="xxabcdzz",
        bounds=(3, 8),
    ),
    BoundedPatternCase(
        id="quantified-alternation-broader-range-named-fullmatch-does-not-expand-to-whole-string",
        pattern_case_id="quantified-alternation-broader-range-named-compile-metadata-str",
        helper="fullmatch",
        string="yyabccdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="quantified-alternation-conditional-match-fails-when-endpos-truncates-yes-arm",
        pattern_case_id="quantified-alternation-conditional-numbered-compile-metadata-str",
        helper="match",
        string="xxabcdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="quantified-alternation-nested-branch-search-fails-when-endpos-truncates-tail",
        pattern_case_id="quantified-alternation-nested-branch-numbered-compile-metadata-str",
        helper="search",
        string="xxabcdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="quantified-alternation-bytes-search-skips-match-before-pos",
        pattern_case_id="quantified-alternation-numbered-compile-metadata-bytes",
        helper="search",
        string=b"xxabcdzz",
        bounds=(3, 8),
    ),
    BoundedPatternCase(
        id="quantified-alternation-broader-range-named-bytes-fullmatch-does-not-expand-to-whole-string",
        pattern_case_id="quantified-alternation-broader-range-named-compile-metadata-bytes",
        helper="fullmatch",
        string=b"yyabccdzz",
        bounds=(-50, 999),
    ),
    BoundedPatternCase(
        id="quantified-alternation-open-ended-named-bytes-search-skips-match-before-pos",
        pattern_case_id="quantified-alternation-open-ended-named-compile-metadata-bytes",
        helper="search",
        string=b"xxabcbcdzz",
        bounds=(3, 10),
    ),
    BoundedPatternCase(
        id="quantified-alternation-conditional-numbered-bytes-match-fails-when-endpos-truncates-yes-arm",
        pattern_case_id="quantified-alternation-conditional-numbered-compile-metadata-bytes",
        helper="match",
        string=b"xxabcdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="quantified-alternation-nested-branch-named-bytes-search-fails-when-endpos-truncates-tail",
        pattern_case_id="quantified-alternation-nested-branch-named-compile-metadata-bytes",
        helper="search",
        string=b"xxadebdzz",
        bounds=(2, 6),
    ),
)


def _compile_case_prefix(case: FixtureCase) -> str:
    suffix = "-compile-metadata-str"
    assert case.case_id.endswith(suffix)
    return case.case_id.removesuffix(suffix)


def _build_backtracking_trace_cases() -> tuple[BacktrackingTraceCase, ...]:
    cases: list[BacktrackingTraceCase] = []
    for case in BACKTRACKING_HEAVY_COMPILE_CASES:
        pattern = case_pattern(case)
        assert isinstance(pattern, str)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(1, 3):
            for branch_order in product(("short", "long"), repeat=repetition_count):
                body = "".join(BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    BacktrackingTraceCase(
                        id=f"{prefix}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


def _compile_pattern(case_id: str) -> str | bytes:
    pattern = case_pattern(COMPILE_CASES_BY_ID[case_id])
    assert isinstance(pattern, (str, bytes))
    return pattern


def _bounded_pattern(case: BoundedPatternCase) -> str | bytes:
    return _compile_pattern(case.pattern_case_id)


def _build_supplemental_no_match_cases() -> tuple[SupplementalNoMatchCase, ...]:
    cases: list[SupplementalNoMatchCase] = []
    for case in BACKTRACKING_HEAVY_COMPILE_CASES:
        pattern = case_pattern(case)
        assert isinstance(pattern, str)
        prefix = _compile_case_prefix(case)
        cases.extend(
            [
                SupplementalNoMatchCase(
                    id=f"{prefix}-module-search-miss-zero-repetition",
                    target="module",
                    pattern=pattern,
                    text=f"zz{ZERO_REPETITION_NO_MATCH_TEXT}zz",
                ),
                SupplementalNoMatchCase(
                    id=f"{prefix}-module-search-miss-overlap-tail",
                    target="module",
                    pattern=pattern,
                    text=f"zz{OVERLAP_TAIL_NO_MATCH_TEXT}zz",
                ),
                SupplementalNoMatchCase(
                    id=f"{prefix}-pattern-fullmatch-miss-zero-repetition",
                    target="pattern",
                    pattern=pattern,
                    text=ZERO_REPETITION_NO_MATCH_TEXT,
                ),
            ]
        )

    numbered_pattern = _compile_pattern(
        "quantified-nested-group-alternation-numbered-compile-metadata-str"
    )
    named_pattern = _compile_pattern(
        "quantified-nested-group-alternation-named-compile-metadata-str"
    )
    cases.extend(
        [
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-module-search-miss-too-short",
                target="module",
                pattern=numbered_pattern,
                text="zzadzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-module-search-miss-invalid-branch",
                target="module",
                pattern=numbered_pattern,
                text="zzabedzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-pattern-fullmatch-miss-too-short",
                target="pattern",
                pattern=numbered_pattern,
                text="ad",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-pattern-fullmatch-miss-invalid-branch",
                target="pattern",
                pattern=numbered_pattern,
                text="abed",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-module-search-miss-too-short",
                target="module",
                pattern=named_pattern,
                text="zzadzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-module-search-miss-invalid-branch",
                target="module",
                pattern=named_pattern,
                text="zzabedzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-pattern-fullmatch-miss-too-short",
                target="pattern",
                pattern=named_pattern,
                text="ad",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-pattern-fullmatch-miss-invalid-branch",
                target="pattern",
                pattern=named_pattern,
                text="abed",
            ),
        ]
    )
    return tuple(cases)


BACKTRACKING_TRACE_CASES = _build_backtracking_trace_cases()
SUPPLEMENTAL_NO_MATCH_CASES = _build_supplemental_no_match_cases()


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


@pytest.mark.parametrize(
    "spec",
    GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS,
    ids=lambda spec: spec.bundle.expected_manifest_id,
)
def test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests(
    spec: GeneratedQuantifiedAlternationParitySpec,
) -> None:
    compile_cases = fixture_cases_for_operation((spec.bundle,), "compile")

    assert spec.bundle.manifest.path == CORRECTNESS_FIXTURES_ROOT / spec.fixture_name
    assert tuple(case.case_id for case in compile_cases) == spec.expected_compile_case_ids
    assert {case_pattern(case) for case in compile_cases} == spec.expected_patterns
    assert {case.text_model for case in compile_cases} == spec.expected_text_models
    assert (
        len(
            GENERATED_STR_CANDIDATE_TEXTS_BY_MANIFEST_ID[
                spec.bundle.expected_manifest_id
            ]
        )
        == spec.expected_candidate_count
    )


def test_quantified_alternation_parity_suite_tracks_published_case_frontier() -> None:
    for bundle in FIXTURE_BUNDLES:
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=tuple(case.case_id for case in bundle.cases),
        )


def test_quantified_alternation_direct_test_case_id_buckets_cover_selected_frontier(
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        _quantified_alternation_direct_test_case_id_buckets(),
        selected_case_ids=QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS,
        coverage_label="quantified alternation direct-test case-id buckets",
    )


def test_direct_bytes_follow_on_case_surfaces_keep_expected_ids() -> None:
    assert tuple(
        (spec.follow_on_id, spec.bundle.manifest.manifest_id)
        for spec in DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
    ) == (
        ("bounded", "quantified-alternation-workflows"),
        ("broader-range", "quantified-alternation-broader-range-workflows"),
        ("conditional", "quantified-alternation-conditional-workflows"),
        ("open-ended", "quantified-alternation-open-ended-workflows"),
        ("nested-branch", "quantified-alternation-nested-branch-workflows"),
        ("backtracking-heavy", "quantified-alternation-backtracking-heavy-workflows"),
    )


@pytest.mark.parametrize(
    "spec",
    DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES,
    ids=lambda spec: spec.follow_on_id,
)
def test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets(
    spec: QuantifiedAlternationDirectBytesFollowOnSpec,
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
    ids=lambda spec: spec.follow_on_id,
)
def test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor(
    spec: QuantifiedAlternationDirectBytesFollowOnSpec,
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
        expected_payload = spec.expected_case_payloads[case.id]
        assert case.unsupported_backends == ()
        assert case.unsupported_backend_reason is None
        assert case.search_matches == expected_payload.search_matches
        assert case.fullmatch_matches == expected_payload.fullmatch_matches
        assert case.fullmatch_misses == expected_payload.fullmatch_misses
        assert set(case.search_matches).isdisjoint(case.fullmatch_misses)
        assert set(case.fullmatch_matches).isdisjoint(case.fullmatch_misses)
        assert all(
            isinstance(text, bytes)
            for text in (
                *case.search_matches,
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


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case_pattern(case), case.flags or 0)


@pytest.mark.parametrize(
    "case",
    GENERATED_QUANTIFIED_ALTERNATION_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_generated_quantified_alternation_text_matrix_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    spec = GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPEC_BY_MANIFEST_ID[case.manifest_id]
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        case.flags or 0,
    )

    failures: list[str] = []
    for text in _generated_candidate_texts(spec, case):
        for helper in HELPERS:
            record_generated_match_failure(
                failures,
                label=f"module.{helper}({pattern!r}, {text!r})",
                backend_name=backend_name,
                observed=getattr(backend, helper)(pattern, text),
                expected=getattr(re, helper)(pattern, text),
            )
            record_generated_match_failure(
                failures,
                label=f"pattern.{helper}({pattern!r}, {text!r})",
                backend_name=backend_name,
                observed=getattr(observed_pattern, helper)(text),
                expected=getattr(expected_pattern, helper)(text),
            )

    failure_preview = "\n".join(failures[:FAILURE_PREVIEW_LIMIT])
    if len(failures) > FAILURE_PREVIEW_LIMIT:
        failure_preview += f"\n... {len(failures) - FAILURE_PREVIEW_LIMIT} more"
    assert not failures, f"{spec.failure_prefix}:\n{failure_preview}"


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

    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


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

    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


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


@pytest.mark.parametrize(
    "case",
    MATCH_GROUP_ACCESS_CASES,
    ids=lambda case: case.case_id,
)
def test_match_group_access_apis_match_cpython(
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
            case_pattern(case),
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
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


def test_pattern_bounds_cases_stay_anchored_to_quantified_alternation_patterns() -> None:
    assert {
        case.id: _bounded_pattern(case) for case in PATTERN_BOUNDS_MATCH_CASES
    } == {
        "quantified-alternation-search-normalizes-negative-and-oversized-bounds": (
            r"a(b|c){1,2}d"
        ),
        "quantified-alternation-broader-range-named-fullmatch-honors-narrowed-window": (
            r"a(?P<word>b|c){1,3}d"
        ),
        "quantified-alternation-conditional-match-honors-else-window": (
            r"a((b|c){1,2})?(?(1)d|e)"
        ),
        "quantified-alternation-nested-branch-search-normalizes-negative-and-oversized-bounds": (
            r"a(?P<word>(b|c)|de){1,2}d"
        ),
        "quantified-alternation-bytes-search-normalizes-negative-and-oversized-bounds": (
            rb"a(b|c){1,2}d"
        ),
        "quantified-alternation-broader-range-named-bytes-fullmatch-honors-narrowed-window": (
            rb"a(?P<word>b|c){1,3}d"
        ),
        "quantified-alternation-open-ended-named-bytes-search-normalizes-negative-and-oversized-bounds": (
            rb"a(?P<word>b|c){1,}d"
        ),
        "quantified-alternation-conditional-named-bytes-match-honors-else-window": (
            rb"a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        ),
        "quantified-alternation-nested-branch-named-bytes-search-normalizes-negative-and-oversized-bounds": (
            rb"a(?P<word>(b|c)|de){1,2}d"
        ),
    }
    assert {
        case.id: _bounded_pattern(case) for case in PATTERN_BOUNDS_NO_MATCH_CASES
    } == {
        "quantified-alternation-search-skips-match-before-pos": r"a(b|c){1,2}d",
        "quantified-alternation-broader-range-named-fullmatch-does-not-expand-to-whole-string": (
            r"a(?P<word>b|c){1,3}d"
        ),
        "quantified-alternation-conditional-match-fails-when-endpos-truncates-yes-arm": (
            r"a((b|c){1,2})?(?(1)d|e)"
        ),
        "quantified-alternation-nested-branch-search-fails-when-endpos-truncates-tail": (
            r"a((b|c)|de){1,2}d"
        ),
        "quantified-alternation-bytes-search-skips-match-before-pos": (
            rb"a(b|c){1,2}d"
        ),
        "quantified-alternation-broader-range-named-bytes-fullmatch-does-not-expand-to-whole-string": (
            rb"a(?P<word>b|c){1,3}d"
        ),
        "quantified-alternation-open-ended-named-bytes-search-skips-match-before-pos": (
            rb"a(?P<word>b|c){1,}d"
        ),
        "quantified-alternation-conditional-numbered-bytes-match-fails-when-endpos-truncates-yes-arm": (
            rb"a((b|c){1,2})?(?(1)d|e)"
        ),
        "quantified-alternation-nested-branch-named-bytes-search-fails-when-endpos-truncates-tail": (
            rb"a(?P<word>(b|c)|de){1,2}d"
        ),
    }


@pytest.mark.parametrize("case", PATTERN_BOUNDS_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        _bounded_pattern(case),
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


@pytest.mark.parametrize("case", PATTERN_BOUNDS_NO_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_bounds_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        _bounded_pattern(case),
    )

    observed = invoke_bounded_pattern_case(observed_pattern, case)
    expected = invoke_bounded_pattern_case(expected_pattern, case)

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_heavy_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_heavy_pattern_fullmatch_branch_traces_match_cpython(
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
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", SUPPLEMENTAL_NO_MATCH_CASES, ids=lambda case: case.id)
def test_supplemental_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalNoMatchCase,
) -> None:
    backend_name, backend = regex_backend

    if case.target == "module":
        observed = backend.search(case.pattern, case.text)
        expected = re.search(case.pattern, case.text)
    else:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern,
        )
        observed = observed_pattern.fullmatch(case.text)
        expected = expected_pattern.fullmatch(case.text)

    assert observed is None
    assert expected is None


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
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython(
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
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)

    for text in case.fullmatch_misses:
        assert_match_result_parity(
            backend_name,
            observed_pattern.fullmatch(text),
            expected_pattern.fullmatch(text),
            check_regs=True,
        )


@pytest.mark.parametrize(
    "case",
    _flatten_direct_bytes_follow_on_surfaces(),
    ids=lambda case: case.id,
)
def test_direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython(
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
