from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_direct_bytes_follow_on_bundle_routing,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    partition_direct_bytes_follow_on_case_buckets,
    published_fixture_bundle_by_manifest_id,
    str_case_pattern,
)


@dataclass(frozen=True)
class SupplementalMissCase:
    id: str
    target: str
    pattern: str
    helper: str
    text: str


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern_case_id: str
    helper: str
    string: str
    bounds: tuple[int, ...]


@dataclass(frozen=True)
class DirectBytesBoundedPatternCase:
    id: str
    pattern: bytes
    helper: str
    string: bytes
    bounds: tuple[int, ...]


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
    bucket_label: str
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_module_search_texts_by_pattern: dict[bytes, frozenset[bytes]]
    expected_pattern_fullmatch_texts_by_pattern: dict[bytes, frozenset[bytes]]


FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "branch_local_backreference_workflows.py",
        expected_manifest_id="branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "branch-local-numbered-backreference-compile-metadata-str",
                "branch-local-numbered-backreference-module-search-str",
                "branch-local-numbered-backreference-pattern-fullmatch-str",
                "branch-local-named-backreference-compile-metadata-str",
                "branch-local-named-backreference-module-search-str",
                "branch-local-named-backreference-pattern-fullmatch-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b)|c)\2d",
                r"a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
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
        "quantified_branch_local_backreference_workflows.py",
        expected_manifest_id="quantified-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-branch-local-numbered-backreference-compile-metadata-str",
                "quantified-branch-local-numbered-backreference-module-search-lower-bound-str",
                "quantified-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-str",
                "quantified-branch-local-numbered-backreference-pattern-fullmatch-absent-branch-str",
                "quantified-branch-local-named-backreference-compile-metadata-str",
                "quantified-branch-local-named-backreference-module-search-lower-bound-str",
                "quantified-branch-local-named-backreference-pattern-fullmatch-second-iteration-str",
                "quantified-branch-local-named-backreference-pattern-fullmatch-absent-branch-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b)+|c)\2d",
                r"a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
    ),
    FixtureBundleSpec(
        "optional_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="optional-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "optional-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "optional-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
                "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
                "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-absent-group-str",
                "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
                "optional-group-alternation-branch-local-named-backreference-compile-metadata-str",
                "optional-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
                "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
                "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-absent-group-str",
                "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)\2)?d",
                r"a(?P<outer>(?P<inner>b|c)(?P=inner))?d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
    FixtureBundleSpec(
        "conditional_group_exists_branch_local_backreference_workflows.py",
        expected_manifest_id="conditional-group-exists-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-branch-local-numbered-backreference-compile-metadata-str",
                "conditional-group-exists-branch-local-numbered-backreference-module-search-present-str",
                "conditional-group-exists-branch-local-numbered-backreference-pattern-fullmatch-absent-str",
                "conditional-group-exists-branch-local-named-backreference-compile-metadata-str",
                "conditional-group-exists-branch-local-named-backreference-module-search-present-str",
                "conditional-group-exists-branch-local-named-backreference-pattern-fullmatch-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b)|c)\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)",
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
        "nested_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="nested-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
                "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
                "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
                "nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
                "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
                "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
                "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c))\2d",
                r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
    ),
    FixtureBundleSpec(
        "quantified_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="quantified-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
                "quantified-alternation-branch-local-named-backreference-compile-metadata-str",
                "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-c-branch-str",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
                "quantified-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
                "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-bytes",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-bytes",
                "quantified-alternation-branch-local-named-backreference-compile-metadata-bytes",
                "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-c-branch-bytes",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-bytes",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-bytes",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)\2){1,2}d",
                r"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
                rb"a((b|c)\2){1,2}d",
                rb"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 12,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "quantified_nested_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="quantified-nested-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
                "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
                "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-bytes",
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-bytes",
                "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
                "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-bytes",
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-bytes",
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-bytes",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)+)\2d",
                r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
                rb"a((b|c)+)\2d",
                rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 12,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-str",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-bytes",
                "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-bytes",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){1,4})\2d",
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
                rb"a((b|c){1,4})\2d",
                rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
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
    FixtureBundleSpec(
        "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){2,})\2d",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
    FixtureBundleSpec(
        "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py",
        expected_manifest_id="nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows",
        expected_case_ids=frozenset(
            {
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-str",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){2,})\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE = (
    published_fixture_bundle_by_manifest_id(
        FIXTURE_BUNDLES,
        "quantified-alternation-branch-local-backreference-workflows",
    )
)
QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE = (
    published_fixture_bundle_by_manifest_id(
        FIXTURE_BUNDLES,
        "quantified-nested-group-alternation-branch-local-backreference-workflows",
    )
)
NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BUNDLE = (
    published_fixture_bundle_by_manifest_id(
        FIXTURE_BUNDLES,
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows",
    )
)
NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_REASON = (
    "broader {1,4} nested branch-local-backreference bytes parity is still unpublished for rebar"
)
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
        unsupported_backends=("rebar",),
        unsupported_backend_reason=(
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_REASON
        ),
    ),
    BranchLocalBackreferenceBytesFollowOnCase(
        id="nested-broader-range-wider-ranged-repeat-branch-local-named-bytes",
        pattern=rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        search_matches=(b"zzaccdzz", b"zzabbdzz"),
        fullmatch_matches=(b"abccd", b"acccccd"),
        fullmatch_misses=(b"abcbcd", b"accccccd"),
        unsupported_backends=("rebar",),
        unsupported_backend_reason=(
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_REASON
        ),
    ),
)
DIRECT_BYTES_FOLLOW_ON_BUNDLES = (
    QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
)
DIRECT_BYTES_FOLLOW_ON_SPECS = (
    BranchLocalBytesFollowOnSpec(
        bundle=QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        cases=QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES,
        bucket_label="quantified-alternation-branch-local-backreference-bytes-follow-on",
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
        bucket_label=(
            "quantified-nested-group-alternation-branch-local-backreference-"
            "bytes-follow-on"
        ),
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
        bucket_label=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
            "branch-local-backreference-bytes-follow-on"
        ),
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
)
DIRECT_BYTES_FOLLOW_ON_CASES = tuple(
    case for spec in DIRECT_BYTES_FOLLOW_ON_SPECS for case in spec.cases
)
SUPPORTED_DIRECT_BYTES_PATTERNS = frozenset(
    case.pattern for case in DIRECT_BYTES_FOLLOW_ON_CASES if not case.unsupported_backends
)
PUBLISHED_CASES = fixture_cases_from_bundles(FIXTURE_BUNDLES)
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}
COMPILE_CASES, MODULE_CASES, PATTERN_CASES = partition_direct_bytes_follow_on_case_buckets(
    FIXTURE_BUNDLES,
    DIRECT_BYTES_FOLLOW_ON_BUNDLES,
)
_SHARED_WORKFLOW_CASE_IDS = frozenset(
    case.case_id for case in (*MODULE_CASES, *PATTERN_CASES)
)
WORKFLOW_CASES = tuple(
    case for case in PUBLISHED_CASES if case.case_id in _SHARED_WORKFLOW_CASE_IDS
)
BRANCH_LOCAL_BACKREFERENCE_SELECTED_CASE_IDS = tuple(
    case.case_id for case in PUBLISHED_CASES
)
BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS = {
    "shared-compile": frozenset(case.case_id for case in COMPILE_CASES),
    "shared-module": frozenset(case.case_id for case in MODULE_CASES),
    "shared-pattern": frozenset(case.case_id for case in PATTERN_CASES),
    **{
        spec.bucket_label: frozenset(
            case.case_id for case in spec.bundle.cases if case.text_model == "bytes"
        )
        for spec in DIRECT_BYTES_FOLLOW_ON_SPECS
    },
}
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
    case.case_id
    for case in WORKFLOW_CASES
    if case.manifest_id in MATCH_CONVENIENCE_MANIFEST_IDS and case.operation != "compile"
)
MATCH_GROUP_ACCESS_CASE_IDS = (
    "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
    "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
    "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
    "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
    "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
    "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
    "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
    "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
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
)
SUPPLEMENTAL_MISS_CASES = (
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
    CASES_BY_ID[case_id] for case_id in MATCH_GROUP_ACCESS_CASE_IDS
)


def _bounded_pattern(case: BoundedPatternCase) -> str:
    return str_case_pattern(CASES_BY_ID[case.pattern_case_id])


def _invoke_bound_helper(
    pattern: object,
    case: BoundedPatternCase | DirectBytesBoundedPatternCase,
) -> object:
    return getattr(pattern, case.helper)(case.string, *case.bounds)


def _workflow_result_for_case(
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str] | None]:
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

    return observed, expected


def _assert_direct_bytes_follow_on_case_backend_gating(
    case: BranchLocalBackreferenceBytesFollowOnCase,
) -> None:
    if case in NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES:
        assert case.unsupported_backends == ("rebar",)
        assert (
            case.unsupported_backend_reason
            == NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BYTES_REASON
        )
        return

    assert case.unsupported_backends == ()
    assert case.unsupported_backend_reason is None


def _published_bytes_follow_on_texts_by_pattern(
    bundle_bytes_cases: tuple[FixtureCase, ...],
) -> tuple[dict[bytes, frozenset[bytes]], dict[bytes, frozenset[bytes]]]:
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

    return (
        {
            pattern: frozenset(texts)
            for pattern, texts in published_module_texts_by_pattern.items()
        },
        {
            pattern: frozenset(texts)
            for pattern, texts in published_fullmatch_texts_by_pattern.items()
        },
    )


def test_match_group_access_rows_remain_on_branch_local_fixture_paths() -> None:
    assert tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES) == MATCH_GROUP_ACCESS_CASE_IDS
    assert {case.text_model for case in MATCH_GROUP_ACCESS_CASES} == {"str"}


def test_pattern_bounds_cases_stay_anchored_to_supported_branch_local_patterns() -> None:
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


@pytest.mark.parametrize("bundle", FIXTURE_BUNDLES, ids=lambda bundle: bundle.expected_manifest_id)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


def test_branch_local_backreference_parity_suite_tracks_published_case_frontier() -> None:
    for bundle in FIXTURE_BUNDLES:
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=tuple(case.case_id for case in bundle.cases),
        )


def test_branch_local_backreference_direct_test_case_id_buckets_cover_selected_frontier(
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS,
        selected_case_ids=BRANCH_LOCAL_BACKREFERENCE_SELECTED_CASE_IDS,
        coverage_label="branch-local-backreference direct-test case-id buckets",
    )


def test_branch_local_backreference_mixed_text_model_manifests_keep_explicit_direct_bytes_follow_on_routing(
) -> None:
    assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(
        FIXTURE_BUNDLES,
        direct_bytes_follow_on_bundles=DIRECT_BYTES_FOLLOW_ON_BUNDLES,
        coverage_label="branch-local-backreference",
    )


@pytest.mark.parametrize(
    "spec",
    DIRECT_BYTES_FOLLOW_ON_SPECS,
    ids=lambda spec: spec.bundle.manifest.manifest_id,
)
def test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor(
    spec: BranchLocalBytesFollowOnSpec,
) -> None:
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

    assert BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS[spec.bucket_label] == frozenset(
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
        _assert_direct_bytes_follow_on_case_backend_gating(case)
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
    ) = _published_bytes_follow_on_texts_by_pattern(bundle_bytes_cases)
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


@pytest.mark.parametrize("case", WORKFLOW_CASES, ids=lambda case: case.case_id)
def test_published_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _workflow_result_for_case(backend_name, backend, case)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    if expected is None:
        return

    if case.case_id in MATCH_CONVENIENCE_CASE_IDS:
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_CASES, ids=lambda case: case.id)
def test_direct_bytes_follow_on_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: BranchLocalBackreferenceBytesFollowOnCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_CASES, ids=lambda case: case.id)
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


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_CASES, ids=lambda case: case.id)
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


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_CASES, ids=lambda case: case.id)
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


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_CASES, ids=lambda case: case.id)
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


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_CASES, ids=lambda case: case.id)
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


@pytest.mark.parametrize("case", DIRECT_BYTES_FOLLOW_ON_CASES, ids=lambda case: case.id)
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

    observed = _invoke_bound_helper(observed_pattern, case)
    expected = _invoke_bound_helper(expected_pattern, case)

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

    observed = _invoke_bound_helper(observed_pattern, case)
    expected = _invoke_bound_helper(expected_pattern, case)

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=lambda case: case.case_id)
def test_match_group_accessors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _workflow_result_for_case(backend_name, backend, case)

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
    observed, expected = _workflow_result_for_case(backend_name, backend, case)

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
