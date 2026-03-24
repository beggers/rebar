from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import (
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    BoundedPatternCase as DirectBytesBoundedPatternCase,
    CaseIdBoundedPatternCase as BoundedPatternCase,
    FixtureBundle,
    WRAPPER_PAIRS,
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
    direct_test_case_id_buckets_for_follow_on_bundles,
    fixture_cases_by_id,
    fixture_cases_for_operation,
    invoke_bounded_pattern_case,
    load_published_fixture_bundles,
    ordered_fixture_bundle_case_ids,
    partition_direct_bytes_follow_on_case_buckets,
    published_bytes_texts_by_pattern,
    record_generated_match_failure,
    requested_published_fixture_bundles,
    SupplementalMissCase,
    str_case_pattern,
    workflow_result_with_cpython_parity,
)


@dataclass(frozen=True)
class BranchLocalBackreferenceBytesFollowOnCase:
    id: str
    pattern: bytes
    search_matches: tuple[bytes, ...]
    fullmatch_matches: tuple[bytes, ...]
    fullmatch_misses: tuple[bytes, ...]
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


@dataclass(frozen=True)
class BranchLocalBytesFollowOnSpec:
    bundle: FixtureBundle
    cases: tuple[BranchLocalBackreferenceBytesFollowOnCase, ...]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_module_search_texts_by_pattern: dict[bytes, frozenset[bytes]]
    expected_pattern_fullmatch_texts_by_pattern: dict[bytes, frozenset[bytes]]
    expected_unsupported_backends: tuple[str, ...] = ()
    expected_unsupported_backend_reason: str | None = None


@dataclass(frozen=True)
class GeneratedQuantifiedBranchLocalParitySpec:
    bundle: FixtureBundle
    expected_compile_case_ids: tuple[str, ...]
    expected_patterns: frozenset[str | bytes]
    expected_text_models: frozenset[str]
    candidate_body_atoms: tuple[str, ...]
    candidate_suffixes: tuple[str, ...]
    candidate_lengths: range
    failure_prefix: str


HELPERS = ("search", "match", "fullmatch")
BODY_ATOMS = ("b", "c", "e")
FAILURE_PREVIEW_LIMIT = 20
STR_AND_BYTES_TEXT_MODELS = frozenset({"bytes", "str"})


FIXTURE_BUNDLES, FIXTURE_BUNDLES_BY_MANIFEST_ID = load_published_fixture_bundles(
    (
        SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR,
        BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    ),
    pattern_extractor=case_pattern,
)
(
    NAMED_BACKREFERENCE_BUNDLE,
    NUMBERED_BACKREFERENCE_BUNDLE,
    QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE,
) = requested_published_fixture_bundles(
    FIXTURE_BUNDLES_BY_MANIFEST_ID,
    (
        "named-backreference-workflows",
        "numbered-backreference-workflows",
        "quantified-alternation-branch-local-backreference-workflows",
        "quantified-nested-group-alternation-branch-local-backreference-workflows",
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows",
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows",
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows",
    ),
)
WHOLE_MANIFEST_BACKREFERENCE_BUNDLES = (
    NAMED_BACKREFERENCE_BUNDLE,
    NUMBERED_BACKREFERENCE_BUNDLE,
)
GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS = (
    GeneratedQuantifiedBranchLocalParitySpec(
        bundle=QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        expected_compile_case_ids=(
            "quantified-nested-group-alternation-branch-local-numbered-"
            "backreference-compile-metadata-str",
            "quantified-nested-group-alternation-branch-local-named-"
            "backreference-compile-metadata-str",
            "quantified-nested-group-alternation-branch-local-numbered-"
            "backreference-compile-metadata-bytes",
            "quantified-nested-group-alternation-branch-local-named-"
            "backreference-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)+)\2d",
                r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
                rb"a((b|c)+)\2d",
                rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
            }
        ),
        expected_text_models=STR_AND_BYTES_TEXT_MODELS,
        candidate_body_atoms=BODY_ATOMS,
        candidate_suffixes=("d",),
        candidate_lengths=range(5),
        failure_prefix=(
            "quantified nested-group alternation branch-local-backreference "
            "generated parity drifted"
        ),
    ),
    GeneratedQuantifiedBranchLocalParitySpec(
        bundle=(
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE
        ),
        expected_compile_case_ids=(
            "nested-broader-range-open-ended-quantified-group-alternation-"
            "branch-local-backreference-conditional-numbered-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-"
            "branch-local-backreference-conditional-named-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-"
            "branch-local-backreference-conditional-numbered-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-"
            "branch-local-backreference-conditional-named-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){2,})\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                rb"a((b|c){2,})\2(?(2)d|e)",
                rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            }
        ),
        expected_text_models=STR_AND_BYTES_TEXT_MODELS,
        candidate_body_atoms=("b", "c"),
        candidate_suffixes=("", "d", "e"),
        candidate_lengths=range(5),
        failure_prefix=(
            "broader-range open-ended conditional branch-local-backreference "
            "generated parity drifted"
        ),
    ),
)


def _build_generated_quantified_branch_local_candidate_texts(
    candidate_body_atoms: tuple[str, ...],
    candidate_suffixes: tuple[str, ...],
    candidate_lengths: range,
) -> tuple[str, ...]:
    return tuple(
        f"{prefix}a{''.join(body)}{terminal}{suffix}"
        for length in candidate_lengths
        for body in product(candidate_body_atoms, repeat=length)
        for terminal in candidate_suffixes
        for prefix, suffix in WRAPPER_PAIRS
    )


GENERATED_QUANTIFIED_BRANCH_LOCAL_COMPILE_CASES = tuple(
    case
    for spec in GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS
    for case in fixture_cases_for_operation((spec.bundle,), "compile")
)


def _generated_quantified_branch_local_spec(
    manifest_id: str,
) -> GeneratedQuantifiedBranchLocalParitySpec:
    for spec in GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS:
        if spec.bundle.expected_manifest_id == manifest_id:
            return spec
    raise AssertionError(
        f"unexpected generated branch-local manifest id {manifest_id!r}"
    )


def _generated_branch_local_candidate_texts(
    spec: GeneratedQuantifiedBranchLocalParitySpec,
    case: FixtureCase,
) -> tuple[str | bytes, ...]:
    texts = _build_generated_quantified_branch_local_candidate_texts(
        spec.candidate_body_atoms,
        spec.candidate_suffixes,
        spec.candidate_lengths,
    )
    if case.text_model == "bytes":
        return tuple(text.encode("ascii") for text in texts)
    return texts


QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES = (
    BranchLocalBackreferenceBytesFollowOnCase(
        id="quantified-alternation-branch-local-numbered-bytes",
        pattern=rb"a((b|c)\2){1,2}d",
        search_matches=(b"zzabbdzz",),
        fullmatch_matches=(b"accd", b"abbbbd"),
        fullmatch_misses=(b"abcd",),
    ),
    BranchLocalBackreferenceBytesFollowOnCase(
        id="quantified-alternation-branch-local-named-bytes",
        pattern=rb"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
        search_matches=(b"zzaccdzz",),
        fullmatch_matches=(b"accccd", b"abbccd"),
        fullmatch_misses=(b"abcd",),
    ),
)
QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES = (
    BranchLocalBackreferenceBytesFollowOnCase(
        id="quantified-nested-group-alternation-branch-local-numbered-bytes",
        pattern=rb"a((b|c)+)\2d",
        search_matches=(b"zzabbdzz",),
        fullmatch_matches=(b"accd", b"abbbd"),
        fullmatch_misses=(b"abcd",),
    ),
    BranchLocalBackreferenceBytesFollowOnCase(
        id="quantified-nested-group-alternation-branch-local-named-bytes",
        pattern=rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        search_matches=(b"zzaccdzz",),
        fullmatch_matches=(b"abbd", b"abccd"),
        fullmatch_misses=(b"acbd",),
    ),
)
NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES = (
    BranchLocalBackreferenceBytesFollowOnCase(
        id="nested-broader-range-wider-ranged-repeat-branch-local-numbered-bytes",
        pattern=rb"a((b|c){1,4})\2d",
        search_matches=(b"zzabbdzz", b"zzaccdzz"),
        fullmatch_matches=(b"abbbd", b"abcbccd"),
        fullmatch_misses=(b"abcd", b"abbbbbbd"),
    ),
    BranchLocalBackreferenceBytesFollowOnCase(
        id="nested-broader-range-wider-ranged-repeat-branch-local-named-bytes",
        pattern=rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        search_matches=(b"zzaccdzz", b"zzabbdzz"),
        fullmatch_matches=(b"abccd", b"acccccd"),
        fullmatch_misses=(b"abcbcd", b"accccccd"),
    ),
)
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES = (
    BranchLocalBackreferenceBytesFollowOnCase(
        id="nested-broader-range-open-ended-branch-local-numbered-bytes",
        pattern=rb"a((b|c){2,})\2d",
        search_matches=(b"zzabbbdzz",),
        fullmatch_matches=(b"acccd", b"abcbccd"),
        fullmatch_misses=(b"abbd",),
    ),
    BranchLocalBackreferenceBytesFollowOnCase(
        id="nested-broader-range-open-ended-branch-local-named-bytes",
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        search_matches=(b"zzacccdzz",),
        fullmatch_matches=(b"abbbd", b"abcccd"),
        fullmatch_misses=(b"accd",),
    ),
)
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BYTES_CASES = (
    BranchLocalBackreferenceBytesFollowOnCase(
        id="nested-broader-range-open-ended-branch-local-backreference-conditional-numbered-bytes",
        pattern=rb"a((b|c){2,})\2(?(2)d|e)",
        search_matches=(b"zzabbbdzz",),
        fullmatch_matches=(b"acccd", b"abcbccd"),
        fullmatch_misses=(b"abcbcc",),
    ),
    BranchLocalBackreferenceBytesFollowOnCase(
        id="nested-broader-range-open-ended-branch-local-backreference-conditional-named-bytes",
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        search_matches=(b"zzacccdzz",),
        fullmatch_matches=(b"abbbd", b"abcbccd"),
        fullmatch_misses=(b"abbd",),
    ),
)


DIRECT_BYTES_FOLLOW_ON_SPECS = (
    BranchLocalBytesFollowOnSpec(
        bundle=QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[0].pattern: frozenset(
                {b"zzabbdzz"}
            ),
            QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[1].pattern: frozenset(
                {b"zzaccdzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[0].pattern: frozenset(
                {b"accd", b"abbbbd", b"abcd"}
            ),
            QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[1].pattern: frozenset(
                {b"accccd", b"abbccd", b"abcd"}
            ),
        },
    ),
    BranchLocalBytesFollowOnSpec(
        bundle=QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        cases=QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                0
            ].pattern: frozenset({b"zzabbdzz"}),
            QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                1
            ].pattern: frozenset({b"zzaccdzz"}),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                0
            ].pattern: frozenset({b"accd", b"abbbd", b"abcd"}),
            QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                1
            ].pattern: frozenset({b"abbd", b"abccd", b"acbd"}),
        },
    ),
    BranchLocalBytesFollowOnSpec(
        bundle=NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        cases=NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
        expected_module_search_texts_by_pattern={
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                0
            ].pattern: frozenset({b"zzabbdzz", b"zzaccdzz"}),
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                1
            ].pattern: frozenset({b"zzaccdzz", b"zzabbdzz"}),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                0
            ].pattern: frozenset({b"abbbd", b"abcbccd", b"abcd", b"abbbbbbd"}),
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                1
            ].pattern: frozenset({b"abccd", b"acccccd", b"abcbcd", b"accccccd"}),
        },
    ),
    BranchLocalBytesFollowOnSpec(
        bundle=NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        cases=NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                0
            ].pattern: frozenset({b"zzabbbdzz"}),
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                1
            ].pattern: frozenset({b"zzacccdzz"}),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                0
            ].pattern: frozenset({b"acccd", b"abcbccd", b"abbd"}),
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES[
                1
            ].pattern: frozenset({b"abbbd", b"abcccd", b"accd"}),
        },
    ),
    BranchLocalBytesFollowOnSpec(
        bundle=NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE,
        cases=(
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BYTES_CASES
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BYTES_CASES[
                0
            ].pattern: frozenset({b"zzabbbdzz"}),
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BYTES_CASES[
                1
            ].pattern: frozenset({b"zzacccdzz"}),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BYTES_CASES[
                0
            ].pattern: frozenset({b"acccd", b"abcbccd", b"abcbcc"}),
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BYTES_CASES[
                1
            ].pattern: frozenset({b"abbbd", b"abcbccd", b"abbd"}),
        },
    ),
)
DIRECT_BYTES_FOLLOW_ON_CASES = tuple(
    case for spec in DIRECT_BYTES_FOLLOW_ON_SPECS for case in spec.cases
)
DIRECT_BYTES_FOLLOW_ON_PARAMS = tuple(
    pytest.param(case, id=case.id) for case in DIRECT_BYTES_FOLLOW_ON_CASES
)


def _iter_fixture_cases() -> Iterator[FixtureCase]:
    for bundle in FIXTURE_BUNDLES:
        yield from bundle.cases


def _simple_backreference_workflow_case_ids() -> tuple[str, ...]:
    return tuple(
        case.case_id
        for bundle in WHOLE_MANIFEST_BACKREFERENCE_BUNDLES
        for case in bundle.cases
        if case.operation != "compile"
    )


SUPPORTED_DIRECT_BYTES_PATTERNS = frozenset(
    case.pattern
    for case in DIRECT_BYTES_FOLLOW_ON_CASES
    if not case.unsupported_backends
)
CASES_BY_ID = fixture_cases_by_id(FIXTURE_BUNDLES)
assert len(CASES_BY_ID) == sum(len(bundle.cases) for bundle in FIXTURE_BUNDLES)
COMPILE_CASES, MODULE_CASES, PATTERN_CASES = partition_direct_bytes_follow_on_case_buckets(
    FIXTURE_BUNDLES,
    tuple(spec.bundle for spec in DIRECT_BYTES_FOLLOW_ON_SPECS),
)


def _shared_workflow_case_ids() -> frozenset[str]:
    return frozenset(case.case_id for case in (*MODULE_CASES, *PATTERN_CASES))


WORKFLOW_CASES = tuple(
    case for case in _iter_fixture_cases() if case.case_id in _shared_workflow_case_ids()
)


MATCH_CONVENIENCE_MANIFEST_IDS = frozenset(
    {
        "quantified-branch-local-backreference-workflows",
        "nested-group-alternation-branch-local-backreference-workflows",
        "quantified-alternation-branch-local-backreference-workflows",
        "quantified-nested-group-alternation-branch-local-backreference-workflows",
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows",
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows",
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows",
    }
)
MATCH_CONVENIENCE_CASE_IDS = frozenset(
    _simple_backreference_workflow_case_ids()
) | frozenset(
    case.case_id
    for case in WORKFLOW_CASES
    if case.manifest_id in MATCH_CONVENIENCE_MANIFEST_IDS and case.operation != "compile"
)


def _nested_branch_local_match_group_access_case_ids() -> tuple[str, ...]:
    bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[
        "nested-group-alternation-branch-local-backreference-workflows"
    ]
    return tuple(
        case.case_id
        for case in bundle.cases
        if case.text_model == "str"
        and case.operation != "compile"
        and "no-match" not in case.case_id
    )


def _quantified_branch_local_match_group_access_case_ids() -> tuple[str, ...]:
    return tuple(
        case.case_id
        for case in QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE.cases
        if case.text_model == "str"
        and case.operation != "compile"
        and "no-match" not in case.case_id
        and (
            case.operation == "module_call"
            or ("second-repetition" in case.case_id and "c-branch" not in case.case_id)
        )
    )


def _match_group_access_case_ids() -> tuple[str, ...]:
    return (
        *_simple_backreference_workflow_case_ids(),
        *_nested_branch_local_match_group_access_case_ids(),
        *_quantified_branch_local_match_group_access_case_ids(),
    )


SIMPLE_NAMED_PATTERN_SEARCH_CASE_ID = "named-backreference-pattern-search-str"
SIMPLE_NUMBERED_PATTERN_SEARCH_CASE_ID = "numbered-backreference-pattern-search-str"
SIMPLE_NUMBERED_SEGMENT_MODULE_SEARCH_CASE_ID = (
    "numbered-backreference-segment-module-search-str"
)
SIMPLE_NUMBERED_PREFIX_PATTERN_SEARCH_CASE_ID = (
    "numbered-backreference-prefix-pattern-search-str"
)
NESTED_GROUP_NUMBERED_COMPILE_CASE_ID = (
    "nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str"
)
BROADER_RANGE_NAMED_COMPILE_CASE_ID = (
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-"
    "named-backreference-compile-metadata-str"
)
OPEN_ENDED_NUMBERED_COMPILE_CASE_ID = (
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-"
    "backreference-compile-metadata-str"
)
OPEN_ENDED_NAMED_COMPILE_CASE_ID = (
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-"
    "backreference-compile-metadata-str"
)
PATTERN_BOUNDS_MATCH_CASES = (
    BoundedPatternCase(
        id="numbered-backreference-match-honors-narrowed-window",
        pattern_case_id=SIMPLE_NUMBERED_PATTERN_SEARCH_CASE_ID,
        helper="match",
        string="zzababzz",
        bounds=(2, 6),
    ),
    BoundedPatternCase(
        id="named-backreference-fullmatch-honors-narrowed-window",
        pattern_case_id=SIMPLE_NAMED_PATTERN_SEARCH_CASE_ID,
        helper="fullmatch",
        string="zzababzz",
        bounds=(2, 6),
    ),
    BoundedPatternCase(
        id="numbered-backreference-segment-search-honors-narrowed-window",
        pattern_case_id=SIMPLE_NUMBERED_SEGMENT_MODULE_SEARCH_CASE_ID,
        helper="search",
        string="zzabxabzz",
        bounds=(2, 7),
    ),
    BoundedPatternCase(
        id="numbered-backreference-prefix-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id=SIMPLE_NUMBERED_PREFIX_PATTERN_SEARCH_CASE_ID,
        helper="search",
        string="zzxababzz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="numbered-nested-match-window",
        pattern_case_id=NESTED_GROUP_NUMBERED_COMPILE_CASE_ID,
        helper="match",
        string="zzabbdzz",
        bounds=(2, 6),
    ),
    BoundedPatternCase(
        id="named-broader-range-search-window",
        pattern_case_id=BROADER_RANGE_NAMED_COMPILE_CASE_ID,
        helper="search",
        string="yyabcccdzz",
        bounds=(2, 8),
    ),
    BoundedPatternCase(
        id="numbered-open-ended-fullmatch-window",
        pattern_case_id=OPEN_ENDED_NUMBERED_COMPILE_CASE_ID,
        helper="fullmatch",
        string="xxabbbbdyy",
        bounds=(2, 8),
    ),
    BoundedPatternCase(
        id="named-open-ended-fullmatch-window",
        pattern_case_id=OPEN_ENDED_NAMED_COMPILE_CASE_ID,
        helper="fullmatch",
        string="yyaccccdzz",
        bounds=(2, 8),
    ),
)
PATTERN_BOUNDS_NO_MATCH_CASES = (
    BoundedPatternCase(
        id="numbered-backreference-search-skips-match-before-pos",
        pattern_case_id=SIMPLE_NUMBERED_PATTERN_SEARCH_CASE_ID,
        helper="search",
        string="zzababzz",
        bounds=(3, 8),
    ),
    BoundedPatternCase(
        id="named-backreference-fullmatch-does-not-expand-to-the-whole-string",
        pattern_case_id=SIMPLE_NAMED_PATTERN_SEARCH_CASE_ID,
        helper="fullmatch",
        string="zzababzz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="numbered-backreference-segment-search-skips-match-before-pos",
        pattern_case_id=SIMPLE_NUMBERED_SEGMENT_MODULE_SEARCH_CASE_ID,
        helper="search",
        string="zzabxabzz",
        bounds=(3, 9),
    ),
    BoundedPatternCase(
        id="numbered-backreference-prefix-search-fails-when-endpos-truncates-the-replay",
        pattern_case_id=SIMPLE_NUMBERED_PREFIX_PATTERN_SEARCH_CASE_ID,
        helper="search",
        string="zzxababzz",
        bounds=(2, 6),
    ),
    BoundedPatternCase(
        id="numbered-nested-search-skips-match-before-pos",
        pattern_case_id=NESTED_GROUP_NUMBERED_COMPILE_CASE_ID,
        helper="search",
        string="zzabbdzz",
        bounds=(3, 8),
    ),
    BoundedPatternCase(
        id="named-broader-range-match-truncated-endpos",
        pattern_case_id=BROADER_RANGE_NAMED_COMPILE_CASE_ID,
        helper="match",
        string="yyabcccdzz",
        bounds=(2, 7),
    ),
    BoundedPatternCase(
        id="numbered-open-ended-fullmatch-truncated-endpos",
        pattern_case_id=OPEN_ENDED_NUMBERED_COMPILE_CASE_ID,
        helper="fullmatch",
        string="xxabbbbdyy",
        bounds=(2, 7),
    ),
    BoundedPatternCase(
        id="named-open-ended-fullmatch-starts-inside-window",
        pattern_case_id=OPEN_ENDED_NAMED_COMPILE_CASE_ID,
        helper="fullmatch",
        string="yyaccccdzz",
        bounds=(3, 8),
    ),
)
DIRECT_BYTES_PATTERN_BOUNDS_MATCH_CASES = (
    DirectBytesBoundedPatternCase(
        id="quantified-alternation-branch-local-named-bytes-search-window",
        pattern=rb"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
        helper="search",
        string=b"yyaccdzz",
        bounds=(2, 6),
    ),
    DirectBytesBoundedPatternCase(
        id="quantified-nested-group-branch-local-numbered-bytes-match-window",
        pattern=rb"a((b|c)+)\2d",
        helper="match",
        string=b"zzabbdxx",
        bounds=(2, 6),
    ),
    DirectBytesBoundedPatternCase(
        id="quantified-nested-group-branch-local-named-bytes-fullmatch-window",
        pattern=rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        helper="fullmatch",
        string=b"yyabccdzz",
        bounds=(2, 7),
    ),
    DirectBytesBoundedPatternCase(
        id="nested-broader-range-wider-ranged-repeat-branch-local-numbered-bytes-search-window",
        pattern=rb"a((b|c){1,4})\2d",
        helper="search",
        string=b"yyabbbdzz",
        bounds=(2, 7),
    ),
    DirectBytesBoundedPatternCase(
        id="nested-broader-range-wider-ranged-repeat-branch-local-named-bytes-fullmatch-window",
        pattern=rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        helper="fullmatch",
        string=b"yyabccdzz",
        bounds=(2, 7),
    ),
    DirectBytesBoundedPatternCase(
        id="nested-broader-range-open-ended-branch-local-numbered-bytes-fullmatch-window",
        pattern=rb"a((b|c){2,})\2d",
        helper="fullmatch",
        string=b"xxabbbbdyy",
        bounds=(2, 8),
    ),
    DirectBytesBoundedPatternCase(
        id="nested-broader-range-open-ended-branch-local-named-bytes-fullmatch-window",
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="fullmatch",
        string=b"yyaccccdzz",
        bounds=(2, 8),
    ),
    DirectBytesBoundedPatternCase(
        id=(
            "nested-broader-range-open-ended-branch-local-backreference-"
            "conditional-numbered-bytes-fullmatch-window"
        ),
        pattern=rb"a((b|c){2,})\2(?(2)d|e)",
        helper="fullmatch",
        string=b"xxacccdyy",
        bounds=(2, 7),
    ),
    DirectBytesBoundedPatternCase(
        id=(
            "nested-broader-range-open-ended-branch-local-backreference-"
            "conditional-named-bytes-fullmatch-window"
        ),
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        helper="fullmatch",
        string=b"yyabbbdzz",
        bounds=(2, 7),
    ),
)
DIRECT_BYTES_PATTERN_BOUNDS_NO_MATCH_CASES = (
    DirectBytesBoundedPatternCase(
        id="quantified-alternation-branch-local-numbered-bytes-search-skips-match-before-pos",
        pattern=rb"a((b|c)\2){1,2}d",
        helper="search",
        string=b"xxabbdyy",
        bounds=(3, 8),
    ),
    DirectBytesBoundedPatternCase(
        id="quantified-nested-group-branch-local-numbered-bytes-fullmatch-truncated-endpos",
        pattern=rb"a((b|c)+)\2d",
        helper="fullmatch",
        string=b"yyabccdzz",
        bounds=(2, 6),
    ),
    DirectBytesBoundedPatternCase(
        id="nested-broader-range-open-ended-branch-local-numbered-bytes-fullmatch-truncated-endpos",
        pattern=rb"a((b|c){2,})\2d",
        helper="fullmatch",
        string=b"xxabbbbdyy",
        bounds=(2, 7),
    ),
    DirectBytesBoundedPatternCase(
        id="nested-broader-range-open-ended-branch-local-named-bytes-fullmatch-starts-inside-window",
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="fullmatch",
        string=b"yyaccccdzz",
        bounds=(3, 8),
    ),
)
SUPPLEMENTAL_MISS_CASES = (
    SupplementalMissCase(
        id="simple-named-module-search-miss-partial",
        target="module",
        pattern=r"(?P<word>ab)(?P=word)",
        helper="search",
        text="zzabzz",
    ),
    SupplementalMissCase(
        id="simple-named-module-search-miss-short",
        target="module",
        pattern=r"(?P<word>ab)(?P=word)",
        helper="search",
        text="zzz",
    ),
    SupplementalMissCase(
        id="simple-named-pattern-search-miss-partial",
        target="pattern",
        pattern=r"(?P<word>ab)(?P=word)",
        helper="search",
        text="zzabzz",
    ),
    SupplementalMissCase(
        id="simple-named-pattern-search-miss-short",
        target="pattern",
        pattern=r"(?P<word>ab)(?P=word)",
        helper="search",
        text="zzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-module-search-miss-partial",
        target="module",
        pattern=r"(ab)\1",
        helper="search",
        text="zzabzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-module-search-miss-short",
        target="module",
        pattern=r"(ab)\1",
        helper="search",
        text="zzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-pattern-search-miss-partial",
        target="pattern",
        pattern=r"(ab)\1",
        helper="search",
        text="zzabzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-pattern-search-miss-short",
        target="pattern",
        pattern=r"(ab)\1",
        helper="search",
        text="zzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-segment-module-search-miss-partial",
        target="module",
        pattern=r"(ab)x\1",
        helper="search",
        text="zzabzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-segment-module-search-miss-short",
        target="module",
        pattern=r"(ab)x\1",
        helper="search",
        text="zzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-prefix-pattern-search-miss-partial",
        target="pattern",
        pattern=r"x(ab)\1",
        helper="search",
        text="zzabzz",
    ),
    SupplementalMissCase(
        id="simple-numbered-prefix-pattern-search-miss-short",
        target="pattern",
        pattern=r"x(ab)\1",
        helper="search",
        text="zzz",
    ),
    SupplementalMissCase(
        id="module-numbered-search-miss-mismatched-replay",
        target="module",
        pattern=r"a((b)+|c)\2d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-mismatched-replay",
        target="pattern",
        pattern=r"a((b)+|c)\2d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-mismatched-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-mismatched-replay",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-numbered-search-miss-mismatched-replay-nested",
        target="module",
        pattern=r"a((b|c))\2d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-mismatched-replay-nested",
        target="pattern",
        pattern=r"a((b|c))\2d",
        helper="fullmatch",
        text="acbd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-mismatched-replay-nested",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        helper="search",
        text="zzacbdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-mismatched-replay-nested",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-numbered-search-miss-mixed-branch-repetition",
        target="module",
        pattern=r"a((b|c)\2){1,2}d",
        helper="search",
        text="zzabccdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-mixed-branch-repetition",
        target="pattern",
        pattern=r"a((b|c)\2){1,2}d",
        helper="fullmatch",
        text="abccd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-cross-branch-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
        helper="search",
        text="zzacbbdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-cross-branch-replay",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
        helper="fullmatch",
        text="acbbd",
    ),
    SupplementalMissCase(
        id="module-numbered-search-miss-mismatched-replay-quantified-nested",
        target="module",
        pattern=r"a((b|c)+)\2d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-short-replay",
        target="pattern",
        pattern=r"a((b|c)+)\2d",
        helper="fullmatch",
        text="acbd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-short-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        helper="search",
        text="zzacbdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-mismatched-replay-quantified-nested",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-broader-range-numbered-search-miss-missing-replay",
        target="module",
        pattern=r"a((b|c){1,4})\2d",
        helper="search",
        text="zzabcbcdzz",
    ),
    SupplementalMissCase(
        id="pattern-broader-range-numbered-fullmatch-miss-overflow",
        target="pattern",
        pattern=r"a((b|c){1,4})\2d",
        helper="fullmatch",
        text="abbbbbbd",
    ),
    SupplementalMissCase(
        id="module-broader-range-named-search-miss-missing-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        helper="search",
        text="zzabcbcdzz",
    ),
    SupplementalMissCase(
        id="pattern-broader-range-named-fullmatch-miss-overflow",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        helper="fullmatch",
        text="accccccd",
    ),
)
MATCH_GROUP_ACCESS_CASES = tuple(
    CASES_BY_ID[case_id] for case_id in _match_group_access_case_ids()
)


def test_match_group_access_rows_remain_on_shared_backreference_fixture_paths() -> None:
    expected_case_ids = (
        "named-backreference-module-search-str",
        "named-backreference-pattern-search-str",
        "numbered-backreference-module-search-str",
        "numbered-backreference-pattern-search-str",
        "numbered-backreference-segment-module-search-str",
        "numbered-backreference-prefix-pattern-search-str",
        "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
        "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
        "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
        "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
        "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
        "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
        "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
        "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
    )
    assert _match_group_access_case_ids() == expected_case_ids
    assert tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES) == expected_case_ids
    assert {case.text_model for case in MATCH_GROUP_ACCESS_CASES} == {"str"}


def test_pattern_bounds_cases_stay_anchored_to_supported_backreference_patterns() -> None:
    assert str_case_pattern(CASES_BY_ID[SIMPLE_NAMED_PATTERN_SEARCH_CASE_ID]) == (
        r"(?P<word>ab)(?P=word)"
    )
    assert str_case_pattern(CASES_BY_ID[SIMPLE_NUMBERED_PATTERN_SEARCH_CASE_ID]) == r"(ab)\1"
    assert str_case_pattern(CASES_BY_ID[SIMPLE_NUMBERED_SEGMENT_MODULE_SEARCH_CASE_ID]) == (
        r"(ab)x\1"
    )
    assert str_case_pattern(CASES_BY_ID[SIMPLE_NUMBERED_PREFIX_PATTERN_SEARCH_CASE_ID]) == (
        r"x(ab)\1"
    )
    assert str_case_pattern(CASES_BY_ID[NESTED_GROUP_NUMBERED_COMPILE_CASE_ID]) == r"a((b|c))\2d"
    assert str_case_pattern(CASES_BY_ID[BROADER_RANGE_NAMED_COMPILE_CASE_ID]) == (
        r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"
    )
    assert str_case_pattern(CASES_BY_ID[OPEN_ENDED_NUMBERED_COMPILE_CASE_ID]) == (
        r"a((b|c){2,})\2d"
    )
    assert str_case_pattern(CASES_BY_ID[OPEN_ENDED_NAMED_COMPILE_CASE_ID]) == (
        r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"
    )


def test_direct_bytes_pattern_bounds_cases_stay_anchored_to_supported_bytes_patterns(
) -> None:
    assert {
        case.pattern
        for case in (
            *DIRECT_BYTES_PATTERN_BOUNDS_MATCH_CASES,
            *DIRECT_BYTES_PATTERN_BOUNDS_NO_MATCH_CASES,
        )
    } == SUPPORTED_DIRECT_BYTES_PATTERNS


def test_whole_manifest_backreference_bundles_load_in_declared_order_with_bundle_validation(
) -> None:
    bundles = WHOLE_MANIFEST_BACKREFERENCE_BUNDLES

    assert tuple(bundle.manifest.path.name for bundle in bundles) == (
        tuple(
            path.name
            for path in select_correctness_fixture_paths(
                SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR
            )
        )
    )
    for bundle in bundles:
        assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_fixture_case_operation_selection_preserves_published_row_order() -> None:
    bundles = WHOLE_MANIFEST_BACKREFERENCE_BUNDLES

    assert tuple(
        case.case_id for case in fixture_cases_for_operation(bundles, "pattern_call")
    ) == (
        "named-backreference-pattern-search-str",
        "numbered-backreference-pattern-search-str",
        "numbered-backreference-prefix-pattern-search-str",
    )


@pytest.mark.parametrize("bundle", FIXTURE_BUNDLES, ids=lambda bundle: bundle.expected_manifest_id)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


@pytest.mark.parametrize(
    "spec",
    GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS,
    ids=lambda spec: spec.bundle.expected_manifest_id,
)
def test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests(
    spec: GeneratedQuantifiedBranchLocalParitySpec,
) -> None:
    compile_cases = fixture_cases_for_operation((spec.bundle,), "compile")
    candidate_texts = _build_generated_quantified_branch_local_candidate_texts(
        spec.candidate_body_atoms,
        spec.candidate_suffixes,
        spec.candidate_lengths,
    )
    expected_candidate_count = (
        len(WRAPPER_PAIRS)
        * len(spec.candidate_suffixes)
        * sum(
            len(spec.candidate_body_atoms) ** length
            for length in spec.candidate_lengths
        )
    )

    assert tuple(
        generated_spec.bundle.manifest.path
        for generated_spec in GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS
    ) == (
        (
            QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE.manifest.path
        ),
        (
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE.manifest.path
        ),
    )
    assert (
        spec.bundle.manifest.path
        == FIXTURE_BUNDLES_BY_MANIFEST_ID[spec.bundle.expected_manifest_id].manifest.path
    )
    assert tuple(case.case_id for case in compile_cases) == spec.expected_compile_case_ids
    assert {case_pattern(case) for case in compile_cases} == spec.expected_patterns
    assert {case.text_model for case in compile_cases} == spec.expected_text_models
    assert len(candidate_texts) == expected_candidate_count
    assert len(candidate_texts) == len(set(candidate_texts))


def test_branch_local_backreference_parity_suite_tracks_published_case_frontier() -> None:
    for bundle in FIXTURE_BUNDLES:
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=tuple(case.case_id for case in bundle.cases),
        )


def test_branch_local_backreference_direct_test_case_id_buckets_cover_selected_frontier(
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        direct_test_case_id_buckets_for_follow_on_bundles(
            compile_cases=COMPILE_CASES,
            module_cases=MODULE_CASES,
            pattern_cases=PATTERN_CASES,
            module_bucket_label="shared-module",
            pattern_bucket_label="shared-pattern",
            follow_on_buckets=(
                (
                    f"{spec.bundle.expected_manifest_id.removesuffix('-workflows')}-bytes-follow-on",
                    spec.bundle,
                )
                for spec in DIRECT_BYTES_FOLLOW_ON_SPECS
            ),
        ),
        selected_case_ids=ordered_fixture_bundle_case_ids(FIXTURE_BUNDLES),
        coverage_label="branch-local-backreference direct-test case-id buckets",
    )


def test_branch_local_backreference_mixed_text_model_manifests_keep_explicit_direct_bytes_follow_on_routing(
) -> None:
    mixed_manifest_ids = {
        bundle.manifest.manifest_id
        for bundle in FIXTURE_BUNDLES
        if {case.text_model for case in bundle.cases} == {"bytes", "str"}
    }
    direct_follow_on_manifest_ids = {
        spec.bundle.manifest.manifest_id for spec in DIRECT_BYTES_FOLLOW_ON_SPECS
    }

    assert direct_follow_on_manifest_ids == mixed_manifest_ids


@pytest.mark.parametrize(
    "spec",
    DIRECT_BYTES_FOLLOW_ON_SPECS,
    ids=lambda spec: spec.bundle.manifest.manifest_id,
)
def test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor(
    spec: BranchLocalBytesFollowOnSpec,
) -> None:
    direct_test_case_id_buckets = direct_test_case_id_buckets_for_follow_on_bundles(
        compile_cases=COMPILE_CASES,
        module_cases=MODULE_CASES,
        pattern_cases=PATTERN_CASES,
        module_bucket_label="shared-module",
        pattern_bucket_label="shared-pattern",
        follow_on_buckets=(
            (
                f"{follow_on_spec.bundle.expected_manifest_id.removesuffix('-workflows')}-bytes-follow-on",
                follow_on_spec.bundle,
            )
            for follow_on_spec in DIRECT_BYTES_FOLLOW_ON_SPECS
        ),
    )
    bucket_label = (
        f"{spec.bundle.expected_manifest_id.removesuffix('-workflows')}-bytes-follow-on"
    )
    bundle_str_cases, bundle_bytes_cases = assert_direct_bytes_follow_on_bundle_routing(
        spec.bundle,
        compile_cases=COMPILE_CASES,
        module_cases=MODULE_CASES,
        pattern_cases=PATTERN_CASES,
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (spec.bundle,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert direct_test_case_id_buckets[bucket_label] == frozenset(
        case.case_id for case in bundle_bytes_cases
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
        assert case.unsupported_backends == spec.expected_unsupported_backends
        assert (
            case.unsupported_backend_reason
            == spec.expected_unsupported_backend_reason
        )
        assert frozenset(case.search_matches) == spec.expected_module_search_texts_by_pattern[
            case.pattern
        ]
        assert frozenset((*case.fullmatch_matches, *case.fullmatch_misses)) == (
            spec.expected_pattern_fullmatch_texts_by_pattern[case.pattern]
        )
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
    compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(case),
        case.flags or 0,
    )


@pytest.mark.parametrize(
    "case",
    GENERATED_QUANTIFIED_BRANCH_LOCAL_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_generated_quantified_branch_local_text_matrix_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    spec = _generated_quantified_branch_local_spec(case.manifest_id)
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        case.flags or 0,
    )

    failures: list[str] = []
    for text in _generated_branch_local_candidate_texts(spec, case):
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


@pytest.mark.parametrize("case", WORKFLOW_CASES, ids=lambda case: case.case_id)
def test_published_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    if expected is None:
        return

    if case.case_id in MATCH_CONVENIENCE_CASE_IDS:
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_PARAMS)
def test_direct_bytes_follow_on_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_PARAMS)
def test_direct_bytes_follow_on_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
) -> None:
    backend_name, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_PARAMS)
def test_direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_PARAMS)
def test_direct_bytes_follow_on_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_PARAMS)
def test_direct_bytes_follow_on_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
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


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_PARAMS)
def test_direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
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


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_PARAMS)
def test_direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
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


@pytest.mark.parametrize("case", PATTERN_BOUNDS_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_helper_bounds_match_cpython(
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


@pytest.mark.parametrize("case", PATTERN_BOUNDS_NO_MATCH_CASES, ids=lambda case: case.id)
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


@pytest.mark.parametrize(
    "case",
    DIRECT_BYTES_PATTERN_BOUNDS_MATCH_CASES,
    ids=lambda case: case.id,
)
def test_direct_bytes_pattern_helper_bounds_match_cpython(
    regex_backend: tuple[str, object],
    case: DirectBytesBoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
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


@pytest.mark.parametrize(
    "case",
    DIRECT_BYTES_PATTERN_BOUNDS_NO_MATCH_CASES,
    ids=lambda case: case.id,
)
def test_direct_bytes_pattern_helper_bounds_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: DirectBytesBoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = invoke_bounded_pattern_case(observed_pattern, case)
    expected = invoke_bounded_pattern_case(expected_pattern, case)

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=lambda case: case.case_id)
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
    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_valid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=lambda case: case.case_id)
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
    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("miss_case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_supplemental_negative_paths_match_cpython(
    regex_backend: tuple[str, object],
    miss_case: SupplementalMissCase,
) -> None:
    backend_name, backend = regex_backend

    if miss_case.target == "module":
        observed = getattr(backend, miss_case.helper)(miss_case.pattern, miss_case.text)
        expected = getattr(re, miss_case.helper)(miss_case.pattern, miss_case.text)
    else:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            miss_case.pattern,
        )
        observed = getattr(observed_pattern, miss_case.helper)(miss_case.text)
        expected = getattr(expected_pattern, miss_case.helper)(miss_case.text)

    assert observed is None
    assert expected is None
