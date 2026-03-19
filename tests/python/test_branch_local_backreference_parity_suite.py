from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields
from itertools import product
import re

import pytest

from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT, FixtureCase
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
    expected_unsupported_backends: tuple[str, ...] = ()
    expected_unsupported_backend_reason: str | None = None


@dataclass(frozen=True)
class GeneratedQuantifiedBranchLocalParitySpec:
    bundle: FixtureBundle
    fixture_name: str
    expected_compile_case_ids: tuple[str, ...]
    expected_patterns: frozenset[str | bytes]
    expected_text_models: frozenset[str]
    candidate_body_atoms: tuple[str, ...]
    candidate_suffixes: tuple[str, ...]
    candidate_lengths: range
    expected_candidate_count: int
    failure_prefix: str


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
SIMPLE_BACKREFERENCE_WORKFLOW_CASE_IDS = (
    "named-backreference-module-search-str",
    "named-backreference-pattern-search-str",
    "numbered-backreference-module-search-str",
    "numbered-backreference-pattern-search-str",
    "numbered-backreference-segment-module-search-str",
    "numbered-backreference-prefix-pattern-search-str",
)


FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "named_backreference_workflows.py",
        expected_manifest_id="named-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "named-backreference-compile-metadata-str",
                "named-backreference-module-search-str",
                "named-backreference-pattern-search-str",
            }
        ),
        expected_patterns=frozenset({r"(?P<word>ab)(?P=word)"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
    FixtureBundleSpec(
        "numbered_backreference_workflows.py",
        expected_manifest_id="numbered-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "numbered-backreference-compile-metadata-str",
                "numbered-backreference-module-search-str",
                "numbered-backreference-pattern-search-str",
                "numbered-backreference-segment-module-search-str",
                "numbered-backreference-prefix-pattern-search-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"(ab)\1",
                r"(ab)x\1",
                r"x(ab)\1",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 2,
                ("pattern_call", "search"): 2,
            }
        ),
    ),
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
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){2,})\2d",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
                rb"a((b|c){2,})\2d",
                rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
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
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-bytes",
                "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-bytes",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){2,})\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                rb"a((b|c){2,})\2(?(2)d|e)",
                rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
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
)

WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES = (
    "named_backreference_workflows.py",
    "numbered_backreference_workflows.py",
)


def _whole_manifest_backreference_bundle_specs() -> tuple[FixtureBundleSpec, ...]:
    specs = tuple(
        spec
        for spec in FIXTURE_BUNDLE_SPECS
        if spec.fixture_name in WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES
    )
    assert tuple(spec.fixture_name for spec in specs) == (
        WHOLE_MANIFEST_BACKREFERENCE_FIXTURE_NAMES
    )
    return specs


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
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BUNDLE = (
    published_fixture_bundle_by_manifest_id(
        FIXTURE_BUNDLES,
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows",
    )
)
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE = (
    published_fixture_bundle_by_manifest_id(
        FIXTURE_BUNDLES,
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows",
    )
)
GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS = (
    GeneratedQuantifiedBranchLocalParitySpec(
        bundle=QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        fixture_name=(
            "quantified_nested_group_alternation_branch_local_backreference_"
            "workflows.py"
        ),
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
        expected_candidate_count=484,
        failure_prefix=(
            "quantified nested-group alternation branch-local-backreference "
            "generated parity drifted"
        ),
    ),
    GeneratedQuantifiedBranchLocalParitySpec(
        bundle=(
            NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE
        ),
        fixture_name=(
            "nested_broader_range_open_ended_quantified_group_alternation_"
            "branch_local_backreference_conditional_workflows.py"
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
        expected_candidate_count=372,
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


GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPEC_BY_MANIFEST_ID = {
    spec.bundle.expected_manifest_id: spec
    for spec in GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS
}
GENERATED_STR_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID = {
    spec.bundle.expected_manifest_id: _build_generated_quantified_branch_local_candidate_texts(
        spec.candidate_body_atoms,
        spec.candidate_suffixes,
        spec.candidate_lengths,
    )
    for spec in GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS
}
GENERATED_BYTES_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID = {
    manifest_id: tuple(text.encode("ascii") for text in texts)
    for manifest_id, texts in GENERATED_STR_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID.items()
}
GENERATED_QUANTIFIED_BRANCH_LOCAL_COMPILE_CASES = tuple(
    case
    for spec in GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS
    for case in fixture_cases_for_operation((spec.bundle,), "compile")
)


def _generated_branch_local_candidate_texts(
    spec: GeneratedQuantifiedBranchLocalParitySpec,
    case: FixtureCase,
) -> tuple[str | bytes, ...]:
    if case.text_model == "bytes":
        return GENERATED_BYTES_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID[
            spec.bundle.expected_manifest_id
        ]
    return GENERATED_STR_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID[
        spec.bundle.expected_manifest_id
    ]


def _record_generated_match_failure(
    failures: list[str],
    *,
    label: str,
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
) -> None:
    try:
        assert_match_result_parity(
            backend_name,
            observed,
            expected,
            check_regs=True,
        )
        if expected is None:
            return

        assert_match_convenience_api_parity(observed, expected)
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)
    except AssertionError as exc:
        failures.append(f"{label}: {exc}")

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
DIRECT_BYTES_FOLLOW_ON_BUNDLES = (
    QUANTIFIED_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
    NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_BUNDLE,
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
    BranchLocalBytesFollowOnSpec(
        bundle=NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BUNDLE,
        cases=NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_BYTES_CASES,
        bucket_label=(
            "nested-broader-range-open-ended-quantified-group-alternation-"
            "branch-local-backreference-bytes-follow-on"
        ),
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
        bucket_label=(
            "nested-broader-range-open-ended-quantified-group-alternation-"
            "branch-local-backreference-conditional-bytes-follow-on"
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
SUPPORTED_DIRECT_BYTES_PATTERNS = frozenset(
    case.pattern for case in DIRECT_BYTES_FOLLOW_ON_CASES if not case.unsupported_backends
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
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
    SIMPLE_BACKREFERENCE_WORKFLOW_CASE_IDS
) | frozenset(
    case.case_id
    for case in WORKFLOW_CASES
    if case.manifest_id in MATCH_CONVENIENCE_MANIFEST_IDS and case.operation != "compile"
)
MATCH_GROUP_ACCESS_CASE_IDS = (
    *SIMPLE_BACKREFERENCE_WORKFLOW_CASE_IDS,
    "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
    "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
    "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
    "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
    "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
    "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
    "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
    "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
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
    *,
    expected_unsupported_backends: tuple[str, ...] = (),
    expected_unsupported_backend_reason: str | None = None,
) -> None:
    assert case.unsupported_backends == expected_unsupported_backends
    assert case.unsupported_backend_reason == expected_unsupported_backend_reason


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


def test_match_group_access_rows_remain_on_shared_backreference_fixture_paths() -> None:
    assert tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES) == MATCH_GROUP_ACCESS_CASE_IDS
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


def test_whole_manifest_bundle_specs_load_in_declared_order_with_bundle_validation() -> None:
    bundles = load_fixture_bundles(_whole_manifest_backreference_bundle_specs())

    assert tuple(bundle.manifest.path.name for bundle in bundles) == (
        "named_backreference_workflows.py",
        "numbered_backreference_workflows.py",
    )
    for bundle in bundles:
        assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_fixture_case_operation_selection_preserves_published_row_order() -> None:
    bundles = load_fixture_bundles(_whole_manifest_backreference_bundle_specs())

    assert tuple(
        case.case_id for case in fixture_cases_for_operation(bundles, "pattern_call")
    ) == (
        "named-backreference-pattern-search-str",
        "numbered-backreference-pattern-search-str",
        "numbered-backreference-prefix-pattern-search-str",
    )


def test_whole_manifest_bundle_contract_supports_exact_case_id_validation() -> None:
    named_bundle_spec = _whole_manifest_backreference_bundle_specs()[0]
    (bundle,) = load_fixture_bundles((named_bundle_spec,))

    assert (
        bundle.manifest.path
        == CORRECTNESS_FIXTURES_ROOT / "named_backreference_workflows.py"
    )
    assert bundle.expected_case_ids is not None
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_expected_fixture_bundle_contract_supports_exact_case_id_validation() -> None:
    named_bundle_spec = _whole_manifest_backreference_bundle_specs()[0]
    (bundle,) = load_fixture_bundles((named_bundle_spec,))

    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=(
            CORRECTNESS_FIXTURES_ROOT / "named_backreference_workflows.py"
        ),
    )
    assert (bundle.manifest.path,) == (
        CORRECTNESS_FIXTURES_ROOT / "named_backreference_workflows.py",
    )


def test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field(
) -> None:
    field_names = {field.name for field in fields(FixtureBundle)}
    named_bundle_spec = _whole_manifest_backreference_bundle_specs()[0]
    (bundle,) = load_fixture_bundles((named_bundle_spec,))

    assert "expected_manifest_id" not in field_names
    assert bundle.expected_manifest_id == "named-backreference-workflows"
    assert bundle.expected_manifest_id == bundle.manifest.manifest_id


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

    assert spec.bundle.manifest.path == CORRECTNESS_FIXTURES_ROOT / spec.fixture_name
    assert tuple(case.case_id for case in compile_cases) == spec.expected_compile_case_ids
    assert {case_pattern(case) for case in compile_cases} == spec.expected_patterns
    assert {case.text_model for case in compile_cases} == spec.expected_text_models
    assert (
        len(
            GENERATED_STR_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID[
                spec.bundle.expected_manifest_id
            ]
        )
        == spec.expected_candidate_count
    )


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
        _assert_direct_bytes_follow_on_case_backend_gating(
            case,
            expected_unsupported_backends=spec.expected_unsupported_backends,
            expected_unsupported_backend_reason=spec.expected_unsupported_backend_reason,
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


@pytest.mark.parametrize(
    "case",
    GENERATED_QUANTIFIED_BRANCH_LOCAL_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_generated_quantified_branch_local_text_matrix_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    spec = GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPEC_BY_MANIFEST_ID[case.manifest_id]
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
            _record_generated_match_failure(
                failures,
                label=f"module.{helper}({pattern!r}, {text!r})",
                backend_name=backend_name,
                observed=getattr(backend, helper)(pattern, text),
                expected=getattr(re, helper)(pattern, text),
            )
            _record_generated_match_failure(
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
