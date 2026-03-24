from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
import textwrap

import pytest

from rebar_harness.correctness import (
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
    COLLECTION_REPLACEMENT_FIXTURE_SELECTOR,
    CpythonReAdapter,
    FixtureCase,
    RebarAdapter,
    evaluate_case,
    load_fixture_manifest,
    normalize_exception,
    select_correctness_fixture_paths,
)
from tests.conftest import manifest_records_by_id
from tests.python.fixture_parity_support import (
    FixtureBundle,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    flatten_fixture_bundles,
    load_single_published_fixture_bundle,
    load_published_fixture_bundles,
    str_case_pattern,
)

@dataclass(frozen=True)
class CallableManifestSpec:
    manifest_id: str
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str | bytes]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_text_models: frozenset[str]
    expected_near_miss_patterns: frozenset[str | bytes]
    pending_rebar_case_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class CallableNearMissCase:
    id: str
    manifest_id: str
    use_compiled_pattern: bool
    pattern: str | bytes
    helper: str
    text: str | bytes
    count: int
    expected_result: str | bytes | tuple[str | bytes, int]


TextValue = str | bytes


CALLABLE_STR_ONLY_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
CALLABLE_MIXED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 4,
        ("module_call", "subn"): 4,
        ("pattern_call", "sub"): 4,
        ("pattern_call", "subn"): 4,
    }
)
STR_ONLY_TEXT_MODELS = frozenset({"str"})
MIXED_TEXT_MODELS = frozenset({"str", "bytes"})


CALLABLE_MANIFEST_SPECS = (
    CallableManifestSpec(
        manifest_id="quantified-nested-group-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-quantified-nested-group-numbered-lower-bound-str",
                "module-subn-callable-quantified-nested-group-numbered-first-match-only-str",
                "pattern-sub-callable-quantified-nested-group-numbered-repeated-outer-capture-str",
                "pattern-subn-callable-quantified-nested-group-numbered-first-match-only-str",
                "module-sub-callable-quantified-nested-group-named-lower-bound-str",
                "module-subn-callable-quantified-nested-group-named-first-match-only-str",
                "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-str",
                "pattern-subn-callable-quantified-nested-group-named-first-match-only-str",
                "module-sub-callable-quantified-nested-group-numbered-lower-bound-bytes",
                "module-subn-callable-quantified-nested-group-numbered-first-match-only-bytes",
                "pattern-sub-callable-quantified-nested-group-numbered-repeated-outer-capture-bytes",
                "pattern-subn-callable-quantified-nested-group-numbered-first-match-only-bytes",
                "module-sub-callable-quantified-nested-group-named-lower-bound-bytes",
                "module-subn-callable-quantified-nested-group-named-first-match-only-bytes",
                "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-bytes",
                "pattern-subn-callable-quantified-nested-group-named-first-match-only-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((bc)+)d",
                r"a(?P<outer>(?P<inner>bc)+)d",
                rb"a((bc)+)d",
                rb"a(?P<outer>(?P<inner>bc)+)d",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(),
    ),
    CallableManifestSpec(
        manifest_id="nested-group-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-group-numbered-str",
                "module-subn-callable-nested-group-numbered-str",
                "pattern-sub-callable-nested-group-numbered-str",
                "pattern-subn-callable-nested-group-numbered-str",
                "module-sub-callable-nested-group-named-str",
                "module-subn-callable-nested-group-named-str",
                "pattern-sub-callable-nested-group-named-str",
                "pattern-subn-callable-nested-group-named-str",
                "module-sub-callable-nested-group-numbered-bytes",
                "module-subn-callable-nested-group-numbered-bytes",
                "pattern-sub-callable-nested-group-numbered-bytes",
                "pattern-subn-callable-nested-group-numbered-bytes",
                "module-sub-callable-nested-group-named-bytes",
                "module-subn-callable-nested-group-named-bytes",
                "pattern-sub-callable-nested-group-named-bytes",
                "pattern-subn-callable-nested-group-named-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b))d",
                r"a(?P<outer>(?P<inner>b))d",
                rb"a((b))d",
                rb"a(?P<outer>(?P<inner>b))d",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(),
    ),
    CallableManifestSpec(
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-quantified-nested-group-alternation-numbered-lower-bound-b-branch-str",
                "module-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-c-branch-str",
                "pattern-sub-callable-quantified-nested-group-alternation-numbered-mixed-branches-str",
                "pattern-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-b-branch-str",
                "module-sub-callable-quantified-nested-group-alternation-named-lower-bound-c-branch-str",
                "module-subn-callable-quantified-nested-group-alternation-named-first-match-only-b-branch-str",
                "pattern-sub-callable-quantified-nested-group-alternation-named-mixed-branches-str",
                "pattern-subn-callable-quantified-nested-group-alternation-named-first-match-only-c-branch-str",
                "module-sub-callable-quantified-nested-group-alternation-numbered-lower-bound-b-branch-bytes",
                "module-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-c-branch-bytes",
                "pattern-sub-callable-quantified-nested-group-alternation-numbered-mixed-branches-bytes",
                "pattern-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-b-branch-bytes",
                "module-sub-callable-quantified-nested-group-alternation-named-mixed-branches-bytes",
                "module-subn-callable-quantified-nested-group-alternation-named-first-match-only-b-branch-bytes",
                "pattern-sub-callable-quantified-nested-group-alternation-named-mixed-branches-bytes",
                "pattern-subn-callable-quantified-nested-group-alternation-named-first-match-only-c-branch-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c)+)d",
                r"a(?P<outer>(?P<inner>b|c)+)d",
                rb"a((b|c)+)d",
                rb"a(?P<outer>(?P<inner>b|c)+)d",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(
            {
                r"a((b|c)+)d",
                r"a(?P<outer>(?P<inner>b|c)+)d",
            }
        ),
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-"
            "alternation-backtracking-heavy-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-str",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-str",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-upper-bound-b-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-str",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-str",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-bytes",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-bytes",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-bytes",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-upper-bound-b-branch-first-match-only-bytes",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-mixed-branches-bytes",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-bytes",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-bytes",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(((bc|b)c){1,4})d",
                r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
                rb"a(((bc|b)c){1,4})d",
                rb"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(),
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-"
            "backtracking-heavy-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-fourth-repetition-b-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-bytes",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-bytes",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-bytes",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-fourth-repetition-b-branch-first-match-only-bytes",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-mixed-branches-bytes",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-bytes",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-bytes",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(((bc|b)c){2,})d",
                r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
                rb"a(((bc|b)c){2,})d",
                rb"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(),
    ),
    CallableManifestSpec(
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-conditional-group-exists-present-str",
                "module-subn-callable-conditional-group-exists-absent-str",
                "pattern-sub-callable-conditional-group-exists-present-str",
                "pattern-subn-callable-conditional-group-exists-absent-str",
                "module-sub-callable-named-conditional-group-exists-present-str",
                "module-subn-callable-named-conditional-group-exists-absent-str",
                "pattern-sub-callable-named-conditional-group-exists-present-str",
                "pattern-subn-callable-named-conditional-group-exists-absent-str",
                "module-sub-callable-conditional-group-exists-alternation-present-first-arm-str",
                "module-subn-callable-conditional-group-exists-alternation-present-second-arm-str",
                "pattern-sub-callable-conditional-group-exists-alternation-absent-first-arm-str",
                "pattern-subn-callable-conditional-group-exists-alternation-absent-second-arm-str",
                "module-sub-callable-named-conditional-group-exists-alternation-present-first-arm-str",
                "module-subn-callable-named-conditional-group-exists-alternation-present-second-arm-str",
                "pattern-sub-callable-named-conditional-group-exists-alternation-absent-first-arm-str",
                "pattern-subn-callable-named-conditional-group-exists-alternation-absent-second-arm-str",
                "module-sub-callable-conditional-group-exists-negative-count-str",
                "module-subn-callable-named-conditional-group-exists-negative-count-str",
                "pattern-sub-callable-conditional-group-exists-negative-count-str",
                "pattern-subn-callable-named-conditional-group-exists-negative-count-str",
                "module-sub-callable-conditional-group-exists-present-bytes",
                "module-subn-callable-conditional-group-exists-absent-bytes",
                "pattern-sub-callable-conditional-group-exists-present-bytes",
                "pattern-subn-callable-conditional-group-exists-absent-bytes",
                "module-sub-callable-named-conditional-group-exists-present-bytes",
                "module-subn-callable-named-conditional-group-exists-absent-bytes",
                "pattern-sub-callable-named-conditional-group-exists-present-bytes",
                "pattern-subn-callable-named-conditional-group-exists-absent-bytes",
                "module-sub-callable-conditional-group-exists-alternation-present-first-arm-bytes",
                "module-subn-callable-conditional-group-exists-alternation-present-second-arm-bytes",
                "pattern-sub-callable-conditional-group-exists-alternation-absent-first-arm-bytes",
                "pattern-subn-callable-conditional-group-exists-alternation-absent-second-arm-bytes",
                "module-sub-callable-named-conditional-group-exists-alternation-present-first-arm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-present-second-arm-bytes",
                "pattern-sub-callable-named-conditional-group-exists-alternation-absent-first-arm-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-absent-second-arm-bytes",
                "module-sub-callable-conditional-group-exists-negative-count-bytes",
                "module-subn-callable-named-conditional-group-exists-negative-count-bytes",
                "pattern-sub-callable-conditional-group-exists-negative-count-bytes",
                "pattern-subn-callable-named-conditional-group-exists-negative-count-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e)",
                r"a(b)?c(?(1)(de|df)|(eg|eh))",
                r"a(?P<word>b)?c(?(word)d|e)",
                r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
                rb"a(b)?c(?(1)d|e)",
                rb"a(b)?c(?(1)(de|df)|(eg|eh))",
                rb"a(?P<word>b)?c(?(word)d|e)",
                rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "sub"): 10,
                ("module_call", "subn"): 10,
                ("pattern_call", "sub"): 10,
                ("pattern_call", "subn"): 10,
            }
        ),
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e)",
                r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
            "branch-local-backreference-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-bytes",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-bytes",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c){1,4})\2d",
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
                rb"a((b|c){1,4})\2d",
                rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(),
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
            "branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-upper-bound-c-branch-str",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-bytes",
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-upper-bound-c-branch-bytes",
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c){1,4})\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
                rb"a((b|c){1,4})\2(?(2)d|e)",
                rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(),
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-bytes",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-bytes",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c){2,})\2d",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
                rb"a((b|c){2,})\2d",
                rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(
            {
                r"a((b|c){2,})\2d",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
                rb"a((b|c){2,})\2d",
                rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
            }
        ),
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-bytes",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-bytes",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-bytes",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c){2,})\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                rb"a((b|c){2,})\2(?(2)d|e)",
                rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            }
        ),
        expected_operation_helper_counts=CALLABLE_MIXED_OPERATION_HELPER_COUNTS,
        expected_text_models=MIXED_TEXT_MODELS,
        expected_near_miss_patterns=frozenset(
            {
                rb"a((b|c){2,})\2(?(2)d|e)",
                rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            }
        ),
    ),
)
CALLABLE_MANIFEST_SPECS_BY_ID = manifest_records_by_id(CALLABLE_MANIFEST_SPECS)
CALLABLE_NEAR_MISS_CASE_SPECS = (
    CallableNearMissCase(
        id="module-numbered-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-numbered-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="pattern-numbered-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="module-named-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="module-named-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="module-numbered-sub-no-match-too-short",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a((b|c)+)d",
        helper="sub",
        text="zzadzz",
        count=0,
        expected_result="zzadzz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-invalid-branch",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a((b|c)+)d",
        helper="subn",
        text="zzabedzz",
        count=0,
        expected_result=("zzabedzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-too-short",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c)+)d",
        helper="sub",
        text="zzadzz",
        count=0,
        expected_result="zzadzz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-invalid-branch",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c)+)d",
        helper="subn",
        text="zzabedzz",
        count=0,
        expected_result=("zzabedzz", 0),
    ),
    CallableNearMissCase(
        id="module-numbered-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a((b|c){2,})\2d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a((b|c){2,})\2d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-numbered-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a((b|c){2,})\2d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="pattern-numbered-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a((b|c){2,})\2d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="module-named-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="module-named-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="module-numbered-sub-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a((b|c){2,})\2d",
        helper="sub",
        text=b"zzabbdzz",
        count=0,
        expected_result=b"zzabbdzz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a((b|c){2,})\2d",
        helper="subn",
        text=b"zzabbdzz",
        count=1,
        expected_result=(b"zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-numbered-sub-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a((b|c){2,})\2d",
        helper="sub",
        text=b"zzabbdzz",
        count=0,
        expected_result=b"zzabbdzz",
    ),
    CallableNearMissCase(
        id="pattern-numbered-subn-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a((b|c){2,})\2d",
        helper="subn",
        text=b"zzabbdzz",
        count=1,
        expected_result=(b"zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="module-named-sub-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="sub",
        text=b"zzabbdzz",
        count=0,
        expected_result=b"zzabbdzz",
    ),
    CallableNearMissCase(
        id="module-named-subn-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="subn",
        text=b"zzabbdzz",
        count=1,
        expected_result=(b"zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="sub",
        text=b"zzabbdzz",
        count=0,
        expected_result=b"zzabbdzz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-missing-replay-broader-range-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="subn",
        text=b"zzabbdzz",
        count=1,
        expected_result=(b"zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="module-numbered-sub-no-match-missing-conditional-d-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a((b|c){2,})\2(?(2)d|e)",
        helper="sub",
        text=b"zzabcbcczz",
        count=0,
        expected_result=b"zzabcbcczz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-missing-conditional-d-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a((b|c){2,})\2(?(2)d|e)",
        helper="subn",
        text=b"zzabcbcczz",
        count=1,
        expected_result=(b"zzabcbcczz", 0),
    ),
    CallableNearMissCase(
        id="pattern-numbered-sub-no-match-missing-conditional-d-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a((b|c){2,})\2(?(2)d|e)",
        helper="sub",
        text=b"zzabcbcczz",
        count=0,
        expected_result=b"zzabcbcczz",
    ),
    CallableNearMissCase(
        id="pattern-numbered-subn-no-match-missing-conditional-d-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a((b|c){2,})\2(?(2)d|e)",
        helper="subn",
        text=b"zzabcbcczz",
        count=1,
        expected_result=(b"zzabcbcczz", 0),
    ),
    CallableNearMissCase(
        id="module-named-sub-no-match-below-lower-bound-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        helper="sub",
        text=b"zzabbdzz",
        count=0,
        expected_result=b"zzabbdzz",
    ),
    CallableNearMissCase(
        id="module-named-subn-no-match-below-lower-bound-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        helper="subn",
        text=b"zzabbdzz",
        count=1,
        expected_result=(b"zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-below-lower-bound-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        helper="sub",
        text=b"zzabbdzz",
        count=0,
        expected_result=b"zzabbdzz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-below-lower-bound-bytes",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        helper="subn",
        text=b"zzabbdzz",
        count=1,
        expected_result=(b"zzabbdzz", 0),
    ),
)

CONDITIONAL_GROUP_EXISTS_BYTES_NEAR_MISS_CASES = (
    CallableNearMissCase(
        id="module-numbered-sub-no-match-present-branch-rejects-no-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=rb"a(b)?c(?(1)d|e)",
        helper="sub",
        text=b"zzabcezz",
        count=0,
        expected_result=b"zzabcezz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-absent-branch-rejects-yes-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=rb"a(b)?c(?(1)d|e)",
        helper="subn",
        text=b"zzacdzz",
        count=1,
        expected_result=(b"zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-numbered-sub-no-match-present-branch-rejects-no-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=rb"a(b)?c(?(1)d|e)",
        helper="sub",
        text=b"zzabcezz",
        count=0,
        expected_result=b"zzabcezz",
    ),
    CallableNearMissCase(
        id="pattern-numbered-subn-no-match-absent-branch-rejects-yes-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=rb"a(b)?c(?(1)d|e)",
        helper="subn",
        text=b"zzacdzz",
        count=1,
        expected_result=(b"zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="module-named-sub-no-match-present-branch-rejects-no-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=rb"a(?P<word>b)?c(?(word)d|e)",
        helper="sub",
        text=b"zzabcezz",
        count=0,
        expected_result=b"zzabcezz",
    ),
    CallableNearMissCase(
        id="module-named-subn-no-match-absent-branch-rejects-yes-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=rb"a(?P<word>b)?c(?(word)d|e)",
        helper="subn",
        text=b"zzacdzz",
        count=1,
        expected_result=(b"zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-present-branch-rejects-no-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=rb"a(?P<word>b)?c(?(word)d|e)",
        helper="sub",
        text=b"zzabcezz",
        count=0,
        expected_result=b"zzabcezz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-absent-branch-rejects-yes-arm-bytes",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=rb"a(?P<word>b)?c(?(word)d|e)",
        helper="subn",
        text=b"zzacdzz",
        count=1,
        expected_result=(b"zzacdzz", 0),
    ),
)


class CallbackExplosion(RuntimeError):
    pass


def _assert_callback_match_sequence_parity(
    *,
    backend_name: str,
    observed_matches: list[object],
    expected_matches: list[re.Match[str] | re.Match[bytes]],
) -> None:
    assert len(observed_matches) == len(expected_matches)

    for observed, expected in zip(observed_matches, expected_matches, strict=True):
        assert_match_parity(
            backend_name,
            observed,
            expected,
            check_regs=True,
        )
        assert_match_convenience_api_parity(observed, expected)
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)


def _callable_replacement_marker(value: TextValue) -> TextValue:
    if isinstance(value, bytes):
        return b"X"
    return "X"


def assert_callable_replacement_match_parity(
    *,
    backend_name: str,
    backend: object,
    helper: str,
    pattern: TextValue,
    string: TextValue,
    count: int,
    group_names: tuple[str, ...] = (),
    use_compiled_pattern: bool = False,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str] | re.Match[bytes]] = []
    replacement_value = _callable_replacement_marker(string)

    def observed_replacement(match: object) -> TextValue:
        observed_matches.append(match)
        return replacement_value

    def expected_replacement(match: re.Match[str] | re.Match[bytes]) -> TextValue:
        expected_matches.append(match)
        return replacement_value

    if use_compiled_pattern:
        observed_target = backend.compile(pattern)
        expected_target = re.compile(pattern)
        observed = getattr(observed_target, helper)(
            observed_replacement,
            string,
            count=count,
        )
        expected = getattr(expected_target, helper)(
            expected_replacement,
            string,
            count=count,
        )
    else:
        observed = getattr(backend, helper)(
            pattern,
            observed_replacement,
            string,
            count=count,
        )
        expected = getattr(re, helper)(
            pattern,
            expected_replacement,
            string,
            count=count,
        )

    assert observed == expected
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )


def assert_callable_replacement_exception_parity(
    *,
    backend_name: str,
    backend: object,
    helper: str,
    pattern: TextValue,
    string: TextValue,
    count: int,
    group_names: tuple[str, ...] = (),
    use_compiled_pattern: bool = False,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str] | re.Match[bytes]] = []
    marker_message = "callable replacement callback exploded"
    observed_marker = CallbackExplosion(marker_message)
    expected_marker = CallbackExplosion(marker_message)

    def observed_replacement(match: object) -> TextValue:
        observed_matches.append(match)
        raise observed_marker

    def expected_replacement(
        match: re.Match[str] | re.Match[bytes],
    ) -> TextValue:
        expected_matches.append(match)
        raise expected_marker

    with pytest.raises(CallbackExplosion) as observed_error:
        if use_compiled_pattern:
            observed_target = backend.compile(pattern)
            getattr(observed_target, helper)(
                observed_replacement,
                string,
                count=count,
            )
        else:
            getattr(backend, helper)(
                pattern,
                observed_replacement,
                string,
                count=count,
            )

    with pytest.raises(CallbackExplosion) as expected_error:
        if use_compiled_pattern:
            expected_target = re.compile(pattern)
            getattr(expected_target, helper)(
                expected_replacement,
                string,
                count=count,
            )
        else:
            getattr(re, helper)(
                pattern,
                expected_replacement,
                string,
                count=count,
            )

    assert observed_error.value is observed_marker
    assert expected_error.value is expected_marker
    assert observed_error.value.args == expected_error.value.args == (marker_message,)
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


def assert_callable_replacement_return_type_error_parity(
    *,
    backend_name: str,
    backend: object,
    helper: str,
    pattern: TextValue,
    string: TextValue,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str] | re.Match[bytes]] = []
    wrong_type_replacement = "X" if isinstance(string, bytes) else b"X"

    def observed_replacement(match: object) -> str | bytes:
        observed_matches.append(match)
        return wrong_type_replacement

    def expected_replacement(match: re.Match[str] | re.Match[bytes]) -> str | bytes:
        expected_matches.append(match)
        return wrong_type_replacement

    with pytest.raises(TypeError) as expected_error:
        if use_compiled_pattern:
            expected_target = re.compile(pattern)
            getattr(expected_target, helper)(
                expected_replacement,
                string,
                count=count,
            )
        else:
            getattr(re, helper)(
                pattern,
                expected_replacement,
                string,
                count=count,
            )

    with pytest.raises(TypeError) as observed_error:
        if use_compiled_pattern:
            observed_target = backend.compile(pattern)
            getattr(observed_target, helper)(
                observed_replacement,
                string,
                count=count,
            )
        else:
            getattr(backend, helper)(
                pattern,
                observed_replacement,
                string,
                count=count,
            )

    assert type(observed_error.value) is type(expected_error.value)
    assert observed_error.value.args == expected_error.value.args
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )


LITERAL_CALLABLE_PARITY_VARIANTS = (
    pytest.param("sub", 0, False, id="literal-module-sub-replace-all"),
    pytest.param("subn", 1, False, id="literal-module-subn-first-match-only"),
    pytest.param("sub", 0, True, id="literal-pattern-sub-replace-all"),
    pytest.param("subn", 1, True, id="literal-pattern-subn-first-match-only"),
)
CALLABLE_NO_MATCH_VARIANTS = (
    pytest.param("sub", False, id="module-sub"),
    pytest.param("subn", False, id="module-subn"),
    pytest.param("sub", True, id="pattern-sub"),
    pytest.param("subn", True, id="pattern-subn"),
)
PENDING_REBAR_MANIFEST_IDS = frozenset(
    spec.manifest_id
    for spec in CALLABLE_MANIFEST_SPECS
    if spec.pending_rebar_case_ids
)
PENDING_REBAR_CASE_IDS = frozenset(
    case_id
    for spec in CALLABLE_MANIFEST_SPECS
    for case_id in spec.pending_rebar_case_ids
)
NO_MATCH_TEXT_CANDIDATES = ("zzz", "", "no-match", "----", "999")


def _is_pending_rebar_callable_case(case: FixtureCase) -> bool:
    return case.case_id in PENDING_REBAR_CASE_IDS


def _skip_pending_rebar_callable_parity(
    backend_name: str,
    case: FixtureCase,
) -> None:
    if (
        backend_name == "rebar"
        and _is_pending_rebar_callable_case(case)
    ):
        pytest.skip(
            f"callable replacement parity for {case.case_id} remains queued behind a later Rust-backed parity task"
        )


def _bytes_case_pattern(case: FixtureCase) -> bytes:
    pattern = case_pattern(case)
    assert isinstance(pattern, bytes)
    return pattern


def _pending_rebar_str_patterns() -> frozenset[str]:
    return frozenset(
        str_case_pattern(case)
        for case in PUBLISHED_CALLABLE_CASES
        if _is_pending_rebar_callable_case(case) and case.text_model == "str"
    )


def _pending_rebar_bytes_patterns() -> frozenset[bytes]:
    return frozenset(
        _bytes_case_pattern(case)
        for case in PUBLISHED_CALLABLE_CASES
        if _is_pending_rebar_callable_case(case) and case.text_model == "bytes"
    )

COLLECTION_REPLACEMENT_LITERAL_CALLABLE_CASE_ID = "module-sub-callable-str"
COLLECTION_REPLACEMENT_OWNER_BUNDLE = load_single_published_fixture_bundle(
    COLLECTION_REPLACEMENT_FIXTURE_SELECTOR
)
FIXTURE_BUNDLES, FIXTURE_BUNDLES_BY_MANIFEST_ID = load_published_fixture_bundles(
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR
)
PUBLISHED_CALLABLE_CASES = flatten_fixture_bundles(FIXTURE_BUNDLES)
SHARED_CALLABLE_CASES = tuple(
    case for case in PUBLISHED_CALLABLE_CASES if not _is_pending_rebar_callable_case(case)
)

COMPILE_PATTERNS = tuple(
    sorted(
        {
            str_case_pattern(case)
            for case in SHARED_CALLABLE_CASES
            if case.text_model == "str"
        }
    )
)
BYTES_NO_MATCH_PATTERNS = tuple(
    sorted(
        {
            _bytes_case_pattern(case)
            for case in SHARED_CALLABLE_CASES
            if case.text_model == "bytes"
        }
    )
)
MODULE_CASES = tuple(
    case for case in SHARED_CALLABLE_CASES if case.operation == "module_call"
)
PATTERN_CASES = tuple(
    case for case in SHARED_CALLABLE_CASES if case.operation == "pattern_call"
)
BYTES_MODULE_CASES = tuple(
    case
    for case in PUBLISHED_CALLABLE_CASES
    if case.operation == "module_call" and case.text_model == "bytes"
)
BYTES_PATTERN_CASES = tuple(
    case
    for case in PUBLISHED_CALLABLE_CASES
    if case.operation == "pattern_call" and case.text_model == "bytes"
)
PENDING_REBAR_MODULE_CASES = tuple(
    case for case in BYTES_MODULE_CASES if _is_pending_rebar_callable_case(case)
)
PENDING_REBAR_PATTERN_CASES = tuple(
    case for case in BYTES_PATTERN_CASES if _is_pending_rebar_callable_case(case)
)
CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS = (
    "quantified",
    "broader-range",
    "open-ended",
)


def _manifest_matches_return_type_error_frontier(manifest_id: str) -> bool:
    return any(
        keyword in manifest_id
        for keyword in CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS
    )


def _callable_return_type_error_expected_manifest_ids() -> frozenset[str]:
    spec_manifest_ids = frozenset(
        spec.manifest_id
        for spec in CALLABLE_MANIFEST_SPECS
        if _manifest_matches_return_type_error_frontier(spec.manifest_id)
    )
    default_manifest_ids = frozenset(
        bundle.manifest.manifest_id
        for bundle in FIXTURE_BUNDLES
        if bundle.manifest.manifest_id not in CALLABLE_MANIFEST_SPECS_BY_ID
        and _manifest_matches_return_type_error_frontier(
            bundle.manifest.manifest_id
        )
    )
    return spec_manifest_ids | default_manifest_ids


MODULE_RETURN_TYPE_ERROR_CASES = tuple(
    case
    for case in MODULE_CASES
    if _manifest_matches_return_type_error_frontier(case.manifest_id)
)
PATTERN_RETURN_TYPE_ERROR_CASES = tuple(
    case
    for case in PATTERN_CASES
    if _manifest_matches_return_type_error_frontier(case.manifest_id)
)


def _literal_callable_case() -> FixtureCase:
    matches = tuple(
        case
        for case in COLLECTION_REPLACEMENT_OWNER_BUNDLE.cases
        if case.case_id == COLLECTION_REPLACEMENT_LITERAL_CALLABLE_CASE_ID
    )
    if len(matches) != 1:
        raise AssertionError(
            "collection replacement owner bundle drifted from the literal callable "
            f"case {COLLECTION_REPLACEMENT_LITERAL_CALLABLE_CASE_ID!r}: {matches!r}"
        )
    return matches[0]


def _source_callable_replacement(case: FixtureCase) -> dict[str, object]:
    replacement_index = 1 if case.operation == "module_call" else 0
    replacement = case.source_args[replacement_index]
    assert isinstance(replacement, dict)
    return replacement


def _literal_callable_pattern() -> str:
    pattern = _literal_callable_case().args[0]
    assert isinstance(pattern, str)
    return pattern


def _literal_callable_string() -> str:
    string = _literal_callable_case().args[2]
    assert isinstance(string, str)
    return string


def _case_string(case: FixtureCase) -> TextValue:
    string = case_text_argument(case)
    assert isinstance(string, (str, bytes))
    return string


def _case_count(case: FixtureCase) -> int:
    if "count" in case.kwargs:
        return int(case.kwargs["count"])

    count_index = 3 if case.operation == "module_call" else 2
    if len(case.args) > count_index:
        return int(case.args[count_index])
    return 0


def _is_negative_count_callable_case(case: FixtureCase) -> bool:
    return _case_count(case) < 0


MODULE_CALLBACK_EXCEPTION_CASES = tuple(
    case for case in MODULE_CASES if not _is_negative_count_callable_case(case)
)
PATTERN_CALLBACK_EXCEPTION_CASES = tuple(
    case for case in PATTERN_CASES if not _is_negative_count_callable_case(case)
)
BYTES_MODULE_CALLBACK_EXCEPTION_CASES = tuple(
    case
    for case in BYTES_MODULE_CASES
    if not _is_negative_count_callable_case(case)
)
BYTES_PATTERN_CALLBACK_EXCEPTION_CASES = tuple(
    case
    for case in BYTES_PATTERN_CASES
    if not _is_negative_count_callable_case(case)
)


def _case_group_names(case: FixtureCase) -> tuple[str, ...]:
    return tuple(re.compile(case_pattern(case), case.flags or 0).groupindex)


def _invoke_callable_replacement(
    backend: object,
    *,
    pattern: TextValue,
    helper: str,
    string: TextValue,
    count: int,
    replacement: object,
    use_compiled_pattern: bool,
) -> object:
    if use_compiled_pattern:
        target = backend.compile(pattern)
        return getattr(target, helper)(replacement, string, count=count)

    return getattr(backend, helper)(pattern, replacement, string, count=count)


def _invoke_published_callable_case(backend: object, case: FixtureCase) -> object:
    if case.helper is None:
        raise ValueError(f"case {case.case_id!r} requires a helper name")

    if case.operation == "module_call":
        return getattr(backend, case.helper)(*case.args, **case.kwargs)

    if case.operation == "pattern_call":
        compiled = backend.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise ValueError(f"unsupported callable replacement operation {case.operation!r}")


def _observe_published_callable_case(backend: object, case: FixtureCase) -> tuple[str, object]:
    try:
        return ("result", _invoke_published_callable_case(backend, case))
    except Exception as exc:
        return ("exception", normalize_exception(exc))


def _near_miss_patterns_for_manifest(
    manifest_id: str,
) -> frozenset[str | bytes]:
    return frozenset(
        near_miss_case.pattern
        for near_miss_case in CALLABLE_NEAR_MISS_CASE_SPECS
        if near_miss_case.manifest_id == manifest_id
    )


def _bytes_mirror_expected_result(expected_result: object) -> object:
    if isinstance(expected_result, str):
        return expected_result.encode("latin-1")
    assert isinstance(expected_result, tuple)
    text, count = expected_result
    assert isinstance(text, str)
    assert isinstance(count, int)
    return (text.encode("latin-1"), count)


def _assert_bytes_direct_case_table_mirrors_str_table(
    *,
    str_cases: tuple[tuple[str, int | str, str, str, int], ...],
    bytes_cases: tuple[tuple[bytes, int | str, str, bytes, int], ...],
) -> None:
    assert len(str_cases) == len(bytes_cases)

    for str_case, bytes_case in zip(str_cases, bytes_cases):
        str_pattern, str_group_ref, str_helper, str_text, str_count = str_case
        bytes_pattern, bytes_group_ref, bytes_helper, bytes_text, bytes_count = (
            bytes_case
        )

        assert bytes_pattern == str_pattern.encode("latin-1")
        assert bytes_group_ref == str_group_ref
        assert bytes_helper == str_helper
        assert bytes_text == str_text.encode("latin-1")
        assert bytes_count == str_count


def _normalize_source_text_fragment(fragment: object) -> str:
    if isinstance(fragment, str):
        return fragment

    assert isinstance(fragment, dict)
    assert fragment.get("type") == "bytes"
    assert fragment.get("encoding", "latin-1") == "latin-1"
    value = fragment.get("value")
    assert isinstance(value, str)
    return value


def _normalized_source_callable_replacement(case: FixtureCase) -> dict[str, object]:
    replacement = _source_callable_replacement(case)
    return {
        "type": replacement.get("type"),
        "group": replacement.get("group"),
        "prefix": _normalize_source_text_fragment(replacement.get("prefix", "")),
        "suffix": _normalize_source_text_fragment(replacement.get("suffix", "")),
    }


def _assert_published_callable_bytes_cases_mirror_str_cases(
    *,
    manifest_id: str,
    str_cases: tuple[FixtureCase, ...],
    bytes_cases: tuple[FixtureCase, ...],
) -> None:
    bytes_cases_by_id = {case.case_id: case for case in bytes_cases}

    assert set(bytes_cases_by_id) == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in str_cases
    }

    for str_case in str_cases:
        bytes_case = bytes_cases_by_id[f"{str_case.case_id.removesuffix('-str')}-bytes"]
        str_pattern = case_pattern(str_case)
        str_text = case_text_argument(str_case)

        assert isinstance(str_pattern, str)
        assert isinstance(str_text, str)
        assert str_case.manifest_id == manifest_id
        assert bytes_case.manifest_id == manifest_id
        assert bytes_case.operation == str_case.operation
        assert bytes_case.helper == str_case.helper
        assert bytes_case.family == str_case.family
        assert bytes_case.use_compiled_pattern == str_case.use_compiled_pattern
        assert _case_count(bytes_case) == _case_count(str_case)
        assert tuple(
            "bytes" if category == "str" else category
            for category in str_case.categories
        ) == tuple(bytes_case.categories)
        assert _bytes_case_pattern(bytes_case) == str_pattern.encode("latin-1")
        assert case_text_argument(bytes_case) == str_text.encode("latin-1")
        assert _normalized_source_callable_replacement(bytes_case) == (
            _normalized_source_callable_replacement(str_case)
        )


CONDITIONAL_GROUP_EXISTS_ALTERNATION_GROUP_ACCESS_CASES = (
    (r"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "sub", "zzabcdezz", 0),
    (r"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "subn", "zzabcdfzz", 1),
    (
        r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "sub",
        "zzabcdezz",
        0,
    ),
    (
        r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "subn",
        "zzabcdfzz",
        1,
    ),
)


CONDITIONAL_GROUP_EXISTS_ALTERNATION_ABSENT_EXCEPTION_CASES = (
    (r"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "sub", "zzacegzz", 0),
    (r"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "subn", "zzacehzz", 1),
    (
        r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "sub",
        "zzacegzz",
        0,
    ),
    (
        r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "subn",
        "zzacehzz",
        1,
    ),
)


CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_GROUP_ACCESS_CASES = (
    (rb"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "sub", b"zzabcdezz", 0),
    (rb"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "subn", b"zzabcdfzz", 1),
    (
        rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "sub",
        b"zzabcdezz",
        0,
    ),
    (
        rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "subn",
        b"zzabcdfzz",
        1,
    ),
)


CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_ABSENT_EXCEPTION_CASES = (
    (rb"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "sub", b"zzacegzz", 0),
    (rb"a(b)?c(?(1)(de|df)|(eg|eh))", 1, "subn", b"zzacehzz", 1),
    (
        rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "sub",
        b"zzacegzz",
        0,
    ),
    (
        rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        "word",
        "subn",
        b"zzacehzz",
        1,
    ),
)


def _callable_no_match_text(pattern: TextValue, flags: int = 0) -> TextValue:
    compiled = re.compile(pattern, flags)
    for text in NO_MATCH_TEXT_CANDIDATES:
        candidate = text if isinstance(pattern, str) else text.encode()
        if compiled.search(candidate) is None:
            return candidate

    raise AssertionError(f"could not find a shared no-match text for pattern {pattern!r}")


def assert_callable_replacement_no_match_path_leaves_input_unchanged(
    *,
    backend: object,
    pattern: TextValue,
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    callback_calls: list[object] = []
    string = _callable_no_match_text(pattern)
    replacement_value = _callable_replacement_marker(string)

    def replacement(match: object) -> TextValue:
        callback_calls.append(match)
        return replacement_value

    observed = _invoke_callable_replacement(
        backend,
        pattern=pattern,
        helper=helper,
        string=string,
        count=1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=pattern,
        helper=helper,
        string=string,
        count=1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected_result: object = string if helper == "sub" else (string, 0)

    assert observed == expected == expected_result
    assert callback_calls == []


def assert_callable_replacement_near_miss_path_leaves_input_unchanged(
    *,
    backend: object,
    near_miss_case: CallableNearMissCase,
) -> None:
    callback_calls: list[object] = []
    replacement_value = _callable_replacement_marker(near_miss_case.text)

    def replacement(match: object) -> TextValue:
        callback_calls.append(match)
        return replacement_value

    observed = _invoke_callable_replacement(
        backend,
        pattern=near_miss_case.pattern,
        helper=near_miss_case.helper,
        string=near_miss_case.text,
        count=near_miss_case.count,
        replacement=replacement,
        use_compiled_pattern=near_miss_case.use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=near_miss_case.pattern,
        helper=near_miss_case.helper,
        string=near_miss_case.text,
        count=near_miss_case.count,
        replacement=replacement,
        use_compiled_pattern=near_miss_case.use_compiled_pattern,
    )

    assert observed == expected == near_miss_case.expected_result
    assert callback_calls == []


def assert_callable_replacement_negative_count_short_circuits(
    *,
    backend: object,
    helper: str,
    pattern: TextValue,
    string: TextValue,
    use_compiled_pattern: bool = False,
) -> None:
    callback_calls: list[object] = []
    replacement_value = _callable_replacement_marker(string)

    def replacement(match: object) -> TextValue:
        callback_calls.append(match)
        return replacement_value

    observed = _invoke_callable_replacement(
        backend,
        pattern=pattern,
        helper=helper,
        string=string,
        count=-1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=pattern,
        helper=helper,
        string=string,
        count=-1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected_result: object = string if helper == "sub" else (string, 0)

    assert observed == expected == expected_result
    assert callback_calls == []


def assert_callable_replacement_invalid_count_typeerror_parity(
    *,
    backend: object,
    helper: str,
    pattern: TextValue,
    string: TextValue,
    count: object,
    use_compiled_pattern: bool = False,
) -> None:
    callback_calls: list[object] = []
    replacement_value = _callable_replacement_marker(string)

    def replacement(match: object) -> TextValue:
        callback_calls.append(match)
        return replacement_value

    with pytest.raises(TypeError) as observed_error:
        _invoke_callable_replacement(
            backend,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    with pytest.raises(TypeError) as expected_error:
        _invoke_callable_replacement(
            re,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    assert type(observed_error.value) is type(expected_error.value)
    assert observed_error.value.args == expected_error.value.args
    assert callback_calls == []


def _assert_source_callable_replacement_reference_is_valid(case: FixtureCase) -> None:
    replacement = _source_callable_replacement(case)
    assert replacement.get("type") == "callable_match_group"

    prefix = replacement.get("prefix", "")
    suffix = replacement.get("suffix", "")

    def assert_text_fragment_is_valid(fragment: object) -> None:
        if isinstance(fragment, str):
            return
        assert isinstance(fragment, dict)
        assert fragment.get("type") == "bytes"
        assert isinstance(fragment.get("value"), str)
        assert isinstance(fragment.get("encoding", "latin-1"), str)

    assert_text_fragment_is_valid(prefix)
    assert_text_fragment_is_valid(suffix)

    compiled = re.compile(case_pattern(case), case.flags or 0)
    group_reference = replacement.get("group", 0)
    if isinstance(group_reference, int):
        assert 0 <= group_reference <= compiled.groups
    else:
        assert isinstance(group_reference, str)
        assert group_reference in compiled.groupindex


def _live_unimplemented_callable_cases() -> tuple[FixtureCase, ...]:
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()

    return tuple(
        case
        for bundle in FIXTURE_BUNDLES
        for case in bundle.cases
        if evaluate_case(case, cpython_adapter, rebar_adapter)["comparison"]
        == "unimplemented"
    )


def test_pending_rebar_callable_frontier_matches_live_unimplemented_cases() -> None:
    live_unimplemented_cases = _live_unimplemented_callable_cases()

    assert {case.case_id for case in live_unimplemented_cases} == (
        PENDING_REBAR_CASE_IDS
    )
    assert {case.manifest_id for case in live_unimplemented_cases} == (
        PENDING_REBAR_MANIFEST_IDS
    )


def test_callable_replacement_selector_tracks_published_callable_manifests() -> None:
    expected_paths = select_correctness_fixture_paths(
        CALLABLE_REPLACEMENT_FIXTURE_SELECTOR
    )

    assert expected_paths
    assert tuple(bundle.manifest.path for bundle in FIXTURE_BUNDLES) == expected_paths
    assert tuple(bundle.manifest.path.name for bundle in FIXTURE_BUNDLES) == tuple(
        path.name for path in expected_paths
    )


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.manifest.manifest_id,
)
def test_callable_replacement_fixture_shape_contract(
    bundle: FixtureBundle,
) -> None:
    manifest_spec = CALLABLE_MANIFEST_SPECS_BY_ID.get(bundle.manifest.manifest_id)
    compile_patterns = bundle.expected_patterns
    expected_text_models = (
        manifest_spec.expected_text_models
        if manifest_spec is not None
        else bundle.expected_text_models
    )
    expected_operation_helper_counts = (
        manifest_spec.expected_operation_helper_counts
        if manifest_spec is not None
        else bundle.expected_operation_helper_counts
    )

    assert FIXTURE_BUNDLES_BY_MANIFEST_ID[bundle.manifest.manifest_id] is bundle
    assert bundle.manifest.layer == "module_workflow"
    assert bundle.manifest.defaults.get("text_model") == "str"
    assert len(bundle.cases) == sum(expected_operation_helper_counts.values())
    assert {case.text_model for case in bundle.cases} == expected_text_models
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        expected_operation_helper_counts
    )
    if manifest_spec is not None:
        assert bundle.expected_patterns == manifest_spec.expected_compile_patterns
    else:
        expected_pattern_count = 4 if expected_text_models == MIXED_TEXT_MODELS else 2
        assert len(bundle.expected_patterns) == expected_pattern_count

    has_named_pattern = False
    has_numbered_pattern = False
    for pattern in compile_patterns:
        compiled = re.compile(pattern)
        if compiled.groupindex:
            has_named_pattern = True
        else:
            has_numbered_pattern = True

    assert has_named_pattern
    assert has_numbered_pattern

    for case in bundle.cases:
        assert "callable-replacement" in case.categories
        assert case.text_model in case.categories
        _assert_source_callable_replacement_reference_is_valid(case)


def test_fixture_manifest_loader_materializes_callable_replacement_descriptors(
    tmp_path,
) -> None:
    fixture_path = tmp_path / "quantified_nested_group_callable_fixture.py"
    fixture_path.write_text(
        textwrap.dedent(
            """
            MANIFEST = {
                "schema_version": 1,
                "manifest_id": "quantified-nested-group-callable-loader-contract",
                "layer": "module_workflow",
                "suite_id": "collection.replacement.quantified_nested_group.callable.contract",
                "defaults": {
                    "text_model": "str",
                },
                "cases": [
                    {
                        "id": "module-sub-callable-numbered-contract-str",
                        "operation": "module_call",
                        "family": "quantified_nested_group_numbered_callable_contract",
                        "helper": "sub",
                        "args": [
                            r"a((bc)+)d",
                            {
                                "type": "callable_match_group",
                                "group": 1,
                                "suffix": "x",
                            },
                            "zzabcbcdzz",
                        ],
                        "categories": [
                            "workflow",
                            "callable-replacement",
                            "quantified",
                            "nested-group",
                            "str",
                        ],
                        "notes": [
                            "Ensures Python-backed fixtures can materialize numbered callable replacement descriptors for quantified nested-group workflows."
                        ],
                    },
                    {
                        "id": "pattern-subn-callable-named-contract-str",
                        "operation": "pattern_call",
                        "family": "quantified_nested_group_named_callable_contract",
                        "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                        "helper": "subn",
                        "args": [
                            {
                                "type": "callable_match_group",
                                "group": "inner",
                                "prefix": "<",
                                "suffix": ">",
                            },
                            "zzabcbcdabcbcdzz",
                            1,
                        ],
                        "categories": [
                            "workflow",
                            "callable-replacement",
                            "quantified",
                            "nested-group",
                            "str",
                        ],
                        "notes": [
                            "Ensures Python-backed fixtures can materialize named callable replacement descriptors for quantified nested-group workflows."
                        ],
                    },
                    {
                        "id": "module-sub-callable-constant-contract-str",
                        "operation": "module_call",
                        "family": "quantified_nested_group_constant_callable_contract",
                        "helper": "sub",
                        "args": [
                            r"a((bc)+)d",
                            {
                                "type": "callable_constant",
                                "value": "CONST",
                            },
                            "zzabcdzz",
                        ],
                        "categories": [
                            "workflow",
                            "callable-replacement",
                            "quantified",
                            "nested-group",
                            "str",
                        ],
                        "notes": [
                            "Ensures Python-backed fixtures can materialize constant callable descriptors without falling back to raw dict payloads."
                        ],
                    },
                ],
            }
            """
        ).lstrip(),
        encoding="utf-8",
    )

    manifest = load_fixture_manifest(fixture_path)
    numbered_case, named_case, constant_case = manifest.cases

    assert manifest.manifest_id == "quantified-nested-group-callable-loader-contract"
    assert manifest.layer == "module_workflow"
    assert (
        manifest.suite_id
        == "collection.replacement.quantified_nested_group.callable.contract"
    )
    assert [case.case_id for case in manifest.cases] == [
        "module-sub-callable-numbered-contract-str",
        "pattern-subn-callable-named-contract-str",
        "module-sub-callable-constant-contract-str",
    ]

    assert numbered_case.helper == "sub"
    assert case_pattern(numbered_case) == r"a((bc)+)d"
    assert numbered_case.source_args == [
        r"a((bc)+)d",
        {
            "type": "callable_match_group",
            "group": 1,
            "suffix": "x",
        },
        "zzabcbcdzz",
    ]
    assert numbered_case.source_kwargs == {}
    numbered_replacement = case_replacement_argument(numbered_case)
    assert callable(numbered_replacement)
    numbered_match = re.search(
        case_pattern(numbered_case),
        case_text_argument(numbered_case),
    )
    assert numbered_match is not None
    assert numbered_replacement(numbered_match) == "bcbcx"
    assert numbered_case.serialized_args()[1] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_match_group",
    }
    assert numbered_case.serialized_kwargs() == {}

    assert named_case.helper == "subn"
    assert case_pattern(named_case) == r"a(?P<outer>(?P<inner>bc)+)d"
    assert named_case.source_args == [
        {
            "type": "callable_match_group",
            "group": "inner",
            "prefix": "<",
            "suffix": ">",
        },
        "zzabcbcdabcbcdzz",
        1,
    ]
    assert named_case.source_kwargs == {}
    named_replacement = case_replacement_argument(named_case)
    assert callable(named_replacement)
    named_match = re.search(case_pattern(named_case), "zzabcbcdzz")
    assert named_match is not None
    assert named_replacement(named_match) == "<bc>"
    assert named_case.serialized_args()[0] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_match_group",
    }
    assert named_case.serialized_kwargs() == {}

    assert constant_case.helper == "sub"
    assert constant_case.source_args == [
        r"a((bc)+)d",
        {
            "type": "callable_constant",
            "value": "CONST",
        },
        "zzabcdzz",
    ]
    assert constant_case.source_kwargs == {}
    constant_replacement = case_replacement_argument(constant_case)
    assert callable(constant_replacement)
    constant_match = re.search(
        case_pattern(constant_case),
        case_text_argument(constant_case),
    )
    assert constant_match is not None
    assert constant_replacement(constant_match) == "CONST"
    assert constant_case.serialized_args()[1] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_constant",
    }
    assert constant_case.serialized_kwargs() == {}


def test_fixture_manifest_loader_materializes_bytes_callables_without_aliasing_defaults(
    tmp_path,
) -> None:
    fixture_path = tmp_path / "bytes_callable_fixture.py"
    fixture_path.write_text(
        textwrap.dedent(
            """
            MANIFEST = {
                "schema_version": 1,
                "manifest_id": "bytes-callable-loader-contract",
                "layer": "module_workflow",
                "suite_id": "collection.replacement.bytes.callable.contract",
                "defaults": {
                    "operation": "pattern_call",
                    "helper": "sub",
                    "text_model": "bytes",
                    "pattern_encoding": "latin-1",
                    "args": [
                        {
                            "type": "callable_match_group",
                            "group": 1,
                            "prefix": {
                                "type": "bytes",
                                "value": "<",
                            },
                            "suffix": {
                                "type": "bytes",
                                "value": ">",
                            },
                        },
                        {
                            "type": "bytes",
                            "value": "zzabcbcdzz",
                        },
                    ],
                    "kwargs": {
                        "count": 1,
                    },
                },
                "cases": [
                    {
                        "id": "pattern-sub-callable-match-group-default-a-bytes",
                        "family": "bytes_callable_match_group_default",
                        "pattern": r"a((bc)+)d",
                    },
                    {
                        "id": "pattern-sub-callable-match-group-default-b-bytes",
                        "family": "bytes_callable_match_group_default",
                        "pattern": r"a((bc)+)d",
                    },
                    {
                        "id": "pattern-sub-callable-constant-override-bytes",
                        "family": "bytes_callable_constant_override",
                        "pattern": r"a((bc)+)d",
                        "args": [
                            {
                                "type": "callable_constant",
                                "value": {
                                    "type": "bytes",
                                    "value": "CONST",
                                },
                            },
                            {
                                "type": "bytes",
                                "value": "zzabcbcdzz",
                            },
                        ],
                    },
                ],
            }
            """
        ).lstrip(),
        encoding="utf-8",
    )

    manifest = load_fixture_manifest(fixture_path)
    first_default_case, second_default_case, constant_case = manifest.cases

    assert manifest.manifest_id == "bytes-callable-loader-contract"
    assert manifest.layer == "module_workflow"
    assert manifest.suite_id == "collection.replacement.bytes.callable.contract"
    assert [case.case_id for case in manifest.cases] == [
        "pattern-sub-callable-match-group-default-a-bytes",
        "pattern-sub-callable-match-group-default-b-bytes",
        "pattern-sub-callable-constant-override-bytes",
    ]
    assert case_pattern(first_default_case) == rb"a((bc)+)d"
    assert case_pattern(second_default_case) == rb"a((bc)+)d"
    assert case_pattern(constant_case) == rb"a((bc)+)d"

    assert first_default_case.args is not second_default_case.args
    assert first_default_case.kwargs is not second_default_case.kwargs
    assert first_default_case.source_args is not second_default_case.source_args
    assert first_default_case.source_kwargs is not second_default_case.source_kwargs
    assert first_default_case.source_args == [
        {
            "type": "callable_match_group",
            "group": 1,
            "prefix": {
                "type": "bytes",
                "value": "<",
            },
            "suffix": {
                "type": "bytes",
                "value": ">",
            },
        },
        {
            "type": "bytes",
            "value": "zzabcbcdzz",
        },
    ]
    assert first_default_case.source_kwargs == {"count": 1}
    assert second_default_case.source_args == [
        {
            "type": "callable_match_group",
            "group": 1,
            "prefix": {
                "type": "bytes",
                "value": "<",
            },
            "suffix": {
                "type": "bytes",
                "value": ">",
            },
        },
        {
            "type": "bytes",
            "value": "zzabcbcdzz",
        },
    ]
    assert second_default_case.source_kwargs == {"count": 1}

    first_default_replacement = case_replacement_argument(first_default_case)
    second_default_replacement = case_replacement_argument(second_default_case)
    assert callable(first_default_replacement)
    assert callable(second_default_replacement)
    assert first_default_replacement is not second_default_replacement
    assert first_default_case.source_args[0] is not second_default_case.source_args[0]
    assert case_text_argument(first_default_case) == b"zzabcbcdzz"
    assert first_default_case.serialized_args() == [
        {
            "type": "callable",
            "module": "rebar_harness.correctness",
            "qualname": "callable_match_group",
        },
        {
            "encoding": "latin-1",
            "value": "zzabcbcdzz",
        },
    ]
    assert first_default_case.serialized_kwargs() == {"count": 1}

    default_match = re.search(
        case_pattern(first_default_case),
        case_text_argument(first_default_case),
    )
    assert default_match is not None
    assert first_default_replacement(default_match) == b"<bcbc>"

    first_default_case.args[1] = b"mutated"
    first_default_case.kwargs["count"] = 0
    first_default_case.source_args[0]["prefix"]["value"] = "["
    first_default_case.source_args[1]["value"] = "mutated-source"
    first_default_case.source_kwargs["count"] = 0
    assert second_default_case.args[1] == b"zzabcbcdzz"
    assert second_default_case.kwargs["count"] == 1
    assert second_default_case.source_args[0]["prefix"]["value"] == "<"
    assert second_default_case.source_args[1]["value"] == "zzabcbcdzz"
    assert second_default_case.source_kwargs["count"] == 1
    assert constant_case.kwargs["count"] == 1
    assert constant_case.source_kwargs["count"] == 1

    constant_replacement = case_replacement_argument(constant_case)
    assert callable(constant_replacement)
    assert constant_case.source_args == [
        {
            "type": "callable_constant",
            "value": {
                "type": "bytes",
                "value": "CONST",
            },
        },
        {
            "type": "bytes",
            "value": "zzabcbcdzz",
        },
    ]
    constant_match = re.search(
        case_pattern(constant_case),
        case_text_argument(constant_case),
    )
    assert constant_match is not None
    assert constant_replacement(constant_match) == b"CONST"
    assert constant_case.serialized_args()[0] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_constant",
    }
    assert constant_case.serialized_args()[1] == {
        "encoding": "latin-1",
        "value": "zzabcbcdzz",
    }
    assert constant_case.serialized_kwargs() == {"count": 1}


def test_literal_callable_case_stays_aligned_with_published_collection_fixture() -> None:
    case = _literal_callable_case()
    source_replacement = _source_callable_replacement(case)
    (expected_fixture_path,) = select_correctness_fixture_paths(
        COLLECTION_REPLACEMENT_FIXTURE_SELECTOR
    )

    assert COLLECTION_REPLACEMENT_OWNER_BUNDLE.manifest.path == expected_fixture_path
    assert COLLECTION_REPLACEMENT_OWNER_BUNDLE.manifest.manifest_id == (
        "collection-replacement-workflows"
    )
    assert tuple(
        fixture_case.case_id for fixture_case in COLLECTION_REPLACEMENT_OWNER_BUNDLE.cases
    ) == COLLECTION_REPLACEMENT_OWNER_BUNDLE.published_case_ids
    assert case.case_id == COLLECTION_REPLACEMENT_LITERAL_CALLABLE_CASE_ID
    assert case.operation == "module_call"
    assert case.helper == "sub"
    assert _literal_callable_pattern() == "abc"
    assert _literal_callable_string() == "abcabc"
    assert callable(case_replacement_argument(case))
    assert "callable-replacement" in case.categories
    assert "str" in case.categories
    assert source_replacement == {"type": "callable_constant", "value": "x"}
    assert case.source_kwargs == {}


@pytest.mark.parametrize(
    "manifest_spec",
    CALLABLE_MANIFEST_SPECS,
    ids=lambda spec: spec.manifest_id,
)
def test_callable_replacement_cases_stay_aligned_with_published_fixture(
    manifest_spec: CallableManifestSpec,
) -> None:
    bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[manifest_spec.manifest_id]

    assert bundle.manifest.manifest_id == manifest_spec.manifest_id
    assert len(bundle.cases) == len(manifest_spec.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == manifest_spec.expected_case_ids
    assert bundle.expected_patterns == manifest_spec.expected_compile_patterns
    assert {case.text_model for case in bundle.cases} == manifest_spec.expected_text_models
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        manifest_spec.expected_operation_helper_counts
    )
    assert {
        case.case_id for case in bundle.cases if _is_pending_rebar_callable_case(case)
    } == manifest_spec.pending_rebar_case_ids
    observed_near_miss_patterns = _near_miss_patterns_for_manifest(
        manifest_spec.manifest_id
    )
    assert observed_near_miss_patterns == manifest_spec.expected_near_miss_patterns
    assert any(
        near_miss_case.manifest_id == manifest_spec.manifest_id
        for near_miss_case in CALLABLE_NEAR_MISS_CASE_SPECS
    ) is bool(
        manifest_spec.expected_near_miss_patterns
    )


@pytest.mark.parametrize(
    "manifest_spec",
    tuple(
        pytest.param(spec, id=spec.manifest_id)
        for spec in CALLABLE_MANIFEST_SPECS
        if spec.expected_text_models == MIXED_TEXT_MODELS
    ),
)
def test_mixed_text_callable_manifest_partitions_track_pending_or_landed_bytes_cases(
    manifest_spec: CallableManifestSpec,
) -> None:
    bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[manifest_spec.manifest_id]
    shared_module_case_ids = frozenset(
        case.case_id
        for case in MODULE_CASES
        if case.manifest_id == manifest_spec.manifest_id
    )
    shared_pattern_case_ids = frozenset(
        case.case_id
        for case in PATTERN_CASES
        if case.manifest_id == manifest_spec.manifest_id
    )
    bytes_module_case_ids = frozenset(
        case.case_id
        for case in BYTES_MODULE_CASES
        if case.manifest_id == manifest_spec.manifest_id
    )
    bytes_pattern_case_ids = frozenset(
        case.case_id
        for case in BYTES_PATTERN_CASES
        if case.manifest_id == manifest_spec.manifest_id
    )
    expected_bytes_module_case_ids = frozenset(
        case.case_id
        for case in bundle.cases
        if case.text_model == "bytes" and case.operation == "module_call"
    )
    expected_bytes_pattern_case_ids = frozenset(
        case.case_id
        for case in bundle.cases
        if case.text_model == "bytes" and case.operation == "pattern_call"
    )
    expected_shared_module_case_ids = frozenset(
        case.case_id
        for case in bundle.cases
        if case.operation == "module_call"
        and case.case_id not in manifest_spec.pending_rebar_case_ids
    )
    expected_shared_pattern_case_ids = frozenset(
        case.case_id
        for case in bundle.cases
        if case.operation == "pattern_call"
        and case.case_id not in manifest_spec.pending_rebar_case_ids
    )

    assert {
        case.case_id for case in bundle.cases if case.text_model == "bytes"
    } == (
        expected_bytes_module_case_ids | expected_bytes_pattern_case_ids
    )
    assert bytes_module_case_ids == expected_bytes_module_case_ids
    assert bytes_pattern_case_ids == expected_bytes_pattern_case_ids
    assert shared_module_case_ids == expected_shared_module_case_ids
    assert shared_pattern_case_ids == expected_shared_pattern_case_ids
    assert manifest_spec.pending_rebar_case_ids <= (
        bytes_module_case_ids | bytes_pattern_case_ids
    )
    if manifest_spec.pending_rebar_case_ids:
        assert not {
            case.case_id
            for case in PATTERN_RETURN_TYPE_ERROR_CASES
            if case.case_id in manifest_spec.pending_rebar_case_ids
        }


def test_module_callable_replacement_return_type_error_cases_cover_quantified_callable_fixture_frontier(
) -> None:
    assert MODULE_RETURN_TYPE_ERROR_CASES
    assert {case.text_model for case in MODULE_RETURN_TYPE_ERROR_CASES} == {
        "bytes",
        "str",
    }
    assert not {
        case.case_id
        for case in MODULE_RETURN_TYPE_ERROR_CASES
        if _is_pending_rebar_callable_case(case)
    }
    assert {
        case.manifest_id for case in MODULE_RETURN_TYPE_ERROR_CASES
    } == _callable_return_type_error_expected_manifest_ids()


def test_pattern_callable_replacement_return_type_error_cases_cover_quantified_callable_fixture_frontier(
) -> None:
    assert PATTERN_RETURN_TYPE_ERROR_CASES
    assert {case.text_model for case in PATTERN_RETURN_TYPE_ERROR_CASES} == {
        "bytes",
        "str",
    }
    assert {
        case.manifest_id for case in PATTERN_RETURN_TYPE_ERROR_CASES
    } == _callable_return_type_error_expected_manifest_ids()


def test_shared_callable_pattern_pools_exclude_pending_rebar_frontier() -> None:
    shared_str_patterns = frozenset(
        str_case_pattern(case)
        for case in SHARED_CALLABLE_CASES
        if case.text_model == "str"
    )
    shared_bytes_patterns = frozenset(
        _bytes_case_pattern(case)
        for case in SHARED_CALLABLE_CASES
        if case.text_model == "bytes"
    )
    published_str_patterns = frozenset(
        str_case_pattern(case)
        for case in PUBLISHED_CALLABLE_CASES
        if case.text_model == "str"
    )
    published_bytes_patterns = frozenset(
        _bytes_case_pattern(case)
        for case in PUBLISHED_CALLABLE_CASES
        if case.text_model == "bytes"
    )
    near_miss_str_patterns = frozenset(
        near_miss_case.pattern
        for near_miss_case in CALLABLE_NEAR_MISS_CASE_SPECS
        if isinstance(near_miss_case.pattern, str)
    )
    near_miss_bytes_patterns = frozenset(
        near_miss_case.pattern
        for near_miss_case in CALLABLE_NEAR_MISS_CASE_SPECS
        if isinstance(near_miss_case.pattern, bytes)
    )

    assert set(COMPILE_PATTERNS) == shared_str_patterns
    assert set(NO_MATCH_PATTERNS) == shared_str_patterns | {_literal_callable_pattern()}
    assert set(BYTES_NO_MATCH_PATTERNS) == shared_bytes_patterns
    assert shared_str_patterns | PENDING_REBAR_STR_PATTERNS == published_str_patterns
    assert shared_bytes_patterns | PENDING_REBAR_BYTES_PATTERNS == (
        published_bytes_patterns
    )
    assert shared_str_patterns.isdisjoint(PENDING_REBAR_STR_PATTERNS)
    assert shared_bytes_patterns.isdisjoint(PENDING_REBAR_BYTES_PATTERNS)
    assert near_miss_str_patterns <= shared_str_patterns
    assert near_miss_bytes_patterns <= shared_bytes_patterns
    assert near_miss_str_patterns.isdisjoint(PENDING_REBAR_STR_PATTERNS)
    assert near_miss_bytes_patterns.isdisjoint(PENDING_REBAR_BYTES_PATTERNS)


def test_conditional_group_exists_bytes_near_miss_cases_mirror_str_cases() -> None:
    manifest_id = "conditional-group-exists-callable-replacement-workflows"
    bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[manifest_id]
    str_cases = tuple(
        case
        for case in CALLABLE_NEAR_MISS_CASE_SPECS
        if case.manifest_id == manifest_id
    )
    bytes_cases_by_id = {
        case.id: case for case in CONDITIONAL_GROUP_EXISTS_BYTES_NEAR_MISS_CASES
    }

    assert set(bytes_cases_by_id) == {f"{case.id}-bytes" for case in str_cases}
    assert {case.pattern for case in CONDITIONAL_GROUP_EXISTS_BYTES_NEAR_MISS_CASES} == {
        pattern for pattern in bundle.expected_patterns if isinstance(pattern, bytes)
    }
    assert {
        case.pattern for case in CONDITIONAL_GROUP_EXISTS_BYTES_NEAR_MISS_CASES
    }.isdisjoint(PENDING_REBAR_BYTES_PATTERNS)

    for str_case in str_cases:
        bytes_case = bytes_cases_by_id[f"{str_case.id}-bytes"]

        assert isinstance(str_case.pattern, str)
        assert isinstance(str_case.text, str)
        assert bytes_case.manifest_id == manifest_id
        assert bytes_case.use_compiled_pattern == str_case.use_compiled_pattern
        assert bytes_case.helper == str_case.helper
        assert bytes_case.count == str_case.count
        assert bytes_case.pattern == str_case.pattern.encode("latin-1")
        assert bytes_case.text == str_case.text.encode("latin-1")
        assert bytes_case.expected_result == _bytes_mirror_expected_result(
            str_case.expected_result
        )


def test_conditional_group_exists_negative_count_bytes_cases_mirror_str_cases() -> None:
    manifest_id = "conditional-group-exists-callable-replacement-workflows"
    bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[manifest_id]
    str_cases = tuple(
        case
        for case in bundle.cases
        if case.text_model == "str" and "negative-count" in case.categories
    )
    bytes_cases_by_id = {
        case.case_id: case
        for case in bundle.cases
        if case.text_model == "bytes" and "negative-count" in case.categories
    }

    assert len(str_cases) == len(bytes_cases_by_id) == 4
    _assert_published_callable_bytes_cases_mirror_str_cases(
        manifest_id=manifest_id,
        str_cases=str_cases,
        bytes_cases=tuple(bytes_cases_by_id.values()),
    )
    assert all(_case_count(case) == -1 for case in str_cases)
    assert all(_case_count(case) == -1 for case in bytes_cases_by_id.values())


def test_conditional_group_exists_alternation_bytes_cases_mirror_str_cases() -> None:
    manifest_id = "conditional-group-exists-callable-replacement-workflows"
    bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[manifest_id]
    str_cases = tuple(
        case
        for case in bundle.cases
        if case.text_model == "str" and "alternation" in case.categories
    )
    bytes_cases = tuple(
        case
        for case in bundle.cases
        if case.text_model == "bytes" and "alternation" in case.categories
    )

    assert len(str_cases) == len(bytes_cases) == 8
    _assert_published_callable_bytes_cases_mirror_str_cases(
        manifest_id=manifest_id,
        str_cases=str_cases,
        bytes_cases=bytes_cases,
    )


def test_conditional_group_exists_alternation_direct_case_tables_stay_aligned_with_published_fixture(
) -> None:
    manifest_id = "conditional-group-exists-callable-replacement-workflows"
    bundle = FIXTURE_BUNDLES_BY_MANIFEST_ID[manifest_id]

    def normalized_case_row(
        case: FixtureCase,
    ) -> tuple[str | bytes, int | str, str, str | bytes, int]:
        pattern = case_pattern(case)
        text = case_text_argument(case)
        replacement = _source_callable_replacement(case)

        assert case.helper is not None
        assert isinstance(pattern, (str, bytes))
        assert isinstance(text, (str, bytes))
        assert isinstance(replacement, dict)

        group_ref = replacement["group"]
        assert isinstance(group_ref, (int, str))
        return pattern, group_ref, case.helper, text, _case_count(case)

    alternation_cases = tuple(
        case
        for case in bundle.cases
        if "alternation" in case.categories
    )
    present_rows = {
        normalized_case_row(case)
        for case in alternation_cases
        if case.text_model == "str" and "present" in case.categories
    }
    absent_rows = {
        normalized_case_row(case)
        for case in alternation_cases
        if case.text_model == "str" and "absent" in case.categories
    }
    bytes_present_rows = {
        normalized_case_row(case)
        for case in alternation_cases
        if case.text_model == "bytes" and "present" in case.categories
    }
    bytes_absent_rows = {
        normalized_case_row(case)
        for case in alternation_cases
        if case.text_model == "bytes" and "absent" in case.categories
    }

    assert len(alternation_cases) == (
        len(present_rows)
        + len(absent_rows)
        + len(bytes_present_rows)
        + len(bytes_absent_rows)
    )
    assert present_rows == set(CONDITIONAL_GROUP_EXISTS_ALTERNATION_GROUP_ACCESS_CASES)
    assert absent_rows == set(
        CONDITIONAL_GROUP_EXISTS_ALTERNATION_ABSENT_EXCEPTION_CASES
    )
    assert bytes_present_rows == set(
        CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_GROUP_ACCESS_CASES
    )
    assert bytes_absent_rows == set(
        CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_ABSENT_EXCEPTION_CASES
    )


def test_conditional_group_exists_alternation_bytes_direct_case_tables_mirror_str_tables(
) -> None:
    _assert_bytes_direct_case_table_mirrors_str_table(
        str_cases=CONDITIONAL_GROUP_EXISTS_ALTERNATION_GROUP_ACCESS_CASES,
        bytes_cases=CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_GROUP_ACCESS_CASES,
    )
    _assert_bytes_direct_case_table_mirrors_str_table(
        str_cases=CONDITIONAL_GROUP_EXISTS_ALTERNATION_ABSENT_EXCEPTION_CASES,
        bytes_cases=CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_ABSENT_EXCEPTION_CASES,
    )


def test_callable_replacement_callback_exception_case_pools_exclude_negative_count_rows(
) -> None:
    module_negative_count_case_ids = {
        case.case_id
        for case in MODULE_CASES
        if _is_negative_count_callable_case(case)
    }
    pattern_negative_count_case_ids = {
        case.case_id
        for case in PATTERN_CASES
        if _is_negative_count_callable_case(case)
    }
    bytes_module_negative_count_case_ids = {
        case.case_id
        for case in BYTES_MODULE_CASES
        if _is_negative_count_callable_case(case)
    }
    bytes_pattern_negative_count_case_ids = {
        case.case_id
        for case in BYTES_PATTERN_CASES
        if _is_negative_count_callable_case(case)
    }

    assert module_negative_count_case_ids
    assert pattern_negative_count_case_ids
    assert bytes_module_negative_count_case_ids == (
        module_negative_count_case_ids & {case.case_id for case in BYTES_MODULE_CASES}
    )
    assert bytes_pattern_negative_count_case_ids == (
        pattern_negative_count_case_ids
        & {case.case_id for case in BYTES_PATTERN_CASES}
    )
    assert {case.case_id for case in MODULE_CALLBACK_EXCEPTION_CASES}.isdisjoint(
        module_negative_count_case_ids
    )
    assert {case.case_id for case in PATTERN_CALLBACK_EXCEPTION_CASES}.isdisjoint(
        pattern_negative_count_case_ids
    )
    assert {
        case.case_id for case in BYTES_MODULE_CALLBACK_EXCEPTION_CASES
    }.isdisjoint(bytes_module_negative_count_case_ids)
    assert {
        case.case_id for case in BYTES_PATTERN_CALLBACK_EXCEPTION_CASES
    }.isdisjoint(bytes_pattern_negative_count_case_ids)
    assert (
        {case.case_id for case in MODULE_CALLBACK_EXCEPTION_CASES}
        | module_negative_count_case_ids
        == {case.case_id for case in MODULE_CASES}
    )
    assert (
        {case.case_id for case in PATTERN_CALLBACK_EXCEPTION_CASES}
        | pattern_negative_count_case_ids
        == {case.case_id for case in PATTERN_CASES}
    )
    assert (
        {case.case_id for case in BYTES_MODULE_CALLBACK_EXCEPTION_CASES}
        | bytes_module_negative_count_case_ids
        == {case.case_id for case in BYTES_MODULE_CASES}
    )
    assert (
        {case.case_id for case in BYTES_PATTERN_CALLBACK_EXCEPTION_CASES}
        | bytes_pattern_negative_count_case_ids
        == {case.case_id for case in BYTES_PATTERN_CASES}
    )


def test_callable_replacement_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {
            "shared-module": frozenset(case.case_id for case in MODULE_CASES),
            "shared-pattern": frozenset(case.case_id for case in PATTERN_CASES),
            "pending-rebar-bytes-module": frozenset(
                case.case_id for case in PENDING_REBAR_MODULE_CASES
            ),
            "pending-rebar-bytes-pattern": frozenset(
                case.case_id for case in PENDING_REBAR_PATTERN_CASES
            ),
        },
        selected_case_ids=(
            case.case_id for case in PUBLISHED_CALLABLE_CASES
        ),
        coverage_label="callable replacement direct-test case-id buckets",
    )


NO_MATCH_PATTERNS = tuple(sorted({*COMPILE_PATTERNS, _literal_callable_pattern()}))
PENDING_REBAR_STR_PATTERNS = _pending_rebar_str_patterns()
PENDING_REBAR_BYTES_PATTERNS = _pending_rebar_bytes_patterns()


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    _, backend = regex_backend

    observed = backend.compile(pattern)
    expected = re.compile(pattern)

    assert observed is backend.compile(pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    LITERAL_CALLABLE_PARITY_VARIANTS,
)
def test_literal_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    def replacement(_match: object) -> str:
        return "x"

    if use_compiled_pattern:
        observed_target = backend.compile(_literal_callable_pattern())
        expected_target = re.compile(_literal_callable_pattern())
        observed = getattr(observed_target, helper)(
            replacement,
            _literal_callable_string(),
            count=count,
        )
        expected = getattr(expected_target, helper)(
            replacement,
            _literal_callable_string(),
            count=count,
        )
    else:
        observed = getattr(backend, helper)(
            _literal_callable_pattern(),
            replacement,
            _literal_callable_string(),
            count=count,
        )
        expected = getattr(re, helper)(
            _literal_callable_pattern(),
            replacement,
            _literal_callable_string(),
            count=count,
        )

    assert observed == expected


@pytest.mark.parametrize("pattern", NO_MATCH_PATTERNS)
@pytest.mark.parametrize(
    ("helper", "use_compiled_pattern"),
    CALLABLE_NO_MATCH_VARIANTS,
)
def test_callable_replacement_no_match_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    pattern: str,
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    assert_callable_replacement_no_match_path_leaves_input_unchanged(
        backend=backend,
        pattern=pattern,
        helper=helper,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("pattern", BYTES_NO_MATCH_PATTERNS)
@pytest.mark.parametrize(
    ("helper", "use_compiled_pattern"),
    CALLABLE_NO_MATCH_VARIANTS,
)
def test_bytes_callable_replacement_no_match_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    pattern: bytes,
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    assert_callable_replacement_no_match_path_leaves_input_unchanged(
        backend=backend,
        pattern=pattern,
        helper=helper,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    "near_miss_case",
    CALLABLE_NEAR_MISS_CASE_SPECS,
    ids=lambda case: case.id,
)
def test_callable_replacement_near_miss_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    near_miss_case: CallableNearMissCase,
) -> None:
    _, backend = regex_backend
    assert_callable_replacement_near_miss_path_leaves_input_unchanged(
        backend=backend,
        near_miss_case=near_miss_case,
    )


@pytest.mark.parametrize(
    "near_miss_case",
    CONDITIONAL_GROUP_EXISTS_BYTES_NEAR_MISS_CASES,
    ids=lambda case: case.id,
)
def test_conditional_group_exists_bytes_callable_replacement_near_miss_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    near_miss_case: CallableNearMissCase,
) -> None:
    _, backend = regex_backend
    assert_callable_replacement_near_miss_path_leaves_input_unchanged(
        backend=backend,
        near_miss_case=near_miss_case,
    )


@pytest.mark.parametrize(
    ("helper", "use_compiled_pattern"),
    CALLABLE_NO_MATCH_VARIANTS,
)
def test_literal_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize("case", BYTES_MODULE_CASES, ids=lambda case: case.case_id)
def test_module_bytes_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
    )


@pytest.mark.parametrize("case", BYTES_PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_bytes_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize(
    ("helper", "use_compiled_pattern"),
    CALLABLE_NO_MATCH_VARIANTS,
)
def test_literal_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        count=None,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        count=None,
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        count=None,
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize("case", BYTES_MODULE_CASES, ids=lambda case: case.case_id)
def test_module_bytes_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
        count=None,
    )


@pytest.mark.parametrize("case", BYTES_PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_bytes_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
        count=None,
        use_compiled_pattern=True,
    )


def _nested_group_bytes_replacement(group: int | str):
    def replacement(match: object) -> bytes:
        capture = match.group(group)
        assert isinstance(capture, bytes)
        return b"<" + capture + b">"

    return replacement


@pytest.mark.parametrize(
    ("helper", "count", "group", "expected"),
    (
        pytest.param("sub", 0, 1, b"<b><b>", id="sub-group-1"),
        pytest.param("subn", 1, 2, (b"<b>abd", 1), id="subn-count-one-group-2"),
    ),
)
def test_nested_group_callable_bytes_module_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    group: int,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a((b))d"
    string = b"abdabd"
    replacement = _nested_group_bytes_replacement(group)

    observed = getattr(backend, helper)(pattern, replacement, string, count=count)
    expected_result = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "group", "expected"),
    (
        pytest.param("sub", 0, "outer", b"<b><b>", id="sub-outer"),
        pytest.param("subn", 1, "inner", (b"<b>abd", 1), id="subn-count-one-inner"),
    ),
)
def test_nested_group_callable_bytes_pattern_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    group: str,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a(?P<outer>(?P<inner>b))d"
    string = b"abdabd"
    replacement = _nested_group_bytes_replacement(group)

    observed_target = backend.compile(pattern)
    expected_target = re.compile(pattern)
    observed = getattr(observed_target, helper)(replacement, string, count=count)
    expected_result = getattr(expected_target, helper)(replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "group", "expected"),
    (
        pytest.param("sub", 0, 1, b"zz<bcbc>zz", id="sub-group-1"),
        pytest.param("subn", 1, 2, (b"zz<bc>abcbcdzz", 1), id="subn-count-one-group-2"),
    ),
)
def test_quantified_nested_group_callable_bytes_module_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    group: int,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a((bc)+)d"
    string = b"zzabcbcdabcbcdzz" if helper == "subn" else b"zzabcbcdzz"
    replacement = _nested_group_bytes_replacement(group)

    observed = getattr(backend, helper)(pattern, replacement, string, count=count)
    expected_result = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "group", "expected"),
    (
        pytest.param("sub", 0, "outer", b"zz<bcbc>zz", id="sub-outer"),
        pytest.param("subn", 1, "inner", (b"zz<bc>abcbcdzz", 1), id="subn-count-one-inner"),
    ),
)
def test_quantified_nested_group_callable_bytes_pattern_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    group: str,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a(?P<outer>(?P<inner>bc)+)d"
    string = b"zzabcbcdabcbcdzz" if helper == "subn" else b"zzabcbcdzz"
    replacement = _nested_group_bytes_replacement(group)

    observed_target = backend.compile(pattern)
    expected_target = re.compile(pattern)
    observed = getattr(observed_target, helper)(replacement, string, count=count)
    expected_result = getattr(expected_target, helper)(replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "string", "expected"),
    (
        pytest.param("sub", 0, b"zzabdzz", b"zzbxzz", id="sub-group-1"),
        pytest.param(
            "subn",
            1,
            b"zzabccdacbbdzz",
            (b"zz<c>acbbdzz", 1),
            id="subn-count-one-group-2",
        ),
    ),
)
def test_quantified_nested_group_alternation_callable_bytes_module_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    string: bytes,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a((b|c)+)d"
    replacement = (
        (lambda match: match.group(1) + b"x")
        if helper == "sub"
        else (lambda match: b"<" + match.group(2) + b">")
    )

    observed = getattr(backend, helper)(pattern, replacement, string, count=count)
    expected_result = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "string", "expected"),
    (
        pytest.param("sub", 0, b"zzabccdzz", b"zzbccxzz", id="sub-outer"),
        pytest.param(
            "subn",
            1,
            b"zzabccdzz",
            (b"zz<c>zz", 1),
            id="subn-count-one-inner",
        ),
    ),
)
def test_quantified_nested_group_alternation_callable_bytes_pattern_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    string: bytes,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a(?P<outer>(?P<inner>b|c)+)d"
    replacement = (
        (lambda match: match.group("outer") + b"x")
        if helper == "sub"
        else (lambda match: b"<" + match.group("inner") + b">")
    )

    observed_target = backend.compile(pattern)
    expected_target = re.compile(pattern)
    observed = getattr(observed_target, helper)(replacement, string, count=count)
    expected_result = getattr(expected_target, helper)(replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "string", "expected"),
    (
        pytest.param("sub", 0, b"zzabbdzz", b"zzbxzz", id="sub-group-1"),
        pytest.param(
            "subn",
            1,
            b"abbdaccd",
            (b"<b>accd", 1),
            id="subn-count-one-group-2",
        ),
    ),
)
def test_nested_group_alternation_branch_local_backreference_callable_bytes_module_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    string: bytes,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a((b|c))\2d"
    replacement = (
        (lambda match: match.group(1) + b"x")
        if helper == "sub"
        else (lambda match: b"<" + match.group(2) + b">")
    )

    observed = getattr(backend, helper)(pattern, replacement, string, count=count)
    expected_result = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "string", "expected"),
    (
        pytest.param("sub", 0, b"abbdaccd", b"bxcx", id="sub-outer"),
        pytest.param(
            "subn",
            1,
            b"abbdaccd",
            (b"<b>accd", 1),
            id="subn-count-one-inner",
        ),
    ),
)
def test_nested_group_alternation_branch_local_backreference_callable_bytes_pattern_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    string: bytes,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a(?P<outer>(?P<inner>b|c))(?P=inner)d"
    replacement = (
        (lambda match: match.group("outer") + b"x")
        if helper == "sub"
        else (lambda match: b"<" + match.group("inner") + b">")
    )

    observed_target = backend.compile(pattern)
    expected_target = re.compile(pattern)
    observed = getattr(observed_target, helper)(replacement, string, count=count)
    expected_result = getattr(expected_target, helper)(replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "string", "expected"),
    (
        pytest.param("sub", 0, b"abbd", b"bx", id="sub-group-1"),
        pytest.param(
            "subn",
            1,
            b"abbbdaccd",
            (b"<b>accd", 1),
            id="subn-count-one-group-2",
        ),
    ),
)
def test_quantified_nested_group_alternation_branch_local_backreference_callable_bytes_module_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    string: bytes,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a((b|c)+)\2d"
    replacement = (
        (lambda match: match.group(1) + b"x")
        if helper == "sub"
        else (lambda match: b"<" + match.group(2) + b">")
    )

    observed = getattr(backend, helper)(pattern, replacement, string, count=count)
    expected_result = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "string", "expected"),
    (
        pytest.param("sub", 0, b"accd", b"cx", id="sub-outer"),
        pytest.param(
            "subn",
            1,
            b"abbbdaccd",
            (b"<b>accd", 1),
            id="subn-count-one-inner",
        ),
    ),
)
def test_quantified_nested_group_alternation_branch_local_backreference_callable_bytes_pattern_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    string: bytes,
    expected: bytes | tuple[bytes, int],
) -> None:
    _, backend = regex_backend
    pattern = rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"
    replacement = (
        (lambda match: match.group("outer") + b"x")
        if helper == "sub"
        else (lambda match: b"<" + match.group("inner") + b">")
    )

    observed_target = backend.compile(pattern)
    expected_target = re.compile(pattern)
    observed = getattr(observed_target, helper)(replacement, string, count=count)
    expected_result = getattr(expected_target, helper)(replacement, string, count=count)

    assert observed == expected_result
    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "pattern", "string"),
    (
        pytest.param("sub", 0, "(abc)", "abcabc", id="str-sub"),
        pytest.param("subn", 1, "(abc)", "abcabc", id="str-subn-count-one"),
        pytest.param("sub", 0, rb"(abc)", b"abcabc", id="bytes-sub"),
        pytest.param("subn", 1, rb"(abc)", b"abcabc", id="bytes-subn-count-one"),
    ),
)
def test_grouped_callable_replacement_module_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    pattern: TextValue,
    string: TextValue,
) -> None:
    backend_name, backend = regex_backend

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=helper,
        pattern=pattern,
        string=string,
        count=count,
    )


@pytest.mark.parametrize(
    ("helper", "count", "pattern", "string"),
    (
        pytest.param("sub", 0, "(?P<word>abc)", "abcabc", id="str-sub"),
        pytest.param(
            "subn",
            1,
            "(?P<word>abc)",
            "abcabc",
            id="str-subn-count-one",
        ),
        pytest.param("sub", 0, rb"(?P<word>abc)", b"abcabc", id="bytes-sub"),
        pytest.param(
            "subn",
            1,
            rb"(?P<word>abc)",
            b"abcabc",
            id="bytes-subn-count-one",
        ),
    ),
)
def test_grouped_callable_replacement_pattern_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    pattern: TextValue,
    string: TextValue,
) -> None:
    backend_name, backend = regex_backend

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=helper,
        pattern=pattern,
        string=string,
        count=count,
        group_names=("word",),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    observed = _observe_published_callable_case(backend, case)
    expected = _observe_published_callable_case(re, case)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    observed = _observe_published_callable_case(backend, case)
    expected = _observe_published_callable_case(re, case)

    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    LITERAL_CALLABLE_PARITY_VARIANTS,
)
def test_literal_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    LITERAL_CALLABLE_PARITY_VARIANTS,
)
def test_literal_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend

    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
    )


@pytest.mark.parametrize(
    "case",
    MODULE_CALLBACK_EXCEPTION_CASES,
    ids=lambda case: case.case_id,
)
def test_module_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
    )


@pytest.mark.parametrize("case", BYTES_MODULE_CASES, ids=lambda case: case.case_id)
def test_module_bytes_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
        count=_case_count(case),
    )


@pytest.mark.parametrize(
    "case",
    BYTES_MODULE_CALLBACK_EXCEPTION_CASES,
    ids=lambda case: case.case_id,
)
def test_module_bytes_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
        count=_case_count(case),
    )


def _assert_conditional_group_exists_bytes_callable_group_access_parity(
    *,
    backend_name: str,
    backend: object,
    pattern: bytes,
    group_ref: int | str,
    use_compiled_pattern: bool,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[bytes]] = []

    def observed_replacement(match: object) -> bytes:
        observed_matches.append(match)
        return match.group(group_ref) + b"x"

    def expected_replacement(match: re.Match[bytes]) -> bytes:
        expected_matches.append(match)
        return match.group(group_ref) + b"x"

    observed = _invoke_callable_replacement(
        backend,
        pattern=pattern,
        helper="sub",
        string=b"zzabcdzz",
        count=0,
        replacement=observed_replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=pattern,
        helper="sub",
        string=b"zzabcdzz",
        count=0,
        replacement=expected_replacement,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed == expected
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


def _assert_conditional_group_exists_bytes_callable_absent_capture_typeerror_parity(
    *,
    backend_name: str,
    backend: object,
    pattern: bytes,
    group_ref: int | str,
    use_compiled_pattern: bool,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[bytes]] = []

    def observed_replacement(match: object) -> bytes:
        observed_matches.append(match)
        return match.group(group_ref) + b"x"

    def expected_replacement(match: re.Match[bytes]) -> bytes:
        expected_matches.append(match)
        return match.group(group_ref) + b"x"

    with pytest.raises(TypeError) as observed_error:
        _invoke_callable_replacement(
            backend,
            pattern=pattern,
            helper="subn",
            string=b"zzacezz",
            count=1,
            replacement=observed_replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    with pytest.raises(TypeError) as expected_error:
        _invoke_callable_replacement(
            re,
            pattern=pattern,
            helper="subn",
            string=b"zzacezz",
            count=1,
            replacement=expected_replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    assert normalize_exception(observed_error.value) == normalize_exception(
        expected_error.value
    )
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


def _assert_conditional_group_exists_alternation_callable_group_access_parity(
    *,
    backend_name: str,
    backend: object,
    pattern: str,
    group_ref: int | str,
    helper: str,
    string: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str]] = []

    def observed_replacement(match: object) -> str:
        observed_matches.append(match)
        return match.group(group_ref) + "x"

    def expected_replacement(match: re.Match[str]) -> str:
        expected_matches.append(match)
        return match.group(group_ref) + "x"

    observed = _invoke_callable_replacement(
        backend,
        pattern=pattern,
        helper=helper,
        string=string,
        count=count,
        replacement=observed_replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=pattern,
        helper=helper,
        string=string,
        count=count,
        replacement=expected_replacement,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed == expected
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


def _assert_conditional_group_exists_alternation_callable_absent_capture_typeerror_parity(
    *,
    backend_name: str,
    backend: object,
    pattern: str,
    group_ref: int | str,
    helper: str,
    string: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str]] = []

    def observed_replacement(match: object) -> str:
        observed_matches.append(match)
        return match.group(group_ref) + "x"

    def expected_replacement(match: re.Match[str]) -> str:
        expected_matches.append(match)
        return match.group(group_ref) + "x"

    with pytest.raises(TypeError) as observed_error:
        _invoke_callable_replacement(
            backend,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=observed_replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    with pytest.raises(TypeError) as expected_error:
        _invoke_callable_replacement(
            re,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=expected_replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    assert normalize_exception(observed_error.value) == normalize_exception(
        expected_error.value
    )
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


def _assert_conditional_group_exists_alternation_bytes_callable_group_access_parity(
    *,
    backend_name: str,
    backend: object,
    pattern: bytes,
    group_ref: int | str,
    helper: str,
    string: bytes,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[bytes]] = []

    def observed_replacement(match: object) -> bytes:
        observed_matches.append(match)
        return match.group(group_ref) + b"x"

    def expected_replacement(match: re.Match[bytes]) -> bytes:
        expected_matches.append(match)
        return match.group(group_ref) + b"x"

    observed = _invoke_callable_replacement(
        backend,
        pattern=pattern,
        helper=helper,
        string=string,
        count=count,
        replacement=observed_replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=pattern,
        helper=helper,
        string=string,
        count=count,
        replacement=expected_replacement,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed == expected
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


def _assert_conditional_group_exists_alternation_bytes_callable_absent_capture_typeerror_parity(
    *,
    backend_name: str,
    backend: object,
    pattern: bytes,
    group_ref: int | str,
    helper: str,
    string: bytes,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[bytes]] = []

    def observed_replacement(match: object) -> bytes:
        observed_matches.append(match)
        return match.group(group_ref) + b"x"

    def expected_replacement(match: re.Match[bytes]) -> bytes:
        expected_matches.append(match)
        return match.group(group_ref) + b"x"

    with pytest.raises(TypeError) as observed_error:
        _invoke_callable_replacement(
            backend,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=observed_replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    with pytest.raises(TypeError) as expected_error:
        _invoke_callable_replacement(
            re,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=expected_replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    assert normalize_exception(observed_error.value) == normalize_exception(
        expected_error.value
    )
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (False, True),
    ids=("module", "pattern"),
)
@pytest.mark.parametrize(
    ("pattern", "group_ref", "helper", "string", "count"),
    CONDITIONAL_GROUP_EXISTS_ALTERNATION_GROUP_ACCESS_CASES,
    ids=(
        "numbered-sub-present-first-arm",
        "numbered-subn-present-second-arm",
        "named-sub-present-first-arm",
        "named-subn-present-second-arm",
    ),
)
def test_conditional_group_exists_alternation_callable_replacement_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
    group_ref: int | str,
    helper: str,
    string: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    _assert_conditional_group_exists_alternation_callable_group_access_parity(
        backend_name=backend_name,
        backend=backend,
        pattern=pattern,
        group_ref=group_ref,
        helper=helper,
        string=string,
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (False, True),
    ids=("module", "pattern"),
)
@pytest.mark.parametrize(
    ("pattern", "group_ref", "helper", "string", "count"),
    CONDITIONAL_GROUP_EXISTS_ALTERNATION_ABSENT_EXCEPTION_CASES,
    ids=(
        "numbered-sub-absent-first-arm",
        "numbered-subn-absent-second-arm",
        "named-sub-absent-first-arm",
        "named-subn-absent-second-arm",
    ),
)
def test_conditional_group_exists_alternation_callable_replacement_absent_capture_typeerror_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
    group_ref: int | str,
    helper: str,
    string: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    _assert_conditional_group_exists_alternation_callable_absent_capture_typeerror_parity(
        backend_name=backend_name,
        backend=backend,
        pattern=pattern,
        group_ref=group_ref,
        helper=helper,
        string=string,
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (False, True),
    ids=("module", "pattern"),
)
@pytest.mark.parametrize(
    ("pattern", "group_ref", "helper", "string", "count"),
    CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_GROUP_ACCESS_CASES,
    ids=(
        "numbered-sub-present-first-arm",
        "numbered-subn-present-second-arm",
        "named-sub-present-first-arm",
        "named-subn-present-second-arm",
    ),
)
def test_conditional_group_exists_alternation_bytes_callable_replacement_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: bytes,
    group_ref: int | str,
    helper: str,
    string: bytes,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    _assert_conditional_group_exists_alternation_bytes_callable_group_access_parity(
        backend_name=backend_name,
        backend=backend,
        pattern=pattern,
        group_ref=group_ref,
        helper=helper,
        string=string,
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (False, True),
    ids=("module", "pattern"),
)
@pytest.mark.parametrize(
    ("pattern", "group_ref", "helper", "string", "count"),
    CONDITIONAL_GROUP_EXISTS_ALTERNATION_BYTES_ABSENT_EXCEPTION_CASES,
    ids=(
        "numbered-sub-absent-first-arm",
        "numbered-subn-absent-second-arm",
        "named-sub-absent-first-arm",
        "named-subn-absent-second-arm",
    ),
)
def test_conditional_group_exists_alternation_bytes_callable_replacement_absent_capture_typeerror_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: bytes,
    group_ref: int | str,
    helper: str,
    string: bytes,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    _assert_conditional_group_exists_alternation_bytes_callable_absent_capture_typeerror_parity(
        backend_name=backend_name,
        backend=backend,
        pattern=pattern,
        group_ref=group_ref,
        helper=helper,
        string=string,
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (False, True),
    ids=("module", "pattern"),
)
@pytest.mark.parametrize(
    ("pattern", "group_ref"),
    (
        (rb"a(b)?c(?(1)d|e)", 1),
        (rb"a(?P<word>b)?c(?(word)d|e)", "word"),
    ),
    ids=("numbered", "named"),
)
def test_conditional_group_exists_bytes_callable_replacement_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: bytes,
    group_ref: int | str,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    _assert_conditional_group_exists_bytes_callable_group_access_parity(
        backend_name=backend_name,
        backend=backend,
        pattern=pattern,
        group_ref=group_ref,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (False, True),
    ids=("module", "pattern"),
)
@pytest.mark.parametrize(
    ("pattern", "group_ref"),
    (
        (rb"a(b)?c(?(1)d|e)", 1),
        (rb"a(?P<word>b)?c(?(word)d|e)", "word"),
    ),
    ids=("numbered", "named"),
)
def test_conditional_group_exists_bytes_callable_replacement_absent_capture_typeerror_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: bytes,
    group_ref: int | str,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    _assert_conditional_group_exists_bytes_callable_absent_capture_typeerror_parity(
        backend_name=backend_name,
        backend=backend,
        pattern=pattern,
        group_ref=group_ref,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize("case", BYTES_PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_bytes_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
        count=_case_count(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize(
    "case",
    PATTERN_CALLBACK_EXCEPTION_CASES,
    ids=lambda case: case.case_id,
)
def test_pattern_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize(
    ("pattern", "group_ref"),
    (
        (rb"a(b)?c(?(1)d|e)", 1),
        (rb"a(?P<word>b)?c(?(word)d|e)", "word"),
    ),
    ids=("numbered", "named"),
)
def test_conditional_group_exists_pattern_bytes_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: bytes,
    group_ref: int | str,
) -> None:
    backend_name, backend = regex_backend
    observed_matches: list[object] = []
    expected_matches: list[re.Match[bytes]] = []
    observed_target = backend.compile(pattern)
    expected_target = re.compile(pattern)

    def observed_replacement(match: object) -> bytes:
        observed_matches.append(match)
        return match.group(group_ref) + b"x"

    def expected_replacement(match: re.Match[bytes]) -> bytes:
        expected_matches.append(match)
        return match.group(group_ref) + b"x"

    observed = observed_target.sub(observed_replacement, b"zzabcdzz")
    expected = expected_target.sub(expected_replacement, b"zzabcdzz")

    assert observed == expected
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )


@pytest.mark.parametrize(
    ("pattern", "group_ref"),
    (
        (rb"a(b)?c(?(1)d|e)", 1),
        (rb"a(?P<word>b)?c(?(word)d|e)", "word"),
    ),
    ids=("numbered", "named"),
)
def test_conditional_group_exists_pattern_bytes_callable_replacement_absent_capture_typeerror_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: bytes,
    group_ref: int | str,
) -> None:
    backend_name, backend = regex_backend
    observed_matches: list[object] = []
    expected_matches: list[re.Match[bytes]] = []
    observed_target = backend.compile(pattern)
    expected_target = re.compile(pattern)

    def observed_replacement(match: object) -> bytes:
        observed_matches.append(match)
        return match.group(group_ref) + b"x"

    def expected_replacement(match: re.Match[bytes]) -> bytes:
        expected_matches.append(match)
        return match.group(group_ref) + b"x"

    with pytest.raises(TypeError) as observed_error:
        observed_target.subn(observed_replacement, b"zzacezz", 1)

    with pytest.raises(TypeError) as expected_error:
        expected_target.subn(expected_replacement, b"zzacezz", 1)

    assert normalize_exception(observed_error.value) == normalize_exception(
        expected_error.value
    )
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


@pytest.mark.parametrize(
    "case",
    BYTES_PATTERN_CALLBACK_EXCEPTION_CASES,
    ids=lambda case: case.case_id,
)
def test_pattern_bytes_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    assert case.text_model == "bytes"

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=case_text_argument(case),
        count=_case_count(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize(
    "case",
    PATTERN_RETURN_TYPE_ERROR_CASES,
    ids=lambda case: case.case_id,
)
def test_pattern_callable_replacement_wrong_return_type_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_return_type_error_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        use_compiled_pattern=True,
    )
