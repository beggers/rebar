from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import (
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    published_fixture_paths_from_bundles,
    str_case_pattern,
)
PUBLISHED_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATHS = select_correctness_fixture_paths(
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR
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
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)\2){1,2}d",
                r"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
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
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)+)\2d",
                r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
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
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){1,4})\2d",
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
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
PUBLISHED_CASES = fixture_cases_from_bundles(FIXTURE_BUNDLES)
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}
COMPILE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
WORKFLOW_CASES = tuple(case for case in PUBLISHED_CASES if case.operation != "compile")
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
    for case in PUBLISHED_CASES
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


def _invoke_bound_helper(pattern: object, case: BoundedPatternCase) -> object:
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


def test_expected_branch_local_backreference_fixtures_remain_published() -> None:
    assert PUBLISHED_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATHS == (
        published_fixture_paths_from_bundles(FIXTURE_BUNDLES)
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


@pytest.mark.parametrize("bundle", FIXTURE_BUNDLES, ids=lambda bundle: bundle.expected_manifest_id)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


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
